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
عطى أخذ جاب حطّ شال مسك رمى لقى ضيّع لبّس ناول
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

# root frequency proxy: entries per root across the whole lexicon
_rf = df['ROOT'].astype(str).value_counts().to_dict()
CORE_BONUS = 1_000_000                    # guarantees every core root outranks the tail
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
        'freq':  rootscore(e['root']),
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

top = out[:1000]
print('\ntop 20 by frequency proxy:')
for x in top[:20]:
    pp = x['past']['caphi'] + ' / ' + (x['pres']['caphi'] if x['pres'] else '—')
    print('  F%-2s %-10s %-22s %s' % (x['form'], pp[:20], (x['gloss'] or '')[:26], x['root']))

# Full paradigms — all four Form I weak classes plus Form II (measure II). The engine is
# DERIVED by rule and verified against the Lingualism reference (pipeline/verify_conjugation.py:
# 98.7% overall; residual is optional variation, not error). Verbs that don't parse cleanly
# keep just their principal parts, so a misfiled entry can never emit a bad paradigm.
from conjugate import (conjugate, conjugate_hollow, conjugate_defective,
                       conjugate_geminate, conjugate_II)
# Dispatch by (measure, weak class). Form I splits by weak class; Form II is regular.
_FORM1 = {'sound': conjugate, 'hollow': conjugate_hollow,
          'defective': conjugate_defective, 'doubled': conjugate_geminate}
def paradigm(x):
    if not x['pres']:
        return None
    root, pa, pr = x['root'], x['past']['caphi'], x['pres']['caphi']
    if x['form'] == 1:
        eng = _FORM1.get(x['weak'])
        return eng(root, pa, pr) if eng else None
    if x['form'] == 2:
        return conjugate_II(root, pa, pr)
    return None

# Roman numerals for display; group label per Form.
ROMAN = {1:'I',2:'II',3:'III',4:'IV',5:'V',6:'VI',7:'VII',8:'VIII',10:'X','Q':'Q'}
def slim(x):
    part = lambda pp: pp and {'ar': pp['ar'], 'caphi': pp['caphi']}
    d = {
        'lemma': x['lemma'], 'root': x['root'],
        'gloss': (x['gloss'] or '').replace('_',' ').replace(';',' · ').split(' [auto]')[0],
        'form': ROMAN.get(x['form'], '?'), 'weak': x['weak'], 'core': x['core'],
        'past': part(x['past']), 'pres': part(x['pres']), 'imp': part(x['imp']),
    }
    conj = paradigm(x)
    if conj: d['conj'] = conj
    return d
data = {'verbs': [slim(x) for x in top]}
_nconj = sum(1 for v in data['verbs'] if 'conj' in v)
_bycls = Counter(v['weak'] for v in data['verbs'] if 'conj' in v)
print('\nfull paradigms attached (Form I): %d verbs — %s' % (_nconj, dict(_bycls)))
os.makedirs(os.path.join(ROOT, 'app', 'data'), exist_ok=True)
with open(os.path.join(ROOT, 'app', 'data', 'verbs.js'), 'w', encoding='utf-8') as f:
    f.write('// GENERATED by pipeline/build_verbs.py — do not edit.\n')
    f.write('window.VERBS = '); json.dump(data, f, ensure_ascii=False); f.write(';\n')
print('\n-> app/data/verbs.js  (%d verbs)' % len(top))
print('   size:', os.path.getsize(os.path.join(ROOT,'app','data','verbs.js'))//1024, 'KB')
