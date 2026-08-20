#!/usr/bin/env python3
"""Assemble texts/lessons/unit-NN.json from the transcribed reference library.

THE RULE THIS SCRIPT EXISTS TO ENFORCE: no Arabic is ever typed by hand here. Every Arabic
string in a lesson unit is COPIED verbatim out of texts/ref/<book>.json (the user's own
teaching materials, transcribed page by page), carrying its `src` page with it. What IS
authored here is the English scaffolding a self-study learner needs and a classroom handout
doesn't: the unit's objective, the grammar point in plain English, and the production prompt.

Units 1-4 were assembled by hand first (their greeting glosses were written one by one) and
are left alone; this generates unit 5 onward. Re-running is safe and idempotent.

Run:  python3 pipeline/lesson_author.py           # write the units
      python3 pipeline/lesson_author.py --check   # report what would be written, write nothing
"""
import argparse, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
REF = os.path.join(ROOT, 'texts', 'ref')
OUT = os.path.join(ROOT, 'texts', 'lessons')

_books = {}
def book(slug):
    if slug not in _books:
        _books[slug] = json.load(open(os.path.join(REF, slug + '.json'), encoding='utf-8'))
    return _books[slug]

def ref_unit(slug, n):
    for u in book(slug)['units']:
        if u.get('unit') == n:
            return u
    raise KeyError('%s unit %s not found' % (slug, n))

def ref_unit_titled(slug, needle):
    """Find a unit by title OR by one of its grammar topics — the meaning-lessons (صار, خَلّى)
    sit under a structural unit title like "Form 2, third radical ya"."""
    for u in book(slug)['units']:
        t = (u.get('title') or {})
        if needle in str(t.get('en') or '') or needle in str(t.get('ar') or ''):
            return u
        for s in u.get('sections', []):
            if s.get('kind') == 'grammar' and needle in str(s.get('topic') or ''):
                return u
    raise KeyError('%s title ~%s not found' % (slug, needle))

def secs(u, kind):
    return [s for s in u.get('sections', []) if s.get('kind') == kind]

# The books are a student's working copies: some glosses are pencil marginalia, some carry the
# transcriber's [notes], one or two are printed misprints. Keep the gloss clean and move the
# apparatus into `note` so the flashcard face stays readable and the provenance stays honest.
_FIX = {'nice': 'niece', 'pairs': 'pears', 'ether ...or': 'either … or', 'more then': 'more than',
        'caffee': 'coffee', 'exited': 'excited', 'principle': 'principal'}
def gloss(en):
    if not en:
        return None, None
    notes = re.findall(r'\[(.*?)\]', en)
    e = re.sub(r'\s*\[.*?\]', '', en)
    for tag in ('(handwritten)', '(printed)'):
        e = e.replace(tag, '')
    e = e.strip(' .;')
    if e in _FIX:
        notes.append('printed in the book as "%s"' % e)
        e = _FIX[e]
    return (e or None), ('; '.join(n for n in notes if n) or None)

def chunks_from(u, slug, group=None, limit=None):
    """Vocab items -> lesson chunks. Vocab always carries the book's own English, so these are
    safe to put on a flashcard; dialogue lines (usually untranslated in class handouts) do not
    become chunks — they render as dialogue instead."""
    out = []
    for s in secs(u, 'vocab'):
        g = group or (s.get('title') or None)
        for it in s.get('items', []):
            ar = (it.get('ar') or '').strip()
            if not ar:
                continue
            en, note = gloss(it.get('en'))
            c = {'ar': ar, 'en': en, 'src': '%s %s' % (slug, s.get('src') or '')}
            if g: c['group'] = g
            if note: c['note'] = 'book: ' + note
            out.append(c)
            if limit and len(out) >= limit:
                return out
    return out

def drills_from(u, slug, titles=None):
    out = []
    for i, s in enumerate(secs(u, 'drill')):
        items = [{'cue': it.get('cue'), 'answer': it.get('answer')} for it in (s.get('items') or [])
                 if it.get('cue')]
        if not items:
            continue
        t = (titles or {}).get(i) or (s.get('instructions') or 'Practice').strip()
        kind = 'roleplay' if 'role' in str(s.get('type') or '') or 'أدْوار' in str(s.get('instructions') or '') else 'qa'
        out.append({'type': kind, 'title': t[:70], 'instructions': s.get('instructions') or
                    'Answer out loud, in Arabic, in full sentences.',
                    'items': items, 'src': '%s %s' % (slug, s.get('src') or '')})
    return out

def dialogues_from(u, slug):
    out = []
    for s in secs(u, 'dialogue'):
        lines = [{'sp': l.get('sp'), 'ar': l.get('ar'), 'en': l.get('en')}
                 for l in (s.get('lines') or []) if l.get('ar')]
        if lines:
            out.append({'title': s.get('title'), 'lines': lines, 'src': '%s %s' % (slug, s.get('src') or '')})
    return out

