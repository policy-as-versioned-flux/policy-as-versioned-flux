#!/usr/bin/env bash
# Ticket 21 / ADR-0019. Every published feed under .estate-clone/ validates against the one
# envelope (platform/feeds/schema.json) and its own payload schema; every adopter inherits[]
# resolves to a publisher's publishes[] record and to a tag on the publisher's REAL remote.
# Exit 0 observed true; 3 could not look (remote unreachable, or a tag queued for
# cut-release.yml); 1 observed false.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import jsonschema, yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks jsonschema/pyyaml"; exit 3; }
fi
[ -d "$ROOT/.estate-clone/platform" ] || bash "$ROOT/clone-estate.sh" >/dev/null || { echo "FAIL: could not assemble .estate-clone/"; exit 1; }

"$PY" "$HERE/feed_contract.py" selfcheck >/dev/null || { echo "FAIL: feed_contract.py selfcheck"; exit 1; }
log="$(mktemp)"; "$PY" "$HERE/feed_contract.py" check | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  # "resolves to a real tag" was read as a signature check. It is not: `git ls-remote --tags`
  # proves a tag of that NAME exists on the publisher's real remote and nothing about who signed
  # it. The gitsign verification of a tag is verify/e2e/verify-e2e-step6-provenance.sh part 3 and
  # platform/verify-source-verification.sh; this line says only what it looked at.
  0) echo "PASS: every published feed is one envelope, and every subscription names a tag that exists on the publisher's real remote (existence, not signature -- step 6 checks the signature)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") feed-contract check(s) observed false";;
esac
rm -f "$log"; exit "$rc"
