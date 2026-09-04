#!/usr/bin/env bash
# NORTH-STAR §4 step 3: price crosses band and PR opens (ticket 25 builds the python half;
# ticket 26 owns the cluster half). Real, and offline: a residual that crosses the adopter's OWN
# signed appetite band selects a different tier through the estate's one selection engine, at the
# version the adopter's selection-policy package publishes, and the proposer -- in --dry-run --
# would open a pull request editing the tier DECLARATION: `posture.acme.io/tier` on the
# adopter's governed Namespace manifest (ADR-0022), found by its governed label, never the pod
# label, which is that declaration's output. NOTHING IS OPENED and nothing is
# written: the dry run works on a throwaway copy in a directory that is not a git repo at all.
# What this step does NOT observe: the proposed tier landing in force in a cluster. That is
# step 4's fact, and step 4 says so itself.
#
# 2026-09-04: ticket 78's tighten-only clamp changed which outcome this fixture reaches.
# driftwood declares `isolated`, the top rung of the ladder, so a priced line can only ever
# select something LOOSER and the proposer HOLDS instead of writing. That hold is what this
# step now grades -- see the block above judge_held() in step3_band.py for why driving a
# different party is not available and why loosening driftwood's real declaration to keep a
# green was refused. The file name is left alone: this is still NORTH-STAR §4 step 3, and the
# price still crosses the band.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 3 "price crosses band and PR opens"
"$PY" -c 'import yaml' 2>/dev/null || skip "python lacks pyyaml"
log="$(mktemp)"; trap 'rm -f "$log"' EXIT
# The judgement below is only ever handed ONE document shape by the real estate (driftwood is
# declared `isolated`, the top rung, so the clamp always holds). A judgement never exercised on
# the shapes it is meant to catch is not a judgement, so it is driven first on fixtures.
"$PY" "$E2E_DIR/step3_band.py" --selfcheck >/dev/null 2>&1 \
  || fail "step3_band.py --selfcheck: the held-document judgement does not bite, so this step's verdict cannot be trusted"
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
