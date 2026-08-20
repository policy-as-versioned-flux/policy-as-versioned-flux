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

# Istio consumes SPIRE identity for WORKLOADS, but istiod still needs its own
# CA server to mint its control-plane/webhook serving cert (ticket 04). NOTE:
# global.caName is a no-op on Istio 1.24 (only ever consulted for
# GkeWorkloadCertificate) — it must stay deleted, not asserted. What actually
# makes SPIRE the mesh CA for workloads: sidecar injection mounts the SPIRE
# workload socket at Envoy's well-known SDS path (see istio/helmrelease.yaml
# and https://istio.io/latest/docs/ops/integrations/spire/).
istiod = find("HelmRelease", "istiod")
check(bool(istiod), "istiod HelmRelease present")
iv = istiod[0]["spec"]["values"] if istiod else {}
check("caName" not in iv.get("global", {}),
      "global.caName is absent (it's a no-op on Istio 1.24 and must not be reintroduced)")
check(iv.get("pilot", {}).get("env", {}).get("ENABLE_CA_SERVER") != "false",
      "istiod's own CA server is NOT disabled — it must mint its own webhook serving cert "
      "(ENABLE_CA_SERVER: false was the ticket-04 bug: no CA bundle ever loads, webhook fails "
      "\"tls: internal error\")")
check(iv.get("meshConfig", {}).get("trustDomain") == "acme.internal",
      "meshConfig.trustDomain matches SPIRE's trust domain (acme.internal, not the cluster.local default)")
spire_tmpl = iv.get("sidecarInjectorWebhook", {}).get("templates", {}).get("spire", "")
check("csi.spiffe.io" in spire_tmpl and "/run/secrets/workload-spiffe-uds" in spire_tmpl,
      "sidecar injection mounts the SPIRE workload socket at Envoy's SDS default path (this, not caName, makes SPIRE the mesh CA)")
check("spiffe.io/spire-managed-identity" in spire_tmpl,
      "spire injection template carries the spiffe.io/spire-managed-identity label block")

# STRICT mesh mTLS.
pa = find("PeerAuthentication", "default")
check(bool(pa) and pa[0]["spec"]["mtls"]["mode"] == "STRICT", "mesh-wide PeerAuthentication STRICT")

# Base identity template + authz on SPIFFE principals.
csid = find("ClusterSPIFFEID", "mesh-base")
check(bool(csid), "base ClusterSPIFFEID present")
tmpl = csid[0]["spec"]["spiffeIDTemplate"] if csid else ""
check("spiffe://" in tmpl and "TrustDomain" in tmpl, "SVID template derives a spiffe:// path from pod/ns/sa")
# ticket 11 (live-discovered): the spire chart scopes its controller-manager
# to className "<release-namespace>-<release-name>" and runs with "handle
# crs without class name: false" — a ClusterSPIFFEID with no className is
# never reconciled at all (no error, .status.stats stays empty forever).
# Confirmed live: this object minted zero registration entries since it was
# first applied; the chart's own same-shaped fallback CSID
# (<release>-default) was producing the base-identity SVIDs the estate had
# been crediting to this file.
check(csid[0]["spec"].get("className") not in (None, ""),
      "className set, so spire-controller-manager actually reconciles this object")
ap = find("AuthorizationPolicy", "pong-allow-ping")
check(bool(ap), "AuthorizationPolicy present")
prin = ap[0]["spec"]["rules"][0]["from"][0]["source"]["principals"] if ap else []
# Scheme-less: Istio's AuthorizationPolicy takes "<trustDomain>/ns/<ns>/sa/<sa>"
# and prepends "spiffe://" itself when building the Envoy RBAC matcher — a
# "spiffe://"-prefixed value here double-prefixes to an unmatchable principal
# (ticket 04/11 finding; https://istio.io/latest/docs/reference/config/security/authorization-policy/).
check(any(p.startswith("acme.internal/") for p in prin),
      f"authz admits by SPIFFE principal, not IP ({prin})")
