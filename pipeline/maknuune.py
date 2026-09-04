"""Maknuune lookup — the metadata authority.

SPEC 7.4.2: retrieve real candidates, never generate. Morphology narrows by POS,
because the clitic tells you the part of speech before you look at anything else.
"""
try:
    import pandas as pd
except ModuleNotFoundError:                       # the python3 first on PATH is not the one
    raise SystemExit(                             # that can run this pipeline. Say so, once.
        "\n!! This needs pandas, and the python3 at the front of your PATH does not have it.\n"
        "   Re-run the same command with the interpreter that does:\n"
        "       /usr/local/bin/python3 <the rest of your command>\n"
        "   (Homebrew's python3 is first on PATH here and carries no pandas; the framework\n"
        "    build at /usr/local/bin/python3 is the one the pipeline has always used.)\n")
import re, os

DIAC = re.compile(r'[ً-ْٰـ]')
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARQUET = os.path.join(_HERE, '..', 'data', 'maknuune.parquet')

def norm(s):
    s = DIAC.sub('', str(s))
    for a, b in [('أ','ا'),('إ','ا'),('آ','ا'),('ى','ي'),('ة','ه'),('ؤ','ء'),('ئ','ء')]:
        s = s.replace(a, b)
    return s.strip()

class Lexicon:
    def __init__(self, path=_PARQUET):
        df = pd.read_parquet(path)
        df['_F'] = df['FORM'].map(norm)
        df['_L'] = df['LEMMA'].map(norm)
        self.df = df
        self.by_form, self.by_lemma, self.by_id = {}, {}, {}
        for rec in df.to_dict('records'):
            self.by_form.setdefault(rec['_F'], []).append(rec)
            self.by_lemma.setdefault(rec['_L'], []).append(rec)
            self.by_id[str(rec['ID'])] = rec

    @staticmethod
    def spellings(w):
        """The word as the LEXICON might file it — dialect letters mapped back, nothing stripped.

        Split out of morph()'s coda() so candidates() can ask which stems are still the word
        itself rather than a fragment of it. That distinction is what stops the b- heuristic
        from throwing the answer away: see the pos filter there.
        """
        out = []
        for a_, b_ in (('ت', 'ث'), ('د', 'ذ'), ('ض', 'ظ')):
            if a_ in w:
                out.append(w.replace(a_, b_))
        # ص -> ز only at the FRONT. A ص before a voiced consonant is said, and so written, ز:
        # زغير for صغير "small", the commonest untappable word in the books at 106 tokens.
        # Anywhere else in the word it is a different letter doing its own job, and swapping
        # every ز turned وزيت "and oil" into "make an order" and المزيفة "forged" into
        # "spending the summer". Initial only.
        if w.startswith('ز') and len(w) > 2:
            out.append('ص' + w[1:])
        # NOT a final-hamza rule. ضوء -> ضو "light" is right and it is not worth what it costs:
        # بهدوء "calmly" loses its hamza, then its بـ, and lands on "demolish" — 15 tokens for
        # 4. ضوء is curated by name instead.
        # NOT a final ا -> ة rule. It looks like the same phenomenon -- the lexicon files مرة
        # and the dialect writes مرا -- and measured over the corpus it is a net loss: Arabic
        # is full of words that legitimately end in alif, and mapping them all wrecked more
        # than it fixed. وأنا "I" (165 tokens) became an interjection, كلها "all of it" became
        # "to him", بالمسا "in the evening" became "frighten", لنا "to us" became "will not".
        # The handful of real cases -- بكرا, مرا -- are curated by name in curated.py instead.
        return out

    def morph(self, w):
        """Peel Palestinian clitics. Returns (ordered stems, ANALYSIS constraint or None).

        ORDER IS LOAD-BEARING. Candidates are tried in sequence, so a real word must
        always outrank a fragment: كتير -> كثير (a word) must beat كتير -> تير (what's
        left after stripping a ك that was never a clitic). Tiers below run in priority
        order and the dedupe keeps first occurrence.

        COMPOSITIONAL within each tier: وسجّلوا needs w- AND -uu removed; التانية needs
        al- removed AND ت->ث AND the feminine ending. Rules applied only to the original
        word miss every combination.
        """
        w = norm(w); pos = None

        def coda(x):
            """Dialect spelling -> the letters the lexicon files the word under.

            Each pair is the same phenomenon: the writer spelled what Palestinian SAYS and
            Maknuune files what the word IS. ث/ذ/ظ merge into ت/د/ض in this dialect, and a ص
            before a voiced consonant is said, and written, ز -- زغير for صغير "small", which
            was the single commonest untappable word in the books at 106 tokens.

            Safe by construction: candidates() returns an exact match without ever calling
            morph(), so a variant can only be reached by a word that has already missed. زيت
            "oil" is in the lexicon as itself and never gets here.
            """
            return Lexicon.spellings(x)

        def desuffix(x):
            """Every suffix-stripped form of x, cheapest first."""
            out = []
            # A feminine noun's ة becomes ت the moment anything is glued to it: قهوة -> قهوته,
            # طنجرة -> طنجرتك, ساعة -> ساعتين. norm() has already folded ة to ه, so stripping
            # the suffix leaves ...ت where the lexicon has ...ه and the word misses by one
            # letter. Offering the ه form is what lets an ordinary possessed noun resolve.
            def fem(b):
                out = [b[:-1] + 'ه'] if b.endswith('ت') and len(b) > 2 else []
                # A final-weak verb keeps its ي in the lexicon and shows ا once something is
                # glued on: أعطى -> أعطاه, so stripping the ه leaves اعطا where اعطي is filed.
                # Applied to the STRIPPED STEM only, never to the whole word — the wider version
                # of this rule was measured and thrown away (see spellings()).
                if b.endswith('ا') and len(b) > 2:
                    out.append(b[:-1] + 'ي')
                return out

            # 'ني' is the object "me" and it was missing: شافني "he saw me", بتوجعني "it hurts
            # me", بتساعدني "will you help me". Stripping the 'ي' of the possessive instead left
            # شافن, which is not a word, so eight everyday verbs in one book had no card. Listed
            # before 'نا' and 'ي' because the loop takes every match and the longest is the one
            # that leaves a real stem.
            for suf in ['ني','ها','هم','هن','نا','كم','ي','ك','ه']:  # object / possessive
                # 'ني' needs THREE letters behind it, not two. An Arabic verb stem is at least
                # three, and the looser guard let لأني "because" become لأ "No!" (26 tokens) and
                # عيني "my eye" become the relative pronoun. Anything shorter that ends in ني
                # is a word that happens to, not a verb carrying an object.
                need = 3 if suf == 'ني' else 2      # 2 preserves the original guard exactly
                if x.endswith(suf) and len(x) - len(suf) >= need:
                    base = x[:-len(suf)]
                    out += [base, base + 'ه', 'ي' + base] + fem(base)
            for suf in ['وا','تو','تي','نا','ت','و']:                # past subject
                if x.endswith(suf) and len(x) > len(suf) + 1:
                    out.append(x[:-len(suf)])
            if x.endswith('ات') and len(x) > 3:                      # sound fem. plural
                out += [x[:-2] + 'ه', x[:-2]]
            for suf in ('ين','ون'):                        # sound masc. plural, and the DUAL
                if x.endswith(suf) and len(x) > len(suf) + 2:
                    base = x[:-len(suf)]
                    # ساعتين "two hours" is ساعة + ـتين. Same one-letter miss as above.
                    out += [base] + fem(base)
            if x.endswith('ه') and len(x) > 2:                       # feminine ending
                out.append(x[:-1])
            return out

        # TIER 1 — the word itself and its spelling variants. Highest priority: these
        # are real words, not fragments.
        tier1 = [w] + coda(w)
        # TIER 1b — suffixes off the whole word (طيارات -> طيارة, no prefix involved).
        # NOT stripped twice, though Arabic does stack them: سألوه is سأل + وا + ه. Measured, a
        # second pass resolves 1,292 more tokens and wrecks 542, because every extra stem is
        # another chance for a wrong word to win — لأني "because" became "No!", بقوة "with
        # force" became "pour water", الموت "death" became "pain". One strip is the floor that
        # keeps the stem list honest. Stacked suffixes need per-word adjudication, not a wider net.
        tier1b = []
        for x in tier1:
            for y in desuffix(x):
                tier1b += [y] + coda(y)

        # TIER 2 — prefix stripped. The prefix also tells us the verb form.
        pre = []
        if w.startswith('وب') and len(w) > 3:
            pre += [w[2:], 'ي' + w[2:]]; pos = 'VERB:I'
        elif w.startswith('بت') and len(w) > 3:
            pre += [w[2:], 'ي' + w[2:], 'ت' + w[2:]]; pos = 'VERB:I'
        elif w.startswith('ب') and len(w) > 2:
            pre += [w[1:], 'ي' + w[1:]]; pos = 'VERB:I'
        # Proclitics STACK, and this list is single-strip, so a compound has to be spelled out:
        # وبالمسا is و + بـ + الـ and one pass only ever took the و off. And هال is the spoken
        # demonstrative — هالبيت "this house" — which nothing here knew at all. Written out
        # rather than made compositional, because a second pass over the prefix list is the same
        # trade the suffix side lost: more stems, more chances for a wrong word to win.
        for p_ in ['وبال', 'فبال', 'وهال', 'بهال', 'لهال', 'هال', 'فب',   # 'وب' costs وبده 9 tokens
                   
                   'عال','بال','وال','فال','لل','ال','و','ع','ل','ف','ك']:
            if w.startswith(p_) and len(w) > len(p_) + 1:
                pre += [w[len(p_):], 'ال' + w[len(p_):]]
                if p_ in ('ال','بال','عال','وال','فال','وبال','فبال','هال','بهال','وهال','لهال'):
                    pos = pos or 'NOUN'
        # imperfect without b-: تضرب, ترمي, نوصل. Maknuune stores the يـ form.
        for base in [w] + list(pre):
            if base and base[0] in 'تنأا' and len(base) > 2:
                pre += [base[1:], 'ي' + base[1:]]

        tier2 = []
        for x in pre:
            tier2 += [x] + coda(x)
        # TIER 3 — suffixes off the prefix-stripped forms (the combinations).
        tier3 = []
        for x in tier2:
            for y in desuffix(x):
                tier3 += [y] + coda(y)

        # Tier 1 and 2 are the word with letters taken off the FRONT; 1b and 3 have had letters
        # taken off the BACK as well. Kept separately because the curated table may only be
        # reached the first way -- see prefix_stems().
        # A SECOND pass of suffix stripping, kept aside. Arabic stacks its suffixes -- سألوه is
        # سأل + وا + ه, شفتوا is شاف + ت + وا -- and one pass leaves سالو and شفت, neither of
        # which is a word. Folding these into the main list resolves 1,292 more tokens and
        # WRECKS 542, because every extra stem is another chance for a wrong word to win: لأني
        # "because" became "No!", بقوة "with force" became "pour water". So they are held here
        # and candidates() reaches for them only when nothing else matched at all, where they
        # cannot displace an answer because there is none.
        self._deep = list(dict.fromkeys(
            [z for y in tier1b + tier3 for z in desuffix(y)]))
        self._pre_only = list(dict.fromkeys(tier1 + tier2))
        return list(dict.fromkeys(tier1 + tier1b + tier2 + tier3)), pos

    def prefix_stems(self, w):
        """The stems reachable by stripping PREFIXES only.

        The curated table is consulted before the lexicon, so a stem that reaches it overrides
        a real answer rather than merely failing to help. Suffix stripping is where that goes
        wrong: مرات "times" loses its ت and lands on a curated مرا "woman"; بكرات "come early"
        lands on بكرا "tomorrow". A proclitic is different — a word genuinely does carry و/ب/ال
        in front of it, and بالكابتن IS the captain.

        Arabic's clitics run both ways, so this cannot be the whole story the way it is in
        Hebrew, where suffixes are possessives and a borrowed name never takes one. It is the
        half that was doing the damage.
        """
        self.morph(w)
        return self._pre_only

    def candidates(self, w):
        """Exact match wins. Only fall back to clitic-stripping if the word isn't real.

        Clitic stripping is AMBIGUOUS: the ب of بطال and بجد is a root letter, not the
        habitual prefix; the و of والله is root, not the conjunction. Applying the VERB:I
        filter to the whole set let stripped garbage beat the correct noun —
        مش بطال became "mish yt.uul" (طال, 'be long'). So: try the surface form first,
        unfiltered. Strip only when it isn't in the lexicon at all.
        """
        bare = norm(w)
        exact = []
        for tbl in (self.by_form, self.by_lemma):
            for r in tbl.get(bare, []):
                if not any(r['ID'] == e['ID'] for e in exact): exact.append(r)
        if exact:
            return exact

        stems, pos = self.morph(w)
        spell = {bare} | set(self.spellings(bare))     # the word itself, however it is spelled
        hits, seen = [], set()
        for st in stems:
            if st == bare: continue
            for tbl in (self.by_form, self.by_lemma):
                for r in tbl.get(st, []):
                    if r['ID'] not in seen:
                        seen.add(r['ID'])
                        r = dict(r); r['_stem'] = st       # which spelling found it
                        hits.append(r)
        # LAST RESORT ONLY: a word nothing matched gets the deeper peel. See morph()._deep.
        if not hits:
            for st in self._deep:
                if st == bare: continue
                for tbl in (self.by_form, self.by_lemma):
                    for r in tbl.get(st, []):
                        if r['ID'] not in seen:
                            seen.add(r['ID'])
                            r = dict(r); r['_stem'] = st
                            hits.append(r)
        # The pos filter exists to stop a STRIPPED fragment beating a correct word: مش بطال
        # became "be long" when the ب was read as a verb prefix. It must not be applied to the
        # word's own spelling, which is not a fragment of anything. بكرا "tomorrow" starts with
        # ب, so the heuristic declared it VERB:I and then discarded بكره — the actual answer —
        # leaving يبَكِّر "come early" as the best candidate for the word "tomorrow".
        if pos:
            keep = [h for h in hits if str(h['ANALYSIS']).startswith(pos)]
            if keep: hits = keep
        return hits

def entry_to_word(rec, surface):
    return {
        "surface": surface,
        "root":     str(rec['ROOT']),
        "lemma":    str(rec['LEMMA']),
        "form":     str(rec['FORM']),
        "caphi_raw": str(rec['CAPHI++']),          # template, uppercase = variable
        "caphi":    str(rec['CAPHI++']).replace(' ', ''),
        "gloss":    str(rec['GLOSS']),
        "analysis": str(rec['ANALYSIS']),
        "maknuune_id": str(rec['ID']),
        "village": None if str(rec.get('SOURCE')) in ('nan', 'None') else str(rec.get('SOURCE')),
    }
