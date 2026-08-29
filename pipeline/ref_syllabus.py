#!/usr/bin/env python3
"""Draft texts/ref/SYLLABUS.md from the merged reference transcriptions.

Walks every texts/ref/<book>.json and emits a per-book unit table: unit number, title,
pages, the grammar topics taught, and content counts. This is the raw teaching sequence
mined from the user's materials; the hand-written synthesis at the top of SYLLABUS.md
(how the books merge into ONE sequence, and how that maps onto the app's 7 phases) is
curated on top of this draft and preserved between runs (everything above the
AUTO-GENERATED marker is kept).

Run:  python3 pipeline/ref_syllabus.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import glob, json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
REF = paths.texts('ref')
OUT = os.path.join(REF, 'SYLLABUS.md')
MARK = '<!-- AUTO-GENERATED below — edit above this line only -->'


def unit_row(u):
    secs = u.get('sections', [])
    topics = [s.get('topic') for s in secs if s.get('kind') == 'grammar' and s.get('topic')]
    n_vocab = sum(len(s.get('items', [])) for s in secs if s.get('kind') == 'vocab')
    n_dlg = sum(1 for s in secs if s.get('kind') == 'dialogue')
    n_drill = sum(1 for s in secs if s.get('kind') == 'drill')
    n_text = sum(1 for s in secs if s.get('kind') in ('text', 'conjugation'))
    t = u.get('title') or {}
    title = (t.get('en') or t.get('ar') or '—') if isinstance(t, dict) else str(t)
    pages = u.get('pages') or ['?', '?']
    return '| %s | %s | %s–%s | %s | %dv · %dd · %dx · %dt |' % (
        u.get('unit') if u.get('unit') is not None else '—', title.replace('|', '/'),
        pages[0], pages[1], ', '.join(topics) or '—', n_vocab, n_dlg, n_drill, n_text)


def main():
    head = ''
    if os.path.exists(OUT):
        cur = open(OUT, encoding='utf-8').read()
        if MARK in cur:
            head = cur.split(MARK)[0]
    body = [MARK, '']
    for f in sorted(glob.glob(os.path.join(REF, '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        if 'units' not in d:
            continue
        body.append('## %s (pages %s–%s, %d units)' % (d['book'], d['pages'][0], d['pages'][1], len(d['units'])))
        body.append('')
        body.append('| unit | title | pages | grammar topics | content (vocab·dialogues·drills·texts) |')
        body.append('|---|---|---|---|---|')
        body.extend(unit_row(u) for u in d['units'])
        body.append('')
    open(OUT, 'w', encoding='utf-8').write(head + '\n'.join(body) + '\n')
    print('-> texts/ref/SYLLABUS.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
