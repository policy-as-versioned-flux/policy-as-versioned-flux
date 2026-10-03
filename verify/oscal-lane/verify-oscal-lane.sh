#!/usr/bin/env bash
# Ticket 155: collect PolicyReports, then join every failed observation to a real cage risk.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${HERE}/../served-workloads/verify-served-workloads.sh" oscal_lane.py
