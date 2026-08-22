#!/usr/bin/env python3
"""جحا — forty short tales, retold in spoken Palestinian, graded to beginner.

Juha (Nasreddin Hoja in Turkish, Goha in Egyptian) is folk material: centuries old, anonymous,
retold in every language between Morocco and Central Asia. Public domain by age — there is no
author to credit and no edition being translated. These are retellings from the traditional
plots, written for graded reading.

WHY THIS IS THE RIGHT FIRST BEGINNER BOOK. The tales run three to eight sentences, they repeat
their own frame (جحا راح…، جحا قال…، جاره سأله…), and they live in markets and kitchens and on a
donkey — so A1 vocabulary comes from the material rather than from restraint. And they are funny,
which is what gets a beginner to read the next one.

Written to the numbers pipeline/bookshelf_check.py measures: sentences under ~25 Arabic characters,
present and simple past, no subordination stacked more than one deep, and the same small cast
(جحا، جاره، الحمار، السوق، القاضي) recurring so vocabulary is reinforced instead of just met.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated), but
every WORD's root, meaning and pronunciation is looked up in Maknuune by the ingest pipeline.

Run:  python3 pipeline/book_juha.py    then ingest each chapter + build_app.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bookshelf import P, emit_book

BOOK_ID = 'juha'
BOOK_TITLE = {'en': 'Juha', 'ar': 'جحا'}

# (english title, arabic title, [paragraph, ...])
CHAPTERS = [
 ('The Donkey and the Neighbour', 'الحمار والجار', [
  P(('جحا كان عنده حمار زغير.', 'Juha had a small donkey.'),
    ('إجا جاره وقال له: بدي الحمار اليوم.', 'His neighbour came and said: I want the donkey today.')),
  P(('جحا ما بده يعطيه.', "Juha didn't want to give it to him."),
    ('قال له: الحمار مش هون، راح عالسوق.', 'He said: the donkey is not here, it went to the market.')),
  P(('بهاي اللحظة، الحمار نهق من ورا البيت.', 'At that moment, the donkey brayed from behind the house.'),
    ('قال الجار: بس أنا بسمع الحمار!', 'The neighbour said: but I hear the donkey!'),
    ('قال جحا: يا زلمة، بتصدق الحمار ولا بتصدقني؟', 'Juha said: man, do you believe the donkey or do you believe me?'))]),

 ('The Coat at the Feast', 'الكبوت بالعزيمة', [
  P(('جحا راح على عزيمة بلبس قديم.', 'Juha went to a feast in old clothes.'),
    ('محدا سلم عليه ولا حدا قعّده.', 'Nobody greeted him and nobody seated him.')),
  P(('رجع عالبيت ولبس كبوت جديد وحلو.', 'He went home and put on a new, handsome coat.'),
    ('رجع عالعزيمة، وهلق كل الناس قامت إله.', 'He came back to the feast, and now everyone stood up for him.'),
    ('قعّدوه بالصدر وحطوا قدامه الأكل.', 'They seated him in the place of honour and put the food in front of him.')),
  P(('جحا مد كم الكبوت عالصحن وقال: كول يا كبوتي.', 'Juha put the coat sleeve to the plate and said: eat, my coat.'),
    ('سألوه: شو عم تعمل؟', 'They asked him: what are you doing?'),
    ('قال: الأكل للكبوت، مش إلي.', 'He said: the food is for the coat, not for me.'))]),

 ('The Pot That Gave Birth', 'الطنجرة اللي ولدت', [
  P(('جحا استعار طنجرة كبيرة من جاره.', 'Juha borrowed a big pot from his neighbour.'),
    ('لما رجعها، حط جواتها طنجرة زغيرة.', 'When he returned it, he put a small pot inside it.')),
  P(('قال الجار: شو هاي الزغيرة؟', 'The neighbour said: what is this small one?'),
    ('قال جحا: طنجرتك ولدت.', 'Juha said: your pot gave birth.'),
    ('الجار فرح وأخذ التنتين.', 'The neighbour was happy and took both.')),
  P(('بعد أسبوع، استعار الطنجرة كمان مرة.', 'A week later, he borrowed the pot again.'),
    ('هاي المرة ما رجعها.', 'This time he did not return it.'),
    ('سأله الجار عنها، قال له: ماتت.', 'The neighbour asked about it; he said: it died.'),
    ('قال الجار: الطناجر ما بتموت!', 'The neighbour said: pots do not die!'),
    ('قال جحا: صدقت إنها بتولد.', 'Juha said: you believed it gives birth.'),
    ('وما بتصدق إنها بتموت؟', 'And you do not believe it dies?'))]),

 ('The Smell of the Food', 'ريحة الأكل', [
  P(('واحد فقير قعد جنب دكان أكل.', 'A poor man sat next to a food shop.'),
    ('أكل خبزه اليابس وهو بيشم الريحة.', 'He ate his dry bread while smelling the smell.')),
  P(('صاحب الدكان طلب منه مصاري.', 'The shop owner asked him for money.'),
    ('قال: إنت شميت أكلي، لازم تدفع.', 'He said: you smelled my food, you must pay.'),
    ('راحوا عند جحا، لأنه كان قاضي.', 'They went to Juha, because he was a judge.')),
  P(('جحا أخذ كيس مصاري وهزه قدام الرجل.', 'Juha took a bag of money and shook it in front of the man.'),
    ('سأله: سمعت صوت المصاري؟', 'He asked him: did you hear the sound of the money?'),
    ('قال: سمعت.', 'He said: I heard it.'),
    ('قال جحا: صوت المصاري بدفع ريحة الأكل.',
     'Juha said: the sound of the money pays for the smell of the food.'))]),

 ('Riding to Market', 'رايحين عالسوق', [
  P(('جحا وابنه راحوا عالسوق والحمار معهم.', 'Juha and his son went to the market with the donkey.'),
    ('جحا راكب والولد ماشي.', 'Juha was riding and the boy was walking.')),
  P(('ناس بالطريق حكوا: شوف الأب راكب.', 'People on the road said: look, the father is riding.'),
    ('وابنه ماشي تعبان.', 'And his son is walking, tired.'),
    ('فنزل جحا وركّب ابنه.', 'So Juha got down and put his son on.')),
  P(('ناس تانيين حكوا: شوف الولد راكب.', 'Other people said: look, the boy is riding.'),
    ('وأبوه كبير وماشي.', 'And his father is old and walking.'),
    ('فركبوا التنين مع بعض.', 'So the two of them rode together.'),
    ('وناس تانيين حكوا: مساكين، الحمار تعب.',
     'And other people said: poor thing, the donkey is tired.')),
  P(('بالآخر نزلوا التنين ومشيوا.', 'In the end they both got down and walked.'),
    ('قال جحا لابنه: مهما تعمل، في حدا رح يحكي.',
     'Juha said to his son: whatever you do, someone will talk.'))]),

 ('The Key in the Light', 'المفتاح بالضوء', [
  P(('جحا ضيّع مفتاحه بالليل.', 'Juha lost his key at night.'),
    ('قعد يدور عليه تحت الضوء بالشارع.', 'He was searching for it under the light in the street.')),
  P(('إجا جاره وصار يدور معه.', 'His neighbour came and searched with him.'),
    ('سأله: وين وقع المفتاح بالزبط؟', 'He asked him: where exactly did the key fall?'),
    ('قال جحا: وقع جوا البيت.', 'Juha said: it fell inside the house.')),
  P(('قال الجار: وليش عم تدور هون؟', 'The neighbour said: and why are you searching here?'),
    ('قال جحا: لأنه هون في ضوء.', 'Juha said: because here there is light.'))]),

 ('Three Days of Bread', 'خبز تلات أيام', [
  P(('جحا اشترى خبز لتلات أيام.', 'Juha bought bread for three days.'),
    ('حطه عالطاولة وراح ينام.', 'He put it on the table and went to sleep.')),
  P(('الصبح لقي الخبز كله ناقص.', 'In the morning he found all the bread was short.'),
    ('قال: في فار بالبيت.', 'He said: there is a mouse in the house.'),
    ('جاب قطة زغيرة.', 'He brought a small cat.')),
  P(('تاني يوم، الخبز واللبن كمان ناقصين.', 'The next day, the bread and the milk were both short.'),
    ('قال جحا: هلق صار عندي فار وقطة.', 'Juha said: now I have a mouse and a cat.'))]),

 ('The Sermon', 'الخطبة', [
  P(('طلبوا من جحا يخطب بالناس.', 'They asked Juha to give a sermon to the people.'),
    ('وقف قدامهم وسأل: بتعرفوا شو بدي أحكي؟',
     'He stood in front of them and asked: do you know what I am going to say?')),
  P(('قالوا: لأ، ما بنعرف.', 'They said: no, we do not know.'),
    ('قال: وأنا كمان ما بعرف. سلامتكم.', 'He said: and I also do not know. Goodbye.')),
  P(('الأسبوع الجاي سألهم نفس السؤال.', 'The next week he asked them the same question.'),
    ('قالوا: بنعرف.', 'They said: we know.'),
    ('قال: إذا بتعرفوا، ما في داعي أحكي.',
     'He said: if you know, there is no need for me to speak.')),
  P(('الأسبوع التالت، نص الناس قالوا بنعرف.', 'The third week, half the people said we know.'),
    ('والنص التاني قالوا ما بنعرف.', 'And the other half said we do not know.'),
    ('قال جحا: مليح.', 'Juha said: good.'),
    ('اللي بيعرف يحكي للي ما بيعرف.', 'Whoever knows should tell whoever does not know.'))]),

 ('Carrying the Door', 'شايل الباب', [
  P(('جحا بده يسافر ويترك البيت.', 'Juha wanted to travel and leave the house.'),
    ('أمه قالت له: دير بالك عالباب.', 'His mother said to him: take care of the door.')),
  P(('جحا قلع الباب وحمله على ظهره.', 'Juha took the door off and carried it on his back.'),
    ('مشي فيه كل الطريق.', 'He walked with it the whole way.')),
  P(('الناس سألوه: ليش شايل الباب؟', 'People asked him: why are you carrying the door?'),
    ('قال: أمي قالت لي دير بالك عليه.', 'He said: my mother told me to take care of it.'))]),

 ('The Ring in the Well', 'الخاتم بالبير', [
  P(('وقع خاتم جحا بالبير.', "Juha's ring fell in the well."),
    ('البير عميق والمي بعيدة.', 'The well was deep and the water far.')),
  P(('جحا جاب صحن لبن وكبه بالبير.', 'Juha brought a plate of yoghurt and poured it in the well.'),
    ('جاره شافه وسأله: شو عم تعمل؟', 'His neighbour saw him and asked: what are you doing?')),
  P(('قال جحا: عم أعمل لبن.', 'Juha said: I am making yoghurt.'),
    ('قال الجار: البير ما بيصير لبن!', 'The neighbour said: a well does not become yoghurt!'),
    ('قال جحا: وإذا صار؟', 'Juha said: and if it does?'))]),

 ('Counting the Donkeys', 'عد الحمير', [
  P(('جحا كان معه عشر حمير.', 'Juha had ten donkeys.'),
    ('ركب على واحد وعد الباقيين.', 'He rode one and counted the rest.')),
  P(('عد تسعة وخاف.', 'He counted nine and was afraid.'),
    ('نزل ومشي وعد كمان مرة: عشرة.', 'He got down and walked and counted again: ten.')),
  P(('ركب، صاروا تسعة. نزل، صاروا عشرة.',
     'He rode, they were nine. He got down, they were ten.'),
    ('قال: المشي أحسن، بس الحمير بتضل عشرة.',
     'He said: walking is better, but the donkeys stay ten.'))]),

 ('The Cold Night', 'الليلة الباردة', [
  P(('حدا راهن جحا: بتقدر تقضي الليل بالبرد؟',
     'Someone bet Juha: can you spend the night in the cold?'),
    ('قال جحا: بقدر.', 'Juha said: I can.')),
  P(('جحا وقف برا كل الليل بلا نار.', 'Juha stood outside all night with no fire.'),
    ('الصبح، الرجل سأله: شفت شي ضوء؟', 'In the morning, the man asked him: did you see any light?'),
    ('قال: شفت شمعة بعيدة كتير.', 'He said: I saw a candle very far away.')),
  P(('قال الرجل: يعني تدفيت فيها. ما بدفع.',
     'The man said: so you warmed yourself with it. I will not pay.')),
  P(('تاني يوم جحا عزمه على أكل.', 'The next day Juha invited him for food.'),
    ('الرجل قعد وقعد والأكل ما إجا.', 'The man sat and sat and the food did not come.'),
    ('راح عالمطبخ ولقي الطنجرة معلقة فوق شمعة.',
     'He went to the kitchen and found the pot hanging above a candle.'),
    ('قال جحا: الشمعة اللي بتدفي زلمة بتطبخ أكل.',
     'Juha said: a candle that warms a man cooks food.'))]),

 ('Which Half', 'أي نص', [
  P(('واحد سأل جحا سؤال صعب.', 'Someone asked Juha a hard question.'),
    ('ليش الدنيا نصها ليل ونصها نهار؟', 'Why is the world half night and half day?')),
  P(('جحا فكر شوي وقال: ما بعرف.', 'Juha thought a little and said: I do not know.'),
    ('الرجل زعل: إنت عالم ولازم تعرف!', 'The man was upset: you are a scholar and you should know!')),
  P(('قال جحا: العالم بيعرف إمتى يقول ما بعرف.',
     'Juha said: a scholar knows when to say I do not know.'))]),

 ('The Long Way Home', 'الطريق الطويل', [
  P(('جحا رجع من السوق بالليل.', 'Juha came back from the market at night.'),
    ('مشي ومشي ورجع لنفس المحل.', 'He walked and walked and came back to the same place.')),
  P(('قعد تحت شجرة وقال: بستنى الصبح.',
     'He sat under a tree and said: I will wait for the morning.'),
    ('نام شوي وصحي على صوت ديك.', 'He slept a little and woke to the sound of a rooster.')),
  P(('لقي حاله قدام باب بيته.', 'He found himself in front of his own door.'),
    ('قال: أقرب طريق للبيت هو النوم.', 'He said: the shortest way home is sleep.'))]),

 ('Salt and Wool', 'الملح والصوف', [
  P(('جحا حمل الملح على حماره.', 'Juha loaded salt on his donkey.'),
    ('الحمار وقع بالمي والملح داب.', 'The donkey fell in the water and the salt melted.')),
  P(('الحمل صار خفيف والحمار مبسوط.', 'The load became light and the donkey was happy.'),
    ('المرة الجاي، الحمار وقع بالمي بالقصد.',
     'The next time, the donkey fell in the water on purpose.')),
  P(('بس هاي المرة كان شايل صوف.', 'But this time it was carrying wool.'),
    ('الصوف شرب المي وصار تقيل كتير.', 'The wool drank the water and became very heavy.'),
    ('قال جحا: كل شغلة إلها وقتها.', 'Juha said: everything has its time.'))]),

 ('The Borrowed Cooking', 'الطبخة المستعارة', [
  P(('جارة جحا طلبت منه ملح.', "Juha's neighbour asked him for salt."),
    ('جحا أعطاها.', 'Juha gave her some.')),
  P(('بعد شوي طلبت زيت، وبعدين بصل.', 'A little later she asked for oil, then onion.'),
    ('جحا أعطاها كل إشي.', 'Juha gave her everything.')),
  P(('بالآخر إجت وقالت: الأكل جاهز، بتحب تاكل؟',
     'In the end she came and said: the food is ready, would you like to eat?'),
    ('قال جحا: أكيد، هاد أكلي.', 'Juha said: of course, this is my food.'))]),

 ('The Fur Coat in Summer', 'الفروة بالصيف', [
  P(('بعز الصيف، جحا لبس فروة تقيلة.', 'In the middle of summer, Juha wore a heavy fur coat.'),
    ('الناس ضحكوا عليه.', 'People laughed at him.')),
  P(('سألوه: مش حر عليك؟', 'They asked him: are you not hot?'),
    ('قال: الفروة بتمنع الحر يفوت.', 'He said: the fur stops the heat from getting in.')),
  P(('بالشتا، لبس نفس الفروة.', 'In the winter, he wore the same fur coat.'),
    ('قال: وبتمنع الدفا يطلع.', 'He said: and it stops the warmth from getting out.'))]),

 ('The Debt', 'الدين', [
  P(('جحا استلف مصاري من واحد.', 'Juha borrowed money from someone.'),
    ('وصل وقت الدفع وما كان معه.', 'The time to pay came and he did not have it.')),
  P(('الرجل إجا عالبيت وصار يصرخ.', 'The man came to the house and started shouting.'),
    ('جحا قال لمرته: قولي له مش هون.', 'Juha said to his wife: tell him he is not here.')),
  P(('مرته قالت: جحا مش بالبيت.', 'His wife said: Juha is not at home.'),
    ('صرخ الرجل من الشباك: بس أنا بشوفه!',
     'The man shouted from the window: but I can see him!'),
    ('قال جحا: بكرا لما أموت، رح تشوفني كمان؟',
     'Juha said: tomorrow when I die, will you see me too?'))]),

 ('The Old Tree', 'الشجرة القديمة', [
  P(('جحا زرع شجرة زيتون وهو كبير بالعمر.', 'Juha planted an olive tree when he was old.'),
    ('جاره ضحك وقال: إنت مش رح تاكل منها.',
     'His neighbour laughed and said: you will not eat from it.')),
  P(('قال جحا: أنا بكلت من شجر ما زرعته.',
     'Juha said: I ate from trees I did not plant.'),
    ('وحدا غيري رح ياكل من هاي.', 'And someone else will eat from this one.'))]),

 ('The Broken Jar', 'الجرة المكسورة', [
  P(('جحا بعت ابنه يجيب مي.', 'Juha sent his son to bring water.'),
    ('قبل ما يطلع، ضربه كف.', 'Before he left, he slapped him.')),
  P(('الجيران زعلوا: ليش ضربته وهو ما عمل إشي؟',
     'The neighbours were upset: why did you hit him when he did nothing?')),
  P(('قال جحا: لما تنكسر الجرة بتنكسر.', 'Juha said: when the jar breaks, it is broken.'),
    ('والضرب بعدها ما بينفع.', 'And hitting after that is no use.'))]),

 ('Both Are Right', 'التنين على حق', [
  P(('اتنين إجوا لجحا وهو قاضي.', 'Two men came to Juha while he was a judge.'),
    ('الأول حكى قصته.', 'The first told his story.'),
    ('قال جحا: معك حق.', 'Juha said: you are right.')),
  P(('التاني حكى قصته.', 'The second told his story.'),
    ('قال جحا: وإنت كمان معك حق.', 'Juha said: and you are also right.')),
  P(('مرته كانت قاعدة هناك.', 'His wife was sitting there.'),
    ('قالت: ما بصير التنين على حق!', 'She said: they cannot both be right!'),
    ('قال جحا: وإنتِ كمان معك حق.', 'Juha said: and you are right too.'))]),

 ('The Heavy Basket', 'السلة التقيلة', [
  P(('جحا شال سلة تقيلة عالحمار.', 'Juha put a heavy basket on the donkey.'),
    ('وبعدين ركب هو كمان.', 'And then he rode as well.')),
  P(('بس هو حامل السلة على راسه.', 'But he was carrying the basket on his head.'),
    ('واحد سأله: ليش ما بتحطها عالحمار؟',
     'Someone asked him: why do you not put it on the donkey?')),
  P(('قال جحا: الحمار شايلني، حرام أثقل عليه.',
     'Juha said: the donkey is carrying me, it would be cruel to make it heavier.'))]),

 ('Nine Months', 'تسع شهور', [
  P(('واحد جاره سأل جحا: إمتى بتخلص الشغلة؟',
     'A neighbour asked Juha: when will the work be finished?')),
  P(('قال جحا: بتسعة شهور.', 'Juha said: in nine months.'),
    ('قال الجار: هاي شغلة يومين!', 'The neighbour said: this is two days of work!')),
  P(('قال جحا: كل إشي حلو بده تسع شهور.',
     'Juha said: everything good needs nine months.'))]),

 ('The Guest Who Stayed', 'الضيف اللي ضل', [
  P(('ضيف إجا عند جحا وضل تلات أيام.', 'A guest came to Juha and stayed three days.'),
    ('بعدها ما بده يروح.', 'After that he did not want to leave.')),
  P(('جحا صار يحكي عن السمك.', 'Juha started talking about fish.'),
    ('قال: السمك والضيف بعد تلات أيام بيريحوا.',
     'He said: fish and a guest after three days start to smell.')),
  P(('الضيف ضحك وقال: أنا مش سمك.', 'The guest laughed and said: I am not a fish.'),
    ('قال جحا: بس أنا جعان.', 'Juha said: but I am hungry.'))]),

 ('Which Is Older', 'مين أكبر', [
  P(('سألوا جحا: القمر أهم ولا الشمس؟',
     'They asked Juha: is the moon more important or the sun?')),
  P(('جحا فكر وقال: القمر.', 'Juha thought and said: the moon.'),
    ('سألوه: ليش؟', 'They asked him: why?')),
  P(('قال: لأنه بيطلع بالليل.', 'He said: because it comes out at night.'),
    ('وقتها بنكون محتاجين ضوء.', 'That is when we need light.'),
    ('والشمس بتطلع بالنهار والدنيا ضوء.',
     'And the sun comes out in the day when the world is already light.'))]),

 ('The Mirror', 'المراية', [
  P(('جحا شاف حاله بالمراية أول مرة.', 'Juha saw himself in a mirror for the first time.'),
    ('قال: مين هاد الرجل الكبير؟', 'He said: who is this old man?')),
  P(('راح على مرته وقال: في زلمة بالمراية.',
     'He went to his wife and said: there is a man in the mirror.'),
    ('هي شافت وقالت: ولا في مرا كمان!',
     'She looked and said: and there is a woman too!'))]),

 ('The Wrong Grave', 'القبر الغلط', [
  P(('جحا مشي بالليل وخاف.', 'Juha walked at night and was afraid.'),
    ('نام جوا حفرة عالطريق.', 'He slept inside a hole on the road.')),
  P(('ناس مرقوا وسألوه: شو بتعمل هون؟',
     'People passed and asked him: what are you doing here?'),
    ('قال: أنا ميت.', 'He said: I am dead.')),
  P(('قالوا: والميت بيحكي؟', 'They said: and does a dead man talk?'),
    ('قال: بيحكي إذا كان جعان.', 'He said: he talks if he is hungry.'))]),

 ('The Egg', 'البيضة', [
  P(('جحا لقي بيضة بالطريق.', 'Juha found an egg on the road.'),
    ('قال: من هاي البيضة رح تطلع دجاجة.',
     'He said: from this egg a chicken will come.')),
  P(('ومن الدجاجة بيض كتير.', 'And from the chicken, many eggs.'),
    ('ومن البيض دجاج كتير.', 'And from the eggs, many chickens.'),
    ('ومن الدجاج مصاري كتير.', 'And from the chickens, a lot of money.')),
  P(('وهو عم يفكر، وقعت البيضة وانكسرت.',
     'While he was thinking, the egg fell and broke.'),
    ('قال: راحت كل مصاريي.', 'He said: all my money is gone.'))]),

 ('Teaching the Donkey', 'تعليم الحمار', [
  P(('الحاكم قال لجحا: علّم حماري يقرا.',
     'The ruler said to Juha: teach my donkey to read.'),
    ('قال جحا: بحاجة عشر سنين.', 'Juha said: I need ten years.')),
  P(('الناس قالوا له: إنت مجنون، الحمار ما بيقرا!',
     'People told him: you are crazy, a donkey does not read!')),
  P(('قال جحا: بعشر سنين بصير كتير إشي.', 'Juha said: in ten years a lot can happen.'),
    ('يا بموت الحاكم، يا بموت الحمار، يا بموت أنا.', 'Either the ruler dies, or the donkey dies, or I die.'))]),

 ('The Fastest Way', 'أسرع طريق', [
  P(('واحد سأل جحا: قديش بدي وقت لأوصل عالبلد؟',
     'Someone asked Juha: how long do I need to reach the town?'),
    ('جحا ما رد عليه.', 'Juha did not answer him.')),
  P(('الرجل مشي شوي.', 'The man walked a little.'),
    ('صرخ جحا: بساعتين!', 'Juha shouted: two hours!')),
  P(('الرجل سأله: وليش ما حكيت من الأول؟',
     'The man asked him: and why did you not say so at first?'),
    ('قال جحا: لازم أشوف كيف بتمشي.',
     'Juha said: I had to see how you walk.'))]),

 ('The Two Ends', 'الطرفين', [
  P(('جحا قعد على غصن وصار يقصه.', 'Juha sat on a branch and started cutting it.'),
    ('واحد مرق وقال: رح توقع!', 'Someone passed and said: you will fall!')),
  P(('جحا ما سمع منه، وبعد شوي وقع.',
     'Juha did not listen, and a little later he fell.')),
  P(('ركض ورا الرجل وقال: إنت بتعرف الغيب!',
     'He ran after the man and said: you know the unseen!'),
    ('قول لي إمتى بموت!', 'Tell me when I will die!'))]),

 ('The Bag of Onions', 'كيس البصل', [
  P(('جحا اشترى كيس بصل من السوق.', 'Juha bought a bag of onions from the market.'),
    ('الطريق طويلة والكيس تقيل.', 'The road was long and the bag heavy.')),
  P(('كل شوي كان يوقف ويعد البصلات.',
     'Every little while he would stop and count the onions.'),
    ('واحد سأله: ليش بتعد؟', 'Someone asked him: why are you counting?')),
  P(('قال جحا: كل ما بعد، بنسى إني تعبان.',
     'Juha said: every time I count, I forget that I am tired.'))]),

 ('Two Dinners', 'عزيمتين', [
  P(('جحا انعزم على عزيمتين بنفس الليلة.', 'Juha was invited to two dinners on the same night.'),
    ('ما عرف على وين يروح.', 'He did not know where to go.')),
  P(('راح عالأولى وأكل شوي.', 'He went to the first and ate a little.'),
    ('وبعدين راح عالتانية وأكل كمان.', 'And then he went to the second and ate again.')),
  P(('رجع عالبيت تعبان ومبطنه بتوجعه.',
     'He came home tired with his stomach hurting.'),
    ('قال: مرة وحدة أحسن من مرتين.',
     'He said: once is better than twice.'))]),

 ('The Neighbour Who Never Returns', 'الجار اللي ما بيرجّع', [
  P(('جار جحا كان يستعير ولا يرجع.', "Juha's neighbour would borrow and not return."),
    ('استعار المنشار، الحبل، والسلم.',
     'He borrowed the saw, the rope, and the ladder.')),
  P(('يوم إجا وقال: بدي حمارك.', 'One day he came and said: I want your donkey.'),
    ('قال جحا: الحمار مسافر.', 'Juha said: the donkey is travelling.')),
  P(('قال الجار: لوين؟', 'The neighbour said: where to?'),
    ('قال جحا: راح يجيب أغراضي من عندك.',
     'Juha said: it went to bring my things back from your house.'))]),

 ('The Sweetest Thing', 'أحلى إشي', [
  P(('سألوا جحا: شو أحلى إشي بالدنيا؟',
     'They asked Juha: what is the sweetest thing in the world?')),
  P(('قال: العسل.', 'He said: honey.'),
    ('قالوا: والصحة؟', 'They said: and health?')),
  P(('قال: الصحة مش إشي بالدنيا.', 'He said: health is not a thing in the world.'),
    ('الصحة هي الدنيا.', 'Health is the world.'))]),

 ('The Empty Purse', 'الجزدان الفاضي', [
  P(('حرامي فات على بيت جحا بالليل.', 'A thief entered Juha\'s house at night.'),
    ('صار يدور بالعتمة.', 'He started searching in the dark.')),
  P(('جحا صحي وصار يدور معه.', 'Juha woke up and started searching with him.'),
    ('الحرامي خاف وقال: شو بتعمل؟', 'The thief was afraid and said: what are you doing?')),
  P(('قال جحا: بساعدك.', 'Juha said: I am helping you.'),
    ('أنا بالنهار ما بلاقي إشي.', 'In the day I find nothing.'),
    ('بلكي بالليل بيبان.', 'Maybe at night something will show up.'))]),

 ('The Wise Fool', 'المجنون العاقل', [
  P(('ولاد الحي كانوا يضحكوا على جحا.', 'The neighbourhood children used to laugh at Juha.'),
    ('كانوا يعطوه قرش وقرشين، وهو ياخد الزغير.',
     'They would offer him one coin or two, and he would take the small one.')),
  P(('واحد قال له: خد الكبير، أحسن!',
     'Someone said to him: take the big one, it is better!'),
    ('قال جحا: لو أخدت الكبير، بيبطلوا يلعبوا.',
     'Juha said: if I took the big one, they would stop playing.')),
  P(('وقتها ما بضل آخذ ولا قرش.', 'Then I would not get a single coin.'))]),

 ('The Letter', 'المكتوب', [
  P(('واحد طلب من جحا يكتب له مكتوب.', 'Someone asked Juha to write him a letter.'),
    ('قال جحا: ما بقدر، إجري بتوجعني.',
     'Juha said: I cannot, my legs hurt.')),
  P(('قال الرجل: شو دخل إجريك بالكتابة؟',
     'The man said: what do your legs have to do with writing?')),
  P(('قال جحا: خطي محدا بيقراه غيري.',
     'Juha said: nobody can read my handwriting but me.'),
    ('فلازم أمشي لعندهم وأقراه.',
     'So I have to walk to them and read it.'))]),

 ('The Full Moon', 'القمر البدر', [
  P(('جحا وصاحبه قعدوا يتطلعوا عالقمر.',
     'Juha and his friend sat looking at the moon.'),
    ('صاحبه سأل: شو بيصير بالقمر القديم؟',
     'His friend asked: what happens to the old moon?')),
  P(('قال جحا: بيكسروه ويعملوا منه نجوم.',
     'Juha said: they break it and make stars out of it.'))]),

 ('Everyone Is a Little Right', 'كل واحد شوي على حق', [
  P(('بآخر عمره، سألوا جحا: شو تعلمت؟',
     'At the end of his life, they asked Juha: what did you learn?')),
  P(('قال: تعلمت إني ما بعرف كتير.',
     'He said: I learned that I do not know much.'),
    ('وتعلمت إن اللي بيضحك بيعيش أطول.',
     'And I learned that whoever laughs lives longer.')),
  P(('وتعلمت إن الحمار بيفهم أكتر من صاحبه.', 'And I learned that the donkey understands more than its owner.'))]),
]

if __name__ == '__main__':
    emit_book(BOOK_ID, BOOK_TITLE, 'beginner', CHAPTERS, unit='Tale', unit_ar='حكاية', shelf=1,
              meta={'work': 'the Juha / Nasreddin folk tales', 'author': 'traditional',
                    'year': 'medieval', 'status': 'public domain — folk material, no known author'})
