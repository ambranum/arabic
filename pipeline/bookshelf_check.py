#!/usr/bin/env python3
"""Is this book actually the level it claims? — an advisory report, never a gate.

Grading in this project is a LABEL: book_<id>.py declares level='beginner' and nothing checks it.
For the middle of the shelf that was harmless. For a book tagged "Beginner · A1 · Phase 1" it is a
promise to someone who cannot yet read their way out of a mistake, so this measures the prose
against the content already shipped and prints what it finds.

Read it while writing. A number outside the peer range is a prompt to rewrite a few sentences, not
an error — this script always exits 0 and never blocks a build.

WHICH NUMBERS TO TRUST, measured across the current corpus:

    sentence length  beginner stories 24 chars · advanced 34 · the existing book 50
    vocabulary rate  beginner stories 23.5% outside the corpus' top-500 lemmas · advanced 21.3%

Sentence length separates levels cleanly. The vocabulary rate barely does — 30 short stories on 30
topics each bring their own nouns, so a low-level text can score "hard" purely for being varied.
Weight length heavily, treat vocabulary as a hint, and look hardest at the new-lemmas curve.

Needs the book INGESTED first (no --audio, costs nothing) — it reads per-word lemmas out of
build/<id>/text.json, which is where the Maknuune lookup lands.

Run:
    python3 pipeline/bookshelf_check.py                 # every book
    python3 pipeline/bookshelf_check.py juha aesop      # named books
    python3 pipeline/bookshelf_check.py --estimate      # + the ElevenLabs bill per book
"""
import json, os, glob, argparse
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BUILD = os.path.join(ROOT, 'build')
TOP_N = 500                      # the frequency band "known words" is measured against
CREDITS_PER_CHAR = 1.0           # eleven_multilingual_v2; flash is half


def load(kind=None, book=None, level=None):
    """Every annotated text matching the filters, straight out of build/."""
    out = []
    for f in glob.glob(os.path.join(BUILD, '*', 'text.json')):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if kind and d.get('kind') != kind: continue
        if book and d.get('book') != book: continue
        if level and d.get('level') != level: continue
        out.append(d)
    return out


def words(texts):
    return [w for d in texts for s in d['sentences'] for w in s['words']]


def corpus_top(exclude_book=None):
    """The TOP_N most frequent lemmas across the corpus, excluding the book being judged —
    a long book would otherwise inflate its own reference set and grade itself easy."""
    freq = Counter()
    for d in load():
        if d.get('kind') not in ('story', 'news', 'book-chapter'): continue
        if exclude_book and d.get('book') == exclude_book: continue
        for w in words([d]):
            if w.get('lemma'): freq[w['lemma']] += 1
    return {l for l, _ in freq.most_common(TOP_N)}


def pct(n, d):
    return 0.0 if not d else round(n / d * 100, 1)


def measure(texts, top):
    """The numbers, for a book or for a peer group."""
    ws = words(texts)
    lem = [w['lemma'] for w in ws if w.get('lemma')]
    sents = [s for d in texts for s in d['sentences']]
    chars = sorted(len(s['ar']) for s in sents)
    wds = sorted(len(s['ar'].split()) for s in sents)
    p = lambda a, q: a[min(len(a) - 1, int(len(a) * q))] if a else 0
    return {
        'texts': len(texts), 'sentences': len(sents), 'tokens': len(ws),
        'chars_total': sum(chars),
        'len_mean': round(sum(chars) / len(chars), 1) if chars else 0,
        'len_p50': p(chars, .5), 'len_p90': p(chars, .9), 'len_max': chars[-1] if chars else 0,
        'w_mean': round(sum(wds) / len(wds), 1) if wds else 0, 'w_max': wds[-1] if wds else 0,
        'outside': pct(sum(1 for l in lem if l not in top), len(lem)),
        'ttr': pct(len(set(lem)), len(lem)),                       # type/token: lower = more reuse
        'nolemma': pct(sum(1 for w in ws if not w.get('lemma')), len(ws)),
        'ambig': pct(sum(1 for w in ws if str(w.get('provenance', '')).startswith('AMBIGUOUS')), len(ws)),
    }


def new_lemma_curve(texts):
    """Distinct lemmas each chapter introduces. Front-loaded is healthy — a flat line means every
    chapter is a fresh hit of vocabulary and nothing is being reinforced."""
    seen, curve = set(), []
    for d in sorted(texts, key=lambda d: d.get('chapter') or 0):
        fresh = {w['lemma'] for w in words([d]) if w.get('lemma')} - seen
        seen |= fresh
        curve.append(len(fresh))
    return curve


