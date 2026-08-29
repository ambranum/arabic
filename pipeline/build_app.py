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

def main():
    audio_root = os.path.join(ROOT, 'app', 'audio')
    copied = 0
    texts, drills = [], []
    for p in sorted(glob.glob(os.path.join(ROOT, 'build', '*', 'text.json'))):
        d = json.load(open(p, encoding='utf-8'))
        d['_dir'] = os.path.basename(os.path.dirname(p))
        d['_words'] = sum(len(s['words']) for s in d['sentences'])
        # `options` is the ambiguity audit trail: every lexicon candidate the annotator weighed
        # before picking one. The app never reads it (grep says so) but it is ~27% of a book
        # chapter's bytes, and library.js is a synchronous <script> parsed on every page load.
        # It stays in build/ where adjudication happens; it does not ship to the browser.
        for s_ in d['sentences']:
            for w in s_['words']:
                w.pop('options', None)
        # Rewrite audio paths to live inside app/ — a hosted folder can't reach ../build.
        for i, s_ in enumerate(d['sentences']):
            if s_.get('audio'):
                src = os.path.join(ROOT, 'build', d['_dir'], s_['audio'])
                dst_rel = os.path.join('audio', d['_dir'], os.path.basename(s_['audio']))
                dst = os.path.join(ROOT, 'app', dst_rel)
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst); copied += 1
                    s_['audio'] = dst_rel.replace(os.sep, '/')
                else:
                    s_['audio'] = None
        d['_audio'] = any(s_.get('audio') for s_ in d['sentences'])
        texts.append(d)
    for p in sorted(glob.glob(os.path.join(ROOT, 'build', '*', 'session.json'))):
        d = json.load(open(p, encoding='utf-8'))
        d['_dir'] = os.path.basename(os.path.dirname(p))
        for it in d['items']:
            for k in ('cue_audio', 'answer_audio'):
                if it.get(k):
                    src = os.path.join(ROOT, 'build', d['_dir'], it[k])
                    dst_rel = os.path.join('audio', d['_dir'], os.path.basename(it[k]))
                    dst = os.path.join(ROOT, 'app', dst_rel)
                    if os.path.exists(src):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst); copied += 1
                        it[k] = dst_rel.replace(os.sep, '/')
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
    for p in sorted(glob.glob(os.path.join(ROOT, 'app', 'audio', '**', '*.mp3'), recursive=True)):
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
    import lexindex
    lex_sizes = lexindex.write(texts)

    # A text that has been removed from build/ must not leave its body file behind: it would
    # still be served, still be hashed into the cache version, and still be reachable by URL.
    live = {t['id'] for t in texts} | {d['id'] for d in drills}
    for p in glob.glob(os.path.join(ROOT, 'app', 'data', paths.LANG, 'text', '*.js')):
        if os.path.splitext(os.path.basename(p))[0] not in live:
            os.remove(p); print('  removed stale body:', os.path.basename(p))

    # Stamp the service worker's cache name with a hash of the app shell + all data, so every
    # deploy gets a fresh cache and the SW's activate step drops the stale one — no learner stuck
    # on old JS/data behind the cache. (The HTML is fetched network-first regardless; this covers
    # the cache-first data/JS assets.)
    sw_path = os.path.join(ROOT, 'app', 'service-worker.js')
    if os.path.exists(sw_path):
        import re as _re
        ash = hashlib.md5()
        # Everything the browser executes, so a code change always moves the cache version.
        # index.html alone stopped being enough the moment the app moved into app.js: a JS-only
        # change would have left the version untouched and shipped new code behind a stale
        # cache. The nested data glob is for the per-language directories B5 introduces.
        # service-worker.js is deliberately absent: this hash is written INTO it, so including
        # it makes each run's version depend on the previous run's and the value never settles.
        shell = [os.path.join(ROOT, 'app', 'index.html')] + \
            sorted(p for p in glob.glob(os.path.join(ROOT, 'app', '*.js'))
                   if os.path.basename(p) != 'service-worker.js') + \
            sorted(glob.glob(os.path.join(ROOT, 'app', 'lang', '*.js'))) + \
            sorted(glob.glob(os.path.join(ROOT, 'app', 'data', '**', '*.js'), recursive=True))
        for p in shell:
            try:
                ash.update(open(p, 'rb').read())
            except OSError:
                pass
        appver = ash.hexdigest()[:10]
        sw = open(sw_path, encoding='utf-8').read()
        sw2 = _re.sub(r"const CACHE_VERSION = '[^']*';",
                      "const CACHE_VERSION = 'alp-%s';" % appver, sw, count=1)
        if sw2 != sw:
            open(sw_path, 'w', encoding='utf-8').write(sw2)
        print(f"sw cache version: alp-{appver}")

    print(f"audio version: {audio_version}")
    print(f"texts : {len(texts)}")
    for t in texts:
        print(f"    {t['id']:22} {t['_words']:3} words  audio={'yes' if t['_audio'] else 'no'}")
    print(f"drills: {len(drills)}")
    for d in drills:
        print(f"    {d['id']:22} {len(d['items']):3} chunks audio={'yes' if d['_audio'] else 'no'}")
    print(f"audio files copied into app/: {copied}")
    print(f"\n-> {os.path.relpath(OUT, ROOT)}  ({lib_sizes['library.js']//1024} KB index)")
    print(f"   corpus.js {lib_sizes['corpus.js']//1024} KB  ·  "
          f"text/ {lib_sizes['text/']//1024} KB over {lib_sizes['_texts']} files")
    print(f"   lexicon.js {lex_sizes['lexicon.js']//1024} KB  ·  {lex_sizes['rows']} records, "
          f"{lex_sizes['keys']} lemma keys, {lex_sizes['surfaces']} surface keys")
    print("\napp/ is self-contained — that whole folder is the website.")

if __name__ == '__main__':
    main()
