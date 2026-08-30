#!/usr/bin/env python3
"""Select a Hebrew reading shelf from Project Ben-Yehuda -> texts/he/book-*.json.

Project Ben-Yehuda is 26,455 public-domain Hebrew works, and almost none of them are the Hebrew
this app teaches. That is the whole problem with the source and the reason this file measures
instead of browsing: the collection is early-twentieth-century literature, and its fables in
particular are biblical pastiche -- 45 vav-consecutive verbs per thousand words and 59-word
sentences, against the daily paper's 0 and 12. Shipping that under a spoken-Hebrew app because
it is free and real would be trading one kind of dishonesty for another.

So every text is scored against the app's own Hebrew before it is let in:

  * ARCHAIC markers per 1,000 words -- אשר as a relativizer, הנה, פן, טרם, אנכי, עתה.
  * VAV-CONSECUTIVE verbs per 1,000 -- ויאמר, ותלך. The single clearest tell; the paper has none.
  * average sentence length in words.

Measured medians, 120 texts per genre against the paper: fables 46.9 / 44.7 / 58.8, prose
27.2 / 9.3 / 14.7, drama 19.1 / 6.0 / 11.6, memoir 12.7 / 5.3 / 15.9 -- the paper 6.7 / 0.0 /
12.4. Drama and memoir are closest because they are dialogue and recollection, which is the
register this app is for. But the variance WITHIN a genre is larger than between genres, so the
gate is per text, not per genre.

And one more requirement, which turns out to matter more than any of them: the text must be
POINTED in the source. 32 of the 114 that pass the register gate are, and for those the vowels
on the page are Project Ben-Yehuda's, not ours -- the best provenance anywhere in the Hebrew
module, better than the news, where we derive them. Measured on 4,400 tokens of it: the source's
own pointing settles 51% of the ambiguity the annotator would otherwise have to send for
adjudication, taking a text from ~50% of tokens needing a decision to 29%.

    python3 pipeline/he_books.py --lang he            # what would be selected, and why
    python3 pipeline/he_books.py --lang he --write    # write texts/he/book-*.json
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')

DUMP = os.path.join(paths.ROOT, 'spike', 'he', 'benyehuda')
ZIP = os.path.join(DUMP, 'txt.zip')
CAT = os.path.join(DUMP, 'pseudocatalogue.csv')

WORD = re.compile(r'[֐-׿]+(?:["\'׳״][֐-׿]+)*')
NIQQUD = re.compile('[֑-ׇ]')
# Function words that mark the older literary register. Deliberately only the ones a modern
# speaker would NOT use: כי and גם are on both sides of the line, so they are not here.
ARCHAIC = {'אשר', 'הנה', 'פן', 'לבלתי', 'בטרם', 'למען', 'אולם', 'אנכי', 'הלא', 'עתה', 'כה',
           'טרם', 'זולת', 'הללו', 'ויהי', 'לכן', 'אך'}
VAV_CONSEC = re.compile(r'\bו[֑-ׇ]*[ית][֐-׿֑-ׇ]{2,}')

# The gate. Roughly twice the paper's archaism and no vav-consecutive to speak of; a text that
# clears this reads like something a modern Israeli wrote, which is the point.
MAX_ARCHAIC, MAX_VAV, MAX_SENTENCE = 12.0, 2.0, 15.0
MIN_POINTED = 0.90                       # the source's own vowels, or it is not this shelf
MIN_TOKENS, MAX_TOKENS = 300, 6000
GENRES = {'prose', 'drama', 'memoir'}

# Difficulty, and it is measured rather than judged: how long the sentences are and how much of
# the text is words the reader has already met by that phase. Bands are the app's own.
BANDS = [(11.0, 'beginner', 1), (14.0, 'intermediate', 2), (99.0, 'advanced', 3)]


def clean(text, title=''):
    """The dump is a transcription, not a data file: it keeps the page's own line breaks, its
    tabs, and its title line. Sentences have to be found in prose, so the layout goes first."""
    t = text.replace('\u00a0', ' ')
    t = re.sub(r'[ \t]*\n[ \t]*', '\n', t)
    t = re.sub(r'\n{2,}', '\n\n', t).strip()
    lines = [x for x in t.split('\n') if x.strip()]
    # the transcription repeats the title, and often the author under it
    head = NIQQUD.sub('', title).strip()
    while lines and (NIQQUD.sub('', lines[0]).strip() == head or len(WORD.findall(lines[0])) <= 3):
        lines.pop(0)
    return re.sub(r'\s+', ' ', ' '.join(lines)).strip()


def score(text):
    toks = WORD.findall(text)
    if not toks:
        return None
    sents = [s.strip() for s in re.split(r'(?<=[.!?׃])\s+', text) if len(WORD.findall(s)) > 2]
    if not sents:
        return None
    return {
        'tokens': len(toks),
        'pointed': sum(1 for w in toks if NIQQUD.search(w)) / len(toks),
        'archaic': 1000 * sum(1 for w in toks if NIQQUD.sub('', w) in ARCHAIC) / len(toks),
        'vav': 1000 * len(VAV_CONSEC.findall(text)) / len(toks),
        'sentence': statistics.mean(len(WORD.findall(s)) for s in sents),
        'sentences': sents,
    }


def passes(s):
    return (s and MIN_TOKENS <= s['tokens'] <= MAX_TOKENS and s['pointed'] >= MIN_POINTED
            and s['archaic'] <= MAX_ARCHAIC and s['vav'] <= MAX_VAV
            and s['sentence'] <= MAX_SENTENCE)


def band(s):
    for cutoff, name, shelf in BANDS:
        if s['sentence'] <= cutoff:
            return name, shelf
    return BANDS[-1][1], BANDS[-1][2]


def slug(mid):
    return 'book-by-%s' % mid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='write texts/he/book-*.json')
    ap.add_argument('--max', type=int, default=0, help='cap how many are written')
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if not os.path.exists(ZIP):
        raise SystemExit('!! no %s\n   Download txt.zip and pseudocatalogue.csv from\n'
                         '   github.com/projectbenyehuda/public_domain_dump/releases into %s'
                         % (ZIP, DUMP))

    cat = {r['ID']: r for r in csv.DictReader(open(CAT, encoding='utf-8'))}
    z = zipfile.ZipFile(ZIP)
    kept, seen_titles = [], set()
    for n in z.namelist():
        if not n.endswith('.txt'):
            continue
        mid = n.rsplit('/m', 1)[-1][:-4]
        c = cat.get(mid)
        if not c or (c.get('genre', '') or '').rsplit('.', 1)[-1] not in GENRES:
            continue
        s = score(clean(z.read(n).decode('utf-8', 'replace'), c['title']))
        if not passes(s):
            continue
        key = (c['title'].strip(), c['authors'].strip())
        if key in seen_titles:                 # the dump carries a few duplicate transcriptions
            continue
        seen_titles.add(key)
        kept.append((mid, c, s))

    kept.sort(key=lambda t: t[2]['sentence'])
    print('%d texts clear the register gate and are pointed in the source\n' % len(kept))
    print('%-34s %-20s %-13s %5s %6s %5s %5s' %
          ('title', 'author', 'level', 'tok', 'arch', 'vav', 'sent'))
    written = 0
    for mid, c, s in kept:
        name, shelf = band(s)
        print('%-34s %-20s %-13s %5d %6.1f %5.1f %5.1f'
              % (c['title'][:34], c['authors'][:20], name, s['tokens'],
                 s['archaic'], s['vav'], s['sentence']))
        if not a.write or (a.max and written >= a.max):
            continue
        doc = {
            'id': slug(mid), 'kind': 'book-chapter', 'dialect': 'he', 'level': name,
            'shelf': shelf, 'book': 'benyehuda', 'chapter': written + 1,
            'title': {'he': c['title'], 'en': c['title']},
            'book_title': {'he': 'ספרייה עברית', 'en': 'The Hebrew shelf'},
            'book_meta': {'work': c['title'], 'author': c['authors'],
                          'year': '', 'status': 'public domain — Project Ben-Yehuda volunteers',
                          'url': 'https://benyehuda.org' + (c.get('path') or '')},
            # Not "adapted by Claude". Every sentence is as Project Ben-Yehuda transcribed it,
            # vowels included, and the register numbers that let it in are on the record.
            'source': 'Project Ben-Yehuda — public domain, verbatim',
            'register': {'archaic_per_1k': round(s['archaic'], 1),
                         'vav_consecutive_per_1k': round(s['vav'], 1),
                         'avg_sentence_words': round(s['sentence'], 1),
                         'pointed': round(s['pointed'], 3)},
            'sentences': [{'ar': t.strip(), 'en': '', 'p': i // 6}
                          for i, t in enumerate(s['sentences'])],
        }
        json.dump(doc, open(paths.texts('%s.json' % slug(mid)), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        written += 1
    if a.write:
        print('\nwrote %d -> %s' % (written, os.path.relpath(paths.texts(''), paths.ROOT)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
