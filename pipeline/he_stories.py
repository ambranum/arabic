#!/usr/bin/env python3
"""Graded short stories in spoken Israeli Hebrew -> texts/he/story-{beg,int,adv}-NN.json.

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
  * LEVEL, and it means different things per tier. Beginner is short sentences in the present;
    intermediate is longer ones in the PAST, which is the point of the tier -- a story labelled
    intermediate that never leaves the present is mislabelled, so the gate counts past-tense
    verbs and requires them.
  * REACH, for intermediate only. A graded reader is graded by what it assumes you have already
    met, not by how it feels to write: most of its vocabulary should be words the beginner set
    or the rest of the app's Hebrew already used.

Deliberately unpointed, like the news. Vowels come from the lexicon at ingest, where they are
looked up -- pointing is the one thing a generator should not be trusted with, and it is the
one thing this project has never generated.

    python3 pipeline/he_stories.py --lang he                    # check every level
    python3 pipeline/he_stories.py --lang he --write            # write them all
    python3 pipeline/he_stories.py --lang he --level beginner   # one tier
"""
import argparse
import json
import os
import glob
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')

import he_ingest                                    # noqa: E402
from build_lex import he_norm                       # noqa: E402
from lex import Lexicon                             # noqa: E402

SRC = ('%s short story written in spoken Israeli Hebrew by Claude. NOT native-validated.')

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
FINITE = ('past', 'present', 'future', 'imperative')

# tier -> (id prefix, sentence length floor and ceiling, minimum share of sentences carrying a
# past-tense verb, minimum share of lemmas already met elsewhere in the app's Hebrew, minimum
# share of sentences carrying two clauses, minimum share of DISTINCT lemmas that are new)
LEVELS = {
    'beginner':     {'sid': 'beg', 'min_sentence': 0.0, 'max_sentence': 9.0,
                     'min_past': 0.0, 'min_reach': 0.0, 'min_sub': 0.0, 'min_fresh': 0.0},
    'intermediate': {'sid': 'int', 'min_sentence': 7.0, 'max_sentence': 14.0,
                     'min_past': 0.5, 'min_reach': 0.7, 'min_sub': 0.0, 'min_fresh': 0.0},
    # Advanced is a claim in two directions and the gate makes both. It has to be HARDER --
    # longer sentences, two clauses at a time, still narrating in the past -- and it has to
    # actually TEACH something, which the tiers below cannot: a fifth of its lemmas must be
    # words the app's Hebrew has never used. Without that floor "advanced" is intermediate with
    # commas, which is the failure mode of every graded reader that grades itself by feel.
    'advanced':     {'sid': 'adv', 'min_sentence': 12.0, 'max_sentence': 21.0,
                     'min_past': 0.5, 'min_reach': 0.5, 'min_sub': 0.6, 'min_fresh': 0.2},
}
MAX_UNKNOWN = 0             # every word taps, at every level

# level -> [(title_he, title_en, [(he, en), ...]), ...]
STORIES = {}
STORIES['beginner'] = [
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
 ("בחנות", "At the Shop", [
   ("אחרי העבודה אני הולך לחנות גדולה.", "After work I go to a big shop."),
   ("אני לוקח עגלה ומתחיל לקנות.", "I take a trolley and start shopping."),
   ("אני קונה חלב, לחם, ביצים וגבינה.", "I buy milk, bread, eggs and cheese."),
   ("בקופה יש תור ארוך.", "At the checkout there's a long queue."),
   ("אני מחכה ומסתכל על האנשים.", "I wait and look at the people."),
   ("אחר כך אני משלם והולך הביתה.", "Afterwards I pay and go home."),
 ]),
 ("הכלב של השכנים", "The Neighbours' Dog", [
   ("לשכנים שלי יש כלב גדול.", "My neighbours have a big dog."),
   ("הוא חום ויש לו עיניים שחורות.", "He's brown and has black eyes."),
   ("כל בוקר הם הולכים איתו ברחוב.", "Every morning they walk him in the street."),
   ("הוא אוהב לרוץ אחרי חתולים.", "He likes to run after cats."),
   ("לפעמים הוא עושה רעש בלילה.", "Sometimes he makes noise at night."),
   ("אבל הוא כלב טוב ושקט.", "But he's a good, quiet dog."),
 ]),
 ("יום ראשון", "Sunday", [
   ("ביום ראשון אני קם מוקדם.", "On Sunday I get up early."),
   ("זה היום הראשון בשבוע.", "It's the first day of the week."),
   ("אני שותה קפה וקורא חדשות.", "I drink coffee and read the news."),
   ("בעבודה יש הרבה דברים לעשות.", "At work there's a lot to do."),
   ("בצהריים אני אוכל עם חברים.", "At midday I eat with friends."),
   ("בערב אני חוזר הביתה עייף.", "In the evening I come home tired."),
 ]),
 ("במסעדה", "At the Restaurant", [
   ("אנחנו יושבים במסעדה קטנה.", "We're sitting in a small restaurant."),
   ("המלצר נותן לנו תפריט.", "The waiter gives us a menu."),
   ("אני מזמין דג ואשתי מזמינה סלט.", "I order fish and my wife orders salad."),
   ("האוכל טעים והמקום שקט.", "The food is tasty and the place is quiet."),
   ("אנחנו מדברים על העבודה.", "We talk about work."),
   ("בסוף אנחנו משלמים והולכים.", "In the end we pay and go."),
 ]),
 ("הגינה", "The Garden", [
   ("מאחורי הבית שלנו יש גינה קטנה.", "Behind our house there's a small garden."),
   ("יש שם עץ אחד ופרחים אדומים.", "There's one tree there and red flowers."),
   ("בבוקר אני נותן מים לפרחים.", "In the morning I water the flowers."),
   ("ציפורים יושבות על העץ ושרות.", "Birds sit on the tree and sing."),
   ("בערב אנחנו יושבים בגינה.", "In the evening we sit in the garden."),
   ("שם קריר ונעים.", "It's cool and pleasant there."),
 ]),
 ("אחרי הצהריים", "The Afternoon", [
   ("אחרי הצהריים הרחוב שקט.", "In the afternoon the street is quiet."),
   ("הילדים חוזרים מבית הספר.", "The children come back from school."),
   ("הם משחקים בחצר עד הערב.", "They play in the yard until evening."),
   ("אמא קוראת להם לאכול.", "Mum calls them to eat."),
   ("אחר כך הם עושים שיעורי בית.", "Afterwards they do homework."),
   ("בשמונה כולם רוצים לישון.", "At eight everyone wants to sleep."),
 ]),
 ("בספרייה", "At the Library", [
   ("ליד הבית שלי יש ספרייה.", "There's a library near my house."),
   ("שם שקט מאוד וכולם קוראים.", "It's very quiet there and everyone reads."),
   ("אני מחפש ספר על היסטוריה.", "I look for a book about history."),
   ("האישה ליד הדלת עוזרת לי.", "The woman by the door helps me."),
   ("אני יושב ליד החלון וקורא.", "I sit by the window and read."),
   ("אחרי שעה אני לוקח את הספר הביתה.", "After an hour I take the book home."),
 ]),
 ("חברים", "Friends", [
   ("יש לי שני חברים טובים.", "I have two good friends."),
   ("אנחנו נפגשים כל שבוע.", "We meet every week."),
   ("לפעמים אנחנו הולכים לסרט.", "Sometimes we go to a film."),
   ("לפעמים אנחנו רק יושבים ומדברים.", "Sometimes we just sit and talk."),
   ("הם מספרים לי על העבודה שלהם.", "They tell me about their work."),
   ("אני שמח שיש לי אותם.", "I'm glad I have them."),
 ]),
 ("הטלפון שלי", "My Phone", [
   ("הטלפון שלי ישן וקטן.", "My phone is old and small."),
   ("בבוקר אני מסתכל בו בזמן הקפה.", "In the morning I look at it over coffee."),
   ("אני קורא הודעות מהמשפחה.", "I read messages from the family."),
   ("לפעמים אני מדבר עם אמא שלי.", "Sometimes I talk with my mum."),
   ("בערב אני שם אותו על השולחן.", "In the evening I put it on the table."),
   ("לפני השינה אני לא רוצה אותו.", "Before sleep I don't want it."),
 ]),
 ("בדואר", "At the Post Office", [
   ("היום אני הולך לדואר.", "Today I go to the post office."),
   ("אני צריך לשלוח מכתב.", "I need to send a letter."),
   ("בפנים יש הרבה אנשים ותור ארוך.", "Inside there are a lot of people and a long queue."),
   ("אני מחכה עשרים דקות.", "I wait twenty minutes."),
   ("האיש בקופה לוקח את המכתב.", "The man at the counter takes the letter."),
   ("אני יוצא ושמח שגמרתי.", "I leave, glad that I'm finished."),
 ]),
 ("יום הולדת", "A Birthday", [
   ("היום יום הולדת של אחותי.", "Today is my sister's birthday."),
   ("אנחנו קונים עוגה גדולה עם שוקולד.", "We buy a big cake with chocolate."),
   ("בערב כל החברים באים.", "In the evening all the friends come."),
   ("כולם שרים ומביאים מתנות.", "Everyone sings and brings presents."),
   ("אחותי שמחה מאוד וצוחקת.", "My sister is very happy and laughs."),
   ("בסוף אנחנו אוכלים את העוגה.", "In the end we eat the cake."),
 ]),
 ("בכיתה", "In the Classroom", [
   ("בבוקר הכיתה מלאה ילדים.", "In the morning the classroom is full of children."),
   ("המורה כותבת על הלוח.", "The teacher writes on the board."),
   ("הילדים פותחים ספרים ומחברות.", "The children open books and notebooks."),
   ("אחד שואל שאלה והמורה עונה.", "One asks a question and the teacher answers."),
   ("אחרי שעה יש הפסקה.", "After an hour there's a break."),
   ("כולם רצים לחצר.", "Everyone runs to the yard."),
 ]),
 ("הרכבת", "The Train", [
   ("אני נוסע ברכבת לעיר אחרת.", "I travel by train to another city."),
   ("הרכבת יוצאת בשמונה בבוקר.", "The train leaves at eight in the morning."),
   ("אני יושב ליד החלון ומסתכל בחוץ.", "I sit by the window and look outside."),
   ("בחוץ יש שדות ועצים.", "Outside there are fields and trees."),
   ("אני קורא ספר וגם ישן קצת.", "I read a book and also sleep a bit."),
   ("אחרי שעתיים אני מגיע.", "After two hours I arrive."),
 ]),
 ("בפארק", "At the Park", [
   ("ביום שבת אנחנו הולכים לפארק.", "On Saturday we go to the park."),
   ("יש שם עצים גדולים ודשא ירוק.", "There are big trees and green grass there."),
   ("ילדים משחקים בכדור.", "Children play with a ball."),
   ("אנשים מבוגרים יושבים על הספסלים.", "Older people sit on the benches."),
   ("אנחנו אוכלים פירות ושותים מים.", "We eat fruit and drink water."),
   ("אחר כך אנחנו הולכים הביתה לאט.", "Afterwards we walk home slowly."),
 ]),
 ("לבשל", "Cooking", [
   ("בערב אני מבשל ארוחה פשוטה.", "In the evening I cook a simple meal."),
   ("אני חותך בצל ועגבניות.", "I chop onion and tomatoes."),
   ("אני מכניס הכול לסיר עם מים.", "I put everything into a pot with water."),
   ("במטבח יש ריח טוב מאוד.", "In the kitchen there's a very good smell."),
   ("אחרי חצי שעה האוכל מוכן.", "After half an hour the food is ready."),
   ("אני אוכל לבד ושומע מוזיקה.", "I eat alone and listen to music."),
 ]),
 ("הבגדים", "Clothes", [
   ("בבוקר אני פותח את הארון.", "In the morning I open the wardrobe."),
   ("אני לובש חולצה לבנה ומכנסיים.", "I put on a white shirt and trousers."),
   ("בחורף אני צריך גם מעיל.", "In winter I need a coat as well."),
   ("הנעליים שלי ישנות אבל נוחות.", "My shoes are old but comfortable."),
   ("אמא אומרת שאני צריך בגדים חדשים.", "Mum says I need new clothes."),
   ("אולי בשבוע הבא אני קונה.", "Maybe next week I'll buy some."),
 ]),
 ("חורף", "Winter", [
   ("בחורף הימים קצרים והלילות ארוכים.", "In winter the days are short and the nights long."),
   ("בחוץ קר ולפעמים יורד גשם.", "Outside it's cold and sometimes it rains."),
   ("אנשים לובשים מעילים וכובעים.", "People wear coats and hats."),
   ("בבית חם ואני שותה תה.", "At home it's warm and I drink tea."),
   ("הילדים אוהבים לשחק בגשם.", "The children like to play in the rain."),
   ("אני אוהב את החורף בעיר.", "I like the winter in the city."),
 ]),
 ("סוף השבוע", "The Weekend", [
   ("בסוף השבוע אני לא עובד.", "At the weekend I don't work."),
   ("אני קם מאוחר ולא ממהר.", "I get up late and don't rush."),
   ("בבוקר אני הולך לשוק.", "In the morning I go to the market."),
   ("בצהריים אני נח וקורא.", "At midday I rest and read."),
   ("בערב חברים באים לבית.", "In the evening friends come to the house."),
   ("אנחנו מדברים עד מאוחר.", "We talk until late."),
 ]),
]

