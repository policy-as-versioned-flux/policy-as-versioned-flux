#!/usr/bin/env bash
# Beat: "an adopter may sense a role, never a person -- and the gate goes and looks at what each
# adopter actually serves."
#
# Eco-system ticket 31, from ticket 19's resolution ("covert sensing excluded, role-not-person
# signatures"). All three adopters already SAY it, in the note on their own
# `bus-factor-key-person` scenario. Until this script nothing graded the saying, and no rule
# existed for what an adopter could sense if it ever wanted to: `twin/ethics_gate.py` walks a
# ladder but never looks at what a sensor READS, never reads a DPIA record, never asks whether
# the sensed party was told, and knows nothing of the adopter's own people register.
#
# `twin/sensor-admission.yaml` is the rule; `twin/sensor_admission.py` walks it. This script
# runs both legs:
#
#   1. the rules, on planted records and three planted single-unit estates whose served ref is a
#      real refs/remotes/origin/main -- an employee id, a missing DPIA, a cohort reading, a
#      missing notice, an unregistered role, an unnamed sensor and a field outside the closed set
#      are each refused BY NAME, and the one admissible sensor is admitted. A grader only ever
#      run against material that passes it proves nothing.
#   2. the estate, at the SERVED artefact: every fact is read with `git show origin/main:<path>`
#      in the fetched clone, never the working tree, because an uncommitted admission record is
#      not one an adopter has published.
#
# WHAT IT SAYS TODAY. No adopter declares a sensor admission, so leg 2 grades three scenario
# notes and three people registers and then COUNTS what it could not look at. That is a SKIP with
# the counts printed, never a pass: "0 admission decisions could be graded" is the honest line,
# and the day an adopter publishes twin/orgs/<org>/sensor-admissions/<sensor>.yaml this script
# grades it and can pass. Nothing here plants an admission record into an adopter: a DPIA is a
# record of an act a controller performed, and writing one into a demonstration adopter would be
# a faked observation.
#
# Exit 0 observed true; 1 observed false; 3 could not look, reason on the last line.
# Offline: reads committed refs only, and fetches nothing.
#
#   bash verify/sensor-admission/verify-sensor-admission.sh            both legs
#   bash verify/sensor-admission/verify-sensor-admission.sh selfcheck  leg 1 alone
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no $ROOT/.venv and python3 lacks pyyaml; the twin package cannot be imported"; exit 3; }
fi
[ -f "$ROOT/twin/sensor-admission.yaml" ] || { echo "SKIP: no twin/sensor-admission.yaml in $ROOT; this is not a checkout of the hub"; exit 3; }

# -- 1: the rules, on planted material ----------------------------------------------------------
self="$(mktemp)"; trap 'rm -f "$self"' EXIT
if ! (cd "$ROOT" && "$PY" -m twin.sensor_admission --selfcheck) >"$self" 2>&1; then
  sed 's/^/  /' "$self"
  echo "FAIL: twin/sensor_admission.py --selfcheck: the planted cases no longer grade as planted"
  exit 1
fi
sed 's/^/  /' "$self"

if [ "${1:-}" = "selfcheck" ]; then
  echo "PASS: $(tail -1 "$self" | cut -c7-)"
  exit 0
fi

# -- 2: the estate, at the served artefact ------------------------------------------------------
ESTATE="${PAVC_ESTATE_CLONE:-$ROOT/.estate-clone}"
[ -d "$ESTATE" ] || { echo "SKIP: no $ESTATE/ -- run ./clone-estate.sh first, so origin/main can be read for each adopter"; exit 3; }

# Printed on every run, not only in this header: what this check does NOT observe. Ticket 31
# built a rule and a grader, and no sensing substrate exists anywhere in this estate.
echo "  LIMIT: this run grades the RULE and any admission record an adopter serves. Nothing here"
echo "  LIMIT: observes a sensor running or a person; no sensing substrate exists in this estate."
echo "  LIMIT: no rule here reads English. A personal name written in plain words -- into a DPIA's"
echo "  LIMIT: lawful_basis, what_is_sensed or what_is_not_sensed, into a notice path, or as a"
echo "  LIMIT: role id -- matches no token and no value shape, and is refused by nothing. What is"
echo "  LIMIT: refused is a key the table does not declare, an identifier-SHAPED filename, id, key"
echo "  LIMIT: or value, an email address and a UK national insurance number (review F1/F2)."

log="$(mktemp)"; (cd "$ROOT" && "$PY" -m twin.sensor_admission "$ESTATE") | tee "$log"; rc=${PIPESTATUS[0]}
last="$(tail -1 "$log")"
rm -f "$log"
case "$rc" in
  0) echo "PASS: ${last#PASS: }"; exit 0;;
  3) echo "SKIP: ${last#SKIP: }"; exit 3;;
  *) echo "FAIL: ${last#FAIL: }"; exit 1;;
esac
