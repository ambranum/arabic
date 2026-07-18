# Language Reader — Spec Part I (v0.2 draft)

> **This document specs the reader.** The reader is now **one activity in one slot** of a
> larger system — see **`LEARNING-SYSTEM.md`** (Part II) for the scheduler, the curriculum,
> and the daily loop. Read Part II first for what the app *is*; read this for how reading
> works inside it.
>
> **Status: both blockers are cleared.** The Palestinian voice is solved (§7.2.0 —
> ElevenLabs Voice Design v3), which unblocks the commute, the fluency engine, and the
> multi-party dinner-table audio. Validation is solved (§7.3, §7.4.1) — a native Levantine
> ear for prose, the Maknuune lexicon for metadata. **The design phase is over; this is
> now a build.**

Working title. A web app for learning a language by *reading real texts* with every
support layer you'd want available on demand, and then *speaking* about what you read.

Built language-agnostic, loaded with Arabic first.

---

## 1. The core idea

Most language tools give you either a dictionary or a textbook. This gives you a text —
and then lets you peel back as many layers as you need to actually understand it, sound
it out, and say it. The layers are toggles, not modes: you turn on what you need today
and turn it off as you improve.

The reading surface is the product. Everything else (lessons, Anki, the speaking bot)
hangs off it.

---

## 2. The reader

### 2.1 Parallel translation
English on one side, target-language text on the other, aligned. Reading English and
seeing the direct translation next to it.

**DECIDED — direction: Arabic-primary.** Arabic is the text you're reading. English is a
collapsible safety net you pull up when stuck, not a column you read. This is the
immersion mode and the English is a crutch to wean off.

**Open question — alignment granularity:** sentence-by-sentence is the safe default
(paragraph blocks feel too coarse to be useful; word-by-word breaks down badly for
Arabic word order). Sentence-aligned pairs that highlight together on hover.

### 2.2 Word-level hover dictionary
Hover any word → popup with:
- Lemma (dictionary form) — critical for Arabic, since surface forms are heavily inflected
- Root (the triliteral root, e.g. ك-ت-ب) — this is *the* organizing principle of Arabic
  vocabulary and a major learning lever
- Part of speech, gender/number where relevant
- Gloss / definitions
- The word fully vocalized
- Transliteration
- Audio for that word alone
- "Add to my unknown list" button

### 2.3 Vocalization toggle (tashkīl / harakāt)
Real Arabic text is written *unvocalized* — the short vowels are omitted and you're
expected to know them. This is the single biggest wall for learners. Toggle:
- **Full vocalization** — every letter marked, sound out anything
- **Partial** — only ambiguous / hard words marked (nice intermediate step)
- **None** — how it's actually written in the wild

This requires a diacritization engine, not just a font toggle. See §7 Risks.

### 2.4 Transliteration toggle
Latin-script pronunciation guide. Separate toggle from vocalization — some people want
one, some the other, beginners want both.

**Open question:** which scheme? Academic (IJMES/DIN) vs. chat-Arabic (3arabizi, "3" for
ع, "7" for ح). Chat-Arabic is what people actually text in and is arguably more useful
for a spoken-dialect learner. Possibly offer both.

### 2.5 Audio
- Full-text playback with word highlighting that follows along (karaoke-style)
- Per-sentence playback
- Per-word playback from the hover card
- Playback speed control (slow is essential for dialect)

Audio must be in the **selected dialect**, not MSA-read-aloud. An MSA recording of a
Levantine sentence is worse than useless.

### 2.6 Register toggle — MSA ↔ dialect
This is the piece that makes the app different from everything else.

Almost all written Arabic on the internet is **Modern Standard Arabic (fuṣḥā)** — the
formal register. Almost all *speech* is dialect (Levantine, Egyptian, Gulf, Maghrebi…),
and they differ enough in vocabulary, grammar, and pronunciation to be a real barrier.
A learner who reads MSA all day still can't order coffee in Ramallah.

So: for a given text, show it in
- MSA (as sourced), and/or
- the spoken dialect you've selected (Palestinian Levantine first)

side by side or toggled. The dialect version is generated (see §4).

---

## 3. Marking vocabulary & Anki export

While reading, click/select words you don't know → they collect into a per-text
"unknown words" list. Review the list, then export.

**Export to Anki** (feature extension, not v1 core):
- `.apkg` or CSV export
- Card fields: word (vocalized), word (unvocalized), root, lemma, gloss, the *sentence
  it appeared in* (cloze context is what makes vocab stick), audio file
- Deck per text, or one growing deck — TBD

Marked words should also persist as a personal known/unknown model that feeds back into
the reader: known words render plain, unknown words get a subtle highlight. That's the
loop that makes this worth using daily.

---

## 4. Text library & lesson creation

### 4.1 Loading texts
The library is a set of texts you can open, each with the full toggle set. Sources:

