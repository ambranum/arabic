#!/usr/bin/env python3
"""Annotate Hebrew sentences against the lexicon -> build/he/<id>/text.json.

The Hebrew counterpart of pipeline/ingest.py, and it does the same job under the same rule:
every word's metadata is RETRIEVED from a licensed lexicon, never generated. What differs is
which half is hard.

For Arabic the pronunciation is looked up per entry and the VOCALIZATION has to be derived --
pipeline/vocalize.py exists for that, and only 46% of words get their vowels straight from
Maknuune. Hebrew is the mirror image: Israelis write unpointed, the lexicon's forms are pointed,
and pointing IS the disambiguation. Choosing the right entry for מלך decides between מֶלֶךְ
"king" and מָלַךְ "he reigned" -- so this file's one real decision, which entry a surface form
belongs to, hands the app the pointing, the pronunciation, the gloss and the root at once.

That is also why the ambiguity rate is higher than Arabic's: A1 measured 49.9% of Hebrew tokens
matching more than one lemma against 32.5% for Arabic. Those go to the same place they go on the
Arabic side -- a resolution queue that picks from REAL candidates and can never invent one.

    python3 pipeline/he_ingest.py texts/he/news-2026-08-30.json [--audio]
"""
import argparse
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths          # noqa: E402

# Before the heavy imports: the lexicon this needs is Hebrew's, and loading it to then discover
# we are running as Arabic wastes the time and buries the message.
paths.require('he')
from voice import language_code, model_id, voice_id   # noqa: E402
from build_lex import he_norm                          # noqa: E402
import he_curated                                      # noqa: E402
from lex import Lexicon                                # noqa: E402
from phon import NIQQUD, respell, unpoint              # noqa: E402

RESOLUTIONS = paths.resolutions()

import net           # noqa: E402  -- one HTTPS context, one diagnosis
_SSL = net.SSL_CTX

# MATCH the words rather than splitting on the gaps, because in Hebrew the same character is
# both punctuation and part of a word. A gershayim before the last letter makes an acronym --
# צה"ל, ח"כ, ארה"ב, השב"כ, all everyday news vocabulary -- and a geresh makes a foreign sound
# (ג'ורג'). Splitting on the quote shredded them: השב"כ became שב + כ, which the annotator then
# pointed as שָׁב "returned" and shipped that way. Israelis write these with an ASCII " as often
# as with ״, so both are accepted, and a quote that is NOT between letters still separates.
# The Hebrew block is not all letters. \u0590-\u05FF also holds the MAQAF (־), which is a
# hyphen: בֶּן־יְהוּדָה is two words joined, the way "well-known" is, and no lexicon has an entry
# for the pair. Matching it as part of a word made 149 compounds unresolvable in one stroke --
# בֶּן־יְהוּדָה itself 37 times, חוֹבְבֵי־צִיּוֹן, בְּאֶרֶץ־יִשְׂרָאֵל, כִּי־אִם, לְאַט־לְאַט -- and
# left the bare ־ standing in the text as a word of its own. So the class is spelled out: the
# letters, and the marks that belong to a letter. Everything else in the block is punctuation
# and separates, exactly as a space does. The reader puts it back on the page either way -- it
# prints whatever lies between one word and the next, verbatim.
LETTER = r'[\u05D0-\u05EA\u05EF-\u05F2]'
MARK = r'[\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]'      # niqqud, cantillation, dots
# The trailing geresh is PART OF THE WORD. A geresh after the last letter is how Hebrew writes
# the sounds its alphabet does not have -- ג׳ for j, צ׳ for ch, ז׳ for zh -- so ג׳ורג׳ "George"
# ends in one, and without the optional tail below the regex stopped at the last letter and
# handed back ג׳ורג. The word then missed its own entry, which is why pipeline/he_curated.py
# carries a second, truncated key for every such name. Only the geresh and the apostrophe people
# type for it are allowed to trail: a gershayim or a double quote in that position is a closing
# quotation mark, and "שלום" has to keep coming back as שלום.
WORD = re.compile(r'(?:%(l)s%(m)s*)+(?:["\'\u05F3\u05F4](?:%(l)s%(m)s*)+)*[\'\u05F3]?'
                  % {'l': LETTER, 'm': MARK})
