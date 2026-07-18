#!/usr/bin/env python3
"""Build a car session: an English-cue -> YOU SPEAK -> Palestinian-answer drill.

NOT a listening track. LEARNING-SYSTEM §2.4: passive listening without attention
produces almost nothing and is the most common way people waste a commute for years.
Every car activity must force retrieval.

So the shape is Pimsleur's, and it is deliberate:
    cue (English)  ->  GAP: you say it out loud  ->  answer (Palestinian)  ->  gap: repeat
The gap is the product. Hearing the answer before you've tried is the failure mode.

Run:
    export ELEVENLABS_API_KEY=...
    export ELEVENLABS_VOICE_ID=...           # your Palestinian Voice Design voice
    export ELEVENLABS_EN_VOICE_ID=...        # any English voice (optional; default Rachel)
    python3 pipeline/car_session.py texts/car-01-reactions.json --audio

Without keys it emits the script and manifest so you can read/verify it first.
"""
import json, os, sys, argparse, urllib.request, subprocess, shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
EN_DEFAULT = "21m00Tcm4TlvDq8ikWAM"   # Rachel — an ElevenLabs stock English voice

def tts(text, path, key, voice, model="eleven_v3"):
    if os.path.exists(path): return True, "cached"
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        data=json.dumps({"text": text, "model_id": model}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            open(path, 'wb').write(r.read())
        return True, "ok"
    except Exception as e:
        return False, str(e)[:80]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source'); ap.add_argument('--audio', action='store_true')
    ap.add_argument('--gap', type=float, default=3.0, help='seconds to produce before the answer')
    a = ap.parse_args()

    d = json.load(open(a.source, encoding='utf-8'))
    out = os.path.join(ROOT, 'build', d['id']); os.makedirs(os.path.join(out,'audio'), exist_ok=True)

    key   = os.environ.get('ELEVENLABS_API_KEY')
    ar_v  = os.environ.get('ELEVENLABS_VOICE_ID')
    en_v  = os.environ.get('ELEVENLABS_EN_VOICE_ID', EN_DEFAULT)
    do    = a.audio and key and ar_v

    unval = [c for c in d['chunks'] if c.get('provenance','').endswith('needs-native-validation')]
    if unval and do:
        print(f"!! {len(unval)} chunks are UNSOURCED and unvalidated:")
        for c in unval: print(f"     {c['ar']:14} {c['en']}")
        print("   Generating audio bakes them in. Validate first (design/chunk-review.html).\n")

    script, manifest = [], []
    for i, c in enumerate(d['chunks']):
        cue, ans = c['en'], c['ar']
        script.append(f"{i+1:2}. CUE: {cue}\n    [{a.gap}s — say it out loud]\n"
                      f"    ANS: {ans}\n    [{a.gap}s — say it again]\n")
        item = {"i": i, "cue": cue, "answer": ans, "use": c.get('use'),
                "provenance": c.get('provenance'), "cue_audio": None, "answer_audio": None}
        if do:
            p1 = os.path.join(out,'audio',f"{i:02d}-cue.mp3")
            p2 = os.path.join(out,'audio',f"{i:02d}-ans.mp3")
            ok1,_ = tts(cue, p1, key, en_v)
            ok2,_ = tts(ans, p2, key, ar_v)
            item['cue_audio']    = f"audio/{i:02d}-cue.mp3" if ok1 else None
            item['answer_audio'] = f"audio/{i:02d}-ans.mp3" if ok2 else None
            print(f"  {i:02d} {'ok' if ok1 and ok2 else 'FAIL'}  {ans}")
        manifest.append(item)

    open(os.path.join(out,'script.txt'),'w',encoding='utf-8').write(
        f"{d['title']['en']}\n{'='*60}\n\n" + "\n".join(script))
    json.dump({"id": d['id'], "title": d['title'], "gap_seconds": a.gap,
               "provenance_note": d.get('provenance_note'), "items": manifest},
              open(os.path.join(out,'session.json'),'w',encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print(f"\nscript   -> build/{d['id']}/script.txt")
    print(f"manifest -> build/{d['id']}/session.json")
    if not do:
        print("\naudio: skipped (set ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID, pass --audio)")
    else:
        has_ff = shutil.which('ffmpeg')
        print("\nstitch into one car-ready MP3:")
        if has_ff:
            print(f"    python3 pipeline/car_session.py {a.source} --audio && ffmpeg ...")
        else:
            print("    ffmpeg not installed — `brew install ffmpeg` to stitch one file.")
            print("    Without it: play the audio/ folder in order; most car players do this.")

if __name__ == '__main__':
    main()
