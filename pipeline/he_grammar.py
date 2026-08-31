#!/usr/bin/env python3
"""Build app/data/he/grammar.js — the binyan system, taught from the verb data.

The Arabic grammar module mines its examples from the corpus: twenty structures, thirty real
sentences each, out of 384 texts. Hebrew has eighteen sentences, so that road is closed until the
daily paper has run for a month or two, and pretending otherwise would mean writing the examples.

But Hebrew's central grammar is not a sentence pattern at all. It is the BINYANIM -- seven fixed
shapes a three-letter root is poured into, each with its own job -- and the evidence for it is
already in the repo, looked up: 2,084 pointed paradigms carrying a root, a binyan and a gloss,
1,272 distinct roots, 502 of them attested in two binyanim and 169 in three or more. שָׁמַר "to
guard" beside נִשְׁמַר "to be guarded" is not an example somebody wrote; it is two rows of the verb
list with the same root.

So the prose here is curated teaching and every WORD in every table is mined. A lesson whose
table comes up short of its minimum stops the build rather than shipping a thin one.

    python3 pipeline/he_grammar.py --lang he
"""
import argparse
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths          # noqa: E402
paths.require('he')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import lex as helex          # noqa: E402

VERBS = paths.data('verbs.js')
OUT = paths.data('grammar.js')

# How many real sentences a lesson may carry, and how many may come from one text. The cap per
# text is the point: six sentences from one story is one story, not six examples.
EXAMPLES, PER_TEXT, PER_WORD, MIN_EXAMPLES = 12, 2, 3, 6
# Spoken register first. The Ben-Yehuda shelf is real Hebrew and it is published prose; a
# grammar lesson about how people speak should reach for the stories and the paper first and
# let the books fill what is left.
KIND_ORDER = {'story': 0, 'news': 0, 'book-chapter': 1}

NAMES = {'paal': 'פָּעַל', 'nifal': 'נִפְעַל', 'piel': 'פִּעֵל', 'pual': 'פֻּעַל',
         'hifil': 'הִפְעִיל', 'hufal': 'הֻפְעַל', 'hitpael': 'הִתְפַּעֵל'}


def one_reading(lex, cache={}):
    """-> a test: does the lexicon read this word's letters exactly one way?

    Nothing else is evidence of a binyan. Hebrew is full of the other kind, and the corpus
    inherits every one of them: שם is the paal verb שָׂם "put" and it is also the ordinary word
    for "there"; לשוק is לְשַׁוֵּק "to market" and it is ל־ + שׁוּק "to the market", which is what
    the story said and not how it was annotated; גינה is "he denounced" and it is "a garden".

    Three ways a second reading hides, and all three are checked. A PROCLITIC: לשוק is
    לְשַׁוֵּק "to market" and it is ל־ + שׁוּק "to the market", which is what the story said and
    not how it was annotated. A DEFECTIVE SPELLING: גינה matched the verb גִּנָּה "to denounce"
    exactly, because that entry lists its full spelling, while the noun גִּנָּה "a garden" lists
    only גנה and never got the chance -- an exact match wins before the skeleton tier runs. And
    plain HOMOGRAPHY: שם is the paal verb שָׂם "put" and the ordinary word for "there".

    lex.alt_readings answers only the first, and answers it for a different purpose: it compares
    LEMMA_SEARCH, the consonantal skeleton, so that בְּחִירוֹת listed twice counts once -- and by
    that rule the piel שִׁוֵּק and the noun שׁוּק, sharing the skeleton שוק, counted as one word.
    Here the pair is (pointed lemma, part of speech), which is too strict to interrupt a human
    over and right for deciding what a lesson may point at.
    """
    from build_lex import he_norm

    def ident(recs):
        return {(r['LEMMA'], str(r['POS'])) for r in (recs or [])}

    def test(surface):
        if surface in cache:
            return cache[surface]
        recs, _prov, cut = lex.look(surface)
        ok = bool(recs) and not cut and len(lex.readings(recs)) == 1
        if ok:
            key, mine = he_norm(surface), ident(recs)
            others = list(lex._spellable(key, lex.by_skeleton.get(helex.MATRES.sub('', key))))
            present = any('present' in str(r['ANALYSIS']) for r in recs)
            for stem, strip in lex.stems(key)[1:]:
                if not strip.endswith('-'):        # a suffix strip is a different question
                    continue
                # The one prefix a binyan supplies itself. Piel, hitpael and hifil build their
                # present tense with מ־ and nothing else -- מדבר, מסתכל, מגיע -- so a מ־ in
                # front of a present-tense reading is that binyan's own letter, not a
                # preposition that happens to be there. Without this the filter deletes the
                # participle, which is most of how these three binyanim are actually spoken,
                # and piel loses its lesson to מ־ + a noun that nobody said.
                #
                # Only מ־ and only on a present tense. ל־ gets no such pass, which is what
                # keeps לשוק ("to the market", annotated as לְשַׁוֵּק "to market") out.
                if present and strip == 'מ-':
                    continue
                peeled, _p, c = lex.look(stem)
                if not c:
                    others += peeled
            ok = not (ident(others) - mine)
        cache[surface] = ok
        return ok
    return test


