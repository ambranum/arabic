#!/usr/bin/env python3
"""One-off: strip the transcription apparatus out of texts/lessons/unit-*.json.

The lesson units were transcribed from a physical copy of the reference books — a copy a
previous student had annotated in pencil. The transcription faithfully recorded the
annotations, and then the app rendered them at the learner:

    group  "Handwritten additions at the bottom of p011 (student pencil)"   <- a section HEADER
    note   "book: pencil note 'form 7'"
    en     "(handwritten: happy)"                                           <- the whole GLOSS

That is the cosmetic half. The other half is not cosmetic: where the book's printed English
was wrong, the transcriber left the wrong gloss in `en` and put the correction in `note`.
The app was teaching مُشْكِلِة = "mountain", مَطْعَم = "mountain", بَقَرَة = "caw",
عامِل = "musician". Twenty glosses, all wrong on screen, all correct one field away.

Corrections come from the note itself (the book's own handwritten fix) and were cross-checked
against Maknuune where it has the word; where Maknuune and the note differ, both are kept
rather than picking a winner. Nothing here is invented.

Run once, then `python3 pipeline/lessons.py` to regenerate app/data/lessons.js.
"""
import json, glob, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# (unit, chunk index) -> corrected English, or None to keep `en` and only drop the note.
# Every entry was read against its Arabic; see the module docstring for provenance.
EN_FIX = {
    ('unit-04', 14): 'worker',                       # عامِل — was "musician"
    ('unit-04', 20): 'soldier',                      # جُنْدي — was "musician"
    ('unit-04', 24): 'psychologist',                 # was "psychology"
    ('unit-07',  2): 'dining table',                 # طاولة السفرة — was "door"
    ('unit-07',  3): 'sitting area, salon',          # was "sitting era, salon"
    ('unit-11',  6): 'fennel',                       # شُومَر — was "dill"
    ('unit-11', 11): 'mint',                         # نَعْنَع — was "nana"
    ('unit-11', 13): 'beet',                         # شَمَنْدَر — was "fennel"
    ('unit-12', 25): 'dark purple',                  # was "dark perple"
    ('unit-12', 26): 'big, old – small, young',      # was "bid, old- small, young"
    ('unit-14', 35): 'horse, mare',                  # was "hors, mare"
    ('unit-14', 41): 'cow',                          # was "caw"
    ('unit-14', 44): 'goose',                        # was "gees"
    ('unit-19',  4): 'plane',                        # was "plain"
    ('unit-28', 36): 'bored',
    ('unit-28', 41): 'relaxed, comfortable',         # note "relaxed" + Maknuune "comfortable"
    ('unit-28', 46): 'depressed',
    ('unit-28', 48): 'stressed, under pressure',     # note "stressed" + Maknuune "very busy"
    ('unit-28', 53): 'hardline, extremist',          # was "conservative"
    ('unit-28', 58): 'beloved, well-liked',          # note "beloved" + Maknuune "lovable"
    ('unit-28', 65): 'racist',                       # gloss was an illegibility note
    ('unit-30', 65): 'café, coffeehouse',            # مَقْهَى — was "coffee" (that is قَهْوَة)
    ('unit-30', 66): 'problem',                      # مُشْكِلِة — was "mountain"
    ('unit-30', 67): 'restaurant',                   # مَطْعَم — was "mountain"
}

# Parentheticals in `en` that describe the physical page rather than the word. The capture
# keeps anything genuinely linguistic that shares the bracket ("Hebrew loanword").
# ORDER MATTERS. The unwrap has to run before the strip: with the strip first, a gloss that is
# ENTIRELY an annotation — "(handwritten: happy)", which is most of unit-28 — matched the strip
# rule and became the empty string, deleting the meaning instead of the noise. And the unwrap is
# greedy to the LAST bracket so "(handwritten: tired (sleepy))" keeps its inner one.
EN_STRIP = [
    (re.compile(r'^\(handwritten:?\s*(.*)\)$'), r'\1'),
    (re.compile(r'\s*\(handwritten[^)]*;\s*(Hebrew loanword)\)'), r' (\1)'),
    (re.compile(r'\s*\(handwritten[^)]*\)'), ''),
    (re.compile(r'[\s;,]+$'), ''),          # "hesitant ; (handwritten: confused)" left a dangling ;
]

