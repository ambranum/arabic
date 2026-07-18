# How to run this

Written for someone who is not a developer. Every command here is meant to be
copy-pasted exactly. You never have to understand it, only paste it.

---

> **Want it automatic?** See **GOING-LIVE.md** — hosts the app at a real URL and
> imports the news by itself every morning at 6am. This file covers running it by hand.

## The two halves

**1. The pipeline** — runs on your Mac, in Terminal. Takes Arabic text, looks up every
word in a 36,000-entry Palestinian lexicon, produces a data file. You run this when you
want to *add new content*. Maybe once a week.

**2. The app** — the `app/` folder. That whole folder **is** the website. Open it in a
browser, or upload it somewhere to use it on your phone. This is what you use *daily*.

The pipeline feeds the app. Nothing else connects them.

---

## Opening the app right now

Open **Terminal** (⌘-Space, type "Terminal"). Paste this:

```bash
cd "/Users/alexbranum/Desktop/Projects/Arabic Language Project/app" && python3 -m http.server 8000
```

Then open your browser to **http://localhost:8000**

Leave that Terminal window open while you use it. To stop, press `Ctrl-C` in Terminal.

> **Why not just double-click `index.html`?** It mostly works — the app deliberately
> avoids the one technique that breaks on double-click. But browsers restrict some things
> on files opened directly, and the command above sidesteps all of it. Use the command.

---

## Getting it on your phone

The command above only works on this Mac. For the phone — which is where the car and
drill content matter — you need it hosted. Easiest way, no account, free:

1. Go to **https://app.netlify.com/drop**
2. Drag the entire **`app`** folder onto that page
3. You get a URL. Open it on your phone. Add to Home Screen and it behaves like an app.

The `app/` folder is self-contained, so this works — audio included. Re-drag the folder
whenever you add content.

---

## The two buttons

**Today's lesson** — opens the current curriculum item. Right now that's the 30 reaction
chunks, because those come first deliberately: thirty of them let you be a real presence
at a table long before you can describe your job.

**Daily news** — today's world headlines, summarised and written in spoken Palestinian.

### How the news actually works

The app is a folder of files with no server behind it. That's why it costs nothing and
can't break — and it's also why the button can't go fetch the news itself. Summarising
headlines, writing them in Palestinian, and checking every word against a 36,000-entry
lexicon all happen on your Mac.

So the flow is:

1. **Ask Claude:** "import today's news"
2. Claude writes `texts/news-YYYY-MM-DD.json`
3. **You paste:**

```bash
cd "/Users/alexbranum/Desktop/Projects/Arabic Language Project"
python3 pipeline/ingest.py texts/news-$(date +%F).json
python3 pipeline/build_app.py
```

4. Reload the app — it's on the home screen.

If there's no import for today, the button turns amber and shows you that command.

**The news is written the way you'd TELL someone the headlines, not the way a newsreader
reads them.** That's deliberate — newsreader Arabic is fuṣḥā, which isn't the goal.

**News sentences are not native-validated.** The app shows an amber banner saying so on
any text that hasn't been checked. Every word's root, meaning and vowels still come from
the lexicon; it's the *phrasing* that's unverified.

---

## Adding new content

Three commands, always in this order. Paste all three at once:

```bash
cd "/Users/alexbranum/Desktop/Projects/Arabic Language Project"
python3 pipeline/ingest.py texts/YOUR-TEXT.json
python3 pipeline/build_app.py
```

- `ingest.py` — annotates every word against the lexicon
- `build_app.py` — collects everything into the app

If ingest says **"N ambiguous"**, that's the pipeline refusing to guess between real
dictionary entries. That's the design working. Tell me and I'll resolve them.

### With audio

Only after your voice is set up:

```bash
cd "/Users/alexbranum/Desktop/Projects/Arabic Language Project"
export ELEVENLABS_API_KEY="paste-your-key-here"
export ELEVENLABS_VOICE_ID="paste-your-voice-id-here"
python3 pipeline/ingest.py texts/morning-coffee.json --audio
python3 pipeline/car_session.py texts/car-01-reactions.json --audio
python3 pipeline/build_app.py
```

The `export` lines last only for that Terminal window. Paste them again next time.
Your key is never written into any file.

---

## What the app does today

| | |
|---|---|
| Read a text in Palestinian Arabic | ✅ |
| Tap any word → root, meaning, pronunciation | ✅ all from the lexicon, not generated |
| Mark words you don't know | ✅ remembered on that device |
| Export to Anki | ✅ copies rows you paste into Anki |
| The 30-chunk car drill | ✅ tap to reveal |
| Vowel marks on the running text | ✅ 96% of words — tap any word to see where they came from |
| Listen | ⏳ needs your ElevenLabs key |

### About the vowel marks

The lexicon stores **dictionary forms** (`يُقْعُد` "he sits"); your text has **conjugated
ones** (`بقعد` "I sit"). Those two share their stem, so the app takes the stem's vowels
from the lexicon and works out the prefix. Of 24 words:

- **11 (46%)** are straight from the lexicon, untouched
- **8 (33%)** are lexicon stem + a standard prefix rule
- **4 (17%)** are lexicon stem where **we chose the prefix vowel** — a real judgment call
- **1** we couldn't work out honestly, so it stays bare

Tap any word and the card tells you which of those it is, in plain English. Turn vowels
off with the **Vowels** button to see the text the way Palestinians actually write it.

**Worth having checked:** those 4 judgment calls are `بَصْحَى`, `وبَعْمَل`, `بَقْعُد`,
`وبَشْرَب`. `بَقْعُد` is the uncertain one — it could be `بُقْعُد`. Both are attested.

Transliteration on the running text is still missing — that's a separate problem, and
the word cards carry the accurate pronunciation.

---

## If something breaks

Nothing here can break badly. There's no server, no database, no account, no monthly
bill. The worst case is a file gets confused, and every file can be regenerated by
re-running the three commands above.

Your marked words live in the browser on each device. They are **not** synced between
your Mac and your phone, and clearing your browser data erases them. Export to Anki
periodically if you care about the list.
