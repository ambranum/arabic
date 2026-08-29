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
import re
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


# Which script a language's content is written in. Used to check that an ingested artifact
# actually belongs to the tree it is sitting in -- see build_app.py. A Hebrew article reached
# build/ar/ once, and the thing that would have caught it before it deployed is not its metadata
# (which is written by whoever made the mistake) but its letters.
SCRIPTS = {'ar': re.compile('[\u0600-\u06FF\u0750-\u077F]'),
           'he': re.compile('[\u0590-\u05FF\uFB1D-\uFB4F]')}


def in_script(text, code=None):
    return bool(SCRIPTS[code or LANG].search(text or ''))


def require(code):
    """Refuse to run as a language this script was not written for.

    Most of the pipeline is language-generic and takes whatever --lang says. A few scripts are
    not: ingest.py knows Maknuune, he_ingest.py knows Wiktionary, and neither can do the other's
    job. Without this, running one under the wrong language does not fail -- it writes correct
    output into the WRONG TREE, which is how a Hebrew news article came to overwrite the Arabic
    one for the same day and reach git.
    """
    if LANG != code:
        raise SystemExit(
            '%s is %s-only, but the active language is %r.\n'
            'Pass --lang %s (or set ALP_LANG=%s) if that is what you meant.'
            % (os.path.basename(sys.argv[0]), code, LANG, code, code))


def shared(*parts):
    """A path in `app/data/` itself -- for the few files that belong to no language."""
    return os.path.join(ROOT, 'app', 'data', *parts)


def texts(*parts):
    """Source content: what a human or a generator wrote, before ingestion."""
    return os.path.join(ROOT, 'texts', LANG, *parts)


def build(*parts):
    """Ingested content: the annotated intermediate the app is built from."""
    return os.path.join(ROOT, 'build', LANG, *parts)


def audio(*parts):
    """Voiced clips ON DISK, under app/ so the whole folder stays servable."""
    return os.path.join(ROOT, 'app', 'audio', LANG, *parts)


def audio_url(*parts):
    """The same clip as the BROWSER addresses it -- a path relative to app/.

    This is the reason app/audio/ had to be split at all. Clip names are positional
    (`s0.mp3` inside a directory named for the text), so a Hebrew retelling of Aesop would have
    written over the Arabic one and the app would have gone on playing the wrong language with
    no error anywhere. Every generator that stamps a path into shipped data goes through here.
    """
    return '/'.join(('audio', LANG) + parts)


def resolutions():
    """The ambiguity audit trail: which lexicon entry was chosen for which word."""
    return os.path.join(ROOT, 'pipeline', 'resolutions.%s.json' % LANG)
