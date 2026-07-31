#!/usr/bin/env bash
# Idempotent, OFFLINE-safe bring-up of the two EUDs' local prep. Never boots a
# VM, never waits on Windows/Linux install (GUI/ISO-gated, can't run headless),
# never touches a live cluster beyond a best-effort apply if the SVID
# fingerprint has already been filled in. Re-runnable at a venue.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

say "preparing disks + swtpm state dirs for both EUDs (offline)"
"$HERE/build-vm.sh"

say "device SVID templates (fill in the real tpm_devid fingerprint after live attestation)"
for eud in windows11-eud linux-eud; do
  out="$HERE/vms/${eud}-device-svid.yaml"
  "$HERE/tpm-devid-enroll.sh" "$eud" > "$out"
  echo "  wrote $out"
done

if command -v kubectl >/dev/null 2>&1 && timeout 10 kubectl --context "$CTX" get ns spire-system >/dev/null 2>&1; then
  say "spire-system reachable — applying device SVID templates (fingerprints still placeholders until attested)"
  kubectl --context "$CTX" apply -f "$HERE/vms/windows11-eud-device-svid.yaml" -f "$HERE/vms/linux-eud-device-svid.yaml" \
    || echo "  (SPIRE CRDs not ready — re-run up.sh)"
else
  echo "  (driftwood/spire-system not reachable — templates written, not applied; run estate/platform/identity/up.sh + estate/platform/access/up.sh first)"
fi

say "VENUE STEPS (human, hardware-gated — see README.md + windows-hello-for-business.md):"
echo "  1. boot each VM with the command build-vm.sh printed (or import into UTM's GUI, enable TPM)"
echo "  2. install the OS; enrol WHfB (Windows) / confirm the vTPM (Linux, tpm2_getekcertificate)"
echo "  3. run the SPIRE agent on the guest with the tpm_devid attestor; read the fingerprint off the server log"
echo "  4. tpm-devid-enroll.sh <eud> <fingerprint> | kubectl apply -f -   # replaces the placeholder entry"
echo "  5. access.py decide break-glass --oidc --webauthn --device       # now ALLOW"

say "done. verify with estate/platform/eud/verify-eud.sh"
