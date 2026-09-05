"""Hand-curated entries for what a lexicon legitimately doesn't contain.

Maknuune is a lexicon of Palestinian CONTENT words. Three classes fall outside it, and
all three are small, finite and safe to curate by hand rather than guess at:

  1. FUNCTION   prepositions/conjunctions. Maknuune has عَلّي "elevate!" but not
                على-the-preposition. Closed class, a few dozen items.
  2. PROPER     place, country and organisation names. No lexicon carries these, and
                news is full of them. Foreign names have no Arabic root — that's not a
                gap in the data, it's a fact about the words.
  3. MODERN     vocabulary postdating the lexicon (الذكاء الاصطناعي = AI).

Pronunciation is urban Palestinian in the same notation as CAPHI++ after realization:
2 = glottal stop, 3 = ʿayn, 7 = ḥāʾ. Note حريق -> 7arii2: the ق is a glottal stop in
urban speech (SPEC 7.4.4), so it must NOT be written 7ariiq.

Every entry here is marked `curated:*` in the artifact, so it is never mistaken for
lexicon-sourced data.
"""

FUNCTION = {
    "على": ("على", "3ala", "on, at, upon", "PREP"),
    "في":  ("في",  "fi",   "in", "PREP"),
    "من":  ("مِن", "min",  "from", "PREP"),
    "مع":  ("مَع", "ma3",  "with", "PREP"),
    "عن":  ("عَن", "3an",  "about, from", "PREP"),
    "و":   ("و",   "w",    "and", "CONJ"),
    "لما": ("لَمّا","lamma","when", "CONJ_SUB"),
    "اللي":("اللي","2illi","who, which, that", "PRON_REL"),
    "بين": ("بين", "been", "between", "PREP"),
    "أكتر":("أَكتَر","2aktar","more", "ADJ_COMP"),
    # Core Levantine grammar: عم + verb marks the progressive ("is ...-ing").
    # Maknuune only has عمّ "paternal uncle" — the particle is a function word.
    "عم":  ("عَم",  "3am",  "(marks an action in progress)", "PART_PROG"),
}

PROPER = {
    "الصين":    ("الصِّين",   "2is.s.iin",  "China", "NOUN_PROP"),
    "الكونغو":  ("الكونغو",  "2ilkongo",   "Congo", "NOUN_PROP"),
    "كييف":     ("كِييف",    "kiyev",      "Kyiv", "NOUN_PROP"),
    "بانكوك":   ("بانكوك",   "baangkook",  "Bangkok", "NOUN_PROP"),
    "إيران":    ("إيران",    "2iiraan",    "Iran", "NOUN_PROP"),
    "أمريكا":   ("أَمريكا",  "2ameerka",   "America", "NOUN_PROP"),
    "الإيبولا": ("الإيبولا", "2il2iibola", "Ebola", "NOUN_PROP"),
    # Characters from the graded readers. جحا is the protagonist of forty tales and appears in
    # nearly every sentence of that book — without an entry his own name reads "no entry" to a
    # beginner on the very first word they tap.
    "جحا":      ("جُحا",     "ju7a",       "Juha (the folk-tale trickster)", "NOUN_PROP"),
}

