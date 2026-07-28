#!/usr/bin/env python3
"""Add resolutions for ambiguous words, choosing a real Maknuune entry by a gloss/analysis
hint. Never invents — it picks among the candidates the morphology already allows, and
writes the chosen Maknuune ID to pipeline/resolutions.json (the audit trail).

Usage: python3 pipeline/resolve_helper.py  "بشرب=drink:VERB"  "بروح=go:VERB"  ...
Each arg is  <surface>=<needle>  where <needle> is a substring to match in
"GLOSS:ANALYSIS" (case-insensitive). Prints what it picked; only writes on a clean match.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maknuune import Lexicon, norm

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RES = os.path.join(ROOT, 'pipeline', 'resolutions.json')

def main(args):
    lex = Lexicon()
    res = json.load(open(RES, encoding='utf-8'))
    changed = 0
    for a in args:
        surface, needle = a.split('=', 1)
        needle = needle.lower()
        cands = lex.candidates(surface)
        cands.sort(key=lambda c: str(c.get('SOURCE')) not in ('nan', 'None', ''))
        hits = [c for c in cands
                if needle in (str(c.get('GLOSS')) + ':' + str(c.get('ANALYSIS'))).lower()]
        if not hits:
            print('  NO MATCH  %-12s needle=%r  (cands: %s)' % (
                surface, needle, ', '.join(str(c.get('GLOSS'))[:14] for c in cands[:4])))
            continue
        pick = hits[0]
        res[surface] = str(pick['ID'])
        changed += 1
        print('  OK  %-12s -> %s  %s [%s]' % (
            surface, pick['ID'], str(pick['GLOSS'])[:32], str(pick['ANALYSIS'])[:14]))
    if changed:
        json.dump(res, open(RES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote %d resolution(s)' % changed)

if __name__ == '__main__':
    main(sys.argv[1:])
