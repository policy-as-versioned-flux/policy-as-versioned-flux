#!/usr/bin/env bash
# verify-rederive-bumps.sh -- ticket cs-01. Runs the REAL kyverno CLI, offline,
# against the old faithful-floor's real, signed release line (fixed input
# copied into corpus/). Exits non-zero if the engine fails to rederive any of
# the three known-good bumps that release proved live.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v kyverno >/dev/null; then
  echo "SKIP: kyverno CLI not found -- rederive-bumps check needs it (offline, no cluster)"
  exit 0
fi

python3 rederive_bumps.py
