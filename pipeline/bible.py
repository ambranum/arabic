#!/usr/bin/env python3
"""Parse a public-domain scripture edition into the app's Bible data.

SOURCE: Arabic Van Dyck translation (Smith & Van Dyke, 1865) — PUBLIC DOMAIN, downloaded
from ebible.org (arb-vd). The USFM sits in data/bible-vandyck/ and is committed because it's
PD and keeps the build reproducible offline. This is the ARABIC (right) column of the
parallel Bible. The ESV (left column) is NOT stored anywhere — it's fetched at runtime from
Crossway with the user's own API key (their licence forbids redistributing the text).

Output, split so the app stays fast — the whole Bible as one script tag would be ~5 MB on
every page load:
  app/data/bible-index.js   window.BIBLE_INDEX — 66 books: id, English + Arabic name,
                            testament, chapter count. Small; loaded up front for navigation.
  app/data/<lang>/bible/<ID>.js  one file per book, loaded on demand by a <script> tag
                            only when that book is opened.

The USFM book codes (GEN…REV) are exactly the OSIS-style ids the ESV API also uses, so the
two columns line up on reference with no mapping table beyond the display names below.

Run:  python3 pipeline/bible.py [--lang he]
"""
import json, os, re, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- where this language's generated data lives

# Which public-domain edition supplies each language's right-hand column. A list, because a
# language may need more than one: Hebrew's Old Testament is the ORIGINAL and arrives fully
# pointed, but there is no pointed public-domain Hebrew New Testament, so the two testaments
# come from different editions and say so.
SOURCES = {
    'ar': [{'dir': 'bible-vandyck', 'glob': '*arb-vd.usfm',
            'name': 'Van Dyck (1865)', 'covers': None}],
    'he': [{'dir': 'bible-wlc', 'glob': '*hboWLC.usfm',
            'name': 'Westminster Leningrad Codex', 'covers': 'OT'},
           {'dir': 'bible-delitzsch', 'glob': '*heb.usfm',
            'name': 'Delitzsch (1877)', 'covers': 'NT'}],
}
OUT_DIR = paths.data('bible')
INDEX = paths.data('bible-index.js')

# The WLC wraps every word in \w ... |strong="H7225" x-morph="HR/Ncfsa"\w*. The lemma and
# morphology are the CC BY-SA part of that edition and the app does its own lookups, so the
# markup is stripped and only the pointed word kept. It is worth knowing it is in the source:
# a future pass could take Strong's numbers straight from it rather than resolving them.
WORD_MARKUP = re.compile(r'\\w \*?([^|\\]*?)(?:\|[^\\]*?)?\\w\*')

