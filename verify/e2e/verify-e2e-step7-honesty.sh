#!/usr/bin/env bash
# NORTH-STAR §4 step 7: "Honesty: one command reports every claim above as pass, fail or
# could-not-look."
#
# This is the roll-up, not a seventh claim of its own. It runs steps 1..6 and prints them as one
# table. It FAILS when a step cannot be GRADED honestly, which is three things:
#
#   * the step script is missing, hangs, or ends on something that is not PASS:/FAIL:/SKIP:;
#   * its exit code and its last line disagree (exit 0 under a SKIP: line, exit 3 under a PASS:);
#   * it claims PASS while that same PASS line names something it could not look at.
#
# It does NOT fail merely because a step reports FAIL or SKIP -- talk/verify-all.sh already
# grades each step script on its own, and counting the same red twice would inflate the TRUTH
# line. A red step shows as red in the table and step 7 stays green, because step 7's claim is
# "every claim above is reported honestly", not "every claim above is true".
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 7 "honesty"

# Phrases that mean "I did not actually look". A PASS line carrying one of these is a green that
# could not look, which NORTH-STAR §3.6 calls a red. Deliberately narrow: words that describe an
# OBSERVED state of the world (a tag not yet cut, a queued artefact, a piece handed to another
# step) are not on this list, because observing that is looking, not failing to look.
HEDGE='could not|couldn.t|cannot|can.t look|unreachable|not reachable|unable to|unavailable|absent|not observed|did not look|didn.t look|assumed|presumed|offline only|not checked|no substrate'

# WHAT THIS CANNOT CATCH, said out loud: HEDGE only catches a PASS that CONFESSES, in words,
# that it could not look. A step that simply asserts something false -- "the twin forecasts and
# OpenBao trusts SPIRE JWKS" while OpenBao's jwt auth was dead -- has no hedge word in it and
# grades as honest here. Nothing at this level can detect a fabricated claim; only that step's own
# script, observing the fact rather than a config string, can. The structural rule below is the
# cheap second net: a step whose stdout says "could not look" ANYWHERE may not exit 0.
NOT_OBSERVED='NOT OBSERVED|could not look|was not observed'

names=(); verdicts=(); reasons=(); bad=0
STEPS="${E2E_STEPS_DIR:-$E2E_DIR}"   # overridden only by `verify-e2e-step7-honesty.sh selfcheck`

if [ "${1:-}" = selfcheck ]; then
  # The smallest thing that fails if the grading above breaks: plant one step of each shape and
  # require this script to catch exactly the four dishonest ones.
  t="$(mktemp -d)"; trap 'rm -rf "$t"' EXIT
  echo 'echo "PASS: all fine, though the cluster was unreachable"'   >"$t/verify-e2e-step1-hedged.sh"
  printf 'echo "SKIP: honest reason"\nexit 0\n'                      >"$t/verify-e2e-step2-mismatch.sh"
  printf 'echo done\nexit 2\n'                                       >"$t/verify-e2e-step3-nonconforming.sh"
  # step 4 deliberately absent
  printf 'echo "SKIP: honest reason"\nexit 3\n'                      >"$t/verify-e2e-step5-honest-skip.sh"
  printf 'echo "FAIL: observed false"\nexit 1\n'                     >"$t/verify-e2e-step6-honest-fail.sh"
  # ...and the structural net: a green whose own transcript confesses mid-run.
  printf 'echo "  SKIP (live tail): the mTLS reach was not observed"\necho "PASS: mTLS holds"\nexit 0\n' \
                                                                     >"$t/verify-e2e-step4-buried-confession.sh"
  out="$(E2E_STEPS_DIR="$t" bash "$E2E_DIR/$(basename "${BASH_SOURCE[0]}")" 2>&1)"; rc=$?
  ok=1
  [ "$rc" -eq 1 ] || { echo "selfcheck: expected exit 1, got $rc"; ok=0; }
  for want in "PASS that names something it could not look at" \
              "disagrees with its last line" \
              "could not look' line in its own output" \
              "not PASS:/FAIL:/SKIP:" \
              "4 step(s) cannot be graded honestly"; do
    printf '%s' "$out" | grep -qF -- "$want" || { echo "selfcheck: did not catch '$want'"; ok=0; }
  done
  printf '%s' "$out" | grep -qE '^  5 .*SKIP' || { echo "selfcheck: an honest SKIP was not graded SKIP"; ok=0; }
  printf '%s' "$out" | grep -qE '^  6 .*FAIL' || { echo "selfcheck: an honest FAIL was not graded FAIL"; ok=0; }
  [ "$ok" -eq 1 ] || { printf '%s\n' "$out"; fail "step 7's own grading is broken"; }
  pass "selfcheck: a hedged PASS, an exit/last-line mismatch, a non-conforming step and a green whose own transcript confesses mid-run are each caught; an honest SKIP and an honest FAIL are not"
