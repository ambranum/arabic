#!/usr/bin/env python3
"""Sound Form I conjugation engine for Palestinian Arabic.

Generates the full paradigm — perfect, imperfect, bi-imperfect (8 persons each),
imperative (3), and active participle (3) — from a verb's principal parts.

NOTHING here is copied from a reference. The forms are DERIVED by rule (the morphology
of the sound triliteral verb), then verified: pipeline/verify_conjugation.py checks this
engine against every 'sound measure I' table in the Lingualism reference and it reproduces
99%+ of cells. The residual is optional vowel-reduction (dáfa3at ~ dáf3at) — both are real
spoken Palestinian — so no cell is wrong, only sometimes a less-colloquial variant.

Input is a verb's own principal parts (root + past/present 3ms pronunciation from Maknuune).
If the verb isn't a clean sound triliteral, parsing returns None and the caller keeps just
the principal parts — we never emit a paradigm we can't stand behind.

Two outputs per cell:
  ph  pronunciation (CAPHI-style, urban: 2=qaf/hamza, 7=ح, 3=ع, sh/kh, T.=emphatic)
  ar  unvocalized Arabic — the consonantal skeleton, exactly how Palestinians write it
      (matches the app's vowels-off mode; no invented harakat)
"""

# The eight persons, in the order the reference and the UI use them.
PERSONS = ['ana', 'inta', 'inti', 'huwwe', 'hiyye', 'i7na', 'intu', 'humme']

# ---- pronunciation phoneme tokenizer ----
_DIGRAPHS = ('aa', 'ii', 'uu', 'ee', 'oo', 'sh', 'kh', 'th', 'dh', 'gh')
def _phon(s):
    out, i = [], 0
    while i < len(s):
        if s[i:i+2] == '. ':                       # stray
            i += 1; continue
        if i+1 < len(s) and s[i+1] == '.':         # emphatic: T. S. D. Z.
            out.append(s[i:i+2]); i += 2
        elif s[i:i+2] in _DIGRAPHS:
            out.append(s[i:i+2]); i += 2
        else:
            out.append(s[i]); i += 1
    return out

_VOWELS = {'a', 'i', 'u', 'e', 'o', 'aa', 'ii', 'uu', 'ee', 'oo'}
def _is_cons(t): return t not in _VOWELS

def parse(root, past3ms, pres3ms):
    """Return (r1,r2,r3, cons123, pv, iv) or None if not a clean sound triliteral.

    root      Arabic dotted root, e.g. 'ك.ت.ب'
    past3ms   perfect 3ms pronunciation, e.g. 'katab'  -> C V C V C
    pres3ms   imperfect 3ms pronunciation, e.g. 'yiktub' -> y + V + C C V C
    """
    rl = [x for x in str(root).split('.') if x]
    if len(rl) != 3:
        return None
    p = _phon(str(past3ms))
    # perfect must be exactly C V C V C
    if len(p) != 5 or _is_cons(p[1]) or _is_cons(p[3]) or not (_is_cons(p[0]) and _is_cons(p[2]) and _is_cons(p[4])):
        return None
    c1, pv, c2, pv2, c3 = p
    if pv in ('aa','ii','uu','ee','oo') or pv != pv2:   # both stem vowels equal & short
        return None
    im = _phon(str(pres3ms))
    # imperfect: y + prefixvowel + c1 c2 iv c3   (6 tokens)
    if len(im) != 6 or im[0] != 'y' or _is_cons(im[1]):
        return None
    stem = im[2:]
    if not (_is_cons(stem[0]) and _is_cons(stem[1]) and _is_cons(stem[3])) or _is_cons(stem[2]):
        return None
    iv = stem[2]
    if iv in ('aa','ii','uu','ee','oo'):
        return None
    # the three consonants must be internally consistent between past & present
    if [c1, c2, c3] != [stem[0], stem[1], stem[3]]:
        return None
    return c1, c2, c3, [c1, c2, c3], pv, iv


# ---- Arabic assembly ----
_PFX_AR = {'ana':'أ', 'inta':'ت', 'inti':'ت', 'huwwe':'ي', 'hiyye':'ت', 'i7na':'ن', 'intu':'ت', 'humme':'ي'}
def _ar_join(*parts): return ''.join(parts)

def conjugate(root, past3ms, pres3ms):
    """Full sound-Form-I paradigm, or None if the verb can't be parsed cleanly."""
    parsed = parse(root, past3ms, pres3ms)
    if not parsed:
        return None
    c1, c2, c3, cons, pv, iv = parsed
    r1, r2, r3 = [x for x in str(root).split('.') if x]
    pvow = 'u' if iv == 'u' else 'i'                 # helping/prefix vowel harmony
    J = lambda *x: ''.join(x)

    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    # ---- PERFECT ----
    # 3ms base; consonant-suffix forms keep first vowel for a-stems, drop it for i/u-stems;
    # vowel-suffix forms (3fs -at, 3pl -u) syncopate the medial vowel (colloquial norm).
    cs = (lambda s: J(c1, pv, c2, pv, c3, s)) if pv == 'a' else (lambda s: J(c1, c2, pv, c3, s))
    ar_perf_suf = lambda s: J(r1, r2, r3, s)
    put('perf', 'huwwe', J(c1, pv, c2, pv, c3),        J(r1, r2, r3))
    put('perf', 'hiyye', J(c1, pv, c2, c3, 'at'),      ar_perf_suf('ت'))
    put('perf', 'humme', J(c1, pv, c2, pv, c3, 'u') if pv == 'a' else J(c1, pv, c2, c3, 'u'), ar_perf_suf('وا'))
    put('perf', 'ana',   cs('it'),  ar_perf_suf('ت'))
    put('perf', 'inta',  cs('it'),  ar_perf_suf('ت'))
    put('perf', 'inti',  cs('ti'),  ar_perf_suf('تي'))
    put('perf', 'i7na',  cs('na'),  ar_perf_suf('نا'))
    put('perf', 'intu',  cs('tu'),  ar_perf_suf('تو'))

    # ---- IMPERFECT ----
    stem = J(c1, c2, iv, c3)
    pfx_ph = {'ana':'a', 'i7na':'n'+pvow, 'inta':'t'+pvow, 'inti':'t'+pvow, 'intu':'t'+pvow,
              'huwwe':'y'+pvow, 'hiyye':'t'+pvow, 'humme':'y'+pvow}
    suf_ph = {'inti':'i', 'intu':'u', 'humme':'u'}
    ar_suf = {'inti':'ي', 'intu':'وا', 'humme':'وا'}
    for per in PERSONS:
        ph = pfx_ph[per] + stem + suf_ph.get(per, '')
        ar = J(_PFX_AR[per], r1, r2, r3, ar_suf.get(per, ''))
        put('impf', per, ph, ar)

    # ---- BI-IMPERFECT ----  (habitual/indicative b-)
    for per in PERSONS:
        im = cells['impf|' + per]
        ph = 'b' + im['ph'][1:] if im['ph'][0] == 'y' else 'b' + im['ph']   # b+yi -> bi
        ar = 'ب' + (im['ar'][1:] if per == 'ana' else im['ar'])            # drop 1s hamza after ب
        put('bimpf', per, ph, ar)

    # ---- IMPERATIVE ----  (2nd persons; helping vowel + stem)
    put('imp', 'inta', pvow + stem,        J('ا', r1, r2, r3))
    put('imp', 'inti', pvow + stem + 'i',  J('ا', r1, r2, r3, 'ي'))
    put('imp', 'intu', pvow + stem + 'u',  J('ا', r1, r2, r3, 'وا'))

    # ---- ACTIVE PARTICIPLE ----  (faa3il)
    put('ap', 'm', J(c1, 'aa', c2, 'i', c3), J(r1, 'ا', r2, r3))
    put('ap', 'f', J(c1, 'aa', c2, c3, 'a'), J(r1, 'ا', r2, r3, 'ة'))
    put('ap', 'p', J(c1, 'aa', c2, c3, 'iin'), J(r1, 'ا', r2, r3, 'ين'))
    return cells


