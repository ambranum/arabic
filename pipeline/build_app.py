#!/usr/bin/env python3
"""Collect pipeline output into one file the app can read.

Emits a .js file (not .json) that assigns to a global. This is deliberate: a browser
opening a page from file:// REFUSES to fetch() a .json next to it (CORS), so a plain
JSON data file would work when hosted and silently fail when you double-click the app.
A <script> tag has no such restriction. So the app works both ways, with no server —
which is the whole point of a static site.

    python3 pipeline/build_app.py
"""
import json, os, glob, shutil, hashlib

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- where this language's generated data lives

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT  = paths.data('library.js')

# ---------- the deploy stamp: one hash, written into two files ----------
# A hash of the app shell + all data goes into the service worker's cache name, so every deploy
# gets a fresh cache and the SW's activate step drops the stale one — no learner stuck on old
# JS/data behind the cache. (The HTML is fetched network-first regardless; this covers the
# cache-first data/JS assets.)
#
# The SAME hash goes into index.html as window.ALP_BUILD, which the page appends to the URL of
# every script it loads. That is the half that makes a refresh enough. A new cache name only
# takes effect once the browser has fetched, installed and activated the new service worker —
# an extra round trip the page cannot make on its own, and one a home-screen PWA resumed from
# the app switcher may not make for days. A phone in that state served a cached
# data/he/library.js and showed yesterday's news while a laptop showed today's. With the version
# in the URL there is nothing to match, so the first refresh after a deploy is already right.
def stamp_build():
    import re as _re
    sw_path   = os.path.join(ROOT, 'app', 'service-worker.js')
    html_path = os.path.join(ROOT, 'app', 'index.html')
    if not os.path.exists(sw_path):
        return None
    # index.html is hashed with its own stamp NEUTRALISED, for exactly the reason
    # service-worker.js is left out of the file list below: hash a file that contains the hash
    # and each run's version depends on the previous run's, and the value never settles.
    build_re = _re.compile(r"window\.ALP_BUILD = '[^']*';")
    ash = hashlib.md5()
    # Everything the browser executes, so a code change always moves the cache version.
    # index.html alone stopped being enough the moment the app moved into app.js: a JS-only
    # change would have left the version untouched and shipped new code behind a stale cache.
    # The nested data glob is for the per-language directories B5 introduces.
    shell = [html_path] + \
        sorted(p for p in glob.glob(os.path.join(ROOT, 'app', '*.js'))
               if os.path.basename(p) != 'service-worker.js') + \
        sorted(glob.glob(os.path.join(ROOT, 'app', 'lang', '*.js'))) + \
        sorted(glob.glob(os.path.join(ROOT, 'app', 'data', '**', '*.js'), recursive=True))
    for p in shell:
        try:
            blob = open(p, 'rb').read()
        except OSError:
            continue
        if p == html_path:
            blob = build_re.sub("window.ALP_BUILD = '';", blob.decode('utf-8')).encode('utf-8')
        ash.update(blob)
    appver = ash.hexdigest()[:10]

    sw = open(sw_path, encoding='utf-8').read()
    sw2 = _re.sub(r"const CACHE_VERSION = '[^']*';",
                  "const CACHE_VERSION = 'alp-%s';" % appver, sw, count=1)
    if sw2 != sw:
        open(sw_path, 'w', encoding='utf-8').write(sw2)

    # The page and the service worker have to name the SAME versioned URLs — the SW precaches
    # './app.js?v=' + CACHE_VERSION without its prefix — so both are written here, from one hash.
    html = open(html_path, encoding='utf-8').read()
    if 'window.ALP_BUILD' not in html:
        print("!! app/index.html has no window.ALP_BUILD to stamp — its scripts will not be "
              "cache-busted; see the build-stamp comment in its <head>.")
    else:
        html2 = build_re.sub("window.ALP_BUILD = '%s';" % appver, html, count=1)
        if html2 != html:
            open(html_path, 'w', encoding='utf-8').write(html2)
    print(f"sw cache version: alp-{appver}")
    return appver


