#!/usr/bin/env python3
"""עשרים סיפורים: מופסאן וצ'כוב — twenty stories retold in modern Hebrew, graded to advanced.

The Hebrew twin of pipeline/book_shortstories.py: ten by Maupassant, ten by Chekhov, the same
twenty the Arabic shelf carries. Maupassant died in 1893 and Chekhov in 1904; both are public
domain, and these are retellings from the plots rather than translations of anyone's version.

WHY THIS IS THE LAST BOOK ON THE SHELF. Every other reader here rewards a reader who follows the
plot. These do not: the plot of "The Necklace" fits in one sentence and means nothing, and the
whole story is in what the last line does to the first. A reader who gets that in Hebrew is no
longer decoding Hebrew — which is the only honest definition of finishing a graded shelf.

The sentences are the longest in this project, and they carry the load in the tier's own way:
two clauses at a time, a past tense that does not restart at every sentence, and irony, which
needs the reader to hold what was said against what was meant.

Deliberately unpointed; the vowels are looked up at ingest.

Run:  python3 pipeline/he_book_shortstories.py --lang he            # check
      python3 pipeline/he_book_shortstories.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'short stories by Guy de Maupassant and Anton Chekhov',
        'author': 'Maupassant (d. 1893) and Chekhov (d. 1904)', 'year': '1880s–1900s',
        'status': 'public domain — retold from the plots, not from any translation'}

CHAPTERS = [
 ('Fat and Thin at the Station', 'השמן והרזה בתחנה', [
  P(('שני גברים נפגשו בתחנת רכבת אחרי שלא ראו זה את זה עשרים שנה.', 'Two men met at a railway station after not seeing each other for twenty years.'),
    ('הם למדו יחד בבית ספר, והיו אז חברים שאין קרובים מהם.', 'They had been at school together, and had then been friends than whom none were closer.')),
  P(('הרזה הציג את האישה שלו ואת הבן שלו, ודיבר מהר מרוב שמחה.', 'The thin one introduced his wife and his son, and talked fast out of sheer joy.'),
    ('הוא סיפר שהוא עובד במשרד, שהמשכורת קטנה, ושבבית תמיד חסר משהו.', 'He told that he worked in an office, that the salary was small, and that at home something was always missing.')),
  P(('השמן חייך ואמר שגם הוא במשרד, אבל במקום קצת אחר.', 'The fat one smiled and said that he too was in an office, but in a slightly different place.'),
    ('הרזה שאל באיזה מקום בדיוק, והשמן אמר לו את התואר שלו.', 'The thin one asked in exactly what place, and the fat one told him his title.')),
  P(('הפנים של הרזה השתנו, הגב שלו התכופף, והוא התחיל לדבר אחרת לגמרי.', 'The thin one’s face changed, his back bent, and he began to talk quite differently.'),
    ('הוא הוסיף מילים של כבוד לכל משפט, וקרא לחבר שלו אדוני.', 'He added words of respect to every sentence, and called his friend sir.')),
  P(('השמן ניסה לומר שאין צורך בזה, שהם חברים מבית הספר.', 'The fat one tried to say that there was no need for this, that they were friends from school.'),
    ('אבל הרזה המשיך להתכופף, והאישה והבן שלו התכופפו גם הם.', 'But the thin one went on bowing, and his wife and his son bowed too.'),
    ('השמן נתן להם יד, הסתובב, והלך לרכבת שלו בלי לומר עוד מילה.', 'The fat one gave them his hand, turned, and went to his train without another word.'))]),

 ('The Umbrella', 'המטרייה', [
  P(('אישה אחת שמרה על כל אגורה בבית, וכעסה על כל דבר שנקנה.', 'One woman watched every penny in the house, and was angry at everything that was bought.'),
    ('הבעל שלה עבד במשרד, והמעיל שלו היה ישן והמטרייה שלו הייתה ישנה יותר.', 'Her husband worked in an office, and his coat was old and his umbrella was older still.')),
  P(('אחרי שנים היא הסכימה לקנות לו מטרייה חדשה ויפה מאוד.', 'After years she agreed to buy him a new and very fine umbrella.'),
    ('אחרי שבוע הוא חזר הביתה, והמטרייה הייתה מלאה חורים קטנים.', 'A week later he came home, and the umbrella was full of small holes.')),
  P(('היא צעקה עליו כל הערב ואמרה שהוא עשה את זה בכוונה.', 'She shouted at him all evening and said that he had done it on purpose.'),
    ('הוא הסביר שאנשים במשרד שמים סיגריות ליד הדברים, ואף אחד לא נזהר.', 'He explained that people at the office put cigarettes down beside things, and nobody is careful.')),
  P(('בבוקר היא לקחה את המטרייה השבורה והלכה איתה לחברת הביטוח בעיר.', 'In the morning she took the ruined umbrella and went with it to the insurance company in the city.'),
    ('היא חיכתה שעה, נכנסה, וסיפרה את הסיפור בקול חזק וברור.', 'She waited an hour, went in, and told the story in a loud, clear voice.')),
  P(('הפקיד אמר שהם משלמים על שריפה של בית ולא על מטרייה.', 'The clerk said that they pay for a house fire and not for an umbrella.'),
    ('היא לא זזה מהמקום ודיברה עוד ועוד, עד שהוא הפסיק להתווכח.', 'She did not move from the spot and talked on and on, until he stopped arguing.'),
    ('בסוף הוא נתן לה כסף למטרייה חדשה, והיא קנתה אחת זולה יותר.', 'In the end he gave her money for a new umbrella, and she bought a cheaper one.'))]),

 ('The Piece of String', 'חתיכת החוט', [
  P(('בשוק של כפר בנורמנדי איכר זקן ראה חתיכת חוט על האדמה.', 'At a village market in Normandy an old farmer saw a piece of string on the ground.'),
    ('הוא התכופף ולקח אותה, כי אצלו שום דבר לא נזרק.', 'He bent down and took it, because at his house nothing was thrown away.')),
  P(('שכן שלו, שרב איתו שנים, ראה אותו מתכופף והסתכל עליו טוב.', 'A neighbour of his, who had quarrelled with him for years, saw him bend down and looked at him carefully.'),
    ('באותו יום מישהו איבד ארנק עם כסף בדרך בין השוק לכפר.', 'That day someone lost a purse with money on the road between the market and the village.')),
  P(('השכן הלך למשטרה ואמר שראה את האיכר מרים משהו מהאדמה.', 'The neighbour went to the police and said that he had seen the farmer pick something up from the ground.'),
    ('לקחו את האיכר, והוא הוציא מהכיס חתיכת חוט והראה אותה לכולם.', 'They took the farmer, and he took a piece of string out of his pocket and showed it to everyone.')),
  P(('אף אחד לא האמין לו, כי סיפור כזה נשמע כמו סיפור שממציאים.', 'Nobody believed him, because such a story sounds like a story people invent.'),
    ('אחרי כמה ימים הארנק נמצא, ואיש אחר החזיר אותו לבעלים.', 'A few days later the purse was found, and another man returned it to its owner.')),
  P(('האיכר הלך משוק לשוק וסיפר לכל אדם שהוא לא לקח כלום.', 'The farmer went from market to market and told every man that he had taken nothing.'),
    ('וככל שהוא סיפר את זה יותר, אנשים האמינו לו פחות וצחקו יותר.', 'And the more he told it, the less people believed him and the more they laughed.'),
    ('הוא חלה ומת בחורף, וגם ברגע האחרון דיבר על החוט.', 'He fell ill and died in the winter, and even at the last moment he talked about the string.'))]),

 ('The Necklace', 'השרשרת', [
  P(('אישה יפה נולדה במשפחה פשוטה, והתחתנה עם פקיד קטן במשרד.', 'A beautiful woman was born into a simple family, and married a small clerk in an office.'),
    ('היא חשבה כל יום על החיים שהיו יכולים להיות לה, ולא הייתה מרוצה מכלום.', 'She thought every day about the life she might have had, and was pleased with nothing.')),
  P(('יום אחד הבעל הביא הזמנה לנשף גדול אצל אנשים חשובים.', 'One day the husband brought an invitation to a great ball at the house of important people.'),
    ('היא בכתה ואמרה שאין לה מה ללבוש, והוא נתן לה את הכסף ששמר לעצמו.', 'She cried and said she had nothing to wear, and he gave her the money he had been saving for himself.')),
  P(('היא קנתה שמלה, ואז אמרה שבלי תכשיט אי אפשר ללכת לשם.', 'She bought a dress, and then said that without a piece of jewellery it was impossible to go there.'),
    ('היא הלכה לחברה עשירה שלה, וקיבלה ממנה שרשרת יפה מאוד.', 'She went to a rich friend of hers, and got from her a very beautiful necklace.')),
  P(('בנשף כולם הסתכלו עליה, והיא רקדה כל הלילה והייתה מאושרת.', 'At the ball everyone looked at her, and she danced all night and was happy.'),
    ('בבוקר, כשהגיעו הביתה, היא שמה את היד על הצוואר והשרשרת לא הייתה שם.', 'In the morning, when they got home, she put her hand to her neck and the necklace was not there.')),
  P(('הם חיפשו ימים ולא מצאו, ואז קנו שרשרת דומה בכסף שלווּ.', 'They searched for days and did not find it, and then bought a similar necklace with borrowed money.'),
    ('עשר שנים הם עבדו קשה, עברו לדירה קטנה, והיא איבדה את היופי שלה.', 'For ten years they worked hard, moved to a small flat, and she lost her beauty.')),
  P(('יום אחד היא פגשה את החברה העשירה ברחוב, וסיפרה לה הכול.', 'One day she met the rich friend in the street, and told her everything.'),
    ('החברה החזיקה לה את הידיים ואמרה שהשרשרת ההיא לא הייתה אמיתית.', 'The friend held her hands and said that that necklace had not been real.'),
    ('היא אמרה שהיא הייתה שווה מעט מאוד כסף, פחות ממה שאפשר לחשוב.', 'She said that it had been worth very little money, less than one might think.'))]),

 ('My Uncle Jules', "הדוד ז'ול", [
  P(('במשפחה שלנו דיברו כל חיי על דוד אחד שנסע לאמריקה.', 'In our family they talked all my life about one uncle who had gone to America.'),
    ("קראו לו ז'ול, והוא היה קודם הבושה של המשפחה ואחר כך התקווה שלה.", 'His name was Jules, and he was first the shame of the family and afterwards its hope.')),
  P(('הוא בזבז כסף כשהיה צעיר, ולכן שלחו אותו רחוק מהבית.', 'He had wasted money when he was young, and so they sent him far from home.'),
    ('משם הוא כתב שהוא עובד, שהוא מרוויח, ושהוא יחזור עשיר.', 'From there he wrote that he was working, that he was earning, and that he would come back rich.')),
  P(('אבא שלי קרא את המכתב הזה בקול בכל שבת במשך שנים.', 'My father read that letter aloud every Saturday for years.'),
    ('כל תוכנית בבית שלנו התחילה תמיד באותן שתי מילים: כשהדוד יחזור.', 'Every plan in our house always began with the same two words: when the uncle comes back.')),
  P(('קיץ אחד נסענו כולנו יחד בספינה קטנה לטיול של יום אחד.', 'One summer we all went together on a small boat for a trip of one day.'),
    ('על הסיפון ישב איש זקן ומלוכלך ופתח צדפים בשביל הנוסעים.', 'On the deck sat an old, dirty man opening shellfish for the passengers.')),
  P(('אבא שלי הסתכל עליו זמן ארוך, והפנים שלו נהיו לבנות מאוד.', 'My father looked at him for a long moment, and his face went very white.'),
    ('הוא לחש לאמא שלי שזה הדוד, והיא אמרה לו לשבת ולשתוק.', 'He whispered to my mother that it was the uncle, and she told him to sit down and be quiet.')),
  P(('אמא שלי אמרה שאסור שהילדים ידעו ושצריך לרדת בצד השני.', 'My mother said that the children must not know and that we must get off on the other side.'),
    ('שילמתי לו על הצדפים, והוא הודה לי ולא הסתכל עליי בכלל.', 'I paid him for the shellfish, and he thanked me and did not look at me at all.'),
    ('בדרך חזרה עלינו על ספינה אחרת, כדי לא לעבור שם שוב.', 'On the way back we took a different boat, so as not to pass there again.'))]),

 ('The Jewels', 'התכשיטים', [
  P(('פקיד צעיר התחתן עם אישה שקטה, וכולם אמרו שהוא מצא אוצר.', 'A young clerk married a quiet woman, and everyone said that he had found a treasure.'),
    ('היא ניהלה את הבית יפה, והוציאה פחות ממה שהוא הרוויח.', 'She ran the house well, and spent less than he earned.')),
  P(('היו לה שני דברים שהוא לא אהב: תיאטרון ותכשיטים זולים.', 'She had two things that he did not like: the theatre and cheap jewellery.'),
    ('כל ערב היא ישבה וסידרה את התכשיטים שלה על השולחן והסתכלה עליהם.', 'Every evening she sat and arranged her jewellery on the table and looked at it.')),
  P(('הוא צחק עליה ואמר שאישה בלי כסף צריכה פנים יפות ולא זכוכית צבעונית.', 'He laughed at her and said that a woman without money needs a fine face and not coloured glass.'),
    ('היא ענתה בשקט שכל אחד אוהב מה שהוא אוהב, והמשיכה לסדר.', 'She answered quietly that everyone loves what he loves, and went on arranging.')),
  P(('חורף אחד היא חזרה מהתיאטרון בקור, חלתה, ומתה בתוך שבוע.', 'One winter she came back from the theatre in the cold, fell ill, and died within a week.'),
    ('הוא נשאר לבד ולא הצליח לחיות עם המשכורת שלו בכלל.', 'He was left alone and could not manage on his salary at all.')),
  P(('הוא לקח את התכשיטים לחנות כדי למכור אותם בכמה מטבעות.', 'He took the jewellery to a shop in order to sell it for a few coins.'),
    ('המוכר הסתכל בזכוכית, יצא לחדר אחורי, וחזר עם עוד אדם.', 'The dealer looked through a glass, went into a back room, and came back with another man.')),
  P(('הם אמרו לו שהתכשיטים אמיתיים ושהם שווים הרבה מאוד כסף.', 'They told him that the jewellery was real and that it was worth a great deal of money.'),
    ('הוא שאל מאיפה הם יודעים, והם אמרו שהם מכרו אותם בעצמם.', 'He asked how they knew, and they said that they had sold them themselves.'),
    ('הוא לקח את כל הכסף, עזב את המשרד באותו שבוע, והתחתן שוב אחרי שנה.', 'He took all the money, left the office that same week, and married again a year later.'))]),

 ('Two Friends', 'שני חברים', [
  P(('בזמן המלחמה פריז הייתה סגורה, ולא היה בעיר כמעט אוכל.', 'During the war Paris was closed, and there was almost no food in the city.'),
    ('שני חברים, שדגו יחד כל שבת לפני המלחמה, נפגשו ברחוב במקרה.', 'Two friends, who had fished together every Saturday before the war, met by chance in the street.')),
  P(('הם נכנסו לשתות משהו, וכל אחד סיפר כמה הוא מתגעגע לנהר.', 'They went in for a drink, and each said how much he missed the river.'),
    ('אחד מהם אמר שאולי אפשר לצאת בשקט לשעה, ולחזור לפני החושך.', 'One of them said that perhaps they could slip out for an hour, and be back before dark.')),
  P(('הם קיבלו נייר מקצין אחד, והם ירדו לנהר בין השדות הריקים והשקטים.', 'They got a paper from one officer, and they went down to the river between the empty, quiet fields.'),
    ('היה שקט מאוד, והשמש ירדה על המים כמו בכל שנה אחרת.', 'It was very quiet, and the sun came down on the water as in any other year.')),
  P(('הם דגו כמה שעות ולא דיברו הרבה, כי לא היה צריך.', 'They fished for a few hours and did not talk much, because there was no need.'),
    ('ואז יצאו חיילים מבין העצים ולקחו את שניהם בלי לומר מילה.', 'And then soldiers came out from among the trees and took them both without a word.')),
  P(('הקצין אמר שאם ייתנו לו את המילה הסודית של הכניסה לעיר, הוא ישחרר את שניהם מיד.', 'The officer said that if they gave him the secret word for entering the city, he would let them both go at once.'),
    ('הוא הבטיח להם חיים ואוכל, ואמר שאף אחד לא יידע כלום.', 'He promised them their lives and food, and said that nobody would ever know.')),
  P(('שני החברים הסתכלו זה על זה ולא אמרו כלום בכלל.', 'The two friends looked at each other and said nothing at all.'),
    ('הקצין חיכה בשקט, שאל אותם שוב, ואז נתן סימן קטן לחיילים שלו.', 'The officer waited quietly, asked them again, and then gave a small sign to his soldiers.'),
    ('אחרי זה הוא לקח את הדגים והביא אותם למטבח שלו.', 'Afterwards he took the fish and brought them to his kitchen.'))]),

 ('In the Fields', 'בשדות', [
  P(('שתי משפחות עניות גרו בשני בתים קטנים ליד אותה דרך.', 'Two poor families lived in two small houses beside the same road.'),
    ('לכל אחת היו ארבעה ילדים, וכולם שיחקו יחד בבוץ מול הבתים.', 'Each had four children, and they all played together in the mud in front of the houses.')),
  P(('יום אחד עצרה שם כרכרה יפה, ומתוכה ירדה אישה עשירה.', 'One day a fine carriage stopped there, and a rich woman got out of it.'),
    ('היא הסתכלה על הילדים זמן רב, ואז דיברה עם הבעל שלה בשקט.', 'She looked at the children for a long time, and then spoke quietly with her husband.')),
  P(('היא נכנסה לבית הראשון וביקשה לקחת את הילד הקטן לגדל אותו.', 'She went into the first house and asked to take the small child and bring him up.'),
    ('היא הבטיחה כסף כל חודש, ושהילד ילמד ויהיה לו הכול.', 'She promised money every month, and that the child would study and have everything.')),
  P(('האישה בבית הראשון צעקה עליה בקול גדול ואמרה לה לצאת מיד.', 'The woman in the first house shouted at her loudly and told her to get out at once.'),
    ('בבית השני ישבו, חשבו, שאלו על הכסף, ובסוף אמרו כן.', 'In the second house they sat, thought, asked about the money, and in the end said yes.')),
  P(('שנים אחר כך שתי המשפחות עוד גרו באותם בתים ליד הדרך.', 'Years later the two families still lived in the same houses beside the road.'),
    ('אחת קיבלה כסף כל חודש, והשנייה אמרה שהיא לא מכרה ילד.', 'One received money every month, and the other said that it had not sold a child.')),
  P(('יום אחד חזר לכפר בחור צעיר בבגדים יפים, והוא נכנס לבית השני.', 'One day a young man in fine clothes came back to the village, and he went into the second house.'),
    ('הבן שנשאר בבית הראשון ראה אותו והבין מה יכול היה להיות.', 'The son who had stayed in the first house saw him and understood what might have been.'),
    ('באותו ערב הוא צעק על ההורים שלו, והוא יצא מהבית שלהם לתמיד.', 'That evening he shouted at his parents, and he left their house for good.'))]),

 ('The Beggar', 'הקבצן', [
  P(('בכפר אחד חי איש שלא יכול היה ללכת בלי שתי מקלות.', 'In one village lived a man who could not walk without two sticks.'),
    ('כשהיה קטן עברה עליו עגלה, ומאז הרגליים שלו לא עבדו.', 'When he was small a cart had gone over him, and since then his legs had not worked.')),
  P(('אמא שלו נתנה לו אוכל כל חייה, ואחרי שהיא מתה לא נשאר אף אחד.', 'His mother gave him food all her life, and after she died nobody was left.'),
    ('הוא ישב על יד הדרך וביקש לחם, וכולם הכירו אותו בשם.', 'He sat by the road and asked for bread, and everyone knew him by name.')),
  P(('בהתחלה נתנו לו, ואחר כך התרגלו אליו והפסיקו לראות אותו.', 'At first they gave to him, and afterwards they got used to him and stopped seeing him.'),
    ('הוא הלך משדה לשדה, וכל יום היה קצת יותר קשה מהיום שלפניו.', 'He went from field to field, and every day was a little harder than the day before.')),
  P(('בחורף אחד לא נתנו לו כלום שלושה ימים, והוא היה רעב מאוד.', 'One winter they gave him nothing for three days, and he was very hungry.'),
    ('הוא תפס תרנגולת בחצר של מישהו ואכל אותה מאחורי גדר.', 'He caught a hen in someone’s yard and ate it behind a fence.')),
  P(('הביאו שוטרים, והם לקחו אותו והכניסו אותו לחדר סגור עד הבוקר.', 'They fetched policemen, and they took him and put him in a locked room until morning.'),
    ('בבוקר פתחו את הדלת כדי לשאול אותו שאלות ומצאו אותו מת.', 'In the morning they opened the door in order to ask him questions and found him dead.'),
    ('כולם התפלאו מאוד, כי אף אחד לא חשב שהוא חולה.', 'Everyone was very surprised, because nobody had thought he was ill.'))]),

 ('Mother Sauvage', 'האם מהכפר', [
  P(('בזמן המלחמה אישה זקנה חיה לבד בבית קטן בקצה הכפר.', 'During the war an old woman lived alone in a small house at the edge of the village.'),
    ('הבן שלה היה חייל רחוק, והיא חיכתה למכתב ממנו כל בוקר.', 'Her son was a soldier far away, and she waited for a letter from him every morning.')),
  P(('יום אחד הביאו לבית שלה ארבעה חיילים זרים לגור אצלה.', 'One day they brought four foreign soldiers to her house to live with her.'),
    ('הם היו צעירים מאוד, עזרו לה בעבודה בבית, והביאו לה עצים לאש.', 'They were very young, helped her with the work in the house, and brought her wood for the fire.')),
  P(('היא בישלה להם כל ערב, והם הראו לה תמונות של האימהות שלהם.', 'She cooked for them every evening, and they showed her photographs of their mothers.'),
    ('היא לא הבינה את השפה שלהם, אבל הבינה את התמונות היטב.', 'She did not understand their language, but she understood the photographs well.')),
  P(('אחרי חודשיים הגיע מכתב, ובו כתבו שהבן שלה נהרג בקרב.', 'After two months a letter came, in which it was written that her son had been killed in battle.'),
    ('היא ישבה עם המכתב כל היום ולא אמרה לחיילים שום דבר.', 'She sat with the letter all day and said nothing to the soldiers.')),
  P(('בערב היא ביקשה מהם להביא עוד עצים, והם הביאו הרבה.', 'In the evening she asked them to bring more wood, and they brought a great deal.'),
    ('בלילה, כשהם ישנו למעלה, היא סגרה את הדלת והדליקה את הבית.', 'At night, while they slept upstairs, she shut the door and set the house alight.')),
  P(('היא עמדה בחוץ בשקט והסתכלה עד הבוקר, ולא ברחה לשום מקום.', 'She stood outside quietly and watched until morning, and did not run anywhere.'),
    ('כשבאו ושאלו אותה, היא הוציאה מהכיס את המכתב ואת ארבע התמונות.', 'When they came and asked her, she took the letter and the four photographs out of her pocket.'),
    ('היא אמרה שהיא רוצה שידעו את השמות, ואמרה אותם אחד אחד.', 'She said that she wanted the names to be known, and said them one by one.'))]),

 ('The Death of a Clerk', 'המוות של הפקיד', [
  P(('פקיד קטן ישב בתיאטרון והיה מרוצה מהחיים שלו באותו ערב.', 'A small clerk sat in the theatre and was pleased with his life that evening.'),
    ('באמצע ההצגה הוא התעטש, ולא שם לב במי בדיוק פגע.', 'In the middle of the play he sneezed, and did not notice whom exactly it reached.')),
  P(('לפניו ישב באותו ערב איש מבוגר וחשוב מאוד מהמשרד הגדול בעיר.', 'In front of him that evening sat an older and very important man from the big office in the city.'),
    ('הפקיד התכופף מיד וביקש סליחה, והאיש אמר שזה לא נורא.', 'The clerk bent forward at once and apologised, and the man said it was nothing.')),
  P(('אחרי חמש דקות הפקיד ביקש סליחה שוב, כי לא היה בטוח.', 'Five minutes later the clerk apologised again, because he was not sure.'),
    ('האיש אמר שכבר שכח מזה, וביקש לשמוע את ההצגה בשקט.', 'The man said he had already forgotten it, and asked to hear the play in peace.')),
  P(('בבית הפקיד לא ישן, וסיפר לאישה שלו את כל הסיפור.', 'At home the clerk did not sleep, and told his wife the whole story.'),
    ('בבוקר הוא לבש בגדים טובים והלך למשרד של האיש להסביר.', 'In the morning he put on good clothes and went to the man’s office to explain.')),
  P(('הוא בא שלושה ימים ברציפות, וכל פעם הסביר את זה מחדש.', 'He came three days in a row, and each time explained it afresh.'),
    ('ביום הרביעי האיש איבד את הסבלנות וצעק עליו לצאת מהחדר.', 'On the fourth day the man lost his patience and shouted at him to get out of the room.')),
  P(('הפקיד יצא, הלך הביתה ברגליים, ולא הרגיש את הדרך בכלל.', 'The clerk went out, walked home on foot, and did not feel the way at all.'),
    ('הוא נכנס הביתה בשקט, שכב על הספה עם הבגדים, ומת שם באותו ערב.', 'He went into the house quietly, lay down on the sofa in his clothes, and died there that evening.'))]),

 ('The Chameleon', 'איש שמשנה צבע', [
  P(('שוטר עבר בשוק בבוקר שקט, ומאחוריו הלך אדם עם סל.', 'A policeman was crossing the market on a quiet morning, and behind him walked a man with a basket.'),
    ('פתאום נשמעה צעקה, ואיש יצא מהחצר וצעק שכלב נשך אותו.', 'Suddenly a shout was heard, and a man came out of a yard shouting that a dog had bitten him.')),
  P(('השוטר הסתכל על הכלב הקטן ואמר שצריך להרוג אותו מיד.', 'The policeman looked at the little dog and said that it should be killed at once.'),
    ('הוא אמר שאסור שכלבים קטנים כאלה יסתובבו חופשי ברחובות של העיר.', 'He said that small dogs like this must not go about the streets of the city free.')),
  P(('מישהו בקהל אמר בשקט שהכלב הזה אולי שייך לאיש חשוב.', 'Someone in the crowd said quietly that this dog might belong to an important man.'),
    ('השוטר עצר, חשב, ואמר שהאיש בטח הרגיז את הכלב בעצמו.', 'The policeman stopped, thought, and said that the man had surely annoyed the dog himself.')),
  P(('מישהו אחר אמר שזה לא הכלב שלו, ושהוא בטוח בזה לגמרי.', 'Someone else said that it was not his dog, and that he was quite sure of it.'),
    ('השוטר כעס שוב ואמר שכלב בלי בעלים צריך ללכת מפה.', 'The policeman was angry again and said that a dog with no owner must be taken away.')),
  P(('ואז עבר שם הטבח של אותו בית, ואמרו לו לומר את האמת.', 'And then the cook of that house passed by, and they told him to say the truth.'),
    ('הוא הסתכל ואמר שהכלב שייך לאח של האיש החשוב, שבא אתמול.', 'He looked and said that the dog belonged to the important man’s brother, who had come yesterday.'),
    ('השוטר חייך, ליטף את הכלב, ואמר לאיש הפצוע ללכת הביתה.', 'The policeman smiled, stroked the dog, and told the injured man to go home.'))]),

 ('Fat and Thin', 'שוב השמן והרזה', [
  P(('שני פקידים עבדו שנים באותו משרד, אחד גדול ואחד קטן.', 'Two clerks had worked for years in the same office, one senior and one junior.'),
    ('הם ישבו קרוב, אכלו יחד, ודיברו על הכול חוץ מהעבודה.', 'They sat close together, ate together, and talked about everything except work.')),
  P(('יום אחד קיבל הקטן מכתב שהוא עולה לתפקיד חדש וגבוה.', 'One day the junior got a letter saying that he was rising to a new and high position.'),
    ('הוא לא סיפר לאף אחד יומיים, ורק חייך לעצמו בשקט.', 'He told nobody for two days, and only smiled to himself quietly.')),
  P(('כשהחבר שלו שמע, הוא לחץ לו את היד ואמר מזל טוב.', 'When his friend heard, he shook his hand and said congratulations.'),
    ('אבל למחרת בבוקר הוא כבר קם מהכיסא שלו כשהחבר נכנס לחדר.', 'But the next morning he already got up from his chair when the friend came into the room.')),
  P(('אחרי שבוע הוא הפסיק לקרוא לו בשם והתחיל לקרוא לו אדוני.', 'After a week he stopped calling him by name and started calling him sir.'),
    ('הם לא אכלו יחד יותר, כי זה כבר לא נראה מתאים.', 'They no longer ate together, because it no longer seemed suitable.')),
  P(('החבר החדש בתפקיד ניסה לדבר איתו כמו קודם, ולא הצליח.', 'The friend in the new position tried to talk to him as before, and did not succeed.'),
    ('בסוף גם הוא התרגל למצב החדש, והפסיק לנסות אחרי חודש בערך.', 'In the end he too got used to the new state of things, and stopped trying after about a month.'))]),

 ('The Lottery Ticket', 'כרטיס ההגרלה', [
  P(('בערב אחד איש ישב עם האישה שלו וקרא את העיתון בשקט.', 'One evening a man sat with his wife and read the paper quietly.'),
    ('היא ביקשה שיבדוק את המספרים, כי היה לה כרטיס בארון.', 'She asked him to check the numbers, because she had a ticket in the cupboard.')),
  P(('הוא הסתכל וראה שהמספר הראשון בעיתון הוא בדיוק המספר שלה.', 'He looked and saw that the first number in the paper was exactly her number.'),
    ('הוא לא בדק את השאר, והשאיר את העיתון על הברכיים.', 'He did not check the rest, and left the paper on his knees.')),
  P(('הוא התחיל לחשוב מה יקנה, ואיפה הם יגורו, ולאן ייסעו.', 'He began to think what he would buy, and where they would live, and where they would travel.'),
    ('הוא ראה בית עם גינה, נהר קרוב, וערבים ארוכים בלי עבודה.', 'He saw a house with a garden, a river nearby, and long evenings without work.')),
  P(('ואז הוא נזכר שהכרטיס הוא שלה ולא שלו, וזה שינה משהו.', 'And then he remembered that the ticket was hers and not his, and that changed something.'),
    ('הוא חשב על המשפחה שלה שתבוא, ועל האחות שלה שתדבר.', 'He thought about her family who would come, and about her sister who would talk.')),
  P(('הוא הסתכל עליה והיא נראתה לו זקנה, קטנה ולא נעימה.', 'He looked at her and she seemed to him old, small and unpleasant.'),
    ('הוא כמעט אמר לה משהו רע, ואז לקח את העיתון בחזרה.', 'He almost said something unkind to her, and then took the paper back.')),
  P(('הוא בדק את שאר המספרים, והם לא היו המספרים שלה.', 'He checked the rest of the numbers, and they were not her numbers.'),
    ('שניהם שתקו זמן ארוך, והחדר נראה להם פתאום קטן וחשוך מאוד.', 'They both fell silent for a long time, and the room suddenly seemed to them small and very dark.'))]),

 ('Vanka', 'ואנקה', [
  P(('ילד בן תשע עבד אצל נגר בעיר, ולמד את המקצוע.', 'A boy of nine worked for a carpenter in the city, and was learning the trade.'),
    ('קראו לו ואנקה, וההורים שלו מתו כשהוא היה עוד קטן מאוד.', 'His name was Vanka, and his parents had died when he was still very small.')),
  P(('בלילה של חג, כשכל האנשים בבית יצאו, הוא הוציא נייר ועט.', 'On the night of a holiday, when all the people in the house had gone out, he took out paper and a pen.'),
    ('הוא ישב על הרצפה הקרה ליד החלון והתחיל לכתוב מכתב לסבא שלו בכפר.', 'He sat on the cold floor by the window and began to write a letter to his grandfather in the village.')),
  P(('הוא כתב שהאדון מכה אותו, ושהוא ישן במסדרון בלי שמיכה.', 'He wrote that the master beat him, and that he slept in the passage without a blanket.'),
    ('הוא כתב שהוא רעב כל הזמן, ושהילדים האחרים בבית צוחקים עליו.', 'He wrote that he was hungry all the time, and that the other children in the house laughed at him.')),
  P(('הוא ביקש מהסבא לבוא ולקחת אותו, ואמר שיעשה כל עבודה.', 'He asked his grandfather to come and take him, and said that he would do any work.'),
    ('הוא הזכיר את הכלב של הסבא, את היער בחורף ואת האור בבית.', 'He mentioned his grandfather’s dog, the forest in winter and the light in the house.')),
  P(('הוא קיפל את הנייר לשניים, שם אותו במעטפה ישנה, וכתב עליה כתובת.', 'He folded the paper in two, put it in an old envelope, and wrote an address on it.'),
    ('הוא כתב את השם של הסבא ואת שם הכפר, ולא הוסיף שום דבר אחר.', 'He wrote his grandfather’s name and the name of the village, and added nothing else.')),
  P(('הוא רץ החוצה בלי מעיל ושם את המכתב בתיבה הראשונה שראה.', 'He ran outside without a coat and put the letter in the first box he saw.'),
    ('הוא חזר לבית, שכב על הרצפה, והשינה באה מהר, ובחלום הוא ראה את הסבא קורא את המכתב.', 'He came back to the house, lay down on the floor, and sleep came quickly, and in his dream he saw his grandfather reading the letter.'))]),

 ('Oysters', 'הצדפים', [
  P(('ילד עמד עם אבא שלו ברחוב, ושניהם לא אכלו יומיים.', 'A boy stood with his father in the street, and neither had eaten for two days.'),
    ('האבא איבד את העבודה שלו, ולא רצה לבקש כסף מאנשים ברחוב.', 'The father had lost his job, and did not want to ask people in the street for money.')),
  P(('הילד הרגיש חלש מאוד, והוא הסתכל על החלונות של המסעדות בלי להבין כלום.', 'The boy felt very weak, and he looked at the restaurant windows without understanding anything.'),
    ('על שלט אחד הייתה מילה שהוא לא הכיר, והוא שאל מה זה.', 'On one sign was a word he did not know, and he asked what it was.')),
  P(('האבא הסביר לו שזאת חיה קטנה שחיה בים, ושאוכלים אותה חיה.', 'The father explained to him that it was a small creature that lives in the sea, and that it is eaten alive.'),
    ('הילד לא הבין את זה בכלל, וחשב על זה זמן רב.', 'The boy did not understand that at all, and thought about it for a long time.')),
  P(('הוא דמיין חיה קטנה עם עיניים, שוכבת על צלחת ומסתכלת.', 'He imagined a small creature with eyes, lying on a plate and looking.'),
    ('הוא הרגיש רע מאוד, ובכל זאת אמר בקול שהוא רוצה לאכול את זה.', 'He felt very ill, and all the same said aloud that he wanted to eat it.')),
  P(('שני אנשים שעברו שם בדרך שמעו אותו וצחקו, והכניסו אותו למסעדה.', 'Two men who were passing on the road heard him and laughed, and took him into the restaurant.'),
    ('הם שמו לפניו צלחת מלאה, הסתכלו עליו בשקט, ואמרו לו לאכול.', 'They put a full plate in front of him, watched him quietly, and told him to eat.')),
  P(('הוא אכל מהר מאוד, בלי ללעוס בכלל ובלי להרים את הראש מהצלחת.', 'He ate very fast, without chewing at all and without raising his head from the plate.'),
    ('אחר כך הוא יצא ומצא את אבא שלו עומד באותו מקום בדיוק.', 'Afterwards he went out and found his father standing in exactly the same place.'))]),

 ('The Complaints Book', 'ספר התלונות', [
  P(('בתחנת רכבת קטנה עמד שולחן, ועליו ספר לתלונות של נוסעים.', 'At a small railway station stood a table, and on it a book for passengers’ complaints.'),
    ('הספר היה פתוח על השולחן כל היום, ואף אחד לא שמר עליו.', 'The book lay open on the table all day, and nobody guarded it.')),
  P(('נוסע אחד כתב שהפקיד בתחנה לא ענה לו בכלל כשביקש מידע.', 'One passenger wrote that the clerk at the station had not answered him at all when he asked for information.'),
    ('מתחתיו מישהו אחר כתב שהוא לא מסכים בכלל, ושהפקיד איש טוב.', 'Below him someone else wrote that he did not agree at all, and that the clerk was a good man.')),
  P(('אחר כך כתבו שם שיר קצר על אישה שעברה בתחנה.', 'Afterwards a short poem about a woman who had passed through the station was written there.'),
    ('אחריו מישהו כתב שהוא היה פה, וכתב את השם שלו גדול.', 'After him someone wrote that he had been here, and wrote his name large.')),
  P(('מישהו כתב שאסור לכתוב דברים כאלה בספר רשמי של הרכבת.', 'Someone wrote that it was forbidden to write such things in an official railway book.'),
    ('מתחת לזה כתבו שתי מילים לא יפות על מי שכתב את זה.', 'Under that two unkind words were written about whoever had written it.')),
  P(('בסוף הגיע לתחנה פקיד גדול, קרא את הכול מההתחלה, וכעס מאוד.', 'In the end a senior official came to the station, read it all from the beginning, and was very angry.'),
    ('הוא כתב בסוף הספר שאסור לכתוב בספר, וחתם את השם שלו.', 'He wrote at the end of the book that writing in the book was forbidden, and signed his name.'))]),

 ('The Bet', 'ההתערבות', [
  P(('בנשף אצל איש עשיר דיברו אם עדיף מוות או מאסר לכל החיים.', 'At a party at a rich man’s house they argued whether death or life imprisonment is better.'),
    ('עורך דין צעיר אמר שהוא מוכן לשבת סגור חמש עשרה שנה.', 'A young lawyer said that he was ready to sit locked up for fifteen years.')),
  P(('בעל הבית צחק והבטיח לו סכום כסף עצום אם יעמוד בזה.', 'The host laughed and promised him an enormous sum of money if he stood it.'),
    ('הם חתמו על הנייר, והצעיר עבר לגור בבית קטן בגינה של העשיר.', 'They signed the paper, and the young man went to live in a small house in the rich man’s garden.')),
  P(('בשנים הראשונות הוא ניגן בערבים, שתה יין טוב, וביקש ספרים קלים.', 'In the first years he played music in the evenings, drank good wine, and asked for light books.'),
    ('אחר כך הוא הפסיק לשתות וביקש ספרים על היסטוריה ועל שפות.', 'Afterwards he stopped drinking and asked for books on history and on languages.')),
  P(('בשנים האחרונות הוא קרא רק ספרי דת וספרים על הכוכבים בשמיים.', 'In the last years he read only books of religion and books about the stars in the sky.'),
    ('הוא כמעט לא זז מהכיסא, ומהחלון הקטן ראו אותו יושב שעות בלי לזוז.', 'He hardly moved from his chair, and through the small window they saw him sitting for hours without moving.')),
  P(('בלילה שלפני הסוף העשיר נכנס לשם, כי הכסף שלו כבר נגמר.', 'On the night before the end the rich man went in there, because his money had already run out.'),
    ('על השולחן היה מכתב, ובו כתב האיש שהוא לא רוצה את הכסף.', 'On the table was a letter, in which the man wrote that he did not want the money.')),
  P(('הוא כתב שהוא קרא הכול, ראה הכול בספרים, ולא נשאר לו רצון.', 'He wrote that he had read everything, seen everything in books, and had no desire left.'),
    ('הוא כתב שהוא ייצא שעה לפני הזמן, כדי להפסיד בכוונה.', 'He wrote that he would leave an hour before the time, in order to lose on purpose.'),
    ('בבוקר הוא לא היה שם, והעשיר שמר את המכתב בכספת.', 'In the morning he was not there, and the rich man kept the letter in the safe.'))]),

 ('A Trifle', 'דבר קטן', [
  P(('אישה גרושה חיה עם הבן שלה, ואיש אחד בא לבקר כל יום.', 'A divorced woman lived with her son, and one man came to visit every day.'),
    ('הילד היה אז בן שמונה, והוא לא אהב את האיש הזה בכלל.', 'The boy was eight years old at the time, and he did not like this man at all.')),
  P(('יום אחד האיש ישב עם הילד בחדר וניסה לדבר איתו יפה.', 'One day the man sat with the boy in the room and tried to talk to him nicely.'),
    ('הוא אמר לו שהם צריכים להיות חברים, ושאפשר לספר לו הכול.', 'He told him that they should be friends, and that he could tell him everything.')),
  P(('הילד שתק זמן רב, ואז אמר שיש לו סוד גדול מאוד.', 'The boy was silent for a long time, and then said that he had a very big secret.'),
    ('הוא סיפר שהוא ראה את אבא שלו בסתר, ושאבא בכה.', 'He told him that he had seen his father in secret, and that his father had cried.')),
  P(('הוא ביקש מהאיש לא לספר את זה לאמא, כי אמא תכעס מאוד.', 'He asked the man not to tell it to his mother, because his mother would be very angry.'),
    ('האיש הבטיח לו, והילד הרגיש הקלה גדולה מאוד וסיפר לו עוד דברים.', 'The man promised him, and the boy felt a very great relief and told him more things.')),
  P(('בערב, כשהאם נכנסה, האיש סיפר לה את הכול תוך כדי ארוחה.', 'In the evening, when the mother came in, the man told her everything during the meal.'),
    ('הוא סיפר את זה כמו דבר קטן ומצחיק, וצחק בזמן שדיבר.', 'He told it as a small, funny thing, and laughed while he was speaking.')),
  P(('הילד עמד בדלת של החדר והסתכל על שניהם, ולא אמר מילה אחת.', 'The boy stood in the doorway of the room and watched them both, and did not say a single word.'),
    ('אחר כך הוא הלך לחדר שלו, ומאותו ערב הוא לא סיפר לאף אחד כלום.', 'Afterwards he went to his room, and from that evening he told nobody anything.'))]),

 ('Grief', 'הצער', [
  P(('בערב חורף אחד עמד איש זקן עם עגלה וסוס ברחוב, וחיכה לנוסע.', 'On one winter evening an old man with a cart and a horse stood in the street, and waited for a fare.'),
    ('השלג ירד עליו ועל הסוס, והם לא זזו שעות.', 'The snow fell on him and on the horse, and they did not move for hours.')),
  P(('לפני שבוע מת הבן שלו, והוא רצה מאוד לספר את זה למישהו.', 'A week before, his son had died, and he wanted very much to tell it to someone.'),
    ('הוא לא רצה עצה ולא עזרה מאף אחד, הוא רק רצה שמישהו ישמע אותו.', 'He did not want advice and did not want help from anyone, he only wanted someone to hear him.')),
  P(('הנוסע הראשון מיהר, וכעס עליו שהוא נוסע לאט מדי.', 'The first passenger was in a hurry, and was angry with him for driving too slowly.'),
    ('הוא אמר לו שהבן שלו מת, והנוסע שאל ממה, ולא חיכה לתשובה.', 'He told him that his son had died, and the passenger asked of what, and did not wait for an answer.')),
  P(('אחר כך עלו שלושה צעירים שצחקו ודיברו כל הדרך.', 'Afterwards three young men got in who laughed and talked the whole way.'),
    ('הוא ניסה לספר להם, והם צחקו ואמרו שכולם מתים בסוף.', 'He tried to tell them, and they laughed and said that everyone dies in the end.')),
  P(('בלילה הוא חזר לחצר, ושם עמדו אנשים אחרים עם עגלות והם ישנו.', 'At night he went back to the yard, and other men with carts stood there and they were asleep.'),
    ('הוא העיר אחד מהם, אבל האיש הסתובב והמשיך לישון.', 'He woke one of them, but the man turned over and went on sleeping.'),
    ('הוא ישב לבד על הספסל הקר והחזיק את הראש בשתי הידיים.', 'He sat alone on the cold bench and held his head in both hands.')),
  P(('אחרי חצות הוא קם והלך לרפת לתת לסוס קצת אוכל.', 'After midnight he got up and went to the stable to give the horse a little food.'),
    ('הוא עמד לידו בחושך, ליטף אותו על הצוואר, והתחיל לדבר בשקט.', 'He stood beside it in the dark, stroked its neck, and began to talk quietly.'),
    ('הוא סיפר לו את הכול מההתחלה ועד הסוף, והסוס אכל בשקט והקשיב לו.', 'He told it everything from the beginning to the end, and the horse ate quietly and listened to him.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('shortstories', {'en': 'Twenty Stories: Maupassant & Chekhov',
                                           'he': "עשרים סיפורים: מופסאן וצ'כוב"}, 'advanced',
                          CHAPTERS, unit='Story', unit_he='סיפור', shelf=21, meta=META))