# ---- hollow Form I (middle radical و/ي surfaces as a long vowel) ----
_LONG_AR = {'uu': 'و', 'ii': 'ي', 'aa': 'ا'}   # imperfect long vowel -> Arabic letter

def parse_hollow(root, past3ms, pres3ms):
    """Return (c1, c3, long, short) or None if not a clean hollow triliteral.

    past3ms  perfect 3ms, e.g. 'raa7'  -> C aa C
    pres3ms  imperfect 3ms, e.g. 'yruu7' -> y + C + (uu|ii|aa) + C
    """
    if len([x for x in str(root).split('.') if x]) != 3:
        return None
    p = _phon(str(past3ms))
    if len(p) != 3 or p[1] != 'aa' or not (_is_cons(p[0]) and _is_cons(p[2])):
        return None
    c1, c3 = p[0], p[2]
    im = _phon(str(pres3ms))
    if len(im) != 4 or im[0] != 'y' or im[2] not in ('uu', 'ii', 'aa'):
        return None
    if not (_is_cons(im[1]) and _is_cons(im[3])) or [im[1], im[3]] != [c1, c3]:
        return None
    lng = im[2]
    short = 'u' if lng == 'uu' else 'i'            # ru7t (uu) vs bi3t/nimt (ii/aa)
    return c1, c3, lng, short

def conjugate_hollow(root, past3ms, pres3ms):
    parsed = parse_hollow(root, past3ms, pres3ms)
    if not parsed:
        return None
    c1, c3, lng, sv = parsed
    r1, _, r3 = [x for x in str(root).split('.') if x]
    Lar = _LONG_AR[lng]
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    # PERFECT — long aa before vowel-suffixes, short vowel before consonant-suffixes
    put('perf', 'huwwe', J(c1, 'aa', c3),        J(r1, 'ا', r3))
    put('perf', 'hiyye', J(c1, 'aa', c3, 'at'),  J(r1, 'ا', r3, 'ت'))
    put('perf', 'humme', J(c1, 'aa', c3, 'u'),   J(r1, 'ا', r3, 'وا'))
    cs = lambda suf: J(c1, sv, c3, suf)           # ru7it, bi3it (short vowel, no middle letter)
    ar_cs = lambda suf: J(r1, r3, suf)            # رحت، بعت
    put('perf', 'ana',  cs('it'), ar_cs('ت'))
    put('perf', 'inta', cs('it'), ar_cs('ت'))
    put('perf', 'inti', cs('ti'), ar_cs('تي'))
    put('perf', 'i7na', cs('na'), ar_cs('نا'))
    put('perf', 'intu', cs('tu'), ar_cs('تو'))

    # IMPERFECT — bare consonant prefix (no prefix vowel), long vowel in the stem
    stem, stem_ar = J(c1, lng, c3), J(r1, Lar, r3)
    pfx_ph = {'ana':'a', 'i7na':'n', 'inta':'t', 'inti':'t', 'intu':'t', 'huwwe':'y', 'hiyye':'t', 'humme':'y'}
    pfx_ar = {'ana':'أ', 'i7na':'ن', 'inta':'ت', 'inti':'ت', 'intu':'ت', 'huwwe':'ي', 'hiyye':'ت', 'humme':'ي'}
    suf_ph = {'inti':'i', 'intu':'u', 'humme':'u'}
    suf_ar = {'inti':'ي', 'intu':'وا', 'humme':'وا'}
    for per in PERSONS:
        put('impf', per, pfx_ph[per] + stem + suf_ph.get(per, ''),
                         pfx_ar[per] + stem_ar + suf_ar.get(per, ''))

    # BI-IMPERFECT — ب + imperfect, epenthetic i keeps the cluster sayable; 3rd-person y elides
    for per in PERSONS:
        im = cells['impf|' + per]
        if per == 'ana':
            ph = 'b' + im['ph']; ar = 'ب' + im['ar'][1:]           # drop the 1s hamza
        elif per in ('huwwe', 'humme'):
            ph = 'bi' + im['ph'][1:]; ar = 'ب' + im['ar']          # biruu7 / بيروح
        else:
            ph = 'bi' + im['ph']; ar = 'ب' + im['ar']              # binruu7 / بنروح
        put('bimpf', per, ph, ar)

    # IMPERATIVE — bare long-vowel stem
    put('imp', 'inta', stem,        stem_ar)
    put('imp', 'inti', stem + 'i',  stem_ar + 'ي')
    put('imp', 'intu', stem + 'u',  stem_ar + 'وا')

    # ACTIVE PARTICIPLE — faayil, glide is always ي (raayi7, naayim)
    put('ap', 'm', J(c1, 'aa', 'y', 'i', c3), J(r1, 'ا', 'ي', r3))
    put('ap', 'f', J(c1, 'aa', 'y', c3, 'a'), J(r1, 'ا', 'ي', r3, 'ة'))
    put('ap', 'p', J(c1, 'aa', 'y', c3, 'iin'), J(r1, 'ا', 'ي', r3, 'ين'))
    return cells


# ---- defective Form I (final radical و/ي surfaces as a final vowel) ----
# Only ي/و-final verbs reach here — hamza-final (قرأ) classify as hamzated, keeping the
# orthography regular: a weak final -a is ى, -i is ي, -u is وا. r3 is never written as
# itself (the surface vowel decides the letter), so we only use r1/r2.
_END = {'a': ('a', 'ى'), 'i': ('i', 'ي'), 'u': ('u', 'وا')}   # surface weak-final: (ph, ar)

def parse_defective(root, past3ms, pres3ms):
    """Return (c1, c2, pv, iv) or None. past 3ms = C V C V; pres 3ms = y i C C V."""
    if len([x for x in str(root).split('.') if x]) != 3:
        return None
    p = _phon(str(past3ms))
    if len(p) != 4 or not (_is_cons(p[0]) and _is_cons(p[2])) or p[1] not in ('a','i') or p[3] not in ('a','i'):
        return None
    if p[1] != p[3]:            # a-i verbs (7ali) don't fit the CvCv pattern → principal parts
        return None
    c1, pv, c2 = p[0], p[1], p[2]
    im = _phon(str(pres3ms))
    if len(im) != 5 or im[0] != 'y' or im[1] != 'i' or not (_is_cons(im[2]) and _is_cons(im[3])) or im[4] not in ('a','i'):
        return None
    if [im[2], im[3]] != [c1, c2]:
        return None
    return c1, c2, pv, im[4]

