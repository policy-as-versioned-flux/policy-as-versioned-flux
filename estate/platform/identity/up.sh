#!/usr/bin/env bash
# Idempotent bring-up of the identity substrate (SPIRE + Istio + OpenBao) onto
# the EXISTING driftwood KinD cluster, delivered as inherited platform machinery
# via Flux HelmReleases. Re-runnable at a venue. Never creates/deletes a cluster.
#
# Drives everything through Flux's helm-controller (installed by driftwood/up.sh),
# so the HelmRelease YAML is the single source of truth — no duplicated helm flags.
# Every reconcile is `timeout`-bounded: nothing hangs; a slow image pull just
# means "re-run up.sh", it never blocks the tour.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
KAPPLY() { kubectl --context "$CTX" apply -f "$@"; }
RECON()  { timeout 300 flux --context "$CTX" reconcile helmrelease -n "$1" "$2" || \
             echo "  (reconcile of $2 not finished within timeout — safe to re-run up.sh)"; }
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

for c in kubectl flux; do command -v "$c" >/dev/null || { echo "MISSING cli: $c" >&2; exit 1; }; done
kubectl --context "$CTX" version >/dev/null 2>&1 || { echo "driftwood cluster not reachable ($CTX); run estate/driftwood/scripts/up.sh first" >&2; exit 1; }
flux check --context "$CTX" >/dev/null 2>&1 || { echo "Flux not installed on $CTX; run driftwood/up.sh first" >&2; exit 1; }

say "namespaces"
KAPPLY "$HERE/namespaces.yaml"

say "SPIRE (server + agent + controller-manager + csi + oidc)"
KAPPLY "$HERE/spire/helmrelease.yaml"
RECON spire-system spire-crds
RECON spire-system spire

say "Istio, consuming SPIRE identity (SPIRE Workload API socket integration)"
KAPPLY "$HERE/istio/helmrelease.yaml"
RECON istio-system istio-base
RECON istio-system istiod

say "OpenBao (dev-mode secret plane)"
KAPPLY "$HERE/openbao/helmrelease.yaml"
RECON openbao openbao

# CRD-dependent objects — apply after the charts have registered their CRDs.
# Best-effort: if a CRD isn't up yet, re-running up.sh applies these cleanly.
say "identity config: base ClusterSPIFFEID, STRICT mTLS, OpenBao jwt seam"
KAPPLY "$HERE/spire/clusterspiffeid-mesh.yaml" || echo "  (ClusterSPIFFEID CRD not ready — re-run up.sh)"
KAPPLY "$HERE/istio/peerauthentication-strict.yaml" || echo "  (Istio CRDs not ready — re-run up.sh)"
KAPPLY "$HERE/openbao/jwt-auth.yaml"

say "mTLS proof workloads (ping -> pong, SPIFFE AuthorizationPolicy)"
KAPPLY "$HERE/demo-mtls/workloads.yaml"
KAPPLY "$HERE/demo-mtls/authorizationpolicy.yaml" || echo "  (Istio CRDs not ready — re-run up.sh)"

say "done. verify with estate/platform/identity/verify-identity.sh"
