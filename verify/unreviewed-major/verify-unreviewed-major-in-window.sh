#!/usr/bin/env bash
# Eco-system tickets 99 and 129. Which majors is an institution carrying in its composed window,
# and does its own repository carry a record accepting each one?
#
# THE NAME OF THIS SCRIPT AND ITS DIRECTORY IS HISTORICAL: they are named for the fact ticket 99
# was about. This check cannot see a review. Since ticket 129 it reads an acceptance record, one
# file per accepted major under accepted-majors/ in the adopter's own tree at the commit it serves
# (the format is in unreviewed_major.py), and grades a carried major accepted or not. Since ticket
# 132 each adopter gate reads the same records through a byte-for-byte copy of the hub's reader, and
# this check fails an adopter whose served copy differs.
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
# IT WRITES NO ACCEPTANCE. Accepting a major is an authorisation the owner makes (ADR-0025), and it
# reaches this check only as a record in the adopter's own repository. The check says what it
# observed: which version is carried, at which tag, what the publisher's own signed evidence
# computes for it, and which record accepts it, or that none at the served commit does.
#
# Exit 0 observed true (no adopter carries an unaccepted major); 1 observed false, each carrier
# named; 3 could not look, reason on the last line.
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
# the same rules pass a clean window, fail a carried major, pass only a major its own adopter's
# record accepts, and refuse to soften an observed major with an adopter nobody could look at.
"$PY" "$HERE/unreviewed_major.py" --selfcheck >/dev/null \
  || { echo "FAIL: unreviewed_major.py --selfcheck -- the planted rules no longer grade as written"; exit 1; }

log="$(mktemp)"; "$PY" "$HERE/unreviewed_major.py" "$ESTATE" | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: no party claiming the adopter role carries a policy version whose publisher-signed evidence, verified in this run under that party's own identity constant at the tag it pins, records a major that party's own tree does not accept at the commit it serves";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  # The FAIL line says what was observed: a major is carried, and no record at the served commit
  # accepts it. It names the record directory it read, never a review it cannot see. A non-zero
  # exit with no FAIL line means the grader stopped, not that nothing was found.
  *) n=$(grep -c '^FAIL:' "$log")
     if [ "$n" -eq 0 ]; then
       echo "FAIL: unreviewed_major.py exited $rc without reporting on a single adopter: $(tail -1 "$log")"
     else
       echo "FAIL: $n line(s) observed false: a major carried in an adopter's composed window with no record in its own tree accepting it, evidence at an adopter's own pin that did not verify, or an adopter gate whose acceptance reader is not the hub's byte for byte -- each named above"
     fi;;
esac
rm -f "$log"; exit "$rc"
