#!/usr/bin/env python3
"""שרלוק הולמס: עשרה סיפורים — Conan Doyle, retold in modern Hebrew, graded to advanced.

The Hebrew twin of pipeline/book_holmes.py: ten stories in thirty chapters, three chapters
each, the same ten the Arabic shelf carries. All of Holmes entered the public domain by 2023,
and these are retellings from the plots rather than translations of any edition.

WHY IT OPENS THE ADVANCED SHELF. A detective story is the only popular form that REQUIRES the
reader to hold two accounts of the same events at once — what appears to have happened and what
did — and holding two things at once is exactly what advanced Hebrew asks of you
grammatically. The sentences here run long on purpose and hang clauses off each other, because
a reader who can follow Holmes explaining himself can follow a newspaper leader.

Deliberately unpointed; the vowels are looked up at ingest. The names are declared in
pipeline/he_curated.py.

Run:  python3 pipeline/he_book_holmes.py --lang he            # check
      python3 pipeline/he_book_holmes.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'the Sherlock Holmes stories', 'author': 'Arthur Conan Doyle',
        'year': '1891–1904',
        'status': 'public domain — all Holmes entered the US public domain by 2023'}

CHAPTERS = [
 ('The King Who Would Not Say His Name', 'המלך שלא רצה לומר את שמו', [
  P(('בערב אחד ישבתי אצל שרלוק הולמס ברחוב בייקר, וקראנו בשקט כל אחד את העיתון שלו.', 'One evening I was sitting with Sherlock Holmes in Baker Street, and each of us was quietly reading his own paper.'),
    ('הולמס הרים את הראש ואמר שמישהו יעלה במדרגות בעוד רגע, כי שמע כרכרה עוצרת למטה.', 'Holmes raised his head and said that someone would come up the stairs in a moment, because he had heard a carriage stop below.'),
    ('בדלת עמד איש גבוה מאוד, לבוש יקר, ועל הפנים שלו הייתה מסכה שחורה.', 'In the doorway stood a very tall man, expensively dressed, and on his face was a black mask.')),
  P(('האיש אמר שהוא בא בשם אדם חשוב מאוד, ושהוא לא יכול לומר את השם שלו.', 'The man said that he had come on behalf of a very important person, and that he could not say his name.'),
    ('הולמס חייך ואמר שהוא מדבר עם מלך בוהמיה, ואפשר להוריד את המסכה.', 'Holmes smiled and said that he was speaking to the King of Bohemia, and that the mask could come off.'),
    ('המלך הוריד את המסכה, ישב, ואמר שהוא בצרה גדולה מאוד.', 'The King took off the mask, sat down, and said that he was in very great trouble.')),
  P(('הוא סיפר שלפני שנים הכיר אישה בשם אירן אדלר, והם היו יחד תקופה.', 'He told them that years before he had known a woman called Irene Adler, and that they had been together for a time.'),
    ('עכשיו הוא עומד להתחתן, ואם משהו מהתקופה ההיא ייצא לאור, הכול ייגמר.', 'Now he was about to marry, and if anything from that time came to light, everything would be over.'),
    ('הולמס שאל מה בדיוק יש לה בידיים, ולמלך היה קשה מאוד לענות.', 'Holmes asked what exactly she had in her hands, and the King found it very hard to answer.'),
    ('בסוף הוא אמר שיש לה תמונה של שניהם יחד.', 'In the end he said that she had a photograph of the two of them together.'))]),

 ('A Photograph in Someone Else’s Hands', 'תמונה בידיים של מישהי אחרת', [
  P(('הולמס שאל אם ניסו לקנות את התמונה, והמלך אמר שניסו הכול ולא הצליחו.', 'Holmes asked whether they had tried to buy the photograph, and the King said they had tried everything and failed.'),
    ('אנשים שלו נכנסו לבית שלה פעמיים, חיפשו בכל מקום, ולא מצאו כלום.', 'His men had entered her house twice, searched everywhere, and found nothing.'),
    ('הולמס אמר שאם היא לא מחביאה את התמונה רחוק, סימן שהיא רוצה אותה קרוב.', 'Holmes said that if she was not hiding the photograph far away, it meant she wanted it close at hand.')),
  P(('בבוקר הולמס יצא מהבית לבוש כמו עובד פשוט, ואני לא הכרתי אותו בכלל.', 'In the morning Holmes left the house dressed like a simple workman, and I did not recognise him at all.'),
    ('הוא חזר אחרי שעות, ישב בכיסא, וסיפר לי מה שמע ברחוב שלה.', 'He came back hours later, sat in his chair, and told me what he had heard in her street.'),
    ('אנשי המקום סיפרו לו הכול על האישה הזאת, כי איש עם בגדים כאלה לא מפחיד אף אחד.', 'The local people had told him everything about that woman, because a man in such clothes frightens nobody.')),
  P(('הוא סיפר שראה אותה נוסעת לכנסייה, ושהיא התחתנה שם באותו יום עם עורך דין צעיר.', 'He told me that he had seen her drive to a church, and that she had married a young lawyer there that same day.'),
    ('הולמס עצמו עמד שם כעד, כי חסר להם אדם אחד ברגע האחרון.', 'Holmes himself had stood there as a witness, because at the last moment they were one person short.'),
    ('הוא אמר שזה משנה הכול, כי אישה נשואה כבר לא צריכה את התמונה כמו קודם.', 'He said that this changed everything, because a married woman no longer needs the photograph as she did before.'))]),

 ('The Woman Who Was Ahead of Him', 'האישה שהייתה לפניו', [
  P(('בערב הולמס לבש בגדים של איש דת זקן, וביקש ממני לעמוד מתחת לחלון שלה.', 'In the evening Holmes dressed as an old clergyman, and asked me to stand under her window.'),
    ('הוא סידר שאנשים ברחוב יריבו בדיוק כשהיא נכנסת, והוא נכנס באמצע לעזור.', 'He arranged for people in the street to quarrel just as she arrived, and he went in among them to help.'),
    ('הוא נפל על האדמה כאילו נפגע, והאישה הכניסה אותו הביתה מיד.', 'He fell to the ground as if he had been hurt, and the woman brought him into the house at once.')),
  P(('כשנתתי את הסימן, זרקתי פנימה משהו שעשה עשן, וצעקתי שיש אש בבית.', 'When I gave the signal, I threw in something that made smoke, and shouted that there was a fire in the house.'),
    ('הולמס אמר לי אחר כך שאישה במצב כזה רצה קודם כול אל הדבר היקר לה ביותר.', 'Holmes told me afterwards that a woman in such a moment runs first of all to the thing dearest to her.'),
    ('היא רצה לקיר, פתחה דלת קטנה, והוא ראה בדיוק איפה התמונה נמצאת.', 'She ran to the wall, opened a small door, and he saw exactly where the photograph was.')),
  P(('בבוקר הלכנו לשם עם המלך, אבל הבית כבר היה ריק והיא נסעה בלילה.', 'In the morning we went there with the King, but the house was already empty and she had left in the night.'),
    ('במקום התמונה היה מכתב אליו, ובו כתבה שהיא הבינה מי היה איש הדת.', 'In place of the photograph was a letter to him, in which she wrote that she had understood who the clergyman was.'),
    ('היא כתבה שהיא לא תשתמש בתמונה לעולם, כי היא אוהבת את הבעל שלה.', 'She wrote that she would never use the photograph, because she loved her husband.'),
    ('מאותו יום הולמס קרא לה רק האישה, ולא בשם אחר.', 'From that day Holmes called her only the woman, and by no other name.'))]),

 ('A Job for Red-Haired Men Only', 'עבודה רק לאדומי שיער', [
  P(('יום אחד בא אלינו איש שמן עם שיער אדום מאוד, והוא היה כועס ומבולבל.', 'One day a stout man with very red hair came to us, and he was angry and confused.'),
    ('הוא סיפר שיש לו חנות קטנה, ושהעובד שלו הראה לו מודעה מוזרה בעיתון.', 'He told us that he had a small shop, and that his assistant had shown him a strange advertisement in the paper.'),
    ('במודעה כתבו שמשלמים כסף טוב לאנשים עם שיער אדום, ורק להם.', 'The advertisement said that good money was paid to men with red hair, and to them only.')),
  P(('הוא הלך לשם, ומצא תור ארוך של אנשים אדומי שיער מכל העיר.', 'He went there, and found a long queue of red-haired men from all over the city.'),
    ('בחרו דווקא בו, ואמרו לו לבוא כל בוקר ולהעתיק ספרים בחדר ריק.', 'They chose him of all people, and told him to come every morning and copy books in an empty room.'),
    ('הוא ישב שם שמונה שבועות, קיבל כסף כל שבוע, ולא הבין למה.', 'He sat there for eight weeks, received money every week, and did not understand why.')),
  P(('באותו בוקר הוא הגיע ומצא את הדלת סגורה ופתק קטן עליה.', 'That morning he had arrived and found the door shut and a small note on it.'),
    ('בפתק היה כתוב שהעניין נגמר, בלי מילה נוספת.', 'On the note it was written that the matter was closed, without another word.'),
    ('הולמס הקשיב עד הסוף, ואז שאל שאלה אחת: כמה משלם לך העובד שלך.', 'Holmes listened to the end, and then asked one question: how much does your assistant pay you.'))]),

 ('Who Wanted Him Out of the Shop', 'מי רצה אותו מחוץ לחנות', [
  P(('האיש ענה שהעובד לא משלם לו, אלא להפך: הוא מוכן לעבוד בחצי מחיר.', 'The man answered that the assistant did not pay him, but the opposite: he was willing to work for half wages.'),
    ('הולמס הסתכל עליי ואמר שזה הדבר היחיד שמעניין בכל הסיפור.', 'Holmes looked at me and said that this was the only interesting thing in the whole story.'),
    ('הוא שאל איך העובד נראה, והאיש סיפר על סימן לבן קטן על המצח שלו.', 'He asked what the assistant looked like, and the man told of a small white mark on his forehead.')),
  P(('אחרי שהאיש הלך, הולמס ישב שעה שלמה בלי לזוז ובלי לומר מילה.', 'After the man had gone, Holmes sat a whole hour without moving and without saying a word.'),
    ('אחר כך הוא קם ואמר שנלך לראות את הרחוב של החנות בעצמנו.', 'Afterwards he got up and said that we would go and see the shop’s street ourselves.'),
    ('הוא דפק על הדלת, שאל שאלה סתמית, והסתכל טוב על האיש שפתח.', 'He knocked on the door, asked a pointless question, and looked hard at the man who opened it.')),
  P(('אחר כך הוא הכה על המדרכה עם המקל שלו כמה פעמים בכל צד.', 'Afterwards he struck the pavement with his stick several times on each side.'),
    ('הוא אמר לי שהחשוב פה הוא לא החנות, אלא מה שנמצא מאחוריה.', 'He said to me that what mattered here was not the shop, but what stood behind it.'),
    ('הסתובבנו לרחוב הבא, ושם עמד בנק גדול עם קירות אבן.', 'We went round to the next street, and there stood a big bank with stone walls.'))]),

 ('Under the Bank', 'מתחת לבנק', [
  P(('בלילה ירדנו למרתף של הבנק עם מנהל הבנק ועם השוטר לסטרייד.', 'At night we went down into the bank’s cellar with the bank manager and with the policeman Lestrade.'),
    ('המנהל סיפר שלפני חודשים הביאו לשם זהב רב מאוד, והוא עוד שם.', 'The manager told us that months before a great deal of gold had been brought there, and that it was still there.'),
    ('הולמס ביקש שכולם ישבו בחושך גמור ולא יזוזו עד שיאמר.', 'Holmes asked that everyone sit in complete darkness and not move until he said so.')),
  P(('חיכינו שעות, והרגליים שלי כאבו, וכבר חשבתי שטעינו בכול.', 'We waited for hours, and my legs hurt, and I was already thinking that we had been wrong about everything.'),
    ('פתאום ראיתי קו דק של אור בין האבנים ברצפה, והוא גדל לאט.', 'Suddenly I saw a thin line of light between the stones in the floor, and it grew slowly.'),
    ('אבן אחת זזה הצידה, ויד עלתה מלמטה והניחה נר על הרצפה.', 'One stone moved aside, and a hand came up from below and put a candle on the floor.')),
  P(('איש עלה מהחור, ואחריו עוד אחד, ואז הולמס קפץ עליהם.', 'A man came up out of the hole, and after him another, and then Holmes sprang at them.'),
    ('לסטרייד תפס את השני, והראשון ברח בחזרה למנהרה ולא הרחיק.', 'Lestrade caught the second, and the first fled back into the tunnel and did not get far.'),
    ('הולמס אמר שהעבודה המוזרה עם השיער האדום הייתה רק דרך להוציא אדם מהחנות שלו.', 'Holmes said that the strange red-haired job had been only a way of getting a man out of his own shop.'))]),

 ('A Woman Who Came Before Dawn', 'אישה שבאה לפני הבוקר', [
  P(('לפני אור הבוקר הולמס העיר אותי ואמר שיש אישה בסלון שלנו.', 'Before daylight Holmes woke me and said that there was a woman in our sitting room.'),
    ('היא ישבה עטופה במעיל, רעדה מקור ומפחד, והשיער שלה היה אפור לפני הזמן.', 'She sat wrapped in a coat, shaking with cold and with fear, and her hair was grey before its time.'),
    ('היא סיפרה שהיא גרה עם אבא חורג בבית ישן וגדול מחוץ לעיר.', 'She told us that she lived with a stepfather in an old, big house outside the city.')),
  P(('היא סיפרה שהאחות שלה מתה לפני שנתיים, כמה ימים לפני החתונה שלה.', 'She told us that her sister had died two years before, a few days before her own wedding.'),
    ('בלילה ההוא האחות יצאה מהחדר, נפלה, ואמרה מילים על סרט מנוקד.', 'That night the sister had come out of her room, fallen, and said words about a spotted band.'),
    ('אף אחד לא הבין מה זה, והרופאים לא מצאו ממה היא מתה.', 'Nobody understood what it meant, and the doctors did not find what she had died of.')),
  P(('עכשיו גם היא עומדת להתחתן, ולפני שבוע העבירו אותה לחדר של האחות.', 'Now she too was about to marry, and a week before they had moved her into her sister’s room.'),
    ('בלילה הראשון שם היא שמעה בדיוק את אותה שריקה נמוכה בחושך.', 'On her first night there she had heard exactly the same low whistle in the dark.'),
    ('הולמס אמר לה לחזור הביתה כרגיל, ושאנחנו נגיע אחרי הצהריים.', 'Holmes told her to go home as usual, and that we would come in the afternoon.'))]),

 ('The Room That Was Changed', 'החדר ששינו בו משהו', [
  P(('אחרי שהיא יצאה נכנס אלינו איש ענק, אדום מכעס, ושבר את הברזל של האח.', 'After she had gone, a huge man came in to us, red with anger, and broke the iron of the fireplace.'),
    ('הוא צעק שאסור לנו להתערב בעניינים שלו, והלך בלי לחכות לתשובה.', 'He shouted that we must not interfere in his affairs, and left without waiting for an answer.'),
    ('הולמס יישר את הברזל בשקט וחייך, ואמר שעכשיו העניין נהיה מעניין.', 'Holmes quietly straightened the iron and smiled, and said that now the matter had become interesting.')),
  P(('אחר הצהריים הגענו לבית והסתכלנו על החדרים אחד אחרי השני.', 'In the afternoon we came to the house and looked at the rooms one after another.'),
    ('הולמס שם לב שהמיטה בחדר קבועה לרצפה ולא זזה בכלל.', 'Holmes noticed that the bed in the room was fixed to the floor and did not move at all.'),
    ('מעל המיטה היה חבל פעמון חדש, אבל הפעמון לא היה מחובר לכלום.', 'Above the bed was a new bell rope, but the bell was connected to nothing.')),
  P(('הוא ראה גם חור קטן בקיר, שמוביל ישר לחדר של האב החורג.', 'He also saw a small hole in the wall, leading straight into the stepfather’s room.'),
    ('בחדר השני עמדה כספת גדולה, וליד הכספת היה צלחת חלב על הרצפה.', 'In the other room stood a big safe, and beside the safe was a saucer of milk on the floor.'),
    ('הולמס אמר לי בשקט שכלב לא שותה מצלחת כזאת, וגם חתול לא.', 'Holmes said to me quietly that no dog drinks from such a saucer, and no cat either.'))]),

 ('The Whistle in the Dark', 'השריקה בחושך', [
  P(('בלילה ישבנו שנינו בחושך בחדר של האישה, בלי לדבר ובלי להדליק אור.', 'At night the two of us sat in the dark in the woman’s room, without speaking and without lighting a lamp.'),
    ('ההמתנה הייתה ארוכה מאוד, ושמעתי כל רעש בבית כאילו הוא לידי.', 'The wait was very long, and I heard every noise in the house as if it were beside me.'),
    ('אחרי חצות ראינו אור חלש עולה מהחור בקיר, ואז הוא נעלם.', 'After midnight we saw a faint light come up from the hole in the wall, and then it disappeared.')),
  P(('שמענו קול קטן מאוד, כמו מים שיוצאים לאט מכלי סגור.', 'We heard a very small sound, like water coming slowly out of a closed vessel.'),
    ('הולמס קפץ מיד, הדליק אור, והכה בכל הכוח על חבל הפעמון.', 'Holmes leapt up at once, lit a light, and struck the bell rope with all his strength.'),
    ('לא ראיתי כלום, אבל ראיתי את הפנים שלו, והן היו לבנות מאוד.', 'I saw nothing, but I saw his face, and it was very white.')),
  P(('מהחדר השני נשמעה צעקה נוראה, ואחר כך היה שקט גמור.', 'From the other room came a terrible cry, and afterwards there was complete silence.'),
    ('נכנסנו ומצאנו את האיש יושב ליד הכספת, ועל הראש שלו נחש.', 'We went in and found the man sitting beside the safe, and on his head a snake.'),
    ('הולמס אמר שהוא שלח אותו דרך החור, והנחש חזר אליו בכעס.', 'Holmes said that he had sent it through the hole, and that the snake had come back to him in anger.'))]),

 ('A Hat and a Goose', 'כובע ואווז', [
  P(('כמה ימים אחרי החג בא אלינו איש עם כובע ישן וקרוע ביד.', 'A few days after the holiday a man came to us with an old, torn hat in his hand.'),
    ('הוא סיפר שראה ריב ברחוב, ושאיש אחד ברח והשאיר כובע ואווז על האדמה.', 'He told us that he had seen a quarrel in the street, and that a man had fled and left a hat and a goose on the ground.'),
    ('הולמס לקח את הכובע, סובב אותו באור, וסיפר עשרה דברים על הבעלים שלו.', 'Holmes took the hat, turned it in the light, and told ten things about its owner.')),
  P(('הוא אמר שהאיש היה פעם בעל כסף, ושעכשיו הוא כבר לא.', 'He said that the man had once had money, and that now he had none.'),
    ('הוא אמר שהאישה שלו כבר לא אוהבת אותו, כי אף אחד לא ניקה את הכובע חודשים.', 'He said that his wife no longer loved him, because nobody had cleaned the hat for months.'),
    ('אמרתי שזה נשמע כמו משחק, והוא אמר שכל דבר פה כתוב על הכובע.', 'I said that it sounded like a game, and he said that everything here was written on the hat.')),
  P(('באותו רגע נכנס האיש שהביא את הכובע, והוא היה נרגש מאוד.', 'At that moment the man who had brought the hat came in, and he was very excited.'),
    ('הוא אמר שפתחו את האווז בבית, ומצאו בתוכו אבן כחולה גדולה.', 'He said that they opened the goose at home, and found a big blue stone inside it.'),
    ('הולמס הכיר את האבן מיד, כי כל העיתונים כתבו עליה באותו שבוע.', 'Holmes knew the stone at once, because all the papers had written about it that week.'))]),

 ('The Stone in the Bird', 'האבן בתוך הציפור', [
  P(('האבן נגנבה מחדר במלון גדול, ותפסו עובד צעיר שעבד שם.', 'The stone had been stolen from a room in a big hotel, and a young workman who worked there had been caught.'),
    ('הוא אמר שהוא לא לקח כלום, ואף אחד לא האמין לו.', 'He said that he had taken nothing, and nobody believed him.'),
    ('הולמס אמר שהשאלה היחידה עכשיו היא איך אבן נכנסת לתוך אווז.', 'Holmes said that the only question now was how a stone gets inside a goose.')),
  P(('שמנו מודעה בעיתון על כובע ואווז שנמצאו, וחיכינו בערב בבית.', 'We put an advertisement in the paper about a hat and a goose that had been found, and waited at home in the evening.'),
    ('איש בא, לקח את הכובע, ורצה ללכת בלי לשאול על האווז בכלל.', 'A man came, took the hat, and wanted to go without asking about the goose at all.'),
    ('הולמס שאל אותו מאיפה קנה את הציפור, והאיש ענה בלי לחשוב.', 'Holmes asked him where he had bought the bird, and the man answered without thinking.')),
  P(('הלכנו לשוק ומצאנו את המוכר, והוא כעס על כל השאלות האלה.', 'We went to the market and found the seller, and he was angry at all these questions.'),
    ('הולמס התערב איתו על כסף קטן, והמוכר הוציא מיד את כל הפנקסים שלו.', 'Holmes made a small bet with him, and the seller at once brought out all his books.'),
    ('בפנקסים היה שם של אישה שגידלה את האווזים, ושם של האיש שקנה אותם.', 'In the books was the name of a woman who raised the geese, and the name of the man who bought them.'))]),

 ('The Man Who Came for His Goose', 'האיש שבא בשביל האווז שלו', [
  P(('בזמן שדיברנו, איש קטן רץ אלינו ברחוב ושאל על האווזים גם הוא.', 'While we were talking, a small man ran up to us in the street and asked about the geese too.'),
    ('הולמס הסתכל עליו רגע ואמר לו בשקט שהוא יודע בדיוק מה הוא מחפש.', 'Holmes looked at him a moment and said quietly that he knew exactly what he was looking for.'),
    ('האיש נהיה לבן כמו נייר, ולא הצליח לעמוד בלי להחזיק בקיר.', 'The man went white as paper, and could not stand without holding on to the wall.')),
  P(('לקחנו אותו הביתה, ושם הוא סיפר הכול בלי שביקשנו פעמיים.', 'We took him home, and there he told everything without our asking twice.'),
    ('הוא עבד במלון, ראה איפה האבן, ולקח אותה כשאף אחד לא הסתכל.', 'He worked at the hotel, saw where the stone was, and took it when nobody was looking.'),
    ('הוא הכניס אותה לגרון של אווז אצל האחות שלו, ואחר כך התבלבל בין הציפורים.', 'He put it down the throat of a goose at his sister’s, and afterwards mixed up the birds.')),
  P(('הוא בכה ואמר שהוא לא יעשה דבר כזה עוד פעם בחיים שלו.', 'He wept and said that he would never do such a thing again in his life.'),
    ('הולמס פתח את הדלת ואמר לו מילה אחת: לך.', 'Holmes opened the door and said one word to him: go.'),
    ('אחר כך הוא אמר לי שהוא לא המשטרה, ושלפעמים אדם צריך הזדמנות אחת.', 'Afterwards he said to me that he was not the police, and that sometimes a man needs one chance.'))]),

 ('A Wife Who Saw Her Husband', 'אישה שראתה את בעלה', [
  P(('אישה באה אלינו וסיפרה שהבעל שלה נעלם ביום שלישי בבוקר.', 'A woman came to us and told us that her husband had disappeared on Tuesday morning.'),
    ('היא סיפרה שהיא עברה ברחוב צר ליד הנהר, והרימה את הראש במקרה.', 'She told us that she had been passing through a narrow street by the river, and had happened to look up.'),
    ('בחלון של בית ישן היא ראתה את הפנים שלו, והוא הזיז ידיים ונעלם.', 'In the window of an old house she had seen his face, and he had moved his hands and disappeared.')),
  P(('היא רצה לבית, אבל האנשים שם לא נתנו לה לעלות למעלה.', 'She had run to the house, but the people there would not let her go up.'),
    ('כשהמשטרה הגיעה, מצאו בחדר רק בגדים שלו ומעט דם על החלון.', 'When the police came, they found in the room only his clothes and a little blood on the window.'),
    ('בחדר היה גם קבצן ידוע, איש מכוער עם שפה עקומה, והוא לא הסביר כלום.', 'In the room there was also a well-known beggar, an ugly man with a twisted lip, and he explained nothing.')),
  P(('הולמס נסע לשם, ישב על הרצפה בחדר של המשטרה, ועישן כל הלילה.', 'Holmes went there, sat on the floor in the police room, and smoked all night.'),
    ('בבוקר הוא העיר אותי וצחק, ואמר שהוא היה טיפש כמו כולם.', 'In the morning he woke me and laughed, and said that he had been as foolish as everyone.'),
    ('הוא ביקש מהשוטרים דלי מים וספוג גדול, ולא הסביר למה.', 'He asked the policemen for a bucket of water and a big sponge, and did not explain why.'))]),

 ('The Beggar in the Cell', 'הקבצן בתא', [
  P(('נכנסנו לתא של הקבצן, והוא ישן על המיטה בפה פתוח.', 'We went into the beggar’s cell, and he was sleeping on the bed with his mouth open.'),
    ('הולמס העביר את הספוג על הפנים שלו, ולאט לאט הכול ירד.', 'Holmes passed the sponge over his face, and slowly everything came off.')),
  P(('מתחת לצבע ולשפה העקומה היו הפנים של הבעל שנעלם.', 'Under the paint and the twisted lip was the face of the husband who had disappeared.'),
    ('הוא התעורר, הסתכל עלינו, והבין שאין לו מה לומר.', 'He woke, looked at us, and understood that he had nothing to say.')),
  P(('הוא סיפר שהוא היה עיתונאי, ושפעם ישב יום שלם ברחוב בשביל כתבה.', 'He told us that he had been a journalist, and that once he had sat a whole day in the street for an article.'),
    ('הוא גילה שהוא מרוויח ביום אחד יותר מאשר בשבוע שלם של עבודה.', 'He discovered that he earned in one day more than in a whole week of work.'))]),

 ('Why He Did Not Come Home', 'למה הוא לא חזר הביתה', [
  P(('הוא עשה את זה שנים, והמשפחה שלו חשבה שהוא עובד במשרד בעיר.', 'He had done it for years, and his family thought that he worked in an office in the city.'),
    ('הוא שכר חדר ליד הנהר, ושם הוא היה מחליף בגדים בבוקר ובערב.', 'He rented a room by the river, and there he changed his clothes morning and evening.')),
  P(('ביום ההוא הוא ראה את האישה שלו מהחלון, ונבהל יותר מאי פעם.', 'That day he had seen his wife from the window, and was more frightened than ever.'),
    ('הוא הוריד את הבגדים שלו מהחלון וצבע את הפנים מהר מאוד.', 'He threw his own clothes out of the window and painted his face very fast.')),
  P(('הולמס אמר שאם הוא יפסיק עם זה, המשטרה לא תספר לאף אחד.', 'Holmes said that if he stopped it, the police would tell nobody.'),
    ('האיש הבטיח, ובאותו ערב הוא חזר הביתה בבגדים שלו.', 'The man promised, and that evening he went home in his own clothes.'),
    ('בדרך חזרה הולמס אמר לי שהעולם מלא אנשים שחיים שני חיים.', 'On the way back Holmes said to me that the world is full of people who live two lives.'))]),

 ('The Horse That Disappeared', 'הסוס שנעלם', [
  P(('סוס מפורסם נעלם מהאורווה שלו לילה אחד, והמאמן שלו נמצא מת בשדה.', 'A famous horse disappeared from its stable one night, and its trainer was found dead in a field.'),
    ('כל העיתונים כתבו על זה, כי המרוץ הגדול היה אמור להיות בעוד שבוע.', 'All the papers wrote about it, because the big race was due in a week.'),
    ('לסטרייד כבר עצר איש אחד, והיה בטוח לגמרי שהוא מצא את הרוצח.', 'Lestrade had already arrested a man, and was completely sure that he had found the killer.')),
  P(('נסענו לשם ברכבת, והולמס לא דיבר איתי כמעט כל הדרך.', 'We travelled there by train, and Holmes hardly spoke to me the whole way.'),
    ('הוא קרא את כל העיתונים, אחד אחרי השני, ואז זרק אותם על הרצפה.', 'He read all the papers, one after another, and then threw them on the floor.'),
    ('הוא אמר שהכול ברור, ושכולם מסתכלים בדיוק לכיוון אחר.', 'He said that everything was clear, and that everyone was looking in exactly the other direction.')),
  P(('כשהגענו, הוא הלך בשדה לבד וחיפש סימנים באדמה הרטובה.', 'When we arrived, he walked in the field alone and looked for marks in the wet ground.'),
    ('הוא מצא נר שרוף וגפרור, וגם עקבות שיצאו מהאורווה ולא חזרו.', 'He found a burnt candle and a match, and also tracks that led out of the stable and did not come back.'))]),

 ('The Dog in the Night', 'הכלב בלילה', [
  P(('בערב הולמס שאל את השוטר על הכלב ששמר על האורווה בלילה.', 'In the evening Holmes asked the policeman about the dog that guarded the stable at night.'),
    ('השוטר אמר שהכלב לא עשה שום דבר מיוחד באותו לילה.', 'The policeman said that the dog had done nothing special that night.'),
    ('הולמס אמר: זה בדיוק הדבר המיוחד, וזה כל התיק.', 'Holmes said: that is exactly the special thing, and that is the whole case.')),
  P(('הוא הסביר לי אחר כך שכלב נובח על זר ושותק מול מישהו שהוא מכיר.', 'He explained to me afterwards that a dog barks at a stranger and is silent before someone it knows.'),
    ('לכן האיש שהוציא את הסוס בלילה לא היה זר בכלל.', 'So the man who took the horse out at night was not a stranger at all.'),
    ('הוא היה מישהו שהכלב ראה כל יום, ולכן לא נשמע קול.', 'He was someone the dog saw every day, and so no sound was heard.')),
  P(('הולמס בדק גם את האוכל של הנער ששמר, ומצא בו אבקה לבנה.', 'Holmes also checked the food of the boy on watch, and found a white powder in it.'),
    ('הוא אמר שמי ששם את האבקה ידע בדיוק מה יאכלו באותו ערב.', 'He said that whoever put the powder there knew exactly what would be eaten that evening.'))]),

 ('What the Trainer Was Doing', 'מה עשה המאמן', [
  P(('הולמס מצא את הסוס אצל שכן, צבוע בצבע אחר, ועומד בין סוסים רגילים.', 'Holmes found the horse at a neighbour’s, painted a different colour, and standing among ordinary horses.'),
    ('הוא לא אמר כלום לאף אחד, והחזיר אותו רק ביום המרוץ עצמו.', 'He said nothing to anyone, and returned it only on the day of the race itself.')),
  P(('הוא הסביר שהמאמן עצמו הוציא את הסוס מהאורווה באותו לילה.', 'He explained that the trainer himself had taken the horse out of the stable that night.'),
    ('הוא רצה לפצוע אותו קצת ברגל, כדי שלא ירוץ מהר במרוץ.', 'He had wanted to hurt its leg a little, so that it would not run fast in the race.'),
    ('הוא היה חייב כסף רב, והימר בסתר על סוס אחר.', 'He owed a great deal of money, and had bet secretly on another horse.')),
  P(('הוא הביא איתו סכין קטן וחד, כזה שרופא משתמש בו.', 'He had brought with him a small, sharp knife, the kind a doctor uses.'),
    ('הסוס פחד ובעט בו בראש, והוא מת שם בשדה לבד.', 'The horse was frightened and kicked him in the head, and he died there alone in the field.'),
    ('הולמס אמר שהתיק הזה נפתר בעצמו, ושהוא רק הקשיב למה שלא קרה.', 'Holmes said that this case had solved itself, and that he had only listened to what had not happened.'))]),

 ('Someone Is Breaking Statues', 'מישהו שובר פסלים', [
  P(('לסטרייד בא אלינו עם סיפור שהוא עצמו קרא לו טיפשי לגמרי.', 'Lestrade came to us with a story that he himself called completely silly.'),
    ('מישהו נכנס לבתים ושבר פסלים קטנים של נפוליאון, ולא לקח שום דבר אחר.', 'Someone was breaking into houses and smashing small statues of Napoleon, and taking nothing else.'),
    ('בכל פעם הפסל נשבר לחתיכות קטנות, תמיד בחוץ ותמיד באור.', 'Each time the statue was broken into small pieces, always outside and always in the light.')),
  P(('הולמס שאל אם כל הפסלים באו מאותו מקום, ולסטרייד לא ידע.', 'Holmes asked whether all the statues had come from the same place, and Lestrade did not know.'),
    ('הם בדקו, והתברר שכולם נעשו באותו בית מלאכה קטן ובאותו יום.', 'They checked, and it turned out that they had all been made in the same little workshop and on the same day.'),
    ('הולמס אמר שזה לא איש חולה, אלא איש שמחפש דבר אחד מסוים.', 'Holmes said that this was not a sick man, but a man looking for one particular thing.')),
  P(('אחרי כמה ימים מצאו אדם מת ליד בית שבו נשבר פסל בלילה.', 'A few days later a dead man was found beside a house where a statue had been broken in the night.'),
    ('עכשיו זה כבר לא היה סיפור טיפשי, ולסטרייד הפסיק לצחוק.', 'Now it was no longer a silly story, and Lestrade stopped laughing.'),
    ('הולמס ביקש רשימה של כל האנשים שקנו פסל מאותה סדרה.', 'Holmes asked for a list of everyone who had bought a statue from that batch.'))]),

 ('All From the Same Mould', 'כולם מאותה תבנית', [
  P(('בבית המלאכה סיפרו שעבד שם איטלקי צעיר, והוא נעלם באותה תקופה.', 'At the workshop they said that a young Italian had worked there, and that he had disappeared at that time.'),
    ('הולמס הראה להם תמונה של האיש שנמצא מת, והם הכירו אותו מיד.', 'Holmes showed them a photograph of the man who had been found dead, and they knew him at once.'),
    ('הם אמרו שהשניים היו חברים פעם, ואחר כך רבו על משהו.', 'They said that the two had once been friends, and afterwards had quarrelled over something.')),
  P(('הולמס בדק את התאריך של הפסלים, והתאריך הזה אמר לו הכול.', 'Holmes checked the date of the statues, and that date told him everything.'),
    ('באותו יום נגנבה אבן יקרה מאוד מבית של משפחה עשירה בעיר.', 'On that day a very valuable stone had been stolen from a rich family’s house in the city.'),
    ('הגנב נתפס בלי האבן, ואף אחד לא ידע לאן היא נעלמה.', 'The thief had been caught without the stone, and nobody knew where it had gone.')),
  P(('הולמס אמר שהגנב היה בבית המלאכה באותו רגע, עם שוטרים מאחוריו.', 'Holmes said that the thief had been in the workshop at that moment, with policemen behind him.'),
    ('הוא הכניס את האבן לתוך אחד הפסלים כשהחומר עוד היה רך.', 'He had pushed the stone into one of the statues while the material was still soft.'),
    ('הוא ישב בכלא שנים, ואחר כך התחיל לחפש את הפסל הנכון.', 'He had sat in prison for years, and afterwards had begun looking for the right statue.'))]),

 ('The Last Statue', 'הפסל האחרון', [
  P(('נשאר פסל אחד ברשימה, אצל אדם שגר רחוק מהעיר.', 'One statue was left on the list, at the house of a man who lived far from the city.'),
    ('הולמס נסע אליו בשקט, קנה ממנו את הפסל, ולא הסביר כלום.', 'Holmes travelled to him quietly, bought the statue from him, and explained nothing.'),
    ('הוא הביא אותו הביתה ושם אותו על השולחן מול לסטרייד ומולי.', 'He brought it home and put it on the table in front of Lestrade and me.')),
  P(('הוא הכה עליו פעם אחת, והפסל נשבר לחתיכות על מפה לבנה.', 'He struck it once, and the statue broke into pieces on a white cloth.'),
    ('בין החתיכות שכבה אבן שחורה, והיא האירה כשהרים אותה לאור.', 'Among the pieces lay a black stone, and it shone when he lifted it to the light.'),
    ('לסטרייד קם על הרגליים ולא הצליח לומר מילה אחת.', 'Lestrade rose to his feet and could not say a single word.')),
  P(('הוא אמר שראה הרבה דברים במשטרה, ושמעולם לא ראה עבודה כזאת.', 'He said that he had seen many things in the police, and had never seen work like it.'),
    ('הולמס חייך ואמר שהוא רק עשה מה שכל אחד היה עושה.', 'Holmes smiled and said that he had only done what anyone would have done.'),
    ('אחר כך הוא ישב בכיסא, לקח את הכינור, וניגן חצי שעה.', 'Afterwards he sat in his chair, took his violin, and played for half an hour.'))]),

 ('Little Men on the Paper', 'אנשים קטנים על הנייר', [
  P(('איש כפרי בא אלינו עם נייר, ועליו ציורים של אנשים קטנים רוקדים.', 'A country gentleman came to us with a paper, and on it drawings of little dancing men.'),
    ('הוא אמר שהאישה שלו ראתה את הציורים והתחילה לפחד מאוד.', 'He said that his wife had seen the drawings and had begun to be very afraid.'),
    ('היא ביקשה ממנו לא לשאול אותה שום דבר, והוא הבטיח לה.', 'She had asked him to ask her nothing, and he had promised her.')),
  P(('הולמס הסתכל על הנייר ואמר שאלה לא ציורים אלא אותיות.', 'Holmes looked at the paper and said that these were not drawings but letters.'),
    ('הוא ביקש מהאיש לשלוח לו כל ציור חדש שיופיע על הבית.', 'He asked the man to send him every new drawing that appeared on the house.')),
  P(('אחרי כמה שבועות הגיעו עוד ארבעה ניירות, אחד אחרי השני.', 'A few weeks later four more papers arrived, one after another.'),
    ('הולמס ישב איתם ימים ולא יצא מהחדר כמעט בכלל.', 'Holmes sat with them for days and hardly left the room at all.'))]),

 ('Counting the Letters', 'סופרים את האותיות', [
  P(('הוא הסביר לי שבכל שפה יש אות אחת שחוזרת יותר מכל האחרות.', 'He explained to me that in every language there is one letter that comes back more than all the rest.'),
    ('הוא ספר את האנשים הקטנים, ומצא איזה מהם חוזר הכי הרבה.', 'He counted the little men, and found which of them came back most often.'),
    ('משם הוא הלך למילים קצרות, ואחר כך לשם של האישה עצמה.', 'From there he went to short words, and afterwards to the woman’s own name.')),
  P(('כשהיו לו מספיק אותיות, הוא קרא את המשפטים בלי קושי.', 'When he had enough letters, he read the sentences without difficulty.'),
    ('בהודעה האחרונה היה כתוב משפט קצר מאוד, והוא קם מהכיסא מיד.', 'In the last message a very short sentence was written, and he got up from his chair at once.'),
    ('הוא אמר לי לקחת אקדח, כי אנחנו נוסעים ברכבת הראשונה.', 'He told me to take a pistol, because we were taking the first train.')),
  P(('בדרך הוא סיפר לי שהאישה באה מאמריקה ומשפחה קשה מאוד.', 'On the way he told me that the woman came from America and from a very hard family.'),
    ('האיש שכותב לה היה קרוב אליה פעם, ועכשיו הוא בא לקחת אותה בחזרה.', 'The man writing to her had once been close to her, and now he had come to take her back.'),
    ('הולמס אמר בשקט שהוא מקווה שאנחנו לא מאחרים ביום אחד.', 'Holmes said quietly that he hoped we were not one day too late.'))]),

 ('Too Late by One Day', 'מאחרים ביום אחד', [
  P(('כשהגענו לתחנה חיכה לנו שוטר, והוא סיפר לנו מה קרה בלילה.', 'When we reached the station a policeman was waiting for us, and he told us what had happened in the night.'),
    ('בעל הבית מת, והאישה שכבה פצועה קשה בחדר שלה.', 'The master of the house was dead, and the woman lay badly hurt in her room.'),
    ('כולם חשבו שהיא ירתה בו ואחר כך בעצמה, וזה נראה ברור מאוד.', 'Everyone thought that she had shot him and then herself, and it looked very clear.')),
  P(('הולמס נכנס לחדר, מדד את המרחקים, וחיפש חור נוסף בקיר.', 'Holmes went into the room, measured the distances, and looked for another hole in the wall.'),
    ('הוא מצא כדור שלישי, ומזה הבין שהיה שם אדם שלישי בחלון.', 'He found a third bullet, and from that understood that there had been a third person at the window.'),
    ('הוא אמר לשוטרים שהאישה לא ירתה באף אחד, גם לא בעצמה.', 'He said to the policemen that the woman had shot nobody, not even herself.')),
  P(('הולמס כתב הודעה משלו באנשים הקטנים ושלח אותה לבית שבו האיש גר.', 'Holmes wrote a message of his own in the little men and sent it to the house where the man was staying.'),
    ('האיש בא מיד, כי חשב שהאישה קוראת לו, והוא נכנס ישר לחדר.', 'The man came at once, because he thought the woman was calling him, and he walked straight into the room.'),
    ('לסטרייד סגר עליו את הדלת, והולמס אמר לו שהוא כתב את המכתב בעצמו.', 'Lestrade shut the door on him, and Holmes told him that he had written the letter himself.'))]),

 ('The Man Behind Everything', 'האיש שמאחורי הכול', [
  P(('ערב אחד הולמס נכנס אליי הביתה מאוחר, וסגר את כל התריסים.', 'One evening Holmes came into my house late, and closed all the shutters.'),
    ('הידיים שלו נפגעו, והוא סיפר שניסו להרוג אותו פעמיים באותו יום.', 'His hands had been hurt, and he told me that they had tried to kill him twice that day.'),
    ('הוא אמר לי שיש בלונדון אדם אחד שעומד מאחורי חצי מהפשעים בעיר.', 'He told me that there was one man in London who stood behind half the crimes in the city.')),
  P(('הוא אמר שקוראים לו מוריארטי, ושהוא היה פעם מורה למתמטיקה מכובד.', 'He said that his name was Moriarty, and that he had once been a respected teacher of mathematics.'),
    ('הוא אמר שהוא לא עושה כלום בעצמו, אלא רק חושב ומסדר.', 'He said that he did nothing himself, but only thought and arranged.'),
    ('הולמס אמר שהוא עבד שנתיים כדי לחבר את כל החוטים ליד אחת.', 'Holmes said that he had worked for two years to bring all the threads into one hand.')),
  P(('הוא אמר שעוד שלושה ימים המשטרה תעצור את כולם ביחד.', 'He said that in three days the police would arrest them all together.'),
    ('אבל עד אז מוריארטי ינסה כל דבר כדי לעצור אותו, ולכן צריך לצאת מלונדון.', 'But until then Moriarty would try anything to stop him, and so they had to leave London.'),
    ('הוא ביקש ממני לבוא איתו לאירופה, ואני הסכמתי בלי לשאול.', 'He asked me to come with him to Europe, and I agreed without asking.'))]),

 ('Across the Water', 'מעבר למים', [
  P(('בבוקר נסענו לתחנה בדרכים שונות, כמו שהולמס ביקש.', 'In the morning we went to the station by different routes, as Holmes had asked.'),
    ('ברגע האחרון עלה לרכבת איש דת זקן, וזה היה הולמס עצמו.', 'At the last moment an old clergyman got on the train, and it was Holmes himself.')),
  P(('כשיצאנו מהתחנה ראינו איש עומד על הרציף ומסתכל ברכבת שיוצאת.', 'As we left the station we saw a man standing on the platform watching the train go.'),
    ('הולמס אמר שזה מוריארטי, ושהוא יגיע לצרפת לפנינו ברכבת מיוחדת.', 'Holmes said that it was Moriarty, and that he would reach France before us on a special train.')),
  P(('ירדנו באמצע הדרך, עברנו לרכבת אחרת, ונסענו לשווייץ.', 'We got off midway, changed to another train, and travelled to Switzerland.'),
    ('שם הלכנו כמה ימים בהרים, וכמעט שכחתי בשביל מה באנו.', 'There we walked for a few days in the mountains, and I almost forgot why we had come.'))]),

 ('The Waterfall', 'המפל', [
  P(('ביום השלישי הגענו למפל גדול בשם ריכנבאך, והמים ירדו לתוך חור עמוק.', 'On the third day we came to a great waterfall called Reichenbach, and the water fell into a deep hole.'),
    ('עמדנו שם והסתכלנו, והרעש היה חזק כל כך שהיה קשה לדבר.', 'We stood there and watched, and the noise was so strong that it was hard to talk.')),
  P(('ילד הגיע בריצה עם מכתב, ובו כתבו שאישה אנגלייה חולה מאוד במלון.', 'A boy came running with a letter, in which it was written that an English woman was very ill at the hotel.'),
    ('חזרתי מיד, כי אני רופא, והולמס נשאר לחכות לי ליד המים.', 'I went back at once, because I am a doctor, and Holmes stayed to wait for me by the water.'),
    ('כשהגעתי למלון, לא הייתה שם שום אישה חולה, והבנתי מה עשיתי.', 'When I reached the hotel, there was no sick woman there, and I understood what I had done.')),
  P(('רצתי בחזרה, ובסוף הדרך היו רק שני עקבות שהולכים ולא חוזרים.', 'I ran back, and at the end of the path there were only two sets of tracks going and not returning.'),
    ('על סלע היה מכתב ממנו אליי, כתוב בשקט כמו כל דבר שהוא כתב.', 'On a rock was a letter from him to me, written as calmly as everything he wrote.'),
    ('הוא כתב שהוא שמח לגמור ככה, אם זה גומר גם את מוריארטי.', 'He wrote that he was glad to end this way, if it also ended Moriarty.'))]),

 ('Three Years Later', 'שלוש שנים אחר כך', [
  P(('שלוש שנים חייתי בלונדון והמשכתי בעבודה שלי כרופא.', 'For three years I lived in London and went on with my work as a doctor.'),
    ('קראתי על תיקים במשטרה וחשבתי כל פעם מה הוא היה אומר.', 'I read about police cases and thought each time what he would have said.')),
  P(('יום אחד קראתי בעיתון על אדם עשיר שנמצא מת בחדר סגור מבפנים.', 'One day I read in the paper about a rich man found dead in a room locked from the inside.'),
    ('הלכתי לראות את הבית מבחוץ, כי לא יכולתי לשבת בשקט.', 'I went to see the house from outside, because I could not sit still.')),
  P(('ליד הבית התנגשתי באיש זקן עם ספרים, והספרים נפלו על האדמה.', 'Near the house I bumped into an old man with books, and the books fell on the ground.'),
    ('הרמתי אותם ואמרתי סליחה, והוא כעס ואמר משהו לא ברור.', 'I picked them up and said sorry, and he was angry and said something unclear.'),
    ('חזרתי הביתה, וכעבור שעה הזקן דפק על הדלת שלי.', 'I went home, and an hour later the old man knocked at my door.'))]),

 ('How He Lived', 'איך הוא נשאר בחיים', [
  P(('הזקן עמד בחדר, ואז הוא התיישר, והפנים שלו השתנו לגמרי.', 'The old man stood in the room, and then he straightened up, and his face changed completely.'),
    ('זה היה הולמס, והוא חייך אליי כאילו נפגשנו אתמול בבוקר.', 'It was Holmes, and he smiled at me as if we had met yesterday morning.'),
    ('ישבתי על הרצפה, כי הרגליים שלי לא החזיקו אותי.', 'I sat down on the floor, because my legs would not hold me.')),
  P(('הוא סיפר שבמפל הוא נלחם עם מוריארטי על השביל הצר.', 'He told me that at the waterfall he had fought with Moriarty on the narrow path.'),
    ('מוריארטי נפל למים, והולמס נשאר עומד ולא נפל איתו.', 'Moriarty had fallen into the water, and Holmes had stayed standing and had not fallen with him.'),
    ('הוא הבין באותו רגע שאם כולם יחשבו שהוא מת, האנשים של מוריארטי לא יחפשו אותו.', 'He understood at that moment that if everyone thought he was dead, Moriarty’s men would not look for him.')),
  P(('הוא עלה על הסלע, נשאר שם שעות, ואחר כך נסע רחוק מאוד.', 'He climbed the rock, stayed there for hours, and afterwards travelled very far away.'),
    ('הוא היה בטיבט, במצרים ובצרפת, וכתב לי רק פעם אחת בלי שם.', 'He had been in Tibet, in Egypt and in France, and had written to me only once without a name.'),
    ('הוא אמר שהוא מצטער על כל יום, ושלא היה יכול לעשות אחרת.', 'He said that he was sorry for every day, and that he could not have done otherwise.'))]),

 ('The Empty House', 'הבית הריק', [
  P(('הוא אמר שהוא חזר בגלל התיק שקראתי עליו בעיתון בדיוק באותו בוקר.', 'He said that he had come back because of the case I had read about in the paper that very morning.'),
    ('הוא אמר שהאיש האחרון של מוריארטי עוד בלונדון, והוא הכי מסוכן מכולם.', 'He said that Moriarty’s last man was still in London, and was the most dangerous of them all.'),
    ('הוא ביקש שאבוא איתו בערב, ולא ישאל שאלות עד שנגיע.', 'He asked me to come with him in the evening, and to ask no questions until we arrived.')),
  P(('נכנסנו לבית ריק מול הדירה הישנה שלנו ברחוב בייקר.', 'We went into an empty house opposite our old rooms in Baker Street.'),
    ('בחלון שלנו ראיתי צל של אדם יושב, והצל זז לאט מדי פעם.', 'In our window I saw the shadow of a man sitting, and the shadow moved slowly now and then.'),
    ('הולמס אמר שזה פסל שעשו בשבילו, ושמישהו מזיז אותו כל רבע שעה.', 'Holmes said that it was a figure made for him, and that someone moved it every quarter of an hour.')),
  P(('חיכינו בחושך שעות, ואז שמענו מישהו נכנס לחדר מתחתינו.', 'We waited in the dark for hours, and then we heard someone come into the room below us.'),
    ('האיש פתח את החלון והרים רובה מיוחד לכיוון הצל.', 'The man opened the window and raised a special rifle towards the shadow.'),
    ('הולמס קפץ עליו מאחור, ואני עזרתי לו, ולסטרייד עלה במדרגות בריצה.', 'Holmes sprang on him from behind, and I helped him, and Lestrade came running up the stairs.')),
  P(('אחר כך חזרנו לדירה הישנה, וכל דבר שם היה בדיוק כמו לפני שלוש שנים.', 'Afterwards we went back to the old rooms, and everything there was exactly as it had been three years before.'),
    ('הולמס ישב בכיסא שלו, לקח את הכינור, ולא אמר שום דבר חשוב.', 'Holmes sat in his chair, took his violin, and said nothing important.'),
    ('ואני ישבתי מולו וחשבתי שהעיר הזאת חזרה להיות מה שהייתה.', 'And I sat opposite him and thought that this city had gone back to being what it was.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('holmes', {'en': 'Sherlock Holmes: Ten Stories',
                                     'he': 'שרלוק הולמס: עשרה סיפורים'}, 'advanced',
                          CHAPTERS, unit='Chapter', unit_he='פרק', shelf=20, meta=META))
