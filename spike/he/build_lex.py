#!/usr/bin/env python3
"""kaikki-hebrew.jsonl -> hebrew_lex.parquet. The Hebrew answer to data/maknuune.parquet.

Columns mirror Maknuune's contract on purpose, so pipeline/ingest.py needs an adapter rather
than a rewrite:

    ID  LEMMA  LEMMA_SEARCH  FORM  FORM_SEARCH  PHON  POS  ANALYSIS  GLOSS
    BINYAN  PATTERN  ROOT  SOURCE

The one structural difference from Maknuune is that this table has a row per INFLECTED FORM,
not per lemma. Wiktionary ships the whole paradigm -- 204,051 form rows across 17,744 entries,
including every person of every tense for verbs and the possessed forms for nouns -- and Hebrew
running text is mostly inflected. Indexing lemmas alone would throw away the part that makes
lookup work.

That also means the pronunciation is largely LOOKED UP rather than computed. Wiktionary prints
a Modern Israeli romanization for the lemma; phon.py fills in the forms it doesn't cover. Both
are recorded in PHON_SRC so the app can tell a learner which one it is, the same way the Arabic
side distinguishes `lexicon:exact` from `derived:affix`.

    python3 spike/he/build_lex.py
"""
import json
import os
import re
import sys
import unicodedata

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phon import phon, strip_cantillation                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, 'kaikki-hebrew.jsonl')
OUT = os.path.join(HERE, 'hebrew_lex.parquet')

NIQQUD_RE = re.compile('[֑-ׇ]')
FINALS = str.maketrans('ךםןףץ', 'כמנפצ')

# Wiktionary's binyan codes, as they appear in the he-verb head template's first positional arg.
BINYAN = {'pa': 'paal', 'paal': 'paal',
          'ni': 'nifal', 'nif': 'nifal',
          'pi': 'piel', 'piel': 'piel',
          'pu': 'pual', 'pual': 'pual',
          'hi': 'hifil', 'hif': 'hifil',
          'hu': 'hufal', 'huf': 'hufal',
          'hit': 'hitpael', 'hitp': 'hitpael', "hitpu'al": 'hitpual'}


def binyan_of(d):
    """The binyan, from wherever this entry happens to keep it.

    Most verbs put it in the he-verb head template's first positional arg. Several hundred use
    a generic `head` template instead, which puts the LANGUAGE code there ("he") -- for those
    the code is in the he-conj inflection template's args. Reading only the first place loses
    544 of 2,084 paradigms to a blank binyan, which then propagates into the difficulty model.
    """
    ht = (d.get('head_templates') or [{}])[0].get('args', {})
    hit = BINYAN.get(str(ht.get('1', '')).lower())
    if hit:
        return hit
    for it in d.get('inflection_templates') or []:
        hit = BINYAN.get(str((it.get('args') or {}).get('1', '')).lower())
        if hit:
            return hit
    return ''

# Tag sets Wiktionary emits that are not a form of the word.
SKIP_TAGS = {'romanization', 'table-tags', 'inflection-template', 'class',
             'error-unrecognized-form'}


def he_norm(s):
    """The Hebrew arNorm: strip pointing, fold final letters, drop the joiner.

    Deliberately NOT folding ktiv male/haser (the optional yod and vav of unpointed spelling).
    That is a real ambiguity -- folding it would merge distinct words -- so it is handled as a
    second lookup attempt in lex.py rather than baked into the key.
    """
    s = unicodedata.normalize('NFC', s or '')
    s = NIQQUD_RE.sub('', strip_cantillation(s))
    s = s.replace('־', ' ').replace('״', '').replace('׳', '')
    return s.translate(FINALS).strip()


def _analysis(pos, tags):
    """POS:features, in the shape ingest.py already parses for Arabic."""
    keep = [t for t in tags if t not in SKIP_TAGS]
    return (pos or 'X').upper() + (':' + '.'.join(sorted(keep)) if keep else '')


