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
#   * live, where GitHub is reachable: each clock ran inside its own period.
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

# The live half needs `gh` AND an authenticated session. Without either, schedules.py itself
# records one SKIP line and still runs everything that does not need the network.
offline=""
command -v gh >/dev/null 2>&1 || offline="--offline"

log="$(mktemp)"; trap 'rm -f "$log"' EXIT
"$PY" "$HERE/schedules.py" check $offline | tee "$log"
rc=${PIPESTATUS[0]}

case $rc in
  0) echo "PASS: every clock is declared, timed, caged to the observation lane, unable to mint a"
     echo "PASS: signed artefact, and running inside its period";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") schedule/cage check(s) observed false";;
esac
exit "$rc"
