#!/usr/bin/env python3
"""Build the verb dataset: every Maknuune verb, classified by Form + weak class,
with its three principal parts (past/present/imperative), gloss, and pronunciation.

Everything here is LOOKED UP from Maknuune (CC BY-SA) — principal parts, gloss, CAPHI.
Only the Form/weak classification is computed (verbforms.py), and that's derivable
grammar, not a guess. No conjugation is invented here — full paradigms come later,
verified per class.

Ranking: Maknuune has no frequency field. Two signals decide the top 1000, in order:

  1. A curated CORE of the verbs every Levantine learner needs first (go, come, see,
     want, eat…). These are guaranteed inclusion and sit at the top. Corpus-derivative
     count alone misses them — شاف "see", مشى "walk", صار "become" are lexically lean
     (few dictionary derivatives) yet spoken constantly. The list only decides PRIORITY;
     every conjugation shown is still looked up from Maknuune, never invented. Core verbs
     Maknuune has no VERB entry for are reported and simply omitted — we don't fabricate.
  2. A corpus proxy for everything after: how many lexicon entries share the verb's root
     (senses, phrases, examples). Crude, but it orders the workhorse tail sensibly.
"""
import pandas as pd, json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verbforms import classify, bare, weak_class
from subdialect import realize

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
df = pd.read_parquet(os.path.join(ROOT, 'data', 'maknuune.parquet'))

# --- curated core: the essential Levantine/Palestinian verbs, as past-tense (3ms) forms.
# Resolved to roots against Maknuune below, so exact spelling/root stays the lexicon's.
CORE_VERBS = """
راح مشى رجع وصل طلع نزل دخل خرج سافر وقف قعد نام صحي ركض ركب هرب لحق مرق لف رجّع
شاف سمع عرف فهم حفظ نسي فكّر حسّ لاحظ شعر عدّ
حكى قال سأل جاوب ردّ صرخ نادى خبّر
ودّ حبّ كره فضّل تمنّى خاف زعل فرح استنّى
أكل شرب طبخ لبس غسل نظّف اشترى باع دفع صرف ذاق شمّ
اشتغل درس تعلّم علّم كتب قرا عمل سوّى ساعد جرّب بلّش خلّص بطّل شغّل
صار ضلّ بقي كان قدر لزم احتاج قبل رفض قرّر
عطى أخذ جاب حطّ شال مسك رمى لقى ضيّع لبّس ناول ترك
زار قابل تجوّز مات عاش ضحك بكى لعب رقص غنّى سكن ولد نسي
فتح سكّر كسر صلّح بنى غيّر حرّك دقّ ضرب قتل قصّ كبّر صغّر
بعث ودّى اتّصل استلم وصّل وعد سمّى أرسل
""".split()

def _norm(x):
    x = str(x).replace('ـ', '').translate({ord(c): None for c in 'ًٌٍَُِّْٰ'})
    return x.translate({ord('أ'):'ا', ord('إ'):'ا', ord('آ'):'ا', ord('ى'):'ي', ord('ة'):'ه'})

# Map every verb lemma → its root(s), for resolving the core list.
_vrows = df[df['ANALYSIS'].astype(str).str.startswith('VERB:', na=False)]
_lemma_roots = {}
for lem, rt in zip(_vrows['LEMMA'].astype(str), _vrows['ROOT'].astype(str)):
    _lemma_roots.setdefault(_norm(lem), set()).add(rt)

CORE_ROOTS, _missing = set(), []
for cv in CORE_VERBS:
    roots = _lemma_roots.get(_norm(cv))
    if roots: CORE_ROOTS |= {r for r in roots if r not in ('NTWS', 'nan', '')}
    else:     _missing.append(cv)
if _missing:
    print('core verbs with no Maknuune VERB entry (omitted, not fabricated):',
          ' '.join(_missing))
print('curated core: %d verbs → %d roots' % (len(CORE_VERBS), len(CORE_ROOTS)))

# Verbs the reference grammar conjugates are guaranteed inclusion too. It teaches 104
# verbs chosen for learners, and a third of them fell below the lexicon-derivative ranking
# (celebrate, be happy, have lunch, be born…). The grammar only affects PRIORITY — every
# part is still looked up from Maknuune. The PDF is gitignored, so build proceeds without
# the signal when it isn't on disk (and says so).
BOOK_KEYS = set()
try:
    from book_sweep import book_tables, onset_key
    BOOK_KEYS = {onset_key(p3) for _pg, _cls, _gl, p3, _i3 in book_tables()}
    print('reference grammar verbs feeding the ranking:', len(BOOK_KEYS))
