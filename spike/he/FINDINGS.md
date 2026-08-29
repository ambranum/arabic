# Stage A — go/no-go

**Verdict: GO**, with one component sent back for rework and one question that needs your ears
before any corpus is voiced.

Stage A existed to answer one question in a week rather than a quarter: with no Maknuune for
Hebrew, can a module be built that keeps the project's rule — *word metadata is looked up, never
generated*? It can, and by a wider margin than expected, because Wiktionary turns out to carry
more than a lexicon: whole pointed conjugation tables, a Modern Israeli romanization per lemma,
binyanim, roots and noun patterns, all under CC BY-SA.

## The four bars

| | bar | measured | |
|---|---|---|---|
| **A1** lexicon coverage of live Hebrew news | ≥90% | **94.6%** | ✅ |
| **A2** niqqud → pronunciation | ≥99% | 95.4% | ⚠️ reframed — see below |
| **A3** conjugation accuracy | ≥98% | **98.99%** | ✅ |
| **A4** `eleven_v3` Hebrew | usable | mixed | ⚠️ rework |

### A1 — 94.6%

176,610 rows over 12,662 lemmas, 109,168 distinct surface keys, measured against 7,137 tokens of
live RSS from Ynet, Walla, Israel Hayom and Maariv. The 5.2% that misses is almost entirely
proper nouns — Smotrich, Trump, Jenin, Gantz, Khamenei — which is what `curated.py`'s `PROPER`
dict exists for on the Arabic side.

The finding that shapes Stage C: **49.9% of tokens are ambiguous, against 32.5% for Arabic.**
That is not a defect and it did not move when Wiktionary's root and acronym pseudo-entries were
filtered out. It is what unpointed Hebrew is. The untested lever is DICTA's Nakdan — adding
niqqud is precisely what disambiguates Hebrew, and the lexicon is already keyed on pointed
forms, so it should collapse most of that before any adjudication call is made.

### A2 — 95.4%, and the bar was aimed at the wrong thing

The transducer clears nothing like 99%, and it does not need to. Wiktionary supplies a
romanization for 16,428 entries outright, so pronunciation is **looked up** and `phon.py` is the
fallback for what the lexicon lacks — inflected forms, compounds, names, novel text. 95% on
unseen material is a good number for a generalizer.

Worth keeping: the oracle overturned four rules I was confident about (initial shva pronounced,
second-of-two-shvas, shva under dagesh, qamatz in a closed syllable) and surfaced one I had
missed that was worth more than all of them (the patach genuva — מָשִׁיחַ is *mashiakh*).
88.75% → 95.36%.

### A3 — 98.99%, and no engine needed

Wiktionary ships 2,084 pointed paradigms, 1,906 of them complete across all 24 slots, covering
all seven binyanim. **The paradigms are looked up, not derived** — the project's own rule applied
more strictly than the Arabic side manages, where `conjugate.py` has to derive 30 cells from
three. Pealim is not needed as an oracle and stays unshipped.

Verified against Wiktionary's own lemma romanization — which for a Hebrew verb *is* the 3ms
past, the cell the app banks a card under: 1768/1786, uniform across binyanim. 91% of verb tokens
in live news resolve to a verb that has a paradigm.

### A4 — Hebrew works; the vocabulary bank does not, yet

✅ `eleven_v3` accepts `language_code: he`. Both voices work.
✅ **Niqqud is read.** Duration is identical across repeats of the same text (5.36s twice) and
moves with the pointing (ספר 1.92s / סֵפֶר 1.36 / סַפָּר 0.88 / סִפֵּר 1.68 / סָפַר 1.84).
❌ **Determinism fails.** Same text, same seed, different audio — and not a metadata artefact;
the decoded PCM differs.
❌ **Single words are unstable.** Seconds-per-syllable across sixteen two-syllable words runs
0.24 to 1.16, a **4.8× spread**. יֶלֶד (*yeled*, two syllables) takes 2.32 seconds.
❌ **The planned mitigation does not exist.** `previous_text`/`next_text` return
`unsupported_model` on v3 — the only model that speaks Hebrew.

## What has to change before Stage C

1. **Build the 1,843-word bank with the timestamps endpoint, not bare synthesis.**
   `/v1/text-to-speech/{voice_id}/with-timestamps` returns character-level alignment: synthesize
   the word inside a real carrier sentence, then slice it out on the returned offsets. That buys
   the carrier's prosody without the unsupported parameter. **This must be proven before any
   corpus is voiced** — it is the one open engineering risk left in the audio path.

2. **Hebrew clips are immutable.** `pipeline/regen_audio.sh` deletes before re-voicing; under a
   non-deterministic model that silently changes the reading of every word in the corpus. A
   re-voice is a content change, not a refresh, and the script needs a guard saying so.

3. **A `PROPER` table for Hebrew**, seeded from the A1 miss list.

## What needs your ears

Nothing above tells us the readings are *correct* — only that the pointing is being read. Listen
to `spike/he/audio/sefer-1..4.mp3`, which should be four different words:

| clip | should say |
|---|---|
| `sefer-1` | *sefer* — book |
| `sefer-2` | *sapar* — barber |
| `sefer-3` | *siper* — he told |
| `sefer-4` | *safar* — he counted |

If those four are right, the audio path is sound and only the single-word packaging needs work.
If they are wrong, that is a much bigger problem than the packaging, and it is the one thing a
measurement cannot settle.

## Cost of Stage B and C, unchanged by any of this

The refactor pays for itself in Arabic alone — it halves a 22 MB page load and deletes a
conjugation renderer that currently exists twice. The content remains the real expense: 90
stories, 266 book chapters, 50 lesson units, 20 grammar lessons, 64 reactions, 12 dialogues, all
of it again in Hebrew.
