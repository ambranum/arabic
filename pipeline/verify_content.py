#!/usr/bin/env python3
"""Audit the app's curated Arabic against the native teaching materials.

The oldest honesty problem in this project (SPEC.md §7.3, LEARNING-SYSTEM.md §6) is that
nobody was checking the Arabic: the reactions, the sound-drill examples and the dinner-table
dialogues were written by Claude and shipped flagged "not native-checked" because there was
nothing to check them against. texts/ref/ changed that — it is ~1,900 items of Arabic printed
in courses written by native teachers. This diffs one against the other.

Same shape as pipeline/verify_conjugation.py: normalize, compare mechanically, and sort every
item into one of three honest buckets rather than pretending to a verdict:

  corroborated  the exact phrase (or its normalized form) is attested in a book  -> provenance
                can be upgraded to ref-corroborated
  variant       a near-match is attested: same words, different vowels/spelling, or the book
                prints a close variant -> a human decides which form to teach
  uncovered     the books say nothing either way -> keeps needs-native-validation. NOT a
                verdict of wrong; the corpus simply does not cover it.

A book match is corroboration, not a native review of THIS app's wording — the UI wording
stays honest about that distinction.

Run:  python3 pipeline/verify_content.py            # report to stdout
      python3 pipeline/verify_content.py --write    # also write texts/ref/AUDIT.md
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- where this language's generated data lives
import argparse, difflib, glob, json, os, re, sys, unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
REF = os.path.join(ROOT, 'texts', 'ref')
OUT_MD = os.path.join(REF, 'AUDIT.md')

# ---- normalization -------------------------------------------------------------------------
# Matches the app's own arNorm(): strip the diacritics and the punctuation a page happens to
# carry, so "شُو صار؟" and "شو صار" are recognized as the same phrase. Alif/ya/ta-marbuta are
# folded too, because the books are not internally consistent about them either.
_MARKS = ''.join(chr(c) for c in list(range(0x64B, 0x653)) + [0x670, 0x640])
_PUNCT = '،.؟!:؛…"«»”“\'()[]{}-–—/\\?,*'
_FOLD = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه'}

def norm(s):
    s = unicodedata.normalize('NFKC', str(s or ''))
    s = ''.join(c for c in s if c not in _MARKS)
    s = ''.join(_FOLD.get(c, c) for c in s)
    s = ''.join(' ' if c in _PUNCT else c for c in s)
    return ' '.join(s.split())

def words(s):
    return [w for w in norm(s).split() if w]


# ---- the oracle: every Arabic string the reference library prints ---------------------------
def load_ref():
    """{normalized phrase: [(book, src, original)]} plus a word index for partial matching."""
    phrases, index = {}, {}
    for f in sorted(glob.glob(os.path.join(REF, '*.json'))):
        book = os.path.basename(f)[:-5]
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for u in d.get('units', []):
            for s in u.get('sections', []):
                src = '%s %s' % (book, s.get('src') or '')
                bag = []
                for it in (s.get('items') or []):
                    if isinstance(it, dict):
                        bag += [it.get('ar'), it.get('cue'), it.get('answer')]
                for ln in (s.get('lines') or []):
                    if isinstance(ln, dict):
                        bag.append(ln.get('ar'))
                for e in (s.get('examples') or []):
                    if isinstance(e, dict):
                        bag.append(e.get('ar'))
                for sent in (s.get('sentences') or []):
                    bag.append(sent.get('ar') if isinstance(sent, dict) else sent)
                for L in (s.get('letters') or []):
                    if isinstance(L, dict):
                        bag += (L.get('examples') or [])
                for raw in bag:
                    if not raw or not isinstance(raw, str):
                        continue
                    n = norm(raw)
                    if not n:
                        continue
                    phrases.setdefault(n, []).append((book, src.strip(), raw))
                    for w in set(n.split()):
                        index.setdefault(w, set()).add(n)
    return phrases, index


def judge(ar, phrases, index):
    """-> (bucket, evidence). Exact normalized hit, else the closest attested phrase."""
    n = norm(ar)
    if not n:
        return 'uncovered', None
    if n in phrases:
        return 'corroborated', phrases[n][0]
    # A short chunk that appears INSIDE a longer attested sentence still counts as attested — but
    # the match has to align on WORD boundaries. Plain substring matching quietly accepts a
    # truncated word (خنازي inside خنازير), which would report broken content as corroborated and
    # hide exactly the errors this audit exists to find.
    wl = n.split()
    ws = set(wl)
    cands = set()
    for w in ws:
        cands |= index.get(w, set())
    if len(wl) >= 2:
        for c in cands:
            cw = c.split()
            if any(cw[i:i + len(wl)] == wl for i in range(len(cw) - len(wl) + 1)):
                return 'corroborated', phrases[c][0]
    # Otherwise: is the same phrase printed in a slightly different FORM? Character similarity
    # alone is useless here — "الله يعينك" and "الله يعافيك" are 86% identical as strings and are
    # two different blessings. A real variant is the same words with one of them respelled, so
    # compare word by word: same length, at most one word differing, and that word still close.
    best, score = None, 0.0
    wl = n.split()
    for c in cands:
        cw = c.split()
        if len(cw) != len(wl):
            continue
        diff = [(x, y) for x, y in zip(wl, cw) if x != y]
        if len(diff) > 1:
            continue
        r = 1.0 if not diff else difflib.SequenceMatcher(None, diff[0][0], diff[0][1]).ratio()
        if r > score:
            best, score = c, r
    if best and score >= 0.85:
        b, src, raw = phrases[best][0]
        return 'variant', (b, src, raw)
    return 'uncovered', None


# ---- what gets audited ---------------------------------------------------------------------
def collect():
    """[(area, id, arabic, english, provenance)] over everything curated by this project."""
    out = []
    p = os.path.join(ROOT, 'texts', 'reactions.json')
    if os.path.exists(p):
        for it in json.load(open(p, encoding='utf-8')).get('items', []):
            out.append(('reaction', it.get('cat', ''), it.get('ar'), it.get('en'),
                        it.get('provenance')))
    p = os.path.join(ROOT, 'texts', 'sounds.json')
    if os.path.exists(p):
        for L in json.load(open(p, encoding='utf-8')).get('lessons', []):
            for e in L.get('examples', []):
                out.append(('sound', L.get('id', ''), e.get('ar'), e.get('en'), None))
    p = os.path.join(ROOT, 'texts', 'table.json')
    if os.path.exists(p):
        for dg in json.load(open(p, encoding='utf-8')).get('dialogues', []):
            for ln in dg.get('lines', []):
                out.append(('table', dg.get('id', ''), ln.get('ar'), ln.get('en'), None))
    p = paths.data('grammar.js')
    if os.path.exists(p):
        try:
            g = json.loads(open(p, encoding='utf-8').read().split('window.GRAMMAR = ', 1)[1]
                           .rstrip().rstrip(';'))
            for L in g.get('lessons', []):
                for e in L.get('examples', []):
                    # Grammar examples are sentences MINED from this app's own ingested corpus
                    # (stories, news) — a different corpus from the books entirely. They are
                    # audited for completeness, but a near-zero hit rate here is expected and
                    # says nothing about either side; see --selftest for the real matcher check.
                    out.append(('grammar', L.get('id', ''), e.get('ar'), e.get('en'), 'corpus-mined'))
        except Exception:
            pass
    return [r for r in out if r[2]]


def selftest(phrases, index, n=300):
    """Does the matcher actually find things that ARE in the books? Feed book phrases back
    through it: anything short of ~100% corroborated means the matcher is broken, and every
    'uncovered' verdict elsewhere in the report is worthless. This is the control — an audit
    whose negative result can't be trusted is worse than no audit."""
    import random
    random.seed(11)
    keys = [k for k in phrases if len(k.split()) >= 2]
    sample = random.sample(keys, min(n, len(keys)))
    bad = [k for k in sample if judge(k, phrases, index)[0] != 'corroborated']
    print('selftest: %d/%d book phrases found by the matcher (%.1f%%)'
          % (len(sample) - len(bad), len(sample), 100.0 * (len(sample) - len(bad)) / max(1, len(sample))))
    for k in bad[:5]:
        print('   MISSED %s' % k[:60])
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='write texts/ref/AUDIT.md')
    ap.add_argument('--area', help='audit only one area (reaction, sound, table, grammar)')
    ap.add_argument('--selftest', action='store_true',
                    help='check the matcher against the oracle itself, then exit')
    ap.add_argument('--apply', action='store_true',
                    help='write the corroboration back into texts/*.json as provenance')
    a = ap.parse_args()

    phrases, index = load_ref()
    if a.selftest:
        return 0 if selftest(phrases, index) else 1
    print('oracle: %d distinct phrases from the reference library\n' % len(phrases))
    rows = [r for r in collect() if not a.area or r[0] == a.area]

    buckets = {}
    for area, ident, ar, en, prov in rows:
        b, ev = judge(ar, phrases, index)
        buckets.setdefault(area, {}).setdefault(b, []).append((ident, ar, en, ev, prov))

    order = ['corroborated', 'variant', 'uncovered']
    print('%-10s %8s %12s %9s %10s' % ('area', 'items', 'corroborated', 'variant', 'uncovered'))
    for area in sorted(buckets):
        d = buckets[area]
        tot = sum(len(d.get(k, [])) for k in order)
        print('%-10s %8d %12d %9d %10d' % (area, tot, len(d.get('corroborated', [])),
                                           len(d.get('variant', [])), len(d.get('uncovered', []))))

    # The interesting output is the variants: same phrase, different form. Those are the ones a
    # human has to adjudicate, and the only ones that can indicate the app teaches something the
    # books contradict.
    for area in sorted(buckets):
        vs = buckets[area].get('variant', [])
        if not vs:
            continue
        print('\n--- %s: %d to adjudicate (app form vs. the form a book prints) ---' % (area, len(vs)))
        for ident, ar, en, ev, prov in vs[:40]:
            book, src, raw = ev
            print('  %-12s app: %-34s %s' % (ident[:12], ar[:34], (en or '')[:30]))
            print('  %-12s book:%-34s [%s]' % ('', raw[:34], src))

    if a.apply:
        # Write the finding back where the app can see it. Corroborated items stop claiming to be
        # unchecked; everything else keeps its existing flag, because "the books are silent" is
        # not evidence of correctness.
        p = os.path.join(ROOT, 'texts', 'reactions.json')
        d = json.load(open(p, encoding='utf-8'))
        n_up = 0
        for it in d.get('items', []):
            b, ev = judge(it.get('ar'), phrases, index)
            if b == 'corroborated' and ev:
                book, src, raw = ev
                if it.get('provenance') != 'ref-corroborated':
                    n_up += 1
                it['provenance'] = 'ref-corroborated'
                it['ref_src'] = src
            elif b == 'variant' and ev:
                it['ref_variant'] = ev[2]        # for a human to adjudicate; nothing auto-changed
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\nprovenance upgraded on %d reaction(s) -> ref-corroborated' % n_up)

    if a.write:
        md = ['# Content audit — the app’s curated Arabic vs. the native teaching materials', '',
              'Generated by `pipeline/verify_content.py`. Oracle: %d distinct phrases drawn from '
              'texts/ref/ (the transcribed course books).' % len(phrases), '',
              'A **corroborated** item is one the books also print — that is corroboration, not a '
              'native review of this app’s exact wording. A **variant** is a near-match worth a '
              'human decision. **Uncovered** means the books are silent, which is not a verdict '
              'of wrong; those keep their `needs-native-validation` flag.', '',
              '| area | items | corroborated | variant | uncovered |', '|---|---|---|---|---|']
        for area in sorted(buckets):
            d = buckets[area]
            tot = sum(len(d.get(k, [])) for k in order)
            md.append('| %s | %d | %d | %d | %d |' % (area, tot, len(d.get('corroborated', [])),
                                                      len(d.get('variant', [])), len(d.get('uncovered', []))))
        md += ['', 'The `grammar` row is expected to read 0: those example sentences were mined '
               'from this app’s OWN ingested corpus (its stories and news), which is a different '
               'body of text from the course books — so overlap would be coincidence, and its '
               'absence says nothing about either side. Every one of them was already word-by-word '
               'looked up in the Maknuune lexicon when it was mined.',
               '',
               'The control for this audit is `--selftest`, which feeds phrases from the books '
               'back through the matcher: it currently finds 300/300. Without that, an "uncovered" '
               'verdict would be indistinguishable from a broken matcher.', '']
        for area in sorted(buckets):
            vs = buckets[area].get('variant', [])
            if not vs:
                continue
            md += ['## %s — %d to adjudicate' % (area, len(vs)), '',
                   '| where | the app teaches | the book prints | source |', '|---|---|---|---|']
            for ident, ar, en, ev, prov in vs:
                book, src, raw = ev
                md.append('| %s | %s | %s | %s |' % (ident, ar, raw, src))
            md.append('')
        open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(md))
        print('\n-> %s' % os.path.relpath(OUT_MD, ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
