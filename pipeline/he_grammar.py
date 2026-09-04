#!/usr/bin/env python3
"""Build app/data/he/grammar.js — twenty lessons: eleven on the sentence, nine on the binyanim.

The sentence half came second and could not have come first. This module used to open by saying
that the Arabic side mines its examples from 384 texts while Hebrew had eighteen sentences, so
that road was closed — true when it was written, and false now: the Hebrew corpus is 400 texts
and 9,301 sentences with an English pair, which is enough to show a pattern rather than assert
it. See SENT_SPEC below for the eleven and for what each matcher counts as evidence.

The other half is the BINYANIM -- seven fixed
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



# ==========================================================================================
# THE SENTENCE LESSONS. The nine binyan lessons below teach how a WORD is built. These eleven
# teach how a SENTENCE is built, and until now Hebrew had none of them: a learner could
# conjugate שָׁמַר through seven shapes and had never been shown how to say "I want", "there is"
# or "the one that".
#
# The reason they were missing is in this module's own docstring, and it expired. Mining
# examples needs a corpus, Hebrew had eighteen sentences when the binyan lessons were written,
# and it now has 9,301 with an English pair. So these lessons are built the way the Arabic ones
# are: the prose and the closed-class paradigm tables are hand-written, and every EXAMPLE
# SENTENCE is a real sentence out of the app's own annotated Hebrew, chosen by a matcher.
#
# A matcher is handed one sentence's word list and returns the surfaces to highlight, or []
# for no match. It answers "does this sentence SHOW the pattern", never "is this sentence
# correct" -- the corpus is the authority on the second question and this file is not.

SUBJ_PRON = {'אני', 'אתה', 'את', 'הוא', 'היא', 'אנחנו', 'אתם', 'אתן', 'הם', 'הן'}
L_PRON = {'לי', 'לך', 'לו', 'לה', 'לנו', 'לכם', 'לכן', 'להם', 'להן'}
SHEL = {'של', 'שלי', 'שלך', 'שלו', 'שלה', 'שלנו', 'שלכם', 'שלכן', 'שלהם', 'שלהן'}
QWORD = {'מה', 'מי', 'איפה', 'למה', 'מתי', 'איך', 'כמה', 'איזה', 'איזו', 'לאן', 'מאיפה'}
YESH = {'יש', 'אין'}


def _pos(w):
    return str(w.get('analysis') or '').split(':')[0]


def _cut(w):
    return str(w.get('_cut') or '')


def _bare(s):
    """The word without a leading vav, which is how half of Hebrew narration starts."""
    return s[1:] if len(s) > 2 and s[0] == 'ו' else s


def m_nominal(ws, _ar):
    """No verb anywhere, and something doing the describing. Hebrew's present tense IS a
    participle and is tagged VERB, so 'no VERB in the sentence' is exactly the sentence that
    has left the copula out -- הבית גדול, 'the house big'.

    יש and אין are refused. They are not tagged VERB and so they sail through the test above,
    but יש לנו חתול קטן is the HAVING pattern with an adjective in it, and showing it here
    teaches the reader that leaving out 'is' looks like יש, which is the opposite of true."""
    if len(ws) < 4 or any(_pos(w) == 'VERB' for w in ws):
        return []
    if any(_bare(w['surface']) in YESH for w in ws):
        return []
    adj = [w['surface'] for w in ws if _pos(w) == 'ADJ']
    return adj[:1] if adj else []


def m_article(ws, _ar):
    """The article is not a word, it is a letter glued on, so the evidence for it is the
    peeler's own answer: this token matched only after ה- came off the front."""
    return [w['surface'] for w in ws if _cut(w) in ('ה-', 'וה-')][:2]


def m_pron(ws, _ar):
    return [w['surface'] for w in ws if _bare(w['surface']) in SUBJ_PRON][:1]


def m_yesh(ws, _ar):
    """יש / אין on their own -- existence. The having lesson takes the ones with a ל־ pronoun,
    so this one refuses them, or the two lessons would show the same twelve sentences."""
    hit = [w['surface'] for w in ws if _bare(w['surface']) in YESH]
    if not hit or any(_bare(w['surface']) in L_PRON for w in ws):
        return []
    return hit[:1]


