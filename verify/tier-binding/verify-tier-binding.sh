#!/usr/bin/env bash
# Ticket 78 / ADR-0022. The enacted tier is bound to the priced tier: no party in
# this estate declares a `posture.acme.io/tier` on its governed Namespace looser
# than the strictest `proposed_tier` its own composed evidence prices, clamped to
# its own `overlay.floor` -- and where a party publishes a selection-policy
# package, its party fold and platform's agree on every shape on the ladder.
#
# The rule is PLATFORM's, published once at platform/shift-left/tier_binding.py
# and pinned by each adopter; each adopter's shift-left.yml runs the same module
# on every pull request. This script is the hub asking the same question of what
# is committed across .estate-clone/ right now. It reads committed files only:
# no cluster, no network, and nothing written.
#
# Exit 0 observed true; 3 could not look (no estate, no platform checkout with
# the rule in it, nothing composed anywhere); 1 observed false.
#
# ESTATE_CLONE points this at another estate layout (a tree of ticket worktrees,
# say); it defaults to the hub's own .estate-clone/.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3

ESTATE="${ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/ -- run ./clone-estate.sh first"; exit 3; }

# ORDER MATTERS (fixed 2026-09-04, ticket 78 review). The selfcheck plants its
# estate around the REAL platform tree, because the rule under test is the one
# platform publishes and wargamer.py imports its own siblings. So it can only run
# where this estate's platform checkout already carries the rule -- and until the
# owner pushes ticket 78's platform branch, it does not. Running the selfcheck
# first turned that could-not-look into a FAIL: an unnamed red on the gate that
# said the planted case "no longer bites" when the truth was that the rule is not
# here yet. `check` is asked first and its SKIP wins; the selfcheck runs only
# where check could look, which is exactly where the rule exists to be planted
# against.
log="$(mktemp)"
"$PY" "$HERE/tier_binding_estate.py" check --estate-clone "$ESTATE" | tee "$log"
rc=${PIPESTATUS[0]}
if [ "$rc" -eq 3 ]; then
  echo "SKIP: $(grep '^SKIP:' "$log" | tail -1 | cut -c7-)"
  rm -f "$log"
  exit 3
fi

# check could look, so platform's rule is in this estate: now prove the walk still
# bites before believing the verdict it just printed.
if ! "$PY" "$HERE/tier_binding_estate.py" selfcheck --estate-clone "$ESTATE" >/dev/null; then
  rm -f "$log"
  echo "FAIL: tier_binding_estate.py selfcheck -- the planted loose declaration or the planted disagreeing selection package no longer bites"
  exit 1
fi

case $rc in
  0) skipped="$(grep -c '^SKIP:' "$log" | tr -d ' ')"
     if [ "$skipped" -gt 0 ]; then
       named="$(grep '^SKIP:' "$log" | sed -E 's/^SKIP: ([^:]+):.*/\1/' | paste -sd, - )"
       echo "PASS: every party this run could look at declares a tier at least as tight as its own strictest priced line, and every published party fold agrees with platform's; $skipped party/parties could not be looked at by name ($named) and are graded by nothing here"
     else
       echo "PASS: every party in this estate that declares a governed Namespace declares a tier at least as tight as its own strictest priced line, and every published party fold agrees with platform's"
     fi;;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") party/parties declare a cage looser than they price, or fold the party differently from platform";;
esac
rm -f "$log"
exit "$rc"
