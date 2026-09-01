// The active pack. One language per page load -- switching is a reload, because every data
// global below is const-bound and eagerly indexed, so swapping them in place would leave a
// dozen derived caches stale and make every future cache someone adds a silent switch bug.
// A pack must be READY to be activated. A hand-typed ?lang=he would otherwise boot the
// Hebrew chrome on top of Arabic data, which looks like a working switch and is not one.
const _wanted = document.documentElement.getAttribute('data-lang');
const LANG = ((window.LANG_PACKS[_wanted] || {}).ready !== false && window.LANG_PACKS[_wanted])
          || window.LANG_PACKS.ar;
const SEC_ART = LANG.art;
// data-lang only. NOT dir: LANG.dir describes the SCRIPT, and the elements that render target-
// language text set dir="rtl" themselves. Putting it on <html> flips the whole chrome -- the
// header, the English prose, the button order -- which is a different thing entirely and was
// visibly wrong the moment it was tried.
document.documentElement.setAttribute('data-lang', LANG.code);

// The switcher: a flag per language, top right. It reads the ROSTER, not the loaded packs --
// only one pack is ever in memory now, so asking LANG_PACKS what languages exist would draw a
// switcher with one flag and nothing to switch to.
function langSwitchHTML() {
  const packs = window.LANGUAGES || [];
  if (packs.length < 2) return '';
  return '<div class="langsw" role="group" aria-label="Language">' + packs.map(p => {
    const on = p.code === LANG.code, soon = p.ready === false;
    return `<button class="langsw-b${on ? ' on' : ''}${soon ? ' soon' : ''}"
       aria-pressed="${on}" ${soon ? 'disabled' : ''}
       title="${esc(soon ? p.name + ' — being built' : p.name)}"
       onclick="switchLang('${p.code}')"><span class="langsw-f">${p.flag}</span>
       <span class="langsw-n">${esc(p.short)}</span></button>`;
  }).join('') + '</div>';
}

// A full reload, deliberately -- see the comment on LANG. Keeps your place when the section
// exists on the other side, and lands on home when it does not.
const langMeta = code => (window.LANGUAGES || []).find(l => l.code === code);
function switchLang(code) {
  const p = langMeta(code);
  if (!p || p.ready === false || code === LANG.code) return;
  try { localStorage.setItem('alp.lang', code); } catch (e) {}
  const sec = (location.hash.slice(1).split('/')[1]) || '';
  const has = (p.sections || []).includes(sec);
  // ?lang= is what the boot script in index.html reads, and the reload is what makes the switch
  // real: the other language's 15 MB has to be fetched, and this page has this language's.
  location.replace(location.pathname + '?lang=' + code + (has ? '#/' + sec : '#/'));
}

// ---------- storage policy: one device, two languages ----------
// Everything this app remembers is a `alp.*` key in localStorage. Two languages now share one
// device and one Supabase row, so almost every key is namespaced BY LANGUAGE:
// `alp.ar.cards.v1` and `alp.he.cards.v1` are different decks, different plans, different
// progress, and neither can see the other. That separation is the point of B4 -- a Hebrew
// learner's streak has nothing to do with their Arabic one.
//
// Three kinds of key deliberately stay outside the namespace:
//   GLOBAL_KEYS  -- a property of the person or the device rather than of a language: which
//                   language you last used, how fast you like audio, when this device last
//                   changed. Duplicating those per language would just make them disagree.
//   alp.esv.*    -- your ESV API key and the English chapters it fetches. English is neither of
//                   the two languages, and the text is licensed, so it is global AND never
//                   synced: until now every chapter you read was being copied to your Supabase
//                   row and growing it forever.
//   alp.backup.* -- the pre-migration snapshot written below. A local safety net; pushing it
//                   would double the size of every sync.
const LANGS_ALL = ['ar', 'he'];
const GLOBAL_KEYS = new Set(['alp.lang', 'alp.speed.v1', 'alp.sync.at', 'alp.marked.v1',
                             'alp.read.v1']);
const isGlobalKey = k => GLOBAL_KEYS.has(k) || k.startsWith('alp.esv.') || k.startsWith('alp.backup.');
const noSync = k => k === 'alp.sync.at' || k.startsWith('alp.esv.') || k.startsWith('alp.backup.');
// The single place a per-language key is built. Every `const *KEY` below goes through it, so
// "which language owns this data" is answered once instead of at thirteen call sites.
const LKEY = k => 'alp.' + LANG.code + '.' + k;
const _pj = s => { try { return JSON.parse(s); } catch (e) { return null; } };
// base key name -> how two copies of it combine. Used twice: when the cloud first meets a device
// (mergeProgress), and when a legacy key meets its namespaced replacement (migrateStorage). A
// key with no entry here is a scalar or a config blob: the newer side wins outright.
const MERGERS = {'cards.v1': mergeCards, 'decks.v1': unionById, 'plan.seen.v1': unionArr,
                 'plan.log.v1': mergeLog, 'plan.extra.v1': mergeExtra};

// `plan.seen.v1` used to key a finished verb as `v:<index into VB>`. That index is assigned at
// build time and shifts every time build_verbs.py reorders the list, so the record of what you
// had studied silently pointed at a different verb after each rebuild. Key on the verb itself
// instead.
//
// Which parts of "the verb itself": the VOCALIZED citation form, the measure, and the vocalized
// present. Measured over the 2,459 conjugating verbs, the bare consonantal skeleton collides for
// 786 of them -- فتح is both "open" and "be opened", لِزِم and لَزَم are different verbs -- so a
// normalized key would silently tick two verbs off the walk at once. These three fields together
// collide for none, and none of them depends on build order.
const verbKey = v => 'v:' + v.lemma + '|' + (v.form || '') + '|' + ((v.pres && v.pres.ar) || '');
// An index that no longer resolves is dropped rather than guessed: a wrong verb marked done is
// worse than one left unmarked.
function reseedSeen(ids) {
  const VBs = (window.VERBS && window.VERBS.verbs) || [];
  const out = [];
  for (const id of ids || []) {
    if (typeof id !== 'string' || !/^v:\d+$/.test(id)) { out.push(id); continue; }
    const v = VBs[+id.slice(2)];
    if (v) out.push(verbKey(v));
  }
  return [...new Set(out)];
}

// ---- migration: legacy `alp.<key>` -> `alp.ar.<key>` ----
// Everything written before the split is Palestinian Arabic, so legacy keys belong to `ar` no
// matter which language is booting now.
//
// It is a MERGE, not a move, and it runs on every boot AND after every remote apply. That
// second part is what makes it safe: a phone that hasn't reloaded the new build keeps pushing
// flat `alp.cards.v1` into the same Supabase row, so legacy keys can reappear at any time. A
// move would let that older flat deck overwrite the newer namespaced one; a merge folds them
// together and the union survives. Idempotent by construction -- once a legacy key is folded it
// is deleted, so a second run has nothing to do.
const LEGACY_OWNER = 'ar';
function legacyKeys(store) {
  const out = [];
  for (let i = 0; i < store.length; i++) {
    const k = store.key(i);
    if (k && k.startsWith('alp.') && !isGlobalKey(k)
        && !LANGS_ALL.some(c => k.startsWith('alp.' + c + '.'))) out.push(k);
  }
  return out;
}
function migrateStorage(store) {
  store = store || localStorage;
  const flat = legacyKeys(store);
  if (!flat.length) return 0;
  // A snapshot of everything, taken before the first key moves, so a bad migration is
  // recoverable from this device alone -- Account -> "Backup & restore" reads it back out.
  if (!store.getItem('alp.backup.premigrate.v1')) {
    const snap = {};
    for (let i = 0; i < store.length; i++) { const k = store.key(i);
      if (k && k.startsWith('alp.') && !k.startsWith('alp.backup.')) snap[k] = store.getItem(k); }
    try { store.setItem('alp.backup.premigrate.v1', JSON.stringify({at: Date.now(), data: snap})); }
    catch (e) { return 0; }        // no room for the backup means no migration: leave data alone
  }
  for (const k of flat) {
    const base = k.slice(4), dst = 'alp.' + LEGACY_OWNER + '.' + base;
    let val = store.getItem(k);
    if (base === 'plan.seen.v1') val = JSON.stringify(reseedSeen(_pj(val) || []));
    const cur = store.getItem(dst), fn = MERGERS[base];
    // Argument order matters: the already-namespaced copy is the newer one and wins every tie.
    if (cur != null) val = fn ? JSON.stringify(fn(_pj(cur), _pj(val))) : cur;
    try { store.setItem(dst, val); store.removeItem(k); } catch (e) {}
  }
  // Local storage really did change, so say so: without this the cloud copy (still all legacy
  // keys) can look newer than the device that just cleaned itself up.
  try { store.setItem('alp.sync.at', String(Date.now())); } catch (e) {}
  return flat.length;
}
migrateStorage();

// ---------- persistence: the memorization deck ----------
// localStorage, on this device, no server. Each word you "don't know" becomes a CARD keyed
// by LEMMA (so it's the same card in every text), carrying its lexicon data, the sentence you
// met it in, and its spaced-repetition state (Anki's SM-2). `marked` = the card map; the
// reader highlights any word that has a card.
const KEY = LKEY('cards.v1');
const DKEY = LKEY('decks.v1');
const now = () => Date.now();
const DAY = 864e5;

let marked = new Map();
try { marked = new Map(JSON.parse(localStorage.getItem(KEY) || 'null') || []); } catch (e) {}
if (!marked.size) {   // one-time migration from the old marked-words list
  try {
    const old = JSON.parse(localStorage.getItem('alp.marked.v1') || '[]');
    for (const [l, m] of old) marked.set(l, srsInit({lemma: l, ...m, deck: 'default'}));
  } catch (e) {}
}
// The deck is keyed by the lemma STRING, and the same word reaches it under different
// vocalizations depending on where you added it from: the reader uses the corpus's resolved
// lemma, the verb page uses verbs.js's citation form, and for 215 of 461 verb tokens those two
// disagree (إجا vs أَجَا, رَوح vs رَوَّح). Adding the same verb from two places therefore made two
// cards, each with its own schedule. Now that a word can be banked from the verb page, the
// translator and the reader, that had to be settled.
//
// Rather than re-key the deck — it is live study data, and a migration that mis-merges two
// genuinely different words is worse than the duplicate — membership is matched on the
// NORMALIZED lemma. An existing card wins its key, so a verb you banked months ago from a story
// still reads "in your deck" on its conjugation page, and removing it there removes that card.
// Namespaced keys (¶ phrases, ® reactions) keep their prefix through arNorm and never collide.
let _deckNormIx = null;
function deckNormIndex() {
  if (_deckNormIx) return _deckNormIx;
  const m = new Map();
  for (const k of marked.keys()) { const n = arNorm(k); if (!m.has(n)) m.set(n, k); }
  // Cards banked before verbs were canonicalised sit under a tense-specific lemma. Each one
  // knows its own citation form, so index that too and they keep resolving.
  for (const [k, c] of marked) { const hp = cardHePast(c);
    if (hp && hp.ar) { const n = arNorm(hp.ar); if (!m.has(n)) m.set(n, k); } }
  // And under the citation form its paradigm gives it TODAY, which is not always the one it was
  // filed under: Hebrew verbs used to bank as the 3ms past and now bank as the infinitive, so a
  // card saved as כָּתַב has to be findable from לִכְתּוֹב or the next tap opens a second card on
  // a second schedule. Looking it up beats migrating: nothing is rewritten, and the existing
  // merge screen still offers to tidy the headword when you want it tidied.
  for (const [k, c] of marked) { const cite = verbCite(cardVerb(c));
    if (cite && cite.ar) { const n = arNorm(cite.ar); if (!m.has(n)) m.set(n, k); } }
  return (_deckNormIx = m);
}
const deckKeyFor = lemma => marked.has(lemma) ? lemma
  : (deckNormIndex().get(arNorm(lemma)) || lemma);
const inDeck = lemma => marked.has(deckKeyFor(lemma));
// For a word RECORD we can do better than the string: run it through the paradigm first, so a
// present-tense token finds the card filed under the past.
const deckKeyForWord = w => deckKeyFor((w && (verbPast(w) || {}).ar) || (w && w.lemma) || '');
const inDeckWord = w => marked.has(deckKeyForWord(w));

const save = () => { _deckNormIx = null;
  try { localStorage.setItem(KEY, JSON.stringify([...marked])); } catch (e) {} };

let decks = [];
try { decks = JSON.parse(localStorage.getItem(DKEY) || 'null') || []; } catch (e) {}
if (!decks.length) decks = [{id: 'default', name: 'My words', created: now()}];
const saveDecks = () => { try { localStorage.setItem(DKEY, JSON.stringify(decks)); } catch (e) {} };
const deckName = id => (decks.find(d => d.id === id) || {}).name || 'My words';
// The deck new cards drop into (remembered; the deck view can change it).
const AKEY = LKEY('activedeck.v1');
const activeDeck = () => { const id = localStorage.getItem(AKEY);
  return decks.some(d => d.id === id) ? id : 'default'; };
const setActiveDeck = id => { try { localStorage.setItem(AKEY, id); } catch (e) {} };

// Fresh SM-2 state for a new card (due immediately, in the learning phase).
function srsInit(c) {
  return {deck: 'default', ...c, ease: 2.5, interval: 0, due: now(), reps: 0, lapses: 0,
          lapses_: 0, created: c.created || now()};
}
// Anki-style SM-2 scheduler. g: 0 Again · 1 Hard · 2 Good · 3 Easy. Returns the next state.
function srsGrade(c, g) {
  let {ease = 2.5, interval = 0, reps = 0, lapses = 0} = c;
  if (g === 0) {                              // Again — relearn, back in ~10 min this session
    return {...c, ease: Math.max(1.3, ease - 0.2), interval: 0, reps: 0,
            lapses: lapses + 1, due: now() + 6e5};
  }
  reps += 1;
  if (g === 1) ease = Math.max(1.3, ease - 0.15);
  if (g === 3) ease += 0.15;
  if (reps === 1)      interval = g === 3 ? 4 : 1;
  else if (reps === 2) interval = g === 1 ? 3 : 6;
  else                 interval = Math.max(interval + 1,
                          Math.round(interval * (g === 1 ? 1.2 : g === 3 ? ease * 1.3 : ease)));
  return {...c, ease, interval, reps, lapses, due: now() + interval * DAY};
}
// What the four buttons would schedule, in human terms (shown under each grade button).
function srsPreview(c) {
  const fmt = ms => { const d = Math.round(ms / DAY);
    return ms < DAY ? '<10m' : d < 1 ? '1d' : d < 30 ? d + 'd' : Math.round(d / 30) + 'mo'; };
  return [0, 1, 2, 3].map(g => g === 0 ? '<10m' : fmt(srsGrade(c, g).due - now()));
}
const dueCards = () => [...marked.values()].filter(c => (c.due || 0) <= now());
const cardsInDeck = id => [...marked.values()].filter(c => (c.deck || 'default') === id);

// Audio clips are named by position (audio/<text>/s0.mp3), so re-voicing swaps the bytes but
// NOT the URL — and a browser that already played a clip keeps serving the old voice from its
// cache forever. au() stamps every audio URL with AUDIO_VERSION (emitted by build_app.py from
// the clip bytes), so any re-voice busts the cache automatically.
const AUDIO_V = window.AUDIO_VERSION || '';
const au = src => !src ? src : (AUDIO_V ? src + (src.includes('?') ? '&' : '?') + 'v=' + AUDIO_V : src);

// ---------- word audio: your Palestinian clip if we have one, else the browser's voice ----------
const VA = window.VOCAB_AUDIO || {};
let _wa = null;
function playWord(card) {
  // A phrase card carries its own clip when the span was a whole recorded sentence; otherwise
  // there is no Palestinian recording of that particular chunk and we fall back to the
  // browser voice, same as any word we never generated audio for.
  const clip = (card.kind === 'phrase' || card.kind === 'reaction' ? card.audio : null) || VA[card.lemma];
  if (clip) { try { (_wa = _wa || new Audio()).src = au(clip); _wa.playbackRate = SPEED;
                    _wa.play().catch(() => speakWord(card)); return; } catch (e) {} }
  speakWord(card);
}
function speakWord(card) {                    // browser SpeechSynthesis fallback (generic Arabic)
  if (!window.speechSynthesis) return;
  const u = new SpeechSynthesisUtterance(card.vocalized || card.lemma || '');
  u.lang = LANG.tts.lang; u.rate = Math.min(1, SPEED);
  const v = speechSynthesis.getVoices().find(v => LANG.tts.voiceRe.test(v.lang));
  if (v) u.voice = v;
  speechSynthesis.cancel(); speechSynthesis.speak(u);
}

// Playback speed. Slow is the single most useful setting for dialect — a Palestinian
// sentence at full pace is a wall; at 0.5x you can actually pick the words apart. Kept
// in its own localStorage key so it persists across sessions like the marked list.
// How you like to READ: vowels on, English on, marked words highlighted. Global for the same
// reason the playback speed is -- it is a property of the reader, not of a language -- and
// PERSISTED because it was not, and reset to "off" on every text. Toggling the English back on
// for each of a book's ten chapters is not a setting, it is a chore.
const RKEY = 'alp.read.v1';
const readPrefs = () => Object.assign({voc: true, en: false, mk: true},
                                      _pj(localStorage.getItem(RKEY)) || {});
const setReadPref = (k, v) => { const p = readPrefs(); p[k] = v;
  try { localStorage.setItem(RKEY, JSON.stringify(p)); } catch (e) {} };

const SKEY = 'alp.speed.v1';        // global on purpose: a playback speed, not a language
let SPEED = parseFloat(localStorage.getItem(SKEY)) || 1;
const setSpeed = v => { SPEED = v; try { localStorage.setItem(SKEY, String(v)); } catch (e) {} };
// One list, used by every speed control — the inline players and the guided-shadow view had
// their own copies and would drift apart. 0.75 is the useful middle rung: 0.5 is for picking
// a sentence apart word by word, 0.9 is "almost native", and the gap between them was too big
// to shadow comfortably.
const SPEEDS = [[0.5, '0.5×'], [0.75, '0.75×'], [0.9, '0.9×'], [1, '1×']];

// ---------- one real audio engine, many inline players ----------
// A single <audio> is reused for every line. Only one clip is ever audible; hitting play
// on a new line re-points this element and resets the previous line's transport. The
// per-line player UI (play/pause, scrubber, speed) binds to whichever line is active.
const A = new Audio();
A.preservesPitch = true; A.mozPreservesPitch = true; A.webkitPreservesPitch = true;
let activeSrc = null;

const fmt = t => (isFinite(t) ? Math.floor(t/60) + ':' + String(Math.floor(t%60)).padStart(2,'0') : '0:00');

function activePlayer() {
  return activeSrc ? document.querySelector(`.player[data-src="${cssq(activeSrc)}"]`) : null;
}
function cssq(s) { return String(s).replace(/["\\]/g, '\\$&'); }

function resetPlayer(pl) {
  if (!pl) return;
  pl.classList.remove('playing');
  const seek = pl.querySelector('.seek'); if (seek) { seek.value = 0; seek.style.setProperty('--fill','0%'); }
  const cur = pl.querySelector('.t-cur'); if (cur) cur.textContent = '0:00';
}

function playSrc(pl) {
  paraStop();                             // an inline line and the paragraph never play at once
  const src = pl.dataset.src;
  if (activeSrc !== src) {
    resetPlayer(activePlayer());          // hand the audio over from the old line
    activeSrc = src;
    A.src = src;
  }
  A.playbackRate = SPEED;
  A.play().catch(() => {});
  pl.classList.add('playing');
}
function toggleSrc(pl) {
  if (activeSrc === pl.dataset.src && !A.paused) { A.pause(); pl.classList.remove('playing'); }
  else playSrc(pl);
}

A.addEventListener('timeupdate', () => {
  const pl = activePlayer(); if (!pl) return;
  const pct = A.duration ? (A.currentTime / A.duration * 100) : 0;
  const seek = pl.querySelector('.seek');
  if (seek && document.activeElement !== seek) {   // don't fight a finger that's dragging
    seek.value = pct; seek.style.setProperty('--fill', pct + '%');
  }
  const cur = pl.querySelector('.t-cur'); if (cur) cur.textContent = fmt(A.currentTime);
});
A.addEventListener('loadedmetadata', () => {
  const pl = activePlayer(); if (!pl) return;
  const dur = pl.querySelector('.t-dur'); if (dur) dur.textContent = fmt(A.duration);
});
A.addEventListener('ended', () => { const pl = activePlayer(); resetPlayer(pl); });
A.addEventListener('pause', () => { const pl = activePlayer(); if (pl) pl.classList.remove('playing'); });

// Called from the delegated input handler when a scrubber is dragged.
function seekTo(pl, pct) {
  if (activeSrc !== pl.dataset.src) { activeSrc = pl.dataset.src; A.src = pl.dataset.src; }
  const set = () => { A.currentTime = (pct/100) * (A.duration || 0);
                      pl.querySelector('.seek').style.setProperty('--fill', pct + '%'); };
  if (A.duration) set(); else A.addEventListener('loadedmetadata', set, {once:true});
}

// Change speed everywhere; apply live if something is playing. Persisted (SKEY).
function applySpeed(v, pl) {
  setSpeed(v);
  A.playbackRate = v;
  PA.playbackRate = v;
  document.querySelectorAll('.pspd .sb').forEach(b =>
    b.setAttribute('aria-pressed', String(parseFloat(b.dataset.spd) === v)));
}

// The inline player component — one per line. LTR so the scrubber fills left→right even
// though the Arabic around it is RTL. Disabled lines show a plain note instead.
function player(src) {
  if (!src) return `<span class="noaud">no audio yet</span>`;
  return `<div class="player" data-src="${esc(au(src))}" dir="ltr">
      <button class="pp" aria-label="Play / pause"></button>
      <span class="t-cur">0:00</span>
      <input class="seek" type="range" min="0" max="100" value="0" step="0.5"
             aria-label="Seek" style="--fill:0%">
      <span class="t-dur">0:00</span>
      <div class="pspd" role="group" aria-label="Speed">
        ${SPEEDS.map(([v,t]) =>
          `<button class="sb" data-spd="${v}" aria-pressed="${SPEED===v}">${t}</button>`).join('')}
      </div>
    </div>`;
}

// ---------- paragraph player ----------
// The whole passage read as one continuous take. There is no single combined MP3 — the
// audio is per-sentence — so this plays the sentence clips back-to-back behind one transport
// and presents them as a single timeline (cumulative time, one scrubber). It has its own
// <audio> (PA) so it never fights the per-line players, which keep the shared A element.
const PA = new Audio();
PA.preservesPitch = true; PA.mozPreservesPitch = true; PA.webkitPreservesPitch = true;
let PARA = null;   // {el, srcs:[url…], dur:[secs…], i}  — one paragraph player per reader

// Same component as player(), minus a data-src: it's driven by index, not by one clip.
function paraPlayer() {
  return `<div class="player para" data-para="1" dir="ltr">
      <button class="pp" aria-label="Play / pause the whole passage"></button>
      <span class="t-cur">0:00</span>
      <input class="seek" type="range" min="0" max="100" value="0" step="0.5"
             aria-label="Seek" style="--fill:0%">
      <span class="t-dur">0:00</span>
      <div class="pspd" role="group" aria-label="Speed">
        ${SPEEDS.map(([v,t]) =>
          `<button class="sb" data-spd="${v}" aria-pressed="${SPEED===v}">${t}</button>`).join('')}
      </div>
    </div>`;
}

function paraStop() { PA.pause(); if (PARA) PARA.el.classList.remove('playing'); }

// A view can hold more than one continuous player (a lesson unit with two conversations). Only
// one can be the active PARA, so each player's clips are registered against its element and the
// player takes over on first press — see the .pp handler.
const PARA_SRCS = new WeakMap();
const paraRegister = (el, srcs) => { if (el && srcs && srcs.length) PARA_SRCS.set(el, srcs); };

function paraSetup(el, srcs) {
  paraStop();
  paraRegister(el, srcs);
  PARA = { el, srcs, dur: srcs.map(() => 0), i: 0 };
  // Preload each clip's duration so the combined scrubber and total time are accurate from
  // the first play rather than only after a full listen-through.
  srcs.forEach((src, k) => { const a = new Audio(); a.preload = 'metadata';
    a.addEventListener('loadedmetadata', () => { if (PARA) { PARA.dur[k] = a.duration || 0; paraRecalc(); } });
    a.src = src; });
}
const paraTotal = () => PARA ? PARA.dur.reduce((x, y) => x + (isFinite(y) ? y : 0), 0) : 0;
function paraRecalc() { if (!PARA) return; const tot = paraTotal();
  const d = PARA.el.querySelector('.t-dur'); if (d && tot) d.textContent = fmt(tot); }

function paraPlayIdx() {
  resetPlayer(activePlayer()); A.pause(); activeSrc = null;   // take audio off the inline lines
  PA.src = PARA.srcs[PARA.i]; PA.playbackRate = SPEED;
  PA.play().catch(() => {});
  PARA.el.classList.add('playing');
}
function paraToggle() {
  if (!PARA || !PARA.srcs.length) return;
  if (!PA.paused) { PA.pause(); PARA.el.classList.remove('playing'); } else paraPlayIdx();
}
function paraReset() { if (!PARA) return; PARA.i = 0; PARA.el.classList.remove('playing');
  const sk = PARA.el.querySelector('.seek'); if (sk) { sk.value = 0; sk.style.setProperty('--fill', '0%'); }
  const c = PARA.el.querySelector('.t-cur'); if (c) c.textContent = '0:00'; }

PA.addEventListener('ended', () => {
  if (!PARA) return;
  PARA.dur[PARA.i] = PA.duration || PARA.dur[PARA.i]; paraRecalc();
  if (PARA.i < PARA.srcs.length - 1) {          // roll straight into the next sentence
    PARA.i++; PA.src = PARA.srcs[PARA.i]; PA.playbackRate = SPEED; PA.play().catch(() => {});
  } else paraReset();
});
PA.addEventListener('timeupdate', () => {
  if (!PARA) return;
  const before = PARA.dur.slice(0, PARA.i).reduce((x, y) => x + (isFinite(y) ? y : 0), 0);
  const elapsed = before + PA.currentTime, tot = paraTotal();
  const pct = tot > 0 ? elapsed / tot * 100
    : (PARA.i + (PA.duration ? PA.currentTime / PA.duration : 0)) / PARA.srcs.length * 100;
  const sk = PARA.el.querySelector('.seek');
  if (sk && document.activeElement !== sk) { sk.value = pct; sk.style.setProperty('--fill', pct + '%'); }
  const c = PARA.el.querySelector('.t-cur'); if (c) c.textContent = fmt(elapsed);
});
PA.addEventListener('loadedmetadata', () => {
  if (PARA) { PARA.dur[PARA.i] = PA.duration || PARA.dur[PARA.i]; paraRecalc(); } });
PA.addEventListener('pause', () => { if (PARA) PARA.el.classList.remove('playing'); });

// Map a scrubber percentage onto (sentence, offset-within-sentence) using the known durations.
function paraSeek(pct) {
  if (!PARA) return; const tot = paraTotal(); if (!tot) return;
  let target = pct / 100 * tot, acc = 0, k = 0;
  for (; k < PARA.srcs.length - 1; k++) { const d = PARA.dur[k] || 0; if (acc + d >= target) break; acc += d; }
  PARA.i = k; const within = Math.max(0, target - acc);
  const wasPlaying = !PA.paused;
  PA.src = PARA.srcs[k]; PA.playbackRate = SPEED;
  const go = () => { PA.currentTime = Math.min(within, PA.duration || within); if (wasPlaying || PARA.el.classList.contains('playing')) PA.play().catch(() => {}); };
  if (PA.readyState >= 1) go(); else PA.addEventListener('loadedmetadata', go, { once: true });
  const sk = PARA.el.querySelector('.seek'); if (sk) sk.style.setProperty('--fill', pct + '%');
}

const VOCSRC = {
  'lexicon:exact'              : 'straight from the lexicon',
  'derived:affix'              : 'lexicon stem + prefix rule',
  'derived:verb'               : 'lexicon stem — prefix vowel is our best call',
  'unvocalized:weak-final-verb': "not shown — we couldn't derive it honestly",
  'unvocalized:no-alignment'   : "not shown — couldn't match the dictionary form",
  'unvocalized:no-entry'       : 'not in the lexicon',
  // Hebrew: the lexicon points ktiv haser and the text is written ktiv male, so the vowels are
  // the lexicon's but the letters are the reader's -- עֲדַיִן's pointing on עדיין's spelling.
  'derived:ktiv'               : "lexicon vowels, on the text's own spelling",
  // Hebrew again, and the commonest of the lot: Ben-Yehuda's texts arrive pointed, so the vowels
  // on the page are the publisher's and no derivation of ours improves on them. These three were
  // missing and the card printed the raw key -- "source:pointed" -- to the reader.
  'source:pointed'             : 'the vowels printed in the text itself',
  'unvocalized:clitic'         : 'not shown — the lexicon points the word, not what is attached to it',
  'curated'                    : 'hand-written by us, not from the lexicon',
  'curated:stem'               : "not shown — hand-written entry, and the particle isn't pointed",
  'unvocalized:curated-with-clitic': 'not shown — name carries a prefix'
};
const LIB = window.LIBRARY || {texts: [], drills: []};

// ---------- loading data on demand ----------
// The app used to fetch 15.4 MB before it drew anything, and the home screen -- a list of
// section names and counts -- paid all of it. Measured, 97% of the library and 85% of the verbs
// is content you can only see by opening something: sentences and paradigms. So both datasets
// ship as an INDEX plus BODIES (pipeline/split.py), and the bodies arrive when asked for.
//
// <script> tags, not fetch(), for the reason everything else here is a <script> tag: on file://
// a fetch() of a sibling file is a CORS error, and this app is meant to work by double-click.
const _needing = {};
function needFile(name) {
  if (_needing[name]) return _needing[name];
  return (_needing[name] = new Promise((ok, no) => {
    const el = document.createElement('script');
    el.src = 'data/' + LANG.code + '/' + name + '.js';
    el.onload = ok;
    el.onerror = () => { delete _needing[name]; no(new Error(name + ' could not be loaded')); };
    document.head.appendChild(el);
  }));
}

// Sentences. One text is ~18 KB; all of them together are 6.9 MB. Both files write into the
// same window.CORPUS, so whichever path fed a text, the rest of the app cannot tell.
const textReady = id => !!(window.CORPUS && window.CORPUS[id]);
const needText = id => textReady(id) ? Promise.resolve() : needFile('text/' + id);
let _corpusAll = false;
const corpusReady = () => _corpusAll;
function needCorpus() {                    // the whole thing -- translator, placement, phrases
  return needFile('corpus').then(() => { _corpusAll = true; });
}

// The word lookup used to be a reason to download all of it. It no longer is: the index it built
// by walking 21,817 tokens is a DEDUPLICATION down to 5,748 records, and that is computed at
// build time now (pipeline/lexindex.py, checked key-for-key against the corpus walk by
// pipeline/verify_lexindex.py). 7.3 MB becomes 1.2 MB -- 1.1 MB becomes 312 KB over the wire.
//
// Either file can answer, so whichever is already here wins: a page that has the corpus for
// other reasons never fetches the index, and a page that only wants to look words up never
// fetches the corpus.
// Arabic's index is DERIVED from its corpus, so either file answers and whichever is already
// in memory wins. Hebrew's is a dictionary in its own right and the corpus is a separate thing
// entirely -- letting an empty corpus stand in for it meant the Hebrew lookup silently resolved
// nothing, which is how the translator came to read ספר as English.
const lexReady = () => !!window.LEXICON || (LANG.lex.source === 'corpus' && corpusReady());
const needLexicon = () => lexReady() ? Promise.resolve() : needFile('lexicon');
// `t.sentences` becomes a getter over that store. Same reasoning as `v.conj`: ten call sites
// walk `t.sentences`, and none of them has to learn that the sentences now arrive separately.
// It reads as an empty text until the body lands, which is what the existing `(t.sentences ||
// [])` guards already expect -- so a page that renders early renders thin rather than throwing.
LIB.texts.forEach(t => Object.defineProperty(t, 'sentences', {
  configurable: true, get: () => (window.CORPUS || {})[t.id] || []}));
LIB.drills.forEach(d => Object.defineProperty(d, 'items', {
  configurable: true, get: () => (window.CORPUS || {})[d.id] || []}));

// ---------- verbs ----------
// Sourced from Maknuune: root, gloss, the three principal parts (past / present / command)
// and their pronunciation are looked up, never generated. The Form (measure I–X) and the
// weak class are computed by pipeline/verbforms.py from the perfect form + root.
const VB = (window.VERBS && window.VERBS.verbs) || [];
// `conj` is a getter, not a field. That is what lets 2,459 paradigms -- 4.4 MB, and 85% of this
// dataset -- stay on disk until a table is actually opened, without touching any of the dozen
// places that read `v.conj`. `v.hasConj` ships in the index and answers "is there a paradigm"
// for the code that only needs to know that: the study plan's verb walk, the section count, the
// "conjugates" badge.
const CONJ_CHUNK = 256;                  // must match pipeline/split.py
const conjChunk = i => 'verbs-conj-' + String(Math.floor(i / CONJ_CHUNK)).padStart(2, '0');
const conjReady = i => !!(window.VCONJ && window.VCONJ[i]);
const needConj = i => conjReady(i) ? Promise.resolve() : needFile(conjChunk(i));
VB.forEach((v, i) => {
  v._i = i;                              // stable index for detail-view routing
  Object.defineProperty(v, 'conj', {configurable: true, get: () => (window.VCONJ || {})[i]});
});
// Every paradigm at once, for the two readers that genuinely need all of them.
const needAllConj = () => Promise.all(
  [...new Set(VB.filter(v => v.hasConj).map(v => conjChunk(v._i)))].map(needFile));
const FORM_ORDER = LANG.verb.classOrder;
// One honest line on what each measure tends to do. Patterns, not promises — a given verb
// can drift from its measure's core sense, so these orient rather than define.
const FORM_INFO  = LANG.verb.classInfo;
const WEAK_INFO  = LANG.verb.weakInfo;
const WEAK_ORDER = LANG.verb.weakOrder;
const byForm = f => VB.filter(v => v.form === f);
const irregular = VB.filter(v => WEAK_INFO[v.weak]);
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pretty = g => String(g || '').replace(/_/g, ' ').replace(/;/g, ' · ');

// ---------- Arabic keyboard ----------
// Half the app's typing fields want Arabic, and plenty of people learning Palestinian have no
// Arabic layout on their machine — they were stuck copy-pasting or just not using those fields.
// One shared panel serves every field: mark an input with kbdWrap() and it gets a ع toggle.
// The layout is the standard Arabic 101 one, so anyone who later installs a real keyboard has
// already learnt where the letters live. It is opt-in per use: pressing ع opens it, and while
// it is open it follows you between fields, but nothing else ever summons it. It used to
// remember being on and reappear at every focused field forever after, which is only what you
// want if the panel is the ONLY way you type Arabic.
// The iPhone Arabic layout, key for key: 11 / 11 / 9-plus-backspace, ١٢٣ and the harakat key on
// the bottom row. Anyone who already types Arabic on a phone knows exactly where everything is,
// and anyone who doesn't is learning the layout they'll meet everywhere else.
const KBD_LETTERS = LANG.kbd.letters;
const KBD_NUMS    = LANG.kbd.nums;
// iOS hides the alef and hamza variants behind press-and-hold rather than giving each a key.
// Same here — hold ا for أ إ آ, ل for the lam-alef ligatures, ّ for the full set of harakat.
const KBD_HOLD    = LANG.kbd.hold;
let _kbdEl = null;                                   // the field the panel is typing into
let _kbdPage = 'ar', _kbdHoldT = null, _kbdHeld = false;

// Wrap a field's HTML so it carries the toggle. `inline` puts the button beside the field
// instead of inside it (for the tutor's textarea row, where the field grows as you type).
function kbdWrap(inputHTML, id, inline) {
  const btn = `<button type="button" class="kbd-tog${inline ? ' inline' : ''}" id="kbdt-${id}"
     title="${esc(LANG.short)} keyboard" aria-label="${esc(LANG.short)} keyboard"
     onmousedown="event.preventDefault()" onclick="kbdToggle('${id}')">${LANG.kbd.toggle}</button>`;
  const rtl = /dir=["']rtl["']/.test(inputHTML) ? ' rtl' : '';
  return inline ? inputHTML + btn : `<div class="kbd-wrap${rtl}">${inputHTML}${btn}</div>`;
}
function kbdToggle(id) {
  const el = $(id); if (!el) return;
  if (_kbdEl === el && !$('akbd').hidden) return kbdClose();
  kbdOpen(el);
}
function kbdOpen(el) {
  _kbdEl = el;
  let p = $('akbd');
  if (!p) {
    p = document.createElement('div');
    p.id = 'akbd'; p.hidden = true;
    document.body.appendChild(p);
    // Delegated, because the panel redraws whenever you switch to the ١٢٣ page.
    p.addEventListener('pointerdown', kbdDown);
    p.addEventListener('pointerup', kbdUp);
    p.addEventListener('pointercancel', kbdCancelHold);
  }
  _kbdPage = 'ar';
  kbdDraw();
  p.hidden = false;
  document.querySelectorAll('.kbd-tog').forEach(b => b.classList.toggle('on', b.id === 'kbdt-' + el.id));
  el.focus({preventScroll: true});
  // A panel pinned to the bottom would otherwise sit on top of the field it types into, and on a
  // short page there is nothing to scroll. Grow the page by the panel's height first, then move
  // the field clear of it.
  document.documentElement.style.setProperty('--kbdh', p.offsetHeight + 'px');
  const r = el.getBoundingClientRect(), top = p.getBoundingClientRect().top;
  if (r.bottom > top - 10) window.scrollTo(0, window.scrollY + (r.bottom - top) + 18);
}
function kbdDraw() {
  const p = $('akbd'); if (!p) return;
  const rows = _kbdPage === 'ar' ? KBD_LETTERS : KBD_NUMS;
  const k = ch => `<button class="akbd-k${KBD_HOLD[ch] ? ' more' : ''}" data-k="${ch}">${ch}</button>`;
  p.innerHTML = `<div class="akbd-in">
      <div class="akbd-hd"><span>${esc(LANG.short)} keyboard</span>
        <button class="akbd-x" data-a="hide">Hide</button></div>
      ${rows.map((r, i) => `<div class="akbd-r">${r.map(k).join('')}${
        i === rows.length - 1 ? `<button class="akbd-k fn" data-a="back">⌫</button>` : ''}</div>`).join('')}
      <div class="akbd-r">
        <button class="akbd-k fn" data-a="page">${_kbdPage === 'ar' ? LANG.kbd.numsLabel : LANG.kbd.lettersLabel}</button>
        <button class="akbd-k wide" data-k=" ">space</button>
        ${_kbdPage === 'ar' && LANG.kbd.diacritic
          ? `<button class="akbd-k fn more" data-k="${LANG.kbd.diacritic}">${LANG.kbd.diacriticLabel}</button>` : ''}
      </div></div>`;
}
// Press-and-hold opens the variants; a normal tap types the key itself. Everything runs off
// pointer events so one code path covers finger, mouse and trackpad.
function kbdDown(e) {
  const b = e.target.closest('[data-k],[data-a]');
  kbdPopClose();
  if (!b) return;
  e.preventDefault();                                  // never let the field lose the caret
  _kbdHeld = false;
  const v = KBD_HOLD[b.dataset.k];
  if (v) _kbdHoldT = setTimeout(() => { _kbdHoldT = null; _kbdHeld = true; kbdPop(b, v); }, 380);
}
function kbdUp(e) {
  const b = e.target.closest('[data-k],[data-a]');
  kbdCancelHold();
  if (!b || _kbdHeld) { _kbdHeld = false; return; }
  e.preventDefault();
  if (b.dataset.a === 'hide') return kbdClose();
  if (b.dataset.a === 'back') return kbdBack();
  if (b.dataset.a === 'page') { _kbdPage = _kbdPage === 'ar' ? 'num' : 'ar'; return kbdDraw(); }
  kbdIns(b.dataset.k);
}
function kbdCancelHold() { if (_kbdHoldT) { clearTimeout(_kbdHoldT); _kbdHoldT = null; } }
function kbdPop(btn, variants) {
  kbdPopClose();
  const pop = document.createElement('div');
  pop.className = 'akbd-pop';
  pop.innerHTML = variants.map(v => `<button class="akbd-k" data-v="${v}">${v}</button>`).join('');
  pop.addEventListener('pointerdown', e => {
    const b = e.target.closest('[data-v]'); if (!b) return;
    e.preventDefault(); e.stopPropagation();
    kbdIns(b.dataset.v); kbdPopClose();
  });
  $('akbd').appendChild(pop);
  const r = btn.getBoundingClientRect(), pr = $('akbd').getBoundingClientRect();
  pop.style.top = (r.top - pr.top - pop.offsetHeight - 6) + 'px';
  let left = r.left - pr.left + r.width / 2 - pop.offsetWidth / 2;
  pop.style.left = Math.max(4, Math.min(left, pr.width - pop.offsetWidth - 4)) + 'px';
}
function kbdPopClose() { const q = document.querySelector('.akbd-pop'); if (q) q.remove(); }
// `sticky` = the user asked for it to go away, so don't reopen on the next field.
function kbdClose() {
  kbdCancelHold(); kbdPopClose();
  const p = $('akbd'); if (p) p.hidden = true;
  document.documentElement.style.removeProperty('--kbdh');
  document.querySelectorAll('.kbd-tog').forEach(b => b.classList.remove('on'));
  _kbdEl = null;
}
// Insert at the caret and tell the app: the search fields filter on `input`, so a key press
// has to look exactly like a typed character or nothing would update.
function kbdIns(ch) {
  const el = _kbdEl; if (!el) return;
  const a = el.selectionStart, b = el.selectionEnd;
  if (a == null) el.value += ch;
  else { el.value = el.value.slice(0, a) + ch + el.value.slice(b); const c = a + ch.length; el.setSelectionRange(c, c); }
  el.dispatchEvent(new Event('input', {bubbles: true}));
  el.focus({preventScroll: true});
}
function kbdBack() {
  const el = _kbdEl; if (!el) return;
  const a = el.selectionStart, b = el.selectionEnd;
  if (a == null) el.value = el.value.slice(0, -1);
  else if (a !== b) { el.value = el.value.slice(0, a) + el.value.slice(b); el.setSelectionRange(a, a); }
  else if (a > 0) { el.value = el.value.slice(0, a - 1) + el.value.slice(a); el.setSelectionRange(a - 1, a - 1); }
  el.dispatchEvent(new Event('input', {bubbles: true}));
  el.focus({preventScroll: true});
}
// Follow the caret between fields — the exercise list has several inputs on one screen — but
// only when the panel is ALREADY open. Focus never summons it; pressing ع is the only thing
// that does.
document.addEventListener('focusin', e => {
  const el = e.target;
  if (!el || !el.id || !document.getElementById('kbdt-' + el.id)) return;
  if (_kbdEl === el) return;
  if (_kbdEl && !$('akbd').hidden) kbdOpen(el);
});

// ---------- sections (the menu) ----------
// Order here is the order in the menu bar. `route` is the hash; `ready:false` sections
// render an honest "coming soon" instead of pretending to have content.
// Inline SVG icons — no external requests, works offline. 24-grid, currentColor stroke.
const ICON = {
  home:    '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
  news:    '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h10M7 16h6"/>',
  verbs:   '<path d="M13 2 4 14h6l-1 8 9-12h-6z"/>',
  vocab:   '<rect x="4" y="3" width="14" height="18" rx="2"/><path d="M8 3v18"/><path d="M11 8h4M11 12h4"/>',
  spk:     '<path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16 8a5 5 0 0 1 0 8"/>',
  grammar: '<path d="M5 4h13a1 1 0 0 1 1 1v15H6a1 1 0 0 1-1-1z"/><path d="M5 17h14"/>',
  stories: '<path d="M12 7c-2-1.4-5-1.4-8 0v12c3-1.4 6-1.4 8 0 2-1.4 5-1.4 8 0V7c-3-1.4-6-1.4-8 0z"/><path d="M12 7v12"/>',
  plan:    '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/><path d="M8.5 14.5l2 2 4-4.5"/>',
  ext:     '<path d="M14 4h6v6"/><path d="M20 4l-8 8"/><path d="M18 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h5"/>',
  books:   '<path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M4 19a2 2 0 0 1 2-2h12"/>',
  bible:   '<path d="M5 4a2 2 0 0 1 2-2h11v18H7a2 2 0 0 0-2 2z"/><path d="M11.5 6.5v6M9 9h5"/>',
  video:   '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 9l5 3-5 3z"/>',
  react:   '<path d="M20 4H4a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h4v4l5-4h7a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1z"/><path d="M12 7.5v3.5M12 13.4v.2"/>',
  sound:   '<path d="M3 10v4M7 7v10M11 4v16M15 8v8M19 11v2"/>',
  table:   '<circle cx="14" cy="12" r="6"/><circle cx="14" cy="12" r="2.5"/><path d="M4 4v6a1.5 1.5 0 0 0 3 0V4M5.5 4v16"/>',
  user:    '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6.5 8-6.5s8 2.5 8 6.5"/>',
  translate: '<path d="M4 5h9M8.5 3v2c0 4-2.2 7-5.5 8.5"/><path d="M5 10c0 2 2.2 4 5.5 5"/><path d="M12.5 20l4.5-9 4.5 9M14.5 17h5"/>',
  tutor:   '<path d="M21 11.5a8 8 0 0 1-8 8H7l-4 3v-6.5a8 8 0 1 1 18-4.5z"/><path d="M9.3 9.4a2.8 2.8 0 0 1 5.3 1c0 1.8-2.7 2.1-2.7 3.9"/><path d="M11.9 17v.1"/>',
  ears:    '<path d="M4 14v-3a8 8 0 0 1 16 0v3"/><rect x="2" y="13" width="4" height="7" rx="1.6"/><rect x="18" y="13" width="4" height="7" rx="1.6"/>',
  lesson:  '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 3v18"/><path d="M11.5 8h5M11.5 12h5M11.5 16h3"/>',
};
const svg = n => `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"
  stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${ICON[n]}</svg>`;

// ---------- home artwork ----------
// The app ships as one folder with no external assets, so the homepage's "pictures" are inline
// SVG drawn in the theme's own variables: they recolor themselves in dark mode, weigh nothing,
// and carry no licence. Two pieces: a tatreez band (Palestinian cross-stitch — the diamond
// motif), and a Jerusalem skyline with the Dome of the Rock, drawn as a line engraving.
let _tzN = 0;
function tatreez() {
  const id = 'tz' + (_tzN++);                       // pattern ids are document-global
  return `<svg class="tz" height="16" aria-hidden="true"><defs>
    <pattern id="${id}" width="32" height="16" patternUnits="userSpaceOnUse">
      <rect x="12" y="4" width="8" height="8" transform="rotate(45 16 8)" fill="var(--rubric)"/>
      <rect x="14.6" y="6.6" width="2.8" height="2.8" transform="rotate(45 16 8)" fill="var(--paper)"/>
      <rect x="0" y="6.7" width="2.6" height="2.6" transform="rotate(45 1.3 8)" fill="var(--verdigris)"/>
      <rect x="29.4" y="6.7" width="2.6" height="2.6" transform="rotate(45 30.7 8)" fill="var(--verdigris)"/>
      <rect x="0" y="0" width="32" height="1.4" fill="var(--ochre)"/>
      <rect x="0" y="14.6" width="32" height="1.4" fill="var(--ochre)"/>
    </pattern></defs>
    <rect width="100%" height="16" fill="url(#${id})"/></svg>`;
}
// Jerusalem, looking at the Old City: hills, the wall, cypresses and olives, a minaret, and the
// Dome of the Rock. Strokes only, one accent fill on the dome — an engraving, not a postcard.
const HOME_SKYLINE = `<svg class="hm-sky" viewBox="0 0 1200 210" preserveAspectRatio="xMidYMax meet"
   fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62">
    <path d="M0 190 Q180 148 380 166 T760 158 T1200 172" opacity=".45"/>
    <path d="M0 208 Q240 180 520 194 T1200 196"/>
    <circle cx="1010" cy="52" r="24" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
    <path d="M120 196v-32h34v32M124 164v-7h6v7M137 164v-7h6v7M150 164v-7h6v7"/>
    <path d="M690 196v-26h30v26M694 170v-6h5v6M705 170v-6h5v6M716 170v-6h5v6"/>
    <path d="M580 196V86m22 110V86M580 92h22M580 86l11-12 11 12M585 120h12M584 146h14"/>
    <path d="M591 62l0-10m0 0a4 4 0 1 1 3-7" stroke="var(--ochre)"/>
    <path d="M575 120h32l-4 8h-24z" opacity=".8"/>
    <path d="M244 196v-60l26-14v74M250 148v-10h7v10M262 148v-10h7v10"/>
    <path d="M840 196v-44h56v44M848 176v-24a8 8 0 0 1 16 0v24M872 176v-24a8 8 0 0 1 16 0v24"/>
    <path d="M950 196v-30h40v30M958 186v-20a6 6 0 0 1 12 0v20"/>
  </g>
  <g>
    <path d="M292 196v-58h136v58" stroke="var(--ink-soft)" stroke-width="1.8"/>
    <path d="M300 138l60-26 68 26" stroke="var(--ink-soft)" stroke-width="1.8"/>
    <path d="M316 196v-26a9 9 0 0 1 18 0v26M356 196v-26a9 9 0 0 1 18 0v26M396 196v-26a9 9 0 0 1 18 0v26"
       stroke="var(--ink-soft)" stroke-width="1.6" opacity=".8"/>
    <path d="M312 112 C312 74 344 52 360 46 C376 52 408 74 408 112"
       fill="var(--ochre-wash)" stroke="var(--ochre)" stroke-width="2.2"/>
    <path d="M360 46V30m0 0a5 5 0 1 1 4-8" stroke="var(--ochre)" stroke-width="2"/>
    <path d="M322 112c8-4 68-4 76 0" stroke="var(--ochre)" stroke-width="1.6" opacity=".7"/>
  </g>
  <g fill="var(--verdigris)" opacity=".5" stroke="none">
    <path d="M96 196c0-30 10-52 14-58 4 6 14 28 14 58z"/>
    <path d="M198 196c0-24 8-42 11-47 3 5 11 23 11 47z"/>
    <path d="M478 196c0-34 11-58 15-64 4 6 15 30 15 64z"/>
    <path d="M772 196c0-26 8-45 12-50 4 5 12 24 12 50z"/>
    <path d="M1084 196c0-22 7-38 10-43 3 5 10 21 10 43z"/>
    <path d="M1150 178c-10-2-16-10-16-18 6-4 16-4 22 2 6-6 16-6 22-2 0 8-6 16-16 18v18h-12z" opacity=".9"/>
  </g>
  <path d="M0 196h1200" stroke="var(--ink-soft)" stroke-width="1.8" opacity=".7"/>
</svg>`;

// The menu grew section by section into a long flat list. It's organized now into a few
// intent-groups — Practice (the skill drills the Plan schedules), Read & Listen (graded input),
// and Ask (look-things-up tools) — with My Plan pinned on top as the spine and Account at the
// bottom. `group` drives both the sidebar and the home tiles; order within a group is the
// learning arc (sounds → reactions → grammar → verbs → vocab, etc.).
const GROUPS = [
  {id: 'practice', label: 'Practice',      blurb: 'The daily drills your plan walks you through.'},
  {id: 'input',    label: 'Read & Listen', blurb: `Graded ${LANG.name} to read and hear.`},
  {id: 'ask',      label: 'Ask & look up', blurb: 'Answers and lookups, on demand.'},
];
// ---------- the section registry -----------------------------------------------------------
// One definition per section, and it is the ONLY one. Before this, four places had to agree
// about the same seventeen things -- a SECTIONS array, a 22-branch ternary for the status line,
// a SEC_ART map, and a 17-arm `if` ladder inside route(). Adding a section meant editing all
// four and the compiler could not tell you when you missed one.
//
// These definitions are language-NEUTRAL. `view` and `status` are functions so they read live
// data at call time rather than at load time; the art and the labels come from the pack.
//
// `lex: 1` means "this section's pages are made of lexicon lookups" -- every Arabic word in a
// grammar lesson, a Bible verse or a dinner-table line is tappable, and that needs the 7.3 MB
// corpus. Those sections prefetch it in the background while the page they asked for renders
// from the index. It is declared here, per section, rather than guessed from how much Arabic
// happens to be on the page: the home screen shows a phrase of the day, which is four tappable
// words, and a guess would have made the lightest page in the app pull the heaviest file.
const SECTION_DEFS = {
  plan: {icon: 'plan', label: 'My Plan', group: 'plan',
    view: (id, arg) => planSection(id, arg),
    status: () => planCfg()
      ? 'Phase ' + (curPhaseIndex(planCfg()) + 1) + ' · ' + esc(CUR.phases[curPhaseIndex(planCfg())].name)
      : 'Build your study plan'},
  lessons: {icon: 'lesson', lex: 1, label: 'Lessons', group: 'practice',
    view: id => lessonsSection(id),
    status: () => (LSN.units || []).length
      ? (LSN.units || []).length + ' units, from native materials' : 'Teaching units'},
  sounds: {icon: 'sound', lex: 1, label: 'Sounds', group: 'practice',
    view: id => soundsSection(id),
    status: () => SND.lessons ? SND.lessons.length + ' sound contrasts to master'
                              : 'Get the ear & mouth right'},
  reactions: {icon: 'react', lex: 1, label: 'Reactions', group: 'practice',
    view: id => reactionsSection(id),
    status: () => RX.items ? RX.items.length + ' quick replies, by feel' : 'Conversation reflexes'},
  grammar: {icon: 'grammar', lex: 1, label: 'Grammar Lessons', group: 'practice',
    view: id => grammarSection(id),
    status: () => GRAM.length + ' spoken structures'},
  verbs: {icon: 'verbs', label: 'Verbs', group: 'practice',
    view: id => verbsSection(id),
    status: () => VB.length + ' verbs, by ' + LANG.verb.classNoun},
  vocab: {icon: 'vocab', lex: 1, label: 'Vocabulary', group: 'practice',
    view: (id, arg) => vocabSection(id, arg),
    status: () => marked.size ? dueCards().length + ' due · ' + marked.size + ' cards'
                              : 'Your flashcards'},
  news: {icon: 'news', label: "Today's News", group: 'input',
    view: () => newsSection(),
    status: () => LIB.texts.filter(t => t.kind === 'news').length + ' articles'},
  stories: {icon: 'stories', label: 'Short Stories', group: 'input',
    view: id => storiesSection(id),
    status: () => LIB.texts.filter(t => t.kind === 'story').length + ' stories, 3 levels'},
  table: {icon: 'table', lex: 1, label: 'The Dinner Table', group: 'input',
    view: id => tableSection(id),
    status: () => TBL.dialogues ? TBL.dialogues.length + ' conversations · follow the room'
                                : 'The north-star skill'},
  books: {icon: 'books', label: 'Books', group: 'input',
    view: (id, arg) => booksSection(id, arg),
    status: () => booksList().length
      ? booksList().length + ' book' + (booksList().length === 1 ? '' : 's') + ' to read'
      : 'Full graded readers'},
  videos: {icon: 'video', label: 'Videos', group: 'input',
    view: id => videosSection(id),
    status: () => VIDEOS.length + ' playlists · Shami Speaker'},
  listening: {icon: 'ears', label: 'Listening', group: 'input',
    view: id => listeningSection(id),
    status: () => LISTEN.length + ' episodes · native speed, with transcripts'},
  bible: {icon: 'bible', lex: 1, label: 'Bible', group: 'input',
    view: (id, arg) => bibleSection(id, arg),
    status: () => LANG.bibleBlurb},
  tutor: {icon: 'tutor', label: 'Ask a Tutor', group: 'ask',
    view: id => tutorSection(id),
    status: () => tutorKey() ? 'Ask anything, in dialect' : 'Add your key to ask questions'},
  translate: {icon: 'translate', label: 'Translate', group: 'ask',
    view: () => translateSection(),
    status: () => 'Words & phrases in context'},
  account: {icon: 'user', label: 'Account', group: 'you',
    view: () => accountSection(),
    status: () => _user ? esc(_user.email) : 'Sign in to sync your progress'},
};

// The pack declares WHICH sections it has and IN WHAT ORDER, because order is pedagogy and it
// differs between languages. A pack naming a section that does not exist is a typo, and it
// should say so at boot rather than quietly render one tab fewer.
const SECTIONS = LANG.sections.map(id => {
  const d = SECTION_DEFS[id];
  if (!d) throw new Error('language pack "' + LANG.code + '" lists unknown section "' + id + '"');
  return Object.assign({route: id, ready: true}, d, (LANG.sectionLabels || {})[id] || {},
                       {art: LANG.art[id] || null});
});
const SEC_BY_ROUTE = new Map(SECTIONS.map(s => [s.route, s]));

// Each section already declares an `icon` and never used it on the home tiles — sixteen
// identical outlined rectangles. The icon plus a per-group tint turns the wall into a set.
const GROUP_COLOR = {practice: 'var(--verdigris)', input: 'var(--ochre)',
                     ask: 'var(--rubric)', you: 'var(--muted)'};

function secHero(sec) {
  const art = sec && sec.art;
  if (!sec || !art) return '';
  const gc = GROUP_COLOR[sec.group] || 'var(--verdigris)';
  // Every scene is somewhere real, so it says where in the corner — the Arabic name too, since
  // half the point of the app is that you can read it. <bdi> keeps the RTL name from dragging
  // the punctuation around it to the wrong side.
  const cap = art.place ? `<div class="sh-cap"><b>${esc(art.place)}</b> <bdi class="ar"
      dir="rtl">${esc(art.placeAr)}</bdi> · ${esc(art.what)}</div>` : '';
  // Wordmark first, scene beneath — the same order as the home page's masthead and skyband.
  return `<div class="sh" style="--gc:${gc}">
      <div class="sh-in">
        <div class="sh-ar" dir="rtl">${esc(art.ar)}</div>
        <div class="sh-en">${esc(sec.label)}</div>
      </div>
      <div class="sh-band"><svg class="sh-sky" viewBox="0 0 1200 210"
        preserveAspectRatio="xMidYMax meet" fill="none" stroke-linecap="round"
        stroke-linejoin="round" aria-hidden="true">${art.art()}</svg></div>${cap}
    </div>`;
}

function homeTile(sec) {
  return `<button class="tile${sec.ready ? '' : ' soon'}" style="--gc:${GROUP_COLOR[sec.group] || 'var(--verdigris)'}"
      onclick="location.hash='/${sec.route}'">
      <div class="tile-h"><span class="tile-i">${svg(sec.icon)}</span>
        <span class="tile-t">${esc(sec.label)}</span></div>
      <div class="tile-s">${sec.status()}</div></button>`;
}

// Short-story reading levels, in order. label shown on tiles; blurb sets expectations.
// Which nav tab a text belongs to. Was a nested ternary that handled news and stories and left
// book chapters lighting nothing at all — you were inside Books with Books unlit.
const SEC_FOR_KIND = {news: 'news', story: 'stories', 'book-chapter': 'books'};
// What a tier IS differs by language, because the gate that admits a story differs: Arabic's
// top tier is dialogue and idiom, Hebrew's is two clauses a sentence and vocabulary you have
// not met. The pack says; a blurb promising dialogue over a set that has none is worse than no
// blurb at all.
const STORY_LEVELS = LANG.storyLevels;
const storiesAt = lvl => LIB.texts.filter(t => t.kind === 'story' && t.level === lvl)
                                  .sort((a, b) => (a.id).localeCompare(b.id));

function renderNav(active){
  const item = (route, icon, label, ready) =>
    `<button class="navb${route===active?' on':''}" onclick="location.hash='/${route==='home'?'':route}'">
       ${svg(icon)}<span>${esc(label)}</span>${ready===false?'<em>soon</em>':''}</button>`;
  const sec = s => item(s.route, s.icon, s.label, s.ready);
  const inGroup = g => SECTIONS.filter(s => s.group === g);
  let h = item('home', 'home', 'Home', true) + `<div class="side-sep"></div>` +
    inGroup('plan').map(sec).join('');
  GROUPS.forEach(g => {
    const items = inGroup(g.id); if (!items.length) return;
    h += `<div class="side-group">${esc(g.label)}</div>` + items.map(sec).join('');
  });
  h += `<div class="side-sep"></div>` + inGroup('you').map(sec).join('');
  $('nav').innerHTML = h;
}

// ---------- routing (hash so Back works, and it survives a reload) ----------
function route() {
  if (typeof closeSide === 'function') closeSide();
  if (typeof askHide === 'function') askHide();
  if (typeof askPopClose === 'function') askPopClose();   // the page under it is being replaced
  // The section renders synchronously below; repaint arLive()'s words once it has.
  setTimeout(() => { if (typeof lexPaint === 'function') lexPaint(); }, 0);
  if (typeof kbdClose === 'function') kbdClose();          // its target is about to be re-rendered
  if (typeof spkStop === 'function') spkStop();           // stop any running speaking timer
  if (typeof gsStop === 'function') { gsStop(); _gs = null; }   // stop guided-shadow audio
  if (typeof paraStop === 'function') paraStop();               // stop the paragraph player
  const cw = $('cw'); if (cw) cw.classList.remove('on');   // close the word sheet on nav
  const h = location.hash.slice(1) || '/';
  const [, kind, id, arg] = h.split('/');

  // Everything below this line renders synchronously, the way it always has. What changed is
  // that the data it renders may not be here yet -- so the route says what it needs, and if any
  // of it is missing the render is deferred and re-entered once. One gate, rather than an await
  // threaded through twenty view functions.
  const want = [];
  if ((kind === 'text' || kind === 'speak') && id && !textReady(id)) want.push(needText(id));
  if (kind === 'drill' && id && !textReady(id)) want.push(needText(id));
  if (kind === 'verb' && VB[+id] && VB[+id].hasConj && !conjReady(+id)) want.push(needConj(+id));
  // Translate would be WRONG rather than merely thin without the whole corpus -- searching a
  // partial index quietly returns "no results" for words that are there. It is the one page
  // whose entire job is to read across every text, so it waits for them. Everywhere else
  // degrades gracefully and repaints when the lexicon arrives -- see lexIndex(). (The placement
  // test needs it too, and asks for it in assessStart, where there is an intro screen to cover
  // the wait.)
  if (kind === 'translate' && !corpusReady()) want.push(needCorpus());
  // Sections declared `lex` are made of lookups, so they fetch the word index -- but in the
  // BACKGROUND, not in `want`. The page draws immediately and lexPaint() makes its words live a
  // moment later, which beats a spinner over content that is already here.
  if (!lexReady() && (SECTION_DEFS[kind] || {}).lex) needLexicon().then(lexRefresh, () => {});
  if (want.length) {
    routeLoading();
    Promise.all(want).then(route, e => routeFailed(e));
    return;
  }

  // A text/drill belongs to whichever section it came from; light that tab when we can.
  if (kind === 'text')  { const t = LIB.texts.find(x => x.id === id);
    if (t) { renderNav(SEC_FOR_KIND[t.kind] || null); return reader(t); } }
  if (kind === 'speak') { const t = LIB.texts.find(x => x.id === id);
    if (t) { renderNav(SEC_FOR_KIND[t.kind] || null); return speakView(t); } }
  if (kind === 'drill') { const d = LIB.drills.find(x => x.id === id);
    if (d) { renderNav(null); return drill(d); } }
  if (kind === 'verb') { renderNav('verbs'); return verbDetail(id); }
  const sec = SEC_BY_ROUTE.get(kind);
  if (sec) {
    renderNav(sec.route);
    // The hero belongs to a section's LANDING page, not to a story, a verb or a chapter --
    // those have their own headers and their own job.
    if (!id) setTimeout(() => { const v = $('view');
      if (v && !v.querySelector('.sh')) v.insertAdjacentHTML('afterbegin', secHero(sec)); }, 0);
    return sec.view(id, arg);
  }
  // The section exists, but not in the language you are reading. Saying so beats bouncing the
  // learner silently to the home page and letting them wonder where the link went.
  if (SECTION_DEFS[kind]) return sectionElsewhere(kind);
  renderNav('home');
  home();
}
addEventListener('hashchange', route);

// Only shown while a body is in flight, and only when there is one to wait for -- a page whose
// data is already in memory never sees it.
function routeLoading() {
  $('back').hidden = false;
  $('view').innerHTML = '<div class="empty"><div class="empty-t">Loading…</div></div>';
}
function routeFailed(e) {
  $('view').innerHTML = `<div class="empty"><div class="empty-t">That didn’t load</div>
    <p>${esc((e && e.message) || 'Something is missing.')} You may be offline, or this may be an
    old link to something that has since been removed.</p>
    <div class="ctl" style="justify-content:center">
      <button class="tog" onclick="location.hash='/'">Back to home</button></div></div>`;
}

// ---------- home ----------
// "Today" is Israel civil time everywhere — the plan resets and the news freshens at midnight
// Jerusalem, regardless of the device's timezone (the daily news is written on Israel time too).
// en-CA formats as YYYY-MM-DD; a fixed timeZone makes the day boundary Israel-local.
const _ILDATE = (() => { try { return new Intl.DateTimeFormat('en-CA', {timeZone: 'Asia/Jerusalem',
  year: 'numeric', month: '2-digit', day: '2-digit'}); } catch (e) { return null; } })();
function todayISO(){
  if (_ILDATE) return _ILDATE.format(new Date());       // e.g. "2026-08-10"
  const d = new Date(); return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function home(){
  $('back').hidden = true;
  // The app bar carries the PRODUCT on the home screen; which language you are in is said by
  // the flags beside it, the sidebar under it and the masthead below that.
  $('title').textContent = ALP.name;
  const today = todayISO();
  const news = LIB.texts.filter(t => t.kind === 'news')
                        .sort((a, b) => (b.date || '').localeCompare(a.date || ''))[0];
  const fresh = news && news.date === today;
  const d = isoToDate(today);

  // ---- masthead: a broadsheet front page, in the language it teaches ----
  let h = `<div class="hm-mast">
      ${LANG.ornament()}
      <div class="hm-mast-in">
        <div class="hm-ed">Read it · Hear it · Say it</div>
        ${LANG.homeMasthead()}
      </div>
      <div class="hm-dl">
        <span>ISSUE ${esc(today)}</span>
        <span class="ar">${LANG.dateLine(d)}</span>
        <span>${esc(WD[d.getDay()]).toUpperCase()} · ${esc(MON[d.getMonth()]).toUpperCase()} ${d.getDate()}</span>
      </div>
    </div>`;

  // the Old City on the horizon; today's cards stand in front of it
  // The skyline is a place, and a place is a language's own. Arabic's is Jerusalem's Old City;
  // a pack with nothing to draw yet draws nothing, rather than borrowing the other's.
  if (LANG.skyline) h += `<div class="hm-skyband">${LANG.skyline()}</div>`;

  h += '<div class="hm-top">';

  // ---- the plan, as the one dominant card, carrying its phase colour ----
  const _pc = planCfg();
  if (_pc) {
    const day = getDay(_pc, today, dueCards().length);
    const doneMap = (planLog()[today] && planLog()[today].done) || {};
    const doneN = day.tasks.filter(t => t.id in doneMap).length;
    const pct = day.tasks.length ? Math.round(doneN / day.tasks.length * 100) : 0;
    const L = levelAt(day.phase.id);
    h += `<button class="hm-plan" style="--pc:${PHASE_COLOR[day.phase.id]}" onclick="location.hash='/plan'">
      <div class="hm-k">Today · Phase ${day.phase.id + 1} · ${esc(day.phase.name)}</div>
      <div class="hm-t">${day.rest ? 'Rest day'
        : doneN === day.tasks.length && day.tasks.length ? 'Done for today ✓'
        : day.tasks.length + ' task' + (day.tasks.length === 1 ? '' : 's') + ' today'}</div>
      <div class="hm-s">${day.rest
        ? 'Nothing scheduled — recovery is part of the plan.'
        : esc(day.phase.milestone || '')}</div>
      ${day.rest ? '' : `<div class="hm-bar"><i style="width:${Math.max(2, pct)}%"></i></div>`}
      <div class="hm-meta"><span>${doneN} of ${day.tasks.length} done</span>
        <span>${Math.round(day.totalMin / 60 * 10) / 10}h planned</span>
        <span>${esc(L.band)} · ${esc(L.cefr)}</span>
        ${planStreak() ? `<span>🔥 ${planStreak()}-day streak</span>` : ''}</div>
    </button>`;
  } else if (LANG.sections.includes('plan')) {
    // Only where there is a plan to build. A language whose content is still being written has
    // nothing to schedule, and inviting someone to build a study plan out of it would be an
    // invitation to an empty page.
    h += `<button class="hm-plan" onclick="location.hash='/plan/new'">
      <div class="hm-k">Start here</div>
      <div class="hm-t">Build your study plan</div>
      <div class="hm-s">Tell it when you can study and roughly where you are. It builds a daily,
        self-adjusting path — ${esc(LANG.planGoal)}.</div>
      <div class="hm-meta"><span>~${asMins()}-minute placement</span><span>${
        (CUR.phases || []).length} phases</span>
        <span>adjusts to your week</span></div>
    </button>`;
  }

  // ---- phrase of the day: real Arabic on the front page, and audible ----
  // Picked deterministically from the date, so it is the same phrase all day on every device and
  // changes at midnight without anything being stored. Reactions are the right well to draw on:
  // all 64 are lexicon-corroborated and all are voiced.
  const rx = (RX.items || []);
  if (rx.length) {
    const seed = [...today].reduce((a, c) => a * 31 + c.charCodeAt(0) >>> 0, 7);
    const it = rx[seed % rx.length];
    h += `<div class="hm-phrase">
      <div class="hm-k" style="color:var(--ochre)">Phrase of the day</div>
      <div class="hm-ph-ar">${arLive(it.ar)}</div>
      <div class="hm-ph-en">${esc(it.en)}</div>
      <div class="hm-ph-use">${esc(it.use || '')}</div>
      <div class="hm-ph-row">
        ${it.audio ? `<button class="tog go" onclick="sndPlay('${cssq(it.audio)}')">▶ Hear it</button>` : ''}
        <button class="tog" onclick="location.hash='/reactions'">More like this</button>
      </div></div>`;
  }
  h += '</div>';

  // ---- news: one scannable line, not a second hero competing with the plan ----
  // Only for a language that HAS a daily paper. "No news yet · Written fresh each morning" was
  // a promise Hebrew is not yet in a position to make.
  if (!LANG.sections.includes('news')) { /* no daily paper in this language yet */ }
  else if (fresh) {
    const lead = (news.sentences[0] || {}).en || news.title.en;
    h += `<button class="hm-news" onclick="location.hash='/text/${esc(news.id)}'">
      <span class="k">Today's news</span>
      <span class="t">${esc(lead)}</span>
      <span class="ar">${esc(news.title.ar)}</span>
      <span class="s">${news.sentences.length} sentences${news._audio ? ' · audio' : ''}</span>
    </button>`;
  } else {
    // A day behind is normal (the job runs at 05:00 Israel). A WEEK behind means the job is
    // broken — usually an expired ANTHROPIC_API_KEY or an empty balance — and the old wording
    // ("today's isn't in yet") hid that for a fortnight. Say the number out loud past 3 days.
    const staleDays = news ? Math.round((isoToDate(today) - isoToDate(news.date)) / 864e5) : 0;
    h += `<button class="hm-news${staleDays > 3 ? ' warn' : ''}" onclick="location.hash='/news'">
      <span class="k">Today's news</span>
      <span class="t">${!news ? 'No news yet'
        : staleDays > 3 ? staleDays + ' days behind — the morning job has stopped writing'
        : 'Latest is ' + esc(news.date)}</span>
      <span class="s">${!news ? 'Written fresh each morning.'
        : staleDays > 3 ? 'check the Anthropic key' : 'browse →'}</span>
    </button>`;
  }

  // The menu as tiles — grouped by intent (Practice · Read & Listen · Ask), so the growing set
  // of sections stays scannable. My Plan is the hero above; Account sits on its own at the end.
  GROUPS.forEach(g => {
    const items = SECTIONS.filter(s => s.group === g.id); if (!items.length) return;
    h += `<div class="hm-gh" style="--gc:${GROUP_COLOR[g.id]}"><b>${esc(g.label)}</b>
        <span>${esc(g.blurb)}</span></div><div class="tiles">` +
      items.map(homeTile).join('') + '</div>';
  });
  h += `<div class="hm-gh" style="--gc:${GROUP_COLOR.you}"><b>Account</b>
      <span>Sync across your devices, and study with friends.</span></div><div class="tiles">` +
    SECTIONS.filter(s => s.group === 'you').map(homeTile).join('') + '</div>';

  // Existing practice content that predates the sections. Kept reachable rather than
  // orphaned; morning-coffee could later live under Short Stories.
  const drill = LIB.drills[0];
  const coffee = LIB.texts.find(t => t.kind !== 'news' && t.kind !== 'book-chapter' && t.kind !== 'story');
  if (drill || coffee) {
    h += '<div class="sec">Extras</div>';
    if (drill) h += card(drill, 'drill');
    if (coffee) h += card(coffee, 'text');
  }

  h += `<div style="margin:26px 0 14px">${LANG.ornament()}</div>`;
  // Which lexicon stands behind the words is the pack's to say -- Maknuune for Palestinian
  // Arabic, Wiktionary for Hebrew. The claim ("not generated") is the same either way, and it
  // is the claim the whole pipeline exists to be able to make.
  h += `<div class="note"><b>What this shows is real.</b> Every root, meaning and
    pronunciation comes from ${esc(LANG.lex.name)}, ${esc(LANG.lex.blurb)} — not generated.
    Tap any word and the card tells you exactly where its root, gloss and vowels came from.
    <div style="margin-top:10px;padding-top:9px;border-top:1px solid var(--rule);
      font-size:11px;color:var(--muted)">Word data from ${LANG.lex.credit}</div></div>`;
  $('view').innerHTML = h;
}

function newsSection(){
  $('back').hidden = false;
  $('title').textContent = "Today's News";
  const news = LIB.texts.filter(t => t.kind === 'news')
                        .sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  if (!news.length) { $('view').innerHTML =
    `<p class="hint">No news yet. It's written fresh each morning by the daily job.</p>`;
    return; }
  const today = todayISO();
  let h = '';
  if (news[0].date !== today)
    h += `<div class="unval"><b>Today's isn't in yet.</b> The morning job writes it around
      5am; until then the latest is ${esc(news[0].date)}.</div>`;
  h += news.map(t => card(t, 'text')).join('');
  $('view').innerHTML = h;
}

// ---------- Books (full graded readers, with print-to-PDF) ----------
// A book is a set of texts with kind "book-chapter", grouped by their `book` id and ordered by
// `chapter`. Reading a chapter reuses the normal reader; the whole book can be printed to PDF.
// Memoized: secStatus calls this three times per home render, and each call was a full scan of
// every text in the library. With nine books that is ~350 chapters filtered nine times over.
let _books = null;
function booksList() {
  if (_books) return _books;
  const byBook = {};
  LIB.texts.filter(t => t.kind === 'book-chapter').forEach(t => (byBook[t.book] = byBook[t.book] || []).push(t));
  return (_books = Object.keys(byBook).map(id => {
    const chapters = byBook[id].slice().sort((a, b) => (a.chapter || 0) - (b.chapter || 0));
    const c0 = chapters[0];
    return {id, title: c0.book_title || {en: id, ar: ''}, level: c0.level,
            shelf: c0.shelf == null ? 999 : c0.shelf, meta: c0.book_meta || null, chapters};
    // Order decided in the pipeline, not here; id breaks a tie so it is never non-deterministic.
  }).sort((a, b) => (a.shelf - b.shelf) || a.id.localeCompare(b.id)));
}
const bookById = id => booksList().find(b => b.id === id);
// Books print their chapter number in the target language ("الفصل ٣ — ..."); the reader
// shows its own numbering, so the prefix is stripped by a pattern the pack owns.
const chTitleAr = c => (c.title.ar || '').replace(LANG.chapterPrefix, '');
const chTitleEn = c => (c.title.en || '').replace(/^Chapter \d+ — /, '');

// ============ Bible: ESV (your key) ‖ Van Dyck (public domain), side by side ============
// The Arabic is the public-domain Van Dyck, split into one file per book and loaded only
// when a book is opened (data/<lang>/bible/<ID>.js), so the whole app doesn't carry ~7 MB up
// front. The ESV is fetched at runtime from Crossway with the reader's OWN api key — their
// licence forbids redistributing the text, so nothing ESV is ever stored in this repo. The
// key lives in localStorage only (alp.esv.key), never committed, never synced.
const BIB = window.BIBLE_INDEX || [];
const bibById = id => BIB.find(b => b.id === id);
const ESV_KEY = 'alp.esv.key';
const esvKey = () => { try { return localStorage.getItem(ESV_KEY) || ''; } catch (e) { return ''; } };
const _bibCache = {};                 // in-memory Van Dyck book jsons this session
const _esvCache = {};                 // fetched ESV chapters, also mirrored to localStorage


// One book at a time -- the whole Van Dyck text is 7.3 MB, which is not something to load on
// the chance that someone opens the Bible.
//
// A <script> tag rather than fetch(), and this is not a style preference: opened by double-click
// the app runs on file://, where fetch() of a sibling file is a CORS error and nothing else in
// the app does it. The Bible was the one section that worked when hosted and silently failed
// when the app was used the way the whole static-site design exists to allow.
const _bibPending = {};
function loadBibBook(id) {
  if (_bibCache[id]) return Promise.resolve(_bibCache[id]);
  if (_bibPending[id]) return _bibPending[id];
  return (_bibPending[id] = new Promise((ok, no) => {
    const done = () => {
      const d = (window.BIB_BOOKS || {})[id];
      if (!d) return no(new Error('bible book ' + id + ' did not load'));
      ok((_bibCache[id] = d.chapters));
    };
    const s = document.createElement('script');
    s.src = 'data/' + LANG.code + '/bible/' + id + '.js';
    s.onload = done;
    s.onerror = () => no(new Error('bible book ' + id + ' is missing'));
    document.head.appendChild(s);
  }).finally(() => { delete _bibPending[id]; }));
}
// Crossway passage-text API. We ask for clean verse-numbered prose, no footnotes/headings,
// and cache each chapter (localStorage) so a re-open doesn't spend another API call.
async function loadEsv(id, ch) {
  const ref = bibById(id).en + ' ' + ch;
  const ck = id + '.' + ch;
  if (_esvCache[ck]) return _esvCache[ck];
  try { const s = localStorage.getItem('alp.esv.' + ck); if (s) return (_esvCache[ck] = JSON.parse(s)); } catch (e) {}
  const key = esvKey();
  if (!key) return {error: 'nokey'};
  const url = 'https://api.esv.org/v3/passage/text/?q=' + encodeURIComponent(ref) +
    '&include-headings=false&include-footnotes=false&include-verse-numbers=true' +
    '&include-short-copyright=false&include-passage-references=false';
  try {
    const r = await fetch(url, {headers: {Authorization: 'Token ' + key}});
    if (r.status === 401) return {error: 'badkey'};
    if (!r.ok) return {error: 'http ' + r.status};
    const d = await r.json();
    const out = {verses: esvSplit((d.passages || []).join('\n'))};
    _esvCache[ck] = out;
    try { localStorage.setItem('alp.esv.' + ck, JSON.stringify(out)); } catch (e) {}
    return out;
  } catch (e) { return {error: 'network'}; }
}
// The API returns one block of text with inline [n] verse markers; split it back to a
// {num: text} map so each ESV verse can sit beside its Van Dyck counterpart.
function esvSplit(text) {
  const map = {}; const re = /\[(\d+)\]\s*/g; let m, last = null, li = 0;
  while ((m = re.exec(text))) {
    if (last !== null) map[last] = text.slice(li, m.index).trim();
    last = +m[1]; li = re.lastIndex;
  }
  if (last !== null) map[last] = text.slice(li).replace(/\s+/g, ' ').trim();
  return map;
}

function bibleSection(sub, arg) {
  $('back').hidden = false;
  if (sub === 'settings') return bibleSettings();
  if (sub && arg) return bibleChapter(sub, +arg);
  if (sub) return bibleBook(sub);
  return bibleHome();
}

function bibleHome() {
  $('title').textContent = 'Bible';
  const grid = test => BIB.filter(b => b.test === test).map(b =>
    `<button class="bib-b" onclick="location.hash='/bible/${b.id}'">
       <span class="bib-b-en">${esc(b.en)}</span>
       <span class="bib-b-ar" dir="rtl">${esc(b.ar)}</span></button>`).join('');
  // Which edition sits in the right-hand column, and what it is, is the pack's to say. The
  // Arabic side is a 19th-century translation; the Hebrew Old Testament is the original.
  let h = `<p class="hint">${LANG.bible.intro}
     ${esvKey() ? '' : '<button class="lnk" onclick="location.hash=\'/bible/settings\'">Add your ESV key</button> to show the English.'}</p>
    <div class="sec">Old Testament</div><div class="bib-grid">${grid('OT')}</div>
    <div class="sec">New Testament</div><div class="bib-grid">${grid('NT')}</div>
    <div class="note">${LANG.bible.credit} English: ESV, fetched live with your own Crossway
      key — <button class="lnk" onclick="location.hash='/bible/settings'">key settings</button>.
      ${LANG.bible.note || ''}</div>`;
  $('view').innerHTML = h;
}

function bibleBook(id) {
  const b = bibById(id); if (!b) return bibleHome();
  $('title').textContent = b.en;
  let h = `<div class="bib-hd"><div class="bib-hd-en">${esc(b.en)}</div>
     <div class="bib-hd-ar" dir="rtl">${esc(b.ar)}</div>
     <div class="bib-hd-s">${b.chapters.length} chapter${b.chapters.length === 1 ? '' : 's'}</div></div>
    <div class="bib-chs">`;
  for (let c = 1; c <= b.chapters.length; c++)
    h += `<button class="bib-ch" onclick="location.hash='/bible/${id}/${c}'">${c}</button>`;
  h += `</div>`;
  $('view').innerHTML = h;
}

async function bibleChapter(id, ch) {
  const b = bibById(id); if (!b || ch < 1 || ch > b.chapters.length) return bibleBook(id);
  $('title').textContent = b.en + ' ' + ch;
  const gal = LANG.bible.chapterLink ? LANG.bible.chapterLink(id, ch) : null;
  const nav = pos => {
    const prev = pos === 'top';
    let t = ch > 1 ? `<button class="tog" onclick="location.hash='/bible/${id}/${ch - 1}'">← ${ch - 1}</button>` : '<span></span>';
    let n = ch < b.chapters.length ? `<button class="tog" onclick="location.hash='/bible/${id}/${ch + 1}'">${ch + 1} →</button>` : '<span></span>';
    return `<div class="bib-nav">${t}<button class="tog" onclick="location.hash='/bible/${id}'">${esc(b.en)} ${ch}</button>${n}</div>`;
  };
  $('view').innerHTML = `${nav('top')}<div class="bib-read" id="bibRead">
     <div class="hint" style="text-align:center">Loading…</div></div>`;

  const [arCh, esv] = await Promise.all([loadBibBook(id), loadEsv(id, ch)]);
  const verses = arCh[ch - 1] || [];
  let rows = '';
  for (let i = 0; i < verses.length; i++) {
    const n = i + 1;
    const en = esv.verses ? (esv.verses[n] || '') : '';
    rows += `<div class="bib-v">
       <div class="bib-en">${esv.error ? '' : esc(en)}</div>
       <div class="bib-ar" dir="rtl"><span class="bib-vn">${n}</span> ${arLive(verses[i], 'lx-msa')}</div></div>`;
  }
  let head = '';
  if (esv.error === 'nokey')
    head = `<div class="unval">The English side is empty until you add your free ESV key.
       <button class="lnk" onclick="location.hash='/bible/settings'">Add it now →</button></div>`;
  else if (esv.error === 'badkey')
    head = `<div class="unval">That ESV key was rejected (401).
       <button class="lnk" onclick="location.hash='/bible/settings'">Check it →</button></div>`;
  else if (esv.error)
    head = `<div class="unval">Couldn’t load the English (${esc(esv.error)}). Usually that’s a
       wrong or expired ESV key, or a dropped connection — the Arabic still reads below.
       <button class="lnk" onclick="location.hash='/bible/settings'">Check your key →</button></div>`;
  const foot = `${gal ? `<div class="ctl" style="justify-content:center">
      <a class="tog pext" href="${gal}" target="_blank" rel="noopener">Read this chapter in spoken Galilean Arabic ${svg('ext')}</a></div>` : ''}
    <div class="note">Left: ESV®, © Crossway, shown via your API key. Right: Van Dyck (1865), public domain.</div>`;
  const el = $('bibRead'); if (el) el.innerHTML = head + rows + foot + nav('bot');
}

function bibleSettings() {
  $('title').textContent = 'ESV key';
  const has = esvKey();
  $('view').innerHTML = `
    <p class="hint">The English column uses the <b>ESV</b>, which can’t be bundled into a free
      app — but Crossway gives out a free API key that lets this app fetch it for your own
      reading. It’s stored only on this device and never leaves it except to Crossway.</p>
    <ol class="hint" style="line-height:1.9">
      <li>Go to <a href="https://api.esv.org/" target="_blank" rel="noopener">api.esv.org</a> and create a free API key.</li>
      <li>Paste it here.</li></ol>
    <label class="phlab">ESV API key
      <input id="esvk" value="${esc(has)}" placeholder="paste your key" autocomplete="off"></label>
    <div class="ctl" style="margin-top:12px">
      <button class="tog go" onclick="bibleSaveKey()">Save</button>
      ${has ? '<button class="tog" onclick="bibleClearKey()">Remove key</button>' : ''}
      <button class="tog" onclick="location.hash='/bible'">Back to the Bible</button></div>
    <div class="note">Stored in this browser only (localStorage), never committed to the app
      and never sent anywhere but Crossway. Fetched chapters are cached here so you don’t
      re-spend API calls re-reading.</div>`;
}
function bibleSaveKey() {
  const v = ($('esvk') || {}).value || '';
  try { localStorage.setItem(ESV_KEY, v.trim()); } catch (e) {}
  location.hash = '/bible';
}
function bibleClearKey() {
  try { localStorage.removeItem(ESV_KEY);
    Object.keys(localStorage).filter(k => k.startsWith('alp.esv.')).forEach(k => localStorage.removeItem(k));
  } catch (e) {}
  _esvCache && Object.keys(_esvCache).forEach(k => delete _esvCache[k]);
  location.hash = '/bible/settings';
}

// ============ Ask a Tutor — a grounded dialect chat, on the learner's OWN Claude key ============
// The one thing the rest of the app can't do: answer a question you didn't know to ask. This is a
// bring-your-own-key chat with Claude, hard-anchored to SPOKEN urban Palestinian (not MSA) and
// primed with what this app actually teaches (grammar structures, sounds, reaction categories) so
// its answers stay consistent with everything else here. The key is the learner's own, stored on
// THIS device only (tutor.claude.key — deliberately not an alp.* key, so it never rides the
// Supabase sync; a billable secret shouldn't leave the device). Nothing is committed or synced.
const TUTOR_KEY = 'tutor.claude.key';
const TUTOR_MODEL_KEY = 'tutor.model';
const TUTOR_MODELS = [
  {id: 'claude-sonnet-5', label: 'Sonnet — balanced (recommended)'},
  {id: 'claude-opus-5', label: 'Opus — most capable, priciest'},
  {id: 'claude-haiku-4-5', label: 'Haiku — fastest & cheapest'},
];
const TUTOR_SPEED_KEY = 'tutor.speed';
const tutorSpeed = () => { try { return localStorage.getItem(TUTOR_SPEED_KEY) || 'fast'; } catch (e) { return 'fast'; } };

// Per-model request tuning. Sonnet 5 and Opus 5 run ADAPTIVE THINKING when the `thinking`
// field is omitted — which this request did, so every question a learner asked was silently
// paying for extended reasoning at the default `high` effort before a single word came back.
// For "why is it بدي and not أريد" that is a recall question, not a reasoning one. Effort
// `low` is the lever; thinking stays on (adaptive) rather than disabled, because disabling it
// on Opus 5 can leak <thinking> tags into the visible answer.
//
// Haiku 4.5 predates both parameters — `effort` is rejected outright there and its default is
// already no-thinking, so it gets neither field and is fast as-is.
function tutorTuning(model) {
  if (model === 'claude-haiku-4-5') return {};
  return {thinking: {type: 'adaptive'},
          output_config: {effort: tutorSpeed() === 'fast' ? 'low' : 'high'}};
}
const tutorKey = () => { try { return localStorage.getItem(TUTOR_KEY) || ''; } catch (e) { return ''; } };
const tutorModel = () => { try { return localStorage.getItem(TUTOR_MODEL_KEY) || 'claude-sonnet-5'; } catch (e) { return 'claude-sonnet-5'; } };
let _tutorMsgs = [];        // in-memory conversation for this session (role, content, error?)
let _tutorBusy = false;

const TUTOR_STARTERS = LANG.tutorStarters;

// Ground the model in this app's actual scope + the dialect model, so answers don't drift to MSA.
// The pack writes the tutor's brief; the app supplies what the pack cannot know at load
// time -- grammar, sounds and reactions only exist once the data scripts have run.
function tutorSystemPrompt() {
  return LANG.tutorPrompt({grammar: GRAM, sounds: SND.lessons || [], reactions: RX.cats || []});
}

function tutorSection(sub) {
  $('back').hidden = false;
  if (sub === 'settings') return tutorSettings();
  return tutorHome();
}

function tutorSettings() {
  $('title').textContent = 'Tutor settings';
  const has = tutorKey(), model = tutorModel();
  $('view').innerHTML = `
    <p class="hint">The tutor talks to <b>Claude</b> using <b>your own</b> Anthropic API key. It's
      stored only on this device and is never committed, synced, or sent anywhere but Anthropic —
      unlike the rest of your progress, this key deliberately does <b>not</b> sync to your other
      devices, because it's a billable secret.</p>
    <ol class="hint" style="line-height:1.9">
      <li>Go to <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">console.anthropic.com</a>, add a little credit, and create an API key.</li>
      <li>Paste it here. You pay Anthropic directly for what you use (a few questions costs cents).</li></ol>
    <label class="phlab">Anthropic API key
      <input id="tutk" value="${esc(has)}" placeholder="sk-ant-…" autocomplete="off"></label>
    <label class="phlab">Model
      <select id="tutm">${TUTOR_MODELS.map(m => `<option value="${m.id}"${m.id === model ? ' selected' : ''}>${esc(m.label)}</option>`).join('')}</select></label>
    <label class="phlab">Answer speed
      <select id="tuts">
        <option value="fast"${tutorSpeed() === 'fast' ? ' selected' : ''}>Fast — short thinking, best for everyday questions</option>
        <option value="thorough"${tutorSpeed() === 'thorough' ? ' selected' : ''}>Thorough — more thinking, slower and pricier</option>
      </select></label>
    <p class="hint" style="margin-top:-4px">Fast keeps thinking short. Raise it if you're asking
      something genuinely knotty; for “how do I say…” it makes no difference but the wait.
      Haiku ignores this — it has no thinking mode.</p>
    <div class="ctl" style="margin-top:14px">
      <button class="tog go" onclick="tutorSaveKey()">Save</button>
      ${has ? '<button class="tog" onclick="tutorClearKey()">Remove key</button>' : ''}
      <button class="tog" onclick="location.hash='/tutor'">Back to the tutor</button></div>
    <div class="note">Stored in this browser only (localStorage), never committed to the app and
      never synced. The tutor's answers are AI-generated in spoken Palestinian — high quality, but
      confirm anything you'll lean on with a native speaker.</div>`;
}
function tutorSaveKey() {
  const v = ($('tutk') || {}).value || '';
  const m = ($('tutm') || {}).value || 'claude-sonnet-5';
  const sp = ($('tuts') || {}).value || 'fast';
  try { localStorage.setItem(TUTOR_KEY, v.trim()); localStorage.setItem(TUTOR_MODEL_KEY, m);
        localStorage.setItem(TUTOR_SPEED_KEY, sp); } catch (e) {}
  location.hash = '/tutor';
}
function tutorClearKey() {
  try { localStorage.removeItem(TUTOR_KEY); } catch (e) {}
  _tutorMsgs = [];
  location.hash = '/tutor/settings';
}

function tutorHome() {
  $('title').textContent = 'Ask a Tutor';
  if (!tutorKey()) {
    $('view').innerHTML = `
      <p class="hint">The one thing the rest of the app can't do: answer a question you didn't know
        to ask. Chat with an AI tutor that answers in <b>spoken Palestinian</b> (not textbook MSA) —
        “why is it <span dir="rtl">بدي</span> and not <span dir="rtl">أريد</span>?”, “how do I say I've
        been waiting an hour?”, “what do I say when someone cooks for me?”</p>
      <div class="unval"><b>Bring your own key.</b> This uses your own Anthropic (Claude) API key,
        stored only on this device — you pay Anthropic directly, usually cents. Answers are
        AI-generated: excellent for practice, but confirm anything important with a native speaker.</div>
      ${_askPend ? `<div class="tut-held"><b>Your question is being held:</b>
        <span class="tut-held-q">${esc(_askPend.split('\n')[0])}${_askPend.includes('\n') ? ' …' : ''}</span>
        It will be asked as soon as you add a key.</div>` : ''}
      <div class="ctl"><button class="tog go" style="font-size:14px;padding:11px 20px"
        onclick="location.hash='/tutor/settings'">Add your Claude key →</button></div>`;
    return;
  }
  const savedN = tutorSavedCount();
  let h = `<p class="hint">Ask anything about spoken Palestinian — grammar, a word, how to say
    something, or “is this how a Palestinian would put it?” When it teaches you a phrase, tap
    <b>+ Save</b> and it becomes a flashcard — so what you couldn't say today comes back in your
    daily review. <button class="lnk" style="background:none;border:none;color:var(--verdigris);cursor:pointer;font:inherit;padding:0"
    onclick="location.hash='/tutor/settings'">Settings</button></p>
    ${savedN ? `<div class="tut-loop">🗂 <b>${savedN}</b> phrase${savedN === 1 ? '' : 's'} saved from your tutor ${savedN === 1 ? 'is' : 'are'} in your review rotation.
      <button class="lnk" style="background:none;border:none;color:var(--verdigris);cursor:pointer;font:inherit;padding:0" onclick="location.hash='/vocab/review'">Review now →</button></div>` : ''}
    <div class="tut-log" id="tut-log"></div>`;
  if (!_tutorMsgs.length) {
    h += `<div class="sec" style="margin-top:2px">Try one of these</div>
      <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px">` +
      TUTOR_STARTERS.map((s, i) => `<button class="tut-chip" onclick="tutorStart(${i})">${esc(s)}</button>`).join('') +
      `</div>`;
  }
  h += `<div class="tut-row">
      ${kbdWrap(`<textarea id="tut-in" rows="1" placeholder="Ask in English or ${esc(LANG.name)}…"
        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();tutorAsk(this.value)}"></textarea>`,
        'tut-in', true)}
      <button class="tut-send" id="tut-send" onclick="tutorAsk(($('tut-in')||{}).value)">Ask</button>
    </div>
    ${_tutorMsgs.length ? '<div class="ctl" style="margin-top:10px"><button class="tog" onclick="tutorClearChat()">Clear chat</button></div>' : ''}`;
  $('view').innerHTML = h;
  tutorRenderLog();
  const inp = $('tut-in'); if (inp) inp.focus();
  tutorFlushPending();
}

function tutorStart(i) { tutorAsk(TUTOR_STARTERS[i]); }
function tutorClearChat() { _tutorMsgs = []; tutorHome(); }

// Minimal formatter: escape, **bold**, wrap Arabic runs so they render in the Arabic face, newlines.
function tutFmt(t) {
  let s = esc(t);
  s = s.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
  // The tutor's own Arabic is tappable as well: it answers in words, and any one of them can
  // be the word you didn't know. The run matched here holds only Arabic, digits and .،؟! —
  // none of which esc() rewrites — so re-tokenizing it cannot double-escape anything.
  s = s.replace(/[؀-ۿݐ-ݿ][؀-ۿݐ-ݿً-ٟ\s\d.،؟!]*[؀-ۿݐ-ݿ]/g,
    m => '<span class="rt">' + arLive(m) + '</span>');
  return s.replace(/\n/g, '<br>');
}

// Pull the tutor's machine-readable <save>…</save> block into [{ar,en}] — the phrases worth keeping.
function tutorParseSaves(txt) {
  const m = /<save>([\s\S]*?)<\/save>/i.exec(txt || '');
  if (!m) return [];
  const out = [], seen = new Set();
  m[1].split('\n').forEach(line => {
    const l = line.replace(/^[\s\-•*]+/, '').trim();
    const eq = l.indexOf('=');
    if (eq < 1) return;
    const ar = l.slice(0, eq).trim(), en = l.slice(eq + 1).trim();
    if (!ar || !en || !isTargetScript(ar) || seen.has(ar)) return;
    seen.add(ar);
    out.push({ar, en});
  });
  return out.slice(0, 4);
}

// The loop: a saved phrase becomes a real SRS card (kind 'phrase', tagged from the tutor), so it
// flows into daily review and the Plan's spaced-review task exactly like any other flashcard.
function tutorSaveCard(mi, si) {
  const m = _tutorMsgs[mi]; if (!m || !m.saves) return;
  const sv = m.saves[si]; if (!sv) return;
  const key = phKey(sv.ar);
  if (!marked.has(key)) {
    marked.set(key, srsInit({kind: 'phrase', lemma: key, phrase: sv.ar, vocalized: sv.ar,
      surface: sv.ar, gloss: sv.en, caphi: '', parts: [], analysis: 'PHRASE', root: '',
      provenance: 'tutor', source: 'tutor', deck: activeDeck()}));
    save(); count();
  }
  sv.saved = true;
  tutorRenderLog();
}
const tutorSavedCount = () => { try { return [...marked.values()].filter(c => c.source === 'tutor').length; } catch (e) { return 0; } };

function tutorRenderLog() {
  const log = $('tut-log'); if (!log) return;
  let h = _tutorMsgs.map((m, mi) => {
    if (m.error) return `<div class="tut-b err">${tutFmt(m.error)}</div>`;
    const cls = m.role === 'user' ? 'me' : 'ai';
    let b = `<div class="tut-b ${cls}">${tutFmt(m.content)}</div>`;
    if (m.saves && m.saves.length) {
      b += `<div class="tut-saves"><div class="tut-saves-h">Save to your review</div>` +
        m.saves.map((sv, si) => {
          const done = sv.saved || marked.has(phKey(sv.ar));
          return done
            ? `<span class="tut-save done">✓ <span class="rt" dir="rtl">${esc(sv.ar)}</span> — ${esc(sv.en)}</span>`
            : `<button class="tut-save" onclick="tutorSaveCard(${mi},${si})">+ <span class="rt" dir="rtl">${esc(sv.ar)}</span> — ${esc(sv.en)}</button>`;
        }).join('') + `</div>`;
    }
    return b;
  }).join('');
  if (_tutorBusy) h += `<div class="tut-dots">· · ·</div>`;
  log.innerHTML = h;
  log.scrollIntoView(false);
  const s = $('tut-send'); if (s) s.disabled = _tutorBusy;
}

// Send a turn to Claude with the learner's own key, straight from the browser.
// Build the request body. Two things here are about speed rather than content:
//
// STREAMING. The old request awaited the whole reply, then res.json(), then rendered — so the
// learner watched a "· · ·" for the entire generation, however long the answer ran. Streaming
// does not make Claude faster; it makes the wait start at the FIRST word instead of the last,
// which for a paragraph-length answer is most of the perceived delay.
//
// PROMPT CACHING. The system prompt is ~2,830 characters — roughly 700-950 tokens, which is
// BELOW the 1,024-token minimum cacheable prefix on Sonnet 5 and Haiku 4.5 (Opus 5's minimum is
// 512). So a breakpoint on the system block alone would silently cache nothing on the default
// model. The breakpoint that pays is the one on the last message of the turn being sent: from
// the next turn on, the whole system-plus-history prefix is one cached read, and by then it is
// comfortably over the minimum. Both are marked — the system one starts earning on Opus
// immediately, and costs nothing where it doesn't.
function tutorBody(msgs) {
  const model = tutorModel();
  const wire = msgs.filter(m => !m.error && m.content)
                   .map(m => ({role: m.role, content: m.content}));
  if (wire.length) {              // cache_control needs block form, so convert just the last turn
    const last = wire[wire.length - 1];
    last.content = [{type: 'text', text: last.content, cache_control: {type: 'ephemeral'}}];
  }
  return Object.assign({
    model, max_tokens: 2048, stream: true,
    system: [{type: 'text', text: tutorSystemPrompt(), cache_control: {type: 'ephemeral'}}],
    messages: wire,
  }, tutorTuning(model));
}

// Repaint only the streaming bubble, and at most ~15x a second. tutFmt() runs the Arabic
// through arLive(), so re-rendering the whole answer on every delta is O(n²) in the length of
// the reply — fine for a sentence, visibly janky by the time it is a few paragraphs.
let _tutStreamAt = 0;
function tutorPaintStream(force) {
  const now = Date.now();
  if (!force && now - _tutStreamAt < 66) return;
  _tutStreamAt = now;
  const log = $('tut-log'); if (!log) return;
  const bubbles = log.querySelectorAll('.tut-b.ai');
  const el = bubbles[bubbles.length - 1];
  const m = _tutorMsgs[_tutorMsgs.length - 1];
  if (!el || !m) return;
  el.innerHTML = tutFmt(m.content || '');
  log.scrollIntoView(false);
}

async function tutorStream(msgs, onDelta) {
  let res;
  try {
    res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {'content-type': 'application/json', 'x-api-key': tutorKey(),
        'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true'},
      body: JSON.stringify(tutorBody(msgs)),
    });
  } catch (e) {
    return {error: "Network error — couldn't reach Claude. Check your connection and try again."};
  }
  if (!res.ok) {
    // An error response is JSON, not an event stream — read it as text and parse.
    let data = {}; try { data = JSON.parse(await res.text()); } catch (e) {}
    const msg = (data && data.error && data.error.message) || ('HTTP ' + res.status);
    return {error: res.status === 401
      ? "Your Claude API key was rejected (401). Check or re-paste it in Settings."
      : (res.status === 400 && /credit balance/i.test(msg))
        ? "Your Anthropic account is out of credit. Add a little at console.anthropic.com, then try again."
        : ('Couldn’t reach Claude: ' + msg)};
  }
  const reader = res.body.getReader(), dec = new TextDecoder();
  let buf = '', out = '', stop = null;
  try {
    for (;;) {
      const {done, value} = await reader.read();
      if (done) break;
      buf += dec.decode(value, {stream: true});
      // SSE frames are separated by a blank line; keep any partial frame in the buffer.
      const frames = buf.split('\n\n'); buf = frames.pop();
      for (const f of frames) {
        const line = f.split('\n').find(x => x.startsWith('data:'));
        if (!line) continue;
        let ev; try { ev = JSON.parse(line.slice(5).trim()); } catch (e) { continue; }
        if (ev.type === 'content_block_delta' && ev.delta && ev.delta.type === 'text_delta') {
          out += ev.delta.text; onDelta(out, false);
        } else if (ev.type === 'message_delta' && ev.delta) {
          stop = ev.delta.stop_reason || stop;
        } else if (ev.type === 'error') {
          return {error: 'Couldn’t reach Claude: ' + ((ev.error && ev.error.message) || 'the stream ended early')};
        }
      }
    }
  } catch (e) {
    return {error: "Network error — the answer stopped part-way. Try again."};
  }
  onDelta(out, true);
  if (stop === 'refusal') return {error: "The model declined to answer that one — try rephrasing."};
  return {text: out, stop};
}

// Send a turn to Claude with the learner's own key, straight from the browser.
async function tutorAsk(text) {
  text = (text || '').trim();
  if (!tutorKey()) { location.hash = '/tutor/settings'; return; }
  if (!text || _tutorBusy) return;
  const hadStarters = !_tutorMsgs.length;   // first message: re-render to drop the starter chips
  _tutorMsgs.push({role: 'user', content: text});
  _tutorBusy = true;
  const inp = $('tut-in'); if (inp) inp.value = '';
  if (hadStarters) tutorHome(); else tutorRenderLog();

  // Placeholder bubble the deltas stream into.
  const slot = {role: 'assistant', content: '', streaming: true};
  _tutorMsgs.push(slot);
  tutorRenderLog();

  const r = await tutorStream(_tutorMsgs.slice(0, -1), (out, done) => {
    slot.content = out; tutorPaintStream(done);
  });
  slot.streaming = false;
  if (r.error) { _tutorMsgs.pop(); _tutorMsgs.push({role: 'assistant', error: r.error}); }
  else {
    const txt = (r.text || '').trim();
    slot.saves = tutorParseSaves(txt);          // pull out the machine-readable phrase block
    slot.content = txt.replace(/<save>[\s\S]*?<\/save>\s*$/i, '').trim() || '(no answer came back)';
  }
  _tutorBusy = false;
  tutorRenderLog();
}

// ============ Lessons — teaching units from the native reference materials ============
// The spine of the rebuilt curriculum (Stage 3). Each unit is a coherent ~30-45 min lesson whose
// Arabic is copied VERBATIM from the user's own teaching materials (texts/ref/ — courses written
// and used by native/professional teachers); per-chunk src names the exact book page. This is a
// STRONGER provenance tier than "curated": the Arabic itself comes from native teaching print.
// English glosses are the book's where it had them, the app's where a page was Arabic-only.
const LSN = window.LESSONS || {units: []};
const lsnById = id => (LSN.units || []).find(u => u.id === id);
const lsnDone = id => contentSeen().has('lsn:' + id);

function lessonsSection(sub) {
  $('back').hidden = false;
  const u = lsnById(sub);
  return u ? lessonView(u) : lessonsHome();
}

function lessonsHome() {
  $('title').textContent = 'Lessons';
  let h = `<p class="hint">Structured teaching units — the spine your plan walks through, one unit
    at a time. Each one: the new chunks, one grammar point, and the same drills the source course
    uses, ending with you producing real sentences about your real life.</p>
    <div class="refsrc"><b>From native teaching materials.</b> The Arabic in these units is copied
    verbatim from courses written by native-speaker teachers (each item names its page). English
    glosses follow the books where given.</div>
    <div class="vtiles">`;
  h += (LSN.units || []).map(u => `<button class="vtile wide" onclick="location.hash='/lessons/${u.id}'">
      <div class="vtile-h"><span class="vtile-t">Unit ${u.n} — ${esc(u.title.en)}</span>
        <span class="vtile-n">${lsnDone(u.id) ? '✓ done' : ''}</span></div>
      <div class="vtile-s">${lvlTagFor('unit', u)} <span dir="rtl">${esc(u.title.ar)}</span> · ${u.chunks.length} chunks</div>
    </button>`).join('');
  h += `</div>`;
  $('view').innerHTML = h;
}

const _lsnKey = ar => phKey(ar);
function lsnSaved(ar) { return marked.has(_lsnKey(ar)); }
const lsnLeft = u => (u.chunks || []).filter(c => c.ar && !lsnSaved(c.ar)).length;
// A unit with nothing to check off (the dialogue- and reading-driven ones) has nothing to gate —
// otherwise it could never be completed and would wedge the plan on that day.
const lsnAllSaved = u => !!u && lsnLeft(u) === 0;
// A lesson chunk becomes a real SRS phrase card — same loop as the tutor's saved phrases:
// what a unit teaches comes back in daily review and the plan with zero extra wiring.
// Tapping again UNCHECKS it (mis-taps happen); a card you've already reviewed asks first,
// since removing it would throw away real spaced-repetition progress.
function lsnToggle(uid, ci) {
  const u = lsnById(uid); if (!u) return;
  const c = u.chunks[ci]; if (!c || !c.ar) return;
  const key = _lsnKey(c.ar), had = marked.get(key);
  if (had) {
    if ((had.reps || 0) > 0 &&
        !confirm('You’ve already reviewed this card ' + had.reps + ' time' + (had.reps === 1 ? '' : 's') +
                 '. Remove it and lose that progress?')) return;
    marked.delete(key);
  } else {
    marked.set(key, srsInit({kind: 'phrase', lemma: key, phrase: c.ar, vocalized: c.ar,
      surface: c.ar, gloss: c.en || '', caphi: '', parts: [], analysis: 'PHRASE', root: '',
      audio: c.audio || null, example_ar: c.reply ? c.ar + ' — ' + c.reply.ar : null,
      example_en: c.reply ? (c.en || '') + ' — ' + (c.reply.en || '') : null,
      provenance: 'ref', source: 'lesson', deck: activeDeck()}));
  }
  save(); count();
  lessonView(u);
}
// Finishing a unit is gated on having worked every chunk — that's what "done" means here.
function lsnFinish(uid) {
  const u = lsnById(uid); if (!u) return;
  const done = lsnDone(u.id);
  if (!done && !lsnAllSaved(u)) return;                 // button is disabled in this state anyway
  markSeen('lsn:' + u.id, !done);
  lessonView(u);
}

function lsnChunkRow(uid, c, ci) {
  const say = c.audio ? `<button class="say" onclick="sndPlay('${cssq(c.audio)}')" aria-label="Play">${svg('spk')}</button>` : '';
  const saved = lsnSaved(c.ar);
  return `<div class="lsn-chunk">
    <div class="lsn-ar" dir="rtl">${arLive(c.ar)}${say}</div>
    <div class="lsn-en">${esc(c.en || '')}${c.note ? ` <span class="lsn-note">${esc(c.note)}</span>` : ''}
      ${c.reply ? `<div class="lsn-reply" dir="rtl">↩ ${esc(c.reply.ar)}</div>
        <div class="lsn-replyen">${esc(c.reply.en || '')}</div>` : ''}</div>
    <button class="lsn-add${saved ? ' on' : ''}" onclick="lsnToggle('${uid}',${ci})"
      aria-pressed="${saved}" title="${saved ? 'Tap to uncheck' : 'Save to flashcards'}"
      aria-label="${saved ? 'Uncheck — remove from flashcards' : 'Save to flashcards'}">${saved ? '✓' : '+'}</button>
  </div>`;
}

const AR_RUN = LANG.script.run;
function bidiMix(str) {
  return String(str == null ? '' : str).split(AR_RUN).map(p => {
    if (!p) return '';
    if (AR_RUN.test(p) || !/[A-Za-z]/.test(p)) return esc(p);
    const m = p.match(/^([^A-Za-z(\[{"'\u00AB]*)([\s\S]*)$/);
    return esc(m[1]) + `<bdi dir="ltr">${esc(m[2])}</bdi>`;
  }).join('');
}

function lsnDrillHTML(u, d) {
  let h = `<div class="sec">${esc(d.title || 'Drill')}</div>`;
  if (d.instructions) h += `<p class="hint" dir="rtl">${bidiMix(d.instructions)}</p>`;
  if (d.type === 'pairs') {
    // The book's own format: greeting → SAY the reply → check. Reuses the drill reveal style.
    u.chunks.filter(c => c.reply).forEach(c => {
      h += `<div class="ch"><div class="q" dir="rtl">${arLive(c.ar)}</div>
        <div class="a" tabindex="0" dir="rtl">${esc(c.reply.ar)}</div>
        ${c.reply.audio ? player(c.reply.audio) : ''}
        <div class="u">${esc((c.en || '') + (c.reply.en ? ' → ' + c.reply.en : ''))}</div></div>`;
    });
  } else if (d.type === 'roleplay') {
    (d.items || []).forEach(it => { h += `<div class="lsn-ad" dir="rtl">${bidiMix(it.cue)}</div>`; });
  } else {  // qa and anything else: numbered say-out-loud prompts
    h += (d.items || []).map(it => `<div class="lsn-qa" dir="rtl">${bidiMix(it.cue)}</div>`).join('');
  }
  return h;
}

function lessonView(u) {
  $('title').textContent = 'Unit ' + u.n;
  let h = `<div class="lsn-head">
      <div class="lsn-title" dir="rtl">${esc(u.title.ar)}</div>
      <div class="lsn-title-en">${esc(u.title.en)}</div>
      <p class="hint">${esc(u.objective)}</p>
      <div class="refsrc">From native teaching materials. Tap <b>+</b> on any chunk
        to send it to your flashcards.</div></div>`;
  if (u.grammar) {
    h += `<div class="sec">The grammar point</div>
      <div class="lsn-gram"><b>${esc(u.grammar.point)}</b>
        <p>${esc(u.grammar.body || '')}</p>
        ${(u.grammar.examples || []).map(e => `<div class="lsn-gx"><span dir="rtl">${arLive(e.ar)}</span>
           <em>${esc(e.en)}</em></div>`).join('')}
        ${u.gram_id && gramById(u.gram_id) ? `<button class="tog" onclick="location.hash='/grammar/${u.gram_id}'">Full lesson: ${esc(gramById(u.gram_id).title)} →</button>` : ''}
      </div>`;
  }
  if (u.chunks.length) {
    h += `<div class="sec">The chunks</div>`;
    let lastGroup = null;
    u.chunks.forEach((c, ci) => {
      if ((c.group || null) !== lastGroup) { lastGroup = c.group || null;
        if (lastGroup) h += `<div class="lsn-group">${bidiMix(lastGroup)}</div>`; }
      h += lsnChunkRow(u.id, c, ci);
    });
  }
  // Dialogues and readings come straight off the page, untranslated as the book prints them —
  // read them aloud. Speaker labels are kept so you can hear who is talking.
  (u.dialogues || []).forEach((d, di) => {
    const srcs = (d.lines || []).filter(l => l.audio).map(l => l.audio);
    h += `<div class="sec">${esc(d.title || 'Dialogue')}</div>`;
    // Same continuous player the Dinner Table uses, so the whole conversation runs start to
    // finish — which is the point of giving each speaker their own voice.
    if (srcs.length) h += paraPlayer();
    h += `<div class="lsn-dlg">` +
      d.lines.map(l => `<div class="lsn-line">
        ${l.sp ? `<span class="lsn-sp">${esc(l.sp)}${
          l.audio ? `<button class="say" onclick="sndPlay('${cssq(l.audio)}')" aria-label="Play line">${svg('spk')}</button>` : ''}</span>` : ''}
        <span class="lsn-lar" dir="rtl">${arLive(l.ar)}</span>
        ${l.en ? `<span class="lsn-len">${esc(l.en)}</span>` : ''}</div>`).join('') +
      `</div>${(d.cast || []).length > 1
        ? '<div class="note">Each speaker has their own voice.</div>' : ''}`;
  });
  // Reading passages were the one place still rendering Arabic as flat escaped text, so they
  // were also the one place a word couldn't be tapped. arLive() fixes that — and it is why the
  // English had to come out of the `ar` string first (pipeline/lesson_cleanup.py): inline Latin
  // would have been tokenized into dead spans. The lifted glosses come back as a key underneath.
  (u.texts || []).forEach(t => {
    h += `<div class="sec">${esc(t.title || 'Reading')}</div><div class="lsn-text" dir="rtl">` +
      t.sentences.map(s => {
        const ar = typeof s === 'string' ? s : (s.ar || '');
        const en = typeof s === 'string' ? null : s.en;
        const gl = (typeof s === 'string' ? null : s.gloss) || [];
        return `<p>${arLive(ar)}${en ? `<em class="lsn-ten">${esc(en)}</em>` : ''}${
          gl.length ? `<span class="lsn-key" dir="ltr">${gl.map(g =>
            `<span class="lsn-kw"><b dir="rtl">${esc(g.w)}</b>${esc(g.en)}</span>`).join('')}</span>` : ''}</p>`;
      }).join('') + `</div>`;
  });
  (u.drills || []).forEach(d => { h += lsnDrillHTML(u, d); });
  if (u.produce) h += `<div class="sec">Now produce</div><div class="lsn-produce">${esc(u.produce)}</div>`;
  const i = (LSN.units || []).findIndex(x => x.id === u.id);
  const next = (LSN.units || [])[i + 1];
  const left = lsnLeft(u), all = lsnAllSaved(u), fin = lsnDone(u.id);
  h += `<div class="lsn-finish">
      <div class="lsn-prog">${u.chunks.length
        ? `${u.chunks.length - left} of ${u.chunks.length} chunks checked${
            left ? ` · <b>${left}</b> to go` : ' · all done'}`
        : 'Work through the dialogue and the drills out loud, then mark it done.'}</div>
      <button class="tog go lsn-fin" ${all || fin ? '' : 'disabled'} onclick="lsnFinish('${u.id}')">${
        fin ? '✓ Unit complete — tap to reopen' : 'Mark unit complete'}</button>
      ${!all && !fin ? `<div class="lsn-gate">Check off every chunk above before finishing the unit —
        that's how the material gets into your review.</div>` : ''}
    </div>
    <div class="ctl" style="margin-top:16px">
    ${next ? `<button class="tog go" onclick="location.hash='/lessons/${next.id}'">Next: Unit ${next.n} →</button>` : ''}
    <button class="tog" onclick="location.hash='/lessons'">All units</button></div>`;
  $('view').innerHTML = h;
  // Hand each conversation's clips to its own player, in render order. The first is bound live;
  // the others take over when pressed.
  const players = [...$('view').querySelectorAll('.player.para')];
  (u.dialogues || []).filter(d => (d.lines || []).some(l => l.audio)).forEach((d, k) => {
    const el = players[k]; if (!el) return;
    const srcs = d.lines.filter(l => l.audio).map(l => l.audio);
    if (k === 0) paraSetup(el, srcs); else paraRegister(el, srcs);
  });
}

// ============ Listening — real Levantine speech, transcript on the maker's site ============
function listeningSection(sub) {
  $('back').hidden = false;
  const ep = lsById(sub);
  return ep ? listeningEp(ep) : listeningHome();
}

function listeningHome() {
  $('title').textContent = 'Listening';
  const seen = contentSeen();
  let h = `<p class="hint">Adults talking at full speed about real subjects — the one thing the
    app's own audio can't be, because everything else here was recorded for a learner. Every
    episode has a transcript, an English translation and a vocabulary list on the makers' site.</p>
    <div class="refsrc"><b>Real Arabic</b>, by Amer (Suweida, Syria) and Keire Murphy. The audio and
    transcripts live on <a href="${LISTEN_HOME}" target="_blank" rel="noopener">their site</a> and
    stay there — this is a signposted index, not a copy. If it earns its keep for you,
    <a href="https://realarabic.weebly.com/support.html" target="_blank" rel="noopener">support
    them</a>.</div>
    <div class="unval"><b>Syrian and Lebanese, not Palestinian.</b> Close kin to what you're
    learning and superb ear-training, but the ق, some vowels and a fair bit of vocabulary differ
    from the urban Palestinian the lessons drill. Listen for the shape, not the model.</div>
    <div class="vtiles">`;
  h += LISTEN.slice().sort((a, b) => (a.phase - b.phase) || a.date.localeCompare(b.date))
    .map(e => `<button class="vtile wide" onclick="location.hash='/listening/${e.slug}'">
      <div class="vtile-h"><span class="vtile-t">${esc(e.title)}</span>
        <span class="vtile-n">${seen.has('ls:' + e.slug) ? '✓ done' : ''}</span></div>
      <div class="vtile-s">${lvlTagFor('listen', e)} ${esc(e.date)} · transcript ${e.tr === 'pdf' ? 'as a PDF' : 'on the page'}</div>
    </button>`).join('');
  h += `</div>`;
  $('view').innerHTML = h;
}

function listeningEp(e) {
  $('title').textContent = 'Listening';
  $('view').innerHTML = `
    <div class="lsn-title-en">${esc(e.title)}</div>
    <p class="hint">${esc(e.date)} · Real Arabic · transcript ${e.tr === 'pdf' ? 'as a downloadable PDF' : 'printed on the page'}</p>
    <div class="sec">How to use it</div>
    <ol class="hint" style="line-height:1.9">
      <li><b>Listen once with nothing in front of you.</b> Get the gist — who is talking, what about.
        You are not meant to catch it all.</li>
      <li><b>Listen again with the transcript.</b> Now the words you missed attach to sounds you
        already heard, which is the part that actually builds the ear.</li>
      <li><b>Retell it out loud</b> in three or four sentences, in Arabic, without looking.</li>
      <li>Note what you couldn't say — that's tomorrow's question for the tutor.</li>
    </ol>
    <div class="ctl" style="margin-top:14px">
      <button class="tog go" onclick="window.open('${cssq(e.url)}','_blank','noopener')">
        Open the episode &amp; transcript →</button>
      <button class="tog" onclick="location.hash='/listening'">All episodes</button>
      <button class="tog" onclick="location.hash='/tutor'">Ask about something you heard</button>
    </div>
    <div class="note">Opens realarabic.weebly.com in a new tab — the audio and the transcript are
      theirs and are read there.</div>`;
}

function booksSection(sub, arg) {
  $('back').hidden = false;
  if (sub && arg === 'print') return bookPrintView(sub);
  if (sub) return bookView(sub);
  return booksHome();
}

function booksHome() {
  $('title').textContent = 'Books';
  const books = booksList();
  // Arabic's books are retold by Claude; Hebrew's are public-domain literature, verbatim, with
  // only the English ours. Opposite claims, so the blurb is the language's own.
  let h = `<p class="hint">${LANG.booksBlurb}</p>`;
  // Grouped by level, using the SAME three names and order the stories use — books and stories
  // can then never disagree about what "intermediate" means. The chip moves to the section
  // header, which frees the tile's last line for chapter count and how far you have read.
  const seen = contentSeen();
  const tile = b => { const read = b.chapters.filter(c => seen.has(c.id)).length;
    return `<button class="bk-cover" onclick="location.hash='/books/${esc(b.id)}'">
      <div class="bk-cover-ar" dir="rtl">${esc(b.title.ar)}</div>
      <div class="bk-cover-en">${esc(b.title.en)}</div>
      <div class="bk-cover-s">${b.chapters.length} chapters${read ? ' · ' + read + ' read' : ''}</div>
      </button>`; };
  const placed = new Set();
  STORY_LEVELS.forEach(([key, label]) => {
    const at = books.filter(b => b.level === key); if (!at.length) return;
    at.forEach(b => placed.add(b.id));
    h += `<div class="sec">${esc(label)} ${lvlTagFor('book', {level: key}, true)}</div>
      <div class="bk-shelf">${at.map(tile).join('')}</div>`;
  });
  // A book whose level isn't one of the three would otherwise be silently drawn as Beginner by
  // the phase-0 fallthrough. Show it as unshelved instead of quietly mislabelling it.
  const rest = books.filter(b => !placed.has(b.id));
  if (rest.length) h += `<div class="sec">Not yet graded</div>
      <div class="bk-shelf">${rest.map(tile).join('')}</div>`;
  if (!books.length) h += `<p class="hint">No books yet.</p>`;
  $('view').innerHTML = h;
}

function bookView(id) {
  const b = bookById(id); if (!b) return booksHome();
  $('title').textContent = b.title.en;
  const seen = contentSeen();
  const readN = b.chapters.filter(c => seen.has(c.id)).length;
  let h = `<div class="bk-hero"><div class="bk-hero-ar" dir="rtl">${esc(b.title.ar)}</div>
     <div class="bk-hero-en">${esc(b.title.en)}</div>
     <div class="bk-hero-s">${(b.chapters[0] || {}).register ? 'Public domain, verbatim' : 'Adapted for learners'} · ${b.chapters.length} chapters · ${readN} read</div></div>`;
  // A shelf is not one person's book. `meta` is chapter 1's, and printing it as the volume's
  // source credited ישראל דושמן with thirty-seven works by twelve authors — a misattribution of
  // public-domain literature, which is the one thing this shelf cannot get wrong. A book that
  // really is one work still reads exactly as it did.
  const bkAuthors = [...new Set(b.chapters.map(c => ((c.book_meta || {}).author || '').trim())
                                          .filter(Boolean))];
  if (bkAuthors.length > 1)
    h += `<div class="bk-src">${b.chapters.length} works by ${bkAuthors.length} authors${
       b.meta && b.meta.status ? ' · ' + esc(b.meta.status) : ''}.</div>`;
  else if (b.meta) h += `<div class="bk-src">${(b.chapters[0] || {}).register ? 'From' : 'Retold from'} ${esc(b.meta.work || b.title.en)}${
     b.meta.author ? ' — ' + esc(b.meta.author) : ''}${b.meta.year ? ', ' + esc(b.meta.year) : ''}${
     b.meta.status ? ' · ' + esc(b.meta.status) : ''}.</div>`;
  // A book whose chapters carry register numbers was SELECTED, not written, and the honest
  // banner is the one that shows what it was selected against.
  const reg = (b.chapters[0] || {}).register;
  h += reg
    ? `<div class="unval"><b>Published Hebrew, chosen by measurement.</b> Every sentence is as
       Project Ben-Yehuda transcribed it, vowels included — the English is ours. It was let onto
       this shelf for reading like present-day Hebrew: ${reg.archaic_per_1k} archaic words and
       ${reg.vav_consecutive_per_1k} biblical verb forms per thousand, ${reg.avg_sentence_words}-word
       sentences, against the daily paper's 6.7, 0.0 and 12.4.</div>`
    : `<div class="unval"><b>Not checked by a native speaker.</b> This retelling is written by Claude —
     every word’s root and meaning is from the lexicon, but read it for practice; don’t memorise the phrasing.</div>`;
  h += `<div class="ctl">
     <button class="tog go" onclick="location.hash='/text/${esc(b.chapters[0].id)}'">${readN ? 'Keep reading' : 'Start reading'}</button>
     <button class="tog" onclick="location.hash='/books/${esc(b.id)}/print'">⬇ Download as PDF</button></div>`;
  h += `<div class="sec">Chapters</div>`;
  h += b.chapters.map(c => { const done = seen.has(c.id);
    // Whose story this one is, but only where that varies — on a single-author book the line
    // would repeat the same name down the whole table of contents.
    const by = bkAuthors.length > 1 ? ((c.book_meta || {}).author || '').trim() : '';
    return `<button class="bk-ch" onclick="location.hash='/text/${esc(c.id)}'">
      <span class="bk-ch-n${done ? ' read' : ''}">${done ? '✓' : c.chapter}</span>
      <span class="bk-ch-t"><b dir="rtl">${esc(chTitleAr(c))}</b><span>${esc(chTitleEn(c))}${
        by ? ` <span dir="rtl">— ${esc(by)}</span>` : ''}</span></span></button>`;
  }).join('');
  $('view').innerHTML = h;
}

// The printable whole book. On screen it's a clean reading layout; the print stylesheet strips the
// app chrome so "Save as PDF" yields just the book. Browsers shape Arabic RTL better than any PDF lib.
function bookPrintView(id) {
  const b = bookById(id); if (!b) return booksHome();
  $('title').textContent = b.title.en;
  let h = `<div class="ctl bk-noprint">
      <button class="tog go" onclick="window.print()">⬇ Save as PDF / Print</button>
      <button class="tog" onclick="location.hash='/books/${esc(b.id)}'">Back to book</button></div>
    <p class="hint bk-noprint">This opens your browser’s print dialog — pick <b>Save as PDF</b> as the destination
      to download the whole book, laid out cleanly with one chapter per page.</p>
    <div class="bk-print">
      <div class="bk-print-title"><div class="ar" dir="rtl">${esc(b.title.ar)}</div>
        <div class="en">${esc(b.title.en)}</div>
        <div class="sub">Adapted for learners of spoken Palestinian Arabic</div>
        <div class="sub2">Retelling written by Claude — not checked by a native speaker · word data from the Maknuune lexicon</div></div>`;
  b.chapters.forEach(c => {
    h += `<div class="bk-print-ch"><h2 dir="rtl">${esc(c.title.ar)}</h2><h3>${esc(chTitleEn(c))}</h3>`;
    // group sentences into paragraphs, English and Arabic side by side
    let cur = null, ar = [], en = [];
    const flush = () => { if (!ar.length) return;
      h += `<div class="bk-print-p"><div class="en">${esc(en.join(' '))}</div>
        <div class="ar" dir="rtl">${esc(ar.join(' '))}</div></div>`; ar = []; en = []; };
    c.sentences.forEach(s => { if (cur !== null && s.p !== cur) flush(); cur = s.p; ar.push(s.ar); en.push(s.en); });
    flush();
    h += `</div>`;
  });
  h += `</div>`;
  $('view').innerHTML = h;
}

// ---------- short stories section ----------
function storiesSection(sub){
  $('back').hidden = false;
  const lvl = STORY_LEVELS.find(l => l[0] === sub);
  if (lvl) return storiesLevel(lvl);
  return storiesHome();
}

function storiesHome(){
  $('title').textContent = 'Short Stories';
  let h = `<p class="hint">Graded short stories in spoken ${esc(LANG.name)}, by level. Tap any
    word to see its root, meaning and pronunciation — all from the lexicon. The <b>stories</b>
    themselves are written by Claude, not native-checked, so read for practice and don't
    memorise the phrasing.</p><div class="vtiles">`;
  // Only the levels that have stories in them. Hebrew has beginner and nothing else yet, and a
  // tile reading "Advanced 0" is a promise the section cannot keep.
  h += STORY_LEVELS.filter(([key]) => storiesAt(key).length).map(([key, label, blurb]) => {
    const n = storiesAt(key).length;
    return `<button class="vtile wide" onclick="location.hash='/stories/${key}'">
      <div class="vtile-h"><span class="vtile-t">${esc(label)}</span>
        <span class="vtile-n">${n}</span></div>
      <div class="vtile-s">${lvlTagFor('story', {level: key})} ${esc(blurb)}</div></button>`;
  }).join('');
  h += '</div>';
  $('view').innerHTML = h;
}

function storiesLevel(lvl){
  const [key, label, blurb] = lvl;
  $('title').textContent = label + ' Stories';
  const list = storiesAt(key);
  const seen = contentSeen();
  const readN = list.filter(t => seen.has(t.id)).length;
  let h = `<div class="lvl-row">${lvlTagFor('story', {level: key})}
      <a class="lvl-what" href="#/plan/journey">what do these mean?</a></div>
    <p class="hint">${esc(blurb)}</p>`;
  if (list.length) h += `<div class="sec">Read them in order — ${readN} of ${list.length} done</div>`;
  h += list.length ? list.map((t, i) =>
        `<div class="story-row"><span class="story-n${seen.has(t.id) ? ' read' : ''}">${seen.has(t.id) ? '✓' : (i + 1)}</span>
         <div class="story-c">${card(t, 'text')}</div></div>`).join('')
                   : `<p class="hint">No stories here yet.</p>`;
  h += `<div class="sec" style="margin-top:20px">Levels</div><div class="ctl">` +
    STORY_LEVELS.map(([k, l]) => `<button class="tog"${k === key ? ' aria-pressed="true"' : ''}
        onclick="location.hash='/stories/${k}'">${esc(l)}</button>`).join('') + `</div>`;
  $('view').innerHTML = h;
}

// ---------- videos (Shami Speaker, embedded) ----------
// Supplementary immersion from the Shami Speaker YouTube channel (Levantine, with a northern-
// Palestinian / southern-Lebanon camp focus). EMBEDDED via YouTube's official iframe — nothing
// is downloaded or re-hosted, and this content is NOT run through the lexicon pipeline, so it's
// deliberately kept separate from the app's own dialect-verified material. `pl` is the YouTube
// playlist id; `cat` groups the playlists the way the rest of the app is organised.
// `phase` = the earliest plan phase (0..6) at which the Plan will start scheduling this playlist,
// so a beginner's "watch" task is letters/vocab, not a full TV drama. Higher phases unlock the rest.
// ---- Real Arabic: unscripted native speech, with the transcript on their site ----
// Amer (Suweida, Syria) and Keire Murphy make a Levantine podcast of real interviews and stories,
// each with a transcript, English translation and vocabulary. This is the one thing the app's own
// audio can't be: adults talking at full speed about real subjects, unedited for learners.
//
// WE LINK, WE DON'T COPY. The site carries no licence, so the transcripts are theirs, all rights
// reserved — the same rule this repo already applies to the ESV and the Lingualism book. Each entry
// below is a signpost to their page; the audio and the transcript are read there, where the two
// people who made them get the visit. They also run a Support page and take partnerships, so if we
// ever want the transcripts inside the app, the route is to ask them, not to scrape them.
//
// DIALECT NOTE: this is SYRIAN/LEBANESE Levantine, not the urban Palestinian the rest of the app
// teaches. Close kin, and excellent ear-training — but expect ق, vowels and some vocabulary to
// differ from what the lessons drill. That mismatch is surfaced in the UI, not hidden.
const LISTEN = [
  {slug:'electricity', title:"What's Up With Lebanese Electricity?", date:'2022-03-06', phase:4,
   tr:'page', url:'https://realarabic.weebly.com/podcast-transcripts/episode-27-whats-up-with-lebanese-electricity'},
  {slug:'dzovig', title:'Dzovig, interviewed', date:'2022-04-01', phase:4,
   tr:'page', url:'https://realarabic.weebly.com/podcast-transcripts/episode28-dzovig-interview'},
  {slug:'shireen', title:'شيرين أبو عاقلة', date:'2022-09-23', phase:5,
   tr:'page', url:'https://realarabic.weebly.com/podcast-transcripts/episode'},
  {slug:'immigration', title:'Immigration', date:'2023-01-03', phase:5,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/immigration'},
  {slug:'manar', title:'Manar and Dzovig, interviewed', date:'2023-03-04', phase:5,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/episode-manar-and-dzovig-interviwe'},
  {slug:'ukraine1', title:'Russia/Ukraine and the MENA region, part 1', date:'2023-03-13', phase:5,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/the-impact-of-the-russiaukraine-conflict-on-mena-countries-part-1'},
  {slug:'ukraine2', title:'Russia/Ukraine and the MENA region, part 2', date:'2023-05-18', phase:6,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/the-impact-of-the-russiaukraine-conflict-on-mena-countries-part-2'},
  {slug:'gibran', title:"Gibran's sanctuary — Bcharre and the Prophet's legacy", date:'2023-06-20', phase:6,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/our-journey-to-gibrans-sanctuary-exploring-bcharre-and-the-prophets-legacy'},
  {slug:'firstday', title:"First day at work — Layal and Rana's story", date:'2025-06-25', phase:4,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/first-day-at-work-layal-and-ranas-story'},
  {slug:'july4', title:"The history of America's Independence Day", date:'2025-07-04', phase:6,
   tr:'pdf', url:'https://realarabic.weebly.com/podcast-transcripts/the-history-of-americas-independence-day'},
];
const LISTEN_HOME = 'https://realarabic.weebly.com/';
const lsById = s => LISTEN.find(x => x.slug === s);

const VIDEOS = [
  {slug:'letters',  pl:'PLtMbzvT4n03q7SbY9SxKRC1n7EUBcwyGA', title:'Arabic Letters', n:3, cat:'Lessons', phase:0},
  {slug:'vocab',    pl:'PLtMbzvT4n03rL_Lnf-xRE8dCDnGM81_95', title:'Vocabulary in Levantine Arabic', n:52, cat:'Lessons', phase:0},
  {slug:'grammar',  pl:'PLtMbzvT4n03oW8Grw7m4ooYwOvnrYGKW_', title:'Grammar in Levantine Arabic', n:17, cat:'Lessons', phase:1},
  {slug:'verbs',    pl:'PLtMbzvT4n03rz4hTUdJ_oN3-GmJrLdSL0', title:'Verbs in Levantine Arabic', n:7, cat:'Lessons', phase:1},
  {slug:'quizzes',  pl:'PLtMbzvT4n03qSWHbWAC1UZBON5-dqXHM3', title:'Quizzes in Levantine Arabic', n:3, cat:'Culture & practice', phase:1},
  {slug:'culture',  pl:'PLtMbzvT4n03p3N1F0hl-qVGN0g8abfa_u', title:'Cultural Lessons of the Levant', n:10, cat:'Culture & practice', phase:2},
  {slug:'vlogs',    pl:'PLtMbzvT4n03rQo0_pgwoFZ68O5lQc93Yi', title:'Vlogs & Listening Comprehension', n:7, cat:'Listening', phase:2},
  {slug:'drama',    pl:'PLtMbzvT4n03rWi2DHGB6qLZgh9OXTKuIn', title:'Master Mix: Drama with Subtitles', n:16, cat:'Listening', phase:3},
  {slug:'music',    pl:'PLtMbzvT4n03p4hY5Ef6wbl_drHfP0pqYn', title:'Music Resources', n:16, cat:'Listening', phase:3},
  {slug:'tv',       pl:'PLtMbzvT4n03rs5dniarLMfujIzO6B0J2R', title:'Learn with TV Series', n:11, cat:'Listening', phase:4},
];
const CHANNEL_URL = 'https://www.youtube.com/@ShamiSpeaker';

function videosSection(sub){
  $('back').hidden = false;
  const v = VIDEOS.find(x => x.slug === sub);
  return v ? videosPlay(v) : videosHome();
}

function videosHome(){
  $('title').textContent = 'Videos';
  let h = `<p class="hint">Video lessons and listening practice from
    <a href="${CHANNEL_URL}" target="_blank" rel="noopener">Shami Speaker</a> — a Levantine
    Arabic channel with a northern-Palestinian and southern-Lebanon focus. These play here from
    YouTube; they're <b>supplementary immersion</b>, not part of the app's own lexicon-verified
    material, so the dialect is broader Levantine (some Syrian/Lebanese/Jordanian too).</p>`;
  const cats = [...new Set(VIDEOS.map(v => v.cat))];
  cats.forEach(cat => {
    h += `<div class="sec">${esc(cat)}</div><div class="vtiles">`;
    h += VIDEOS.filter(v => v.cat === cat).map(v =>
      `<button class="vtile wide" onclick="location.hash='/videos/${v.slug}'">
        <div class="vtile-h"><span class="vtile-t">${esc(v.title)}</span>
          <span class="vtile-n">${v.n}</span></div>
        <div class="vtile-s">Playlist · ${v.n} video${v.n === 1 ? '' : 's'}</div></button>`).join('');
    h += '</div>';
  });
  $('view').innerHTML = h;
}

function videosPlay(v){
  $('title').textContent = v.title;
  // youtube-nocookie: privacy-enhanced embed. videoseries?list= plays the whole playlist.
  const embed = `https://www.youtube-nocookie.com/embed/videoseries?list=${encodeURIComponent(v.pl)}&rel=0`;
  const watch = `https://www.youtube.com/playlist?list=${encodeURIComponent(v.pl)}`;
  $('view').innerHTML =
    `<div class="reading">
       <div class="yt-wrap"><iframe src="${embed}" title="${esc(v.title)}"
         allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
         referrerpolicy="strict-origin-when-cross-origin" allowfullscreen loading="lazy"></iframe></div>
       <div class="yt-meta">
         <div>Playlist of ${v.n} video${v.n === 1 ? '' : 's'} · by
           <a href="${CHANNEL_URL}" target="_blank" rel="noopener">Shami Speaker</a></div>
         <a class="tog" href="${watch}" target="_blank" rel="noopener">Open on YouTube ↗</a>
       </div>
       <div class="sec" style="margin-top:22px">More playlists</div><div class="ctl">` +
    VIDEOS.map(x => `<button class="tog"${x.slug === v.slug ? ' aria-pressed="true"' : ''}
        onclick="location.hash='/videos/${x.slug}'">${esc(x.title.split(':')[0])}</button>`).join('') +
    `</div></div>`;
}

// ---------- Reactions (Phase 1: the reflexes of conversation) ----------
// Curated conversational chunks grouped by the job they do (surprise, agreement, sympathy…).
// Drilling one grades it into the SAME SM-2 deck as vocabulary (kind:'reaction'), so reactions
// come back on a spacing schedule and interleave — that's what stops it being the same 30 daily.
const RX = window.REACTIONS || {cats: [], items: []};
const rxCat = id => (RX.cats || []).find(c => c.id === id);
const rxItemsIn = cat => (RX.items || []).filter(r => r.cat === cat);
const rxKey = ar => '®' + arNorm(ar);                        // SRS key, namespaced like phrase '¶'
const rxGot = ar => marked.has(rxKey(ar));                    // "have I started learning this one?"
function rxCard(it) {
  return {kind: 'reaction', lemma: rxKey(it.ar), phrase: it.ar, vocalized: it.ar, surface: it.ar,
          gloss: it.en, audio: it.audio || null, cat: it.cat};
}
// Grade a reaction into the deck. g: 2 Good ("Got it") · 0 Again ("Not yet").
function rxGrade(ar, g) {
  const it = (RX.items || []).find(r => r.ar === ar); if (!it) return;
  const key = rxKey(ar);
  if (!marked.has(key)) marked.set(key, srsInit(rxCard(it)));
  marked.set(key, srsGrade(marked.get(key), g));
  save(); count();
}
const _rxUnval = it => (it.provenance || '').includes('needs-native-validation');
// Three honest states, not two. "Corroborated" means the same phrase is printed in the native
// teaching materials (pipeline/verify_content.py) — real evidence, but still not the same thing
// as a native speaker reviewing THIS app's wording, and the tooltip says so.
const _rxProv = it => {
  const p = it.provenance || '';
  if (p.includes('ref-corroborated'))
    return ['✓', 'rx-ok', 'Also printed in the native teaching materials' +
            (it.ref_src ? ' (' + it.ref_src + ')' : '') + ' — corroborated, though not a native review of this wording'];
  if (p.includes('lex-corroborated') || p.includes('maknuune-corroborated'))
    return ['·', 'rx-lex', 'Every word is confirmed in the ' + LANG.lex.name
            + ' lexicon; the phrasing is not native-checked'];
  return ['•', 'rx-flag', it.note
          ? 'Not native-checked, and the lexicon cannot confirm it: ' + it.note
          : 'Not native-checked, and the reference books don’t cover it'];
};

function reactionsSection(sub) {
  $('back').hidden = false;
  const c = rxCat(sub);
  return c ? reactionsCat(c) : reactionsHome();
}

function reactionsHome() {
  $('title').textContent = 'Reactions';
  let h = `<div class="lvl-row">${lvlTagFor('reaction', {})}
      <a class="lvl-what" href="#/plan/journey">what do these mean?</a></div>
    ${RX.intro ? `<p class="hint">${RX.intro}</p>` : ''}
    ${(() => { const its = RX.items || [];
      // Both kinds of corroboration, counted for whichever language is loaded. Arabic can point
      // at printed teaching materials; Hebrew has none in the repo, and its claim is the smaller
      // one it can actually make — every word of the phrase is a form the lexicon confirms.
      const p = i => i.provenance || '';
      const ref = its.filter(i => p(i).includes('ref-corroborated')).length;
      const lex = its.filter(i => p(i).includes('lex-corroborated')
                               || p(i).includes('maknuune-corroborated')).length;
      return `<div class="unval"><b>How checked is this?</b> ${ref ? `${ref} of ${its.length} are
        also printed in the native teaching materials in your reference library
        (<span class="rx-ok">✓</span>). ` : ''}${lex} have every word confirmed in the
        ${esc(LANG.lex.name)} lexicon (<span class="rx-lex">·</span>) — that is the spelling, not a
        native speaker reviewing this app's wording. The rest
        (<span class="rx-flag">•</span>) are idiomatic but unconfirmed; check the feel with a
        native speaker before leaning on the rarer ones.</div>`; })()}
    <div class="vtiles">`;
  h += (RX.cats || []).map(c => {
    const items = rxItemsIn(c.id), got = items.filter(r => rxGot(r.ar)).length;
    return `<button class="vtile wide" onclick="location.hash='/reactions/${c.id}'">
      <div class="vtile-h"><span class="vtile-t">${esc(c.en)}</span>
        <span class="vtile-n">${got}/${items.length}</span></div>
      <div class="vtile-s">${esc(c.blurb || '')}</div></button>`;
  }).join('');
  h += `</div>`;
  $('view').innerHTML = h;
}

// One category: browse the reactions, or drill them (cue → say → reveal + hear → grade).
let _rxMode = 'browse';
function reactionsCat(c) {
  $('title').textContent = c.en;
  const items = rxItemsIn(c.id);
  let h = `<p class="hint">${esc(c.blurb || '')}</p>
    <div class="ctl" style="margin-bottom:14px">
      <button class="tog" id="rx-browse" aria-pressed="${_rxMode !== 'drill'}" onclick="rxSetMode('browse','${c.id}')">Browse</button>
      <button class="tog" id="rx-drill" aria-pressed="${_rxMode === 'drill'}" onclick="rxSetMode('drill','${c.id}')">Drill</button>
    </div>`;
  h += _rxMode === 'drill' ? rxDrillHTML(items, c) : rxBrowseHTML(items);
  h += `<div class="sec" style="margin-top:22px">Other feelings</div><div class="ctl">` +
    (RX.cats || []).map(x => `<button class="tog"${x.id === c.id ? ' aria-pressed="true"' : ''}
        onclick="location.hash='/reactions/${x.id}'">${esc(x.en)}</button>`).join('') + `</div>`;
  $('view').innerHTML = h;
}
function rxSetMode(m, cat) { _rxMode = m; reactionsCat(rxCat(cat)); }

function rxBrowseHTML(items) {
  return items.map(it => `<div class="rx-card${rxGot(it.ar) ? ' got' : ''}">
      <div class="rx-top">
        <div class="rx-ar" dir="rtl">${arLive(it.ar)}</div>
        ${it.tr ? `<div class="rx-tr">${esc(it.tr)}</div>` : ''}
        <div class="rx-deck">${deckBtnHTML(rxKey(it.ar), `deckToggleRx('${cssq(it.ar)}')`)}</div>
        ${it.audio ? `<button class="say" onclick="playWord({kind:'reaction',audio:'${cssq(it.audio)}',lemma:'${cssq(rxKey(it.ar))}',vocalized:'${cssq(it.ar)}'})" aria-label="Play">${svg('spk')}</button>`
          : `<span class="rx-noaud">audio pending</span>`}
      </div>
      <div class="rx-en">${esc(it.en)} <span class="${_rxProv(it)[1]}" title="${esc(_rxProv(it)[2])}">${_rxProv(it)[0]}</span></div>
      <div class="rx-use">${esc(it.use || '')}</div>
      ${it.reply ? `<div class="rx-reply">reply: <span dir="rtl">${esc(it.reply)}</span></div>` : ''}
    </div>`).join('');
}

// Drill: one reaction at a time. Read the English, SAY it out loud, reveal to check + hear it, grade.
let _rxDrill = {items: [], i: 0, shown: false};
function rxDrillHTML(items, c) {
  _rxDrill = {items, i: 0, shown: false, cat: c.id};
  return `<div id="rx-drill-box">${rxCurrent()}</div>`;
}
function rxCurrent() {
  const d = _rxDrill, it = d.items[d.i];
  if (!it) return `<div class="pdone">✓ Went through all ${d.items.length}. They're in your flashcards now — review brings them back.</div>
    <div class="ctl" style="margin-top:10px;justify-content:center"><button class="tog go" onclick="location.hash='/vocab/review'">Review flashcards</button></div>`;
  return `<div class="rx-drill">
      <div class="rx-drill-n">${d.i + 1} / ${d.items.length}</div>
      <div class="rx-cue">${esc(it.en)}</div>
      ${d.shown
        ? `<div class="rx-ar big" dir="rtl">${arLive(it.ar)}</div>
           ${it.tr ? `<div class="rx-tr">${esc(it.tr)}</div>` : ''}
           ${it.audio ? `<button class="tog" onclick="playWord({kind:'reaction',audio:'${cssq(it.audio)}',lemma:'${cssq(rxKey(it.ar))}',vocalized:'${cssq(it.ar)}'})">🔊 Hear it</button>` : ''}
           <div class="rx-use">${esc(it.use || '')}</div>
           ${it.reply ? `<div class="rx-reply">reply: <span dir="rtl">${esc(it.reply)}</span></div>` : ''}
           <div class="ctl" style="margin-top:12px;justify-content:center">
             <button class="rv-g rv-g0" onclick="rxAnswer(0)">Not yet</button>
             <button class="rv-g rv-g2" onclick="rxAnswer(2)">Got it</button></div>`
        : `<p class="hint" style="text-align:center">Say it out loud, then reveal.</p>
           <div class="ctl" style="justify-content:center"><button class="tog go" onclick="rxReveal()">Show answer</button></div>`}
    </div>`;
}
function rxReveal() { _rxDrill.shown = true; const b = $('rx-drill-box'); if (b) b.innerHTML = rxCurrent();
  const it = _rxDrill.items[_rxDrill.i]; if (it && it.audio) playWord({kind: 'reaction', audio: it.audio, lemma: rxKey(it.ar), vocalized: it.ar}); }
function rxAnswer(g) {
  const it = _rxDrill.items[_rxDrill.i]; if (it) rxGrade(it.ar, g);
  _rxDrill.i++; _rxDrill.shown = false;
  const b = $('rx-drill-box'); if (b) b.innerHTML = rxCurrent();
}

// ---------- Sounds (Phase 0: get the ear and the mouth right first) ----------
// Six pronunciation contrasts of urban Palestinian (ق→ء, ع, ح/خ/ه, emphatics, ث/ذ→t/d, ē/ō) —
// matches pipeline/subdialect.py, the same model the voice uses. Leads with an articulation TIP,
// because for the throat sounds and emphatics a synthetic clip is less trustworthy than the note.
const SND = window.SOUNDS || {lessons: []};
const sndLesson = id => (SND.lessons || []).find(L => L.id === id);
let _sndA = null;
function sndPlay(src) { if (!src) return; try { (_sndA = _sndA || new Audio()).src = au(src); _sndA.playbackRate = SPEED; _sndA.play().catch(() => {}); } catch (e) {} }

function soundsSection(sub) {
  $('back').hidden = false;
  const L = sndLesson(sub);
  return L ? soundsLesson(L) : soundsHome();
}

function soundsHome() {
  $('title').textContent = 'Sounds';
  // The blurb and the caveat are the LANGUAGE'S, from its sounds.json: they name its letters and
  // its dialect, and a page that told a Hebrew learner about ع and Ramallah would be worse than
  // one that said nothing.
  let h = `<div class="lvl-row">${lvlTagFor('sound', {})}
      <a class="lvl-what" href="#/plan/journey">what do these mean?</a></div>
    ${SND.intro ? `<p class="hint">${SND.intro}</p>` : ''}
    ${SND.caveat ? `<div class="unval">${SND.caveat}</div>` : ''}
    <div class="vtiles">`;
  h += (SND.lessons || []).map(L => `<button class="vtile wide" onclick="location.hash='/sounds/${L.id}'">
      <div class="vtile-h"><span class="vtile-t">${esc(L.en)}</span><span class="vtile-n" dir="rtl">${esc(L.ar)}</span></div>
      <div class="vtile-s">${esc(L.target)}</div></button>`).join('');
  h += `</div>`;
  $('view').innerHTML = h;
}

const _sndCell = w => `${w.audio ? `<button class="say sm" onclick="sndPlay('${cssq(w.audio)}')" aria-label="Play">${svg('spk')}</button>` : ''}
    <span class="snd-ar" dir="rtl">${arLive(w.ar)}</span>
    <span class="snd-tr">${esc(w.tr)}</span>
    <span class="snd-gl">${esc(w.en)}</span>`;
function soundsLesson(L) {
  $('title').textContent = L.en;
  let h = `<div class="snd-target"><span dir="rtl">${esc(L.ar)}</span> · ${esc(L.target)}</div>
    <div class="note snd-tip">${esc(L.tip)}</div>
    <div class="sec">Minimal pairs & examples</div>`;
  // Some lessons pair words that sound ALIKE — Hebrew's א/ע, ת/ט, כּ/ק are one sound each, and
  // that is the lesson. Printing ≠ between them would teach the opposite of what the page says.
  h += L.examples.map(e => `<div class="snd-row">
      <div class="snd-cell">${_sndCell(e)}</div>
      ${e.contrast ? `<div class="snd-vs">${L.same ? '=' : '≠'}</div><div class="snd-cell dim">${_sndCell(e.contrast)}</div>` : ''}
    </div>`).join('');
  const anyAudio = L.examples.some(e => e.audio || (e.contrast && e.contrast.audio));
  if (!anyAudio) h += `<p class="hint" style="margin-top:12px">🔊 Audio is pending — for now, use the
     romanization and the tip. (Run <code>pipeline/sounds.py --audio</code> to add reference clips.)</p>`;
  else if (!L.same) h += earTestHTML(L);   // no ear test on homophones: that IS the lesson
  h += `<div class="sec" style="margin-top:22px">Other sounds</div><div class="ctl">` +
    (SND.lessons || []).map(x => `<button class="tog"${x.id === L.id ? ' aria-pressed="true"' : ''}
        onclick="location.hash='/sounds/${x.id}'">${esc(x.target)}</button>`).join('') + `</div>`;
  $('view').innerHTML = h;
}

// Test your ear: play one word of a minimal pair, choose which you heard. Only when both have audio.
let _ear = {pairs: [], i: 0, target: ''};
function earTestHTML(L) {
  const pairs = L.examples.filter(e => e.contrast && e.audio && e.contrast.audio);
  if (!pairs.length) return '';
  _ear = {pairs, i: 0, target: ''};
  return `<div class="sec" style="margin-top:22px">Test your ear</div>
    <p class="hint">Tap play, then choose which word you heard.</p>
    <div id="ear-box">${earCurrent()}</div>`;
}
function earCurrent() {
  const p = _ear.pairs[_ear.i];
  if (!p) return `<div class="pdone">✓ Nice ear.</div>`;
  const w = Math.random() < 0.5 ? p : p.contrast; _ear.target = w.ar;
  return `<div class="ear">
      <button class="tog go" onclick="sndPlay('${cssq(w.audio)}')">🔊 Play</button>
      <div class="ctl" style="margin-top:10px">
        <button class="tog" onclick="earPick('${cssq(p.ar)}')" dir="rtl">${esc(p.ar)}</button>
        <button class="tog" onclick="earPick('${cssq(p.contrast.ar)}')" dir="rtl">${esc(p.contrast.ar)}</button>
      </div><div id="ear-fb" class="hint" style="margin-top:8px"></div></div>`;
}
function earPick(ar) {
  const fb = $('ear-fb'); const ok = ar === _ear.target;
  if (fb) fb.innerHTML = ok ? '✓ Right' : `✗ It was <span dir="rtl">${esc(_ear.target)}</span>`;
  setTimeout(() => { _ear.i++; const b = $('ear-box'); if (b) b.innerHTML = earCurrent(); }, 950);
}

// ---------- The Dinner Table (Phase 6: multi-party listening — the north star) ----------
// Speaker-labeled Palestinian conversations. Read + follow now; once per-line audio exists (a
// distinct voice per speaker), the continuous player (reused paraPlayer) makes it real multi-voice
// listening. Written by Claude, flagged not native-checked.
const TBL = window.TABLE || {dialogues: []};
const tblById = id => (TBL.dialogues || []).find(d => d.id === id);
function tableSection(sub) {
  $('back').hidden = false;
  const dg = tblById(sub);
  return dg ? tableView(dg) : tableHome();
}
function tableHome() {
  $('title').textContent = 'The Dinner Table';
  let h = `<p class="hint">The north-star skill: following <b>several people at once</b> — the
    greetings, the hospitality, the small talk that fills a Palestinian family table. Read each
    conversation, check you followed it, then <b>retell it out loud</b>. Once audio is added you'll
    listen first and follow the room by ear. All of it is phase-7 material; <i>easier</i> and
    <i>hardest</i> order them within that.</p><div class="vtiles">`;
  h += (TBL.dialogues || []).map(dg => `<button class="vtile wide" onclick="location.hash='/table/${dg.id}'">
      <div class="vtile-h"><span class="vtile-t">${esc(dg.title.en)}</span>
        <span class="vtile-n">${{beginner: 'easier', intermediate: 'harder', advanced: 'hardest'}[dg.level] || esc(dg.level)}</span></div>
      <div class="vtile-s">${lvlTagFor('dialogue', dg)} ${esc(dg.scene)}</div></button>`).join('');
  h += `</div>`;
  $('view').innerHTML = h;
}
function tblToggleEn() { const el = document.querySelector('.tbl-lines'), btn = $('tblEn'); if (!el) return;
  const on = el.dataset.en !== 'on'; el.dataset.en = on ? 'on' : 'off'; if (btn) btn.setAttribute('aria-pressed', String(on)); }
function tableView(dg) {
  $('title').textContent = dg.title.en;
  const nameOf = {}; dg.cast.forEach(c => nameOf[c.id] = c.name);
  const clips = dg.lines.map(l => l.audio ? au(l.audio) : null).filter(Boolean);
  let h = `<div class="unval"><b>Not native-checked.</b> A spoken-Palestinian conversation written by
     Claude — for listening & comprehension, not for memorising the exact phrasing.</div>
    <div class="tbl-cast">${dg.cast.map(c => `<span><b dir="rtl">${esc(c.name)}</b> — ${esc(c.en)}</span>`).join('')}</div>
    <p class="hint">${esc(dg.scene)}</p>
    <div class="ctl"><button class="tog" id="tblEn" aria-pressed="false" onclick="tblToggleEn()">English</button></div>`;
  if (clips.length) h += `<div class="tbl-listen"><div class="pl-cap">Listen to the whole conversation</div>${paraPlayer()}</div>`;
  else h += `<p class="hint">🔊 Audio pending — <code>python3 pipeline/table.py --audio</code> adds per-speaker voices, and this becomes a real listening drill.</p>`;
  h += `<div class="tbl-lines" data-en="off">`;
  dg.lines.forEach(l => { h += `<div class="tbl-line">
      <div class="tbl-sp" dir="rtl">${esc(nameOf[l.sp] || l.sp)}</div>
      <div class="tbl-body"><div class="tbl-ar" dir="rtl">${arLive(l.ar)}</div><div class="tbl-en">${esc(l.en)}</div></div>
      ${l.audio ? `<button class="say sm" onclick="sndPlay('${cssq(l.audio)}')" aria-label="Play">${svg('spk')}</button>` : ''}
    </div>`; });
  h += `</div>`;
  if (dg.questions && dg.questions.length) {
    h += `<div class="sec" style="margin-top:22px">Did you follow it?</div>`;
    h += dg.questions.map(q => `<div class="tbl-q">
        <div class="tbl-q-q">${esc(q.q)}</div>
        <button class="tog" onclick="this.nextElementSibling.classList.toggle('show');this.textContent=this.nextElementSibling.classList.contains('show')?'Hide':'Show answer'">Show answer</button>
        <div class="tbl-q-a">${esc(q.a)}</div></div>`).join('');
  }
  h += `<div class="note" style="margin-top:18px"><b>Now retell it.</b> In your own words, out loud —
     who came, what they ate, what they talked about. Two minutes. That retelling <i>is</i> the skill.</div>
    <div class="sec" style="margin-top:20px">Other conversations</div><div class="ctl">` +
    (TBL.dialogues || []).map(x => `<button class="tog"${x.id === dg.id ? ' aria-pressed="true"' : ''}
        onclick="location.hash='/table/${x.id}'">${esc(x.title.en)}</button>`).join('') + `</div>`;
  $('view').innerHTML = h;
  const pel = $('view').querySelector('.player.para'); if (pel && clips.length) paraSetup(pel, clips);
}

// ---------- vocabulary / memorization (Anki SM-2) ----------
// ---------- merging duplicate cards -------------------------------------------------------
// Verbs now bank under one citation form, but cards added BEFORE that are still filed under
// whatever tense they were met in — قال and قالت as two cards, two schedules, one verb. New
// adds find them (deckKeyFor matches on the normalized lemma and on each card's own he_past),
// so nothing new duplicates; the existing pairs still sit there.
//
// This merges them, and it asks first. Two cards that a script thinks are one word occasionally
// are not — a wrong paradigm resolution from before findVerb was fixed could have filed an
// unrelated verb under a shared root — and a bad merge silently destroys review history that
// cannot be reconstructed. So it shows every group with what survives and what is lost, and
// merges only what you press.
//
// Phrase (¶) and reaction (®) cards are never grouped: two phrases sharing a verb are two
// different things to be able to say.
function dupGroups() {
  const by = new Map();
  for (const [k, c] of marked) {
    if (c.kind === 'phrase' || c.kind === 'reaction' || k[0] === '¶' || k[0] === '®') continue;
    const hp = cardHePast(c);
    const canon = arNorm((hp && hp.ar) || c.lemma || k);
    if (!canon) continue;
    if (!by.has(canon)) by.set(canon, []);
    by.get(canon).push([k, c]);
  }
  return [...by.entries()].filter(([, g]) => g.length > 1)
    .map(([canon, g]) => ({canon, cards: g.sort((a, b) => (b[1].reps || 0) - (a[1].reps || 0)
                                                       || (a[1].created || 0) - (b[1].created || 0))}));
}

// The survivor is the card with the most reps — that is where the real review history lives.
// Its schedule is kept, EXCEPT the due date, which becomes the earliest in the group: if one
// copy was still being learned you evidently didn't know the word in that form, so the merged
// card should come round again soon and prove itself rather than inheriting a 40-day interval.
// Lapses are summed, the earliest `created` wins, and the headword moves to the citation form.
function mergeGroup(canon) {
  const g = dupGroups().find(x => x.canon === canon); if (!g) return;
  const [[keepKey, keep]] = g.cards;
  const hp = cardHePast(keep);
  const merged = {...keep,
    lemma: (hp && hp.ar) || keep.lemma,
    vocalized: (hp && hp.ar) || keep.vocalized,
    caphi: (hp && hp.caphi) || keep.caphi,
    due: Math.min(...g.cards.map(([, c]) => c.due || 0)),
    lapses: g.cards.reduce((a, [, c]) => a + (c.lapses || 0), 0),
    created: Math.min(...g.cards.map(([, c]) => c.created || now())),
    merged_from: g.cards.map(([k]) => k).filter(k => k !== keepKey),
  };
  g.cards.forEach(([k]) => marked.delete(k));
  marked.set(merged.lemma, srsKeep(merged));
  save(); count();
}
// Keep an existing SM-2 state as-is (srsInit would reset it to a new card).
const srsKeep = c => ({ease: 2.5, interval: 0, reps: 0, lapses: 0, ...c});

function mergeAllDups() {
  const n = dupGroups().length;
  if (!n) return;
  if (!confirm('Merge all ' + n + ' group' + (n === 1 ? '' : 's') +
      '? Each keeps the card with the most reviews behind it and folds the rest into it.')) return;
  dupGroups().forEach(g => mergeGroup(g.canon));
  vocabMerge();
}

function vocabMerge() {
  $('title').textContent = 'Merge duplicates';
  const groups = dupGroups();
  if (!groups.length) {
    $('view').innerHTML = `<div class="empty"><div class="empty-t">Nothing to merge 🎉</div>
      <p>No two cards in your deck are the same word. Verbs added from here on bank under their
      “he” past, so a verb you meet in a new tense finds the card it already has.</p>
      <div class="ctl" style="justify-content:center"><button class="tog"
        onclick="location.hash='/vocab'">Back to Vocabulary</button></div></div>`;
    return;
  }
  const when = d => !d ? '—' : (d <= now() ? 'due now'
    : 'in ' + Math.max(1, Math.round((d - now()) / 864e5)) + 'd');
  let h = `<p class="hint">${groups.length} group${groups.length === 1 ? '' : 's'} look like the
    same word filed twice — usually a verb banked in two different tenses before verbs were
    canonicalised. The card with the most reviews survives and keeps its schedule; the merged
    card is re-dated to the earliest due in its group, so it comes round again soon rather than
    inheriting a long interval you may not have earned in that form.</p>
    <p class="hint"><b>Check each one before merging.</b> Merging deletes the other cards'
    review history, and that can't be undone.</p>
    <div class="ctl"><button class="tog go" onclick="mergeAllDups()">Merge all ${groups.length}</button></div>`;
  h += groups.map(g => `<div class="mg">
      <div class="mg-rows">${g.cards.map(([k, c], i) => `<div class="mg-row${i ? '' : ' keep'}">
        <span class="mg-ar" dir="rtl">${esc(c.vocalized || c.lemma)}</span>
        <span class="mg-gl">${esc(pretty(c.gloss) || '—')}</span>
        <span class="mg-st">${c.reps || 0} rep${(c.reps || 0) === 1 ? '' : 's'} · ${when(c.due)}</span>
        <span class="mg-tag">${i ? 'folded in' : 'kept'}</span></div>`).join('')}</div>
      <div class="ctl"><button class="tog" onclick="mergeGroup('${cssq(g.canon)}');vocabMerge()">Merge these</button></div>
    </div>`).join('');
  h += `<div class="ctl" style="margin-top:14px"><button class="tog"
    onclick="location.hash='/vocab'">Back to Vocabulary</button></div>`;
  $('view').innerHTML = h;
}

function vocabSection(sub, arg){
  $('back').hidden = false;
  if (sub === 'review') return vocabReview();
  if (sub === 'decks')  return vocabDecks();
  if (sub === 'deck')   return vocabDeck(arg);
  if (sub === 'browse') return vocabBrowse();
  if (sub === 'merge')  return vocabMerge();
  return vocabHome();
}

function vocabHome(){
  $('title').textContent = 'Vocabulary';
  const all = [...marked.values()], due = dueCards();
  const mature = all.filter(c => (c.interval || 0) >= 21).length;
  if (!all.length){
    $('view').innerHTML = `<div class="empty"><div class="empty-t">No words yet</div>
      <p>While you read a story or the news, tap any word you don’t know and hit
      <b>“Don’t know it.”</b> It becomes a flashcard here, and comes back for review on the
      schedule that makes it stick (the Anki method). Every card carries the word’s meaning,
      pronunciation, root, and the sentence you met it in.</p></div>`;
    return;
  }
  let h = `<div class="hero"><button class="big${due.length ? '' : ' warn'}"
      onclick="location.hash='/vocab/review'">
      <div class="k">Daily review</div>
      <div class="t">${due.length ? due.length + ' card' + (due.length===1?'':'s') + ' due' : 'All caught up'}</div>
      <div class="s">${due.length ? 'Grade each one Again / Hard / Good / Easy — spaced repetition does the rest.'
                                  : 'Nothing due right now. Come back later, or add more words while you read.'}</div>
    </button></div>`;
  h += `<div class="vstats">
     <div class="vstat"><b>${all.length}</b><span>cards</span></div>
     <div class="vstat"><b>${due.length}</b><span>due now</span></div>
     <div class="vstat"><b>${mature}</b><span>learned</span></div></div>`;
  h += `<div class="sec">Decks</div>`;
  h += decks.map(d => { const n = cardsInDeck(d.id).length,
                        dn = cardsInDeck(d.id).filter(c => (c.due||0) <= now()).length;
    return `<button class="card" onclick="location.hash='/vocab/deck/${d.id}'">
      <div class="en">${esc(d.name)}${d.id === activeDeck() ? ' <span class="pill on">active</span>' : ''}</div>
      <div class="meta"><span>${n} card${n===1?'':'s'}</span>${dn ? `<span style="color:var(--ochre)">${dn} due</span>` : ''}</div>
    </button>`; }).join('');
  h += `<p class="hint" style="margin-top:14px">Whole <b>phrases</b> stick better than single
     words. While reading, tap a word → <b>+ Phrase…</b> → tap the last word of the chunk.</p>`;
  const dups = dupGroups().length;
  if (dups) h += `<div class="mg-nudge">${dups} word${dups === 1 ? '' : 's'} in your deck
     ${dups === 1 ? 'is' : 'are'} filed twice — usually a verb banked in two tenses before verbs
     were canonicalised. <button class="tog" onclick="location.hash='/vocab/merge'">Review and merge</button></div>`;
  h += `<div class="ctl" style="margin-top:6px">
     <button class="tog" onclick="addPhraseManual()">+ Add a phrase</button>
     <button class="tog" onclick="location.hash='/vocab/decks'">Manage decks</button>
     <button class="tog" onclick="location.hash='/vocab/browse'">Browse all</button>
     <button class="tog" onclick="ankiExport()">Export to Anki</button></div>`;
  $('view').innerHTML = h;
}

// ---- SM-2 review flow ----
let _revq = null;
// Which way a review card faces. The two directions are not the same exercise:
//
//   ar  RECOGNITION  — see قهوة, recall "coffee". The easy direction. It builds the
//                      form-meaning link cheaply and is what reading and listening need.
//   en  PRODUCTION   — see "coffee", recall قهوة. The hard direction, and the only one that
//                      rehearses what your mouth has to do at a dinner table. Harder retrieval
//                      is also stronger retrieval, so the same card studied this way sticks
//                      better — it just costs more effort per rep and is discouraging on a
//                      word you only met yesterday.
//   mix RECOGNITION FIRST, THEN PRODUCTION — a card faces Arabic while it's new and flips to
//                      English once it has survived a few reps. This is the ordinary
//                      recommendation: learn it receptively, then make it produce.
//
// `mix` is the default. It is the direction that matches what this app is for — you cannot
// produce a word you don't yet recognise, and recognition alone never becomes speech — so the
// order is the teaching, not a preference. A deck that has never set this will start flipping
// its established cards to production; the toggle at the bottom of every review card changes
// it back in one tap, and the choice persists.
const RDIR_KEY = LKEY('rev.dir.v1');
// `ar` is the KEY, not the language: it means "the target language first", and it is a stored
// value in every existing deck, so it stays what it is. The labels are the pack's.
const _L = LANG.short;
const REV_DIRS = [
  ['ar',  _L + ' first', 'See the ' + _L + ', recall the English. Easier — good for new words and for reading.'],
  ['en',  'English first', 'See the English, say the ' + _L + '. Harder, and the direction that trains speaking.'],
  ['mix', _L + ' first, then English', 'New cards show ' + _L + '; once a card is established it flips to English — recognise it first, then learn to say it. This is the default.'],
];
const revDir = () => { try { return localStorage.getItem(RDIR_KEY) || 'mix'; } catch (e) { return 'mix'; } };
function setRevDir(v) {
  try { localStorage.setItem(RDIR_KEY, v); } catch (e) {}
  vocabReview();                                    // redraw the current card the new way round
}
// In `mix`, a card graduates to production once the SRS says it has stuck. `reps` is the
// card's own counter, so the flip is per-card rather than per-session — no card changes
// direction while you are looking at it.
const MIX_AFTER = 3;
function cardFaces(c) {
  const d = revDir();
  if (d !== 'mix') return d;
  return (c && (c.reps || 0) >= MIX_AFTER) ? 'en' : 'ar';
}

function vocabReview(){
  $('title').textContent = 'Review';
  if (!_revq) _revq = dueCards().sort((a,b)=>(a.due||0)-(b.due||0)).map(c => c.lemma);
  // drop any that are no longer due (e.g. graded away)
  while (_revq.length && !(marked.has(_revq[0]) && (marked.get(_revq[0]).due||0) <= now())) _revq.shift();
  if (!_revq.length){
    _revq = null;
    $('view').innerHTML = `<div class="empty"><div class="empty-t">Done for now 🎉</div>
      <p>You reviewed everything that was due. New cards and the ones you got wrong will come
      back later.</p><div class="ctl" style="justify-content:center"><button class="tog"
      onclick="location.hash='/vocab'">Back to Vocabulary</button></div></div>`;
    return;
  }
  const c = marked.get(_revq[0]);
  const total = dueCards().length;
  vocabCardView(c, false, total);
}
function vocabShow(){ vocabCardView(marked.get(_revq[0]), true, dueCards().length); }
function vocabAnswer(g){
  const lemma = _revq[0];
  marked.set(lemma, srsGrade(marked.get(lemma), g));
  save(); _revq.shift(); count(); vocabReview();
}
function vocabCardView(c, showing, remaining){
  const prev = srsPreview(c);
  const ex = c.example_ar ? `<div class="rv-ex" dir="rtl">${esc(c.example_ar)}</div>
      <div class="rv-exen">${esc(c.example_en || '')}</div>` : '';
  const isPh = c.kind === 'phrase';
  const face = cardFaces(c);
  const gloss = esc(pretty(c.gloss) || '—');
  const arabic = `<div class="rv-front${isPh ? ' rv-phrase' : ''}" ${isPh ? 'dir="rtl"' : ''}>${esc(c.vocalized || c.lemma)}
        <button class="say" onclick="playWord(marked.get('${cssq(c.lemma)}'))"
          aria-label="Pronounce">${svg('spk')}</button></div>`;
  let h = `<div class="rv-top">${remaining} to go${
    revDir() === 'mix' ? ` · <span class="rv-face">${face === 'en' ? 'producing' : 'recognising'}</span>` : ''}</div>
    <div class="rv-card">`;
  // Producing: the prompt is the English, and the pronounce button is deliberately absent —
  // hearing the word aloud IS the answer, so offering it here would hand the card away.
  h += face === 'en' && !showing
    ? `<div class="rv-ask">Say it in Palestinian</div><div class="rv-gl rv-gl-front">${gloss}</div>`
    : arabic;
  if (!showing){
    h += `<button class="rv-showbtn" onclick="vocabShow()">Show answer</button></div>`;
  } else {
    const hp = cardHePast(c);
    h += (face === 'en' ? arabic : '') +
      `<div class="rv-ph">${esc(c.caphi || '')}</div>
      ${face === 'en' ? '' : `<div class="rv-gl">${gloss}</div>`}
      ${hp ? hePastHTML(hp, 'rv-hepast') : ''}
      ${isPh
        ? (c.parts && c.parts.length
            ? `<div class="phw">${c.parts.map(p => `<span><b dir="rtl">${esc(p.ar)}</b>
                 ${esc(p.gloss)}</span>`).join('')}</div>`
            : `<div class="rv-root">your own phrase — not from a text</div>`)
        : `<div class="rv-root">root ${esc((c.root||'—').replace(/\./g,' · '))}</div>`}
      ${ex}${cardConjHTML(c)}</div>
      <div class="rv-grades">
        ${[['Again',0],['Hard',1],['Good',2],['Easy',3]].map(([lbl,g]) =>
          `<button class="rv-g rv-g${g}" onclick="vocabAnswer(${g})">
             <span>${lbl}</span><em>${prev[g]}</em></button>`).join('')}</div>`;
  }
  h += revDirHTML();
  $('view').innerHTML = h;
}

// Switchable mid-session, because which direction you want depends on the day as much as on
// the deck — and the blurb has to be there, since "Arabic first" and "English first" don't
// say which one is the hard one or what each is for.
function revDirHTML() {
  const d = revDir();
  return `<div class="rv-dir">
    <div class="rv-dir-h">Which side first</div>
    <div class="rv-dir-btns">${REV_DIRS.map(([id, label]) =>
      `<button class="tog" aria-pressed="${id === d}" onclick="setRevDir('${id}')">${esc(label)}</button>`).join('')}</div>
    <p class="rv-dir-w">${esc((REV_DIRS.find(x => x[0] === d) || [])[2] || '')}</p></div>`;
}

function vocabDecks(){
  $('title').textContent = 'Decks';
  let h = `<p class="hint">New words drop into the <b>active</b> deck. Tap a deck to make it
    active, rename, or remove it.</p>`;
  h += decks.map(d => { const n = cardsInDeck(d.id).length, act = d.id === activeDeck();
    return `<div class="card" style="cursor:default">
      <div class="en">${esc(d.name)} <span class="pill${act?' on':''}">${act?'active':n+' cards'}</span></div>
      <div class="ctl" style="margin-top:8px">
        ${act ? '' : `<button class="tog" onclick="setActiveDeck('${d.id}');route()">Make active</button>`}
        <button class="tog" onclick="renameDeck('${d.id}')">Rename</button>
        ${d.id==='default'?'':`<button class="tog" onclick="deleteDeck('${d.id}')">Delete</button>`}
      </div></div>`; }).join('');
  h += `<div class="ctl" style="margin-top:12px"><button class="tog go" onclick="newDeck()">+ New deck</button></div>`;
  $('view').innerHTML = h;
}
function newDeck(){ const name = prompt('Deck name:'); if (!name) return;
  const id = 'd' + now().toString(36); decks.push({id, name: name.trim(), created: now()});
  saveDecks(); setActiveDeck(id); route(); }
function renameDeck(id){ const d = decks.find(x=>x.id===id); if (!d) return;
  const name = prompt('Rename deck:', d.name); if (!name) return; d.name = name.trim(); saveDecks(); route(); }
function deleteDeck(id){ if (id==='default') return;
  const n = cardsInDeck(id).length;
  if (!confirm(`Delete “${deckName(id)}”` + (n?` and move its ${n} card(s) to “My words”?`:'?'))) return;
  for (const c of cardsInDeck(id)) marked.set(c.lemma, {...c, deck: 'default'});
  decks = decks.filter(d=>d.id!==id); if (activeDeck()===id) setActiveDeck('default');
  save(); saveDecks(); location.hash = '/vocab/decks'; }

function vocabDeck(id){ vocabCardList(deckName(id), cardsInDeck(id), id); }
function vocabBrowse(){ vocabCardList('All cards', [...marked.values()], null); }
function vocabCardList(title, list, deckId){
  $('title').textContent = title;
  list = list.slice().sort((a,b)=>(a.due||0)-(b.due||0));
  let h = deckId ? `<div class="ctl">${deckId===activeDeck()?'<button class="tog" aria-pressed="true">Active deck</button>'
      :`<button class="tog" onclick="setActiveDeck('${deckId}');route()">Make this the active deck</button>`}
      <button class="tog" onclick="location.hash='/vocab/decks'">All decks</button></div>` : '';
  h += `<div class="sec">${list.length} card${list.length===1?'':'s'}</div>`;
  h += list.map(c => { const due = (c.due||0) <= now(); const hp = cardHePast(c);
    return `<div class="vccard">
      <div class="vcc-h"><span class="vcc-ar"${c.kind === 'phrase' ? ' dir="rtl"' : ''}>${esc(c.vocalized || c.lemma)}</span>
        ${c.kind === 'phrase' ? '<span class="vcc-ph">phrase</span>' : ''}
        <button class="say" onclick="playWord(marked.get('${cssq(c.lemma)}'))" aria-label="Pronounce">${svg('spk')}</button>
        <span class="vcc-gl">${esc(pretty(c.gloss) || '—')}</span>
        <span class="vcc-due">${due ? 'due' : 'in ' + Math.max(0,Math.round(((c.due||0)-now())/864e5)) + 'd'}</span></div>
      ${hp ? hePastHTML(hp, 'vcc-hepast') : ''}
      ${c.example_ar ? `<div class="vcc-ex" dir="rtl">${esc(c.example_ar)}</div>` : ''}
      ${cardConjHTML(c)}
      <div class="ctl" style="margin-top:6px">
        <button class="tog" onclick="moveCard('${cssq(c.lemma)}')">Move</button>
        <button class="tog" onclick="delCard('${cssq(c.lemma)}')">Remove</button></div>
    </div>`; }).join('') || `<p class="hint">No cards here.</p>`;
  $('view').innerHTML = h;
}
function delCard(lemma){ if (!confirm('Remove this card?')) return; marked.delete(lemma); save(); count(); route(); }
function moveCard(lemma){
  const names = decks.map((d,i)=>`${i+1}. ${d.name}`).join('\n');
  const pick = prompt('Move to which deck?\n'+names); const idx = parseInt(pick,10)-1;
  if (isNaN(idx) || !decks[idx]) return;
  marked.set(lemma, {...marked.get(lemma), deck: decks[idx].id}); save(); route();
}
function ankiExport(){
  const rows = [...marked.values()].map(c =>
    [c.vocalized||c.lemma, pretty(c.gloss), c.caphi||'', c.root||'', c.example_ar||''].join('\t')).join('\n');
  if (!rows) return;
  navigator.clipboard.writeText(rows).then(() =>
    alert('Copied ' + marked.size + ' cards (tab-separated). In Anki: File → Import, set the field separator to Tab.')
  ).catch(() => { $('title').textContent='Export';
    $('view').innerHTML = '<div class="sec">Copy into Anki (Tab-separated)</div><pre class="cmd" style="white-space:pre-wrap">'+esc(rows)+'</pre>'; });
}

// ---------- My Plan (the study-plan scheduler) ----------
// A deterministic, client-side plan generator. It lays LEARNING-SYSTEM.md's 6-phase path
// onto YOUR weekly time + context, and emits a checkable daily task list that deep-links to
// real in-app activities (and clearly labeled external resources for the gaps).
//
// The model is a CONSUMABLE QUEUE, not a fixed date→task map: your phase and progress are
// driven by the MINUTES YOU ACTUALLY COMPLETE (the log), never by the calendar. That's what
// makes reflow automatic — miss a day and you simply haven't advanced; the finish line moves,
// nothing is lost, and no guilt-tripping "you're 40 tasks behind."
const CUR = window.CURRICULUM || {phases: [], activities: {}, external: {}, totalHours: 2000};
const PKEY = LKEY('plan.cfg.v1'), PLKEY = LKEY('plan.log.v1');
// `external` (the outside-resources toggles) postdates the first configs and arrives absent on
// old or partially-synced ones; buildDay reads it unguarded, so normalize it here rather than
// scattering `cfg.external &&` through every call site.
const planCfg = () => {
  try {
    const c = JSON.parse(localStorage.getItem(PKEY) || 'null');
    if (c && !c.external) c.external = {};
    return c;
  } catch (e) { return null; }
};
const savePlanCfg = c => { try { localStorage.setItem(PKEY, JSON.stringify(c)); } catch (e) {} };
const planLog = () => { try { return JSON.parse(localStorage.getItem(PLKEY) || '{}') || {}; } catch (e) { return {}; } };
const savePlanLog = l => { try { localStorage.setItem(PLKEY, JSON.stringify(l)); } catch (e) {} };

// ---- date helpers (parse ISO as LOCAL, so weekday math matches the user's calendar) ----
const isoToDate = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
const isofmt = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
const addDaysISO = (s, n) => { const d = isoToDate(s); d.setDate(d.getDate() + n); return isofmt(d); };
const daysBetween = (a, b) => Math.round((isoToDate(b) - isoToDate(a)) / DAY);
const WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const fmtMD = iso => { const d = isoToDate(iso); return MON[d.getMonth()] + ' ' + d.getDate(); };
const fmtMY = iso => { const d = isoToDate(iso); return MON[d.getMonth()] + ' ' + d.getFullYear(); };
const PHASE_COLOR = ['#6E7DB3', '#2F8E7E', '#C8912F', '#B4372A', '#7A5EA6', '#3E8EA6', '#B5643A'];

// ---------- what level is this? ----------
// Every piece of content in the plan can name its own difficulty the same way: the coarse band,
// the CEFR signpost, and the phase that serves it — "Beginner · A1 · Phase 1".
//
// The phase is DERIVED, never restated. Which phase first serves a pool is read off the mixes in
// curriculum.js, and grammar/verb levels come from the same grammarCap/verbTier arrays the plan
// gates on. So a tag cannot drift from what the plan actually does: change the curriculum and
// every label in the app moves with it.
let _poolPh = null;
function poolPhase(pool) {
  if (!_poolPh) {
    _poolPh = {};
    (CUR.phases || []).forEach((p, i) => (p.mix || []).forEach(sp => {
      if (sp.pool && _poolPh[sp.pool] == null) _poolPh[sp.pool] = i;
    }));
  }
  return _poolPh[pool] != null ? _poolPh[pool] : 0;
}
const _capPhase = (arr, need) => {                       // first phase whose cap reaches `need`
  const i = (arr || []).findIndex(c => c >= need);
  return i < 0 ? (CUR.phases || []).length - 1 : i;
};
const levelAt = i => {
  const n = Math.max(0, Math.min((CUR.levels || []).length - 1, i | 0));
  return Object.assign({phase: n}, (CUR.levels || [])[n] || {cefr: '—', band: '—'});
};
// The phase a piece of content belongs to. `what` is the content type; `it` the item.
function contentPhase(what, it) {
  switch (what) {
    case 'story':     return poolPhase((it.level || 'beginner'));
    case 'book':      return poolPhase((it.level || 'beginner'));
    case 'news':      return poolPhase('news');
    case 'unit':      return it.phase | 0;
    case 'reaction':  return poolPhase('reaction');
    case 'dialogue':  return poolPhase('dialogue');
    case 'sound':     return 0;                                      // phase 1 is the sound phase
    case 'listen':    return it.phase | 0;
    case 'grammar':   return _capPhase(CUR.grammarCap, (it.n | 0) + 1);   // n = 0-based position
    case 'verb':      return _capPhase(CUR.verbTier, it.tier || 2);
    default:          return it && it.phase != null ? it.phase | 0 : 0;
  }
}
// The chip. `small` drops the band for tight rows; `dot` shows the phase colour.
function lvlTag(phaseIdx, small) {
  // A level is a claim about a curriculum, and a language without one cannot make it. Hebrew
  // ships its verbs before its study plan, and the tag rendered as "— — Phase 1": three pieces
  // of furniture around no content.
  if (!(CUR.phases || []).length) return '';
  const L = levelAt(phaseIdx);
  return `<span class="lvl" title="${esc(L.band)} · CEFR ${esc(L.cefr)} · phase ${L.phase + 1} of ${CUR.phases.length} in your plan"
     style="--lc:${PHASE_COLOR[L.phase]}">${small ? '' : `<b>${esc(L.band)}</b>`}
     <i>${esc(L.cefr)}</i> <em>Phase ${L.phase + 1}</em></span>`;
}
const lvlTagFor = (what, it, small) => lvlTag(contentPhase(what, it), small);

// ---- progress: phases are measured in COMPLETED minutes, not dates ----
function phaseBounds() { let acc = 0; return CUR.phases.map(p => (acc += p.hours * 60)); }   // cumulative min at each phase end
function phaseIndexFor(min) { const b = phaseBounds(); for (let i = 0; i < b.length; i++) if (min < b[i]) return i; return b.length - 1; }
function phaseStartMin(i) { return i <= 0 ? 0 : phaseBounds()[i - 1]; }
function loggedMinutes() { const L = planLog(); let s = 0; for (const d in L) { const done = L[d].done || {}; for (const k in done) s += done[k] || 0; } return s; }
// baseMinutes seeds where the learner starts (from their self-placement), so an experienced
// user isn't put back at Phase 0. Real completed minutes accumulate on top.
function planProgressMin(cfg) { return (cfg && cfg.baseMinutes || 0) + loggedMinutes(); }
function curPhaseIndex(cfg) { return phaseIndexFor(planProgressMin(cfg)); }
function weeklyMin(cfg) { let s = 0; for (let i = 0; i < 7; i++) s += (cfg.hours[i] || 0) * 60; return s; }
// Projected calendar date at which cumulative practice reaches targetMin, at the current pace.
function projDateISO(cfg, targetMin) {
  const wk = weeklyMin(cfg); if (wk <= 0) return null;
  const remain = Math.max(0, targetMin - planProgressMin(cfg));
  return addDaysISO(todayISO(), Math.ceil(remain / (wk / 7)));
}

// ---- content progression: which texts you've worked through (so the plan walks a real path) ----
const CSEEN_KEY = LKEY('plan.seen.v1');
function contentSeen() { try { return new Set(JSON.parse(localStorage.getItem(CSEEN_KEY) || '[]')); } catch (e) { return new Set(); } }
function markSeen(id, on) { if (!id) return; const s = contentSeen();
  if (on) s.add(id); else s.delete(id); try { localStorage.setItem(CSEEN_KEY, JSON.stringify([...s])); } catch (e) {} }

// ---- content pools: resolve an abstract pool to a concrete, ORDERED list of content ----
const POOL_LABEL = {beginner: 'Beginner story', intermediate: 'Intermediate story', advanced: 'Advanced story'};
function planPool(pool) {
  if (pool === 'unit') return (LSN.units || []).map(u => ({id: 'lsn:' + u.id, title: 'Unit ' + u.n + ' — ' + u.title.en, link: '/lessons/' + u.id}));
  if (pool === 'reaction') return (RX.cats || []).map(c => ({id: 'rx:' + c.id, title: c.en + ' reactions', link: '/reactions/' + c.id}));
  if (pool === 'dialogue') return (TBL.dialogues || []).map(dg => ({id: 'tbl:' + dg.id, title: dg.title.en, link: '/table/' + dg.id}));
  // The shelf, in shelf order then chapter order — the same order the Books section shows.
  // Books were browsable and nothing else: a plan could send you to a story or the paper but
  // never to a chapter, so ten voiced books sat outside the daily path entirely.
  if (pool === 'book') return LIB.texts.filter(t => t.kind === 'book-chapter')
    .sort((a, b) => (a.shelf || 0) - (b.shelf || 0) || (a.chapter || 0) - (b.chapter || 0))
    .map(t => ({id: t.id, title: t.title.en, link: '/text/' + t.id}));
  if (pool === 'news') return LIB.texts.filter(t => t.kind === 'news')
    .sort((a, b) => (b.date || '').localeCompare(a.date || '')).map(t => ({id: t.id, title: t.title.en, link: '/text/' + t.id}));
  return storiesAt(pool).map(t => ({id: t.id, title: t.title.en, link: '/text/' + t.id}));   // ordered by id
}
// Serve content IN ORDER: the ord-th story you HAVEN'T done yet, with its position in the full set
// (so a task can say "Beginner story 4 of 30"). When everything's been read, cycle back for re-reading.
function poolPick(pool, ord) {
  const all = planPool(pool); if (!all.length) return null;
  const seen = contentSeen();
  const unseen = all.filter(x => !seen.has(x.id));
  const list = unseen.length ? unseen : all;
  const pick = list[((ord % list.length) + list.length) % list.length];
  return {...pick, pos: all.findIndex(x => x.id === pick.id) + 1, total: all.length, allSeen: !unseen.length};
}
// The phase's primary reading level — used for "study more" bonus content.
function phaseReadPool(phase) {
  const r = (phase.mix || []).find(sp => sp.act === 'read' && POOL_LABEL[sp.pool]);
  return r ? r.pool : 'beginner';
}

// The one study day of the week that carries a tutor session: the highest-budget day.
function weeklyTutorDay(cfg) { let best = -1, bestH = -1; for (let i = 0; i < 7; i++) if ((cfg.hours[i] || 0) > bestH) { bestH = cfg.hours[i] || 0; best = i; } return bestH > 0 ? best : -1; }
// One weekly consolidation day — the lowest-budget study day — leans on review over new material.
function weeklyReviewDay(cfg) { let best = -1, bestH = Infinity; for (let i = 0; i < 7; i++) { const h = cfg.hours[i] || 0; if (h > 0 && h < bestH) { bestH = h; best = i; } } return best; }

// ---- leveled walkers for grammar / verbs / videos (beginner → fluent) ----
// Each walks its ORDERED list and serves the next item you haven't done, capped by phase so
// difficulty ramps. `seen` keys are namespaced (g:/v:/w:) so they never collide with story ids.
const GRAM_LIST = () => GRAM.map((l, i) => ({key: 'g:' + l.id, id: l.id, title: l.title, link: '/grammar/' + l.id}));
// Difficulty is the pack's judgement, not a shared table: Arabic sequences verbs by weak
// class, Hebrew by binyan at least as much as by gzara. See LANG.verb.tier.
let _verbPlan = null;
function verbPlan() {
  if (_verbPlan) return _verbPlan;
  const list = VB.filter(v => v.hasConj && (v.gloss || '').trim());
  list.sort((a, b) => (b.core ? 1 : 0) - (a.core ? 1 : 0)                 // core verbs first
    || LANG.verb.tier(a) - LANG.verb.tier(b)               // then easiest weak class
    || (a.form === 'I' ? 0 : 1) - (b.form === 'I' ? 0 : 1)               // then Form I before derived
    || (a.gloss || '').localeCompare(b.gloss || ''));
  _verbPlan = list.map(v => ({key: verbKey(v), i: v._i, title: v.gloss || v.lemma,
    ar: (verbCite(v) || {}).ar || v.lemma, weak: v.weak, tier: LANG.verb.tier(v), link: '/verb/' + v._i}));
  return _verbPlan;
}
// Serve the ord-th not-yet-done item from a namespaced list; cycle back once all are seen (mirrors poolPick).
function walkPick(items, ord, seen) {
  if (!items.length) return null;
  const unseen = items.filter(x => !seen.has(x.key));
  const list = unseen.length ? unseen : items;
  const pick = list[((ord % list.length) + list.length) % list.length];
  return {...pick, pos: items.findIndex(x => x.key === pick.key) + 1, total: items.length, allSeen: !unseen.length};
}
function pickGrammar(phaseIndex, ord) {
  const cap = (CUR.grammarCap || [])[Math.min(phaseIndex, 6)] || GRAM.length;
  return walkPick(GRAM_LIST().slice(0, cap), ord || 0, contentSeen());
}
const SND_LIST = () => (SND.lessons || []).map(L => ({key: 'snd:' + L.id, id: L.id, title: L.en, link: '/sounds/' + L.id}));
function pickSound(ord) { return walkPick(SND_LIST(), ord || 0, contentSeen()); }
function pickVerb(phaseIndex, ord) {
  const tier = (CUR.verbTier || [])[Math.min(phaseIndex, 6)] || 3;
  return walkPick(verbPlan().filter(v => v.tier <= tier), ord || 0, contentSeen());
}
// Same walk as the videos: only episodes at or below your phase, in order, advancing via seen.
function pickListen(phaseIndex, ord) {
  const list = LISTEN.filter(v => (v.phase || 0) <= phaseIndex)
    .map(v => ({key: 'ls:' + v.slug, slug: v.slug, title: v.title, link: '/listening/' + v.slug}));
  return walkPick(list, ord || 0, contentSeen());
}

function pickVideo(phaseIndex, ord) {
  const list = VIDEOS.filter(v => (v.phase || 0) <= phaseIndex)
    .map(v => ({key: 'w:' + v.slug, slug: v.slug, title: v.title, n: v.n, link: '/videos/' + v.slug}));
  return walkPick(list, ord || 0, contentSeen());
}

// ---- spaced re-exposure for grammar & verbs (SRS already handles vocab) ----
// When you first complete a lesson/verb we remember the date; the generator then resurfaces it
// as a short "review" task after 2, then 7, then 21 days — the expanding intervals memory wants.
const PRKEY = LKEY('plan.review.v1');
function planReview() { try { return JSON.parse(localStorage.getItem(PRKEY) || '{}') || {}; } catch (e) { return {}; } }
function savePlanReview(r) { try { localStorage.setItem(PRKEY, JSON.stringify(r)); } catch (e) {} }
function noteReview(key) { if (!key) return; const r = planReview();
  if (!r[key]) { r[key] = {first: todayISO(), last: todayISO(), reps: 0}; savePlanReview(r); } }
function advanceReview(key, forward) { const r = planReview(), it = r[key]; if (!it) return;
  it.reps = Math.max(0, (it.reps || 0) + (forward ? 1 : -1)); if (forward) it.last = todayISO(); savePlanReview(r); }
function dueReviewKeys(dateISO) {
  const r = planReview(), iv = CUR.reviewDays || [2, 7, 21], out = [];
  for (const k in r) { const it = r[k], n = it.reps || 0; if (n >= iv.length) continue;
    if (daysBetween(it.last || it.first, dateISO) >= iv[n]) out.push(k); }
  return out;                                            // grammar (g:) and verb (v:) keys due for review
}
// Build a short review task from a due key.
function reviewTaskFor(key, k) {
  const isG = key.startsWith('g:');
  const t = {id: 'rv-' + k, act: isG ? 'grammar' : 'verbs', label: isG ? 'Grammar review' : 'Verb review',
    instr: 'You met this before — recall it first, then open to check. Spacing is what makes it stick.',
    builds: 'Spaced review', minutes: 8, order: 2, source: 'inapp', speak: false, ideal: 'at a desk',
    review: true, rkey: key, cid: key};
  if (isG) { const g = gramById(key.slice(2)); if (g) { t.title = 'Review — ' + g.title; t.link = '/grammar/' + g.id; } }
  else { const v = VB[+key.slice(2)]; if (v) { t.title = 'Review verb — ' + (v.gloss || v.lemma); t.link = '/verb/' + (+key.slice(2)); } }
  return t.title ? t : null;
}

// ---- the generator: one day → an ordered, budget-fitted task list ----
// Pure given (cfg, phaseIndex, dateISO, dueCount): same inputs → same plan (deterministic).
// dueCount: number of SRS cards due (real for today); pass null for future days to keep review visible.
function buildDay(cfg, phaseIndex, dateISO, dueCount) {
  const ph = CUR.phases[phaseIndex] || CUR.phases[CUR.phases.length - 1] || {mix: [], name: '—'};
  const wd = isoToDate(dateISO).getDay();
  const totalMin = Math.round((cfg.hours[wd] || 0) * 60);
  if (totalMin <= 0) return {rest: true, tasks: [], phase: ph, totalMin: 0, phaseIndex};
  const carAvail = !!(cfg.car && cfg.car.has && (cfg.car.days || []).includes(wd));
  const speakAvail = carAvail || cfg.speakHome;
  const tutorDay = weeklyTutorDay(cfg);

  const base = ph.mix.filter(sp => {
    const A = CUR.activities[sp.act] || {};
    if (sp.act === 'srs' && dueCount === 0) return false;                 // nothing due today → skip review
    if (sp.src === 'external') {
      if (sp.act === 'course' || sp.act === 'sound') return !!(cfg.external.languageTransfer || cfg.external.pimsleur);
      // The Real Arabic catalogue is always available (it's just links), so listening no longer
      // depends on the podcasts toggle — that only decides whether we ALSO suggest going wider.
      if (sp.act === 'listen') return true;
      if (sp.act === 'tutor') return true;   // in-app Ask a Tutor is always available (a real tutor is a bonus)
    }
    if (A.speak && !speakAvail && sp.act !== 'tutor') return false;       // no voice slot → drop speaking (tutor is the honest fallback)
    if (sp.cadence === 'weekly' && wd !== tutorDay) return false;         // tutor ~once a week
    return true;
  }).map(sp => {
    // Placement-driven tilt: a few minutes a day move toward the assessed weakest skill and
    // off the strongest. Small and bounded — the phase mix stays the plan; this is a lean.
    const asr = cfg.assess; if (!asr || !asr.skills) return sp;
    const accOf = s => { const k = asr.skills[s]; return k && k.n >= 2 ? k.ok / k.n : null; };
    const rated = (AS.skills || []).filter(s => accOf(s) != null)
      .sort((a, b) => accOf(a) - accOf(b));
    if (rated.length < 2 || accOf(rated[0]) === accOf(rated[rated.length - 1])) return sp;
    const nudge = AS.nudgeMin || 5;
    if ((AS.skillActs[rated[0]] || []).includes(sp.act)) return {...sp, min: sp.min + nudge};
    if ((AS.skillActs[rated[rated.length - 1]] || []).includes(sp.act)) return {...sp, min: Math.max(5, sp.min - nudge)};
    return sp;
  });

  // Cycle the mix to fill the day's budget. A phase-mix is one ~session's worth; a longer day
  // repeats it, pulling FRESH content each time (new story, etc.), capped per activity so we
  // don't schedule eight identical reads or a second tutor. Short early phases may not fill a
  // long day — that's honest (you shouldn't cram 3h of sound drills), and we say so via `banked`.
  const CAPS = {course: 2, sound: 2, encode: 1, tutor: 1, srs: 1, grammar: 1, verbs: 1, watch: 1, read: 5, listen: 3, shadow: 3, drill432: 3, produce: 3};
  const chosen = []; const cnt = {}; let planned = 0;
  for (let pass = 0; pass < 9 && planned < totalMin; pass++) {
    let addedThisPass = false;
    for (const sp of base) {
      if (planned >= totalMin) break;
      if ((cnt[sp.act] || 0) >= (CAPS[sp.act] || 3)) continue;
      chosen.push(sp); cnt[sp.act] = (cnt[sp.act] || 0) + 1; planned += sp.min; addedThisPass = true;
    }
    if (!addedThisPass) break;                                            // everything capped out
  }

  chosen.sort((a, b) => (CUR.activities[a.act].order) - (CUR.activities[b.act].order));
  const tasks = []; let used = 0, k = 0;
  const readOrd = {};                                        // per-pool sequential index for READING
  const seenKeys = new Set();                                // avoid duplicate in-app items in one day
  for (const sp of chosen) {
    const remaining = totalMin - used;
    if (remaining < 5) break;
    let ord = 0;
    if (sp.pool) {                                           // reading walks the list in order; shadow/4-3-2
      if (sp.act === 'read') { ord = readOrd[sp.pool] || 0; readOrd[sp.pool] = ord + 1; }
      else ord = 0;                                          // pair with the day's current (first) story
    }
    const t = resolveTask(cfg, sp, ord, k, Math.min(sp.min, remaining), carAvail, phaseIndex);
    // Never schedule the same item twice in one day — same in-app content, same external resource
    // (e.g. two "Pimsleur" rows), or the same open-ended task ("talk about your day").
    const key = t.act + '|' + (t.link || t.url || t.title || '');
    if (seenKeys.has(key)) continue;
    seenKeys.add(key);
    k++; tasks.push(t); used += t.minutes;
  }
  const banked = totalMin - used >= 20 ? totalMin - used : 0;             // unfilled minutes at this phase
  return {rest: false, tasks, phase: ph, totalMin, usedMin: used, banked, phaseIndex, spoken: tasks.some(t => t.speak)};
}

// ---- freeze the day: build ONCE, then rehydrate ----
// The user's rule: today's list is fixed. Completing an item checks it off and it stays done —
// it never swaps in a new one. So the first time a date is opened we generate it, fold in any due
// spaced-review + the weekly consolidation, and STORE the snapshot under L[date].day; every later
// render reads that snapshot. Content only advances across days (a fresh date builds the next
// items from what's still unseen — a missed item simply reappears tomorrow: reflow, for free).
function getDay(cfg, dateISO, dueCount) {
  const L = planLog();
  if (L[dateISO] && L[dateISO].day) return L[dateISO].day;           // frozen — rehydrate
  const day = buildDay(cfg, curPhaseIndex(cfg), dateISO, dueCount);
  if (!day.rest) {
    // spaced review: 1 due item on a normal day, up to 3 on the weekly consolidation day.
    const isReviewDay = weeklyReviewDay(cfg) === isoToDate(dateISO).getDay();
    const due = dueReviewKeys(dateISO);
    const nRev = Math.min(isReviewDay ? 3 : 1, due.length);
    const revs = [];
    for (let r = 0; r < nRev; r++) { const rt = reviewTaskFor(due[r], 'r' + r); if (rt) revs.push(rt); }
    day.tasks = revs.concat(day.tasks);
    day.tasks.sort((a, b) => (a.order || 3) - (b.order || 3));
    day.review = isReviewDay;
    day.totalMin += revs.reduce((s, t) => s + t.minutes, 0);
  }
  // Persist only real days (today/past). Future calendar projections stay dynamic.
  if (dateISO <= todayISO()) {
    const d = L[dateISO] || (L[dateISO] = {done: {}});
    d.day = day;
    for (const kk in L) if (kk !== dateISO && L[kk] && L[kk].day) delete L[kk].day;   // keep the log small
    savePlanLog(L);
  }
  return day;
}

// Turn a phase-mix spec into a concrete, linkable task. `ord` = which item in a content pool.
function resolveTask(cfg, sp, ord, k, minutes, carAvail, phaseIndex) {
  if (phaseIndex == null) phaseIndex = curPhaseIndex(cfg);
  const A = CUR.activities[sp.act] || {};
  const t = {id: 'k' + k + '-' + sp.act, act: sp.act, label: A.label, instr: A.instr,
    builds: A.builds, minutes, order: A.order || 3, source: sp.src, speak: !!A.speak,
    ideal: A.slot === 'car' ? (carAvail ? 'in the car' : 'somewhere you can speak')
      : A.slot === 'desk' ? 'at a desk' : A.slot === 'break' ? 'on a break' : 'in the evening'};
  // The tutor conversation now has an in-app home: Ask a Tutor, primed on spoken Palestinian.
  // Point the task there and fold in the "what you couldn't say" loop; a real tutor stays the
  // gold-standard bonus when they have one.
  // Listening resolves to a NAMED episode from the Real Arabic catalogue rather than the old
  // "pick a short episode" search link — a real next thing, walked in order like the stories.
  if (sp.act === 'listen') {
    const pick = pickListen(phaseIndex, ord);
    if (pick) {
      const ep = lsById(pick.slug) || {};
      t.title = pick.title; t.link = pick.link; t.cid = pick.key; t.source = 'inapp';
      t.seq = 'Real Arabic · ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : '');
      t.note = 'Native speed, unscripted. Listen once without the transcript, then again with it.' +
        (cfg.external && cfg.external.podcasts ? ' Then widen out to your own podcasts.' : '');
      return t;
    }
  }
  if (sp.act === 'tutor') {
    t.title = 'Ask a Tutor — the things you couldn’t say';
    t.link = '/tutor'; t.source = 'inapp';
    t.instr = 'Open Ask a Tutor and work through what you got stuck on this week. Tap “Save” on any phrase it gives you to send it to your flashcards.';
    t.note = (cfg.external && cfg.external.tutor)
      ? 'And when you can, a live session with a real Palestinian tutor is the gold standard.'
      : '';
    return t;
  }
  if (sp.src === 'external') {
    // With both courses enabled the first audio block of the day goes to Pimsleur — it's the
    // one being paid for and it tracks a specific lesson — and Language Transfer takes the
    // second, instead of Language Transfer silently winning every slot as it used to.
    const bothCourses = cfg.external.languageTransfer && cfg.external.pimsleur;
    const key = (sp.act === 'course' || sp.act === 'sound')
      ? (bothCourses ? (ord % 2 === 0 ? 'pimsleur' : 'languageTransfer')
         : (cfg.external.pimsleur ? 'pimsleur' : 'languageTransfer'))
      : sp.res;
    const R = CUR.external[key] || {};
    t.title = R.name || A.label; t.url = R.url; t.note = R.note;
    // Name the actual lesson so the task is "do this next thing", not "do some Pimsleur".
    if (key === 'pimsleur' && pimOn()) {
      t.title = 'Pimsleur — ' + pimLabel();
      t.seq = 'Eastern Arabic (Levantine) · lesson ' + (pim().lesson || 1) + ' of ' + PIM_LESSONS;
      t.pim = true;
      t.note = 'Listen in the Pimsleur app, then tick this off — the app moves you to the next lesson.';
    }
  } else if (sp.pool) {
    const pick = poolPick(sp.pool, ord);
    if (pick) {
      // Speaking activities open the Speak view (4/3/2 + shadow); reading opens the reader.
      // Reaction chunks already ARE a speaking drill (cue→say→check), so leave those as-is.
      let link = pick.link;
      if ((sp.act === 'shadow' || sp.act === 'drill432') && link.startsWith('/text/'))
        link = link.replace('/text/', '/speak/');
      t.title = pick.title; t.link = link;
      if (sp.act === 'read' || sp.pool === 'reaction' || sp.pool === 'dialogue' || sp.pool === 'unit'
          || sp.pool === 'book') t.cid = pick.id;   // advances the systematic path
      if (POOL_LABEL[sp.pool]) t.seq = POOL_LABEL[sp.pool] + ' ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : '');
      else if (sp.pool === 'news') t.seq = 'Latest news';
      else if (sp.pool === 'book') t.seq = 'Chapter ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : '');
      else if (sp.pool === 'reaction') t.seq = 'Reactions · set ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : '');
      else if (sp.pool === 'dialogue') t.seq = 'Conversation ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : '');
      else if (sp.pool === 'unit') t.seq = 'Lesson unit ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : '');
    } else { t.title = A.label; t.note = 'No ' + sp.pool + ' content loaded yet.'; }
  } else if (sp.act === 'srs') {
    t.title = 'Review your due flashcards'; t.link = '/vocab/review';
  } else if (sp.act === 'sound') {
    const pick = pickSound(ord);
    if (pick) { t.title = pick.title; t.link = pick.link; t.cid = pick.key;
      t.seq = 'Sound ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : ''); }
    else { t.title = 'Sound & ear drill'; t.link = '/sounds'; }
  } else if (sp.act === 'grammar') {
    const pick = pickGrammar(phaseIndex, ord);
    if (pick) { t.title = pick.title; t.link = pick.link; t.cid = pick.key; t.rkey = pick.key;
      t.seq = 'Grammar ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : ''); }
    else { t.title = 'Grammar lesson'; t.link = '/grammar'; }
  } else if (sp.act === 'verbs') {
    const pick = pickVerb(phaseIndex, ord);
    if (pick) { t.title = 'Verb — ' + pick.title + (pick.ar ? ' · ' + pick.ar : ''); t.link = pick.link;
      t.cid = pick.key; t.rkey = pick.key;
      t.seq = (WEAK_INFO[pick.weak] ? WEAK_INFO[pick.weak][0] : 'Verb') + ' · ' + pick.pos + ' of ' + pick.total + (pick.allSeen ? ' · revisiting' : ''); }
    else { t.title = 'Study a verb'; t.link = '/verbs'; }
  } else if (sp.act === 'watch') {
    const pick = pickVideo(phaseIndex, ord);
    if (pick) { t.title = pick.title; t.link = pick.link; t.cid = pick.key; t.source = 'inapp';
      t.seq = 'Video playlist · ' + pick.n + ' clip' + (pick.n === 1 ? '' : 's') + (pick.allSeen ? ' · revisiting' : ''); }
    else { t.title = 'Watch a lesson'; t.link = '/videos'; }
  } else if (sp.act === 'produce') {
    t.title = 'Talk about your day, out loud';
  } else if (sp.act === 'encode') {
    t.title = 'Meet a few new chunks before bed';
  } else {
    t.title = A.label;
  }
  return t;
}

// ---- section entry ----
function planSection(sub, arg) {
  $('back').hidden = false;
  if (sub === 'new') return arg === 'assess' ? assessView() : planIntake();
  if (!planCfg()) return planWelcome();
  if (sub === 'calendar') return planCalendar();
  if (sub === 'journey') return planJourney();
  if (sub === 'dashboard') return planDashboard();
  return planToday();
}

// ---- streak: consecutive days with at least one completed task (frequency is the method) ----
function planStreak() {
  const L = planLog();
  const doneOn = day => { const r = L[day]; return !!(r && r.done && Object.keys(r.done).length); };
  let d = todayISO(), n = 0;
  if (!doneOn(d)) d = addDaysISO(d, -1);        // today not started yet → streak runs up to yesterday
  while (doneOn(d)) { n++; d = addDaysISO(d, -1); }
  return n;
}
const streakChip = () => { const s = planStreak(); return s > 0 ? `<span class="streak">🔥 ${s}-day streak</span>` : ''; };

// ---- daily warm-up: recall a few of YESTERDAY'S items before meeting new material ----
let _warmEx = [];
function planWarmupHTML(date, doneMap) {
  const y = addDaysISO(date, -1), yr = planLog()[y];
  if (!yr || !yr.day) return '';
  _warmEx = planExerciseItems(yr.day, y).slice(0, 3);
  if (!_warmEx.length) return '';
  const done = 'warmup' in doneMap;
  let h = `<div class="warmup${done ? ' done' : ''}">
    <div class="warmup-h"><button class="pcheck" onclick="planToggle('${date}','warmup',3,'',0,'',0)" aria-label="Mark done">${done ? '✓' : ''}</button>
      <span class="warmup-t">Warm-up — recall yesterday</span><span class="pmin">3m</span></div>
    <p class="hint" style="margin:2px 0 8px 34px">Say each in ${esc(LANG.name)} from memory first — a 30-second retrieval primes today.</p>`;
  h += _warmEx.map((it, i) => `<div class="wex" style="margin-left:34px">
      <span class="wex-q">${esc(it.en)}</span>
      <button class="tog" onclick="planWarmShow(${i})">Show</button>
      <span class="wex-a" id="wex-a-${i}" dir="rtl"></span></div>`).join('');
  return h + '</div>';
}
function planWarmShow(i) { const it = _warmEx[i], el = $('wex-a-' + i); if (it && el) el.textContent = it.ar; }

// ---- record yourself: produce speech, play it back. Local only — nothing is uploaded or kept. ----
let _rec = {mr: null, chunks: [], url: null, on: false};
function planRecordHTML(date, doneMap, topic) {
  const done = 'record' in doneMap;
  return `<div class="recard${done ? ' done' : ''}">
    <div class="warmup-h"><button class="pcheck" onclick="planToggle('${date}','record',10,'',0,'',0)" aria-label="Mark done">${done ? '✓' : ''}</button>
      <span class="warmup-t">Record yourself</span><span class="pmin">10m</span></div>
    <p class="hint" style="margin:2px 0 8px 34px">${esc(topic)} — record ~30–60s out loud, then play it back and notice what you couldn't say. Stays on your device; nothing is uploaded.</p>
    <div class="ctl" style="margin-left:34px">
      <button class="tog go" id="recBtn" onclick="recToggle()">● Record</button>
      <audio id="recAudio" controls style="display:none;vertical-align:middle"></audio></div>
    <div class="pt-note" id="recNote" style="margin-left:34px;display:none"></div></div>`;
}
async function recToggle() {
  const btn = $('recBtn'), au = $('recAudio'), note = $('recNote');
  if (_rec.on && _rec.mr) { _rec.mr.stop(); return; }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    _rec.chunks = []; _rec.mr = new MediaRecorder(stream);
    _rec.mr.ondataavailable = e => { if (e.data.size) _rec.chunks.push(e.data); };
    _rec.mr.onstop = () => { stream.getTracks().forEach(t => t.stop()); _rec.on = false;
      if (_rec.url) URL.revokeObjectURL(_rec.url);
      _rec.url = URL.createObjectURL(new Blob(_rec.chunks, {type: 'audio/webm'}));
      if (au) { au.src = _rec.url; au.style.display = 'inline-block'; }
      if (btn) { btn.textContent = '● Record again'; btn.classList.remove('rec-on'); } };
    _rec.mr.start(); _rec.on = true;
    if (btn) { btn.textContent = '■ Stop'; btn.classList.add('rec-on'); }
    if (note) note.style.display = 'none';
  } catch (e) {
    if (note) { note.style.display = 'block'; note.textContent = 'Microphone unavailable — allow mic access, or just do it out loud and tick it off.'; }
  }
}

function planWelcome() {
  $('title').textContent = 'My Plan';
  // The destination and the phase list are the CURRICULUM's, not this file's. Arabic runs seven
  // phases to a family dinner; Hebrew runs three, to reading the paper, because that is how much
  // content exists — and a page that named Arabic's path to a Hebrew learner would be promising
  // four phases the app cannot serve.
  const ph = CUR.phases || [];
  const path = ph.map(p => esc(p.name)).join(' → ');
  const nWord = ['no', 'a one', 'a two', 'a three', 'a four', 'a five', 'a six', 'a seven'][ph.length] || ('a ' + ph.length);
  $('view').innerHTML = `<div class="hero"><div class="big">
      <div class="k">Your path to the table</div>
      <div class="t">A study plan built around your week</div>
      <div class="s">Tell us how much time you have and where (a commute? somewhere you can talk out
      loud?) and we’ll turn it into a daily checklist — reading, speaking drills, flashcards and a
      few great outside resources — that walks you from the sounds of ${esc(LANG.name)}
      ${esc(LANG.planGoal)}. Miss a day and it quietly reflows; nothing is lost.</div>
    </div></div>
    <div class="note"><b>How it works.</b> The plan follows ${nWord}-phase path — ${path} —
    grounded in how memory actually works:
    spaced repetition, retrieval out loud, and whole chunks over lone words. Your progress is measured
    in the minutes you actually finish, so the schedule bends to your real life instead of shaming you.</div>
    <div class="ctl" style="justify-content:center;margin-top:18px">
      <button class="tog go" style="font-size:14px;padding:11px 20px" onclick="location.hash='/plan/new'">Create my plan →</button>
    </div>`;
}

// ---- intake wizard ----
// ============ Placement assessment — find where you are before the plan builds ============
// An adaptive ~8-minute test at the start of "Build my plan". Every item is sampled at
// runtime from content that is already verified: Maknuune-verified corpus words (with their
// generated audio), engine-verified conjugation cells, grammar examples MINED from the corpus,
// and Maknuune-corroborated reactions. Nothing unverified is ever shown as a "correct answer".
// The ladder: rounds of one item per skill; a strong round moves the tier up, a weak one down;
// the tier you converge on decides the phase your plan starts in, and the per-skill accuracy
// tilts each day's minutes toward your weakest skill.
const ASSESS_KEY = LKEY('plan.assess.v1');
const AS = window.ASSESS || {};
function assessResult() { try { return JSON.parse(localStorage.getItem(ASSESS_KEY) || 'null'); } catch (e) { return null; } }
function assessClear() {
  try { localStorage.removeItem(ASSESS_KEY); } catch (e) {}
  const cfg = planCfg(); if (cfg && cfg.assess) { cfg.assess = null; savePlanCfg(cfg); }
  route();
}
const _asShuf = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const _asPick = a => a[Math.floor(Math.random() * a.length)];
const _asGloss = g => pretty(g).split('·')[0].trim();

// Indices built once per session from the loaded data. ranked = corpus lemmas by frequency
// (verified words only); sents = sentences with audio for tier-3/4 listening; rx = the
// corroborated reactions (the only ones clean enough to be test answers).
let _asIdx = null;
function assessIndex() {
  if (_asIdx) return _asIdx;
  const freq = new Map();
  (LIB.texts || []).forEach(t => (t.sentences || []).forEach(s => (s.words || []).forEach(w => {
    if (!w.lemma || !w.gloss || !String(w.provenance || '').startsWith('maknuune')) return;
    const e = freq.get(w.lemma) || {n: 0, gloss: w.gloss, voc: w.vocalized || w.lemma};
    e.n++; freq.set(w.lemma, e);
  })));
  const ranked = [...freq.entries()]
    .map(([lemma, e]) => ({lemma, gloss: e.gloss, voc: e.voc, n: e.n,
                           audio: (window.VOCAB_AUDIO || {})[lemma] || null}))
    .filter(x => _asGloss(x.gloss))
    .sort((a, b) => b.n - a.n);
  const sents = [];
  (LIB.texts || []).forEach(t => {
    if (t.kind !== 'news' && t.kind !== 'story') return;
    (t.sentences || []).forEach(s => { if (s.audio && s.en && s.ar)
      sents.push({ar: s.ar, en: s.en, audio: s.audio,
                  hard: t.kind === 'news' || t.level === 'advanced'}); });
  });
  const rx = (RX.items || []).filter(r => (r.provenance || '').includes('corroborated'));
  _asIdx = {ranked, sents, rx};
  return _asIdx;
}

// ---- item builders: each returns {skill, prompt, sub?, audio?, choices:[{t,ok}]} or null ----
function _asChoices(correct, distractors) {
  const seen = new Set([correct]);
  const ds = distractors.filter(d => d && !seen.has(d) && seen.add(d)).slice(0, 3);
  if (ds.length < 3) return null;
  return _asShuf([{t: correct, ok: true}, ...ds.map(t => ({t, ok: false}))]);
}
function asVocabItem(tier) {
  const {ranked} = assessIndex();
  const [a, b] = (AS.vocabBands || [])[tier - 1] || [0, 200];
  const band = ranked.slice(a, Math.min(b, ranked.length));
  if (band.length < 8) return null;
  const w = _asPick(band);
  const choices = _asChoices(_asGloss(w.gloss),
    _asShuf(band).map(x => _asGloss(x.gloss)).filter(g => g !== _asGloss(w.gloss)));
  if (!choices) return null;
  return {skill: 'vocab', prompt: `<span class="as-ar" dir="rtl">${esc(w.voc)}</span>`,
          sub: 'What does this mean?', choices};
}
function asListenItem(tier) {
  const {ranked, sents} = assessIndex();
  if (tier >= 3 && sents.length >= 8) {
    const pool = sents.filter(s => s.hard === (tier === 4)) .length >= 8
      ? sents.filter(s => s.hard === (tier === 4)) : sents;
    const s = _asPick(pool);
    const choices = _asChoices(s.en, _asShuf(pool).map(x => x.en).filter(e => e !== s.en));
    if (!choices) return null;
    return {skill: 'listening', prompt: '', sub: 'Listen — what does it mean?', audio: s.audio, choices};
  }
  const [a, b] = (AS.vocabBands || [])[tier - 1] || [0, 200];
  const band = assessIndex().ranked.slice(a, Math.min(b, ranked.length)).filter(x => x.audio);
  if (band.length < 8) return null;
  const w = _asPick(band);
  const choices = _asChoices(_asGloss(w.gloss),
    _asShuf(band).map(x => _asGloss(x.gloss)).filter(g => g !== _asGloss(w.gloss)));
  if (!choices) return null;
  return {skill: 'listening', prompt: '', sub: 'Listen — what does the word mean?', audio: w.audio, choices};
}
// How long the placement takes, in whole minutes. Arabic asks 4 rounds of 5 skills = 20 items
// and has always been advertised as eight, so roughly 24 seconds an item. Hebrew asked four
// skills until the binyan lessons had sentences to sample; saying "8 minutes" for a test that
// is a fifth shorter is the kind of small untruth that makes a learner distrust the rest.
function asMins() {
  return Math.max(1, Math.round((AS.rounds || 4) * (AS.skills || []).length * 0.4));
}
function asGrammarItem(tier) {
  const [a, b] = (AS.grammarBands || [])[tier - 1] || [0, 4];
  const lessons = GRAM.slice(a, Math.min(b, GRAM.length))
    .filter(l => (l.examples || []).some(e => e.hi && e.hi.length && e.ar.includes(e.hi[0])));
  if (!lessons.length) return null;
  const L = _asPick(lessons);
  const ex = _asPick(L.examples.filter(e => e.hi && e.hi.length && e.ar.includes(e.hi[0])));
  const hi = ex.hi[0];
  const others = GRAM.filter(x => x.id !== L.id)
    .flatMap(x => (x.examples || []).flatMap(e => e.hi || []))
    .filter(w => w !== hi && !ex.ar.includes(w));
  const choices = _asChoices(hi, _asShuf(others));
  if (!choices) return null;
  return {skill: 'grammar',
          prompt: `<span class="as-ar" dir="rtl">${esc(ex.ar.replace(hi, '____'))}</span>
                   <div class="as-en">“${esc(ex.en)}”</div>`,
          sub: 'Which word completes it?', choices, rtl: true};
}
function asVerbItem(tier) {
  const spec = (AS.verbSpec || [])[tier - 1]; if (!spec) return null;
  const verbs = VB.filter(v => v.hasConj && v.gloss && spec.weak.includes(v.weak));
  if (!verbs.length) return null;
  for (let tries = 0; tries < 12; tries++) {
    const v = _asPick(verbs), person = _asPick(spec.persons), aspect = _asPick(spec.aspects);
    const cell = v.conj[aspect + '|' + person]; if (!cell) continue;
    const others = spec.persons.filter(p => p !== person)
      .map(p => (v.conj[aspect + '|' + p] || {}).ar).filter(Boolean);
    // Extra distractors from persons the tier does not itself test. The list is the LANGUAGE's,
    // not this file's -- Arabic's four were sitting here hardcoded, so a Hebrew item silently
    // had none and fell back to whatever the tier happened to include.
    const extra = (AS.extraPersons || []).map(p => (v.conj[aspect + '|' + p] || {}).ar).filter(Boolean);
    const choices = _asChoices(cell.ar, _asShuf([...others, ...extra]));
    if (!choices) continue;
    const pEn = (PERSONS.find(p => p[0] === person) || [])[1] || person;
    // Likewise the tense name: 'past' meant Arabic's `perf`, and Hebrew's own `past` fell
    // through the ternary to be labelled "present".
    const aEn = (AS.aspectLabels || {})[aspect] || aspect;
    return {skill: 'verbs',
            prompt: `<div class="as-en" style="font-size:17px"><b>${esc(_asGloss(v.gloss))}</b> — ${esc(pEn)}, ${aEn}</div>`,
            sub: 'Pick the right form', choices, rtl: true};
  }
  return null;
}
function asChunkItem(tier) {
  const {rx} = assessIndex(); if (rx.length < 8) return null;
  const r = _asPick(rx);
  const choices = _asChoices(r.ar, _asShuf(rx).map(x => x.ar).filter(a => a !== r.ar));
  if (!choices) return null;
  return {skill: 'chunks',
          prompt: `<div class="as-en" style="font-size:17px">“${esc(r.en)}”</div>`,
          sub: 'Which chunk says it?', choices, rtl: true};
}
const _AS_BUILDERS = {listening: asListenItem, vocab: asVocabItem, grammar: asGrammarItem,
                      verbs: asVerbItem, chunks: asChunkItem};
function asItem(skill, tier) {
  let it = _AS_BUILDERS[skill](tier);
  if (!it) it = asVocabItem(tier) || asChunkItem(tier);      // graceful fallback, same tier
  if (it) it.skill = it.skill || skill;
  return it;
}

// ---- the flow ----
let _as = null;   // {tier, round, qi, order, skills:{s:{ok,n}}, cur, total, answered}
function assessView() {
  $('back').hidden = false;
  $('title').textContent = 'Placement';
  // The test samples real vocabulary by corpus frequency, so it needs every text. Start that
  // now: there are four paragraphs and a radio group to read before anyone presses Start.
  if (!corpusReady()) needCorpus().catch(() => {});
  if (_as && !_as.done) return assessRender();
  const radio = (val, label, sub) => `<label class="pf-radio">
     <input type="radio" name="aslvl" value="${val}" ${val === 'none' ? 'checked' : ''}>
     <span><b>${label}</b>${sub ? '<em>' + sub + '</em>' : ''}</span></label>`;
  // Length and skill list come from the spec, not from Arabic's five. Hebrew tests four skills,
  // so it is 16 questions and about six minutes, and the page has to say the number it will
  // actually ask.
  const nSk = (AS.skills || []).length || 5;
  const nQ = (AS.rounds || 4) * nSk;
  const skNames = (AS.skills || []).map(k => ((AS.skillLabels || {})[k] || k).toLowerCase());
  const skList = skNames.length > 1
    ? skNames.slice(0, -1).join(', ') + ' and ' + skNames[skNames.length - 1] : skNames.join('');
  $('view').innerHTML = `
    <p class="hint">About <b>${Math.max(3, Math.round(nQ * 0.4))} minutes</b>, ${nQ} quick questions
      across ${esc(skList)}. It adapts as you go — getting things wrong
      is fine, that's how it finds your level. Your plan starts where this says you are, so
      <b>press "I don't know" rather than guessing</b>; a lucky guess only places you too high.</p>
    <div class="sec">First, your own guess</div>
    ${radio('none', 'Brand new', 'Never really studied ' + esc(LANG.name))}
    ${radio('greetings', 'A few greetings', esc(LANG.assessGreetings || 'the basics'))}
    ${radio('conversation', 'Simple conversations', 'I can introduce myself and get by')}
    ${radio('comfortable', 'Fairly comfortable', 'I can tell a story, with effort')}
    <div class="ctl" style="margin-top:18px">
      <button class="tog go" style="font-size:14px;padding:11px 20px" onclick="assessStart()">Start →</button>
      <button class="tog" onclick="location.hash='/plan/new'">Back</button>
    </div>`;
}
// `guess` is passed on the retry: the waiting screen replaces the radio group, so re-reading
// it after the load would silently reset a self-assessment to "brand new".
function assessStart(guess) {
  guess = guess || (document.querySelector('input[name=aslvl]:checked') || {}).value || 'none';
  // The paradigms as well as the corpus. `hasConj` says a verb HAS a table; `v.conj` is a getter
  // over the lazily-loaded chunks, so before they are in it is undefined -- and the verb sampler
  // read straight through it and threw "Cannot read properties of undefined (reading 'past|ata')",
  // leaving the test stuck on "Getting the questions ready…". Arabic never showed it because
  // something else on the way to the plan had already pulled the chunks in.
  if (!corpusReady() || !conjIdxReady()) {
    $('view').innerHTML = '<div class="empty"><div class="empty-t">Getting the questions ready…</div></div>';
    return Promise.all([needCorpus(), needAllConj()]).then(
      () => { _asIdx = null; assessStart(guess); },
      () => routeFailed(new Error('The question bank could not be loaded.')));
  }
  const tier = (AS.selfStart || {})[guess] || 1;
  _as = {tier, round: 0, qi: 0, roundOk: 0, total: (AS.rounds || 4) * ((AS.skills || []).length || 5), answered: 0,
         skills: {}, order: _asShuf(AS.skills.slice()), done: false};
  assessNextItem();
}
function assessNextItem() {
  const skill = _as.order[_as.qi % _as.order.length];
  _as.cur = asItem(skill, _as.tier);
  if (!_as.cur) { _as.qi++; _as.answered++; if (!_asAdvance()) return; return assessNextItem(); }
  assessRender();
  if (_as.cur.audio) setTimeout(() => sndPlay(_as.cur.audio), 250);
}
function assessRender() {
  const it = _as.cur;
  $('title').textContent = 'Placement';
  $('view').innerHTML = `
    <div class="rv-top">Question ${_as.answered + 1} of ${_as.total} · ${esc((AS.skillLabels || {})[it.skill] || it.skill)}</div>
    <div class="rv-card" style="padding-bottom:18px">
      ${it.audio ? `<button class="tog go" style="margin-bottom:12px" onclick="sndPlay('${cssq(it.audio)}')">🔊 Play it again</button>` : ''}
      ${it.prompt}
      <div class="as-sub">${esc(it.sub || '')}</div>
      <div class="as-choices">${it.choices.map((c, i) =>
        `<button class="as-choice" ${it.rtl && isTargetScript(c.t) ? 'dir="rtl"' : ''}
           onclick="assessAnswer(${i})">${esc(c.t)}</button>`).join('')}
        <button class="as-choice idk" onclick="assessIdk()">I don't know</button></div>
    </div>`;
}
function assessAnswer(i) {
  const it = _as.cur; if (!it) return;
  const ok = !!it.choices[i].ok;
  const sk = _asSkill(it.skill);
  sk.n++; if (ok) { sk.ok++; _as.roundOk++; }
  _asReveal(i, ok);
  setTimeout(() => { if (_asAdvance()) assessNextItem(); }, ok ? 350 : 900);
}
// Four choices means a blind guess lands one time in four, and a couple of lucky guesses are
// enough to place someone a whole phase too high. "I don't know" is the honest exit: it scores
// exactly like a wrong answer for placement, but it is counted separately so the result can say
// how much of the test was actually known rather than survived.
function assessIdk() {
  const it = _as.cur; if (!it) return;
  const sk = _asSkill(it.skill);
  sk.n++; sk.idk = (sk.idk || 0) + 1;
  _asReveal(-1, false);
  setTimeout(() => { if (_asAdvance()) assessNextItem(); }, 900);
}
const _asSkill = k => (_as.skills[k] = _as.skills[k] || {ok: 0, n: 0, idk: 0});
// Mark the chosen button, always show the right answer, lock the rest, and step the counter.
function _asReveal(i, ok) {
  const it = _as.cur, btns = document.querySelectorAll('.as-choice');
  if (i >= 0 && btns[i]) btns[i].classList.add(ok ? 'good' : 'bad');
  if (!ok) { const ci = it.choices.findIndex(c => c.ok); if (btns[ci]) btns[ci].classList.add('good'); }
  btns.forEach(b => b.disabled = true);
  _as.qi++; _as.answered++;
}
// End-of-round tier moves; returns false when the test is finished (and renders the result).
function _asAdvance() {
  if (_as.qi % _as.order.length === 0) {                     // a round just ended
    if (_as.roundOk >= (AS.upAt || 4)) _as.tier = Math.min(4, _as.tier + 1);
    else if (_as.roundOk <= (AS.downAt || 2)) _as.tier = Math.max(1, _as.tier - 1);
    _as.roundOk = 0; _as.round++;
    _as.order = _asShuf(AS.skills.slice());
    if (_as.round >= (AS.rounds || 4)) { assessFinish(); return false; }
  }
  return true;
}
function assessFinish() {
  _as.done = true;
  const res = {tier: _as.tier, skills: _as.skills, at: todayISO()};
  try { localStorage.setItem(ASSESS_KEY, JSON.stringify(res)); } catch (e) {}
  // Seed grammar lessons BELOW the learner's band as already-known, so the plan's grammar
  // walker doesn't re-teach what the test just watched them do.
  const g = res.skills.grammar || {ok: 0, n: 0};
  if (res.tier >= 2 && g.n && g.ok / g.n >= (AS.seedGrammarMin || 0.5)) {
    const upto = (AS.grammarBands || [])[res.tier - 1][0] || 0;
    GRAM.slice(0, upto).forEach(l => markSeen('g:' + l.id, true));
  }
  // An existing plan re-bases immediately; a new user carries the result into the intake.
  const cfg = planCfg();
  if (cfg) {
    cfg.assess = res;
    cfg.startPhase = (AS.tierPhase || [0, 2, 3, 5])[res.tier - 1] || 0;
    cfg.baseMinutes = phaseStartMin(cfg.startPhase);
    savePlanCfg(cfg);
  }
  assessResultView(res);
}
const _asPct = s => s && s.n ? Math.round(100 * s.ok / s.n) : null;
function assessProfileHTML(res, small) {
  return `<div class="as-prof${small ? ' small' : ''}">` + (AS.skills || []).map(s => {
    const p = _asPct((res.skills || {})[s]);
    return `<div class="as-skill"><span>${esc((AS.skillLabels || {})[s] || s)}</span>
      <div class="as-bar"><i style="width:${p == null ? 0 : p}%"></i></div>
      <em>${p == null ? '—' : p + '%'}</em></div>`;
  }).join('') + `</div>`;
}
function assessResultView(res) {
  const phase = (AS.tierPhase || [0, 2, 3, 5])[res.tier - 1] || 0;
  const ph = CUR.phases[phase] || {name: '—'};
  $('title').textContent = 'Your placement';
  $('view').innerHTML = `
    <div class="hero"><div class="big" style="cursor:default">
      <div class="k">Placed</div>
      <div class="t">${esc((AS.tierNames || [])[res.tier - 1] || 'Tier ' + res.tier)}</div>
      <div class="s">Your plan starts in <b>Phase ${phase + 1} · ${esc(ph.name)}</b>. Grammar you
        already showed you know is marked done, and your daily mix tilts toward your weakest skill.</div>
    </div></div>
    <div class="sec">Skill profile</div>
    ${assessProfileHTML(res)}
    ${(() => {
      const sk = Object.values(res.skills || {});
      const idk = sk.reduce((a, s) => a + (s.idk || 0), 0), n = sk.reduce((a, s) => a + s.n, 0);
      if (!idk) return '';
      return `<p class="hint" style="margin-top:10px">You marked <b>${idk}</b> of ${n}
        as "I don't know" — that's the honest signal this placement is built on, and it counts the
        same as a wrong answer. Better here than three phases into a plan that doesn't fit.</p>`;
    })()}
    <div class="ctl" style="margin-top:18px">
      ${planCfg()
        ? `<button class="tog go" style="font-size:14px;padding:11px 20px" onclick="location.hash='/plan'">Back to my plan →</button>`
        : `<button class="tog go" style="font-size:14px;padding:11px 20px" onclick="location.hash='/plan/new'">Continue — build my plan →</button>`}
      <button class="tog" onclick="_as=null;location.hash='/plan/new/assess';route()">Retake</button>
    </div>`;
}

function planIntake() {
  $('title').textContent = 'Create my plan';
  const c = planCfg() || {};
  const h = c.hours || {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0};
  const car = c.car || {has: false, minutes: 45, days: [1, 2, 3, 4, 5]};
  const ext = c.external || {languageTransfer: true, pimsleur: false, tutor: false, podcasts: true};
  const dayRow = i => `<label class="pf-day"><span>${WD[i]}</span>
     <input id="ph${i}" type="number" min="0" max="16" step="0.5" value="${h[i] ?? 0}"></label>`;
  const carDay = i => `<label class="pf-cd"><input id="cd${i}" type="checkbox" ${car.days.includes(i) ? 'checked' : ''}>${WD[i]}</label>`;
  const lvl = c.level || 'none', pace = c.pace || 'sustainable';
  const radio = (name, val, cur, label, sub) => `<label class="pf-radio">
     <input type="radio" name="${name}" value="${val}" ${cur === val ? 'checked' : ''}>
     <span><b>${label}</b>${sub ? '<em>' + sub + '</em>' : ''}</span></label>`;
  const chk = (id, on, label, sub) => `<label class="pf-chk"><input id="${id}" type="checkbox" ${on ? 'checked' : ''}>
     <span><b>${label}</b>${sub ? '<em>' + sub + '</em>' : ''}</span></label>`;
  $('view').innerHTML = `
    <p class="hint">A few questions. The more honest you are about your real week, the better the plan fits.</p>

    <div class="sec">1 · Hours you can study, by day</div>
    <div class="pf-days">${[0, 1, 2, 3, 4, 5, 6].map(dayRow).join('')}</div>

    <div class="sec">2 · Where you can practice</div>
    <p class="hint" style="margin-bottom:8px">Speaking needs a moment where you’re alone and can talk out
      loud — usually a commute. It’s the scarcest, most valuable slot, so we ask directly.</p>
    ${chk('carHas', car.has, 'I have commute / alone time', 'A car, a walk — time to speak out loud')}
    <div class="pf-carwrap" id="carWrap" style="${car.has ? '' : 'display:none'}">
      <label class="pf-inline">Minutes of it, on a typical day
        <input id="carMin" type="number" min="5" max="180" step="5" value="${car.minutes}"></label>
      <div class="pf-cds">${[0, 1, 2, 3, 4, 5, 6].map(carDay).join('')}</div>
    </div>
    ${chk('spkHome', c.speakHome, 'I can speak out loud at home', 'Somewhere private enough not to feel silly')}
    ${chk('headph', c.headphones !== false, 'I usually have headphones', 'For audio and shadowing')}

    <div class="sec">3 · Where you’re starting</div>
    ${(() => { const as = assessResult();
      if (as) { const phase = (AS.tierPhase || [0,2,3,5])[as.tier - 1] || 0;
        return `<div class="as-placed"><b>Placed by assessment</b> (${esc(as.at)}):
          ${esc((AS.tierNames || [])[as.tier - 1] || 'Tier ' + as.tier)} — your plan starts in
          Phase ${phase + 1} · ${esc((CUR.phases[phase] || {}).name || '')}.
          <div class="ctl" style="margin-top:9px">
            <button class="tog" onclick="_as=null;location.hash='/plan/new/assess'">Re-take the test</button>
            <button class="tog" onclick="assessClear()">Use self-rating instead</button></div></div>`; }
      return `<div class="as-cta"><button class="tog go" style="font-size:13.5px;padding:10px 16px"
          onclick="location.hash='/plan/new/assess'">Take the ${asMins()}-minute placement →</button>
          <span class="hint" style="margin:0">finds your real level — or just rate yourself:</span></div>
        ${radio('lvl', 'none', lvl, 'Brand new', 'Never really studied ' + LANG.name)}
        ${radio('lvl', 'greetings', lvl, 'A few greetings', 'Salaam, shukran, the basics')}
        ${radio('lvl', 'conversation', lvl, 'Simple conversations', 'I can introduce myself and get by')}
        ${radio('lvl', 'comfortable', lvl, 'Fairly comfortable', 'I can tell a story, with effort')}`; })()}

    <div class="sec">4 · Pace</div>
    ${radio('pace', 'sustainable', pace, 'Sustainable', 'Something I can keep up for the long haul')}
    ${radio('pace', 'push', pace, 'Push', 'I want to move fast and I’ll feel it')}

    <div class="sec">5 · Outside resources to blend in</div>
    <p class="hint" style="margin-bottom:8px">We have a strong reading + flashcard core, but the speaking and
      listening half leans on great outside resources for now. Pick what you’re open to — we’ll only schedule these.</p>
    ${chk('extLT', ext.languageTransfer, 'Language Transfer', 'Free audio course — excellent for structure')}
    ${chk('extPim', ext.pimsleur, 'Pimsleur (Eastern Arabic)', 'Paid audio course, strong speaking drills')}
    ${chk('extPod', ext.podcasts, 'Podcasts / YouTube', 'Free Levantine listening (you’ll retell, not zone out)')}
    ${chk('extTut', ext.tutor, 'A tutor (iTalki / Preply)', 'Paid — the fastest fix for the speaking gap')}

    <div class="ctl" style="margin-top:20px">
      <button class="tog go" style="font-size:14px;padding:11px 20px" onclick="planCreate()">${planCfg() ? 'Update my plan' : 'Create my plan'} →</button>
      ${planCfg() ? `<button class="tog" onclick="location.hash='/plan'">Cancel</button>` : ''}
    </div>`;
  const cw = $('carHas'); if (cw) cw.onchange = e => { $('carWrap').style.display = e.target.checked ? '' : 'none'; };
}

const LVL_PHASE = {none: 0, greetings: 1, conversation: 2, comfortable: 4};
function planCreate() {
  const num = id => Math.max(0, parseFloat($(id).value) || 0);
  const hours = {}; for (let i = 0; i < 7; i++) hours[i] = num('ph' + i);
  if (!Object.values(hours).some(v => v > 0)) { alert('Add at least a little time on one day so we have something to plan.'); return; }
  const carDays = []; for (let i = 0; i < 7; i++) if ($('cd' + i) && $('cd' + i).checked) carDays.push(i);
  const lvl = (document.querySelector('input[name=lvl]:checked') || {}).value || 'none';
  const pace = (document.querySelector('input[name=pace]:checked') || {}).value || 'sustainable';
  const prev = planCfg();
  // Placement: an assessment result beats the self-rating radios. Without one, re-running the
  // intake with the SAME self-rating must not re-derive the phase (no silent teleporting) —
  // only an actually-changed rating moves the start.
  const as = assessResult();
  const startPhase = as ? ((AS.tierPhase || [0, 2, 3, 5])[as.tier - 1] || 0)
    : (prev && !prev.assess && prev.level === lvl && prev.startPhase != null) ? prev.startPhase
    : (LVL_PHASE[lvl] || 0);
  const cfg = {
    created: (prev && prev.created) || now(),
    start: (prev && prev.start) || todayISO(),
    hours,
    car: {has: $('carHas').checked, minutes: Math.max(5, parseInt($('carMin').value, 10) || 45), days: carDays},
    speakHome: $('spkHome').checked,
    headphones: $('headph').checked,
    level: lvl, pace, assess: as || null,
    startPhase, baseMinutes: phaseStartMin(startPhase),
    external: {
      languageTransfer: $('extLT').checked, pimsleur: $('extPim').checked,
      podcasts: $('extPod').checked, tutor: $('extTut').checked,
    },
  };
  savePlanCfg(cfg);
  location.hash = '/plan';
}

// ---- Today: the daily driver ----
function planToday() {
  const cfg = planCfg(); if (!cfg) return planWelcome();
  $('title').textContent = 'My Plan';
  const date = todayISO();
  const pi = curPhaseIndex(cfg);
  const due = dueCards().length;
  const day = getDay(cfg, date, due);
  const L = planLog(); const doneMap = (L[date] && L[date].done) || {};
  const journeyPct = Math.min(100, Math.round(planProgressMin(cfg) / (CUR.totalHours * 60) * 100));

  let h = `<div class="pjourney">
      <div class="pj-top"><span>Phase ${day.phase.id + 1} · <b>${esc(day.phase.name)}</b></span>
        <span class="pj-pct">${streakChip()} ${journeyPct}% of the way</span></div>
      <div class="pj-bar"><i style="width:${Math.max(2, journeyPct)}%;background:${PHASE_COLOR[day.phase.id] || 'var(--verdigris)'}"></i></div>
      <div class="pj-goal">${esc(day.phase.focus)}</div>
      <div class="ctl" style="margin-top:10px"><button class="tog" onclick="location.hash='/plan/dashboard'">📊 Dashboard</button></div></div>`;

  if (day.rest) {
    h += `<div class="empty"><div class="empty-t">Rest day</div>
      <p>Nothing scheduled today — recovery is part of the plan, and sleep is where yesterday’s
      practice actually sets. ${due ? `You do have <b>${due}</b> card${due === 1 ? '' : 's'} due if you want a quick round.` : 'See you tomorrow.'}</p>
      ${due ? `<div class="ctl" style="justify-content:center"><button class="tog go" onclick="location.hash='/vocab/review'">Review ${due} card${due === 1 ? '' : 's'}</button></div>` : ''}
      </div>`;
    if (cfg.external && cfg.external.pimsleur) h += pimCardHTML();
    h += planExtraHTML(cfg, day.phase, date, doneMap, 0);   // studying on an off-day is allowed
    h += planMoreBtn(date, true);
    h += planFooterCtls();
    $('view').innerHTML = h; return;
  }

  const total = day.tasks.length;
  const doneN = day.tasks.filter(t => t.id in doneMap).length;
  h += `<div class="pt-head"><div class="pt-h-l">Today · ${WD[isoToDate(date).getDay()]} ${fmtMD(date)}</div>
     <div class="pt-h-r">${doneN}/${total} done · ${Math.round(day.totalMin / 60 * 10) / 10}h</div></div>
     <div class="pj-bar sm"><i style="width:${total ? Math.round(doneN / total * 100) : 0}%"></i></div>`;
  if (doneN === total && total) h += `<div class="pdone">✓ Done for today — nicely done.</div>`;
  if (day.review) h += `<div class="pt-note" style="border:1px solid var(--verdigris);border-radius:7px;padding:10px 12px;color:var(--muted);margin-bottom:12px">
     <b>Review day.</b> Lighter on new material — today leans on re-surfacing what you met this week, which is when it actually sets.</div>`;

  h += planWarmupHTML(date, doneMap);
  h += day.tasks.map(t => planTaskRow(t, date, t.id in doneMap)).join('');
  if (day.banked) h += `<div class="pt-note" style="border:1px solid var(--rule);border-radius:7px;padding:10px 12px;color:var(--muted)">
     That’s a full session for <b>${esc(day.phase.name)}</b> — this early phase is deliberately short, so
     the other ~${Math.round(day.banked / 60 * 10) / 10}h today is yours. Quality over hours; the plan
     leans in as you advance.</div>`;
  const schedReads = day.tasks.filter(t => t.act === 'read' && t.cid).length;
  h += planExtraHTML(cfg, day.phase, date, doneMap, schedReads);
  h += `<div id="fr-strip"></div>`;
  h += planMoreBtn(date, false);
  h += planExerciseHTML(day, date);
  if (day.spoken || cfg.speakHome) h += planRecordHTML(date, doneMap, day.phase.focus.split('.')[0]);
  // Only offer the Pimsleur tracker to people who told the intake they have it.
  if (cfg.external && cfg.external.pimsleur) h += pimCardHTML();
  h += planFooterCtls();
  $('view').innerHTML = h;
  frStrip();
}

// One line on Today: who else has practised, and how you compare this week. Only appears once
// you actually have friends — an empty prompt to "add friends" on the main screen every day is
// nagging, and the dashboard is where you go looking for it.
async function frStrip() {
  const el = $('fr-strip'); if (!el || !frOn()) return;
  const d = await frLoad(); if (!d || !d.friends.length) { if (d && d.incoming.length) {
      el.innerHTML = `<span><b>${d.incoming.length}</b> friend request waiting</span>
        <a href="#/plan/dashboard">Open</a>`; } return; }
  const today = d.friends.filter(f => f.stats && f.stats.last_active === todayISO());
  const mineWk = frMyStats().week_min;
  const ahead = d.friends.filter(f => ((f.stats || {}).week_min || 0) > mineWk).length;
  el.innerHTML = `<span>${today.length
      ? '<b>' + today.map(f => esc(f.profile.display_name || f.profile.handle)).slice(0, 3).join(', ')
        + '</b> studied today'
      : 'None of your friends have practised today yet'}</span>
    <span>${ahead ? '<b>' + ahead + '</b> ahead of you this week' : 'you’re top this week'}</span>
    <a href="#/plan/dashboard">Friends</a>`;
}

// ---- production exercise: say today's material in Arabic (retrieval practice) ----
// Pulls English→Arabic pairs from the texts/drills scheduled today, and asks you to produce the
// Arabic from the English before revealing the answer. Auto-checks leniently (order/diacritics don't matter).
let _planEx = [];
function planExerciseItems(day, date) {
  const seen = new Set(), pool = [];
  (day.tasks || []).forEach(t => {
    const tm = (t.link || '').match(/^\/(?:text|speak)\/(.+)$/);
    if (tm) { const tx = LIB.texts.find(x => x.id === tm[1]);
      if (tx) (tx.sentences || []).forEach(s => { if (s.en && s.ar && !seen.has(s.ar)) { seen.add(s.ar); pool.push({en: s.en, ar: s.ar}); } }); }
    const dm = (t.link || '').match(/^\/drill\/(.+)$/);
    if (dm) { const d = LIB.drills.find(x => x.id === dm[1]);
      if (d) (d.items || []).forEach(it => { if (it.cue && it.answer && !seen.has(it.answer)) { seen.add(it.answer); pool.push({en: it.cue, ar: it.answer}); } }); }
  });
  if (!pool.length) return [];
  const seed = Math.abs(daysBetween('2020-01-01', date));   // deterministic per day
  return pool.map((it, i) => [it, (i * 9301 + seed * 49297) % 233280]).sort((a, b) => a[1] - b[1]).slice(0, 5).map(x => x[0]);
}
function planExerciseHTML(day, date) {
  _planEx = planExerciseItems(day, date);
  if (!_planEx.length) return '';
  let h = `<div class="sec" style="margin-top:22px">Exercise — say it in ${esc(LANG.name)}</div>
    <p class="hint" style="margin-bottom:10px">From today’s material. Producing it from memory (not just
      rereading) is what makes it stick — try each one before you check.</p>`;
  h += _planEx.map((it, i) => `<div class="pex">
      <div class="pex-q">${esc(it.en)}</div>
      ${kbdWrap(`<input class="pex-in" id="pex-in-${i}" dir="rtl" autocomplete="off" placeholder="اكتب بالعربي…"
        onkeydown="if(event.key==='Enter')planExCheck(${i})">`, 'pex-in-' + i)}
      <div class="ctl" style="margin-top:8px">
        <button class="tog go" onclick="planExCheck(${i})">Check</button>
        <button class="tog" onclick="planExShow(${i})">Show answer</button></div>
      <div class="pex-res" id="pex-res-${i}"></div></div>`).join('');
  return h;
}
const _exNorm = s => arNorm(s).replace(/[،.؟!:؛…"«»”“\-—()]/g, '').replace(/\s+/g, ' ').trim();
function planExCheck(i) {
  const it = _planEx[i], res = $('pex-res-' + i); if (!it || !res) return;
  const ans = _exNorm((($('pex-in-' + i) || {}).value) || ''), gold = _exNorm(it.ar);
  const at = new Set(ans.split(' ').filter(Boolean)), gt = new Set(gold.split(' ').filter(Boolean));
  const overlap = gt.size ? [...gt].filter(x => at.has(x)).length / gt.size : 0;
  let cls, verdict;
  if (ans && (ans === gold || overlap >= 0.85)) { cls = 'ok'; verdict = '✓ Nailed it'; }
  else if (overlap >= 0.5) { cls = 'close'; verdict = 'Close — compare with the answer'; }
  else { cls = 'no'; verdict = ans ? 'Not quite — here’s the answer' : 'Here’s the answer'; }
  res.innerHTML = `<div class="pex-v ${cls}">${verdict}</div><div class="pex-ans" dir="rtl">${esc(it.ar)}</div>`;
}
function planExShow(i) { const it = _planEx[i], res = $('pex-res-' + i);
  if (it && res) res.innerHTML = `<div class="pex-ans" dir="rtl">${esc(it.ar)}</div>`; }

// ---- "study more": extra content on demand (extra time, or an off day) ----
const PXKEY = LKEY('plan.extra.v1');
function planExtra() { try { return JSON.parse(localStorage.getItem(PXKEY) || '{}') || {}; } catch (e) { return {}; } }
function addPlanExtra(date) { const x = planExtra(); x[date] = (x[date] || 0) + 1;
  try { localStorage.setItem(PXKEY, JSON.stringify(x)); } catch (e) {} planToday(); }
// The next unseen stories for the current phase's level, as extra checkable reading tasks.
function planExtraHTML(cfg, phase, date, doneMap, offset) {
  const nx = planExtra()[date] || 0;
  if (nx <= 0) return '';
  const pool = phaseReadPool(phase);
  let h = `<div class="sec">Extra practice — you asked for more</div>`;
  for (let j = 0; j < nx; j++) {
    const t = resolveTask(cfg, {act: 'read', src: 'inapp', pool, min: 20}, offset + j, 0, 20, false, curPhaseIndex(cfg));
    t.id = 'x' + j + '-read';                               // stable per-day id for the log
    h += planTaskRow(t, date, t.id in doneMap);
  }
  return h;
}
function planMoreBtn(date, restday) {
  return `<div class="ctl" style="margin-top:14px;justify-content:center">
     <button class="tog go" onclick="addPlanExtra('${date}')">＋ ${restday ? 'Study anyway' : 'Study more'}</button></div>`;
}

// A task's level is the level of the thing it opens — resolved from the content id, so it can't
// disagree with the same item's tag in its own section. Tasks that open something external (a
// course, a video) or nothing at all (SRS reps) get no tag rather than an invented one.
function taskPhase(t) {
  const cid = t.cid || '';
  if (cid.startsWith('lsn:')) { const u = lsnById(cid.slice(4)); return u ? contentPhase('unit', u) : null; }
  if (cid.startsWith('ls:'))  { const e = lsById(cid.slice(3)); return e ? contentPhase('listen', e) : null; }
  if (cid.startsWith('rx:'))  return contentPhase('reaction', {});
  if (cid.startsWith('tbl:')) return contentPhase('dialogue', {});
  if (cid.startsWith('snd:')) return contentPhase('sound', {});
  if (cid.startsWith('g:'))   { const i = (GRAM || []).findIndex(l => l.id === cid.slice(2));
                                return i < 0 ? null : contentPhase('grammar', {n: i}); }
  if (cid.startsWith('v:'))   { const v = verbPlan().find(x => x.key === cid);
                                return v ? contentPhase('verb', v) : null; }
  const tx = cid && LIB.texts.find(x => x.id === cid);
  return tx ? contentPhase(textType(tx), tx) : null;
}
const textType = tx => tx.kind === 'news' ? 'news' : tx.kind === 'book-chapter' ? 'book' : 'story';
function planTaskRow(t, date, done) {
  const srcPill = t.source === 'inapp' ? '<span class="pill on">in-app</span>' : '<span class="pill">external</span>';
  const open = t.link ? `<button class="tog" onclick="location.hash='${t.link}'">Open</button>`
    : t.url ? `<a class="tog pext" href="${esc(t.url)}" target="_blank" rel="noopener">Open ${svg('ext')}</a>` : '';
  return `<div class="ptask${done ? ' done' : ''}">
      <button class="pcheck" onclick="planToggle('${date}','${esc(t.id)}',${t.minutes},'${cssq(t.cid || '')}',${t.pim ? 1 : 0},'${cssq(t.rkey || '')}',${t.review ? 1 : 0})" aria-label="Mark done">${done ? '✓' : ''}</button>
      <div class="pt-main">
        <div class="pt-top"><span class="pt-title">${esc(t.title)}</span><span class="pmin">${t.minutes}m</span></div>
        ${t.seq ? `<div class="pt-seq">${esc(t.seq)}</div>` : ''}
        <div class="pt-sub">${esc(t.label)} · ${esc(t.builds)} · <span class="pt-slot">${esc(t.ideal)}</span></div>
        <div class="pt-instr">${esc(t.instr)}</div>
        ${t.note ? `<div class="pt-note">${esc(t.note)}</div>` : ''}
        <div class="pt-act">${open}${srcPill}${
          (() => { const ph = taskPhase(t); return ph == null ? '' : lvlTag(ph); })()}</div>
      </div></div>`;
}
function planToggle(date, tid, minutes, cid, isPim, rkey, isReview) {
  const L = planLog(); const d = L[date] || (L[date] = {done: {}}); d.done = d.done || {};
  const nowDone = d.done[tid] == null;
  // A lesson unit isn't "done" until every chunk in it has been worked through. Unchecking is
  // always allowed; only claiming completion is gated. Missing/empty units never block.
  if (nowDone && cid && cid.indexOf('lsn:') === 0) {
    const u = lsnById(cid.slice(4));
    if (u && !lsnAllSaved(u)) {
      alert('Unit ' + u.n + ' still has ' + lsnLeft(u) + ' chunk' + (lsnLeft(u) === 1 ? '' : 's') +
            ' to check off.\n\nOpen the unit and work through them — then you can mark it done.');
      location.hash = '/lessons/' + u.id;
      return;
    }
  }
  if (nowDone) d.done[tid] = +minutes || 0; else delete d.done[tid];
  savePlanLog(L);
  if (cid) markSeen(cid, nowDone);                          // checking a content task walks the path forward
  if (isPim) pimAdvance(nowDone);                           // finishing a Pimsleur lesson moves you on
  if (rkey) { if (isReview) advanceReview(rkey, nowDone);   // a review rep → widen its next interval
              else if (nowDone) noteReview(rkey); }         // first time learning it → schedule reviews
  planToday();
}
// ---- Pimsleur progress ---------------------------------------------------------------
// Pimsleur has no public API and its audio is DRM-protected subscription content, so nothing
// here touches their servers or their recordings. What it does is stop the plan from saying
// a vague "do Pimsleur" every day: it remembers which level and lesson you're on, schedules
// the NEXT one by name, advances when you tick it off, and counts the minutes like any other
// task. The listening still happens in their app.
const PIMKEY = LKEY('pimsleur.v1');
const PIM_LESSONS = 30;                        // every Pimsleur level is 30 half-hour lessons
function pim() {
  try { return JSON.parse(localStorage.getItem(PIMKEY) || 'null') || {}; } catch (e) { return {}; }
}
function pimSave(p) { try { localStorage.setItem(PIMKEY, JSON.stringify(p)); } catch (e) {} }
const pimOn = () => { const p = pim(); return !!p.on; };
const pimLabel = () => { const p = pim();
  return 'Level ' + (p.level || 1) + ' · Lesson ' + (p.lesson || 1); };
// Ticking the task off moves you to the next lesson; unticking puts it back.
function pimAdvance(forward) {
  const p = pim(); if (!p.on) return;
  let lv = p.level || 1, ls = p.lesson || 1;
  if (forward) { ls++; if (ls > PIM_LESSONS) { ls = 1; lv = Math.min(5, lv + 1); } }
  else { ls--; if (ls < 1) { lv = Math.max(1, lv - 1); ls = PIM_LESSONS; } }
  p.level = lv; p.lesson = ls; p.done = Math.max(0, (p.done || 0) + (forward ? 1 : -1));
  pimSave(p);
}
function pimSetup() {
  const p = pim();
  const lv = prompt('Which Pimsleur level are you on? (1–5)', String(p.level || 1));
  if (lv === null) return;
  const ls = prompt('Which lesson are you up to? (1–30)', String(p.lesson || 1));
  if (ls === null) return;
  const L = Math.min(5, Math.max(1, parseInt(lv, 10) || 1));
  const N = Math.min(PIM_LESSONS, Math.max(1, parseInt(ls, 10) || 1));
  pimSave({...p, on: true, level: L, lesson: N, done: p.done || 0});
  route();
}
function pimOff() { pimSave({...pim(), on: false}); route(); }
// The curriculum only schedules an audio course in the early phases — later on the plan
// deliberately spends your time on production and a tutor instead. But a Pimsleur
// subscription runs to Level 5, so let a lesson be logged on any day: it advances the
// counter and records the half hour against today, so real work still counts toward the
// phase you're in.
function pimLogLesson() {
  const p = pim(); if (!p.on) return;
  const date = todayISO();
  const L = planLog(); const d = L[date] || (L[date] = {done: {}}); d.done = d.done || {};
  d.done['pim-' + ((p.done || 0) + 1)] = 30;
  savePlanLog(L);
  pimAdvance(true);
  route();
}
function pimCardHTML() {
  const p = pim();
  if (!p.on) {
    return `<div class="pimc"><div class="pimc-t">Have a Pimsleur subscription?</div>
      <p class="hint" style="margin:4px 0 0">Tell the app which lesson you're on and it will
        schedule the next one by name, then move you forward as you finish them.</p>
      <div class="ctl" style="margin-top:8px">
        <button class="tog" onclick="pimSetup()">Set up Pimsleur</button></div></div>`;
  }
  const pct = Math.round(((p.level - 1) * PIM_LESSONS + p.lesson - 1) / (5 * PIM_LESSONS) * 100);
  return `<div class="pimc"><div class="pimc-t">Pimsleur — Eastern Arabic</div>
    <div class="pimc-now">${esc(pimLabel())}</div>
    <div class="pimc-bar"><i style="width:${pct}%"></i></div>
    <div class="pimc-sub">${p.done || 0} lesson${(p.done || 0) === 1 ? '' : 's'} logged here ·
      ${pct}% through the five levels</div>
    <div class="ctl" style="margin-top:8px">
      <a class="tog pext" href="https://www.pimsleur.com/learn-arabic" target="_blank"
         rel="noopener">Open Pimsleur ${svg('ext')}</a>
      <button class="tog go" onclick="pimLogLesson()">✓ Logged lesson ${p.lesson}</button>
      <button class="tog" onclick="pimSetup()">Change lesson</button>
      <button class="tog" onclick="pimOff()">Turn off</button></div></div>`;
}

function planFooterCtls() {
  return `<div class="ctl" style="margin-top:18px">
     <button class="tog" onclick="location.hash='/plan/journey'">🗺 The whole journey</button>
     <button class="tog" onclick="location.hash='/plan/dashboard'">📊 Dashboard</button>
     <button class="tog" onclick="location.hash='/plan/calendar'">Next four weeks</button>
     <button class="tog" onclick="location.hash='/plan/new'">Adjust my time</button>
     <button class="tog" onclick="planReassess()">Re-take the placement</button></div>`;
}

// ---- dashboard: the numbers that keep you honest (activity, streak, coverage, trouble cards) ----
function planDashboard() {
  const cfg = planCfg(); if (!cfg) { location.hash = '/plan'; return; }
  $('title').textContent = 'Dashboard';
  const L = planLog(), seen = contentSeen();
  const totalH = Math.round(loggedMinutes() / 60 * 10) / 10;
  const pct = Math.min(100, Math.round(planProgressMin(cfg) / (CUR.totalHours * 60) * 100));
  const flu = projDateISO(cfg, CUR.totalHours * 60);
  const streak = planStreak();
  const seenPre = pre => [...seen].filter(k => k.startsWith(pre)).length;

  // 14-day activity (minutes completed per day)
  const bars14 = []; for (let i = 13; i >= 0; i--) { const d = addDaysISO(todayISO(), -i);
    const done = (L[d] && L[d].done) || {}; let m = 0; for (const k in done) m += done[k] || 0; bars14.push({d, m}); }
  const maxM = Math.max(30, ...bars14.map(x => x.m));
  const chart = bars14.map(x => `<div class="dbar" title="${x.d}: ${x.m} min"><i style="height:${Math.max(2, Math.round(x.m / maxM * 100))}%${x.m ? '' : ';opacity:.25'}"></i>
      <span class="dbar-x">${isoToDate(x.d).getDate()}</span></div>`).join('');

  // content coverage
  const stories = STORY_LEVELS.map(([k, label]) => ({label, done: storiesAt(k).filter(t => seen.has(t.id)).length, tot: storiesAt(k).length}));
  const gTot = GRAM.length, gDone = seenPre('g:');
  const vDone = seenPre('v:'), wDone = seenPre('w:'), wTot = VIDEOS.length;
  const cover = (label, done, tot) => `<div class="dcov"><div class="dcov-h"><span>${label}</span><span>${done}${tot ? ' / ' + tot : ''}</span></div>
     <div class="pj-bar sm"><i style="width:${tot ? Math.round(done / tot * 100) : (done ? 100 : 0)}%"></i></div></div>`;

  // vocab deck
  const cards = [...marked.values()];
  const dueN = dueCards().length;
  const mature = cards.filter(c => (c.interval || 0) >= 21).length;
  const learning = cards.length - mature;
  const trouble = cards.filter(c => (c.reps || 0) > 0).sort((a, b) => (a.ease || 2.5) - (b.ease || 2.5)).slice(0, 5);

  const stat = (k, v) => `<div class="dstat"><div class="dstat-v">${v}</div><div class="dstat-k">${k}</div></div>`;
  let h = `<div class="dstats">
      ${stat('Day streak', '🔥 ' + streak)}
      ${stat('Hours logged', totalH)}
      ${stat('Journey', pct + '%')}
      ${stat('Cards due', dueN)}
    </div>
    <div class="pj-goal" style="margin:2px 0 18px">Phase ${curPhaseIndex(cfg) + 1} · <b>${esc(CUR.phases[curPhaseIndex(cfg)].name)}</b>${flu ? ' · on pace for ~' + fmtMY(flu) : ''}</div>

    <div class="sec">Last 14 days</div>
    <div class="dchart">${chart}</div>

    <div class="sec" style="margin-top:22px">Content covered</div>`;
  stories.forEach(s => h += cover(s.label + ' stories', s.done, s.tot));
  h += cover('Grammar lessons', gDone, gTot);
  h += cover('Verbs practiced', vDone, 0);
  h += cover('Video playlists', wDone, wTot);

  // placement: the assessed skill profile, and the door to re-assessing as you improve
  const asr = cfg.assess || assessResult();
  h += `<div class="sec" style="margin-top:22px">Your level</div>`;
  if (asr) {
    h += `<p class="hint" style="margin-bottom:8px">Placed <b>${esc((AS.tierNames || [])[asr.tier - 1] || 'tier ' + asr.tier)}</b> on ${esc(asr.at)}. Re-assess when it starts feeling easy — the plan re-bases to the result.</p>`
      + assessProfileHTML(asr, true);
  } else {
    h += `<p class="hint" style="margin-bottom:8px">You self-rated at intake. An 8-minute adaptive test places you more honestly — per skill.</p>`;
  }
  h += `<div class="ctl" style="margin:10px 0 4px"><button class="tog" onclick="${asr ? 'planReassess()' : `_as=null;location.hash='/plan/new/assess'`}">${asr ? 'Re-assess my level' : 'Take the placement test'}</button></div>`;

  h += `<div class="sec" style="margin-top:22px">Flashcards</div>
    <div class="dstats">
      ${stat('Total', cards.length)}
      ${stat('Learning', learning)}
      ${stat('Mature', mature)}
      ${stat('Due now', dueN)}
    </div>`;
  if (trouble.length) {
    h += `<div class="sec" style="margin-top:18px">Trouble cards — the ones fighting you</div>`;
    h += trouble.map(c => `<div class="dtrouble"><span dir="rtl">${esc(c.vocalized || c.lemma)}</span>
       <span class="dtr-gl">${esc(c.gloss || '')}</span>
       <span class="dtr-e">ease ${(c.ease || 2.5).toFixed(2)}</span>
       <button class="say" onclick="playWord(marked.get('${cssq(c.lemma)}'))" aria-label="Pronounce">${svg('spk')}</button></div>`).join('');
  } else {
    h += `<p class="hint">No flashcards yet — tap any word in a story and hit “Don’t know it” to start a deck.</p>`;
  }
  h += `<div class="sec" style="margin-top:22px">Studying together</div><div id="fr-panel"></div>`;
  h += `<div class="ctl" style="margin-top:20px"><button class="tog" onclick="location.hash='/plan'">← Back to today</button></div>`;
  $('view').innerHTML = h;
  frRender();                                   // fills #fr-panel once the network answers
}

// ---- the friends panel ----------------------------------------------------------------
// Async and self-contained: the dashboard renders instantly and this fills in when the round
// trip lands, so a slow or missing connection never holds up the numbers you already have.
async function frRender() {
  const el = $('fr-panel'); if (!el) return;
  if (!_sb) return void (el.innerHTML = `<p class="hint">Cloud sync isn’t configured for this build,
    so there’s nobody to study with yet.</p>`);
  if (!_user) return void (el.innerHTML = `<p class="hint">
    <a href="#/account">Sign in</a> to compare notes with friends. You’ll get a six-character code to
    share; you each have to accept before either of you sees anything.</p>`);
  if (!el.innerHTML) el.innerHTML = `<p class="hint">Loading…</p>`;
  const d = await frLoad();
  if (!d) return void (el.innerHTML = _frErr === 'setup'
    ? `<div class="note"><b>Almost there.</b> The friends tables aren’t on the server yet. Run
       <code>supabase/friends.sql</code> once in the Supabase SQL editor and reload — everything
       else keeps working in the meantime.</div>`
    : `<p class="hint">Couldn’t load your friends${_frErr ? ' — ' + esc(_frErr) : ''}.
       <button class="tog" onclick="_frCache=null;frRender()">Try again</button></p>`);

  const mine = frMyStats();
  const nm = f => esc(f.profile.display_name || f.profile.handle);
  let h = `<div class="fr-me">
      <div class="fr-me-l"><span class="fr-k">Your friend code</span>
        <span class="fr-code">${esc(d.me.handle)}</span></div>
      <div class="fr-me-r">
        <button class="tog" onclick="frCopy('${cssq(d.me.handle)}')">Copy</button>
        <button class="tog" onclick="frRename()">Name: ${esc(d.me.display_name || '—')}</button></div>
    </div>
    <p class="hint">Send that code to someone learning too. Friends see your hours, your streak and
      which phase you’re in — never your cards, your texts, or what you actually studied.</p>`;

  if (d.incoming.length) {
    h += `<div class="sec">Waiting on you</div>` + d.incoming.map(f => `<div class="fr-row">
        <div class="fr-n">${nm(f)}<span class="fr-h">${esc(f.profile.handle)}</span></div>
        <div class="fr-act">
          <button class="tog go" onclick="frAccept(${f.link})">Accept</button>
          <button class="tog" onclick="frRemove(${f.link},'${cssq(f.profile.display_name || '')}')">Decline</button>
        </div></div>`).join('');
  }

  if (d.friends.length) {
    // You are in the table too. Comparing against people who study more is the entire point, and
    // leaving yourself out of your own leaderboard makes it a list of strangers.
    const rows = d.friends.map(f => ({name: nm(f), handle: f.profile.handle, link: f.link,
                                      s: f.stats, me: false}))
      .concat([{name: 'You', handle: d.me.handle, link: null, s: mine, me: true}])
      .sort((a, b) => ((b.s || {}).week_min || 0) - ((a.s || {}).week_min || 0));
    const together = rows.reduce((n, r) => n + ((r.s || {}).week_min || 0), 0);
    h += `<div class="sec">This week</div>
      <p class="hint" style="margin-bottom:8px"><b>${frHrs(together)}</b> between the
        ${rows.length} of you.</p>
      <table class="fr-tbl"><thead><tr><th></th><th>Week</th><th>Streak</th><th>Level</th><th>Total</th></tr></thead><tbody>`;
    h += rows.map(r => {
      const s = r.s || {};
      return `<tr class="${r.me ? 'me' : ''}">
        <td><span class="fr-n">${esc(r.name)}${r.me ? '' : `<span class="fr-h">${esc(r.handle)}</span>`}</span>
          <div class="fr-seen">${frSeen(s.last_active)}</div></td>
        <td><b>${frHrs(s.week_min || 0)}</b></td>
        <td>${s.streak ? '🔥 ' + s.streak : '—'}</td>
        <td>${s.phase != null ? lvlTag(s.phase, true) : '—'}</td>
        <td>${s.hours != null ? Math.round(s.hours) + 'h' : '—'}</td>
        ${r.me ? '<td></td>' : `<td><button class="fr-x" title="Disconnect"
           onclick="frRemove(${r.link},'${cssq(r.name)}')">×</button></td>`}</tr>`;
    }).join('') + `</tbody></table>`;
  }

  if (d.outgoing.length) {
    h += `<div class="sec">Waiting on them</div>` + d.outgoing.map(f => `<div class="fr-row">
        <div class="fr-n">${nm(f)}<span class="fr-h">${esc(f.profile.handle)}</span></div>
        <div class="fr-act"><span class="fr-pend">asked</span>
          <button class="fr-x" onclick="frRemove(${f.link},'${cssq(f.profile.display_name || '')}')">×</button>
        </div></div>`).join('');
  }

  if (!d.friends.length && !d.incoming.length && !d.outgoing.length) {
    h += `<p class="hint">Nobody yet. Studying alongside someone is one of the few things that
      reliably keeps a daily habit alive — it doesn't have to be a race.</p>`;
  }
  h += `<div class="sec">Add someone</div>
    <div class="fr-add"><input id="fr-code" class="vsearch" maxlength="6" autocomplete="off"
        placeholder="Their six-character code" style="text-transform:uppercase"
        onkeydown="if(event.key==='Enter')frAdd(this.value)">
      <button class="tog go" onclick="frAdd(($('fr-code')||{}).value)">Send request</button></div>
    <div id="fr-msg" class="hint" style="margin-top:8px"></div>`;
  el.innerHTML = h;
}
const frHrs = min => min >= 60 ? (Math.round(min / 6) / 10) + 'h' : (min | 0) + 'm';
function frSeen(iso) {
  if (!iso) return 'not started yet';
  const n = daysBetween(iso, todayISO());
  return n <= 0 ? 'studied today' : n === 1 ? 'yesterday' : n + ' days ago';
}
function frCopy(code) {
  const done = () => { const el = $('fr-msg'); if (el) el.textContent = 'Code copied — send it over.'; };
  if (navigator.clipboard) navigator.clipboard.writeText(code).then(done, () => {});
  else done();
}

// ---- the plan ahead: projection + a 4-week look-ahead ----
// ---- the whole journey, not just the next month ----
// The calendar answered "what am I doing this month?"; this answers "how do I actually get from
// here to fluent, and when?" Every month from your start date to the projected finish, coloured by
// the phase you'll be in, with each phase's real dates and the milestone that ends it. It's a
// projection from ONE number — your weekly hours — so it's honest about being a projection.
function planJourney() {
  const cfg = planCfg(); if (!cfg) { location.hash = '/plan'; return; }
  $('title').textContent = 'The journey';
  const wk = weeklyMin(cfg), perDay = wk / 7;
  const done = planProgressMin(cfg), total = CUR.totalHours * 60;
  const pcur = curPhaseIndex(cfg);
  const pct = Math.min(100, Math.round(done / total * 100));
  const logged = loggedMinutes();

  let h = `<div class="jr-top">
      <div class="jr-pct">${pct}%</div>
      <div class="jr-sum"><b>${Math.round(done / 60)}</b> of ${CUR.totalHours} hours ·
        you're in phase ${pcur + 1}, <b>${esc(CUR.phases[pcur].name)}</b>
        <div class="jr-sub">${Math.round(logged / 60)}h logged here${
          cfg.baseMinutes ? ' · ' + Math.round(cfg.baseMinutes / 60) + 'h credited from your placement' : ''} ·
          ${Math.round(wk / 60 * 10) / 10}h a week</div></div>
    </div>
    <div class="jr-bar"><i style="width:${pct}%"></i></div>`;

  if (wk <= 0) {
    h += `<div class="unval">You haven't set any study hours, so there's nothing to project.
      <button class="lnk" style="background:none;border:none;color:var(--verdigris);cursor:pointer;font:inherit;padding:0"
        onclick="location.hash='/plan/new'">Set your week →</button></div>`;
    $('view').innerHTML = h; return;
  }

  // Phase bands with real start/end dates.
  // "The seven phases" was true of Arabic and of nothing else. Hebrew's plan is three, because
  // that is how far its content reaches, and the heading has to say what the data says.
  const NUM = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'];
  h += `<div class="sec">The ${NUM[(CUR.phases || []).length] || (CUR.phases || []).length} phases</div><div class="jr-phases">`;
  h += CUR.phases.map((p, i) => {
    const startMin = phaseStartMin(i), endMin = phaseBounds()[i];
    const state = i < pcur ? 'done' : i === pcur ? 'now' : 'ahead';
    const from = i <= pcur ? (i < pcur ? 'done' : 'now') : fmtMY(projDateISO(cfg, startMin));
    const to = fmtMY(projDateISO(cfg, endMin));
    const within = i === pcur
      ? Math.round((done - startMin) / (endMin - startMin) * 100) : (i < pcur ? 100 : 0);
    return `<div class="jr-ph ${state}">
      <span class="jr-dot" style="background:${PHASE_COLOR[i]}"></span>
      <div class="jr-ph-b">
        <div class="jr-ph-h"><b>${i + 1}. ${esc(p.name)}</b>
          <span class="jr-ph-when">${from === 'done' ? 'done' : from === 'now' ? 'now → ' + to : from + ' → ' + to}</span></div>
        <div class="jr-ph-goal">${lvlTag(i)} ${esc(p.milestone)}</div>
        <div class="jr-mini"><i style="width:${within}%;background:${PHASE_COLOR[i]}"></i></div>
        <div class="jr-ph-n">${p.hours}h${i === pcur ? ` · ${Math.max(0, Math.round((endMin - done) / 60))}h to go` : ''}</div>
      </div></div>`;
  }).join('');
  h += `</div>`;

  // What the tags on every story, unit and lesson in the app actually mean.
  h += `<div class="sec">How the levels on content work</div>
    <p class="hint">Everything in the app carries a tag like
      ${lvlTag(2)} — the level, the CEFR band, and the phase of this plan that serves it.
      Tags are computed from the plan itself, so content is never labelled a level the plan
      doesn't actually give you at that point.</p>
    <table class="lvl-key">${(CUR.levels || []).map((L, i) => `<tr>
        <td>${lvlTag(i)}</td>
        <td><span class="k-n">${esc((CUR.phases[i] || {}).name || '')}</span>
          <div class="k-g">${esc((CUR.phases[i] || {}).milestone || '')}</div></td></tr>`).join('')}</table>
    <div class="note" style="margin-bottom:18px"><b>CEFR here is a signpost, not a certificate.</b>
      The bands come from this plan's own hour budget read against how long Arabic actually takes —
      the US Foreign Service Institute puts it in its hardest group, ~2,200 class hours to
      professional working proficiency. Two things to keep in mind: CEFR describes a whole language
      including reading and writing, while this plan trains <i>spoken</i> Palestinian; and nobody
      here is examining you. Use it to judge whether a text is worth your time, not as a score.</div>`;

  // Month grid: one cell per month from the start of this month to the projected finish.
  h += `<div class="sec">Every month from here to fluent</div>
    <p class="hint">One square per month, numbered and coloured by the phase you'll be in.
      Read the phase numbers against the list above; the outlined square is this month.</p>`;
  const start = isoToDate(todayISO());
  const blank = '<span class="jr-m off"></span>';
  let acc = done, y = start.getFullYear(), m = start.getMonth(), rows = [], curY = y;
  let cells = Array(m).fill(blank);                      // pad so column 1 is always January
  let guard = 0;
  while (acc < total && guard++ < 240) {                 // 20 years of headroom; loop cannot run away
    const dim = new Date(y, m + 1, 0).getDate();
    const idx = phaseIndexFor(Math.min(acc, total - 1));
    if (y !== curY) { rows.push([curY, cells]); cells = []; curY = y; }
    const isNow = y === start.getFullYear() && m === start.getMonth();
    cells.push(`<span class="jr-m${isNow ? ' now' : ''}"
        title="${MON[m]} ${y} — phase ${idx + 1}, ${esc(CUR.phases[idx].name)}${isNow ? ' (you are here)' : ''}"
        style="background:${PHASE_COLOR[idx]}">${idx + 1}</span>`);
    acc += perDay * dim;
    m++; if (m > 11) { m = 0; y++; }
  }
  rows.push([curY, cells]);
  h += `<div class="jr-hd"><span></span><div class="jr-ms">`
     + MON.map(mo => `<span class="jr-mh">${mo[0]}</span>`).join('') + `</div></div>`;
  h += `<div class="jr-years">` + rows.map(([yr, cs]) =>
    `<div class="jr-year"><span class="jr-yl">${yr}</span><div class="jr-ms">${cs.join('')}</div></div>`).join('') + `</div>`;

  const flu = projDateISO(cfg, total);
  h += `<div class="note"><b>${flu ? fmtMY(flu) : '—'}</b> is where ${Math.round(wk / 60 * 10) / 10} hours a week
    lands you on the ~${CUR.totalHours}-hour estimate. It is arithmetic, not a promise: the estimate itself is
    rough, and the date moves with the hours you actually do. Miss a week and it slides a week; add an hour a
    day and it pulls in by months. The one thing that doesn't help is a different plan.</div>`;

  h += `<div class="ctl" style="margin-top:16px">
      <button class="tog" onclick="location.hash='/plan/calendar'">Next four weeks</button>
      <button class="tog" onclick="location.hash='/plan'">Back to today</button>
      <button class="tog" onclick="location.hash='/plan/new'">Change my hours</button>
      <button class="tog go" onclick="planReassess()">Re-take the placement</button></div>`;
  $('view').innerHTML = h;
}

// Re-taking the placement is allowed at ANY time — from Today, the journey or the dashboard. It
// re-bases which phase you're in without touching a single completed task in the log.
function planReassess() {
  if (!confirm('Re-take the ~' + asMins() + '-minute placement?\n\nIt re-bases which phase you start from. '
             + 'Everything you have already completed stays exactly as it is.')) return;
  _as = null;
  location.hash = '/plan/new/assess';
}

function planCalendar() {
  const cfg = planCfg(); if (!cfg) { location.hash = '/plan'; return; }
  $('title').textContent = 'The plan ahead';
  const wk = weeklyMin(cfg);
  const bounds = phaseBounds();
  const flu = projDateISO(cfg, CUR.totalHours * 60);

  let h = `<div class="note"><b>Your projection.</b> At ${Math.round(wk / 60 * 10) / 10} hours a week, you’re on
    track for <b>${flu ? fmtMY(flu) : '—'}</b> to reach the ~${CUR.totalHours}-hour mark that the spoken-fluency
    estimate assumes. That’s a target, not a promise — the honest truth is it depends on showing up. Miss days and
    this date simply slides; keep going and it holds.</div>`;

  // upcoming phase milestones
  const pcur = curPhaseIndex(cfg);
  h += `<div class="sec">Milestones ahead</div><div class="pmiles">`;
  h += CUR.phases.map((p, i) => {
    const reached = i < pcur;
    const at = i <= pcur ? (i === pcur ? 'now' : 'done') : (wk > 0 ? fmtMY(projDateISO(cfg, phaseStartMin(i))) : '—');
    return `<div class="pmile${i === pcur ? ' on' : ''}${reached ? ' past' : ''}">
       <span class="pm-dot" style="background:${PHASE_COLOR[i]}"></span>
       <span class="pm-name">${esc(p.name)}</span>
       <span class="pm-goal">${esc(p.milestone)}</span>
       <span class="pm-at">${at}</span></div>`;
  }).join('');
  h += `</div>`;

  // 4-week look-ahead, projecting phase forward by assumed completion
  h += `<div class="sec">Next four weeks</div>`;
  let proj = planProgressMin(cfg);
  const today = todayISO();
  for (let w = 0; w < 4; w++) {
    h += `<div class="pweek">`;
    for (let i = 0; i < 7; i++) {
      const date = addDaysISO(today, w * 7 + i);
      const day = buildDay(cfg, phaseIndexFor(proj), date, null);
      const isToday = date === today;
      h += `<div class="pday${day.rest ? ' rest' : ''}${isToday ? ' today' : ''}"
          style="border-left-color:${day.rest ? 'var(--rule)' : (PHASE_COLOR[day.phase.id] || 'var(--verdigris)')}"
          ${day.rest ? '' : `onclick="location.hash='/plan'"`}>
          <div class="pd-d"><b>${WD[isoToDate(date).getDay()]}</b><span>${fmtMD(date)}</span></div>
          <div class="pd-b">${day.rest ? '<span class="pd-rest">Rest</span>'
            : `<span class="pd-ph">${esc(day.phase.name)}</span>
               <span class="pd-n">${day.tasks.length} task${day.tasks.length === 1 ? '' : 's'} · ${Math.round(day.totalMin / 60 * 10) / 10}h${day.spoken ? ' · 🗣' : ''}</span>`}</div>
        </div>`;
      if (!day.rest) proj += day.totalMin;
    }
    h += `</div>`;
  }
  h += `<div class="ctl" style="margin-top:18px">
     <button class="tog go" onclick="location.hash='/plan/journey'">See the whole journey →</button>
     <button class="tog" onclick="location.hash='/plan'">Back to today</button>
     <button class="tog" onclick="location.hash='/plan/new'">Adjust my time</button></div>`;
  $('view').innerHTML = h;
}

// ---------- Translate (Reverso-Context style: dictionary + real in-context examples) ----------
// Fully offline, from the app's own looked-up data: an index of every word that appears in the
// corpus (stories / news / book) and the bilingual sentences it lives in. No machine translation,
// no external calls — so every line shown is real Palestinian dialect with a source you can open.
// The identity every deck key, SRS key and lexicon lookup is built on. It stays a named
// function with one definition and ~34 untouched call sites; only the body moved.
function arNorm(s) { return LANG.script.norm(s); }
// Is there any target-script text in here? Every place that asked this used a hardcoded Arabic
// Unicode block, which for a Hebrew learner answered "no" to every Hebrew word they typed --
// the translator read ספר as English and returned nothing.
const isTargetScript = t => LANG.script.chars.test(String(t == null ? '' : t));
const glossWords = g => String(g || '').toLowerCase().replace(/_/g, ' ').split(/[;·,()\/\s]+/).filter(Boolean);

let _tridx = null, _trQ = '', _trT = null;

// Every bilingual line the app ships OUTSIDE the corpus: reactions, pronunciation examples,
// dinner-table dialogue, lesson chunks and their replies, grammar examples. Each is a real
// Palestinian sentence with a real translation — exactly what Translate exists to show — but
// none of it lived in LIB.texts, so none of it was findable. Measured before this change:
// 3,348 distinct word-forms existed somewhere in the app and nowhere in the translator.
let _trLines = null;
function trCuratedLines() {
  if (_trLines) return _trLines;
  const out = [];
  const add = (ar, en, where, hash) => { if (ar && en) out.push({ar, en, where, hash}); };
  (RX.items || []).forEach(r => add(r.ar, r.en, 'Reactions', '#/reactions'));
  (SND.lessons || []).forEach(l => (l.examples || []).forEach(x =>
    add(x.ar, x.en, 'Sounds · ' + l.en, '#/sounds/' + l.id)));
  (TBL.dialogues || []).forEach(d => (d.lines || []).forEach(l =>
    add(l.ar, l.en, 'Dinner table · ' + ((d.title && d.title.en) || d.id), '#/table/' + d.id)));
  (LSN.units || []).forEach(u => {
    const w = 'Lesson ' + u.n + ' · ' + ((u.title && u.title.en) || '');
    (u.chunks || []).forEach(c => { add(c.ar, c.en, w, '#/lessons/' + u.id);
      if (c.reply) add(c.reply.ar, c.reply.en, w, '#/lessons/' + u.id); });
    if (u.grammar) (u.grammar.examples || []).forEach(x => add(x.ar, x.en, w, '#/lessons/' + u.id));
  });
  GRAM.forEach(l => (l.examples || []).forEach(x =>
    add(x.ar, x.en, 'Grammar · ' + (l.title || l.id), '#/grammar/' + l.id)));
  _trLines = out;
  return out;
}

// EVERY source below is spoken Palestinian: LIB.texts (stories, news, book chapters, lessons),
// verbs.js (Maknuune, a Palestinian lexicon), and the curated decks. The Van Dyck Bible is
// deliberately absent — it is Classical Arabic from 1865, it ships in its own lazily-loaded
// files, and it must stay out of both the translator and the vocabulary deck. If a new content
// type is ever added here, check what dialect it is first.
function trIndex() {
  if (_tridx) return _tridx;
  const byKey = new Map();
  const ent = (key, raw, lemma, w) => { let e = byKey.get(key);
    if (!e) { e = {key, raw, lemma, gloss: (w && w.gloss) || '', root: (w && w.root) || '',
                   caphi: (w && (w.caphi_urban || w.caphi)) || '', vb: null, hits: [], surf: new Set()};
      byKey.set(key, e); }
    if (!e.gloss && w && w.gloss) e.gloss = w.gloss;
    if (!e.root && w && w.root) e.root = w.root;
    return e; };
  LIB.texts.forEach(t => (t.sentences || []).forEach((s, si) => s.words.forEach((w, wi) => {
    if (!w.lemma) return;
    const key = arNorm(w.lemma); if (!key) return;
    const e = ent(key, w.lemma, w.vocalized || w.form || w.lemma, w);
    e.surf.add(arNorm(w.surface));
    if (e.hits.length < 80) e.hits.push({tid: t.id, si, wi});
  })));
  // Every verb that ships with a paradigm becomes findable, whether or not it was ever used in
  // a text — 1,873 of the 3,003 had no corpus occurrence, so searching them returned nothing.
  VB.forEach(v => { const key = arNorm(v.lemma); if (!key) return;
    const e = ent(key, v.lemma, v.lemma, {gloss: v.gloss, root: v.root,
                                          caphi: (verbCite(v) || {}).caphi});
    if (e.vb == null) e.vb = v._i;
    ['past', 'pres', 'imp'].forEach(k => { if (v[k] && v[k].ar) e.surf.add(arNorm(v[k].ar)); });
  });
  // Curated lines: index their words, and keep the line itself as a usable example.
  trCuratedLines().forEach((ln, li) => {
    String(ln.ar).split(/[\s،.؟!:؛…"«»“”'()\-—\[\]{}\\\/,;?]+/).filter(Boolean).forEach(tok => {
      const key = arNorm(tok); if (!key) return;
      const r = lexLook(tok);
      const e = ent(key, (r && r.lemma) || tok, (r && (r.vocalized || r.form)) || tok, r || null);
      e.surf.add(key);
      if (e.hits.length < 80) e.hits.push({lit: li});
    });
  });
  _tridx = {all: [...byKey.values()], byKey};
  return _tridx;
}
const trDedupe = list => { const seen = new Set(), out = []; list.forEach(e => { if (!seen.has(e.key)) { seen.add(e.key); out.push(e); } }); return out; };
function trLookupAr(idx, tk) { const k = arNorm(tk); return idx.byKey.get(k) || idx.all.find(e => e.surf.has(k)) || null; }
function trMatchAr(idx, q) { const k = arNorm(q);
  const exact = idx.all.filter(e => e.key === k || e.surf.has(k));
  return (exact.length ? exact : idx.all.filter(e => e.key.includes(k) || [...e.surf].some(s => s.includes(k)))).slice(0, 12); }
function trSearch(q) {
  q = (q || '').trim(); if (!q) return {type: 'empty'};
  const idx = trIndex();
  if (isTargetScript(q)) {
    const toks = q.split(/\s+/).filter(Boolean);
    if (toks.length > 1) return {type: 'ar-sentence', q, toks: toks.map(tk => ({tk, e: trLookupAr(idx, tk)}))};
    return {type: 'ar-word', q, entries: trMatchAr(idx, q)};
  }
  const ql = q.toLowerCase();
  const score = e => { const g = (e.gloss || '').toLowerCase().replace(/_/g, ' '); const gw = glossWords(e.gloss);
    if (g === ql) return 0; if (gw[0] === ql) return 1; if (gw.includes(ql)) return 2; if (g.includes(ql)) return 3; return 9; };
  const entries = trDedupe(idx.all.filter(e => score(e) < 9)
    .sort((a, b) => score(a) - score(b) || (a.gloss || '').length - (b.gloss || '').length)).slice(0, 15);
  return {type: 'en', q, entries};
}

function translateSection() {
  $('back').hidden = false; $('title').textContent = 'Translate';
  $('view').innerHTML = `
    <p class="hint">Type a word or phrase — ${esc(LANG.short)} <b>or</b> English — to see what it means and,
      Reverso-style, real sentences from the app’s own texts where it’s actually used. Everything is from the
      ${esc(LANG.lex.name)} lexicon and those texts, with a source for every line.</p>
    ${kbdWrap(`<input id="tr-q" class="vsearch" type="search" inputmode="search" autocomplete="off"
      placeholder="${esc(LANG.searchHint)}" value="${esc(_trQ)}" oninput="trOnInput(this.value)">`, 'tr-q')}
    <div id="tr-out"></div>`;
  const inp = $('tr-q'); if (inp) { inp.focus(); if (_trQ) trRender(_trQ); }
}
function trOnInput(v) { _trQ = v; if (_trT) clearTimeout(_trT); _trT = setTimeout(() => trRender(v), 250); }
function trRender(v) {
  const out = $('tr-out'); if (!out) return;
  const r = trSearch(v);
  if (r.type === 'empty') { out.innerHTML = ''; return; }
  if (r.type === 'ar-sentence') { out.innerHTML = trSentenceHTML(r); return; }
  out.innerHTML = r.entries.length ? r.entries.map(trEntryHTML).join('') : trNotFound(v);
}
function trEntryHTML(e) {
  const ex = e.hits.slice(0, 6).map(trExHTML).filter(Boolean).join('');
  return `<div class="tr-entry">
    <div class="tr-head">
      <span class="tr-word" dir="rtl">${esc(e.lemma)}</span>
      <button class="say" onclick="playWord({lemma:'${cssq(e.raw)}',vocalized:'${cssq(e.lemma)}',caphi:'${cssq(e.caphi)}'})" aria-label="Pronounce">${svg('spk')}</button>
      <span class="tr-gloss">${esc(pretty(e.gloss) || '—')}</span>
    </div>
    ${e.root ? `<div class="tr-root">root ${esc((e.root || '').replace(/\./g, ' · '))}${e.caphi ? ' &nbsp;·&nbsp; ' + esc(e.caphi) : ''}</div>` : ''}
    <div class="tr-acts">
      ${deckBtnHTML(e.raw, `deckToggleLex('${cssq(e.raw)}','tr')`)}
      ${e.vb != null && VB[e.vb] && VB[e.vb].hasConj
        ? `<a class="tr-vb" href="#/verb/${e.vb}">See the full conjugation →</a>` : ''}</div>
    ${ex ? `<div class="tr-exs"><div class="tr-exs-h">In context</div>${ex}</div>` : ''}
  </div>`;
}
function trExHTML(hit) {
  if (hit.lit != null) {                      // a curated line (reaction, lesson chunk, dialogue…)
    const ln = trCuratedLines()[hit.lit]; if (!ln) return '';
    return `<div class="tr-ex" onclick="location.hash='${cssq(ln.hash)}'">
      <div class="tr-ex-ar" dir="rtl">${esc(ln.ar)}</div>
      <div class="tr-ex-en">${esc(ln.en)} <span class="tr-ex-src">— ${esc(ln.where)}</span></div></div>`;
  }
  const t = LIB.texts.find(x => x.id === hit.tid); if (!t) return '';
  const s = t.sentences[hit.si]; if (!s) return '';
  const ar = s.words.map((w, i) => `<span class="${i === hit.wi ? 'tr-hl' : ''}">${esc(w.vocalized || w.surface)}</span>`).join(' ');
  return `<div class="tr-ex" onclick="location.hash='/text/${esc(hit.tid)}'">
    <div class="tr-ex-ar" dir="rtl">${ar}</div>
    <div class="tr-ex-en">${esc(s.en)} <span class="tr-ex-src">— ${esc((t.title && t.title.en) || t.id)}</span></div></div>`;
}
function trSentenceHTML(r) {
  let h = `<div class="tr-exs-h">Word by word</div><div class="tr-wbw">`;
  h += r.toks.map(({tk, e}) => `<div class="tr-tok">
      <span class="tr-tok-ar" dir="rtl">${esc(tk)}</span>
      <span class="tr-tok-gl">${e ? esc(pretty(e.gloss) || '—') : '<i>not in the app’s words</i>'}</span></div>`).join('');
  h += `</div>`;
  const best = r.toks.filter(x => x.e && x.tk.length >= 3).sort((a, b) => b.tk.length - a.tk.length)[0];
  if (best) { const ex = best.e.hits.slice(0, 5).map(trExHTML).filter(Boolean).join('');
    if (ex) h += `<div class="tr-exs"><div class="tr-exs-h">Sentences using “${esc(best.tk)}”</div>${ex}</div>`; }
  return h;
}
function trNotFound(v) { return `<div class="empty"><div class="empty-t">No match yet</div>
  <p>“${esc(v)}” isn’t among the words in the app’s texts and lexicon-backed vocabulary. Try a simpler or more
  common form of the word — the library grows as more stories and books are added.</p></div>`; }

// ---------- Grammar lessons ----------
// Spoken-Palestinian structures. Explanations + the closed-class paradigm tables are
// hand-written (curated function words); every EXAMPLE SENTENCE is a real one pulled from
// the app's corpus, where each word was looked up in Maknuune. See pipeline/grammar.py.
const GRAM = (window.GRAMMAR && window.GRAMMAR.lessons) || [];
const GRAM_INTRO = (window.GRAMMAR && window.GRAMMAR.intro) || '';
const gramById = id => GRAM.find(l => l.id === id);

function grammarSection(sub){
  $('back').hidden = false;
  if (sub && gramById(sub)) return grammarLesson(sub);
  return grammarHome();
}

function grammarHome(){
  $('title').textContent = 'Grammar Lessons';
  // The blurb is the language's own: Arabic's grammar section is about the present tense and
  // negation, Hebrew's is about the binyanim, and one hardcoded paragraph cannot be both.
  let h = `${GRAM_INTRO ? `<p class="hint">${GRAM_INTRO}</p>` : ''}<div class="vtiles">`;
  h += GRAM.map((l, i) => `<button class="vtile wide" onclick="location.hash='/grammar/${l.id}'">
      <div class="vtile-h"><span class="vtile-t">${esc(l.title)}</span>
        <span class="vtile-n">${i + 1}</span></div>
      <div class="vtile-s" dir="auto">${lvlTagFor('grammar', {n: i})} ${esc(l.sub)}</div></button>`).join('');
  h += `</div>`;
  $('view').innerHTML = h;
}

// Bold the tokens that demonstrate the pattern. `hi` holds cleaned surfaces (matching the
// same stripping pipeline/grammar.py used), so we clean each token the same way to compare.
// The highlight marks the structure the lesson is about; arLive() makes each word tappable
// underneath it, so "what is this word?" and "what is this pattern?" are both answerable here.
function gexMore() {
  const box = $('gex-more'), btn = $('gex-more-btn');
  if (!box) return;
  box.hidden = !box.hidden;
  btn.textContent = box.hidden
    ? 'Show ' + box.children.length + ' more example' + (box.children.length === 1 ? '' : 's')
    : 'Show fewer';
  if (!box.hidden) lexPaint();     // the newly-revealed examples need their marked words painted
}

function gramHi(ar, hi){
  const set = new Set(hi || []);
  return ar.split(/(\s+)/).map(tok => {
    const c = tok.replace(/[،.؟!:؛…"«»”“\-—()]/g, '');
    return (c && set.has(c)) ? `<b class="gx">${arLive(tok)}</b>` : arLive(tok);
  }).join('');
}

function grammarLesson(id){
  const l = gramById(id);
  $('title').textContent = l.title;
  const idx = GRAM.findIndex(x => x.id === id);
  // dir="ltr", not "auto". These paragraphs are English prose about a right-to-left language,
  // and dir="auto" takes its direction from the first strong character — so a sentence that
  // opens with its subject, "נִפְעַל puts a נ on the front…", flipped the whole paragraph and
  // read backwards. The embedded Hebrew and Arabic still lay out right-to-left inside it.
  let h = `<div class="gsub" dir="ltr">${esc(l.sub)}</div>`;
  h += `<div class="gbody">${(l.body || []).map(p => `<p dir="ltr">${p}</p>`).join('')}</div>`;

  (l.tables || []).forEach(t => {
    h += `<div class="sec">${esc(t.title)}</div><div class="gtable">`;
    h += t.rows.map(r => `<div class="grow">
        <span class="g-ar">${esc(r[0])}</span>
        <span class="g-tr">${esc(r[1])}</span>
        <span class="g-en">${esc(r[2])}</span></div>`).join('');
    h += `</div>`;
  });

  // Each lesson carries 30 examples, each from a DIFFERENT text (pipeline/grammar.py). Thirty
  // at once is a wall, so the page opens with six and the rest are one tap away — enough to see
  // the pattern immediately, and enough to keep reading if it hasn't landed. The count is read
  // from the data, not hard-coded, so changing n in the pipeline needs no change here.
  if (l.examples && l.examples.length){
    const GEX_SHOWN = 6;
    const one = e => {
      const t = LIB.texts.find(x => x.id === e.src);
      return `<div class="gex">
        <div class="gex-ar" dir="rtl">${gramHi(e.ar, e.hi)}</div>
        <div class="gex-en">${esc(e.en)}</div>
        ${t ? `<button class="gex-src" onclick="location.hash='/text/${esc(e.src)}'">Read “${esc(e.title)}” in full →</button>` : ''}
      </div>`;
    };
    const nsrc = new Set(l.examples.map(e => e.src)).size;
    h += `<div class="sec">In real sentences</div>
      <p class="hint gex-hint">${l.examples.length} sentence${l.examples.length === 1 ? '' : 's'} from
        ${nsrc} different ${nsrc === 1 ? 'text' : 'texts'} in the app — every one real, every word
        looked up in the lexicon.</p>`;
    h += l.examples.slice(0, GEX_SHOWN).map(one).join('');
    const rest = l.examples.slice(GEX_SHOWN);
    if (rest.length) {
      h += `<div id="gex-more" hidden>${rest.map(one).join('')}</div>
        <button class="tog gex-more-btn" id="gex-more-btn"
          onclick="gexMore()">Show ${rest.length} more example${rest.length === 1 ? '' : 's'}</button>`;
    }
  }

  // "Every example above" is a lie on a lesson with no examples, and Hebrew has two: פועל and
  // הופעל are too rare in real speech for the corpus to illustrate honestly, and they say so in
  // their own text. The provenance claim still needs making, just about the tables instead.
  h += `<div class="note">${l.examples && l.examples.length
    ? `Every example above is a real sentence from this app's texts — the words were looked up in
       ${esc(LANG.lex.name)}, not invented. The explanation and the tables are written by us to
       orient you; they describe`
    : `Every word in the tables above was looked up in ${esc(LANG.lex.name)}, not invented. The
       explanation is written by us to orient you; it describes`}
    ${esc(LANG.lex.usage)}.</div>`;

  // prev / next lesson
  h += `<div class="ctl" style="margin-top:16px">`;
  if (idx > 0) h += `<button class="tog" onclick="location.hash='/grammar/${GRAM[idx - 1].id}'">← ${esc(GRAM[idx - 1].title)}</button>`;
  if (idx < GRAM.length - 1) h += `<button class="tog" onclick="location.hash='/grammar/${GRAM[idx + 1].id}'">${esc(GRAM[idx + 1].title)} →</button>`;
  h += `<button class="tog" onclick="location.hash='/grammar'">All lessons</button></div>`;
  $('view').innerHTML = h;
}

// ---------- verbs section ----------
function verbsSection(sub){
  $('back').hidden = false;
  if (sub && FORM_INFO[sub]) return verbsForm(sub);
  if (sub === 'irregular')   return verbsIrregular();
  return verbsHome();
}

// One verb → a card with its root, gloss, badges and the three principal parts. The
// principal parts are the skeleton of the whole paradigm; full conjugations come later.
function verbCard(v){
  const badges = `<span class="b-form">${esc(v.form === 'Q' ? 'Quad' : v.form)}</span>` +
    (WEAK_INFO[v.weak] ? `<span class="b-wk">${esc(WEAK_INFO[v.weak][0].toLowerCase())}</span>` : '') +
    (v.hasConj ? `<span class="b-cj">conjugates</span>` : '');
  const root = esc((v.root || '').replace(/\./g, ' · '));
  const part = (k, pp) => pp ? `<div class="pp">
      <span class="pp-k">${k}</span>
      <span class="pp-ar">${esc(pp.ar)}</span>
      <span class="pp-c">${esc(pp.caphi)}</span></div>` : '';
  return `<button class="vc" onclick="location.hash='/verb/${v._i}'">
    <div class="vc-h"><span class="vc-gl">${esc(v.gloss || '—')}</span>
      <span class="vc-badges">${badges}</span></div>
    <div class="vc-root">${root}</div>
    <div class="vc-pp">
      ${LANG.verb.summary.map(([k, label]) => part(label, v[k])).join('')}</div>
  </button>`;
}

// Person rows, in the reference's order. label = English, ar = the pronoun.
const PERSONS = LANG.verb.persons;

function verbDetail(i){
  const v = VB[+i];
  $('back').hidden = false;
  if (!v) { $('title').textContent = 'Verb'; $('view').innerHTML =
      `<p class="hint">That verb isn’t loaded. <a href="#/verbs">Back to verbs</a>.</p>`; return; }
  $('title').textContent = v.gloss ? v.gloss.split(' · ')[0] : 'Verb';
  const badges = `<span class="b-form">${esc(v.form === 'Q' ? 'Quad' : v.form)}</span>` +
    (WEAK_INFO[v.weak] ? `<span class="b-wk">${esc(WEAK_INFO[v.weak][0].toLowerCase())}</span>` : '');
  const root = esc((v.root || '').replace(/\./g, ' · '));

  let h = `<div class="vd-head">
    <div class="vd-ar">${esc((verbCite(v) || {}).ar || '')}</div>
    <div class="vd-meta"><div class="vd-gl">${esc(v.gloss || '—')}</div>
      <div class="vd-sub">${root} &nbsp;·&nbsp; ${badges}</div>
      <div class="vd-lvl">${lvlTagFor('verb', {tier: LANG.verb.tier(v)})}</div>
      <div class="vd-deck">${deckBtnHTML(v.lemma, `deckToggleVerb(${+i})`, '+ Add this verb to my deck')}</div>
      </div></div>`;
  // Where the reference grammar and the lexicon disagree on how a verb is vowelled, the
  // grammar wins and we say so — the variant is real speech, not an error to hide.
  if (v.note) h += `<div class="vd-note">${esc(v.note)}</div>`;

  const c = v.conj;
  if (!c) {
    h += `<div class="unval" style="border-color:var(--rule);background:var(--paper-2)">
      <b style="color:var(--verdigris)">Principal parts.</b> Full conjugation tables for
      this class are being added in a later wave — verified against the reference before
      they ship. Here are the three parts every form is built from.</div>`;
    const part = (k, pp) => pp ? `<div class="pp"><span class="pp-k">${k}</span>
        <span class="pp-ar">${esc(pp.ar)}</span><span class="pp-c">${esc(pp.caphi)}</span></div>` : '';
    h += `<div class="vc-pp" style="max-width:420px">
        ${LANG.verb.summary.map(([k, label]) => part(label, v[k])).join('')}</div>`;
    $('view').innerHTML = h;
    return;
  }

  h += paradigmHTML(v, 'cj');

  const cls = (WEAK_INFO[v.weak] ? WEAK_INFO[v.weak][0].toLowerCase() + ' ' : '') + 'Form ' + v.form;
  h += `<div class="note">Conjugations are <b>derived by rule</b> from this verb’s principal
    parts, then verified against <i>Palestinian Arabic Verbs</i> (Aldrich, Lingualism): the
    engine reproduces 99%+ of the book’s ${esc(cls)} cells, the rest being optional vowel
    reductions that vary in everyday speech. Arabic is shown unvocalized, the way it’s written.</div>`;
  $('view').innerHTML = h;
}

function verbsHome(){
  $('title').textContent = 'Verbs';
  // How a language builds verbs is the pack's to explain: Arabic has measures on a root,
  // Hebrew has binyanim. Saying "measures I-X" over a Hebrew verb list was the loudest thing
  // left in here that assumed the language.
  let h = `<p class="hint">${LANG.verb.blurb(VB.length)}</p>`;

  h += kbdWrap(`<input id="vsearch" class="vsearch" type="search" inputmode="search"
    placeholder="Search ${VB.length} verbs — English, root or ${esc(LANG.short)}…"
    oninput="verbSearch(this.value)" aria-label="Search verbs">`, 'vsearch')
    + `<div id="vsearchout"></div>`;

  h += `<div class="sec">${esc(LANG.verb.classPlural)}</div><div class="vtiles">`;
  h += FORM_ORDER.map(f => {
    const n = byForm(f).length; if (!n) return '';
    const [label, desc] = FORM_INFO[f];
    return `<button class="vtile" onclick="location.hash='/verbs/${f}'">
      <div class="vtile-h"><span class="vtile-t">${esc(label)}</span>
        <span class="vtile-n">${n}</span></div>
      <div class="vtile-s">${esc(desc)}</div></button>`;
  }).join('');
  h += '</div>';

  // Only when the pack has a weak-class model at all. Hebrew's gzarot are real but not yet
  // labelled in the data, and an empty shelf reading "Irregular verbs 0" is a worse answer
  // than no shelf.
  if (LANG.verb.weakOrder.length) {
    h += `<div class="sec">Cross-cutting</div>
      <button class="vtile wide" onclick="location.hash='/verbs/irregular'">
        <div class="vtile-h"><span class="vtile-t">Irregular / weak verbs</span>
          <span class="vtile-n">${irregular.length}</span></div>
        <div class="vtile-s">${esc(LANG.verb.weakBlurb)}</div></button>`;
  }
  $('view').innerHTML = h;
}

// Live search across all verbs. Kept simple: substring over gloss, root and Arabic.
function verbSearch(q){
  const out = $('vsearchout'); if (!out) return;
  q = (q || '').trim().toLowerCase();
  if (q.length < 2) { out.innerHTML = ''; return; }
  // Score so the verb you meant floats up: an exact gloss sense beats a word that merely
  // starts with q, which beats a bare substring ("eat" shouldn't rank "seat" first).
  const wordRe = new RegExp('(^|[\\s·])' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const qAr = /[\u0600-\u06FF]/.test(q), qn = arNorm(q);
  const score = v => {
    const g = (v.gloss || '').toLowerCase();
    if (g.split(' · ').includes(q)) return 0;          // exact sense
    if (wordRe.test(g))             return 1;          // a sense word starts with q
    if (g.includes(q))              return 2;          // gloss substring
    if ((v.root || '').includes(q)) return 3;          // root
    if ([v.past, v.pres, v.imp].some(p => p && (p.ar.includes(q) || p.caphi.toLowerCase().includes(q))))
      return 4;                                        // arabic / pronunciation
    // Every form in here is fully vocalized (رَاح), but nobody types the diacritics — not on a
    // physical Arabic keyboard and not on ours. Without this, searching Arabic never matched.
    if (qAr) {
      if (arNorm((v.root || '').replace(/\./g, '')).includes(qn)) return 5;
      if ([v.past, v.pres, v.imp].some(p => p && arNorm(p.ar).includes(qn))) return 6;
    }
    return 99;
  };
  const hits = VB.map(v => [score(v), v]).filter(x => x[0] < 99)
    .sort((a, b) => a[0] - b[0]).map(x => x[1]).slice(0, 60);
  out.innerHTML = hits.length
    ? `<div class="sec">${hits.length}${hits.length === 60 ? '+' : ''} match${hits.length===1?'':'es'}</div>` +
      `<div class="vlist">${hits.map(verbCard).join('')}</div>`
    : `<p class="hint">No verb matches “${esc(q)}”.</p>`;
}

function verbsForm(f){
  const [label, desc] = FORM_INFO[f];
  $('title').textContent = label;
  const list = byForm(f);
  let h = `<div class="unval" style="border-color:var(--rule);background:var(--paper-2)">
    <b style="color:var(--verdigris)">${esc(label)}.</b> ${esc(desc)}</div>`;
  h += `<div class="sec">${list.length} verbs</div>`;
  h += `<div class="vlist">${list.map(verbCard).join('')}</div>`;
  $('view').innerHTML = h;
}

function verbsIrregular(){
  $('title').textContent = 'Irregular verbs';
  let h = `<p class="hint">Weak verbs carry a و, ي or ء in the root that shifts or
    disappears when conjugated. They cut across all the forms. Grouped here by the kind
    of weakness so the patterns sit side by side.</p>`;
  WEAK_ORDER.forEach(w => {
    const list = irregular.filter(v => v.weak === w); if (!list.length) return;
    const [label, desc] = WEAK_INFO[w];
    h += `<div class="sec">${esc(label)} · ${list.length}</div>
      <p class="hint" style="margin-bottom:12px">${esc(desc)}</p>
      <div class="vlist">${list.map(verbCard).join('')}</div>`;
  });
  $('view').innerHTML = h;
}

// An honest placeholder for a section with no content yet.
// A deep link to a section this language does not have. It exists in the app, just not here.
function sectionElsewhere(kind) {
  const d = SECTION_DEFS[kind];
  const other = (window.LANGUAGES || [])
    .find(p => p.code !== LANG.code && (p.sections || []).includes(kind));
  $('title').textContent = d.label;
  $('back').hidden = false;
  $('view').innerHTML = `<div class="empty">
    <div class="empty-t">${esc(d.label)} isn't part of ${esc(LANG.name)}</div>
    <p>This section belongs to ${other ? esc(other.name) : 'another language'}.</p>
    <div class="ctl" style="justify-content:center">
      ${other && other.ready !== false
        ? `<button class="tog go" onclick="switchLang('${other.code}')">
             <span style="font-size:15px">${other.flag}</span> Switch to ${esc(other.short)}</button>`
        : ''}
      <button class="tog" onclick="location.hash='/'">Back to home</button></div></div>`;
}

function emptySection(sec){
  $('back').hidden = false;
  $('title').textContent = sec.label;
  $('view').innerHTML =
    `<div class="empty">
       <div class="empty-t">${esc(sec.label)}</div>
       <p>Nothing here yet — this section is being built.</p>
     </div>`;
}

function card(t, kind){
  const isDrill = kind === 'drill';
  const n = isDrill ? 0 : t.sentences.reduce((a,s) =>
    a + s.words.filter(w => w.lemma && inDeckWord(w)).length, 0);
  return `<button class="card" onclick="location.hash='/${kind}/${esc(t.id)}'">
    ${!isDrill && t.title.ar ? `<div class="ar">${esc(t.title.ar)}</div>` : ''}
    <div class="en">${esc(t.title.en)}</div>
    <div class="meta">
      <span>${isDrill ? t.items.length+' chunks' : t._words+' words'}</span>
      ${n ? `<span style="color:var(--ochre)">${n} marked</span>` : ''}
      ${t.kind === 'news' ? '<span class="pill">news</span>' : ''}
      <span class="pill ${t._audio ? 'on' : 'off'}">${t._audio ? 'audio' : 'no audio'}</span>
    </div></button>`;
}

// ---------- reader ----------
let cur = null;
function reader(t) {
  cur = t;
  const _rp = readPrefs();                // vowels / English / marked, as you last left them
  PARA = null; paraStop();                // a fresh reader starts with no paragraph audio
  let paraClips = [];
  $('back').hidden = false;
  $('title').textContent = t.title.en;
  let h = `<div class="lvl-row">${lvlTagFor(textType(t), t)}
      <a class="lvl-what" href="#/plan/journey">what do these mean?</a></div>
    <div class="ctl">
      <button class="tog" id="tVoc" aria-pressed="${_rp.voc}">Vowels</button>
      <button class="tog" id="tEn" aria-pressed="${_rp.en}">English</button>
      <button class="tog" id="tMk" aria-pressed="${_rp.mk}">Show marked</button>
      <button class="tog sk-go" onclick="location.hash='/speak/${esc(t.id)}'">🗣 Speak it</button>
    </div>` +
    (/not native-validated/i.test(t.source || '')
      ? `<div class="unval"><b>Not checked by a native speaker.</b> Every word's root,
         meaning and vowels come from the lexicon — but the <i>sentences</i> were written
         by Claude. Fine for reading practice; don't memorise the phrasing yet.</div>`
      : '') +
    // Who wrote it. The reader never said, which was survivable while a book was one work by one
    // author and the cover carried the name — it is not now that a shelf holds a dozen people's
    // stories, and the reader is where most of them are opened from.
    // Gated on `register`, which marks a text that was SELECTED verbatim rather than retold. The
    // Arabic books carry book_meta too, but Jules Verne did not write their Arabic — printing his
    // name over a Claude retelling would be the same misattribution pointing the other way.
    ((t.register && t.book_meta && t.book_meta.author)
      ? `<div class="bk-src">${esc(t.book_meta.author)}${t.book_meta.year ? ', ' + esc(t.book_meta.year) : ''}${
          t.book_meta.url ? ` · <a href="${esc(t.book_meta.url)}" target="_blank" rel="noopener"
             style="color:var(--verdigris)">Project Ben-Yehuda</a>` : ''}</div>`
      : '') +
    `<div class="rd" id="rd" data-en="${_rp.en ? 'on' : 'off'}" data-voc="${_rp.voc ? 'on' : 'off'}"
        data-mk="${_rp.mk ? 'on' : 'off'}">`;
  // Both spellings ship; the vowels toggle swaps which is shown. A word we couldn't vocalize
  // honestly falls back to its plain spelling and says so in the card.
  const wspan = (w, si, wi, trail) => { const voc = w.vocalized || w.surface;
    return `<span class="w${!w.lemma ? ' gap' : ''}${w.vocalized ? '' : ' novoc'}"
      data-s="${si}" data-w="${wi}" tabindex="0"><span class="v">${esc(voc)}</span><span class="p">${esc(w.surface)}</span></span>${trail === false ? '' : ' '}`; };
  // s.words is the list of ANNOTATABLE words, not the sentence: the tokenizer drops whatever it
  // cannot look up. Rendering the array alone therefore deleted content, not just punctuation —
  // Hebrew matches runs of Hebrew letters, so every numeral vanished from the page. "ארבעה
  // אנשים נהרגו ... ביניהם בן 93" was displayed as "...בן בצומת", and the English underneath
  // still said "a 93-year-old", which reads as a translation that made something up.
  //
  // So walk s.ar and put back EVERYTHING between one word and the next, verbatim: the spaces,
  // the punctuation, and the numerals and Latin the tokenizer never claimed. Whatever the
  // pipeline chose not to annotate, the reader still sees.
  const arHTML = (s, si) => {
    const ar = s.ar || ''; let pos = 0, out = '';
    s.words.forEach((w, wi) => {
      const idx = ar.indexOf(w.surface, pos);
      if (idx < 0) { out += (wi ? ' ' : '') + wspan(w, si, wi, false); return; }
      const gap = ar.slice(pos, idx);
      out += !gap ? (wi ? ' ' : '')
           : !gap.trim() ? gap
           : `<span class="pu">${esc(gap)}</span>`;
      out += wspan(w, si, wi, false);
      pos = idx + w.surface.length;
    });
    const tail = ar.slice(pos);
    if (tail) out += `<span class="pu">${esc(tail)}</span>`;
    return out;
  };
  // Books carry paragraph markers (`p`): render as flowing bilingual paragraphs (nicer for reading a
  // book). Stories/news have no markers → the classic one-sentence-at-a-time layout, unchanged.
  const hasPara = t.sentences.some(s => s.p != null);
  if (hasPara) {
    // A chapter's clips play as ONE continuous reading, same transport the passage view uses.
    // This branch had no player at all: books are the only content with `p` markers, so every
    // book chapter ever voiced — all 346 of Around the World's clips — was unreachable in the
    // reader. Nothing surfaced it, because there was no error; the audio simply wasn't offered.
    paraClips = t.sentences.map(s => s.audio ? au(s.audio) : null).filter(Boolean);
    if (paraClips.length) h += `<div class="sent rd-para para-head">
      <div class="pl-cap">Listen to the whole chapter</div>${paraPlayer()}</div>`;
    let cur_p = null, group = [];
    const flush = () => { if (!group.length) return;
      h += '<div class="sent rd-para"><div class="ar">';
      group.forEach((si, gi) => { if (gi > 0) h += ' '; h += arHTML(t.sentences[si], si); });
      const en = group.map(si => t.sentences[si].en).filter(Boolean).join(' ');
      h += '</div>' + (en ? '<p class="en">' + esc(en) + '</p>' : '');
      h += `<button class="peek" data-peek="${group[0]}">Peek at English</button></div>`; group = []; };
    t.sentences.forEach((s, si) => { if (cur_p !== null && s.p !== cur_p) flush(); cur_p = s.p; group.push(si); });
    flush();
  } else {
    // The whole passage first, as one flowing paragraph with one continuous player — then the
    // exact same material split sentence-by-sentence below. Same words (so vowels/marked/tap
    // all work), same English peek, same transport UI.
    paraClips = t.sentences.map(s => s.audio ? au(s.audio) : null).filter(Boolean);
    h += '<div class="sent rd-para para-head"><div class="pl-cap">Whole passage</div><div class="ar">';
    t.sentences.forEach((s, si) => { if (si > 0) h += ' '; h += arHTML(s, si); });
    h += '</div><p class="en">' + t.sentences.map(s => esc(s.en)).join(' ') + '</p>';
    if (paraClips.length) h += paraPlayer();
    h += `<button class="peek" data-peek="0">Peek at English</button></div>`;

    t.sentences.forEach((s, si) => {
      h += '<div class="sent"><div class="ar">';
      h += arHTML(s, si);
      // A text can be real Hebrew with the English not written yet -- the Ben-Yehuda shelf
      // arrives that way. An empty paragraph reads as a bug; no paragraph reads as Hebrew.
      h += `</div>${s.en ? `<p class="en">${esc(s.en)}</p>` : ''}`;
      h += player(s.audio);
      h += `<button class="peek" data-peek="${si}">Peek at English</button></div>`;
    });
  }
  // book-chapter navigation: previous / all chapters / mark-read-and-next
  let bnav = '';
  if (t.book) {
    const b = bookById(t.book);
    if (b) {
      const i = b.chapters.findIndex(c => c.id === t.id), prev = b.chapters[i - 1], next = b.chapters[i + 1];
      bnav = `<div class="ctl bk-chnav">
        ${prev ? `<button class="tog" onclick="location.hash='/text/${esc(prev.id)}'">← Previous</button>` : ''}
        <button class="tog" onclick="location.hash='/books/${esc(b.id)}'">All chapters</button>
        ${next ? `<button class="tog go" onclick="markSeen('${esc(t.id)}',true);location.hash='/text/${esc(next.id)}'">Mark read &amp; next →</button>`
               : `<button class="tog go" onclick="markSeen('${esc(t.id)}',true);location.hash='/books/${esc(b.id)}'">Mark read &amp; finish ✓</button>`}</div>`;
    }
  }
  // Reading prose gets a comfortable centered measure even though the app shell is now wide —
  // a 1200px line of text is hard to read. Grids and lists still use the full width.
  $('view').innerHTML = '<div class="reading">' + h + '</div>' + bnav + '</div>';
  paint();
  const pel = $('view').querySelector('.player.para');
  if (pel && paraClips.length) paraSetup(pel, paraClips);

  $('tVoc').onclick = e => {
    const on = e.target.getAttribute('aria-pressed') !== 'true';
    e.target.setAttribute('aria-pressed', String(on));
    $('rd').dataset.voc = on ? 'on' : 'off';
    setReadPref('voc', on);
  };
  $('tEn').onclick = e => {
    const on = e.target.getAttribute('aria-pressed') !== 'true';
    e.target.setAttribute('aria-pressed', String(on));
    $('rd').dataset.en = on ? 'on' : 'off';
    setReadPref('en', on);
  };
  $('tMk').onclick = e => {
    const on = e.target.getAttribute('aria-pressed') !== 'true';
    e.target.setAttribute('aria-pressed', String(on));
    $('rd').dataset.mk = on ? 'on' : 'off';
    setReadPref('mk', on);
    paint();
  };
}

function paint() {
  const showMk = $('rd') && $('rd').dataset.mk !== 'off';
  document.querySelectorAll('#rd .w').forEach(el => {
    const w = cur.sentences[+el.dataset.s].words[+el.dataset.w];
    el.classList.toggle('mk', showMk && !!w.lemma && inDeckWord(w));
  });
  count();
}


// ---------- ask the tutor from anywhere ----------------------------------------------------
// The tutor answers the questions no other module can — but until now you had to leave what
// you were reading, open /tutor, and retype the sentence you were confused by. Selecting text
// anywhere now offers to carry it over, with its own page named as the context, so the answer
// is about the line in front of you rather than about Palestinian Arabic in general.
let _askPend = null;                       // {text, what} handed to the tutor across the route

// Where the selection came from, in words a question can use ("in a story you're reading").
function askWhere() {
  const h = (location.hash.slice(1) || '/').split('/')[1] || '';
  const M = {text: "something you're reading", story: 'a short story', news: 'a news piece',
             books: 'a book', grammar: 'a grammar lesson', lessons: 'a lesson',
             reactions: 'a list of reactions', sounds: 'a pronunciation lesson',
             table: 'a dinner-table conversation', bible: 'a Bible passage',
             verb: 'a verb page', vocab: 'a flashcard', translate: 'the translator'};
  if (h === 'text' && cur && cur.title) return '"' + cur.title.en + '"';
  return M[h] || 'the app';
}

function tutorAskAbout(text, what) {
  text = String(text || '').trim(); if (!text) return;
  if (text.length > 600) text = text.slice(0, 600) + '…';
  const ar = isTargetScript(text);
  const q = ar
    ? 'I came across this in ' + (what === 'a word' ? askWhere() : askWhere()) + ':\n\n'
      + text + '\n\nWhy is it written like this? Break it down for me.'
    : 'From ' + askWhere() + ': "' + text + '" — how would I say that in spoken Palestinian?';
  _askPend = q;
  askHide();
  if ((location.hash.slice(1) || '/').split('/')[1] === 'tutor') tutorFlushPending();
  else location.hash = '/tutor';
}

// Called by tutorHome() once the chat is on screen. Without a key we leave the question in the
// box rather than dropping it, so adding a key and pressing Ask still sends what you selected.
function tutorFlushPending() {
  const q = _askPend; if (!q) return; _askPend = null;
  if (!tutorKey()) { const i = $('tut-in'); if (i) { i.value = q; i.focus(); } return; }
  tutorAsk(q);
}

// ---- the floating action that appears over a selection ----
function askHide() { const b = $('askbtn'); if (b) b.hidden = true; }
function askSelText() {
  const sel = window.getSelection(); if (!sel || sel.isCollapsed) return '';
  return String(sel).replace(/\s+/g, ' ').trim();
}
function askShowFor(sel) {
  const t = askSelText(); if (t.length < 2) { askHide(); return; }
  let b = $('askbtn');
  if (!b) { b = document.createElement('button'); b.id = 'askbtn'; b.className = 'askbtn';
    b.textContent = '💬 Ask the tutor';
    b.addEventListener('mousedown', e => e.preventDefault());   // don't clear the selection
    b.addEventListener('click', () => askPopOpen(askSelText()));
    document.body.appendChild(b); }
  const r = sel.getRangeAt(0).getBoundingClientRect();
  if (!r.width && !r.height) { askHide(); return; }
  b.hidden = false;
  const w = b.offsetWidth || 132;
  b.style.left = Math.max(8, Math.min(window.innerWidth - w - 8, r.left + r.width / 2 - w / 2)) + 'px';
  b.style.top  = (r.top > 52 ? r.top - 42 : r.bottom + 10) + 'px';
}
document.addEventListener('selectionchange', () => {
  const sel = window.getSelection();
  // Typing in the popover's own box moves the selection into it; that must not be read as
  // "the learner deselected the sentence they asked about".
  if (_askPop && _askPop.contains(document.activeElement)) return;
  if (!sel || sel.isCollapsed || !sel.rangeCount) { askHide(); return; }
  clearTimeout(window._askT);
  window._askT = setTimeout(() => askShowFor(window.getSelection()), 180);
});
// Right-click over a selection: same action, offered where the platform menu would be. We only
// pre-empt the browser's own menu when there is actually a selection to ask about.
document.addEventListener('contextmenu', e => {
  const t = askSelText(); if (t.length < 2) return;
  e.preventDefault();
  askShowFor(window.getSelection());
});
window.addEventListener('scroll', askHide, true);

// ---- the tutor, answering in place ----------------------------------------------------
// Highlighting a sentence and pressing Ask used to navigate to /tutor: the passage you were
// reading went off screen at exactly the moment you had a question about it, and coming back
// meant finding your place again. The same question now answers in a panel over the text, and
// takes a follow-up of your own — the trip to the full tutor is a link, not a toll gate.
let _askPop = null, _askMsgs = [], _askBusy = false, _askSubject = '';

const askIsAr = t => isTargetScript(t);
// Prompts are phrased as the learner would ask them, with the passage and the place it came
// from attached once, at the top of the conversation.
const ASK_CHIPS = {
  ar: [['Break it down', 'Break this down for me word by word.'],
       ['Why this form?', 'Why is it in this form here, rather than another one?'],
       ['What does it mean?', 'What does this mean, and when would I use it?']],
  en: [['Say it in Palestinian', 'How would I say that in spoken Palestinian?'],
       ['Is it natural?', 'Is that how a Palestinian would actually say it, or does it sound translated?']],
};

function askPopClose() {
  if (_askPop) _askPop.remove();
  _askPop = null; _askMsgs = []; _askBusy = false; _askSubject = '';
}

function askPopOpen(text) {
  text = String(text || '').trim();
  if (text.length < 2) return;
  if (text.length > 600) text = text.slice(0, 600) + '…';
  const sel = window.getSelection();
  const r = sel && sel.rangeCount ? sel.getRangeAt(0).getBoundingClientRect() : null;
  askHide(); askPopClose();
  _askSubject = text;
  _askMsgs = [];
  const p = document.createElement('div');
  p.className = 'askpop'; p.id = 'askpop';
  p.addEventListener('mousedown', e => { if (e.target.tagName !== 'INPUT') e.preventDefault(); });
  document.body.appendChild(p);
  _askPop = p;
  askPopRender();
  askPopPlace(r);
}

// Anchored to the selection, but a panel is much taller than the little button was: prefer
// below, flip above when there is no room, and never let it hang off either edge.
function askPopPlace(r) {
  const p = _askPop; if (!p) return;
  const w = p.offsetWidth, h = p.offsetHeight;
  if (!r) { p.style.left = Math.max(8, (innerWidth - w) / 2) + 'px'; p.style.top = '64px'; return; }
  const left = Math.max(8, Math.min(innerWidth - w - 8, r.left + r.width / 2 - w / 2));
  const below = r.bottom + 10, above = r.top - h - 10;
  p.style.left = left + 'px';
  p.style.top = (below + h < innerHeight - 8 ? below : Math.max(8, above)) + 'px';
}

function askPopRender() {
  const p = _askPop; if (!p) return;
  const chips = ASK_CHIPS[askIsAr(_askSubject) ? 'ar' : 'en'];
  const keyed = !!tutorKey();
  p.innerHTML = `<div class="askpop-h">
      <span class="askpop-sel" dir="auto">${esc(_askSubject)}</span>
      <button class="askpop-x" onclick="askPopClose()" aria-label="Close">×</button></div>
    ${_askMsgs.length ? `<div class="askpop-log">${_askMsgs.map(m => m.role === 'user'
        ? `<div class="askpop-q">${esc(m.content)}</div>`
        : `<div class="askpop-a${m.error ? ' err' : ''}">${m.error ? esc(m.error) : tutFmt(m.content || '')}</div>`
      ).join('')}${_askBusy ? '<div class="tut-dots">· · ·</div>' : ''}</div>` : ''}
    ${keyed ? `<div class="askpop-chips">${chips.map(([label, q]) =>
        `<button onclick="askPopSend(${JSON.stringify(q).replace(/"/g, '&quot;')})">${esc(label)}</button>`).join('')}</div>
      <form class="askpop-ask" onsubmit="askPopCustom(event)">
        ${kbdWrap(`<input id="askpop-in" autocomplete="off" placeholder="…or ask your own question">`, 'askpop-in', true)}
        <button type="submit" ${_askBusy ? 'disabled' : ''}>Ask</button></form>`
      : `<p class="askpop-nokey">Add your own Claude API key to ask here.
         <a href="#/tutor/settings" onclick="askPopClose()">Add a key →</a></p>`}
    <a class="askpop-full" href="#/tutor" onclick="askPopHandOff()">Continue in the tutor →</a>`;
}

// Leaving for the full page should take the conversation with it, not restart it.
function askPopHandOff() {
  if (_askMsgs.length) _tutorMsgs = _tutorMsgs.concat(_askMsgs.filter(m => m.content || m.error));
  else _askPend = askLead() + 'Break this down for me word by word.';
  askPopClose();
}

const askLead = () => askIsAr(_askSubject)
  ? 'I came across this in ' + askWhere() + ':\n\n' + _askSubject + '\n\n'
  : 'From ' + askWhere() + ': "' + _askSubject + '"\n\n';

function askPopCustom(e) {
  e.preventDefault();
  const i = $('askpop-in'); if (!i) return;
  const q = i.value.trim(); if (!q) return;
  i.value = '';
  askPopSend(q);
}

async function askPopSend(q) {
  if (_askBusy || !_askPop) return;
  if (!tutorKey()) { location.hash = '/tutor/settings'; askPopClose(); return; }
  // The passage rides on the first question only; after that it is already in the history.
  _askMsgs.push({role: 'user', content: q, wire: _askMsgs.length ? q : askLead() + q});
  const slot = {role: 'assistant', content: ''};
  _askMsgs.push(slot);
  _askBusy = true; askPopRender();
  const wire = _askMsgs.slice(0, -1).map(m =>
    ({role: m.role, content: m.role === 'user' ? (m.wire || m.content) : (m.content || '')}));
  const r = await tutorStream(wire, out => {
    slot.content = out;
    const el = _askPop && _askPop.querySelector('.askpop-a:last-of-type');
    if (el) el.innerHTML = tutFmt(out);
  });
  if (!_askPop) return;                       // closed mid-answer
  if (r.error) { slot.error = r.error; slot.content = ''; }
  else slot.content = (r.text || '').replace(/<save>[\s\S]*?<\/save>\s*$/i, '').trim()
       || '(no answer came back)';
  _askBusy = false; askPopRender();
}

// ---------- one "add to deck" control, for every view that shows a word ------------------
// Banking a word only existed in one place: the card you get by tapping a word in running
// text. Anywhere the word IS the subject of the page — a verb's conjugation table, a
// translator result, a reaction in the browse list — there was no way to keep it, which is
// exactly where you are most likely to want to.
//
// Each of those views can name its word from something it already has (a verb index, a token,
// a reaction's Arabic), so the control takes an id and rebuilds the card on click rather than
// stashing payloads. That keeps it stateless: correct after a re-render, and safe to drop into
// any markup with no bookkeeping around it.
function deckBtnHTML(key, call, label) {
  const on = inDeck(key);
  return `<button class="tog deck-add" aria-pressed="${on}" onclick="${call}">${
    on ? '✓ In your deck' : esc(label || '+ Add to deck')}</button>`;
}

// Removing is as important as adding — the same button undoes a mistap, which is why every
// caller toggles rather than adds. `after` lets a view repaint itself in place.
function deckToggleKey(key, build, after) {
  key = deckKeyFor(key);                     // reuse the card this word already has, if any
  if (marked.has(key)) marked.delete(key);
  else { marked.set(key, srsInit(build())); playWord(marked.get(key)); }
  save(); count();
  if (typeof after === 'function') after();
}

// A verb's card is anchored on its citation form — the "he" past — because that is the entry
// the rest of the paradigm is built from, and it is what the review card already expects.
function cardFromVerb(v) {
  // The citation slot, not v.lemma — they differ for a couple of verbs (اِتْشَاوَف vs
  // تْشَاوَف), and the citation form is the one every other entry point now agrees on.
  const cite = verbCite(v);
  const head = (cite && cite.ar) || v.lemma;
  return {lemma: head, vocalized: head, surface: head, root: v.root || '',
          caphi: (cite && cite.caphi) || '', gloss: v.gloss || '',
          analysis: 'VERB:' + (v.form || 'I'),
          // The field name is `he_past` in every card ever saved, so it stays; what it HOLDS is
          // the citation form, which is the past in Arabic and the infinitive in Hebrew.
          he_past: cite ? {ar: cite.ar, caphi: cite.caphi} : null,
          deck: activeDeck()};
}
function deckToggleVerb(i) {
  const v = VB[+i]; if (!v) return;
  deckToggleKey((verbCite(v) || {}).ar || v.lemma, () => cardFromVerb(v), () => verbDetail(i));
}

// A translator result. lexLook() gives back a card-shaped record, so this reuses exactly the
// same builder the reader's word card uses — one definition of what a word card is.
function deckToggleLex(tok, redraw) {
  const r = lexLook(tok, true); if (!r || !r.lemma) return;
  deckToggleKey(r.lemma, () => cardFromWord(r), redraw === 'tr' ? () => trRender(_trQ) : null);
}

function deckToggleRx(ar) {
  const it = (RX.items || []).find(r => r.ar === ar); if (!it) return;
  deckToggleKey(rxKey(ar), () => rxCard(it), () => route());
}

// ---------- LEX: one lexicon, shared by every module --------------------------------------
// Word data used to live *inside* LIB.texts, reachable only by the reader. So only the reader
// could make a word tappable, and only the reader's words were findable in Translate —
// Reactions, Sounds, the Dinner Table, lesson chunks and grammar examples all rendered plain
// Arabic with no way to ask what a word meant, even though the same lexicon sat behind them.
//
// LEX merges every source the app already ships into one index keyed by normalized Arabic:
//   1. corpus word records   — richest: root, gloss, CAPHI++, analysis, Maknuune id, vowels
//   2. verbs.js lemmas       — 3,003 verbs, most of which never appear in the corpus at all
//   3. verbs.js conjugations — built lazily, so a *conjugated* verb in a lesson still resolves
// Nothing here is generated. An entry is a looked-up record or it does not exist, and a word
// LEX can't answer for stays visibly greyed rather than getting an invented gloss.
let _lexI = null, _lexConj = null;

// How much a record can actually say. Two sources can offer the same key; the fuller one wins.
const lexRank = r => (r.gloss ? 4 : 0) + (r.maknuune_id ? 2 : 0) + ((r.caphi_urban || r.caphi) ? 1 : 0);

// A handful of words the ingest pipeline resolves wrongly, corrected where they are SHOWN.
//
// pipeline/ingest.py falls back to stripping clitics off a token to reach a curated function
// word, and for these it strips too much: الله and الهوا both come out as الـ + له "to him",
// كلهم as أكل "eat". Fourteen tokens corpus-wide — but الله is the commonest word in spoken
// Palestinian, so a learner met "to him, for him" constantly.
//
// Fixing it in the pipeline was tried twice and both attempts were net-negative: refusing short
// stems promotes a worse reading (منها became اليَمَن "Yemen"), and adding الله to the curated
// map pulled الآلة and كلهم onto "God" too. So the correction lives here instead — explicit,
// auditable, and applied at the one place a word becomes visible, without re-annotating 380
// texts on a heuristic. Each entry is a word whose reading is not in doubt.
const LEX_FIX = LANG.script.fixes;
function lexFix(w) {
  if (!w) return w || null;
  const f = LEX_FIX[arNorm(w.surface || '')];
  if (!f) return w;
  // caphi_raw carries the CAPHI++ template the Wadi Ara variant is computed from. A corrected
  // entry has no template of its own, so clear it — otherwise the village line would render the
  // pronunciation of the word we just decided this ISN'T (والله showed Wadi Ara "2ilo").
  return Object.assign({}, w, f, {surface: w.surface, vocalized: f.lemma, form: f.lemma,
    caphi_urban: '', caphi_raw: '', root: '', maknuune_id: null,
    vocalized_from: 'curated', provenance: 'curated:app-correction'});
}

// A verbs.js entry shaped like a corpus word record, so showWord() needs no special case.
// `_vb` carries the verb across, which is what puts the full paradigm on the card.
function lexFromVerb(v, surface, cell) {
  return {surface: surface || v.lemma, lemma: v.lemma, vocalized: surface || v.lemma,
          form: v.lemma, root: v.root || '', gloss: v.gloss || '',
          analysis: 'VERB:' + (v.form || 'I'),
          caphi: (cell && cell.ph) || (verbCite(v) || {}).caphi || '',
          provenance: 'verbs.js', _vb: v};
}

// Built from whatever is in memory. The verb half is always there; the word half comes from the
// prebuilt index, or from the corpus when that happens to be loaded already -- the two are
// verified equal, so which one answered is not observable.
//
// It deliberately does NOT fetch anything itself. It is called once per rendered token, and the
// home screen's phrase of the day is four tokens: making the lookup greedy meant the lightest
// page in the app pulled the heaviest file. Sections that are made of lookups say so (`lex: 1`)
// and a tap says so; this function just uses what is here.
function lexIndex() {
  if (_lexI) return _lexI;
  const byKey = new Map(), bySurf = new Map();
  const put = (m, k, rec) => { if (!k) return;
    const p = m.get(k); if (!p || lexRank(rec) > lexRank(p)) m.set(k, rec); };
  const L = window.LEXICON;
  if (L) {
    // Rows are positional -- `f` names the columns -- because repeating the key names once per
    // record was 45% of the file. Three further encodings are OPTIONAL and only Hebrew uses
    // them, because Hebrew ships its whole inflection table (111,327 surface keys) where Arabic
    // ships only what its corpus contains (5,748):
    //   `intern` pools the columns with few distinct values (`analysis` has 171 across 128,000
    //            rows) and the row holds an index into the pool;
    //   `base`   lets a surface row carry only what varies -- the pointed form, its
    //            pronunciation, its analysis -- and inherit the gloss, root and lemma from its
    //            lemma's row, which is written once for 8.6 surfaces;
    //   trailing nulls are dropped, so a row may be shorter than `f`.
    const pools = L.intern || {};
    const raw = L.r.map(row => { const o = {};
      L.f.forEach((name, i) => {
        let v = i < row.length ? row[i] : null;
        if (v != null && pools[name]) v = pools[name][v];
        o[name] = v;
      });
      return o; });
    // A payload that omits `vocalized` is saying the surface IS the pointed form -- true for
    // Hebrew, where every row comes from Wiktionary already pointed. Arabic keeps the column,
    // because plenty of its words have no vowels the lexicon can stand behind, and defaulting
    // there would claim a vocalization the pipeline deliberately refused to guess.
    const pointed = L.f.indexOf('vocalized') < 0;
    // Resolve `base` after every row exists, so a lemma row later in the file still works.
    const recs = raw.map(o => {
      let out = o;
      if (o.base != null) {
        const b = raw[o.base];
        out = {};
        L.f.forEach(name => { out[name] = (o[name] != null && o[name] !== '') ? o[name] : b[name]; });
        delete out.base;
      }
      if (pointed) out.vocalized = out.surface;
      return out; });
    for (const k in L.k) byKey.set(k, recs[L.k[k]]);
    for (const k in L.s) bySurf.set(k, recs[L.s[k]]);
  } else {
    LIB.texts.forEach(t => (t.sentences || []).forEach(s => (s.words || []).forEach(w => {
      if (!w.lemma) return;
      put(byKey, arNorm(w.lemma), w);
      put(bySurf, arNorm(w.surface), w);
    })));
  }
  VB.forEach(v => {
    put(byKey, arNorm(v.lemma), lexFromVerb(v));
    ['past', 'pres', 'imp'].forEach(k => { const c = v[k];
      if (c && c.ar) put(bySurf, arNorm(c.ar), lexFromVerb(v, c.ar, {ph: c.caphi})); });
  });
  _lexI = {byKey, bySurf};
  return _lexI;
}

// Everything the corpus feeds is stale once the corpus grows. Drop it and repaint.
function lexRefresh() {
  _lexI = _tridx = _asIdx = null;
  if (typeof lexPaint === 'function') lexPaint();
}
// Every conjugated cell -> its verb. ~2,300 paradigms x ~50 cells, so it is built only on the
// first lookup that misses everything else — which is the only time it can possibly help.
// That is also the only lookup that needs every paradigm file, so this is where they are asked
// for; until they arrive the fallback simply finds nothing, which is what it did before them.
const conjIdxReady = () => VB.every(v => !v.hasConj || conjReady(v._i));
function lexConjIndex() {
  if (_lexConj) return _lexConj;
  if (!conjIdxReady()) {
    needAllConj().then(() => { _lexConj = null; lexRefresh(); }, () => {});
    return new Map();
  }
  const m = new Map();
  VB.forEach(v => { const c = v.conj; if (!c) return;
    for (const k in c) { const cell = c[k]; const ar = cell && (cell.arv || cell.ar);
      if (!ar) continue; const n = arNorm(ar); if (n && !m.has(n)) m.set(n, {v, cell}); } });
  _lexConj = m; return m;
}

// Clitics the writing system glues on: the article and one-letter prepositions/conjunctions in
// front, object and possessive pronouns behind. SHORTEST first, so the least is cut away: with
// longest-first, والله ("by God" — the commonest word in the app, and absent from the corpus)
// lost وال- and came back as ه "to him". Cutting only و- finds الله. Cut as little as possible.
const LEX_PRE = LANG.script.pre;
const LEX_SUF = LANG.script.suf;
const LEX_MIN = LANG.script.minStem;

// Last resort, and only ever a GUESS: strip a clitic and look the remainder up. It recovers 205
// forms the exact index can't reach (بالتوفيق, خليكن, أبوك) — and it is also wrong sometimes:
// قصتها segments to قصة+ها, but قصت happens to exist as a verb form, so the stripper takes it.
// So the result is tagged `lexclitic` and the card says the segmentation is a guess, rather than
// presenting a stripped match with the same confidence as a real lexicon hit.
function lexStrip(k, ix) {
  // lexFix here too: strip و- off والله and you land on the same mis-annotated الله record.
  const hit = r => lexFix(ix.byKey.get(r) || ix.bySurf.get(r) || null);
  for (const p of LEX_PRE) {
    if (!k.startsWith(p) || k.length - p.length < LEX_MIN) continue;
    const rest = k.slice(p.length);
    const r = hit(rest) || hit('ال' + rest);
    if (r) return {r, cut: p + 'ـ'};
  }
  for (const sf of LEX_SUF) {
    if (!k.endsWith(sf) || k.length - sf.length < LEX_MIN) continue;
    const rest = k.slice(0, -sf.length);
    const r = hit(rest) || hit(rest + 'ه');
    if (r) return {r, cut: 'ـ' + sf};
  }
  for (const p of LEX_PRE) {
    if (!k.startsWith(p) || k.length - p.length < LEX_MIN + 1) continue;
    for (const sf of LEX_SUF) {
      if (!k.endsWith(sf)) continue;
      const rest = k.slice(p.length, -sf.length);
      if (rest.length < LEX_MIN) continue;
      const r = hit(rest);
      if (r) return {r, cut: p + 'ـ…ـ' + sf};
    }
  }
  return null;
}

// The index stores whole word RECORDS under their lemma, so a lemma key can point at a record
// whose own surface is a different token: tapping فِي found the record for فيك and the card
// showed فيك as the headword. The entry is still the right one — the gloss, root and analysis
// all belong to that lemma — but the word on the card has to be the word that was tapped, and
// its vowels are then unknown rather than borrowed from a neighbour.
function lexAs(r, tok) {
  if (!r) return null;
  if (arNorm(r.surface || '') === arNorm(tok)) return r;
  return Object.assign({}, r, {surface: tok, vocalized: '', vocalized_from: ''});
}

// The one lookup every module uses. Returns a word record (card-shaped) or null.
//
// `deep` decides whether a miss is allowed to reach for the 5.4 MB of paradigm files. It is
// false while PAINTING -- deciding whether to grey out a word is not worth downloading every
// conjugation in the language, and on a page of Classical Arabic like the Bible almost every
// token misses -- and true when a person has actually asked about a word. What is already in
// memory is always used either way.
function lexLook(tok, deep) {
  const k = arNorm(tok); if (!k) return null;
  // A correction is a SOURCE, not only a patch on something the index already had. بدكم "you
  // want (pl)" is in no index at all, so correcting-after-lookup never reached it and the word
  // came back unknown — while its six siblings resolved.
  if (LEX_FIX[k]) return lexFix({surface: tok, lemma: tok, gloss: '', provenance: ''});
  const ix = lexIndex();
  const r = ix.byKey.get(k) || ix.bySurf.get(k);
  if (r) return lexFix(lexAs(r, tok));
  // lexFix on EVERY branch, not just the first. بدنا "we want" fell through to the conjugation
  // index, matched a cell of بدن "stoop, lower", and returned before the correction could apply.
  const cj = (deep || conjIdxReady()) ? lexConjIndex().get(k) : null;
  if (cj) return lexFix(lexFromVerb(cj.v, tok, cj.cell));
  const st = lexStrip(k, ix);
  if (!st) return null;
  return lexFix(Object.assign({}, st.r, {surface: tok, vocalized: tok,
    provenance: 'lexclitic', _cut: st.cut}));
}

// ---------- tappable Arabic, anywhere ------------------------------------------------------
// The reader builds spans from per-word records the pipeline annotated. Everywhere else only
// has a plain Arabic string — so arLive() tokenizes it and looks each token up in LEX. Same
// span, same card, same "+ Don't know it". The token itself is the handle (no registry to keep
// in sync with the DOM), and a word LEX can't place is dotted rather than silently plain.
const LEX_PUNCT = LANG.script.punct;
function arLive(str, cls) {
  const s = String(str == null ? '' : str); if (!s) return '';
  let out = '', buf = '';
  const flush = () => { if (!buf) return;
    // `gap` means "not in the lexicon", and that is only a claim we can make once the lexicon
    // is complete. Before then the word renders as an ordinary tappable one and lexPaint()
    // settles it later -- greying out every word on the page while the corpus is still on disk
    // would be a lie about the content, not a loading state.
    const hit = lexLook(buf);
    out += '<span class="w lw' + (hit || !lexReady() ? '' : ' gap') + '" data-lw="'
         + esc(buf) + '" tabindex="0">' + esc(buf) + '</span>';
    buf = ''; };
  for (const ch of s) {
    if (/\s/.test(ch)) { flush(); out += ch; }
    else if (LEX_PUNCT.indexOf(ch) >= 0) { flush(); out += '<span class="pu">' + esc(ch) + '</span>'; }
    else buf += ch;
  }
  flush();
  return '<span class="lx' + (cls ? ' ' + cls : '') + '">' + out + '</span>';
}

// ---------- word card ----------
// human-readable word type from the Maknuune analysis code (VERB:I → "verb", NOUN:MS → "noun"…)
const WTYPE = {VERB: 'verb', NOUN: 'noun', ADJ: 'adjective', ADV: 'adverb', PREP: 'preposition',
  PRON: 'pronoun', PRON_REL: 'relative pronoun', PRON_DEM: 'demonstrative', PRON_INTERR: 'question word',
  CONJ: 'conjunction', CONJ_SUB: 'conjunction', NOUN_PROP: 'proper noun', NOUN_NUM: 'number',
  NOUN_QUANT: 'quantifier', ADJ_COMP: 'comparative', PART: 'particle', PART_PROG: 'particle (‑ing marker)',
  PART_NEG: 'negation', PART_FUT: 'future marker', INTERJ: 'interjection', ABBREV: 'abbreviation'};
function wordType(analysis) { if (!analysis) return null; const a = String(analysis);
  return WTYPE[a] || WTYPE[a.split(':')[0]] || a.split(':')[0].toLowerCase().replace(/_/g, ' '); }

// Index the conjugating verbs by root, so a tapped verb can show its full table. Grouped on
// `hasConj` rather than on the table itself: this runs on any page that renders a word card,
// and touching `v.conj` here would drag in 4.4 MB of paradigms to answer a yes/no question.
let _vbByRootI = null;
function vbByRoot() {
  if (_vbByRootI) return _vbByRootI;
  const m = new Map();
  VB.forEach(v => { if (v.root && v.hasConj) { if (!m.has(v.root)) m.set(v.root, []); m.get(v.root).push(v); } });
  return (_vbByRootI = m);
}
// Find the paradigm for a verb token. This used to pick `cands[0]` — the first verb sharing the
// root — whenever it couldn't match a form code, which was 3,537 of the corpus's 5,388 verb
// tokens, and handed back a verb contradicting the token's own lemma 1,947 times: كان came back
// as تْكَوَّن "be formed", قال as تْقَوَّل "attribute a made-up statement".
//
// Two causes. The corpus's `analysis` carries ASPECT (VERB:P perfective, VERB:I imperfective,
// VERB:C imperative), never the measure — so the form lookup almost never had anything to match.
// And `[IVXQ]+` read the aspect letter "I" as Measure I, which is right by luck for the many
// Form I verbs and silently wrong for the rest.
//
// The token's own lemma is the strongest signal available and was going unused. Match on it
// first; fall back to a measure code only when the analysis genuinely carries one (VERB:II,
// VERB:X — never a bare I, which is ambiguous with the aspect). Then give up: a wrong paradigm
// is worse than no paradigm, and this now decides which card a word banks under.
const _VERB_MEASURE = /VERB:(II|III|IV|V|VI|VII|VIII|IX|X|Q)(?![A-Z])/;
// A verb by its LEMMA, for a lexicon whose roots cannot be trusted. Maknuune states a full
// Arabic root for every entry; Wiktionary states Hebrew's in a template whose פ/ע/ל arguments
// are often only partly filled, so the corpus carries roots like "ע.ה" and "ה" and not one
// Hebrew verb token in the whole shelf could reach its paradigm through vbByRoot(). The pointed
// lemma can: it IS the 3ms past, which is the key verbs.js files a verb under. Only a UNIQUE
// match is accepted -- a wrong paradigm is worse than none, and this decides which card a word
// banks under.
let _vbByLemmaI = null;
function vbByLemma() {
  if (_vbByLemmaI) return _vbByLemmaI;
  const m = new Map();
  VB.forEach(v => [v.lemma, v.past && v.past.ar].filter(Boolean).forEach(x => {
    const n = arNorm(x); if (!n) return;
    if (!m.has(n)) m.set(n, []);
    if (!m.get(n).includes(v)) m.get(n).push(v);
  }));
  return (_vbByLemmaI = m);
}
function findVerb(w) {
  if (w && w._vb) return w._vb.hasConj ? w._vb : null; // came straight from verbs.js via LEX
  if (!w || !String(w.analysis || '').startsWith('VERB')) return null;
  const n = arNorm(w.lemma || '');
  const cands = w.root ? vbByRoot().get(w.root) : null;
  if (cands) {
    if (n) { const byLemma = cands.find(v => arNorm(v.lemma) === n
               || (v.past && arNorm(v.past.ar) === n)
               || (verbCite(v) && arNorm(verbCite(v).ar) === n));
      if (byLemma) return byLemma; }
    const m = String(w.analysis).match(_VERB_MEASURE);
    const byForm = m && cands.find(v => v.form === m[1]);
    if (byForm) return byForm;
  }
  // Only now, and only when it is unambiguous. This runs where the root path found nothing at
  // all, so it can add matches but never overrule one.
  const g = n && vbByLemma().get(n);
  return (g && g.length === 1) ? g[0] : null;
}
// The table on its own, with no surrounding chrome — the word sheet wraps it in a popup, the
// review card puts it behind a disclosure. Same paradigm either way, rendered once.
// ---------- one paradigm renderer ------------------------------------------------------
// There used to be two: a compact one for the word-sheet popup and a near-identical copy
// inside verbDetail for the full page. Both hard-coded the same thing -- eight person rows
// against Past / Present / Present+bi -- so every change to the verb model had to be made
// twice, and Hebrew would have needed a third.
//
// The shape now comes from LANG.verb.tables, a list of descriptors. `scale` picks the CSS
// prefix and how much to show: 'wcj' is the popup (the grid only), 'cj' is the full page
// (grid plus the imperative and participle strips).
//
// One rule does the work that would otherwise be per-language special-casing: SKIP ANY ROW OR
// TABLE WITH NO FILLED CELLS. Hebrew's present has four cells where Arabic's has eight;
// Arabic's participle has three; a defective verb has no imperative. All of that falls out of
// that single line, with no `if (LANG.code === ...)` anywhere in the UI.
function paradigmHTML(v, scale) {
  const c = v.conj;
  if (!c) {
    if (!v.hasConj) return '';
    // The paradigm exists but its block is still on disk. Leave a marker, fetch it, and swap
    // the table in where the marker is -- the same repaint-in-place trick lexPaint() uses, and
    // it works no matter which view asked (word card, review card, popup) without any of them
    // having to become async.
    needConj(v._i).then(paintConj, () => {});
    return `<div class="cj-wait" data-cji="${v._i}" data-cjs="${esc(scale)}"></div>`;
  }
  const P = scale, full = scale === 'cj', out = [];
  const filled = k => !!c[k];
  const txt = k => c[k] ? {ar: c[k].arv || c[k].ar, ph: c[k].ph} : null;

  for (const t of LANG.verb.tables) {
    if (t.full && !full) continue;
    // `persons` is the pack's own top-level list (it is PERSONS elsewhere); the smaller
    // sets live in rowSets. Resolving from either place avoids duplicating an 8-row array.
    const rows = (LANG.verb.rowSets || {})[t.rows] || LANG.verb[t.rows] || [];
    const cols = t.cols || [{slot: t.slot}];
    const live = rows.filter(r => cols.some(col => filled(col.slot + '|' + r[0])));
    if (!live.length) continue;

    if (t.kind === 'grid') {
      const head = cols.map(col => `<${full ? 'div' : 'span'}>${
        esc(full ? col.label : (col.short || col.label))}</${full ? 'div' : 'span'}>`).join('');
      let h = full
        ? `<div class="cj-tbl" style="--cols:${cols.length}">
    <div class="cj-row cj-hdr"><div class="cj-pr"></div>
      ${head}</div>`
        : `<div class="wcj-tbl" style="--cols:${cols.length}"><div class="wcj-row wcj-hdr"><span></span>${head}</div>`;
      for (const r of live) {
        const cells = cols.map(col => {
          const d = txt(col.slot + '|' + r[0]);
          return full
            ? (d ? `<div class="cj-cell"><span class="cj-ar">${esc(d.ar)}</span>
      <span class="cj-ph">${esc(d.ph)}</span></div>` : `<div class="cj-cell">—</div>`)
            : `<span class="wcj-c">${d ? `<span class="wcj-ar">${esc(d.ar)}</span><span class="wcj-ph">${esc(d.ph)}</span>` : '—'}</span>`;
        }).join('');
        h += full
          ? `\n    <div class="cj-row"><div class="cj-pr"><span class="cj-pr-ar">${esc(r[2])}</span>
        <span class="cj-pr-en">${esc(r[1])}</span></div>
      ${cells}</div>`
          : `<div class="wcj-row">
      <span class="wcj-pr">${esc(r[2])}<em>${esc(r[1])}</em></span>
      ${cells}</div>`;
      }
      out.push(h + (full ? `\n  </div>` : `</div>`));
    } else {                                   // a strip: one labelled cell per row
      out.push(`<div class="cj-mini"><div class="sec">${esc(t.label)}</div>
    <div class="cj-mini-row" style="--mini:${live.length}">${live.map(r => {
      const d = txt(t.slot + '|' + r[0]);
      return `<div class="cj-cell"><span class="cj-k">${esc(r[1])}</span>
        <span class="cj-ar">${esc(d.ar)}</span><span class="cj-ph">${esc(d.ph)}</span></div>`;
    }).join('')}</div></div>`);
    }
  }
  return out.join('');
}

function conjTableHTML(v) { return paradigmHTML(v, 'wcj'); }
// Fill every waiting marker whose block has since landed.
function paintConj() {
  document.querySelectorAll('.cj-wait').forEach(el => {
    const v = VB[+el.dataset.cji];
    if (v && v.conj) el.outerHTML = paradigmHTML(v, el.dataset.cjs);
  });
}
function conjPopupHTML(v) {
  if (!v.hasConj) return '';
  return `<div class="wcj"><div class="wcj-h"><span>Conjugation${WEAK_INFO[v.weak] ? ' · ' + esc(WEAK_INFO[v.weak][0].toLowerCase()) : ''} Form ${esc(v.form)}</span>
      <a href="#/verb/${v._i}" onclick="hideCard()">full page →</a></div>${conjTableHTML(v)}</div>`;
}

// Wadi Ara (central rural) realization of the word's Maknuune CAPHI++ template. Mirrors
// pipeline/subdialect.py: uppercase letters in the template are the sub-dialect variables;
// the Wadi Ara / Triangle villages say q as k, k as ch, and keep the interdentals.
// Emphatics (tokens containing a period) never vary. Returns null when the village form
// is identical to the urban one — no variant line for words that don't differ.

// Sub-dialect variants are a per-language LIST (empty for Hebrew), not a hard-coded pair.
// The card takes a word RECORD, not coordinates into the open text — that coupling was the
// only reason a definition could be shown in the reader and nowhere else. `ctx` is the
// reader's {si, wi} when there is one; without it the card simply drops the two affordances
// that need a surrounding sentence (phrase-building, in-place re-highlighting).
function showCard(si, wi) { showWord(cur.sentences[si].words[wi], {si, wi}); }
// `opts.msa` marks text that is NOT spoken Palestinian — today that means the Van Dyck Bible
// (1865, Classical Arabic). Those words stay tappable, because looking one up is exactly what
// helps while reading — but they must never reach the deck. The vocabulary the app schedules,
// drills and syncs is Palestinian dialect; a Classical form banked from Genesis would be
// reviewed for months as though someone might say it at a dinner table.
function showWord(w0, ctx, opts) {
  if (!w0) return;
  const msa = !!(opts && opts.msa);
  const w = lexFix(w0);
  const variants = (LANG.phon.variants || [])
    .map(v => ({label: v.label, val: v.apply(w)})).filter(v => v.val);
  const on = w.lemma && inDeckWord(w);
  const wt = wordType(w.analysis);
  const vb = findVerb(w);
  const CUR = {'curated:function-word':'hand-curated · common function word',
               'curated:proper-noun'  :'hand-curated · name, no lexicon has these',
               'curated:modern-term'  :'hand-curated · too new for the lexicon'};
  // An AMBIGUOUS word carries the FIRST candidate's maknuune_id — a guess among several, not a
  // resolved sense. Checking the id first said "Maknuune #30787" for it, which is the exact
  // failure the lookup pipeline exists to prevent, leaking back in at the display layer. Say what
  // it actually is instead: 33% of the book's tokens are still waiting on adjudication.
  const amb = (w.provenance || '').startsWith('AMBIGUOUS');
  const src = w.provenance === 'curated:app-correction'
              ? 'corrected in the app — the lexicon pipeline mis-splits this one'
            : w.provenance === 'lexclitic'
              ? `matched after removing ${esc(w._cut)} — the split is a guess, not a lexicon entry`
            : w.provenance === 'wiktionary:ktiv'
              ? 'matched by ignoring the vowel letters — the entry can spell this word, but it is not an exact entry for it'
            : w.provenance === 'wiktionary:haser'
              ? 'matched to the fuller spelling of the same word — the vowels here are the ones printed on the page'
            : w.provenance === 'verbs.js' ? 'from the verb list — paradigm below'
            : amb ? 'lexicon match not yet confirmed — one of several possible entries'
            : w.maknuune_id ? `${esc(LANG.lex.name)} #${esc(w.maknuune_id)}`
            : CUR[w.provenance] || ((w.provenance||'').startsWith('curated')
              ? 'hand-curated' : 'not in the lexicon — unverified');
  $('wc').innerHTML =
    `<div class="hw">${esc(w.vocalized || w.surface)}
       ${w.lemma ? `<button class="say" data-a="say" aria-label="Pronounce">${svg('spk')}</button>` : ''}</div>
     ${w._cut ? `<div class="wcut">reading it as <b dir="rtl">${esc(w._cut)}</b> + <b dir="rtl">${esc(w.lemma)}</b></div>` : ''}
     <div class="ph">${esc(w.caphi_urban || w.caphi || '')}</div>
     ${variants.map(v => `<div class="phwa"><b>${esc(v.label)}</b>${esc(v.val)}</div>`).join('')}
     ${wt ? `<div class="wtype">${esc(wt)}</div>` : ''}
     <div class="gl">${esc(pretty(w.gloss)) || (w._looking
        ? '<span style="color:var(--muted)">looking it up…</span>'
        : '<span style="color:var(--muted)">no entry</span>')}</div>
     ${vb ? conjPopupHTML(vb) : ''}
     <dl>
       <dt>As written</dt><dd class="rtl">${esc(w.surface)}</dd>
       <dt>Vowels</dt><dd>${esc(VOCSRC[w.vocalized_from] || w.vocalized_from || '—')}</dd>
       <dt>Dictionary</dt><dd class="rtl">${esc(w.form || '—')}</dd>
       <dt>Root</dt><dd class="rtl">${esc(w.root || '—')}</dd>
       <dt>Type</dt><dd>${esc(wt ? wt + (w.analysis && w.analysis.includes(':') ? ' (' + w.analysis + ')' : '') : (w.analysis || '—'))}</dd>
     </dl>
     ${msa ? `<div class="msa-note">${LANG.bible.wordNote}</div>` : ''}
     <div class="src">${src}${on && !msa ? ' · in your deck (' + esc(deckName((marked.get(deckKeyForWord(w)) || {}).deck)) + ')' : ''}</div>
     <div class="acts">
       <button data-a="close">Close</button>
       ${ctx && !msa ? '<button data-a="phrase">+ Phrase…</button>' : ''}
       <button data-a="ask">Ask the tutor</button>
       ${msa ? '' : `<button class="mk" data-a="mark" data-on="${on ? 1 : 0}" ${w.lemma ? '' : 'disabled'}>
         ${on ? '✓ In your deck' : "+ Don't know it"}</button>`}
     </div>
     ${(() => { const p = msa ? null : verbPast(w);
       return p && arNorm(p.ar) !== arNorm(w.surface || '')
         ? `<div class="wc-banks">Banks as <b dir="rtl">${esc(p.ar)}</b> — ${esc(LANG.verb.citeNote)}.
            One card per verb, whatever form you meet it in.</div>`
         : ''; })()}`;
  $('cw').classList.add('on');
  $('wc').querySelector('[data-a="close"]').onclick = hideCard;
  const phb = $('wc').querySelector('[data-a="phrase"]');
  if (phb && ctx) phb.onclick = () => startPhrase(ctx.si, ctx.wi);
  const say = $('wc').querySelector('[data-a="say"]');
  if (say) say.onclick = () => playWord(marked.get(w.lemma) || cardFromWord(w));
  const ask = $('wc').querySelector('[data-a="ask"]');
  if (ask) ask.onclick = () => { hideCard(); tutorAskAbout(w.surface || w.lemma, 'a word'); };
  const mk = $('wc').querySelector('[data-a="mark"]');
  if (w.lemma && mk) mk.onclick = () => {
    const k = deckKeyForWord(w);        // the card this word already has, in whatever tense
    if (marked.has(k)) marked.delete(k);
    else { marked.set(k, cardFromWord(w)); playWord(marked.get(k)); }
    save(); if (ctx) paint(); else lexPaint(); showWord(w, ctx);
  };
}

// The reader repaints marked words through paint(), which walks cur.sentences. Words rendered
// by arLive() have no sentence behind them, so they get their own repaint keyed on the token.
function lexPaint() {
  document.querySelectorAll('.lx .lw').forEach(el => {
    const r = lexLook(el.dataset.lw);
    el.classList.toggle('mk', !!(r && r.lemma && inDeckWord(r)));
    el.classList.toggle('gap', lexReady() && !r);
  });
}
// ---------- phrase cards ------------------------------------------------------------
// LEARNING-SYSTEM.md's finding: teach CHUNKS, not words. "بشرب قهوة" is one thing your mouth
// learns to say; drilling بشرب and قهوة separately never assembles it. A phrase card is an
// ordinary SRS card — same deck, same schedule, same grading — it just holds a span of words.
//
// The map is keyed by `lemma`, so phrases get a synthetic key with a ¶ prefix. That keeps
// every existing path working untouched (delete, move, grade, sync) and can never collide
// with a real lemma — which also means the reader's marked-word highlighting ignores them.
const phKey = ar => '¶' + arNorm(ar);
let _ph = null;                       // {si, wi} — the anchor while picking a phrase

// Where a phrase's MEANING comes from. Never invented — three real sources, best first:
//   1. the span is the whole sentence, so the sentence's own translation IS the meaning;
//   2. the same phrase occurs elsewhere in the corpus, and those sentences are translated —
//      the Reverso-style trick the Translate section already uses, applied to a chunk;
//   3. failing both, the sentence it came from, shown so you can read the meaning off it.
// The word-by-word glosses are reference material, not a translation, and are no longer
// pretending to be one by sitting in the answer box.
// Match on the WORD SEQUENCE, not the raw sentence text: sentences carry commas and full
// stops between words ("الصبح، بصحى"), so a substring test against s.ar misses the phrase
// even in the very sentence it was lifted from.
const phSeq = words => words.map(w => arNorm(w.surface)).join(' ');
function phraseMeanings(words, si, whole) {
  const out = [], seen = new Set();
  const needle = phSeq(words);
  const here = cur && cur.sentences[si];
  // The sentence it came from is always the first offer — for a sub-span it's the honest
  // starting point you trim down, not a perfect answer.
  if (here && here.en) {
    out.push({en: here.en, why: whole ? 'this sentence' : 'the sentence it’s from — trim it down'});
    seen.add(here.en);
  }
  try {
    LIB.texts.forEach(t => (t.sentences || []).forEach(s => {
      if (out.length >= 5 || !s.en || seen.has(s.en) || !s.words) return;
      if (!phSeq(s.words).includes(needle)) return;
      seen.add(s.en);
      out.push({en: s.en, why: 'the same phrase in “' + esc(t.title.en || t.id) + '”'});
    }));
  } catch (e) {}
  return out;
}

function startPhrase(si, wi) {
  _ph = {si, wi};
  // Starting a phrase is a commitment to needing the rest of the corpus: the best meaning a
  // phrase card can have is the SAME phrase translated in another text, and that is a search
  // across every sentence. Fetch it while the second word is still being chosen -- by the time
  // phraseMeanings() runs it is normally here, and if it is not the card still has the two
  // sources that come from the sentence in front of you.
  if (!corpusReady()) needCorpus().catch(() => {});
  hideCard();
  document.querySelectorAll('.rd .w.phsel').forEach(x => x.classList.remove('phsel'));
  const el = document.querySelector(`.rd .w[data-s="${si}"][data-w="${wi}"]`);
  if (el) el.classList.add('phsel');
  let bar = $('phbar');
  if (!bar) { bar = document.createElement('div'); bar.id = 'phbar'; bar.className = 'phbar';
    document.body.appendChild(bar); }
  bar.innerHTML = `<span>Tap the <b>last word</b> of the phrase</span>
    <button onclick="cancelPhrase()">Cancel</button>`;
  bar.classList.add('on');
}
function cancelPhrase() {
  _ph = null;
  document.querySelectorAll('.rd .w.phsel').forEach(x => x.classList.remove('phsel'));
  const bar = $('phbar'); if (bar) bar.classList.remove('on');
}
// Second tap: build the span and show it for confirmation. Order doesn't matter — tapping
// right-to-left is natural in Arabic, so we just take the min/max.
function phrasePick(si, wi) {
  if (!_ph || _ph.si !== si) return startPhrase(si, wi);       // different sentence → re-anchor
  const a = Math.min(_ph.wi, wi), b = Math.max(_ph.wi, wi);
  const s = cur.sentences[si];
  const words = s.words.slice(a, b + 1);
  const ar = words.map(w => w.vocalized || w.surface).join(' ');
  const key = phKey(ar);
  document.querySelectorAll('.rd .w').forEach(x => {
    const i = +x.dataset.w;
    x.classList.toggle('phsel', +x.dataset.s === si && i >= a && i <= b);
  });
  const already = marked.has(key);
  const whole = a === 0 && b === s.words.length - 1;
  const sugg = phraseMeanings(words, si, whole);
  // The prompt bar has done its job — leave it up and it sits on top of this sheet's input.
  const bar = $('phbar'); if (bar) bar.classList.remove('on');
  $('wc').innerHTML =
    `<div class="hw" dir="rtl">${esc(ar)}</div>
     <div class="ph">${esc(words.map(w => w.caphi_urban || w.caphi || '').filter(Boolean).join(' '))}</div>
     <div class="wtype">phrase · ${words.length} words</div>
     <label class="phlab">What the phrase means
       <input id="phen" value="${esc(whole && sugg.length ? sugg[0].en : '')}"
         placeholder="say it in natural English" autocomplete="off"></label>
     ${sugg.length ? `<div class="phsug"><div class="phsug-t">${
        whole ? 'The translation of this sentence' : 'Tap to start from a real translation'}</div>
       ${sugg.map(x => `<button class="phsug-b" data-en="${esc(x.en)}">
          <span class="phsug-en">${esc(x.en)}</span>
          <span class="phsug-w">${esc(x.why)}</span></button>`).join('')}</div>` : ''}
     <div class="phwrap"><div class="phsug-t">Word by word, from the lexicon</div>
       <div class="phw">${words.map(w => `<span><b dir="rtl">${esc(w.vocalized || w.surface)}</b>
          ${esc(pretty(w.gloss) || '—')}</span>`).join('')}</div></div>
     <div class="src">Meanings are the app's own translations; the wording you save is yours.
       Wrong end? Cancel and pick again.</div>
     <div class="acts">
       <button data-a="close">Cancel</button>
       <button class="mk" id="phadd" ${already ? 'disabled' : ''}>${
         already ? '✓ Already in your deck' : '+ Add phrase'}</button>
     </div>`;
  $('wc').querySelectorAll('.phsug-b').forEach(btn => btn.onclick = () => {
    const inp = $('phen'); if (inp) { inp.value = btn.dataset.en; inp.focus(); }
  });
  $('cw').classList.add('on');
  $('wc').querySelector('[data-a="close"]').onclick = () => { hideCard(); cancelPhrase(); };
  const add = $('phadd');
  if (add && !already) add.onclick = () => addPhrase(si, a, b);
}
function addPhrase(si, a, b) {
  const s = cur.sentences[si];
  const words = s.words.slice(a, b + 1);
  const ar = words.map(w => w.vocalized || w.surface).join(' ');
  // No silent fallback to the word-by-word chain — a card whose "meaning" is
  // "day · morning · wake up" is worse than no card, and that is exactly what you'd get by
  // tapping Add without reading. Make the meaning a deliberate act.
  const en = (($('phen') || {}).value || '').trim();
  if (!en) { const i = $('phen'); if (i) { i.focus(); i.classList.add('phbad');
      setTimeout(() => i.classList.remove('phbad'), 1200); } return; }
  const whole = a === 0 && b === s.words.length - 1;            // the span IS the whole sentence
  marked.set(phKey(ar), srsInit({
    kind: 'phrase', lemma: phKey(ar), phrase: ar, vocalized: ar, surface: ar, gloss: en,
    caphi: words.map(w => w.caphi_urban || w.caphi || '').filter(Boolean).join(' '),
    parts: words.map(w => ({ar: w.vocalized || w.surface, gloss: pretty(w.gloss) || '—',
                            caphi: w.caphi_urban || w.caphi || ''})),
    analysis: 'PHRASE', root: '', audio: whole ? s.audio || null : null,
    example_ar: s.ar, example_en: s.en, text: cur ? cur.id : null, deck: activeDeck(),
  }));
  save(); count(); paint();
  hideCard(); cancelPhrase();
}
// Heard something out in the world? Add it without a text to tap. Marked user-supplied,
// because nothing here went through the lexicon.
function addPhraseManual() {
  const ar = (prompt('The Arabic phrase — type or paste it:') || '').trim();
  if (!ar) return;
  const en = (prompt('What does it mean?') || '').trim();
  if (!en) return;
  const key = phKey(ar);
  if (marked.has(key)) { alert('That phrase is already in your deck.'); return; }
  marked.set(key, srsInit({kind: 'phrase', lemma: key, phrase: ar, vocalized: ar, surface: ar,
    gloss: en, caphi: '', parts: [], analysis: 'PHRASE', root: '',
    provenance: 'user', deck: activeDeck()}));
  save(); count(); route();
}

// Build a fresh SRS card from a tapped word + the sentence it was found in.
// A VERB always enters the deck as its citation form — the 3rd-person-masculine-singular past,
// the "he" form — no matter which tense you happened to meet it in. Meeting بيجي in a story,
// جيت in a drill and أَجَا on its conjugation page used to make three separate cards on three
// separate schedules; the corpus's own lemma disagrees with the paradigm's past for 215 of 461
// verb tokens, so this was not a rare edge. One verb, one card, and the paradigm page is where
// you go to see the other forms.
//
// This applies to a verb banked as a WORD. A verb inside a phrase card keeps whatever form the
// phrase uses — بدي أروح is the thing you are learning to say, and reducing it to راح would
// destroy it. Phrase and reaction cards never come through here (they build their own, keyed
// ¶/®), so that separation is structural rather than a rule to remember.
// The slot a verb is FILED under, which is the pack's to name. Arabic has no infinitive and
// files under the 3ms past; Hebrew has one and files under it -- לִכְתּוֹב, what a dictionary
// lists and what a learner is taught to say. Everything downstream reads this rather than
// `v.past`, so the two languages differ in one line instead of in twelve.
const verbCite = v => (v && v[LANG.verb.cite] && v[LANG.verb.cite].ar) ? v[LANG.verb.cite] : null;
const verbPast = w => verbCite(findVerb(w));

function cardFromWord(w) {
  const s = cur && cur.sentences ? cur.sentences.find(x => x.words.includes(w)) : null;
  const vb = findVerb(w);
  const past = verbPast(w);
  // Headword, pronunciation and vowels all have to move together — keeping the tapped word's
  // CAPHI beside the past-tense headword would print أَجَا and say "biiji".
  const head = past ? past.ar : (w.vocalized || w.form || w.lemma);
  return srsInit({
    lemma: past ? past.ar : w.lemma, vocalized: head, surface: w.surface,
    root: w.root, caphi: past ? past.caphi : (w.caphi_urban || w.caphi),
    gloss: w.gloss || (vb && vb.gloss) || '', analysis: w.analysis,
    he_past: past ? {ar: past.ar, caphi: past.caphi} : null,
    // What you actually tapped, when it wasn't the citation form — so the card can say why its
    // headword isn't the word you clicked.
    met_as: past && arNorm(w.surface || '') !== arNorm(past.ar) ? w.surface : null,
    example_ar: s ? s.ar : null, example_en: s ? s.en : null,
    text: cur ? cur.id : null, deck: activeDeck(),
  });
}
// The 3rd-person-masculine-singular past ("he" form) — Arabic's dictionary form for a verb. Stored
// on the card when it's added; for verb cards saved before this existed, look it up from the deck's
// root + form. Returns null for non-verbs, and when the card's headword IS already that past form.
function cardHePast(c) {
  if (!c || c.kind === 'phrase') return null;
  let hp = c.he_past;
  if (!hp) {
    if (!String(c.analysis || '').startsWith('VERB') || !c.root) return null;
    const cands = vbByRoot().get(c.root); if (!cands) return null;
    const form = (String(c.analysis).match(/VERB:([IVXQ]+)/) || [])[1];
    const v = cands.find(x => x.form === form) || cands[0];
    hp = verbCite(v);
  }
  if (!hp || !hp.ar) return null;
  if (arNorm(hp.ar) === arNorm(c.vocalized || c.lemma || '')) return null;   // headword already IS it
  return hp;
}
// A saved card back to its paradigm. Cards banked since verbs started banking as the "he" past
// carry that citation form as their headword, so they match a VB entry directly; older cards
// (and ones banked from a conjugated token) fall back to he_past, then to a measure code. Same
// lemma-first order as findVerb, and for the same reason: a wrong paradigm is worse than none.
function cardVerb(c) {
  if (!c || c.kind === 'phrase' || !c.root) return null;
  if (!String(c.analysis || '').startsWith('VERB')) return null;
  const cands = vbByRoot().get(c.root); if (!cands) return null;
  const heads = [c.he_past && c.he_past.ar, c.lemma, c.vocalized].filter(Boolean).map(arNorm);
  for (const h of heads) {
    const hit = cands.find(v => arNorm(v.lemma) === h || (v.past && arNorm(v.past.ar) === h)
                                || (verbCite(v) && arNorm(verbCite(v).ar) === h));
    if (hit) return hit;
  }
  const m = String(c.analysis).match(_VERB_MEASURE);
  return (m && cands.find(v => v.form === m[1])) || null;
}
// The paradigm on a deck card, collapsed. Open during review it is a reference, not the answer;
// the "he · past" line above it is what the card is actually testing.
function cardConjHTML(c) {
  const v = cardVerb(c);
  if (!v || !v.hasConj) return '';
  return `<details class="rv-conj"><summary>Conjugation · Form ${esc(v.form)}${
      WEAK_INFO[v.weak] ? ' · ' + esc(WEAK_INFO[v.weak][0].toLowerCase()) : ''}</summary>
    ${conjTableHTML(v)}
    <a class="rv-conj-full" href="#/verb/${v._i}">Open the full paradigm →</a></details>`;
}
const hePastHTML = (hp, cls) => `<div class="${cls}"><b>he · past</b>
  <span class="rt">${esc(hp.ar)}</span>${hp.caphi ? `<span class="hp">${esc(hp.caphi)}</span>` : ''}</div>`;
const hideCard = () => $('cw').classList.remove('on');
$('scrim').onclick = hideCard;
addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (_askPop) return askPopClose();
  hideCard();
});

// ---------- drill ----------
function drill(d) {
  $('back').hidden = false;
  $('title').textContent = d.title.en;
  let h = `<p class="hint">Read the English, <b>say it out loud</b>, then tap to check.
    The saying-it-first part is what makes it work — checking before you try is the
    one way to get nothing out of this.</p>`;
  d.items.forEach((it, i) => {
    h += `<div class="ch"><div class="q">${esc(it.cue)}</div>
      <div class="a" tabindex="0">${esc(it.answer)}</div>` +
      (it.answer_audio
        ? player(it.answer_audio)
        : '') +
      `<div class="u">${esc(it.use || '')}</div></div>`;
  });
  $('view').innerHTML = h;
}

// ---------- speaking practice (the fluency engine) ----------
// Two drills over any text. The 4/3/2 retell (LEARNING-SYSTEM §2.3) needs no audio — it's a
// timer that forces you to say the same thing faster and faster until the words come automatically.
// Shadowing needs real Palestinian sentence audio; it lights up automatically once a text has it,
// and until then we say so plainly rather than shadow a wrong-accent robotic voice.
const SK_ROUNDS = [240, 180, 120];                        // 4, 3, 2 minutes, in seconds
let _skTimer = null, _skLeft = SK_ROUNDS[0], _skRound = 0, _skDone = [false, false, false];
let _spkT = null;                                         // the text the Speak view is showing
const skFmt = s => { s = Math.max(0, s); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
function spkStop() { if (_skTimer) { clearInterval(_skTimer); _skTimer = null; } }

function speakView(t) {
  spkStop();
  _spkT = t;
  $('back').hidden = false;
  $('title').textContent = 'Speak';
  _skRound = 0; _skLeft = SK_ROUNDS[0]; _skDone = [false, false, false];
  const hasAudio = t.sentences.some(s => s.audio);

  let h = `<div class="sk-hd"><div class="sk-hk">Speaking practice</div>
      <div class="sk-ht">${esc(t.title.en)}</div></div>`;

  h += `<div class="note" style="margin:0 0 16px">The <b>4/3/2 drill</b>: retell this out loud from
     memory — first in four minutes, then three, then two. Speeding up is the whole point; it forces the
     words to come as chunks instead of one at a time. Keep talking the entire time — if you blank, say
     what you remember or just describe it. Nobody’s grading you. The talking <i>is</i> the exercise.</div>`;

  h += `<div class="sk-rounds">${[0, 1, 2].map(i =>
     `<button class="sk-round" id="sk-r${i}" onclick="spkSetRound(${i})">
        <b>${[4, 3, 2][i]} min</b><span>Round ${i + 1}</span></button>`).join('')}</div>`;

  h += `<div class="sk-timer">
      <div class="sk-time" id="sk-time">${skFmt(_skLeft)}</div>
      <div class="sk-status" id="sk-status"></div>
      <div class="ctl" style="justify-content:center;margin:12px 0 0">
        <button class="tog go" id="sk-play" onclick="spkToggle()">Start</button>
        <button class="tog" onclick="spkReset()">Reset</button></div></div>`;

  h += `<button class="sk-peek" onclick="this.nextElementSibling.classList.toggle('open');
     this.textContent=this.nextElementSibling.classList.contains('open')?'Hide the text ▴':'Peek at the text ▾'">Peek at the text ▾</button>
     <div class="sk-ref">`;
  t.sentences.forEach(s => { h += `<div class="sk-ref-s"><div class="ar" dir="rtl">${esc(s.ar)}</div>
     <div class="sk-ref-en">${esc(s.en)}</div></div>`; });
  h += `</div>`;

  h += `<div class="sec">Shadow the audio</div>`;
  if (hasAudio) {
    h += `<button class="gs-launch" onclick="gsOpen()">▶ Start guided shadow
       <span>Hands-free — it plays each line, then waits for you to echo it back.</span></button>`;
    h += `<p class="hint">…or go line by line yourself: play each one, then say it straight back — copy the
       rhythm and melody, not just the words. Drop it to 0.5× until your mouth keeps up.</p>`;
    t.sentences.forEach(s => { if (!s.audio) return;
      h += `<div class="sk-shadow"><div class="ar" dir="rtl">${esc(s.ar)}</div>${player(s.audio)}</div>`; });
  } else {
    h += `<div class="unval" style="border-color:var(--rule);color:var(--ink-soft)">
       <b style="color:var(--verdigris)">Shadowing unlocks with audio.</b> This text doesn’t have spoken
       audio yet. Once the ${esc(LANG.name)} audio is generated, each line gets a player here and you can
       shadow it. For now, the 4/3/2 retell above is your speaking workout.</div>`;
  }

  h += `<div class="ctl" style="margin-top:16px">
     <button class="tog" onclick="location.hash='/text/${esc(t.id)}'">Read it first</button></div>`;
  $('view').innerHTML = h;
  spkPaint();
}

function spkPaint() {
  const tv = $('sk-time'); if (tv) tv.textContent = skFmt(_skLeft);
  const pl = $('sk-play'); if (pl) pl.textContent = _skTimer ? 'Pause' : (_skLeft < SK_ROUNDS[_skRound] && _skLeft > 0 ? 'Resume' : 'Start');
  [0, 1, 2].forEach(i => { const b = $('sk-r' + i); if (b) {
    b.classList.toggle('on', i === _skRound); b.classList.toggle('done', _skDone[i]); } });
}
function spkTick() {
  _skLeft--;
  if (_skLeft <= 0) {
    _skLeft = 0; spkStop(); _skDone[_skRound] = true;
    const allDone = _skDone.every(x => x);
    if (_skRound < 2) { _skRound++; _skLeft = SK_ROUNDS[_skRound]; }
    spkPaint();
    const st = $('sk-status'); if (st) st.textContent = allDone
      ? 'All three rounds done — that’s the drill. 🎉'
      : 'Round done. Next: ' + [4, 3, 2][_skRound] + ' minutes — faster this time.';
    return;
  }
  spkPaint();
}
function spkToggle() {
  if (_skTimer) { spkStop(); }
  else { if (_skLeft <= 0) _skLeft = SK_ROUNDS[_skRound]; _skTimer = setInterval(spkTick, 1000);
    const st = $('sk-status'); if (st) st.textContent = 'Talking… keep going, don’t stop.'; }
  spkPaint();
}
function spkSetRound(n) { spkStop(); _skRound = n; _skLeft = SK_ROUNDS[n];
  const st = $('sk-status'); if (st) st.textContent = ''; spkPaint(); }
function spkReset() { spkStop(); _skRound = 0; _skLeft = SK_ROUNDS[0]; _skDone = [false, false, false];
  const st = $('sk-status'); if (st) st.textContent = ''; spkPaint(); }

// ---------- guided shadow (hands-free) ----------
// Steps through a text line by line: play the clip → a symmetric "your turn" beat to echo it →
// auto-advance. Uses its OWN <audio> so it never tangles with the reader's shared player. After
// the first user-gesture play, subsequent programmatic plays on the same element are allowed.
let _gs = null;
function gsClear() { if (_gs) { if (_gs.timer) clearTimeout(_gs.timer); if (_gs.tick) clearInterval(_gs.tick);
  _gs.timer = _gs.tick = null; if (_gs.audio) { _gs.audio.onended = null; _gs.audio.pause(); } } }
function gsStop() { gsClear(); if (_gs) _gs.running = false; }

function gsOpen() {
  const t = _spkT; if (!t) return;
  const sents = t.sentences.filter(s => s.audio).map(s => ({ar: s.ar, en: s.en, audio: s.audio}));
  if (!sents.length) return;
  const a = new Audio(); a.preservesPitch = true; a.mozPreservesPitch = true; a.webkitPreservesPitch = true;
  _gs = {t, sents, i: 0, phase: 'idle', timer: null, tick: null, audio: a, speed: SPEED, running: false};
  gsRender();
}
function gsExit() { const t = _gs && _gs.t; gsStop(); _gs = null; if (t) speakView(t); }

function gsPlayLine() {
  if (!_gs) return;
  _gs.phase = 'listen'; _gs.running = true; gsRender();
  const a = _gs.audio, s = _gs.sents[_gs.i];
  a.src = au(s.audio); a.playbackRate = _gs.speed; a.currentTime = 0;
  a.onended = () => { if (_gs && _gs.running) gsYourTurn(); };
  a.play().catch(() => { _gs.running = false; _gs.phase = 'paused'; gsRender(); });   // autoplay blocked → wait for tap
}
function gsYourTurn() {
  if (!_gs) return;
  _gs.phase = 'turn'; gsRender();
  const elapsed = (isFinite(_gs.audio.duration) ? _gs.audio.duration : 3) / _gs.speed;   // real time the clip took
  const total = Math.max(2000, elapsed * 1000 + 800);
  const start = now();
  _gs.tick = setInterval(() => {
    const el = $('gs-bar'); if (!el) { clearInterval(_gs.tick); _gs.tick = null; return; }
    el.style.width = Math.min(100, (now() - start) / total * 100) + '%';
  }, 60);
  _gs.timer = setTimeout(() => { if (_gs && _gs.running) gsNext(); }, total);
}
function gsNext() {
  if (!_gs) return; gsClear();
  if (_gs.i < _gs.sents.length - 1) { _gs.i++; gsPlayLine(); }
  else { _gs.phase = 'done'; _gs.running = false; gsRender(); }
}
function gsToggle() {                                    // Start / Pause / Resume
  if (!_gs) return;
  if (_gs.running) { gsStop(); _gs.phase = 'paused'; gsRender(); }
  else { gsPlayLine(); }                                 // (re)play the current line and continue
}
function gsReplay() { if (_gs) { gsClear(); gsPlayLine(); } }
function gsRestart() { if (_gs) { gsClear(); _gs.i = 0; gsPlayLine(); } }
function gsSkip() { if (_gs) { gsClear(); _gs.running = true; gsNext(); } }
function gsSpeed(v) { if (!_gs) return; _gs.speed = v; if (_gs.audio) _gs.audio.playbackRate = v; setSpeed(v); gsRender(); }

function gsRender() {
  if (!_gs) return;
  const s = _gs.sents[_gs.i], n = _gs.sents.length, p = _gs.phase;
  const speeds = `<div class="pspd" role="group" aria-label="Speed">${SPEEDS.map(([v, l]) =>
    `<button class="sb" aria-pressed="${_gs.speed === v}" onclick="gsSpeed(${v})">${l}</button>`).join('')}</div>`;

  if (p === 'done') {
    $('view').innerHTML = `<div class="gs">
      <div class="gs-done"><div class="gs-done-t">Nicely done 🎉</div>
        <p>You shadowed all ${n} lines. Do it again a little faster, or head back.</p></div>
      <div class="ctl" style="justify-content:center">
        <button class="tog go" onclick="gsRestart()">Shadow again</button>
        <button class="tog" onclick="gsExit()">Back to Speak</button></div></div>`;
    return;
  }

  const phaseLabel = p === 'listen' ? '🔊 Listen…'
    : p === 'turn' ? '🎤 Your turn — say it back'
    : p === 'paused' ? '⏸ Paused' : 'Ready when you are';
  const bar = p === 'turn' ? `<div class="gs-progbar"><i id="gs-bar" style="width:0%"></i></div>` : `<div class="gs-progbar off"></div>`;
  const playLbl = _gs.running ? '⏸ Pause' : (p === 'idle' ? '▶ Start' : '▶ Resume');

  $('view').innerHTML = `<div class="gs">
    <div class="gs-top"><span>Line ${_gs.i + 1} of ${n}</span>${speeds}</div>
    <div class="gs-card gs-${p}">
      <div class="gs-phase">${phaseLabel}</div>
      <div class="gs-ar" dir="rtl">${esc(s.ar)}</div>
      <div class="gs-en">${esc(s.en || '')}</div>
      ${bar}
    </div>
    <div class="ctl" style="justify-content:center;margin-top:14px">
      <button class="tog go" onclick="gsToggle()">${playLbl}</button>
      <button class="tog" onclick="gsReplay()">↺ Replay line</button>
      <button class="tog" onclick="gsSkip()">Skip →</button>
    </div>
    <div class="ctl" style="justify-content:center">
      <button class="tog" onclick="gsRestart()">Start over</button>
      <button class="tog" onclick="gsExit()">Exit</button>
    </div>
    <p class="hint" style="text-align:center;margin-top:14px">Listen, then echo it out loud — match the melody,
      not just the words. It moves on by itself; pause any time.</p></div>`;
}

// ---------- tray ----------
function count() { const due = dueCards().length;
  $('cnt').textContent = due || marked.size;
  $('cntlbl').textContent = due ? (due === 1 ? 'due' : 'due') : (marked.size === 1 ? 'card' : 'cards');
  $('exp').disabled = !marked.size; $('rev').disabled = !due; }
// Return to wherever you came from (the section list, home, etc.) rather than
// always jumping home. Falls back to home if there's no in-app history.
$('back').onclick = () => { if (history.length > 1) history.back(); else location.hash = '/'; };

// ---------- sidebar drawer ----------
function openSide(){ $('sidebar').classList.add('open'); $('sideScrim').hidden = false;
  $('ham').setAttribute('aria-expanded','true'); $('sidebar').setAttribute('aria-hidden','false'); }
function closeSide(){ $('sidebar').classList.remove('open'); $('sideScrim').hidden = true;
  $('ham').setAttribute('aria-expanded','false'); $('sidebar').setAttribute('aria-hidden','true'); }
$('ham').onclick = () => $('sidebar').classList.contains('open') ? closeSide() : openSide();
$('sideScrim').onclick = closeSide;
addEventListener('keydown', e => { if (e.key === 'Escape') closeSide(); });
$('rev').onclick = () => { _revq = null; location.hash = '/vocab/review'; };
$('exp').onclick = () => ankiExport();

// Single delegated click handler for the whole app. Attached ONCE — a per-render
// listener on the reused #view element stacked with every navigation and played each
// clip multiple times (the echo). Every branch below keys off a distinct class, so one
// handler serves reader, drill, and word cards alike.
$('view').addEventListener('click', e => {
  const pp = e.target.closest('.player .pp');
  if (pp) { const pl = pp.closest('.player');
    if (pl.dataset.para) {
      // Pressing a player that isn't the active one hands control to it first, so a second
      // conversation on the page plays itself rather than the first one.
      if (!PARA || PARA.el !== pl) { const s = PARA_SRCS.get(pl); if (s) paraSetup(pl, s); }
      paraToggle();
    } else toggleSrc(pl); return; }   // play / pause
  // Only the inline players tag their buttons with data-spd. The guided-shadow view reuses
  // the same .pspd markup but drives itself through gsSpeed(), so without this guard the
  // delegated handler also fired there, parsed undefined, and wrote NaN over the saved
  // speed — which then read back as 1x on the next visit.
  const sb = e.target.closest('.pspd .sb');
  if (sb) { const v = parseFloat(sb.dataset.spd);
    if (!isNaN(v)) applySpeed(v, sb.closest('.player'));
    return; }
  const pk = e.target.closest('[data-peek]');
  if (pk) { pk.closest('.sent').classList.add('peek'); return; }
  const lw = e.target.closest('.lx .lw');
  if (lw) {
    const tok = lw.dataset.lw, ctx = {msa: !!lw.closest('.lx-msa')};
    const r = lexLook(tok, true);
    // A miss with the corpus still on disk is not "unknown word" -- it is "we haven't looked
    // yet". Tapping is the clearest possible statement that this lookup is wanted, so it is
    // where the corpus is paid for on a page that didn't prefetch it.
    if (!r && !lexReady()) {
      showWord({surface: tok, lemma: '', gloss: '', _looking: 1}, null, ctx);
      needLexicon().then(() => { lexRefresh();
        showWord(lexLook(tok, true) || {surface: tok, lemma: '', gloss: ''}, null, ctx); }, () => {});
      return;
    }
    showWord(r || {surface: tok, lemma: '', gloss: ''}, null, ctx);
    return; }
  const w = e.target.closest('.rd .w');
  // Mid-phrase, a tap means "this is the other end of the chunk" rather than "open this word".
  if (w) { const si = +w.dataset.s, wi = +w.dataset.w;
    if (_ph) phrasePick(si, wi); else showCard(si, wi);
    return; }
  const a = e.target.closest('.ch .a');
  if (a) { a.classList.toggle('show'); return; }
});
$('view').addEventListener('input', e => {
  const sk = e.target.closest('.player .seek');
  if (sk) { const pl = sk.closest('.player');
    if (pl.dataset.para) paraSeek(parseFloat(sk.value)); else seekTo(pl, parseFloat(sk.value)); }
});

// ---------- accounts & cloud sync (Supabase) ----------
// All progress lives under the alp.* localStorage prefix. Signed in, we mirror that blob to a
// per-user row in Supabase (protected by row-level security) and keep devices in step. Signed out
// or offline, the app is exactly as before — everything stays local. First sign-in on a device MERGES
// local + cloud (union of cards/decks/read-stories/plan-log) so nothing is lost when two devices meet.
// Capture whether we arrived via a magic-link redirect BEFORE the client cleans the URL.
const _hadAuthHash = /access_token=|type=(magiclink|recovery|signup)|error_code=/.test(location.hash || '');
const _sb = (window.SUPA && window.supabase)
  ? window.supabase.createClient(window.SUPA.url, window.SUPA.anon,
      {auth: {persistSession: true, autoRefreshToken: true, detectSessionInUrl: true}})
  : null;
let _user = null, _syncing = false, _applyingRemote = false, _syncTimer = null;
let _loginEmail = '', _navdAfterLogin = false;
const SYNC_AT = 'alp.sync.at';

// What goes to the server. `noSync` holds back the ESV cache (licensed English text that was
// growing this row with every chapter read) and the pre-migration backup (a local safety net --
// uploading it would double every push).
function collectProgress() {
  const o = {};
  for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i);
    if (k && k.startsWith('alp.') && !noSync(k)) o[k] = localStorage.getItem(k); }
  return o;
}
// Write the remote blob over local storage.
//
// This used to delete every `alp.*` key first. That is the single most dangerous line the app
// ever had: a key the blob does not mention was treated as a key the server had deleted. With
// storage namespaced by language it becomes catastrophic -- a phone still running the old build
// pushes a flat `alp.cards.v1`, this device applies that blob, deletes `alp.ar.cards.v1` because
// the blob never named it, and the deck is empty. Then it syncs the emptiness everywhere.
//
// So: absence is not a delete instruction. The blob overwrites what it names and nothing else.
// Nothing is lost by that, because the app has no operation that removes a synced key -- deleting
// a deck or a card rewrites the key's VALUE, which still travels.
function applyProgress(o) {
  _applyingRemote = true;
  try {
    for (const k in o) if (!noSync(k)) localStorage.setItem(k, o[k]);
    // The blob may carry legacy flat keys from a device that hasn't updated. Fold them in here,
    // inside the remote-apply guard, so the merge is one atomic change rather than a burst of
    // writes each scheduling its own push.
    migrateStorage();
  } finally { _applyingRemote = false; }
  reloadState();
}
// re-read the in-memory structures after localStorage changed underneath us, then re-render
function reloadState() {
  try { marked = new Map(JSON.parse(localStorage.getItem(KEY) || 'null') || []); } catch (e) { marked = new Map(); }
  try { decks = JSON.parse(localStorage.getItem(DKEY) || 'null') || [{id: 'default', name: 'My words', created: now()}]; } catch (e) {}
  if (!decks || !decks.length) decks = [{id: 'default', name: 'My words', created: now()}];
  SPEED = parseFloat(localStorage.getItem(SKEY)) || 1;
  count(); route();
}
const localChangedAt = () => +(localStorage.getItem(SYNC_AT) || 0);
function markChanged() { try { localStorage.setItem(SYNC_AT, String(now())); } catch (e) {} }

// hook every alp.* write: a change bumps the local timestamp and (when signed in) schedules a push
const _origSet = localStorage.setItem.bind(localStorage);
localStorage.setItem = function (k, v) {
  _origSet(k, v);
  if (!_applyingRemote && typeof k === 'string' && k.startsWith('alp.') && !noSync(k)) {
    _origSet(SYNC_AT, String(now()));
    if (_user) scheduleSync();
  }
};
function scheduleSync() { if (_syncTimer) clearTimeout(_syncTimer); _syncTimer = setTimeout(pushProgress, 1500); }

// ---- merge: never lose collection progress when two devices first meet ----
// (`_pj` and the MERGERS table that indexes these live at the top of the file, next to the
// migration that uses the same rules.)
function mergeCards(a, b) {                         // arrays of [lemma, card]; keep the more-reviewed
  const m = new Map(); (a || []).forEach(([k, c]) => m.set(k, c));
  (b || []).forEach(([k, c]) => { const e = m.get(k); if (!e || (c.reps || 0) > (e.reps || 0)) m.set(k, c); });
  return [...m];
}
function unionById(a, b) { const m = new Map(); (a || []).forEach(x => m.set(x.id, x));
  (b || []).forEach(x => { if (!m.has(x.id)) m.set(x.id, x); }); return [...m.values()]; }
function unionArr(a, b) { return [...new Set([...(a || []), ...(b || [])])]; }
function mergeLog(a, b) { const out = {...(b || {})};
  for (const d in (a || {})) { out[d] = out[d] || {done: {}}; out[d].done = {...(out[d].done || {}), ...((a[d] || {}).done || {})}; }
  return out; }
function mergeExtra(a, b) { const out = {...(b || {})}; for (const d in (a || {})) out[d] = Math.max(out[d] || 0, a[d] || 0); return out; }
function mergeProgress(loc, rem, cloudNewer) {
  const scalarSrc = cloudNewer ? rem : loc;        // config/scalars follow the more recently used device
  const out = {}; const keys = new Set([...Object.keys(loc || {}), ...Object.keys(rem || {})]);
  keys.forEach(k => { out[k] = (scalarSrc && scalarSrc[k] != null) ? scalarSrc[k] : (loc[k] != null ? loc[k] : rem[k]); });
  // Union-of-keys already carries both languages, since the row holds `alp.ar.*` and
  // `alp.he.*` side by side. The collection merge just has to find its own key whatever the
  // prefix: `alp.ar.cards.v1`, `alp.he.cards.v1` and a legacy flat `alp.cards.v1` each merge
  // with their own counterpart and never with each other.
  keys.forEach(k => {
    const base = Object.keys(MERGERS).find(b => k === 'alp.' + b
      || LANGS_ALL.some(c => k === 'alp.' + c + '.' + b));
    if (base && (loc[k] || rem[k])) out[k] = JSON.stringify(MERGERS[base](_pj(loc[k]), _pj(rem[k])));
  });
  return out;
}

async function pushProgress() {
  if (!_sb || !_user) return;
  _syncing = true; renderAccountBadge();
  try { await _sb.from('progress').upsert({user_id: _user.id, data: collectProgress(), updated_at: new Date().toISOString()}); }
  catch (e) {}
  try { await frPublish(); } catch (e) {}            // keep what friends see in step with the sync
  _syncing = false; renderAccountBadge();
}
async function pullMerge() {
  if (!_sb || !_user) return;
  _syncing = true; renderAccountBadge();
  try {
    const {data} = await _sb.from('progress').select('data, updated_at').eq('user_id', _user.id).maybeSingle();
    const local = collectProgress();
    if (data && data.data) {
      const merged = mergeProgress(local, data.data, +new Date(data.updated_at) >= localChangedAt());
      applyProgress(merged); markChanged();
      await pushProgress();                          // push the merged result so both sides converge
    } else { await pushProgress(); }                 // first device seeds the cloud
  } catch (e) {}
  _syncing = false; renderAccountBadge();
}

// ============ Study together: friend codes, shared numbers, requests ============
// What a friend can see is deliberately narrow: hours, this week's minutes, streak, plan phase
// and card count — no card, no text, nothing about WHAT you studied. Those numbers live in their
// own `stats` table (see supabase/friends.sql); the `progress` table that holds everything else
// is never readable by anyone but you. Nothing is shared until BOTH people accept.
let _frProfile = null, _frCache = null, _frErr = null;
const FR_CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';        // no O/0/I/1 — codes get read aloud
const frCode = () => Array.from({length: 6}, () =>
  FR_CODE_CHARS[Math.floor(Math.random() * FR_CODE_CHARS.length)]).join('');
const frOn = () => !!(_sb && _user);
// The tables are created by hand in the Supabase editor, so a build can be live before they
// exist. Tell those errors apart from real ones and say something useful instead of failing.
const frMissing = e => /relation .* does not exist|schema cache|PGRST205|PGRST202/i.test(
  (e && (e.message || e.details || e.hint)) || '');

async function frEnsureProfile() {
  if (!frOn()) return null;
  if (_frProfile) return _frProfile;
  const {data, error} = await _sb.from('profiles').select('*').eq('user_id', _user.id).maybeSingle();
  if (error) { _frErr = frMissing(error) ? 'setup' : error.message; return null; }
  if (data) { _frProfile = data; return data; }
  // First time: claim a code. Collisions are vanishingly rare (32^6) but a unique index means a
  // clash is a hard error, not a duplicate — so retry a few times rather than trusting luck.
  for (let i = 0; i < 5; i++) {
    const row = {user_id: _user.id, handle: frCode(),
                 display_name: (_user.email || '').split('@')[0].slice(0, 24)};
    const {data: made, error: e2} = await _sb.from('profiles').insert(row).select().maybeSingle();
    if (!e2) { _frProfile = made; return made; }
    if (frMissing(e2)) { _frErr = 'setup'; return null; }
    if (!/duplicate|unique/i.test(e2.message || '')) { _frErr = e2.message; return null; }
  }
  _frErr = 'Could not create a friend code — try again.';
  return null;
}

// The numbers, recomputed from the local log. Pushed alongside progress so a friend's view is
// never staler than your own sync.
function frMyStats() {
  const cfg = planCfg(), L = planLog();
  let week = 0;
  for (let i = 0; i < 7; i++) {
    const d = L[addDaysISO(todayISO(), -i)];
    if (d && d.done) for (const k in d.done) week += d.done[k] || 0;
  }
  const days = Object.keys(L).filter(d => L[d] && L[d].done && Object.keys(L[d].done).length).sort();
  return {hours: Math.round(loggedMinutes() / 6) / 10, week_min: week, streak: planStreak(),
          phase: cfg ? curPhaseIndex(cfg) : 0, cards: marked.size,
          last_active: days.length ? days[days.length - 1] : null,
          updated_at: new Date().toISOString()};
}
async function frPublish() {
  if (!frOn()) return;
  const me = await frEnsureProfile(); if (!me) return;
  try { await _sb.from('stats').upsert(Object.assign({user_id: _user.id}, frMyStats())); }
  catch (e) {}
}

// One round trip for the connections, one for the names, one for the numbers — then stitched
// locally. Friends you've accepted come back with stats; pending ones deliberately don't.
async function frLoad(force) {
  if (!frOn()) return null;
  if (_frCache && !force) return _frCache;
  const me = await frEnsureProfile();
  if (!me) return null;
  const {data: links, error} = await _sb.from('friendships').select('*');
  if (error) { _frErr = frMissing(error) ? 'setup' : error.message; return null; }
  const others = (links || []).map(f => f.user_a === _user.id ? f.user_b : f.user_a);
  let names = {}, nums = {};
  if (others.length) {
    const {data: ps} = await _sb.from('profiles').select('user_id, handle, display_name').in('user_id', others);
    (ps || []).forEach(x => names[x.user_id] = x);
    const {data: st} = await _sb.from('stats').select('*').in('user_id', others);
    (st || []).forEach(x => nums[x.user_id] = x);
  }
  const row = f => { const id = f.user_a === _user.id ? f.user_b : f.user_a;
    return {link: f.id, id, mine: f.requester === _user.id,
            profile: names[id] || {handle: '??????', display_name: 'A friend'}, stats: nums[id] || null}; };
  _frErr = null;
  _frCache = {
    me,
    friends: (links || []).filter(f => f.status === 'accepted').map(row)
      .sort((a, b) => ((b.stats || {}).week_min || 0) - ((a.stats || {}).week_min || 0)),
    incoming: (links || []).filter(f => f.status === 'pending' && f.requester !== _user.id).map(row),
    outgoing: (links || []).filter(f => f.status === 'pending' && f.requester === _user.id).map(row),
  };
  return _frCache;
}

async function frAdd(code) {
  code = String(code || '').trim().toUpperCase();
  const msg = t => { const el = $('fr-msg'); if (el) el.textContent = t; };
  if (!/^[A-Z0-9]{6}$/.test(code)) return msg('A friend code is six letters and numbers.');
  const me = await frEnsureProfile(); if (!me) return msg('Sign in first.');
  if (code === me.handle) return msg("That's your own code — send it to a friend instead.");
  const {data: them, error} = await _sb.from('profiles').select('user_id, display_name').eq('handle', code).maybeSingle();
  if (error) return msg(frMissing(error) ? 'Friends aren’t set up on the server yet.' : error.message);
  if (!them) return msg('No one has that code. Check the letters and try again.');
  const [a, b] = [_user.id, them.user_id].sort();     // the table stores the pair in one order
  const {error: e2} = await _sb.from('friendships').insert({user_a: a, user_b: b, requester: _user.id});
  if (e2) return msg(/duplicate|unique/i.test(e2.message || '')
    ? 'You two are already connected, or a request is already waiting.' : e2.message);
  msg('Request sent to ' + (them.display_name || code) + '. They have to accept before either of you sees anything.');
  const inp = $('fr-code'); if (inp) inp.value = '';
  _frCache = null; frRender();
}
async function frAccept(linkId) {
  await _sb.from('friendships').update({status: 'accepted'}).eq('id', linkId);
  await frPublish();                                  // they can see me now — make sure it's current
  _frCache = null; frRender();
}
async function frRemove(linkId, name) {
  if (!confirm('Disconnect from ' + (name || 'this person') + '?\n\nYou stop seeing each other\'s progress. Nothing you have studied changes.')) return;
  await _sb.from('friendships').delete().eq('id', linkId);
  _frCache = null; frRender();
}
async function frRename() {
  const me = await frEnsureProfile(); if (!me) return;
  const name = prompt('What should friends see you as?', me.display_name || '');
  if (name == null) return;
  await _sb.from('profiles').update({display_name: name.slice(0, 24)}).eq('user_id', _user.id);
  _frProfile = null; _frCache = null; frRender();
}

async function onAuth(session) {
  _user = session ? session.user : null;
  _frProfile = _frCache = _frErr = null;             // never show one account another's friends
  renderAccountBadge();
  if (_user) {
    await pullMerge();
    // If we just landed here from a magic-link email, show the account page once.
    if (_hadAuthHash && !_navdAfterLogin) { _navdAfterLogin = true; location.hash = '#/account'; }
  }
}
let _recovery = false;                                   // in a password-reset (set a new password) flow
if (_sb) {
  _sb.auth.getSession().then(({data}) => onAuth(data.session));
  _sb.auth.onAuthStateChange((_e, session) => {
    if (_e === 'PASSWORD_RECOVERY') {                     // arrived via a reset-password link
      _recovery = true;
      if (!(location.hash || '').startsWith('#/account')) location.hash = '#/account';
    }
    onAuth(session);
  });
}

// ---- account section (email + password; sign in / create / reset) ----
function renderAccountBadge() { if ((location.hash || '').startsWith('#/account')) accountSection(); }

function accountSection() {
  $('back').hidden = false;
  $('title').textContent = 'Account';
  if (!_sb) { $('view').innerHTML = `<div class="empty"><div class="empty-t">Sync isn’t set up</div>
      <p>Cloud sync isn’t configured for this build.</p></div>`; return; }
  if (_recovery) {                                       // arrived from a reset-password link
    $('view').innerHTML = `<div class="hero"><div class="big">
        <div class="k">Reset password</div><div class="t">Set a new password</div>
        <div class="s">Choose a new password for <b>${esc((_user && _user.email) || 'your account')}</b>.
          You'll use it to sign in from now on — on your phone and your computer.</div></div></div>
      <input id="acct-newpass" class="vsearch" type="password" autocomplete="new-password"
        placeholder="New password (6+ characters)" onkeydown="if(event.key==='Enter')acctSetPassword()">
      <div class="ctl" style="margin-top:10px"><button class="tog go" onclick="acctSetPassword()">Save new password</button></div>
      <div id="acct-msg" class="hint" style="margin-top:10px"></div>`;
    return;
  }
  let h;
  if (_user) {
    h = `<div class="hero"><div class="big">
        <div class="k">Signed in</div><div class="t">${esc(_user.email)}</div>
        <div class="s" id="acct-sync">${_syncing ? 'Syncing…' : '✓ Your progress is synced across your devices.'}</div>
      </div></div>
      <div class="ctl"><button class="tog go" onclick="acctSyncNow()">Sync now</button>
        <button class="tog" onclick="acctSignOut()">Sign out</button></div>
      <div class="note">Sign in with the same email on your phone and your computer, and your flashcards,
        study plan, and reading progress stay in step. Signed out, the app still works — it just keeps
        everything on this one device.</div>
      <div id="push-card" style="margin-top:14px"></div>`;
  } else {
    h = `<div class="hero"><div class="big">
        <div class="k">Sync across devices</div><div class="t">Sign in to save your progress</div>
        <div class="s">Use an email and a password — it signs you in right here in the app, phone or
          computer, and your flashcards, study plan and reading progress follow you across them.</div></div></div>
      <input id="acct-email" class="vsearch" type="email" inputmode="email" autocomplete="email" placeholder="you@example.com">
      <input id="acct-pass" class="vsearch" type="password" autocomplete="current-password"
        placeholder="Password (6+ characters)" style="margin-top:8px" onkeydown="if(event.key==='Enter')acctSignIn()">
      <div class="ctl" style="margin-top:10px"><button class="tog go" onclick="acctSignIn()">Sign in</button>
        <button class="tog" onclick="acctSignUp()">Create account</button>
        <button class="tog" onclick="acctReset()">Forgot password?</button></div>
      <div id="acct-msg" class="hint" style="margin-top:10px"></div>
      <div class="note">Signed out, everything works and stays on this device. Signing in just adds cloud
        backup + sync — you can sign out any time.</div>
      <div id="push-card" style="margin-top:14px"></div>`;
  }
  $('view').innerHTML = h + backupCardHTML();
  renderPushCard();
}

// ---- backup & restore ------------------------------------------------------------------------
// Namespacing storage by language is the one change in this app that could lose study history,
// so the escape hatch ships in the same release rather than after the first complaint. A
// snapshot is written automatically before the first key is touched; this panel lets you take
// one on demand, keep it somewhere safe, and paste one back.
//
// Deliberately plain JSON in a text box, not a file-only flow: on an installed iOS PWA a
// downloaded file is easy to lose track of, and a paste always works.
function backupBlob() {
  const data = {};
  for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i);
    if (k && k.startsWith('alp.') && !k.startsWith('alp.backup.')) data[k] = localStorage.getItem(k); }
  return JSON.stringify({v: 1, app: 'alp', at: Date.now(), data});
}
const _bkPre = () => { try { return localStorage.getItem('alp.backup.premigrate.v1'); } catch (e) { return null; } };
function backupCardHTML() {
  const pre = _pj(_bkPre() || 'null');
  const n = Object.keys((_pj(backupBlob()) || {}).data || {}).length;
  return `<div class="note" style="margin-top:14px"><b>Backup &amp; restore</b><br>
      Your flashcards, plan and progress live on this device (and in your account, if you are signed
      in). A backup is a single block of text you can keep anywhere &mdash; ${n} saved
      ${n === 1 ? 'key' : 'keys'} right now.</div>
    <div class="ctl"><button class="tog" onclick="bkCopy()">Copy backup</button>
      <button class="tog" onclick="bkDownload()">Download file</button>
      ${pre ? `<button class="tog" onclick="bkLoadPre()">Load the pre-upgrade snapshot</button>` : ''}</div>
    ${pre ? `<div class="hint">Taken automatically on ${esc(new Date(pre.at || 0).toLocaleString())},
      just before this device split its storage into Arabic and Hebrew.</div>` : ''}
    <textarea id="bk-in" class="vsearch" rows="3" spellcheck="false" dir="ltr"
      style="margin-top:10px;width:100%;font-family:ui-monospace,monospace;font-size:12px"
      placeholder="Paste a backup here to restore it"></textarea>
    <div class="ctl"><button class="tog" onclick="bkRestore()">Restore from this text</button></div>
    <div id="bk-msg" class="hint"></div>`;
}
function bkCopy() {
  navigator.clipboard.writeText(backupBlob())
    .then(() => alert('Backup copied. Paste it somewhere you will still have in a year — a note to yourself, an email, a file.'))
    .catch(() => { const t = $('bk-in'); if (t) { t.value = backupBlob(); t.select(); } });
}
function bkDownload() {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([backupBlob()], {type: 'application/json'}));
  a.download = 'palestinian-arabic-backup-' + todayISO() + '.json';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
function bkLoadPre() { const t = $('bk-in'); if (t) { t.value = _bkPre() || ''; t.focus(); }
  const m = $('bk-msg'); if (m) m.textContent = 'Loaded. Read it if you like, then tap Restore.'; }

// Restore REPLACES, because the point of a restore is to get out of a bad state and a merge
// would keep whatever went wrong. It is still undoable: the current state is snapshotted to
// alp.backup.prerestore.v1 first.
function bkRestore() {
  const msg = $('bk-msg'), say = t => { if (msg) msg.textContent = t; };
  let o = null;
  try { o = JSON.parse((($('bk-in') || {}).value || '').trim()); } catch (e) {}
  const data = o && typeof o === 'object' && (o.data && typeof o.data === 'object' ? o.data : o);
  const keys = data ? Object.keys(data).filter(k => k.startsWith('alp.') && !k.startsWith('alp.backup.')) : [];
  if (!keys.length) return say('That does not look like a backup. Paste the whole block of text, including the outer { }.');
  if (!confirm('Restore ' + keys.length + ' saved ' + (keys.length === 1 ? 'key' : 'keys') + '?\n\n'
    + 'This replaces the study data on THIS device' + (_user ? ', and pushes the restored copy to your other devices' : '')
    + '. The current state is saved first, so you can undo it.')) return;
  _applyingRemote = true;                       // one atomic change, not a burst of pushes
  try {
    localStorage.setItem('alp.backup.prerestore.v1', backupBlob());
    const kill = []; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i);
      if (k && k.startsWith('alp.') && !k.startsWith('alp.backup.')) kill.push(k); }
    kill.forEach(k => localStorage.removeItem(k));
    keys.forEach(k => localStorage.setItem(k, String(data[k])));
    migrateStorage();                           // an old backup is all flat keys; fold them in
  } finally { _applyingRemote = false; }
  markChanged();
  reloadState();
  if (_user) pushProgress();
  alert('Restored. The previous state was saved as a "prerestore" backup on this device.');
}
// Email + password. This is the one method that works inside an installed iOS PWA: no email round
// trip and no magic LINK (which would open Safari, a separate storage jar, so the PWA never gets the
// session). Sign-up needs Supabase Auth → Email → "Confirm email" OFF, so the account is usable at
// once; with it on, signUp returns no session until the (template-gated) confirmation email is used.
function _acctCreds() {
  return {email: (($('acct-email') || {}).value || '').trim(), pass: (($('acct-pass') || {}).value || '')};
}
async function acctSignIn() {
  const {email, pass} = _acctCreds(), msg = $('acct-msg');
  if (!email || !pass) { if (msg) msg.textContent = 'Enter your email and password.'; return; }
  if (msg) msg.textContent = 'Signing in…';
  const {error} = await _sb.auth.signInWithPassword({email, password: pass});
  if (error) { if (msg) msg.textContent = /invalid login/i.test(error.message)
    ? 'Wrong email or password. New here? Tap “Create account”.' : 'Couldn’t sign in: ' + error.message; }
  // success → onAuthStateChange → onAuth() re-renders as signed-in
}
async function acctSignUp() {
  const {email, pass} = _acctCreds(), msg = $('acct-msg');
  if (!email || pass.length < 6) { if (msg) msg.textContent = 'Enter an email and a password of at least 6 characters.'; return; }
  if (msg) msg.textContent = 'Creating your account…';
  const {data, error} = await _sb.auth.signUp({email, password: pass});
  if (error) { if (msg) msg.textContent = /already|registered|exists/i.test(error.message)
    ? 'You already have an account with this email. Tap “Sign in”, or “Forgot password?” to set a password on it.'
    : 'Couldn’t create the account: ' + error.message; return; }
  if (!data.session && msg) msg.textContent = 'Account created — now tap “Sign in”. (If it asks you to confirm by email, turn off Auth → Email → “Confirm email” in Supabase.)';
  // if a session came back (Confirm email OFF) → onAuth() re-renders as signed-in
}
// Send a reset-password email. The link opens a page where a new password is set (updateUser);
// after that you sign in with email + the new password — which works in the PWA. This is also how
// an OLD passwordless account (created before the switch) gets its first password.
async function acctReset() {
  const {email} = _acctCreds(), msg = $('acct-msg');
  if (!email) { if (msg) msg.textContent = 'Type your email above first, then tap “Forgot password?”.'; return; }
  if (msg) msg.textContent = 'Sending a reset email…';
  const {error} = await _sb.auth.resetPasswordForEmail(email, {redirectTo: location.origin + location.pathname});
  if (error) { if (msg) msg.textContent = 'Couldn’t send it: ' + error.message; return; }
  if (msg) msg.textContent = 'Check your email for a reset link. Open it, set a new password, then come back here and sign in.';
}
async function acctSetPassword() {
  const pass = (($('acct-newpass') || {}).value || ''); const msg = $('acct-msg');
  if (pass.length < 6) { if (msg) msg.textContent = 'Password must be at least 6 characters.'; return; }
  if (msg) msg.textContent = 'Saving…';
  const {error} = await _sb.auth.updateUser({password: pass});
  if (error) { if (msg) msg.textContent = 'Couldn’t save: ' + error.message; return; }
  _recovery = false; accountSection();                   // now signed in with the new password
}
async function acctSignOut() { try { await _sb.auth.signOut(); } catch (e) {} _user = null; accountSection(); }

// ---- push notifications: lock-screen practice reminders --------------------------------------
// Web Push. The browser subscribes with the VAPID PUBLIC key; we store the subscription in Supabase
// (`push_subscriptions`); a scheduled GitHub Action (pipeline/send_push.py) signs and sends the
// reminders with the VAPID PRIVATE key. That private key and the Supabase service_role key live ONLY
// in GitHub secrets — never in this file. iOS delivers web push ONLY after the app is added to the
// Home Screen (a PWA), on iOS 16.4+, with permission granted.
const PUSH_PUB = ((window.PUSH_PUBLIC_KEY || '') + '').trim();
const pushConfigured = () => PUSH_PUB.length > 20;
const pushSupported = () => 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
function urlB64ToUint8(b64) {
  const pad = '='.repeat((4 - b64.length % 4) % 4);
  const s = (b64 + pad).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(s), arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr;
}
async function pushCurrentSub() {
  try { const reg = await navigator.serviceWorker.ready; return await reg.pushManager.getSubscription(); }
  catch (e) { return null; }
}
// Saved via a DIRECT REST call with Prefer: return=minimal — NOT supabase-js .upsert(), which asks
// for the row back (return=representation) and RLS rejects that whole write because the table has no
// SELECT policy (subscriptions are read only by the server). return=minimal skips the RETURNING.
// We authenticate with the ANON key (role `anon`) even when signed in: the anon INSERT policy is the
// one that actually accepts the write, and check(true) lets us still stamp our own user_id in the row.
// A plain INSERT (return=minimal). Deliberately NOT an upsert: only the INSERT RLS policy is
// effective on this table (the ON-CONFLICT/UPDATE variants 401), so we insert and treat a duplicate
// (409/23505 — this endpoint already registered) as success. p256dh/auth are fixed per endpoint, so
// the existing row is already correct; nothing to update.
async function _pushInsert(body) {
  try {
    const r = await fetch(window.SUPA.url + '/rest/v1/push_subscriptions', {
      method: 'POST',
      headers: {apikey: window.SUPA.anon, Authorization: 'Bearer ' + window.SUPA.anon,
        'Content-Type': 'application/json', Prefer: 'return=minimal'},
      body: JSON.stringify(body)
    });
    return {ok: r.ok || r.status === 409, status: r.status, text: r.ok ? '' : (await r.text()).slice(0, 140)};
  } catch (e) { return {ok: false, status: 0, text: String(e.message || e)}; }
}
async function savePushSub(sub) {
  if (!window.SUPA) return {error: {message: 'sync not configured'}};
  const j = sub.toJSON();
  const body = {endpoint: j.endpoint, p256dh: j.keys.p256dh, auth: j.keys.auth,
    tz: 'Asia/Jerusalem', updated_at: new Date().toISOString()};
  if (_user && _user.id) body.user_id = _user.id;
  let r = await _pushInsert(body);
  if (r.ok) return {};
  if (body.user_id) { const b2 = {...body}; delete b2.user_id; r = await _pushInsert(b2); if (r.ok) return {}; }  // fall back to an anonymous sub
  return {error: {message: 'HTTP ' + r.status + ' ' + r.text}};
}
async function deletePushSub(endpoint) {
  if (!window.SUPA) return;
  try {
    await fetch(window.SUPA.url + '/rest/v1/push_subscriptions?endpoint=eq.' + encodeURIComponent(endpoint),
      {method: 'DELETE', headers: {apikey: window.SUPA.anon, Authorization: 'Bearer ' + window.SUPA.anon, Prefer: 'return=minimal'}});
  } catch (e) {}
}
async function pushEnable() {
  const msg = $('push-msg');
  if (!pushSupported() || !pushConfigured()) return;
  try {
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') { if (msg) msg.textContent = 'Notifications are blocked — allow them for this site in your browser settings, then try again.'; return; }
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: urlB64ToUint8(PUSH_PUB)});
    const res = await savePushSub(sub);
    if (res && res.error) { if (msg) msg.textContent = 'Subscribed on this device, but saving it failed: ' + res.error.message; return; }
    accountSection();
  } catch (e) { if (msg) msg.textContent = 'Could not enable reminders: ' + (e.message || e); }
}
async function pushDisable() {
  const sub = await pushCurrentSub();
  if (sub) { await deletePushSub(sub.endpoint); try { await sub.unsubscribe(); } catch (e) {} }
  accountSection();
}
function pushCardHTML(on) {
  const wrap = inner => `<div class="pimc"><div class="pimc-t">Practice reminders</div>${inner}</div>`;
  if (!pushSupported()) return wrap(`<p class="hint" style="margin:4px 0 0">This browser can't do reminders.
     On iPhone, add the app to your Home Screen (Share → Add to Home Screen), open it from there, then come back.</p>`);
  if (!pushConfigured()) return wrap(`<p class="hint" style="margin:4px 0 0">Reminders aren't switched on for this site yet.</p>`);
  return wrap(`<p class="hint" style="margin:4px 0 8px">A gentle lock-screen nudge on days you haven't practised yet —
     it keeps the streak alive, and stops once you've done something. Nothing else is ever sent.</p>
    <div class="ctl">${on
      ? `<button class="tog" onclick="pushDisable()">Turn off reminders</button>`
      : `<button class="tog go" onclick="pushEnable()">Turn on reminders</button>`}</div>
    <div id="push-msg" class="hint" style="margin-top:8px"></div>`);
}
async function renderPushCard() {
  const el = $('push-card'); if (!el) return;
  el.innerHTML = pushCardHTML(!!(await pushCurrentSub()));
}
async function acctSyncNow() { await pushProgress(); await pullMerge();
  const s = $('acct-sync'); if (s) s.textContent = '✓ Synced just now.'; }

// The switcher mounts once, here rather than at the seam, because it needs esc() and the
// header element -- both of which exist by the time the boot runs.
const _lsw = $('langsw'); if (_lsw) _lsw.innerHTML = langSwitchHTML();
// The sidebar wordmark: the product over the language. It was hardcoded القهوة in index.html
// until Hebrew arrived, then briefly a per-language coffee-house name I had invented because
// the app had no name of its own. It has one now.
const _sb2 = $('sideBrand');
if (_sb2) _sb2.innerHTML = esc(ALP.name) + '<span>' + esc(LANG.name) + '</span>';

count();
route();

// Register the service worker so the app is installable to the home screen and works offline.
// The SW fetches the HTML network-first, so a new deploy is never masked by a stale cache.
if ('serviceWorker' in navigator) {
  addEventListener('load', () => navigator.serviceWorker.register('service-worker.js').catch(() => {}));
}
