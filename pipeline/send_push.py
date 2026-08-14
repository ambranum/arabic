#!/usr/bin/env python3
"""Send practice-reminder Web Push notifications. Runs on a schedule (a GitHub Action).

Reads the browser subscriptions from Supabase with the service_role key (bypassing RLS), and sends a
VAPID-signed push to each subscriber who HASN'T practised yet today (Israel time) — a nudge that
stops the moment they've done something, so it never nags. Expired subscriptions (404/410) are pruned.

Secrets come from the environment (GitHub Actions), NEVER from the repo:
  SUPABASE_URL, SUPABASE_SERVICE_ROLE   # read subscriptions + progress
  VAPID_PRIVATE_KEY                     # base64url; pairs with app/data/pushconfig.js's public key
  VAPID_SUBJECT                         # e.g. mailto:you@example.com

Run:  python3 pipeline/send_push.py [--title ...] [--body ...] [--force] [--dry-run]
"""
import os, json, argparse, datetime, urllib.request, urllib.parse, urllib.error

SUPA_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SERVICE = os.environ.get('SUPABASE_SERVICE_ROLE', '')
VAPID_PRIV = os.environ.get('VAPID_PRIVATE_KEY', '')
VAPID_SUB = os.environ.get('VAPID_SUBJECT', 'mailto:admin@example.com')


def israel_today():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo('Asia/Jerusalem')).date().isoformat()
    except Exception:
        return datetime.datetime.utcnow().date().isoformat()


def supa_get(path):
    req = urllib.request.Request(SUPA_URL + '/rest/v1/' + path,
        headers={'apikey': SERVICE, 'Authorization': 'Bearer ' + SERVICE})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def supa_delete(endpoint):
    q = '/rest/v1/push_subscriptions?endpoint=eq.' + urllib.parse.quote(endpoint, safe='')
    req = urllib.request.Request(SUPA_URL + q, method='DELETE',
        headers={'apikey': SERVICE, 'Authorization': 'Bearer ' + SERVICE})
    try:
        urllib.request.urlopen(req, timeout=30)
    except Exception:
        pass


def practiced_today(progress_by_user, user_id, today):
    """True if this signed-in user already completed a plan task today — skip the reminder."""
    if not user_id:
        return False
    data = progress_by_user.get(user_id) or {}
    try:
        raw = data.get('alp.plan.log.v1')
        log = json.loads(raw) if isinstance(raw, str) else (raw or {})
        return bool((log.get(today) or {}).get('done'))
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', default='Palestinian Arabic')
    ap.add_argument('--body', default='A few minutes keeps your streak alive — open today’s plan.')
    ap.add_argument('--url', default='./index.html#/plan')
    ap.add_argument('--force', action='store_true', help='notify everyone, even if they practised today')
    ap.add_argument('--dry-run', action='store_true', help='count recipients, send nothing')
    a = ap.parse_args()

    if not (SUPA_URL and SERVICE):
        print('!! SUPABASE_URL / SUPABASE_SERVICE_ROLE not set'); return 1
    if not VAPID_PRIV and not a.dry_run:
        print('!! VAPID_PRIVATE_KEY not set'); return 1

    subs = supa_get('push_subscriptions?select=endpoint,p256dh,auth,user_id')
    today = israel_today()
    print(f'{len(subs)} subscription(s) · Israel date {today}')

    progress_by_user = {}
    if not a.force:
        try:
            for r in supa_get('progress?select=user_id,data'):
                progress_by_user[r['user_id']] = r.get('data') or {}
        except Exception as e:
            print('  (progress read failed — notifying everyone this run):', str(e)[:80])

    payload = json.dumps({'title': a.title, 'body': a.body, 'url': a.url})
    if not a.dry_run:
        from pywebpush import webpush, WebPushException

    sent = skipped = pruned = failed = 0
    for s in subs:
        if not a.force and practiced_today(progress_by_user, s.get('user_id'), today):
            skipped += 1; continue
        if a.dry_run:
            sent += 1; continue
        info = {'endpoint': s['endpoint'], 'keys': {'p256dh': s['p256dh'], 'auth': s['auth']}}
        try:
            webpush(subscription_info=info, data=payload,
                    vapid_private_key=VAPID_PRIV, vapid_claims={'sub': VAPID_SUB})
            sent += 1
        except WebPushException as e:
            code = getattr(getattr(e, 'response', None), 'status_code', None)
            if code in (404, 410):
                supa_delete(s['endpoint']); pruned += 1        # gone/expired → drop it
            else:
                failed += 1; print('  push failed:', str(e)[:120])
        except Exception as e:
            # A malformed subscription (bad p256dh/auth base64) throws before the HTTP call and would
            # otherwise crash the whole run. Prune it (service_role bypasses RLS) and carry on.
            print('  bad subscription pruned:', str(e)[:100]); supa_delete(s['endpoint']); pruned += 1

    print(f'sent {sent} · skipped(practised today) {skipped} · pruned(expired) {pruned} · failed {failed}')
    # A few transient failures shouldn't fail the whole run; only a total wipeout is worth a red build.
    return 1 if (subs and not a.dry_run and sent == 0 and failed) else 0


if __name__ == '__main__':
    raise SystemExit(main())
