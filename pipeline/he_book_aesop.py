#!/usr/bin/env python3
"""משלי איזופוס — thirty fables retold in modern Hebrew, graded to beginner.

The Hebrew twin of pipeline/book_aesop.py, fable for fable, so the two shelves are one shelf in
two languages. Aesop is ancient and anonymous in any practical sense — public domain by age,
with no edition being translated. These are retellings from the traditional plots.

WHY AESOP OPENS THE HEBREW SHELF TOO. The plots are known in English, so nothing is spent
working out what happens and all of the attention goes to the Hebrew. And a fable is the one
narrative shape that fits inside beginner sentences honestly: a setup, a turn, a line at the
end, none of which needs a subordinate clause.

Written to what he_bookshelf.py measures: present-tense narration where Hebrew prefers it,
past where the story turns, one clause a sentence, and a small recurring cast — שועל, אריה,
זאב, עורב, עכבר — so the same words come back fable after fable.

Deliberately unpointed. The vowels are looked up at ingest, never typed here.

Run:  python3 pipeline/he_book_aesop.py --lang he            # check
      python3 pipeline/he_book_aesop.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': "Aesop's Fables", 'author': 'Aesop (traditional)', 'year': 'c. 600 BCE',
        'status': 'public domain — ancient, anonymous'}

# (english title, hebrew title, [paragraph, ...])
CHAPTERS = [
 ('The Oak and the Reed', 'האלון והקנה', [
  P(('אלון גדול צחק על הקנה.', 'A big oak laughed at the reed.'),
    ('הוא אמר לו: אתה חלש ואתה מתכופף.', 'He said to him: you are weak and you bend.')),
  P(('הקנה אמר: אני מתכופף ואני נשאר.', 'The reed said: I bend and I stay.')),
  P(('בלילה הגיעה סופה חזקה.', 'At night a strong storm came.'),
    ('האלון נפל והקנה נשאר.', 'The oak fell and the reed stayed.'),
    ('מי שמתכופף לא נשבר.', 'The one who bends does not break.'))]),

 ('The Fox and the Grapes', 'השועל והענבים', [
  P(('שועל ראה ענבים גבוהים.', 'A fox saw some grapes up high.'),
    ('הענבים היו גדולים ויפים.', 'The grapes were big and beautiful.')),
  P(('הוא קפץ פעם, פעמיים ושלוש.', 'He jumped once, twice and three times.'),
    ('הוא לא הגיע.', "He didn't reach them.")),
  P(('הוא הלך ואמר: הענבים חמוצים.', 'He walked off and said: the grapes are sour.'),
    ('מה שאדם לא מקבל, הוא לא אוהב.', 'What a person cannot get, he decides he does not want.'))]),

 ('The Tortoise and the Hare', 'הצב והארנב', [
  P(('הארנב צחק על הצב.', 'The hare laughed at the tortoise.'),
    ('הוא אמר לו: אתה איטי מאוד.', 'He said to him: you are very slow.'),
    ('הצב אמר: בוא נעשה מרוץ.', 'The tortoise said: come, let us have a race.')),
  P(('הארנב רץ מהר והיה רחוק מאוד.', 'The hare ran fast and was far ahead.'),
    ('אחר כך הוא ישן מתחת לעץ.', 'Afterwards he slept under a tree.')),
  P(('הצב הלך ולא עצר.', 'The tortoise walked and did not stop.'),
    ('הוא הגיע לפניו.', 'He arrived before him.'),
    ('האיטי שלא עוצר מגיע.', 'The slow one who never stops arrives.'))]),

 ('The Lion and the Mouse', 'האריה והעכבר', [
  P(('עכבר קטן הלך על אריה ישן.', 'A small mouse walked on a sleeping lion.'),
    ('האריה התעורר ותפס אותו.', 'The lion woke up and caught him.')),
  P(('העכבר ביקש: תעזוב אותי ואני אעזור לך.', 'The mouse asked: let me go and I will help you.'),
    ('האריה צחק ועזב אותו.', 'The lion laughed and let him go.')),
  P(('אחרי חודש האריה נפל ברשת.', 'A month later the lion fell into a net.'),
    ('העכבר בא וכרסם את החבלים.', 'The mouse came and gnawed through the ropes.'),
    ('גם הקטן יכול לעזור לגדול.', 'Even the small can help the great.'))]),

 ('The Fox and the Stork', 'השועל והחסידה', [
  P(('השועל הזמין את החסידה לארוחה.', 'The fox invited the stork to a meal.'),
    ('הוא שם את המרק בצלחת שטוחה.', 'He put the soup in a flat dish.'),
    ('החסידה לא הצליחה לאכול.', 'The stork could not manage to eat.')),
  P(('אחר כך היא הזמינה אותו אליה.', 'Afterwards she invited him to her place.'),
    ('היא שמה את האוכל בכד צר וגבוה.', 'She put the food in a narrow, tall jug.')),
  P(('השועל הריח ולא אכל כלום.', 'The fox smelled it and ate nothing.'),
    ('מה שאתה עושה, יעשו גם לך.', 'What you do will be done to you.'))]),

 ('The Fisherman and the Little Fish', 'הדייג והדג הקטן', [
  P(('דייג תפס דג קטן מאוד.', 'A fisherman caught a very small fish.'),
    ('הדג ביקש: תחזיר אותי למים.', 'The fish asked: put me back in the water.')),
  P(('הוא אמר: אני אגדל ואז אהיה דג גדול.', 'He said: I will grow and then I will be a big fish.'),
    ('הדייג הסתכל עליו וחשב.', 'The fisherman looked at him and thought.')),
  P(('הוא אמר: דג קטן ביד עדיף.', 'He said: a small fish in the hand is better.'),
    ('מה שיש עכשיו שווה יותר.', 'What you have now is worth more.'))]),

 ('The Dove and the Ant', 'היונה והנמלה', [
  P(('נמלה נפלה לתוך הנהר.', 'An ant fell into the river.'),
    ('יונה ראתה אותה מהעץ.', 'A dove saw her from the tree.')),
  P(('היונה זרקה לה עלה גדול.', 'The dove threw her a big leaf.'),
    ('הנמלה עלתה על העלה ויצאה.', 'The ant climbed onto the leaf and got out.')),
  P(('אחר כך צייד בא עם רשת.', 'Afterwards a hunter came with a net.'),
    ('הנמלה נשכה את הרגל שלו.', 'The ant bit his foot.'),
    ('היונה שמעה וברחה.', 'The dove heard and flew away.'),
    ('טובה קטנה חוזרת.', 'A small kindness comes back.'))]),

 ('The Stag at the Pool', 'האייל ליד הבריכה', [
  P(('אייל שתה מים והסתכל על עצמו.', 'A stag drank water and looked at himself.'),
    ('הוא אהב את הקרניים היפות שלו.', 'He liked his beautiful antlers.'),
    ('הוא לא אהב את הרגליים הדקות.', 'He did not like his thin legs.')),
  P(('פתאום כלבים רצו אחריו.', 'Suddenly dogs ran after him.'),
    ('הרגליים הדקות הצילו אותו.', 'His thin legs saved him.')),
  P(('הקרניים נתפסו בין העצים.', 'The antlers got caught between the trees.'),
    ('מה שיפה לא תמיד עוזר.', 'What is beautiful does not always help.'))]),

 ('The Peacock and the Crane', 'הטווס והעגור', [
  P(('הטווס הראה את הנוצות שלו.', 'The peacock showed off his feathers.'),
    ('הוא אמר לעגור: אתה אפור ופשוט.', 'He said to the crane: you are grey and plain.')),
  P(('העגור לא כעס ולא ענה.', 'The crane did not get angry and did not answer.'),
    ('הוא פתח כנפיים ועף גבוה.', 'He opened his wings and flew up high.')),
  P(('הטווס נשאר על האדמה.', 'The peacock stayed on the ground.'),
    ('נוצות יפות בלי כוח לא מרימות אותך.', 'Beautiful feathers without strength do not lift you.'))]),

 ('The Wolf and the Crane', 'הזאב והעגור', [
  P(('עצם נתקעה בגרון של הזאב.', 'A bone got stuck in the wolf’s throat.'),
    ('הוא ביקש עזרה מהעגור.', 'He asked the crane for help.')),
  P(('העגור הכניס את הראש והוציא את העצם.', 'The crane put his head in and pulled the bone out.'),
    ('אחר כך הוא ביקש תשלום.', 'Afterwards he asked for payment.')),
  P(('הזאב אמר: היית בפה שלי ויצאת.', 'The wolf said: you were in my mouth and you came out.'),
    ('זה כל התשלום שלך.', 'That is all the payment you get.'))]),

 ('The Town Mouse and the Country Mouse', 'עכבר העיר ועכבר הכפר', [
  P(('עכבר מהעיר בא לבקר בכפר.', 'A mouse from the city came to visit the country.'),
    ('הוא אכל לחם יבש וזרעים.', 'He ate dry bread and seeds.'),
    ('הוא אמר: בוא איתי לעיר.', 'He said: come with me to the city.')),
  P(('בעיר היה אוכל טוב על השולחן.', 'In the city there was good food on the table.'),
    ('היו גבינה, בשר ועוגה.', 'There were cheese, meat and cake.')),
  P(('פתאום נכנס כלב גדול.', 'Suddenly a big dog came in.'),
    ('שני העכברים ברחו מהר.', 'The two mice ran away fast.'),
    ('לחם בשקט טוב מבשר בפחד.', 'Bread in quiet is better than meat in fear.'))]),

 ('The Boastful Traveller', 'המטייל שהתפאר', [
  P(('אדם חזר מטיול ארוך וסיפר.', 'A man came back from a long trip and told stories.'),
    ('הוא אמר: קפצתי קפיצה ענקית באי.', 'He said: I made a huge jump on the island.')),
  P(('הוא אמר: כל האנשים שם ראו אותי.', 'He said: everyone there saw me.'),
    ('חבר אחד הסתכל עליו ושתק.', 'One friend looked at him and said nothing.')),
  P(('אחר כך החבר אמר: תקפוץ פה.', 'Afterwards the friend said: jump here.'),
    ('מי שעושה לא צריך לספר.', 'The one who does it does not need to tell it.'))]),

 ('The Frog and the Ox', 'הצפרדע והשור', [
  P(('צפרדע ראתה שור גדול בשדה.', 'A frog saw a big ox in the field.'),
    ('היא רצתה להיות גדולה כמו השור.', 'She wanted to be as big as the ox.')),
  P(('היא נשמה והתנפחה קצת.', 'She breathed in and puffed up a bit.'),
    ('הילדים שלה אמרו: השור עוד יותר גדול.', 'Her children said: the ox is even bigger.')),
  P(('היא נשמה שוב והתנפחה חזק.', 'She breathed in again and puffed up hard.'),
    ('בסוף היא התפוצצה.', 'In the end she burst.'),
    ('מי שרוצה להיות אחר מפסיד את עצמו.', 'Whoever wants to be someone else loses himself.'))]),

 ('The Farmer and the Snake', 'האיכר והנחש', [
  P(('איכר מצא נחש קפוא בשלג.', 'A farmer found a snake frozen in the snow.'),
    ('הוא לקח אותו ושם אותו ליד האש.', 'He took it and put it by the fire.')),
  P(('הנחש התחמם והתעורר.', 'The snake warmed up and woke.'),
    ('הוא נשך את היד שעזרה לו.', 'It bit the hand that helped it.')),
  P(('האיכר אמר: רחמתי על נחש.', 'The farmer said: I took pity on a snake.'),
    ('טבע רע לא משתנה מחום.', 'A bad nature is not changed by warmth.'))]),

 ("The Ass and His Masters", 'החמור והבעלים שלו', [
  P(('חמור עבד אצל גנן וביקש בעלים אחר.', 'A donkey worked for a gardener and asked for another owner.'),
    ('הוא עבר לעבוד אצל יוצר כדים.', 'He went to work for a potter.')),
  P(('שם המשא היה כבד יותר.', 'There the load was heavier.'),
    ('הוא ביקש שוב לעבור.', 'He asked to move again.')),
  P(('הבעלים החדש היה קשה מכולם.', 'The new owner was the hardest of all.'),
    ('מי שתמיד בורח מוצא גרוע יותר.', 'Whoever always runs finds worse.'))]),

 ('The Goose and the Golden Eggs', 'האווז וביצי הזהב', [
  P(('לאיש היה אווז מיוחד.', 'A man had a special goose.'),
    ('כל בוקר האווז הטיל ביצת זהב.', 'Every morning the goose laid a golden egg.')),
  P(('האיש רצה את כל הזהב מיד.', 'The man wanted all the gold at once.'),
    ('הוא חשב שיש אוצר בפנים.', 'He thought there was a treasure inside.')),
  P(('הוא הרג את האווז ולא מצא כלום.', 'He killed the goose and found nothing.'),
    ('מי שרוצה הכול מאבד גם את המעט.', 'Whoever wants everything loses the little too.'))]),

 ('The Dog and His Reflection', 'הכלב והבבואה', [
  P(('כלב לקח עצם והלך הביתה.', 'A dog took a bone and walked home.'),
    ('בדרך הוא עבר על גשר.', 'On the way he crossed a bridge.')),
  P(('הוא הסתכל במים וראה כלב אחר.', 'He looked in the water and saw another dog.'),
    ('לכלב הזה הייתה עצם גדולה יותר.', 'That dog had a bigger bone.')),
  P(('הוא פתח את הפה ונבח עליו.', 'He opened his mouth and barked at him.'),
    ('העצם נפלה למים ונעלמה.', 'The bone fell into the water and disappeared.'),
    ('מי שרודף אחרי צל מאבד את היש.', 'Whoever chases a shadow loses what is there.'))]),

 ('The Old Man and Death', 'הזקן והמוות', [
  P(('זקן נשא עצים כבדים בדרך.', 'An old man carried heavy wood along the road.'),
    ('הוא היה עייף והניח את העצים.', 'He was tired and put the wood down.')),
  P(('הוא אמר: שהמוות יבוא כבר.', 'He said: let death come already.'),
    ('פתאום המוות עמד לידו.', 'Suddenly death stood beside him.')),
  P(('הזקן אמר: רק תרים לי את העצים.', 'The old man said: just lift the wood for me.'),
    ('אנשים מבקשים מה שהם לא רוצים.', 'People ask for what they do not want.'))]),

 ('The Two Travellers and the Bear', 'שני המטיילים והדוב', [
  P(('שני חברים הלכו ביער.', 'Two friends walked in the forest.'),
    ('פתאום דוב גדול יצא מבין העצים.', 'Suddenly a big bear came out from between the trees.')),
  P(('אחד עלה מהר על עץ.', 'One climbed a tree fast.'),
    ('השני שכב על האדמה ולא זז.', 'The other lay on the ground and did not move.')),
  P(('הדוב הריח אותו והלך.', 'The bear smelled him and left.'),
    ('החבר ירד ושאל מה הדוב אמר.', 'The friend came down and asked what the bear said.'),
    ('הוא ענה: אל תלך עם מי שבורח.', 'He answered: do not travel with someone who runs.'))]),

 ('The Crow and the Pitcher', 'העורב והכד', [
  P(('עורב צמא חיפש מים.', 'A thirsty crow looked for water.'),
    ('הוא מצא כד עם מעט מים.', 'He found a jug with a little water.')),
  P(('המים היו נמוכים והמקור לא הגיע.', 'The water was low and his beak did not reach.'),
    ('הוא חשב רגע.', 'He thought for a moment.')),
  P(('הוא הביא אבנים קטנות והכניס אותן.', 'He brought small stones and put them in.'),
    ('המים עלו והוא שתה.', 'The water rose and he drank.'),
    ('ראש טוב עדיף על כוח.', 'A good head is better than strength.'))]),

 ('The Bundle of Sticks', 'צרור המקלות', [
  P(('לאב היו בנים שרבו כל היום.', 'A father had sons who quarrelled all day.'),
    ('הוא הביא צרור מקלות וקשר אותו.', 'He brought a bundle of sticks and tied it.')),
  P(('כל בן ניסה לשבור את הצרור.', 'Each son tried to break the bundle.'),
    ('אף אחד לא הצליח.', 'None of them managed.')),
  P(('האב פתח את הצרור ונתן מקל לכל אחד.', 'The father untied it and gave each one a stick.'),
    ('כולם שברו מיד.', 'They all broke theirs at once.'))]),

 ('Belling the Cat', 'הפעמון על החתול', [
  P(('העכברים פחדו מהחתול של הבית.', 'The mice were afraid of the house cat.'),
    ('הם התאספו כדי לחשוב יחד.', 'They gathered to think together.')),
  P(('עכבר צעיר אמר: נשים עליו פעמון.', 'A young mouse said: we will put a bell on him.'),
    ('כולם שמחו מאוד ואמרו כן.', 'They were all delighted and said yes.')),
  P(('עכבר זקן שאל: מי ישים אותו.', 'An old mouse asked: who will put it on.'),
    ('בחדר נהיה שקט.', 'The room went quiet.'),
    ('קל להציע וקשה לעשות.', 'It is easy to suggest and hard to do.'))]),

 ('The Fox and the Crow', 'השועל והעורב', [
  P(('עורב ישב על ענף עם גבינה.', 'A crow sat on a branch with cheese.'),
    ('שועל עמד למטה והסתכל.', 'A fox stood below and looked.')),
  P(('השועל אמר: אתה הציפור הכי יפה.', 'The fox said: you are the most beautiful bird.'),
    ('הוא אמר: בטח יש לך גם קול יפה.', 'He said: surely you have a beautiful voice too.')),
  P(('העורב פתח את הפה ושר.', 'The crow opened his mouth and sang.'),
    ('הגבינה נפלה והשועל לקח אותה.', 'The cheese fell and the fox took it.'),
    ('מי שאוהב מחמאות משלם עליהן.', 'Whoever loves compliments pays for them.'))]),

 ("The Donkey in the Lion's Skin", 'החמור בעור האריה', [
  P(('חמור מצא עור של אריה בשדה.', 'A donkey found a lion’s skin in the field.'),
    ('הוא לבש אותו והלך בין הכפרים.', 'He put it on and walked between the villages.')),
  P(('כל החיות ברחו ממנו בפחד.', 'All the animals ran from him in fear.'),
    ('החמור שמח מאוד.', 'The donkey was very pleased.')),
  P(('הוא פתח את הפה ונער.', 'He opened his mouth and brayed.'),
    ('כולם הבינו מיד מי הוא.', 'They all understood at once who he was.'))]),

 ("The Wolf in Sheep's Clothing", 'הזאב בעור הכבש', [
  P(('זאב רצה להיכנס לעדר.', 'A wolf wanted to get into the flock.'),
    ('הוא מצא עור של כבשה ולבש אותו.', 'He found a sheepskin and put it on.')),
  P(('הרועה לא ראה אותו והוא נכנס.', 'The shepherd did not see him and he got in.'),
    ('בלילה הרועה חיפש בשר לארוחה.', 'At night the shepherd looked for meat for a meal.')),
  P(('הוא לקח את הכבשה הראשונה.', 'He took the first sheep.'),
    ('השקר עבד עד הסוף.', 'The lie worked right to the end.'))]),

 ('The Boy Who Cried Wolf', 'הילד שצעק זאב', [
  P(('ילד שמר על הכבשים ליד ההר.', 'A boy watched the sheep near the hill.'),
    ('היה לו משעמם והוא צעק זאב.', 'He was bored and shouted wolf.')),
  P(('כל הכפר רץ אליו עם מקלות.', 'The whole village ran to him with sticks.'),
    ('הילד צחק ואמר שאין זאב.', 'The boy laughed and said there was no wolf.')),
  P(('אחרי שבוע זאב אמיתי בא.', 'A week later a real wolf came.'),
    ('הילד צעק וצעק ואף אחד לא בא.', 'The boy shouted and shouted and nobody came.'),
    ('מי שמשקר פעמיים לא מאמינים לו.', 'Whoever lies twice is not believed.'))]),

 ('The Milkmaid and Her Pail', 'הנערה ודלי החלב', [
  P(('נערה הלכה לשוק עם דלי חלב.', 'A girl walked to the market with a pail of milk.'),
    ('היא נשאה אותו על הראש.', 'She carried it on her head.')),
  P(('היא חשבה: אקנה ביצים מהכסף.', 'She thought: I will buy eggs with the money.'),
    ('היא חשבה: מהביצים יהיו תרנגולות.', 'She thought: from the eggs there will be chickens.'),
    ('היא חשבה: אקנה שמלה חדשה.', 'She thought: I will buy a new dress.')),
  P(('היא רקדה קצת מרוב שמחה.', 'She danced a little from joy.'),
    ('הדלי נפל והחלב נשפך.', 'The pail fell and the milk spilled.'),
    ('אל תספור לפני שיש לך.', 'Do not count before you have it.'))]),

 ('The Ant and the Grasshopper', 'הנמלה והחגב', [
  P(('בקיץ הנמלה עבדה כל היום.', 'In summer the ant worked all day.'),
    ('היא אספה זרעים והכניסה אותם הביתה.', 'She gathered seeds and took them home.')),
  P(('החגב שר וניגן בשמש.', 'The grasshopper sang and played in the sun.'),
    ('הוא אמר לה: יש עוד זמן.', 'He said to her: there is still time.')),
  P(('בחורף ירד גשם והיה קר.', 'In winter it rained and it was cold.'),
    ('החגב היה רעב ובא לבקש.', 'The grasshopper was hungry and came to ask.'),
    ('הנמלה אמרה: בקיץ שרת.', 'The ant said: in summer you sang.'))]),

 ('The Wind and the Sun', 'הרוח והשמש', [
  P(('הרוח והשמש רבו מי חזק יותר.', 'The wind and the sun argued over who was stronger.'),
    ('הם ראו אדם עם מעיל בדרך.', 'They saw a man with a coat on the road.'),
    ('הם אמרו: מי שיוריד את המעיל.', 'They said: whoever gets the coat off.')),
  P(('הרוח נשבה חזק מאוד.', 'The wind blew very hard.'),
    ('האיש החזיק את המעיל חזק.', 'The man held the coat tight.'),
    ('הרוח נשבה עוד והוא סגר אותו.', 'The wind blew more and he closed it.')),
  P(('אחר כך השמש חיממה לאט.', 'Afterwards the sun warmed slowly.'),
    ('האיש הוריד את המעיל לבד.', 'The man took the coat off by himself.'),
    ('רוך עושה מה שכוח לא עושה.', 'Gentleness does what force cannot.'))]),

 ('The Miser and His Gold', 'הקמצן והזהב', [
  P(('אדם עשיר קבר זהב מתחת לעץ.', 'A rich man buried gold under a tree.'),
    ('כל יום הוא בא והסתכל עליו.', 'Every day he came and looked at it.')),
  P(('שכן ראה אותו ולקח את הזהב.', 'A neighbour saw him and took the gold.'),
    ('האיש בכה ליד הבור הריק.', 'The man cried beside the empty hole.')),
  P(('השכן אמר: תשים אבן בבור.', 'The neighbour said: put a stone in the hole.'),
    ('הוא אמר: לא השתמשת בזהב בכלל.', 'He said: you never used the gold at all.'),
    ('מה שלא משתמשים בו שווה אבן.', 'What is never used is worth a stone.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('aesop', {'en': "Aesop's Fables", 'he': 'משלי איזופוס'}, 'beginner',
                          CHAPTERS, unit='Fable', unit_he='משל', shelf=2, meta=META))
