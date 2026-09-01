#!/usr/bin/env python3
"""Vocalized Hebrew -> Modern Israeli pronunciation. Deterministic, no lexicon.

This is the Hebrew answer to the Arabic side's CAPHI++ field, and it exists because the two
languages put the hard part in different places. Maknuune SHIPS a pronunciation per entry, and
the Arabic pipeline's difficulty is vocalization: only 46% of corpus words get their vowels
straight from the lexicon. Hebrew is the mirror image. No open Hebrew lexicon carries reliable
per-entry phonetics -- but it doesn't need to, because once a word has niqqud its Israeli
pronunciation is a FUNCTION of the spelling. So we don't look pronunciation up. We compute it,
and the only thing that has to be looked up is the niqqud.

What "Modern Israeli" means here, since it is a choice and not a fact:

  * The historical distinctions are gone, as they are in ordinary Tel Aviv speech.
    ת = ט = t.  כּ = ק = k.  ב = ו = v.  א = ע = nothing (a hiatus at most).  ח = כ = x.
    We are teaching people to be understood at a table, not to read Tiberian.
  * ר is the uvular [R]. Romanized plainly as "r" -- writing "R" would suggest a contrast
    that modern Hebrew does not have.
  * Five vowels: a e i o u. Qamatz and patach both -> a; tsere and segol both -> e. Qamatz
    qatan is the one exception and it is genuinely ambiguous in unpointed text (see below).
  * Shva: this is the only rule with real judgement in it, and it is documented at `_shva`.

Output is a plain ASCII romanization in the same spirit as CAPHI's urban realization -- what a
learner should say, not a phonemic analysis. Stress is marked with an acute on the vowel only
when it is NOT final, because Hebrew is final-stressed by default (milra) and marking the
default everywhere would be noise. Penultimate stress (mil'el) is common enough in nouns and in
the past tense that leaving it unmarked would teach the wrong word.

    python3 spike/he/phon.py --selftest
    python3 spike/he/phon.py 'שָׁלוֹם' 'סֵפֶר' 'סַפָּר'
"""
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------------------
# The signs. Hebrew niqqud are combining marks that follow their consonant, except for the
# holam male / shuruk which involve a vav. Order within a cluster is not guaranteed by the
# encoders in the wild, so everything below matches on SET MEMBERSHIP, never on position.
# ---------------------------------------------------------------------------------------
SHEVA      = 'ְ'
HATAF_SEG  = 'ֱ'
HATAF_PAT  = 'ֲ'
HATAF_QAM  = 'ֳ'
HIRIQ      = 'ִ'
TSERE      = 'ֵ'
SEGOL      = 'ֶ'
PATACH     = 'ַ'
QAMATZ     = 'ָ'
HOLAM      = 'ֹ'
HOLAM_HASER= 'ֺ'
QUBUTZ     = 'ֻ'
DAGESH     = 'ּ'          # dagesh AND mappiq AND shuruk-dot: same codepoint
METEG      = 'ֽ'
RAFE       = 'ֿ'
SHIN_DOT   = 'ׁ'
SIN_DOT    = 'ׂ'
QAMATZ_QAT = 'ׇ'          # explicit qamatz qatan, rare but unambiguous when present

NIQQUD = set('ְֱֲֳִֵֶַָֹֺֻ'
             'ׇּֽֿׁׂ')
# Cantillation (te'amim) -- the Tanakh text is full of them and they are not pronunciation.
CANTILLATION = re.compile('[\u0591-\u05af\u05bd\u05c0\u05c3\u05c6]')   # NOT \u05f3/\u05f4: geresh marks a sound

VOWEL_SIGNS = {HIRIQ: 'i', TSERE: 'e', SEGOL: 'e', PATACH: 'a', QAMATZ: 'a',
               HOLAM: 'o', HOLAM_HASER: 'o', QUBUTZ: 'u', QAMATZ_QAT: 'o',
               HATAF_SEG: 'e', HATAF_PAT: 'a', HATAF_QAM: 'o'}
HATAFS = {HATAF_SEG, HATAF_PAT, HATAF_QAM}

# Final forms fold to their base for lookup; they are not different letters.
FINAL = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ',
         'ף': 'פ', 'ץ': 'צ'}

