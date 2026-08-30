#!/usr/bin/env python3
"""Fetch today's headlines, write them in spoken Palestinian, annotate, voice.

This is the 6am job. It exists because the app is a static site with no server:
summarising news, writing Palestinian, and checking 36K lexicon entries can't
happen in a browser.

The hard part is NOT the translation — it's the disambiguation. 43% of words in a
news text need someone to pick the right sense from real Maknuune candidates
("bqʿd" is sit-down, not wooden-bucket-for-milking). In conversation that someone
is Claude. At 6am it has to be the API, or the pipeline regresses to taking
cands[0] — the exact bug this project spent its life eliminating.

So there are two API calls:
  1. summarise + write Palestinian
  2. resolve ambiguities BY CHOOSING FROM REAL CANDIDATE LISTS

Call 2 is the one that preserves the guarantee. It cannot invent a root; it can
only pick among entries Maknuune actually contains.

    export ANTHROPIC_API_KEY=...
    export ELEVENLABS_API_KEY=...      # optional
    export ELEVENLABS_VOICE_ID=...     # optional
    python3 pipeline/daily_news.py [--sentences 9] [--dry-run]
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import json, os, sys, re, argparse, subprocess, datetime, ssl, urllib.request
import xml.etree.ElementTree as ET

# macOS python.org builds ship without a CA bundle unless Install Certificates.command
# was run, so HTTPS fails locally with CERTIFICATE_VERIFY_FAILED even though the network
# is fine. Linux CI has system certs. Use certifi when present, else the system default.
import net           # noqa: E402  -- one HTTPS context, one diagnosis
SSLCTX = net.SSL_CTX

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)

MODEL = "claude-opus-4-8"

# Where the day's headlines come from, per language. Arabic reads the world wires in English;
# Hebrew reads Israel's own papers, because a Hebrew learner's news should be the news Israelis
# are actually reading, and because those feeds are what A1 measured lexicon coverage against.
FEEDS_BY_LANG = {
    "ar": [
        ("BBC World",   "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("Al Jazeera",  "https://www.aljazeera.com/xml/rss/all.xml"),
        ("NPR World",   "https://feeds.npr.org/1004/rss.xml"),
    ],
    "he": [
        ("Ynet",         "https://www.ynet.co.il/Integration/StoryRss2.xml"),
        ("Walla",        "https://rss.walla.co.il/feed/1?type=main"),
        # 403s from GitHub's runners (fine from a laptop) — left in because it costs one
        # logged line and works for anyone running this locally; the other three carry the day.
        ("Israel Hayom", "https://www.israelhayom.co.il/rss.xml"),
        ("Maariv",       "https://www.maariv.co.il/Rss/RssFeedsMivzakiChadashot"),
    ],
}
FEEDS = FEEDS_BY_LANG[paths.LANG]

def headlines(limit=30):
    """Pull recent headlines. Uses only the stdlib so the CI image stays thin."""
    out = []
    for name, url in FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "arabic-reader/1.0"})
            with urllib.request.urlopen(req, timeout=25, context=SSLCTX) as r:
                root = ET.fromstring(r.read())
            for item in root.iter("item"):
                t = item.findtext("title") or ""
                d = item.findtext("description") or ""
                d = re.sub(r"<[^>]+>", "", d).strip()
                if t:
                    out.append(f"[{name}] {t}" + (f" — {d[:200]}" if d else ""))
                if len(out) >= limit:
                    break
        except Exception as e:
            print(f"  !! {name}: {str(e)[:70]}")
    return out

# The register matters more than the content: newsreader Arabic is fuṣḥā, which is
# explicitly not the goal (LEARNING-SYSTEM §1). Ask for the telling-a-friend register.
AR_PROMPT = """You are helping someone learn SPOKEN PALESTINIAN ARABIC (urban \
Levantine — Jerusalem/Ramallah/Nablus).

Write {n} sentences summarising today's most significant world news.

