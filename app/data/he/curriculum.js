// The curriculum spec the plan generator consumes. Plain data, shipped, deterministic.
//
// It carries STRUCTURE only — hours and activity mixes — and deliberately holds NO Hebrew word
// data: per the project's rule, Hebrew is looked up in the lexicon, never written here. Every
// activity below points at content that already exists in the app and was looked up there.
//
// THIS PLAN STOPS WHERE THE MATERIAL STOPS, and the material has moved. It was three phases to
// A2, written when Hebrew had the ear, the reflexes, the binyanim, 2,084 paradigms, a dictionary
// and a paper every morning — and that was the honest ceiling at the time. Since then the shelf
// has gained 24 interactive teaching units, 90 graded stories with 30 of them advanced, and 37
// chapters of published Ben-Yehuda literature. Two more phases now have something real to be
// made of: narrative, and reading published Hebrew rather than Hebrew written for a learner.
//
// It stops at FIVE and at B1, not seven and C1, because the thing Arabic's last two phases are
// built on — several people talking at once, the dinner table — does not exist in Hebrew yet.
// Claiming B2 for a shelf with no multi-party listening on it would be the promise this comment
// was written to prevent, just made two phases later.
window.CURRICULUM = {
  // FSI puts Hebrew in its Category II — about 1,100 class hours to professional working
  // proficiency, roughly half of Arabic's. Used only to project a finish line from real weekly
  // hours; it is an estimate, and the app shows it as one.
  totalHours: 1100,

  // How far up each ordered list a phase reaches. Nine grammar lessons, and verbs by BINYAN
  // (see LANG.verb.tier in lang/he.js): 1 = paal, 2 = nifal/piel/hifil, 3 = hitpael and the
  // two passives, which are the ones you meet last in speech.
  grammarCap: [2, 5, 9, 9, 9],
  verbTier:   [1, 2, 3, 3, 3],
  reviewDays: [2, 7, 21, 45, 90],

  // What level each phase IS. Read off this plan's own cumulative budget (12 / 62 / 262 hours)
  // against FSI's ~1,100 for Hebrew. The same two caveats the Arabic plan states apply: CEFR
  // describes a whole language including reading and writing, and nobody here is examining you.
  levels: [
    {cefr: 'A1', band: 'Beginner'},        // 1 Sound     — the ear and the mouth
    {cefr: 'A1', band: 'Beginner'},        // 2 Reaction  — automatic conversational reflexes
    {cefr: 'A2', band: 'Beginner'},        // 3 The paper — read something real, every day
    {cefr: 'B1', band: 'Intermediate'},    // 4 The story — follow one, and tell it back
    {cefr: 'B1', band: 'Intermediate'},    // 5 The shelf — published Hebrew, not learner Hebrew
  ],

  // ---- the activity library ----
  // slot: car = voice free and alone · desk = eyes and hands · break = micro, silent OK ·
  // evening = high attention. order: the daily encode→retrieve→read→reps→produce position.
  activities: {
    sound:    {label: 'Sound & ear drill',       slot: 'evening', order: 1, speak: true,
               builds: 'The ear and the mouth',
               instr: 'Read the tip first, then listen to each pair and say both OUT LOUD. Finish with the ear test.'},
    shadow:   {label: 'Shadow out loud',         slot: 'car',     order: 1, speak: true,
               builds: 'Pronunciation & chunk fluency',
               instr: 'Play a line, then say it back copying the rhythm exactly. Your mouth has to move — no silent reading.'},
    drill432: {label: 'Reaction drill',          slot: 'car',     order: 2, speak: true,
               builds: 'Automatic conversational reflexes',
               instr: 'Read the English, SAY the Hebrew out loud before you reveal it, then grade yourself honestly.'},
    grammar:  {label: 'Grammar lesson',          slot: 'desk',    order: 2, speak: false,
               builds: 'The binyan system',
               instr: 'Read the explanation, then read every pair in the tables aloud. The point is to see the root through the shape.'},
    verbs:    {label: 'Verb paradigm',           slot: 'desk',    order: 3, speak: true,
               builds: 'Conjugation you can reach for',
               instr: 'Say the whole table out loud, past then present then future. Tap + to bank the ones that stick.'},
    // The units are the spine of the early phases and the plan had no way to schedule them:
    // this activity did not exist, so 24 lessons sat in the app that no day ever pointed at.
    lesson:   {label: 'Lesson unit',             slot: 'desk',    order: 1, speak: true,
               builds: 'The day’s new material, properly taught',
               instr: 'Work the unit top to bottom OUT LOUD. Type the answers rather than think '
                    + 'them — the checking is generous about spelling and strict about the point. '
                    + 'Tap + on any new word to send it to your flashcards.'},
    read:     {label: "Read today's paper",      slot: 'desk',    order: 3, speak: false,
               builds: 'Real Hebrew, current, every day',
               instr: 'Read it through once without the English. Tap any word you do not know — every one is in the lexicon — and bank the ones worth keeping.'},
    srs:      {label: 'Flashcard review',        slot: 'break',   order: 4, speak: true,
               builds: 'Keeping what you have met',
               instr: 'Say each card out loud before you flip it. Silent review is recognition, not recall.'},
    produce:  {label: 'Say something real',      slot: 'car',     order: 5, speak: true,
               builds: 'Turning what you know into speech',
               instr: 'Talk about your day out loud in Hebrew for the whole time. Where you get stuck, note the gap — that is tomorrow’s tutor question.'},
    tutor:    {label: 'Ask a Tutor',             slot: 'evening', order: 5, speak: false,
               builds: 'The gaps only a conversation finds',
               instr: 'Work through what you got stuck on this week. Tap Save on any phrase to send it to your flashcards.'},
    encode:   {label: 'Bank new words',          slot: 'evening', order: 4, speak: false,
               builds: 'Deliberate first exposure',
               instr: 'Look up five things you wanted to say today and could not. Bank them with the sentence you wanted them in.'},
    listen:   {label: 'Listen to real Hebrew',   slot: 'car',     order: 1, speak: false,
               builds: 'Native speed, unscripted',
               instr: 'Listen once without following along, then again reading the transcript if there is one.'},
  },

  external: {
    podcasts: {name: 'Streetwise Hebrew', free: true,
               url: 'https://tlv1.fm/streetwise-hebrew/',
               note: 'Short episodes on one slang word or phrase each, in English with Hebrew clips. The closest thing to this app in podcast form.'},
    news:     {name: 'Ynet / Walla — read the real thing', free: true,
               url: 'https://www.ynet.co.il/',
               note: 'When the app’s daily article feels easy, go to the source it was written from.'},
  },

  // ---- the phases ----
  phases: [
    {id: 0, name: 'Sound', hours: 12,
     focus: 'Get the ear and the mouth right first — the uvular ר, ח and כ as one sound, צ as ts, '
          + 'the letters that are now identical, and where the beat falls. Short and deliberate, '
          + 'before habits set.',
     milestone: 'You can hear and make the sounds that trip up every English speaker, and read '
              + 'a short story without the English.',
     mix: [
       {act: 'lesson',  min: 25, src: 'inapp', pool: 'unit'},
       {act: 'sound',   min: 15, src: 'inapp'},
       {act: 'grammar', min: 15, src: 'inapp'},
       {act: 'verbs',   min: 10, src: 'inapp'},
       {act: 'srs',     min: 10, src: 'inapp'},
       // A beginner story, not the paper. The paper is real Hebrew about whatever happened
       // yesterday, which is the right thing to read LATER and the wrong thing to be handed on
       // day one -- it does not know what you have met.
       {act: 'read',    min: 15, src: 'inapp', pool: 'beginner'},
     ]},

    {id: 1, name: 'Reaction', hours: 50,
     focus: 'The connective tissue of talk — "בֶּאֱמֶת?", "בְּדִיּוּק", "חֲבָל", "יַאלְלָה". These let '
          + 'you be a real presence at a table long before you can describe your job, and they '
          + 'come back the fastest for the time you put in.',
     milestone: 'The reactions are automatic — you can hold your end of a conversation you are mostly listening to.',
     mix: [
       {act: 'lesson',   min: 25, src: 'inapp', pool: 'unit'},
       {act: 'drill432', min: 15, src: 'inapp', pool: 'reaction'},
       // Shadowing wants something you can already mostly read, and every story is voiced.
       {act: 'shadow',   min: 15, src: 'inapp', pool: 'beginner'},
       {act: 'sound',    min: 10, src: 'inapp'},
       {act: 'grammar',  min: 15, src: 'inapp'},
       {act: 'verbs',    min: 10, src: 'inapp'},
       // Both tiers, because this is where the step between them is taken: the beginner set
       // is what you can already read, the intermediate set is the one that is teaching.
       {act: 'read',     min: 15, src: 'inapp', pool: 'beginner'},
       {act: 'read',     min: 15, src: 'inapp', pool: 'intermediate'},
       {act: 'read',     min: 15, src: 'inapp', pool: 'news'},
       {act: 'srs',      min: 10, src: 'inapp'},
       {act: 'produce',  min: 10, src: 'inapp'},
       {act: 'listen',   min: 15, src: 'external', res: 'podcasts'},
       {act: 'encode',   min: 10, src: 'inapp'},
       {act: 'tutor',    min: 20, src: 'inapp', cadence: 'weekly'},
     ]},

    {id: 2, name: 'The paper', hours: 200,
     focus: 'A real Hebrew article every morning, the longer stories, and the public-domain '
          + 'shelf underneath them both. This is the phase that compounds: the paper is written '
          + 'fresh each day, so the reading never runs out and the vocabulary is whatever Israel '
          + 'is actually talking about.',
     milestone: 'You can read the day’s news with the English hidden, and say what it said.',
     mix: [
       {act: 'lesson',   min: 25, src: 'inapp', pool: 'unit'},
       {act: 'read',     min: 25, src: 'inapp', pool: 'news'},
       // The advanced set, which the tier below has been building toward. Same shape and a
       // real step up: two clauses a sentence instead of one, and a fifth of the words in each
       // story are ones this app has never used, which is the point of a last tier.
       {act: 'read',     min: 20, src: 'inapp', pool: 'intermediate'},
       {act: 'shadow',   min: 15, src: 'inapp', pool: 'intermediate'},
       {act: 'grammar',  min: 15, src: 'inapp'},
       {act: 'verbs',    min: 15, src: 'inapp'},
       {act: 'drill432', min: 10, src: 'inapp', pool: 'reaction'},
       {act: 'srs',      min: 15, src: 'inapp'},
       {act: 'produce',  min: 15, src: 'inapp'},
       {act: 'listen',   min: 20, src: 'external', res: 'podcasts'},
       {act: 'encode',   min: 10, src: 'inapp'},
       {act: 'tutor',    min: 20, src: 'inapp', cadence: 'weekly'},
     ]},

    // THE STORY. The paper tells you what happened; a story makes you hold a whole thing in your
    // head and hand it back. That is the step from understanding Hebrew to using it, and the 30
    // advanced stories plus the 4/3/2 retell are what it is made of.
    {id: 3, name: 'The story', hours: 300,
     focus: 'One long thing at a time, and then you tell it back. The advanced stories carry two '
          + 'clauses a sentence and a fifth of their words are new to this app, so they are the '
          + 'first reading that is genuinely stretching rather than graded down to you.',
     milestone: 'You can read an advanced story, close it, and retell the whole thing out loud '
              + 'in under four minutes without going back.',
     mix: [
       {act: 'read',     min: 25, src: 'inapp', pool: 'advanced'},
       {act: 'shadow',   min: 20, src: 'inapp', pool: 'advanced'},
       {act: 'produce',  min: 20, src: 'inapp'},
       {act: 'read',     min: 20, src: 'inapp', pool: 'news'},
       {act: 'lesson',   min: 20, src: 'inapp', pool: 'unit'},
       {act: 'grammar',  min: 15, src: 'inapp'},
       {act: 'verbs',    min: 15, src: 'inapp'},
       {act: 'srs',      min: 15, src: 'inapp'},
       {act: 'encode',   min: 10, src: 'inapp'},
       {act: 'listen',   min: 20, src: 'external', res: 'podcasts'},
       {act: 'tutor',    min: 20, src: 'inapp', cadence: 'weekly'},
     ]},

    // THE SHELF. Everything before this was Hebrew written FOR a learner -- graded, counted,
    // checked against what you had met. Ben-Yehuda's authors were not writing for you, and that
    // is the whole point of the phase: the first Hebrew here that was not adjusted to fit.
    {id: 4, name: 'The shelf', hours: 500,
     focus: 'Published Hebrew, in order, a chapter at a time — Dushman, Barash, Bergstein, and '
          + 'the translations of Grimm and Daudet the Ben-Yehuda volunteers transcribed. Slower '
          + 'than the paper and worth it: this is how the language is written when nobody is '
          + 'making it easy.',
     milestone: 'You can finish a Ben-Yehuda chapter with the English hidden, and say what kind '
              + 'of person the author was from how they wrote it.',
     mix: [
       {act: 'read',     min: 30, src: 'inapp', pool: 'book'},
       {act: 'read',     min: 20, src: 'inapp', pool: 'news'},
       {act: 'produce',  min: 20, src: 'inapp'},
       {act: 'shadow',   min: 15, src: 'inapp', pool: 'advanced'},
       {act: 'drill432', min: 10, src: 'inapp', pool: 'reaction'},
       {act: 'grammar',  min: 15, src: 'inapp'},
       {act: 'verbs',    min: 10, src: 'inapp'},
       {act: 'srs',      min: 15, src: 'inapp'},
       {act: 'encode',   min: 10, src: 'inapp'},
       {act: 'listen',   min: 25, src: 'external', res: 'podcasts'},
       {act: 'tutor',    min: 25, src: 'inapp', cadence: 'weekly'},
     ]},
  ],
};