except Exception as _e:
    print('reference grammar not on disk (%s) — ranking without it' % _e)
    onset_key = lambda s: s                # unused when BOOK_KEYS is empty

# root frequency proxy: entries per root across the whole lexicon
_rf = df['ROOT'].astype(str).value_counts().to_dict()
CORE_BONUS = 1_000_000                    # guarantees every core root outranks the tail
BOOK_BONUS = 500_000                      # below the curated core, above the whole tail
def rootscore(root):
    r = str(root)
    if r in ('NTWS', 'nan', '') or '.' not in r:   # rootless / quad-ish → low base
        return CORE_BONUS if r in CORE_ROOTS else 0
    return (CORE_BONUS if r in CORE_ROOTS else 0) + _rf.get(r, 0)

v = df[df['ANALYSIS'].astype(str).str.match(r'VERB:[PIC]$', na=False)].copy()
v['stem'] = v['ANALYSIS'].str.split(':').str[1]

verbs = {}
for r in v.to_dict('records'):
    key = str(r['LEMMA'])
    e = verbs.setdefault(key, {'lemma': key, 'root': str(r['ROOT']),
                               'gloss': '', 'parts': {}})
    e['parts'][r['stem']] = {
        'ar': str(r['FORM']),
        'caphi': realize(str(r['CAPHI++']), 'urban'),
        'id': str(r['ID']),
    }
    if r['stem'] == 'P' and not e['gloss']:
        e['gloss'] = str(r['GLOSS'])

out = []
for e in verbs.values():
    P = e['parts'].get('P')
    if not P: continue                      # need at least the perfect to anchor a verb
    cls = classify(P['ar'], (e['parts'].get('I') or {}).get('ar', ''), e['root'])
    out.append({
        'lemma': e['lemma'], 'root': e['root'], 'gloss': e['gloss'],
        'form': cls['form'], 'weak': cls['weak'],
        'past':  P,
        'pres':  e['parts'].get('I'),
        'imp':   e['parts'].get('C'),
        'freq':  rootscore(e['root'])
                 + (BOOK_BONUS if onset_key(P['caphi']) in BOOK_KEYS else 0),
        'core':  e['root'] in CORE_ROOTS,
    })

out.sort(key=lambda x: -x['freq'])
from collections import Counter
print('total verbs:', len(out))
print('\nby Form:')
for f, n in sorted(Counter(str(x['form']) for x in out).items()):
    print('  Form %-3s %5d' % (f, n))
print('\nby weak class:')
for w, n in Counter(x['weak'] for x in out).most_common():
    print('  %-12s %5d' % (w, n))

# The top-3000 cut is a *frequency* judgement, and frequency is not the only thing that makes a
# verb worth shipping: a verb the learner will actually meet, in a story or a news item or a
# chapter of a book, needs its paradigm whether or not the proxy ranked it. Before this, 193 of
# the 790 verb lemmas in the reading corpus (654 tokens) had no conjugation to open — tapping
# them in the reader showed a gloss and nothing else. So the cut is a UNION: the top 3000, plus
# every verb the shipped content attests. Nothing is generated; these entries already existed in
# Maknuune and were simply below the line.
def attested_lemmas():
    import glob
    seen = set()
    for f in glob.glob(os.path.join(ROOT, 'build', '*', 'text.json')):
        try: d = json.load(open(f, encoding='utf-8'))
        except Exception: continue
        for sn in d.get('sentences', []):
            for w in sn.get('words', []):
                if str(w.get('analysis', '')).startswith('VERB') and w.get('lemma'):
                    seen.add(w['lemma'])
    return seen

ATT = attested_lemmas()
top = out[:3000]
_have = {x['lemma'] for x in top}
extra = [x for x in out[3000:] if x['lemma'] in ATT and x['lemma'] not in _have]
top += extra
missing = ATT - {x['lemma'] for x in top}
print('\ncontent-attested verb lemmas: %d' % len(ATT))
print('  already inside the top 3000 : %d' % len(ATT & _have))
print('  pulled up from below the cut: %d' % len(extra))
print('  still with no entry at all  : %d  (aspect-only citation forms and mis-resolutions —'
      ' these have no VERB:P row in Maknuune to anchor a paradigm)' % len(missing))
print('shipping %d verbs' % len(top))

