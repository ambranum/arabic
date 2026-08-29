#!/usr/bin/env python3
"""Hebrew verb paradigms -> app/data/he/verbs.js + verbs-conj-*.js.

The linguistics live in spike/he/, and this imports them rather than copying them: that is
where Stage A's verification harnesses are (verify_verbs.py, verify_phon.py), and a transducer
separated from the tests that measure it is a transducer nobody can trust. This module is the
thin part -- take what verbs_he.paradigms() extracts and write it in the shape app.js reads.

Hebrew inverts the Arabic problem. Maknuune gives principal parts and pipeline/conjugate.py has
to DERIVE thirty cells from three; Wiktionary gives Hebrew's tables already filled in and
pointed, so the paradigms are LOOKED UP, which is the project's rule applied more strictly than
the Arabic side manages. A3 measured them at 98.99% against Wiktionary's own romanization of
the 3ms past -- the cell a card is banked under.

    curl -L https://kaikki.org/dictionary/Hebrew/kaikki.org-dictionary-Hebrew.jsonl \
        -o spike/he/kaikki-hebrew.jsonl        # 57 MB, gitignored, regenerable
    python3 pipeline/he_verbs.py --lang he
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
import split          # noqa: E402
import verbs_he       # noqa: E402

# Binyan -> how hard, for the study plan's verb walk. The plan flagged this: Arabic difficulty
# tracks the weak class, Hebrew's tracks the binyan at least as much as the gzara, which is why
# LANG.verb.tier is a function per pack rather than a shared table.
TIER = {'paal': 1, 'nifal': 2, 'piel': 2, 'hifil': 2, 'hitpael': 3, 'pual': 3, 'hufal': 3}


def _pp(cell):
    """A principal part in the app's shape: the pointed form plus its pronunciation."""
    if not cell:
        return None
    return {'ar': cell.get('arv') or cell['ar'], 'caphi': cell.get('ph') or ''}


def build():
    out = []
    for v in verbs_he.paradigms():
        conj = {k: {'ar': c['ar'], 'arv': c['arv'], 'ph': c['ph']} for k, c in v['conj'].items()}
        rec = {
            'lemma': v['lemma'],
            'root': v['root'] or '',
            'gloss': (v['gloss'] or '').strip(),
            'form': v['form'] or '',                 # the binyan; `form` is the app's class field
            'weak': v['form'] or '',                 # Hebrew has no separate weak axis yet
            'core': False,
            'src': 'wiktionary',
            'past': _pp(v.get('past')),
            'pres': _pp(v.get('pres')),
            'imp': _pp(v['conj'].get('imp|ata')),
            'inf': _pp(v.get('inf')),
        }
        if conj:
            rec['conj'] = conj
        out.append(rec)
    # Deterministic order, so a rebuild does not reshuffle the verb list under anyone's plan.
    out.sort(key=lambda r: (TIER.get(r['form'], 4), r['gloss'].lower(), r['lemma']))
    return {'verbs': out}


def main():
    data = build()
    vs = data['verbs']
    sizes = split.write_verbs(data, note='pipeline/he_verbs.py')
    withc = sum(1 for v in vs if v.get('conj'))
    print('verbs: %d   with a paradigm: %d' % (len(vs), withc))
    import collections
    for b, n in collections.Counter(v['form'] or '(none)' for v in vs).most_common():
        print('  %-10s %5d' % (b, n))
    print('\n-> %s  (%d KB index + %d paradigm files)'
          % (os.path.relpath(paths.data('verbs.js'), paths.ROOT),
             sizes['verbs.js'] // 1024, sizes['_chunks']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
