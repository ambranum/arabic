# The Learning System — Spec Part II (v0.1 draft)

Part I (`SPEC.md`) specs the **reader**. This specs the thing around it: a scheduler, a
curriculum, and the daily loop that connects them.

---

## 1. The north star

> *"Sit down with a family for a full dinner and describe the same feelings and
> conversation that I could in my native tongue."*

Every design decision below answers to that sentence. It is unusually good as a goal
because of what it **rules out**:

- **Not tourist Arabic.** Nobody at a dinner table asks where the bathroom is. Directions,
  hotels, airports, shopping — the spine of most courses — are near-useless here.
- **Not transactional exchange.** Dinner is long turns, stories, tangents, interruption.
- **Not MSA, ever.** Nobody has ever spoken fuṣḥā at a family dinner.
- **Not vocabulary breadth.** It's *expressive depth* on a narrow, personal set of topics.

And what it **requires** that most courses never teach:

| Requirement | Why it's usually missed |
|---|---|
| **Interiority** — feelings, opinions, hedging, ambivalence | Courses teach nouns; dinner runs on "I felt like…", "it kind of bothered me", "honestly?" |
| **Narrative** — telling what happened to you | Requires past tense + sequencing + comic timing. Rarely drilled. |
| **Reaction** — the connective tissue | "No way." "Same." "That's rough." "Wallah?" This is most of what you actually say at a table. |
| **Multi-party listening** | Courses train you on one clean speaker. A real table is four people overlapping with dishes clattering. Learners drown here. |
| **Hospitality register** | Palestinian dinner has ritual language — تفضّل, صحتين, يسلمو إيديكي. High frequency, totally learnable, enormous social payoff. |
| **Being *yourself*** | Personality, humor, warmth. Comes from chunks and confidence, not grammar. |

**The honest version of the goal.** Literal parity with your native tongue — the *same*
feelings, the same range — is a decades-long thing and may never fully arrive. But that's
not really what's being asked. The real goal is **being yourself in Arabic**: present,
funny, warm, able to say what you actually mean. The 90% version is genuinely reachable.
The last 10% is a lifetime, and everyone who loves a second language makes peace with it.

---

## 2. The scheduler

**The feature: you describe your day in plain language; the app derives a study plan.**

Not "Alex's schedule" — an engine that works for anyone who describes their day.

### 2.1 The insight

Time is not fungible. An hour in a car and an hour at a desk are **different resources**,
because they permit different things. Almost every language app hands you one surface and
ignores where you are — so it wastes your commute and interrupts your desk.

The scheduler's whole job: **match activity to constraint.**

### 2.2 The slot model

A described day is parsed into **slots**. Each slot carries:

| Dimension | Values | Why it matters |
|---|---|---|
| `eyes` | free / occupied | Gates reading, and *everything visual* |
| `hands` | free / occupied | Gates typing, tapping, writing |
| `voice` | free / must be silent | **Gates all speaking practice** — the scarcest affordance |
| `duration` | micro (<5m) / short (5–20m) / medium (20–60m) / long (60m+) | Sets what can fit |
| `attention` | high / medium / low | Fresh brain vs. fried brain |
| `privacy` | alone / around others | Embarrassment is real and it kills speaking |
| `network` | online / maybe offline | Commutes lose signal |
| `interruptible` | yes / no | Micro-breaks get interrupted; evenings shouldn't |

`voice: free` + `privacy: alone` is the rarest and most valuable combination in a normal
life, and it's almost always **the car**. Most people have it and nobody uses it.

### 2.3 The activity library

Each activity declares what it *needs*. Matching is then mechanical.

| Activity | Needs | Best slot | Builds |
|---|---|---|---|
| **Shadowing** | audio, voice, eyes may be occupied | car | Pronunciation, prosody, chunk fluency |
| **Free production** (talk about your day, unscripted) | voice, audio, alone | car | Retrieval speed, confidence |
| **4/3/2 drill** (same story in 4 min, then 3, then 2) | voice, timer, alone | car | Automaticity under pressure |
| **Conversation bot** | voice, audio, network | car / evening | Two-way, unpredictable |
| **Listening comprehension** | audio | car | Ear training |
| **Multi-party listening** | audio, attention | car | The dinner-table skill |
| **The reader** (Part I) | eyes, hands, silent OK | work desk | Vocabulary in context, noticing |
| **SRS reps** | eyes, hands, micro-duration, silent OK | breaks | Retention |
| **New lesson / encoding** | eyes, high attention, uninterrupted | evening | New material |
| **Writing** | eyes, hands, attention | evening | Consolidation, noticing gaps |

