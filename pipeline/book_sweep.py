#!/usr/bin/env python3
"""Compare every verb the reference grammar conjugates against what the app ships.

Reads reference/Palestinian_Arabic_Verbs_-_Lingualism.pdf (gitignored, copyrighted — used
for VERIFICATION only, never shipped) and pulls just two facts per table: the 3ms perfect
and the 3ms imperfect, in the app's own romanization. Those are linguistic facts, not the
book's prose or its tables; nothing from the book is written into the repo by this script.

Its whole job is to surface DISAGREEMENTS for a human to adjudicate — the عمل case, where
Maknuune recorded a minority vowelling and the grammar prints the majority one. Confirmed
ones go into pipeline/book_overrides.py by hand.

Run: python3 pipeline/book_sweep.py
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
PDF = os.path.join(ROOT, 'reference', 'Palestinian_Arabic_Verbs_-_Lingualism.pdf')
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

AR = lambda ch: ('؀' <= ch <= 'ۿ') or ('ﭐ' <= ch <= '﻿') or ch == 'ـ'
strip_ar = lambda s: ''.join(c for c in s if not AR(c))
JUNK = set('£:eF')

def canon(t):
    """The book's romanization -> ours (same mapping verify_conjugation.py uses)."""
    if not t: return t
    s = t.replace(':', '').replace('F', '')
    for a, b in [('ā','aa'),('ī','ii'),('ū','uu'),('ē','ee'),('ō','oo'),('á','a'),('í','i'),('ú','u')]:
        s = s.replace(a, b)
    return (s.replace('ʔ','2').replace('g','2').replace('š','sh').replace('x','kh')
             .replace('ɧ','7').replace('ʈ','T.').replace('ɖ','D.').replace('ʂ','S.')
             .replace('ž','j').replace('ɣ','gh'))

def clean(toks):
    return [t for t in toks if len(t) > 1 and t not in JUNK
            and any(v in t.lower() for v in 'aeiouáíúāīū')]

def book_tables():
    """[(page, class, gloss, perfect3ms, imperfect3ms)] for every conjugation table."""
    r = PdfReader(PDF)
    out = []
    for i in range(len(r.pages)):
        lines = [l.strip() for l in (r.pages[i].extract_text() or '').split('\n')]
        if len(lines) < 2: continue
        m = re.match(r'^(\d+)\s+(.+?)\s+to\s+(.+)$', lines[1].strip())
        if not m: continue
        cls, gloss = m.group(2).strip(), strip_ar(m.group(3)).strip()
        p3 = i3 = None
        for l in lines:
            raw = strip_ar(l).split()
            if raw[:1] == ['húwwa']:
                v = clean(raw[1:])
                if len(v) >= 2: p3, i3 = canon(v[0]), canon(v[1])
                break
        if p3 and i3:
            out.append((i + 1, cls, gloss, p3, i3))
    return out

def main():
    if not os.path.exists(PDF):
        print('reference PDF not on disk — nothing to compare.'); return 1
    src = open(os.path.join(ROOT, 'app', 'data', 'verbs.js'), encoding='utf-8').read()
    verbs = json.loads(src[src.index('{'): src.rindex(';')])['verbs']

    # The two sources write a word-initial glottal onset differently — the book prints
    # ista3mal / it3allam / i7marr, we print 2ista3mal / t3allam / 2i7marr. Same words,
    # different convention, and comparing them raw reports nine "disagreements" that are
    # purely orthographic. Normalize the onset away so only real vowel differences surface.
    def key(s):
        s = str(s or '')
        if s.startswith('2'): s = s[1:]
        if s.startswith('i') and len(s) > 2: s = s[1:]
        return s

    by_past = {}
    for v in verbs:
        by_past.setdefault(key((v.get('past') or {}).get('caphi')), []).append(v)

    tables = book_tables()
    agree, missing, disagree = 0, [], []
    for pg, cls, gloss, p3, i3 in tables:
        if key(p3) in by_past:
            agree += 1
            continue
        # Same imperfect, different perfect = the two sources vowel the perfect differently.
        cand = [v for v in verbs if key((v.get('pres') or {}).get('caphi')) == key(i3)]
        if cand:
            disagree.append((pg, gloss, p3, i3, cand[0]))
        else:
            missing.append((pg, gloss, p3, i3))

    print(f'grammar tables read: {len(tables)}')
    print(f'  principal parts already identical : {agree}')
    print(f'  DISAGREE on the perfect           : {len(disagree)}')
    print(f'  verb not in our 1000              : {len(missing)}\n')
    if disagree:
        print('DISAGREEMENTS — book vs app (each needs a human call):')
        for pg, gloss, p3, i3, v in disagree:
            print(f'  p{pg:<4} {gloss[:26]:26} book={p3:12}/{i3:12}  '
                  f'app={v["past"]["caphi"]:12}/{v["pres"]["caphi"]:12}  {v["lemma"]}  root={v["root"]}')
    if missing:
        print(f'\nnot in our verb list (first 15 of {len(missing)}):')
        for pg, gloss, p3, i3 in missing[:15]:
            print(f'  p{pg:<4} {gloss[:26]:26} {p3}/{i3}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
