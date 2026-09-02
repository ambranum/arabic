#!/usr/bin/env python3
"""מסביב לעולם בשמונים יום — Jules Verne, retold in modern Hebrew, graded to intermediate.

The Hebrew twin of pipeline/book_atw80.py, chapter for chapter. Verne died in 1905 and the
novel is public domain everywhere; this is a retelling from the plot, not a translation of any
edition.

WHY THIS OPENS THE INTERMEDIATE SHELF. It is the first book here with a PLOT that has to be
carried across thirty-eight chapters, and that is the whole difficulty of the tier: the reader
has to hold Fogg's bet in their head from chapter three to chapter thirty-eight, in Hebrew.
Everything else is chosen to make that possible — the same four people in every chapter, the
past tense throughout, and a journey that supplies its own vocabulary as it goes.

Sentences run longer than the beginner shelf's and are meant to: two clauses is where the
tier lives. Deliberately unpointed; the vowels are looked up at ingest.

Run:  python3 pipeline/he_book_atw80.py --lang he            # check
      python3 pipeline/he_book_atw80.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'Around the World in Eighty Days', 'author': 'Jules Verne', 'year': '1872',
        'status': 'public domain — author died 1905'}

CHAPTERS = [
 ('Passepartout Finds a New Master', 'פספרטו מוצא אדון חדש', [
  P(('בשכונה שקטה ויפה בלונדון עמד בית גדול, ובו גר אדם בשם פיליאס פוג.', 'In a quiet, handsome neighbourhood in London stood a big house, and in it lived a man named Phileas Fogg.'),
    ('הוא היה עשיר מאוד, אבל אף אחד לא ידע מאיפה בא הכסף שלו ומה ההיסטוריה שלו.', 'He was very rich, but nobody knew where his money came from or what his history was.'),
    ('לא הייתה לו אישה, לא היו לו ילדים, וגם חברים לא היו לו הרבה.', 'He had no wife, he had no children, and he did not have many friends either.'),
    ('הוא היה חבר במועדון מכובד, ושם הוא בילה את רוב הזמן שלו.', 'He was a member of a respectable club, and there he spent most of his time.')),
  P(('הדבר הכי חשוב בחיים של פוג היה הדיוק והסדר.', "The most important thing in Fogg's life was precision and order."),
    ('כל דבר היה צריך לקרות בדיוק בזמן, לא דקה יותר ולא דקה פחות.', 'Everything had to happen exactly on time, not a minute more and not a minute less.'),
    ('באותו יום הוא פיטר את המשרת הישן שלו, כי המים לגילוח לא היו בחום הנכון.', 'That very day he dismissed his old servant, because the shaving water was not at the right temperature.'),
    ('לכן הוא היה צריך למצוא משרת חדש.', 'So he had to find a new servant.')),
  P(('צרפתי בשם פספרטו בא לבקש את העבודה.', 'A Frenchman named Passepartout came to ask for the job.'),
    ('הוא היה איש חזק ושמח, ובחיים שלו הוא עשה הרבה עבודות שונות.', 'He was a strong, cheerful man, and in his life he had done many different jobs.'),
    ('פספרטו אמר: נמאס לי מהחיים בלי מנוחה, ואני רוצה עבודה שקטה אצל אדון ששומר על סדר.', 'Passepartout said: I am tired of a life without rest, and I want a quiet job with a master who keeps order.'),
    ('פוג שאל אותו כמה שאלות קצרות ואז אמר: התקבלת, מהיום אתה המשרת שלי.', 'Fogg asked him a few short questions and then said: you are hired, from today you are my servant.'))]),

 ('A Servant to His Liking', 'משרת לפי הטעם שלו', [
  P(('פוג יצא מהבית והשאיר את פספרטו לבד.', 'Fogg left the house and left Passepartout on his own.'),
    ('פספרטו הלך להסתכל על הבית החדש שלו, ומצא אותו נקי ומסודר כמו שעון.', 'Passepartout went to look at his new house, and found it clean and orderly like a clock.'),
    ('על הקיר היה תלוי דף עם כל המשימות והשעה של כל אחת בדיוק.', 'On the wall hung a sheet with all the tasks and the hour of each one exactly.'),
    ('פספרטו שמח מאוד ואמר: האיש הזה הוא מכונה, ואלה החיים שחלמתי עליהם.', 'Passepartout was delighted and said: this man is a machine, and this is the life I dreamed of.')),
  P(('אבל באותו לילה פוג חזר הביתה בשעה לא נכונה, דבר שמעולם לא קרה.', 'But that very night Fogg came home at the wrong hour, something that had never happened.'),
    ('הוא אמר לפספרטו בשקט: בעוד עשר דקות אתה ואני נוסעים מסביב לעולם.', 'He said to Passepartout quietly: in ten minutes you and I are travelling around the world.'),
    ('פספרטו לא האמין למה ששמע, וחשב שהאדון שלו צוחק עליו.', 'Passepartout did not believe what he heard, and thought his master was joking with him.'),
    ('אבל פוג לא צחק אף פעם אחת בכל החיים שלו.', 'But Fogg had not joked a single time in his whole life.'))]),

 ('The Bet at the Club', 'ההימור במועדון', [
  P(('נחזור קצת אחורה, כדי לראות איך ההימור הזה התחיל.', 'Let us go back a little, to see how this bet began.'),
    ('באותו יום פוג ישב במועדון עם כמה מהחברים שלו.', 'That day Fogg was sitting at the club with a few of his friends.'),
    ('הם קראו בעיתון על שוד גדול שהיה בבנק המרכזי.', 'They were reading in the paper about a big robbery at the central bank.'),
    ('מישהו גנב חמישים וחמישה אלף לירות, והמשטרה חיפשה אותו בכל מקום.', 'Someone had stolen fifty-five thousand pounds, and the police were looking for him everywhere.')),
  P(('אחר כך הם דיברו על העולם, ועל כמה שהנסיעות נהיו מהירות וקלות.', 'Afterwards they talked about the world, and how fast and easy travel had become.'),
    ('אחד מהם אמר: נכון, אבל אי אפשר לעבור את כל כדור הארץ בזמן קצר.', 'One of them said: true, but it is impossible to cross the whole globe in a short time.'),
    ('פוג אמר בשקט: להפך, אפשר לעשות את זה בשמונים יום בלבד.', 'Fogg said quietly: on the contrary, it can be done in eighty days only.'),
    ('כולם צחקו ואמרו: זה רק על הנייר, לא במציאות.', 'They all laughed and said: that is only on paper, not in reality.')),
  P(('פוג אמר: אני מוכן להמר עשרים אלף לירות שאני אעשה את זה בעצמי.', 'Fogg said: I am ready to bet twenty thousand pounds that I will do it myself.'),
    ('היה שקט בחדר, ואז כולם הסכימו להימור.', 'The room went quiet, and then they all agreed to the bet.'),
    ('פוג אמר: הרכבת לפריז יוצאת הערב בשמונה ארבעים וחמש.', 'Fogg said: the train to Paris leaves this evening at eight forty-five.'),
    ('אני חייב לחזור למועדון הזה אחרי שמונים יום בדיוק, או שאני מפסיד הכול.', 'I must come back to this club after exactly eighty days, or I lose everything.'))]),

 ('The Departure', 'היציאה לדרך', [
  P(('פוג חזר הביתה וסיפר לפספרטו, והמשרת המסכן נבהל מאוד.', 'Fogg went home and told Passepartout, and the poor servant was very frightened.'),
    ('פוג אמר לו: קח תיק קטן ושים בו רק כמה בגדים.', 'Fogg said to him: take a small bag and put only a few clothes in it.'),
    ('הוא שם בתיק סכום כסף גדול, עשרים אלף לירות, בשביל הדרך.', 'He put a large sum of money in the bag, twenty thousand pounds, for the journey.'),
    ('הם הלכו לתחנה ועלו על הרכבת בדיוק בשמונה ארבעים וחמש.', 'They went to the station and boarded the train at exactly eight forty-five.')),
  P(('פוג ישב במקום שלו בשקט, בלי שום דאגה בעולם.', 'Fogg sat in his seat quietly, without a care in the world.'),
    ('אבל פספרטו נזכר פתאום שהוא שכח לכבות את מנורת הגז בחדר שלו.', 'But Passepartout suddenly remembered that he had forgotten to turn off the gas lamp in his room.'),
    ('הוא סיפר לאדון שלו, ופוג ענה בקור רוח: היא תדלוק על החשבון שלך עד שנחזור.', 'He told his master, and Fogg answered coolly: it will burn at your expense until we return.'),
    ('פספרטו שתק והבין שהנסיעה הזאת תהיה ארוכה ומוזרה.', 'Passepartout fell silent and understood that this journey would be long and strange.'))]),

 ('A Stir in London', 'סערה בלונדון', [
  P(('כשהחדשות על ההימור התפרסמו, כל לונדון דיברה על זה.', 'When the news of the bet got out, all of London was talking about it.'),
    ('היו אנשים שהימרו שפוג יצליח, והיו כאלה שהימרו שהוא ייכשל.', 'There were people who bet that Fogg would succeed, and others who bet that he would fail.'),
    ('אבל פתאום התגלה משהו ששינה את הכול.', 'But suddenly something came out that changed everything.'),
    ('המשטרה אמרה שהתיאור של גנב הבנק דומה מאוד לפיליאס פוג.', 'The police said that the description of the bank thief closely resembled Phileas Fogg.')),
  P(('אנשים התחילו לחשוד שפוג שדד את הבנק, ושהנסיעה הזאת היא רק תירוץ לברוח.', 'People began to suspect that Fogg had robbed the bank, and that this journey was only an excuse to escape.'),
    ('בלש חכם בשם פיקס רצה לתפוס את הגנב כדי להיות מפורסם ולקבל פרס.', 'A clever detective named Fix wanted to catch the thief in order to become famous and get a reward.'),
    ('הוא שמע שפוג נוסע מזרחה, אז הוא ארז את הדברים שלו והלך אחריו.', 'He heard that Fogg was travelling east, so he packed his things and went after him.'),
    ('פיקס אמר לעצמו: אני אתפוס את הגנב הזה, גם אם אסע אחריו מסביב לעולם.', 'Fix said to himself: I will catch this thief, even if I travel round the world after him.'))]),

 ('Fix Waits at Suez', 'פיקס מחכה בסואץ', [
  P(('פוג הגיע לעיר סואץ במצרים, ופיקס חיכה לו בנמל.', 'Fogg reached the city of Suez in Egypt, and Fix was waiting for him at the port.'),
    ('פיקס היה מודאג, כי הצו הרשמי שיאפשר לו לעצור את פוג עוד לא הגיע מלונדון.', 'Fix was worried, because the official warrant that would let him arrest Fogg had not yet arrived from London.'),
    ('בלי הצו הוא לא היה יכול לעשות שום דבר מחוץ לאנגליה.', 'Without the warrant he could do nothing outside England.'),
    ('אז הוא החליט לחכות, להסתכל, וללכת אחרי פוג עד שהצו יגיע.', 'So he decided to wait, to watch, and to follow Fogg until the warrant arrived.')),
  P(('פוג ירד מהספינה רק כדי לקבל חותמת על הדרכון שלו.', 'Fogg got off the ship only to get a stamp on his passport.'),
    ('פיקס ראה אותו מרחוק, הסתכל עליו היטב, והיה בטוח יותר שזה הגנב.', 'Fix saw him from a distance, looked at him closely, and was more certain that this was the thief.'),
    ('אבל הוא היה צריך לדעת לאן הם נוסעים כדי ללכת אחרי פוג כמו שצריך.', 'But he needed to know where they were going in order to follow Fogg properly.'),
    ('אז הוא ניגש למשרת פספרטו וניסה להוציא ממנו את המידע.', 'So he went up to the servant Passepartout and tried to get the information out of him.'))]),

 ('Passports and Police', 'דרכונים ומשטרה', [
  P(('פיקס ניגש לפספרטו והתחיל לדבר איתו יפה, כאילו הוא סתם נוסע רגיל.', 'Fix went up to Passepartout and started talking to him nicely, as if he were just an ordinary traveller.'),
    ('פספרטו היה עייף, ושמח למצוא מישהו שמדבר בשפה שלו.', 'Passepartout was tired, and glad to find someone who spoke his language.'),
    ('פיקס שאל אותו על האדון שלו ועל הנסיעה, ופספרטו ענה בתמימות גמורה.', 'Fix asked him about his master and about the journey, and Passepartout answered in complete innocence.'),
    ('הוא סיפר לו על ההימור ואמר: האדון שלי רוצה לעבור את העולם בשמונים יום.', 'He told him about the bet and said: my master wants to cross the world in eighty days.')),
  P(('פיקס לא האמין למזל שלו ואמר לעצמו: ההימור הזה הוא רק כיסוי לבריחה עם הכסף.', 'Fix could not believe his luck and said to himself: this bet is only a cover for escaping with the money.'),
    ('הוא אמר לפספרטו: כל הכסף הזה שיש לכם, זה בטח סכום גדול.', 'He said to Passepartout: all this money you have, it must be a large sum.'),
    ('פספרטו ענה: כן, יש לנו תיק מלא, והאדון שלי משלם במזומן בכל מקום.', 'Passepartout answered: yes, we have a full bag, and my master pays cash everywhere.'),
    ('פיקס חייך, ועכשיו הוא היה בטוח שהוא בדרך הנכונה.', 'Fix smiled, and now he was sure he was on the right track.'))]),

 ('Passepartout Talks Too Much', 'פספרטו מדבר יותר מדי', [
  P(('הם עלו שוב על ספינה לכיוון בומביי שבהודו, ופיקס נסע איתם ושמר מרחק.', 'They boarded a ship again towards Bombay in India, and Fix travelled with them and kept his distance.'),
    ('פספרטו התחיל לראות את פיקס בכל מקום, בכל ספינה ובכל תחנה.', 'Passepartout began to see Fix everywhere, on every ship and at every stop.'),
    ('אבל הוא לא חשד בו, וחשב שהאיש נהיה חבר שלו.', 'But he did not suspect him, and thought the man had become his friend.'),
    ('בכל פעם הוא דיבר איתו עוד, וגילה בלי לשים לב את כל הסודות של הנסיעה.', 'Each time he talked with him more, and revealed without noticing all the secrets of the journey.')),
  P(('פוג נשאר בחדר שלו בשקט, שיחק קלפים, ולא הסתכל לא על הים ולא על האנשים.', 'Fogg stayed in his room quietly, played cards, and looked neither at the sea nor at the people.'),
    ('הוא רק כתב במחברת שלו: הגענו לכאן ביום הזה, מוקדם או מאוחר מהתוכנית.', 'He only wrote in his notebook: we arrived here on this day, early or late against the plan.'),
    ('עד עכשיו הכול הלך בדיוק לפי התוכנית.', 'So far everything had gone exactly according to plan.'),
    ('אבל פיקס חיכה להזדמנות שלו, והעין שלו הייתה על פוג כל הזמן.', 'But Fix was waiting for his chance, and his eye was on Fogg the whole time.'))]),

 ('The Red Sea and Beyond', 'ים סוף והלאה', [
  P(('הספינה עברה את ים סוף, ומזג האוויר היה חם מאוד מאוד.', 'The ship crossed the Red Sea, and the weather was very, very hot.'),
    ('הנוסעים היו עייפים מהחום, אבל על פוג זה לא השפיע בכלל.', 'The passengers were tired from the heat, but it did not affect Fogg at all.'),
    ('בערב הוא שיחק קלפים עם כמה נוסעים, ותמיד ניצח בשקט.', 'In the evening he played cards with a few passengers, and always won quietly.'),
    ('פספרטו היה מאושר, והסתכל על הערים המוזרות ועל הנמלים.', 'Passepartout was delighted, and looked at the strange cities and at the ports.')),
  P(('אחרי כמה ימים הם הגיעו לעיר עדן, ומשם המשיכו לאוקיינוס ההודי.', 'After a few days they reached the city of Aden, and from there continued to the Indian Ocean.'),
    ('הים היה שקט והרוח הייתה טובה, אז הם נסעו במהירות יפה.', 'The sea was calm and the wind was good, so they travelled at a fine speed.'),
    ('הם הגיעו לבומביי יומיים לפני הזמן שחיכו לו.', 'They reached Bombay two days before the expected time.'),
    ('פוג לא שמח ולא דאג, הוא פשוט כתב את המספרים במחברת כרגיל.', 'Fogg was neither glad nor worried, he simply wrote the figures in the notebook as usual.'))]),

 ('Trouble at the Pagoda', 'צרות במקדש', [
  P(('בומביי הייתה עיר גדולה, מלאה אנשים, צבעים וריחות מוזרים.', 'Bombay was a big city, full of people, colours and strange smells.'),
    ('פוג נשאר בתחנה וחיכה לרכבת, אבל פספרטו הלך לטייל ולהסתכל.', 'Fogg stayed at the station and waited for the train, but Passepartout went to walk about and look.'),
    ('הכול היה חדש בעיניים שלו, והוא הרגיש כאילו הוא בחלום.', 'Everything was new to his eyes, and he felt as if he were in a dream.'),
    ('בלי לשים לב הוא נכנס למקדש גדול והנעליים עוד היו על הרגליים שלו.', 'Without noticing he went into a big temple and his shoes were still on his feet.')),
  P(('זה היה אסור והעליב מאוד את האנשים שם.', 'This was forbidden and greatly offended the people there.'),
    ('הם התנפלו עליו בכעס, לקחו את הנעליים והכו אותו.', 'They fell on him in anger, took his shoes and beat him.'),
    ('פספרטו ברח מהמקדש מהר ככל שיכול, בלי הנעליים שלו.', 'Passepartout fled the temple as fast as he could, without his shoes.'),
    ('הוא חזר לפוג מפוחד, אבל לא סיפר לו על הצרה כי פחד שהוא יכעס.', 'He came back to Fogg frightened, but did not tell him about the trouble because he was afraid he would be angry.')),
  P(('הם עלו על הרכבת שעוברת את הודו, מבומביי לכלכותה.', 'They boarded the train that crosses India, from Bombay to Calcutta.'),
    ('פיקס ראה כל מה שקרה במקדש והיה מרוצה מאוד.', 'Fix saw everything that happened at the temple and was very pleased.'),
    ('הוא אמר לעצמו: עכשיו יש לי סיבה לעצור את פוג בהודו, כי המקום הזה שייך לאנגליה.', 'He said to himself: now I have a reason to stop Fogg in India, because this place belongs to England.'),
    ('אבל הוא החליט לחכות לרגע הנכון.', 'But he decided to wait for the right moment.'))]),

 ('The Elephant', 'הפיל', [
  P(('בזמן הנסיעה הרכבת עצרה פתאום באמצע הדרך, רחוק מכל עיר.', 'During the journey the train suddenly stopped in the middle of the way, far from any city.'),
    ('התברר שהמסילה לא נגמרה, והעיתונים בלונדון טעו.', 'It turned out that the track was not finished, and the papers in London had been wrong.'),
    ('כל הנוסעים ירדו בכעס והתחילו לחפש דרך להמשיך.', 'All the passengers got off angrily and began looking for a way to continue.'),
    ('פוג נשאר רגוע ואמר: אנחנו חייבים למצוא פתרון, לא לעצור.', 'Fogg stayed calm and said: we must find a solution, not stop.')),
  P(('פספרטו מצא איש הודי עם פיל גדול וחזק.', 'Passepartout found an Indian man with a big, strong elephant.'),
    ('פוג הציע לו הרבה כסף כדי לקנות את הפיל, והאיש סירב בהתחלה.', 'Fogg offered him a lot of money to buy the elephant, and the man refused at first.'),
    ('בכל פעם פוג העלה את המחיר, והאיש סירב עוד, עד שהגיעו לסכום עצום.', 'Each time Fogg raised the price, and the man refused again, until they reached an enormous sum.'),
    ('בסוף האיש הסכים, והם לקחו גם מדריך צעיר שהכיר את הדרך ביער.', 'In the end the man agreed, and they also took a young guide who knew the way through the forest.')),
  P(('הם עלו על הגב של הפיל: פוג, פספרטו והמדריך.', 'They climbed onto the elephant’s back: Fogg, Passepartout and the guide.'),
    ('הם נסעו שעות ביער סמיך ובדרך קשה.', 'They travelled for hours through a dense forest and along a hard road.'),
    ('פספרטו היה מאושר, כי הוא מעולם לא רכב על פיל בחיים שלו.', 'Passepartout was overjoyed, because he had never ridden an elephant in his life.'),
    ('הפיל הלך בקצב קבוע, והמדריך הוביל אותו ביד בטוחה.', 'The elephant walked at a steady pace, and the guide led it with a sure hand.'))]),

 ('The Suttee', 'הטקס בלילה', [
  P(('בזמן שנסעו בלילה הם שמעו קולות של מוזיקה עצובה וראו אור של אש.', 'As they travelled at night they heard sounds of sad music and saw the light of a fire.'),
    ('המדריך אמר להם: תתחבאו, האנשים האלה עושים טקס ישן ומסוכן.', 'The guide said to them: hide, these people are performing an old and dangerous rite.'),
    ('הם התקרבו בשקט וראו קהל גדול מסביב לאישה צעירה ויפה.', 'They came closer quietly and saw a great crowd around a young, beautiful woman.'),
    ('המדריך אמר: קוראים לה אאודה, והבעל הזקן שלה מת.', 'The guide said: her name is Aouda, and her old husband has died.')),
  P(('לפי מנהג אכזרי הם רוצים לשרוף אותה חיה עם הגוף שלו בבוקר.', 'According to a cruel custom they intend to burn her alive with his body in the morning.'),
    ('הם נתנו לה סם בכוח כדי שלא תוכל להתנגד.', 'They had given her a drug by force so that she could not resist.'),
    ('פוג שתק רגע ואז אמר: יש לנו זמן עד חצות, אנחנו חייבים להציל אותה.', 'Fogg was silent a moment and then said: we have time until midnight, we must save her.'),
    ('המדריך פחד ואמר שזה מסוכן מאוד, אבל פוג היה נחוש.', 'The guide was afraid and said it was very dangerous, but Fogg was determined.'))]),

 ('The Bold Rescue', 'ההצלה הנועזת', [
  P(('הם חיכו עד חצות, כשהשומרים התעייפו והתחילו להירדם.', 'They waited until midnight, when the guards grew tired and started to fall asleep.'),
    ('הם ניסו להגיע לאישה, אבל היו הרבה שומרים מסביבה.', 'They tried to reach the woman, but there were many guards around her.'),
    ('כל תוכנית נכשלה, הבוקר התקרב, ופוג התעצב שהוא לא יכול לעשות כלום.', 'Every plan failed, the morning drew near, and Fogg grew sad that he could do nothing.'),
    ('אבל פספרטו נעלם, ואף אחד לא ידע לאן הוא הלך.', 'But Passepartout had disappeared, and nobody knew where he had gone.')),
  P(('עם אור ראשון הם שמו את הגוף של הבעל על האש והשכיבו את האישה לידו.', 'At first light they placed the husband’s body on the fire and laid the woman beside it.'),
    ('ופתאום הגוף קם, הרים את האישה, וכל האנשים ברחו מפוחדים.', 'And suddenly the body rose, lifted the woman, and all the people fled in terror.'),
    ('התברר שפספרטו נכנס בשקט ולקח את המקום של המת, ועשה את התרגיל החכם הזה.', 'It turned out that Passepartout had slipped in and taken the dead man’s place, and played this clever trick.'),
    ('הוא רץ עם האישה אל הפיל, וכולם ברחו מהר ככל שיכלו.', 'He ran with the woman to the elephant, and they all escaped as fast as they could.')),
  P(('אאודה הייתה עוד קצת תחת הסם ולא הבינה מה קרה.', 'Aouda was still a little under the drug and did not understand what had happened.'),
    ('כשהיא התעוררה היא הבינה שהם הצילו אותה ממוות בטוח.', 'When she woke she understood that they had saved her from certain death.'),
    ('היא הודתה להם מאוד, ופוג התנהג אליה בכבוד ובנימוס.', 'She thanked them greatly, and Fogg behaved towards her with respect and courtesy.'),
    ('הוא החליט לקחת אותה למקום בטוח, והיא נהייתה הרביעית בנסיעה.', 'He decided to take her to a safe place, and she became the fourth in the journey.'))]),

 ('Down to Calcutta', 'במורד הנהר לכלכותה', [
  P(('הם הגיעו לתחנת רכבת, נפרדו מהמדריך הצעיר והודו לו.', 'They reached a railway station, said goodbye to the young guide and thanked him.'),
    ('פוג נתן לו את הפיל במתנה, כי הוא כבר לא היה צריך אותו.', 'Fogg gave him the elephant as a gift, because he no longer needed it.'),
    ('הם עלו על הרכבת ונסעו לאורך הנהר לכיוון כלכותה.', 'They boarded the train and travelled along the river towards Calcutta.'),
    ('אאודה התחילה לדבר איתם ולהודות לפוג על האצילות שלו.', 'Aouda began to talk with them and to thank Fogg for his nobility.')),
  P(('אאודה שאלה: למה עשית את כל זה בשביל אישה שאתה לא מכיר?', 'Aouda asked: why did you do all this for a woman you do not know?'),
    ('פוג ענה בשקט: זה הדבר הנכון, והיה לנו זמן, זה הכול.', 'Fogg answered quietly: it is the right thing, and we had time, that is all.'),
    ('פספרטו היה גאה באדון שלו, כי הוא היה איש אמיץ וטוב.', 'Passepartout was proud of his master, because he was a brave and good man.'),
    ('עד עכשיו הם היו בזמן, והנסיעה הלכה יפה.', 'So far they were on time, and the journey was going well.'))]),

 ('The Court and the Bail', 'בית המשפט והערבות', [
  P(('הם הגיעו לכלכותה ושמחו שהספיקו לספינה להונג קונג.', 'They reached Calcutta and were glad they had made the ship to Hong Kong.'),
    ('אבל ברגע שירדו, המשטרה באה ועצרה את פוג ואת פספרטו.', 'But the moment they got off, the police came and arrested Fogg and Passepartout.'),
    ('הסיבה הייתה הצרה במקדש שקרתה בבומביי.', 'The reason was the trouble at the temple that had happened in Bombay.'),
    ('פיקס הוא זה שסידר את זה, כדי לעכב אותם עד שהצו יגיע.', 'Fix was the one who had arranged it, in order to delay them until the warrant arrived.')),
  P(('הם הגיעו לבית המשפט, והשופט נתן להם מאסר וקנס גדול.', 'They came to court, and the judge gave them prison and a big fine.'),
    ('פספרטו הצטער מאוד, כי הוא היה הסיבה לטעות שקרתה.', 'Passepartout was very sorry, because he was the cause of the mistake that had happened.'),
    ('אבל פוג נשאר רגוע ושילם את הקנס מיד, בלי לחשוב פעמיים.', 'But Fogg stayed calm and paid the fine at once, without thinking twice.'),
    ('הם יצאו מהר מבית המשפט ועלו על ספינה לכיוון הונג קונג.', 'They left the court quickly and boarded a ship towards Hong Kong.'))]),

 ("Fix Doesn't Understand", 'פיקס לא מבין', [
  P(('פיקס כעס מאוד, כי פוג ברח לו מהידיים עוד פעם.', 'Fix was very angry, because Fogg had slipped from his hands again.'),
    ('הוא עלה על אותה ספינה והמשיך להסתכל עליהם מרחוק.', 'He boarded the same ship and went on watching them from a distance.'),
    ('אבל הפעם פספרטו התחיל לחשוד בו קצת.', 'But this time Passepartout began to suspect him a little.'),
    ('הוא אמר לעצמו: למה האיש הזה איתנו בכל מקום? משהו פה לא בסדר.', 'He said to himself: why is this man with us everywhere? Something here is not right.')),
  P(('אאודה נהייתה חלק מהחבורה והתייחסה לפוג בחום ובנעימות.', 'Aouda had become part of the group and treated Fogg with warmth and kindness.'),
    ('אבל פוג נשאר שקט ולא הראה רגשות, ובכל זאת דאג לה בשקט.', 'But Fogg stayed quiet and showed no feelings, and yet cared for her in silence.'),
    ('פספרטו שם לב לזה וחייך לעצמו.', 'Passepartout noticed this and smiled to himself.'),
    ('הספינה המשיכה בדרך, ופיקס עוד היה בלי צו ומודאג.', 'The ship continued on its way, and Fix was still without a warrant and worried.'))]),

 ('Toward Hong Kong', 'בדרך להונג קונג', [
  P(('בדרך הספינה עצרה בעיר סינגפור לכמה שעות.', 'On the way the ship stopped in the city of Singapore for a few hours.'),
    ('פוג ואאודה יצאו לטיול קצר, והעיר הייתה ירוקה ויפה.', 'Fogg and Aouda went out for a short walk, and the city was green and lovely.'),
    ('פוג קטף פרח בשביל אאודה, וזה היה הדבר הרומנטי הראשון שהוא עשה.', 'Fogg picked a flower for Aouda, and this was the first romantic thing he did.'),
    ('הם חזרו לספינה והמשיכו בדרך להונג קונג.', 'They returned to the ship and continued on the way to Hong Kong.')),
  P(('אבל בדרך באה סופה חזקה ועיכבה את הספינה.', 'But on the way a strong storm came and delayed the ship.'),
    ('פספרטו התחיל לדאוג לזמן, אבל פוג נשאר רגוע כרגיל.', 'Passepartout began to worry about the time, but Fogg stayed calm as usual.'),
    ('פיקס דווקא היה מרוצה מהעיכוב.', 'Fix, on the other hand, was pleased with the delay.'),
    ('כי הונג קונג הייתה המקום האחרון ששייך לאנגליה, ושם הייתה ההזדמנות האחרונה שלו.', 'Because Hong Kong was the last place belonging to England, and there was his last chance.'))]),

 ('Each About His Business', 'כל אחד והעניין שלו', [
  P(('הם הגיעו להונג קונג, ופוג רצה להעביר את אאודה לקרוב משפחה שלה שם.', 'They reached Hong Kong, and Fogg wanted to hand Aouda over to a relative of hers there.'),
    ('פספרטו הלך לשאול על הקרוב הזה, וחזר עם חדשות רעות.', 'Passepartout went to ask about this relative, and came back with bad news.'),
    ('הקרוב עבר דירה מזמן והלך לגור באירופה.', 'The relative had moved long ago and gone to live in Europe.'),
    ('אז פוג אמר לאאודה: אם את רוצה, בואי איתנו ללונדון ושם תהיי בטוחה.', 'So Fogg said to Aouda: if you wish, come with us to London and there you will be safe.')),
  P(('אאודה הסכימה בשמחה, כי היא לא רצתה לעזוב אותם.', 'Aouda agreed gladly, because she did not want to leave them.'),
    ('באותו זמן פיקס היה קרוע מאוד.', 'At the same time Fix was very torn.'),
    ('הצו עוד לא הגיע, ופוג היה אמור לצאת מהונג קונג מחר.', 'The warrant had still not arrived, and Fogg was due to leave Hong Kong tomorrow.'),
    ('הוא החליט לעשות הכול כדי לעצור אותו, גם בדרך לא ישרה.', 'He decided to do anything to stop him, even by a crooked means.'))]),

 ('The Opium Den', 'בית האופיום', [
  P(('פיקס ניגש לפספרטו והחליט לספר לו את האמת.', 'Fix went up to Passepartout and decided to tell him the truth.'),
    ('הוא אמר: אני בלש, והאדון שלך חשוד בשוד בנק בלונדון.', 'He said: I am a detective, and your master is suspected of robbing a bank in London.'),
    ('פספרטו נבהל וכעס מאוד, ולא האמין למילה אחת.', 'Passepartout was shocked and very angry, and did not believe a single word.'),
    ('הוא אמר: האדון שלי איש ישר ואתה שקרן, ולא אתן לך לפגוע בו.', 'He said: my master is an honest man and you are a liar, and I will not let you harm him.')),
  P(('פיקס פחד שפספרטו יזהיר את פוג והם ייצאו מוקדם.', 'Fix was afraid that Passepartout would warn Fogg and that they would leave early.'),
    ('אז הוא לקח אותו למקום שמוכרים בו אופיום והזמין לו משקה.', 'So he took him to a place where they sold opium and ordered him a drink.'),
    ('פספרטו שתה בכעס בלי לשים לב, והיה בפנים סם שינה.', 'Passepartout drank in anger without noticing, and there was a sleeping drug in it.'),
    ('הראש שלו הסתובב, הוא נרדם על הרצפה ושכח הכול.', 'His head spun, he fell asleep on the floor and forgot everything.')),
  P(('אבל לפני שנרדם, פספרטו שמע ידיעה חשובה.', 'But before he fell asleep, Passepartout heard an important piece of news.'),
    ('הספינה ליפן תצא הערב ולא מחר.', 'The ship to Japan would leave this evening and not tomorrow.'),
    ('הוא רצה לספר לפוג, אבל הסם היה חזק ממנו.', 'He wanted to tell Fogg, but the drug was stronger than he was.'),
    ('הוא נשאר ישן, ופוג לא ידע שהספינה יוצאת מוקדם.', 'He stayed asleep, and Fogg did not know that the ship was leaving early.'))]),

 ('Fix Confronts Fogg', 'פיקס מול פוג', [
  P(('בבוקר פוג התעורר ולא מצא את פספרטו בשום מקום.', 'In the morning Fogg woke and did not find Passepartout anywhere.'),
    ('הוא הלך עם אאודה לנמל, אבל הספינה יצאה בלילה.', 'He went with Aouda to the port, but the ship had left in the night.'),
    ('הוא לא כעס ואמר בשקט: אנחנו חייבים למצוא דרך אחרת.', 'He did not get angry and said quietly: we must find another way.'),
    ('הוא חיפש בנמל עד שמצא סירה קטנה ומהירה.', 'He searched the port until he found a small, fast boat.')),
  P(('הוא סיכם עם בעל הסירה שייקח אותו ואת אאודה ליפן.', 'He agreed with the boat’s owner to take him and Aouda to Japan.'),
    ('ברגע האחרון פיקס בא וביקש לעלות איתם.', 'At the last moment Fix came and asked to come aboard with them.'),
    ('פוג הסכים, בלי לדעת מי הוא באמת.', 'Fogg agreed, without knowing who he really was.'),
    ('פיקס היה קרוע: הוא רצה שפוג יגיע לאנגליה כדי לעצור אותו, אבל לא מהר מדי.', 'Fix was torn: he wanted Fogg to reach England so he could arrest him, but not too fast.'))]),

 ('The Storm', 'הסופה', [
  P(('הסירה הקטנה יצאה לים הפתוח, ובהתחלה מזג האוויר היה יפה.', 'The small boat set out on the open sea, and at first the weather was fine.'),
    ('אבל באמצע הדרך באה סופה גדולה וחזקה.', 'But in the middle of the way a big, strong storm came.'),
    ('הגלים נהיו כמו הרים, והסירה זזה בכוח למעלה ולמטה.', 'The waves became like mountains, and the boat moved violently up and down.'),
    ('כולם פחדו, אבל פוג נשאר עומד ורגוע בלי פחד.', 'Everyone was afraid, but Fogg stayed standing and calm without fear.')),
  P(('בעל הסירה אמר: אנחנו חייבים לעצור, אחרת כולנו נטבע.', 'The boat’s owner said: we must stop, or we will all drown.'),
    ('אבל פוג הציע לו כסף נוסף כדי להמשיך בכל דרך.', 'But Fogg offered him extra money to continue by any means.'),
    ('בעל הסירה התפתה לפרס והחליט להמשיך למרות הסכנה.', 'The owner was tempted by the reward and decided to continue despite the danger.'),
    ('אחרי ימים קשים הסופה נרגעה והם הגיעו קרוב ליפן.', 'After hard days the storm calmed and they came near Japan.')),
  P(('אבל עכשיו הם היו צריכים למצוא את פספרטו שאבד להם בהונג קונג.', 'But now they had to find Passepartout, who had been lost to them in Hong Kong.'),
    ('אאודה דאגה לו, כי היא אהבה אותו כמו אח.', 'Aouda worried about him, because she loved him like a brother.'),
    ('פוג אמר: נמצא אותו, אל תפחדי.', 'Fogg said: we will find him, do not be afraid.'),
    ('הם הגיעו לעיר יוקוהמה והתחילו לחפש אותו.', 'They reached the city of Yokohama and started looking for him.'))]),

 ('Passepartout in Japan', 'פספרטו ביפן', [
  P(('נחזור לפספרטו, שהתעורר מהשינה על הספינה.', 'Let us go back to Passepartout, who woke from his sleep on the ship.'),
    ('התברר שבזמן שהראש שלו הסתובב מישהו עזר לו והעלה אותו לספינה בטעות.', 'It turned out that while his head was spinning someone helped him and put him on the ship by mistake.'),
    ('הספינה לקחה אותו ליפן בזמן שהוא ישן, בלי האדון שלו.', 'The ship took him to Japan while he slept, without his master.'),
    ('הוא הגיע ליוקוהמה בלי מטבע אחד בכיס.', 'He reached Yokohama without a single coin in his pocket.')),
  P(('הוא היה רעב ועייף, ולא ידע מה לעשות בארץ זרה.', 'He was hungry and tired, and did not know what to do in a strange land.'),
    ('הוא מכר כמה מהבגדים שלו כדי לאכול ולהמשיך לחיות.', 'He sold some of his clothes in order to eat and go on living.'),
    ('הוא לבש בגדים יפניים מוזרים והלך לשוטט ברחובות.', 'He put on strange Japanese clothes and went wandering the streets.'),
    ('הוא היה עצוב, אבל עוד הייתה לו תקווה למצוא את האדון שלו.', 'He was sad, but he still had hope of finding his master.'))]),

 ("Passepartout's Long Nose", 'האף הארוך של פספרטו', [
  P(('פספרטו מצא קבוצת קרקס שעשתה הצגות לאנשים.', 'Passepartout found a circus troupe that put on shows for people.'),
    ('הוא עבד איתם כדי לאכול, והיה חלק מהצגה גדולה ומפורסמת.', 'He worked with them in order to eat, and was part of a big, famous show.'),
    ('קראו להצגה האפים הארוכים, והשחקנים לבשו אפים ארוכים ומצחיקים.', 'The show was called the Long Noses, and the performers wore long, funny noses.'),
    ('הם היו בונים מגדל גדול של אנשים שעומדים אחד על השני.', 'They used to build a big tower of people standing one on top of the other.')),
  P(('פספרטו היה למטה במגדל, כי הוא היה חזק ויכול לשאת את המשקל.', 'Passepartout was at the bottom of the tower, because he was strong and could bear the weight.'),
    ('הוא עשה תנועות מצחיקות, והאנשים צחקו ושמחו.', 'He made funny movements, and the people laughed and enjoyed it.'),
    ('אבל בפנים הוא חשב רק על האדון שלו ואיפה הוא נמצא.', 'But inside he thought only of his master and where he was.'),
    ('הוא לא ידע שפוג הגיע ליוקוהמה ומחפש אותו.', 'He did not know that Fogg had reached Yokohama and was looking for him.'))]),

 ('The Reunion', 'המפגש', [
  P(('באותו יום פוג ואאודה חיפשו את פספרטו בכל מקום.', 'That same day Fogg and Aouda were looking for Passepartout everywhere.'),
    ('במקרה הם הלכו לראות את הצגת הקרקס כדי לנוח קצת.', 'By chance they went to see the circus show in order to rest a little.'),
    ('הם ישבו בין האנשים ולא ידעו שפספרטו נמצא שם.', 'They sat among the people and did not know that Passepartout was there.'),
    ('ופתאום פספרטו ראה את האדון שלו בין הצופים.', 'And suddenly Passepartout saw his master among the spectators.')),
  P(('מרוב שמחה הוא שכח את עצמו ועזב את המקום שלו במגדל.', 'From sheer joy he forgot himself and left his place in the tower.'),
    ('כל המגדל נפל, והיה בלגן ומחזה מצחיק.', 'The whole tower fell, and there was chaos and a funny scene.'),
    ('פספרטו רץ לאדון שלו וחיבק אותו באושר.', 'Passepartout ran to his master and hugged him in delight.'),
    ('גם אאודה שמחה מאוד, כי היא פחדה בשבילו.', 'Aouda too was very glad, because she had been afraid for him.')),
  P(('פוג נרגע כשמצא את המשרת שלו בשלום, אבל לא הראה הרבה רגשות.', 'Fogg was relieved to find his servant safe, but did not show much feeling.'),
    ('פספרטו שילם לקרקס על המגדל שנפל.', 'Passepartout paid the circus for the tower that fell.'),
    ('כולם יצאו לדרך יחד, עם פיקס, ועלו על ספינה גדולה לאמריקה.', 'They all set out together, with Fix, and boarded a big ship for America.'),
    ('הספינה הייתה גדולה ומלאה נוסעים מכל העולם.', 'The ship was big and full of passengers from all over the world.'))]),

 ('Crossing the Pacific', 'חוצים את האוקיינוס', [
  P(('הספינה עברה את האוקיינוס השקט, שהיה עצום וארוך בלי סוף.', 'The ship crossed the Pacific Ocean, which was vast and endlessly long.'),
    ('פוג המשיך לספור את הימים בדיוק, והוא עוד היה בזמן.', 'Fogg went on counting the days exactly, and he was still on time.'),
    ('הרגשות של אאודה כלפי פוג נהיו חזקים יותר, אבל היא לא אמרה כלום.', 'Aouda’s feelings for Fogg grew stronger, but she said nothing.'),
    ('היא הסתכלה עליו בשקט והתפלאה על הלב הטוב מתחת לפנים הקרות.', 'She watched him quietly and marvelled at the kind heart beneath the cold face.')),
  P(('פספרטו חשד בפיקס יותר ויותר והחליט להסתכל עליו.', 'Passepartout suspected Fix more and more and decided to watch him.'),
    ('הוא אמר לעצמו: האיש הזה הולך אחרינו מסיבה, אבל מאיזו סיבה?', 'He said to himself: this man follows us for a reason, but for what reason?'),
    ('הוא עוד לא חיבר את החלקים יחד.', 'He had not yet put the pieces together.'),
    ('ובלי שידעו, כשעברו את האוקיינוס, הם הרוויחו יום שלם בחשבון.', 'And without their knowing, as they crossed the ocean, they gained a whole day in the reckoning.'))]),

 ('A Glimpse of San Francisco', 'הצצה בסן פרנסיסקו', [
  P(('הם הגיעו לעיר סן פרנסיסקו באמריקה, עיר גדולה וחיה.', 'They reached the city of San Francisco in America, a big and lively city.'),
    ('הם הלכו לקבל חותמת על הדרכונים ואחר כך לטייל ברחוב.', 'They went to get a stamp on their passports and afterwards to walk in the street.'),
    ('אבל הייתה שם הפגנה פוליטית גדולה ופרצה מכה בין האנשים.', 'But there was a big political demonstration there and a brawl broke out among the people.'),
    ('פוג ופיקס נתפסו באמצע, ואנשים דחפו והכו.', 'Fogg and Fix were caught in the middle, and people pushed and hit.')),
  P(('איש גדול ניסה להכות את פוג, אבל פיקס עמד מולו וקיבל את המכה.', 'A big man tried to hit Fogg, but Fix stood in front of him and took the blow.'),
    ('פוג הודה לו ואמר: אני אחזיר לך את הטובה יום אחד.', 'Fogg thanked him and said: I will repay you the favour one day.'),
    ('הם יצאו מהמכות בשלום, והבגדים שלהם לא היו מסודרים.', 'They got out of the brawl safely, and their clothes were not in good order.'),
    ('אחר כך הלכו לתחנה ועלו על הרכבת הגדולה שחוצה את אמריקה.', 'Afterwards they went to the station and boarded the great train that crosses America.'))]),

 ('Aboard the Pacific Railroad', 'ברכבת הגדולה', [
  P(('הרכבת יצאה מסן פרנסיסקו לכיוון ניו יורק במזרח.', 'The train left San Francisco towards New York in the east.'),
    ('הדרך הייתה ארוכה מאוד ועברה הרים, מישורים, מדבר ונהרות.', 'The route was very long and crossed mountains, plains, desert and rivers.'),
    ('פספרטו הסתכל מהחלון על ארץ גדולה ומוזרה.', 'Passepartout looked from the window at a big, strange land.'),
    ('הכול היה עצום: האדמה, השמיים והמרחקים בלי סוף.', 'Everything was vast: the land, the sky and the endless distances.')),
  P(('פוג נשאר במקום שלו ושיחק קלפים כרגיל.', 'Fogg stayed in his seat and played cards as usual.'),
    ('אאודה ישבה לידו, והם התחילו לדבר לאט לאט.', 'Aouda sat beside him, and they began to talk little by little.'),
    ('פספרטו היה מרוצה, אבל העין שלו הייתה תמיד על פיקס.', 'Passepartout was pleased, but his eye was always on Fix.'),
    ('הם עוד היו בזמן, אבל בדרך חיכו להם הרבה הפתעות.', 'They were still on time, but many surprises were waiting for them on the way.'))]),

 ('A Story Along the Way', 'סיפור בדרך', [
  P(('בדרך עלה איש לרכבת והתחיל לספר לאנשים על ההיסטוריה של הארץ.', 'On the way a man got on the train and began telling people about the history of the country.'),
    ('פספרטו ישב והקשיב, והכול היה חדש ומוזר בשבילו.', 'Passepartout sat and listened, and everything was new and strange to him.'),
    ('הוא למד קצת על האנשים שחיו בארץ הענקית הזאת.', 'He learned a little about the people who lived in this enormous land.'),
    ('אבל זה לא נמשך הרבה, כי הרכבת תמיד מיהרה.', 'But it did not last long, because the train was always in a hurry.')),
  P(('פוג לא שם לב לסיפורים, והעניין שלו היה רק זמן ומרחק.', 'Fogg paid no attention to the stories, and his concern was only time and distance.'),
    ('כל שעה הוא הסתכל במפה וחישב איפה הם נמצאים.', 'Every hour he looked at the map and worked out where they were.'),
    ('הם היו קצת לפני הזמן, וזה שימח את פספרטו.', 'They were a little ahead of time, and this pleased Passepartout.'),
    ('אבל הרכבת התקרבה למקום עם הרבה צרות.', 'But the train was drawing near to a place with a lot of trouble.'))]),

 ('Buffalo on the Track', 'עדר על המסילה', [
  P(('פתאום הרכבת עצרה, והם ירדו לראות מה קרה.', 'Suddenly the train stopped, and they got off to see what had happened.'),
    ('עדר ענק של בקר בר עבר על המסילה, אלפים על אלפים.', 'A huge herd of wild cattle was crossing the track, thousands upon thousands.'),
    ('לא היה מה לעשות חוץ מלחכות עד שיגמרו לעבור.', 'There was nothing to do but wait until they finished crossing.'),
    ('הם עברו שעות ארוכות, והרכבת עמדה במקום.', 'They crossed for long hours, and the train stood still.')),
  P(('פספרטו יצא מדעתו מכעס על העיכוב הזה.', 'Passepartout went out of his mind with anger at this delay.'),
    ('הוא צעק והניף את הידיים, אבל העדר לא שם לב אליו.', 'He shouted and waved his arms, but the herd paid him no attention.'),
    ('פוג נשאר רגוע במקום שלו בלי שום דאגה.', 'Fogg stayed calm in his seat without any care.'),
    ('בסוף העדר נגמר, והרכבת המשיכה בדרך.', 'In the end the herd finished, and the train continued on its way.'))]),

 ('The Broken Bridge', 'הגשר החלש', [
  P(('אחרי זמן מה הרכבת הגיעה לגשר ישן וחלש מעל נהר עמוק.', 'After some time the train reached an old, weak bridge over a deep river.'),
    ('הנהג פחד ואמר: הגשר לא חזק והוא עלול ליפול תחת המשקל.', 'The driver was afraid and said: the bridge is not strong and it may fall under the weight.'),
    ('פרץ ויכוח בין הנוסעים: לחכות או לנסות לעבור?', 'An argument broke out among the passengers: wait, or try to cross?'),
    ('אחד הציע רעיון אמיץ: לעבור במהירות הכי גבוהה, כדי שהרכבת לא תלחץ על הגשר.', 'One suggested a bold idea: to cross at the highest speed, so the train would not press on the bridge.')),
  P(('הרכבת חזרה אחורה ואז רצה קדימה במהירות מטורפת.', 'The train backed up and then rushed forward at a mad speed.'),
    ('כולם עצרו את הנשימה מפחד בזמן המעבר.', 'Everyone held their breath in fear during the crossing.'),
    ('הרכבת עברה את הגשר בשלום, ורגע אחרי שעברה הגשר נפל לנהר.', 'The train crossed the bridge safely, and a moment after it passed the bridge fell into the river.'),
    ('כולם נרגעו, ופספרטו ניגב את הזיעה מהמצח.', 'Everyone was relieved, and Passepartout wiped the sweat from his forehead.'))]),

 ('Fogg Does His Duty', 'פוג עושה את שלו', [
  P(('בזמן הנסיעה קבוצה של אנשים התנפלה על הרכבת.', 'During the journey a group of men attacked the train.'),
    ('פרץ קרב ופחד גדול עבר בין הנוסעים.', 'A fight broke out and great fear passed among the passengers.'),
    ('פוג, פיקס ופספרטו נלחמו יחד עם האנשים כדי להגן על עצמם.', 'Fogg, Fix and Passepartout fought together with the people to defend themselves.'),
    ('פוג היה אמיץ, והוא נלחם בשקט ובלי פחד.', 'Fogg was brave, and he fought calmly and without fear.')),
  P(('פספרטו היה גיבור: הוא זחל מתחת לקרונות כדי לעצור את הרכבת.', 'Passepartout was a hero: he crawled under the carriages in order to stop the train.'),
    ('הוא הצליח לעצור אותה, וכך הציל את הנוסעים מסכנה.', 'He managed to stop it, and so saved the passengers from danger.'),
    ('אבל בזמן ההתקפה הוא וכמה נוסעים אחרים נלקחו בכוח.', 'But during the attack he and a few other passengers were taken by force.'),
    ('כשהרכבת עצרה, גילו שפספרטו נלקח.', 'When the train stopped, they discovered that Passepartout had been taken.'))]),

 ('Fix Takes Charge', 'פיקס לוקח אחריות', [
  P(('פוג אמר: אני לא אסע מכאן בלי המשרת שלי.', 'Fogg said: I will not travel on from here without my servant.'),
    ('הוא ביקש מהקצינים שייתנו לו חיילים כדי לחפש את פספרטו.', 'He asked the officers to give him soldiers in order to look for Passepartout.'),
    ('פוג הלך בעצמו עם החיילים בשלג ובקור.', 'Fogg went himself with the soldiers through the snow and the cold.'),
    ('אאודה נשארה ודאגה להם מאוד.', 'Aouda stayed behind and worried about them greatly.')),
  P(('פיקס רצה לעצור את פוג, אבל עכשיו הוא הרגיש שהוא חייב לעזור לו.', 'Fix wanted to arrest Fogg, but now he felt he had to help him.'),
    ('הוא אמר לאאודה: אני אחכה לפוג כאן, אל תפחדי.', 'He said to Aouda: I will wait for Fogg here, do not be afraid.'),
    ('אחרי שעות פוג חזר, והוא הציל את פספרטו ואת האחרים.', 'After hours Fogg came back, and he had saved Passepartout and the others.'),
    ('אאודה שמחה, אבל הרכבת כבר יצאה לדרך.', 'Aouda was glad, but the train had already set off.'))]),

 ('Fogg Fights Ill Fortune', 'פוג נלחם במזל הרע', [
  P(('עכשיו הם היו מאחור, הזמן ברח, וההימור היה בסכנה.', 'Now they were behind, the time was running away, and the bet was in danger.'),
    ('הם מצאו איש עם מזחלת שנוסעת על השלג בכוח הרוח ומפרש.', 'They found a man with a sledge that travels on the snow by the power of the wind and a sail.'),
    ('הם עלו עליה, והיא רצה מהר על השלג הלבן.', 'They got on it, and it ran fast over the white snow.'),
    ('הקור היה נורא, אבל לא היה זמן לנוח.', 'The cold was terrible, but there was no time to rest.')),
  P(('המזחלת עפה על השלג כמו ציפור.', 'The sledge flew over the snow like a bird.'),
    ('הם הגיעו לתחנת רכבת אחרת מהר ממה שחיכו.', 'They reached another railway station faster than they expected.'),
    ('הם עלו שוב על רכבת בדרך לעיר ניו יורק.', 'They boarded a train again on the way to the city of New York.'),
    ('פוג חישב את הזמן, ועוד הייתה תקווה קטנה.', 'Fogg worked out the time, and there was still a small hope.'))]),

 ('Fogg Equal to the Occasion', 'פוג עומד במבחן', [
  P(('הם הגיעו לניו יורק ורצו לנמל מהר ככל שיכלו.', 'They reached New York and rushed to the port as fast as they could.'),
    ('אבל הספינה לאירופה יצאה רק קצת לפניהם.', 'But the ship to Europe had left only a little before them.'),
    ('שוב הם איחרו את הספינה בכמה דקות.', 'Again they missed the ship by a few minutes.'),
    ('פספרטו הרגיש אשם, כי כל העיכוב הזה היה בגללו.', 'Passepartout felt guilty, because all this delay was on his account.')),
  P(('אבל פוג לא ויתר והלך לחפש ספינה אחרת.', 'But Fogg did not give up and went to look for another ship.'),
    ('הוא מצא ספינה קטנה, אבל הבעלים שלה לא רצה לנסוע לאנגליה.', 'He found a small ship, but its owner did not want to travel to England.'),
    ('פוג הציע לו הרבה כסף, והאיש עוד סירב.', 'Fogg offered him a lot of money, and the man still refused.'),
    ('פוג סיכם איתו רק על נסיעה לצרפת, והם עלו על הספינה.', 'Fogg agreed with him only on a journey to France, and they boarded the ship.'))]),

 ('Burning the Ship', 'שורפים את הספינה', [
  P(('באמצע הדרך פוג שילם למלחים כדי שישמעו לו ולא לבעלים.', 'Midway, Fogg paid the sailors so that they would obey him and not the owner.'),
    ('הם סגרו את הבעלים בחדר שלו, ופוג נהיה אחראי על הספינה.', 'They shut the owner in his cabin, and Fogg became in charge of the ship.'),
    ('הוא הפנה את הספינה לכיוון אנגליה, והזמן נגמר.', 'He turned the ship towards England, and the time was running out.'),
    ('הוא היה חייב להגיע מהר ככל האפשר, בכל מחיר.', 'He had to arrive as fast as possible, at any price.')),
  P(('אבל בדרך נגמר הפחם שמפעיל את הספינה.', 'But on the way the coal that drives the ship ran out.'),
    ('אז פוג אמר להם לשרוף את העץ של הספינה עצמה כדי להמשיך.', 'So Fogg told them to burn the ship’s own wood in order to continue.'),
    ('הם שרפו כל דבר מעץ: את הכיסאות, את הדלתות ואת הרצפה.', 'They burned everything wooden: the chairs, the doors and the deck.'),
    ('בסוף נשאר רק הברזל, והם הגיעו לחוף של אנגליה.', 'In the end only the iron was left, and they reached the shore of England.'))]),

 ('The Arrest', 'המעצר', [
  P(('הם הגיעו לנמל אנגלי, ופוג שמח שעוד יש זמן.', 'They reached an English port, and Fogg was glad there was still time.'),
    ('אבל ברגע שירד, פיקס בא ושם את היד על הכתף שלו.', 'But the moment he got off, Fix came and put his hand on his shoulder.'),
    ('הוא אמר: בשם החוק, אתה עצור.', 'He said: in the name of the law, you are under arrest.'),
    ('הפעם הצו הרשמי הגיע, אז שמו את פוג בבית הסוהר.', 'This time the official warrant had arrived, so they put Fogg in prison.')),
  P(('פספרטו יצא מדעתו מכעס, כשהבין שפיקס הוא זה שעצר אותם כל הזמן.', 'Passepartout went out of his mind with anger, when he understood that Fix was the one stopping them all along.'),
    ('אאודה הייתה עצובה מאוד והרגישה שהכול אבוד.', 'Aouda was very sad and felt that everything was lost.'),
    ('פוג נשאר רגוע בבית הסוהר, אבל בפנים ידע שהזמן הולך.', 'Fogg stayed calm in prison, but inside he knew the time was going.'),
    ('כל דקה בבית הסוהר הייתה צעד אחד להפסד בהימור.', 'Every minute in prison was one more step towards losing the bet.'))]),

 ('Fogg Innocent', 'פוג חף מפשע', [
  P(('אחרי שעות בבית הסוהר הדלת נפתחה פתאום.', 'After hours in prison the door suddenly opened.'),
    ('פיקס נכנס נבוך ואמר: תסלח לי, אדוני.', 'Fix came in embarrassed and said: forgive me, sir.'),
    ('התברר שהגנב האמיתי נתפס כבר לפני כמה ימים בלונדון.', 'It turned out that the real thief had been caught days ago in London.'),
    ('פוג היה נקי, ולא היה לו שום קשר לשוד.', 'Fogg was innocent, and had no connection at all to the robbery.')),
  P(('פוג בפעם הראשונה בחיים שלו איבד את הסבלנות והכה את פיקס מכה אחת.', 'For the first time in his life Fogg lost his patience and struck Fix a single blow.'),
    ('ואז הוא נרגע שוב, ומיד הלך מהר עם אאודה ועם פספרטו.', 'And then he calmed again, and at once went quickly with Aouda and with Passepartout.'),
    ('הם לקחו רכבת מיוחדת ונסעו מהר ככל שיכלו ללונדון.', 'They took a special train and travelled as fast as they could to London.'),
    ('אבל כשהגיעו הזמן כבר עבר, ופוג הרגיש שהפסיד את ההימור.', 'But when they arrived the time had already passed, and Fogg felt that he had lost the bet.'))]),

 ('Fogg Wins Happiness', 'פוג זוכה באושר', [
  P(('פוג חזר הביתה רגוע, אבל בפנים הוא היה עצוב מאוד.', 'Fogg came home calm, but inside he was very sad.'),
    ('הוא הרגיש שהוא איבד הכול: את הכסף, את ההימור ואת כל המאמץ.', 'He felt that he had lost everything: the money, the bet and all the effort.'),
    ('הוא ישב לבד בחדר החשוך ולא רצה לראות אף אחד.', 'He sat alone in the dark room and did not want to see anyone.'),
    ('אבל אאודה דפקה על הדלת, והיא ישבה לידו.', 'But Aouda knocked on the door, and she sat beside him.')),
  P(('אאודה אמרה: אדוני, גם אני איבדתי הכול, אבל עכשיו יש לי אותך.', 'Aouda said: sir, I too lost everything, but now I have you.'),
    ('היא אמרה בביישנות: תתחתן איתי? אני אוהבת אותך.', 'She said shyly: will you marry me? I love you.'),
    ('בפעם הראשונה עלתה שמחה על הפנים של פוג.', 'For the first time joy rose on Fogg’s face.'),
    ('הוא אמר: גם אני אוהב אותך, וזה הדבר היקר ביותר שזכיתי בו בנסיעה.', 'He said: I love you too, and this is the most precious thing I won on this journey.'),
    ('הוא שלח מיד את פספרטו לסדר את החתונה.', 'He sent Passepartout at once to arrange the wedding.')),
  P(('פספרטו רץ, ואחרי זמן קצר חזר בריצה וצעק.', 'Passepartout ran off, and a short time later came running back and shouted.'),
    ('הוא אמר: אדוני, יש טעות בחשבון, היום זה לא ראשון אלא שבת.', 'He said: sir, there is a mistake in the reckoning, today is not Sunday but Saturday.'),
    ('כי הם נסעו מסביב לכדור הארץ מזרחה, והרוויחו יום שלם בלי לשים לב.', 'Because they had travelled round the globe eastwards, and had gained a whole day without noticing.'),
    ('עוד היה זמן, ואפשר היה עוד לזכות בהימור.', 'There was still time, and the bet could still be won.')),
  P(('פוג רץ למועדון מהר ככל שיכול, וכולם חיכו לו שם.', 'Fogg ran to the club as fast as he could, and everyone was waiting for him there.'),
    ('הוא נכנס בדלת בשנייה האחרונה, בדיוק לפני שהזמן נגמר.', 'He came through the door at the last second, exactly before the time ran out.'),
    ('הוא זכה בהימור וקיבל את עשרים אלף הלירות.', 'He won the bet and received the twenty thousand pounds.'),
    ('אבל יותר מההימור, הוא זכה באאודה והיה מאושר בפעם הראשונה.', 'But more than the bet, he won Aouda and was happy for the first time.'),
    ('וכך האיש ששמר על סדר ולא הכיר אהבה עבר את כדור הארץ ומצא את הלב שלו.', 'And so the man who kept order and had never known love crossed the globe and found his heart.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('atw80', {'en': 'Around the World in 80 Days',
                                    'he': 'מסביב לעולם בשמונים יום'}, 'intermediate',
                          CHAPTERS, unit='Chapter', unit_he='פרק', shelf=10, meta=META))
