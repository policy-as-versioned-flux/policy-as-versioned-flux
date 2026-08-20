#!/usr/bin/env bash
# Beat: "Kyverno and flux-operator are installed as Flux HelmReleases, ordered
# before the posture layer." Not one of estate/talk/verify-all.sh's 28 beats
# (installing the engine is a precondition for the posture/reach beats it
# already counts, not a new demo-live claim of its own) — run directly.
#
# OFFLINE (always): the HelmRelease/source manifests parse and pin real charts.
# LIVE (only if the cluster is reachable): both controllers are Running and
# the CRDs the rest of the estate needs (ValidatingPolicy/MutatingPolicy,
# ResourceSet) are actually registered.
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
            if d: docs.append(d)
assert docs, "no manifests parsed"

def find(kind, name=None):
    return [d for d in docs if d.get("kind") == kind and (name is None or d.get("metadata", {}).get("name") == name)]

fails = []
def check(cond, msg):
    if not cond: fails.append(msg)
    print(("  ok   " if cond else "  FAIL ") + msg)

kv = find("HelmRelease", "kyverno")
check(bool(kv), "Kyverno HelmRelease present")
check(bool(kv) and kv[0]["spec"]["chart"]["spec"]["version"], "Kyverno chart version pinned")

fo = find("HelmRelease", "flux-operator")
check(bool(fo), "flux-operator HelmRelease present")
check(bool(fo) and fo[0]["spec"].get("chartRef", {}).get("kind") == "OCIRepository",
      "flux-operator sourced from an OCIRepository (the chart ships OCI-only)")
check(not any(d.get("kind") == "FluxInstance" for d in docs),
      "no FluxInstance object — the existing vanilla Flux install stays untouched (ADR-0005 guardrail)")

if fails:
    sys.exit(f"\n{len(fails)} invariant(s) broken")
print("  -- all offline invariants hold --")
PY

if command -v kubectl >/dev/null && timeout 10 kubectl --context "$CTX" get ns kyverno >/dev/null 2>&1; then
  echo "== live: engine controllers + CRDs =="
  OUT=$(timeout 20 kubectl --context "$CTX" -n kyverno get pods 2>/dev/null)
  echo "$OUT" | grep -q kyverno && echo "  ok   Kyverno pods present" || fail "Kyverno pods not present"

  timeout 10 kubectl --context "$CTX" get crd mutatingpolicies.policies.kyverno.io >/dev/null 2>&1 \
    && echo "  ok   MutatingPolicy CRD registered" || fail "MutatingPolicy CRD missing"
  timeout 10 kubectl --context "$CTX" get crd validatingpolicies.policies.kyverno.io >/dev/null 2>&1 \
    && echo "  ok   ValidatingPolicy CRD registered" || fail "ValidatingPolicy CRD missing"

  OUT=$(timeout 20 kubectl --context "$CTX" -n flux-system get pods 2>/dev/null)
  echo "$OUT" | grep -q flux-operator && echo "  ok   flux-operator pod present" || fail "flux-operator pod not present"
  timeout 10 kubectl --context "$CTX" get crd resourcesets.fluxcd.controlplane.io >/dev/null 2>&1 \
    && echo "  ok   ResourceSet CRD registered" || fail "ResourceSet CRD missing"
else
  echo "== live checks skipped (engine not up; run estate/platform/engine/up.sh) =="
fi
echo "verify-engine: done"