CRITICAL — the register:
- Write as you would TELL a friend the news over coffee, NOT as a newsreader reads it.
- Newsreader Arabic is fuṣḥā (MSA). That is exactly what we do NOT want.
- Use dialect markers naturally: عم + verb for the progressive, b- prefix on habitual
  verbs, لسه, هيك, كتير, شو, مش (not ليس), اللي (not الذي).
- Use dialect spellings people actually type: تلاتين not ثلاثين, أكتر not أكثر,
  تانية not ثانية, هاد/هاي not هذا/هذه.
- Short sentences. One story each. A2/B1 learner level.
- Plain factual reporting. No editorialising, no emotive framing.

Each sentence needs a natural English translation — meaning, not word-for-word.

Today's headlines:
{headlines}"""

# Hebrew's register problem is the mirror image. Written Hebrew is not a different language the
# way fuṣḥā is, but news Hebrew is markedly bookish -- אין ביכולתו, לאחר ש-, בטרם -- and a
# learner needs what people say. And it must be written UNPOINTED, the way Israelis write:
# pipeline/he_ingest.py adds the pointing by choosing a lexicon entry, and pointing supplied by
# the writer would bypass the lookup that is the whole guarantee.
HE_PROMPT = """You are helping someone learn MODERN SPOKEN ISRAELI HEBREW.

Write {n} sentences summarising today's most significant news from Israel and the world.

CRITICAL — the register:
- Write as you would TELL a friend the news over coffee, NOT as a newsreader reads it and NOT
  as a newspaper writes it. Israeli news Hebrew is markedly bookish; that is what we do NOT want.
- Prefer the everyday word over the literary one: אחרי ש- not לאחר ש-, לפני ש- not בטרם,
  אבל not אולם, גם not אף, כי not מכיוון ש-.
- Use ordinary spoken syntax: ש- for "that", של for possession rather than the construct chain
  where a speaker would, את before definite objects.
- Write UNPOINTED, in ordinary ktiv male, exactly as it would appear in a message: יכתוב,
  תוכנית, שמונים. Do NOT add niqqud — the pipeline supplies it from the lexicon.
- Short sentences. One story each. A2/B1 learner level.
- Plain factual reporting. No editorialising, no emotive framing.

Each sentence needs a natural English translation — meaning, not word-for-word.

