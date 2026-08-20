#!/usr/bin/env bash
# Assert the identity substrate holds together. Two layers:
#   OFFLINE (always) — every manifest parses, and the load-bearing wiring is
#     present: SPIRE is Istio's CA, mTLS is STRICT, authz matches SPIFFE
#     principals, OpenBao's jwt auth points at SPIRE's OIDC JWKS, and the
#     SPIRE agent socket is exposed for Envoy's SDS.
#   LIVE (only if the substrate is already up) — SPIRE/istiod/openbao pods
#     exist and ping reaches pong over SPIFFE mTLS. Bounded; skipped otherwise.
# Exits non-zero if any invariant the talk relies on is broken.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
fail() { echo "FAIL: $*" >&2; exit 1; }

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

# SPIRE stood up, with controller-manager + oidc + csi enabled.
spire = find("HelmRelease", "spire")
check(bool(spire), "SPIRE HelmRelease present")
v = spire[0]["spec"]["values"] if spire else {}
check(v.get("spire-server", {}).get("controllerManager", {}).get("enabled") is True,
      "spire-controller-manager enabled (renders ClusterSPIFFEID -> entries)")
check(v.get("spiffe-oidc-discovery-provider", {}).get("enabled") is True,
      "SPIRE OIDC Discovery Provider enabled (JWKS for OpenBao)")
check(v.get("spiffe-csi-driver", {}).get("enabled") is True,
      "spiffe-csi-driver enabled (mounts agent socket into meshed pods)")
td = v.get("global", {}).get("spire", {}).get("trustDomain")
check(td == "acme.internal", f"trust domain is the one estate root (acme.internal), got {td!r}")
agent_sock = v.get("spire-agent", {}).get("socketPath", "")
check(agent_sock.startswith("/run/spire/agent-sockets/"), f"agent socket exposed for Envoy SDS ({agent_sock})")

# Istio consumes SPIRE identity, not its own CA. NOTE: global.caName is a no-op
# on Istio 1.24 (only ever consulted for GkeWorkloadCertificate) — asserting it
# equals "SPIRE" passed regardless of how the mesh was actually wired. What
# really makes SPIRE the mesh CA: istiod's own CA server is switched off, and
# sidecar injection mounts the SPIRE workload socket at Envoy's well-known SDS
# path (see istio/helmrelease.yaml and https://istio.io/latest/docs/ops/integrations/spire/).
istiod = find("HelmRelease", "istiod")
check(bool(istiod), "istiod HelmRelease present")
iv = istiod[0]["spec"]["values"] if istiod else {}
check(iv.get("pilot", {}).get("env", {}).get("ENABLE_CA_SERVER") == "false",
      "istiod's own CA server is disabled (ENABLE_CA_SERVER: false) — istiod cannot mint certs itself")
spire_tmpl = iv.get("sidecarInjectorWebhook", {}).get("templates", {}).get("spire", "")
check("csi.spiffe.io" in spire_tmpl and "/run/secrets/workload-spiffe-uds" in spire_tmpl,
      "sidecar injection mounts the SPIRE workload socket at Envoy's SDS default path (this, not caName, makes SPIRE the mesh CA)")

# STRICT mesh mTLS.
pa = find("PeerAuthentication", "default")
check(bool(pa) and pa[0]["spec"]["mtls"]["mode"] == "STRICT", "mesh-wide PeerAuthentication STRICT")

# Base identity template + authz on SPIFFE principals.
csid = find("ClusterSPIFFEID", "mesh-base")
check(bool(csid), "base ClusterSPIFFEID present")
tmpl = csid[0]["spec"]["spiffeIDTemplate"] if csid else ""
check("spiffe://" in tmpl and "TrustDomain" in tmpl, "SVID template derives a spiffe:// path from pod/ns/sa")
ap = find("AuthorizationPolicy", "pong-allow-ping")
check(bool(ap), "AuthorizationPolicy present")
prin = ap[0]["spec"]["rules"][0]["from"][0]["source"]["principals"] if ap else []
check(any(p.startswith("spiffe://acme.internal/") for p in prin),
      f"authz admits by SPIFFE principal, not IP ({prin})")

# OpenBao running + jwt auth wired to SPIRE OIDC (the secret-plane seam).
check(bool(find("HelmRelease", "openbao")), "OpenBao HelmRelease present")
job = find("Job", "openbao-jwt-setup")
check(bool(job), "OpenBao jwt-auth setup Job present")
args = "".join(job[0]["spec"]["template"]["spec"]["containers"][0].get("args", [])) if job else ""
check("oidc_discovery_url" in args and "spire-spiffe-oidc-discovery-provider" in args,
      "OpenBao jwt auth points at SPIRE's OIDC Discovery Provider JWKS")

if fails:
    sys.exit(f"\n{len(fails)} invariant(s) broken")
print("  -- all offline invariants hold --")
PY

# Bonus: kubectl client-side schema check on core kinds (no cluster mutation).
if command -v kubectl >/dev/null; then
  echo "== offline: kubectl dry-run (core kinds) =="
  kubectl apply --dry-run=client -f "$HERE/namespaces.yaml" >/dev/null && echo "  ok   namespaces dry-run" || echo "  (dry-run needs a reachable cluster; skipped)"
fi

# LIVE proof — only if the substrate is already up; strictly bounded, never hangs.
if command -v kubectl >/dev/null && timeout 10 kubectl --context "$CTX" get ns spire-system >/dev/null 2>&1; then
  echo "== live: substrate + mTLS proof =="
  timeout 20 kubectl --context "$CTX" -n spire-system get pods 2>/dev/null | grep -q spire && echo "  ok   SPIRE pods present" || fail "SPIRE pods not present"
  timeout 20 kubectl --context "$CTX" -n istio-system get deploy istiod >/dev/null 2>&1 && echo "  ok   istiod present" || fail "istiod not present"
  timeout 20 kubectl --context "$CTX" -n openbao get pods 2>/dev/null | grep -q openbao && echo "  ok   OpenBao present" || fail "OpenBao not present"
  # ping -> pong must succeed over mTLS (ping is the allowed SPIFFE principal).
  P=$(timeout 20 kubectl --context "$CTX" -n mesh-demo get pod -l app=ping -o name 2>/dev/null | head -1)
  if [ -n "$P" ]; then
    timeout 20 kubectl --context "$CTX" -n mesh-demo exec "$P" -c ping -- curl -sS -o /dev/null -w '%{http_code}' pong.mesh-demo/ 2>/dev/null | grep -q 200 \
      && echo "  ok   ping -> pong over SPIFFE mTLS (200)" || fail "ping -> pong over SPIFFE mTLS did not return 200"
  fi
else
  echo "== live checks skipped (substrate not up; run up.sh on the driftwood cluster) =="
fi
echo "verify-identity: done"