# The base consonant table. Modern Israeli, with the mergers stated in the docstring.
CONS = {
    'א': '',    # alef   -- silent
    'ב': 'v',   # bet    -- b with dagesh
    'ג': 'g',
    'ד': 'd',
    'ה': 'h',
    'ו': 'v',   # vav    -- also a vowel letter, handled before we get here
    'ז': 'z',
    'ח': 'x',   # het    -- merged with chaf
    'ט': 't',   # tet    -- merged with tav
    'י': 'y',
    'כ': 'x',   # chaf   -- k with dagesh
    'ל': 'l',
    'מ': 'm',
    'נ': 'n',
    'ס': 's',
    'ע': '',    # ayin   -- silent for most speakers
    'פ': 'f',   # fe     -- p with dagesh
    'צ': 'ts',
    'ק': 'k',   # kuf    -- merged with kaf
    'ר': 'r',
    'ש': 'sh',  # shin   -- sin when it carries the sin dot
    'ת': 't',   # tav    -- merged with tet
}
# BeGeD KeFeT: only these three still alternate in modern speech. Gimel, dalet and tav lost
# their spirantized forms; writing "gh"/"dh"/"th" would be teaching Hebrew nobody speaks.
PLOSIVE = {'ב': 'b', 'כ': 'k', 'פ': 'p'}

GUTTURAL = set('אהחער')   # can't take a dagesh; take hatafs
# The subset that actually blocks a consonant cluster in MODERN speech. ר is excluded on
# purpose: see _shva_map.
THROATY = set('אהחע')

# A geresh after these three letters marks a sound Hebrew has no letter for. Loanwords are a
# real part of spoken Israeli -- ג׳וק, צ׳יפס, בז׳... -- so this is not an edge case.
GERESH = '\u05f3'
GERESHED = {'ג': 'j', 'צ': 'ch', 'ז': 'zh', 'ת': 'th', 'ד': 'dh'}
MAQAF = '\u05be'          # the Hebrew hyphen: a word joiner, not a sound


class Seg:
    """One consonant plus whatever vowel material rides on it."""
    __slots__ = ('cons', 'marks', 'vowel', 'sign', 'is_shva', 'dagesh', 'geresh', 'i')

    def __init__(self, cons, i):
        self.cons, self.i = cons, i
        self.marks = set()
        self.vowel = None
        self.sign = None          # the actual niqqud character, kept for qamatz-qatan
        self.is_shva = False
        self.dagesh = False
        self.geresh = False

    def __repr__(self):
        return '<%s%s%s>' % (self.cons, self.vowel or '', ':' if self.is_shva else '')


def strip_cantillation(s):
    return CANTILLATION.sub('', s)


def clusters(word):
    """[(letter, its marks)] -- niqqud belongs to the consonant in front of it."""
    w = strip_cantillation(unicodedata.normalize('NFC', word))
    out = []
    for ch in w:
        if ch in NIQQUD and out:
            out[-1][1] += ch
        elif ch == MAQAF:
            continue
        else:
            out.append([ch, ''])
    return [(c, m) for c, m in out]


def unpoint(word):
    return ''.join(c for c, _ in clusters(word))


# A vowel letter the text writes and the lexicon spells with a sign instead. Left of the arrow:
# what the previous consonant carries. Right: what the vav or yod becomes once it is written.
# HOLAM and QUBUTZ move ONTO the vav -- כֹּל written כול is כּוֹל, and מיֻחד written מיוחד is
# מיוּחד -- because that is where the sign goes once the letter is there. HIRIQ and TSERE stay
# put and the yod is written bare, which is what מִלָּה -> מִילָּה does.
MALE = {'י': {HIRIQ: None, TSERE: None, SEGOL: None},
        'ו': {HOLAM: HOLAM, HOLAM_HASER: HOLAM, QUBUTZ: DAGESH}}


