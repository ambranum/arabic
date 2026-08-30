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
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths          # noqa: E402
paths.require('he')

VERBS = paths.data('verbs.js')
OUT = paths.data('grammar.js')

NAMES = {'paal': 'פָּעַל', 'nifal': 'נִפְעַל', 'piel': 'פִּעֵל', 'pual': 'פֻּעַל',
         'hifil': 'הִפְעִיל', 'hufal': 'הֻפְעַל', 'hitpael': 'הִתְפַּעֵל'}


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
        L.append({'id': form, 'title': '%s — %s' % (NAMES[form], title), 'sub': sub,
                  'body': body, 'tables': tabs})

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
    print('%d lessons · %d tables · %d rows'
          % (len(L), sum(len(x['tables']) for x in L),
             sum(len(t['rows']) for x in L for t in x['tables'])))
    print('-> %s' % os.path.relpath(OUT, paths.ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
