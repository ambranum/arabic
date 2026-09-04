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

try:
    import pandas as pd
except ModuleNotFoundError:                       # the python3 first on PATH is not the one
    raise SystemExit(                             # that can run this pipeline. Say so, once.
        "\n!! This needs pandas, and the python3 at the front of your PATH does not have it.\n"
        "   Re-run the same command with the interpreter that does:\n"
        "       /usr/local/bin/python3 <the rest of your command>\n"
        "   (Homebrew's python3 is first on PATH here and carries no pandas; the framework\n"
        "    build at /usr/local/bin/python3 is the one the pipeline has always used.)\n")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phon import beat, phon, phon_stressed, respell, strip_cantillation   # noqa: E402

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
            # An ACRONYM sneaking in as a FORM of a spelled-out lemma. The lemma test above
            # catches מצ״ב and שו״ם, whose headword is the acronym; it does not catch ב״ה filed
            # under בָּרוּךְ הַשֵּׁם or ד״ר under דּוֹקְטוֹר. he_norm drops the gershayim, so those
            # arrive in the index spelled בה and דר -- and בה, "in it", is an everyday word that
            # was coming back from the daily paper as "baruch Hashem, thank God". 41 rows, 18 of
            # whose keys spell a real word, including כי. They are not reachable as acronyms
            # either: a text types the ASCII quote, which he_norm keeps, so ד"ר never matched
            # ד״ר anyway. The everyday ones are answered in he_curated.py, where an abbreviation
            # can also carry the reading its letters do not give.
            if '\u05f4' in form:
                continue
            seen.add((key, tuple(tags)))
            # ONE NOTATION FOR THE WHOLE LEXICON. Wiktionary's romanizations were taken
            # verbatim wherever it had one, which left 12% of the shipped rows in a different
            # system from the other 88%: kélev and khatúl beside kelev and xatul, bóqer with a
            # q where every other kuf is a k. A learner tapping two words in one sentence saw
            # two transliteration schemes, and the Sounds lesson that says ח and כ are one sound
            # written x was contradicted by every word card that spelled it kh.
            #
            # So the SEGMENTS are always phon.py's, derived from the pointing by one set of
            # rules, and Wiktionary supplies only the STRESS -- which is the one thing the
            # pointing does not determine and therefore the one thing worth looking up.
            # An UNPOINTED form whose lemma is pointed can borrow it. Wiktionary lists the
            # ktiv-male spelling as a form of the ktiv-haser headword and points only the
            # headword -- so בוקר "morning" and מילה "word" arrived with no vowels and no
            # reading, and lost every tiebreak to בּוֹקֵר "a cowboy" and מִילָה "circumcision",
            # which happen to be spelled full and pointed. respell() moves the lemma's vowels
            # onto the letters the form actually uses, and refuses when the lemma cannot spell
            # them, so nothing is invented: 1,531 of 26,072 unpointed rows, and the rest stay
            # unpointed because their lemma genuinely does not spell them.
            if not NIQQUD_RE.search(form):
                borrowed = respell(form, lemma) if NIQQUD_RE.search(lemma) else None
                # ...and only if it still SOUNDS like the word. Moving מָוֶת's vowels onto מוות
                # gives מָוֶות, which is the right spelling but which phon.py reads as "mavevt":
                # it takes the doubled vav for two consonants. The lemma's own reading is the
                # check -- if the respelled form does not say the same thing, the borrowing is
                # refused and the form stays unpointed, which is what it was.
                if borrowed and phon(borrowed) == phon(lemma):
                    form = borrowed
            pointed = bool(NIQQUD_RE.search(form))
            if pointed:
                ph = phon_stressed(form, beat(r))
                ph_src = 'derived:niqqud+stress' if r else 'derived:niqqud'
            elif r:
                ph, ph_src = r, 'wiktionary'      # nothing to derive from; the entry's own
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


def _share_stress(df):
    """Where any row knows where the beat falls, every row of that FORM gets it.

    Wiktionary romanizes some inflection rows and not others, so the same pointed word came out
    as kélev on one row and kelev on another -- and which one the app showed depended on which
    row happened to win a tiebreak. Stress is a property of the FORM, not of the tag set that
    happened to carry a transliteration, so one row saying mil'el settles it for all of them.
    """
    beats = {}
    for form, src, ph in zip(df['FORM'], df['PHON_SRC'], df['PHON']):
        if src == 'derived:niqqud+stress' and form not in beats:
            beats[form] = _stress_of(ph)
    ph, src = [], []
    for form, s0, p0 in zip(df['FORM'], df['PHON_SRC'], df['PHON']):
        n = beats.get(form)
        if n and s0.startswith('derived:niqqud'):
            ph.append(phon_stressed(form, n))
            src.append('derived:niqqud+stress')
        else:
            ph.append(p0)
            src.append(s0)
    df['PHON'], df['PHON_SRC'] = ph, src
    return df


def _stress_of(romanized):
    """Read the beat back off a romanization phon.py produced (an acute, or final)."""
    return beat(romanized)


XREF = re.compile(r'^\s*(defective|excessive|alternative|nonstandard|obsolete)\s+(spelling|form)\b'
                  r'|^\s*misspelling\b', re.I)
XREF_TARGET = re.compile(r'of\s+([\u0590-\u05ff][\u0590-\u05ff\u05f3\u05f4"\']*)')


def _follow_xrefs(df):
    """A cross-reference is not a definition. Where the lexicon only points, follow the pointer.

    2.4% of rows gloss a word by naming another spelling of it -- "excessive spelling of
    מִשְׁמֵשׁ", "misspelling of ויקי" -- and a learner who taps מישמשים wants "apricot", not a
    redirect. 527 keys answered that way. For 290 the lexicon has a real definition under the
    same key and _rank now prefers it; for the rest this reads the target out of the pointer,
    looks it up, and puts its definition in front. The pointer is kept, in parentheses, because
    it is true and it is the lexicon's own words: nothing is removed, the useful half is first.
    """
    real = {}
    for form, key, gloss in zip(df['FORM'], df['FORM_SEARCH'], df['GLOSS']):
        g = str(gloss or '')
        if g and not XREF.match(g):
            real.setdefault(key, g)
    out, n = [], 0
    for key, gloss in zip(df['FORM_SEARCH'], df['GLOSS']):
        g = str(gloss or '')
        m = XREF.match(g) and XREF_TARGET.search(g)
        if m and key not in real:
            hit = real.get(he_norm(m.group(1)))
            if hit:
                g = '%s (%s)' % (hit.rstrip('.'), g.rstrip('.'))
                n += 1
        out.append(g)
    df['GLOSS'] = out
    print('cross-references followed to a definition: %d' % n)
    return df


def main():
    df = _follow_xrefs(_share_stress(pd.DataFrame(rows())))
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
