#!/usr/bin/env python3
"""Every script daily_news.py launches must accept the language it is told.

pipeline/paths.py reads --lang from argv before argparse runs, so a child that is not TOLD its
language silently runs as the default and writes into the wrong tree. The fix for that was to
pass --lang to the annotator. The fix broke the Arabic run outright, because ingest.py's parser
had never been told the flag exists:

    ingest.py: error: unrecognized arguments: --lang ar

Two failures a day apart, opposite in shape, same seam: what the parent passes and what the
child accepts are written in different files and nothing checked they agreed. This checks.

    python3 pipeline/verify_child_args.py
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DAILY = os.path.join(HERE, 'daily_news.py')

ok = fail = 0


def check(cond, what, detail=''):
    global ok, fail
    if cond:
        ok += 1
        print('  \033[32m✓\033[0m %s' % what)
    else:
        fail += 1
        print('  \033[31m✗ %s\033[0m%s' % (what, '\n      ' + detail if detail else ''))


def main():
    src = open(DAILY, encoding='utf-8').read()

    # Which annotator each language uses, read from daily_news.py rather than repeated here --
    # a list kept in step by hand is the thing that just failed.
    m = re.search(r'INGEST_SCRIPT = (\{[^}]*\})', src)
    scripts = eval(m.group(1)) if m else {}
    check(bool(scripts), 'found the annotator table in daily_news.py')
    check(set(scripts) == set(paths.LANGS),
          'every language has one (%s)' % ', '.join(sorted(scripts)))

    # The flag really is passed. If this line ever loses it, the silent-wrong-tree bug is back.
    check('"--lang", paths.LANG' in src, 'daily_news.py passes --lang to the annotator')

    for code, name in sorted(scripts.items()):
        p = os.path.join(HERE, name)
        r = subprocess.run([sys.executable, p, '--lang', code, '--help'],
                           capture_output=True, text=True, cwd=paths.ROOT)
        bad = 'unrecognized arguments' in (r.stderr + r.stdout)
        check(not bad and r.returncode == 0,
              '%s accepts --lang %s' % (name, code),
              (r.stderr or r.stdout).strip().splitlines()[-1] if bad or r.returncode else '')

    # build_app.py takes --lang too, and takes it without argparse; make sure it still resolves.
    for code in paths.LANGS:
        r = subprocess.run([sys.executable, '-c',
                            'import sys; sys.path.insert(0, %r); import paths; print(paths.LANG)'
                            % HERE, '--lang', code], capture_output=True, text=True)
        check(r.stdout.strip() == code, 'paths.LANG resolves to %r from --lang' % code,
              r.stdout.strip() + r.stderr.strip())

    print('\n%d passed, %d failed' % (ok, fail))
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
