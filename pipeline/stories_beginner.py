#!/usr/bin/env python3
"""Beginner short stories — emit one texts/story-beg-NN.json per story.

Written in simple spoken Palestinian (present/habitual, everyday topics). Not
native-validated; every word's metadata is still looked up from Maknuune at ingest.
Run: python3 pipeline/stories_beginner.py   (then ingest each, then build_app)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = ("Beginner short story written in spoken Palestinian by Claude. "
       "NOT native-validated.")

# (title_ar, title_en, [(ar, en), ...])
STORIES = [
 ("قهوة الصبح", "Morning Coffee", [
   ("كل يوم بصحى الساعة سبعة.", "Every day I wake up at seven."),
   ("بروح عالمطبخ وبعمل قهوة.", "I go to the kitchen and make coffee."),
   ("بحب القهوة سادة، بدون سكر.", "I like my coffee plain, without sugar."),
   ("بقعد عالشباك وبشرب قهوتي على مهل.", "I sit by the window and drink my coffee slowly."),
   ("الجو حلو والشمس طالعة.", "The weather is nice and the sun is up."),
   ("بعدين بلبس وبروح عالشغل.", "Then I get dressed and go to work."),
 ]),
 ("عيلتي", "My Family", [
   ("أنا اسمي سامي وعندي عيلة كبيرة.", "My name is Sami and I have a big family."),
   ("أبوي بشتغل بالسوق وإمي بتطبخ أحلى أكل.", "My dad works at the market and my mom cooks the best food."),
   ("عندي أخ وأخت، وهمة أصغر مني.", "I have a brother and a sister, and they're younger than me."),
   ("جدّتي بتسكن معنا بالبيت.", "My grandmother lives with us in the house."),
   ("كل مسا بنقعد سوا ونحكي كتير.", "Every evening we sit together and talk a lot."),
   ("بحب عيلتي كتير.", "I love my family a lot."),
 ]),
 ("بيتنا", "Our House", [
   ("بيتنا صغير بس حلو.", "Our house is small but nice."),
   ("فيه غرفتين ومطبخ وحمام.", "It has two rooms, a kitchen, and a bathroom."),
   ("قدام البيت في حديقة صغيرة.", "In front of the house there is a small garden."),
   ("إمي بتزرع ورد وشوية نعنع.", "My mom plants flowers and some mint."),
   ("بحب أقعد بالحديقة بعد الظهر.", "I like to sit in the garden in the afternoon."),
 ]),
 ("القطة", "The Cat", [
   ("عنا قطة صغيرة اسمها مشمش.", "We have a little cat named Mishmish."),
   ("لونها أبيض وعيونها خضر.", "She is white and her eyes are green."),
   ("كل الصبح بتنط عالسرير وبتصحيني.", "Every morning she jumps on the bed and wakes me up."),
   ("بحب تاكل سمك وبتشرب حليب.", "She likes to eat fish and drinks milk."),
   ("بالليل بتنام جنبي.", "At night she sleeps next to me."),
 ]),
 ("الفطور", "Breakfast", [
   ("كل يوم بنفطر مع بعض.", "Every day we have breakfast together."),
   ("بناكل خبز وزيت وزعتر وجبنة.", "We eat bread, oil, za'tar, and cheese."),
   ("إمي بتعمل بيض وشاي بالنعنع.", "My mom makes eggs and mint tea."),
   ("أنا بحب الزيت والزعتر كتير.", "I really like oil and za'tar."),
   ("بعد الفطور، كل واحد بروح على شغله.", "After breakfast, everyone goes to their work."),
 ]),
 ("عالسوق", "To the Market", [
   ("يوم الجمعة بروح عالسوق.", "On Friday I go to the market."),
   ("السوق مليان ناس وأصوات.", "The market is full of people and sounds."),
   ("بشتري خضرة وفواكه ولحمة.", "I buy vegetables, fruit, and meat."),
   ("البياع بيعرفني وبيضحك.", "The seller knows me and smiles."),
   ("بشتري كل شي وبرجع عالبيت.", "I buy everything and go back home."),
 ]),
 ("صاحبي", "My Friend", [
   ("صاحبي اسمه كريم.", "My friend's name is Karim."),
   ("بنشوف بعض كل يوم بعد المدرسة.", "We see each other every day after school."),
   ("بنلعب كورة بالشارع.", "We play ball in the street."),
   ("كريم بيضحك كتير وبيحكي نكت.", "Karim laughs a lot and tells jokes."),
   ("هو أحسن صاحب عندي.", "He's my best friend."),
 ]),
 ("الجو اليوم", "The Weather Today", [
   ("اليوم الجو بارد شوي.", "Today the weather is a bit cold."),
   ("السما رمادية والغيم كتير.", "The sky is gray and there are many clouds."),
   ("بلبس جاكيت قبل ما أطلع.", "I put on a jacket before I go out."),
   ("يمكن اليوم تنزل شتا.", "Maybe it will rain today."),
   ("بحب صوت المطر عالشباك.", "I like the sound of rain on the window."),
 ]),
 ("الشاي", "Tea", [
   ("بعد الغدا، بنشرب شاي.", "After lunch, we drink tea."),
   ("إمي بتحط نعنع بالشاي.", "My mom puts mint in the tea."),
   ("جدّي بيحب الشاي تقيل وحلو.", "My grandpa likes his tea strong and sweet."),
   ("بنقعد بالصالون ونحكي.", "We sit in the living room and talk."),
   ("الشاي بالنعنع أحلى شي بالمسا.", "Mint tea is the nicest thing in the evening."),
 ]),
 ("الحديقة", "The Garden", [
   ("جنب بيتنا في حديقة كبيرة.", "Next to our house there is a big garden."),
   ("فيها شجر زيتون وليمون.", "It has olive and lemon trees."),
   ("الولاد بيلعبوا بالحديقة كل يوم.", "The kids play in the garden every day."),
   ("بحب أقعد تحت الشجرة وأقرا كتاب.", "I like to sit under the tree and read a book."),
   ("الجو هناك هادي وحلو.", "The atmosphere there is quiet and nice."),
 ]),
 ("البلد القديمة", "The Old Town", [
   ("بحب أمشي بالبلد القديمة.", "I like to walk in the old town."),
   ("الشوارع ضيقة والحجار قديمة.", "The streets are narrow and the stones are old."),
   ("في دكاكين بتبيع حلويات وبهارات.", "There are shops selling sweets and spices."),
   ("ريحة القهوة والخبز بكل مكان.", "The smell of coffee and bread is everywhere."),
   ("بشتري كنافة وبقعد أكلها.", "I buy knafeh and sit and eat it."),
 ]),
 ("الجيران", "The Neighbors", [
   ("جيراننا ناس طيبين.", "Our neighbors are good people."),
   ("أم أحمد بتسكن جنبنا.", "Um Ahmad lives next to us."),
   ("كل يوم بتبعت لإمي صحن أكل.", "Every day she sends my mom a plate of food."),
   ("وإمي بترد عليها بصحن تاني.", "And my mom sends her back another plate."),
   ("هيك الجيرة بتصير حلوة.", "That's how being neighbors becomes nice."),
 ]),
 ("الغدا", "Lunch", [
   ("الساعة تنتين بنتغدى.", "At two o'clock we have lunch."),
   ("اليوم إمي طبخت ملوخية ورز.", "Today my mom cooked mulukhiyah and rice."),
   ("كلنا بنقعد حول الطاولة.", "We all sit around the table."),
   ("الأكل بيتهني لما نكون سوا.", "The food is more enjoyable when we're together."),
   ("بعد الغدا، بننام شوي.", "After lunch, we nap a little."),
 ]),
 ("المدرسة", "School", [
   ("بروح عالمدرسة كل الصبح.", "I go to school every morning."),
   ("المدرسة قريبة من بيتنا.", "The school is close to our house."),
   ("بحب درس العربي والرسم.", "I like Arabic class and drawing."),
   ("المعلمة طيبة وبتساعدنا.", "The teacher is kind and helps us."),
   ("بعد المدرسة بلعب مع صحابي.", "After school I play with my friends."),
 ]),
 ("كتاب", "A Book", [
   ("عندي كتاب حلو بأوضتي.", "I have a nice book in my room."),
   ("فيه قصص وصور كتير.", "It has stories and many pictures."),
   ("كل ليلة بقرا صفحة أو تنتين.", "Every night I read a page or two."),
   ("القراية بتساعدني أنام.", "Reading helps me sleep."),
   ("بحب القصص القديمة.", "I like the old stories."),
 ]),
 ("المطر", "The Rain", [
   ("اليوم نزلت شتا من الصبح.", "Today it rained from the morning."),
   ("الشوارع صارت مليانة مي.", "The streets got full of water."),
   ("قعدت بالبيت وشربت شاي سخن.", "I stayed home and drank hot tea."),
   ("بحب أتفرج عالمطر من الشباك.", "I like watching the rain from the window."),
   ("الجو بارد بس البيت دافي.", "The weather is cold but the house is warm."),
 ]),
 ("أوضتي", "My Room", [
   ("أوضتي صغيرة بس مرتبة.", "My room is small but tidy."),
   ("فيها سرير وطاولة وكرسي.", "It has a bed, a table, and a chair."),
   ("عالحيط في صورة للبحر.", "On the wall there is a picture of the sea."),
   ("بحب أقعد عالطاولة وأكتب.", "I like to sit at the table and write."),
   ("بالليل، بطفي الضو وبنام.", "At night, I turn off the light and sleep."),
 ]),
 ("بطبخ مع إمي", "Cooking with Mom", [
   ("اليوم بدي أساعد إمي بالطبخ.", "Today I want to help my mom cook."),
   ("بنغسل الخضرة وبنقطعها.", "We wash the vegetables and cut them."),
   ("إمي بتحط البهارات وأنا بحرك.", "My mom adds the spices and I stir."),
   ("ريحة الأكل بتملى البيت.", "The smell of food fills the house."),
   ("بحب أتعلم الطبخ من إمي.", "I like learning to cook from my mom."),
 ]),
 ("الفرن", "The Bakery", [
   ("قريب من بيتنا في فرن.", "Near our house there is a bakery."),
   ("كل الصبح بيطلع منه ريحة خبز.", "Every morning the smell of bread comes out of it."),
   ("بروح بشتري خبز سخن.", "I go and buy hot bread."),
   ("الخباز بيعرفني وبيعطيني قطعة زيادة.", "The baker knows me and gives me an extra piece."),
   ("الخبز السخن أحلى شي.", "Hot bread is the nicest thing."),
 ]),
 ("الولاد", "The Kids", [
   ("بعد الظهر، الولاد بينزلوا عالشارع.", "In the afternoon, the kids go out to the street."),
   ("بيلعبوا ويجروا ويضحكوا.", "They play, run, and laugh."),
   ("واحد بيركض والتاني بيلحقه.", "One runs and the other chases him."),
   ("أصواتهم بتملى الحارة.", "Their voices fill the neighborhood."),
   ("بحب أتفرج عليهم من الشباك.", "I like to watch them from the window."),
 ]),
 ("الباص", "The Bus", [
   ("كل يوم بركب الباص عالشغل.", "Every day I take the bus to work."),
   ("الباص بيجي الساعة تمنية.", "The bus comes at eight o'clock."),
   ("بقعد جنب الشباك وأتفرج عالطريق.", "I sit by the window and watch the road."),
   ("الناس بالباص كتير بالصبح.", "There are many people on the bus in the morning."),
   ("بعد نص ساعة، بوصل عالشغل.", "After half an hour, I arrive at work."),
 ]),
 ("المسا", "The Evening", [
   ("بالمسا، بنقعد كلنا بالصالون.", "In the evening, we all sit in the living room."),
   ("أبوي بيتفرج عالأخبار.", "My dad watches the news."),
   ("إمي بتخيط وأنا بقرا.", "My mom sews and I read."),
   ("بنشرب شاي وناكل بسكوت.", "We drink tea and eat biscuits."),
   ("المسا بالبيت أحلى وقت.", "The evening at home is the nicest time."),
 ]),
 ("جدّتي", "My Grandmother", [
   ("جدّتي كبيرة بالعمر بس قلبها شاب.", "My grandmother is old but her heart is young."),
   ("بتحكيلي قصص من زمان.", "She tells me stories from long ago."),
   ("بتعرف تطبخ أكلات قديمة كتير.", "She knows how to cook many old dishes."),
   ("كل يوم بنقعد سوا ونحكي.", "Every day we sit together and talk."),
   ("بحب جدّتي كتير.", "I love my grandmother a lot."),
 ]),
 ("البحر", "The Sea", [
   ("بالصيف، بنروح عالبحر.", "In the summer, we go to the sea."),
   ("المي زرقا والرملة دافية.", "The water is blue and the sand is warm."),
   ("الولاد بيسبحوا ويلعبوا بالرملة.", "The kids swim and play in the sand."),
   ("بنقعد تحت الشمس وناكل بطيخ.", "We sit under the sun and eat watermelon."),
   ("بحب صوت الموج كتير.", "I really like the sound of the waves."),
 ]),
 ("الخضرة", "The Vegetables", [
   ("بحب أشتري خضرة طازة.", "I like to buy fresh vegetables."),
   ("بالسوق في بندورة وخيار وكوسا.", "At the market there are tomatoes, cucumbers, and zucchini."),
   ("البياع بيقول إنها من بستانه.", "The seller says they are from his garden."),
   ("بشتري شوية وبرجع عالبيت.", "I buy some and go back home."),
   ("إمي بتعمل منها سلطة حلوة.", "My mom makes a nice salad from them."),
 ]),
 ("الكلب", "The Dog", [
   ("جارنا عنده كلب اسمه لولو.", "Our neighbor has a dog named Lulu."),
   ("لونه بني وذيله طويل.", "He is brown and has a long tail."),
   ("كل الصبح بيلعب بالحديقة.", "Every morning he plays in the garden."),
   ("لما يشوفني، بيجي بيركض.", "When he sees me, he comes running."),
   ("بحب ألعب معه شوي.", "I like to play with him a little."),
 ]),
 ("الشتا", "Winter", [
   ("بالشتا، الجو بارد كتير.", "In winter, the weather is very cold."),
   ("بنشعل الصوبا ونقعد حواليها.", "We light the heater and sit around it."),
   ("إمي بتعمل شوربة عدس سخنة.", "My mom makes hot lentil soup."),
   ("برا بتنزل شتا والريح قوية.", "Outside it rains and the wind is strong."),
   ("بس جوا البيت دافي ومريح.", "But inside the house is warm and cozy."),
 ]),
 ("الصيف", "Summer", [
   ("بالصيف، النهار طويل والجو سخن.", "In summer, the day is long and the weather is hot."),
   ("بنقعد برا بالمسا لأنه أبرد.", "We sit outside in the evening because it's cooler."),
   ("الولاد بياكلوا بوظة.", "The kids eat ice cream."),
   ("بنسقي الحديقة كل مسا.", "We water the garden every evening."),
   ("بحب ليالي الصيف الطويلة.", "I like the long summer nights."),
 ]),
 ("مشوار", "An Errand", [
   ("اليوم لازم أروح مشوار.", "Today I have to run an errand."),
   ("بدي أشتري خبز وحليب وبيض.", "I want to buy bread, milk, and eggs."),
   ("بمشي عالدكان لأنه قريب.", "I walk to the shop because it's close."),
   ("بشوف ناس بعرفهم بالطريق وبسلم عليهم.", "I see people I know on the way and greet them."),
   ("بشتري كل شي وبرجع بسرعة.", "I buy everything and come back quickly."),
 ]),
 ("الليل", "The Night", [
   ("بالليل، البيت بيصير هادي.", "At night, the house becomes quiet."),
   ("كل الناس بيناموا بكير.", "Everyone sleeps early."),
   ("بطفي الضو وبفتح الشباك شوي.", "I turn off the light and open the window a little."),
   ("الهوا بارد والسما مليانة نجوم.", "The air is cool and the sky is full of stars."),
   ("بسكر عيوني وبنام مبسوط.", "I close my eyes and sleep happy."),
 ]),
]

def main():
    from bookshelf import check_sentences
    rc = check_sentences('beginner stories',
                         [(a, e) for _t, _te, ss in STORIES for a, e in ss])
    if rc:
        return rc
    tdir = paths.texts()
    for i, (t_ar, t_en, sents) in enumerate(STORIES, 1):
        sid = 'story-beg-%02d' % i
        obj = {'id': sid, 'kind': 'story', 'level': 'beginner',
               'title': {'ar': t_ar, 'en': t_en},
               'dialect': 'pal', 'subdialect': 'urban', 'source': SRC,
               'sentences': [{'ar': a, 'en': e} for a, e in sents]}
        json.dump(obj, open(os.path.join(tdir, sid + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    print('wrote %d beginner stories' % len(STORIES))

if __name__ == '__main__':
    raise SystemExit(main() or 0)