def corpus_examples(binyan_of):
    """Real sentences for each binyan, from the app's own annotated Hebrew.

    The Arabic grammar module does this from 384 texts and takes thirty a lesson. Hebrew has 73
    and takes twelve, which is what there is -- and for the two passives there is much less than
    that, because פועל and הופעל are genuinely rare in speech. That is not a gap in the corpus,
    it is the fact the lesson is teaching, so the count is shown rather than padded.
    """
    sole = one_reading(helex.Lexicon())
    by_binyan, raw = collections.defaultdict(list), collections.Counter()
    for f in sorted(glob.glob(paths.build('*', 'text.json'))):
        d = json.load(open(f, encoding='utf-8'))
        rank = KIND_ORDER.get(d.get('kind'), 2)
        for sn in d['sentences']:
            if not sn.get('en'):
                continue
            hits = collections.defaultdict(list)
            for w in sn['words']:
                b0 = binyan_of.get(w.get('lemma'))
                if b0:
                    raw[b0] += 1        # before any filtering: how often the binyan turns up
                # The pointing has to come from the very lexicon row that names the binyan.
                # Any other source means the row was chosen on consonants alone, and a
                # consonantal match is not evidence of a binyan:
                # במוצאי (ב + the construct of מוֹצָא) came back as the hufal הוּצָא, and
                # מִשֹּׁרֶשׁ ('from the root') as a pual present מְשֹׁרָשׁ. Both spell the same
                # letters as a real passive verb and neither is one.
                if w.get('vocalized_from') != 'lexicon' or not sole(w['surface']):
                    continue
                b = binyan_of.get(w.get('lemma'))
                if b:
                    hits[b].append(w['surface'])
            for b, surfaces in hits.items():
                by_binyan[b].append((rank, len(sn['words']), d['id'],
                                     d['title'].get('en') or d['id'], sn['ar'], sn['en'],
                                     sorted(set(surfaces))))
    out = {}
    for b, rows in by_binyan.items():
        rows.sort(key=lambda r: r[:2])          # spoken first, then shortest
        picked, per, said, word = [], collections.Counter(), set(), collections.Counter()
        for _rank, _n, tid, title, ar, en, hi in rows:
            # The paper reruns a story the next morning with the tail reworded, so the same
            # sentence arrives twice under two ids and is not string-equal. Six opening words
            # is what a rerun keeps. And one lesson showing הגעתי six times teaches less than
            # three different verbs do.
            head = ' '.join(ar.split()[:6])
            if per[tid] >= PER_TEXT or head in said or any(word[x] >= PER_WORD for x in hi):
                continue
            said.add(head)
            for x in hi:
                word[x] += 1
            per[tid] += 1
            picked.append({'ar': ar, 'en': en, 'src': tid, 'title': title, 'hi': hi})
            if len(picked) >= EXAMPLES:
                break
        out[b] = picked
    return out, raw


def load():
    s = open(VERBS, encoding='utf-8').read()
    d = json.loads(s[s.index('window.VERBS = ') + len('window.VERBS = '):s.rindex(';')])
    return d['verbs']


def rom(v):
    """The romanization of THIS lemma, or nothing.

    Only a slot whose Hebrew is the citation form itself will do. Taking whichever slot happened
    to have one printed lheraot under נִרְאָה -- the infinitive's reading beneath the past
    tense's spelling, which is a pronunciation guide to a different word.
    """
    for k in ('past', 'pres', 'inf'):
        slot = v.get(k) or {}
        if slot.get('caphi') and slot.get('ar') == v.get('lemma'):
            return slot['caphi']
    return ''


LEAD = ('To ', 'A ', 'An ', 'The ')


