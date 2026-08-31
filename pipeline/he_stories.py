#!/usr/bin/env python3
"""Graded short stories in spoken Israeli Hebrew -> texts/he/story-{beg,int}-NN.json.

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
# tier -> (id prefix, max average sentence, minimum share of sentences carrying a past-tense
# verb, minimum share of lemmas already met elsewhere in the app's Hebrew)
LEVELS = {
    'beginner':     {'sid': 'beg', 'min_sentence': 0.0, 'max_sentence': 9.0,
                     'min_past': 0.0, 'min_reach': 0.0},
    'intermediate': {'sid': 'int', 'min_sentence': 7.0, 'max_sentence': 14.0,
                     'min_past': 0.5, 'min_reach': 0.7},
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
    return bad, {'tokens': len(toks), 'avg': avg, 'longest': max(lengths),
                 'past': past, 'reach': reach}


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
        print('  %-22s %-24s %5s %6s %5s %5s %5s'
              % ('title', 'English', 'words', 'avg', 'max', 'past', 'met'))
        for t_he, t_en, sents in STORIES.get(level, []):
            bad, st = check(lex, level, sents, known)
            print('  %-22s %-24s %5d %6.1f %5d %4.0f%% %4.0f%%%s'
                  % (t_he[:22], t_en[:24], st['tokens'], st['avg'], st['longest'],
                     100 * st['past'], 100 * st['reach'], '' if not bad else '  !!'))
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
