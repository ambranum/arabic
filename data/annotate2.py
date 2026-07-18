"""Maknuune annotator v2 — retrieve CANDIDATES, don't pick blindly.

v1 lesson: first-match lookup guesses the wrong homograph ~40% of the time. Coverage
is not accuracy. So v2 never picks by itself. It returns the real Maknuune candidate
set, narrowed by morphology, and marks anything ambiguous for a disambiguation step.

The architecture that falls out: Claude's job is SELECTION among real entries, not
generation. It cannot invent ر-و-ح if the only options are what Maknuune actually has.
"""
import pandas as pd, re

DIAC = re.compile(r'[ً-ْٰـ]')
def norm(s):
    s = DIAC.sub('', str(s))
    for a,b in [('أ','ا'),('إ','ا'),('آ','ا'),('ى','ي'),('ة','ه'),('ؤ','ء'),('ئ','ء')]:
        s = s.replace(a,b)
    return s.strip()

_df = pd.read_parquet('maknuune.parquet')
_df['_F'] = _df['FORM'].map(norm)
_df['_L'] = _df['LEMMA'].map(norm)
FORMS = {}
for _,r in _df.iterrows():
    FORMS.setdefault(r['_F'], []).append(r)
LEMMAS = {}
for _,r in _df.iterrows():
    LEMMAS.setdefault(r['_L'], []).append(r)

def morph(w):
    """Peel Palestinian clitics; return (stems, expected_pos) — the prefix TELLS us the POS."""
    w = norm(w); stems=[w]; pos=None
    if w.startswith('وب') and len(w)>3:      # w- + b-  -> habitual verb
        stems += [w[2:], 'ي'+w[2:]]; pos='VERB'
    elif w.startswith('بت') and len(w)>3:    # b- + t-  -> habitual verb, 2nd/3fem
        stems += [w[2:], 'ي'+w[2:], 'ت'+w[2:]]; pos='VERB'
    elif w.startswith('ب') and len(w)>2:     # b-       -> habitual verb
        stems += [w[1:], 'ي'+w[1:]]; pos='VERB'
    for pre in ['عال','بال','وال','فال','ال','و','ع','ل','ف','ك']:
        if w.startswith(pre) and len(w)>len(pre)+1:
            stems.append(w[len(pre):]); stems.append('ال'+w[len(pre):])
            if pre in ('ال','بال','عال','وال','فال'): pos = pos or 'NOUN'  # ال = definite -> nominal
    for suf in ['ي','ك','ها','هم','نا']:
        if w.endswith(suf) and len(w)>len(suf)+2:
            stems += [w[:-len(suf)], w[:-len(suf)]+'ه']
    return list(dict.fromkeys(stems)), pos

def candidates(w):
    stems, pos = morph(w)
    hits=[]
    for s in stems:
        for tbl in (FORMS, LEMMAS):
            for r in tbl.get(s, []):
                if not any(r['ID']==h['ID'] for h in hits): hits.append(r)
    if pos:  # morphology constrains POS — drop entries that can't be right
        keep = [h for h in hits if str(h['ANALYSIS']).startswith(pos)]
        if keep: hits = keep
    return hits

TEXT = ("كل يوم الصبح بصحى بكير وبعمل قهوة ريحة الهيل بتملا البيت "
        "بقعد عالبلكونة وبشرب فنجاني على مهلي الشارع لسه هادي هاي أحلى لحظة بالنهار")

uniq = amb = none = 0
print("%-12s %-4s %s" % ("word","n","candidates (root · gloss)"))
print("-"*94)
for w in TEXT.split():
    c = candidates(w)
    if not c:
        none += 1; print("%-12s %-4s %s" % (w, 0, "?? not found — flag")); continue
    roots = list(dict.fromkeys([str(x['ROOT']) for x in c]))
    if len(roots) == 1:
        uniq += 1
        print("%-12s %-4s ✓ %s · %s" % (w, len(c), roots[0], str(c[0]['GLOSS'])[:34]))
    else:
        amb += 1
        opts = " | ".join("%s(%s)" % (r, str([x for x in c if str(x['ROOT'])==r][0]['GLOSS'])[:18]) for r in roots[:3])
        print("%-12s %-4s ? %s" % (w, len(c), opts))
print("-"*94)
n = len(TEXT.split())
print("unambiguous (safe to auto-fill): %d/%d = %d%%" % (uniq, n, round(100*uniq/n)))
print("ambiguous (needs disambiguation): %d" % amb)
print("not found (needs a human):        %d" % none)
