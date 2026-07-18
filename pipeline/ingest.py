#!/usr/bin/env python3
"""Ingest: raw Palestinian text -> fully annotated, cached artifact.

Architecture (SPEC 7.4.2) — metadata is LOOKED UP, never generated:
  1 candidate  -> auto-fill              provenance "maknuune:unique"
  n candidates -> resolutions.json       provenance "maknuune:resolved"
  0 candidates -> flagged, left empty    provenance "unresolved"   (NEVER guessed)

Every word carries its provenance, so a reader can always answer "who said so?".

Audio runs once at ingest and is cached (SPEC 4.2). Needs:
    export ELEVENLABS_API_KEY=...
    export ELEVENLABS_VOICE_ID=...     # the Palestinian Voice Design voice
Without them the pipeline still emits the artifact with audio: null.
"""
import json, os, sys, re, argparse, hashlib, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maknuune import Lexicon, entry_to_word, norm
from subdialect import realize
from vocalize import vocalize
import curated

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RESOLUTIONS = os.path.join(ROOT, 'pipeline', 'resolutions.json')

def load_resolutions():
    if os.path.exists(RESOLUTIONS):
        return json.load(open(RESOLUTIONS, encoding='utf-8'))
    return {}

def tokenize(sent):
    return [w for w in re.split(r'[\s،.؟!]+', sent.strip()) if w]

def annotate_word(lex, surface, res):
    key = norm(surface)
    c = curated.lookup(surface, key)
    if not c:
        # Proper nouns take clitics too (بكييف = بـ + كييف, وأمريكا = وـ + أمريكا).
        stems, _ = lex.morph(surface)
        for st in stems[1:]:
            c = curated.lookup(st, st)
            if c:
                c = {**c, 'surface': surface, 'vocalized': None,
                     'vocalized_from': 'unvocalized:curated-with-clitic'}
                break
    if c:
        return c
    cands = lex.candidates(surface)
    # Prefer untagged entries. A SOURCE village marks a LOCAL variant (قهوة->"ghawa" is
    # tagged الخليل>الظاهرية>الرماضين). Only ~2% are tagged; untagged is the general form.
    cands.sort(key=lambda c: str(c.get('SOURCE')) not in ('nan', 'None', ''))
    if not cands:
        return {"surface": surface, "root": None, "lemma": None, "form": surface,
                "caphi": None, "gloss": None, "analysis": None, "maknuune_id": None,
                "provenance": "unresolved"}
    if surface in res or key in res:
        want = res.get(surface) or res.get(key)
        pick = lex.by_id.get(str(want))
        if pick:
            return {**entry_to_word(pick, surface), "provenance": "maknuune:resolved"}
    # A unique ROOT is not a unique ENTRY: seven entries can share ص.ح.و and mean
    # different things. Auto-fill ONLY when exactly one candidate survives morphology.
    # Anything else is ambiguous and goes to a human/Claude — taking cands[0] is guessing.
    if len(cands) == 1:
        return {**entry_to_word(cands[0], surface), "provenance": "maknuune:unique"}
    return {**entry_to_word(cands[0], surface),
            "provenance": "AMBIGUOUS-needs-resolution",
            "options": [{"id": str(c['ID']), "root": str(c['ROOT']),
                         "gloss": str(c['GLOSS'])[:40], "analysis": str(c['ANALYSIS'])}
                        for c in cands[:6]]}

def tts(text, out_path, api_key, voice_id):
    if os.path.exists(out_path):
        return True, "cached"
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({"text": text, "model_id": "eleven_v3"}).encode(),
        headers={"xi-api-key": api_key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            open(out_path, 'wb').write(r.read())
        return True, "generated"
    except Exception as e:
        return False, str(e)[:90]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--audio', action='store_true', help='generate MP3s (needs env keys)')
    a = ap.parse_args()

    SUB = os.environ.get('PAL_SUBDIALECT', 'urban')
    src = json.load(open(a.source, encoding='utf-8'))
    lex, res = Lexicon(), load_resolutions()
    outdir = os.path.join(ROOT, 'build', src['id'])
    os.makedirs(os.path.join(outdir, 'audio'), exist_ok=True)

    key, voice = os.environ.get('ELEVENLABS_API_KEY'), os.environ.get('ELEVENLABS_VOICE_ID')
    do_audio = a.audio and key and voice
    if a.audio and not do_audio:
        print("!! --audio requested but ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID not set;"
              " emitting artifact with audio: null\n")

    art = {"id": src['id'], "title": src['title'], "dialect": src.get('dialect', 'pal'),
           "kind": src.get('kind', 'lesson'), "date": src.get('date'),
           "subdialect": SUB,
           "source": src.get('source', 'original'), "sentences": []}
    stats = {}
    for si, s in enumerate(src['sentences']):
        words = [annotate_word(lex, w, res) for w in tokenize(s['ar'])]
        for w in words:
            stats[w['provenance']] = stats.get(w['provenance'], 0) + 1
        for w in words:
            w['caphi_urban'] = realize(w.get('caphi_raw') or w.get('caphi'), SUB)
            # SPEC 7.4.6: vocalize the SURFACE form from the lexicon's citation form.
            # Curated entries already carry their own vocalization and must NOT be
            # relabelled as lexicon-sourced — that would launder hand-written data.
            if str(w.get('provenance','')).startswith('curated'):
                w.setdefault('vocalized', w.get('form'))
                w['vocalized_from'] = 'curated'
            else:
                v, vp = vocalize(w['surface'], w.get('form'), w.get('analysis'))
                w['vocalized'], w['vocalized_from'] = v, vp
        sent = {"ar": s['ar'], "en": s['en'], "words": words, "audio": None}
        if do_audio:
            p = os.path.join(outdir, 'audio', f"s{si}.mp3")
            ok, how = tts(s['ar'], p, key, voice)
            sent['audio'] = f"audio/s{si}.mp3" if ok else None
            print(f"  audio s{si}: {how}")
        art['sentences'].append(sent)

    out = os.path.join(outdir, 'text.json')
    json.dump(art, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    total = sum(stats.values())
    print(f"\n{'PROVENANCE':32} {'N':>4}  {'%':>4}")
    print('-' * 46)
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"{k:32} {v:4}  {round(100*v/total):3}%")
    print('-' * 46)
    amb = stats.get('AMBIGUOUS-needs-resolution', 0)
    unres = stats.get('unresolved', 0)
    print(f"artifact -> {os.path.relpath(out, ROOT)}")
    if amb: print(f"!! {amb} ambiguous — add ids to pipeline/resolutions.json")
    if unres: print(f"!! {unres} unresolved — not in Maknuune; needs a human")
    if not amb and not unres: print("clean: every word traced to a real lexicon entry")

if __name__ == '__main__':
    main()
