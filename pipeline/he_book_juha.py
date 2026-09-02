#!/usr/bin/env python3
"""ג'וחא — forty folk tales retold in modern Hebrew, graded to beginner.

The Hebrew twin of pipeline/book_juha.py, tale for tale. Juha — Nasreddin, ג'וחא — is the wise
fool of the whole eastern Mediterranean, and he crossed into Hebrew a long time before this
app: the tales are told in Israel too, and the joke lands in either language because it is
never in the words.

WHY HE OPENS THIS SHELF AS WELL. A Juha tale is three sentences of setup and one that turns,
which is exactly the shape a beginner can hold. And it is entirely dialogue and everyday
objects — a donkey, a pot, a door, a neighbour who borrows — so the vocabulary is the
vocabulary of the street rather than of literature.

Deliberately unpointed. The vowels are looked up at ingest, never typed here. ג'וחא himself has
no lexical entry in any language and is declared in pipeline/he_curated.py, where the pointing
and the gloss are written down once.

Run:  python3 pipeline/he_book_juha.py --lang he            # check
      python3 pipeline/he_book_juha.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'the Juha / Nasreddin folk tales', 'author': 'traditional', 'year': 'medieval',
        'status': 'public domain — folk material, no known author'}

CHAPTERS = [
 ('The Donkey and the Neighbour', 'החמור והשכן', [
  P(("לג'וחא היה חמור קטן.", 'Juha had a small donkey.'),
    ('השכן בא ואמר: אני רוצה את החמור היום.', 'The neighbour came and said: I want the donkey today.')),
  P(("ג'וחא לא רצה לתת לו אותו.", "Juha didn't want to give it to him."),
    ('הוא אמר: החמור לא פה, הוא הלך לשוק.', 'He said: the donkey is not here, it went to the market.')),
  P(('באותו רגע החמור נער מאחורי הבית.', 'At that moment the donkey brayed from behind the house.'),
    ('השכן אמר: אבל אני שומע את החמור.', 'The neighbour said: but I hear the donkey!'),
    ("ג'וחא אמר: אתה מאמין לחמור או לי?", 'Juha said: do you believe the donkey or me?'))]),

 ('The Coat at the Feast', 'המעיל בסעודה', [
  P(("ג'וחא הלך לסעודה בבגדים ישנים.", 'Juha went to a feast in old clothes.'),
    ('אף אחד לא אמר שלום ואף אחד לא הושיב אותו.', 'Nobody greeted him and nobody seated him.')),
  P(('הוא הלך הביתה ולבש מעיל חדש ויפה.', 'He went home and put on a new, handsome coat.'),
    ('הוא חזר לסעודה וכולם קמו לכבודו.', 'He came back to the feast and everyone stood up for him.'),
    ('הם הושיבו אותו בראש ושמו לפניו אוכל.', 'They seated him at the head and put food in front of him.')),
  P(('הוא שם את השרוול בצלחת ואמר: תאכל, מעיל.', 'He put the sleeve in the plate and said: eat, coat.'),
    ('שאלו אותו: מה אתה עושה?', 'They asked him: what are you doing?'),
    ('הוא אמר: האוכל למעיל, לא לי.', 'He said: the food is for the coat, not for me.'))]),

 ('The Pot That Gave Birth', 'הסיר שילד', [
  P(("ג'וחא לקח סיר גדול מהשכן.", 'Juha borrowed a big pot from the neighbour.'),
    ('כשהוא החזיר אותו, הוא שם בתוכו סיר קטן.', 'When he returned it, he put a small pot inside it.')),
  P(('השכן שאל: מה זה הקטן הזה?', 'The neighbour asked: what is this small one?'),
    ("ג'וחא אמר: הסיר שלך ילד.", 'Juha said: your pot gave birth.'),
    ('השכן שמח ולקח את שניהם.', 'The neighbour was happy and took both.')),
  P(('אחרי שבוע הוא לקח את הסיר שוב.', 'A week later he borrowed the pot again.'),
    ('הפעם הוא לא החזיר אותו.', 'This time he did not return it.'),
    ('השכן שאל עליו והוא אמר: הוא מת.', 'The neighbour asked about it and he said: it died.'),
    ('השכן אמר: סיר לא מת.', 'The neighbour said: a pot does not die!'),
    ("ג'וחא אמר: האמנת שהוא יולד.", 'Juha said: you believed that it gives birth.'),
    ('ואתה לא מאמין שהוא מת?', 'And you do not believe that it dies?'))]),

 ('The Smell of the Food', 'הריח של האוכל', [
  P(('איש עני ישב ליד חנות אוכל.', 'A poor man sat next to a food shop.'),
    ('הוא אכל לחם יבש והריח את הריח.', 'He ate dry bread and smelled the smell.')),
  P(('בעל החנות ביקש ממנו כסף.', 'The shop owner asked him for money.'),
    ('הוא אמר: הרחת את האוכל שלי, תשלם.', 'He said: you smelled my food, pay up.'),
    ("הם הלכו לג'וחא, כי הוא היה שופט.", 'They went to Juha, because he was a judge.')),
  P(("ג'וחא לקח שקית כסף ועשה בה רעש.", 'Juha took a bag of money and made a noise with it.'),
    ('הוא שאל אותו: שמעת את הקול של הכסף?', 'He asked him: did you hear the sound of the money?'),
    ('הוא אמר: שמעתי.', 'He said: I heard it.'),
    ("ג'וחא אמר: הקול משלם על הריח.", 'Juha said: the sound pays for the smell.'))]),

 ('Riding to Market', 'בדרך לשוק', [
  P(("ג'וחא והבן שלו הלכו לשוק עם החמור.", 'Juha and his son went to the market with the donkey.'),
    ("ג'וחא רכב והילד הלך.", 'Juha rode and the boy walked.')),
  P(('אנשים בדרך אמרו: תראו, האבא רוכב.', 'People on the road said: look, the father is riding.'),
    ('והבן שלו הולך ועייף.', 'And his son walks and is tired.'),
    ("ג'וחא ירד והושיב את הבן.", 'Juha got down and sat the boy on.')),
  P(('אנשים אחרים אמרו: תראו, הילד רוכב.', 'Other people said: look, the boy is riding.'),
    ('והאבא שלו זקן והולך.', 'And his father is old and walking.'),
    ('אז שניהם רכבו יחד.', 'So the two of them rode together.'),
    ('ואנשים אחרים אמרו: מסכן, החמור עייף.', 'And other people said: poor thing, the donkey is tired.')),
  P(('בסוף שניהם ירדו והלכו.', 'In the end they both got down and walked.'),
    ("ג'וחא אמר לבן: מה שלא תעשה, ידברו.", 'Juha said to his son: whatever you do, people will talk.'))]),

 ('The Key in the Light', 'המפתח באור', [
  P(("ג'וחא איבד את המפתח שלו בלילה.", 'Juha lost his key at night.'),
    ('הוא חיפש אותו מתחת לאור ברחוב.', 'He looked for it under the light in the street.')),
  P(('השכן בא וחיפש איתו.', 'The neighbour came and searched with him.'),
    ('הוא שאל: איפה בדיוק נפל המפתח?', 'He asked: where exactly did the key fall?'),
    ("ג'וחא אמר: הוא נפל בתוך הבית.", 'Juha said: it fell inside the house.')),
  P(('השכן אמר: אז למה אתה מחפש פה?', 'The neighbour said: so why are you looking here?'),
    ("ג'וחא אמר: כי פה יש אור.", 'Juha said: because here there is light.'))]),

 ('Three Days of Bread', 'לחם לשלושה ימים', [
  P(("ג'וחא קנה לחם לשלושה ימים.", 'Juha bought bread for three days.'),
    ('הוא שם אותו על השולחן והלך לישון.', 'He put it on the table and went to sleep.')),
  P(('בבוקר הוא ראה שחסר לחם.', 'In the morning he saw that bread was missing.'),
    ('הוא אמר: יש עכבר בבית.', 'He said: there is a mouse in the house.'),
    ('הוא הביא חתול קטן.', 'He brought a small cat.')),
  P(('למחרת חסרו גם הלחם וגם החלב.', 'The next day both the bread and the milk were missing.'),
    ("ג'וחא אמר: עכשיו יש לי עכבר וחתול.", 'Juha said: now I have a mouse and a cat.'))]),

 ('The Sermon', 'הדרשה', [
  P(("ביקשו מג'וחא לדבר לפני האנשים.", 'They asked Juha to speak in front of the people.'),
    ('הוא עמד ושאל: אתם יודעים מה אני אומר?', 'He stood and asked: do you know what I am going to say?')),
  P(('הם אמרו: לא, אנחנו לא יודעים.', 'They said: no, we do not know.'),
    ('הוא אמר: גם אני לא יודע. שלום.', 'He said: I do not know either. Goodbye.')),
  P(('בשבוע הבא הוא שאל את אותה שאלה.', 'The next week he asked the same question.'),
    ('הם אמרו: אנחנו יודעים.', 'They said: we know.'),
    ('הוא אמר: אז אין צורך שאני אדבר.', 'He said: then there is no need for me to speak.')),
  P(('בשבוע השלישי חצי אמרו יודעים.', 'The third week half of them said we know.'),
    ('והחצי השני אמרו לא יודעים.', 'And the other half said we do not know.'),
    ("ג'וחא אמר: טוב מאוד.", 'Juha said: very good.'),
    ('מי שיודע יספר למי שלא יודע.', 'Whoever knows should tell whoever does not know.'))]),

 ('Carrying the Door', 'הדלת על הגב', [
  P(("ג'וחא רצה לנסוע ולעזוב את הבית.", 'Juha wanted to travel and leave the house.'),
    ('אמא שלו אמרה לו: תשמור על הדלת.', 'His mother said to him: look after the door.')),
  P(('הוא הוריד את הדלת ושם אותה על הגב.', 'He took the door off and put it on his back.'),
    ('הוא הלך איתה כל הדרך.', 'He walked with it the whole way.')),
  P(('אנשים שאלו: למה אתה נושא דלת?', 'People asked: why are you carrying a door?'),
    ('הוא אמר: אמא שלי אמרה לשמור עליה.', 'He said: my mother told me to look after it.'))]),

 ('The Ring in the Well', 'הטבעת בבאר', [
  P(("הטבעת של ג'וחא נפלה לבאר.", "Juha's ring fell into the well."),
    ('הבאר הייתה עמוקה והמים רחוקים.', 'The well was deep and the water far down.')),
  P(('הוא הביא צלחת יוגורט ושפך אותה פנימה.', 'He brought a plate of yoghurt and poured it in.'),
    ('השכן ראה אותו ושאל: מה אתה עושה?', 'The neighbour saw him and asked: what are you doing?')),
  P(("ג'וחא אמר: אני מכין יוגורט.", 'Juha said: I am making yoghurt.'),
    ('השכן אמר: באר לא נהיית יוגורט.', 'The neighbour said: a well does not become yoghurt!'),
    ("ג'וחא אמר: ואם כן?", 'Juha said: and what if it does?'))]),

 ('Counting the Donkeys', 'סופרים את החמורים', [
  P(("לג'וחא היו עשרה חמורים.", 'Juha had ten donkeys.'),
    ('הוא רכב על אחד וספר את השאר.', 'He rode one and counted the rest.')),
  P(('הוא ספר תשעה ופחד.', 'He counted nine and was frightened.'),
    ('הוא ירד, הלך וספר שוב: עשרה.', 'He got down, walked and counted again: ten.')),
  P(('הוא רכב והיו תשעה. הוא ירד והיו עשרה.', 'He rode and there were nine. He got down and there were ten.'),
    ('הוא אמר: ללכת יותר טוב לחמורים.', 'He said: walking is better for the donkeys.'))]),

 ('The Cold Night', 'הלילה הקר', [
  P(("איש התערב עם ג'וחא: תעמוד לילה בקור?", 'A man bet Juha: can you stand a night in the cold?'),
    ("ג'וחא אמר: אני יכול.", 'Juha said: I can.')),
  P(('הוא עמד בחוץ כל הלילה בלי אש.', 'He stood outside all night with no fire.'),
    ('בבוקר האיש שאל: ראית איזה אור?', 'In the morning the man asked: did you see any light?'),
    ('הוא אמר: ראיתי נר רחוק מאוד.', 'He said: I saw a candle very far away.')),
  P(('האיש אמר: אז התחממת ממנו. לא אשלם.', 'The man said: then you warmed yourself with it. I will not pay.')),
  P(('למחרת הוא הזמין אותו לאוכל.', 'The next day he invited him for food.'),
    ('האיש ישב הרבה זמן והאוכל לא בא.', 'The man sat for a long time and the food did not come.'),
    ('הוא הלך למטבח וראה סיר מעל נר.', 'He went to the kitchen and saw a pot above a candle.'),
    ("ג'וחא אמר: נר שמחמם איש מבשל אוכל.", 'Juha said: a candle that warms a man cooks food.'))]),

 ('Which Half', 'איזה חצי', [
  P(("שאלו את ג'וחא שאלה קשה.", 'They asked Juha a hard question.'),
    ('למה העולם חצי לילה וחצי יום?', 'Why is the world half night and half day?')),
  P(('הוא חשב קצת ואמר: אני לא יודע.', 'He thought a little and said: I do not know.'),
    ('האיש כעס: אתה חכם, אתה צריך לדעת.', 'The man was cross: you are a scholar, you should know.')),
  P(('הוא אמר: חכם יודע מתי לומר לא יודע.', 'He said: a scholar knows when to say I do not know.'))]),

 ('The Long Way Home', 'הדרך הארוכה הביתה', [
  P(("ג'וחא חזר מהשוק בלילה.", 'Juha came back from the market at night.'),
    ('הוא הלך והלך וחזר לאותו מקום.', 'He walked and walked and came back to the same place.')),
  P(('הוא ישב מתחת לעץ ואמר: אחכה לבוקר.', 'He sat under a tree and said: I will wait for morning.'),
    ('הוא ישן קצת והתעורר מקול תרנגול.', 'He slept a little and woke to the sound of a rooster.')),
  P(('הוא ראה שהוא מול הדלת של הבית שלו.', 'He saw that he was in front of his own door.'),
    ('הוא אמר: הדרך הכי קצרה הביתה היא שינה.', 'He said: the shortest way home is sleep.'))]),

 ('Salt and Wool', 'מלח וצמר', [
  P(("ג'וחא שם מלח על החמור.", 'Juha loaded salt on the donkey.'),
    ('החמור נפל למים והמלח נעלם.', 'The donkey fell into the water and the salt disappeared.')),
  P(('המשא נהיה קל והחמור שמח.', 'The load became light and the donkey was pleased.'),
    ('בפעם הבאה החמור נפל למים בכוונה.', 'The next time the donkey fell in the water on purpose.')),
  P(('אבל הפעם הוא נשא צמר.', 'But this time he was carrying wool.'),
    ('הצמר שתה את המים והיה כבד מאוד.', 'The wool drank the water and became very heavy.'),
    ("ג'וחא אמר: לכל דבר יש זמן.", 'Juha said: everything has its time.'))]),

 ('The Borrowed Cooking', 'הבישול המושאל', [
  P(("השכנה ביקשה מג'וחא מלח.", 'The neighbour asked Juha for salt.'),
    ('הוא נתן לה קצת.', 'He gave her some.')),
  P(('אחר כך היא ביקשה שמן ואז בצל.', 'Afterwards she asked for oil and then onion.'),
    ('הוא נתן לה הכול.', 'He gave her everything.')),
  P(('בסוף היא אמרה: האוכל מוכן, בא לך לאכול?', 'In the end she said: the food is ready, would you like to eat?'),
    ("ג'וחא אמר: בטח, זה האוכל שלי.", 'Juha said: of course, it is my food.'))]),

 ('The Fur Coat in Summer', 'מעיל הפרווה בקיץ', [
  P(("באמצע הקיץ ג'וחא לבש מעיל פרווה.", 'In the middle of summer Juha wore a fur coat.'),
    ('אנשים צחקו עליו.', 'People laughed at him.')),
  P(('הם שאלו: לא חם לך?', 'They asked: are you not hot?'),
    ('הוא אמר: הפרווה לא נותנת לחום להיכנס.', 'He said: the fur does not let the heat in.')),
  P(('בחורף הוא לבש את אותו מעיל.', 'In winter he wore the same coat.'),
    ('הוא אמר: והיא לא נותנת לחום לצאת.', 'He said: and it does not let the warmth out.'))]),

 ('The Debt', 'החוב', [
  P(("ג'וחא לקח כסף מאיש אחד.", 'Juha borrowed money from a man.'),
    ('הגיע הזמן לשלם ולא היה לו.', 'The time to pay came and he did not have it.')),
  P(('האיש בא לבית והתחיל לצעוק.', 'The man came to the house and started shouting.'),
    ("ג'וחא אמר לאשתו: תגידי שהוא לא פה.", 'Juha said to his wife: tell him he is not here.')),
  P(("האישה אמרה: ג'וחא לא בבית.", 'The wife said: Juha is not at home.'),
    ('האיש צעק מהחלון: אבל אני רואה אותו.', 'The man shouted from the window: but I can see him!'),
    ("ג'וחא אמר: מחר כשאמות, גם תראה אותי?", 'Juha said: tomorrow when I die, will you see me too?'))]),

 ('The Old Tree', 'העץ של הזקן', [
  P(("ג'וחא שתל עץ זית כשהיה זקן.", 'Juha planted an olive tree when he was old.'),
    ('השכן צחק ואמר: לא תאכל ממנו.', 'The neighbour laughed and said: you will not eat from it.')),
  P(('הוא אמר: אכלתי מעצים שלא שתלתי.', 'He said: I ate from trees I did not plant.'),
    ('ומישהו אחר יאכל מזה.', 'And someone else will eat from this one.'))]),

 ('The Broken Jar', 'הכד השבור', [
  P(("ג'וחא שלח את הבן להביא מים.", 'Juha sent his son to bring water.'),
    ('לפני שהוא יצא, הוא נתן לו סטירה.', 'Before he left, he gave him a slap.')),
  P(('השכנים כעסו: למה הכית אותו סתם?', 'The neighbours were angry: why did you hit him for nothing?')),
  P(('הוא אמר: כשהכד נשבר, הוא שבור.', 'He said: when the jar breaks, it is broken.'),
    ('ולהכות אחרי זה לא עוזר.', 'And hitting after that does not help.'))]),

 ('Both Are Right', 'שניהם צודקים', [
  P(("שני אנשים באו לג'וחא כשהיה שופט.", 'Two men came to Juha when he was a judge.'),
    ('הראשון סיפר את הסיפור שלו.', 'The first told his story.'),
    ("ג'וחא אמר: אתה צודק.", 'Juha said: you are right.')),
  P(('השני סיפר את הסיפור שלו.', 'The second told his story.'),
    ("ג'וחא אמר: גם אתה צודק.", 'Juha said: you are right too.')),
  P(('אשתו ישבה שם.', 'His wife was sitting there.'),
    ('היא אמרה: הם לא יכולים שניהם לצדוק.', 'She said: they cannot both be right!'),
    ("ג'וחא אמר: וגם את צודקת.", 'Juha said: and you are right as well.'))]),

 ('The Heavy Basket', 'הסל הכבד', [
  P(("ג'וחא שם סל כבד על החמור.", 'Juha put a heavy basket on the donkey.'),
    ('ואחר כך הוא גם רכב.', 'And then he rode as well.')),
  P(('אבל הוא נשא את הסל על הראש.', 'But he was carrying the basket on his head.'),
    ('מישהו שאל: למה לא לשים אותו על החמור?', 'Someone asked: why not put it on the donkey?')),
  P(('הוא אמר: החמור נושא אותי, זה מספיק.', 'He said: the donkey is carrying me, that is enough.'))]),

 ('Nine Months', 'תשעה חודשים', [
  P(("שכן שאל את ג'וחא: מתי העבודה תיגמר?", 'A neighbour asked Juha: when will the work be finished?')),
  P(('הוא אמר: בעוד תשעה חודשים.', 'He said: in nine months.'),
    ('השכן אמר: זו עבודה של יומיים.', 'The neighbour said: this is two days of work!')),
  P(('הוא אמר: כל דבר טוב צריך תשעה חודשים.', 'He said: everything good needs nine months.'))]),

 ('The Guest Who Stayed', 'האורח שנשאר', [
  P(("אורח בא לג'וחא והוא נשאר שלושה ימים.", 'A guest came to Juha and he stayed three days.'),
    ('אחר כך הוא לא רצה ללכת.', 'Afterwards he did not want to leave.')),
  P(("ג'וחא התחיל לדבר על דגים.", 'Juha started talking about fish.'),
    ('הוא אמר: דג ואורח מריחים אחרי שלושה ימים.', 'He said: a fish and a guest smell after three days.')),
  P(('האורח צחק ואמר: אני לא דג.', 'The guest laughed and said: I am not a fish.'),
    ("ג'וחא אמר: אבל אני רעב.", 'Juha said: but I am hungry.'))]),

 ('Which Is Older', 'מה יותר חשוב', [
  P(("שאלו את ג'וחא: הירח או השמש?", 'They asked Juha: the moon or the sun?')),
  P(('הוא חשב ואמר: הירח.', 'He thought and said: the moon.'),
    ('שאלו אותו: למה?', 'They asked him: why?')),
  P(('הוא אמר: כי הוא יוצא בלילה.', 'He said: because it comes out at night.'),
    ('אז אנחנו צריכים אור.', 'That is when we need light.'),
    ('והשמש יוצאת ביום כשכבר אור.', 'And the sun comes out in the day when it is already light.'))]),

 ('The Mirror', 'המראה', [
  P(("ג'וחא ראה את עצמו במראה בפעם הראשונה.", 'Juha saw himself in a mirror for the first time.'),
    ('הוא אמר: מי הזקן הזה?', 'He said: who is this old man?')),
  P(('הוא הלך לאשתו ואמר: יש איש במראה.', 'He went to his wife and said: there is a man in the mirror.'),
    ('היא הסתכלה ואמרה: ויש גם אישה.', 'She looked and said: and there is a woman too!'))]),

 ('The Wrong Grave', 'הקבר הלא נכון', [
  P(("ג'וחא הלך בלילה ופחד.", 'Juha walked at night and was afraid.'),
    ('הוא נכנס לבור בדרך וישן.', 'He got into a hole in the road and slept.')),
  P(('אנשים עברו ושאלו: מה אתה עושה פה?', 'People passed and asked: what are you doing here?'),
    ('הוא אמר: אני מת.', 'He said: I am dead.')),
  P(('הם אמרו: ומת מדבר?', 'They said: and does a dead man talk?'),
    ('הוא אמר: מדבר אם הוא רעב.', 'He said: he talks if he is hungry.'))]),

 ('The Egg', 'הביצה', [
  P(("ג'וחא מצא ביצה בדרך.", 'Juha found an egg on the road.'),
    ('הוא אמר: מהביצה תצא תרנגולת.', 'He said: from the egg a chicken will come.')),
  P(('ומהתרנגולת יהיו הרבה ביצים.', 'And from the chicken there will be many eggs.'),
    ('ומהביצים הרבה תרנגולות.', 'And from the eggs many chickens.'),
    ('ומהתרנגולות הרבה כסף.', 'And from the chickens a lot of money.')),
  P(('בזמן שהוא חשב, הביצה נפלה ונשברה.', 'While he was thinking, the egg fell and broke.'),
    ('הוא אמר: כל הכסף שלי הלך.', 'He said: all my money is gone.'))]),

 ('Teaching the Donkey', 'מלמדים את החמור', [
  P(("השליט אמר לג'וחא: תלמד את החמור לקרוא.", 'The ruler said to Juha: teach my donkey to read.'),
    ('הוא אמר: אני צריך עשר שנים.', 'He said: I need ten years.')),
  P(('אנשים אמרו לו: אתה משוגע, חמור לא קורא.', 'People told him: you are mad, a donkey does not read!')),
  P(('הוא אמר: בעשר שנים קורים הרבה דברים.', 'He said: in ten years a lot of things happen.'),
    ('או שהשליט ימות, או החמור, או אני.', 'Either the ruler dies, or the donkey, or I do.'))]),

 ('The Fastest Way', 'הדרך הכי מהירה', [
  P(("מישהו שאל את ג'וחא: כמה זמן לעיר?", 'Someone asked Juha: how long to the town?'),
    ("ג'וחא לא ענה לו.", 'Juha did not answer him.')),
  P(('האיש הלך קצת.', 'The man walked a little.'),
    ("ג'וחא צעק: שעתיים!", 'Juha shouted: two hours!')),
  P(('האיש שאל: למה לא אמרת בהתחלה?', 'The man asked: why did you not say so at first?'),
    ('הוא אמר: הייתי צריך לראות איך אתה הולך.', 'He said: I had to see how you walk.'))]),

 ('The Two Ends', 'שני הצדדים', [
  P(("ג'וחא ישב על ענף והתחיל לחתוך אותו.", 'Juha sat on a branch and started cutting it.'),
    ('מישהו עבר ואמר: אתה תיפול.', 'Someone passed and said: you will fall!')),
  P(('הוא לא שמע, ואחרי רגע הוא נפל.', 'He did not listen, and a moment later he fell.')),
  P(('הוא רץ אחרי האיש ואמר: אתה יודע הכול.', 'He ran after the man and said: you know everything!'),
    ('תגיד לי מתי אני אמות.', 'Tell me when I will die.'))]),

 ('The Bag of Onions', 'שק הבצל', [
  P(("ג'וחא קנה שק בצל בשוק.", 'Juha bought a bag of onions at the market.'),
    ('הדרך הייתה ארוכה והשק כבד.', 'The road was long and the bag heavy.')),
  P(('כל כמה דקות הוא עצר וספר את הבצל.', 'Every few minutes he stopped and counted the onions.'),
    ('מישהו שאל: למה אתה סופר?', 'Someone asked: why are you counting?')),
  P(('הוא אמר: כשאני סופר אני שוכח שאני עייף.', 'He said: when I count I forget that I am tired.'))]),

 ('Two Dinners', 'שתי ארוחות', [
  P(("הזמינו את ג'וחא לשתי ארוחות באותו ערב.", 'Juha was invited to two dinners the same evening.'),
    ('הוא לא ידע לאן ללכת.', 'He did not know where to go.')),
  P(('הוא הלך לראשונה ואכל קצת.', 'He went to the first and ate a little.'),
    ('ואחר כך הלך לשנייה ואכל שוב.', 'And then he went to the second and ate again.')),
  P(('הוא חזר הביתה עייף וכאבה לו הבטן.', 'He came home tired and his stomach hurt.'),
    ('הוא אמר: פעם אחת יותר טוב משתיים.', 'He said: once is better than twice.'))]),

 ('The Neighbour Who Never Returns', 'השכן שלא מחזיר', [
  P(("השכן של ג'וחא היה לוקח ולא מחזיר.", "Juha's neighbour used to borrow and not return."),
    ('הוא לקח את המסור, את החבל ואת הסולם.', 'He borrowed the saw, the rope and the ladder.')),
  P(('יום אחד הוא בא ואמר: אני רוצה את החמור.', 'One day he came and said: I want the donkey.'),
    ("ג'וחא אמר: החמור נסע.", 'Juha said: the donkey has travelled.')),
  P(('השכן שאל: לאן?', 'The neighbour asked: where to?'),
    ('הוא אמר: להביא את הדברים שלי מהבית שלך.', 'He said: to bring my things back from your house.'))]),

 ('The Sweetest Thing', 'הדבר הכי מתוק', [
  P(("שאלו את ג'וחא: מה הכי מתוק בעולם?", 'They asked Juha: what is the sweetest thing in the world?')),
  P(('הוא אמר: דבש.', 'He said: honey.'),
    ('הם אמרו: ובריאות?', 'They said: and health?')),
  P(('הוא אמר: בריאות היא לא דבר בעולם.', 'He said: health is not a thing in the world.'),
    ('בריאות היא העולם.', 'Health is the world.'))]),

 ('The Empty Purse', 'הארנק הריק', [
  P(("גנב נכנס לבית של ג'וחא בלילה.", "A thief came into Juha's house at night."),
    ('הוא התחיל לחפש בחושך.', 'He started searching in the dark.')),
  P(("ג'וחא התעורר והתחיל לחפש איתו.", 'Juha woke up and started searching with him.'),
    ('הגנב פחד ואמר: מה אתה עושה?', 'The thief was frightened and said: what are you doing?')),
  P(('הוא אמר: אני עוזר לך.', 'He said: I am helping you.'),
    ('ביום אני לא מוצא כלום.', 'In the day I find nothing.'),
    ('אולי בלילה יימצא משהו.', 'Maybe at night something will turn up.'))]),

 ('The Wise Fool', 'החכם שנראה טיפש', [
  P(("הילדים ברחוב היו צוחקים על ג'וחא.", 'The children in the street used to laugh at Juha.'),
    ('הם נתנו לו לבחור מטבע גדול או קטן.', 'They let him choose a big coin or a small one.'),
    ('הוא תמיד לקח את הקטן.', 'He always took the small one.')),
  P(('מישהו אמר לו: קח את הגדול, הוא שווה יותר.', 'Someone said to him: take the big one, it is worth more.'),
    ('הוא אמר: אם אקח, הם יפסיקו לשחק.', 'He said: if I take it, they will stop playing.')),
  P(('ואז לא אקבל אפילו מטבע אחד.', 'And then I will not get even one coin.'))]),

 ('The Letter', 'המכתב', [
  P(("מישהו ביקש מג'וחא לכתוב לו מכתב.", 'Someone asked Juha to write him a letter.'),
    ('הוא אמר: אני לא יכול, כואבות לי הרגליים.', 'He said: I cannot, my legs hurt.')),
  P(('האיש שאל: מה הקשר בין רגליים לכתיבה?', 'The man asked: what have legs to do with writing?')),
  P(('הוא אמר: אף אחד לא קורא את הכתב שלי.', 'He said: nobody can read my handwriting.'),
    ('אז אני צריך ללכת ולקרוא להם.', 'So I have to walk over and read it to them.'))]),

 ('The Full Moon', 'הירח המלא', [
  P(("ג'וחא וחבר שלו ישבו והסתכלו על הירח.", 'Juha and a friend sat looking at the moon.'),
    ('החבר שאל: מה קורה לירח הישן?', 'The friend asked: what happens to the old moon?')),
  P(('הוא אמר: שוברים אותו ועושים ממנו כוכבים.', 'He said: they break it and make stars out of it.'))]),

 ('Everyone Is a Little Right', 'לכל אחד יש קצת צדק', [
  P(("בסוף החיים שאלו את ג'וחא: מה למדת?", 'At the end of his life they asked Juha: what did you learn?')),
  P(('הוא אמר: למדתי שאני לא יודע הרבה.', 'He said: I learned that I do not know much.'),
    ('ולמדתי שמי שצוחק חי יותר.', 'And I learned that whoever laughs lives longer.')),
  P(('ולמדתי שהחמור מבין יותר מהבעלים שלו.', 'And I learned that the donkey understands more than its owner.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('juha', {'en': 'Juha', 'he': "ג'וחא"}, 'beginner', CHAPTERS,
                          unit='Tale', unit_he='מעשה', shelf=1, meta=META))