1. **Claude finds real texts on the internet** — news, stories, essays, at a stated
   level. Preferred: authentic material.
2. **Claude generates lessons/texts** — when nothing good exists at the right level or
   on the right topic. Level-targeted, topic-targeted.
3. **User pastes/uploads their own text.**

### 4.2 The MSA→dialect problem
Found texts will be MSA. To be useful for a *spoken* learner they need a dialect
rendering. So the ingest pipeline for any text is roughly:

```
source text (MSA)
  → English translation
  → dialect translation (Palestinian / Egyptian / …)
  → vocalization pass (each version)
  → transliteration pass
  → tokenize + lemmatize + root-extract + gloss each word
  → TTS audio (per word, per sentence, full text) in the target dialect
  → store as a fully-annotated text object
```

That's a heavyweight per-text pipeline. It should run **once at ingest time**, not on
page load — a text becomes a cached, static, annotated artifact. This is the main
architectural decision in the app.

### 4.3 Levels
Texts need a difficulty rating so "find me something to read" works. Open question:
CEFR (A1–C2)? Custom levels? Derived from % of words outside your known list — which is
attractive because it's *personal* and falls out of the vocab model for free.

---

## 5. Speaking practice

A conversational bot that speaks in the dialect you're studying, for whatever language.

Purpose: not just learn new vocabulary, but **practice speaking at the same time**. The
strong version ties it to the reader — you just read a text about the market, so the bot
talks with you about the market, using that text's vocabulary and pushing your marked-
unknown words at you. That closes the loop between reading and production.

Needs: speech-to-text (dialect Arabic ASR — hard), the conversation model, TTS out
(dialect), and ideally gentle correction/feedback.

Almost certainly a phase 2+ feature. It is the biggest technical lift here and the
reader has to be good first.

---

## 6. Shape & scope

**Web app.** Open a text → get the toggle panel → read → mark words → export.

Multi-language from the ground up: language is a toggle/setting, not a hardcoded
assumption. Load Arabic first. The architecture shouldn't have "Arabic" baked in
anywhere except a config + data layer — but it *does* need to survive RTL, non-Latin
script, root morphology, and register-splitting, which are exactly the hard cases. If
Arabic works, most things work.

(Hebrew was mentioned first, then corrected to Arabic. Noting it as a plausible second
language: also Semitic, also root-based, also RTL, also has a vocalization system —
much of the Arabic machinery would transfer.)

**DECIDED — audience: personal tool.** Built for one user, for now. No accounts, no
hosting story, copyright of sourced texts is a non-issue at this scale, and we can be
scrappy about per-text pipeline cost. Revisit only if it ever goes wider.

### Phasing

- **Phase 0 — prove it. ← DECIDED, this is the starting point.** One hand-annotated
  Palestinian text, full toggle set, hover dictionary, audio. No pipeline, no accounts.
  Answers the only question that matters first: is this actually good to use? If the
  reading experience isn't compelling on one text, no amount of pipeline saves it.
- **Phase 1 — the reader.** Ingest pipeline, text library, vocab marking, persistence.
- **Phase 2 — export & lessons.** Anki export, Claude-generated/-sourced lessons, levels.
- **Phase 3 — speaking.** The dialect conversation bot.
- **Phase 4 — more languages.**

---

## 7. Risks / hard parts

| Thing | Why it's hard |
|---|---|
| **Automatic diacritization** | Real accuracy problem; existing tools (Farasa, Mishkal, CAMeL) are decent for MSA, weaker for dialect. Errors here directly teach wrong pronunciation. |
| **You cannot style diacritics independently in HTML** | Still true. Verified, §7.1. Cosmetic only — the show/hide toggle works. |
| ~~**Dialect TTS**~~ | ✅ **SOLVED** — ElevenLabs Voice Design v3, see §7.2.0. |
| **Dialect ASR** | Same problem, worse. Gates the speaking bot. |
| **MSA→dialect translation quality** | No gold standard, hard to validate, and dialects vary by city. Needs a "this is machine-generated" honesty stance. |
| ~~**Dialect lexicography**~~ | ✅ **SOLVED** — Maknuune, 36K Palestinian entries, in `data/`. See §7.4. |
| **Per-text pipeline cost** | Every layer × every text × every dialect. Cache aggressively; make ingest an explicit, reviewable step. |
| **Copyright** | "Claude finds texts on the internet" and stores them, annotated. Fine for personal use; a real question if this becomes a product. |

---

### 7.1 Finding: diacritics can't be colored separately from their letter

Found while building the mockup, and worth writing down because it kills a whole
category of design ideas.

**What happens:** wrap a ḥaraka in its own `<span>` and give it a color — even
`#00FF00 !important` — and it renders in the *base letter's* color. `getComputedStyle`
cheerfully reports the color you asked for; the pixels ignore it. Verified across Geeza
Pro, SF Arabic, Damascus, Al Bayan, and generic serif, so it is not a font quirk.

