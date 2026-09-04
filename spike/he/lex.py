#!/usr/bin/env python3
"""Lookup over hebrew_lex.parquet. The Hebrew counterpart of pipeline/maknuune.py.

Same contract, same discipline: retrieve real candidates, report how confident the match is,
and never invent an entry. The differences from the Arabic side are all Hebrew's:

  * PROCLITICS ARE A SLOT SYSTEM, NOT A LIST. Hebrew stacks its one-letter particles in a fixed
    order -- ו, then ש or כש, then one of ב/כ/ל/מ, then ה -- so ומהבית and וכשהילד are both
    ordinary words. Enumerating the ~90 attested combinations by hand would be error-prone and
    would miss the rare ones; generating them from the slot model is both shorter and complete.

  * KTIV MALE IS THE REAL PROBLEM. Unpointed Hebrew adds vowel letters that pointed Hebrew
    leaves out -- יכתוב for יִכְתֹּב, תוכנית for תָּכְנִית. Running text is written one way and
    the lexicon's pointed forms the other, so a plain string match misses. This is handled as a
    LAST resort with an explicit `ktiv` provenance, never folded into the key: collapsing every
    optional yod and vav would merge genuinely different words.

Provenance strings match the Arabic pipeline's vocabulary so ingest.py can treat them alike:
`wiktionary:exact`, `wiktionary:clitic`, `wiktionary:ktiv`, `AMBIGUOUS-needs-resolution`,
`unresolved`.
"""
import itertools
import os
import re

try:
    import pandas as pd
except ModuleNotFoundError:                       # the python3 first on PATH is not the one
    raise SystemExit(                             # that can run this pipeline. Say so, once.
        "\n!! This needs pandas, and the python3 at the front of your PATH does not have it.\n"
        "   Re-run the same command with the interpreter that does:\n"
        "       /usr/local/bin/python3 <the rest of your command>\n"
        "   (Homebrew's python3 is first on PATH here and carries no pandas; the framework\n"
        "    build at /usr/local/bin/python3 is the one the pipeline has always used.)\n")

from phon import DAGESH, MAQAF, NIQQUD, clusters, haser, respell, unpoint

HERE = os.path.dirname(os.path.abspath(__file__))
PARQUET = os.path.join(HERE, 'hebrew_lex.parquet')

# The proclitic slots, in the order Hebrew stacks them. A word may take one from each, so the
# attested set is the product -- ו + כש + ל + ה is a real (if rare) prefix.
SLOTS = [['', 'ו'], ['', 'ש', 'כש'], ['', 'ב', 'כ', 'ל', 'מ'], ['', 'ה']]
PREFIXES = sorted({''.join(p) for p in itertools.product(*SLOTS)} - {''},
                  key=len, reverse=True)

# Possessive and object suffixes. Longest first so ־יהם is tried before ־ם.
SUFFIXES = ['ותיהם', 'ותיהן', 'ותיכם', 'ותיכן', 'יהם', 'יהן', 'יכם', 'יכן', 'ינו', 'ותי',
            'תיו', 'תיה', 'נו', 'כם', 'כן', 'הם', 'הן', 'יו', 'יה', 'יך', 'יי', 'ני',
            'ם', 'ן', 'י', 'ך', 'ו', 'ה']
MIN_STEM = 2

MATRES = re.compile('[וי]')

# A proclitic from these slots attaches to a NOUN or an adjective, never to a tensed verb:
# מ + "he judged" is not Hebrew, so משפט is מִשְׁפָּט and nothing else. ו/ש/כש take a clause and
# are exempt.
NOMINAL_SLOT = set('בכלמה')
TENSED = {'past', 'future', 'imperative'}