fi

# The selfcheck is what proves this script's grading still bites. Nothing ran it: the gate calls
# this script with no argument and the only other references were a comment and the README
# (review, 2026-08-28). Run it here, once, the way verify-schedules.sh runs schedules.py selfcheck.
if [ -z "${E2E_STEPS_DIR:-}" ]; then
  bash "$E2E_DIR/$(basename "${BASH_SOURCE[0]}")" selfcheck >/dev/null 2>&1 \
    || fail "step 7's own selfcheck did not bite -- the grading below cannot be trusted"
fi

for n in 1 2 3 4 5 6; do
  s=$(ls "$STEPS"/verify-e2e-step$n-*.sh 2>/dev/null | head -1)
  if [ -z "$s" ]; then
    names+=("(missing)"); verdicts+=("UNGRADED"); reasons+=("no verify-e2e-step$n-*.sh exists")
    bad=$((bad+1)); continue
  fi
  nm="$(basename "$s" .sh)"; nm="${nm#verify-e2e-step$n-}"; names+=("${nm//-/ }")
  out="$(timeout 300 bash "$s" 2>/dev/null)"; rc=$?
  last="$(printf '%s' "$out" | tail -1)"
  case "$rc/$last" in
    124/*)          verdicts+=("UNGRADED"); reasons+=("hung: no verdict inside 300s"); bad=$((bad+1));;
    0/PASS:*)
      if printf '%s' "$last" | grep -qiE "$HEDGE"; then
        verdicts+=("UNGRADED"); reasons+=("PASS that names something it could not look at: ${last#PASS: }")
        bad=$((bad+1))
      elif printf '%s' "$out" | grep -qE "$NOT_OBSERVED"; then
        # The structural net: the confession is in the transcript, not on the verdict line.
        verdicts+=("UNGRADED")
        reasons+=("exit 0 with a 'could not look' line in its own output: $(printf '%s' "$out" | grep -E "$NOT_OBSERVED" | head -1)")
        bad=$((bad+1))
      else
        verdicts+=("PASS"); reasons+=("${last#PASS: }")
      fi;;
    3/SKIP:*)       verdicts+=("SKIP"); reasons+=("${last#SKIP: }");;
    0/*|3/*)        verdicts+=("UNGRADED"); reasons+=("exit $rc disagrees with its last line: $last"); bad=$((bad+1));;
    */FAIL:*)       verdicts+=("FAIL"); reasons+=("${last#FAIL: }");;
    *)              verdicts+=("UNGRADED"); reasons+=("exit $rc, last line not PASS:/FAIL:/SKIP: -- $last"); bad=$((bad+1));;
  esac
done

if [ "$bad" -eq 0 ]; then self=PASS; selfwhy="steps 1-6 each report one honest verdict"
else self=FAIL; selfwhy="$bad step(s) cannot be graded honestly"; fi
names+=("honesty"); verdicts+=("$self"); reasons+=("$selfwhy")

echo
printf '  %-3s %-26s %-9s %s\n' "#" "step (NORTH-STAR 4)" "verdict" "why"
printf '  %-3s %-26s %-9s %s\n' "---" "--------------------------" "---------" "---"
for i in 0 1 2 3 4 5 6; do
  why="${reasons[$i]}"; [ ${#why} -le 96 ] || why="${why:0:93}..."
  printf '  %-3s %-26s %-9s %s\n' "$((i+1))" "${names[$i]:0:26}" "${verdicts[$i]}" "$why"
done
echo

[ "$bad" -eq 0 ] || fail "$selfwhy"
pass "$selfwhy (verdicts: $(printf '%s ' "${verdicts[@]}" | sed 's/ $//'))"
