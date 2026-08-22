#!/usr/bin/env python3
"""جزيرة الكنز — Treasure Island, retold in spoken Palestinian, graded to intermediate.

Robert Louis Stevenson died in 1894; the novel (1883) is public domain. This is a retelling from
the plot, not a translation of any edition.

WHY IT EARNS A PLACE. It is told in the FIRST PERSON by a boy roughly the age of a beginner's
confidence, and that is worth a lot pedagogically: شفت، كنت، خفت، ما عرفت. A learner reading
Sindbad or Kalila is reading about people; reading Jim, they are rehearsing the forms they will
actually use to tell their own day. It is also the most plot-driven book on the shelf — the
chapter endings pull, which is what gets someone to read thirty of them.

LEVEL. Written near the intermediate story baseline (32.5 characters a sentence), like Sindbad and
Kalila. Past-tense first-person narration with real connectors, dialogue carrying the tension, one
clause at a time.

A NOTE ON THE VILLAIN. Silver is not simplified into a monster. Half of what makes the book work
is that Jim likes him and cannot stop liking him, and that reads at B1 as easily as it does in
English — the ambivalence is in what people say, not in complicated syntax.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated), but
every WORD's root, meaning and pronunciation is looked up in Maknuune by the ingest pipeline.

Run:  python3 pipeline/book_treasure.py    then ingest each chapter + build_app.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bookshelf import P, emit_book

BOOK_ID = 'treasure'
BOOK_TITLE = {'en': 'Treasure Island', 'ar': 'جزيرة الكنز'}

# (english title, arabic title, [paragraph, ...])
CHAPTERS = [
 ('The Old Sea-Dog', 'البحري العجوز', [
  P(('أهلي كان عندهم نزل صغير عالبحر.', 'My family had a small inn by the sea.'),
    ('اسمي جيم، وكنت ولد وقتها.', 'My name is Jim, and I was a boy then.')),
  P(('بيوم، إجا رجل كبير وسكن عندنا.', 'One day, an old man came and stayed with us.'),
    ('وجهه فيه ندبة كبيرة وشعره أبيض.',
     'His face had a big scar and his hair was white.'),
    ('كان يشرب كتير ويغني أغاني بحارة.',
     'He drank a lot and sang sailors’ songs.')),
  P(('أعطاني مصاري وقال: راقب الطريق.',
     'He gave me money and said: watch the road.'),
    ('إذا شفت بحري بإجر وحدة، قول لي.',
     'If you see a sailor with one leg, tell me.'),
    ('من يومها صرت أحلم فيه بالليل.',
     'From that day I dreamed of him at night.'))]),

 ('Black Dog', 'الكلب الأسود', [
  P(('بيوم شتوي، إجا زلمة شاحب عالنزل.',
     'On a winter day, a pale man came to the inn.'),
    ('ناقص منه إصبعين من إيده.', 'Two fingers were missing from his hand.')),
  P(('سأل عن البحري العجوز وقعد يستنى.',
     'He asked about the old sailor and sat waiting.'),
    ('لما دخل العجوز، وقف وجهه.', 'When the old man came in, his face froze.')),
  P(('حكوا شوي وبعدين صار صوت وسيوف.',
     'They talked a little and then there was noise and swords.'),
    ('الزلمة هرب وهو بينزف من كتفه.',
     'The man fled bleeding from his shoulder.'),
    ('العجوز وقع عالأرض من التعب.',
     'The old man fell to the floor from exhaustion.'))]),

 ('The Black Spot', 'النقطة السودا', [
  P(('الدكتور ليفزي إجا وقال له: بطل شرب.',
     'Doctor Livesey came and told him: stop drinking.'),
    ('العجوز ما سمع الكلام.', 'The old man did not listen.')),
  P(('بعد أيام، إجا أعمى بعصاية.', 'After days, a blind man came with a stick.'),
    ('حط ورقة بإيد العجوز وراح.',
     'He put a paper in the old man’s hand and left.')),
  P(('العجوز فتح الورقة وشاف نقطة سودا.',
     'The old man opened the paper and saw a black spot.'),
    ('قال: عندي لحد الليل.', 'He said: I have until tonight.'),
    ('وبعد شوي وقع وما قام.', 'And a little later he fell and did not get up.'))]),

 ('The Sea Chest', 'صندوق البحر', [
  P(('أنا وأمي فتحنا صندوقه.', 'My mother and I opened his chest.'),
    ('لأنه كان مديون لنا مصاري.', 'Because he owed us money.')),
  P(('لقينا تياب وسلاح وكيس مصاري.',
     'We found clothes and a weapon and a bag of money.'),
    ('وتحت كل إشي، لقينا ورق مربوط.',
     'And under everything, we found tied papers.')),
  P(('أمي كانت تعد المصاري بالضوء.',
     'My mother was counting the money by the light.'),
    ('سمعنا صوت عصاية عالطريق.', 'We heard the sound of a stick on the road.'),
    ('أخذت الورق وهربنا من الباب الخلفي.',
     'I took the papers and we fled from the back door.'))]),

 ('The Blind Man', 'الأعمى', [
  P(('خبينا حالنا تحت جسر صغير.', 'We hid ourselves under a small bridge.'),
    ('أمي أغمى عليها من الخوف.', 'My mother fainted from fear.')),
  P(('سمعنا ناس كتار بيكسروا بالنزل.',
     'We heard many men breaking into the inn.'),
    ('كانوا يدوروا على الورق اللي معي.',
     'They were looking for the papers I had.')),
  P(('إجا خيالة من البلد بسرعة.', 'Horsemen from the town came quickly.'),
    ('الحرامية هربوا والأعمى ما قدر.',
     'The robbers fled and the blind man could not.'),
    ('وقع تحت الخيل ومات بالطريق.',
     'He fell under the horses and died on the road.'))]),

 ('The Captain’s Papers', 'أوراق الكابتن', [
  P(('رحت عند الدكتور ليفزي بالورق.',
     'I went to Doctor Livesey with the papers.'),
    ('كان قاعد مع السيد تريلوني.', 'He was sitting with Squire Trelawney.')),
  P(('فتحوا الورق ولقوا خريطة جزيرة.',
     'They opened the papers and found a map of an island.'),
    ('عليها إشارة حمرا وكلمة: الكنز هون.',
     'On it was a red mark and a word: the treasure is here.')),
  P(('تريلوني قال: بشتري سفينة وبنروح.',
     'Trelawney said: I will buy a ship and we will go.'),
    ('الدكتور قال: بس لا تحكي مع حدا.',
     'The doctor said: only, do not speak to anyone.'),
    ('وهاي بالزبط الشغلة اللي ما عملها.',
     'And that is exactly the thing he did not do.'))]),

 ('To Bristol', 'على بريستول', [
  P(('بعد شهور، وصلني مكتوب من تريلوني.',
     'After months, a letter reached me from Trelawney.'),
    ('كتب: السفينة جاهزة، تعال بسرعة.',
     'He wrote: the ship is ready, come quickly.')),
  P(('ودعت أمي وأنا حزين ومبسوط بنفس الوقت.',
     'I said goodbye to my mother, sad and happy at once.'),
    ('كانت أول مرة بطلع من البلد.',
     'It was the first time I had left the town.')),
  P(('بريستول كانت مليانة سفن وبحارة.',
     'Bristol was full of ships and sailors.'),
    ('وقفت عالميناء وأنا ما بصدق.',
     'I stood at the harbour hardly believing it.'))]),

 ('The Sign of the Spy-glass', 'دكان جون سيلفر', [
  P(('تريلوني بعتني عند طباخ السفينة.',
     'Trelawney sent me to the ship’s cook.'),
    ('اسمه جون سيلفر وعنده دكان صغير.',
     'His name was John Silver and he had a small shop.')),
  P(('لما فتّ، شفته وقف على إجر وحدة.',
     'When I went in, I saw him standing on one leg.'),
    ('تذكرت كلام البحري العجوز وبردت.',
     'I remembered the old sailor’s words and went cold.')),
  P(('بس سيلفر ضحك وحكى معي بلطف.',
     'But Silver laughed and spoke to me kindly.'),
    ('بعد ساعة، كنت بحبه.', 'After an hour, I liked him.'),
    ('وهاي كانت أول غلطة مني.', 'And that was my first mistake.'))]),

 ('Powder and Arms', 'البارود والسلاح', [
  P(('الكابتن سمولت ما كان مبسوط.', 'Captain Smollett was not pleased.'),
    ('قال للسيد تريلوني: كل البحارة بيعرفوا عن الكنز.',
     'He said to Squire Trelawney: all the sailors know about the treasure.')),
  P(('قال: ما بحب هالرحلة ولا هالطاقم.',
     'He said: I do not like this voyage nor this crew.'),
    ('طلب ينقلوا البارود والسلاح لمحل قريب منهم.',
     'He asked that the powder and arms be moved near them.')),
  P(('تريلوني زعل بس وافق.', 'Trelawney was annoyed but agreed.'),
    ('وأنا وقتها حسبت الكابتن رجل صعب.',
     'And I at the time thought the captain a difficult man.'),
    ('طلع إنه كان الوحيد اللي فاهم.',
     'It turned out he was the only one who understood.'))]),

 ('The Voyage', 'الرحلة', [
  P(('طلعنا بالبحر والريح كانت منيحة.',
     'We set out to sea and the wind was good.'),
    ('السفينة اسمها هيسبانيولا.', 'The ship was called the Hispaniola.')),
  P(('سيلفر كان محبوب من كل البحارة.',
     'Silver was loved by all the sailors.'),
    ('كان عنده ببغاء بيقول: قطع ذهب!',
     'He had a parrot that said: pieces of eight!')),
  P(('كان يقول إن الببغاء عمرها ميتين سنة.',
     'He used to say the parrot was two hundred years old.'),
    ('وإنها شافت أشياء ما بتنحكى.',
     'And that it had seen things that cannot be told.'))]),

 ('What I Heard in the Apple Barrel', 'اللي سمعته بالبرميل', [
  P(('بليلة هادية، بدي آكل تفاحة.', 'On a quiet night, I wanted an apple.'),
    ('نزلت جوا برميل التفاح ونمت شوي.',
     'I climbed inside the apple barrel and slept a little.')),
  P(('صحيت على صوت سيلفر جنب البرميل.',
     'I woke to Silver’s voice beside the barrel.'),
    ('كان يحكي مع بحري شاب.', 'He was talking with a young sailor.')),
  P(('قال: لما نلاقي الكنز، بنقتلهم كلهم.',
     'He said: when we find the treasure, we kill them all.'),
    ('ضلّيت ساكت وأنا ما بقدر أتنفس.',
     'I stayed silent, unable to breathe.'),
    ('كنت بحبه، وهلق صرت بخاف منه.',
     'I had liked him, and now I feared him.'))]),

 ('Council of War', 'مجلس الحرب', [
  P(('لما راحوا، طلعت من البرميل.', 'When they left, I got out of the barrel.'),
    ('رحت عالكابتن والدكتور وتريلوني.',
     'I went to the captain, the doctor and Trelawney.')),
  P(('حكيت لهم كل إشي سمعته.', 'I told them everything I had heard.'),
    ('الكابتن قال: منيح إنك سمعت.',
     'The captain said: it is good that you heard.')),
  P(('عدينا الناس: احنا سبعة وهم تسعتعش.',
     'We counted the men: we were seven and they nineteen.'),
    ('قال الكابتن: بنستنى وما بنبين إشي.',
     'The captain said: we wait and we show nothing.'))]),

 ('The Island', 'الجزيرة', [
  P(('الصبح، شفنا الجزيرة من بعيد.', 'In the morning, we saw the island from afar.'),
    ('كانت رمادية وفيها تلات جبال.',
     'It was grey and had three hills.')),
  P(('البحارة صاروا يحكوا بصوت واطي.',
     'The sailors began speaking in low voices.'),
    ('الجو عالسفينة صار تقيل.', 'The mood on the ship became heavy.')),
  P(('سيلفر حكى عن الجزيرة كإنه بيعرفها.',
     'Silver spoke about the island as though he knew it.'),
    ('وقال إنه اشتغل مع القبطان فلينت زمان.',
     'And he said he had worked with Captain Flint long ago.'))]),

 ('Ashore', 'عالشط', [
  P(('نص البحارة نزلوا عالشط.', 'Half the sailors went ashore.'),
    ('وأنا نزلت معهم بلا ما حدا يشوفني.',
     'And I went down with them without anyone seeing me.')),
  P(('ركضت لجوا الجزيرة وخبيت حالي.',
     'I ran inland and hid myself.'),
    ('سمعت صوت سيلفر بيحكي مع بحري.',
     'I heard Silver’s voice talking with a sailor.')),
  P(('البحري رفض ينضم لهم.', 'The sailor refused to join them.'),
    ('سيلفر قتله بضربة وحدة.', 'Silver killed him with one blow.'),
    ('ركضت وأنا ما بشوف قدامي.',
     'I ran without seeing in front of me.'))]),

 ('The Man of the Island', 'رجل الجزيرة', [
  P(('وأنا هارب، شفت إشي بيتحرك بين الشجر.',
     'While fleeing, I saw something moving among the trees.'),
    ('طلع زلمة شعره طويل وتيابه من جلد.',
     'It was a man with long hair and clothes of skin.')),
  P(('قال: أنا بن غن، من تلات سنين هون.',
     'He said: I am Ben Gunn, three years here.'),
    ('تركوني البحارة على هالجزيرة لحالي.',
     'The sailors left me on this island alone.')),
  P(('سألني: عندك جبنة؟', 'He asked me: do you have cheese?'),
    ('وقال: أنا بعرف كل إشي عن فلينت.',
     'And he said: I know everything about Flint.'),
    ('وعنده مركب صغير مخبى.', 'And he had a small boat hidden.'))]),

 ('The Ship Abandoned', 'السفينة المتروكة', [
  P(('بنفس الوقت، الدكتور كان عالسفينة.',
     'At the same time, the doctor was on the ship.'),
    ('حس إن الوضع صار خطر.', 'He felt the situation had become dangerous.')),
  P(('نزل عالشط وشاف بيت خشب قديم.',
     'He went ashore and saw an old wooden house.'),
    ('كان محاط بسور، وقالوا عليه القلعة.',
     'It was surrounded by a fence, and they called it the stockade.')),
  P(('رجع وقال: منترك السفينة ومنروح لهناك.',
     'He returned and said: we leave the ship and go there.'),
    ('نقلوا أكل وسلاح بمركب صغير.',
     'They moved food and weapons in a small boat.'))]),

 ('The Last Boat', 'آخر مركب', [
  P(('آخر مركب كان محمل كتير.', 'The last boat was heavily loaded.'),
    ('البحارة شافوهم وصاروا يرموا عليهم.',
     'The sailors saw them and began firing at them.')),
  P(('المركب غرق قريب من الشط.',
     'The boat sank close to the shore.'),
    ('نزلوا بالمي ووصلوا وهم مبلولين.',
     'They went into the water and arrived soaked.')),
  P(('واحد منهم انجرح بكتفه.', 'One of them was wounded in the shoulder.'),
    ('وصلوا عالقلعة بالكاد.', 'They barely reached the stockade.'))]),

 ('The First Day’s Fighting', 'أول يوم قتال', [
  P(('أنا وبن غن كنا نتفرج من بعيد.',
     'Ben Gunn and I were watching from afar.'),
    ('شفت العلم البريطاني فوق القلعة.',
     'I saw the British flag above the stockade.')),
  P(('عرفت إن أصحابي وصلوا لهناك.',
     'I knew my friends had reached there.'),
    ('ركضت لعندهم بالليل ودقيت عالباب.',
     'I ran to them at night and knocked at the door.')),
  P(('الدكتور فتح لي وقال: جيم!', 'The doctor opened for me and said: Jim!'),
    ('كانوا حاسبيني ميت.', 'They had thought me dead.'))]),

 ('The Garrison in the Stockade', 'الحامية بالقلعة', [
  P(('قعدنا نحرس عالدور طول الليل.',
     'We sat guarding in turns all night.'),
    ('الأكل كان قليل والمي أقل.',
     'The food was little and the water less.')),
  P(('الكابتن كتب كل إشي بدفتر.',
     'The captain wrote everything in a notebook.'),
    ('عد الأيام وعد الرصاص.', 'He counted the days and counted the bullets.')),
  P(('حكيت لهم عن بن غن ومركبه.',
     'I told them about Ben Gunn and his boat.'),
    ('الدكتور سمع وما قال إشي.',
     'The doctor listened and said nothing.'),
    ('بس شفت بعينه إنه فكر بإشي.',
     'But I saw in his eye that he had thought of something.'))]),

 ('Silver’s Embassy', 'سيلفر بيجي يحكي', [
  P(('الصبح، إجا سيلفر لحاله بعلم أبيض.',
     'In the morning, Silver came alone with a white flag.'),
    ('وقف قدام السور وطلب يحكي.',
     'He stood before the fence and asked to talk.')),
  P(('قال: أعطونا الخريطة وبنترككم تروحوا.',
     'He said: give us the map and we let you go.'),
    ('الكابتن قال: لأ.', 'The captain said: no.')),
  P(('سيلفر زعل وقام بصعوبة.', 'Silver grew angry and rose with difficulty.'),
    ('قال: قبل الظهر رح تشوفوا.', 'He said: before noon you will see.'),
    ('ومشي وهو بيسند على عكازه.',
     'And he walked away leaning on his crutch.'))]),

 ('The Attack', 'الهجوم', [
  P(('بعد ساعة، هجموا من كل الجهات.',
     'An hour later, they attacked from every side.'),
    ('طلعوا عالسور وفاتوا عالساحة.',
     'They came over the fence and into the yard.')),
  P(('صار قتال قريب وصعب.', 'There was close, hard fighting.'),
    ('الكابتن انجرح بكتفه.', 'The captain was wounded in the shoulder.')),
  P(('بالآخر هربوا وتركوا قتلاهم.',
     'In the end they fled and left their dead.'),
    ('ربحنا، بس خسرنا اتنين مننا.',
     'We won, but we lost two of us.'))]),

 ('I Slip Away', 'بهرب لحالي', [
  P(('بعد الضهر، الكل نام من التعب.',
     'In the afternoon, everyone slept from exhaustion.'),
    ('أنا ما قدرت أنام وفكرت بفكرة.',
     'I could not sleep and thought of an idea.')),
  P(('أخذت مسدسين وأكل وطلعت بالسر.',
     'I took two pistols and food and went out secretly.'),
    ('ما حكيت لحدا، وهاي كانت غلطة.',
     'I told no one, and that was a mistake.')),
  P(('لقيت مركب بن غن تحت الشجر.',
     'I found Ben Gunn’s boat under the trees.'),
    ('كان صغير كتير وخفيف.', 'It was very small and light.'))]),

 ('The Ebb-Tide Runs', 'الجزر بيسحب', [
  P(('نزلت بالمركب بالليل عالمي.',
     'I went out in the boat at night on the water.'),
    ('كان القمر مخبى ورا غيمة.', 'The moon was hidden behind a cloud.')),
  P(('وصلت للسفينة وقصيت حبل المرساة.',
     'I reached the ship and cut the anchor rope.'),
    ('الجزر بلش يسحب السفينة عالبحر.',
     'The ebb tide began pulling the ship out to sea.')),
  P(('سمعت صوتين بيتخانقوا جوا.',
     'I heard two voices quarrelling inside.'),
    ('وبعدين صار سكوت.', 'And then there was silence.'))]),

 ('The Cruise of the Coracle', 'رحلة المركب الصغير', [
  P(('الموج رماني بعيد عن الشط.',
     'The waves threw me far from the shore.'),
    ('المركب كان يدور معي بلا اتجاه.',
     'The boat spun with me in no direction.')),
  P(('نمت من التعب وأنا مبلول.',
     'I slept from exhaustion, soaked.'),
    ('لما صحيت، الشمس كانت عالية.',
     'When I woke, the sun was high.')),
  P(('شفت الهيسبانيولا قريبة مني.',
     'I saw the Hispaniola close to me.'),
    ('كانت تمشي غريب، زي ما في حدا يقودها.',
     'She was moving strangely, as if nobody were steering her.'))]),

 ('I Strike the Jolly Roger', 'بنزل علم القراصنة', [
  P(('طلعت عالسفينة من الحبل.',
     'I climbed onto the ship by the rope.'),
    ('عالسطح لقيت اتنين، واحد ميت.',
     'On the deck I found two men, one dead.')),
  P(('التاني اسمه إسرائيل هاندز ومجروح.',
     'The other was named Israel Hands and was wounded.'),
    ('قال لي: جيب لي نبيذ وبساعدك.',
     'He said to me: bring me wine and I will help you.')),
  P(('نزلت علم القراصنة الأسود.',
     'I took down the black pirate flag.'),
    ('قلت له: أنا هلق كابتن هالسفينة.',
     'I said to him: I am now the captain of this ship.'))]),

 ('Israel Hands', 'إسرائيل هاندز', [
  P(('اتفقنا نوصل السفينة لخليج آمن.',
     'We agreed to bring the ship to a safe bay.'),
    ('كان يعلمني كيف أمسك الدفة.',
     'He was teaching me how to hold the tiller.')),
  P(('بس شفته يأخذ سكينة ويخبيها.',
     'But I saw him take a knife and hide it.'),
    ('عملت حالي ما شفت إشي.', 'I pretended I had seen nothing.')),
  P(('لما وصلنا، هجم عليّ فجأة.',
     'When we arrived, he attacked me suddenly.'),
    ('طلعت عالصاري وهو ورايي.',
     'I climbed the mast with him behind me.'),
    ('رمى السكينة وجرح كتفي، بس وقع بالمي.',
     'He threw the knife and cut my shoulder, but he fell in the water.'))]),

 ('Pieces of Eight', 'قطع الذهب', [
  P(('نزلت عالشط وأنا فرحان بحالي.',
     'I went ashore pleased with myself.'),
    ('السفينة صارت عندنا وهم ما بيعرفوا.',
     'The ship was ours and they did not know.')),
  P(('مشيت عالقلعة بالعتمة.', 'I walked to the stockade in the dark.'),
    ('فتّ من السور وأنا ساكت.',
     'I came through the fence quietly.')),
  P(('سمعت صوت بالعتمة: قطع ذهب! قطع ذهب!',
     'I heard a voice in the dark: pieces of eight! pieces of eight!'),
    ('كانت ببغاء سيلفر.', 'It was Silver’s parrot.'),
    ('القلعة كانت صارت إلهم.', 'The stockade had become theirs.'))]),

 ('In the Enemy’s Camp', 'بمعسكر العدو', [
  P(('صحيوا كلهم وأنا واقف بينهم.',
     'They all woke and I was standing among them.'),
    ('سيلفر ضحك وقال: جيم هوكنز!',
     'Silver laughed and said: Jim Hawkins!')),
  P(('البحارة بدهم يقتلوني بسرعة.',
     'The sailors wanted to kill me at once.'),
    ('سيلفر وقف قدامي وقال: مين بده يوصله؟',
     'Silver stood in front of me and said: who wants to reach him?')),
  P(('ما فهمت ليش حماني.', 'I did not understand why he protected me.'),
    ('وبعدها بسنين، لسا ما فهمت.',
     'And years later, I still did not understand.'))]),

 ('The Black Spot Again', 'النقطة السودا كمان مرة', [
  P(('البحارة طلعوا برا وحكوا مع بعض.',
     'The sailors went outside and talked together.'),
    ('رجعوا وأعطوا سيلفر ورقة.',
     'They came back and gave Silver a paper.')),
  P(('عليها نقطة سودا، زي اللي شفتها زمان.',
     'On it was a black spot, like the one I had seen long ago.'),
    ('سيلفر تطلع فيها وضحك.', 'Silver looked at it and laughed.')),
  P(('طلّع الخريطة من جيبه ورماها لهم.',
     'He took the map from his pocket and threw it to them.'),
    ('صاروا يصرخوا من الفرح.', 'They began shouting with joy.'),
    ('وأنا كنت بعرف إشي هم ما بيعرفوه.',
     'And I knew something they did not know.'))]),

 ('The Treasure Hunt', 'البحث عن الكنز', [
  P(('الصبح، مشينا كلنا عالجبل.',
     'In the morning, we all walked to the hill.'),
    ('سيلفر ربطني بحبل ومسكه بإيده.',
     'Silver tied me with a rope and held it in his hand.')),
  P(('وصلنا عالمحل اللي عالخريطة.',
     'We reached the place marked on the map.'),
    ('لقينا حفرة كبيرة وفاضية.',
     'We found a big hole, and it was empty.'),
    ('البحارة وقفوا ساكتين، وبعدين غضبوا.',
     'The sailors stood silent, and then they were furious.')),
  P(('وقتها إجا رصاص من بين الشجر.',
     'Then shots came from among the trees.'),
    ('كان الدكتور وبن غن وأصحابنا.',
     'It was the doctor and Ben Gunn and our friends.'),
    ('بن غن كان لقى الكنز من زمان ونقله.',
     'Ben Gunn had found the treasure long ago and moved it.')),
  P(('رجعنا عالسفينة ومعنا الذهب.',
     'We went back to the ship with the gold.'),
    ('سيلفر هرب بالليل ومعه كيس مصاري.',
     'Silver escaped at night with a bag of money.'),
    ('وأنا لحد اليوم بحلم بصوت الببغاء.',
     'And to this day I dream of the parrot’s voice.'))]),
]

if __name__ == '__main__':
    emit_book(BOOK_ID, BOOK_TITLE, 'intermediate', CHAPTERS, shelf=13,
              meta={'work': 'Treasure Island', 'author': 'Robert Louis Stevenson',
                    'year': '1883', 'status': 'public domain'})
