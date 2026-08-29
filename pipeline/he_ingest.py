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
from voice import language_code, model_id, voice_id   # noqa: E402
from build_lex import he_norm                          # noqa: E402
from lex import Lexicon                                # noqa: E402

RESOLUTIONS = paths.resolutions()

try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL = ssl.create_default_context()

# Hebrew punctuation is the Latin set plus the geresh pair, which mark sounds and abbreviations
# and must NOT be split on inside a word (צה״ל, ג׳ורג׳) -- only when they stand alone.
SPLIT = re.compile(r'[\s.,;:!?…"«»“”()\[\]—–\-]+')


def tokenize(sent):
    return [w for w in SPLIT.split(sent.strip()) if w and re.search(r'[֐-׿]', w)]


def load_resolutions():
    if os.path.exists(RESOLUTIONS):
        return json.load(open(RESOLUTIONS, encoding='utf-8'))
    return {}


def _word(rec, surface, prov, cut=''):
    """One lexicon record, in the record shape app.js reads.

    The field names are the Arabic pipeline's and stay that way on purpose: they are what the
    word card, the deck and the lexicon index already read, and `caphi`/`maknuune_id` mean "the
    pronunciation" and "the lexicon's id for this" rather than anything Arabic. Renaming them
    would migrate live study data for no visible gain.
    """
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
        'vocalized': None if cut else rec['FORM'],
        'vocalized_from': ('unvocalized:clitic' if cut
                           else 'lexicon' if rec['FORM'] else 'unvocalized:no-entry'),
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
    want = res.get(surface) or res.get(key)
    if want:
        pick = lex.by_id.get(str(want))
        if pick:
            return _word(pick, surface, 'wiktionary:resolved')
    rec, prov, cands = lex.resolve(surface)
    if rec is None:
        return _blank(surface)
    _, _, cut = lex.look(surface)
    w = _word(rec, surface, prov, cut)
    if prov == 'AMBIGUOUS-needs-resolution':
        w['options'] = [{'id': str(c['ID']), 'root': str(c['ROOT'] or ''),
                         'gloss': str(c['GLOSS'] or '')[:60],
                         'analysis': str(c['ANALYSIS'] or ''),
                         'pointed': c['FORM']} for c in cands]
    return w


def tts(text, out_path, api_key):
    if os.path.exists(out_path):
        return True, 'cached'
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
        return True, 'generated'
    except urllib.error.HTTPError as e:
        return False, 'HTTP %s — %s' % (e.code, e.read().decode('utf-8', 'replace')[:150])
    except Exception as e:
        return False, str(e)[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--audio', action='store_true', help='generate MP3s (needs ELEVENLABS_API_KEY)')
    ap.add_argument('--lang', default='he', help=argparse.SUPPRESS)
    a = ap.parse_args()

    src = json.load(open(a.source, encoding='utf-8'))
    if 'sentences' not in src:
        print('skip %s: not a sentence-text' % os.path.basename(a.source))
        return 0

    lex, res = Lexicon(), load_resolutions()
    outdir = paths.build(src['id'])
    os.makedirs(os.path.join(outdir, 'audio'), exist_ok=True)

    key = os.environ.get('ELEVENLABS_API_KEY')
    do_audio = a.audio and key
    if a.audio and not do_audio:
        print('!! --audio requested but ELEVENLABS_API_KEY not set; '
              'emitting artifact with audio: null\n')

    art = {'id': src['id'], 'title': src['title'], 'dialect': src.get('dialect', 'he'),
           'kind': src.get('kind', 'lesson'), 'date': src.get('date'),
           'level': src.get('level'), 'book': src.get('book'), 'chapter': src.get('chapter'),
           'book_title': src.get('book_title'), 'shelf': src.get('shelf', 0),
           'book_meta': src.get('book_meta'), 'subdialect': None,
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
            ok, how = tts(s['ar'], ap_, key)
            sent['audio'] = 'audio/s%d.mp3' % si if ok else None
            print('  audio s%d: %s' % (si, how))
        art['sentences'].append(sent)

    out = os.path.join(outdir, 'text.json')
    json.dump(art, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    total = sum(stats.values()) or 1
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


if __name__ == '__main__':
    sys.exit(main())
