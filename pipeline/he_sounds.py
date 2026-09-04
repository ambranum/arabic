#!/usr/bin/env python3
"""Build texts/he/sounds.json — the Phase-0 Hebrew pronunciation contrasts.

The Arabic side's sounds.json is hand-written: a dialect's realizations are not in any lexicon,
so somebody had to write down that ق is a glottal stop in Jerusalem. Hebrew does not need that
and must not do it, because everything a Sounds lesson wants is already looked up:

  * the word and its POINTING come from the lexicon;
  * the romanization is its PHON column, which is Wiktionary's or phon.py's, not ours;
  * the meaning is its GLOSS.

So this file curates only what is genuinely teaching -- which contrasts are worth six lessons,
and how to explain each one -- and every WORD is a reference the lexicon has to answer. Ask for a
word that is not there, or that two entries answer to, and the build stops rather than shipping a
pair somebody remembered.

The pairs themselves were not remembered either. They came out of a sweep for lexicon entries
whose pronunciations differ in exactly one segment (or in nothing but the stress), which is what
makes them minimal pairs rather than illustrations.

    python3 pipeline/he_sounds.py            # writes texts/he/sounds.json
    python3 pipeline/sounds.py --lang he     # then this turns it into app/data/he/sounds.js
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')

try:
    import pandas as pd   # noqa: E402
except ModuleNotFoundError:                       # the python3 first on PATH is not the one
    raise SystemExit(                             # that can run this pipeline. Say so, once.
        "\n!! This needs pandas, and the python3 at the front of your PATH does not have it.\n"
        "   Re-run the same command with the interpreter that does:\n"
        "       /usr/local/bin/python3 <the rest of your command>\n"
        "   (Homebrew's python3 is first on PATH here and carries no pandas; the framework\n"
        "    build at /usr/local/bin/python3 is the one the pipeline has always used.)\n")
from phon import beat, phon_stressed   # noqa: E402

LEX = os.path.join(paths.ROOT, 'spike', 'he', 'hebrew_lex.parquet')
OUT = paths.texts('sounds.json')

# id, heading, the letter(s), the one-line target, the explanation, then the words. A word is
# ('<pointed form>', '<a word from its gloss>'), and a pair is two of them.
LESSONS = [
 {'id': 'resh', 'en': 'ר — the r is in the throat, not on the tongue', 'ar': 'ריש',
  'target': 'ר = uvular r',
  'tip': 'Israeli ר is made at the very back of the mouth, where you gargle — much closer to '
         'French or German r than to English. An English "r" (tongue curled up in the middle of '
         'the mouth) is the single loudest giveaway of a foreign accent in Hebrew, and it is the '
         'easiest one to fix: leave the tip of your tongue behind your bottom teeth and let the '
         'back of the tongue do the work. It is the same sound at the start, middle and end of a '
         'word — there is no silent ר.',
  'words': [('רַק', 'only'), ('רוּחַ', 'wind'), ('בֹּקֶר', 'morning'),
            ('חָבֵר', '(male) friend'), ('עִיר', 'city'), ('אֶרֶץ', 'land')]},

 {'id': 'het-khaf', 'en': 'ח and כ — one sound, and it is not h and not k', 'ar': 'חית וכף',
  'target': 'ח, כ = kh',
  'tip': 'Both letters are the rasp at the back of the throat, the sound at the end of Bach or '
         'loch — written x in the romanization here, the way the rest of the app writes it. ח '
         'used to be a deeper, pharyngeal sound and still is for some '
         'speakers, but in general Israeli speech ח and כ (without its dot) are the same. The two '
         'mistakes to avoid are saying an English h, which turns חוֹל "sand" into a different '
         'word, and saying k, which turns it into another one. Each pair below is a real pair: '
         'the only difference is this sound.',
  'pairs': [(('חָלַם', 'dream'), ('הָלַם', 'strike')),
            (('חוֹל', 'sand'), ('קוֹל', 'voice')),
            (('חַד', 'sharp'), ('כַּד', 'jar')),
            (('חֵץ', 'arrow'), ('קֵץ', 'end')),
            (('רַךְ', 'soft'), ('רַק', 'only'))]},

 {'id': 'same-sound', 'en': 'The letters that sound identical', 'ar': 'אותיות זהות', 'same': True,
  'target': 'א=ע  ת=ט  כּ=ק  שׂ=ס  ב=ו  ח=כ',
  'tip': 'Hebrew keeps letters for distinctions the modern language stopped making, so several '
         'pairs are now pronounced exactly alike. Nothing in the sound tells you which one to '
         'write — you learn the spelling with the word, the way English speakers learn there / '
         'their. This is the good news for listening and the bad news for spelling: every pair '
         'below is two DIFFERENT words that sound the same.',
  'pairs': [(('אַל', 'not'), ('עַל', 'on')),
            (('אַף', 'nose'), ('עָף', 'fly')),
            (('עֵט', 'pen'), ('עֵת', 'time')),
            (('כֵּן', 'yes'), ('קֵן', 'nest')),
            (('סַם', 'drug'), ('שָׂם', 'place')),
            (('צָב', 'turtle'), ('צַו', 'decree')),
            (('מָחָר', 'tomorrow'), ('מָכַר', 'sell'))]},

 {'id': 'tsadi', 'en': 'צ — one letter, two English sounds', 'ar': 'צדי', 'target': 'צ = ts',
  'tip': 'צ is ts, the sound at the end of cats — both consonants, together, including at the '
         'start of a word where English never puts them. That is the hard part: English has no '
         'word beginning ts-, so the instinct is to drop the t and say s. Do that and צָם "he '
         'fasted" becomes סַם "a drug". Practise from the end: say "cats", then "cats am", then '
         'drop the ca-.',
  'pairs': [(('צָם', 'fast'), ('סַם', 'drug')),
            (('צַר', 'narrow'), ('סָר', 'turn')),
            (('נֵץ', 'hawk'), ('נֵס', 'miracle')),
            (('צָף', 'float'), ('סַף', 'threshold'))]},

 {'id': 'dagesh', 'en': 'The dot inside the letter changes it', 'ar': 'דגש',
  'target': 'בּ/ב · כּ/כ · פּ/פ',
  'tip': 'Three letters are two sounds each, and a dot in the middle is what tells them apart: '
         'בּ is b and ב is v, כּ is k and כ is kh, פּ is p and פ is f. Unpointed writing leaves the '
         'dot out, so the reader has to know the word — one more reason to learn words with their '
         'vowels. Each pair below is the SAME three root letters: only the dot moves.',
  'pairs': [(('שַׁבָּת', 'Shabbat'), ('שָׁבַת', 'rest')),
            (('סַפָּר', 'barber'), ('סָפַר', 'count')),
            (('צַבָּר', 'cactus'), ('צָבַר', 'store')),
            (('נַפָּח', 'smith'), ('נָפַח', 'blow')),
            (('טַבָּח', 'butcher'), ('טָבַח', 'slaughter'))]},

 {'id': 'stress', 'en': "Where the beat falls — milra and mil'el", 'ar': 'מלרע ומלעיל',
  'target': 'final vs next-to-last',
  'tip': 'Hebrew stresses the LAST syllable by default — that is milra, and it is why the '
         'romanization here only marks the stress when it is somewhere else. The exception is '
         "common enough to matter: mil'el, stress on the next-to-last syllable, which is where a "
         'great many everyday nouns sit. Same root, same letters, and the beat is the only thing '
         'telling the noun from the verb: PÁ-xad is fear, pa-XÁD is he was afraid. Say them '
         'wrong and you are understood, but you sound like you are reading.',
  'stress': True,
  'pairs': [(('פַּחַד', 'fear'), ('פָּחַד', 'afraid')),
            (('כַּעַס', 'anger'), ('כָּעַס', 'angry')),
            (('זַחַל', 'caterpillar'), ('זָחַל', 'crawl')),
            (('בֶּרֶךְ', 'knee'), ('בֵּרֵךְ', 'to bless')),
            (('עֹדֶף', 'change'), ('עוֹדֵף', 'surplus'))]},
]

PAREN = re.compile(r'\s*\([^)]*\)')
POINTER = re.compile(r'^(defective|excessive|alternative|misspelling|form of|singular|plural)', re.I)


def short(gloss):
    """The lexicon's gloss, cut to its first sense. Trimmed, never rewritten."""
    g = PAREN.sub('', str(gloss)).strip()
    for sep in (';', ':', ' \u2014 '):
        g = g.split(sep)[0].strip()
    if len(g) > 42:
        g = g.split(',')[0].strip()
    return g.rstrip('.').strip() or str(gloss)[:42]


