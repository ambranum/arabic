#!/usr/bin/env python3
"""Render the reference teaching materials to page images for transcription.

The books in reference/ are image scans with no text layer (verified — pypdf extracts
zero characters), so they can't be parsed; they have to be READ. This script renders
every page to a PNG under build/ref/<slug>/pNNN.png so Claude can transcribe them
page-by-page into texts/ref/<slug>.json. The renders are a local working artifact
(build/ is not committed); the transcriptions are the deliverable.

The Lingualism verbs book is EXCLUDED here on purpose: it has a text layer and its own
dedicated verifier (pipeline/verify_conjugation.py), and it is a commercial third-party
book used for verification only.

Run:
    python3 pipeline/ref_extract.py            # render everything not yet rendered
    python3 pipeline/ref_extract.py --stats    # coverage: pages rendered / transcribed
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
REF = os.path.join(ROOT, 'reference')
OUT = paths.build('ref')
TXT = paths.texts('ref')

# slug -> filename. "Speaking Arabic.pdf" is byte-identical to "Spoken Arabic Lessons.pdf"
# (same md5), so only one of the pair is rendered.
BOOKS = {
    'ar': {
        'najah':        'Najah lessons.pdf',
        'speaking':     'Speaking Arabic.pdf',
        'spoken-extra': 'Spoken Arabic Lessons additional.pdf',
        'vocab-gram':   'Vocab and Grammar.pdf',
        'stories':      'Short Stories.pdf',
        'verb-forms':   'Verb Forms.pdf',
        'verb-drills':  'Verb Drills.pdf',
    },
    # The Hebrew shelf. Same job, same treatment: image scans with no text layer, rendered so
    # they can be read. The last two DO have a text layer and are read straight out of the PDF.
    'he': {
        'aleph':     'Aleph ++.pdf',
        'bet':       'Bet.pdf',
        'gimel':     'Gimel.pdf',
        'gimel-plus': 'Gimmel +.pdf',
        'pod':       'HebrewPod.pdf',
        'reichman':  'Reichman.pdf',
    },
}[paths.LANG]
DPI = 200   # crisp enough for Arabic diacritics without huge files


def render(slug, fname, force=False):
    import pymupdf
    src = os.path.join(REF, fname)
    if not os.path.exists(src):
        print(f'!! missing {fname} — skipped'); return 0
    outdir = os.path.join(OUT, slug)
    os.makedirs(outdir, exist_ok=True)
    doc = pymupdf.open(src)
    n = 0
    for i, page in enumerate(doc):
        out = os.path.join(outdir, 'p%03d.png' % (i + 1))
        if os.path.exists(out) and not force:
            continue
        page.get_pixmap(dpi=DPI).save(out)
        n += 1
    print(f'{slug:14} {len(doc):4} pages ({n} newly rendered) -> build/ref/{slug}/')
    return len(doc)


def stats():
    print(f'{"book":14} {"pages":>5} {"rendered":>9} {"transcribed":>12}')
    for slug, fname in BOOKS.items():
        outdir = os.path.join(OUT, slug)
        rendered = len([f for f in os.listdir(outdir) if f.endswith('.png')]) if os.path.isdir(outdir) else 0
        done = set()
        tf = os.path.join(TXT, slug + '.json')
        if os.path.exists(tf):
            d = json.load(open(tf, encoding='utf-8'))
            for u in d.get('units', []):
                pg = u.get('pages')                     # the convention the transcribers settled on
                if isinstance(pg, list) and len(pg) == 2 and all(isinstance(x, int) for x in pg):
                    done.update(range(pg[0], pg[1] + 1))
                    continue
                m = re.match(r'(\d+)\s*[-–]\s*(\d+)$', str(u.get('page_range', '')))
                if m:
                    done.update(range(int(m.group(1)), int(m.group(2)) + 1))
                elif str(u.get('page_range', '')).isdigit():
                    done.add(int(u['page_range']))
        src = os.path.join(REF, fname)
        total = 0
        if os.path.exists(src):
            import pymupdf
            total = len(pymupdf.open(src))
        print(f'{slug:14} {total:5} {rendered:9} {len(done):12}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stats', action='store_true')
    ap.add_argument('--force', action='store_true', help='re-render existing pages')
    ap.add_argument('--book', help='render just one slug')
    a = ap.parse_args()
    if a.stats:
        return stats()
    os.makedirs(TXT, exist_ok=True)
    for slug, fname in BOOKS.items():
        if a.book and slug != a.book:
            continue
        render(slug, fname, a.force)
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
