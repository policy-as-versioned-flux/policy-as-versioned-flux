#!/usr/bin/env bash
# Idempotent bring-up of the posture projection layer onto the EXISTING driftwood
# KinD cluster: the two Kyverno trust-boundary policies + the posture
# ClusterSPIFFEID. Requires the identity substrate (estate/platform/identity/up.sh)
# and Kyverno already installed. Never creates/deletes/waits on a cluster.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

command -v kubectl >/dev/null || { echo "MISSING cli: kubectl" >&2; exit 1; }
kubectl --context "$CTX" version >/dev/null 2>&1 || {
  echo "driftwood cluster not reachable ($CTX); run estate/driftwood/scripts/up.sh first" >&2; exit 1; }

say "Kyverno posture policies (stamp-posture mutate + posture-trust-boundary validate)"
kubectl --context "$CTX" apply -f "$HERE/policies/stamp-posture.yaml" \
  || echo "  (Kyverno MutatingPolicy CRD not ready — install Kyverno, then re-run up.sh)"
kubectl --context "$CTX" apply -f "$HERE/policies/posture-trust-boundary.yaml" \
  || echo "  (Kyverno ValidatingPolicy CRD not ready — install Kyverno, then re-run up.sh)"

say "posture ClusterSPIFFEID (bakes posture/<vN> into the SVID path)"
kubectl --context "$CTX" apply -f "$HERE/spire/clusterspiffeid-posture.yaml" \
  || echo "  (SPIRE ClusterSPIFFEID CRD not ready — run identity/up.sh first, then re-run up.sh)"

say "done. verify with estate/platform/posture/verify-posture-projection.sh"
