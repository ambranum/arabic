import pandas as pd, re
df = pd.read_parquet('maknuune.parquet')
DIAC = re.compile(r'[ً-ْٰـ]')
def bare(s): return DIAC.sub('', str(s)).strip()
df['_L'] = df['LEMMA'].map(bare)
df['_F'] = df['FORM'].map(bare)

# Match on undiacritized lemma, then disambiguate by gloss keyword — so we compare
# against the entry I actually meant, not whatever collided first.
CLAIMS = [
    ("كُلّ","ك-ل-ل","every"),      ("يَوْم","ي-و-م","day"),
    ("صُبْح","ص-ب-ح","morning"),   ("صِحي","ص-ح-و","wake"),
    ("بَكير","ب-ك-ر","early"),     ("عَمِل","ع-م-ل","do"),
    ("قَهْوة","ق-ه-و","coffee"),   ("ريحة","ر-و-ح","smell"),
    ("هيل","ه-ي-ل","cardamom"),    ("مَلا","م-ل-أ","fill"),
    ("بَيْت","ب-ي-ت","house"),     ("قَعَد","ق-ع-د","sit"),
    ("شِرِب","ش-ر-ب","drink"),     ("فِنْجان","ف-ن-ج-ن","cup"),
    ("مَهْل","م-ه-ل","slow"),      ("شارِع","ش-ر-ع","street"),
    ("لِسّا","—","still"),          ("هادي","ه-د-أ","calm"),
    ("حِلو","ح-ل-و","sweet"),      ("لَحْظة","ل-ح-ظ","moment"),
    ("نَهار","ن-ه-ر","day"),
]
def norm_root(r):
    return bare(r).replace('.','').replace('-','').replace('أ','ء').replace('إ','ء').replace('ا','ء')

real_err, ok, notfound = [], 0, []
for lemma, myroot, key in CLAIMS:
    b = bare(lemma)
    m = df[(df['_L']==b) | (df['_F']==b)]
    if not len(m):
        notfound.append(lemma); continue
    best = m[m['GLOSS'].astype(str).str.contains(key, case=False, na=False)]
    r = (best if len(best) else m).iloc[0]
    mk = str(r['ROOT'])
    if myroot == "—":
        real_err.append((lemma, "I claimed NO ROOT", mk, str(r['GLOSS'])[:28]))
    elif norm_root(mk) != norm_root(myroot):
        real_err.append((lemma, myroot, mk, str(r['GLOSS'])[:28]))
    else:
        ok += 1

print("REAL ROOT ERRORS (matched against the correct sense):")
print("-"*74)
for l, mine, theirs, g in real_err:
    print(f"  {l:9}  I said {mine:16} → Maknuune: {theirs:10}  ({g})")
print("-"*74)
print(f"  correct: {ok}   wrong: {len(real_err)}   not found: {notfound}")
print(f"  root error rate: {len(real_err)}/{ok+len(real_err)} = {100*len(real_err)//(ok+len(real_err))}%")
