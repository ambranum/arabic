import re
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
    "غون":      ("غون",      "ghuun",      "Gunn (Ben Gunn)", "NOUN_PROP"),
    "فيلياس":   ("فيلياس",   "filyaas",    "Phileas (Phileas Fogg)", "NOUN_PROP"),
    # THE NEWS. Countries, clubs, brands and the people in the headlines — the one part of
    # the corpus that is not written here and cannot be gated, because the scraper brings
    # whoever was in the paper this morning. These are the recurring ones.
    "زيلينسكي":     ("زيلينسكي",     "ziilinski",       "Zelensky", "NOUN_PROP"),
    "هرمز":         ("هرمز",         "hurmuz",          "Hormuz (the strait)", "NOUN_PROP"),
    "نيبال":        ("نيبال",        "niibaal",         "Nepal", "NOUN_PROP"),
    "إسبانيا":      ("إسبانيا",      "2isbaanya",       "Spain", "NOUN_PROP"),
    "بريطانيا":     ("بريطانيا",     "brit.aanya",      "Britain", "NOUN_PROP"),
    "سوريا":        ("سوريا",        "suurya",          "Syria", "NOUN_PROP"),
    "هارالد":       ("هارالد",       "haaraald",        "Harald", "NOUN_PROP"),
    "فيفا":         ("فيفا",         "fiifa",           "FIFA", "NOUN_PROP"),
    "أميركا":       ("أميركا",       "2amiirka",        "America", "NOUN_PROP"),
    "كوريا":        ("كوريا",        "kuurya",          "Korea", "NOUN_PROP"),
    "إنفانتينو":    ("إنفانتينو",    "2infantiino",     "Infantino", "NOUN_PROP"),
    "لايبزيغ":      ("لايبزيغ",      "laaybziigh",      "Leipzig", "NOUN_PROP"),
    "العراق":       ("العراق",       "2il3iraa2",       "Iraq", "NOUN_PROP"),
    "الأرجنتين":    ("الأرجنتين",    "2il2arjentiin",   "Argentina", "NOUN_PROP"),
    "غوغل":         ("غوغل",         "guugil",          "Google", "NOUN_PROP"),
    "جوجل":         ("جوجل",         "juujil",          "Google", "NOUN_PROP"),
    "برلين":        ("برلين",        "barliin",         "Berlin", "NOUN_PROP"),
    "ممداني":       ("ممداني",       "mamdaani",        "Mamdani", "NOUN_PROP"),
    "واشنطن":       ("واشنطن",       "waashint.un",     "Washington", "NOUN_PROP"),
    "غراندي":       ("غراندي",       "graandi",         "Grande", "NOUN_PROP"),
    "جونسون":       ("جونسون",       "joonson",         "Johnson", "NOUN_PROP"),
    "بولندا":       ("بولندا",       "bulanda",         "Poland", "NOUN_PROP"),
    "اليونان":      ("اليونان",      "2ilyuunaan",      "Greece", "NOUN_PROP"),
    "باكستان":      ("باكستان",      "baakistaan",      "Pakistan", "NOUN_PROP"),
    "ميانمار":      ("ميانمار",      "myaanmaar",       "Myanmar", "NOUN_PROP"),
    "ميتا":         ("ميتا",         "miita",           "Meta", "NOUN_PROP"),
    "أستراليا":     ("أستراليا",     "2ustraalya",      "Australia", "NOUN_PROP"),
    "دمشق":         ("دمشق",         "dimash2",         "Damascus", "NOUN_PROP"),
    "أونتاريو":     ("أونتاريو",     "2ontaaryo",       "Ontario", "NOUN_PROP"),
    "فنزويلا":      ("فنزويلا",      "fanazweela",      "Venezuela", "NOUN_PROP"),
    "أوربان":       ("أوربان",       "2urbaan",         "Orban", "NOUN_PROP"),
    "فيكرام":       ("فيكرام",       "fiikraam",        "Vikram", "NOUN_PROP"),
    "درامن":        ("درامن",        "draamin",         "Drammen", "NOUN_PROP"),
    "شاكيرا":       ("شاكيرا",       "shaakiira",       "Shakira", "NOUN_PROP"),
    "مادونا":       ("مادونا",       "madoona",         "Madonna", "NOUN_PROP"),
    "جاستن":        ("جاستن",        "jaastin",         "Justin", "NOUN_PROP"),
    "بيبر":         ("بيبر",         "biiber",          "Bieber", "NOUN_PROP"),
    "وانغ":         ("وانغ",         "waang",           "Wang", "NOUN_PROP"),
    "جيبينغ":       ("جيبينغ",       "jiibiing",        "Jinping", "NOUN_PROP"),
    "أوشا":         ("أوشا",         "2uusha",          "Usha", "NOUN_PROP"),
    "السنوار":      ("السنوار",      "2issinwaar",      "Sinwar", "NOUN_PROP"),
    "هيغسيث":       ("هيغسيث",       "hiigsiith",       "Hegseth", "NOUN_PROP"),
    "الكونغرس":     ("الكونغرس",     "2ilkongres",      "Congress", "NOUN_PROP"),
    "سيرسكي":       ("سيرسكي",       "siirski",         "Syrskyi", "NOUN_PROP"),
    "وايلدبيريز":   ("وايلدبيريز",   "waayldberiiz",    "Wildberries", "NOUN_PROP"),
    "هتلر":         ("هتلر",         "hitler",          "Hitler", "NOUN_PROP"),
    "النازيين":     ("النازيين",     "2innaaziyyiin",   "the Nazis", "NOUN_PROP"),
    "ليبيريا":      ("ليبيريا",      "liibiirya",       "Liberia", "NOUN_PROP"),
    "سونام":        ("سونام",        "suunaam",         "Sonam", "NOUN_PROP"),
    "وانغتشوك":     ("وانغتشوك",     "waangtshuuk",     "Wangchuk", "NOUN_PROP"),
    "رمافوزا":      ("رمافوزا",      "ramafooza",       "Ramaphosa", "NOUN_PROP"),
    "تيسلا":        ("تيسلا",        "tesla",           "Tesla", "NOUN_PROP"),
    "سياتل":        ("سياتل",        "syaatil",         "Seattle", "NOUN_PROP"),
    "نتنياهو":      ("نتنياهو",      "netanyaahu",      "Netanyahu", "NOUN_PROP"),
    "زيدان":        ("زيدان",        "ziidaan",         "Zidane", "NOUN_PROP"),
    "ريال":         ("ريال",         "ryaal",           "Real (Real Madrid)", "NOUN_PROP"),
    "مدريد":        ("مدريد",        "madriid",         "Madrid", "NOUN_PROP"),
    "تورنتو":       ("تورنتو",       "tuurunto",        "Toronto", "NOUN_PROP"),
    "تلغرام":       ("تلغرام",       "tiligraam",       "Telegram", "NOUN_PROP"),
    "دوروف":        ("دوروف",        "duurof",          "Durov", "NOUN_PROP"),
    "جاريد":        ("جاريد",        "jaariid",         "Jared", "NOUN_PROP"),
    "غانا":         ("غانا",         "ghaana",          "Ghana", "NOUN_PROP"),
    "ميلان":        ("ميلان",        "miilaan",         "Milan (the club)", "NOUN_PROP"),
    "باريزي":       ("باريزي",       "baariizi",        "Parisi", "NOUN_PROP"),
    "اليويفا":      ("اليويفا",      "2ilyuwiifa",      "UEFA", "NOUN_PROP"),
    "شنغن":         ("شنغن",         "shengen",         "Schengen", "NOUN_PROP"),
    "كينيا":        ("كينيا",        "kiinya",          "Kenya", "NOUN_PROP"),
    "إندونيسيا":    ("إندونيسيا",    "2induuniisya",    "Indonesia", "NOUN_PROP"),
    "أندونيسيا":    ("أندونيسيا",    "2anduuniisya",    "Indonesia", "NOUN_PROP"),
    "نازكا":        ("نازكا",        "naazka",          "Nazca", "NOUN_PROP"),
    "روما":         ("روما",         "ruuma",           "Rome", "NOUN_PROP"),
    "ميلانو":       ("ميلانو",       "miilaano",        "Milano", "NOUN_PROP"),
    "نيرمال":       ("نيرمال",       "niirmaal",        "Nirmal", "NOUN_PROP"),
    "بورجا":        ("بورجا",        "buurja",          "Purja", "NOUN_PROP"),
    "تيمان":        ("تيمان",        "tiimaan",         "Tieman", "NOUN_PROP"),
    "الراين":       ("الراين",       "2irraayn",        "the Rhine", "NOUN_PROP"),
    "أونغ":         ("أونغ",         "2oong",           "Aung", "NOUN_PROP"),
    "خيرسون":       ("خيرسون",       "kheerson",        "Kherson", "NOUN_PROP"),
    "أفغانستان":    ("أفغانستان",    "2afghaanistaan",  "Afghanistan", "NOUN_PROP"),
    "الأفغاني":     ("الأفغاني",     "2il2afghaani",    "Afghan", "NOUN_PROP"),
    "مشيغن":        ("مشيغن",        "mishighan",       "Michigan", "NOUN_PROP"),
    "انستغرام":     ("انستغرام",     "2instaghraam",    "Instagram", "NOUN_PROP"),
    "واتساب":       ("واتساب",       "waatsaab",        "WhatsApp", "NOUN_PROP"),
    "الأوسكار":     ("الأوسكار",     "2il2oskaar",      "the Oscars", "NOUN_PROP"),
    "تركيا":        ("تركيا",        "turkya",          "Turkey", "NOUN_PROP"),
    "يوسين":        ("يوسين",        "yuusiin",         "Yusin", "NOUN_PROP"),
    "بكين":         ("بكين",         "bikiin",          "Beijing", "NOUN_PROP"),
    "غينيا":        ("غينيا",        "ghiinya",         "Guinea", "NOUN_PROP"),
    "حزيران":       ("حزيران",       "7aziiraan",       "June", "NOUN_PROP"),
    "تايلاند":      ("تايلاند",      "taaylaand",       "Thailand", "NOUN_PROP"),
    "الإثيوبي":     ("الإثيوبي",     "2il2ithyoobi",    "Ethiopian", "NOUN_PROP"),
    "كيجيلتشا":     ("كيجيلتشا",     "kiijiiltsha",     "Kejelcha", "NOUN_PROP"),
    "نيفادا":       ("نيفادا",       "nifaada",         "Nevada", "NOUN_PROP"),
    "رينو":         ("رينو",         "riino",           "Reno", "NOUN_PROP"),
    "أنثروبيك":     ("أنثروبيك",     "2anthroobik",     "Anthropic", "NOUN_PROP"),
    "البنتاغون":    ("البنتاغون",    "2ilbentaaghon",   "the Pentagon", "NOUN_PROP"),
    "السودان":      ("السودان",      "2issuudaan",      "Sudan", "NOUN_PROP"),
    "يانوبولوس":    ("يانوبولوس",    "yaanopoolos",     "Yiannopoulos", "NOUN_PROP"),
    "الإكوادور":    ("الإكوادور",    "2il2ikwaadoor",   "Ecuador", "NOUN_PROP"),
    "مورينو":       ("مورينو",       "muriino",         "Moreno", "NOUN_PROP"),
    "أوغندا":       ("أوغندا",       "2ughanda",        "Uganda", "NOUN_PROP"),
    "قبرص":         ("قبرص",         "2ubrus.",         "Cyprus", "NOUN_PROP"),
    "أيسلندا":      ("أيسلندا",      "2ayslanda",       "Iceland", "NOUN_PROP"),
    "الغراند":      ("الغراند",      "2ilgraand",       "the Grand", "NOUN_PROP"),
    "ناسا":         ("ناسا",         "naasa",           "NASA", "NOUN_PROP"),
    "دوين":         ("دوين",         "dweyn",           "Dwayne", "NOUN_PROP"),
    "ديفيس":        ("ديفيس",        "diifiis",         "Davis", "NOUN_PROP"),
    "شاكور":        ("شاكور",        "shaakuur",        "Shakur", "NOUN_PROP"),
    "دريسكول":      ("دريسكول",      "driiskol",        "Driscoll", "NOUN_PROP"),
    "ميسي":         ("ميسي",         "miisi",           "Messi", "NOUN_PROP"),
    "فرنانديز":     ("فرنانديز",     "firnaandiiz",     "Fernandez", "NOUN_PROP"),
    "تشيلسي":       ("تشيلسي",       "tshelsi",         "Chelsea", "NOUN_PROP"),
    "مانشستر":      ("مانشستر",      "maanshister",     "Manchester", "NOUN_PROP"),
    "سيتي":         ("سيتي",         "siiti",           "City (Manchester City)", "NOUN_PROP"),
    "الفلبين":      ("الفلبين",      "2ilfilibbiin",    "the Philippines", "NOUN_PROP"),
    "هولندا":       ("هولندا",       "holanda",         "Holland", "NOUN_PROP"),
    "مالطا":        ("مالطا",        "maalt.a",         "Malta", "NOUN_PROP"),
    "دافني":        ("دافني",        "daafni",          "Daphne", "NOUN_PROP"),
    "المغير":       ("المغير",       "2ilmughayyir",    "al-Mughayyir", "NOUN_PROP"),
    "غلوريا":       ("غلوريا",       "gloorya",         "Gloria", "NOUN_PROP"),
    "ستاينم":       ("ستاينم",       "staaynim",        "Steinem", "NOUN_PROP"),
    "الكناري":      ("الكناري",      "2ilkanaari",      "the Canaries", "NOUN_PROP"),
    "النينيو":      ("النينيو",      "2inniinyo",       "El Nino", "NOUN_PROP"),
    "كلانسي":       ("كلانسي",       "klaansi",         "Clancy", "NOUN_PROP"),
    "الحوثي":       ("الحوثي",       "2il7uuthi",       "the Houthi", "NOUN_PROP"),
    "الحوثيين":     ("الحوثيين",     "2il7uuthiyyiin",  "the Houthis", "NOUN_PROP"),
    "لبنان":        ("لبنان",        "libnaan",         "Lebanon", "NOUN_PROP"),
    "المواصي":      ("المواصي",      "2ilmawaas.i",     "al-Mawasi", "NOUN_PROP"),
    "الإسبانية":    ("الإسبانية",    "2il2isbaaniyye",  "Spanish", "NOUN_PROP"),
    "السعودي":      ("السعودي",      "2issa3uudi",      "Saudi", "NOUN_PROP"),
    # Maupassant and Chekhov, so: Normandy and Petersburg.
    "خريوكين":      ("خريوكين",      "khryuukiin",      "Khryukin", "NOUN_PROP"),
    "بيليجي":     ("بيليجي",     "biliiji",       "Pelageya (the maid)", "NOUN_PROP"),
    "جين":        ("جين",        "jiin",          "Jean, Jeanne", "NOUN_PROP"),
    "لانتان":       ("لانتان",       "lantaan",         "Lantin", "NOUN_PROP"),
    "تيفاش":        ("تيفاش",        "tiifaash",        "Tuvache", "NOUN_PROP"),
    "إيفان":        ("إيفان",        "2iifaan",         "Ivan", "NOUN_PROP"),
    "أليوشا":       ("أليوشا",       "2alyoosha",       "Alyosha", "NOUN_PROP"),
    "فوريستييه":    ("فوريستييه",    "foristye",        "Forestier", "NOUN_PROP"),
    "ماتيلد":       ("ماتيلد",       "maatiild",        "Mathilde", "NOUN_PROP"),
    "نثنائيل":      ("نثنائيل",      "nathanaa2iil",    "Nathanael", "NOUN_PROP"),
    "فانكا":        ("فانكا",        "faanka",          "Vanka", "NOUN_PROP"),
    "مالاندان":     ("مالاندان",     "malandaan",       "Malandain", "NOUN_PROP"),
    "لوازيل":       ("لوازيل",       "lwaaziil",        "Loisel", "NOUN_PROP"),
    "شارلو":        ("شارلو",        "shaarlo",         "Charlot", "NOUN_PROP"),
    "لويزا":        ("لويزا",        "lwiiza",          "Louisa", "NOUN_PROP"),
    "ديميتريتش":    ("ديميتريتش",    "dimiitritsh",     "Dmitritch", "NOUN_PROP"),
    "جوكوف":        ("جوكوف",        "jukoof",          "Zhukov", "NOUN_PROP"),
    "قسطنطين":      ("قسطنطين",      "2ust.ant.iin",    "Konstantin", "NOUN_PROP"),
    "مكاريتش":      ("مكاريتش",      "makaaritsh",      "Makaritch", "NOUN_PROP"),
    "إفانوف":       ("إفانوف",       "2ifaanof",        "Ivanov", "NOUN_PROP"),
    "بطرسبورغ":     ("بطرسبورغ",     "bit.rsbuurgh",    "Petersburg", "NOUN_PROP"),
    "مارينيان":     ("مارينيان",     "maarinyaan",      "Marignan", "NOUN_PROP"),
    "أوريل":        ("أوريل",        "2ooriil",         "Aurel", "NOUN_PROP"),
    "غودرفيل":      ("غودرفيل",      "guudarfiil",      "Goderville", "NOUN_PROP"),
    "جيرزي":        ("جيرزي",        "jeerzi",          "Jersey", "NOUN_PROP"),
    "دارمانش":      ("دارمانش",      "daarmaansh",      "D'Armanches", "NOUN_PROP"),
    "نيكولا":       ("نيكولا",       "nikola",          "Nicolas", "NOUN_PROP"),
    "توسان":        ("توسان",        "tuusaan",         "Toussaint", "NOUN_PROP"),
    "بريزجالوف":    ("بريزجالوف",    "brizjaalof",      "Prishibeyev", "NOUN_PROP"),
    "أوتشوميلوف":   ("أوتشوميلوف",   "2otshumiilof",    "Otchumyelov", "NOUN_PROP"),
    "جيغالوف":      ("جيغالوف",      "jiighaalof",      "Zhigalov", "NOUN_PROP"),
    "بورفيري":      ("بورفيري",      "borfiiri",        "Porfiry", "NOUN_PROP"),
    "ميشا":         ("ميشا",         "miisha",          "Misha", "NOUN_PROP"),
    "هيروستراتوس":  ("هيروستراتوس",  "hiirostraatos",   "Herostratus", "NOUN_PROP"),
    "إفيالتيس":     ("إفيالتيس",     "2ifyaaltiis",     "Ephialtes", "NOUN_PROP"),
    "أولغا":        ("أولغا",        "2oolgha",         "Olga", "NOUN_PROP"),
    "إغناتييفنا":   ("إغناتييفنا",   "2ighnaatyeefna",  "Ignatyevna", "NOUN_PROP"),
    "يارمونكين":    ("يارمونكين",    "yaarmoonkiin",    "Yarmonkin", "NOUN_PROP"),
    "سلوفتسوف":     ("سلوفتسوف",     "slooftsof",       "Slovtsov", "NOUN_PROP"),
    "نيكاندروف":    ("نيكاندروف",    "nikaandrof",      "Nikandrov", "NOUN_PROP"),
    "كوزمودميانسكي": ("كوزمودميانسكي", "kozmodimyaanski", "Kozmodemyansky", "NOUN_PROP"),
    "نيكولاي":      ("نيكولاي",      "nikolaay",        "Nikolai", "NOUN_PROP"),
    "إيليتش":       ("إيليتش",       "2iilitsh",        "Ilitch", "NOUN_PROP"),
    "بوتابوف":      ("بوتابوف",      "butaabof",        "Potapov", "NOUN_PROP"),
    "فيبورغ":       ("فيبورغ",       "viiburgh",        "Vyborg", "NOUN_PROP"),
    "أنيسيا":       ("أنيسيا",       "2aniisya",        "Anisya", "NOUN_PROP"),
    "كوزما":        ("كوزما",        "kuzma",           "Kuzma", "NOUN_PROP"),
    "إيونيتش":      ("إيونيتش",      "2iyoonitsh",      "Ionitch", "NOUN_PROP"),
    "يفنكن":        ("يفنكن",        "yifnkn",          "an illegible signature in the complaint book", "NOUN_PROP"),
    # The Holmes cast and its map of London — more names than any other book on the shelf.
    "أدلر":       ("أدلر",       "2adler",        "Adler (Irene Adler)", "NOUN_PROP"),
    "أوكشوت":     ("أوكشوت",     "2okshoot",      "Oakshott", "NOUN_PROP"),
    "بليز":       ("بليز",       "bleez",         "Blaze (Silver Blaze)", "NOUN_PROP"),
    "هورنر":      ("هورنر",      "horner",        "Horner", "NOUN_PROP"),
    "سيمبسون":    ("سيمبسون",    "simbson",       "Simpson", "NOUN_PROP"),
    "رونالد":     ("رونالد",     "ronald",        "Ronald (Ronald Adair)", "NOUN_PROP"),
    "موران":      ("موران",      "moraan",        "Moran (Colonel Moran)", "NOUN_PROP"),
    "بريكنريدج":  ("بريكنريدج",  "brekinrij",     "Breckinridge", "NOUN_PROP"),
    "غريغوري":    ("غريغوري",    "griigori",      "Gregory (Inspector Gregory)", "NOUN_PROP"),
    "هاركر":      ("هاركر",      "haarker",       "Harker", "NOUN_PROP"),
    "تشيزيك":     ("تشيزيك",     "tshiizik",      "Chiswick", "NOUN_PROP"),
    "نورفولك":    ("نورفولك",    "norfolk",       "Norfolk", "NOUN_PROP"),
    "بوهيميا":    ("بوهيميا",    "bohiimya",      "Bohemia", "NOUN_PROP"),
    "مونيكا":     ("مونيكا",     "moniika",       "Monica", "NOUN_PROP"),
    "دنكان":      ("دنكان",      "dankan",        "Duncan", "NOUN_PROP"),
    "بيترسون":    ("بيترسون",    "biiterson",     "Peterson", "NOUN_PROP"),
    "ألمانيا":    ("ألمانيا",    "2almaanya",     "Germany", "NOUN_PROP"),
    "ألماني":     ("ألماني",     "2almaani",      "German", "NOUN_PROP"),
    "بايكر":      ("بايكر",      "baayker",       "Baker (Baker Street; Henry Baker)", "NOUN_PROP"),
    "غاردن":      ("غاردن",      "gaardin",       "Garden (Covent Garden)", "NOUN_PROP"),
    "دربيشير":    ("دربيشير",    "darbishiir",    "Derbyshire", "NOUN_PROP"),
    "بورجيا":     ("بورجيا",     "borjya",        "Borgia", "NOUN_PROP"),
    "بريدينغ":    ("بريدينغ",    "briidiing",     "Breeding", "NOUN_PROP"),
    "أورمشتاين":  ("أورمشتاين",  "2ormshtaayn",   "Ormstein", "NOUN_PROP"),
    "وارسو":      ("وارسو",      "waarso",        "Warsaw", "NOUN_PROP"),
    "جيرسي":      ("جيرسي",      "jeersi",        "Jersey", "NOUN_PROP"),
    "لودج":       ("لودج",       "lodj",          "Lodge (Briony Lodge)", "NOUN_PROP"),
    "سيربنتاين":  ("سيربنتاين",  "serbentaayn",   "Serpentine", "NOUN_PROP"),
    "أفينيو":     ("أفينيو",     "2afinyu",       "Avenue", "NOUN_PROP"),
    "غودفري":     ("غودفري",     "gudfri",        "Godfrey", "NOUN_PROP"),
    "جابيز":      ("جابيز",      "jaabiiz",       "Jabez (Jabez Wilson)", "NOUN_PROP"),
    "ويلسون":     ("ويلسون",     "wilson",        "Wilson", "NOUN_PROP"),
    "أركري":      ("أركري",      "2arkri",        "Archery", "NOUN_PROP"),
    "أرمور":      ("أرمور",      "2armuur",       "Armour", "NOUN_PROP"),
    "أثينا":      ("أثينا",      "2athiina",      "Athens", "NOUN_PROP"),
    "ستراند":     ("ستراند",     "straand",       "Strand", "NOUN_PROP"),
    "كوبرغ":      ("كوبرغ",      "koburgh",       "Coburg (Saxe-Coburg Square)", "NOUN_PROP"),
    "ستونر":      ("ستونر",      "stoner",        "Stoner (Helen Stoner)", "NOUN_PROP"),
    "رويلوت":     ("رويلوت",     "roylot",        "Roylott (Dr Grimesby Roylott)", "NOUN_PROP"),
    "موركار":     ("موركار",     "morkaar",       "Morcar (the Countess of Morcar)", "NOUN_PROP"),
    "غودج":       ("غودج",       "gudj",          "Goodge (Goodge Street)", "NOUN_PROP"),
    "كوفنت":      ("كوفنت",      "kofent",        "Covent (Covent Garden)", "NOUN_PROP"),
    "بريكستون":   ("بريكستون",   "brikston",      "Brixton", "NOUN_PROP"),
    "جيمس":       ("جيمس",       "jeems",         "James", "NOUN_PROP"),
    "كوزموبوليتان": ("كوزموبوليتان", "kozmopolitaan", "Cosmopolitan (the hotel)", "NOUN_PROP"),
    "دارتمور":    ("دارتمور",    "daartmoor",     "Dartmoor", "NOUN_PROP"),
    "ويسيكس":     ("ويسيكس",     "wiisiks",       "Wessex", "NOUN_PROP"),
    "سترايكر":    ("سترايكر",    "straayker",     "Straker (John Straker)", "NOUN_PROP"),
    "كينغز":      ("كينغز",      "kiingz",        "King's (King's Pyland)", "NOUN_PROP"),
    "بايلاند":    ("بايلاند",    "baaylaand",     "Pyland (King's Pyland)", "NOUN_PROP"),
    "كينسينغتون": ("كينسينغتون", "kinsingtoon",   "Kensington", "NOUN_PROP"),
    "ستيبني":     ("ستيبني",     "stibni",        "Stepney", "NOUN_PROP"),
    "ريدينغ":     ("ريدينغ",     "riidiing",      "Reading", "NOUN_PROP"),
    "ساندفورد":   ("ساندفورد",   "saandford",     "Sandeford", "NOUN_PROP"),
    "ثورستون":    ("ثورستون",    "thorston",      "Thurston", "NOUN_PROP"),
    "إلريج":      ("إلريج",      "2ilrij",        "Elrige (Elrige's Farm)", "NOUN_PROP"),
    "بروكسل":     ("بروكسل",     "bruksil",       "Brussels", "NOUN_PROP"),
    "سويسرا":     ("سويسرا",     "swiisra",       "Switzerland", "NOUN_PROP"),
    "سويسري":     ("سويسري",     "swiisri",       "Swiss", "NOUN_PROP"),
    "مايرينغن":   ("مايرينغن",   "maayringin",    "Meiringen", "NOUN_PROP"),
    "رايخنباخ":   ("رايخنباخ",   "raaykhinbaakh", "Reichenbach", "NOUN_PROP"),
    "مايكروفت":   ("مايكروفت",   "maaykroft",     "Mycroft", "NOUN_PROP"),
    "سيباستيان":  ("سيباستيان",  "sibaastyaan",   "Sebastian (Colonel Sebastian Moran)", "NOUN_PROP"),
    "هدسون":      ("هدسون",      "hadson",        "Hudson (Mrs Hudson)", "NOUN_PROP"),
    "هنري":       ("هنري",       "henri",         "Henry (Henry Baker)", "NOUN_PROP"),
    "سانفرانسيسكو":("سان فرانسيسكو","saan fransiisko","San Francisco", "NOUN_PROP"),
    "سكوتلانديارد":("سكوتلاند يارد","skotlaand yaard","Scotland Yard", "NOUN_PROP"),
    "بونسبي":   ("بونسبي",   "bunsbi",     "Bunsby", "NOUN_PROP"),
    "ريفورم":   ("ريفورم",   "rifoorm",    "Reform (the Reform Club)", "NOUN_PROP"),
    "مادج":     ("مادج",     "maadj",      "Madge", "NOUN_PROP"),
    "غرانت":    ("غرانت",    "graant",     "Grant", "NOUN_PROP"),
    "كرومارتي": ("كرومارتي", "krumaarti",  "Cromarty (Sir Francis Cromarty)", "NOUN_PROP"),
    "كامرفيلد": ("كامرفيلد", "kaamerfiild","Camerfield", "NOUN_PROP"),
    "ماندبوي":  ("ماندبوي",  "maandbooy",  "Mandiboy", "NOUN_PROP"),
    "ستامب":    ("ستامب",    "staamb",     "Stamp", "NOUN_PROP"),
    "سميث":     ("سميث",     "smiith",     "Smith", "NOUN_PROP"),
    "سافيل":    ("سافيل",    "saafiil",    "Savile (Savile Row)", "NOUN_PROP"),
    "سوتي":     ("سوتي",     "suuti",      "suttee (the widow-burning rite)", "NOUN:MS"),
    "يانكي":    ("يانكي",    "yaanki",     "Yankee", "NOUN:MS"),
    "مورمون":   ("مورمون",   "muurmuun",   "Mormon", "NOUN_PROP"),
    "أكتوبر":   ("أكتوبِر",   "2oktoober",  "October", "NOUN_PROP"),
    "نوفمبر":   ("نوفَمبِر",   "noofamber",  "November", "NOUN_PROP"),
    "فرنسي":    ("فَرَنسي",   "faransi",    "French", "ADJ:MS"),
    # Places and ships on the route.
    "كلكتا":    ("كَلكُتا",   "kalkuta",    "Calcutta", "NOUN_PROP"),
    "شنغهاي":   ("شَنغهاي",  "shanghaay",  "Shanghai", "NOUN_PROP"),
    "سنغافورة": ("سِنغافورة", "singhafuura","Singapore", "NOUN_PROP"),
    "اليابان":  ("اليابان",  "2ilyaabaan", "Japan", "NOUN_PROP"),
    "ياباني":   ("ياباني",   "yaabaani",   "Japanese", "ADJ:MS"),
    "سويس":     ("السّويس",   "2issuwees",  "Suez", "NOUN_PROP"),
    "أوروبا":   ("أوروبا",   "2uurubba",   "Europe", "NOUN_PROP"),
    "إيطاليا":  ("إيطاليا",  "2iit.aalya", "Italy", "NOUN_PROP"),
    "أيرلندا":  ("أيرلَندا",  "2ayrlanda",  "Ireland", "NOUN_PROP"),
    "باريس":    ("باريس",    "baariis",    "Paris", "NOUN_PROP"),
    "دوفر":     ("دوفَر",    "duufar",     "Dover", "NOUN_PROP"),
    "ليفربول":  ("ليفَربول",  "liifarbuul", "Liverpool", "NOUN_PROP"),
    "شيكاغو":   ("شيكاغو",   "shiikaaghu", "Chicago", "NOUN_PROP"),
    "روكي":     ("روكي",     "ruuki",      "Rocky (the Rocky Mountains)", "NOUN_PROP"),
    "سكوتلاند": ("سكوتلاند", "skotlaand",  "Scotland (Scotland Yard)", "NOUN_PROP"),
    "التايمز":  ("التايمز",  "2ittaayimz", "The Times", "NOUN_PROP"),
    "المونغوليا":("المونغوليا","2ilmungholya","the Mongolia (the steamer)", "NOUN_PROP"),
    "الكارناتيك":("الكارناتيك","2ilkarnaatiik","the Carnatic (the steamer)", "NOUN_PROP"),
    "الرانغون": ("الرانغون", "2irrangoon", "the Rangoon (the steamer)", "NOUN_PROP"),
    "التانكادير":("التانكادير","2ittankadiir","the Tankadere (the pilot boat)", "NOUN_PROP"),
    "الهنريتا": ("الهِنريتا", "2ilhinriita","the Henrietta (the steamer)", "NOUN_PROP"),
    "يوهوهو":   ("يوهوهو",   "yo-ho-ho",   "yo-ho-ho (the pirates' chorus)", "INTJ"),
    "بونز":     ("بونز",     "buunz",      "Bones (Billy Bones)", "NOUN_PROP"),
    "هنتر":     ("هَنتِر",    "hanter",     "Hunter", "NOUN_PROP"),
    "هوكينز":   ("هوكينز",   "hookinz",    "Hawkins (Jim Hawkins)", "NOUN_PROP"),
    "بريستول":  ("بريستول",  "bristol",    "Bristol", "NOUN_PROP"),
    "هيسبانيولا":("هيسبانيولا","hispanyoola","Hispaniola (the ship)", "NOUN_PROP"),
    "آرو":      ("آرو",      "2aarow",     "Arrow (the first mate)", "NOUN_PROP"),
    "ريدروث":   ("ريدروث",   "redruuth",   "Redruth", "NOUN_PROP"),
    "جويس":     ("جويس",     "joyis",      "Joyce", "NOUN_PROP"),
    "جوب":      ("جوب",      "joob",       "Job (Job Anderson)", "NOUN_PROP"),
    "هاري":     ("هاري",     "haari",      "Harry", "NOUN_PROP"),
    "أبراهام":  ("أبراهام",  "2abraahaam", "Abraham (Abraham Gray)", "NOUN_PROP"),
    "داربي":    ("داربي",    "daarbi",     "Darby (Darby McGraw)", "NOUN_PROP"),
    "ماكغرو":   ("ماكغرو",   "maakghrow",  "McGraw (Darby McGraw)", "NOUN_PROP"),
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
    # THE AMBIGUOUS QUEUE, the part of it a resolution cannot reach. A resolution picks among the
    # candidates the morphology allows; these five have no right candidate at all, because the
    # exact surface matches a different word and the real answer never enters the list. قلت
    # matches قَلّ "be reduced" rather than قال "say"; شفت matches شَفّ "run over" rather than
    # شاف "see"; وكل matches وَكَّل "authorize" rather than و + كل. Each was checked with
    # pipeline/collide.py first, and each captures only its own family:
    #   وجه   252 tokens across ووجهه، وجهه، وجهها، الوجه، وجهك — every one a face
    #   شفت   128 tokens across وشفت، شفته، شفتوا، شفتها — every one seeing
    #   قلت    72 tokens across وقلت، قلته، قلتها — and نقلت "I transferred", 2 tokens, wrong
    #   وكل    20 tokens across وكلهم، وكله، وكلنا — every one "all of"
    # وبعد is NOT here: it would have taken وبعدين "and then" with it, 441 tokens that are
    # already right. It gets a resolution pointing at the real بَعِد entry instead.
    "وجه":        ("وِجِه",      "wijih",       "face", "NOUN:MS"),
    "أخد":        ("أخَد",      "2akhad",      "he took", "VERB"),
    "قلب":        ("قَلب",      "2alb",        "heart", "NOUN:MS"),
    # خالة is not in Maknuune at all. It takes خالي "my maternal uncle" with it — six tokens —
    # so that one is written down too rather than left reading "aunt".
    "خالة":       ("خالة",      "khaale",      "maternal aunt", "NOUN:FS"),
    "أبدا":       ("أبَداً",     "2abadan",     "never, not at all", "ADV"),
    "فرنك":       ("فرَنك",     "frank",       "franc", "NOUN:MS"),
    "ميل":        ("ميل",       "miil",        "mile", "NOUN:MS"),
    "خالي":       ("خالي",      "khaali",      "my maternal uncle", "NOUN:MS"),
    "ضل":         ("ضَلّ",       "d.all",       "stay, remain", "VERB"),
    # ضل takes فضلك "please" with it, six tokens, so فضلك is written down too.
    "فضلك":       ("فَضلَك",    "fad.lak",     "please (من فضلك)", "NOUN:MS"),
    "بلا":        ("بَلا",      "bala",        "without", "PREP"),
    "شفت":        ("شُفت",      "shuft",       "I saw, you saw", "VERB"),
    "قلت":        ("قُلت",      "2ult",        "I said, you said", "VERB"),
    "وكل":        ("وكُلّ",      "wkull",       "and every, and all", "PART"),
    "جنيه":       ("جْنيه",     "jneeh",       "pound (the currency)", "NOUN:MS"),
    # THE NEWS, second half: the modern vocabulary a daily paper needs and a dialect lexicon
    # has no reason to hold — tariffs, sanctions, aftershocks, antibiotics, an envoy.
    "أوروبي":       ("أوروبي",       "2uurubbi",       "European", "ADJ:MS"),
    "جمركي":        ("جُمرُكي",      "jumruki",        "customs, tariff", "ADJ:MS"),
    "جمركية":       ("جُمرُكيّة",    "jumrukiyye",     "customs, tariff (feminine)", "ADJ:FS"),
    "إسرائيلي":     ("إسرائيلي",     "2israa2iili",    "Israeli", "ADJ:MS"),
    "إسرائيلية":    ("إسرائيليّة",   "2israa2iiliyye", "Israeli (feminine)", "ADJ:FS"),
    "إسرائيليين":   ("إسرائيليّين",  "2israa2iiliyyiin", "Israelis", "NOUN:P"),
    "مضيق":         ("مَضيق",        "mad.ii2",        "strait", "NOUN:MS"),
    "أونلاين":      ("أونلاين",      "2onlaayn",       "online", "ADV"),
    "أمريكان":      ("أمريكان",      "2amriikaan",     "Americans", "NOUN:P"),
    "نووي":         ("نَووي",        "nawawi",         "nuclear", "ADJ:MS"),
    "نووية":        ("نَوَويّة",     "nawawiyye",      "nuclear (feminine)", "ADJ:FS"),
    "العليا":       ("العُليا",      "2il3ulya",       "the supreme (court)", "ADJ:FS"),
    "مؤقتا":        ("مُؤَقَّتاً",   "mu2aqqatan",     "temporarily", "ADV"),
    "اتهامات":      ("اتِّهامات",    "ttihaamaat",     "accusations", "NOUN:P"),
    "تكنولوجيا":    ("تكنولوجيا",    "teknolojya",     "technology", "NOUN:FS"),
    "طوارئ":        ("طَوارِئ",      "t.awaari2",      "emergency", "NOUN:P"),
    "بترول":        ("بِترول",       "bitrool",        "oil, petroleum", "NOUN:MS"),
    "قياسي":        ("قياسي",        "2iyaasi",        "record (a record time)", "ADJ:MS"),
    "قياسية":       ("قياسيّة",      "2iyaasiyye",     "record (feminine)", "ADJ:FS"),
    "مشتبه":        ("مُشتَبَه",     "mushtabah",      "suspect", "NOUN:MS"),
    "غالبا":        ("غالباً",       "ghaaliban",      "mostly, probably", "ADV"),
    "شبان":         ("شُبّان",       "shubbaan",       "young men", "NOUN:P"),
    "تنين":        ("تْنين",       "tneen",        "two (and يوم التنين = Monday)", "NUM"),
    "سوتشي":       ("سو تشي",     "suu tshi",     "Suu Kyi", "NOUN_PROP"),
    "هنغاريا":     ("هَنغاريا",    "hanghaarya",   "Hungary", "NOUN_PROP"),
    "يوصلولو":     ("يوصَلولو",    "yoos.aluulu",  "they reach it (an agreement)", "VERB"),
    "ومتضربش":     ("وما تضربش",  "wmaa tud.rubsh","and do not strike", "VERB"),
    "شبين":         ("شَبّين",       "shabbeen",       "two young men", "NOUN:D"),
    "جزئيا":        ("جُزئياً",      "juz2iyyan",      "partly", "ADV"),
    "توصيل":        ("توصيل",        "taws.iil",       "delivery", "NOUN:MS"),
    "كنديين":       ("كَنَديّين",    "kanadiyyiin",    "Canadians", "NOUN:P"),
    "متطابقين":     ("مِتطابقين",    "mit.aab2iin",    "identical", "ADJ:P"),
    "كوكايين":      ("كوكايين",      "kokaayiin",      "cocaine", "NOUN:MS"),
    "سراح":         ("سَراح",        "saraa7",         "release (إطلاق سراح)", "NOUN:MS"),
    "سياسيا":       ("سياسياً",      "siyaasiyyan",    "politically", "ADV"),
    "مدعي":         ("مُدَّعي",      "muddaa3i",       "prosecutor", "NOUN:MS"),
    "مدعين":        ("مُدَّعين",     "muddaa3iin",     "prosecutors", "NOUN:P"),
    "مخاوف":        ("مَخاوِف",      "makhaawif",      "fears, concerns", "NOUN:P"),
    "قسري":         ("قَسري",        "qasri",          "forced, coerced", "ADJ:MS"),
    "مدعوم":        ("مَدعوم",       "mad3uum",        "backed, supported", "ADJ:MS"),
    "مدعومين":      ("مَدعومين",     "mad3uumiin",     "backed, supported (plural)", "ADJ:P"),
    "جنائية":       ("جِنائيّة",     "jinaa2iyye",     "criminal (court)", "ADJ:FS"),
    "إلكتروني":     ("إلكتروني",     "2ilktrooni",     "electronic", "ADJ:MS"),
    "إلكترونية":    ("إلكترونيّة",   "2ilktrooniyye",  "electronic (feminine)", "ADJ:FS"),
    "مفوض":         ("مُفَوَّض",     "mufawwad.",      "commissioner", "NOUN:MS"),
    "رسميا":        ("رَسمياً",      "rasmiyyan",      "officially", "ADV"),
    "كيلومتر":      ("كيلومِتر",     "kiiloomiter",    "kilometre", "NOUN:MS"),
    "كيلومترات":    ("كيلومِترات",   "kiiloomitraat",  "kilometres", "NOUN:P"),
    "ميليشيات":     ("ميليشيات",     "miilishyaat",    "militias", "NOUN:P"),
    "إجرامي":       ("إجرامي",       "2ijraami",       "criminal", "ADJ:MS"),
    "أمور":         ("أُمور",        "2umuur",         "matters, affairs", "NOUN:P"),
    "ارتدادية":     ("ارتِداديّة",   "rtidaadiyye",    "aftershock (هزة ارتدادية)", "ADJ:FS"),
    "نازحين":       ("نازحين",       "naaz7iin",       "displaced people", "NOUN:P"),
    "منتجعات":      ("مُنتَجَعات",   "muntaja3aat",    "resorts", "NOUN:P"),
    "مبررة":        ("مْبَرَّرة",    "mbarrara",       "justified", "ADJ:FS"),
    "جليدي":        ("جَليدي",       "jaliidi",        "glacial, of ice", "ADJ:MS"),
    "سيانيد":       ("سيانيد",       "sayaaniid",      "cyanide", "NOUN:MS"),
    "محكوم":        ("مَحكوم",       "ma7kuum",        "sentenced, condemned", "ADJ:MS"),
    "متسلق":        ("مِتسَلِّق",    "mitsalli2",      "climber", "NOUN:MS"),
    "طارئ":         ("طارِئ",        "t.aari2",        "emergency, urgent", "ADJ:MS"),
    "بمثابة":       ("بمَثابة",      "bmathaabe",      "tantamount to, as good as", "PART"),
    "متعطل":        ("مِتعَطِّل",    "mit3at.t.il",    "out of order, broken down", "ADJ:MS"),
    "ركام":         ("رُكام",        "rukaam",         "rubble", "NOUN:MS"),
    "مقذوف":        ("مَقذوف",       "ma2zuuf",        "projectile, shell", "NOUN:MS"),
    "متفجرات":      ("مُتَفَجِّرات", "mutafajjiraat",  "explosives", "NOUN:P"),
    "نموذج":        ("نَموذَج",      "namuuzaj",       "model", "NOUN:MS"),
    "إنترنت":       ("إنتَرنِت",     "2internet",      "the internet", "NOUN:MS"),
    "فيلم":         ("فيلم",         "fiilm",          "film", "NOUN:MS"),
    "مصفاتين":      ("مَصفاتين",     "mas.faateen",    "two refineries", "NOUN:D"),
    "كليا":         ("كُلّياً",      "kulliyyan",      "entirely", "ADV"),
    "شيفرة":        ("شيفرة",        "shiifra",        "code, cipher", "NOUN:FS"),
    "احتياطا":      ("احتياطاً",     "7tiyaat.an",     "as a precaution", "ADV"),
    "مقتل":         ("مَقتَل",       "ma2tal",         "the killing of", "NOUN:MS"),
    "روبوتات":      ("روبوتات",      "roobotaat",      "robots", "NOUN:P"),
    "مضادة":        ("مُضادّة",      "mud.aadda",      "anti-, counter- (feminine)", "ADJ:FS"),
    "مضادات":       ("مُضادّات",     "mud.aaddaat",    "antibiotics (مضادات حيوية)", "NOUN:P"),
    "حيوية":        ("حَيَويّة",     "7ayawiyye",      "biological, vital", "ADJ:FS"),
    "مكب":          ("مَكَبّ",       "makabb",         "dump, landfill", "NOUN:MS"),
    "حرائق":        ("حَرائِق",      "7araa2i2",       "fires", "NOUN:P"),
    "متعمدة":       ("مِتعَمَّدة",   "mit3ammada",     "deliberate", "ADJ:FS"),
    "ماراثون":      ("ماراثون",      "maaraathoon",    "marathon", "NOUN:MS"),
    "ماليا":        ("مالياً",       "maaliyyan",      "financially", "ADV"),
    "إدارة":        ("إدارة",        "2idaara",        "administration", "NOUN:FS"),
    "مقابض":        ("مَقابِض",      "ma2aabid.",      "handles", "NOUN:P"),
    "مخفية":        ("مَخفيّة",      "makhfiyye",      "hidden (feminine)", "ADJ:FS"),
    "موبيليا":      ("موبيليا",      "mobiilya",       "furniture", "NOUN:FS"),
    "عقوبات":       ("عُقوبات",      "3u2uubaat",      "sanctions", "NOUN:P"),
    "معلنة":        ("مُعلَنة",      "mu3lana",        "declared, announced", "ADJ:FS"),
    "مبعوث":        ("مَبعوث",       "mab3uuth",       "envoy", "NOUN:MS"),
    "مبعوثين":      ("مَبعوثين",     "mab3uuthiin",    "envoys", "NOUN:P"),
    "لاعودة":       ("لا عَودة",     "laa 3awda",      "no return (نقطة اللاعودة)", "NOUN:FS"),
    "مفاجئ":        ("مُفاجِئ",      "mufaaji2",       "sudden", "ADJ:MS"),
    "تلسكوب":       ("تلسكوب",       "teleskoob",      "telescope", "NOUN:MS"),
    "محتجزين":      ("مُحتَجَزين",   "mu7tajaziin",    "detained, held", "ADJ:P"),
    "بضائع":        ("بَضائِع",      "bad.aa2i3",      "goods", "NOUN:P"),
    "جثمان":        ("جُثمان",       "juthmaan",       "body, remains", "NOUN:MS"),
    "مراهقين":      ("مُراهقين",     "muraah2iin",     "teenagers", "NOUN:P"),
    "شظايا":        ("شَظايا",       "shaz.aaya",      "shrapnel", "NOUN:P"),
    "ناجين":        ("ناجين",        "naajiin",        "survivors", "NOUN:P"),
    "مزروعة":       ("مَزروعة",      "mazruu3a",       "planted (feminine)", "ADJ:FS"),
    "مجانية":       ("مَجّانيّة",    "majjaaniyye",    "free of charge", "ADJ:FS"),
    "ظاهرة":        ("ظاهِرة",       "z.aahira",       "phenomenon", "NOUN:FS"),
    "محلفين":       ("مُحَلَّفين",   "mu7allafiin",    "jurors", "NOUN:P"),
    "ديزل":         ("ديزِل",        "diizel",         "diesel", "NOUN:MS"),
    "بريطاني":      ("بريطاني",      "brit.aani",      "British", "ADJ:MS"),
    "هكروا":        ("هَكَروا",      "hakaru",         "they hacked", "VERB"),
    "هكر":          ("هَكَر",        "hakar",          "he hacked", "VERB"),
    "فيديوهاتها":   ("فيديوهاتها",   "fiidyohaatha",   "her videos", "NOUN:P"),
    "يتبادلوا":     ("يِتبادَلوا",   "yitbaadalu",     "they exchange", "VERB"),
    "انعتقلوا":     ("انعَتَقَلوا",  "n3ata2alu",      "they were arrested", "VERB"),
    "انولدوا":      ("انوَلَدوا",    "nwaladu",        "they were born", "VERB"),
    "يطالبوا":      ("يطالبوا",      "yt.aalbu",       "they demand", "VERB"),
    "نقذوا":        ("نَقَذوا",      "na2azu",         "they rescued", "VERB"),
    "يشتروا":       ("يِشتَروا",     "yishtaru",       "they buy", "VERB"),
    "يعطوا":        ("يِعطوا",       "yi3t.u",         "they give", "VERB"),
    "نثق":          ("نِثِق",        "nithi2",         "we trust", "VERB"),
    "تبتعد":        ("تِبتِعِد",     "tibti3id",       "she moves away", "VERB"),
    "صعدت":         ("صَعَّدَت",     "s.a33adat",      "she/it escalated", "VERB"),
    "مسمينه":       ("مْسَمّينه",    "msammiin",       "calling it, naming it", "VERB"),
    "ماسكاه":       ("ماسكاه",       "maaskaa",        "holding it (feminine)", "VERB"),
    "حاطة":         ("حاطّة",        "7aat.t.a",       "having put (feminine)", "VERB"),
    "سان":          ("سان",          "saan",           "San (Aung San Suu Kyi)", "NOUN_PROP"),
    # The short stories. Village life, so: the harvest, courgettes, spiders, ululating at a
    # wedding, and a great deal of resting after work.
    "شاء":        ("شاء",        "shaa2",        "willed (إن شاء الله)", "VERB"),
    "عيال":       ("عْيال",      "3yaal",        "kids, children", "NOUN:P"),
    "رأسا":       ("رأساً",      "ra2san",       "straight, directly", "ADV"),
    "سرا":        ("سِرّاً",     "sirran",       "secretly", "ADV"),
    "زغردوا":     ("زَغرَدوا",   "zaghradu",     "they ululated", "VERB"),
    "محصود":      ("مَحصود",     "ma7s.uud",     "harvested, reaped", "ADJ:MS"),
    "يرتجف":      ("يِرتِجِف",   "yirtijif",     "he shivers, trembles", "VERB"),
    "مرتجف":      ("مِرتِجِف",   "mirtijif",     "shivering, trembling", "ADJ:MS"),
    "عقلاء":      ("عُقَلاء",    "3u2alaa2",     "the wise, sensible people", "NOUN:P"),
    "بسطاء":      ("بُسَطاء",    "busat.aa2",    "simple, plain people", "NOUN:P"),
    "ورايا":      ("ورايا",      "waraaya",      "behind me", "ADV"),
    "عناكب":      ("عَناكِب",    "3anaakib",     "spiders", "NOUN:P"),
    "يستنوا":     ("يِستَنّوا",  "yistannu",     "they wait", "VERB"),
    "انبلوا":     ("انبَلّوا",   "nballu",       "they got soaked", "VERB"),
    "عريانة":     ("عَريانة",    "3aryaane",     "bare, naked (feminine)", "ADJ:FS"),
    "غارق":       ("غارِق",      "ghaari2",      "drowning, sunk deep", "ADJ:MS"),
    "كوسا":       ("كوسا",       "kuusa",        "courgettes, marrows", "NOUN:P"),
    "مزدحم":      ("مِزدَحِم",   "mizda7im",     "crowded", "ADJ:MS"),
    "احترق":      ("احتَرَق",    "7tara2",       "it burned", "VERB"),
    "افترقنا":    ("افتَرَقنا",  "ftara2na",     "we parted", "VERB"),
    "نفترق":      ("نِفتِرِق",   "niftiri2",     "we part", "VERB"),
    "نتقابل":     ("نِتقابَل",   "nit2aabal",    "we meet", "VERB"),
    "ارتحنا":     ("ارتَحنا",    "rta7na",       "we rested", "VERB"),
    "ارتحت":      ("ارتَحت",     "rta7t",        "I rested", "VERB"),
    "ترحيب":      ("تَرحيب",     "tar7iib",      "welcome, welcoming", "NOUN:MS"),
    "قطاف":       ("قْطاف",      "2t.aaf",       "the picking, the harvest", "NOUN:MS"),
    "شتوات":      ("شِتوات",     "shitwaat",     "winters", "NOUN:P"),
    "تراشقنا":    ("تراشَقنا",   "traasha2na",   "we pelted each other", "VERB"),
    "حطلي":       ("حُطّلي",     "7ut.tli",      "put for me", "VERB"),
    "يحطولوا":    ("يحُطّولوا",  "y7ut.t.uulu",  "they put for him", "VERB"),
    "حطولوا":     ("حَطّولوا",   "7at.t.uulu",   "they put for him", "VERB"),
    "وفتخرت":     ("وافتَخَرَت", "wiftakharat",  "and she was proud", "VERB"),
    "يترد":       ("يِتِردّ",    "yitridd",      "he hesitates, holds back", "VERB"),
    "ضاق":        ("ضاق",        "d.aa2",        "it grew tight, narrow", "VERB"),
    "يوسف":       ("يوسِف",      "yuusif",       "Yusuf, Joseph", "NOUN_PROP"),
    # Twenty Stories. Maupassant and Chekhov: a wallet, a lottery ticket, roubles, vodka,
    # a privy councillor and a great many people being called fools.
    "تخين":       ("تْخين",      "tkhiin",       "fat, thick", "ADJ:MS"),
    "ظلين":     ("ظِلّين",    "z.illeen",   "two shadows", "NOUN:D"),
    "نادل":     ("نادِل",    "naadil",     "waiter", "NOUN:MS"),
    "شناتي":    ("شْناتي",   "shnaati",    "bags, cases", "NOUN:P"),
    "هممم":     ("هممم",     "hmmm",       "hmm (thinking it over)", "INTJ"),
    "ثقوب":       ("ثُقوب",      "thu2uub",      "holes", "NOUN:P"),
    "مؤمن":       ("مْؤَمَّن",   "mu2amman",     "insured", "ADJ:MS"),
    "محفظة":      ("مَحفَظة",    "ma7faz.a",     "wallet, purse", "NOUN:FS"),
    "بقشيش":      ("بَقشيش",     "ba2shiish",    "tip, gratuity", "NOUN:MS"),
    "صايغ":       ("صايِغ",      "s.aayigh",     "jeweller, goldsmith", "NOUN:MS"),
    "صحون":       ("صُحون",      "s.u7uun",      "dishes, plates", "NOUN:P"),
    "أغبيا":      ("أغبِيا",     "2aghbiya",     "fools, stupid people", "NOUN:P"),
    "أذكيا":      ("أذكِيا",     "2azkiya",      "clever people", "NOUN:P"),
    "روبل":       ("روبل",       "ruubl",        "rouble", "NOUN:MS"),
    "روبلات":     ("روبلات",     "ruublaat",     "roubles", "NOUN:P"),
    "أحمق":       ("أحمَق",      "2a7ma2",       "fool, idiot", "NOUN:MS"),
    "ظلال":       ("ظْلال",      "z.laal",       "shadows", "NOUN:P"),
    "محدود":      ("مَحدود",     "ma7duud",      "limited", "ADJ:MS"),
    "خردوات":     ("خُردَوات",   "khurdawaat",   "haberdashery, small wares", "NOUN:P"),
    "شراء":       ("شِراء",      "shiraa2",      "buying, purchase", "NOUN:MS"),
    "متوحش":      ("مِتوَحِّش",  "mitwa77ish",   "savage, wild", "ADJ:MS"),
    "سمان":       ("سُمان",      "sumaan",       "quail", "NOUN:P"),
    "قفاز":       ("قُفّاز",     "2uffaaz",      "glove", "NOUN:MS"),
    "مستشار":     ("مُستَشار",   "musteshaar",   "councillor, adviser", "NOUN:MS"),
    "يانصيب":     ("يانَصيب",    "yaanas.iib",   "lottery", "NOUN:MS"),
    "قمامة":      ("قُمامة",     "2umaame",      "rubbish", "NOUN:FS"),
    "فودكا":      ("فودكا",      "voodka",       "vodka", "NOUN:FS"),
    "مهترئ":      ("مِهتَرِئ",   "mihtari2",     "worn out, threadbare", "ADJ:MS"),
    "لزجة":       ("لَزجة",      "lazje",        "sticky (feminine)", "ADJ:FS"),
    "انطباع":     ("انطِباع",    "nt.ibaa3",     "impression", "NOUN:MS"),
    "مؤبد":       ("مُؤَبَّد",   "mu2abbad",     "for life (a life sentence)", "ADJ:MS"),
    "مسموح":      ("مَسموح",     "masmuu7",      "allowed, permitted", "ADJ:MS"),
    "بيانو":      ("بيانو",      "byaano",       "piano", "NOUN:MS"),
    "كيميا":      ("كيميا",      "kiimya",       "chemistry", "NOUN:FS"),
    "مصابيح":     ("مَصابيح",    "mas.aabii7",   "lamps", "NOUN:P"),
    "مشيئة":      ("مَشيئة",     "mashii2a",     "will (God's will)", "NOUN:FS"),
    "ممشط":       ("مْمَشَّط",   "mmashshat.",   "combed", "ADJ:MS"),
    "مشققة":      ("مْشَقَّقة",  "msha22a2a",    "cracked, chapped (feminine)", "ADJ:FS"),
    "غثى":        ("غَثى",       "ghatha",       "he felt sick, nauseous", "VERB"),
    "أتقيأ":      ("أتقَيَّأ",   "2at2ayya2",    "I vomit", "VERB"),
    "مقترب":      ("مِقتَرِب",   "mi2tarib",     "approaching, drawing near", "ADJ:MS"),
    "تلاتا":      ("التَّلاتا",  "2ittalaata",   "Tuesday", "NOUN_PROP"),
    "عصيدة":      ("عَصيدة",     "3as.iide",     "porridge, gruel", "NOUN:FS"),
    "احترقت":     ("احتَرَقَت",  "7tara2at",     "she/it burned down", "VERB"),
    "اشترت":      ("اشتَرَت",    "shtarat",      "she bought", "VERB"),
    "واستحت":     ("واستَحَت",   "wista7at",     "and she was ashamed", "VERB"),
    "استلفوه":    ("استَلَفوه",  "stalafuu",     "they borrowed it", "VERB"),
    "بيخبوا":     ("بيخَبّوا",   "byikhabbu",    "they hide (something)", "VERB"),
    "تستنوا":     ("تِستَنّوا",  "tistannu",     "you wait (plural)", "VERB"),
    "وعطتني":     ("وعَطَتني",   "w3at.atni",    "and she gave me", "VERB"),
    "اختفت":      ("اختَفَت",    "khtafat",      "she/it disappeared", "VERB"),
    "وخوذ":       ("وخوذ",       "wkhuuz",       "and take (imperative)", "VERB"),
    "بيتباع":     ("بيتباع",     "byitbaa3",     "it is sold", "VERB"),
    "بيعطوه":     ("بيعطوه",     "byi3t.uu",     "they give him", "VERB"),
    "بيتألم":     ("بيتأَلَّم",  "byit2allam",   "he is in pain", "VERB"),
    "بيتقابلوا":  ("بيتقابَلوا", "byit2aabalu",  "they meet each other", "VERB"),
    "ومسابق":     ("ومْسابِق",   "wmsaabi2",     "and woodcock (game birds)", "NOUN:P"),
    "ويستبدل":    ("ويِستَبدِل", "wyistabdil",   "and he replaces", "VERB"),
    "سأقفله":     ("سأقفِله",    "sa2a2filu",    "I shall close it", "VERB"),
    "ولوهلة":     ("ولوَهلة",    "wlawahle",     "and for a moment", "ADV"),
    # Sherlock Holmes. Ten stories, and the vocabulary is a Victorian crime scene: a stable, a
    # noose, handcuffs, plaster of Paris, a magnifying glass, a sundial, an air rifle.
    "إسطبل":      ("إسطَبل",     "2is.t.abl",    "stable", "NOUN:MS"),
    "مساء":     ("مَسا",     "masa",       "evening", "NOUN:MS"),
    "بحيرة":    ("بُحَيرة",   "bu7ayra",    "lake", "NOUN:FS"),
    "حقيبة":    ("حَقيبة",   "7a2iibe",    "case, bag", "NOUN:FS"),
    "جايزة":    ("جايزة",    "jaayze",     "prize, reward", "NOUN:FS"),
    "فقرا":     ("فُقَرا",    "fu2ara",     "the poor", "NOUN:P"),
    "فهد":      ("فَهد",     "fahd",       "cheetah, leopard", "NOUN:MS"),
    "غجر":        ("غَجَر",      "ghajar",       "gypsies", "NOUN:P"),
    "غجري":       ("غَجَري",     "ghajari",      "gypsy", "ADJ:MS"),
    "شريط":       ("شْريط",      "shriit.",      "band, ribbon, tape", "NOUN:MS"),
    "كلبشات":     ("كَلَبشات",   "kalabshaat",   "handcuffs", "NOUN:P"),
    "حانة":       ("حانة",       "7aana",        "tavern, pub", "NOUN:FS"),
    "ريف":        ("ريف",        "riif",         "countryside", "NOUN:MS"),
    "جبس":        ("جِبس",       "jibs",         "plaster", "NOUN:MS"),
    "مقصورة":     ("مَقصورة",    "ma2s.uura",    "compartment (of a train)", "NOUN:FS"),
    "هوائية":     ("هَوائيّة",   "hawaa2iyye",   "air- (بندقية هوائية = air rifle)", "ADJ:FS"),
    "هوائي":      ("هَوائي",     "hawaa2i",      "air-, pneumatic", "ADJ:MS"),
    "خدوش":       ("خُدوش",      "khuduush",     "scratches", "NOUN:P"),
    "حاخام":      ("حاخام",      "7aakhaam",     "rabbi", "NOUN:MS"),
    "أوبرا":      ("أوبرا",      "2obra",        "opera", "NOUN:FS"),
    "صارمة":      ("صارمة",      "s.aarme",      "stern, strict (feminine)", "ADJ:FS"),
    "سيجار":      ("سيجار",      "siigaar",      "cigar", "NOUN:MS"),
    "سيجارة":     ("سيجارة",     "siigaara",     "cigarette", "NOUN:FS"),
    "رفوف":       ("رْفوف",      "rfuuf",        "shelves", "NOUN:P"),
    "مفتعل":      ("مِفتَعَل",   "mifta3al",     "staged, put on", "ADJ:MS"),
    "مليونير":    ("مِليونير",   "milyoneer",    "millionaire", "NOUN:MS"),
    "جرايم":      ("جَرايِم",    "jaraayim",     "crimes", "NOUN:P"),
    "أنشوطة":     ("أُنشوطة",    "2unshuut.a",   "noose, slip-knot", "NOUN:FS"),
    "سرطان":      ("سَرَطان",    "sarat.aan",    "cancer", "NOUN:MS"),
    "قضيب":       ("قَضيب",      "2ad.iib",      "rod, bar", "NOUN:MS"),
    "زهور":       ("زُهور",      "zuhuur",       "flowers", "NOUN:P"),
    "جارح":       ("جارِح",      "jaari7",       "predatory, savage", "ADJ:MS"),
    "مكبرة":      ("مْكَبِّرة",  "mkabbira",     "magnifying (عدسة مكبرة = magnifying glass)", "ADJ:FS"),
    "بطانة":      ("بِطانة",     "bit.aana",     "lining", "NOUN:FS"),
    "فاصولية":    ("فاصولية",    "faas.uulya",   "beans", "NOUN:P"),
    "مسائية":     ("مَسائيّة",   "masaa2iyye",   "evening (of a newspaper)", "ADJ:FS"),
    "مزرور":      ("مَزرور",     "mazruur",      "buttoned up", "ADJ:MS"),
    "بائع":       ("بائِع",      "baa2i3",       "seller, dealer", "NOUN:MS"),
    "متراهنين":   ("مِتراهنين",  "mitraahniin",  "betting, wagering (plural)", "ADJ:P"),
    "مشعث":       ("مْشَعَّث",   "msha33ath",    "dishevelled, tousled", "ADJ:MS"),
    "مكياج":      ("مِكياج",     "mikyaaj",      "make-up", "NOUN:MS"),
    "مصدق":       ("مْصَدِّق",   "ms.addi2",     "believing, convinced", "ADJ:MS"),
    "حدوته":      ("حَدّوتة",    "7adduute",     "tale, story", "NOUN:FS"),
    "مصباح":      ("مِصباح",     "mis.baa7",     "lamp", "NOUN:MS"),
    "تصفيق":      ("تَصفيق",     "tas.fii2",     "applause, clapping", "NOUN:MS"),
    "كيميائية":   ("كيميائيّة",  "kiimyaa2iyye", "chemical (feminine)", "ADJ:FS"),
    "كيمياء":     ("كيمياء",     "kiimyaa2",     "chemistry", "NOUN:FS"),
    "بلياردو":    ("بِلياردو",   "bilyaardo",    "billiards", "NOUN:MS"),
    "مزولة":      ("مَزولة",     "mazuula",      "sundial", "NOUN:FS"),
    "ملامح":      ("مَلامِح",    "malaami7",     "features (of a face)", "NOUN:P"),
    "بروفيسور":   ("بروفيسور",   "brofisoor",    "professor", "NOUN:MS"),
    "غايرة":      ("غايرة",      "ghaayra",      "jealous (feminine)", "ADJ:FS"),
    "رذاذ":       ("رَذاذ",      "razaaz",       "spray, fine mist", "NOUN:MS"),
    "صعود":       ("صُعود",      "s.u3uud",      "climbing, going up", "NOUN:MS"),
    "مسنودة":     ("مَسنودة",    "masnuude",     "propped, leaning (feminine)", "ADJ:FS"),
    "ملف":        ("مَلَفّ",     "malaff",       "file, dossier", "NOUN:MS"),
    "براندي":     ("براندي",     "braandi",      "brandy", "NOUN:MS"),
    "مختبر":      ("مُختَبَر",   "mukhtabar",    "laboratory", "NOUN:MS"),
    "زنبرك":      ("زُنبُرُك",   "zunburuk",     "spring (the coiled kind)", "NOUN:MS"),
    "ثواني":      ("ثَواني",     "thawaani",     "seconds", "NOUN:P"),
    "مهترية":     ("مِهتَرية",   "mihtariya",    "worn out, frayed (feminine)", "ADJ:FS"),
    "اشمئزاز":    ("اشمِئزاز",   "shmi2zaaz",    "disgust, revulsion", "NOUN:MS"),
    "كرام":       ("كِرام",      "kiraam",       "noble, honourable (plural)", "ADJ:P"),
    "فهرس":       ("فِهرِس",     "fihris",       "index", "NOUN:MS"),
    "بينما":      ("بينَما",     "beenama",      "while, whereas", "PART"),
    "إيطالي":     ("إيطالي",     "2iit.aali",    "Italian", "ADJ:MS"),
    "إيطالية":    ("إيطاليّة",   "2iit.aaliyye", "Italian (feminine)", "ADJ:FS"),
    "البريطانية": ("البريطانيّة", "2ilbrit.aaniyye", "the British (feminine)", "ADJ:FS"),
    "أفريقيا":    ("أفريقيا",    "2afrii2ya",    "Africa", "NOUN_PROP"),
    "كونتيسة":    ("كونتيسة",    "kontiise",     "countess", "NOUN:FS"),
    "سبعمية":     ("سَبعميّة",   "sab3amiyye",   "seven hundred", "NUM"),
    "أربعمية":    ("أربَعميّة",  "2arba3miyye",  "four hundred", "NUM"),
    "سبعتعشر":    ("سَبعَتعشَر", "sab3ata3shar", "seventeen", "NUM"),
    "أبريل":      ("أبريل",      "2abriil",      "April", "NOUN_PROP"),
    "يناير":      ("يَناير",     "yanaayir",     "January", "NOUN_PROP"),
    "فبراير":     ("فبراير",     "fibraayir",    "February", "NOUN_PROP"),
    "انسكر":      ("انسَكَر",    "nsakar",       "it was shut, locked", "VERB"),
    "أطفوا":      ("أطفوا",      "2at.fu",       "they put out (a light)", "VERB"),
    "بيستنوه":    ("بيستَنّوه",  "byistannuu",   "they wait for him", "VERB"),
    "اتباعت":     ("اتباعَت",    "tbaa3at",      "she/it was sold", "VERB"),
    "انلاحق":     ("انلاحَق",    "nlaa7a2",      "he was chased, pursued", "VERB"),
    "بيغلوا":     ("بيغلوا",     "byighlu",      "they boil", "VERB"),
    "وقضت":       ("وقَضَت",     "w2ad.at",      "and she spent (time)", "VERB"),
    "تتأثر":      ("تِتأثَّر",   "tit2aththar",  "she is affected, moved", "VERB"),
    "انزلقت":     ("انزَلَقَت",  "nzala2at",     "she/it slipped", "VERB"),
    "بيتقاربوا":  ("بيتقاربوا",  "byit2aarabu",  "they come close together", "VERB"),
    "ينادوه":     ("ينادوه",     "ynaaduu",      "they call him", "VERB"),
    "وخادمتك":    ("وخادِمتَك",  "wkhaadimtak",  "and your servant (feminine)", "NOUN:FS"),
    # Around the World in 80 Days. A book about consulates, timetables and steamships, so the
    # missing words are the machinery of Victorian travel plus one Indian acrobat troupe.
    "بهلوان":   ("بَهلَوان",  "bahlawaan",  "acrobat", "NOUN:MS"),
    "بهلوانات": ("بَهلَوانات", "bahlawaanaat","acrobats", "NOUN:P"),
    "كمساري":   ("كُمساري",  "kumsaari",   "ticket conductor", "NOUN:MS"),
    "قنصل":     ("قُنصُل",   "2uns.ul",    "consul", "NOUN:MS"),
    "قنصلية":   ("قُنصُليّة",  "2uns.uliyye","consulate", "NOUN:FS"),
    "أنوف":     ("أنوف",     "2unuuf",     "noses", "NOUN:P"),
    "جاموس":    ("جاموس",    "jaamuus",    "buffalo", "NOUN:MS"),
    "سائق":     ("سائِق",    "saa2i2",     "driver", "NOUN:MS"),
    "قاطرة":    ("قاطِرة",   "2aat.ira",   "locomotive, engine", "NOUN:FS"),
    "زلاجة":    ("زَلّاجة",   "zallaaja",   "sledge, sled", "NOUN:FS"),
    "موانئ":    ("مَوانِئ",   "mawaani2",   "ports, harbours", "NOUN:P"),
    "إطفاء":    ("إطفاء",    "2it.faa2",   "putting out (fire), extinguishing", "NOUN:MS"),
    "مكافأة":   ("مُكافأة",  "mukaafa2a",  "reward", "NOUN:FS"),
    "جورب":     ("جَورَب",   "jawrab",     "sock", "NOUN:MS"),
    "جوارب":    ("جَوارِب",   "jawaarib",   "socks", "NOUN:P"),
    "ماكينة":   ("ماكينة",   "maakiine",   "engine, machine", "NOUN:FS"),
    "بورصة":    ("بورصة",    "buurs.a",    "stock exchange", "NOUN:FS"),
    "صواري":    ("صَواري",   "s.awaari",   "masts", "NOUN:P"),
    "كابينة":   ("كابينة",   "kaabiine",   "cabin", "NOUN:FS"),
    "صحرا":     ("صَحرا",    "s.a7ra",     "desert", "NOUN:FS"),
    "أحرار":    ("أحرار",    "2a7raar",    "free men", "NOUN:P"),
    "خشن":      ("خِشِن",    "khishin",    "rough, coarse", "ADJ:MS"),
    "موقوف":    ("مَوقوف",   "maw2uuf",    "under arrest, detained", "ADJ:MS"),
    "مصدوم":    ("مَصدوم",   "mas.duum",   "shocked, stunned", "ADJ:MS"),
    "ماهر":     ("ماهِر",    "maahir",     "skilful", "ADJ:MS"),
    "متأكد":    ("مِتأكِّد",   "mit2akkid",  "sure, certain", "ADJ:MS"),
    "شاكرة":    ("شاكرة",    "shaakra",    "grateful (feminine)", "ADJ:FS"),
    "مشعول":    ("مَشعول",   "mash3uul",   "lit, alight", "ADJ:MS"),
    "مشعولة":   ("مَشعولة",  "mash3uule",  "lit, alight (feminine)", "ADJ:FS"),
    # Hundreds. Palestinian says each as one word; the lexicon has only مية.
    "مئتين":    ("مِتين",    "miteen",     "two hundred", "NUM"),
    "تلاتمية":  ("تلاتميّة",  "tlatmiyye",  "three hundred", "NUM"),
    "خمسمية":   ("خَمسميّة",  "khamsmiyye", "five hundred", "NUM"),
    "تمانمية":  ("تمانميّة",  "tmanmiyye",  "eight hundred", "NUM"),
    "ستاشر":    ("سِتّاشَر",   "sittaashar", "sixteen", "NUM"),
    "تمانتعشر": ("تمانتَعشَر", "tmanta3shar","eighteen", "NUM"),
    # Verbs and adverbs.
    "دلني":     ("دِلّني",    "dillni",     "show me the way", "VERB"),
    "استخبوا":  ("استَخَبّوا",  "stakhabbu",  "they hid", "VERB"),
    "بنتقابل":  ("بنِتقابَل",  "bnit2aabal", "we meet", "VERB"),
    "بيتسلقوا": ("بيتسَلَّقوا", "byitsalla2u","they climb", "VERB"),
    "واشتروا":  ("واشتَروا",  "wishtaru",   "and they bought", "VERB"),
    "أخيرا":    ("أخيراً",    "2akhiiran",  "finally, at last", "ADV"),
    "نظريا":    ("نَظَرياً",   "naz.ariyyan","in theory", "ADV"),
    "فعلا":     ("فِعلاً",    "fi3lan",     "indeed, actually", "ADV"),
    # Treasure Island. A sea story with a ship's chandlery in it — a spyglass, gunpowder, tar,
    # a sealed packet, a parrot — and none of it is in a lexicon of spoken Palestinian.
    "منظار":    ("مِنظار",   "minz.aar",   "spyglass, telescope", "NOUN:MS"),
    "بارود":    ("بارود",    "baaruud",    "gunpowder", "NOUN:MS"),
    "صفير":     ("صَفير",    "s.afiir",    "whistling", "NOUN:MS"),
    "رزمة":     ("رِزمة",    "rizme",      "bundle, packet", "NOUN:FS"),
    "شراب":     ("شَراب",    "sharaab",    "drink, liquor", "NOUN:MS"),
    "ببغا":     ("بَبَّغا",    "babbagha",   "parrot", "NOUN:MS"),
    "صلبان":    ("صُلبان",   "s.ulbaan",   "crosses (on a map)", "NOUN:P"),
    "هدنة":     ("هُدنة",    "hudne",      "truce", "NOUN:FS"),
    "خليج":     ("خَليج",    "khaliij",    "bay, inlet", "NOUN:MS"),
    "مقبض":     ("مَقبَض",   "ma2bad.",    "hilt, handle", "NOUN:MS"),
    "جمارك":    ("جَمارِك",   "jamaarik",   "customs (the service)", "NOUN:P"),
    "قطران":    ("قَطران",   "2at.raan",   "tar", "NOUN:MS"),
    "جذوع":     ("جْذوع",    "jzuu3",      "tree trunks", "NOUN:P"),
    "قتال":     ("قِتال",    "2itaal",     "fighting, combat", "NOUN:MS"),
    "ماعز":     ("ماعِز",    "maa3iz",     "goats", "NOUN:P"),
    "أدميرال":  ("أدميرال",  "2admiraal",  "admiral (the Admiral Benbow inn)", "NOUN:MS"),
    "مختوم":    ("مَختوم",   "makhtuum",   "sealed", "ADJ:MS"),
    "شتوي":     ("شِتوي",    "shitwi",     "wintry", "ADJ:MS"),
    "شاحب":     ("شاحِب",    "shaa7ib",    "pale", "ADJ:MS"),
    "مغمى":     ("مُغمى",    "mughma",     "unconscious (مغمى عليه)", "ADJ:MS"),
    "ممدد":     ("مْمَدَّد",    "mmaddad",    "stretched out, lying flat", "ADJ:MS"),
    "مسمر":     ("مْسَمَّر",    "msammar",    "nailed down", "ADJ:MS"),
    "مخلوع":    ("مَخلوع",   "makhluu3",   "wrenched off, unhinged", "ADJ:MS"),
    "مبتسم":    ("مِبتَسِم",   "mibtasim",   "smiling", "ADJ:MS"),
    "مقطوع":    ("مَقطوع",   "ma2t.uu3",   "cut off, severed", "ADJ:MS"),
    "غلطان":    ("غَلطان",   "ghalt.aan",  "mistaken, in the wrong", "ADJ:MS"),
    "رامي":     ("رامي",     "raami",      "marksman, shooter", "NOUN:MS"),
    "إنجلترا":  ("إنجِلترا",  "2injiltera", "England", "NOUN_PROP"),
    "إنجليزي":  ("إنجليزي",  "2injliizi",  "English", "ADJ:MS"),
    # Teen numerals again — Palestinian says them as one word, the lexicon lists the MSA shapes.
    "تلاتعشر":  ("تلاتَعشَر",  "talata3shar","thirteen", "NUM"),
    "أربعتعشر": ("أربَعتَعشَر", "2arba3ta3shar", "fourteen", "NUM"),
    "خمستاشر":  ("خَمستاشَر",  "khamstaashar","fifteen", "NUM"),
    "تسعتعشر":  ("تِسعَتعشَر",  "tis3ata3shar","nineteen", "NUM"),
    # Verbs.
    "اخترتهم":  ("اخترتهم",  "khtarthum",  "I chose them", "VERB"),
    "جات":      ("جات",      "jaat",       "she came", "VERB"),
    "اختلطت":   ("اختَلَطَت",  "khtalat.at", "she/it got mixed up", "VERB"),
    "بيتترددوا":("بيتردَّدوا", "byitraddadu","they hesitate", "VERB"),
    "بيستنوا":  ("بيستَنّوا",  "byistannu",  "they wait", "VERB"),
    "ضاقت":     ("ضاقَت",    "d.aa2at",    "she/it narrowed, tightened", "VERB"),
    "بصق":      ("بَصَق",     "bas.a2",     "spit, spat", "VERB"),
    "قمت":      ("قُمت",     "2umt",       "I got up", "VERB"),
    "جدف":      ("جَدَّف",     "jaddaf",     "he rowed", "VERB"),
    "أجدف":     ("أجَدِّف",    "2ajaddif",   "I row", "VERB"),
    "جدفت":     ("جَدَّفت",    "jaddaft",    "I rowed", "VERB"),
    "بيغنوا":   ("بيغَنّوا",   "byighannu",  "they sing", "VERB"),
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

