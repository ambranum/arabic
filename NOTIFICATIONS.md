# Lock-screen practice reminders (Web Push) — setup

The code is all here. Turning it on is a one-time setup **you** do, because it involves secrets I
must never handle. ~10 minutes. Until it's done, the app hides the reminders toggle and everything
else works normally.

## How it works

1. In the app (Account → **Turn on reminders**) the browser subscribes for push and saves the
   subscription to Supabase (`push_subscriptions`).
2. A scheduled GitHub Action (`.github/workflows/push-reminders.yml`) runs twice a day, reads the
   subscriptions, and sends a VAPID-signed push to anyone who **hasn't practised yet today** (Israel).
3. The service worker shows it as a real lock-screen notification; tapping it opens today's plan.

The VAPID **private** key and the Supabase **service_role** key live only in GitHub secrets — never
in the repo.

## Setup

### 1. Generate a VAPID key pair
Easiest:
```bash
npx web-push generate-vapid-keys
```
It prints a **Public Key** and a **Private Key** (both base64url strings).

### 2. Put the PUBLIC key in the app
Edit [`app/data/pushconfig.js`](app/data/pushconfig.js) and set:
```js
window.PUSH_PUBLIC_KEY = "<the Public Key>";
```
This is safe to commit. Commit + push (deploys).

### 3. Create the Supabase table
Supabase dashboard → **SQL** → New query → paste all of
[`supabase/push_subscriptions.sql`](supabase/push_subscriptions.sql) → **Run**.

### 4. Add the GitHub Actions secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**, add four:

| Secret | Value |
|---|---|
| `VAPID_PRIVATE_KEY` | the **Private Key** from step 1 |
| `VAPID_SUBJECT` | `mailto:you@example.com` (your email) |
| `SUPABASE_URL` | `https://dwpswqccyddplvvqltjb.supabase.co` (your project URL) |
| `SUPABASE_SERVICE_ROLE` | Supabase → Settings → API → **service_role** key (secret!) |

### 5. Turn it on and test
- Deploy (steps 2–4 pushed). On your **phone**, open the site in Safari → Share → **Add to Home
  Screen**, then open it *from the home-screen icon* (iOS only delivers push to installed PWAs,
  iOS 16.4+). On desktop/Android Chrome no install is needed.
- Account → **Turn on reminders** → allow notifications.
- Fire a test now: repo → Actions → **Practice reminders** → **Run workflow** → check **force** →
  Run. You should get a notification within a few seconds. (`force` ignores the "already practised
  today" skip.)

## Tuning
- **Times:** edit the two `cron:` lines in the workflow (they're UTC).
- **Message:** the defaults live in `pipeline/send_push.py` (`--title`, `--body`).
- **Only-if-work-remains:** the sender already skips anyone who completed a plan task today; pass
  `--force` to override.

## Attribution
The reminder model (streak-driven, lock-screen push) follows `willmanidis2/arabic-drill` (MIT).
No code is copied — see `data/ATTRIBUTION.md`.
