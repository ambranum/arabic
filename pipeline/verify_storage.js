#!/usr/bin/env node
/* B4 verification: prove the storage migration cannot lose study history.
 *
 * Namespacing localStorage by language (`alp.cards.v1` -> `alp.ar.cards.v1`) is the only change
 * in this app that touches data a person cannot recreate -- a year of spaced repetition, a study
 * log, a plan. And it propagates: whatever this device decides is pushed to Supabase and then to
 * every other device, so a mistake is not local and is not noticed until the deck looks empty.
 *
 * So the migration is tested as a pure function over a storage snapshot, against the REAL source:
 * the code below is sliced straight out of app/app.js rather than reimplemented, because a test
 * of a copy proves nothing about what ships.
 *
 *     node pipeline/verify_storage.js [path/to/a/real/backup.json]
 *
 * With no argument it runs against a synthetic snapshot in the exact shapes the app writes. Pass
 * a backup taken from Account -> "Copy backup" to run every check against real data as well.
 */
const fs = require('fs');
const path = require('path');

const SRC = fs.readFileSync(path.join(__dirname, '..', 'app', 'app.js'), 'utf8');

// ---- lift the real code out of app.js --------------------------------------------------------
function slice(from, to, label) {
  const i = SRC.indexOf(from);
  const j = SRC.indexOf(to, i + 1);
  if (i < 0 || j < 0) throw new Error('could not find ' + label + ' in app/app.js — the slice markers have drifted');
  return SRC.slice(i, j);
}
const POLICY = slice('const LANGS_ALL =', '\nmigrateStorage();', 'the storage-policy block');
const MERGE  = slice('function mergeCards(a, b)', '\nasync function pushProgress', 'the merge helpers');
const SYNC   = slice('function collectProgress()', '\n// re-read the in-memory structures', 'collect/applyProgress');

// ---- the world those slices expect -----------------------------------------------------------
class Store {                                   // a localStorage that behaves like the real one
  constructor(obj) { this.m = new Map(Object.entries(obj || {})); }
  get length() { return this.m.size; }
  key(i) { return [...this.m.keys()][i]; }
  getItem(k) { return this.m.has(k) ? this.m.get(k) : null; }
  setItem(k, v) { this.m.set(k, String(v)); }
  removeItem(k) { this.m.delete(k); }
  snapshot() { return Object.fromEntries(this.m); }
}

function load(store, verbs) {
  const sandbox = {
    localStorage: store,
    window: {VERBS: {verbs: verbs || []}},
    LANG: {code: 'ar'},
    // the same normalization app.js uses for Arabic (LANG.script.norm), narrowed to what the
    // migration needs: strip vowel marks and unify alif/ya/ta-marbuta.
    arNorm: s => String(s || '').replace(/[\u064B-\u0652\u0670\u0640]/g, '')
      .replace(/[\u0622\u0623\u0625]/g, '\u0627').replace(/\u0649/g, '\u064A').replace(/\u0629/g, '\u0647'),
    _applyingRemote: false,
    reloadState: () => {},
    SYNC_AT: 'alp.sync.at',
  };
  const names = Object.keys(sandbox);
  const body = MERGE + '\n' + SYNC + '\n' + POLICY + '\n' + `
    return {migrateStorage, legacyKeys, isGlobalKey, noSync, reseedSeen, mergeProgress,
            collectProgress, applyProgress, mergeCards, unionArr, LKEY, MERGERS};`;
  return new Function(...names, body)(...names.map(n => sandbox[n]));
}

// ---- checks ----------------------------------------------------------------------------------
let pass = 0, fail = 0;
function ok(cond, what, detail) {
  if (cond) { pass++; console.log('  \x1b[32m✓\x1b[0m ' + what); }
  else { fail++; console.log('  \x1b[31m✗ ' + what + '\x1b[0m' + (detail ? '\n      ' + detail : '')); }
}
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// A snapshot in the exact shapes app.js writes, including a card mid-way through SM-2.
const VERBS = [{lemma: 'كَتَب', form: 'I', pres: {ar: 'يِكْتُب'}}, {lemma: 'أَجَا', form: 'I', pres: {ar: 'يِيجِي'}},
               {lemma: 'شَاف', form: 'I', pres: {ar: 'يْشُوف'}}, {lemma: 'رَاح', form: 'I', pres: {ar: 'يْرُوح'}}];
