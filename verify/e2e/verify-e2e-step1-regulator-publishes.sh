#!/usr/bin/env bash
# NORTH-STAR §4 step 1: a regulator publishes. ico's newest local envelope validates against
# platform/feeds/schema.json and its version is a gitsign tag on the real ico remote
# (ticket 21 contract, ADR-0019). Tag queued for cut-release.yml -> SKIP naming it.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 1 "regulator publishes"
"$PY" -c 'import jsonschema, yaml' 2>/dev/null || skip "python lacks jsonschema/pyyaml"
[ -d "$ESTATE/ico" ] || skip "no .estate-clone/ico (run clone-estate.sh)"
log="$(mktemp)"; trap 'rm -f "$log"' EXIT
"$PY" "$ROOT/verify/feed-contract/feed_contract.py" newest ico penalty-schema | tee "$log"; rc=${PIPESTATUS[0]}
case $rc in
  0) pass "ico's newest penalty-schema envelope validates and its tag is on the real remote";;
  3) skip "$(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) fail "ico's newest penalty-schema envelope is not published";;
esac
