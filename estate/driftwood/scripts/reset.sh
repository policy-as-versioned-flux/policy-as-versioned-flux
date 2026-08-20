#!/usr/bin/env bash
# Tear driftwood down to nothing. `reset.sh soft` keeps the cluster+Flux and
# just re-applies the GitOps sources + forces a reconcile (fast between-run
# reset); default deletes the whole KinD cluster.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

if [ "${1:-hard}" = soft ]; then
  say "soft reset: re-applying GitOps sources, keeping cluster + Flux"
  exec "$(dirname "${BASH_SOURCE[0]}")/up.sh"
fi

say "deleting KinD cluster '$CLUSTER'"
kind delete cluster --name "$CLUSTER" 2>/dev/null || true
say "clean"