def respell(surface, pointed):
    """The lexicon's niqqud, moved onto the spelling the text actually uses. None if it can't.

    Israelis write ktiv male and the lexicon points ktiv haser -- עדיין against עֲדַיִן, קייב
    against קִיֶב -- so the pointed form and the written word are different STRINGS for the same
    word, and the reader is shown the vowels of one over the letters of the other. Two things
    go wrong with that. The mild one is cosmetic: the page silently drops the reader's letters.
    The bad one is that a skeleton match ignores every vav and yod, so it also matches words
    that merely look alike once you do -- ביניהם "among them" came back as בְּנֵיהֶם "their
    sons", ווינטר (a surname) as נִטּוּר "monitoring" -- and the page was rewritten into a
    different word with a different meaning.

    Aligning the two answers both. Every letter of `surface` must be either a letter of
    `pointed` or a vowel letter the pointing accounts for at exactly that spot, so an entry that
    cannot spell the written word is rejected instead of displayed. What comes back is the
    surface, letter for letter, wearing the lexicon's vowels: strip the niqqud and you get the
    word that was written, always.
    """
    src, dst, i, j = list(unpoint(surface)), clusters(pointed), 0, 0
    out = []
    while i < len(src) and j < len(dst):
        ch, marks = dst[j]
        if src[i] == ch or FINAL.get(src[i], src[i]) == FINAL.get(ch, ch):
            out.append([src[i], marks])
            i += 1
            j += 1
            continue
        # An extra vav or yod in the text: allowed only where the pointing puts that vowel, or
        # doubling a consonantal one (בְּעָיָתִי written בעייתי), never as a free letter.
        prev = out[-1] if out else None
        rule = MALE.get(src[i], {})
        sign = next((k for k in rule if k in (prev[1] if prev else '')), None)
        if sign is not None:
            moved = rule[sign]
            if moved:                                  # holam and qubutz belong on the vav
                prev[1] = prev[1].replace(sign, '')
            out.append([src[i], moved or ''])
            i += 1
            continue
        if prev and prev[0] == src[i] and src[i] in MALE:   # יי / וו for one consonantal letter
            out.append([src[i], ''])
            i += 1
            continue
        return None
    if i != len(src) or j != len(dst):
        return None                                    # the lexicon spells it fuller, or longer
    got = ''.join(c + m for c, m in out)
    assert unpoint(got) == ''.join(src), (surface, pointed, got)
    return got


def haser(tok, pointed):
    """Is `pointed` (ktiv male, from the lexicon) the same word as `tok` (pointed, defective)?

    respell() reads the variation one way only: the TEXT may carry a vowel letter the entry
    does without, because that is what modern unpointed writing does. Ben-Yehuda runs the other
    way. Its texts are pointed, and pointed Hebrew is written ktiv HASER -- the vowel is a sign,
    so the letter that would stand for it is left out. אֶפְרֹחִים against the lexicon's
    אֶפְרוֹחִים, סְעֻדָּה against סְעוּדָה, סִמָּנִים against סִימָנִים: the same word, the same
    pointing, one letter apart, and respell rejected every one of them because the entry spells
    it fuller.

    What makes this safe is that the token is pointed BY THE PUBLISHER. A vav or yod may be
    missing from the text only where the text's own niqqud carries the vowel that letter would
    have stood for -- holam for the vav, hiriq or tsere for the yod -- so the evidence for the
    match is the text's, not ours. That is what keeps it from doing what the bare skeleton does:
    נִרְגָּז does not become נַרְגִּיז, because the text points that letter with a qamatz and the
    entry's yod stands for a hiriq.
    """
    t, f = clusters(tok), clusters(pointed)
    i = j = dropped = 0
    while i < len(t) and j < len(f):
        if t[i][0] == f[j][0] or FINAL.get(t[i][0], t[i][0]) == FINAL.get(f[j][0], f[j][0]):
            i += 1
            j += 1
            continue
        ch, marks = f[j]
        prev = t[i - 1][1] if i else ''
        # a vav standing for a holam or a shuruq the text writes as a bare sign
        if ch == 'ו' and ((HOLAM in marks or HOLAM_HASER in marks)
                          and (HOLAM in prev or HOLAM_HASER in prev)
                          or DAGESH in marks and QUBUTZ in prev):
            j += 1
            dropped += 1
            continue
        # a silent yod after the hiriq or tsere the text writes without it
        if ch == 'י' and not marks and any(
                v in (f[j - 1][1] if j else '') and v in prev for v in (HIRIQ, TSERE, SEGOL)):
            j += 1
            dropped += 1
            continue
        return False
    # `dropped`: an alignment that took nothing out is respell()'s job, not this one.
    return i == len(t) and j == len(f) and dropped > 0


