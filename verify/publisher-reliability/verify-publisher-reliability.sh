#!/usr/bin/env bash
# Another party's signed report; an empty population is not a measured pass.
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo 'SKIP: publisher reliability instrument missing: Python 3'; exit 3; }
exec "$PY" "$ROOT/verify/publisher-reliability/report_check.py" "$@"
