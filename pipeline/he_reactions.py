#!/usr/bin/env python3
"""Build texts/he/reactions.json — Phase-1 Hebrew conversational reflexes.

Reactions are the one kind of content that cannot be looked up whole: no lexicon records that
אֵין מַצָּב is what an Israeli says when they don't believe you. What CAN be checked is every
word of it, and that is what this does. The phrases and their categories are curated teaching;
the POINTING is then verified letter for letter against the lexicon, word by word, and anything
the lexicon will not confirm is flagged in the artifact rather than quietly shipped.

That is a weaker claim than the Sounds module makes and it is stated as one. Sounds asks the
lexicon for its words; this tells the lexicon what it wrote and asks whether that is a real
form. The app shows the difference: a phrase every word of which checks out gets the lexicon
mark, and one with a word the lexicon has never seen -- וואו, יאללה, תכל'ס, the borrowings that
are exactly what people actually say -- keeps the "not native-checked" flag.

    python3 pipeline/he_reactions.py --lang he      # writes texts/he/reactions.json
    python3 pipeline/reactions.py --lang he         # -> app/data/he/reactions.js
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')

from build_lex import he_norm                  # noqa: E402
from lex import Lexicon, MATRES                # noqa: E402
from phon import clusters, phon, respell, unpoint   # noqa: E402
import he_ingest                               # noqa: E402

OUT = paths.texts('reactions.json')

CATS = [
 ('surprise', 'Surprise & disbelief', 'הַפְתָּעָה',
  "Really?! No way. The reactions that show you're following — and a little amazed."),
 ('agree', 'Agreement & confirmation', 'הַסְכָּמָה',
  "Exactly, sure, obviously. The 'I'm with you' chunks that keep a conversation moving."),
 ('sympathy', 'Sympathy & care', 'אַהֲדָה',
  "What a shame, never mind, get well. What you say when someone is having a hard time."),
 ('praise', 'Praise & evaluation', 'שֶׁבַח',
  'Nice, excellent, well done. Reacting to food, a photo, a story — you need these hourly.'),
 ('hedge', 'Hedging & uncertainty', 'הִסּוּס',
  "Maybe, depends, something like that. How to not commit, which is most of real speech."),
 ('glue', 'Conversation glue', 'מִלּוֹת קֶשֶׁר',
  'So, anyway, hold on, listen. The little words that hold turns together.'),
 ('table', 'At the table', 'לְיַד הַשֻּׁלְחָן',
  "Bon appétit, cheers, I'm full. The Shabbat-table set, and the one this app is aiming at."),
 ('blessing', 'Blessings & wishes', 'בְּרָכוֹת',
  'Good luck, congratulations, Shabbat shalom. Hebrew runs on these.'),
]

# (category, POINTED phrase, English, when you say it, optional reply)
ITEMS = [
 ('surprise', 'בֶּאֱמֶת?', 'Really?', 'The everyday one. Rising tone.', None),
 ('surprise', 'בִּרְצִינוּת?', 'Seriously?', 'A shade more incredulous than באמת.', None),
 ('surprise', 'אֵין מַצָּב!', 'No way!', 'Literally "there is no situation". Disbelief, not refusal.', None),
 ('surprise', 'מָה פִּתְאוֹם!', 'What?! Come off it!', 'Literally "what suddenly" — rejects the premise, not the fact.', None),
 ('surprise', 'לֹא יֵאָמֵן!', 'Unbelievable!', 'For genuinely astonishing news, good or bad.', None),
 ('surprise', 'מָה אַתָּה אוֹמֵר!', "You don't say!", 'To a man; to a woman, מה את אומרת.', None),
 ('surprise', 'וַואו!', 'Wow!', 'Borrowed, and said constantly.', None),

 ('agree', 'בְּדִיּוּק', 'Exactly', 'The single most useful agreement token.', None),
 ('agree', 'נָכוֹן', 'Right / true', 'Confirms a fact rather than an opinion.', None),
 ('agree', 'בֶּטַח', 'Sure, of course', 'Warm and casual.', None),
 ('agree', 'בָּרוּר', 'Obviously', 'Literally "clear". Agreement with a shrug.', None),
 ('agree', 'אֵין בְּעָיָה', 'No problem', 'Accepting a request.', None),
 ('agree', 'כַּמּוּבָן', 'Of course', 'The polite, slightly formal one.', None),
 ('agree', 'בְּהֶחְלֵט', 'Absolutely', 'Emphatic agreement.', None),
 ('agree', 'סַבַּבָּה', 'Cool, fine', 'Borrowed from Arabic صبابة and everywhere in Israeli speech.', None),

 ('sympathy', 'חֲבָל', 'What a shame', 'The all-purpose sympathy word.', None),
 ('sympathy', 'אוֹי', 'Oy', 'Small dismay. Doubles as an opener for bad news.', None),
 ('sympathy', 'מִסְכֵּן', 'Poor thing', 'To or about a man; מסכנה about a woman.', None),
 ('sympathy', 'לֹא נוֹרָא', "Never mind, it's not that bad", 'Reassurance, and how you wave off an apology.', None),
 ('sympathy', 'תַּרְגִּישׁ טוֹב', 'Get well', 'To a man; תרגישי טוב to a woman.', 'תּוֹדָה'),
 ('sympathy', 'אֲנִי מִצְטַעֵר', "I'm sorry", 'A man speaking; a woman says אני מצטערת.', None),

 ('praise', 'יָפֶה מְאוֹד', 'Very nice', 'General approval, of a thing or of what someone did.', None),
 ('praise', 'מְעוּלֶה', 'Excellent', 'A notch above יפה.', None),
 ('praise', 'אַחְלָה', 'Great', 'Another Arabic borrowing, thoroughly at home.', None),
 ('praise', 'כָּל הַכָּבוֹד', 'Well done', 'Literally "all the honour". Said to a person, not a thing.', None),
 ('praise', 'מַדְהִים', 'Amazing', 'Strong praise; keeps its force.', None),
 ('praise', 'תַּעֲנוּג', 'A delight', 'Especially of food.', None),

 ('hedge', 'אוּלַי', 'Maybe', 'The plain one.', None),
 ('hedge', 'נִרְאֶה לִי', 'I think / it seems to me', 'Literally "it seems to me". Softens any claim.', None),
 ('hedge', 'לֹא בָּטוּחַ', 'Not sure', 'A man speaking; לא בטוחה from a woman.', None),
 ('hedge', 'תָּלוּי', 'It depends', 'A whole answer on its own.', None),
 ('hedge', 'בְּעֵרֶךְ', 'Roughly, about', 'Attaches to any number.', None),
 ('hedge', 'מַשֶּׁהוּ כָּזֶה', 'Something like that', 'Closes a vague description.', None),

 ('glue', 'אָז', 'So', 'Starts a turn, or resumes one.', None),
 ('glue', 'בְּקִצּוּר', 'In short', 'Signals you are about to land the point.', None),
 ('glue', 'כְּאִילּוּ', 'Like, sort of', 'The Israeli "like". Everywhere in speech.', None),
 ('glue', 'בְּכָל אוֹפֶן', 'Anyway', 'Returns to the thread after a digression.', None),
 ('glue', 'רֶגַע', 'Hold on', 'Literally "a moment". Interrupts politely.', None),
 ('glue', 'תִּשְׁמַע', 'Listen', 'To a man; תשמעי to a woman. Prefaces something real.', None),
 ('glue', 'יַאלְלָה', "Come on, let's go", 'Arabic again, and unavoidable.', None),
 ('glue', 'מָה נִשְׁמָע?', "How's it going?", 'Literally "what is heard". The standard greeting.', 'הַכֹּל טוֹב'),

 ('table', 'בְּתֵאָבוֹן', 'Bon appétit', 'Said as people start eating.', None),
 ('table', 'לְחַיִּים', 'Cheers', 'Literally "to life". Glasses up.', None),
 ('table', 'תּוֹדָה רַבָּה', 'Thank you very much', 'The full form; תודה alone is fine.', 'בְּבַקָּשָׁה'),
 ('table', 'בְּבַקָּשָׁה', "Please / here you go", 'Both asking and handing over.', None),
 ('table', 'עוֹד קְצָת?', 'A bit more?', 'Offering another helping.', None),
 ('table', 'אֲנִי שָׂבֵעַ', "I'm full", 'A man speaking; אני שבעה from a woman.', None),
 ('table', 'הָיָה טָעִים', 'It was delicious', 'The thing to say to whoever cooked.', None),

 ('blessing', 'בְּהַצְלָחָה', 'Good luck', 'Before an exam, an interview, anything.', None),
 ('blessing', 'מַזָּל טוֹב', 'Congratulations', 'Births, weddings, birthdays, a new job.', None),
 ('blessing', 'שַׁבָּת שָׁלוֹם', 'Shabbat shalom', 'From Friday morning through Saturday.', 'שַׁבָּת שָׁלוֹם'),
 ('blessing', 'חַג שָׂמֵחַ', 'Happy holiday', 'Any festival.', 'חַג שָׂמֵחַ'),
 ('blessing', 'לַבְּרִיאוּת', 'Bless you', 'After a sneeze. Literally "to health".', None),
 ('blessing', 'תִּתְחַדֵּשׁ', 'Enjoy the new one', 'Said about new clothes, a phone, a car. No English equivalent.', None),
]


def confirm(lx, tok):
    """Is this pointed word a real form? -> (ok, why not).

    The test is respell(): the lexicon's vowels, moved onto the spelling this file used, must
    come out as exactly the string it wrote. That accepts a pointing that is right but written
    full where the entry is defective -- אוֹפֶן against the entry's אֹפֶן, כְּאִילּוּ against
    כְּאִלּוּ -- and refuses one that is a different word wearing the same consonants, which is
    the failure that matters: אופן is also אוֹפַן "a wheel".

    Every candidate is tried, not just the first the reader's tiered lookup would settle on,
    because the phrase decides which word is meant and the lookup does not know the phrase. A
    proclitic is peeled first and only the stem is checked -- nothing in the lexicon points a
    particle, so its vowel here is ours and the artifact says so.
    """
    plain = he_norm(unpoint(tok))
    for stem, cut in lx.stems(plain):
        if cut and not cut.endswith('-'):
            continue                                   # suffix strips are a different question
        cl = clusters(tok)[len(cut) - 1 if cut else 0:]
        mine = ''.join(c + m for c, m in cl)
        sp = he_norm(unpoint(mine))
        if sp != stem:
            continue
        cands = (lx.by_form.get(sp) or []) + (lx.by_skeleton.get(MATRES.sub('', sp)) or [])
        for r in cands:
            f = str(r['FORM'])
            if f == mine or respell(unpoint(mine), f) == mine:
                return True, ''
    hit = lx._hit(plain) or lx.by_skeleton.get(MATRES.sub('', plain))
    if not hit:
        return False, 'not in the lexicon'
    if all(unpoint(str(r['FORM'])) == str(r['FORM']) for r in hit):
        return False, 'in the lexicon, but unpointed there'
    return False, 'the lexicon points it differently'


def main():
    lx = Lexicon()

    items, stats = [], {'lex': 0, 'flag': 0}
    for cat, he, en, use, reply in ITEMS:
        toks = he_ingest.tokenize(he)
        checks = {t: confirm(lx, t) for t in toks}
        unchecked = [t for t in toks if not checks[t][0]]
        prov = 'lex-corroborated' if not unchecked else 'needs-native-validation'
        stats['lex' if prov == 'lex-corroborated' else 'flag'] += 1
        it = {'cat': cat, 'ar': he, 'plain': unpoint(he).replace('?', ''),
              'tr': ' '.join(phon(t) for t in toks),
              'en': en, 'use': use, 'provenance': prov}
        if unchecked:
            it['unchecked'] = unchecked
            it['note'] = '; '.join('%s — %s' % (t, checks[t][1]) for t in unchecked)
        if reply:
            it['reply'] = reply
        items.append(it)

    doc = {
        'id': 'reactions-he', 'title': {'ar': 'תְּגוּבוֹת', 'en': 'Reactions'},
        'kind': 'reactions', 'dialect': 'he',
        'intro': 'The reflexes of a conversation — the short, automatic chunks that let you be a '
                 'real presence at a table long before you can build sentences. Grouped by the '
                 'job they do, so you can drill one at a time.',
        'rationale': 'Phase 1. Curated interjections, not lexicon entries: no dictionary records '
                     'that אין מצב is what you say when you do not believe someone.',
        'provenance_note': 'The phrases and the grouping are curated teaching and are NOT '
                           'native-checked. What is checked is the spelling: pipeline/'
                           'he_reactions.py verifies every pointed word against the lexicon and '
                           'flags any phrase containing one it cannot confirm. Romanization is '
                           'derived from the pointing by spike/he/phon.py.',
        'cats': [{'id': i, 'en': e, 'ar': a, 'blurb': b} for i, e, a, b in CATS],
        'items': items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%d reactions in %d categories · %d fully confirmed · %d flagged'
          % (len(items), len(CATS), stats['lex'], stats['flag']))
    for it in items:
        if it.get('unchecked'):
            print('   %-18s %-22s %s' % (it['ar'], ' '.join(it['unchecked']), it['note']))
    print('-> %s' % os.path.relpath(OUT, paths.ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