# USFM id -> (English display name, testament). Canonical order is the file order (01..66).
BOOKS = {
    'GEN': ('Genesis', 'OT'), 'EXO': ('Exodus', 'OT'), 'LEV': ('Leviticus', 'OT'),
    'NUM': ('Numbers', 'OT'), 'DEU': ('Deuteronomy', 'OT'), 'JOS': ('Joshua', 'OT'),
    'JDG': ('Judges', 'OT'), 'RUT': ('Ruth', 'OT'), '1SA': ('1 Samuel', 'OT'),
    '2SA': ('2 Samuel', 'OT'), '1KI': ('1 Kings', 'OT'), '2KI': ('2 Kings', 'OT'),
    '1CH': ('1 Chronicles', 'OT'), '2CH': ('2 Chronicles', 'OT'), 'EZR': ('Ezra', 'OT'),
    'NEH': ('Nehemiah', 'OT'), 'EST': ('Esther', 'OT'), 'JOB': ('Job', 'OT'),
    'PSA': ('Psalms', 'OT'), 'PRO': ('Proverbs', 'OT'), 'ECC': ('Ecclesiastes', 'OT'),
    'SNG': ('Song of Solomon', 'OT'), 'ISA': ('Isaiah', 'OT'), 'JER': ('Jeremiah', 'OT'),
    'LAM': ('Lamentations', 'OT'), 'EZK': ('Ezekiel', 'OT'), 'DAN': ('Daniel', 'OT'),
    'HOS': ('Hosea', 'OT'), 'JOL': ('Joel', 'OT'), 'AMO': ('Amos', 'OT'),
    'OBA': ('Obadiah', 'OT'), 'JON': ('Jonah', 'OT'), 'MIC': ('Micah', 'OT'),
    'NAM': ('Nahum', 'OT'), 'HAB': ('Habakkuk', 'OT'), 'ZEP': ('Zephaniah', 'OT'),
    'HAG': ('Haggai', 'OT'), 'ZEC': ('Zechariah', 'OT'), 'MAL': ('Malachi', 'OT'),
    'MAT': ('Matthew', 'NT'), 'MRK': ('Mark', 'NT'), 'LUK': ('Luke', 'NT'),
    'JHN': ('John', 'NT'), 'ACT': ('Acts', 'NT'), 'ROM': ('Romans', 'NT'),
    '1CO': ('1 Corinthians', 'NT'), '2CO': ('2 Corinthians', 'NT'), 'GAL': ('Galatians', 'NT'),
    'EPH': ('Ephesians', 'NT'), 'PHP': ('Philippians', 'NT'), 'COL': ('Colossians', 'NT'),
    '1TH': ('1 Thessalonians', 'NT'), '2TH': ('2 Thessalonians', 'NT'), '1TI': ('1 Timothy', 'NT'),
    '2TI': ('2 Timothy', 'NT'), 'TIT': ('Titus', 'NT'), 'PHM': ('Philemon', 'NT'),
    'HEB': ('Hebrews', 'NT'), 'JAS': ('James', 'NT'), '1PE': ('1 Peter', 'NT'),
    '2PE': ('2 Peter', 'NT'), '1JN': ('1 John', 'NT'), '2JN': ('2 John', 'NT'),
    '3JN': ('3 John', 'NT'), 'JUD': ('Jude', 'NT'), 'REV': ('Revelation', 'NT'),
}

# USFM cleanup. Footnotes and cross-references carry their own text and must be removed
# whole; the character wrappers (\add, \nd, \w, \qs…) mark up text we keep, so drop only the
# marker and keep what it wrapped.
_NOTE = re.compile(r'\\(f|x|fe)\b.*?\\\1\*', re.S)         # \f ... \f*  and  \x ... \x*
_CHAR_PAIR = re.compile(r'\\(\+?[a-z0-9]+)\s(.*?)\\\1\*')  # \nd text\nd*  ->  text
_LONE = re.compile(r'\\[a-z0-9]+\*?')                      # any leftover lone marker
_WS = re.compile(r'\s+')

def clean(t):
    t = _NOTE.sub('', t)
    for _ in range(3):                                    # nested char styles
        t2 = _CHAR_PAIR.sub(lambda m: m.group(2), t)
        if t2 == t: break
        t = t2
    t = _LONE.sub('', t)
    return _WS.sub(' ', t).strip()

def parse_book(path):
    """-> (usfm_id, arabic_name, [[verse, ...], ...])  chapters are 1-indexed in the file."""
    text = WORD_MARKUP.sub(lambda m: m.group(1), open(path, encoding='utf-8').read())
    bid = re.search(r'\\id\s+(\S+)', text).group(1)
    hm = re.search(r'\\(?:toc2|h)\s+(.+)', text)
    arname = clean(hm.group(1)) if hm else BOOKS.get(bid, ('', ''))[0]

    chapters, cur, verse_parts, vnum = [], None, [], None
    def flush_verse():
        if vnum is not None:
            v = clean(''.join(verse_parts))
            while len(cur) < vnum - 1:                    # pad any skipped verse numbers
                cur.append('')
            if len(cur) == vnum - 1: cur.append(v)
            else: cur[vnum - 1] = (cur[vnum - 1] + ' ' + v).strip()

    for line in text.split('\n'):
        cm = re.match(r'\\c\s+(\d+)', line)
        if cm:
            flush_verse(); verse_parts, vnum = [], None
            cur = []; chapters.append(cur); continue
        if cur is None:                                    # header lines before \c 1
            continue
        vm = re.match(r'\\v\s+(\d+)\s?(.*)', line)
        if vm:
            flush_verse()
            vnum = int(vm.group(1)); verse_parts = [vm.group(2)]
        elif re.match(r'\\(p|m|q\d?|li\d?|pi\d?|b|pc|pmo|nb)\b', line):
            # poetry/paragraph line that continues the current verse
            verse_parts.append(' ' + re.sub(r'^\\\S+\s?', '', line))
        # \s (section heads), \d, \ms etc. are editorial — skip.
    flush_verse()
    return bid, arname, [c for c in chapters if c is not None]

