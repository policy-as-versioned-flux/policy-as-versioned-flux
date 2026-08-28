#!/usr/bin/env bash
# Shared by the seven NORTH-STAR §4 step scripts (ticket 52). Source, do not run.
# Contract: last line PASS:/FAIL:/SKIP:; exit 0 / 1 / 3. A step that brings the ephemeral
# cluster up deletes it on exit (trap), so the harness owns no state between runs.
set -uo pipefail
E2E_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$E2E_DIR/../.." && pwd)"
ESTATE="$ROOT/.estate-clone"
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY=python3
CLUSTER=pav-e2e   # ephemeral; never one of driftwood/tuppence/ludlow

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
pass() { echo "PASS: $*"; exit 0; }
fail() { echo "FAIL: $*"; exit 1; }
skip() { echo "SKIP: $*"; exit 3; }
step() { echo "E2E step $1 $2"; }   # step N <name>

cluster_up() {
  command -v kind >/dev/null && docker info >/dev/null 2>&1 || skip "substrate absent (kind/docker)"
  kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --wait 60s >/dev/null || fail "kind create cluster $CLUSTER"
  trap cluster_down EXIT
}
cluster_down() { kind delete cluster --name "$CLUSTER" >/dev/null 2>&1 || true; }
