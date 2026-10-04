#!/usr/bin/env bash
# Ticket 142: served workflows and priced rungs, with local capability ceiling named.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3
"$PY" "$HERE/twin_cage.py" selfcheck
"$PY" "$HERE/twin_cage.py" check --estate "${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
