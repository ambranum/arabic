/* Modern Hebrew — the language pack.

   Everything that makes the app Hebrew rather than Arabic: the writing system's rules, the verb
   model, the keyboard, the tutor's brief. app.js contains none of it.

   Stage A measured what fills this: 179,033 lexicon rows over 12,662 lemmas at 94.6% coverage of
   live Hebrew news, and 2,084 pointed verb paradigms verified at 98.99% against Wiktionary's own
   romanization of the 3ms past — the cell a flashcard is banked under. See spike/he/FINDINGS.md.

   Hebrew inverts Arabic's difficulty, and the pack shows it. For Arabic, pronunciation is looked
   up per entry and VOCALIZATION is the hard part. For Hebrew, niqqud → Israeli pronunciation is
   deterministic (spike/he/phon.py), so pronunciation is nearly free once you have the pointing —
   and there is no CAPHI-style sub-dialect system to model, which is why `phon.variants` is empty
   where Arabic's carries Wadi Ara. */
defineLang({
  code: 'he',

  lex: {
    // Hebrew's index is a dictionary in its own right, built from Wiktionary rather than from
    // any text the app ships -- so the corpus, empty or not, cannot stand in for it.
    source: 'lexicon',
    name: 'Wiktionary',
    blurb: 'a 12,662-lemma Hebrew lexicon with the pointing, the binyan and the root',
    credit: '<b>English Wiktionary</b> via <a href="https://kaikki.org/dictionary/Hebrew/" '
          + 'target="_blank" rel="noopener" style="color:var(--verdigris)">kaikki.org</a>, '
          + 'CC BY-SA 4.0 — extracted by spike/he/build_lex.py, pronunciation from the pointing.',
  },

  // ---- the writing system ---------------------------------------------------------------
  script: {
    // MUST match he_norm() in spike/he/build_lex.py, which keyed the shipped lexicon: strip
    // cantillation and pointing, drop geresh and gershayim, fold the five final letters.
    // pipeline/verify_he_norm.py compares the two over every key in the index.
    //
    // Deliberately NOT folding ktiv male/haser — the optional yod and vav of unpointed spelling.
    // That is a real ambiguity, and folding it would merge distinct words.
    norm: s => (s || '').normalize('NFC')
      .replace(/[֑-ׇ]/g, '')
      .replace(/[׳״]/g, '')
      .replace(/[ךםןףץ]/g,
               c => 'כמנפצ'['ךםןףץ'.indexOf(c)])
      .trim(),
    run: /([֐-׿יִ-ﭏ][\s֐-׿יִ-ﭏ]*)/,
    // Does a string contain any Hebrew? Asked wherever the app has to tell "the learner
    // typed the target language" from "the learner typed English".
    chars: /[֐-׿יִ-ﭏ]/,
    punct: '.,;:?!…"«»“”\'()-—[]{}–׳״',
    // Hebrew's clitics are a SLOT SYSTEM, not a list of glued words: a conjunction, then a
    // preposition or the relativizer, then the article — וְשֶׁבַּבַּיִת is ו+ש+ב+ה. Shortest first,
    // so the least is cut away; the peeling algorithm itself is language-generic.
    pre: ['ו', 'ב', 'כ', 'ל', 'מ', 'ש', 'ה',
          'וה', 'וב', 'ול', 'ומ', 'וש',
          'שב', 'של', 'שה', 'כש', 'מש',
          'וכש', 'לכש'],
    // Pronominal endings: possessive on nouns, object on verbs and prepositions.
    suf: ['י', 'ך', 'כ', 'ו', 'ה', 'ם', 'ן',
          'נו', 'כם', 'כן', 'הם', 'הן',
          'יו', 'יה', 'יך', 'ים'],
    minStem: 2,                 // Hebrew roots are three letters, but a stem can surface as two
    fixes: {},                  // nothing corrected yet — the honest state before real content
  },

  // No sub-dialect axis. Israeli Hebrew has regional and register variation, but nothing with
  // the systematic, per-phoneme shape Wadi Ara has on the Arabic side, so nothing is claimed.
  phon: {
    fields: {main: 'caphi', urban: 'caphi', raw: 'caphi_raw'},
    variants: [],
  },

  // ---- the verb model -------------------------------------------------------------------
  verb: {
    classNoun: 'binyan',
    classPlural: 'Binyanim',
    blurb: n => `Hebrew verbs are built on three-letter roots, run through seven patterns called
      <b>binyanim</b> — "buildings". The binyan sets the voice and the flavour of the action;
      the root supplies the meaning. Browse by binyan below, or search across all ${n} verbs.
      Every paradigm here is looked up, fully pointed, from Wiktionary — none of it is derived.`,
    weakBlurb: '',
    // The same renderer as Arabic, driven by a different descriptor. Hebrew's present is four
    // cells (gender × number, no person) where Arabic's is eight, and the infinitive is a single
    // cell — both fall out of the renderer's one rule, skip any row or table with no filled
    // cells, with no `if (LANG.code === 'he')` anywhere in the UI.
    rowSets: {
      pres: [['ms', 'he / I (m)', 'הוא'], ['fs', 'she / I (f)', 'היא'],
             ['mp', 'they (m)', 'הם'], ['fp', 'they (f)', 'הן']],
      imp: [['ata', 'you (m)', 'אתה'], ['at', 'you (f)', 'את'],
            ['atem', 'you (pl)', 'אתם']],
      inf: [['-', 'to …', '']],
    },
    tables: [
      {kind: 'grid', rows: 'persons', cols: [
        {slot: 'past', label: 'Past', short: 'Past'},
        {slot: 'fut',  label: 'Future', short: 'Fut.'}]},
      // Hebrew's present is a participle: it inflects for gender and number, never for person,
      // so "I write / you write / he writes" are one form.
      {kind: 'strip', label: 'Present (gender and number, not person)', rows: 'pres', slot: 'pres'},
      {kind: 'strip', full: true, label: 'Imperative', rows: 'imp', slot: 'imp'},
      {kind: 'strip', full: true, label: 'Infinitive', rows: 'inf', slot: 'inf'},
    ],
    classOrder: ['paal', 'piel', 'hifil', 'nifal', 'hitpael', 'pual', 'hufal'],
    classInfo: {
      paal:    ['Paʿal', 'The base verb — the plain action, and much the biggest group. כָּתַב “he wrote”.'],
      piel:    ['Piʿel', 'Doubled middle root letter. Often intensive, or makes a verb from a noun — דִּבֵּר “he spoke”.'],
      hifil:   ['Hifʿil', 'A hi- prefix. Causative: making someone do the thing — הִכְתִיב “he dictated”.'],
      nifal:   ['Nifʿal', 'An n- prefix. Passive or middle voice of paʿal — נִכְתַב “it was written”.'],
      hitpael: ['Hitpaʿel', 'A hit- prefix. Reflexive or reciprocal — הִתְכַתֵּב “he corresponded”.'],
      pual:    ['Puʿal', 'The passive of piʿel. Mostly met in the present, as a participle — מְדֻבָּר “spoken”.'],
      hufal:   ['Hufʿal', 'The passive of hifʿil. Rare in speech; you meet it in writing and the news.'],
    },
    // No separate weak axis yet. Hebrew's gzarot (פ"נ, ע"ו, ל"ה …) are real and worth teaching, but
    // Wiktionary does not label them and deriving them is its own piece of work. An empty table
    // means no badge and no "irregular" shelf — absent rather than guessed.
    weakInfo: {},
    weakOrder: [],
    persons: [
      ['ani', 'I', 'אֲנִי'], ['ata', 'you (m)', 'אַתָּה'],
      ['at', 'you (f)', 'אַתְּ'], ['hu', 'he', 'הוּא'],
      ['hi', 'she', 'הִיא'], ['anaxnu', 'we', 'אֲנַחְנוּ'],
      ['atem', 'you (pl)', 'אַתֶם'], ['hem', 'they', 'הֵם'],
    ],
    // Difficulty tracks the BINYAN, which is the whole reason this is a function per pack rather
    // than a table shared with Arabic: paʿal is where everyone starts, the passives are last
    // because they are mostly read rather than said.
    tier: v => ({paal: 1, nifal: 2, piel: 2, hifil: 2, hitpael: 3, pual: 3, hufal: 3})[v.form] || 2,
  },

  // ---- keyboard, voice ------------------------------------------------------------------
  kbd: {
    toggle: 'א', title: 'Hebrew keyboard',
    numsLabel: '123', lettersLabel: 'א ב ג',
    diacritic: 'ַ', diacriticLabel: 'ִַָ',
    // The standard Israeli layout, which is the one a Hebrew speaker's fingers already know.
    letters: [
      ['ק', 'ר', 'א', 'ט', 'ו', 'ן', 'ם', 'פ'],
      ['ש', 'ד', 'ג', 'כ', 'ע', 'י', 'ח', 'ל', 'ך', 'ף'],
      ['ז', 'ס', 'ב', 'ה', 'נ', 'מ', 'צ', 'ת', 'ץ'],
    ],
    nums: [
      ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
      ['-', '/', ':', ';', '(', ')', '%', '&', '@', '"'],
      [',', '.', '?', '!', '׳', '״', '–'],
    ],
    hold: {
      'כ': ['ך'], 'מ': ['ם'], 'נ': ['ן'],
      'פ': ['ף'], 'צ': ['ץ'],
      // The pointing, on one key: the vowels, then shva, then dagesh.
      'ַ': ['ַ', 'ָ', 'ֵ', 'ֶ', 'ִ', 'ֹ', 'ֻ', 'ְ', 'ּ'],
    },
  },
  tts: {lang: 'he-IL', voiceRe: /^he/i},
  searchHint: 'בית · הלך · house · tired…',
  // A plain rule, not a motif. Arabic's home page carries tatreez and the Old City; borrowing
  // either for a Hebrew learner would be a claim about whose page this is. A Hebrew visual
  // identity is worth designing rather than defaulting into, so until then: a line.
  ornament: () => '<div class="tz-rule" style="height:1px;background:var(--rule)"></div>',
  // skyline: deliberately absent — see ornament.
  // Hebrew day and month names as Israelis write them: יום ראשון … and the Gregorian months,
  // which is what a calendar in Israel actually says. The Hebrew calendar's own months are a
  // different thing and are not what a date line means here.
  dateLine: d => {
    const DAYS = ['יוֹם רִאשׁוֹן', 'יוֹם שֵׁנִי', 'יוֹם שְׁלִישִׁי', 'יוֹם רְבִיעִי',
                  'יוֹם חֲמִישִׁי', 'יוֹם שִׁישִׁי', 'שַׁבָּת'];
    const MONTHS = ['יָנוּאָר', 'פֶבְּרוּאָר', 'מֶרְץ', 'אַפְּרִיל', 'מַאי', 'יוּנִי',
                    'יוּלִי', 'אוֹגוּסְט', 'סֶפְּטֶמְבֶּר', 'אוֹקְטוֹבֶּר', 'נוֹבֶמְבֶּר', 'דֶּצֶמְבֶּר'];
    return DAYS[d.getDay()] + ', ' + d.getDate() + ' ' + MONTHS[d.getMonth()];
  },

  homeMasthead: () => `<div class="hm-mark">עִבְרִית <em>מְדֻבֶּרֶת</em></div>`,
  chapterPrefix: /^פרק[^—]*—\s*/,

  bibleBlurb: 'ESV ‖ Hebrew, side by side',
  tutorStarters: [
    'What’s the difference between לא and אין?',
    'How do I say “I’ve been waiting for an hour” in everyday Hebrew?',
    'When do Israelis actually use the future tense for a request?',
    'Give me 3 natural things to say when someone cooks me a great meal.',
    'Is היננו something people say, or only write?',
  ],

  tutorPrompt: ({grammar, sounds, reactions}) => {
    const gram = grammar.map(l => l.title).filter(Boolean).slice(0, 24).join('; ');
    const snds = sounds.map(L => L.target || L.en).filter(Boolean).join('; ');
    const rxc = reactions.map(c => c.en).filter(Boolean).join('; ');
    return [
      "You are a warm, precise tutor for MODERN SPOKEN ISRAELI HEBREW — the everyday speech of Tel Aviv, Jerusalem and Haifa. The learner is an English speaker in a self-study app, working toward holding their own in ordinary conversation.",
      "",
      "How to answer:",
      "- Answer in SPOKEN Israeli Hebrew, not Biblical or literary Hebrew. Where the spoken form differs from the written register, give the spoken one and note the difference briefly. If the learner's phrase is Biblical or bookish, say so gently and give what people actually say.",
      "- For any Hebrew you give: pointed Hebrew script, then a simple transliteration in parentheses, then the English gloss. Point the Hebrew — the pointing is what makes it readable, and this app shows it everywhere.",
      "- Pronunciation model to reflect in transliterations: ר is uvular; ח and כ (without dagesh) are both a throaty kh; ע and א are silent for most speakers; צ is ts; stress is usually final (milra). e.g. שָׁלוֹם = shaLOM, בֹּקֶר טוֹב = BOker tov.",
      "- Honesty first: if you're not sure something is current spoken usage rather than textbook Hebrew, say so plainly. Never invent a proverb, a “Israelis always say…”, or confident detail you're unsure of.",
      "- You can explain grammar, translate, compare near-synonyms, give example sentences, and role-play short exchanges. Match the learner's level; be encouraging and concrete.",
      "",
      "SAVING PHRASES (important): when your answer teaches a specific Hebrew word or phrase the learner can reuse — above all for “how do I say…” questions — finish your ENTIRE reply with a machine-readable block listing the 1–4 most useful save-worthy items, each on its own line as “Hebrew = English” (Hebrew script only in this block, NO transliteration):",
      "<save>",
      "אֲנִי רוֹצֶה = I want",
      "אֲנִי רוֹצֶה לָלֶכֶת הַבַּיְתָה = I want to go home",
      "</save>",
      "Only list phrases genuinely worth memorizing as-is. For a pure grammar explanation with no single save-worthy phrase, omit the block entirely. Write nothing after </save>.",
      "",
      "This app already teaches the learner these things — reference them naturally, don't just list them:",
      "• Grammar structures: " + (gram || "(various spoken structures)"),
      "• Pronunciation contrasts: " + (snds || "(Israeli sound contrasts)"),
      "• Conversational reaction categories: " + (rxc || "(everyday reactions)"),
    ].join("\n");
  },

  // The engraved section banners are Arabic-side work that has no Hebrew equivalent yet. An
  // empty map means the sections render without a banner rather than borrowing Jaffa and Acco
  // for a Hebrew learner, which would be a different and worse kind of wrong.
  art: {},
});