def gloss(v):
    g = str(v.get('gloss') or '').strip()
    for sep in (';', ' (', ':'):
        g = g.split(sep)[0].strip()
    g = g.rstrip('.').strip()
    # Wiktionary capitalises some glosses and not others; in a table of ten the difference reads
    # as meaning. Only the leading article or infinitive marker is touched.
    for w in LEAD:
        if g.startswith(w):
            g = w.lower() + g[len(w):]
    return g


def usable(v):
    return bool(v.get('lemma') and rom(v) and gloss(v) and len(gloss(v)) <= 38)


SEEN = set()


def rank(v):
    """Central verbs first, but not the SAME central verbs nine times.

    Ranking by root spread alone put פ.ט.ר, פ.ש.ט and ש.ל.ט at the top of every table in the
    module, which reads as a very small language. A root already spent in an earlier table goes
    to the back, so each lesson mostly brings new words while still preferring the roots the
    language leans on.

    "Shortest gloss" alone put פִּהֵק "yawn" and לִבְלֵב "to bud" at the top of the piel table,
    which is what optimising for brevity gets you. The better proxy for a verb worth showing is
    its ROOT: a root the dictionary has in four binyanim is a root the language leans on, and its
    verbs are the ones a learner meets. Nothing here is frequency data -- there is none for
    Hebrew in this repo -- but it beats counting characters.
    """
    return ((v.get('root') or '') in SEEN, -v.get('_spread', 0),
            0 if v.get('hasConj') else 1, len(gloss(v)))


def row(v):
    return [v['lemma'], rom(v), gloss(v)]


def pairs(by_root, a, b, n):
    """Roots attested in BOTH binyanim: the pattern shown twice over the same three letters.

    A pair whose two glosses say the same thing -- "to fail → to fail", "to boil → to boil" --
    is worse than no pair: it shows the reader a change of shape and no change of meaning, which
    is the opposite of the lesson. Those are dropped, not reordered.
    """
    out = []
    for root, forms in by_root.items():
        if a in forms and b in forms and usable(forms[a]) and usable(forms[b]):
            ga, gb = gloss(forms[a]).lower(), gloss(forms[b]).lower()
            if ga == gb or ga in gb or gb in ga:
                continue
            out.append((root, forms[a], forms[b]))
    out.sort(key=lambda t: (rank(t[1]), rank(t[2])))
    got = out[:n]
    SEEN.update(root for root, _, _ in got)
    return got


def pair_table(title, got):
    return {'title': title,
            'rows': [[' · '.join((x['lemma'], y['lemma'])), ' · '.join((rom(x), rom(y))),
                      '%s → %s' % (gloss(x), gloss(y))] for _, x, y in got]}


