#!/usr/bin/env python3
"""Adjudicate ambiguous Hebrew words -> pipeline/resolutions.he.json (the audit trail).

The Hebrew counterpart of resolve_helper.py, and it never invents: it picks among the readings
the morphology ALREADY allows for that surface, by matching a hint against "GLOSS:ANALYSIS".
If the hint matches no candidate, or matches more than one, nothing is written and it says so.

Two scopes, because a homograph's reading is a property of the CONTEXT and not of the corpus.

    python3 pipeline/he_resolve.py --lang he "מפה=map"            # everywhere
    python3 pipeline/he_resolve.py --lang he --in book-juha- "חמור=donkey"

חמור is the case that forced this. In the daily paper it is חָמוּר "serious"; in forty pages of
Juha it is חֲמוֹר, the donkey, in almost every tale. One global answer has to be wrong for one
of them, and the wrong one was showing on the first sentence of the first book. A scoped line
says which text it speaks for, and the file still names a REAL lexicon id either way.

    python3 pipeline/he_resolve.py --lang he --show חמור         # what are the candidates?
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths                                          # noqa: E402
paths.require('he')
from build_lex import he_norm                         # noqa: E402
from lex import Lexicon                               # noqa: E402

RES = paths.resolutions()
SCOPED = '@texts'          # reserved key: id-prefix -> {surface: lexicon id}


def candidates(lex, surface):
    recs, _prov, _cut = lex.look(surface)
    return lex.readings(recs) if recs else []


def describe(c):
    return '%-9s %-14s %-12s %s' % (c['ID'], c['LEMMA'], c['ANALYSIS'], str(c['GLOSS'])[:60])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('picks', nargs='*', help='<surface>=<hint matched against GLOSS:ANALYSIS>')
    ap.add_argument('--in', dest='scope', help='apply only to texts whose id starts with this')
    ap.add_argument('--show', help='print every reading of one surface and exit')
    ap.add_argument('--find', help='print lexicon rows whose LEMMA equals this, and exit')
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()

    lex = Lexicon()
    if a.show:
        for c in candidates(lex, a.show):
            print(describe(c))
        return 0
    if a.find:
        seen = set()
        for rows in lex.by_form.values():
            for r in rows:
                if str(r['LEMMA']) == a.find and str(r['ID']) not in seen:
                    seen.add(str(r['ID']))
                    print(describe(r))
        return 0

    res = json.load(open(RES, encoding='utf-8')) if os.path.exists(RES) else {}
    target = res
    if a.scope:
        target = res.setdefault(SCOPED, {}).setdefault(a.scope, {})
    changed = 0
    for p in a.picks:
        surface, hint = p.split('=', 1)
        cands = candidates(lex, surface)
        # Two readings of one word can carry the SAME gloss and differ only in their pointing --
        # אוֹתוֹ and אוֹתָהּ are both "The same." in Wiktionary, and the wrong one was being shown
        # for both אותו and אותה. When no hint can separate them, name the id.
        if hint.startswith('#'):
            # An id names a row directly, and it does NOT have to be one look() offered. The
            # clitic peeler can miss the reading a human can see -- והיא peels to יָא, the
            # vocative particle, when it is plainly ו + הִיא -- and he_ingest applies a trail
            # line by id and then asks cut_for whether it spells the word. That check below is
            # the real guard, so the candidate list is not one here.
            row = lex.by_id.get(hint[1:])
            hits = [row] if row is not None else []
        else:
            hits = [c for c in cands
                    if hint.lower() in ('%s:%s' % (c['GLOSS'], c['ANALYSIS'])).lower()]
        if not hits:
            print('!! %s: no reading matches %r — %d candidates:' % (surface, hint, len(cands)))
            for c in cands[:8]:
                print('     ' + describe(c))
            continue
        # More than one hit is not a tie to break by order: the hint was not specific enough,
        # and picking the first would put an arbitrary reading in a file whose whole job is to
        # record a decision someone made.
        if len(hits) > 1:
            print('!! %s: %r matches %d readings — be more specific:' % (surface, hint, len(hits)))
            for c in hits[:8]:
                print('     ' + describe(c))
            continue
        pick = hits[0]
        # The same check he_ingest makes before applying a trail line: this id must be a
        # reading of THIS surface, spelled the way the page spells it.
        if lex.cut_for(he_norm(surface), pick) is None:
            print('!! %s: %s is not a reading of this surface — not written' % (surface, pick['ID']))
            continue
        target[surface] = str(pick['ID'])
        print('%s%-12s -> %s' % ('[%s] ' % a.scope if a.scope else '', surface, describe(pick)))
        changed += 1

    if changed:
        json.dump(res, open(RES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1,
                  sort_keys=True)
        print('\nwrote %d to %s' % (changed, os.path.relpath(RES, paths.ROOT)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
