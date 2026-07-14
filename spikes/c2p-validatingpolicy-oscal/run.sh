#!/usr/bin/env bash
# Runnable check: does OSCAL Compass Compliance-to-Policy (C2P) v2 consume Kyverno CEL
# ValidatingPolicy PolicyReports and emit correct OSCAL assessment-results?
#
# Proves two things:
#   1. C2P result2oscal keys on results[].policy, which Kyverno writes as the VP
#      metadata.name verbatim -> the ValidatingPolicy path works (no legacy ClusterPolicy needed).
#   2. Kyverno >=1.18 emits per-resource reports with the subject in .scope and
#      results[].resources=null; C2P reads subjects from results[].resources, so a ~6-line
#      jq shim (scope -> resources) is required. RAW run is wrong (passing control shows
#      not-satisfied); SHIMMED run is correct.
#
# Prereqs: docker, kind, kubectl, helm, go (>=1.24), jq, git.  ~4 min from cold.
set -euo pipefail
cd "$(dirname "$0")"
CLUSTER=c2p-spike
WORK=./.work            # gitignored: cloned C2P + built binaries + generated inputs/outputs
KEEP=${KEEP:-0}         # KEEP=1 to leave the cluster up

mkdir -p "$WORK"

echo "== 1. KiND cluster =="
kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --wait 120s

echo "== 2. Kyverno (>=1.17 for CEL ValidatingPolicy + reports) =="
helm repo add kyverno https://kyverno.github.io/kyverno/ >/dev/null 2>&1 || true
helm repo update kyverno >/dev/null 2>&1
helm upgrade --install kyverno kyverno/kyverno -n kyverno --create-namespace --wait --timeout 5m >/dev/null
kubectl -n kyverno wait --for=condition=Available deploy --all --timeout=180s >/dev/null

echo "== 3. Policies + compliant/non-compliant pods =="
kubectl apply -f manifests.yaml >/dev/null
echo "   waiting for background-scan PolicyReports..."
for i in $(seq 1 40); do
  n=$(kubectl -n spike get policyreports.wgpolicyk8s.io -o json 2>/dev/null | jq '[.items[].results[]?]|length')
  [ "${n:-0}" -ge 4 ] && break; sleep 5
done
echo "   results[].policy values Kyverno wrote (the crux — must equal the VP names):"
kubectl -n spike get policyreports.wgpolicyk8s.io -o json | jq -r '.items[].results[]?|"     policy=\(.policy) result=\(.result) source=\(.source)"' | sort -u

echo "== 4. Build C2P v2.0.0-rc.1 =="
[ -d "$WORK/c2p" ] || git clone --depth 1 --branch v2.0.0-rc.1 https://github.com/oscal-compass/compliance-to-policy-go.git "$WORK/c2p" >/dev/null 2>&1
( cd "$WORK/c2p" && go build -o bin/c2pcli ./cmd/c2pcli && go build -o bin/kyverno-plugin ./cmd/kyverno-plugin )
CLI="$WORK/c2p/bin/c2pcli"

echo "== 5. Assemble C2P inputs =="
rm -rf "$WORK/plugins" "$WORK/reports"
mkdir -p "$WORK/plugins" "$WORK/policy-resources" "$WORK/tmp" "$WORK/tmp-out" "$WORK/reports"
cp "$WORK/c2p/bin/kyverno-plugin" "$WORK/plugins/kyverno-plugin"
sum=$(shasum -a 256 "$WORK/plugins/kyverno-plugin" | cut -d' ' -f1)
cat > "$WORK/plugins/c2p-kyverno-manifest.json" <<EOF
{ "metadata": { "id": "kyverno", "description": "Kyverno PVP Plugin", "version": "0.0.1", "types": ["pvp"] },
  "executablePath": "kyverno-plugin", "sha256": "$sum",
  "configuration": [
    { "name": "policy-dir", "required": true },
    { "name": "policy-results-dir", "required": true },
    { "name": "temp-dir", "required": true },
    { "name": "output-dir", "required": false, "default": "." } ] }
EOF
cat > "$WORK/c2p-config.yaml" <<EOF
component-definition: $(pwd)/component-definition.json
plugins:
  kyverno:
    policy-dir: $(pwd)/$WORK/policy-resources
    policy-results-dir: $(pwd)/$WORK/reports
    temp-dir: $(pwd)/$WORK/tmp
    output-dir: $(pwd)/$WORK/tmp-out
EOF
# required-but-unused legacy files (C2P stats them; only *policyreports* are read)
empty(){ printf 'apiVersion: v1\nkind: List\nitems: []\n' > "$1"; }
empty "$WORK/reports/policies.kyverno.io.yaml"
empty "$WORK/reports/clusterpolicies.kyverno.io.yaml"
empty "$WORK/reports/clusterpolicyreports.wgpolicyk8s.io.yaml"

verdict(){ # $1 out.json
  for ctl in cm-8 sc-7; do
    hit=$(jq --arg c "$ctl" '[.["assessment-results"].results[0].findings[]?|select(.target["target-id"]|startswith($c))]|length' "$1")
    [ "$hit" -gt 0 ] && echo "     $ctl -> NOT-SATISFIED" || echo "     $ctl -> SATISFIED"
  done
}

echo "== 6a. RAW reports (results[].resources = null) =="
kubectl -n spike get policyreports.wgpolicyk8s.io -o json > "$WORK/reports/policyreports.wgpolicyk8s.io.yaml"
"$CLI" result2oscal -c "$WORK/c2p-config.yaml" -n nist_800_53 -o "$WORK/out-raw.json" -p "$WORK/plugins" 2>/dev/null
echo "   subjects captured: $(jq '[.["assessment-results"].results[0].observations[]?.subjects[]?]|length' "$WORK/out-raw.json")   (0 == broken)"
verdict "$WORK/out-raw.json"

echo "== 6b. SHIMMED reports (scope -> results[].resources) =="
kubectl -n spike get policyreports.wgpolicyk8s.io -o json \
 | jq '.items |= map(.scope as $s | .results |= map(.resources = [{apiVersion:$s.apiVersion, kind:$s.kind, namespace:$s.namespace, name:$s.name, uid:$s.uid}]))' \
 > "$WORK/reports/policyreports.wgpolicyk8s.io.yaml"
"$CLI" result2oscal -c "$WORK/c2p-config.yaml" -n nist_800_53 -o "$WORK/out-shim.json" -p "$WORK/plugins" 2>/dev/null
echo "   subjects captured: $(jq '[.["assessment-results"].results[0].observations[]?.subjects[]?]|length' "$WORK/out-shim.json")   (4 == correct)"
verdict "$WORK/out-shim.json"

echo
echo "EXPECTED: RAW  -> cm-8 NOT-SATISFIED, sc-7 NOT-SATISFIED (false negative on sc-7)"
echo "          SHIM -> cm-8 NOT-SATISFIED, sc-7 SATISFIED     (correct)"
echo "OSCAL written to $WORK/out-shim.json (C2P self-validates it; oscal-version 1.1.3)."

[ "$KEEP" = 1 ] || kind delete cluster --name "$CLUSTER" >/dev/null 2>&1
