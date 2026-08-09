"""Vocalize the SURFACE form using the lexicon's citation form. (SPEC 7.4.6)

The gap: Maknuune stores citation forms (يُقْعُد "he sits"); running text has conjugated
ones (بقعد "I sit"). We cannot print the citation form over the text — it's a different
word. But the two SHARE their stem consonants, and the lexicon already knows how that
stem is vowelled. So we align on the shared stem, transfer its diacritics, and vowel the
affixes by rule.

Three confidence tiers, kept distinct because they carry different risk:

  lexicon:exact     surface == citation form. Maknuune's own vocalization, untouched.
                    Zero inference. ~46% of running text.
  derived:affix     ال / بال / عال / و + stem, or stem + ي. The stem keeps the lexicon's
                    vowels; the affix is vowelled by uncontroversial rules (incl. sun-letter
                    assimilation). Low risk.
  derived:verb      b-imperfect. The stem comes from the lexicon, but the PREFIX VOWEL is a
                    genuine dialectal judgment we are making. Flagged for native review.

Anything that doesn't align cleanly stays unvocalized and says so. Never invent vowels.
"""
import re

HARAKAT = re.compile(r'[ً-ْٰ]')
SUN = set('تثدذرزسشصضطظلن')

FATHA, DAMMA, KASRA, SUKUN, SHADDA = 'َ', 'ُ', 'ِ', 'ْ', 'ّ'

def strip(s):
    return HARAKAT.sub('', str(s)).replace('ـ', '')

def split(s):
    """[(base_char, diacritics)] — diacritics attach to the preceding base char."""
    out = []
    for ch in str(s):
        if HARAKAT.match(ch) or ch == SHADDA:
            if out: out[-1][1] += ch
        else:
            out.append([ch, ''])
    return [(c, d) for c, d in out]

def join(pairs):
    return ''.join(c + d for c, d in pairs)

def _norm_align(c):
    """Letters that vary orthographically but are the same consonant for alignment."""
    return {'أ':'ا','إ':'ا','آ':'ا','ى':'ي','ة':'ه','ؤ':'ء','ئ':'ء'}.get(c, c)

def _stem_match(surf_bare, form_pairs):
    """Locate the citation stem inside the surface word. Returns (start, end) or None."""
    form_bare = ''.join(_norm_align(c) for c, _ in form_pairs)
    s = ''.join(_norm_align(c) for c in surf_bare)
    if not form_bare: return None
    i = s.find(form_bare)
    if i >= 0: return (i, i + len(form_bare), False)
    # Allow the citation form to lose its own prefix (يِعْمَل -> عمل inside وبعمل)
    for drop in (1, 2):
        if len(form_bare) > drop + 1:
            sub = form_bare[drop:]
            i = s.find(sub)
            if i >= 0: return (i, i + len(sub), False)
    # Weak-final verbs: ى/ا/ي are the same radical and alternate freely by person
    # (يِمْلِي "he fills" vs بتملا "she fills"). Match on the stem minus its final
    # weak letter; the caller re-attaches the surface's own final letter.
    for drop in (0, 1, 2):
        body = form_bare[drop:]
        if len(body) > 2 and body[-1] in 'ايو':
            i = s.find(body[:-1])
            if i >= 0 and len(s) > i + len(body) - 1 and s[i + len(body) - 1] in 'ايو':
                return (i, i + len(body), True)
    return None

