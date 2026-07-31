#!/usr/bin/env bash
# Idempotent bring-up of the human/device ACCESS plane onto the EXISTING
# driftwood cluster: Pomerium Core (IAP) + Dex (estate OIDC) + the device SVID
# on the ticket-14 SPIRE root. Re-runnable at a venue. Never creates/deletes a
# cluster; every reconcile timeout-bounded so a slow pull just means "re-run".
#
# Prereqs: driftwood cluster + Flux (estate/driftwood/scripts/up.sh) AND the
# ticket-14 identity substrate (estate/platform/identity/up.sh) — this plane
# rides that SPIRE root; it does not stand up its own.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
KAPPLY() { kubectl --context "$CTX" apply -f "$@"; }
RECON()  { timeout 300 flux --context "$CTX" reconcile helmrelease -n "$1" "$2" || \
             echo "  (reconcile of $2 not finished within timeout — safe to re-run up.sh)"; }
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

for c in kubectl flux; do command -v "$c" >/dev/null || { echo "MISSING cli: $c" >&2; exit 1; }; done
kubectl --context "$CTX" version >/dev/null 2>&1 || { echo "driftwood not reachable ($CTX); run estate/driftwood/scripts/up.sh first" >&2; exit 1; }
kubectl --context "$CTX" get ns spire-system >/dev/null 2>&1 || { echo "identity substrate missing; run estate/platform/identity/up.sh first" >&2; exit 1; }

say "namespace: access"
KAPPLY "$HERE/namespaces.yaml"

say "Dex — estate OIDC issuer (human login, same root as the gitsign committer)"
KAPPLY "$HERE/oidc/dex-helmrelease.yaml"
RECON access dex

say "Pomerium Core — IAP in front of the kube-apiserver (OIDC + WebAuthn + device gate)"
KAPPLY "$HERE/pomerium/helmrelease.yaml"
RECON access pomerium

say "device SVID on the acme.internal root (spire-controller-manager reconciles it)"
KAPPLY "$HERE/device/device-svid.yaml" || echo "  (SPIRE CRDs not ready — re-run up.sh)"

# The tpm_devid node attestor is a values OVERLAY for ticket 14's `spire`
# HelmRelease (can't be a second release — would collide). Applied by merging
# device/spire-tpm-devid-values.yaml into that release's values and reconciling.
# Kept manual because it edits another ticket's release; do it once per venue.
say "tpm_devid attestor: MERGE device/spire-tpm-devid-values.yaml into"
echo "    estate/platform/identity/spire/helmrelease.yaml (spec.values), then:"
echo "    flux --context $CTX reconcile helmrelease -n spire-system spire"
echo "    (needs a real/virtual TPM on the EUD — see device/secure-enclave.md)"

say "decision engine selfcheck (the graded human/device gate)"
python3 "$HERE/access.py" selfcheck

say "done. verify with estate/platform/access/verify-access.sh"