def _segment(word):
    """Split into consonant-anchored segments, resolving the vowel letters as we go.

    Vav and yod are the awkward part of Hebrew orthography: each is sometimes a consonant and
    sometimes half of a vowel, and which one it is depends on the pointing around it rather
    than on the letter. Resolving that here keeps every rule downstream working on segments
    that already know what they are.
    """
    w = strip_cantillation(unicodedata.normalize('NFC', word))
    segs, i, n = [], 0, len(w)
    while i < n:
        ch = w[i]
        if ch in NIQQUD:                      # stray mark with no consonant -- ignore
            i += 1
            continue
        if ch not in CONS and ch not in FINAL:
            if ch == MAQAF:
                segs.append(Seg('-', i))
            elif ch.strip() and ch != GERESH:
                segs.append(Seg(ch, i))       # punctuation/latin passes through
            i += 1
            continue
        base = FINAL.get(ch, ch)
        marks = set()
        j = i + 1
        while j < n and w[j] in NIQQUD:
            marks.add(w[j])
            j += 1

        # --- vav: shuruk, holam male, or a real consonant ---------------------------------
        if base == 'ו' and segs:
            prev = segs[-1]
            if DAGESH in marks and not (marks & set(VOWEL_SIGNS)):
                # וּ after a bare consonant is shuruk -- the vowel of the PREVIOUS consonant.
                if prev.vowel is None and not prev.is_shva:
                    prev.vowel = 'u'
                    i = j
                    continue
            if HOLAM in marks and not (marks - {HOLAM}):
                if prev.vowel is None and not prev.is_shva:
                    prev.vowel = 'o'          # holam male
                    i = j
                    continue

        s = Seg(base, i)
        s.marks = marks
        s.geresh = (j < n and w[j] == GERESH) or (i + 1 < n and w[i + 1] == GERESH)
        if j < n and w[j] == GERESH:
            j += 1
        s.dagesh = DAGESH in marks
        if marks & HATAFS:
            s.sign = next(iter(marks & HATAFS))
            s.vowel = VOWEL_SIGNS[s.sign]
            s.is_shva = True                  # a hataf is a coloured shva: never a full vowel
        else:
            v = [m for m in marks if m in VOWEL_SIGNS]
            if v:
                s.sign = v[0]
                s.vowel = VOWEL_SIGNS[s.sign]
            elif SHEVA in marks:
                s.is_shva = True
        segs.append(s)
        i = j

    # --- yod as the mater for hiriq male: כִּי is "ki", not "kiy" --------------------------
    out = []
    for k, s in enumerate(segs):
        if (s.cons == 'י' and not s.marks and out
                and out[-1].vowel == 'i' and not out[-1].is_shva):
            continue                          # silent mater
        # --- וו and יי for ONE consonant: unpointed Hebrew doubles a consonantal vav or yod
        # inside a word (צוות, בעייתי, עדיין) and pointed Hebrew does not. respell() keeps the
        # letters the text actually wrote, so the pointing it hands back carries the double --
        # and this transducer was then reading it twice. צֶוֶות came out "tsevevt" where the
        # voice says tsevet, which is the display contradicting the audio on the same word.
        # The second one carries no niqqud of its own; that is what makes it orthography.
        # ...but only where the doubling really is orthographic. When the letter BEFORE it
        # carries a vowel this letter is the mater for -- tsere before a yod, holam before a
        # vav -- the second one is doing a job, and MALE below reads it. יֵינוֹת stays "yeynot",
        # the same way בֵּיצָה is "beytsa"; it is צֶוֶות (segol before the vav) and בְּעָיָיתִי
        # (qamatz before the yod) that are spelling one consonant with two letters.
        # `out[-1].marks` is the third guard and it is not decoration: a segment whose vowel was
        # absorbed from a FOLLOWING vav or yod carries no niqqud of its own, and in נְיוּ יוֹרְק
        # that made the yod of "yu" and the yod of "york" look like a doubled pair across the
        # space between the two words. It ate one and said "nyurk".
        if (s.cons in ('ו', 'י') and not s.marks and out and out[-1].cons == s.cons
                and out[-1].marks and out[-1].sign not in MALE[s.cons]):
            continue
        out.append(s)
    return out


