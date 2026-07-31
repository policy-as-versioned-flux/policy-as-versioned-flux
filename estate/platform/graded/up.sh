#!/usr/bin/env bash
# Idempotent bring-up of the graded enforcement envelope onto the EXISTING
# driftwood KinD cluster: the eviction PriorityClasses, the cage-tier MutatingPolicy,
# and the cage-netpol GeneratingPolicy. Requires Kyverno already installed
# (estate/platform/distribution path). Never creates/deletes/waits on a cluster.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

command -v kubectl >/dev/null || { echo "MISSING cli: kubectl" >&2; exit 1; }
kubectl --context "$CTX" version >/dev/null 2>&1 || {
  echo "driftwood cluster not reachable ($CTX); run estate/driftwood/scripts/up.sh first" >&2; exit 1; }

say "eviction PriorityClasses (cage-baseline / cage-restricted / cage-quarantine)"
kubectl --context "$CTX" apply -f "$HERE/policies/priorityclasses.yaml"

say "cage-tier MutatingPolicy (behind-posture pod -> its cage, by degree)"
kubectl --context "$CTX" apply -f "$HERE/policies/cage-tier.yaml" \
  || echo "  (Kyverno MutatingPolicy CRD not ready — install Kyverno, then re-run up.sh)"

say "cage-netpol GeneratingPolicy (caged pod -> egress-lockdown NetworkPolicy)"
kubectl --context "$CTX" apply -f "$HERE/policies/cage-netpol.yaml" \
  || echo "  (Kyverno GeneratingPolicy CRD not ready — install Kyverno, then re-run up.sh)"

say "done. verify with estate/platform/graded/verify-graded.sh"
