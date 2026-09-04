#!/usr/bin/env bash
# Ticket 70 / ADR-0023 (amended 2026-09-03). The observation lane, graded on what actually
# landed, not on what the workflow promises.
#
# verify-schedules.sh reads each scheduled workflow's YAML and grades the cage step it carries.
# That is a promise about the future. This script reads the past: it walks the first-parent
# history of every observation ref -- each unit's `main` and, where a publisher clock has
# created it, the orphan `observations` branch -- plus the hub's own `main`, and grades every
# commit a scheduled identity has ever landed there:
#
#   * it touched only observation paths (talk/truth.log, drift/samples.jsonl, talk/captures/**,
#     observations/**), read from the unit's own OBSERVATION_LANE declarations with ADR-0024
#     point 3 as the floor, and never a declaration (a tier, a pin, a floor, an overlay, a
#     priced evidence file, a published feed);
#   * it is not a merge -- a clock appends, it never merges.
#
# The scheduled identities are the `user.email` values the unit's own scheduled workflows
# configure, plus GitHub's github-actions[bot]. A commit authored by a clock that reached the
# ref through a human's merge, squash or rebase is a reviewed proposal and is not graded; a
# human's own commit is never a lane violation whatever it touches.
#
# Why this exists: the push ruleset ADR-0023/0024 promised as the server-side cage cannot be
# applied -- GitHub allows push rulesets on private and internal repositories only, and these
# are public (ticket 58 Q4(b), 2026-08-31). So the cage is preventive in the workflow step and
# DETECTIVE here: a declaration that slips past the step is a red on the next citable run.
#
# Signature verification of the landed commits is not graded here: gitsign is not in git's own
# verify chain (`%G?` reads N or U for every one of them) and the Rekor-backed identity check is
# ticket 73's verifier, not a second copy of it.
#
# Exit 0 observed true; 3 could not look, with the reason on the last line; 1 observed false.
# Fully offline: it reads the refs .estate-clone/ already holds, after a best-effort fetch it
# names in its own output when that fetch fails.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi

[ -d "$ROOT/.estate-clone/platform" ] || bash "$ROOT/clone-estate.sh" >/dev/null \
  || { echo "FAIL: could not assemble .estate-clone/"; exit 1; }

"$PY" "$HERE/lane.py" selfcheck >/dev/null \
  || { echo "FAIL: lane.py selfcheck -- the lane grader does not bite its own fixtures"; exit 1; }

log="$(mktemp)"; trap 'rm -f "$log"' EXIT
"$PY" "$HERE/lane.py" check 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}
fails=$(grep -c '^FAIL:' "$log")

# A checker that crashed (a traceback, no FAIL: line of its own) is not a lane verdict: it is
# a could-not-look that exits 1 on Python's account, and it must not read as "0 outside the lane".
case $rc in
  0) echo "PASS: every commit a scheduled identity has landed on an observation ref touched only"
     echo "PASS: the observation lane, and none of them is a merge";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) if [ "$fails" -gt 0 ]; then
       echo "FAIL: $fails landed commit(s) or ref(s) observed outside the lane"
     else
       echo "FAIL: lane.py did not grade -- it exited $rc without a verdict ($(tail -1 "$log"))"
       rc=1
     fi;;
esac
exit "$rc"
