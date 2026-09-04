#!/usr/bin/env bash
# Eco-system ticket 69 / ADR-0020. An untagged pin is a priced hole, never a refusal and never
# free. For every adopter inherits[] feed pin, the pin's signature state is read from the
# publisher's REAL remote -- ls-remote for tag existence, then the platform's identity-pinned
# gitsign verifier over the tag object fetched read-only, under the publisher's own release.yml
# pins -- and graded: a signed tag PASSes with no hole; an untagged pin PASSes only where the
# adopter's composed/evidence.json prices it as an open hole on the premium entry under the
# adopter's own perspective and currency, and FAILs otherwise; a remote or a verifier that could
# not look is a SKIP.
# Exit 0 observed true; 3 could not look; 1 observed false. Network: ls-remote and one tag fetch
# per pin, both read-only. Nothing here signs, tags or writes to a remote.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import jsonschema, yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks jsonschema/pyyaml"; exit 3; }
fi
# PAVC_ESTATE_CLONE names another estate to grade (the override composition.py and
# verify-priced-holes.sh take), so a scratch estate of freshly composed adopter copies can be
# graded before the owner pushes them.
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE/platform" ] || { echo "SKIP: no $ESTATE/platform -- run ./clone-estate.sh first"; exit 3; }

"$PY" "$HERE/untagged_pin.py" selfcheck >/dev/null || { echo "FAIL: untagged_pin.py selfcheck -- the planted grades no longer bite"; exit 1; }
log="$(mktemp)"; "$PY" "$HERE/untagged_pin.py" check | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: every adopter feed pin resolves to a tag that verifies under its publisher's own identity pins, or is priced as a hole under the adopter's own perspective and currency ($(grep -c 'untagged (' "$log") untagged pin(s) priced)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") untagged-pin check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