# ==========================================================================================
# HOW TO SAY A NUMBER. This used to be a lookup table of thirteen values, and everything else
# fell through to str(val) — the card for 45 said its pronunciation was "45". It also only
# accepted ARABIC-INDIC digits, which meant that Around the World in 80 Days, a book whose plot
# is a railway timetable, had 74 tokens of bare Western numerals with no card behind them: the
# clock times (8:45, 7:25), the wager (20,000 pounds), the year 1872.
#
# Generated rather than listed, because a table stops at whatever number somebody remembered to
# add and the next book brings a bigger one. Palestinian builds numbers the ordinary Levantine
# way: units first in the compound (waaHad w-3ishriin, not 3ishriin waaHad), and the teens and
# the hundreds are single words rather than phrases.
_UNITS = ["sifr", "waaHad", "tneen", "tlaate", "2arb3a", "khamse",
          "sitte", "sab3a", "tmaanye", "tis3a"]
_TEENS = ["3ashara", "iH.da3sh", "tna3sh", "tlat.t.a3sh", "2arba3ta3sh", "khamsta3sh",
          "sitta3sh", "sab3ata3sh", "tmanta3sh", "tis3ata3sh"]
_TENS = {2: "3ishriin", 3: "talaatiin", 4: "2arb3iin", 5: "khamsiin",
         6: "sittiin", 7: "sab3iin", 8: "tmaaniin", 9: "tis3iin"}