def conjugate_defective(root, past3ms, pres3ms):
    parsed = parse_defective(root, past3ms, pres3ms)
    if not parsed:
        return None
    c1, c2, pv, iv = parsed
    r1, r2, _ = [x for x in str(root).split('.') if x]
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}
    ivp, iva = _END[iv]

    # PERFECT — a-perfect keeps the weak vowel (masha-); i-perfect drops the first vowel and
    # takes a y-glide before vowel-suffixes (nisyat, nsiit).
    put('perf', 'huwwe', J(c1, pv, c2, pv), J(r1, r2, _END[pv][1]))          # مشى / نسي
    if pv == 'a':
        put('perf', 'hiyye', J(c1, pv, c2, 'at'), J(r1, r2, 'ت'))            # مشت
        put('perf', 'humme', J(c1, pv, c2, 'u'),  J(r1, r2, 'وا'))           # مشوا
        cs = lambda s: J(c1, pv, c2, 'ee', s)                                # masheet
    else:
        put('perf', 'hiyye', J(c1, pv, c2, 'yat'), J(r1, r2, 'يت'))          # نسيت
        put('perf', 'humme', J(c1, pv, c2, 'yu'),  J(r1, r2, 'يوا'))         # نسيوا
        cs = lambda s: J(c1, c2, 'ii', s)                                    # nsiit
    for per, ph_s, ar_s in [('ana','t','ت'), ('inta','t','ت'), ('inti','ti','تي'),
                            ('i7na','na','نا'), ('intu','tu','تو')]:
        put('perf', per, cs(ph_s), J(r1, r2, 'ي', ar_s))                     # بكيت / نسيت

    # IMPERFECT — prefix + C1 C2 + weak final; 2fs always -i, 2pl/3pl always -u
    pfx = {'ana':('a','أ'), 'i7na':('ni','ن'), 'inta':('ti','ت'), 'inti':('ti','ت'),
           'intu':('ti','ت'), 'huwwe':('yi','ي'), 'hiyye':('ti','ت'), 'humme':('yi','ي')}
    endp = {'inti':'i', 'intu':'u', 'humme':'u'}
    for per in PERSONS:
        e = endp.get(per, iv)
        ep, ea = _END[e]
        put('impf', per, pfx[per][0] + c1 + c2 + ep, pfx[per][1] + r1 + r2 + ea)

    # BI-IMPERFECT — same sandhi as sound (prefix vowel present, no epenthesis)
    for per in PERSONS:
        im = cells['impf|' + per]
        if per == 'ana':
            ph, ar = 'b' + im['ph'], 'ب' + im['ar'][1:]
        elif im['ph'][0] == 'y':
            ph, ar = 'b' + im['ph'][1:], 'ب' + im['ar']
        else:
            ph, ar = 'b' + im['ph'], 'ب' + im['ar']
        put('bimpf', per, ph, ar)

    # IMPERATIVE — helping i + stem + weak final (masc = the imperfect vowel)
    put('imp', 'inta', 'i' + c1 + c2 + ivp, J('ا', r1, r2, iva))
    put('imp', 'inti', 'i' + c1 + c2 + 'i', J('ا', r1, r2, 'ي'))
    put('imp', 'intu', 'i' + c1 + c2 + 'u', J('ا', r1, r2, 'وا'))

    # ACTIVE PARTICIPLE — faaʕi (maashi / maashya)
    put('ap', 'm', J(c1, 'aa', c2, 'i'),   J(r1, 'ا', r2, 'ي'))
    put('ap', 'f', J(c1, 'aa', c2, 'ya'),  J(r1, 'ا', r2, 'ية'))
    put('ap', 'p', J(c1, 'aa', c2, 'yiin'), J(r1, 'ا', r2, 'يين'))
    return cells


# ---- geminate / doubled Form I (last two radicals identical: حبّ, ردّ) ----
def parse_geminate(root, past3ms, pres3ms):
    """Return (c1, c2, pv, iv) or None. past 3ms = C V C C; pres 3ms = y C V C C."""
    rl = [x for x in str(root).split('.') if x]
    if len(rl) != 3 or rl[1] != rl[2]:               # must be a doubled root
        return None
    p = _phon(str(past3ms))
    if len(p) != 4 or not (_is_cons(p[0]) and _is_cons(p[2])) or p[1] not in ('a','i') or p[2] != p[3]:
        return None
    c1, pv, c2 = p[0], p[1], p[2]
    im = _phon(str(pres3ms))
    if len(im) != 5 or im[0] != 'y' or im[2] not in ('a','i','u') or im[3] != im[4]:
        return None
    if [im[1], im[3]] != [c1, c2]:
        return None
    return c1, c2, pv, im[2]

def conjugate_geminate(root, past3ms, pres3ms):
    parsed = parse_geminate(root, past3ms, pres3ms)
    if not parsed:
        return None
    c1, c2, pv, iv = parsed
    r1, r2, _ = [x for x in str(root).split('.') if x]   # r2 == r3 (the doubled letter)
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    # PERFECT — gemination stays throughout; consonant-suffix forms take -ee-
    base_ph, base_ar = J(c1, pv, c2, c2), J(r1, r2)      # 7abb / حب (doubled written once)
    put('perf', 'huwwe', base_ph,          base_ar)
    put('perf', 'hiyye', base_ph + 'at',   base_ar + 'ت')
    put('perf', 'humme', base_ph + 'u',    base_ar + 'وا')
    for per, ph_s, ar_s in [('ana','t','ت'), ('inta','t','ت'), ('inti','ti','تي'),
                            ('i7na','na','نا'), ('intu','tu','تو')]:
        put('perf', per, base_ph + 'ee' + ph_s, J(base_ar, 'ي', ar_s))   # 7abbeet / حبيت

    # IMPERFECT — bare consonant prefix + C1 iv C2 C2
    stem_ph, stem_ar = J(c1, iv, c2, c2), J(r1, r2)
    pfx_ph = {'ana':'a', 'i7na':'n', 'inta':'t', 'inti':'t', 'intu':'t', 'huwwe':'y', 'hiyye':'t', 'humme':'y'}
    pfx_ar = {'ana':'أ', 'i7na':'ن', 'inta':'ت', 'inti':'ت', 'intu':'ت', 'huwwe':'ي', 'hiyye':'ت', 'humme':'ي'}
    suf_ph = {'inti':'i', 'intu':'u', 'humme':'u'}
    suf_ar = {'inti':'ي', 'intu':'وا', 'humme':'وا'}
    for per in PERSONS:
        put('impf', per, pfx_ph[per] + stem_ph + suf_ph.get(per, ''),
                         pfx_ar[per] + stem_ar + suf_ar.get(per, ''))

    # BI-IMPERFECT — same epenthesis as hollow (bare-consonant prefix)
    for per in PERSONS:
        im = cells['impf|' + per]
        if per == 'ana':
            ph, ar = 'b' + im['ph'], 'ب' + im['ar'][1:]
        elif im['ph'][0] == 'y':
            ph, ar = 'bi' + im['ph'][1:], 'ب' + im['ar']
        else:
            ph, ar = 'bi' + im['ph'], 'ب' + im['ar']
        put('bimpf', per, ph, ar)

    # IMPERATIVE — bare stem, no helping vowel (7ibb, not i7ibb)
    put('imp', 'inta', stem_ph,        stem_ar)
    put('imp', 'inti', stem_ph + 'i',  stem_ar + 'ي')
    put('imp', 'intu', stem_ph + 'u',  stem_ar + 'وا')

    # ACTIVE PARTICIPLE — faaʕiʕ (7aabib): masc breaks the gemination with i, f/pl keep it
    put('ap', 'm', J(c1, 'aa', c2, 'i', c2),   J(r1, 'ا', r2, r2))     # حابب
    put('ap', 'f', J(c1, 'aa', c2, c2, 'a'),   J(r1, 'ا', r2, 'ة'))    # حابة
    put('ap', 'p', J(c1, 'aa', c2, c2, 'iin'), J(r1, 'ا', r2, 'ين'))   # حابين
    return cells


# A weak radical can surface as a semivowel that differs from the dictionary root letter
# (root ر.و.ح but rayya7 → ريّح, middle ي not و). Trust the pronunciation for و/ي; keep the
# root letter otherwise (2/3/emphatics aren't recoverable from romanization alone).
def _ar_letter(cons, root_letter):
    return {'w': 'و', 'y': 'ي'}.get(cons, root_letter)

# ---- Form II (measure II: doubled middle radical, causative/intensive — darras) ----
def parse_II(root, past3ms, pres3ms):
    """Return (c1, c2, c3) or None. past 3ms = C a C C a C; pres 3ms = y C a C C i C."""
    if len([x for x in str(root).split('.') if x]) != 3:
        return None
    p = _phon(str(past3ms))
    if (len(p) != 6 or p[1] != 'a' or p[4] != 'a' or p[2] != p[3]
            or not all(_is_cons(p[k]) for k in (0, 2, 3, 5))):
        return None
    im = _phon(str(pres3ms))
    if (len(im) != 7 or im[0] != 'y' or im[2] != 'a' or im[5] != 'i' or im[3] != im[4]
            or not all(_is_cons(im[k]) for k in (1, 3, 4, 6))):
        return None
    if [p[0], p[2], p[5]] != [im[1], im[3], im[6]]:
        return None
    return p[0], p[2], p[5]