def _shva_map(segs, verb=False):
    """Which shvas are pronounced (-> "e") and which are silent?

    In Modern Israeli Hebrew: a plain shva is SILENT, everywhere. A hataf is a coloured shva
    and is always pronounced. That is the whole rule.

    This is not what the grammars say, and it is not what I wrote first. The classical account
    has shva na word-initially, after a long stressed vowel, in the second of two adjacent
    shvas, and under a dagesh hazaq. I implemented three of those and then measured all eight
    combinations against 14,710 Wiktionary romanizations (spike/he/verify_phon.py). Every extra
    rule made agreement WORSE:

        initial pronounced ................ 81.8%      initial silent ......... 93.0%
        + "second of two adjacent" ........ -1.1pp     + "under dagesh" ....... -1.5pp

    Israelis say braxa, ktiva, smixa, anglit, shilma -- not beraxa, ketiva, semixa, angelit,
    shilema. Teaching the classical rule would be teaching a register nobody speaks.

    I also tried "pronounced next to a throat consonant" (רְחוֹב = rexov, מַעְגָּל = ma'agal),
    which is what the 175 remaining `dropped e` mismatches look like they are asking for. It
    is a trap in the other direction: under a guttural it costs 1.5pp, before one it costs
    5.2pp. It fixes 175 words and breaks 968.

    The residue is real but small, and it lands almost entirely on verb forms (יִכְתְּבוּ is
    yixtevu, not "yixtvu"). Those do not come through here: a verb's pronunciation comes from
    the conjugation engine, which knows the paradigm and can place the vowel correctly.
    """
    out = []
    for k, s in enumerate(segs):
        if not s.is_shva:
            out.append(False)
        elif s.marks & HATAFS:
            out.append(True)
        elif verb and k > 0 and segs[k - 1].is_shva and not out[k - 1]:
            # VERB PARADIGMS ONLY. Inside a conjugated form, a shva following a silent one is
            # pronounced -- יִכְתְּבוּ is yixtevu, תִּכְתְּבִי is tixtevi. The prefix has already
            # closed a syllable, so leaving both silent would ask for a three-obstruent onset
            # that Hebrew does not have.
            #
            # It is deliberately NOT the general rule: measured over 14,710 Wiktionary
            # romanizations it costs 1.1pp, because in nouns the same shape resolves the other
            # way (אַנְגְּלִית is anglit, not "angelit" -- the cluster ends in a sonorant, which
            # Hebrew is happy to say). Rather than guess a phonotactic rule that would have to
            # be right about every cluster, this is switched on only where the caller knows it
            # is looking at a verb form -- which is exactly where verbs_he.py calls it.
            out.append(True)
        else:
            out.append(False)
    return out


def _qamatz_qatan(segs, k):
    """Is the qamatz on segment k actually a qamatz QATAN, pronounced "o"?

    Only one case is claimed by rule: a qamatz immediately before a hataf qamatz, which is
    reliable -- צָהֳרַיִם = tsohorayim.

    I also tried the textbook rule, "qamatz in a closed unstressed syllable", and it is a trap.
    It gets חָכְמָה = xoxma and אָזְנַיִם = oznayim right, and then gets צָרְפַת, סָבְתָא and
    יָלְדָה wrong -- 60 false positives against the oracle, and a net LOSS of 0.3pp. The
    spelling genuinely does not determine the sound here.

    So the rest is a table, not a rule (QATAN below), built from the words where the oracle
    says "o" and the rule says "a". Same posture as pipeline/curated.py on the Arabic side: a
    rule that guesses is worse than a table that knows.
    """
    if segs[k].sign != QAMATZ:
        return False
    return k + 1 < len(segs) and segs[k + 1].sign == HATAF_QAM


# Words whose qamatz is qatan with no derivable reason. Harvested from the oracle (the words
# where Wiktionary says "o" and the rule says "a"), then kept by hand. Keyed on the pointed
# spelling; a lexicon entry may always override with an explicit pronunciation.
QATAN = {
    'כָּל': 'kol', 'כָּל־': 'kol', 'חָכְמָה': 'xoxma', 'אָזְנַיִם': 'oznayim',
    'תָּכְנִית': 'toxnit', 'חָדְשׁוֹ': 'xodsho', 'עָנְיוֹ': 'onyo', 'קָדְשׁוֹ': 'kodsho',
    'צָהֳרַיִם': 'tsohorayim', 'אָנִיָּה': 'oniya', 'חָפְשִׁי': 'xofshi',
}


def _cons_sound(s):
    c = s.cons
    if s.geresh and c in GERESHED:
        return GERESHED[c]
    if c == 'ש':                                   # shin vs sin
        return 's' if SIN_DOT in s.marks else 'sh'
    if c in PLOSIVE and s.dagesh:
        return PLOSIVE[c]
    if c == 'ה' and s.dagesh:
        return 'h'                                      # mappiq: pronounced h word-finally
    return CONS.get(c, c)


