#!/usr/bin/env bash
# Idempotent bring-up of the tuppence institution:
#   KinD cluster  ->  Flux  ->  real GitHub git source  ->  reconcile healthy
# Same shape as driftwood's scripts/up.sh (the provenance base) — tuppence inherits
# the pattern, not a copy of the risk. Re-runnable at a venue between talk runs.
# Pair with reset.sh to start clean.
# Requires internet: the GitRepository sources pull from the real
# policy-as-versioned-tuppence/tuppence and policy-as-versioned-nist/nist repos
# on GitHub (see gitops/flux-system/gotk-sync*.yaml), so step 3 below fails fast
# with a clear message rather than hanging if there is no route to github.com.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

require kind kubectl flux curl

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

# 3. GitRepository + Kustomization sources, pointed at the real GitHub repos
#    (gotk-sync.yaml / gotk-sync-nist.yaml already declare the real URLs) ---
say "checking route to github.com before asking Flux to pull from it"
if ! curl --fail --silent --show-error --max-time 5 -o /dev/null https://github.com; then
  echo "ERROR: no route to github.com (timed out after 5s)." >&2
  echo "       GitRepository sources pull from GitHub now; there is no offline fallback." >&2
  echo "       Fix network access and re-run." >&2
  exit 1
fi

say "applying tuppence + nist GitRepository/Kustomization sources"
kubectl apply -f "$GITOPS_DIR/flux-system/gotk-sync.yaml" -f "$GITOPS_DIR/flux-system/gotk-sync-nist.yaml"

# 4. reconcile + report -----------------------------------------------------
# Short, explicit timeouts: a GitHub outage or a revoked route fails these
# within seconds with Flux's own error instead of sitting on the CLI's 5m
# default, which reads as a hang at a venue.
say "forcing reconcile"
flux reconcile source git tuppence --context "$CTX" --timeout 30s
flux reconcile source git nist --context "$CTX" --timeout 30s
flux reconcile kustomization tuppence --with-source --context "$CTX" --timeout 60s

say "done. status:"
flux get sources git tuppence --context "$CTX"
flux get sources git nist --context "$CTX"
flux get kustomizations tuppence --context "$CTX"
echo
say "run  estate/tuppence/verify-reconcile.sh  to assert the beat"