**Why:** Arabic text shaping composes each base letter plus its combining marks into a
single glyph cluster. The cluster is painted as one unit in the color of the run that
owns the base character. An inline element boundary around the mark doesn't split the
cluster.

**What still works:**
- **Hiding** marks (`display: none`) — removes the character from the shaping input
  entirely, so the toggle itself is completely fine. The core feature is safe.
- **Coloring at word granularity** — a whole word is one run and takes color normally.
- Underlines, backgrounds, and box-shadows on the word.

**Consequence:** the vocalization toggle works exactly as specced. But "show the vowels
in a different color from the consonantal skeleton" — which is a genuinely nice teaching
idea, and is how the manuscript tradition actually did it — is not available in plain
HTML text.

**If we ever want it:** it requires glyph-level rendering — shape the text yourself with
harfbuzzjs, get glyph IDs and positions, and paint mark glyphs separately to canvas or
SVG. That's a real investment, but it's the same machinery that would give precise
glyph-level karaoke highlighting, so the two features would share a foundation. Not
Phase 0.

**For now:** the mockup moves the red to word granularity — in Partial mode, the words
that keep their marks get a red rule beneath them. Those are the words you'd actually
misread, which is the reason tashkīl was invented in the first place.

---

### 7.2.0 ✅ RESOLVED — the voice problem is solved

**ElevenLabs Voice Design v3, prompted for a Palestinian speaker.** Listened and confirmed
by the user:

1. **It clears the ē/ō ceiling.** `fō'` not `fawq`. `bēt` not `bayt`. `yōm` not `yawm`.
2. **It sounds like a person**, not a robot.
3. **It sounds Palestinian** — not Lebanese, not Syrian, not generic Levantine.

**Tested on normal, correctly-spelled Arabic.** No tricks, no respelling. The model carries
Levantine phonology natively.

**The ceiling in §7.2.2 was never a property of Arabic. It was a property of Majed.** A
legacy MSA on-device voice cannot produce vowels its inventory lacks; a modern model
trained on real Levantine speech simply has them. Everything downstream of that diagnosis
was reasoning correctly from a bad sample.

**It automates.** The v3 API is public: `model_id: eleven_v3`, official Python/JS SDKs,
3,000 chars/request, ~$0.10 per 1,000 characters. A fully annotated text with per-word
audio ≈ **$0.15**; a 100-text library ≈ **$15**. Generate once at ingest, cache the MP3s
(§4.2) — the cost is one-time per text, not per listen.

**Unblocked by this:** the car (~40% of study time and 100% of speaking time —
`LEARNING-SYSTEM.md` §2.5), shadowing, 4/3/2, per-word audio in the hover card, and the
reader's whole audio layer.

**New capability — the dinner table becomes buildable.** Voice Design mints *distinct*
voices on demand, and v3 ships **Text to Dialogue** for multi-speaker conversational audio.
So **multi-party listening** — following four Palestinians talking over each other, the
north-star skill nobody trains (`LEARNING-SYSTEM.md` §1, §5 phase 6) — can be synthesized
rather than hoped for. This was previously not just blocked but inconceivable.

**Open:** save the designed voice in the account and record its `voice_id`; a voice you
can't retrieve isn't a dependency, it's an anecdote. Also unmeasured: whether quality
holds on long-form and on emotional/narrative register (§7.4.3's caveat applies to audio
too — it was validated on short, easy material).

§7.2 below is retained as the record of how we got here, and because the market analysis
is still true: **no vendor ships a Palestinian voice.** We didn't find one. We generated
one.

---

### 7.2 Finding: there is no free path to Palestinian audio *(superseded by §7.2.0)*

Checked on the actual dev machine. Of **157** installed speech voices, exactly **one**
is Arabic: `Majed`, `ar-001` — where `001` is the "world" region code, meaning generic
MSA. **Zero Levantine. Zero Palestinian.**

So the built-in TTS path is:
- **Fine for MSA.** The mockup now uses Majed for real, with sentence highlighting
  driven by the utterance's own `onend` event. Free, offline, correct register.
- **Useless for Palestinian.** Majed would read قهوة as *qahwa* where a Palestinian says
  *ahwe*, أقعد as *ajlis* rather than *buqʿud*, and would restore all the case endings
  the dialect drops. That's not "slightly off" — it drills in exactly the habit the app
  exists to break.

**Decision taken in the mockup:** MSA speaks, Palestinian stays silent, and the UI says
why. The per-word "Hear it" button is disabled on the dialect side with a tooltip
explaining that the fuṣḥā voice would mispronounce it. The gap is visible on purpose.

Word-level karaoke also needs forced alignment, which no TTS gives for free. The mockup
therefore highlights **per sentence** when speaking for real, because that's the only
timing it honestly knows. Word-level timing is a Phase 1 pipeline artifact.

