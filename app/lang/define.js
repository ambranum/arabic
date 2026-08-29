/* The contract a language pack registers against.  window.defineLang, window.LANG_PACKS

   Loads FIRST, before any pack, because a pack calls defineLang() at its own top level.
   It lived in app.js for about ten minutes and the browser said so immediately: app.js is
   last in the load order, so every pack failed with "defineLang is not defined". A contract
   cannot be defined after the things that have to satisfy it. */
// This app teaches ONE language at a time, and which one is a load-time decision. Everything
// that makes it Arabic rather than Hebrew -- the writing system's rules, the verb model, the
// keyboard, the tutor's brief, the section banners -- lives in a pack under app/lang/ and is
// reached through LANG. Nothing below this line contains Arabic.
//
// defineLang() VALIDATES rather than merges. A pack that forgets verb.citation must fail at
// boot, loudly, because the alternative is silently falling through to another language's rule
// and banking a learner's flashcards under the wrong key. There are no `||` fallbacks in the
// seam; the two genuinely optional fields say so at their read sites instead.
const LANG_REQUIRED = ['code', 'dir', 'flag', 'name', 'nativeName', 'short', 'font', 'art'];

function defineLang(spec) {
  const missing = LANG_REQUIRED.filter(
    k => k.split('.').reduce((o, part) => (o == null ? o : o[part]), spec) == null);
  if (missing.length) {
    throw new Error('language pack "' + (spec && spec.code) + '" is missing: ' + missing.join(', '));
  }
  (window.LANG_PACKS || (window.LANG_PACKS = {}))[spec.code] = spec;
  return spec;
}