STORIES['intermediate'] = [
 ("השיעור הראשון", "The First Lesson", [
  ("בשנה שעברה התחלתי ללמוד עברית בבית ספר קטן ליד הבית.", "Last year I started learning Hebrew at a small school near my house."),
  ("בשיעור הראשון הייתי לחוץ מאוד ולא הבנתי כמעט כלום.", "In the first lesson I was very tense and understood almost nothing."),
  ("המורה דיברה לאט ושאלה כל אחד מאיפה הוא בא.", "The teacher spoke slowly and asked each person where they came from."),
  ("כשהגיע התור שלי אמרתי רק את השם שלי.", "When my turn came I said only my name."),
  ("כולם צחקו, אבל זה היה צחוק טוב ונעים.", "Everyone laughed, but it was a good, warm laugh."),
  ("אחרי השיעור המורה אמרה לי שבפעם הבאה יהיה יותר קל.", "After the lesson the teacher told me that next time would be easier."),
  ("חזרתי הביתה עייף אבל שמח שהתחלתי.", "I went home tired but glad I had started."),
 ]),
 ("המפתחות", "The Keys", [
  ("אתמול בבוקר יצאתי מהבית וסגרתי את הדלת אחריי.", "Yesterday morning I left the house and closed the door behind me."),
  ("רק כשהגעתי לרחוב הבנתי שהמפתחות נשארו בפנים.", "Only when I got to the street did I realise the keys had stayed inside."),
  ("חיפשתי בכיסים, בתיק ובמעיל, אבל הם לא היו שם.", "I searched my pockets, my bag and my coat, but they weren't there."),
  ("ישבתי על המדרגות וחשבתי מה לעשות.", "I sat on the steps and thought about what to do."),
  ("אחרי חצי שעה השכנה מלמעלה חזרה מהעבודה.", "After half an hour the neighbour from upstairs came back from work."),
  ("היא נתנה לי כוס תה וחיכינו יחד לבעל הבית.", "She gave me a cup of tea and we waited together for the landlord."),
  ("בסוף הכול הסתדר, אבל למדתי לקחת מפתח נוסף.", "In the end everything worked out, but I learned to take a spare key."),
 ]),
 ("הטיול לצפון", "The Trip North", [
  ("בקיץ שעבר נסענו עם חברים לצפון לשלושה ימים.", "Last summer we went north with friends for three days."),
  ("יצאנו מוקדם בבוקר כי רצינו להגיע לפני החום.", "We left early in the morning because we wanted to arrive before the heat."),
  ("בדרך עצרנו במסעדה קטנה ואכלנו ארוחת בוקר גדולה.", "On the way we stopped at a small restaurant and ate a big breakfast."),
  ("בערב הגענו למקום ופתחנו את החלונות אל ההרים.", "In the evening we arrived and opened the windows onto the hills."),
  ("למחרת הלכנו ליד המים ודיברנו על הכול.", "The next day we walked by the water and talked about everything."),
  ("היה קריר ושקט, ואף אחד לא מיהר לשום מקום.", "It was cool and quiet, and nobody was rushing anywhere."),
  ("כשחזרנו הביתה כבר התגעגענו לשם.", "When we got home we already missed the place."),
 ]),
 ("השכן החדש", "The New Neighbour", [
  ("לפני חודש עברה משפחה חדשה לדירה שמעלינו.", "A month ago a new family moved into the flat above us."),
  ("בהתחלה שמענו רק רעש של ארגזים ורהיטים.", "At first we only heard the noise of boxes and furniture."),
  ("אחרי כמה ימים פגשתי את האיש במדרגות.", "After a few days I met the man on the stairs."),
  ("הוא סיפר שהם באו מעיר אחרת בגלל העבודה שלו.", "He said they had come from another city because of his work."),
  ("שאלתי אם הם צריכים משהו והוא אמר שהכול בסדר.", "I asked if they needed anything and he said everything was fine."),
  ("בשבת הם הביאו לנו עוגה קטנה ואמרו תודה.", "On Saturday they brought us a small cake and said thank you."),
  ("מאז אנחנו מדברים כל פעם שאנחנו נפגשים.", "Since then we talk every time we meet."),
 ]),
 ("הגשם בדרך", "Rain on the Way", [
  ("בבוקר יצאתי לעבודה בלי מעיל כי השמים היו בהירים.", "In the morning I left for work without a coat because the sky was clear."),
  ("אחרי עשר דקות התחיל גשם חזק ולא היה איפה לעמוד.", "After ten minutes heavy rain started and there was nowhere to stand."),
  ("רצתי עד תחנת האוטובוס אבל כבר הייתי רטוב לגמרי.", "I ran to the bus stop but I was already completely wet."),
  ("אישה מבוגרת שעמדה שם צחקה ואמרה שגם היא שכחה מעיל.", "An older woman standing there laughed and said she had forgotten a coat too."),
  ("חיכינו יחד וסיפרנו על מזג האוויר של פעם.", "We waited together and talked about the weather of the old days."),
  ("כשהאוטובוס הגיע הגשם כבר נפסק.", "When the bus arrived the rain had already stopped."),
  ("הגעתי לעבודה באיחור, אבל עם סיפור טוב.", "I got to work late, but with a good story."),
 ]),
 ("העוגה של סבתא", "Grandma's Cake", [
  ("כשהייתי ילד סבתא שלי אפתה עוגה כל יום שישי.", "When I was a child my grandmother baked a cake every Friday."),
  ("הריח מילא את כל הבית ואי אפשר היה לחכות.", "The smell filled the whole house and it was impossible to wait."),
  ("היא לא נתנה לנו לטעום לפני הארוחה.", "She wouldn't let us taste it before the meal."),
  ("פעם אחת ניסיתי לקחת חתיכה קטנה בשקט.", "Once I tried to take a small piece quietly."),
  ("היא ראתה אותי מהמטבח ולא אמרה מילה.", "She saw me from the kitchen and didn't say a word."),
  ("בערב היא שמה לידי חתיכה גדולה במיוחד.", "In the evening she put an especially big piece next to me."),
  ("היום אני מנסה לאפות אותה, אבל זה לא אותו דבר.", "Today I try to bake it, but it's not the same."),
 ]),
 ("הראיון", "The Interview", [
  ("בשבוע שעבר הלכתי לראיון עבודה בעיר.", "Last week I went to a job interview in the city."),
  ("לבשתי חולצה לבנה ויצאתי מהבית שעה מוקדם.", "I put on a white shirt and left the house an hour early."),
  ("במשרד חיכיתי עשרים דקות וקראתי עיתון ישן.", "At the office I waited twenty minutes and read an old newspaper."),
  ("האישה ששאלה אותי הייתה נחמדה ודיברה לאט.", "The woman who questioned me was nice and spoke slowly."),
  ("לא ידעתי לענות על הכול, אבל אמרתי את האמת.", "I didn't know how to answer everything, but I told the truth."),
  ("בסוף היא אמרה שהם יתקשרו בשבוע הבא.", "In the end she said they would call the following week."),
  ("יצאתי משם עם הרגשה טובה, וזה כבר מספיק.", "I left with a good feeling, and that's already enough."),
 ]),
 ("החתול שברח", "The Cat That Ran Away", [
  ("בערב אחד שכחנו לסגור את החלון והחתול יצא החוצה.", "One evening we forgot to close the window and the cat got out."),
  ("חיפשנו אותו בחצר, ברחוב ומתחת לכל המכוניות.", "We looked for him in the yard, in the street and under all the cars."),
  ("הילדים בכו והיה כבר מאוחר וחשוך.", "The children cried and it was already late and dark."),
  ("שאלנו את השכנים והם אמרו שלא ראו כלום.", "We asked the neighbours and they said they hadn't seen anything."),
  ("בבוקר שמענו רעש קטן מאחורי הדלת.", "In the morning we heard a small noise behind the door."),
  ("הוא ישב שם רגוע לגמרי, כאילו כלום לא קרה.", "He was sitting there completely calm, as if nothing had happened."),
  ("מאז אנחנו סוגרים את החלון כל ערב.", "Since then we close the window every evening."),
 ]),
 ("יום בירושלים", "A Day in Jerusalem", [
  ("לפני שנה נסעתי לירושלים ליום אחד עם חבר.", "A year ago I went to Jerusalem for one day with a friend."),
  ("הרכבת יצאה בשמונה והגענו לפני עשר.", "The train left at eight and we arrived before ten."),
  ("הלכנו ברחובות הצרים והסתכלנו על הבתים הישנים.", "We walked the narrow streets and looked at the old houses."),
  ("בצהריים אכלנו במקום קטן שחבר שלי הכיר.", "At midday we ate in a small place my friend knew."),
  ("אחר כך ישבנו בשמש ולא דיברנו הרבה.", "Afterwards we sat in the sun and didn't talk much."),
  ("בערב חזרנו ברכבת ושנינו היינו עייפים מאוד.", "In the evening we went back by train and we were both very tired."),
  ("זה היה יום פשוט, אבל אני זוכר אותו עד היום.", "It was a simple day, but I remember it to this day."),
 ]),
 ("המכתב", "The Letter", [
  ("לפני שבועיים קיבלתי מכתב מחבר ישן.", "Two weeks ago I got a letter from an old friend."),
  ("לא דיברנו כבר עשר שנים ולא ידעתי איפה הוא גר.", "We hadn't spoken for ten years and I didn't know where he lived."),
  ("הוא כתב שהוא חושב עליי ושהוא רוצה להיפגש.", "He wrote that he thinks about me and wants to meet."),
  ("קראתי את המכתב פעמיים ואחר כך שמתי אותו על השולחן.", "I read the letter twice and then put it on the table."),
  ("כל היום חשבתי על הזמן ההוא ועל האנשים.", "All day I thought about that time and about the people."),
  ("בערב ישבתי וכתבתי לו תשובה ארוכה.", "In the evening I sat down and wrote him a long reply."),
  ("בשבוע הבא אנחנו נפגשים בבית קפה בעיר.", "Next week we're meeting at a café in the city."),
 ]),
 ("הרכבת האחרונה", "The Last Train", [
  ("בערב אחד נשארתי בעיר יותר מדי זמן עם חברים.", "One evening I stayed in the city too long with friends."),
  ("כשהסתכלתי על השעון הבנתי שהרכבת האחרונה יוצאת בעוד עשר דקות.", "When I looked at the clock I realised the last train left in ten minutes."),
  ("רצתי ברחוב ועליתי במדרגות של התחנה.", "I ran down the street and up the station steps."),
  ("הרכבת עמדה שם והדלתות עוד היו פתוחות.", "The train was standing there and the doors were still open."),
  ("נכנסתי בשנייה האחרונה וישבתי בלי אוויר.", "I got in at the last second and sat down out of breath."),
  ("איש מבוגר מולי חייך ואמר שגם הוא רץ פעם.", "An older man opposite me smiled and said he had run once too."),
  ("כל הדרך הביתה חשבתי כמה זה היה קרוב.", "All the way home I thought how close it had been."),
 ]),
 ("הדירה החדשה", "The New Flat", [
  ("לפני שנתיים עברנו לדירה חדשה בקומה השלישית.", "Two years ago we moved to a new flat on the third floor."),
  ("בהתחלה הכול היה ריק ולא היו לנו כמעט רהיטים.", "At first everything was empty and we had almost no furniture."),
  ("ישבנו על הרצפה ואכלנו את הארוחה הראשונה מקופסאות.", "We sat on the floor and ate our first meal out of boxes."),
  ("בשבועות הבאים קנינו שולחן, כיסאות ומיטה.", "In the following weeks we bought a table, chairs and a bed."),
  ("שכן מהקומה למטה עזר לנו להעלות את הארון.", "A neighbour from the floor below helped us carry the wardrobe up."),
  ("אחרי חודש הדירה כבר הרגישה כמו בית.", "After a month the flat already felt like home."),
  ("היום אני לא זוכר איך היה במקום הקודם.", "Today I don't remember what it was like in the old place."),
 ]),
 ("הים בחורף", "The Sea in Winter", [
  ("בחורף שעבר נסענו לים ביום קר ואפור.", "Last winter we drove to the sea on a cold, grey day."),
  ("החוף היה ריק לגמרי ורק שני אנשים הלכו רחוק.", "The beach was completely empty and only two people walked far off."),
  ("הרוח הייתה חזקה והמים היו כהים מאוד.", "The wind was strong and the water was very dark."),
  ("הלכנו על החול עם מעילים וכובעים.", "We walked on the sand in coats and hats."),
  ("אף אחד לא נכנס למים, אבל זה לא היה חשוב.", "Nobody went into the water, but that wasn't important."),
  ("אחר כך ישבנו בבית קפה קטן ושתינו תה חם.", "Afterwards we sat in a small café and drank hot tea."),
  ("מאז אני אוהב את הים בחורף יותר מאשר בקיץ.", "Since then I like the sea in winter more than in summer."),
 ]),
 ("הבחינה", "The Exam", [
  ("בשנה שעברה למדתי חודש שלם לבחינה אחת.", "Last year I studied a whole month for one exam."),
  ("בלילה לפני זה כמעט לא ישנתי בכלל.", "The night before I hardly slept at all."),
  ("בבוקר הגעתי מוקדם וישבתי בשורה האחרונה.", "In the morning I arrived early and sat in the back row."),
  ("השאלות היו קשות יותר ממה שחשבתי.", "The questions were harder than I had thought."),
  ("אחרי שעתיים יצאתי מהחדר בלי לדעת מה יהיה.", "After two hours I left the room without knowing what would happen."),
  ("חיכיתי שבועיים לתשובה וכל יום חשבתי על זה.", "I waited two weeks for the answer and thought about it every day."),
  ("בסוף עברתי, ואז שכחתי את כל הפחד.", "In the end I passed, and then I forgot all the fear."),
 ]),
 ("העבודה הראשונה", "The First Job", [
  ("בגיל שמונה עשרה התחלתי לעבוד בחנות קטנה בעיר.", "At eighteen I started working in a small shop in the city."),
  ("הייתי צריך להגיע כל בוקר בשבע ולפתוח את הדלת.", "I had to arrive every morning at seven and open the door."),
  ("בהתחלה לא ידעתי כלום ושברתי שתי כוסות ביום הראשון.", "At first I knew nothing and broke two glasses on the first day."),
  ("הבעלים לא כעס והראה לי איך לעשות הכול לאט.", "The owner didn't get angry and showed me how to do it all slowly."),
  ("אחרי חודש כבר הכרתי את כל הלקוחות בשם.", "After a month I already knew all the customers by name."),
  ("עבדתי שם שנתיים ולמדתי יותר מאשר בבית הספר.", "I worked there two years and learned more than at school."),
  ("היום החנות סגורה, אבל אני עובר שם לפעמים.", "Today the shop is closed, but I pass by sometimes."),
 ]),
 ("הספר ששכחתי", "The Book I Forgot", [
  ("לפני חודש שכחתי ספר על ספסל בפארק.", "A month ago I forgot a book on a bench in the park."),
  ("רק בערב הבנתי שהוא לא בתיק שלי.", "Only in the evening did I realise it wasn't in my bag."),
  ("למחרת בבוקר חזרתי לשם בלי הרבה תקווה.", "The next morning I went back there without much hope."),
  ("הספר עוד היה שם, רטוב קצת מהלילה.", "The book was still there, a little wet from the night."),
  ("מישהו שם אותו מתחת לעץ כדי שלא יירטב יותר.", "Someone had put it under a tree so it wouldn't get wetter."),
  ("לקחתי אותו הביתה וייבשתי אותו ליד החלון.", "I took it home and dried it by the window."),
  ("עד היום אני רואה בו את הסימנים של הגשם.", "To this day I see the marks of the rain in it."),
 ]),
 ("הדוד מאמריקה", "The Uncle from America", [
  ("בקיץ הגיע אלינו דוד שלא ראינו כבר עשרים שנה.", "In summer an uncle we hadn't seen for twenty years came to us."),
  ("הוא בא מאמריקה עם מזוודה גדולה ומתנות לכולם.", "He came from America with a big suitcase and presents for everyone."),
  ("הוא דיבר עברית לאט ולפעמים שכח מילים.", "He spoke Hebrew slowly and sometimes forgot words."),
  ("בערב ישבנו כולם סביב השולחן והוא סיפר סיפורים.", "In the evening we all sat around the table and he told stories."),
  ("הילדים שאלו אותו שאלות עד מאוחר בלילה.", "The children asked him questions until late at night."),
  ("אחרי שבועיים הוא חזר, והבית פתאום היה שקט מדי.", "After two weeks he went back, and the house was suddenly too quiet."),
  ("מאז אנחנו מדברים איתו כל חודש.", "Since then we talk to him every month."),
 ]),
 ("ההליכה בערב", "The Evening Walk", [
  ("כל ערב בקיץ ההוא יצאתי להליכה ארוכה בעיר.", "Every evening that summer I went for a long walk in the city."),
  ("הלכתי באותם רחובות והסתכלתי על אותם בתים.", "I walked the same streets and looked at the same houses."),
  ("לפעמים עצרתי ליד חלון פתוח ושמעתי מוזיקה.", "Sometimes I stopped by an open window and heard music."),
  ("אנשים ישבו בחוץ ודיברו עד מאוחר.", "People sat outside and talked until late."),
  ("פעם אחת פגשתי מורה ישנה שלי והיא זכרה את השם שלי.", "Once I met an old teacher of mine and she remembered my name."),
  ("דיברנו עשרים דקות ואחר כך כל אחד הלך לדרכו.", "We talked for twenty minutes and then each went our own way."),
  ("אני עוד הולך שם, אבל עכשיו זה לא אותו דבר.", "I still walk there, but now it isn't the same."),
 ]),
 ("סבתא והתמונות", "Grandma and the Photographs", [
  ("בשבת אחת סבתא הוציאה קופסה ישנה עם תמונות.", "One Saturday my grandmother took out an old box of photographs."),
  ("ישבנו על הספה והיא סיפרה על כל תמונה בנפרד.", "We sat on the sofa and she told me about each photograph separately."),
  ("בתמונה אחת היא הייתה ילדה קטנה ליד בית לבן.", "In one photograph she was a small girl beside a white house."),
  ("היא אמרה שהבית ההוא כבר לא קיים היום.", "She said that house doesn't exist any more."),
  ("שאלתי אותה אם היא עצובה והיא רק חייכה.", "I asked her if she was sad and she only smiled."),
  ("אחר כך היא נתנה לי שתי תמונות לקחת הביתה.", "Afterwards she gave me two photographs to take home."),
  ("הן עומדות אצלי על המדף עד היום.", "They stand on my shelf to this day."),
 ]),
 ("סוף הקיץ", "The End of Summer", [
  ("בסוף אוגוסט הרגשנו שהקיץ מתחיל להיגמר.", "At the end of August we felt the summer starting to end."),
  ("הימים היו עוד חמים, אבל הערבים כבר היו קרירים.", "The days were still hot, but the evenings were already cool."),
  ("הילדים חזרו מהחופש ודיברו רק על בית הספר.", "The children came back from the holiday and talked only about school."),
  ("קנינו מחברות, עפרונות ותיק חדש לקטן.", "We bought notebooks, pencils and a new bag for the little one."),
  ("בערב האחרון של החופש ישבנו כולנו בגינה.", "On the last evening of the holiday we all sat in the garden."),
  ("אף אחד לא רצה ללכת לישון מוקדם.", "Nobody wanted to go to bed early."),
  ("למחרת התחילה שנה חדשה, וזה תמיד מרגיש כמו התחלה.", "The next day a new year began, and that always feels like a beginning."),
 ]),
 ("השוק ביום שישי", "The Market on Friday", [
  ("ביום שישי אחד קמתי מוקדם והלכתי לשוק לבד.", "One Friday I got up early and went to the market alone."),
  ("היו שם המון אנשים וכמעט לא היה מקום ללכת.", "There were crowds of people and almost no room to walk."),
  ("המוכרים צעקו על הירקות ועל המחירים.", "The sellers shouted about the vegetables and the prices."),
  ("קניתי עגבניות, לחם וגבינה, והכול היה טרי מאוד.", "I bought tomatoes, bread and cheese, and everything was very fresh."),
  ("בסוף השוק ישב איש זקן ומכר פרחים.", "At the end of the market an old man sat selling flowers."),
  ("קניתי ממנו פרחים לבנים בלי לחשוב הרבה.", "I bought white flowers from him without thinking much."),
  ("בבית שמתי אותם על השולחן והם עמדו שם שבוע.", "At home I put them on the table and they stood there a week."),
 ]),
 ("החנות שנסגרה", "The Shop That Closed", [
  ("בקצה הרחוב שלנו הייתה חנות קטנה של ספרים.", "At the end of our street there was a small bookshop."),
  ("האיש שעבד שם הכיר כל לקוח וזכר מה כל אחד אוהב.", "The man who worked there knew every customer and remembered what each liked."),
  ("נכנסתי לשם כמעט כל שבוע, גם כשלא קניתי כלום.", "I went in almost every week, even when I didn't buy anything."),
  ("בחורף שעבר ראיתי פתאום שלט על הדלת.", "Last winter I suddenly saw a sign on the door."),
  ("הוא כתב שהחנות נסגרת אחרי שלושים שנה.", "It said the shop was closing after thirty years."),
  ("ביום האחרון הלכתי לשם ואמרתי לו תודה.", "On the last day I went there and said thank you to him."),
  ("היום יש שם בית קפה, ואני עובר בלי להיכנס.", "Today there's a café there, and I pass by without going in."),
 ]),
 ("הסרט", "The Film", [
  ("בערב אחד הלכנו לראות סרט ישן בבית קולנוע קטן.", "One evening we went to see an old film at a small cinema."),
  ("היו רק עשרה אנשים באולם וכולם ישבו רחוק זה מזה.", "There were only ten people in the hall and all sat far apart."),
  ("הסרט היה איטי מאוד ובהתחלה לא הבנתי אותו.", "The film was very slow and at first I didn't understand it."),
  ("אחרי חצי שעה שכחתי לגמרי איפה אני יושב.", "After half an hour I completely forgot where I was sitting."),
  ("כשהאור נדלק אף אחד לא קם מיד.", "When the lights came on nobody got up straight away."),
  ("בדרך הביתה דיברנו עליו כל הזמן.", "On the way home we talked about it the whole time."),
  ("עד היום אני חושב על הסוף ההוא.", "To this day I think about that ending."),
 ]),
 ("הנסיעה לעבודה", "The Journey to Work", [
  ("במשך שנה נסעתי כל יום שעה שלמה לעבודה.", "For a year I travelled a whole hour to work every day."),
  ("יצאתי מהבית בשש וחצי כשעוד היה חושך.", "I left the house at half past six when it was still dark."),
  ("באוטובוס תמיד ישבתי באותו מקום ליד החלון.", "On the bus I always sat in the same seat by the window."),
  ("ראיתי את אותם אנשים כל בוקר ולא דיברתי איתם.", "I saw the same people every morning and didn't talk to them."),
  ("קראתי ספרים שלמים בדרך ולא הרגשתי את הזמן.", "I read whole books on the way and didn't feel the time."),
  ("אחרי שנה מצאתי עבודה קרובה לבית.", "After a year I found work close to home."),
  ("היום אני הולך ברגל, אבל קורא הרבה פחות.", "Today I walk, but I read far less."),
 ]),
 ("יום השלג", "The Day of Snow", [
  ("לפני שנים ירד שלג בעיר, וזה קורה כמעט אף פעם.", "Years ago snow fell in the city, and that almost never happens."),
  ("בבוקר הסתכלנו מהחלון ולא האמנו למה שראינו.", "In the morning we looked out of the window and didn't believe what we saw."),
  ("בתי הספר נסגרו וכל הילדים ירדו לרחוב.", "The schools closed and all the children went down to the street."),
  ("אנשים מבוגרים עמדו בחוץ וצילמו את העצים.", "Older people stood outside and photographed the trees."),
  ("היה קר מאוד, אבל אף אחד לא רצה להיכנס הביתה.", "It was very cold, but nobody wanted to go inside."),
  ("אחרי יומיים הכול נמס ונשארו רק שלוליות.", "After two days it all melted and only puddles were left."),
  ("הילדים דיברו על היום ההוא עוד חודשים.", "The children talked about that day for months afterwards."),
 ]),
 ("הטלפון שאבד", "The Phone That Was Lost", [
  ("ביום שישי אחד איבדתי את הטלפון שלי באוטובוס.", "One Friday I lost my phone on the bus."),
  ("הבנתי את זה רק כשהגעתי הביתה ורציתי להתקשר.", "I only realised when I got home and wanted to make a call."),
  ("חיפשתי בכל הכיסים ובכל התיק, אבל הוא לא היה שם.", "I searched every pocket and the whole bag, but it wasn't there."),
  ("בערב מישהו התקשר לאשתי ואמר שהוא מצא אותו.", "In the evening someone called my wife and said he had found it."),
  ("נסעתי אליו למחרת בבוקר לקצה השני של העיר.", "I travelled to him the next morning, to the other side of the city."),
  ("הוא לא רצה כסף ורק אמר שזה קרה גם לו פעם.", "He didn't want money and only said it had happened to him too once."),
  ("מאז אני בודק את הכיס בכל פעם שאני קם.", "Since then I check my pocket every time I stand up."),
 ]),
 ("ארוחה עם חברים", "A Meal with Friends", [
  ("בשבת בערב הזמנו ארבעה חברים לארוחה בבית.", "On Saturday evening we invited four friends for a meal at home."),
  ("בישלנו כל היום ובסוף היה יותר מדי אוכל.", "We cooked all day and in the end there was too much food."),
  ("הם הגיעו באיחור של חצי שעה, כמו תמיד.", "They arrived half an hour late, as always."),
  ("ישבנו סביב השולחן ודיברנו עד אחת בלילה.", "We sat around the table and talked until one in the morning."),
  ("אחד מהם סיפר סיפור ארוך וכולם צחקו הרבה.", "One of them told a long story and everyone laughed a lot."),
  ("כשהם הלכו המטבח היה מלא כלים.", "When they left the kitchen was full of dishes."),
  ("שטפנו הכול בשקט וזה היה ערב טוב מאוד.", "We washed everything quietly and it had been a very good evening."),
 ]),
 ("המורה שלי", "My Teacher", [
  ("בבית הספר הייתה לי מורה אחת שאני זוכר עד היום.", "At school I had one teacher I remember to this day."),
  ("היא לימדה היסטוריה ודיברה תמיד בשקט.", "She taught history and always spoke quietly."),
  ("כשמישהו לא הבין היא הסבירה שוב בלי לכעוס.", "When someone didn't understand she explained again without getting angry."),
  ("פעם אחת כתבתי עבודה גרועה והיא לא נתנה לי ציון.", "Once I wrote a bad essay and she didn't give me a mark."),
  ("היא אמרה שאני יכול לכתוב אותה שוב בשבוע הבא.", "She said I could write it again the following week."),
  ("עבדתי עליה שבוע שלם וקיבלתי ציון טוב.", "I worked on it a whole week and got a good mark."),
  ("היום אני מבין מה היא באמת לימדה אותי שם.", "Today I understand what she really taught me there."),
 ]),
 ("הכלב במדרגות", "The Dog on the Stairs", [
  ("בערב אחד מצאתי כלב קטן יושב במדרגות של הבניין.", "One evening I found a small dog sitting on the stairs of the building."),
  ("הוא היה רטוב ופחד מכל רעש ברחוב.", "He was wet and frightened by every noise in the street."),
  ("נתתי לו מים ושמתי לידו שמיכה ישנה.", "I gave him water and put an old blanket next to him."),
  ("דפקתי אצל כל השכנים ושאלתי אם מישהו מכיר אותו.", "I knocked on all the neighbours' doors and asked if anyone knew him."),
  ("בקומה השנייה אישה אמרה שהוא של הבן שלה.", "On the second floor a woman said he belonged to her son."),
  ("הבן ירד מיד ולקח אותו, והכלב שמח מאוד.", "The son came down at once and took him, and the dog was very happy."),
  ("מאז הוא נובח לי שלום כל פעם שאנחנו נפגשים.", "Since then he barks hello at me every time we meet."),
 ]),
 ("השיחה בבוקר", "The Morning Conversation", [
  ("בכל בוקר פגשתי את השכנה שלי ליד תיבות הדואר.", "Every morning I met my neighbour by the letterboxes."),
  ("היא תמיד שאלה מה שלומי ואיך היה הלילה.", "She always asked how I was and how the night had been."),
  ("בהתחלה עניתי בקצרה כי מיהרתי לעבודה.", "At first I answered briefly because I was rushing to work."),
  ("אחרי כמה חודשים התחלתי לצאת חמש דקות מוקדם.", "After a few months I started leaving five minutes early."),
  ("דיברנו על מזג האוויר, על הרחוב ועל הילדים שלה.", "We talked about the weather, the street and her children."),
  ("בחורף היא הייתה חולה שבועיים ולא ראיתי אותה.", "In winter she was ill for two weeks and I didn't see her."),
  ("כשהיא חזרה הבנתי כמה חיכיתי לשיחה הזאת.", "When she came back I realised how much I had missed that conversation."),
 ]),
]


