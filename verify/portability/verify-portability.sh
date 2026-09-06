#!/usr/bin/env bash
# Eco-system ticket 45 / ADR-0019 / ADR-0020. Can each adopter re-derive its own signed prices
# with the publisher's clone absent, and does every switching cost it prints carry the adopter's
# own perspective, its own currency, and a window it was really annualised over?
#
# Every read is of a SERVED tree: the adopter's own commit (`git show HEAD:`) and the
# publisher's tree AT THE TAG THAT ADOPTER PINS, out of the adopter's own Flux pin. Never a
# working tree, never platform's main, never a file merely existing. Offline throughout.
#
# Exit 0 observed true; 3 could not look (no estate, no interpreter, nothing vendored yet, an
# adopter with no signed size); 1 observed false.
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
  0) echo "PASS: every adopter carries its own copy of every payload it was priced from and the converter that priced it, byte-identical to the publisher's own artefact at the tag it pins, runnable with that publisher's clone absent; and every switching cost is annualised over a window between two signed dates under that adopter's own perspective and currency";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") portability check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
