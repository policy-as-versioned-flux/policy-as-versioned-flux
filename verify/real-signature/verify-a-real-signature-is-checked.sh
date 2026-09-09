#!/usr/bin/env bash
# Eco-system ticket 101. Does every adopter gate really check a real signature?
#
# THE SENTENCE GRADED. Every adopter's own gate, run the way its own shift-left.yml runs it,
# ACCEPTS platform's real published evidence for a version arriving in its window, and REFUSES the
# same evidence when one byte of the publisher's own signature is changed.
#
# WHY BOTH HALVES. On 2026-09-05 ticket 99's fold-agreement check found that ludlow's gate could
# not verify ANY bundle platform publishes: it passed --trusted-root with --new-bundle-format=true
# and cosign v3.1.3, the version ludlow itself pins, answered "--trusted-root only supported with
# --new-bundle-format" before it looked at the signature at all. A check that asked only "does the
# gate refuse a corrupted signature?" would have called that a PASS. A check that asked only "does
# it accept a good one?" would pass a gate that accepts everything, which would adopt a forged
# bump. So both halves, per adopter, or nothing is claimed.
#
# It was LATENT for weeks -- a gate reaches its signature check only when its composed member set
# moves -- which is why this is a standing check on the clock and not something a pull request
# happens to exercise.
#
# WHAT IS SERVED AND WHAT REACHES IT. The served artefact is platform's own committed
# computed-semver/evidence/<version>.json[.bundle] at a real tag, read from a real clone. The
# operation is each adopter's own committed gate script, through the flags its own
# .github/workflows/shift-left.yml spells, under the identity constant that repository itself
# holds -- read out of the workflow by verify/fold-agreement/fold_agreement.py, whose argument
# whitelist this reuses rather than re-deriving. Only the MOVEMENT is planted (which versions the
# adopter's composed window names before and after), because that is what a Renovate pull request
# changes. Nothing is signed here: the REFUSE half changes one byte of a real signature, which
# corrupts the served artefact rather than fabricating a fixture.
#
# ALSO PRINTED, NEVER GRADED: how offline each adopter's signature check is, as an exit code per
# adopter. Until ticket 105 (2026-09-09) ludlow pinned its Sigstore trust material and verified with
# a cold TUF cache and blocked egress while driftwood and tuppence passed cosign no trust root and
# fetched one from Sigstore's TUF CDN on every CI run; every adopter now pins, and all three print
# 0. It stays a number rather than a sentence, because this ticket's own lesson is that a sentence
# about what a check cannot do goes stale and nothing re-reads it -- and the words beside a
# non-zero number are derived from the gate's own output (a TUF fetch or a refused connection),
# never from the exit code alone (review R2-1): a pinned gate refusing a wrong pin returns exit 1 too.
#
# Exit 0 observed true; 1 observed false; 3 could not look, reason on the last line.
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
# the comparator goes red on a gate that refuses everything, on a gate that adopts a corrupted
# signature, and on a refusal that names neither cosign nor the signature.
"$PY" "$HERE/real_signature.py" --selfcheck >/dev/null \
  || { echo "FAIL: real_signature.py --selfcheck -- the planted rules no longer grade as written"; exit 1; }

# 2>&1 into the tee: a grader that stops before it grades anything says WHY on stderr, and a
# red whose reason reached only the terminal is a red nobody can act on. Measured during
# ticket 101's review: a failed planting printed "FAIL: ... without grading a single
# adopter gate:" with nothing after the colon.
log="$(mktemp)"; "$PY" "$HERE/real_signature.py" "$ESTATE" 2>&1 | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: $(grep '^SUMMARY:' "$log" | head -1 | cut -c10-)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) n=$(grep -c '^FAIL:' "$log")
     if [ "$n" -eq 0 ]; then
       # A non-zero exit with no FAIL line means the grader itself stopped -- never "nothing was
       # found", which is a different sentence and a false one.
       echo "FAIL: real_signature.py exited $rc without grading a single adopter gate: $(tail -1 "$log")"
     else
       a=$(grep -c '^FAIL: .*did NOT accept' "$log")
       r=$(grep -c '^FAIL: .*ADOPTED the same evidence' "$log")
       n2=$(grep -c "^FAIL: .*names neither cosign nor the signature" "$log")
       if [ $((a + r + n2)) -eq 0 ]; then
         # A red that is not about any gate's answer -- the planting failed, or the grader stopped.
         # Reporting it in the gate-shaped sentence would print two zero counts and name the wrong
         # thing, which is how a red teaches its reader to ignore it (ticket 101 review, F3).
         echo "FAIL: $(grep -m1 '^FAIL:' "$log" | cut -c7-)"
       else
         echo "FAIL: an adopter gate did not verify platform's real published signature the way its own workflow runs it ($a), refused a corrupted one for a reason naming neither cosign nor the signature ($n2), or adopted the same evidence with one byte of that signature changed ($r) -- each named above"
       fi
     fi;;
esac
rm -f "$log"; exit "$rc"
