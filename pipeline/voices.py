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
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import argparse, json, os, ssl, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from voice import roster, cast_voices, cast_by_gender, cast_dialogue, VOICE_ID, PREVIOUS

import net           # noqa: E402  -- one HTTPS context, one diagnosis
_SSL = net.SSL_CTX


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
        v = r.get(role)
        if not v:
            continue
        pin = '  ← the pinned app voice' if v.get('id') == VOICE_ID else ''
        print('  %-5s %-24s %-9s %s%s' % (role, v.get('id'), (v.get('name') or ''),
                                          v.get('gender') or '?', pin))
        if v.get('note'):
            print('        %s' % v['note'])
    g = cast_by_gender()
    print('\n%d distinct voice(s) — %d male, %d female' % (len(cast_voices()), len(g['m']), len(g['f'])))
    # Show how the real dialogues will actually be cast, before any credits are spent.
    try:
        import glob
        print('\ndialogue casting (as it will be generated):')
        for f in sorted(glob.glob(paths.texts('lessons', 'unit-*.json'))):
            u = json.load(open(f, encoding='utf-8'))
            for d in u.get('dialogues', []):
                d['cast'] = cast_dialogue(d.get('lines', []))
                if not d.get('cast'):
                    continue
                by = {v['id']: (v.get('name') or v['id'][:6]) for v in r.values() if v.get('id')}
                who = ', '.join('%s=%s%s' % (c['sp'], by.get(c['voice'], c['voice'][:6]),
                                             '' if c.get('gender') else '?')
                                for c in d['cast'])
                print('  %-9s %s' % (u['id'], who))
    except Exception:
        pass
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