print('\ntop 20 by frequency proxy:')
for x in top[:20]:
    pp = x['past']['caphi'] + ' / ' + (x['pres']['caphi'] if x['pres'] else '—')
    print('  F%-2s %-10s %-22s %s' % (x['form'], pp[:20], (x['gloss'] or '')[:26], x['root']))

# Full paradigms — all four Form I weak classes plus Form II (measure II). The engine is
# DERIVED by rule and verified against the Lingualism reference (pipeline/verify_conjugation.py:
# 98.7% overall; residual is optional variation, not error). Verbs that don't parse cleanly
# keep just their principal parts, so a misfiled entry can never emit a bad paradigm.
from conjugate import (conjugate, conjugate_hollow, conjugate_defective, conjugate_geminate,
                       conjugate_II, conjugate_II_defective, conjugate_III, conjugate_IV,
                       conjugate_V, conjugate_VI,
                       conjugate_VII, conjugate_VIII, conjugate_X,
                       conjugate_assimilated, conjugate_hamzated_akal,
                       conjugate_VIII_defective, conjugate_X_gemdef, conjugate_ija,
                       vocalize_cell)
# Dispatch by measure. Form I splits by weak class; derived measures have one engine each
# (parsers reject anything not matching the measure's template → principal parts only).
# hamzated chains: أكل/أخذ take the irregular engine; hamza-final verbs like قرا (2ara/yi2ra)
# behave as defectives; anything else falls through to sound (سأل-type) or stays parts-only.
_FORM1 = {'sound': conjugate, 'hollow': conjugate_hollow,
          'defective': conjugate_defective, 'doubled': conjugate_geminate,
          'assimilated': conjugate_assimilated,
          'hamzated': (lambda rt,pa,pr: conjugate_hamzated_akal(rt,pa,pr)
                       or conjugate_defective(rt,pa,pr) or conjugate(rt,pa,pr))}
_MEASURE = {2: (lambda rt,pa,pr: conjugate_II(rt,pa,pr) or conjugate_II_defective(rt,pa,pr)), 3: conjugate_III, 4: conjugate_IV, 5: conjugate_V,
            6: conjugate_VI, 7: conjugate_VII,
            8: (lambda rt,pa,pr: conjugate_VIII(rt,pa,pr) or conjugate_VIII_defective(rt,pa,pr)),
            10: (lambda rt,pa,pr: conjugate_X(rt,pa,pr) or conjugate_X_gemdef(rt,pa,pr))}
def paradigm(x):
    if not x['pres']:
        return None
    root, pa, pr = x['root'], x['past']['caphi'], x['pres']['caphi']
    if x['form'] == 1:
        eng = _FORM1.get(x['weak'])
        return eng(root, pa, pr) if eng else None
    eng = _MEASURE.get(x['form'])
    return eng(root, pa, pr) if eng else None

# Roman numerals for display; group label per Form.
ROMAN = {1:'I',2:'II',3:'III',4:'IV',5:'V',6:'VI',7:'VII',8:'VIII',10:'X','Q':'Q'}
from book_overrides import override_for, DROP
def slim(x):
    if (x['root'], ROMAN.get(x['form'], '?'), (x['past'] or {}).get('caphi')) in DROP:
        return None                       # duplicate record superseded by a book override
    # The reference grammar outranks the lexicon on how a verb CONJUGATES: Maknuune records
    # one citation form and can't say which of two competing vowellings people actually use.
    ov = override_for(x['root'], ROMAN.get(x['form'], '?'),
                      (x['past'] or {}).get('caphi'))
    if ov:
        x = dict(x, past={'ar': ov['past_ar'], 'caphi': ov['past']},
                 pres={'ar': ov['pres_ar'], 'caphi': ov['pres']},
                 lemma=ov['past_ar'], _note=ov['note'])
    part = lambda pp: pp and {'ar': pp['ar'], 'caphi': pp['caphi']}
    d = {
        'lemma': x['lemma'], 'root': x['root'],
        'gloss': (x['gloss'] or '').replace('_',' ').replace(';',' · ').split(' [auto]')[0],
        'form': ROMAN.get(x['form'], '?'), 'weak': x['weak'], 'core': x['core'],
        'past': part(x['past']), 'pres': part(x['pres']), 'imp': part(x['imp']),
    }
    if x.get('_note'): d['note'] = x['_note']; d['src'] = 'book'
    conj = paradigm(x)
    if conj:
        # `arv` = the same form with harakat, rendered from the romanization the engine already
        # derived. Cells the renderer can't align exactly get no `arv` and the app shows the
        # plain spelling — a wrong vowel teaches a wrong word.
        for cell in conj.values():
            v = vocalize_cell(cell['ar'], cell['ph'])
            if v: cell['arv'] = v
        d['conj'] = conj
    return d