_HUNDREDS = {1: "miyye", 2: "miteen", 3: "tlatmiyye", 4: "2arba3miyye", 5: "khamsmiyye",
             6: "sittmiyye", 7: "sab3amiyye", 8: "tmanmiyye", 9: "tis3amiyye"}


def say_number(n):
    """-> how a Palestinian speaker reads the integer n aloud. Handles 0..99,999."""
    if n < 10:
        return _UNITS[n]
    if n < 20:
        return _TEENS[n - 10]
    if n < 100:
        tens, unit = divmod(n, 10)
        return _TENS[tens] if not unit else '%s w-%s' % (_UNITS[unit], _TENS[tens])
    if n < 1000:
        h, rest = divmod(n, 100)
        return _HUNDREDS[h] if not rest else '%s w-%s' % (_HUNDREDS[h], say_number(rest))
    th, rest = divmod(n, 1000)
    head = '2alf' if th == 1 else ('2alfeen' if th == 2 else '%s 2aalaaf' % say_number(th))
    return head if not rest else '%s w-%s' % (head, say_number(rest))


def numeral(surface):
    """-> word dict for a numeral written in either digit set, else None.

    Both sets on purpose. The books are translated prose and use Western digits; the news
    scraper brings back Arabic-Indic ones. Neither is a word the lexicon can hold, and a reader
    who taps 1872 wants the same thing either way — the value and how to say it.
    """
    core = surface.strip("،.؟!,")
    # A numeral in the paper carries clitics like any other word, and a writer separates them
    # from the digits with a tatweel: لـ١١٢ "to 112", الـ١٤ "the 14", و٨٣ "and 83", بـ٦٥, ٥٢٪.
    # Every one of those was untappable, which is silly — the clitic is the easy half.
    m = re.match('^(?:و|ف)?(?:لل|ال|ب|ل|ك|ع)?\u0640?([0-9\u0660-\u0669]+)\u0640?[\u066a%]?$', core)
    if m:
        core = m.group(1)
    if not core:
        return None
    if all(ch in _AR_DIGITS for ch in core):
        digits = "".join(str(_AR_DIGITS.index(ch)) for ch in core)
    elif core.isdigit() and core.isascii():
        digits = core
    else:
        return None
    val = int(digits)
    say = say_number(val) if val < 100000 else digits
    return {"surface": surface, "root": "—", "lemma": core, "form": core,
            "caphi_raw": say, "caphi": say, "gloss": f"{val}", "analysis": "NOUN_NUM",
            "maknuune_id": None, "village": None,
            "vocalized": core, "vocalized_from": "curated",
            "provenance": "curated:numeral"}

