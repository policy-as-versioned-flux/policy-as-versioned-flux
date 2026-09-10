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
# inventory for fact 5. By 2026-09-09 all three adopters record fact 5 false on the schedule.
#
# THE FAILURE MODE THIS CHECK EXISTS TO REFUSE, in one sentence: a wait that asks its question
# before the answer can exist and takes the silence for a yes. An enumeration of a resource type
# that finds nothing is silence, not a yes, so it may not sit above the thing that creates what it
# would have enumerated -- and the names it derives must actually be waited for.
#
# WHAT THIS CHECK GRADES, EXACTLY, because a claim wider than the grep behind it is the defect
# this estate is about. It reads ONE file per adopter, `.github/workflows/drift-sample.yml`, as
# TEXT. It grades two things and nothing else:
#
#   A. THE TEXTUAL ORDER of seven markers, each required exactly once (a duplicate is how round 2
#      went wrong), each strictly below the last:
#        1 the kyverno admission-controller rollout wait
#        2 the flux-operator rollout wait
#        3 kubectl apply -k gitops/composed/
#        4 the ResourceSet Ready waits            (get resourcesets... -o name)
#        5 the composed Kustomizations NAMED off the ResourceSet's own status inventory
#                                                 (get resourcesets... -o json)
#        6 the Kustomization Ready waits          (get kustomizations... -o name), now below 4
#                                                 and 5, so the enumeration runs when its answers
#                                                 can exist
#        7 the five-fact sample step
#   B. CONTAINMENT: marker 6's line, with any trailing `#` comment stripped, must carry the
#      variable marker 5 assigns -- `${composed}`, `${composed:-...}` or the unbraced `$composed`.
#      Without this a workflow can derive the names, print that it is waiting for them, and wait
#      for none of them: round 3 restored with a log line asserting the opposite. Measured on the
#      real head files -- deleting the token, or moving it out of the loop's word list into a
#      trailing comment on the same line, each dropped the waits actually made from four to one
#      (the adopter's own) while the step still announced all three composed names.
#
#      WHAT RULE B DOES AND DOES NOT CLOSE, because a rule added to stop a check asserting a
#      property it does not derive must not itself do that. It greps ONE LINE for a token. It
#      closes the token being DELETED from that line, and the token being RELOCATED into a
#      trailing comment on it. It does NOT parse the loop's word list, so a mention of the token
#      ANYWHERE ELSE on that line still satisfies it -- an `echo` on the loop line, an assignment
#      to a variable nothing reads, an expansion redirected away, or the token inside single
#      quotes. Four forms, each measured passing. Grading the word list needs a shell parser and
#      is not what this is. The comment strip is `sed 's/#.*$//'`, which would also cut a `#`
#      inside a string: that direction of error is a FALSE RED on a workflow that waits
#      correctly, never a false green, which is the direction to be wrong in.
#
# WHAT IT DOES NOT GRADE, named because an undisclosed limit rots like any other claim. Each of
# these was PLANTED on all three adopters and passed the order rule; only the first is closed, by
# rule B:
#   * the token deleted from the enumeration line                       -- CLOSED by rule B
#   * the token moved into a trailing comment on that line              -- CLOSED by rule B
#   * the token present on that line but not in the loop's word list
#     (echo, unread assignment, redirected expansion, single quotes)    -- still passes: rule B
#                                                                          greps a line, it does
#                                                                          not parse shell
#   * `seq 1 30` cut to `seq 1 1`: the retry becomes a single look     -- still passes
#   * `--timeout=180s` set to `--timeout=0s`: the waits do not wait    -- still passes
#   * a marker inside a TRAILING comment on a code line: the comment
#     filter is anchored at line start, so only FULL-LINE comments are
#     ignored                                                          -- still passes
#   * the derivation hoisted into a function defined above and invoked
#     below the enumeration: text order and run order part company     -- still passes
#   * `if: false` on the step, or the step deleted from the job: this
#     reads no `if:` and no job structure                              -- still passes
#   * whether any of it runs, converges, or samples anything. This is a
#     grep of one file. It is necessary and it is not sufficient; the
#     estate's evidence is the adopter's own scheduled sample.
#
# Exit 0 all three adopters in order; 1 a marker missing, duplicated or out of order, or the
# enumeration not carrying the derived names; 3 the estate clone is not here. It grades the
# CHECKOUT the gate reads: until round 4 is merged on an adopter's main and pulled, that adopter
# is red here, which is the truth.
#
#   verify-sampler-wait-order.sh            selfcheck first, then grade the three checkouts
#   verify-sampler-wait-order.sh selfcheck  selfcheck only: round 4's order passes; round 3's
#                                           order, round 2's order, a derivation below the
#                                           enumeration, one computed and unused, one named only
#                                           in a trailing comment, a duplicated wait and a
#                                           missing wait fail
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
WAITS_IDX=5          # index of "Kustomization waits" in NAMES/PATS: rule B's subject
# `${composed}`, `${composed:-...}` and the unbraced `$composed` all wait for the derived names;
# `$composedfoo` is a different variable and does not match. Rejecting a form that waits correctly
# would be a red for a working workflow, so all three spellings are accepted.
DERIVED='\$\{composed[:}]|\$composed([^A-Za-z0-9_]|$)'

