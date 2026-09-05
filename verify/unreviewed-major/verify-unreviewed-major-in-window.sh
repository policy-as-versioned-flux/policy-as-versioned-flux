#!/usr/bin/env bash
# Eco-system ticket 99. Which majors is an institution carrying in its composed window?
#
# THE NAME OF THIS SCRIPT AND ITS DIRECTORY IS HISTORICAL: they are named for the fact the ticket
# was about, and this check cannot see a review and never asserts one is absent. It looks for no
# acceptance record and says nothing about whether one exists. It grades what is CARRIED.
#
# This is the property tuppence's adopter gate was protecting when it folded its whole supported
# window instead of what a pull request moves. That reading broke -- a major in the window refused
# every pull request, whatever it changed -- and it was the wrong shape besides: the fact does not
# depend on anyone opening a pull request. So it is a standing report, carried here on every run,
# visible on a day nobody proposes anything, which is exactly when it matters.
#
# WHAT IT MEASURES, AND AGAINST WHAT. The served artefacts are each adopter's own
# composed/evidence.json at the commit it serves, and platform's computed-semver evidence read AT
# THE TAG THAT ADOPTER'S OWN PIN NAMES -- never platform's main, never a working-tree copy. The
# operation is the adopter's own verification: real `cosign verify-blob`, offline, identity-pinned
# to the constant that repository itself holds, read out of the repository rather than typed here.
# A bump is reported only from evidence that really verified in this run.
#
# IT RECORDS NO REVIEW AND INVENTS NONE. Whether a major an institution carries is accepted is an
# authorisation the owner makes (ADR-0025). This check has no input for one, and says only what it
# observed: which version is carried, at which tag, and what the publisher's own signed evidence
# computes for it.
#
# Exit 0 observed true (no adopter carries a major); 1 observed false, each carrier named; 3 could
# not look, reason on the last line.
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

# The rules first, on planted inputs, so a run that reports on the estate has already shown that
# the same rules pass a clean window, fail a carried major, and refuse to soften an observed major
# with an adopter nobody could look at.
"$PY" "$HERE/unreviewed_major.py" --selfcheck >/dev/null \
  || { echo "FAIL: unreviewed_major.py --selfcheck -- the planted rules no longer grade as written"; exit 1; }

log="$(mktemp)"; "$PY" "$HERE/unreviewed_major.py" "$ESTATE" | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: no party claiming the adopter role carries a policy version whose publisher-signed evidence, verified in this run under that party's own identity constant at the tag it pins, records a major";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  # The FAIL line says what was observed -- a major is carried -- and never that an authorisation
  # is absent, which this check does not look for and cannot see (review, 2026-09-05). A non-zero
  # exit with no FAIL line means the grader stopped, not that nothing was found.
  *) n=$(grep -c '^FAIL:' "$log")
     if [ "$n" -eq 0 ]; then
       echo "FAIL: unreviewed_major.py exited $rc without reporting on a single adopter: $(tail -1 "$log")"
     else
       echo "FAIL: $n line(s) observed false: a major carried in an adopter's composed window, or evidence at an adopter's own pin that did not verify -- each named above"
     fi;;
esac
rm -f "$log"; exit "$rc"