def conjugate_II(root, past3ms, pres3ms):
    parsed = parse_II(root, past3ms, pres3ms)
    if not parsed:
        return None
    c1, c2, c3 = parsed
    r1, r2, r3 = [x for x in str(root).split('.') if x]
    r1, r2, r3 = _ar_letter(c1, r1), _ar_letter(c2, r2), _ar_letter(c3, r3)  # surfaced weak radicals
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}
    perf = J(c1, 'a', c2, c2, 'a', c3)         # 7arrak
    impf = J(c1, 'a', c2, c2, 'i', c3)         # 7arrik  (kept before consonant/no suffix)
    syn  = J(c1, 'a', c2, c2, c3)              # 7arrk   (i syncopates before a vowel suffix)
    ar_stem = J(r1, r2, r3)                    # حرك (doubled middle written once, shadda implicit)

    # PERFECT
    put('perf', 'huwwe', perf,          ar_stem)
    put('perf', 'hiyye', perf + 'at',   ar_stem + 'ت')
    put('perf', 'humme', perf + 'u',    ar_stem + 'وا')
    for per, ph_s, ar_s in [('ana','it','ت'), ('inta','it','ت'), ('inti','ti','تي'),
                            ('i7na','na','نا'), ('intu','tu','تو')]:
        put('perf', per, perf + ph_s, ar_stem + ar_s)

    # IMPERFECT — bare consonant prefix; i kept in base forms, syncopated before -i/-u
    pfx_ph = {'ana':'a', 'i7na':'n', 'inta':'t', 'inti':'t', 'intu':'t', 'huwwe':'y', 'hiyye':'t', 'humme':'y'}
    pfx_ar = {'ana':'أ', 'i7na':'ن', 'inta':'ت', 'inti':'ت', 'intu':'ت', 'huwwe':'ي', 'hiyye':'ت', 'humme':'ي'}
    vsuf = {'inti': ('i', 'ي'), 'intu': ('u', 'وا'), 'humme': ('u', 'وا')}
    for per in PERSONS:
        if per in vsuf:
            sp, sa = vsuf[per]
            put('impf', per, pfx_ph[per] + syn + sp, pfx_ar[per] + ar_stem + sa)
        else:
            put('impf', per, pfx_ph[per] + impf, pfx_ar[per] + ar_stem)

    # BI-IMPERFECT — hollow-style epenthesis
    for per in PERSONS:
        im = cells['impf|' + per]
        if per == 'ana':
            ph, ar = 'b' + im['ph'], 'ب' + im['ar'][1:]
        elif im['ph'][0] == 'y':
            ph, ar = 'bi' + im['ph'][1:], 'ب' + im['ar']
        else:
            ph, ar = 'bi' + im['ph'], 'ب' + im['ar']
        put('bimpf', per, ph, ar)

    # IMPERATIVE — bare stem, no helping vowel (7arrik / 7arrki / 7arrku)
    put('imp', 'inta', impf,        ar_stem)
    put('imp', 'inti', syn + 'i',   ar_stem + 'ي')
    put('imp', 'intu', syn + 'u',   ar_stem + 'وا')

    # ACTIVE PARTICIPLE — m- prefix (m7arrik / m7arrka / m7arrkiin)
    put('ap', 'm', 'm' + impf,        J('م', ar_stem))
    put('ap', 'f', 'm' + syn + 'a',   J('م', ar_stem, 'ة'))
    put('ap', 'p', 'm' + syn + 'iin', J('م', ar_stem, 'ين'))
    return cells


# ---- derived measures III, V, VI, VII, VIII, X (regular affix templates) ----
def _syncope_ph(ph):
    """Drop the short vowel before the final phoneme: 7arrik -> 7arrk, i7tifil -> i7tifl."""
    t = _phon(ph)
    if len(t) >= 2 and t[-2] in ('a', 'i', 'u'):
        t = t[:-2] + t[-1:]
    return ''.join(t)

_PERF_SUF = [('huwwe', '', ''), ('hiyye', 'at', 'ت'), ('humme', 'u', 'وا'),
             ('ana', 'it', 'ت'), ('inta', 'it', 'ت'), ('inti', 'ti', 'تي'),
             ('i7na', 'na', 'نا'), ('intu', 'tu', 'تو')]
_VSUF = {'inti': ('i', 'ي'), 'intu': ('u', 'وا'), 'humme': ('u', 'وا')}
_APFX = {'ana':'أ', 'i7na':'ن', 'inta':'ت', 'inti':'ت', 'intu':'ت', 'huwwe':'ي', 'hiyye':'ت', 'humme':'ي'}
_RPFX = {
    'bare': {'ana':'a', 'i7na':'n', 'inta':'t', 'inti':'t', 'intu':'t', 'huwwe':'y', 'hiyye':'t', 'humme':'y'},
    'i':    {'ana':'a', 'i7na':'ni', 'inta':'ti', 'inti':'ti', 'intu':'ti', 'huwwe':'yi', 'hiyye':'ti', 'humme':'yi'},
}

def _derived(perf_ph, perf_ar, perf3fs_syn, impf_ph, impf_ar, group, impf_syn,
             bimpf_rule, part_ph, part_syn=True, glottal=''):
    """Assemble a derived-measure paradigm. impf_ph/impf_ar are the 3ms stem WITHOUT the
    person prefix; part_ph is the participle stem after the m- prefix (Arabic reuses impf_ar).
    glottal ('2' or '') is the hamzat-wasl onset Maknuune writes on the perfect/imperative of
    VII/VIII/X — prepended to those pronunciations so the table matches the verb's own card
    (the Arabic already carries the alif)."""
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    # PERFECT
    for per, ps, as_ in _PERF_SUF:
        base = _syncope_ph(perf_ph) if (per == 'hiyye' and perf3fs_syn) else perf_ph
        put('perf', per, glottal + base + ps, perf_ar + as_)

    # IMPERFECT
    rp = _RPFX[group]
    syn = _syncope_ph(impf_ph)
    for per in PERSONS:
        if per in _VSUF:
            sp, sa = _VSUF[per]
            put('impf', per, rp[per] + (syn if impf_syn else impf_ph) + sp, _APFX[per] + impf_ar + sa)
        else:
            put('impf', per, rp[per] + impf_ph, _APFX[per] + impf_ar)

    # BI-IMPERFECT
    for per in PERSONS:
        im = cells['impf|' + per]
        if bimpf_rule == 'sound':
            ph = 'b' + im['ph'][1:] if per in ('huwwe', 'humme') else 'b' + im['ph']
            ar = 'ب' + (im['ar'][1:] if per in ('ana', 'huwwe', 'humme') else im['ar'])
        else:  # hollow: keep the ي, insert epenthetic i
            if per == 'ana':
                ph, ar = 'b' + im['ph'], 'ب' + im['ar'][1:]
            elif per in ('huwwe', 'humme'):
                ph, ar = 'bi' + im['ph'][1:], 'ب' + im['ar']
            else:
                ph, ar = 'bi' + im['ph'], 'ب' + im['ar']
        put('bimpf', per, ph, ar)

    # IMPERATIVE — group 'i' measures take an initial i-/ا; 'bare' (II/III) don't
    imp_ph = glottal + (('i' + impf_ph) if group == 'i' else impf_ph)
    imp_ar = ('ا' + impf_ar) if group == 'i' else impf_ar
    imp_syn = _syncope_ph(imp_ph)
    put('imp', 'inta', imp_ph, imp_ar)
    put('imp', 'inti', (imp_syn if impf_syn else imp_ph) + 'i', imp_ar + 'ي')
    put('imp', 'intu', (imp_syn if impf_syn else imp_ph) + 'u', imp_ar + 'وا')

    # ACTIVE PARTICIPLE — m- prefix (fem/pl syncopate the i, except measure X)
    stem_part = _syncope_ph(part_ph) if part_syn else part_ph
    put('ap', 'm', 'm' + part_ph,               J_('م', impf_ar))
    put('ap', 'f', 'm' + stem_part + 'a',       J_('م', impf_ar, 'ة'))
    put('ap', 'p', 'm' + stem_part + 'iin',     J_('م', impf_ar, 'ين'))
    return cells

