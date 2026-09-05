"""Which corpus surfaces would a proposed curated KEY capture? -> the shadowing risk, per key.

Cheaper than the full before/after diff and answers the question that keeps coming up while
choosing a spelling for a name: is this one reachable from a real word? A key is reachable when
lex.morph(surface) produces its normalised form as a stem, which is exactly the path
ingest.annotate_word takes through curated.lookup.
"""
import sys, re, collections
sys.path.insert(0, 'pipeline')
import curated
from maknuune import Lexicon

lex = Lexicon()
src = open('app/data/ar/corpus.js', encoding='utf-8').read()
counts = collections.Counter(re.findall(r'[ء-ي]{2,}', src))
keys = {curated._norm(k): k for k in sys.argv[1:]}
hits = collections.defaultdict(list)
for surface, n in counts.items():
    if curated._norm(surface) in keys:
        continue                      # the key itself, not a collision
    for st in lex.morph(surface)[0][1:]:
        if st in keys:
            hits[keys[st]].append((surface, n))
            break
for k in sys.argv[1:]:
    h = sorted(hits.get(k, []), key=lambda x: -x[1])
    tot = sum(n for _, n in h)
    print('%-14s %s' % (k, 'CLEAN' if not h else '%d tokens: %s' %
          (tot, ', '.join('%s(%d)' % (s, n) for s, n in h[:8]))))
