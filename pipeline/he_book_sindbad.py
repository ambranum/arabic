#!/usr/bin/env python3
"""שבעת מסעות סינדבאד — the seven voyages, retold in modern Hebrew, graded to intermediate.

The Hebrew twin of pipeline/book_sindbad.py. Sindbad comes out of the Thousand and One Nights —
medieval, anonymous, public domain by age — and these are retellings from the traditional plots
rather than a translation of any edition.

WHY IT SITS HERE. Seven voyages is seven times the same sentence pattern with different nouns
in it: he sailed, the ship broke, he found, he came home rich. A learner who has read the first
voyage can read the third almost without help, and that experience — reading Hebrew fast enough
to forget you are reading — is what the intermediate tier is for. It is also the one book on
this shelf whose story is native to the region on both sides of the Green Line.

Deliberately unpointed; the vowels are looked up at ingest.

Run:  python3 pipeline/he_book_sindbad.py --lang he            # check
      python3 pipeline/he_book_sindbad.py --lang he --write    # emit
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from he_bookshelf import P, book                       # noqa: E402

META = {'work': 'The Seven Voyages of Sindbad, from the Thousand and One Nights',
        'author': 'traditional', 'year': 'medieval',
        'status': 'public domain — medieval, anonymous'}

CHAPTERS = [
 ('The Porter and the Sailor', 'הסבל והמלח', [
  P(('בבגדד חי איש עני שנשא משאות כבדים על הגב בשביל כמה מטבעות.', 'In Baghdad lived a poor man who carried heavy loads on his back for a few coins.'),
    ('יום אחד הוא עצר לנוח ליד בית גדול ויפה מאוד.', 'One day he stopped to rest beside a big and very beautiful house.'),
    ('מהחלון יצאו קולות של מוזיקה, צחוק וריח של אוכל טוב.', 'From the window came sounds of music, laughter and the smell of good food.')),
  P(('האיש אמר בקול: יש אנשים שיושבים ואוכלים, ויש אנשים שנושאים על הגב.', 'The man said aloud: some people sit and eat, and some people carry on their backs.'),
    ('בעל הבית שמע אותו וקרא לו להיכנס.', 'The owner of the house heard him and called him to come in.'),
    ('הוא אמר: קוראים לי סינדבאד, וגם אני נשאתי על הגב לפני שנים.', 'He said: my name is Sindbad, and I too carried things on my back years ago.')),
  P(('סינדבאד אמר: שב, תאכל, ואני אספר לך איך קיבלתי את הכסף הזה.', 'Sindbad said: sit, eat, and I will tell you how I got this money.'),
    ('ואז הוא התחיל לספר על שבעה מסעות בים.', 'And then he began to tell of seven voyages at sea.'))]),

 ('The First Ship', 'הספינה הראשונה', [
  P(('סינדבאד סיפר: אבא שלי מת והשאיר לי הרבה כסף.', 'Sindbad told: my father died and left me a lot of money.'),
    ('הייתי צעיר וטיפש, ובזבזתי את הכול על חברים ועל אוכל.', 'I was young and foolish, and I spent it all on friends and on food.')),
  P(('יום אחד ראיתי שנשאר לי מעט מאוד, ופחדתי מאוד.', 'One day I saw that very little was left, and I was very frightened.'),
    ('מכרתי את מה שהיה לי, קניתי סחורה ועליתי על ספינה בנמל.', 'I sold what I had, bought goods and boarded a ship at the port.')),
  P(('הים היה שקט, והספינה עברה מאי לאי.', 'The sea was calm, and the ship went from island to island.'),
    ('בכל מקום מכרנו וקנינו, והכסף שלי גדל לאט לאט.', 'At every place we sold and bought, and my money grew little by little.'),
    ('חשבתי שהחיים בים קלים ויפים, אבל טעיתי.', 'I thought that life at sea was easy and lovely, but I was wrong.'))]),

 ('The Island That Moved', 'האי שזז', [
  P(('יום אחד ראינו אי קטן וירוק באמצע הים.', 'One day we saw a small green island in the middle of the sea.'),
    ('ירדנו מהספינה, הדלקנו אש ובישלנו אוכל על האדמה.', 'We got off the ship, lit a fire and cooked food on the ground.'),
    ('צחקנו ושרנו, כי היה טוב לעמוד על משהו שלא זז.', 'We laughed and sang, because it was good to stand on something that did not move.')),
  P(('ופתאום האדמה מתחתינו זזה בכוח.', 'And suddenly the ground beneath us moved violently.'),
    ('זה לא היה אי אלא דג ענק שישן על פני המים שנים.', 'It was not an island but a huge fish that had slept on the surface of the water for years.'),
    ('האש חיממה את הגב שלו, והוא ירד למים.', 'The fire warmed its back, and it went down into the water.')),
  P(('כולם צעקו ורצו לספינה, אבל אני נשארתי מאחור.', 'Everyone shouted and ran for the ship, but I stayed behind.'),
    ('תפסתי חתיכת עץ והמים לקחו אותי רחוק.', 'I grabbed a piece of wood and the water carried me far away.'),
    ('הספינה נסעה בלעדיי, כי חשבו שאני כבר מת.', 'The ship sailed without me, because they thought I was already dead.'))]),

 ('The King of the Sea Horses', 'המלך וסוסי הים', [
  P(('המים הביאו אותי לאי אחר, ושכבתי על החול יום שלם.', 'The water brought me to another island, and I lay on the sand for a whole day.'),
    ('כשקמתי מצאתי עצים עם פירות ומים מתוקים.', 'When I got up I found trees with fruit and sweet water.')),
  P(('הלכתי ומצאתי אנשים ששמרו על סוסים ליד הים.', 'I walked and found men who were watching horses by the sea.'),
    ('הם סיפרו לי שהם עובדים אצל מלך האי.', 'They told me that they worked for the king of the island.'),
    ('הם לקחו אותי אליו, והמלך קיבל אותי יפה.', 'They took me to him, and the king received me kindly.')),
  P(('חייתי שם זמן, ובכל יום עמדתי בנמל וחיכיתי לספינה.', 'I lived there for a time, and every day I stood in the port and waited for a ship.'),
    ('יום אחד באה ספינה, ובתוכה הייתה הסחורה שלי מהמסע הראשון.', 'One day a ship came, and in it was my own cargo from the first voyage.'),
    ('בעל הספינה הכיר אותי, החזיר לי הכול, ונסעתי הביתה עשיר.', 'The ship’s owner recognised me, gave everything back, and I went home rich.'))]),

 ('Bored at Home', 'משעמם בבית', [
  P(('בבגדד ישבתי בבית יפה ואכלתי טוב, ולא היה לי חסר כלום.', 'In Baghdad I sat in a fine house and ate well, and I lacked nothing.'),
    ('אבל אחרי כמה חודשים התחיל להיות לי משעמם.', 'But after a few months I began to be bored.')),
  P(('חשבתי כל היום על הים, על האיים ועל הדברים שראיתי.', 'I thought all day about the sea, about the islands and about the things I had seen.'),
    ('אמרתי לעצמי: אדם צריך לראות עוד, ולא לשבת ולחכות.', 'I said to myself: a person must see more, and not sit and wait.')),
  P(('קניתי סחורה חדשה ועליתי שוב על ספינה.', 'I bought new goods and boarded a ship again.'),
    ('החברים שלי אמרו שאני משוגע, ואולי הם צדקו.', 'My friends said I was mad, and perhaps they were right.'),
    ('אבל הים קרא לי, ולא יכולתי להישאר.', 'But the sea called me, and I could not stay.'),
    ('יצאנו מהנמל בבוקר יפה ושקט.', 'We set out from the port on a fine, quiet morning.'))]),

 ('The Great White Dome', 'הכיפה הלבנה', [
  P(('הפעם הספינה עצרה באי ירוק ומלא עצים.', 'This time the ship stopped at a green island full of trees.'),
    ('ירדתי לטייל, שכבתי מתחת לעץ ונרדמתי.', 'I got off to walk about, lay down under a tree and fell asleep.'),
    ('כשהתעוררתי הספינה כבר לא הייתה שם.', 'When I woke the ship was no longer there.')),
  P(('הלכתי באי ומצאתי דבר לבן וגדול מאוד, בלי דלת ובלי חלון.', 'I walked about the island and found a big white thing, with no door and no window.'),
    ('חשבתי שזה בית, אבל זו הייתה ביצה של ציפור ענקית.', 'I thought it was a house, but it was the egg of a huge bird.')),
  P(('בערב השמיים החשיכו, כי הציפור באה ועמדה על הביצה.', 'In the evening the sky went dark, because the bird came and stood on the egg.'),
    ('קשרתי את עצמי לרגל שלה בבד מהבגד שלי.', 'I tied myself to its leg with cloth from my clothes.'),
    ('בבוקר הציפור עפה, ואני עפתי איתה.', 'In the morning the bird flew, and I flew with it.'))]),

 ('The Valley of Diamonds', 'עמק היהלומים', [
  P(('הציפור ירדה בעמק עמוק בין הרים גבוהים.', 'The bird came down in a deep valley between high mountains.'),
    ('התרתי את עצמי מהרגל שלה, והיא עפה משם.', 'I untied myself from its leg, and it flew away.')),
  P(('הסתכלתי על האדמה וראיתי אבנים יפות שמאירות באור.', 'I looked at the ground and saw beautiful stones that shone in the light.'),
    ('כל העמק היה מלא יהלומים, יותר מכל אוצר בעולם.', 'The whole valley was full of diamonds, more than any treasure in the world.'),
    ('אבל בין האבנים היו נחשים גדולים ומסוכנים.', 'But among the stones were big, dangerous snakes.')),
  P(('הבנתי שאני עשיר ובאותו רגע גם קרוב למוות.', 'I understood that I was rich and at the same moment close to death.'),
    ('ההרים היו גבוהים מדי, ולא הייתה שום דרך למעלה.', 'The mountains were too high, and there was no way up.'),
    ('ישבתי במערה קטנה וחיכיתי לבוקר.', 'I sat in a small cave and waited for morning.'))]),

 ('The Meat and the Eagles', 'הבשר והנשרים', [
  P(('בבוקר נפלו לעמק חתיכות בשר גדולות מלמעלה.', 'In the morning big pieces of meat fell into the valley from above.'),
    ('הבנתי מיד: אנשים על ההר זורקים בשר כדי לקחת את האבנים.', 'I understood at once: people on the mountain throw meat in order to get the stones.')),
  P(('האבנים נשארות על הבשר, ואז נשרים גדולים לוקחים אותו למעלה.', 'The stones stay on the meat, and then big eagles carry it up.'),
    ('מילאתי את הכיסים שלי באבנים וקשרתי את עצמי לחתיכת בשר.', 'I filled my pockets with stones and tied myself to a piece of meat.')),
  P(('נשר גדול בא, לקח את הבשר ואותי איתו, ועלה אל ההר.', 'A big eagle came, took the meat and me with it, and rose to the mountain.'),
    ('האנשים למעלה צעקו כשראו אדם במקום אבנים.', 'The people above shouted when they saw a man instead of stones.'),
    ('סיפרתי להם הכול, נתתי להם חלק מהאבנים, והם עזרו לי לחזור.', 'I told them everything, gave them some of the stones, and they helped me get back.'))]),

 ('The Hairy People', 'האנשים הקטנים', [
  P(('במסע השלישי הרוח הביאה אותנו לאי שלא הכרנו.', 'On the third voyage the wind brought us to an island we did not know.'),
    ('מהיער יצאו אנשים קטנים ורבים מאוד, כמו נמלים.', 'From the forest came little people, very many, like ants.')),
  P(('הם עלו על הספינה, לקחו הכול והורידו אותנו לחוף.', 'They climbed onto the ship, took everything and put us off on the shore.'),
    ('הספינה נסעה איתם, ואנחנו נשארנו על האי בלי כלום.', 'The ship sailed away with them, and we were left on the island with nothing.')),
  P(('הלכנו ביער ומצאנו בית גדול מאוד עם דלת פתוחה.', 'We walked in the forest and found a very big house with an open door.'),
    ('נכנסנו, וראינו עצמות על הרצפה ואש גדולה בפינה.', 'We went in, and saw bones on the floor and a big fire in the corner.'),
    ('הבנו מאוחר מדי שזה לא בית של אנשים.', 'We understood too late that this was not a house of people.'))]),

 ('The Giant', 'הענק', [
  P(('בערב נכנס לבית איש ענק, גבוה כמו עץ.', 'In the evening a giant man came into the house, tall as a tree.'),
    ('היו לו עיניים אדומות ושיניים כמו של חיה.', 'He had red eyes and teeth like an animal’s.')),
  P(('הוא הסתכל עלינו, בחר את החבר הכי גדול ואכל אותו.', 'He looked at us, chose the biggest of our friends and ate him.'),
    ('אחר כך שכב על הרצפה, והבית רעד מהנשימה שלו.', 'Afterwards he lay down on the floor, and the house shook from his breathing.')),
  P(('בכינו כל הלילה ולא ידענו מה לעשות.', 'We wept all night and did not know what to do.'),
    ('בבוקר הוא יצא, וסגר אחריו את הדלת הכבדה.', 'In the morning he went out, and shut the heavy door behind him.'),
    ('אמרתי לחברים: אם נחכה, כולנו נמות פה בזה אחר זה.', 'I said to my friends: if we wait, we will all die here one after another.'))]),

 ('The Iron in the Fire', 'הברזל באש', [
  P(('בערב השני הענק אכל עוד אחד מאיתנו ושוב נרדם.', 'On the second evening the giant ate another one of us and fell asleep again.'),
    ('חיכינו עד שהוא נשם עמוק, ואז קמנו בשקט.', 'We waited until he was breathing deeply, and then we got up quietly.')),
  P(('שמנו מוטות ברזל באש עד שהיו אדומים מחום.', 'We put iron bars in the fire until they were red with heat.'),
    ('אחר כך רצנו אליו כולנו יחד.', 'Afterwards we all ran at him together.'),
    ('הענק צעק צעקה נוראה, קם והתחיל לחפש אותנו בחושך.', 'The giant gave a terrible shout, rose and began looking for us in the dark.')),
  P(('ברחנו מהבית ורצנו לחוף מהר ככל שיכולנו.', 'We fled the house and ran to the shore as fast as we could.'),
    ('בנינו סירה קטנה מעצים ומחבלים ויצאנו לים.', 'We built a small boat from wood and ropes and put out to sea.'))]),

 ('The Serpent and the Board', 'הנחש והלוח', [
  P(('הים לקח אותנו לאי אחר, ושם חשבנו שאנחנו בטוחים.', 'The sea took us to another island, and there we thought we were safe.'),
    ('אבל בלילה בא נחש ענק ולקח אחד מהחברים שלי.', 'But at night a huge snake came and took one of my friends.')),
  P(('בלילה השני הוא לקח עוד אחד, ונשארתי לבד.', 'On the second night it took another, and I was left alone.'),
    ('לא ידעתי איפה להסתתר, כי הנחש עלה גם על העצים.', 'I did not know where to hide, because the snake climbed the trees too.')),
  P(('לקחתי לוחות עץ וקשרתי אותם מסביבי מכל הצדדים.', 'I took wooden boards and tied them around me on every side.'),
    ('שכבתי כמו בתוך קופסה, והנחש ניסה ולא הצליח.', 'I lay as if inside a box, and the snake tried and did not succeed.'),
    ('בבוקר ראיתי ספינה מרחוק וצעקתי בכל הכוח.', 'In the morning I saw a ship in the distance and shouted with all my strength.'))]),

 ('The Storm', 'הסופה', [
  P(('במסע הרביעי יצאנו עם רוח טובה ועם ספינה חזקה.', 'On the fourth voyage we set out with a good wind and a strong ship.'),
    ('אבל באמצע הים באה סופה שלא ראיתי כמוה.', 'But in the middle of the sea came a storm the like of which I had not seen.')),
  P(('הרוח שברה את המפרש, והגלים שברו את הספינה.', 'The wind broke the sail, and the waves broke the ship.'),
    ('אנשים נפלו למים, וכל אחד תפס מה שיכול.', 'People fell into the water, and each one grabbed what he could.'),
    ('החזקתי בלוח עץ יומיים בלי אוכל ובלי מים.', 'I held on to a wooden board for two days without food and without water.')),
  P(('בסוף הגעתי לחוף של אי חדש, ואנשים מצאו אותי שם.', 'In the end I reached the shore of a new island, and people found me there.'),
    ('הם נתנו לי מים ולקחו אותי לעיר שלהם.', 'They gave me water and took me to their city.'),
    ('חשבתי שניצלתי, אבל המסע הזה עוד לא נגמר.', 'I thought I was saved, but this voyage was not over yet.'))]),

 ('The King and the Saddle', 'המלך והאוכף', [
  P(('בעיר הזאת רכבו על סוסים בלי אוכף ובלי כלום.', 'In that city they rode horses with no saddle and nothing else.'),
    ('שאלתי את המלך למה, והוא אמר שהם לא מכירים דבר כזה.', 'I asked the king why, and he said that they did not know such a thing.')),
  P(('הלכתי לנגר, וביחד בנינו אוכף עץ.', 'I went to a carpenter, and together we built a wooden saddle.'),
    ('הוספתי עור רך ומקום לרגליים.', 'I added soft leather and a place for the feet.'),
    ('המלך רכב עליו וצחק מרוב שמחה.', 'The king rode on it and laughed for joy.')),
  P(('כל השרים רצו אוכף, ומכרתי הרבה וקיבלתי כסף רב.', 'All the ministers wanted a saddle, and I sold many and received a great deal of money.'),
    ('המלך אהב אותי מאוד ואמר שאני אחד מהאנשים שלו.', 'The king loved me greatly and said that I was one of his own people.'))]),

 ('The Law of the City', 'החוק של העיר', [
  P(('המלך רצה שאשאר לתמיד, ונתן לי אישה מהמשפחה שלו.', 'The king wanted me to stay for ever, and gave me a wife from his family.'),
    ('חייתי טוב, אבל תמיד חשבתי על בגדד.', 'I lived well, but I always thought about Baghdad.')),
  P(('יום אחד שכן שלי בכה, כי האישה שלו מתה.', 'One day a neighbour of mine wept, because his wife had died.'),
    ('שאלתי מה יקרה עכשיו, והוא אמר משפט נורא.', 'I asked what would happen now, and he said a terrible thing.'),
    ('הוא אמר: פה קוברים את הבעל יחד עם האישה.', 'He said: here they bury the husband together with the wife.')),
  P(('אחרי חודשים האישה שלי חלתה ומתה.', 'After some months my wife fell ill and died.'),
    ('לקחו אותי עם הגוף שלה למערה עמוקה בהר וסגרו אותה.', 'They took me with her body to a deep cave in the mountain and closed it.'))]),

 ('The Way Out', 'הדרך החוצה', [
  P(('במערה היה חושך, וריח כבד, ועצמות של אנשים.', 'In the cave there was darkness, a heavy smell, and the bones of people.'),
    ('נתנו לי מעט לחם ומים, ואחר כך שום דבר.', 'They gave me a little bread and water, and after that nothing.')),
  P(('ישבתי ימים ולא רציתי למות שם בשקט.', 'I sat for days and did not want to die there quietly.'),
    ('שמעתי קול קטן בחושך, וראיתי חיה שרצה בין האבנים.', 'I heard a small sound in the dark, and saw an animal running among the stones.'),
    ('הלכתי אחריה, כי חיה נכנסת ויוצאת מאיפה שהיא רוצה.', 'I followed it, because an animal goes in and out where it wishes.')),
  P(('החיה הובילה אותי לחור קטן, ומשם ראיתי אור וים.', 'The animal led me to a small hole, and from there I saw light and the sea.'),
    ('לקחתי מהמערה זהב ואבנים יקרות ויצאתי לחוף.', 'I took gold and precious stones from the cave and went out to the shore.'))]),

 ('The Broken Egg', 'הביצה השבורה', [
  P(('במסע החמישי הספינה עצרה באי ריק, ושם הייתה ביצה לבנה גדולה.', 'On the fifth voyage the ship stopped at an empty island, and there was a big white egg there.'),
    ('אמרתי לאנשים: אל תיגעו בה, אני יודע מה זה.', 'I said to the men: do not touch it, I know what this is.')),
  P(('הם צחקו עליי, שברו את הביצה ובישלו את מה שהיה בפנים.', 'They laughed at me, broke the egg and cooked what was inside.'),
    ('אכלו ושמחו, ואני עמדתי בצד ופחדתי.', 'They ate and rejoiced, and I stood aside and was afraid.')),
  P(('בערב השמיים החשיכו, והציפורים הגדולות חזרו.', 'In the evening the sky went dark, and the great birds came back.'),
    ('הן עפו מעל הספינה והפילו עליה אבנים ענקיות.', 'They flew over the ship and dropped huge stones on it.'),
    ('הספינה נשברה, וכולם טבעו חוץ ממני.', 'The ship broke apart, and everyone drowned except me.'))]),

 ('The Old Man of the Sea', 'הזקן על הגב', [
  P(('הגעתי לאי ומצאתי זקן יושב ליד נהר קטן.', 'I reached an island and found an old man sitting beside a small river.'),
    ('הוא ביקש בסימנים שאעביר אותו לצד השני.', 'He asked with signs that I carry him to the other side.')),
  P(('הרמתי אותו על הגב, והוא סגר את הרגליים על הצוואר שלי.', 'I lifted him onto my back, and he closed his legs round my neck.'),
    ('כשהגענו לצד השני הוא לא ירד.', 'When we reached the other side he did not get down.'),
    ('הוא נשאר עליי ימים ולילות, ולא יכולתי להוריד אותו.', 'He stayed on me for days and nights, and I could not get him off.')),
  P(('יום אחד עשיתי יין מפירות והשארתי אותו בשמש.', 'One day I made wine from fruit and left it in the sun.'),
    ('שתיתי קצת בשמחה, והזקן רצה גם הוא.', 'I drank a little happily, and the old man wanted some too.'))]),

 ('The Wine', 'היין', [
  P(('נתתי לו את היין, והוא שתה הרבה מאוד.', 'I gave him the wine, and he drank a great deal.'),
    ('הראש שלו הסתובב, והרגליים שלו נפתחו.', 'His head spun, and his legs opened.')),
  P(('הפלתי אותו על האדמה וברחתי משם מהר.', 'I threw him to the ground and fled from there quickly.'),
    ('רצתי לחוף ולא הסתכלתי אחורה אפילו פעם אחת.', 'I ran to the shore and did not look back even once.')),
  P(('בחוף פגשתי אנשים מספינה שעצרה למים.', 'On the shore I met men from a ship that had stopped for water.'),
    ('סיפרתי להם על הזקן, והם אמרו שהרבה מתו ככה.', 'I told them about the old man, and they said many had died that way.'),
    ('הם לקחו אותי איתם, ושוב ניצלתי בדרך שלא חשבתי עליה.', 'They took me with them, and again I was saved by a way I had not thought of.'))]),

 ('The City of Apes', 'עיר הקופים', [
  P(('הספינה הביאה אותי לעיר מוזרה על שפת הים.', 'The ship brought me to a strange city on the sea shore.'),
    ('בבוקר כל האנשים עלו על סירות ונסעו לים.', 'In the morning all the people got into boats and went off to sea.')),
  P(('שאלתי למה, והם אמרו: בלילה הקופים באים לעיר.', 'I asked why, and they said: at night the monkeys come into the city.'),
    ('מי שנשאר בבית לא רואה את הבוקר.', 'Whoever stays in the house does not see the morning.')),
  P(('בלילה ראיתי אותם מהמים: אלפי קופים ברחובות.', 'At night I saw them from the water: thousands of monkeys in the streets.'),
    ('בבוקר הם הלכו, וכולם חזרו לבתים כאילו כלום.', 'In the morning they went away, and everyone went back to the houses as if nothing had happened.'),
    ('גרתי שם חודש ולמדתי לחיות לפי הזמן של החיות.', 'I lived there a month and learned to live by the animals’ hours.'))]),

 ('The Mountain of Wrecks', 'הר הספינות השבורות', [
  P(('במסע השישי הרוח הביאה אותנו להר גבוה בתוך הים.', 'On the sixth voyage the wind brought us to a high mountain in the sea.'),
    ('מסביב להר היו ספינות שבורות רבות מאוד.', 'Around the mountain were very many broken ships.')),
  P(('בעל הספינה בכה ואמר: אף אחד לא יוצא מפה חי.', 'The ship’s owner wept and said: nobody gets out of here alive.'),
    ('הספינה שלנו נשברה על הסלעים, וכולנו ירדנו לחוף.', 'Our ship broke on the rocks, and we all went down to the shore.')),
  P(('על החוף היו אבנים יקרות בלי מספר, אבל אי אפשר היה לאכול אותן.', 'On the shore were countless precious stones, but they could not be eaten.'),
    ('החברים שלי מתו אחד אחרי השני, ואני נשארתי אחרון.', 'My friends died one after another, and I was the last left.'))]),

 ('The River Under the Mountain', 'הנהר מתחת להר', [
  P(('ראיתי נהר שיצא מהחוף והלך לתוך ההר.', 'I saw a river that came from the shore and went into the mountain.'),
    ('אמרתי: אם המים נכנסים, אולי הם גם יוצאים באיזה מקום.', 'I said: if the water goes in, perhaps it comes out somewhere too.')),
  P(('בניתי סירה קטנה מהעץ של הספינות השבורות.', 'I built a small boat from the wood of the broken ships.'),
    ('שמתי עליה אבנים יקרות ומעט אוכל ונכנסתי לחושך.', 'I put precious stones on it and a little food and went into the dark.')),
  P(('נסעתי שעות במים בין קירות אבן, בלי לראות כלום.', 'I travelled for hours on the water between stone walls, without seeing anything.'),
    ('נרדמתי מעייפות, וכשהתעוררתי הייתי מתחת לשמש.', 'I fell asleep from weariness, and when I woke I was under the sun.'))]),

 ('Serendib', 'סרנדיב', [
  P(('אנשים מצאו אותי על הנהר ולקחו אותי לאי סרנדיב.', 'People found me on the river and took me to the island of Serendib.'),
    ('זה היה המקום הכי יפה שראיתי בכל המסעות.', 'It was the most beautiful place I saw in all the voyages.')),
  P(('היו שם הרים גבוהים, נהרות מתוקים ופרחים בכל צבע.', 'There were high mountains, sweet rivers and flowers of every colour.'),
    ('המלך שמע עליי וקרא לי לארמון.', 'The king heard of me and called me to the palace.'),
    ('הוא שאל שאלות על בגדד ועל המלך שלנו.', 'He asked questions about Baghdad and about our king.')),
  P(('סיפרתי לו הכול, והוא הקשיב שעות בלי לזוז.', 'I told him everything, and he listened for hours without moving.'),
    ('הוא אמר: אתה תחזור הביתה, אבל קודם תעשה בשבילי דבר אחד.', 'He said: you will go home, but first do one thing for me.'))]),

 ('The King’s Letter', 'המכתב של המלך', [
  P(('המלך כתב מכתב למלך של בגדד והוסיף מתנות יקרות.', 'The king wrote a letter to the king of Baghdad and added precious gifts.'),
    ('הוא נתן לי אותם ואמר: קח אותם ביד שלך.', 'He gave them to me and said: carry them in your own hand.')),
  P(('נסעתי בים חודשים, והפעם בלי סופה ובלי חיה.', 'I travelled at sea for months, and this time with no storm and no beast.'),
    ('הגעתי לבגדד ונתתי את המכתב ואת המתנות.', 'I reached Baghdad and handed over the letter and the gifts.')),
  P(('המלך שלנו שאל אותי הרבה על האי הרחוק.', 'Our king asked me a great deal about the far island.'),
    ('אמרתי לו את האמת, וגם את מה שקשה להאמין.', 'I told him the truth, and also what is hard to believe.'),
    ('הוא צחק ואמר: אתה האיש שהים לא הצליח להרוג.', 'He laughed and said: you are the man the sea did not manage to kill.'))]),

 ('One Last Time', 'עוד פעם אחרונה', [
  P(('אמרתי לעצמי: זהו, נגמר, אני נשאר בבית.', 'I said to myself: that is it, it is over, I am staying at home.'),
    ('אבל אחרי שנה שוב שמעתי את הים קורא לי.', 'But after a year I again heard the sea calling me.')),
  P(('החברים שלי אמרו: שש פעמים ניצלת, אל תנסה בפעם השביעית.', 'My friends said: you were saved six times, do not try a seventh.'),
    ('צחקתי ואמרתי שהמזל שלי חזק.', 'I laughed and said my luck was strong.')),
  P(('יצאתי לים, ואחרי חודש ספינת שודדים תפסה אותנו.', 'I put out to sea, and after a month a pirate ship caught us.'),
    ('הם לקחו את הסחורה ומכרו אותנו כעבדים בעיר רחוקה.', 'They took the goods and sold us as slaves in a far city.'),
    ('קנה אותי סוחר עשיר שהיה איש טוב.', 'A rich merchant who was a good man bought me.'))]),

 ('The Elephants', 'הפילים', [
  P(('הסוחר נתן לי קשת וחצים ואמר לי לעלות על העץ ולחכות לפילים.', 'The merchant gave me a bow and arrows and told me to climb the tree and wait for the elephants.'),
    ('כל לילה ישבתי על עץ גבוה ביער.', 'Every night I sat in a high tree in the forest.')),
  P(('ציידתי פיל אחד, והסוחר קיבל את השן ומכר אותה ביוקר.', 'I hunted one elephant, and the merchant took the tusk and sold it dear.'),
    ('כך עברו חודשים, ולא אהבתי את העבודה הזאת בכלל.', 'So months passed, and I did not like this work at all.')),
  P(('לילה אחד באו הרבה פילים ועמדו מתחת לעץ שלי.', 'One night many elephants came and stood under my tree.'),
    ('הם לא הלכו, והבנתי שהם באו בשבילי.', 'They did not leave, and I understood that they had come for me.'))]),

 ('The Elephant Who Carried Me', 'הפיל שנשא אותי', [
  P(('הפיל הכי גדול הרים אותי מהעץ עם האף הארוך שלו.', 'The biggest elephant lifted me from the tree with its long nose.'),
    ('פחדתי מאוד וחשבתי שזה הסוף שלי.', 'I was very frightened and thought this was my end.')),
  P(('אבל הוא הניח אותי על הגב שלו ולקח אותי ליער.', 'But it set me on its back and took me into the forest.'),
    ('הוא הביא אותי למקום מלא עצמות ושיניים של פילים.', 'It brought me to a place full of the bones and tusks of elephants.'),
    ('הבנתי: הם הראו לי איפה הם מתים, כדי שלא נהרוג עוד.', 'I understood: they showed me where they die, so that we would kill no more.')),
  P(('חזרתי לסוחר וסיפרתי לו הכול.', 'I went back to the merchant and told him everything.'),
    ('הוא בכה, שחרר אותי, ונתן לי חלק מהכסף שלו.', 'He wept, set me free, and gave me part of his money.'),
    ('אמר לי: קח את הכסף ולך הביתה, כי למדת משהו שאני לא ידעתי.', 'He said to me: take the money and go home, because you have learned something I did not know.'))]),

 ('The Last Return', 'החזרה האחרונה', [
  P(('חזרתי לבגדד עשיר יותר מכל הפעמים.', 'I came back to Baghdad richer than all the other times.'),
    ('בניתי את הבית הזה, וישבתי בו בשקט.', 'I built this house, and sat in it quietly.')),
  P(('סינדבאד הסתכל על הסבל וחייך.', 'Sindbad looked at the porter and smiled.'),
    ('הוא אמר: עכשיו אתה מבין מאיפה בא הכסף.', 'He said: now you understand where the money came from.'),
    ('הוא אמר: כל מטבע פה עלה לי משהו שלא רואים.', 'He said: every coin here cost me something you cannot see.')),
  P(('הוא נתן לסבל כסף וביקש שיבוא לאכול כל יום.', 'He gave the porter money and asked him to come and eat every day.'),
    ('הסבל בא, והם ישבו יחד שנים וסיפרו סיפורים.', 'The porter came, and they sat together for years and told stories.')),
  P(('וכך שני האנשים עם אותו שם נהיו חברים.', 'And so the two men with the same name became friends.'),
    ('אחד ראה את העולם, והשני ראה רחוב אחד, ושניהם ידעו משהו.', 'One had seen the world, and the other one street, and both knew something.'))]),
]

if __name__ == '__main__':
    raise SystemExit(book('sindbad', {'en': "Sindbad's Seven Voyages",
                                      'he': 'שבעת מסעות סינדבאד'}, 'intermediate',
                          CHAPTERS, unit='Chapter', unit_he='פרק', shelf=11, meta=META))
