"""Hand-curated Hebrew entries for what a lexicon legitimately doesn't contain.

The Hebrew half of pipeline/curated.py, under the same rule and the same discipline. English
Wiktionary's Hebrew is 12,662 lemmas -- a real dictionary, but a thin one -- and two classes of
word fall outside it on principle rather than by accident:

  1. FUNCTION   closed-class words and the inflected prepositions. Hebrew writes בֵּינֵיהֶם
                "among them" and כָּמוֹהוּ "like him" as single words, and no dictionary lists
                every person of every preposition. The class is finite and can be written down.
  2. PROPER     the names of people and places. גִּמְפֶּל, יְרַחְמִיאֵל, פִּינְסְקֶר. A name has no
                lexical entry anywhere; that is a fact about names, not a gap in the data.

AND NOTHING ELSE. The temptation here is the third class -- the ordinary content words this
lexicon happens to lack, אוֹלָר "pocketknife", דּוֹגֶרֶת "brooding hen", מִשְׂרָפוֹת "kilns" -- and
writing those by hand is exactly what the whole pipeline exists to prevent. A content word's
meaning has to be looked up or the app is teaching someone what we guessed. They stay
unresolved, and the word card says so, until a lexicon that has them is added.

Pronunciation is NOT curated: phon.py derives it from the pointing by the same rules that read
every other Hebrew word in the app. Only the stress is supplied here, and only where it is not
the Hebrew default of final -- that is the one thing the pointing does not determine.

The single exception is an abbreviation, whose letters are not the sounds it is read with:
ל"ג is said "lag" and ד"ר is said "doktor", and no transducer gets there from the letters. Those
carry their reading in the same slot the stress uses, and they are the only entries that may.

Every entry is marked `curated:*` in the artifact, so it is never mistaken for lexicon data.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
from build_lex import he_norm            # noqa: E402
from phon import phon_stressed           # noqa: E402

# key -> (pointed, gloss, analysis, stress-from-end). Stress defaults to 1, Hebrew's own default.

# Hebrew writes a preposition and its pronoun as one word, and inflects the whole closed class
# that way: בֵּין becomes בֵּינֵיהֶם, כְּמוֹ becomes כָּמוֹהוּ. Wiktionary lists the preposition and
# not its persons, so every one of these came back as no entry at all -- and the skeleton, asked
# to find something, offered בְּנֵיהֶם "their sons" for בֵּינֵיהֶם, which respell() then refused.
# They are written out rather than derived because the forms are irregular enough that a rule
# would be a guess (בֵּינֵי־, not בֵּינ־; כָּמוֹ־, not כְּמוֹ־).
FUNCTION = {
    'ביניהם':  ('בֵּינֵיהֶם', 'among them, between them', 'PREP+PRON_3MP'),
    'ביניהן':  ('בֵּינֵיהֶן', 'among them, between them (f.)', 'PREP+PRON_3FP'),
    'ביניכם':  ('בֵּינֵיכֶם', 'among you, between you (pl.)', 'PREP+PRON_2MP'),
    'בינינו':  ('בֵּינֵינוּ', 'among us, between us', 'PREP+PRON_1P'),
    'כמוהו':   ('כָּמוֹהוּ', 'like him, like it', 'PREP+PRON_3MS', 2),
    'כמוה':    ('כָּמוֹהָ', 'like her, like it', 'PREP+PRON_3FS', 2),
    'כמוך':    ('כָּמוֹךָ', 'like you (m.)', 'PREP+PRON_2MS', 2),
    'כמוני':   ('כָּמוֹנִי', 'like me', 'PREP+PRON_1S', 2),
    'כמוהם':   ('כְּמוֹהֶם', 'like them', 'PREP+PRON_3MP', 2),
    'עמהם':    ('עִמָּהֶם', 'with them', 'PREP+PRON_3MP'),
    'שתיהן':   ('שְׁתֵּיהֶן', 'both of them (f.), the two of them', 'NUM+PRON_3FP'),
    'שתיהם':   ('שְׁתֵּיהֶם', 'both of them, the two of them', 'NUM+PRON_3MP'),
    'שניהם':   ('שְׁנֵיהֶם', 'both of them, the two of them (m.)', 'NUM+PRON_3MP'),
    # Literary particles and adverbs. Everyday in a book of this age, absent from a lexicon
    # built on present-day usage.
    'אפוא':    ('אֵפוֹא', 'then, so (in that case)', 'ADV'),
    'שמא':     ('שֶׁמָּא', 'lest, in case, perhaps', 'CONJ'),
    # The reflexive pronouns. Wiktionary lemmatises עֶצֶם "bone/object" and stops there, so
    # every עַצְמוֹ in this corpus read as "his object" and every לְעַצְמוֹ as "to close one's
    # eyes" -- a plural imperative of a different verb. There is no entry to resolve TO.
    'עצמו':    ('עַצְמוֹ', 'himself, itself', 'PRON_REFL_3MS'),
    'עצמה':    ('עַצְמָהּ', 'herself, itself', 'PRON_REFL_3FS'),
    'עצמי':    ('עַצְמִי', 'myself', 'PRON_REFL_1S'),
    'עצמם':    ('עַצְמָם', 'themselves', 'PRON_REFL_3MP'),
    'עצמנו':   ('עַצְמֵנוּ', 'ourselves', 'PRON_REFL_1P'),
    # Same gap on the other side of מִן: the lexicon has מִמֶּנּוּ only as "from us", and the
    # spelling is identical for "from him", which is what it means on nearly every page here.
    'ממנו':    ('מִמֶּנּוּ', 'from him, from it (and, spelled the same way, from us)', 'PREP+PRON'),
    'אדות':    ('אֹדוֹת', 'concerning, about (usually עַל אֹדוֹת)', 'PREP'),
    'בינתים':  ('בֵּינָתַיִם', 'meanwhile, in the meantime', 'ADV', 2),
    'ממחרת':   ('מִמָּחֳרָת', 'the next day, on the morrow', 'ADV'),
    'הו':      ('הוֹ', 'oh! (a cry)', 'INTJ'),
    # Abbreviations, which are fixed expressions rather than words. A gershayim before the last
    # letter is what makes one; build_lex drops them from the lexicon on purpose, so the only
    # place they can be answered is here.
    'ד"ר':     ('ד"ר', 'Dr. (doctor)', 'ABBREV', 'dóktor'),
    'ל"ג':     ('ל"ג', 'Lag — the 33rd, as in Lag BaOmer', 'ABBREV', 'lag'),
    'ארה"ב':   ('ארה"ב', 'the USA', 'ABBREV', 'artsot habrit'),
    'ח"כ':     ('ח"כ', 'MK, member of the Knesset', 'ABBREV', 'xáver knéset'),
    'רע"מ':    ('רע"מ', 'Ra\u2019am (the United Arab List party)', 'ABBREV', 'rá\u2019am'),
    'שב"כ':    ('שב"כ', 'the Shin Bet (Israel\u2019s internal security service)', 'ABBREV', 'shabák'),
    # בָּהּ and בּוֹ are ב־ with a pronoun, the same closed class as בֵּינֵיהֶם above. Neither is in
    # Wiktionary, and בה was answered by the acronym ב״ה until build_lex stopped indexing those:
    # the daily paper said “baruch Hashem, thank God” where the sentence said “in it”.
    'בה':      ('בָּהּ', 'in it, in her', 'PREP+PRON_3FS'),
    # Four entries came back out after measuring what the table SHADOWS now that it is consulted
    # first: עִמָּהּ and עִמָּנוּ hid עַם "a nation", whose reading עַמֵּנוּ "our people" is just as
    # real; בּוֹ was already in Wiktionary and needed no help; and דָּן, the name, hid דָּן "to
    # discuss", which is what the word is in every sentence about a court. A curated name is only
    # safe where it is not also an ordinary word.
}

# Names. No lexicon carries these and none ever will: a name is not a word with a meaning, and
# the gloss says which name it is rather than what it means. These are the people, animals and
# places of the thirty-seven Ben-Yehuda chapters -- a character whose own name reads "not in the
# lexicon" is the first word a reader taps and the worst one to have nothing for.
PROPER = {
    'גמפל':     ('גִּמְפֶּל', 'Gimpel (a name)', 'NOUN_PROP', 2),
    'עמינדב':   ('עַמִּינָדָב', 'Amminadav (a name)', 'NOUN_PROP'),
    'ירחמיאל':  ('יְרַחְמִיאֵל', 'Yerachmiel (a name)', 'NOUN_PROP'),
    'גרשון':    ('גֵרְשׁוֹן', 'Gershon (a name)', 'NOUN_PROP'),
    'עשהאל':    ('עֲשָׂהאֵל', 'Asahel (a name)', 'NOUN_PROP'),
    "חיימ'ל":   ("חַיִּימְ'ל", "Chaim'l (an affectionate form of the name Chaim)", 'NOUN_PROP', 2),
    'אולה':     ('אוֹלָה', 'Ola (the name given to one of the shoes)', 'NOUN_PROP'),
    'הבהבה':    ('הַבְהֲבָה', 'Havhava (the dog, from הַב־הַב "woof woof")', 'NOUN_PROP'),
    'מיאה':     ('מְיָאָה', 'Meah (the cat, from her miaow)', 'NOUN_PROP'),
    'פינסקר':   ('פִּינְסְקֶר', 'Pinsker (Leon Pinsker, of the Lovers of Zion)', 'NOUN_PROP', 2),
    'הרצל':     ('הֶרְצֵל', 'Herzl (Theodor Herzl)', 'NOUN_PROP', 2),
    'נורדוי':   ('נוֹרְדוֹי', 'Nordau (Max Nordau)', 'NOUN_PROP', 2),
    'ליאון':    ('לֵיאוֹן', 'Leon (a name)', 'NOUN_PROP'),
    'מטץ':      ('מֶטְץ', 'Metz (a city in France)', 'NOUN_PROP'),
    # And the people and places the daily paper is full of. News is where this class bites: a
    # name has no lexical entry anywhere, so every one of these read “not in the lexicon” on
    # the word card, and two of them read as something else -- דן as “to discuss” and מנסור
    # as “to saw”.
    'טראמפ':    ('טְרַאמְפּ', 'Trump (Donald Trump)', 'NOUN_PROP'),
    'זלנסקי':   ('זֶלֶנְסְקִי', 'Zelensky (Volodymyr Zelensky)', 'NOUN_PROP', 2),
    'עבאס':     ('עַבַּאס', 'Abbas (a surname)', 'NOUN_PROP'),
    'מנסור':    ('מַנְסוּר', 'Mansour (a given name)', 'NOUN_PROP'),
    'דריסקול':  ('דְּרִיסְקוֹל', 'Driscoll (a surname)', 'NOUN_PROP', 2),
    'גמליאל':   ('גַּמְלִיאֵל', 'Gamliel (a surname)', 'NOUN_PROP'),
    'חאלד':     ('חָאלֶד', 'Khaled (a given name)', 'NOUN_PROP', 2),
    'טיימס':    ('טַיְמְס', 'Times (as in Times Square)', 'NOUN_PROP'),
    'סקוור':    ('סְקְוֵר', 'Square (as in Times Square)', 'NOUN_PROP'),
    'יורק':     ('יוֹרְק', 'York (as in New York)', 'NOUN_PROP'),
    'הורמוז':   ('הוֹרְמוּז', 'Hormuz (the strait between Iran and Oman)', 'NOUN_PROP'),
    # And the characters on the shelf. A retelling says its hero's name in every other
    # sentence, so one missing row is 254 unresolvable tokens rather than one.
    #
    # These carry their pronunciation as a STRING rather than a stress number, because
    # phon_stressed cannot read them: it has no rule for the geresh, and "ג'וּחָא" came back
    # as g'xa -- the j lost and the u with it. A borrowed name is exactly where a derived
    # pronunciation should not be trusted, so it is written out.
    "ג'וחא":    ("ג'וּחָא", 'Juha (Nasreddin, the wise fool of the folk tales)', 'NOUN_PROP', 'juxa'),
    # Around the World in Eighty Days. Two of these are why the table is consulted BEFORE the
    # lexicon rather than after it: פוג came back as פּוּג "to expire" and סן as a real word,
    # confidently, so a fallback would never have reached them -- nothing failed.
    'פוג':      ('פוֹג', 'Fogg (Phileas Fogg)', 'NOUN_PROP', 'fog'),
    'פספרטו':   ('פַּסְפַּרְטוּ', "Passepartout (Fogg's servant)", 'NOUN_PROP', 'paspartú'),
    'פיקס':     ('פִיקְס', 'Fix (the detective)', 'NOUN_PROP', 'fiks'),
    'אאודה':    ('אָאוּדָה', 'Aouda (the woman rescued in India)', 'NOUN_PROP', 'aúda'),
    'בומביי':   ('בּוֹמְבֵּיי', 'Bombay (Mumbai, in India)', 'NOUN_PROP', 'bombéy'),
    'כלכותה':   ('כַּלְכּוּתָּה', 'Calcutta (Kolkata, in India)', 'NOUN_PROP', 'kalkúta'),
    'הונג':     ('הוֹנְג', 'Hong (as in Hong Kong)', 'NOUN_PROP', 'hong'),
    'קונג':     ('קוֹנְג', 'Kong (as in Hong Kong)', 'NOUN_PROP', 'kong'),
    'יוקוהמה':  ('יוֹקוֹהָמָה', 'Yokohama (in Japan)', 'NOUN_PROP', 'yokoháma'),
    'סן':       ('סָן', 'San (as in San Francisco)', 'NOUN_PROP', 'san'),
    'פרנסיסקו': ('פְרַנְסִיסְקוֹ', 'Francisco (as in San Francisco)', 'NOUN_PROP', 'fransísko'),
    'ניו':      ('נְיוּ', 'New (as in New York)', 'NOUN_PROP', 'nyu'),
    # Wiktionary lemmatises צָרְפַת only as Zarephath, the Phoenician town in the book of
    # Kings. In Hebrew since the middle ages it has also been the ordinary word for France,
    # which is what it means every time it appears in this corpus.
    'צרפת':     ('צָרְפַת', 'France', 'NOUN_PROP', 2),
    'פיליאס':   ('פִילְיָאס', 'Phileas (Phileas Fogg)', 'NOUN_PROP', 'filias'),
    'סואץ':     ('סוּאֵץ', 'Suez (the canal and the city in Egypt)', 'NOUN_PROP', 'suéts'),
    # The seven voyages.
    'סינדבאד':  ('סִינְדְּבַּאד', 'Sindbad (the sailor of the Thousand and One Nights)', 'NOUN_PROP', 'sindbád'),
    'סרנדיב':   ('סֶרֶנְדִּיב', 'Serendib (the old name for Sri Lanka)', 'NOUN_PROP', 'serendív'),
    # Kalila and Dimna. Both jackals are ordinary Hebrew verbs when unpointed -- כלילה came
    # back as "to include" and דמנה as "to pause" -- so the two title characters would have
    # been glossed as conjugations of something else on every page of their own book.
    'כלילה':    ('כְּלִילָה', 'Kalila (one of the two jackals)', 'NOUN_PROP', 'klilá'),
    'דמנה':     ('דִּמְנָה', 'Dimna (the other of the two jackals)', 'NOUN_PROP', 'dimná'),
    # Treasure Island.
    "ג'ים":     ("ג'ים", 'Jim (Jim Hawkins, who tells the story)', 'NOUN_PROP', 'jim'),
    'הוקינס':   ('הוֹקִינְס', 'Hawkins (Jim Hawkins)', 'NOUN_PROP', 'hókins'),
    'סילבר':    ('סִילְבֶר', 'Silver (Long John Silver, the cook)', 'NOUN_PROP', 'sílver'),
    'פלינט':    ('פְלִינְט', 'Flint (the pirate captain who buried the treasure)', 'NOUN_PROP', 'flint'),
    'ליבסי':    ('לִיבְּסִי', 'Livesey (the doctor)', 'NOUN_PROP', 'lívsi'),
    'טרלוני':   ('טְרֶלוֹנִי', 'Trelawney (the squire)', 'NOUN_PROP', 'trelóni'),
    'סמולט':    ('סְמוֹלֶט', 'Smollett (the captain of the ship)', 'NOUN_PROP', 'smólet'),
    'בילי':     ('בִּילִי', 'Billy (Billy Bones, the old sailor)', 'NOUN_PROP', 'bíli'),
    'בונס':     ('בּוֹנְס', 'Bones (Billy Bones)', 'NOUN_PROP', 'bons'),
    'גאן':      ('גָּאן', 'Gunn (Ben Gunn, the man left on the island)', 'NOUN_PROP', 'gan'),
    'בריסטול':  ('בְּרִיסְטוֹל', 'Bristol (the English port)', 'NOUN_PROP', 'brístol'),
    "ג'ון":     ("ג'ון", 'John (Long John Silver)', 'NOUN_PROP', 'jon'),
    # Tom Sawyer.
    'טום':      ('טוֹם', 'Tom (Tom Sawyer)', 'NOUN_PROP', 'tom'),
    'סוייר':    ('סוֹיֶיר', 'Sawyer (Tom Sawyer)', 'NOUN_PROP', 'sóyer'),
    'האק':      ('הָאק', 'Huck (Huckleberry Finn)', 'NOUN_PROP', 'hak'),
    'בקי':      ('בֶּקִי', 'Becky (Becky Thatcher)', 'NOUN_PROP', 'béki'),
    'פולי':     ('פּוֹלִי', "Polly (Tom's aunt)", 'NOUN_PROP', 'póli'),
    "ג'ו":      ("ג'ו", "Joe (Injun Joe, and also Tom's friend Joe Harper)", 'NOUN_PROP', 'jo'),
    'פוטר':     ('פּוֹטֶר', 'Potter (Muff Potter)', 'NOUN_PROP', 'póter'),
    'מיסיסיפי': ('מִיסִיסִיפִּי', 'Mississippi (the river)', 'NOUN_PROP', 'misisípi'),
    # WITHDRAWN, and the reason belongs next to the table rather than in a commit message,
    # because it is the standing hazard of this file. A curated row is consulted BEFORE the
    # lexicon, so a name that is also an ordinary Hebrew string does not merely fail to help --
    # it overwrites a correct answer that was already there. Measured across the whole Hebrew
    # corpus, four of these were doing exactly that:
    #   פין   (Finn)  shadowed פִּינָּה "corner" via the clitic peeler -- four texts
    #   בצרה  (Basra) shadowed בְּצָרָה "in trouble"
    #   מאף   (Muff)  shadowed מֵאַף אֶחָד "from anyone", and מֵאַף "from a nose"
    #   סיד   (Sid)   shadowed סִיד "lime, plaster" -- and was never used in the book at all
    # The books were reworded instead: Huck goes by האק, Sindbad sails from the port, and
    # Potter goes by his surname. A name that cannot be spelled without stepping on a word is
    # not worth the word.
    # Sherlock Holmes.
    'שרלוק':    ('שֶׁרְלוֹק', 'Sherlock (Sherlock Holmes)', 'NOUN_PROP', 'sherlók'),
    'הולמס':    ('הוֹלְמְס', 'Holmes (Sherlock Holmes)', 'NOUN_PROP', 'hólms'),
    'ווטסון':   ('וָוטְסוֹן', 'Watson (Doctor Watson, who tells the stories)', 'NOUN_PROP', 'vátson'),
    'לסטרייד':  ('לֶסְטְרֵייד', 'Lestrade (the police inspector)', 'NOUN_PROP', 'lestréyd'),
    'מוריארטי': ('מוֹרִיאַרְטִי', 'Moriarty (Holmes’s enemy)', 'NOUN_PROP', 'moriárti'),
    'בייקר':    ('בֵּייקֶר', 'Baker (as in Baker Street)', 'NOUN_PROP', 'béyker'),
    'אירן':     ('אִירֶן', 'Irene (Irene Adler)', 'NOUN_PROP', 'íren'),
    'אדלר':     ('אַדְלֶר', 'Adler (Irene Adler)', 'NOUN_PROP', 'ádler'),
    'ריכנבאך':  ('רַיְכֶנְבַּאך', 'Reichenbach (the waterfall in Switzerland)', 'NOUN_PROP', 'raykhenbákh'),
    'נפוליאון': ('נָפּוֹלֵיאוֹן', 'Napoleon (Napoleon Bonaparte)', 'NOUN_PROP', 'napoleón'),
    'בוהמיה':   ('בּוֹהֶמְיָה', 'Bohemia (the kingdom, now part of the Czech Republic)', 'NOUN_PROP', 'bohémya'),
    'שווייץ':   ('שְׁוַויְץ', 'Switzerland', 'NOUN_PROP', 'shvayts'),
    # Maupassant and Chekhov.
    "ז'ול":     ("ז'ול", 'Jules (the uncle in the Maupassant story)', 'NOUN_PROP', 'zhul'),
    'ואנקה':    ('וָואנְקָה', 'Vanka (the boy in the Chekhov story)', 'NOUN_PROP', 'vánka'),
    'נורמנדי':  ('נוֹרְמַנְדִּי', 'Normandy (in northern France)', 'NOUN_PROP', 'normándi'),
    # Second-edition Treasure Island (2026-09-04): the twins now carry the whole cast.
    'הנדס':     ('הֶנְדְס', 'Hands (Israel Hands, the coxswain)', 'NOUN_PROP', 'hends'),
    'היספניולה': ('הִיסְפָּנְיוֹלָה', 'Hispaniola (the ship)', 'NOUN_PROP', 'hispanyóla'),
    'גריי':     ('גְּרֵיי', 'Gray (Abraham Gray, the sailor who stayed loyal)', 'NOUN_PROP', 'grey'),
    "ג'ורג'":   ("ג'וֹרְג'", 'George (George Merry, one of the pirates)', 'NOUN_PROP', 'jorj'),
    "ג'ורג":    ("ג'וֹרְג'", 'George (George Merry, one of the pirates)', 'NOUN_PROP', 'jorj'),
    'אלן':      ('אָלָן', 'Alan (a sailor)', 'NOUN_PROP', 'álan'),
    'הארי':     ('הָארִי', 'Harry (a sailor)', 'NOUN_PROP', 'hári'),
}

_ALL = {}


def _index():
    for src, tag in ((FUNCTION, 'function-word'), (PROPER, 'proper-noun')):
        for k, v in src.items():
            _ALL[k] = (v, tag)
            _ALL[he_norm(k)] = (v, tag)


_index()


def lookup(surface, key=None):
    """-> a word dict in he_ingest's shape, or None. Tries the surface, then a normalised key."""
    hit = _ALL.get(surface) or _ALL.get(he_norm(surface)) or (_ALL.get(key) if key else None)
    if not hit:
        return None
    entry, tag = hit
    pointed, gloss, analysis = entry[0], entry[1], entry[2]
    extra = entry[3] if len(entry) > 3 else 1
    say = extra if isinstance(extra, str) else phon_stressed(pointed, extra)
    return {'surface': surface, 'lemma': pointed, 'form': pointed,
            'vocalized': pointed if he_norm(pointed) == he_norm(surface) else None,
            'vocalized_from': 'curated' if he_norm(pointed) == he_norm(surface) else 'curated:stem',
            'root': None, 'gloss': gloss, 'analysis': analysis,
            'caphi': say, 'caphi_urban': say, 'caphi_raw': None,
            'maknuune_id': None, 'provenance': 'curated:' + tag}
