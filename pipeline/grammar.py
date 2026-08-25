#!/usr/bin/env python3
"""Build the Grammar section: spoken-Palestinian structures, each illustrated by REAL
sentences mined from the app's own corpus.

Integrity, the same as everywhere else in this project:
  * The EXPLANATIONS are hand-written pedagogy — standard descriptions of how spoken
    Palestinian works, meant to orient, not to be memorised word-for-word. (Same status as
    the verb-form notes in the app.)
  * The PARADIGM TABLES are closed-class function words (pronouns, بدّي, عندي, question
    words…). Maknuune is a lexicon of CONTENT words and doesn't carry these, exactly as
    `curated.py` explains — so they're curated by hand, in the app's urban notation
    (2=glottal stop, 3=ʿayn, 7=ḥāʾ), and labelled as such.
  * The EXAMPLE SENTENCES are NOT written here. They're pulled from build/*/text.json —
    sentences already ingested, where every word was looked up in Maknuune. So no Arabic
    is invented for the examples; we only SELECT sentences that show each pattern, and note
    which text each came from so the learner can read it in full context.

Run:  python3 pipeline/grammar.py    →  app/data/grammar.js  (window.GRAMMAR)
"""
import json, os, glob, re
from subdialect import realize

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'app', 'data', 'grammar.js')

# ---- load the corpus ----
def load():
    out = []
    for p in glob.glob(os.path.join(ROOT, 'build', '*', 'text.json')):
        t = json.load(open(p, encoding='utf-8'))
        out.append(t)
    return out

TEXTS = load()
# rank source texts so simpler material is preferred for examples
LEVEL_RANK = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
def text_rank(t):
    if t.get('kind') == 'story':
        return LEVEL_RANK.get(t.get('level'), 2)
    if t.get('kind') == 'news':
        return 4
    return 3
SENTS = []
for t in TEXTS:
    for s in t['sentences']:
        SENTS.append({'tid': t['id'], 'title': (t.get('title') or {}).get('en', t['id']),
                      'rank': text_rank(t), 'ar': s['ar'], 'en': s['en'], 'words': s['words']})

# ---- small predicates over a sentence's word list ----
def anal(w):    return str(w.get('analysis') or '')
def is_verb(w): return anal(w).startswith('VERB')
def surf(w):    return w.get('surface') or ''
def clean(x):   return re.sub(r'[،.؟!:؛…"«»”“\-—()]', '', x or '')

QWORDS = {'شو', 'مين', 'وين', 'إيمتى', 'ايمتى', 'ليش', 'كيف', 'قديش', 'أديش', 'قدّيش', 'كم', 'أيّ', 'أي'}
DEMS = {'هاد', 'هاي', 'هدول', 'هادا', 'هاظ', 'هاظا'}
SUBJ_PRON = {'أنا', 'انا', 'إنت', 'انت', 'إنتي', 'انتي', 'هو', 'هي', 'إحنا', 'احنا', 'إنتو', 'انتو', 'هم', 'همّ', 'هنّ'}
COMPAR = {'أكتر', 'اكتر', 'أحسن', 'احسن', 'أكبر', 'اكبر', 'أصغر', 'أزغر', 'أطيب', 'أحلى', 'احلى', 'أقل', 'اقل'}
PRESENT_PREF = ('ب', 'بت', 'بن', 'بي', 'من', 'عم', 'ح', 'ي', 'ت', 'ن', 'رح')

def m_nominal(w):   # no verb, short, has an adjective → "is" is invisible
    if any(is_verb(x) for x in w): return None
    if not (2 <= len(w) <= 6): return None
    adjs = [surf(x) for x in w if anal(x).startswith('ADJ')]
    return adjs if adjs else None

def m_definite(w):
    hits = [surf(x) for x in w if clean(surf(x)).startswith('ال') and len(clean(surf(x))) > 3]
    return hits[:1] or None

def m_pron(w):
    hits = [surf(x) for x in w if clean(surf(x)) in SUBJ_PRON]
    return hits[:1] or None