# ==========================================================================================
# TOKENS THAT ARE NOT ARABIC WORDS. Two kinds turn up in translated prose and neither is a
# lexicon failure, though both counted as one:
#
#   LATIN SCRIPT. The Dancing Men turns on an English cipher, so the Arabic page carries
#   ELSIE PREPARE TO MEET THY GOD and the letter frequencies E T A O I N — 33 tokens in
#   Sherlock Holmes that no Arabic lexicon will ever hold.
#
#   A SINGLE ARABIC LETTER, used as an initial: the two on the hat in The Blue Carbuncle are
#   ه and ب. The letter is not the word.
#
# Read LAST, after the curated tables and the lexicon have both had their turn, so it cannot
# shadow anything: و and ب and ل are one-letter words as well as letters, and they must stay
# words. What it gives back is honest — the token as written, said as what it is.
_LETTER_NAMES = {
    'ا': '2alif', 'ب': 'baa2', 'ت': 'taa2', 'ث': 'thaa2', 'ج': 'jiim', 'ح': '7aa2',
    'خ': 'khaa2', 'د': 'daal', 'ذ': 'zaal', 'ر': 'raa2', 'ز': 'zaay', 'س': 'siin',
    'ش': 'shiin', 'ص': 's.aad', 'ض': 'd.aad', 'ط': 't.aa2', 'ظ': 'z.aa2', 'ع': '3een',
    'غ': 'gheen', 'ف': 'faa2', 'ق': '2aaf', 'ك': 'kaaf', 'ل': 'laam', 'م': 'miim',
    'ن': 'nuun', 'ه': 'haa2', 'و': 'waaw', 'ي': 'yaa2'}


