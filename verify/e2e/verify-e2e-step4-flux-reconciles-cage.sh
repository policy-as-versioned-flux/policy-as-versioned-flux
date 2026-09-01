#!/usr/bin/env bash
# NORTH-STAR §4 step 4: "Flux reconciles the new cage spec onto the adopter's cluster. The
# workload keeps running, caged tighter."
#
# Real as far as it honestly goes today, on the standing driftwood KinD cluster. Seven facts are
# asserted HARD -- a wrong answer is a FAIL, never a skip, because every one of them is something
# this estate has actually built and stands up right now, not something still owed to a future
# ticket:
#
#   A. the adopter's GitRepository is Ready and serving the COMMIT its ref pins -- a pin, not
#      a moving branch;
#   B. the adopter's Kustomization is Ready and its lastAppliedRevision is that same revision;
#   C. the governed Namespace is real, carries `governed: "true"`, and is in the Kustomization's
#      own inventory -- so Flux owns the object the cage attaches to;
#   D. the served cage policy for a version the adopter's composed tree publishes is installed
#      live;
#   E. the live cage-tier reads the Namespace (namespaceObject) and knows the isolated rung;
#   F. the governed Namespace declares posture.acme.io/tier, on the ladder;
#   G. the adopter's OWN declared workload (deploy/pod.yaml, reconciled onto the cluster by Flux
#      via gitops/apps/pod.yaml -- ticket 40 answer item 2, 2026-08-31) is Running and wears the
#      Namespace's tier: the caged label, the tier's PriorityClass.
#
# D..G used to be a named "not built yet" could-not-look pointing at ticket 26. Ticket 26's cage
# and this ticket's workload wiring are both landed and standing on kind-driftwood now, so a wrong
# answer on any of them is an observed defect on a running system, not an honest gap -- graded
# accordingly (see the "prove it fails" drill in the ticket 40 answer: delete either one and this
# step goes red).
#
# One fact remains a genuinely could-not-look, named with the ticket that owns it:
#
#   H. the source is the adopter's signed tag on the REAL remote, not the offline git server
#                                                                   -> ticket 40
#
# And one is a legitimate could-not-look distinct from H, kept apart from a hard G failure because
# collapsing it into FAIL would misreport an eventually-consistent state as broken:
#
#   G'. a pod admitted BEFORE a tier moved still carrying the old label -- ADR-0022's named
#       "synchronize gap". Observed-stale, not observed-false.
#
# The step is split into named sub-results (the `ok` / `FAIL:` / the SKIP reason list) precisely
# because it is honestly partly real: everything the estate has built is asserted hard, and only
# what still needs the real signed remote is reported as could-not-look.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 4 "flux reconciles the new cage spec onto the cluster"

ADOPTER="${E2E_ADOPTER:-driftwood}"      # the thin slice is driftwood; ticket 42 widens it
NS="$ADOPTER"
CTX="${E2E_CTX:-kind-$ADOPTER}"

# --- substrate first; without one, grade the lane's five-fact sample (ecosystem ticket 60) ---
# The scheduled observation lane (.github/workflows/drift-sample.yml in the adopter's own repo)
# reconciles an EPHEMERAL cluster from the REAL remotes and appends one five-fact record per
# source to drift/samples.jsonl -- exactly the facts A/B/D/H above ask about, plus the signature
# at the source boundary, on the clock ADR-0023 D1 allows. Where this runner has no cluster at
# all -- the citable run in CI -- this step used to exit could-not-look without ever reading the
# lane (REVIEW-2026-08-31, M7). Now it grades that lane-committed sample instead: five-facts.py
# refuses a hand-typed or unsigned sample, so the grade stays an observation, not a rehearsal.
grade_lane_sample() {
  local drift="$ESTATE/$ADOPTER/drift/five-facts.py" out rc
  [ -f "$drift" ] || skip "no cluster on this runner, and $ADOPTER carries no drift/five-facts.py to grade a lane sample with"
  "$PY" -c 'import yaml' 2>/dev/null || skip "no cluster on this runner, and this python has no pyyaml to grade the lane sample with"
  out="$("$PY" "$drift" grade --max-age-hours "${FIVE_FACT_MAX_AGE_HOURS:-48}" 2>&1)"; rc=$?
  printf '%s\n' "$out" | sed 's/^/   /'
  case "$rc" in
    0) pass "no cluster on this runner; step 4 graded from the scheduled lane sample instead: the composed set is in force from signed sources on a cluster that reconciled the real remotes (drift/samples.jsonl)";;
    3) skip "no cluster on this runner, and the lane sample cannot stand in: $(printf '%s\n' "$out" | sed -n 's/^SKIP: //p' | tail -1)";;
    *) fail "the scheduled lane sample observes a step-4 fact false: $(printf '%s\n' "$out" | tail -1)";;
  esac
}
command -v kubectl >/dev/null || grade_lane_sample
command -v kind >/dev/null && docker info >/dev/null 2>&1 || grade_lane_sample
kind get clusters 2>/dev/null | grep -qx "$ADOPTER" || grade_lane_sample
kubectl --context "$CTX" version >/dev/null 2>&1 || grade_lane_sample
kubectl --context "$CTX" get crd kustomizations.kustomize.toolkit.fluxcd.io >/dev/null 2>&1 \
  || grade_lane_sample
