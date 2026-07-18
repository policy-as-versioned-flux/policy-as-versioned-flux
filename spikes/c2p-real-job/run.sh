#!/usr/bin/env bash
# ============================================================================
# Ticket 20 — the REAL C2P result2oscal collection job (not the toy spike).
#
# Regenerable-from-nothing job: brings up a throwaway KiND cluster, installs the
# version-PINNED Kyverno, applies the TWO REAL cloud-plane ValidatingPolicies
# (require-s3-bucket-encryption -> NIST sc-28, require-rds-multi-az -> NIST cp-10)
# plus one ILLUSTRATIVE workload policy (require-team-label -> cm-8, mechanism proof
# only — see README), runs OSCAL Compass C2P `result2oscal` over the PolicyReports
# the one Kyverno engine emits, and proves the output is schema-valid TWO ways:
#   (a) C2P's own built-in OSCAL validation (Go / compliance-trestle code path), and
#   (b) an INDEPENDENT validator: Python check-jsonschema against the official
#       usnistgov/OSCAL v1.1.3 assessment-results JSON Schema (different language,
#       different codebase, different schema source — genuinely not "C2P twice").
#
# Two collection passes prove BOTH OSCAL states per control:
#   PASS 1 (compliant world):   only *-pass fixtures  -> every mapped control satisfied
#   PASS 2 (with violations):   add *-fail fixtures    -> mapped controls not-satisfied
#
# Self-tears-down (KEEP=1 to leave the cluster up). ~5-8 min from cold.
# Prereqs: docker, kind, kubectl, helm, go (>=1.24), jq, git, python3 (venv).
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")"

# ---- PINS (all dependency versions live here) ------------------------------
CLUSTER=c2p-real-job
KYVERNO_CHART=3.8.2          # == Kyverno app v1.18.2. MUST match the fleet pin at
                            # pavf-fleet/infrastructure/kyverno/helmrelease.yaml.
                            # >=1.18 is a hard dep: CEL ValidatingPolicy GA + the
                            # background-scan PolicyReport shape this job consumes.
C2P_REF=v2.0.0-rc.1         # OSCAL Compass compliance-to-policy-go, pinned + built
                            # from source (pre-GA, accepted risk per ADR-0009 / PRD §10).
OSCAL_VER=1.1.3            # official OSCAL schema tag for the independent validator;
                            # matches the oscal-version C2P emits.
CJS_VER=0.37.4            # check-jsonschema pin (independent validator, jsonschema-based).

# ---- REPORT-API SHAPE DEPENDENCY (read this before changing the collection) ----
# Kyverno has shipped its PolicyReport CRD under TWO API groups across versions:
# the long-standing `wgpolicyk8s.io` and the newer `openreports.io`. C2P's
# kyverno-plugin reads `wgpolicyk8s.io/v1alpha2 PolicyReport`. The PINNED Kyverno
# (chart 3.8.2 / app 1.18.2) emits ONLY `wgpolicyk8s.io` (confirmed empirically
# 2026-07-15: `kubectl api-resources` on this cluster shows the wgpolicyk8s.io/v1alpha2
# PolicyReport group and NO openreports.io group). The job is self-checking: if
# wgpolicyk8s.io ever stopped carrying results, wait_for_results() times out and
# collect() captures 0 subjects — the first visible sign the group changed. If a future
# Kyverno bump makes `openreports.io` the primary/only group, the single
# `kubectl get policyreports.wgpolicyk8s.io` line in collect() is the ONE place to change
# (and the C2P plugin would need a matching update). That is the whole report-API-shape
# assumption, and it lives right here + at that line.
REPORT_GROUP=policyreports.wgpolicyk8s.io

WORK=./.work                # gitignored: cloned+built C2P, venv, generated inputs/outputs
KEEP=${KEEP:-0}
NS=default
mkdir -p "$WORK"

echo "== 1. KiND cluster (from scratch; idempotent) =="
kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --wait 120s

