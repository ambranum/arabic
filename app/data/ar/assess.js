// Placement assessment spec — hand-written config, like curriculum.js.
// The assessment ITEMS are never stored here: they are sampled at runtime from the app's
// verified content (Maknuune-verified corpus words + audio, engine-verified conjugations,
// corpus-mined grammar examples, corroborated reactions), so the bank is broad, stays in
// sync with content, and contains nothing unverified. Per the project's rule, this file
// holds NO Arabic word data.
window.ASSESS = {
  // ---- the adaptive ladder ----
  rounds: 4,            // rounds of one item per skill → rounds*5 = 20 items ≈ 8 minutes
  upAt: 4,              // ≥4 of 5 right in a round → move up a tier
  // ≤1 of 5 right → move down. This was 2 when guessing was the only alternative to answering:
  // with four choices, a learner who genuinely knew 2 of 5 scored about 2.75 and usually held
  // their tier on the strength of a lucky guess. Now that "I don't know" is on every item, that
  // same learner honestly scores 2 — so keeping the old threshold would simply swap systematic
  // over-placement for systematic under-placement. One rung lower restores the calibration.
  downAt: 1,
  skills: ['listening', 'vocab', 'grammar', 'verbs', 'chunks'],
  skillLabels: {listening: 'Listening', vocab: 'Vocabulary', grammar: 'Grammar',
                verbs: 'Verbs', chunks: 'Conversation chunks'},

  // tier (1..4) ≈ phases 0-1 / 2 / 3-4 / 5-6 → the phase a finisher starts in
  tierPhase: [0, 2, 3, 5],
  tierNames: ['Getting started', 'Early conversation', 'Real conversation', 'Fluent-leaning'],
  // the 1-question self-guess that seeds the starting tier (reuses the old intake wording)
  selfStart: {none: 1, greetings: 1, conversation: 2, comfortable: 3},

  // ---- what each tier draws on ----
  vocabBands:  [[0, 120], [120, 350], [350, 800], [800, 99999]],  // corpus frequency-rank bands
  grammarBands: [[0, 4], [4, 8], [8, 15], [15, 20]],              // GRAM lesson-index bands
  verbSpec: [
    {weak: ['sound'],                        aspects: ['perf'],           persons: ['ana', 'huwwe', 'inta']},
    {weak: ['sound', 'hollow', 'doubled'],   aspects: ['perf', 'bimpf'],  persons: ['ana', 'huwwe', 'inta', 'hiyye']},
    {weak: ['sound', 'hollow', 'doubled', 'defective'], aspects: ['perf', 'bimpf', 'impf'], persons: ['ana', 'huwwe', 'hiyye', 'i7na', 'intu']},
    {weak: ['hollow', 'doubled', 'defective', 'assimilated', 'irregular'], aspects: ['perf', 'bimpf', 'impf'], persons: ['inti', 'i7na', 'intu', 'humme']},
  ],

  // ---- how the result feeds the plan ----
  seedGrammarMin: 0.5,  // grammar accuracy needed before lower-band lessons are marked known
  nudgeMin: 5,          // daily minutes moved toward the weakest skill (and off the strongest)
  skillActs: {listening: ['listen', 'watch'], vocab: ['read'], grammar: ['grammar'],
              verbs: ['verbs'], chunks: ['shadow', 'drill432']},
};
