#!/usr/bin/env python3
"""السندباد البحري — the seven voyages, retold in spoken Palestinian, graded to intermediate.

Sindbad belongs to the ألف ليلة وليلة tradition: medieval, anonymous, public domain by age. These
are retellings from the traditional plots, not a translation of Burton, Lane or any other edition.

WHY THIS BOOK, HERE. It is structurally the same thing that works about Around the World in 80
Days — a journey, one self-contained episode per chapter, a reason to open the next one — except
it is Arab heritage rather than Victorian Europe, and a Palestinian reader meets it as something
already half known.

LEVEL. The existing intermediate book runs 49.5 characters a sentence against a 32.5 baseline for
the intermediate short stories, so the middle of the shelf currently has no gentle way in. This
one is deliberately written near the baseline: past-tense narrative with real connectors
(لما، بعد ما، لأنه، بس، وقتها) and relative clauses with اللي, but one clause at a time.

Every voyage runs four chapters — out, the trouble, the escape, the return — so a reader can stop
after any of them and has finished something.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated), but
every WORD's root, meaning and pronunciation is looked up in Maknuune by the ingest pipeline.

Run:  python3 pipeline/book_sindbad.py    then ingest each chapter + build_app.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bookshelf import P, emit_book

BOOK_ID = 'sindbad'
BOOK_TITLE = {'en': "Sindbad's Seven Voyages", 'ar': 'رحلات السندباد السبع'}

# (english title, arabic title, [paragraph, ...])
CHAPTERS = [
 # ---------------- Voyage One ----------------
 ('The Porter and the Sailor', 'الحمّال والبحري', [
  P(('ببغداد، كان في حمّال فقير اسمه السندباد.', 'In Baghdad there was a poor porter named Sindbad.'),
    ('بيوم حر، قعد يرتاح قدام بيت كبير.', 'On a hot day, he sat resting in front of a big house.'),
    ('سمع موسيقى وضحك من جوا.', 'He heard music and laughter from inside.')),
  P(('قال بصوت عالي: ليش هاد غني وأنا تعبان؟',
     'He said out loud: why is this man rich and I am worn out?'),
    ('صاحب البيت سمعه وطلع عليه.', 'The owner of the house heard him and came out to him.')),
  P(('قال له: أنا كمان اسمي السندباد.', 'He said to him: my name is Sindbad too.'),
    ('وأنا ما جبت مصاريي بالسهل.', 'And I did not get my money easily.'),
    ('أدخل واقعد، وبحكي لك سبع رحلات.',
     'Come in and sit, and I will tell you seven voyages.'))]),

 ('The First Ship', 'أول سفينة', [
  P(('قال السندباد: ورثت مصاري من أبوي.', 'Sindbad said: I inherited money from my father.'),
    ('صرفتها كلها بسرعة على أصحاب وأكل.',
     'I spent it all quickly on friends and food.'),
    ('لما خلصت، عرفت إني لازم أشتغل.',
     'When it ran out, I knew I had to work.')),
  P(('بعت اللي ضل عندي واشتريت بضاعة.', 'I sold what was left and bought goods.'),
    ('ركبت سفينة رايحة على بلاد بعيدة.', 'I boarded a ship going to far countries.')),
  P(('البحر كان هادي بالأول.', 'The sea was calm at first.'),
    ('كنت مبسوط وحاسس إني عملت صح.', 'I was happy and felt I had done the right thing.'))]),

 ('The Island That Moved', 'الجزيرة اللي تحركت', [
  P(('بعد كم أسبوع، وقفنا عند جزيرة زغيرة.', 'After a few weeks, we stopped at a small island.'),
    ('نزلنا عليها ولعبنا وطبخنا أكل.', 'We got out on it and played and cooked food.'),
    ('أشعلنا نار عالأرض لنسخن الأكل.', 'We lit a fire on the ground to heat the food.')),
  P(('فجأة، الأرض تحركت تحت إجرينا.', 'Suddenly, the ground moved under our feet.'),
    ('صرخ الريس من السفينة: هربوا!', 'The captain shouted from the ship: run!'),
    ('هاي مش جزيرة، هاي حوت نايم.', 'This is not an island, this is a sleeping whale.')),
  P(('الحوت حس بالنار وغطس بالبحر.', 'The whale felt the fire and dived into the sea.'),
    ('الناس ركضوا عالسفينة وأنا تأخرت.', 'The men ran to the ship and I was late.'),
    ('ضلّيت لحالي بالمي.', 'I was left alone in the water.'))]),

 ('The King of the Sea Horses', 'ملك خيل البحر', [
  P(('مسكت قطعة خشب وضلّيت عليها يومين.', 'I grabbed a piece of wood and stayed on it two days.'),
    ('الموج رماني على جزيرة حقيقية.', 'The waves threw me onto a real island.')),
  P(('لقيت ناس بيربوا خيل عالشط.', 'I found people raising horses on the shore.'),
    ('أخذوني عند ملكهم واسمه مهرجان.', 'They took me to their king, named Mihrjan.'),
    ('الملك سمع قصتي وحبني.', 'The king heard my story and liked me.')),
  P(('بعد شهور، وصلت سفينة عالميناء.', 'After months, a ship arrived at the harbour.'),
    ('كانت نفس السفينة اللي تركتني.', 'It was the same ship that had left me.'),
    ('بضاعتي كانت لسا فيها، ورجعت لبغداد غني.',
     'My goods were still on it, and I returned to Baghdad rich.'))]),

 # ---------------- Voyage Two ----------------
 ('Bored at Home', 'زهقان بالبيت', [
  P(('قعدت ببغداد وعشت مرتاح.', 'I sat in Baghdad and lived comfortably.'),
    ('بس بعد سنة، صرت أزهق من الراحة.', 'But after a year, I began to tire of comfort.'),
    ('كنت بفكر بالبحر كل يوم.', 'I thought about the sea every day.')),
  P(('اشتريت بضاعة جديدة وركبت سفينة تانية.', 'I bought new goods and boarded another ship.'),
    ('وقفنا عند جزيرة خضرا وفيها مي حلوة.', 'We stopped at a green island with fresh water.')),
  P(('أكلت وشربت ونمت تحت شجرة.', 'I ate and drank and slept under a tree.'),
    ('لما صحيت، السفينة كانت راحت.', 'When I woke, the ship had gone.'),
    ('نسيوني وأنا نايم.', 'They forgot me while I was asleep.'))]),

 ('The Great White Dome', 'القبة البيضا', [
  P(('طلعت على شجرة عالية لأشوف.', 'I climbed a tall tree to look around.'),
    ('شفت قبة بيضا كبيرة بالبعيد.', 'I saw a big white dome in the distance.'),
    ('مشيت لعندها وهي بلا باب ولا شباك.',
     'I walked to it and it had no door and no window.')),
  P(('فجأة صارت الدنيا عتمة.', 'Suddenly the world went dark.'),
    ('طير ضخم كان طاير فوقي.', 'A huge bird was flying above me.'),
    ('جناحاته غطوا الشمس كلها.', 'Its wings covered the whole sun.')),
  P(('وقتها فهمت: القبة كانت بيضة.', 'Then I understood: the dome was an egg.'),
    ('والطير اسمه الرخ.', 'And the bird was called the roc.'))]),

 ('The Valley of Diamonds', 'وادي الألماس', [
  P(('ربطت حالي بعمامتي على إجر الطير.', 'I tied myself with my turban to the bird’s leg.'),
    ('لما طار، حملني معه بعيد كتير.', 'When it flew, it carried me far away.'),
    ('نزل بوادي عميق بين جبال.', 'It landed in a deep valley between mountains.')),
  P(('فكيت الحبل وتطلعت حولي.', 'I untied the rope and looked around me.'),
    ('الأرض كانت مليانة ألماس.', 'The ground was covered in diamonds.'),
    ('بس بين الحجار كان في حيات كبيرة.', 'But among the stones there were huge snakes.')),
  P(('ما قدرت أطلع لأن الجبال عالية.', 'I could not climb out because the mountains were high.'),
    ('خبيت حالي بمغارة كل الليل.', 'I hid myself in a cave all night.'))]),

 ('The Meat and the Eagles', 'اللحمة والنسور', [
  P(('الصبح، وقعت قطعة لحمة كبيرة جنبي.', 'In the morning, a big piece of meat fell beside me.'),
    ('تذكرت حكاية سمعتها من التجار.', 'I remembered a story I had heard from merchants.'),
    ('التجار بيرموا لحمة، والألماس بيلزق فيها.',
     'The merchants throw meat, and the diamonds stick to it.')),
  P(('حطيت ألماس بجيبي وربطت حالي باللحمة.',
     'I put diamonds in my pocket and tied myself to the meat.'),
    ('إجا نسر كبير وحملها لفوق.', 'A big eagle came and carried it up.')),
  P(('التجار صرخوا عالنسر فترك اللحمة.', 'The merchants shouted at the eagle so it left the meat.'),
    ('لما شافوني، خافوا وبعدين ضحكوا.', 'When they saw me, they were afraid and then they laughed.'),
    ('أعطيتهم شوية ألماس ورجعنا مع بعض.',
     'I gave them some diamonds and we went back together.'))]),

 # ---------------- Voyage Three ----------------
 ('The Hairy People', 'الناس الشعرانية', [
  P(('الرحلة التالتة بلشت زي غيرها.', 'The third voyage began like the others.'),
    ('بس ريح قوية رمتنا على جزيرة غريبة.',
     'But a strong wind threw us onto a strange island.')),
  P(('طلعوا علينا ناس زغار وشعرانيين.', 'Small, hairy people came out at us.'),
    ('كانوا كتار وما بنفهم حكيهم.', 'They were many and we did not understand their speech.'),
    ('أخذوا السفينة ورمونا عالشط.', 'They took the ship and threw us on the shore.')),
  P(('مشينا لجوا الجزيرة وشفنا قصر كبير.', 'We walked inland and saw a big palace.'),
    ('الباب كان مفتوح وما في حدا.', 'The door was open and there was nobody.'))]),

 ('The Giant', 'العملاق', [
  P(('بالليل، سمعنا صوت إجرين تقال.', 'At night, we heard the sound of heavy feet.'),
    ('فات علينا عملاق طوله زي نخلة.', 'A giant as tall as a palm tree came in on us.'),
    ('عينه وحدة بنص وجهه.', 'He had one eye in the middle of his face.')),
  P(('تطلع فينا ومسك أكبر واحد فينا.', 'He looked at us and grabbed the biggest of us.'),
    ('ما بحب أحكي شو صار بعدها.', 'I do not like to say what happened after that.')),
  P(('ضلّينا خايفين لآخر الليل.', 'We stayed afraid until the end of the night.'),
    ('الصبح طلع وترك الباب مفتوح.', 'In the morning he went out and left the door open.'))]),

 ('The Iron in the Fire', 'الحديد بالنار', [
  P(('قلت للباقيين: لازم نعمل إشي الليلة.',
     'I said to the others: we have to do something tonight.'),
    ('لقينا حديد طويل بالقصر وحطيناه بالنار.',
     'We found a long iron rod in the palace and put it in the fire.')),
  P(('لما نام العملاق، قربنا منه بهدوء.',
     'When the giant slept, we came near him quietly.'),
    ('كان صوت نفسه زي الرعد.', 'The sound of his breathing was like thunder.')),
  P(('استعملنا الحديد وهربنا عالشط.', 'We used the iron and fled to the shore.'),
    ('كنا عاملين طوافة من خشب من قبل.',
     'We had made a raft from wood beforehand.'),
    ('دفعناها بالمي ونزلنا فيها.', 'We pushed it into the water and got on it.'))]),

 ('The Serpent and the Board', 'الحية واللوح', [
  P(('العملاق حس فينا وصار يرمي حجار.', 'The giant sensed us and began throwing stones.'),
    ('حجر كبير كسر نص الطوافة.', 'A big stone broke half the raft.'),
    ('ضل معي رفيقين بس.', 'Only two companions were left with me.')),
  P(('وصلنا جزيرة تانية ونمنا من التعب.',
     'We reached another island and slept from exhaustion.'),
    ('بالليل، إجت حية طويلة كتير.', 'At night, a very long snake came.')),
  P(('ربطت حالي بين ألواح خشب عريضة.',
     'I tied myself between wide wooden boards.'),
    ('الحية ما قدرت تفتح تمها عليّ.', 'The snake could not get its mouth around me.'),
    ('الصبح، مرقت سفينة وشافتني.', 'In the morning, a ship passed and saw me.'))]),

 # ---------------- Voyage Four ----------------
 ('The Storm', 'العاصفة', [
  P(('بالرحلة الرابعة، إجت عاصفة قوية.', 'On the fourth voyage, a strong storm came.'),
    ('السفينة انكسرت والناس غرقوا.', 'The ship broke and the men drowned.'),
    ('طلعت عالشط مع كم واحد بس.', 'I got to shore with only a few others.')),
  P(('ناس الجزيرة استقبلونا وأعطونا أكل.',
     'The island’s people received us and gave us food.'),
    ('الأكل كان حلو وكتير وغريب الطعم.',
     'The food was sweet and plentiful and strange in taste.')),
  P(('رفقاتي أكلوا كتير وأنا أكلت شوي.',
     'My companions ate a lot and I ate a little.'),
    ('بعد أيام، صاروا زي المجانين.', 'After days, they became like madmen.'),
    ('ما بقيوا يعرفوا حالهم ولا حكيهم.',
     'They no longer knew themselves or their own speech.'))]),

 ('The King and the Saddle', 'الملك والسرج', [
  P(('هربت لحالي ومشيت سبع أيام.', 'I fled alone and walked seven days.'),
    ('وصلت مدينة فيها ناس عاقلين.', 'I reached a city with sane people.')),
  P(('لاحظت إنهم بيركبوا الخيل بلا سرج.',
     'I noticed they rode horses with no saddle.'),
    ('عملت سرج بإيدي وأعطيته للملك.', 'I made a saddle with my hands and gave it to the king.')),
  P(('الملك ركب عليه وانبسط كتير.', 'The king rode on it and was very pleased.'),
    ('صرت أعمل سروج وصرت غني وقريب منه.',
     'I began making saddles and became rich and close to him.'),
    ('زوجني بنت من عيلة كبيرة.', 'He married me to a woman from a great family.'))]),

 ('The Law of the City', 'قانون المدينة', [
  P(('بعد سنة، مرضت مرتي وماتت.', 'After a year, my wife fell ill and died.'),
    ('إجوا الناس ولبسوني تياب سودا.', 'The people came and dressed me in black clothes.')),
  P(('قالوا لي: عنا قانون قديم.', 'They said to me: we have an old law.'),
    ('لما بيموت واحد، بينزل معه شريكه.',
     'When one dies, their partner goes down with them.')),
  P(('نزلوني بمغارة تحت الأرض.', 'They lowered me into a cave under the ground.'),
    ('أعطوني خبز ومي لكم يوم بس.', 'They gave me bread and water for a few days only.'),
    ('العتمة كانت تقيلة والريحة صعبة.',
     'The darkness was heavy and the smell was hard.'))]),

 ('The Way Out', 'طريق الخروج', [
  P(('مشيت بالعتمة أيام وأنا خايف.', 'I walked in the dark for days, afraid.'),
    ('بيوم، حسيت هوا بارد جاي من بعيد.',
     'One day, I felt cold air coming from far off.')),
  P(('تبعت الهوا لحد ما شفت ضوء زغير.',
     'I followed the air until I saw a small light.'),
    ('كان في فتحة عالبحر من ورا الجبل.',
     'There was an opening to the sea behind the mountain.')),
  P(('طلعت منها وقعدت عالشط أستنى.', 'I came out of it and sat on the shore waiting.'),
    ('بعد كم يوم مرقت سفينة وأخذتني.',
     'After a few days a ship passed and took me.'),
    ('رجعت لبغداد وأنا ما بصدق حالي.',
     'I returned to Baghdad hardly believing myself.'))]),

 # ---------------- Voyage Five ----------------
 ('The Broken Egg', 'البيضة المكسورة', [
  P(('بالرحلة الخامسة، اشتريت سفينة لحالي.',
     'On the fifth voyage, I bought a ship of my own.'),
    ('وقفنا عند جزيرة فيها بيضة رخ كبيرة.',
     'We stopped at an island with a big roc’s egg.')),
  P(('التجار اللي معي كسروا البيضة.', 'The merchants with me broke the egg.'),
    ('قلت لهم لا، بس ما سمعوا مني.', 'I told them no, but they did not listen to me.')),
  P(('إجا الرخ وشاف بيضته.', 'The roc came and saw its egg.'),
    ('طار فوقنا ورمى صخرة ضخمة عالسفينة.',
     'It flew above us and dropped a huge rock on the ship.'),
    ('السفينة انكسرت وأنا طلعت عالشط لحالي.',
     'The ship broke and I got to shore alone.'))]),

 ('The Old Man of the Sea', 'شيخ البحر', [
  P(('لقيت رجل كبير قاعد جنب نهر.', 'I found an old man sitting beside a river.'),
    ('أشر لي إنه بده يعبر عالتاني.', 'He signalled to me that he wanted to cross to the other side.')),
  P(('شلته على كتافي بكل طيبة.', 'I carried him on my shoulders in all kindness.'),
    ('لما عبرنا، ما بده ينزل.', 'When we crossed, he would not get down.'),
    ('لف إجريه على رقبتي وشدها.', 'He wrapped his legs around my neck and squeezed.')),
  P(('ضل على ظهري أيام وأيام.', 'He stayed on my back for days and days.'),
    ('كنت آكل وأنام وهو فوقي.', 'I would eat and sleep with him on top of me.'))]),

 ('The Wine', 'النبيذ', [
  P(('بيوم، مرقنا على شجر عنب.', 'One day, we passed some grapevines.'),
    ('عصرت العنب بقرعة كبيرة وتركتها بالشمس.',
     'I pressed the grapes in a big gourd and left it in the sun.')),
  P(('بعد أيام، شربت منها وارتحت شوي.',
     'After days, I drank from it and felt a little better.'),
    ('الرجل شاف وجهي وبده يشرب كمان.',
     'The man saw my face and wanted to drink too.')),
  P(('شرب كتير ورخيت إجريه.', 'He drank a lot and his legs loosened.'),
    ('وقع عن ظهري وأنا هربت.', 'He fell off my back and I fled.'),
    ('كنت أول واحد يهرب منه.', 'I was the first man to escape him.'))]),

 ('The City of Apes', 'مدينة القرود', [
  P(('وصلت مدينة عالبحر وفيها ناس طيبين.',
     'I reached a city on the sea with kind people.'),
    ('حكوا لي: عنا شغلة غريبة كل يوم.',
     'They told me: we have a strange business every day.')),
  P(('بالمغرب، بيطلعوا عالمراكب ويناموا فيها.',
     'At sunset, they go out to the boats and sleep in them.'),
    ('لأن القرود بتنزل عالمدينة بالليل.',
     'Because the apes come down on the city at night.')),
  P(('صرت أرمي حجار عالقرود وهي ترمي جوز.',
     'I began throwing stones at the apes and they threw nuts.'),
    ('جمعت الجوز وبعته وصرت غني.', 'I gathered the nuts and sold them and became rich.'),
    ('ورجعت لبغداد مرة تانية.', 'And I returned to Baghdad once again.'))]),

 # ---------------- Voyage Six ----------------
 ('The Mountain of Wrecks', 'جبل السفن المكسورة', [
  P(('بالرحلة السادسة، ضاع الريس بالطريق.',
     'On the sixth voyage, the captain lost his way.'),
    ('السفينة راحت على جبل عالي بالبحر.',
     'The ship went onto a high mountain in the sea.')),
  P(('حول الجبل كان في سفن مكسورة كتيرة.',
     'Around the mountain there were many broken ships.'),
    ('وعظام ناس ما رجعوا لبيوتهم.', 'And bones of people who never went home.')),
  P(('كل اللي معي ماتوا بالأيام الأولى.', 'Everyone with me died in the first days.'),
    ('ضلّيت لحالي بين الصخر والبرد.',
     'I was left alone among the rocks and the cold.'))]),

 ('The River Under the Mountain', 'النهر تحت الجبل', [
  P(('لقيت نهر داخل جوا الجبل.', 'I found a river going inside the mountain.'),
    ('ما كنت بعرف على وين بيوصل.', 'I did not know where it led.')),
  P(('عملت طوافة من خشب السفن المكسورة.',
     'I made a raft from the wood of the broken ships.'),
    ('حطيت عليها ألماس وعنبر من الجبل.',
     'I put diamonds and ambergris from the mountain on it.')),
  P(('قلت لحالي: يا بموت هون، يا بوصل.',
     'I said to myself: either I die here, or I arrive.'),
    ('دفعت الطوافة بالنهر وفتت بالعتمة.',
     'I pushed the raft into the river and entered the darkness.'))]),

 ('Serendib', 'سرنديب', [
  P(('نمت من التعب وأنا عالطوافة.', 'I slept from exhaustion on the raft.'),
    ('لما صحيت، كانت الشمس على وجهي.', 'When I woke, the sun was on my face.'),
    ('ناس واقفين حولي وبيحكوا لغة ما بعرفها.',
     'People were standing around me speaking a language I did not know.')),
  P(('كنت وصلت جزيرة اسمها سرنديب.', 'I had reached an island called Serendib.'),
    ('جبالها عالية وفيها كل أنواع الشجر.',
     'Its mountains are high and it has every kind of tree.')),
  P(('أخذوني عند ملكهم وحكيت له كل إشي.',
     'They took me to their king and I told him everything.'),
    ('ما صدق إني عبرت الجبل بالنهر.',
     'He could not believe I had crossed the mountain by the river.'))]),

 ('The King’s Letter', 'مكتوب الملك', [
  P(('الملك سألني عن بغداد وعن الخليفة.',
     'The king asked me about Baghdad and about the caliph.'),
    ('حكيت له عن المدينة وعن سوقها.',
     'I told him about the city and its market.')),
  P(('قال لي: بدي أبعت مكتوب وهدية.',
     'He said to me: I want to send a letter and a gift.'),
    ('وإنت اللي رح توصلها.', 'And you are the one who will deliver them.')),
  P(('أعطاني مكتوب مكتوب على جلد غالي.',
     'He gave me a letter written on costly leather.'),
    ('رجعت لبغداد ووصلت المكتوب بإيدي.',
     'I returned to Baghdad and delivered the letter with my own hand.'),
    ('الخليفة سمع قصتي وضحك من العجب.',
     'The caliph heard my story and laughed in wonder.'))]),

 # ---------------- Voyage Seven ----------------
 ('One Last Time', 'آخر مرة', [
  P(('قلت لحالي: خلص، ما بسافر بعد.',
     'I said to myself: enough, I will not travel again.'),
    ('بس الخليفة طلب مني أروح لسرنديب.',
     'But the caliph asked me to go to Serendib.'),
    ('ما قدرت أرفض طلب الخليفة.', 'I could not refuse the caliph’s request.')),
  P(('وصلت وسلمت الهدية وارتحت شوي.',
     'I arrived and delivered the gift and rested a little.'),
    ('وبالرجعة، هاجمونا حرامية البحر.',
     'And on the way back, sea robbers attacked us.')),
  P(('باعوني كعبد بمدينة بعيدة.', 'They sold me as a slave in a far city.'),
    ('اشتراني تاجر طيب وسألني: شو بتعرف تعمل؟',
     'A kind merchant bought me and asked: what do you know how to do?'))]),

 ('The Elephants', 'الفيلة', [
  P(('قلت له: بعرف أرمي بالقوس.', 'I said to him: I know how to shoot with a bow.'),
    ('قال: طيب، تعال معي عالغابة.', 'He said: good, come with me to the forest.')),
  P(('كل ليلة كنت أطلع على شجرة عالية.',
     'Every night I would climb a tall tree.'),
    ('وأرمي فيل لأجل العاج.', 'And shoot an elephant for its ivory.')),
  P(('عملت هيك شهرين وأنا مش مرتاح.',
     'I did this for two months and I was not at ease.'),
    ('كنت بحس إني عم أعمل غلط.', 'I felt I was doing something wrong.'))]),

 ('The Elephant Who Carried Me', 'الفيل اللي شالني', [
  P(('بليلة، إجا فيل كبير عالشجرة.', 'One night, a big elephant came to the tree.'),
    ('لفها بخرطومه وقلعها من الأرض.',
     'It wrapped its trunk around it and pulled it from the ground.'),
    ('وقعت وأنا متأكد إني رح أموت.',
     'I fell, certain that I was going to die.')),
  P(('بس الفيل شالني بهدوء على ظهره.',
     'But the elephant lifted me gently onto its back.'),
    ('مشى فيني ساعات لمحل بعيد.', 'It walked with me for hours to a far place.')),
  P(('حطني عالأرض وراح.', 'It put me on the ground and left.'),
    ('كنت واقف بوسط عظام فيلة كتيرة.',
     'I was standing in the middle of many elephants’ bones.'),
    ('فهمت: هاد المحل اللي بيموتوا فيه.',
     'I understood: this is the place where they die.'))]),

 ('The Last Return', 'الرجعة الأخيرة', [
  P(('رجعت للتاجر وحكيت له كل إشي.',
     'I went back to the merchant and told him everything.'),
    ('راح معي وشاف العاج بعينه.', 'He came with me and saw the ivory with his own eyes.')),
  P(('قال لي: إنت حر من اليوم.', 'He said to me: you are free from today.'),
    ('والفيلة أعطتك اللي ما بيعطيه حدا.',
     'And the elephants gave you what no one else gives.')),
  P(('رجعت لبغداد ومعي مصاري كتيرة.',
     'I returned to Baghdad with a great deal of money.'),
    ('ومن يومها ما ركبت البحر.', 'And from that day I never went to sea again.')),
  P(('التفت السندباد عالحمّال وقال:',
     'Sindbad turned to the porter and said:'),
    ('شفت؟ كل قرش عندي إله قصة.',
     'You see? Every coin I have has a story behind it.'),
    ('والحمّال قال: وأنا بكتفي بخبزي.',
     'And the porter said: and I am content with my bread.'))]),
]

if __name__ == '__main__':
    emit_book(BOOK_ID, BOOK_TITLE, 'intermediate', CHAPTERS, shelf=11,
              meta={'work': 'The Seven Voyages of Sindbad, from ألف ليلة وليلة',
                    'author': 'traditional', 'year': 'medieval',
                    'status': 'public domain — medieval, anonymous'})