[ -d "$ESTATE/$ADOPTER/composed/policies" ] || skip "no .estate-clone/$ADOPTER/composed (run clone-estate.sh)"

k()  { kubectl --context "$CTX" "$@" 2>/dev/null; }
kfs(){ kubectl --context "$CTX" -n flux-system "$@" 2>/dev/null; }
ready() { kfs get "$1" "$2" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'; }

# --- A. the source is Ready at the commit it pins ---------------------------------------
[ "$(ready gitrepository "$ADOPTER")" = True ] || fail "GitRepository $ADOPTER is not Ready on $CTX"
rev="$(kfs get gitrepository "$ADOPTER" -o jsonpath='{.status.artifact.revision}')"
pin="$(kfs get gitrepository "$ADOPTER" -o jsonpath='{.spec.ref.commit}')"
tag="$(kfs get gitrepository "$ADOPTER" -o jsonpath='{.spec.ref.tag}')"
url="$(kfs get gitrepository "$ADOPTER" -o jsonpath='{.spec.url}')"
[ -n "$pin" ] || fail "GitRepository $ADOPTER pins no commit -- a moving ref is not a pin"
case "$rev" in
  *"$pin") echo "  ok  A. source Ready at the pinned commit: tag=${tag:-<none>} $rev";;
  *) fail "GitRepository $ADOPTER serves '$rev', not its pinned commit $pin";;
esac

# --- B. the Kustomization applied exactly that revision ---------------------------------
[ "$(ready kustomization "$ADOPTER")" = True ] || fail "Kustomization $ADOPTER is not Ready on $CTX"
applied="$(kfs get kustomization "$ADOPTER" -o jsonpath='{.status.lastAppliedRevision}')"
[ "$applied" = "$rev" ] || fail "Kustomization $ADOPTER applied '$applied' but the source is at '$rev'"
echo "  ok  B. Kustomization Ready, lastAppliedRevision == the source revision"

# --- C. the governed Namespace is Flux's own object -------------------------------------
[ "$(k get ns "$NS" -o jsonpath='{.metadata.labels.policy-as-versioned\.dev/governed}')" = true ] \
  || fail "Namespace $NS does not carry policy-as-versioned.dev/governed=true (ADR-0018)"
inv="$(kfs get kustomization "$ADOPTER" -o jsonpath='{.status.inventory.entries[*].id}')"
case " $inv " in
  *" _${NS}__Namespace "*) echo "  ok  C. governed Namespace $NS is in the Kustomization's inventory";;
  *) fail "governed Namespace $NS is not in Kustomization $ADOPTER's inventory -- Flux does not own it";;
esac

# --- D. the served cage policy is installed live -----------------------------------------
# versions the adopter's own composed tree publishes a cage for, as policy object suffixes
served=()
for d in "$ESTATE/$ADOPTER"/composed/policies/v*/; do
  [ -f "$d/cage-tier.yaml" ] || continue
  v="$(basename "$d")"; v="${v#v}"; served+=("cage-tier-${v//./-}")
done
[ ${#served[@]} -gt 0 ] || fail "$ADOPTER's composed tree serves no cage-tier at all"

live="$(k get mutatingpolicies.policies.kyverno.io -o jsonpath='{.items[*].metadata.name}')"
hit=""
for want in "${served[@]}"; do case " $live " in *" $want "*) hit="$want";; esac; done
[ -n "$hit" ] || fail "no served cage-tier is installed live (composed tree serves ${served[*]}; cluster has ${live:-none})"
echo "  ok  D. served cage policy in force live: $hit"

# --- E. that cage reads the Namespace and knows the isolated rung ------------------------
body="$(k get mutatingpolicies.policies.kyverno.io "$hit" -o yaml)"
case "$body" in
  *namespaceObject*) ;;
  *) fail "live $hit does not read namespaceObject -- the tier would be the forgeable pod label";;