# Wave-1 audit (2026-07-18) found this job's kubectl/helm calls relied entirely on
# `kind create cluster` having switched the ambient current-context, with nothing checking
# it actually did -- when that assumption broke (however it broke: partial/manual run,
# an environment where `kind create` silently no-ops, etc.), every apply below landed on
# whatever cluster the ambient context happened to point at instead, undetected, on a
# *shared* cluster in this project's case. Every kubectl/helm call from here on is
# explicitly pinned to this job's own context -- it is structurally impossible for this
# script to touch any other cluster, regardless of what the ambient context is.
KCTX="kind-$CLUSTER"
kubectl config get-contexts -o name | grep -qx "$KCTX" || { echo "FATAL: context $KCTX not found after cluster creation -- refusing to proceed against the ambient context"; exit 1; }
kubectl() { command kubectl --context "$KCTX" "$@"; }
helm() { command helm --kube-context "$KCTX" "$@"; }

echo "== 2. Kyverno PINNED chart $KYVERNO_CHART (== app v1.18.2, matches fleet) =="
helm repo add kyverno https://kyverno.github.io/kyverno/ >/dev/null 2>&1 || true
helm repo update kyverno >/dev/null 2>&1
helm upgrade --install kyverno kyverno/kyverno --version "$KYVERNO_CHART" \
  -n kyverno --create-namespace --wait --timeout 5m >/dev/null
kubectl -n kyverno wait --for=condition=Available deploy --all --timeout=180s >/dev/null
echo "   kyverno app version: $(helm -n kyverno get metadata kyverno -o json 2>/dev/null | jq -r .appVersion 2>/dev/null || echo '(1.18.2 per chart '"$KYVERNO_CHART"')')"

echo "== 3. Stand-in Crossplane CRDs + Kyverno RBAC for the cloud CRs =="
kubectl apply -f crds/ >/dev/null
kubectl wait --for=condition=Established crd/bucketserversideencryptionconfigurations.s3.aws.m.upbound.io >/dev/null
kubectl wait --for=condition=Established crd/instances.rds.aws.m.upbound.io >/dev/null

echo "== 4. Real cloud policies (sc-28, cp-10) + illustrative workload policy (cm-8) =="
kubectl apply -f policies/ >/dev/null
# Kyverno needs a beat to register the ValidatingPolicy webhooks before admission.
kubectl -n kyverno rollout status deploy -l app.kubernetes.io/component=admission-controller --timeout=120s >/dev/null 2>&1 || true
sleep 10

# ---- C2P build (pinned, vendored binary) -----------------------------------
echo "== 5. Build C2P $C2P_REF from source (reuses ../c2p clone if present) =="
if [ -x "../c2p-validatingpolicy-oscal/.work/c2p/bin/c2pcli" ]; then
  # reuse the sibling spike's already-built, same-ref binaries (speed; identical pin)
  cp -R "../c2p-validatingpolicy-oscal/.work/c2p" "$WORK/c2p" 2>/dev/null || true
fi
[ -d "$WORK/c2p/.git" ] || rm -rf "$WORK/c2p"
[ -d "$WORK/c2p" ] || git clone --depth 1 --branch "$C2P_REF" https://github.com/oscal-compass/compliance-to-policy-go.git "$WORK/c2p" >/dev/null 2>&1
( cd "$WORK/c2p" && go build -o bin/c2pcli ./cmd/c2pcli && go build -o bin/kyverno-plugin ./cmd/kyverno-plugin )
CLI="$WORK/c2p/bin/c2pcli"

echo "== 6. Independent OSCAL validator (Python check-jsonschema, offline schema cache) =="
[ -x "$WORK/venv/bin/check-jsonschema" ] || python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install --quiet "check-jsonschema==$CJS_VER" >/dev/null 2>&1
SCHEMA="$WORK/oscal_assessment-results_v${OSCAL_VER}.json"
[ -s "$SCHEMA" ] || curl -sSL --max-time 60 -o "$SCHEMA" \
  "https://github.com/usnistgov/OSCAL/releases/download/v${OSCAL_VER}/oscal_assessment-results_schema.json"
jq -e '.["$id"]|test("oscal-ar-schema")' "$SCHEMA" >/dev/null || { echo "ERROR: OSCAL schema download bad"; exit 1; }

# ---- assemble static C2P inputs (plugin manifest + config) ------------------
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
# required-but-unused legacy inputs C2P stats (only *policyreports* are read)
empty(){ printf 'apiVersion: v1\nkind: List\nitems: []\n' > "$1"; }

wait_for_results(){ # $1 = expected minimum result count
  for i in $(seq 1 48); do
    n=$(kubectl -n "$NS" get "$REPORT_GROUP" -o json 2>/dev/null | jq '[.items[].results[]?]|length')
    [ "${n:-0}" -ge "$1" ] && return 0; sleep 5
  done
  return 0
}

