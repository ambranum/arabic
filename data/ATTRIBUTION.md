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
   CAPHI transcriptions, so **`build/` and `app/data/<lang>/library.js` are CC BY-SA 4.0 too.**

Publishing this repo publicly (which GitHub Pages on a free account requires) is
redistribution. That's permitted — with the notice above kept intact.

Not derived from Maknuune, and not covered by its licence: the pipeline code, the app,
and the Palestinian sentences written by Claude.

---

# Bible section — two sources, two very different statuses

## Arabic column — Van Dyck (1865). PUBLIC DOMAIN.

`data/bible-vandyck/*.usfm` is the Smith & Van Dyke Arabic translation, downloaded from
ebible.org (id `arb-vd`), which states its status as **Public Domain**. It is committed here
(source) and processed by `pipeline/bible.py` into `app/data/<lang>/bible/*.js` +
`app/data/<lang>/bible-index.js`. Public domain imposes no obligation; the note here is courtesy.

## English column — ESV. NOT stored; fetched with the user's own key.

The English Standard Version is © Crossway and **may not be redistributed**, so **no ESV
text is stored anywhere in this repository**. The app fetches passages at runtime from
`api.esv.org` using an API key the user obtains themselves from Crossway and pastes into the
app; the key lives only in that browser's localStorage (`alp.esv.key`), is never committed,
and is sent only to Crossway. Fetched chapters are cached in the user's own browser for their
personal reading. Each user is responsible for their own key and Crossway's API terms.

## Spoken dialect New Testament — linked, never copied.

A spoken Galilean/Palestinian New Testament exists but only inside YouVersion (display-only,
not redistributable), so it is **linked out to, chapter by chapter**, never embedded.

---

# Videos section — Shami Speaker (YouTube). EMBEDDED, never copied.

The Videos section embeds playlists from the **Shami Speaker** YouTube channel
(https://www.youtube.com/@ShamiSpeaker), a Levantine Arabic learning channel with a northern-
Palestinian / southern-Lebanon-camp focus. Playback uses YouTube's official privacy-enhanced
iframe (`youtube-nocookie.com`); **no video or audio is downloaded, transcribed, or re-hosted**,
and the content is deliberately kept OUTSIDE the lexicon pipeline (no tappable words, no decks),
so the app's own dialect-verified material stays distinct from this broader-Levantine immersion.
Only the public playlist ids are stored (in `app/index.html`). Each playlist credits the channel
and links back to it. This is embedding/linking under YouTube's Terms of Service — not
redistribution of the creator's content.

---

# Plan dashboard / streak / notification model — arabic-drill (MIT), design credit.

The Plan's **dashboard, streak, and the (follow-up) lock-screen Web-Push model** are inspired by
`github.com/willmanidis2/arabic-drill` (MIT) — its home-screen "due count, streak, session
modes", its analytics page (14-day chart, deck spread, trouble cards), and its VAPID-signed Web
Push flow that turns due work into a real lock-screen notification. No code or content is copied
from that repo; only the interaction design is credited here.
