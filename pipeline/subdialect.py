"""Sub-dialect realization.

Maknuune's CAPHI++ does not give one pronunciation — it gives a TEMPLATE. Uppercase
consonants are the sub-dialect *variables*, and they are exactly the three that vary
across Arabic: Q=ق (3140 uses), J=ج (3415), K=ك (549). Maknuune even ships explicit
alternations (q||K, Z||D).

So "Qahwe" is not "qahwe". It is qaf+ahwe, and the sub-dialect decides:
    urban   Q->2   ahwe      (Jerusalem/Ramallah/Nablus)
    rural   Q->k   kahwe     (fellahi)
    bedouin Q->g   gahwe

This MUST match the TTS voice. Ours is Voice-Designed "from Ramallah" = urban, so urban
is the default. A mismatch here would print one pronunciation and speak another.
"""

REALIZATION = {
    # Jerusalem / Ramallah / Nablus — matches our Voice Design prompt.
    # NB: J->j (dʒ), NOT zh. [ʒ] is Lebanese/Syrian jim; Palestinian keeps the affricate.
    # Getting this wrong would give the learner a Beirut accent while the voice says Ramallah.
    "urban":   {"Q": "2",  "J": "j",  "K": "k"},
    # fellahi / village
    "rural":   {"Q": "k",  "J": "dj", "K": "tsh"},
    "bedouin": {"Q": "g",  "J": "dj", "K": "k"},
    # keep the variables visible — useful for debugging, useless for learners
    "raw":     {},
}

def realize(caphi, sub="urban"):
    """Resolve CAPHI++ variables for a sub-dialect. Input is space-separated phonemes."""
    if caphi is None: return None
    rules = REALIZATION.get(sub, {})
    out = []
    for tok in str(caphi).split():
        if "||" in tok:                       # explicit alternation, e.g. q||K
            a, b = tok.split("||", 1)
            tok = rules.get(b.strip(), a.strip()) if b.strip() in rules else a.strip()
        elif tok in rules:
            tok = rules[tok]
        else:
            for var, val in rules.items():    # variable inside a cluster, e.g. KK
                if var in tok: tok = tok.replace(var, val)
        out.append(tok)
    return "".join(out)

if __name__ == "__main__":
    tests = ["Q a h w e", "y u Q 3 u d", "b a K K ii r", "f i n J aa n", "2 i b r e"]
    print("%-16s %-10s %-10s %-10s" % ("CAPHI++", "urban", "rural", "bedouin"))
    print("-"*50)
    for t in tests:
        print("%-16s %-10s %-10s %-10s" % (t.replace(' ',''),
              realize(t,'urban'), realize(t,'rural'), realize(t,'bedouin')))
