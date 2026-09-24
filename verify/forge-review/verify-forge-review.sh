#!/usr/bin/env bash
# Eco-system ticket 87 item 1. The pin and the protection cannot drift apart: every branch an
# identity pattern the estate serves admits is one the forge refuses to move without a reviewed
# pull request, and refuses to create unreviewed; every one of the nine repositories carries a
# ruleset and a floor on its default branch; every release tag is held against update and delete.
# forge_review.py says what it grades and its stated ceiling.
#
# WHERE THE FACTS COME FROM. The gate job holds no GitHub credential (ticket 56). truth.yml's
# `clocks` job runs `forge_review.py collect`, which reads files and asks GitHub, runs no
# third-party code, and hands the raw facts to the gate through FORGE_FACTS. Locally an
# authenticated `gh` collects them here. With neither this is a could-not-look, never a pass.
#
# Exit 0 observed true; 3 could not look; 1 observed false.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3

if [ "${1:-}" = "--selfcheck" ]; then
  if "$PY" "$HERE/forge_review.py" selfcheck; then
    echo "PASS: forge_review.py selfcheck: an unreviewed pinned main, a release branch anyone may create and a tag ruleset not in force are each refused"
    exit 0
  fi
  echo "FAIL: forge_review.py selfcheck -- a planted refusal no longer bites"; exit 1
fi

"$PY" "$HERE/forge_review.py" selfcheck >/dev/null \
  || { echo "FAIL: forge_review.py selfcheck -- a planted refusal no longer bites"; exit 1; }

ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
facts="${FORGE_FACTS:-}"
if [ -z "$facts" ]; then
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    echo "SKIP: no FORGE_FACTS file -- the clocks job did not hand one in, and the gate holds no credential to read the forge with"; exit 3
  fi
  if ! command -v gh >/dev/null 2>&1 || ! gh auth status >/dev/null 2>&1; then
    echo "SKIP: no FORGE_FACTS file and no authenticated gh to read the forge with"; exit 3
  fi
  facts="$tmp/forge.json"
  "$PY" "$HERE/forge_review.py" collect --estate "$ESTATE" --out "$facts" >/dev/null \
    || { echo "SKIP: forge_review.py collect could not read the forge"; exit 3; }
fi
[ -s "$facts" ] || { echo "SKIP: the forge facts file $facts is missing or empty -- the clocks job did not hand one in"; exit 3; }

log="$tmp/check.out"
"$PY" "$HERE/forge_review.py" check --facts "$facts" --estate "$ESTATE" >"$log" 2>&1; rc=$?
cat "$log"
case $rc in
  0) echo "PASS: every branch an estate identity pin admits is protected by a reviewed-PR ruleset on the forge, all nine repositories carry the floor, and every release tag is held ($(grep -c '^PASS:' "$log") repositories)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) if grep -q '^FAIL:' "$log"; then
       echo "FAIL: $(grep -c '^FAIL:' "$log") forge protection(s) observed missing: $(grep -m1 '^FAIL:' "$log" | cut -c7-)"
     else
       echo "FAIL: forge_review.py exited $rc having graded nothing: $(tail -1 "$log")"
     fi;;
esac
exit "$rc"
