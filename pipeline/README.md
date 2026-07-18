# Ingest pipeline

Raw Palestinian text → fully annotated, cached artifact.

## Run

```bash
python3 pipeline/ingest.py texts/morning-coffee.json            # annotate only
python3 pipeline/ingest.py texts/morning-coffee.json --audio    # + MP3s
```

Audio needs (never committed, read from env):

```bash
export ELEVENLABS_API_KEY=...
export ELEVENLABS_VOICE_ID=...      # the Palestinian Voice Design voice
export PAL_SUBDIALECT=urban         # urban | rural | bedouin  (default urban)
```

Without the keys it still emits the artifact, `audio: null`.

## The rule

**Metadata is looked up, never generated.** Claude got 15% of roots wrong by
generating them, and every error was MSA leakage (SPEC 7.4.1).

```
text → peel clitics (morphology gives the exact form: b- ⇒ VERB:I)
     → retrieve REAL Maknuune candidates, untagged-first
     → 1 survivor?  auto-fill            provenance maknuune:unique
       n survivors? resolutions.json     provenance maknuune:resolved
       0 survivors? flag, leave empty    provenance unresolved   ← never guess
     → realize CAPHI variables for the sub-dialect
     → emit build/<id>/text.json
```

Claude's job is **selection**, not generation. It cannot invent ر-و-ح when the only
options are what Maknuune actually contains.

## Three bugs this survived — all the same bug

1. Claude generates roots → 15% wrong, all MSA leakage.
2. Naive lookup → 100% "coverage", ~40% wrong sense (`بقعد` = "wooden bucket").
3. Unique-*root* auto-fill → right root, wrong word (`بقعد` = causative "make sb sit").

Each time the fix was **narrow it mechanically, then choose from real entries** — never
take `cands[0]`. Auto-fill requires exactly one survivor.

## Files

| | |
|---|---|
| `maknuune.py` | lexicon + clitic morphology |
| `subdialect.py` | CAPHI++ variables → sub-dialect (SPEC 7.4.4) |
| `ingest.py` | orchestrator |
| `resolutions.json` | audit trail: word → Maknuune ID, with reasons |

`resolutions.json` is the point: every choice is data, checkable against
`data/maknuune.parquet`. Decisions are reviewable, not buried in code.

## Known gap

Maknuune stores **citation** forms (`yis.7a`), the text has **conjugated** ones
(`baṣḥa`). The hover card is fully sourced; the inline surface transliteration is not.
See SPEC 7.4.6.

## Car sessions

```bash
python3 pipeline/car_session.py texts/car-01-reactions.json --gap 3          # script only
python3 pipeline/car_session.py texts/car-01-reactions.json --audio          # + MP3s
```

**A drill, not a track.** `cue (English) → GAP: you speak → answer (Palestinian) → gap: repeat`.
The gap is the product. Passive listening produces almost nothing (LEARNING-SYSTEM §2.4);
hearing the answer before you've tried is the failure mode.

**Chunks are NOT Maknuune-sourced.** Maknuune is a content lexicon — معليش، والله، صحتين،
يسلمو إيديك are not in it, and its PHRASE entries are idioms, not conversational glue. The
authority for this deck is a **native speaker**. Validate with `design/chunk-review.html`
before generating audio: once it's drilled, an error is permanent.

## Provenance discipline — a near-miss worth remembering

A smoke test of `design/chunk-review.html` was left displayed in the browser pane in a
completed state. Its synthetic output — *"13. معليش → she says معلش, 1 of 30 flagged"* —
was later handed back as if it were the native speaker's review.

It was caught only because the fabricated answer matched the test byte-for-byte.

**The dangerous part: the fake was plausible.** Both معلش and معليش circulate (معلش leans
Egyptian/Lebanese, معليش leans Palestinian). Accepted, it would have "corrected" the deck
toward the wrong dialect based on invented data, and would have looked exactly like the
subtle catch a real native speaker makes.

Guards added:
- Every export is stamped with a **timestamp and session id**. Unstamped output is not a review.
- No output renders at all until the reviewer **explicitly attests** they are a real person.
- Never leave a test-filled form displayed. Reset the pane after testing.

The rule that governs the whole pipeline — *know where every fact came from, never let a
guess masquerade as an answer* — applies to *human* validation too, and applies hardest
exactly where the human is the only check that exists.

## News imports

`texts/news-YYYY-MM-DD.json` with `"kind": "news"` and a `"date"`. The app finds today's
by date and puts it on the home screen.

Written as you'd **tell** someone the news, not as a newsreader reads it — newsreader
Arabic is fuṣḥā, which is not the target register.

### What news vocabulary taught us

First news run: **37% of words unresolved**, against 0% for the morning-coffee text.
News is simply harder, and it exposed three fixable classes:

| Problem | Fix |
|---|---|
| Dialect vs CODA spelling (كتير / كثير, تانية / ثانية, أكتر / أكثر) | Try ت↔ث, د↔ذ, ض↔ظ variants — **before** clitic stripping, or كتير matches the fragment تير instead of the real word كثير |
| Past-tense suffixes (عملت، نزلوا، توقعوا) | Strip ـت ـوا ـنا ـتي; only b-imperfect prefixes were handled before |
| Proper nouns, modern terms | `curated.py` — no lexicon has Bangkok or "artificial intelligence" |

After those: **0% unresolved.** All three fixes benefit every future text.

Also found: **عم**, the Levantine progressive particle, is core grammar and is not in
Maknuune as such (only عمّ "paternal uncle"). It is now a curated function word.

### Curated ≠ sourced

`curated.py` entries are hand-written. A bug had the vocalizer overwrite their provenance
with `lexicon:exact`, which claimed Maknuune sourced words we invented. Fixed — curated
entries keep `curated` provenance and the app labels them
"hand-written by us, not from the lexicon". **Never let hand-written data wear a
lexicon label.**
