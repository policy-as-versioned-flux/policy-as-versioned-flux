#!/usr/bin/env bash
# Eco-system ticket 45 / ADR-0019 / ADR-0020. Can each adopter re-derive its own signed prices
# with the publisher's clone absent, and does every switching cost it prints carry the adopter's
# own perspective, its own currency, and a window it was really annualised over?
#
# Every read is of a SERVED tree: the adopter's own commit at `origin/main`, FETCHED first and
# then read with `git show origin/main:` (never HEAD, never a working tree -- review F7), and the
# publisher's tree AT THE TAG THAT ADOPTER PINS, out of the adopter's own Flux pin. Never
# platform's main, never a file merely existing. The vendored converter is replayed with the
# invocation its own PROVENANCE.json records, in a bare directory, to the digest it records --
# no flag is guessed (review F1). The fetch is the one thing here that needs the network; a unit
# that cannot be fetched is a could-not-look naming the reason, never a quiet read of the clone.
#
# Exit 0 observed true; 3 could not look (no estate, no interpreter, a unit that could not be
# fetched, nothing vendored yet, no vendored converter records an invocation, an adopter with no
# signed size); 1 observed false.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
[ -d "$ROOT/.estate-clone" ] || { echo "SKIP: no .estate-clone (run clone-estate.sh)"; exit 3; }

"$PY" "$HERE/portability.py" selfcheck >/dev/null || {
  echo "FAIL: portability.py selfcheck — the planted defects no longer bite"; exit 1; }

log="$(mktemp)"; "$PY" "$HERE/portability.py" check | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: every adopter's served commit carries its own copy of every payload it was priced from, byte-identical to the publisher's own artefact at the tag it pins, and the vendored converter replays the invocation its record names, in a bare directory with that publisher's clone absent, to the digest the record says was priced; every switching cost is annualised over a window between two signed dates under that adopter's own perspective and currency; and no price string names the machine that composed it";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") portability check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
