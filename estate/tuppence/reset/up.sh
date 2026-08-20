#!/usr/bin/env bash
# Idempotent bring-up of the workload flagship (ticket 17) onto the EXISTING
# cluster that already runs the identity substrate (SPIRE + Istio + OpenBao) and
# the posture projection (ticket 15). Never creates/deletes/waits on a cluster —
# a slow reconcile just means "re-run up.sh".
#
# Prereqs (run these first, they install what this depends on):
#   estate/platform/identity/up.sh   — SPIRE + Istio + OpenBao + jwt seam
#   estate/platform/posture/up.sh    — stamp-posture + trust-boundary + posture ClusterSPIFFEID
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

command -v kubectl >/dev/null || { echo "MISSING cli: kubectl" >&2; exit 1; }
kubectl --context "$CTX" version >/dev/null 2>&1 || { echo "cluster not reachable ($CTX); run the identity substrate up first" >&2; exit 1; }

say "customer-accounts-reset + current/stale callers (meshed, posture-managed)"
kubectl --context "$CTX" apply -f "$HERE/workloads.yaml"

say "reach gate: Istio AuthorizationPolicy on the current-posture prefix"
kubectl --context "$CTX" apply -f "$HERE/authorizationpolicy.yaml" \
  || echo "  (Istio CRDs not ready — re-run up.sh once istiod is up)"

say "peer SAN override: expect the real posture-shaped SVID, not Istio's ns/sa default"
kubectl --context "$CTX" apply -f "$HERE/destinationrule.yaml" \
  || echo "  (Istio CRDs not ready — re-run up.sh once istiod is up)"

say "secret gate: OpenBao jwt role bound to the current-posture prefix"
kubectl --context "$CTX" apply -f "$HERE/openbao-role.yaml" \
  || echo "  (openbao namespace not ready — re-run up.sh)"

say "done. verify with estate/tuppence/reset/verify-reach-secrets.sh"
