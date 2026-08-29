# Hebrew spike — Stage A

Nothing here is wired into the app. This is the gate described in the plan: find out in a week,
rather than a quarter, whether a Modern Hebrew module can keep the project's central promise —
**word metadata is looked up, never generated** — when there is no Maknuune for Hebrew.

## Get the data

```bash
curl -o spike/he/kaikki-hebrew.jsonl \
  https://kaikki.org/dictionary/Hebrew/kaikki.org-dictionary-Hebrew.jsonl
```

55 MB, gitignored, regenerable. English Wiktionary's Hebrew entries as machine-readable JSONL
(kaikki.org / wiktextract), **CC BY-SA** — the same licence family as Maknuune, so the repo's
existing ShareAlike posture in `data/ATTRIBUTION.md` carries over without change.

17,744 entries. 16,428 of them (93%) carry all three of a pointed spelling, a Modern Israeli
romanization, and an English gloss. It also ships the plural, the construct, the feminine, the
noun *pattern*, and gender — most of what a lexicon row needs.

## Files

| | |
|---|---|
| `phon.py` | Pointed Hebrew → Modern Israeli pronunciation. Deterministic, no lexicon. `--selftest` |
| `verify_phon.py` | Scores `phon.py` against every Wiktionary romanization. The oracle. |
| `build_lex.py` | The dump → `hebrew_lex.parquet`. Maknuune's column contract. |
| `lex.py` | Lookup + clitic peeling. The Hebrew `pipeline/maknuune.py`. |
| `coverage.py` | **The gate.** Scores the lexicon against live Hebrew news. |

## A1 — the gate: 94.7%

```
$ python3 spike/he/coverage.py --n 300
lexicon: 176,610 rows, 109,168 distinct keys      corpus: 300 sentences, 7,137 tokens

  wiktionary:exact               1842   25.8%
  wiktionary:clitic              1072   15.0%
  wiktionary:ktiv                 173    2.4%
  AMBIGUOUS-needs-resolution     3560   49.9%
  acronym (not lexical)           119    1.7%
  unresolved                      371    5.2%

  GOT lemma+gloss+POS            6647   94.7%   <- bar was 90%
```

**Passes.** Corpus is live RSS from Ynet, Walla, Israel Hayom and Maariv — the text the Hebrew
news module would actually ingest on day one, unfiltered and not chosen to flatter the number.

The lexicon is **176,610 rows over 12,662 lemmas**, and the reason it works at that lemma count
is that Wiktionary ships whole paradigms: every person of every tense for verbs, the possessed
forms for nouns, plurals and constructs. 109,168 distinct surface keys. It also carries the
binyan for 56,807 verb rows and a root for 22,429 — so `BINYAN` and `ROOT` are looked up, not
inferred, which is more than the Arabic side manages.

### The 5.2% that misses is almost entirely names

Smotrich, Trump, Jenin, Feiglin, Gantz, Erdan, Khamenei, Ratcliffe, Hezbollah. Proper nouns are
not a lexicon's job and never were — `pipeline/curated.py` has a `PROPER` dict for exactly this
on the Arabic side, and Hebrew needs the same table. The genuine word misses in the top 25 are
four: נעדרים, באמצעות, אינטימיות, הפיננסית.

### The real finding: Hebrew is half ambiguous

**49.9% of tokens match more than one lemma, against 32.5% for Arabic.** That is not a defect in
the lexicon and it did not move when root and acronym pseudo-entries were filtered out — it is
what unpointed Hebrew *is*. חיות is *xayot* (animals) or *xayut* (vitality); בשום is "in no" or
"with garlic"; לנו is "to us" or "he stayed the night".

Ambiguity is a normal state in this pipeline, not a failure — the Arabic side resolves it with
one Claude call per text that picks from the real candidate list and is rejected if it invents
an id. Hebrew needs the same call, roughly 1.5× as often.

There is an obvious lever not yet pulled: **run the text through DICTA's Nakdan first.** Adding
niqqud is precisely what disambiguates Hebrew, and the lexicon is already keyed on pointed
forms. That should collapse most of the 49.9% before any API call is made. Untested here; it is
the first thing to try in Stage C, and the reason the Hebrew news job may end up cheaper than
the Arabic one rather than dearer.

## Why there is an oracle

Wiktionary prints a Modern Israeli romanization beside the pointed spelling. That gives 14,710
pointed/romanized pairs written by people who were not us — the same role the Lingualism verb
book plays for Arabic in `pipeline/verify_conjugation.py`. It is a far better test set than any
list I could hand-build: it is large, it was not chosen by whoever wrote the rules, and it
covers the long tail where rules actually break.

It earned its keep immediately. Four rules I was confident about were wrong, and the oracle said
so in numbers rather than in argument:

| Rule I believed | Measured |
|---|---|
| Initial shva is pronounced (*beraxa*) | **Wrong.** Silent wins by 11.2pp — Israelis say *braxa* |
| Second of two adjacent shvas is pronounced | **Wrong.** Costs 1.1pp |
| Shva under a dagesh hazaq is pronounced | **Wrong.** Costs 1.5pp |
| Qamatz in a closed unstressed syllable is *o* | **Wrong.** 60 false positives, costs 0.3pp |