def _genuva(segs, k):
    """Is the patach on segment k a patach GENUVA -- said BEFORE its letter, not after?

    A word-final ח, ע or הּ carrying a patach, with a real vowel before it, takes the "stolen
    patach": מָשִׁיחַ is mashiakh, not "mashixa"; שָׁבוּעַ is shavua, not "shavua'" with the
    vowel after the ayin. It is the single biggest rule I had missing -- 205 words in the
    oracle -- and it is completely regular, which is why it is worth a rule rather than a table.
    """
    s = segs[k]
    if k != len(segs) - 1 or s.sign != PATACH or s.cons not in ('ח', 'ע', 'ה'):
        return False
    if s.cons == 'ה' and not s.dagesh:          # plain final he is a mater, not a consonant
        return False
    return any(p.vowel and not p.is_shva for p in segs[:k])


def _realize(word, verb=False):
    """-> (pieces, nuclei). One pass, shared by every public entry point."""
    segs = _segment(word)
    shvas = _shva_map(segs, verb)
    out, nuclei = [], []          # nuclei: index into `out` of each syllable's vowel
    for k, s in enumerate(segs):
        if s.cons not in CONS:                          # passthrough
            out.append(s.cons)
            continue
        # A final he with no mark is a mater, not an /h/: תּוֹרָה = tora, not "torah".
        # Unless it CARRIES a vowel it took from a following vav -- כָּמוֹהוּ, תָּמְהוּ,
        # זְכַרְיָהוּ. The vav is absorbed into the segment before it, which makes the he the last
        # one and left it looking bare, so the rule fired and dropped the /h/ AND the /u/ with
        # it: kamohu was read "kamo" and tamhu "tam", in 122 lexicon rows as well as here.
        if s.cons == 'ה' and k == len(segs) - 1 and not s.marks and not s.vowel:
            continue
        c = _cons_sound(s)
        if _genuva(segs, k):
            nuclei.append(len(out))
            out.append('a')                     # the vowel jumps in front of the letter
            if c:
                out.append(c)
            continue
        # Alef/ayin are silent, but a silent letter still can't swallow its vowel.
        if c:
            out.append(c)
        if s.vowel and not s.is_shva:
            nuclei.append(len(out))
            out.append('o' if _qamatz_qatan(segs, k) else s.vowel)
        elif s.is_shva and shvas[k]:
            nuclei.append(len(out))
            out.append(s.vowel or 'e')
    return out, nuclei


def phon(word, verb=False):
    """Vocalized Hebrew -> romanized Modern Israeli pronunciation.

    Pass verb=True for a cell of a conjugation table; see _shva_map for why that differs.
    """
    hit = QATAN.get(unicodedata.normalize('NFC', word).strip())
    return hit if hit else ''.join(_realize(word, verb)[0])


# Stress is a separate entry point rather than baked in, because the pipeline wants both: the
# plain romanization for display, and a stress-marked one for the audio check.
ACUTE = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú'}


VOWEL = re.compile(r'[aeiou]')


def beat(romanization):
    """Which syllable from the end carries the stress, per an acute in `romanization`.

    Stress is the one thing about a Hebrew word's sound that its POINTING does not determine --
    בֶּרֶךְ and בֵּרֵךְ are both berex until you know where the beat falls -- so it is the one
    thing that has to be looked up rather than computed. 1 (milra, final) is the default, and
    also what a romanization with no accent gets: it is the language's own default, not a guess
    dressed up as one.
    """
    n = unicodedata.normalize('NFD', romanization or '')
    after, seen = 0, False
    for ch in n:
        if unicodedata.combining(ch):
            seen, after = True, 0
        elif seen and VOWEL.match(ch):
            after += 1
    return after + 1 if seen else 1


def phon_stressed(word, syllable_from_end=1, mark_final=False):
    """Romanization with non-final stress marked. syllable_from_end=1 means milra (default).

    `mark_final` marks it even when it IS final, which is normally left unmarked because final
    is the default and marking the default everywhere would be noise. The exception is a lesson
    ABOUT stress, where the pair only teaches anything if both members show where the beat is.
    """
    out, nuclei = _realize(word)
    if (syllable_from_end > 1 or mark_final) and len(nuclei) >= syllable_from_end:
        at = nuclei[-syllable_from_end]
        out[at] = ACUTE.get(out[at], out[at])
    return ''.join(out)


