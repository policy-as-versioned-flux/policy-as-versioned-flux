#!/usr/bin/env bash
# Whole source fixture only; all monetary inputs and signature responses synthetic.
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo 'SKIP: publisher price vertical instrument missing: Python 3'; exit 3; }
command -v git >/dev/null 2>&1 || { echo 'SKIP: publisher price vertical instrument missing: Git'; exit 3; }
"$PY" "$ROOT/tests/test_publisher_price_vertical.py"
echo 'PASS: complete synthetic publisher producer, independent resolver, scorer and actual composition consume the publisher target; no genuine signature, monetary observation or price credit'
