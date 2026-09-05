#!/usr/bin/env bash
# Eco-system ticket 99. Do the three adopter gates answer ADR-0011's question the same way?
#
# Three institutions carry three hand-written gates. Nothing graded whether they agreed, so when
# tuppence's fold read its whole supported window where driftwood's and ludlow's read what the pull
# request moves, the estate found out by watching one repository go red for a fortnight. This is the
# check that names the next divergence on the day it appears.
#
# WHAT IT MEASURES, AND AGAINST WHAT. The served artefact is each adopter's own committed gate
# script in the estate checkout. The operation is that repository's own shift-left.yml step named
# `adopter gate ...`: fold_agreement.py reads that step's command line out of the workflow, keeps
# its flags exactly as the workflow spells them, and substitutes only the values. An argument the
# workflow grows that this grader has no planted value for stops the run with a named refusal
# rather than being dropped. Nothing is faked: platform's real committed evidence at a real tag,
# real cosign, real exit codes, and only the subject -- a throwaway adopter repository whose
# composed window and pin move in a stated way -- is planted.
#
# Exit 0 observed true; 1 observed false (two gates answered one planted movement differently, or
# a gate's answer was not the reading ADR-0011 gives that movement); 3 could not look, reason on
# the last line.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
# PAVC_ESTATE_CLONE names another estate to grade, so a branch can be graded before it merges.
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE" ] || { echo "SKIP: no $ESTATE/ -- run ./clone-estate.sh first"; exit 3; }

# The rules first, on planted inputs, so a run that grades the estate green has already shown that
# the comparator goes red on a divergence and refuses to reproduce an operation it cannot resolve.
# A comparator only ever exercised against gates that agree proves nothing.
"$PY" "$HERE/fold_agreement.py" --selfcheck >/dev/null \
  || { echo "FAIL: fold_agreement.py --selfcheck -- the planted rules no longer grade as written"; exit 1; }

log="$(mktemp)"; "$PY" "$HERE/fold_agreement.py" "$ESTATE" | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  # The PASS line says what was compared and nothing more: four planted movements, each answered by
  # three real gates run through their own workflows' own flags. It does not say the gates are
  # right about anything else; each repository's own verify-adopter-gate.sh grades its own gate.
  0) echo "PASS: on four planted movements of a composed window, the three adopters' gates -- each run through the flag shape its own shift-left.yml uses, against platform's real signed evidence with real cosign -- returned the same verdict and the same composed bump, and each was the verdict ADR-0011's reading gives that movement";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") planted movement(s) were answered differently by two adopter gates, or answered differently from ADR-0011's own reading";;
esac
rm -f "$log"; exit "$rc"
