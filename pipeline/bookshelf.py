#!/usr/bin/env python3
"""Shared emitter for the graded readers in the Books section.

NOT to be confused with book_overrides.py / book_sweep.py / apply_book_overrides.py, which are
about the Lingualism VERB REFERENCE book (the conjugation oracle). This file and book_<id>.py are
about the readers on the shelf. Hence "bookshelf".

A book script is a docstring, four constants and a CHAPTERS literal — the prose is the point, and
it should stay pleasant to write. Everything mechanical lives here: flattening paragraphs into
sentences, numbering chapters, naming them, and writing one JSON per chapter into texts/.

The house rule holds as everywhere else in this project: the PROSE is written by hand (by Claude,
flagged NOT native-validated), but nothing about the WORDS is invented — root, lemma, gloss and
CAPHI are looked up in Maknuune by pipeline/ingest.py after these files are written.

Content is organized in PARAGRAPHS: a chapter is a list of paragraphs, a paragraph a list of
(arabic, english) pairs. Every emitted sentence carries `p`, its paragraph index, which is what
makes the reader and the print-to-PDF view lay a book out as flowing bilingual paragraphs rather
than a list of sentences.

    from bookshelf import P, emit_book

    CHAPTERS = [
      ('The Donkey and the Neighbour', 'الحمار والجار', [
        P(('جحا كان عنده حمار.', 'Juha had a donkey.'),
          ('إجا جاره وقال له بدي أستعير الحمار.', 'His neighbour came and said: I want to borrow the donkey.')),
      ]),
    ]
    emit_book('juha', {'en': 'Juha', 'ar': 'جحا'}, 'beginner', CHAPTERS,
              unit='Tale', unit_ar='حكاية', shelf=10)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import json, os, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SOURCE = 'adapted by Claude — NOT native-validated'


def P(*pairs):   # a paragraph: P(("ar","en"), ("ar","en"), ...)
    return list(pairs)


import re

_AR_END = re.compile(r'(?<=[.؟!])\s+(?=\S)')
_EN_END = re.compile(r'(?<=[.?!])\s+(?=[A-Z"“‘\'])')
_ABBREV = re.compile(r'\b(Mr|Mrs|Dr|St|No)\.$')


def split_pair(ar, en):
    """One (ar, en) pair -> a list of pairs, one per spoken sentence.

    A pair written as `قال: خلص. بكرا منرجع.` is two sentences the reader taps, translates and
    (in the shadow drill) repeats as one unit, and it is what pushed the second-edition books to
    a 90th-percentile sentence length half again over their level. The two halves were written
    in parallel, so when the Arabic and the English hold the SAME number of sentences the split
    is safe; when they do not, the pair is left whole and reported, for a human to look at.
    """
    a = [s for s in _AR_END.split(ar.strip()) if s]
    e = [s for s in _EN_END.split(en.strip()) if s]
    # "Mr. Holmes" is not a sentence boundary: glue an abbreviation back onto what follows.
    i = 0
    while i < len(e) - 1:
        if _ABBREV.search(e[i]):
            e[i:i + 2] = [e[i] + ' ' + e[i + 1]]
        else:
            i += 1
    if len(a) > 1 and len(a) == len(e):
        return list(zip(a, e))
    return [(ar, en)]


LEVELS = ('beginner', 'intermediate', 'advanced')   # the only strings the app maps to a phase


def emit_book(book_id, title, level, chapters, *, unit='Chapter', unit_ar='الفصل',
              shelf=0, meta=None, source=SOURCE, outdir=None):
    """Write texts/book-<book_id>-chNN.json, one file per chapter. Returns (chapters, sentences).

    unit / unit_ar name the division, because "Chapter 3" is wrong for a book of folk tales —
    Juha gets "Tale 3 / حكاية 3", Aesop "Fable 7 / خرافة 7".

    shelf is a sort key the Books shelf orders by, so the running order of nine books is decided
    here rather than falling out of whatever order the build directory happens to be globbed in.

    meta credits the source work — {work, author, year, status} — shown on the book's page and in
    the PDF. Every reader here is a retelling of a PUBLIC DOMAIN work, and saying which one, on
    the page, is the same diligence data/ATTRIBUTION.md gives the lexicon and the Bible text.

    WARNING when re-emitting a book that already has audio: clip filenames are POSITIONAL
    (s0.mp3, s1.mp3 …). Adding, removing or reordering a sentence silently re-points every later
    clip at the wrong text. Change prose freely, but then delete build/book-<id>-*/audio/ and
    re-voice — see pipeline/README.md.
    """
    # `level` decides the phase chip in the app, and an unrecognised string silently renders as
    # Beginner/A1 rather than failing. Catch the typo here, where it is one word to fix.
    if level not in LEVELS:
        raise SystemExit('!! %s: level %r must be one of %s' % (book_id, level, ', '.join(LEVELS)))
    outdir = outdir or paths.texts()
    # Drop this book's old chapter files first, so a shortened CHAPTERS leaves no orphans behind.
    # Scoped to this book_id — two book scripts never clobber each other.
    for old in glob.glob(os.path.join(outdir, 'book-%s-ch*.json' % book_id)):
        os.remove(old)

    total = 0
    splits, uneven = 0, []
    for i, (en, ar, paras) in enumerate(chapters, 1):
        cid = 'book-%s-ch%02d' % (book_id, i)
        sentences = []
        for pi, para in enumerate(paras):
            for (a, e) in para:
                parts = split_pair(a, e)
                if len(parts) > 1:
                    splits += len(parts) - 1
                elif len(_AR_END.split(a.strip())) > 1:
                    uneven.append((cid, a))
                for (a2, e2) in parts:
                    sentences.append({'ar': a2, 'en': e2, 'p': pi})
        art = {
            'id': cid,
            'title': {'en': '%s %d — %s' % (unit, i, en), 'ar': '%s %d — %s' % (unit_ar, i, ar)},
            'kind': 'book-chapter', 'book': book_id, 'book_title': title, 'chapter': i,
            'shelf': shelf,
            'book_meta': meta or None,
            'level': level,
            'source': source,
            'sentences': sentences,
        }
        with open(os.path.join(outdir, cid + '.json'), 'w', encoding='utf-8') as f:
            json.dump(art, f, ensure_ascii=False, indent=1)
        total += len(sentences)
        print('wrote %s  (%d paragraphs, %d sentences)' % (cid, len(paras), len(sentences)))

    # Characters in the target script ≈ ElevenLabs credits, so this line is also the voicing bill.
    chars = sum(len(a) for (_en, _ar, paras) in chapters for para in paras for (a, _e) in para)
    u = unit.lower()
    plural = u[:-1] + 'ies' if u.endswith('y') else u + 's'      # story -> stories, not storys
    print('\n%d %s, %d sentences, %d chars -> %s/book-%s-ch*.json'
          % (len(chapters), plural, total, chars, os.path.relpath(outdir, ROOT), book_id))
    if splits:
        print('%d pairs split at sentence boundaries (Arabic and English agreed on the count)' % splits)
    for cid, a in uneven:
        print('!! %s: multi-sentence Arabic whose English does not split the same way, left whole:\n     %s'
              % (cid, a))
    return len(chapters), total