# ---------------------------------------------------------------------------------------
# Self-test. Every case is a real word chosen to exercise exactly one rule, so a failure
# names the rule that broke. Expected values are Modern Israeli, as an Israeli says them.
# ---------------------------------------------------------------------------------------
CASES = [
    # plain vowels
    ('שָׁלוֹם', 'shalom', 'qamatz + holam male'),
    ('סֵפֶר', 'sefer', 'tsere + segol -> both e'),
    ('בַּיִת', 'bayit', 'dagesh in bet; yod as consonant'),
    ('שֻׁלְחָן', 'shulxan', 'qubutz; silent shva; het=x'),
    ('אִמָּא', 'ima', 'initial alef silent; final alef silent'),
    # begedkefet
    ('כֶּלֶב', 'kelev', 'kaf w/ dagesh = k; final vet = v'),
    ('פָּרָה', 'para', 'pe w/ dagesh = p; final he mater'),
    ('תּוֹרָה', 'tora', 'tav = t; holam male; he mater'),
    # mergers
    ('חָלָב', 'xalav', 'het = x'),
    ('עֶרֶב', 'erev', 'ayin silent'),
    ('קָשֶׁה', 'kashe', 'kuf = k; final he mater'),
    ('צָהֳרַיִם', 'tsohorayim', 'tsadi = ts; hataf qamatz'),
    # shin / sin
    ('שָׂמַח', 'samax', 'sin dot -> s'),
    # shuruk
    ('שׁוּלחָן', 'shulxan', 'shuruk written with vav'),
    ('הוּא', 'hu', 'shuruk + silent alef'),
    # shva
    ('בְּרָכָה', 'braxa', 'initial shva dropped in modern speech'),
    ('כְּתִיבָה', 'ktiva', 'initial shva dropped; hiriq male'),
    # patach genuva -- the vowel jumps in front of a final throat consonant
    ('מָשִׁיחַ', 'mashiax', 'patach genuva after a long vowel'),
    ('שָׁבוּעַ', 'shavua', 'patach genuva on final ayin'),
    # geresh: the borrowed sounds of spoken Israeli
    ('גֶ׳ל', 'jel', 'gimel + geresh = j'),
    ('נִינְגָ׳ה', 'ninja', 'geresh mid-word'),
    # qamatz qatan, from the table rather than a rule
    ('כָּל', 'kol', 'qamatz qatan: lexical, not derivable'),
    # hiriq male
    ('שִׁיר', 'shir', 'yod as mater after hiriq'),
    # וו / יי for one consonant, and the three words apart that decide it
    ('צֶוֶות', 'tsevet', 'doubled vav for one consonant: segol before it, so orthographic'),
    ('בֵּיצָה', 'beytsa', 'tsere + yod is a mater, not a doubling'),
    ('יֵינוֹת', 'yeynot', 'consonantal yod, then its tsere mater — both kept'),
    ('נְיוּ יוֹרְק', 'nyuyork', 'two words: the yods are not a pair across the space'),
    # the homographs that make niqqud matter
    ('סֵפֶר', 'sefer', 'homograph: book'),
    ('סַפָּר', 'sapar', 'homograph: barber'),
    ('סִפֵּר', 'siper', 'homograph: he told'),
    ('סָפַר', 'safar', 'homograph: he counted'),
]


# Words the rules get wrong, kept visible rather than quietly dropped from CASES. Each one
# is a real limitation with a known cause; a regression here is a different thing from a bug.
KNOWN_GAPS = [
    ('יִכְתְּבוּ', 'yixtevu', 'yixtvu',
     'a shva between two consonants of a VERB is pronounced. Not derivable from the spelling '
     'alone -- it needs the paradigm, so the conjugation engine supplies verb pronunciations '
     'and this transducer never sees them.'),
]


def selftest():
    bad = 0
    for word, want, why in CASES:
        got = phon(word)
        ok = got == want
        if not ok:
            bad += 1
        print('%s %-12s want %-12s got %-12s  %s'
              % ('ok ' if ok else 'FAIL', word, want, got, why))
    print('\n%d/%d' % (len(CASES) - bad, len(CASES)))
    print('\nknown gaps (not failures):')
    for word, real, ours, why in KNOWN_GAPS:
        print('  %-12s says %-10s we say %-10s' % (word, real, ours))
        print('      %s' % why)
    return 1 if bad else 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    for w in sys.argv[1:]:
        print('%s\t%s' % (w, phon(w)))