### 7.2.1 The market, surveyed

**Headline: no vendor ships a Palestinian TTS voice.** Not one.

| Vendor | Levantine offering | Verdict |
|---|---|---|
| **Azure** | 16 Arabic locales. `ar-JO` (Sana, Taim), `ar-LB` (Layla, Rami), `ar-SY` (Amany, Laith). **No `ar-PS`.** | Closest locale available. `ar-PS` exists in Azure **only for speech-to-*text***, never TTS — a telling asymmetry: they can hear Palestinian, they won't speak it. |
| **ElevenLabs** | Arabic as **one undifferentiated language**. No dialect parameter. Voice cloning across 70+ languages. | Best raw quality; no dialect control. Cloning is the real lever — see below. |
| **Google** | `ar-XA` — pan-Arabic, i.e. MSA. | No dialect. |
| **Amazon Polly** | Zeina (MSA), Hala (`ar-AE`). | No Levantine. |
| **Narakeet / Nabarati** | Marketing claims Palestinian among "14 dialects". | Unverified. Treat as claims until heard. |

**The critical unknown, undocumented by anyone:** whether Azure's regional Arabic voices
actually *speak dialect* or merely read MSA with a regional accent. No vendor documents
this. It cannot be resolved by reading — only by listening.

**Prior art, same use case.** Salah Adawi tried exactly this — Palestinian TTS for Anki
decks. Found ElevenLabs voices *tagged Palestinian* still produced "formal, Modern
Standard Arabic (MSA/Fusha) form, not the spoken form of Palestinian Arabic," and
concluded **Eleven v3's base model** was the most promising path. A tag saying
"Palestinian" does not make a voice speak Palestinian.

**Ranked options:**
1. **ElevenLabs Voice Design v3 — generate a Palestinian voice from a text prompt.**
   The current lead. Advertised as supporting "hundreds of localized accents," and their
   own prompting guidance is to *"be explicit about language and dialect — always specify
   the language and regional variant in the first sentence to prevent drift."* Requires
   **no speaker and no recordings**, works on the free tier, and — decisive given §7.3 —
   produces a **synthetic voice, not a copy of a real person**, so it raises no consent
   question. If the resulting voice's phonology is genuinely Levantine, it should clear
   the ē/ō ceiling that respelling cannot, because the model would carry Levantine vowels
   natively rather than substituting graphemes.
2. **ElevenLabs Professional Voice Clone of a *consenting* Palestinian speaker.** Highest
   authenticity. A clone's "accent characteristics carry through every language," and
   training on the target language is recommended. Needs 30 min–2 hrs of clean audio.
   Ties to §7.3 — the person who validates the Arabic could be the voice.
   **Boundary: cloning a real person's voice requires their explicit consent.** Scraping
   a Palestinian podcaster or YouTuber to clone them is impersonation, not a shortcut,
   and is out of scope regardless of how convenient the audio is.
3. **Azure `ar-JO`.** Cheap, instant, closest available locale. Unknown whether it speaks
   dialect or MSA-with-accent. Worth an audition, but note it may hit the same ē/ō
   ceiling if it's fundamentally an MSA voice wearing an accent.
4. **Human recordings.** Doesn't scale, but a personal library is small. Best quality by
   definition, and sidesteps every model problem at once.

Options 1–3 all need the same thing before any of them can be trusted: **someone listens.**
See §7.3 — the user is the only sensor this project has.

### 7.2.2 ❌ DELETED — the respelling layer *(do not build this)*

**Killed by §7.2.0.** Respelling was a workaround for a broken voice. A working voice
needs no workaround — and feeding the pipeline deliberately misspelled Arabic to fix a
problem that no longer exists would actively *cause* harm: wrong spellings on screen,
wrong data in the corpus, wrong words in Anki.

The reasoning below was sound and the conclusion was wrong, because the sample was wrong.
It generalized from the only Arabic voice on one Mac — a legacy MSA voice — to "Arabic
TTS." Kept as the record of a plausible idea that a real test destroyed.

**The transferable lesson: a ceiling measured on one bad sample is not a ceiling.** Test
the good tool before you architect around the limits of the bad one.

*(Original reasoning follows.)*

### 7.2.2-old The lever: we control the TTS input

Levantine pronounces ق as a **glottal stop** in most words — *but still writes it as ق*.
So the orthography itself is what drags every engine back to fuṣḥā. قهوة spelled that
way invites "qahwa" from any model.

But this app **generates its own dialect text**, which means the string fed to the engine
need not be the string on screen. Display قَهْوة; send أَهْوة. A **TTS-input spelling
layer**, separate from the display text, could extract dialect phonology from a generic
Arabic voice with no dialect-specific model at all.

If this works, it reframes the problem from "find a Palestinian model" (nothing exists)
to "spell for the engine" (fully under our control) — and it would improve *every*
option above, including a cloned voice.