def texts_from(u, slug):
    out = []
    for s in secs(u, 'text'):
        sents = [x for x in (s.get('sentences') or []) if (x.get('ar') if isinstance(x, dict) else x)]
        if sents:
            out.append({'title': s.get('title'), 'sentences': sents, 'src': '%s %s' % (slug, s.get('src') or '')})
    return out

def grammar_chunks(u, slug, glosses=None):
    """For the meaning-lessons, the grammar EXAMPLES are the content: each is a whole usable
    sentence, grouped under the meaning it illustrates. The book prints these untranslated (it
    expects a teacher in the room), so `glosses` supplies English positionally — the Arabic is
    still copied, only the English is authored."""
    out, i = [], 0
    for s in secs(u, 'grammar'):
        topic = re.sub(r'^.*?—\s*', '', str(s.get('topic') or '')).strip() or s.get('topic')
        for e in (s.get('examples') or []):
            ar = (e.get('ar') or '').strip()
            if not ar:
                continue
            en = e.get('en') or (glosses[i] if glosses and i < len(glosses) else None)
            c = {'ar': ar, 'en': en, 'group': topic, 'src': '%s %s' % (slug, s.get('src') or '')}
            if not e.get('en') and en:
                c['note'] = 'English added by this app — the book prints these untranslated'
            out.append(c)
            i += 1
    return out


def grammar_from(u, slug):
    """Ref grammar sections -> the unit's grammar block (verbatim topic/explanation/examples)."""
    gs = secs(u, 'grammar')
    if not gs:
        return None
    parts, ex = [], []
    for s in gs:
        if s.get('topic'):
            parts.append(s['topic'])
        for e in (s.get('examples') or []):
            if e.get('ar'):
                ex.append({'ar': e['ar'], 'en': e.get('en')})
    return {'point': parts[0] if parts else 'From the book',
            'topics': parts, 'examples': ex[:12],
            'src': '%s %s' % (slug, gs[0].get('src') or '')}


