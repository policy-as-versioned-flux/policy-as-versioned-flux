#!/usr/bin/env bash
# The sampler waits for the webhooks BEFORE it applies the composed set (eco-system ticket 81;
# ticket 60 rounds 2 and 3). OFFLINE: it reads three checked-out workflow files.
#
# Round 2 (2026-09-01, PRs driftwood #22, tuppence #14, ludlow #12) meant to move the kyverno
# rollout wait above the composed apply. Its second string replace hit the FIRST occurrence of
# the kyverno line -- the one the edit had just inserted -- so the executed order stayed:
# ResourceSet waits (empty: nothing applied yet), flux-operator wait, composed apply, kyverno
# wait, Kustomization waits. tuppence and ludlow kept recording 16 of 16 rendered objects absent
# (runs 33558854558, 33558858820); driftwood passed by the luck of a 3-minute timeout. Nothing
# graded the order, so the mis-order shipped quietly. This check grades it.
#
# For each adopter's .github/workflows/drift-sample.yml it finds six lines, each required exactly
# once (a duplicate is how round 2 went wrong), and requires them in this order:
#   1 the kyverno admission-controller rollout wait
#   2 the flux-operator rollout wait
#   3 kubectl apply -k gitops/composed/
#   4 the Kustomization Ready waits
#   5 the ResourceSet Ready waits
#   6 the five-fact sample step
# Comment lines are ignored, so the prose above a step cannot satisfy or break the check.
#
# Exit 0 all three adopters in order; 1 a marker missing, duplicated or out of order; 3 the
# estate clone is not here. It grades the CHECKOUT the gate reads: until round 3 is merged on an
# adopter's main and pulled, that adopter is red here, which is the truth.
#
#   verify-sampler-wait-order.sh            selfcheck first, then grade the three checkouts
#   verify-sampler-wait-order.sh selfcheck  selfcheck only: the right order passes; round 2's
#                                           order, a duplicated wait and a missing wait fail
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ESTATE="${SAMPLER_ESTATE:-$ROOT/.estate-clone}"   # overridden only by the selfcheck
UNITS="driftwood tuppence ludlow"
WORKFLOW=".github/workflows/drift-sample.yml"
bad=0
ok()   { printf '  ok   %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; bad=$((bad+1)); }

# The six markers, in the order the workflow must execute them.
NAMES=( "kyverno wait" "flux-operator wait" "composed apply" "Kustomization waits" "ResourceSet waits" "five-fact sample" )
PATS=(
  'rollout status deploy/kyverno-admission-controller'
  'rollout status deploy/flux-operator'
  'apply -k gitops/composed/'
  'get kustomizations\.kustomize\.toolkit\.fluxcd\.io'
  'get resourcesets\.fluxcd\.controlplane\.io'
  '- name: take the five-fact sample'
)

# grade <unit> <file>: prints ok/FAIL lines, counts failures in $bad.
grade() {
  local unit="$1" f="$2" i n prev=0 prevname="top" order="" lines before=$bad
  [ -f "$f" ] || { fail "$unit: $f is missing"; return; }
  for i in "${!PATS[@]}"; do
    # line numbers of non-comment lines matching the marker
    lines="$(grep -nE -- "${PATS[$i]}" "$f" | grep -vE '^[0-9]+:[[:space:]]*#' | cut -d: -f1 | tr '\n' ' ')"
    lines="${lines% }"
    n=$(printf '%s' "$lines" | wc -w | tr -d ' ')
    if [ "$n" -eq 0 ]; then fail "$unit: no ${NAMES[$i]} line (${PATS[$i]})"; continue; fi
    if [ "$n" -gt 1 ]; then fail "$unit: ${NAMES[$i]} appears $n times (lines $lines); round 2's bug was a duplicate"; continue; fi
    if [ "$lines" -le "$prev" ]; then fail "$unit: ${NAMES[$i]} (line $lines) sits above the $prevname (line $prev)"; fi
    prev="$lines"; prevname="${NAMES[$i]}"; order="$order ${NAMES[$i]}@$lines"
  done
  [ "$bad" -eq "$before" ] && ok "$unit:${order}"
}

selfcheck() {
  local t me good=1 u
  t="$(mktemp -d)"
  me="$ROOT/verify/sampler-wait-order/$(basename "${BASH_SOURCE[0]}")"
  # Six fixture lines, shaped like the real workflow's; the selfcheck rearranges them.
  local K='          kubectl --context "${CTX}" -n kyverno rollout status deploy/kyverno-admission-controller --timeout=180s || true'
  local F='          kubectl --context "${CTX}" -n flux-system rollout status deploy/flux-operator --timeout=180s || true'
  local A='          kubectl --context "${CTX}" apply -k gitops/composed/'
  local Z='          for k in $(kubectl --context "${CTX}" -n flux-system get kustomizations.kustomize.toolkit.fluxcd.io -o name 2>/dev/null); do'
  local R='          for r in $(kubectl --context "${CTX}" -n flux-system get resourcesets.fluxcd.controlplane.io -o name 2>/dev/null); do'
  local S='      - name: take the five-fact sample and append it to the observation log'
  local C='          # comment that mentions apply -k gitops/composed/ and rollout status deploy/kyverno-admission-controller'
  write() { # write <estate-dir> <lines...>: the same workflow for all three units
    local d="$1"; shift
    for u in $UNITS; do mkdir -p "$d/$u/.github/workflows"; printf '%s\n' "$@" >"$d/$u/$WORKFLOW"; done
  }
  write "$t/round3"   "$C" "$K" "$F" "$A" "$Z" "$R" "$S"     # round 3: the order the ticket asserts
  write "$t/round2"   "$R" "$F" "$A" "$K" "$Z" "$S"          # round 2 as merged: kyverno below the apply
  write "$t/dup"      "$K" "$F" "$A" "$K" "$Z" "$R" "$S"     # the kyverno wait twice (round 2's replace bug)
  write "$t/missing"  "$F" "$A" "$Z" "$R" "$S"               # no kyverno wait at all
  SAMPLER_ESTATE="$t/round3"  bash "$me" >/dev/null 2>&1 || { echo "selfcheck: the round-3 order failed"; good=0; }
  SAMPLER_ESTATE="$t/round2"  bash "$me" >/dev/null 2>&1 && { echo "selfcheck: round 2's order passed"; good=0; }
  SAMPLER_ESTATE="$t/dup"     bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a duplicated kyverno wait passed"; good=0; }
  SAMPLER_ESTATE="$t/missing" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a missing kyverno wait passed"; good=0; }
  SAMPLER_ESTATE="$t/nowhere" bash "$me" >/dev/null 2>&1; [ $? -eq 3 ] || { echo "selfcheck: an absent estate did not exit 3"; good=0; }
  rm -rf "$t"
  if [ "$good" = 1 ]; then echo "  ok   selfcheck: round 3 passes; round 2, a duplicate and a missing wait fail; no clone skips"; return 0; fi
  echo "FAIL: selfcheck: the grader does not grade"; return 1
}

if [ "${1:-}" = selfcheck ]; then
  selfcheck || exit 1
  echo "PASS: selfcheck: round 3's order passes; round 2's order, a duplicated wait and a missing wait fail; an absent clone skips"; exit 0
fi
if [ -z "${SAMPLER_ESTATE:-}" ]; then
  echo "0. the grader can fail"
  selfcheck || exit 1
fi

for u in $UNITS; do
  [ -d "$ESTATE/$u" ] || { echo "SKIP: $ESTATE/$u is not here (run clone-estate.sh)"; exit 3; }
done

echo "1. each adopter's drift-sample.yml waits for kyverno and flux-operator, applies, then waits for the applied set"
for u in $UNITS; do grade "$u" "$ESTATE/$u/$WORKFLOW"; done

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: driftwood, tuppence and ludlow each wait for the webhooks before applying the composed set, then wait for what they applied (round 3 order)"
  exit 0
fi
echo "FAIL: $bad wait-order fact(s) false in a checked-out drift-sample.yml (ticket 81): the sampler would race the webhooks again"
exit 1