`design/voice-test.html` tests exactly this on the free local MSA voice: seven minimal
pairs plus a sentence, standard spelling vs. respelled, ق→ء and ث/ذ→ت/د.

**VERDICT (listened): "a little better, but still not great."** Partially validated, and
the failure mode is informative.

**Respelling fixes consonants. It cannot fix vowels. This is a hard ceiling.**

- **Works:** ق→ء and ث/ذ→ت/د succeed because MSA's inventory *contains* ء, ت, د. We're
  swapping to phonemes the voice already has.
- **Cannot work:** **MSA has no /eː/ or /oː/.** Levantine's ē and ō descend from
  monophthongized *ay* and *aw*, which MSA never underwent. Worse, Arabic script cannot
  write ē distinctly from ī — both are ي. So there is no respelling that produces them.
  قديش → أديش still yields *addīsh*, not *addēsh* (the reported failure, exactly). بيت
  stays *bayt*, never *bēt*; يوم stays *yawm*, never *yōm*.

Since ē and ō saturate Levantine speech, an MSA voice is capped at "a little better"
no matter how the text is spelled. That is precisely the observed result.

**Second, independent finding: "sounds like a robot, not a Palestinian speaker."**
Naturalness is a separate axis from accent. Majed is a legacy on-device voice — of 143
voices on the machine it's the only Arabic one, basic tier, no Enhanced/Premium variant
available. It would sound robotic reading flawless Palestinian.

**Conclusion: Majed is exhausted.** Both remaining problems — the ē/ō gap and
naturalness — require a *different model*, not different text. Respelling is retained as
a cheap consonant-level assist, not a solution. It is a minor lever, not the answer.

### 7.2.3 Bonus find: the dictionary layer is solved

Not voice, but it fell out of the same search and it's a significant win.

Birzeit University's Sina Institute (Mustafa Jarrar) has built exactly the Palestinian
resources this app's hover card needs:
- **Curras** — the first morphologically annotated Palestinian Arabic corpus, 56K+ tokens
  with rich morphological and lexical features, linked to SAMA lemmas.
- **Maknuune** — a large open **Palestinian Arabic lexicon**, extracted from Curras.
- **Baladi** — the Lebanese counterpart; Curras+Baladi form a Levantine corpus.

§7 lists "dialect lexicography" as a risk on the grounds that dictionaries are
MSA-centric. **Maknuune substantially answers that** for Palestinian specifically. Worth
evaluating properly for the lemma/root/gloss layer instead of hand-writing glosses or
generating them.

### 7.3 Validation — RESOLVED (mostly), via two complementary halves

**Superseded.** This was the project's most serious unsolved risk. It now has a real
answer, from two sources that cover each other's blind spots almost exactly.

