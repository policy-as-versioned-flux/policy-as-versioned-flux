#!/usr/bin/env bash
# Eco-system ticket 64. "The twin is three adopters" -- graded across the estate, per adopter,
# from the party artefacts outwards, so that an adopter WITHOUT an overlay is named instead of
# being invisible. Every twin check in this estate before this one was driftwood's own, run
# against driftwood, so the two adopters REGRILL answer 39 promised and ticket 29 claimed could
# be absent for a week with the gate fully green.
#
# It grades structure and parity only: which parties claim the adopter role, which of them carry
# an overlay, whether every overlay vendors the same world layer at the same content-addressed
# world_ref, and whether each carries the six standing scenarios and an emitter. It prices
# nothing and it runs no adopter's emitter -- each adopter's own verify-twin-overlay.sh and
# twin/verify-twin-scenarios.sh are in the gate in their own repositories and are consumed by
# verify/e2e/verify-e2e-step5-twin-forecasts.sh. A hub check that re-derived half of those could
# pass while the repository owning the artefact failed, which is the shape ticket 64 exists to end.
#
# Exit 0 observed true; 1 observed false; 3 could not look, reason on the last line.
# Offline: reads committed files only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
# PAVC_ESTATE_CLONE names another estate to grade (the override composition.py takes), so a
# scratch estate can be graded before the owner pushes the branches.
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE" ] || { echo "SKIP: no $ESTATE/ -- run ./clone-estate.sh first"; exit 3; }

# The rules first, on planted directories, so a run that grades the estate green has already
# shown that the same rules go red on a missing overlay, a short scenario set and a split
# world_ref. A grader only ever exercised against material that passes it proves nothing.
"$PY" "$HERE/twin_per_adopter.py" --selfcheck >/dev/null \
  || { echo "FAIL: twin_per_adopter.py --selfcheck -- the planted cases no longer grade as written"; exit 1; }

log="$(mktemp)"; "$PY" "$HERE/twin_per_adopter.py" "$ESTATE" | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  # Counted, not judged: this check observed six scenario FILES, an emitter file and a
  # vendored world layer at one shared ref. Whether those six files are the six standing
  # scenarios of decision ticket 11 answer item 4, naming committed classes that land in
  # the enum and the library, is each adopter's own twin/verify-twin-scenarios.sh, and
  # step 5 consumes that verdict. The PASS line says what this run looked at.
  0) echo "PASS: every party claiming the adopter role carries a twin overlay of its own, each with six scenario files, an emitter, and the same vendored world layer pinned at one shared content-addressed world_ref";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") twin-per-adopter check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
