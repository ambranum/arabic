# ElevenLabs Voice Design test — 10 minutes, free, no API key

Majed is exhausted. He can't produce ē or ō at all (MSA doesn't have them), and he sounds
robotic regardless. Both problems need a different model. This tests the leading
candidate.

**No code, no API key, no credentials.** Free account, web playground, your ears.

---

## Step 1 — Voice Design

Go to **elevenlabs.io** → free account → **Voice Design** (not the Voice Library — the
library's "Palestinian"-tagged voices are known to still read MSA).

Paste this prompt. ElevenLabs' own guidance is to name the language and regional variant
in the **first sentence** to stop the model drifting to MSA, which is why it's front-loaded:

```
A 32-year-old Palestinian man from Ramallah speaking colloquial spoken Palestinian
Arabic (Levantine dialect), not Modern Standard Arabic. Warm, relaxed and conversational,
like a friend talking to you over coffee — not a newsreader, not formal. He speaks
everyday street dialect: qaf pronounced as a glottal stop, and the ē and ō vowels of
Levantine speech. Natural pacing, clean studio recording.
```

Generate a few. Pick the least formal one.

---

## Step 2 — The diagnostics

Paste these into the playground with your generated voice. **Model: Eleven v3.**

Each line is chosen to break in a specific, audible way. You don't need to judge "does
this sound Palestinian" in the abstract — just whether each word lands on the right side.

| Arabic | ❌ MSA says | ✅ Palestinian says | What it proves |
|---|---|---|---|
| فوق | `fawq` | `fō'` | **The killer.** Tests aw→ō *and* ق→ء at once. |
| بيت | `bayt` | `bēt` | ay→ē — the vowel Majed couldn't do |
| يوم | `yawm` | `yōm` | aw→ō |
| زيت | `zayt` | `zēt` | ay→ē |
| قديش | `qadīsh` | `addēsh` | ق→ء **and** ay→ē. The word that failed on Majed. |
| شو بدك؟ | (not MSA at all) | `shū biddak?` | Pure dialect — does it even handle it? |

Paste as one block:

```
فوق. بيت. يوم. زيت. قديش. شو بدك؟
```

---

## Step 3 — The real sentence

```
كل يوم الصبح، بصحى بكير وبعمل قهوة. بقعد عالبلكونة وبشرب فنجاني على مهلي. الشارع لسا هادي.
```

*Every morning I wake up early and make coffee. I sit on the balcony and drink my cup
slowly. The street is still quiet.*

Listen for: `ahwe` not `qahwa` · `bēt` not `bayt` · `yōm` not `yawm` · `bu'ud` not `aq'ud`
· and whether the case endings are **dropped** (dialect) or **pronounced** (MSA).

---

## Step 4 — Also try it *without* respelling

Feed it the normal spelling above. If a genuinely Palestinian-accented voice says `ahwe`
when reading قهوة, then **the respelling layer is unnecessary** — the model carries the
phonology natively and we can delete that whole idea from the pipeline. That's the
cleanest possible outcome, so it's worth checking before we build anything.

---

## What to tell me

1. Does it clear the **ē/ō ceiling** — `bēt`/`yōm`/`fō'`, or still `bayt`/`yawm`/`fawq`?
2. Does it sound like **a person** rather than a robot?
3. Does it sound **Palestinian**, or Lebanese/Syrian/generic Levantine? (Close is likely
   fine — Jordanian/Palestinian especially. Your call.)
4. Did respelling still help, or did the good voice make it moot?

If it clears 1 and 2, audio is solved and we build. If it fails on 1, no amount of
prompting fixes it and we go to human recordings — which, for a personal library, is
genuinely a fine answer, not a defeat.

---

## Not on the table

Cloning a real Palestinian speaker from a podcast or YouTube without their consent. The
audio is easy to get and that's exactly why it's worth naming: it's impersonation. A
cloned voice needs a person who agreed. Voice Design sidesteps this entirely by inventing
a speaker who doesn't exist.