**Half 1 — a native Levantine ear (the user's wife, a Lebanese native speaker).**
Judges what no lexicon can: *does this sound like a human being?* Catches MSA leakage
(the single biggest failure mode of generated dialect), unnatural phrasing, broken
grammar, and "nobody would ever say that." **Cannot** reliably judge
Palestinian-vs-Lebanese lexical choice — she's Lebanese, and the target is Palestinian.

**Half 2 — Maknuune, the open Palestinian lexicon.** Judges what no single speaker can
hold in their head: *is this the Palestinian word, root, and form?* Has no opinion on
naturalness.

| | Word-level Palestinian specificity | Sentence-level naturalness |
|---|---|---|
| **Wife** | ✗ | ✓✓ |
| **Maknuune** | ✓✓ | ✗ |

Together: near-complete coverage. **Ask each the question it can actually answer** —
`design/native-review.html` is built on exactly this principle and explicitly tells her
we are *not* asking "is this Palestinian?"

**Half 3 (buildable) — the Curras↔Baladi delta.** Curras (Palestinian) and Baladi
(Lebanese) are both annotated against **SAMA lemmas and tags** — i.e. joined on a shared
backbone. So the Lebanese–Palestinian divergence is *computable*, not vibes. That lets us
**mechanically flag the items where her judgment doesn't transfer** and route only those
to Maknuune or a Palestinian speaker. Everything outside the delta, she is a full
validator.

**Still true regardless:** mark generated dialect as unverified in the UI until a human
has seen it. Prefer authentic sourced text where it exists.

### 7.4 Resource: Maknuune answers four layers at once

[palestine-lexicon.org](https://palestine-lexicon.org/) ·
[CAMeL-Lab/maknuune_lexicon](https://github.com/CAMeL-Lab/maknuune_lexicon) · CC BY-SA 4.0
Shahd Dibas (Oxford) & Nizar Habash (NYU Abu Dhabi).

**36K entries · 17K lemmas · 3.7K roots.** Every entry carries:

| Maknuune field | Feeds |
|---|---|
| Diacritized orthography | **The vocalization toggle** (§2.3) — real Palestinian tashkīl, not generated |
| **Phonological transcription** | **The transliteration layer** (§2.4) — and the *ground truth for ē/ō*, which Arabic script cannot encode (§7.2.2) |
| English gloss, root, lemma, POS | **The hover card** (§2.2) — human-annotated, not generated |
| **Collocations & associated phrases** | **The formulaic chunks** the entire learning system runs on (`LEARNING-SYSTEM.md` §4) |
| Notes on regional usage within Palestine | Sub-dialect accuracy |

This substantially retires the "dialect lexicography" risk in §7 and removes the need to
*generate* the vocabulary layer at all. **Evaluate before building any of it by hand.**

Also open (CC BY 4.0), via the [Currasat portal](https://sina.birzeit.edu/currasat/) —
download by Google Form, no API:
- **Curras** — Palestinian, ~56K tokens, morphologically annotated
- **Baladi** — Lebanese, ~9.6K tokens
- **Nabra** — Syrian, ~60K tokens across 10 regional variants

All annotated with POS, stem, prefixes, suffixes, lemma, English gloss, sourced from
social media, blogs, and poems — the only places written dialect naturally occurs.

### 7.4.1 RESULT: Maknuune is obtained, and it caught real errors

**The lexicon is in hand.** Not the Google Form — the parquet is on HuggingFace at
**`arbml/Maknuune`** (3.5 MB, 36,302 rows). Direct:
`https://huggingface.co/datasets/arbml/Maknuune/resolve/main/data/train-00000-of-00001.parquet`

Columns: `ID · ROOT · ROOT_NTWS · ROOT_1 · LEMMA · LEMMA_SEARCH · FORM · LEMMA_BW ·
FORM_BW · CAPHI++ · ANALYSIS · GLOSS · GLOSS_MSA · EXAMPLE_USAGE · NOTES · SOURCE ·
ANNOTATOR`

**CAPHI++ is the ē/ō ground truth.** Arabizi-style phonetic transcription: `2`=glottal
stop, `3`=ʿayn, `7`=ḥāʾ, `aa/uu`=long vowels, and **`e`/`oo` for the Levantine vowels
Arabic script cannot write**. `إِبْرِة` → `2 i b r e`. `بَيْت` → `biit`. `يَوْم` → `yoom`.
This is what §2.4's transliteration layer should render, and what any TTS output should be
*graded* against (though not driven by — see §7.5).

**First validation run — Claude's hand-written glosses vs. Maknuune (21 rooted claims):**

| | |
|---|---|
| Roots correct | **17** |
| Roots wrong | **3** (~15%) |
| Not found (misspelled) | **1** |

| Claude said | Maknuune | |
|---|---|---|
| ريحة → ر-و-ح | **ر-ي-ح** | MSA association |
| هادي → ه-د-أ | **ه-د-ي** | *literally the MSA root* |
| حِلو → ح-ل-و | **ح-ل-ي** | MSA etymology |
| لِسّا → "no root, pure dialect" | **ل-س-س**, spelled **لِسَّه** | confidently wrong twice |

**Every error is MSA leakage — at the root level.** The predicted failure mode, confirmed,
in the one field a learner would never think to question.

**The layer split matters.** The user (who has studied some Palestinian) reviewed the
sentences and judged them correct — and *he was right*. Zero sentence errors. All errors
were in the **metadata**: roots and lemma spelling. Human review covers the visible layer;
Maknuune covers the invisible one. **Neither alone is sufficient**, which is a sharper
version of the §7.3 argument than the wife/Maknuune split alone.

Root errors are not cosmetic: the root is Arabic's filing system and the elaborative-
encoding hook the whole reader is built on (§2.2). A wrong root files the word in the
wrong drawer permanently.

**Fixed in `design/reader-mockup.html`** — Palestinian entries only. The MSA column keeps
ر-و-ح and ه-د-أ because those are genuinely correct *for MSA*. The divergence is real and
now visible: toggle the register and رائحة (ر-و-ح) becomes ريحة (ر-ي-ح) — same concept,
different root. **That's a teaching moment the validation produced for free.**

**Standing policy: never ship a generated root. Look it up.**

### 7.4.2 The pipeline architecture, derived from failure

Three iterations, each one's failure producing the next design.

**1. Claude generates metadata.** → 15% root error rate, every error MSA leakage (§7.4.1).

**2. Naive Maknuune lookup.** → *100% coverage, ~40% wrong sense.* `كل` matched "eat!",
`بقعد` matched "wooden bucket for milking", `على` matched "elevate!". **Coverage is not
accuracy.** This did not remove the guessing, it relocated it from the model to the
matcher. Same bug, different hat.

**3. Morphology-constrained candidate retrieval.** → **88% unambiguous, roots reliable.**
The unlock wasn't better matching, it was *morphology*: the clitic tells you the POS.
`ب-` marks a habitual verb, so entries tagged `ADJ`/`NOUN` are inadmissible before you
look at anything else. `بصحى` stops matching صِحِّي ("healthy") and lands on ص.ح.و.

**The architecture:**

```
text → peel clitics (morphology gives expected POS)
     → retrieve the REAL Maknuune candidate set
     → 1 candidate?  auto-fill, done            (88%)
       n candidates? Claude SELECTS by context  (12%)
       0 candidates? flag for a human — never guess
```

**Claude's job is selection, not generation.** It cannot invent ر-و-ح if the only options
are what Maknuune actually contains. Constrained choice among real entries plays to what
models are good at (context) and fences off what they're bad at (confident invention).
This is the load-bearing design rule of the whole ingest pipeline.

**Layer status:**

| Layer | State |
|---|---|
| **Root** | Reliable via lookup. *The layer Claude got wrong is now the safest.* |
| **Sense / gloss** | Still picks wrong senses (`بقعد`→causative, `لحظة`→interjection). Needs the disambiguation step. |
| **Function words** | `على` has no clean prepositional entry — Maknuune is a content lexicon. Expect a gap; hand-curate the closed class (it's small and finite). |

Code: `data/annotate.py` (v1, naive — kept as the cautionary case), `data/annotate2.py`
(v2, morphology-constrained).

### 7.4.3 Native review result (n=5)

Wife (Lebanese native) reviewed the five reader sentences: **0 of 5 flagged.**

**Converging evidence across three independent checks:**

| Checker | Layer | Result |
|---|---|---|
| Wife | sentences | 0/5 flagged |
| User (some Palestinian) | sentences | "mostly correct" |
| Maknuune | metadata | 4 errors |

All three agree: **the prose is sound, the metadata was not.** This is the empirical basis
for §7.4.2's rule — *generate the sentences, look up the metadata.*

**Do not over-read it.** n=5, and those five were the easiest register in the language:
short, present-tense, concrete, domestic — and hand-written as a showcase. 0/5 is
statistically consistent with a true error rate near 50%. It refutes "Claude's Levantine
is garbage"; it does **not** establish "generated Palestinian is safe." The dinner-table
target register (feelings, ambivalence, humour, narrative) is far harder and remains
untested.

**Next real test:** generated text at length, on varied topics, that Claude did not
hand-craft.

### 7.4.4 MAJOR: CAPHI++ is a template, not a pronunciation

**The single most useful discovery in the data.** Maknuune's CAPHI++ uses **uppercase for
sub-dialect-*variable* consonants** — and they are exactly the three that vary across all
of Arabic:

| Symbol | Letter | Uses | urban | rural | bedouin |
|---|---|---|---|---|---|
| `Q` | ق | 3,140 | **2** (glottal) | k | g |
| `J` | ج | 3,415 | **j** (dʒ) | dj | dj |
| `K` | ك | 549 | **k** | tsh | k |

Maknuune even ships explicit alternations: `q||K`, `Z||D`, `qIIk`.

So **`Qahwe` is not "qahwe"** — it's *qaf*+ahwe, and the sub-dialect resolves it:
`Qahwe` → urban **`2ahwe`** ("ahwe") · rural `kahwe` · bedouin `gahwe`.

This independently confirms the hand-written transliteration used throughout the reader,
and turns it from an assertion into sourced data.

**Consequence: the app needs a sub-dialect setting** — `pipeline/subdialect.py`, default
`urban` (Jerusalem/Ramallah/Nablus). **It must match the TTS voice**, which was Voice-
Designed "from Ramallah" = urban. A mismatch would print one pronunciation and speak
another, which is worse than either alone.

**Watch `J`.** Urban Palestinian jim is **[dʒ] → `j`**, *not* `zh`. [ʒ] is Lebanese/Syrian.
Getting this wrong gives the learner a Beirut accent while the voice says Ramallah — an
easy, invisible error given the household validator is Lebanese.

### 7.4.5 Rule: prefer untagged entries

Only **830 / 36,302 (2%)** of Maknuune entries carry a `SOURCE` village. Those tags mark
**local variants**, not defaults. قهوة has four entries:

| ID | CAPHI | SOURCE | |
|---|---|---|---|
| 26910 | `Qahwe` | *(untagged)* | ✅ the general form |
| 26911 | `ghawa` | الخليل > الظاهرية > الرماضين | Bedouin-influenced village ("Ghawa syndrome") |
| 26912 | `tshahwa` | بيت فجار | one village near Bethlehem |
| 26913 | `2itshheewa` | بيت فجار | same village |

Selecting on gloss alone picked **26911** — a hyper-local Bedouin form from one village
near Hebron — because its gloss read cleaner ("coffee" vs "coffee;coffeehouse"). **Rank by
provenance, not by prose.** The pipeline now sorts untagged entries first.

Village tags are a *feature* for later: sub-dialect authenticity down to the village.

### 7.4.6 ✅ SOLVED — vocalizing the surface form

**The gap was:** Maknuune stores citation forms (`يُقْعُد` "he sits"); running text has
conjugated ones (`بقعد` "I sit"). We can't print the citation form over the text — it's a
different word.

**The insight:** the two *share their stem consonants*, and the lexicon already knows how
that stem is vowelled. So align on the shared stem, transfer its diacritics, and vowel the
affixes by rule. `pipeline/vocalize.py`.

**Result on morning-coffee: 23/24 = 96% vocalized**, in three tiers kept deliberately
distinct because they carry different risk:

| Tier | N | % | What it means |
|---|---|---|---|
| `lexicon:exact` | 11 | 46% | Surface *is* the citation form. Maknuune's own vocalization, untouched. **Zero inference.** |
| `derived:affix` | 8 | 33% | ال / بال / عال / و + stem, or stem + ي. Stem keeps the lexicon's vowels; affix vowelled by uncontroversial rules incl. sun-letter assimilation. Low risk. |
| `derived:verb` | 4 | 17% | b-imperfect. Stem from the lexicon, but **the prefix vowel is our judgment.** Flagged. |
| refused | 1 | 4% | Printed bare rather than guessed. |

**Corroboration:** the derived forms independently reproduce the hand-written vocalization
from the original mockup — `بَصْحَى`, `وبَعْمَل`, `الصُّبِح`, `وبَشْرَب` all match. The
method agrees with a human on everything except one word, which isolates the uncertainty
precisely.

**The one real judgment — b-imperfect prefix vowels.** Palestinian: 1sg `بَـ` (ba-), but
2/3/1pl take kasra — `بِتْ`, `بِنْ`, `بِيْ`. Applying one vowel uniformly would be wrong.
The four affected words are the *only* place in this text where we chose a vowel rather
than looked one up:

| Derived | Written | Dictionary |
|---|---|---|
| `بَصْحَى` | بصحى | يِصْحَى |
| `وبَعْمَل` | وبعمل | يِعْمَل |
| `بَقْعُد` | بقعد | يُقْعُد |
| `وبَشْرَب` | وبشرب | يِشْرَب |

`بَقْعُد` is the known soft spot: the hand-written mockup had `بُقْعُد` (vowel harmony
with the u-stem). Both are attested. **Send these four to native review.**

**Refused: weak-final verbs.** `يِمْلِي` (yimli) → `بتملا` (bitmala). ى/ا/ي alternate
freely, *and the internal vowel pattern shifts by person*, so the citation form does not
predict the conjugated one. Alignment produced `بِتْمْلِا`, which is wrong. The vocalizer
now detects weak-final + VERB and refuses. Nominals with weak finals are safe and still
derive.

**In the app:** a **Vowels** toggle (default on). Both spellings ship in the DOM; CSS
picks. A refused word renders bare, and every word card states which tier its vowels came
from in plain English ("straight from the lexicon" / "prefix vowel is our best call" /
"not shown — we couldn't derive it honestly").

**Note this does NOT solve inline transliteration.** Vowels are Arabic script; a Latin
transliteration of a *conjugated* form still needs generation. The word card shows the
lexicon's citation pronunciation, correctly labelled as such.

### 7.5 Dead end: phoneme injection

Recorded so nobody re-derives it. **Azure SSML `<phoneme>` supports IPA/SAPI only for
en-US/CA, fr, de, es, ja, zh — Arabic is not on the list.** You cannot force Levantine
vowels into an Arabic voice via phonemes. The tempting idea — pipe Maknuune's phonological
transcription into Azure and bypass the orthographic ceiling of §7.2.2 — **does not work.**
The ē/ō ceiling stands. Maknuune's transcription remains valuable for display and for
*grading* TTS output, just not for driving it.

---

## 8. Decisions

**Made:**
- Reading direction: **Arabic-primary**, English collapsible.
- First build: **Phase 0** — one hand-annotated text, full toggle set, no pipeline.
- Audience: **personal tool**, for now.

- Dialect: **Palestinian specifically**, not Levantine broadly.
- User's level: **can sound words out**; vocabulary and dialect are the wall, not the
  script. The A2 sample text is roughly right.
- Validation: **none available** — see §7.3.

**Still open:**
1. **How Palestinian audio happens at all** — the blocking question. See §7.2.
2. Alignment granularity: sentence or finer? (Sentence for now, forced by §7.2.)
3. Transliteration scheme: academic, chat-Arabic, or both?
4. Levels: CEFR vs. derived-from-your-known-words?
5. Anki: real `.apkg` with audio, or CSV to start?

Item 1 gates the audio layer and possibly the dialect choice. Items 3–5 don't block and
can be settled once the reader is real.

---

## 9. Next step

Design artifacts — a mockup of the reader with the toggle panel, the hover card, and
the MSA/dialect split — to confirm we're seeing the same thing before any code.
