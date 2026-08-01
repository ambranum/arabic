#!/usr/bin/env python3
"""Around the World in 80 Days — an abridged, graded retelling in spoken Palestinian Arabic.

Jules Verne's novel is public domain. This is a SIMPLIFIED adaptation for learners — the
sentences are written by Claude (NOT native-validated, flagged as such), graded to roughly the
"intermediate" story level. As everywhere in this project, the sentences are generated but every
WORD's metadata is looked up in Maknuune by the ingest pipeline — nothing about the words is invented.

Emits one text per chapter: texts/book-atw80-chNN.json (kind "book-chapter", grouped by book "atw80").
Run:  python3 pipeline/book_atw80.py    then ingest each chapter + build_app.py.
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BOOK_ID = 'atw80'
BOOK_TITLE = {'en': 'Around the World in 80 Days', 'ar': 'حول العالم في ثمانين يوم'}

# (english title, arabic title, [(arabic, english), ...])
CHAPTERS = [
 ('The Bet', 'الرهان', [
  ('فيلياس فوغ كان رجل إنجليزي محترم، بيعيش بلندن.', 'Phileas Fogg was a respectable English gentleman who lived in London.'),
  ('كان دقيق كتير بمواعيده، وكل يوم بيعمل نفس الإشي بنفس الوقت.', 'He was very precise about his schedule, and every day did the same thing at the same time.'),
  ('بيوم من الأيام، كان قاعد بالنادي مع أصحابه.', 'One day, he was sitting at the club with his friends.'),
  ('صاروا يحكوا عن الدنيا وقديش صارت صغيرة.', 'They started talking about the world and how small it had become.'),
  ('قال فوغ: بقدر ألف الكرة الأرضية كلها بثمانين يوم.', 'Fogg said: I can go around the whole world in eighty days.'),
  ('ضحكوا أصحابه وما صدقوه.', "His friends laughed and didn't believe him."),
  ('قال لهم: بتراهن معكم على عشرين ألف جنيه.', "He told them: I'll bet you twenty thousand pounds."),
  ('وافقوا على الرهان، وقرر فوغ يسافر بنفس الليلة.', 'They agreed to the bet, and Fogg decided to travel that very night.'),
  ('رجع على بيته وقال لخادمه إنهم رح يسافروا حالًا.', 'He went home and told his servant they would travel at once.'),
  ('الخادم انصدم، بس جهّز الشنطة وطلعوا.', 'The servant was shocked, but he packed the bag and they left.'),
 ]),
 ('The Servant and the Detective', 'الخادم والمخبر', [
  ('خادم فوغ اسمه باسبارتو، وكان رجل فرنسي طيّب.', "Fogg's servant was named Passepartout, and he was a good-natured Frenchman."),
  ('هو كان بس هلق بلّش يشتغل عند فوغ، وكان بدّه حياة هادية.', 'He had only just started working for Fogg, and he wanted a quiet life.'),
  ('بس هلق لقى حاله مسافر حول العالم!', 'But now he found himself traveling around the world!'),
  ('ركبوا القطار وبعدين المركب باتجاه مصر.', 'They took the train and then the ship toward Egypt.'),
  ('بنفس الوقت، بلندن، صار في سرقة كبيرة من البنك.', 'At the same time, in London, there was a big robbery at the bank.'),
  ('الشرطة كانت تدوّر على الحرامي، وشكّوا بفوغ.', 'The police were looking for the thief, and they suspected Fogg.'),
  ('مخبر اسمه فيكس راح يلحق فوغ ليمسكه.', 'A detective named Fix went to chase Fogg to catch him.'),
  ('فيكس صار يتبع فوغ من بلد لبلد.', 'Fix started following Fogg from country to country.'),
  ('بس ما كان معه ورقة تسمح له يمسكه بره إنجلترا.', "But he didn't have a warrant that let him arrest him outside England."),
  ('فقرر يمشي معهم ويستنى الفرصة المناسبة.', 'So he decided to travel with them and wait for the right chance.'),
 ]),
 ('From Suez to Bombay', 'من السويس لبومباي', [
  ('وصلوا مدينة السويس بمصر، وكان فيكس مستنيهم هناك.', 'They reached the city of Suez in Egypt, and Fix was waiting for them there.'),
  ('باسبارتو ما كان يعرف إنه فيكس مخبر.', "Passepartout didn't know that Fix was a detective."),
  ('حكى معه بلطف وقال له كل إشي عن رحلتهم.', 'He talked to him kindly and told him everything about their journey.'),
  ('فيكس فرح، لأنه هلق بيعرف وين رايحين.', 'Fix was happy, because now he knew where they were going.'),
  ('ركبوا المركب من جديد وعبروا البحر لبومباي بالهند.', 'They boarded the ship again and crossed the sea to Bombay in India.'),
  ('فوغ ظلّ هادي، بيلعب الورق وما بيهتم بالمنظر.', 'Fogg stayed calm, playing cards and not caring about the scenery.'),
  ('أما باسبارتو، فكان مبسوط ومندهش من كل إشي جديد.', 'But Passepartout was happy and amazed by everything new.'),
  ('وصلوا بومباي بالوقت المضبوط، لهلق كل إشي تمام.', 'They arrived in Bombay right on time; so far everything was fine.'),
  ('بس الطريق قدامهم كان طويل وصعب.', 'But the road ahead of them was long and hard.'),
  ('لازم ياخدوا القطار يعبر الهند كلها.', 'They had to take the train across all of India.'),
 ]),
 ('Rescuing Aouda', 'إنقاذ عودا', [
  ('ركبوا القطار من بومباي، بس فجأة وقف بنص الطريق.', 'They boarded the train from Bombay, but suddenly it stopped in the middle of the way.'),
  ('السكة ما كانت خالصة، فاضطروا يكملوا على ظهر فيل.', "The track wasn't finished, so they had to continue on the back of an elephant."),
  ('وهم ماشيين، شافوا ناس كتير حوالين امرأة شابة.', 'As they were going, they saw many people around a young woman.'),
  ('عرفوا إنها أميرة اسمها عودا، وبدهم يأذوها حسب عادة قديمة.', 'They learned she was a princess named Aouda, and they wanted to harm her according to an old custom.'),
  ('قرر فوغ ينقذها، مع إنه هالإشي رح يأخره.', 'Fogg decided to save her, even though this would delay him.'),
  ('بالليل، تسلل باسبارتو وخطفها بذكاء.', 'At night, Passepartout sneaked in and cleverly snatched her away.'),
  ('هربوا كلهم سوا قبل ما حدا يصحى.', 'They all escaped together before anyone woke up.'),
  ('عودا صارت معهم بالرحلة، وكانت شاكرة كتير.', 'Aouda joined them on the journey, and she was very grateful.'),
  ('فوغ عاملها باحترام، وقرر ياخدها لمكان أمان.', 'Fogg treated her with respect and decided to take her to a safe place.'),
  ('وهيك صاروا ثلاثة بدل اثنين.', 'And so they became three instead of two.'),
 ]),
 ('Trouble in Calcutta', 'مشكلة بكلكتا', [
  ('وصلوا مدينة كلكتا بعد مشوار تعبان.', 'They reached the city of Calcutta after a tiring trip.'),
  ('بس أول ما نزلوا، جت الشرطة وأمسكت باسبارتو.', 'But as soon as they got off, the police came and arrested Passepartout.'),
  ('كان قبل هيك عمل مشكلة صغيرة بمعبد بالغلط.', 'He had earlier caused a small problem at a temple by mistake.'),
  ('راحوا كلهم عالمحكمة، وفوغ دفع مصاري ليطلعوهم.', 'They all went to court, and Fogg paid money to get them released.'),
  ('فيكس كان فرحان، لأنه هالتأخير بيساعده.', 'Fix was happy, because this delay helped him.'),
  ('بس فوغ ما ضيّع وقت، وركبوا المركب فورًا.', "But Fogg didn't waste time, and they boarded the ship at once."),
  ('هالمرة كانوا رايحين لهونغ كونغ.', 'This time they were headed to Hong Kong.'),
  ('عودا سألت فوغ ليش عم يساعدها هالقد.', 'Aouda asked Fogg why he was helping her so much.'),
  ('قال لها بهدوء: هاد الإشي الصح، وبس.', "He told her calmly: it's the right thing, that's all."),
  ('المركب أبحر، والرحلة كملت.', 'The ship set sail, and the journey continued.'),
 ]),
 ("Fix's Scheme", 'خطة فيكس', [
  ('بالطريق لهونغ كونغ، فيكس قرر يحكي مع باسبارتو.', 'On the way to Hong Kong, Fix decided to talk to Passepartout.'),
  ('حاول يقنعه إنه فوغ حرامي، بس باسبارتو ما صدّق.', "He tried to convince him that Fogg was a thief, but Passepartout didn't believe it."),
  ('زعل منه كتير، لأنه بيحب سيده ويثق فيه.', 'He got very angry at him, because he loved his master and trusted him.'),
  ('لما وصلوا هونغ كونغ، فيكس كان لسا ما معه الورقة.', "When they reached Hong Kong, Fix still didn't have the warrant."),
  ('عرف إنه هونغ كونغ آخر مكان إنجليزي بالطريق.', 'He realized Hong Kong was the last English place on the route.'),
  ('إذا فوغ طلع منها، ما رح يقدر يمسكه أبدًا.', 'If Fogg left it, he would never be able to catch him.'),
  ('فقرر يعمل أي إشي ليأخر باسبارتو والمركب.', 'So he decided to do anything to delay Passepartout and the ship.'),
  ('راح مع باسبارتو على مطعم وطلب له مشروب.', 'He went with Passepartout to a restaurant and ordered him a drink.'),
  ('المشروب كان فيه دوا بينوّم.', 'The drink had a sleeping drug in it.'),
  ('باسبارتو نام، ونسي يخبّر فوغ إنه المركب رح يسافر بكير.', 'Passepartout fell asleep and forgot to tell Fogg that the ship would leave early.'),
 ]),
 ('The Missed Boat', 'ضاع المركب', [
  ('صحي فوغ الصبح وما لقى باسبارتو.', "Fogg woke up in the morning and didn't find Passepartout."),
  ('راح عالميناء، بس المركب كان طلع من زمان.', 'He went to the port, but the ship had left long ago.'),
  ('ما فقد أعصابه، ودوّر على مركب تاني صغير.', "He didn't lose his temper, and looked for another small boat."),
  ('لقى واحد ووافق صاحبه ياخده هو وعودا.', 'He found one, and its owner agreed to take him and Aouda.'),
  ('فيكس لحقهم بالمركب الصغير كمان.', 'Fix followed them on the small boat too.'),
  ('البحر كان هايج والجو صعب كتير.', 'The sea was rough and the weather very hard.'),
  ('بس بعد أيام تعبانة، وصلوا مدينة يوكوهاما باليابان.', 'But after exhausting days, they reached the city of Yokohama in Japan.'),
  ('فوغ كان بدّه يلاقي باسبارتو، بس ما عرف وينه.', "Fogg wanted to find Passepartout, but didn't know where he was."),
  ('المركب الأول كان وصل قبلهم، وباسبارتو كان هناك.', 'The first ship had arrived before them, and Passepartout was there.'),
  ('بس المدينة كبيرة، وكيف رح يلاقوا بعض؟', 'But the city is big, so how would they find each other?'),
 ]),
 ('Reunion in Yokohama', 'اللقاء بيوكوهاما', [
  ('باسبارتو صحي بالمركب وهو ما بيعرف شو صار.', "Passepartout woke up on the ship not knowing what had happened."),
  ('وصل يوكوهاما وما كان معه ولا قرش.', 'He reached Yokohama without a single coin.'),
  ('اضطر يشتغل بسيرك ليقدر ياكل.', 'He had to work in a circus to be able to eat.'),
  ('بالصدفة، فوغ وعودا كانوا عم يتفرجوا على نفس السيرك.', 'By chance, Fogg and Aouda were watching the same circus.'),
  ('لما شاف باسبارتو سيده، فرح كتير وركض عليه.', 'When Passepartout saw his master, he was so happy and ran to him.'),
  ('فوغ كان مبسوط إنه لقاه سالم.', 'Fogg was glad he found him safe.'),
  ('طلعوا كلهم سوا من جديد، ومعهم فيكس.', 'They all set off together again, with Fix along.'),
  ('ركبوا مركب كبير باتجاه أمريكا.', 'They boarded a big ship toward America.'),
  ('باسبارتو حكى لفوغ كل الي صار معه.', 'Passepartout told Fogg everything that had happened to him.'),
  ('بس ما حكى إشي عن شكوكه بفيكس لهلق.', 'But he said nothing about his suspicions of Fix yet.'),
 ]),
 ('Crossing the Ocean', 'عبور المحيط', [
  ('المحيط الهادي كان واسع كتير، والرحلة طويلة.', 'The Pacific Ocean was very wide, and the trip long.'),
  ('فوغ ظلّ يحسب الأيام بدقة، وكان لسا بالوقت.', 'Fogg kept counting the days precisely, and he was still on time.'),
  ('عودا صارت تحس بإشي حلو تجاه فوغ.', 'Aouda started to feel something sweet toward Fogg.'),
  ('بس فوغ كان مشغول بالرهان وما بيّن إشي.', "But Fogg was busy with the bet and didn't show anything."),
  ('باسبارتو لاحظ إنه فيكس لسا معهم.', 'Passepartout noticed that Fix was still with them.'),
  ('صار يشك أكتر إنه هاد الرجل بدّه إشي مش منيح.', 'He grew more suspicious that this man wanted something bad.'),
  ('بعد كم يوم، شافوا بر أمريكا من بعيد.', 'After a few days, they saw the shore of America from afar.'),
  ('وصلوا مدينة سان فرانسيسكو بالوقت المضبوط.', 'They arrived in San Francisco right on time.'),
  ('لهلق، الرهان كان لسا ممكن يربحوه.', 'So far, the bet could still be won.'),
  ('بس أمريكا كلها كانت قدامهم، من الغرب للشرق.', 'But all of America was ahead of them, from west to east.'),
 ]),
 ('The Train in America', 'القطار بأمريكا', [
  ('ركبوا القطار من سان فرانسيسكو باتجاه نيويورك.', 'They boarded the train from San Francisco toward New York.'),
  ('الطريق كان يعبر جبال وسهول كتيرة.', 'The route crossed many mountains and plains.'),
  ('بنص الطريق، وقف القطار قدام جسر خربان.', 'Midway, the train stopped in front of a broken bridge.'),
  ('الناس خافوا، بس قرروا يعبروا بسرعة كبيرة.', 'The people were scared, but they decided to cross at high speed.'),
  ('عبروا الجسر بالسلامة، والكل ارتاح.', 'They crossed the bridge safely, and everyone was relieved.'),
  ('بس بعدها، هجم ناس على القطار وصار في مشكلة.', 'But after that, some people attacked the train and there was trouble.'),
  ('بالهجوم، انخطف باسبارتو مع كم واحد تانيين.', 'In the attack, Passepartout was taken along with a few others.'),
  ('فوغ ما تركه، وراح يدوّر عليه مع جنود.', "Fogg didn't abandon him, and went to look for him with soldiers."),
  ('لقاه وأنقذه، بس هالإشي أخرهم كمان.', 'He found and rescued him, but this delayed them again.'),
  ('ضاع منهم القطار، ولازم يلاقوا طريقة تانية.', 'They missed the train, and had to find another way.'),
 ]),
 ('Racing to the Ship', 'السباق للمركب', [
  ('فوغ استأجر مركبة صغيرة تمشي عالتلج.', 'Fogg hired a small sled that moves on the snow.'),
  ('مشيوا فيها بسرعة لحدّ ما لحقوا قطار تاني.', 'They rode it fast until they caught another train.'),
  ('وصلوا نيويورك، بس المركب لأوروبا كان طلع.', 'They reached New York, but the ship to Europe had left.'),
  ('مرة تانية، ضيّعوا المركب بفرق دقايق.', 'Once again, they missed the ship by a few minutes.'),
  ('فوغ ما استسلم، ولقى مركب صغير تاني.', "Fogg didn't give up, and found another small ship."),
  ('دفع مصاري كتير ليوصلهم بأسرع وقت.', 'He paid a lot of money to get them across as fast as possible.'),
  ('البحر كان صعب، والفحم خلص بالطريق.', 'The sea was hard, and the coal ran out on the way.'),
  ('فوغ اشترى المركب كله وحرق خشبه ليكمّلوا.', 'Fogg bought the whole ship and burned its wood to keep going.'),
  ('أخيرًا، لمحوا بر إنجلترا من بعيد.', 'At last, they glimpsed the shore of England from afar.'),
  ('كان لسا في أمل يوصلوا بالوقت.', "There was still hope they'd arrive in time."),
 ]),
 ('The Winning Day', 'اليوم المربوح', [
  ('وصلوا إنجلترا، وأول ما نزل فوغ، أمسكه فيكس.', 'They reached England, and as soon as Fogg got off, Fix arrested him.'),
  ('حطّه بالحبس، لأنه لسا مفكّره الحرامي.', 'He put him in jail, because he still thought he was the thief.'),
  ('بس بعد ساعات، بان إنه الحرامي الحقيقي انمسك من زمان.', 'But after hours, it turned out the real thief had been caught long ago.'),
  ('فيكس اعتذر، بس الوقت كان راح، وفوغ خسر ساعات غالية.', 'Fix apologized, but the time was gone, and Fogg lost precious hours.'),
  ('رجع فوغ على بيته وهو مفكّر إنه خسر الرهان.', 'Fogg went home thinking he had lost the bet.'),
  ('كان زعلان، بس عودا وقفت جنبه وقالت له إنها بتحبه.', 'He was sad, but Aouda stood by him and told him she loved him.'),
  ('فرح فوغ كتير، وقرروا يتجوزوا.', 'Fogg was very happy, and they decided to get married.'),
  ('بعتوا باسبارتو ليجهّز الزواج، وهو ركض عالكنيسة.', 'They sent Passepartout to arrange the wedding, and he ran to the church.'),
  ('هناك عرف إشي مهم: كانوا غلطانين بالحساب بيوم كامل!', 'There he learned something important: they had miscalculated by a whole day!'),
  ('لأنهم لفّوا الأرض باتجاه الشرق، ربحوا يوم كامل.', 'Because they went around the earth toward the east, they gained a whole day.'),
  ('ركض باسبارتو ورجع يصرخ: لسا معكم وقت، اليوم هو السبعين!', 'Passepartout ran back shouting: you still have time, today is the eightieth!'),
  ('فوغ راح عالنادي بآخر لحظة وربح الرهان.', 'Fogg went to the club at the last moment and won the bet.'),
  ('بس أهم إشي، إنه ربح عودا وصار مبسوط بحياته.', 'But the most important thing was that he won Aouda and became happy in his life.'),
 ]),
]

def main():
    outdir = os.path.join(ROOT, 'texts')
    for i, (en, ar, sents) in enumerate(CHAPTERS, 1):
        cid = 'book-%s-ch%02d' % (BOOK_ID, i)
        art = {
            'id': cid,
            'title': {'en': 'Chapter %d — %s' % (i, en), 'ar': 'الفصل %d — %s' % (i, ar)},
            'kind': 'book-chapter', 'book': BOOK_ID, 'book_title': BOOK_TITLE, 'chapter': i,
            'level': 'intermediate',
            'source': 'adapted by Claude — NOT native-validated',
            'sentences': [{'ar': a, 'en': e} for (a, e) in sents],
        }
        with open(os.path.join(outdir, cid + '.json'), 'w', encoding='utf-8') as f:
            json.dump(art, f, ensure_ascii=False, indent=1)
        print('wrote %s  (%d sentences)' % (cid, len(sents)))
    print('\n%d chapters -> texts/book-%s-ch*.json' % (len(CHAPTERS), BOOK_ID))

if __name__ == '__main__':
    main()
