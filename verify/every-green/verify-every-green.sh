#!/usr/bin/env bash
# Beat (ecosystem ticket 76): "every green rests on an observation."
#
# Reads every verify script the gate discovers and refuses the shape that produced fourteen
# false greens in REVIEW-2026-09-02: a `SKIP` printed and then `exit 0`, which verify-all.sh
# grades PASS. Ticket 55 closed this class once by hand and seven scripts escaped it; this is the
# net that names the next one by file and line rather than waiting for a review to.
#
# WHAT THIS GRADES. One shape, by text: a print statement whose first printed token is the
# estate's `SKIP` verdict word, reaching exit 0 (or no exit at all, and so the script's own PASS
# line). It does NOT grade a could-not-look worded as prose -- `(skipped: kyverno CLI not found)`
# -- because whether the PASS after one of those is false depends on what that PASS sentence
# claims, and this net reads shapes, not sentences. See every_green.py's docstring for the four
# scripts in this estate that print a prose skip, two of which were false greens (fixed by this
# ticket) and two of which narrow their closing sentence honestly. The prose kind is caught by
# execution, not text, but only where a script carries the leg: `selfcheck_absent` re-runs a
# script with the instrument hidden and requires exit 3 with a `SKIP:` last line, and 9 of the 95
# discovered scripts carry it today. The four prose sites in this estate (verify-currency.sh,
# verify-upflow.sh and verify-reach-secrets.sh twice) carry none, so nothing grades them; ticket
# 76's Answer records that as its own ticket.
#
#   PASS (exit 0)  no discovered script prints the SKIP verdict token and then reaches exit 0
#   FAIL (exit 1)  one does, named by file and line
#   SKIP (exit 3)  no .estate-clone to read (the hub alone is half the surface), or a discovered
#                  script could not be read at all -- a could-not-read is a could-not-look
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

say "1. the scanner grades planted good and bad scripts as planted"
python3 "$HERE/every_green.py" selfcheck || { echo "FAIL: every_green.py selfcheck failed"; exit 1; }

[ -d "$ROOT/.estate-clone" ] || { echo "SKIP: no .estate-clone (run clone-estate.sh); only the hub's own verify/ could be read"; exit 3; }

say "2. every verify script the gate discovers, hub and estate"
python3 "$HERE/every_green.py" scan "$ROOT/verify" "$ROOT/.estate-clone"; rc=$?
n="$(find -L "$ROOT/verify" "$ROOT/.estate-clone" -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')"
case "$rc" in
  0) echo "PASS: none of the $n discovered verify scripts prints the SKIP verdict token and then reaches exit 0; the prose-worded could-not-look is not graded here (see the header), and is graded only where a script carries a selfcheck_absent leg, which 9 of them do and the four prose sites do not"
     exit 0 ;;
  3) echo "SKIP: a discovered verify script could not be read (named above), so this run did not observe the other $((n - 1)) to be the whole surface"
     exit 3 ;;
  1) echo "FAIL: a verify script prints the SKIP verdict token and then reaches exit 0, which the gate would grade PASS (named above)"
     exit 1 ;;
  *) echo "FAIL: every_green.py scan exited $rc"
     exit 1 ;;
esac
