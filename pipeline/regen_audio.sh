#!/usr/bin/env bash
# Regenerate Palestinian audio with a chosen ElevenLabs voice, then rebuild the app data.
# Runtime TTS is avoided (it would expose the key on a public page), so clips are pre-generated
# here and committed.
#
# WHY THE DELETE STEP: vocab_audio.py and ingest.py cache clips by CONTENT hash, not by voice —
# a given word/sentence always maps to the same filename. So to actually SWITCH voices we must
# remove the old clips first; otherwise the cached (old-voice) files are reused.
#
# The VOICE is pinned in pipeline/voice.py — you don't pass it. Only the key, which stays
# in your terminal and is never committed.
#
# Usage:
#   # cheap + fast: re-voice ONLY the flashcard words (the most-heard audio) so you can audition the voice
#   ELEVENLABS_API_KEY=... bash pipeline/regen_audio.sh words
#
#   # just the sentences: re-voice stories/news/book (keeps the flashcard words as-is)
#   ELEVENLABS_API_KEY=... bash pipeline/regen_audio.sh sentences
#
#   # everything: flashcard words + every story/news/book sentence (~2,300 clips — real credits)
#   ELEVENLABS_API_KEY=... bash pipeline/regen_audio.sh all
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
MODE="${1:-all}"

: "${ELEVENLABS_API_KEY:?set ELEVENLABS_API_KEY in your terminal}"

# The pinned voice WINS over any ELEVENLABS_VOICE_ID left exported in this terminal. A stale
# export is what once re-voiced the whole corpus back into the OLD voice — the run looked
# perfect and only the audio timbre revealed it.
PINNED="$(python3 -c 'import sys; sys.path.insert(0,"pipeline"); import voice; print(voice.VOICE_ID)')"
if [ -n "${ELEVENLABS_VOICE_ID:-}" ] && [ "$ELEVENLABS_VOICE_ID" != "$PINNED" ]; then
  if [ "${ELEVENLABS_VOICE_OVERRIDE:-}" = "1" ]; then
    echo "!! using OVERRIDE voice $ELEVENLABS_VOICE_ID instead of the pinned $PINNED"
    PINNED="$ELEVENLABS_VOICE_ID"
  else
    echo "!! your terminal exports ELEVENLABS_VOICE_ID=$ELEVENLABS_VOICE_ID — IGNORING it."
    echo "   Using the pinned voice $PINNED. (ELEVENLABS_VOICE_OVERRIDE=1 to force the other.)"
  fi
fi
ELEVENLABS_VOICE_ID="$PINNED"
export ELEVENLABS_VOICE_ID

# PREFLIGHT — verify the key + voice actually work BEFORE deleting anything. This script deletes the
# old clips so the new voice regenerates; if the key is invalid/expired/out-of-credits, that delete
# would leave you with NO audio (which is exactly how the sentence audio got wiped once). So we do a
# real 1-word test synthesis first and abort — deleting nothing — if it fails.
echo "Preflight: testing the ElevenLabs key + voice…"
_tmp="$(mktemp -t elabtest).mp3"
_code=$(curl -s -o "$_tmp" -w '%{http_code}' -X POST \
  "https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"text\":\"مرحبا\",\"model_id\":\"${ELEVENLABS_MODEL:-eleven_multilingual_v2}\"}")
if [ "$_code" != "200" ] || [ ! -s "$_tmp" ]; then
  echo "!! ElevenLabs test FAILED (HTTP $_code). Likely: bad/expired key, out of credits, or the voice"
  echo "   id '${ELEVENLABS_VOICE_ID}' isn't saved in your account. NOTHING was deleted — safe to retry."
  echo "   (Server said:)"; head -c 300 "$_tmp" 2>/dev/null; echo; rm -f "$_tmp"; exit 1
fi
rm -f "$_tmp"
# Print the voice's NAME, not just its id. An id is unreadable; a name makes a wrong voice
# obvious BEFORE spending credits and overwriting a whole corpus.
_name=$(curl -s -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
        "https://api.elevenlabs.io/v1/voices/${ELEVENLABS_VOICE_ID}" \
        | python3 -c 'import sys,json;
try: print(json.load(sys.stdin).get("name","(unnamed)"))
except Exception: print("(could not read name)")' 2>/dev/null)
echo "  key OK — synthesizing with voice: ${ELEVENLABS_VOICE_ID}  [\"${_name}\"]"
echo "  ^ if that is NOT the voice you want, Ctrl-C NOW (nothing has been deleted yet)."
sleep 4

if [ "$MODE" = "words" ]; then
  echo "Re-voicing FLASHCARD WORDS ONLY with voice: $ELEVENLABS_VOICE_ID"
  echo "  (sentence audio for stories/news/books is left as-is — run 'all' later for those)"
  echo
  echo "1/2  removing cached word clips so the new voice regenerates…"
  rm -rf app/audio/*/vocab
  echo "2/2  per-word vocabulary audio (writes app/audio/<lang>/vocab + the manifest)…"
  python3 pipeline/vocab_audio.py
  echo
  echo "Done. Audition it (open the app, play a card), then commit:"
  echo "  git add app/audio/*/vocab app/data/*/vocab_audio.js && git commit -m 'Audio: re-voice flashcard words' && git push"
  exit 0
fi

if [ "$MODE" = "sentences" ]; then
  echo "Re-voicing SENTENCE audio (stories, news, book) with voice: $ELEVENLABS_VOICE_ID"
  echo "  Flashcard words are left as-is. Already-regenerated book-chapter clips are reused (not re-billed)."
  echo
  echo "1/3  removing old story/news sentence clips so they regenerate (keeping words + book)…"
  rm -rf build/*/story-*/audio build/*/news-*/audio build/*/morning-coffee/audio 2>/dev/null || true
  find app/audio -mindepth 1 -maxdepth 1 -type d ! -name vocab -exec rm -rf {} + 2>/dev/null || true
  echo "2/3  per-sentence audio (book chapters cached; stories/news regenerate; drill skipped)…"
  for f in texts/${ALP_LANG:-ar}/*.json; do python3 pipeline/ingest.py "$f" --audio; done
  echo "3/3  rebuilding app/data/<lang>/library.js and copying clips into app/…"
  python3 pipeline/build_app.py
  echo
  echo "Done. Give it a listen, then commit:"
  echo "  git add -A && git commit -m 'Audio: re-voice story/news/book sentences' && git push"
  exit 0
fi

echo "Regenerating ALL audio (words + every sentence) with voice: $ELEVENLABS_VOICE_ID"
echo "  ~2,300 clips — this uses a real chunk of ElevenLabs credits."
echo
echo "1/4  removing cached clips so the new voice regenerates…"
rm -rf app/audio/${ALP_LANG:-ar}/* build/${ALP_LANG:-ar}/*/audio
echo "2/4  per-word vocabulary audio…"
python3 pipeline/vocab_audio.py
echo "3/4  per-sentence audio for every text (stories, news, book chapters; the drill is skipped)…"
for f in texts/${ALP_LANG:-ar}/*.json; do python3 pipeline/ingest.py "$f" --audio; done
echo "4/4  rebuilding app/data/<lang>/library.js and copying clips into app/…"
python3 pipeline/build_app.py
echo
echo "Done. Give it a listen, then commit:"
echo "  git add -A && git commit -m 'Audio: switch to ElevenLabs voice $ELEVENLABS_VOICE_ID' && git push"