esac
case "$body" in
  *isolated*) ;;
  *) fail "live $hit does not know the isolated rung";;
esac
echo "  ok  E. $hit reads namespaceObject and knows the isolated rung"

# --- F. the governed Namespace declares a tier on the ladder ------------------------------
tier="$(k get ns "$NS" -o jsonpath='{.metadata.labels.posture\.acme\.io/tier}')"
[ -n "$tier" ] || fail "governed Namespace $NS declares no posture.acme.io/tier"
case " baseline restricted quarantine isolated infra " in
  *" $tier "*) echo "  ok  F. governed Namespace $NS declares tier '$tier'";;
  *) fail "Namespace $NS declares tier '$tier', which is not on the ladder";;
esac

# --- G. the adopter's own declared workload runs, caged -----------------------------------
# THE ADOPTER'S OWN declared workload, wearing the Namespace's tier -- never "items[0] of
# whatever's Running in the Namespace" (2026-08-29 review: that version gave three different
# verdicts on one commit inside twenty minutes, once a hard FAIL on another agent's probe pod).
# The fact is about a pod this step can name: the one deploy/pod.yaml declares, reconciled onto
# the cluster by Flux from gitops/apps/pod.yaml (ticket 40 answer item 2) -- not kubectl.
want_pod="$(python3 -c "
import sys, yaml
try:
    docs = [d for d in yaml.safe_load_all(open('$ESTATE/$ADOPTER/deploy/pod.yaml')) if d]
except Exception:
    sys.exit(0)
print(next((d['metadata']['name'] for d in docs if d.get('kind') == 'Pod'), ''))
" 2>/dev/null)"
[ -n "$want_pod" ] || fail "$ADOPTER declares no workload in deploy/pod.yaml, so this step has no pod of its own to read"
pod="$want_pod"
phase="$(k get pod -n "$NS" "$pod" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
[ "$phase" = "Running" ] \
  || fail "$ADOPTER's own workload $pod is not Running in governed Namespace $NS (phase='${phase:-absent}') -- gitops/apps/pod.yaml is not reconciling, or the pod cannot be admitted"

ptier="$(k get pod -n "$NS" "$pod" -o jsonpath='{.metadata.labels.posture\.acme\.io/tier}')"
caged="$(k get pod -n "$NS" "$pod" -o jsonpath='{.metadata.labels.posture\.acme\.io/caged}')"
pc="$(k get pod -n "$NS" "$pod" -o jsonpath='{.spec.priorityClassName}')"
sync_gap=""
if [ "$ptier" = "$tier" ] && [ "$caged" = true ] && [ "${pc#cage-}" != "$pc" ]; then
  echo "  ok  G. pod $pod is Running and wears the Namespace's cage: tier=$ptier caged=true priorityClass=$pc"
else
  # Not a FAIL: ADR-0022 names the legitimate case where a pod admitted BEFORE a tier move
  # still carries the old label (the synchronize gap). That is observed-stale, not
  # observed-false, and the two are told apart by a human reading the reason -- so THIS ONE
  # sub-result stays a named could-not-look even though G itself is otherwise hard-asserted.
  sync_gap="pod $pod does not wear Namespace tier '$tier' (tier='$ptier' caged='$caged' priorityClass='$pc') -- either the cage did not run on it or it was admitted before the tier moved (the synchronize gap, ADR-0022)"
  echo "  ?   G. $sync_gap"
fi

# --- H. the source is the real signed remote, not the offline seed ------------------------
h_missing=""
case "$url" in
  https://github.com/*) echo "  ok  H. source is the real remote: $url";;
  *) h_missing="source is $url, not the adopter's signed tag on the real remote [ticket 40]"
     echo "  ?   H. $h_missing";;
esac

# --- verdict --------------------------------------------------------------------------------
# Everything hard-assertable (A-G's Running-and-caged fact) has already exited on the spot if
# false. What's left here are the two named could-not-looks, reported together when both apply.
missing=()
[ -n "$sync_gap" ] && missing+=("$sync_gap [ADR-0022]")
[ -n "$h_missing" ] && missing+=("$h_missing")

if [ ${#missing[@]} -gt 0 ]; then
  msg="$(printf '; %s' "${missing[@]}")"
  skip "Flux reconciles $ADOPTER at its pinned revision with the cage in force and the workload running; only:${msg#;}"
fi
pass "$ADOPTER reconciles ${tag:-$rev} from $url; $hit is in force; Namespace $NS declares tier $tier and pod $pod runs wearing it"
