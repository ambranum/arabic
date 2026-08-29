#!/usr/bin/env python3
"""Is the precomputed lexicon the SAME index the app used to build at runtime?

lexicon.js exists so the word lookup stops costing 7.3 MB. That is only safe if it answers
identically -- a normalization or ranking rule that drifts from app/app.js does not fail, it
just quietly resolves some words to a different entry, and nobody finds out.

So this rebuilds the index the old way, by walking every sentence in corpus.js exactly as
lexIndex() did, and compares it key for key against the shipped file. Not a spot check: every
lemma key, every surface key, and for each one every field of the record it points at.

    python3 pipeline/verify_lexindex.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lexindex  # noqa: E402
import paths  # noqa: E402


def _load(path, marker, close=';'):
    s = open(path, encoding='utf-8').read()
    return json.loads(s[s.index(marker) + len(marker): s.rindex(close)])


def main():
    corpus = _load(paths.data('corpus.js'), 'Object.assign(window.CORPUS,', ')')
    library = _load(paths.data('library.js'), 'window.LIBRARY = ')
    shipped = _load(paths.data('lexicon.js'), 'window.LEXICON = ')

    # The app iterates LIB.texts and reads each one's sentences out of CORPUS, so reproduce that
    # order rather than the dict's -- ties between equal-ranked records go to whichever came first.
    texts = [{'id': t['id'], 'sentences': corpus.get(t['id'], [])} for t in library['texts']]

    want = lexindex.build(texts)
    fields = shipped['f']
    if fields != want['f']:
        print('FIELD LIST DIFFERS'); return 1

    bad = 0
    for side, name in (('k', 'lemma'), ('s', 'surface')):
        a, b = want[side], shipped[side]
        missing = set(a) - set(b)
        extra = set(b) - set(a)
        print('%-8s keys  walked %6d   shipped %6d   missing %d   extra %d'
              % (name, len(a), len(b), len(missing), len(extra)))
        bad += len(missing) + len(extra)
        for k in sorted(set(a) & set(b)):
            ra, rb = want['r'][a[k]], shipped['r'][b[k]]
            if ra != rb:
                bad += 1
                if bad < 6:
                    diff = [(f, x, y) for f, x, y in zip(fields, ra, rb) if x != y]
                    print('   %-14s differs: %s' % (k, diff[:3]))

    tokens = sum(len(s.get('words', [])) for t in texts for s in t['sentences'])
    print('\n%d word tokens walked -> %d distinct records' % (tokens, len(shipped['r'])))
    cor = os.path.getsize(paths.data('corpus.js'))
    lex = os.path.getsize(paths.data('lexicon.js'))
    print('corpus.js %d KB  ->  lexicon.js %d KB  (%.1fx smaller)'
          % (cor // 1024, lex // 1024, cor / max(lex, 1)))
    print('\n%s' % ('MISMATCHES: %d' % bad if bad else
                    'identical — the precomputed index answers exactly as the corpus walk did'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
