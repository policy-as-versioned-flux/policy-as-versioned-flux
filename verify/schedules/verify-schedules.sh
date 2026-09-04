#!/usr/bin/env bash
# Ticket 28 / ADR-0024 (which supersedes ADR-0015 point 5). The eco-system runs on daily clocks,
# and the lane those clocks write to is a cage:
#
#   * every unit carries the clocks its own party artefact and its own contents say it needs --
#     a publisher fetch, an adopter's Renovate run and propose-tier, a twin sweep where an
#     overlay lives, the hub's truth run -- and each of them has a `schedule:`;
#   * every scheduled job that pushes the default branch stages ONLY observation paths
#     (talk/truth.log, drift/samples.jsonl, captures/**, observations/**), declares that list in
#     its own `env:` so the workflow and this checker cannot drift apart, and carries a cage step
#     that fails the run on anything else. The workflow YAML is PARSED, not grepped;
#   * no scheduled job can mint or merge a signed artefact -- no `git tag`, no `gh release
#     create`, no `gh pr merge`. A release stays a human act;
#   * live: each clock ran inside its own period, and a clock that did not names the open
#     ticket that owns its red (verify/schedules/clock-owners.yaml, eco-system ticket 85).
#
# WHERE THE LIVE HALF GETS ITS FACTS (ticket 56, 2026-09-04). This script runs inside the gate,
# beside 84 verify scripts cloned unpinned off eight other organisations' default branches, and
# the gate step holds no GitHub credential on purpose -- so until now the live half SKIPped on
# every citable run and the surface was permanently blind to whether any clock had ticked.
# `truth.yml` now runs a separate `clocks` job first: it holds `actions: read`, runs no
# third-party code, and writes the raw facts (per unit the ruleset state, per clock the remote
# `schedule:` and the newest scheduled run) to a JSON file the gate job reads through
# `CLOCK_VERDICT`. Grading happens here, holding nothing. Locally, an authenticated `gh` is used
# directly. A CLOCK_VERDICT that is missing, malformed or stale is a could-not-look that says so;
# it never falls back to a credential this job is not supposed to have. The file carries the run
# id and repository that wrote it and a reader inside a workflow run refuses any other run's file
# -- which narrows the window on a forged clocks.json rather than closing a trust boundary, since
# the scripts beside this one could rewrite schedules.py itself (ticket 56, round 2).
#
# A clock's newest scheduled run that is still IN FLIGHT -- including the very run doing the
# grading, which is what a scheduled truth.yml run sees when it reads truth.yml -- is a named SKIP
# and never a red: a run that has not finished has concluded nothing.
#
# This script grades the PROMISE: what the workflow says its next run may stage. The server-side
# ruleset ADR-0024 named cannot exist on a public repository (ADR-0023, amended 2026-09-03), so
# the other half of the cage is detective: verify-lane.sh, beside this one, walks the history of
# every observation ref and fails on any commit a scheduled identity landed outside the lane.
#
# Exit 0 observed true; 3 could not look, with the reason on the last line; 1 observed false.
# Offline the first three checks still run in full: absence of a network is never a pass, and
# never an excuse to skip the half that does not need one.
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

"$PY" "$HERE/schedules.py" selfcheck >/dev/null \
  || { echo "FAIL: schedules.py selfcheck -- the cage does not bite its own fixtures"; exit 1; }

# The live half reads CLOCK_VERDICT if the workflow handed one in, else an authenticated `gh`.
# With neither, schedules.py records one named SKIP per unit and still runs everything that does
# not need the network. `--offline` is only for the case where `gh` is not installed at all and
# no verdict file was handed in; schedules.py decides the rest and says which source it used.
offline=""
if [ -z "${CLOCK_VERDICT:-}" ] && ! command -v gh >/dev/null 2>&1; then offline="--offline"; fi

log="$(mktemp)"; trap 'rm -f "$log"' EXIT
"$PY" "$HERE/schedules.py" check $offline | tee "$log"
rc=${PIPESTATUS[0]}

case $rc in
  0) echo "PASS: every clock is declared, timed, caged to the observation lane, unable to mint a"
     echo "PASS: signed artefact, and running inside its period";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  # The FAIL line names the reds themselves, not just how many: "5 clocks are red" sends a reader
  # to the capture, and every one of these lines already carries the ticket that owns it
  # (clock-owners.yaml). One line, so the grade table can hold it.
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") schedule/cage check(s) observed false:$(
       grep '^FAIL:' "$log" | sed 's/^FAIL: \([^:]*\):.*/ \1/' | tr -d '\n')";;
esac
exit "$rc"
