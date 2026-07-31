#!/usr/bin/env bash
# Idempotent, offline-safe bring-up of the tuppence institution:
#   KinD cluster  ->  Flux  ->  in-cluster signed git source  ->  reconcile healthy
# Same shape as driftwood's scripts/up.sh (the provenance base) — tuppence inherits
# the pattern, not a copy of the risk. Re-runnable at a venue between talk runs.
# Pair with reset.sh to start clean.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

require kind kubectl flux docker git

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

# 3. seed a git repo from the gitops tree, tag it, bake into an image -------
say "seeding tuppence gitops repo + building offline git server"
rm -rf "$WORK"; mkdir -p "$WORK/seed" "$WORK/ctx"
cp -R "$GITOPS_DIR/." "$WORK/seed/"
git -C "$WORK/seed" init -q -b main
git -C "$WORK/seed" -c user.email=demo@tuppence -c user.name=demo add -A
git -C "$WORK/seed" -c user.email=demo@tuppence -c user.name=demo commit -q -m "tuppence gitops @1.0.0"
# Annotated tag = the pinned release. On the real remote this tag is
# gitsign-signed (keyless -> Rekor); offline we pin tag+commit for immutability.
git -C "$WORK/seed" -c user.email=demo@tuppence -c user.name=demo tag -a v1.0.0 -m "tuppence v1.0.0"
COMMIT="$(git -C "$WORK/seed" rev-parse HEAD)"
say "pinned revision: v1.0.0 @ ${COMMIT}"
git -C "$WORK/seed" clone -q --bare "$WORK/seed" "$WORK/ctx/tuppence.git"
cp "$GITSERVER_DIR/Dockerfile" "$GITSERVER_DIR/lighttpd.conf" "$WORK/ctx/"

# 3b. seed tuppence's pinned nist dependency the same way, from estate/nist ---
say "seeding pinned nist catalog dependency"
NIST_DIR="${HERE}/../nist"
NIST_SEED="$WORK/nist-seed"
rm -rf "$NIST_SEED"; mkdir -p "$NIST_SEED"
cp -R "$NIST_DIR/catalog/." "$NIST_SEED/"
git -C "$NIST_SEED" init -q -b main
git -C "$NIST_SEED" -c user.email=regulator@nist -c user.name=nist add -A
git -C "$NIST_SEED" -c user.email=regulator@nist -c user.name=nist commit -q -m "nist 800-53 catalog @ 1.0.0"
git -C "$NIST_SEED" -c user.email=regulator@nist -c user.name=nist tag -a v1.0.0 -m "nist catalog v1.0.0"
NIST_COMMIT="$(git -C "$NIST_SEED" rev-parse HEAD)"
say "pinned nist revision: v1.0.0 @ ${NIST_COMMIT}"
git -C "$NIST_SEED" clone -q --bare "$NIST_SEED" "$WORK/ctx/nist.git"

docker build -q -t "$IMAGE" "$WORK/ctx" >/dev/null
kind load docker-image "$IMAGE" --name "$CLUSTER"

# 4. run the git server ----------------------------------------------------
kubectl apply -f "$GITSERVER_DIR/deployment.yaml"
kubectl -n flux-system rollout status deploy/git-server --timeout=120s

# 5. GitRepository (pinned tag+commit) + Kustomization ---------------------
say "applying GitRepository (pinned v1.0.0 @ ${COMMIT:0:12}) + Kustomization"
cat <<YAML | kubectl apply -f -
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: { name: tuppence, namespace: flux-system }
spec:
  interval: 1m
  url: ${GIT_URL_IN_CLUSTER}
  ref:
    tag: v1.0.0
    commit: ${COMMIT}
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: tuppence, namespace: flux-system }
spec:
  interval: 5m
  retryInterval: 1m
  timeout: 3m
  sourceRef: { kind: GitRepository, name: tuppence }
  path: ./apps
  prune: true
  wait: true
YAML

say "applying pinned nist GitRepository (v1.0.0 @ ${NIST_COMMIT:0:12})"
cat <<YAML | kubectl apply -f -
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: nist
  namespace: flux-system
  labels: { policy-as-versioned.dev/upstream: nist }
spec:
  interval: 5m
  url: http://git-server.flux-system.svc.cluster.local/cgi-bin/git/nist.git
  ref:
    tag: v1.0.0
    commit: ${NIST_COMMIT}
YAML

# 6. reconcile + report ----------------------------------------------------
say "forcing reconcile"
flux reconcile source git tuppence --context "$CTX"
flux reconcile source git nist --context "$CTX"
flux reconcile kustomization tuppence --with-source --context "$CTX"

say "done. status:"
flux get sources git tuppence --context "$CTX"
flux get sources git nist --context "$CTX"
flux get kustomizations tuppence --context "$CTX"
echo
say "run  estate/tuppence/verify-reconcile.sh  to assert the beat"
