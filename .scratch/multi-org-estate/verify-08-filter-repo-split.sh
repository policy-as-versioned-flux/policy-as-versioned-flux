#!/usr/bin/env bash
# Verification beat for ticket 08 (filter-repo-split): each of the six
# estate/<unit> directories now lives as its own public GitHub repo, in its
# matching org, with a README (not the estate/README.md monorepo framing), a
# licence, and history preserved.
#
# mo-12 note: the "file tree matches the hub's estate/<unit>/ tree 1:1" check
# below is now PERMANENTLY INERT, on purpose, not a bug to fix. Its baseline
# was the hub's own committed estate/<unit>/ copy -- mo-12 deletes that copy
# from the hub (the whole point: the six repos are the source of truth, not a
# mirror of one). Re-deriving the baseline via ../../clone-estate.sh would
# just diff each repo against a fresh clone of itself -- always true, proves
# nothing. The comparison this check made is preserved in git history (the
# commit before mo-12 removed estate/<unit>/) rather than kept live; every
# other check in this script (visibility, history/attribution, README,
# LICENSE) is unaffected and still runs for real.
#
# Run from the repo root. Requires: gh (authenticated), git.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UNITS="platform driftwood tuppence ludlow nist ico"

fail=0
ok()  { printf '  OK   %s\n' "$*"; }
bad() { printf '  FAIL %s\n' "$*"; fail=1; }

for u in $UNITS; do
  org="policy-as-versioned-$u"
  echo "== $u -> $org/$u =="

  vis="$(gh api "repos/$org/$u" --jq '.visibility' 2>/dev/null || echo MISSING)"
  branch="$(gh api "repos/$org/$u" --jq '.default_branch' 2>/dev/null || echo MISSING)"
  [ "$vis" = "public" ] && ok "visibility=public" || bad "visibility=$vis (want public)"
  [ "$branch" = "main" ] && ok "default_branch=main" || bad "default_branch=$branch"

  # History preserved: more than one commit, oldest and newest both
  # attributed to the estate's real author (not a squash-to-one-commit dump).
  n_commits="$(gh api "repos/$org/$u/commits" --jq 'length' 2>/dev/null || echo 0)"
  newest_author="$(gh api "repos/$org/$u/commits/main" --jq '.commit.author.email' 2>/dev/null || echo MISSING)"
  oldest_sha="$(gh api "repos/$org/$u/commits?per_page=100" --jq '.[-1].sha' 2>/dev/null || echo MISSING)"
  oldest_author="$(gh api "repos/$org/$u/commits/$oldest_sha" --jq '.commit.author.email' 2>/dev/null || echo MISSING)"
  if [ "$n_commits" -gt 1 ] && [ "$newest_author" = "chris@cns.me.uk" ] && [ "$oldest_author" = "chris@cns.me.uk" ]; then
    ok "history preserved: $n_commits+ commits, attribution intact (chris@cns.me.uk)"
  else
    bad "history/attribution: n=$n_commits newest=$newest_author oldest=$oldest_author"
  fi

  # README: present, correctly titled, not the estate/README.md monorepo
  # framing, and carries the ticket-03 Role vocabulary.
  readme="$(gh api "repos/$org/$u/contents/README.md" --jq '.content' 2>/dev/null | base64 -d || echo '')"
  if echo "$readme" | grep -q "^# policy-as-versioned-$u\$"; then ok "README.md present, correct title"; else bad "README.md missing/wrong title"; fi
  if echo "$readme" | grep -qi "Monorepo-style working tree\|becomes its own.*GitHub repo at split"; then
    bad "README.md still carries the estate/README.md monorepo framing"
  else
    ok "README.md does not carry the monorepo framing"
  fi
  echo "$readme" | grep -q '\*\*Role:\*\*' && ok "README.md states a Role (ticket-03 vocabulary)" || bad "README.md missing Role line"

  # Licence present.
  lic="$(gh api "repos/$org/$u/contents/LICENSE" --jq '.content' 2>/dev/null | base64 -d || echo '')"
  echo "$lic" | grep -q "Apache License" && ok "LICENSE present (Apache-2.0)" || bad "LICENSE missing/wrong"

  # File tree matches the hub's estate/<unit>/ tree 1:1 -- RETIRED by mo-12,
  # see the file header. estate/$u/ no longer exists in this hub by design,
  # so this is reported as SKIP, not FAIL: there is nothing wrong here, the
  # baseline was deliberately removed.
  if [ -d "$ROOT/estate/$u" ]; then
    hub_files="$(cd "$ROOT/estate/$u" && find . -type f -not -path './README.md' | sed 's|^\./||' | LC_ALL=C sort)"
    tree_json="$(gh api "repos/$org/$u/git/trees/main?recursive=1" --jq '[.tree[] | select(.type=="blob") | .path] | sort | .[]' 2>/dev/null || echo '')"
    split_files="$(echo "$tree_json" | grep -v '^README.md$' | grep -v '^LICENSE$' || true)"
    if [ "$hub_files" = "$split_files" ]; then
      ok "file tree matches hub estate/$u/ 1:1 (excluding README.md/LICENSE)"
    else
      bad "file tree diverges from hub estate/$u/"
    fi
  else
    printf '  SKIP file tree vs. hub estate/%s/ (retired by mo-12 -- see git history)\n' "$u"
  fi

  echo
done

if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASSED for: $UNITS"
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
