#!/usr/bin/env bash
# Regenerate ALL Palestinian audio (per-word vocabulary + per-sentence) with a chosen ElevenLabs
# voice, then rebuild the app data. Runtime TTS is avoided (it would expose the key on a public
# page), so the clips are pre-generated here and committed.
#
# WHY THE DELETE STEP: vocab_audio.py and ingest.py cache clips by CONTENT hash, not by voice —
# a given word/sentence always maps to the same filename. So to actually SWITCH voices we must
# remove the old clips first; otherwise the cached (old-voice) files are reused.
#
# Usage (your key stays in your terminal; never commit it):
#   ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=oJQlz7pz2yWd7MRmDUXm bash pipeline/regen_audio.sh
#
# NOTE: this re-synthesizes every clip (~2,300), so it uses a real chunk of ElevenLabs credits.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${ELEVENLABS_API_KEY:?set ELEVENLABS_API_KEY in your terminal}"
: "${ELEVENLABS_VOICE_ID:?set ELEVENLABS_VOICE_ID in your terminal}"
echo "Regenerating all audio with voice: $ELEVENLABS_VOICE_ID"
echo

echo "1/4  removing cached clips so the new voice actually regenerates…"
rm -rf app/audio/* build/*/audio

echo "2/4  per-word vocabulary audio (writes app/audio/vocab + the manifest)…"
python3 pipeline/vocab_audio.py

echo "3/4  per-sentence audio for every text (stories, news, book chapters)…"
for f in texts/*.json; do python3 pipeline/ingest.py "$f" --audio; done

echo "4/4  rebuilding app/data/library.js and copying clips into app/…"
python3 pipeline/build_app.py

echo
echo "Done. Give it a listen, then commit:"
echo "  git add -A && git commit -m 'Audio: switch to ElevenLabs voice $ELEVENLABS_VOICE_ID' && git push"
