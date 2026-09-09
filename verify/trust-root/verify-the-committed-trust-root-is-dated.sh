#!/usr/bin/env bash
# Eco-system ticket 105. The committed trust roots are dated, and they carry what is served.
#
# WHY. Ticket 101 pinned ludlow's Sigstore trust material in a committed trusted_root.json so its
# gate verifies platform's evidence with a cold TUF cache and no egress; ticket 105 put the same
# pin in driftwood and tuppence. A pin refuses BY NAME when it lacks a key for the log an artefact
# names -- the right failure, and a real maintenance obligation: Sigstore rotating a log turns
# three required checks red until three pull requests land. This check makes that a schedule
# rather than a surprise.
#
# PRINTED, NEVER GRADED: per adopter, the sha256 of the committed root, when it was committed and
# how many days ago, when its newest log key starts and how many days ago, every key's validity
# window against today (current / retired N days ago / not yet valid), and whether the adopters'
# copies are byte-identical. No sentence of the form "the root is fresh" is printed, because that
# sentence goes stale the day it is written.
#
# GRADED, because it cannot go stale in the reassuring direction: every log platform's own
# published evidence at the tag THAT ADOPTER pins names -- the SCT log ids in the Fulcio
# certificate's own DER, the Rekor log id in its own rekorBundle -- is carried by that adopter's
# own committed .github/scripts/trusted_root.json at HEAD, by key id, with the artefact's own
# timestamp inside the key's validFor window. Both read with `git show`, never from a working
# tree. The day this is false the adopter's gate refuses by name, so this line is red before a
# Renovate pull request is. An absent root is a could-not-look BY NAME, never a pass.
#
# Exit 0 observed true; 1 observed false; 3 could not look, reason on the last line.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE" ] || { echo "SKIP: no $ESTATE/ -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/trust_root.py" --selfcheck >/dev/null \
  || { echo "FAIL: trust_root.py --selfcheck -- the planted rules no longer grade as written"; exit 1; }

log="$(mktemp)"; "$PY" "$HERE/trust_root.py" "$ESTATE" 2>&1 | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: $(grep '^SUMMARY:' "$log" | head -1 | cut -c10-)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | tail -1 | cut -c7-)";;
  *) n=$(grep -c '^FAIL:' "$log")
     if [ "$n" -eq 0 ]; then
       echo "FAIL: trust_root.py exited $rc without grading a single committed root: $(tail -1 "$log")"
     else
       echo "FAIL: $(grep '^FAIL:' "$log" | tail -1 | cut -c7-)"
     fi;;
esac
rm -f "$log"; exit "$rc"
