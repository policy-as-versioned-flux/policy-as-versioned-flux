#!/usr/bin/env bash
# The sampler waits for the webhooks BEFORE it applies the composed set, and then waits for the
# objects THAT APPLY CREATED -- including the ones a ResourceSet generates, which do not exist at
# the moment the apply returns (eco-system tickets 81 and 107; ticket 60 rounds 2, 3 and 4).
# OFFLINE: it reads three checked-out workflow files.
#
# Three rounds got this wrong, twice in the same way. Round 2 (2026-09-01, PRs driftwood #22,
# tuppence #14, ludlow #12) meant to move the kyverno rollout wait above the composed apply; its
# second string replace hit the FIRST occurrence of the kyverno line -- the one the edit had just
# inserted -- so the executed order stayed: ResourceSet waits (empty: nothing applied yet),
# flux-operator wait, composed apply, kyverno wait, Kustomization waits. Round 3 (2026-09-04) fixed
# the webhook half and left the second half mis-ordered: it enumerated
# `get kustomizations -o name` BEFORE waiting for the ResourceSet, so the enumeration ran while
# composed-v2-0-0, composed-v2-0-1 and composed-v3-0-0 -- the Kustomizations the ResourceSet
# generates, which apply the fifteen policies -- did not exist yet. It found only the adopter's own
# already-Ready Kustomization and returned in ~0.3s, and the sample was taken the instant the
# composed Kustomizations were created: fifteen policies live and byte-equal for fact 4, in no
# inventory for fact 5, on every scheduled sample from 2026-09-05 to 2026-09-08.
#
# THE FAILURE MODE THIS CHECK EXISTS TO REFUSE, in one sentence: a wait that asks its question
# before the answer can exist and takes the silence for a yes. An enumeration of a resource type
# that finds nothing is silence, not a yes, so it may not sit above the thing that creates what it
# would have enumerated.
#
# Round 4's order, which is what this grades. For each adopter's
# .github/workflows/drift-sample.yml it finds seven lines, each required exactly once (a duplicate
# is how round 2 went wrong), and requires them strictly in this order:
#   1 the kyverno admission-controller rollout wait
#   2 the flux-operator rollout wait
#   3 kubectl apply -k gitops/composed/
#   4 the ResourceSet Ready waits            (get resourcesets... -o name)
#   5 the composed Kustomizations NAMED off the ResourceSet's own status inventory
#                                            (get resourcesets... -o json)
#   6 the Kustomization Ready waits          (get kustomizations... -o name), now below 4 and 5,
#                                            so the enumeration runs when its answers can exist
#   7 the five-fact sample step
# Comment lines are ignored, so the prose above a step cannot satisfy or break the check.
#
# Marker 5 is what makes marker 6 honest. Swapping 4 and 6 alone would still leave a bare
# enumeration deciding when the sample is taken; marker 5 requires the workflow to derive the
# names from the object that created them, so "found nothing" is a list it can see is empty rather
# than a loop that quietly does not run.
#
# Exit 0 all three adopters in order; 1 a marker missing, duplicated or out of order; 3 the
# estate clone is not here. It grades the CHECKOUT the gate reads: until round 4 is merged on an
# adopter's main and pulled, that adopter is red here, which is the truth.
#
#   verify-sampler-wait-order.sh            selfcheck first, then grade the three checkouts
#   verify-sampler-wait-order.sh selfcheck  selfcheck only: round 4's order passes; round 3's
#                                           order, round 2's order, the derivation below the
#                                           enumeration, a duplicated wait and a missing wait fail
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ESTATE="${SAMPLER_ESTATE:-$ROOT/.estate-clone}"   # overridden only by the selfcheck
UNITS="driftwood tuppence ludlow"
WORKFLOW=".github/workflows/drift-sample.yml"
bad=0
ok()   { printf '  ok   %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; bad=$((bad+1)); }

# The seven markers, in the order the workflow must execute them.
NAMES=( "kyverno wait" "flux-operator wait" "composed apply" "ResourceSet waits" "composed names derived" "Kustomization waits" "five-fact sample" )
PATS=(
  'rollout status deploy/kyverno-admission-controller'
  'rollout status deploy/flux-operator'
  'apply -k gitops/composed/'
  'get resourcesets\.fluxcd\.controlplane\.io -o name'
  'get resourcesets\.fluxcd\.controlplane\.io -o json'
  'get kustomizations\.kustomize\.toolkit\.fluxcd\.io'
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
  # Seven fixture lines, shaped like the real workflow's; the selfcheck rearranges them. K, F, A,
  # Z and S are copied from round 3 as it shipped, verbatim, so the round-3 fixture below is the
  # order that was actually on all three adopters' main between 2026-09-04 and this change.
  local K='          kubectl --context "${CTX}" -n kyverno rollout status deploy/kyverno-admission-controller --timeout=180s || true'
  local F='          kubectl --context "${CTX}" -n flux-system rollout status deploy/flux-operator --timeout=180s || true'
  local A='          kubectl --context "${CTX}" apply -k gitops/composed/'
  local Z='          for k in $(kubectl --context "${CTX}" -n flux-system get kustomizations.kustomize.toolkit.fluxcd.io -o name 2>/dev/null); do'
  local R='          for r in $(kubectl --context "${CTX}" -n flux-system get resourcesets.fluxcd.controlplane.io -o name 2>/dev/null); do'
  local J='            composed="$(kubectl --context "${CTX}" -n flux-system get resourcesets.fluxcd.controlplane.io -o json 2>/dev/null | python3 -c "${composed_names}" 2>/dev/null)"'
  local S='      - name: take the five-fact sample and append it to the observation log'
  local C='          # comment that mentions apply -k gitops/composed/ and rollout status deploy/kyverno-admission-controller'
  write() { # write <estate-dir> <lines...>: the same workflow for all three units
    local d="$1"; shift
    for u in $UNITS; do mkdir -p "$d/$u/.github/workflows"; printf '%s\n' "$@" >"$d/$u/$WORKFLOW"; done
  }
  write "$t/round4"   "$C" "$K" "$F" "$A" "$R" "$J" "$Z" "$S"  # round 4: the order this check asserts
  write "$t/round3"   "$C" "$K" "$F" "$A" "$Z" "$R" "$S"       # round 3 as merged 2026-09-04: enumerate, THEN the ResourceSet
  write "$t/round2"   "$R" "$F" "$A" "$K" "$Z" "$S"            # round 2 as merged: kyverno below the apply
  write "$t/late"     "$C" "$K" "$F" "$A" "$R" "$Z" "$J" "$S"  # the derivation added, but below the bare enumeration
  write "$t/dup"      "$C" "$K" "$F" "$A" "$K" "$R" "$J" "$Z" "$S"  # the kyverno wait twice (round 2's replace bug)
  write "$t/missing"  "$F" "$A" "$R" "$J" "$Z" "$S"            # no kyverno wait at all
  SAMPLER_ESTATE="$t/round4"  bash "$me" >/dev/null 2>&1 || { echo "selfcheck: the round-4 order failed"; good=0; }
  SAMPLER_ESTATE="$t/round3"  bash "$me" >/dev/null 2>&1 && { echo "selfcheck: round 3's order passed"; good=0; }
  SAMPLER_ESTATE="$t/round2"  bash "$me" >/dev/null 2>&1 && { echo "selfcheck: round 2's order passed"; good=0; }
  SAMPLER_ESTATE="$t/late"    bash "$me" >/dev/null 2>&1 && { echo "selfcheck: the derivation below the bare enumeration passed"; good=0; }
  SAMPLER_ESTATE="$t/dup"     bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a duplicated kyverno wait passed"; good=0; }
  SAMPLER_ESTATE="$t/missing" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a missing kyverno wait passed"; good=0; }
  SAMPLER_ESTATE="$t/nowhere" bash "$me" >/dev/null 2>&1; [ $? -eq 3 ] || { echo "selfcheck: an absent estate did not exit 3"; good=0; }
  rm -rf "$t"
  if [ "$good" = 1 ]; then echo "  ok   selfcheck: round 4 passes; round 3, round 2, a late derivation, a duplicate and a missing wait fail; no clone skips"; return 0; fi
  echo "FAIL: selfcheck: the grader does not grade"; return 1
}

if [ "${1:-}" = selfcheck ]; then
  selfcheck || exit 1
  echo "PASS: selfcheck: round 4's order passes; round 3's order, round 2's order, a derivation below the bare enumeration, a duplicated wait and a missing wait fail; an absent clone skips"; exit 0
fi
if [ -z "${SAMPLER_ESTATE:-}" ]; then
  echo "0. the grader can fail"
  selfcheck || exit 1
fi

for u in $UNITS; do
  [ -d "$ESTATE/$u" ] || { echo "SKIP: $ESTATE/$u is not here (run clone-estate.sh)"; exit 3; }
done

echo "1. each adopter's drift-sample.yml waits for kyverno and flux-operator, applies, then waits for what that apply created -- the ResourceSet, the Kustomizations it names, and only then the rest"
for u in $UNITS; do grade "$u" "$ESTATE/$u/$WORKFLOW"; done

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: driftwood, tuppence and ludlow each wait for the webhooks before applying the composed set, then wait for the ResourceSet and for the Kustomizations it names before enumerating anything (round 4 order)"
  exit 0
fi
echo "FAIL: $bad wait-order fact(s) false in a checked-out drift-sample.yml (tickets 81, 107): the sampler would ask before the answer could exist and read the silence as a yes"
exit 1
