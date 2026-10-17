#!/usr/bin/env bash
# Local caller proofs only; never a cluster admission observation.
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${ROOT}/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo 'SKIP: cloud contract self-proof needs Python 3'; exit 3; }
"$PY" -c 'import yaml' >/dev/null 2>&1 || { echo 'SKIP: cloud contract self-proof needs PyYAML'; exit 3; }
command -v git >/dev/null 2>&1 || { echo 'SKIP: cloud contract self-proof needs git'; exit 3; }

# ADR0020: exercise the actual absent-instrument exits before the caller proof.
# PATH hiding alone cannot hide the preferred absolute .venv interpreter.
if [ -z "${PAV_SELFCHECK_CHILD:-}" ]; then
  (
    temporary="$(mktemp -d)"
    trap 'rm -rf "$temporary"' EXIT
    script="$temporary/verify/cloud-plane/verify-cloud-plane-contract.sh"
    mkdir -p "${script%/*}" "$temporary/bin" "$temporary/.venv/bin"
    cp "${BASH_SOURCE[0]}" "$script"
    ln -s "$(command -v dirname)" "$temporary/bin/dirname"
    expect_skip() {
      local output result=0 last
      output="$("$@" 2>&1)" || result=$?
      last="$(printf '%s\n' "$output" | tail -1)"
      case "$result:$last" in
        3:SKIP:*) ;;
        *) printf 'FAIL: cloud dependency selfcheck wanted exit 3/SKIP, got %s: %s\n' "$result" "$last"; exit 1 ;;
      esac
    }
    expect_skip env PAV_SELFCHECK_CHILD=1 PATH="$temporary/bin" "${BASH:-/bin/bash}" "$script"
    # -S creates a real absent-PyYAML interpreter, including when .venv exists.
    printf '#!/bin/bash\nexec %q -S "$@"\n' "$PY" > "$temporary/.venv/bin/python"
    chmod +x "$temporary/.venv/bin/python"
    expect_skip env PAV_SELFCHECK_CHILD=1 PYTHONPATH= "${BASH:-/bin/bash}" "$script"
  )
  source "$ROOT/verify/lib-observation.sh"
  selfcheck_absent "$ROOT/verify/cloud-plane/verify-cloud-plane-contract.sh" git
fi
exec "$PY" "$ROOT/tests/test_cloud_plane_contract.py"
