#!/usr/bin/env bash
# Local caller proofs only; never a cluster admission observation.
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${ROOT}/.venv/bin/python"
[ -x "$PY" ] || PY=python3
exec "$PY" "$ROOT/tests/test_cloud_plane_contract.py"
