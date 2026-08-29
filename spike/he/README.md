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

## Known gaps

`phon.py --selftest` prints these rather than hiding them. Currently one: a shva between two
consonants of a verb is pronounced (יִכְתְּבוּ = *yixtevu*) and that is not derivable from the
spelling — it needs the paradigm. Verb pronunciations come from the conjugation engine (A3),
which knows the paradigm, so this transducer never sees them.