Today's headlines:
{headlines}"""

WRITE_PROMPT = {"ar": AR_PROMPT, "he": HE_PROMPT}[paths.LANG]

# What the annotator is called and which script runs it, per language.
LEXICON_NAME = {"ar": "Maknuune", "he": "Wiktionary"}[paths.LANG]
INGEST_SCRIPT = {"ar": "ingest.py", "he": "he_ingest.py"}[paths.LANG]
NEWS_TITLE = {"ar": "أخبار اليوم", "he": "חדשות היום"}[paths.LANG]
NEWS_SOURCE = {
    "ar": "World headlines, written in spoken Palestinian by Claude. NOT native-validated.",
    "he": "Israeli and world headlines, written in spoken Hebrew by Claude. NOT native-validated.",
}[paths.LANG]

SENTENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "sentences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ar": {"type": "string",
                           "description": "The target language, in its own script"},
                    "en": {"type": "string", "description": "Natural English translation"},
                },
                "required": ["ar", "en"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["sentences"],
    "additionalProperties": False,
}

RESOLVE_SCHEMA = {
    "type": "object",
    "properties": {
        "resolutions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    # The NUMBER, not the word. Echoing the word back was fine while the texts
                    # were unpointed consonants; on pointed Hebrew it stopped matching, because
                    # a word like הַרְבֵּה is a string of combining marks whose order is not
                    # guaranteed by any encoder. 758 of 1,413 picks were thrown away on the
                    # first Ben-Yehuda run for that reason alone -- every id was RIGHT and in
                    # the word's own option list, and the key it came back under was not equal
                    # to the key it went out under. A number cannot drift.
                    "n":    {"type": "integer", "description": "the number of the word above"},
                    "id":   {"type": "string", "description": "a lexicon id from its options"},
                    "why":  {"type": "string"},
                },
                "required": ["n", "id", "why"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["resolutions"],
    "additionalProperties": False,
}

def client():
    return net.need("anthropic").Anthropic()


def explain_api_failure(e):
    """Say WHICH thing is wrong, in words that name the fix.

    An expired key and an empty balance both surface as 'the news job failed', and this job runs
    unattended at 05:00 — the last time one of them happened it went unnoticed for two weeks while
    the app quietly served a fortnight-old article. The exception type is enough to tell them
    apart, so say so loudly instead of dumping a traceback nobody reads.
    """
    anthropic = sys.modules.get("anthropic")
    if anthropic is None:                                     # never got as far as importing it
        return str(e)[:200], ""
    if isinstance(e, anthropic.AuthenticationError):          # 401
        return ("the ANTHROPIC_API_KEY is invalid, revoked or expired",
                "Make a new key at console.anthropic.com/settings/keys, then update the "
                "ANTHROPIC_API_KEY repo secret (Settings → Secrets and variables → Actions).")
    if isinstance(e, anthropic.PermissionDeniedError):        # 403
        return ("the key is valid but not allowed to use this model",
                "Check the key's workspace/permissions, or that %s is enabled for it." % MODEL)
    if isinstance(e, anthropic.NotFoundError):                # 404
        return ("the model id %r was rejected" % MODEL,
                "Update MODEL in pipeline/daily_news.py to a current model.")
    if isinstance(e, anthropic.RateLimitError):               # 429
        return ("the account is rate limited right now",
                "Usually transient — tomorrow's run should recover on its own.")
    msg = str(getattr(e, "message", "") or e)
    if isinstance(e, anthropic.BadRequestError) and "credit" in msg.lower():
        return ("the Anthropic account is out of credit",
                "Add credit at console.anthropic.com/settings/billing. The key itself is fine.")
    if isinstance(e, anthropic.APIStatusError):
        return ("the API returned %s: %s" % (getattr(e, "status_code", "?"), msg[:160]), "")
    if isinstance(e, anthropic.APIConnectionError):
        return ("could not reach the API (network)", "Usually transient; the next run should work.")
    return (msg[:200] or e.__class__.__name__, "")

def write_sentences(c, heads, n):
    r = c.messages.create(
        model=MODEL, max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": SENTENCE_SCHEMA}},
        messages=[{"role": "user", "content": WRITE_PROMPT.format(
            n=n, headlines="\n".join(f"- {h}" for h in heads))}],
    )
    txt = next(b.text for b in r.content if b.type == "text")
    return json.loads(txt)["sentences"]

BATCH = 40


def resolve(c, ambiguous):
    """Pick the right sense — from REAL candidates only. This is the guarantee.

    In batches, because the size of this call is set by the language, not by us: Hebrew's news
    runs about 50% ambiguous against Arabic's 32% (A1 measured 49.9%), so a day's article asks
    for ninety-odd decisions where Arabic asks for forty. One reply carrying all of them is a
    long JSON object with a token limit at the end of it, and a truncated reply is not a partial
    answer — it is a parse error that loses every decision in it.
    """
    if not ambiguous:
        return {}
    out = {}
    for i in range(0, len(ambiguous), BATCH):
        chunk = ambiguous[i:i + BATCH]
        if len(ambiguous) > BATCH:
            print(f"  batch {i // BATCH + 1}: {len(chunk)} words")
        out.update(_resolve_batch(c, chunk))
    return out


def _resolve_batch(c, ambiguous):
    lines = []
    for n, a in enumerate(ambiguous, 1):
        # The whole sentence, not just its translation: which sense a word has is decided by
        # the words around it, and the English is a paraphrase of all of them at once.
        lines.append(f'\n{n}. WORD: {a["surface"]}   in: "{a.get("sent", "")}"'
                     f'\n   means: "{a["en"]}"')
        if a.get("cut"):
            lines.append(f'   NOTE: matched after removing the prefix {a["cut"]}-, so the '
                         f'options below are entries for the STEM. Pick the one that fits '
                         f'{a["surface"]} in the sentence, not the bare stem.')
        for o in a["options"]:
            lines.append(f'   id={o["id"]}  root={o["root"]}  {o["analysis"]}  {o["gloss"]}')
    r = c.messages.create(
        model=MODEL, max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": RESOLVE_SCHEMA}},
        messages=[{"role": "user", "content":
            "Each word below appeared in a sentence and matches several entries in the "
            + LEXICON_NAME + " lexicon. Pick the ONE id whose sense fits the sentence.\n\n"
            "Answer with the WORD'S NUMBER and one id from that word's own options. Do not "
            "invent ids, and do not answer for a number that is not listed.\n"
            "Watch for causatives: 'sit down' vs 'make sb sit' are different entries.\n"
            # A word can be a word AND a particle plus a different word -- Hebrew's are single
            # letters -- and which one it is comes from the sentence, not from the spelling.
            "An option beginning \"as X- + ...\" reads the word as the particle X plus the "
            "word after it. Pick it when that is what the sentence says, even though the "
            "word also matches an entry on its own.\n"
            + "\n".join(lines)}],
    )
    txt = next(b.text for b in r.content if b.type == "text")
    picks = json.loads(txt)["resolutions"]
    out = {}
    for p in picks:
        n, i = int(p.get("n", 0)), str(p["id"])
        if not 1 <= n <= len(ambiguous):
            print(f"  !! rejected id {i} — no word numbered {n} in this batch")
            continue
        a = ambiguous[n - 1]
        if i in {o["id"] for o in a["options"]}:
            out[a["surface"]] = i
        else:
            # A hallucinated id would silently poison the lexicon layer. Drop it and
            # leave the word flagged rather than accept an unverifiable answer.
            print(f"  !! rejected id {i} for {a['surface']} — not in its candidate list")
    return out

def ingest(src, audio=False):
    # --lang is not optional here. paths.py reads it from argv, so a child launched without it
    # runs as the DEFAULT language whatever the parent is doing: the Hebrew annotator wrote its
    # output over build/ar/news-<today>/text.json and the parent then failed looking for an
    # artifact under build/he. Passing it explicitly, and asserting it in the child, are two
    # halves of the same fix -- this one stops it happening, the assert stops it being silent.
    cmd = ([sys.executable, os.path.join(HERE, INGEST_SCRIPT), src, "--lang", paths.LANG]
           + (["--audio"] if audio else []))
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    print(r.stdout.rstrip())
    if r.returncode: print(r.stderr[:600])
    return r.returncode == 0

def ambiguities(text_id):
    p = paths.build(text_id, "text.json")
    a = json.load(open(p, encoding="utf-8"))
    out = []
    for s in a["sentences"]:
        for w in s["words"]:
            if w["provenance"] == "AMBIGUOUS-needs-resolution":
                out.append({"surface": w["surface"], "en": s["en"], "options": w["options"],
                            "cut": w.get("_cut_for_prompt", ""), "sent": s["ar"]})
    return out

# "Today" means today WHERE THE LEARNER IS, not on the build runner. The runner is UTC, and the
# schedule now fires before midnight UTC so the job can finish before 5am Israel — so a UTC date
# would label the morning's news with yesterday. Asia/Jerusalem also carries DST, which is the
# whole reason the cron can't just be pinned to a wall-clock hour.
def israel_today():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()
    except Exception as e:                      # no tzdata on this box — say so, don't guess wrong
        print(f"!! Asia/Jerusalem unavailable ({e}); falling back to UTC date")
        return datetime.datetime.now(datetime.timezone.utc).date()

def adjudicate(src):
    """Annotate one existing text and settle its ambiguities. Same cycle the news runs.

    The Ben-Yehuda shelf is written by pipeline/he_books.py, not by this file, but the half that
    costs money -- deciding which entry a word is -- is the same job with the same rules, so it
    is the same code rather than a second copy of it that drifts. What differs is only that
    there is no article to write first.
    """
    tid = json.load(open(src, encoding="utf-8"))["id"]
    print(f"=== {tid} ===")
    if not ingest(src):
        return 1
    amb = ambiguities(tid)
    if not amb:
        print("  nothing ambiguous — the text's own pointing settled it")
        return 0
    print(f"resolving {len(amb)} ambiguous words (selecting from real entries)…")
    rp = paths.resolutions()
    res = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {}
    try:
        picks = resolve(client(), amb)
    except Exception as e:
        # Same tolerance the news has, for the same reason: every word this would have settled
        # is already in the artifact, flagged, and the card says so. A readable text with
        # honest uncertainty in it beats no text.
        what, fix = explain_api_failure(e)
        print(f"  !! could not resolve: {what}")
        if fix:
            print(f"  !! FIX: {fix}")
        return 0
    if picks:
        res.update(picks)
        json.dump(res, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  resolved {len(picks)}/{len(amb)}")
        if not ingest(src):
            return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentences", type=int, default=9)
    ap.add_argument("--dry-run", action="store_true", help="fetch headlines only")
    ap.add_argument("--skip-if-done", action="store_true",
                    help="exit 0 without spending anything if today's news is already written")
    ap.add_argument("--adjudicate", metavar="TEXT.json",
                    help="annotate and adjudicate an existing text instead of writing news")
    # Read by pipeline/paths.py at import time, before argparse ever runs. Declared here only so
    # --help lists it and an unknown-argument error never fires on it.
    ap.add_argument("--lang", default=paths.LANG, choices=paths.LANGS,
                    help="which language's news to write (default: %s)" % paths.LANG)
    a = ap.parse_args()

    if a.adjudicate:
        return adjudicate(a.adjudicate)

    today = israel_today().isoformat()
    print(f"=== daily news · {today} (Asia/Jerusalem) ===")

    # For the catch-up run. GitHub states plainly that scheduled workflows can be delayed or
    # dropped under load, and a single daily fire means a dropped fire is a day with no news
    # (2026-08-27 was one). A second, later schedule covers that — but only if it costs nothing
    # on the ordinary day when the first one worked, hence this guard, ahead of both API calls.
    if a.skip_if_done and os.path.exists(paths.texts(f"news-{today}.json")):
        print("today's news is already written — nothing to do")
        return 0

    print("fetching headlines…")
    heads = headlines()
    print(f"  {len(heads)} headlines")
    if not heads:
        print("!! no headlines — aborting (feeds unreachable)"); return 1
    if a.dry_run:
        for h in heads[:12]: print("   ", h[:110])
        return 0

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("!! ANTHROPIC_API_KEY not set"); return 1

    c = client()
    print(f"writing {a.sentences} sentences…")
    try:
        sents = write_sentences(c, heads, a.sentences)
    except Exception as e:
        what, fix = explain_api_failure(e)
        print("\n" + "!" * 72)
        print("!! TODAY'S NEWS WAS NOT WRITTEN — %s" % what)
        if fix:
            print("!! FIX: %s" % fix)
        print("!! Until then the app keeps serving the last article it has, and says so on the")
        print("!! home screen. Nothing else in the app is affected.")
        print("!" * 72 + "\n")
        return 1
    for s in sents: print("   ", s["ar"])

    tid = f"news-{today}"
    src = paths.texts(f"{tid}.json")
    json.dump({
        "id": tid, "kind": "news", "date": today,
        "title": {"ar": NEWS_TITLE, "en": f"Today's News — {today}"},
        "dialect": paths.LANG, "subdialect": "urban" if paths.LANG == "ar" else None,
        "source": NEWS_SOURCE,
        "sentences": sents,
    }, open(src, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"annotating against {LEXICON_NAME}…")
    if not ingest(src): return 1

    amb = ambiguities(tid)
    if amb:
        print(f"resolving {len(amb)} ambiguous words (selecting from real entries)…")
        rp = paths.resolutions()
        # A language on its FIRST run has no audit trail yet. This read assumed one existed,
        # because Arabic's has been in the repo since the beginning — so Hebrew's first news
        # article died here, after being written, annotated and paid for.
        res = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {}
        try:
            picks = resolve(c, amb)
        except Exception as e:
            # Adjudication failing must not cost the day's paper. Every word it would have
            # settled is already in the artifact, flagged AMBIGUOUS, and the app says so on the
            # card: "lexicon match not yet confirmed". A paper with honest uncertainty in it
            # beats no paper, and tomorrow's run re-resolves the same words.
            what, fix = explain_api_failure(e)
            print(f"  !! could not resolve: {what}")
            if fix:
                print(f"  !! FIX: {fix}")
            print("  !! shipping the article with those words flagged as unconfirmed.")
            picks = {}
        if picks:
            res.update(picks)
            json.dump(res, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print(f"  resolved {len(picks)}/{len(amb)}")
            if not ingest(src): return 1

    # Voice comes from pipeline/voice.py — the Action deliberately does NOT pass a voice
    # secret, so the daily news can't drift onto a different voice than the rest of the app.
    from voice import voice_id
    have_key = bool(os.environ.get("ELEVENLABS_API_KEY"))
    if have_key:
        print(f"generating audio… (voice {voice_id()})")
        ingest(src, audio=True)
    else:
        print("audio: skipped (no ELEVENLABS_API_KEY)")

    # A news item can introduce a verb the app has never carried. build_verbs.py takes the
    # union of the top-3000 frequency cut with every verb lemma attested in build/*/text.json,
    # so re-running it here conjugates today's new verbs and folds them into verbs.js — the
    # word card, the Verbs section and Translate all pick them up with no further work. It
    # reads data/maknuune.parquet (tracked) and is deterministic, so a day with no new verbs
    # leaves the file byte-identical and the commit step simply sees nothing to stage.
    # Arabic only. build_verbs.py derives paradigms from data/maknuune.parquet, which is
    # tracked; the Hebrew equivalent reads the 57 MB Wiktionary dump, which is not, so a Hebrew
    # verb met in the news gets its lexicon entry today and its paradigm at the next local
    # he_verbs.py run. Downloading 57 MB nightly to catch a verb or two is the wrong trade.
    if paths.LANG == "ar":
        print("rebuilding the verb list (any new verb in today's news gets its paradigm)…")
        subprocess.run([sys.executable, os.path.join(HERE, "build_verbs.py")], cwd=ROOT)

    subprocess.run([sys.executable, os.path.join(HERE, "build_app.py"),
                    "--lang", paths.LANG], cwd=ROOT)

    # FAIL LOUDLY on silent news. This step used to exit 0 whether or not any audio came
    # back, so a revoked/expired key produced a green run and a day of silent news that
    # nobody noticed until a learner opened it. A red run is the whole point of having CI.
    art = paths.build(tid, "text.json")
    voiced = total = 0
    if os.path.exists(art):
        d = json.load(open(art, encoding="utf-8"))
        total = len(d.get("sentences") or [])
        voiced = sum(1 for s in d.get("sentences") or [] if s.get("audio"))
    print(f"\ndone — {tid}  (audio {voiced}/{total})")
    if total and voiced < total:
        print(f"!! {tid} has {total - voiced} sentence(s) with NO audio.")
        print("   Usual cause: the ELEVENLABS_API_KEY repo secret is missing, revoked or out of")
        print("   credits. Update it in Settings > Secrets and variables > Actions, then re-run.")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
