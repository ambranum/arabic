#!/usr/bin/env python3
"""Around the World in 80 Days — a full, graded retelling in spoken Palestinian Arabic.

Jules Verne's novel is public domain. This is a complete chapter-by-chapter retelling for
learners — the prose is written by Claude (NOT native-validated, flagged as such), graded to
roughly "intermediate" level. As everywhere in this project, the sentences are generated but every
WORD's metadata is looked up in Maknuune by the ingest pipeline — nothing about the words is invented.

Content is organized in PARAGRAPHS: each chapter is a list of paragraphs, each paragraph a list of
(arabic, english) sentence pairs. On emit, every sentence gets a `p` (paragraph index) so the reader
and the PDF can lay the book out as flowing bilingual paragraphs instead of one line at a time.

Emits one text per chapter: texts/book-atw80-chNN.json (kind "book-chapter", grouped by book "atw80").
Run:  python3 pipeline/book_atw80.py    then ingest each chapter + build_app.py.
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BOOK_ID = 'atw80'
BOOK_TITLE = {'en': 'Around the World in 80 Days', 'ar': 'حول العالم في ثمانين يوم'}

# (english title, arabic title, [ paragraph, ... ]) where paragraph = [ (arabic, english), ... ]
CHAPTERS = [
 ('A Precise Man', 'رجل دقيق', [
  [('بلندن، بحي هادي، كان في رجل اسمه فيلياس فوغ.', 'In London, in a quiet neighborhood, there was a man named Phileas Fogg.'),
   ('كان رجل غني ومحترم، بس محدا كان يعرف عنه إشي كتير.', 'He was a rich and respectable man, but nobody knew much about him.'),
   ('ما كان له عيلة ولا أصحاب كتار، وكان يعيش لحاله بهدوء.', "He had no family and not many friends, and he lived alone, quietly."),
   ('أهم إشي بحياته كان الوقت والدقة.', 'The most important thing in his life was time and precision.')],
  [('كل يوم كان يعمل نفس الأشيا بنفس الساعة بالزبط.', 'Every day he did the same things at exactly the same times.'),
   ('كان يفطر، ويقرا الجرايد، ويروح على ناديه.', 'He would eat breakfast, read the newspapers, and go to his club.'),
   ('بالنادي كان يغدّى، يلعب الورق، ويرجع عالبيت بالليل.', 'At the club he would have lunch, play cards, and return home at night.'),
   ('حياته كانت زي الساعة، ما فيها ولا مفاجأة.', 'His life was like a clock, without a single surprise.')],
 ]),
 ('The Great Bet', 'الرهان الكبير', [
  [('بيوم من الأيام، كان فوغ قاعد بالنادي مع كم واحد من أصحابه.', 'One day, Fogg was sitting at the club with a few of his friends.'),
   ('صاروا يحكوا عن خبر بالجريدة عن سرقة كبيرة من البنك.', 'They started talking about a story in the paper about a big bank robbery.'),
   ('وبعدين صار الحكي عن الدنيا وقديش صارت أسهل للسفر.', 'And then the talk turned to the world and how much easier it had become to travel.'),
   ('قال فوغ بهدوء: هلق بقدر الواحد يلف الأرض كلها بثمانين يوم بس.', 'Fogg said calmly: now a person can go around the whole earth in just eighty days.')],
  [('ضحكوا أصحابه، وقالوا هاد إشي مستحيل.', "His friends laughed and said this was impossible."),
   ('قال لهم فوغ: أنا مستعد أراهن على عشرين ألف جنيه إني بقدر أعملها.', "Fogg told them: I'm ready to bet twenty thousand pounds that I can do it."),
   ('انصدموا، بس وافقوا على الرهان.', 'They were shocked, but they agreed to the bet.'),
   ('قال فوغ: القطار لباريس بيطلع الليلة الساعة تمانية وربع، وأنا رح أكون فيه.', "Fogg said: the train to Paris leaves tonight at a quarter past eight, and I'll be on it."),
   ('لازم يرجع لنفس النادي بعد ثمانين يوم بالزبط، مش أكتر ولا دقيقة.', 'He had to return to this same club after exactly eighty days, not one minute more.')],
 ]),
 ('A New Servant', 'خادم جديد', [
  [('بنفس الصبح، كان فوغ لسا هلق استأجر خادم جديد.', 'That very morning, Fogg had only just hired a new servant.'),
   ('الخادم اسمه باسبارتو، وكان رجل فرنسي طيّب ومرح.', "The servant's name was Passepartout, and he was a good-natured, cheerful Frenchman."),
   ('كان قبل هيك اشتغل بشغلات كتيرة، وهلق بدّه حياة هادية ومرتبة.', 'He had worked many jobs before, and now he wanted a calm, orderly life.'),
   ('لما شاف بيت فوغ المرتب والهادي، فرح وقال: هاد بالزبط الي بدّي إياه.', "When he saw Fogg's neat, quiet house, he was glad and said: this is exactly what I want.")],
  [('بس بنفس الليلة، إجا فوغ وقال له: يلا، رح نسافر حول العالم.', "But that very night, Fogg came and said: let's go, we're going to travel around the world."),
   ('باسبارتو ما صدق حاله، وانصدم كتير.', "Passepartout couldn't believe it, and was very shocked."),
   ('ما كان معهم غير شنطة صغيرة فيها شوية أواعي ومصاري كتيرة.', 'They took only a small bag with a few clothes and a lot of money.'),
   ('وهيك، بدل الحياة الهادية، لقى باسبارتو حاله مسافر عالدنيا كلها.', 'And so, instead of the quiet life, Passepartout found himself traveling across the whole world.')],
 ]),
 ('Departure from London', 'الانطلاق من لندن', [
  [('طلعوا من البيت وراحوا عالمحطة بسرعة.', 'They left the house and went to the station quickly.'),
   ('ركبوا القطار الساعة تمانية وربع بالزبط، متل ما قال فوغ.', 'They boarded the train at exactly a quarter past eight, just as Fogg had said.'),
   ('فوغ كان هادي، قاعد بمكانه وما عليه ولا هم.', "Fogg was calm, sitting in his seat without a worry."),
   ('أما باسبارتو، فكان قلبه بيدق من الخوف والفرحة بنفس الوقت.', 'But Passepartout, his heart was pounding from fear and joy at the same time.')],
  [('عبروا فرنسا بالقطار، وبعدين ركبوا مركب باتجاه مصر.', 'They crossed France by train, and then boarded a ship toward Egypt.'),
   ('فوغ كتب كل محطة وكل يوم بدفتره الصغير.', 'Fogg wrote down every stop and every day in his little notebook.'),
   ('كان لازم يوصلوا كل مكان بالوقت المضبوط، وإلا بيخسر الرهان.', 'They had to reach every place at the right time, or he would lose the bet.'),
   ('باسبارتو صار يفهم إنه هاي الرحلة مش لعب، هاي جدّ.', "Passepartout began to understand that this journey was no game — it was serious.")],
 ]),
 ('Detective Fix', 'المخبر فيكس', [
  [('بنفس الوقت الي كان فوغ مسافر فيه، كانت لندن كلها بتحكي عن سرقة البنك.', "At the same time Fogg was traveling, all of London was talking about the bank robbery."),
   ('حدا سرق مصاري كتيرة، والشرطة ما عرفت مين.', 'Someone had stolen a lot of money, and the police didn\'t know who.'),
   ('الوصف الي طلع عن الحرامي كان يشبه فوغ شوي.', 'The description that came out of the thief resembled Fogg a little.'),
   ('فصار في ناس تشك إنه فوغ هو الي سرق وهرب.', 'So some people suspected that Fogg was the one who had robbed and fled.')],
  [('مخبر اسمه فيكس كان بدّه يمسك الحرامي ليصير بطل.', 'A detective named Fix wanted to catch the thief so he could be a hero.'),
   ('سمع إنه فوغ مسافر لمصر، فراح مستناه هناك بالميناء.', 'He heard that Fogg was traveling to Egypt, so he went and waited for him there at the port.'),
   ('بس ما كان معه ورقة رسمية تخلّيه يمسكه بره إنجلترا.', 'But he didn\'t have an official warrant that would let him arrest him outside England.'),
   ('فقرر يمشي وراه من بلد لبلد، لحد ما توصل الورقة.', 'So he decided to follow him from country to country until the warrant arrived.')],
 ]),
 ('In Egypt', 'بمصر', [
  [('وصل فوغ لمدينة السويس بمصر، وكان فيكس مستنيه.', 'Fogg reached the city of Suez in Egypt, and Fix was waiting.'),
   ('فيكس شاف فوغ ودقّق فيه منيح، وصار أكتر متأكد إنه هو الحرامي.', 'Fix saw Fogg and looked at him carefully, and became more sure he was the thief.'),
   ('بس محتاج يعرف وين رايح ليقدر يلحقه.', 'But he needed to know where he was going in order to follow him.'),
   ('فراح لعند باسبارتو وصار يحكي معه بلطف.', 'So he went to Passepartout and started talking to him kindly.')],
  [('باسبarتو ما كان يعرف إنه فيكس مخبر، فحكى معه بكل بساطة.', 'Passepartout didn\'t know Fix was a detective, so he talked to him very openly.'),
   ('قال له كل إشي: عن الرهان، وعن الرحلة، ووين رايحين.', 'He told him everything: about the bet, about the journey, and where they were going.'),
   ('فيكس فرح كتير من جوّاته، لأنه هلق بيعرف كل الطريق.', 'Fix was very happy inside, because now he knew the whole route.'),
   ('ركبوا المركب من جديد باتجاه الهند، وفيكس معهم من بعيد.', 'They boarded the ship again toward India, with Fix along, keeping his distance.')],
 ]),
 ('Across the Sea to India', 'عبر البحر للهند', [
  [('المركب أبحر بالبحر الأحمر، والجو كان حامي كتير.', 'The ship sailed the Red Sea, and the weather was very hot.'),
   ('فوغ ظلّ هادي بغرفته، بيلعب الورق وما بيهتم بالمنظر.', 'Fogg stayed calm in his room, playing cards and not caring about the view.'),
   ('كان مركز بس على إشي واحد: الوقت.', 'He was focused on one thing only: the time.'),
   ('كل ما وصلوا محطة، كان يشوف إذا هم متقدمين ولا متأخرين.', 'Every time they reached a stop, he checked whether they were ahead or behind.')],
  [('أما باسبارتو، فكان مبسوط ومندهش من كل إشي جديد بيشوفه.', 'But Passepartout was happy and amazed by every new thing he saw.'),
   ('لاحظ إنه فيكس دايمًا موجود، بأي مركب وبأي بلد.', 'He noticed that Fix was always around, on every ship and in every country.'),
   ('بس ما شكّ فيه، وفكر إنه بس مسافر متلهم.', "But he didn't suspect him, and thought he was just a traveler like them."),
   ('بعد كم يوم، وصلوا مدينة بومباي بالهند بالوقت المضبوط.', 'After a few days, they reached the city of Bombay in India, right on time.')],
 ]),
 ('The Land of India', 'أرض الهند', [
  [('بومباي كانت مدينة كبيرة ومليانة ناس وألوان وأصوات.', 'Bombay was a big city, full of people, colors, and sounds.'),
   ('باسبارتو راح يتمشى ويتفرج، وكان كل إشي غريب وحلو بعينه.', 'Passepartout went for a walk to look around, and everything seemed strange and lovely to him.'),
   ('بس بالغلط، فوت على معبد وهو لابس جزمته.', 'But by mistake, he entered a temple while still wearing his shoes.'),
   ('هالإشي كان ممنوع، فزعلوا منه الناس هناك كتير وطردوه.', 'This was forbidden, so the people there got very angry at him and drove him out.')],
  [('رجع باسبارتو لعند فوغ وهو خايف، بس ما حكى له عن المشكلة.', "Passepartout returned to Fogg, scared, but he didn't tell him about the problem."),
   ('ركبوا القطار الي بيعبر الهند كلها من بومباي لكلكتا.', 'They boarded the train that crosses all of India, from Bombay to Calcutta.'),
   ('فيكس ظلّ وراهم، وكان فرحان لأنه بالهند بيقدر يمسك فوغ.', 'Fix stayed behind them, and was glad because in India he could arrest Fogg.'),
   ('بس لسا الورقة الرسمية ما وصلت، فاضطر يستنى.', "But the official warrant still hadn't arrived, so he had to wait."),]
 ]),
 ('The Forest and the Elephant', 'الغابة والفيل', [
  [('وهم بالقطار، وقف فجأة بنص الطريق.', 'While they were on the train, it suddenly stopped in the middle of the way.'),
   ('طلع إنه السكة لسا ما خلصوها، والقطار ما بيقدر يكمّل.', "It turned out the track wasn't finished, and the train couldn't continue."),
   ('كل الركاب زعلوا، بس فوغ ظلّ هادي زي عادته.', 'All the passengers were upset, but Fogg stayed calm as usual.'),
   ('قال: لازم نلاقي طريقة تانية نكمّل فيها.', 'He said: we have to find another way to continue.')],
  [('لقوا رجل معه فيل كبير، فاشترى فوغ الفيل بمصاري كتيرة.', 'They found a man with a big elephant, and Fogg bought the elephant for a lot of money.'),
   ('ركبوا على ظهر الفيل: فوغ، وباسبارتو، ودليل بيعرف الطريق.', 'They rode on the elephant\'s back: Fogg, Passepartout, and a guide who knew the way.'),
   ('مشيوا بغابة كبيرة وطريق صعب لساعات طويلة.', 'They traveled through a big forest and a hard road for long hours.'),
   ('باسبارتو كان مبسوط ومكشوش، لأنه ما ركب فيل بحياته من قبل.', 'Passepartout was happy and thrilled, because he had never ridden an elephant in his life.')],
 ]),
 ('Rescuing Aouda', 'إنقاذ عودا', [
  [('وهم ماشيين بالليل، سمعوا أصوات وشافوا ضو من بعيد.', 'As they traveled at night, they heard voices and saw a light in the distance.'),
   ('قرّبوا بهدوء، وشافوا ناس كتير حوالين امرأة شابة وحلوة.', 'They approached quietly and saw many people around a young, beautiful woman.'),
   ('الدليل حكى لهم إنها أميرة اسمها عودا، ومات جوزها.', 'The guide told them she was a princess named Aouda, and her husband had died.'),
   ('حسب عادة قديمة وظالمة، كانوا بدهم يأذوها بكرة الصبح.', 'According to an old and cruel custom, they intended to harm her the next morning.')],
  [('قال فوغ: ما بقدر أتركها، لازم ننقذها، ولو هالإشي أخّرنا.', "Fogg said: I can't leave her — we must save her, even if it delays us."),
   ('استنوا لنص الليل، لما الكل نام.', 'They waited until midnight, when everyone was asleep.'),
   ('تسلل باسبارتو بذكاء وشجاعة، وقدر يطلّع الأميرة بالخفية.', 'Passepartout sneaked in cleverly and bravely, and managed to spirit the princess away.'),
   ('هربوا كلهم على الفيل قبل ما يصحى حدا.', 'They all escaped on the elephant before anyone woke up.'),
   ('عودا كانت شاكرة كتير، وصارت تسافر معهم.', 'Aouda was very grateful, and she began traveling with them.')],
 ]),
 ('Trouble in Calcutta', 'مشكلة بكلكتا', [
  [('وصلوا مدينة كلكتا بعد مشوار طويل وتعبان.', 'They reached the city of Calcutta after a long, tiring trip.'),
   ('بس أول ما نزلوا، جت الشرطة وأمسكت فوغ وباسبارتو.', 'But as soon as they got off, the police came and arrested Fogg and Passepartout.'),
   ('السبب كان مشكلة المعبد الي صارت ببومباي.', 'The reason was the temple problem that had happened in Bombay.'),
   ('راحوا عالمحكمة، والقاضي حكم عليهم بغرامة وحبس.', 'They went to court, and the judge sentenced them to a fine and jail.')],
  [('فيكس كان هو الي رتّب هالإشي، ليأخّر فوغ لحد ما توصل الورقة.', 'Fix was the one who had arranged this, to delay Fogg until the warrant arrived.'),
   ('بس فوغ دفع الغرامة فورًا، وطلعوا من المحكمة بسرعة.', 'But Fogg paid the fine immediately, and they left the court quickly.'),
   ('ركبوا مركب كبير باتجاه هونغ كونغ، ومعهم عودا.', 'They boarded a big ship toward Hong Kong, with Aouda along.'),
   ('عودا سألت فوغ ليش عم يتعب حاله عشانها، فقال: هاد الإشي الصح، وبس.', "Aouda asked Fogg why he was troubling himself for her, and he said: it's the right thing, that's all.")],
 ]),
 ('On the Open Sea', 'عرض البحر', [
  [('المركب أبحر بالبحر، والجو صار مش منيح.', 'The ship sailed the sea, and the weather turned bad.'),
   ('إجت عاصفة قوية، والموج صار عالي وخطير.', 'A strong storm came, and the waves grew high and dangerous.'),
   ('المركب تأخّر كتير بسبب العاصفة.', 'The ship was greatly delayed because of the storm.'),
   ('فوغ ظلّ هادي، بس باسبارتو صار يخاف على الوقت.', 'Fogg stayed calm, but Passepartout began to worry about the time.')],
  [('فيكس كان لسا معهم، وصار يفكّر بخطة.', 'Fix was still with them, and he began thinking of a plan.'),
   ('عرف إنه هونغ كونغ آخر بلد إنجليزي بالطريق.', 'He realized Hong Kong was the last English land on the route.'),
   ('إذا فوغ طلع منها، ما رح يقدر يمسكه أبدًا، لأنه الورقة بتنفع بس ببلاد الإنجليز.', "If Fogg left it, he would never be able to catch him, because the warrant only worked in British lands."),
   ('فقرر يعمل أي إشي ليأخّر فوغ بهونغ كونغ.', 'So he decided to do anything to delay Fogg in Hong Kong.')],
 ]),
 ('Hong Kong', 'هونغ كونغ', [
  [('وصلوا هونغ كونغ، وكان فوغ بدّه يوصّل عودا لعند قريب إلها بيعيش هناك.', 'They reached Hong Kong, and Fogg wanted to deliver Aouda to a relative of hers who lived there.'),
   ('بس عرفوا إنه القريب سافر وراح لبلد تانية من زمان.', 'But they learned that the relative had traveled and moved to another country long ago.'),
   ('فقال فوغ لعودا: إذا بدّك، تعي معنا لحد لندن، وهناك بتكوني بأمان.', 'So Fogg said to Aouda: if you wish, come with us to London, and there you will be safe.'),
   ('عودا وافقت، وكانت مبسوطة إنها رح تظلّ معهم.', 'Aouda agreed, and she was glad she would stay with them.')],
  [('فيكس راح لعند باسبارتو وحكى له الحقيقة: أنا مخبر، وسيدك حرامي.', "Fix went to Passepartout and told him the truth: I am a detective, and your master is a thief."),
   ('باسبارتو زعل كتير وما صدّق، لأنه بيحب سيده ويثق فيه.', "Passepartout got very angry and didn't believe it, because he loved his master and trusted him."),
   ('فيكس خاف إنه باسبارتو رح يخبّر فوغ ويطلعوا بسرعة.', 'Fix was afraid Passepartout would warn Fogg and they would leave quickly.'),
   ('فقرر يعمل حيلة ليوقف باسبارتو عن التحرك.', 'So he decided to play a trick to stop Passepartout from acting.')],
 ]),
 ('The Lost Night', 'الليلة الي ضاعت', [
  [('راح فيكس مع باسبارتو على مكان وطلب له مشروب.', 'Fix went with Passepartout to a place and ordered him a drink.'),
   ('حط بالمشروب دوا بينوّم، بدون ما باسبارتو يعرف.', 'He put a sleeping drug in the drink, without Passepartout knowing.'),
   ('بس قبل ما ينام، باسبارتو كان سمع خبر مهم.', 'But before he fell asleep, Passepartout had heard an important piece of news.'),
   ('الباخرة لليابان رح تطلع بكير، قبل الوقت الي كانوا حاسبينه.', 'The steamer to Japan would leave early, before the time they had counted on.')],
  [('باسبارتو بدّه يخبّر فوغ، بس الدوا صار يشتغل فيه.', 'Passepartout wanted to tell Fogg, but the drug started to take effect on him.'),
   ('صار دايخ، وعيونه بتسكّر، ونام قبل ما يقدر يعمل إشي.', 'He grew dizzy, his eyes closing, and he fell asleep before he could do anything.'),
   ('ظلّ نايم طول الليل، وهو ما يدري وين.', 'He stayed asleep all night, not knowing where he was.'),
   ('وهيك، فوغ ما عرف إنه الباخرة رح تطلع بكير.', 'And so, Fogg did not learn that the steamer would leave early.')],
 ]),
 ('The Ship That Left', 'الباخرة الي راحت', [
  [('الصبح، صحي فوغ وما لقى باسبارتو.', "In the morning, Fogg woke up and didn't find Passepartout."),
   ('راح مع عودا عالميناء، بس الباخرة كانت طلعت من زمان.', 'He went with Aouda to the port, but the ship had left long ago.'),
   ('ما فقد أعصابه، وما صرخ ولا زعل.', "He didn't lose his temper — he neither shouted nor grew angry."),
   ('قال بهدوء: لازم نلاقي طريقة تانية.', 'He said calmly: we must find another way.')],
  [('دوّر فوغ عالميناء لحد ما لقى مركب صغير وسريع.', 'Fogg searched the port until he found a small, fast boat.'),
   ('اتفق مع صاحب المركب إنه ياخده هو وعودا لليابان.', 'He agreed with the boat\'s owner to take him and Aouda to Japan.'),
   ('بالآخر لحظة، إجا فيكس كمان وركب معهم.', 'At the last moment, Fix came too and boarded with them.'),
   ('فيكس صار محتار: بدّه فوغ يوصل إنجلترا ليمسكه، بس مش بسرعة كتير.', 'Fix grew torn: he wanted Fogg to reach England so he could arrest him, but not too fast.')],
 ]),
 ('A Storm at Sea', 'عاصفة بالبحر', [
  [('المركب الصغير أبحر بالبحر الواسع.', 'The small boat set out on the wide sea.'),
   ('بس بنص الطريق، إجت عاصفة كبيرة وقوية.', 'But midway, a big, strong storm came.'),
   ('الموج صار زي الجبال، والمركب صار يرتفع وينزل.', 'The waves became like mountains, and the boat rose and fell.'),
   ('الكل خاف، بس فوغ ظلّ واقف هادي بلا خوف.', 'Everyone was afraid, but Fogg remained standing, calm, without fear.')],
  [('صاحب المركب بدّه يوقف ويستنى لحد ما تهدا العاصفة.', 'The boat\'s owner wanted to stop and wait until the storm calmed.'),
   ('بس فوغ دفع له مصاري زيادة ليكمّل بأي طريقة.', 'But Fogg paid him extra money to continue by any means.'),
   ('بعد أيام صعبة وتعبانة، وصلوا بر اليابان.', 'After hard, exhausting days, they reached the shore of Japan.'),
   ('بس هلق، لازم يلاقوا باسبارتو الي ضاع منهم بهونغ كونغ.', 'But now, they had to find Passepartout, who had been lost from them in Hong Kong.')],
 ]),
 ('Passepartout in Japan', 'باسبارتو باليابان', [
  [('باسبارتو صحي من النوم وهو عالباخرة، ما بيعرف شو صار.', "Passepartout woke from his sleep aboard the steamer, not knowing what had happened."),
   ('الباخرة كانت مشيت وأخدته لليابان وهو نايم.', 'The steamer had sailed and taken him to Japan while he slept.'),
   ('وصل مدينة يوكوهاما وما كان معه ولا قرش.', 'He reached the city of Yokohama without a single coin.'),
   ('صار جوعان وتعبان، وما بيعرف شو يعمل.', 'He grew hungry and tired, and didn\'t know what to do.')],
  [('باع شوية من أواعيه عشان ياكل.', 'He sold some of his clothes so he could eat.'),
   ('وبعدين لقى فرقة بتعمل عروض للناس بالشارع.', 'And then he found a troupe that performed shows for people in the street.'),
   ('اشتغل معهم ليقدر يعيش، وصار جزء من عرض كبير.', 'He worked with them to survive, and became part of a big show.'),
   ('كانوا بيعملوا برج من ناس واقفين فوق بعض، وباسبارتو صار تحت.', 'They would build a tower of people standing on top of each other, and Passepartout was at the bottom.')],
 ]),
 ('Reunion at the Circus', 'اللقاء بالسيرك', [
  [('بنفس اليوم، فوغ وعودا كانوا عم يدوّروا على باسبارتو.', 'That same day, Fogg and Aouda were searching for Passepartout.'),
   ('بالصدفة، راحوا يتفرجوا على نفس العرض الي فيه باسبارتو.', 'By chance, they went to watch the very show that Passepartout was in.'),
   ('كانوا قاعدين بين الناس، ما بيعرفوا إنه هو هناك.', 'They were sitting among the people, not knowing he was there.'),
   ('وفجأة، باسبارتو شاف سيده فوغ بين المتفرجين.', 'And suddenly, Passepartout saw his master Fogg among the spectators.')],
  [('من الفرحة، نسي حاله وترك مكانه، والبرج كله وقع!', 'Out of joy, he forgot himself and left his spot, and the whole tower collapsed!'),
   ('ركض باسبارتو على سيده، وكان مبسوط كتير إنه لقاه.', 'Passepartout ran to his master, so happy to have found him.'),
   ('فوغ كمان ارتاح إنه لقى خادمه سالم.', 'Fogg too was relieved to have found his servant safe.'),
   ('طلعوا كلهم سوا، ومعهم فيكس، وركبوا باخرة كبيرة باتجاه أمريكا.', 'They all set off together, with Fix along, and boarded a big steamer toward America.')],
 ]),
 ('Toward America', 'نحو أمريكا', [
  [('الباخرة عبرت المحيط الهادي، وكان واسع وطويل كتير.', 'The steamer crossed the Pacific Ocean, which was very wide and long.'),
   ('فوغ ظلّ يحسب الأيام بدقة، وكان لسا بالوقت.', 'Fogg kept counting the days precisely, and he was still on time.'),
   ('عودا صارت تحس بإشي حلو تجاه فوغ، بس ما حكت.', "Aouda began to feel something sweet toward Fogg, but she didn't speak."),
   ('فوغ كان مشغول بالرهان، وما بيّن مشاعره لحدا.', "Fogg was busy with the bet, and didn't show his feelings to anyone."),]
  ,
  [('باسبارتو صار يشك بفيكس، وسأل حاله: ليش هالرجل معنا دايمًا؟', 'Passepartout grew suspicious of Fix, and asked himself: why is this man always with us?'),
   ('بس ما حكى إشي لهلق، وقرر يراقبه.', "But he said nothing yet, and decided to keep an eye on him."),
   ('بعد كم يوم، وصلوا مدينة سان فرانسيسكو بأمريكا.', 'After a few days, they reached the city of San Francisco in America.'),
   ('لهلق كل إشي تمام، بس أمريكا كلها كانت قدامهم.', 'So far everything was fine, but all of America lay ahead of them.')],
 ]),
 ('The American Train', 'القطار الأمريكي', [
  [('بسان فرانسيسكو، صار في مشكلة صغيرة بالشارع بين ناس كتار.', 'In San Francisco, there was a small trouble in the street among many people.'),
   ('فوغ وباسبارتو انحشروا بالنص، بس طلعوا بالسلامة.', 'Fogg and Passepartout got caught in the middle, but they got out safely.'),
   ('بعدها ركبوا القطار الكبير الي بيعبر أمريكا من الغرب للشرق.', 'Then they boarded the great train that crosses America from west to east.'),
   ('الطريق كان طويل، بيعبر جبال وسهول وأنهار.', 'The route was long, crossing mountains, plains, and rivers.')],
  [('باسبارتو كان يتفرج من الشباك على بلد جديدة وغريبة.', 'Passepartout watched from the window a new, strange land.'),
   ('كل إشي كان كبير وواسع: الأرض، والسما، والمسافات.', 'Everything was big and vast: the land, the sky, the distances.'),
   ('فوغ ظلّ قاعد بمكانه، بيلعب الورق زي عادته.', 'Fogg stayed in his seat, playing cards as usual.'),
   ('كان لسا بالوقت، بس الطريق قدامهم كان فيه مفاجآت.', 'He was still on time, but the road ahead held surprises.')],
 ]),
 ('Buffalo and Bridge', 'الجاموس والجسر', [
  [('وهم بالقطار، وقف فجأة، لأنه في قطيع جاموس كبير عم يعبر السكة.', 'While they were on the train, it suddenly stopped, because a big herd of buffalo was crossing the tracks.'),
   ('كانوا آلاف، وظلوا يعبروا لساعات طويلة.', 'They were thousands, and they kept crossing for long hours.'),
   ('ما كان في إشي يعملوه غير إنهم يستنوا.', 'There was nothing they could do but wait.'),
   ('باسبارتو زعل من التأخير، بس فوغ ظلّ هادي زي عادته.', 'Passepartout was upset at the delay, but Fogg stayed calm as usual.')],
  [('بعدين، وصلوا لجسر قديم وضعيف فوق نهر.', 'Later, they reached an old, weak bridge over a river.'),
   ('السائق خاف إنه الجسر ما بيتحمّل وزن القطار.', "The driver was afraid the bridge couldn't hold the train’s weight."),
   ('فقرروا يعبروا بأسرع سرعة ممكنة، عشان يخفّ الوزن عالجسر.', 'So they decided to cross at the fastest possible speed, to lighten the weight on the bridge.'),
   ('عبر القطار بسرعة جنونية، وبعد ما عبر، وقع الجسر وراهم.', 'The train crossed at a mad speed, and after it passed, the bridge collapsed behind them.')],
 ]),
 ('The Attack', 'هجوم الهنود', [
  [('وهم ماشيين، هجمت مجموعة من السكان الأصليين على القطار.', 'As they were going, a group of natives attacked the train.'),
   ('صار في قتال وخوف كبير بين الركاب.', 'A fight broke out and great fear spread among the passengers.'),
   ('فوغ وباسبارتو وفيكس حاربوا مع الناس ليدافعوا عن حالهم.', 'Fogg, Passepartout, and Fix fought alongside the people to defend themselves.'),
   ('باسبارتو كان شجاع، وقفز عالقطار ليوقفه ويخلّص الركاب.', 'Passepartout was brave, and leaped onto the train to stop it and save the passengers.')],
  [('نجح إنه يوقف القطار، بس بالهجمة، انخطف هو وكم واحد تانيين.', 'He managed to stop the train, but in the attack, he and a few others were seized.'),
   ('القطار وقف عند حصن فيه جنود.', 'The train stopped at a fort with soldiers.'),
   ('فوغ ما تركه، وقال: ما بروح وأترك خادمي.', "Fogg didn't abandon him, and said: I won't go and leave my servant."),
   ('راح مع مجموعة جنود ليدوّر على باسبارتو وينقذه.', 'He went with a group of soldiers to search for Passepartout and rescue him.')],
 ]),
 ('The Sledge on the Snow', 'الزحّافة عالتلج', [
  [('فوغ لقى باسبارتو وأنقذه هو والباقيين.', 'Fogg found Passepartout and rescued him and the others.'),
   ('عودا كانت قلقانة كتير، وفرحت لما رجعوا بالسلامة.', 'Aouda had been very worried, and she was glad when they came back safe.'),
   ('بس بهالوقت، القطار كان مشي وتركهم.', 'But by this time, the train had left them.'),
   ('صاروا متأخرين، ولازم يلاقوا طريقة يلحقوا فيها الوقت.', 'They were now behind, and had to find a way to make up the time.')],
  [('لقوا رجل معه زحّافة بتمشي عالتلج بقوة الهوا.', 'They found a man with a sledge that moves on the snow by the power of the wind.'),
   ('ركبوا فيها، ومشيت بسرعة كبيرة فوق التلج الأبيض.', 'They boarded it, and it sped along fast over the white snow.'),
   ('كان الجو بارد كتير، بس الزحّافة أخدتهم لمحطة قطار تانية.', 'The weather was very cold, but the sledge took them to another train station.'),
   ('ركبوا القطار من جديد، ورايحين لمدينة نيويورك.', 'They boarded the train again, headed for the city of New York.')],
 ]),
 ('The Race in New York', 'السباق بنيويورك', [
  [('وصلوا نيويورك، وركضوا عالميناء بسرعة.', 'They reached New York, and rushed to the port.'),
   ('بس الباخرة الي لأوروبا كانت طلعت قبلهم بشوي.', 'But the ship to Europe had left just before them.'),
   ('مرة تانية، ضيّعوا الباخرة بفرق دقايق بس.', 'Once again, they missed the ship by just a few minutes.'),
   ('باسبارتو حس بالذنب، لأنه بسببه صار كل هالتأخير.', 'Passepartout felt guilty, because all this delay was on his account.')],
  [('بس فوغ ما استسلم، وراح يدوّر على أي مركب تاني.', "But Fogg didn't give up, and went to look for any other ship."),
   ('لقى مركب صغير اسمه هنريتّا، بس صاحبه ما بدّه يروح لإنجلترا.', 'He found a small ship called the Henrietta, but its owner didn\'t want to go to England.'),
   ('فوغ دفع له مصاري كتيرة كتيرة، لحد ما وافق.', 'Fogg paid him a great deal of money, until he agreed.'),
   ('طلعوا بالمركب باتجاه أوروبا، والوقت عم يركض.', 'They set out on the ship toward Europe, with time running out.')],
 ]),
 ('Burning the Ship', 'حرق الباخرة', [
  [('بنص الطريق، صاحب المركب بدّه يغيّر الاتجاه ويروح لمكان تاني.', 'Midway, the ship\'s owner wanted to change course and go somewhere else.'),
   ('بس فوغ كان لازم يوصل إنجلترا بأسرع وقت.', 'But Fogg had to reach England as fast as possible.'),
   ('فعرض على صاحب المركب إنه يشتري منه المركب كله.', 'So he offered to buy the whole ship from its owner.'),
   ('صاحب المركب وافق، وصار فوغ هو المسؤول.', 'The owner agreed, and Fogg became the one in charge.')],
  [('بس بالطريق، الفحم الي بيشغّل المركب خلص.', 'But on the way, the coal that runs the ship ran out.'),
   ('فأمر فوغ إنهم يحرقوا خشب المركب نفسه عشان يكمّلوا.', "So Fogg ordered them to burn the ship's own wood to keep going."),
   ('حرقوا كل إشي من خشب، لحد ما ضلّ بس الحديد.', 'They burned everything wooden, until only the iron was left.'),
   ('أخيرًا، لمحوا بر إنجلترا من بعيد، وكان لسا في أمل.', 'At last, they glimpsed the shore of England from afar, and there was still hope.')],
 ]),
 ('The Arrest', 'الاعتقال', [
  [('وصلوا إنجلترا، وأول ما نزل فوغ، إجا فيكس وأمسكه.', 'They reached England, and as soon as Fogg got off, Fix came and arrested him.'),
   ('هالمرة كانت الورقة الرسمية وصلت، فحطّه فيكس بالحبس.', 'This time the official warrant had arrived, so Fix put him in jail.'),
   ('باسبارتو انجنّ من الغضب، لأنه عرف إنه فيكس كان السبب بكل التأخير.', 'Passepartout went mad with anger, realizing Fix had been the cause of all the delays.'),
   ('فوغ ظلّ هادي بالحبس، مع إنه الوقت كان عم يضيع.', 'Fogg stayed calm in jail, even as the time was slipping away.')],
  [('بعد ساعات، بان إنه الحرامي الحقيقي انمسك من كم يوم.', 'After hours, it turned out the real thief had been caught days ago.'),
   ('فوغ كان بريء، وما كان له علاقة بالسرقة أبدًا.', 'Fogg was innocent, and had nothing to do with the robbery at all.'),
   ('فيكس اعتذر كتير، بس الوقت كان راح، وفوغ خسر ساعات غالية.', 'Fix apologized profusely, but the time was gone, and Fogg had lost precious hours.'),
   ('رجع فوغ عالبيت وهو مفكّر إنه خسر الرهان.', 'Fogg returned home thinking he had lost the bet.')],
 ]),
 ('The Eightieth Day', 'اليوم الثمانين', [
  [('فوغ رجع عالبيت هادي، بس من جوّاته كان زعلان.', 'Fogg returned home calm, but inside he was sad.'),
   ('حس إنه خسر كل إشي: المصاري، والرهان، والتعب راح على الفاضي.', 'He felt he had lost everything: the money, the bet, and all the effort gone for nothing.'),
   ('بس عودا قعدت جنبه وقالت له: أنا بحبك، وبدّي أظلّ معك.', 'But Aouda sat by him and said: I love you, and I want to stay with you.'),
   ('فرح فوغ كتير، ولأول مرة بان الفرح على وجهه.', 'Fogg was very happy, and for the first time joy showed on his face.'),
   ('قرروا يتجوزوا، وبعتوا باسبارتو ليجهّز كل إشي.', 'They decided to marry, and sent Passepartout to arrange everything.')],
  [('ركض باسبارتو عالكنيسة، وهناك عرف إشي مهم كتير.', 'Passepartout ran to the church, and there he learned something very important.'),
   ('طلع إنهم غلطانين بالحساب بيوم كامل!', 'It turned out they had miscalculated by a whole day!'),
   ('لأنهم لفّوا الأرض باتجاه الشرق، ربحوا يوم بدون ما ينتبهوا.', 'Because they had gone around the earth toward the east, they had gained a day without noticing.'),
   ('اليوم مش الواحد وثمانين، اليوم هو الثمانين بالزبط!', "Today wasn't the eighty-first — today was exactly the eightieth!"),],
  [('ركض باسبارتو ورجع يصرخ: لسا في وقت، لسا فيك تربح!', 'Passepartout ran back shouting: there’s still time, you can still win!'),
   ('فوغ ركض عالنادي بأسرع ما يقدر.', 'Fogg raced to the club as fast as he could.'),
   ('وصل بآخر ثانية، ودخل قبل ما يخلص الوقت، وربح الرهان.', 'He arrived at the last second, entered before the time ran out, and won the bet.'),
   ('بس أهم من الرهان، إنه ربح عودا، وصار مبسوط بحياته لأول مرة.', 'But more important than the bet, he had won Aouda, and became happy in his life for the first time.')],
 ]),
]

def main():
    outdir = os.path.join(ROOT, 'texts')
    total = 0
    for i, (en, ar, paras) in enumerate(CHAPTERS, 1):
        cid = 'book-%s-ch%02d' % (BOOK_ID, i)
        sentences = []
        for pi, para in enumerate(paras):
            for (a, e) in para:
                sentences.append({'ar': a, 'en': e, 'p': pi})
        art = {
            'id': cid,
            'title': {'en': 'Chapter %d — %s' % (i, en), 'ar': 'الفصل %d — %s' % (i, ar)},
            'kind': 'book-chapter', 'book': BOOK_ID, 'book_title': BOOK_TITLE, 'chapter': i,
            'level': 'intermediate',
            'source': 'adapted by Claude — NOT native-validated',
            'sentences': sentences,
        }
        with open(os.path.join(outdir, cid + '.json'), 'w', encoding='utf-8') as f:
            json.dump(art, f, ensure_ascii=False, indent=1)
        total += len(sentences)
        print('wrote %s  (%d paragraphs, %d sentences)' % (cid, len(paras), len(sentences)))
    print('\n%d chapters, %d sentences -> texts/book-%s-ch*.json' % (len(CHAPTERS), total, BOOK_ID))

if __name__ == '__main__':
    main()
