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
# its flags exactly as the workflow spells them, and substitutes only the values. Every token past
# the interpreter must be a long flag the grader has a role for or a token it planted a value for;
# anything else -- a new flag, its value, a new positional, templated or plain literal alike --
# stops the run with a named refusal. Nothing is faked: platform's real committed evidence at a tag,
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
  # The PASS line is the module's own SUMMARY, quoted rather than restated, so it names HOW MANY
  # gates answered instead of hard-coding "the three adopters" over however many did. It says what
  # was compared and nothing more; each repository's own harness grades its own gate in depth.
  0) echo "PASS: $(grep '^SUMMARY:' "$log" | head -1 | cut -c10-)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) n=$(grep -c '^FAIL:' "$log")
     if [ "$n" -eq 0 ]; then
       # A non-zero exit with no FAIL line means the grader itself stopped -- never "nothing was
       # found", which is what a bare count printed here before review.
       echo "FAIL: fold_agreement.py exited $rc without grading a single planted movement: $(tail -1 "$log")"
     else
       echo "FAIL: $n planted movement(s) were answered differently by two adopter gates, or answered differently from ADR-0011's own reading"
     fi;;
esac
rm -f "$log"; exit "$rc"