check(not any(p.startswith("spiffe://") for p in prin),
      f"authz principal is scheme-less, not double-prefixed ({prin})")

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
# NOTE: every check below captures kubectl's output into a variable first,
# THEN greps/heads the variable — never `kubectl ... | grep -q ...` directly.
# `grep -q`/`head -N` exit as soon as they see a match/line, SIGPIPEing the
# still-writing kubectl on the other end of the pipe; under `pipefail` that
# turns a PASSING check into a coin-flip FAIL (found live, debugging this
# ticket's own new checks — a real, if minor, instance of the ticket-01 bug
# class: a gate whose failure meant nothing).
if command -v kubectl >/dev/null && timeout 10 kubectl --context "$CTX" get ns spire-system >/dev/null 2>&1; then
  echo "== live: substrate + mTLS proof =="
  OUT=$(timeout 20 kubectl --context "$CTX" -n spire-system get pods 2>/dev/null)
  echo "$OUT" | grep -q spire && echo "  ok   SPIRE pods present" || fail "SPIRE pods not present"

  # istiod comes up: not merely present (it ran 1/1 the whole time ticket 04's
  # bug was live) but with an available replica.
  AVAIL=$(timeout 20 kubectl --context "$CTX" -n istio-system get deploy istiod \
    -o jsonpath='{.status.availableReplicas}' 2>/dev/null)
  echo "$AVAIL" | grep -qE '^[1-9]' && echo "  ok   istiod has an available replica" || fail "istiod has no available replica"

  # the webhook serves: its caBundle must be populated. This is exactly what
  # ENABLE_CA_SERVER: false left empty ("Failed to load CA bundle: could not
  # decode pem" -> the webhook patch controller never wrote a caBundle here).
  CABUNDLE_LEN=$(timeout 20 kubectl --context "$CTX" get mutatingwebhookconfiguration istio-sidecar-injector \
    -o jsonpath='{.webhooks[0].clientConfig.caBundle}' 2>/dev/null | wc -c | tr -d ' ')
  [ "${CABUNDLE_LEN:-0}" -gt 100 ] && echo "  ok   sidecar-injector webhook has a populated caBundle (serves)" \
    || fail "sidecar-injector webhook caBundle is empty — it is not serving"

  OUT=$(timeout 20 kubectl --context "$CTX" -n openbao get pods 2>/dev/null)
  echo "$OUT" | grep -q openbao && echo "  ok   OpenBao present" || fail "OpenBao not present"

  # a meshed pod schedules with a real SPIFFE SVID: the webhook must actually
  # have injected istio-proxy (2/2, not admission-only), and that proxy's own
  # workload cert must carry a spiffe://acme.internal/... SAN.
  PODS=$(timeout 20 kubectl --context "$CTX" -n mesh-demo get pod -l app=ping -o name 2>/dev/null)
  P=$(echo "$PODS" | head -1)
  if [ -n "$P" ]; then
    READY=$(timeout 20 kubectl --context "$CTX" -n mesh-demo get "$P" -o jsonpath='{.status.containerStatuses[?(@.name=="istio-proxy")].ready}' 2>/dev/null)
    [ "$READY" = "true" ] && echo "  ok   ping's istio-proxy sidecar is injected and Ready" \
      || fail "ping has no Ready istio-proxy sidecar — webhook did not inject"
    CERTS=$(timeout 20 kubectl --context "$CTX" -n mesh-demo exec "$P" -c istio-proxy -- pilot-agent request GET certs 2>/dev/null)
    echo "$CERTS" | grep -q 'spiffe://acme\.internal/ns/mesh-demo/sa/ping' && echo "  ok   ping's proxy holds a real SVID (spiffe://acme.internal/ns/mesh-demo/sa/ping)" \
      || fail "ping's proxy has no spiffe://acme.internal SVID"
    # ticket 04 found, ticket 11 fixed: authorizationpolicy.yaml's `principals`
    # is now scheme-less (see the offline check above), so Istio's own
    # "spiffe://" prepend renders a matchable principal and this call reaches.
    CODE=$(timeout 20 kubectl --context "$CTX" -n mesh-demo exec "$P" -c ping -- curl -sS -o /dev/null -w '%{http_code}' pong.mesh-demo/ 2>/dev/null)
    echo "$CODE" | grep -q 200 && echo "  ok   ping -> pong over SPIFFE mTLS (200)" || fail "ping -> pong over SPIFFE mTLS did not return 200"
  fi
else
  echo "== live checks skipped (substrate not up; run up.sh on the driftwood cluster) =="
fi
echo "verify-identity: done"