STORIES['advanced'] = [
 ("המכתב שלא נשלח", "The Letter That Was Never Sent", [
  ("אחרי שאבא שלי נפטר מצאתי במגירה שלו מכתב ארוך שכתב לאח שלו ומעולם לא שלח אותו.",
   "After my father passed away I found in his drawer a long letter he had written to his brother and never sent."),
  ("הם הפסיקו לדבר לפני עשרים שנה בגלל ריב על ירושה שאף אחד כבר לא זכר בדיוק.",
   "They stopped speaking twenty years ago because of a quarrel over an inheritance nobody remembered exactly any more."),
  ("קראתי את המכתב פעמיים והתיישבתי ליד השולחן בלי לזוז, כי לא הבנתי מה מבקשים ממני.",
   "I read the letter twice and sat down at the table without moving, because I didn't understand what was being asked of me."),
  ("בסוף החלטתי לנסוע אליו בעצמי, למרות שלא פגשתי אותו מאז שהייתי ילד קטן בכיתה ג.",
   "In the end I decided to drive to him myself, even though I hadn't met him since I was a small child in third grade."),
  ("הוא פתח את הדלת, הביט בי כמה שניות ארוכות ולחש את השם של אבא שלי.",
   "He opened the door, gazed at me for a few long seconds and whispered my father's name."),
  ("התיישבנו במטבח הצר שלו עד הערב ולא קראנו את המכתב, כי כבר לא היה צורך.",
   "We sat down in his narrow kitchen until evening and didn't read the letter, because there was no longer any need."),
  ("כשיצאתי הוא ביקש שאבוא שוב, והבטחתי לו שאבוא, וזאת ההבטחה היחידה ששמרתי השנה.",
   "When I left he asked me to come again, and I promised him I would, and that's the only promise I kept this year."),
 ]),
 ("הדירה הראשונה", "The First Flat", [
  ("הדירה הראשונה ששכרתי הייתה צרה מאוד וקרה בחורף, אבל הרגשתי בה חופשי לגמרי.",
   "The first flat I rented was very narrow and cold in winter, but I felt completely free in it."),
  ("שילמתי עליה כמעט את כל המשכורת, ולכן במשך חודשיים בישלתי רק אורז וביצים.",
   "I paid almost my whole salary for it, so for two months I cooked nothing but rice and eggs."),
  ("החלון היחיד הביט אל חצר קטנה שבה שכן זקן גידל עגבניות בתוך פחים ישנים.",
   "The only window looked onto a small yard where an old neighbour grew tomatoes in old tins."),
  ("בלילות הראשונים לא הצלחתי להירדם, כי כל רעש שעלה מהרחוב נשמע לי חזק מדי.",
   "In the first nights I couldn't fall asleep, because every noise that rose from the street sounded too loud to me."),
  ("אחרי חודש התרגלתי, וכשחזרתי מהעבודה הרגשתי שאני נכנס הביתה ולא סתם לחדר שכור.",
   "After a month I got used to it, and when I came back from work I felt I was coming home and not just into a rented room."),
  ("מאז עברו שמונה שנים ואני גר במקום מרווח יותר, שיש בו חדר לכל אחד מהילדים.",
   "Eight years have passed since and I live somewhere more spacious, where there's a room for each of the children."),
  ("אבל בכל פעם שאני חולף ליד הבניין ההוא אני מרים את הראש ומחפש את החלון.",
   "But every time I pass that building I lift my head and look for the window."),
 ]),
 ("הראיון", "The Interview", [
  ("הגעתי לראיון עשרים דקות מוקדם מדי, ולכן התיישבתי בבית קפה ממול וניסיתי להירגע.",
   "I arrived twenty minutes too early for the interview, so I sat down in a café opposite and tried to calm down."),
  ("הכנתי תשובות לכל שאלה שעלתה בדעתי, אבל הם שאלו דווקא דברים אחרים לגמרי.",
   "I had prepared answers to every question that occurred to me, but they asked completely different things."),
  ("אישה אחת שאלה מה הדבר האחרון שלמדתי, ולא הבנתי אם היא מתכוונת לעבודה או לחיים.",
   "One woman asked what the last thing I had learned was, and I didn't understand whether she meant at work or in life."),
  ("סיפרתי על שכן שלימד אותי לתקן ברז דולף, וכולם צחקו ואני הסמקתי מול כולם.",
   "I told them about a neighbour who taught me to fix a dripping tap, and everyone laughed and I blushed in front of them all."),
  ("יצאתי משם בטוח שנכשלתי, ובערב הסברתי לאשתי שאין שום סיכוי שיתקשרו אליי.",
   "I left sure I had failed, and in the evening I explained to my wife that there was no chance at all they would call."),
  ("אחרי שלושה ימים הם התקשרו והודיעו שדווקא התשובה על הברז שכנעה אותם לקחת אותי.",
   "After three days they called and announced that it was actually the answer about the tap that convinced them to take me."),
  ("אני עובד שם כבר ארבע שנים, ועדיין לא הבנתי מה בדיוק קרה בחדר ההוא.",
   "I've been working there four years now, and I still haven't understood what exactly happened in that room."),
 ]),
 ("השכונה שהשתנתה", "The Neighbourhood That Changed", [
  ("גדלתי בשכונה שבה כל אחד הכיר את כולם, ואף אחד לא נעל את הדלת בצהריים.",
   "I grew up in a neighbourhood where everyone knew everyone, and nobody locked the door in the afternoon."),
  ("היו בה שתי חנויות קטנות, מספרה ובית קפה אחד שבו ישבו אותם גברים כל בוקר.",
   "It had two small shops, a barber's and one café where the same men sat every morning."),
  ("כשחזרתי לבקר אחרי עשר שנים כמעט לא זיהיתי את הרחוב שבו למדתי לרכוב על אופניים.",
   "When I came back to visit after ten years I barely recognised the street where I learned to ride a bicycle."),
  ("במקום החנות נפתחה חנות בגדים יקרה, ובמקום המספרה בנו משרד עם חלונות ענקיים.",
   "In place of the shop an expensive clothes shop had opened, and in place of the barber's they built an office with enormous windows."),
  ("פגשתי אישה אחת שזכרה את אמא שלי, והיא סיפרה לי מי עוד נשאר ומי כבר עזב.",
   "I met a woman who remembered my mother, and she told me who was still there and who had already left."),
  ("היא טענה שהשכונה לא נהייתה גרועה יותר אלא רק אחרת, וכנראה שהיא צדקה.",
   "She argued that the neighbourhood hadn't got worse but only different, and she was probably right."),
  ("בכל זאת יצאתי משם עצוב, כי הבנתי שהמקום ממשיך בלעדיי ולא מחכה לאף אחד.",
   "All the same I left sad, because I realised the place goes on without me and waits for nobody."),
 ]),
 ("הקיץ ההוא", "That Summer", [
  ("בקיץ שאחרי בית הספר עבדתי במסעדה קטנה על החוף ולא תכננתי שום דבר.",
   "In the summer after school I worked in a small restaurant on the beach and planned nothing at all."),
  ("התחלנו את המשמרת בארבע אחר הצהריים וסיימנו אחרי חצות, וכל הזמן היה חם ורועש.",
   "We started the shift at four in the afternoon and finished after midnight, and it was hot and noisy the whole time."),
  ("היינו חמישה עובדים בערך בגיל שלי, ואחרי המשמרת ירדנו למים למרות שהיינו מותשים.",
   "There were five of us, roughly my age, and after the shift we went down to the water even though we were exhausted."),
  ("אחד מהם ניגן בגיטרה בצורה לא טובה במיוחד, אבל אף אחד לא ביקש ממנו להפסיק.",
   "One of them played guitar not especially well, but nobody asked him to stop."),
  ("דיברנו על מה שנעשה בשנה הבאה, וכל אחד תיאר תוכנית שלא התגשמה אף פעם.",
   "We talked about what we would do the following year, and each of us described a plan that never came true."),
  ("בסוף אוגוסט נסגרה המסעדה לעונה, והתפזרנו בלי שהבטחנו לשמור על קשר.",
   "At the end of August the restaurant closed for the season, and we scattered without promising to stay in touch."),
  ("אני זוכר את הקיץ ההוא טוב יותר מכל שנה אחרת, אף על פי שלא קרה בו כלום.",
   "I remember that summer better than any other year, even though nothing happened in it."),
 ]),
 ("הרכבת האחרונה", "The Last Train", [
  ("איחרתי לרכבת האחרונה בשתי דקות וראיתי אותה יוצאת מהתחנה בזמן שרצתי על הרציף.",
   "I missed the last train by two minutes and watched it leaving the station while I was running along the platform."),
  ("התיישבתי על הספסל והבנתי שאין לי דרך לחזור הביתה לפני הבוקר.",
   "I sat down on the bench and realised I had no way of getting home before morning."),
  ("איש אחד שניקה את הרציף שאל לאן אני צריך להגיע, וכשעניתי הוא צחק בקול.",
   "A man who was cleaning the platform asked where I needed to get to, and when I answered he laughed out loud."),
  ("הוא הסביר שהוא גר באותו כיוון ושהוא מסיים את המשמרת בעוד עשרים דקות.",
   "He explained that he lived in the same direction and that he was finishing his shift in twenty minutes."),
  ("נסענו יחד במכונית ישנה שלו והוא סיפר על שלושת הילדים שלו כל הדרך.",
   "We drove together in his old car and he talked about his three children the whole way."),
  ("כשירדתי ליד הבית ניסיתי לשלם לו, אבל הוא סירב ואמר שגם לו קרה דבר כזה פעם.",
   "When I got out near my house I tried to pay him, but he refused and said the same thing had happened to him once."),
  ("מאז אני מגיע לתחנה עשר דקות מוקדם, ותמיד נזכר באיש שניקה את הרציף.",
   "Since then I get to the station ten minutes early, and I always remember the man who cleaned the platform."),
 ]),
 ("החנות שנסגרה", "The Shop That Closed", [
  ("החנות בפינת הרחוב הייתה פתוחה שישים שנה, ומעולם לא ראיתי אותה סגורה באמצע היום.",
   "The shop on the street corner had been open for sixty years, and I never saw it closed in the middle of the day."),
  ("בעל החנות הכיר את כל הלקוחות בשם וידע מי אוהב חלב וכמה לחם כל אחד לוקח.",
   "The shopkeeper knew all the customers by name and knew who liked milk and how much bread each one took."),
  ("כשהוא חלה בחורף בתו החליפה אותו, אבל היא לא הצליחה לזכור את כל ההזמנות.",
   "When he fell ill in the winter his daughter replaced him, but she couldn't remember all the orders."),
  ("באביב הוא חזר לכמה שבועות, ואז תלה מודעה קטנה שהודיעה על סגירה בסוף החודש.",
   "In the spring he came back for a few weeks, and then hung a small notice announcing a closure at the end of the month."),
  ("ביום האחרון נכנסו הרבה אנשים שלא קנו כלום ורק לחצו את היד שלו ואמרו תודה.",
   "On the last day a lot of people came in who bought nothing and only shook his hand and said thank you."),
  ("שאלתי אותו מה יעשה עכשיו והוא ענה שסוף סוף ילמד לשחות בבריכה העירונית.",
   "I asked him what he would do now and he answered that he would finally learn to swim at the municipal pool."),
  ("החנות עמדה ריקה כמעט שנה, ועכשיו יש שם בית קפה שאני נכנס אליו לפעמים.",
   "The shop stood empty for almost a year, and now there's a café there that I go into sometimes."),
 ]),
 ("השעון של סבא", "Grandpa's Watch", [
  ("כשסבא שלי נפטר קיבלתי ממנו שעון ישן שהוא ענד על היד כל השנים שהכרתי אותו.",
   "When my grandfather died I received from him an old watch that he wore on his wrist all the years I knew him."),
  ("השעון פיגר שלוש דקות בכל יום, וסבא סירב לתקן אותו כי כך התרגל לחשב.",
   "The watch lost three minutes a day, and grandpa refused to fix it because that was how he was used to calculating."),
  ("הנחתי אותו במגירה ולא נגעתי בו שנתיים, כי חשבתי שלא מתאים לי לענוד אותו.",
   "I put it in a drawer and didn't touch it for two years, because I thought it didn't suit me to wear it."),
  ("ביום שנולד הבן שלי הוצאתי אותו והבנתי שהוא עדיין עובד, למרות שאיש לא מתח אותו.",
   "On the day my son was born I took it out and realised it was still working, even though nobody had wound it."),
  ("לקחתי אותו לשען זקן ברחוב יפו, והוא הסתכל עליו והחזיר לי אותו בלי לגעת.",
   "I took it to an old watchmaker on Jaffa Street, and he looked at it and gave it back to me without touching it."),
  ("הוא אמר ששעון שמפגר שלוש דקות בדיוק כבר שישים שנה לא צריך שום תיקון.",
   "He said a watch that has lost exactly three minutes a day for sixty years needs no repair at all."),
  ("אני עונד אותו בכל אירוע משפחתי, ותמיד מגיע שלוש דקות אחרי כולם.",
   "I wear it at every family occasion, and I always arrive three minutes after everyone else."),
 ]),
 ("שיחה במונית", "A Conversation in a Taxi", [
  ("לקחתי מונית לשדה התעופה בחמש בבוקר, ובהתחלה לא רציתי לדבר עם אף אחד.",
   "I took a taxi to the airport at five in the morning, and at first I didn't want to talk to anyone."),
  ("הנהג שאל לאן אני טס, וכשאמרתי לו הוא סיפר שהוא נולד באותה עיר בדיוק.",
   "The driver asked where I was flying to, and when I told him he said he had been born in that very city."),
  ("הוא עזב אותה בגיל תשע עם ההורים שלו ומאז ביקר שם רק פעמיים.",
   "He left it at the age of nine with his parents and since then had visited only twice."),
  ("במשך כל הנסיעה הוא תיאר רחובות ובתים, ואני זיהיתי כמעט את כולם.",
   "Throughout the drive he described streets and houses, and I recognised almost all of them."),
  ("כשהגענו לשדה התעופה הוא ביקש שאצלם בשבילו את הכיכר שבה שיחק כילד.",
   "When we reached the airport he asked me to photograph for him the square where he had played as a child."),
  ("צילמתי אותה בערב הראשון ושלחתי לו את התמונה, והוא ענה במילה אחת בלבד.",
   "I photographed it on the first evening and sent him the picture, and he answered with a single word."),
  ("כתוב היה שם תודה, ומאז שמרתי את המספר שלו אף על פי שלא התקשרתי אליו.",
   "It said thank you, and since then I kept his number even though I never called him."),
 ]),
 ("הלילה בלי חשמל", "The Night Without Electricity", [
  ("בערב אחד בחורף נפל החשמל בכל הבניין, ותוך רגע הכול נהיה חשוך ושקט לגמרי.",
   "One winter evening the power went out in the whole building, and in a moment everything became completely dark and quiet."),
  ("ירדנו כולנו למדרגות עם נרות, וזאת הייתה הפעם הראשונה שראיתי את כל השכנים ביחד.",
   "We all came down to the stairs with candles, and it was the first time I had seen all the neighbours together."),
  ("שכנה מהקומה השנייה הביאה קומקום ישן שפועל על גז והרתיחה תה לכולם.",
   "A neighbour from the second floor brought an old kettle that runs on gas and boiled tea for everyone."),
  ("ילד קטן ביקש לשמוע סיפורי רוחות, וההורים שלו הסכימו מיד למרות שהשעה הייתה מאוחרת.",
   "A small boy asked to hear ghost stories, and his parents agreed at once even though the hour was late."),
  ("ישבנו שם כמעט שלוש שעות וגילינו שהזוג מהקומה העליונה מתגורר איתנו כבר תשע שנים מבלי שידענו.",
   "We sat there almost three hours and discovered that the couple from the top floor had been living with us for nine years without our knowing."),
  ("כשהחשמל חזר כולם צעקו מרוב שמחה, ואז טיפסו לדירות והדלת נסגרה אחרי כל אחד.",
   "When the power came back everyone shouted for joy, and then climbed to their flats and the door closed behind each one."),
  ("למחרת נפגשנו במדרגות והחלפנו שלום, ומאז אנחנו עושים את זה כל בוקר.",
   "The next day we met on the stairs and exchanged greetings, and since then we do it every morning."),
 ]),
 ("איך למדתי לבשל", "How I Learned to Cook", [
  ("עד גיל עשרים ושתיים לא בישלתי כלום, כי תמיד מישהו אחר עמד במטבח במקומי.",
   "Until the age of twenty-two I cooked nothing, because someone else always stood in the kitchen instead of me."),
  ("כשעברתי לגור לבד גיליתי שאני יודע להכין רק חביתה, וגם אותה שרפתי פעמיים.",
   "When I moved to live alone I discovered I only knew how to make an omelette, and I burned even that twice."),
  ("התקשרתי לאמא שלי וביקשתי מתכון פשוט, והיא הכתיבה לי אותו בטלפון בסבלנות אינסופית.",
   "I called my mother and asked for a simple recipe, and she dictated it to me on the phone with endless patience."),
  ("בפעם הראשונה שכחתי את המלח לגמרי, ובפעם השנייה הוספתי כל כך הרבה שלא יכולתי לאכול.",
   "The first time I forgot the salt entirely, and the second time I added so much I couldn't eat it."),
  ("אחרי חודשיים כבר הכנתי מרק שהחברים שלי אכלו בלי שהתלוננו, וזאת הייתה הצלחה גדולה.",
   "After two months I was already making a soup my friends ate without complaining, and that was a great success."),
  ("היום אני מבשל כמעט כל ערב, ואף פעם לא מודד שום דבר בכוס או בכפית.",
   "Today I cook almost every evening, and I never measure anything in a cup or a teaspoon."),
  ("כשאמא שלי מגיעה לבקר היא טועמת ואומרת שזה טעים, ואז מוסיפה קצת מלח בשקט.",
   "When my mother comes to visit she tastes it and says it's delicious, and then quietly adds a little salt."),
 ]),
 ("הצילום הישן", "The Old Photograph", [
  ("בזמן שסידרתי ארונות מצאתי מעטפה ובתוכה צילום שחור לבן שלא זיהיתי אף אחד בו.",
   "While I was tidying cupboards I found an envelope and inside it a black and white photograph in which I recognised nobody."),
  ("בגב הצילום מישהו רשם תאריך משנת חמישים ושבע ושתי מילים שלא הצלחתי לפענח.",
   "On the back of the photograph someone had written a date from nineteen fifty-seven and two words I couldn't decipher."),
  ("הראיתי אותו לאמא שלי, והיא לקחה משקפיים והביטה בו זמן רב מבלי לומר מילה.",
   "I showed it to my mother, and she took her glasses and gazed at it a long while without saying a word."),
  ("בסוף היא הצביעה על ילדה קטנה בשמאל והסבירה שזאת אחותה שנפטרה לפני שנולדתי.",
   "In the end she pointed at a small girl on the left and explained that it was her sister who died before I was born."),
  ("מעולם לא שמעתי עליה, כי במשפחה שלנו לא נהגו לדבר על דברים שכואבים.",
   "I had never heard of her, because in our family it wasn't the custom to talk about painful things."),
  ("אמא סיפרה על אותה שנה כמעט שעה, ובסוף ביקשה שאחזיר את הצילום למקום.",
   "Mum talked about that year for almost an hour, and at the end asked me to put the photograph back."),
  ("החזרתי אותו, אבל צילמתי אותו קודם בטלפון, כי הבנתי שלא נדבר על זה שוב.",
   "I put it back, but I photographed it first on my phone, because I understood we wouldn't speak of it again."),
 ]),
 ("המעבר לעיר", "The Move to the City", [
  ("עברתי לעיר הגדולה בגיל שלושים, אחרי ששלוש עשרה שנים גרתי במושב קטן בדרום.",
   "I moved to the big city at thirty, after living thirteen years in a small village in the south."),
  ("בשבוע הראשון הלכתי לאיבוד שלוש פעמים, כי כל הרחובות נראו לי בדיוק אותו דבר.",
   "In the first week I got lost three times, because all the streets looked exactly the same to me."),
  ("הרעש הפריע לי מאוד בהתחלה, ובלילות הראשונים ישנתי עם כרית על האוזניים.",
   "The noise bothered me a lot at first, and in the first nights I slept with a pillow over my ears."),
  ("אחרי חודש גיליתי שוק קטן ליד הבית שבו המוכרים זיהו אותי כבר בשבוע השני.",
   "After a month I discovered a small market near the house where the sellers recognised me by the second week."),
  ("מצאתי עבודה קרובה לבית ולכן ויתרתי על המכונית, ומאז אני הולך לכל מקום ברגל.",
   "I found work close to home so I gave up the car, and since then I walk everywhere."),
  ("החברים מהמושב שואלים אם אני מתגעגע, ואני עונה שכן אבל שלא הייתי חוזר.",
   "My friends from the village ask whether I miss it, and I answer that I do but that I wouldn't go back."),
  ("בשבתות אני יושב במרפסת, שומע את העיר מרחוק ומרגיש שהמקום הזה כבר שלי.",
   "On Saturdays I sit on the balcony, hear the city from a distance and feel that this place is mine now."),
 ]),
 ("הבוקר של הבחינה", "The Morning of the Exam", [
  ("בבוקר של הבחינה האחרונה התעוררתי שעה לפני השעון, ולא הצלחתי להירדם שוב.",
   "On the morning of the last exam I woke an hour before the alarm, and couldn't fall asleep again."),
  ("למדתי חודש שלם ובכל זאת הרגשתי שאני לא זוכר שום דבר שקראתי בשבוע האחרון.",
   "I had studied a whole month and still felt I remembered nothing I had read in the last week."),
  ("בדרך לאוניברסיטה פגשתי סטודנטית מהקורס שאמרה שגם היא לא ישנה כמעט בכלל.",
   "On the way to the university I met a student from the course who said she had hardly slept either."),
  ("ישבנו יחד על המדשאה עשרים דקות ובחנו זה את זה על החומר בקול רם.",
   "We sat together on the lawn for twenty minutes and tested each other on the material out loud."),
  ("כשנכנסתי לאולם וקיבלתי את השאלון הבנתי שדווקא כל מה שחזרנו עליו מופיע בו.",
   "When I entered the hall and received the paper I realised that everything we had gone over was in it."),
  ("סיימתי חצי שעה לפני הזמן ויצאתי, ואז עמדתי בחוץ וחיכיתי לה שתסיים גם.",
   "I finished half an hour early and left, and then stood outside and waited for her to finish too."),
  ("קיבלנו את אותו הציון בדיוק, ומאז אנחנו לומדים יחד לכל בחינה שנייה.",
   "We got exactly the same mark, and since then we study together for every other exam."),
 ]),
 ("הכלב שחיכה", "The Dog That Waited", [
  ("ברחוב שלנו הסתובב כלב חום שהתיישב כל בוקר מול אותו בניין וחיכה שם למישהו.",
   "On our street there was a brown dog that sat down every morning opposite the same building and waited there for someone."),
  ("בהתחלה חשבנו שהוא אבד, אבל הפרווה שלו נראתה מסורקת ולכן הבנו שמישהו מטפל בו.",
   "At first we thought he was lost, but his coat looked brushed so we realised somebody was looking after him."),
  ("שכנה אחת סיפרה שהאישה שגידלה אותו הועברה בסתיו לבית אבות בעיר אחרת.",
   "One neighbour said that the woman who raised him had been moved in the autumn to a care home in another city."),
  ("הבן שלה לקח את הכלב אליו, אבל הוא נמלט בכל הזדמנות, חזר לרחוב והתיישב מול הבניין.",
   "Her son took the dog to his place, but he escaped at every opportunity, came back to the street and sat down opposite the building."),
  ("במשך חודשיים כמעט כל מי שגר ברחוב הביא לו מים או שאריות בדרך לעבודה.",
   "For two months almost everyone who lived on the street brought him water or leftovers on the way to work."),
  ("באחד הימים הבן הביא את אמא שלו לביקור, והכלב זיהה אותה מרחוק והתחיל לנבוח.",
   "One day the son brought his mother for a visit, and the dog recognised her from afar and started barking."),
  ("מאז הם באים כל שבוע, והכלב יושב איתה על הספסל ומחכה שהיא תלטף אותו.",
   "Since then they come every week, and the dog sits with her on the bench and waits for her to stroke him."),
 ]),
 ("הגינה על הגג", "The Garden on the Roof", [
  ("שכן אחד ביקש רשות מכל הדיירים להשתמש בגג, ורק אחרי חצי שנה כולם הסכימו.",
   "One neighbour asked all the residents for permission to use the roof, and only after six months did everyone agree."),
  ("הוא הזמין עשרים עציצים ריקים ושק אדמה כבד, סחב את הכול לבד במדרגות הצרות.",
   "He ordered twenty empty pots and a heavy sack of soil, dragged it all up the narrow stairs alone."),
  ("בהתחלה צחקנו עליו קצת, כי לא האמנו שמשהו יגדל שם בחום של הקיץ.",
   "At first we laughed at him a bit, because we didn't believe anything would grow up there in the summer heat."),
  ("באביב הוא הזמין את כל הבניין לעלות, ושם גילינו עגבניות, נענע ושתי גפנים קטנות.",
   "In the spring he invited the whole building up, and there we discovered tomatoes, mint and two small vines."),
  ("מאז כל אחד מטפל בפינה שלו, והילדים טיפסו לשם כל אחר צהריים והשקו לפי רשימה שתלינו על הדלת.",
   "Since then everyone looks after their own corner, and the children climbed up every afternoon and watered according to a list we hung on the door."),
  ("השכן שהתחיל את הכול עזב לפני שנה, אבל הוא השאיר לנו דף ארוך ובו כל ההוראות.",
   "The neighbour who started it all left a year ago, but he left us a long page with all the instructions."),
  ("אנחנו עדיין קוראים לגג הגינה שלו, אף על פי שהוא לא ראה אותה כבר מזמן.",
   "We still call the roof his garden, even though he hasn't seen it for a long time."),
 ]),
 ("השיר ברדיו", "The Song on the Radio", [
  ("נסעתי לבד בכביש ריק בשתיים בלילה, וברדיו התנגן שיר שלא שמעתי שנים.",
   "I was driving alone on an empty road at two in the morning, and on the radio played a song I hadn't heard in years."),
  ("עצרתי בצד הדרך והקשבתי עד הסוף, כי פתאום נזכרתי איפה שמעתי אותו לראשונה.",
   "I pulled over at the side of the road and listened to the end, because I suddenly remembered where I first heard it."),
  ("סבתא שלי נהגה לשיר אותו במטבח בזמן שקילפה תפוחי אדמה לארוחת הצהריים.",
   "My grandmother used to sing it in the kitchen while she peeled potatoes for lunch."),
  ("לא ידעתי בכלל שזה שיר אמיתי, וכל השנים חשבתי שהיא המציאה אותו בעצמה.",
   "I had no idea it was a real song, and all those years I thought she had made it up herself."),
  ("חיפשתי אותו למחרת ומצאתי הקלטה ישנה משנת ארבעים ותשע עם זמרת שאיש לא זוכר.",
   "I looked it up the next day and found an old recording from nineteen forty-nine with a singer nobody remembers."),
  ("שלחתי אותו לאמא ולדודות שלי, וכולן ענו תוך דקות שגם הן שכחו אותו לגמרי.",
   "I sent it to my mother and my aunts, and they all replied within minutes that they had completely forgotten it too."),
  ("עכשיו אנחנו שרים אותו בכל ארוחה משפחתית, אף על פי שאיש לא זוכר את המילים.",
   "Now we sing it at every family meal, even though nobody remembers the words."),
 ]),
 ("הספר ששכחתי ברכבת", "The Book I Left on the Train", [
  ("שכחתי ספר על המושב ברכבת, ורק אחרי שהגעתי הביתה גיליתי שהתיק שלי ריק.",
   "I left a book on the seat on the train, and only after I got home did I discover my bag was empty."),
  ("זה לא היה ספר יקר, אבל רשמתי בשוליים שלו הערות וציטוטים במשך חצי שנה.",
   "It wasn't an expensive book, but I had written notes and quotations in its margins over six months."),
  ("התקשרתי למחלקת האבידות ואמרו לי לבוא בעוד שבוע, כי הכול מגיע אליהם באיחור.",
   "I called the lost property office and they told me to come in a week, because everything reaches them late."),
  ("כשהגעתי לשם המצאי היה עצום, ופקידה עייפה הוציאה ארגז מלא ספרים שאיש לא תבע.",
   "When I got there the stock was enormous, and a tired clerk pulled out a box full of books nobody had claimed."),
  ("הספר שלי לא היה שם, אבל מצאתי בארגז רומן ישן שרציתי לקרוא כבר שנים.",
   "My book wasn't there, but in the box I found an old novel I had wanted to read for years."),
  ("הפקידה אמרה שאם אף אחד לא בא אחרי חודשיים אפשר לקחת, ורשמה את השם שלי.",
   "The clerk said that if nobody came after two months you could take it, and she wrote down my name."),
  ("היא התקשרה אליי בפברואר, ואני נוסע ברכבת עם הרומן ההוא כבר שנה שלמה.",
   "She called me in February, and I've been riding the train with that novel for a whole year now."),
 ]),
 ("יום ההולדת של אמא", "Mum's Birthday", [
  ("שלושה שבועות תכננו לאמא מסיבה מפתיעה, ושמרנו את הסוד בקושי רב מאוד.",
   "For three weeks we planned a surprise party for Mum, and kept the secret only with great difficulty."),
  ("אחותי הזמינה עשרים אורחים, הבטחתי לה שאביא את אמא הביתה בדיוק בשבע וחצי.",
   "My sister invited twenty guests and I promised her I would bring Mum home at exactly half past seven."),
  ("לקחתי אותה לקניות בקניון והמצאתי תירוצים חדשים בכל פעם שהיא רצתה לחזור.",
   "I took her shopping at the mall and invented new excuses every time she wanted to go back."),
  ("כשנכנסנו לבית כולם צעקו הפתעה, והיא נעצרה בדלת וחייכה בלי להגיד כלום.",
   "When we came into the house everyone shouted surprise, and she stopped in the doorway and smiled without saying anything."),
  ("אחר כך היא הודתה שידעה הכול כבר שבועיים, כי שכחנו רשימה על שולחן המטבח.",
   "Afterwards she admitted she had known everything for two weeks, because we forgot a list on the kitchen table."),
  ("היא התאמנה על הפרצוף המופתע כל ערב מול המראה, וגם צילמה את עצמה פעמיים.",
   "She had practised the surprised face every evening in front of the mirror, and even photographed herself twice."),
  ("כולם צחקו חצי שעה, ומאז אנחנו נזכרים בהצגה הזאת בכל יום הולדת שמגיע.",
   "Everyone laughed for half an hour, and since then we think back to that performance at every birthday that comes."),
 ]),
 ("החבר מהאוניברסיטה", "The Friend from University", [
  ("הכרתי אותו ביום הראשון באוניברסיטה, כי שנינו הגענו בטעות לאותה כיתה שגויה.",
   "I met him on the first day at university, because we both arrived by mistake at the same wrong classroom."),
  ("במשך שלוש שנים ישבנו יחד בכל שיעור וחילקנו כל כריך שמישהו מאיתנו הביא.",
   "For three years we sat together in every class and shared every sandwich either of us brought."),
  ("אחרי הלימודים הוא נסע לעבוד בחוץ לארץ, ואני נשארתי ומצאתי עבודה בעיר.",
   "After our studies he went to work abroad, and I stayed and found work in the city."),
  ("בהתחלה כתבנו כל שבוע, אחר כך כל חודש, ואחרי שנתיים הפסקנו כמעט לגמרי.",
   "At first we wrote every week, then every month, and after two years we stopped almost entirely."),
  ("לפני חודש הוא הודיע שהוא חוזר לביקור, וקבענו להיפגש באותו בית קפה הישן.",
   "A month ago he announced he was coming back for a visit, and we arranged to meet in that same old café."),
  ("פחדתי שלא יהיה לנו על מה לדבר, אבל אחרי חמש דקות זה נמשך כאילו לא עברו שנים.",
   "I was afraid we wouldn't have anything to talk about, but after five minutes it went on as if no years had passed."),
  ("ישבנו שם עד שסגרו את המקום, והבטחנו זה לזה שלא נחכה שוב כל כך הרבה.",
   "We sat there until they closed the place, and promised each other we wouldn't wait that long again."),
 ]),
 ("הארנק שאבד", "The Wallet That Was Lost", [
  ("איבדתי את הארנק שלי בקניון ביום שישי, וגיליתי את זה רק כשעמדתי בקופה.",
   "I lost my wallet at the mall on Friday, and discovered it only when I was standing at the till."),
  ("חזרתי על כל המסלול שעברתי, בדקתי בכל חנות ושאלתי כל מוכר שנראה לי מוכר.",
   "I retraced the whole route I had taken, checked in every shop and asked every seller who looked familiar to me."),
  ("ביטלתי את הכרטיסים בטלפון תוך חצי שעה, אבל הצטערתי בעיקר על תצלום דהוי שהחזקתי בתא הפנימי.",
   "I cancelled the cards by phone within half an hour, but mostly I regretted a faded photo I kept in the inner compartment."),
  ("אחרי ארבעה ימים התקשרה אליי אישה שמצאה אותו ברחוב ליד תחנת האוטובוס.",
   "After four days a woman called me who had found it in the street near the bus stop."),
  ("היא הסבירה שחיפשה אותי לפי כרטיס ספרייה שנשאר שם, כי הכסף כבר נעלם.",
   "She explained that she had searched for me by a library card that was still there, because the money had already gone."),
  ("נפגשנו למחרת והצעתי לה משהו, אבל היא סירבה וביקשה רק שאעשה את זה למישהו אחר.",
   "We met the next day and I offered her something, but she refused and asked only that I do the same for someone else."),
  ("התמונה נשארה שלמה בפנים, ומאז היא תלויה במסגרת במסדרון ולא נודדת איתי.",
   "The photograph stayed whole inside, and since then it hangs in a frame in the hallway and doesn't travel with me."),
 ]),
 ("שנה בחוץ לארץ", "A Year Abroad", [
  ("בגיל עשרים ושש עזבתי הכול ונסעתי לשנה לעיר קרה שלא הכרתי בה איש.",
   "At twenty-six I left everything and went for a year to a cold city where I knew nobody."),
  ("בחודשיים הראשונים כמעט לא דיברתי עם אף אחד, כי השפה שם נשמעה לי בלתי אפשרית.",
   "In the first two months I hardly spoke to anyone, because the language there sounded impossible to me."),
  ("מצאתי עבודה במאפייה קטנה, והמנהל לימד אותי מילים חדשות בזמן שלשנו בצק יחד.",
   "I found work in a small bakery, and the manager taught me new words while we kneaded dough together."),
  ("בחורף החשיך שם בארבע אחר הצהריים, וזה הפחיד אותי הרבה יותר מהקור עצמו.",
   "In winter it got dark there at four in the afternoon, and that frightened me far more than the cold itself."),
  ("באביב התחלתי להבין את הבדיחות של הלקוחות, וזה שינה את הכול תוך שבועות.",
   "In the spring I started to understand the customers' jokes, and that changed everything within weeks."),
  ("כשהגיע הזמן לחזור ארזתי מזוודה אחת בלבד, כי כל השאר כבר לא נראה לי חשוב.",
   "When the time came to go back I packed only one suitcase, because everything else no longer seemed important to me."),
  ("המנהל העניק לי שקית קמח כמזכרת, ואני עדיין מחביא אותה במדף העליון בארון.",
   "The manager gave me a bag of flour as a keepsake, and I still hide it on the top shelf of the cupboard."),
 ]),
 ("הכביש למדבר", "The Road to the Desert", [
  ("יצאנו לדרום בחמש בבוקר, כי רצינו להגיע למכתש לפני שהשמש תעלה גבוה.",
   "We set out south at five in the morning, because we wanted to reach the crater before the sun rose high."),
  ("אחרי שעתיים נגמר הכביש הסלול, המשכנו על דרך עפר צרה והמכונית רעדה כל הזמן.",
   "After two hours the paved road ended, we continued on a narrow dirt track and the car shook the whole time."),
  ("עצרנו ליד עץ בודד, שתינו קפה מהתרמוס ולא שמענו שום דבר מלבד הרוח בענפים.",
   "We stopped by a lone tree, drank coffee from the thermos and heard nothing but the wind in the branches."),
  ("חבר שלי נשבע שראה יעל על הרכס, אבל אף אחד מאיתנו לא הצליח לצלם אותה.",
   "A friend of mine swore he saw an ibex on the ridge, but none of us managed to photograph it."),
  ("בצהריים הגענו למקום שממנו רואים את כל המכתש, שתקנו שם כמה דקות ואיש לא צילם.",
   "At midday we reached a place from which you can see the whole crater, we were silent there a few minutes and nobody took a photograph."),
  ("בדרך חזרה נתקע הרכב בחול, וחפרנו כמעט שעה עד שהצלחנו לצאת משם.",
   "On the way back the vehicle got stuck in sand, and we dug for almost an hour until we managed to get out."),
  ("הגענו הביתה מלוכלכים ומאוחר, וכולנו הסכמנו שנחזור לשם כבר בחורף הבא.",
   "We got home dirty and late, and we all agreed we would go back there the very next winter."),
 ]),
 ("מה שלא אמרתי", "What I Didn't Say", [
  ("בערב שלפני הטיסה של אחי ישבנו במטבח ודיברנו על דברים לא חשובים בכלל.",
   "On the evening before my brother's flight we sat in the kitchen and talked about entirely unimportant things."),
  ("רציתי לומר לו שאני גאה בו, אבל בכל פעם שפתחתי את הפה יצא משהו אחר.",
   "I wanted to tell him I was proud of him, but every time I opened my mouth something else came out."),
  ("דיברנו על הכבודה, על השעה שהוא צריך לצאת ועל מזג האוויר שמחכה לו שם.",
   "We talked about the luggage, about the time he had to leave and about the weather waiting for him there."),
  ("בבוקר הסעתי אותו לשדה התעופה, והוא נרדם במכונית אחרי חמש דקות נסיעה.",
   "In the morning I drove him to the airport, and he fell asleep in the car after five minutes of driving."),
  ("כשהעירו את הנוסעים לטיסה הוא חיבק אותי חזק ואמר שהוא יתקשר בערב.",
   "When they called the passengers for the flight he hugged me hard and said he would call in the evening."),
  ("חזרתי לבד לחניון והבנתי שוב שלא הצלחתי לומר את המשפט האחד שתכננתי.",
   "I went back to the car park alone and realised again that I hadn't managed to say the one sentence I had planned."),
  ("כתבתי לו אותו באותו לילה בהודעה, והוא ענה שידע את זה ממילא.",
   "I wrote it to him that same night in a message, and he answered that he knew it anyway."),
 ]),
 ("המורה של אחותי", "My Sister's Teacher", [
  ("אחותי שנאה בית ספר עד כיתה חמש, בכתה כל בוקר והתחננה שנשאיר אותה בבית.",
   "My sister hated school until fifth grade, cried every morning and begged us to leave her at home."),
  ("בשנה ההיא הגיעה מורה חדשה שהחליטה לשבת איתה חצי שעה אחרי כל שיעור.",
   "That year a new teacher arrived who decided to sit with her for half an hour after every lesson."),
  ("היא גילתה שאחותי לא רואה טוב את הלוח, שלחה אותה לבדיקה והתקשרה אלינו בערב.",
   "She discovered that my sister couldn't see the board well, sent her for a test and called us in the evening."),
  ("קיבלנו משקפיים תוך עשרה ימים, ותוך חודשיים הציונים שלה השתנו לגמרי.",
   "We got glasses within ten days, and within two months her marks changed completely."),
  ("אמא שלי הודתה למורה בכל פגישה, והמורה ענתה בכל פעם שזאת העבודה שלה.",
   "My mother thanked the teacher at every meeting, and the teacher answered each time that it was her job."),
  ("אחותי סיימה תואר בהוראה לפני שנתיים ועובדת עכשיו באותו בית ספר בדיוק.",
   "My sister finished a teaching degree two years ago and now works at that very same school."),
  ("המורה כבר פרשה מההוראה, אבל היא הגיעה לטקס והתיישבה בשורה הראשונה.",
   "The teacher has already retired from teaching, but she came to the ceremony and sat down in the front row."),
 ]),
 ("שיעורי נהיגה", "Driving Lessons", [
  ("התחלתי ללמוד נהיגה בגיל שלושים ושמונה, אחרי שכל החברים שלי כבר נהגו שנים.",
   "I started learning to drive at thirty-eight, after all my friends had already been driving for years."),
  ("המורה שלי היה איש שקט שכמעט לא דיבר, ורק הצביע לאן צריך לפנות.",
   "My instructor was a quiet man who barely spoke, and only pointed where I needed to turn."),
  ("בשיעור השלישי כיביתי את המנוע ארבע פעמים ברמזור אחד, והוא רק חייך ואמר שוב.",
   "In the third lesson I stalled the engine four times at one traffic light, and he only smiled and said again."),
  ("נכשלתי במבחן הראשון בגלל חנייה, ולמדתי אותה אחר כך שלושה שבועות ברציפות.",
   "I failed the first test because of parking, and afterwards I practised it for three weeks straight."),
  ("במבחן השני הבוחן כמעט לא כתב כלום, וזה הפחיד אותי הרבה יותר מהצעקות.",
   "In the second test the examiner wrote almost nothing, and that frightened me far more than shouting would have."),
  ("כשקיבלתי את הרישיון התקשרתי קודם כול למורה, והוא ענה שהוא ידע מההתחלה.",
   "When I got my licence I called the instructor first of all, and he answered that he had known from the start."),
  ("אני נוהג היום כל יום לעבודה, ועדיין מכבה את הרדיו כשאני מחפש חנייה.",
   "Today I drive to work every day, and I still turn off the radio when I'm looking for parking."),
 ]),
 ("המפתח מתחת לשטיח", "The Key Under the Mat", [
  ("במשך שלושים שנה השאירו ההורים שלי מפתח מתחת לשטיח שליד דלת הכניסה.",
   "For thirty years my parents left a key under the mat by the front door."),
  ("כל השכנים ידעו על זה, וכמה מהם השתמשו בו כשהם שכחו את המפתחות שלהם.",
   "All the neighbours knew about it, and several of them used it when they forgot their own keys."),
  ("פעם אחת הגעתי בלילה בלי להודיע, מצאתי את המפתח בדיוק במקום ונכנסתי בשקט.",
   "Once I arrived at night without letting them know, found the key exactly in place and went in quietly."),
  ("אמא שלי טענה תמיד שגנב לא מחפש מתחת לשטיח, כי זה פשוט מדי בשבילו.",
   "My mother always argued that a thief doesn't look under the mat, because it's too simple for him."),
  ("אחרי שהם עזבו לדירה קטנה יותר הם התקינו מנעול חדש עם קוד, וזרקו את השטיח.",
   "After they left for a smaller flat they installed a new lock with a code, and threw the mat away."),
  ("שכחתי את הקוד בביקור הראשון ועמדתי בחוץ עשרים דקות עד שמישהו פתח לי.",
   "I forgot the code on the first visit and stood outside twenty minutes until someone opened for me."),
  ("אמא צחקה ואמרה שהיא הזהירה אותם, ואבא שלי הסכים איתה בשקט מוחלט.",
   "Mum laughed and said she had warned them, and my father agreed with her in complete silence."),
 ]),
 ("השכנה מלמטה", "The Neighbour Downstairs", [
  ("השכנה מלמטה התלוננה על רעש כל שבוע, ובהתחלה כעסתי עליה מאוד.",
   "The neighbour downstairs complained about noise every week, and at first I was very angry with her."),
  ("ירדתי אליה פעם אחת כדי לריב, אבל היא הזמינה אותי להיכנס והציעה עוגיות.",
   "I went down to her once in order to argue, but she invited me in and offered biscuits."),
  ("היא הסבירה שהיא עובדת בלילות בבית חולים וישנה בשעות שאנחנו בבית.",
   "She explained that she works nights at a hospital and sleeps at the hours when we're at home."),
  ("הצעתי שנקבע שעות שקטות, והיא הסכימה מיד ורשמה אותן על פתק בטלפון.",
   "I suggested we set quiet hours, and she agreed immediately and noted them on a note in her phone."),
  ("מאז לא שמעתי ממנה תלונה אחת, והיא עצרה אותי במדרגות רק כדי לשאול מה שלומנו.",
   "Since then I haven't heard a single complaint from her, and she stopped me on the stairs only to ask how we were."),
  ("בקיץ היא נסעה לחודש והשאירה לנו את הצמחים שלה ואת המפתח שלה.",
   "In summer she went away for a month and left us her plants and her key."),
  ("החזרתי לה הכול ירוק ופורח, והיא הודתה לי כאילו הצלתי משהו יקר ערך.",
   "I gave it all back to her green and blooming, and she thanked me as if I had rescued something precious."),
 ]),
 ("הטלפון באמצע הלילה", "The Call in the Middle of the Night", [
  ("הטלפון צלצל בשתיים וחצי בלילה, וקפצתי מהמיטה לפני שהספקתי להתעורר לגמרי.",
   "The phone rang at half past two in the night, and I jumped out of bed before I had fully woken."),
  ("קול של גבר מבוגר שאל אם מדובר במוסך, וברקע שמעתי גשם וכביש.",
   "The voice of an older man asked whether this was a garage, and in the background I heard rain and a road."),
  ("הסברתי לו שטעה במספר, אבל משהו בקול שלו גרם לי להישאר על הקו.",
   "I explained to him that he had the wrong number, but something in his voice made me stay on the line."),
  ("הוא סיפר שהמכונית שלו נעצרה בצד הדרך ושהוא לא זוכר לאן הוא נסע.",
   "He said his car had stopped at the side of the road and that he couldn't remember where he was driving."),
  ("שאלתי איפה הוא נמצא בדיוק, והוא תיאר גשר וצומת שזיהיתי מיד לפי התיאור.",
   "I asked exactly where he was, and he described a bridge and a junction I recognised at once from the description."),
  ("התקשרתי למשטרה ונשארתי איתו בטלפון עוד עשרים דקות עד שהם הגיעו אליו.",
   "I called the police and stayed on the phone with him another twenty minutes until they reached him."),
  ("הוא לא ידע את השם שלי ואני לא ידעתי את שלו, ומאז חשבתי עליו הרבה.",
   "He didn't know my name and I didn't know his, and since then I have thought about him a lot."),
 ]),
 ("הדרך חזרה", "The Way Back", [
  ("אחרי שתים עשרה שנים בחוץ לארץ החלטנו לחזור, ומכרנו כמעט הכול תוך חודשיים.",
   "After twelve years abroad we decided to come back, and sold almost everything within two months."),
  ("הילדים לא רצו לעזוב את החברים שלהם, והבת הגדולה לא דיברה איתנו שבוע.",
   "The children didn't want to leave their friends, and my eldest daughter didn't speak to us for a week."),
  ("נחתנו בקיץ בחום נורא, והדירה שקיבלנו הייתה קטנה בהרבה ממה שזכרנו.",
   "We landed in summer in terrible heat, and the flat we got was much smaller than we remembered."),
  ("בשבועות הראשונים הילדים התעקשו לדבר בבית רק בשפה שהם למדו שם.",
   "In the first weeks the children insisted on speaking at home only in the language they had learned there."),
  ("בספטמבר הם התחילו בבית ספר חדש, ואחרי חודש הם כבר ריבו בעברית שוטפת.",
   "In September they started a new school, and after a month they were already quarrelling in fluent Hebrew."),
  ("בחורף הראשון ירד גשם שבוע שלם, והבת הגדולה אמרה שהיא אוהבת את הריח.",
   "In the first winter it rained a whole week, and my eldest daughter said she liked the smell."),
  ("אני עדיין מתגעגע לעיר ההיא לפעמים, אבל אף אחד מאיתנו לא הציע לחזור.",
   "I still miss that city sometimes, but none of us has suggested going back."),
 ]),
]


