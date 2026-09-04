#!/usr/bin/env bash
# NORTH-STAR §4 step 3: price crosses band and PR opens (ticket 25 builds the python half;
# ticket 26 owns the cluster half). Real, and offline: a residual that crosses the adopter's OWN
# signed appetite band selects a different tier through the estate's one selection engine, at the
# version the adopter's selection-policy package publishes, and the proposer -- in --dry-run --
# would open a pull request editing the tier DECLARATION: `posture.acme.io/tier` on the
# adopter's governed Namespace manifest (ADR-0022), found by its governed label, never the pod
# label, which is that declaration's output. NOTHING IS OPENED and nothing is written: each dry
# run works on a throwaway copy, a git repository with no remote and no credential.
# What this step does NOT observe: the proposed tier landing in force in a cluster. That is
# step 4's fact, and step 4 says so itself.
#
# 2026-09-04: ticket 78's tighten-only clamp changed which outcome the REAL declaration
# reaches. driftwood declares `isolated`, the top rung of the ladder, so a priced line can only
# select something looser and the proposer HOLDS. BOTH outcomes are graded: the hold against
# driftwood's own declaration, and the landed dry-run pull request against a throwaway copy
# whose declaration the step rewrites itself -- which is how the PR half of this step's name
# stays observed without loosening one byte of the real repository, and why a party that later
# declares a tier the priced line tightens reads as correct rather than as a fault. See the
# block above judge_held()/judge_landed() in step3_band.py.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 3 "price crosses band and PR opens"
"$PY" -c 'import yaml' 2>/dev/null || skip "python lacks pyyaml"
log="$(mktemp)"; trap 'rm -f "$log"' EXIT
# Each judgement below sees exactly ONE document shape per run -- the real declaration reaches
# one outcome and the rewritten copy the other -- and never the malformed shapes the guards
# exist for. A judgement never exercised on the shapes it is meant to catch is not a judgement,
# so both are driven first on fixtures.
"$PY" "$E2E_DIR/step3_band.py" --selfcheck >/dev/null 2>&1 \
  || fail "step3_band.py --selfcheck: the proposal-document judgements do not bite, so this step's verdict cannot be trusted"
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