def m_bpresent(w):
    hits = [surf(x) for x in w if is_verb(x) and clean(surf(x)).startswith('ب') and len(clean(surf(x))) >= 3]
    return hits[:1] or None

def m_prog(w):   # the particle عم is spelled exactly عم and ALWAYS precedes a verb — that guard
    for i, x in enumerate(w):   # keeps out عمّي “my uncle” and friends
        if clean(surf(x)) == 'عم' and i + 1 < len(w) and is_verb(w[i + 1]):
            return [surf(x), surf(w[i + 1])]
    return None

def m_future(w):   # only the رح token — the short حـ prefix is indistinguishable from a root ح
    for i, x in enumerate(w):   # (حطّيت “I put”, حسّيت “I felt” are PAST, ح is a radical)
        if clean(surf(x)) == 'رح':
            nxt = [surf(w[j]) for j in range(i + 1, min(i + 2, len(w)))]
            return [surf(x)] + nxt
    return None

# ما is also “before/when/that” in قبل ما, يوم ما, لما… — only count it as NEGATION when a verb
# follows and it isn't glued to one of those subordinators.
NEG_MA_BLOCK = {'قبل', 'بعد', 'زي', 'متل', 'مثل', 'كل', 'يوم', 'لما', 'طول', 'أول', 'وقت', 'ساعة', 'مثلما', 'بدون', 'من'}
def m_neg(w):
    hits = []
    for i, x in enumerate(w):
        c = clean(surf(x))
        if c in ('مش', 'مو'):
            hits.append(surf(x))
        elif c == 'ما':
            prev = clean(surf(w[i - 1])) if i > 0 else ''
            if i + 1 < len(w) and is_verb(w[i + 1]) and prev not in NEG_MA_BLOCK:
                hits.append(surf(x))
    # (We skip the colloquial -ش negation suffix: too many content words end in ش legitimately —
    #  أبلش “I start”, حوش “yard” — to detect it from spelling without false positives.)
    return hits[:2] or None

BADDI = re.compile(r'^بدّ?(ي|ك|ه|ها|نا|كم|هم|و|هن)$')
def m_baddi(w):
    hits = [surf(x) for x in w if BADDI.match(clean(surf(x)))]
    return hits[:1] or None

def m_3ind(w):
    hits = [surf(x) for x in w if clean(surf(x)).startswith('عند')]
    return hits[:1] or None

POSS = re.compile(r'.+(ي|ه|ها|نا|كم|هم|هن)$')   # drop bare ك: too many roots end in ك (شباك)
POSS_BLOCK = ('كل', 'بعض', 'نفس', 'ال')      # quantifiers/definite aren't possessed nouns
def m_poss(w):
    hits = [surf(x) for x in w if anal(x).startswith('NOUN') and len(clean(surf(x))) >= 4
            and POSS.match(clean(surf(x))) and not clean(surf(x)).startswith(POSS_BLOCK)]
    return hits[:1] or None

def m_q(w):
    hits = [surf(x) for x in w if clean(surf(x)) in QWORDS]
    return hits[:1] or None

def m_dem(w):
    hits = [surf(x) for x in w if clean(surf(x)) in DEMS or clean(surf(x)).startswith('هال')]
    return hits[:1] or None

def m_rel(w):
    hits = [surf(x) for x in w if clean(surf(x)) == 'اللي']
    return hits[:1] or None

def m_kaan(w):
    hits = [surf(x) for x in w if clean(surf(x)).startswith('كان') or clean(surf(x)) in ('كنت', 'كنّا', 'كانوا')]
    return hits[:1] or None

def m_compar(w):
    hits = [surf(x) for x in w if clean(surf(x)) in COMPAR]
    return hits[:1] or None

