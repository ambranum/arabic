#!/usr/bin/env bash
# A/B two ElevenLabs voices on the SAME sentence, so you can hear (and measure) whether they
# actually differ at all.
#
# WHY: after a re-voice, "it still sounds like the old voice" has two very different causes —
# (a) the run used the wrong voice, or (b) the two voices genuinely sound alike (easy to end up
# with if both were Voice-Designed from similar prompts). Timbre analysis of the corpus can't
# separate those. Synthesizing one identical sentence with each id can.
#
# Your key stays in your terminal — nothing here is committed.
#   ELEVENLABS_API_KEY=sk_... bash pipeline/voice_ab.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${ELEVENLABS_API_KEY:?set ELEVENLABS_API_KEY in your terminal}"

NEW="$(python3 -c 'import sys; sys.path.insert(0,"'"$ROOT"'/pipeline"); import voice; print(voice.VOICE_ID)')"
OLD="${1:-8sSDN08XkFeN2zqNwCZk}"
OUT="$ROOT/ab_voice_test"; mkdir -p "$OUT"
TEXT="كل يوم الصبح بشرب قهوة عالبلكونة وبقعد شوي لحالي."
MODEL="${ELEVENLABS_MODEL:-eleven_multilingual_v2}"

say() {   # $1=voice id  $2=out file
  code=$(curl -s -o "$2" -w '%{http_code}' -X POST \
    "https://api.elevenlabs.io/v1/text-to-speech/$1" \
    -H "xi-api-key: ${ELEVENLABS_API_KEY}" -H "Content-Type: application/json" \
    -d "{\"text\":\"${TEXT}\",\"model_id\":\"${MODEL}\"}")
  name=$(curl -s -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
         "https://api.elevenlabs.io/v1/voices/$1" \
         | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("name","(name not readable)"))
except Exception: print("(name not readable)")' 2>/dev/null)
  if [ "$code" = "200" ] && [ -s "$2" ]; then
    echo "  OK  $1  [\"$name\"]  -> $(basename "$2")  ($(wc -c < "$2" | tr -d ' ') bytes)"
  else
    echo "  FAILED $1 (HTTP $code)"; head -c 200 "$2" 2>/dev/null; echo
  fi
}

echo "Synthesizing the same sentence with both voices…"
say "$NEW" "$OUT/NEW_${NEW}.mp3"
say "$OLD" "$OUT/OLD_${OLD}.mp3"
echo
echo "Listen to both in: $OUT"
echo "  open \"$OUT\""
echo "If they sound the SAME, the two voice ids are near-identical and re-voicing can't help —"
echo "you'd need to pick a genuinely different voice. If they sound DIFFERENT, the app's audio"
echo "should match the NEW_ file; if it doesn't, the pipeline is still using the wrong one."
