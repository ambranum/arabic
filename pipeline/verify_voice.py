#!/usr/bin/env python3
"""Did the audio actually change VOICE? Answer it from the bytes, not by ear.

WHY THIS EXISTS. A re-voice run can "succeed" — new files, new sizes, a clean commit, a
happy log — and still be the OLD voice, because a stale ELEVENLABS_VOICE_ID in the shell
silently won. That happened here, and file size did NOT reveal it: re-synthesizing the same
text with the SAME voice changed clip sizes ~25%, which is the same ballpark as an actual
voice change. Size is noise. Timbre is signal.

HOW. For each clip we take a long-term average log-spectrum over 200 Hz–5 kHz (loudness
removed) — a coarse fingerprint of vocal tract / timbre — and compare the CURRENT clip with
the SAME clip at a baseline git revision. Same text, so the only variable is the voice.

Calibration measured on this corpus:
    same word, real voice change (8sSD -> oJQ) ....... ~0.19
    same voice, different words ...................... ~0.18   <- content alone moves it this much
    same text, same voice, re-synthesized ............ ~0.03
So only a SAME-TEXT before/after comparison is meaningful; anything above ~0.10 is a real
voice change, anything near ~0.03 means you re-rendered the same voice.

Run (after a re-voice, before committing):
    python3 pipeline/verify_voice.py                 # compares against the last commit
    python3 pipeline/verify_voice.py 61c1fda         # or any baseline revision
Needs only afconvert (ships with macOS) + numpy.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import os, sys, glob, wave, subprocess, tempfile
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
THRESHOLD = 0.10          # above this: the voice really changed

def _decode(data, tmpdir, tag):
    mp3 = os.path.join(tmpdir, tag + '.mp3'); wav = os.path.join(tmpdir, tag + '.wav')
    open(mp3, 'wb').write(data)
    r = subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@22050', '-c', '1', mp3, wav],
                       capture_output=True)
    return wav if r.returncode == 0 and os.path.exists(wav) else None

def fingerprint(wav):
    w = wave.open(wav); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64); w.close()
    if len(x) < 2048: return None
    x /= (np.abs(x).max() or 1)
    win, hop = 1024, 512
    hann = np.hanning(win); acc = np.zeros(win // 2 + 1); n = 0
    for i in range(0, len(x) - win, hop):
        fr = x[i:i + win]
        if np.sqrt((fr ** 2).mean()) < 0.05: continue        # skip silence
        acc += np.abs(np.fft.rfft(fr * hann)); n += 1
    if n < 5: return None
    S = np.log(acc / n + 1e-9); S -= S.mean()                # drop loudness
    lo, hi = int(200 / (sr / win)), int(5000 / (sr / win))   # where voice identity lives
    v = S[lo:hi]
    return v / (np.linalg.norm(v) or 1)

def git(*args):
    return subprocess.check_output(['git'] + list(args), cwd=ROOT, stderr=subprocess.DEVNULL)

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    # Only clips that exist in BOTH the baseline and now are comparable — a clip added since
    # the baseline (e.g. a new book chapter) has nothing to be compared against.
    try:
        in_base = {p for p in git('ls-tree', '-r', '--name-only', base, '--', 'app/audio')
                   .decode().split() if p.endswith('.mp3') and '/vocab/' not in p}
    except Exception:
        print('cannot read revision %s' % base); return 1
    here = {os.path.relpath(c, ROOT) for c in
            glob.glob(os.path.join(paths.audio(), '**', '*.mp3'), recursive=True)}
    clips = [os.path.join(ROOT, r) for r in sorted(in_base & here)][:24]
    if not clips:
        print('no sentence clips exist in both %s and now — nothing to compare' % base); return 1

    dists = []
    with tempfile.TemporaryDirectory() as td:
        for i, cur in enumerate(clips):
            rel = os.path.relpath(cur, ROOT)
            try:
                old = git('cat-file', 'blob', '%s:%s' % (base, rel))
            except Exception:
                continue                                       # new clip, nothing to compare
            a = _decode(old, td, 'a%d' % i)
            b = _decode(open(cur, 'rb').read(), td, 'b%d' % i)
            if not a or not b: continue
            fa, fb = fingerprint(a), fingerprint(b)
            if fa is None or fb is None: continue
            dists.append((float(1 - np.dot(fa, fb)), rel))

    if not dists:
        print('nothing comparable against %s (all clips are new?)' % base); return 0
    dists.sort()
    med = dists[len(dists) // 2][0]
    print('compared %d sentence clips against %s\n' % (len(dists), base))
    for d, rel in dists[:3]:  print('   %.4f  %s' % (d, rel))
    print('   ...')
    for d, rel in dists[-3:]: print('   %.4f  %s' % (d, rel))
    print('\nmedian timbre distance: %.4f   (voice change ~0.19, same voice re-render ~0.03)' % med)
    print('VERDICT: %s' % ('VOICE CHANGED — this is a different speaker.' if med > THRESHOLD
          else 'SAME VOICE. The clips were re-rendered but the speaker did not change.'))
    return 0

if __name__ == '__main__':
    sys.exit(main())