def main():
    srcs = SOURCES[paths.LANG]
    parsed, edition = {}, {}
    for src in srcs:
        d = os.path.join(ROOT, 'data', src['dir'])
        paths_found = glob.glob(os.path.join(d, src['glob']))
        if not paths_found:
            print('%s USFM not found in data/%s/.' % (src['name'], src['dir']))
            print('Download it from ebible.org — see the header of this file.')
            return 1
        for path in paths_found:
            bid, arname, chapters = parse_book(path)
            if bid not in BOOKS:                          # front/back matter (FRT, GLO…)
                continue
            # A source may be limited to one testament. The Delitzsch package ships a whole
            # Bible, but its Old Testament is unpointed where the WLC's is the original text --
            # so it is used for the New only, and `covers` is what says so.
            if src['covers'] and BOOKS[bid][1] != src['covers']:
                continue
            parsed[bid] = (arname, chapters)
            edition[bid] = src['name']
    os.makedirs(OUT_DIR, exist_ok=True)

    index, tot_v = [], 0
    for bid, (en, test) in BOOKS.items():
        if bid not in parsed:
            print('  MISSING book:', bid); continue
        arname, chapters = parsed[bid]
        # .js, not .json, and assigning to a global rather than being fetched. A page opened
        # by double-click runs on file://, where fetch() of a sibling file is a CORS error --
        # so the Bible was the one section that silently failed when the app was used the way
        # the whole static-site design exists to allow. A <script> tag has no such restriction.
        with open(os.path.join(OUT_DIR, bid + '.js'), 'w', encoding='utf-8') as bf:
            bf.write('// GENERATED by pipeline/bible.py -- Van Dyck (1865), public domain.\n')
            bf.write('(window.BIB_BOOKS=window.BIB_BOOKS||{})["%s"]=' % bid)
            json.dump({'chapters': chapters}, bf, ensure_ascii=False, separators=(',', ':'))
            bf.write(';\n')
        nv = sum(len(c) for c in chapters); tot_v += nv
        index.append({'id': bid, 'en': en, 'ar': arname, 'test': test,
                      'ed': edition[bid],
                      'chapters': [len(c) for c in chapters]})

    with open(INDEX, 'w', encoding='utf-8') as f:
        f.write('// GENERATED by pipeline/bible.py — do not edit.\n')
        f.write('// Arabic: Van Dyck (1865), PUBLIC DOMAIN. English (ESV) is fetched at\n')
        f.write('// runtime with the user\'s own Crossway API key — never stored here.\n')
        f.write('window.BIBLE_INDEX = ')
        json.dump(index, f, ensure_ascii=False)
        f.write(';\n')

    import collections
    print('books: %d   verses: %d' % (len(index), tot_v))
    for name, n in collections.Counter(edition[b['id']] for b in index).most_common():
        print('  %-32s %2d books' % (name, n))
    print('sample GEN 1:1 ->', parsed['GEN'][1][0][0][:60])
    print('sample JHN 3:16 ->', parsed['JHN'][1][2][15][:60])
    print('-> %s + %s/*.js' % (os.path.relpath(INDEX, ROOT), os.path.relpath(OUT_DIR, ROOT)))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
