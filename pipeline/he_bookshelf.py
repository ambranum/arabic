#!/usr/bin/env python3
"""Shared emitter + gate for the Hebrew graded readers -> texts/he/book-<id>-chNN.json.

The Hebrew counterpart of bookshelf.py, and it reuses that file's emitter rather than copying
it: a chapter file has the same shape in both languages, and `ar` in these records has always
meant "in the target script". What this adds is the GATE, because the Hebrew shelf cannot be
written the way the Arabic one was.

The Arabic readers are checked by bookshelf_check.py after the fact, by eye and by sentence
length. Hebrew has something better available and the stories already use it: the lexicon knows
whether a word exists. So the same three refusals that guard pipeline/he_stories.py guard the
shelf, and a book that fails one is not written at all.

  * EVERY WORD MUST BE IN THE LEXICON. The reader taps words; a retelling built on a word the
    app cannot gloss is a broken page, not a hard one.
  * REGISTER. No biblical vav-consecutive, no archaic function words. Retelling Treasure Island
    in Hebrew pulls literary without meaning to -- the language HAS a narrative past that is
    two thousand years old and it is not what anyone speaks.
  * LENGTH, per level, so "intermediate" is a claim the file has to earn rather than a label.

Deliberately unpointed, like the stories and the news. Vowels come from the lexicon at ingest,
where they are looked up -- see pipeline/he_ingest.py on why pointing IS the disambiguation.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated),
but every WORD's lemma, pointing, gloss and root is retrieved, never generated.

    from he_bookshelf import P, book
    book('aesop', {'en': "Aesop's Fables", 'he': 'משלי איזופוס'}, 'beginner', CHAPTERS,
         unit='Fable', unit_he='משל', shelf=2, meta={...})

Run a book file with no arguments to CHECK it; --write to emit. Nothing is written while a
single chapter has a problem.
"""
import argparse
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths                                          # noqa: E402
paths.require('he')

import he_ingest                                      # noqa: E402
from bookshelf import P, emit_book                    # noqa: E402
from he_stories import ARCHAIC, vav_consecutives      # noqa: E402
from lex import Lexicon                               # noqa: E402

__all__ = ['P', 'book']

SOURCE = 'retold in modern Hebrew by Claude — NOT native-validated'

# level -> average-words-per-sentence band. The same numbers he_stories.py measured its tiers
# against, and for the same reason: a graded reader grades itself by feel unless something
# counts. A book is checked on its whole-book average, not per chapter -- one short chapter of
# dialogue inside a long book is fine and a book of them is not.
BANDS = {'beginner': (0.0, 9.0), 'intermediate': (7.0, 14.0), 'advanced': (11.0, 21.0)}


def check(lex, level, chapters):
    """-> (problems, stats) for a whole book. Problems are named per chapter, since that is
    where they get fixed."""
    lo, hi = BANDS[level]
    bad, lengths, toks = [], [], []
    for i, (en, _he, paras) in enumerate(chapters, 1):
        sents = [h for para in paras for (h, _e) in para]
        ctoks = [t for h in sents for t in he_ingest.tokenize(h)]
        toks += ctoks
        lengths += [len(he_ingest.tokenize(h)) for h in sents]
        # The question is not "is this in the lexicon", it is "will the reader be able to tap
        # it", and only one function knows the answer: the annotator itself. Asking it directly
        # means the gate cannot drift from what actually gets written to the page -- it sees
        # the curated table, the clitic peeler and the resolution trail in the same order and
        # with the same precedence he_ingest.py uses at ingest.
        #
        # A shelf of novels needs this in a way the stories did not. A character's NAME has no
        # lexical entry in any language -- טוֹם, פוֹג, הוֹלְמְס, ג'וֹחָא -- so every one of them
        # would read "not in the lexicon" here and "not in the lexicon" on the word card. The
        # honest place for the answer is he_curated.PROPER, written down once, pointing and
        # gloss together, and marked `curated:proper-noun` where the reader can see it.
        unknown = sorted({t for t in ctoks
                          if he_ingest.annotate(lex, t, {})['provenance'] == 'unresolved'})
        if unknown:
            bad.append('ch%02d %s — not in the lexicon: %s' % (i, en, ', '.join(unknown)))
        arch = sorted({t for t in ctoks if t in ARCHAIC})
        if arch:
            bad.append('ch%02d %s — literary register: %s' % (i, en, ', '.join(arch)))
        vav = sorted(set(vav_consecutives(lex, ctoks)))
        if vav:
            bad.append('ch%02d %s — vav-consecutive: %s' % (i, en, ', '.join(vav)))
        # An English line is what makes this a bilingual reader; a blank one ships a page with
        # a gap in it, and it is easier to miss in a 40-chapter literal than anything else here.
        for (h, e) in [(h, e) for para in paras for (h, e) in para]:
            if not e.strip() or not h.strip():
                bad.append('ch%02d %s — empty side: %r / %r' % (i, en, h, e))
    avg = statistics.mean(lengths) if lengths else 0.0
    if avg > hi:
        bad.append('sentences average %.1f words — %s tops out at %.0f' % (avg, level, hi))
    if avg < lo:
        bad.append('sentences average %.1f words — %s starts at %.0f' % (avg, level, lo))
    return bad, {'chapters': len(chapters), 'sentences': len(lengths), 'tokens': len(toks),
                 'avg': avg, 'longest': max(lengths) if lengths else 0}


def book(book_id, title, level, chapters, *, unit='Chapter', unit_he='פרק', shelf=0, meta=None):
    """Check this book, and write it only if it passes. The book scripts' whole main()."""
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='emit texts/he/book-%s-ch*.json' % book_id)
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()

    lex = Lexicon()
    bad, st = check(lex, level, chapters)
    print('%s — %s, %d chapters, %d sentences, %d words, %.1f per sentence (longest %d)'
          % (title['en'], level, st['chapters'], st['sentences'], st['tokens'],
             st['avg'], st['longest']))
    for b in bad:
        print('  !! %s' % b)
    if bad:
        print('\n%d problems — nothing written. A page the reader cannot tap every word of, or '
              'that reads like scripture, is not one of these.' % len(bad))
        return 1
    if not a.write:
        print('all clear. --write to emit.')
        return 0
    emit_book(book_id, {'en': title['en'], 'ar': title['he']}, level, chapters,
              unit=unit, unit_ar=unit_he, shelf=shelf, meta=meta, source=SOURCE,
              outdir=paths.texts())
    return 0