Note how much lands in the car. In the worked commuter example (`design/scheduler-mockup.html`)
the car is **~37% of total study time and 100% of the speaking time.** It is the fluency
engine.

**Measure speaking, not permission.** An early-morning slot may *permit* speech and still
be spent encoding, because a fresh uninterrupted brain is scarcer than a free mouth. The
budget metric must count slots whose *activity* is speech, not slots that merely allow it
— conflating the two inflates every plan. (This was caught only by building the mockup and
noticing the numbers contradicted the prose.)

### 2.4 The trap the scheduler must prevent

The obvious thing to do with a commute — *put on an Arabic podcast* — is close to
**worthless**. Passive background listening without attention produces very little; it is
the single most common way people waste a commute for years and feel productive doing it.

**Every car activity must force output or retrieval.** Shadowing, answering aloud,
retelling. If the learner can zone out and the audio keeps playing, the design has failed.
The scheduler should never emit "listen to something."

### 2.5 ✅ Dependency cleared

The car is audio-only and audio-first, and for most of this project's life we had **no
Palestinian voice** — which gated ~40% of the study plan and 100% of the speaking time.

**Solved.** ElevenLabs Voice Design v3, prompted for a Palestinian speaker: clears the
ē/ō ceiling, sounds human, sounds Palestinian, reads normal Arabic spelling, and automates
via a public API at ~$0.10/1K chars (`SPEC.md` §7.2.0).

The car is live. Shadowing, 4/3/2, free production, and cold retrieval all have a voice.

**And the north star got closer.** Voice Design mints distinct voices; v3 ships **Text to
Dialogue** for multi-speaker audio. So §5's phase 6 — **multi-party listening**, following
four people talking over each other at a table — is now *synthesizable*. The hardest and
least-taught skill in the plan, and the one the whole project is named after, is buildable.
Generate four Palestinian voices and let them talk over each other.

---

## 3. The daily loop

Slots shouldn't be independent. They should **hand off** to each other, so material
travels through a full encode → consolidate → retrieve → use cycle every 24 hours.

```
  EVENING            encode new chunks, in context, with attention
      ↓
  SLEEP              consolidation (this is real; it does the work for free)
      ↓
  MORNING CAR        retrieve it OUT LOUD, cold, before you've seen it again
      ↓
  WORK DESK          meet it again in real text — the reader; mark what's still fuzzy
      ↓
  MICRO-BREAKS       SRS reps on whatever's fuzzy
      ↓
  EVENING CAR        PRODUCE with it — unscripted, about your actual life
      ↓
  EVENING            encode tomorrow's, plus write what you couldn't say today
```

Two deliberate properties:

1. **Encoding sits before sleep.** Consolidation is free and we should use it.
2. **The first retrieval is cold, out loud, in the morning car.** Retrieval when it's
   *hard* is what builds durable memory. Easy review builds almost nothing.

The loop closes on itself: what you *couldn't say* in the evening car becomes tomorrow's
evening encoding. **The gaps drive the curriculum.** That's the engine.

---

## 4. The science, honestly

The user asked for "the latest science" and said they weren't sure what that means. So:
what's actually supported, what's contested, and what to ignore.

### Build on this

- **Spacing effect / spaced repetition.** Expanding intervals beat massed review. **FSRS**
  is the current best-in-class scheduler (what modern Anki uses); SM-2 is the older
  standard. Micro-breaks are a natural fit.
- **Retrieval practice (testing effect).** Recall > recognition > rereading, decisively.
  Every slot should make you *produce*, not just look at things.
- **Desirable difficulty (Bjork).** If it feels easy, you're not encoding. The struggle is
  the mechanism, not friction to design away. Fights the instinct to make apps feel nice.
- **Generation effect.** Producing an answer beats reading the same answer.
- **Sleep consolidation.** Encode before sleep.
- **Interleaving.** Mixing topics beats blocking, despite feeling worse in the moment.
- **Formulaic chunks.** Fluent speech is largely **prefabricated multi-word units**, not
  words assembled live under time pressure. This is *the* speaking-fluency finding and
  most apps ignore it entirely. **Teach chunks, not vocabulary.**
