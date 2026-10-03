#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3
"$PY" "$HERE/enact_record.py" selfcheck || exit 1
[ "${1:-}" != --selfcheck ] || exit 0
"$PY" "$HERE/enact_record.py" check