def _shell(surface, lemma, caphi, gloss, pos, prov):
    return {"surface": surface, "root": "—", "lemma": lemma, "form": lemma,
            "caphi_raw": caphi, "caphi": caphi, "gloss": gloss, "analysis": pos,
            "maknuune_id": None, "village": None,
            "vocalized": lemma, "vocalized_from": "curated", "provenance": prov}


def not_a_word(surface):
    """-> word dict for a token no Arabic lexicon can hold, else None. Consulted LAST."""
    core = surface.strip("،.؟!?,:;\"'()")
    if not core:
        return None
    # An Arabic clitic glued straight onto a Latin word: الBBC "the BBC", وBBC, لـBBC. The
    # word is still English; only the article in front of it is not.
    lat = re.match('^(?:و|ف)?(?:لل|ال|ب|ل|ك|ع)?\u0640?([A-Za-z][A-Za-z0-9]*)$', core)
    if lat and not core.isascii():
        return _shell(surface, lat.group(1), lat.group(1),
                      'English, printed in the story as it stands', 'FOREIGN',
                      'curated:latin-script')
    if core.isascii() and any(ch.isalpha() for ch in core) and core.replace("'", "").isalnum():
        return _shell(surface, core, core,
                      'English, printed in the story as it stands', 'FOREIGN',
                      'curated:latin-script')
    if len(core) == 1:
        # The hamza-carrying alefs and the two tied letters are the SAME letter to a reader
        # signing an initial: Chekhov's complaint book is signed أ. ز. and إ. يارمونكين.
        name = _LETTER_NAMES.get({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي',
                                  'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي'}.get(core, core))
        if name:
            return _shell(surface, core, name, 'the letter %s' % name,
                          'LETTER', 'curated:letter')
    return None


