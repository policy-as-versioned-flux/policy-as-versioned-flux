#!/usr/bin/env bash
# Ticket 151: a cloud admission observation, never a green on offline replay.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${ROOT}/.venv/bin/python"
[ -x "$PY" ] || PY=python3
exec "$PY" "$ROOT/verify/cloud-plane/cloud_plane.py" "$@"
