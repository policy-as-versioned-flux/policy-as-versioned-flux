#!/usr/bin/env bash
# PROTOTYPE — spike cs-06. One command, no arguments, no setup.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
exec python3 compare.py