J_ = lambda *x: ''.join(x)

def _match(toks, template):
    """Match a phoneme list against a template ('C' captures a consonant, else literal)."""
    if len(toks) != len(template):
        return None
    caps = []
    for t, pat in zip(toks, template):
        if pat == 'C':
            if not _is_cons(t):
                return None
            caps.append(t)
        elif t != pat:
            return None
    return caps

def _radicals3(root):
    r = [x for x in str(root).split('.') if x]
    return r if len(r) == 3 else None

def conjugate_III(root, past3ms, pres3ms):
    r = _radicals3(root)
    if not r: return None
    p = _match(_phon(str(past3ms)), ['C', 'aa', 'C', 'a', 'C'])
    im = _match(_phon(str(pres3ms)), ['y', 'C', 'aa', 'C', 'i', 'C'])
    if not p or not im or p != im: return None
    c1, c2, c3 = p
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    return _derived(J_(c1,'aa',c2,'a',c3), J_(r1,'ا',r2,r3), False,
                    J_(c1,'aa',c2,'i',c3), J_(r1,'ا',r2,r3), 'bare', True, 'hollow',
                    J_(c1,'aa',c2,'i',c3))

def conjugate_V(root, past3ms, pres3ms):
    # The imperfect (yit-CaCCaC) is the reliable anchor; the perfect may carry the
    # prosthetic i- (book it3allam) or not (Maknuune tsallam) — we preserve whichever.
    r = _radicals3(root)
    if not r: return None
    im = _match(_phon(str(pres3ms)), ['y','i','t','C','a','C','C','a','C'])
    if not im or im[1] != im[2]: return None
    c1, c2, _, c3 = im
    g, p = _deglottal(past3ms)                       # data may write 2itkabbar
    pre = p[:1] == ['i']
    pc = _match(p, (['i'] if pre else []) + ['t','C','a','C','C','a','C'])
    if not pc or pc[1] != pc[2] or [pc[0], pc[1], pc[3]] != [c1, c2, c3]: return None
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    perf_ph = ('it' if pre else 't') + J_(c1,'a',c2,c2,'a',c3)
    perf_ar = ('ا' if pre else '') + J_('ت',r1,r2,r3)
    return _derived(perf_ph, perf_ar, False,
                    J_('t',c1,'a',c2,c2,'a',c3), J_('ت',r1,r2,r3), 'i', False, 'sound',
                    J_('it',c1,'a',c2,c2,'i',c3), glottal=g)

def conjugate_VI(root, past3ms, pres3ms):
    r = _radicals3(root)
    if not r: return None
    im = _match(_phon(str(pres3ms)), ['y','i','t','C','aa','C','a','C'])
    if not im: return None
    c1, c2, c3 = im
    g, p = _deglottal(past3ms)
    pre = p[:1] == ['i']
    pc = _match(p, (['i'] if pre else []) + ['t','C','aa','C','a','C'])
    if not pc or [pc[0], pc[1], pc[2]] != [c1, c2, c3]: return None
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    perf_ph = ('it' if pre else 't') + J_(c1,'aa',c2,'a',c3)
    perf_ar = ('ا' if pre else '') + J_('ت',r1,'ا',r2,r3)
    return _derived(perf_ph, perf_ar, False,
                    J_('t',c1,'aa',c2,'a',c3), J_('ت',r1,'ا',r2,r3), 'i', False, 'sound',
                    J_('it',c1,'aa',c2,'i',c3), glottal=g)

# Maknuune writes the hamzat-wasl of the perfect with a glottal onset (2irtakab); the book
# drops it (irtakab). Strip it for matching, remember it, and hand it to _derived so the
# output pronunciation matches whichever citation form the input used.
def _deglottal(past3ms):
    p = _phon(str(past3ms))
    return ('2', p[1:]) if p[:1] == ['2'] else ('', p)

def conjugate_II_defective(root, past3ms, pres3ms):
    """Form II with a final weak radical (غنّى/يغنّي, سوّى, بنّى): doubled middle + defective
    final. C1aC2C2a perfect / yC1aC2C2i imperfect; -ee- suffixes, m- participle, ي glide."""
    r = _radicals3(root)
    if not r: return None
    p = _match(_phon(str(past3ms)), ['C','a','C','C','a'])
    im = _match(_phon(str(pres3ms)), ['y','C','a','C','C','i'])
    if not p or not im or p[1] != p[2] or im[1] != im[2] or [p[0], p[1]] != [im[0], im[1]]:
        return None
    c1, c2 = p[0], p[1]
    r1, r2 = _ar_letter(c1, r[0]), _ar_letter(c2, r[1])
    J = J_
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}
    put('perf', 'huwwe', J(c1,'a',c2,c2,'a'),  J(r1,r2,'ى'))         # ghanna / غنى
    put('perf', 'hiyye', J(c1,'a',c2,c2,'at'), J(r1,r2,'ت'))
    put('perf', 'humme', J(c1,'a',c2,c2,'u'),  J(r1,r2,'وا'))
    for per, ps, ars in [('ana','t','ت'), ('inta','t','ت'), ('inti','ti','تي'),
                         ('i7na','na','نا'), ('intu','tu','تو')]:
        put('perf', per, J(c1,'a',c2,c2,'ee',ps), J(r1,r2,'ي',ars))  # ghanneet / غنيت
    stem, stem_ar = J(c1,'a',c2,c2), J(r1,r2)                        # ghann / غن
    pf = {'ana':'a', 'i7na':'n', 'inta':'t', 'inti':'t', 'intu':'t', 'huwwe':'y', 'hiyye':'t', 'humme':'y'}
    va = {'intu': ('u','وا'), 'humme': ('u','وا')}
    for per in PERSONS:
        sp, sa = va.get(per, ('i', 'ي'))
        put('impf', per, pf[per] + stem + sp, _APFX[per] + stem_ar + sa)
    for per in PERSONS:                                             # bi-imperfect (hollow rule)
        im2 = cells['impf|' + per]
        if per == 'ana':
            ph, ar = 'b' + im2['ph'], 'ب' + im2['ar'][1:]
        elif per in ('huwwe', 'humme'):
            ph, ar = 'bi' + im2['ph'][1:], 'ب' + im2['ar']
        else:
            ph, ar = 'bi' + im2['ph'], 'ب' + im2['ar']
        put('bimpf', per, ph, ar)
    put('imp', 'inta', J(c1,'a',c2,c2,'i'), J(r1,r2,'ي'))
    put('imp', 'inti', J(c1,'a',c2,c2,'i'), J(r1,r2,'ي'))
    put('imp', 'intu', J(c1,'a',c2,c2,'u'), J(r1,r2,'وا'))
    put('ap', 'm', J('m',c1,'a',c2,c2,'i'),   J('م',r1,r2,'ي'))     # mghanni / مغني
    put('ap', 'f', J('m',c1,'a',c2,c2,'ya'),  J('م',r1,r2,'ية'))
    put('ap', 'p', J('m',c1,'a',c2,c2,'yiin'), J('م',r1,r2,'يين'))
    return cells

