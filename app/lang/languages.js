/* The roster: which languages exist, what each one is called, and what each one loads.
   window.LANGUAGES

   This is the ONE file that is always fetched, in every language, before anything else. It is
   deliberately tiny, because everything downstream is a decision made from it: which pack to
   load, which 15 MB of data to load, what to put in the switcher, and -- when a new visitor has
   not chosen yet -- what to offer them.

   It exists because a language pack cannot answer "which language should we load?" without
   already being loaded. Reading the roster first is what lets a Hebrew learner never download a
   byte of Arabic. It also means the switcher can list a language whose pack is not in memory,
   which is what makes the second flag honest rather than decorative.

   `ready` lives here rather than in the pack for the same reason: the boot script has to know
   whether a language can be activated BEFORE it decides to fetch it.

   `data` is the load order for `app/data/<code>/<name>.js`, and it is an order, not a set --
   these files assign to globals that app.js reads at its own top level.

   `sections` is here rather than in the pack for the same reason `ready` is: the app has to
   answer "does the OTHER language have this section?" -- for the switcher, and for the page
   that explains why a deep link went nowhere -- without that language's pack in memory. The
   order is the teaching order, and it differs between the two. */
window.LANGUAGES = [
  {
    code: 'ar',
    ready: true,
    dir: 'rtl',
    flag: '🇵🇸',           // Palestinian flag
    name: 'Palestinian Arabic',
    nativeName: 'عربي فلسطيني',
    short: 'Arabic',
    blurb: 'The spoken dialect of Palestine — what people actually say, not Modern Standard.',
    font: '"Geeza Pro","SF Arabic","Damascus","Al Bayan",serif',
    data: ['library', 'verbs', 'vocab_audio', 'curriculum', 'assess', 'grammar',
           'lessons', 'reactions', 'sounds', 'table', 'bible-index'],
    sections: ['plan', 'lessons', 'sounds', 'reactions', 'grammar', 'verbs', 'vocab',
               'news', 'stories', 'table', 'books', 'videos', 'listening', 'bible',
               'tutor', 'translate', 'account'],
  },
  {
    code: 'he',
    ready: true,
    dir: 'rtl',
    flag: '🇮🇱',           // Israeli flag
    name: 'Modern Hebrew',
    nativeName: 'עברית',
    short: 'Hebrew',
    blurb: 'Spoken Israeli Hebrew. Sounds, verbs, grammar, the dictionary, 90 graded stories, a public-domain shelf, the daily paper and the Bible.',
    font: '"Taamey Frank CLM","SBL Hebrew","Ezra SIL","Times New Roman",serif',
    data: ['library', 'verbs', 'sounds', 'reactions', 'grammar', 'lessons', 'curriculum',
           'assess', 'vocab_audio', 'bible-index'],
    // What actually exists, and nothing else. Hebrew arrives with the things Stage A proved
    // could be LOOKED UP rather than written -- 2,084 pointed paradigms and a 12,662-lemma
    // dictionary -- the sections built on them, the daily paper written fresh each morning by
    // the same job that writes the Arabic one, and Sounds, whose lessons are curated teaching
    // but whose every WORD, vowel, reading and meaning is the lexicon's. Since then the authored
    // content has landed too: 90 graded stories, 20 grammar lessons, the reactions, and the
    // Ben-Yehuda shelf, and now the lessons -- which could not be transcribed the way Arabic's
    // were, because the Hebrew reference shelf is commercial and this repo is the public site,
    // so they are written in those books' idiom instead and are worked rather than read. The
    // dinner table is the one that does not exist yet, and listing a section before it exists
    // is a lie the switcher would tell on every page.
    sections: ['plan', 'lessons', 'sounds', 'reactions', 'grammar', 'verbs', 'news', 'stories',
               'books', 'bible', 'vocab', 'translate', 'tutor', 'account'],
  },
];
