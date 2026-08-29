#!/usr/bin/env python3
"""Check phon.py against every romanization English Wiktionary gives for Hebrew.

This is the Hebrew analogue of pipeline/verify_conjugation.py: an INDEPENDENT oracle, written
by people who were not us, that we compare against rather than trust ourselves about. Wiktionary
prints a Modern Israeli romanization beside the pointed spelling for ~16k Hebrew entries, which
is a far better test set than any list I could hand-build -- it is large, it was not chosen by
the person writing the rules, and it covers the long tail where the rules actually break.

Their conventions differ from ours in a few fixed ways (kh vs x, tz vs ts, stress written with
an acute). Those are notation, not disagreement, so they are normalized away on both sides
before comparing -- and the normalization is deliberately narrow: anything beyond a spelling
convention has to show up as a mismatch, or the test is measuring nothing.

    python3 spike/he/verify_phon.py            # summary + the top mismatch shapes
    python3 spike/he/verify_phon.py --show 40  # plus 40 individual mismatches
"""
import collections
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phon import phon                                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, 'kaikki-hebrew.jsonl')

# A romanization carrying any of these is Tiberian, not Modern Israeli -- Wiktionary prints
# both and we only want the one people actually say.
TIBERIAN = set('ḇḵḏḡṯṗāēīōūǝăĕŏʾʿšśṣṭḥăq̄')


def is_modern(r):
    return not (set(unicodedata.normalize('NFC', r)) & TIBERIAN)


def canon(s):
    """Fold the two notations onto one so only real disagreements survive."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')   # drop the stress acute
    s = s.lower().replace('kh', 'x').replace('ch', 'x').replace('tz', 'ts')
    s = s.replace('’', '').replace("'", '').replace('`', '').replace('-', '')
    s = s.replace('ẖ', 'x').replace('ẖ', 'x')
    # Wiktionary writes the tsere+yod diphthong as "ei" or plain "e"; we write
    # "ey". Same sound -- fold it rather than score a notation choice as a miss.
    s = re.sub(r'[^a-z]', '', s)
    for a, b in (('ei', 'e'), ('ey', 'e'), ('ai', 'ay'), ('oi', 'oy'),
                ('ui', 'uy'), ('iya', 'ia'), ('iyo', 'io')):
        s = s.replace(a, b)
    return s


def rows():
    for line in open(DUMP, encoding='utf-8'):
        d = json.loads(line)
        ht = (d.get('head_templates') or [{}])[0].get('args', {})
        wv = ht.get('wv') or next((f['form'] for f in d.get('forms', [])
                                   if 'canonical' in (f.get('tags') or [])), None)
        roms = [f['form'] for f in d.get('forms', [])
                if 'romanization' in (f.get('tags') or [])]
        roms = [r for r in roms if is_modern(r)]
        if not wv or not roms:
            continue
        # Multi-word entries and anything with latin/digits in the Hebrew are out of scope for
        # a single-word transducer.
        if ' ' in wv.strip() or re.search(r'[A-Za-z0-9]', wv):
            continue
        yield d.get('word'), wv, roms, d.get('pos')


def main():
    show = 0
    if '--show' in sys.argv:
        show = int(sys.argv[sys.argv.index('--show') + 1])
    n = ok = 0
    shapes = collections.Counter()
    misses = []
    for word, wv, roms, pos in rows():
        got = canon(phon(wv))
        want = [canon(r) for r in roms]
        n += 1
        if got in want:
            ok += 1
        else:
            shapes[(want[0], got)] += 0        # placeholder so the key exists
            misses.append((wv, roms[0], phon(wv), pos))
    print('checked %d vocalized entries' % n)
    print('agree   %d  (%.2f%%)' % (ok, 100.0 * ok / max(n, 1)))
    print('differ  %d' % (n - ok))

    # Group the mismatches by what CHANGED, so a systematic rule error is visible as a big
    # bucket instead of hiding in a thousand one-offs.
    pat = collections.Counter()
    for wv, want, got, pos in misses:
        w, g = canon(want), got and canon(got)
        pat[_diff_shape(w, g)] += 1
    print('\ntop mismatch shapes:')
    for (shape, c) in pat.most_common(18):
        print('  %6d  %s' % (c, shape))
    if show:
        print('\nexamples:')
        for wv, want, got, pos in misses[:show]:
            print('  %-16s want %-16s got %-16s %s' % (wv, want, got, pos))


def _diff_shape(want, got):
    """A one-line description of how two romanizations differ."""
    if not got:
        return '(empty output)'
    if want == got:
        return '(equal after canon)'
    if len(want) == len(got):
        d = [(a, b) for a, b in zip(want, got) if a != b]
        if len(d) == 1:
            return '%s -> %s' % (d[0][0], d[0][1])
        return '%d char substitutions' % len(d)
    if len(got) == len(want) + 1:
        for i in range(len(got)):
            if got[:i] + got[i + 1:] == want:
                return 'inserted %r' % got[i]
    if len(want) == len(got) + 1:
        for i in range(len(want)):
            if want[:i] + want[i + 1:] == got:
                return 'dropped %r' % want[i]
    return 'len %d -> %d' % (len(want), len(got))


if __name__ == '__main__':
    main()