# ---------------------------------------------------------------------------------------
# THE GRADED READERS' OWN PEOPLE. جحا above was the first of these and the reason is general:
# a character's name is the word a reader taps most in a book, and Maknuune is a dialect
# lexicon, not a gazetteer, so it either says nothing or says something else. Before this
# table توم was تَوم "twins" through all of Tom Sawyer, واطسون was طَسّ "break sb's heart",
# دمنة was أَدْمَن "be addicted to", جو was جَوّ "weather", فلينت was فَلِّين "cork", and
# 542 tokens of Holmes, Fogg, Silver and Passepartout had no card at all.
#
# Every one below was checked against the WHOLE Arabic corpus first: each appears only where
# it is a name, so none of them shadows an ordinary word the way سيد shadowed "lime" on the
# Hebrew side. Prefixed forms need no entry — lex.morph peels وفوغ, لفوغ, بفوغ back to فوغ.
PROPER.update({
    # Around the World in Eighty Days
    "فوغ":       ("فوغ",       "foog",        "Fogg (Phileas Fogg)", "NOUN_PROP"),
    "باسبارتو":  ("باسبارتو",  "baasbartu",   "Passepartout (Fogg's servant)", "NOUN_PROP"),
    "فيكس":      ("فيكس",      "fiks",        "Fix (the detective)", "NOUN_PROP"),
    "عودا":      ("عودا",      "3ooda",       "Aouda", "NOUN_PROP"),
    "فرانسيس":   ("فرانسيس",   "fraansis",    "Francis (Sir Francis Cromarty)", "NOUN_PROP"),
    "بروكتور":   ("بروكتور",   "brooktor",    "Proctor (Colonel Proctor)", "NOUN_PROP"),
    "سبيدي":     ("سبيدي",     "sbiidi",      "Speedy (the ship's captain)", "NOUN_PROP"),
    "هونغ":      ("هونغ",      "hong",        "Hong (as in Hong Kong)", "NOUN_PROP"),
    "كونغ":      ("كونغ",      "kong",        "Kong (as in Hong Kong)", "NOUN_PROP"),
    "يوكوهاما":  ("يوكوهاما",  "yokohaama",   "Yokohama", "NOUN_PROP"),
    "فرانسيسكو": ("فرانسيسكو", "fransisko",   "Francisco (as in San Francisco)", "NOUN_PROP"),
    "نيويورك":   ("نيويورك",   "nyuuyork",    "New York", "NOUN_PROP"),
    # Sherlock Holmes
    "هولمز":     ("هولمز",     "holmz",       "Holmes (Sherlock Holmes)", "NOUN_PROP"),
    "شرلوك":     ("شرلوك",     "sherlok",     "Sherlock", "NOUN_PROP"),
    "واطسون":    ("واطسون",    "waatson",     "Watson (Doctor Watson)", "NOUN_PROP"),
    "ليستراد":   ("ليستراد",   "listraad",    "Lestrade (the inspector)", "NOUN_PROP"),
    "موريارتي":  ("موريارتي",  "moryaarti",   "Moriarty (the professor)", "NOUN_PROP"),
    "جوليا":     ("جوليا",     "julya",       "Julia (Julia Stoner)", "NOUN_PROP"),
    "كيوبت":     ("كيوبت",     "kyuubit",     "Cubitt (of the dancing men)", "NOUN_PROP"),
    "بيبو":      ("بيبو",      "bibbo",       "Beppo (of the six Napoleons)", "NOUN_PROP"),
    "سانت":      ("سانت",      "saant",       "Saint (as in St Clair)", "NOUN_PROP"),
    "كلير":      ("كلير",      "kleer",       "Clair (Neville St Clair)", "NOUN_PROP"),
    "رايدر":     ("رايدر",     "raayder",     "Ryder (James Ryder)", "NOUN_PROP"),
    "سبولدينغ":  ("سبولدينغ",  "sbolding",    "Spaulding (Wilson's assistant)", "NOUN_PROP"),
    "ميريويذر":  ("ميريويذر",  "meryweeder",  "Merryweather (the bank director)", "NOUN_PROP"),
    "جونز":      ("جونز",      "joonz",       "Jones (the police agent)", "NOUN_PROP"),
    "لندن":      ("لَندن",     "landan",      "London", "NOUN_PROP"),
    # Kalila and Dimna
    "كليلة":     ("كَليلة",    "kaliila",     "Kalila (the jackal)", "NOUN_PROP"),
    "دمنة":      ("دِمنة",     "dimna",       "Dimna (the jackal)", "NOUN_PROP"),
    "بيدبا":     ("بيدبا",     "beedaba",     "Bidpai (the philosopher)", "NOUN_PROP"),
    "شتربة":     ("شَتربة",    "shatraba",    "Shatraba (the bull)", "NOUN_PROP"),
    "دبشليم":    ("دبشليم",    "dabshaliim",  "Dabshalim (the king)", "NOUN_PROP"),
    # Twenty Stories
    "سوفاج":     ("سوفاج",     "sofaaj",      "Sauvage", "NOUN_PROP"),
    "موريسو":    ("موريسو",    "moriso",      "Morissot", "NOUN_PROP"),
    "بيلاييف":   ("بيلاييف",   "bilaayif",    "Belyaev", "NOUN_PROP"),
    "تشيرفياكوف":("تشيرفياكوف","tshirfyaakof","Chervyakov (the clerk)", "NOUN_PROP"),
    "هوشكورن":   ("هوشكورن",   "hoshkorn",    "Hauchecorne (of the piece of string)", "NOUN_PROP"),
    "فاليان":    ("فاليان",    "falyaan",     "Vallin", "NOUN_PROP"),
    # Sindbad
    "سندباد":    ("سِندباد",   "sindbaad",    "Sinbad", "NOUN_PROP"),
    "سرنديب":    ("سَرنديب",   "sarandiib",   "Serendib (Sri Lanka)", "NOUN_PROP"),
    "بغداد":     ("بَغداد",    "baghdaad",    "Baghdad", "NOUN_PROP"),
    # Tom Sawyer
    "توم":       ("توم",       "toom",        "Tom (Tom Sawyer)", "NOUN_PROP"),
    "سوير":      ("سوير",      "sooyer",      "Sawyer", "NOUN_PROP"),
    "هَك":       ("هَك",       "hak",         "Huck (Huckleberry Finn)", "NOUN_PROP"),
    "هك":        ("هَك",       "hak",         "Huck (Huckleberry Finn)", "NOUN_PROP"),
    # لهَك has to be spelled out. The peeler offers له before هك, and له is itself a curated
    # function word ("to him"), so the shorter answer won and five tokens of "to Huck" read as
    # "to him". This is the eat-the-opening-letters case the note on annotate_word describes;
    # naming the whole form is the only fix that does not reorder the peeler for everyone.
    "لهَك":      ("لهَك",      "lahak",       "to Huck", "NOUN_PROP"),
    "لهك":       ("لهَك",      "lahak",       "to Huck", "NOUN_PROP"),
    "بيكي":      ("بيكي",      "biki",        "Becky (Becky Thatcher)", "NOUN_PROP"),
    "ماف":       ("ماف",       "maf",         "Muff (Muff Potter)", "NOUN_PROP"),
    "هاربر":     ("هاربر",     "haarber",     "Harper (Joe Harper)", "NOUN_PROP"),
    "بولي":      ("بولي",      "bolli",       "Polly (Aunt Polly)", "NOUN_PROP"),
    # Treasure Island
    "سيلفر":     ("سيلفر",     "silfer",      "Silver (Long John Silver)", "NOUN_PROP"),
    "جيم":       ("جيم",       "jiim",        "Jim (Jim Hawkins)", "NOUN_PROP"),
    "هاندز":     ("هاندز",     "haandz",      "Hands (Israel Hands)", "NOUN_PROP"),
    "سمولت":     ("سمولت",     "smolit",      "Smollett (the captain)", "NOUN_PROP"),
    "فلينت":     ("فلينت",     "flint",       "Flint (the old captain)", "NOUN_PROP"),
    "جورج":      ("جورج",      "jorj",        "George", "NOUN_PROP"),
    "جون":       ("جون",       "joon",        "John", "NOUN_PROP"),
    "جوني":      ("جوني",      "jooni",       "Johnny", "NOUN_PROP"),
    # LEFT OUT ON PURPOSE: غن (Ben Gunn), جو (Joe) and بيل (Bill). morph() reaches a curated
    # name through stripped SUFFIXES as well as prefixes, so those three are reachable from
    # ordinary words and would overwrite correct answers -- غن from غني "wealthy", أغنى, الغنى,
    # غنوا "they sang" and ten more; جو from الجو "the weather", نجونا "we escaped", فجوة "gap";
    # بيل from نبيل "noble". Together that is some sixty tokens of real Arabic traded for
    # eighty-odd of three names, and a name that eats a real word is the failure this table is
    # most dangerous for. They stay as they were until the peel can be restricted to prefixes.
})