def has_past(lex, sentence):
    """Does this sentence carry a past-tense verb? Asked of the lexicon, not of a suffix."""
    for t in he_ingest.tokenize(sentence):
        rows = lex.by_form.get(he_norm(t)) or []
        if not rows:
            continue
        kinds = {str(r['ANALYSIS'] or '') for r in rows}
        # Every reading a verb, at least one of them past. "Any reading past" counts בֹּקֶר,
        # which shares a skeleton with a past-tense form and is a noun in every story here.
        if all(k.startswith('VERB') for k in kinds) and any('past' in k for k in kinds):
            return True
    return False


def finite_verbs(lex, sentence):
    """How many conjugated verbs this sentence carries -- its clause count, near enough.

    What makes a sentence advanced is not its length, it is that it holds two thoughts at once:
    "the letter he wrote and never sent", "I left sure I had failed". Beginner Hebrew is a
    chain of one-verb sentences; advanced Hebrew hangs clauses off each other.

    The first version of this counted subordinating CONJUNCTIONS from a word list and measured
    the wrong thing in both directions -- it scored a story of relative clauses at 29% because
    they hang off a bare ש-, and one of plain "and then" sentences at 71% because they happened
    to contain כי. Counting the verbs asks the question directly.

    Same all-readings-are-verbs strictness as has_past, and for the same reason: מת, כתב and
    שלח are each also a noun. Two adjustments, both for false NEGATIVES rather than to be
    lenient. It asks look() rather than the form table, so a verb the lexicon reaches by its
    other spelling counts (בישלתי is only there as a ktiv match). And it ignores a NOUN row in
    the possessed form, which is a Wiktionary artefact that collides exactly with the
    first-person past: החלטתי, הרגשתי and חזרתי each carry "my decision", "my feeling", "my
    return" beside the verb, and without this every such sentence read as verbless.

    Measured over what this app already has: two finite verbs in 3% of beginner sentences,
    38% of intermediate, 36% of the Ben-Yehuda shelf and 74% of the daily paper."""
    n = 0
    for t in he_ingest.tokenize(sentence):
        recs, _prov, cut = lex.look(t)
        if not recs or cut:
            continue
        kinds = {str(r['ANALYSIS'] or '') for r in recs}
        kinds = {k for k in kinds if not (k.startswith('NOUN') and 'possessed-form' in k)}
        if kinds and all(k.startswith('VERB') for k in kinds) and any(
                any(f in k for f in FINITE) for k in kinds):
            n += 1
    return n