const SYNTHETIC = {
  'alp.cards.v1': JSON.stringify([
    ['كتب', {lemma: 'كتب', deck: 'default', reps: 7, due: 1788000000000, ease: 2.36, lapses: 1, ivl: 21}],
    ['بيت', {lemma: 'بيت', deck: 'default', reps: 0, due: 0, ease: 2.5, lapses: 0, ivl: 0}],
    ['شاف', {lemma: 'شاف', deck: 'travel', reps: 12, due: 1790000000000, ease: 2.9, lapses: 0, ivl: 60}],
  ]),
  'alp.decks.v1': JSON.stringify([{id: 'default', name: 'My words', created: 1}, {id: 'travel', name: 'Travel', created: 2}]),
  'alp.activedeck.v1': 'travel',
  'alp.plan.cfg.v1': JSON.stringify({minutes: 30, startPhase: 1}),
  'alp.plan.log.v1': JSON.stringify({'2026-08-20': {done: {a: 10, b: 5}}, '2026-08-21': {done: {c: 20}}}),
  'alp.plan.seen.v1': JSON.stringify(['g:l01', 'v:0', 'v:2', 'lsn:u3', 'story-07', 'v:9999']),
  'alp.plan.extra.v1': JSON.stringify({'2026-08-20': 12}),
  'alp.plan.review.v1': JSON.stringify({'g:l01': '2026-08-20'}),
  'alp.plan.assess.v1': JSON.stringify({phase: 2, at: 1}),
  'alp.pimsleur.v1': JSON.stringify({slot: 3}),
  'alp.rev.dir.v1': 'ar-en',
  'alp.speed.v1': '0.85',
  'alp.lang': 'ar',
  'alp.esv.key': 'SECRET-ESV-KEY',
  'alp.esv.GEN.1': JSON.stringify({v: ['In the beginning...']}),
  'alp.sync.at': '1788000000000',
};

function cardsOf(snap, key) {
  const raw = snap[key];
  return raw ? new Map(JSON.parse(raw)) : new Map();
}

function run(label, before) {
  console.log('\n\x1b[1m' + label + '\x1b[0m');
  const store = new Store(before);
  const M = load(store, VERBS);

  const beforeCards = cardsOf(before, 'alp.cards.v1');
  const moved = M.migrateStorage();
  const after = store.snapshot();
  const afterCards = cardsOf(after, 'alp.ar.cards.v1');

  // 1. nothing about a card changes except which key holds it
  ok(afterCards.size === beforeCards.size,
     'card count preserved (' + beforeCards.size + ')', afterCards.size + ' after');
  let drift = [];
  for (const [k, c] of beforeCards) {
    const d = afterCards.get(k);
    if (!d) { drift.push(k + ' missing'); continue; }
    for (const f of ['reps', 'due', 'ease', 'lapses', 'ivl'])
      if (JSON.stringify(c[f]) !== JSON.stringify(d[f])) drift.push(k + '.' + f + ' ' + c[f] + '→' + d[f]);
  }
  ok(!drift.length, 'every card keeps its reps / due / ease / lapses / ivl', drift.slice(0, 5).join('; '));

  // 2. the plan log survives day for day
  const dayCount = o => Object.keys(JSON.parse(o || '{}')).length;
  ok(dayCount(after['alp.ar.plan.log.v1']) === dayCount(before['alp.plan.log.v1']),
     'plan log keeps every day (' + dayCount(before['alp.plan.log.v1']) + ')');

  // 3. globals stay put, and no per-language key is left flat
  ok(after['alp.speed.v1'] === before['alp.speed.v1'] && after['alp.lang'] === before['alp.lang'],
     'alp.speed.v1 and alp.lang stay global');
  ok(after['alp.esv.key'] === before['alp.esv.key'], 'the ESV key is untouched');
  ok(!M.legacyKeys(store).length, 'no flat per-language key is left behind',
     M.legacyKeys(store).join(', '));

  // 4. idempotence
  const again = new Store(after);
  load(again, VERBS).migrateStorage();
  const twice = again.snapshot();
  delete twice['alp.sync.at']; const once = {...after}; delete once['alp.sync.at'];
  ok(eq(Object.keys(once).sort().map(k => [k, once[k]]), Object.keys(twice).sort().map(k => [k, twice[k]])),
     'migrate(migrate(x)) === migrate(x)');

  // 5. the backup exists and holds everything that was there before
  const bk = JSON.parse(after['alp.backup.premigrate.v1'] || 'null');
  const wanted = Object.keys(before).filter(k => k.startsWith('alp.') && !k.startsWith('alp.backup.'));
  ok(bk && wanted.every(k => bk.data[k] === before[k]),
     'the pre-migration backup holds all ' + wanted.length + ' original keys');

  return {store, M, after, before};
}