_ACRONYM = re.compile(r'^(%(l)s%(m)s*)?["\u05F4]((?:%(l)s%(m)s*){2,})$'
                      % {'l': LETTER, 'm': MARK})


def tokenize(sent):
    out = []
    for tok in WORD.findall(sent.strip()):
        # A gershayim BEFORE THE LAST LETTER makes an acronym -- צה"ל, ד"ר, תנ"ך, ל"ג -- and the
        # regex keeps those whole on purpose. But Israelis type the same character as an ordinary
        # quotation mark, and when the quoted word carries a proclitic the opening quote lands
        # between two letters and is swallowed with them: בַּ"חֶדֶר was one token, and so was
        # בְּ"גוּלִים. What separates the two is which side the letters are on. An acronym is
        # mostly before the mark; a quotation is a particle before it and a whole word after.
        m = _ACRONYM.match(tok)
        if m:
            if m.group(1):
                out.append(m.group(1))
            out.append(m.group(2))
        else:
            out.append(tok)
    return out


SCOPED = '@texts'      # reserved key in the trail: id-prefix -> {surface: lexicon id}


def load_resolutions(text_id=None):
    """The adjudication trail, flattened for one text.

    A homograph's reading is a property of the CONTEXT, not of the corpus, and one global map
    from surface to lexicon id cannot say that. חמור is the case that proved it: in the daily
    paper it is חָמוּר "serious", and in forty tales of ג'וחא it is the donkey, in nearly every
    one of them. Whichever answer the global line gives is wrong for the other half of the
    corpus, and it was wrong on the first sentence of the first book.

    So the file may also carry an "@texts" section, keyed by an id PREFIX, and those lines win
    for texts whose id starts with it. Prefixes are applied shortest-first so a longer, more
    specific one has the last word. Everything else is unchanged: each line still names a real
    lexicon id, and he_ingest still refuses one that is not a reading of the word on the page.
    """
    if not os.path.exists(RESOLUTIONS):
        return {}
    raw = json.load(open(RESOLUTIONS, encoding='utf-8'))
    scoped = raw.pop(SCOPED, {}) or {}
    if not text_id:
        return raw
    for prefix in sorted(scoped, key=len):
        if text_id.startswith(prefix):
            raw.update(scoped[prefix])
    return raw


