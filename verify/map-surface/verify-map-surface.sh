#!/usr/bin/env bash
# The map matches the surface (eco-system ticket 67).
#
# THE DEFECT. `.scratch/ecosystem/map.md` is the one live wayfinder. On 2026-08-31 it said
# "65 pass, 0 fail, 16 could-not-look of 83. Nothing is red." No TRUTH line ever recorded that
# figure -- it was a local rehearsal -- and the citable line of the day read `pass=53 fail=7
# skip=21`. It was corrected by hand at charting time. Correcting a map fixes a map. This script
# refuses the next one.
#
# WHAT IT GRADES, five rules:
#   1. every pass/fail figure map.md quotes is a figure talk/truth.log records, and one quoted
#      beside a run number is THAT run's figure (ticket 67 item (d));
#   2. every check map.md names in backticks is one the gate discovers -- a row in
#      talk/verify-manifest.txt, which talk/verify-all.sh requires for every script it runs;
#   3. every relative link in map.md resolves, because "a reader following the map" is the
#      ticket's own definition of done;
#   4. no unit repository declares an OBSERVATION_LANE path it does not own (item (c)). The hub's
#      four-path list had been copied verbatim into twelve unit workflows across eight
#      repositories, and verify/schedules/lane.py grades every commit a scheduled identity landed
#      in a repository against the union of THAT repository's own declarations -- so a copied
#      path is one a clock there may land and be graded green for;
#   5. ticket 67 item (a)'s corrections are still in the record, and what they removed has not
#      come back.
#
# HOW IT COMPOSES WITH verify/cited-truth/ (ticket 80). That check grades the same class of claim
# in `.scratch/ecosystem/issues/*.md` and names map.md as out of its scope; this one grades map.md
# and reads no ticket. The populations are disjoint, nothing is graded twice, and the union is the
# whole record. What is shared is the PARSER -- both resolve a citation through
# talk/truth_manifest.py's parse_truth -- so a change to the TRUTH line's shape cannot make one of
# the two quietly wrong.
#
# WHAT IT REFUSES TO GRADE, counted rather than asserted: whether the figure the map quotes is the
# RIGHT figure, or the check it names the right check -- it grades that both exist on the surface.
# Ticket 67 item (b) is graded by ico's own .github/scripts/verify-declared-bump.sh, in the
# manifest, because reading another party's declaration from a working copy here would be the
# proxy this ticket exists to end. A figure whose own text line calls it local, a rehearsal, a
# fixture, planted, hypothetical, not citable or an Actions-log quote, and one a DATED correction
# elsewhere in the map disposes of, are not graded -- and both counts are PRINTED on every run, so
# the size of the ungraded population is a number that moves rather than a sentence written once.
#
# NO COULD-NOT-LOOK, by decision (delegated, ADR-0025, 2026-09-06), following verify/can-record/
# and verify/cited-truth/. Rules 1 to 3 and 5 read only files in this repository. Rule 4 reads
# .estate-clone/, which clone-estate.sh assembles and which verify/schedules/verify-lane.sh
# already refuses rather than shrugs for. So this row declares no skip pattern in
# talk/verify-manifest.txt and there is none to declare: a missing map, a missing truth.log, a
# missing manifest and a missing unit are each RED with their own line.
#
# Exit 0 PASS, 1 FAIL. Never 3.
#
#   verify-map-surface.sh            selfcheck first, then grade the committed record
#   verify-map-surface.sh selfcheck  selfcheck only: planted defects grade as planted
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || { echo "FAIL: cannot enter the hub root"; exit 1; }
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
GRADER="$HERE/map_surface.py"

[ -n "$PY" ] || { echo "FAIL: no python to read the record with; a runner that has lost its interpreter goes red, it does not shrug"; exit 1; }

if [ "${1:-}" = selfcheck ]; then
  "$PY" "$GRADER" selfcheck || exit 1
  echo "PASS: selfcheck: an unrecorded figure, a figure disagreeing with the run beside it, a run"
  echo "PASS: nobody recorded, a check the gate does not discover, a dead link, a lane path the"
  echo "PASS: repository does not own and a record correction that came undone each fail by name"
  exit 0
fi

bad=0
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

say "0. the grader can fail"
"$PY" "$GRADER" selfcheck >/dev/null || { echo "  !! map_surface.py selfcheck: the grader does not bite its own planted defects"; bad=$((bad + 1)); }
[ "$bad" -eq 0 ] && echo "  ok   every rule bites a planted defect"

say "1. what a citation points at is here to be read"
[ -f "$ROOT/.scratch/ecosystem/map.md" ] || { echo "  !! .scratch/ecosystem/map.md is missing: there is no map to grade"; bad=$((bad + 1)); }
[ -f "$ROOT/talk/truth.log" ] || { echo "  !! talk/truth.log is missing: no figure the map quotes can be resolved"; bad=$((bad + 1)); }
[ -f "$ROOT/talk/verify-manifest.txt" ] || { echo "  !! talk/verify-manifest.txt is missing: what the gate discovers cannot be read"; bad=$((bad + 1)); }
[ -f "$ROOT/talk/truth_manifest.py" ] || { echo "  !! talk/truth_manifest.py is missing: the one TRUTH-line parser is not here"; bad=$((bad + 1)); }
if [ ! -d "$ROOT/.estate-clone/platform" ]; then
  bash "$ROOT/clone-estate.sh" >/dev/null 2>&1 \
    || { echo "  !! could not assemble .estate-clone/: a lane declaration cannot be read against a repository that is not here"; bad=$((bad + 1)); }
fi
[ "$bad" -eq 0 ] && echo "  ok   map.md, talk/truth.log, the manifest, the parser and .estate-clone are all readable"

say "2. the map quotes no figure and names no check the surface does not carry, and item (a) holds"
"$PY" "$GRADER" grade "$ROOT" || bad=$((bad + 1))

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: every pass/fail figure .scratch/ecosystem/map.md quotes is a figure talk/truth.log records, every check it names is one talk/verify-all.sh discovers, every relative link resolves, no unit declares an observation-lane path it does not own, and ticket 67's record corrections are each still there"
  exit 0
fi
echo "FAIL: the record and the surface disagree -- $bad of this script's legs observed false; the ' == ' tally above says how many findings of which kind, and every one of them names its own file"
exit 1