# ---------------------------------------------------------------------------------------------
# The spec. `src` entries are (book, unit-number) or (book, '~title-substring'). Everything in
# English below is authored for this app; everything in Arabic comes from the books.
# ---------------------------------------------------------------------------------------------
SPEC = [
 dict(n=5, phase=2, gram='nominal', src=[('speaking', 6), ('speaking', 18), ('speaking', 15)],
   title_en='Days, times & when things happen',
   objective='Say what day it is, what time it is, and when something happened or will happen. '
             'Note that Arabic tells the time with no verb at all — الساعة وحدة is literally '
             '"the hour one".',
   point='Telling the time takes no verb',
   body='This is the no-“is” sentence you already know, doing real work: الساعة plus a number '
        'IS the sentence. The book’s own examples run through the clock and then add the part of '
        'day — morning, afternoon, evening — on the end.',
   produce='Out loud: today’s day and date, the time right now, what time you got up, and what '
           'time you’ll eat dinner.'),

 dict(n=6, phase=2, gram='fi', src=[('speaking', 7)],
   title_en='The town and the village',
   objective='Describe where you live — the buildings, the streets, what your area has and hasn’t '
             'got. This is the vocabulary a host will use in the first ten minutes of showing you around.',
   point='في — “there is”, and “in”',
   body='The same little word does both jobs: في المَدينة سينما ("there’s a cinema in town") uses '
        'في twice over — once as "in", once as "there is". Negate it with ما في.',
   produce='Describe your own town out loud in five sentences: what there is, what there isn’t, '
           'and what you like about it.'),

 dict(n=7, phase=2, gram='fi', src=[('speaking', 24)],
   title_en='The house',
   objective='Name the rooms and the things in them — so you can be shown around a home, offered a '
             'seat, and asked to pass something, without losing the thread.',
   point='Rooms, and what’s in them',
   body='Pair each room word with في and a thing that lives there. The book’s list is ordered the '
        'way you’d walk through a house, which is also the order you’ll be shown one.',
   produce='Walk through your own home out loud, room by room, saying one thing that’s in each.'),

 dict(n=8, phase=2, gram='bpresent', src=[('speaking', 23)],
   title_en='Your day, start to finish',
   objective='Narrate an ordinary day — waking, eating, working, coming home. Everyday habitual '
             'actions are exactly what the b- present is for, so this unit is where that pattern '
             'starts paying off.',
   point='The b- present is the everyday tense',
   body='بَصْحى، بَاكُل، بَشْتْغِل — the بـ on the front marks what you habitually do. It is the '
        'workhorse tense of ordinary talk, and a daily routine is the cleanest place to drill it.',
   produce='Tell your whole day in order, out loud, in the b- present. Then tell it again about '
           'someone else in your family (he/she forms).'),

 dict(n=9, phase=2, gram='pronouns', src=[('speaking', 25)],
   title_en='Who I am',
   objective='The paperwork of being a person — name, age, where you’re from, what you are. The '
             'questions you get asked first, and the ones you’ll be asked at every border.',
   point='I, you, he — and the words that follow them',
   body='This unit is where the pronouns stop being a table and start being sentences: أنا plus a '
        'noun, إنت plus a question. No verb needed for any of it.',
   produce='Introduce yourself out loud in six sentences, then do it again as if introducing '
           'someone else in your family.'),

 dict(n=10, phase=2, gram='baddi', src=[('speaking', 14)],
   fill_en=["I like going on trips", "I like going for walks in nature", "I listen to music", "I cook", "I like learning", "I like travelling", "I like eating in restaurants", "I like sitting in cafés", "I swim", "I talk with my friends", "I sit in cafés", "I go shopping", "I play football / tennis / basketball"],
   title_en='Hobbies & free time',
   objective='Say what you like doing, what you do at weekends, and what you’d rather be doing — '
             'the reliable escape hatch when dinner conversation runs dry.',
   point='بحِبّ + a verb — “I like to…”',
   body='بَحِبّ اقرا, بَحِبّ اسْبَح — like/want words take a following verb with no “to”. Pair it with '
        'بدّي from the grammar lessons and you can express most of what you feel like doing.',
   produce='Say three things you like doing, one you hate, and one you want to try — out loud, '
           'with a reason for each.'),

 dict(n=11, phase=2, gram='idafa', src=[('speaking', 10)],
   title_en='Food & the vegetable market',
   objective='Name what’s on the table and what’s on the stall. This is the single most useful '
             'vocabulary list in the book for a dinner guest.',
   point='Stacking nouns instead of saying “of”',
   body='There is no word for “of”: سَلَطَة خُضْرَة is "salad (of) vegetables", كيلو بَنْدُورة is "a kilo '
        '(of) tomatoes". Just put the two nouns together, in that order.',
   produce='Out loud: order a kilo of three things, then say what you ate yesterday and what you '
           'never eat.'),

 dict(n=12, phase=3, gram='gender', src=[('speaking', 20), ('speaking', 21)],
   title_en='Colours & opposites',
   objective='Describe things — and their opposites. Colours behave like adjectives, which means '
             'they have to agree with what they describe, and that agreement is the point of the unit.',
   point='Adjectives agree with their noun',
   body='A masculine thing takes the plain adjective, a feminine thing takes the ة form: بيت أَبْيَض '
        'but سَيّارة بيضا. The opposites list is the fastest way to double this vocabulary.',
   produce='Look around the room and describe five things out loud, each with a colour and one '
           'other adjective — watching the agreement.'),

 dict(n=13, phase=3, gram='nominal', src=[('speaking', 16)],
   fill_en=["month one (January)", "month two (February)", "month three (March)", "month four (April)", "month five (May)…", "(July)… (August)… (September)… (October)… (November)… (December)"],
   title_en='Seasons & weather',
   objective='Talk about the weather — the universal opener, and in this region a real topic: heat, '
             'rain, and which season everything happens in.',
   point='Weather sentences need no verb either',
   body='إلجَوّ حِلو, إلدُّنْيا شوب — subject then description, nothing in between. Same nominal '
        'sentence, new vocabulary.',
   produce='Describe today’s weather, your favourite season and why, and what the weather was like '
           'last week — out loud.'),

 dict(n=14, phase=3, gram='gender', src=[('speaking', 17)],
   title_en='Animals',
   objective='Farm animals, house animals, and the ones that turn up in every proverb and children’s '
             'story you’ll ever be told.',
   point='Sound and broken plurals, in one list',
   body='Animal words show off both plural types at once — some add an ending, many change shape '
        'internally (كَلْب ← كْلاب). Learn each plural with its singular; there is no shortcut.',
   produce='Name five animals with their plurals out loud, and say which you’d keep and which you’d '
           'never have in the house.'),

 dict(n=15, phase=3, gram='nominal', src=[('speaking', 29)],
   title_en='Feelings & emotions',
   objective='Say how you actually feel, and ask how someone else does — the interiority that makes '
             'you a person at the table rather than a polite guest reciting facts.',
   point='أنا + how you are',
   body='مَبْسوط، زَعْلان، تَعْبان — these are adjectives, so they agree with you: مَبْسوط if you’re '
        'a man, مَبْسوطة if you’re a woman. No verb; just أنا and the state.',
   produce='Say how you feel right now and why; then how you felt yesterday and why it changed.'),

 dict(n=16, phase=3, gram='baddi', src=[('speaking', 30)],
   title_en='Values — what matters to you',
   objective='The vocabulary of what you believe in and care about. This is where dinner conversation '
             'goes once the pleasantries are done.',
   point='Saying what matters',
   body='Abstract nouns behave like any other noun — الصِّدْق مُهِمّ ("honesty is important") is still '
        'just a nominal sentence. Stack these with بدّي and بَحِبّ to say what you want and value.',
   produce='Name three things you value and say why, out loud, one sentence each.'),

 dict(n=17, phase=3, gram='questions', src=[('speaking', 39), ('speaking', 40), ('speaking', 41),
                                            ('speaking', 42), ('speaking', 43)],
   fill_en=["oxygen"],
   title_en='شو رايَك؟ — saying what you think',
   objective='The book closes with five rounds of exactly one question: what do you think? Agreeing, '
             'disagreeing, hedging, giving a reason. This is the unit that turns vocabulary into opinion.',
   point='Asking for and giving an opinion',
   body='شو رايَك؟ literally "what is your opinion?" — رأي plus the possessive ending you already know. '
        'Answer with بَعْتِقِد ("I think"), بِالنِّسْبِة إلي ("for me"), or straight agreement/disagreement.',
   produce='Take any topic from the drills and speak for sixty seconds: your opinion, one reason, '
           'one thing you’d concede to someone who disagreed.'),

 dict(n=18, phase=3, gram='negation', src=[('speaking', 34)],
   title_en='Allowed & forbidden',
   objective='مَمْنوع and مَسْموح — the language of rules, permission and refusal, including how to '
             'say no to a third helping without offending anyone.',
   point='Saying no, and saying not allowed',
   body='ما and مش negate different things — and مَمْنوع does the job on its own. The dialogues here '
        'show refusal done politely, which is the version you actually need.',
   produce='Out loud: three things forbidden where you live, one thing you’re not allowed to do, and '
           'a polite refusal of food you don’t want.'),

 dict(n=19, phase=4, gram='past', src=[('speaking', 12), ('speaking', 13)],
   title_en='Travelling — journeys & the bus',
   objective='Getting somewhere: tickets, stops, asking where the bus goes, and telling the story of '
             'a trip afterwards.',
   point='Telling it in the past',
   body='A journey is a story, so it lives in the past tense: سافَرْت، وِصِلْت، رِكِبْت. The dialogue '
        'here is two friends arguing about buses — read it, then retell it as something that '
        'happened to you.',
   produce='Tell the story of a real journey out loud in the past tense: where, how, how long, what '
           'went wrong.'),

 dict(n=20, phase=4, gram='kaan', src=[('speaking', 28)],
   title_en='Old times',
   objective='How things used to be — the register every older relative at the table will reach for '
             'within about twenty minutes.',
   point='كان — was, were, used to',
   body='كان plus the b- present is "used to": كان بِيشْتْغِل ("he used to work"). That one combination '
        'unlocks every "back in the day" story you will ever be told.',
   produce='Describe how something used to be — your town, your job, your family — in five sentences '
           'with كان.'),

 dict(n=21, phase=4, gram='past', src=[('verb-drills', '~The meanings of Saar')],
   from_grammar=True,
   glosses=["What happened?", "What happened to you? (m / f)", "What’s happening tomorrow?",
            "He’s become a big boy.", "She became Israeli — you’d never guess she was born in America.",
            "My love has turned romantic. He brings me chocolate and flowers.",
            "I’ve been living in Jerusalem for five years.", "We’ve been married three years.",
            "Mohammed has been studying at the university for two years.",
            "How long have you (pl.) been here?", "It’s been two weeks since she saw her mother.",
            "He started understanding Arabic.", "She started crying.", "I started talking to him.",
            "— Have you seen Mohammed? — He’s already been travelling for a week.",
            "My daughter started learning two months ago and she can already write and read.",
            "— Did Amir bring you the money? — Yes, he’s already put down half the amount.",
            "Yesterday there were no tomatoes in the market, and today there are.",
            "Mahmoud used to be poor, and now he has a house and everything.",
            "There was no electricity all morning. Suddenly there was. Who fixed it?",
            "They haven’t fixed the electricity! That’s not on!"],
   title_en='صار — the verb that does seven jobs',
   objective='One verb, seven distinct meanings, all of them common: it happened, it became, it’s been '
             'X years, he started to, he already has, now there is, and "that’s not on". Learning صار '
             'properly is one of the biggest single jumps in sounding fluent.',
   point='Seven meanings of صار',
   body='The book lays them out one at a time with examples. Read each meaning, then say the examples '
        'out loud until the pattern of each one is in your ear — they are distinguished by what '
        'follows صار, not by the verb itself.',
   produce='Make one sentence of your own for each of the seven meanings, out loud. This is hard; do '
           'it anyway — it is the whole point of the unit.'),

 dict(n=22, phase=4, gram='future', src=[('speaking', 37)],
   title_en='Plans for the future',
   objective='What you’re going to do — next week, next year, one day. رح plus a verb, and the '
             'vocabulary of intention.',
   point='رح — the future',
   body='رح plus the bare present makes the future: رح أسافِر ("I’ll travel"). Pair it with بدّي '
        '("I want to") and لازِم ("I have to") to say not just what will happen but why.',
   produce='Say three plans out loud — one for this week, one for this year, one you may never do — '
           'each with a reason.'),

 dict(n=23, phase=5, gram='baddi', src=[('verb-drills', '~The meanings of خَلّى')],
   from_grammar=True,
   glosses=["I left the milk at the shop.", "My daughter leaves the book on the table.",
            "Please leave your bag there (leave it there).",
            "Let it go — forget about it. (literally: leave it to whoever took it)",
            "Her father made her study all night.",
            "What he said made me understand that he loves me a lot.",
            "Her story makes me cry.", "That music made us feel as if we were in paradise.",
            "Let me come with you!", "The teacher doesn’t let us play outside.",
            "Let us watch the film together!", "Stay sitting! (to a man)",
            "Stay sitting! (to a woman)", "Stay sitting! (to a group)",
            "Keep quiet, students!", "Stay asleep a little longer! (to a group of women)",
            "Stay here!", "Stay at home! (to a woman)", "Keep going straight.",
            "Stay till the end.", "Please! Bring me the books from my room.",
            "Please, come back in an hour. (to a woman)"],
   title_en='خلّى — leave it, let me, make me',
   objective='The other verb that does several jobs at once: to leave something, to make someone do '
             'something, to let someone, to stay put, and to ask a favour. Enormously common and '
             'almost never taught.',
   point='Five meanings of خَلّى',
   body='As with صار, what follows the verb decides the meaning — a noun, a person plus a verb, or an '
        'imperative. خَلّيك قاعِد ("stay sitting") and الله يْخَلّيك ("please / God keep you") are both '
        'daily-life phrases hiding in this one root.',
   produce='Use خَلّى three ways out loud: leave something somewhere, ask to be let do something, and '
           'ask someone a favour.'),

 dict(n=24, phase=5, gram='relative', src=[('speaking', 36), ('speaking', 26)],
   fill_en=["cartoons / animated films", "documentaries", "historical films", "romantic films", "nature films", "science programmes", "detective films", "children's programmes", "radio", "television", "internet", "Facebook"],
   title_en='Books, films & the news',
   objective='Talking about what you’ve read, watched and heard — including how to say "the film that '
             'I saw", which is where اللي earns its keep.',
   point='اللي — the one that',
   body='اللي covers who, which and that: الفيلم اللي شُفْتُه ("the film that I saw"). It never changes '
        'shape, which makes it one of the easiest big wins in the language.',
   produce='Describe a book or film out loud using اللي at least twice, and say whether you’d '
           'recommend it.'),

 dict(n=25, phase=6, gram='indi', src=[('speaking', 9), ('speaking', 19), ('speaking', 11)],
   fill_en=["Where is the bathroom?"],
   title_en='At the table — visiting, coffee & what’s cooking',
   objective='The hospitality unit, and the closest thing in the book to the dinner table itself: '
             'preparing to visit a family, how Arabic coffee is actually made, and a recipe read '
             'end to end in Arabic.',
   point='Being a guest',
   body='Hospitality runs on fixed phrases more than grammar — the offering, the refusing once before '
        'accepting, the blessing of the cook’s hands. Take these as whole chunks; that is how they '
        'are used.',
   produce='Out loud: accept a coffee, compliment the food, refuse a third helping politely, and '
           'bless the hands that cooked it.'),

 # ---- the bulk mining pass: everything substantial the books still had left ----
 # Weighted hard toward phases 4-6, which carried 1,475 of the 2,000 planned hours but only a
 # handful of units. Story units are whole graded readings with their own قاموس and the books'
 # retell/perspective-shift exercises — the 4/3/2 pedagogy, natively confirmed.

 dict(n=26, phase=2, gram='idafa', src=[('speaking', 2)],
   title_en='Capitals of the Arab world',
   objective='The capitals, so a place name in the news or across the table is a place and not a '
             'noise. Pairs directly with the countries you already learned.',
   point='"The capital of Jordan" — no word for "of"',
   body='عاصْمِة الأُرْدُن stacks the two nouns and lets the order do the work, exactly like '
        'سَلَطَة خُضْرَة. The first noun never takes الـ in this construction.',
   produce='Out loud: name five capitals with their countries, then say which you have been to.'),

 dict(n=27, phase=2, gram='fi', src=[('vocab-gram', '~Prepositions')],
   from_grammar=True,
   title_en='Prepositions — in, on, with, from',
   objective='The small words that put everything else in place. They are few, they are constant, '
             'and they carry pronoun endings, which is what makes them worth a unit of their own.',
   point='Prepositions take the possessive endings',
   body='مَعي (with me), مِنُّه (from him), عَلَيها (on her) — the same endings you learned on nouns '
        'attach here too. Learn the preposition and its endings as one set.',
   produce='Say where five things in the room are, out loud, each with a different preposition.'),

 dict(n=28, phase=3, gram='gender', src=[('vocab-gram', '~Adjectives')],
   fill_en=["mature, sensible", "calm, quiet", "wide, spacious"],
   title_en='Adjectives — describing people and things',
   objective='A large, ordered adjective list plus the agreement rules the book states outright. '
             'This is the vocabulary that turns bare naming into description.',
   point='Agreement in spoken Arabic',
   body='The book gives the rules of agreement in ʿāmmiyye directly: the adjective follows its '
        'noun and matches it. Definite noun, definite adjective — البيت الكبير, not البيت كبير '
        '(which is a whole sentence, "the house is big").',
   produce='Describe three people you know out loud, two adjectives each, watching the agreement.'),

 dict(n=29, phase=3, gram='relative', src=[('vocab-gram', '~Conjunctions')],
   title_en='Joining sentences up',
   objective='Because, but, so, when, if. Fifty-odd connectors — the difference between speaking in '
             'fragments and speaking in paragraphs.',
   point='Connectors carry the argument',
   body='Every one of these lets you attach a reason, a contrast or a condition to what you just '
        'said. Learning even ten well is what makes an opinion sound like an opinion rather than a '
        'list of facts.',
   produce='Say one sentence, then extend it three times with a different connector each time.'),

 dict(n=30, phase=3, gram='gender', src=[('vocab-gram', '~Singular and plural')],
   title_en='Singular & plural — the big glossary',
   objective='Two hundred everyday nouns, each printed with its plural. Arabic plurals mostly cannot '
             'be predicted, so they have to be learned in pairs — and this is the list to learn them from.',
   point='Learn the plural WITH the singular',
   body='Some plurals just add an ending; most change the word internally (كِتاب ← كُتُب). There is '
        'no reliable rule, which is exactly why the book prints them side by side. Never learn a '
        'noun without its plural.',
   produce='Pick twenty from the list and say each pair out loud: one book, two books, many books.'),

 dict(n=31, phase=4, gram='past', src=[('vocab-gram', '~Broken and Sound Plurals')],
   from_grammar=True,
   title_en='Plural patterns — the shapes behind them',
   objective='After learning plurals one by one, this is the pattern behind them: the handful of '
             'shapes most broken plurals actually fall into.',
   point='مَفاعِل, فْعال, أفْعال and friends',
   body='The book lays out the recurring templates. You still cannot predict which noun takes which, '
        'but recognizing the shapes makes the plurals you meet in reading far easier to place.',
   produce='Sort twenty plurals you already know into the book’s patterns, out loud.'),

 dict(n=32, phase=4, gram='questions', src=[('speaking', 22)],
   title_en='On the phone',
   objective='A phone call is the hardest ordinary conversation: no face, no gestures, no lip-reading. '
             'Three real dialogues of someone trying to reach a family.',
   point='Phone-call formulas',
   body='Calls run on fixed openers and closers — asking for someone, saying who you are, saying '
        'they are not in, leaving a message. Take them as whole chunks; that is how they are used.',
   produce='Role-play a call out loud: ask for someone, be told they are out, leave a message.'),

 dict(n=33, phase=4, gram='past', src=[('stories', 1)],
   title_en='The camel who wanted to learn',
   objective='Your first full story in Palestinian, with its own glossary and the book’s retell '
             'exercises. Read it, then tell it back — that retelling is the whole point.',
   point='Narrative runs in the past',
   body='A story is a chain of past-tense verbs with connectors between them. Read for the chain '
        'first: who did what, then what happened next.',
   produce='Tell the story from memory, out loud, in under two minutes. Then again in one.'),

 dict(n=34, phase=4, gram='past', src=[('stories', 2)],
   fill_en=["the time came"],
   title_en='The man and the mouse',
   objective='A longer story in five parts with a big glossary — the step up from the first one, and '
             'the book’s pronoun-shift drill on top.',
   point='Changing who the story is about',
   body='The book’s exercise asks you to change the pronouns of the underlined sentences and retell. '
        'That single drill forces every ending in the language to become active rather than recognized.',
   produce='Retell the story as if it happened to YOU — first person throughout.'),

 dict(n=35, phase=4, gram='past', src=[('stories', 3)],
   title_en='The fisherman and the rich tourist',
   objective='The well-known parable, in Palestinian, with its glossary and retell drills. Short, '
             'pointed, and the kind of story that actually gets told at a table.',
   point='Telling a story with a point',
   body='This one has a punchline, which means the telling has to build. Notice where the book’s '
        'text slows down and where it moves — that pacing is what you are copying.',
   produce='Tell it to someone in under ninety seconds, landing the ending.'),

 dict(n=36, phase=4, gram='kaan', src=[('stories', 4)],
   title_en='The king and the shirt',
   objective='A folk tale with a moral, its glossary, and the perspective-shift exercise the book is '
             'fond of — tell it again as a different character.',
   point='Retelling from another point of view',
   body='The book asks each group to tell the story from a different character’s side while the rest '
        'guess who. It is the most demanding speaking exercise in the whole reader, and the most useful.',
   produce='Tell the story from the king’s point of view, then from the shirt-owner’s.'),

 dict(n=37, phase=5, gram='wadi-ara', src=[('stories', 5)],
   title_en='The golden lira — a story in Galilee dialect',
   objective='A six-part story printed deliberately in the GALILEE dialect rather than the urban '
             'speech the rest of the app teaches. Hearing the difference is the skill here.',
   point='Not everyone speaks the way this app teaches',
   body='The app’s baseline is urban (Jerusalem/Ramallah/Nablus). This story is northern, and prints '
        'forms the city would say differently. That is not an error in either — it is what regional '
        'variation looks like on the page. Compare it with the Wadi Ara accent lesson.',
   produce='Read a passage aloud twice: once as printed, once "translated" into the urban forms.'),

 dict(n=38, phase=5, gram='past', src=[('stories', 6)],
   title_en='Kanafani — the little lamp',
   objective='Real Palestinian literature, by Ghassan Kanafani, in five parts. No glossary and no '
             'exercises — just the text, which is the point: this is reading for its own sake.',
   point='Literary Arabic, read for pleasure',
   body='This is a step above everything before it and is meant to be. Read for the shape of it; '
        'look up what stops you and let the rest go by.',
   produce='Say what happens, in your own words, in five sentences.'),

 dict(n=39, phase=5, gram='baddi', src=[('speaking', 38)],
   title_en='Love?',
   objective='Three short texts on the subject every dinner table gets to eventually, with the '
             'book’s discussion questions.',
   point='Talking about feelings you have opinions about',
   body='This unit is discussion, not vocabulary: the texts exist to be argued with. Use the '
        'opinion frames from the شو رايَك؟ unit.',
   produce='Answer the book’s questions out loud, in full sentences, with a reason for each.'),

 dict(n=40, phase=5, gram='questions', src=[('speaking', 33)],
   title_en='Women and men',
   objective='A discussion text on roles and expectations — the kind of subject where you need to be '
             'able to disagree politely and still be understood.',
   point='Disagreeing without falling out',
   body='Pair the opinion frames with hedges: بِالنِّسْبِة إلي (for me), مُمْكِن (maybe), '
        'بَسّ (but). Softening is what keeps a strong opinion sociable.',
   produce='Give your view, then argue the opposite side as convincingly, out loud.'),

 dict(n=41, phase=5, gram='baddi', src=[('speaking', 35)],
   title_en='Diets & eating well',
   objective='Twenty-five terms for food, health and what you do or don’t eat — which at a Palestinian '
             'table is genuinely practical vocabulary.',
   point='Saying what you don’t eat',
   body='Combine بَاكُلْش / ما بَاكُل with the food words, and pair with the polite refusals from the '
        'hospitality unit. Refusing food gracefully is a real skill here.',
   produce='Explain what you eat and don’t eat, and why, out loud — then refuse a dish politely.'),

 dict(n=42, phase=5, gram='bpresent', src=[('speaking', 27)],
   title_en='Learning and teaching Arabic',
   objective='A text about learning the language, in the language — plus the book’s questions about '
             'how you are finding it.',
   point='Talking about the thing you are doing',
   body='Being able to discuss your own learning — what is hard, what helps — is unusually useful: '
        'it is the conversation you will have with every teacher and every patient friend.',
   produce='Out loud: what you find hardest, what has helped most, what you want next.'),

 dict(n=43, phase=5, gram='kaan', src=[('speaking', 32)],
   title_en='Independence Day and the Arab minority',
   objective='Vocabulary and questions on a subject that is unavoidable and genuinely sensitive. The '
             'book presents it as a discussion; so does this unit.',
   point='Sensitive subjects, carefully',
   body='This is the vocabulary of a difficult conversation. The value is being able to listen and '
        'ask rather than to argue — and to understand what is being said around you.',
   produce='Practise asking, not asserting: three questions you could genuinely ask someone.'),

 dict(n=44, phase=5, gram='past', src=[('spoken-extra', 3)],
   title_en='Ziyad and Abu Siwar',
   objective='A natural two-person conversation from the Givat Haviva packet — ordinary talk at '
             'ordinary speed, with a short glossary.',
   point='Following a conversation you are not in',
   body='Listening to two other people talk is harder than being addressed, because nobody is '
        'accommodating you. Read it, then listen without reading.',
   produce='Summarize what the two of them settled, out loud, in three sentences.'),

 dict(n=45, phase=6, gram='indi', src=[('speaking', 31)],
   title_en='Visits on occasions',
   objective='What you say at a wedding, a birth, a condolence visit, a holiday. Hospitality has '
             'fixed language for every occasion, and getting it right matters more than fluency.',
   point='The right phrase for the occasion',
   body='These are formulas, not sentences you compose. Each occasion has its greeting and its '
        'expected answer, exactly like the greetings unit — learn them in pairs.',
   produce='Out loud: congratulate a new marriage, a new baby, and offer condolences.'),

 dict(n=46, phase=6, gram='past', src=[('spoken-extra', 6)],
   title_en='Majed got engaged',
   objective='A conversation about an engagement — the single most common piece of family news, and '
             'a scene you will sit through many times.',
   point='Reacting to news',
   body='This is where the Reactions unit pays off: مبروك, والله؟, ما شاء الله. Follow the '
        'conversation and notice how much of it is reaction rather than information.',
   produce='Someone tells you a family member got engaged. React, ask two questions, congratulate.'),

 dict(n=47, phase=6, gram='baddi', src=[('spoken-extra', 7)],
   title_en='Before the market',
   objective='Planning a shopping trip out loud — what is needed, who is going, what it costs. '
             'Everyday domestic negotiation.',
   point='Working out a plan together',
   body='Notice how the plan is made: suggestions, objections, agreement. That three-move pattern is '
        'most of domestic conversation everywhere.',
   produce='Plan a shopping trip out loud with an imagined partner: propose, object, agree.'),

 dict(n=48, phase=6, gram='baddi', src=[('spoken-extra', 9)],
   title_en='Rana returns some disks',
   objective='A short transactional dialogue — wanting to exchange something. The politeness of '
             'asking for something you are entitled to.',
   point='Asking for something, politely',
   body='بِدّي plus a soft opener does most of the work. Transactions are formulaic, which makes '
        'them a cheap win: learn the frame once and swap the noun.',
   produce='Out loud: return something to a shop and ask to exchange it.'),

 dict(n=49, phase=6, gram='past', src=[('spoken-extra', 10)],
   title_en='The mosquito and the wind',
   objective='A short fable with a glossary — light reading to finish on, and a story short enough '
             'to actually memorize and retell.',
   point='A story you can carry',
   body='Short fables are the most useful stories to know by heart: they fit in a gap in conversation '
        'and they always land.',
   produce='Learn it well enough to tell it from memory, out loud, with no notes.'),

 dict(n=50, phase=6, gram='idafa', src=[('vocab-gram', '~Mass Nouns')],
   from_grammar=True,
   title_en='Counting food — mass nouns & unit words',
   objective='How to ask for an amount of something that has no plural: a head of lettuce, a clove '
             'of garlic, a grain of rice. The last piece of table and market language.',
   point='حَبَّة, راس, قَرْن — the unit words',
   body='You cannot say "two lettuces". The book gives two methods and a reference table of which '
        'unit word goes with which produce — that table is the unit.',
   produce='Out loud: order six different things by their correct unit word.'),
]