def m_past(w):   # a perfect verb with a 1st/2nd-person subject SUFFIX (رحت، طبخت، رحنا) — the most
    for x in w:  # reliable past signal from spelling alone. We avoid the ـوا ending (present 3pl
        c = clean(surf(x))   # also ends ـوا: بيلعبوا) and any b- present.
        if (is_verb(x) and len(c) >= 3 and (c.endswith('ت') or c.endswith('نا'))
                and not c.startswith(('ب', 'عم', 'رح'))):
            return [surf(x)]
    return None

def m_fi(w):     # في / فيه = "there is/are" (the token itself)
    hits = [surf(x) for x in w if clean(surf(x)) in ('في', 'فيه', 'فيها', 'فينا')]
    return hits[:1] or None

# adverbial "nouns" (بعد الغدا = after lunch) read like an idafa but aren't possessive — skip them
IDAFA_BLOCK = {'بعد', 'قبل', 'كل', 'نص', 'وسط', 'جنب', 'حول', 'طول', 'عند', 'مع', 'بين', 'فوق',
               'تحت', 'قدام', 'ورا', 'جوا', 'برا', 'مثل', 'متل', 'زي', 'غير', 'بدون', 'ضد', 'أول', 'آخر'}
def m_idafa(w):  # possession by juxtaposition: plain BARE NOUN + definite NOUN (باب البيت)
    for i in range(len(w) - 1):
        a, b = w[i], w[i + 1]; ca = clean(surf(a))
        # first noun must be bare — no ال and no clitic prefix (بال/عال/لل = adverbial "in/at/to the …")
        if (anal(a).startswith('NOUN:') and ca not in IDAFA_BLOCK
                and not ca.startswith(('ال', 'بال', 'عال', 'لل', 'وال', 'فال', 'كال', 'بل'))
                and clean(surf(b)).startswith('ال') and anal(b).startswith('NOUN')):
            return [surf(a), surf(b)]
    return None

def m_gender(w):  # prefer a feminine ADJECTIVE (shows agreement); else a feminine noun (analysis :F)
    adj = [surf(x) for x in w if anal(x).startswith('ADJ') and clean(surf(x)).endswith('ة')]
    if adj:
        return adj[:1]
    hits = [surf(x) for x in w if anal(x).startswith('NOUN') and ':F' in anal(x)]
    return hits[:1] or None

# ---- Wadi Ara (central rural) support ------------------------------------------------
# The corpus's Maknuune CAPHI++ templates carry the sub-dialect variables; realize() them
# both ways to SHOW the correspondence — nothing invented, same lexicon data either way.
WADI_WORDS = [('وَقِت', 'time'), ('قَدِيم', 'old'), ('طَرِيق', 'road'),
              ('حَكَى', 'he spoke'), ('ثَانِي', 'second, other'), ('كْثِير', 'a lot, many')]
def _rawfor(lemma):
    for s in SENTS:
        for w in s['words']:
            if w.get('lemma') == lemma and w.get('caphi_raw'):
                return str(w['caphi_raw']).split(',')[0].strip()
    return None
def _wadi_rows():
    rows = []
    for lemma, en in WADI_WORDS:
        raw = _rawfor(lemma)
        if raw:
            rows.append([lemma, '%s → %s' % (realize(raw, 'urban'), realize(raw, 'rural')), en])
    return rows

def _hasvar(tok):   # a CAPHI++ sub-dialect variable: uppercase, not an emphatic (no '.')
    return '.' not in tok and any(c in 'QKTDZ' for c in tok)   # J excluded: j = j in both accents
def m_wadi(w):
    hits = [surf(x) for x in w if any(_hasvar(t) for t in str(x.get('caphi_raw') or '').split())]
    return hits[:2] or None