def m_having(ws, _ar):
    """יש plus a ל־ pronoun, and they have to be NEAR each other: יש לי is the construction,
    while a יש at the start of a sentence and a להם at the end of it are two separate facts."""
    for i, w in enumerate(ws):
        if _bare(w['surface']) not in YESH:
            continue
        for nxt in ws[i + 1:i + 3]:
            if _bare(nxt['surface']) in L_PRON:
                return [w['surface'], nxt['surface']]
    return []


def m_want(ws, _ar):
    """Matched on the GLOSS the lexicon gave the word, not on a list of spellings. רוצה is a
    participle and inflects for gender and number, and the lexicon already knows which forms
    belong to רָצָה -- restating that here as a spelling list would be a second, worse copy."""
    out = []
    for w in ws:
        g = str(w.get('gloss') or '').lower()
        if _pos(w) == 'VERB' and (g.startswith('to want') or 'want' in g.split(',')[0]):
            out.append(w['surface'])
    return out[:1]


def m_neg(ws, _ar):
    return [w['surface'] for w in ws if _bare(w['surface']) in ('לא', 'אל')][:1]


def m_haya(ws, _ar):
    """The verb הָיָה. Hebrew has no present tense of it, which is the nominal-sentence lesson;
    this is what happens when the same sentence moves into the past or the future."""
    return [w['surface'] for w in ws
            if _pos(w) == 'VERB' and str(w.get('lemma') or '') == 'הָיָה'][:1]


def m_shel(ws, _ar):
    return [w['surface'] for w in ws if _bare(w['surface']) in SHEL][:1]


def m_q(ws, ar):
    """A question word AND a question mark. Without the second test this lesson filled up with
    sentences that are not questions at all: מה is 'what' in חשבתי מה לעשות 'I thought about
    what to do', and כמה is 'a few' in אחרי כמה ימים. Both are the right word doing a job this
    lesson is not about."""
    if '?' not in ar:
        return []
    return [w['surface'] for w in ws if _bare(w['surface']) in QWORD][:1]


def m_rel(ws, _ar):
    """ש־ glued to a verb. Same evidence as the article: the token only resolved once ש- came
    off the front, and what is behind it is a verb, which is what makes it a clause rather
    than the noun שם or the number שתיים."""
    return [w['surface'] for w in ws
            if _cut(w) in ('ש-', 'וש-') and _pos(w) == 'VERB'][:1]


