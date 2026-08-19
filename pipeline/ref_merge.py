#!/usr/bin/env python3
"""Merge transcription fragments into per-book reference files.

Transcription is fanned out in page-range chunks (texts/ref/fragments/<book>-pXXX-YYY.json,
written by parallel transcribers). This stitches each book's fragments back into one
texts/ref/<book>.json, joining lessons that were split across chunk boundaries:
a unit flagged `incomplete` at the end of one fragment absorbs the `continues`/unit:null
unit at the start of the next (their sections concatenate, page ranges extend).

Run:  python3 pipeline/ref_merge.py            # merge all books with fragments
      python3 pipeline/ref_merge.py --book najah
"""
import argparse, glob, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FRAG = os.path.join(ROOT, 'texts', 'ref', 'fragments')
OUT = os.path.join(ROOT, 'texts', 'ref')


def merge_book(slug):
    files = sorted(glob.glob(os.path.join(FRAG, slug + '-p*.json')),
                   key=lambda f: int(re.search(r'-p(\d+)', os.path.basename(f)).group(1)))
    if not files:
        return None
    units, pages_lo, pages_hi = [], 10 ** 9, 0
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        pages_lo = min(pages_lo, d['pages'][0]); pages_hi = max(pages_hi, d['pages'][1])
        for u in d.get('units', []):
            joined = False
            # A continuation (unit:null/continues) glues onto the previous incomplete unit.
            # Same printed unit number also glues — two transcribers saw the same lesson.
            if units:
                prev = units[-1]
                same_no = u.get('unit') is not None and u.get('unit') == prev.get('unit')
                if (u.get('continues') or u.get('unit') is None or same_no) and prev.get('incomplete'):
                    prev['sections'].extend(u.get('sections', []))
                    prev['pages'] = [prev['pages'][0], max(prev['pages'][1], (u.get('pages') or prev['pages'])[1])]
                    prev['incomplete'] = bool(u.get('incomplete'))
                    if not prev.get('title') and u.get('title'):
                        prev['title'] = u['title']
                    joined = True
            if not joined:
                u.pop('continues', None)
                units.append(u)
    for u in units:
        u.pop('incomplete', None)
    book = {'book': slug, 'pages': [pages_lo, pages_hi],
            'source': 'transcribed from the user\'s reference materials — see reference/README.md',
            'units': units}
    out = os.path.join(OUT, slug + '.json')
    json.dump(book, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n_vocab = sum(len(s.get('items', [])) for u in units for s in u.get('sections', []) if s.get('kind') == 'vocab')
    n_dlg = sum(1 for u in units for s in u.get('sections', []) if s.get('kind') == 'dialogue')
    n_drill = sum(1 for u in units for s in u.get('sections', []) if s.get('kind') == 'drill')
    print(f'{slug:14} {len(units):3} units · {n_vocab:4} vocab · {n_dlg:3} dialogues · {n_drill:3} drills -> texts/ref/{slug}.json')
    return book


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book')
    a = ap.parse_args()
    slugs = sorted({re.match(r'(.+?)-p\d+', os.path.basename(f)).group(1)
                    for f in glob.glob(os.path.join(FRAG, '*-p*.json'))})
    for slug in slugs:
        if a.book and slug != a.book:
            continue
        merge_book(slug)
    return 0


if __name__ == '__main__':
    sys.exit(main())
