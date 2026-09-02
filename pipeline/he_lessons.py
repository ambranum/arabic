#!/usr/bin/env python3
"""Build the Hebrew Lessons -> app/data/he/lessons.js.

The Arabic side's lessons are TRANSCRIBED: their Arabic is copied verbatim out of the user's own
teaching materials, page by page, with a `src` on every chunk. The Hebrew shelf could not be
built that way. Its reference books -- Aleph, Bet, Gimel, Gimel+, Reichman, and the HebrewPod
slang packs -- are commercial published workbooks, and this repo IS the public website. So what
is taken from them is their METHOD, and the content is ours:

  Aleph      a bilingual exercise heading, one worked דוגמה, then numbered items with a blank
             in the middle of a real sentence. Never a word list to memorise -- always a
             sentence someone would say, with one piece missing.
  Bet        transformation drills (rewrite this sentence in another tense) and a מילים חדשות
             table that sorts the new words by part of speech.
  Gimel      vocabulary carrying its GOVERNED PREPOSITION -- לגרום ל, לשמור על, לסבול מ. In
             Hebrew the preposition is part of the verb and teaching one without the other is
             teaching half a word.
  Reichman   the infinitive given in brackets as the prompt, the learner writing the inflected
             form: "אנחנו ____ עם החברים [להיפגש]".
  HebrewPod  the slang card: the literal reading, the real meaning, when you would say it, and
             sample sentences. לדפוק לילה לבן is "to knock a white night" and means to stay up
             all night, and a learner who is only told the second half has not learned it.

WHAT IS LOOKED UP. The prose, the sentences and the exercise design are curated teaching, the
same standing as pipeline/he_grammar.py's explanations and he_stories.py's stories. Every WORD
in a vocabulary table is checked against the lexicon at build time: the pointing and the gloss
come from there, and anything the lexicon does not have is reported and ships unpointed rather
than pointed by us. Exercise sentences are stored unpointed, the way Israelis write, and the app
renders them through arLive() so every word is tappable and gets the same word card as anywhere
else in the app.

Run:
    python3 pipeline/he_lessons.py            # build, and report the lexicon check
    python3 pipeline/he_lessons.py --check    # report only, write nothing
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')
from build_lex import he_norm                          # noqa: E402
from lex import Lexicon                                # noqa: E402
from phon import unpoint                               # noqa: E402
import he_curated                                      # noqa: E402

OUT = paths.data('lessons.js')


# ---------------------------------------------------------------------------------------------
# THE UNITS.
#
# Hebrew is written here the way an Israeli writes it -- ktiv male, no niqqud. The pointing is
# the lexicon's job (look_up below), not ours, which is the same rule the rest of the app runs
# on and the reason a lesson word tapped here opens the same card as the same word in the paper.
#
# Block kinds, and every one of them is something the learner DOES except `teach`, `vocab` and
# `slang`:
#   teach      the grammar point, with examples
#   vocab      מילים חדשות, sorted by part of speech, prepositions attached
#   slang      the HebrewPod card: literal, meaning, when to say it, examples
#   fill       type the missing word into the blank            (Aleph)
#   bracket    type the verb, infinitive given as the prompt   (Reichman)
#   choose     pick from a dropdown                            (Aleph, multiple-choice variant)
#   transform  rewrite the whole sentence                      (Bet)
#   match      pair Hebrew with English
#   order      put the words in order
#   quiz       multiple choice, with a reason shown after
#
# `a` is always a LIST of accepted answers. Hebrew spelling varies -- ktiv male against haser,
# איתך against אתך -- and marking a learner wrong for writing it the other correct way teaches
# them to distrust the app.
UNITS = [
  {
    'id': 'he-01', 'n': 1, 'level': 'beginner',
    'title': {'he': 'מה קורה?', 'en': 'What’s going on?'},
    'objective': 'Greet someone, ask how they are, and answer — in the register Israelis '
                 'actually use, which is not the one the textbooks open with.',
    'blocks': [
      {'kind': 'teach', 'title': 'שלום is the one nobody says',
       'body': 'שָׁלוֹם is correct and everyone understands it, and almost nobody greets a friend '
               'with it. What you will hear is <b>היי</b>, <b>מה נשמע</b>, <b>מה קורה</b> — and the '
               'answer is almost never a description of your feelings. It is one word, and then '
               'you ask back.',
       'examples': [
         {'he': 'היי, מה נשמע?', 'en': 'Hey, how’s it going?'},
         {'he': 'סבבה, ואת?', 'en': 'Fine, and you?'},
         {'he': 'מה קורה?', 'en': 'What’s up?'},
         {'he': 'הכל טוב, תודה.', 'en': 'All good, thanks.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'שלום', 'en': 'hello, peace', 'pos': 'noun'},
         {'he': 'בוקר', 'en': 'morning', 'pos': 'noun'},
         {'he': 'ערב', 'en': 'evening', 'pos': 'noun'},
         {'he': 'לילה', 'en': 'night', 'pos': 'noun'},
         {'he': 'תודה', 'en': 'thank you', 'pos': 'other'},
         {'he': 'בבקשה', 'en': 'please, here you are', 'pos': 'other'},
         {'he': 'סליחה', 'en': 'excuse me, sorry', 'pos': 'other'},
         {'he': 'טוב', 'en': 'good', 'pos': 'adj'},
         {'he': 'נעים', 'en': 'pleasant', 'pos': 'adj'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את המילה החסרה',
       'en': 'Fill in the missing word',
       'instructions': 'Type the missing word. Vowels are never required — write it the way you '
                       'would type it on a phone.',
       'example': {'q': 'בוקר ___! — Good morning!', 'a': 'טוב'},
       'items': [
         {'q': '___ טוב, איך היה היום שלך?', 'a': ['ערב'], 'en': 'Good evening, how was your day?'},
         {'q': 'לילה ___, נתראה מחר.', 'a': ['טוב'], 'en': 'Good night, see you tomorrow.'},
         {'q': '___ רבה על העזרה!', 'a': ['תודה'], 'en': 'Thank you very much for the help!'},
         {'q': '___, איפה התחנה?', 'a': ['סליחה'], 'en': 'Excuse me, where is the station?'},
         {'q': 'נעים ___ אותך.', 'a': ['להכיר'], 'en': 'Nice to meet you.',
          'hint': 'from להכיר, "to know / to be acquainted with"'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את התשובה', 'en': 'Choose the answer',
       'instructions': 'Someone says the line on the right. Pick the reply an Israeli would give.',
       'items': [
         {'q': 'מה נשמע?', 'options': ['סבבה, ואתה?', 'אני שלום.', 'שלום עליכם.'],
          'a': 'סבבה, ואתה?', 'en': '“How’s it going?”'},
         {'q': 'תודה רבה!', 'options': ['בבקשה', 'סליחה', 'להתראות'], 'a': 'בבקשה',
          'en': '“Thanks a lot!”'},
         {'q': 'נעים להכיר.', 'options': ['גם לי', 'גם אני', 'טוב מאוד'], 'a': 'גם לי',
          'en': '“Nice to meet you.” — the set reply is “likewise”.'},
         {'q': 'איך היה?', 'options': ['היה מעולה', 'הוא מעולה', 'יש מעולה'], 'a': 'היה מעולה',
          'en': '“How was it?”'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap a Hebrew phrase, then its English.',
       'pairs': [
         {'he': 'בוקר טוב', 'en': 'Good morning'},
         {'he': 'ערב טוב', 'en': 'Good evening'},
         {'he': 'להתראות', 'en': 'See you'},
         {'he': 'מה שלומך?', 'en': 'How are you?'},
         {'he': 'הכל בסדר', 'en': 'Everything’s fine'},
         {'he': 'נתראה מחר', 'en': 'See you tomorrow'},
       ]},
      {'kind': 'slang', 'he': 'מה נשמע', 'literal': '“what is heard?”',
       'meaning': 'How’s it going?',
       'when': 'The everyday greeting between people who know each other. It is a real question '
               'only in the way “how are you” is a real question in English — the expected answer '
               'is one word and then the same question back.',
       'examples': [
         {'he': 'היי דני, מה נשמע?', 'en': 'Hey Dani, how’s it going?'},
         {'he': 'מה נשמע איתך היום?', 'en': 'How are things with you today?'},
       ]},
      {'kind': 'slang', 'he': 'סבבה', 'literal': '(from Arabic صَبابة, by way of army slang)',
       'meaning': 'Cool, fine, all good.',
       'when': 'The default answer to מה נשמע, and the default way to agree to anything. It is '
               'informal but not rude, and you will hear it from a twenty-year-old and a '
               'fifty-year-old on the same afternoon.',
       'examples': [
         {'he': 'סבבה, נתראה בשמונה.', 'en': 'Cool, see you at eight.'},
         {'he': 'הכל סבבה?', 'en': 'Everything OK?'},
       ]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-02', 'n': 2, 'level': 'beginner',
    'title': {'he': 'יש לי, אין לי', 'en': 'Having and not having'},
    'objective': 'Say what you have and what you do not. Hebrew has no verb "to have", so this '
                 'is a different sentence from the English one, not a translation of it.',
    'blocks': [
      {'kind': 'teach', 'title': 'There is no verb “to have”',
       'body': 'Hebrew says <b>יש ל־</b> — "there is to me" — and for the negative <b>אין ל־</b>. '
               'The thing you have is the SUBJECT, so nothing agrees with you: it is יש לי כלב '
               'and יש לי כלבים, and the לי never changes shape for what follows it.',
       'examples': [
         {'he': 'יש לי זמן.', 'en': 'I have time.'},
         {'he': 'אין לי זמן.', 'en': 'I don’t have time.'},
         {'he': 'יש לה שאלה.', 'en': 'She has a question.'},
         {'he': 'אין לנו כסף.', 'en': 'We don’t have money.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'כסף', 'en': 'money', 'pos': 'noun'},
         {'he': 'זמן', 'en': 'time', 'pos': 'noun'},
         {'he': 'עבודה', 'en': 'work, job', 'pos': 'noun'},
         {'he': 'שאלה', 'en': 'question', 'pos': 'noun'},
         {'he': 'רעיון', 'en': 'idea', 'pos': 'noun'},
         {'he': 'מכונית', 'en': 'car', 'pos': 'noun'},
         {'he': 'כלב', 'en': 'dog', 'pos': 'noun'},
         {'he': 'חבר', 'en': 'friend', 'pos': 'noun'},
         {'he': 'בעיה', 'en': 'problem', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'יש ל… / אין ל…', 'en': 'Who has it?',
       'instructions': 'Type the right form of ל־ for the person named. לי, לך, לו, לה, לנו, לכם, להם.',
       'example': {'q': 'דני: יש ___ אחות. — Dani: I have a sister.', 'a': 'לי'},
       'items': [
         {'q': 'יש ___ שאלה, המורה!', 'a': ['לי'], 'en': 'I have a question, teacher!'},
         {'q': 'לרותי יש כלב. יש ___ גם חתול.', 'a': ['לה'], 'en': 'Ruti has a dog. She also has a cat.'},
         {'q': 'דני עובד הרבה. אין ___ זמן.', 'a': ['לו'], 'en': 'Dani works a lot. He has no time.'},
         {'q': 'אנחנו סטודנטים, אין ___ כסף.', 'a': ['לנו'], 'en': 'We’re students, we have no money.'},
         {'q': 'הילדים שמחים — יש ___ חופש.', 'a': ['להם'], 'en': 'The children are happy — they have a holiday.'},
         {'q': 'שרה, יש ___ רגע?', 'a': ['לך'], 'en': 'Sarah, do you have a moment?'},
       ]},
      {'kind': 'transform', 'title': 'מיש לאין', 'en': 'From יש to אין',
       'instructions': 'Rewrite each sentence in the negative. Type the whole sentence.',
       'example': {'from': 'יש לי זמן.', 'to': 'אין לי זמן.'},
       'items': [
         {'from': 'יש לו עבודה.', 'to': ['אין לו עבודה.', 'אין לו עבודה'], 'en': 'He has a job.'},
         {'from': 'יש לנו בעיה.', 'to': ['אין לנו בעיה.', 'אין לנו בעיה'], 'en': 'We have a problem.'},
         {'from': 'יש להם מכונית.', 'to': ['אין להם מכונית.', 'אין להם מכונית'], 'en': 'They have a car.'},
         {'from': 'יש לך רעיון.', 'to': ['אין לך רעיון.', 'אין לך רעיון'], 'en': 'You have an idea.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Which is “She doesn’t have a car”?',
          'options': ['אין לה מכונית', 'אין לו מכונית', 'היא לא מכונית'],
          'a': 'אין לה מכונית',
          'why': 'לה is “to her”. לו is “to him”, and the third is not a Hebrew sentence.'},
         {'q': 'Why is it יש לי כלבים and not יש לי כלביםים?',
          'options': ['Because ל־ never agrees with what you have',
                      'Because כלב is masculine',
                      'Because יש is plural already'],
          'a': 'Because ל־ never agrees with what you have',
          'why': 'The thing owned is the subject of the sentence; לי points at the owner and is '
                 'fixed.'},
       ]},
      {'kind': 'slang', 'he': 'יש מצב', 'literal': '“there is a situation”',
       'meaning': 'Maybe / is there a chance? — and on its own, “sure, why not”.',
       'when': 'Asking whether something is possible, or agreeing to it. The negative אין מצב is '
               'much stronger: “no way”, flat refusal or disbelief.',
       'examples': [
         {'he': 'יש מצב שתעזור לי?', 'en': 'Any chance you could help me?'},
         {'he': 'אין מצב! באמת?', 'en': 'No way! Really?'},
       ]},
    ],
  },
  {
    'id': 'he-03', 'n': 3, 'level': 'beginner',
    'title': {'he': 'זמן הווה', 'en': 'The present tense'},
    'objective': 'Say what you are doing. Hebrew’s present is four forms and no “am/is/are”, '
                 'which makes it the tense you can start speaking in on day one.',
    'blocks': [
      {'kind': 'teach', 'title': 'Four forms, no person',
       'body': 'The Hebrew present does not inflect for person — only for GENDER and NUMBER. '
               '<b>כותב</b> covers "I write", "you write" and "he writes" as long as the speaker '
               'is male. So one verb gives you four forms and the pronoun does the rest. And '
               'there is no "am": אני כותב is the whole sentence.',
       'examples': [
         {'he': 'אני כותב מכתב.', 'en': 'I (m.) am writing a letter.'},
         {'he': 'היא כותבת מכתב.', 'en': 'She is writing a letter.'},
         {'he': 'אנחנו כותבים.', 'en': 'We (m.) are writing.'},
         {'he': 'הן כותבות.', 'en': 'They (f.) are writing.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לכתוב', 'en': 'to write', 'pos': 'verb'},
         {'he': 'לקרוא', 'en': 'to read, to call', 'pos': 'verb'},
         {'he': 'לאכול', 'en': 'to eat', 'pos': 'verb'},
         {'he': 'לשתות', 'en': 'to drink', 'pos': 'verb'},
         {'he': 'ללמוד', 'en': 'to learn, to study', 'pos': 'verb'},
         {'he': 'לעבוד', 'en': 'to work', 'pos': 'verb'},
         {'he': 'לגור', 'en': 'to live, to reside', 'pos': 'verb'},
         {'he': 'לרצות', 'en': 'to want', 'pos': 'verb'},
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל בהווה', 'en': 'Write the verb in the present',
       'instructions': 'The infinitive is in brackets. Type the present-tense form that fits the '
                       'subject.',
       'example': {'q': 'אני ___ עברית. [ללמוד]', 'a': 'לומד'},
       'items': [
         {'q': 'דני ___ בתל אביב. [לגור]', 'a': ['גר'], 'en': 'Dani lives in Tel Aviv.'},
         {'q': 'רותי ___ קפה בבוקר. [לשתות]', 'a': ['שותה'], 'en': 'Ruti drinks coffee in the morning.'},
         {'q': 'אנחנו ___ בבית ספר. [לעבוד]', 'a': ['עובדים', 'עובדות'], 'en': 'We work at a school.'},
         {'q': 'הילדות ___ ספר. [לקרוא]', 'a': ['קוראות'], 'en': 'The girls are reading a book.'},
         {'q': 'אתה ___ לאכול משהו? [לרצות]', 'a': ['רוצה'], 'en': 'Do you want to eat something?'},
         {'q': 'הם ___ פלאפל כל יום שישי. [לאכול]', 'a': ['אוכלים'], 'en': 'They eat falafel every Friday.'},
       ]},
      {'kind': 'transform', 'title': 'מזכר לנקבה', 'en': 'Masculine to feminine',
       'instructions': 'Rewrite each sentence as if a woman were speaking or being spoken about.',
       'example': {'from': 'הוא לומד עברית.', 'to': 'היא לומדת עברית.'},
       'items': [
         {'from': 'הוא עובד בבנק.', 'to': ['היא עובדת בבנק.', 'היא עובדת בבנק'], 'en': 'He works at a bank.'},
         {'from': 'אני גר בירושלים.', 'to': ['אני גרה בירושלים.', 'אני גרה בירושלים'], 'en': 'I live in Jerusalem.'},
         {'from': 'הם קוראים עיתון.', 'to': ['הן קוראות עיתון.', 'הן קוראות עיתון'], 'en': 'They read a newspaper.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['אני', 'שותה', 'קפה', 'בבוקר'], 'a': 'אני שותה קפה בבוקר',
          'en': 'I drink coffee in the morning.'},
         {'words': ['היא', 'לא', 'רוצה', 'ללכת', 'היום'], 'a': 'היא לא רוצה ללכת היום',
          'en': 'She doesn’t want to go today.'},
         {'words': ['אנחנו', 'לומדים', 'עברית', 'כל', 'שבוע'], 'a': 'אנחנו לומדים עברית כל שבוע',
          'en': 'We study Hebrew every week.'},
       ]},
      {'kind': 'slang', 'he': 'בקטע של', 'literal': '“in the segment of”',
       'meaning': 'Into (something), in the mood for.',
       'when': 'Saying what you are into or up for right now. Very common with young speakers, '
               'and it takes a noun or a verb straight after it.',
       'examples': [
         {'he': 'אני בקטע של סרטים ישנים.', 'en': 'I’m into old films.'},
         {'he': 'אתה בקטע של לצאת הערב?', 'en': 'Are you up for going out tonight?'},
       ]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-04', 'n': 4, 'level': 'beginner',
    'title': {'he': 'למי? — ל־ עם כינויים', 'en': 'To whom? — ל־ with pronouns'},
    'objective': 'Hebrew glues its pronouns onto its prepositions. Learn the ל־ set cold and you '
                 'have unlocked יש לי, תן לי, אמרתי לו and half of everyday speech.',
    'blocks': [
      {'kind': 'teach', 'title': 'One preposition, eight endings',
       'body': 'English says "to me"; Hebrew says one word, <b>לִי</b>. The whole set: '
               'לִי, לְךָ (m.), לָךְ (f.), לוֹ, לָהּ, לָנוּ, לָכֶם, לָהֶם. This is the pattern almost '
               'every Hebrew preposition follows, so learning ל־ is learning the shape of ב־, '
               'עם, של and אֶת as well.',
       'examples': [
         {'he': 'תן לי רגע.', 'en': 'Give me a moment.'},
         {'he': 'אמרתי לו הכל.', 'en': 'I told him everything.'},
         {'he': 'קניתי לה מתנה.', 'en': 'I bought her a present.'},
         {'he': 'זה לא מתאים לנו.', 'en': 'That doesn’t suit us.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לתת', 'en': 'to give', 'pos': 'verb'},
         {'he': 'לומר', 'en': 'to say', 'pos': 'verb'},
         {'he': 'לשלוח', 'en': 'to send', 'pos': 'verb'},
         {'he': 'לקנות', 'en': 'to buy', 'pos': 'verb'},
         {'he': 'מתנה', 'en': 'present, gift', 'pos': 'noun'},
         {'he': 'מכתב', 'en': 'letter', 'pos': 'noun'},
         {'he': 'סיפור', 'en': 'story', 'pos': 'noun'},
         {'he': 'עזרה', 'en': 'help', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'כתבו את ל־ הנכון', 'en': 'Write ל־ correctly',
       'instructions': 'One worked example, then eleven of them — the Aleph workbook’s own drill, '
                       'with our sentences. Type just the ל־ word.',
       'example': {'q': 'אנחנו קונים ___ ספר. (לגליה) — We’re buying Galia a book.', 'a': 'לה'},
       'items': [
         {'q': 'אבא מספר ___ סיפור כל ערב. (לדני)', 'a': ['לו'], 'en': 'Dad tells him a story every evening.'},
         {'q': 'למה אתה לא אומר ___ בוקר טוב? (לנוגה)', 'a': ['לה'], 'en': 'Why don’t you say good morning to her?'},
         {'q': 'רחל, מי שולח ___ פרחים?', 'a': ['לך'], 'en': 'Rachel, who is sending you flowers?'},
         {'q': 'אני רוצה לכתוב ___ מכתב. (לאבי)', 'a': ['לו'], 'en': 'I want to write him a letter.'},
         {'q': 'שרה, את רואה את החברות שלך היום? אני רוצה לתת ___ משהו.', 'a': ['להן', 'להם'],
          'en': 'Sarah, are you seeing your friends today? I want to give them something.'},
         {'q': 'המורה נותנת ___ הרבה שיעורי בית. (לתלמידים)', 'a': ['להם'],
          'en': 'The teacher gives them a lot of homework.'},
         {'q': 'אנחנו קונים ___ מחשב חדש. (לאבא)', 'a': ['לו'], 'en': 'We’re buying him a new computer.'},
         {'q': 'החברה שלי בגרמניה. אני שולח ___ ווטסאפ כל יום.', 'a': ['לה'],
          'en': 'My friend is in Germany. I send her a WhatsApp every day.'},
         {'q': 'איפה אתם? אני רוצה לתת ___ משהו קטן.', 'a': ['לכם'],
          'en': 'Where are you? I want to give you something small.'},
         {'q': 'תודה רבה ___ על העזרה! (לך, נקבה)', 'a': ['לך'], 'en': 'Thank you very much for the help!'},
         {'q': 'אין ___ זמן היום, אנחנו עובדים. (אנחנו)', 'a': ['לנו'], 'en': 'We have no time today, we’re working.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'לי', 'en': 'to me'},
         {'he': 'לך', 'en': 'to you'},
         {'he': 'לו', 'en': 'to him'},
         {'he': 'לה', 'en': 'to her'},
         {'he': 'לנו', 'en': 'to us'},
         {'he': 'להם', 'en': 'to them'},
       ]},
      {'kind': 'slang', 'he': 'תעשה לי טובה', 'literal': '“do me a favour”',
       'meaning': 'Come off it. / Oh please.',
       'when': 'Rarely an actual request. Said with a falling tone it is disbelief or impatience '
               '— the English “give me a break”. Ask for a real favour with אפשר בבקשה.',
       'examples': [
         {'he': 'תעשה לי טובה, זה לא נכון.', 'en': 'Come off it, that’s not true.'},
         {'he': 'תעשי לי טובה ותפסיקי.', 'en': 'Do me a favour and stop.'},
       ]},
    ],
  },
  {
    'id': 'he-05', 'n': 5, 'level': 'intermediate',
    'title': {'he': 'זמן עתיד', 'en': 'The future tense'},
    'objective': 'Say what will happen. The future is built with PREFIXES, which is why it looks '
                 'nothing like the past and why it is the tense that makes Hebrew click.',
    'blocks': [
      {'kind': 'teach', 'title': 'The future is a prefix',
       'body': 'Past tense adds endings; future adds a letter at the FRONT: '
               '<b>א</b>כתוב (I), <b>ת</b>כתוב (you m.), <b>ת</b>כתבי (you f.), <b>י</b>כתוב (he), '
               '<b>ת</b>כתוב (she), <b>נ</b>כתוב (we), <b>ת</b>כתבו (you pl.), <b>י</b>כתבו (they). '
               'Say the letters אתי״ן to yourself — א for me, ת for you and her, י for him, נ for us.',
       'examples': [
         {'he': 'מחר אני אכתוב לו.', 'en': 'Tomorrow I’ll write to him.'},
         {'he': 'הם יגיעו בשמונה.', 'en': 'They’ll arrive at eight.'},
         {'he': 'נדבר בערב.', 'en': 'We’ll talk in the evening.'},
         {'he': 'מתי תגיעי?', 'en': 'When will you (f.) arrive?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להגיע', 'en': 'to arrive', 'pos': 'verb'},
         {'he': 'לדבר', 'en': 'to speak', 'pos': 'verb'},
         {'he': 'להתחיל', 'en': 'to begin', 'pos': 'verb'},
         {'he': 'לטוס', 'en': 'to fly', 'pos': 'verb'},
         {'he': 'להיפגש', 'en': 'to meet (each other)', 'pos': 'verb'},
         {'he': 'להכין', 'en': 'to prepare', 'pos': 'verb'},
         {'he': 'מחר', 'en': 'tomorrow', 'pos': 'other'},
         {'he': 'בקרוב', 'en': 'soon', 'pos': 'other'},
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל בזמן עתיד', 'en': 'Write the verb in the future',
       'instructions': 'Reichman’s drill, our sentences: the infinitive is the prompt in brackets, '
                       'you write the future form that fits the subject.',
       'example': {'q': 'הוא ___ מכתב להורים שלו. [לכתוב]', 'a': 'יכתוב'},
       'items': [
         {'q': 'בשבוע הבא אנחנו ___ עם החברים שלנו. [להיפגש]', 'a': ['ניפגש'],
          'en': 'Next week we’ll meet up with our friends.'},
         {'q': 'אתה ___ לפריז בקיץ הבא. [לטוס]', 'a': ['תטוס'], 'en': 'You’ll fly to Paris next summer.'},
         {'q': 'באוקטובר היא ___ ללמוד באוניברסיטה. [להתחיל]', 'a': ['תתחיל'],
          'en': 'In October she’ll start studying at university.'},
         {'q': 'אין לי ספק שהן ___ בזמן לשיעור. [להגיע]', 'a': ['יגיעו'],
          'en': 'I have no doubt they’ll get to the lesson on time.'},
         {'q': 'אולי אתה ___ לנו ארוחת צהריים היום? [להכין]', 'a': ['תכין'],
          'en': 'Maybe you’ll make us lunch today?'},
         {'q': 'אני ___ איתך בטלפון בערב. [לדבר]', 'a': ['אדבר'],
          'en': 'I’ll talk to you on the phone in the evening.'},
       ]},
      {'kind': 'transform', 'title': 'מהווה לעתיד', 'en': 'Present to future',
       'instructions': 'Rewrite the sentence in the future. Keep everything else the same.',
       'example': {'from': 'אני כותב מכתב.', 'to': 'אני אכתוב מכתב.'},
       'items': [
         {'from': 'הוא מגיע בשמונה.', 'to': ['הוא יגיע בשמונה.', 'הוא יגיע בשמונה'], 'en': 'He arrives at eight.'},
         {'from': 'אנחנו מדברים מחר.', 'to': ['אנחנו נדבר מחר.', 'אנחנו נדבר מחר'], 'en': 'We speak tomorrow.'},
         {'from': 'הם מתחילים בקרוב.', 'to': ['הם יתחילו בקרוב.', 'הם יתחילו בקרוב'], 'en': 'They start soon.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Which letter starts the future for אנחנו?',
          'options': ['נ', 'א', 'ת', 'י'], 'a': 'נ',
          'why': 'אתי״ן: א for אני, ת for אתה/את/היא/אתם, י for הוא/הם, נ for אנחנו.'},
         {'q': 'תכתוב could mean —',
          'options': ['“you (m.) will write” or “she will write”',
                      'only “you will write”', 'only “she will write”'],
          'a': '“you (m.) will write” or “she will write”',
          'why': 'ת does double duty. Context, or the pronoun, tells you which one is meant.'},
       ]},
      {'kind': 'slang', 'he': 'יהיה בסדר', 'literal': '“it will be in order”',
       'meaning': 'It’ll be fine.',
       'when': 'The national reflex. Said to reassure, to close an argument, and sometimes to '
               'avoid answering — which is a thing worth knowing about it before you rely on it.',
       'examples': [
         {'he': 'אל תדאג, יהיה בסדר.', 'en': 'Don’t worry, it’ll be fine.'},
         {'he': 'יהיה בסדר, נסתדר.', 'en': 'It’ll be OK, we’ll manage.'},
       ]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-06', 'n': 6, 'level': 'intermediate',
    'title': {'he': 'לחפש דירה', 'en': 'Looking for a flat'},
    'objective': 'The vocabulary of the thing every Israeli under forty talks about constantly. '
                 'Gimel teaches this set as a topic, with the adjectives that go with it.',
    'blocks': [
      {'kind': 'teach', 'title': 'Reading a flat ad',
       'body': 'A Yad2 listing is a stack of adjectives: <b>משופצת</b> renovated, <b>מרוהטת</b> '
               'furnished, <b>מרכזית</b> central, <b>שקטה</b> quiet. They agree with דירה, which '
               'is feminine — so they all end in ־ה. Change the noun to a masculine one and every '
               'adjective changes with it.',
       'examples': [
         {'he': 'דירה משופצת במרכז העיר.', 'en': 'A renovated flat in the city centre.'},
         {'he': 'הדירה מרוהטת ושקטה.', 'en': 'The flat is furnished and quiet.'},
         {'he': 'כמה שכר הדירה?', 'en': 'How much is the rent?'},
         {'he': 'בעל הבית גר למטה.', 'en': 'The landlord lives downstairs.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'דירה', 'en': 'flat, apartment', 'pos': 'noun'},
         {'he': 'חדר', 'en': 'room', 'pos': 'noun'},
         {'he': 'מטבח', 'en': 'kitchen', 'pos': 'noun'},
         {'he': 'שכן', 'en': 'neighbour', 'pos': 'noun'},
         {'he': 'רהיטים', 'en': 'furniture', 'pos': 'noun'},
         {'he': 'שקט', 'en': 'quiet', 'pos': 'adj'},
         {'he': 'רועש', 'en': 'noisy', 'pos': 'adj'},
         {'he': 'מרכזי', 'en': 'central', 'pos': 'adj'},
         {'he': 'יקר', 'en': 'expensive', 'pos': 'adj'},
         {'he': 'זול', 'en': 'cheap', 'pos': 'adj'},
         {'he': 'לשכור', 'en': 'to rent', 'pos': 'verb', 'prep': 'את'},
         {'he': 'לעבור', 'en': 'to move, to pass', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את שם התואר', 'en': 'Choose the adjective',
       'instructions': 'Pick the form that agrees with the noun.',
       'items': [
         {'q': 'דירה ___ במרכז העיר.', 'options': ['משופצת', 'משופץ', 'משופצים'], 'a': 'משופצת',
          'en': 'דירה is feminine singular.'},
         {'q': 'החדר הזה ___ מאוד.', 'options': ['שקט', 'שקטה', 'שקטים'], 'a': 'שקט',
          'en': 'חדר is masculine singular.'},
         {'he': '', 'q': 'השכנים שלנו ___.', 'options': ['רועשים', 'רועש', 'רועשת'], 'a': 'רועשים',
          'en': 'שכנים is masculine plural.'},
         {'q': 'שכר הדירה פה ___ מדי.', 'options': ['יקר', 'יקרה', 'יקרים'], 'a': 'יקר',
          'en': 'שכר is masculine singular.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Complete the ad',
       'instructions': 'Type the missing word from the vocabulary above.',
       'example': {'q': 'אני מחפש ___ עם שני חדרים. — I’m looking for a flat with two rooms.', 'a': 'דירה'},
       'items': [
         {'q': 'הדירה קטנה אבל ה___ גדול.', 'a': ['מטבח'], 'en': 'The flat is small but the kitchen is big.'},
         {'q': 'ה___ שלי מנגן בגיטרה כל לילה.', 'a': ['שכן'], 'en': 'My neighbour plays guitar every night.'},
         {'q': 'אנחנו רוצים ___ דירה ליד הים.', 'a': ['לשכור'], 'en': 'We want to rent a flat near the sea.'},
         {'q': 'בחודש הבא אנחנו ___ לתל אביב.', 'a': ['עוברים', 'עוברות'], 'en': 'Next month we’re moving to Tel Aviv.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'שכר דירה', 'en': 'rent'},
         {'he': 'בעל בית', 'en': 'landlord'},
         {'he': 'מרוהטת', 'en': 'furnished (f.)'},
         {'he': 'משופצת', 'en': 'renovated (f.)'},
         {'he': 'מרכזי', 'en': 'central'},
         {'he': 'רהיטים', 'en': 'furniture'},
       ]},
      {'kind': 'slang', 'he': 'על הפנים', 'literal': '“on the face”',
       'meaning': 'Terrible, awful.',
       'when': 'A flat, a film, a day, a mood. Blunt but not obscene — you can say it about the '
               'weather in front of anyone.',
       'examples': [
         {'he': 'הדירה הייתה על הפנים.', 'en': 'The flat was awful.'},
         {'he': 'הרגשתי על הפנים כל השבוע.', 'en': 'I felt terrible all week.'},
       ]},
    ],
  },
  {
    'id': 'he-07', 'n': 7, 'level': 'intermediate',
    'title': {'he': 'הפועל והמילית שלו', 'en': 'A verb and its preposition'},
    'objective': 'In Hebrew the preposition is part of the verb. Learning לחכות without ל־ is '
                 'learning half a word — which is exactly why Gimel prints them joined.',
    'blocks': [
      {'kind': 'teach', 'title': 'They come as a pair',
       'body': 'English "wait for" and Hebrew <b>לחכות ל־</b> happen to agree. Most do not: you '
               '<b>use IN</b> something (להשתמש ב), you <b>guard ON</b> it (לשמור על), you '
               '<b>suffer FROM</b> it (לסבול מ), and you <b>cause TO</b> it (לגרום ל). There is no '
               'rule — the preposition is memorised with the verb, in one piece.',
       'examples': [
         {'he': 'אני מחכה לך כבר שעה.', 'en': 'I’ve been waiting for you for an hour.'},
         {'he': 'הוא משתמש במחשב של אחותו.', 'en': 'He uses his sister’s computer.'},
         {'he': 'תשמור על הילדים.', 'en': 'Watch the kids.'},
         {'he': 'היא סובלת מכאב ראש.', 'en': 'She suffers from a headache.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות — עם המילית', 'note': 'Learn each one with its preposition.',
       'rows': [
         {'he': 'לחכות', 'en': 'to wait for', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'להשתמש', 'en': 'to use', 'pos': 'verb', 'prep': 'ב'},
         {'he': 'לשמור', 'en': 'to keep, to guard', 'pos': 'verb', 'prep': 'על'},
         {'he': 'לסבול', 'en': 'to suffer, to tolerate', 'pos': 'verb', 'prep': 'מ'},
         {'he': 'לגרום', 'en': 'to cause', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'לעזור', 'en': 'to help', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'להתקשר', 'en': 'to phone', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'לבחור', 'en': 'to choose', 'pos': 'verb', 'prep': 'ב'},
         {'he': 'לחשוב', 'en': 'to think about', 'pos': 'verb', 'prep': 'על'},
         {'he': 'לדאוג', 'en': 'to worry about', 'pos': 'verb', 'prep': 'ל'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את המילית', 'en': 'Choose the preposition',
       'instructions': 'This is the whole point of the unit. Pick the preposition the verb takes.',
       'items': [
         {'q': 'אני מחכה ___ האוטובוס.', 'options': ['ל', 'ב', 'על', 'מ'], 'a': 'ל', 'en': 'לחכות ל־'},
         {'q': 'היא משתמשת ___ מילון טוב.', 'options': ['ב', 'ל', 'על', 'מ'], 'a': 'ב', 'en': 'להשתמש ב־'},
         {'q': 'תשמרי ___ עצמך.', 'options': ['על', 'ל', 'ב', 'מ'], 'a': 'על', 'en': 'לשמור על'},
         {'q': 'הוא סובל ___ הרעש בלילה.', 'options': ['מ', 'ל', 'ב', 'על'], 'a': 'מ', 'en': 'לסבול מ־'},
         {'q': 'הגשם גרם ___ הרבה בעיות.', 'options': ['ל', 'ב', 'מ', 'על'], 'a': 'ל', 'en': 'לגרום ל־'},
         {'q': 'אתה חושב ___ זה יותר מדי.', 'options': ['על', 'ל', 'ב', 'מ'], 'a': 'על', 'en': 'לחשוב על'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את הפועל והמילית', 'en': 'Verb and preposition together',
       'instructions': 'Type both words — the verb in the present, and its preposition.',
       'example': {'q': 'אני ___ ___ אחותי כל ערב. [להתקשר] — I phone my sister every evening.',
                   'a': 'מתקשר ל'},
       'items': [
         {'q': 'הם ___ ___ הילדים בכל יום שישי. [לדאוג]', 'a': ['דואגים ל'],
          'en': 'They worry about the children every Friday.'},
         {'q': 'אני ___ ___ המסעדה הזאת. [לבחור]', 'a': ['בוחר ב', 'בוחרת ב'],
          'en': 'I choose this restaurant.'},
         {'q': 'היא ___ ___ אמא שלה בבית. [לעזור]', 'a': ['עוזרת ל', 'עוזר ל'],
          'en': 'She helps her mother at home.'},
       ]},
      {'kind': 'slang', 'he': 'חבל על הזמן', 'literal': '“a pity about the time”',
       'meaning': 'Amazing — or a total waste. Both. The tone decides.',
       'when': 'The most Israeli expression there is. Said fast and rising, it means something '
               'was so good it is beyond describing. Said flat and falling, it means do not '
               'bother. Listen for the melody before you copy it.',
       'examples': [
         {'he': 'האוכל שם חבל על הזמן!', 'en': 'The food there is incredible!'},
         {'he': 'לחכות שם שעתיים? חבל על הזמן.', 'en': 'Wait there two hours? Not worth it.'},
       ]},
    ],
  },
  {
    'id': 'he-08', 'n': 8, 'level': 'intermediate',
    'title': {'he': 'עברית של הרחוב', 'en': 'Street Hebrew'},
    'objective': 'Eight expressions you will hear on your first day in Israel and will not find '
                 'in Aleph, Bet or Gimel. Half of them are Arabic, which is the point.',
    'blocks': [
      {'kind': 'teach', 'title': 'Where Israeli slang comes from',
       'body': 'A great deal of it is <b>Arabic</b> — יאללה, סבבה, אחלה, וואלה, מבסוט — borrowed '
               'through Mizrahi Hebrew and the army and now completely ordinary. If you already '
               'speak some Palestinian Arabic you have a head start on this unit that a German '
               'or a Russian learner does not.',
       'examples': [
         {'he': 'יאללה, בוא נלך.', 'en': 'Come on, let’s go.'},
         {'he': 'אחלה רעיון!', 'en': 'Great idea!'},
         {'he': 'וואלה? לא ידעתי.', 'en': 'Really? I didn’t know.'},
       ]},
      {'kind': 'slang', 'he': 'יאללה', 'literal': 'Arabic يالله, “come on / let’s go”',
       'meaning': 'Come on, let’s go, right then.',
       'when': 'Starts things and ends them. יאללה ביי is the standard way to get off the phone.',
       'examples': [{'he': 'יאללה, אנחנו מאחרים.', 'en': 'Come on, we’re late.'},
                    {'he': 'יאללה ביי!', 'en': 'OK, bye!'}]},
      {'kind': 'slang', 'he': 'אחלה', 'literal': 'Arabic أحلى, “sweeter, best”',
       'meaning': 'Great, excellent.',
       'when': 'Goes straight in front of a noun with no agreement at all: אחלה סרט, אחלה בחורה, '
               'אחלה יום. That invariability is the giveaway that it is a loanword.',
       'examples': [{'he': 'אחלה מקום, נבוא שוב.', 'en': 'Great place, we’ll come again.'},
                    {'he': 'היה אחלה.', 'en': 'It was great.'}]},
      {'kind': 'slang', 'he': 'וואלה', 'literal': 'Arabic والله, “by God”',
       'meaning': 'Really? / Huh. / True.',
       'when': 'Mild surprise, or filling a gap while you take something in. Not an oath any more '
               '— it is closer to English “huh” or “no kidding”.',
       'examples': [{'he': 'וואלה, לא חשבתי על זה.', 'en': 'Huh, I hadn’t thought of that.'},
                    {'he': 'וואלה? מתי?', 'en': 'Really? When?'}]},
      {'kind': 'slang', 'he': 'בקיצור', 'literal': '“in short”',
       'meaning': 'Anyway. / Long story short.',
       'when': 'Cuts a story short — and is also how Israelis get to the point after a digression. '
               'Extremely common in speech, and a good one to have ready.',
       'examples': [{'he': 'בקיצור, לא הלכנו.', 'en': 'Anyway, we didn’t go.'},
                    {'he': 'בקיצור, מה קרה?', 'en': 'So — what happened?'}]},
      {'kind': 'slang', 'he': 'לדפוק לילה לבן', 'literal': '“to knock a white night”',
       'meaning': 'To stay up all night.',
       'when': 'Studying for an exam, or out until sunrise — the phrase covers both. לילה לבן on '
               'its own is the night itself.',
       'examples': [{'he': 'דפקתי לילה לבן לפני המבחן.', 'en': 'I pulled an all-nighter before the exam.'},
                    {'he': 'הלילה לא חוזרים הביתה.', 'en': 'Tonight we’re not going home.'}]},
      {'kind': 'slang', 'he': 'לעשות חיים', 'literal': '“to make life”',
       'meaning': 'To have a great time.',
       'when': 'Said to someone going away — the standard send-off before a trip.',
       'examples': [{'he': 'תעשו חיים באיטליה!', 'en': 'Have a great time in Italy!'},
                    {'he': 'עשינו חיים בקיץ.', 'en': 'We had an amazing summer.'}]},
      {'kind': 'quiz', 'title': 'מה זה אומר?', 'en': 'What does it mean?',
       'items': [
         {'q': 'Your friend says האוכל שם חבל על הזמן with a big grin. They mean —',
          'options': ['the food is amazing', 'the food is a waste of time', 'the restaurant closed'],
          'a': 'the food is amazing',
          'why': 'חבל על הזמן swings both ways and the tone decides. Grinning and rising = the good one.'},
         {'q': 'Which of these is NOT from Arabic?',
          'options': ['בקיצור', 'יאללה', 'סבבה', 'אחלה'], 'a': 'בקיצור',
          'why': 'בקיצור is ordinary Hebrew, from קיצור "shortening". The other three came in from '
                 'Arabic and are now completely at home.'},
         {'q': 'Someone ends a call with יאללה ביי. That is —',
          'options': ['completely normal', 'quite rude', 'very formal'], 'a': 'completely normal',
          'why': 'It is the default way to end a phone call between friends, and between plenty of '
                 'people who are not friends.'},
       ]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
def load_resolutions():
    p = paths.resolutions()
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def look_up(lex, word, res):
    """The lexicon's pointing and gloss for one vocabulary word, or None.

    Nothing here invents a vowel. A word the lexicon cannot answer ships unpointed and is listed
    in the build report, which is the same bargain the corpus makes: the app would rather show a
    learner a bare spelling than a pointing we made up for them.

    The resolution trail is consulted FIRST, exactly as he_ingest does it. Without that a
    vocabulary table asks the lexicon cold and prints whatever comes back first -- which for
    בוקר is "a cowboy". A word already decided once for the daily paper should not have to be
    decided again here, and certainly not differently.
    """
    want = res.get(word) or res.get(he_norm(word))
    if want:
        pick = lex.by_id.get(str(want))
        if pick is not None and lex.cut_for(he_norm(word), pick) is not None:
            from phon import respell
            voc = respell(he_norm(word), pick['FORM']) or (
                str(pick['FORM']) if he_norm(str(pick['FORM'])) == he_norm(word) else None)
            return {'voc': voc, 'say': pick['PHON'] or None,
                    'lex': str(pick['GLOSS'] or '')[:70],
                    'prov': 'wiktionary:resolved', 'id': str(pick['ID'])}
    rec, prov, cands = lex.resolve(word)
    if rec is None:
        c = he_curated.lookup(word, he_norm(word))
        if c is None:
            return None
        return {'voc': c['vocalized'] or c['lemma'], 'say': c['caphi'],
                'lex': c['gloss'], 'prov': c['provenance'], 'id': None}
    from phon import respell
    voc = respell(he_norm(word), rec['FORM']) or (
        str(rec['FORM']) if he_norm(str(rec['FORM'])) == he_norm(word) else None)
    return {'voc': voc, 'say': rec['PHON'] or None, 'lex': str(rec['GLOSS'] or '')[:70],
            'prov': prov, 'id': str(rec['ID'])}


def build(check_only=False):
    lex, res = Lexicon(), load_resolutions()
    missing, ambiguous, rows = [], [], 0
    for u in UNITS:
        for b in u['blocks']:
            if b.get('kind') != 'vocab':
                continue
            for r in b['rows']:
                rows += 1
                hit = look_up(lex, r['he'], res)
                if hit is None:
                    missing.append((u['id'], r['he'], r['en']))
                    continue
                # OURS is the teaching gloss -- short, and the one the unit is written around.
                # THEIRS is the lexicon's, kept beside it so the two can be compared on the page
                # and so nobody has to take our word for what the word means.
                r['voc'] = hit['voc']
                r['say'] = hit['say']
                r['lex'] = hit['lex']
                r['prov'] = hit['prov']
                if hit['prov'].startswith('AMBIG'):
                    ambiguous.append((u['id'], r['he'], hit['lex']))

    # The plan reads `phase` off a unit to place it on the journey (lvlTagFor's 'unit' arm), and
    # a unit with none lands in phase 0 -- which is why every one of these was reading "Beginner"
    # on the shelf whatever it taught. The level the unit was written at decides it.
    for u in UNITS:
        u['phase'] = 0 if u.get('level') == 'beginner' else 1

    n = {'teach': 0, 'vocab': 0, 'slang': 0, 'ex': 0, 'items': 0}
    for u in UNITS:
        for b in u['blocks']:
            k = b.get('kind')
            n[k if k in ('teach', 'vocab', 'slang') else 'ex'] += 1
            n['items'] += len(b.get('items') or b.get('pairs') or [])

    print('units %d   blocks: %d teach, %d vocab, %d slang, %d exercises (%d items)'
          % (len(UNITS), n['teach'], n['vocab'], n['slang'], n['ex'], n['items']))
    print('vocabulary rows %d   looked up %d   not in the lexicon %d   ambiguous %d'
          % (rows, rows - len(missing), len(missing), len(ambiguous)))
    for uid, w, en in missing:
        print('   !! %-7s %-12s "%s" — ships unpointed' % (uid, w, en))
    for uid, w, g in ambiguous[:8]:
        print('   ~  %-7s %-12s lexicon is unsure: %s' % (uid, w, g))
    if check_only:
        return 0

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// GENERATED by pipeline/he_lessons.py -- do not edit by hand.\n')
        f.write('// Interactive teaching units. The prose, the sentences and the exercise design\n')
        f.write('// are curated teaching; every word in a vocabulary table was looked up in the\n')
        f.write('// lexicon at build time and carries the pointing and gloss it found.\n')
        f.write('window.LESSONS = ')
        json.dump({'units': UNITS}, f, ensure_ascii=False)
        f.write(';\n')
    print('\n-> %s' % os.path.relpath(OUT, paths.ROOT))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='report the lexicon check, write nothing')
    ap.add_argument('--lang', default='he', help=argparse.SUPPRESS)
    a = ap.parse_args()
    return build(check_only=a.check)


if __name__ == '__main__':
    raise SystemExit(main())
