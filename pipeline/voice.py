"""The canonical ElevenLabs voice for this app — recorded in the repo, on purpose.

WHY THIS FILE EXISTS. The voice id used to live only in an environment variable, so
nothing in the repo knew which voice any given clip was spoken in. That went wrong twice:

  * the story/news/book SENTENCE clips silently stayed on the old voice while the
    flashcard WORD clips moved to the new one, and nothing flagged the mismatch;
  * the daily-news GitHub Action passed its own `ELEVENLABS_VOICE_ID` secret, so every
    new day's news came back in the OLD voice even after the switch — an override no one
    could see from the code.

SPEC.md already called this out: "a voice you can't retrieve isn't a dependency, it's an
anecdote." So the id lives here now, in version control. It is NOT a secret — a voice id
is a public identifier, useless without the API key (which stays in your terminal and is
never committed).

PRECEDENCE: VOICE_ID below WINS. An `export ELEVENLABS_VOICE_ID=<old voice>` left over in a
terminal is exactly what re-voiced a whole corpus back into the OLD voice while every commit
message said otherwise — the run "succeeded", the bytes changed, and only the timbre gave it
away. So a stale env var can no longer quietly override the pin: to use a different voice you
must ALSO set ELEVENLABS_VOICE_OVERRIDE=1, which is deliberate rather than forgotten.
"""
import os

# The voice every clip in this app should be spoken in.
VOICE_ID = "oJQlz7pz2yWd7MRmDUXm"
MODEL_ID = "eleven_multilingual_v2"

# Voices this project has used before, kept so old clips can be identified later.
PREVIOUS = {
    "8sSDN08XkFeN2zqNwCZk": "original Voice-Designed 'Ramallah' voice — used for the first "
                            "word clips (63e1db7) and all sentence clips (61c1fda)",
}

def voice_id():
    """The voice to synthesize with. The pin wins unless overriding is opted into explicitly."""
    env = os.environ.get("ELEVENLABS_VOICE_ID")
    if env and env != VOICE_ID:
        if os.environ.get("ELEVENLABS_VOICE_OVERRIDE") == "1":
            return env
        print("!! ignoring ELEVENLABS_VOICE_ID=%s from the environment — the pinned voice is %s."
              "\n   (set ELEVENLABS_VOICE_OVERRIDE=1 too if you really mean to use a different voice)"
              % (env, VOICE_ID))
    return VOICE_ID

def model_id():
    return os.environ.get("ELEVENLABS_MODEL") or MODEL_ID

if __name__ == "__main__":
    v = voice_id()
    print("voice: %s%s" % (v, "  (env override)" if v != VOICE_ID else "  (pinned in voice.py)"))
    print("model: %s" % model_id())
