#!/usr/bin/env python3
"""Repair b-prefix vocalization in already-built artifacts.

The three bugs this fixes are fixed at source in vocalize.py + ingest.py, so a full
`ingest.py` re-run produces correct output and this script becomes unnecessary. It exists
because a re-ingest needs data/maknuune.parquet, and that file is often not on disk (it's
iCloud-offloaded, and it's the one input we can't regenerate). This pass needs nothing but
the artifacts themselves, so the shipped app can be corrected either way.

  1. بـ is also the PREPOSITION "in/with". The b-imperfect branch had no VERB guard, so
     بسبب / بمدينة / بطريقة were all handed a verb's 1sg fatha. Always kasra on a non-verb.
  2. بشتغل is genuinely ambiguous: بَشتِغِل "I work" and بِشتِغِل "he works" are spelt the
     same. It always guessed 1sg. Now the neighbouring word decides — an explicit أنا means
     first person, a preceding noun or he/she/they pronoun means third — and where nothing
     decides it, the vowels come off rather than teach the wrong person.
  3. بت/بن/بي wrote a blind sukuun on the affix consonant, giving بِتْسْكُن — three
     consonants in a row, which no one can say. The affix takes the imperfect's own prefix
     vowel (recoverable from the stored pronunciation): بِتُسْكُن.

Run: python3 pipeline/repair_vocalization.py   (then rebuild: python3 pipeline/build_app.py)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import json, glob, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FATHA, DAMMA, KASRA, SUKUN = 'َ', 'ُ', 'ِ', 'ْ'
VOWEL_OF = {'a': FATHA, 'u': DAMMA, 'i': KASRA, 'o': DAMMA, 'e': KASRA}
THIRD_PRON = ('هو', 'هي', 'هم', 'همه', 'هنّ', 'هُمّة')
FIRST_PRON = ('أنا', 'انا', 'وأنا', 'وانا')

def subject_of(words, i):
    """Who is doing this verb, judged from the word before it."""
    if i == 0: return None
    ps = words[i - 1].get('surface') or ''
    pa = str(words[i - 1].get('analysis') or '')
    if ps in FIRST_PRON: return '1sg'
    if pa.startswith(('NOUN', 'ADJ')) or ps in THIRD_PRON: return '3'
    return None

def imperfect_prefix_vowel(caphi):
    """يُسْكُن is stored as 'yuskun' -> the prefix vowel is u -> damma."""
    c = str(caphi or '')
    if len(c) > 1 and c[0] == 'y' and c[1].lower() in VOWEL_OF:
        return VOWEL_OF[c[1].lower()]
    return ''

CONS_PH = {'ب':'b','ت':'t','ث':'th','ج':'j','ح':'7','خ':'kh','د':'d','ذ':'dh','ر':'r','ز':'z',
           'س':'s','ش':'sh','ص':'s','ض':'d','ط':'t','ظ':'z','ع':'3','غ':'gh','ف':'f','ق':'2',
           'ك':'k','ل':'l','م':'m','ن':'n','ه':'h','و':'w','ي':'y'}

def repair(words):
    changed = {'nonverb': 0, 'person': 0, 'dropped': 0, 'cluster': 0, 'initial': 0}
    for w in words:
        # A word can't open with two sukuun-ed consonants — مْخْتَلِف is unsayable. The stored
        # pronunciation says which vowel belongs there (mukhtalif -> damma on the م).
        v = w.get('vocalized') or ''
        m = re.match(r'^(.)' + SUKUN + r'(.)' + SUKUN, v)
        if m:
            ph = str(w.get('caphi_urban') or w.get('caphi') or '')
            want = CONS_PH.get(m.group(1))
            if want and ph.startswith(want):
                rest = ph[len(want):]
                if rest and rest[0].lower() in VOWEL_OF:
                    w['vocalized'] = v[0] + VOWEL_OF[rest[0].lower()] + v[2:]
                    changed['initial'] += 1
    for i, w in enumerate(words):
        if w.get('vocalized_from') != 'derived:verb':
            continue
        v = w.get('vocalized') or ''
        if not v:
            continue
        is_verb = str(w.get('analysis') or '').startswith('VERB')

        # (1) بـ on a non-verb is the preposition — kasra, and it isn't a verb derivation.
        if not is_verb:
            if v.startswith('بَ'):
                w['vocalized'] = 'بِ' + v[2:]
                changed['nonverb'] += 1
            w['vocalized_from'] = 'derived:affix'
            continue

        # (2) bare بَ on a real verb: let the subject decide, or take the vowels off.
        if v.startswith('بَ'):
            subj = subject_of(words, i)
            if subj == '3':
                w['vocalized'] = 'بِ' + v[2:]; changed['person'] += 1
            elif subj != '1sg':
                w['vocalized'] = None
                w['vocalized_from'] = 'unvocalized:ambiguous-person'
                changed['dropped'] += 1
                continue

        # (3) بت / بن / بي with two sukuuns in a row is unpronounceable.
        m = re.match(r'^(ب[ِْ]?)([تني])' + SUKUN + r'(.)' + SUKUN, w['vocalized'] or '')
        if m:
            vowel = imperfect_prefix_vowel(w.get('caphi_urban') or w.get('caphi'))
            if vowel:
                s = w['vocalized']
                cut = len(m.group(1)) + 1                      # index just after the affix letter
                w['vocalized'] = s[:cut] + vowel + s[cut + 1:]
                changed['cluster'] += 1
    return changed

def main():
    total = {'nonverb': 0, 'person': 0, 'dropped': 0, 'cluster': 0, 'initial': 0}
    files = 0
    for p in sorted(glob.glob(paths.build('*', 'text.json'))):
        d = json.load(open(p, encoding='utf-8'))
        touched = False
        for s in d.get('sentences') or []:
            c = repair(s.get('words') or [])
            if any(c.values()):
                touched = True
                for k in total: total[k] += c[k]
        if touched:
            json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            files += 1
    print('files rewritten:', files)
    print('  non-verb بـ  fatha -> kasra :', total['nonverb'])
    print('  verb, 3rd-person subject    :', total['person'])
    print('  verb, subject unknown -> unvocalized:', total['dropped'])
    print('  impossible clusters repaired:', total['cluster'])
    print('  unsayable word-initial clusters:', total['initial'])
    return 0

if __name__ == '__main__':
    sys.exit(main())
