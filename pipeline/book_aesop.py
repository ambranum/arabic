#!/usr/bin/env python3
"""خرافات إيسوب — thirty fables, retold in spoken Palestinian, graded to beginner.

Aesop's fables are ancient and anonymous in any practical sense — public domain by age, with no
edition being translated. These are retellings from the traditional plots.

WHY THIS SITS BESIDE JUHA. The animal-fable shape is already familiar to an Arabic learner from
كليلة ودمنة, and the plots are known in English, so nothing is spent on working out what happens
— all of the attention goes to the Arabic. Where Juha teaches the rhythm of everyday speech, these
teach the rhythm of narrative: a setup, a turn, a line at the end.

Written against what pipeline/bookshelf_check.py measures, and tighter than Juha was on its first
pass: sentences at or under ~25 Arabic characters, one clause each, a small recurring cast of
animals (ثعلب، أسد، فار، ذيب، غراب) so the same words come back fable after fable.

Each fable ends on its moral as a separate short sentence rather than a clause tacked onto the
action — which keeps the last line quotable and the sentence length down at the same time.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated), but
every WORD's root, meaning and pronunciation is looked up in Maknuune by the ingest pipeline.

Run:  python3 pipeline/book_aesop.py    then ingest each chapter + build_app.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bookshelf import P, emit_book

BOOK_ID = 'aesop'
BOOK_TITLE = {'en': "Aesop's Fables", 'ar': 'خرافات إيسوب'}

# (english title, arabic title, [paragraph, ...])
CHAPTERS = [
 ('The Oak and the Reed', 'السنديانة والقصبة', [
  P(('سنديانة كبيرة ضحكت عالقصبة.', 'A big oak laughed at the reed.'),
    ('قالت: إنتِ ضعيفة وبتنحني.', 'She said: you are weak and you bend.')),
  P(('قالت القصبة: بنحني وبضل.', 'The reed said: I bend and I remain.')),
  P(('إجت عاصفة قوية بالليل.', 'A strong storm came at night.'),
    ('السنديانة وقعت والقصبة ضلت.', 'The oak fell and the reed stayed.'),
    ('اللي بينحني ما بينكسر.', 'What bends does not break.'))]),

 ('The Fox and the Grapes', 'الثعلب والعنب', [
  P(('ثعلب شاف عنب عالي.', 'A fox saw some grapes up high.'),
    ('العنب كان حلو ولونه حلو.', 'The grapes were sweet and a nice colour.')),
  P(('نط مرة، ومرتين، وتلاتة.', 'He jumped once, twice, and three times.'),
    ('ما وصل.', "He didn't reach them.")),
  P(('مشي وقال: العنب حامض.', 'He walked off and said: the grapes are sour.'),
    ('اللي ما بيقدر عليه، بيعيبه.', 'What a person cannot get, he finds fault with.'))]),

 ('The Tortoise and the Hare', 'السلحفاة والأرنب', [
  P(('الأرنب ضحك عالسلحفاة.', 'The hare laughed at the tortoise.'),
    ('قال لها: إنتِ بطيئة كتير.', 'He said to her: you are very slow.'),
    ('قالت: تعال نتسابق.', 'She said: come, let us race.')),
  P(('الأرنب ركض وابتعد كتير.', 'The hare ran and got far ahead.'),
    ('وبعدين نام تحت شجرة.', 'And then he slept under a tree.')),
  P(('السلحفاة مشيت وما وقفت.', 'The tortoise walked and did not stop.'),
    ('وصلت قبله.', 'She arrived before him.'),
    ('البطيء اللي ما بيوقف بيوصل.', 'The slow one who never stops arrives.'))]),

 ('The Lion and the Mouse', 'الأسد والفار', [
  P(('فار زغير مشي على أسد نايم.', 'A small mouse walked on a sleeping lion.'),
    ('الأسد صحي ومسكه.', 'The lion woke and caught him.')),
  P(('قال الفار: خليني وبساعدك يوم.', 'The mouse said: let me go and one day I will help you.'),
    ('الأسد ضحك وتركه.', 'The lion laughed and let him go.')),
  P(('بعد شهر، وقع الأسد بشبكة.', 'A month later, the lion fell in a net.'),
    ('الفار إجا وقرض الحبال.', 'The mouse came and gnawed the ropes.'),
    ('الزغير بيقدر يساعد الكبير.', 'The small one can help the big one.'))]),

 ('The Fox and the Stork', 'الثعلب واللقلق', [
  P(('الثعلب عزم اللقلق على أكل.', 'The fox invited the stork for food.'),
    ('حط الأكل بصحن واسع.', 'He put the food in a wide flat plate.'),
    ('منقار اللقلق طويل وما أكل.', "The stork's beak was long and he did not eat."),),
  P(('بعد أسبوع، اللقلق عزمه.', 'A week later, the stork invited him.'),
    ('حط الأكل بجرة ضيقة.', 'He put the food in a narrow jar.')),
  P(('الثعلب شم وما وصل.', 'The fox smelled it and could not reach.'),
    ('اللي بتعمله بينعمل فيك.', 'What you do is done to you.'))]),

 ('The Fisherman and the Little Fish', 'الصياد والسمكة الزغيرة', [
  P(('صياد مسك سمكة زغيرة.', 'A fisherman caught a small fish.'),
    ('قالت له: أنا زغيرة، رجعني.', 'She said to him: I am small, put me back.'),
    ('بكبر وبترجع تمسكني.', 'I will grow and you will catch me again.')),
  P(('قال الصياد: ما بترك اللي بإيدي.', 'The fisherman said: I do not leave what is in my hand.'),
    ('وأنا ما بعرف بكرا.', 'And I do not know about tomorrow.'),
    ('عصفور بالإيد ولا عشرة عالشجرة.',
     'A bird in the hand is better than ten on the tree.'))]),

 ('The Dove and the Ant', 'الحمامة والنملة', [
  P(('نملة وقعت بالمي.', 'An ant fell in the water.'),
    ('حمامة رمت لها ورقة شجر.', 'A dove threw her a leaf.'),
    ('النملة طلعت عليها ونجت.', 'The ant climbed on it and was saved.')),
  P(('بعد كم يوم، إجا صياد.', 'A few days later, a hunter came.'),
    ('صوب على الحمامة.', 'He aimed at the dove.')),
  P(('النملة قرصته بإجره.', 'The ant bit him on the foot.'),
    ('الحمامة طارت ونجت.', 'The dove flew away and was saved.'),
    ('المعروف بيرجع لصاحبه.', 'A kindness comes back to the one who gave it.'))]),

 ('The Stag at the Pool', 'الغزال والبركة', [
  P(('غزال شاف حاله بالمي.', 'A stag saw himself in the water.'),
    ('عجبه قرونه الكبيرة.', 'He liked his big horns.'),
    ('وما عجبته إجريه الرفيعة.', 'And he did not like his thin legs.')),
  P(('إجا صياد وركض وراه.', 'A hunter came and ran after him.'),
    ('إجريه أنقذوه بالسهل.', 'His legs saved him on the plain.')),
  P(('بس قرونه علقت بالشجر.', 'But his horns caught in the trees.'),
    ('اللي بنحبه بيأذينا أحياناً.', 'What we love sometimes harms us.'))]),

 ('The Peacock and the Crane', 'الطاووس والكركي', [
  P(('الطاووس فتح ريشه الحلو.', 'The peacock spread his beautiful feathers.'),
    ('قال للكركي: شوف ألواني.', 'He said to the crane: look at my colours.'),
    ('ريشك رمادي وباهت.', 'Your feathers are grey and dull.')),
  P(('الكركي فرد جناحيه وطار.', 'The crane spread his wings and flew.'),
    ('قال: أنا بطير وإنت بتمشي.', 'He said: I fly and you walk.'),
    ('الحلو مش دايماً الأحسن.', 'The prettiest is not always the best.'))]),

 ('The Wolf and the Crane', 'الذيب والكركي', [
  P(('عظمة وقفت بزور الذيب.', 'A bone stuck in the wolf’s throat.'),
    ('وعد الكركي بمكافأة كبيرة.', 'He promised the crane a big reward.')),
  P(('الكركي حط راسه بتم الذيب.', 'The crane put his head in the wolf’s mouth.'),
    ('طلّع العظمة وطلب المكافأة.', 'He took the bone out and asked for the reward.')),
  P(('قال الذيب: مكافأتك إنك عايش.',
     'The wolf said: your reward is that you are alive.'),
    ('ما تنتظر شكر من ظالم.', 'Do not expect thanks from a cruel one.'))]),

 ('The Town Mouse and the Country Mouse', 'فار المدينة وفار الضيعة', [
  P(('فار من المدينة زار قريبه.', 'A mouse from the city visited his relative.'),
    ('قريبه ساكن بالضيعة.', 'His relative lived in the village.')),
  P(('أكلوا حب وخبز يابس.', 'They ate grain and dry bread.'),
    ('قال فار المدينة: تعال معي.', 'The city mouse said: come with me.')),
  P(('بالمدينة، الأكل كان كتير وحلو.', 'In the city, the food was plenty and good.'),
    ('بس القطة إجت مرتين.', 'But the cat came twice.')),
  P(('فار الضيعة رجع عالضيعة.', 'The village mouse went back to the village.'),
    ('قال: خبز يابس وأنا مرتاح.', 'He said: dry bread, and I am at peace.'))]),

 ('The Boastful Traveller', 'المسافر المفشخر', [
  P(('واحد رجع من السفر وصار يحكي.', 'A man came back from travelling and started talking.'),
    ('قال: بجزيرة بعيدة نطيت نطة كبيرة.', 'He said: on a far island I made a huge jump.')),
  P(('الناس سمعوا وسكتوا.', 'People listened and said nothing.'),
    ('واحد قال: نط هون قدامنا.', 'One said: jump here in front of us.')),
  P(('ما نط وسكت.', 'He did not jump and fell silent.'),
    ('اللي بتعمله بيحكي عنك.', 'What you do speaks for you.'))]),

 ('The Frog and the Ox', 'الضفدع والثور', [
  P(('ضفدع شاف ثور كبير.', 'A frog saw a big ox.'),
    ('بده يصير كبير مثله.', 'He wanted to become big like him.')),
  P(('نفخ حاله شوي.', 'He puffed himself up a little.'),
    ('سأل أولاده: صرت مثله؟', 'He asked his children: have I become like him?'),
    ('قالوا: لسا لأ.', 'They said: not yet.')),
  P(('نفخ أكتر وأكتر وانفجر.', 'He puffed more and more and burst.'),
    ('اعرف حالك واقنع فيها.', 'Know yourself and be content with it.'))]),

 ('The Farmer and the Snake', 'الفلاح والحية', [
  P(('فلاح لقي حية نص ميتة من البرد.', 'A farmer found a snake half dead from the cold.'),
    ('حطها بصدره لتدفى.', 'He put it in his shirt to warm it.')),
  P(('الحية دفيت وقويت.', 'The snake warmed up and grew strong.'),
    ('ولدغته.', 'And it bit him.')),
  P(('قال وهو عم يموت: أنا الغلطان.', 'He said as he was dying: I am the one at fault.'),
    ('الطبع ما بيتغير.', 'A nature does not change.'))]),

 ('The Ass and His Masters', 'الحمار وأصحابه', [
  P(('حمار زعل من صاحبه الفلاح.', 'A donkey was unhappy with his farmer owner.'),
    ('طلب صاحب تاني.', 'He asked for another owner.')),
  P(('صار عند الفخراني وشغله أتقل.', 'He went to the potter and his work was heavier.'),
    ('طلب تغيير كمان مرة.', 'He asked to change again.')),
  P(('صار عند الدباغ.', 'He went to the tanner.'),
    ('قال: يا ريتني ضلّيت بأول محل.',
     'He said: I wish I had stayed in the first place.'))]),
 ('The Goose and the Golden Eggs', 'الوزة وبيض الدهب', [
  P(('واحد عنده وزة غريبة.', 'A man had a strange goose.'),
    ('كل يوم بتبيض بيضة دهب.', 'Every day she laid a golden egg.')),
  P(('صار طماع وما بده يستنى.', 'He became greedy and did not want to wait.'),
    ('قال: الدهب كله جواتها.', 'He said: all the gold is inside her.')),
  P(('ذبح الوزة وما لقي إشي.', 'He killed the goose and found nothing.'),
    ('الطمع بيضيع القليل والكتير.', 'Greed loses both the little and the much.'))]),

 ('The Dog and His Reflection', 'الكلب وخياله', [
  P(('كلب كان شايل لحمة بتمه.', 'A dog was carrying meat in his mouth.'),
    ('مرق فوق جسر عالمي.', 'He passed over a bridge above the water.')),
  P(('شاف خياله بالمي.', 'He saw his reflection in the water.'),
    ('حسب إنه كلب تاني معه لحمة.', 'He thought it was another dog with meat.')),
  P(('فتح تمه ليهوش عليه.', 'He opened his mouth to bark at him.'),
    ('اللحمة وقعت وراحت.', 'The meat fell and was lost.'),
    ('اللي بده كل إشي بيخسر اللي معه.', 'Whoever wants everything loses what he has.'))]),

 ('The Old Man and Death', 'الرجل الكبير والموت', [
  P(('رجل كبير كان شايل حطب تقيل.', 'An old man was carrying heavy firewood.'),
    ('تعب وحط الحطب عالأرض.', 'He got tired and put the wood down.')),
  P(('قال: يا ريت الموت يجيني.', 'He said: I wish death would come to me.'),
    ('إجا الموت وقال: نعم؟', 'Death came and said: yes?')),
  P(('خاف الرجل وقال: ساعدني أشيل الحطب.',
     'The man was afraid and said: help me lift the wood.'),
    ('بنطلب إشي ولما بيجي بنخاف.',
     'We ask for a thing, and when it comes we are afraid.'))]),

 ('The Two Travellers and the Bear', 'المسافرين والدب', [
  P(('اتنين أصحاب كانوا مسافرين.', 'Two friends were travelling.'),
    ('طلع عليهم دب بالطريق.', 'A bear came upon them on the road.')),
  P(('الأول طلع عالشجرة بسرعة.', 'The first climbed the tree quickly.'),
    ('التاني رمى حاله عالأرض.', 'The second threw himself on the ground.')),
  P(('الدب شمه وراح.', 'The bear sniffed him and left.'),
    ('نزل الأول وسأل: شو قال لك؟', 'The first came down and asked: what did he say to you?')),
  P(('قال: قال لي لا تسافر مع حدا بيتركك.',
     'He said: he told me not to travel with someone who leaves you.'))]),

 ('The Crow and the Pitcher', 'الغراب والجرة', [
  P(('غراب عطشان لقي جرة.', 'A thirsty crow found a jug.'),
    ('المي كانت بالأسفل بعيدة.', 'The water was far down at the bottom.')),
  P(('حاول يوصل ومنقاره قصير.', 'He tried to reach and his beak was short.'),
    ('فكر شوي.', 'He thought a little.')),
  P(('صار يحط حجار زغيرة بالجرة.', 'He started putting small stones in the jug.'),
    ('المي طلعت لفوق وشرب.', 'The water rose and he drank.'),
    ('العقل بيعمل اللي القوة ما بتعمله.', 'The mind does what strength cannot.'))]),

 ('The Bundle of Sticks', 'حزمة العصي', [
  P(('أب عنده كم ولد بيتخانقوا.', 'A father had several sons who quarrelled.'),
    ('جاب حزمة عصي وقال: اكسروها.', 'He brought a bundle of sticks and said: break it.')),
  P(('حاولوا كلهم وما قدروا.', 'They all tried and could not.'),
    ('فك الحزمة وأعطاهم عصاية عصاية.', 'He untied the bundle and gave them one stick at a time.')),
  P(('انكسروا كلهم بسهولة.', 'They all broke easily.'),
    ('مع بعض بتقووا، ولحالكم بتنكسروا.',
     'Together you are strong; alone you break.'))]),

 ('Belling the Cat', 'جرس القطة', [
  P(('الفيران اجتمعوا بالسر.', 'The mice gathered in secret.'),
    ('القطة كانت تاكل منهم كل يوم.', 'The cat was eating them every day.')),
  P(('فار زغير قال: نحط جرس عليها.', 'A small mouse said: let us put a bell on her.'),
    ('كلهم صفقوا وفرحوا بالفكرة.', 'They all clapped and liked the idea.')),
  P(('فار كبير سأل: مين بيحط الجرس؟', 'An old mouse asked: who puts the bell on?'),
    ('محدا رد.', 'Nobody answered.'),
    ('الفكرة سهلة والعمل صعب.', 'The idea is easy and the doing is hard.'))]),

 ('The Fox and the Crow', 'الثعلب والغراب', [
  P(('غراب مسك جبنة بتمه.', 'A crow held a piece of cheese in his beak.'),
    ('قعد على غصن عالي.', 'He sat on a high branch.')),
  P(('الثعلب شافه وقال: يا أحلى طير!', 'The fox saw him and said: what a beautiful bird!'),
    ('صوتك أكيد أحلى من ريشك.', 'Your voice must be lovelier than your feathers.')),
  P(('الغراب فرح وفتح تمه ليغني.', 'The crow was pleased and opened his beak to sing.'),
    ('الجبنة وقعت والثعلب أخذها.', 'The cheese fell and the fox took it.'),
    ('دير بالك من اللي بيمدحك كتير.', 'Beware of the one who praises you too much.'))]),

 ("The Donkey in the Lion's Skin", 'الحمار بجلد الأسد', [
  P(('حمار لقي جلد أسد ولبسه.', 'A donkey found a lion skin and wore it.'),
    ('صار يخوف الحيوانات.', 'He started frightening the animals.')),
  P(('كلهم هربوا منه وهو مبسوط.', 'They all ran from him and he was pleased.'),
    ('نسي حاله ونهق.', 'He forgot himself and brayed.')),
  P(('عرفوه من صوته وضحكوا.', 'They knew him by his voice and laughed.'),
    ('اللبس بيغير الشكل مش الصوت.', 'Clothes change the look, not the voice.'))]),

 ("The Wolf in Sheep's Clothing", 'الذيب بجلد الخروف', [
  P(('ذيب لبس جلد خروف.', 'A wolf put on a sheepskin.'),
    ('فات بين الغنم وما حدا انتبه.', 'He entered among the sheep and nobody noticed.')),
  P(('بالليل، الراعي جاع.', 'At night, the shepherd got hungry.'),
    ('دخل وأخذ أول خروف لقيه.', 'He went in and took the first sheep he found.')),
  P(('كان الذيب.', 'It was the wolf.'),
    ('الحيلة بترجع على صاحبها.', 'A trick comes back on the one who plays it.'))]),

 ('The Boy Who Cried Wolf', 'الولد والذيب', [
  P(('ولد كان يرعى غنم عالجبل.', 'A boy used to herd sheep on the hill.'),
    ('زهق وصار يصرخ: ذيب! ذيب!', 'He got bored and started shouting: wolf! wolf!')),
  P(('الناس ركضوا وما لقوا إشي.', 'People ran and found nothing.'),
    ('عمل هيك مرتين وضحك.', 'He did this twice and laughed.')),
  P(('بيوم، إجا ذيب حقيقي.', 'One day, a real wolf came.'),
    ('صرخ الولد وما حدا إجا.', 'The boy shouted and nobody came.'),
    ('الكذاب محدا بيصدقه بالآخر.', 'In the end nobody believes a liar.'))]),

 ('The Milkmaid and Her Pail', 'البنت وسطل الحليب', [
  P(('بنت كانت شايلة سطل حليب.', 'A girl was carrying a pail of milk.'),
    ('كانت ماشية عالسوق.', 'She was walking to the market.')),
  P(('صارت تفكر بالمصاري.', 'She started thinking about the money.'),
    ('قالت: بشتري بيض ودجاج.', 'She said: I will buy eggs and chickens.'),
    ('وبعدين بشتري فستان حلو.', 'And then I will buy a nice dress.')),
  P(('وهي عم تفكر، هزت راسها.', 'While she was thinking, she shook her head.'),
    ('السطل وقع والحليب راح.', 'The pail fell and the milk was gone.'),
    ('ما تعد الشغلة قبل ما تصير.', 'Do not count a thing before it happens.'))]),

 ('The Ant and the Grasshopper', 'النملة والصرصور', [
  P(('بالصيف، النملة شغلت كتير.', 'In the summer, the ant worked hard.'),
    ('كانت تجمع حب وتخزنه.', 'She used to gather grain and store it.')),
  P(('الصرصور كان يغني ويلعب.', 'The grasshopper used to sing and play.'),
    ('قال لها: ليش تتعبي؟', 'He said to her: why tire yourself?')),
  P(('إجا الشتا والبرد.', 'The winter and the cold came.'),
    ('الصرصور جاع ودق عالباب.', 'The grasshopper got hungry and knocked on the door.'),
    ('وقت الشغل مش وقت الغنا.', 'The time for work is not the time for singing.'))]),

 ('The Wind and the Sun', 'الريح والشمس', [
  P(('الريح والشمس اختلفوا.', 'The wind and the sun disagreed.'),
    ('مين أقوى فيهم؟', 'Which of them is stronger?')),
  P(('شافوا مسافر لابس كبوت.', 'They saw a traveller wearing a coat.'),
    ('قالوا: اللي بيشلحه هو الأقوى.', 'They said: whoever takes it off him is stronger.')),
  P(('الريح نفخت بقوة.', 'The wind blew hard.'),
    ('المسافر شد الكبوت عليه.', 'The traveller pulled the coat tighter.')),
  P(('الشمس دفت بهدوء.', 'The sun warmed gently.'),
    ('المسافر شلح كبوته لحاله.', 'The traveller took his coat off himself.'),
    ('اللطف أقوى من القوة.', 'Gentleness is stronger than force.'))]),

 ('The Miser and His Gold', 'البخيل ودهبه', [
  P(('بخيل دفن دهبه تحت حجر.', 'A miser buried his gold under a stone.'),
    ('كل يوم يروح يتطلع عليه.', 'Every day he went to look at it.')),
  P(('بيوم، لقي الحفرة فاضية.', 'One day, he found the hole empty.'),
    ('قعد يبكي ويصرخ.', 'He sat crying and shouting.')),
  P(('جاره قال له: حط حجر مكانه.', 'His neighbour said to him: put a stone in its place.'),
    ('إنت ما استعملت الدهب أصلاً.', 'You never used the gold anyway.'),
    ('المال اللي ما بينصرف زي الحجر.', 'Money that is never spent is like a stone.'))]),

]

if __name__ == '__main__':
    emit_book(BOOK_ID, BOOK_TITLE, 'beginner', CHAPTERS, unit='Fable', unit_ar='خرافة', shelf=2,
              meta={'work': "Aesop's Fables", 'author': 'Aesop (traditional)',
                    'year': 'c. 600 BCE', 'status': 'public domain — ancient, anonymous'})
