#!/usr/bin/env bash
# Eco-system ticket 147 / hub ADR-0033 point 2: each adopter declares its engine in
# gitops/engine/kyverno.yaml, the file its drift lane, its shift-left job and hub talk/engine-up.sh
# install from. Three assertions, each read from the estate clone (origin/main on the runner):
#   (a) every figure in each adopter's file equals the platform engine table's row for its version;
#   (b) adopters that share a named cluster declare the same engine, the sharing derived from the
#       scripts talk/up.sh runs;
#   (c) talk/up.sh installs each named cluster's engine from its owner's file, only where the
#       platform's layers run, and never through the platform's reference install.
# See adopter_engines.py for what each reads and what it does not grade.
#
# Exit 0 observed true; 1 observed false, each fault named; 3 no platform clone to read. Offline:
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
  "$PY" "$HERE/adopter_engines.py" selfcheck; exit $?
fi

ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

# The planted estates run first, every time: a check whose refusals no longer bite would read a
# broken estate as green.
"$PY" "$HERE/adopter_engines.py" selfcheck || { echo "FAIL: adopter_engines.py selfcheck -- the planted estates no longer grade as planted"; exit 1; }
log="$(mktemp)"; err="$(mktemp)"
"$PY" "$HERE/adopter_engines.py" check --hub "$ROOT" --estate "$ESTATE" >"$log" 2>"$err"; rc=$?
cat "$log"; [ -s "$err" ] && cat "$err" >&2
fails=$(grep -c '^FAIL:' "$log")
passes=$(grep -c '^PASS:' "$log")
case $rc in
  0) echo "PASS: all $passes assertions hold: each adopter's gitops/engine/kyverno.yaml is the platform engine table's row for its version, the adopters that share a named cluster declare one engine, and talk/up.sh installs each named cluster's engine from its owner's file";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) if [ "$fails" -gt 0 ]; then
       echo "FAIL: $fails of the adopters' engine assertions do not hold: $(grep -m1 '^FAIL:' "$log" | cut -c7-)"
     else
       echo "FAIL: adopter_engines.py exited $rc having graded nothing -- it crashed rather than observed anything: $(tail -1 "$err" 2>/dev/null || echo 'no output')"
     fi;;
esac
rm -f "$log" "$err"; exit "$rc"
