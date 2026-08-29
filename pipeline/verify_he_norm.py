#!/usr/bin/env python3
"""Does app/lang/he.js normalize Hebrew exactly as the pipeline that keyed the lexicon did?

The Hebrew index is keyed by he_norm() in spike/he/build_lex.py. At runtime the app looks words
up through LANG.script.norm in app/lang/he.js. If those two ever disagree — one folds a final
letter the other keeps, one strips a mark the other does not — the lookup does not fail, it just
returns nothing for the words where they differ, and the section quietly has holes in it.

So they are compared directly: the JS function is lifted out of the pack and run in node over
every key the shipped index contains, plus a set of cases chosen to hit each rule.

    python3 pipeline/verify_he_norm.py --lang he
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spike', 'he'))
import paths            # noqa: E402
from build_lex import he_norm   # noqa: E402

# Each of these exercises one rule, so a failure names the rule rather than just a word.
CASES = [
    ('סֵפֶר', 'niqqud stripped'),
    ('שָׁלוֹם', 'dagesh and shin-dot stripped'),
    ('בָּנִים', 'final mem folded'),
    ('מֶלֶךְ', 'final kaf folded'),
    ('אָרֶץ', 'final tsadi folded'),
    ('יוֹסֵף', 'final pe folded'),
    ('לָשׁוֹן', 'final nun folded'),
    ('בְּרֵאשִׁ֖ית', 'cantillation stripped'),
    ('צה״ל', 'gershayim dropped'),
    ('ג׳ורג׳', 'geresh dropped — but the letter it marks survives'),
    ('בֵּית־לֶחֶם', 'maqaf'),
    ('  רָץ  ', 'trimmed'),
]


def main():
    lex_path = paths.data('lexicon.js')
    if not os.path.exists(lex_path):
        print('no %s — run pipeline/he_lexicon.py first' % os.path.relpath(lex_path, paths.ROOT))
        return 1
    src = open(lex_path, encoding='utf-8').read()
    lex = json.loads(src[src.index('window.LEXICON = ') + len('window.LEXICON = '): src.rindex(';')])

    pack = open(os.path.join(paths.ROOT, 'app', 'lang', 'he.js'), encoding='utf-8').read()
    m = re.search(r'\n    norm: (s => .*?),\n    run:', pack, re.S)
    if not m:
        print('could not find LANG.script.norm in app/lang/he.js'); return 1

    keys = sorted(set(lex['k']) | set(lex['s']))
    # The index is already normalized, so feed the RAW forms too -- that is what the app sees.
    raw = [r[0] for r in lex['r'] if r and r[0]] + [r[1] for r in lex['r'] if len(r) > 1 and r[1]]
    words = keys + raw + [c[0] for c in CASES]

    # 124,000 Hebrew strings is past the argv limit, so they go through a temp file.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        wp = os.path.join(tmp, 'w.json')
        with open(wp, 'w', encoding='utf-8') as f:
            json.dump(words, f)
        script = ('const norm = %s;\n'
                  'const ws = JSON.parse(require("fs").readFileSync(%s, "utf8"));\n'
                  'process.stdout.write(JSON.stringify(ws.map(norm)));'
                  % (m.group(1), json.dumps(wp)))
        out = subprocess.run(['node', '-e', script], capture_output=True, text=True)
    if out.returncode:
        print('node failed:\n' + out.stderr[:500]); return 1
    got = json.loads(out.stdout)

    print('rules:')
    bad_case = 0
    for i, (w, label) in enumerate(CASES):
        j = len(keys) + len(raw) + i
        want, mine = he_norm(w), got[j]
        ok = want == mine
        bad_case += not ok
        print('  %-4s %-14s %-46s %s' % ('ok' if ok else 'FAIL', w, label,
                                         '' if ok else 'python %r  js %r' % (want, mine)))

    bad, sample = 0, []
    for w, mine in zip(words, got):
        want = he_norm(w)
        if want != mine:
            bad += 1
            if len(sample) < 5:
                sample.append((w, want, mine))
    print('\n%d strings compared — %d index keys, %d raw forms'
          % (len(words), len(keys), len(raw)))
    for w, a, b in sample:
        print('  %r  python %r  js %r' % (w, a, b))
    print('\n%s' % ('MISMATCHES: %d' % bad if (bad or bad_case) else
                    'identical — the app normalizes Hebrew exactly as the index was keyed'))
    return 1 if (bad or bad_case) else 0


if __name__ == '__main__':
    sys.exit(main())
