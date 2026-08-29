#!/usr/bin/env python3
"""Strip transcription notes from texts/lessons/unit-*.json.

When the reference books were transcribed, some notes about the PRINTED PAGE came along with
the content: "[numbered 5 twice in print]", "(the last three pairs are printed in smaller
type)", "printed on to you in your family". Those describe the paper. A learner reading a
drill has no use for them, and one of them ("numbered 5 twice") reproduced a numbering bug
from the book into the app.

Rules, in order:
  1. FIX      — exact string replacements, listed so every change is auditable.
  2. RENUMBER — a drill whose items carry "1." "2." … is renumbered 1..n, but ONLY when the
                existing numbers actually repeat. That is what fixes the duplicate 5 without
                touching the drills that number themselves deliberately (unit-05 uses "1)").

Notes about the CONTENT are deliberately kept — "More directions (not in the printed book)"
tells you that those chunks are not native-sourced, which is a provenance claim and the whole
point of this module. Only notes about the physical page go.

Idempotent: run it twice and the second run reports 0 changes.

    python3 pipeline/lesson_notes.py && python3 pipeline/lessons.py && python3 pipeline/build_app.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import glob
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = paths.texts('lessons')

FIX = {
    # unit-02 — a note on how the book misprinted the English, and one on its numbering
    "3. مين أقْرَب واحَد عَليك في الْعيلة. (Who is the closest one to you in your family? "
    "[printed 'on to you in your family'])":
        '3. مين أقْرَب واحَد عَليك في الْعيلة. (Who is the closest one to you in your family?)',
    '5. إحكي-لْنا عَن سيدَك وسِتَّك. [numbered 5 twice in print]':
        '5. إحكي-لْنا عَن سيدَك وسِتَّك.',
    # unit-02 — punctuation the book got wrong either way round: مين makes the first a question
    # and the book left the ؟ off; the second is an imperative that picked up a stray ?.
    '3. مين أقْرَب واحَد عَليك في الْعيلة. (Who is the closest one to you in your family?)':
        '3. مين أقْرَب واحَد عَليك في الْعيلة؟ (Who is the closest one to you in your family?)',
    '(Talk about a well known family from the history?)':
        '(Talk about a well-known family from history.)',
    # unit-04 — the page's layout, described
    '(Six job ads printed in boxes; phone numbers printed in Arabic-Indic digits.) ': '',
    # unit-28 — the book's own plural was unreadable; saying so does not help you say the word
    "ugly (printed; the plural is printed as '؟؟')": 'ugly',
    # unit-30/31 — the book's notation and its type sizes
    "وحدة 17. Plural printed as 'ات' alone means the noun simply takes the ات suffix.":
        "وحدة 17. A plural shown as 'ات' means the noun just takes the ات ending.",
    'Two hundred everyday nouns, each printed with its plural.':
        'Two hundred everyday nouns, each with its plural.',
    'pattern aF3aaL (the last three pairs are printed in smaller type)': 'pattern aF3aaL',
    # unit-37 — "printed" is about the book; the point is the dialect
    'A six-part story printed deliberately in the GALILEE dialect':
        'A six-part story told deliberately in the Galilee dialect',
    'Read a passage aloud twice: once as printed, once "translated" into the urban forms.':
        'Read a passage aloud twice: once as written, once "translated" into the urban forms.',
}

NUM = re.compile(r'^\s*(\d+)\s*\.\s*(.+)$', re.S)


def fix_str(s):
    out = s
    for a, b in FIX.items():
        if a in out:
            out = out.replace(a, b)
    return out.strip() if out != s else s


def walk(o):
    """Rewrite every string in place; returns the number of strings changed."""
    n = 0
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if isinstance(v, str):
                f = fix_str(v)
                if f != v:
                    o[k] = f
                    n += 1
            else:
                n += walk(v)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str):
                f = fix_str(v)
                if f != v:
                    o[i] = f
                    n += 1
            else:
                n += walk(v)
    return n


def renumber(drill):
    """1..n, but only for a drill whose numbering actually repeats itself."""
    items = [it for it in drill.get('items', []) if isinstance(it, dict) and it.get('cue')]
    ms = [NUM.match(it['cue']) for it in items]
    if len(items) < 2 or not all(ms):
        return 0
    nums = [int(m.group(1)) for m in ms]
    if len(set(nums)) == len(nums):        # no duplicate — leave the book's own numbering alone
        return 0
    n = 0
    for i, (it, m) in enumerate(zip(items, ms), 1):
        cue = '%d. %s' % (i, m.group(2))
        if cue != it['cue']:
            it['cue'] = cue
            n += 1
    return n


def main():
    files = sorted(glob.glob(os.path.join(SRC, 'unit-*.json')))
    total, touched = 0, 0
    for path in files:
        with io.open(path, encoding='utf-8') as f:
            d = json.load(f)
        n = walk(d)
        for drill in d.get('drills', []):
            n += renumber(drill)
        if n:
            with io.open(path, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
                f.write('\n')
            touched += 1
            total += n
            print('  %-14s %d string%s' % (os.path.basename(path), n, '' if n == 1 else 's'))
    print('%d change%s across %d of %d unit files'
          % (total, '' if total == 1 else 's', touched, len(files)))


if __name__ == '__main__':
    main()
