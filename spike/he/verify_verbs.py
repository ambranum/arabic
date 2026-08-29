#!/usr/bin/env python3
"""A3's two questions, answered with numbers.

The plan asked for a conjugation ENGINE verified against Pealim at >=98%. A1 changed the
question: Wiktionary already ships pointed paradigms, so the honest measure is not "how well
does our derivation imitate a book" but

  1. ARE THE TABLES RIGHT?  Wiktionary romanizes the lemma, and for a Hebrew verb the lemma IS
     the 3ms past -- the same cell the app banks a card under. So every verb gives one free
     cross-check of extraction + phonology against a transcription we did not write.

  2. DO THE VERBS A LEARNER MEETS HAVE ONE?  Coverage over the verb tokens in live news, not
     over the dictionary. A paradigm for a verb nobody says is worth nothing.

    python3 spike/he/verify_verbs.py
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coverage import ACRONYM, HEB_TOKEN, sentences                # noqa: E402
from lex import Lexicon                                           # noqa: E402
from verbs_he import SLOTS, paradigms                             # noqa: E402
from verify_phon import canon, is_modern                          # noqa: E402


def lemma_romanizations():
    """{POINTED lemma -> Wiktionary's Modern Israeli romanization} for verbs.

    Keyed on the pointed form, not the normalized one. Unpointed מהר is both מָהַר (paal, to
    hurry) and מִהֵר (piel, to hasten); a normalized key silently compares one binyan's cell
    against the other's transcription and reports it as a 71% piel failure rate. That is a bug
    in the harness, not in the data, and it is exactly the ambiguity A1 measured.
    """
    import json
    import re
    out = {}
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'kaikki-hebrew.jsonl'), encoding='utf-8'):
        d = json.loads(line)
        if d.get('pos') != 'verb':
            continue
        ht = (d.get('head_templates') or [{}])[0].get('args', {})
        wv = ht.get('wv')
        rom = [f['form'] for f in d.get('forms', [])
               if 'romanization' in (f.get('tags') or []) and is_modern(f['form'])]
        if wv and rom and not re.search(r'[A-Za-z0-9]', wv):
            out.setdefault(wv.strip(), rom[0])
    return out


def main():
    vs = paradigms()
    by_lemma = {v['lemma_search']: v for v in vs}
    print('paradigms extracted: %d   complete (all %d slots): %d  (%.0f%%)\n'
          % (len(vs), len(SLOTS), sum(1 for v in vs if len(v['conj']) == len(SLOTS)),
             100.0 * sum(1 for v in vs if len(v['conj']) == len(SLOTS)) / len(vs)))

    # ---- 1. are the tables right? -------------------------------------------------------
    roms = lemma_romanizations()
    per_binyan = collections.defaultdict(lambda: [0, 0])
    bad = []
    for v in vs:
        cell = v['conj'].get('past|hu')
        want = roms.get(v['lemma'].strip())
        if not cell or not want:
            continue
        b = v['form'] or '(none)'
        per_binyan[b][1] += 1
        if canon(cell['ph']) == canon(want):
            per_binyan[b][0] += 1
        elif len(bad) < 12:
            bad.append((v['lemma'], b, want, cell['ph']))
    ok = sum(a for a, _ in per_binyan.values())
    tot = sum(b for _, b in per_binyan.values())
    print('1. 3ms-past cell vs Wiktionary\'s own romanization')
    print('   %d/%d  %.2f%%' % (ok, tot, 100.0 * ok / max(tot, 1)))
    for b in sorted(per_binyan, key=lambda x: -per_binyan[x][1]):
        a, n = per_binyan[b]
        print('     %-10s %4d/%-4d %5.1f%%' % (b, a, n, 100.0 * a / max(n, 1)))
    if bad:
        print('   sample disagreements:')
        for lem, b, want, got in bad[:6]:
            print('     %-12s %-9s want %-14s got %s' % (lem, b, want, got))

    # ---- 2. do the verbs a learner meets have one? --------------------------------------
    lx = Lexicon()
    sents = sentences(300)
    seen = collections.Counter()
    withp = collections.Counter()
    tokens = hits = 0
    for _, text in sents:
        for tok in HEB_TOKEN.findall(text):
            if ACRONYM.search(tok):
                continue
            recs, prov, cut = lx.look(tok)
            vrec = next((r for r in recs if r['POS'] == 'verb'), None)
            if not vrec:
                continue
            tokens += 1
            key = vrec['LEMMA_SEARCH']
            seen[key] += 1
            if key in by_lemma:
                hits += 1
                withp[key] += 1
    print('\n2. verb tokens in 300 live news sentences')
    print('   verb tokens          %5d' % tokens)
    print('   distinct verb lemmas %5d' % len(seen))
    print('   tokens with a paradigm %5d  %.1f%%' % (hits, 100.0 * hits / max(tokens, 1)))
    print('   lemmas with a paradigm %5d  %.1f%%'
          % (len(withp), 100.0 * len(withp) / max(len(seen), 1)))
    missing = [(w, c) for w, c in seen.most_common() if w not in by_lemma]
    if missing:
        print('\n   most frequent verbs with NO paradigm:')
        for w, c in missing[:12]:
            print('     %4d  %s' % (c, w))


if __name__ == '__main__':
    main()