# grade <unit> <file>: prints ok/FAIL lines, counts failures in $bad.
grade() {
  local unit="$1" f="$2" i n prev=0 prevname="top" order="" lines before=$bad waitline=""
  [ -f "$f" ] || { fail "$unit: $f is missing"; return; }
  for i in "${!PATS[@]}"; do
    # line numbers of non-comment lines matching the marker
    lines="$(grep -nE -- "${PATS[$i]}" "$f" | grep -vE '^[0-9]+:[[:space:]]*#' | cut -d: -f1 | tr '\n' ' ')"
    lines="${lines% }"
    n=$(printf '%s' "$lines" | wc -w | tr -d ' ')
    if [ "$n" -eq 0 ]; then fail "$unit: no ${NAMES[$i]} line (${PATS[$i]})"; continue; fi
    if [ "$n" -gt 1 ]; then fail "$unit: ${NAMES[$i]} appears $n times (lines $lines); round 2's bug was a duplicate"; continue; fi
    if [ "$lines" -le "$prev" ]; then fail "$unit: ${NAMES[$i]} (line $lines) sits above the $prevname (line $prev)"; fi
    [ "$i" = "$WAITS_IDX" ] && waitline="$lines"
    prev="$lines"; prevname="${NAMES[$i]}"; order="$order ${NAMES[$i]}@$lines"
  done
  # Rule B: the enumeration must wait for the names marker 5 derived, not merely beside them.
  # The trailing comment is stripped FIRST: without that, moving the token off the word list and
  # into a comment on the same line satisfied this rule while the step waited for none of the
  # composed Kustomizations (measured on the real head files, 2026-09-10).
  if [ -n "$waitline" ]; then
    if sed -n "${waitline}p" "$f" | sed 's/#.*$//' | grep -qE -- "$DERIVED"; then
      order="$order +derived-names-waited"
    else
      fail "$unit: the ${NAMES[$WAITS_IDX]} (line $waitline) carry no \${composed} outside a comment: the names are derived and then never waited for, which is round 3 with a log line that says otherwise"
    fi
  fi
  [ "$bad" -eq "$before" ] && ok "$unit:${order}"
}