def build(spec):
    slug_first = spec['src'][0][0]
    chunks, drills, dialogues, texts, gram_ref, srcs = [], [], [], [], None, []
    ar_title = None
    for slug, key in spec['src']:
        u = ref_unit_titled(slug, key[1:]) if isinstance(key, str) and key.startswith('~') \
            else ref_unit(slug, key)
        t = (u.get('title') or {})
        if not ar_title and t.get('ar'):
            ar_title = t['ar']
        if spec.get('from_grammar'):
            chunks += grammar_chunks(u, slug, spec.get('glosses'))
            continue
        chunks += chunks_from(u, slug)
        drills += drills_from(u, slug)
        dialogues += dialogues_from(u, slug)
        texts += texts_from(u, slug)
        gram_ref = gram_ref or grammar_from(u, slug)
        srcs.append('%s %s' % (slug, '-'.join(str(x) for x in (u.get('pages') or []))))

    # de-dupe chunks that appear in more than one source unit
    seen, uniq = set(), []
    for c in chunks:
        k = c['ar']
        if k in seen:
            continue
        seen.add(k); uniq.append(c)

    # Some pages are printed Arabic-only (the class had a teacher to gloss them). Fill those in
    # positionally, in the order they appear, so a flashcard never ends up with a blank meaning.
    fill = list(spec.get('fill_en') or [])
    if fill:
        for c in uniq:
            if not c.get('en') and fill:
                c['en'] = fill.pop(0)
                c['note'] = 'English added by this app — the book prints this list untranslated'
        if fill:
            print('  !! unit-%02d: %d unused fill_en entries' % (spec['n'], len(fill)))

    grammar = {'point': spec['point'], 'body': spec['body']}
    if gram_ref:
        grammar['examples'] = [e for e in gram_ref['examples'] if e.get('ar')][:10]
        grammar['src'] = gram_ref['src']
        if len(gram_ref.get('topics') or []) > 1:
            grammar['topics'] = gram_ref['topics']
    return {
        'id': 'unit-%02d' % spec['n'], 'n': spec['n'], 'phase': spec['phase'],
        'title': {'ar': ar_title, 'en': spec['title_en']},
        'objective': spec['objective'],
        'src': ', '.join(srcs), 'gram_id': spec['gram'],
        'grammar': grammar,
        'chunks': uniq, 'dialogues': dialogues, 'texts': texts, 'drills': drills,
        'produce': spec['produce'], 'provenance': 'ref:' + slug_first,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='report only, write nothing')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for spec in SPEC:
        u = build(spec)
        tot += len(u['chunks'])
        print('unit-%02d %-46s %3d chunks · %d drills · %d dlg · %d texts'
              % (spec['n'], spec['title_en'][:46], len(u['chunks']), len(u['drills']),
                 len(u['dialogues']), len(u['texts'])))
        if not a.check:
            p = os.path.join(OUT, u['id'] + '.json')
            json.dump(u, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%d units · %d chunks%s' % (len(SPEC), tot, ' (check only, nothing written)' if a.check else ''))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
