#!/usr/bin/env python3
"""Inspect the ElevenLabs voice library and the app's speaking cast.

`--list` asks ElevenLabs which voices your account has, so you can fill the roles in
texts/voices.json with real ids instead of guessing. Needs ELEVENLABS_API_KEY in your
terminal; the key is only read from the environment, never written anywhere.

`--cast` (the default) prints the roster as the pipelines will resolve it — no key needed,
no network — so you can see which roles are still falling back before spending credits.

Run:
    python3 pipeline/voices.py                 # show the cast as configured
    export ELEVENLABS_API_KEY=...; python3 pipeline/voices.py --list
"""
import argparse, json, os, ssl, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from voice import roster, cast_voices, VOICE_ID, PREVIOUS

try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL = ssl.create_default_context()


def list_voices(key):
    req = urllib.request.Request('https://api.elevenlabs.io/v1/voices',
                                 headers={'xi-api-key': key})
    with urllib.request.urlopen(req, timeout=60, context=_SSL) as r:
        data = json.load(r)
    vs = data.get('voices', [])
    print('%-26s %-22s %s' % ('voice_id', 'name', 'labels'))
    for v in vs:
        labels = v.get('labels') or {}
        bits = ' '.join('%s=%s' % (k, labels[k]) for k in ('gender', 'accent', 'age') if labels.get(k))
        mine = ' *' if v.get('category') in ('cloned', 'generated', 'professional') else ''
        print('%-26s %-22s %s%s' % (v.get('voice_id'), (v.get('name') or '')[:22], bits, mine))
    print('\n%d voices (* = your own designed/cloned voices — those are the ones worth using here)' % len(vs))
    return 0


def show_cast():
    r = roster()
    print('the app’s speaking cast (texts/voices.json):')
    for role in ('main', 'b', 'c', 'd', 'e'):
        vid = r.get(role)
        note = ''
        if vid == VOICE_ID:
            note = '  (the pinned app voice)'
        elif vid in PREVIOUS:
            note = '  (%s)' % PREVIOUS[vid][:60]
        print('  %-5s %s%s' % (role, vid or '— not set, falls back', note))
    print('\nresolved to %d distinct voice(s): %s' % (len(cast_voices()), ', '.join(cast_voices())))
    if len(cast_voices()) < 4:
        print('note: the four-way dialogues (units 20 and 24) will reuse voices until roles c/d are set.')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true', help='list your ElevenLabs voices (needs the key)')
    a = ap.parse_args()
    if a.list:
        key = os.environ.get('ELEVENLABS_API_KEY')
        if not key:
            print('ELEVENLABS_API_KEY is not set in this shell — export it and re-run.')
            return 1
        return list_voices(key)
    return show_cast()


if __name__ == '__main__':
    raise SystemExit(main())
