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
// Two tiers, because "not finished" and "broken" are different claims.
//
// CHROME is what any pack must have to be listed in the switcher at all -- enough to draw a
// flag and a name. A pack that cannot manage this is malformed.
//
// FULL is what a pack must have to be ACTIVATED, and it is checked only for `ready: true`.
// A pack declaring ready:false is saying "do not use me yet"; demanding the whole contract
// from it would mean a half-built language could not even appear as "coming soon". The
// guarantee that matters is unchanged: nothing incomplete is ever switched ON.
const LANG_CHROME = ['code', 'dir', 'flag', 'name', 'nativeName', 'short', 'font'];
const LANG_FULL = LANG_CHROME.concat([
  'art', 'script.norm', 'script.run', 'script.punct', 'script.pre', 'script.suf',
  'script.minStem', 'script.fixes', 'phon.fields', 'verb.classOrder', 'verb.persons',
  'verb.tier', 'kbd.letters', 'kbd.toggle', 'tts.lang', 'tutorPrompt',
  'homeMasthead', 'chapterPrefix', 'sections', 'verb.classNoun', 'bibleBlurb',
  'tutorStarters', 'lex.name', 'lex.blurb', 'lex.credit',
  'verb.blurb', 'verb.classPlural', 'verb.weakOrder', 'lex.source',
  'script.chars', 'searchHint', 'dateLine', 'ornament']);

// Read only on a path a pack can switch off. `planGoal` is shown by the home screen's
// "build your plan" card, which only renders for a language that lists a `plan` section --
// so requiring it of every pack would force a language with no curriculum to invent a goal.
const LANG_IF_PLAN = ['planGoal'];

// Identity comes from the roster, not from the pack. `code`, `flag`, `name`, `short` and
// `ready` have to be readable BEFORE a pack is fetched -- the boot script picks a language and
// the switcher lists both of them without either pack in memory -- so lang/languages.js owns
// them and defineLang folds them in. Writing them twice would mean a pack could disagree with
// the roster about its own name, and the one the user saw would depend on load order.
function defineLang(spec) {
  const meta = (window.LANGUAGES || []).find(l => l.code === (spec || {}).code);
  if (!meta) {
    throw new Error('language pack "' + ((spec || {}).code) + '" is not in lang/languages.js');
  }
  ['dir', 'flag', 'name', 'nativeName', 'short', 'brand', 'font', 'ready', 'sections']
    .forEach(k => { spec[k] = meta[k]; });
  const required = spec.ready === false ? LANG_CHROME
    : LANG_FULL.concat((spec.sections || []).includes('plan') ? LANG_IF_PLAN : []);
  const missing = required.filter(
    k => k.split('.').reduce((o, part) => (o == null ? o : o[part]), spec) == null);
  if (missing.length) {
    throw new Error('language pack "' + (spec && spec.code) + '" is missing: ' + missing.join(', '));
  }
  (window.LANG_PACKS || (window.LANG_PACKS = {}))[spec.code] = spec;
  return spec;
}