def fresh_lemmas(lex, toks, known):
    """Share of a story's DISTINCT lemmas that this app's Hebrew has not used before.

    Counted per lemma rather than per token on purpose: a story that says one new word forty
    times has taught one word, and by token it would look like a whole new vocabulary."""
    lem = set()
    for t in toks:
        recs, _prov, _cut = lex.look(t)
        if recs:
            lem.add(str(lex.readings(recs)[0]['LEMMA']))
    if not lem:
        return 0.0
    return sum(1 for x in lem if x not in known) / len(lem)


def met_before(lex, toks, known):
    """Share of a story's words whose lemma the reader has already met in this app."""
    lem = []
    for t in toks:
        recs, prov, _ = lex.look(t)
        if recs:
            lem.append(str(lex.readings(recs)[0]['LEMMA']))
    if not lem:
        return 1.0
    return sum(1 for x in lem if x in known) / len(lem)


def check(lex, level, sents, known):
    """-> (list of problems, stats). A story that has problems is not written."""
    L = LEVELS[level]
    toks = [t for he, _ in sents for t in he_ingest.tokenize(he)]
    unknown = sorted({t for t in toks if lex.look(t)[1] == 'unresolved'})
    arch = [t for t in toks if t in ARCHAIC]
    vav = vav_consecutives(lex, toks)
    lengths = [len(he_ingest.tokenize(he)) for he, _ in sents]
    avg = statistics.mean(lengths)
    past = sum(1 for he, _ in sents if has_past(lex, he)) / len(sents)
    reach = met_before(lex, toks, known)
    sub = sum(1 for he, _ in sents if finite_verbs(lex, he) >= 2) / len(sents)
    fresh = fresh_lemmas(lex, toks, known)
    bad = []
    if len(unknown) > MAX_UNKNOWN:
        bad.append('not in the lexicon: ' + ', '.join(unknown))
    if arch:
        bad.append('literary register: ' + ', '.join(sorted(set(arch))))
    if vav:
        bad.append('vav-consecutive: ' + ', '.join(sorted(set(vav))))
    if avg > L['max_sentence']:
        bad.append('sentences average %.1f words (max %.0f)' % (avg, L['max_sentence']))
    # A floor as well as a ceiling. "Intermediate" is a claim about being harder than the tier
    # below it, and a story that drifts back to beginner length is not one however it is filed.
    if avg < L['min_sentence']:
        bad.append('sentences average %.1f words (min %.0f for this level)'
                   % (avg, L['min_sentence']))
    if past < L['min_past']:
        bad.append('only %.0f%% of sentences are in the past (needs %.0f%%)'
                   % (100 * past, 100 * L['min_past']))
    if reach < L['min_reach']:
        bad.append('%.0f%% of its words have been met before (needs %.0f%%)'
                   % (100 * reach, 100 * L['min_reach']))
    if sub < L['min_sub']:
        bad.append('only %.0f%% of sentences carry two clauses (needs %.0f%%; intermediate '
                   'runs 31%%)' % (100 * sub, 100 * L['min_sub']))
    if fresh < L['min_fresh']:
        bad.append('only %.0f%% of its lemmas are new to this app (needs %.0f%%)'
                   % (100 * fresh, 100 * L['min_fresh']))
    return bad, {'tokens': len(toks), 'avg': avg, 'longest': max(lengths),
                 'past': past, 'reach': reach, 'sub': sub, 'fresh': fresh}