# Group headers double as section titles, so they are trimmed, not deleted: keep the part that
# describes the material, drop the part that describes the paper it was printed on.
GROUP_FIX = {
    # Kept as provenance, not as an archival note: this material genuinely is not in the
    # printed book, and a learner should know that before trusting it like the rest.
    'Handwritten additions at the bottom of p011 (student pencil)':
        'More directions (not in the printed book)',
    'مجموعة 1: adjectives with broken plurals (printed page 156). Handwritten glosses in pencil: '
    'short, long, big, little, cheep, old, new, clean, poor, rich, sad, far, weak, slowly.':
        'مجموعة 1 — adjectives with broken plurals',
    'مجموعة 3: فَعْلان-pattern adjectives, all pluralized with ين (printed page 157). Handwritten '
    "arrow note at top: 'ات for girls'. English equivalents are handwritten pencil glosses, given "
    'in parentheses below.':
        'مجموعة 3 — فَعْلان adjectives (plural ين; ات for a group of women)',
    'مجموعة 4: participial adjectives, plural ين; printed English glosses in parentheses, some '
    'handwritten (printed page 157)':
        'مجموعة 4 — participial adjectives (plural ين)',
    "حروف الاتصال في العامية — conjunctions (printed page 149; handwritten note 'Only amia' at top)":
        'حروف الاتصال — conjunctions in spoken Arabic only',
    # This header warned that "the last four glosses on this run are misprinted". It was true,
    # and it is the reason those four were checked: سوق was already corrected to "market" by the
    # lesson author, and مَقْهَى / مُشْكِلِة / مَطْعَم are fixed above. A standing warning that
    # something is wrong, after it has been made right, only teaches distrust.
    'وحدة 6 (printed pages 160-161; continues onto p.8). The last four glosses on this run are '
    'misprinted in the book.': 'وحدة 6',
}

TITLE_STRIP = re.compile(r'\s*\((?:heavily )?annotated[^)]*\)\s*$')

# Page references inside group headers: "وحدة 17 (printed page 166)". 294 chunks across 31
# headers. The unit already carries its page provenance in `src`, which the app shows — a page
# number repeated inside a section title is the archivist talking again. Only the parenthetical
# goes; anything after it stays, because some of those trailing sentences are real teaching
# notes ("The last four glosses on this run are misprinted in the book.").
GROUP_PAGE = re.compile(r'\s*\(printed pages?[^)]*\)')
DANGLING   = re.compile(r'\s+([.;,])')

# One drill cue carried an editorial bracket AND contradicted itself: the book prints 7:45 while
# the English answer is "ten to eight" (7:50). Stripping the bracket alone would leave a drill
# that teaches the wrong time, so the cue takes the reading its own English demands.
CUE_FIX = {"7:45 It's ten to eight. [sic — printed 7:45; presumably 7:50]":
           "7:50 It's ten to eight."}

# A single [sic] left inside an ARABIC field (unit-31, فَلّاح – فلّاحات [sic]). Latin brackets in
# an `ar` string are worse than untidy: arLive() tokenizes that field, so the marker rendered as
# tappable Latin inside a right-to-left line. The book's plural stands as the book has it.
AR_MARK = re.compile(r'\s*\[sic[^\]]*\]')

def main():
    changed = files = 0
    log = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'texts', 'lessons', 'unit-*.json'))):
        uid = os.path.basename(path).replace('.json', '')
        u = json.load(open(path, encoding='utf-8'))
        before = json.dumps(u, ensure_ascii=False, sort_keys=True)

        for i, c in enumerate(u.get('chunks', [])):
            if c.get('note', '').startswith('book:'):
                fix = EN_FIX.get((uid, i))
                if fix:
                    log.append('%s c%-3d en  %-36r -> %r' % (uid, i, (c.get('en') or '')[:34], fix))
                    c['en'] = fix
                c.pop('note', None)
            a = c.get('ar')
            if a and AR_MARK.search(a):
                na = AR_MARK.sub('', a)
                log.append('%s c%-3d ar  stripped editorial [sic]' % (uid, i))
                c['ar'] = na
            en = c.get('en')
            if en:
                new = en
                for pat, rep in EN_STRIP:
                    new = pat.sub(rep, new)
                new = new.strip()
                if new != en:
                    log.append('%s c%-3d en  %-36r -> %r' % (uid, i, en[:34], new))
                    c['en'] = new
            g = c.get('group')
            if g in GROUP_FIX:
                c['group'] = GROUP_FIX[g]
            elif g and GROUP_PAGE.search(g):
                ng = DANGLING.sub(r'\1', GROUP_PAGE.sub('', g)).strip()
                if ng != g:
                    log.append('%s c%-3d grp %-36r -> %r' % (uid, i, g[:34], ng[:40]))
                    c['group'] = ng
        for d in u.get('drills', []):
            for it in d.get('items', []):
                for k in ('cue', 'answer'):
                    if it.get(k) in CUE_FIX:
                        log.append('%s      cue %r -> %r' % (uid, it[k][:44], CUE_FIX[it[k]]))
                        it[k] = CUE_FIX[it[k]]
        for d in u.get('dialogues', []):
            t = d.get('title')
            if t and TITLE_STRIP.search(t):
                d['title'] = TITLE_STRIP.sub('', t).strip()
                log.append('%s      title %r -> %r' % (uid, t[:40], d['title']))

        after = json.dumps(u, ensure_ascii=False, sort_keys=True)
        if after != before:
            json.dump(u, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            files += 1
            changed += 1
    for line in log:
        print(line)
    print('\n%d files rewritten, %d edits' % (files, len(log)))

if __name__ == '__main__':
    main()
