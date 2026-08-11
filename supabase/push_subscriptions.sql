-- Web Push subscriptions for practice reminders.
-- Run once in the Supabase SQL editor (Dashboard → SQL → New query → paste → Run).
--
-- Each row is one browser's push subscription. The endpoint is an unguessable, per-browser secret
-- URL, so it doubles as the row key. Anyone (anonymous) may INSERT their own subscription and DELETE
-- it by its endpoint — that's how the app turns reminders on/off without forcing a login. Nobody can
-- SELECT: reads happen only from the scheduled sender, which uses the service_role key (bypasses RLS).

create table if not exists public.push_subscriptions (
  endpoint    text primary key,
  p256dh      text not null,
  auth        text not null,
  user_id     uuid references auth.users(id) on delete cascade,
  tz          text default 'Asia/Jerusalem',
  created_at  timestamptz default now(),
  updated_at  timestamptz default now(),
  last_sent   timestamptz
);

alter table public.push_subscriptions enable row level security;

-- subscribe (anon or signed-in) — upsert on endpoint
drop policy if exists "push insert" on public.push_subscriptions;
create policy "push insert" on public.push_subscriptions
  for insert to anon, authenticated with check (true);

drop policy if exists "push update own endpoint" on public.push_subscriptions;
create policy "push update own endpoint" on public.push_subscriptions
  for update to anon, authenticated using (true) with check (true);

-- unsubscribe — delete by endpoint (endpoints are secret, so this is safe)
drop policy if exists "push delete" on public.push_subscriptions;
create policy "push delete" on public.push_subscriptions
  for delete to anon, authenticated using (true);

-- NOTE: intentionally NO select policy. The sender reads with the service_role key.
