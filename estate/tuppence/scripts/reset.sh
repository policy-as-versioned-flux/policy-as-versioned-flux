#!/usr/bin/env bash
# Tear tuppence down to nothing. `reset.sh soft` keeps the cluster+Flux and only
# re-seeds the git source (fast between-run reset); default deletes the whole
# KinD cluster.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

if [ "${1:-hard}" = soft ]; then
  say "soft reset: re-seeding git source, keeping cluster + Flux"
  kubectl --context "$CTX" -n flux-system delete deploy git-server --ignore-not-found
  exec "$(dirname "${BASH_SOURCE[0]}")/up.sh"
fi

say "deleting KinD cluster '$CLUSTER'"
kind delete cluster --name "$CLUSTER" 2>/dev/null || true
docker image rm "$IMAGE" >/dev/null 2>&1 || true
rm -rf "$WORK"
say "clean"
