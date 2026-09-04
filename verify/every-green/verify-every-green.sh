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
# script with the instrument hidden and requires exit 3 with a `SKIP:` last line. How many
# discovered scripts call it is counted on each run and printed, never quoted here. How many prose
# sites there are is not counted at all: a text scan cannot tell a false green from an honest
# narrowing. No inventory of those sites is kept here either: three attempts at one were each
# wrong, which is the same lesson. Giving the scripts that print a prose could-not-look their own
# leg is ticket 76's Answer's own follow-on ticket.
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

scan_log="$(mktemp)"; trap 'rm -f "$scan_log"' EXIT
say "2. every verify script the gate discovers, hub and estate"
python3 "$HERE/every_green.py" scan "$ROOT/verify" "$ROOT/.estate-clone" | tee "$scan_log"; rc="${PIPESTATUS[0]}"

# The figure below is measured on this run, never typed: a later ticket that gives a prose site its
# own selfcheck_absent leg moves it, and the sentence stays true without anyone editing it. How many
# prose sites there are is not counted here -- a text scan cannot tell a false green from an honest
# narrowing, which is the whole reason this net grades the verdict token instead.
discovered="$(find -L "$ROOT/verify" "$ROOT/.estate-clone" -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' 2>/dev/null)"
n="$(printf '%s\n' "$discovered" | grep -c . | tr -d ' ')"
legged="$(printf '%s\n' "$discovered" | while IFS= read -r f; do [ -n "$f" ] && grep -qE '^[[:space:]]*(if .*; then )?selfcheck_absent[[:space:]]' "$f" 2>/dev/null && echo "$f"; done | grep -c . | tr -d ' ')"
unread="$(grep -c '^  ??   could not read ' "$scan_log" | tr -d ' ')"
case "$rc" in
  0) echo "PASS: none of the $n discovered verify scripts prints the SKIP verdict token and then reaches exit 0; the prose-worded could-not-look is not graded here (see the header), and is graded only where a script carries a selfcheck_absent leg, which $legged of them do; a prose could-not-look in any of the rest is graded by nothing"
     exit 0 ;;
  3) echo "SKIP: $unread discovered verify script(s) could not be read (named above), so this run did not observe the other $((n - unread)) to be the whole surface"
     exit 3 ;;
  1) echo "FAIL: a verify script prints the SKIP verdict token and then reaches exit 0, which the gate would grade PASS (named above)"
     exit 1 ;;
  *) echo "FAIL: every_green.py scan exited $rc"
     exit 1 ;;
esac
