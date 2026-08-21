#!/usr/bin/env bash
# PROTOTYPE — spike cs-06b. One command, no arguments.
# Reads what platform really publishes from ../../.estate-clone/platform.
# SKIPs (exit 0) if that clone is absent; run ../../clone-estate.sh first.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
exec python3 compose.py
