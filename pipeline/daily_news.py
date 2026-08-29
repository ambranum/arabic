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
try:
    import certifi
    SSLCTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSLCTX = ssl.create_default_context()

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)

MODEL = "claude-opus-4-8"

FEEDS = [
    ("BBC World",   "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Al Jazeera",  "https://www.aljazeera.com/xml/rss/all.xml"),
    ("NPR World",   "https://feeds.npr.org/1004/rss.xml"),
]

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
WRITE_PROMPT = """You are helping someone learn SPOKEN PALESTINIAN ARABIC (urban \
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

SENTENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "sentences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ar": {"type": "string", "description": "Spoken Palestinian Arabic"},
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
                    "word": {"type": "string"},
                    "id":   {"type": "string", "description": "Maknuune ID from the options"},
                    "why":  {"type": "string"},
                },
                "required": ["word", "id", "why"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["resolutions"],
    "additionalProperties": False,
}

def client():
    import anthropic
    return anthropic.Anthropic()


def explain_api_failure(e):
    """Say WHICH thing is wrong, in words that name the fix.

    An expired key and an empty balance both surface as 'the news job failed', and this job runs
    unattended at 05:00 — the last time one of them happened it went unnoticed for two weeks while
    the app quietly served a fortnight-old article. The exception type is enough to tell them
    apart, so say so loudly instead of dumping a traceback nobody reads.
    """
    import anthropic
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

def resolve(c, ambiguous):
    """Pick the right sense — from REAL candidates only. This is the guarantee."""
    if not ambiguous:
        return {}
    lines = []
    for a in ambiguous:
        lines.append(f'\nWORD: {a["surface"]}   (sentence: "{a["en"]}")')
        for o in a["options"]:
            lines.append(f'   id={o["id"]}  root={o["root"]}  {o["analysis"]}  {o["gloss"]}')
    r = c.messages.create(
        model=MODEL, max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": RESOLVE_SCHEMA}},
        messages=[{"role": "user", "content":
            "Each word below appeared in a Palestinian Arabic sentence and matches several "
            "entries in the Maknuune lexicon. Pick the ONE id whose sense fits the sentence.\n\n"
            "You MUST return an id that appears in that word's options. Do not invent ids.\n"
            "Watch for causatives: 'sit down' vs 'make sb sit' are different entries.\n"
            + "\n".join(lines)}],
    )
    txt = next(b.text for b in r.content if b.type == "text")
    picks = json.loads(txt)["resolutions"]
    valid = {a["surface"]: {o["id"] for o in a["options"]} for a in ambiguous}
    out = {}
    for p in picks:
        w, i = p["word"], str(p["id"])
        if w in valid and i in valid[w]:
            out[w] = i
        else:
            # A hallucinated id would silently poison the lexicon layer. Drop it and
            # leave the word flagged rather than accept an unverifiable answer.
            print(f"  !! rejected id {i} for {w} — not in its candidate list")
    return out

def ingest(src):
    r = subprocess.run([sys.executable, os.path.join(HERE, "ingest.py"), src],
                       capture_output=True, text=True, cwd=ROOT)
    print(r.stdout.rstrip())
    if r.returncode: print(r.stderr[:600])
    return r.returncode == 0

def ambiguities(text_id):
    p = os.path.join(ROOT, "build", text_id, "text.json")
    a = json.load(open(p, encoding="utf-8"))
    out = []
    for s in a["sentences"]:
        for w in s["words"]:
            if w["provenance"] == "AMBIGUOUS-needs-resolution":
                out.append({"surface": w["surface"], "en": s["en"], "options": w["options"]})
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentences", type=int, default=9)
    ap.add_argument("--dry-run", action="store_true", help="fetch headlines only")
    ap.add_argument("--skip-if-done", action="store_true",
                    help="exit 0 without spending anything if today's news is already written")
    a = ap.parse_args()

    today = israel_today().isoformat()
    print(f"=== daily news · {today} (Asia/Jerusalem) ===")

    # For the catch-up run. GitHub states plainly that scheduled workflows can be delayed or
    # dropped under load, and a single daily fire means a dropped fire is a day with no news
    # (2026-08-27 was one). A second, later schedule covers that — but only if it costs nothing
    # on the ordinary day when the first one worked, hence this guard, ahead of both API calls.
    if a.skip_if_done and os.path.exists(os.path.join(ROOT, "texts", f"news-{today}.json")):
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
    print(f"writing {a.sentences} sentences in Palestinian…")
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
    src = os.path.join(ROOT, "texts", f"{tid}.json")
    json.dump({
        "id": tid, "kind": "news", "date": today,
        "title": {"ar": "أخبار اليوم", "en": f"Today's News — {today}"},
        "dialect": "pal", "subdialect": "urban",
        "source": "World headlines, written in spoken Palestinian by Claude. NOT native-validated.",
        "sentences": sents,
    }, open(src, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("annotating against Maknuune…")
    if not ingest(src): return 1

    amb = ambiguities(tid)
    if amb:
        print(f"resolving {len(amb)} ambiguous words (selecting from real entries)…")
        picks = resolve(c, amb)
        rp = paths.resolutions()
        res = json.load(open(rp, encoding="utf-8"))
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
        subprocess.run([sys.executable, os.path.join(HERE, "ingest.py"), src, "--audio"],
                       cwd=ROOT)
    else:
        print("audio: skipped (no ELEVENLABS_API_KEY)")

    # A news item can introduce a verb the app has never carried. build_verbs.py takes the
    # union of the top-3000 frequency cut with every verb lemma attested in build/*/text.json,
    # so re-running it here conjugates today's new verbs and folds them into verbs.js — the
    # word card, the Verbs section and Translate all pick them up with no further work. It
    # reads data/maknuune.parquet (tracked) and is deterministic, so a day with no new verbs
    # leaves the file byte-identical and the commit step simply sees nothing to stage.
    print("rebuilding the verb list (any new verb in today's news gets its paradigm)…")
    subprocess.run([sys.executable, os.path.join(HERE, "build_verbs.py")], cwd=ROOT)

    subprocess.run([sys.executable, os.path.join(HERE, "build_app.py")], cwd=ROOT)

    # FAIL LOUDLY on silent news. This step used to exit 0 whether or not any audio came
    # back, so a revoked/expired key produced a green run and a day of silent news that
    # nobody noticed until a learner opened it. A red run is the whole point of having CI.
    art = os.path.join(ROOT, "build", tid, "text.json")
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
