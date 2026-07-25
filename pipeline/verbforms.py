"""Classify a Palestinian verb into its Arabic Form (measure I–X) + weak class.

Computed from the perfect stem pattern relative to the triliteral root — the same
system the Lingualism index uses (1s / 5h / 7d …). We derive it independently from
Maknuune's data (roots + perfect form) so nothing is copied from the copyrighted book;
the book is only used to spot-check that this classifier agrees.

Form is the derivational measure (how the root is augmented). Weak-class is which
radical is weak (sound / hollow / defective / doubled / assimilated / hamzated).
"""
import re
DIAC = re.compile(r'[ً-ْٰـ]')
def bare(s): return DIAC.sub('', str(s)).strip()

WEAK = set('وياء')

def radicals(root):
    return [x for x in bare(root).replace('.', '-').split('-') if x]

def weak_class(root):
    r = radicals(root)
    if len(r) == 4: return 'quad'
    if len(r) != 3: return 'other'
    r1, r2, r3 = r
    if r1 == r2 or r2 == r3: return 'doubled'
    if r1 in 'وي':          return 'assimilated'
    if r2 in 'وياأ':         return 'hollow'
    if r3 in 'وياى':         return 'defective'
    if 'ء' in (r1, r2, r3) or 'أ' in r1: return 'hamzated'
    return 'sound'

def measure(perfect, root):
    """Return 1..10 (Arabic Form), 'Q' for quadriliteral, or None. Uses the shadda and
    the weak class, both of which disambiguate patterns that look identical when bare."""
    p = bare(perfect)
    r = radicals(root)
    weak = weak_class(root)
    if len(r) == 4: return 'Q'
    if len(r) != 3: return None
    c1, c2, c3 = r
    has_shadda = 'ّ' in str(perfect)          # keep the shadda from the vocalized form
    body = p[1:] if p[:1] in 'اأإ' else p       # drop a fronting dialectal alef

    if body.startswith('ست'):                   return 10   # X: ista-
    if body.startswith('ت') and c1 != 'ت':                  # V (ta-) vs VI (taCaaCaC)
        return 6 if body[2:3] == 'ا' else 5
    if body.startswith('ن') and c1 != 'ن':      return 7    # VII: n-
    if len(body) >= 2 and body[0] == c1 and body[1] == 'ت' and c2 != 'ت':
        return 8                                            # VIII: C1 + t infix
    # III (CaaCaC) — the alef after C1 is an AUGMENT only if the middle radical is sound.
    # For hollow verbs (قال) that alef IS the weak radical → Form I, not III.
    if len(p) >= 2 and p[0] == c1 and p[1] == 'ا' and weak != 'hollow':
        return 3
    # II (CaCCaC) — doubled middle radical, shown by a shadda. A doubled ROOT (حبّ) also
    # has a shadda but is Form I; the weak class tells them apart.
    if has_shadda and weak != 'doubled':        return 2
    if p.startswith('أ') and bare(p)[1:2] == c1: return 4   # IV: 'a- (rare in dialect)
    return 1                                                # I: the default

def classify(perfect, imperfect, root):
    return {'form': measure(perfect, root), 'weak': weak_class(root)}
