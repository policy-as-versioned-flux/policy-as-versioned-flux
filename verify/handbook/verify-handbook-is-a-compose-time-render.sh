#!/usr/bin/env bash
# Eco-system ticket 34. Is every adopter's handbook a pure re-render of the artefact it SERVES?
#
# ADR-0007's last-mile section (confirmed 2026-09-06 by ticket 80) says the handbook is a
# compose-time render carried under the artefact's own tag, and that verify-fresh.sh grades it.
# platform publishes both the renderer and verify-fresh.sh; NORTH-STAR §2 forbids the publisher
# reading an institution's repository, so platform's own script proves the TOOL over planted
# repositories and this is where the three real adopters are read.
#
# WHAT IS GRADED, AND AGAINST WHAT.
#   served artefact  each adopter's composed/ tree at ONE named ref of that adopter's repository,
#                    read with git ls-tree/git show -- newest signed tag carrying a handbook,
#                    else the branch tip, and the run PRINTS which and why.
#   operation        handbook.py render, taken from the copy of compose/handbook.py that PLATFORM
#                    SERVES at the tag the adopter pins (falling back to platform's branch tip and
#                    saying so). This check carries no renderer of its own: a hub copy would grade
#                    the hub's idea of the render instead of the estate's.
#   comparison       bytes, against `git show <ref>:composed/HANDBOOK.md`.
#
# A file EXISTING is graded by nothing. A page that exists and does not re-render is the failure
# this check exists for, and it goes red rather than skipping. Two properties are proved on the
# real artefact every run so the byte comparison cannot pass vacuously: the render is PURE (same
# served bytes, another directory, another environment, identical output) and it BITES (one field
# of the served artefact moved in memory must move the page).
#
# THREE DISCLOSED LIMITS, PRINTED AS NUMBERS, never asserted: how many adopters serve a page at
# all, how many were graded at a SIGNED TAG rather than a branch tip, and how many pin a platform
# tag that already carries the renderer. Each moves on its own the day a tag is cut or a pin moves.
#
# THREE OVERRIDES, none of them set by the gate, all for grading a branch before it merges:
# PAVC_ESTATE_CLONE names another estate, PAVC_HANDBOOK_REFS="unit=ref,..." names an adopter's ref,
# and PAVC_HANDBOOK_PLATFORM_REF names a platform ref to take the renderer from. None of them can
# make a run look better than it is: the "pinned tag already carries the renderer" count is
# computed from the adopter's own pin file and never from an override.
#
# Exit 0 observed true; 1 observed false; 3 could not look, reason on the last line.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  command -v "$PY" >/dev/null 2>&1 || { echo "SKIP: no .venv and no python3 to run the grader with"; exit 3; }
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml, which the served renderer needs"; exit 3; }
fi
command -v git >/dev/null 2>&1 || { echo "SKIP: git is not on PATH, so no served ref can be read"; exit 3; }
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE" ] || { echo "SKIP: no $ESTATE/ -- run ./clone-estate.sh first"; exit 3; }

# The rules first, on planted inputs, and through the renderer PLATFORM SERVES -- so a run that
# grades the estate green has already shown, with the same code, that a hand-edited page goes red,
# that an artefact moving under an unmoved page goes red, and that a renderer ignoring its input is
# caught by the sensitivity leg rather than sliding through the byte comparison.
SERVED_RENDERER="$(mktemp)"
trap 'rm -f "$SERVED_RENDERER" "${LOG:-}"' EXIT
for ref in ${PAVC_HANDBOOK_PLATFORM_REF:-} origin/main main HEAD; do
  if git -C "$ESTATE/platform" show "$ref:compose/handbook.py" >"$SERVED_RENDERER" 2>/dev/null; then
    found="$ref"; break
  fi
done
[ -n "${found:-}" ] || { echo "SKIP: no ref of $ESTATE/platform serves compose/handbook.py, so the grader has no renderer to prove its own rules with"; exit 3; }
"$PY" "$HERE/handbook_check.py" --selfcheck "$SERVED_RENDERER" >/dev/null \
  || { echo "FAIL: handbook_check.py --selfcheck -- the planted rules no longer grade as written, so nothing this run says about the estate can be trusted"; exit 1; }

LOG="$(mktemp)"
"$PY" "$HERE/handbook_check.py" "$ESTATE" | tee "$LOG"; rc=${PIPESTATUS[0]}
counts="$(grep '^COUNTS:' "$LOG" | head -1 | cut -c9-)"
case $rc in
  # The verdict is the module's own SUMMARY, quoted rather than restated, so the line names how
  # many adopters were compared instead of hard-coding a number over however many exist.
  0) echo "PASS: $(grep '^SUMMARY:' "$LOG" | head -1 | cut -c10-)";;
  3) echo "SKIP: $(grep '^SKIP:' "$LOG" | tail -1 | cut -c7-)";;
  *) echo "FAIL: $(grep '^FAILED:' "$LOG" | head -1 | cut -c9-) serve a composed/HANDBOOK.md that is not a re-render of the artefact they serve beside it, or whose render is not a function of that artefact -- ${counts:-no counts printed}";;
esac
exit "$rc"
