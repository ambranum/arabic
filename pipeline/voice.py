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
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402  -- per-language file layout
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


# ---------------------------------------------------------------------------------------------
# The cast. A greeting and its answer are two different people; a dialogue is three or four. One
# voice reading every part is the single biggest thing that makes synthesized dialogue sound fake,
# so lessons assign a voice PER ROLE. Roles are filled from texts/voices.json — voice ids are
# public identifiers (useless without the API key), so that file is committed like this pin is.
# Unfilled roles fall back to earlier ones, so a half-filled roster degrades to fewer voices
# rather than failing.
# ---------------------------------------------------------------------------------------------
ROSTER_FILE = paths.texts("voices.json")

def roster():
    """{role: {id, name, gender, note}} for the speaking roles. 'main' is always the pin."""
    out = {"main": {"id": voice_id(), "name": "main", "gender": "m"}}
    try:
        import json
        cfg = json.load(open(ROSTER_FILE, encoding="utf-8"))
        for role, v in (cfg.get("roster") or {}).items():
            v = {"id": v} if isinstance(v, str) else dict(v or {})
            if not v.get("id"):
                continue
            if role == "main" and v["id"] != voice_id():
                # The pin is the one thing texts/voices.json may not quietly override — every
                # existing word and sentence clip in the app was spoken in it.
                print("!! %s sets main=%s but the pinned voice is %s — keeping the pin."
                      % (ROSTER_FILE, v["id"], voice_id()))
                out["main"].update({k: v[k] for k in ("name", "gender", "note") if k in v})
                continue
            out[role] = v
    except FileNotFoundError:
        pass
    except Exception as e:
        print("!! couldn't read %s (%s) — using the pinned voice for every role" % (ROSTER_FILE, e))
    return out

def _ordered_roles(r):
    order = ["main", "b", "c", "d", "e"]
    return [k for k in order if k in r] + sorted(k for k in r if k not in order)

def cast_voices():
    """The roster as an ordered list of ids: main first, then the rest. Never empty."""
    r = roster()
    seen, out = set(), []
    for role in _ordered_roles(r):
        vid = (r[role] or {}).get("id")
        if vid and vid not in seen:
            seen.add(vid); out.append(vid)
    return out or [VOICE_ID]

def cast_by_gender():
    """{'m': [ids…], 'f': [ids…]} in roster order — so a woman's lines are never read by a man."""
    r, out = roster(), {"m": [], "f": []}
    for role in _ordered_roles(r):
        v = r[role] or {}
        g = (v.get("gender") or "").lower()[:1]
        if v.get("id") and g in out and v["id"] not in out[g]:
            out[g].append(v["id"])
    return out


# Speaker names in the books are people, and half of them are women. إم فلان is "mother of…",
# ست is a lady/grandmother, بنات is "girls" — all unmistakably female; أبو and سيد are male. The
# rest fall back to a small list of the given names these particular dialogues actually use.
_F_NAMES = {"سمر", "هدى", "مي", "ميّ", "سميرة", "نور", "نهى", "امينة", "فاطمة", "ليلى", "سلمى", "رنا"}
_M_NAMES = {"عمر", "وليد", "امير", "جميل", "احمد", "رمزي", "سمير", "فتحي", "محمد", "سامي",
            "خالد", "كريم", "زياد", "ماهر", "يوسف", "حسن"}

def speaker_gender(name):
    """'f', 'm' or None for a dialogue speaker label. None means "cast me by position"."""
    n = norm_speaker(name).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    if not n:
        return None
    if n.startswith("ام ") or n.startswith("امّ") or n.startswith("ست") or "بنات" in n or "الست" in n:
        return "f"
    if n.startswith("ابو") or "السيد" in n or n.startswith("سيد"):
        return "m"
    head = n.replace("ال", "", 1) if n.startswith("ال") else n
    head = head.split()[0] if head.split() else head
    if head in _F_NAMES:
        return "f"
    if head in _M_NAMES:
        return "m"
    return None


def cast_dialogue(lines):
    """Assign a voice to each speaker in one conversation, in order of first appearance, and hold
    it for the whole scene. Prefers an unused voice of the speaker's gender; when that gender runs
    out (four men, two male voices) it reuses within the gender rather than letting a man read a
    woman's lines. Returns [{sp, voice, gender}] — one entry per distinct speaker."""
    cast_all, by_g = cast_voices(), cast_by_gender()
    roles, used, out = {}, [], []
    for l in lines or []:
        sp = norm_speaker(l.get("sp") if isinstance(l, dict) else l) or "?"
        if sp in roles:
            continue
        g = speaker_gender(sp)
        pool = by_g.get(g) or []
        pick = (next((v for v in pool if v not in used), None)
                or next((v for v in cast_all if v not in used and (not g or v in pool)), None)
                or (pool[len(out) % len(pool)] if pool else cast_all[len(out) % len(cast_all)]))
        roles[sp] = pick; used.append(pick)
        out.append({"sp": sp, "voice": pick, "gender": g})
    return out

_AR_MARKS = set("ًٌٍَُِّْٰـ")
def norm_speaker(name):
    """Same person, same voice. The books vocalize a name inconsistently across pages (وَليد on
    one, وليد on the next); without this they'd be handed different voices mid-conversation."""
    return "".join(c for c in str(name or "") if c not in _AR_MARKS).strip()

if __name__ == "__main__":
    v = voice_id()
    print("voice: %s%s" % (v, "  (env override)" if v != VOICE_ID else "  (pinned in voice.py)"))
    print("model: %s" % model_id())
