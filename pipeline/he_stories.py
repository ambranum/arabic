#!/usr/bin/env python3
"""Beginner short stories in spoken Israeli Hebrew -> texts/he/story-beg-NN.json.

This is the one piece of Hebrew content that is WRITTEN rather than looked up, and it is worth
being plain about what that means. The Ben-Yehuda shelf is somebody else's published Hebrew,
transcribed; the news is written but tied to real headlines; the sounds, the reactions and the
grammar are curated teaching over words the lexicon supplies. These are prose, by Claude, and
the app flags every one of them as not native-checked.

What can still be checked is checked, and the build refuses a story that fails:

  * EVERY WORD MUST BE IN THE LEXICON. A story is only useful here if the reader can tap any
    word in it -- a story built on words the app cannot gloss teaches nothing and looks broken.
  * REGISTER. The same two measures the Ben-Yehuda gate uses, against the daily paper: no
    biblical vav-consecutive verbs at all, and archaic function words near zero. Written Hebrew
    drifts literary without meaning to, and a "beginner" story with אֲשֶׁר in it is not one.
  * LEVEL. Beginner means short sentences; the gate holds them under nine words.

Deliberately unpointed, like the news. Vowels come from the lexicon at ingest, where they are
looked up -- pointing is the one thing a generator should not be trusted with, and it is the
one thing this project has never generated.

    python3 pipeline/he_stories.py --lang he           # check only
    python3 pipeline/he_stories.py --lang he --write   # write texts/he/story-beg-NN.json
"""
import argparse
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')

import he_ingest                                    # noqa: E402
from lex import Lexicon                             # noqa: E402

SRC = ('Beginner short story written in spoken Israeli Hebrew by Claude. '
       'NOT native-validated.')

WORD = re.compile(r'[֐-׿]+(?:["\'׳״][֐-׿]+)*')
ARCHAIC = {'אשר', 'הנה', 'פן', 'לבלתי', 'בטרם', 'למען', 'אולם', 'אנכי', 'הלא', 'עתה', 'כה',
           'טרם', 'זולת', 'הללו', 'ויהי'}
# The vav-consecutive is ו + a PREFIX-CONJUGATED verb: וַיֹּאמֶר, וַתֵּלֶךְ. Unpointed, that is
# just ו followed by something starting י/ת/א/נ, which also describes וְיַיִן "and wine" and
# וְיוֹשֵׁב "and sits" -- both of which the first version of this gate refused. So the test is not
# the shape, it is the LEXICON: strip the vav and ask whether what is left is an attested future
# form and nothing else. A word that is also a noun or a participle is not one of these.
VAV_PREFIX = re.compile(r'^ו[יתאנ]')


def _future_only(lex, key):
    rows = lex.by_form.get(key) or []
    if not rows:
        return False
    kinds = {str(r['ANALYSIS'] or '') for r in rows}
    # Every reading a VERB, at least one of them future. "All readings future" was too strict:
    # יאמר carries the lemma's own bare VERB rows alongside VERB:future and so slipped through.
    # "Any reading future" would be too loose the other way.
    return any('future' in k for k in kinds) and all(k.startswith('VERB') for k in kinds)


def vav_consecutives(lex, toks):
    from build_lex import he_norm
    out = []
    for t in toks:
        if VAV_PREFIX.match(t) and len(t) > 3 and _future_only(lex, he_norm(t[1:])):
            out.append(t)
    return out
MAX_SENTENCE = 9.0          # beginner: short sentences, and the gate holds them there
MAX_UNKNOWN = 0             # every word taps

