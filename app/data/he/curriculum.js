// The curriculum spec the plan generator consumes. Plain data, shipped, deterministic.
//
// It carries STRUCTURE only — hours and activity mixes — and deliberately holds NO Hebrew word
// data: per the project's rule, Hebrew is looked up in the lexicon, never written here. Every
// activity below points at content that already exists in the app and was looked up there.
//
// THIS PLAN IS SHORT ON PURPOSE. The Arabic side runs seven phases to a Palestinian family
// dinner because it has the content to fill them: lessons, 90 graded stories, 266 book chapters,
// dialogues. Hebrew has the ear, the reflexes, the binyanim, 2,084 paradigms, a dictionary and a
// paper written fresh every morning — enough for a real first stretch and not a step more.
// Writing four more phases against content that does not exist would be a promise the app breaks
// on the day you reach it, so the plan stops where the material stops and says so.
window.CURRICULUM = {
  // FSI puts Hebrew in its Category II — about 1,100 class hours to professional working
  // proficiency, roughly half of Arabic's. Used only to project a finish line from real weekly
  // hours; it is an estimate, and the app shows it as one.
  totalHours: 1100,

  // How far up each ordered list a phase reaches. Nine grammar lessons, and verbs by BINYAN
  // (see LANG.verb.tier in lang/he.js): 1 = paal, 2 = nifal/piel/hifil, 3 = hitpael and the
  // two passives, which are the ones you meet last in speech.
  grammarCap: [2, 5, 9],
  verbTier:   [1, 2, 3],
  reviewDays: [2, 7, 21],

  // What level each phase IS. Read off this plan's own cumulative budget (12 / 62 / 262 hours)
  // against FSI's ~1,100 for Hebrew. The same two caveats the Arabic plan states apply: CEFR
  // describes a whole language including reading and writing, and nobody here is examining you.
  levels: [
    {cefr: 'A1', band: 'Beginner'},      // 1 Sound     — the ear and the mouth
    {cefr: 'A1', band: 'Beginner'},      // 2 Reaction  — automatic conversational reflexes
    {cefr: 'A2', band: 'Beginner'},      // 3 The paper — read something real, every day
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
       {act: 'read',     min: 25, src: 'inapp', pool: 'news'},
       // The advanced set, which the tier below has been building toward. Same shape and a
       // real step up: two clauses a sentence instead of one, and a fifth of the words in each
       // story are ones this app has never used, which is the point of a last tier.
       {act: 'read',     min: 20, src: 'inapp', pool: 'advanced'},
       // The Ben-Yehuda shelf, in order. Published Hebrew rather than written for you, which is
       // what this phase is for: the paper for what is happening, a book for how it is written.
       {act: 'read',     min: 20, src: 'inapp', pool: 'book'},
       {act: 'shadow',   min: 15, src: 'inapp', pool: 'advanced'},
       {act: 'grammar',  min: 15, src: 'inapp'},
       {act: 'verbs',    min: 15, src: 'inapp'},
       {act: 'drill432', min: 10, src: 'inapp', pool: 'reaction'},
       {act: 'srs',      min: 15, src: 'inapp'},
       {act: 'produce',  min: 15, src: 'inapp'},
       {act: 'listen',   min: 20, src: 'external', res: 'podcasts'},
       {act: 'encode',   min: 10, src: 'inapp'},
       {act: 'tutor',    min: 20, src: 'inapp', cadence: 'weekly'},
     ]},
  ],
};