def main():
    audio_root = paths.audio()
    copied = 0
    texts, drills = [], []
    wrong_script = []
    for p in sorted(glob.glob(paths.build('*', 'text.json'))):
        d = json.load(open(p, encoding='utf-8'))
        d['_dir'] = os.path.basename(os.path.dirname(p))
        # Is this text actually in this language? Its metadata is written by whoever built it,
        # so the metadata cannot be the check -- the letters can. A Hebrew news article once
        # landed in build/ar/ (an annotator launched without --lang) and nothing downstream
        # noticed; it would have shipped as that day's Arabic paper.
        first = next((s_.get('ar', '') for s_ in d.get('sentences') or [] if s_.get('ar')), '')
        if first and not paths.in_script(first):
            wrong_script.append((d['_dir'], first[:40]))
            continue
        d['_words'] = sum(len(s['words']) for s in d['sentences'])
        # `options` is the ambiguity audit trail: every lexicon candidate the annotator weighed
        # before picking one. The app never reads it (grep says so) but it is ~27% of a book
        # chapter's bytes, and library.js is a synchronous <script> parsed on every page load.
        # It stays in build/ where adjudication happens; it does not ship to the browser.
        for s_ in d['sentences']:
            for w in s_['words']:
                w.pop('options', None)
        # Rewrite audio paths to live inside app/ — a hosted folder can't reach ../build.
        # Under the language, because clip names are positional: a Hebrew retelling of Aesop
        # would otherwise write over the Arabic chapter's s0.mp3 and the app would go on playing
        # the wrong language with nothing to show for it.
        for i, s_ in enumerate(d['sentences']):
            if s_.get('audio'):
                src = paths.build(d['_dir'], s_['audio'])
                base = os.path.basename(s_['audio'])
                dst = paths.audio(d['_dir'], base)
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst); copied += 1
                    s_['audio'] = paths.audio_url(d['_dir'], base)
                else:
                    s_['audio'] = None
        d['_audio'] = any(s_.get('audio') for s_ in d['sentences'])
        texts.append(d)
    for p in sorted(glob.glob(paths.build('*', 'session.json'))):
        d = json.load(open(p, encoding='utf-8'))
        d['_dir'] = os.path.basename(os.path.dirname(p))
        for it in d['items']:
            for k in ('cue_audio', 'answer_audio'):
                if it.get(k):
                    src = paths.build(d['_dir'], it[k])
                    base = os.path.basename(it[k])
                    dst = paths.audio(d['_dir'], base)
                    if os.path.exists(src):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst); copied += 1
                        it[k] = paths.audio_url(d['_dir'], base)
                    else:
                        it[k] = None
        d['_audio'] = any(i.get('answer_audio') for i in d['items'])
        drills.append(d)

    # AUDIO CACHE BUSTING. Clips are named by position (audio/<text>/s0.mp3), so re-voicing
    # replaces a file WITHOUT changing its URL — and every browser that already played it keeps
    # serving the old voice from cache, indefinitely. That's exactly what made a completed
    # re-voice look like "the voice didn't change". So stamp a version derived from the actual
    # audio bytes; the app appends it to every audio URL, and any change forces a refetch.
    sig = hashlib.md5()
    for p in sorted(glob.glob(os.path.join(paths.audio(), '**', '*.mp3'), recursive=True)):
        st = os.stat(p)
        sig.update(os.path.relpath(p, ROOT).encode('utf-8'))
        sig.update(str(st.st_size).encode('ascii'))
    audio_version = sig.hexdigest()[:10]

    # Written as an index plus bodies -- see pipeline/split.py. The sentences are 97% of this
    # dataset and the home screen needs none of them.
    import split
    lib_sizes = split.write_library(texts, drills, audio_version)
    # The word-lookup index, precomputed from the same texts in the same order -- the order is
    # load-bearing, since equal-ranked records are broken by first-seen.
    #
    # lexindex.write() declines if the file on disk was written by someone else -- a language
    # whose lookup comes from a dictionary rather than from its own texts (Hebrew:
    # pipeline/he_lexicon.py) owns its own, and this must not stand on it.
    import lexindex
    lex_sizes = lexindex.write(texts) if texts else None

    # A text that has been removed from build/ must not leave its body file behind: it would
    # still be served, still be hashed into the cache version, and still be reachable by URL.
    live = {t['id'] for t in texts} | {d['id'] for d in drills}
    for p in glob.glob(os.path.join(ROOT, 'app', 'data', paths.LANG, 'text', '*.js')):
        if os.path.splitext(os.path.basename(p))[0] not in live:
            os.remove(p); print('  removed stale body:', os.path.basename(p))

    stamp_build()

    print(f"audio version: {audio_version}")
    print(f"texts : {len(texts)}")
    for t in texts:
        print(f"    {t['id']:22} {t['_words']:3} words  audio={'yes' if t['_audio'] else 'no'}")
    print(f"drills: {len(drills)}")
    for d in drills:
        print(f"    {d['id']:22} {len(d['items']):3} chunks audio={'yes' if d['_audio'] else 'no'}")
    if wrong_script:
        print("\n!! %d text(s) under build/%s are NOT in %s's script — skipped, not shipped:"
              % (len(wrong_script), paths.LANG, paths.LANG))
        for d_, sample in wrong_script:
            print("     %-28s %s" % (d_, sample))
        print("   Rebuild them with the right --lang, or delete the stray directory.")

    print(f"audio files copied into app/: {copied}")
    print(f"\n-> {os.path.relpath(OUT, ROOT)}  ({lib_sizes['library.js']//1024} KB index)")
    print(f"   corpus.js {lib_sizes['corpus.js']//1024} KB  ·  "
          f"text/ {lib_sizes['text/']//1024} KB over {lib_sizes['_texts']} files")
    if lex_sizes:
        print(f"   lexicon.js {lex_sizes['lexicon.js']//1024} KB  ·  {lex_sizes['rows']} records, "
              f"{lex_sizes['keys']} lemma keys, {lex_sizes['surfaces']} surface keys")
    print("\napp/ is self-contained — that whole folder is the website.")

if __name__ == '__main__':
    main()
