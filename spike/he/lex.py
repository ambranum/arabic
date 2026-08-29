#!/usr/bin/env python3
"""Lookup over hebrew_lex.parquet. The Hebrew counterpart of pipeline/maknuune.py.

Same contract, same discipline: retrieve real candidates, report how confident the match is,
and never invent an entry. The differences from the Arabic side are all Hebrew's:

  * PROCLITICS ARE A SLOT SYSTEM, NOT A LIST. Hebrew stacks its one-letter particles in a fixed
    order -- ו, then ש or כש, then one of ב/כ/ל/מ, then ה -- so ומהבית and וכשהילד are both
    ordinary words. Enumerating the ~90 attested combinations by hand would be error-prone and
    would miss the rare ones; generating them from the slot model is both shorter and complete.

  * KTIV MALE IS THE REAL PROBLEM. Unpointed Hebrew adds vowel letters that pointed Hebrew
    leaves out -- יכתוב for יִכְתֹּב, תוכנית for תָּכְנִית. Running text is written one way and
    the lexicon's pointed forms the other, so a plain string match misses. This is handled as a
    LAST resort with an explicit `ktiv` provenance, never folded into the key: collapsing every
    optional yod and vav would merge genuinely different words.

Provenance strings match the Arabic pipeline's vocabulary so ingest.py can treat them alike:
`wiktionary:exact`, `wiktionary:clitic`, `wiktionary:ktiv`, `AMBIGUOUS-needs-resolution`,
`unresolved`.
"""
import itertools
import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PARQUET = os.path.join(HERE, 'hebrew_lex.parquet')

# The proclitic slots, in the order Hebrew stacks them. A word may take one from each, so the
# attested set is the product -- ו + כש + ל + ה is a real (if rare) prefix.
SLOTS = [['', 'ו'], ['', 'ש', 'כש'], ['', 'ב', 'כ', 'ל', 'מ'], ['', 'ה']]
PREFIXES = sorted({''.join(p) for p in itertools.product(*SLOTS)} - {''},
                  key=len, reverse=True)

# Possessive and object suffixes. Longest first so ־יהם is tried before ־ם.
SUFFIXES = ['ותיהם', 'ותיהן', 'ותיכם', 'ותיכן', 'יהם', 'יהן', 'יכם', 'יכן', 'ינו', 'ותי',
            'תיו', 'תיה', 'נו', 'כם', 'כן', 'הם', 'הן', 'יו', 'יה', 'יך', 'יי', 'ני',
            'ם', 'ן', 'י', 'ך', 'ו', 'ה']
MIN_STEM = 2

MATRES = re.compile('[וי]')


class Lexicon:
    def __init__(self, path=PARQUET):
        df = pd.read_parquet(path)
        self.df = df
        recs = df.to_dict('records')
        self.by_form = {}
        self.by_lemma = {}
        for r in recs:
            self.by_form.setdefault(r['FORM_SEARCH'], []).append(r)
            self.by_lemma.setdefault(r['LEMMA_SEARCH'], []).append(r)
        # For ktiv male/haser: index every entry under a skeleton with the vowel letters
        # removed. Lossy on purpose, and only ever consulted after everything else has failed.
        self.by_skeleton = {}
        for k, v in self.by_form.items():
            self.by_skeleton.setdefault(MATRES.sub('', k), []).extend(v)

    # -- the peeler ----------------------------------------------------------------------
    def stems(self, w):
        """Every (stem, what-was-stripped) the clitic slots can produce, longest strip first."""
        out = [(w, '')]
        for p in PREFIXES:
            if w.startswith(p) and len(w) - len(p) >= MIN_STEM:
                out.append((w[len(p):], p + '-'))
        for s in SUFFIXES:
            if w.endswith(s) and len(w) - len(s) >= MIN_STEM:
                out.append((w[:-len(s)], '-' + s))
                for p in PREFIXES:
                    if w.startswith(p) and len(w) - len(p) - len(s) >= MIN_STEM:
                        out.append((w[len(p):-len(s)], p + '-' + s))
        seen, uniq = set(), []
        for st, cut in out:
            if st not in seen:
                seen.add(st)
                uniq.append((st, cut))
        return uniq

    def _hit(self, key):
        return self.by_form.get(key) or self.by_lemma.get(key)

    def look(self, surface):
        """-> (records, provenance, what_was_cut). records is [] when nothing was found."""
        from build_lex import he_norm
        w = he_norm(surface)
        if not w:
            return [], 'unresolved', ''
        hit = self._hit(w)
        if hit:
            return hit, 'wiktionary:exact', ''
        for stem, cut in self.stems(w)[1:]:
            hit = self._hit(stem)
            if hit:
                return hit, 'wiktionary:clitic', cut
        # last resort: the same word spelled with or without its optional vowel letters
        skel = MATRES.sub('', w)
        if len(skel) >= MIN_STEM:
            hit = self.by_skeleton.get(skel)
            if hit:
                return hit, 'wiktionary:ktiv', ''
            for stem, cut in self.stems(w)[1:]:
                hit = self.by_skeleton.get(MATRES.sub('', stem))
                if hit:
                    return hit, 'wiktionary:ktiv', cut
        return [], 'unresolved', ''

    def resolve(self, surface):
        """look(), then decide whether the answer is unique enough to use unattended."""
        recs, prov, cut = self.look(surface)
        if not recs:
            return None, 'unresolved', []
        lemmas = {r['LEMMA'] for r in recs}
        if len(lemmas) == 1:
            return recs[0], prov, recs
        # Several distinct lemmas share this spelling. Same rule as the Arabic side: do not
        # pick for the learner, hand the candidates on for adjudication.
        return recs[0], 'AMBIGUOUS-needs-resolution', recs[:6]
