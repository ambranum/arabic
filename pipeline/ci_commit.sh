#!/usr/bin/env bash
# Save whatever the step before this one paid for. $1 is what to call it.
#
# This used to run once, after everything. Then a run spent real credit adjudicating a hundred
# texts, ran out partway through the books, and exited before it reached here -- so every
# decision that had been bought was thrown away and the next run had to buy them again. A step
# that costs money commits before the next one starts.
set -u
git config user.name  "hebrew-books"
git config user.email "actions@github.com"
git add texts/ build/ app/ pipeline/resolutions.he.json
git diff --staged --quiet && { echo "nothing to save after: $1"; exit 0; }
git commit -m "Hebrew: $1"
for attempt in 1 2 3 4 5 6; do
  if git pull --rebase --autostash origin main; then
    git push && exit 0
  else
    git rebase --abort || true
    git stash pop 2>/dev/null || true
    echo "rebase conflicted on attempt $attempt — tree restored"
  fi
  sleep $((attempt * 10))
done
echo "::error::could not push after 6 attempts"
exit 1