def conjugate_IV(root, past3ms, pres3ms):
    """Form IV (2af3al, causative): 2a-C1C2aC3 perfect, yi-C1C2iC3 imperfect (1sg keeps the
    hamza — 2a3lin), no syncope, mi- participle. Sound roots only (weak IV → principal parts)."""
    r = _radicals3(root)
    if not r: return None
    p = _match(_phon(str(past3ms)), ['2','a','C','C','a','C'])
    im = _match(_phon(str(pres3ms)), ['y','i','C','C','i','C'])
    if not p or not im or p != im: return None
    c1, c2, c3 = p
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    J = J_
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}
    perf, perf_ar = J('2a', c1, c2, 'a', c3), J('أ', r1, r2, r3)          # 2a3lan / أعلن
    for per, ps, as_ in _PERF_SUF:
        put('perf', per, perf + ps, perf_ar + as_)
    stem, stem_ar = J(c1, c2, 'i', c3), J(r1, r2, r3)                     # 3lin / علن
    pf = {'ana':'2a', 'i7na':'ni', 'inta':'ti', 'inti':'ti', 'intu':'ti', 'huwwe':'yi', 'hiyye':'ti', 'humme':'yi'}
    va = {'inti':('i','ي'), 'intu':('u','وا'), 'humme':('u','وا')}
    for per in PERSONS:
        sp, sa = va.get(per, ('', ''))
        put('impf', per, pf[per] + stem + sp, _APFX[per] + stem_ar + sa)
    for per in PERSONS:                                                  # bi-imperfect (sound rule)
        im2 = cells['impf|' + per]
        if per == 'ana':                                                # ba3lin (glottal drops)
            ph, ar = 'b' + im2['ph'][1:], 'ب' + im2['ar'][1:]
        elif per in ('huwwe', 'humme'):
            ph, ar = 'b' + im2['ph'][1:], 'ب' + im2['ar'][1:]
        else:
            ph, ar = 'b' + im2['ph'], 'ب' + im2['ar']
        put('bimpf', per, ph, ar)
    put('imp', 'inta', J('i', stem),       J('ا', stem_ar))             # i3lin / اعلن
    put('imp', 'inti', J('i', stem, 'i'),  J('ا', stem_ar, 'ي'))
    put('imp', 'intu', J('i', stem, 'u'),  J('ا', stem_ar, 'وا'))
    put('ap', 'm', J('mi', stem),          J('م', stem_ar))             # mi3lin / معلن (no syncope)
    put('ap', 'f', J('mi', stem, 'a'),     J('م', stem_ar, 'ة'))
    put('ap', 'p', J('mi', stem, 'iin'),   J('م', stem_ar, 'ين'))
    return cells

def conjugate_VII(root, past3ms, pres3ms):
    r = _radicals3(root)
    if not r: return None
    g, pp = _deglottal(past3ms)
    p = _match(pp, ['i','n','C','a','C','a','C'])
    im = _match(_phon(str(pres3ms)), ['y','i','n','C','i','C','i','C'])
    if not p or not im or p != im: return None
    c1, c2, c3 = p
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    return _derived(J_('in',c1,'a',c2,'a',c3), J_('ا','ن',r1,r2,r3), True,
                    J_('n',c1,'i',c2,'i',c3), J_('ن',r1,r2,r3), 'i', True, 'sound',
                    J_('in',c1,'i',c2,'i',c3), glottal=g)

def conjugate_VIII(root, past3ms, pres3ms):
    r = _radicals3(root)
    if not r: return None
    g, pp = _deglottal(past3ms)
    p = _match(pp, ['i','C','t','a','C','a','C'])
    # Maknuune sometimes records the imperfect with an a-stem (yishtaghil) where the book
    # conjugates the i-stem (yishtighil) — both are real speech. Accept either on input;
    # generation stays the book-verified i-stem.
    im = (_match(_phon(str(pres3ms)), ['y','i','C','t','i','C','i','C'])
          or _match(_phon(str(pres3ms)), ['y','i','C','t','a','C','i','C']))
    if not p or not im or p != im: return None
    c1, c2, c3 = p
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    return _derived(J_('i',c1,'ta',c2,'a',c3), J_('ا',r1,'ت',r2,r3), True,
                    J_(c1,'ti',c2,'i',c3), J_(r1,'ت',r2,r3), 'i', True, 'sound',
                    J_('i',c1,'ti',c2,'i',c3), glottal=g)

def conjugate_X(root, past3ms, pres3ms):
    r = _radicals3(root)
    if not r: return None
    g, pp = _deglottal(past3ms)
    p = _match(pp, ['i','s','t','a','C','C','a','C'])
    im = _match(_phon(str(pres3ms)), ['y','i','s','t','a','C','C','i','C'])
    if not p or not im or p != im: return None
    c1, c2, c3 = p
    r1, r2, r3 = (_ar_letter(c1, r[0]), _ar_letter(c2, r[1]), _ar_letter(c3, r[2]))
    return _derived(J_('ista',c1,c2,'a',c3), J_('ا','س','ت',r1,r2,r3), False,
                    J_('sta',c1,c2,'i',c3), J_('س','ت',r1,r2,r3), 'i', False, 'sound',
                    J_('ista',c1,c2,'i',c3), part_syn=False, glottal=g)


# ---- assimilated Form I (w-initial: وصل wiSil/yuuSal, وقف wi2if/yuu2af) ----------------
# The perfect behaves like a sound i-stem; in the imperfect the w vocalizes to uu for every
# person EXCEPT ana, which keeps it as a consonant (awS.al / bawS.al). Verified against the
# book's w-initial 'sound measure I' tables (to arrive), which the sound spec deliberately
# skips.
def conjugate_assimilated(root, past3ms, pres3ms):
    rl = [x for x in str(root).split('.') if x]
    if len(rl) != 3:
        return None
    p = _phon(str(past3ms))
    if len(p) != 5 or p[0] != 'w' or _is_cons(p[1]) or _is_cons(p[3]):
        return None
    c1, pv, c2, pv2, c3 = p
    if pv != pv2 or pv in ('aa', 'ii', 'uu', 'ee', 'oo'):
        return None
    im = _phon(str(pres3ms))                        # y uu C V C
    if (len(im) != 5 or im[0] != 'y' or im[1] != 'uu'
            or not (_is_cons(im[2]) and _is_cons(im[4])) or _is_cons(im[3])
            or [im[2], im[4]] != [c2, c3]):
        return None
    iv = im[3]
    r1, r2, r3 = rl
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    # PERFECT — sound-engine rules (i-stem drops the first vowel before consonant suffixes)
    cs = (lambda s: J(c1, pv, c2, pv, c3, s)) if pv == 'a' else (lambda s: J(c1, c2, pv, c3, s))
    ars = lambda s: J(r1, r2, r3, s)
    put('perf', 'huwwe', J(c1, pv, c2, pv, c3), J(r1, r2, r3))
    put('perf', 'hiyye', J(c1, pv, c2, c3, 'at'), ars('ت'))
    put('perf', 'humme', J(c1, pv, c2, pv, c3, 'u') if pv == 'a' else J(c1, pv, c2, c3, 'u'), ars('وا'))
    put('perf', 'ana',  cs('it'), ars('ت'))
    put('perf', 'inta', cs('it'), ars('ت'))
    put('perf', 'inti', cs('ti'), ars('تي'))
    put('perf', 'i7na', cs('na'), ars('نا'))
    put('perf', 'intu', cs('tu'), ars('تو'))

    # IMPERFECT — ana keeps the w (awS.al); everyone else vocalizes it (nuuS.al, yuuS.al).
    # Vowel suffixes attach WITHOUT syncope (tuuS.ali, yuuS.alu — the long stem carries them).
    stem_uu = J('uu', c2, iv, c3)
    put('impf', 'ana',   J('a', c1, c2, iv, c3), J('أ', r1, r2, r3))
    for per, pfx in (('i7na','n'), ('inta','t'), ('hiyye','t'), ('huwwe','y')):
        put('impf', per, pfx + stem_uu, J(_PFX_AR[per], r1, r2, r3))
    put('impf', 'inti',  't' + stem_uu + 'i', J('ت', r1, r2, r3, 'ي'))
    put('impf', 'intu',  't' + stem_uu + 'u', J('ت', r1, r2, r3, 'وا'))
    put('impf', 'humme', 'y' + stem_uu + 'u', J('ي', r1, r2, r3, 'وا'))

    # BI-IMPERFECT — the generic rule (b+y -> b; ana keeps its a)
    for per in PERSONS:
        imf = cells['impf|' + per]
        ph = 'b' + imf['ph'][1:] if imf['ph'][0] == 'y' else 'b' + imf['ph']
        ar = 'ب' + (imf['ar'][1:] if per == 'ana' else imf['ar'])
        put('bimpf', per, ph, ar)

    # IMPERATIVE — follows the imperfect stem vowel: a-imperfects vocalize the w
    # (uuS.al! أوصل), i-imperfects keep it as a consonant (iw3id! اوعد).
    if iv == 'a':
        imp, impar = stem_uu, J('أ', r1, r2, r3)
    else:
        imp, impar = J('i', c1, c2, iv, c3), J('ا', r1, r2, r3)
    put('imp', 'inta', imp,       impar)
    put('imp', 'inti', imp + 'i', impar + 'ي')
    put('imp', 'intu', imp + 'u', impar + 'وا')

    # ACTIVE PARTICIPLE — regular faa3il with w as a plain consonant (waaS.il)
    put('ap', 'm', J(c1, 'aa', c2, 'i', c3), J(r1, 'ا', r2, r3))
    put('ap', 'f', J(c1, 'aa', c2, c3, 'a'), J(r1, 'ا', r2, r3, 'ة'))
    put('ap', 'p', J(c1, 'aa', c2, c3, 'iin'), J(r1, 'ا', r2, r3, 'ين'))
    return cells


