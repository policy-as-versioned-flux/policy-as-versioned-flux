#!/usr/bin/env bash
# Tear ludlow down to nothing. `reset.sh soft` keeps the cluster+Flux and only
# re-applies the GitRepository/Kustomization sources (fast between-run reset);
# default deletes the whole KinD cluster.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

if [ "${1:-hard}" = soft ]; then
  say "soft reset: re-applying git sources, keeping cluster + Flux"
  exec "$(dirname "${BASH_SOURCE[0]}")/up.sh"
fi

say "deleting KinD cluster '$CLUSTER'"
kind delete cluster --name "$CLUSTER" 2>/dev/null || true
say "clean"