data = {'verbs': [s for s in (slim(x) for x in top) if s]}

# إجا "to come" — the most common motion verb in the language, and the one everyday verb
# Maknuune has no VERB entry for (the build's own report shows it omitted). Its paradigm is
# NOT invented: it is the 'irregular defective measure I' table of the same Lingualism
# reference every engine here is verified against (checked cell-for-cell by
# verify_conjugation.py). Provenance carried in `src` so the UI can say so.
data['verbs'].insert(0, {
    'lemma': 'أَجَا', 'root': 'ج.ي.ء', 'gloss': 'come',
    'form': 'I', 'weak': 'irregular', 'core': True, 'src': 'book',
    'past': {'ar': 'أَجَا', 'caphi': 'aja'},
    'pres': {'ar': 'يِيجِي', 'caphi': 'yiiji'},
    'imp':  {'ar': 'تَعَال', 'caphi': 'ta3aal'},
    'conj': conjugate_ija(),
})

# Three more verbs the grammar conjugates but Maknuune lacks entirely (checked directly in
# the parquet). Same footing as أجا: principal parts from the book's own tables, paradigms
# generated by our engines from those parts. اِسْتَفَزّ has no engine for its class
# (geminate Form X) yet, so it ships with principal parts only — never a fabricated table.
from conjugate import conjugate_III as _c3, conjugate_VII as _c7
_BOOK_ONLY = [
    dict(lemma='عَامَل', root='ع.م.ل', gloss='treat sb (in a certain way)', form='III',
         weak='sound', core=True, src='book',
         past={'ar': 'عَامَل', 'caphi': '3aamal'}, pres={'ar': 'يْعَامِل', 'caphi': 'y3aamil'},
         imp={'ar': 'عَامِل', 'caphi': '3aamil'}, conj=_c3('ع.م.ل', '3aamal', 'y3aamil')),
    dict(lemma='اِنْوَلَد', root='و.ل.د', gloss='be born', form='VII', weak='sound',
         core=True, src='book',
         past={'ar': 'اِنْوَلَد', 'caphi': 'inwalad'}, pres={'ar': 'يِنْوِلِد', 'caphi': 'yinwilid'},
         imp=None, conj=_c7('و.ل.د', 'inwalad', 'yinwilid')),
    dict(lemma='اِسْتَفَزّ', root='ف.ز.ز', gloss='provoke', form='X', weak='doubled',
         core=True, src='book',
         past={'ar': 'اِسْتَفَزّ', 'caphi': 'istafazz'}, pres={'ar': 'يِسْتَفِزّ', 'caphi': 'yistafizz'},
         imp=None),
]
for _b in _BOOK_ONLY:
    if _b.get('conj'):
        for _cell in _b['conj'].values():
            _v = vocalize_cell(_cell['ar'], _cell['ph'])
            if _v: _cell['arv'] = _v
    else:
        _b.pop('conj', None)
    data['verbs'].insert(1, _b)
_cells = [c for v in data['verbs'] for c in (v.get('conj') or {}).values()]
print('vocalized cells: %d/%d (%.1f%%) — the rest show unvocalized rather than guess'
      % (sum(1 for c in _cells if 'arv' in c), len(_cells),
         100 * sum(1 for c in _cells if 'arv' in c) / max(len(_cells), 1)))
_nconj = sum(1 for v in data['verbs'] if 'conj' in v)
_bycls = Counter(v['weak'] for v in data['verbs'] if 'conj' in v)
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- where this language's generated data lives

print('\nfull paradigms attached (Form I): %d verbs — %s' % (_nconj, dict(_bycls)))
with open(paths.data('verbs.js'), 'w', encoding='utf-8') as f:
    f.write('// GENERATED by pipeline/build_verbs.py — do not edit.\n')
    f.write('window.VERBS = '); json.dump(data, f, ensure_ascii=False); f.write(';\n')
# len(top) misses the four hand-added verbs inserted above (it read 3000 while shipping 3003).
print('\n-> app/data/verbs.js  (%d verbs)' % len(data['verbs']))
print('   size:', os.path.getsize(os.path.join(ROOT,'app','data','verbs.js'))//1024, 'KB')