# ---- irregular Form I: أكل / أخذ (2aCaC / yaaCuC) ------------------------------------
# The twins every learner meets in week one. Long-vowel imperfect (yaakul), suppletive
# short imperative (kul!, khud!), and an m- participle (maakil) — all against the book's
# two 'irregular measure I' tables.
def conjugate_hamzated_akal(root, past3ms, pres3ms):
    rl = [x for x in str(root).split('.') if x]
    if len(rl) != 3:
        return None
    p = _match(_phon(str(past3ms)), ['2', 'a', 'C', 'a', 'C'])
    im = _match(_phon(str(pres3ms)), ['y', 'aa', 'C', 'u', 'C'])
    if not p or not im or p != im:
        return None
    c2, c3 = p
    ar2 = _ar_letter(c2, rl[1]); ar3 = _ar_letter(c3, rl[2])
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    # PERFECT — a-stem sound behaviour on a 2aCaC base (2akalit, 2akhadti, 2aklat)
    ars = lambda s: J('أ', ar2, ar3, s)
    put('perf', 'huwwe', J('2a', c2, 'a', c3), J('أ', ar2, ar3))
    put('perf', 'hiyye', J('2a', c2, c3, 'at'), ars('ت'))
    put('perf', 'humme', J('2a', c2, 'a', c3, 'u'), ars('وا'))
    for per, s in (('ana','it'), ('inta','it'), ('inti','ti'), ('i7na','na'), ('intu','tu')):
        put('perf', per, J('2a', c2, 'a', c3, s), ars({'it':'ت','ti':'تي','na':'نا','tu':'تو'}[s]))

    # IMPERFECT — long aa stem; the u drops before vowel suffixes (taakli, yaaklu)
    put('impf', 'ana',   J('2aa', c2, 'u', c3), J('آ', ar2, ar3))
    for per, pfx in (('i7na','n'), ('inta','t'), ('hiyye','t'), ('huwwe','y')):
        put('impf', per, J(pfx, 'aa', c2, 'u', c3), J(_PFX_AR[per], 'ا', ar2, ar3))
    put('impf', 'inti',  J('taa', c2, c3, 'i'), J('ت', 'ا', ar2, ar3, 'ي'))
    put('impf', 'intu',  J('taa', c2, c3, 'u'), J('ت', 'ا', ar2, ar3, 'وا'))
    put('impf', 'humme', J('yaa', c2, c3, 'u'), J('ي', 'ا', ar2, ar3, 'وا'))

    # BI-IMPERFECT — b sits on the long vowel; 3rd persons KEEP the y (byaakul, byaaklu)
    put('bimpf', 'ana',   J('baa', c2, 'u', c3), J('ب', 'ا', ar2, ar3))
    put('bimpf', 'i7na',  J('bnaa', c2, 'u', c3), J('بن', 'ا', ar2, ar3))
    for per in ('inta', 'hiyye'):
        put('bimpf', per, J('btaa', c2, 'u', c3), J('بت', 'ا', ar2, ar3))
    put('bimpf', 'inti',  J('btaa', c2, c3, 'i'), J('بت', 'ا', ar2, ar3, 'ي'))
    put('bimpf', 'intu',  J('btaa', c2, c3, 'u'), J('بت', 'ا', ar2, ar3, 'وا'))
    put('bimpf', 'huwwe', J('byaa', c2, 'u', c3), J('بي', 'ا', ar2, ar3))
    put('bimpf', 'humme', J('byaa', c2, c3, 'u'), J('بي', 'ا', ar2, ar3, 'وا'))

    # IMPERATIVE — the famous short forms: kul / kuli / kulu, khud / khudi / khudu
    put('imp', 'inta', J(c2, 'u', c3),       J(ar2, ar3))
    put('imp', 'inti', J(c2, 'u', c3, 'i'),  J(ar2, ar3, 'ي'))
    put('imp', 'intu', J(c2, 'u', c3, 'u'),  J(ar2, ar3, 'وا'))

    # ACTIVE PARTICIPLE — m-initial, unlike regular Form I: maakil / maakla / maakliin
    put('ap', 'm', J('maa', c2, 'i', c3), J('م', 'ا', ar2, ar3))
    put('ap', 'f', J('maa', c2, c3, 'a'), J('م', 'ا', ar2, ar3, 'ة'))
    put('ap', 'p', J('maa', c2, c3, 'iin'), J('م', 'ا', ar2, ar3, 'ين'))
    return cells


# ---- defective Form VIII (اشترى ishtara / yishtiri) ----------------------------------
def conjugate_VIII_defective(root, past3ms, pres3ms):
    rl = _radicals3(root)
    if not rl:
        return None
    g, pp = _deglottal(past3ms)
    p = _match(pp, ['i', 'C', 't', 'a', 'C', 'a'])
    im = _match(_phon(str(pres3ms)), ['y', 'i', 'C', 't', 'i', 'C', 'i'])
    if not p or not im or p != im:
        return None
    c1, c2 = p
    a1 = _ar_letter(c1, rl[0]); a2 = _ar_letter(c2, rl[1])
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    base = J('i', c1, 'ta', c2)                     # ishtara-
    arb = J('ا', a1, 'ت', a2)
    put('perf', 'huwwe', base + 'a', arb + 'ى')
    put('perf', 'hiyye', base + 'at', arb + 'ت')
    put('perf', 'humme', base + 'u', arb + 'وا')
    for per, s, a in (('ana','eet','يت'), ('inta','eet','يت'), ('inti','eeti','يتي'),
                      ('i7na','eena','ينا'), ('intu','eetu','يتو')):
        put('perf', per, base + s, arb + a)

    stem = J(c1, 'ti', c2)                          # -shtiri-
    put('impf', 'ana', J('a', stem, 'i'), J('أ', a1, 'ت', a2, 'ي'))
    for per, pfx, arp in (('i7na','ni','ن'), ('inta','ti','ت'), ('hiyye','ti','ت'), ('huwwe','yi','ي')):
        put('impf', per, J(pfx, stem, 'i'), J(arp, a1, 'ت', a2, 'ي'))
    put('impf', 'inti', J('ti', stem, 'i'), J('ت', a1, 'ت', a2, 'ي'))       # f = m for -i finals
    put('impf', 'intu', J('ti', stem, 'u'), J('ت', a1, 'ت', a2, 'وا'))
    put('impf', 'humme', J('yi', stem, 'u'), J('ي', a1, 'ت', a2, 'وا'))

    for per in PERSONS:
        imf = cells['impf|' + per]
        ph = 'b' + imf['ph'][1:] if imf['ph'][0] == 'y' else 'b' + imf['ph']
        ar = 'ب' + (imf['ar'][1:] if per == 'ana' else imf['ar'])
        put('bimpf', per, ph, ar)

    put('imp', 'inta', J('i', stem, 'i'), J('ا', a1, 'ت', a2, 'ي'))
    put('imp', 'inti', J('i', stem, 'i'), J('ا', a1, 'ت', a2, 'ي'))
    put('imp', 'intu', J('i', stem, 'u'), J('ا', a1, 'ت', a2, 'وا'))

    put('ap', 'm', J('mi', stem, 'i'), J('م', a1, 'ت', a2, 'ي'))
    put('ap', 'f', J('mi', stem, 'ya'), J('م', a1, 'ت', a2, 'ية'))
    put('ap', 'p', J('mi', stem, 'yiin'), J('م', a1, 'ت', a2, 'يين'))
    return cells


