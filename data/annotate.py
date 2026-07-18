"""Maknuune-backed annotator.

The rule this encodes: LOOK UP metadata, never generate it. Where Maknuune has no
entry we return None and flag it — we do not guess. Guessing is exactly what produced
the MSA-leaked roots (SPEC 7.4.1).
"""
import pandas as pd, re, sys

DIAC = re.compile(r'[ً-ْٰـ]')
def norm(s):
    s = DIAC.sub('', str(s))
    for a,b in [('أ','ا'),('إ','ا'),('آ','ا'),('ى','ي'),('ة','ه'),('ؤ','ء'),('ئ','ء')]:
        s = s.replace(a,b)
    return s.strip()

_df = pd.read_parquet('maknuune.parquet')
_df['_F'] = _df['FORM'].map(norm)
_df['_L'] = _df['LEMMA'].map(norm)
BY_FORM, BY_LEMMA = {}, {}
for _,r in _df.iterrows():
    BY_FORM.setdefault(r['_F'], []).append(r)
    BY_LEMMA.setdefault(r['_L'], []).append(r)

# Palestinian stacks clitics onto the stem. Maknuune stores citation forms, so we peel
# candidates off and try each. Ordered longest-first: عال = عا + ال.
def candidates(w):
    w = norm(w)
    out = [w]
    for pre in ['عال','وبال','وبت','بال','وال','فال','كال','ولل','بت','وب','ال','و','ب','ل','ع','ف','ك']:
        if w.startswith(pre) and len(w) > len(pre)+1:
            out.append(w[len(pre):])
            out.append('ال' + w[len(pre):])
    # b-imperfect: بَصْحى (I wake) vs Maknuune's يِصْحَى (3ms imperfect)
    if w.startswith('ب') and len(w) > 2:
        stem = w[1:]
        out += ['ي'+stem, 'ي'+stem[1:] if stem[0] in 'اتينأ' else 'ي'+stem, stem]
    for suf in ['ي','ك','ها','هم','نا','و']:          # possessives / object pronouns
        if w.endswith(suf) and len(w) > len(suf)+2:
            out.append(w[:-len(suf)])
            out.append(w[:-len(suf)]+'ه')
    return list(dict.fromkeys(out))

def lookup(word):
    for c in candidates(word):
        for table in (BY_FORM, BY_LEMMA):
            if c in table:
                r = table[c][0]
                return {"root": r['ROOT'], "lemma": r['LEMMA'], "form": r['FORM'],
                        "gloss": str(r['GLOSS'])[:38], "caphi": str(r['CAPHI++']).replace(' ',''),
                        "analysis": r['ANALYSIS'], "via": c}
    return None

def annotate(text, label):
    words = [w for w in re.split(r'[\s،.؟!]+', text) if w]
    hit = 0
    print("=" * 92)
    print(label)
    print("=" * 92)
    for w in words:
        a = lookup(w)
        if a:
            hit += 1
            print("  %-14s %-9s %-11s %-13s %s" %
                  (w, a['root'], a['caphi'][:11], str(a['analysis'])[:13], a['gloss'][:30]))
        else:
            print("  %-14s %s" % (w, "?? NOT IN MAKNUUNE — flag, do not guess"))
    print("-" * 92)
    print("  coverage: %d/%d = %d%%" % (hit, len(words), round(100*hit/len(words))))
    return hit, len(words)

if __name__ == "__main__":
    TEXTS = [
      ("MORNING COFFEE (Claude-written, human-reviewed, roots corrected)",
       "كل يوم الصبح بصحى بكير وبعمل قهوة ريحة الهيل بتملا البيت "
       "بقعد عالبلكونة وبشرب فنجاني على مهلي الشارع لسه هادي هاي أحلى لحظة بالنهار"),
    ]
    tot_h = tot_n = 0
    for t,l in TEXTS:
        h,n = annotate(l,t); tot_h += h; tot_n += n
