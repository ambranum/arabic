# Going live — automatic news at 6am

Written for someone who is not a developer. Copy-paste each block exactly.

Once this is done you'll have a URL that works on your phone, and every morning
before you leave the house it will have that day's world news written in spoken
Palestinian, annotated against the lexicon, and (if you set up the voice) read aloud.

**About 20 minutes, once.**

---

## What you'll need

| | | |
|---|---|---|
| A GitHub account | free | github.com |
| An Anthropic API key | ~$0.30/month | console.anthropic.com → API keys |
| Your ElevenLabs key + voice ID | ~$4.50/month | optional — text works without it |

---

## One thing to decide first: the repo must be public

GitHub only gives free website hosting to **public** repositories. Private ones need
a paid plan.

Public is fine here. There are **no passwords or keys in the files** — those live in
GitHub's encrypted secrets, which stay private even on a public repo. Your marked words
live in your browser, not the repo. What's public is: the pipeline code, the lesson
texts, and the lexicon.

One obligation that comes with publishing: the Maknuune lexicon is **CC BY-SA 4.0**,
which requires attribution. That's already handled — see `data/ATTRIBUTION.md` and the
credit at the bottom of the app's home screen. **Don't remove either.**

If you'd rather stay private, tell me and I'll switch the hosting to Netlify instead
(also free, no public repo).

---

## Step 1 — Put the project on GitHub

Go to **github.com/new**. Name it `arabic` (or anything). Choose **Public**. Do **not**
tick "Add a README". Click **Create repository**.

Then paste this, replacing `YOUR-USERNAME`:

```bash
cd "/Users/alexbranum/Desktop/Projects/Arabic Language Project"
git init
git add .
git commit -m "Palestinian Arabic reader"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/arabic.git
git push -u origin main
```

If it asks for a password, GitHub wants a **personal access token**, not your account
password — github.com/settings/tokens → "Generate new token (classic)" → tick `repo`
→ copy → paste as the password.

---

## Step 2 — Add your keys as secrets

In your new repo: **Settings → Secrets and variables → Actions → New repository secret.**

Add these (names must match exactly):

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Anthropic key |
| `ELEVENLABS_API_KEY` | your ElevenLabs key — skip for text-only |
| `ELEVENLABS_VOICE_ID` | your Palestinian voice ID — skip for text-only |

Secrets are encrypted. They aren't visible in the code, in the logs, or to anyone
browsing the repo — including you, after saving.

---

## Step 3 — Turn on the website

**Settings → Pages → Source → GitHub Actions.** That's the whole step.

---

## Step 4 — Run it once by hand

Don't wait until tomorrow to find out if it works.

**Actions tab → "Daily news" → "Run workflow" → green button.**

It takes 2–3 minutes. Green tick = working. Your site is at:

```
https://YOUR-USERNAME.github.io/arabic/
```

Open that on your phone and **Add to Home Screen** — it behaves like an app.

If it fails, click the run and read the red step. Send me what it says.

---

## What happens every morning

**10:00 UTC = 5am EST / 6am EDT.** GitHub's scheduler has no timezone setting and
can't follow daylight saving, so it's deliberately set an hour early in winter —
content that isn't ready before the drive is content you don't use.

To shift it: edit `.github/workflows/daily-news.yml`, change the `10` in
`cron: '0 10 * * *'`. It's UTC — `11` = 6am EST, `12` = 7am EST.

GitHub also delays scheduled jobs when busy, sometimes 10+ minutes. Treat it as
"before the drive", not an alarm clock.

Each morning the job: reads ~30 headlines from BBC / Al Jazeera / NPR → writes 9
sentences in spoken Palestinian → looks up every word in the lexicon → asks Claude to
pick the right sense for ambiguous words → generates audio → publishes.

---

## The part worth understanding

**43% of words in a news text need someone to pick the right meaning.** `بقعد` matches
both "sit down" and "make somebody sit" — the lexicon has both, and only context decides.
In our conversations that someone is me. At 6am it has to be the API.

So the job makes **two** calls: one to write the Arabic, one to choose senses. The second
call can only pick from **real lexicon entries** — it's handed the actual candidate list.
And if it ever returns an ID that isn't on that list, the pipeline **rejects it** and
leaves the word flagged rather than accept something unverifiable. I tested that guard
specifically.

That's what keeps the "never guess" guarantee alive when nobody's watching.

---

## Costs

| | |
|---|---|
| GitHub Actions + Pages | free (public repo) |
| Claude API | ~$0.01/day → **~$0.30/month** |
| ElevenLabs audio | ~$0.15/day → **~$4.50/month** |

Set a spend limit at console.anthropic.com → Billing so a bug can't run up a bill.

---

## When it breaks

It will, eventually — that's the cost of automation. Most likely: an expired API key,
a lapsed billing account, or a news feed changing format.

**How you'll notice:** no new news on the home screen. The button turns amber and says
so — it never shows yesterday's news as if it were today's.

**How to check:** the **Actions** tab. Green tick = ran fine. Red X = click it, read the
failed step.

**Turn it off:** Actions tab → "Daily news" → "..." → Disable workflow. Nothing else
breaks; the app keeps working with whatever content it already has.

Nothing here can break *quietly*, and nothing can break the reader or the drill —
those are just files.
