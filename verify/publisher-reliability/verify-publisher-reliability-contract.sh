#!/usr/bin/env bash
# Synthetic local consumer proofs only; no genuine signature or outcome claim.
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo 'SKIP: publisher reliability contract needs Python 3'; exit 3; }
command -v git >/dev/null 2>&1 || { echo 'SKIP: publisher reliability contract needs git'; exit 3; }
"$PY" "$ROOT/tests/test_publisher_reliability.py"
echo 'PASS: synthetic consumer fixtures preserve signed-tag routing, native recomputation, genuine population waits and separate binary/monetary claim scopes; no genuine signature or forecast outcome was measured'
