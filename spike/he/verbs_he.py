#!/usr/bin/env python3
"""Hebrew verb paradigms out of the Wiktionary dump, in the app's `conj` record shape.

A1 turned up something that changes what A3 should be. Wiktionary does not just give Hebrew
lemmas -- it gives whole POINTED conjugation tables: every person of the past and future, all
four present participles, the imperative, the infinitive, plus the binyan and often the root.

For Arabic there was no choice about this. Maknuune has principal parts and nothing else, so
pipeline/conjugate.py had to derive 30 cells per verb from three, and the whole apparatus of
per-measure engines and parse gates exists to make that derivation trustworthy. Hebrew arrives
with the tables already filled in, from a source we can ship.

So the order is inverted, and it is the right way round for this project's rule: LOOK UP first,
derive only what is missing. This module does the looking up. `conjugate_he.py` handles the
gaps, and is verified against what this produces.

Slot keys match the Arabic convention (`section|person`) so one renderer serves both:

    past|ani past|ata past|at past|hu past|hi past|anaxnu past|atem past|hem
    pres|ms pres|fs pres|mp pres|fp
    fut|ani fut|ata fut|at fut|hu fut|hi fut|anaxnu fut|atem fut|hem
    imp|ata imp|at imp|atem      inf|-

    python3 spike/he/verbs_he.py            # completeness report
    python3 spike/he/verbs_he.py לכתוב      # one paradigm
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lex import binyan_of, he_norm                          # noqa: E402
from phon import phon                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, 'kaikki-hebrew.jsonl')
NIQQUD_RE = re.compile('[֑-ׇ]')

PAST = ['ani', 'ata', 'at', 'hu', 'hi', 'anaxnu', 'atem', 'hem']
PRES = ['ms', 'fs', 'mp', 'fp']
IMP = ['ata', 'at', 'atem']
SLOTS = (['past|' + p for p in PAST] + ['pres|' + p for p in PRES]
         + ['fut|' + p for p in PAST] + ['imp|' + p for p in IMP] + ['inf|-'])


def _slot(tags):
    """Wiktionary's tag bag -> our slot key, or None if this form isn't a paradigm cell.

    The tags are a set, not a tuple, so a form shared by both genders carries BOTH gender tags
    -- 'feminine first-person masculine past singular' is the 1sg, common gender. Reading
    gender as "masculine unless feminine says otherwise" would mislabel every common cell, so
    both-or-neither is treated explicitly as common.
    """
    t = set(tags)
    if 'participle' in t or 'passive' in t or 'noun-from-verb' in t:
        return None
    m, f = 'masculine' in t, 'feminine' in t
    gen = 'm' if (m and not f) else 'f' if (f and not m) else 'c'
    plural = 'plural' in t
    person = ('1' if 'first-person' in t else '2' if 'second-person' in t
              else '3' if 'third-person' in t else None)

    if 'present' in t:
        if person and person != '3':
            return None
        return 'pres|' + (('mp' if gen != 'f' else 'fp') if plural
                          else ('fs' if gen == 'f' else 'ms'))
    if 'imperative' in t:
        return 'imp|' + ('atem' if plural else ('at' if gen == 'f' else 'ata'))
    if 'infinitive' in t:
        return 'inf|-'
    sec = 'past' if 'past' in t else 'fut' if 'future' in t else None
    if not sec or not person:
        return None
    if person == '1':
        return '%s|%s' % (sec, 'anaxnu' if plural else 'ani')
    if person == '2':
        return '%s|%s' % (sec, ('atem' if plural else ('at' if gen == 'f' else 'ata')))
    return '%s|%s' % (sec, 'hem' if plural else ('hi' if gen == 'f' else 'hu'))


def paradigms():
    """-> list of verb records in the app's shape."""
    out = []
    for line in open(DUMP, encoding='utf-8'):
        d = json.loads(line)
        if d.get('pos') != 'verb':
            continue
        ht = (d.get('head_templates') or [{}])[0].get('args', {})
        lemma = ht.get('wv') or next(
            (f['form'] for f in d.get('forms', []) if 'canonical' in (f.get('tags') or [])), None)
        gloss = next((s['glosses'][0] for s in d.get('senses', []) if s.get('glosses')), '')
        if not lemma or not gloss:
            continue
        conj = {}
        for f in d.get('forms', []):
            tags = f.get('tags') or []
            form = (f.get('form') or '').strip()
            if not form or not NIQQUD_RE.search(form):
                continue                     # pointed cells only; the bare ones are duplicates
            k = _slot(tags)
            # wiktextract cannot label the Hebrew infinitive and files it as
            # `error-unrecognized-form` -- 2,671 rows of it. It is unmistakable in the data
            # (pointed, tagged as the error, and beginning with the ל- prefix), and dropping it
            # would leave every paradigm one cell short of complete.
            if not k and 'error-unrecognized-form' in tags and form.startswith('ל'):
                k = 'inf|-'
            if k and k not in conj:
                conj[k] = {'ar': NIQQUD_RE.sub('', form), 'arv': form, 'ph': phon(form, verb=True)}
        if not conj:
            continue
        out.append({
            'lemma': lemma, 'lemma_search': he_norm(lemma), 'gloss': gloss,
            'form': binyan_of(d),
            'root': '.'.join(x for x in (ht.get('פ'), ht.get('ע'), ht.get('ל')) if x),
            'past': conj.get('past|hu'), 'pres': conj.get('pres|ms'),
            'fut': conj.get('fut|hu'), 'inf': conj.get('inf|-'),
            'conj': conj,
        })
    return out


def main():
    if len(sys.argv) > 1:
        q = he_norm(sys.argv[1])
        for v in paradigms():
            if v['lemma_search'] == q or he_norm((v.get('inf') or {}).get('ar', '')) == q:
                print('%s  %s  [%s]  root %s' % (v['lemma'], v['gloss'][:40],
                                                 v['form'] or '?', v['root'] or '?'))
                for k in SLOTS:
                    c = v['conj'].get(k)
                    print('  %-12s %-14s %s' % (k, c['arv'] if c else '—', c['ph'] if c else ''))
                return 0
        print('not found'); return 1

    vs = paradigms()
    import collections
    by_binyan = collections.Counter(v['form'] or '(none)' for v in vs)
    filled = collections.Counter()
    complete = 0
    for v in vs:
        n = len(v['conj'])
        filled[n] += 1
        if all(k in v['conj'] for k in SLOTS):
            complete += 1
    print('verb entries with any pointed cell: %d' % len(vs))
    print('with ALL %d slots filled          : %d  (%.0f%%)'
          % (len(SLOTS), complete, 100.0 * complete / max(len(vs), 1)))
    for lo, hi, label in ((20, 24, '20-24 slots'), (12, 19, '12-19'), (1, 11, '1-11')):
        c = sum(v for k, v in filled.items() if lo <= k <= hi)
        print('  %-12s %d' % (label, c))
    print('\nby binyan:')
    for b, c in by_binyan.most_common():
        print('  %-10s %5d' % (b, c))
    print('\nper-slot fill rate:')
    for k in SLOTS:
        c = sum(1 for v in vs if k in v['conj'])
        print('  %-12s %5d  %3.0f%%' % (k, c, 100.0 * c / max(len(vs), 1)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
