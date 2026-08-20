#!/usr/bin/env python3
"""Build the Lessons (native-sourced teaching units) data (+ audio).

Reads texts/lessons/unit-*.json and emits app/data/lessons.js -> window.LESSONS =
{units:[...]}. Each unit is a coherent ~30-45 min teaching unit whose Arabic is copied
VERBATIM from the transcribed reference library (texts/ref/, the user's own native teaching
materials) — per-chunk src fields point at the exact book page. English glosses are the
book's where it had them, the app's where the page was Arabic-only.

With --audio it generates a clip per chunk, per reply and per dialogue line, CAST rather than
narrated: the taught chunk is the pinned app voice, a reply is the other person answering, and
each dialogue speaker keeps one voice for the whole scene — picked to match their gender, so a
woman's lines are never read by a man (see texts/voices.json and voice.cast_dialogue).
Files: app/audio/lessons/<unit>-cNN[r].mp3 and <unit>-dN-lNN.mp3.

Run:
    python3 pipeline/lessons.py                 # data only
    export ELEVENLABS_API_KEY=...; python3 pipeline/lessons.py --audio
"""
import json, os, sys, glob, argparse, ssl, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from voice import voice_id, cast_voices, cast_dialogue, norm_speaker

try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL = ssl.create_default_context()

SRC_GLOB = os.path.join(ROOT, 'texts', 'lessons', 'unit-*.json')
OUT_JS = os.path.join(ROOT, 'app', 'data', 'lessons.js')
AUDIO_DIR = os.path.join(ROOT, 'app', 'audio', 'lessons')


def tts(text, path, key, voice, model='eleven_multilingual_v2'):
    if os.path.exists(path):
        return True, 'cached'
    req = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{voice}',
        data=json.dumps({'text': text, 'model_id': model}).encode(),
        headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=90, context=_SSL) as r:
            open(path, 'wb').write(r.read())
        return True, 'generated'
    except Exception as e:
        return False, str(e)[:100]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audio', action='store_true', help='generate per-chunk MP3s (needs ELEVENLABS_API_KEY)')
    ap.add_argument('--min-words', type=int, default=1, metavar='N',
                    help='only voice items of at least N words (2 = skip single words, which the '
                         'word-audio bank and the browser voice already cover)')
    ap.add_argument('--estimate', action='store_true',
                    help='print the ElevenLabs character/credit cost and exit — generates nothing')
    a = ap.parse_args()

    def wc(s):
        return len([w for w in s.replace('\\', ' ').split() if w.strip()])

    key, voice = os.environ.get('ELEVENLABS_API_KEY'), voice_id()
    CAST = cast_voices()          # [main, b, c, …] — a reply and each dialogue speaker get their own
    do_audio = a.audio and key and voice and not a.estimate
    if a.audio and not (key and voice) and not a.estimate:
        print('!! --audio requested but ELEVENLABS_API_KEY not set; emitting data with no audio\n')
    if do_audio:
        os.makedirs(AUDIO_DIR, exist_ok=True)
    est = [0, 0]        # [characters, clips] that WOULD be generated at this --min-words
    skipped = [0]

    units = []
    for f in sorted(glob.glob(SRC_GLOB)):
        u = json.load(open(f, encoding='utf-8'))
        for i, c in enumerate(u.get('chunks', [])):
            base = '%s-c%02d' % (u['id'], i)
            # The taught chunk is the app's own voice; its reply is the OTHER person answering.
            for suffix, ar, vx in (('', c.get('ar'), CAST[0]),
                                   ('r', (c.get('reply') or {}).get('ar'), CAST[1 % len(CAST)])):
                if not ar:
                    continue
                if wc(ar) < a.min_words:      # single words fall back to the word bank / browser voice
                    skipped[0] += 1
                    continue
                est[0] += len(ar); est[1] += 1
                clip = os.path.join(AUDIO_DIR, base + suffix + '.mp3')
                rel = 'audio/lessons/%s%s.mp3' % (base, suffix)
                tgt = c if not suffix else c['reply']
                if os.path.exists(clip):
                    tgt['audio'] = rel
                elif do_audio:
                    ok, how = tts(ar, clip, key, vx)
                    print('  %s%s %-24s %s' % (base, suffix, ar[:22], how))
                    if ok:
                        tgt['audio'] = rel

        # Dialogues: one voice per speaker, assigned in order of appearance and held for the whole
        # conversation. Speaker names are normalized first — the books vocalize the same name
        # differently from page to page, which would otherwise swap an actor mid-scene.
        for di, d in enumerate(u.get('dialogues', [])):
            d['cast'] = cast_dialogue(d.get('lines', []))
            cast_of = {c['sp']: c['voice'] for c in d['cast']}
            for li, l in enumerate(d.get('lines', [])):
                ar = l.get('ar')
                if not ar or wc(ar) < a.min_words:
                    if ar: skipped[0] += 1
                    continue
                est[0] += len(ar); est[1] += 1
                lid = '%s-d%d-l%02d' % (u['id'], di, li)
                clip = os.path.join(AUDIO_DIR, lid + '.mp3')
                rel = 'audio/lessons/%s.mp3' % lid
                if os.path.exists(clip):
                    l['audio'] = rel
                elif do_audio:
                    ok, how = tts(ar, clip, key, cast_of.get(norm_speaker(l.get('sp')) or '?', CAST[0]))
                    print('  %s [%s] %-20s %s' % (lid, (l.get('sp') or '?')[:8], ar[:20], how))
                    if ok:
                        l['audio'] = rel
        units.append(u)

    units.sort(key=lambda u: u.get('n', 99))
    os.makedirs(os.path.dirname(OUT_JS), exist_ok=True)
    with open(OUT_JS, 'w', encoding='utf-8') as f:
        f.write('// GENERATED by pipeline/lessons.py — do not edit by hand.\n')
        f.write('// Teaching units whose Arabic is copied verbatim from the reference library\n')
        f.write('// (texts/ref/ — the native teaching materials); per-chunk src = book page.\n')
        f.write('window.LESSONS = ')
        json.dump({'units': units}, f, ensure_ascii=False, indent=1)
        f.write(';\n')

    n_ch = sum(len(u.get('chunks', [])) for u in units)
    voiced = sum(1 for u in units for c in u.get('chunks', []) if c.get('audio'))
    print('units: %d · %d chunks · audio %d/%d' % (len(units), n_ch, voiced, n_ch))
    if a.estimate or a.audio:
        # ElevenLabs bills 1 credit per character on the multilingual model this pipeline uses
        # (the faster flash/turbo models bill half). Quoted as characters so it stays true if
        # their pricing tiers change.
        print('audio scope at --min-words %d: %d clips · %s characters ≈ %s credits (%s on flash)'
              % (a.min_words, est[1], format(est[0], ','), format(est[0], ','), format(est[0] // 2, ',')))
        if skipped[0]:
            print('  (%d shorter item(s) skipped — the word-audio bank and browser voice cover those)' % skipped[0])
    print('-> app/data/lessons.js')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