def vocalize(surface, form, analysis=None, subject=None):
    """-> (vocalized_or_None, provenance)

    `subject` disambiguates the b-imperfect, which is genuinely ambiguous in writing:
    بشتغل is بَشتِغِل "I work" and بِشتِغِل "he works". Pass '1sg' or '3' when the sentence
    makes it clear; pass nothing and an ambiguous word stays unvocalized rather than guess.
    """
    if not form: return None, 'unvocalized:no-entry'
    surf_bare = strip(surface)
    form_pairs = split(form)

    if surf_bare == strip(form):
        return form, 'lexicon:exact'

    span = _stem_match(surf_bare, form_pairs)
    if not span:
        return None, 'unvocalized:no-alignment'
    start, end, weak_final = span

    # Diacritics for the matched stem come straight from the lexicon.
    offset = len(form_pairs) - (end - start)
    # When the citation form's own imperfect prefix was dropped (يُسْكُن -> سكن), keep the
    # vowel that sat on it: بت/بن/بي need it, or they end up with two sukuuns in a row.
    pfx_vowel = ''
    if offset > 0 and form_pairs[offset - 1][0] in 'يتنأا':
        pfx_vowel = ''.join(ch for ch in form_pairs[offset - 1][1] if ch in (FATHA, KASRA, DAMMA))
    # Keep the SURFACE letter, take the LEXICON's diacritics. Where a weak final letter
    # differs (ى vs ا), the surface spelling is what the reader sees and must win.
    stem = []
    for k in range(end - start):
        fi = offset + k
        sc = surf_bare[start + k]
        dia = form_pairs[fi][1] if 0 <= fi < len(form_pairs) else ''
        # A weak final letter that differs (ي -> ا) must NOT inherit the other's vowel:
        # يِمْلِي ends -lī, بتملا ends -la. Carrying the kasra over would print مْلِا.
        if 0 <= fi < len(form_pairs) and _norm_align(form_pairs[fi][0]) != _norm_align(sc):
            dia = ''
        stem.append((sc, dia))

    if weak_final and str(analysis or '').startswith('VERB'):
        return None, 'unvocalized:weak-final-verb'

    prefix, suffix = surf_bare[:start], surf_bare[end:]
    out, prov = [], None

    if prefix:
        p = prefix
        lead = []
        if p.startswith('و'): lead.append(('و', '')); p = p[1:]
        if p in ('ال', 'بال', 'عال', 'فال', 'كال', 'لل'):
            if len(p) > 2: lead.append((p[0], FATHA if p[0] in 'عف' else KASRA))
            lead += [('ا', ''), ('ل', '')]
            if stem and stem[0][0] in SUN:                     # sun-letter assimilation
                stem[0] = (stem[0][0], SHADDA + stem[0][1].replace(SUKUN, ''))
            prov = 'derived:affix'
        elif p in ('ب', 'بت', 'بن', 'بي') and str(analysis or '').startswith('VERB'):
            # b-imperfect. The STEM is the lexicon's; the PREFIX VOWEL is our judgment.
            # NB the VERB guard above: بـ is also the preposition "in/with", and without the
            # guard every بسبب / بمدينة / بطريقة was being handed a verb prefix vowel.
            third = bool(stem) and stem[0][0] == 'ي'
            if p == 'ب':
                # Genuinely ambiguous in writing: بشتغل is both بَشتِغِل "I work" and
                # بِشتِغِل "he works". Only the subject decides, so ask the caller — and if
                # the caller can't say, refuse rather than teach the wrong person.
                if third:                          person = KASRA
                elif subject == '1sg':             person = FATHA
                elif subject == '3':               person = KASRA
                else: return None, 'unvocalized:ambiguous-person'
                lead.append(('ب', person))
            else:
                # بت / بن / بي. The affix consonant takes the imperfect's OWN prefix vowel,
                # which the citation form carries (يُسْكُن -> بِتُسْكُن). Blindly writing a
                # sukuun there produced بِتْسْكُن — three consonants in a row, unsayable.
                lead.append(('ب', KASRA))
                for extra in p[1:]: lead.append((extra, pfx_vowel or SUKUN))
            prov = 'derived:verb'
        elif p in ('ع', 'ل', 'ب', 'ف', 'ك'):
            lead.append((p, FATHA if p in 'عف' else KASRA)); prov = 'derived:affix'
        else:
            return None, 'unvocalized:unknown-prefix'
        out += lead
    out += stem
    if suffix:
        if suffix in ('ي', 'ك', 'ها', 'هم', 'نا', 'و'):
            out += [(c, '') for c in suffix]
            prov = prov or 'derived:affix'
        else:
            return None, 'unvocalized:unknown-suffix'
    return join(out), (prov or 'derived:affix')

if __name__ == '__main__':
    tests = [("الصبح","صُبِح"),("بقعد","يُقْعُد"),("وبشرب","يِشْرَب"),("فنجاني","فِنْجَان"),
             ("بالنهار","نْهَار"),("عالبلكونة","بَلْكَونِة"),("قهوة","قَهْوِة"),("بتملا","يِمْلِي")]
    print("%-12s %-12s %-14s %s" % ("SURFACE","LEXICON","VOCALIZED","PROVENANCE"))
    print("-"*62)
    for s, f in tests:
        v, p = vocalize(s, f)
        print("%-12s %-12s %-14s %s" % (s, f, v or "—", p))