# ==========================================================================================
# THE TEENS AND THE HUNDREDS, EVERY WAY THEY GET SPELLED. Palestinian says these as one word
# and nobody agrees how to write it: fifteen turns up as خمستعش, خمسطعش, خمستاشر, خمستعشر and
# بخمستعش, and each spelling was its own untappable token. Twenty-two of them in the news
# alone, all of the same seven numbers.
#
# Generated, for the same reason say_number() is: a hand-list stops at whatever spelling
# somebody happened to meet, and the next day's paper brings another. setdefault so an entry
# already written by hand keeps its own pronunciation.
_TEEN_UNITS = {'حدا': 11, 'اطنا': 12, 'اتنا': 12, 'تلت': 13, 'تلات': 13, 'تلط': 13, 'أربع': 14,
               'اربع': 14, 'خمس': 15, 'خمست': 15, 'ست': 16, 'سبع': 17, 'تمن': 18,
               'تمان': 18, 'تسع': 19}
_TEEN_TAILS = ('عش', 'عشر', 'اعش', 'اعشر', 'تعش', 'طعش', 'تاعش', 'طاعش', 'تعشر', 'طعشر',
               'تاعشر', 'طاعشر', 'اشر', 'تاشر', 'طاشر')
# 100 and 200 are deliberately NOT here. مية is already in the lexicon, and its construct ميت
# is the word for "dead"; ميتين is "two dead" far more often than "two hundred". Generating them
# turned ميت، ميتة، ميتين، وميت and بمية "with water" into numbers — measured, then removed. Only
# the compounds, which are unambiguous.
_HUND = {'تلتمية': 3, 'تلاتمية': 3, 'أربعمية': 4, 'خمسمية': 5,
         'ستمية': 6, 'سبعمية': 7, 'تمنمية': 8, 'تمانمية': 8, 'تسعمية': 9}

for _stem, _val in _TEEN_UNITS.items():
    for _tail in _TEEN_TAILS:
        MODERN.setdefault(_stem + _tail, (_stem + _tail, say_number(_val), str(_val), 'NUM'))
for _w, _h in _HUND.items():
    MODERN.setdefault(_w, (_w, say_number(_h * 100), str(_h * 100), 'NUM'))
    # ...ميت is the construct form, said before a counted noun: خمسميت شخص "five hundred people".
    if _w.endswith('مية'):
        MODERN.setdefault(_w[:-1] + 'ت', (_w[:-1] + 'ت', say_number(_h * 100),
                                          str(_h * 100), 'NUM'))

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
