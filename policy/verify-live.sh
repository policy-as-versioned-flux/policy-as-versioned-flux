#!/usr/bin/env bash
# Runnable check for issue 03's last claim: the Audit lane-keeper reports but
# admits, the Deny gate refuses -- a distinction `kyverno test` can't show,
# since it evaluates the CEL rule, not the admission webhook. Requires a live
# cluster with Kyverno (fleet/up.sh); applies+removes the policies directly
# with kubectl, bypassing GitOps (Flux wiring lands in a later issue).
set -euo pipefail
cd "$(dirname "$0")"

cleanup() {
  kubectl delete pod live-audit-fail --ignore-not-found >/dev/null
  kubectl delete -k workloads/kyverno/require-known-department-label --ignore-not-found >/dev/null
  kubectl delete -k workloads/kyverno/require-department-label --ignore-not-found >/dev/null
}
trap cleanup EXIT

echo "== apply both policies =="
kubectl apply -k workloads/kyverno/require-department-label >/dev/null
kubectl apply -k workloads/kyverno/require-known-department-label >/dev/null
kubectl wait --for=jsonpath='{.status.conditionStatus.ready}'=true \
  validatingpolicy/require-department-label-1.0.0 \
  validatingpolicy/require-known-department-label-1.0.0 --timeout=60s >/dev/null

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
