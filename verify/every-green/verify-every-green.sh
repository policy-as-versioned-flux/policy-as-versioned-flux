#!/usr/bin/env bash
# Beat (ecosystem ticket 76): "every green rests on an observation."
#
# Reads every verify script the gate discovers and refuses the shape that produced fourteen
# false greens in REVIEW-2026-09-02: a `SKIP` printed and then `exit 0`, which verify-all.sh
# grades PASS. Ticket 55 closed this class once by hand and seven scripts escaped it; this is the
# net that names the next one by file and line rather than waiting for a review to.
#
#   PASS (exit 0)  no discovered script prints SKIP and exits 0
#   FAIL (exit 1)  one does, named
#   SKIP (exit 3)  no .estate-clone to read (the hub alone is half the surface)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

say "1. the scanner grades planted good and bad scripts as planted"
python3 "$HERE/every_green.py" selfcheck || { echo "FAIL: every_green.py selfcheck failed"; exit 1; }

[ -d "$ROOT/.estate-clone" ] || { echo "SKIP: no .estate-clone (run clone-estate.sh); only the hub's own verify/ could be read"; exit 3; }

say "2. every verify script the gate discovers, hub and estate"
if python3 "$HERE/every_green.py" scan "$ROOT/verify" "$ROOT/.estate-clone"; then
  n="$(find -L "$ROOT/verify" "$ROOT/.estate-clone" -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' | wc -l | tr -d ' ')"
  echo "PASS: none of the $n discovered verify scripts prints SKIP and then exits 0; a could-not-look is exit 3 everywhere"
  exit 0
fi
echo "FAIL: a verify script prints SKIP and then exits 0, which the gate would grade PASS (named above)"
exit 1
