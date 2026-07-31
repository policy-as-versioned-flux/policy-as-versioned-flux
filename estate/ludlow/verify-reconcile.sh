#!/usr/bin/env bash
# Beat: "ludlow reconciles from a pinned, signed GitRepository, healthily, and
# carries its risk skin (Deny-heavy (strictest))." Exits non-zero if that beat would fail on
# stage. Run after scripts/up.sh.
source "$(dirname "${BASH_SOURCE[0]}")/scripts/lib.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
ready() { # kind/name/ns -> asserts Ready=True
  local got
  got=$(kubectl --context "$CTX" -n "$3" get "$1" "$2" \
        -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
  [ "$got" = True ] || fail "$1/$2 Ready=$got (want True)"
}

say "1. GitRepository is Ready and pinned to a tag+commit"
ready gitrepository ludlow flux-system
kubectl --context "$CTX" -n flux-system get gitrepository ludlow \
  -o jsonpath='{.spec.ref.tag}' | grep -qx v1.0.0 || fail "GitRepository not pinned to tag v1.0.0"
kubectl --context "$CTX" -n flux-system get gitrepository ludlow \
  -o jsonpath='{.spec.ref.commit}' | grep -qE '^[0-9a-f]{40}$' || fail "GitRepository commit not pinned"

say "2. Kustomization is Ready (reconcile healthy)"
ready kustomization ludlow flux-system

say "3. the reconciled content actually landed in the cluster"
kubectl --context "$CTX" get ns ludlow >/dev/null 2>&1 || fail "namespace 'ludlow' not reconciled"
v=$(kubectl --context "$CTX" -n ludlow get cm ludlow-live-version \
    -o jsonpath='{.data.policyVersion}' 2>/dev/null)
[ "$v" = "1.0.0" ] || fail "live version configmap not reconciled (got '$v')"

say "4. the pinned nist (regulator) dependency reconciled healthy"
ready gitrepository nist flux-system
kubectl --context "$CTX" -n flux-system get gitrepository nist \
  -o jsonpath='{.spec.ref.tag}' | grep -qx v1.0.0 || fail "nist GitRepository not pinned to tag v1.0.0"
kubectl --context "$CTX" -n flux-system get gitrepository nist \
  -o jsonpath='{.spec.ref.commit}' | grep -qE '^[0-9a-f]{40}$' || fail "nist GitRepository commit not pinned"
nv=$(kubectl --context "$CTX" -n ludlow get cm ludlow-nist-pin \
    -o jsonpath='{.data.catalogVersion}' 2>/dev/null)
[ "$nv" = "1.0.0" ] || fail "nist-pin configmap not reconciled (got '$nv')"

say "5. the risk-appetite skin reconciled and matches platform/risk/appetite.json"
tol=$(kubectl --context "$CTX" -n ludlow get cm ludlow-risk-appetite \
    -o jsonpath='{.data.toleranceGBP}' 2>/dev/null)
[ "$tol" = "5000" ] || fail "risk-appetite configmap tolerance mismatch (got '$tol', want 5000)"
want_tol=$(python3 -c "import json; print(json.load(open('$HERE/../platform/risk/appetite.json'))['orgs']['ludlow']['tolerance'])")
[ "$tol" = "$want_tol" ] || fail "risk-appetite configmap ($tol) drifted from platform/risk/appetite.json ($want_tol)"

echo "PASS: ludlow reconciles from a pinned GitRepository, healthy, content live, nist dependency pinned, risk skin (Deny-heavy (strictest), £5000) live."