# ---- the lessons ----
# body: paragraphs. tables: [{title, rows:[[ar, tr, en], ...]}]. match: predicate.
LESSONS = [
    {'id': 'nominal', 'title': 'Sentences with no “is”', 'sub': 'البيت كبير — “the house (is) big”',
     'body': [
        'Palestinian Arabic has no word for “is / am / are” in the present. You just put the two '
        'things side by side: <b>البيت كبير</b> — literally “the house big” — means “the house is big.” '
        'Same with “I’m tired” (<b>أنا تعبان</b>) or “the coffee’s hot” (<b>القهوة سخنة</b>).',
        'This is one of the first things that makes you sound natural: don’t hunt for a verb where '
        'English has one. Subject, then the describing word, and you’re done.'],
     'match': m_nominal},

    {'id': 'article', 'title': 'The definite article الـ', 'sub': '“the”, glued to the front',
     'body': [
        'There’s one word for “the”: <b>الـ</b> (al-), stuck onto the front of the noun — <b>البيت</b> '
        '“the house”, <b>الولد</b> “the boy”.',
        'When the noun starts with a “sun letter” (ت ث د ذ ر ز س ش ص ض ط ظ ل ن), the <b>ل</b> of الـ '
        'assimilates: <b>الشمس</b> is written al-shams but <i>said</i> <b>ish-shams</b>, <b>الرمل</b> '
        'is <b>ir-raml</b>. With the other “moon letters”, you hear the l normally: <b>القمر</b> '
        '<b>il-2amar</b> (the ق is a glottal stop in city speech). You don’t have to memorise '
        'the list — your ear picks it up fast.'],
     'match': m_definite},

    {'id': 'pronouns', 'title': 'The people: I, you, he, she…', 'sub': 'subject pronouns',
     'body': [
        'The subject pronouns. Note that Palestinian keeps a separate “you” for men and women, and '
        'the verb usually already tells you who’s acting — so these often get dropped for emphasis only.'],
     'tables': [{'title': 'Subject pronouns', 'rows': [
        ['أنا', 'ana', 'I'], ['إنت', 'inta', 'you (m)'], ['إنتي', 'inti', 'you (f)'],
        ['هو', 'huwwe', 'he'], ['هي', 'hiyye', 'she'], ['إحنا', 'i7na', 'we'],
        ['إنتو', 'intu', 'you (pl)'], ['هم', 'humme', 'they']]}],
     'match': m_pron},

    {'id': 'bpresent', 'title': 'Everyday actions — the b- present', 'sub': 'بحب، بشرب، بروح',
     'body': [
        'For what you do regularly or are doing now, spoken Palestinian puts a little <b>بـ</b> (b-) on '
        'the front of the present verb: <b>بحب</b> “I like”, <b>بشرب</b> “I drink”, <b>بروح</b> “I go”. '
        'This is the everyday workhorse tense — most sentences you say will use it.',
        'The prefix shifts a bit by person — <b>بحب</b> (I), <b>بتحب</b> (you), <b>بيحب</b> (he), '
        '<b>بنحب</b> (we). The <b>Verbs</b> section conjugates all of these for any verb.'],
     'match': m_bpresent},

    {'id': 'progressive', 'title': 'Right now — عم', 'sub': 'عم بشتغل — “I’m working (right now)”',
     'body': [
        'To stress that something is happening <i>right this moment</i>, put <b>عم</b> (3am) before the '
        'verb: <b>عم بشتغل</b> “I’m working”, <b>عم باكل</b> “I’m eating”. Without عم, the plain b- '
        'present covers both “I work” and “I’m working”; عم just makes the “right now” explicit.'],
     'match': m_prog},

    {'id': 'future', 'title': 'The future — رح', 'sub': 'رح أروح — “I’m going to go”',
     'body': [
        'For the future, put <b>رح</b> (ra7) — or its short form <b>حـ</b> stuck to the verb — before '
        'the <i>bare</i> present (no بـ): <b>رح أروح</b> / <b>حروح</b> “I’ll go”, <b>رح آكل</b> “I’ll eat”. '
        'Think of رح as “gonna”.'],
     'match': m_future},

    {'id': 'negation', 'title': 'Saying no — ما and مش', 'sub': 'ما بحب · مش هون',
     'body': [
        'Two tools. To negate a <b>verb</b>, put <b>ما</b> (ma) in front: <b>ما بحب</b> “I don’t like”, '
        '<b>ما رحت</b> “I didn’t go.” In casual speech you’ll often hear a <b>ـش</b> tacked on the end '
        'too: <b>ما بحبش</b>.',
        'To negate <b>everything else</b> — a noun, an adjective, a place — use <b>مش</b> (mish): '
        '<b>مش هون</b> “not here”, <b>مش كبير</b> “not big”, <b>مش أنا</b> “not me.”'],
     'match': m_neg},

    {'id': 'baddi', 'title': 'Wanting — بدّي', 'sub': 'بدّي أروح — “I want to go”',
     'body': [
        '“Want” isn’t a normal verb — it’s the little word <b>بدّ</b> plus an ending for who wants: '
        '<b>بدّي</b> “I want”, <b>بدّك</b> “you want”, <b>بدّه</b> “he wants.” Follow it with a bare '
        'present verb for “want to …”: <b>بدّي أروح</b> “I want to go”, <b>بدّك تاكل؟</b> “do you want to eat?”'],
     'tables': [{'title': 'بدّ + ending = want', 'rows': [
        ['بدّي', 'baddi', 'I want'], ['بدّك', 'baddak', 'you want (m)'], ['بدّك', 'baddik', 'you want (f)'],
        ['بدّه', 'baddo', 'he wants'], ['بدّها', 'baddha', 'she wants'], ['بدّنا', 'baddna', 'we want'],
        ['بدّكم', 'baddkom', 'you want (pl)'], ['بدّهم', 'baddhom', 'they want']]}],
     'match': m_baddi},

    {'id': 'indi', 'title': 'Having — عندي', 'sub': 'عندي وقت — “I have time”',
     'body': [
        'Same idea for “have”: there’s no verb, just <b>عند</b> (“at / by”) plus the ending — literally '
        '“at-me / at-you”: <b>عندي</b> “I have”, <b>عندك</b> “you have”, <b>عنده</b> “he has.” '
        '<b>عندي وقت</b> “I have time”, <b>عندك سيارة؟</b> “do you have a car?”'],
     'tables': [{'title': 'عند + ending = have', 'rows': [
        ['عندي', '3indi', 'I have'], ['عندك', '3indak', 'you have (m)'], ['عندك', '3indik', 'you have (f)'],
        ['عنده', '3indo', 'he has'], ['عندها', '3indha', 'she has'], ['عندنا', '3indna', 'we have'],
        ['عندكم', '3indkom', 'you have (pl)'], ['عندهم', '3indhom', 'they have']]}],
     'match': m_3ind},

    {'id': 'possessive', 'title': 'Mine, yours, his — endings on nouns', 'sub': 'بيتي، بيتك، بيته',
     'body': [
        'To say “my / your / his …”, you don’t use a separate word — you stick an ending on the noun, '
        'the same endings as بدّي and عندي: <b>بيت</b> “house” → <b>بيتي</b> “my house”, <b>بيتك</b> '
        '“your house”, <b>بيته</b> “his house”, <b>بيتنا</b> “our house.”'],
     'tables': [{'title': 'بيت (house) + ending', 'rows': [
        ['بيتي', 'beeti', 'my house'], ['بيتك', 'beetak', 'your house (m)'], ['بيتك', 'beetik', 'your house (f)'],
        ['بيته', 'beeto', 'his house'], ['بيتها', 'beetha', 'her house'], ['بيتنا', 'beetna', 'our house'],
        ['بيتكم', 'beetkom', 'your house (pl)'], ['بيتهم', 'beethom', 'their house']]}],
     'match': m_poss},

    {'id': 'questions', 'title': 'Asking things', 'sub': 'شو، وين، ليش…',
     'body': [
        'The question words. Word order stays the same as a statement — you just drop the question word '
        'in, usually at the front: <b>وين رايح؟</b> “where are you going?”, <b>شو بدّك؟</b> “what do you want?”'],
     'tables': [{'title': 'Question words', 'rows': [
        ['شو', 'shu', 'what'], ['مين', 'miin', 'who'], ['وين', 'ween', 'where'],
        ['إيمتى', 'eemta', 'when'], ['ليش', 'leesh', 'why'], ['كيف', 'kiif', 'how'],
        ['قدّيش', '2addeesh', 'how much'], ['كم', 'kam', 'how many']]}],
     'match': m_q},

    {'id': 'demonstratives', 'title': 'This and these', 'sub': 'هاد، هاي، هدول',
     'body': [
        '“This” changes with gender, “these” doesn’t: <b>هاد</b> (haad) for a masculine thing, '
        '<b>هاي</b> (hayy) for a feminine one, <b>هدول</b> (hadool) for plural. '
        '<b>هاد الولد</b> “this boy”, <b>هاي البنت</b> “this girl”, <b>هدول الناس</b> “these people.”'],
     'match': m_dem},

    {'id': 'relative', 'title': 'The one that… — اللي', 'sub': 'الولد اللي بيلعب',
     'body': [
        'One little word does the job of “who / which / that”: <b>اللي</b> (illi), for people and things '
        'alike. <b>الولد اللي بيلعب</b> “the boy who’s playing”, <b>الأكل اللي طبخته</b> “the food that I cooked.”'],
     'match': m_rel},

    {'id': 'kaan', 'title': 'Was and were — كان', 'sub': 'كان تعبان — “he was tired”',
     'body': [
        'Remember there’s no “is” in the present — but there <i>is</i> a past “was / were”: <b>كان</b> '
        '(kaan). <b>كان تعبان</b> “he was tired”, <b>كنت هون</b> “I was here”, <b>كانوا مبسوطين</b> '
        '“they were happy.” Put كان before a present verb and you get “used to / was …-ing”: '
        '<b>كنت بلعب</b> “I used to play.”'],
     'match': m_kaan},

    {'id': 'past', 'title': 'Telling what happened — the past', 'sub': 'رحت، أكلت، شفت',
     'body': [
        'Stories run on the past tense, and it’s built by changing the <i>end</i> of the verb instead of '
        'the front: <b>راح</b> “he went”, <b>رحت</b> “I went”, <b>رحنا</b> “we went.” No بـ here — the '
        'past never takes it.',
        'The full set of endings, for any verb and any pattern, is in the <b>Verbs</b> section — open a '
        'verb and look at the “Past” column.'],
     'match': m_past},

    {'id': 'comparative', 'title': 'Bigger, better — comparatives', 'sub': 'أكبر من · أحسن',
     'body': [
        'To compare, most adjectives take an <b>أ-</b> shape: <b>كبير</b> “big” → <b>أكبر</b> “bigger”, '
        '<b>حلو</b> → <b>أحلى</b> “sweeter/nicer”, <b>كتير</b> → <b>أكتر</b> “more.” Add <b>من</b> for '
        '“than”: <b>أكبر من بيتنا</b> “bigger than our house.”'],
     'match': m_compar},

    # ---- extra: the things that trip up English speakers specifically ----
    {'id': 'fi', 'title': '“There is / there are” — في (and “in” is بـ)', 'sub': 'في أكل · ما في وقت · بالبيت',
     'body': [
        'This one confuses English speakers because <b>في</b> <i>looks</i> like it should mean “in” — and in '
        'Modern Standard Arabic it does. But in spoken Palestinian, <b>في</b> (fi) usually means '
        '<b>“there is / there are”</b>: <b>في أكل</b> “there’s food”, <b>في ناس كتير</b> “there are a lot of '
        'people.” The negative is <b>ما في</b>: <b>ما في وقت</b> “there’s no time.”',
        'So how do you say <b>“in / at”</b>? Palestinian sticks <b>بـ</b> (b-) onto the noun instead: '
        '<b>بالبيت</b> “in the house”, <b>بالسيارة</b> “in the car”, <b>بالشغل</b> “at work.” Keep the two '
        'apart — <b>في</b> = there is, <b>بـ</b> = in — and في stops feeling random.'],
     'match': m_fi},

    {'id': 'idafa', 'title': 'No word for “of” — just stack the nouns', 'sub': 'باب البيت = the door of the house',
     'body': [
        'English links nouns with “of” or “’s” (“the door <i>of</i> the house”, “the house<i>’s</i> door”). '
        'Arabic just sets the two nouns next to each other, the owned thing first, with <b>no</b> word for “of”: '
        '<b>باب البيت</b> “the door of the house”, <b>بيت الرجل</b> “the man’s house”, <b>اسم البنت</b> '
        '“the girl’s name.”',
        'Watch the “the”: only the <i>second</i> noun takes الـ — <b>باب البيت</b>, literally “door the-house” '
        '(never الباب البيت). For a looser “belonging to,” spoken Palestinian also has <b>تبع</b>: '
        '<b>الكتاب تبع أحمد</b> “Ahmad’s book.”'],
     'match': m_idafa},

    {'id': 'gender', 'title': 'Masculine & feminine', 'sub': 'ولد كبير · بنت كبيرة',
     'body': [
        'Arabic sorts every noun as masculine or feminine, and the words around it must match — something '
        'English never does. The usual sign of feminine is a <b>ة</b> ending: <b>بنت</b> “girl”, <b>سيارة</b> '
        '“car”, <b>قهوة</b> “coffee” are feminine; most other nouns are masculine.',
        'Adjectives and verbs agree with it. Masculine <b>ولد كبير</b> “a big boy” → feminine <b>بنت كبيرة</b> '
        '“a big girl” (add ة). <b>هو راح</b> “he went” → <b>هي راحت</b> “she went.” Learn each noun’s gender '
        'together with the word — there’s no shortcut, but the ة gives most of them away.'],
     'match': m_gender},

    {'id': 'wadi-ara', 'title': 'The Wadi Ara accent', 'sub': 'وادي عارة — how the Triangle villages sound',
     'body': [
        'This app teaches <b>urban Palestinian</b> — the city speech of Jerusalem, Ramallah and Haifa '
        'that works everywhere, Wadi Ara included. But the home accent of Wadi Ara — Umm il-Faḥm, '
        'ʿArʿara, Kufur Qariʿ, Bāqa — is <b>central rural Palestinian</b> (“fallāḥi”), the village '
        'dialect of the Triangle and the central hills. Same grammar, same words; what changes is a '
        'handful of sounds, and they change <i>systematically</i> — learn four correspondences and '
        'you can convert anything you know on the fly.',
        'First: <b>ق is said k</b>. وقت “time” is city <i>wa2it</i>, village <i>wakit</i>; قهوة is '
        '<i>2ahwe</i> in town, <i>kahwe</i> in the village. And <b>ك is said ch</b> (č, as in '
        '“church”): كيف <i>kiif</i> → <i>chiif</i>, حكى&lrm; <i>7aka</i> → <i>7acha</i>; “your (f.)” '
        '<b>ـِك</b> becomes <i>-ich</i>. The two shifts work as a pair — ك moved to <i>ch</i> and '
        'freed <i>k</i> for ق — so in Wadi Ara <i>kalb</i> is قلب “heart”, while “dog” (كلب) is '
        '<i>chalb</i>. No confusion, ever.',
        'The <b>interdentals survive</b> in the village where the city dropped them: ث stays '
        '<i>th</i> (ثاني city <i>taani</i>, village <i>thaani</i>) and ذ stays <i>dh</i> (هاد ~ '
        '<i>haadh</i>). Traditional village speech also keeps the <b>feminine plurals</b> the city '
        'lost — إنتن <i>intin</i> “you (f. pl.)”, هنّ <i>hinne</i> “they (f.)”, verbs ending in '
        '<i>ـِن</i> — today mostly from older speakers. Younger Wadi Ara speakers mix city forms '
        'freely, but the <i>ch</i> stays a proud local badge.',
        'Everything in this app — spelling, tables, audio — stays in the urban koine, because that '
        'is what the recorded voice speaks and what every Palestinian understands. The word cards '
        'show the Wadi Ara form automatically whenever it differs, and the examples below are corpus '
        'sentences containing words a Wadi Ara speaker says differently — try converting them as '
        'you read.'],
     'tables': [
        {'title': 'The four correspondences', 'rows': [
            ['ق', 'city: 2 (glottal stop)', 'Wadi Ara: k'],
            ['ك', 'city: k', 'Wadi Ara: ch (č, as in “church”)'],
            ['ث', 'city: t', 'Wadi Ara: th (as in “three”)'],
            ['ذ', 'city: d', 'Wadi Ara: dh (as in “this”)']]},
        {'title': 'Same word, two accents — computed from the lexicon’s own templates',
         'rows': _wadi_rows()}],
     'match': m_wadi},
]

