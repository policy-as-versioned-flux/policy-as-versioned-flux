#!/usr/bin/env bash
# Shared config + helpers for the tuppence bring-up. Sourced, not run.
set -euo pipefail

CLUSTER=tuppence
CTX="kind-${CLUSTER}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # estate/tuppence
GITOPS_DIR="${HERE}/gitops"
GITSERVER_DIR="${HERE}/git-server"
WORK="${HERE}/.work"
IMAGE=tuppence-git:local
GIT_URL_IN_CLUSTER="http://git-server.flux-system.svc.cluster.local/cgi-bin/git/tuppence.git"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

require() {
  local missing=0
  for c in "$@"; do have "$c" || { echo "MISSING cli: $c" >&2; missing=1; }; done
  [ "$missing" = 0 ] || { echo "install the missing CLIs and re-run" >&2; exit 1; }
}
