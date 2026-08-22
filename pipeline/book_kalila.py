#!/usr/bin/env python3
"""كليلة ودمنة — twenty tales, retold in spoken Palestinian, graded to intermediate.

Ibn al-Muqaffaʿ's 8th-century Arabic version of the Panchatantra, by way of Persian. Public domain
by age; these are retellings from the traditional plots, not a translation of any edition.

WHY IT BELONGS ON THIS SHELF. It is the Arabic narrative classic — an educated Arab meets Kalila
and Dimna at school, and the two jackals are as familiar as Aesop's fox is in English. It also
teaches something no other book here does: the FRAME. A character stops the action to tell a story
that argues a point, and the outer plot resumes changed. That is a real feature of how Arabic
narrative and, for that matter, Arabic conversation works.

TALES CHOSEN TO NOT DUPLICATE THE AESOP BOOK. No tortoise-and-hare, no lion-and-mouse, no crane.
What's here is the Lion and the Ox cycle that gives the book its two jackals, plus the nested
fables that are distinctive to this tradition.

LEVEL. Written near the intermediate story baseline (32.5 characters a sentence), like Sindbad and
unlike the existing Around the World at 49.5. Past-tense narrative with connectors and reported
speech, one clause at a time. The nested tales let dialogue carry a lot of the work, which keeps
sentences short without making the prose childish.

As everywhere in this project the PROSE is written by Claude (flagged NOT native-validated), but
every WORD's root, meaning and pronunciation is looked up in Maknuune by the ingest pipeline.

Run:  python3 pipeline/book_kalila.py    then ingest each chapter + build_app.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bookshelf import P, emit_book

BOOK_ID = 'kalila'
BOOK_TITLE = {'en': 'Kalila and Dimna', 'ar': 'كليلة ودمنة'}

# (english title, arabic title, [paragraph, ...])
CHAPTERS = [
 ('The Philosopher and the King', 'الفيلسوف والملك', [
  P(('كان في ملك اسمه دبشليم.', 'There was a king named Dabshalim.'),
    ('صار ظالم وما حدا بيقدر يحكي معه.',
     'He became unjust and nobody could speak with him.')),
  P(('فيلسوف اسمه بيدبا قرر يروح لعنده.',
     'A philosopher named Bidpai decided to go to him.'),
    ('أصحابه قالوا له: رح يقتلك.', 'His friends said to him: he will kill you.'),
    ('قال: بحكي معه بطريقة تانية.', 'He said: I will speak to him another way.')),
  P(('وقف قدام الملك وحكى له قصة حيوانات.',
     'He stood before the king and told him a story about animals.'),
    ('الملك سمع وما زعل، لأن القصة مش عنه.',
     'The king listened and was not angry, because the story was not about him.'),
    ('وبعدين فهم إنها عنه.', 'And then he understood that it was.'))]),

 ('Two Jackals at the Lion’s Gate', 'ابنا آوى عند باب الأسد', [
  P(('بغابة بعيدة، كان في أسد ملك.', 'In a far forest, there was a lion who was king.'),
    ('عنده خدم كتار من كل الحيوانات.', 'He had many servants from all the animals.')),
  P(('اتنين من ابن آوى كانوا قريبين من الباب.',
     'Two jackals were close to the gate.'),
    ('الأول اسمه كليلة والتاني اسمه دمنة.',
     'The first was called Kalila and the second Dimna.'),
    ('كليلة كان قنوع، ودمنة كان طموح.',
     'Kalila was content, and Dimna was ambitious.')),
  P(('قال دمنة: ليش نضل بعيدين عن الملك؟',
     'Dimna said: why do we stay far from the king?'),
    ('قال كليلة: اللي بيقرب من النار بينحرق.',
     'Kalila said: whoever comes near the fire gets burned.'),
    ('بس دمنة ما سمع منه.', 'But Dimna did not listen to him.'))]),

 ('The Ox Called Shatraba', 'الثور شتربة', [
  P(('بيوم، سمع الأسد صوت غريب وقوي.', 'One day, the lion heard a strange, powerful sound.'),
    ('خاف بس ما بده حدا يعرف إنه خايف.',
     'He was afraid but did not want anyone to know it.')),
  P(('دمنة لاحظ الخوف بعينيه.', 'Dimna noticed the fear in his eyes.'),
    ('قال: أنا بروح بشوف شو هاد الصوت.',
     'He said: I will go and see what this sound is.')),
  P(('الصوت كان لثور اسمه شتربة.', 'The sound belonged to an ox named Shatraba.'),
    ('كان ضايع عن أصحابه وبيخور من الجوع.',
     'He had been lost from his people and was bellowing from hunger.'),
    ('دمنة جابه عند الأسد.', 'Dimna brought him to the lion.'))]),

 ('The Friendship That Grew', 'الصداقة اللي كبرت', [
  P(('الأسد حب شتربة كتير.', 'The lion grew very fond of Shatraba.'),
    ('صاروا يقعدوا مع بعض كل يوم.', 'They began sitting together every day.'),
    ('الثور كان عاقل وبيحكي حكي حلو.', 'The ox was wise and spoke well.')),
  P(('دمنة زعل كتير من هالشغلة.', 'Dimna became very unhappy about this.'),
    ('قال: أنا جبته وهلق صار أقرب مني.',
     'He said: I brought him and now he is closer than me.')),
  P(('قال له كليلة: إنت عملتها بإيدك.',
     'Kalila said to him: you did this with your own hand.'),
    ('قال دمنة: واللي عملته بقدر أفكه.',
     'Dimna said: and what I made I can undo.'))]),

 ('The Monkey and the Carpenter', 'القرد والنجار', [
  P(('كليلة قال: خليني أحكي لك قصة.', 'Kalila said: let me tell you a story.'),
    ('قرد شاف نجار بيشق خشبة طويلة.',
     'A monkey watched a carpenter splitting a long plank.')),
  P(('النجار كان يحط إسفين بالشق.', 'The carpenter would put a wedge in the split.'),
    ('راح النجار ياكل، والقرد قعد مكانه.',
     'The carpenter went to eat, and the monkey sat in his place.')),
  P(('القرد شد الإسفين قبل ما يفهم شغله.',
     'The monkey pulled the wedge before he understood the work.'),
    ('الخشبة سكرت على إيديه ووجعته.', 'The plank closed on his hands and hurt him.'),
    ('اللي بيتدخل بشغل مش شغله بيتأذى.',
     'Whoever meddles in work that is not his gets hurt.'))]),

 ('Dimna Speaks to the Lion', 'دمنة بيحكي للأسد', [
  P(('راح دمنة عند الأسد وقعد ساكت.',
     'Dimna went to the lion and sat silent.'),
    ('الأسد سأله: مالك؟', 'The lion asked him: what is wrong with you?')),
  P(('قال دمنة: في إشي بس بخاف أحكيه.',
     'Dimna said: there is something, but I am afraid to say it.'),
    ('الملك قال: احكي.', 'The king said: speak.')),
  P(('قال: شتربة بيحكي مع الحيوانات عنك.',
     'He said: Shatraba talks to the animals about you.'),
    ('وبيقول إنه أقوى منك.', 'And he says he is stronger than you.'),
    ('الأسد سكت طويل وصار يفكر.',
     'The lion was silent a long time and began to think.'))]),

 ('Dimna Speaks to the Ox', 'دمنة بيحكي للثور', [
  P(('وبعدها راح دمنة عند شتربة.', 'And afterwards Dimna went to Shatraba.'),
    ('قال له: أنا صاحبك وبحذرك.',
     'He said to him: I am your friend and I am warning you.')),
  P(('الأسد بده يتخلص منك.', 'The lion wants to be rid of you.'),
    ('شتربة ما صدق بالأول.', 'Shatraba did not believe it at first.')),
  P(('قال دمنة: لما تشوفه، رح يكون شكله متغير.',
     'Dimna said: when you see him, his look will be changed.'),
    ('وهيك صار، لأن كل واحد فيهم صار خايف من التاني.',
     'And so it was, because each of them had become afraid of the other.'))]),

 ('The Fight', 'الخناقة', [
  P(('لما التقوا، كل واحد شاف الخوف بعين التاني.',
     'When they met, each saw the fear in the other’s eye.'),
    ('والخوف بيشبه العداوة كتير.', 'And fear looks a great deal like enmity.')),
  P(('انخانقوا بلا ما حدا منهم بده.',
     'They fought without either of them wanting to.'),
    ('الثور مات والأسد انجرح.', 'The ox died and the lion was wounded.')),
  P(('بعد شوي، الأسد قعد حزين.', 'A little later, the lion sat grieving.'),
    ('قال: خسرت أحسن صاحب عندي.',
     'He said: I have lost the best friend I had.'))]),

 ('The Trial of Dimna', 'محاكمة دمنة', [
  P(('الحيوانات حكت مع بعضها.', 'The animals talked among themselves.'),
    ('كلهم عرفوا مين اللي عمل هالشغلة.',
     'They all knew who had done this.')),
  P(('أم الأسد إجت وحكت لابنها كل إشي.',
     'The lion’s mother came and told her son everything.'),
    ('انحبس دمنة واتحاكم قدام الكل.',
     'Dimna was imprisoned and tried before them all.')),
  P(('قال دمنة: أنا حكيت كلام بس.',
     'Dimna said: I only spoke words.'),
    ('قال القاضي: والكلام بيقتل زي السيف.',
     'The judge said: and words kill like a sword.'),
    ('كليلة مات من الحزن على أخوه.',
     'Kalila died of grief over his brother.'))]),

 ('The Fox and the Drum', 'الثعلب والطبل', [
  P(('ثعلب جعان كان يمشي جنب شجرة.',
     'A hungry fox was walking beside a tree.'),
    ('الريح كانت تحرك غصن على طبل قديم.',
     'The wind was moving a branch against an old drum.')),
  P(('الصوت كان عالي ومخيف.', 'The sound was loud and frightening.'),
    ('قال الثعلب: هاد إشي كبير، أكيد فيه لحم كتير.',
     'The fox said: this is something big, surely there is much meat in it.')),
  P(('قرب وفتح الطبل بأسنانه.', 'He came near and opened the drum with his teeth.'),
    ('لقيه فاضي من جوا.', 'He found it empty inside.'),
    ('أكبر صوت بيطلع من أفرغ إشي.',
     'The biggest noise comes out of the emptiest thing.'))]),

 ('The Three Fish', 'السمكات التلات', [
  P(('بغدير بعيد، كان في تلات سمكات.', 'In a far pond, there were three fish.'),
    ('وحدة عاقلة، وحدة نص نص، وحدة غافلة.',
     'One wise, one middling, one heedless.')),
  P(('سمعوا صيادين بيحكوا: بكرا منرجع لهون.',
     'They heard fishermen saying: tomorrow we come back here.'),
    ('العاقلة طلعت من الغدير بنفس الليلة.',
     'The wise one left the pond that same night.')),
  P(('لما إجوا الصيادين، النص نص عملت حالها ميتة ونجت.',
     'When the fishermen came, the middling one played dead and escaped.'),
    ('والغافلة ضلت تسبح لحد ما انمسكت.',
     'And the heedless one kept swimming until it was caught.'),
    ('التفكير قبل الخطر أحسن من التفكير بعده.',
     'Thinking before danger is better than thinking after it.'))]),

 ('The Hare and the Lion', 'الأرنب والأسد', [
  P(('أسد كان ياكل من حيوانات الغابة كل يوم.',
     'A lion used to eat from the forest animals every day.'),
    ('اتفقوا يبعتوا له واحد كل يوم لحاله.',
     'They agreed to send him one each day by itself.')),
  P(('إجا دور أرنب زغير وذكي.', 'The turn came to a small, clever hare.'),
    ('راح متأخر عالقصد.', 'He went late on purpose.')),
  P(('قال للأسد: في أسد تاني بالغابة أخذ أكلي.',
     'He said to the lion: there is another lion in the forest who took my food.'),
    ('ودّاه على بير عميق وقال: هو تحت.',
     'He led him to a deep well and said: he is down there.')),
  P(('الأسد شاف خياله بالمي وحسبه عدو.',
     'The lion saw his reflection in the water and thought it an enemy.'),
    ('نط عليه وما طلع.', 'He jumped at it and never came out.'))]),

 ('The Ringdove and the Net', 'الحمامة المطوقة والشبكة', [
  P(('سرب حمام كان طاير ورا حبة.', 'A flock of doves was flying after some grain.'),
    ('نزلوا كلهم عالأرض ووقعوا بشبكة.',
     'They all landed on the ground and fell into a net.')),
  P(('كل حمامة صارت تشد لجهتها.', 'Each dove began pulling its own way.'),
    ('الشبكة ما تحركت أبداً.', 'The net did not move at all.')),
  P(('قالت الحمامة المطوقة: شدوا كلكم مع بعض.',
     'The ringdove said: all of you pull together.'),
    ('شدوا سوا وطاروا بالشبكة كلها.',
     'They pulled together and flew off with the whole net.'))]),

 ('The Mouse Who Cut the Net', 'الفار اللي قص الشبكة', [
  P(('طاروا عند فار صاحب الحمامة المطوقة.',
     'They flew to a mouse who was the ringdove’s friend.'),
    ('اسمه زيرك وبيسكن تحت الأرض.',
     'His name was Zirak and he lived under the ground.')),
  P(('بلش يقص الحبال، وبلش من حمامة تانية.',
     'He began cutting the ropes, and he began with another dove.'),
    ('سألته المطوقة: ليش مش مني أنا؟',
     'The ringdove asked him: why not from me first?')),
  P(('قال الفار: عشان ما يزعلوا منك.',
     'The mouse said: so that they do not resent you.'),
    ('لو فكيتك أول، بيشكوا إنك نسيتيهم.',
     'If I freed you first, they would suspect you had forgotten them.'),
    ('القائد بيتحرر آخر واحد.', 'A leader is freed last.'))]),

 ('The Four Friends', 'الأصحاب الأربعة', [
  P(('غراب شاف اللي صار وحب يصير صاحبهم.',
     'A crow saw what happened and wanted to be their friend.'),
    ('بالأول الفار خاف منه.', 'At first the mouse was afraid of him.'),
    ('قال: إنت بتاكل الفيران.', 'He said: you eat mice.')),
  P(('الغراب قال: بغير طبعي عشانك.',
     'The crow said: I will change my nature for you.'),
    ('صاروا أصحاب، وبعدين لحقتهم سلحفاة.',
     'They became friends, and later a tortoise joined them.')),
  P(('وبعدها إجت غزالة وصارت رابعتهم.',
     'And after that a gazelle came and became their fourth.'),
    ('عاشوا سوا جنب المي.', 'They lived together beside the water.'))]),

 ('The Gazelle in the Trap', 'الغزالة بالفخ', [
  P(('بيوم، الغزالة تأخرت وما رجعت.', 'One day, the gazelle was late and did not return.'),
    ('الغراب طار ودور عليها من فوق.',
     'The crow flew and searched for her from above.')),
  P(('لقاها واقعة بفخ صياد.', 'He found her caught in a hunter’s trap.'),
    ('رجع وجاب الفار، والفار قص الحبال.',
     'He went back and brought the mouse, and the mouse cut the ropes.')),
  P(('بس السلحفاة إجت مشي وهي بطيئة.',
     'But the tortoise came walking, and she is slow.'),
    ('الصياد وصل ومسك السلحفاة.', 'The hunter arrived and caught the tortoise.')),
  P(('عملوا خطة: الغزالة عملت حالها عرجا.',
     'They made a plan: the gazelle pretended to be lame.'),
    ('الصياد ركض وراها وترك السلحفاة.',
     'The hunter ran after her and left the tortoise.'),
    ('اللي عندهم أصحاب ما بيضيعوا.',
     'Those who have friends are not lost.'))]),

 ('The Owls and the Crows', 'البوم والغربان', [
  P(('كان في عداوة قديمة بين البوم والغربان.',
     'There was an old enmity between the owls and the crows.'),
    ('البوم بيشوفوا بالليل، والغربان بالنهار.',
     'Owls see at night, and crows by day.')),
  P(('البوم هجموا بالليل وقتلوا كتار.',
     'The owls attacked at night and killed many.'),
    ('الغربان اجتمعوا وما عرفوا شو يعملوا.',
     'The crows gathered and did not know what to do.')),
  P(('غراب كبير وعاقل قال: عندي فكرة.',
     'An old, wise crow said: I have an idea.'),
    ('بس لازم تنتفوا ريشي وترموني.',
     'But you must pluck my feathers and throw me out.'))]),

 ('The Crow Among the Owls', 'الغراب بين البوم', [
  P(('البوم لقوه مرمي ومجروح.', 'The owls found him thrown out and wounded.'),
    ('قال: الغربان عملوا فيّ هيك لأني حكيت عنكم منيح.',
     'He said: the crows did this to me because I spoke well of you.')),
  P(('صدقوه وأخذوه لمغارتهم.', 'They believed him and took him to their cave.'),
    ('ضل عندهم شهور وهو بيتفرج وبيعد.',
     'He stayed with them for months, watching and counting.')),
  P(('بيوم، جاب حطب ورماه عند باب المغارة.',
     'One day, he brought firewood and threw it at the cave door.'),
    ('وجاب الغربان وأشعلوا النار.',
     'And he brought the crows and they lit the fire.'),
    ('العدو اللي بتاخده لبيتك أخطر من اللي برا.',
     'The enemy you take into your house is more dangerous than the one outside.'))]),

 ('The Monkey and the Tortoise', 'القرد والسلحفاة', [
  P(('قرد وسلحفاة صاروا أصحاب عالشط.',
     'A monkey and a tortoise became friends on the shore.'),
    ('القرد كان يرمي لها تين من الشجرة.',
     'The monkey used to throw her figs from the tree.')),
  P(('مرت السلحفاة زعلت وقالت إنها مريضة.',
     'The tortoise’s wife was jealous and said she was ill.'),
    ('قالت: ما بيشفيني إلا قلب قرد.',
     'She said: nothing will cure me but a monkey’s heart.')),
  P(('السلحفاة حملت صاحبها عالبحر وهي حزينة.',
     'The tortoise carried her friend out to sea, and she was sad.'),
    ('بالنص، ما قدرت تسكت وحكت له.',
     'Halfway, she could not keep silent and told him.')),
  P(('قال القرد: ليش ما قلتي من الأول؟',
     'The monkey said: why did you not say so at the start?'),
    ('قلبي متروك عالشجرة، خليني آخده.',
     'My heart is left on the tree; let me fetch it.'),
    ('رجعوا، وطلع القرد عالشجرة وما نزل.',
     'They went back, and the monkey climbed the tree and did not come down.'))]),

 ('The Ascetic and the Mongoose', 'الناسك وابن عرس', [
  P(('ناسك عنده ولد زغير وابن عرس ربّاه.',
     'An ascetic had a small child and a mongoose he had raised.'),
    ('كان يثق فيه زي ما بيثق بولد.',
     'He trusted it as he would trust a child.')),
  P(('بيوم، ترك الولد نايم وطلع.',
     'One day, he left the child sleeping and went out.'),
    ('لما رجع، لقى ابن عرس عند الباب وتمه دم.',
     'When he came back, he found the mongoose at the door with blood on its mouth.')),
  P(('ضربه بسرعة وقتله.', 'He struck it quickly and killed it.'),
    ('وبعدين فات، ولقى الولد نايم بالسلامة.',
     'And then he went in, and found the child sleeping safely.'),
    ('وجنبه حية كبيرة مقتولة.', 'And beside him a big snake, killed.')),
  P(('قعد الناسك يبكي وما نفع البكا.',
     'The ascetic sat weeping and the weeping was no use.'),
    ('اللي بيحكم بسرعة بيندم على مهل.',
     'Whoever judges quickly repents slowly.'))]),
]

if __name__ == '__main__':
    emit_book(BOOK_ID, BOOK_TITLE, 'intermediate', CHAPTERS, unit='Tale', unit_ar='حكاية', shelf=12,
              meta={'work': 'كليلة ودمنة', 'author': 'Ibn al-Muqaffaʿ, from the Panchatantra',
                    'year': '8th century', 'status': 'public domain — medieval'})
