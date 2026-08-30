// Placement assessment spec — hand-written config, like curriculum.js.
// The assessment ITEMS are never stored here: they are sampled at runtime from the app's
// verified content (lexicon-verified corpus words with audio, engine-verified conjugations,
// lexicon-corroborated reactions), so the bank stays in sync with the content and contains
// nothing unverified. Per the project's rule, this file holds NO Hebrew word data.
window.ASSESS = {
  // ---- the adaptive ladder ----
  // Four skills rather than Arabic's five, so four rounds is 16 items rather than 20 — about
  // six minutes. `grammar` is missing on purpose: the Hebrew grammar module teaches the
  // binyanim from paradigm tables, and there is no bank of mined example sentences to sample a
  // question from. Testing a skill this app cannot yet sample honestly would just be noise.
  rounds: 4,
  upAt: 3,              // >=3 of 4 right in a round -> move up a tier
  downAt: 1,            // <=1 of 4 -> move down. Same calibration as Arabic, scaled to 4 items.
  skills: ['listening', 'vocab', 'verbs', 'chunks'],
  skillLabels: {listening: 'Listening', vocab: 'Vocabulary',
                verbs: 'Verbs', chunks: 'Conversation chunks'},

  // tier (1..4) -> the phase a finisher starts in. Three phases exist, so the top two tiers
  // both land in the last one: this plan does not have a phase 4 to place anyone into, and
  // pretending otherwise is exactly what the short curriculum is there to avoid.
  tierPhase: [0, 1, 2, 2],
  tierNames: ['Getting started', 'Early conversation', 'Reading the paper', 'Past what this plan covers'],
  selfStart: {none: 1, greetings: 1, conversation: 2, comfortable: 3},

  // ---- what each tier draws on ----
  vocabBands: [[0, 120], [120, 350], [350, 800], [800, 99999]],   // corpus frequency-rank bands
  grammarBands: [[0, 2], [2, 5], [5, 9], [5, 9]],                 // unused; kept for the seeder
  // `weak` is the binyan for Hebrew (see he_verbs.py) and the ladder follows LANG.verb.tier:
  // paal first, then the other three actives, the passives and hitpael last.
  verbSpec: [
    {weak: ['paal'],                                   aspects: ['past'],
     persons: ['ani', 'hu', 'ata']},
    {weak: ['paal', 'piel'],                           aspects: ['past', 'pres'],
     persons: ['ani', 'hu', 'ata', 'hi']},
    {weak: ['paal', 'piel', 'hifil', 'nifal'],         aspects: ['past', 'pres', 'fut'],
     persons: ['ani', 'hu', 'hi', 'anaxnu', 'atem']},
    {weak: ['piel', 'hifil', 'nifal', 'hitpael', 'pual', 'hufal'], aspects: ['past', 'pres', 'fut'],
     persons: ['at', 'anaxnu', 'atem', 'hem']},
  ],
  // Hebrew's present tense has four forms by gender and number, not by person, so the present
  // slots are keyed ms/fs/mp/fp and a person key finds nothing there. Named here rather than
  // guessed, and the extra distractors are the persons no tier tests.
  aspectLabels: {past: 'past', pres: 'present', fut: 'future'},
  extraPersons: ['at', 'atem', 'hem', 'anaxnu'],

  // ---- how the result feeds the plan ----
  seedGrammarMin: 0.5,
  nudgeMin: 5,
  skillActs: {listening: ['listen', 'shadow'], vocab: ['read'],
              verbs: ['verbs'], chunks: ['drill432', 'produce']},
};