- **Frequency.** The top ~1000 spoken words carry most ordinary conversation. Ruthless
  prioritization pays enormously.
- **Automaticity.** Knowing a word and retrieving it in 400ms are *different skills*. Only
  the second is fluency. It comes from repeated retrieval under time pressure — hence
  4/3/2 in the car.

### Contested — use with care

- **Krashen's input hypothesis** (comprehensible input, i+1). Hugely influential, and
  input is clearly necessary. But "input alone is sufficient" is contested; **output
  matters** (Swain) — production forces you to notice what you can't yet say. Our loop
  treats input as fuel and output as the engine.
- **Critical period.** Nuanced; adults learn fine. Accent is the most age-sensitive part
  and the least important for the dinner table.

### Ignore

- **Learning styles** ("I'm an auditory learner"). No credible evidence; repeatedly failed
  to replicate. Modality should be chosen by *context and content*, not personality type.
- **Sleep-learning.** Playing audio while asleep does nothing.
- **Immersion alone.** Without attention and noticing, exposure doesn't convert. Hence §2.4.
- **Streak-maximizing gamification.** Optimizes for app-opening, not speech.

---

## 5. The path to the dinner table

Frequency-first and chunk-first, ordered by what gets you into the chair soonest.

| Phase | Focus | Why here |
|---|---|---|
| **0. Sound** | ق→ء, ث/ذ→ت/د, the ē/ō vowels, ʿayn/ḥa | The exact things found in `SPEC.md` §7.2.2. Get the ear and mouth right *before* habits set. Short phase. |
| **1. Reaction** | "Really?" "Same." "That's rough." "Wallah?" "I know, right?" | **First, deliberately.** The connective tissue of conversation. Lets you *participate* at a table long before you can hold forth. Enormous morale payoff. |
| **2. The self** | Your life, work, family, where you're from, your day | Dinner opens with "who are you?" Highly personal, so it's *your* vocabulary, not a generic list. |
| **3. Feeling & opinion** | Like/dislike, want, ambivalence, hedging, mild disagreement | The interiority the goal explicitly asks for. |
| **4. Narrative** | Past tense, sequencing, "one time I…", timing | Stories are the currency of a dinner table. |
| **5. Nuance** | Humor, sympathy, politeness, teasing, disagreeing warmly | Where "being yourself" actually lives. |
| **6. The table** | Multi-party listening, overlap, noise, hospitality ritual | The final skill, trained deliberately — not left to chance. |

Note **Reaction comes before The self.** Standard courses start with self-introduction;
but you can sit at a table and be a real presence with 30 reaction chunks and good ears,
long before you can describe your job. It's the fastest route to feeling human in the
language, and morale compounds.

---

## 6. Open questions

1. **Where does content come from?** Phases 2–5 are inherently *personal* — your life, your
   family, your stories. This is generated per-user, which loops straight back to `SPEC.md`
   §7.3: **nobody is checking the Arabic.** Personalized generated content has no
   validator. This is the most serious unsolved problem in the project.
2. **Multi-party listening audio** — needs several voices overlapping. With no Palestinian
   voice at all, this is doubly blocked.
3. **How does the app know what you couldn't say?** The loop depends on capturing gaps in
   the evening car. Voice capture + ASR? Self-report? (Azure *does* support `ar-PS` for
   speech-to-text — see `SPEC.md` §7.2.1. The one thing Palestinian has support for is
   being *heard*, which is exactly what gap-capture needs.)
4. **Scheduler input format** — free-text description parsed by Claude, or a structured
   builder? Free text is the better product and the harder build.
5. **Does the reader survive?** In this system the reader is *one activity in one slot*
   (work desk). It's still the best-developed piece, but it's no longer the app.

---

## 7. Reality check

At ~10 hrs/week ≈ 500 hrs/year. Arabic is among the hardest languages for English
speakers, but skipping the script and the formal register removes most of what makes it
slow.

- **~6 months:** simple conversation. Present at a table, understanding gist, reacting.
- **18 months–2 years:** comfortable conversation. The dinner, mostly.
- **Beyond:** the last 10% of expressive parity. Forever, and that's fine.

No deadline was set, which is the right call — it means optimizing for **sustainability
over intensity**. The plan that survives three years beats the plan that wins three weeks.
Every design choice should be checked against: *would someone still do this in month
eight?*
