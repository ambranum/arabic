#!/usr/bin/env python3
"""כלילה ודמנה — the animal fables, retold in modern Hebrew, graded to intermediate.

The Hebrew twin of pipeline/book_kalila.py. Ibn al-Muqaffaʿ made the Arabic in the eighth
century from the Sanskrit Panchatantra by way of Persian; it is public domain by age, and these
are retellings from the plots.

WHY IT BELONGS ON A HEBREW SHELF AS MUCH AS AN ARABIC ONE. Kalila and Dimna is one of the few
books that both literatures actually share: Rabbi Joel translated it into Hebrew in the twelfth
century, one of the earliest Hebrew translations of anything, and from his version it went into
Latin and out to the rest of Europe. A learner meeting it in Hebrew is not meeting a foreign
book — they are meeting one that came home.

The frame is a court: a philosopher tells a king a story, and inside it two jackals plot. That
frame is what makes it intermediate rather than beginner — the reader has to hold one story
inside another, which is a grammatical demand as much as a narrative one.

Deliberately unpointed; the vowels are looked up at ingest.

Run:  python3 pipeline/he_book_kalila.py --lang he            # check
      python3 pipeline/he_book_kalila.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'Kalila and Dimna', 'author': 'Ibn al-Muqaffaʿ, from the Panchatantra',
        'year': '8th century', 'status': 'public domain — medieval'}

CHAPTERS = [
 ('The Philosopher and the King', 'החכם והמלך', [
  P(('מלך גדול קרא לחכם הזקן של הארמון וביקש ממנו עצה.', 'A great king called the old sage of the palace and asked him for advice.'),
    ('הוא אמר: אני רוצה ללמוד איך לשלוט ואיך לבחור אנשים.', 'He said: I want to learn how to rule and how to choose people.')),
  P(('החכם אמר: אני לא אתן לך חוקים, אני אספר לך סיפורים.', 'The sage said: I will not give you laws, I will tell you stories.'),
    ('הוא אמר: בסיפורים החיות מדברות, אבל הן מדברות עלינו.', 'He said: in the stories the animals speak, but they speak about us.'),
    ('המלך צחק ואמר: תספר, יש לי זמן.', 'The king laughed and said: tell them, I have time.')),
  P(('החכם התחיל: היה מלך אריה ביער גדול.', 'The sage began: there was a lion king in a great forest.'),
    ('ולמלך היו שני יועצים, ושמם היה כלילה ודמנה.', 'And the king had two advisers, and their names were Kalila and Dimna.'),
    ('אחד מהם רצה שקט, והשני רצה לעלות גבוה.', 'One of them wanted quiet, and the other wanted to rise high.'))]),

 ('Two Jackals at the Lion’s Gate', 'שני התנים בשער', [
  P(('כלילה ודמנה חיו קרוב לארמון של האריה.', 'Kalila and Dimna lived close to the lion’s palace.'),
    ('הם לא היו קרובים למלך, אבל ראו הכול מרחוק.', 'They were not close to the king, but they saw everything from a distance.')),
  P(('דמנה אמר: למה אנחנו יושבים פה כל היום בלי לעשות כלום?', 'Dimna said: why do we sit here all day doing nothing?'),
    ('כלילה אמר: כי זה בטוח, ומי שקרוב למלך גם קרוב לסכנה.', 'Kalila said: because it is safe, and whoever is close to a king is close to danger.')),
  P(('דמנה אמר: מי שלא מנסה נשאר בחוץ לתמיד.', 'Dimna said: whoever does not try stays outside for ever.'),
    ('כלילה אמר: ומי שמנסה יותר מדי מפסיד גם את מה שיש לו.', 'Kalila said: and whoever tries too much loses even what he has.'),
    ('דמנה לא הקשיב, וקם והלך לכיוון הארמון.', 'Dimna did not listen, and got up and went towards the palace.'))]),

 ('The Ox Called Shatraba', 'השור שנשאר בבוץ', [
  P(('סוחר עבר ביער עם עגלה ועם שור חזק וגדול.', 'A merchant passed through the forest with a cart and a strong, big ox.'),
    ('בדרך השור נפל בבוץ ולא הצליח לקום.', 'On the way the ox fell in the mud and could not get up.')),
  P(('הסוחר חיכה יום, ואז אמר: הוא ימות פה, אני ממשיך.', 'The merchant waited a day, and then said: it will die here, I am going on.'),
    ('הוא השאיר את השור והמשיך בדרך.', 'He left the ox and went on his way.')),
  P(('אבל השור קם אחרי יומיים ומצא שדה ירוק ומים.', 'But the ox got up after two days and found a green field and water.'),
    ('הוא אכל ושתה והיה חזק מאוד.', 'It ate and drank and grew very strong.'),
    ('כשהיה שמח הוא געה בקול גדול, וכל היער שמע אותו.', 'When it was happy it bellowed loudly, and the whole forest heard it.'))]),

 ('The Friendship That Grew', 'החברות שגדלה', [
  P(('האריה שמע את הקול הגדול ופחד, כי לא ידע מה זה.', 'The lion heard the loud sound and was afraid, because he did not know what it was.'),
    ('הוא לא אמר לאף אחד שהוא פוחד, אבל דמנה ראה את זה.', 'He did not tell anyone that he was afraid, but Dimna saw it.')),
  P(('דמנה בא למלך ואמר: אני אביא לך את בעל הקול הזה.', 'Dimna came to the king and said: I will bring you the owner of that sound.'),
    ('הוא הלך לשור, דיבר איתו יפה, והביא אותו לארמון.', 'He went to the ox, spoke to him nicely, and brought him to the palace.')),
  P(('האריה ראה שהשור אוכל עשב ולא בשר, והפחד שלו עבר.', 'The lion saw that the ox ate grass and not meat, and his fear passed.'),
    ('הם דיברו הרבה, ומהר מאוד נהיו חברים טובים.', 'They talked a great deal, and very soon became good friends.'),
    ('האריה בילה איתו כל היום, ושכח את כל האחרים.', 'The lion spent all day with him, and forgot all the others.'))]),

 ('The Monkey and the Carpenter', 'הקוף והנגר', [
  P(('כלילה ראה שדמנה כועס, ושאל אותו למה.', 'Kalila saw that Dimna was angry, and asked him why.'),
    ('דמנה אמר: הבאתי את השור, ועכשיו אין לי מקום ליד המלך.', 'Dimna said: I brought the ox, and now I have no place beside the king.')),
  P(('כלילה אמר: אני אספר לך על קוף שראה נגר עובד.', 'Kalila said: I will tell you about a monkey that watched a carpenter working.'),
    ('הנגר חתך עץ ארוך ושם בו חתיכת ברזל כדי לפתוח אותו.', 'The carpenter cut a long log and put a piece of iron in it to open it up.')),
  P(('כשהנגר הלך, הקוף ישב על העץ ומשך את הברזל.', 'When the carpenter went away, the monkey sat on the log and pulled out the iron.'),
    ('העץ נסגר עליו, והוא צעק ולא הצליח לצאת.', 'The log closed on him, and he shouted and could not get out.'),
    ('כלילה אמר: מי שנכנס לעבודה של אחרים משלם על זה.', 'Kalila said: whoever meddles in other people’s work pays for it.'))]),

 ('Dimna Speaks to the Lion', 'דמנה מדבר אל האריה', [
  P(('דמנה לא הקשיב, והלך לאריה בפנים עצובות.', 'Dimna did not listen, and went to the lion with a sad face.'),
    ('האריה שאל: מה קרה לך? למה אתה שקט?', 'The lion asked: what has happened to you? Why are you quiet?')),
  P(('דמנה אמר: קשה לי לדבר, כי זה נוגע לחבר שלך.', 'Dimna said: it is hard for me to speak, because it concerns your friend.'),
    ('הוא אמר: השור מדבר עם החיות ואומר שהוא הכי חזק ביער.', 'He said: the ox talks to the animals and says he is the strongest in the forest.')),
  P(('האריה כעס, אבל אמר: אני לא מאמין, הוא חבר שלי.', 'The lion was angry, but said: I do not believe it, he is my friend.'),
    ('דמנה אמר: תסתכל עליו מחר, ואתה תראה איך הוא עומד מולך.', 'Dimna said: look at him tomorrow, and you will see how he stands before you.'),
    ('ומאותו רגע הספק נכנס ללב של המלך.', 'And from that moment the doubt entered the king’s heart.'))]),

 ('Dimna Speaks to the Ox', 'דמנה מדבר אל השור', [
  P(('אחר כך דמנה הלך אל השור ודיבר איתו בשקט.', 'Afterwards Dimna went to the ox and spoke to him quietly.'),
    ('הוא אמר: המלך כבר לא רוצה אותך פה, ואני שמעתי מה הוא אומר.', 'He said: the king no longer wants you here, and I heard what he says.')),
  P(('השור אמר: לא עשיתי לו כלום, למה שיכעס?', 'The ox said: I did nothing to him, why should he be angry?'),
    ('דמנה אמר: מלך לא צריך שום דבר, הוא צריך רק מצב רוח.', 'Dimna said: a king needs nothing at all, he needs only a mood.')),
  P(('הוא אמר: מחר תראה אותו עומד מוכן לקפוץ.', 'He said: tomorrow you will see him standing ready to spring.'),
    ('השור הלך משם עם פחד גדול בלב.', 'The ox went away with great fear in his heart.'))]),

 ('The Fight', 'הקרב', [
  P(('בבוקר השור בא אל המלך, אבל עמד רחוק ומוכן.', 'In the morning the ox came to the king, but stood far off and ready.'),
    ('האריה ראה את זה ואמר לעצמו: דמנה צדק.', 'The lion saw this and said to himself: Dimna was right.')),
  P(('שניהם הסתכלו זה על זה וחשבו את אותו דבר.', 'They both looked at each other and thought the same thing.'),
    ('אף אחד מהם לא רצה להילחם, ובכל זאת הם נלחמו.', 'Neither of them wanted to fight, and all the same they fought.')),
  P(('השור מת, והאריה עמד מעליו ובכה.', 'The ox died, and the lion stood over him and wept.'),
    ('הוא אמר: איבדתי חבר, ואני לא בטוח בשביל מה.', 'He said: I have lost a friend, and I am not sure what for.'))]),

 ('The Trial of Dimna', 'המשפט של דמנה', [
  P(('החיות ראו את הכול ודיברו על זה בכל היער.', 'The animals saw everything and talked about it all over the forest.'),
    ('אמא של האריה אמרה: מישהו דיבר, ואתה צריך לדעת מי.', 'The lion’s mother said: someone spoke, and you need to know who.')),
  P(('היה משפט, וכל החיות באו לשמוע.', 'There was a trial, and all the animals came to listen.'),
    ('דמנה דיבר יפה והסביר כל דבר בדרך אחרת.', 'Dimna spoke well and explained everything a different way.')),
  P(('אבל כלילה סיפר את האמת, כי לא יכול היה לשתוק.', 'But Kalila told the truth, because he could not stay silent.'),
    ('דמנה נסגר בבור, ושם הוא מת לבד.', 'Dimna was shut in a pit, and there he died alone.'),
    ('החכם אמר למלך: לכן מלך צריך לבדוק דברים בעצמו.', 'The sage said to the king: that is why a king must check things himself.'))]),

 ('The Fox and the Drum', 'השועל והתוף', [
  P(('שועל רעב הלך ביער ושמע קול חזק מאוד.', 'A hungry fox walked in the forest and heard a very loud noise.'),
    ('הקול בא מעץ גדול, והשועל פחד ממנו.', 'The sound came from a big tree, and the fox was afraid of it.')),
  P(('הוא אמר: מי שעושה קול כזה בטח גדול ומלא בשר.', 'He said: whatever makes such a sound must be big and full of meat.'),
    ('הוא התקרב לאט לאט, ומצא תוף ישן תלוי על ענף.', 'He came closer little by little, and found an old drum hanging on a branch.')),
  P(('הרוח הכתה בתוף, והתוף עשה את הרעש.', 'The wind struck the drum, and the drum made the noise.'),
    ('השועל שבר אותו ומצא בפנים רק אוויר.', 'The fox broke it open and found only air inside.'),
    ('הוא אמר: הכי הרבה רעש בא מהדברים הכי ריקים.', 'He said: the most noise comes from the emptiest things.'))]),

 ('The Three Fish', 'שלושת הדגים', [
  P(('בבריכה קטנה חיו שלושה דגים, ואחד היה חכם.', 'In a small pool lived three fish, and one was wise.'),
    ('יום אחד עברו שם דייגים ואמרו: נחזור מחר עם רשת.', 'One day fishermen passed and said: we will come back tomorrow with a net.')),
  P(('הדג החכם שמע, והוא יצא מהבריכה עוד באותו ערב.', 'The wise fish heard, and he left the pool that very evening.'),
    ('הדג השני חיכה, ורק כשראה את הרשת התחיל לחשוב.', 'The second fish waited, and only when he saw the net did he begin to think.')),
  P(('הוא עשה את עצמו מת, והדייגים זרקו אותו בחזרה.', 'He pretended to be dead, and the fishermen threw him back.'),
    ('הדג השלישי שחה כמו תמיד ולא שינה כלום.', 'The third fish swam as always and changed nothing.'),
    ('אותו הם לקחו, כי הוא לא חשב לא לפני ולא אחרי.', 'Him they took, because he thought neither before nor after.'))]),

 ('The Hare and the Lion', 'הארנב והאריה', [
  P(('אריה חזק חי ביער והרג הרבה יותר ממה שאכל.', 'A strong lion lived in the forest and killed far more than he ate.'),
    ('החיות באו אליו ואמרו: נשלח לך אחד כל יום, ואתה תפסיק לרדוף.', 'The animals came to him and said: we will send you one a day, and you will stop hunting.')),
  P(('האריה הסכים, וכל יום חיה אחת הלכה אליו.', 'The lion agreed, and every day one animal went to him.'),
    ('יום אחד הגיע התור של ארנב קטן וחכם.', 'One day it was the turn of a small, clever hare.')),
  P(('הארנב הגיע מאוחר, והאריה כעס מאוד.', 'The hare arrived late, and the lion was very angry.'),
    ('הארנב אמר: אריה אחר עצר אותי בדרך ואמר שהיער שלו.', 'The hare said: another lion stopped me on the way and said the forest is his.')),
  P(('האריה צעק: תראה לי אותו מיד.', 'The lion shouted: show him to me at once.'),
    ('הארנב הביא אותו לבאר עמוקה ואמר: הוא שם בפנים.', 'The hare brought him to a deep well and said: he is in there.'),
    ('האריה ראה את עצמו במים, קפץ פנימה, ולא יצא.', 'The lion saw himself in the water, jumped in, and did not come out.'))]),

 ('The Ringdove and the Net', 'היונה והרשת', [
  P(('להקת יונים עפה מעל שדה וראתה זרעים על האדמה.', 'A flock of doves flew over a field and saw seeds on the ground.'),
    ('הן ירדו לאכול, ומיד נסגרה עליהן רשת.', 'They came down to eat, and at once a net closed on them.')),
  P(('היונים התחילו לעוף לכל הצדדים, כל אחת לכיוון אחר.', 'The doves began to fly in all directions, each one a different way.'),
    ('הרשת לא זזה, כי כל אחת משכה נגד השנייה.', 'The net did not move, because each pulled against the other.')),
  P(('היונה הגדולה אמרה: כולנו נעוף יחד למעלה, באותו רגע.', 'The big dove said: we will all fly up together, at the same moment.'),
    ('הן עשו את זה, והרשת עלתה איתן לאוויר.', 'They did it, and the net rose with them into the air.'))]),

 ('The Mouse Who Cut the Net', 'העכבר שחתך את הרשת', [
  P(('היונים עפו עם הרשת עד לחור של עכבר שהיונה הכירה.', 'The doves flew with the net to the hole of a mouse the dove knew.'),
    ('היא קראה לו, והעכבר יצא והסתכל עליהן.', 'She called him, and the mouse came out and looked at them.')),
  P(('העכבר אמר: אני אתחיל לחתוך אותך קודם, כי את החברה שלי.', 'The mouse said: I will start by cutting you free first, because you are my friend.'),
    ('היונה אמרה: לא, תתחיל מהאחרות, ואותי תשאיר לסוף.', 'The dove said: no, begin with the others, and leave me for last.')),
  P(('העכבר שאל למה, והיא אמרה: אם אני אצא, אולי תתעייף.', 'The mouse asked why, and she said: if I get out, perhaps you will grow tired.'),
    ('העכבר חתך את כולן, ואחר כך אותה.', 'The mouse cut them all free, and afterwards her.'),
    ('הוא אמר: עכשיו אני מבין למה כולן שומעות לך.', 'He said: now I understand why they all listen to you.'))]),

 ('The Four Friends', 'ארבעת החברים', [
  P(('העכבר, היונה, צב וצבי נהיו חברים ליד אותו נהר.', 'The mouse, the dove, a tortoise and a deer became friends beside the same river.'),
    ('כל בוקר הם נפגשו ודיברו על מה שראו.', 'Every morning they met and talked about what they had seen.')),
  P(('יום אחד הצבי לא בא, וכולם דאגו לו.', 'One day the deer did not come, and they all worried about him.'),
    ('היונה עפה למעלה וראתה אותו סגור ברשת של צייד.', 'The dove flew up and saw him caught in a hunter’s net.')),
  P(('העכבר רץ וחתך את הרשת, והצבי יצא.', 'The mouse ran and cut the net, and the deer got out.'),
    ('אבל הצב הגיע לאט, והצייד תפס אותו במקום.', 'But the tortoise arrived slowly, and the hunter caught him instead.'),
    ('אז הם עשו תוכנית חדשה, כי חבר לא נשאר מאחור.', 'So they made a new plan, because a friend is not left behind.'))]),

 ('The Gazelle in the Trap', 'הצבי מציל את הצב', [
  P(('הצבי הלך ושכב על יד הדרך כאילו הוא פצוע.', 'The deer went and lay down by the road as if he were hurt.'),
    ('הצייד ראה אותו והניח את הצב על האדמה.', 'The hunter saw him and put the tortoise down on the ground.')),
  P(('הוא רץ אחרי הצבי, והצבי ברח ממנו לאט.', 'He ran after the deer, and the deer fled from him slowly.'),
    ('כל פעם שהצייד התקרב, הצבי זז עוד קצת.', 'Every time the hunter came close, the deer moved a little further.')),
  P(('בזמן הזה העכבר חתך את החבל של הצב.', 'In that time the mouse cut the rope of the tortoise.'),
    ('הצב נכנס למים והצבי ברח ליער.', 'The tortoise went into the water and the deer fled into the forest.')),
  P(('הצייד חזר ולא מצא כלום, לא צבי ולא צב.', 'The hunter came back and found nothing, no deer and no tortoise.'),
    ('הוא אמר: היער הזה מוזר, ואני הולך מפה.', 'He said: this forest is strange, and I am leaving.'),
    ('החכם אמר למלך: ארבע חיות קטנות ניצחו איש עם רשת.', 'The sage said to the king: four small animals beat a man with a net.'))]),

 ('The Owls and the Crows', 'הינשופים והעורבים', [
  P(('בעץ גדול חיו עורבים, ובהר קרוב חיו ינשופים.', 'In a big tree lived crows, and on a nearby hill lived owls.'),
    ('הם נלחמו שנים, ואף אחד כבר לא זכר למה.', 'They had fought for years, and nobody remembered why any more.')),
  P(('בלילה הינשופים ראו טוב, ובאו והרגו עורבים.', 'At night the owls saw well, and came and killed crows.'),
    ('ביום העורבים לא מצאו אותם, כי הם ישנו במערות.', 'By day the crows did not find them, because they slept in caves.')),
  P(('העורב הזקן אמר: בכוח לא ננצח מלחמה כזאת.', 'The old crow said: by force we will not win a war like this.'),
    ('הוא אמר: יש דרך אחת, אבל היא קשה לאחד מאיתנו.', 'He said: there is one way, but it is hard on one of us.'))]),

 ('The Crow Among the Owls', 'העורב בין הינשופים', [
  P(('העורב הזקן ביקש מהחברים שלו להכות אותו ולזרוק אותו מהעץ.', 'The old crow asked his friends to beat him and throw him out of the tree.'),
    ('החברים שלו עשו את זה, ואחר כך עפו משם.', 'His friends did it, and afterwards flew away.')),
  P(('הינשופים מצאו אותו פצוע ושאלו מי עשה לו את זה.', 'The owls found him hurt and asked who had done this to him.'),
    ('הוא אמר: העורבים, כי אמרתי שצריך לעשות איתכם שלום.', 'He said: the crows, because I said we should make peace with you.')),
  P(('הינשופים ריחמו עליו ולקחו אותו לגור איתם במערה.', 'The owls pitied him and took him to live with them in the cave.'),
    ('הוא חי שם חודשים, ולמד כל פינה וכל דרך.', 'He lived there for months, and learned every corner and every way.'),
    ('יום אחד הוא הביא את העורבים, והמערה נסגרה על הינשופים.', 'One day he brought the crows, and the cave was closed on the owls.'))]),

 ('The Monkey and the Tortoise', 'הקוף והצב', [
  P(('קוף חי על עץ תאנים על שפת הים ואכל טוב.', 'A monkey lived in a fig tree by the sea and ate well.'),
    ('צב שחה שם כל יום, והקוף זרק לו תאנים למים.', 'A tortoise swam there every day, and the monkey threw him figs in the water.')),
  P(('הם נהיו חברים ודיברו הרבה שעות.', 'They became friends and talked for many hours.'),
    ('הצב חזר הביתה מאוחר, והאישה שלו כעסה.', 'The tortoise came home late, and his wife was angry.')),
  P(('היא אמרה: אם הקוף אוכל תאנים כל היום, הלב שלו מתוק.', 'She said: if the monkey eats figs all day, his heart is sweet.'),
    ('היא אמרה: אני חולה, ורק הלב הזה ירפא אותי.', 'She said: I am ill, and only that heart will cure me.')),
  P(('הצב לקח את הקוף על הגב וסיפר לו באמצע הים.', 'The tortoise took the monkey on his back and told him in the middle of the sea.'),
    ('הקוף אמר בשקט: חבל, השארתי את הלב על העץ.', 'The monkey said quietly: what a pity, I left my heart in the tree.'),
    ('הצב חזר לחוף, והקוף קפץ ועלה על העץ וצחק.', 'The tortoise went back to the shore, and the monkey jumped up into the tree and laughed.'))]),

 ('The Ascetic and the Mongoose', 'הנזיר והחיה הנאמנה', [
  P(('לאיש טוב ולאישה שלו נולד בן אחרי שנים.', 'A good man and his wife had a son after many years.'),
    ('בבית שלהם גרה גם חיה קטנה שגדלה איתם.', 'In their house also lived a small animal that had grown up with them.')),
  P(('יום אחד האישה יצאה לשוק והשאירה את הילד ישן.', 'One day the wife went out to the market and left the child asleep.'),
    ('האיש יצא לרגע גם הוא, והחיה נשארה ליד המיטה.', 'The man too went out for a moment, and the animal stayed by the bed.')),
  P(('נחש נכנס לחדר והתקרב אל הילד.', 'A snake came into the room and approached the child.'),
    ('החיה נלחמה בו, הרגה אותו, והפה שלה נהיה אדום.', 'The animal fought it, killed it, and its mouth turned red.')),
  P(('האיש חזר, ראה את הפה האדום, וחשב שהחיה הרגה את הבן.', 'The man came back, saw the red mouth, and thought the animal had killed his son.'),
    ('הוא הרג אותה מיד, ורק אחר כך נכנס וראה את הילד ישן.', 'He killed it at once, and only afterwards went in and saw the child asleep.'),
    ('החכם אמר למלך: מי שעושה לפני שהוא חושב מתחרט אחרי.', 'The sage said to the king: whoever acts before he thinks regrets it afterwards.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('kalila', {'en': 'Kalila and Dimna', 'he': 'כלילה ודמנה'},
                          'intermediate', CHAPTERS, unit='Tale', unit_he='מעשה',
                          shelf=12, meta=META))
