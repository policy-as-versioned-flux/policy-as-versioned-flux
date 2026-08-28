#!/usr/bin/env bash
# NORTH-STAR §4 step 4: "Flux reconciles the new cage spec onto the adopter's cluster. The
# workload keeps running, caged tighter."
#
# Real as far as it honestly goes today, on the standing driftwood KinD cluster. Three facts
# are asserted hard (a wrong answer is a FAIL, never a skip):
#
#   A. the adopter's GitRepository is Ready and serving the COMMIT its ref pins -- a pin, not
#      a moving branch;
#   B. the adopter's Kustomization is Ready and its lastAppliedRevision is that same revision;
#   C. the governed Namespace is real, carries `governed: "true"`, and is in the Kustomization's
#      own inventory -- so Flux owns the object the cage attaches to.
#
# Then four facts are looked for and, when a piece is not there yet, NAMED with the ticket that
# owns it and the step exits 3. It never asserts the pre-ladder shape to get a green:
#
#   D. the served cage policy for a version the adopter's composed tree publishes is installed
#      live                                                        -> ticket 26
#   E. the live cage-tier reads the Namespace (namespaceObject) and knows the isolated rung
#                                                                   -> ticket 26
#   F. the governed Namespace declares posture.acme.io/tier         -> ticket 26
#   G. a pod in the governed Namespace is Running and carries that Namespace's tier, the caged
#      label and the tier's PriorityClass                           -> ticket 26 (its live
#      defect 1: the priority admission collision means no pod can be created in a caged
#      Namespace at all today)
#   H. the source is the adopter's signed tag on the REAL remote, not the offline git server
#                                                                   -> ticket 40
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 4 "flux reconciles the new cage spec onto the cluster"

ADOPTER="${E2E_ADOPTER:-driftwood}"      # the thin slice is driftwood; ticket 42 widens it
NS="$ADOPTER"
CTX="${E2E_CTX:-kind-$ADOPTER}"

# --- substrate first, or could-not-look -------------------------------------------------
command -v kubectl >/dev/null || skip "kubectl absent"
command -v kind >/dev/null && docker info >/dev/null 2>&1 || skip "substrate absent (kind/docker)"
kind get clusters 2>/dev/null | grep -qx "$ADOPTER" || skip "KinD cluster '$ADOPTER' absent"
kubectl --context "$CTX" version >/dev/null 2>&1 || skip "cluster $CTX unreachable"
kubectl --context "$CTX" get crd kustomizations.kustomize.toolkit.fluxcd.io >/dev/null 2>&1 \
  || skip "Flux CRDs absent on $CTX (nothing reconciles there)"
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
  *"$pin") echo "  ok  source Ready at the pinned commit: tag=${tag:-<none>} $rev";;
  *) fail "GitRepository $ADOPTER serves '$rev', not its pinned commit $pin";;
esac

# --- B. the Kustomization applied exactly that revision ---------------------------------
[ "$(ready kustomization "$ADOPTER")" = True ] || fail "Kustomization $ADOPTER is not Ready on $CTX"
applied="$(kfs get kustomization "$ADOPTER" -o jsonpath='{.status.lastAppliedRevision}')"
[ "$applied" = "$rev" ] || fail "Kustomization $ADOPTER applied '$applied' but the source is at '$rev'"
echo "  ok  Kustomization Ready, lastAppliedRevision == the source revision"

# --- C. the governed Namespace is Flux's own object -------------------------------------
[ "$(k get ns "$NS" -o jsonpath='{.metadata.labels.policy-as-versioned\.dev/governed}')" = true ] \
  || fail "Namespace $NS does not carry policy-as-versioned.dev/governed=true (ADR-0018)"
inv="$(kfs get kustomization "$ADOPTER" -o jsonpath='{.status.inventory.entries[*].id}')"
case " $inv " in
  *" _${NS}__Namespace "*) echo "  ok  governed Namespace $NS is in the Kustomization's inventory";;
  *) fail "governed Namespace $NS is not in Kustomization $ADOPTER's inventory -- Flux does not own it";;
esac

# --- D..H. what is not in force yet, each named with its ticket --------------------------
missing=()

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
if [ -z "$hit" ]; then
  missing+=("no served cage-tier is installed live (composed tree serves ${served[*]}; cluster has ${live:-none}) [ticket 26]")
else
  echo "  ok  served cage policy in force live: $hit"
  body="$(k get mutatingpolicies.policies.kyverno.io "$hit" -o yaml)"
  case "$body" in *namespaceObject*) ;; *) missing+=("live $hit does not read namespaceObject -- the tier is still the forgeable pod label [ticket 26]");; esac
  case "$body" in *isolated*) ;; *) missing+=("live $hit does not know the isolated rung [ticket 26]");; esac
fi

tier="$(k get ns "$NS" -o jsonpath='{.metadata.labels.posture\.acme\.io/tier}')"
if [ -z "$tier" ]; then
  missing+=("governed Namespace $NS declares no posture.acme.io/tier [ticket 26]")
else
  case " baseline restricted quarantine isolated infra " in
    *" $tier "*) echo "  ok  governed Namespace $NS declares tier '$tier'";;
    *) fail "Namespace $NS declares tier '$tier', which is not on the ladder";;
  esac
fi

# the workload keeps running, caged tighter: a Running pod wearing the Namespace's tier.
pod="$(k get pods -n "$NS" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')"
if [ -z "$pod" ]; then
  missing+=("no Running pod in governed Namespace $NS to carry the cage [ticket 26, live defect 1]")
elif [ -n "$tier" ]; then
  ptier="$(k get pod -n "$NS" "$pod" -o jsonpath='{.metadata.labels.posture\.acme\.io/tier}')"
  caged="$(k get pod -n "$NS" "$pod" -o jsonpath='{.metadata.labels.posture\.acme\.io/caged}')"
  pc="$(k get pod -n "$NS" "$pod" -o jsonpath='{.spec.priorityClassName}')"
  if [ "$ptier" = "$tier" ] && [ "$caged" = true ] && [ "${pc#cage-}" != "$pc" ]; then
    echo "  ok  pod $pod is Running and wears the Namespace's cage: tier=$ptier caged=true priorityClass=$pc"
  else
    fail "pod $pod does not wear Namespace tier '$tier' (tier='$ptier' caged='$caged' priorityClass='$pc')"
  fi
fi

case "$url" in
  https://github.com/*) echo "  ok  source is the real remote: $url";;
  *) missing+=("source is $url, not the adopter's signed tag on the real remote [ticket 40]");;
esac

if [ ${#missing[@]} -gt 0 ]; then
  msg="$(printf '; %s' "${missing[@]}")"
  skip "Flux reconciles $ADOPTER at its pinned revision, but the cage is not in force:${msg#;}"
fi
pass "$ADOPTER reconciles ${tag:-$rev} from $url; $hit is in force; Namespace $NS declares tier $tier and pod $pod runs wearing it"
