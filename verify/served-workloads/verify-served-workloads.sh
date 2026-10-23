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
CHECK_PATH="verify/served-workloads/verify-served-workloads.sh"
if [ "$INSTRUMENT" = oscal_lane.py ]; then CHECK_PATH="verify/oscal-lane/verify-oscal-lane.sh"; fi
WORK="$(mktemp -d)" || { echo 'FAIL: cannot capture workload lane verdicts'; exit 1; }
trap 'rm -rf "$WORK"' EXIT
result=0
wait_reason=""
record_wait() {
  local line="$1" verdict
  # Judge every party's reason before aggregation: a declared wait must not hide
  # another party's new, undeclared reason, even when a later party passes.
  if [[ "$line" == SKIP:* ]] && verdict="$("$PY" "$ROOT/talk/truth_manifest.py" judge "$ROOT/talk/verify-manifest.txt" "$CHECK_PATH" "$line")"; then
    wait_reason="$line"
    [ "$result" = 1 ] || result=3
  else
    echo "FAIL: ${party}: undeclared workload lane wait: ${line}"
    result=1
  fi
}
for party in driftwood tuppence ludlow; do
  adopter="${ROOT}/.estate-clone/${party}"
  for instrument in "$INSTRUMENT"; do
    if [ ! -f "${adopter}/drift/${instrument}" ]; then
      line="SKIP: ${party} has no ${instrument}; ticket 155's instrument has not reached this checkout"
      echo "$line"; record_wait "$line"; continue
    fi
    echo "==> ${party}: ${instrument}"
    "$PY" "${adopter}/drift/${instrument}" selfcheck
    rc=$?
    if [ "$rc" != 0 ]; then result=1; continue; fi
    "$PY" "${adopter}/drift/${instrument}" grade >"$WORK/grade.out" 2>&1
    rc=$?
    cat "$WORK/grade.out"
    case "$rc" in
      0) ;;
      3) record_wait "$(tail -n 1 "$WORK/grade.out")" ;;
      *) result=1 ;;
    esac
  done
done
case "$result" in
  0) echo "PASS: every party's ${INSTRUMENT} lane verdict passed" ;;
  3) echo "$wait_reason" ;;
  *) echo "FAIL: workload lane aggregation contains a failed check or undeclared wait; see party outputs above" ;;
esac
exit "$result"