def resolve(df, form, hint, mark_final=False):
    """The lexicon's answer for this word, or a loud failure. Never a guess."""
    hit = df[(df['FORM'] == form) & (df['GLOSS'].astype(str).str.contains(re.escape(hint), case=False))]
    if hit.empty:
        raise SystemExit('!! no lexicon entry for %s with %r in its gloss' % (form, hint))
    lemmas = set(hit['LEMMA'])
    if len(lemmas) > 1:
        raise SystemExit('!! %s / %r is ambiguous: %s' % (form, hint, ', '.join(lemmas)))
    # A row whose gloss only points at another spelling ("defective spelling of בוקר") is a
    # cross-reference, not a definition, and it is not what a learner should be shown.
    rows = sorted(hit.to_dict('records'),
                  key=lambda r: (bool(POINTER.match(str(r['GLOSS']))),
                                 not str(r['PHON_SRC']).endswith('+stress')))
    r = rows[0]
    if not str(r['PHON']):
        raise SystemExit('!! %s has no pronunciation in the lexicon' % form)
    # The SEGMENTS come from phon.py rather than from the lexicon's romanization, and the whole
    # module is better for it. Wiktionary's transliterations are inconsistent between entries --
    # ken for כֵּן but bóqer for בֹּקֶר -- and a page whose job is to say that כּ and ק are one
    # sound cannot spell them two ways. phon.py derives every reading from the pointing by the
    # same rules, so the lesson and the romanization agree by construction. The STRESS is still
    # Wiktionary's, because nothing derives it.
    # The lexicon's own reading already carries the beat where anything knows it (build_lex
    # shares it across every row of a form), so this reads it back rather than re-deriving.
    known = next((x['PHON'] for x in rows if str(x['PHON_SRC']).endswith('+stress')), '')
    tr = phon_stressed(r['FORM'], beat(known), mark_final=mark_final)
    return {'ar': r['FORM'], 'tr': tr, 'en': short(r['GLOSS']), 'id': str(r['ID'])}


