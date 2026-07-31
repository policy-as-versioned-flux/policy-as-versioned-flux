#!/usr/bin/env bash
# Beat: "driftwood reconciles from a pinned, signed GitRepository, healthily."
# Exits non-zero if that beat would fail on stage. Run after scripts/up.sh.
source "$(dirname "${BASH_SOURCE[0]}")/scripts/lib.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
ready() { # kind/name/ns -> asserts Ready=True
  local got
  got=$(kubectl --context "$CTX" -n "$3" get "$1" "$2" \
        -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
  [ "$got" = True ] || fail "$1/$2 Ready=$got (want True)"
}

say "1. GitRepository is Ready and pinned to a tag+commit"
ready gitrepository driftwood flux-system
kubectl --context "$CTX" -n flux-system get gitrepository driftwood \
  -o jsonpath='{.spec.ref.tag}' | grep -qx v1.0.0 || fail "GitRepository not pinned to tag v1.0.0"
kubectl --context "$CTX" -n flux-system get gitrepository driftwood \
  -o jsonpath='{.spec.ref.commit}' | grep -qE '^[0-9a-f]{40}$' || fail "GitRepository commit not pinned"

say "2. Kustomization is Ready (reconcile healthy)"
ready kustomization driftwood flux-system

say "3. the reconciled content actually landed in the cluster"
kubectl --context "$CTX" get ns driftwood >/dev/null 2>&1 || fail "namespace 'driftwood' not reconciled"
v=$(kubectl --context "$CTX" -n driftwood get cm driftwood-live-version \
    -o jsonpath='{.data.policyVersion}' 2>/dev/null)
[ "$v" = "1.0.0" ] || fail "live version configmap not reconciled (got '$v')"

echo "PASS: driftwood reconciles from a pinned GitRepository, healthy, content live."