def already_met(lex):
    """Every lemma the app's Hebrew has already used -- the beginner stories, the news, the
    shelf. What "already met" means for a graded reader, read off the content rather than
    asserted by whoever wrote the story."""
    known = set()
    for f in glob.glob(paths.build('*', 'text.json')):
        d = json.load(open(f, encoding='utf-8'))
        for s in d['sentences']:
            for w in s['words']:
                if w.get('lemma'):
                    known.add(w['lemma'])
    return known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='write texts/he/story-*-NN.json')
    ap.add_argument('--level', choices=sorted(LEVELS), help='just one tier')
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()

    lex = Lexicon()
    known = already_met(lex)
    print('%d lemmas already met in this app\'s Hebrew\n' % len(known))
    problems = 0
    for level in sorted(LEVELS):
        if a.level and level != a.level:
            continue
        print('%s' % level.upper())
        print('  %-22s %-24s %5s %6s %5s %5s %5s %5s %5s'
              % ('title', 'English', 'words', 'avg', 'max', 'past', 'met', 'sub', 'new'))
        for t_he, t_en, sents in STORIES.get(level, []):
            bad, st = check(lex, level, sents, known)
            print('  %-22s %-24s %5d %6.1f %5d %4.0f%% %4.0f%% %4.0f%% %4.0f%%%s'
                  % (t_he[:22], t_en[:24], st['tokens'], st['avg'], st['longest'],
                     100 * st['past'], 100 * st['reach'], 100 * st['sub'], 100 * st['fresh'],
                     '' if not bad else '  !!'))
            for b in bad:
                print('       !! %s' % b)
                problems += 1
        print()
    if problems:
        print('%d problems — nothing written. A story the reader cannot tap every word of, '
              'that reads like scripture, or that is not the level it claims, is not one of '
              'these.' % problems)
        return 1
    if not a.write:
        print('all clear. --write to emit them.')
        return 0
    n = 0
    for level in sorted(LEVELS):
        if a.level and level != a.level:
            continue
        for i, (t_he, t_en, sents) in enumerate(STORIES.get(level, []), 1):
            sid = 'story-%s-%02d' % (LEVELS[level]['sid'], i)
            json.dump({'id': sid, 'kind': 'story', 'level': level,
                       'title': {'ar': t_he, 'en': t_en},
                       'dialect': 'he', 'subdialect': None, 'source': SRC % level,
                       'sentences': [{'ar': h, 'en': e} for h, e in sents]},
                      open(paths.texts(sid + '.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            n += 1
    print('wrote %d stories -> %s' % (n, os.path.relpath(paths.texts(''), paths.ROOT)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
