"""The ambiguous queue, commonest first, with the candidates and one real context each."""
import sys, re, json, glob, collections
sys.path.insert(0, 'pipeline')
import ingest
from maknuune import Lexicon

N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
START = int(sys.argv[2]) if len(sys.argv) > 2 else 0
lex, res = Lexicon(), ingest.load_resolutions()

counts = collections.Counter()
ctx = {}
for f in sorted(glob.glob('texts/ar/*.json')):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    for s in d.get('sentences', []):
        for t in ingest.tokenize(s['ar']):
            a = ingest.annotate_word(lex, t, res)
            if a['provenance'].startswith('AMBIGUOUS'):
                counts[t] += 1
                ctx.setdefault(t, (s['ar'], s.get('en', '')))

print('%d distinct, %d tokens\n' % (len(counts), sum(counts.values())))
for i, (w, n) in enumerate(counts.most_common()[START:START + N], START + 1):
    cands = lex.candidates(w)
    cands.sort(key=lambda c: str(c.get('SOURCE')) not in ('nan', 'None', ''))
    print('%3d. %-12s %3d  %s' % (i, w, n, ctx[w][0][:66]))
    print('              %s' % ctx[w][1][:74])
    for c in cands[:6]:
        print('       %-7s %-13s %-30s %s' % (c['ID'], str(c.get('LEMMA', ''))[:13],
              str(c.get('GLOSS'))[:30], str(c.get('ANALYSIS'))[:16]))
    print()