SENT_SPEC = [
    {'id': 'nominal', 'title': 'Sentences with no “is”', 'sub': 'הבית גדול — “the house (is) big”',
     'body': [
        'Hebrew has no word for “is / am / are” in the present tense. You put the two things '
        'next to each other and stop: <b>הבית גדול</b> is literally “the house big”, and it '
        'means “the house is big”. Same with <b>אני עייף</b> “I am tired” and '
        '<b>הקפה חם</b> “the coffee is hot”.',
        'This is the first thing that stops you sounding translated. When English reaches for '
        '“is”, Hebrew reaches for nothing at all — subject, then the describing word, done. '
        'The verb <b>היה</b> exists, but it is for the past and the future only; there is a '
        'lesson on it further down.'],
     'tables': [{'title': 'The pattern', 'rows': [
        ['הבית גדול', 'ha-báyit gadól', 'the house is big'],
        ['אני עייף', 'aní ayéf', 'I am tired'],
        ['היא רופאה', 'hi rofá', 'she is a doctor'],
        ['הם בבית', 'hem ba-báyit', 'they are at home'],
        ['זה יפה', 'ze yafé', 'that is beautiful']]}],
     'match': m_nominal},

    {'id': 'article', 'title': 'The definite article ה־', 'sub': '“the”, glued to the front',
     'body': [
        'There is one word for “the” and it is a single letter: <b>ה־</b>, stuck onto the front '
        'of the noun. <b>בית</b> is “a house”, <b>הבית</b> is “the house”.',
        'Two things follow from it being glued on rather than standing alone. An adjective '
        'after a definite noun takes the ה too, so “the big house” is <b>הבית הגדול</b>, with '
        'the article twice — miss the second one and you have said “the house is big” instead, '
        'which is the lesson above. And when a preposition comes in front, the two letters '
        'merge: ב + ה becomes <b>ב</b> with a different vowel, so “in the house” is '
        '<b>בבית</b> (ba-báyit) against “in a house” <b>בבית</b> (be-váyit) — same letters, and '
        'only the vowels tell them apart.'],
     'tables': [{'title': 'With and without', 'rows': [
        ['בית · הבית', 'báyit · ha-báyit', 'a house · the house'],
        ['בית גדול', 'báyit gadól', 'a big house'],
        ['הבית הגדול', 'ha-báyit ha-gadól', 'the big house (the article twice)'],
        ['הבית גדול', 'ha-báyit gadól', 'the house is big (article once)'],
        ['בבית', 'ba-báyit', 'in the house (ב + ה merged)']]}],
     'match': m_article},

    {'id': 'pronouns', 'title': 'The people: I, you, he, she…', 'sub': 'subject pronouns',
     'body': [
        'Hebrew keeps a separate “you” for men and women and a separate “they” as well, so '
        'there are ten of these where English has seven.',
        'In the past and future the verb ending already says who is acting, so the pronoun is '
        'often dropped: <b>הלכתי</b> is “I went” on its own. In the present it is NOT dropped, '
        'because the present tense marks gender and number but not person — <b>הולך</b> is '
        '“going, masculine singular”, and only the pronoun tells you whether that is I, you or '
        'he.'],
     'tables': [{'title': 'Subject pronouns', 'rows': [
        ['אני', 'aní', 'I'], ['אתה', 'atá', 'you (m)'], ['את', 'at', 'you (f)'],
        ['הוא', 'hu', 'he'], ['היא', 'hi', 'she'], ['אנחנו', 'anákhnu', 'we'],
        ['אתם', 'atém', 'you (m pl)'], ['אתן', 'atén', 'you (f pl)'],
        ['הם', 'hem', 'they (m)'], ['הן', 'hen', 'they (f)']]}],
     'match': m_pron},

    {'id': 'yesh', 'title': '“There is” and “there isn’t” — יש and אין', 'sub': 'יש · אין',
     'body': [
        'Two words carry all of English’s “there is”, “there are”, “there was” and their '
        'negatives. <b>יש</b> says something exists, <b>אין</b> says it does not, and neither '
        'of them inflects for anything at all — no gender, no number, no person.',
        'For the past and the future you put <b>היה</b> in front: <b>היה יש</b> is not said, '
        'but <b>היו הרבה אנשים</b> “there were a lot of people” is, and for the negative you '
        'get <b>לא היה</b>. In the present, יש and אין do the whole job by themselves.'],
     'tables': [{'title': 'Existence', 'rows': [
        ['יש', 'yesh', 'there is, there are'],
        ['אין', 'eyn', 'there is not, there are not'],
        ['יש אנשים בחוץ', 'yesh anashím ba-khúts', 'there are people outside'],
        ['אין מים', 'eyn máyim', 'there is no water'],
        ['היו הרבה אנשים', 'hayú harbé anashím', 'there were a lot of people']]}],
     'match': m_yesh},

    {'id': 'having', 'title': 'Having — יש לי', 'sub': '“there is to me”',
     'body': [
        'Hebrew has no verb “to have”. It says the thing exists, and then says to whom: '
        '<b>יש לי</b> is literally “there is to me”, and it means “I have”.',
        'So the thing owned is the subject of the sentence and the owner is a prepositional '
        'phrase, which is why nothing agrees with the owner. <b>יש לי ספר</b>, <b>יש לה ספר</b> '
        'and <b>יש להם ספר</b> differ in one word. The negative is <b>אין לי</b>, and the past '
        'is <b>היה לי</b> — and there the verb agrees with the THING, so it is '
        '<b>הייתה לי בעיה</b> “I had a problem”, feminine, because בעיה is feminine.'],
     'tables': [{'title': 'To me, to you, to him…', 'rows': [
        ['יש לי', 'yesh li', 'I have'], ['יש לך', 'yesh lekhá / lakh', 'you have (m / f)'],
        ['יש לו', 'yesh lo', 'he has'], ['יש לה', 'yesh la', 'she has'],
        ['יש לנו', 'yesh lánu', 'we have'], ['יש לכם', 'yesh lakhém', 'you have (pl)'],
        ['יש להם', 'yesh lahém', 'they have'],
        ['אין לי', 'eyn li', 'I do not have'],
        ['היה לי', 'hayá li', 'I had']]}],
     'match': m_having},

    {'id': 'wanting', 'title': 'Wanting — רוצה', 'sub': 'and צריך, “need”',
     'body': [
        '<b>רוצה</b> is an ordinary present-tense verb, which means it agrees with the speaker '
        'in gender and number and not in person: a man says <b>אני רוצה</b>, a woman says '
        '<b>אני רוצה</b> too — the spelling is the same and the vowels differ — and a group '
        'says <b>אנחנו רוצים</b>.',
        'What follows it is the infinitive: <b>אני רוצה ללכת</b> “I want to go”. If you want '
        'someone ELSE to do the thing, Hebrew switches to <b>ש</b> plus the future: '
        '<b>אני רוצה שתלך</b> “I want you to go”, literally “I want that you will go”. '
        '<b>צריך</b> “need” and <b>אוהב</b> “like” take the infinitive the same way.'],
     'tables': [{'title': 'Want, need, like', 'rows': [
        ['אני רוצה', 'aní rotsé / rotsá', 'I want (m / f)'],
        ['אנחנו רוצים', 'anákhnu rotsím', 'we want'],
        ['אני רוצה ללכת', 'aní rotsé lalékhet', 'I want to go'],
        ['אני רוצה שתלך', 'aní rotsé she-teléch', 'I want you to go'],
        ['אני צריך', 'aní tsaríkh', 'I need'],
        ['אני אוהב', 'aní ohév', 'I like, I love']]}],
     'match': m_want},

    {'id': 'negation', 'title': 'Saying no — לא and אל', 'sub': 'and where אין comes in',
     'body': [
        '<b>לא</b> negates almost everything, and it goes in front of what it negates: '
        '<b>לא הלכתי</b> “I did not go”, <b>לא טוב</b> “not good”. It never changes shape.',
        'Two places take a different word. To tell someone NOT to do something you use '
        '<b>אל</b> with the future, not לא: <b>אל תלך</b> “do not go”. And to say a thing does '
        'not exist you use <b>אין</b>, from the lesson above: <b>אין לי זמן</b> “I have no '
        'time”. Saying <b>לא</b> where Hebrew wants אל or אין is one of the most audible '
        'mistakes a learner makes.'],
     'tables': [{'title': 'Three different “no”', 'rows': [
        ['לא הלכתי', 'lo halákhti', 'I did not go'],
        ['לא טוב', 'lo tov', 'not good'],
        ['אל תלך', 'al teléch', 'do not go (command)'],
        ['אין לי זמן', 'eyn li zman', 'I have no time'],
        ['לא, תודה', 'lo, todá', 'no, thank you']]}],
     'match': m_neg},

    {'id': 'haya', 'title': 'Was and will be — היה', 'sub': 'the verb the present does without',
     'body': [
        'The lesson on nominal sentences said Hebrew leaves “is” out. <b>היה</b> is what comes '
        'back the moment the sentence stops being about now: <b>הבית גדול</b> “the house is '
        'big” becomes <b>הבית היה גדול</b> in the past and <b>הבית יהיה גדול</b> in the future.',
        'It agrees with the subject like any other verb, and it is irregular enough to be worth '
        'learning as a table rather than as a pattern. It is also the verb that puts יש and '
        'אין into the past: <b>היו הרבה אנשים</b>, <b>לא היה זמן</b>.'],
     'tables': [{'title': 'היה, past', 'rows': [
        ['הייתי', 'hayíti', 'I was'], ['היית', 'hayíta / hayít', 'you were (m / f)'],
        ['היה', 'hayá', 'he was'], ['הייתה', 'haytá', 'she was'],
        ['היינו', 'hayínu', 'we were'], ['הייתם', 'heyitém', 'you were (pl)'],
        ['היו', 'hayú', 'they were']]},
        {'title': 'היה, future', 'rows': [
        ['אהיה', 'ehyé', 'I will be'], ['תהיה', 'tihyé', 'you will be (m)'],
        ['יהיה', 'yihyé', 'he will be'], ['תהיה', 'tihyé', 'she will be'],
        ['נהיה', 'nihyé', 'we will be'], ['יהיו', 'yihyú', 'they will be']]}],
     'match': m_haya},

    {'id': 'shel', 'title': 'Mine, yours, his — של', 'sub': 'the easy way, and the short way',
     'body': [
        'Possession is one word, <b>של</b>, and it takes the endings: <b>הספר שלי</b> “my book”, '
        'literally “the book of-me”. Note the noun keeps its <b>ה</b> — it is “THE book of me”, '
        'never “book of me”.',
        'There is a second, older way that glues the ending straight onto the noun — '
        '<b>ספרי</b> for “my book”, <b>שמו</b> for “his name”. You will meet it constantly in '
        'writing and in fixed phrases, and almost never in speech, where של does the work. '
        'Learn to recognise it; use the של form.'],
     'tables': [{'title': 'Of me, of you, of him…', 'rows': [
        ['שלי', 'shelí', 'my, mine'], ['שלך', 'shelkhá / shelákh', 'your (m / f)'],
        ['שלו', 'sheló', 'his'], ['שלה', 'shelá', 'her'],
        ['שלנו', 'shelánu', 'our'], ['שלכם', 'shelakhém', 'your (pl)'],
        ['שלהם', 'shelahém', 'their'],
        ['הספר שלי', 'ha-séfer shelí', 'my book'],
        ['שמו', 'shmo', 'his name (the glued form)']]}],
     'match': m_shel},

    {'id': 'questions', 'title': 'Asking things', 'sub': 'מה, מי, איפה, למה…',
     'body': [
        'The question word goes first and nothing else moves. Hebrew does not invert the '
        'sentence and has no “do” to insert, so <b>אתה הולך</b> “you are going” becomes '
        '<b>לאן אתה הולך</b> “where are you going” with a word added and nothing rearranged.',
        'A yes/no question is the statement with a question mark on it and a rise at the end: '
        '<b>אתה בא?</b> “are you coming?”. There is a formal particle <b>האם</b> for these, and '
        'in speech it is essentially never used.'],
     'tables': [{'title': 'Question words', 'rows': [
        ['מה', 'ma', 'what'], ['מי', 'mi', 'who'], ['איפה', 'éyfo', 'where'],
        ['לאן', 'le-án', 'where to'], ['מאיפה', 'me-éyfo', 'where from'],
        ['מתי', 'matáy', 'when'], ['למה', 'láma', 'why'], ['איך', 'eykh', 'how'],
        ['כמה', 'káma', 'how much, how many'], ['איזה', 'éyze', 'which']]}],
     'match': m_q},

    {'id': 'relative', 'title': 'The one that — ש־', 'sub': 'one letter does the whole job',
     'body': [
        'English has “that”, “which”, “who”, “where” and drops them half the time. Hebrew has '
        '<b>ש־</b>, one letter glued to the front of the next word, and never drops it: '
        '<b>האיש שבא</b> “the man who came”, <b>הספר שקראתי</b> “the book that I read”, '
        '<b>המקום שגרנו בו</b> “the place we lived in”.',
        'The same <b>ש־</b> is also plain “that” after verbs of saying and thinking — '
        '<b>הוא אמר שהוא בא</b> “he said that he is coming” — and it is the ש in '
        '<b>אני רוצה שתלך</b> from the wanting lesson. One letter, three jobs in English, and '
        'you never have a choice about whether to include it.'],
     'tables': [{'title': 'ש־ at work', 'rows': [
        ['האיש שבא', 'ha-ísh she-ba', 'the man who came'],
        ['הספר שקראתי', 'ha-séfer she-karáti', 'the book that I read'],
        ['הבית שגרנו בו', 'ha-báyit she-gárnu bo', 'the house we lived in'],
        ['הוא אמר שהוא בא', 'hu amár she-hu ba', 'he said that he is coming'],
        ['אני חושב שכן', 'aní khoshév she-ken', 'I think so']]}],
     'match': m_rel},
]


