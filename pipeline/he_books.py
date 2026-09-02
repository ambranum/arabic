#!/usr/bin/env python3
"""Select a Hebrew reading shelf from Project Ben-Yehuda -> texts/he/book-*.json.

Project Ben-Yehuda is 26,455 public-domain Hebrew works, and almost none of them are the Hebrew
this app teaches. That is the whole problem with the source and the reason this file measures
instead of browsing: the collection is early-twentieth-century literature, and its fables in
particular are biblical pastiche -- 45 vav-consecutive verbs per thousand words and 59-word
sentences, against the daily paper's 0 and 12. Shipping that under a spoken-Hebrew app because
it is free and real would be trading one kind of dishonesty for another.

So every text is scored against the app's own Hebrew before it is let in:

  * ARCHAIC markers per 1,000 words -- אשר as a relativizer, הנה, פן, טרם, אנכי, עתה.
  * VAV-CONSECUTIVE verbs per 1,000 -- ויאמר, ותלך. The single clearest tell; the paper has none.
  * average sentence length in words.

Measured medians, 120 texts per genre against the paper: fables 46.9 / 44.7 / 58.8, prose
27.2 / 9.3 / 14.7, drama 19.1 / 6.0 / 11.6, memoir 12.7 / 5.3 / 15.9 -- the paper 6.7 / 0.0 /
12.4. Drama and memoir are closest because they are dialogue and recollection, which is the
register this app is for. But the variance WITHIN a genre is larger than between genres, so the
gate is per text, not per genre.

And one more requirement, which turns out to matter more than any of them: the text must be
POINTED in the source. 32 of the 114 that pass the register gate are, and for those the vowels
on the page are Project Ben-Yehuda's, not ours -- the best provenance anywhere in the Hebrew
module, better than the news, where we derive them. Measured on 4,400 tokens of it: the source's
own pointing settles 51% of the ambiguity the annotator would otherwise have to send for
adjudication, taking a text from ~50% of tokens needing a decision to 29%.

    python3 pipeline/he_books.py --lang he              # what would be selected, and why
    python3 pipeline/he_books.py --lang he --write      # write texts/he/book-*.json
    export ANTHROPIC_API_KEY=...
    python3 pipeline/he_books.py --lang he --translate  # fill in the English
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys
import difflib
import shutil
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402
paths.require('he')

DUMP = os.path.join(paths.ROOT, 'spike', 'he', 'benyehuda')
ZIP = os.path.join(DUMP, 'txt.zip')
CAT = os.path.join(DUMP, 'pseudocatalogue.csv')

WORD = re.compile(r'[֐-׿]+(?:["\'׳״][֐-׿]+)*')
NIQQUD = re.compile('[֑-ׇ]')
# Function words that mark the older literary register. Deliberately only the ones a modern
# speaker would NOT use: כי and גם are on both sides of the line, so they are not here.
ARCHAIC = {'אשר', 'הנה', 'פן', 'לבלתי', 'בטרם', 'למען', 'אולם', 'אנכי', 'הלא', 'עתה', 'כה',
           'טרם', 'זולת', 'הללו', 'ויהי', 'לכן', 'אך'}
VAV_CONSEC = re.compile(r'\bו[֑-ׇ]*[ית][֐-׿֑-ׇ]{2,}')

# The gate. Roughly twice the paper's archaism and no vav-consecutive to speak of; a text that
# clears this reads like something a modern Israeli wrote, which is the point.
# Where to draw the line, measured rather than picked. Sweeping the three thresholds over the
# 546 pointed, in-range, de-duplicated texts:
#
#     gate (archaic/vav/sentence)   texts    words   median archaic / vav / sentence
#     12 /  2 / 15                     10    6,837        6.8 /  1.0 / 10.4
#     16 /  3 / 17                     21   14,959        9.3 /  1.5 / 11.3
#     20 /  4 / 19                     37   31,354       10.7 /  2.3 / 11.3
#     25 /  5 / 21                     67   70,544       11.7 /  3.4 / 11.6
#     30 /  6 / 24                     94  119,993       11.4 /  4.0 / 11.7
#     no gate                         546  718,175       18.5 / 17.1 / 15.2
#     the daily paper                            —        6.7 /  0.0 / 12.4
#
# The interesting column is the middle one. SENTENCE LENGTH barely moves across the whole range
# and stays under the paper's own 12.4 the entire way, so it is not what separates these texts.
# The vav-consecutive is: 1.0 at the tightest gate, 17.1 with no gate at all. So the gate is set
# where that count is still close to the paper's zero -- a thousand words of this shelf carries
# about two biblical narrative verbs -- and the shelf quadruples, from 6,837 words to 31,354.
#
# The numbers above were swept while clean() still let the archive's credit line and the footnote
# apparatus through, so every text was being scored on its prose PLUS about fourteen tokens of
# website. That chrome is modern, unpointed and carries no vav-consecutive, so it diluted every
# ratio by the same trick -- a bigger denominator over an unchanged count. Measured across the
# thirty-seven, dropping it moves the scores by a median ×1.025 archaic, ×1.022 vav, ×1.010
# sentence, and ×0.976 tokens. So the thresholds are restated in the units they are now measured
# in rather than loosened: the same line through the same texts, converted by what the chrome was
# worth. (It matters at the boundary. Five of the thirty-seven sat inside the old numbers only
# because the footer was padding them, and would have fallen off the shelf on a unit change.)
MAX_ARCHAIC, MAX_VAV, MAX_SENTENCE = 20.5, 4.1, 19.2
MIN_POINTED = 0.90                       # the source's own vowels, or it is not this shelf
MIN_TOKENS, MAX_TOKENS = 290, 6000
GENRES = {'prose', 'drama', 'memoir'}

# Difficulty, and it is measured rather than judged: how long the sentences are and how much of
# the text is words the reader has already met by that phase. Bands are the app's own.
# Which shelf a text lands on, by how far its register is from the daily paper's. This was the
# average sentence length alone, and at ten texts that was fine because the shelf was short
# enough to read in order. At thirty-seven it is not: sentence length turns out to be the axis
# these texts vary LEAST on, so it filed חֲבֵרִים -- the second most archaic thing here -- as
# beginner reading on the strength of its short sentences.
#
# The vav-consecutive is weighted triple because the paper has exactly none of it, so every one
# is a reading the app teaches nowhere else; sentence length counts only what it has over the
# paper's own 12.4.
BANDS = [(11.0, 'beginner', 1), (20.0, 'intermediate', 2), (999.0, 'advanced', 3)]

# Where each shelf sits in the Books section's running order -- a different number from the key
# above, which names the shelf. The graded readers this project writes (pipeline/he_book_*.py)
# take 1-2, 10-14 and 20-21 inside their bands, and Ben-Yehuda comes after them in each: a
# retelling built for a learner is the way IN to a level, and published literature that was
# never adjusted for anyone is what you read once you are there.
ORDER = {1: 5, 2: 15, 3: 25}

# One book per shelf, not one book for the whole library. These are thirty-seven standalone works
# by twelve authors -- Ben-Yehuda is an archive, not an anthology someone edited -- so there is no
# volume they all belong to. Filing them under a single `book` made the Books section show one
# 37-chapter title, and because a book takes its level from its first chapter, the whole thing sat
# under Beginner with a difficulty banner describing only עָפְרָה וְהַבֻּבָּה שֶׁלָּהּ.
#
# Grouping by author was the other candidate and it is what a library looks like, but an author
# here spans the bands -- דושמן alone runs beginner to advanced -- and a book with one level chip
# and one register banner cannot describe that honestly. The shelf already IS the unit the app
# grades by, so it becomes the book: three volumes, each level-uniform, each banner true of every
# chapter in it. The Arabic side works the same way -- a book there is a collection with one level.
SHELVES = {
    1: ('benyehuda-1', {'ar': 'הַמַּדָּף הָרִאשׁוֹן', 'en': 'The first shelf'}),
    2: ('benyehuda-2', {'ar': 'הַמַּדָּף הַשֵּׁנִי', 'en': 'The second shelf'}),
    3: ('benyehuda-3', {'ar': 'הַמַּדָּף הַשְּׁלִישִׁי', 'en': 'The third shelf'}),
}

# The dump gives a Hebrew title and nothing else, and `title.en` was being filled with that same
# Hebrew -- so every card in the Books list, and every reader header, printed Hebrew in the slot
# the English belongs in. These are ours, translated the way the sentences were, and they are
# written down rather than generated per run so a rebuild cannot quietly retitle the shelf.
TITLES_EN = {
    'book-by-11478': 'Ofra and Her Doll',
    'book-by-11485': 'The Riddle',
    'book-by-11497': 'The Broken Windowpane',
    'book-by-11498': 'Chicks',
    'book-by-11499': 'Returning What Was Lost',
    'book-by-11500': 'Havhava and Meah',
    'book-by-11502': 'On Passover Eve',
    'book-by-11503': 'Patience',
    'book-by-11504': 'In Honour of Rabbi Shimon bar Yochai',
    'book-by-11505': 'Friends',
    'book-by-11506': 'Lela',
    'book-by-11513': "Little Naomi's Appetite",
    'book-by-11517': 'The Change of Name',
    'book-by-11518': 'On Lag BaOmer',
    'book-by-11519': 'In Class',
    'book-by-20271': 'The Caravan',
    'book-by-20919': 'The Hidden Face',
    'book-by-23823': "Racheli's Wonderful Shoes",
    'book-by-24301': 'Little Naomi',
    'book-by-29717': 'We Are in the Movement',
    'book-by-30778': 'The Festival of Our Freedom',
    'book-by-30780': 'The First of May',
    'book-by-30782': 'How Shall We Welcome the Immigrants?',
    'book-by-30784': 'The Odessa Committee',
    'book-by-30793': 'The Children in Cyprus',
    'book-by-39948': 'Chapter Two: The Mysteries of the Lime Kiln',
    'book-by-40622': 'The Standard-Bearer',
    'book-by-44547': 'The Worm and the Crane',
    'book-by-46040': 'The Buyer of Oxen',
    'book-by-46211': 'The Talking Talisman',
    'book-by-46212': 'The Decree of the Barrel',
    'book-by-52536': 'Nashkan the Dog and His Tail',
    'book-by-53622': 'The Tale of the Goat That Went Up the Mountain',
    'book-by-59045': "King Solomon's Three Students",
    'book-by-59077': 'Clever Dan',
    'book-by-62450': 'The Chinese',
    'book-by-64290': 'A Hero and a Sage Before His Wife',
}


def distance(s):
    """How far this text's register is from the daily paper's. 0 is the paper."""
    return s['archaic'] + 3 * s['vav'] + max(0.0, s['sentence'] - 12.4)


# What the page carries that the story does not. Every transcription ends with the archive's own
# credit line, and the shelf was reading it as the last sentence of the book: all thirty-seven
# chapters closed on "the text(s) above were produced by the volunteers of the Ben-Yehuda Project
# on the internet", translated into English at the API's expense and, in twenty-five of them, read
# aloud in the Hebrew voice. It is also where the single most common unresolved word in the whole
# corpus came from -- לעיל, thirty-seven times, once per book, never once in a story.
#
# Above it sit the apparatus lines: the scanned illustration's filename, the illustrator's credit,
# and the footnote glossary, whose entries the sentence splitter glued onto the last real sentence
# ("...that he might get hungry… Ivy — a kind of plant with many leaves").
CREDIT = re.compile(r'את הטקסט\[ים\] לעיל|הכל זמין תמיד בכתובת|benyehuda\.org/read/')
APPARATUS = re.compile(r'↩︎|\.(?:jpg|jpeg|png|gif)\b|^\s*א?יור\s*:|^\s*האיור\s*:')


def clean(text, title=''):
    """The dump is a transcription, not a data file: it keeps the page's own line breaks, its
    tabs, and its title line. Sentences have to be found in prose, so the layout goes first."""
    t = text.replace('\u00a0', ' ').replace('&nbsp;', ' ')
    t = re.sub(r'[ \t]*\n[ \t]*', '\n', t)
    t = re.sub(r'\n{2,}', '\n\n', t).strip()
    lines = [x for x in t.split('\n') if x.strip()]
    # the transcription repeats the title, and often the author under it
    head = NIQQUD.sub('', title).strip()
    while lines and (NIQQUD.sub('', lines[0]).strip() == head or len(WORD.findall(lines[0])) <= 3):
        lines.pop(0)
    # everything from the archive's credit line down is the website, not the book
    for i, x in enumerate(lines):
        if CREDIT.search(x):
            lines = lines[:i]
            break
    lines = [x for x in lines if not APPARATUS.search(x)]
    return re.sub(r'\s+', ' ', ' '.join(lines)).strip()


def score(text):
    toks = WORD.findall(text)
    if not toks:
        return None
    sents = [s.strip() for s in re.split(r'(?<=[.!?׃])\s+', text) if len(WORD.findall(s)) > 2]
    if not sents:
        return None
    return {
        'tokens': len(toks),
        'pointed': sum(1 for w in toks if NIQQUD.search(w)) / len(toks),
        'archaic': 1000 * sum(1 for w in toks if NIQQUD.sub('', w) in ARCHAIC) / len(toks),
        'vav': 1000 * len(VAV_CONSEC.findall(text)) / len(toks),
        'sentence': statistics.mean(len(WORD.findall(s)) for s in sents),
        'sentences': sents,
    }


def passes(s):
    return (s and MIN_TOKENS <= s['tokens'] <= MAX_TOKENS and s['pointed'] >= MIN_POINTED
            and s['archaic'] <= MAX_ARCHAIC and s['vav'] <= MAX_VAV
            and s['sentence'] <= MAX_SENTENCE)


def band(s):
    d = distance(s)
    for cutoff, name, shelf in BANDS:
        if d <= cutoff:
            return name, shelf
    return BANDS[-1][1], BANDS[-1][2]


def slug(mid):
    return 'book-by-%s' % mid


# The one thing here that is not measurement. A translation of a public-domain text is a much
# weaker claim than writing the Hebrew would be -- the Hebrew is Project Ben-Yehuda's, verbatim,
# and only the English is ours -- but it IS ours, and the artifact says so per text.
MODEL = "claude-opus-4-8"
BATCH = 25
TRANSLATE_SCHEMA = {
    "type": "object",
    "properties": {"lines": {"type": "array", "items": {"type": "object", "properties": {
        "i": {"type": "integer"}, "en": {"type": "string"}},
        "required": ["i", "en"], "additionalProperties": False}}},
    "required": ["lines"], "additionalProperties": False,
}
PROMPT = (
    "Below are numbered sentences from a Hebrew short story, published before 1950 and now in "
    "the public domain. Translate each into natural, plain English.\n\n"
    "Rules that matter more than elegance:\n"
    "- One English sentence per numbered Hebrew one, same number. Do not merge or split.\n"
    "- Say what the Hebrew says. Do not add detail it does not contain, and do not drop detail "
    "it does — a reader is going to check the English against the Hebrew word by word.\n"
    "- Keep it readable for a learner: everyday words, present-day English, no archaism to "
    "match the Hebrew's age.\n"
    "- Dialogue stays dialogue, with its quotation marks.\n\n")


def translate(paths_glob):
    import net
    c = net.need('anthropic').Anthropic()
    for f in sorted(paths_glob):
        d = json.load(open(f, encoding='utf-8'))
        todo = [i for i, s in enumerate(d['sentences']) if not s.get('en')]
        if not todo:
            print('  %-28s already done' % os.path.basename(f))
            continue
        print('  %-28s %d sentences' % (os.path.basename(f), len(todo)))
        for k in range(0, len(todo), BATCH):
            chunk = todo[k:k + BATCH]
            body = PROMPT + '\n'.join('%d. %s' % (i, d['sentences'][i]['ar']) for i in chunk)
            r = c.messages.create(
                model=MODEL, max_tokens=8000, thinking={"type": "adaptive"},
                output_config={"effort": "high",
                               "format": {"type": "json_schema", "schema": TRANSLATE_SCHEMA}},
                messages=[{"role": "user", "content": body}])
            got = json.loads(next(b.text for b in r.content if b.type == 'text'))['lines']
            want = set(chunk)
            for line in got:
                if line['i'] in want and line['en'].strip():
                    d['sentences'][line['i']]['en'] = line['en'].strip()
            missing = [i for i in chunk if not d['sentences'][i]['en']]
            if missing:
                print('     !! %d of %d came back empty' % (len(missing), len(chunk)))
        d['translation'] = 'English by Claude — the Hebrew is Project Ben-Yehuda\'s, verbatim'
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        left = sum(1 for s in d['sentences'] if not s.get('en'))
        print('     %d/%d translated%s' % (len(d['sentences']) - left, len(d['sentences']),
                                           '' if not left else '  (%d still empty)' % left))


def realign(stored, fresh):
    """Carry the English across a re-extraction. -> (sentences, fresh index -> stored index).

    A translated sentence is worth keeping: the English cost an API call and a person may have
    read it. But it is only worth keeping ON THE SAME SENTENCE, so the two lists are aligned and
    the English travels with the Hebrew it was written for. Anything the alignment does not
    match comes back empty and translate() fills it in on the next run.
    """
    sm = difflib.SequenceMatcher(a=[x['ar'] for x in stored], b=fresh, autojunk=False)
    src = {}
    for tag, i1, _i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(j2 - j1):
                src[j1 + k] = i1 + k
    out = []
    for j, ar in enumerate(fresh):
        old = stored[src[j]] if j in src else {}
        out.append({'ar': ar, 'en': old.get('en', ''), 'p': j // 3})
    return out, src


def move_clips(tid, src, n):
    """Renumber a text's audio to follow its sentences. -> (kept, dropped).

    Clips are named for the POSITION they read -- s0.mp3, s1.mp3 -- so a sentence that moves
    leaves its clip behind on a sentence it does not say. Dropping a line from the middle of a
    chapter would silently shift every clip after it onto the wrong words, and the reader would
    hear it before anyone saw it. So the clips are moved with the sentences, and any clip whose
    sentence no longer exists, or whose words changed, is deleted rather than reused: under a
    non-deterministic voice a re-synthesis is the only honest way to get it back.
    """
    d = paths.build(tid, 'audio')
    if not os.path.isdir(d):
        return 0, 0
    have = {i: os.path.join(d, 's%d.mp3' % i) for i in range(4096)
            if os.path.exists(os.path.join(d, 's%d.mp3' % i))}
    tmp = d + '.new'
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    kept = 0
    for j in range(n):
        i = src.get(j)
        if i is not None and i in have:
            shutil.copy2(have[i], os.path.join(tmp, 's%d.mp3' % j))
            kept += 1
    shutil.rmtree(d)
    os.rename(tmp, d)
    # app/ holds a copy per clip and build_app.py only ever adds to it, so a stale name would
    # outlive the clip it was copied from and go on being served.
    shutil.rmtree(paths.audio(tid), ignore_errors=True)
    return kept, len(have) - kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='write texts/he/book-*.json')
    ap.add_argument('--max', type=int, default=0, help='cap how many are written')
    ap.add_argument('--translate', action='store_true',
                    help='fill in the English (needs ANTHROPIC_API_KEY)')
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.translate:
        import glob
        return translate(glob.glob(paths.texts('book-by-*.json'))) or 0
    if not os.path.exists(ZIP):
        raise SystemExit('!! no %s\n   Download txt.zip and pseudocatalogue.csv from\n'
                         '   github.com/projectbenyehuda/public_domain_dump/releases into %s'
                         % (ZIP, DUMP))

    cat = {r['ID']: r for r in csv.DictReader(open(CAT, encoding='utf-8'))}
    z = zipfile.ZipFile(ZIP)
    kept, seen_titles = [], set()
    for n in z.namelist():
        if not n.endswith('.txt'):
            continue
        mid = n.rsplit('/m', 1)[-1][:-4]
        c = cat.get(mid)
        if not c or (c.get('genre', '') or '').rsplit('.', 1)[-1] not in GENRES:
            continue
        s = score(clean(z.read(n).decode('utf-8', 'replace'), c['title']))
        if not passes(s):
            continue
        key = (c['title'].strip(), c['authors'].strip())
        if key in seen_titles:                 # the dump carries a few duplicate transcriptions
            continue
        seen_titles.add(key)
        kept.append((mid, c, s))

    kept.sort(key=lambda t: t[2]['sentence'])
    print('%d texts clear the register gate and are pointed in the source\n' % len(kept))
    print('%-34s %-20s %-13s %5s %6s %5s %5s' %
          ('title', 'author', 'level', 'tok', 'arch', 'vav', 'sent'))
    written = 0
    # Chapters are numbered within their own shelf now, and the counter has to advance for
    # every text that KEEPS its number -- including one left alone below -- or two chapters
    # end up sharing one.
    chap = {k: 0 for k in SHELVES}
    for mid, c, s in kept:
        name, shelf = band(s)
        chap[shelf] += 1
        print('%-34s %-20s %-13s %5d %6.1f %5.1f %5.1f'
              % (c['title'][:34], c['authors'][:20], name, s['tokens'],
                 s['archaic'], s['vav'], s['sentence']))
        if not a.write or (a.max and written >= a.max):
            continue
        # A translated text keeps its SENTENCES. The English cost an API call and the audio is
        # keyed by sentence index, so a reorder would silently re-point every clip at a
        # different sentence.
        #
        # Its metadata is another matter, and used to be frozen with it. That was fine while the
        # shelf was ten texts written in one go; it is not now, because widening the gate
        # rebands and renumbers the whole shelf, and a text that skipped the rewrite would keep
        # a chapter number another text had just been given. So the doc is rebuilt either way
        # and the old sentences are dropped back into it -- but only if they are the same
        # sentences. If the dump or clean() ever produces a different list, the file is left
        # exactly as it is and says so, because at that point the clips no longer line up and
        # that is not something to paper over.
        if slug(mid) not in TITLES_EN:
            print('   !! no English title for %s — the Hebrew stands in until one is '
                  'written into TITLES_EN' % slug(mid))
        out_path = paths.texts('%s.json' % slug(mid))
        keep_sentences = keep_translation = None
        if os.path.exists(out_path):
            done = json.load(open(out_path, encoding='utf-8'))
            if any(x.get('en') for x in done.get('sentences', [])):
                fresh = [t.strip() for t in s['sentences']]
                stored = done['sentences']
                # translate() stamps this on the way past. It is a claim about who wrote the
                # English, so it belongs to the text and not to whichever step last touched it.
                keep_translation = done.get('translation')
                if [x['ar'] for x in stored] == fresh:
                    keep_sentences = stored
                else:
                    keep_sentences, src = realign(stored, fresh)
                    kept, gone = move_clips(slug(mid), src, len(fresh))
                    lost = sum(1 for x in keep_sentences if not x['en'])
                    print('   re-extracted: %d sentences -> %d, %d to re-translate, '
                          '%d clips kept, %d dropped'
                          % (len(stored), len(fresh), lost, kept, gone))
        doc = {
            'id': slug(mid), 'kind': 'book-chapter', 'dialect': 'he', 'level': name,
            'shelf': ORDER[shelf], 'book': SHELVES[shelf][0], 'chapter': chap[shelf],
            # `ar` is the target script whatever the language, the same as every other text
            # in the repo -- renaming it per language would fork every reader in the app.
            'title': {'ar': c['title'], 'en': TITLES_EN.get(slug(mid)) or c['title']},
            'book_title': dict(SHELVES[shelf][1]),
            'book_meta': {'work': c['title'], 'author': c['authors'],
                          'year': '', 'status': 'public domain — Project Ben-Yehuda volunteers',
                          'url': 'https://benyehuda.org' + (c.get('path') or '')},
            # Not "adapted by Claude". Every sentence is as Project Ben-Yehuda transcribed it,
            # vowels included, and the register numbers that let it in are on the record.
            'source': 'Project Ben-Yehuda — public domain, verbatim',
            'register': {'archaic_per_1k': round(s['archaic'], 1),
                         'vav_consecutive_per_1k': round(s['vav'], 1),
                         'avg_sentence_words': round(s['sentence'], 1),
                         'pointed': round(s['pointed'], 3)},
            # Three sentences to a paragraph, not six. Pointed Hebrew is set large -- it has
            # to be, the vowels are small -- so six sentences is a wall, and a wall does not
            # sit beside its translation: the English is a short block against a column six
            # times its height.
            'sentences': keep_sentences or [{'ar': t.strip(), 'en': '', 'p': i // 3}
                                            for i, t in enumerate(s['sentences'])],
        }
        if keep_translation:
            doc['translation'] = keep_translation
        if keep_sentences:
            print('   (translated already — sentences kept, %s ch.%d)' % (name, chap[shelf]))
        json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        written += 1
    if a.write:
        print('\nwrote %d -> %s' % (written, os.path.relpath(paths.texts(''), paths.ROOT)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
