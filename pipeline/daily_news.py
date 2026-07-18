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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentences", type=int, default=9)
    ap.add_argument("--dry-run", action="store_true", help="fetch headlines only")
    a = ap.parse_args()

    today = datetime.date.today().isoformat()
    print(f"=== daily news · {today} ===")

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
    sents = write_sentences(c, heads, a.sentences)
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
        rp = os.path.join(HERE, "resolutions.json")
        res = json.load(open(rp, encoding="utf-8"))
        res.update(picks)
        json.dump(res, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  resolved {len(picks)}/{len(amb)}")
        if not ingest(src): return 1

    if os.environ.get("ELEVENLABS_API_KEY") and os.environ.get("ELEVENLABS_VOICE_ID"):
        print("generating audio…")
        subprocess.run([sys.executable, os.path.join(HERE, "ingest.py"), src, "--audio"],
                       cwd=ROOT)
    else:
        print("audio: skipped (no ElevenLabs keys)")

    subprocess.run([sys.executable, os.path.join(HERE, "build_app.py")], cwd=ROOT)
    print(f"\ndone — {tid}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
