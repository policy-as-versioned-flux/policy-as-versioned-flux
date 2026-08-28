#!/usr/bin/env bash
# Ticket 25 / ADR-0020 / ADR-0021. Every adopter's composed evidence prices under ONE
# perspective in ONE currency, labels where each price came from, restates it per customer,
# carries exactly one twin edge where a forward-intel feed is published, breaks its regime
# price into holes that add up, reads its appetite off its own signed party.yaml, and names a
# selection-policy version the estate actually publishes -- and that the adopter's own
# selection-policy package agrees with platform/graded/cage.py on both the curve hash and the
# rung it picks, at the band boundary and under every floor.
# Exit 0 observed true; 3 could not look (no estate, no interpreter, nothing composed yet);
# 1 observed false. Offline: reads committed files only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
# A missing estate is the textbook could-not-look, and this script promises to
# read committed files only -- fetching eight repos mid-gate would break that
# promise and red a laptop with no network. pound_seam.py's own SKIP path
# handles it; this is only the earlier, cheaper version of the same answer.
[ -d "$ROOT/.estate-clone/platform" ] || { echo "SKIP: no .estate-clone/ -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/pound_seam.py" selfcheck >/dev/null || { echo "FAIL: pound_seam.py selfcheck — the planted defects no longer bite"; exit 1; }
log="$(mktemp)"; "$PY" "$HERE/pound_seam.py" check | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: every price names its perspective, currency, source and per-customer share; no sum crosses either; and wherever a party publishes both a selection-policy package and composed evidence, the two selection engines agree";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") £-seam check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
