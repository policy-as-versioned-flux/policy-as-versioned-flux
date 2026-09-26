#!/usr/bin/env bash
# Eco-system ticket 148 / hub ADR-0033 point 3: composition prices an unsupported engine pairing,
# and never refuses it. The platform composer the estate serves is run through its own CLI on
# copies of the adopters' committed trees:
#   planted  a copy of driftwood declaring its own engine, an engine the composed line does not
#            list, the same with a planted claim of a weighted control (so the price is a number
#            that moves), no declaration, and a declaration that does not read;
#   forward  each real adopter's committed tree composed now against the served platform tree;
#   served   each real adopter's committed composed/ against the platform commit it pins.
# Every expected figure (the bodies, the claims, the tested engines, the hole prices) is derived
# here, never read from the delta it grades. See engine_pairing.py.
#
# Exit 0 observed true; 1 observed false, each case named; 3 could not look (no estate, or an
# adopter artefact composed before ticket 148, which only the adopter's own push changes).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
if [ "${1:-}" = "--selfcheck" ]; then
  "$PY" "$HERE/engine_pairing.py" selfcheck; exit $?
fi
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

# The planted evidence runs first, every time: a grader whose rules no longer bite would read a
# wrong price as green.
"$PY" "$HERE/engine_pairing.py" selfcheck >/dev/null || { echo "FAIL: engine_pairing.py selfcheck -- the planted defects no longer grade FAIL"; exit 1; }
log="$(mktemp)"
"$PY" "$HERE/engine_pairing.py" check | tee "$log"; rc=${PIPESTATUS[0]}
platform="$(git -C "$ESTATE/platform" rev-parse --short=12 HEAD 2>/dev/null || echo 'the working tree')"
case $rc in
  0) echo "PASS: platform $platform's composer prices every planted unsupported pairing at the sum of its claimed controls' hole prices, an undeclared engine the same way, refuses an unreadable declaration by name, and every adopter's committed and forward composition shows exactly the engine deltas its pinned tree implies";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") engine-pairing check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
