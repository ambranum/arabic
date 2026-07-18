"""Maknuune lookup — the metadata authority.

SPEC 7.4.2: retrieve real candidates, never generate. Morphology narrows by POS,
because the clitic tells you the part of speech before you look at anything else.
"""
import pandas as pd, re, os

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
            out = []
            for a_, b_ in (('ت','ث'), ('د','ذ'), ('ض','ظ')):
                if a_ in x: out.append(x.replace(a_, b_))
            return out

        def desuffix(x):
            """Every suffix-stripped form of x, cheapest first."""
            out = []
            for suf in ['ها','هم','هن','نا','كم','ي','ك','ه']:      # object / possessive
                if x.endswith(suf) and len(x) > len(suf) + 1:
                    base = x[:-len(suf)]
                    out += [base, base + 'ه', 'ي' + base]
            for suf in ['وا','تو','تي','نا','ت','و']:                # past subject
                if x.endswith(suf) and len(x) > len(suf) + 1:
                    out.append(x[:-len(suf)])
            if x.endswith('ات') and len(x) > 3:                      # sound fem. plural
                out += [x[:-2] + 'ه', x[:-2]]
            for suf in ('ين','ون'):                                  # sound masc. plural
                if x.endswith(suf) and len(x) > len(suf) + 2:
                    out.append(x[:-len(suf)])
            if x.endswith('ه') and len(x) > 2:                       # feminine ending
                out.append(x[:-1])
            return out

        # TIER 1 — the word itself and its spelling variants. Highest priority: these
        # are real words, not fragments.
        tier1 = [w] + coda(w)
        # TIER 1b — suffixes off the whole word (طيارات -> طيارة, no prefix involved).
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
        for p_ in ['عال','بال','وال','فال','لل','ال','و','ع','ل','ف','ك']:
            if w.startswith(p_) and len(w) > len(p_) + 1:
                pre += [w[len(p_):], 'ال' + w[len(p_):]]
                if p_ in ('ال','بال','عال','وال','فال'): pos = pos or 'NOUN'
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

        return list(dict.fromkeys(tier1 + tier1b + tier2 + tier3)), pos

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
        hits, seen = [], set()
        for st in stems:
            if st == bare: continue
            for tbl in (self.by_form, self.by_lemma):
                for r in tbl.get(st, []):
                    if r['ID'] not in seen:
                        seen.add(r['ID']); hits.append(r)
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