# ---- pick the best example sentences for each lesson ----
def pick_examples(match, n=30):
    """Corpus sentences showing this structure — varied by source, simplest first.

    Two problems with taking the globally top-scored N. First, N was 4, so of the 9,661
    sentences in the corpus that demonstrate one of these structures, 80 shipped — 0.8%.
    Second, and worse at that size: `rank` is a property of the TEXT, not the sentence, so
    every sentence in one beginner story scores identically and they win as a block. The
    article lesson drew 3 of its 4 examples from a single story, the past-tense lesson 2 of
    4 — the handful a learner did see were the same voice describing the same scene.

    So: bucket candidates by source text, order the buckets by their best sentence (which
    keeps the simplest material first), then round-robin — everyone's best, then everyone's
    second-best. Variety is structural rather than hoped for: at n=30 every example in every
    lesson still comes from a different text — the corpus has enough distinct sources that the
    round-robin never has to go back for a second sentence from the same one.
    """
    by_text, seen = {}, set()
    for s in SENTS:
        hi = match(s['words'])
        if not hi or s['ar'] in seen:
            continue
        seen.add(s['ar'])
        nwords = len(s['words'])
        # prefer simpler texts and medium-length sentences (4–9 words)
        length_pen = 0 if 4 <= nwords <= 9 else (1 if nwords <= 12 else 3)
        by_text.setdefault(s['tid'], []).append(
            (s['rank'] + length_pen, nwords, s, [clean(x) for x in hi]))
    for v in by_text.values():
        v.sort(key=lambda z: (z[0], z[1]))
    texts = sorted(by_text, key=lambda t: (by_text[t][0][0], by_text[t][0][1]))

    out, depth = [], 0
    while len(out) < n:
        took = False
        for t in texts:
            if depth < len(by_text[t]):
                out.append(by_text[t][depth])
                took = True
                if len(out) >= n:
                    break
        if not took:            # every text exhausted — this structure is simply rare
            break
        depth += 1
    return [{'ar': s['ar'], 'en': s['en'], 'src': s['tid'], 'title': s['title'], 'hi': hi}
            for _, _, s, hi in out]

def main():
    lessons = []
    for L in LESSONS:
        ex = pick_examples(L['match'])
        lessons.append({k: L[k] for k in ('id', 'title', 'sub', 'body') if k in L}
                       | ({'tables': L['tables']} if 'tables' in L else {})
                       | {'examples': ex})
        print('%-14s %3d examples from %3d texts%s'
              % (L['id'], len(ex), len({e['src'] for e in ex}), '' if ex else '   !! none found'))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// GENERATED by pipeline/grammar.py — do not edit by hand.\n')
        f.write('// Explanations + closed-class paradigm tables are hand-written (curated function\n')
        f.write('// words, urban notation). Example SENTENCES are selected from the ingested corpus,\n')
        f.write('// where every word was looked up in Maknuune — no Arabic is invented here.\n')
        f.write('window.GRAMMAR = ')
        json.dump({'lessons': lessons}, f, ensure_ascii=False)
        f.write(';\n')
    print('\n%d lessons -> %s' % (len(lessons), os.path.relpath(OUT, ROOT)))

if __name__ == '__main__':
    main()
