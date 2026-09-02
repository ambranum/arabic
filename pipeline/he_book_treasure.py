#!/usr/bin/env python3
"""אי המטמון — Stevenson, retold in modern Hebrew, graded to intermediate.

The Hebrew twin of pipeline/book_treasure.py, chapter for chapter. Stevenson died in 1894 and
the book is public domain; this is a retelling from the plot rather than a translation.

WHY IT IS ON THIS SHELF. It is told in the FIRST PERSON by a boy roughly the age of the reader
of any language course's imagined self, which does two useful things at once: it keeps the verbs
in a person a learner uses constantly, and it means every fact arrives as something someone
noticed rather than as narration from above. That is the register spoken Hebrew actually has.

Deliberately unpointed; the vowels are looked up at ingest. The names are declared in
pipeline/he_curated.py.

Run:  python3 pipeline/he_book_treasure.py --lang he            # check
      python3 pipeline/he_book_treasure.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'Treasure Island', 'author': 'Robert Louis Stevenson', 'year': '1883',
        'status': 'public domain'}

CHAPTERS = [
 ('The Old Sea-Dog', 'המלח הזקן', [
  P(('קוראים לי ג\'ים הוקינס, ולמשפחה שלי היה פונדק קטן על יד הים.', 'My name is Jim Hawkins, and my family had a small inn by the sea.'),
    ('יום אחד בא אלינו מלח זקן עם ארגז כבד מאוד.', 'One day an old sailor came to us with a very heavy chest.'),
    ('הוא היה גדול, שרוף מהשמש, ועל הפנים שלו הייתה צלקת ארוכה.', 'He was big, burned by the sun, and on his face was a long scar.')),
  P(('הוא אמר לאבא שלי: אני נשאר פה, ואל תשאלו אותי שאלות.', 'He said to my father: I am staying here, and do not ask me questions.'),
    ('כל ערב הוא שתה ושר שירים על מלחים ועל ים.', 'Every evening he drank and sang songs about sailors and about the sea.'),
    ('האנשים בפונדק פחדו ממנו, אבל גם אהבו לשמוע אותו.', 'The people in the inn were afraid of him, but also liked to listen to him.')),
  P(('הוא נתן לי כסף וביקש דבר אחד: לחפש מלח עם רגל אחת.', 'He gave me money and asked one thing: to look out for a sailor with one leg.'),
    ('אמרתי לו שאסתכל, ולא הבנתי למה הוא מפחד כל כך.', 'I told him I would watch, and I did not understand why he was so afraid.'))]),

 ('Black Dog', 'הכלב השחור', [
  P(('בבוקר קר בא לפונדק איש חיוור עם שתי אצבעות חסרות.', 'On a cold morning a pale man with two fingers missing came to the inn.'),
    ('הוא שאל על המלח הזקן וחיכה לו בשקט בפינה.', 'He asked about the old sailor and waited for him quietly in the corner.')),
  P(('כשהמלח נכנס וראה אותו, הפנים שלו נהיו לבנות.', 'When the sailor came in and saw him, his face went white.'),
    ('הם דיברו בשקט, ואחר כך התחילו לצעוק אחד על השני.', 'They talked quietly, and afterwards began shouting at each other.')),
  P(('הם הוציאו חרבות, והשולחן נשבר, והאיש ברח החוצה.', 'They drew swords, and the table broke, and the man ran outside.'),
    ('המלח הזקן נפל על הרצפה, ואמא שלי רצה להביא מים.', 'The old sailor fell on the floor, and my mother ran to bring water.'),
    ('הוא אמר לי: הם רוצים את הארגז שלי, ואני חייב לצאת מפה.', 'He said to me: they want my chest, and I must get out of here.'))]),

 ('The Black Spot', 'הכתם השחור', [
  P(('אחרי כמה ימים בא איש עיוור עם מקל וביקש שאביא אותו אליו.', 'A few days later a blind man with a stick came and asked me to bring him to him.'),
    ('הוא לחץ לי על היד חזק מאוד, עד שכאב.', 'He pressed my hand very hard, until it hurt.')),
  P(('הוא שם משהו ביד של המלח והלך מהר.', 'He put something in the sailor’s hand and went away fast.'),
    ('המלח פתח את היד וראה נייר עגול עם כתם שחור.', 'The sailor opened his hand and saw a round paper with a black spot.')),
  P(('הוא אמר: יש לי זמן עד עשר, ואחר כך הם באים.', 'He said: I have until ten, and after that they are coming.'),
    ('הוא ניסה לקום, החזיק את הלב, והוא נפל.', 'He tried to get up, held his heart, and he fell.'),
    ('באותו רגע הבנתי שהמלח הזקן מת.', 'At that moment I understood that the old sailor was dead.'))]),

 ('The Sea Chest', 'ארגז המלח', [
  P(('אמא שלי אמרה: הוא היה חייב לנו כסף, ואנחנו ניקח רק את שלנו.', 'My mother said: he owed us money, and we will take only what is ours.'),
    ('פתחנו את הארגז בחדר שלו והדלקנו נר אחד.', 'We opened the chest in his room and lit one candle.')),
  P(('בפנים היו בגדים, סכין, שני אקדחים ושקית כסף.', 'Inside were clothes, a knife, two pistols and a bag of money.'),
    ('מתחת לכול היה חבילה של ניירות קשורה בחוט.', 'Under everything was a packet of papers tied with string.')),
  P(('שמעתי קול בדרך, ואמרתי לאמא שצריך לברוח מיד.', 'I heard a sound on the road, and told my mother we had to run at once.'),
    ('לקחתי את הניירות, והיא לקחה את הכסף שהגיע לנו.', 'I took the papers, and she took the money that was owed to us.'),
    ('יצאנו מהדלת של המטבח וברחנו לגשר הקטן.', 'We went out of the kitchen door and fled to the little bridge.'))]),

 ('The Blind Man', 'העיוור', [
  P(('התחבאנו מתחת לגשר ושמענו אנשים רצים לפונדק.', 'We hid under the bridge and heard men running to the inn.'),
    ('הם שברו את הדלת, נכנסו פנימה וצעקו.', 'They broke the door, went in and shouted.')),
  P(('העיוור עמד בחוץ וצעק להם: תמצאו את הניירות.', 'The blind man stood outside and shouted to them: find the papers.'),
    ('הם חיפשו בכל החדרים ולא מצאו את מה שרצו.', 'They searched all the rooms and did not find what they wanted.')),
  P(('פתאום שמענו סוסים באים מהר בדרך.', 'Suddenly we heard horses coming fast on the road.'),
    ('השודדים ברחו לכל הכיוונים, והעיוור נשאר לבד ברחוב.', 'The robbers fled in all directions, and the blind man was left alone in the street.'),
    ('הוא לא ראה לאן ללכת, והסוסים עברו עליו.', 'He could not see where to go, and the horses went over him.'))]),

 ('The Captain’s Papers', 'הניירות של המלח', [
  P(('לקחתי את הניירות לדוקטור ליבסי, שהיה גם שופט בעיירה.', 'I took the papers to Doctor Livesey, who was also a judge in the town.'),
    ('אצלו ישב טרלוני, איש עשיר שאהב מאוד ספינות.', 'With him sat Trelawney, a rich man who loved ships very much.')),
  P(('פתחנו את החבילה, ובפנים הייתה מפה של אי קטן.', 'We opened the packet, and inside was a map of a small island.'),
    ('על המפה היה כתוב איפה פלינט שם את הזהב שלו.', 'On the map was written where Flint had put his gold.')),
  P(('טרלוני קם וצעק: אני קונה ספינה, ואנחנו נוסעים.', 'Trelawney stood up and shouted: I am buying a ship, and we are going.'),
    ('ליבסי אמר: טוב, אבל אל תספר לאף אחד מילה.', 'Livesey said: fine, but do not tell anyone a word.'),
    ('טרלוני הבטיח לשתוק, ולא שתק אפילו יום אחד.', 'Trelawney promised to keep quiet, and did not keep quiet even one day.'))]),

 ('To Bristol', 'לבריסטול', [
  P(('אחרי כמה שבועות קיבלתי מכתב מטרלוני מבריסטול.', 'A few weeks later I got a letter from Trelawney in Bristol.'),
    ('הוא כתב שקנה ספינה יפה ומצא אנשים טובים.', 'He wrote that he had bought a fine ship and found good men.')),
  P(('נסעתי לבריסטול ופגשתי אותו בנמל.', 'I travelled to Bristol and met him at the port.'),
    ('הוא סיפר לי בשמחה על הטבח שהוא מצא, מלח עם רגל אחת.', 'He told me happily about the cook he had found, a sailor with one leg.')),
  P(('שמעתי את זה ונזכרתי במלח הזקן ובפחד שלו.', 'I heard that and remembered the old sailor and his fear.'),
    ('אבל לא אמרתי כלום, כי טרלוני היה מאושר מדי.', 'But I said nothing, because Trelawney was too happy.'))]),

 ('The Sign of the Spy-glass', 'הפונדק של סילבר', [
  P(('הלכתי לפונדק של הטבח כדי לתת לו מכתב.', 'I went to the cook’s inn in order to give him a letter.'),
    ('בפנים ישבו מלחים, וביניהם עמד איש גדול על רגל אחת.', 'Inside sat sailors, and among them stood a big man on one leg.')),
  P(('הוא חייך אליי, דיבר יפה, ושאל אותי על עצמי.', 'He smiled at me, spoke nicely, and asked me about myself.'),
    ('קראו לו ג\'ון סילבר, ומיד אהבתי אותו.', 'His name was John Silver, and I liked him at once.')),
  P(('הוא לא נראה כמו האיש שהמלח הזקן פחד ממנו.', 'He did not look like the man the old sailor had feared.'),
    ('חשבתי שטעיתי, ושהמלח הזקן פחד מהצל של עצמו.', 'I thought I had been wrong, and that the old sailor had feared his own shadow.'),
    ('לקחו לי שנים להבין כמה טעיתי באותו רגע.', 'It took me years to understand how wrong I was at that moment.'))]),

 ('Powder and Arms', 'נשק וכלים', [
  P(('סמולט, המפקד של הספינה, בא לספינה ולא היה מרוצה מכלום.', 'Smollett, the ship’s commander, came aboard and was not pleased with anything.'),
    ('הוא אמר: כל הנמל יודע לאן אנחנו נוסעים ולמה.', 'He said: the whole port knows where we are going and why.')),
  P(('הוא ביקש לשים את הנשק ואת אבק השרפה קרוב לחדרים שלנו.', 'He asked to put the arms and the powder near our own cabins.'),
    ('טרלוני כעס, אבל ליבסי אמר שסמולט צודק.', 'Trelawney was angry, but Livesey said Smollett was right.')),
  P(('סידרנו הכול, ובערב הספינה יצאה לים.', 'We arranged everything, and in the evening the ship put out to sea.'),
    ('סילבר בישל טוב, שר שירים, וכולם אהבו אותו.', 'Silver cooked well, sang songs, and everyone loved him.'),
    ('גם אני הייתי בטוח שאנחנו בידיים טובות.', 'I too was sure that we were in good hands.'))]),

 ('The Voyage', 'המסע', [
  P(('הימים בים היו ארוכים ושקטים, והרוח הייתה טובה.', 'The days at sea were long and quiet, and the wind was good.'),
    ('עבדתי במטבח ליד סילבר ושמעתי את כל הסיפורים שלו.', 'I worked in the galley beside Silver and heard all his stories.')),
  P(('היה לו תוכי על הכתף שצעק כל היום מילה אחת.', 'He had a parrot on his shoulder that shouted one word all day.'),
    ('הוא אמר שהתוכי הזה עבר ים יותר מכל מלח בספינה.', 'He said that this parrot had crossed more sea than any sailor on the ship.')),
  P(('סמולט לא אהב את האנשים, אבל לא אמר למה.', 'Smollett did not like the men, but did not say why.'),
    ('חשבתי שהוא סתם איש קשה, ולא חשבתי יותר מזה.', 'I thought he was just a hard man, and thought no more of it.'))]),

 ('What I Heard in the Apple Barrel', 'מה שמעתי בחבית', [
  P(('בערב אחד רציתי תפוח ונכנסתי לתוך חבית התפוחים.', 'One evening I wanted an apple and got into the apple barrel.'),
    ('החבית הייתה כמעט ריקה, ונשארתי בפנים ונרדמתי קצת.', 'The barrel was nearly empty, and I stayed inside and dozed off a little.')),
  P(('התעוררתי כששמעתי את הקול של סילבר ממש לידי.', 'I woke when I heard Silver’s voice right beside me.'),
    ('הוא דיבר עם מלח צעיר ואמר לו: אני הייתי אצל פלינט.', 'He was talking to a young sailor and said: I sailed with Flint.')),
  P(('הוא אמר: כשנמצא את הזהב, ניקח את הספינה לעצמנו.', 'He said: when we find the gold, we will take the ship for ourselves.'),
    ('הוא אמר: את סמולט ואת השאר נשאיר על האי.', 'He said: Smollett and the rest we will leave on the island.'),
    ('שכבתי בחבית בלי לזוז ופחדתי לנשום.', 'I lay in the barrel without moving and was afraid to breathe.'))]),

 ('Council of War', 'ישיבה בלילה', [
  P(('כשכולם ישנו סיפרתי הכול לסמולט, לדוקטור ולטרלוני.', 'When everyone was asleep I told everything to Smollett, the doctor and Trelawney.'),
    ('הם הקשיבו בשקט, ואף אחד לא הפסיק אותי.', 'They listened quietly, and nobody interrupted me.')),
  P(('המפקד אמר: אנחנו שלושה ואתה, והם תשעה עשר.', 'The commander said: we are three and you, and they are nineteen.'),
    ('ליבסי אמר: יש לנו הנשק, וזה משהו.', 'Livesey said: we have the arms, and that is something.')),
  P(('החלטנו לא להראות שאנחנו יודעים, עד שנגיע לאי.', 'We decided not to show that we knew, until we reached the island.'),
    ('טרלוני אמר לי: ג\'ים, הצלת את כולנו הערב.', 'Trelawney said to me: Jim, you saved us all tonight.'))]),

 ('The Island', 'האי', [
  P(('בבוקר ראינו את האי, אפור וירוק מתחת לעננים.', 'In the morning we saw the island, grey and green under the clouds.'),
    ('היו בו שלושה הרים, ואחד גבוה מהאחרים.', 'There were three hills on it, and one higher than the others.')),
  P(('הריח מהחוף היה של עצים רטובים ושל משהו ישן.', 'The smell from the shore was of wet trees and of something old.'),
    ('כל המלחים דיברו בשקט, ומשהו באוויר השתנה.', 'All the sailors talked quietly, and something in the air changed.')),
  P(('סילבר הסתכל על ההרים כמו מישהו שחוזר הביתה.', 'Silver looked at the hills like someone coming home.'),
    ('הבנתי שהוא היה פה, ושהוא זוכר כל דבר.', 'I understood that he had been here, and that he remembered everything.'))]),

 ('Ashore', 'יורדים לחוף', [
  P(('המפקד נתן לאנשים לרדת לחוף, כדי שלא יכעסו.', 'The commander let the men go ashore, so that they would not be angry.'),
    ('שלוש עשרה מלחים ירדו, ואני קפצתי לסירה הראשונה.', 'Thirteen sailors went down, and I jumped into the first boat.')),
  P(('כשהגענו לחול, ברחתי מיד בין העצים.', 'When we reached the sand, I ran off at once among the trees.'),
    ('שמעתי מאחוריי את סילבר קורא לי בשם.', 'I heard Silver behind me calling my name.')),
  P(('רצתי עד שלא שמעתי כלום, ואז שכבתי על האדמה.', 'I ran until I heard nothing, and then lay on the ground.'),
    ('אחרי כמה דקות שמעתי קולות של שני אנשים מדברים.', 'After a few minutes I heard the voices of two men talking.'),
    ('אחד מהם היה סילבר, והשני צעק ואז שתק לתמיד.', 'One of them was Silver, and the other shouted and then was silent for ever.'))]),

 ('The Man of the Island', 'האיש של האי', [
  P(('הלכתי בין הסלעים וראיתי משהו זז מהר מאחורי עץ.', 'I walked among the rocks and saw something move fast behind a tree.'),
    ('חשבתי שזו חיה, אבל זה היה אדם.', 'I thought it was an animal, but it was a man.')),
  P(('הוא היה רזה מאוד, שרוף, ולבוש בעורות ובבדים ישנים.', 'He was very thin, sunburned, and dressed in skins and old cloth.'),
    ('הוא אמר: קוראים לי גאן, ואני פה שלוש שנים לבד.', 'He said: my name is Gunn, and I have been here three years alone.')),
  P(('הוא סיפר שפלינט הביא אותו, ושהחברים שלו השאירו אותו.', 'He told me that Flint had brought him, and that his friends had left him.'),
    ('הוא ביקש רק דבר אחד: גבינה, כי חלם עליה כל לילה.', 'He asked for only one thing: cheese, because he dreamed of it every night.'),
    ('אמרתי לו שיש לנו, והוא צחק וגם בכה.', 'I told him we had some, and he laughed and also cried.'))]),

 ('The Ship Abandoned', 'עוזבים את הספינה', [
  P(('בזמן שאני הייתי ביער, הדוקטור החליט לעזוב את הספינה.', 'While I was in the forest, the doctor decided to leave the ship.'),
    ('הוא ראה מבנה עץ ישן על הגבעה, עם קיר וחצר.', 'He saw an old wooden building on the hill, with a wall and a yard.')),
  P(('הם לקחו נשק, אוכל ומים בסירה קטנה.', 'They took arms, food and water in a small boat.'),
    ('הסירה הייתה כבדה מדי, והמים כמעט נכנסו פנימה.', 'The boat was too heavy, and the water almost came in.')),
  P(('השודדים ראו אותם וירו עליהם מהספינה.', 'The robbers saw them and fired at them from the ship.'),
    ('הם הגיעו לחוף רטובים, ואיבדו חצי מהאוכל בדרך.', 'They reached the shore wet, and lost half the food on the way.'))]),

 ('The Last Boat', 'הסירה האחרונה', [
  P(('בתוך המבנה סידרו הכול ושמו את הנשק ליד הקיר.', 'Inside the building they arranged everything and put the arms by the wall.'),
    ('היה קר, והם הדליקו אש קטנה באמצע.', 'It was cold, and they lit a small fire in the middle.')),
  P(('אני הגעתי לשם עם גאן בערב, מהצד השני של הגבעה.', 'I got there with Gunn in the evening, from the other side of the hill.'),
    ('כשראו אותי, כולם שמחו, כי חשבו שאני מת.', 'When they saw me, they were all glad, because they thought I was dead.')),
  P(('סיפרתי להם על גאן ועל הסירה הקטנה שהוא בנה.', 'I told them about Gunn and about the little boat he had built.'),
    ('סמולט אמר: זה יכול להיות שווה יותר מכל הזהב.', 'The commander said: that may be worth more than all the gold.'))]),

 ('The First Day’s Fighting', 'היום הראשון של הקרב', [
  P(('בבוקר ראינו דגל שחור על הספינה שלנו.', 'In the morning we saw a black flag on our ship.'),
    ('השודדים ירו לכיוון המבנה מבין העצים.', 'The robbers fired towards the building from among the trees.')),
  P(('המפקד אמר: תשמרו על הכדורים, אל תירו סתם.', 'The commander said: save the shot, do not fire for nothing.'),
    ('כל אחד מאיתנו עמד ליד חלון אחר.', 'Each of us stood by a different window.')),
  P(('ירו עלינו כל הבוקר, ואף אחד לא נפגע.', 'They fired at us all morning, and nobody was hit.'),
    ('אחרי הצהריים היה שקט, וזה הפחיד אותנו יותר.', 'In the afternoon there was quiet, and that frightened us more.'))]),

 ('The Garrison in the Stockade', 'המבנה על הגבעה', [
  P(('ליבסי טיפל באנשים שנפגעו ובדק את המים והאוכל.', 'Livesey looked after the men who had been hit and checked the water and food.'),
    ('היה לנו אוכל לעשרה ימים, לא יותר.', 'We had food for ten days, no more.')),
  P(('סמולט כתב הכול ביומן: מי חי, מי מת, כמה נשאר.', 'Smollett wrote everything in the log: who was alive, who dead, how much was left.'),
    ('הוא כתב בשקט, בלי לשנות את הקול שלו.', 'He wrote quietly, without changing his voice.')),
  P(('בלילה שמענו שירה מהחוף, כי השודדים שתו.', 'At night we heard singing from the shore, because the robbers were drinking.'),
    ('גאן אמר: הם שותים כי הם מפחדים מהמקום הזה.', 'Gunn said: they drink because they are afraid of this place.'),
    ('שכבתי על הרצפה ולא הצלחתי להירדם.', 'I lay on the floor and could not fall asleep.'))]),

 ('Silver’s Embassy', 'סילבר בא לדבר', [
  P(('בבוקר בא סילבר לבד עם דגל לבן ביד.', 'In the morning Silver came alone with a white flag in his hand.'),
    ('הוא עלה על הגבעה לאט, כי רגל אחת לא עוזרת בהר.', 'He came up the hill slowly, because one leg does not help on a slope.')),
  P(('הוא אמר: תנו לי את המפה, ואנחנו ניתן לכם לחיות.', 'He said: give me the map, and we will let you live.'),
    ('המפקד אמר: לא. עכשיו לך, ולך לאט.', 'The commander said: no. Now go, and go slowly.')),
  P(('סילבר כעס בפעם הראשונה, וניסה לקום מהר.', 'Silver was angry for the first time, and tried to get up fast.'),
    ('הוא אמר: לפני הערב אתם תבקשו את מה שהצעתי.', 'He said: before evening you will ask for what I offered.'),
    ('הוא ירד מהגבעה, ואחרי שעה התחילה ההתקפה.', 'He went down the hill, and an hour later the attack began.'))]),

 ('The Attack', 'ההתקפה', [
  P(('הם באו מכל הצדדים וקפצו על הקיר.', 'They came from all sides and jumped onto the wall.'),
    ('נלחמנו בחצר, וכולם צעקו ואף אחד לא שמע.', 'We fought in the yard, and everyone shouted and nobody heard.')),
  P(('שניים מאיתנו נפלו, וגם כמה מהם.', 'Two of us fell, and some of them too.'),
    ('אחרי כמה דקות הם ברחו בחזרה ליער.', 'After a few minutes they ran back to the forest.')),
  P(('המפקד נפגע ברגל, והוא שכב ליד הקיר.', 'The commander was hit in the leg, and he lay by the wall.'),
    ('ליבסי טיפל בו ואמר שהוא יחיה, אבל לא ילך מהר.', 'Livesey treated him and said he would live, but would not walk fast.'))]),

 ('I Slip Away', 'אני יוצא בשקט', [
  P(('אחרי הצהריים הדוקטור לקח את המפה, והוא יצא לבד.', 'In the afternoon the doctor took the map, and he went out alone.'),
    ('הבנתי שהוא הולך לגאן, ורציתי גם לעשות משהו.', 'I understood he was going to Gunn, and I wanted to do something too.')),
  P(('לקחתי אוכל ושני אקדחים ויצאתי בלי לומר מילה.', 'I took food and two pistols and went out without saying a word.'),
    ('היום הזה היה הטיפשי והחשוב ביותר בחיים שלי.', 'That day was the most foolish and the most important of my life.')),
  P(('הלכתי לחוף וחיפשתי את הסירה הקטנה של גאן.', 'I went to the shore and looked for Gunn’s little boat.'),
    ('מצאתי אותה מתחת לענפים, קטנה כמו קערה.', 'I found it under branches, small as a bowl.'))]),

 ('The Ebb-Tide Runs', 'המים מושכים', [
  P(('חיכיתי עד הלילה ואז שמתי את הסירה על המים.', 'I waited until night and then put the boat on the water.'),
    ('רציתי לחתוך את החבל של הספינה הגדולה.', 'I wanted to cut the rope of the big ship.')),
  P(('התקרבתי בשקט ושמעתי שני שודדים רבים בפנים.', 'I came close quietly and heard two robbers quarrelling inside.'),
    ('חתכתי את החבל, והספינה התחילה לזוז לאט.', 'I cut the rope, and the ship began to move slowly.')),
  P(('המים לקחו גם אותי, ולא הצלחתי לחזור.', 'The water took me too, and I could not get back.'),
    ('שכבתי בסירה, הסתכלתי על הכוכבים ונרדמתי.', 'I lay in the boat, looked at the stars and fell asleep.'))]),

 ('The Cruise of the Coracle', 'הסירה הקטנה', [
  P(('בבוקר התעוררתי רחוק מהחוף ולא ידעתי איפה אני.', 'In the morning I woke far from the shore and did not know where I was.'),
    ('הסירה הייתה קטנה מדי, וכל גל הרים אותה גבוה.', 'The boat was too small, and every wave lifted it high.')),
  P(('ראיתי את הספינה שלנו נוסעת לבד בין הגלים.', 'I saw our ship moving alone among the waves.'),
    ('אף אחד לא עמד ליד ההגה, והיא הסתובבה במקום.', 'Nobody stood at the wheel, and she turned in place.')),
  P(('חתרתי אליה בידיים כי לא היו לי משוטים.', 'I paddled to her with my hands because I had no oars.'),
    ('כשהיא התקרבה, קפצתי ותפסתי חבל בשתי הידיים.', 'When she came near, I jumped and caught a rope with both hands.'))]),

 ('I Strike the Jolly Roger', 'מוריד את הדגל השחור', [
  P(('עליתי על הספינה ומצאתי שני אנשים על הרצפה.', 'I climbed onto the ship and found two men on the deck.'),
    ('אחד היה מת, והשני היה פצוע ושתוי.', 'One was dead, and the other was wounded and drunk.')),
  P(('קראו לו ישראל הנדס, והוא הסתכל עליי בשקט.', 'His name was Israel Hands, and he looked at me quietly.'),
    ('הורדתי את הדגל השחור וזרקתי אותו למים.', 'I took down the black flag and threw it into the water.')),
  P(('אמרתי לו: הספינה הזאת שלי עכשיו.', 'I said to him: this ship is mine now.'),
    ('הוא צחק ואמר: אז תיקח אותה לחוף, ילד.', 'He laughed and said: then take her to the shore, boy.'))]),

 ('Israel Hands', 'ישראל הנדס', [
  P(('הוא הסביר לי איך להפנות את הספינה, ואני עשיתי.', 'He explained to me how to turn the ship, and I did it.'),
    ('נסענו לאט לכיוון החוף הצפוני של האי.', 'We moved slowly towards the northern shore of the island.')),
  P(('ראיתי בעיניים שלו שהוא מחכה לרגע הנכון.', 'I saw in his eyes that he was waiting for the right moment.'),
    ('כשהסתכלתי הצידה, הוא קם עם סכין ביד.', 'When I looked aside, he got up with a knife in his hand.')),
  P(('עליתי מהר על התורן, והוא בא אחריי לאט.', 'I climbed the mast fast, and he came after me slowly.'),
    ('הוא זרק את הסכין ופגע לי בכתף.', 'He threw the knife and hit me in the shoulder.'),
    ('שני האקדחים שלי ירו, והוא נפל למים.', 'My two pistols fired, and he fell into the water.'))]),

 ('Pieces of Eight', 'מטבעות זהב', [
  P(('קשרתי את הספינה טוב וירדתי לחוף בחושך.', 'I tied the ship well and went ashore in the dark.'),
    ('הכתף כאבה, אבל הייתי מאושר כמו אף פעם.', 'My shoulder hurt, but I was happier than ever.')),
  P(('הלכתי לגבעה כדי לספר לכולם על הספינה.', 'I walked to the hill in order to tell everyone about the ship.'),
    ('נכנסתי בשקט לחצר, כי לא רציתי להעיר אותם.', 'I went quietly into the yard, because I did not want to wake them.')),
  P(('פתאום קול בחושך צעק את המילה של התוכי.', 'Suddenly a voice in the dark shouted the parrot’s word.'),
    ('הדליקו אש, ובאור ראיתי את הפנים של סילבר.', 'They lit a fire, and in the light I saw Silver’s face.'),
    ('הבנתי שהחברים שלי כבר לא במקום הזה.', 'I understood that my friends were no longer in this place.'))]),

 ('In the Enemy’s Camp', 'במחנה של האויב', [
  P(('סילבר אמר לאנשים שלו: הילד הזה שלי, אל תיגעו בו.', 'Silver said to his men: this boy is mine, do not touch him.'),
    ('הם כעסו, אבל אף אחד לא עשה כלום.', 'They were angry, but nobody did anything.')),
  P(('הוא סיפר לי שהדוקטור נתן להם את המפה בבוקר.', 'He told me that the doctor had given them the map in the morning.'),
    ('לא הבנתי למה, ולא שאלתי אותו שאלות.', 'I did not understand why, and I did not ask him questions.')),
  P(('בלילה סילבר ישב לידי ודיבר בשקט.', 'At night Silver sat beside me and spoke quietly.'),
    ('הוא אמר: אני שומר עליך, ואתה תשמור עליי אחר כך.', 'He said: I am keeping you safe, and you will keep me safe afterwards.'))]),

 ('The Black Spot Again', 'שוב הכתם השחור', [
  P(('בבוקר האנשים ישבו בצד ודיברו בלי סילבר.', 'In the morning the men sat aside and talked without Silver.'),
    ('אחר כך אחד מהם בא ונתן לו נייר עגול.', 'Afterwards one of them came and gave him a round paper.')),
  P(('סילבר הסתכל עליו וצחק בקול גדול.', 'Silver looked at it and laughed loudly.'),
    ('הוא אמר: זה נייר מספר קודש, אתם משוגעים.', 'He said: this is paper from a holy book, you are mad.')),
  P(('הוא הוציא מהכיס את המפה של פלינט והרים אותה.', 'He took Flint’s map out of his pocket and held it up.'),
    ('כולם קפצו לראות, ושכחו מיד מה שרצו.', 'They all jumped to see, and forgot at once what they had wanted.'),
    ('סילבר הסתכל עליי וקרץ, כאילו שיחקנו יחד.', 'Silver looked at me and winked, as if we were playing together.'))]),

 ('The Treasure Hunt', 'מחפשים את המטמון', [
  P(('הלכנו כולנו ליער עם המפה ביד של סילבר.', 'We all went to the forest with the map in Silver’s hand.'),
    ('הוא קשר אותי בחבל והחזיק אותי כמו כלב.', 'He tied me with a rope and held me like a dog.')),
  P(('הגענו למקום שעל המפה, וראינו בור פתוח באדמה.', 'We reached the place on the map, and saw an open hole in the ground.'),
    ('הבור היה ריק, וכל הזהב כבר לא היה שם.', 'The hole was empty, and all the gold was no longer there.')),
  P(('השודדים כעסו והרימו את הנשק על סילבר.', 'The robbers were angry and raised their arms against Silver.'),
    ('באותו רגע מישהו ירה מבין העצים.', 'At that moment someone fired from among the trees.'),
    ('ליבסי וגאן יצאו, והשודדים ברחו לכל הכיוונים.', 'Livesey and Gunn came out, and the robbers fled in all directions.')),
  P(('גאן מצא את הזהב לפני חודשים והעביר אותו למערה שלו.', 'Gunn had found the gold months before and moved it to his cave.'),
    ('לקחנו הכול לספינה, ויצאנו מהאי אחרי כמה ימים.', 'We took everything to the ship, and left the island a few days later.'),
    ('סילבר נסע איתנו וברח בנמל הראשון עם שקית זהב.', 'Silver travelled with us and escaped at the first port with a bag of gold.'),
    ('לא ראיתי אותו יותר, ולפעמים אני עוד חולם על התוכי.', 'I never saw him again, and sometimes I still dream about the parrot.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('treasure', {'en': 'Treasure Island', 'he': 'אי המטמון'},
                          'intermediate', CHAPTERS, unit='Chapter', unit_he='פרק',
                          shelf=13, meta=META))
