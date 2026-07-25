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


if __name__ == '__main__':
    import json
    for root, p, i in [('ك.ت.ب','katab','yiktub'), ('ش.ر.ب','shirib','yishrab'),
                       ('ط.ل.ع','t.ili3','yit.la3'), ('س.ك.ن','sakan','yuskun'),
                       ('ر.و.ح','raa7','yruu7'), ('ب.ي.ع','baa3','ybii3'), ('ن.و.م','naam','ynaam'),
                       ('م.ش.ي','mishi','yimshi'), ('ن.س.ي','nisi','yinsa'), ('ب.ك.ي','baka','yibki'),
                       ('ح.ب.ب','7abb','y7ibb'), ('ح.ط.ط','7aT.T.','y7uT.T.'), ('ر.د.د','radd','yrudd')]:
        c = (conjugate(root, p, i) or conjugate_hollow(root, p, i)
             or conjugate_defective(root, p, i) or conjugate_geminate(root, p, i))
        print('\n==', root, p, '/', i, '==')
        for sec in ('perf','impf','bimpf','imp','ap'):
            row = [(k.split('|')[1], v['ph'], v['ar']) for k, v in c.items() if k.startswith(sec+'|')]
            print(' ', sec)
            for per, ph, ar in row:
                print('    %-7s %-10s %s' % (per, ph, ar))
