#!/usr/bin/env python3
"""הרפתקאות טום סוייר — Mark Twain, retold in modern Hebrew, graded to intermediate.

The Hebrew twin of pipeline/book_tomsawyer.py, chapter for chapter. Twain died in 1910 and the
book is public domain; this is a retelling from the plot rather than a translation.

WHY IT CLOSES THE INTERMEDIATE SHELF. Everything before it happens somewhere far away — an
island, a voyage, a forest of talking animals. This one happens in a small town where people go
to school, sit in class, get bored, fall out with each other and make up. That is where a
learner's own Hebrew has to work, and it is the hardest vocabulary to come by from adventure
stories: the words for ordinary weeks.

Deliberately unpointed; the vowels are looked up at ingest. The names are declared in
pipeline/he_curated.py.

Run:  python3 pipeline/he_book_tomsawyer.py --lang he            # check
      python3 pipeline/he_book_tomsawyer.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'The Adventures of Tom Sawyer', 'author': 'Mark Twain', 'year': '1876',
        'status': 'public domain'}

CHAPTERS = [
 ('Tom and Aunt Polly', 'טום ודודה פולי', [
  P(('טום סוייר גר בעיירה קטנה על שפת נהר גדול.', 'Tom Sawyer lived in a small town on the bank of a big river.'),
    ('הוא גר עם דודה פולי, כי ההורים שלו כבר לא היו.', 'He lived with his aunt Polly, because his parents were no longer alive.')),
  P(('דודה פולי אהבה אותו מאוד, אבל כעסה עליו כל יום.', 'Aunt Polly loved him very much, but was angry with him every day.'),
    ('היא קראה לו, והוא לא ענה, כי היה במרתף עם הריבה.', 'She called him, and he did not answer, because he was in the cellar with the jam.')),
  P(('כשהיא תפסה אותו, הוא הצביע מאחוריה וצעק: תראי מה שם.', 'When she caught him, he pointed behind her and shouted: look what is there.'),
    ('היא הסתובבה, והוא קפץ מהחלון וברח.', 'She turned round, and he jumped out of the window and ran.'),
    ('היא צחקה לבד בבית ואמרה: הילד הזה יגמור אותי.', 'She laughed alone in the house and said: that boy will finish me.'))]),

 ('The Fence', 'הגדר', [
  P(('בשבת בבוקר דודה פולי נתנה לטום דלי צבע ומברשת.', 'On Saturday morning Aunt Polly gave Tom a bucket of paint and a brush.'),
    ('היא אמרה: תצבע את כל הגדר, ורק אז תלך לשחק.', 'She said: paint the whole fence, and only then go and play.')),
  P(('הגדר הייתה ארוכה מאוד, וטום ישב עליה והתעצב.', 'The fence was very long, and Tom sat on it and felt miserable.'),
    ('כל החברים שלו הלכו לנהר, והוא נשאר עם הצבע.', 'All his friends went to the river, and he was left with the paint.')),
  P(('ואז בא ילד אחד וצחק עליו, וטום לא ענה לו.', 'And then one boy came and laughed at him, and Tom did not answer him.'),
    ('טום צבע לאט ובזהירות, כאילו זו העבודה הכי חשובה בעולם.', 'Tom painted slowly and carefully, as if it were the most important work in the world.'),
    ('הוא אמר: לא כל ילד יכול לצבוע גדר כמו שצריך.', 'He said: not every boy can paint a fence properly.')),
  P(('הילד ביקש לנסות, וטום אמר שהוא לא בטוח.', 'The boy asked to try, and Tom said he was not sure.'),
    ('בסוף הילד נתן לו תפוח כדי לקבל את המברשת.', 'In the end the boy gave him an apple in order to get the brush.'),
    ('עד הצהריים הגדר הייתה צבועה, ולטום היו עשרה דברים חדשים.', 'By midday the fence was painted, and Tom had ten new things.'))]),

 ('The New Girl', 'הילדה החדשה', [
  P(('בדרך הביתה טום עבר ליד בית עם גינה קטנה.', 'On the way home Tom passed a house with a small garden.'),
    ('בחלון הוא ראה ילדה חדשה עם שיער בהיר.', 'In the window he saw a new girl with fair hair.')),
  P(('הוא עמד שם ולא זז, ואז התחיל לעשות שטויות.', 'He stood there and did not move, and then began doing silly things.'),
    ('הוא קפץ, עמד על הידיים ושר בקול גדול.', 'He jumped, stood on his hands and sang loudly.')),
  P(('הילדה הסתכלה עליו רגע, ואז זרקה לו פרח.', 'The girl looked at him a moment, and then threw him a flower.'),
    ('טום לקח את הפרח ושם אותו קרוב ללב.', 'Tom took the flower and put it close to his heart.'),
    ('כל הלילה הוא חשב עליה ולא הצליח להירדם.', 'All night he thought about her and could not fall asleep.'))]),

 ('Sunday School', 'בית הספר של יום ראשון', [
  P(('ביום ראשון כל הילדים הלכו ללמוד פסוקים בעל פה.', 'On Sunday all the children went to learn verses by heart.'),
    ('מי שידע הרבה פסוקים קיבל כרטיס, ועל הכרטיסים נתנו ספר.', 'Whoever knew many verses got a ticket, and for the tickets they gave a book.')),
  P(('טום לא ידע כמעט כלום, אבל היו לו דברים לסחור בהם.', 'Tom knew almost nothing, but he had things to trade with.'),
    ('הוא החליף חבל, מברשת וכדור על כרטיסים של ילדים אחרים.', 'He traded a rope, a brush and a ball for other children’s tickets.')),
  P(('באמצע השיעור בא אורח חשוב עם הבת שלו.', 'In the middle of the lesson an important guest came with his daughter.'),
    ('הבת הייתה הילדה מהחלון, וקראו לה בקי.', 'The daughter was the girl from the window, and her name was Becky.')),
  P(('טום הרים את היד ואמר שיש לו מספיק כרטיסים לספר.', 'Tom raised his hand and said he had enough tickets for a book.'),
    ('נתנו לו את הספר לפני כולם, וזה היה רגע גדול.', 'They gave him the book in front of everyone, and it was a great moment.'),
    ('ואז שאלו אותו שאלה אחת קלה, והוא לא ידע לענות.', 'And then they asked him one easy question, and he could not answer.'))]),

 ('The Beetle and the Dog', 'החיפושית והכלב', [
  P(('בבית הכנסת של העיירה היה חם, וכולם ישבו בשקט.', 'In the town’s meeting house it was hot, and everyone sat quietly.'),
    ('טום הוציא מהכיס קופסה קטנה עם חיפושית שחורה.', 'Tom took a small box with a black beetle out of his pocket.')),
  P(('החיפושית ברחה לו, והיא נפלה על הרצפה בין הספסלים.', 'The beetle escaped him, and it fell on the floor between the benches.'),
    ('כלב אחד שהיה שם ראה אותה והתחיל לשחק איתה.', 'A dog that was there saw it and started to play with it.')),
  P(('החיפושית נשכה אותו, והכלב קפץ וצעק ורץ בין האנשים.', 'The beetle bit him, and the dog jumped and yelped and ran among the people.'),
    ('כולם צחקו, וגם המבוגרים לא הצליחו לעצור.', 'Everyone laughed, and even the grown-ups could not stop.'),
    ('טום היה מרוצה מאוד, כי סוף סוף היה מעניין.', 'Tom was very pleased, because at last it had been interesting.'))]),

 ('Huck Finn', 'האק', [
  P(('בעיירה חי ילד אחד שלא הלך לבית ספר בכלל.', 'In the town lived one boy who did not go to school at all.'),
    ('קראו לו האק, והוא ישן איפה שרצה.', 'His name was Huck, and he slept wherever he liked.')),
  P(('כל ההורים אמרו לילדים שלהם לא לדבר איתו.', 'All the parents told their children not to talk to him.'),
    ('ולכן כל הילדים רצו לדבר איתו כל הזמן.', 'And therefore all the children wanted to talk to him all the time.')),
  P(('טום פגש אותו בדרך, ולהאק הייתה חתולה מתה ביד.', 'Tom met him on the road, and Huck had a dead cat in his hand.'),
    ('האק אמר: עם חתולה כזאת מרפאים יבלות בבית הקברות.', 'Huck said: with a cat like this you cure warts in the graveyard.'),
    ('הם סיכמו להיפגש בחצות ליד הקבר החדש.', 'They agreed to meet at midnight beside the new grave.'))]),

 ('Tom and Becky', 'טום ובקי', [
  P(('בבית הספר טום ישב ליד בקי ודיבר איתה בשקט.', 'At school Tom sat beside Becky and talked to her quietly.'),
    ('הוא צייר לה בית על הלוח הקטן שלו.', 'He drew her a house on his little slate.')),
  P(('הוא אמר לה: את אוהבת אותי? ואני אוהב אותך.', 'He said to her: do you love me? And I love you.'),
    ('בקי אמרה כן, ושניהם היו מאושרים חצי שעה.', 'Becky said yes, and they were both happy for half an hour.')),
  P(('ואז טום סיפר לה שהוא אמר את זה גם לילדה אחרת.', 'And then Tom told her that he had said it to another girl too.'),
    ('בקי בכתה, וטום לא הבין מה עשה לא בסדר.', 'Becky cried, and Tom did not understand what he had done wrong.'))]),

 ('At Midnight in the Graveyard', 'בחצות בבית הקברות', [
  P(('בחצות טום והאק נכנסו לבית הקברות עם החתולה.', 'At midnight Tom and Huck went into the graveyard with the cat.'),
    ('היה חושך, והרוח הזיזה את העצים מעל הקברים.', 'It was dark, and the wind moved the trees above the graves.')),
  P(('פתאום הם ראו שלושה אנשים באים עם פנס.', 'Suddenly they saw three men coming with a lantern.'),
    ('הילדים התחבאו מאחורי עץ ולא נשמו.', 'The boys hid behind a tree and did not breathe.')),
  P(('האנשים חפרו קבר, ואז התחילו לריב על כסף.', 'The men dug up a grave, and then began to quarrel about money.'),
    ('אחד מהם, ג\'ו, לקח סכין והרג את הרופא הצעיר.', 'One of them, Joe, took a knife and killed the young doctor.'),
    ('אחר כך הוא שם את הסכין ביד של פוטר, שהיה שתוי וישן.', 'Afterwards he put the knife in the hand of Potter, who was drunk and asleep.'))]),

 ('The Oath', 'השבועה', [
  P(('הילדים ברחו משם ורצו עד שלא יכלו יותר.', 'The boys fled from there and ran until they could run no more.'),
    ('הם נכנסו לרפת ישנה, ישבו על האדמה ורעדו.', 'They went into an old barn, sat on the ground and shook.')),
  P(('האק אמר: אם נספר, ג\'ו יהרוג גם אותנו.', 'Huck said: if we tell, Joe will kill us too.'),
    ('טום כתב על חתיכת עץ שהם לא יספרו לאף אחד.', 'Tom wrote on a piece of wood that they would tell nobody.')),
  P(('הם חתמו בדם מהאצבע ושמו את העץ באדמה.', 'They signed in blood from a finger and put the wood in the ground.'),
    ('אחר כך הם הלכו הביתה, וכל אחד שכב בלי לישון.', 'Afterwards they went home, and each lay without sleeping.'))]),

 ('Potter in Prison', 'פוטר בכלא', [
  P(('בבוקר כל העיירה דיברה על מה שקרה בלילה.', 'In the morning the whole town was talking about what had happened in the night.'),
    ('לקחו את פוטר לכלא, כי הסכין הייתה שלו.', 'They took Potter to prison, because the knife was his.')),
  P(('פוטר אמר שהוא לא זוכר כלום, ואף אחד לא האמין לו.', 'Potter said he remembered nothing, and nobody believed him.'),
    ('ג\'ו עמד בין האנשים וסיפר בשקט מה ראה.', 'Joe stood among the people and quietly told what he had seen.')),
  P(('טום הסתכל עליו ופחד שהוא יראה את העיניים שלו.', 'Tom looked at him and was afraid he would see his eyes.'),
    ('בערב הילדים הביאו לפוטר לחם ותפוזים דרך החלון הקטן.', 'In the evening the boys brought Potter bread and oranges through the small window.'),
    ('פוטר הודה להם, וזה היה קשה יותר מהכול.', 'Potter thanked them, and that was harder than anything.'))]),

 ('Becky Turns Away', 'בקי מסתובבת', [
  P(('בבית הספר בקי לא הסתכלה על טום בכלל.', 'At school Becky did not look at Tom at all.'),
    ('היא דיברה עם ילדים אחרים וצחקה בקול.', 'She talked with other children and laughed out loud.')),
  P(('טום עשה שטויות כדי שהיא תשים לב, ולא עזר.', 'Tom did silly things so that she would notice, and it did not help.'),
    ('הוא ישב לבד בהפסקה והרגיש שכולם שכחו אותו.', 'He sat alone at break and felt that everyone had forgotten him.')),
  P(('בערב הוא אמר לעצמו: אני אלך מפה ואף אחד לא ידע.', 'In the evening he said to himself: I will go away from here and nobody will know.'),
    ('הוא חשב שכשיחזור, כולם יבינו כמה הם טעו.', 'He thought that when he came back, everyone would understand how wrong they had been.'))]),

 ('The Pirates Set Out', 'השודדים יוצאים לדרך', [
  P(('טום סיפר להאק ולג\'ו על התוכנית שלו.', 'Tom told Huck and Joe about his plan.'),
    ('הוא אמר: יש אי באמצע הנהר, ושם נהיה שודדי ים.', 'He said: there is an island in the middle of the river, and there we will be pirates.')),
  P(('בלילה הם לקחו לחם, בשר מלוח ומחבת ישנה.', 'At night they took bread, salt meat and an old pan.'),
    ('הם מצאו קרש גדול ושמו עליו את הדברים.', 'They found a big plank and put their things on it.')),
  P(('הם חתרו בחושך והגיעו לאי לפני הבוקר.', 'They paddled in the dark and reached the island before morning.'),
    ('הם הדליקו אש, אכלו, וצחקו כמו שלא צחקו מזמן.', 'They lit a fire, ate, and laughed as they had not laughed for a long time.'))]),

 ('Life on the Island', 'החיים על האי', [
  P(('בבוקר הם התרחצו בנהר ושכבו על החול החם.', 'In the morning they bathed in the river and lay on the hot sand.'),
    ('לא היה בית ספר, לא היו הורים ולא היו שעות.', 'There was no school, there were no parents and there were no hours.')),
  P(('הם דגו דגים ובישלו אותם על האש.', 'They caught fish and cooked them on the fire.'),
    ('טום אמר: זה הכי טוב שהיה לי בחיים.', 'Tom said: this is the best thing I have had in my life.')),
  P(('אבל בערב, כשהיה שקט, כל אחד חשב על הבית.', 'But in the evening, when it was quiet, each one thought about home.'),
    ('אף אחד לא אמר כלום, וכולם ידעו מה השני חושב.', 'Nobody said anything, and they all knew what the other was thinking.'))]),

 ('The Sound on the River', 'הקול על הנהר', [
  P(('ביום השני הם שמעו קול חזק מהנהר, כמו רובה.', 'On the second day they heard a loud sound from the river, like a gun.'),
    ('הם עלו על סלע גבוה וראו סירה גדולה עם הרבה אנשים.', 'They climbed a high rock and saw a big boat with many people.')),
  P(('טום הבין מיד: ככה מחפשים מישהו שטבע.', 'Tom understood at once: that is how they look for someone who has drowned.'),
    ('הוא אמר: הם מחפשים אותנו, כולם חושבים שאנחנו מתים.', 'He said: they are looking for us, everyone thinks we are dead.')),
  P(('בהתחלה הם היו גאים מאוד, וצחקו ורקדו על החול.', 'At first they were very proud, and laughed and danced on the sand.'),
    ('אחר כך ג\'ו אמר בשקט: אמא שלי בטח בוכה עכשיו.', 'Afterwards Joe said quietly: my mother is surely crying now.'))]),

 ('Tom Goes Home in the Dark', 'טום חוזר בלילה', [
  P(('בלילה טום חיכה שכולם יישנו ואז ירד למים.', 'At night Tom waited for everyone to sleep and then went down to the water.'),
    ('הוא שחה את כל הנהר וחזר לעיירה רטוב.', 'He swam the whole river and came back to the town wet.')),
  P(('הוא נכנס לבית של דודה פולי דרך החלון.', 'He went into Aunt Polly’s house through the window.'),
    ('הוא התחבא מתחת למיטה ושמע אותה מדברת.', 'He hid under the bed and heard her talking.')),
  P(('היא בכתה ואמרה: הוא לא היה ילד רע, רק ילד.', 'She wept and said: he was not a bad boy, only a boy.'),
    ('טום רצה לצאת ולומר שהוא חי, אבל לא יצא.', 'Tom wanted to come out and say he was alive, but he did not.'),
    ('הוא נישק אותה כשהיא ישנה וחזר לאי לפני הבוקר.', 'He kissed her while she slept and went back to the island before morning.'))]),

 ('The Storm', 'הסופה', [
  P(('בלילה השלישי באה סופה חזקה על האי.', 'On the third night a strong storm came over the island.'),
    ('הרוח שברה ענפים, והמים נכנסו לכל מקום.', 'The wind broke branches, and the water came in everywhere.')),
  P(('הילדים ברחו מתחת לעץ גדול והחזיקו אחד את השני.', 'The boys ran under a big tree and held on to one another.'),
    ('הברק האיר את הנהר, והכול נראה לבן לרגע.', 'The lightning lit the river, and everything looked white for a moment.')),
  P(('בבוקר הכול היה רטוב, אבל השמש חזרה.', 'In the morning everything was wet, but the sun came back.'),
    ('טום אמר: אנחנו חוזרים, אבל לא סתם ככה.', 'Tom said: we are going back, but not just like that.'))]),

 ('Their Own Funeral', 'הלוויה שלהם', [
  P(('ביום ראשון כל העיירה באה להיפרד משלושת הילדים.', 'On Sunday the whole town came to say goodbye to the three boys.'),
    ('כולם בכו וסיפרו כמה הם היו ילדים טובים.', 'Everyone wept and told how good those boys had been.')),
  P(('דודה פולי ישבה מקדימה ולא הרימה את הראש.', 'Aunt Polly sat at the front and did not raise her head.'),
    ('פתאום הדלת נפתחה, ושלושת הילדים נכנסו פנימה.', 'Suddenly the door opened, and the three boys came in.')),
  P(('היה שקט של רגע, ואז כולם קמו וצעקו.', 'There was a moment of silence, and then everyone stood and shouted.'),
    ('דודה פולי חיבקה את טום חזק וגם הכתה אותו קצת.', 'Aunt Polly hugged Tom hard and also hit him a little.'),
    ('טום היה מאושר, וזה היה הרגע הכי גדול שלו.', 'Tom was overjoyed, and it was his greatest moment.'))]),

 ('The Torn Book', 'הספר הקרוע', [
  P(('בבית הספר למורה היה ספר סודי בתוך המגירה.', 'At school the teacher had a secret book inside the drawer.'),
    ('בקי פתחה את המגירה כשהוא יצא, וקרעה דף אחד.', 'Becky opened the drawer when he went out, and tore one page.')),
  P(('היא נבהלה מאוד, כי ידעה מה יקרה לה.', 'She was very frightened, because she knew what would happen to her.'),
    ('טום ראה את זה ולא אמר כלום.', 'Tom saw it and said nothing.')),
  P(('המורה שאל מי קרע, וכולם שתקו.', 'The teacher asked who had torn it, and everyone was silent.'),
    ('כשהוא הגיע לבקי, טום קם ואמר: אני עשיתי את זה.', 'When he got to Becky, Tom stood up and said: I did it.'),
    ('הוא קיבל מכות, ובקי הסתכלה עליו כמו שלא הסתכלה מעולם.', 'He was beaten, and Becky looked at him as she had never looked before.'))]),

 ('Examination Day', 'יום המבחן', [
  P(('בסוף השנה היה ערב גדול עם ההורים בבית הספר.', 'At the end of the year there was a big evening with the parents at the school.'),
    ('הילדים קראו שירים בעל פה, ואחד שכח באמצע.', 'The children recited poems by heart, and one forgot in the middle.')),
  P(('הבנות קראו חיבורים ארוכים על החיים ועל הזמן.', 'The girls read long compositions about life and about time.'),
    ('טום עלה ושכח את המילים אחרי שתי שורות.', 'Tom went up and forgot the words after two lines.')),
  P(('בסוף הערב הילדים עשו תרגיל אחד למורה מלמעלה.', 'At the end of the evening the children played one trick on the teacher from above.'),
    ('כולם צחקו, והמורה לא ידע מי עשה את זה.', 'Everyone laughed, and the teacher did not know who had done it.'),
    ('אחרי זה התחילה החופשה הגדולה.', 'After that the long holiday began.'))]),

 ('The Trial', 'המשפט', [
  P(('בקיץ התחיל המשפט של פוטר בבית המשפט הקטן.', 'In the summer Potter’s trial began in the small courthouse.'),
    ('כל העיירה באה, וכולם היו בטוחים שהוא אשם.', 'The whole town came, and everyone was sure he was guilty.')),
  P(('טום לא ישן שלושה לילות וידע שהוא חייב לדבר.', 'Tom did not sleep for three nights and knew that he had to speak.'),
    ('ביום השני הוא הרים את היד וביקש לומר משהו.', 'On the second day he raised his hand and asked to say something.')),
  P(('הוא סיפר הכול: את בית הקברות, את הסכין ואת ג\'ו.', 'He told everything: the graveyard, the knife and Joe.'),
    ('כל האנשים הסתובבו להסתכל, וג\'ו קפץ מהחלון וברח.', 'All the people turned to look, and Joe jumped out of the window and fled.'),
    ('פוטר יצא חופשי, וטום נהיה גיבור העיירה.', 'Potter went free, and Tom became the town’s hero.'))]),

 ('After the Trial', 'אחרי המשפט', [
  P(('ביום טום היה מאושר, ובלילה הוא פחד.', 'By day Tom was happy, and at night he was afraid.'),
    ('הוא ידע שג\'ו נמצא איפשהו ושהוא זוכר הכול.', 'He knew that Joe was somewhere and that he remembered everything.')),
  P(('הוא סגר את החלון בלילה, וזה לא עזר.', 'He shut the window at night, and it did not help.'),
    ('האק אמר לו: אני שומע מישהו הולך בכל מקום.', 'Huck said to him: I hear someone walking everywhere.')),
  P(('הם החליטו לחפש משהו אחר, כדי לא לחשוב על זה.', 'They decided to look for something else, so as not to think about it.'),
    ('טום אמר: בואו נחפש מטמון, כמו בסיפורים.', 'Tom said: let us look for treasure, like in the stories.'))]),

 ('The Haunted House', 'הבית הריק', [
  P(('הם הלכו לבית ישן וריק בקצה העיירה.', 'They went to an old, empty house at the edge of the town.'),
    ('החלונות היו שבורים, והדלת נשארה פתוחה שנים.', 'The windows were broken, and the door had stood open for years.')),
  P(('הם עלו למעלה כדי לחפש כלים ישנים.', 'They went upstairs in order to look for old tools.'),
    ('פתאום שמעו קולות למטה, ושכבו על הרצפה.', 'Suddenly they heard voices below, and lay down on the floor.')),
  P(('דרך חור ברצפה הם ראו שני אנשים עם שקית.', 'Through a hole in the floor they saw two men with a bag.'),
    ('אחד מהם היה ג\'ו, והם הכירו את הקול שלו מיד.', 'One of them was Joe, and they knew his voice at once.'),
    ('שני הילדים לא זזו ולא נשמו במשך שעה שלמה.', 'The two boys did not move and did not breathe for a whole hour.'))]),

 ('The Box of Gold', 'ארגז הזהב', [
  P(('האנשים למטה חפרו באדמה כדי להחביא את השקית.', 'The men below dug in the ground in order to hide the bag.'),
    ('המעדר פגע במשהו קשה, והם הוציאו ארגז ישן.', 'The hoe struck something hard, and they pulled out an old box.')),
  P(('בארגז היה זהב, יותר ממה שהם חשבו.', 'In the box was gold, more than they had thought.'),
    ('ג\'ו אמר: לא נשאיר את זה פה, ניקח למקום שלנו.', 'Joe said: we will not leave this here, we will take it to our place.')),
  P(('הוא אמר: המקום השני, מתחת למספר שתיים.', 'He said: the other place, under number two.'),
    ('הילדים שמעו כל מילה ולא הבינו מה זה אומר.', 'The boys heard every word and did not understand what it meant.'))]),

 ('Number Two', 'מספר שתיים', [
  P(('בעיירה היה פונדק אחד עם חדרים למעלה.', 'In the town there was one inn with rooms upstairs.'),
    ('טום חשב: אולי מספר שתיים זה חדר בפונדק.', 'Tom thought: perhaps number two is a room in the inn.')),
  P(('הם באו בערב ובדקו את הדלתות אחת אחת.', 'They came in the evening and checked the doors one by one.'),
    ('דלת אחת הייתה סגורה תמיד, וזאת הייתה מספר שתיים.', 'One door was always shut, and that was number two.')),
  P(('האק אמר: אני אשמור פה כל לילה עד שהוא יצא.', 'Huck said: I will watch here every night until he comes out.'),
    ('טום הסכים, כי הוא היה צריך ללכת לטיול עם הכיתה.', 'Tom agreed, because he had to go on an outing with his class.'))]),

 ('Huck Saves the Widow', 'האק מציל את האלמנה', [
  P(('בלילה האק ראה שני אנשים יוצאים מהחדר עם שקית.', 'At night Huck saw two men come out of the room with a bag.'),
    ('הוא הלך אחרי שניהם בשקט בין הבתים והגנים.', 'He followed the two of them quietly among the houses and gardens.')),
  P(('הם עלו לגבעה ועצרו ליד הבית של אישה זקנה.', 'They went up the hill and stopped by an old woman’s house.'),
    ('האק שמע את ג\'ו אומר שהוא בא לעשות לה רע.', 'Huck heard Joe say that he had come to do her harm.')),
  P(('האק רץ למטה וקרא לשכנים, וכולם עלו עם נשק.', 'Huck ran down and called the neighbours, and they all came up with guns.'),
    ('האנשים ברחו לתוך היער, והאישה ניצלה.', 'The men fled into the forest, and the woman was saved.'),
    ('האק ביקש שלא יגידו שזה הוא, כי פחד מג\'ו.', 'Huck asked them not to say it was him, because he was afraid of Joe.'))]),

 ('The Picnic', 'הטיול', [
  P(('כל ילדי הכיתה נסעו בסירה לחוף רחוק על הנהר.', 'All the children of the class went by boat to a far shore on the river.'),
    ('הם אכלו, שיחקו ורצו כל היום בין העצים.', 'They ate, played and ran all day among the trees.')),
  P(('אחר הצהריים הם נכנסו למערה גדולה עם נרות.', 'In the afternoon they went into a big cave with candles.'),
    ('היו שם מסדרונות ארוכים, ואחד נכנס לתוך השני.', 'There were long passages there, and one led into another.')),
  P(('טום ובקי הלכו רחוק מכולם וראו חדר גדול ויפה.', 'Tom and Becky went far from everyone and saw a big, beautiful room.'),
    ('כשרצו לחזור, הם כבר לא ידעו מאיפה באו.', 'When they wanted to go back, they no longer knew where they had come from.'),
    ('הם קראו לאחרים, ואף אחד לא ענה.', 'They called to the others, and nobody answered.'))]),

 ('Lost in the Cave', 'אבודים במערה', [
  P(('הנר הראשון נגמר, ואחר כך גם השני.', 'The first candle finished, and afterwards the second too.'),
    ('בקי בכתה, וטום אמר לה שהכול יהיה בסדר.', 'Becky cried, and Tom told her everything would be all right.')),
  P(('הם הלכו לאט וסימנו את הדרך על הקירות.', 'They walked slowly and marked the way on the walls.'),
    ('הם מצאו מים על סלע ושתו מהם.', 'They found water on a rock and drank from it.')),
  P(('בקי כבר לא יכלה ללכת, וטום השאיר אותה יושבת.', 'Becky could no longer walk, and Tom left her sitting.'),
    ('הוא לקח חוט ארוך והלך לבד לחפש דרך.', 'He took a long string and went alone to look for a way.'))]),

 ('A Face in the Dark', 'פנים בחושך', [
  P(('במסדרון אחד טום ראה אור קטן רחוק.', 'In one passage Tom saw a small light far away.'),
    ('הוא התקרב בשקט, כי חשב שאלה אנשים שמחפשים אותם.', 'He came closer quietly, because he thought these were people looking for them.')),
  P(('הוא ראה יד עם נר, ואז ראה את הפנים.', 'He saw a hand with a candle, and then he saw the face.'),
    ('זה היה ג\'ו, שהתחבא במערה מאז אותו לילה.', 'It was Joe, who had been hiding in the cave since that night.')),
  P(('טום לא זז ולא נשם עד שהאור נעלם.', 'Tom did not move and did not breathe until the light disappeared.'),
    ('הוא חזר לבקי ולא סיפר לה כלום.', 'He went back to Becky and told her nothing.'),
    ('הוא אמר רק: מצאתי דרך, בואי נלך לאט.', 'He only said: I have found a way, let us go slowly.'))]),

 ('Out of the Hill', 'יוצאים מההר', [
  P(('טום ניסה מסדרון שלישי ומצא אור קטן בקצה.', 'Tom tried a third passage and found a small light at the end.'),
    ('הוא הרחיב את החור בידיים וראה את הנהר.', 'He widened the hole with his hands and saw the river.')),
  P(('הם יצאו מההר רחוק מאוד מהכניסה למערה.', 'They came out of the hill very far from the entrance to the cave.'),
    ('אנשים בסירה ראו אותם ולקחו אותם הביתה.', 'People in a boat saw them and took them home.')),
  P(('בעיירה כולם שמחו, כי חיפשו אותם שלושה ימים.', 'In the town everyone rejoiced, because they had been searching three days.'),
    ('אבא של בקי סגר את המערה בדלת ברזל.', 'Becky’s father closed the cave with an iron door.'))]),

 ('The Treasure', 'המטמון', [
  P(('אחרי שבועיים טום סיפר לאבא של בקי מה שראה במערה.', 'Two weeks later Tom told Becky’s father what he had seen in the cave.'),
    ('הם פתחו את הדלת ומצאו את ג\'ו מת ליד הכניסה.', 'They opened the door and found Joe dead by the entrance.')),
  P(('טום והאק חזרו למערה עם חבל ועם נרות.', 'Tom and Huck went back into the cave with rope and candles.'),
    ('הם מצאו את הארגז מתחת לסלע, בדיוק כמו שחשבו.', 'They found the box under a rock, exactly as they had thought.')),
  P(('הם הביאו את הזהב לעיירה בשקית ישנה.', 'They brought the gold to the town in an old bag.'),
    ('כשספרו את הכסף, זה היה יותר ממה שאנשים רואים בחיים.', 'When they counted the money, it was more than people see in a lifetime.')),
  P(('האלמנה לקחה את האק לגור אצלה בבית נקי.', 'The widow took Huck to live with her in a clean house.'),
    ('הוא לבש בגדים חדשים ואכל בשעות קבועות.', 'He wore new clothes and ate at set hours.'),
    ('אחרי שלושה שבועות הוא ברח וישן שוב בחבית.', 'After three weeks he ran away and slept in a barrel again.')),
  P(('טום מצא אותו ואמר: תחזור, אחרת לא תוכל להיות בחבורה שלנו.', 'Tom found him and said: come back, or you cannot be in our band.'),
    ('האק חשב רגע ואמר: בסדר, בשביל זה אני אנסה.', 'Huck thought a moment and said: all right, for that I will try.'),
    ('וכך נגמר הקיץ הזה, והתחיל קיץ אחר.', 'And so that summer ended, and another summer began.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('tomsawyer', {'en': 'The Adventures of Tom Sawyer',
                                        'he': 'הרפתקאות טום סוייר'}, 'intermediate',
                          CHAPTERS, unit='Chapter', unit_he='פרק', shelf=14, meta=META))
