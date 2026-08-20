#!/usr/bin/env bash
# Idempotent bring-up of the admission + fleet engine (Kyverno + flux-operator)
# onto the EXISTING driftwood KinD cluster, delivered as Flux HelmReleases —
# the same five-HelmRelease pattern as spire/istio/openbao/pomerium/dex.
# Re-runnable at a venue. Never creates/deletes a cluster.
#
# Run this BEFORE estate/platform/posture/up.sh — the posture MutatingPolicy /
# ValidatingPolicy objects need Kyverno's CRDs to exist first.
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

say "Kyverno (admission engine — ValidatingPolicy/MutatingPolicy CRDs)"
KAPPLY "$HERE/kyverno/helmrelease.yaml"
RECON kyverno kyverno

say "flux-operator (fleet layer — ResourceSet CRD; no FluxInstance, existing Flux install untouched)"
KAPPLY "$HERE/flux-operator/helmrelease.yaml"
RECON flux-system flux-operator

say "done. verify with estate/platform/engine/verify-engine.sh"