PROPER.update({
    # Countries and cities. News is full of these and no lexicon carries them.
    "روسيا":("روسيا","ruusya","Russia","NOUN_PROP"),
    "أوكرانيا":("أوكرانيا","2ukraanya","Ukraine","NOUN_PROP"),
    "موسكو":("موسكو","mosko","Moscow","NOUN_PROP"),
    "كندا":("كندا","kanada","Canada","NOUN_PROP"),
    "المكسيك":("المَكسيك","2ilmaksiik","Mexico","NOUN_PROP"),
    "النرويج":("النَّرويج","2innarwiij","Norway","NOUN_PROP"),
    "الكويت":("الكُويت","2ilkuweet","Kuwait","NOUN_PROP"),
    "اليمن":("اليَمَن","2ilyaman","Yemen","NOUN_PROP"),
    "الصومال":("الصّومال","2is.s.oomaal","Somalia","NOUN_PROP"),
    "الهند":("الهِند","2ilhind","India","NOUN_PROP"),
    "ترامب":("ترامب","traamb","Trump","NOUN_PROP"),
    # Demonyms — derived from the country but not stored in the lexicon.
    "روسي":("روسي","ruusi","Russian","ADJ:MS"),
    "روسية":("روسِيّة","ruusiyye","Russian (f.)","ADJ:FS"),
    "أوكراني":("أوكراني","2ukraani","Ukrainian","ADJ:MS"),
    "أوكرانية":("أوكرانِيّة","2ukraaniyye","Ukrainian (f.)","ADJ:FS"),
    "أوكرانيين":("أوكرانِيّين","2ukraaniyyiin","Ukrainians","ADJ:P"),
    "أمريكي":("أَمريكي","2ameerki","American","ADJ:MS"),
    "أمريكية":("أَمريكِيّة","2ameerkiyye","American (f.)","ADJ:FS"),
    "صومالي":("صومالي","s.oomaali","Somali","ADJ:MS"),
    "صوماليين":("صوماليّين","s.oomaaliyyiin","Somalis","ADJ:P"),
    "هندية":("هِندِيّة","hindiyye","Indian (f.)","ADJ:FS"),
})

MODERN = {
    "الذكاء":    ("الذَّكاء",   "2iz.zakaa2",   "intelligence", "NOUN:MS"),
    "الاصطناعي": ("الاصطِناعي","2il2is.t.inaa3i","artificial", "ADJ:MS"),
    "حريق":      ("حَريق",     "7arii2",       "a fire, blaze", "NOUN:MS"),
    "دول":       ("دُوَل",      "duwal",        "countries", "NOUN:P"),
    "تلاتين":    ("تَلاتين",   "talaatiin",    "thirty", "NOUN_NUM"),
    "مطعم":      ("مَطعَم",    "mat.3am",      "restaurant, venue", "NOUN:MS"),
    # News vocabulary a colloquial lexicon doesn't carry.
    "نفط":       ("نِفط",      "nift.",        "oil, petroleum", "NOUN:MS"),
    "ناقلة":     ("ناقِلة",    "naa2ile",      "tanker, carrier", "NOUN:FS"),
    "قراصنة":    ("قَراصنة",   "2araas.ne",    "pirates", "NOUN:P"),
    "بوليس":     ("بوليس",     "buliis",       "police", "NOUN:MS"),
    "هليكوبتر":  ("هِليكوبتر", "hilikobter",   "helicopter", "NOUN:MS"),
    "هليكوبترات":("هِليكوبترات","hilikobteraat","helicopters", "NOUN:P"),
    "ناشئة":     ("ناشئة",     "naashi2a",     "start-up, emerging", "ADJ:FS"),
    "مصمم":      ("مُصَمَّم",   "mus.ammam",    "designed", "ADJ:MS"),
    "مدار":      ("مَدار",     "madaar",       "orbit", "NOUN:MS"),
    "صاروخ":     ("صاروخ",     "s.aaruukh",    "rocket, missile", "NOUN:MS"),
}

# ---------------------------------------------------------------------------------------
# THE GRADED READERS' OWN VOCABULARY. Maknuune is a lexicon of Palestinian content words and
# these are the ones it turned out not to have — measured, not guessed: every entry below was
# an `unresolved` token in app/data/ar/corpus.js, which is to say a word a learner tapped and
# got nothing for. 4,448 such tokens remained after the spelling rules in maknuune.py, and the
# ones here are the head of that distribution.
#
# Three kinds, and the third is the reason this list is not longer:
#
#   RANKS AND TITLES. Loanwords a dialect lexicon has no reason to carry — captain, squire,
#   colonel, general — and the nine graded readers are full of them because they are sea
#   stories and detective stories. الكابتن alone was 70 tokens, the single commonest word in
#   the books with no card behind it.
#
#   EVERYDAY WORDS Maknuune simply lacks: بكرا "tomorrow", مرا "woman", مبارح "yesterday".
#   These are not obscure. They are among the first hundred words anyone learns, and every one
#   of them was untappable.
#
#   BASE FORMS ONLY. Nothing inflected or cliticised is written down here. مرته "his wife" and
#   بالكابتن "with the captain" are reached by the peeler once the base exists, and curating
#   each surface separately would be a second lexicon to maintain and get wrong.
PROPER.update({
    # Countries and places the daily paper needs.
    "إسرائيل":  ("إِسرائيل",  "2israa2iil", "Israel", "NOUN_PROP"),
    "السعودية": ("السَّعودية", "2issa3uudiyye", "Saudi Arabia", "NOUN_PROP"),
    "فرنسا":    ("فَرَنسا",   "faransa",    "France", "NOUN_PROP"),
    "ديسمبر":   ("ديسَمبر",   "disamber",   "December", "NOUN_PROP"),
    "رودس":     ("رودُس",     "rodos",      "Rhodes (the Greek island)", "NOUN_PROP"),
    "مطوقة":    ("المطَوَّقة",  "2ilmt.awwa2a", "the Ring-Dove (her name in the fable)", "NOUN_PROP"),
    "هارون":    ("هارون",    "haaruun",    "Harun (al-Rashid, the Caliph)", "NOUN_PROP"),
    "رشيد":     ("الرَّشيد",  "2irrashiid", "al-Rashid (Harun al-Rashid)", "NOUN_PROP"),
    "مهراجان":  ("مِهراجان",  "mihraajaan", "Maharaja (the king Sindbad serves)", "NOUN_PROP"),
    "ويلزي":    ("الويلزي",  "2ilwilzi",   "the Welshman (Tom Sawyer)", "NOUN_PROP"),
    "تاتشر":    ("تاتشِر",   "taatsher",   "Thatcher (Becky's family)", "NOUN_PROP"),
    "بيلي":     ("بيلي",     "bili",       "Billy", "NOUN_PROP"),
    "بطرس":     ("بُطرُس",   "but.rus",    "Peter (Aunt Polly's cat)", "NOUN_PROP"),
    "داود":     ("داود",     "daawuud",    "David (King David)", "NOUN_PROP"),
    "جاكسون":   ("جاكسون",   "jaakson",    "Jackson (Jackson's Island)", "NOUN_PROP"),
    "دوغلاس":   ("دوغلاس",   "duughlaas",  "Douglas (the Widow Douglas)", "NOUN_PROP"),
    "دوبنز":    ("دوبِنز",   "duubinz",    "Dobbins (the schoolmaster)", "NOUN_PROP"),
    "روجرز":    ("روجِرز",   "rujerz",     "Rogers", "NOUN_PROP"),
    "روبنسون":  ("روبِنسون",  "rubinson",   "Robinson (Dr Robinson)", "NOUN_PROP"),
    "موريل":    ("موريل",    "muriil",     "Muriel", "NOUN_PROP"),
    "ماكدوغال": ("ماكدوغال", "maakduughaal","McDougal (the cave)", "NOUN_PROP"),
})

