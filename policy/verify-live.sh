#!/usr/bin/env bash
# Runnable check for issue 03's last claim: the Audit lane-keeper reports but
# admits, the Deny gate refuses -- a distinction `kyverno test` can't show,
# since it evaluates the CEL rule, not the admission webhook. Requires a live
# cluster with Kyverno (fleet/up.sh); applies+removes the policies directly
# with kubectl, bypassing GitOps (Flux wiring lands in a later issue).
set -euo pipefail
cd "$(dirname "$0")"

cleanup() {
  kubectl delete pod live-audit-fail live-gate-fail --ignore-not-found >/dev/null
  kubectl delete -k workloads/kyverno/require-known-department-label --ignore-not-found >/dev/null
  kubectl delete -k workloads/kyverno/require-department-label --ignore-not-found >/dev/null
}
trap cleanup EXIT

echo "== apply both policies =="
audit_policy=$(kubectl apply -k workloads/kyverno/require-department-label -o name)
gate_policy=$(kubectl apply -k workloads/kyverno/require-known-department-label -o name)
# ValidatingPolicy has no `Ready`-typed condition (unlike FluxInstance/HelmRelease
# elsewhere in this repo) -- .status.conditionStatus.ready is the field Kyverno
# actually exposes, still via native `kubectl wait`, not a hand-rolled poll loop.
kubectl wait --for=jsonpath='{.status.conditionStatus.ready}'=true \
  "$audit_policy" "$gate_policy" --timeout=60s >/dev/null

echo "== Audit lane-keeper: a non-compliant pod is admitted =="
kubectl apply -f - >/dev/null <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: live-audit-fail
  labels:
    mycompany.com/policy-version: "1.0.0"
spec:
  containers:
    - name: app
      image: nginx:latest
EOF
kubectl get pod live-audit-fail >/dev/null || { echo "FAIL: Audit policy blocked admission (should only report)"; exit 1; }
echo "OK: pod admitted despite missing 'department' label"

echo "== ...and the admission is reported as a failure, not silently dropped =="
# The PolicyReport write-back is async (it lands on the next background scan,
# not synchronously with the API response, and can take tens of seconds);
# poll for it -- not a substitute for kubectl wait, there's no condition to
# wait on, only a report that doesn't exist yet. Resource identity is on the
# report's `.scope`, not `.results[].resources` -- Kyverno >=1.18's per-result
# shape has no resources field (see spikes/c2p-validatingpolicy-oscal, which
# normalizes the same gap for C2P).
reported=false
for _ in $(seq 1 60); do
  fails=$(kubectl get polr -A -o json | jq '[.items[] | select(.scope.name=="live-audit-fail") | .results[]? | select(.policy=="require-department-label-1.0.0" and .result=="fail")] | length')
  [ "$fails" -ge 1 ] && { reported=true; break; }
  sleep 1
done
$reported || { echo "FAIL: no PolicyReport fail entry for the admitted non-compliant pod"; exit 1; }
echo "OK: PolicyReport records the failure"

echo "== Deny gate: a non-compliant pod is refused =="
if kubectl apply -f - >/dev/null 2>&1 <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: live-gate-fail
  labels:
    mycompany.com/policy-version: "1.0.0"
    department: not-a-real-department
spec:
  containers:
    - name: app
      image: nginx:latest
EOF
then
  echo "FAIL: Deny gate admitted a pod with an unknown department"; exit 1
fi
echo "OK: admission refused by the Deny gate"