def spark(curve):
    if not curve: return ''
    hi = max(curve) or 1
    bars = '▁▂▃▄▅▆▇█'
    return ''.join(bars[min(len(bars) - 1, int(n / hi * (len(bars) - 1)))] for n in curve)


def cmp_line(label, val, peer, unit='', lower_is_simpler=True, tol=0.15):
    """One metric against its peer baseline, with a plain verdict."""
    if peer in (None, 0):
        return '    %-34s %7s%s' % (label, val, unit)
    d = (val - peer) / peer
    over = d > tol if lower_is_simpler else d < -tol
    flag = 'HARDER than its level' if over else ('in range' if abs(d) <= tol else 'easier than its level')
    return '    %-34s %7s%s   peers %s%s   %s' % (label, val, unit, peer, unit, flag)


def report(book, estimate=False):
    texts = load(kind='book-chapter', book=book)
    if not texts:
        print('  no ingested chapters for %r — run the book script, then ingest\n' % book)
        return
    lvl = texts[0].get('level') or '?'
    title = (texts[0].get('book_title') or {}).get('en', book)
    top = corpus_top(exclude_book=book)
    me = measure(texts, top)
    peers = load(kind='story', level=lvl)
    pe = measure(peers, top) if peers else {}

    print('%s  %s' % (book.ljust(12), title))
    print('  declared %s · shelf %s · %d chapters · %d sentences · %d tokens'
          % (lvl, texts[0].get('shelf'), me['texts'], me['sentences'], me['tokens']))

    print('\n  sentence length — the signal that actually separates levels')
    print(cmp_line('mean characters', me['len_mean'], pe.get('len_mean')))
    print(cmp_line('90th percentile', me['len_p90'], pe.get('len_p90')))
    print(cmp_line('longest', me['len_max'], pe.get('len_max')))
    print(cmp_line('mean words', me['w_mean'], pe.get('w_mean')))

    print('\n  vocabulary — a hint, not a verdict (varied topics read as "hard")')
    print(cmp_line('outside the corpus top-%d' % TOP_N, me['outside'], pe.get('outside'), '%'))
    print(cmp_line('type/token ratio', me['ttr'], pe.get('ttr'), '%'))

    print('\n  what the lexicon could not settle')
    print('    %-34s %7s%%   these words show as unconfirmed in the app'
          % ('ambiguous word senses', me['ambig']))
    print('    %-34s %7s%%   no lexicon entry at all' % ('no lemma', me['nolemma']))

    curve = new_lemma_curve(texts)
    if curve:
        front = pct(sum(curve[:max(1, len(curve) // 4)]), sum(curve))
        peak, late = max(curve), sum(curve[len(curve) // 2:]) / max(1, len(curve) - len(curve) // 2)
        print('\n  new lemmas per chapter   %s' % spark(curve))
        print('    peak %d in one chapter · %.1f average in the second half' % (peak, late))
        # A novel with one cast SHOULD front-load. A collection of one-off casts cannot, and that
        # is not a defect — for those the number that matters is the peak, not the shape.
        print('    first quarter carries %s%% of the vocabulary   %s'
              % (front, 'front-loaded — a single cast, reused' if front >= 40
                 else 'even — a collection of separate casts; watch the peak, not the shape'))

    if estimate:
        # Only what is still MISSING. Quoting the whole book overstates the bill after a partial
        # run, which is the number you'd actually be deciding on.
        todo = [s for d in texts for s in d['sentences'] if not s.get('audio')]
        c = sum(len(s['ar']) for s in todo)
        have = me['sentences'] - len(todo)
        print('\n  audio: %d of %d sentences already voiced' % (have, me['sentences']))
        print('    remaining %d sentences ≈ %s credits (%s Arabic chars)'
              % (len(todo), format(int(c * CREDITS_PER_CHAR), ','), format(c, ',')) if todo
              else '    nothing to generate')
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('books', nargs='*', help='book ids; default every book on the shelf')
    ap.add_argument('--estimate', action='store_true', help='also print the ElevenLabs bill')
    a = ap.parse_args()

    ids = a.books or sorted({d['book'] for d in load(kind='book-chapter') if d.get('book')})
    if not ids:
        print('no ingested books found under build/')
        return 0
    print('\nGrading report — advisory only, nothing here blocks a build.')
    print('Peers are the SHORT STORIES at the same declared level.\n')
    for b in ids:
        report(b, a.estimate)
    return 0                      # always: this script reports, it does not judge


if __name__ == '__main__':
    raise SystemExit(main())