MODERN.update({
    # Ranks and titles. The readers are sea stories and detective stories; a dialect lexicon
    # has no reason to carry the English navy's vocabulary, and every one of these is a word
    # a reader meets on the first page and taps.
    "كابتن":    ("كابتِن",   "kaabtin",    "captain", "NOUN:MS"),
    "قبطان":    ("قُبطان",   "2ubt.aan",   "sea captain, skipper", "NOUN:MS"),
    "جنرال":    ("جِنِرال",  "jineraal",   "general (military rank)", "NOUN:MS"),
    "كولونيل":  ("كولونيل",  "koloniil",   "colonel", "NOUN:MS"),
    "سكوير":    ("سكواير",   "skwaayer",   "squire", "NOUN:MS"),
    "حمال":     ("حَمّال",    "7ammaal",    "porter, carrier", "NOUN:MS"),
    "مليار":    ("مِليار",   "milyaar",    "billion", "NOUN:MS"),
    "رسوم":     ("رُسوم",    "rusuum",     "fees, duties, tariffs", "NOUN:P"),
    # Everyday words the lexicon does not have. Ordinary spoken Palestinian, every one of them
    # in the first hundred words a learner meets.
    "بكرا":     ("بُكرا",    "bukra",      "tomorrow", "ADV"),
    "مبارح":    ("مبارِح",   "mbaari7",    "yesterday", "ADV"),
    # مرا "woman" is NOT here either, for the same reason as لك: the peeler takes the ت off
    # مرات "times" and lands on it, so 20 tokens of "woman" would cost 8 of "three times".
        "مقفول":    ("مَقفول",   "ma2fuul",    "locked, shut", "ADJ:MS"),
    "ضد":       ("ضِدّ",     "d.idd",      "against", "PREP"),
    "غصن":      ("غُصن",     "ghus.n",     "branch, bough", "NOUN:MS"),
    "دجاج":     ("دَجاج",    "djaaj",      "chickens, poultry", "NOUN:P"),
    "سلحفاة":   ("سُلَحفاة",  "sula7faa",   "tortoise, turtle", "NOUN:FS"),
    "سعادة":    ("سَعادة",   "sa3aade",    "excellency (form of address)", "NOUN:FS"),
    "سنتين":    ("سَنتين",   "santeen",    "two years", "NOUN:D"),
    # Teen numerals. Palestinian says them as one word and the lexicon lists the MSA shapes.
    "ضوء":      ("ضَوء",     "d.aw",       "light", "NOUN:MS"),
    # Aesop's cast. A fable is mostly animals and trees, and a lexicon of everyday Palestinian
    # speech turns out not to carry an oak, a stork, a peacock or a frog — measured, one by one,
    # against Maknuune. Broken plurals are written out beside their singulars because nothing
    # derives them: ضفدع does not get you ضفادع by any rule.
    "سنديانة":  ("سِنديانة",  "sindyaane",  "oak tree", "NOUN:FS"),
    # Kalila and Dimna. A book of fables set at a king's court and a water-hole, so the words
    # it needs are the ones a lexicon of everyday speech has least reason to hold: a pool, dust,
    # leftovers, haste. Checked one by one against Maknuune, same as Aesop's cast.
    "غدير":     ("غَدير",    "ghadiir",    "pool, water-hole", "NOUN:MS"),
    # Sindbad. Seven sea voyages, so: diamonds, pearls, ivory, a roc, an elephant's trunk and a
    # harbour. None of it is everyday Palestinian and none of it is in Maknuune.
    "ألماس":    ("ألماس",    "2almaas",    "diamonds", "NOUN:MS"),
    # Tom Sawyer. A Missouri boyhood: warts and marbles and a graveyard at midnight, and none of
    # the props are Palestinian household items, so Maknuune has none of them.
    "زجاج":     ("زْجاج",    "zjaaj",      "glass", "NOUN:MS"),
    "زجاجة":    ("زْجاجة",   "zjaaje",     "bottle", "NOUN:FS"),
    "قرصان":    ("قُرصان",   "2urs.aan",   "pirate", "NOUN:MS"),
    "زقاق":     ("زُقاق",    "zu2aa2",     "alley, lane", "NOUN:MS"),
    "تبغ":      ("تَبِغ",    "tabigh",     "tobacco", "NOUN:MS"),
    "كماشة":    ("كَمّاشة",   "kammaashe",  "pincers, pliers", "NOUN:FS"),
    "تآليل":    ("تآليل",    "ta2aaliil",  "warts", "NOUN:P"),
    "دراقة":    ("دُرّاقة",   "durraa2a",   "peach", "NOUN:FS"),
    "مواء":     ("مُواء",    "muwaa2",     "meowing", "NOUN:MS"),
    "موء":      ("مُوء",     "muu2",       "meow (the sound)", "INTJ"),
    "سنجاب":    ("سِنجاب",   "sinjaab",    "squirrel", "NOUN:MS"),
    "عنكبوت":   ("عَنكَبوت",  "3ankabuut",  "spider", "NOUN:MS"),
    "مقلاية":   ("مِقلاية",  "mi2laaye",   "frying pan", "NOUN:FS"),
    "قضبان":    ("قُضبان",   "2ud.baan",   "bars (of a cell)", "NOUN:P"),
    "منصة":     ("مِنَصّة",   "minas.s.a",  "platform, stage", "NOUN:FS"),
    "محقق":     ("مْحَقِّق",   "m7a22i2",    "detective, investigator", "NOUN:MS"),
    "جغرافيا":  ("جُغرافيا",  "jughraafya", "geography", "NOUN:FS"),
    "انتقام":   ("انتِقام",  "nti2aam",    "revenge", "NOUN:MS"),
    "سباح":     ("سَبّاح",    "sabbaa7",    "swimmer", "NOUN:MS"),
    "شقاوة":    ("شَقاوة",   "sha2aawe",   "mischief, naughtiness", "NOUN:FS"),
    "خدش":      ("خَدش",     "khadsh",     "scratch", "NOUN:MS"),
    "ذباب":     ("ذُباب",    "dubaab",     "flies", "NOUN:P"),
    "طعام":     ("طَعام",    "t.a3aam",    "food", "NOUN:MS"),
    "فوايد":    ("فَوايِد",   "fawaayid",   "benefits, uses", "NOUN:P"),
    "أظافير":   ("أظافير",   "2az.aafiir", "claws, nails", "NOUN:P"),
    "ستمية":    ("سِتّمِيّة",   "sittmiyye",  "six hundred", "NUM"),
    "نادرا":    ("نادِراً",   "naadiran",   "rarely", "ADV"),
    "طبعا":     ("طَبعاً",    "t.ab3an",    "of course, naturally", "ADV"),
    "مشمس":     ("مِشمِس",   "mishmis",    "sunny", "ADJ:MS"),
    "مجدول":    ("مَجدول",   "majduul",    "braided, plaited", "ADJ:MS"),
    "مخلخل":    ("مْخَلخَل",   "mkhalkhal",  "loose, wobbly", "ADJ:MS"),
    "مستحق":    ("مِستَحَقّ",  "mista7a22",  "deserved, due", "ADJ:MS"),
    "مهذب":     ("مْهَذَّب",    "mhazzab",    "polite, well-mannered", "ADJ:MS"),
    "مأكول":    ("مأكول",    "ma2kuul",    "eaten", "ADJ:MS"),
    "مشقوق":    ("مَشقوق",   "mash2uu2",   "split, cracked", "ADJ:MS"),
    "مسروق":    ("مَسروق",   "masruu2",    "stolen", "ADJ:MS"),
    "مقلوع":    ("مَقلوع",   "ma2luu3",    "pulled out, uprooted", "ADJ:MS"),
    "لامع":     ("لامِع",    "laami3",     "shiny, gleaming", "ADJ:MS"),
    # Verbs. Bases in the lexicon, forms not — same story as Sindbad.
    "قفز":      ("قَفَز",     "2afaz",      "he jumped", "VERB"),
    "يقفز":     ("يِقفِز",    "yi2fiz",     "he jumps", "VERB"),
    "اهتز":     ("اهتَزّ",    "htazz",      "it shook", "VERB"),
    "أغنيا":    ("أغنِيا",   "2aghniya",   "rich people", "NOUN:P"),
    "التقوا":   ("التَقوا",   "lta2u",      "they met", "VERB"),
    "انشنق":    ("انشَنَق",   "nshana2",    "he was hanged", "VERB"),
    "بينشنق":   ("بينشَنِق",  "byinshani2", "he gets hanged", "VERB"),
    "غنوا":     ("غَنّوا",    "ghannu",     "they sang", "VERB"),
    "وغنت":     ("وغَنَّت",    "wghannat",   "and she sang", "VERB"),
    "اختبى":    ("اختَبى",   "khtaba",     "he hid (himself)", "VERB"),
    "اختبوا":   ("اختَبوا",   "khtabu",     "they hid", "VERB"),
    "يختبي":    ("يِختِبي",   "yikhtibi",   "he hides", "VERB"),
    "مختبيين":  ("مِختِبيين", "mikhtibyiin","hiding (plural)", "ADJ:P"),
    "ارتجف":    ("ارتَجَف",   "rtajaf",     "he shivered, trembled", "VERB"),
    "بيموء":    ("بيموء",    "byimuu2",    "it meows", "VERB"),
    "تموء":     ("تْموء",    "tmuu2",      "she/it meows", "VERB"),
    "أعطته":    ("أعطَته",   "2a3t.atu",   "she gave him", "VERB"),
    "بيعطوك":   ("بيعطوك",   "byi3t.uuk",  "they give you", "VERB"),
    "بيمشوا":   ("بيمشوا",   "byimshu",    "they walk", "VERB"),
    "يبصق":     ("يِبصُق",    "yibs.u2",    "he spits", "VERB"),
    "بيشتروا":  ("بيشتَروا",  "byishtaru",  "they buy", "VERB"),
    "حاطها":    ("حاطها",    "7aat.ha",    "having put it (f)", "VERB"),
    "ضوين":     ("ضَوّين",    "d.awwiin",   "lit up, glowing (plural)", "ADJ:P"),
    "نتخطب":    ("نِتخَطَب",   "nitkhat.ab", "we get engaged", "VERB"),
    # Sindbad's verbs. Every base below IS in Maknuune; what is not is the form the story uses —
    # a final-weak stem under a subject ending, an internal passive, a 1st-person plural. The
    # peeler reaches one affix, not two, and widening it to reach two was measured twice and
    # thrown away both times (see maknuune.py). Written out with the و left off, because a
    # leading conjunction the peeler DOES take.
    "ماء":      ("ماء",      "maa2",       "water (بماء الذهب = in gold ink)", "NOUN:MS"),
    "اختفوا":   ("اختَفوا",   "khtafu",     "they disappeared", "VERB"),
    "اهتزت":    ("اهتَزَّت",   "htazzat",    "she/it shook", "VERB"),
    "بتهتز":    ("بتِهتَزّ",   "btihtazz",   "she/it shakes", "VERB"),
    "بيربوا":   ("بيرَبّوا",  "biyrabbu",   "they raise, they bring up", "VERB"),
    "بيلاقوه":  ("بيلاقوه",  "biylaa2uu",  "they find him", "VERB"),
    "بينشال":   ("بينشال",   "byinshaal",  "it is being lifted", "VERB"),
    "بينطلع":   ("بينطَلَع",  "byint.ala3", "it can be climbed", "VERB"),
    "بينعبر":   ("بينعَبَر",  "byin3abar",  "it can be crossed", "VERB"),
    "رست":      ("رَسَت",     "rasat",      "she/it anchored, came to rest", "VERB"),
    "نجدف":     ("نِجدِف",    "nijdif",     "we row", "VERB"),
    "تنحفظ":    ("تِنحِفِظ",   "tin7ifiz.",  "it is kept, preserved", "VERB"),
    "حطينا":    ("حَطّينا",   "7at.t.eena", "we put, we placed", "VERB"),
    "شتغلت":    ("شتَغَلت",   "shtaghalt",  "I worked", "VERB"),
    "قفزنا":    ("قَفَزنا",   "2afazna",    "we jumped", "VERB"),
    "ماسكين":   ("ماسكين",   "maaskiin",   "holding, gripping (plural)", "ADJ:P"),
    "لحال":     ("لَحال",    "la7aal",     "by oneself, alone", "ADV"),
    "يبول":     ("يْبول",    "ybuul",      "he urinates", "VERB"),
    "كول":      ("كول",      "kuul",       "eat! (imperative)", "VERB"),
    "يأذيك":    ("يأذيك",    "yi2ziik",    "he will harm you", "VERB"),
    "عاج":      ("عاج",      "3aaj",       "ivory", "NOUN:MS"),
    "ياقوت":    ("ياقوت",    "yaa2uut",    "rubies", "NOUN:MS"),
    "لؤلؤ":     ("لُؤلُؤ",    "lu2lu2",     "pearls", "NOUN:MS"),
    "مئات":     ("مِئات",    "mi2aat",     "hundreds", "NOUN:P"),
    "مخلب":     ("مِخلَب",   "mikhlab",    "claw, talon", "NOUN:MS"),
    "مخالب":    ("مَخالِب",  "makhaalib",  "claws, talons", "NOUN:P"),
    "خرطوم":    ("خُرطوم",   "khurt.uum",  "trunk (of an elephant)", "NOUN:MS"),
    "خراطيم":   ("خَراطيم",  "kharaat.iim","trunks (of elephants)", "NOUN:P"),
    "ميناء":    ("ميناء",    "miina",      "harbour, port", "NOUN:MS"),
    "غروب":     ("غُروب",    "ghuruub",    "sunset", "NOUN:MS"),
    "منادي":    ("مْنادي",   "mnaadi",     "town crier, herald", "NOUN:MS"),
    "مؤمنين":   ("مُؤمِنين",  "mu2miniin",  "believers (أمير المؤمنين = the Caliph)", "NOUN:P"),
    "جذع":      ("جِذع",     "jiz3",       "tree trunk", "NOUN:MS"),
    "خزائن":    ("خَزائِن",   "khazaa2in",  "treasuries, storerooms", "NOUN:P"),
    "صخور":     ("صْخور",    "s.khuur",    "rocks, boulders", "NOUN:P"),
    "قطعان":    ("قُطعان",   "2ut.3aan",   "herds", "NOUN:P"),
    "مقبرة":    ("مَقبَرة",   "ma2bara",    "graveyard", "NOUN:FS"),
    "نبيذ":     ("نَبيذ",    "nabiid",     "wine", "NOUN:MS"),
    "قوس":      ("قَوس",     "2aws",       "bow (for arrows)", "NOUN:MS"),
    "ذراع":     ("ذْراع",    "draa3",      "arm", "NOUN:MS"),
    "شخير":     ("شَخير",    "shakhiir",   "snoring", "NOUN:MS"),
    "مجوهرات":  ("مُجَوهَرات", "mujawharaat","jewels, jewellery", "NOUN:P"),
    "ملسا":     ("مَلسا",    "malsa",      "smooth (feminine)", "ADJ:FS"),
    "مدبوح":    ("مَدبوح",   "madbuu7",    "slaughtered", "ADJ:MS"),
    "حيين":     ("حَيّين",    "7ayyiin",    "alive (dual/plural)", "ADJ:P"),
    "وراء":     ("وَراء",    "waraa",      "behind", "PREP"),
    "رغما":     ("رَغماً",    "raghman",    "in spite of (رغماً عن)", "ADV"),
    "مما":      ("مِمّا",    "mimma",      "than what, of what", "PART"),
    "غبار":     ("غُبار",    "ghubaar",    "dust", "NOUN:MS"),
    "بقايا":    ("بَقايا",   "ba2aaya",    "leftovers, remains", "NOUN:P"),
    "فراش":     ("فِراش",    "firaash",    "bed, bedding", "NOUN:MS"),
    "استعجال":  ("استِعجال",  "sti3jaal",   "haste, hurrying", "NOUN:MS"),
    "وزرا":     ("وُزَرا",    "wuzara",     "ministers", "NOUN:P"),
    "غافل":     ("غافِل",    "ghaafil",    "heedless, inattentive", "ADJ:MS"),
    "مستخبي":   ("مستَخبّي",  "mistakhabbi","hiding, hidden", "ADJ:MS"),
    "استخبى":   ("استَخبّى",  "stakhabba",  "he hid himself", "VERB"),
    "مقتول":    ("مَقتول",   "ma2tuul",    "killed", "ADJ:MS"),
    "راكض":     ("راكِض",    "raakid.",    "running", "ADJ:MS"),
    "مدور":     ("مدَوَّر",   "mdawwar",    "round", "ADJ:MS"),
    "مخيف":     ("مْخيف",    "mkhiif",     "frightening", "ADJ:MS"),
    "مشدود":    ("مَشدود",   "mashduud",   "taut, stretched tight", "ADJ:MS"),
    "طموح":     ("طَموح",    "t.amuu7",    "ambitious", "ADJ:MS"),
    "خادم":     ("خادِم",    "khaadim",    "servant", "NOUN:MS"),
    "قلوب":     ("قْلوب",    "2luub",      "hearts", "NOUN:P"),
    # Verb forms no rule reaches: final-weak stems under a subject ending, and a form VI.
    "جيت":      ("جيت",      "jiit",       "came (past of إجا)", "VERB"),
    "جبت":      ("جِبت",     "jibt",       "I brought", "VERB"),
    "نجت":      ("نَجَت",     "najat",      "she escaped, survived", "VERB"),
    "ينجوا":    ("ينجوا",    "yinjuu",     "they escape, survive", "VERB"),
    "استنت":    ("استَنَّت",   "stannat",    "she waited", "VERB"),
    "استنوا":   ("استَنّوا",  "stannu",     "they waited; wait! (pl)", "VERB"),
    "يبكوا":    ("يِبكوا",   "yibku",      "they cry", "VERB"),
    "تبكوا":    ("تِبكوا",   "tibku",      "you cry (pl)", "VERB"),
    "انخانقوا": ("انخانَقوا", "nkhaana2u",  "they quarrelled with each other", "VERB"),
    "انزحفت":   ("انزَحَفَت",  "nza7afat",   "she crawled", "VERB"),
    "لقلق":     ("لَقلَق",    "la2la2",     "stork", "NOUN:MS"),
    "طاووس":    ("طاووس",    "t.aawuus",   "peacock", "NOUN:MS"),
    "غزال":     ("غَزال",    "ghazaal",    "gazelle, deer", "NOUN:MS"),
    "ضفدع":     ("ضِفدَع",   "d.ifda3",    "frog", "NOUN:MS"),
    "ضفادع":    ("ضَفادِع",  "d.afaadi3",  "frogs", "NOUN:P"),
    "صيصان":    ("صيصان",   "s.iis.aan",  "chicks", "NOUN:P"),
    "جلود":     ("جْلود",    "jluud",      "hides, skins", "NOUN:P"),
    "جذور":     ("جْذور",    "jduur",      "roots", "NOUN:P"),
    "أغصان":    ("أَغصان",   "2aghs.aan",  "branches", "NOUN:P"),
    "معطف":     ("مِعطَف",   "mi3t.af",    "coat", "NOUN:MS"),
    "أشياء":    ("أَشياء",   "2ashyaa2",   "things", "NOUN:P"),
    "صفق":      ("صَفَّق",    "s.affa2",    "he clapped, applauded", "VERB"),
    "مسطح":     ("مُسَطَّح",  "musat.t.a7", "flat", "ADJ:MS"),
    "مربوط":    ("مَربوط",   "marbuut.",   "tied, tied up", "ADJ:MS"),
    "انحنت":    ("انحَنَت",   "in7anat",    "she/it bent over", "VERB"),
    "تخبوا":    ("تخَبّوا",   "tkhabbu",    "they hid", "VERB"),
    "منسمع":    ("ما منِسمَع", "ma mnisma3", "we do not hear", "VERB"),
    "كااااع":   ("كااااع",   "kaaa3",      "caw (a crow's call)", "INTJ"),
    "خروف":     ("خَروف",    "kharuuf",    "sheep, lamb", "NOUN:MS"),
    "زبط":      ("زَبط",     "zabt.",      "exactness (بالزبط = exactly)", "NOUN:MS"),
    "استلف":    ("استَلَف",   "stalaf",     "he borrowed", "VERB"),
    # Keyed as norm() leaves it: the tatweel goes, the drawn-out aaa stays, because that IS
    # the word on the page — a donkey brays at length and the book spells it that way.
    "هيهاااو":  ("هيـهاااو",  "hiihaaaw",   "hee-haw (a donkey's bray)", "INTJ"),
    "اتناعشر":  ("اتناعشَر",  "itna3shar",  "twelve", "NUM"),
    "خمستعشر":  ("خمستَعشَر", "khamasta3shar", "fifteen", "NUM"),
})