// ---------------------------------------------------------------------------------------------
console.log('\x1b[1mB4 — storage namespacing\x1b[0m  (code sliced live from app/app.js)');
const base = run('synthetic snapshot', SYNTHETIC);

// ---- the resurrection case: an old device keeps pushing flat keys ----------------------------
console.log('\n\x1b[1mresurrection — a phone still on the old build pushes flat keys\x1b[0m');
{
  // this device is already migrated and has studied two more words since
  const migrated = {...base.after};
  const cards = JSON.parse(migrated['alp.ar.cards.v1']);
  cards.push(['جديد', {lemma: 'جديد', reps: 3, due: 5, ease: 2.5, lapses: 0}]);
  migrated['alp.ar.cards.v1'] = JSON.stringify(cards);
  // ...then the old phone's blob lands on top of it
  const store = new Store({...migrated, 'alp.cards.v1': SYNTHETIC['alp.cards.v1']});
  const M = load(store, VERBS);
  M.migrateStorage();
  const out = cardsOf(store.snapshot(), 'alp.ar.cards.v1');
  ok(out.size === 4 && out.has('جديد') && out.has('شاف'),
     'the union survives: 3 legacy cards + 1 new = ' + out.size);
  ok(out.get('شاف').reps === 12, 'the more-reviewed copy of a shared card wins');
  ok(!store.getItem('alp.cards.v1'), 'the resurrected flat key is folded away again');
}

// ---- applyProgress with a blob that never mentions this language -----------------------------
console.log('\n\x1b[1mapplyProgress — a remote blob missing this language must be a no-op\x1b[0m');
{
  const store = new Store({...base.after});
  const M = load(store, VERBS);
  const mine = store.getItem('alp.ar.cards.v1');
  M.applyProgress({'alp.he.cards.v1': '[]', 'alp.lang': 'he'});   // a Hebrew-only device's blob
  ok(store.getItem('alp.ar.cards.v1') === mine,
     'the Arabic deck is untouched by a blob that never names it');
  ok(store.getItem('alp.he.cards.v1') === '[]', 'the Hebrew key the blob did name was written');
}
{   // and the old failure mode, in the shape that would have caused it
  const store = new Store({...base.after});
  const M = load(store, VERBS);
  M.applyProgress({'alp.speed.v1': '1'});          // an almost-empty blob
  ok(cardsOf(store.snapshot(), 'alp.ar.cards.v1').size === 3,
     'an almost-empty blob does not wipe the deck');
}

// ---- what leaves the device ------------------------------------------------------------------
console.log('\n\x1b[1msync boundary\x1b[0m');
{
  const store = new Store({...base.after});
  const M = load(store, VERBS);
  const blob = M.collectProgress();
  ok(!Object.keys(blob).some(k => k.startsWith('alp.esv.')),
     'no ESV key and no licensed ESV text is uploaded');
  ok(!Object.keys(blob).some(k => k.startsWith('alp.backup.')), 'the local backup is not uploaded');
  ok(!('alp.sync.at' in blob), 'the sync clock is not uploaded');
  ok(Object.keys(blob).some(k => k === 'alp.ar.cards.v1'), 'the deck IS uploaded');
}

// ---- plan.seen re-keying ---------------------------------------------------------------------
console.log('\n\x1b[1mplan.seen stops keying verbs on a build index\x1b[0m');
{
  const seen = JSON.parse(base.after['alp.ar.plan.seen.v1']);
  ok(seen.includes('v:كَتَب|I|يِكْتُب') && seen.includes('v:شَاف|I|يْشُوف'),
     'v:0 and v:2 became vocalized citation keys', seen.join(' '));
  ok(!seen.some(x => /^v:\d+$/.test(x)), 'no raw index survives');
  ok(!seen.includes('v:9999'), 'an index that no longer resolves is dropped, not guessed');
  ok(seen.includes('g:l01') && seen.includes('story-07') && seen.includes('lsn:u3'),
     'non-verb ids pass through untouched');
}

// ---- optional: the user's real backup --------------------------------------------------------
const real = process.argv[2];
if (real) {
  const j = JSON.parse(fs.readFileSync(real, 'utf8'));
  const data = j && (j.data && typeof j.data === 'object' ? j.data : j);
  run('REAL backup — ' + path.basename(real) + ' (' + Object.keys(data).length + ' keys)', data);
} else {
  console.log('\n\x1b[2m(no real backup passed — run again with a path from Account → "Copy backup"' +
              ' to check the same properties against your own data)\x1b[0m');
}

console.log('\n' + (fail ? '\x1b[31m' : '\x1b[32m') + pass + ' passed, ' + fail + ' failed\x1b[0m');
process.exit(fail ? 1 : 0);
