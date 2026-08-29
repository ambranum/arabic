#!/usr/bin/env python3
"""Apply pipeline/book_overrides.py to the built app/data/verbs.js.

build_verbs.py is the proper home for this, but a full rebuild needs
data/maknuune.parquet, which is frequently iCloud-offloaded. This script needs only
verbs.js and conjugate.py, so a correction can ship either way. Re-running build_verbs.py
later is harmless — it applies the same overrides and produces the same result.

Run: python3 pipeline/apply_book_overrides.py   (then python3 pipeline/build_app.py)
"""
import json, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, '..')
from book_overrides import OVERRIDES, override_for
from conjugate import (conjugate, conjugate_hollow, conjugate_defective, conjugate_geminate,
                       conjugate_II, conjugate_II_defective, conjugate_III, conjugate_IV,
                       conjugate_V, conjugate_VI, conjugate_VII, conjugate_VIII, conjugate_X,
                       conjugate_assimilated, conjugate_hamzated_akal,
                       conjugate_VIII_defective, conjugate_X_gemdef, vocalize_cell)

FORM1 = {'sound': conjugate, 'hollow': conjugate_hollow, 'defective': conjugate_defective,
         'doubled': conjugate_geminate, 'assimilated': conjugate_assimilated,
         'hamzated': lambda r, p, i: (conjugate_hamzated_akal(r, p, i)
                                      or conjugate_defective(r, p, i) or conjugate(r, p, i))}
MEASURE = {'II': lambda r, p, i: conjugate_II(r, p, i) or conjugate_II_defective(r, p, i),
           'III': conjugate_III, 'IV': conjugate_IV, 'V': conjugate_V, 'VI': conjugate_VI,
           'VII': conjugate_VII,
           'VIII': lambda r, p, i: conjugate_VIII(r, p, i) or conjugate_VIII_defective(r, p, i),
           'X': lambda r, p, i: conjugate_X(r, p, i) or conjugate_X_gemdef(r, p, i)}

def paradigm(v, past_ph, pres_ph):
    if v['form'] == 'I':
        eng = FORM1.get(v.get('weak'))
        return eng(v['root'], past_ph, pres_ph) if eng else None
    eng = MEASURE.get(v['form'])
    return eng(v['root'], past_ph, pres_ph) if eng else None

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- where this language's generated data lives

def main():
    p = paths.data('verbs.js')
    src = open(p, encoding='utf-8').read()
    head = src[:src.index('window.VERBS = ') + len('window.VERBS = ')]
    data = json.loads(src[src.index('{'): src.rindex(';')])

    applied, failed = [], []
    for v in data['verbs']:
        ov = override_for(v.get('root'), v.get('form'), (v.get('past') or {}).get('caphi'))
        if not ov:
            continue
        conj = paradigm(v, ov['past'], ov['pres'])
        if not conj:
            failed.append(v['lemma']); continue
        for cell in conj.values():
            a = vocalize_cell(cell['ar'], cell['ph'])
            if a: cell['arv'] = a
        before = (v['past']['caphi'], v['pres']['caphi'])
        v['past'] = {'ar': ov['past_ar'], 'caphi': ov['past']}
        v['pres'] = {'ar': ov['pres_ar'], 'caphi': ov['pres']}
        v['lemma'] = ov['past_ar']
        v['conj'] = conj
        v['note'] = ov['note']
        v['src'] = 'book'
        applied.append((v['lemma'], before, (ov['past'], ov['pres'])))

    with open(p, 'w', encoding='utf-8') as f:
        f.write(head); json.dump(data, f, ensure_ascii=False); f.write(';\n')

    for lem, b, a in applied:
        print(f'  {lem}: {b[0]}/{b[1]}  ->  {a[0]}/{a[1]}  (book)')
    print(f'overrides applied: {len(applied)}' + (f'  FAILED: {failed}' if failed else ''))
    return 0

if __name__ == '__main__':
    sys.exit(main())
