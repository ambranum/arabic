#!/usr/bin/env python3
"""Ingest: raw Palestinian text -> fully annotated, cached artifact.

Architecture (SPEC 7.4.2) — metadata is LOOKED UP, never generated:
  1 candidate  -> auto-fill              provenance "maknuune:unique"
  n candidates -> resolutions.<lang>.json provenance "maknuune:resolved"
  0 candidates -> flagged, left empty    provenance "unresolved"   (NEVER guessed)

Every word carries its provenance, so a reader can always answer "who said so?".

Audio runs once at ingest and is cached (SPEC 4.2). Needs:
    export ELEVENLABS_API_KEY=...
    export ELEVENLABS_VOICE_ID=...     # the Palestinian Voice Design voice
Without them the pipeline still emits the artifact with audio: null.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
import json, os, sys, re, argparse, hashlib, urllib.request, ssl, urllib.error
import net           # noqa: E402  -- one HTTPS context, one diagnosis
_SSL = net.SSL_CTX
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maknuune import Lexicon, entry_to_word, norm
from subdialect import realize
from vocalize import vocalize
from voice import voice_id
import curated

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
paths.require('ar')

RESOLUTIONS = paths.resolutions()

def load_resolutions():
    if os.path.exists(RESOLUTIONS):
        return json.load(open(RESOLUTIONS, encoding='utf-8'))
    return {}

def tokenize(sent):
    # Split on whitespace and punctuation — including the colon/semicolon and quotes that
    # dialogue uses (قال: ...), so "قال:" tokenizes as قال, not an unmatchable "قال:".
    return [w for w in re.split(r'[\s،.؟!:؛…"«»”“\-—()]+', sent.strip()) if w]

def annotate_word(lex, surface, res):
    key = norm(surface)
    c = curated.numeral(surface) or curated.lookup(surface, key)
    if not c:
        # Proper nouns take clitics too (بكييف = بـ + كييف, وأمريكا = وـ + أمريكا).
        #
        # NOTE: this branch can eat a real word's opening letters to reach a curated FUNCTION
        # word: الله and الهوا both read as الـ+له "to him", كلهم as أكل "eat" — 14 tokens
        # corpus-wide. Two one-line fixes were tried and both made things worse. Refusing
        # short stems promotes a worse reading, because morph()'s order is load-bearing
        # (منها stopped being مِن "from" and became اليَمَن "Yemen"); adding الله to
        # curated.PROPER then pulled الآلة, الهوا and كلهم onto "God" as well. This needs
        # per-token adjudication alongside the AMBIGUOUS queue, not a heuristic here.
        # The app corrects the handful that matter at display time — see LEX_FIX in index.html.
        # A THIRD attempt at restricting this branch, and a third one that measured worse. The
        # Hebrew side fixed the identical bug by letting a curated name be reached only through
        # a PREFIX, and here that costs 1,085 tokens: Arabic's prepositions carry their pronoun
        # as a SUFFIX, and عليه معي منه عنه بينهم are exactly what this table is for. Reached
        # by prefix alone they fall back to the lexicon and become "attic", "bleat", "because
        # of". The suffix path is load-bearing; it is the short curated ENTRIES that are unsafe,
        # not the path that finds them.
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
        data=json.dumps({"text": text,
            "model_id": os.environ.get('ELEVENLABS_MODEL', 'eleven_multilingual_v2')}).encode(),
        headers={"xi-api-key": api_key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90, context=_SSL) as r:
            open(out_path, 'wb').write(r.read())
        return True, "generated"
    except urllib.error.HTTPError as e:
        return False, "HTTP %s — %s" % (e.code, e.read().decode('utf-8', 'replace')[:150])
    except Exception as e:
        return False, str(e)[:120]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--audio', action='store_true', help='generate MP3s (needs env keys)')
    # paths.py reads this from argv before argparse ever runs. It is declared so the flag can be
    # PASSED -- which is the whole point, a child that is not told its language runs as the
    # default and writes into the wrong tree. Not declaring it here is what turned "the Hebrew
    # annotator ran as Arabic" into "neither language annotated at all".
    ap.add_argument('--lang', default=paths.LANG, choices=paths.LANGS, help=argparse.SUPPRESS)
    a = ap.parse_args()

    SUB = os.environ.get('PAL_SUBDIALECT', 'urban')
    src = json.load(open(a.source, encoding='utf-8'))
    # Some files under texts/ aren't sentence-texts (e.g. the reaction DRILL uses `items`, not
    # `sentences`, and gets its audio from car_session.py). Skip those cleanly so a batch loop
    # over texts/*.json doesn't crash on them.
    if 'sentences' not in src:
        print(f"skip {os.path.basename(a.source)}: not a sentence-text (no 'sentences' key)")
        return
    lex, res = Lexicon(), load_resolutions()
    outdir = paths.build(src['id'])
    os.makedirs(os.path.join(outdir, 'audio'), exist_ok=True)

    # Voice comes from pipeline/voice.py (env var overrides) so it can never silently
    # differ between runs — only the KEY has to be supplied.
    key, voice = os.environ.get('ELEVENLABS_API_KEY'), voice_id()
    do_audio = a.audio and key and voice
    if a.audio and not do_audio:
        print("!! --audio requested but ELEVENLABS_API_KEY not set;"
              " emitting artifact with audio: null\n")

    art = {"id": src['id'], "title": src['title'], "dialect": src.get('dialect', 'pal'),
           "kind": src.get('kind', 'lesson'), "date": src.get('date'),
           "level": src.get('level'),          # beginner/intermediate/advanced (stories)
           "book": src.get('book'), "chapter": src.get('chapter'),   # book grouping (book chapters)
           "book_title": src.get('book_title'),
           "shelf": src.get('shelf', 0),       # running order of books on the Books shelf
           "book_meta": src.get('book_meta'),  # the public-domain work this retells
           "subdialect": SUB,
           "source": src.get('source', 'original'), "sentences": []}
    stats = {}
    for si, s in enumerate(src['sentences']):
        words = [annotate_word(lex, w, res) for w in tokenize(s['ar'])]
        for w in words:
            stats[w['provenance']] = stats.get(w['provenance'], 0) + 1
        for wi, w in enumerate(words):
            w['caphi_urban'] = realize(w.get('caphi_raw') or w.get('caphi'), SUB)
            # Who is doing the verb? بشتغل is "I work" AND "he works" — same letters, and
            # only the subject tells them apart. The word before it usually says: an explicit
            # أنا makes it first person, a noun or a he/she/they pronoun makes it third.
            prev = words[wi - 1] if wi else None
            ps = (prev or {}).get('surface', '')
            pa = str((prev or {}).get('analysis') or '')
            subj = None
            if ps in ('أنا', 'انا', 'وأنا', 'وانا'): subj = '1sg'
            elif pa.startswith(('NOUN', 'ADJ')) or ps in ('هو', 'هي', 'هم', 'همه', 'هنّ', 'هُمّة'):
                subj = '3'
            w['_subject'] = subj
            # SPEC 7.4.6: vocalize the SURFACE form from the lexicon's citation form.
            # Curated entries already carry their own vocalization and must NOT be
            # relabelled as lexicon-sourced — that would launder hand-written data.
            if str(w.get('provenance','')).startswith('curated'):
                w.setdefault('vocalized', w.get('form'))
                w['vocalized_from'] = 'curated'
            else:
                v, vp = vocalize(w['surface'], w.get('form'), w.get('analysis'), w.get('_subject'))
                w['vocalized'], w['vocalized_from'] = v, vp
            w.pop('_subject', None)
        sent = {"ar": s['ar'], "en": s['en'], "p": s.get('p'), "words": words, "audio": None}
        # ALWAYS adopt a clip that already exists on disk — with or without an API key, and
        # whether or not this run generates audio. This used to say `if do_audio:` only, so a
        # re-ingest without a key (or a run that hit an ElevenLabs credit limit part-way) wrote
        # audio:null over texts whose mp3s were sitting right there, and the app showed
        # "no audio yet" for material we already had.
        ap = os.path.join(outdir, 'audio', f"s{si}.mp3")
        if os.path.exists(ap):
            sent['audio'] = f"audio/s{si}.mp3"
        elif do_audio:
            ok, how = tts(s['ar'], ap, key, voice)
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
    if amb: print(f"!! {amb} ambiguous — add ids to {os.path.relpath(RESOLUTIONS, ROOT)}")
    if unres: print(f"!! {unres} unresolved — not in Maknuune; needs a human")
    if not amb and not unres: print("clean: every word traced to a real lexicon entry")

if __name__ == '__main__':
    main()