# لك "to you" is NOT here, and it is the biggest single word still without a card at 43 tokens.
# Two letters is too few: the peeler reaches it by stripping a ت or a بال from the front, so
# adding it turned تلك "that night" and دير بالك "watch out" and علكة "chewing gum" into "to
# you". A curated entry that overwrites a correct answer is worse than a missing one, and this
# table's whole safety rests on that. It needs a minimum-stem rule, which has been tried twice
# here and made other things worse — see the note on annotate_word in ingest.py.

# STORY — words the short stories need that the lexicon can't resolve on its own:
# character/pet names (proper nouns, like PROPER), and a handful of everyday possessive
# forms whose base+clitic collides with a homograph verb (بيت+نا "our house" vs بيّتنا
# "made us sleep"; أمّ+ي "my mom" vs أمّي "illiterate"). The possessives are transparent
# morphology, not guesses; curated so the reader sees the intended word. Keyed by the
# NORMALISED surface (diacritics stripped, أإآ→ا, ة→ه) to match the ingest lookup.
STORY = {
    "سامي": ("سامي",   "saami",   "Sami (a name)", "NOUN_PROP"),
    "كريم": ("كَريم",   "kariim",  "Karim (a name)", "NOUN_PROP"),
    "احمد": ("أَحمَد",  "2a7mad",  "Ahmad (a name)", "NOUN_PROP"),
    "مشمش": ("مِشمِش",  "mishmish","Mishmish (a cat's name)", "NOUN_PROP"),
    "لولو": ("لولو",   "luulu",   "Lulu (a dog's name)", "NOUN_PROP"),
    "بيتنا": ("بيتْنا",  "beetna",  "our house", "NOUN:MS"),
    "بالبيت":("بالبيت", "bilbeet", "at home, in the house", "NOUN:MS"),
    "جدتي": ("جِدّتي",  "jiddti",  "my grandmother", "NOUN:FS"),
    "جدي":  ("جِدّي",   "jiddi",   "my grandfather", "NOUN:MS"),
    "امي":  ("إمّي",    "2immi",   "my mom", "NOUN:FS"),
    "همه":  ("هُمّة",   "humme",   "they", "PRON"),
    "وهمه": ("وهُمّة",  "whumme",  "and they", "PRON"),
    "مني":  ("مِنّي",   "minni",   "from me, than me", "PREP"),
    "الولاد":("الوْلاد", "2ilwlaad","the kids, the boys", "NOUN:P"),
    "صحابي":("صْحابي",  "s.7aabi", "my friends", "NOUN:P"),
    "تنتين":("تِنتين",  "tinteen", "two (feminine)", "NOUN_NUM"),
    "قهوتي":("قَهوتي",  "2ahwti",  "my coffee", "NOUN:FS"),
    # Intermediate stories: past-tense كان "to be" (1s/1pl collide with a homograph), a few
    # everyday words the lexicon lacks, more names, and two very common suffixed verbs.
    "كنت":  ("كُنت",    "kunt",    "I was, you were", "VERB:P"),
    "كنا":  ("كُنّا",   "kunna",   "we were", "VERB:P"),
    "امه":  ("إمّه",    "2immo",   "his mom", "NOUN:FS"),
    "الاشيا":("الأشيا",  "2il2ashya","the things", "NOUN:P"),
    "دايما":("دايماً",  "daayman", "always", "ADV"),
    "حلويات":("حَلَويات","7alawiyyaat","sweets, desserts", "NOUN:P"),
    "شوكولاته":("شوكولاتة","shokolaata","chocolate", "NOUN:FS"),
    "سمير": ("سَمير",   "samiir",  "Samir (a name)", "NOUN_PROP"),
    "خالد": ("خالِد",   "khaalid", "Khaled (a name)", "NOUN_PROP"),
    "زياد": ("زياد",    "ziyaad",  "Ziad (a name)", "NOUN_PROP"),
    "حسيت": ("حَسّيت",  "7asseet", "I felt", "VERB:P"),
    "حطيت": ("حَطّيت",  "7at.t.eet","I put", "VERB:P"),
    # Advanced stories: the core verb إجا "to come" (Maknuune has no clean entry), a few
    # everyday words the lexicon lacks, one more name, and common suffixed forms.
    "اجا":  ("إجا",     "2ija",    "he came", "VERB:P"),
    "اجت":  ("إجت",     "2ijat",   "she came", "VERB:P"),
    "اجاه": ("إجاه",    "2ijaa",   "came to him", "VERB:P"),
    "اجوا": ("إجوا",    "2iju",    "they came", "VERB:P"),
    "توفت": ("تُوَفّت",  "tiwaffat","she passed away", "VERB:P"),
    "رغم":  ("رَغم",    "raghm",   "despite, in spite of", "PREP"),
    "لسا":  ("لِسّا",   "lissa",   "still, not yet", "ADV"),
    "محدا": ("مَحَدا",  "ma7ada",  "nobody, no one", "PRON"),
    "الصوبا":("الصّوبا", "2is.s.oba","the heater, the stove", "NOUN:FS"),
    "ماجد": ("ماجِد",   "maajid",  "Majid (a name)", "NOUN_PROP"),
    "له":   ("لُه",     "2ilo",    "to him, for him", "PREP"),
}

