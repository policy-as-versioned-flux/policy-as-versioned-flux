#!/usr/bin/env bash
# NORTH-STAR §4 step 2, the real event (eco-system ticket 61). The e2e step-2
# script proves the MECHANISM offline (a pin bump re-prices through
# composition, on a throwaway copy). This check grades whether step 2 has
# HAPPENED: one Renovate-authored feed-pin bump, merged by a human, on any
# adopter's real main. It reads the PR record as git landed it -- the merge
# commit, the bot authorship of the branch side, and the coupled diff -- the
# same artefacts Flux reads. No GitHub API, no token, no rate limit.
#
# Exit 0: a merged Renovate feed-pin PR exists and moved party.yaml's
#         inherits entry and composed/ together, merged by a human.
# Exit 1: such a merge exists but broke the invariant (the pin moved without
#         the composed/ re-render, or a bot performed the merge).
# Exit 3: could not look, or no such merge exists yet (waiting on ticket 61's
#         driftwood branch landing and the next feed release).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
ESTATE="${STEP2_ESTATE:-$ROOT/.estate-clone}"
ADOPTERS="${STEP2_ADOPTERS:-driftwood tuppence ludlow}"
BOT='renovate|github-actions|\[bot\]'

flat() { printf '%s' "$*" | tr '\n\t' '  ' | tr -s ' '; }
pass() { echo "PASS: $(flat "$*")"; exit 0; }
fail() { echo "FAIL: $(flat "$*")"; exit 1; }
skip() { echo "SKIP: $(flat "$*")"; exit 3; }

looked=0
for adopter in $ADOPTERS; do
  repo="$ESTATE/$adopter"
  [ -d "$repo/.git" ] || continue
  # Freshen when a real remote exists; a fixture (no origin) is read as is.
  if git -C "$repo" remote get-url origin >/dev/null 2>&1; then
    git -C "$repo" fetch --quiet origin main 2>/dev/null || skip "could not reach $adopter's real remote to read its merge record"
    ref=origin/main
  else
    ref=main
  fi
  looked=1
  while IFS='|' read -r m merger subject; do
    [ -n "$m" ] || continue
    files="$(git -C "$repo" diff --name-only "$m^1" "$m" 2>/dev/null)" || continue
    echo "$files" | grep -qx 'party.yaml' || continue   # a platform/nist bump, not a feed event
    pindiff="$(git -C "$repo" diff "$m^1" "$m" -- party.yaml | grep -E '^[+-].*kind: feed.*version:')"
    [ -n "$pindiff" ] || continue
    oldv="$(echo "$pindiff" | grep '^-' | head -1 | sed -E 's/.*version: "([^"]+)".*/\1/')"
    newv="$(echo "$pindiff" | grep '^+' | head -1 | sed -E 's/.*version: "([^"]+)".*/\1/')"
    feed="$(echo "$pindiff" | grep '^+' | head -1 | sed -E 's/.*name: ([a-z0-9-]+),.*/\1/')"
    # The branch side must be bot-authored, or this is a hand-made PR that
    # only borrowed the branch name -- exactly what M8 said always happened.
    git -C "$repo" log --no-merges --format='%an' "$m^1..$m" | grep -qiE "$BOT" || continue
    pr="$(echo "$subject" | grep -oE '#[0-9]+' | head -1)"
    echo "$merger" | grep -qiE "$BOT" && \
      fail "$adopter $pr: the Renovate feed bump ($feed $oldv -> $newv) was merged by '$merger', not a human -- the reviewed PR is the unit of adoption"
    echo "$files" | grep -q '^composed/' || \
      fail "$adopter $pr: the Renovate feed bump ($feed $oldv -> $newv) moved the pin without the composed/ re-render -- the two must land in one merge"
    pass "$adopter $pr: Renovate raised $feed $oldv -> $newv, $merger merged it, and party.yaml and composed/ moved together -- step 2 happened for real"
  done < <(git -C "$repo" log "$ref" --merges --format='%H|%an|%s' 2>/dev/null | grep -E 'Merge pull request #[0-9]+ from [^ ]*renovate/')
done
[ "$looked" = 1 ] || skip "no adopter clone present under $ESTATE -- run clone-estate.sh first"
skip "no merged Renovate feed-pin PR exists yet on any adopter's main (ticket 61: waiting on the driftwood branch landing and the next feed tag)"