selfcheck() {
  local t me good=1 u
  t="$(mktemp -d)"
  me="$ROOT/verify/sampler-wait-order/$(basename "${BASH_SOURCE[0]}")"
  # Fixture lines shaped like the real workflow's; the selfcheck rearranges them. K, F, A, Z and
  # S are copied from round 3 as it shipped, VERBATIM, so the round-3 fixture below is the order
  # that was actually on all three adopters' main from 2026-09-04. Z4 is round 4's union loop.
  local K='          kubectl --context "${CTX}" -n kyverno rollout status deploy/kyverno-admission-controller --timeout=180s || true'
  local F='          kubectl --context "${CTX}" -n flux-system rollout status deploy/flux-operator --timeout=180s || true'
  local A='          kubectl --context "${CTX}" apply -k gitops/composed/'
  local Z='          for k in $(kubectl --context "${CTX}" -n flux-system get kustomizations.kustomize.toolkit.fluxcd.io -o name 2>/dev/null); do'
  local Z4='          for k in $( { printf '"'"'%s\n'"'"' ${composed}; kubectl --context "${CTX}" -n flux-system get kustomizations.kustomize.toolkit.fluxcd.io -o name 2>/dev/null; } | sed '"'"'/^$/d'"'"' | sort -u); do'
  # the token present on the line but only inside a trailing comment: the escape rule B's first
  # version left open, and the reason the strip above exists.
  local ZC='          for k in $( { kubectl --context "${CTX}" -n flux-system get kustomizations.kustomize.toolkit.fluxcd.io -o name 2>/dev/null; } | sed '"'"'/^$/d'"'"' | sort -u); do   # ${composed} handled above'
  local R='          for r in $(kubectl --context "${CTX}" -n flux-system get resourcesets.fluxcd.controlplane.io -o name 2>/dev/null); do'
  local J='            composed="$(kubectl --context "${CTX}" -n flux-system get resourcesets.fluxcd.controlplane.io -o json 2>/dev/null | python3 -c "${composed_names}")" || composed=""'
  local S='      - name: take the five-fact sample and append it to the observation log'
  local C='          # comment that mentions apply -k gitops/composed/ and rollout status deploy/kyverno-admission-controller'
  write() { # write <estate-dir> <lines...>: the same workflow for all three units
    local d="$1"; shift
    for u in $UNITS; do mkdir -p "$d/$u/.github/workflows"; printf '%s\n' "$@" >"$d/$u/$WORKFLOW"; done
  }
  write "$t/round4"   "$C" "$K" "$F" "$A" "$R" "$J" "$Z4" "$S"      # round 4: the order this check asserts
  write "$t/round3"   "$C" "$K" "$F" "$A" "$Z" "$R" "$S"            # round 3 as merged 2026-09-04: enumerate, THEN the ResourceSet
  write "$t/round2"   "$R" "$F" "$A" "$K" "$Z" "$S"                 # round 2 as merged: kyverno below the apply
  write "$t/late"     "$C" "$K" "$F" "$A" "$R" "$Z4" "$J" "$S"      # the derivation added, but below the enumeration
  write "$t/unused"   "$C" "$K" "$F" "$A" "$R" "$J" "$Z" "$S"       # round 4's ORDER, derived names never waited for (rule B)
  write "$t/unused-comment" "$C" "$K" "$F" "$A" "$R" "$J" "$ZC" "$S" # the token on the line, but only in a trailing comment (rule B's strip)
  write "$t/dup"      "$C" "$K" "$F" "$A" "$K" "$R" "$J" "$Z4" "$S" # the kyverno wait twice (round 2's replace bug)
  write "$t/missing"  "$F" "$A" "$R" "$J" "$Z4" "$S"                # no kyverno wait at all
  SAMPLER_ESTATE="$t/round4"  bash "$me" >/dev/null 2>&1 || { echo "selfcheck: the round-4 order failed"; good=0; }
  SAMPLER_ESTATE="$t/round3"  bash "$me" >/dev/null 2>&1 && { echo "selfcheck: round 3's order passed"; good=0; }
  SAMPLER_ESTATE="$t/round2"  bash "$me" >/dev/null 2>&1 && { echo "selfcheck: round 2's order passed"; good=0; }
  SAMPLER_ESTATE="$t/late"    bash "$me" >/dev/null 2>&1 && { echo "selfcheck: the derivation below the enumeration passed"; good=0; }
  SAMPLER_ESTATE="$t/unused"  bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a derivation that is computed and never waited for passed"; good=0; }
  SAMPLER_ESTATE="$t/unused-comment" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: the derived names mentioned only in a trailing comment passed"; good=0; }
  SAMPLER_ESTATE="$t/dup"     bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a duplicated kyverno wait passed"; good=0; }
  SAMPLER_ESTATE="$t/missing" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a missing kyverno wait passed"; good=0; }
  SAMPLER_ESTATE="$t/nowhere" bash "$me" >/dev/null 2>&1; [ $? -eq 3 ] || { echo "selfcheck: an absent estate did not exit 3"; good=0; }
  rm -rf "$t"
  if [ "$good" = 1 ]; then echo "  ok   selfcheck: round 4 passes; round 3, round 2, a late derivation, an unused derivation, one named only in a comment, a duplicate and a missing wait fail; no clone skips"; return 0; fi
  echo "FAIL: selfcheck: the grader does not grade"; return 1
}

if [ "${1:-}" = selfcheck ]; then
  selfcheck || exit 1
  echo "PASS: selfcheck: round 4's order passes; round 3's order, round 2's order, a derivation below the enumeration, a derivation computed and never waited for, one whose names are mentioned only in a trailing comment, a duplicated wait and a missing wait fail; an absent clone skips"; exit 0
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
  echo "PASS: driftwood, tuppence and ludlow each wait for the webhooks before applying the composed set, then wait for the ResourceSet and for the Kustomizations it names -- and wait for those names -- before enumerating anything (round 4 order)"
  exit 0
fi
echo "FAIL: $bad wait-order fact(s) false in a checked-out drift-sample.yml (tickets 81, 107): the sampler would ask before the answer could exist and read the silence as a yes"
exit 1
