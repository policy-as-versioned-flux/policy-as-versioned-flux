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
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3

[ -d "$ROOT/.estate-clone/platform" ] || { echo "SKIP: no .estate-clone/ -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/tier_binding_estate.py" selfcheck >/dev/null || {
  echo "FAIL: tier_binding_estate.py selfcheck -- the planted loose declaration or the planted disagreeing selection package no longer bites"
  exit 1
}

log="$(mktemp)"
"$PY" "$HERE/tier_binding_estate.py" check --estate-clone "$ROOT/.estate-clone" | tee "$log"
rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: every party in this estate that declares a governed Namespace declares a tier at least as tight as its own strictest priced line, and every published party fold agrees with platform's";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | tail -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") party/parties declare a cage looser than they price, or fold the party differently from platform";;
esac
rm -f "$log"
exit "$rc"
