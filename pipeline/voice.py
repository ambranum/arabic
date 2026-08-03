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

Precedence: ELEVENLABS_VOICE_ID (if you deliberately set it) > VOICE_ID below. Scripts
call voice_id(), so with no env var set they all agree on the same voice by default.
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
    """The voice to synthesize with. Env var wins so one-off experiments stay possible."""
    return os.environ.get("ELEVENLABS_VOICE_ID") or VOICE_ID

def model_id():
    return os.environ.get("ELEVENLABS_MODEL") or MODEL_ID

if __name__ == "__main__":
    print("voice: %s%s" % (voice_id(),
          "  (from ELEVENLABS_VOICE_ID)" if os.environ.get("ELEVENLABS_VOICE_ID") else "  (repo default)"))
    print("model: %s" % model_id())
