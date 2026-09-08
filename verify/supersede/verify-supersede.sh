#!/usr/bin/env bash
# Eco-system ticket 84 / ticket 13 D5 / ADR-0010's banner. Being behind costs something: an
# adopter feed pin sitting behind a newer major its publisher has tagged is priced by a
# `supersede` line in the adopter's SERVED composed/evidence.json (its origin/main, fetched and
# read with `git show`), under the adopter's own perspective and currency, ramped by platform's
# EOL ramp from the day the newer tag was cut (read off the tag object fetched read-only) to the
# entry's own as-of. Prints, as numbers: pins behind a newer tagged major and how many carry the
# line; untagged-feed pins and how many carry a hole (the hole itself is
# verify-untagged-pin-is-priced.sh's grade); retirement PRs opened/merged on wargamer/retire-*
# branches (counted off GitHub, never graded: opened is the clock's, merged is a human's).
# Exit 0 observed true; 3 could not look (a unit that could not be fetched, a remote or a tag
# that could not be read, an adopter whose pinned platform composer carries no supersede rule --
# named by tag); 1 observed false. Network: one fetch per unit, one ls-remote per publisher, one
# tag fetch per behind pin, one gh pr list per adopter, all read-only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import jsonschema, yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks jsonschema/pyyaml"; exit 3; }
fi
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/supersede.py" selfcheck >/dev/null || { echo "FAIL: supersede.py selfcheck -- the planted grades no longer bite"; exit 1; }
log="$(mktemp)"; err="$(mktemp)"
"$PY" "$HERE/supersede.py" check >"$log" 2>"$err"; rc=$?
cat "$log"; [ -s "$err" ] && cat "$err" >&2
graded_fails=$(grep -c '^FAIL:' "$log")
numbers="$(grep '^NOTE: adopters behind' "$log" | head -1 | cut -c7-); $(grep '^NOTE: untagged-feed' "$log" | head -1 | cut -c7-); $(grep '^NOTE: retirement' "$log" | head -1 | cut -c7-)"
case $rc in
  0) echo "PASS: every adopter feed pin at its served commit is either at the newest major its publisher's real remote carries a tag for, or priced as behind by a supersede line under the adopter's own perspective and currency, from the day the newer tag was cut to the entry's own as-of, base x (ramp - 1) -- $numbers";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-) -- $numbers";;
  *) if [ "$graded_fails" -gt 0 ]; then
       echo "FAIL: $graded_fails supersede check(s) observed false -- $numbers"
     else
       echo "FAIL: supersede.py exited $rc having graded nothing -- it crashed rather than observed anything: $(tail -1 "$err" 2>/dev/null || echo 'no output')"
     fi;;
esac
rm -f "$log" "$err"; exit "$rc"