def _norm(x):
    for a, b in (('أ','ا'),('إ','ا'),('آ','ا'),('ى','ي'),('ة','ه'),('ؤ','ء'),('ئ','ء')):
        x = x.replace(a, b)
    return x.strip()

# Arabic-Indic digits. No lexicon contains "١١" — but a learner still needs to know
# it reads eleven, and the pronunciation is derivable, so handle it programmatically
# rather than leave a quarter of a news sentence bare.
_AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_NUM_NAMES = {0:"sifr",1:"waaHad",2:"tneen",3:"tlaate",4:"2arb3a",5:"khamse",
              6:"sitte",7:"sab3a",8:"tmaanye",9:"tis3a",10:"3ashara",11:"iH.da3sh",
              12:"tna3sh",20:"3ishriin",30:"talaatiin",50:"khamsiin",100:"miyye",
              1000:"2alf"}

def numeral(surface):
    """-> word dict for an Arabic-Indic numeral, else None."""
    core = surface.strip("،.؟!")
    if not core or not all(ch in _AR_DIGITS for ch in core):
        return None
    val = int("".join(str(_AR_DIGITS.index(ch)) for ch in core))
    say = _NUM_NAMES.get(val, str(val))
    return {"surface": surface, "root": "—", "lemma": core, "form": core,
            "caphi_raw": say, "caphi": say, "gloss": f"{val}", "analysis": "NOUN_NUM",
            "maknuune_id": None, "village": None,
            "vocalized": core, "vocalized_from": "curated",
            "provenance": "curated:numeral"}

_ALL = {}
for src, tag in ((FUNCTION, 'function-word'), (PROPER, 'proper-noun'), (MODERN, 'modern-term'),
                 (STORY, 'story-word')):
    for k, v in src.items():
        _ALL[k] = (v, tag)
        _ALL[_norm(k)] = (v, tag)          # match normalised lookups too
        if k.startswith('ال'):             # الصين should also match صين
            _ALL[_norm(k[2:])] = (v, tag)

def lookup(surface, bare=None):
    """-> word dict or None. Tries the surface form, then a bare/normalised form."""
    hit = _ALL.get(surface) or (_ALL.get(bare) if bare else None)
    if not hit:
        return None
    (voc, caphi, gloss, pos), tag = hit
    return {"surface": surface, "root": "—", "lemma": voc, "form": voc,
            "caphi_raw": caphi, "caphi": caphi, "gloss": gloss, "analysis": pos,
            "maknuune_id": None, "village": None,
            "vocalized": voc, "vocalized_from": "curated",
            "provenance": "curated:" + tag}
