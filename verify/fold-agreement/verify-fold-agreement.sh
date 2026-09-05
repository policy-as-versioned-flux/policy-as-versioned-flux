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
# stops the run with a named refusal.
#
# THE WHITELIST IS DELIBERATELY NARROWER THAN BASH. It knows `--flag value` and nothing else, so a
# working invocation respelled `--flag=value`, with a short flag, with `python3 -u`, or behind an
# `env FOO=1` prefix is refused too. That is on purpose -- silently guessing at a spelling is how a
# grader ends up grading something nobody planted -- but it means such a red says "teach this
# grader the new spelling", NOT "the estate is broken". The FAIL line counts and names that kind
# separately from a real divergence, so the two are never read as each other.
#
# Nothing is faked: platform's real committed evidence at a tag,
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
  # Two kinds of red, counted apart and named apart (R5-2): a movement two gates answered
  # differently, and a gate whose own served operation this grader could not reproduce. Reporting
  # the second as the first would say the estate diverged when it did not.
  *) n=$(grep -c '^FAIL:' "$log")
     d=$(grep -c '^FAIL: case ' "$log")
     r=$(grep -c 'could not reproduce the operation' "$log")
     if [ "$n" -eq 0 ]; then
       # A non-zero exit with no FAIL line means the grader itself stopped -- never "nothing was
       # found", which is what a bare count printed here before review.
       echo "FAIL: fold_agreement.py exited $rc without grading a single planted movement: $(tail -1 "$log")"
     elif [ "$d" -eq 0 ]; then
       echo "FAIL: $r adopter gate invocation(s) could not be reproduced from the repository's own shift-left.yml, so no planted movement was graded against them -- a red about THIS GRADER needing to learn a new argument spelling, not about the estate diverging"
     elif [ "$r" -eq 0 ]; then
       echo "FAIL: $d planted movement(s) were answered differently by two adopter gates, or answered differently from ADR-0011's own reading"
     else
       echo "FAIL: $d planted movement(s) were answered differently by two adopter gates or from ADR-0011's own reading, and $r gate invocation(s) could not be reproduced from their own shift-left.yml (which is a red about this grader, not about the estate)"
     fi;;
esac
rm -f "$log"; exit "$rc"
