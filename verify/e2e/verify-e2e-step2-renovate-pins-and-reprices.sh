#!/usr/bin/env bash
# NORTH-STAR §4 step 2: renovate pins and re-prices (ticket 25). Real, and offline: an adopter's
# committed tree is copied to a temp dir, one pinned parent version in its own party.yaml is
# bumped from the pinned version to the next one present locally -- the single edit a merged
# Renovate PR makes -- and composition is re-run. The two prices[] documents must differ.
# Exit 3 (could not look) when no adopter pins a priceable feed that has a newer version on disk.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 2 "renovate pins and re-prices"
"$PY" -c 'import yaml' 2>/dev/null || skip "python lacks pyyaml"
log="$(mktemp)"; trap 'rm -f "$log"' EXIT
"$PY" "$E2E_DIR/step2_reprice.py" | tee "$log" | grep -v '^\(PASS\|FAIL\|SKIP\): '; rc=${PIPESTATUS[0]}
last="$(tail -1 "$log")"
case $rc in
  0) pass "${last#PASS: }";;
  3) skip "${last#SKIP: }";;
  *) fail "${last#FAIL: }";;
esac