def rows():
    for i, line in enumerate(open(DUMP, encoding='utf-8')):
        d = json.loads(line)
        pos = d.get('pos') or 'x'
        ht = (d.get('head_templates') or [{}])[0].get('args', {})
        lemma = ht.get('wv') or next(
            (f['form'] for f in d.get('forms', []) if 'canonical' in (f.get('tags') or [])),
            d.get('word'))
        gloss = next((s['glosses'][0] for s in d.get('senses', []) if s.get('glosses')), '')
        if not lemma or not gloss:
            continue
        # Two kinds of Wiktionary entry are not words and must never become lookup candidates.
        # A ROOT entry (ה־י־ה) is a morphological abstraction; an ACRONYM (מצ״ב, שו״ם) is
        # spelled with gershayim and is caught upstream by its punctuation. Left in, they turn
        # every common word into a false ambiguity -- היה matched both הָיָה and the root ה־י־ה,
        # and מצב matched both מַצָּב and מצ״ב.
        if pos == 'root' or '״' in lemma:
            continue
        # The romanization Wiktionary gives is for the LEMMA only.
        rom = next((f['form'] for f in d.get('forms', [])
                    if 'romanization' in (f.get('tags') or [])), None)
        binyan = binyan_of(d) if pos == 'verb' else ''
        # he-verb templates carry the root radicals as פ/ע/ל args.
        root = '.'.join(x for x in (ht.get('פ'), ht.get('ע'), ht.get('ל')) if x) or ''
        pattern = ht.get('pat', '') or ''

        seen = set()
        # the lemma itself, first, so it wins on ties
        cand = [(lemma, [], rom, 'wiktionary:lemma')]
        for f in d.get('forms', []):
            tags = f.get('tags') or []
            form = (f.get('form') or '').strip()
            if not form:
                continue
            # The Hebrew infinitive is filed by wiktextract as `error-unrecognized-form`.
            # Skipping the whole tag would drop לכתוב, לדבר, לעשות, להיות -- four of the most
            # common shapes in running text -- so it is relabelled here instead. Identifiable
            # without guessing: a verb entry, tagged as the error, beginning with ל-.
            if set(tags) & SKIP_TAGS:
                if not (pos == 'verb' and 'error-unrecognized-form' in tags
                        and form.startswith('ל')):
                    continue
                tags = ['infinitive']
            cand.append((form, tags, None, 'wiktionary:form'))
        for form, tags, r, src in cand:
            form = form.strip()
            key = he_norm(form)
            if not key or (key, tuple(tags)) in seen:
                continue
            if re.search(r'[A-Za-z0-9]', form) or not re.search(r'[א-ת]', form):
                continue
            seen.add((key, tuple(tags)))
            pointed = bool(NIQQUD_RE.search(form))
            if r:
                ph, ph_src = r, 'wiktionary'
            elif pointed:
                ph, ph_src = phon(form), 'derived:niqqud'
            else:
                ph, ph_src = '', 'none:unpointed'
            yield {
                'ID': '%d-%d' % (i, len(seen)),
                'LEMMA': lemma, 'LEMMA_SEARCH': he_norm(lemma),
                'FORM': form, 'FORM_SEARCH': key,
                'PHON': ph, 'PHON_SRC': ph_src,
                'POS': pos, 'ANALYSIS': _analysis(pos, tags), 'GLOSS': gloss,
                'BINYAN': binyan, 'PATTERN': pattern, 'ROOT': root, 'SOURCE': src,
            }


def main():
    df = pd.DataFrame(rows())
    df.to_parquet(OUT, index=False)
    print('-> %s  (%.1f MB)' % (OUT, os.path.getsize(OUT) / 1e6))
    print('rows            %7d' % len(df))
    print('distinct lemmas %7d' % df['LEMMA_SEARCH'].nunique())
    print('distinct keys   %7d' % df['FORM_SEARCH'].nunique())
    print('\nby POS:')
    for p, c in df['POS'].value_counts().head(9).items():
        print('  %-10s %7d' % (p, c))
    print('\npronunciation source:')
    for p, c in df['PHON_SRC'].value_counts().items():
        print('  %-18s %7d  (%.0f%%)' % (p, c, 100 * c / len(df)))
    print('\nverbs with a binyan: %d' % (df['BINYAN'] != '').sum())
    print('rows with a root   : %d' % (df['ROOT'] != '').sum())


if __name__ == '__main__':
    main()