def _word(rec, surface, prov, cut='', voc=None):
    """One lexicon record, in the record shape app.js reads.

    The field names are the Arabic pipeline's and stay that way on purpose: they are what the
    word card, the deck and the lexicon index already read, and `caphi`/`maknuune_id` mean "the
    pronunciation" and "the lexicon's id for this" rather than anything Arabic. Renaming them
    would migrate live study data for no visible gain.
    """
    # WHAT IS SHOWN MUST BE WHAT WAS WRITTEN. The lexicon points ktiv haser and Israelis write
    # ktiv male, so the entry's spelling and the word on the page are different strings --
    # עֲדַיִן against עדיין, בִּמְיֻחָד against במיוחד -- and the reading view displays the
    # vocalized field in place of the surface. Printing the entry's letters there does not just
    # drop the reader's: a skeleton match ignores every vav and yod, so ביניהם "among them" was
    # displayed as בְּנֵיהֶם "their sons" and פוטין as פוֹטוֹן "photon". respell() puts the
    # lexicon's vowels on the letters that were actually written, and returns nothing at all
    # when the entry cannot spell them -- in which case no vocalization is claimed, exactly as
    # for a clitic match.
    # A POINTED SOURCE OUTRANKS EVERYTHING. Project Ben-Yehuda's texts arrive with their vowels
    # already on them, put there by the people who transcribed the book, and no derivation of
    # ours improves on that -- not the lexicon's spelling moved across, and certainly not a
    # refusal. When the caller has such a source it passes it in, and the clitic guard does not
    # apply: the particle was pointed too, by the same hand.
    voc = voc or (None if cut else respell(surface, rec['FORM']))
    w = {
        'surface': surface,
        # Pointed, and the same value the verb module banks a card under, so a word met in the
        # news and a verb met in the Verbs section are ONE card rather than two.
        'lemma': rec['LEMMA'],
        'form': rec['LEMMA'],
        # POINTING IS ONLY CLAIMED FOR THE WHOLE WORD. When the match came by cutting a
        # proclitic, the lexicon has pointed the STEM and nothing has pointed the particle --
        # and the particle's own vowel depends on what follows it (בְּ / בַּ / בָּ). Writing the
        # stem's pointing back over the whole word does not just lose a letter, it changes the
        # text: בבית "in the house" was being displayed as בַּיִת "house", and שהשיחות as
        # שִׂיחוֹת. So the gloss, root and lemma are kept -- they are what the card is for -- and
        # the vocalization is refused, exactly as the Arabic side refuses what it cannot derive
        # honestly. The reader falls back to the surface, unpointed, which is at least true.
        'vocalized': voc,
        # The source's own pointing is named FIRST, before the clitic rule: that rule exists
        # because nothing had pointed the particle, and here something has.
        'vocalized_from': ('source:pointed' if voc == surface
                           else 'unvocalized:clitic' if cut
                           else 'unvocalized:no-alignment' if not voc
                           else 'lexicon' if unpoint(rec['FORM']) == unpoint(surface)
                           else 'derived:ktiv'),
        'root': rec['ROOT'] or None,
        'gloss': rec['GLOSS'] or None,
        'analysis': rec['ANALYSIS'] or None,
        'caphi': rec['PHON'] or None,
        'caphi_urban': rec['PHON'] or None,
        'caphi_raw': None,
        'maknuune_id': rec['ID'],
        'provenance': prov,
    }
    if cut:
        w['_cut'] = cut
    return w


def _blank(surface):
    return {'surface': surface, 'lemma': None, 'form': surface, 'vocalized': None,
            'vocalized_from': 'unvocalized:no-entry', 'root': None, 'gloss': None,
            'analysis': None, 'caphi': None, 'caphi_urban': None, 'caphi_raw': None,
            'maknuune_id': None, 'provenance': 'unresolved'}


