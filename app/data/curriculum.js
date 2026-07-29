// The curriculum spec the plan generator consumes. Plain data, shipped, deterministic.
//
// Grounded in LEARNING-SYSTEM.md: the 6-phase path to the dinner table (§5), the slot-based
// activity library (§2.3), and the daily encode→retrieve→use loop (§3). It carries STRUCTURE
// only — hours, activity mixes, and links to external courses. It deliberately holds NO Arabic
// word data: per the project's rule, Arabic is looked up in the lexicon, never written here.
// Phase 1's reaction chunks therefore point at the in-app reaction drill (already vetted),
// not fabricated phrases.
window.CURRICULUM = {
  // The user's working assumption: ~2000 hours of deliberate practice to spoken fluency.
  // Used only to project a finish line from real weekly hours — it is an estimate, shown honestly.
  totalHours: 2000,

  // ---- the activity library (§2.3) ----
  // slot: which kind of moment the activity needs.
  //   car     = voice free + alone (the speaking engine); audio-first, eyes may be busy
  //   desk    = eyes + hands, quiet OK (the reader, grammar)
  //   break   = micro, silent OK (SRS reps)
  //   evening = high attention, uninterrupted (encoding new material, tutor)
  // order: the daily-loop position, so a day's tasks sort into encode→retrieve→read→reps→produce.
  // speak: true if the activity is speech (counts toward the speaking budget, needs a voice slot).
  activities: {
    course:   {label:'Structured audio lesson', slot:'car',     order:1, speak:true,  builds:'New structure, in the car',
               instr:'Do one lesson and answer every prompt OUT LOUD before the speaker does.'},
    shadow:   {label:'Shadow out loud',          slot:'car',     order:1, speak:true,  builds:'Pronunciation & chunk fluency',
               instr:'Play a line, then say it back copying the rhythm exactly. Your mouth has to move — no silent reading.'},
    sound:    {label:'Sound & ear drill',        slot:'evening', order:1, speak:true,  builds:'The ear and the mouth',
               instr:'Minimal pairs — ق vs ء, ث vs ت, the ē/ō vowels. Hear the difference, then make it yourself.'},
    read:     {label:'Read in context',          slot:'desk',    order:2, speak:false, builds:'Vocabulary in context',
               instr:'Read, tap any word you don’t know, and hit “Don’t know it” to send it to your deck.'},
    grammar:  {label:'One grammar pattern',      slot:'desk',    order:2, speak:false, builds:'A reusable structure',
               instr:'Learn one pattern, then say five of your OWN sentences with it.'},
    listen:   {label:'Listen & retell',          slot:'car',     order:2, speak:true,  builds:'Ear training (active)',
               instr:'Listen to a short clip, then retell it out loud in your own words. Never just let it play (§2.4).'},
    srs:      {label:'Flashcard review',         slot:'break',   order:3, speak:false, builds:'Retention (spaced repetition)',
               instr:'Grade each card honestly. The ones you get wrong come back sooner — that’s the whole trick.'},
    drill432: {label:'4/3/2 fluency drill',      slot:'car',     order:4, speak:true,  builds:'Automaticity under pressure',
               instr:'Tell the same little story in 4 minutes, then 3, then 2. Speed forces the words to become automatic.'},
    produce:  {label:'Free production',          slot:'car',     order:4, speak:true,  builds:'Retrieval speed & confidence',
               instr:'Talk about your ACTUAL day, unscripted, out loud. Note what you couldn’t say — that’s tomorrow’s lesson (§3).'},
    tutor:    {label:'Tutor conversation',       slot:'evening', order:4, speak:true,  builds:'Two-way, unpredictable speech',
               instr:'Talk with a Palestinian tutor. Bring the things you couldn’t say this week.'},
    encode:   {label:'Encode tomorrow’s chunks', slot:'evening', order:5, speak:false, builds:'New material, pre-sleep',
               instr:'Meet a few new chunks with attention right before bed — sleep consolidates them for free (§3).'},
  },

  // ---- external resources (clearly labeled, blended in until native content replaces them) ----
  // Search links (rather than named shows) where a specific title would be a guess.
  external: {
    languageTransfer: {name:'Language Transfer — Complete Arabic', free:true,
      url:'https://www.languagetransfer.org/',
      note:'Free “thinking method” audio course. Levantine-leaning, superb for building structure in the car.'},
    pimsleur: {name:'Pimsleur — Eastern Arabic (Levantine)', free:false,
      url:'https://www.pimsleur.com/learn-arabic',
      note:'Paid audio course. Strong speaking drills that fit the car slot.'},
    podcasts: {name:'Levantine Arabic podcasts', free:true,
      url:'https://open.spotify.com/search/levantine%20arabic',
      note:'Pick a short episode and RETELL it — active listening only (§2.4).'},
    youtube: {name:'Palestinian dialect on YouTube', free:true,
      url:'https://www.youtube.com/results?search_query=palestinian+arabic+dialect+lesson',
      note:'Search Palestinian-dialect channels. Shadow and retell — don’t watch passively.'},
    tutor: {name:'iTalki / Preply — a Palestinian tutor', free:false,
      url:'https://www.italki.com/',
      note:'The fastest fix for the speaking gap. 1–2× a week once you’re past Reaction.'},
    dialogue: {name:'Multi-party listening (the dinner table)', free:false,
      url:'https://www.italki.com/',
      note:'Following several people at once is the north-star skill. Until we synthesize it in-app, train it with a tutor + group audio.'},
  },

  // ---- the 6 phases (§5), frequency-first and chunk-first ----
  // hours: rough budget for the phase (sums to ~totalHours); drives the projected timeline.
  // mix: the activities appropriate to the phase, each with a target minutes-per-session and source.
  //   pool: which in-app content pool a `read`/`shadow` task pulls from.
  //   res:  which external.<key> an external task links to.
  //   cadence:'weekly' → scheduled about once per week, not every day (tutor).
  phases: [
    {id:0, name:'Sound', hours:15,
     focus:'Get the ear and the mouth right first — ق→ء, ث/ذ→ت/د, the ē/ō vowels, ʿayn & ḥa. Short, deliberate, before habits set.',
     milestone:'You can hear and make the sounds that trip up every beginner.',
     mix:[
       {act:'course', min:25, src:'external', res:'languageTransfer'},
       {act:'sound',  min:15, src:'external', res:'languageTransfer'},
       {act:'srs',    min:10, src:'inapp'},
       {act:'read',   min:15, src:'inapp', pool:'beginner'},
     ]},
    {id:1, name:'Reaction', hours:60,
     focus:'The connective tissue of talk — “Really?”, “Same.”, “That’s rough.”, “Wallah?”. Lets you be a real presence at a table long before you can describe your job. Huge morale payoff.',
     milestone:'~30 reaction chunks automatic — you can participate at a table.',
     mix:[
       {act:'shadow',   min:20, src:'inapp', pool:'reaction'},
       {act:'drill432', min:15, src:'inapp', pool:'reaction'},
       {act:'read',     min:20, src:'inapp', pool:'beginner'},
       {act:'srs',      min:10, src:'inapp'},
       {act:'produce',  min:15, src:'inapp'},
       {act:'course',   min:20, src:'external', res:'languageTransfer'},
       {act:'encode',   min:10, src:'inapp'},
     ]},
    {id:2, name:'The self', hours:200,
     focus:'Your life, work, family, where you’re from, your day. Dinner opens with “who are you?” — so this is YOUR vocabulary, not a generic list.',
     milestone:'You can introduce yourself and talk about your life in simple sentences.',
     mix:[
       {act:'read',    min:25, src:'inapp', pool:'beginner'},
       {act:'produce', min:20, src:'inapp'},
       {act:'srs',     min:15, src:'inapp'},
       {act:'grammar', min:15, src:'inapp'},
       {act:'course',  min:20, src:'external', res:'languageTransfer'},
       {act:'tutor',   min:45, src:'external', res:'tutor', cadence:'weekly'},
       {act:'encode',  min:10, src:'inapp'},
     ]},
    {id:3, name:'Feeling & opinion', hours:250,
     focus:'Like / dislike, want, ambivalence, hedging, mild disagreement — the interiority the goal asks for.',
     milestone:'You can say what you think and how you feel, and hedge it.',
     mix:[
       {act:'read',    min:25, src:'inapp', pool:'intermediate'},
       {act:'produce', min:20, src:'inapp'},
       {act:'grammar', min:15, src:'inapp'},
       {act:'srs',     min:15, src:'inapp'},
       {act:'listen',  min:20, src:'external', res:'podcasts'},
       {act:'tutor',   min:45, src:'external', res:'tutor', cadence:'weekly'},
       {act:'encode',  min:10, src:'inapp'},
     ]},
    {id:4, name:'Narrative', hours:400,
     focus:'Past tense, sequencing, “one time I…”, timing. Stories are the currency of a dinner table.',
     milestone:'You can tell a story about something that happened, start to finish.',
     mix:[
       {act:'read',     min:25, src:'inapp', pool:'intermediate'},
       {act:'drill432', min:20, src:'inapp', pool:'intermediate'},
       {act:'produce',  min:20, src:'inapp'},
       {act:'grammar',  min:15, src:'inapp'},
       {act:'srs',      min:15, src:'inapp'},
       {act:'listen',   min:20, src:'external', res:'podcasts'},
       {act:'tutor',    min:60, src:'external', res:'tutor', cadence:'weekly'},
     ]},
    {id:5, name:'Nuance', hours:500,
     focus:'Humor, sympathy, politeness, teasing, disagreeing warmly. Where “being yourself” actually lives.',
     milestone:'You can be warm, funny, and diplomatic — recognizably yourself.',
     mix:[
       {act:'read',    min:25, src:'inapp', pool:'advanced'},
       {act:'produce', min:25, src:'inapp'},
       {act:'listen',  min:25, src:'external', res:'youtube'},
       {act:'read',    min:15, src:'inapp', pool:'news'},
       {act:'srs',     min:15, src:'inapp'},
       {act:'tutor',   min:60, src:'external', res:'tutor', cadence:'weekly'},
     ]},
    {id:6, name:'The table', hours:575,
     focus:'Multi-party listening, overlap, noise, the hospitality ritual. The final skill — trained deliberately, not left to chance.',
     milestone:'You can follow several people at once and be yourself at a Palestinian family dinner.',
     mix:[
       {act:'listen',  min:30, src:'external', res:'dialogue'},
       {act:'produce', min:25, src:'inapp'},
       {act:'read',    min:20, src:'inapp', pool:'news'},
       {act:'read',    min:15, src:'inapp', pool:'advanced'},
       {act:'srs',     min:15, src:'inapp'},
       {act:'tutor',   min:60, src:'external', res:'tutor', cadence:'weekly'},
     ]},
  ],
};
