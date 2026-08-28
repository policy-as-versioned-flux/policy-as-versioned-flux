#!/usr/bin/env bash
# NORTH-STAR §4 step 7: honesty. Every other step script exists and, run with a 120s timeout,
# ends on a PASS:/FAIL:/SKIP: line. A hung or silent step is a FAIL: the harness may not
# hide a step it cannot grade.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 7 "honesty"
bad=0
for n in 1 2 3 4 5 6; do
  s=$(ls "$E2E_DIR"/verify-e2e-step$n-*.sh 2>/dev/null | head -1)
  [ -n "$s" ] || { echo "  step $n: missing script"; bad=$((bad+1)); continue; }
  last="$(timeout 120 bash "$s" 2>/dev/null | tail -1)"; rc=${PIPESTATUS[0]}
  case "$rc/$last" in
    124/*) echo "  step $n: hung (120s)"; bad=$((bad+1));;
    0/PASS:*|3/SKIP:*|[12456789]*/FAIL:*) echo "  step $n: $last";;
    *) echo "  step $n: exit $rc with last line '$last' (not PASS:/FAIL:/SKIP:)"; bad=$((bad+1));;
  esac
done
[ "$bad" -eq 0 ] || fail "$bad step(s) cannot be graded honestly"
pass "steps 1-6 each end on PASS:/FAIL:/SKIP: with a matching exit code"
