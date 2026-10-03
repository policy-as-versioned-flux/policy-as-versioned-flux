#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3
"$PY" "$HERE/incumbent_org.py" selfcheck || exit 1
[ "${1:-}" != --selfcheck ] || exit 0
args=(check --estate "${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}")
[ -z "${INCUMBENT_GRADES:-}" ] || args+=(--grades "$INCUMBENT_GRADES")
[ -z "${INCUMBENT_FACTS:-}" ] || args+=(--facts "$INCUMBENT_FACTS")
"$PY" "$HERE/incumbent_org.py" "${args[@]}"
