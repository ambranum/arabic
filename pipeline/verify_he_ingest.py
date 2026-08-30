#!/usr/bin/env python3
"""Does the Hebrew annotator still work once words have been ADJUDICATED?

This exists because of a specific failure. he_ingest.py annotates a text twice: once to find
the ambiguous words, and again after an adjudicator has picked an entry for each. The second
pass calls lex.by_id -- and spike/he/lex.py did not have a by_id. Nothing caught it, because
the only test that had ever run was on a text with NO resolutions, where that branch is never
reached. The first Hebrew news article in history was written, annotated and paid for, and then
died on the line that applies the answer.

So the second pass is what this tests, on real material:

  1. annotate with an empty trail -- the words that need a decision are found;
  2. build a trail from those words' own options, which is what the adjudicator returns;
  3. annotate again -- every decision is APPLIED, and comes back as the entry that was chosen.

Plus the two invariants a resolution must not break: it may not put pointing on a word whose
match required cutting a prefix, and it may not change which word is on the page.

    python3 pipeline/verify_he_ingest.py --lang he
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths  # noqa: E402
paths.require('he')

import he_ingest  # noqa: E402
from lex import Lexicon  # noqa: E402

ARTICLE = paths.texts('news-2026-08-29.json')

ok = fail = 0


def check(cond, what, detail=''):
    global ok, fail
    if cond:
        ok += 1
        print('  \033[32m✓\033[0m %s' % what)
    else:
        fail += 1
        print('  \033[31m✗ %s\033[0m%s' % (what, '\n      ' + detail if detail else ''))


def main():
    if not os.path.exists(ARTICLE):
        print('no %s to test against' % os.path.relpath(ARTICLE, paths.ROOT))
        return 1
    src = json.load(open(ARTICLE, encoding='utf-8'))
    lex = Lexicon()
    toks = [t for s in src['sentences'] for t in he_ingest.tokenize(s['ar'])]
    print('%d tokens from %s\n' % (len(toks), os.path.basename(ARTICLE)))

    # ---- pass 1: nothing decided yet -------------------------------------------------------
    first = [he_ingest.annotate(lex, t, {}) for t in toks]
    amb = [w for w in first if w['provenance'] == 'AMBIGUOUS-needs-resolution']
    check(len(amb) > 0, 'pass 1 finds words needing a decision (%d of %d)' % (len(amb), len(toks)))
    check(all(w.get('options') for w in amb), 'every one of them carries real candidates')

    # ---- pass 2: apply what an adjudicator would have returned ------------------------------
    # The LAST option, not the first: the first is what pass 1 already displays, so picking it
    # would pass this test without proving the decision was applied at all.
    trail = {w['surface']: w['options'][-1]['id'] for w in amb}
    second = [he_ingest.annotate(lex, t, trail) for t in toks]
    by_surface = {w['surface']: w for w in second}

    applied = [w for w in second if w['provenance'] == 'wiktionary:resolved']
    check(len(applied) >= len(trail),
          'pass 2 applies every decision (%d resolved, %d in the trail)' % (len(applied), len(trail)))
    check(not any(w['provenance'] == 'AMBIGUOUS-needs-resolution' for w in second),
          'nothing is still waiting on a decision')

    wrong = [(w['surface'], w['maknuune_id'], trail[w['surface']])
             for w in applied if str(w['maknuune_id']) != str(trail.get(w['surface']))]
    check(not wrong, 'each resolved word carries the entry that was chosen',
          '; '.join('%s got %s wanted %s' % x for x in wrong[:3]))

    # ---- the two invariants ----------------------------------------------------------------
    lied = [w['surface'] for w in second if w.get('_cut') and w.get('vocalized')]
    check(not lied,
          'no word matched by cutting a prefix claims a vocalization',
          ', '.join(lied[:5]))

    moved = [w['surface'] for w, t in zip(second, toks) if w['surface'] != t]
    check(not moved, 'the word on the page is the word that was written', ', '.join(moved[:5]))

    # ---- the word that is also a particle plus a word -------------------------------------
    # An exact match is not an unambiguous one. שקרה IS שִׁקְּרָה "she lied" and it is also
    # ש- + קָרָה "that happened", and the second is what a news sentence means -- but the exact
    # match won in look() before the peeler ever ran, so the word was taken silently, with one
    # candidate, and never reached the adjudicator that could have chosen. Each case below is a
    # word this shipped wrong.
    print()
    for surface, stem in [('שקרה', 'קָרָה'),        # ש + "happened", shipped as "she lied"
                          ('שהיה', 'הָיָה'),        # ש + "was", shipped as "a stay"
                          ('ביום', 'יוֹם'),         # ב + "day", shipped as "staging"
                          ('השאלה', 'שְׁאֵלָה')]:   # ה + "question", shipped as "to lend"
        w = he_ingest.annotate(lex, surface, {})
        pointed = [o['pointed'] for o in w.get('options', [])]
        check(w['provenance'] == 'AMBIGUOUS-needs-resolution' and stem in pointed,
              '%s is offered as a prefix + %s' % (surface, stem),
              '%s, options %s' % (w['provenance'], pointed))
        # and choosing that reading has to behave like any other clitic match: the lexicon
        # pointed the stem, nothing pointed the particle, so no vocalization is claimed.
        pick = next(o['id'] for o in w['options'] if o['pointed'] == stem)
        r = he_ingest.annotate(lex, surface, {surface: pick})
        check(r['provenance'] == 'wiktionary:resolved' and r['_cut'] and not r['vocalized'],
              '%s resolved to %s claims no vocalization' % (surface, stem),
              'cut=%r vocalized=%r' % (r.get('_cut'), r.get('vocalized')))

    # The other half of the rule, which is what keeps the queue affordable. A word the lexicon
    # lists AS A HEADWORD is real as written, and so is an entry that spells the prefix itself
    # -- the ה of a definite noun, the ל of an infinitive, the מ of a participle. Every one of
    # these begins with a particle letter and none of them is ambiguous.
    print()
    for surface in ['משפט',        # headword; מ + שָׁפַט "he judged" is not Hebrew
                    'למרות',       # headword, and ל + מָרוֹת is a coincidence
                    'הבחירות',     # the lexicon's own definite form, pointed whole
                    'להגיע',       # an infinitive: the ל is its own
                    'מחפשים']:     # a present participle: the מ is its own
        w = he_ingest.annotate(lex, surface, {})
        check(w['provenance'] != 'AMBIGUOUS-needs-resolution' and w['vocalized'],
              '%s is not sent for adjudication' % surface,
              '%s, vocalized=%r' % (w['provenance'], w.get('vocalized')))

    # A trail names entries by id, and ids outlive the text they were chosen for. An id that is
    # not a reading of this word at all is a stale line, not an answer: applying it would put a
    # stranger's pointing and gloss on the page.
    stray = he_ingest.annotate(lex, 'בבית', {'בבית': lex.df.iloc[0]['ID']})
    check(stray['provenance'] != 'wiktionary:resolved',
          'a resolution that is not a reading of the word is refused', stray['provenance'])

    # ---- tokenizing ------------------------------------------------------------------------
    # In Hebrew the same character is punctuation and part of a word. A gershayim before the
    # last letter makes an acronym, and everyday news is full of them; splitting on the quote
    # turned השב"כ into שב + כ, which was then pointed as שָׁב "returned" and shipped.
    print()
    for text, want in [('השב"כ אישר', ['השב"כ', 'אישר']),
                       ('ארה"ב תשלוט', ['ארה"ב', 'תשלוט']),
                       ('ג\u05f3ורג\u05f3 הלך', ['ג\u05f3ורג\u05f3', 'הלך']),
                       ('הוא אמר "שלום" ואז', ['הוא', 'אמר', 'שלום', 'ואז']),
                       ('בן 93 נהרג', ['בן', 'נהרג'])]:
        got = he_ingest.tokenize(text)
        check(got == want, 'tokenizes %s' % text, 'got %s' % got)

    print('\n%d passed, %d failed' % (ok, fail))
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
