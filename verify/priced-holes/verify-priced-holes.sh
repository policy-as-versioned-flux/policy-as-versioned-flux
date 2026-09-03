#!/usr/bin/env bash
# Eco-system ticket 38 / ADR-0020. A hole is priced, not counted: composition no longer refuses
# on a new hole, a widened baseline or a new ungoverned namespace but prints each as a delta
# under the adopter's own perspective and currency; every hole is keyed (source, id) across
# every controls parent; an ungoverned namespace carries a ramped workload share of the uncaged
# residual with a since read off the first signed tag naming it; the only hole-shaped refusal
# left is a bespoke control with no signed scenario; and the party schema admits overlay.controls
# in both forms. The arithmetic (share, ramp, bound, since) is re-derived here from the adopter's
# own manifests, tags and pinned feeds, never trusted from the producer.
# Exit 0 observed true; 3 could not look (no estate, no interpreter, evidence composed under the
# refusal shape, a clone with no signed tag); 1 observed false. Offline: reads committed files only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
[ -d "$ROOT/.estate-clone/platform" ] || { echo "SKIP: no .estate-clone/ -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/priced_holes.py" selfcheck >/dev/null || { echo "FAIL: priced_holes.py selfcheck -- the planted defects no longer bite"; exit 1; }
log="$(mktemp)"; "$PY" "$HERE/priced_holes.py" check | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: no hole, widening or ungoverned namespace refuses; each is a priced delta keyed (source, id), the ungoverned share ramps from a signed since and stays within the residual, and only a bespoke control with no scenario still refuses";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") priced-holes check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