# (title_he, title_en, [(he, en), ...])
STORIES = [
 ("קפה של בוקר", "Morning Coffee", [
   ("כל בוקר אני קם בשבע.", "Every morning I get up at seven."),
   ("אני הולך למטבח ועושה קפה.", "I go to the kitchen and make coffee."),
   ("אני אוהב קפה שחור, בלי סוכר.", "I like black coffee, without sugar."),
   ("אני יושב ליד החלון ושותה לאט.", "I sit by the window and drink slowly."),
   ("בחוץ יש שמש והרחוב שקט.", "Outside there's sun and the street is quiet."),
   ("אחר כך אני מתלבש והולך לעבודה.", "Afterwards I get dressed and go to work."),
 ]),
 ("המשפחה שלי", "My Family", [
   ("קוראים לי דני ויש לי משפחה גדולה.", "My name is Danny and I have a big family."),
   ("אבא שלי עובד בשוק ואמא שלי מורה.", "My dad works at the market and my mum is a teacher."),
   ("יש לי אח קטן ואחות גדולה.", "I have a little brother and a big sister."),
   ("סבתא שלי גרה איתנו בבית.", "My grandmother lives with us in the house."),
   ("בשישי בערב כולם אוכלים ביחד.", "On Friday evening everyone eats together."),
   ("אני אוהב את המשפחה שלי מאוד.", "I love my family very much."),
 ]),
 ("האוטובוס", "The Bus", [
   ("אני מחכה לאוטובוס בתחנה.", "I'm waiting for the bus at the stop."),
   ("האוטובוס מאחר קצת, כמו תמיד.", "The bus is a little late, as always."),
   ("יש הרבה אנשים בתחנה.", "There are a lot of people at the stop."),
   ("סוף סוף האוטובוס מגיע.", "Finally the bus arrives."),
   ("אני עולה ומוצא מקום ליד החלון.", "I get on and find a seat by the window."),
   ("בדרך אני מסתכל על העיר.", "On the way I look at the city."),
 ]),
 ("בשוק", "At the Market", [
   ("ביום שישי אני הולך לשוק.", "On Friday I go to the market."),
   ("בשוק יש ירקות, פירות ולחם טרי.", "At the market there are vegetables, fruit and fresh bread."),
   ("המוכר צועק על העגבניות שלו.", "The seller shouts about his tomatoes."),
   ("אני קונה עגבניות, מלפפונים ולחם.", "I buy tomatoes, cucumbers and bread."),
   ("הכול טרי וזול.", "Everything is fresh and cheap."),
   ("אני חוזר הביתה עם שקיות כבדות.", "I go home with heavy bags."),
 ]),
 ("החתול שלנו", "Our Cat", [
   ("יש לנו חתול קטן.", "We have a little cat."),
   ("הוא ישן כל היום על הספה.", "He sleeps all day on the sofa."),
   ("בערב הוא רעב ומבקש אוכל.", "In the evening he's hungry and asks for food."),
   ("הוא לא אוהב מים בכלל.", "He doesn't like water at all."),
   ("כשאני קורא ספר הוא יושב עליי.", "When I read a book he sits on me."),
   ("הוא חתול עצלן ואנחנו אוהבים אותו.", "He's a lazy cat and we love him."),
 ]),
 ("יום בים", "A Day at the Sea", [
   ("בקיץ אנחנו נוסעים לים.", "In summer we go to the sea."),
   ("המים חמים והחול חם מאוד.", "The water is warm and the sand is very hot."),
   ("אני שוחה קצת ואחר כך שוכב בשמש.", "I swim a bit and then lie in the sun."),
   ("הילדים בונים ארמון מחול.", "The children build a castle out of sand."),
   ("אנחנו אוכלים ושותים מים קרים.", "We eat and drink cold water."),
   ("בערב אנחנו חוזרים הביתה עייפים.", "In the evening we go home tired."),
 ]),
 ("ארוחת שישי", "Friday Dinner", [
   ("בשישי בערב כל המשפחה באה.", "On Friday evening the whole family comes."),
   ("אמא מבשלת מרק ועוף עם אורז.", "Mum cooks soup and chicken with rice."),
   ("על השולחן יש חלה ויין.", "On the table there's challah and wine."),
   ("כולם מדברים ביחד וצוחקים.", "Everyone talks together and laughs."),
   ("הילדים רצים בסלון.", "The children run around the living room."),
   ("אחרי האוכל אנחנו שותים תה.", "After the meal we drink tea."),
 ]),
 ("יום גשום", "A Rainy Day", [
   ("היום יורד גשם חזק.", "Today it's raining hard."),
   ("אני לא רוצה לצאת מהבית.", "I don't want to leave the house."),
   ("אני עושה תה ויושב על הספה.", "I make tea and sit on the sofa."),
   ("אני קורא ספר ושומע את הגשם.", "I read a book and listen to the rain."),
   ("אחר כך אני מסתכל בחלון.", "Afterwards I look out of the window."),
   ("הרחוב רטוב והעצים ירוקים.", "The street is wet and the trees are green."),
 ]),
 ("הרחוב שלי", "My Street", [
   ("אני גר ברחוב קטן ושקט.", "I live on a small, quiet street."),
   ("יש שם מכולת ובית קפה.", "There's a corner shop and a café there."),
   ("בבוקר הילדים הולכים לבית הספר.", "In the morning the children go to school."),
   ("השכנים מדברים ברחוב.", "The neighbours talk in the street."),
   ("בערב הרחוב שקט מאוד.", "In the evening the street is very quiet."),
   ("אני אוהב לגור פה.", "I like living here."),
 ]),
 ("בבית קפה", "At the Café", [
   ("אני יושב בבית קפה ליד הבית.", "I'm sitting in a café near home."),
   ("המלצר מביא לי קפה ועוגה.", "The waiter brings me coffee and cake."),
   ("אני פותח מחשב ועובד קצת.", "I open a laptop and work a bit."),
   ("שני חברים יושבים ומדברים.", "Two friends are sitting and talking."),
   ("בחוץ אנשים עוברים ברחוב.", "Outside people pass by in the street."),
   ("אני נשאר שעה ואחר כך הולך.", "I stay an hour and then go."),
 ]),
 ("לומד עברית", "Learning Hebrew", [
   ("אני לומד עברית כבר שנה.", "I've been learning Hebrew for a year now."),
   ("בהתחלה זה היה קשה מאוד.", "At first it was very hard."),
   ("עכשיו אני מבין הרבה מילים.", "Now I understand a lot of words."),
   ("אני קורא חדשות כל בוקר.", "I read the news every morning."),
   ("לפעמים אני מדבר עם השכנים.", "Sometimes I talk with the neighbours."),
   ("לאט לאט זה נהיה יותר קל.", "Slowly it's getting easier."),
 ]),
 ("השכן שלי", "My Neighbour", [
   ("לשכן שלי קוראים יוסי.", "My neighbour's name is Yossi."),
   ("הוא איש מבוגר וגר לבד.", "He's an older man and lives alone."),
   ("כל בוקר הוא יושב על הספסל.", "Every morning he sits on the bench."),
   ("הוא מספר לי סיפורים על העיר.", "He tells me stories about the city."),
   ("לפעמים אני מביא לו עוגה.", "Sometimes I bring him cake."),
   ("הוא תמיד אומר תודה ומחייך.", "He always says thank you and smiles."),
 ]),
]


