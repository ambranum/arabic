#!/usr/bin/env bash
# Regenerate Palestinian audio with a chosen ElevenLabs voice, then rebuild the app data.
# Runtime TTS is avoided (it would expose the key on a public page), so clips are pre-generated
# here and committed.
#
# WHY THE DELETE STEP: vocab_audio.py and ingest.py cache clips by CONTENT hash, not by voice —
# a given word/sentence always maps to the same filename. So to actually SWITCH voices we must
# remove the old clips first; otherwise the cached (old-voice) files are reused.
#
# Usage (your key stays in your terminal; never commit it):
#   # cheap + fast: re-voice ONLY the flashcard words (the most-heard audio) so you can audition the voice
#   ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=oJQlz7pz2yWd7MRmDUXm bash pipeline/regen_audio.sh words
#
#   # just the sentences: re-voice stories/news/book (keeps the flashcard words as-is)
#   ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=oJQlz7pz2yWd7MRmDUXm bash pipeline/regen_audio.sh sentences
#
#   # everything: flashcard words + every story/news/book sentence (~2,300 clips — real credits)
#   ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=oJQlz7pz2yWd7MRmDUXm bash pipeline/regen_audio.sh all
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
MODE="${1:-all}"

: "${ELEVENLABS_API_KEY:?set ELEVENLABS_API_KEY in your terminal}"
: "${ELEVENLABS_VOICE_ID:?set ELEVENLABS_VOICE_ID in your terminal}"

if [ "$MODE" = "words" ]; then
  echo "Re-voicing FLASHCARD WORDS ONLY with voice: $ELEVENLABS_VOICE_ID"
  echo "  (sentence audio for stories/news/books is left as-is — run 'all' later for those)"
  echo
  echo "1/2  removing cached word clips so the new voice regenerates…"
  rm -rf app/audio/vocab
  echo "2/2  per-word vocabulary audio (writes app/audio/vocab + the manifest)…"
  python3 pipeline/vocab_audio.py
  echo
  echo "Done. Audition it (open the app, play a card), then commit:"
  echo "  git add app/audio/vocab app/data/vocab_audio.js && git commit -m 'Audio: re-voice flashcard words' && git push"
  exit 0
fi

if [ "$MODE" = "sentences" ]; then
  echo "Re-voicing SENTENCE audio (stories, news, book) with voice: $ELEVENLABS_VOICE_ID"
  echo "  Flashcard words are left as-is. Already-regenerated book-chapter clips are reused (not re-billed)."
  echo
  echo "1/3  removing old story/news sentence clips so they regenerate (keeping words + book)…"
  rm -rf build/story-*/audio build/news-*/audio build/morning-coffee/audio 2>/dev/null || true
  find app/audio -mindepth 1 -maxdepth 1 -type d ! -name vocab -exec rm -rf {} + 2>/dev/null || true
  echo "2/3  per-sentence audio (book chapters cached; stories/news regenerate; drill skipped)…"
  for f in texts/*.json; do python3 pipeline/ingest.py "$f" --audio; done
  echo "3/3  rebuilding app/data/library.js and copying clips into app/…"
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
rm -rf app/audio/* build/*/audio
echo "2/4  per-word vocabulary audio…"
python3 pipeline/vocab_audio.py
echo "3/4  per-sentence audio for every text (stories, news, book chapters; the drill is skipped)…"
for f in texts/*.json; do python3 pipeline/ingest.py "$f" --audio; done
echo "4/4  rebuilding app/data/library.js and copying clips into app/…"
python3 pipeline/build_app.py
echo
echo "Done. Give it a listen, then commit:"
echo "  git add -A && git commit -m 'Audio: switch to ElevenLabs voice $ELEVENLABS_VOICE_ID' && git push"