# Where the prefix is the ENTRY'S OWN and the alternative is therefore a coincidence of
# spelling: the ה of a definite noun, the מ of a present participle. Each of these entries
# already spells the whole surface and points every letter of it, so a clitic re-reading can
# only take pointing away -- מְחַפֵּשׂ "searching" against מ- + חֳפָשִׁים.
#
# The ל of an infinitive WAS on this list and had to come off. It is not the same case: ה- and
# מ- attach to a shape that is otherwise not a word, but ל- + a noun is the ordinary dative and
# collides with the infinitive of every piel verb built on that noun's root. It cost six texts
# their reading of לבית, which is "to the house" everywhere in this app and was taken as
# לְבַיֵּת "to domesticate"; and three more לשוק, "to the market", taken as לְשַׁוֵּק "to
# market". Neither ever reached adjudication, because this list said the ל was accounted for.
OWN_PREFIX = [('ה', 'definite'), ('מ', 'present'), ('מ', 'participle')]


def _same_word(r):
    """What makes two lexicon rows the same word for ktiv_readings. See its docstring."""
    return (MATRES.sub('', unpoint(str(r['LEMMA']))), str(r['POS']), str(r['BINYAN'] or ''))


def _tensed(r):
    a = str(r['ANALYSIS'] or '')
    return a.startswith('VERB') and bool(TENSED & set(a.split(':')[-1].split('.')))