def check(lex, title, sents):
    """-> (list of problems, stats). A story that has problems is not written."""
    toks = [t for he, _ in sents for t in he_ingest.tokenize(he)]
    unknown = sorted({t for t in toks if lex.look(t)[1] == 'unresolved'})
    arch = [t for t in toks if t in ARCHAIC]
    vav = vav_consecutives(lex, toks)
    lengths = [len(he_ingest.tokenize(he)) for he, _ in sents]
    avg = statistics.mean(lengths)
    bad = []
    if len(unknown) > MAX_UNKNOWN:
        bad.append('not in the lexicon: ' + ', '.join(unknown))
    if arch:
        bad.append('literary register: ' + ', '.join(sorted(set(arch))))
    if vav:
        bad.append('vav-consecutive: ' + ', '.join(sorted(set(vav))))
    if avg > MAX_SENTENCE:
        bad.append('sentences average %.1f words (max %.0f)' % (avg, MAX_SENTENCE))
    return bad, {'tokens': len(toks), 'avg': avg, 'longest': max(lengths)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='write texts/he/story-beg-NN.json')
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()

    lex = Lexicon()
    print('%-22s %-24s %5s %6s %5s' % ('title', 'English', 'words', 'avg', 'max'))
    problems = 0
    for t_he, t_en, sents in STORIES:
        bad, st = check(lex, t_he, sents)
        print('%-22s %-24s %5d %6.1f %5d %s'
              % (t_he[:22], t_en[:24], st['tokens'], st['avg'], st['longest'],
                 '' if not bad else '  !!'))
        for b in bad:
            print('     !! %s' % b)
            problems += 1
    if problems:
        print('\n%d problems — nothing written. A story the reader cannot tap every word of, '
              'or that reads like scripture, is not a beginner story.' % problems)
        return 1
    if not a.write:
        print('\nall %d clear. --write to emit them.' % len(STORIES))
        return 0
    for i, (t_he, t_en, sents) in enumerate(STORIES, 1):
        sid = 'story-beg-%02d' % i
        json.dump({'id': sid, 'kind': 'story', 'level': 'beginner',
                   'title': {'ar': t_he, 'en': t_en},
                   'dialect': 'he', 'subdialect': None, 'source': SRC,
                   'sentences': [{'ar': h, 'en': e} for h, e in sents]},
                  open(paths.texts(sid + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    print('\nwrote %d beginner stories -> %s'
          % (len(STORIES), os.path.relpath(paths.texts(''), paths.ROOT)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
