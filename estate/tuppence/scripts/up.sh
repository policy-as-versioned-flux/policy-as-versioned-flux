#!/usr/bin/env bash
# Idempotent bring-up of the tuppence institution:
#   KinD cluster  ->  Flux  ->  real GitHub source  ->  reconcile healthy
# Same shape as driftwood's scripts/up.sh (the provenance base) — tuppence
# inherits the pattern, not a copy of the risk. Requires internet: the
# GitRepository sources are the real policy-as-versioned-{tuppence,nist}
# GitHub repos, no offline fallback. Re-runnable at a venue between talk
# runs. Pair with reset.sh to start clean.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

require kind kubectl flux docker curl

# 1. cluster (idempotent) --------------------------------------------------
if kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  say "cluster '$CLUSTER' already exists"
else
  say "creating KinD cluster '$CLUSTER'"
  kind create cluster --name "$CLUSTER" --config "${HERE}/kind/tuppence.yaml" --wait 120s
fi
kubectl config use-context "$CTX" >/dev/null

# 2. Flux (idempotent; flux install re-applies cleanly) --------------------
if flux check --context "$CTX" >/dev/null 2>&1; then
  say "Flux already installed and healthy"
else
  say "installing Flux (first run pulls controller images once, then cached)"
  flux install --context "$CTX"
fi

# 3. GitHub must actually be reachable before asking Flux to reconcile from
#    it -- fail fast and legibly here rather than let `flux reconcile` sit
#    out its retry/backoff until a multi-minute timeout expires.
say "checking github.com is reachable"
if ! timeout 10 curl -fsS -o /dev/null https://github.com; then
  echo "FAIL: github.com unreachable within 10s (DNS/network/proxy?)." >&2
  echo "      GitRepository sources are the real GitHub repos now -- there is" >&2
  echo "      no offline fallback. Fix connectivity and re-run." >&2
  exit 1
fi

# 4. GitRepository + Kustomization, straight from the committed manifests --
#    (real GitHub URLs, tag-pinned -- see gitops/flux-system/gotk-sync*.yaml)
say "applying GitRepository + Kustomization (tuppence, real GitHub source)"
kubectl apply -f "${GITOPS_DIR}/flux-system/gotk-sync.yaml"
say "applying pinned nist GitRepository (real GitHub source)"
kubectl apply -f "${GITOPS_DIR}/flux-system/gotk-sync-nist.yaml"

# 5. reconcile + report ----------------------------------------------------
# Bounded and explicit: a network failure here fails within 60s with a
# pointer to the diagnostic command, instead of hanging on flux's default.
say "forcing reconcile"
flux reconcile source git tuppence --context "$CTX" --timeout 60s || {
  echo "FAIL: tuppence GitRepository did not become Ready within 60s." >&2
  echo "      kubectl --context $CTX -n flux-system describe gitrepository tuppence" >&2
  exit 1
}
flux reconcile source git nist --context "$CTX" --timeout 60s || {
  echo "FAIL: nist GitRepository did not become Ready within 60s." >&2
  echo "      kubectl --context $CTX -n flux-system describe gitrepository nist" >&2
  exit 1
}
flux reconcile kustomization tuppence --with-source --context "$CTX" --timeout 60s || {
  echo "FAIL: tuppence Kustomization did not become Ready within 60s." >&2
  echo "      kubectl --context $CTX -n flux-system describe kustomization tuppence" >&2
  exit 1
}

say "done. status:"
flux get sources git tuppence --context "$CTX"
flux get sources git nist --context "$CTX"
flux get kustomizations tuppence --context "$CTX"
echo
say "run  estate/tuppence/verify-reconcile.sh  to assert the beat"