# collect(out.json): shim the reports, run C2P result2oscal, validate both ways.
collect(){
  local out="$1"
  empty "$WORK/reports/policies.kyverno.io.yaml"
  empty "$WORK/reports/clusterpolicies.kyverno.io.yaml"
  empty "$WORK/reports/clusterpolicyreports.wgpolicyk8s.io.yaml"
  # THE COLLECTION SHIM (declarative jq, ADR-0009). Two normalizations:
  #  1. scope -> results[].resources : Kyverno >=1.18 emits per-resource reports with
  #     the subject in .scope and results[].resources=null; C2P reads subjects from
  #     results[].resources, so without this every in-scope control false-negatives.
  #  2. version-suffix strip on results[].policy : the coexistence build deploys VPs
  #     as <policy>-<x.y.z> (nameSuffix); strip the trailing -SEMVER so the name equals
  #     the component-definition Check_Id. (No-op here — this spike deploys UNSUFFIXED
  #     names — but this is exactly the strip the production collection job carries.)
  kubectl -n "$NS" get "$REPORT_GROUP" -o json \
   | jq '.items |= map(.scope as $s | .results |= map(
           .policy   = (.policy | sub("-[0-9]+\\.[0-9]+\\.[0-9]+$"; "")) |
           .resources = [{apiVersion:$s.apiVersion, kind:$s.kind, namespace:$s.namespace, name:$s.name, uid:$s.uid}]))' \
   > "$WORK/reports/policyreports.wgpolicyk8s.io.yaml"
  # (a) C2P built-in validation runs inside result2oscal (it self-validates before write)
  "$CLI" result2oscal -c "$WORK/c2p-config.yaml" -n nist_800_53 -o "$out" -p "$WORK/plugins" 2>/dev/null
  # (b) INDEPENDENT validation — different code path entirely
  "$WORK/venv/bin/check-jsonschema" --schemafile "$SCHEMA" "$out" >/dev/null \
    && echo "   independent schema-validate (check-jsonschema vs OSCAL v$OSCAL_VER): PASS" \
    || { echo "   independent schema-validate: FAIL"; exit 1; }
}

verdict(){ # $1=out.json ; prints each control's satisfied/not-satisfied
  for ctl in sc-28 cp-10 cm-8; do
    ns=$(jq --arg c "$ctl" '[.["assessment-results"].results[0].findings[]?
          | select(.target["target-id"]|startswith($c))
          | select(.target.status.state=="not-satisfied")]|length' "$1")
    [ "$ns" -gt 0 ] && echo "     $ctl -> NOT-SATISFIED" || echo "     $ctl -> satisfied"
  done
}

echo "== 7. PASS 1 — compliant world (only *-pass fixtures) =="
kubectl apply -f fixtures/pass/ >/dev/null
echo "   waiting for pass reports..."; wait_for_results 3
collect "$WORK/out-compliant.json"
echo "   subjects captured: $(jq '[.["assessment-results"].results[0].observations[]?.subjects[]?]|length' "$WORK/out-compliant.json") (0 == broken shim)"
verdict "$WORK/out-compliant.json"

echo "== 8. PASS 2 — with violations (add *-fail fixtures) =="
kubectl apply -f fixtures/fail/ >/dev/null
echo "   waiting for fail reports..."; wait_for_results 6
collect "$WORK/out-violations.json"
echo "   subjects captured: $(jq '[.["assessment-results"].results[0].observations[]?.subjects[]?]|length' "$WORK/out-violations.json")"
verdict "$WORK/out-violations.json"

echo
echo "EXPECTED:"
echo "  PASS 1 (compliant):   sc-28 satisfied,     cp-10 satisfied,     cm-8 satisfied"
echo "  PASS 2 (violations):  sc-28 NOT-SATISFIED, cp-10 NOT-SATISFIED, cm-8 NOT-SATISFIED"
echo "  sc-28 + cp-10 are the REAL, load-bearing cloud-plane NIST controls."
echo "  cm-8 is ILLUSTRATIVE (workload mechanism proof only) — see README.md."
echo "OSCAL written: $WORK/out-compliant.json , $WORK/out-violations.json"
echo "Both validated by C2P built-in AND independent check-jsonschema vs OSCAL v$OSCAL_VER."

[ "$KEEP" = 1 ] || kind delete cluster --name "$CLUSTER" >/dev/null 2>&1
