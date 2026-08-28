#!/usr/bin/env bash
# NORTH-STAR §4 step 3: price crosses band and PR opens (ticket 25 builds the python half;
# ticket 26 owns the cluster half). Real, and offline: a residual that crosses the adopter's OWN
# signed appetite band selects a different tier through the estate's one selection engine, at the
# version the adopter's selection-policy package publishes, and the proposer -- in --dry-run --
# would open a pull request editing the tier declaration. NOTHING IS OPENED and nothing is
# written: the dry run works on a throwaway copy in a directory that is not a git repo at all.
# What this step does NOT observe: the proposed tier landing in force in a cluster. That is
# step 4's fact, and step 4 says so itself.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 3 "price crosses band and PR opens"
"$PY" -c 'import yaml' 2>/dev/null || skip "python lacks pyyaml"
log="$(mktemp)"; trap 'rm -f "$log"' EXIT
# 2>&1: stdout was teed and stderr was not, so a traceback never reached $log and the
# verdict came out as a bare "FAIL:" with no reason at all (review, 2026-08-28).
"$PY" "$E2E_DIR/step3_band.py" 2>&1 | tee "$log" | grep -v '^\(PASS\|FAIL\|SKIP\): '; rc=${PIPESTATUS[0]}
last="$(tail -1 "$log")"
# ...and if the last line still says nothing, quote the last line that does.
case "$last" in
  PASS:*|FAIL:*|SKIP:*) ;;
  *) last="FAIL: $(grep -v '^[[:space:]]*$' "$log" | tail -1)" ;;
esac
case $rc in
  0) pass "${last#PASS: } (python half; the tier landing in force is step 4)";;
  3) skip "${last#SKIP: }";;
  *) fail "${last#FAIL: }";;
esac
