#!/usr/bin/env python3
"""Generate a per-word Palestinian audio clip for the vocabulary that appears in the app's
content (stories, news, lessons), so memorization cards can play your real Ramallah voice.

Runtime TTS from a public web page would expose your key, so we pre-generate here instead.
Cards whose lemma isn't in the emitted manifest fall back to the browser's built-in voice.

Run:  ELEVENLABS_API_KEY=... python3 pipeline/vocab_audio.py
The voice comes from pipeline/voice.py (ELEVENLABS_VOICE_ID overrides it if you set one).
Without the key it just reports how many clips WOULD be generated and writes nothing.
Clips are cached by content hash, so re-runs only synthesize new words.
"""
import argparse, json, os, glob, hashlib, re, urllib.request, ssl, urllib.error
from voice import language_code, model_id, voice_id

# macOS python.org builds ship without wired-up CA certs, so HTTPS verification fails with
# CERTIFICATE_VERIFY_FAILED. Use certifi's bundle when it's installed (it is, via pip).
import net           # noqa: E402  -- one HTTPS context, one diagnosis
_SSL = net.SSL_CTX

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- where this language's generated data lives

OUTDIR = paths.audio('vocab')
MANIFEST = paths.data('vocab_audio.js')

def collect():
    """Unique real-word vocabulary from every ingested text: lemma -> vocalized form to speak."""
    vocab = {}
    for p in glob.glob(paths.build('*', 'text.json')):
        d = json.load(open(p, encoding='utf-8'))
        for s in d['sentences']:
            for w in s['words']:
                lemma = w.get('lemma')
                if not lemma or not (w.get('maknuune_id') or str(w.get('provenance','')).startswith('curated')):
                    continue
                # Speak the vocalized dictionary form; fall back to the lemma itself.
                vocab.setdefault(lemma, w.get('form') or w.get('vocalized') or lemma)
    return vocab

# A BOUND MORPHEME IS NOT A WORD. Hebrew's lexicon lists suffixes and prefixes as entries --
# ־ִים, ־ָיו, ־לָךְ, all written with a maqaf -- and the collector picks them up like anything
# else. Reading "־ִים" aloud is not a pronunciation, it is a noise, and it costs a clip. Nor is
# a lemma the dictionary spells two ways at once ("־ייה \ ־ִיָּה"). 21 of Hebrew's 1,571.
MAQAF = '\u05be'


def speakable(lemma, text):
    # Deliberately NOT "longer than one letter". That rule cost Arabic و "and" and three
    # numerals -- real words with clips already on disk -- and dropping a word from the
    # manifest is the silent failure this file's own comment warns about: the clip stays,
    # the card stops playing it.
    return not (MAQAF in lemma or MAQAF in text          # an affix, not a word
                or re.search(r'[\\/|]', text))           # two spellings in one entry


def tts(text, out_path, key, voice):
    if os.path.exists(out_path):
        return 'cached'
    # The model and the language tag are the LANGUAGE'S, from voice.py. This file used to pin
    # eleven_multilingual_v2, which does not have Hebrew in it at all.
    body = {"text": text, "model_id": model_id()}
    lc = language_code()
    if lc:
        body["language_code"] = lc
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90, context=_SSL) as r:
            open(out_path, 'wb').write(r.read())
        return 'generated'
    except urllib.error.HTTPError as e:            # surface ElevenLabs' actual message
        if net.fatal(e, 'vocab audio: '):          # a rejected key, a spent balance
            raise SystemExit(1)
        raise RuntimeError('HTTP %s — %s' % (e.code, e.read().decode('utf-8', 'replace')[:300]))
    except Exception as e:
        if net.fatal(e, 'vocab audio: '):
            raise SystemExit(1)
        raise

def main():
    ap = argparse.ArgumentParser()
    # Read by pipeline/paths.py at import time, before argparse runs. Declared so --help lists
    # it and an unknown-argument error never fires on it.
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    ap.parse_args()

    vocab = {k: v for k, v in collect().items() if speakable(k, v)}
    key, voice = os.environ.get('ELEVENLABS_API_KEY'), voice_id()
    print('%d speakable vocabulary words in content.' % len(vocab))
    # Without a key this still rewrites the manifest from the clips already on disk. Re-stamping
    # a path is not synthesis, and the alternative -- bailing -- left the manifest pointing at
    # where the clips used to be, which is silent and total: every word plays nothing.
    if not key:
        print('No ELEVENLABS_API_KEY set — no new clips; rebuilding the manifest from the '
              'clips already voiced.')
    else:
        print('voice: %s   model: %s' % (voice, model_id()))
    os.makedirs(OUTDIR, exist_ok=True)
    manifest, gen, cached, failed, absent = {}, 0, 0, 0, 0
    items = sorted(vocab.items())
    for n, (lemma, text) in enumerate(items):
        name = hashlib.md5(lemma.encode('utf-8')).hexdigest()[:16] + '.mp3'
        out = os.path.join(OUTDIR, name)
        if not key:
            if os.path.exists(out):
                manifest[lemma] = paths.audio_url('vocab', name); cached += 1
            else:
                absent += 1
            continue
        try:
            status = tts(text, out, key, voice)
            manifest[lemma] = paths.audio_url('vocab', name)
            gen += status == 'generated'; cached += status == 'cached'
        except Exception as e:
            failed += 1
            print('  !! %s: %s' % (lemma, str(e)[:320]))
            # Don't hammer the API 1400 times if the very first calls all fail — bail with
            # the real error so it can be fixed (bad model, voice, or plan) before retrying.
            if failed >= 3 and gen == 0 and cached == 0:
                print('\nFirst %d requests all failed — stopping so we don’t burn credits.' % failed)
                print('Check the message above (usually the model_id or voice_id, or plan '
                      'limits). Try ELEVENLABS_MODEL=eleven_multilingual_v2 or v1, and confirm '
                      'the voice is saved in your ElevenLabs Voices (not just a Design preview).')
                return
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        f.write('// GENERATED by pipeline/vocab_audio.py — do not edit by hand.\n')
        f.write('window.VOCAB_AUDIO = ')
        json.dump(manifest, f, ensure_ascii=False)
        f.write(';\n')
    print('generated %d, cached %d, %s%d -> %s (%d clips)' % (
        gen, cached, 'not yet voiced ' if not key else 'failed ',
        absent if not key else failed, os.path.relpath(MANIFEST, ROOT), len(manifest)))

if __name__ == '__main__':
    main()