def sentence_examples(spec):
    """Real sentences for each sentence pattern, from the app's own annotated Hebrew.

    Same discipline as corpus_examples above and for the same reasons: spoken registers first,
    at most two sentences from any one text, and a head-of-sentence dedupe because the paper
    reruns a story the next morning with the tail reworded. What is NOT reused is the
    one_reading() guard. That test asks whether a word's letters can be read only one way,
    which is the right question when the claim is "this word is a piel" and the wrong one here:
    the claim is about the shape of the sentence, and יש לי is יש לי however many ways יש can
    be read on its own.
    """
    rows = collections.defaultdict(list)
    for f in sorted(glob.glob(paths.build('*', 'text.json'))):
        d = json.load(open(f, encoding='utf-8'))
        rank = KIND_ORDER.get(d.get('kind'), 2)
        title = d['title'].get('en') or d['id']
        for sn in d['sentences']:
            if not sn.get('en') or not sn.get('words'):
                continue
            for les in spec:
                hi = les['match'](sn['words'], sn['ar'])
                if hi:
                    rows[les['id']].append((rank, len(sn['words']), d['id'], title,
                                            sn['ar'], sn['en'], sorted(set(hi))))
    out = {}
    for lid, rs in rows.items():
        rs.sort(key=lambda r: r[:2])
        picked, per, said = [], collections.Counter(), set()
        for _rank, _n, tid, ttl, ar, en, hi in rs:
            head = ' '.join(ar.split()[:6])
            if per[tid] >= PER_TEXT or head in said:
                continue
            said.add(head)
            per[tid] += 1
            picked.append({'ar': ar, 'en': en, 'src': tid, 'title': ttl, 'hi': hi})
            if len(picked) >= EXAMPLES:
                break
        out[lid] = picked
    return out


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

    # 0 -----------------------------------------------------------------------------------
    # How a SENTENCE is built, before how a word is. This is the order the Arabic side teaches
    # in and the order a beginner needs: nothing in the binyan lessons helps you say "I have".
    sx = sentence_examples(SENT_SPEC)
    for les in SENT_SPEC:
        found = sx.get(les['id'], [])
        if len(found) < MIN_EXAMPLES:
            raise SystemExit('!! %s: only %d real sentences (need %d) — the corpus cannot '
                             'show this pattern yet, and a lesson that illustrates itself '
                             'with two sentences is not one.' % (les['id'], len(found),
                                                                 MIN_EXAMPLES))
        L.append({'id': les['id'], 'title': les['title'], 'sub': les['sub'],
                  'body': list(les['body']), 'tables': list(les.get('tables', [])),
                  'examples': found})

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
        'intro': 'Two halves. The first eleven lessons are how a <b>sentence</b> is built — '
                 'that Hebrew leaves out “is”, that “I have” is “there is to me”, that one '
                 'letter does the work of “that”, “which” and “who”. The last nine are how a '
                 '<b>word</b> is built: the <b>binyanim</b>, the seven shapes a three-letter '
                 'root is poured into, where learning to see the root through the shape leaves '
                 'a word you have never met half known. The prose and the paradigm tables are '
                 'written; every example sentence is a real one out of this app’s own Hebrew, '
                 'and every word in the verb tables is a real dictionary entry.',
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
