#!/usr/bin/env bash
# Assert the human/device access plane holds together. Two layers:
#   OFFLINE (always) — the decision engine's asserts pass, every manifest parses,
#     and the load-bearing wiring is present: Pomerium fronts the kube-apiserver
#     with OIDC (Dex) + a WebAuthn device policy; Dex is the estate issuer; the
#     device SVID sits on the SAME acme.internal root as workloads; tpm_devid is
#     configured with manufacturer/EK trust anchors.
#   LIVE (only if the plane is already up) — Pomerium/Dex pods exist. Bounded.
# Exits non-zero if any invariant the talk relies on is broken.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"

echo "== offline: decision-engine asserts =="
python3 "$HERE/access.py" selfcheck

echo "== offline: structural invariants =="
python3 - "$HERE" <<'PY'
import sys, glob, os
try:
    import yaml
except ImportError:
    sys.exit("PyYAML not available; `pip install pyyaml` to run the offline check")
root = sys.argv[1]
docs = []
for f in glob.glob(os.path.join(root, "**", "*.yaml"), recursive=True):
    with open(f) as fh:
        for d in yaml.safe_load_all(fh):
            if d: docs.append((os.path.relpath(f, root), d))
assert docs, "no manifests parsed"

def find(kind, name=None):
    return [d for _, d in docs if d.get("kind") == kind and (name is None or d.get("metadata", {}).get("name") == name)]

fails = []
def check(cond, msg):
    if not cond: fails.append(msg)
    print(("  ok   " if cond else "  FAIL ") + msg)

# Dex is the estate OIDC issuer for HUMAN login.
dex = find("HelmRelease", "dex")
check(bool(dex), "Dex HelmRelease present (estate OIDC issuer)")
issuer = dex[0]["spec"]["values"]["config"]["issuer"] if dex else ""
check("dex" in issuer, f"Dex advertises an OIDC issuer URL ({issuer})")

# Pomerium fronts the kube-apiserver, consuming the SAME issuer + WebAuthn device.
pom = find("HelmRelease", "pomerium")
check(bool(pom), "Pomerium Core HelmRelease present (IAP)")
pv = pom[0]["spec"]["values"] if pom else {}
idp = pv.get("config", {}).get("idp", {})
check(idp.get("provider") == "oidc" and idp.get("url") == issuer,
      "Pomerium consumes the estate OIDC issuer (Dex) — one human root, not a bolt-on")
routes = pv.get("config", {}).get("routes", [])
kube = [r for r in routes if "kubernetes.default" in str(r.get("to", ""))]
check(bool(kube), "Pomerium has a route to the kube-apiserver (kubectl access)")
# The route policy demands an authenticated human AND a WebAuthn-approved device.
ppl = str(kube[0].get("policy", "")) if kube else ""
check("authenticated_user" in ppl, "route policy requires an authenticated human")
check("device" in ppl and "approved" in ppl,
      "route policy requires a WebAuthn-approved device (phishing-resistant)")
check(bool(pom) and any(d.get("name") == "dex" for d in pom[0]["spec"].get("dependsOn", [])),
      "Pomerium dependsOn Dex (issuer up before the proxy)")

# The DEVICE identity is on the SAME root as workloads — not a parallel system.
dev = find("ClusterStaticEntry", "operator-macbook-device")
check(bool(dev), "device SVID ClusterStaticEntry present")
sid = dev[0]["spec"]["spiffeID"] if dev else ""
check(sid.startswith("spiffe://acme.internal/"),
      f"device SVID on the ONE estate root (acme.internal), got {sid!r}")
check("/device/" in sid, "device SVID lives under /device/ (distinct actor class, same root)")
sels = dev[0]["spec"].get("selectors", []) if dev else []
check(any(str(s).startswith("tpm_devid:") for s in sels),
      "device entry pinned to a tpm_devid selector (this hardware only)")

# tpm_devid node attestor configured with manufacturer/EK trust anchors — the
# thing that makes the device signal hardware-rooted, not self-asserted.
tpm = [d for f, d in docs if "spire-tpm-devid-values" in f]
check(bool(tpm), "tpm_devid values overlay present")
blob = str(tpm[0]) if tpm else ""
check("tpm_devid" in blob and "devid_ca_path" in blob and "endorsement_ca_path" in blob,
      "tpm_devid verifies endorsement + DevID CA chains (proof-of-residency, not a label)")

if fails:
    sys.exit(f"\n{len(fails)} invariant(s) broken")
print("  -- all offline invariants hold --")
PY

# kubectl client-side schema check on the plain kinds (no cluster mutation).
if command -v kubectl >/dev/null; then
  echo "== offline: kubectl dry-run (namespace) =="
  kubectl apply --dry-run=client -f "$HERE/namespaces.yaml" >/dev/null 2>&1 && echo "  ok   namespace dry-run" || echo "  (dry-run needs a reachable cluster; skipped)"
fi

# LIVE — only if the plane is already up; strictly bounded, never hangs.
if command -v kubectl >/dev/null && timeout 10 kubectl --context "$CTX" get ns access >/dev/null 2>&1; then
  echo "== live: plane present =="
  timeout 20 kubectl --context "$CTX" -n access get pods 2>/dev/null | grep -q dex && echo "  ok   Dex present" || echo "  FAIL Dex"
  timeout 20 kubectl --context "$CTX" -n access get pods 2>/dev/null | grep -q pomerium && echo "  ok   Pomerium present" || echo "  FAIL Pomerium"
  echo "  (live WebAuthn + tpm_devid attestation need a human at the Secure Enclave / a (v)TPM — see device/secure-enclave.md)"
else
  echo "== live checks skipped (plane not up; run up.sh on the driftwood cluster) =="
fi
echo "verify-access: done"