class Lexicon:
    def __init__(self, path=PARQUET):
        df = pd.read_parquet(path)
        self.df = df
        recs = df.to_dict('records')
        self.by_form = {}
        self.by_lemma = {}
        # By id, so a decision made once can be applied for good. The resolution trail records
        # the ENTRY that was chosen for a word, and replaying it has to find that entry again --
        # the Arabic lexicon has had this since the beginning and this one did not, so the first
        # Hebrew article that reached adjudication then died trying to use the answer.
        self.by_id = {}
        for r in recs:
            self.by_form.setdefault(r['FORM_SEARCH'], []).append(r)
            self.by_lemma.setdefault(r['LEMMA_SEARCH'], []).append(r)
            self.by_id[str(r['ID'])] = r
        # For ktiv male/haser: index every entry under a skeleton with the vowel letters
        # removed. Lossy on purpose, and only ever consulted after everything else has failed.
        self.by_skeleton = {}
        for k, v in self.by_form.items():
            self.by_skeleton.setdefault(MATRES.sub('', k), []).extend(v)

    # -- the peeler ----------------------------------------------------------------------
    def stems(self, w):
        """Every (stem, what-was-stripped) the clitic slots can produce, longest strip first."""
        out = [(w, '')]
        for p in PREFIXES:
            if w.startswith(p) and len(w) - len(p) >= MIN_STEM:
                out.append((w[len(p):], p + '-'))
        for s in SUFFIXES:
            if w.endswith(s) and len(w) - len(s) >= MIN_STEM:
                out.append((w[:-len(s)], '-' + s))
                for p in PREFIXES:
                    if w.startswith(p) and len(w) - len(p) - len(s) >= MIN_STEM:
                        out.append((w[len(p):-len(s)], p + '-' + s))
        seen, uniq = set(), []
        for st, cut in out:
            if st not in seen:
                seen.add(st)
                uniq.append((st, cut))
        return uniq

    @staticmethod
    def _spellable(word, recs):
        return [r for r in (recs or []) if respell(word, r['FORM'])]

    def _hit(self, key):
        return self.by_form.get(key) or self.by_lemma.get(key)

    def look(self, surface):
        """-> (records, provenance, what_was_cut). records is [] when nothing was found."""
        from build_lex import he_norm
        w = he_norm(surface)
        if not w:
            return [], 'unresolved', ''
        hit = self._hit(w)
        if hit:
            return hit, 'wiktionary:exact', ''
        for stem, cut in self.stems(w)[1:]:
            hit = self._hit(stem)
            if hit:
                return hit, 'wiktionary:clitic', cut
        # Last resort: the same word spelled with or without its optional vowel letters. The
        # skeleton ignores every vav and yod, which is what lets it find יכתוב under יִכְתֹּב --
        # and also what let it find ביניהם "among them" under בְּנֵיהֶם "their sons", פוטין
        # under פוֹטוֹן "photon", מיאמי under מָאמִי. So the skeleton PROPOSES and respell()
        # disposes: an entry stays only if its pointing can actually spell the letters that
        # were written. Of 267 ktiv matches in 300 sentences of live news, 178 could not, and
        # every one of those was a different word about to be printed over the reader's.
        skel = MATRES.sub('', w)
        if len(skel) >= MIN_STEM:
            hit = self._spellable(w, self.by_skeleton.get(skel))
            if hit:
                return hit, 'wiktionary:ktiv', ''
            for stem, cut in self.stems(w)[1:]:
                hit = self._spellable(stem, self.by_skeleton.get(MATRES.sub('', stem)))
                if hit:
                    return hit, 'wiktionary:ktiv', cut
        # And the same variation the other way round, which only a POINTED source can answer.
        # The skeleton already proposes the right rows -- אפרחים and אפרוחים reduce to the same
        # letters -- and _spellable threw them away, because respell() only knows how to add a
        # vowel letter the entry does without, never to drop one the text does without. Here the
        # text has vowels of its own, so spells() can be asked directly: it peels the particles
        # and compares the publisher's pointing against the entry's. See phon.haser.
        if any(c in NIQQUD for c in surface):
            for stem, cut in self.stems(w):
                rows = self.by_skeleton.get(MATRES.sub('', stem)) or []
                hit = [r for r in rows if self.spells(surface, r) == cut]
                if hit:
                    return hit, 'wiktionary:haser', cut
        return [], 'unresolved', ''

    @staticmethod
    def readings(recs):
        """One candidate per distinct READING of this surface, richest first.

        Wiktionary lists a word once per inflection row, so ספר comes back as 24 rows -- but
        those are 6 words. Handing the raw rows to an adjudicator gave it סֵפֶר four times and
        never showed it סַפָּר "barber" or סָפַר "he counted" at all: the six slots were spent
        on one lemma. Collapsing first is what makes the choice a real choice.

        But collapsing by LEMMA alone throws away the other half of the ambiguity, because one
        lemma spells one surface more than one way: מצאו is both מָצְאוּ "they found" and
        מִצְאוּ "find!", both of מָצָא, and חסמו, פרצו, חגג, קשה and היה are the same shape. Those
        went out as one candidate -- and the tie-break, fewest feature tags, systematically
        picked the IMPERATIVE, which is close to the rarest thing a news sentence contains. So
        the key is the lemma AND the pointing, and the page stops saying "find!" for "they
        found". Measured on 300 sentences of live news: +2.7 points of adjudication, 51.2% to
        54.0%.

        Two collapses stay, because neither is a choice a reader could see: a construct form
        when the lemma also has a free one (יוֹם / יוֹם־), and an unpointed row when a pointed
        row OF THE SAME LEMMA spells the same letters. That last qualifier was missing, and it
        is not a detail: the collapse ran across lemmas, so צֶוֶת "crew" -- whose Wiktionary row
        is spelled unpointed -- was deleted because צִוּוּת "staffing" happens to unpoint to the
        same letters. The adjudicator was then handed "to staff / staffing / defective spelling
        of ציוות" and picked one of the three, and the day's news said צִוּוּת where the voice
        says tsevet. Same word, two spellings, is what this is for; two words are a choice.
        """
        free = {r['LEMMA'] for r in recs if 'construct' not in str(r['ANALYSIS'] or '')}
        keep = [r for r in recs
                if 'construct' not in str(r['ANALYSIS'] or '') or r['LEMMA'] not in free]
        best = {}
        for r in keep or recs:
            key = (r['LEMMA'], str(r['FORM']).replace(MAQAF, ''))
            score = ((1 if r['GLOSS'] else 0) * 4 + (1 if r['PHON'] else 0) * 2
                     + (1 if str(r['PHON_SRC']).endswith('+stress') else 0)
                     + (1 if unpoint(r['FORM']) != str(r['FORM']) else 0)
                     - str(r['ANALYSIS'] or '').count('.') * 0.1)
            if key not in best or score > best[key][0]:
                best[key] = (score, r)
        out = [r for _, r in sorted(best.values(), key=lambda x: -x[0])]
        pointed = {(r['LEMMA'], unpoint(r['FORM'])) for r in out
                   if unpoint(r['FORM']) != str(r['FORM'])}
        return [r for r in out if unpoint(r['FORM']) != str(r['FORM'])
                or (r['LEMMA'], str(r['FORM'])) not in pointed]

    def spells(self, tok, rec):
        """Can this entry's pointing be the pointing of THIS token? -> the cut, or None.

        For a source that is already pointed -- a Ben-Yehuda text, where the vowels are the
        publisher's -- the pointing on the page is evidence the annotator does not otherwise
        have, and it is the strongest kind: pointing IS the disambiguation. Comparing strings
        does not work, because the token carries its particles (וְהַסְּנֶה) and the candidates are
        stems (סְנֶה), so the particles are peeled first and only the stem is compared. Measured
        on 4,400 tokens of pointed literature, this settles 51% of what would otherwise go to an
        adjudicator: 50% of tokens needing a decision down to 29%.
        """
        from build_lex import he_norm
        f, plain, cl_all = str(rec['FORM']), he_norm(unpoint(tok)), clusters(tok)
        for stem, cut in self.stems(plain):
            pre, _, suf = cut.partition('-')
            cl = cl_all[len(pre):len(cl_all) - len(suf)] if suf else cl_all[len(pre):]
            if not cl:
                continue
            mine = ''.join(c + m for c, m in cl)
            if he_norm(unpoint(mine)) != stem:
                continue
            if f == mine or respell(unpoint(mine), f) == mine or haser(mine, f):
                return cut
            # A proclitic geminates the first consonant of what follows -- הַסְּנֶה, הַמִּצְרִים --
            # and the citation form does not carry that dagesh. Without this the definite
            # article alone defeated the comparison on a quarter of the tokens in a text.
            if pre:
                bare = ''.join(c + (m.replace(DAGESH, '') if i == 0 else m)
                               for i, (c, m) in enumerate(cl))
                if f == bare or respell(unpoint(bare), f) == bare or haser(bare, f):
                    return cut
        return None

    def cut_for(self, key, rec):
        """What had to be stripped from `key` for `rec` to be the reading -- '' if nothing.

        Asked of the record that was CHOSEN, not of the first one the lookup happened to find.
        A word can match exactly and still be resolved to a clitic reading -- that is the whole
        point of alt_readings() below -- and when it is, the pointing has to be refused just as
        it is on any other clitic match. Deriving the cut from the answer rather than from the
        lookup is what makes the two agree.

        None when `rec` explains no part of `key` at all. That is not a shrug: a resolution
        trail names entries by id, ids outlive the text they were chosen for, and an entry that
        cannot be reached from this word by any route is not an answer to it. Saying so lets the
        caller drop it instead of stamping a stranger's pointing onto the page.
        """
        for stem, cut in self.stems(key):          # stems()[0] is the whole word, so exact wins
            if rec['FORM_SEARCH'] == stem or rec['LEMMA_SEARCH'] == stem:
                return cut
        # The ktiv route, and it has to clear the same bar look() sets: a skeleton match ignores
        # every vav and yod, so without respell() a trail line would quietly bring back the
        # match that gate exists to reject.
        skel = MATRES.sub('', str(rec['FORM_SEARCH']))
        for stem, cut in self.stems(key):
            if skel == MATRES.sub('', stem) and respell(stem, rec['FORM']):
                return cut
        # The feminine, and ONLY on this route -- the plural -ות of a -ה noun, and the singular
        # -ית of a -י adjective. Both are regular Hebrew, and
        # Wiktionary lists the plural for some nouns and not others, so a lookup tier built on
        # it would have to guess which -ה noun a given -ות belongs to. Measured over the corpus
        # it reaches 20 tokens and gets four of them wrong -- פרעות "riots" as "pharaohs",
        # מהוגנות "decent" as "garden", and באלות "with clubs" as "goddesses", since אֵלָה sits
        # under the same key as אַלָּה. So it is not a tier. It is a route the trail can name:
        # nothing resolves this way on its own, and an adjudicator that has read the sentence
        # can say which -ה noun it is and have that answer validate. The -ית arm is the same
        # bargain: Wiktionary lists רוּסִית under רוּסִי and lists nothing under פָלַסְטִינִי, so
        # the feminine of "Palestinian" is a form the lexicon knows the word for and not the
        # shape of.
        for end, base in (('ות', 'ה'), ('ית', 'י')):
            if not key.endswith(end):
                continue
            for stem, cut in self.stems(key):
                if stem.endswith(end) and str(rec['LEMMA_SEARCH']) == stem[:-2] + base:
                    return (cut or '-') + end
        return None

    def alt_readings(self, key, exact, strict=True):
        """Prefix readings of an exactly-matched word that mean something ELSE.

        The peeler never ran for these words: an exact match wins in look() before a single
        prefix is tried, so a word that IS a word and is ALSO a particle plus a different word
        was taken silently, with one candidate, and never reached adjudication. It is not a rare
        shape -- Hebrew's proclitics are single letters and its verbs are unpointed skeletons --
        and the readings it loses are the everyday ones: שקרה is ש- + קָרָה "that happened" and
        was shipped as שִׁקְּרָה "she lied"; שהיה is ש- + הָיָה and was שְׁהִיָּה "a stay"; ביום
        is ב- + יוֹם and was בִּיּוּם "staging".

        Nothing here decides anything. It finds the other real entries so that the sentence, in
        front of an adjudicator, can decide -- the same rule the rest of this file follows.

        `strict` is the difference between the two questions this answers. Strict asks IS THIS
        WORTH INTERRUPTING FOR, and applies the two exemptions below; unstrict asks WHAT ELSE
        COULD THIS BE, and is for a word already on its way to adjudication, where another real
        candidate costs a line of prompt and can only help.
        """
        lemmas = {str(r['LEMMA_SEARCH']) for r in exact}
        # 300 sentences of live news, 7,185 tokens: without either exemption this flags 8.2% of
        # them and takes the article's adjudication rate from 50.0% to 58.2%; the headword rule
        # alone leaves 4.2%; both leave 1.3%, for 51.3% overall. The words the two rules drop
        # were, on inspection, ones the exact match already had right.
        #
        # A HEADWORD is taken at its word. If the lexicon lists this exact string as a lemma --
        # היא, למרות, בתוך, מחר, מִשְׁפָּט -- then the word is real as written, and every one of
        # them starts with a letter that is also a particle, so without this the queue fills
        # with the commonest words in the language. What is left is the case that actually goes
        # wrong: an INFLECTED form, which Hebrew generates far more of than it has headwords,
        # colliding with a particle plus a word. שִׁקְּרָה is one of 30-odd forms of שִׁקֵּר;
        # קָרָה, the word that was meant, is the headword.
        if strict and key in lemmas:
            return []
        out = []
        for stem, cut in self.stems(key)[1:]:
            if not cut.endswith('-'):              # a suffix strip is a different question
                continue
            pre = cut[:-1]
            hit = self._hit(stem)
            if not hit or (strict and self._accounts_for(exact, pre)):
                continue
            # A different WORD is the test, not a different row: Wiktionary lists בְּחִירוֹת
            # both as the plural of בְּחִירָה and as its own entry, and "the choices" read two
            # ways is not an ambiguity, it is the same word card either way.
            #
            # The pair is the pointed lemma AND the part of speech, not LEMMA_SEARCH. The
            # skeleton was too coarse by exactly the amount that matters here: the piel שִׁוֵּק
            # "to market" and the noun שׁוּק "market" share the skeleton שוק, so לשוק compared
            # its own lemma against itself and came back unambiguous. Same for בִּיֵּת and
            # בַּיִת under בית. Both still dedup under the pair when they are genuinely one
            # word, which is what the בְּחִירוֹת case needs.
            ident = {(r['LEMMA'], str(r['POS'])) for r in exact}
            alt = [r for r in hit if (r['LEMMA'], str(r['POS'])) not in ident]
            if pre[-1] in NOMINAL_SLOT:
                alt = [r for r in alt if not _tensed(r)]
            if alt:
                out.append((pre, stem, alt))
        return out

    def ktiv_readings(self, key, exact):
        """Entries the SKELETON can reach that the exact match hid.

        alt_readings asks what a word could be if a letter at the front is a particle. This asks
        the other question Hebrew makes possible: what it could be if the optional vowel letters
        were left out. An entry whose headword is spelled DEFECTIVELY is filed under the
        defective key, so the ktiv-male surface never reaches it -- look() returns on the exact
        tier and the skeleton tier, which exists for exactly this, never runs.

        That cost two words their meaning everywhere this app says them. גינה matched the verb
        גִּנָּה "to denounce", which lists its full spelling, while the noun גִּנָּה "a garden"
        lists only גנה. אישר matched the pual אֻשַּׁר "to be authorized" -- whose own gloss reads
        "passive of אישר" -- while the piel אִשֵּׁר "to approve" sits under אשר. Both are in the
        lexicon. Neither was reachable.

        Two rules keep it from drowning the queue, and the second is the interesting one:

        The alternative has to be a different WORD, and the identity is three things. The
        lemma's SKELETON, not its pointing, because אֹתוֹ and אוֹתוֹ are one word spelled two
        ways and were the single biggest source of noise -- 55 occurrences of אותו alone, plus
        every מאוד and every גדול. The PART OF SPEECH, because גִּנָּה the noun and גִּנָּה the
        verb are two words that share everything else. And the BINYAN, because the piel אִשֵּׁר
        "to approve" and the pual אֻשַּׁר "to be approved" are two verbs of one root, identical
        under the first two tests, and the whole reason אישר is here.

        And a "defective spelling of X" gloss is dropped outright: that entry IS the exact
        match, written the other way. Deliberately not "form of", which is how Wiktionary
        glosses a real inflection -- אִתָּנוּ "form of אֶת including us" is the correct reading
        of איתנו, which had been matching אִיתֵּן "to spell".

        Measured on 12,658 tokens of the app's Hebrew: 423 flagged, 167 of them distinct, and
        the resolution trail answers each distinct word once. Among them שישי, read as the
        imperative "rejoice!" rather than "sixth"; איתנו and איתה as "to spell"; בעיר as
        "flammable" rather than ב- + עיר.
        """
        skel = MATRES.sub('', key)
        if len(skel) < MIN_STEM:
            return []
        hit = self._spellable(key, self.by_skeleton.get(skel)) or []
        ident = {_same_word(r) for r in exact}
        alt = [r for r in hit if _same_word(r) not in ident]
        return [r for r in alt if 'spelling of' not in str(r['GLOSS'])[:34]]

    @staticmethod
    def _accounts_for(exact, pre):
        """The exact entry already spells this prefix, so the alternative is a coincidence.

        Deliberately NOT tested by decomposing the exact entry's own lemma: `lemma == pre +
        stem` is true of every citation form that happens to start with a particle letter, so
        it silently exempted מְכָל, מִשְׁפָּט and every other word this is meant to catch.
        """
        for r in exact:
            a = str(r['ANALYSIS'] or '')
            if any(p in pre and f in a for p, f in OWN_PREFIX):
                return True
        return False

    def resolve(self, surface):
        """look(), then decide whether the answer is unique enough to use unattended."""
        from build_lex import he_norm
        recs, prov, cut = self.look(surface)
        if not recs:
            return None, 'unresolved', []
        cands = self.readings(recs)
        # An exact match is not the same as an unambiguous one. Two ways it can hide a real
        # second reading, and both are asked: the word may be a particle plus a different word,
        # and it may be the full spelling of an entry that only lists the defective one.
        alts = ktiv = []
        if prov == 'wiktionary:exact':
            alts = self.alt_readings(he_norm(surface), recs)
            ktiv = self.ktiv_readings(he_norm(surface), recs)
        if len(cands) == 1 and not alts and not ktiv:
            return cands[0], prov, cands
        # Several distinct lemmas share this spelling. Same rule as the Arabic side: do not
        # pick for the learner, hand the candidates on for adjudication.
        return cands[0], 'AMBIGUOUS-needs-resolution', cands[:6]
