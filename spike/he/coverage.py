#!/usr/bin/env python3
"""The Stage A gate: what fraction of real modern Hebrew does the lexicon actually resolve?

Corpus is live Hebrew news RSS, for the same reason pipeline/daily_news.py uses news feeds --
it is exactly the text the Hebrew module would be ingesting on day one, it is unfiltered, and
nobody chose it to make the number look good.

The bar from the plan: >=90% of tokens get a lemma + gloss + POS. Below ~75%, stop and re-plan.

    python3 spike/he/coverage.py [--n 300] [--misses 40]
"""
import argparse
import collections
import os
import re
import ssl
import sys
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lex import Lexicon                                        # noqa: E402

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()

FEEDS = [("Ynet", "https://www.ynet.co.il/Integration/StoryRss2.xml"),
         ("Walla", "https://rss.walla.co.il/feed/1?type=main"),
         ("Israel Hayom", "https://www.israelhayom.co.il/rss.xml"),
         ("Maariv", "https://www.maariv.co.il/Rss/RssFeedsMivzakiChadashot")]

TAG = re.compile(r'<[^>]+>')
HEB_TOKEN = re.compile(r'[א-ת]+(?:["׳״\'][א-ת]+)*')
# An acronym written with gershayim (צה"ל, ח"כ) is a word, but it is not a LEXICAL word --
# it will never be in a dictionary. Counted separately rather than as a miss.
ACRONYM = re.compile(r'["״]')


def sentences(limit):
    out = []
    for name, url in FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hebrew-spike/1.0"})
            with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
                root = ET.fromstring(r.read())
        except Exception as e:
            print('  !! %s unreachable: %s' % (name, str(e)[:50]), file=sys.stderr)
            continue
        for item in root.iter('item'):
            for field in ('title', 'description'):
                t = TAG.sub(' ', item.findtext(field) or '')
                t = ' '.join(t.split())
                if len(t) > 25:
                    out.append((name, t))
        if len(out) >= limit:
            break
    return out[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=300)
    ap.add_argument('--misses', type=int, default=30)
    a = ap.parse_args()

    lx = Lexicon()
    print('lexicon: %d rows, %d distinct keys' % (len(lx.df), len(lx.by_form)))
    sents = sentences(a.n)
    print('corpus : %d sentences from %d feeds\n'
          % (len(sents), len({s for s, _ in sents})))

    prov = collections.Counter()
    miss = collections.Counter()
    tokens = 0
    for _, text in sents:
        for tok in HEB_TOKEN.findall(text):
            tokens += 1
            if ACRONYM.search(tok):
                prov['acronym (not lexical)'] += 1
                continue
            rec, p, cands = lx.resolve(tok)
            prov[p] += 1
            if p == 'unresolved':
                miss[tok] += 1

    print('tokens: %d\n' % tokens)
    order = ['wiktionary:exact', 'wiktionary:clitic', 'wiktionary:ktiv',
             'AMBIGUOUS-needs-resolution', 'acronym (not lexical)', 'unresolved']
    for k in order:
        c = prov.get(k, 0)
        print('  %-28s %6d  %5.1f%%' % (k, c, 100.0 * c / max(tokens, 1)))

    resolved = sum(prov.get(k, 0) for k in
                   ('wiktionary:exact', 'wiktionary:clitic', 'wiktionary:ktiv',
                    'AMBIGUOUS-needs-resolution'))
    lexical = tokens - prov.get('acronym (not lexical)', 0)
    print('\n  %-28s %6d  %5.1f%%  <- the gate' % ('GOT lemma+gloss+POS', resolved,
                                                   100.0 * resolved / max(lexical, 1)))
    print('  %-28s %6d  %5.1f%%' % ('of which need adjudication',
                                    prov.get('AMBIGUOUS-needs-resolution', 0),
                                    100.0 * prov.get('AMBIGUOUS-needs-resolution', 0)
                                    / max(lexical, 1)))
    if a.misses:
        print('\nmost frequent misses:')
        for w, c in miss.most_common(a.misses):
            print('  %4d  %s' % (c, w))


if __name__ == '__main__':
    main()