def annotate(lex, surface, res):
    key = he_norm(surface)
    # When the text itself is pointed, the pointing is EVIDENCE, and the strongest kind there
    # is: pointing is what tells מלך "king" from מלך "he reigned". So before anything is sent
    # for a decision, the candidates are asked whether they can spell what is on the page.
    # Measured over the whole Ben-Yehuda shelf: it settles 52% of the ambiguity, and takes the
    # share of tokens needing an adjudicator from 62% to 30%.
    pointed = surface if any(c in NIQQUD for c in surface) else None
    # `cut` is what the peeler had to remove to find this word, and it belongs to the word
    # whichever branch answers. Reading it only on the unresolved path meant a resolution
    # silently re-enabled the thing the clitic guard exists to stop: בכמה "in a few" was
    # displayed as כַּמָּה, שהרכב as רֶכֶב. An adjudicated word is not a differently-shaped word.
    recs, _, cut = lex.look(surface)
    want = res.get(surface) or res.get(key)
    if want:
        pick = lex.by_id.get(str(want))
        # The cut is derived from the entry that was CHOSEN, not from the one the lookup
        # happened to find first. A word can match the lexicon exactly and still be adjudicated
        # to a prefix reading -- שקרה is an exact match for שִׁקְּרָה "she lied" where the
        # sentence means ש- + קָרָה "that happened" -- and when it is, the pointing has to go
        # for the usual reason: the lexicon pointed the stem, nothing has pointed the particle.
        cut_p = lex.cut_for(key, pick) if pick is not None else None
        if cut_p is not None:
            return _word(pick, surface, 'wiktionary:resolved', cut_p, voc=pointed)
        if pick is not None:
            # A real entry that is no reading of this word. Ids outlive the text they were
            # picked for, so this is what a stale or mistyped trail line looks like, and
            # applying it would put a stranger's pointing and gloss on the page.
            print('  !! %s: resolution %s is not a reading of this word — ignored'
                  % (surface, want))
    # BEFORE the lexicon, which is where pipeline/ingest.py has always consulted the Arabic one.
    # It was last here, on the theory that a curated entry must never shadow a real one -- and
    # that theory fails on exactly the words the table exists for. A name is a homograph of an
    # ordinary word often enough that the lexicon answers it CONFIDENTLY and wrongly: מַנְסוּר
    # came back as נִסֵּר "to saw". A fallback can never reach those, because nothing failed.
    # What keeps this safe is not the ordering but the table: names and closed-class function
    # words only, written down one at a time, each marked `curated:*` on the page.
    c = he_curated.lookup(surface, key)
    if c is None:
        # `pre_cut`, NOT `cut`. This loop used to bind the peeler's own variable, so by the time
        # it fell through -- which it does for almost every word, because almost no word is a
        # curated name -- `cut` no longer held what lex.look() found. It held the LAST stem the
        # peeler could imagine, 'ש-ה' for שקרה, for any word whose first letter can be a
        # particle. Two things then went wrong at once, and both of them silently. _word() reads
        # cut as "this matched by cutting a proclitic" and refuses to point the word, so exact
        # matches came out unpointed and stamped unvocalized:clitic. And the alt-readings branch
        # below is guarded by `if not cut`, so the one place that offers ש- + קָרָה beside
        # שִׁקְּרָה never ran, and the adjudicator was never shown the reading the sentence meant.
        for stem, pre_cut in lex.stems(key)[1:]:
            # PREFIXES ONLY. A name takes particles in front of it -- לְג'וּחָא, מִפּוֹג,
            # שֶׁפַּסְפַּרְטוּ -- and nothing behind it: Hebrew's suffixes are possessives and
            # feminine endings, and a borrowed name does not inflect for either. Reaching the
            # curated table through a stripped SUFFIX is therefore always a coincidence, and
            # because this table is consulted before the lexicon, a coincidence here does not
            # merely fail to help -- it overwrites a correct answer. It did: the peeler cut
            # הַסְּנֶה, the burning bush of the midrash, down to סנ, which is he_norm's spelling
            # of סָן as in San Francisco, and six sentences of Ben-Yehuda were annotated with a
            # Californian city. cut is 'prefix-suffix'; anything after the dash disqualifies it.
            if pre_cut.split('-', 1)[-1]:
                continue
            c = he_curated.lookup(stem)
            if c is not None:
                # Same refusal as any clitic match: the entry points the STEM, and nothing has
                # pointed the particle in front of it.
                c['surface'], c['_cut'] = surface, pre_cut
                c['vocalized'], c['vocalized_from'] = None, 'unvocalized:clitic'
                break
    if c is not None:
        if pointed:                            # the publisher's vowels outrank ours, as always
            c['vocalized'], c['vocalized_from'] = pointed, 'source:pointed'
        return c

    rec, prov, cands = lex.resolve(surface)
    if rec is None:
        return _blank(surface)
    if pointed:
        fit = [c for c in cands if lex.spells(pointed, c) is not None]
        if len(fit) == 1:
            rec, cands = fit[0], fit
            prov = 'wiktionary:pointed'
        elif fit:
            rec, cands = fit[0], fit
        cut = lex.spells(pointed, rec) or cut
    w = _word(rec, surface, prov, cut, voc=pointed)
    if prov == 'AMBIGUOUS-needs-resolution':
        # A Hebrew word can be BOTH a word and a prefix plus a different word, and the exact
        # match wins before the peeler ever runs. שבו is the verb שָׁבוּ "they returned" and it
        # is ש- + בו "in which"; השבת is הֵשַׁבְתָּ "you returned" and ה- + שבת "the Sabbath". The
        # adjudicator was only ever shown the first reading, so it could not choose the second
        # however much context it had. Offer both.
        extra = []
        if not cut:
            for pre, stem, alt in lex.alt_readings(key, recs, strict=False):
                extra += [(r, pre + '-') for r in lex.readings(alt)[:2]]
        # And the same for the other spelling. An entry whose headword is written defectively is
        # filed under the defective key, so the full spelling in front of us never reached it:
        # גינה saw only the verb "to denounce", never the noun "a garden" that is what the
        # sentence meant. The reading is offered under the pointing the entry can actually give
        # this surface -- גִּינָּה, not the entry's own גִּנָּה -- because that is what the app
        # will print if it is chosen.
        ktiv = [] if cut else lex.ktiv_readings(key, recs)
        w['options'] = [{'id': str(c['ID']), 'root': str(c['ROOT'] or ''),
                         'gloss': str(c['GLOSS'] or '')[:60],
                         'analysis': str(c['ANALYSIS'] or ''),
                         'pointed': c['FORM']} for c in cands]
        w['options'] += [{'id': str(r['ID']), 'root': str(r['ROOT'] or ''),
                          'gloss': ('as %s + %s: ' % (c2, r['LEMMA'])) + str(r['GLOSS'] or '')[:44],
                          'analysis': str(r['ANALYSIS'] or ''),
                          'pointed': r['FORM']} for r, c2 in extra[:4]]
        w['options'] += [{'id': str(r['ID']), 'root': str(r['ROOT'] or ''),
                          'gloss': ('as %s spelled full: ' % r['LEMMA']) + str(r['GLOSS'] or '')[:40],
                          'analysis': str(r['ANALYSIS'] or ''),
                          'pointed': respell(surface, r['FORM']) or r['FORM']}
                         for r in lex.readings(ktiv)[:3]]
        # What the adjudicator is really choosing for. Without this it saw WORD: שבו and a list
        # of entries for the STEM, with nothing to say that ש- had been removed -- so it picked
        # a good entry for בו and returned שָׁבוּ "they returned" for a word meaning "in which".
        if cut:
            w['_cut_for_prompt'] = cut
    return w