# ---- irregular Form X (استنى istanna / yistanna — geminate + defective) ---------------
def conjugate_X_gemdef(root, past3ms, pres3ms):
    rl = [x for x in str(root).split('.') if x]
    g, pp = _deglottal(past3ms)
    p = _match(pp, ['i', 's', 't', 'a', 'C', 'C', 'a'])
    im = _match(_phon(str(pres3ms)), ['y', 'i', 's', 't', 'a', 'C', 'C', 'a'])
    if not p or not im or p != im or p[0] != p[1]:
        return None
    c = p[0]
    ac = _ar_letter(c, rl[1] if len(rl) == 3 else 'ن')
    J = lambda *x: ''.join(x)
    cells = {}
    def put(sec, per, ph, ar): cells[sec + '|' + per] = {'ph': ph, 'ar': ar}

    base = J('ista', c, c)                          # istann-
    arb = J('است', ac)                              # geminate shown single, as written
    put('perf', 'huwwe', base + 'a', arb + 'ى')
    put('perf', 'hiyye', base + 'at', arb + 'ت')
    put('perf', 'humme', base + 'u', arb + 'وا')
    for per, s, a in (('ana','eet','يت'), ('inta','eet','يت'), ('inti','eeti','يتي'),
                      ('i7na','eena','ينا'), ('intu','eetu','يتو')):
        put('perf', per, base + s, arb + a)

    stem = J('sta', c, c)
    put('impf', 'ana', J('a', stem, 'a'), J('أ', 'ست', ac, 'ى'))
    for per, pfx, arp in (('i7na','ni','ن'), ('inta','ti','ت'), ('hiyye','ti','ت'), ('huwwe','yi','ي')):
        put('impf', per, J(pfx, stem, 'a'), J(arp, 'ست', ac, 'ى'))
    put('impf', 'inti', J('ti', stem, 'i'), J('ت', 'ست', ac, 'ي'))
    put('impf', 'intu', J('ti', stem, 'u'), J('ت', 'ست', ac, 'وا'))
    put('impf', 'humme', J('yi', stem, 'u'), J('ي', 'ست', ac, 'وا'))

    for per in PERSONS:
        imf = cells['impf|' + per]
        ph = 'b' + imf['ph'][1:] if imf['ph'][0] == 'y' else 'b' + imf['ph']
        ar = 'ب' + (imf['ar'][1:] if per == 'ana' else imf['ar'])
        put('bimpf', per, ph, ar)

    put('imp', 'inta', J('i', stem, 'a'), arb + 'ى')
    put('imp', 'inti', J('i', stem, 'i'), arb + 'ي')
    put('imp', 'intu', J('i', stem, 'u'), arb + 'وا')

    put('ap', 'm', J('mi', stem, 'i'), J('م', 'ست', ac, 'ي'))
    put('ap', 'f', J('mi', stem, 'ya'), J('م', 'ست', ac, 'ية'))
    put('ap', 'p', J('mi', stem, 'iin'), J('م', 'ست', ac, 'يين'))
    return cells


# ---- the fully irregular إجا "to come" ------------------------------------------------
# Maknuune has no VERB entry for it, and no rule generates it: only the 3rd-person perfects
# begin with a-, and the imperative (ta3aal) is a different word entirely. This table is
# taken from the reference's 'irregular defective measure I' page — the same book every
# engine above is verified against — and is checked against it cell-for-cell in
# verify_conjugation.py. Looked up, not invented.
def conjugate_ija():
    T = {
      'perf': {'ana': ('jiit','جيت'), 'inta': ('jiit','جيت'), 'inti': ('jiiti','جيتي'),
               'huwwe': ('aja','أجا'), 'hiyye': ('ajat','أجت'), 'i7na': ('jiina','جينا'),
               'intu': ('jiitu','جيتو'), 'humme': ('aju','أجوا')},
      'impf': {'ana': ('aaji','آجي'), 'inta': ('tiiji','تيجي'), 'inti': ('tiiji','تيجي'),
               'huwwe': ('yiiji','ييجي'), 'hiyye': ('tiiji','تيجي'), 'i7na': ('niiji','نيجي'),
               'intu': ('tiiju','تيجوا'), 'humme': ('yiiju','ييجوا')},
      'bimpf': {'ana': ('baaji','باجي'), 'inta': ('btiiji','بتيجي'), 'inti': ('btiiji','بتيجي'),
                'huwwe': ('biiji','بيجي'), 'hiyye': ('btiiji','بتيجي'), 'i7na': ('bniiji','بنيجي'),
                'intu': ('btiiju','بتيجوا'), 'humme': ('biiju','بيجوا')},
      'imp': {'inta': ('ta3aal','تعال'), 'inti': ('ta3aali','تعالي'), 'intu': ('ta3aalu','تعالوا')},
      'ap': {'m': ('jaay','جاي'), 'f': ('jaaya','جاية'), 'p': ('jaayiin','جايين')},
    }
    return {sec + '|' + k: {'ph': ph, 'ar': ar} for sec, m in T.items() for k, (ph, ar) in m.items()}


if __name__ == '__main__':
    import json
    for root, p, i in [('ك.ت.ب','katab','yiktub'), ('ح.ر.ك','7arrak','y7arrik'),
                       ('ح.و.ل','7aawal','y7aawil'), ('ع.ل.م','it3allam','yit3allam'),
                       ('ع.م.ل','it3aamal','yit3aamal'), ('ب.س.ط','inbasaT.','yinbisiT.'),
                       ('ح.ف.ل','i7tafal','yi7tifil'), ('ع.م.ل','ista3mal','yista3mil')]:
        c = (conjugate(root, p, i) or conjugate_hollow(root, p, i) or conjugate_defective(root, p, i)
             or conjugate_geminate(root, p, i) or conjugate_II(root, p, i) or conjugate_III(root, p, i)
             or conjugate_V(root, p, i) or conjugate_VI(root, p, i) or conjugate_VII(root, p, i)
             or conjugate_VIII(root, p, i) or conjugate_X(root, p, i))
        print('\n==', root, p, '/', i, '==')
        for sec in ('perf','impf','bimpf','imp','ap'):
            row = [(k.split('|')[1], v['ph'], v['ar']) for k, v in c.items() if k.startswith(sec+'|')]
            print(' ', sec)
            for per, ph, ar in row:
                print('    %-7s %-10s %s' % (per, ph, ar))
