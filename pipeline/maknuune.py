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
        """Peel Palestinian clitics. Returns (stems, exact ANALYSIS constraint or None).

        The prefix doesn't just say "verb" — it says WHICH verb form. b- is the habitual
        present, so it can only be VERB:I. Accepting any VERB here is what let بصحى match
        the causative imperative "wake sb up" instead of "wake up".
        """
        w = norm(w); pos = None
        def codavars(x):
            out = []
            for a, b in (('ت','ث'), ('د','ذ'), ('ض','ظ')):
                if a in x: out.append(x.replace(a, b))
            return out
        # Whole-word spelling variants FIRST: كتير -> كثير is a real word; كتير -> تير
        # is a fragment left by stripping a fake ك- clitic. Order decides which wins.
        stems = [w] + codavars(w)
        if w.startswith('وب') and len(w) > 3:
            stems += [w[2:], 'ي' + w[2:]]; pos = 'VERB:I'
        elif w.startswith('بت') and len(w) > 3:
            stems += [w[2:], 'ي' + w[2:], 'ت' + w[2:]]; pos = 'VERB:I'
        elif w.startswith('ب') and len(w) > 2:
            stems += [w[1:], 'ي' + w[1:]]; pos = 'VERB:I'
        for pre in ['عال','بال','وال','فال','لل','ال','و','ع','ل','ف','ك']:
            if w.startswith(pre) and len(w) > len(pre) + 1:
                stems += [w[len(pre):], 'ال' + w[len(pre):]]
                if pre in ('ال','بال','عال','وال','فال'): pos = pos or 'NOUN'
        for suf in ['ي','ك','ها','هم','نا']:
            if w.endswith(suf) and len(w) > len(suf) + 2:
                stems += [w[:-len(suf)], w[:-len(suf)] + 'ه']
        # Feminine ending: تانية -> (coda) ثانية -> ثاني
        if w.endswith('ه') and len(w) > 2:
            base = w[:-1]
            stems += [base] + codavars(base)

        # Past-tense subject suffixes. Maknuune stores the 3ms perfect (عَمَل), but text
        # carries عملت (3fs/1sg), نزلوا (3pl), توقعوا. Without this the whole past tense
        # is invisible to the lexicon.
        for suf, _p in [('وا','VERB:P'), ('تو','VERB:P'), ('ت','VERB:P'),
                        ('نا','VERB:P'), ('تي','VERB:P'), ('و','VERB:P')]:
            if w.endswith(suf) and len(w) > len(suf) + 1:
                stems.append(w[:-len(suf)])

        # Dialect vs CODA spelling. Maknuune spells etymologically (ثانية، أكثر، ثلاثين);
        # people write phonetically (تانية، أكتر، تلاتين) because the interdentals merged.
        # Try the etymological spelling for every candidate produced so far.
        for st in list(stems):
            stems += codavars(st)
        return list(dict.fromkeys(stems)), pos

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
