#!/usr/bin/env python3
"""شرلوك هولمز — ten stories, retold in spoken Palestinian, graded to advanced.

Arthur Conan Doyle's Holmes stories are all in the US public domain — the last collection entered
in January 2023. These are retellings from the plots, not translations of any edition.

WHY HOLMES IS THE RIGHT ADVANCED BOOK. Phase 6's milestone is being warm, funny and diplomatic —
following what people mean rather than only what they say. Holmes is almost entirely DIALOGUE, and
the plot turns on inference expressed in speech: a client leaves something out, Holmes notices the
gap, Watson misses it, Holmes explains. Following that in Arabic is exactly the B2 skill, and it
comes with the hedging and qualifying language that phase is about — يمكن، بالغالب، ما بستبعد،
اللي بيدل على، معناها.

Every story runs three chapters — the client, the investigation, the answer — so a reader finishes
something in one sitting. The ten are ordered to end on المشكلة الأخيرة and البيت الفارغ, which
gives the collection an arc instead of being ten unrelated puzzles.

LEVEL. Written near the advanced short-story baseline (34 characters a sentence). Longer clauses
than the intermediate books, real subordination, and reported speech carrying most of the weight.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated), but
every WORD's root, meaning and pronunciation is looked up in Maknuune by the ingest pipeline.

Run:  python3 pipeline/book_holmes.py    then ingest each chapter + build_app.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bookshelf import P, emit_book

BOOK_ID = 'holmes'
BOOK_TITLE = {'en': 'Sherlock Holmes: Ten Stories', 'ar': 'شرلوك هولمز: عشر قصص'}

# (english title, arabic title, [paragraph, ...])
CHAPTERS = [
 # ---------------- A Scandal in Bohemia ----------------
 ('The King Who Would Not Say His Name', 'الملك اللي ما بده يقول اسمه', [
  P(('كنت قاعد عند هولمز بشارع بيكر لما دق الجرس.',
     'I was sitting with Holmes on Baker Street when the bell rang.'),
    ('قال هولمز بلا ما يتطلع:', 'Holmes said without looking up:'),
    ('زبون، وغني، وبده يخبي اسمه.', 'A client, wealthy, and wanting to hide his name.')),
  P(('سألته: من وين عرفت كل هاد؟', 'I asked him: how did you know all that?'),
    ('قال: ورق المكتوب اللي وصلني غالي.', 'He said: the paper of the letter that reached me is costly.'),
    ('والخط مش إنجليزي.', 'And the hand is not English.'),
    ('واللي بده يخبي اسمه بيكتب مكتوب قبل ما يجي.',
     'And a man who wants to hide his name writes a letter before he comes.')),
  P(('فات رجل طويل ولابس قناع على نص وجهه.',
     'A tall man came in wearing a mask over half his face.'),
    ('قال: بتقدروا تنادوني الكونت فون كرام.',
     'He said: you may call me Count von Kramm.'),
    ('قال هولمز بهدوء: أهلاً فيك يا صاحب الجلالة.',
     'Holmes said calmly: welcome, Your Majesty.'))]),

 ('A Photograph in Someone Else’s Hands', 'صورة بإيد غيره', [
  P(('الملك حكى إنه كان يعرف مغنية اسمها آيرين آدلر.',
     'The king explained that he had known a singer named Irene Adler.'),
    ('وعندها صورة للتنين مع بعض.',
     'And she has a photograph of the two of them together.')),
  P(('قال: أنا رح أتزوج، وهاي الصورة بتخرب كل إشي.',
     'He said: I am to be married, and this photograph ruins everything.'),
    ('جربت أشتريها، وجربت أسرقها، وما نفع.',
     'I tried to buy it, and I tried to steal it, and nothing worked.')),
  P(('سأل هولمز: وهي، بدها مصاري؟',
     'Holmes asked: and she, does she want money?'),
    ('قال الملك: لأ. هي بدها بس تمنعني.',
     'The king said: no. She only wants to stop me.'),
    ('قال هولمز: يعني احنا قدام واحدة بتفكر منيح.',
     'Holmes said: then we are facing a woman who thinks well.'))]),

 ('The Woman Who Was Ahead of Him', 'المرا اللي سبقته', [
  P(('هولمز تنكر كخوري مجروح وعمل مشكلة قدام بيتها.',
     'Holmes disguised himself as an injured clergyman and staged a scene at her door.'),
    ('حملوه لجوا.', 'They carried him in.'),
    ('وأنا رميت دخان من الشباك وصرخت: حريقة!', 'And I threw smoke through the window and shouted: fire!')),
  P(('قال لي بعدها: أي واحد بينقذ أغلى إشي عنده الأول.',
     'He said to me afterwards: anyone saves the most precious thing they own first.'),
    ('وهي راحت عالصورة من غير ما تفكر.',
     'And she went to the photograph without thinking.')),
  P(('الصبح رجعنا، ولقينا البيت فاضي.',
     'In the morning we returned, and found the house empty.'),
    ('كانت تركت مكتوب: عرفت إنك إنت، وسافرت.',
     'She had left a letter: I knew it was you, and I have gone.'),
    ('من يومها، هولمز بيسميها المرا، مش باسمها.',
     'From that day, Holmes calls her the woman, not by her name.'))]),

 # ---------------- The Red-Headed League ----------------
 ('A Job for Red-Haired Men Only', 'شغلة لأصحاب الشعر الأحمر بس', [
  P(('إجا زبون شعره أحمر وحكى قصة غريبة.',
     'A client with red hair came and told a strange story.'),
    ('قال: لقيت إعلان بتوظيف لأصحاب الشعر الأحمر بس.',
     'He said: I found an advertisement hiring only red-haired men.')),
  P(('الشغلة كانت إني أنسخ كتاب بمكتب.', 'The work was copying a book in an office.'),
    ('أربع ساعات كل يوم.', 'Four hours every day.'),
    ('المصاري كانت كويسة والشغل ما فيه إشي.',
     'The money was good and the work was nothing.')),
  P(('وبعد تمن أسابيع، لقيت المكتب مسكر وورقة عالباب.',
     'And after eight weeks, I found the office shut and a note on the door.'),
    ('مكتوب عليها: العصبة انحلت.', 'It read: the league is dissolved.'))]),

 ('Who Wanted Him Out of the Shop', 'مين بده يطلعه من الدكان', [
  P(('سأله هولمز: مين قال لك عن الإعلان؟',
     'Holmes asked him: who told you about the advertisement?'),
    ('قال: مساعدي بالدكان، شاب بيشتغل عندي بنص أجرة.',
     'He said: my assistant at the shop, a young man who works for half wages.')),
  P(('قال هولمز: وهو شو بيعمل لما بتكون برا؟',
     'Holmes said: and what does he do while you are out?'),
    ('قال الزبون: بينزل عالقبو ويصور، هوايته.',
     'The client said: he goes down to the cellar and takes photographs, his hobby.')),
  P(('بعد ما راح، قال لي هولمز:', 'After he left, Holmes said to me:'),
    ('شاب بيرضى بنص أجرة عنده سبب.', 'A young man content with half wages has a reason.'),
    ('وأربع ساعات كل يوم هي وقت، مش شغل.',
     'And four hours a day is time, not work.'))]),

 ('Under the Bank', 'تحت البنك', [
  P(('رحنا عالدكان وهولمز دق عالبلاط بعصايته.',
     'We went to the shop and Holmes tapped the pavement with his stick.'),
    ('وبعدين لف عالشارع اللي ورا ولقى بنك.',
     'And then he went round to the street behind and found a bank.')),
  P(('قال: القبو اللي بيصور فيه بيمشي بهالاتجاه.',
     'He said: the cellar he photographs in runs in that direction.'),
    ('وركبتين بنطلونه كانوا مغبرين ومهترين.',
     'And the knees of his trousers were dusty and worn.')),
  P(('بالليل، قعدنا بالعتمة بقبو البنك ننتظر.',
     'At night, we sat in the dark in the bank cellar and waited.'),
    ('طلعت إيد من بين حجرتين بالأرض.',
     'A hand came up between two stones in the floor.'),
    ('لستراد مسكه، وهولمز قال: العصبة كانت لتشغلك بس.',
     'Lestrade seized him, and Holmes said: the league was only to keep you busy.'))]),

 # ---------------- The Speckled Band ----------------
 ('A Woman Who Came Before Dawn', 'مرا إجت قبل الفجر', [
  P(('بالسادسة الصبح، إجت وحدة مرتجفة عالبيت.',
     'At six in the morning, a trembling woman came to the house.'),
    ('كان شعرها فيه شيب وهي لسا شابة.',
     'Her hair had grey in it and she was still young.')),
  P(('قالت: أختي ماتت قبل سنتين بشكل ما حدا فهمه.',
     'She said: my sister died two years ago in a way nobody understood.'),
    ('آخر إشي قالته: العصابة! العصابة المرقطة!',
     'The last thing she said was: the band! the speckled band!')),
  P(('قالت: وهلق أنا انتقلت لأوضتها.', 'She said: and now I have moved into her room.'),
    ('وصرت بسمع صفير بالليل.', 'And I have begun hearing a whistle at night.'),
    ('هولمز اتطلع فيها وقال: زوج أمك بيضربك؟',
     'Holmes looked at her and said: your stepfather beats you?'),
    ('كان في آثار أصابع زرقا على إيدها.',
     'There were blue finger-marks on her wrist.'))]),

 ('The Room That Was Changed', 'الأوضة اللي تغيرت', [
  P(('رحنا عالبيت وقت ما زوج أمها كان برا.',
     'We went to the house while her stepfather was out.'),
    ('هولمز فحص الأوضة شبر شبر.',
     'Holmes examined the room inch by inch.')),
  P(('قال: في حبل جرس معلق، بس مربوط بالهوا.',
     'He said: there is a bell-rope hanging, but it is fastened to nothing.'),
    ('والتخت مثبت بالأرض، ما بينحرك.',
     'And the bed is fixed to the floor, it does not move.')),
  P(('وفي فتحة تهوية بتفتح على أوضة زوج أمك.',
     'And there is a ventilator opening onto your stepfather’s room.'),
    ('سألت: يعني شو معناها؟', 'She asked: so what does it mean?'),
    ('قال هولمز: معناها إن إشي بينزل من هناك لهون.',
     'Holmes said: it means that something comes down from there to here.'))]),

 ('The Whistle in the Dark', 'الصفير بالعتمة', [
  P(('قعدنا بالأوضة بالعتمة وما حكينا ولا كلمة.',
     'We sat in the room in the dark and did not say a word.'),
    ('ساعات مرقت وأنا بسمع دقات قلبي.',
     'Hours passed and I could hear my own heartbeat.')),
  P(('فجأة، سمعنا صوت خفيف زي مي بتغلي.',
     'Suddenly, we heard a light sound like water boiling.'),
    ('هولمز أشعل الضوء وضرب الحبل بعصايته.',
     'Holmes struck a light and beat the rope with his stick.')),
  P(('سمعنا صرخة من الأوضة التانية.',
     'We heard a scream from the other room.'),
    ('لقينا زوج أمها ميت والحية ملفوفة على راسه.',
     'We found her stepfather dead with the snake coiled on his head.'),
    ('قال هولمز: كان بده وراثتها، والحية رجعت عليه.',
     'Holmes said: he wanted her inheritance, and the snake turned back on him.'))]),

 # ---------------- The Blue Carbuncle ----------------
 ('A Hat and a Goose', 'قبعة ووزة', [
  P(('بعد عيد الميلاد، جاب لنا الشرطي قبعة قديمة ووزة.',
     'After Christmas, the constable brought us an old hat and a goose.'),
    ('قال: واحد وقعوا منه بخناقة وهرب.',
     'He said: a man dropped them in a scuffle and ran off.')),
  P(('هولمز قلب القبعة وقال: صاحبها كان غني وصار فقير.',
     'Holmes turned the hat over and said: its owner was rich and became poor.'),
    ('وهو ذكي، ومرته بطلت تحبه.',
     'And he is clever, and his wife has stopped loving him.')),
  P(('سألته: ومن وين المرا؟', 'I asked him: and where does the wife come from?'),
    ('قال: القبعة ما انكنست من أسابيع.',
     'He said: the hat has not been brushed in weeks.'),
    ('المرا اللي بتحب زوجها ما بتتركه يطلع هيك.',
     'A woman who loves her husband does not let him go out like that.'))]),

 ('The Stone in the Bird', 'الحجر جوا الطير', [
  P(('السيدة هدسون فتحت الوزة عشان تطبخها.',
     'Mrs Hudson opened the goose to cook it.'),
    ('لقت جواتها حجر أزرق بيلمع.',
     'She found inside it a blue stone that shone.')),
  P(('كانت ياقوتة مسروقة من فندق كبير.',
     'It was a jewel stolen from a great hotel.'),
    ('والشرطة كانت حابسة سباك ومتهمينه.',
     'And the police were holding a plumber and accusing him.')),
  P(('قال هولمز: ما بحب أحد ينحبس على غلط.',
     'Holmes said: I do not like anyone imprisoned wrongly.'),
    ('وحطينا إعلان: لقينا وزة وقبعة.',
     'And we placed an advertisement: goose and hat found.'))]),

 ('The Man Who Came for His Goose', 'الرجل اللي إجا يدور على وزته', [
  P(('بالليل، إجا رجل نحيف ومتوتر.',
     'At night, a thin, nervous man came.'),
    ('لما شاف الحجر عالطاولة، وقع على الكرسي.',
     'When he saw the stone on the table, he collapsed into the chair.')),
  P(('حكى كل إشي: هو اللي أخذها وخبّاها بالوزة.',
     'He told everything: he had taken it and hidden it in the goose.'),
    ('وبعدين اختلطت الوزة بوزة تانية وضاعت منه.',
     'And then the goose got mixed with another and he lost it.')),
  P(('هولمز فتح الباب وقال له: روح.',
     'Holmes opened the door and said to him: go.'),
    ('قلت له: هيك بتخلي مجرم يهرب.',
     'I said to him: this way you let a criminal escape.'),
    ('قال: أنا مش شرطة. وهاد الرجل ما رح يعيدها.',
     'He said: I am not the police. And this man will not do it again.'))]),

 # ---------------- The Man with the Twisted Lip ----------------
 ('A Wife Who Saw Her Husband', 'مرا شافت زوجها', [
  P(('سيدة إجت وقالت: زوجي اختفى من تلات أيام.',
     'A lady came and said: my husband disappeared three days ago.'),
    ('وأنا شفته من شباك بيت قديم بآخر المدينة.',
     'And I saw him at the window of an old house at the end of the city.')),
  P(('قالت: صرخت باسمه، وإيد سحبته من ورا.',
     'She said: I called his name, and a hand pulled him back.'),
    ('لما فتوا الشرطة، ما لقوا غير شحاد بشفة ملتوية.',
     'When the police went in, they found only a beggar with a twisted lip.')),
  P(('وكانوا تياب زوجي بالأوضة، ودم عالشباك.',
     'And my husband’s clothes were in the room, and blood on the window.'),
    ('هولمز سألها: كان يبعت لك مصاري بانتظام؟',
     'Holmes asked her: did he send you money regularly?'),
    ('قالت: كل أسبوع، وما كنا نعرف من وين.',
     'She said: every week, and we never knew from where.'))]),

 ('The Beggar in the Cell', 'الشحاد بالزنزانة', [
  P(('هولمز قعد طول الليل على الأرض بيفكر.',
     'Holmes sat all night on the floor thinking.'),
    ('الصبح، ضحك فجأة وقال: يالله عالحبس.',
     'In the morning, he laughed suddenly and said: come, to the jail.')),
  P(('كان الشحاد نايم بالزنزانة.', 'The beggar was asleep in the cell.'),
    ('هولمز جاب إسفنجة مبلولة ومسح وجهه.',
     'Holmes brought a wet sponge and washed his face.')),
  P(('الشفة الملتوية راحت مع المي.',
     'The twisted lip came away with the water.'),
    ('وطلع تحتها وجه الزوج المفقود.',
     'And under it appeared the face of the missing husband.'))]),

 ('Why He Did Not Come Home', 'ليش ما رجع عالبيت', [
  P(('قال الرجل: كنت صحفي، وجربت الشحادة مرة لمقال.',
     'The man said: I was a journalist, and I tried begging once for an article.')),
  P(('بيوم واحد، جمعت أكتر من راتب أسبوع.',
     'In one day, I collected more than a week’s salary.'),
    ('وما قدرت أرجع عن هالشغلة.',
     'And I could not go back from that.')),
  P(('قال: مرتي بتحسبني تاجر محترم.',
     'He said: my wife thinks me a respectable merchant.'),
    ('هولمز قال: إذا وقفت من اليوم، الشرطة بتنسى.',
     'Holmes said: if you stop today, the police will forget.'),
    ('وبعد ما طلعنا، قال لي: مش كل سر جريمة.',
     'And after we left, he said to me: not every secret is a crime.'))]),

 # ---------------- Silver Blaze ----------------
 ('The Horse That Disappeared', 'الحصان اللي اختفى', [
  P(('حصان سباق غالي اختفى، والمدرب انلقى ميت.',
     'A valuable racehorse disappeared, and the trainer was found dead.'),
    ('الشرطة كانت ماسكة واحد غريب شافوه بالليل.',
     'The police were holding a stranger who had been seen at night.')),
  P(('رحنا عالمزرعة وهولمز قعد يسأل عن العشا.',
     'We went to the farm and Holmes began asking about the supper.'),
    ('قال: العشا كان لحمة بالكاري، صح؟',
     'He said: the supper was curried mutton, correct?')),
  P(('لستراد قال: وشو دخل الأكل بالموضوع؟',
     'Lestrade said: and what has the food to do with it?'),
    ('قال هولمز: الكاري بيخبي طعم أي إشي بتحطه فيه.',
     'Holmes said: curry hides the taste of anything you put in it.'))]),

 ('The Dog in the Night', 'الكلب بالليل', [
  P(('قال هولمز للمفتش: انتبه لتصرف الكلب هديك الليلة.',
     'Holmes said to the inspector: note the dog’s behaviour that night.'),
    ('قال لستراد: الكلب ما عمل إشي هديك الليلة.',
     'Lestrade said: the dog did nothing that night.')),
  P(('قال هولمز: وهاي بالزبط الشغلة الغريبة.',
     'Holmes said: and that is exactly the curious thing.'),
    ('في كلب بالإسطبل، وما نبح على اللي أخذ الحصان.',
     'There is a dog in the stable, and it did not bark at whoever took the horse.')),
  P(('يعني الكلب كان بيعرفه منيح.',
     'Which means the dog knew him well.'),
    ('يعني اللي أخذ الحصان من أهل البيت.',
     'Which means whoever took the horse was of the household.'))]),

 ('What the Trainer Was Doing', 'شو كان بده يعمل المدرب', [
  P(('هولمز لقى الحصان مخبى عند جار وشكله متغير.',
     'Holmes found the horse hidden at a neighbour’s, its appearance altered.'),
    ('ورجعه للسباق وربح.', 'And he returned it to the race and it won.')),
  P(('وبعدين شرح: المدرب هو اللي أخذ الحصان.',
     'And then he explained: the trainer was the one who took the horse.'),
    ('كان بده يجرحه جرح بسيط عشان يخسر السباق.',
     'He meant to give it a small cut so it would lose the race.')),
  P(('حمل عليه سكينة دقيقة.', 'He carried a fine knife on him.'),
    ('من النوع اللي بيستعمله الجراح.', 'The kind a surgeon uses.'),
    ('بس الحصان رفسه بالراس ومات على طول.',
     'But the horse kicked him in the head and he died at once.'),
    ('قال هولمز: أحياناً ما في مجرم، في بس واحد غلطان.',
     'Holmes said: sometimes there is no criminal, only a man who was wrong.'))]),

 # ---------------- The Six Napoleons ----------------
 ('Someone Is Breaking Statues', 'في حدا بيكسر تماثيل', [
  P(('لستراد إجا وقال: في مجنون بيكسر تماثيل نابليون.',
     'Lestrade came and said: there is a madman breaking Napoleon statues.'),
    ('كسر تلاتة بمحلات مختلفة، وما سرق ولا إشي.',
     'He broke three in different places, and stole nothing.')),
  P(('قال هولمز: وبيكسرهم وين؟ جوا ولا برا؟',
     'Holmes said: and where does he break them? Inside or outside?'),
    ('قال لستراد: دايماً برا، تحت ضوء الشارع.',
     'Lestrade said: always outside, under the street lamp.')),
  P(('قال هولمز: يعني بده يشوف.',
     'Holmes said: which means he needs to see.'),
    ('واللي بده يشوف، عم يدور على إشي.', 'And a man who needs to see is searching for something.'),
    ('مش عم ينفس عن غضب.', 'He is not venting rage.'))]),

 ('All From the Same Mould', 'كلهم من نفس القالب', [
  P(('هولمز تتبع التماثيل لحد المصنع اللي عملهم.',
     'Holmes traced the statues to the workshop that made them.'),
    ('طلع إنهم ستة، انصبوا كلهم بنفس اليوم.',
     'It turned out there were six, all cast on the same day.')),
  P(('وبنفس اليوم، انسرقت لؤلؤة كبيرة.', 'And on that same day, a great pearl was stolen.'),
    ('والسرقة صارت قريب من المصنع.', 'And the theft happened near the workshop.'),
    ('وواحد من عمال المصنع كان مطلوب وقتها.',
     'And one of the workshop’s men was wanted at the time.')),
  P(('قال هولمز: خبّى اللؤلؤة بواحد منهم وهو طري.',
     'Holmes said: he hid the pearl in one of them while it was soft.'),
    ('وهلق بيكسرهم واحد واحد لحد ما يلاقيها.',
     'And now he breaks them one by one until he finds it.'))]),

 ('The Last Statue', 'آخر تمثال', [
  P(('هولمز اشترى آخر تمثال بنفسه ورجع فيه عالبيت.',
     'Holmes bought the last statue himself and brought it home.'),
    ('حطه عالطاولة قدام لستراد وأنا.',
     'He set it on the table before Lestrade and me.')),
  P(('ضربه بالمطرقة ضربة وحدة.',
     'He struck it with the hammer once.'),
    ('بين قطع الجبس، كان في لؤلؤة كبيرة.', 'Among the pieces of plaster was a big pearl.'),
    ('كانت زي بيضة حمامة.', 'It was like a pigeon’s egg.')),
  P(('لستراد سكت شوي وبعدين صفق.',
     'Lestrade was silent a moment and then applauded.'),
    ('قال: احنا فخورين فيك.', 'He said: we are proud of you.'),
    ('وشفت هولمز يحمر وجهه لأول مرة.',
     'And I saw Holmes blush for the first time.'))]),

 # ---------------- The Dancing Men ----------------
 ('Little Men on the Paper', 'رجال زغار عالورقة', [
  P(('زبون جاب ورقة عليها رسمات رجال بيرقصوا.',
     'A client brought a paper with drawings of dancing men.'),
    ('قال: مرتي شافتها وأغمى عليها.',
     'He said: my wife saw it and fainted.')),
  P(('قال: هي أمريكية، وقبل الجواز طلبت مني إشي واحد.',
     'He said: she is American, and before the marriage she asked me one thing.'),
    ('إني ما أسألها أبداً عن حياتها قبل ما تعرفني.',
     'That I never ask her about her life before she knew me.')),
  P(('هولمز اتطلع بالرسمات طويل.',
     'Holmes looked at the drawings a long time.'),
    ('قال: هاي مش رسمات ولاد. هاي كتابة.',
     'He said: these are not children’s drawings. This is writing.'))]),

 ('Counting the Letters', 'عد الحروف', [
  P(('قال هولمز: بأي لغة، في حرف بيتكرر أكتر من غيره.',
     'Holmes said: in any language, one letter recurs more than the others.'),
    ('بالإنجليزي، هو حرف الـ E.', 'In English, it is the letter E.')),
  P(('عد الرجال ولقى واحد بيتكرر كتير.',
     'He counted the figures and found one recurring often.'),
    ('وبعدين لقى كلمة قصيرة بأربع حروف بينهم E مرتين.',
     'And then he found a short four-letter word with E twice in it.')),
  P(('كانت اسم مرت الزبون.', 'It was the client’s wife’s name.'),
    ('ومن هون، فك الباقي حرف حرف.',
     'And from there, he unravelled the rest letter by letter.'),
    ('آخر رسالة كانت: استعدي للموت.',
     'The last message read: prepare to die.'))]),

 ('Too Late by One Day', 'تأخرنا يوم', [
  P(('ركبنا أول قطار الصبح، بس كنا متأخرين.',
     'We took the first train in the morning, but we were late.'),
    ('الزبون كان ميت ومرته مجروحة جروح صعبة.',
     'The client was dead and his wife badly wounded.')),
  P(('الشرطة حسبت إنها هي اللي عملتها.',
     'The police assumed she had done it.'),
    ('هولمز قال: في تلات رصاصات، مش تنتين.',
     'Holmes said: there are three shots, not two.')),
  P(('كتب رسالة بنفس رسم الرجال وبعتها لبيت قريب.',
     'He wrote a message in the same dancing figures and sent it to a nearby house.'),
    ('اللي إجا كان الرجل اللي كان يلاحقها من أمريكا.',
     'The man who came was the one who had been pursuing her from America.'),
    ('قال هولمز: استعملت لغته، فما شك إنها مش منها.',
     'Holmes said: I used his own language, so he did not doubt it.'))]),

 # ---------------- The Final Problem ----------------
 ('The Man Behind Everything', 'الرجل اللي ورا كل إشي', [
  P(('بليلة، إجا هولمز عالبيت ووجهه شاحب.',
     'One night, Holmes came to the house with a pale face.'),
    ('قال: سمعت باسم موريارتي من قبل؟',
     'He said: have you heard the name Moriarty before?')),
  P(('قلت: لأ.', 'I said: no.'),
    ('قال: وهاي عظمته.', 'He said: and that is his greatness.'),
    ('محدا بيعرفه، وهو ورا نص الجرائم بلندن.', 'Nobody knows him, and he is behind half the crimes in London.')),
  P(('قال: هو زي عنكبوت بنص شبكة.',
     'He said: he is like a spider in the middle of a web.'),
    ('ما بيتحرك، بس بيحس بكل خيط بينهز.',
     'He does not move, but he feels every thread that trembles.'),
    ('وهلق، لأول مرة، الشبكة كلها بإيدي.',
     'And now, for the first time, the whole web is in my hand.'))]),

 ('Across the Water', 'عبر البحر', [
  P(('سافرنا لأوروبا وهولمز كان يتطلع ورا كل شوي.',
     'We travelled to Europe and Holmes kept looking behind him.'),
    ('بكل محطة كان يغير الخطة.',
     'At every station he changed the plan.')),
  P(('قال لي: أنا مش خايف على حالي.',
     'He said to me: I am not afraid for myself.'),
    ('لو انتهت هالقصة، بكون عملت أهم إشي بحياتي.',
     'If this ends, I will have done the most important thing of my life.')),
  P(('وصلنا سويسرا، ومشينا لعند شلال كبير.',
     'We reached Switzerland, and walked to a great waterfall.'),
    ('الصوت كان عالي والبخار طالع من تحت.',
     'The sound was loud and the spray rose from below.'))]),

 ('The Waterfall', 'الشلال', [
  P(('إجا ولد وقال إن في سيدة مريضة بالفندق.',
     'A boy came and said a lady was ill at the hotel.'),
    ('رجعت راكض، ولقيت إنه ما في ولا سيدة.',
     'I ran back, and found there was no lady at all.')),
  P(('لما رجعت عالشلال، ما كان في حدا.',
     'When I got back to the waterfall, there was nobody.'),
    ('كان في آثار إجرين رايحة، وما في راجعة.',
     'There were footprints going, and none coming back.')),
  P(('لقيت مكتوب على حجر، بخط هولمز.',
     'I found a letter on a stone, in Holmes’s hand.'),
    ('كتب: قول للناس إني عرفت إن هاي رح تكون النهاية.',
     'He wrote: tell them I knew this would be the end.'),
    ('وقفت هناك لحالي وأنا ما بقدر أفهم.',
     'I stood there alone unable to understand.'))]),

 # ---------------- The Empty House ----------------
 ('Three Years Later', 'بعد تلات سنين', [
  P(('عشت تلات سنين وأنا بحسبه ميت.',
     'I lived three years believing him dead.'),
    ('كنت لسا بقرا الجرايد بعينه.',
     'I still read the newspapers with his eye.')),
  P(('بيوم، اصطدمت بعجوز بيبيع كتب بالشارع.',
     'One day, I bumped into an old bookseller in the street.'),
    ('وقعت كتبه وأنا اعتذرت وكملت.',
     'His books fell and I apologised and walked on.')),
  P(('بعد ساعة، إجا العجوز عالعيادة.',
     'An hour later, the old man came to the surgery.'),
    ('لفيت، ووقفت قدامي شرلوك هولمز.',
     'I turned, and Sherlock Holmes was standing before me.'),
    ('وهاي المرة الوحيدة بحياتي اللي أغمى عليّ.',
     'And that is the only time in my life I fainted.'))]),

 ('How He Lived', 'كيف عاش', [
  P(('قال: أنا وموريارتي وقفنا على الحافة.',
     'He said: Moriarty and I stood at the edge.'),
    ('كنت بعرف مصارعة، وهو ما كان بيعرف.',
     'I knew a wrestling art, and he did not.')),
  P(('وقع هو، وأنا ضلّيت.', 'He fell, and I remained.'),
    ('وقتها فكرت: إذا الناس حسبوني ميت، بضل عايش.',
     'Then I thought: if people believe me dead, I stay alive.')),
  P(('لأنه كان في اتنين من رجاله لسا برا.',
     'Because two of his men were still at large.'),
    ('سافرت وغيّرت اسمي وضلّيت أراقب.',
     'I travelled and changed my name and kept watching.'),
    ('قلت له: كان بقدر أسكت لو قلت لي.',
     'I said to him: I could have kept silent if you had told me.'))]),

 ('The Empty House', 'البيت الفارغ', [
  P(('هديك الليلة، أخذني على بيت فاضي.', 'That night, he took me to an empty house.'),
    ('كان قدام بيتنا القديم بالزبط.', 'It faced our old rooms exactly.'),
    ('كان بالشباك خيال راسه، من شمع.',
     'In the window was the shadow of his head, made of wax.')),
  P(('قال: السيدة هدسون بتحركه كل ربع ساعة.',
     'He said: Mrs Hudson moves it every quarter of an hour.'),
    ('ومنستنى اللي رح يرمي عليه.',
     'And we wait for the one who will shoot at it.')),
  P(('بعد ساعتين، فات رجل وفتح شباك بهدوء.',
     'After two hours, a man came in and opened a window quietly.'),
    ('صوّب على الخيال وضرب.',
     'He aimed at the shadow and fired.'),
    ('هولمز نط عليه، وأنا أشعلت الضوء.',
     'Holmes leapt on him, and I struck a light.')),
  P(('قال هولمز وهو ماسكه: آخر خيط بالشبكة.',
     'Holmes said, holding him: the last thread in the web.'),
    ('وبعدين التفت عليّ وقال: يالله يا واطسون.',
     'And then he turned to me and said: come, Watson.'),
    ('رجعنا على بيكر ستريت، وكل إشي كان زي ما تركناه.',
     'We went back to Baker Street, and everything was as we had left it.'))]),
]

if __name__ == '__main__':
    emit_book(BOOK_ID, BOOK_TITLE, 'advanced', CHAPTERS, shelf=20,
              meta={'work': 'the Sherlock Holmes stories', 'author': 'Arthur Conan Doyle',
                    'year': '1891–1904',
                    'status': 'public domain — all Holmes entered the US public domain by 2023'})
