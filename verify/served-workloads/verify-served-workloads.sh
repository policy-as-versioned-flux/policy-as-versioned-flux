#!/usr/bin/env bash
# Ticket 155: the adopter's instruments grade its own scheduled observations.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${HERE}/../.." && pwd)"
PY="${PYTHON:-${ROOT}/.venv/bin/python}"
if [ -z "${PYTHON:-}" ] && [ ! -x "$PY" ]; then
  PY="$(command -v python3 || true)"
fi
[ -x "$PY" ] || { echo 'SKIP: no hub interpreter for the workload lane'; exit 3; }
INSTRUMENT="${1:-served_apps.py}"
case "$INSTRUMENT" in served_apps.py|oscal_lane.py) ;; *) echo "FAIL: unknown lane instrument $INSTRUMENT"; exit 1 ;; esac
result=0
for party in driftwood tuppence ludlow; do
  adopter="${ROOT}/.estate-clone/${party}"
  for instrument in "$INSTRUMENT"; do
    [ -f "${adopter}/drift/${instrument}" ] || { echo "SKIP: ${party} has no ${instrument}; ticket 155's instrument has not reached this checkout"; [ "$result" = 1 ] || result=3; continue; }
    echo "==> ${party}: ${instrument}"
    "$PY" "${adopter}/drift/${instrument}" selfcheck
    rc=$?
    if [ "$rc" != 0 ]; then result=1; continue; fi
    "$PY" "${adopter}/drift/${instrument}" grade
    rc=$?
    if [ "$rc" = 1 ]; then result=1; elif [ "$rc" != 0 ] && [ "$result" != 1 ]; then result=3; fi
  done
done
exit "$result"
