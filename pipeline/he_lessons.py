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

import hashlib                                       # noqa: E402
import re                                            # noqa: E402
import urllib.request                                # noqa: E402
import net                                           # noqa: E402  -- one HTTPS context
from voice import voice_id                           # noqa: E402  -- the pinned app voice

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
#   table      a conjugation grid with some cells printed and some to fill  (Bet)
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
      {'kind': 'choose', 'title': 'מה אומרים?', 'en': 'What do you say?',
       'instructions': 'Pick the slang word an Israeli would drop in here.',
       'items': [
         {'q': 'A friend says the food was excellent.', 'options': ['אחלה', 'וואלה', 'יאללה'],
          'a': 'אחלה', 'en': 'אחלה is the everyday “great”.'},
         {'q': 'You are all standing around and it is time to leave.',
          'options': ['יאללה', 'בקיצור', 'אחלה'], 'a': 'יאללה',
          'en': 'יאללה gets a group moving — it is Arabic, and it is in every Israeli’s mouth.'},
         {'q': 'Someone tells you something surprising and you half believe it.',
          'options': ['וואלה?', 'יאללה?', 'בקיצור?'], 'a': 'וואלה?',
          'en': 'וואלה with a rising tone is “really?”; flat, it is “huh, fair enough”.'},
         {'q': 'You have digressed for a minute and want to get back to the point.',
          'options': ['בקיצור', 'אחלה', 'וואלה'], 'a': 'בקיצור',
          'en': 'And it does not mean you are about to be brief.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['יאללה', 'אנחנו', 'הולכים', 'עכשיו'], 'a': 'יאללה אנחנו הולכים עכשיו',
          'en': 'Come on, we’re going now.'},
         {'words': ['עשינו', 'חיים', 'בסוף', 'השבוע'], 'a': 'עשינו חיים בסוף השבוע',
          'en': 'We had a great time at the weekend.'},
         {'words': ['בקיצור', 'לא', 'הגענו', 'בסוף'], 'a': 'בקיצור לא הגענו בסוף',
          'en': 'Anyway, in the end we didn’t make it.'},
       ]},
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
    # The trail may carry an "@texts" section of per-text overrides (see he_ingest.py). Lessons
    # are not texts and have no id to match against, so the global lines are what apply here --
    # but the section has to come OUT, or "@texts" reads as a surface whose resolution is a dict.
    p = paths.resolutions()
    raw = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    raw.pop('@texts', None)
    return raw


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
            # respell takes the word AS WRITTEN, never he_norm'd. he_norm folds the final
            # letters -- ם to מ, ך to כ -- and respell returns the surface it was handed, so
            # normalising first meant the vocabulary tables printed שָׁלוֹמ, כֶּסֶפ, אֵיכְ:
            # thirty-nine words wearing a medial letter at the end. respell already treats a
            # final and its medial form as the same letter internally, so it needs no help.
            voc = respell(word, pick['FORM']) or (
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
    voc = respell(word, rec['FORM']) or (
        str(rec['FORM']) if he_norm(str(rec['FORM'])) == he_norm(word) else None)
    return {'voc': voc, 'say': rec['PHON'] or None, 'lex': str(rec['GLOSS'] or '')[:70],
            'prov': prov, 'id': str(rec['ID'])}



# ==========================================================================================
# AUDIO. The Arabic lessons have been voiced since they shipped -- 1,481 clips across 44 of
# the 50 units -- and the Hebrew ones had none at all, which made the app's most-used teaching
# screen the one place where one language simply could not be heard.
#
# WHAT SPEAKS, and what deliberately does not. Arabic voices a clip per CHUNK, because an
# Arabic unit is a list of chunks to hear and repeat. A Hebrew unit is not shaped like that:
# it is blocks of worked exercises. So the rule here is about the TEXT, not the block --
# anything that is a whole Hebrew phrase a learner should hear said out loud. Single words are
# skipped on purpose: `--min-words 2` is the default because the word-audio bank already holds
# 2,057 clips and the word card plays from there, so voicing them again here would pay twice
# for the same second of speech. Anything carrying a blank (___) is skipped too -- an exercise
# prompt with a hole in it cannot be read aloud.
#
# CLIP NAMES ARE THE TEXT, not the position. Every other generator in this repo names clips
# positionally (`s0.mp3` in a directory named for the text) and that has gone wrong twice: a
# rewritten chapter adopts the previous edition's audio against different sentences, silently,
# because ingest adopts any clip it finds on disk. Here the filename is a hash of the Hebrew
# itself, so a clip can only ever be adopted against the exact words it says, a phrase repeated
# across units costs one clip rather than five, and re-running after an edit regenerates
# precisely what changed.

AUDIO_DIR = paths.audio('lessons')
_made = [0]      # clips written this run, for the failure message

# Where Hebrew that can be spoken actually lives in a block. Everything else in a unit is
# English scaffolding, a single vocabulary word, or an exercise with a hole in it.
SAY_KEYS = ('he', 'a', 'q', 'from', 'to')
BLANK = ('___', '____', '…')


def _say_texts(node, out):
    """Collect every speakable Hebrew string in a block, wherever it sits in the tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                if k in SAY_KEYS:
                    out.append((node, k, v))
            else:
                _say_texts(v, out)
    elif isinstance(node, list):
        for v in node:
            _say_texts(v, out)
    return out


def _speakable(s, min_words):
    """Is this a Hebrew phrase a learner should hear said?

    "Contains Hebrew" is not the test, and using it billed for lines like
    "What does נו do at the start of a sentence?" and "A friend tries your food and says…" --
    quiz prompts that are English sentences with one Hebrew word quoted inside them. Read by a
    Hebrew voice they are gibberish, and they are not what the clip is for. So the text has to
    be MOSTLY Hebrew: more Hebrew letters than Latin ones.
    """
    if not s or any(b in s for b in BLANK):
        return False
    heb = len(re.findall(r'[֐-׿]', s))
    lat = len(re.findall(r'[A-Za-z]', s))
    if not heb or lat >= heb:
        return False
    return len([w for w in s.split() if w.strip()]) >= min_words


def _clip_name(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:16] + '.mp3'


def tts(text, path, key, voice, model='eleven_multilingual_v2'):
    if os.path.exists(path):
        return True, 'cached'
    req = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s' % voice,
        data=json.dumps({'text': text, 'model_id': model}).encode(),
        headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=90, context=net.SSL_CTX) as r:
            open(path, 'wb').write(r.read())
        return True, 'generated'
    except Exception as e:
        # A TRANSPORT failure does not get better on the next phrase, and net.py exists because
        # this exact loop once printed the same TLS line once per item and still exited 0. If
        # net can name it -- an unverifiable certificate, a rejected key, a spent balance -- say
        # so once and stop. Anything it cannot name is per-item and the run carries on.
        if net.fatal(e, prefix='after %d clip(s): ' % _made[0]):
            raise SystemExit(1)
        return False, str(e)[:100]


def attach_audio(units, do_audio, min_words, estimate):
    """Stamp `audio` onto every speakable phrase, generating the clip when asked to.

    Adoption is unconditional and generation is not: a clip already on disk is wired into the
    data whether or not this run has a key, which is what lets the site be rebuilt on a machine
    that has none without silently dropping the audio it already has.
    """
    key, voice = os.environ.get('ELEVENLABS_API_KEY'), voice_id()
    if do_audio and not (key and voice):
        print('!! --audio requested but ELEVENLABS_API_KEY is not set; '
              'existing clips are still adopted, nothing new is generated\n')
        do_audio = False
    if do_audio:
        os.makedirs(AUDIO_DIR, exist_ok=True)

    seen, chars, made, adopted, skipped = set(), 0, 0, 0, 0
    for u in units:
        for b in u.get('blocks', []):
            for owner, k, text in _say_texts(b, []):
                if not _speakable(text, min_words):
                    skipped += 1
                    continue
                name = _clip_name(text)
                clip, rel = os.path.join(AUDIO_DIR, name), paths.audio_url('lessons', name)
                if text not in seen:
                    seen.add(text)
                    chars += len(text)
                # `audio_<field>`, not `audio`. One node can hold two speakable fields — a
                # transform item has both `from` and `to` — and a single `audio` key meant the
                # second one silently overwrote the first: 981 adoptions came out as 948 fields
                # and 24 clips were generated, paid for, and referenced by nothing.
                fld = 'audio_' + k
                if os.path.exists(clip):
                    owner[fld] = rel
                    adopted += 1
                elif do_audio:
                    ok, how = tts(text, clip, key, voice)
                    print('  %s  %-30s %s' % (name[:8], text[:28], how))
                    if ok:
                        owner[fld] = rel
                        made += 1
                        _made[0] = made
    return {'phrases': len(seen), 'chars': chars, 'adopted': adopted,
            'generated': made, 'skipped': skipped}


def build(check_only=False, do_audio=False, min_words=2, estimate=False):
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

    # TEACHING ORDER, which is not the order they were written in. The ids are stable and the
    # numbers are assigned from this list, so a unit can be moved in the sequence without
    # renaming it and losing whatever progress is filed under it. Past before future; the
    # binyanim only after pa'al is solid in all three tenses. The order also has to CLIMB: the
    # phase chip is read off the unit's level, so an intermediate unit sitting between two
    # advanced ones drops the shelf from B1 back to A2 and then up again, which reads as a
    # mistake. Street Hebrew used to close the sequence "because it is the reward"; with a real
    # advanced tier behind it that ended the course two levels below its own high point, so it
    # now closes the intermediate block and ביטויים -- the idioms, which is the same reward one
    # level up -- closes the whole thing.
    order = ['he-01', 'he-16', 'he-03', 'he-02', 'he-14', 'he-20', 'he-17', 'he-04',
             'he-57', 'he-56', 'he-66', 'he-77', 'he-46', 'he-47', 'he-48', 'he-60',
             'he-74', 'he-62', 'he-73', 'he-86', 'he-87', 'he-09', 'he-19', 'he-18',
             'he-21', 'he-10', 'he-53', 'he-65', 'he-82', 'he-05', 'he-41', 'he-42',
             'he-54', 'he-43', 'he-67', 'he-22', 'he-59', 'he-31', 'he-32', 'he-45',
             'he-49', 'he-58', 'he-50', 'he-85', 'he-63', 'he-51', 'he-76', 'he-84',
             'he-61', 'he-71', 'he-72', 'he-75', 'he-15', 'he-68', 'he-11', 'he-12',
             'he-13', 'he-23', 'he-25', 'he-55', 'he-79', 'he-26', 'he-69', 'he-78',
             'he-44', 'he-80', 'he-24', 'he-29', 'he-28', 'he-27', 'he-81', 'he-07',
             'he-30', 'he-70', 'he-06', 'he-08', 'he-33', 'he-34', 'he-36', 'he-35',
             'he-37', 'he-83', 'he-38', 'he-52', 'he-40', 'he-88', 'he-64', 'he-39']
    # NOT `missing` -- that name already holds the vocabulary the lexicon could not answer, and
    # reusing it here overwrote the list with unit ids. The report then said "8 words not in the
    # lexicon" when it meant "8 units not in the order list", and crashed trying to print them
    # as (unit, word, gloss) triples. A wrong count that looks like a real finding is worse than
    # the crash that followed it.
    unplaced = [u['id'] for u in UNITS if u['id'] not in order]
    if unplaced:
        print('   !! not placed in the teaching order, appended: %s' % ', '.join(unplaced))
    rank = {uid: i for i, uid in enumerate(order)}
    UNITS.sort(key=lambda u: rank.get(u['id'], 999))
    for i, u in enumerate(UNITS):
        u['n'] = i + 1

    # The plan reads `phase` off a unit to place it on the journey (lvlTagFor's 'unit' arm), and
    # a unit with none lands in phase 0 -- which is why every one of these was reading "Beginner"
    # on the shelf whatever it taught. The level the unit was written at decides it, against the
    # curriculum's own CEFR ladder rather than against a two-way split: app/data/he/curriculum.js
    # bands its five phases A1 / A1 / A2 / B1 / B1, so an intermediate unit is phase 2 and an
    # advanced one is phase 3. Filing every non-beginner unit under phase 1 said "A1" of work
    # that is plainly past it.
    PHASE = {'beginner': 0, 'intermediate': 2, 'advanced': 3}
    for u in UNITS:
        u['phase'] = PHASE.get(u.get('level'), 0)

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

    st = attach_audio(UNITS, do_audio, min_words, estimate)
    # ElevenLabs bills per character, and a run that turns out to be four times the size you
    # pictured is a thing to learn BEFORE spending it, not after.
    print('audio: %d phrases at >=%d words · %d adopted from disk · %d generated · %d skipped'
          % (st['phrases'], min_words, st['adopted'], st['generated'], st['skipped']))
    print('       %s characters ≈ %s credits if generated from scratch'
          % (format(st['chars'], ','), format(st['chars'], ',')))
    if estimate:
        print('\n(estimate only — nothing was generated and nothing was written)')
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
    ap.add_argument('--audio', action='store_true',
                    help='generate a clip per phrase (needs ELEVENLABS_API_KEY)')
    ap.add_argument('--min-words', type=int, default=2, metavar='N',
                    help='only voice phrases of at least N words (default 2 — single words are '
                         'already in the word-audio bank and play from the word card)')
    ap.add_argument('--estimate', action='store_true',
                    help='print the character/credit cost and exit — generates and writes nothing')
    ap.add_argument('--lang', default='he', help=argparse.SUPPRESS)
    a = ap.parse_args()
    return build(check_only=a.check, do_audio=a.audio, min_words=a.min_words,
                 estimate=a.estimate)


UNITS += [
  {
    'id': 'he-09', 'n': 9, 'level': 'beginner',
    'title': {'he': 'זמן עבר', 'en': 'The past tense'},
    'objective': 'Say what happened. The past adds ENDINGS, one per person, and it is the tense '
                 'you need first to tell anyone anything about your life.',
    'blocks': [
      {'kind': 'teach', 'title': 'The past is an ending',
       'body': 'Take the three root letters and hang the person on the end: '
               'כָּתַב<b>תִּי</b> (I), כָּתַב<b>תָּ</b> (you m.), כָּתַב<b>תְּ</b> (you f.), כָּתַב (he), '
               'כָּתְב<b>ָה</b> (she), כָּתַב<b>נוּ</b> (we), כְּתַב<b>תֶּם</b> (you pl.), כָּתְב<b>וּ</b> (they). '
               'The he-form is the bare stem — which is why dictionaries list it, and why this app '
               'files verbs under it.',
       'examples': [
         {'he': 'אתמול כתבתי לו.', 'en': 'Yesterday I wrote to him.'},
         {'he': 'היא למדה בירושלים.', 'en': 'She studied in Jerusalem.'},
         {'he': 'לא אכלנו כלום.', 'en': 'We didn’t eat anything.'},
         {'he': 'הם גרו שם שנתיים.', 'en': 'They lived there for two years.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אתמול', 'en': 'yesterday', 'pos': 'other'},
         {'he': 'שבוע', 'en': 'week', 'pos': 'noun'},
         {'he': 'חודש', 'en': 'month', 'pos': 'noun'},
         {'he': 'שנה', 'en': 'year', 'pos': 'noun'},
         {'he': 'לפגוש', 'en': 'to meet', 'pos': 'verb'},
         {'he': 'לחזור', 'en': 'to return', 'pos': 'verb'},
         {'he': 'לשכוח', 'en': 'to forget', 'pos': 'verb'},
         {'he': 'לזכור', 'en': 'to remember', 'pos': 'verb'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'Bet’s own drill. Some cells are printed, the rest you type.',
       'cols': ['שם פועל', 'הוא, עבר', 'אני, עבר', 'הם, עבר'],
       'rows': [
         [{'g': 'לכתוב'}, {'g': 'כתב'}, {'g': 'כתבתי'}, {'g': 'כתבו'}],
         [{'g': 'ללמוד'}, {'a': ['למד']}, {'a': ['למדתי']}, {'a': ['למדו']}],
         [{'g': 'לגמור'}, {'a': ['גמר']}, {'a': ['גמרתי']}, {'a': ['גמרו']}],
         [{'g': 'לזכור'}, {'a': ['זכר']}, {'a': ['זכרתי']}, {'a': ['זכרו']}],
         [{'g': 'לשכוח'}, {'a': ['שכח']}, {'a': ['שכחתי']}, {'a': ['שכחו']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל בעבר', 'en': 'Write the verb in the past',
       'instructions': 'The infinitive is in brackets; write the past form that fits the subject.',
       'example': {'q': 'אתמול אני ___ מכתב. [לכתוב]', 'a': 'כתבתי'},
       'items': [
         {'q': 'בשנה שעברה הם ___ בתל אביב. [לגור]', 'a': ['גרו'], 'en': 'Last year they lived in Tel Aviv.'},
         {'q': 'היא ___ את החברים שלה בשבת. [לפגוש]', 'a': ['פגשה'], 'en': 'She met her friends on Saturday.'},
         {'q': 'סליחה, ___ את השם שלך. [לשכוח]', 'a': ['שכחתי'], 'en': 'Sorry, I forgot your name.'},
         {'q': 'מתי אתם ___ מהחופשה? [לחזור]', 'a': ['חזרתם'], 'en': 'When did you get back from the holiday?'},
         {'q': 'אנחנו ___ עברית שנה שלמה. [ללמוד]', 'a': ['למדנו'], 'en': 'We studied Hebrew for a whole year.'},
       ]},
      {'kind': 'transform', 'title': 'מהווה לעבר', 'en': 'Present to past',
       'instructions': 'Rewrite in the past. Type the whole sentence.',
       'example': {'from': 'אני כותב מכתב.', 'to': 'כתבתי מכתב.'},
       'items': [
         {'from': 'הוא לומד בבית ספר.', 'to': ['הוא למד בבית ספר.', 'הוא למד בבית ספר'],
          'en': 'He studies at a school.'},
         {'from': 'הן חוזרות בערב.', 'to': ['הן חזרו בערב.', 'הן חזרו בערב'], 'en': 'They come back in the evening.'},
         {'from': 'אנחנו זוכרים הכל.', 'to': ['אנחנו זכרנו הכל.', 'אנחנו זכרנו הכל'], 'en': 'We remember everything.'},
       ]},
      {'kind': 'slang', 'he': 'מזמן', 'literal': '“from time”',
       'meaning': 'Ages ago / for ages.',
       'when': 'With a past verb it means "ages ago"; with לא it means "not for ages", which is '
               'where the greeting לא ראיתי אותך מזמן comes from.',
       'examples': [{'he': 'זה היה מזמן.', 'en': 'That was ages ago.'},
                    {'he': 'לא דיברנו מזמן.', 'en': 'We haven’t spoken in ages.'}]},
    ],
  },
  {
    'id': 'he-10', 'n': 10, 'level': 'intermediate',
    'title': {'he': 'פעל ל״ה', 'en': 'Verbs that end in ה'},
    'objective': 'לקנות, לרצות, לראות, לעלות — a whole family whose last root letter drops and '
                 'comes back. Bet gives them a page of their own and so does this unit.',
    'blocks': [
      {'kind': 'teach', 'title': 'The ה that is not really there',
       'body': 'These verbs look irregular and are not: their third root letter is a ה that '
               'behaves like a vowel. Present <b>קונֶה / קונָה / קונִים / קונוֹת</b>, past '
               '<b>קניתי, קנית, קנה, קנתה, קנינו, קנו</b>. Learn one — קנה — and you have '
               'לרצות, לראות, לעלות, לשתות, לבנות and a hundred more.',
       'examples': [
         {'he': 'קניתי לחם בדרך.', 'en': 'I bought bread on the way.'},
         {'he': 'ראינו סרט טוב אתמול.', 'en': 'We saw a good film yesterday.'},
         {'he': 'היא רצתה לבוא.', 'en': 'She wanted to come.'},
         {'he': 'הם עלו במדרגות.', 'en': 'They went up the stairs.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לקנות', 'en': 'to buy', 'pos': 'verb'},
         {'he': 'לרצות', 'en': 'to want', 'pos': 'verb'},
         {'he': 'לראות', 'en': 'to see', 'pos': 'verb'},
         {'he': 'לעלות', 'en': 'to go up, to cost', 'pos': 'verb'},
         {'he': 'לשתות', 'en': 'to drink', 'pos': 'verb'},
         {'he': 'לבנות', 'en': 'to build', 'pos': 'verb'},
         {'he': 'לענות', 'en': 'to answer', 'pos': 'verb'},
         {'he': 'מדרגות', 'en': 'stairs', 'pos': 'noun'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'The same grid Bet prints for this family.',
       'cols': ['שם פועל', 'הוא, הווה', 'אני, עבר', 'הוא, עבר'],
       'rows': [
         [{'g': 'לקנות'}, {'g': 'קונה'}, {'g': 'קניתי'}, {'g': 'קנה'}],
         [{'g': 'לרצות'}, {'a': ['רוצה']}, {'a': ['רציתי']}, {'a': ['רצה']}],
         [{'g': 'לראות'}, {'a': ['רואה']}, {'a': ['ראיתי']}, {'a': ['ראה']}],
         [{'g': 'לשתות'}, {'a': ['שותה']}, {'a': ['שתיתי']}, {'a': ['שתה']}],
         [{'g': 'לעלות'}, {'a': ['עולה']}, {'a': ['עליתי']}, {'a': ['עלה']}],
         [{'g': 'לבנות'}, {'a': ['בונה']}, {'a': ['בניתי']}, {'a': ['בנה']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל בעבר', 'en': 'Write the verb in the past',
       'instructions': 'All ל״ה verbs. Watch the endings — they are not the ones you learned in '
                       'unit 9.',
       'example': {'q': 'לא ידעתי שצריך ___ חלב. [לקנות] — I didn’t know we needed to buy milk.',
                   'a': 'לקנות'},
       'items': [
         {'q': 'למה הוא ___ במדרגות? [לעלות]', 'a': ['עלה'], 'en': 'Why did he go up the stairs?'},
         {'q': 'לא תודה, כבר ___ לפני שבאתי. [לשתות]', 'a': ['שתיתי'], 'en': 'No thanks, I already drank before I came.'},
         {'q': 'הם חלמו על בית, ולפני שנה הם סוף סוף ___ אותו. [לבנות]', 'a': ['בנו'],
          'en': 'They dreamed of a house, and last year they finally built it.'},
         {'q': 'שאלתי אותה והיא לא ___. [לענות]', 'a': ['ענתה'], 'en': 'I asked her and she didn’t answer.'},
         {'q': 'אנחנו ___ את הסרט הזה כבר פעמיים. [לראות]', 'a': ['ראינו'],
          'en': 'We’ve seen this film twice already.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Why is it קניתי and not קנבתי?',
          'options': ['the third root letter is a ה and drops before the ending',
                      'because קנה is irregular', 'because the root has only two letters'],
          'a': 'the third root letter is a ה and drops before the ending',
          'why': 'ק־נ־ה. The ה never survives in front of a consonant ending, and a י shows up '
                 'in its place: קָנִיתִי.'},
         {'q': 'עלה can mean “he went up” and also —',
          'options': ['“it cost”', '“he answered”', '“he built”'], 'a': '“it cost”',
          'why': 'כמה זה עולה? is “how much does it cost?” — the same verb.'},
       ]},
      {'kind': 'slang', 'he': 'כמה זה עולה', 'literal': '“how much does it go up”',
       'meaning': 'How much is it?',
       'when': 'The only way to ask a price. לעלות does double duty as “rise” and “cost”, which '
               'is why this unit’s verb family is the one you need in a shop.',
       'examples': [{'he': 'סליחה, כמה זה עולה?', 'en': 'Excuse me, how much is this?'},
                    {'he': 'זה עלה לי הרבה כסף.', 'en': 'That cost me a lot of money.'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-11', 'n': 11, 'level': 'intermediate',
    'title': {'he': 'בניין פיעל', 'en': 'The piel binyan'},
    'objective': 'The second big verb pattern. Once you can hear פיעל you can guess the meaning '
                 'of verbs you have never met, which is the whole reason binyanim are worth learning.',
    'blocks': [
      {'kind': 'teach', 'title': 'Doubled middle, and often intensive',
       'body': 'פיעל doubles the middle root letter and drops the vowel pattern in: '
               '<b>דִּבֵּר</b>, <b>סִפֵּר</b>, <b>שִׁלֵּם</b>. The infinitive always starts '
               'לְ־ + the shape: לדבר, לספר, לשלם. Many are the "doing" version of a noun — '
               'טיול a trip, <b>לטייל</b> to travel around; ספר a book, <b>לספר</b> to tell.',
       'examples': [
         {'he': 'הוא דיבר איתי אתמול.', 'en': 'He spoke with me yesterday.'},
         {'he': 'ספרי לי מה קרה.', 'en': 'Tell me what happened.'},
         {'he': 'שילמנו על הכל.', 'en': 'We paid for everything.'},
         {'he': 'טיילנו בצפון שבוע.', 'en': 'We travelled around the north for a week.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לדבר', 'en': 'to speak', 'pos': 'verb', 'prep': 'עם'},
         {'he': 'לספר', 'en': 'to tell', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'לשלם', 'en': 'to pay', 'pos': 'verb', 'prep': 'על'},
         {'he': 'לטייל', 'en': 'to travel around, to hike', 'pos': 'verb'},
         {'he': 'לבשל', 'en': 'to cook', 'pos': 'verb'},
         {'he': 'לחפש', 'en': 'to look for', 'pos': 'verb'},
         {'he': 'לקבל', 'en': 'to receive', 'pos': 'verb'},
         {'he': 'לסדר', 'en': 'to arrange, to tidy', 'pos': 'verb'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'All piel. The doubling is in the middle letter every time.',
       'cols': ['שם פועל', 'הוא, הווה', 'אני, עבר', 'הוא, עתיד'],
       'rows': [
         [{'g': 'לדבר'}, {'g': 'מדבר'}, {'g': 'דיברתי'}, {'g': 'ידבר'}],
         [{'g': 'לספר'}, {'a': ['מספר']}, {'a': ['סיפרתי']}, {'a': ['יספר']}],
         [{'g': 'לשלם'}, {'a': ['משלם']}, {'a': ['שילמתי']}, {'a': ['ישלם']}],
         [{'g': 'לבשל'}, {'a': ['מבשל']}, {'a': ['בישלתי']}, {'a': ['יבשל']}],
         [{'g': 'לחפש'}, {'a': ['מחפש']}, {'a': ['חיפשתי']}, {'a': ['יחפש']}],
       ]},
      {'kind': 'choose', 'title': 'בחרו את המילית', 'en': 'Choose the preposition',
       'instructions': 'Piel verbs come with their prepositions too.',
       'items': [
         {'q': 'דיברתי ___ המנהל אתמול.', 'options': ['עם', 'ל', 'ב', 'על'], 'a': 'עם', 'en': 'לדבר עם'},
         {'q': 'ספר ___ מה קרה!', 'options': ['ל', 'עם', 'ב', 'מ'], 'a': 'ל', 'en': 'לספר ל־'},
         {'q': 'מי משלם ___ הארוחה?', 'options': ['על', 'ל', 'ב', 'עם'], 'a': 'על', 'en': 'לשלם על'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Complete the sentence',
       'instructions': 'Type the piel verb in the present.',
       'example': {'q': 'אני ___ עם אמא שלי כל יום. [לדבר]', 'a': 'מדבר'},
       'items': [
         {'q': 'היא ___ ארוחת ערב עכשיו. [לבשל]', 'a': ['מבשלת'], 'en': 'She’s cooking dinner now.'},
         {'q': 'אנחנו ___ דירה חדשה. [לחפש]', 'a': ['מחפשים', 'מחפשות'], 'en': 'We’re looking for a new flat.'},
         {'q': 'הם ___ מכתבים מהבנק כל חודש. [לקבל]', 'a': ['מקבלים'], 'en': 'They get letters from the bank every month.'},
       ]},
      {'kind': 'slang', 'he': 'דיברנו', 'literal': '“we spoke”',
       'meaning': 'Deal. / Agreed. / We’ll be in touch.',
       'when': 'Closing an arrangement — the Hebrew equivalent of "right, we’ll speak". Said on '
               'its own at the end of a call or a conversation, and it means the thing is settled.',
       'examples': [{'he': 'סבבה, דיברנו.', 'en': 'Cool — we’ll be in touch.'},
                    {'he': 'אז מחר בשמונה? דיברנו.', 'en': 'So tomorrow at eight? Deal.'}]},
    ],
  },
  {
    'id': 'he-12', 'n': 12, 'level': 'intermediate',
    'title': {'he': 'בניין הפעיל', 'en': 'The hifil binyan'},
    'objective': 'The causative: making someone else do the thing. It is also where a surprising '
                 'number of the most ordinary verbs live — להגיע, להתחיל, להסביר, להזמין.',
    'blocks': [
      {'kind': 'teach', 'title': 'A ה in front, and someone else does it',
       'body': 'הפעיל puts <b>הִ־</b> on the front and often means "cause to": כתב he wrote, '
               '<b>הכתיב</b> he dictated; בא he came, <b>הביא</b> he brought. The present starts '
               'with מַ־: <b>מגיע, מתחיל, מסביר</b>. Do not let the "causative" label mislead you '
               '— many hifil verbs are just ordinary words that happen to live here.',
       'examples': [
         {'he': 'מתי אתה מגיע?', 'en': 'When are you arriving?'},
         {'he': 'היא הסבירה לי הכל.', 'en': 'She explained everything to me.'},
         {'he': 'הזמנתי שולחן לשמונה.', 'en': 'I booked a table for eight.'},
         {'he': 'הם התחילו בלעדינו.', 'en': 'They started without us.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להגיע', 'en': 'to arrive', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'להתחיל', 'en': 'to begin', 'pos': 'verb'},
         {'he': 'להסביר', 'en': 'to explain', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'להזמין', 'en': 'to order, to invite', 'pos': 'verb'},
         {'he': 'להביא', 'en': 'to bring', 'pos': 'verb'},
         {'he': 'להחליט', 'en': 'to decide', 'pos': 'verb'},
         {'he': 'להרגיש', 'en': 'to feel', 'pos': 'verb'},
         {'he': 'להכיר', 'en': 'to know, to be acquainted with', 'pos': 'verb'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'Present in מ־, past in ה־, future in י־.',
       'cols': ['שם פועל', 'הוא, הווה', 'הוא, עבר', 'הוא, עתיד'],
       'rows': [
         [{'g': 'להגיע'}, {'g': 'מגיע'}, {'g': 'הגיע'}, {'g': 'יגיע'}],
         [{'g': 'להתחיל'}, {'a': ['מתחיל']}, {'a': ['התחיל']}, {'a': ['יתחיל']}],
         [{'g': 'להסביר'}, {'a': ['מסביר']}, {'a': ['הסביר']}, {'a': ['יסביר']}],
         [{'g': 'להזמין'}, {'a': ['מזמין']}, {'a': ['הזמין']}, {'a': ['יזמין']}],
         [{'g': 'להחליט'}, {'a': ['מחליט']}, {'a': ['החליט']}, {'a': ['יחליט']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל', 'en': 'Write the verb',
       'instructions': 'Tense is whatever the sentence needs — read the time words.',
       'example': {'q': 'אתמול הוא ___ מאוחר. [להגיע]', 'a': 'הגיע'},
       'items': [
         {'q': 'מחר אנחנו ___ בשמונה בבוקר. [להתחיל]', 'a': ['נתחיל'], 'en': 'Tomorrow we’ll start at eight.'},
         {'q': 'המורה ___ לנו את זה פעמיים כבר. [להסביר]', 'a': ['הסביר', 'הסבירה'],
          'en': 'The teacher has explained it to us twice already.'},
         {'q': 'אני ___ שולחן לשניים, בבקשה. [להזמין]', 'a': ['מזמין', 'מזמינה'],
          'en': 'I’d like to book a table for two, please.'},
         {'q': 'הם עוד לא ___ איפה לגור. [להחליט]', 'a': ['החליטו'], 'en': 'They haven’t decided where to live yet.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'מגיע', 'en': 'arriving'},
         {'he': 'מסביר', 'en': 'explaining'},
         {'he': 'מזמין', 'en': 'ordering'},
         {'he': 'מרגיש', 'en': 'feeling'},
         {'he': 'מביא', 'en': 'bringing'},
         {'he': 'מחליט', 'en': 'deciding'},
       ]},
      {'kind': 'slang', 'he': 'מה נסגר', 'literal': '“what got closed”',
       'meaning': 'What’s going on? / What’s the deal?',
       'when': 'Asking what is happening, usually with an edge — surprise, confusion or mild '
               'annoyance. מה נסגר איתו? is “what is up with him?”.',
       'examples': [{'he': 'מה נסגר פה?', 'en': 'What’s going on here?'},
                    {'he': 'מה נסגר עם המסיבה?', 'en': 'So what’s the deal with the party?'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-13', 'n': 13, 'level': 'intermediate',
    'title': {'he': 'בניין התפעל', 'en': 'The hitpael binyan'},
    'objective': 'Things you do to yourself, and things people do to each other. Once you spot the '
                 'מת־ at the front you can read half the verbs on an Israeli sign.',
    'blocks': [
      {'kind': 'teach', 'title': 'הת־ at the front, and it comes back to you',
       'body': 'הִתְפַּעֵל is reflexive or reciprocal: לבש he dressed someone, '
               '<b>התלבש</b> he got dressed; כתב he wrote, <b>התכתב</b> they wrote to each other. '
               'Present is <b>מתלבש</b>, past <b>התלבשתי</b>. When the root starts with ס, שׂ, שׁ or '
               'צ the ת swaps places with it: <b>להשתמש</b>, not להתשמש.',
       'examples': [
         {'he': 'אני מתלבש ויוצא.', 'en': 'I’m getting dressed and heading out.'},
         {'he': 'התקשרתי אליך אתמול.', 'en': 'I called you yesterday.'},
         {'he': 'הם התחתנו בקיץ.', 'en': 'They got married in the summer.'},
         {'he': 'איך משתמשים בזה?', 'en': 'How do you use this?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להתלבש', 'en': 'to get dressed', 'pos': 'verb'},
         {'he': 'להתקשר', 'en': 'to phone', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'להתחתן', 'en': 'to get married', 'pos': 'verb', 'prep': 'עם'},
         {'he': 'להשתמש', 'en': 'to use', 'pos': 'verb', 'prep': 'ב'},
         {'he': 'להתעורר', 'en': 'to wake up', 'pos': 'verb'},
         {'he': 'להצטער', 'en': 'to be sorry', 'pos': 'verb'},
         {'he': 'להתרגש', 'en': 'to get excited', 'pos': 'verb'},
         {'he': 'להסתדר', 'en': 'to manage, to work out', 'pos': 'verb'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'Two of these swap the ת with the first root letter. Watch for them.',
       'cols': ['שם פועל', 'הוא, הווה', 'אני, עבר', 'הם, עתיד'],
       'rows': [
         [{'g': 'להתלבש'}, {'g': 'מתלבש'}, {'g': 'התלבשתי'}, {'g': 'יתלבשו'}],
         [{'g': 'להתקשר'}, {'a': ['מתקשר']}, {'a': ['התקשרתי']}, {'a': ['יתקשרו']}],
         [{'g': 'להתעורר'}, {'a': ['מתעורר']}, {'a': ['התעוררתי']}, {'a': ['יתעוררו']}],
         [{'g': 'להשתמש'}, {'a': ['משתמש']}, {'a': ['השתמשתי']}, {'a': ['ישתמשו']}],
         [{'g': 'להסתדר'}, {'a': ['מסתדר']}, {'a': ['הסתדרתי']}, {'a': ['יסתדרו']}],
       ]},
      {'kind': 'quiz', 'title': 'למה ת מתחלפת?', 'en': 'Why does the ת move?',
       'items': [
         {'q': 'Why is it להשתמש and not להתשמש?',
          'options': ['the root starts with ש, so the ת swaps places with it',
                      'because the verb is irregular',
                      'because it is a foreign word'],
          'a': 'the root starts with ש, so the ת swaps places with it',
          'why': 'ש־מ־ש. A root beginning ס, שׂ, שׁ or צ trades places with the ת of הת־ because the '
                 'other order is unpronounceable. Same with להסתדר from ס־ד־ר.'},
         {'q': 'התכתבנו means —',
          'options': ['we wrote to each other', 'we wrote it down', 'we were written about'],
          'a': 'we wrote to each other',
          'why': 'Hitpael is reciprocal as well as reflexive — the action goes back and forth '
                 'between the people doing it.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['אני', 'מתעורר', 'בשש', 'כל', 'בוקר'], 'a': 'אני מתעורר בשש כל בוקר',
          'en': 'I wake up at six every morning.'},
         {'words': ['הם', 'התחתנו', 'לפני', 'שנתיים'], 'a': 'הם התחתנו לפני שנתיים',
          'en': 'They got married two years ago.'},
         {'words': ['איך', 'משתמשים', 'במכונה', 'הזאת'], 'a': 'איך משתמשים במכונה הזאת',
          'en': 'How do you use this machine?'},
       ]},
      {'kind': 'slang', 'he': 'יסתדר', 'literal': '“it will arrange itself”',
       'meaning': 'It’ll work out.',
       'when': 'The hitpael cousin of יהיה בסדר, and just as common. להסתדר also means to manage '
               'or to get along: אני מסתדר "I’m managing", הם מסתדרים "they get on".',
       'examples': [{'he': 'אל תדאג, יסתדר.', 'en': 'Don’t worry, it’ll work out.'},
                    {'he': 'אנחנו מסתדרים יפה.', 'en': 'We get along well.'}]},
    ],
  },
  {
    'id': 'he-14', 'n': 14, 'level': 'beginner',
    'title': {'he': 'שם ותואר', 'en': 'Nouns and adjectives'},
    'objective': 'The adjective follows the noun and agrees with it — in gender, in number, and in '
                 'definiteness. That third one is the piece English does not have and learners drop.',
    'blocks': [
      {'kind': 'teach', 'title': 'It agrees three times',
       'body': 'The adjective comes AFTER: <b>בית גדול</b>, a big house. It agrees in gender and '
               'number — <b>דירה גדולה</b>, <b>בתים גדולים</b>. And if the noun is definite the '
               'adjective takes ה too: <b>הבית הגדול</b>, "the big house". Say הבית גדול and you '
               'have said a different thing: "the house is big".',
       'examples': [
         {'he': 'בית גדול', 'en': 'a big house'},
         {'he': 'הבית הגדול', 'en': 'the big house'},
         {'he': 'הבית גדול.', 'en': 'The house is big.'},
         {'he': 'הדירות החדשות יקרות.', 'en': 'The new flats are expensive.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'גדול', 'en': 'big', 'pos': 'adj'},
         {'he': 'קטן', 'en': 'small', 'pos': 'adj'},
         {'he': 'חדש', 'en': 'new', 'pos': 'adj'},
         {'he': 'ישן', 'en': 'old', 'pos': 'adj'},
         {'he': 'יפה', 'en': 'beautiful', 'pos': 'adj'},
         {'he': 'קשה', 'en': 'hard, difficult', 'pos': 'adj'},
         {'he': 'קל', 'en': 'easy, light', 'pos': 'adj'},
         {'he': 'עייף', 'en': 'tired', 'pos': 'adj'},
         {'he': 'שמח', 'en': 'happy', 'pos': 'adj'},
         {'he': 'עצוב', 'en': 'sad', 'pos': 'adj'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את הצורה', 'en': 'Choose the right form',
       'instructions': 'Gender, number, and the ה if the noun has one.',
       'items': [
         {'q': 'דירה ___', 'options': ['גדולה', 'גדול', 'גדולים'], 'a': 'גדולה',
          'en': 'דירה is feminine singular.'},
         {'q': 'הספרים ___', 'options': ['החדשים', 'חדשים', 'החדש'], 'a': 'החדשים',
          'en': 'Definite noun → the adjective takes ה as well.'},
         {'q': 'ילדות ___', 'options': ['שמחות', 'שמחים', 'שמחה'], 'a': 'שמחות',
          'en': 'Feminine plural.'},
         {'q': 'הבית ___ מאוד.', 'options': ['ישן', 'הישן', 'ישנה'], 'a': 'ישן',
          'en': 'No ה here — this is a sentence, "the house is very old", not a phrase.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את שם התואר', 'en': 'Complete the adjective',
       'instructions': 'Type the adjective in the form the noun needs.',
       'example': {'q': 'ספר ___ (חדש) — a new book', 'a': 'חדש'},
       'items': [
         {'q': 'מכונית ___ (ישן)', 'a': ['ישנה'], 'en': 'an old car'},
         {'q': 'הבחורות ___ (עייף)', 'a': ['העייפות'], 'en': 'the tired girls'},
         {'q': 'שאלות ___ (קשה)', 'a': ['קשות'], 'en': 'difficult questions'},
         {'q': 'הילד ___ (שמח)', 'a': ['השמח'], 'en': 'the happy child'},
       ]},
      {'kind': 'transform', 'title': 'מיחיד לרבים', 'en': 'Singular to plural',
       'instructions': 'Rewrite the phrase in the plural. Type the whole thing.',
       'example': {'from': 'בית גדול', 'to': 'בתים גדולים'},
       'items': [
         {'from': 'דירה יפה', 'to': ['דירות יפות'], 'en': 'a beautiful flat'},
         {'from': 'הספר החדש', 'to': ['הספרים החדשים'], 'en': 'the new book'},
         {'from': 'ילד עצוב', 'to': ['ילדים עצובים'], 'en': 'a sad child'},
       ]},
      {'kind': 'slang', 'he': 'מגניב', 'literal': '“sneaking, smuggling”',
       'meaning': 'Cool.',
       'when': 'Younger than סבבה and a little more enthusiastic. It is an adjective, so it '
               'agrees when it wants to — but most people leave it flat: זה מגניב.',
       'examples': [{'he': 'וואו, זה ממש מגניב.', 'en': 'Wow, that’s really cool.'},
                    {'he': 'מגניב, נתראה שם.', 'en': 'Cool, see you there.'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-15', 'n': 15, 'level': 'intermediate',
    'title': {'he': 'סמיכות', 'en': 'The construct: two nouns stuck together'},
    'objective': 'בית ספר, שכר דירה, ארוחת ערב. Hebrew builds compounds by welding two nouns, and '
                 'the FIRST one changes shape. It is everywhere and it is invisible until you see it.',
    'blocks': [
      {'kind': 'teach', 'title': 'The first noun bends',
       'body': 'English says "a school" as two separate words with "of" understood; Hebrew says '
               '<b>בֵּית סֵפֶר</b> — literally "house of book". The first noun goes into the '
               'construct form: בַּיִת becomes בֵּית, אֲרוּחָה becomes אֲרוּחַת, שָׂכָר becomes שְׂכַר. '
               'And the ה of "the" goes on the SECOND word, never the first: <b>בית הספר</b>.',
       'examples': [
         {'he': 'בית ספר', 'en': 'a school (“house of book”)'},
         {'he': 'בית הספר', 'en': 'the school'},
         {'he': 'ארוחת ערב', 'en': 'dinner (“meal of evening”)'},
         {'he': 'שכר הדירה גבוה.', 'en': 'The rent is high.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ארוחה', 'en': 'meal', 'pos': 'noun'},
         {'he': 'תחנה', 'en': 'station, stop', 'pos': 'noun'},
         {'he': 'חנות', 'en': 'shop', 'pos': 'noun'},
         {'he': 'עוגה', 'en': 'cake', 'pos': 'noun'},
         {'he': 'קפה', 'en': 'coffee', 'pos': 'noun'},
         {'he': 'רחוב', 'en': 'street', 'pos': 'noun'},
         {'he': 'מסעדה', 'en': 'restaurant', 'pos': 'noun'},
         {'he': 'חוף', 'en': 'beach, shore', 'pos': 'noun'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match the compound',
       'instructions': 'Tap the Hebrew, then what it actually means.',
       'pairs': [
         {'he': 'בית ספר', 'en': 'school'},
         {'he': 'בית חולים', 'en': 'hospital'},
         {'he': 'ארוחת בוקר', 'en': 'breakfast'},
         {'he': 'תחנת רכבת', 'en': 'train station'},
         {'he': 'שכר דירה', 'en': 'rent'},
         {'he': 'חוף הים', 'en': 'the seashore'},
       ]},
      {'kind': 'choose', 'title': 'איפה ה־?', 'en': 'Where does the ה go?',
       'instructions': 'Make each compound definite. Only one of these is Hebrew.',
       'items': [
         {'q': 'the school', 'options': ['בית הספר', 'הבית ספר', 'הבית הספר'], 'a': 'בית הספר',
          'en': 'The ה goes on the second noun only.'},
         {'q': 'the dinner', 'options': ['ארוחת הערב', 'הארוחת ערב', 'הארוחה ערב'],
          'a': 'ארוחת הערב', 'en': 'Same rule, every time.'},
         {'q': 'the train station', 'options': ['תחנת הרכבת', 'התחנת רכבת', 'התחנה הרכבת'],
          'a': 'תחנת הרכבת', 'en': 'The first word stays in the construct form and takes no ה.'},
       ]},
      {'kind': 'fill', 'title': 'בנו סמיכות', 'en': 'Build the compound',
       'instructions': 'Type the whole compound, definite where the English is.',
       'example': {'q': 'the coffee shop → ___', 'a': 'בית הקפה'},
       'items': [
         {'q': 'breakfast → ___', 'a': ['ארוחת בוקר'], 'en': 'meal + morning'},
         {'q': 'the restaurant’s name → שם ___', 'a': ['המסעדה'], 'en': 'name of + the restaurant'},
         {'q': 'a bus station → ___', 'a': ['תחנת אוטובוס'], 'en': 'station + bus'},
       ]},
      {'kind': 'slang', 'he': 'בית קפה', 'literal': '“house of coffee”',
       'meaning': 'A café.',
       'when': 'Worth knowing as a compound rather than a word, because it is the model for '
               'dozens of them: בית ספר, בית חולים, בית כנסת, בית משפט. Learn the pattern and you '
               'get the whole family.',
       'examples': [{'he': 'נפגשים בבית קפה?', 'en': 'Shall we meet at a café?'},
                    {'he': 'בית הקפה הזה הכי טוב בעיר.', 'en': 'This café is the best in town.'}]},
    ],
  },
  {
    'id': 'he-16', 'n': 16, 'level': 'beginner',
    'title': {'he': 'מילות שאלה', 'en': 'Question words'},
    'objective': 'Seven words that turn you from someone who answers into someone who can ask — '
                 'which is the point at which a conversation starts going somewhere.',
    'blocks': [
      {'kind': 'teach', 'title': 'Ask, and the word order barely moves',
       'body': 'Hebrew questions do not need "do" the way English does. Put the question word at '
               'the front and leave the rest alone: אתה גר פה → <b>איפה</b> אתה גר? And a yes/no '
               'question is just the statement with a rising tone, or with <b>האם</b> in writing.',
       'examples': [
         {'he': 'מה השם שלך?', 'en': 'What’s your name?'},
         {'he': 'איפה אתה גר?', 'en': 'Where do you live?'},
         {'he': 'מתי הם מגיעים?', 'en': 'When are they arriving?'},
         {'he': 'למה לא אמרת לי?', 'en': 'Why didn’t you tell me?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'מה', 'en': 'what', 'pos': 'other'},
         {'he': 'מי', 'en': 'who', 'pos': 'other'},
         {'he': 'איפה', 'en': 'where', 'pos': 'other'},
         {'he': 'מתי', 'en': 'when', 'pos': 'other'},
         {'he': 'למה', 'en': 'why', 'pos': 'other'},
         {'he': 'איך', 'en': 'how', 'pos': 'other'},
         {'he': 'כמה', 'en': 'how much, how many', 'pos': 'other'},
         {'he': 'לאן', 'en': 'where to', 'pos': 'other'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את מילת השאלה', 'en': 'Complete the question word',
       'instructions': 'The answer underneath tells you which word is missing.',
       'example': {'q': '___ אתה גר? — בתל אביב.', 'a': 'איפה'},
       'items': [
         {'q': '___ זה עולה? — חמישים שקל.', 'a': ['כמה'], 'en': '“How much is it?” — Fifty shekels.'},
         {'q': '___ אתם נוסעים? — לים.', 'a': ['לאן'], 'en': '“Where are you going?” — To the sea.'},
         {'q': '___ לא באת אתמול? — כי הייתי חולה.', 'a': ['למה'], 'en': '“Why didn’t you come?” — Because I was ill.'},
         {'q': '___ מגיע מחר? — דני ורותי.', 'a': ['מי'], 'en': '“Who’s coming tomorrow?” — Dani and Ruti.'},
         {'q': '___ קוראים לך? — יעל.', 'a': ['איך'], 'en': '“What’s your name?” — literally “how do they call you”.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את השאלה', 'en': 'Build the question',
       'instructions': 'Tap the words in order.',
       'items': [
         {'words': ['מתי', 'אתה', 'חוזר', 'הביתה'], 'a': 'מתי אתה חוזר הביתה',
          'en': 'When are you coming home?'},
         {'words': ['כמה', 'זמן', 'אתם', 'גרים', 'פה'], 'a': 'כמה זמן אתם גרים פה',
          'en': 'How long have you lived here?'},
         {'words': ['למה', 'היא', 'לא', 'רוצה', 'לבוא'], 'a': 'למה היא לא רוצה לבוא',
          'en': 'Why doesn’t she want to come?'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'How do Israelis usually ask someone’s name?',
          'options': ['איך קוראים לך?', 'מה השם שלך?', 'both, and the first is more common'],
          'a': 'both, and the first is more common',
          'why': 'איך קוראים לך — “how do they call you” — is the everyday one. מה השם שלך is '
                 'correct and a bit more formal.'},
         {'q': 'איפה and לאן differ how?',
          'options': ['איפה is where something IS, לאן is where it is GOING',
                      'they are interchangeable', 'לאן is more polite'],
          'a': 'איפה is where something IS, לאן is where it is GOING',
          'why': 'Hebrew keeps them apart the way older English kept "where" and "whither".'},
       ]},
      {'kind': 'slang', 'he': 'מה פתאום', 'literal': '“what suddenly”',
       'meaning': 'No way / of course not / don’t be silly.',
       'when': 'Rejecting a suggestion or an accusation, usually warmly. It is also how you wave '
               'away thanks or an offer to pay.',
       'examples': [{'he': 'מה פתאום, אני משלם.', 'en': 'Don’t be silly, I’m paying.'},
                    {'he': 'מה פתאום! לא אמרתי את זה.', 'en': 'No way! I didn’t say that.'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-17', 'n': 17, 'level': 'beginner',
    'title': {'he': 'מספרים ושעות', 'en': 'Numbers and telling the time'},
    'objective': 'Hebrew numbers have a gender, and they take the OPPOSITE one from the noun they '
                 'count. It trips up every learner, so it gets a unit of its own.',
    'blocks': [
      {'kind': 'teach', 'title': 'The numbers are backwards on purpose',
       'body': 'A masculine noun takes the feminine-looking number, and a feminine noun takes the '
               'plain one: <b>שלושה ילדים</b> (m.) but <b>שלוש ילדות</b> (f.). The ־ה forms go with '
               'masculine nouns. Nobody can explain why; everyone has to learn it. For the time '
               'you always use the FEMININE set, because שעה is feminine: <b>שלוש</b>, not שלושה.',
       'examples': [
         {'he': 'שני ילדים ושלוש בנות', 'en': 'two boys and three girls'},
         {'he': 'השעה עכשיו ארבע.', 'en': 'It’s four o’clock now.'},
         {'he': 'בשעה שמונה בערב', 'en': 'at eight in the evening'},
         {'he': 'רבע לשש', 'en': 'quarter to six'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אחד', 'en': 'one', 'pos': 'num'},
         {'he': 'שתיים', 'en': 'two (f.)', 'pos': 'num'},
         {'he': 'שלוש', 'en': 'three (f.)', 'pos': 'num'},
         {'he': 'ארבע', 'en': 'four (f.)', 'pos': 'num'},
         {'he': 'חמש', 'en': 'five (f.)', 'pos': 'num'},
         {'he': 'עשר', 'en': 'ten (f.)', 'pos': 'num'},
         {'he': 'שעה', 'en': 'hour, o’clock', 'pos': 'noun'},
         {'he': 'דקה', 'en': 'minute', 'pos': 'noun'},
         {'he': 'חצי', 'en': 'half', 'pos': 'noun'},
         {'he': 'רבע', 'en': 'quarter', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את המספר', 'en': 'Choose the number',
       'instructions': 'Masculine noun → the ־ה form. Feminine noun → the plain one.',
       'items': [
         {'q': '___ ילדים', 'options': ['שלושה', 'שלוש', 'שלושת'], 'a': 'שלושה',
          'en': 'ילדים is masculine, so the number takes ־ה.'},
         {'q': '___ בנות', 'options': ['שלוש', 'שלושה', 'שלושת'], 'a': 'שלוש',
          'en': 'בנות is feminine, so the number stays plain.'},
         {'q': '___ ספרים', 'options': ['חמישה', 'חמש', 'חמישית'], 'a': 'חמישה',
          'en': 'ספרים is masculine.'},
         {'q': 'השעה ___.', 'options': ['ארבע', 'ארבעה', 'רביעי'], 'a': 'ארבע',
          'en': 'The time is always feminine — שעה is a feminine noun.'},
       ]},
      {'kind': 'fill', 'title': 'מה השעה?', 'en': 'What time is it?',
       'instructions': 'Type the missing word.',
       'example': {'q': '8:30 → שמונה ו___', 'a': 'חצי'},
       'items': [
         {'q': '6:15 → שש ו___', 'a': ['רבע'], 'en': 'quarter past six'},
         {'q': '5:45 → ___ לשש', 'a': ['רבע'], 'en': 'quarter to six'},
         {'q': '9:30 → תשע ו___', 'a': ['חצי'], 'en': 'half past nine'},
         {'q': 'ניפגש ___ שמונה בערב.', 'a': ['בשעה'], 'en': 'We’ll meet at eight in the evening.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match the time',
       'instructions': 'Tap the Hebrew, then the clock time.',
       'pairs': [
         {'he': 'שבע ורבע', 'en': '7:15'},
         {'he': 'עשר וחצי', 'en': '10:30'},
         {'he': 'רבע לשלוש', 'en': '2:45'},
         {'he': 'שתים עשרה', 'en': '12:00'},
         {'he': 'חמש ועשרה', 'en': '5:10'},
       ]},
      {'kind': 'slang', 'he': 'עוד חמש דקות', 'literal': '“another five minutes”',
       'meaning': 'In a minute — and often, considerably longer.',
       'when': 'The universal Israeli estimate. Take it as "soon-ish" rather than as five '
               'minutes, and you will be right more often.',
       'examples': [{'he': 'אני מגיע, עוד חמש דקות.', 'en': 'I’m on my way, five minutes.'},
                    {'he': 'רגע, עוד שנייה.', 'en': 'Hang on, one second.'}]},
    ],
  },
  {
    'id': 'he-18', 'n': 18, 'level': 'beginner',
    'title': {'he': 'ציווי ובקשות', 'en': 'Telling and asking'},
    'objective': 'How to ask for something without sounding rude — which in Hebrew is not what an '
                 'English speaker expects, because the blunt form is the normal one.',
    'blocks': [
      {'kind': 'teach', 'title': 'The imperative is not rude',
       'body': 'Hebrew’s command form — <b>תן</b> give, <b>בוא</b> come, <b>תגיד</b> tell — is '
               'ordinary and polite enough with בבקשה. In speech most people use the FUTURE as a '
               'softer command: <b>תיתן לי</b>, <b>תגיד לי</b>. For "don’t", use <b>אל</b> plus the '
               'future: אל תלך. Never לא — that is a statement, not an instruction.',
       'examples': [
         {'he': 'תן לי את זה, בבקשה.', 'en': 'Give me that, please.'},
         {'he': 'בוא נלך.', 'en': 'Let’s go.'},
         {'he': 'אל תדאג.', 'en': 'Don’t worry.'},
         {'he': 'אפשר לקבל את החשבון?', 'en': 'Could I have the bill?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אפשר', 'en': 'is it possible, may I', 'pos': 'other'},
         {'he': 'אסור', 'en': 'forbidden, not allowed', 'pos': 'other'},
         {'he': 'מותר', 'en': 'allowed', 'pos': 'other'},
         {'he': 'צריך', 'en': 'need to, must', 'pos': 'other'},
         {'he': 'לבוא', 'en': 'to come', 'pos': 'verb'},
         {'he': 'לחכות', 'en': 'to wait', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'לשבת', 'en': 'to sit', 'pos': 'verb'},
         {'he': 'לקום', 'en': 'to get up', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'איך אומרים את זה?', 'en': 'How do you say it?',
       'instructions': 'Pick the form an Israeli would actually use.',
       'items': [
         {'q': 'Don’t go!', 'options': ['אל תלך!', 'לא תלך!', 'לא ללכת!'], 'a': 'אל תלך!',
          'en': '“Don’t” is אל plus the future. לא makes a statement about the future instead.'},
         {'q': 'May I sit here?', 'options': ['אפשר לשבת פה?', 'אני שבתי פה?', 'מותר אני לשבת?'],
          'a': 'אפשר לשבת פה?', 'en': 'אפשר + infinitive is the everyday polite request.'},
         {'q': 'Wait a moment.', 'options': ['חכה רגע', 'חיכיתי רגע', 'לחכות רגע'], 'a': 'חכה רגע',
          'en': 'The bare imperative, and it is not rude.'},
       ]},
      {'kind': 'transform', 'title': 'מבקשה לשלילה', 'en': 'Turn the request into a prohibition',
       'instructions': 'Rewrite each command with אל. Type the whole thing.',
       'example': {'from': 'תלך!', 'to': 'אל תלך!'},
       'items': [
         {'from': 'תדאג!', 'to': ['אל תדאג!', 'אל תדאג'], 'en': 'Worry! → Don’t worry!'},
         {'from': 'תשכח!', 'to': ['אל תשכח!', 'אל תשכח'], 'en': 'Forget! → Don’t forget!'},
         {'from': 'תגיד לו!', 'to': ['אל תגיד לו!', 'אל תגיד לו'], 'en': 'Tell him! → Don’t tell him!'},
       ]},
      {'kind': 'order', 'title': 'סדרו את הבקשה', 'en': 'Build the request',
       'instructions': 'Tap the words in order.',
       'items': [
         {'words': ['אפשר', 'לקבל', 'את', 'החשבון', 'בבקשה'], 'a': 'אפשר לקבל את החשבון בבקשה',
          'en': 'Could I have the bill, please?'},
         {'words': ['תן', 'לי', 'רגע', 'אחד'], 'a': 'תן לי רגע אחד', 'en': 'Give me one moment.'},
         {'words': ['אל', 'תשכחי', 'את', 'המפתחות'], 'a': 'אל תשכחי את המפתחות',
          'en': 'Don’t forget the keys.'},
       ]},
      {'kind': 'slang', 'he': 'רגע', 'literal': '“a moment”',
       'meaning': 'Hang on / wait / hold up.',
       'when': 'On its own it stops the conversation while you think, object or find something. '
               'Said sharply it is "hold on a second" in the sense of "wait, that is not right".',
       'examples': [{'he': 'רגע, מה אמרת?', 'en': 'Hang on, what did you say?'},
                    {'he': 'רגע אחד ואני בא.', 'en': 'One moment and I’m coming.'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-19', 'n': 19, 'level': 'beginner',
    'title': {'he': 'רוצה, יכול, צריך', 'en': 'Want, can, must'},
    'objective': 'Three words that each take an infinitive after them, and between them carry an '
                 'enormous amount of ordinary speech. This is the shortcut to long sentences.',
    'blocks': [
      {'kind': 'teach', 'title': 'Verb + infinitive, and only the first one moves',
       'body': 'רוצה, יכול, צריך and חייב all agree with the subject, and the verb after them '
               'stays in the infinitive: <b>אני רוצה ללכת</b>, <b>היא יכולה לבוא</b>, '
               '<b>אנחנו צריכים לדבר</b>. Note that צריך and יכול inflect like ADJECTIVES — '
               'צריך / צריכה / צריכים / צריכות — not like verbs.',
       'examples': [
         {'he': 'אני רוצה ללמוד עברית.', 'en': 'I want to learn Hebrew.'},
         {'he': 'את יכולה לעזור לי?', 'en': 'Can you help me?'},
         {'he': 'אנחנו צריכים לצאת עכשיו.', 'en': 'We need to leave now.'},
         {'he': 'הוא חייב לעבוד מחר.', 'en': 'He has to work tomorrow.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'יכול', 'en': 'can, able', 'pos': 'other'},
         {'he': 'חייב', 'en': 'must, obliged', 'pos': 'other'},
         {'he': 'לצאת', 'en': 'to go out, to leave', 'pos': 'verb'},
         {'he': 'להיכנס', 'en': 'to enter', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'לנסוע', 'en': 'to travel, to ride', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'לישון', 'en': 'to sleep', 'pos': 'verb'},
         {'he': 'לעזוב', 'en': 'to leave (something)', 'pos': 'verb'},
         {'he': 'לנוח', 'en': 'to rest', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Complete the sentence',
       'instructions': 'Type the modal in the form the subject needs — they inflect like adjectives.',
       'example': {'q': 'היא ___ לבוא מחר. (יכול)', 'a': 'יכולה'},
       'items': [
         {'q': 'אנחנו ___ לדבר איתך. (צריך)', 'a': ['צריכים', 'צריכות'], 'en': 'We need to talk to you.'},
         {'q': 'הן ___ לצאת מוקדם. (חייב)', 'a': ['חייבות'], 'en': 'They (f.) have to leave early.'},
         {'q': 'אתה ___ לעזור לי רגע? (יכול)', 'a': ['יכול'], 'en': 'Can you help me a second?'},
         {'q': 'אני ___ לנוח קצת. (רוצה)', 'a': ['רוצה'], 'en': 'I want to rest a bit.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'The modal agrees; the verb after it does not.',
       'items': [
         {'words': ['אני', 'לא', 'יכול', 'לבוא', 'היום'], 'a': 'אני לא יכול לבוא היום',
          'en': 'I can’t come today.'},
         {'words': ['הם', 'צריכים', 'לנסוע', 'לירושלים', 'מחר'],
          'a': 'הם צריכים לנסוע לירושלים מחר', 'en': 'They need to travel to Jerusalem tomorrow.'},
         {'words': ['את', 'רוצה', 'לשתות', 'משהו'], 'a': 'את רוצה לשתות משהו',
          'en': 'Do you want something to drink?'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Which is right for a woman speaking?',
          'options': ['אני צריכה ללכת', 'אני צריך ללכת', 'אני צריכים ללכת'],
          'a': 'אני צריכה ללכת',
          'why': 'צריך behaves like an adjective, so it agrees with the speaker — and the verb '
                 'after it stays ללכת whatever happens.'},
         {'q': 'אני יכול לבוא means —',
          'options': ['I can come', 'I am coming', 'I came'], 'a': 'I can come',
          'why': 'יכול + infinitive. Present tense on its own would be אני בא.'},
       ]},
      {'kind': 'slang', 'he': 'בא לי', 'literal': '“it comes to me”',
       'meaning': 'I feel like / I fancy.',
       'when': 'What Israelis say far more than אני רוצה for a passing urge. It takes a noun or an '
               'infinitive: בא לי קפה, בא לי לצאת. The negative לא בא לי is a complete and '
               'sufficient refusal.',
       'examples': [{'he': 'בא לי קפה, אתה בא?', 'en': 'I fancy a coffee, coming?'},
                    {'he': 'לא בא לי לצאת הערב.', 'en': 'I don’t feel like going out tonight.'}]},
    ],
  },
  {
    'id': 'he-20', 'n': 20, 'level': 'beginner',
    'title': {'he': 'המשפחה ושייכות', 'en': 'Family and belonging'},
    'objective': 'Who is whose. Hebrew has two ways to say "my" — the easy one everybody uses and '
                 'the tight one that shows up on family words and in writing.',
    'blocks': [
      {'kind': 'teach', 'title': 'של, and the endings that replace it',
       'body': 'The everyday possessive is <b>של</b> with a pronoun stuck on: הבית <b>שלי</b>, '
               'האח <b>שלך</b>, המשפחה <b>שלנו</b>. There is also an older way that welds the '
               'ending onto the noun itself — <b>אמא שלי</b> or <b>אִמִּי</b>, <b>בן שלו</b> or '
               '<b>בְּנוֹ</b> — and family words are exactly where you still hear it.',
       'examples': [
         {'he': 'זאת המשפחה שלי.', 'en': 'This is my family.'},
         {'he': 'האח שלי גר בחיפה.', 'en': 'My brother lives in Haifa.'},
         {'he': 'איך קוראים לאמא שלך?', 'en': 'What’s your mother’s name?'},
         {'he': 'הילדים שלהם כבר גדולים.', 'en': 'Their children are grown up already.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'משפחה', 'en': 'family', 'pos': 'noun'},
         {'he': 'אבא', 'en': 'dad, father', 'pos': 'noun'},
         {'he': 'אמא', 'en': 'mum, mother', 'pos': 'noun'},
         {'he': 'אח', 'en': 'brother', 'pos': 'noun'},
         {'he': 'אחות', 'en': 'sister', 'pos': 'noun'},
         {'he': 'בן', 'en': 'son', 'pos': 'noun'},
         {'he': 'בת', 'en': 'daughter', 'pos': 'noun'},
         {'he': 'סבא', 'en': 'grandfather', 'pos': 'noun'},
         {'he': 'סבתא', 'en': 'grandmother', 'pos': 'noun'},
         {'he': 'בעל', 'en': 'husband, owner', 'pos': 'noun'},
         {'he': 'אישה', 'en': 'woman, wife', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'של מי?', 'en': 'Whose is it?',
       'instructions': 'Type the right form of של.',
       'example': {'q': 'זה הספר ___. (אני)', 'a': 'שלי'},
       'items': [
         {'q': 'האחות ___ לומדת רפואה. (הוא)', 'a': ['שלו'], 'en': 'His sister studies medicine.'},
         {'q': 'איפה המפתחות ___? (אתה)', 'a': ['שלך'], 'en': 'Where are your keys?'},
         {'q': 'הבית ___ קטן אבל יפה. (אנחנו)', 'a': ['שלנו'], 'en': 'Our house is small but pretty.'},
         {'q': 'הילדים ___ באים בשבת. (הם)', 'a': ['שלהם'], 'en': 'Their children are coming on Saturday.'},
         {'q': 'סבתא ___ בת תשעים. (היא)', 'a': ['שלה'], 'en': 'Her grandmother is ninety.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'אבא שלי', 'en': 'my dad'},
         {'he': 'אמא שלה', 'en': 'her mum'},
         {'he': 'האח שלנו', 'en': 'our brother'},
         {'he': 'הבת שלהם', 'en': 'their daughter'},
         {'he': 'סבא וסבתא', 'en': 'grandma and grandpa'},
         {'he': 'המשפחה שלך', 'en': 'your family'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'אשתו means —',
          'options': ['his wife', 'my wife', 'the woman'], 'a': 'his wife',
          'why': 'אישה with the old ־וֹ ending welded on. You will meet it in writing and on '
                 'family words far more than anywhere else.'},
         {'q': 'Which is the everyday way to say “my brother”?',
          'options': ['האח שלי', 'אחי', 'both, and the first is more common in speech'],
          'a': 'both, and the first is more common in speech',
          'why': 'אחי is correct and alive — it is also, on its own, slang for "mate".'},
       ]},
      {'kind': 'slang', 'he': 'אחי', 'literal': '“my brother”',
       'meaning': 'Mate, bro.',
       'when': 'Address to a friend, a stranger, a taxi driver. The feminine אחותי works the same '
               'way. It is warm rather than familiar, and it is everywhere.',
       'examples': [{'he': 'אחי, מה קורה?', 'en': 'Mate, what’s up?'},
                    {'he': 'תודה אחי, אתה מציל.', 'en': 'Thanks mate, you’re a lifesaver.'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-21', 'n': 21, 'level': 'beginner',
    'title': {'he': 'במסעדה ובבית קפה', 'en': 'Eating out'},
    'objective': 'Order, ask what something is, and pay — the single most useful hour of Hebrew '
                 'for anyone who has actually landed.',
    'blocks': [
      {'kind': 'teach', 'title': 'What the waiter will say to you',
       'body': 'You will hear <b>מה תרצה?</b> or just <b>כן?</b>, and at the end <b>הכל בסדר?</b>. '
               'To order, אפשר plus the thing, or <b>אני אקח</b> — "I’ll take". To pay: '
               '<b>אפשר לשלם?</b> or <b>חשבון, בבקשה</b>. Splitting the bill is <b>בנפרד</b>; '
               'together is <b>ביחד</b>.',
       'examples': [
         {'he': 'אפשר תפריט, בבקשה?', 'en': 'Could I have a menu, please?'},
         {'he': 'אני אקח את הסלט.', 'en': 'I’ll take the salad.'},
         {'he': 'מה יש לכם צמחוני?', 'en': 'What vegetarian do you have?'},
         {'he': 'חשבון בבקשה, בנפרד.', 'en': 'The bill please, separately.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'תפריט', 'en': 'menu', 'pos': 'noun'},
         {'he': 'מנה', 'en': 'dish, portion', 'pos': 'noun'},
         {'he': 'חשבון', 'en': 'bill, account', 'pos': 'noun'},
         {'he': 'מלצר', 'en': 'waiter', 'pos': 'noun'},
         {'he': 'לחם', 'en': 'bread', 'pos': 'noun'},
         {'he': 'סלט', 'en': 'salad', 'pos': 'noun'},
         {'he': 'מים', 'en': 'water', 'pos': 'noun'},
         {'he': 'יין', 'en': 'wine', 'pos': 'noun'},
         {'he': 'טעים', 'en': 'tasty', 'pos': 'adj'},
         {'he': 'רעב', 'en': 'hungry', 'pos': 'adj'},
       ]},
      {'kind': 'choose', 'title': 'מה אומרים?', 'en': 'What do you say?',
       'instructions': 'Pick the line that fits the moment.',
       'items': [
         {'q': 'The waiter asks מה תרצו? You want the fish.',
          'options': ['אני אקח את הדג', 'אני לוקח דג אתמול', 'יש לי דג'], 'a': 'אני אקח את הדג',
          'en': '“I’ll take the fish.”'},
         {'q': 'You are done and want to pay.',
          'options': ['אפשר לשלם?', 'אפשר לאכול?', 'כמה אתה?'], 'a': 'אפשר לשלם?',
          'en': '“Can I pay?”'},
         {'q': 'You want to know if there is anything vegetarian.',
          'options': ['יש משהו צמחוני?', 'אני צמחוני מחר?', 'צמחוני יש לי?'],
          'a': 'יש משהו צמחוני?', 'en': '“Is there anything vegetarian?”'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Complete the exchange',
       'instructions': 'Type the missing word.',
       'example': {'q': 'אפשר ___, בבקשה? — Could I have a menu, please?', 'a': 'תפריט'},
       'items': [
         {'q': 'המנה הזאת ממש ___!', 'a': ['טעימה'], 'en': 'This dish is really tasty!'},
         {'q': 'אני ___, בוא נאכל משהו.', 'a': ['רעב', 'רעבה'], 'en': 'I’m hungry, let’s eat something.'},
         {'q': '___ בבקשה, אנחנו משלמים ביחד.', 'a': ['חשבון'], 'en': 'The bill please, we’re paying together.'},
         {'q': 'אפשר עוד ___, בבקשה?', 'a': ['מים'], 'en': 'Could we have some more water, please?'},
       ]},
      {'kind': 'order', 'title': 'סדרו את ההזמנה', 'en': 'Build the order',
       'instructions': 'Tap the words in order.',
       'items': [
         {'words': ['אני', 'אקח', 'את', 'הסלט', 'בבקשה'], 'a': 'אני אקח את הסלט בבקשה',
          'en': 'I’ll take the salad, please.'},
         {'words': ['מה', 'אתם', 'ממליצים', 'היום'], 'a': 'מה אתם ממליצים היום',
          'en': 'What do you recommend today?'},
       ]},
      {'kind': 'slang', 'he': 'בתיאבון', 'literal': '“with appetite”',
       'meaning': 'Enjoy your meal.',
       'when': 'Said by the waiter putting the plate down, and by anyone at the table before '
               'people start. Answer with תודה, or בתיאבון back.',
       'examples': [{'he': 'בתיאבון!', 'en': 'Enjoy!'},
                    {'he': 'תודה, גם לך.', 'en': 'Thanks, you too.'}]},
    ],
  },
  {
    'id': 'he-22', 'n': 22, 'level': 'intermediate',
    'title': {'he': 'איך מגיעים?', 'en': 'Getting around'},
    'objective': 'Ask the way, understand the answer, and survive an Israeli bus. Directions are '
                 'short words said fast, so they have to be automatic.',
    'blocks': [
      {'kind': 'teach', 'title': 'Right, left, straight',
       'body': '<b>ימינה</b> right, <b>שמאלה</b> left, <b>ישר</b> straight on. That ־ה ending means '
               '"towards" and you will meet it again in <b>הביתה</b> homewards, <b>ימינה</b>, '
               '<b>שמאלה</b>, <b>צפונה</b> northward. To ask: <b>איך מגיעים ל…?</b> — "how does one '
               'get to…", with no subject at all.',
       'examples': [
         {'he': 'איך מגיעים לתחנה המרכזית?', 'en': 'How do you get to the central station?'},
         {'he': 'תמשיך ישר ואז ימינה.', 'en': 'Keep straight on and then right.'},
         {'he': 'זה רחוק מפה?', 'en': 'Is it far from here?'},
         {'he': 'אני נוסע הביתה.', 'en': 'I’m travelling home.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אוטובוס', 'en': 'bus', 'pos': 'noun'},
         {'he': 'רכבת', 'en': 'train', 'pos': 'noun'},
         {'he': 'מונית', 'en': 'taxi', 'pos': 'noun'},
         {'he': 'כביש', 'en': 'road', 'pos': 'noun'},
         {'he': 'כרטיס', 'en': 'ticket', 'pos': 'noun'},
         {'he': 'ימינה', 'en': 'to the right', 'pos': 'other'},
         {'he': 'שמאלה', 'en': 'to the left', 'pos': 'other'},
         {'he': 'ישר', 'en': 'straight on', 'pos': 'other'},
         {'he': 'רחוק', 'en': 'far', 'pos': 'adj'},
         {'he': 'קרוב', 'en': 'near', 'pos': 'adj'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את ההוראות', 'en': 'Complete the directions',
       'instructions': 'Type the missing direction word.',
       'example': {'q': 'תמשיך ___ עד הרמזור. — Keep straight on to the lights.', 'a': 'ישר'},
       'items': [
         {'q': 'בסוף הרחוב תפנה ___.', 'a': ['ימינה'], 'en': 'At the end of the street turn right.'},
         {'q': 'התחנה ___ מאוד, שתי דקות ברגל.', 'a': ['קרובה'], 'en': 'The stop is very close, two minutes on foot.'},
         {'q': 'אחרי בית הקפה תפני ___.', 'a': ['שמאלה'], 'en': 'After the café turn left.'},
         {'q': 'צריך לקנות ___ לפני שעולים.', 'a': ['כרטיס'], 'en': 'You have to buy a ticket before boarding.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'תחנה מרכזית', 'en': 'central bus station'},
         {'he': 'איך מגיעים', 'en': 'how do you get to'},
         {'he': 'זה רחוק?', 'en': 'is it far?'},
         {'he': 'ברגל', 'en': 'on foot'},
         {'he': 'הביתה', 'en': 'homewards'},
         {'he': 'תפנה ימינה', 'en': 'turn right'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'What does the ־ה on ימינה, שמאלה and הביתה do?',
          'options': ['it means “towards”', 'it makes the word feminine', 'it makes it definite'],
          'a': 'it means “towards”',
          'why': 'An old directional ending that survives on a handful of very common words. '
                 'הביתה is "homewards", not "the house".'},
         {'q': 'איך מגיעים has no subject. Why?',
          'options': ['it is an impersonal “how does one get”', 'the subject was dropped by mistake',
                      'it is a command'],
          'a': 'it is an impersonal “how does one get”',
          'why': 'Hebrew uses a bare plural verb for “one does”: אומרים "they say / one says", '
                 'איך אומרים "how do you say".'},
       ]},
      {'kind': 'slang', 'he': 'תכלס', 'literal': 'from Yiddish תכלית, “purpose, the point”',
       'meaning': 'Basically / honestly / bottom line.',
       'when': 'Getting to the point, or conceding one. תכלס, אתה צודק — "honestly, you’re right". '
               'Extremely common and slightly blunt.',
       'examples': [{'he': 'תכלס, זה לא כזה רחוק.', 'en': 'Honestly, it’s not that far.'},
                    {'he': 'תכלס, מה עושים עכשיו?', 'en': 'So, bottom line — what do we do now?'}]},
    ],
  },
]

UNITS += [
  {
    'id': 'he-23', 'n': 23, 'level': 'intermediate',
    'title': {'he': 'בניין נפעל', 'en': 'The nifal binyan'},
    'objective': 'The passive-and-middle pattern, and the last of the five you meet constantly. '
                 'נכנס, נמצא, נגמר, נשאר — none of them feels passive, and all of them are nifal.',
    'blocks': [
      {'kind': 'teach', 'title': 'A נ in front, and it happened to you',
       'body': 'Nifal is paʿal’s passive — כתב he wrote, <b>נכתב</b> it was written — but most of '
               'the nifal verbs you will actually use are not passive at all: <b>נכנס</b> to go '
               'in, <b>נמצא</b> to be located, <b>נגמר</b> to run out, <b>נשאר</b> to stay. The '
               'present and past both start with נ; the infinitive starts <b>לְהִי־</b>: להיכנס.',
       'examples': [
         {'he': 'הוא נכנס בלי לדפוק.', 'en': 'He came in without knocking.'},
         {'he': 'איפה נמצא בית הקפה?', 'en': 'Where is the café?'},
         {'he': 'הכסף נגמר.', 'en': 'The money ran out.'},
         {'he': 'נשארתי בבית כל היום.', 'en': 'I stayed home all day.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להיכנס', 'en': 'to enter', 'pos': 'verb', 'prep': 'ל'},
         {'he': 'להישאר', 'en': 'to stay, to remain', 'pos': 'verb'},
         {'he': 'להיגמר', 'en': 'to end, to run out', 'pos': 'verb'},
         {'he': 'להימצא', 'en': 'to be located', 'pos': 'verb'},
         {'he': 'להיפגש', 'en': 'to meet up', 'pos': 'verb', 'prep': 'עם'},
         {'he': 'להיזהר', 'en': 'to be careful', 'pos': 'verb'},
         {'he': 'להירשם', 'en': 'to register', 'pos': 'verb', 'prep': 'ל'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'Present and past both open with נ; the infinitive opens with להי־.',
       'cols': ['שם פועל', 'הוא, הווה', 'הוא, עבר', 'הם, עתיד'],
       'rows': [
         [{'g': 'להיכנס'}, {'g': 'נכנס'}, {'g': 'נכנס'}, {'g': 'ייכנסו'}],
         [{'g': 'להישאר'}, {'a': ['נשאר']}, {'a': ['נשאר']}, {'a': ['יישארו']}],
         [{'g': 'להיגמר'}, {'a': ['נגמר']}, {'a': ['נגמר']}, {'a': ['ייגמרו']}],
         [{'g': 'להיפגש'}, {'a': ['נפגש']}, {'a': ['נפגש']}, {'a': ['ייפגשו']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל', 'en': 'Write the verb',
       'instructions': 'Read the time words and pick the tense yourself.',
       'example': {'q': 'אתמול הוא ___ מאוחר. [להיכנס]', 'a': 'נכנס'},
       'items': [
         {'q': 'החלב ___, צריך לקנות. [להיגמר]', 'a': ['נגמר'], 'en': 'The milk’s run out, we need to buy some.'},
         {'q': 'אנחנו ___ בבית קפה מחר. [להיפגש]', 'a': ['ניפגש'], 'en': 'We’ll meet at a café tomorrow.'},
         {'q': 'היא ___ בעבודה עד מאוחר אתמול. [להישאר]', 'a': ['נשארה'], 'en': 'She stayed at work late yesterday.'},
         {'q': 'תמיד צריך ___ בכביש הזה. [להיזהר]', 'a': ['להיזהר'], 'en': 'You always have to be careful on this road.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'הוא נכנס can mean “he enters” AND “he entered”. Why?',
          'options': ['nifal’s masculine-singular present and past look identical',
                      'because it is irregular', 'because נכנס is not really a verb'],
          'a': 'nifal’s masculine-singular present and past look identical',
          'why': 'Only in this one cell. The context, or the time word, tells you which — and in '
                 'the feminine they separate: נכנסת against נכנסה.'},
         {'q': 'הכסף נגמר is closest to —',
          'options': ['“the money ran out”', '“someone finished the money”', '“the money is over there”'],
          'a': '“the money ran out”',
          'why': 'Nifal is often what English does with an intransitive verb: it broke, it opened, '
                 'it ran out — nobody named as doing it.'},
       ]},
      {'kind': 'slang', 'he': 'נגמר לי', 'literal': '“it ran out to me”',
       'meaning': 'I’ve run out of it — or I’ve had enough.',
       'when': 'נגמר לי החלב is "I’m out of milk". On its own, נגמר לי הכוח or just נגמר לי means '
               'you are done, out of patience or energy.',
       'examples': [{'he': 'נגמר לי הקפה.', 'en': 'I’ve run out of coffee.'},
                    {'he': 'נגמר לי, אני הולך לישון.', 'en': 'I’m done — I’m going to bed.'}]},
    ],
  },
  {
    'id': 'he-24', 'n': 24, 'level': 'intermediate',
    'title': {'he': 'מילות קישור', 'en': 'Joining sentences up'},
    'objective': 'The words that turn a list of short sentences into speech: because, but, so, if, '
                 'in order to, even though. This is the unit that makes you sound less like a book.',
    'blocks': [
      {'kind': 'teach', 'title': 'ש is the workhorse',
       'body': 'A great deal of Hebrew subordination is just <b>ש־</b> glued to the front: '
               'אמרתי <b>ש</b>אני בא, "I said that I’m coming"; <b>כדי ש</b>… "so that"; '
               '<b>למרות ש</b>… "even though"; <b>בגלל ש</b>… "because". Note the pair: '
               '<b>בגלל</b> takes a NOUN, <b>כי</b> or בגלל ש takes a whole clause.',
       'examples': [
         {'he': 'לא באתי כי הייתי חולה.', 'en': 'I didn’t come because I was ill.'},
         {'he': 'לא באתי בגלל הגשם.', 'en': 'I didn’t come because of the rain.'},
         {'he': 'רציתי לבוא, אבל לא יכולתי.', 'en': 'I wanted to come, but I couldn’t.'},
         {'he': 'אם יהיה זמן, נעבור אצלכם.', 'en': 'If there’s time, we’ll drop by yours.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אבל', 'en': 'but', 'pos': 'other'},
         {'he': 'כי', 'en': 'because', 'pos': 'other'},
         {'he': 'אז', 'en': 'so, then', 'pos': 'other'},
         {'he': 'אם', 'en': 'if', 'pos': 'other'},
         {'he': 'כדי', 'en': 'in order to', 'pos': 'other'},
         {'he': 'למרות', 'en': 'despite', 'pos': 'other'},
         {'he': 'בגלל', 'en': 'because of', 'pos': 'other'},
         {'he': 'גם', 'en': 'also', 'pos': 'other'},
         {'he': 'רק', 'en': 'only', 'pos': 'other'},
       ]},
      {'kind': 'choose', 'title': 'כי או בגלל?', 'en': 'כי or בגלל?',
       'instructions': 'בגלל takes a noun. כי takes a whole clause with a verb in it.',
       'items': [
         {'q': 'נשארנו בבית ___ הגשם.', 'options': ['בגלל', 'כי', 'כדי'], 'a': 'בגלל',
          'en': 'הגשם is a noun → בגלל.'},
         {'q': 'נשארנו בבית ___ ירד גשם.', 'options': ['כי', 'בגלל', 'למרות'], 'a': 'כי',
          'en': 'ירד גשם is a clause → כי.'},
         {'q': 'למדתי הרבה ___ לעבור את המבחן.', 'options': ['כדי', 'כי', 'אבל'], 'a': 'כדי',
          'en': 'כדי + infinitive: “in order to”.'},
         {'q': 'יצאנו ___ שהיה קר.', 'options': ['למרות', 'בגלל', 'כדי'], 'a': 'למרות',
          'en': 'למרות ש — “even though”.'},
       ]},
      {'kind': 'fill', 'title': 'חברו את המשפטים', 'en': 'Join the sentences',
       'instructions': 'Type the connective that fits.',
       'example': {'q': 'רציתי לבוא ___ לא יכולתי. — I wanted to come but I couldn’t.', 'a': 'אבל'},
       'items': [
         {'q': '___ יהיה יפה מחר, נלך לים.', 'a': ['אם'], 'en': 'If it’s nice tomorrow, we’ll go to the sea.'},
         {'q': 'הוא לא אכל ___ הוא לא היה רעב.', 'a': ['כי'], 'en': 'He didn’t eat because he wasn’t hungry.'},
         {'q': 'קמתי מוקדם ___ להספיק לרכבת.', 'a': ['כדי'], 'en': 'I got up early in order to catch the train.'},
         {'q': 'היא באה, ו___ אחותה באה.', 'a': ['גם'], 'en': 'She came, and her sister came too.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Two clauses and the word that joins them.',
       'items': [
         {'words': ['לא', 'הלכתי', 'כי', 'הייתי', 'עייף'], 'a': 'לא הלכתי כי הייתי עייף',
          'en': 'I didn’t go because I was tired.'},
         {'words': ['אם', 'תרצה', 'נוכל', 'להיפגש', 'מחר'], 'a': 'אם תרצה נוכל להיפגש מחר',
          'en': 'If you want, we can meet tomorrow.'},
         {'words': ['היא', 'עבדה', 'למרות', 'שהיא', 'הייתה', 'חולה'],
          'a': 'היא עבדה למרות שהיא הייתה חולה', 'en': 'She worked even though she was ill.'},
       ]},
      {'kind': 'slang', 'he': 'בקטנה', 'literal': '“in a small one”',
       'meaning': 'No big deal / a little bit / take it easy.',
       'when': 'Downplaying something — an effort, a favour, a plan. עשינו את זה בקטנה is "we did '
               'it, no problem"; נצא בקטנה is "let’s go out, nothing major".',
       'examples': [{'he': 'בקטנה, אין בעיה.', 'en': 'No big deal, no problem.'},
                    {'he': 'נעשה משהו בקטנה בערב.', 'en': 'Let’s do something low-key this evening.'}]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
# UNITS 25-32 — the intermediate second half. Everything up to here is a learner saying things
# about themselves; from here the units are about following what someone ELSE says, which is
# where Gimel and Gimel+ put their weight and where Hebrew starts to feel like a language rather
# than a set of forms.
UNITS += [
  {
    'id': 'he-25', 'n': 25, 'level': 'intermediate',
    'title': {'he': 'הבניינים הסבילים', 'en': 'The passive binyanim'},
    'objective': 'פועל and הופעל — the two binyanim nobody speaks in and everybody reads. You '
                 'will not need to produce them for years; you need to RECOGNISE them tomorrow, '
                 'because a newspaper headline is half made of them.',
    'blocks': [
      {'kind': 'teach', 'title': 'Every active binyan has a shadow',
       'body': 'פיעל has a passive, פוּעל: <b>סיפר</b> he told → <b>סוּפַּר</b> it was told. '
               'הפעיל has one too, הוּפעל: <b>הודיע</b> he announced → <b>הוּדַע</b> it was made '
               'known. You can hear them coming: a <b>u</b> vowel where the active has an '
               '<b>i</b> or an <b>a</b>. Nobody says these in a café, and the paper cannot get '
               'through a paragraph without them, because a passive lets you report a thing '
               'without naming who did it.',
       'examples': [
         {'he': 'הכביש נסגר בגלל התאונה.', 'en': 'The road was closed because of the accident.'},
         {'he': 'סופר לי שהוא עזב.', 'en': 'I was told that he left.'},
         {'he': 'הבית הזה נבנה לפני מאה שנה.', 'en': 'This house was built a hundred years ago.'},
         {'he': 'ההחלטה התקבלה אתמול.', 'en': 'The decision was taken yesterday.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להודיע', 'en': 'to announce, to let know', 'pos': 'verb'},
         {'he': 'לפרסם', 'en': 'to publish', 'pos': 'verb'},
         {'he': 'לבנות', 'en': 'to build', 'pos': 'verb'},
         {'he': 'לסגור', 'en': 'to close', 'pos': 'verb'},
         {'he': 'החלטה', 'en': 'decision', 'pos': 'noun'},
         {'he': 'הודעה', 'en': 'message, announcement', 'pos': 'noun'},
         {'he': 'תאונה', 'en': 'accident', 'pos': 'noun'},
         {'he': 'כביש', 'en': 'road', 'pos': 'noun'},
       ]},
      {'kind': 'quiz', 'title': 'פעיל או סביל?', 'en': 'Active or passive?',
       'items': [
         {'q': 'הכביש נסגר. — who closed it?',
          'options': ['The sentence does not say', 'The road', 'Nobody, it closed itself'],
          'a': 'The sentence does not say',
          'why': 'That is the whole job of a passive: it lets the writer report the event and '
                 'leave the agent out. Reading the paper, keep asking who is missing.'},
         {'q': 'Which of these is passive?',
          'options': ['הספר נכתב בשנות השישים', 'הוא כתב את הספר', 'הספר על השולחן'],
          'a': 'הספר נכתב בשנות השישים',
          'why': 'נכתב is נפעל, the passive of כתב. The second names the writer; the third has '
                 'no verb at all.'},
         {'q': 'What tells you סופר here is not "a writer"?',
          'options': ['The ל after it', 'It is the first word', 'Nothing — it is ambiguous'],
          'a': 'The ל after it',
          'why': 'סוּפַּר לִי — "it was told TO ME". A noun does not take an indirect object. '
                 'Hebrew asks you to read one word ahead constantly.'},
       ]},
      {'kind': 'transform', 'title': 'מפעיל לסביל', 'en': 'Active to passive',
       'instructions': 'Rewrite so the thing done is the subject and the doer disappears.',
       'example': {'from': 'הם סגרו את הכביש.', 'to': 'הכביש נסגר.'},
       'items': [
         {'from': 'הם בנו את הבית.', 'to': ['הבית נבנה.', 'הבית נבנה'],
          'en': 'They built the house.'},
         {'from': 'הם פרסמו את ההודעה.', 'to': ['ההודעה פורסמה.', 'ההודעה פורסמה'],
          'en': 'They published the announcement.'},
         {'from': 'הם מכרו את הדירה.', 'to': ['הדירה נמכרה.', 'הדירה נמכרה'],
          'en': 'They sold the flat.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the passive form. The active verb is given in the English.',
       'example': {'q': 'הכביש ___ אתמול. — was closed', 'a': 'נסגר'},
       'items': [
         {'q': 'הבית הזה ___ לפני מאה שנה.', 'a': ['נבנה'], 'en': 'This house was built a hundred years ago.'},
         {'q': 'הדירה ___ בשבוע שעבר.', 'a': ['נמכרה'], 'en': 'The flat was sold last week.'},
         {'q': 'ה___ התקבלה אתמול בערב.', 'a': ['החלטה'], 'en': 'The decision was taken yesterday evening.'},
         {'q': 'ה___ פורסמה בעיתון.', 'a': ['הודעה'], 'en': 'The announcement was published in the paper.'},
         {'q': 'החנות ___ בגלל התאונה.', 'a': ['נסגרה'], 'en': 'The shop was closed because of the accident.'},
       ]},
      {'kind': 'slang', 'he': 'נסגר', 'literal': '“it was closed”',
       'meaning': 'It’s settled / it’s a deal.',
       'when': 'The passive doing everyday work. סָגַרְנוּ is "we agreed", and נִסְגַּר on its own '
               'ends a negotiation about where to meet.',
       'examples': [{'he': 'אז נסגר, בשמונה אצלי.', 'en': 'Settled then, eight o’clock at mine.'},
                    {'he': 'סגרנו על מחיר.', 'en': 'We agreed on a price.'}]},
    ],
  },
  {
    'id': 'he-26', 'n': 26, 'level': 'intermediate',
    'title': {'he': 'שם הפעולה', 'en': 'Turning a verb into a noun'},
    'objective': 'כתיבה, הליכה, נסיעה, החלטה. Every binyan makes its verbs into nouns by one '
                 'fixed shape, and knowing the shape doubles your vocabulary for free.',
    'blocks': [
      {'kind': 'teach', 'title': 'One shape per binyan',
       'body': 'פעל gives <b>קְטִילָה</b>: כתב → <b>כתיבה</b>, הלך → <b>הליכה</b>, נסע → '
               '<b>נסיעה</b>. פיעל gives <b>קִיטּוּל</b>: סיפר → <b>סיפור</b>, טייל → '
               '<b>טיול</b>. הפעיל gives <b>הַקְטָלָה</b>: החליט → <b>החלטה</b>, הרגיש → '
               '<b>הרגשה</b>. התפעל gives <b>הִתְקַטְּלוּת</b>: התרגש → <b>התרגשות</b>. Meet a '
               'verb and you have met its noun.',
       'examples': [
         {'he': 'הנסיעה לוקחת שעה.', 'en': 'The journey takes an hour.'},
         {'he': 'ההחלטה הייתה קשה.', 'en': 'The decision was hard.'},
         {'he': 'הכתיבה שלו מאוד ברורה.', 'en': 'His writing is very clear.'},
         {'he': 'אחרי הפגישה נדבר.', 'en': 'We’ll talk after the meeting.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'כתיבה', 'en': 'writing', 'pos': 'noun'},
         {'he': 'קריאה', 'en': 'reading, a call', 'pos': 'noun'},
         {'he': 'הליכה', 'en': 'walking', 'pos': 'noun'},
         {'he': 'נסיעה', 'en': 'a journey, a ride', 'pos': 'noun'},
         {'he': 'פגישה', 'en': 'a meeting', 'pos': 'noun'},
         {'he': 'החלטה', 'en': 'a decision', 'pos': 'noun'},
         {'he': 'הרגשה', 'en': 'a feeling', 'pos': 'noun'},
         {'he': 'שינה', 'en': 'sleep', 'pos': 'noun'},
       ]},
      {'kind': 'match', 'title': 'התאימו פועל לשם הפעולה', 'en': 'Match the verb to its noun',
       'instructions': 'Tap the infinitive, then the noun made from it.',
       'pairs': [
         {'he': 'לכתוב', 'en': 'כתיבה — writing'},
         {'he': 'לנסוע', 'en': 'נסיעה — a journey'},
         {'he': 'להחליט', 'en': 'החלטה — a decision'},
         {'he': 'להרגיש', 'en': 'הרגשה — a feeling'},
         {'he': 'לישון', 'en': 'שינה — sleep'},
         {'he': 'לקרוא', 'en': 'קריאה — reading'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את שם הפעולה', 'en': 'Fill in the verbal noun',
       'instructions': 'The verb is there in the English; type the Hebrew NOUN.',
       'example': {'q': 'ה___ שלו ברורה מאוד. — his writing', 'a': 'כתיבה'},
       'items': [
         {'q': 'ה___ לירושלים לוקחת שעה.', 'a': ['נסיעה'], 'en': 'The journey to Jerusalem takes an hour.'},
         {'q': 'זו הייתה ___ קשה מאוד.', 'a': ['החלטה'], 'en': 'That was a very hard decision.'},
         {'q': 'יש לי ___ טובה לגבי זה.', 'a': ['הרגשה'], 'en': 'I have a good feeling about it.'},
         {'q': 'ה___ בערב עושה לי טוב.', 'a': ['הליכה'], 'en': 'The evening walk does me good.'},
         {'q': 'אחרי ה___ נדבר על זה.', 'a': ['פגישה'], 'en': 'After the meeting we’ll talk about it.'},
       ]},
      {'kind': 'slang', 'he': 'עשה לי הרגשה', 'literal': '“made me a feeling”',
       'meaning': 'It made me feel …',
       'when': 'Hebrew builds a lot of emotion with עשה plus a verbal noun rather than with an '
               'adjective. עָשָׂה לִי טוֹב is "it did me good", and it is far more common than '
               'anything with a feeling-verb in it.',
       'examples': [{'he': 'זה עשה לי טוב.', 'en': 'That did me good.'},
                    {'he': 'הסרט עשה לי הרגשה מוזרה.', 'en': 'The film left me feeling strange.'}]},
    ],
  },
  {
    'id': 'he-27', 'n': 27, 'level': 'intermediate',
    'title': {'he': 'משפטי תנאי', 'en': 'If and would'},
    'objective': 'אם for what might happen, אילו and היה for what did not. The second one is how '
                 'Hebrew says "would", and there is no other way to say it.',
    'blocks': [
      {'kind': 'teach', 'title': 'Two ifs, and only one of them is real',
       'body': '<b>אם</b> + future is a real condition: אם יהיה זמן, נלך — "if there is time, '
               'we will go". <b>אילו</b> (or לו) + past is a condition that did NOT happen, and '
               'the other half of the sentence takes <b>היה</b> plus the present participle: '
               'אילו ידעתי, <b>הייתי אומר</b> לך — "if I had known, I would have told you". That '
               'הייתי + participle IS the Hebrew conditional; there is no separate word for '
               '"would".',
       'examples': [
         {'he': 'אם יהיה לי זמן, אבוא.', 'en': 'If I have time, I’ll come.'},
         {'he': 'אילו הייתי יודע, לא הייתי הולך.', 'en': 'If I’d known, I wouldn’t have gone.'},
         {'he': 'הייתי שמח לעזור.', 'en': 'I’d be glad to help.'},
         {'he': 'מה היית עושה במקומי?', 'en': 'What would you do in my place?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אם', 'en': 'if', 'pos': 'other'},
         {'he': 'אילו', 'en': 'if (contrary to fact)', 'pos': 'other'},
         {'he': 'תנאי', 'en': 'condition', 'pos': 'noun'},
         {'he': 'אולי', 'en': 'maybe', 'pos': 'other'},
         {'he': 'בטח', 'en': 'surely, of course', 'pos': 'other'},
         {'he': 'להבטיח', 'en': 'to promise', 'pos': 'verb'},
         {'he': 'לוותר', 'en': 'to give up (on) — לוותר על', 'pos': 'verb'},
         {'he': 'במקום', 'en': 'instead of, in place of', 'pos': 'other'},
       ]},
      {'kind': 'choose', 'title': 'אם או אילו?', 'en': 'אם or אילו?',
       'instructions': 'One of them is about something that can still happen.',
       'items': [
         {'q': '___ יהיה גשם, ניקח מטרייה.', 'options': ['אם', 'אילו', 'כאשר'], 'a': 'אם',
          'en': 'If it rains, we’ll take an umbrella. — it might still rain.'},
         {'q': '___ הייתי עשיר, הייתי נוסע לעולם.', 'options': ['אילו', 'אם', 'כי'], 'a': 'אילו',
          'en': 'If I were rich, I’d travel the world. — I am not rich.'},
         {'q': '___ ידעתי, לא הייתי שואל.', 'options': ['אילו', 'אם', 'למרות'], 'a': 'אילו',
          'en': 'Had I known, I wouldn’t have asked.'},
         {'q': '___ תרצה, אני יכול לעזור.', 'options': ['אם', 'אילו', 'אף על פי'], 'a': 'אם',
          'en': 'If you want, I can help.'},
       ]},
      {'kind': 'transform', 'title': 'מהעבר לתנאי', 'en': 'Past to conditional',
       'instructions': 'Rewrite with היה so it means "would have".',
       'example': {'from': 'עזרתי לו.', 'to': 'הייתי עוזר לו.'},
       'items': [
         {'from': 'באתי מוקדם.', 'to': ['הייתי בא מוקדם.', 'הייתי בא מוקדם'],
          'en': 'I came early. → I would have come early.'},
         {'from': 'היא אמרה לך.', 'to': ['היא הייתה אומרת לך.', 'היא הייתה אומרת לך'],
          'en': 'She told you. → She would have told you.'},
         {'from': 'הם קנו את הבית.', 'to': ['הם היו קונים את הבית.', 'הם היו קונים את הבית'],
          'en': 'They bought the house. → They would have bought the house.'},
       ]},
      {'kind': 'slang', 'he': 'הייתי שמח', 'literal': '“I would be glad”',
       'meaning': 'I’d like / I’d appreciate it.',
       'when': 'The polite way to ask for something without asking. הייתי שמח אם תוכל is softer '
               'than any imperative and is what you write in an email to someone you do not know.',
       'examples': [{'he': 'הייתי שמח אם תוכל לעזור.', 'en': 'I’d appreciate it if you could help.'},
                    {'he': 'הייתי שמחה לשמוע ממך.', 'en': 'I’d be glad to hear from you.'}]},
    ],
  },
  {
    'id': 'he-28', 'n': 28, 'level': 'intermediate',
    'title': {'he': 'משפטי זיקה', 'en': 'The clause that hangs on ש־'},
    'objective': 'One letter does all of English’s who, which, that and where. Once ש־ is easy, '
                 'your sentences stop being a list and start being a paragraph.',
    'blocks': [
      {'kind': 'teach', 'title': 'ש־ hangs one sentence off another',
       'body': 'האיש <b>ש</b>גר למטה — "the man who lives downstairs". הספר <b>ש</b>קראתי — "the '
               'book that I read". Hebrew keeps a pronoun where English drops one: הבית '
               '<b>ש</b>גרנו <b>בו</b>, literally "the house that we lived IN IT". Also learn '
               '<b>מי ש</b> "whoever" and <b>מה ש</b> "what / the thing that" — both start '
               'sentences constantly.',
       'examples': [
         {'he': 'זה החבר שסיפרתי לך עליו.', 'en': 'That’s the friend I told you about.'},
         {'he': 'מה שאמרת נכון.', 'en': 'What you said is right.'},
         {'he': 'מי שרוצה, שיבוא.', 'en': 'Whoever wants to, let them come.'},
         {'he': 'הדירה שגרנו בה הייתה קטנה.', 'en': 'The flat we lived in was small.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אשר', 'en': 'which, that (written register)', 'pos': 'other'},
         {'he': 'כפי', 'en': 'as, according to — כפי ש', 'pos': 'other'},
         {'he': 'לספר', 'en': 'to tell — לספר על', 'pos': 'verb'},
         {'he': 'להתייחס', 'en': 'to relate, to refer — להתייחס ל', 'pos': 'verb'},
         {'he': 'נכון', 'en': 'right, correct', 'pos': 'adj'},
         {'he': 'ברור', 'en': 'clear', 'pos': 'adj'},
         {'he': 'עיקר', 'en': 'the main thing', 'pos': 'noun'},
         {'he': 'פרט', 'en': 'a detail', 'pos': 'noun'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['זה', 'הספר', 'שקראתי', 'בשבוע', 'שעבר'], 'a': 'זה הספר שקראתי בשבוע שעבר',
          'en': 'That’s the book I read last week.'},
         {'words': ['מה', 'שאמרת', 'לא', 'היה', 'ברור'], 'a': 'מה שאמרת לא היה ברור',
          'en': 'What you said wasn’t clear.'},
         {'words': ['האיש', 'שגר', 'למטה', 'עובד', 'בלילה'], 'a': 'האיש שגר למטה עובד בלילה',
          'en': 'The man who lives downstairs works nights.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word — ש, מי ש, מה ש, or the pronoun the clause needs.',
       'example': {'q': 'הבית ___ גרנו בו נמכר. — the house that', 'a': 'ש'},
       'items': [
         {'q': '___ שרוצה לבוא, שיגיד לי.', 'a': ['מי'], 'en': 'Whoever wants to come should tell me.'},
         {'q': '___ שאמרת אתמול היה מוזר.', 'a': ['מה'], 'en': 'What you said yesterday was strange.'},
         {'q': 'זו הדירה שגרנו ___ שנתיים.', 'a': ['בה'], 'en': 'That’s the flat we lived in for two years.'},
         {'q': 'זה החבר שסיפרתי לך ___.', 'a': ['עליו'], 'en': 'That’s the friend I told you about.'},
         {'q': 'הכל ___ אמרת נכון.', 'a': ['מה'], 'en': 'Everything you said is right.'},
       ]},
      {'kind': 'slang', 'he': 'מה שבא', 'literal': '“what comes”',
       'meaning': 'Whatever / anything you like.',
       'when': 'A מה ש clause doing the work of a whole answer. Asked what you want to eat, מה '
               'שבא is "whatever", and מה שבא לך is "whatever you feel like".',
       'examples': [{'he': 'תזמין מה שבא לך.', 'en': 'Order whatever you like.'},
                    {'he': 'נעשה מה שבא, אין לחץ.', 'en': 'We’ll do whatever, no pressure.'}]},
    ],
  },
  {
    'id': 'he-29', 'n': 29, 'level': 'intermediate',
    'title': {'he': 'בגלל, למרות, בזכות', 'en': 'Because, despite, thanks to'},
    'objective': 'The compound prepositions that let you give a reason. Each one takes a noun or '
                 'takes ש־, never both, and getting that wrong is the most audible mistake a '
                 'learner makes at this level.',
    'blocks': [
      {'kind': 'teach', 'title': 'Noun or ש, never both',
       'body': '<b>בגלל</b> takes a NOUN — בגלל הגשם. To put a whole clause after it you need '
               '<b>בגלל ש</b> — בגלל שירד גשם. Same pair for <b>למרות</b> / למרות ש, and '
               '<b>בזכות</b> / בזכות ש. <b>כי</b> is the plain everyday "because" and takes a '
               'clause on its own. The written register uses <b>מכיוון ש</b> and <b>אף על פי '
               'ש</b> for the same two jobs.',
       'examples': [
         {'he': 'לא באנו בגלל הגשם.', 'en': 'We didn’t come because of the rain.'},
         {'he': 'לא באנו בגלל שירד גשם.', 'en': 'We didn’t come because it was raining.'},
         {'he': 'למרות הכל, הוא הצליח.', 'en': 'In spite of everything, he succeeded.'},
         {'he': 'בזכותך סיימתי בזמן.', 'en': 'Thanks to you I finished on time.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'בגלל', 'en': 'because of', 'pos': 'other'},
         {'he': 'למרות', 'en': 'despite', 'pos': 'other'},
         {'he': 'בזכות', 'en': 'thanks to', 'pos': 'other'},
         {'he': 'בעקבות', 'en': 'following, in the wake of', 'pos': 'other'},
         {'he': 'לפי', 'en': 'according to', 'pos': 'other'},
         {'he': 'לגרום', 'en': 'to cause — לגרום ל', 'pos': 'verb'},
         {'he': 'להשפיע', 'en': 'to influence — להשפיע על', 'pos': 'verb'},
         {'he': 'גורם', 'en': 'a cause, a factor', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את הצורה', 'en': 'Choose the right form',
       'instructions': 'Look at what comes after the gap: a noun, or a whole clause?',
       'items': [
         {'q': 'איחרנו ___ הפקק.', 'options': ['בגלל', 'בגלל ש', 'כי'], 'a': 'בגלל',
          'en': 'We were late because of the traffic. — הפקק is a noun.'},
         {'q': 'איחרנו ___ היה פקק.', 'options': ['בגלל ש', 'בגלל', 'למרות'], 'a': 'בגלל ש',
          'en': 'We were late because there was traffic. — a whole clause follows.'},
         {'q': '___ הקור, יצאנו לטייל.', 'options': ['למרות', 'למרות ש', 'בזכות'], 'a': 'למרות',
          'en': 'Despite the cold, we went out for a walk.'},
         {'q': '___ העזרה שלך סיימתי.', 'options': ['בזכות', 'בגלל ש', 'אף על פי'], 'a': 'בזכות',
          'en': 'Thanks to your help I finished. — בזכות is for good causes, בגלל is neutral.'},
       ]},
      {'kind': 'transform', 'title': 'משם פעולה למשפט', 'en': 'From a noun to a clause',
       'instructions': 'Rewrite with ש so a whole clause follows.',
       'example': {'from': 'לא באנו בגלל הגשם.', 'to': 'לא באנו בגלל שירד גשם.'},
       'items': [
         {'from': 'הוא איחר בגלל הפקק.', 'to': ['הוא איחר בגלל שהיה פקק.', 'הוא איחר בגלל שהיה פקק'],
          'en': 'He was late because of the traffic.'},
         {'from': 'יצאנו למרות הקור.', 'to': ['יצאנו למרות שהיה קר.', 'יצאנו למרות שהיה קר'],
          'en': 'We went out despite the cold.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['לא', 'יצאנו', 'בגלל', 'הגשם'], 'a': 'לא יצאנו בגלל הגשם',
          'en': 'We didn’t go out because of the rain.'},
         {'words': ['למרות', 'הכל', 'הוא', 'הצליח'], 'a': 'למרות הכל הוא הצליח',
          'en': 'In spite of everything he succeeded.'},
         {'words': ['בזכות', 'העזרה', 'שלך', 'סיימתי', 'בזמן'], 'a': 'בזכות העזרה שלך סיימתי בזמן',
          'en': 'Thanks to your help I finished on time.'},
         {'words': ['הוא', 'איחר', 'כי', 'היה', 'פקק', 'גדול'], 'a': 'הוא איחר כי היה פקק גדול',
          'en': 'He was late because there was a big traffic jam.'},
       ]},
      {'kind': 'slang', 'he': 'בגללך', 'literal': '“because of you”',
       'meaning': 'Your fault — or, said warmly, all thanks to you.',
       'when': 'בגלל takes pronoun endings like any preposition: בגללי, בגללך, בגללו. Note that '
               'בגללך leans towards blame and בזכותך towards credit, and Israelis hear the '
               'difference immediately.',
       'examples': [{'he': 'בגללך איחרנו לסרט.', 'en': 'Because of you we were late for the film.'},
                    {'he': 'בזכותך הצלחתי.', 'en': 'Thanks to you I managed it.'}]},
    ],
  },
  {
    'id': 'he-30', 'n': 30, 'level': 'intermediate',
    'title': {'he': 'בעבודה', 'en': 'At work'},
    'objective': 'The office day in Hebrew: meetings, deadlines, email, the boss. This is the '
                 'register most learners meet first in real life and last in a textbook.',
    'blocks': [
      {'kind': 'teach', 'title': 'Work Hebrew is short Hebrew',
       'body': 'A workplace runs on a small set of verbs used constantly: <b>לקבוע</b> a meeting, '
               '<b>להעביר</b> a document, <b>לעדכן</b> someone, <b>לטפל ב</b> something, '
               '<b>לסגור</b> a task. Note how many take a governed preposition — לטפל <b>ב</b>, '
               'לעדכן <b>את</b>, לדווח <b>ל</b> — which is the Gimel lesson again: the '
               'preposition is part of the verb.',
       'examples': [
         {'he': 'נקבע פגישה ליום שלישי.', 'en': 'Let’s set a meeting for Tuesday.'},
         {'he': 'אני מטפל בזה עכשיו.', 'en': 'I’m dealing with it now.'},
         {'he': 'תעדכן אותי כשתדע.', 'en': 'Update me when you know.'},
         {'he': 'העברתי לך את המסמך במייל.', 'en': 'I sent you the document by email.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'משרד', 'en': 'office', 'pos': 'noun'},
         {'he': 'מנהל', 'en': 'manager', 'pos': 'noun'},
         {'he': 'עובד', 'en': 'employee, worker', 'pos': 'noun'},
         {'he': 'ישיבה', 'en': 'a meeting (formal)', 'pos': 'noun'},
         {'he': 'משימה', 'en': 'a task', 'pos': 'noun'},
         {'he': 'משכורת', 'en': 'salary', 'pos': 'noun'},
         {'he': 'להתקשר', 'en': 'to phone — להתקשר ל', 'pos': 'verb'},
         {'he': 'להעביר', 'en': 'to pass on, to transfer', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'יש לנו ___ בשתיים. — a meeting', 'a': 'ישיבה'},
       'items': [
         {'q': 'ה___ שלי רוצה לדבר איתי.', 'a': ['מנהל'], 'en': 'My manager wants to talk to me.'},
         {'q': 'קיבלתי את ה___ בסוף החודש.', 'a': ['משכורת'], 'en': 'I got my salary at the end of the month.'},
         {'q': 'אני ___ אליך אחר כך.', 'a': ['מתקשר', 'מתקשרת'], 'en': 'I’ll call you later.'},
         {'q': 'תוכל ___ לי את המסמך?', 'a': ['להעביר'], 'en': 'Could you send me the document?'},
         {'q': 'יש לי הרבה ___ היום.', 'a': ['משימות', 'עבודה'], 'en': 'I have a lot of tasks today.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'לקבוע פגישה', 'en': 'to set up a meeting'},
         {'he': 'לטפל בבעיה', 'en': 'to deal with a problem'},
         {'he': 'לעדכן את הצוות', 'en': 'to update the team'},
         {'he': 'לשלוח מייל', 'en': 'to send an email'},
         {'he': 'לסיים בזמן', 'en': 'to finish on time'},
         {'he': 'לצאת מוקדם', 'en': 'to leave early'},
       ]},
      {'kind': 'slang', 'he': 'תכלס', 'literal': 'from תכלית, “purpose” (via Yiddish)',
       'meaning': 'Bottom line / actually / let’s get to the point.',
       'when': 'The single most useful word in an Israeli meeting. It marks the moment someone '
               'stops framing and says the real thing, and it is entirely at home at work.',
       'examples': [{'he': 'תכלס, זה לא יהיה מוכן היום.', 'en': 'Bottom line, it won’t be ready today.'},
                    {'he': 'תכלס אתה צודק.', 'en': 'Actually, you’re right.'}]},
    ],
  },
  {
    'id': 'he-31', 'n': 31, 'level': 'intermediate',
    'title': {'he': 'אצל הרופא', 'en': 'At the doctor’s'},
    'objective': 'Say where it hurts, understand what you are told to do, and read a '
                 'prescription. The one situation where guessing is not good enough.',
    'blocks': [
      {'kind': 'teach', 'title': 'Hebrew puts the pain in charge',
       'body': 'English says "I have a headache"; Hebrew says <b>כואב לי הראש</b> — "the head '
               'hurts TO ME". The body part is the subject and you are the indirect object, so '
               'the verb agrees with the body part: כואבת לי הבטן, כואבות לי הרגליים. Learn the '
               'frame and every ache is one noun away.',
       'examples': [
         {'he': 'כואב לי הראש.', 'en': 'I have a headache.'},
         {'he': 'כואבת לי הבטן כבר יומיים.', 'en': 'My stomach has hurt for two days.'},
         {'he': 'יש לי חום גבוה.', 'en': 'I have a high temperature.'},
         {'he': 'אני מרגיש לא טוב.', 'en': 'I don’t feel well.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'רופא', 'en': 'doctor', 'pos': 'noun'},
         {'he': 'מרפאה', 'en': 'clinic', 'pos': 'noun'},
         {'he': 'תור', 'en': 'appointment, queue', 'pos': 'noun'},
         {'he': 'בדיקה', 'en': 'a test, an examination', 'pos': 'noun'},
         {'he': 'תרופה', 'en': 'medicine', 'pos': 'noun'},
         {'he': 'מרשם', 'en': 'prescription', 'pos': 'noun'},
         {'he': 'כאב', 'en': 'pain', 'pos': 'noun'},
         {'he': 'להחלים', 'en': 'to recover', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Mind the agreement — the body part is the subject.',
       'example': {'q': '___ לי הראש. — my head hurts', 'a': 'כואב'},
       'items': [
         {'q': '___ לי הבטן.', 'a': ['כואבת'], 'en': 'My stomach hurts. — בטן is feminine.'},
         {'q': 'קבעתי ___ אצל הרופא ליום שני.', 'a': ['תור'], 'en': 'I made a doctor’s appointment for Monday.'},
         {'q': 'הרופא נתן לי ___ לתרופה.', 'a': ['מרשם'], 'en': 'The doctor gave me a prescription.'},
         {'q': 'צריך לעשות ___ דם.', 'a': ['בדיקת', 'בדיקה'], 'en': 'A blood test is needed.'},
         {'q': 'אני מקווה ש___ מהר.', 'a': ['תחלים', 'תחלימי'], 'en': 'I hope you get better soon.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Why is it כואבת לי הרגל and not כואב?',
          'options': ['רגל is feminine and it is the subject',
                      'Because לי is feminine',
                      'Because a leg is one of two'],
          'a': 'רגל is feminine and it is the subject',
          'why': 'The verb agrees with the body part, never with you. That is the whole trick of '
                 'this construction.'},
         {'q': 'A receptionist says יש לך תור בשלוש. What do you have?',
          'options': ['An appointment at three', 'A queue of three people', 'Three tests'],
          'a': 'An appointment at three',
          'why': 'תור is both "queue" and "your turn / appointment" — in a clinic it is always '
                 'the second.'},
       ]},
      {'kind': 'slang', 'he': 'רפואה שלמה', 'literal': '“a complete healing”',
       'meaning': 'Get well soon.',
       'when': 'What you say or write to someone who is ill. It comes from the prayer for the '
               'sick and is used by everyone, religious or not, exactly the way "bless you" is.',
       'examples': [{'he': 'רפואה שלמה, תשמור על עצמך.', 'en': 'Get well soon, look after yourself.'},
                    {'he': 'שמעתי שאתה חולה — רפואה שלמה.', 'en': 'I heard you’re ill — get well soon.'}]},
    ],
  },
  {
    'id': 'he-32', 'n': 32, 'level': 'intermediate',
    'title': {'he': 'כסף וטפסים', 'en': 'Money and paperwork'},
    'objective': 'The bank, the bill, the form and the queue. Bureaucratic Hebrew is a small '
                 'closed vocabulary, and knowing forty words of it removes most of the fear.',
    'blocks': [
      {'kind': 'teach', 'title': 'The words on the counter',
       'body': 'A form is a <b>טופס</b> and you <b>ממלא</b> it — fill it. Proof of anything is a '
               '<b>תעודה</b> or a <b>מסמך</b>. A receipt is a <b>קבלה</b>, which is also the noun from לקבל, "to '
               'receive". You pay <b>במזומן</b> (cash) or <b>באשראי</b> (card), and the thing '
               'you are paying is a <b>חשבון</b> — which means both "bill" and "bank account".',
       'examples': [
         {'he': 'צריך למלא טופס ולחתום.', 'en': 'You need to fill in a form and sign.'},
         {'he': 'אפשר לקבל קבלה, בבקשה?', 'en': 'Could I have a receipt, please?'},
         {'he': 'שילמתי במזומן.', 'en': 'I paid cash.'},
         {'he': 'פתחתי חשבון בבנק.', 'en': 'I opened an account at the bank.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'טופס', 'en': 'form', 'pos': 'noun'},
         {'he': 'תעודה', 'en': 'certificate, document', 'pos': 'noun'},
         {'he': 'קבלה', 'en': 'receipt', 'pos': 'noun'},
         {'he': 'חשבון', 'en': 'bill, account', 'pos': 'noun'},
         {'he': 'מזומן', 'en': 'cash', 'pos': 'noun'},
         {'he': 'ביטוח', 'en': 'insurance', 'pos': 'noun'},
         {'he': 'מס', 'en': 'tax', 'pos': 'noun'},
         {'he': 'לחסוך', 'en': 'to save (money)', 'pos': 'verb'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'למלא טופס', 'en': 'to fill in a form'},
         {'he': 'לשלם במזומן', 'en': 'to pay cash'},
         {'he': 'לפתוח חשבון', 'en': 'to open an account'},
         {'he': 'לחכות בתור', 'en': 'to wait in the queue'},
         {'he': 'לקבל תעודה', 'en': 'to get a certificate'},
         {'he': 'לחסוך כסף', 'en': 'to save money'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את המילה', 'en': 'Choose the word',
       'instructions': 'One word is the one an Israeli clerk would use.',
       'items': [
         {'q': 'איך אתה משלם? ב___ או באשראי?', 'options': ['מזומן', 'כסף', 'חשבון'],
          'a': 'מזומן', 'en': 'Cash or card?'},
         {'q': 'צריך ___ מהעבודה שאתה עובד שם.', 'options': ['תעודה', 'קבלה', 'מס'],
          'a': 'תעודה', 'en': 'You need a document from work saying you work there.'},
         {'q': 'קח את ה___, זה מוכיח ששילמת.', 'options': ['קבלה', 'מס', 'ביטוח'],
          'a': 'קבלה', 'en': 'Take the receipt, it proves you paid.'},
         {'q': 'יש לי ___ בריאות דרך העבודה.', 'options': ['ביטוח', 'מזומן', 'טופס'],
          'a': 'ביטוח', 'en': 'I have health insurance through work.'},
       ]},
      {'kind': 'slang', 'he': 'עלה לי ביוקר', 'literal': '“it went up to me expensively”',
       'meaning': 'It cost me dearly.',
       'when': 'Used for money and, more often, for anything else that had a price — a mistake, '
               'a decision, a night out. Hebrew uses עלה for costing, never שילם.',
       'examples': [{'he': 'התיקון עלה לי ביוקר.', 'en': 'The repair cost me a fortune.'},
                    {'he': 'כמה זה עולה?', 'en': 'How much does it cost?'}]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
# UNITS 33-40 — the advanced set, and they change what a unit is FOR. Up to here every unit
# taught a form. These teach a use: reading a headline, telling a story in order, disagreeing
# without being rude, hearing the difference between how Hebrew is spoken and how it is written.
# That is the ground the curriculum's phase 3 stands on, and nothing below it can reach it.
UNITS += [
  {
    'id': 'he-33', 'n': 33, 'level': 'advanced',
    'title': {'he': 'סתמי: מה אומרים', 'en': 'When nobody is the subject'},
    'objective': 'אומרים, כותבים, מדברים על. Hebrew has a whole way of saying things with no one '
                 'doing them, and half of what you overhear is built this way.',
    'blocks': [
      {'kind': 'teach', 'title': 'The third-person plural with nobody in it',
       'body': 'Put a verb in the masculine plural with no subject and it means "people do" or '
               '"one does": <b>אומרים ש</b>… "they say that", <b>מדברים על</b>… "there is talk '
               'of", <b>לא עושים את זה</b> "that isn’t done". It is not lazy speech — it is the '
               'standard Hebrew impersonal, and it is more common in the paper than a passive is. '
               'The other frame is <b>אי אפשר</b> / <b>אפשר</b>, which take an infinitive and no '
               'subject at all.',
       'examples': [
         {'he': 'אומרים שהמחירים יעלו.', 'en': 'They say prices will go up.'},
         {'he': 'מדברים על זה כבר חודשיים.', 'en': 'People have been talking about it for two months.'},
         {'he': 'פה לא מעשנים.', 'en': 'There’s no smoking here.'},
         {'he': 'אי אפשר להיכנס בלי תעודה.', 'en': 'You can’t get in without a document.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לדווח', 'en': 'to report — לדווח על', 'pos': 'verb'},
         {'he': 'לציין', 'en': 'to note, to mention', 'pos': 'verb'},
         {'he': 'להזכיר', 'en': 'to mention, to remind', 'pos': 'verb'},
         {'he': 'לשוחח', 'en': 'to converse — לשוחח עם', 'pos': 'verb'},
         {'he': 'עמדה', 'en': 'position, stance', 'pos': 'noun'},
         {'he': 'טענה', 'en': 'a claim', 'pos': 'noun'},
         {'he': 'אפשרות', 'en': 'possibility, option', 'pos': 'noun'},
         {'he': 'מסקנה', 'en': 'conclusion', 'pos': 'noun'},
       ]},
      {'kind': 'transform', 'title': 'מאישי לסתמי', 'en': 'Personal to impersonal',
       'instructions': 'Rewrite so nobody is named. Drop the subject and use the plural.',
       'example': {'from': 'האנשים אומרים שזה יקר.', 'to': 'אומרים שזה יקר.'},
       'items': [
         {'from': 'העיתון מדווח שהוא התפטר.', 'to': ['מדווחים שהוא התפטר.', 'מדווחים שהוא התפטר'],
          'en': 'The paper reports that he resigned.'},
         {'from': 'אנשים מדברים על זה הרבה.', 'to': ['מדברים על זה הרבה.', 'מדברים על זה הרבה'],
          'en': 'People talk about it a lot.'},
         {'from': 'הם לא מעשנים פה.', 'to': ['פה לא מעשנים.', 'לא מעשנים פה.', 'פה לא מעשנים', 'לא מעשנים פה'],
          'en': 'They don’t smoke here.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'אומרים שהוא עוזב. Who says?',
          'options': ['Unspecified — that is the point', 'The speaker', 'Everyone, literally'],
          'a': 'Unspecified — that is the point',
          'why': 'The impersonal reports a rumour without standing behind it, which is exactly '
                 'why it is everywhere in gossip and in news alike.'},
         {'q': 'What is the difference between נסגר and סוגרים?',
          'options': ['One is passive, the other impersonal',
                      'One is past, the other present',
                      'Nothing, they are interchangeable'],
          'a': 'One is passive, the other impersonal',
          'why': 'נסגר is a passive verb with the road as subject; סוגרים has no subject at all. '
                 'Both hide the agent, and Hebrew reaches for the second far more often in speech.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the impersonal verb — masculine plural, no subject.',
       'example': {'q': '___ שהמחירים יעלו. — they say', 'a': 'אומרים'},
       'items': [
         {'q': 'פה לא ___.', 'a': ['מעשנים'], 'en': 'There’s no smoking here.'},
         {'q': '___ על זה כבר חודשיים.', 'a': ['מדברים'], 'en': 'People have been talking about it for two months.'},
         {'q': '___ שהוא עוזב את התפקיד.', 'a': ['אומרים', 'מדווחים'], 'en': 'They say he’s leaving the job.'},
         {'q': 'אי ___ להיכנס בלי תעודה.', 'a': ['אפשר'], 'en': 'You can’t get in without a document.'},
         {'q': 'ככה לא ___ לאנשים.', 'a': ['מדברים'], 'en': 'That’s not how you talk to people.'},
       ]},
      {'kind': 'slang', 'he': 'לא עושים דבר כזה', 'literal': '“one does not do a thing like this”',
       'meaning': 'That’s just not done.',
       'when': 'The impersonal used to enforce a norm without accusing the person in front of '
               'you. Softer than אסור and much more common between friends and family.',
       'examples': [{'he': 'לא מדברים ככה לאמא.', 'en': 'You don’t talk to your mother like that.'},
                    {'he': 'לא באים בלי להתקשר.', 'en': 'One doesn’t just turn up without calling.'}]},
    ],
  },
  {
    'id': 'he-34', 'n': 34, 'level': 'advanced',
    'title': {'he': 'הפועל והמילית שלו, שלב ב', 'en': 'Verbs and their prepositions II'},
    'objective': 'Gimel’s core lesson, taken further: twenty verbs whose preposition changes the '
                 'meaning, or whose preposition is nothing like the English one.',
    'blocks': [
      {'kind': 'teach', 'title': 'The preposition is part of the word',
       'body': 'לְהַשְׁפִּיעַ <b>עַל</b> — to influence. לִסְבּוֹל <b>מ</b> — to suffer FROM. '
               'לְוַתֵּר <b>עַל</b> — to give up ON. לְהִתְרַגֵּל <b>ל</b> — to get used TO. '
               'לְהִתְלוֹנֵן <b>עַל</b> — to complain ABOUT. Learning the verb without it is '
               'learning half a word, and the half you learned will not build a sentence. Some '
               'verbs change meaning outright: חשב <b>על</b> is "think about", חשב <b>ש</b> is '
               '"think that".',
       'examples': [
         {'he': 'זה השפיע עליי מאוד.', 'en': 'That affected me a lot.'},
         {'he': 'הוא סובל מכאבי גב.', 'en': 'He suffers from back pain.'},
         {'he': 'ויתרתי על הנסיעה.', 'en': 'I gave up on the trip.'},
         {'he': 'התרגלתי לרעש.', 'en': 'I got used to the noise.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לסבול', 'en': 'to suffer — לסבול מ', 'pos': 'verb'},
         {'he': 'להתרגל', 'en': 'to get used to — להתרגל ל', 'pos': 'verb'},
         {'he': 'להתלונן', 'en': 'to complain — להתלונן על', 'pos': 'verb'},
         {'he': 'להתעקש', 'en': 'to insist — להתעקש על', 'pos': 'verb'},
         {'he': 'להאמין', 'en': 'to believe — להאמין ב', 'pos': 'verb'},
         {'he': 'לשמור', 'en': 'to keep, to guard — לשמור על', 'pos': 'verb'},
         {'he': 'לוותר', 'en': 'to give up — לוותר על', 'pos': 'verb'},
         {'he': 'להתייחס', 'en': 'to refer, to treat — להתייחס ל', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את המילית', 'en': 'Fill in the preposition',
       'instructions': 'One or two letters. This is the part nobody guesses right.',
       'example': {'q': 'הוא סובל ___ כאבי ראש.', 'a': 'מ'},
       'items': [
         {'q': 'זה השפיע ___ כל המשפחה.', 'a': ['על'], 'en': 'It affected the whole family.'},
         {'q': 'התרגלתי ___ החום.', 'a': ['ל'], 'en': 'I got used to the heat.'},
         {'q': 'הם התלוננו ___ הרעש.', 'a': ['על'], 'en': 'They complained about the noise.'},
         {'q': 'אני מאמין ___ זה.', 'a': ['ב'], 'en': 'I believe in that.'},
         {'q': 'תשמור ___ עצמך.', 'a': ['על'], 'en': 'Look after yourself.'},
         {'q': 'ויתרנו ___ החופשה.', 'a': ['על'], 'en': 'We gave up the holiday.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'לחשוב על', 'en': 'to think about'},
         {'he': 'לחשוב ש', 'en': 'to think that'},
         {'he': 'לדאוג ל', 'en': 'to see to, to provide for'},
         {'he': 'לדאוג מ', 'en': 'to worry about'},
         {'he': 'לשאול את', 'en': 'to ask someone'},
         {'he': 'לבקש מ', 'en': 'to ask something OF someone'},
       ]},
      {'kind': 'slang', 'he': 'סובל מזה', 'literal': '“suffers from it”',
       'meaning': 'Used well beyond illness — for anything you are stuck with.',
       'when': 'Hebrew uses סבל מ for traffic, bureaucracy and bad management as readily as for '
               'a headache, and the מ is fixed in all of them.',
       'examples': [{'he': 'כל השכונה סובלת מהרעש.', 'en': 'The whole neighbourhood suffers from the noise.'},
                    {'he': 'אני סובל מזה כל בוקר.', 'en': 'I put up with that every morning.'}]},
    ],
  },
  {
    'id': 'he-35', 'n': 35, 'level': 'advanced',
    'title': {'he': 'לקרוא עיתון', 'en': 'Reading the paper'},
    'objective': 'A headline is not a sentence. It drops the verb, front-loads the noun and '
                 'assumes you know the frame — and once you can read one, the daily news in this '
                 'app stops being an exercise.',
    'blocks': [
      {'kind': 'teach', 'title': 'The headline drops what you can guess',
       'body': 'Hebrew headlines leave out <b>היה</b> and the definite article, and often the '
               'verb altogether: <b>שר האוצר: “נעשה הכל”</b>, <b>מחאה בתל אביב</b>, '
               '<b>הוחלט: הבחירות ביוני</b>. A colon carries "said" or "it was decided". A whole '
               'clause can hang on a construct — <b>ראש הממשלה</b>, <b>שר הביטחון</b>, '
               '<b>בית המשפט העליון</b> — so the smichut you learned early is what a front page '
               'is made of.',
       'examples': [
         {'he': 'הממשלה החליטה על תקציב חדש.', 'en': 'The government decided on a new budget.'},
         {'he': 'הכנסת אישרה את החוק.', 'en': 'The Knesset approved the law.'},
         {'he': 'המחאה נמשכה עד הערב.', 'en': 'The protest continued until evening.'},
         {'he': 'לפי הדיווח, אין נפגעים.', 'en': 'According to the report, there are no casualties.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'כתבה', 'en': 'an article, a report', 'pos': 'noun'},
         {'he': 'כותרת', 'en': 'headline, title', 'pos': 'noun'},
         {'he': 'ממשלה', 'en': 'government', 'pos': 'noun'},
         {'he': 'כנסת', 'en': 'the Knesset', 'pos': 'noun'},
         {'he': 'בחירות', 'en': 'elections', 'pos': 'noun'},
         {'he': 'חוק', 'en': 'law', 'pos': 'noun'},
         {'he': 'מחאה', 'en': 'protest', 'pos': 'noun'},
         {'he': 'שופט', 'en': 'judge', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'מה הכותרת אומרת?', 'en': 'What does the headline say?',
       'instructions': 'Read the headline, then pick the sentence it stands for.',
       'items': [
         {'q': 'הכנסת אישרה: החוק עובר',
          'options': ['The Knesset approved it and the law passes',
                      'The Knesset will discuss the law',
                      'The law was rejected'],
          'a': 'The Knesset approved it and the law passes',
          'en': 'The colon carries the announcement.'},
         {'q': 'מחאה בתל אביב, אלפי משתתפים',
          'options': ['A protest in Tel Aviv with thousands taking part',
                      'Tel Aviv protests against thousands',
                      'Thousands protested and were arrested'],
          'a': 'A protest in Tel Aviv with thousands taking part',
          'en': 'No verb at all — two noun phrases side by side.'},
         {'q': 'לפי הדיווח: אין נפגעים',
          'options': ['According to the report, nobody was hurt',
                      'The report was not published',
                      'There is no report'],
          'a': 'According to the report, nobody was hurt',
          'en': 'אין plus a plural noun is the standard way to say "there are no".'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'ראש ה___ נאם אתמול. — government', 'a': 'ממשלה'},
       'items': [
         {'q': 'ה___ אישרה את החוק אתמול.', 'a': ['כנסת'], 'en': 'The Knesset approved the law yesterday.'},
         {'q': 'קראתי ___ מעניינת על זה בעיתון.', 'a': ['כתבה'], 'en': 'I read an interesting article about it in the paper.'},
         {'q': 'ה___ יהיו בחודש הבא.', 'a': ['בחירות'], 'en': 'The elections will be next month.'},
         {'q': 'ה___ החליט שהוא לא אשם.', 'a': ['שופט'], 'en': 'The judge decided he was not guilty.'},
         {'q': 'הייתה ___ גדולה ברחוב.', 'a': ['מחאה', 'הפגנה'], 'en': 'There was a big protest in the street.'},
       ]},
      {'kind': 'slang', 'he': 'על הפנים', 'literal': '“on the face”',
       'meaning': 'Terrible, a disaster.',
       'when': 'Said of anything that went badly — a film, a match, a government. It is informal '
               'and everywhere, and it is exactly what a reader says about the news they just read.',
       'examples': [{'he': 'המצב על הפנים.', 'en': 'The situation is a disaster.'},
                    {'he': 'הסרט היה על הפנים.', 'en': 'The film was terrible.'}]},
    ],
  },
  {
    'id': 'he-36', 'n': 36, 'level': 'advanced',
    'title': {'he': 'לספר סיפור', 'en': 'Telling a story'},
    'objective': 'Not new grammar — ORDER. The words that put events in sequence are what turn a '
                 'pile of past-tense sentences into something someone wants to listen to.',
    'blocks': [
      {'kind': 'teach', 'title': 'The spine of a story is four words long',
       'body': 'Open with <b>בהתחלה</b> or <b>יום אחד</b>. Move with <b>אחר כך</b>, '
               '<b>ואז</b>, <b>לאחר מכן</b> (written). Interrupt with <b>פתאום</b>. Close with '
               '<b>בסוף</b> or <b>לבסוף</b>. Hold two things at once with <b>בזמן ש</b> and '
               '<b>כש</b>. Israelis also narrate in the PRESENT for effect — אני הולך ברחוב, '
               'ופתאום — exactly as English does, and it is the most natural thing you can do '
               'with the tense you learned first.',
       'examples': [
         {'he': 'יום אחד הלכתי ברחוב, ופתאום ראיתי אותו.', 'en': 'One day I was walking down the street, and suddenly I saw him.'},
         {'he': 'בהתחלה זה היה קשה, אחר כך התרגלתי.', 'en': 'At first it was hard, then I got used to it.'},
         {'he': 'בזמן שחיכיתי, קראתי את כל העיתון.', 'en': 'While I waited, I read the whole paper.'},
         {'he': 'בסוף הכל הסתדר.', 'en': 'In the end everything worked out.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'בהתחלה', 'en': 'at first', 'pos': 'other'},
         {'he': 'פתאום', 'en': 'suddenly', 'pos': 'other'},
         {'he': 'עדיין', 'en': 'still', 'pos': 'other'},
         {'he': 'מיד', 'en': 'at once', 'pos': 'other'},
         {'he': 'כבר', 'en': 'already', 'pos': 'other'},
         {'he': 'להסתדר', 'en': 'to work out, to manage', 'pos': 'verb'},
         {'he': 'להמשיך', 'en': 'to continue', 'pos': 'verb'},
         {'he': 'להפסיק', 'en': 'to stop', 'pos': 'verb'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['בהתחלה', 'זה', 'היה', 'קשה', 'אבל', 'התרגלתי'],
          'a': 'בהתחלה זה היה קשה אבל התרגלתי', 'en': 'At first it was hard but I got used to it.'},
         {'words': ['בזמן', 'שחיכיתי', 'קראתי', 'את', 'העיתון'],
          'a': 'בזמן שחיכיתי קראתי את העיתון', 'en': 'While I waited I read the paper.'},
         {'words': ['ופתאום', 'הוא', 'קם', 'והלך', 'מהחדר'],
          'a': 'ופתאום הוא קם והלך מהחדר', 'en': 'And suddenly he got up and left the room.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו את מילת הקישור', 'en': 'Fill in the sequencing word',
       'instructions': 'Type the word that puts the events in order.',
       'example': {'q': '___ זה היה קשה. — at first', 'a': 'בהתחלה'},
       'items': [
         {'q': 'חיכיתי שעה, ו___ הוא הגיע.', 'a': ['פתאום', 'אז'], 'en': 'I waited an hour, and then/suddenly he arrived.'},
         {'q': '___ הכל הסתדר.', 'a': ['בסוף', 'לבסוף'], 'en': 'In the end everything worked out.'},
         {'q': 'אכלנו, ו___ הלכנו לים.', 'a': ['אחר כך', 'אז'], 'en': 'We ate, and afterwards we went to the sea.'},
         {'q': 'הוא ___ גר שם, לא עבר דירה.', 'a': ['עדיין'], 'en': 'He still lives there, he didn’t move.'},
         {'q': 'תתקשר אליי ___ כשתדע.', 'a': ['מיד'], 'en': 'Call me at once when you know.'},
       ]},
      {'kind': 'slang', 'he': 'ואז, בום', 'literal': '“and then, boom”',
       'meaning': 'And then it all happened at once.',
       'when': 'The spoken storyteller’s punctuation. Israelis mark the turn of a story out loud '
               'rather than with grammar, and ואז plus a sound effect is the commonest way.',
       'examples': [{'he': 'הכל היה בסדר, ואז בום, הכל נפל.', 'en': 'Everything was fine, and then boom, it all collapsed.'},
                    {'he': 'ואז הבנתי מה קרה.', 'en': 'And then I understood what had happened.'}]},
    ],
  },
  {
    'id': 'he-37', 'n': 37, 'level': 'advanced',
    'title': {'he': 'דעה וויכוח', 'en': 'Having an opinion'},
    'objective': 'Say what you think, disagree, and concede a point. Hebrew argues directly and '
                 'the softeners are different from English ones — knowing them is the difference '
                 'between blunt and rude.',
    'blocks': [
      {'kind': 'teach', 'title': 'Stake the claim, then hedge it',
       'body': 'Open with <b>לדעתי</b> "in my opinion", <b>נראה לי ש</b> "it seems to me", or '
               '<b>אני חושב ש</b>. Disagree with <b>אני לא בטוח</b>, <b>דווקא לא</b>, or the '
               'blunt <b>לא מסכים</b>. Concede with <b>נכון, אבל</b> or <b>בכל זאת</b>. Contrast '
               'two sides with <b>מצד אחד … מצד שני</b>. Note that Hebrew disagrees far more '
               'flatly than English and it is not read as rudeness.',
       'examples': [
         {'he': 'לדעתי זה לא יעבוד.', 'en': 'In my opinion that won’t work.'},
         {'he': 'נראה לי שאתה צודק.', 'en': 'I think you’re right.'},
         {'he': 'נכון, אבל זה לא כל הסיפור.', 'en': 'True, but that’s not the whole story.'},
         {'he': 'מצד אחד זה יקר, מצד שני אין ברירה.', 'en': 'On one hand it’s expensive, on the other there’s no choice.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'דעה', 'en': 'opinion', 'pos': 'noun'},
         {'he': 'להביע', 'en': 'to express — להביע דעה', 'pos': 'verb'},
         {'he': 'להסכים', 'en': 'to agree — להסכים עם', 'pos': 'verb'},
         {'he': 'להתנגד', 'en': 'to object — להתנגד ל', 'pos': 'verb'},
         {'he': 'לשכנע', 'en': 'to persuade', 'pos': 'verb'},
         {'he': 'להדגיש', 'en': 'to emphasise', 'pos': 'verb'},
         {'he': 'ברירה', 'en': 'choice, alternative', 'pos': 'noun'},
         {'he': 'לסכם', 'en': 'to sum up', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'איך עונים?', 'en': 'How do you reply?',
       'instructions': 'Someone says the line. Pick the reply that does what the English asks.',
       'items': [
         {'q': 'זה רעיון גרוע. — disagree, politely',
          'options': ['אני לא בטוח שזה נכון', 'אתה טועה לגמרי', 'בסדר גמור'],
          'a': 'אני לא בטוח שזה נכון', 'en': 'The first hedges; the second is a flat contradiction.'},
         {'q': 'אתה צודק. — concede but keep your point',
          'options': ['נכון, אבל בכל זאת', 'תודה רבה', 'לא מסכים'],
          'a': 'נכון, אבל בכל זאת', 'en': 'נכון, אבל is the standard concession before a counter.'},
         {'q': 'למה אתה חושב ככה? — give a reason',
          'options': ['כי ראיתי את זה בעצמי', 'לדעתי כן', 'אולי'],
          'a': 'כי ראיתי את זה בעצמי', 'en': 'A reason needs כי and a clause.'},
         {'q': 'מה דעתך? — say you are undecided',
          'options': ['אני עוד לא יודע', 'אני מסכים', 'ברור שלא'],
          'a': 'אני עוד לא יודע', 'en': '“I don’t know yet” — עוד לא is “not yet”.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['לדעתי', 'זה', 'לא', 'יעבוד', 'בכלל'], 'a': 'לדעתי זה לא יעבוד בכלל',
          'en': 'In my opinion that won’t work at all.'},
         {'words': ['מצד', 'אחד', 'זה', 'יקר', 'מצד', 'שני', 'אין', 'ברירה'],
          'a': 'מצד אחד זה יקר מצד שני אין ברירה',
          'en': 'On one hand it’s expensive, on the other there’s no choice.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the word that carries the opinion.',
       'example': {'q': '___ זה לא יעבוד. — in my opinion', 'a': 'לדעתי'},
       'items': [
         {'q': '___ לי שאתה צודק.', 'a': ['נראה'], 'en': 'It seems to me you’re right.'},
         {'q': 'אני לא ___ עם זה בכלל.', 'a': ['מסכים', 'מסכימה'], 'en': 'I don’t agree with that at all.'},
         {'q': 'מצד ___ זה יקר, מצד שני אין ברירה.', 'a': ['אחד'], 'en': 'On one hand it’s expensive, on the other there’s no choice.'},
         {'q': 'נכון, ___ זה לא כל הסיפור.', 'a': ['אבל'], 'en': 'True, but that’s not the whole story.'},
         {'q': 'הוא ניסה ___ אותי ולא הצליח.', 'a': ['לשכנע'], 'en': 'He tried to persuade me and didn’t manage.'},
       ]},
      {'kind': 'slang', 'he': 'אין ברירה', 'literal': '“there is no choice”',
       'meaning': 'Nothing to be done / we have no option.',
       'when': 'A national reflex, said with a shrug about anything from a queue to a war. It '
               'ends more Israeli arguments than any counter-argument does.',
       'examples': [{'he': 'אין ברירה, נחכה.', 'en': 'Nothing for it, we’ll wait.'},
                    {'he': 'לא רציתי, אבל לא הייתה ברירה.', 'en': 'I didn’t want to, but there was no choice.'}]},
    ],
  },
  {
    'id': 'he-38', 'n': 38, 'level': 'advanced',
    'title': {'he': 'דיבור מול כתיבה', 'en': 'Spoken Hebrew and written Hebrew'},
    'objective': 'They are further apart than in English. The same thought is said one way and '
                 'written another, and knowing which is which stops you sounding like a document.',
    'blocks': [
      {'kind': 'teach', 'title': 'Two registers, one language',
       'body': 'Spoken uses <b>ש</b>, written uses <b>אשר</b>. Spoken says <b>בגלל ש</b>, written '
               '<b>מכיוון ש</b>. Spoken says <b>אבל</b>, written <b>אולם</b>. Spoken drops '
               '<b>את</b> after some verbs and written never does. Written Hebrew keeps the '
               'future for the future; spoken Hebrew often uses the present. None of the written '
               'forms are wrong out loud — they just sound like you are reading aloud, which is '
               'a specific and slightly funny effect.',
       'examples': [
         {'he': 'האיש שגר למטה — האיש אשר גר למטה', 'en': 'the man who lives downstairs — spoken, then written'},
         {'he': 'בגלל שירד גשם — מכיוון שירד גשם', 'en': 'because it rained — spoken, then written'},
         {'he': 'אני הולך מחר. — אלך מחר.', 'en': 'I’m going tomorrow. — I shall go tomorrow.'},
         {'he': 'זה יקר אבל שווה. — הדבר יקר אולם שווה.', 'en': 'It’s expensive but worth it. — spoken, then written.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ניב', 'en': 'idiom, turn of phrase', 'pos': 'noun'},
         {'he': 'משפט', 'en': 'sentence; also a trial', 'pos': 'noun'},
         {'he': 'לשון', 'en': 'language, tongue', 'pos': 'noun'},
         {'he': 'להעיר', 'en': 'to remark; to wake someone', 'pos': 'verb'},
         {'he': 'להשיב', 'en': 'to reply (written register)', 'pos': 'verb'},
         {'he': 'להוסיף', 'en': 'to add', 'pos': 'verb'},
         {'he': 'רשמי', 'en': 'official, formal', 'pos': 'adj'},
         {'he': 'פשוט', 'en': 'simple; simply', 'pos': 'adj'},
       ]},
      {'kind': 'transform', 'title': 'מכתיבה לדיבור', 'en': 'Written to spoken',
       'instructions': 'Rewrite the way you would actually say it.',
       'example': {'from': 'האיש אשר גר למטה.', 'to': 'האיש שגר למטה.'},
       'items': [
         {'from': 'לא הגענו מכיוון שירד גשם.',
          'to': ['לא הגענו בגלל שירד גשם.', 'לא הגענו בגלל שירד גשם'],
          'en': 'We didn’t come because it rained.'},
         {'from': 'הדבר יקר אולם שווה.', 'to': ['זה יקר אבל שווה.', 'זה יקר אבל שווה'],
          'en': 'It’s expensive but worth it.'},
       ]},
      {'kind': 'quiz', 'title': 'איפה תשמע את זה?', 'en': 'Where would you hear this?',
       'items': [
         {'q': 'אשר, אולם, מכיוון ש — where do these live?',
          'options': ['In writing and in the news', 'In the street', 'Only in the Bible'],
          'a': 'In writing and in the news',
          'why': 'They are current, formal Hebrew — a newsreader says them, a friend does not.'},
         {'q': 'Someone says אלך מחר instead of אני הולך מחר. How does it land?',
          'options': ['Correct but bookish', 'Wrong', 'Rude'],
          'a': 'Correct but bookish',
          'why': 'The future tense is perfectly right; spoken Hebrew just reaches for the '
                 'present far more often, so the future sounds deliberate.'},
       ]},
      {'kind': 'choose', 'title': 'דיבור או כתיבה?', 'en': 'Spoken or written?',
       'instructions': 'Pick the version you would actually say out loud to a friend.',
       'items': [
         {'q': 'the man who was here', 'options': ['האיש שהיה פה', 'האיש אשר היה פה', 'האיש הוא היה פה'],
          'a': 'האיש שהיה פה', 'en': 'ש in speech, אשר on paper.'},
         {'q': 'but it’s worth it', 'options': ['אבל זה שווה', 'אולם הדבר שווה', 'ברם זה שווה'],
          'a': 'אבל זה שווה', 'en': 'אולם and ברם are written-register “but”.'},
         {'q': 'I’ll come tomorrow', 'options': ['אני בא מחר', 'אבוא מחר', 'הנני בא מחר'],
          'a': 'אני בא מחר', 'en': 'Spoken Hebrew uses the present for a near future far more than the future tense.'},
         {'q': 'because there was no time', 'options': ['כי לא היה זמן', 'מכיוון שלא היה זמן', 'הואיל ולא היה זמן'],
          'a': 'כי לא היה זמן', 'en': 'כי is the everyday one; the other two belong in a letter.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['בקיצור', 'לא', 'הגענו', 'בסוף'], 'a': 'בקיצור לא הגענו בסוף',
          'en': 'Anyway, in the end we didn’t make it.'},
         {'words': ['זה', 'יקר', 'אבל', 'שווה', 'את', 'זה'], 'a': 'זה יקר אבל שווה את זה',
          'en': 'It’s expensive but worth it.'},
         {'words': ['האיש', 'שדיברתי', 'איתו', 'עובד', 'שם'], 'a': 'האיש שדיברתי איתו עובד שם',
          'en': 'The man I spoke to works there.'},
       ]},
      {'kind': 'slang', 'he': 'בסך הכל', 'literal': '“in the sum of everything”',
       'meaning': 'All in all — or, said flatly, “it’s only …”.',
       'when': 'A written-looking phrase that lives entirely in speech, which is this unit\'s '
               'whole point. בסך הכל היה בסדר is "all in all it was fine"; בסך הכל ילד is '
               '"he\'s only a child".',
       'examples': [{'he': 'בסך הכל היה בסדר.', 'en': 'All in all it was fine.'},
                    {'he': 'הוא בסך הכל ילד.', 'en': 'He’s only a child.'}]},
    ],
  },
  {
    'id': 'he-39', 'n': 39, 'level': 'advanced',
    'title': {'he': 'ביטויים', 'en': 'Set phrases and idioms'},
    'objective': 'The phrases that cannot be worked out from their words. Many come straight out '
                 'of the Bible and the prayer book and are used by people who have never opened '
                 'either — which is a fact about Hebrew you will meet everywhere.',
    'blocks': [
      {'kind': 'teach', 'title': 'Old words doing everyday work',
       'body': '<b>בסדר גמור</b> "absolutely fine". <b>חבל על הזמן</b> literally "a pity about '
               'the time" and means AMAZING — or occasionally the opposite, and only the tone '
               'tells you. <b>יש דברים בגו</b> "there’s something in it" is Aramaic. '
               '<b>עין בעין</b>, <b>בלב שלם</b>, <b>מפה לאוזן</b> — all biblical, all current, '
               'all said by people who would not call themselves religious at all.',
       'examples': [
         {'he': 'חבל על הזמן כמה שזה טעים.', 'en': 'It’s unbelievably good.'},
         {'he': 'אנחנו לא רואים עין בעין.', 'en': 'We don’t see eye to eye.'},
         {'he': 'עשיתי את זה בלב שלם.', 'en': 'I did it wholeheartedly.'},
         {'he': 'זה עובר מפה לאוזן.', 'en': 'It spreads by word of mouth.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ניב', 'en': 'idiom, turn of phrase', 'pos': 'noun'},
         {'he': 'פתגם', 'en': 'proverb', 'pos': 'noun'},
         {'he': 'משל', 'en': 'a parable, a fable', 'pos': 'noun'},
         {'he': 'לב', 'en': 'heart', 'pos': 'noun'},
         {'he': 'עין', 'en': 'eye', 'pos': 'noun'},
         {'he': 'אוזן', 'en': 'ear', 'pos': 'noun'},
         {'he': 'שלם', 'en': 'whole, complete', 'pos': 'adj'},
         {'he': 'גמור', 'en': 'complete, utter', 'pos': 'adj'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then what it actually means.',
       'pairs': [
         {'he': 'חבל על הזמן', 'en': 'amazing (or: hopeless — tone decides)'},
         {'he': 'עין בעין', 'en': 'eye to eye, in agreement'},
         {'he': 'בלב שלם', 'en': 'wholeheartedly'},
         {'he': 'מפה לאוזן', 'en': 'by word of mouth'},
         {'he': 'בסדר גמור', 'en': 'absolutely fine'},
         {'he': 'אין על זה', 'en': 'nothing beats it'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'A friend tries your food and says חבל על הזמן. Should you be pleased?',
          'options': ['Yes — almost always', 'No, it is an insult', 'It means they are in a hurry'],
          'a': 'Yes — almost always',
          'why': 'It is an intensifier, and in the overwhelming majority of uses it is positive. '
                 'The sarcastic reading exists but is marked heavily by tone.'},
         {'q': 'Why do so many everyday idioms come from religious texts?',
          'options': ['Modern Hebrew was rebuilt out of them',
                      'Israelis are unusually religious',
                      'They were invented in the 1990s'],
          'a': 'Modern Hebrew was rebuilt out of them',
          'why': 'The language was revived from a written corpus that was overwhelmingly '
                 'liturgical, so its idioms carry that history whether or not the speaker does.'},
       ]},
      {'kind': 'slang', 'he': 'אין על זה', 'literal': '“there is nothing on it”',
       'meaning': 'Nothing beats it.',
       'when': 'The highest praise available in casual Hebrew, for food, a place, a person. '
               'אין עליך said to a person means "you are the best".',
       'examples': [{'he': 'החומוס הזה — אין על זה.', 'en': 'This hummus — nothing beats it.'},
                    {'he': 'אין עליך, תודה!', 'en': 'You’re the best, thanks!'}]},
    ],
  },
  {
    'id': 'he-40', 'n': 40, 'level': 'advanced',
    'title': {'he': 'ראיון ושיחת טלפון', 'en': 'Interviews and phone calls'},
    'objective': 'Two situations with no body language to help you: a job interview and a phone '
                 'call. Both run on set phrases, and both are where a learner’s Hebrew first '
                 'gets tested for real.',
    'blocks': [
      {'kind': 'teach', 'title': 'The phone has its own opening',
       'body': 'Israelis answer with <b>הלו</b> or just <b>כן</b>. You identify yourself with '
               '<b>מדבר</b> / <b>מדברת</b> — "David speaking" is <b>דוד מדבר</b>. Ask for '
               'someone with <b>אפשר לדבר עם</b>. If they are out: <b>אפשר להשאיר הודעה?</b> '
               'End with <b>תודה, ביי</b> — and Israelis hang up faster than you expect, which '
               'is not rudeness.',
       'examples': [
         {'he': 'הלו, אפשר לדבר עם דנה?', 'en': 'Hello, could I speak to Dana?'},
         {'he': 'רגע, אני מעביר אותך.', 'en': 'One moment, I’ll put you through.'},
         {'he': 'היא לא נמצאת, אפשר להשאיר הודעה?', 'en': 'She’s not in, can I leave a message?'},
         {'he': 'אני אחזור אליך אחר כך.', 'en': 'I’ll get back to you later.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ראיון', 'en': 'interview', 'pos': 'noun'},
         {'he': 'תפקיד', 'en': 'role, position', 'pos': 'noun'},
         {'he': 'ניסיון', 'en': 'experience; an attempt', 'pos': 'noun'},
         {'he': 'מועמד', 'en': 'candidate', 'pos': 'noun'},
         {'he': 'שיחה', 'en': 'call, conversation', 'pos': 'noun'},
         {'he': 'להשאיר', 'en': 'to leave (something)', 'pos': 'verb'},
         {'he': 'להתקבל', 'en': 'to be accepted, to get in', 'pos': 'verb'},
         {'he': 'להתפטר', 'en': 'to resign', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'הלו, ___ לדבר עם דנה? — could I', 'a': 'אפשר'},
       'items': [
         {'q': 'שלום, דוד ___.', 'a': ['מדבר'], 'en': 'Hello, David speaking.'},
         {'q': 'אפשר ___ הודעה?', 'a': ['להשאיר'], 'en': 'Can I leave a message?'},
         {'q': 'יש לי חמש שנות ___ בתחום.', 'a': ['ניסיון'], 'en': 'I have five years’ experience in the field.'},
         {'q': 'הגעתי ל___ בשעה עשר.', 'a': ['ראיון'], 'en': 'I got to the interview at ten.'},
         {'q': 'אני ___ אליך מחר.', 'a': ['אחזור', 'מתקשר'], 'en': 'I’ll get back to you tomorrow.'},
       ]},
      {'kind': 'choose', 'title': 'מה עונים בראיון?', 'en': 'What do you say in an interview?',
       'instructions': 'Pick the answer that sounds like a Hebrew speaker in a Hebrew interview.',
       'items': [
         {'q': 'ספר לי קצת על עצמך.',
          'options': ['עבדתי חמש שנים בתחום הזה', 'אני בסדר, תודה', 'לא יודע'],
          'a': 'עבדתי חמש שנים בתחום הזה', 'en': '“Tell me a bit about yourself.”'},
         {'q': 'למה עזבת את העבודה הקודמת?',
          'options': ['חיפשתי משהו חדש', 'המנהל היה נורא', 'בגלל הכסף'],
          'a': 'חיפשתי משהו חדש',
          'en': '“Why did you leave your last job?” — the neutral answer is the safe one here too.'},
         {'q': 'יש לך שאלות?',
          'options': ['כן, על התפקיד עצמו', 'לא, הכל בסדר', 'כמה זה משלם?'],
          'a': 'כן, על התפקיד עצמו', 'en': '“Do you have questions?”'},
       ]},
      {'kind': 'slang', 'he': 'נדבר', 'literal': '“we will talk”',
       'meaning': 'We’ll speak / let’s leave it there.',
       'when': 'How an Israeli ends a phone call, and it commits to nothing. Paired with יאללה '
               '— יאללה, נדבר — it is the standard sign-off between people who know each other.',
       'examples': [{'he': 'יאללה, נדבר.', 'en': 'Alright, we’ll speak.'},
                    {'he': 'תודה, נדבר מחר.', 'en': 'Thanks, we’ll talk tomorrow.'}]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
# UNITS 41-52. Four of these close gaps that should never have been open this long -- negation,
# comparison, time and frequency, and the habitual past -- and they are the kind of gap a
# syllabus built topic-first leaves behind: nobody writes a unit called "not", so nobody ever
# teaches אף, שום and בלי, and the learner works them out wrong for a year. The other eight are
# the situations an Israeli week is actually made of.
UNITS += [
  {
    'id': 'he-41', 'n': 41, 'level': 'intermediate',
    'title': {'he': 'שלילה', 'en': 'Saying no'},
    'objective': 'לא, אין, אף, שום, בלי, אל — six ways to negate, each with its own job, and '
                 'Hebrew doubles them where English refuses to.',
    'blocks': [
      {'kind': 'teach', 'title': 'Six words, six jobs',
       'body': '<b>לא</b> negates a verb or an adjective. <b>אין</b> negates existence and '
               'possession — אין לי, אין פה. <b>אף</b> + noun is "not a single": אף אחד '
               '"nobody", אף פעם "never". <b>שום</b> is the same idea with things: שום דבר '
               '"nothing". <b>בלי</b> is "without". <b>אל</b> is the negative IMPERATIVE — אל '
               'תלך, never לא תלך. And Hebrew keeps the לא: אף אחד <b>לא</b> בא, literally '
               '"nobody didn’t come", which is correct and required.',
       'examples': [
         {'he': 'אף אחד לא בא.', 'en': 'Nobody came.'},
         {'he': 'לא אמרתי שום דבר.', 'en': 'I didn’t say anything.'},
         {'he': 'אל תדאג, הכל בסדר.', 'en': 'Don’t worry, everything’s fine.'},
         {'he': 'יצאתי בלי מעיל ואני קופא.', 'en': 'I went out without a coat and I’m freezing.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אף', 'en': 'not a single; also: nose', 'pos': 'other'},
         {'he': 'שום', 'en': 'any (in negatives); also: garlic', 'pos': 'other'},
         {'he': 'בלי', 'en': 'without', 'pos': 'other'},
         {'he': 'אל', 'en': 'don’t (with an imperative)', 'pos': 'other'},
         {'he': 'כלום', 'en': 'nothing', 'pos': 'other'},
         {'he': 'מעולם', 'en': 'never (of the past, written)', 'pos': 'other'},
         {'he': 'עדיין', 'en': 'still, yet', 'pos': 'other'},
         {'he': 'לדאוג', 'en': 'to worry — לדאוג מ; to see to — לדאוג ל', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את השלילה', 'en': 'Choose the negative',
       'instructions': 'Each of these is wrong with the other two.',
       'items': [
         {'q': '___ אחד לא ידע מה לעשות.', 'options': ['אף', 'שום', 'בלי'], 'a': 'אף',
          'en': 'Nobody knew what to do. — אף goes with אחד.'},
         {'q': 'לא קרה ___ דבר.', 'options': ['שום', 'אף', 'אין'], 'a': 'שום',
          'en': 'Nothing happened. — שום goes with דבר.'},
         {'q': '___ תשכח את המפתחות!', 'options': ['אל', 'לא', 'אין'], 'a': 'אל',
          'en': 'Don’t forget the keys! — a negative order takes אל.'},
         {'q': '___ לי זמן היום.', 'options': ['אין', 'לא', 'אף'], 'a': 'אין',
          'en': 'I don’t have time today. — possession is negated with אין.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Hebrew keeps the לא even after אף and שום. Type what is missing.',
       'example': {'q': 'אף אחד ___ ענה. — nobody answered', 'a': 'לא'},
       'items': [
         {'q': 'אף פעם ___ הייתי שם.', 'a': ['לא'], 'en': 'I’ve never been there.'},
         {'q': 'לא רוצה ___ דבר, תודה.', 'a': ['שום'], 'en': 'I don’t want anything, thanks.'},
         {'q': 'הוא יצא ___ לומר מילה.', 'a': ['בלי'], 'en': 'He left without saying a word.'},
         {'q': '___ תגיד לו כלום.', 'a': ['אל'], 'en': 'Don’t tell him anything.'},
         {'q': 'עדיין ___ קיבלתי תשובה.', 'a': ['לא'], 'en': 'I still haven’t had an answer.'},
       ]},
      {'kind': 'transform', 'title': 'מחיוב לשלילה', 'en': 'Positive to negative',
       'instructions': 'Rewrite in the negative. Watch which negator the sentence needs.',
       'example': {'from': 'יש לי זמן.', 'to': 'אין לי זמן.'},
       'items': [
         {'from': 'כולם באו.', 'to': ['אף אחד לא בא.', 'אף אחד לא בא'], 'en': 'Everyone came.'},
         {'from': 'תלך הביתה.', 'to': ['אל תלך הביתה.', 'אל תלך הביתה'], 'en': 'Go home.'},
         {'from': 'אמרתי משהו.', 'to': ['לא אמרתי כלום.', 'לא אמרתי שום דבר.', 'לא אמרתי כלום', 'לא אמרתי שום דבר'],
          'en': 'I said something.'},
       ]},
      {'kind': 'slang', 'he': 'לא נורא', 'literal': '“not terrible”',
       'meaning': 'Never mind / it’s fine.',
       'when': 'The standard reply when someone apologises or something small goes wrong. It is '
               'not enthusiasm — it is dismissal of the problem, and it closes the subject.',
       'examples': [{'he': 'שברתי כוס. — לא נורא.', 'en': 'I broke a glass. — Never mind.'},
                    {'he': 'איחרתי קצת, לא נורא.', 'en': 'I was a bit late, it’s fine.'}]},
    ],
  },
  {
    'id': 'he-42', 'n': 42, 'level': 'intermediate',
    'title': {'he': 'השוואה', 'en': 'More, less, the most'},
    'objective': 'יותר מ, פחות מ, הכי, כמו. Hebrew has no -er and no -est: it puts a separate '
                 'word in front and the comparison hangs on מ.',
    'blocks': [
      {'kind': 'teach', 'title': 'The comparison hangs on מ־',
       'body': 'More is <b>יותר</b> and the thing compared takes <b>מ</b>: הוא גבוה '
               '<b>יותר ממני</b>, or the commoner order גבוה <b>ממני</b>. Less is '
               '<b>פחות מ</b>. The superlative is <b>הכי</b> before the adjective — הכי טוב, '
               'הכי יקר — or, in writing, <b>ה־ ביותר</b>: הטוב ביותר. Equality is <b>כמו</b>: '
               'גבוה כמוני. Note that מ fuses: ממני, ממך, ממנו.',
       'examples': [
         {'he': 'התל אביבי יקר יותר מהירושלמי.', 'en': 'The Tel Aviv one is more expensive than the Jerusalem one.'},
         {'he': 'זה הכי טעים שאכלתי.', 'en': 'That’s the tastiest thing I’ve eaten.'},
         {'he': 'הוא גבוה ממני בראש.', 'en': 'He’s a head taller than me.'},
         {'he': 'זה פחות חשוב ממה שחשבתי.', 'en': 'It’s less important than I thought.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'יותר', 'en': 'more', 'pos': 'other'},
         {'he': 'פחות', 'en': 'less', 'pos': 'other'},
         {'he': 'הכי', 'en': 'the most', 'pos': 'other'},
         {'he': 'כמו', 'en': 'like, as', 'pos': 'other'},
         {'he': 'הבדל', 'en': 'difference', 'pos': 'noun'},
         {'he': 'דומה', 'en': 'similar — דומה ל', 'pos': 'adj'},
         {'he': 'שונה', 'en': 'different — שונה מ', 'pos': 'adj'},
         {'he': 'זול', 'en': 'cheap', 'pos': 'adj'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the comparison word or the preposition it needs.',
       'example': {'q': 'הוא גבוה ___ ממני. — taller', 'a': 'יותר'},
       'items': [
         {'q': 'זה יקר יותר ___ הקודם.', 'a': ['מ', 'מן'], 'en': 'That’s more expensive than the previous one.'},
         {'q': 'זה ה___ טוב שיש.', 'a': ['הכי'], 'en': 'That’s the best there is.', 'hint': 'one word, before the adjective'},
         {'q': 'היא גבוהה ___ אחיה.', 'a': ['כמו'], 'en': 'She’s as tall as her brother.'},
         {'q': 'הבית שלי ___ לשלך.', 'a': ['דומה'], 'en': 'My house is similar to yours.'},
         {'q': 'הטיסה הזאת ___ יקרה מהאחרת.', 'a': ['פחות'], 'en': 'This flight is less expensive than the other.'},
       ]},
      {'kind': 'transform', 'title': 'הפכו להשוואה', 'en': 'Make it a comparison',
       'instructions': 'Rewrite so the two things are compared.',
       'example': {'from': 'הבית גדול. הדירה קטנה.', 'to': 'הבית גדול מהדירה.'},
       'items': [
         {'from': 'תל אביב יקרה. חיפה זולה.', 'to': ['תל אביב יקרה מחיפה.', 'תל אביב יקרה מחיפה'],
          'en': 'Tel Aviv is expensive. Haifa is cheap.'},
         {'from': 'הקפה חם. התה קר.', 'to': ['הקפה חם מהתה.', 'הקפה חם מהתה'],
          'en': 'The coffee is hot. The tea is cold.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Why is it גבוה ממני and not גבוה מאני?',
          'options': ['מ־ fuses with the pronoun', 'אני has no object form', 'It is a spelling rule only'],
          'a': 'מ־ fuses with the pronoun',
          'why': 'Every preposition in Hebrew takes pronoun endings: ממני, ממך, ממנו. Two free '
                 'words never sit there.'},
         {'q': 'הכי טוב and הטוב ביותר — what is the difference?',
          'options': ['Register: spoken and written', 'Meaning: best and better', 'Nothing at all'],
          'a': 'Register: spoken and written',
          'why': 'Identical meaning. הכי is what you say; ביותר is what a newspaper prints.'},
       ]},
      {'kind': 'slang', 'he': 'הכי הכי', 'literal': '“the most the most”',
       'meaning': 'The absolute best.',
       'when': 'Doubling for emphasis is very Hebrew — לאט לאט, טוב טוב, הכי הכי. It is '
               'childlike and completely normal in adult speech.',
       'examples': [{'he': 'זה הכי הכי שיש.', 'en': 'That’s the very best there is.'},
                    {'he': 'לאט לאט, אין לחץ.', 'en': 'Slowly, slowly — no rush.'}]},
    ],
  },
  {
    'id': 'he-43', 'n': 43, 'level': 'intermediate',
    'title': {'he': 'זמן ותדירות', 'en': 'How often, how long'},
    'objective': 'כל, פעם ב, לפני, אחרי, במשך, תוך, מאז. The words that answer "when" and "how '
                 'long" — and two of them are traps, because Hebrew splits duration from deadline.',
    'blocks': [
      {'kind': 'teach', 'title': 'במשך is how long; תוך is by when',
       'body': '<b>במשך שעה</b> means "for an hour, throughout"; <b>תוך שעה</b> means "within '
               'the hour, by then". English blurs them with "in" and Hebrew never does. '
               'Frequency: <b>כל יום</b>, <b>פעמיים בשבוע</b>, <b>אף פעם לא</b>, '
               '<b>בדרך כלל</b>. Anchors: <b>לפני</b>, <b>אחרי</b>, <b>מאז</b>, <b>עד</b>. Note '
               'that <b>לפני שנה</b> is "a year ago", not "before a year".',
       'examples': [
         {'he': 'עבדתי שם במשך שנתיים.', 'en': 'I worked there for two years.'},
         {'he': 'אני אחזור אליך תוך שעה.', 'en': 'I’ll get back to you within the hour.'},
         {'he': 'אנחנו נפגשים פעמיים בשבוע.', 'en': 'We meet twice a week.'},
         {'he': 'מאז שעברנו, לא ראיתי אותם.', 'en': 'Since we moved, I haven’t seen them.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'במשך', 'en': 'for, throughout (duration)', 'pos': 'other'},
         {'he': 'תוך', 'en': 'within (a deadline)', 'pos': 'other'},
         {'he': 'מאז', 'en': 'since', 'pos': 'other'},
         {'he': 'תמיד', 'en': 'always', 'pos': 'other'},
         {'he': 'לפעמים', 'en': 'sometimes', 'pos': 'other'},
         {'he': 'פעמיים', 'en': 'twice', 'pos': 'other'},
         {'he': 'שבועי', 'en': 'weekly', 'pos': 'adj'},
         {'he': 'חודשי', 'en': 'monthly', 'pos': 'adj'},
       ]},
      {'kind': 'choose', 'title': 'במשך או תוך?', 'en': 'במשך or תוך?',
       'instructions': 'Duration, or deadline?',
       'items': [
         {'q': 'הוא דיבר ___ שעה שלמה.', 'options': ['במשך', 'תוך', 'מאז'], 'a': 'במשך',
          'en': 'He talked for a whole hour. — duration.'},
         {'q': 'אני מסיים את זה ___ יומיים.', 'options': ['תוך', 'במשך', 'לפני'], 'a': 'תוך',
          'en': 'I’ll finish it within two days. — deadline.'},
         {'q': '___ שעברנו לפה הכל השתנה.', 'options': ['מאז', 'תוך', 'במשך'], 'a': 'מאז',
          'en': 'Since we moved here everything has changed.'},
         {'q': 'חיכינו ___ שעתיים ואז הלכנו.', 'options': ['במשך', 'תוך', 'עד'], 'a': 'במשך',
          'en': 'We waited for two hours and then left.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the time or frequency word.',
       'example': {'q': 'אנחנו נפגשים ___ בשבוע. — twice', 'a': 'פעמיים'},
       'items': [
         {'q': 'אני שותה קפה ___ בוקר.', 'a': ['כל'], 'en': 'I drink coffee every morning.'},
         {'q': '___ אני הולך ברגל, לפעמים באוטובוס.', 'a': ['בדרך כלל'], 'en': 'Usually I walk, sometimes I take the bus.'},
         {'q': 'הייתי שם ___ שנה.', 'a': ['לפני'], 'en': 'I was there a year ago.'},
         {'q': 'אף ___ לא ראיתי כזה דבר.', 'a': ['פעם'], 'en': 'I’ve never seen such a thing.'},
         {'q': 'נחכה ___ שהוא יגיע.', 'a': ['עד'], 'en': 'We’ll wait until he arrives.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['עבדתי', 'שם', 'במשך', 'שלוש', 'שנים'], 'a': 'עבדתי שם במשך שלוש שנים',
          'en': 'I worked there for three years.'},
         {'words': ['אנחנו', 'נפגשים', 'פעמיים', 'בחודש'], 'a': 'אנחנו נפגשים פעמיים בחודש',
          'en': 'We meet twice a month.'},
         {'words': ['מאז', 'שהוא', 'עזב', 'לא', 'דיברנו'], 'a': 'מאז שהוא עזב לא דיברנו',
          'en': 'Since he left we haven’t spoken.'},
       ]},
      {'kind': 'slang', 'he': 'עוד מעט', 'literal': '“a little more”',
       'meaning': 'In a minute / soon.',
       'when': 'The most elastic time expression in Hebrew: it covers anything from thirty '
               'seconds to next week, and everyone understands that it does.',
       'examples': [{'he': 'עוד מעט אני בא.', 'en': 'I’ll be there in a minute.'},
                    {'he': 'עוד מעט חורף.', 'en': 'Winter’s nearly here.'}]},
    ],
  },
  {
    'id': 'he-44', 'n': 44, 'level': 'intermediate',
    'title': {'he': 'היה + בינוני', 'en': 'What you used to do'},
    'objective': 'הייתי הולך. Same two words as the conditional, a completely different meaning — '
                 'and this one you need to talk about your childhood.',
    'blocks': [
      {'kind': 'teach', 'title': 'One shape, two jobs',
       'body': '<b>הייתי הולך</b> is either "I would have gone" (the conditional, unit '
               '“If and would”) or "I used to go" — a repeated action in the past. Only the '
               'context tells you, and the context is usually a time expression: '
               '<b>כשהייתי קטן</b>, <b>כל קיץ</b>, <b>פעם</b>. Israelis use the plain past for '
               'a habit too — כל קיץ נסענו לים — so this form is a choice, not an obligation, '
               'and it carries a note of nostalgia.',
       'examples': [
         {'he': 'כשהייתי קטן הייתי הולך לים כל יום.', 'en': 'When I was small I used to go to the sea every day.'},
         {'he': 'פעם היינו נפגשים כל שבוע.', 'en': 'We used to meet every week.'},
         {'he': 'סבתא הייתה מבשלת בשישי.', 'en': 'Grandma used to cook on Fridays.'},
         {'he': 'לא היינו יוצאים בערב.', 'en': 'We didn’t use to go out in the evening.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'פעם', 'en': 'once; in the old days', 'pos': 'other'},
         {'he': 'ילדות', 'en': 'childhood', 'pos': 'noun'},
         {'he': 'זיכרון', 'en': 'memory', 'pos': 'noun'},
         {'he': 'להתגעגע', 'en': 'to miss — להתגעגע ל', 'pos': 'verb'},
         {'he': 'להשתנות', 'en': 'to change (intransitive)', 'pos': 'verb'},
         {'he': 'מסורת', 'en': 'tradition', 'pos': 'noun'},
         {'he': 'שכונה', 'en': 'neighbourhood', 'pos': 'noun'},
         {'he': 'רגיל', 'en': 'ordinary, used to', 'pos': 'adj'},
       ]},
      {'kind': 'transform', 'title': 'מעבר להרגל', 'en': 'Past to habit',
       'instructions': 'Rewrite with היה so it means "used to".',
       'example': {'from': 'הלכתי לים כל יום.', 'to': 'הייתי הולך לים כל יום.'},
       'items': [
         {'from': 'נפגשנו כל שבוע.', 'to': ['היינו נפגשים כל שבוע.', 'היינו נפגשים כל שבוע'],
          'en': 'We met every week.'},
         {'from': 'היא בישלה בשישי.', 'to': ['היא הייתה מבשלת בשישי.', 'היא הייתה מבשלת בשישי'],
          'en': 'She cooked on Fridays.'},
         {'from': 'הם גרו בשכונה הזאת.', 'to': ['הם היו גרים בשכונה הזאת.', 'הם היו גרים בשכונה הזאת'],
          'en': 'They lived in this neighbourhood.'},
       ]},
      {'kind': 'quiz', 'title': 'הרגל או תנאי?', 'en': 'Habit or conditional?',
       'items': [
         {'q': 'כשהייתי סטודנט הייתי עובד בלילות.',
          'options': ['A habit — I used to work nights', 'A conditional — I would have worked nights'],
          'a': 'A habit — I used to work nights',
          'why': 'כשהייתי סטודנט anchors it in a real past. A conditional needs an אילו clause '
                 'or an unreal premise somewhere.'},
         {'q': 'אילו הייתי סטודנט הייתי עובד בלילות.',
          'options': ['A conditional — I would work nights', 'A habit — I used to work nights'],
          'a': 'A conditional — I would work nights',
          'why': 'אילו makes the premise untrue, so the same two words become the conditional.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing part of the habitual past.',
       'example': {'q': 'כשהייתי קטן ___ הולך לים. — I used to go', 'a': 'הייתי'},
       'items': [
         {'q': 'פעם ___ נפגשים כל שבוע.', 'a': ['היינו'], 'en': 'We used to meet every week.'},
         {'q': 'סבתא ___ מבשלת בשישי.', 'a': ['הייתה'], 'en': 'Grandma used to cook on Fridays.'},
         {'q': 'הם היו ___ בשכונה הזאת.', 'a': ['גרים'], 'en': 'They used to live in this neighbourhood.'},
         {'q': 'אני ___ געגוע לבית הישן.', 'a': ['מרגיש', 'מרגישה'], 'en': 'I feel nostalgic for the old house.'},
       ]},
      {'kind': 'slang', 'he': 'פעם', 'literal': '“once, a time”',
       'meaning': 'Back in the day.',
       'when': 'On its own at the start of a sentence, פעם means "in the old days" and always '
               'introduces a comparison with now. פעם זה היה אחרת is the whole national mood '
               'in four words.',
       'examples': [{'he': 'פעם זה היה אחרת.', 'en': 'Things were different back then.'},
                    {'he': 'פעם הייתי גר פה.', 'en': 'I used to live here.'}]},
    ],
  },
  {
    'id': 'he-45', 'n': 45, 'level': 'intermediate',
    'title': {'he': 'תאריכים ולוח השנה', 'en': 'Dates and the calendar'},
    'objective': 'Israel runs on two calendars at once, and the days of the week are numbers. '
                 'Both facts change how you say when something is.',
    'blocks': [
      {'kind': 'teach', 'title': 'The days are counted, and there are two calendars',
       'body': 'Sunday is <b>יום ראשון</b>, "day one", and the week runs to <b>יום שישי</b> and '
               'then <b>שבת</b> — which is the only day with a name. The working week starts on '
               'Sunday. Alongside the ordinary months (ינואר, פברואר) every date also has a '
               'Hebrew one — <b>תשרי</b>, <b>ניסן</b>, <b>שבט</b> — and it is the Hebrew date '
               'that decides when a festival falls, which is why they move against the ordinary '
               'calendar every year.',
       'examples': [
         {'he': 'ניפגש ביום שלישי בערב.', 'en': 'Let’s meet on Tuesday evening.'},
         {'he': 'הוא נולד בחודש מרץ.', 'en': 'He was born in March.'},
         {'he': 'ראש השנה חל בתשרי.', 'en': 'Rosh Hashana falls in Tishrei.'},
         {'he': 'סוף השבוע הוא שישי ושבת.', 'en': 'The weekend is Friday and Saturday.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'תאריך', 'en': 'date', 'pos': 'noun'},
         {'he': 'ראשון', 'en': 'first; Sunday', 'pos': 'adj'},
         {'he': 'שני', 'en': 'second; Monday', 'pos': 'adj'},
         {'he': 'שלישי', 'en': 'third; Tuesday', 'pos': 'adj'},
         {'he': 'רביעי', 'en': 'fourth; Wednesday', 'pos': 'adj'},
         {'he': 'חמישי', 'en': 'fifth; Thursday', 'pos': 'adj'},
         {'he': 'שישי', 'en': 'sixth; Friday', 'pos': 'adj'},
         {'he': 'שבת', 'en': 'Saturday, the Sabbath', 'pos': 'noun'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'יום ראשון', 'en': 'Sunday — the first working day'},
         {'he': 'יום חמישי', 'en': 'Thursday'},
         {'he': 'סוף השבוע', 'en': 'the weekend — Friday and Saturday'},
         {'he': 'החודש הבא', 'en': 'next month'},
         {'he': 'בשנה שעברה', 'en': 'last year'},
         {'he': 'מחרתיים', 'en': 'the day after tomorrow'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the day, month or time word.',
       'example': {'q': 'ניפגש ביום ___. — Tuesday', 'a': 'שלישי'},
       'items': [
         {'q': 'העבודה מתחילה ביום ___.', 'a': ['ראשון'], 'en': 'Work starts on Sunday.'},
         {'q': 'ב___ המשפחה אוכלת ביחד.', 'a': ['שבת'], 'en': 'On Saturday the family eats together.'},
         {'q': 'ראש השנה חל בחודש ___.', 'a': ['תשרי'], 'en': 'Rosh Hashana falls in Tishrei.'},
         {'q': 'מה ה___ היום?', 'a': ['תאריך'], 'en': 'What’s the date today?'},
         {'q': 'נוסעים ב___ הבא.', 'a': ['חודש', 'שבוע'], 'en': 'We travel next month / next week.'},
       ]},
      {'kind': 'slang', 'he': 'שבוע הבא בלי נדר', 'literal': '“next week, without a vow”',
       'meaning': 'Next week — but I’m not promising.',
       'when': 'בלי נדר comes straight out of religious law, where a promise is binding, and is '
               'now used by everyone to attach an escape clause to a plan. Perfectly ordinary '
               'in a secular office.',
       'examples': [{'he': 'נדבר מחר, בלי נדר.', 'en': 'We’ll talk tomorrow — no promises.'},
                    {'he': 'אני מגיע בשבע, בלי נדר.', 'en': 'I’ll be there at seven, all being well.'}]},
    ],
  },
  {
    'id': 'he-46', 'n': 46, 'level': 'beginner',
    'title': {'he': 'מזג אוויר', 'en': 'The weather'},
    'objective': 'Small talk you cannot avoid, and a grammar point hiding inside it: weather '
                 'sentences in Hebrew have no subject at all.',
    'blocks': [
      {'kind': 'teach', 'title': 'Nobody is hot — it is hot',
       'body': 'Hebrew says <b>חם</b> — just the adjective, no "it", no verb. <b>חם היום</b> is '
               'a whole sentence. To say YOU are hot, the frame is the same one as pain: '
               '<b>חם לי</b>, "hot to me". Rain and snow take the verb <b>יורד</b> — יורד גשם, '
               '"rain is coming down". And the forecast is a <b>תחזית</b>, which you will hear '
               'on the radio every hour.',
       'examples': [
         {'he': 'חם היום, נכון?', 'en': 'It’s hot today, isn’t it?'},
         {'he': 'קר לי, אני לוקח מעיל.', 'en': 'I’m cold, I’ll take a coat.'},
         {'he': 'יורד גשם מהבוקר.', 'en': 'It’s been raining since this morning.'},
         {'he': 'התחזית אומרת שיהיה נעים.', 'en': 'The forecast says it’ll be pleasant.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'חורף', 'en': 'winter', 'pos': 'noun'},
         {'he': 'אביב', 'en': 'spring', 'pos': 'noun'},
         {'he': 'קיץ', 'en': 'summer', 'pos': 'noun'},
         {'he': 'סתו', 'en': 'autumn', 'pos': 'noun'},
         {'he': 'גשם', 'en': 'rain', 'pos': 'noun'},
         {'he': 'שלג', 'en': 'snow', 'pos': 'noun'},
         {'he': 'ענן', 'en': 'cloud', 'pos': 'noun'},
         {'he': 'תחזית', 'en': 'forecast', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': '___ גשם כל היום. — it’s raining', 'a': 'יורד'},
       'items': [
         {'q': '___ לי, אפשר לסגור את החלון?', 'a': ['קר'], 'en': 'I’m cold, can we shut the window?'},
         {'q': 'ב___ יורד הרבה גשם.', 'a': ['חורף'], 'en': 'In winter it rains a lot.'},
         {'q': 'ה___ אומרת שמחר יהיה חם.', 'a': ['תחזית'], 'en': 'The forecast says it’ll be hot tomorrow.'},
         {'q': 'בהרים ירד ___ בלילה.', 'a': ['שלג'], 'en': 'It snowed in the mountains at night.'},
         {'q': 'ב___ הים חם ונעים.', 'a': ['קיץ'], 'en': 'In summer the sea is warm and pleasant.'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את התשובה', 'en': 'Choose the answer',
       'instructions': 'Pick the sentence a Hebrew speaker would say.',
       'items': [
         {'q': 'It’s hot today.', 'options': ['חם היום', 'זה חם היום', 'הוא חם היום'], 'a': 'חם היום',
          'en': 'No subject at all — that is the rule.'},
         {'q': 'I’m cold.', 'options': ['קר לי', 'אני קר', 'יש לי קר'], 'a': 'קר לי',
          'en': 'אני קר would mean you are a cold person.'},
         {'q': 'It’s raining.', 'options': ['יורד גשם', 'הגשם עושה', 'יש גשם היום'], 'a': 'יורד גשם',
          'en': 'Rain "comes down" in Hebrew.'},
       ]},
      {'kind': 'slang', 'he': 'שרב', 'literal': 'a hot dry desert wind',
       'meaning': 'A heatwave.',
       'when': 'The specific Israeli word for the dry eastern wind that pushes the temperature '
               'up ten degrees in a day. Everyone complains about it and nobody uses a general '
               'word for "heatwave" instead.',
       'examples': [{'he': 'יש שרב כל השבוע.', 'en': 'There’s a heatwave all week.'},
                    {'he': 'אחרי השרב ירד גשם.', 'en': 'After the heatwave it rained.'}]},
    ],
  },
  {
    'id': 'he-47', 'n': 47, 'level': 'beginner',
    'title': {'he': 'בגדים וקניות', 'en': 'Clothes and shopping'},
    'objective': 'Ask for a size, say what colour, try it on and decide. Colours are adjectives '
                 'and agree, which makes this unit quiet grammar practice as well.',
    'blocks': [
      {'kind': 'teach', 'title': 'The colour agrees with what it colours',
       'body': 'חולצה <b>לבנה</b>, מעיל <b>לבן</b>, נעליים <b>לבנות</b> — a colour is an '
               'adjective and takes the gender and number of the noun, like any other. Note '
               'that <b>מכנסיים</b> and <b>נעליים</b> are grammatically DUAL and always plural, '
               'so they take plural adjectives even when you mean one pair. To ask for a size: '
               '<b>יש את זה במידה …</b>',
       'examples': [
         {'he': 'יש את זה במידה גדולה יותר?', 'en': 'Do you have this in a bigger size?'},
         {'he': 'אני מחפש חולצה לבנה.', 'en': 'I’m looking for a white shirt.'},
         {'he': 'אפשר למדוד את זה?', 'en': 'Can I try this on?'},
         {'he': 'הנעליים האלה קטנות עליי.', 'en': 'These shoes are too small for me.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'חולצה', 'en': 'shirt', 'pos': 'noun'},
         {'he': 'מכנסיים', 'en': 'trousers', 'pos': 'noun'},
         {'he': 'שמלה', 'en': 'dress', 'pos': 'noun'},
         {'he': 'נעליים', 'en': 'shoes', 'pos': 'noun'},
         {'he': 'מעיל', 'en': 'coat', 'pos': 'noun'},
         {'he': 'מידה', 'en': 'size', 'pos': 'noun'},
         {'he': 'למדוד', 'en': 'to measure, to try on', 'pos': 'verb'},
         {'he': 'להתאים', 'en': 'to fit, to suit — להתאים ל', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Mind the agreement — the colour follows the noun.',
       'example': {'q': 'חולצה ___ — a white shirt', 'a': 'לבנה'},
       'items': [
         {'q': 'קניתי מעיל ___.', 'a': ['שחור'], 'en': 'I bought a black coat.'},
         {'q': 'הנעליים ה___ יפות.', 'a': ['אדומות'], 'en': 'The red shoes are nice.'},
         {'q': 'יש את זה ב___ אחרת?', 'a': ['מידה'], 'en': 'Do you have it in another size?'},
         {'q': 'אפשר ___ את השמלה?', 'a': ['למדוד'], 'en': 'Can I try the dress on?'},
         {'q': 'המכנסיים האלה לא ___ לי.', 'a': ['מתאימים'], 'en': 'These trousers don’t fit me.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'כמה זה עולה?', 'en': 'How much is it?'},
         {'he': 'אפשר למדוד?', 'en': 'Can I try it on?'},
         {'he': 'יש במידה אחרת?', 'en': 'Do you have another size?'},
         {'he': 'זה קטן עליי', 'en': 'It’s too small for me'},
         {'he': 'אני רק מסתכל', 'en': 'I’m just looking'},
         {'he': 'אפשר להחזיר?', 'en': 'Can I return it?'},
       ]},
      {'kind': 'slang', 'he': 'קטן עליי', 'literal': '“small on me”',
       'meaning': 'Easy — I can handle that.',
       'when': 'In a shop it means the thing does not fit. Everywhere else it means the task is '
               'beneath your abilities, which is the commoner use by far, and it is said with '
               'confidence rather than boasting.',
       'examples': [{'he': 'המבחן הזה קטן עליך.', 'en': 'That exam is easy for you.'},
                    {'he': 'החולצה קטנה עליי.', 'en': 'The shirt is too small for me.'}]},
    ],
  },
  {
    'id': 'he-48', 'n': 48, 'level': 'beginner',
    'title': {'he': 'הגוף', 'en': 'The body'},
    'objective': 'The parts of the body — and the fact that most of the paired ones are '
                 'grammatically feminine and dual, which explains a lot of endings you have '
                 'already seen.',
    'blocks': [
      {'kind': 'teach', 'title': 'Paired parts are feminine and come in twos',
       'body': '<b>יד</b>, <b>רגל</b>, <b>עין</b>, <b>אוזן</b> are all feminine, and their '
               'plural is the DUAL: <b>ידיים</b>, <b>רגליים</b>, <b>עיניים</b>, '
               '<b>אוזניים</b> — the same ־ַיִם you met on מכנסיים and שעתיים. Unpaired parts '
               'are mostly masculine: ראש, גב, פה. This is why כואבות לי הרגליים and כואב לי '
               'הראש take different verb forms.',
       'examples': [
         {'he': 'יש לו עיניים כחולות.', 'en': 'He has blue eyes.'},
         {'he': 'שטפתי ידיים לפני האוכל.', 'en': 'I washed my hands before the meal.'},
         {'he': 'הרגליים שלי עייפות.', 'en': 'My legs are tired.'},
         {'he': 'תשמע בשתי אוזניים.', 'en': 'Listen with both ears.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ראש', 'en': 'head', 'pos': 'noun'},
         {'he': 'פנים', 'en': 'face', 'pos': 'noun'},
         {'he': 'יד', 'en': 'hand, arm', 'pos': 'noun'},
         {'he': 'רגל', 'en': 'leg, foot', 'pos': 'noun'},
         {'he': 'אצבע', 'en': 'finger', 'pos': 'noun'},
         {'he': 'גב', 'en': 'back', 'pos': 'noun'},
         {'he': 'שיער', 'en': 'hair', 'pos': 'noun'},
         {'he': 'עור', 'en': 'skin', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the body part, in the number the sentence needs.',
       'example': {'q': 'יש לו ___ כחולות. — eyes', 'a': 'עיניים'},
       'items': [
         {'q': 'שטפתי ___ לפני האוכל.', 'a': ['ידיים'], 'en': 'I washed my hands before the meal.'},
         {'q': 'ה___ שלי עייפות מההליכה.', 'a': ['רגליים'], 'en': 'My legs are tired from the walk.'},
         {'q': 'כואב לי ה___.', 'a': ['ראש', 'גב'], 'en': 'My head / back hurts.'},
         {'q': 'יש לה ___ ארוך ושחור.', 'a': ['שיער'], 'en': 'She has long black hair.'},
         {'q': 'תשמע בשתי ה___.', 'a': ['אוזניים'], 'en': 'Listen with both ears.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'ראש', 'en': 'head'},
         {'he': 'יד', 'en': 'hand'},
         {'he': 'רגל', 'en': 'leg'},
         {'he': 'עין', 'en': 'eye'},
         {'he': 'אוזן', 'en': 'ear'},
         {'he': 'גב', 'en': 'back'},
       ]},
      {'kind': 'slang', 'he': 'ראש גדול', 'literal': '“a big head”',
       'meaning': 'Someone who takes initiative and does more than asked.',
       'when': 'Army slang that went everywhere. Its opposite, ראש קטן, means doing exactly what '
               'you were told and not one thing more — and it is a serious insult at work.',
       'examples': [{'he': 'הוא עובד עם ראש גדול.', 'en': 'He works with real initiative.'},
                    {'he': 'אל תהיה ראש קטן.', 'en': 'Don’t just do the minimum.'}]},
    ],
  },
  {
    'id': 'he-49', 'n': 49, 'level': 'intermediate',
    'title': {'he': 'הבניין והשכנים', 'en': 'The building and the neighbours'},
    'objective': 'Israeli life happens in a בניין with a ועד בית, and the vocabulary of the '
                 'stairwell is not in any beginner book.',
    'blocks': [
      {'kind': 'teach', 'title': 'The stairwell has its own institutions',
       'body': 'A flat is on a <b>קומה</b>, reached by <b>מדרגות</b> or a <b>מעלית</b>. The '
               'building runs itself through a <b>ועד בית</b> — the residents’ committee, which '
               'collects money and argues about the lift. <b>שיפוץ</b> (renovation) and '
               '<b>רעש</b> are the two words that generate more messages in a building group '
               'than everything else combined.',
       'examples': [
         {'he': 'אני גר בקומה שלישית.', 'en': 'I live on the third floor.'},
         {'he': 'המעלית לא עובדת שוב.', 'en': 'The lift isn’t working again.'},
         {'he': 'ועד הבית ביקש כסף לשיפוץ.', 'en': 'The residents’ committee asked for money for the renovation.'},
         {'he': 'יש רעש מהדירה למעלה.', 'en': 'There’s noise from the flat upstairs.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'בניין', 'en': 'building', 'pos': 'noun'},
         {'he': 'קומה', 'en': 'floor, storey', 'pos': 'noun'},
         {'he': 'מדרגות', 'en': 'stairs', 'pos': 'noun'},
         {'he': 'מעלית', 'en': 'lift, elevator', 'pos': 'noun'},
         {'he': 'מרפסת', 'en': 'balcony', 'pos': 'noun'},
         {'he': 'חניה', 'en': 'parking', 'pos': 'noun'},
         {'he': 'זבל', 'en': 'rubbish', 'pos': 'noun'},
         {'he': 'שיפוץ', 'en': 'renovation', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'אני גר ב___ שלישית. — on the third floor', 'a': 'קומה'},
       'items': [
         {'q': 'ה___ לא עובדת, נעלה במדרגות.', 'a': ['מעלית'], 'en': 'The lift isn’t working, we’ll take the stairs.'},
         {'q': 'יושבים על ה___ בערב.', 'a': ['מרפסת'], 'en': 'We sit on the balcony in the evening.'},
         {'q': 'ועד ה___ אסף כסף.', 'a': ['בית'], 'en': 'The residents’ committee collected money.'},
         {'q': 'צריך להוציא את ה___.', 'a': ['זבל'], 'en': 'The rubbish needs taking out.'},
         {'q': 'אין ___ ברחוב הזה בכלל.', 'a': ['חניה'], 'en': 'There’s no parking on this street at all.'},
       ]},
      {'kind': 'choose', 'title': 'מה אומרים לשכן?', 'en': 'What do you say to a neighbour?',
       'instructions': 'Pick the Hebrew that would actually be said.',
       'items': [
         {'q': 'The noise is keeping you awake at midnight.',
          'options': ['סליחה, אפשר קצת יותר בשקט?', 'אתם עושים רעש!', 'אני קורא למשטרה'],
          'a': 'סליחה, אפשר קצת יותר בשקט?', 'en': 'Politeness first — and it usually works.'},
         {'q': 'You are having work done and want to warn the building.',
          'options': ['סליחה מראש על הרעש, יש שיפוץ', 'יהיה רעש', 'לא אכפת לי'],
          'a': 'סליחה מראש על הרעש, יש שיפוץ', 'en': '“Sorry in advance for the noise, we’re renovating.”'},
         {'q': 'You want to borrow something small.',
          'options': ['יש לך במקרה קצת סוכר?', 'תן לי סוכר', 'אני צריך סוכר'],
          'a': 'יש לך במקרה קצת סוכר?', 'en': 'במקרה — “do you happen to have” — is the softener.'},
       ]},
      {'kind': 'slang', 'he': 'ועד בית', 'literal': '“house committee”',
       'meaning': 'The residents’ committee — and, by extension, any small self-important body.',
       'when': 'Every apartment building has one, everyone complains about it, and calling a '
               'committee at work "ועד בית" is a way of saying it has more meetings than powers.',
       'examples': [{'he': 'שילמתי ועד בית לחודש.', 'en': 'I paid the building fee for the month.'},
                    {'he': 'זה לא ישיבה, זה ועד בית.', 'en': 'That’s not a meeting, it’s a residents’ committee.'}]},
    ],
  },
  {
    'id': 'he-50', 'n': 50, 'level': 'intermediate',
    'title': {'he': 'חגים', 'en': 'The festivals'},
    'objective': 'The year has a shape in Israel and it is not the one on your calendar. Even a '
                 'secular week bends around שבת, and the greetings are fixed phrases you will '
                 'need on specific days.',
    'blocks': [
      {'kind': 'teach', 'title': 'A greeting for every festival',
       'body': 'The general one is <b>חג שמח</b>. On Rosh Hashana it is <b>שנה טובה</b>; before '
               'Yom Kippur, <b>גמר חתימה טובה</b>; on Shabbat, <b>שבת שלום</b>, said from '
               'Thursday onwards. After a festival ends: <b>שבוע טוב</b>. These are said by '
               'everyone, religious or not — they are the calendar’s small talk, and not saying '
               'them back is the only mistake available.',
       'examples': [
         {'he': 'שבת שלום, נתראה בראשון.', 'en': 'Shabbat shalom, see you Sunday.'},
         {'he': 'שנה טובה ומתוקה!', 'en': 'A good and sweet year!'},
         {'he': 'בפסח כל המשפחה מתאספת.', 'en': 'At Passover the whole family gathers.'},
         {'he': 'בחנוכה מדליקים נרות שמונה ימים.', 'en': 'At Hanukkah you light candles for eight days.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'חג', 'en': 'festival, holiday', 'pos': 'noun'},
         {'he': 'נר', 'en': 'candle', 'pos': 'noun'},
         {'he': 'מתנה', 'en': 'present, gift', 'pos': 'noun'},
         {'he': 'סעודה', 'en': 'a festive meal', 'pos': 'noun'},
         {'he': 'מסורת', 'en': 'tradition', 'pos': 'noun'},
         {'he': 'להתאסף', 'en': 'to gather', 'pos': 'verb'},
         {'he': 'להדליק', 'en': 'to light, to switch on', 'pos': 'verb'},
         {'he': 'לחגוג', 'en': 'to celebrate', 'pos': 'verb'},
       ]},
      {'kind': 'match', 'title': 'התאימו ברכה לחג', 'en': 'Match the greeting to the day',
       'instructions': 'Tap the Hebrew, then when you say it.',
       'pairs': [
         {'he': 'שבת שלום', 'en': 'from Thursday until Saturday night'},
         {'he': 'שנה טובה', 'en': 'at Rosh Hashana, the new year'},
         {'he': 'חג שמח', 'en': 'on any festival'},
         {'he': 'שבוע טוב', 'en': 'once Shabbat has ended'},
         {'he': 'מזל טוב', 'en': 'for a birth, a wedding, an exam passed'},
         {'he': 'בשורות טובות', 'en': '“good news” — said when someone is waiting for some'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'בחנוכה ___ נרות. — you light', 'a': 'מדליקים'},
       'items': [
         {'q': 'ב___ כל המשפחה מתאספת לסעודה.', 'a': ['פסח', 'חג'], 'en': 'At Passover / on the festival the whole family gathers for a meal.'},
         {'q': 'קניתי ___ קטנה לילדים.', 'a': ['מתנה'], 'en': 'I bought a small present for the children.'},
         {'q': 'בערב שבת מדליקים ___.', 'a': ['נרות'], 'en': 'On Friday evening you light candles.'},
         {'q': 'איך ___ את יום ההולדת?', 'a': ['חוגגים'], 'en': 'How do you celebrate the birthday?'},
         {'q': 'זו ה___ אצלנו במשפחה.', 'a': ['מסורת'], 'en': 'That’s the tradition in our family.'},
       ]},
      {'kind': 'slang', 'he': 'אחרי החגים', 'literal': '“after the festivals”',
       'meaning': 'Later — much later. Possibly never.',
       'when': 'Between Rosh Hashana and Sukkot the country slows to a stop, and אחרי החגים '
               'becomes the standard way to postpone anything by a month. Said all year round '
               'as a joke about exactly that.',
       'examples': [{'he': 'נטפל בזה אחרי החגים.', 'en': 'We’ll deal with it after the holidays.'},
                    {'he': 'הכל אצלנו אחרי החגים.', 'en': 'With us, everything happens after the holidays.'}]},
    ],
  },
  {
    'id': 'he-51', 'n': 51, 'level': 'intermediate',
    'title': {'he': 'רגשות', 'en': 'How you feel'},
    'objective': 'Hebrew puts most feelings in the PRESENT PARTICIPLE — you are not sad, you are '
                 'sadding — and several of the commonest are reflexive verbs.',
    'blocks': [
      {'kind': 'teach', 'title': 'Many feelings are verbs, not adjectives',
       'body': 'שָׂמֵחַ and עָצוּב are adjectives, but <b>מתרגש</b> (excited), <b>מודאג</b> '
               '(worried), <b>מאוכזב</b> (disappointed) and <b>מתגעגע</b> (missing someone) are '
               'participles of verbs and take the endings of one: מתרגשת, מתרגשים. Note the '
               'preposition — <b>מתגעגע ל</b>, <b>דואג מ</b>, <b>כועס על</b> — and that Hebrew '
               'says <b>נמאס לי</b>, "it has become tiresome to me", for "I’m fed up".',
       'examples': [
         {'he': 'אני מתרגש לקראת הנסיעה.', 'en': 'I’m excited about the trip.'},
         {'he': 'היא כועסת עליי כבר יומיים.', 'en': 'She’s been angry with me for two days.'},
         {'he': 'אני מתגעגע לבית.', 'en': 'I miss home.'},
         {'he': 'נמאס לי מהמצב הזה.', 'en': 'I’m fed up with this situation.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'שמח', 'en': 'happy', 'pos': 'adj'},
         {'he': 'עצוב', 'en': 'sad', 'pos': 'adj'},
         {'he': 'מודאג', 'en': 'worried', 'pos': 'adj'},
         {'he': 'גאה', 'en': 'proud — גאה ב', 'pos': 'adj'},
         {'he': 'בודד', 'en': 'lonely', 'pos': 'adj'},
         {'he': 'להתרגש', 'en': 'to be excited, to be moved', 'pos': 'verb'},
         {'he': 'להתגעגע', 'en': 'to miss — להתגעגע ל', 'pos': 'verb'},
         {'he': 'לכעוס', 'en': 'to be angry — לכעוס על', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the feeling — mind the ending and the preposition.',
       'example': {'q': 'אני ___ לבית. — I miss home', 'a': 'מתגעגע'},
       'items': [
         {'q': 'היא כועסת ___ אחיה.', 'a': ['על'], 'en': 'She’s angry with her brother.'},
         {'q': 'אני ___ מהמצב הזה.', 'a': ['מודאג', 'מודאגת'], 'en': 'I’m worried about this situation.'},
         {'q': 'ההורים שלו ___ בו מאוד.', 'a': ['גאים'], 'en': 'His parents are very proud of him.'},
         {'q': 'נמאס ___ לחכות.', 'a': ['לי'], 'en': 'I’m fed up with waiting.'},
         {'q': 'כולם ___ לקראת החתונה.', 'a': ['מתרגשים'], 'en': 'Everyone is excited about the wedding.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'נמאס לי', 'en': 'I’m fed up'},
         {'he': 'בא לי', 'en': 'I feel like'},
         {'he': 'אכפת לי', 'en': 'I care'},
         {'he': 'מפריע לי', 'en': 'It bothers me'},
         {'he': 'מתחשק לי', 'en': 'I’m in the mood for'},
         {'he': 'חבל לי', 'en': 'I’m sorry about it'},
       ]},
      {'kind': 'slang', 'he': 'בא לי', 'literal': '“it comes to me”',
       'meaning': 'I feel like it.',
       'when': 'The whole grammar of Israeli desire: not "I want" but "it comes to me". '
               'בא לי קפה is "I fancy a coffee", and לא בא לי is a complete and final refusal '
               'that needs no reason.',
       'examples': [{'he': 'בא לי משהו מתוק.', 'en': 'I fancy something sweet.'},
                    {'he': 'לא בא לי לצאת היום.', 'en': 'I don’t feel like going out today.'}]},
    ],
  },
  {
    'id': 'he-52', 'n': 52, 'level': 'advanced',
    'title': {'he': 'מייל והודעה', 'en': 'Writing an email and a text'},
    'objective': 'The register unit put to work. A Hebrew email opens and closes with fixed '
                 'phrases, and a WhatsApp message obeys none of them — getting the two the wrong '
                 'way round is the most visible mistake a fluent learner still makes.',
    'blocks': [
      {'kind': 'teach', 'title': 'Two registers, two sets of furniture',
       'body': 'An email opens <b>שלום רב</b> or <b>היי</b> + name, states the matter, and closes '
               '<b>בברכה</b> or, formally, <b>בכבוד רב</b>. A message opens with nothing at all — '
               'Israelis do not write "Hi, hope you are well", they write the thing. '
               '<b>מצורף</b> means "attached"; <b>בהמשך ל</b> is "further to"; '
               '<b>אשמח לעדכון</b> is the polite way to chase, and it is everywhere.',
       'examples': [
         {'he': 'שלום רב, בהמשך לשיחתנו מאתמול.', 'en': 'Dear Sir/Madam, further to our conversation yesterday.'},
         {'he': 'מצורף המסמך שביקשת.', 'en': 'Attached is the document you asked for.'},
         {'he': 'אשמח לעדכון בהקדם.', 'en': 'I’d appreciate an update as soon as possible.'},
         {'he': 'תודה מראש, בברכה, דנה.', 'en': 'Thanks in advance, best regards, Dana.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'מייל', 'en': 'email', 'pos': 'noun'},
         {'he': 'הודעה', 'en': 'message', 'pos': 'noun'},
         {'he': 'כתובת', 'en': 'address', 'pos': 'noun'},
         {'he': 'נושא', 'en': 'subject, topic', 'pos': 'noun'},
         {'he': 'מסמך', 'en': 'document, file', 'pos': 'noun'},
         {'he': 'לצרף', 'en': 'to attach, to add', 'pos': 'verb'},
         {'he': 'לענות', 'en': 'to reply — לענות ל', 'pos': 'verb'},
         {'he': 'תשובה', 'en': 'an answer, a reply', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'מייל או הודעה?', 'en': 'Email or text?',
       'instructions': 'One of these would look wrong in the other channel.',
       'items': [
         {'q': 'Opening a formal email to someone you have not met.',
          'options': ['שלום רב,', 'מה קורה?', 'היי, מה נשמע'], 'a': 'שלום רב,',
          'en': 'שלום רב is the written opener; the other two are speech.'},
         {'q': 'Closing a work email.',
          'options': ['בברכה', 'ביי', 'נדבר'], 'a': 'בברכה',
          'en': 'ביי and נדבר end a phone call, not a letter.'},
         {'q': 'Texting a friend to ask if they are coming.',
          'options': ['בא?', 'הנך מתכוון להגיע?', 'אשמח לעדכון בהקדם'], 'a': 'בא?',
          'en': 'One word is a complete Israeli text message.'},
         {'q': 'Chasing a reply from an office, politely.',
          'options': ['אשמח לעדכון', 'למה לא ענית?', 'תענה בבקשה'], 'a': 'אשמח לעדכון',
          'en': 'The standard, and it does not sound annoyed even when you are.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['מצורף', 'המסמך', 'שביקשת', 'אתמול'], 'a': 'מצורף המסמך שביקשת אתמול',
          'en': 'Attached is the document you asked for yesterday.'},
         {'words': ['אשמח', 'לקבל', 'תשובה', 'עד', 'יום', 'חמישי'],
          'a': 'אשמח לקבל תשובה עד יום חמישי', 'en': 'I’d be glad to have an answer by Thursday.'},
         {'words': ['תודה', 'מראש', 'על', 'העזרה'], 'a': 'תודה מראש על העזרה',
          'en': 'Thanks in advance for the help.'},
       ]},
      {'kind': 'transform', 'title': 'ממייל להודעה', 'en': 'From an email to a text',
       'instructions': 'Rewrite the way you would actually send it to a friend.',
       'example': {'from': 'שלום רב, האם תוכל להגיע?', 'to': 'בא?'},
       'items': [
         {'from': 'אשמח לעדכון בהקדם האפשרי.', 'to': ['מה קורה עם זה?', 'מה קורה עם זה'],
          'en': 'I’d appreciate an update as soon as possible.'},
         {'from': 'בהמשך לשיחתנו, אני מצרף את המסמך.', 'to': ['שולח לך את המסמך.', 'שולח לך את המסמך'],
          'en': 'Further to our conversation, I attach the document.'},
       ]},
      {'kind': 'slang', 'he': 'אשמח', 'literal': '“I will be glad”',
       'meaning': 'Please / I’d like you to.',
       'when': 'Written Hebrew’s politeness engine. אשמח לעדכון, אשמח לתשובה, אשמח אם תוכל — it '
               'turns a demand into a request, and an Israeli inbox is full of it.',
       'examples': [{'he': 'אשמח אם תוכל לבדוק.', 'en': 'I’d be grateful if you could check.'},
                    {'he': 'אשמח לתשובה עד מחר.', 'en': 'I’d appreciate an answer by tomorrow.'}]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
# UNITS 53-64. Five more grammar gaps, and they are the ones that make a learner sound foreign
# long after their vocabulary is fine: the irregular root families, the preposition paradigms,
# the passive participle, the number-gender system, and the ה/את pair. Then seven more corners
# of an ordinary week -- the ones with their own closed vocabulary that nobody teaches until you
# are standing in them.
UNITS += [
  {
    'id': 'he-53', 'n': 53, 'level': 'intermediate',
    'title': {'he': 'גזרות חריגות', 'en': 'The verbs that lose a letter'},
    'objective': 'ליפול, לתת, לשבת, לדעת, לקחת. Five families whose first root letter vanishes '
                 'in the future and the infinitive — and they are among the commonest verbs in '
                 'the language, so this is not a footnote.',
    'blocks': [
      {'kind': 'teach', 'title': 'A נ or a י at the front does not survive',
       'body': 'פ״נ verbs drop the נ: נפל → <b>אפול</b>, נסע → <b>אסע</b>, נתן → <b>אתן</b>, and '
               'the infinitive shrinks with it — <b>לתת</b>, <b>לגשת</b>. פ״י verbs turn the י '
               'into a vowel: ישב → <b>אשב</b>, <b>לשבת</b>; ידע → <b>אדע</b>, <b>לדעת</b>; '
               'יצא → <b>אצא</b>, <b>לצאת</b>. And <b>לקחת</b> behaves like a פ״נ even though it '
               'starts with ל — the only verb in Hebrew that does. Learn these as a family and '
               'they stop being surprises.',
       'examples': [
         {'he': 'אני אתן לך תשובה מחר.', 'en': 'I’ll give you an answer tomorrow.'},
         {'he': 'נשב פה רגע ונדבר.', 'en': 'Let’s sit here a moment and talk.'},
         {'he': 'מתי תצא מהעבודה?', 'en': 'When will you leave work?'},
         {'he': 'תיקח מונית, זה יותר מהר.', 'en': 'Take a taxi, it’s faster.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לתת', 'en': 'to give', 'pos': 'verb'},
         {'he': 'לשבת', 'en': 'to sit', 'pos': 'verb'},
         {'he': 'לדעת', 'en': 'to know', 'pos': 'verb'},
         {'he': 'לצאת', 'en': 'to go out', 'pos': 'verb'},
         {'he': 'לקחת', 'en': 'to take', 'pos': 'verb'},
         {'he': 'ליפול', 'en': 'to fall', 'pos': 'verb'},
         {'he': 'לגשת', 'en': 'to approach, to go over — לגשת ל', 'pos': 'verb'},
         {'he': 'לגעת', 'en': 'to touch — לגעת ב', 'pos': 'verb'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'The infinitive is printed. Write the אני form in the future.',
       'cols': ['שם פועל', 'הוא, עבר', 'אני, עתיד'],
       'rows': [
         [{'g': 'לתת'}, {'g': 'נתן'}, {'g': 'אתן'}],
         [{'g': 'לשבת'}, {'a': ['ישב']}, {'a': ['אשב']}],
         [{'g': 'לדעת'}, {'a': ['ידע']}, {'a': ['אדע']}],
         [{'g': 'לצאת'}, {'a': ['יצא']}, {'a': ['אצא']}],
         [{'g': 'לקחת'}, {'a': ['לקח']}, {'a': ['אקח']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל', 'en': 'Write the verb',
       'instructions': 'The infinitive is in brackets; write the future form that fits.',
       'example': {'q': 'מחר אני ___ לך תשובה. [לתת]', 'a': 'אתן'},
       'items': [
         {'q': 'אנחנו ___ פה ונחכה. [לשבת]', 'a': ['נשב'], 'en': 'We’ll sit here and wait.'},
         {'q': 'מתי אתה ___ מהבית? [לצאת]', 'a': ['תצא'], 'en': 'When will you leave the house?'},
         {'q': 'הם ___ מונית לשדה התעופה. [לקחת]', 'a': ['ייקחו', 'יקחו'], 'en': 'They’ll take a taxi to the airport.'},
         {'q': 'אני לא ___ מה לעשות. [לדעת]', 'a': ['יודע', 'יודעת'], 'en': 'I don’t know what to do.'},
         {'q': 'תיזהר, אתה ___! [ליפול]', 'a': ['תיפול'], 'en': 'Careful, you’ll fall!'},
       ]},
      {'kind': 'slang', 'he': 'תן לי לחשוב', 'literal': '“give me to think”',
       'meaning': 'Let me think.',
       'when': 'נתן does the work of English "let" all over Hebrew: תן לי, תן לו, אל תיתן. It '
               'is one of the first places a learner meets this family and one of the last '
               'places they expect an irregular verb.',
       'examples': [{'he': 'תן לי רגע לחשוב.', 'en': 'Give me a moment to think.'},
                    {'he': 'אל תיתן לזה להפריע לך.', 'en': 'Don’t let it bother you.'}]},
    ],
  },
  {
    'id': 'he-54', 'n': 54, 'level': 'intermediate',
    'title': {'he': 'מילות יחס עם כינויים', 'en': 'Prepositions that take endings'},
    'objective': 'Not just ל־. Every Hebrew preposition swallows its pronoun — עליי, אליי, איתי, '
                 'בשבילי, אצלי, לידי — and two free words in that slot is the fastest way to '
                 'sound like a translation.',
    'blocks': [
      {'kind': 'teach', 'title': 'The pronoun goes INSIDE the preposition',
       'body': 'Never על אני — always <b>עליי</b>. Never את אני — <b>אותי</b>. The endings are '
               'the same set every time, and they split into two patterns: singular-type '
               '(עליי, עליך, עליו, עליה) and plural-type (עלינו, עליכם, עליהם). Learn one '
               'preposition of each shape and the rest follow: <b>של</b>, <b>ל</b>, <b>ב</b>, '
               '<b>עם/את</b> → איתי, <b>אצל</b>, <b>בשביל</b>, <b>ליד</b>, <b>אחרי</b>, '
               '<b>לפני</b>, <b>בלי</b> → בלעדיי.',
       'examples': [
         {'he': 'הוא סיפר לי עליך.', 'en': 'He told me about you.'},
         {'he': 'בוא איתי, זה בדרך.', 'en': 'Come with me, it’s on the way.'},
         {'he': 'קניתי את זה בשבילך.', 'en': 'I bought it for you.'},
         {'he': 'נפגשנו אצלה בבית.', 'en': 'We met at her place.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אצל', 'en': 'at (someone’s place)', 'pos': 'other'},
         {'he': 'בשביל', 'en': 'for, for the sake of', 'pos': 'other'},
         {'he': 'ליד', 'en': 'next to', 'pos': 'other'},
         {'he': 'מול', 'en': 'opposite, facing', 'pos': 'other'},
         {'he': 'לפני', 'en': 'before, in front of', 'pos': 'other'},
         {'he': 'אחרי', 'en': 'after, behind', 'pos': 'other'},
         {'he': 'בלי', 'en': 'without → בלעדיי', 'pos': 'other'},
         {'he': 'עם', 'en': 'with → איתי', 'pos': 'other'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'Some cells are printed, the rest you type.',
       'cols': ['מילת יחס', 'אני', 'אתה', 'הוא'],
       'rows': [
         [{'g': 'על'}, {'g': 'עליי'}, {'g': 'עליך'}, {'g': 'עליו'}],
         [{'g': 'אל'}, {'a': ['אליי']}, {'a': ['אליך']}, {'a': ['אליו']}],
         [{'g': 'ל'}, {'a': ['לי']}, {'a': ['לך']}, {'a': ['לו']}],
         [{'g': 'עם'}, {'a': ['איתי']}, {'a': ['איתך']}, {'a': ['איתו']}],
         [{'g': 'אצל'}, {'a': ['אצלי']}, {'a': ['אצלך']}, {'a': ['אצלו']}],
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'One word — the preposition with its ending inside it.',
       'example': {'q': 'הוא סיפר לי ___. — about you (m.)', 'a': 'עליך'},
       'items': [
         {'q': 'בוא ___, זה בדרך.', 'a': ['איתי'], 'en': 'Come with me, it’s on the way.'},
         {'q': 'קניתי את זה ___.', 'a': ['בשבילך', 'בשבילה', 'בשבילו'], 'en': 'I bought it for you / her / him.'},
         {'q': 'נפגשנו ___ בבית.', 'a': ['אצלה', 'אצלו', 'אצלי'], 'en': 'We met at her / his / my place.'},
         {'q': 'הוא ישב ___ באוטובוס.', 'a': ['לידי'], 'en': 'He sat next to me on the bus.'},
         {'q': 'אל תלך ___, חכה לי.', 'a': ['בלעדיי'], 'en': 'Don’t go without me, wait for me.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Why is “with me” איתי and not עם אני?',
          'options': ['A preposition always absorbs its pronoun',
                      'עם has no plural', 'It is an exception'],
          'a': 'A preposition always absorbs its pronoun',
          'why': 'It is the rule, not the exception — and it is why איתי, עליי and אליי all '
                 'look like one word: they are.'},
         {'q': 'אצלנו can mean two things. Which?',
          'options': ['“at our place” and “with us / in our culture”',
                      '“near us” and “after us”', 'Only “at our place”'],
          'a': '“at our place” and “with us / in our culture”',
          'why': 'אצלנו בארץ is “here in this country, the way we do it”, and it is used '
                 'constantly to introduce a national habit.'},
       ]},
      {'kind': 'slang', 'he': 'אצלנו', 'literal': '“at our place”',
       'meaning': 'Round here / the way we do things.',
       'when': 'אצלנו בארץ or אצלנו בעבודה opens a comparison with somewhere else. It is the '
               'single most common way an Israeli explains a local habit to a foreigner.',
       'examples': [{'he': 'אצלנו זה עובד אחרת.', 'en': 'Round here it works differently.'},
                    {'he': 'אצלנו בבית תמיד אוכלים בשבע.', 'en': 'In our house we always eat at seven.'}]},
    ],
  },
  {
    'id': 'he-55', 'n': 55, 'level': 'intermediate',
    'title': {'he': 'בינוני פעול', 'en': 'Written, closed, broken'},
    'objective': 'כתוב, סגור, פתוח, שבור, מלא. A shape that looks like an adjective, comes from '
                 'a verb, and answers "what state is it in" — and Hebrew reaches for it where '
                 'English uses a past participle.',
    'blocks': [
      {'kind': 'teach', 'title': 'The result, not the action',
       'body': 'From כתב you get <b>כָּתוּב</b>, "written — in the state of having been '
               'written". From סגר, <b>סגור</b>. From שבר, <b>שבור</b>. It agrees like an '
               'adjective — כתובה, כתובים — and it is NOT the passive verb: '
               '<b>הדלת נסגרה</b> is "the door was closed (something closed it)"; '
               '<b>הדלת סגורה</b> is "the door is closed (that is its state)". Israelis use the '
               'second far more often, and using the first for it sounds like a news report.',
       'examples': [
         {'he': 'החנות סגורה בשבת.', 'en': 'The shop is closed on Saturday.'},
         {'he': 'מה כתוב שם?', 'en': 'What does it say there?'},
         {'he': 'הכוס שבורה, אל תיגע.', 'en': 'The glass is broken, don’t touch it.'},
         {'he': 'אני עסוק עד שלוש.', 'en': 'I’m busy until three.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'כתוב', 'en': 'written', 'pos': 'adj'},
         {'he': 'סגור', 'en': 'closed, shut', 'pos': 'adj'},
         {'he': 'פתוח', 'en': 'open', 'pos': 'adj'},
         {'he': 'שבור', 'en': 'broken', 'pos': 'adj'},
         {'he': 'מלא', 'en': 'full', 'pos': 'adj'},
         {'he': 'ריק', 'en': 'empty', 'pos': 'adj'},
         {'he': 'עסוק', 'en': 'busy', 'pos': 'adj'},
         {'he': 'מוכן', 'en': 'ready', 'pos': 'adj'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the participle, agreeing with the noun.',
       'example': {'q': 'החנות ___ בשבת. — closed', 'a': 'סגורה'},
       'items': [
         {'q': 'החלון ___, נכנס קר.', 'a': ['פתוח'], 'en': 'The window is open, cold is getting in.'},
         {'q': 'הכוסות ___, זרוק אותן.', 'a': ['שבורות'], 'en': 'The glasses are broken, throw them out.'},
         {'q': 'מה ___ במכתב?', 'a': ['כתוב'], 'en': 'What does it say in the letter?'},
         {'q': 'האוטובוס היה ___ לגמרי.', 'a': ['מלא'], 'en': 'The bus was completely full.'},
         {'q': 'האוכל ___, בואו לאכול.', 'a': ['מוכן'], 'en': 'The food is ready, come and eat.'},
       ]},
      {'kind': 'choose', 'title': 'מצב או פעולה?', 'en': 'State or action?',
       'instructions': 'One describes how things ARE; the other says something happened.',
       'items': [
         {'q': 'The shop is shut right now.', 'options': ['החנות סגורה', 'החנות נסגרה', 'החנות סוגרת'],
          'a': 'החנות סגורה', 'en': 'A state — the participle.'},
         {'q': 'The shop closed down last year.', 'options': ['החנות נסגרה', 'החנות סגורה', 'החנות סוגר'],
          'a': 'החנות נסגרה', 'en': 'An event — the passive verb.'},
         {'q': 'It says here that…', 'options': ['כתוב פה ש', 'נכתב פה ש', 'כותבים פה ש'],
          'a': 'כתוב פה ש', 'en': 'The text is in a written state; nobody is writing now.'},
       ]},
      {'kind': 'slang', 'he': 'סגור עליי', 'literal': '“closed on me”',
       'meaning': 'I’ve got it covered / it’s sorted.',
       'when': 'The participle doing everyday work again. Someone asks whether the thing is '
               'handled and סגור עליי means "leave it with me". סגור? on its own asks the same '
               'question back.',
       'examples': [{'he': 'הכל סגור עליי, אל תדאג.', 'en': 'I’ve got it all covered, don’t worry.'},
                    {'he': 'אז סגור? — סגור.', 'en': 'So we’re set? — We’re set.'}]},
    ],
  },
  {
    'id': 'he-56', 'n': 56, 'level': 'beginner',
    'title': {'he': 'מספרים: זכר ונקבה', 'en': 'Numbers have a gender'},
    'objective': 'שלוש ילדות but שלושה ילדים. Hebrew numbers agree with what they count, and — '
                 'the part everyone gets backwards — the form that LOOKS feminine is the one '
                 'used with masculine nouns.',
    'blocks': [
      {'kind': 'teach', 'title': 'The ה goes on the masculine one',
       'body': 'Counting feminine nouns: <b>אחת, שתיים, שלוש, ארבע, חמש</b>. Counting masculine '
               'nouns: <b>אחד, שניים, שלושה, ארבעה, חמישה</b> — with the ־ָה that everywhere '
               'else in the language marks the feminine. It is genuinely the wrong way round, '
               'and there is no trick: <b>שלוש בנות</b>, <b>שלושה בנים</b>. Counting on your '
               'fingers or reading a phone number, use the feminine set — that is the neutral '
               'one, which is why times are שלוש and not שלושה.',
       'examples': [
         {'he': 'יש לי שלוש אחיות ושני אחים.', 'en': 'I have three sisters and two brothers.'},
         {'he': 'קניתי ארבעה כרטיסים.', 'en': 'I bought four tickets.'},
         {'he': 'ניפגש בשלוש.', 'en': 'We’ll meet at three.'},
         {'he': 'חמש דקות ואני מגיע.', 'en': 'Five minutes and I’m there.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'שתיים', 'en': 'two (f.)', 'pos': 'other'},
         {'he': 'שלוש', 'en': 'three (f.)', 'pos': 'other'},
         {'he': 'ארבע', 'en': 'four (f.)', 'pos': 'other'},
         {'he': 'חמש', 'en': 'five (f.)', 'pos': 'other'},
         {'he': 'שלושה', 'en': 'three (m.)', 'pos': 'other'},
         {'he': 'ארבעה', 'en': 'four (m.)', 'pos': 'other'},
         {'he': 'חצי', 'en': 'half', 'pos': 'noun'},
         {'he': 'רבע', 'en': 'quarter', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'בחרו את המספר', 'en': 'Choose the number',
       'instructions': 'Look at the noun, not at the number.',
       'items': [
         {'q': '___ ילדים במשפחה.', 'options': ['שלושה', 'שלוש', 'שליש'], 'a': 'שלושה',
          'en': 'Three children — ילדים is masculine, so the number takes ־ה.'},
         {'q': '___ בנות בכיתה.', 'options': ['ארבע', 'ארבעה', 'ארבעת'], 'a': 'ארבע',
          'en': 'Four girls — בנות is feminine, so the number has no ending.'},
         {'q': 'קניתי ___ כרטיסים.', 'options': ['חמישה', 'חמש', 'חמישית'], 'a': 'חמישה',
          'en': 'Five tickets — כרטיסים is masculine.'},
         {'q': 'חיכיתי ___ שעות.', 'options': ['שלוש', 'שלושה', 'שליש'], 'a': 'שלוש',
          'en': 'Three hours — שעות is feminine.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the number in the right gender.',
       'example': {'q': 'יש לי ___ אחיות. — three', 'a': 'שלוש'},
       'items': [
         {'q': 'יש לו ___ אחים.', 'a': ['שני', 'שניים'], 'en': 'He has two brothers.'},
         {'q': 'הזמנתי ___ מנות.', 'a': ['ארבע'], 'en': 'I ordered four dishes.'},
         {'q': 'ניפגש ב___ וחצי.', 'a': ['שלוש'], 'en': 'We’ll meet at half past three.'},
         {'q': 'עברו ___ ימים.', 'a': ['חמישה'], 'en': 'Five days went by.'},
         {'q': 'תן לי ___ דקות.', 'a': ['חמש'], 'en': 'Give me five minutes.'},
       ]},
      {'kind': 'slang', 'he': 'רגע אחד', 'literal': '“one moment”',
       'meaning': 'Hang on.',
       'when': 'רגע on its own is the everyday "wait". רגע! with force is "hold on a second" and '
               'stops a conversation dead. Israelis say it a great deal, and it is not rude.',
       'examples': [{'he': 'רגע, לא הבנתי.', 'en': 'Hang on, I didn’t follow.'},
                    {'he': 'שנייה אחת ואני איתך.', 'en': 'One second and I’m with you.'}]},
    ],
  },
  {
    'id': 'he-57', 'n': 57, 'level': 'beginner',
    'title': {'he': 'ה׳ הידיעה ואת', 'en': 'The, and the word before it'},
    'objective': 'Hebrew has no "a" at all, one letter for "the", and a small word — את — that '
                 'appears ONLY when the object is definite. That last rule has no English '
                 'equivalent and it is worth an hour.',
    'blocks': [
      {'kind': 'teach', 'title': 'את comes with ה, or not at all',
       'body': 'There is no indefinite article: <b>ספר</b> is "a book". "The book" is '
               '<b>הספר</b>, one letter stuck on the front. Now the rule that catches everyone: '
               'a DEFINITE direct object takes <b>את</b> in front of it, and an indefinite one '
               'takes nothing. קראתי <b>ספר</b> — I read a book. קראתי <b>את הספר</b> — I read '
               'the book. A name is already definite, so it takes את too: ראיתי <b>את</b> דנה. '
               'And the adjective must carry the ה as well: הספר <b>ה</b>חדש.',
       'examples': [
         {'he': 'קניתי ספר חדש.', 'en': 'I bought a new book.'},
         {'he': 'קראתי את הספר החדש.', 'en': 'I read the new book.'},
         {'he': 'ראיתי את דנה ברחוב.', 'en': 'I saw Dana in the street.'},
         {'he': 'אני מחפש דירה בעיר.', 'en': 'I’m looking for a flat in the city.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ספר', 'en': 'book', 'pos': 'noun'},
         {'he': 'מכתב', 'en': 'letter', 'pos': 'noun'},
         {'he': 'מפתח', 'en': 'key', 'pos': 'noun'},
         {'he': 'חדר', 'en': 'room', 'pos': 'noun'},
         {'he': 'חדש', 'en': 'new', 'pos': 'adj'},
         {'he': 'ישן', 'en': 'old (of things)', 'pos': 'adj'},
         {'he': 'לחפש', 'en': 'to look for', 'pos': 'verb'},
         {'he': 'למצוא', 'en': 'to find', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'עם את או בלי?', 'en': 'With את or without?',
       'instructions': 'Is the object definite?',
       'items': [
         {'q': 'קניתי ___ חדש.', 'options': ['ספר', 'את ספר', 'את הספר'], 'a': 'ספר',
          'en': 'I bought a new book — indefinite, so no את.'},
         {'q': 'קראתי ___ שנתת לי.', 'options': ['את הספר', 'ספר', 'את ספר'], 'a': 'את הספר',
          'en': 'I read the book you gave me — definite, so את.'},
         {'q': 'ראיתי ___ ברחוב.', 'options': ['את דנה', 'דנה', 'את הדנה'], 'a': 'את דנה',
          'en': 'A name is definite already — את, but never ה.'},
         {'q': 'אני מחפש ___ בעיר.', 'options': ['דירה', 'את דירה', 'את הדירה'], 'a': 'דירה',
          'en': 'Looking for a flat, any flat.'},
       ]},
      {'kind': 'transform', 'title': 'מסתמי למיודע', 'en': 'Indefinite to definite',
       'instructions': 'Make the object definite. Remember what has to appear in front of it — '
                       'and on the adjective.',
       'example': {'from': 'קראתי ספר.', 'to': 'קראתי את הספר.'},
       'items': [
         {'from': 'מצאתי מפתח.', 'to': ['מצאתי את המפתח.', 'מצאתי את המפתח'], 'en': 'I found a key.'},
         {'from': 'ראיתי סרט טוב.', 'to': ['ראיתי את הסרט הטוב.', 'ראיתי את הסרט הטוב'],
          'en': 'I saw a good film.'},
         {'from': 'הוא כתב מכתב.', 'to': ['הוא כתב את המכתב.', 'הוא כתב את המכתב'],
          'en': 'He wrote a letter.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Why is הבית הגדול right and הבית גדול different?',
          'options': ['The second is a sentence: “the house is big”',
                      'The second is wrong', 'They mean the same thing'],
          'a': 'The second is a sentence: “the house is big”',
          'why': 'Hebrew has no “is”. Repeating the ה makes it a phrase; dropping it makes it a '
                 'statement. One letter is the whole difference.'},
         {'q': 'Does את ever appear before an indefinite object?',
          'options': ['No, never', 'Sometimes, for emphasis', 'Only in writing'],
          'a': 'No, never',
          'why': 'It is a completely reliable rule, which makes it a good test of whether you '
                 'have understood the object of your own sentence.'},
       ]},
      {'kind': 'slang', 'he': 'את זה', 'literal': '“this (object)”',
       'meaning': 'This one / that.',
       'when': 'זה is definite by itself, so pointing at something and asking for it is '
               'את זה, never just זה. תן לי את זה is the most-said three words in any Israeli '
               'market.',
       'examples': [{'he': 'תן לי את זה, בבקשה.', 'en': 'Give me that one, please.'},
                    {'he': 'לא ראיתי את זה קודם.', 'en': 'I didn’t see that before.'}]},
    ],
  },
  {
    'id': 'he-58', 'n': 58, 'level': 'intermediate',
    'title': {'he': 'תיקונים בבית', 'en': 'When something breaks'},
    'objective': 'Say what is broken, describe it well enough over the phone, and agree a time. '
                 'A closed vocabulary of about thirty words that nobody teaches you until you '
                 'are standing in water.',
    'blocks': [
      {'kind': 'teach', 'title': 'Broken is a state; breaking is a verb',
       'body': 'The participle from the last unit does most of the work: <b>מקולקל</b> (out of '
               'order), <b>שבור</b>, <b>סתום</b> (blocked). The verb for a thing going wrong is '
               '<b>התקלקל</b>. You call a <b>בעל מקצוע</b> — a tradesman — or a '
               '<b>טכנאי</b> for anything with electricity in it, and what you are reporting is '
               'a <b>תקלה</b>. To fix is <b>לתקן</b>, and the noun is <b>תיקון</b>.',
       'examples': [
         {'he': 'המקרר התקלקל, אפשר לשלוח טכנאי?', 'en': 'The fridge has broken, can you send a technician?'},
         {'he': 'יש דליפה מתחת לכיור.', 'en': 'There’s a leak under the sink.'},
         {'he': 'הברז לא נסגר עד הסוף.', 'en': 'The tap doesn’t close all the way.'},
         {'he': 'כמה יעלה התיקון?', 'en': 'How much will the repair cost?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לתקן', 'en': 'to repair', 'pos': 'verb'},
         {'he': 'תיקון', 'en': 'a repair', 'pos': 'noun'},
         {'he': 'תקלה', 'en': 'a fault, a breakdown', 'pos': 'noun'},
         {'he': 'טכנאי', 'en': 'technician', 'pos': 'noun'},
         {'he': 'ברז', 'en': 'tap', 'pos': 'noun'},
         {'he': 'צינור', 'en': 'pipe', 'pos': 'noun'},
         {'he': 'חשמל', 'en': 'electricity', 'pos': 'noun'},
         {'he': 'דליפה', 'en': 'a leak', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'המקרר ___, הוא לא עובד. — has broken', 'a': 'התקלקל'},
       'items': [
         {'q': 'יש ___ מתחת לכיור.', 'a': ['דליפה'], 'en': 'There’s a leak under the sink.'},
         {'q': 'צריך לקרוא ל___ בשביל החשמל.', 'a': ['טכנאי'], 'en': 'We need to call a technician for the electricity.'},
         {'q': 'ה___ לא נסגר עד הסוף.', 'a': ['ברז'], 'en': 'The tap doesn’t close all the way.'},
         {'q': 'כמה יעלה ה___?', 'a': ['תיקון'], 'en': 'How much will the repair cost?'},
         {'q': 'אפשר ___ את זה או שצריך חדש?', 'a': ['לתקן'], 'en': 'Can it be fixed or do we need a new one?'},
       ]},
      {'kind': 'choose', 'title': 'מה אומרים בטלפון?', 'en': 'What do you say on the phone?',
       'instructions': 'Pick the line that gets you help fastest.',
       'items': [
         {'q': 'Reporting the problem in one sentence.',
          'options': ['שלום, יש לי דליפה במטבח', 'המים', 'זה לא טוב'],
          'a': 'שלום, יש לי דליפה במטבח', 'en': 'Where, and what.'},
         {'q': 'Asking when they can come.',
          'options': ['מתי אפשר להגיע?', 'בוא עכשיו', 'אני מחכה'],
          'a': 'מתי אפשר להגיע?', 'en': 'The impersonal אפשר is the polite frame.'},
         {'q': 'Asking about the price before they start.',
          'options': ['כמה זה עולה בערך?', 'זה יקר?', 'אני לא משלם הרבה'],
          'a': 'כמה זה עולה בערך?', 'en': 'בערך — “roughly” — is what makes it askable.'},
       ]},
      {'kind': 'slang', 'he': 'יהיה בסדר', 'literal': '“it will be fine”',
       'meaning': 'It’ll work out.',
       'when': 'Said by the tradesman, the doctor, the clerk and your neighbour, often before '
               'anyone has looked at the problem. It is the national reassurance and it is '
               'meant sincerely — which does not mean it is information.',
       'examples': [{'he': 'אל תדאג, יהיה בסדר.', 'en': 'Don’t worry, it’ll be fine.'},
                    {'he': 'יהיה בסדר, אני מטפל בזה.', 'en': 'It’ll be fine, I’m dealing with it.'}]},
    ],
  },
  {
    'id': 'he-59', 'n': 59, 'level': 'intermediate',
    'title': {'he': 'נהיגה ותחבורה', 'en': 'Driving'},
    'objective': 'Roads, junctions, parking and the fine that follows. Getting around by bus is '
                 'one vocabulary; being the one driving is another.',
    'blocks': [
      {'kind': 'teach', 'title': 'The words on the road',
       'body': 'A <b>רמזור</b> is a traffic light, a <b>צומת</b> a junction, a <b>תמרור</b> a '
               'road sign. Traffic is a <b>פקק</b> — literally a cork — and it is the single '
               'most discussed object in the country. Parking is <b>חניה</b> and to park is '
               '<b>לחנות</b>, which is the same root; a parking ticket is a <b>דוח</b>, said '
               '"doh-akh", and a fine in general is a <b>קנס</b>.',
       'examples': [
         {'he': 'יש פקק ענקי בכניסה לעיר.', 'en': 'There’s a huge jam at the entrance to the city.'},
         {'he': 'תפנה ימינה ברמזור הבא.', 'en': 'Turn right at the next traffic light.'},
         {'he': 'חניתי פה חמש דקות וקיבלתי דוח.', 'en': 'I parked here for five minutes and got a ticket.'},
         {'he': 'שכחתי את הרישיון בבית.', 'en': 'I left my licence at home.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'נהג', 'en': 'driver', 'pos': 'noun'},
         {'he': 'רישיון', 'en': 'licence', 'pos': 'noun'},
         {'he': 'רמזור', 'en': 'traffic light', 'pos': 'noun'},
         {'he': 'צומת', 'en': 'junction', 'pos': 'noun'},
         {'he': 'תמרור', 'en': 'road sign', 'pos': 'noun'},
         {'he': 'פקק', 'en': 'traffic jam; a cork', 'pos': 'noun'},
         {'he': 'קנס', 'en': 'fine', 'pos': 'noun'},
         {'he': 'דלק', 'en': 'fuel', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'יש ___ בכניסה לעיר. — a traffic jam', 'a': 'פקק'},
       'items': [
         {'q': 'תפנה שמאלה ב___ הבא.', 'a': ['רמזור', 'צומת'], 'en': 'Turn left at the next light / junction.'},
         {'q': 'שכחתי את ה___ בבית.', 'a': ['רישיון'], 'en': 'I left my licence at home.'},
         {'q': 'קיבלתי ___ על חניה.', 'a': ['קנס', 'דוח'], 'en': 'I got a fine for parking.'},
         {'q': 'צריך למלא ___ לפני הנסיעה.', 'a': ['דלק'], 'en': 'We need to fill up before the drive.'},
         {'q': 'אין ___ ברחוב הזה אף פעם.', 'a': ['חניה'], 'en': 'There’s never any parking on this street.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['תפנה', 'ימינה', 'ברמזור', 'הבא'], 'a': 'תפנה ימינה ברמזור הבא',
          'en': 'Turn right at the next traffic light.'},
         {'words': ['חניתי', 'פה', 'וקיבלתי', 'דוח'], 'a': 'חניתי פה וקיבלתי דוח',
          'en': 'I parked here and got a ticket.'},
         {'words': ['יש', 'פקק', 'גדול', 'בכביש', 'הראשי'], 'a': 'יש פקק גדול בכביש הראשי',
          'en': 'There’s a big jam on the main road.'},
       ]},
      {'kind': 'slang', 'he': 'תעוף לי מהעיניים', 'literal': '“fly out of my eyes”',
       'meaning': 'Get out of my way — road-rage register.',
       'when': 'Included because you WILL hear it through a window, not because you should say '
               'it. Israeli driving has a loud vocabulary, and a learner who does not recognise '
               'it thinks something worse is happening than is.',
       'examples': [{'he': 'נו כבר, תזוז!', 'en': 'Come on, move!'},
                    {'he': 'הוא נכנס לי בפנים.', 'en': 'He cut right in front of me.'}]},
    ],
  },
  {
    'id': 'he-60', 'n': 60, 'level': 'beginner',
    'title': {'he': 'במטבח', 'en': 'In the kitchen'},
    'objective': 'Reading a recipe and saying what you did with the food. Cooking verbs are a '
                 'tight set, and they are where the imperative you learned finally gets used '
                 'for something other than orders.',
    'blocks': [
      {'kind': 'teach', 'title': 'A recipe is a list of imperatives',
       'body': 'A Hebrew recipe talks to you in the plural imperative: <b>חתכו</b>, '
               '<b>הוסיפו</b>, <b>ערבבו</b>, <b>אפו</b> — cut, add, mix, bake. That is the same '
               'form as תלכו and תשבו, just written without the ת, which is the written-register '
               'imperative. Recognising it turns every food package into reading practice.',
       'examples': [
         {'he': 'תחתוך את הבצל דק.', 'en': 'Chop the onion finely.'},
         {'he': 'שמים את הסיר על אש קטנה.', 'en': 'You put the pot on a low flame.'},
         {'he': 'אני מבשל ואתה עורך שולחן.', 'en': 'I’ll cook and you set the table.'},
         {'he': 'האוכל בתנור, עוד עשרים דקות.', 'en': 'The food’s in the oven, twenty more minutes.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'מטבח', 'en': 'kitchen', 'pos': 'noun'},
         {'he': 'סיר', 'en': 'pot', 'pos': 'noun'},
         {'he': 'מחבת', 'en': 'frying pan', 'pos': 'noun'},
         {'he': 'תנור', 'en': 'oven', 'pos': 'noun'},
         {'he': 'מקרר', 'en': 'fridge', 'pos': 'noun'},
         {'he': 'לבשל', 'en': 'to cook', 'pos': 'verb'},
         {'he': 'לחתוך', 'en': 'to cut', 'pos': 'verb'},
         {'he': 'לטגן', 'en': 'to fry', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'שמתי את הסיר על ה___. — the flame', 'a': 'אש'},
       'items': [
         {'q': 'תוציא את החלב מה___.', 'a': ['מקרר'], 'en': 'Take the milk out of the fridge.'},
         {'q': 'העוגה בתוך ה___ כבר שעה.', 'a': ['תנור'], 'en': 'The cake has been in the oven an hour.'},
         {'q': 'צריך ___ את הבצל דק.', 'a': ['לחתוך'], 'en': 'The onion needs chopping finely.'},
         {'q': 'אני ___ אורז עם ירקות.', 'a': ['מבשל', 'מבשלת'], 'en': 'I’m cooking rice with vegetables.'},
         {'q': 'שים את הביצים ב___.', 'a': ['מחבת'], 'en': 'Put the eggs in the frying pan.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'לבשל ארוחה', 'en': 'to cook a meal'},
         {'he': 'לחתוך ירקות', 'en': 'to chop vegetables'},
         {'he': 'לטגן ביצה', 'en': 'to fry an egg'},
         {'he': 'לשים בתנור', 'en': 'to put in the oven'},
         {'he': 'לערוך שולחן', 'en': 'to lay the table'},
         {'he': 'לשטוף כלים', 'en': 'to wash up'},
       ]},
      {'kind': 'slang', 'he': 'על האש', 'literal': '“on the fire”',
       'meaning': 'A barbecue.',
       'when': 'Not a description — a noun. עושים על האש is "we’re having a barbecue", and on '
               'Independence Day the whole country is doing it in the same park at the same '
               'hour.',
       'examples': [{'he': 'עושים על האש בשבת.', 'en': 'We’re doing a barbecue on Saturday.'},
                    {'he': 'הבשר כבר על האש.', 'en': 'The meat’s already on the grill.'}]},
    ],
  },
  {
    'id': 'he-61', 'n': 61, 'level': 'intermediate',
    'title': {'he': 'לימודים', 'en': 'Studying'},
    'objective': 'Courses, lectures, exams and marks. Also the one place where the written '
                 'register you met in the last phase is not optional — an academic email is not '
                 'a text message.',
    'blocks': [
      {'kind': 'teach', 'title': 'The university has its own nouns',
       'body': 'You take a <b>קורס</b>, go to a <b>הרצאה</b>, sit a <b>מבחן</b> and get a '
               '<b>ציון</b>. You register with <b>להירשם ל</b>, you hand in with '
               '<b>להגיש</b>, and a degree is a <b>תואר</b>. Note the pair '
               '<b>ללמוד</b> (to study, what a student does) against <b>ללמד</b> (to teach) — '
               'one letter apart in writing and completely different in speech.',
       'examples': [
         {'he': 'נרשמתי לקורס בעברית.', 'en': 'I registered for a Hebrew course.'},
         {'he': 'ההרצאה מתחילה בעשר.', 'en': 'The lecture starts at ten.'},
         {'he': 'קיבלתי ציון טוב במבחן.', 'en': 'I got a good mark in the exam.'},
         {'he': 'צריך להגיש את העבודה עד חמישי.', 'en': 'The assignment has to be handed in by Thursday.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אוניברסיטה', 'en': 'university', 'pos': 'noun'},
         {'he': 'סטודנט', 'en': 'student', 'pos': 'noun'},
         {'he': 'קורס', 'en': 'course', 'pos': 'noun'},
         {'he': 'הרצאה', 'en': 'lecture', 'pos': 'noun'},
         {'he': 'מבחן', 'en': 'exam', 'pos': 'noun'},
         {'he': 'ציון', 'en': 'mark, grade', 'pos': 'noun'},
         {'he': 'תואר', 'en': 'degree; also an adjective', 'pos': 'noun'},
         {'he': 'ללמד', 'en': 'to teach', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'נרשמתי ל___ בעברית. — a course', 'a': 'קורס'},
       'items': [
         {'q': 'ה___ מתחילה בעשר בבוקר.', 'a': ['הרצאה'], 'en': 'The lecture starts at ten in the morning.'},
         {'q': 'קיבלתי ___ טוב במבחן.', 'a': ['ציון'], 'en': 'I got a good mark in the exam.'},
         {'q': 'היא ___ מתמטיקה בבית ספר.', 'a': ['מלמדת'], 'en': 'She teaches maths at a school.'},
         {'q': 'אני ___ עברית כבר שנתיים.', 'a': ['לומד', 'לומדת'], 'en': 'I’ve been studying Hebrew for two years.'},
         {'q': 'סיימתי ___ ראשון בהיסטוריה.', 'a': ['תואר'], 'en': 'I finished a first degree in history.'},
       ]},
      {'kind': 'choose', 'title': 'ללמוד או ללמד?', 'en': 'ללמוד or ללמד?',
       'instructions': 'One is what a student does; the other is what a teacher does.',
       'items': [
         {'q': 'אני ___ עברית באוניברסיטה.', 'options': ['לומד', 'מלמד', 'לימד'], 'a': 'לומד',
          'en': 'I study Hebrew at the university.'},
         {'q': 'היא ___ אנגלית בבית ספר.', 'options': ['מלמדת', 'לומדת', 'למדה'], 'a': 'מלמדת',
          'en': 'She teaches English at a school.'},
         {'q': 'הוא ___ אותי לנהוג.', 'options': ['לימד', 'למד', 'לומד'], 'a': 'לימד',
          'en': 'He taught me to drive.'},
       ]},
      {'kind': 'slang', 'he': 'לעשות סמינר', 'literal': '“to do a seminar”',
       'meaning': 'To make a whole production out of something.',
       'when': 'Student slang that escaped into general use. Anyone turning a simple decision '
               'into a research project is עושה מזה סמינר, and it is said with affection and '
               'impatience in equal measure.',
       'examples': [{'he': 'אל תעשה מזה סמינר.', 'en': 'Don’t make a whole production of it.'},
                    {'he': 'הוא עושה סמינר על כל קפה.', 'en': 'He turns every coffee into a research project.'}]},
    ],
  },
  {
    'id': 'he-62', 'n': 62, 'level': 'beginner',
    'title': {'he': 'טלפון ומחשב', 'en': 'Phones and computers'},
    'objective': 'The words you need before anything else works: wifi, password, screen, '
                 'download. Half of them are English wearing Hebrew grammar, which is its own '
                 'lesson.',
    'blocks': [
      {'kind': 'teach', 'title': 'Borrowed words take Hebrew endings',
       'body': 'Hebrew borrows freely and then conjugates: <b>לסמס</b> (to text), '
               '<b>לגגל</b> (to google), <b>לפרמט</b>. A borrowed noun takes a Hebrew plural — '
               'אפליקציות, מיילים. But the core words are native: a screen is a <b>מסך</b>, a '
               'password a <b>סיסמה</b>, and to save is <b>לשמור</b> — the same verb as guarding '
               'a child.',
       'examples': [
         {'he': 'שכחתי את הסיסמה שלי.', 'en': 'I’ve forgotten my password.'},
         {'he': 'אין פה אינטרנט בכלל.', 'en': 'There’s no internet here at all.'},
         {'he': 'תוריד את האפליקציה, זה חינם.', 'en': 'Download the app, it’s free.'},
         {'he': 'הסוללה שלי נגמרת.', 'en': 'My battery is running out.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'מחשב', 'en': 'computer', 'pos': 'noun'},
         {'he': 'מסך', 'en': 'screen', 'pos': 'noun'},
         {'he': 'סיסמה', 'en': 'password', 'pos': 'noun'},
         {'he': 'אינטרנט', 'en': 'internet', 'pos': 'noun'},
         {'he': 'אפליקציה', 'en': 'app', 'pos': 'noun'},
         {'he': 'סוללה', 'en': 'battery', 'pos': 'noun'},
         {'he': 'להוריד', 'en': 'to download; to take down', 'pos': 'verb'},
         {'he': 'לשמור', 'en': 'to save; to keep', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'שכחתי את ה___ שלי. — password', 'a': 'סיסמה'},
       'items': [
         {'q': 'אין פה ___ בכלל.', 'a': ['אינטרנט'], 'en': 'There’s no internet here at all.'},
         {'q': 'ה___ שלי נגמרת, יש מטען?', 'a': ['סוללה'], 'en': 'My battery’s dying, is there a charger?'},
         {'q': 'תוריד את ה___, זה חינם.', 'a': ['אפליקציה'], 'en': 'Download the app, it’s free.'},
         {'q': 'ה___ של המחשב לא עובד.', 'a': ['מסך'], 'en': 'The computer screen isn’t working.'},
         {'q': 'אל תשכח ___ את הקובץ.', 'a': ['לשמור'], 'en': 'Don’t forget to save the file.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'יש לך וייפיי?', 'en': 'Do you have wifi?'},
         {'he': 'מה הסיסמה?', 'en': 'What’s the password?'},
         {'he': 'זה לא עובד', 'en': 'It’s not working'},
         {'he': 'תשלח לי בוואטסאפ', 'en': 'Send it to me on WhatsApp'},
         {'he': 'הסוללה נגמרה', 'en': 'The battery’s dead'},
         {'he': 'יש לך מטען?', 'en': 'Have you got a charger?'},
       ]},
      {'kind': 'slang', 'he': 'תסמס לי', 'literal': 'from SMS, verbed',
       'meaning': 'Text me.',
       'when': 'A three-letter English abbreviation turned into a full Hebrew verb — סימסתי, '
               'תסמס, מסמס. Hebrew does this to anything it borrows, and it is why a new word '
               'stops sounding foreign within a year.',
       'examples': [{'he': 'תסמס לי כשאתה מגיע.', 'en': 'Text me when you get here.'},
                    {'he': 'גיגלתי את זה אתמול.', 'en': 'I googled it yesterday.'}]},
    ],
  },
  {
    'id': 'he-63', 'n': 63, 'level': 'intermediate',
    'title': {'he': 'אירוח', 'en': 'Having people over'},
    'objective': 'Invite, arrive, refuse food twice and accept on the third offer. Israeli '
                 'hospitality has a script, and the phrases are fixed.',
    'blocks': [
      {'kind': 'teach', 'title': 'The offering is not a question',
       'body': 'A host says <b>תרגישו בבית</b> ("feel at home") and then offers food repeatedly. '
               'Declining once is not taken as a decision — <b>באמת, תודה</b> is understood as '
               'politeness, and the offer will come again. <b>כיבוד</b> is the word for what is '
               'put out; there is no English equivalent that covers cake, fruit, nuts and '
               'coffee at once. Guests bring something small, and the host says '
               '<b>לא היה צריך</b> — "you shouldn’t have" — every time.',
       'examples': [
         {'he': 'תיכנסו, תרגישו בבית.', 'en': 'Come in, make yourselves at home.'},
         {'he': 'הבאנו משהו קטן. — לא היה צריך!', 'en': 'We brought something small. — You shouldn’t have!'},
         {'he': 'תשתה משהו? קפה? מיץ?', 'en': 'Will you have something to drink? Coffee? Juice?'},
         {'he': 'תודה על האירוח, היה נעים.', 'en': 'Thanks for having us, it was lovely.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אורח', 'en': 'guest', 'pos': 'noun'},
         {'he': 'לארח', 'en': 'to host', 'pos': 'verb'},
         {'he': 'ביקור', 'en': 'a visit', 'pos': 'noun'},
         {'he': 'כיבוד', 'en': 'refreshments put out for guests', 'pos': 'noun'},
         {'he': 'סלון', 'en': 'living room', 'pos': 'noun'},
         {'he': 'להיכנס', 'en': 'to come in — להיכנס ל', 'pos': 'verb'},
         {'he': 'להזמין', 'en': 'to invite; to order', 'pos': 'verb'},
         {'he': 'נעים', 'en': 'pleasant', 'pos': 'adj'},
       ]},
      {'kind': 'choose', 'title': 'מה עונים?', 'en': 'What do you say?',
       'instructions': 'Pick the reply that fits the script.',
       'items': [
         {'q': 'The host says תרגישו בבית.',
          'options': ['תודה, איזה יפה אצלכם', 'כן', 'אני לא בבית'],
          'a': 'תודה, איזה יפה אצלכם', 'en': 'Compliment the place — it is the expected reply.'},
         {'q': 'You bring flowers and the host says לא היה צריך.',
          'options': ['מה פתאום, זה כלום', 'בבקשה', 'אני יודע'],
          'a': 'מה פתאום, זה כלום', 'en': '“Nonsense, it’s nothing” — the ritual has two halves.'},
         {'q': 'You are offered coffee for the third time and you do want it.',
          'options': ['טוב, אם כבר', 'לא, תודה', 'אמרתי לא'],
          'a': 'טוב, אם כבר', 'en': '“Alright, since you insist” — accepting on the third offer.'},
         {'q': 'Leaving after a good evening.',
          'options': ['תודה על האירוח', 'אני הולך', 'זהו'],
          'a': 'תודה על האירוח', 'en': 'The fixed closing phrase.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'תודה על ה___. — the hospitality', 'a': 'אירוח'},
       'items': [
         {'q': 'תיכנסו, ___ בבית.', 'a': ['תרגישו'], 'en': 'Come in, make yourselves at home.'},
         {'q': 'שמנו ___ על השולחן.', 'a': ['כיבוד'], 'en': 'We put refreshments on the table.'},
         {'q': 'הם ___ אותנו לשבת.', 'a': ['הזמינו'], 'en': 'They invited us for Shabbat.'},
         {'q': 'ה___ שלנו נשארו עד מאוחר.', 'a': ['אורחים'], 'en': 'Our guests stayed late.'},
         {'q': 'היה מאוד ___, תודה.', 'a': ['נעים'], 'en': 'It was very pleasant, thank you.'},
       ]},
      {'kind': 'slang', 'he': 'מה פתאום', 'literal': '“what suddenly?”',
       'meaning': 'Nonsense / of course not / don’t mention it.',
       'when': 'A refusal of the premise rather than the request. Offered payment, מה פתאום '
               'means "absolutely not"; thanked, it means "it was nothing"; accused, it means '
               '"that is not what happened at all".',
       'examples': [{'he': 'מה פתאום, אני משלם.', 'en': 'Don’t be silly, I’m paying.'},
                    {'he': 'מה פתאום כעסתי?', 'en': 'What do you mean I was angry?'}]},
    ],
  },
  {
    'id': 'he-64', 'n': 64, 'level': 'advanced',
    'title': {'he': 'שיחת חולין', 'en': 'Small talk with strangers'},
    'objective': 'The taxi, the queue, the lift. Israelis start conversations with strangers '
                 'readily and about things other cultures consider private — and knowing the '
                 'moves means you can hold your end of one.',
    'blocks': [
      {'kind': 'teach', 'title': 'The opening is a complaint',
       'body': 'Small talk here rarely starts with the weather in the English way; it starts '
               'with something shared and slightly annoying — the traffic, the prices, the '
               'queue, the government. <b>מה זה החום הזה</b>, <b>ראית מה קורה בכבישים</b>, '
               '<b>נו, מה יהיה</b>. Personal questions follow fast and are not rude: where are '
               'you from, are you married, how much do you pay in rent. The correct move is to '
               'answer briefly and ask back.',
       'examples': [
         {'he': 'נו, מה יהיה עם המדינה הזאת?', 'en': 'So — what’s going to become of this country?'},
         {'he': 'מאיפה אתה במקור?', 'en': 'Where are you originally from?'},
         {'he': 'ראית מה קורה בכבישים היום?', 'en': 'Did you see what’s going on on the roads today?'},
         {'he': 'תגיד, כמה זמן אתה פה?', 'en': 'Tell me, how long have you been here?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'מונית', 'en': 'taxi', 'pos': 'noun'},
         {'he': 'מקור', 'en': 'origin, source', 'pos': 'noun'},
         {'he': 'מדינה', 'en': 'country, state', 'pos': 'noun'},
         {'he': 'מצב', 'en': 'situation', 'pos': 'noun'},
         {'he': 'לשאול', 'en': 'to ask', 'pos': 'verb'},
         {'he': 'לענות', 'en': 'to answer', 'pos': 'verb'},
         {'he': 'להכיר', 'en': 'to know (a person), to be acquainted', 'pos': 'verb'},
         {'he': 'סקרן', 'en': 'curious', 'pos': 'adj'},
       ]},
      {'kind': 'choose', 'title': 'איך ממשיכים?', 'en': 'How do you keep it going?',
       'instructions': 'A stranger opens. Pick the reply that continues the conversation rather '
                       'than closing it.',
       'items': [
         {'q': 'מאיפה אתה במקור?',
          'options': ['מאנגליה, ואתה?', 'זה לא עניינך', 'למה אתה שואל?'],
          'a': 'מאנגליה, ואתה?', 'en': 'Answer short, ask back. That is the whole move.'},
         {'q': 'נו, מה יהיה?',
          'options': ['מה אפשר לעשות', 'אני לא יודע', 'שאלה טובה'],
          'a': 'מה אפשר לעשות', 'en': '“What can you do” — the standard shrug, and it is a reply.'},
         {'q': 'כמה זמן אתה בארץ?',
          'options': ['שלוש שנים, ואתה מפה?', 'מספיק', 'למה?'],
          'a': 'שלוש שנים, ואתה מפה?', 'en': 'Same shape again — brief, then a question back.'},
         {'q': 'איזה חום היום, נכון?',
          'options': ['נורא, ואומרים שיהיה גרוע יותר', 'כן', 'לא שמתי לב'],
          'a': 'נורא, ואומרים שיהיה גרוע יותר', 'en': 'Agree and escalate — that is how the complaint genre works.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['תגיד', 'כמה', 'זמן', 'אתה', 'גר', 'פה'], 'a': 'תגיד כמה זמן אתה גר פה',
          'en': 'Tell me, how long have you been living here?'},
         {'words': ['ראית', 'מה', 'קורה', 'בכבישים', 'היום'], 'a': 'ראית מה קורה בכבישים היום',
          'en': 'Did you see what’s going on on the roads today?'},
         {'words': ['אני', 'פה', 'כבר', 'שלוש', 'שנים'], 'a': 'אני פה כבר שלוש שנים',
          'en': 'I’ve been here three years now.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'A taxi driver asks how much rent you pay. What is happening?',
          'options': ['Ordinary small talk here', 'He is being rude', 'He wants to sell you a flat'],
          'a': 'Ordinary small talk here',
          'why': 'Money, rent and salary are far less private in Israeli conversation than in '
                 'English-speaking ones. A vague answer is fine; taking offence is the mistake.'},
         {'q': 'What does נו do at the start of a sentence?',
          'options': ['Signals “come on, out with it”', 'Means “no”', 'Is a greeting'],
          'a': 'Signals “come on, out with it”',
          'why': 'From Yiddish, and it carries impatience, invitation or resignation depending '
                 'entirely on the tone. נו? on its own is a complete question.'},
       ]},
      {'kind': 'slang', 'he': 'מה אפשר לעשות', 'literal': '“what can one do”',
       'meaning': 'What can you do. That’s life.',
       'when': 'The universal closing move of a complaint. It accepts the problem, ends the '
               'topic, and asks nothing of anyone — which is precisely why it is said fifty '
               'times a day.',
       'examples': [{'he': 'יקר, אבל מה אפשר לעשות.', 'en': 'It’s expensive, but what can you do.'},
                    {'he': 'ככה זה, מה לעשות.', 'en': 'That’s how it is, what can you do.'}]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
# UNITS 65-76. The five grammar units here are all the same KIND of gap: things Hebrew marks
# that English does not mark at all, so a learner never notices they are missing until a native
# speaker corrects them. A noun's gender when nothing on it says so. A plural that changes the
# word. A construct that changes it again in the plural. The rest are the parts of Israeli life
# that have their own vocabulary and are usually left to the learner to absorb by accident --
# including the one this app's own reader is most likely to be living through.
UNITS += [
  {
    'id': 'he-65', 'n': 65, 'level': 'intermediate',
    'title': {'he': 'גזרת ע״ו', 'en': 'The hollow verbs'},
    'objective': 'לקום, לשים, לבוא, לגור, לרוץ, לשיר. Their middle root letter is a vowel, so '
                 'the past has no vowel-changes at all and the present looks like nothing else '
                 'in the language.',
    'blocks': [
      {'kind': 'teach', 'title': 'Two letters and a long vowel',
       'body': 'These verbs have only two consonants you can hear: ק־ם, ש־ם, ב־א. The present '
               'is <b>קם, קמה, קמים, קמות</b> — no מ prefix, which is why they look wrong at '
               'first. The past is flat: <b>קמתי, קמת, קם, קמה, קמנו, קמו</b>. The future '
               'lengthens: <b>אקום, תקום, יקום</b>. Note that <b>גר</b> and <b>בא</b> are the '
               'same shape, which is why "I live in Tel Aviv" is אני גר and not אני מגור.',
       'examples': [
         {'he': 'אני קם בשש כל בוקר.', 'en': 'I get up at six every morning.'},
         {'he': 'שמתי את המפתחות על השולחן.', 'en': 'I put the keys on the table.'},
         {'he': 'הם גרים פה כבר עשר שנים.', 'en': 'They’ve lived here for ten years.'},
         {'he': 'מתי אתה בא?', 'en': 'When are you coming?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לקום', 'en': 'to get up', 'pos': 'verb'},
         {'he': 'לשים', 'en': 'to put', 'pos': 'verb'},
         {'he': 'לבוא', 'en': 'to come', 'pos': 'verb'},
         {'he': 'לגור', 'en': 'to live, to reside', 'pos': 'verb'},
         {'he': 'לרוץ', 'en': 'to run', 'pos': 'verb'},
         {'he': 'לשיר', 'en': 'to sing', 'pos': 'verb'},
         {'he': 'לטוס', 'en': 'to fly', 'pos': 'verb'},
         {'he': 'לזוז', 'en': 'to move', 'pos': 'verb'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'Some cells are printed, the rest you type.',
       'cols': ['שם פועל', 'הוא, הווה', 'אני, עבר', 'אני, עתיד'],
       'rows': [
         [{'g': 'לקום'}, {'g': 'קם'}, {'g': 'קמתי'}, {'g': 'אקום'}],
         [{'g': 'לשים'}, {'a': ['שם']}, {'a': ['שמתי']}, {'a': ['אשים']}],
         [{'g': 'לגור'}, {'a': ['גר']}, {'a': ['גרתי']}, {'a': ['אגור']}],
         [{'g': 'לרוץ'}, {'a': ['רץ']}, {'a': ['רצתי']}, {'a': ['ארוץ']}],
         [{'g': 'לטוס'}, {'a': ['טס']}, {'a': ['טסתי']}, {'a': ['אטוס']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל', 'en': 'Write the verb',
       'instructions': 'The infinitive is in brackets; write the form the sentence needs.',
       'example': {'q': 'אני ___ בשש כל בוקר. [לקום]', 'a': 'קם'},
       'items': [
         {'q': 'הם ___ בחיפה כבר שנים. [לגור]', 'a': ['גרים'], 'en': 'They’ve lived in Haifa for years.'},
         {'q': 'אתמול ___ את התיק פה. [לשים]', 'a': ['שמתי'], 'en': 'Yesterday I put the bag here.'},
         {'q': 'מחר אנחנו ___ ללונדון. [לטוס]', 'a': ['נטוס'], 'en': 'Tomorrow we fly to London.'},
         {'q': 'היא ___ כל בוקר בפארק. [לרוץ]', 'a': ['רצה'], 'en': 'She runs in the park every morning.'},
         {'q': 'מתי אתם ___? [לבוא]', 'a': ['באים'], 'en': 'When are you coming?'},
       ]},
      {'kind': 'slang', 'he': 'קום קום', 'literal': '“get up, get up”',
       'meaning': 'Come on, up you get.',
       'when': 'The hollow verbs make short, punchy imperatives — קום, שים, בוא, זוז — and those '
               'four are the most-used commands in Hebrew. בוא נלך, "come let’s go", is how '
               'almost every plan starts.',
       'examples': [{'he': 'בוא נלך, מאוחר.', 'en': 'Come on, let’s go, it’s late.'},
                    {'he': 'זוז שנייה, אני לא רואה.', 'en': 'Move a second, I can’t see.'}]},
    ],
  },
  {
    'id': 'he-66', 'n': 66, 'level': 'beginner',
    'title': {'he': 'ריבוי חריג', 'en': 'Plurals that change the word'},
    'objective': 'אישה → נשים. איש → אנשים. בית → בתים. Hebrew has a set of plurals you cannot '
                 'derive, and they are all extremely common words, so they have to be learned '
                 'one at a time.',
    'blocks': [
      {'kind': 'teach', 'title': 'The regular rule, and the words that ignore it',
       'body': 'Normally masculine takes <b>־ים</b> and feminine <b>־ות</b>: ספר → ספרים, '
               'מכונית → מכוניות. Then there are these: <b>אישה → נשים</b>, '
               '<b>איש → אנשים</b>, <b>בית → בתים</b>, <b>בן → בנים</b>, <b>בת → בנות</b>, '
               '<b>עיר → ערים</b>, <b>שנה → שנים</b>, <b>יום → ימים</b>, <b>לילה → לילות</b> '
               '(masculine with a feminine ending), <b>אב → אבות</b>. There is no rule to reach '
               'for; there is only the list, and it is short.',
       'examples': [
         {'he': 'יש הרבה אנשים בתחנה.', 'en': 'There are a lot of people at the stop.'},
         {'he': 'שתי נשים חיכו בחוץ.', 'en': 'Two women waited outside.'},
         {'he': 'בנינו שני בתים בשכונה.', 'en': 'We built two houses in the neighbourhood.'},
         {'he': 'עברו שלוש שנים מאז.', 'en': 'Three years have gone by since then.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'נשים', 'en': 'women — from אישה', 'pos': 'noun'},
         {'he': 'אנשים', 'en': 'people — from איש', 'pos': 'noun'},
         {'he': 'בתים', 'en': 'houses — from בית', 'pos': 'noun'},
         {'he': 'ערים', 'en': 'cities — from עיר', 'pos': 'noun'},
         {'he': 'שנים', 'en': 'years — from שנה', 'pos': 'noun'},
         {'he': 'ימים', 'en': 'days — from יום', 'pos': 'noun'},
         {'he': 'לילות', 'en': 'nights — from לילה, masculine', 'pos': 'noun'},
         {'he': 'אבות', 'en': 'fathers — from אב', 'pos': 'noun'},
       ]},
      {'kind': 'match', 'title': 'התאימו יחיד לרבים', 'en': 'Match singular to plural',
       'instructions': 'Tap the singular, then its plural.',
       'pairs': [
         {'he': 'אישה', 'en': 'נשים — women'},
         {'he': 'איש', 'en': 'אנשים — people, men'},
         {'he': 'בית', 'en': 'בתים — houses'},
         {'he': 'עיר', 'en': 'ערים — cities'},
         {'he': 'שנה', 'en': 'שנים — years'},
         {'he': 'לילה', 'en': 'לילות — nights'},
       ]},
      {'kind': 'transform', 'title': 'מיחיד לרבים', 'en': 'Singular to plural',
       'instructions': 'Rewrite in the plural — and mind what else has to agree.',
       'example': {'from': 'יש פה איש אחד.', 'to': 'יש פה אנשים.'},
       'items': [
         {'from': 'הבית גדול.', 'to': ['הבתים גדולים.', 'הבתים גדולים'], 'en': 'The house is big.'},
         {'from': 'העיר יפה.', 'to': ['הערים יפות.', 'הערים יפות'], 'en': 'The city is beautiful.'},
         {'from': 'האישה עובדת פה.', 'to': ['הנשים עובדות פה.', 'הנשים עובדות פה'], 'en': 'The woman works here.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the plural.',
       'example': {'q': 'יש הרבה ___ בתחנה. — people', 'a': 'אנשים'},
       'items': [
         {'q': 'עברו שלוש ___ מאז.', 'a': ['שנים'], 'en': 'Three years have gone by since.'},
         {'q': 'שתי ___ חיכו בחוץ.', 'a': ['נשים'], 'en': 'Two women waited outside.'},
         {'q': 'בשכונה יש הרבה ___ ישנים.', 'a': ['בתים'], 'en': 'There are a lot of old houses in the neighbourhood.'},
         {'q': 'עבדתי שם חמישה ___.', 'a': ['ימים'], 'en': 'I worked there for five days.'},
         {'q': 'ביקרנו בשלוש ___ בצפון.', 'a': ['ערים'], 'en': 'We visited three cities in the north.'},
       ]},
      {'kind': 'slang', 'he': 'אנשים', 'literal': '“people”',
       'meaning': 'Also: “folks”, as a sceptical aside.',
       'when': 'אנשים on its own, with a shrug, means "people, eh" — the way English says '
               '"people". נו, אנשים is a whole comment on human behaviour.',
       'examples': [{'he': 'מה לעשות, אנשים.', 'en': 'What can you do — people.'},
                    {'he': 'יש אנשים ויש אנשים.', 'en': 'There are people, and then there are people.'}]},
    ],
  },
  {
    'id': 'he-67', 'n': 67, 'level': 'intermediate',
    'title': {'he': 'מין השם', 'en': 'The nouns that hide their gender'},
    'objective': 'עיר, דרך, ארץ, רוח, יד, רגל, אבן, כוס are all FEMININE with nothing on them to '
                 'say so. Every adjective and verb near them agrees, so getting this wrong is '
                 'audible in every sentence.',
    'blocks': [
      {'kind': 'teach', 'title': 'No ה, still feminine',
       'body': 'Most feminine nouns end in <b>ה</b> or <b>ת</b> and are easy. These do not, and '
               'they are all everyday words: <b>עיר</b>, <b>דרך</b>, <b>ארץ</b>, <b>רוח</b>, '
               '<b>נפש</b>, <b>אבן</b>, <b>כוס</b>, and the paired body parts <b>יד</b>, '
               '<b>רגל</b>, <b>עין</b>, <b>אוזן</b>. So: עיר <b>יפה</b>, הדרך <b>ארוכה</b>, '
               'כוס <b>אחת</b>. Going the other way, <b>לילה</b> and <b>כיסא</b> look feminine '
               'and are masculine — לילה <b>טוב</b>.',
       'examples': [
         {'he': 'זו עיר יפה מאוד.', 'en': 'That’s a very beautiful city.'},
         {'he': 'הדרך ארוכה, ניקח אוטו.', 'en': 'The way is long, we’ll take a car.'},
         {'he': 'תביא לי כוס אחת.', 'en': 'Bring me one glass.'},
         {'he': 'לילה טוב, נתראה מחר.', 'en': 'Good night, see you tomorrow.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'עיר', 'en': 'city — feminine', 'pos': 'noun'},
         {'he': 'דרך', 'en': 'way, road — feminine', 'pos': 'noun'},
         {'he': 'ארץ', 'en': 'land, country — feminine', 'pos': 'noun'},
         {'he': 'רוח', 'en': 'wind, spirit — feminine', 'pos': 'noun'},
         {'he': 'נפש', 'en': 'soul, person — feminine', 'pos': 'noun'},
         {'he': 'אבן', 'en': 'stone — feminine', 'pos': 'noun'},
         {'he': 'כוס', 'en': 'glass — feminine', 'pos': 'noun'},
         {'he': 'כיכר', 'en': 'square (in a town) — feminine', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'זכר או נקבה?', 'en': 'Masculine or feminine?',
       'instructions': 'The adjective tells you which the noun is.',
       'items': [
         {'q': 'זו עיר ___.', 'options': ['גדולה', 'גדול', 'גדולים'], 'a': 'גדולה',
          'en': 'עיר is feminine, with nothing on it to say so.'},
         {'q': 'הדרך ___ מאוד.', 'options': ['ארוכה', 'ארוך', 'ארוכים'], 'a': 'ארוכה',
          'en': 'דרך is feminine too.'},
         {'q': 'היה לילה ___.', 'options': ['ארוך', 'ארוכה', 'ארוכות'], 'a': 'ארוך',
          'en': 'לילה LOOKS feminine and is masculine — the trap in the other direction.'},
         {'q': 'תביא כוס ___ מים.', 'options': ['אחת', 'אחד', 'ראשון'], 'a': 'אחת',
          'en': 'כוס is feminine, so the number is too.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the adjective in the gender the noun needs.',
       'example': {'q': 'עיר ___ — a beautiful city', 'a': 'יפה'},
       'items': [
         {'q': 'הרוח הייתה ___ מאוד אתמול.', 'a': ['חזקה'], 'en': 'The wind was very strong yesterday.'},
         {'q': 'היד שלי ___.', 'a': ['כואבת'], 'en': 'My hand hurts.'},
         {'q': 'הארץ הזאת ___ מאוד.', 'a': ['קטנה'], 'en': 'This country is very small.'},
         {'q': 'זו אבן ___, אל תרים אותה.', 'a': ['כבדה'], 'en': 'That’s a heavy stone, don’t lift it.'},
         {'q': 'היה לילה ___ ושקט.', 'a': ['ארוך'], 'en': 'It was a long, quiet night.'},
       ]},
      {'kind': 'slang', 'he': 'בארץ', 'literal': '“in the land”',
       'meaning': 'In Israel.',
       'when': 'Israelis say בארץ for their own country and לחוץ לארץ (or חו"ל) for everywhere '
               'else. It is not patriotic, it is just how the geography is divided in speech: '
               'you are either בארץ or בחו"ל.',
       'examples': [{'he': 'אתה בארץ בשבוע הבא?', 'en': 'Are you in the country next week?'},
                    {'he': 'הם חזרו מחו"ל אתמול.', 'en': 'They got back from abroad yesterday.'}]},
    ],
  },
  {
    'id': 'he-68', 'n': 68, 'level': 'intermediate',
    'title': {'he': 'סמיכות ברבים', 'en': 'When the construct goes plural'},
    'objective': 'בית ספר → בתי ספר. The FIRST word changes, not the second, and it changes into '
                 'a form you have not seen. This is where a learner who is otherwise fluent '
                 'still says בית ספרים.',
    'blocks': [
      {'kind': 'teach', 'title': 'The first word takes the plural, in a special shape',
       'body': 'A construct is two nouns glued into one idea: <b>בית ספר</b> "school", '
               '<b>בית קפה</b> "café", <b>עורך דין</b> "lawyer". To make it plural you pluralise '
               'the FIRST word — and masculine ־ים becomes <b>־י</b>: '
               '<b>בתי ספר</b>, <b>בתי קפה</b>, <b>עורכי דין</b>, <b>אנשי עסקים</b>, '
               '<b>גני ילדים</b>. Feminine ־ות stays: <b>תחנות אוטובוס</b>. And the ה of '
               '"the" goes on the SECOND word: <b>בית הספר</b>, not הבית ספר.',
       'examples': [
         {'he': 'יש שני בתי קפה ברחוב.', 'en': 'There are two cafés on the street.'},
         {'he': 'הילדים הולכים לבית הספר בשמונה.', 'en': 'The children go to school at eight.'},
         {'he': 'דיברנו עם עורכי הדין.', 'en': 'We spoke to the lawyers.'},
         {'he': 'יש הרבה גני ילדים בשכונה.', 'en': 'There are a lot of kindergartens in the neighbourhood.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'בית ספר', 'en': 'school', 'pos': 'noun'},
         {'he': 'בית מלון', 'en': 'hotel', 'pos': 'noun'},
         {'he': 'בית חולים', 'en': 'hospital', 'pos': 'noun'},
         {'he': 'גן ילדים', 'en': 'kindergarten', 'pos': 'noun'},
         {'he': 'עורך דין', 'en': 'lawyer', 'pos': 'noun'},
         {'he': 'תחנת אוטובוס', 'en': 'bus stop', 'pos': 'noun'},
         {'he': 'חדר כושר', 'en': 'gym', 'pos': 'noun'},
         {'he': 'יום הולדת', 'en': 'birthday', 'pos': 'noun'},
       ]},
      {'kind': 'transform', 'title': 'מיחיד לרבים', 'en': 'Singular to plural',
       'instructions': 'Only the first word changes.',
       'example': {'from': 'בית ספר', 'to': 'בתי ספר'},
       'items': [
         {'from': 'בית קפה', 'to': ['בתי קפה'], 'en': 'a café'},
         {'from': 'עורך דין', 'to': ['עורכי דין'], 'en': 'a lawyer'},
         {'from': 'גן ילדים', 'to': ['גני ילדים'], 'en': 'a kindergarten'},
         {'from': 'בית חולים', 'to': ['בתי חולים'], 'en': 'a hospital'},
       ]},
      {'kind': 'choose', 'title': 'איפה שמים את ה?', 'en': 'Where does “the” go?',
       'instructions': 'A construct takes its definite article in one place only.',
       'items': [
         {'q': 'the school', 'options': ['בית הספר', 'הבית ספר', 'הבית הספר'], 'a': 'בית הספר',
          'en': 'The ה goes on the second word, always.'},
         {'q': 'the cafés', 'options': ['בתי הקפה', 'הבתי קפה', 'בתים הקפה'], 'a': 'בתי הקפה',
          'en': 'Plural on the first word, ה on the second.'},
         {'q': 'the bus stop', 'options': ['תחנת האוטובוס', 'התחנת אוטובוס', 'תחנה האוטובוס'],
          'a': 'תחנת האוטובוס', 'en': 'Feminine construct — תחנה becomes תחנת.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the construct in the number the sentence needs.',
       'example': {'q': 'יש שני ___ ברחוב. — cafés', 'a': 'בתי קפה'},
       'items': [
         {'q': 'הילדים הולכים ל___ בשמונה.', 'a': ['בית הספר'], 'en': 'The children go to school at eight.'},
         {'q': 'לקחו אותו ל___.', 'a': ['בית חולים', 'בית החולים'], 'en': 'They took him to hospital.'},
         {'q': 'אני מתאמן ב___ פעמיים בשבוע.', 'a': ['חדר כושר'], 'en': 'I train at the gym twice a week.'},
         {'q': 'מחכים ב___ ליד הבית.', 'a': ['תחנת האוטובוס'], 'en': 'We wait at the bus stop near the house.'},
       ]},
      {'kind': 'slang', 'he': 'יום הולדת שמח', 'literal': '“happy day of birth”',
       'meaning': 'Happy birthday.',
       'when': 'A construct so common nobody hears it as two words any more. Note the adjective '
               'agrees with יום, the first word — יום הולדת שמח, never שמחה.',
       'examples': [{'he': 'יום הולדת שמח!', 'en': 'Happy birthday!'},
                    {'he': 'חגגנו את יום ההולדת שלה בבית.', 'en': 'We celebrated her birthday at home.'}]},
    ],
  },
  {
    'id': 'he-69', 'n': 69, 'level': 'intermediate',
    'title': {'he': 'הבינוני כשם עצם', 'en': 'The word for the person who does it'},
    'objective': 'מורה is "teaching". שומר is "guarding". Hebrew turns the present participle '
                 'into the name of the job, so learning a verb often hands you the worker for '
                 'free.',
    'blocks': [
      {'kind': 'teach', 'title': 'The doer is the participle',
       'body': 'From שמר "guarded" you get <b>שומר</b>, which is both "guarding" and "a guard". '
               'From עבד, <b>עובד</b> — "working" and "a worker". From מכר, <b>מוכר</b> — and '
               'from לימד, <b>מורה</b>. The same word can be a verb or a noun in the same '
               'sentence and only the syntax tells you: <b>המורה מלמד</b> — "the teacher '
               'teaches". A second family uses the <b>קַטָּל</b> shape for trades: '
               '<b>טבח</b>, <b>נגר</b>, <b>ספר</b>.',
       'examples': [
         {'he': 'השומר בכניסה ביקש תעודה.', 'en': 'The guard at the entrance asked for ID.'},
         {'he': 'המוכר אמר שאין במידה שלי.', 'en': 'The salesman said they don’t have my size.'},
         {'he': 'היא עובדת כמורה בבית ספר.', 'en': 'She works as a teacher in a school.'},
         {'he': 'הטבח במסעדה הזאת מצוין.', 'en': 'The cook at this restaurant is excellent.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'שומר', 'en': 'guard; guarding', 'pos': 'noun'},
         {'he': 'מוכר', 'en': 'salesperson; selling', 'pos': 'noun'},
         {'he': 'עובד', 'en': 'worker; working', 'pos': 'noun'},
         {'he': 'מורה', 'en': 'teacher', 'pos': 'noun'},
         {'he': 'טבח', 'en': 'cook', 'pos': 'noun'},
         {'he': 'מלצר', 'en': 'waiter', 'pos': 'noun'},
         {'he': 'שוטר', 'en': 'police officer', 'pos': 'noun'},
         {'he': 'נהג', 'en': 'driver', 'pos': 'noun'},
       ]},
      {'kind': 'match', 'title': 'התאימו פועל לעושה', 'en': 'Match the verb to the doer',
       'instructions': 'Tap the verb, then the person who does it.',
       'pairs': [
         {'he': 'לשמור', 'en': 'שומר — a guard'},
         {'he': 'למכור', 'en': 'מוכר — a salesperson'},
         {'he': 'לעבוד', 'en': 'עובד — a worker'},
         {'he': 'לנהוג', 'en': 'נהג — a driver'},
         {'he': 'לבשל', 'en': 'טבח — a cook'},
         {'he': 'ללמד', 'en': 'מורה — a teacher'},
       ]},
      {'kind': 'quiz', 'title': 'שם עצם או פועל?', 'en': 'Noun or verb?',
       'items': [
         {'q': 'In המורה מלמד, what is מורה doing?',
          'options': ['It is the noun — the teacher', 'It is the verb', 'Both at once'],
          'a': 'It is the noun — the teacher',
          'why': 'It has the definite article and it is the subject, so it is a noun. מלמד is '
                 'the verb. Same shape, different job.'},
         {'q': 'הוא עובד קשה — noun or verb?',
          'options': ['Verb — he works hard', 'Noun — he is a hard worker'],
          'a': 'Verb — he works hard',
          'why': 'No article and an adverb after it. For the noun you would say הוא עובד טוב '
                 'in the sense of “a good worker”, and Hebrew is genuinely ambiguous there.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the person who does it.',
       'example': {'q': 'ה___ בכניסה ביקש תעודה. — the guard', 'a': 'שומר'},
       'items': [
         {'q': 'ה___ הביא לנו את התפריט.', 'a': ['מלצר'], 'en': 'The waiter brought us the menu.'},
         {'q': 'ה___ עצר אותנו בכביש.', 'a': ['שוטר'], 'en': 'The police officer stopped us on the road.'},
         {'q': 'היא עובדת כ___ בבית ספר.', 'a': ['מורה'], 'en': 'She works as a teacher in a school.'},
         {'q': 'ה___ של המונית לא ידע את הדרך.', 'a': ['נהג'], 'en': 'The taxi driver didn’t know the way.'},
         {'q': 'ה___ בחנות אמר שאין.', 'a': ['מוכר'], 'en': 'The salesman in the shop said there aren’t any.'},
       ]},
      {'kind': 'slang', 'he': 'עובד עליי', 'literal': '“working on me”',
       'meaning': 'Winding me up / pulling my leg.',
       'when': 'עבד with על means to trick or tease, not to work on something. אתה עובד עליי? '
               'is "are you kidding me?" and is said constantly, in both senses of disbelief.',
       'examples': [{'he': 'אתה עובד עליי, נכון?', 'en': 'You’re winding me up, right?'},
                    {'he': 'הוא עבד עליהם כל הערב.', 'en': 'He was pulling their leg all evening.'}]},
    ],
  },
  {
    'id': 'he-70', 'n': 70, 'level': 'intermediate',
    'title': {'he': 'פנייה', 'en': 'What to call people'},
    'objective': 'Israelis address strangers, colleagues and friends with a small set of words '
                 'that do not map onto English at all — and using the formal ones by default '
                 'makes you sound stiff rather than polite.',
    'blocks': [
      {'kind': 'teach', 'title': 'There is no “you” to choose',
       'body': 'Hebrew has no formal אתה. Everybody is <b>אתה</b> or <b>את</b>, including your '
               'boss and a government clerk. Politeness lives in the words around it instead: '
               '<b>סליחה</b>, <b>בבקשה</b>, <b>אפשר</b>. <b>אדוני</b> and <b>גברתי</b> exist '
               'but are formal to the point of distance — a police officer or a waiter in a '
               'very good restaurant. To a group, <b>חבר\'ה</b>. To a friend, '
               '<b>אחי</b> or <b>גבר</b>, and among friends and family <b>מותק</b> and '
               '<b>יקירי</b>, which are far less loaded than “darling”.',
       'examples': [
         {'he': 'סליחה, אפשר לשאול משהו?', 'en': 'Excuse me, may I ask something?'},
         {'he': 'חבר\'ה, אנחנו זזים!', 'en': 'Folks, we’re off!'},
         {'he': 'אחי, תודה רבה על הכל.', 'en': 'Mate, thanks a lot for everything.'},
         {'he': 'גברתי, שכחת את התיק.', 'en': 'Madam, you forgot your bag.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אדוני', 'en': 'sir', 'pos': 'other'},
         {'he': 'גברתי', 'en': 'madam', 'pos': 'other'},
         {'he': 'אח', 'en': 'brother → אחי, “mate”', 'pos': 'noun'},
         {'he': 'גבר', 'en': 'man → “mate” between men', 'pos': 'noun'},
         {'he': 'מותק', 'en': 'sweetie, love', 'pos': 'noun'},
         {'he': 'יקירי', 'en': 'my dear', 'pos': 'other'},
         {'he': 'חבר', 'en': 'friend', 'pos': 'noun'},
         {'he': 'נימוס', 'en': 'politeness, manners', 'pos': 'noun'},
       ]},
      {'kind': 'choose', 'title': 'איך פונים?', 'en': 'How do you address them?',
       'instructions': 'Pick what an Israeli would actually say.',
       'items': [
         {'q': 'Stopping a stranger in the street to ask directions.',
          'options': ['סליחה, אפשר לשאול?', 'אדוני הנכבד', 'הלו!'],
          'a': 'סליחה, אפשר לשאול?', 'en': 'סליחה does all the work; no title needed.'},
         {'q': 'Getting a group of friends moving.',
          'options': ['חבר\'ה, יאללה', 'רבותיי', 'אנשים'],
          'a': 'חבר\'ה, יאללה', 'en': 'רבותיי is parliamentary; חבר\'ה is everyone else.'},
         {'q': 'Thanking a friend warmly.',
          'options': ['אחי, תודה', 'אדוני, תודה', 'תודה לך, אזרח'],
          'a': 'אחי, תודה', 'en': 'And אחי is said to women too, increasingly.'},
         {'q': 'Talking to your manager at work.',
          'options': ['אתה', 'אדוני', 'כבודו'],
          'a': 'אתה', 'en': 'There is no formal “you” to fall back on, and reaching for one is odd.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': '___, אפשר לשאול משהו? — excuse me', 'a': 'סליחה'},
       'items': [
         {'q': '___, אנחנו מתחילים בעוד רגע.', 'a': ["חבר'ה"], 'en': 'Folks, we’re starting in a moment.'},
         {'q': '___, שכחת את התיק.', 'a': ['גברתי', 'אדוני'], 'en': 'Madam / sir, you forgot your bag.'},
         {'q': '___, תודה רבה על הכל.', 'a': ['אחי'], 'en': 'Mate, thanks a lot for everything.'},
         {'q': 'תגיד לי ___, איפה התחנה?', 'a': ['סליחה'], 'en': 'Tell me — sorry — where’s the station?'},
       ]},
      {'kind': 'slang', 'he': 'אחי', 'literal': '“my brother”',
       'meaning': 'Mate, man, dude.',
       'when': 'Between friends, to strangers your own age, and increasingly to women as well. '
               'It marks the conversation as informal and equal, and dropping it into a work '
               'email would be very funny and very wrong.',
       'examples': [{'he': 'אחי, אתה לא מאמין מה קרה.', 'en': 'Mate, you won’t believe what happened.'},
                    {'he': 'תודה אחי, אתה מציל.', 'en': 'Thanks mate, you’re a lifesaver.'}]},
    ],
  },
  {
    'id': 'he-71', 'n': 71, 'level': 'intermediate',
    'title': {'he': 'עלייה ואולפן', 'en': 'Arriving and learning the language'},
    'objective': 'The vocabulary of being new here — which is the situation a great many people '
                 'using this app are actually in, and it has its own words that no general '
                 'course teaches.',
    'blocks': [
      {'kind': 'teach', 'title': 'The words for arriving',
       'body': 'Moving to Israel is <b>עלייה</b>, literally "going up", and a person who has '
               'done it is an <b>עולה</b> — עולה חדש for the first years. The language school '
               'is an <b>אולפן</b>, a word that means a studio everywhere else. Someone born '
               'here is a <b>צבר</b>; someone long-established is a <b>ותיק</b>. And '
               '<b>מבטא</b>, accent, is discussed openly and usually kindly: '
               '<b>יש לך מבטא יפה</b> is a compliment.',
       'examples': [
         {'he': 'עליתי לארץ לפני שלוש שנים.', 'en': 'I moved to Israel three years ago.'},
         {'he': 'אני לומדת עברית באולפן בבוקר.', 'en': 'I study Hebrew at an ulpan in the morning.'},
         {'he': 'יש לך מבטא, מאיפה אתה?', 'en': 'You have an accent — where are you from?'},
         {'he': 'קיבלתי תעודת זהות אחרי חודש.', 'en': 'I got an ID card after a month.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'עלייה', 'en': 'immigration to Israel; a rise', 'pos': 'noun'},
         {'he': 'עולה', 'en': 'an immigrant to Israel', 'pos': 'noun'},
         {'he': 'אולפן', 'en': 'Hebrew language school', 'pos': 'noun'},
         {'he': 'מבטא', 'en': 'accent', 'pos': 'noun'},
         {'he': 'זהות', 'en': 'identity', 'pos': 'noun'},
         {'he': 'אזרחות', 'en': 'citizenship', 'pos': 'noun'},
         {'he': 'ותיק', 'en': 'long-established, a veteran', 'pos': 'adj'},
         {'he': 'שפה', 'en': 'language', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'אני לומד עברית ב___. — at an ulpan', 'a': 'אולפן'},
       'items': [
         {'q': '___ לארץ לפני שלוש שנים.', 'a': ['עליתי'], 'en': 'I moved to Israel three years ago.'},
         {'q': 'יש לך ___ יפה, מאיפה אתה?', 'a': ['מבטא'], 'en': 'You have a nice accent, where are you from?'},
         {'q': 'קיבלתי תעודת ___ אחרי חודש.', 'a': ['זהות'], 'en': 'I got an ID card after a month.'},
         {'q': 'עברית היא ___ קשה בהתחלה.', 'a': ['שפה'], 'en': 'Hebrew is a hard language at first.'},
         {'q': 'הוא ___ פה, נולד בתל אביב.', 'a': ['צבר'], 'en': 'He’s a sabra, born in Tel Aviv.'},
       ]},
      {'kind': 'choose', 'title': 'מה עונים?', 'en': 'What do you reply?',
       'instructions': 'These questions get asked in the first two minutes. Pick a reply that '
                       'keeps the conversation going.',
       'items': [
         {'q': 'מאיפה אתה?', 'options': ['מאנגליה, אבל אני פה שלוש שנים', 'מפה', 'זה מסובך'],
          'a': 'מאיפה אתה?' == '' and '' or 'מאנגליה, אבל אני פה שלוש שנים',
          'en': 'Where are you from? — say where, then how long.'},
         {'q': 'כמה זמן אתה בארץ?', 'options': ['שלוש שנים בערך', 'הרבה', 'למה?'],
          'a': 'שלוש שנים בערך', 'en': 'How long have you been in the country?'},
         {'q': 'איפה למדת עברית?', 'options': ['באולפן, ואחר כך לבד', 'בבית', 'לא למדתי'],
          'a': 'באולפן, ואחר כך לבד', 'en': 'Where did you learn Hebrew?'},
       ]},
      {'kind': 'slang', 'he': 'עברית קשה שפה', 'literal': '“Hebrew hard language” — with the '
                                                          'words in the wrong order on purpose',
       'meaning': 'A joke about speaking Hebrew badly, said BY Hebrew speakers.',
       'when': 'The word order is deliberately broken, the way a beginner would break it. '
               'Israelis say it to each other when something is confusing, and to a learner it '
               'is a friendly wave rather than a correction.',
       'examples': [{'he': 'לא הבנתי כלום. עברית קשה שפה.', 'en': 'I understood nothing. Hebrew hard language.'},
                    {'he': 'אל תדאג, גם לנו קשה.', 'en': 'Don’t worry, it’s hard for us too.'}]},
    ],
  },
  {
    'id': 'he-72', 'n': 72, 'level': 'intermediate',
    'title': {'he': 'דתי וחילוני', 'en': 'Religious and secular'},
    'objective': 'A set of words that come up in ordinary conversation constantly — kosher, '
                 'Shabbat, synagogue, secular — and that a learner needs in order to follow what '
                 'people are actually saying about each other.',
    'blocks': [
      {'kind': 'teach', 'title': 'Four words people use about themselves',
       'body': '<b>חילוני</b> — secular. <b>דתי</b> — religious. <b>מסורתי</b> — traditional: '
               'observing some things, and it is the largest group of the three. '
               '<b>חרדי</b> — ultra-orthodox. People describe themselves with these readily and '
               'ask about others. Practically: <b>כשר</b> covers food, <b>שומר שבת</b> means '
               'not driving or working on Saturday, and <b>בית כנסת</b> is a synagogue. Note '
               'that a great deal of the vocabulary is shared regardless — חג שמח and בעזרת השם '
               'are said by everyone.',
       'examples': [
         {'he': 'המשפחה שלי מסורתית, לא דתית.', 'en': 'My family is traditional, not religious.'},
         {'he': 'המסעדה כשרה, אז היא סגורה בשבת.', 'en': 'The restaurant is kosher, so it’s closed on Saturday.'},
         {'he': 'הוא שומר שבת ולא נוסע.', 'en': 'He observes Shabbat and doesn’t drive.'},
         {'he': 'יש בית כנסת בסוף הרחוב.', 'en': 'There’s a synagogue at the end of the street.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'דת', 'en': 'religion', 'pos': 'noun'},
         {'he': 'דתי', 'en': 'religious', 'pos': 'adj'},
         {'he': 'חילוני', 'en': 'secular', 'pos': 'adj'},
         {'he': 'מסורתי', 'en': 'traditional (partly observant)', 'pos': 'adj'},
         {'he': 'כשר', 'en': 'kosher', 'pos': 'adj'},
         {'he': 'בית כנסת', 'en': 'synagogue', 'pos': 'noun'},
         {'he': 'רב', 'en': 'rabbi; also: a great deal', 'pos': 'noun'},
         {'he': 'תפילה', 'en': 'prayer', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'המסעדה ___, אז אין בשר וחלב. — kosher', 'a': 'כשרה'},
       'items': [
         {'q': 'המשפחה שלי ___, לא דתית.', 'a': ['מסורתית'], 'en': 'My family is traditional, not religious.'},
         {'q': 'הוא ___ שבת ולא נוסע.', 'a': ['שומר'], 'en': 'He observes Shabbat and doesn’t drive.'},
         {'q': 'יש ___ כנסת בסוף הרחוב.', 'a': ['בית'], 'en': 'There’s a synagogue at the end of the street.'},
         {'q': 'רוב האנשים בעיר הזאת ___.', 'a': ['חילונים'], 'en': 'Most people in this city are secular.'},
         {'q': 'בשבת הכל ___ פה.', 'a': ['סגור'], 'en': 'On Saturday everything here is closed.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Someone says אני מסורתי. What does that tell you?',
          'options': ['They keep some traditions but are not strictly observant',
                      'They are ultra-orthodox', 'They are not Jewish'],
          'a': 'They keep some traditions but are not strictly observant',
          'why': 'מסורתי is its own category, not a halfway apology — Friday dinner and a '
                 'synagogue on the high holidays, and the car still gets driven.'},
         {'q': 'Why do many shops and buses stop on Friday evening?',
          'options': ['Shabbat begins at sunset on Friday',
                      'It is the end of the working month', 'A national holiday every week'],
          'a': 'Shabbat begins at sunset on Friday',
          'why': 'The Hebrew day starts in the evening, which is also why ערב שבת means Friday '
                 'and not Saturday night.'},
       ]},
      {'kind': 'slang', 'he': 'בעזרת השם', 'literal': '“with God’s help”',
       'meaning': 'Hopefully / all being well.',
       'when': 'Said by religious speakers literally and by plenty of secular ones as a set '
               'phrase, exactly like "God willing" in English. Its short written form is '
               'בס"ד at the top of a page.',
       'examples': [{'he': 'ניפגש מחר, בעזרת השם.', 'en': 'We’ll meet tomorrow, all being well.'},
                    {'he': 'יהיה בסדר, בעזרת השם.', 'en': 'It’ll be fine, God willing.'}]},
    ],
  },
  {
    'id': 'he-73', 'n': 73, 'level': 'beginner',
    'title': {'he': 'חירום', 'en': 'Emergencies'},
    'objective': 'Ten sentences that have to come out without thinking. This unit is short on '
                 'purpose and worth more than any other in the course on one particular day.',
    'blocks': [
      {'kind': 'teach', 'title': 'Say what, then where',
       'body': 'The frame is always the same: <b>יש</b> + what, then the place. '
               '<b>יש תאונה ברחוב הרצל</b>. <b>יש שריפה בבניין</b>. For a person: '
               '<b>מישהו נפצע</b>. To call for help: <b>תעזרו!</b> or <b>הצילו!</b> The '
               'services: <b>משטרה</b> 100, <b>אמבולנס</b> (מד"א) 101, <b>מכבי אש</b> 102. '
               'And <b>דחוף</b> — urgent — is the word that moves a queue.',
       'examples': [
         {'he': 'יש תאונה ברחוב הראשי.', 'en': 'There’s an accident on the main street.'},
         {'he': 'מישהו נפצע, צריך אמבולנס.', 'en': 'Someone’s hurt, we need an ambulance.'},
         {'he': 'תתקשרו למשטרה, מהר!', 'en': 'Call the police, quickly!'},
         {'he': 'זה דחוף, בבקשה.', 'en': 'It’s urgent, please.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'משטרה', 'en': 'police', 'pos': 'noun'},
         {'he': 'אמבולנס', 'en': 'ambulance', 'pos': 'noun'},
         {'he': 'עזרה', 'en': 'help', 'pos': 'noun'},
         {'he': 'סכנה', 'en': 'danger', 'pos': 'noun'},
         {'he': 'פצוע', 'en': 'injured', 'pos': 'adj'},
         {'he': 'דחוף', 'en': 'urgent', 'pos': 'adj'},
         {'he': 'להציל', 'en': 'to save, to rescue', 'pos': 'verb'},
         {'he': 'חירום', 'en': 'emergency', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word. These are worth knowing cold.',
       'example': {'q': 'יש ___ ברחוב. — an accident', 'a': 'תאונה'},
       'items': [
         {'q': 'מישהו ___, צריך אמבולנס.', 'a': ['נפצע'], 'en': 'Someone’s hurt, we need an ambulance.'},
         {'q': 'תתקשרו ל___, מהר!', 'a': ['משטרה'], 'en': 'Call the police, quickly!'},
         {'q': 'זה ___, בבקשה.', 'a': ['דחוף'], 'en': 'It’s urgent, please.'},
         {'q': 'צריך ___, אני לא מסתדר.', 'a': ['עזרה'], 'en': 'I need help, I can’t manage.'},
         {'q': 'יש ___ בבניין!', 'a': ['שריפה'], 'en': 'There’s a fire in the building!'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['יש', 'תאונה', 'ברחוב', 'הראשי'], 'a': 'יש תאונה ברחוב הראשי',
          'en': 'There’s an accident on the main street.'},
         {'words': ['מישהו', 'נפצע', 'צריך', 'אמבולנס'], 'a': 'מישהו נפצע צריך אמבולנס',
          'en': 'Someone is hurt, an ambulance is needed.'},
         {'words': ['אני', 'לא', 'מרגיש', 'טוב', 'בכלל'], 'a': 'אני לא מרגיש טוב בכלל',
          'en': 'I don’t feel well at all.'},
       ]},
      {'kind': 'slang', 'he': 'מד"א', 'literal': 'the initials of מגן דוד אדום',
       'meaning': 'The ambulance service — said as one word, "Mada".',
       'when': 'Israeli institutions live in their acronyms and are said as words, not letters: '
               'מד"א, צה"ל, שב"כ, קופ"ח. A learner who expects the full name will not catch '
               'them in speech.',
       'examples': [{'he': 'תתקשר למד"א, מאה ואחת.', 'en': 'Call Mada — one-oh-one.'},
                    {'he': 'מד"א הגיעו תוך חמש דקות.', 'en': 'The ambulance came within five minutes.'}]},
    ],
  },
  {
    'id': 'he-74', 'n': 74, 'level': 'beginner',
    'title': {'he': 'בסופר', 'en': 'At the supermarket'},
    'objective': 'Weights, quantities, offers and the checkout. The one shop everybody enters '
                 'weekly, and the numbers unit finally gets used on real things.',
    'blocks': [
      {'kind': 'teach', 'title': 'Quantities come before the thing',
       'body': 'Hebrew counts by weight in kilos and by the piece: <b>קילו עגבניות</b>, '
               '<b>חצי קילו גבינה</b>, <b>שתי חבילות</b>, <b>שקית לחם</b>. An offer is a '
               '<b>מבצע</b>, and the sign will say <b>1+1</b> — said "אחד פלוס אחד". '
               '<b>הנחה</b> is a discount. At the till you will be asked '
               '<b>שקית?</b> and <b>חשבונית?</b>, and both answers are one word.',
       'examples': [
         {'he': 'אפשר חצי קילו עגבניות?', 'en': 'Half a kilo of tomatoes, please?'},
         {'he': 'יש מבצע על הגבינה הזאת.', 'en': 'There’s an offer on this cheese.'},
         {'he': 'איפה המדף של הלחם?', 'en': 'Where’s the bread shelf?'},
         {'he': 'לא צריך שקית, תודה.', 'en': 'No bag, thanks.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'עגלה', 'en': 'trolley; a cart', 'pos': 'noun'},
         {'he': 'קופה', 'en': 'till, checkout', 'pos': 'noun'},
         {'he': 'מבצע', 'en': 'a special offer; an operation', 'pos': 'noun'},
         {'he': 'מחיר', 'en': 'price', 'pos': 'noun'},
         {'he': 'מדף', 'en': 'shelf', 'pos': 'noun'},
         {'he': 'שקית', 'en': 'bag', 'pos': 'noun'},
         {'he': 'מוצר', 'en': 'product', 'pos': 'noun'},
         {'he': 'ירקות', 'en': 'vegetables', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'יש ___ על הגבינה. — an offer', 'a': 'מבצע'},
       'items': [
         {'q': 'אפשר חצי ___ עגבניות?', 'a': ['קילו'], 'en': 'Half a kilo of tomatoes, please?'},
         {'q': 'איפה ה___ של הלחם?', 'a': ['מדף'], 'en': 'Where’s the bread shelf?'},
         {'q': 'לא צריך ___, תודה.', 'a': ['שקית'], 'en': 'No bag, thanks.'},
         {'q': 'יש תור ארוך ב___.', 'a': ['קופה'], 'en': 'There’s a long queue at the till.'},
         {'q': 'קניתי ___ ופירות טריים.', 'a': ['ירקות'], 'en': 'I bought fresh vegetables and fruit.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'כמה זה קילו?', 'en': 'How much is a kilo?'},
         {'he': 'יש מבצע?', 'en': 'Is there an offer on?'},
         {'he': 'איפה החלב?', 'en': 'Where’s the milk?'},
         {'he': 'שקית, בבקשה', 'en': 'A bag, please'},
         {'he': 'זה הכל', 'en': 'That’s everything'},
         {'he': 'אפשר לשלם באשראי?', 'en': 'Can I pay by card?'},
       ]},
      {'kind': 'slang', 'he': 'בקטנה', 'literal': '“in a small one”',
       'meaning': 'Just a little / no big deal.',
       'when': 'Ordering, buying and agreeing all use it: תן לי בקטנה is "just a small one", and '
               'נעשה משהו בקטנה is "let’s do something low-key".',
       'examples': [{'he': 'תן לי בקטנה, אני לא רעב.', 'en': 'Just a small one, I’m not hungry.'},
                    {'he': 'בקטנה, בלי לחץ.', 'en': 'No big deal, no pressure.'}]},
    ],
  },
  {
    'id': 'he-75', 'n': 75, 'level': 'intermediate',
    'title': {'he': 'טיולים בארץ', 'en': 'Getting out of the city'},
    'objective': 'A country you can cross in a day, and a national habit of walking around in '
                 'it. The landscape words come up constantly in conversation and never in a '
                 'textbook.',
    'blocks': [
      {'kind': 'teach', 'title': 'North, south and the words in between',
       'body': 'The country divides in speech into <b>הצפון</b>, <b>המרכז</b>, <b>הדרום</b>, '
               'plus <b>הגליל</b> and <b>הנגב</b> by name. You walk a <b>שביל</b>, you go to a '
               '<b>נחל</b> (a stream, usually dry) or a <b>מפל</b>, and you are told constantly '
               'to take <b>הרבה מים</b> and a <b>כובע</b>. A nature reserve is a '
               '<b>שמורה</b>. The verb is <b>לטייל</b>, and it covers everything from a walk to '
               'a year in South America.',
       'examples': [
         {'he': 'נסענו לטייל בצפון בסוף השבוע.', 'en': 'We went hiking in the north at the weekend.'},
         {'he': 'קחו הרבה מים וכובע, חם היום.', 'en': 'Take plenty of water and a hat, it’s hot today.'},
         {'he': 'השביל מתחיל אחרי החנייה.', 'en': 'The trail starts after the car park.'},
         {'he': 'יש מפל יפה בסוף הנחל.', 'en': 'There’s a lovely waterfall at the end of the stream.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'טיול', 'en': 'a trip, a walk', 'pos': 'noun'},
         {'he': 'שביל', 'en': 'trail, path', 'pos': 'noun'},
         {'he': 'נחל', 'en': 'stream, wadi', 'pos': 'noun'},
         {'he': 'מפל', 'en': 'waterfall', 'pos': 'noun'},
         {'he': 'הר', 'en': 'mountain', 'pos': 'noun'},
         {'he': 'מדבר', 'en': 'desert', 'pos': 'noun'},
         {'he': 'שמורה', 'en': 'nature reserve', 'pos': 'noun'},
         {'he': 'תרמיל', 'en': 'backpack', 'pos': 'noun'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'ה___ מתחיל אחרי החנייה. — the trail', 'a': 'שביל'},
       'items': [
         {'q': 'נסענו ל___ בצפון בסוף השבוע.', 'a': ['טיול'], 'en': 'We went on a trip to the north at the weekend.'},
         {'q': 'קחו הרבה מים ו___.', 'a': ['כובע'], 'en': 'Take plenty of water and a hat.'},
         {'q': 'יש ___ יפה בסוף הנחל.', 'a': ['מפל'], 'en': 'There’s a lovely waterfall at the end of the stream.'},
         {'q': 'ב___ אין צל בכלל.', 'a': ['מדבר'], 'en': 'In the desert there’s no shade at all.'},
         {'q': 'עלינו על ה___ בשעתיים.', 'a': ['הר'], 'en': 'We climbed the mountain in two hours.'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Tap the words in the right order.',
       'items': [
         {'words': ['נסענו', 'לטייל', 'בגליל', 'בסוף', 'השבוע'], 'a': 'נסענו לטייל בגליל בסוף השבוע',
          'en': 'We went hiking in the Galilee at the weekend.'},
         {'words': ['קחו', 'הרבה', 'מים', 'חם', 'היום'], 'a': 'קחו הרבה מים חם היום',
          'en': 'Take plenty of water, it’s hot today.'},
         {'words': ['השביל', 'ארוך', 'אבל', 'לא', 'קשה'], 'a': 'השביל ארוך אבל לא קשה',
          'en': 'The trail is long but not hard.'},
       ]},
      {'kind': 'slang', 'he': 'טיול אחרי צבא', 'literal': '“a trip after the army”',
       'meaning': 'The long backpacking trip Israelis take in their early twenties.',
       'when': 'A whole institution in two words, and the reason Hebrew is spoken in hostels in '
               'South America and south-east Asia. Asked where someone has been, this is often '
               'the answer.',
       'examples': [{'he': 'הוא בטיול אחרי צבא בדרום אמריקה.', 'en': 'He’s on his post-army trip in South America.'},
                    {'he': 'חזרתי מטיול של חצי שנה.', 'en': 'I got back from a six-month trip.'}]},
    ],
  },
  {
    'id': 'he-76', 'n': 76, 'level': 'intermediate',
    'title': {'he': 'אנשים ואופי', 'en': 'Describing people'},
    'objective': 'Beyond נחמד. The adjectives Israelis actually use about each other, several of '
                 'which are compliments in Hebrew and would not be in English.',
    'blocks': [
      {'kind': 'teach', 'title': 'Directness is a virtue here',
       'body': '<b>ישיר</b> — direct — is praise. So is <b>חרוץ</b> (hard-working) and '
               '<b>נדיב</b> (generous). <b>עקשן</b>, stubborn, is said with something close to '
               'affection. On the other side: <b>עצלן</b>, <b>קמצן</b>, and '
               '<b>חוצפן</b> — cheeky, from <b>חוצפה</b>, which is a fault and a compliment in '
               'the same breath depending entirely on who is speaking. All of them agree like '
               'ordinary adjectives: נחמד, נחמדה, נחמדים.',
       'examples': [
         {'he': 'הוא בחור נחמד ורציני.', 'en': 'He’s a nice, serious guy.'},
         {'he': 'היא מאוד ישירה, זה טוב.', 'en': 'She’s very direct, and that’s a good thing.'},
         {'he': 'הוא עקשן, אבל בסוף הוא צודק.', 'en': 'He’s stubborn, but in the end he’s right.'},
         {'he': 'איזו חוצפה!', 'en': 'What a cheek!'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'נחמד', 'en': 'nice', 'pos': 'adj'},
         {'he': 'רציני', 'en': 'serious', 'pos': 'adj'},
         {'he': 'חרוץ', 'en': 'hard-working', 'pos': 'adj'},
         {'he': 'עצלן', 'en': 'lazy', 'pos': 'adj'},
         {'he': 'נדיב', 'en': 'generous', 'pos': 'adj'},
         {'he': 'קמצן', 'en': 'stingy', 'pos': 'adj'},
         {'he': 'עקשן', 'en': 'stubborn', 'pos': 'adj'},
         {'he': 'חכם', 'en': 'clever, wise', 'pos': 'adj'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the adjective, agreeing with the person.',
       'example': {'q': 'הוא בחור ___. — nice', 'a': 'נחמד'},
       'items': [
         {'q': 'היא מאוד ___, עובדת מהבוקר עד הלילה.', 'a': ['חרוצה'], 'en': 'She’s very hard-working, from morning till night.'},
         {'q': 'הוא ___ ולא מוותר אף פעם.', 'a': ['עקשן'], 'en': 'He’s stubborn and never gives in.'},
         {'q': 'הם אנשים ___ מאוד, תמיד עוזרים.', 'a': ['נדיבים'], 'en': 'They’re very generous people, always helping.'},
         {'q': 'הילד ה___ הזה לא עשה כלום.', 'a': ['עצלן'], 'en': 'That lazy boy did nothing.'},
         {'q': 'היא בחורה ___ מאוד.', 'a': ['חכמה'], 'en': 'She’s a very clever girl.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'ישיר', 'en': 'direct — and it is a compliment'},
         {'he': 'חרוץ', 'en': 'hard-working'},
         {'he': 'עקשן', 'en': 'stubborn'},
         {'he': 'קמצן', 'en': 'stingy'},
         {'he': 'נדיב', 'en': 'generous'},
         {'he': 'חוצפן', 'en': 'cheeky'},
       ]},
      {'kind': 'slang', 'he': 'חוצפה', 'literal': 'from the root ח־צ־פ, insolence',
       'meaning': 'Nerve, gall — and sometimes admirable nerve.',
       'when': 'The word came into English from Yiddish precisely because it has no equivalent. '
               'איזו חוצפה is outrage; יש לו חוצפה בריאה is closer to "he has some healthy '
               'nerve", which is praise.',
       'examples': [{'he': 'איזו חוצפה, לדבר ככה!', 'en': 'What a nerve, to talk like that!'},
                    {'he': 'צריך חוצפה בשביל לבקש את זה.', 'en': 'You need some nerve to ask for that.'}]},
    ],
  },
]


# ---------------------------------------------------------------------------------------------
# UNITS 77-88. Six grammar units on things that are structurally simple and behaviourally hard --
# a yes/no question with no question word in it, a verb with two objects, an intransitive twin
# that is a whole separate verb, modals that have to borrow היה to leave the present. Then the
# little words that carry attitude rather than meaning, which is where a fluent learner still
# sounds flat. And five more rooms of the week.
UNITS += [
  {
    'id': 'he-77', 'n': 77, 'level': 'beginner',
    'title': {'he': 'שאלות כן ולא', 'en': 'Questions with no question word'},
    'objective': 'Hebrew asks yes/no questions by tone alone — the words do not move and nothing '
                 'is added. Which means you have to hear the question, and produce it.',
    'blocks': [
      {'kind': 'teach', 'title': 'Same sentence, rising at the end',
       'body': 'English inverts — "you are coming" becomes "are you coming". Hebrew does not '
               'move a thing: <b>אתה בא</b> and <b>אתה בא?</b> are the same four letters and '
               'the question is entirely in the voice. In writing, only the mark tells you. '
               'There IS a question word, <b>האם</b>, but it is formal and written, and using '
               'it in speech sounds like a survey. To confirm rather than ask, tack on '
               '<b>נכון?</b> or <b>לא?</b> at the end.',
       'examples': [
         {'he': 'אתה בא איתנו?', 'en': 'Are you coming with us?'},
         {'he': 'יש לך רגע?', 'en': 'Do you have a minute?'},
         {'he': 'זה יקר, נכון?', 'en': 'It’s expensive, isn’t it?'},
         {'he': 'האם קיבלת את המכתב?', 'en': 'Did you receive the letter? — written register.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'האם', 'en': 'whether, “do…?” (written)', 'pos': 'other'},
         {'he': 'נכון', 'en': 'right; isn’t it?', 'pos': 'adj'},
         {'he': 'באמת', 'en': 'really', 'pos': 'other'},
         {'he': 'בטח', 'en': 'sure, of course', 'pos': 'other'},
         {'he': 'ודאי', 'en': 'certain', 'pos': 'adj'},
         {'he': 'לענות', 'en': 'to answer', 'pos': 'verb'},
         {'he': 'לשאול', 'en': 'to ask', 'pos': 'verb'},
         {'he': 'תשובה', 'en': 'answer', 'pos': 'noun'},
       ]},
      {'kind': 'transform', 'title': 'מהצהרה לשאלה', 'en': 'Statement to question',
       'instructions': 'Nothing moves. Change the punctuation and, out loud, the tone.',
       'example': {'from': 'אתה בא איתנו.', 'to': 'אתה בא איתנו?'},
       'items': [
         {'from': 'יש לך זמן היום.', 'to': ['יש לך זמן היום?'], 'en': 'You have time today.'},
         {'from': 'היא גרה בתל אביב.', 'to': ['היא גרה בתל אביב?'], 'en': 'She lives in Tel Aviv.'},
         {'from': 'הם כבר הגיעו.', 'to': ['הם כבר הגיעו?'], 'en': 'They’ve already arrived.'},
       ]},
      {'kind': 'choose', 'title': 'איך שואלים?', 'en': 'How do you ask?',
       'instructions': 'Pick the one an Israeli would say out loud.',
       'items': [
         {'q': 'Are you coming?', 'options': ['אתה בא?', 'האם אתה בא?', 'בא אתה?'], 'a': 'אתה בא?',
          'en': 'No inversion, no האם — just the tone.'},
         {'q': 'It’s expensive, isn’t it?', 'options': ['זה יקר, נכון?', 'זה יקר, האם?', 'האם זה יקר'],
          'a': 'זה יקר, נכון?', 'en': 'נכון? and לא? are the tags Hebrew uses.'},
         {'q': 'On a form: “Have you lived abroad?”',
          'options': ['האם גרת בחו"ל?', 'גרת בחו"ל?', 'אתה גר בחו"ל'],
          'a': 'האם גרת בחו"ל?', 'en': 'This is where האם belongs — written, formal, a form.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'זה יקר, ___? — isn’t it', 'a': 'נכון'},
       'items': [
         {'q': 'יש ___ רגע?', 'a': ['לך'], 'en': 'Do you have a minute?'},
         {'q': '___ קיבלת את המכתב?', 'a': ['האם'], 'en': 'Did you receive the letter? — on a form.'},
         {'q': 'אתה בא, ___?', 'a': ['לא', 'נכון'], 'en': 'You’re coming, aren’t you?'},
         {'q': '___? לא ידעתי בכלל.', 'a': ['באמת'], 'en': 'Really? I had no idea.'},
       ]},
      {'kind': 'slang', 'he': 'מה, באמת?', 'literal': '“what, really?”',
       'meaning': 'You’re kidding.',
       'when': 'מה at the front of a question is not asking "what" — it marks surprise or '
               'disbelief, the way English says "what, seriously?". מה, לא ידעת? is "you '
               'didn’t KNOW?".',
       'examples': [{'he': 'מה, באמת? מתי זה קרה?', 'en': 'Really? When did that happen?'},
                    {'he': 'מה, לא סיפרו לך?', 'en': 'What, nobody told you?'}]},
    ],
  },
  {
    'id': 'he-78', 'n': 78, 'level': 'intermediate',
    'title': {'he': 'שני מושאים', 'en': 'Giving someone something'},
    'objective': 'נתן לי את זה. Verbs that take a person AND a thing put the person on ל and the '
                 'thing on את — and that order barely moves.',
    'blocks': [
      {'kind': 'teach', 'title': 'The person takes ל, the thing takes את',
       'body': '<b>נתתי לו את הספר</b>. <b>הראיתי לה את הבית</b>. <b>שלחתי להם מכתב</b>. The '
               'person is always on <b>ל</b> — never a bare object — and the thing takes '
               '<b>את</b> when it is definite and nothing when it is not. Both can be pronouns '
               'at once: <b>נתתי לו אותו</b>. The verbs that behave this way are a small, high-'
               'frequency set: נתן, הראה, שלח, הסביר, הביא, החזיר, סיפר, הודיע.',
       'examples': [
         {'he': 'נתתי לו את המפתחות.', 'en': 'I gave him the keys.'},
         {'he': 'תראה לי את התמונה.', 'en': 'Show me the photo.'},
         {'he': 'שלחתי לה מכתב אתמול.', 'en': 'I sent her a letter yesterday.'},
         {'he': 'הוא הסביר לנו הכל מההתחלה.', 'en': 'He explained everything to us from the start.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להראות', 'en': 'to show — להראות ל', 'pos': 'verb'},
         {'he': 'לשלוח', 'en': 'to send — לשלוח ל', 'pos': 'verb'},
         {'he': 'להסביר', 'en': 'to explain — להסביר ל', 'pos': 'verb'},
         {'he': 'להביא', 'en': 'to bring — להביא ל', 'pos': 'verb'},
         {'he': 'להחזיר', 'en': 'to return, to give back', 'pos': 'verb'},
         {'he': 'להודיע', 'en': 'to inform — להודיע ל', 'pos': 'verb'},
         {'he': 'מתנה', 'en': 'present', 'pos': 'noun'},
         {'he': 'הזדמנות', 'en': 'opportunity', 'pos': 'noun'},
       ]},
      {'kind': 'order', 'title': 'סדרו את המשפט', 'en': 'Put the sentence in order',
       'instructions': 'Person first, thing second.',
       'items': [
         {'words': ['נתתי', 'לו', 'את', 'המפתחות'], 'a': 'נתתי לו את המפתחות',
          'en': 'I gave him the keys.'},
         {'words': ['תראה', 'לי', 'את', 'התמונה'], 'a': 'תראה לי את התמונה',
          'en': 'Show me the photo.'},
         {'words': ['הוא', 'הסביר', 'לנו', 'הכל'], 'a': 'הוא הסביר לנו הכל',
          'en': 'He explained everything to us.'},
         {'words': ['שלחתי', 'להם', 'מכתב', 'אתמול'], 'a': 'שלחתי להם מכתב אתמול',
          'en': 'I sent them a letter yesterday.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing preposition or pronoun.',
       'example': {'q': 'נתתי ___ את הספר. — to him', 'a': 'לו'},
       'items': [
         {'q': 'תראה ___ מה קנית.', 'a': ['לי'], 'en': 'Show me what you bought.'},
         {'q': 'הבאתי ___ מתנה קטנה.', 'a': ['לך', 'לה', 'לו'], 'en': 'I brought you / her / him a small present.'},
         {'q': 'הוא החזיר לי ___ הכסף.', 'a': ['את'], 'en': 'He gave me back the money.'},
         {'q': 'תודיע ___ כשתדע.', 'a': ['לי'], 'en': 'Let me know when you find out.'},
         {'q': 'סיפרתי ___ הכל אתמול.', 'a': ['להם', 'לו', 'לה'], 'en': 'I told them / him / her everything yesterday.'},
       ]},
      {'kind': 'slang', 'he': 'תן לי לראות', 'literal': '“give me to see”',
       'meaning': 'Let me see.',
       'when': 'נתן plus ל plus an infinitive is the Hebrew "let". תן לי לראות, תן לו לדבר, '
               'אל תיתן לזה לקרות — and it is the same two-object frame with a verb in the '
               'thing slot.',
       'examples': [{'he': 'תן לי לראות רגע.', 'en': 'Let me have a look a second.'},
                    {'he': 'תנו לו לסיים.', 'en': 'Let him finish.'}]},
    ],
  },
  {
    'id': 'he-79', 'n': 79, 'level': 'intermediate',
    'title': {'he': 'זוגות פעלים', 'en': 'It broke, and I broke it'},
    'objective': 'לשבור / להישבר. לפתוח / להיפתח. Hebrew has a separate verb for "it happened by '
                 'itself", and using the transitive one for both is the commonest structural '
                 'mistake at this level.',
    'blocks': [
      {'kind': 'teach', 'title': 'Two verbs, one root',
       'body': 'The פעל verb takes an object: <b>שברתי את הכוס</b>. Its נפעל twin does not: '
               '<b>הכוס נשברה</b> — the glass broke, nobody named. Same for '
               '<b>פתח / נפתח</b>, <b>סגר / נסגר</b>, <b>גמר / נגמר</b>. A second pattern uses '
               'התפעל: <b>שינה / השתנה</b>, <b>הפסיק / נפסק</b>. The test is simple — is there '
               'an את after the verb? If not, you probably want the twin.',
       'examples': [
         {'he': 'שברתי את הכוס בטעות.', 'en': 'I broke the glass by accident.'},
         {'he': 'הכוס נשברה על הרצפה.', 'en': 'The glass broke on the floor.'},
         {'he': 'הדלת נפתחה לבד.', 'en': 'The door opened by itself.'},
         {'he': 'המצב השתנה לגמרי.', 'en': 'The situation has completely changed.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'להישבר', 'en': 'to break (by itself)', 'pos': 'verb'},
         {'he': 'להיפתח', 'en': 'to open (by itself)', 'pos': 'verb'},
         {'he': 'להיסגר', 'en': 'to close (by itself)', 'pos': 'verb'},
         {'he': 'להיגמר', 'en': 'to end, to run out', 'pos': 'verb'},
         {'he': 'להשתנות', 'en': 'to change (by itself)', 'pos': 'verb'},
         {'he': 'לשנות', 'en': 'to change (something)', 'pos': 'verb'},
         {'he': 'בטעות', 'en': 'by mistake', 'pos': 'other'},
         {'he': 'לבד', 'en': 'alone, by itself', 'pos': 'other'},
       ]},
      {'kind': 'choose', 'title': 'איזה מהשניים?', 'en': 'Which of the two?',
       'instructions': 'Is there an object after the verb?',
       'items': [
         {'q': 'הדלת ___ לבד.', 'options': ['נפתחה', 'פתחה', 'פותחת'], 'a': 'נפתחה',
          'en': 'The door opened by itself — no object, so the נפעל twin.'},
         {'q': 'אני ___ את החלון.', 'options': ['פותח', 'נפתח', 'נפתחת'], 'a': 'פותח',
          'en': 'I open the window — there is an את, so the transitive verb.'},
         {'q': 'החלב ___, צריך לקנות.', 'options': ['נגמר', 'גמר', 'גומר'], 'a': 'נגמר',
          'en': 'The milk has run out — it happened, nobody did it.'},
         {'q': 'המצב ___ לגמרי.', 'options': ['השתנה', 'שינה', 'משנה'], 'a': 'השתנה',
          'en': 'The situation changed — intransitive.'},
       ]},
      {'kind': 'transform', 'title': 'מפעיל לעומד', 'en': 'Transitive to intransitive',
       'instructions': 'Rewrite so the thing is the subject and nobody did it.',
       'example': {'from': 'שברתי את הכוס.', 'to': 'הכוס נשברה.'},
       'items': [
         {'from': 'סגרתי את הדלת.', 'to': ['הדלת נסגרה.', 'הדלת נסגרה'], 'en': 'I closed the door.'},
         {'from': 'גמרתי את החלב.', 'to': ['החלב נגמר.', 'החלב נגמר'], 'en': 'I finished the milk.'},
         {'from': 'שיניתי את התוכנית.', 'to': ['התוכנית השתנתה.', 'התוכנית השתנתה'], 'en': 'I changed the plan.'},
       ]},
      {'kind': 'slang', 'he': 'נגמר לי', 'literal': '“it ran out to me”',
       'meaning': 'I’ve run out of it — or, of patience, I’ve had it.',
       'when': 'The intransitive twin plus ל puts the person back in as the one affected. '
               'נגמר לי החלב is about milk; נגמר לי is about you.',
       'examples': [{'he': 'נגמר לי הכסף עד סוף החודש.', 'en': 'My money runs out before the end of the month.'},
                    {'he': 'נגמרה לי הסבלנות.', 'en': 'I’ve run out of patience.'}]},
    ],
  },
  {
    'id': 'he-80', 'n': 80, 'level': 'intermediate',
    'title': {'he': 'צריך היה, יהיה אפשר', 'en': 'Modals outside the present'},
    'objective': 'צריך, יכול, אפשר, כדאי, מותר have no past and no future of their own. They '
                 'borrow היה — and where it goes is not where an English speaker puts it.',
    'blocks': [
      {'kind': 'teach', 'title': 'היה carries the tense, the modal stays put',
       'body': 'Present <b>צריך ללכת</b>. Past <b>הייתי צריך ללכת</b> — היה agrees with the '
               'person. Future <b>אצטרך ללכת</b>, because צריך does have a real verb behind it. '
               'The impersonal ones are simpler and do not agree at all: '
               '<b>אפשר</b> → <b>היה אפשר</b> → <b>יהיה אפשר</b>; <b>כדאי</b> → '
               '<b>היה כדאי</b>; <b>מותר</b> → <b>היה מותר</b>; <b>אסור</b> → <b>היה אסור</b>. '
               'One frozen word plus היה, whoever is talking.',
       'examples': [
         {'he': 'הייתי צריך לצאת מוקדם.', 'en': 'I had to leave early.'},
         {'he': 'היה אפשר להזמין מראש.', 'en': 'It was possible to book in advance.'},
         {'he': 'יהיה אפשר לשלם באשראי?', 'en': 'Will it be possible to pay by card?'},
         {'he': 'היה כדאי לחכות עוד קצת.', 'en': 'It would have been worth waiting a bit longer.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'צריך', 'en': 'need to, have to', 'pos': 'adj'},
         {'he': 'כדאי', 'en': 'worth it, advisable', 'pos': 'adj'},
         {'he': 'מותר', 'en': 'allowed', 'pos': 'adj'},
         {'he': 'אסור', 'en': 'forbidden', 'pos': 'adj'},
         {'he': 'חייב', 'en': 'must; owing', 'pos': 'adj'},
         {'he': 'אפשרות', 'en': 'possibility', 'pos': 'noun'},
         {'he': 'מראש', 'en': 'in advance', 'pos': 'other'},
         {'he': 'להספיק', 'en': 'to manage in time', 'pos': 'verb'},
       ]},
      {'kind': 'transform', 'title': 'מהווה לעבר', 'en': 'Present to past',
       'instructions': 'Add היה — and mind whether it agrees or not.',
       'example': {'from': 'אני צריך ללכת.', 'to': 'הייתי צריך ללכת.'},
       'items': [
         {'from': 'אפשר להזמין מראש.', 'to': ['היה אפשר להזמין מראש.', 'היה אפשר להזמין מראש'],
          'en': 'It’s possible to book in advance.'},
         {'from': 'היא צריכה לעבוד.', 'to': ['היא הייתה צריכה לעבוד.', 'היא הייתה צריכה לעבוד'],
          'en': 'She has to work.'},
         {'from': 'אסור לעשן פה.', 'to': ['היה אסור לעשן פה.', 'היה אסור לעשן פה'],
          'en': 'Smoking is forbidden here.'},
         {'from': 'כדאי לחכות.', 'to': ['היה כדאי לחכות.', 'היה כדאי לחכות'], 'en': 'It’s worth waiting.'},
       ]},
      {'kind': 'quiz', 'title': 'בדיקה מהירה', 'en': 'Quick check',
       'items': [
         {'q': 'Why is it היה אפשר and not היו אפשר, even about many people?',
          'options': ['אפשר is impersonal and never agrees', 'It is an exception', 'Because of the past tense'],
          'a': 'אפשר is impersonal and never agrees',
          'why': 'There is no subject to agree with — that is what makes it impersonal. Same '
                 'for כדאי, מותר and אסור.'},
         {'q': 'הייתי צריך — how many words carry the person?',
          'options': ['One — הייתי', 'Two — both', 'None'],
          'a': 'One — הייתי',
          'why': 'צריך agrees in gender and number (צריכה, צריכים) but not in PERSON. הייתי is '
                 'what makes it “I”.'},
       ]},
      {'kind': 'slang', 'he': 'לא היה צריך', 'literal': '“there was no need”',
       'meaning': 'You shouldn’t have.',
       'when': 'The ritual reply to a present, and it is not a refusal. The full exchange is '
               'לא היה צריך! — מה פתאום, זה כלום, and skipping your line is the only mistake.',
       'examples': [{'he': 'הבאתי משהו קטן. — לא היה צריך!', 'en': 'I brought something small. — You shouldn’t have!'},
                    {'he': 'באמת לא היה צריך, תודה.', 'en': 'Really, you shouldn’t have — thank you.'}]},
    ],
  },
  {
    'id': 'he-81', 'n': 81, 'level': 'intermediate',
    'title': {'he': 'מידת ודאות', 'en': 'Maybe, probably, definitely'},
    'objective': 'אולי, כנראה, בטח, בוודאי, אין סיכוי. Hebrew grades certainty with adverbs '
                 'rather than with modal verbs, and one of them — בטח — means both "certainly" '
                 'and "yeah, right".',
    'blocks': [
      {'kind': 'teach', 'title': 'A ladder of adverbs',
       'body': 'From least to most sure: <b>אולי</b> (maybe), <b>יכול להיות</b> (could be), '
               '<b>כנראה</b> (probably), <b>בטוח</b> / <b>בוודאי</b> (certainly). To doubt '
               'something: <b>אני בספק</b>, <b>אין סיכוי</b>. All of them sit in front of the '
               'clause and nothing else changes — no subjunctive, no modal verb. Watch '
               '<b>בטח</b>: said flatly it means "of course"; said with a lift it means '
               'exactly the opposite.',
       'examples': [
         {'he': 'אולי נגיע מאוחר יותר.', 'en': 'Maybe we’ll come later.'},
         {'he': 'כנראה שהוא כבר הלך.', 'en': 'He’s probably already left.'},
         {'he': 'אני בטוח שראיתי אותה שם.', 'en': 'I’m sure I saw her there.'},
         {'he': 'אין סיכוי שזה יהיה מוכן היום.', 'en': 'There’s no chance that’ll be ready today.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'אולי', 'en': 'maybe', 'pos': 'other'},
         {'he': 'כנראה', 'en': 'probably', 'pos': 'other'},
         {'he': 'בוודאי', 'en': 'certainly', 'pos': 'other'},
         {'he': 'בטוח', 'en': 'sure, safe', 'pos': 'adj'},
         {'he': 'ספק', 'en': 'doubt', 'pos': 'noun'},
         {'he': 'סיכוי', 'en': 'chance', 'pos': 'noun'},
         {'he': 'לקוות', 'en': 'to hope', 'pos': 'verb'},
         {'he': 'להאמין', 'en': 'to believe — להאמין ל / ב', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'כמה בטוח?', 'en': 'How sure?',
       'instructions': 'Pick the word for the degree of certainty the English shows.',
       'items': [
         {'q': 'He’s probably already left.', 'options': ['כנראה', 'אולי', 'בוודאי'], 'a': 'כנראה',
          'en': 'More than maybe, less than certain.'},
         {'q': 'There’s no chance.', 'options': ['אין סיכוי', 'אולי לא', 'אני בספק'], 'a': 'אין סיכוי',
          'en': 'The flattest refusal on the ladder.'},
         {'q': 'I doubt it.', 'options': ['אני בספק', 'אין סיכוי', 'בטוח'], 'a': 'אני בספק',
          'en': 'Doubt, not denial.'},
         {'q': 'I’m sure I saw her.', 'options': ['אני בטוח ש', 'אולי', 'כנראה ש'], 'a': 'אני בטוח ש',
          'en': 'And note that the clause hangs on ש.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the word for how sure the speaker is.',
       'example': {'q': '___ נגיע מאוחר יותר. — maybe', 'a': 'אולי'},
       'items': [
         {'q': '___ שהוא כבר הלך.', 'a': ['כנראה'], 'en': 'He’s probably already left.'},
         {'q': 'אין ___ שזה יהיה מוכן היום.', 'a': ['סיכוי'], 'en': 'There’s no chance it’ll be ready today.'},
         {'q': 'אני ___ שראיתי אותה שם.', 'a': ['בטוח', 'בטוחה'], 'en': 'I’m sure I saw her there.'},
         {'q': 'אני ___ שיהיה בסדר.', 'a': ['מקווה'], 'en': 'I hope it’ll be all right.'},
         {'q': 'יכול ___ שהם כבר יצאו.', 'a': ['להיות'], 'en': 'It could be that they’ve already left.'},
       ]},
      {'kind': 'slang', 'he': 'בטח', 'literal': '“surely”',
       'meaning': 'Of course — or “yeah, right”, depending entirely on the tone.',
       'when': 'Flat and short, it agrees. Drawn out with a rise, it is sarcasm. Israelis rely '
               'on tone to carry the reversal and a learner reading a transcript will get it '
               'wrong every time.',
       'examples': [{'he': 'בטח שאני בא.', 'en': 'Of course I’m coming.'},
                    {'he': 'בטח, והוא גם ישלם.', 'en': 'Sure, and he’ll pay too. (he won’t)'}]},
    ],
  },
  {
    'id': 'he-82', 'n': 82, 'level': 'intermediate',
    'title': {'he': 'גזרת ל״א', 'en': 'The verbs that end in א'},
    'objective': 'קרא, מצא, יצא, מלא. The א is silent, so the past sounds like it lost a letter '
                 'and the spelling keeps it — which is exactly the trap when you write.',
    'blocks': [
      {'kind': 'teach', 'title': 'Written but not heard',
       'body': 'The third root letter is <b>א</b> and it makes no sound: <b>קָרָא</b> is "kara", '
               '<b>מָצָא</b> is "matsa". In the past with an ending, the א stays on the page and '
               'the vowel lengthens: <b>קראתי</b> "karati", <b>מצאתי</b> "matsati" — never '
               'קרתי. The present is <b>קורא, קוראת, קוראים</b>, and the feminine has no ת '
               'after the א you might expect. Watch <b>קרא</b> "read/called" against '
               '<b>קרה</b> "happened" — one letter, and it is the א.',
       'examples': [
         {'he': 'קראתי את זה בעיתון.', 'en': 'I read that in the paper.'},
         {'he': 'מצאתי את המפתחות בכיס.', 'en': 'I found the keys in my pocket.'},
         {'he': 'היא קוראת ספר כל ערב.', 'en': 'She reads a book every evening.'},
         {'he': 'מה קרה? לא הבנתי.', 'en': 'What happened? I didn’t understand.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'לקרוא', 'en': 'to read; to call', 'pos': 'verb'},
         {'he': 'למצוא', 'en': 'to find', 'pos': 'verb'},
         {'he': 'למלא', 'en': 'to fill (in)', 'pos': 'verb'},
         {'he': 'לשנוא', 'en': 'to hate', 'pos': 'verb'},
         {'he': 'לקרות', 'en': 'to happen', 'pos': 'verb'},
         {'he': 'מלא', 'en': 'full', 'pos': 'adj'},
         {'he': 'חסר', 'en': 'missing, lacking', 'pos': 'adj'},
         {'he': 'חן', 'en': 'grace, charm — as in מצא חן בעיניי', 'pos': 'noun'},
       ]},
      {'kind': 'table', 'title': 'מלאו את הטבלה', 'en': 'Fill in the table',
       'instructions': 'The א stays in the writing even where you cannot hear it.',
       'cols': ['שם פועל', 'הוא, עבר', 'אני, עבר', 'היא, הווה'],
       'rows': [
         [{'g': 'לקרוא'}, {'g': 'קרא'}, {'g': 'קראתי'}, {'g': 'קוראת'}],
         [{'g': 'למצוא'}, {'a': ['מצא']}, {'a': ['מצאתי']}, {'a': ['מוצאת']}],
         [{'g': 'למלא'}, {'a': ['מילא', 'מלא']}, {'a': ['מילאתי', 'מלאתי']}, {'a': ['ממלאת']}],
         [{'g': 'לשנוא'}, {'a': ['שנא']}, {'a': ['שנאתי']}, {'a': ['שונאת']}],
       ]},
      {'kind': 'bracket', 'title': 'כתבו את הפועל', 'en': 'Write the verb',
       'instructions': 'The infinitive is in brackets. Do not drop the א.',
       'example': {'q': '___ את זה בעיתון. [לקרוא]', 'a': 'קראתי'},
       'items': [
         {'q': '___ את המפתחות בכיס. [למצוא]', 'a': ['מצאתי'], 'en': 'I found the keys in my pocket.'},
         {'q': 'היא ___ ספר כל ערב. [לקרוא]', 'a': ['קוראת'], 'en': 'She reads a book every evening.'},
         {'q': 'צריך ___ את הטופס. [למלא]', 'a': ['למלא'], 'en': 'The form has to be filled in.'},
         {'q': 'הם ___ אותנו בשם. [לקרוא]', 'a': ['קראו'], 'en': 'They called us by name.'},
         {'q': 'מה ___ פה אתמול? [לקרות]', 'a': ['קרה'], 'en': 'What happened here yesterday?'},
       ]},
      {'kind': 'slang', 'he': 'מצא חן בעיניי', 'literal': '“it found favour in my eyes”',
       'meaning': 'I liked it.',
       'when': 'A biblical phrase doing everyday work — it is how Hebrew says a thing pleased '
               'you, and it puts the THING as the subject, not you. זה מצא חן בעיניי, not '
               'אני מצאתי חן.',
       'examples': [{'he': 'הרעיון מצא חן בעיניי.', 'en': 'I liked the idea.'},
                    {'he': 'זה לא מצא חן בעיניו בכלל.', 'en': 'He didn’t like it at all.'}]},
    ],
  },
  {
    'id': 'he-83', 'n': 83, 'level': 'advanced',
    'title': {'he': 'דווקא, בכלל, אפילו', 'en': 'The little words that carry the attitude'},
    'objective': 'These have almost no dictionary meaning and change the whole point of a '
                 'sentence. A learner who never uses them sounds flat; one who uses them right '
                 'sounds native faster than any amount of vocabulary will manage.',
    'blocks': [
      {'kind': 'teach', 'title': 'Meaning that lives between the words',
       'body': '<b>דווקא</b> is the hardest word in Hebrew to translate: it marks a contrast '
               'with what you would expect. <b>דווקא טעים</b> — "actually quite good", against '
               'expectation. <b>הוא דווקא בא</b> — he came, though we thought he would not. '
               'Said of a person, <b>הוא עושה את זה דווקא</b> means out of spite. '
               '<b>בכלל</b> intensifies a negative (לא הבנתי בכלל) or resets a topic '
               '(בכלל, למה שאלת?). <b>אפילו</b> is "even". <b>ממש</b> is "really", and it is '
               'used constantly.',
       'examples': [
         {'he': 'האוכל שם דווקא טעים.', 'en': 'The food there is actually rather good.'},
         {'he': 'לא הבנתי בכלל מה הוא אמר.', 'en': 'I didn’t understand a thing he said.'},
         {'he': 'אפילו הוא הסכים בסוף.', 'en': 'Even he agreed in the end.'},
         {'he': 'זה ממש לא מה שהתכוונתי.', 'en': 'That’s really not what I meant.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'דווקא', 'en': 'actually, contrary to expectation; on purpose', 'pos': 'other'},
         {'he': 'בכלל', 'en': 'at all; anyway', 'pos': 'other'},
         {'he': 'אפילו', 'en': 'even', 'pos': 'other'},
         {'he': 'ממש', 'en': 'really, absolutely', 'pos': 'other'},
         {'he': 'בעצם', 'en': 'in fact, come to think of it', 'pos': 'other'},
         {'he': 'לגמרי', 'en': 'completely', 'pos': 'other'},
         {'he': 'כמעט', 'en': 'almost', 'pos': 'other'},
         {'he': 'בערך', 'en': 'roughly, about', 'pos': 'other'},
       ]},
      {'kind': 'choose', 'title': 'מה הוא מתכוון?', 'en': 'What is being conveyed?',
       'instructions': 'These change the point of the sentence, not its facts.',
       'items': [
         {'q': 'האוכל שם דווקא טעים.',
          'options': ['Better than expected', 'The best food there is', 'The food is bad'],
          'a': 'Better than expected', 'en': 'דווקא marks the contrast with what you assumed.'},
         {'q': 'הוא עושה את זה דווקא.',
          'options': ['He does it out of spite', 'He does it well', 'He does it sometimes'],
          'a': 'He does it out of spite',
          'en': 'Said of a person’s behaviour, the same word turns into deliberate contrariness.'},
         {'q': 'בכלל, למה שאלת?',
          'options': ['Resets the topic — “anyway, why did you ask?”',
                      'Means “not at all”', 'Is a rebuke'],
          'a': 'Resets the topic — “anyway, why did you ask?”',
          'en': 'At the front of a sentence בכלל changes subject; after a negative it intensifies.'},
         {'q': 'לא הבנתי בכלל.',
          'options': ['I didn’t understand a thing', 'I understood a little', 'I nearly understood'],
          'a': 'I didn’t understand a thing', 'en': 'With a negative it means “at all”.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the little word the English is carrying.',
       'example': {'q': 'האוכל ___ טעים. — actually, against expectation', 'a': 'דווקא'},
       'items': [
         {'q': '___ הוא הסכים בסוף.', 'a': ['אפילו'], 'en': 'Even he agreed in the end.'},
         {'q': 'זה ___ לא מה שהתכוונתי.', 'a': ['ממש'], 'en': 'That’s really not what I meant.'},
         {'q': 'לא ראיתי אותו ___.', 'a': ['בכלל'], 'en': 'I didn’t see him at all.'},
         {'q': '___, מתי חזרת?', 'a': ['בעצם'], 'en': 'Come to think of it, when did you get back?'},
         {'q': 'זה עלה ___ מאתיים שקל.', 'a': ['בערך'], 'en': 'It cost about two hundred shekels.'},
       ]},
      {'kind': 'slang', 'he': 'דווקא', 'literal': 'from Aramaic דַּוְקָא, “precisely”',
       'meaning': 'Precisely the opposite of what you assumed — and, of a person, on purpose.',
       'when': 'It has no English word. Israeli children accuse each other of doing something '
               'דווקא, and an adult who says the film was דווקא טוב is saying they expected '
               'to dislike it. If you learn one word from this unit, this is it.',
       'examples': [{'he': 'דווקא נהניתי, לא ציפיתי.', 'en': 'I actually enjoyed it, which I hadn’t expected.'},
                    {'he': 'אל תעשה לי דווקא.', 'en': 'Don’t do it just to spite me.'}]},
    ],
  },
  {
    'id': 'he-84', 'n': 84, 'level': 'intermediate',
    'title': {'he': 'חיבה', 'en': 'Small words for people you like'},
    'objective': 'Hebrew makes things affectionate by shrinking them, doubling them or borrowing '
                 'a Yiddish ending — and the result is used between adults far more freely than '
                 'English allows.',
    'blocks': [
      {'kind': 'teach', 'title': 'Three ways to make a word smaller',
       'body': 'Double the last syllable: <b>כלב</b> → <b>כלבלב</b>, <b>חתול</b> → '
               '<b>חתלתול</b>, <b>קטן</b> → <b>קטנטן</b>. Add the Yiddish <b>ל־</b>: '
               'חיים → <b>חיימ\'ל</b>, and it is used with names among family. Or use a word '
               'that is affectionate by itself: <b>מותק</b>, <b>נשמה</b>, <b>חמוד</b>, '
               '<b>יקירי</b>. Note that <b>נשמה</b> — literally "soul" — is said to friends, '
               'shopkeepers and strangers, and carries no romance at all.',
       'examples': [
         {'he': 'תודה נשמה, אתה מציל אותי.', 'en': 'Thanks love, you’re saving me.'},
         {'he': 'איזה כלבלב חמוד!', 'en': 'What a sweet little dog!'},
         {'he': 'בוקר טוב, מותק.', 'en': 'Good morning, sweetheart.'},
         {'he': 'הוא ילד קטנטן, בן שנתיים.', 'en': 'He’s a tiny boy, two years old.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'חמוד', 'en': 'cute, sweet', 'pos': 'adj'},
         {'he': 'קטנטן', 'en': 'tiny', 'pos': 'adj'},
         {'he': 'כלבלב', 'en': 'puppy', 'pos': 'noun'},
         {'he': 'חתלתול', 'en': 'kitten', 'pos': 'noun'},
         {'he': 'נשמה', 'en': 'soul; used as a term of affection', 'pos': 'noun'},
         {'he': 'מותק', 'en': 'sweetie', 'pos': 'noun'},
         {'he': 'תינוק', 'en': 'baby', 'pos': 'noun'},
         {'he': 'לחבק', 'en': 'to hug', 'pos': 'verb'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'כלבלב', 'en': 'puppy — כלב doubled'},
         {'he': 'חתלתול', 'en': 'kitten — חתול doubled'},
         {'he': 'קטנטן', 'en': 'tiny — קטן doubled'},
         {'he': 'נשמה', 'en': 'love, dear — literally “soul”'},
         {'he': 'מותק', 'en': 'sweetie — literally “sweetness”'},
         {'he': 'חמוד', 'en': 'cute'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the affectionate word.',
       'example': {'q': 'איזה ___ חמוד! — puppy', 'a': 'כלבלב'},
       'items': [
         {'q': 'תודה ___, אתה מציל אותי.', 'a': ['נשמה'], 'en': 'Thanks love, you’re saving me.'},
         {'q': 'בוקר טוב, ___.', 'a': ['מותק'], 'en': 'Good morning, sweetheart.'},
         {'q': 'הוא ילד ___, בן שנתיים.', 'a': ['קטנטן'], 'en': 'He’s a tiny boy, two years old.'},
         {'q': 'איזה ___ הילדה הזאת!', 'a': ['חמודה'], 'en': 'What a sweet girl!'},
         {'q': 'ה___ ישן כל הלילה.', 'a': ['תינוק'], 'en': 'The baby slept all night.'},
       ]},
      {'kind': 'slang', 'he': 'נשמה', 'literal': '“soul”',
       'meaning': 'Love, mate, dear — to almost anyone.',
       'when': 'A shopkeeper says it to you. A friend says it to you. It is warm and completely '
               'unromantic, and an English speaker who hears "soul" and reads intimacy into it '
               'will misjudge a lot of conversations.',
       'examples': [{'he': 'תודה נשמה!', 'en': 'Thanks, love!'},
                    {'he': 'נשמה, יש לך רגע?', 'en': 'Mate, do you have a minute?'}]},
    ],
  },
  {
    'id': 'he-85', 'n': 85, 'level': 'intermediate',
    'title': {'he': 'אירועי חיים', 'en': 'Weddings, births and funerals'},
    'objective': 'What you say at each. These are fixed phrases with no room for improvisation, '
                 'and getting one wrong is the kind of mistake people remember.',
    'blocks': [
      {'kind': 'teach', 'title': 'A phrase for each occasion',
       'body': 'A wedding, a birth, an exam passed, a new flat: <b>מזל טוב</b>, and for the '
               'parents at a birth, <b>בשעה טובה</b>. For a death, the phrase on hearing the '
               'news is <b>ברוך דיין האמת</b>, and to the family you say '
               '<b>שלא תדעו עוד צער</b> or simply <b>אני משתתף בצערכם</b>. During the week of '
               'mourning — <b>שבעה</b> — people come to the house without being invited, and '
               'that is the expected thing rather than an intrusion.',
       'examples': [
         {'he': 'מזל טוב! שתהיה שעה טובה.', 'en': 'Congratulations! May it be at a good hour.'},
         {'he': 'הזמינו אותנו לחתונה בקיץ.', 'en': 'They invited us to the wedding in the summer.'},
         {'he': 'אני משתתף בצערכם.', 'en': 'My condolences.'},
         {'he': 'הלכנו לנחם אותם בשבעה.', 'en': 'We went to comfort them during the shiva.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'חתונה', 'en': 'wedding', 'pos': 'noun'},
         {'he': 'כלה', 'en': 'bride', 'pos': 'noun'},
         {'he': 'חתן', 'en': 'groom', 'pos': 'noun'},
         {'he': 'להיוולד', 'en': 'to be born', 'pos': 'verb'},
         {'he': 'לוויה', 'en': 'funeral', 'pos': 'noun'},
         {'he': 'אבל', 'en': 'mourning', 'pos': 'noun'},
         {'he': 'צער', 'en': 'sorrow', 'pos': 'noun'},
         {'he': 'לנחם', 'en': 'to comfort', 'pos': 'verb'},
       ]},
      {'kind': 'match', 'title': 'התאימו ברכה לאירוע', 'en': 'Match the phrase to the occasion',
       'instructions': 'Tap the Hebrew, then when you say it.',
       'pairs': [
         {'he': 'מזל טוב', 'en': 'a wedding, a birth, an exam passed'},
         {'he': 'בשעה טובה', 'en': 'to expectant parents, and at a birth'},
         {'he': 'ברוך דיין האמת', 'en': 'on first hearing that someone has died'},
         {'he': 'אני משתתף בצערכם', 'en': 'to the family of someone who has died'},
         {'he': 'תתחדש', 'en': 'to someone with something new — a car, a haircut'},
         {'he': 'לחיים', 'en': 'raising a glass'},
       ]},
      {'kind': 'choose', 'title': 'מה אומרים?', 'en': 'What do you say?',
       'instructions': 'One phrase per occasion, and they do not swap.',
       'items': [
         {'q': 'A colleague has just had a baby.',
          'options': ['מזל טוב, בשעה טובה', 'תתחדש', 'שיהיה בהצלחה'],
          'a': 'מזל טוב, בשעה טובה', 'en': 'Both, together, is the standard.'},
         {'q': 'A friend tells you their grandmother has died.',
          'options': ['ברוך דיין האמת', 'מזל טוב', 'שיהיה בהצלחה'],
          'a': 'ברוך דיין האמת', 'en': 'Said on hearing the news, by religious and secular alike.'},
         {'q': 'A neighbour shows you their new car.',
          'options': ['תתחדש!', 'מזל טוב', 'בשעה טובה'],
          'a': 'תתחדש!', 'en': '“May you be renewed” — for anything new you own or wear.'},
         {'q': 'Before someone sits an exam.',
          'options': ['בהצלחה', 'מזל טוב', 'תתחדש'],
          'a': 'בהצלחה', 'en': 'Congratulations come afterwards, never before.'},
       ]},
      {'kind': 'slang', 'he': 'תתחדש', 'literal': '“may you be renewed”',
       'meaning': 'Said to someone with something new.',
       'when': 'New shoes, a new car, a haircut, a new job. There is no English equivalent and '
               'not saying it when a friend is obviously showing you something new is a small '
               'visible gap.',
       'examples': [{'he': 'נעליים חדשות? תתחדש!', 'en': 'New shoes? Enjoy them!'},
                    {'he': 'תתחדשי על הדירה.', 'en': 'Congratulations on the new flat.'}]},
    ],
  },
  {
    'id': 'he-86', 'n': 86, 'level': 'beginner',
    'title': {'he': 'ילדים', 'en': 'Children'},
    'objective': 'The kindergarten, the pick-up, the nap and the tantrum. A vocabulary you need '
                 'entirely and suddenly, and one that fills a great deal of everyday '
                 'conversation whether or not you have children yourself.',
    'blocks': [
      {'kind': 'teach', 'title': 'The words parents use all day',
       'body': 'A nursery is a <b>מעון</b>, a kindergarten a <b>גן</b> — and the person who runs '
               'it is a <b>גננת</b>. To pick up is <b>לאסוף</b>. A nap is <b>שנת צהריים</b>. '
               'Israelis ask <b>בן כמה הוא?</b> — "how old is he", literally "a son of how '
               'much" — and the answer uses <b>בן</b> or <b>בת</b>: <b>בן שלוש</b>, '
               '<b>בת חמש</b>.',
       'examples': [
         {'he': 'צריך לאסוף את הילדים מהגן בארבע.', 'en': 'The children have to be picked up from kindergarten at four.'},
         {'he': 'בן כמה הוא? — בן שלוש.', 'en': 'How old is he? — Three.'},
         {'he': 'התינוקת ישנה עכשיו.', 'en': 'The baby is asleep now.'},
         {'he': 'הוא לא רוצה לאכול בכלל.', 'en': 'He won’t eat at all.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'תינוק', 'en': 'baby', 'pos': 'noun'},
         {'he': 'גן', 'en': 'kindergarten; a garden', 'pos': 'noun'},
         {'he': 'הורים', 'en': 'parents', 'pos': 'noun'},
         {'he': 'לגדל', 'en': 'to raise, to grow', 'pos': 'verb'},
         {'he': 'לאסוף', 'en': 'to collect, to pick up', 'pos': 'verb'},
         {'he': 'משחק', 'en': 'a game; playing', 'pos': 'noun'},
         {'he': 'צעצוע', 'en': 'toy', 'pos': 'noun'},
         {'he': 'לבכות', 'en': 'to cry', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'צריך ___ אותם מהגן. — to pick up', 'a': 'לאסוף'},
       'items': [
         {'q': '___ כמה הוא? בן שלוש.', 'a': ['בן'], 'en': 'How old is he? Three.'},
         {'q': 'ה___ ישן עכשיו, בשקט.', 'a': ['תינוק'], 'en': 'The baby’s asleep now, quietly.'},
         {'q': 'הילדים ב___ עד ארבע.', 'a': ['גן'], 'en': 'The children are at kindergarten until four.'},
         {'q': 'הוא ___ כי הוא עייף.', 'a': ['בוכה'], 'en': 'He’s crying because he’s tired.'},
         {'q': 'קניתי לו ___ ליום ההולדת.', 'a': ['צעצוע'], 'en': 'I bought him a toy for his birthday.'},
       ]},
      {'kind': 'choose', 'title': 'מה אומרים?', 'en': 'What do you say?',
       'instructions': 'Pick the Hebrew a parent would actually use.',
       'items': [
         {'q': 'Asking a stranger how old their child is.',
          'options': ['בן כמה הוא?', 'כמה שנים הוא?', 'איזה גיל?'], 'a': 'בן כמה הוא?',
          'en': 'Literally “a son of how much” — the standard form.'},
         {'q': 'Saying your daughter is five.',
          'options': ['היא בת חמש', 'היא חמש שנים', 'יש לה חמש'], 'a': 'היא בת חמש',
          'en': 'בן / בת plus the number, and the number is feminine here.'},
         {'q': 'Telling someone you’ll be a bit late for pick-up.',
          'options': ['אני קצת מאחר לאסוף', 'אני לא בא', 'תחכו לי'],
          'a': 'אני קצת מאחר לאסוף', 'en': 'The verb for pick-up is לאסוף.'},
       ]},
      {'kind': 'slang', 'he': 'בן כמה?', 'literal': '“a son of how much?”',
       'meaning': 'How old is he?',
       'when': 'The whole age system runs on בן and בת: אני בן שלושים, היא בת עשרים. It is not '
               'only for children, and there is no other way to say it.',
       'examples': [{'he': 'בת כמה את?', 'en': 'How old are you?'},
                    {'he': 'אני בן ארבעים ואחת.', 'en': 'I’m forty-one.'}]},
    ],
  },
  {
    'id': 'he-87', 'n': 87, 'level': 'beginner',
    'title': {'he': 'ספורט ופנאי', 'en': 'Sport and free time'},
    'objective': 'What you do at the weekend, and the football that half of every casual '
                 'conversation with a stranger is made of.',
    'blocks': [
      {'kind': 'teach', 'title': 'The verb is לשחק, except when it is not',
       'body': 'You <b>משחק</b> a game — כדורגל, כדורסל, שחמט. But you do NOT play a swim or a '
               'run: it is <b>שוחה</b>, <b>רץ</b>, <b>רוכב על אופניים</b>. Going to the gym is '
               '<b>להתאמן</b>, and a training session is an <b>אימון</b>. The football team you '
               'support is what a stranger will ask about: <b>באיזו קבוצה אתה?</b>',
       'examples': [
         {'he': 'אני משחק כדורגל בשישי.', 'en': 'I play football on Fridays.'},
         {'he': 'היא שוחה בבריכה כל בוקר.', 'en': 'She swims in the pool every morning.'},
         {'he': 'אני מתאמן שלוש פעמים בשבוע.', 'en': 'I train three times a week.'},
         {'he': 'ראית את המשחק אתמול?', 'en': 'Did you see the match yesterday?'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'ספורט', 'en': 'sport', 'pos': 'noun'},
         {'he': 'כדורגל', 'en': 'football', 'pos': 'noun'},
         {'he': 'כדורסל', 'en': 'basketball', 'pos': 'noun'},
         {'he': 'בריכה', 'en': 'pool', 'pos': 'noun'},
         {'he': 'קבוצה', 'en': 'team, group', 'pos': 'noun'},
         {'he': 'אימון', 'en': 'training session', 'pos': 'noun'},
         {'he': 'לשחות', 'en': 'to swim', 'pos': 'verb'},
         {'he': 'להתאמן', 'en': 'to train, to work out', 'pos': 'verb'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word — and mind which verb goes with which sport.',
       'example': {'q': 'אני ___ כדורגל בשישי. — play', 'a': 'משחק'},
       'items': [
         {'q': 'היא ___ בבריכה כל בוקר.', 'a': ['שוחה'], 'en': 'She swims in the pool every morning.'},
         {'q': 'אני ___ שלוש פעמים בשבוע.', 'a': ['מתאמן', 'מתאמנת'], 'en': 'I train three times a week.'},
         {'q': 'ראית את ה___ אתמול?', 'a': ['משחק'], 'en': 'Did you see the match yesterday?'},
         {'q': 'באיזו ___ אתה?', 'a': ['קבוצה'], 'en': 'Which team do you support?'},
         {'q': 'הוא ___ על אופניים לעבודה.', 'a': ['רוכב'], 'en': 'He cycles to work.'},
       ]},
      {'kind': 'match', 'title': 'התאימו', 'en': 'Match them up',
       'instructions': 'Tap the Hebrew, then the English.',
       'pairs': [
         {'he': 'לשחק כדורגל', 'en': 'to play football'},
         {'he': 'לשחות בבריכה', 'en': 'to swim in the pool'},
         {'he': 'לרוץ בפארק', 'en': 'to run in the park'},
         {'he': 'להתאמן בחדר כושר', 'en': 'to work out at the gym'},
         {'he': 'לרכוב על אופניים', 'en': 'to ride a bike'},
         {'he': 'לראות משחק', 'en': 'to watch a match'},
       ]},
      {'kind': 'slang', 'he': 'איזה משחק!', 'literal': '“what a game!”',
       'meaning': 'What a match — and, of a person, what a performance.',
       'when': 'איזה plus a noun is the standard Hebrew exclamation and works for anything: '
               'איזה יום, איזה בלגן, איזה כיף. It is the single most useful exclamation frame '
               'in the language.',
       'examples': [{'he': 'איזה כיף, סוף סוף חופש.', 'en': 'What fun — a holiday at last.'},
                    {'he': 'איזה בלגן פה!', 'en': 'What a mess in here!'}]},
    ],
  },
  {
    'id': 'he-88', 'n': 88, 'level': 'advanced',
    'title': {'he': 'שירות לקוחות', 'en': 'On the phone to a company'},
    'objective': 'Cancelling, complaining and being transferred. The hardest listening in the '
                 'language — fast, scripted, no face — and it runs on a small set of sentences '
                 'you can prepare.',
    'blocks': [
      {'kind': 'teach', 'title': 'Get to the sentence that moves you forward',
       'body': 'You will hear <b>רגע, אני מעביר אותך</b> and <b>נציג יענה לך בעוד…</b>. The '
               'things you need to say are short and fixed: <b>אני רוצה לבטל את המנוי</b>, '
               '<b>יש לי בעיה עם החשבון</b>, <b>אפשר לדבר עם מישהו אחר?</b>. Two words carry '
               'more weight than any argument: <b>תלונה</b> — a formal complaint — and '
               '<b>מנהל</b>. And <b>אני מבקש את זה בכתב</b> ends most disputes.',
       'examples': [
         {'he': 'שלום, אני רוצה לבטל את המנוי.', 'en': 'Hello, I’d like to cancel the subscription.'},
         {'he': 'יש לי בעיה עם החשבון של החודש.', 'en': 'I have a problem with this month’s bill.'},
         {'he': 'אפשר לדבר עם מנהל, בבקשה?', 'en': 'Could I speak to a manager, please?'},
         {'he': 'אני מבקש לקבל את זה בכתב.', 'en': 'I’d like to have that in writing.'},
       ]},
      {'kind': 'vocab', 'title': 'מילים חדשות',
       'rows': [
         {'he': 'שירות', 'en': 'service', 'pos': 'noun'},
         {'he': 'לקוח', 'en': 'customer', 'pos': 'noun'},
         {'he': 'נציג', 'en': 'representative, agent', 'pos': 'noun'},
         {'he': 'תלונה', 'en': 'complaint', 'pos': 'noun'},
         {'he': 'מנוי', 'en': 'subscription', 'pos': 'noun'},
         {'he': 'לבטל', 'en': 'to cancel', 'pos': 'verb'},
         {'he': 'להמתין', 'en': 'to wait (formal)', 'pos': 'verb'},
         {'he': 'לטפל', 'en': 'to handle — לטפל ב', 'pos': 'verb'},
       ]},
      {'kind': 'choose', 'title': 'מה אומרים?', 'en': 'What do you say?',
       'instructions': 'Pick the sentence that actually moves the call forward.',
       'items': [
         {'q': 'You have been on hold twenty minutes.',
          'options': ['אני ממתין כבר עשרים דקות', 'זה נורא', 'למה זה לוקח כל כך הרבה?'],
          'a': 'אני ממתין כבר עשרים דקות', 'en': 'State the fact; it is what gets logged.'},
         {'q': 'The agent cannot help and you want someone senior.',
          'options': ['אפשר לדבר עם מנהל?', 'אתה לא מבין', 'תעביר אותי'],
          'a': 'אפשר לדבר עם מנהל?', 'en': 'Polite, specific, and it is a request they are trained to answer.'},
         {'q': 'You want the answer recorded.',
          'options': ['אפשר לקבל את זה בכתב?', 'תזכור מה אמרת', 'אני מקליט'],
          'a': 'אפשר לקבל את זה בכתב?', 'en': 'The single most useful sentence in Israeli bureaucracy.'},
         {'q': 'You are cancelling and being offered a discount instead.',
          'options': ['תודה, אבל אני רוצה לבטל', 'אולי', 'כמה?'],
          'a': 'תודה, אבל אני רוצה לבטל', 'en': 'Repeat the request unchanged; it is the expected move.'},
       ]},
      {'kind': 'fill', 'title': 'השלימו', 'en': 'Fill in the gap',
       'instructions': 'Type the missing word.',
       'example': {'q': 'אני רוצה ___ את המנוי. — to cancel', 'a': 'לבטל'},
       'items': [
         {'q': 'יש לי ___ עם החשבון של החודש.', 'a': ['בעיה'], 'en': 'I have a problem with this month’s bill.'},
         {'q': 'אני רוצה להגיש ___.', 'a': ['תלונה'], 'en': 'I want to make a complaint.'},
         {'q': 'ה___ אמר שהוא יטפל בזה.', 'a': ['נציג'], 'en': 'The agent said he’d deal with it.'},
         {'q': 'אפשר לקבל את זה ___?', 'a': ['בכתב'], 'en': 'Could I have that in writing?'},
         {'q': 'אני ___ כבר עשרים דקות.', 'a': ['ממתין', 'ממתינה'], 'en': 'I’ve been holding for twenty minutes.'},
       ]},
      {'kind': 'slang', 'he': 'תעביר אותי לנציג', 'literal': '“transfer me to a representative”',
       'meaning': 'Get me a human.',
       'when': 'Said to the recorded menu, out loud, by everyone. Israeli phone systems listen '
               'for it, and so, eventually, do the people. נציג is the word — not עובד, not '
               'איש.',
       'examples': [{'he': 'נציג! תעביר אותי לנציג.', 'en': 'Agent! Put me through to an agent.'},
                    {'he': 'הנציג יענה בעוד שתי דקות.', 'en': 'An agent will answer in two minutes.'}]},
    ],
  },
]


# The entry point stays at the very BOTTOM: the units are appended to UNITS by module-level
# statements below the builder, and a guard placed above them runs main() -- and exits -- before
# they have executed. Eight units built where sixteen were written, and nothing said so.
if __name__ == '__main__':
    raise SystemExit(main())