And one rule I had missed entirely turned out to be worth more than any of them: the **patach
genuva**, where a final ח/ע/הּ takes its vowel *before* the letter — מָשִׁיחַ is *mashiakh*, not
"mashixa". 205 words, +1.25pp, completely regular.

Net: **88.75% → 95.36%.**

## Where it stands against the bar

The plan set 99%. It is at 95.36%, and the honest reading is that the bar was aimed at the wrong
thing.

The residue is not noise — it is three known things: initial-shva words where Hebrew genuinely
has two registers (*rexov* vs *rxov*), the `-iya`/`-ia` and `ei`/`ey` notation choices, and
qamatz qatan, which is lexical and not derivable from spelling at all.

All three are handled the same way, and it is the way the Arabic side already works: **the
lexicon carries the pronunciation, and the transducer is the fallback.** Wiktionary gives a
romanization for 16,428 entries outright. Those are looked up, not computed. `phon.py` only runs
on what the lexicon doesn't have — inflected forms, compounds, names, novel text — which is
exactly the generalization job, and 95% on unseen material is a good number for it.

So the bar that matters is not "does the rule reproduce the dictionary" but "what fraction of
running text gets a pronunciation from *somewhere* trustworthy". That is an A1 question, and it
is what the coverage measurement is for.

## A3 — the verbs: 98.99%, and no engine needed

The plan asked for a conjugation engine per binyan, verified against Pealim at ≥98%. A1 changed
the question, because Wiktionary does not just give Hebrew lemmas — it gives **whole pointed
conjugation tables**.

```
$ python3 spike/he/verbs_he.py
verb entries with any pointed cell: 2084
with ALL 24 slots filled          : 1906  (91%)

  paal 650 · piel 532 · hifil 365 · hitpael 256 · nifal 121 · pual 104 · hufal 53 · hitpual 2
```

For Arabic there was no choice: Maknuune has principal parts and nothing else, so
`pipeline/conjugate.py` derives 30 cells from three, and the whole apparatus of per-measure
engines and parse gates exists to make that derivation trustworthy. Hebrew arrives with the
tables filled in, from a source we can ship.

**So the paradigms are looked up, not generated** — which is the project's own rule, applied
more strictly than the Arabic side manages. An engine is still worth building later for verbs
outside Wiktionary's table set, but it is not on the critical path, and Pealim is not needed as
an oracle. It stays available and stays unshipped.

### Are the tables right? 98.99%

Wiktionary romanizes the lemma, and for a Hebrew verb the lemma **is** the 3ms past — the same
cell the app banks a flashcard under. So every verb hands us a free cross-check of extraction
plus phonology against a transcription we did not write:

| binyan | | | binyan | | |
|---|---|---|---|---|---|
| paal | 619/623 | 99.4% | pual | 69/69 | 100% |
| piel | 364/366 | 99.5% | hufal | 27/27 | 100% |
| hifil | 346/353 | 98.0% | nifal | 113/113 | 100% |
| hitpael | 228/233 | 97.9% | hitpual | 2/2 | 100% |

**1768/1786 = 98.99%**, uniform across all seven binyanim. Clears the bar.

It did not start there. The first run said 87% overall with piel at 71% and pual at 13% — which
was a bug in the *harness*, not the data: I keyed the romanization map on the normalized lemma,
and unpointed מהר is both מָהַר (paal, hurry) and מִהֵר (piel, hasten), so it was comparing one
binyan's cell against the other's transcription. Keying on the pointed form fixed it. That is
the A1 ambiguity finding showing up as a measurement error, which is worth remembering: **in
Hebrew, an unpointed key is not an identifier.**

### Do the verbs a learner meets have one? 91%

Over the same live news corpus: **91.0% of verb tokens** and 92.2% of distinct verb lemmas
resolve to a verb that has a paradigm.

### Two real fixes this turned up

- **Infinitives were missing entirely.** wiktextract cannot label the Hebrew infinitive and
  files it as `error-unrecognized-form` — 2,671 rows. They were being dropped, taking לכתוב,
  לדבר, לעשות and להיות with them. Now relabelled on the way in, which pushed exact matches
  from 25.8% to 27.0% of tokens and cut the number resolved by clitic guessing.
- **The shva rule differs inside a verb.** יִכְתְּבוּ is *yixtevu*, not the *yixtvu* the general
  rule gives, because the prefix has already closed a syllable. This is switched on only when
  the caller knows it is looking at a verb cell (`phon(form, verb=True)`), because as a general
  rule it costs 1.1pp — in nouns the same shape resolves the other way (אַנְגְּלִית is *anglit*).
  The A2 known gap is now closed where it mattered and left alone where it did not.

## Known gaps

`phon.py --selftest` prints these rather than hiding them. Currently one: a shva between two
consonants of a verb is pronounced (יִכְתְּבוּ = *yixtevu*) and that is not derivable from the
spelling — it needs the paradigm. Verb pronunciations come from the conjugation engine (A3),
which knows the paradigm, so this transducer never sees them.
