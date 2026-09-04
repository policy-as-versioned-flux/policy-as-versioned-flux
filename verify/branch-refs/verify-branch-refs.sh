#!/usr/bin/env bash
# Eco-system tickets 62 and 77 / NORTH-STAR section 2. No unit consumes another organisation at
# a branch: every actions/checkout of a different policy-as-versioned repository names a tag,
# and where the ref is a workflow expression the consuming repository DECLARES which version it
# is on, in a GitRepository pin under gitops/, a <PUBLISHER>_TAG constant in that workflow, or
# its own party.yaml inherits[] where neither of those names that publisher. The declared tag
# must be one the publisher has actually signed. A `repository:` that is itself an expression is
# expanded from its job's own matrix and graded the same way (insurer/fetch.yml), or, where no
# literal matrix decides it, counted and named as a could-not-look.
#
# Exit 0 observed true; 3 could not look (a publisher this checkout has no clone of, or one that
# has cut no tag at all -- there is nothing to pin to); 1 observed false. Offline: every fact is
# a file in the estate checkout or a tag in it, which clone-estate.sh fetches on purpose.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi

# `--selfcheck` runs the planted fixtures ALONE, which is what this ticket's Answer cites and
# what a reader with no estate clone can run. Until 2026-09-04 the flag was accepted and
# silently ignored, and the full estate check ran instead.
if [ "${1:-}" = "--selfcheck" ]; then
  if "$PY" "$HERE/branch_refs.py" selfcheck; then
    echo "PASS: branch_refs.py selfcheck: every planted refusal bites and every planted could-not-look stays a could-not-look"
    exit 0
  fi
  echo "FAIL: branch_refs.py selfcheck -- the planted refusals no longer bite"; exit 1
fi

ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/branch_refs.py" selfcheck >/dev/null || { echo "FAIL: branch_refs.py selfcheck -- the planted refusals no longer bite"; exit 1; }
log="$(mktemp)"; err="$(mktemp)"
"$PY" "$HERE/branch_refs.py" check >"$log" 2>"$err"; rc=$?
cat "$log"; [ -s "$err" ] && cat "$err" >&2
# A grade and a crash are different facts (the shape verify-untagged-pin-is-priced.sh uses): an
# exit 1 with no FAIL line at all is the script falling over, not an observation.
graded_fails=$(grep -c '^FAIL:' "$log")
case $rc in
  0) echo "PASS: every cross-organisation checkout in the estate names a tag its own repository pins, and every one of those tags is signed on the publisher's remote ($(grep -c '^PASS:' "$log") checkout(s))";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) if [ "$graded_fails" -gt 0 ]; then
       echo "FAIL: $graded_fails cross-organisation checkout(s) are not pinned to a signed tag: $(grep -m1 '^FAIL:' "$log" | cut -c7-)"
     else
       echo "FAIL: branch_refs.py exited $rc having graded nothing -- it crashed rather than observed anything: $(tail -1 "$err" 2>/dev/null || echo 'no output')"
     fi;;
esac
rm -f "$log" "$err"; exit "$rc"