def plain_table(title, verbs, n):
    got = sorted([v for v in verbs if usable(v)], key=rank)[:n]
    SEEN.update(v.get('root') or '' for v in got)
    return {'title': title, 'rows': [row(v) for v in got]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    ap.parse_args()

    vb = load()
    n_texts = len(glob.glob(paths.build('*', 'text.json')))
    n_sents = sum(len(json.load(open(f, encoding='utf-8'))['sentences'])
                  for f in glob.glob(paths.build('*', 'text.json')))
    by_form = collections.defaultdict(list)
    by_root = collections.defaultdict(dict)
    for v in vb:
        by_form[v['form']].append(v)
        r = v.get('root') or ''
        if len([c for c in r if c not in '.\u05be ']) >= 3 and usable(v):
            by_root[r].setdefault(v['form'], v)
    # How many binyanim this verb's root is attested in -- the centrality proxy rank() uses.
    for v in vb:
        v['_spread'] = len(by_root.get(v.get('root') or '', ()))

    binyan_of = {v['lemma']: v['form'] for v in vb if v.get('form')}
    ex, raw = corpus_examples(binyan_of)

    rich = sorted((r for r, f in by_root.items() if len(f) >= 4),
                  key=lambda r: -len(by_root[r]))[:3]
    SEEN.update(rich)

    L = []

    # 1 -----------------------------------------------------------------------------------
    tabs = []
    for r in rich:
        forms = by_root[r]
        tabs.append({'title': 'The root %s' % r,
                     'rows': [row(forms[b]) for b in NAMES if b in forms]})
    L.append({
        'id': 'root-binyan', 'title': 'Roots and patterns',
        'sub': 'ש.מ.ר — one root, seven shapes',
        'body': [
            'A Hebrew word is two things at once: a <b>root</b> of (usually) three consonants '
            'that carries the meaning, and a <b>pattern</b> of vowels and prefixes poured around '
            'it that says what kind of word it is and what is being done to whom. ש.מ.ר is about '
            'guarding; שָׁמַר is "he guarded", נִשְׁמַר is "it was guarded", שִׁמֵּר is "he '
            'preserved", הִשְׁתַּמֵּר is "it was kept".',
            'For verbs there are seven of these patterns, called <b>binyanim</b> — literally '
            '"buildings". Learning them is the single highest-value thing in Hebrew grammar, '
            'because once you can see the root through the pattern, a word you have never met '
            'is half known already. Each table below is one root in every binyan the dictionary '
            'has it in.',
        ], 'tables': tabs})

    # 2..8 --------------------------------------------------------------------------------
    SPEC = [
     ('paal', 'The plain verb', 'שָׁמַר — he guarded',
      ['<b>פָּעַל</b> (also called קַל, "light") is the plain, basic verb: no prefix, two vowels, '
       'nothing done to it. Most of the oldest and commonest verbs in the language live here — '
       'to eat, to write, to go, to guard.',
       'It is the shape to measure the others against. Everything below is פעל plus something.'],
      None),
     ('nifal', 'What happens to you', 'שָׁמַר → נִשְׁמַר — guard → be guarded',
      ['<b>נִפְעַל</b> puts a נ on the front and is, most often, the passive of פעל: what someone '
       'does to you rather than what you do. It also covers a middle ground English handles with '
       '"get" — נִכְנַס "got in", נִשְׁבַּר "broke" (by itself).',
       'Each pair below is one root in both: the same three letters, the doing and the '
       'being-done-to.'],
      ('paal', 'nifal')),
     ('piel', 'Doing it to something', 'שָׁמַר → שִׁמֵּר — guard → preserve',
      ['<b>פִּעֵל</b> doubles the middle consonant (that is the dagesh) and is the workhorse of '
       'modern Hebrew: it makes verbs transitive, intensive, or simply new. Nearly every borrowed '
       'or invented verb lands here — טִלְפֵּן "phoned", סִמֵּס "texted".',
       'The relationship to פעל is real but loose, which is why the pairs below are worth reading '
       'as pairs rather than as a rule.'],
      ('paal', 'piel')),
     ('pual', 'The piel, done to you', 'שִׁמֵּר → שֻׁמַּר — preserve → be preserved',
      ['<b>פֻּעַל</b> is פיעל made passive, and it is nearly always exactly that: if you know the '
       'piel, you know the pual. It is uncommon in speech outside the present tense, where it '
       'supplies a great many everyday adjectives — מְבֻשָּׁל "cooked", מְסֻדָּר "tidy".'],
      ('piel', 'pual')),
     ('hifil', 'Making it happen', 'נִכְנַס → הִכְנִיס — go in → bring in',
      ['<b>הִפְעִיל</b> takes a ה and a long i, and it is the <b>causative</b>: not doing the '
       'thing, but making it happen. If פעל is "he ate", הפעיל is "he fed"; if the plain verb is '
       '"go in", this one is "bring in".',
       'It is the second-biggest binyan in the language and the one that most often surprises '
       'learners, because English usually has a completely different word for the causative.'],
      ('paal', 'hifil')),
     ('hufal', 'Made to happen to you', 'הִכְנִיס → הֻכְנַס — bring in → be brought in',
      ['<b>הֻפְעַל</b> is הפעיל made passive, and like פועל it is a mechanical partner: the '
       'causative done to you. Rare in speech, common in the news, which is where you will meet '
       'it first — הֻחְלַט "it was decided", הֻפְסַק "it was stopped".'],
      ('hifil', 'hufal')),
     ('hitpael', 'Doing it to yourself', 'שִׁמֵּר → הִשְׁתַּמֵּר — preserve → be preserved',
      ['<b>הִתְפַּעֵל</b> takes a הת prefix and is reflexive or reciprocal: to yourself, or to each '
       'other. הִתְלַבֵּשׁ "got dressed", הִתְכַּתְּבוּ "they wrote to each other", הִתְרַגֵּשׁ "got '
       'excited".',
       'A spelling quirk worth knowing before it confuses you: when the root starts with a '
       'sibilant, the ת swaps places with it — הִשְׁתַּמֵּר, not הִתְשַׁמֵּר.'],
      ('piel', 'hitpael')),
    ]
    for form, title, sub, body, pair in SPEC:
        if pair:
            got = pairs(by_root, *pair, 10)
            if len(got) < 6:
                raise SystemExit('!! %s: only %d %s→%s pairs' % (form, len(got), *pair))
            tabs = [pair_table('%s → %s, same root' % (NAMES[pair[0]], NAMES[pair[1]]), got)]
        else:
            tabs = []
        tabs.append(plain_table('%s verbs' % NAMES[form], by_form[form], 10))
        if len(tabs[-1]['rows']) < 6:
            raise SystemExit('!! %s: only %d verbs' % (form, len(tabs[-1]['rows'])))
        les = {'id': form, 'title': '%s — %s' % (NAMES[form], title), 'sub': sub,
               'body': list(body), 'tables': tabs}
        found = ex.get(form, [])
        # Below the floor the examples are not shown at all. With four or five matches in a
        # 1,100-sentence corpus, an individual one is about as likely to be a mis-annotation as
        # a real instance -- and a lesson that illustrates itself with a mistake is worse than
        # one that says plainly how little there was.
        if len(found) >= MIN_EXAMPLES:
            les['examples'] = found
        if len(found) < MIN_EXAMPLES:
            # Say the real number, not the number that survived. Everything this app has in
            # Hebrew turns up eight פועל verbs and six הופעל ones, and every one of them rests
            # on a spelling that reads more than one way -- which is itself the point, since a
            # binyan nobody speaks is a binyan you only ever meet in a word you can misread.
            les['body'].append(
                'Everything this app has in Hebrew — %d texts, %d sentences — turns up '
                '<b>%d</b> with a %s verb in it, and %s. So this lesson has its tables and no '
                'sentences. That is not a gap in the reading. It is how rare this binyan is '
                'once people are actually speaking.'
                % (n_texts, n_sents, raw[form], NAMES[form],
                   'not one of them is spelled a way that can only be read as that verb'
                   if raw[form] else 'that is all of them'))
        L.append(les)

    # 9 -----------------------------------------------------------------------------------
    JOB = {'paal': 'plain, basic', 'nifal': 'passive of פעל', 'piel': 'transitive / intensive',
           'pual': 'passive of פיעל', 'hifil': 'causative', 'hufal': 'passive of הפעיל',
           'hitpael': 'reflexive / reciprocal'}
    rows = []
    for b in NAMES:
        best = sorted([v for v in by_form[b] if usable(v)], key=rank)[:1]
        if best:
            rows.append(['%s  ·  %s' % (NAMES[b], best[0]['lemma']),
                         rom(best[0]), '%s — %s' % (JOB[b], gloss(best[0]))])
    L.append({
        'id': 'binyan-map', 'title': 'The seven, on one page',
        'sub': 'which shape does which job',
        'body': ['Four of the seven come in active/passive pairs — פעל/נפעל, פיעל/פועל, '
                 'הפעיל/הופעל — and התפעל stands on its own. That is the whole system, and it is '
                 'worth memorising the table below the way you would memorise a verb ending.',
                 'The counts are what this app actually has a full paradigm for, so you can see '
                 'which binyanim you will meet most.'],
        'tables': [{'title': 'The seven binyanim', 'rows': rows},
                   {'title': 'How many of each are in the verb list',
                    'rows': [[NAMES[b], str(len(by_form[b])), JOB[b]] for b in NAMES]}]})

    doc = {
        'intro': "Hebrew's central grammar is not a sentence pattern — it is the <b>binyanim</b>, "
                 'the seven shapes a three-letter root is poured into. Learn to see the root '
                 'through the shape and a word you have never met is half known. Every word in '
                 'the tables below is a real dictionary entry: the pairs are one root the '
                 'lexicon happens to have in both binyanim, not examples anyone wrote.',
        'lessons': L,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// GENERATED by pipeline/he_grammar.py -- do not edit by hand.\n')
        f.write('// Prose is curated teaching; every WORD in every table is mined from\n')
        f.write('// app/data/he/verbs.js, which is itself looked up in the lexicon.\n')
        f.write('window.GRAMMAR = ')
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write(';\n')
    print('%d lessons · %d tables · %d rows · %d real sentences from %d texts'
          % (len(L), sum(len(x['tables']) for x in L),
             sum(len(t['rows']) for x in L for t in x['tables']),
             sum(len(x.get('examples', [])) for x in L),
             len({e['src'] for x in L for e in x.get('examples', [])})))
    print('-> %s' % os.path.relpath(OUT, paths.ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
