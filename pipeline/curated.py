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
