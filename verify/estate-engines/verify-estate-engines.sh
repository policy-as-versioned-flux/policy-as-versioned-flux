#!/usr/bin/env bash
# Eco-system ticket 146 item 7 / hub ADR-0033 point 5: the estate's own engine pins name a
# supported engine of everything it serves. Five pins -- the hub truth CLI, the platform release
# and cut-release CLIs, the platform reference install's Helm chart and the hub test constant
# PINNED_KYVERNO -- must each name a row of platform engine/kyverno/engine-table.yaml, carry that
# row's checksum where they carry one, and be listed in the tested_engines of every cut line in
# platform distribution/versions.yaml and of the machinery (platform distribution/machinery.yaml).
# See estate_engines.py for what each pin is and why an adopter's own engine is out of scope.
#
# Exit 0 observed true; 1 observed false, each pin named; 3 no platform clone to read. Offline:
# every fact is a file in this checkout or in the estate clone.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi

# `--selfcheck` runs the planted estates alone, which a reader with no estate clone can run.
if [ "${1:-}" = "--selfcheck" ]; then
  "$PY" "$HERE/estate_engines.py" selfcheck; exit $?
fi

ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

# The planted estates run first, every time: a check whose refusals no longer bite would read a
# broken estate as green.
"$PY" "$HERE/estate_engines.py" selfcheck || { echo "FAIL: estate_engines.py selfcheck -- the planted pins no longer grade as planted"; exit 1; }
log="$(mktemp)"; err="$(mktemp)"
"$PY" "$HERE/estate_engines.py" check --estate "$ESTATE" >"$log" 2>"$err"; rc=$?
cat "$log"; [ -s "$err" ] && cat "$err" >&2
fails=$(grep -c '^FAIL:' "$log")
passes=$(grep -c '^PASS:' "$log")
case $rc in
  0) echo "PASS: all $passes of the estate's own engine pins name a row of the platform engine table and a supported engine of every served line and of the machinery";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) if [ "$fails" -gt 0 ]; then
       echo "FAIL: $fails of the estate's own engine pins do not name a supported engine of everything it serves: $(grep -m1 '^FAIL:' "$log" | cut -c7-)"
     else
       echo "FAIL: estate_engines.py exited $rc having graded nothing -- it crashed rather than observed anything: $(tail -1 "$err" 2>/dev/null || echo 'no output')"
     fi;;
esac
rm -f "$log" "$err"; exit "$rc"
