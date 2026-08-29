/* Modern Hebrew language pack — CHROME ONLY, not yet selectable.

   This exists now, ahead of its content, for two reasons.

   It proves the seam. A pack that registers and appears in the switcher is a real test that
   app.js no longer assumes Arabic; if adding this file had required touching app.js, the seam
   would not be doing its job.

   And it is honest in the interface. The switcher shows both flags from the start, with Hebrew
   plainly marked as still being built, rather than hiding the second language until it is done
   and pretending the app was always bilingual.

   `ready: false` is load-bearing: app.js refuses to ACTIVATE a pack that is not ready, so a
   hand-typed ?lang=he cannot boot a Hebrew shell on top of Arabic data. The real separation —
   per-language data directories, per-language storage — lands in B4 and B5. Until then this
   pack deliberately carries no verb model, no clitic tables and no section art, because a
   half-filled pack that silently fell back to Arabic's rules is exactly the failure the
   validator exists to prevent.

   Stage A measured what will fill it: 176,610 lexicon rows over 12,662 lemmas at 94.6% coverage
   of live Hebrew news, 2,084 pointed verb paradigms verified at 98.99%, and eleven_v3 confirmed
   to read niqqud.  See spike/he/FINDINGS.md. */
defineLang({
  code: 'he',
  ready: false,
  dir: 'rtl',
  flag: '🇮🇱',        // Israeli flag
  name: 'Modern Hebrew',
  nativeName: 'עברית',
  short: 'Hebrew',
  // Hebrew needs its own stack: the Arabic faces have no Hebrew coverage, and the system
  // Hebrew faces render niqqud far better than a generic serif fallback.
  font: '"Taamey Frank CLM","SBL Hebrew","Ezra SIL","Times New Roman",serif',
  // Declared now, though nothing is built yet: switchLang() and sectionElsewhere() read this
  // to answer "does the other language have this section". The Dinner Table and Videos are
  // absent on purpose -- the Shabbat-table dialogues and a Hebrew playlist are Stage C work,
  // and listing a section before it exists is the kind of lie this pack is meant to avoid.
  sections: ['plan', 'lessons', 'sounds', 'reactions', 'grammar', 'verbs', 'vocab',
             'news', 'stories', 'books', 'bible', 'tutor', 'translate', 'account'],
  art: {},
});