def main():
    df = pd.read_parquet(LEX)
    out = []
    for L in LESSONS:
        exs = []
        mf = bool(L.get('stress'))
        for w in L.get('words', []):
            exs.append(resolve(df, *w, mark_final=mf))
        for a, b in L.get('pairs', []):
            e = resolve(df, *a, mark_final=mf)
            e['contrast'] = resolve(df, *b, mark_final=mf)
            exs.append(e)
        les = {k: L[k] for k in ('id', 'en', 'ar', 'target', 'tip')}
        if L.get('same'):
            les['same'] = True
        les['examples'] = exs
        # The page prints = or ≠ between the two halves of a pair, so the claim has to be true
        # of the readings themselves. A lesson that says two words sound alike and shows two
        # different romanizations teaches the reader to distrust the page, and one that prints ≠
        # between homophones teaches them to hear a difference that is not there.
        for e in exs:
            c = e.get('contrast')
            if not c:
                continue
            alike = e['tr'] == c['tr']
            if bool(L.get('same')) != alike:
                raise SystemExit('!! %s: %s (%s) and %s (%s) are %s, but the lesson says %s'
                                 % (L['id'], e['ar'], e['tr'], c['ar'], c['tr'],
                                    'the same' if alike else 'different',
                                    'the same' if L.get('same') else 'different'))
        out.append(les)

    doc = {
        'id': 'sounds-he', 'title': {'ar': 'צלילים', 'en': 'Sounds'}, 'kind': 'sounds',
        'dialect': 'he',
        'intro': 'Six things about Hebrew sound that trip up English speakers. Get these into '
                     'your ear and your mouth <b>first</b> — a sound is much harder to fix once it '
                     'sets. Everything here is general Israeli pronunciation, the same as the '
                     "app's voice.",
        'caveat': '<b>Read the tip, then listen.</b> Every word, its vowels, its '
                           'romanization and its meaning are the lexicon\'s. The clips are '
                           'synthesized for reference — for ר and the throat sounds a real '
                           'speaker beats any voice model, so treat those as a hint, not gospel.',
        # Internal notes, in the shape the Arabic file uses: what this is for, and where each
        # part of it came from. Not displayed.
        'rationale': 'Phase 0. Six things about Hebrew sound that an English speaker gets wrong, '
                     'chosen for what changes a word rather than for what sounds foreign.',
        'provenance_note': 'The lesson set and the tips are curated teaching. Every WORD is '
                           'looked up in the lexicon by pipeline/he_sounds.py -- pointing, gloss '
                           'and id from the entry, romanization derived from the pointing by '
                           'spike/he/phon.py, stress from the entry when Wiktionary marks it. '
                           'The pairs were found by sweeping the lexicon for entries whose '
                           'pronunciations differ in exactly one segment, or in nothing but '
                           'the stress.',
        'lessons': out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = sum(len(L['examples']) for L in out)
    m = sum(1 for L in out for e in L['examples'] if e.get('contrast'))
    print('%d lessons · %d words · %d pairs' % (len(out), n + m, m))
    print('-> %s' % os.path.relpath(OUT, paths.ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