def tts(text, out_path, api_key):
    if os.path.exists(out_path):
        return True, 'cached', None
    body = {'text': text, 'model_id': model_id()}
    lc = language_code()
    if lc:
        body['language_code'] = lc
    req = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s' % voice_id(),
        data=json.dumps(body).encode(),
        headers={'xi-api-key': api_key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120, context=_SSL) as r:
            open(out_path, 'wb').write(r.read())
        return True, 'generated', None
    except urllib.error.HTTPError as e:
        return False, 'HTTP %s — %s' % (e.code, e.read().decode('utf-8', 'replace')[:150]), e
    except Exception as e:
        return False, str(e)[:120], e


def ingest(lex, source, do_audio, key, quiet=False):
    """One text -> build/he/<id>/text.json. Returns 0, or 1 if the artifact was refused.

    Takes the Lexicon rather than making one, because the shelf changed the scale this script
    runs at. Loading the lexicon costs about a second and a half; over four hundred texts that
    is ten minutes of loading the same file, which is most of a re-ingest.
    """
    src = json.load(open(source, encoding='utf-8'))
    if 'sentences' not in src:
        print('skip %s: not a sentence-text' % os.path.basename(source))
        return 0

    res = load_resolutions(src['id'])
    outdir = paths.build(src['id'])
    os.makedirs(os.path.join(outdir, 'audio'), exist_ok=True)

    art = {'id': src['id'], 'title': src['title'], 'dialect': src.get('dialect', 'he'),
           'kind': src.get('kind', 'lesson'), 'date': src.get('date'),
           'level': src.get('level'), 'book': src.get('book'), 'chapter': src.get('chapter'),
           'book_title': src.get('book_title'), 'shelf': src.get('shelf', 0),
           'book_meta': src.get('book_meta'), 'subdialect': None,
           # Why this text is on the shelf, measured (pipeline/he_books.py). It rides into the
           # library index -- every key except the sentences does -- so the book page can show
           # the numbers instead of asserting the claim.
           'register': src.get('register'), 'translation': src.get('translation'),
           'source': src.get('source', 'original'), 'sentences': []}

    stats = {}
    for si, s in enumerate(src['sentences']):
        words = [annotate(lex, w, res) for w in tokenize(s['ar'])]
        for w in words:
            stats[w['provenance']] = stats.get(w['provenance'], 0) + 1
        sent = {'ar': s['ar'], 'en': s['en'], 'p': s.get('p'), 'words': words, 'audio': None}
        ap_ = os.path.join(outdir, 'audio', 's%d.mp3' % si)
        # Adopt a clip that is already on disk whether or not this run can make new ones. Under
        # a non-deterministic model that is not just an optimization: re-synthesizing would give
        # a DIFFERENT reading of the same sentence, so a cached clip is the canonical one.
        if os.path.exists(ap_):
            sent['audio'] = 'audio/s%d.mp3' % si
        elif do_audio:
            ok, how, err = tts(s['ar'], ap_, key)
            sent['audio'] = 'audio/s%d.mp3' % si if ok else None
            print('  audio s%d: %s' % (si, how))
            # A book is 60-odd sentences, not the news's nine. A dead key or a spent balance
            # would otherwise print the same failure sixty times and then hand back an artifact
            # with no audio in it, which reads as a finished run.
            if err is not None and net.fatal(err, 'audio: ', how):
                # 2, matching daily_news: the caller's loop stops on it rather than trying the
                # next hundred texts against the same empty balance. ElevenLabs ran out 12
                # texts into the shelf and the loop worked through every remaining one.
                raise SystemExit(2)
        art['sentences'].append(sent)

    # The reading view displays `vocalized` in place of the surface, so a pointed form whose
    # letters are not the letters that were typed does not annotate the text, it rewrites it.
    # respell() makes that impossible one word at a time; this says so of the whole artifact,
    # because the failure is invisible on the page -- it just reads as a different word.
    rewrote = ['%s -> %s' % (w['surface'], w['vocalized'])
               for s in art['sentences'] for w in s['words']
               if w['vocalized'] and unpoint(w['vocalized']) != unpoint(w['surface'])]
    if rewrote:
        print('!! %d words would be displayed as a different word: %s'
              % (len(rewrote), ', '.join(rewrote[:5])), file=sys.stderr)
        return 1

    out = os.path.join(outdir, 'text.json')
    json.dump(art, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    total = sum(stats.values()) or 1
    if quiet:
        amb = stats.get('AMBIGUOUS-needs-resolution', 0)
        print('%-26s %5d words, %3d%% ambiguous' % (src['id'], total, round(100 * amb / total)))
        return 0
    print('\n%-32s %4s  %4s' % ('PROVENANCE', 'N', '%'))
    print('-' * 46)
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print('%-32s %4d  %3d%%' % (k, v, round(100 * v / total)))
    print('-' * 46)
    print('artifact -> %s' % os.path.relpath(out, paths.ROOT))
    amb = stats.get('AMBIGUOUS-needs-resolution', 0)
    if amb:
        print('!! %d ambiguous — add ids to %s' % (amb, os.path.relpath(RESOLUTIONS, paths.ROOT)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sources', nargs='+')
    ap.add_argument('--audio', action='store_true', help='generate MP3s (needs ELEVENLABS_API_KEY)')
    ap.add_argument('--lang', default='he', help=argparse.SUPPRESS)
    a = ap.parse_args()

    key = os.environ.get('ELEVENLABS_API_KEY')
    do_audio = a.audio and key
    if a.audio and not do_audio:
        print('!! --audio requested but ELEVENLABS_API_KEY not set; '
              'emitting artifact with audio: null\n')

    lex = Lexicon()
    # One text prints its whole provenance table, which is what you want when you are looking
    # at one text. Four hundred of those is not a report, so a batch prints one line each.
    quiet = len(a.sources) > 1
    bad = 0
    for src in a.sources:
        bad += ingest(lex, src, do_audio, key, quiet=quiet)
    if quiet:
        print('\n%d texts, %d refused' % (len(a.sources), bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
