# Data attribution

## Maknuune — Palestinian Arabic Lexicon

`maknuune.parquet` is the Maknuune lexicon (36,302 entries).

> Shahd Dibas, Christian Khairallah, Nizar Habash, Omar Sadi, Tariq Sairafy,
> Karmel Sarabta, Abrar Ardah. **"Maknuune: A Large Open Palestinian Arabic Lexicon."**
> Proceedings of the Seventh Arabic Natural Language Processing Workshop (WANLP), 2022.
> https://aclanthology.org/2022.wanlp-1.13/ · https://palestine-lexicon.org/

**Licence: CC BY-SA 4.0.** Two obligations that bind this repository:

1. **Attribution** — this notice.
2. **ShareAlike** — anything derived from the lexicon must carry the same licence.
   The annotated artifacts under `build/` embed Maknuune roots, lemmas, glosses and
   CAPHI transcriptions, so **`build/` and `app/data/library.js` are CC BY-SA 4.0 too.**

Publishing this repo publicly (which GitHub Pages on a free account requires) is
redistribution. That's permitted — with the notice above kept intact.

Not derived from Maknuune, and not covered by its licence: the pipeline code, the app,
and the Palestinian sentences written by Claude.

---

# Design credits (no code or content used)

Separate from the licence obligations above — nothing here binds this repository, and
nothing here is redistributed. Recorded because the ideas were worth crediting.

## willmanidis2/arabic-drill (MIT)

https://github.com/willmanidis2/arabic-drill — "zero-dependency spaced repetition for
Levantine Arabic."

The **Practice** section's three formats (four-option multiple choice with semantic
distractors, fill-in-the-paradigm, matching round) and the **same-day learning ladder**
(10 min → 30 min → 2 hours before day-level intervals) are modelled on that project.

**No code and no card content were copied.** Every drill item in this app is generated at
runtime from our own data: Maknuune-looked-up lemmas in the user's deck, the verb paradigms
derived by `pipeline/build_verbs.py`, and the curated grammar tables. The MIT licence's
condition applies to "copies or substantial portions of the Software," so it imposes no
obligation here; this credit is a courtesy.

Because drill items are generated from `app/data/library.js` and `app/data/verbs.js`, they
**inherit CC BY-SA 4.0** from Maknuune — that, not MIT, is the licence that actually binds
this feature.
