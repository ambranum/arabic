#!/usr/bin/env python3
"""Where each language's generated data lives.

The app used to be one language, so `app/data/` was simply "the data". It is now two, and the
browser must be able to load one without the other -- a Hebrew learner should never download
15 MB of Arabic. So everything a language owns moves under `app/data/<code>/`, and this module
is the single place that knows it.

Which language a run is for comes from `--lang xx` on the command line, or the `ALP_LANG`
environment variable, or `ar` if neither is given. The default matters: every existing invocation
in the README, in regen_audio.sh and in the nightly news workflow keeps working untouched and
keeps writing Arabic exactly where it did before, one directory deeper.

Only what a language OWNS moves. `app/data/supaconfig.js` and `app/data/pushconfig.js` describe
the account and the push endpoint, which are the same whichever language you are studying, so
they stay at the top level and load on every page.

The content trees -- `texts/`, `build/`, `app/audio/` -- are deliberately NOT split here yet.
Splitting them is pure file movement with nothing to gain until Hebrew content exists, and one
of those trees is written every night by the news cron. See the note at the end of this file.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

LANGS = ('ar', 'he')


def _detect():
    argv = sys.argv
    for i, a in enumerate(argv):
        if a == '--lang' and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith('--lang='):
            return a.split('=', 1)[1]
    return os.environ.get('ALP_LANG', 'ar')


LANG = _detect()
if LANG not in LANGS:
    raise SystemExit('unknown language %r -- expected one of %s' % (LANG, ', '.join(LANGS)))


def data(*parts, code=None):
    """A path inside the active language's data directory, created on demand.

    Generators call this instead of building `app/data/...` by hand, so adding a language never
    means auditing a dozen scripts for a hardcoded path.
    """
    p = os.path.join(ROOT, 'app', 'data', code or LANG, *parts)
    os.makedirs(os.path.dirname(p) if os.path.splitext(p)[1] else p, exist_ok=True)
    return p


def shared(*parts):
    """A path in `app/data/` itself -- for the few files that belong to no language."""
    return os.path.join(ROOT, 'app', 'data', *parts)


# ---- still to split (B5b) ---------------------------------------------------------------------
# texts/<code>/, build/<code>/, app/audio/<code>/ and resolutions.<code>.json. `app/audio/` is the
# one that will bite: clip paths are positional (`audio/book-aesop-ch01/s0.mp3`), so a Hebrew
# Aesop would silently overwrite the Arabic one rather than fail. Nothing is at risk while Arabic
# is the only content, and the move is better done in the quiet before Stage C authors anything
# than in the middle of it.
