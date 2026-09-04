#!/usr/bin/env bash
# Beat: "the misuse catalogues are graded, not read: every row names a mechanism, and the gate
# goes and looks for the eco-system ones."
#
# Eco-system ticket 44, from ticket 19's resolution (re-grill 36). Three catalogues sit under
# twin/: the twin's own (misuse-catalogue.yaml), the behavioural one, and the eco-system one this
# ticket adds (ecosystem-misuse-catalogue.yaml: a publisher gaming its feed price, a regulator's
# data mispriced downstream, an adopter buying intel on a rival, the twin's valuation used in
# negotiation). Until this script none of them was graded by anything talk/verify-all.sh runs.
#
# Three things, all offline:
#   1. this script's own instrument, on planted fixtures: a blanked mechanism is refused, a
#      missing anchor fails, a row waiting on a resolved ticket fails, a row waiting on an open
#      ticket is could-not-look BY NAME, a resolved row passes; and this script's own exit
#      contract, run end to end in a scratch hub whose `twin verify` fails and which has no
#      estate clone: the run must end FAIL, never SKIP
#   2. the harness check `misuse_catalogues_load_and_every_row_names_a_mechanism`, exactly as
#      `twin verify` reports it: three files, one loader, ticket 19's four ids, the refusal bites
#   3. the four eco-system rows graded against THIS checkout: every path anchor resolves in the
#      hub or the estate clone, and a row whose cage price is decided but not built names the
#      open ticket building it (ticket 45 the switching cost, 46 the scorer party, 84 D5) rather
#      than a path that does not exist. Such a row is could-not-look by name, and becomes a FAIL
#      the day that ticket resolves and the row still says it waits.
#
# Three outcomes only:
#   PASS (exit 0)  every assertion observed true; the could-not-look rows are named on the line
#   FAIL (exit 1)  an assertion observed false
#   SKIP (exit 3)  could not look, with the reason on the last line -- and only when nothing
#                  was observed false: a FAIL from an earlier leg always wins over a later leg's
#                  could-not-look (the 2026-09-03 review found leg 3's substrate check masking a
#                  leg-2 FAIL as SKIP; `skip` now consults $fail, and leg 1 proves it)
#
# `bash verify/misuse/verify-misuse.sh selfcheck` runs leg 1 alone.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
CHECK=misuse_catalogues_load_and_every_row_names_a_mechanism

# Exit 3 only while nothing has been observed false. Once $fail is set, a could-not-look is
# reported as the FAIL it sits behind, so the gate never reads an observed-false run as SKIP.
skip() {
  if [ "${fail:-0}" -ne 0 ]; then
    echo "FAIL: an assertion above was observed false, and a later leg could not look: $*"
    exit 1
  fi
  echo "SKIP: $*"; exit 3
}

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || skip "no $ROOT/.venv and python3 lacks pyyaml; the twin package cannot be imported"
fi
[ -f "$ROOT/twin/VERSION" ] || skip "no twin/VERSION in $ROOT; this is not a checkout of the hub"
[ -f "$ROOT/twin/ecosystem-misuse-catalogue.yaml" ] || skip "no twin/ecosystem-misuse-catalogue.yaml in $ROOT"

work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
fail=0

# grade <catalogue> <issues-dir> <estate-dir-or-empty>: one line per row, PASS/SKIP/FAIL <id>: why;
# exit 0 when something resolved and nothing failed, 1 on any FAIL, 3 when it could look at
# nothing (every row could-not-look). The grading itself is twin/misuse.py's `grade_entry`, the
# same function tests/test_misuse.py exercises; this script only maps its outcomes to exit codes.
grade() {
  CATALOGUE="$1" ISSUES="$2" ESTATE="$3" ROOT="$ROOT" "$PY" - <<'PY'
import os, sys
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
sys.path.insert(0, str(ROOT))
from twin import misuse

estate = Path(os.environ["ESTATE"]) if os.environ.get("ESTATE") else None
issues = Path(os.environ["ISSUES"])
try:
    doc = misuse.load_catalogue(Path(os.environ["CATALOGUE"]))
except misuse.MisuseError as exc:
    print(f"FAIL: {exc}")
    sys.exit(1)

outcomes = []
for entry in doc["entries"]:
    grade = misuse.grade_entry(
        entry, root=ROOT, estate=estate,
        ticket_status=lambda number: misuse.ecosystem_ticket_status(number, issues),
    )
    label = {misuse.PASS: "PASS", misuse.FAIL: "FAIL", misuse.COULD_NOT_LOOK: "SKIP"}[grade.outcome]
    print(f"{label} {grade.reason}")
    outcomes.append(grade)

failed = [g for g in outcomes if g.outcome == misuse.FAIL]
unlooked = [g for g in outcomes if g.outcome == misuse.COULD_NOT_LOOK]
resolved = [g for g in outcomes if g.outcome == misuse.PASS]
named = ", ".join(g.reason.split(":", 1)[0] for g in unlooked) or "none"
if failed:
    # The last line is what the gate shows, so it carries the reasons, not just the count.
    why = " | ".join(g.reason for g in failed)
    print(f"FAIL: {len(failed)} of {len(outcomes)} row(s) observed false: {why}; {len(unlooked)} could-not-look by name ({named})")
    sys.exit(1)
if not resolved:
    print(f"SKIP: no row could be looked at; {len(unlooked)} could-not-look by name ({named})")
    sys.exit(3)
print(f"PASS: {len(resolved)} of {len(outcomes)} row(s) resolve by path; {len(unlooked)} could-not-look by name ({named})")
sys.exit(0)
PY
}

# -- 1: the instrument, on planted fixtures ----------------------------------------------------
# Each fixture is built by the script rather than checked in, so the plant cannot drift from what
# the grading expects. A grader that only ever sees rows that pass cannot tell "correct" from
# "always says pass" (the twin-evals script's own reason for asserting its verdict function).
mkdir -p "$work/issues" "$work/estate/platform"
printf '# 45\n\nStatus: open\n' >"$work/issues/45-open.md"
printf '# 19\n\nStatus: resolved\n' >"$work/issues/19-resolved.md"
printf 'PRICE_KINDS = ()\n' >"$work/estate/platform/c.py"

plant() {  # plant <name> <entries-yaml>
  printf 'schema: twin.misuse-catalogue/v1\nversion: 1\nentries:\n%s\n' "$2" >"$work/$1.yaml"
}
plant blank    '  - {id: x, risk: r, mechanism: "  ", anchors: [twin/VERSION]}'
plant missing  '  - {id: x, risk: r, mechanism: m, anchors: [twin/no-such-file.py]}'
plant token    '  - {id: x, risk: r, mechanism: m, anchors: ["platform/c.py::widen_to"]}'
plant closed   '  - {id: x, risk: r, mechanism: m, waits_on: [{ticket: "19", for: p}]}'
plant unknown  '  - {id: x, risk: r, mechanism: m, waits_on: [{ticket: "999", for: p}]}'
plant bare     '  - {id: x, risk: r, mechanism: m}'
plant open     '  - {id: x, risk: r, mechanism: m, anchors: ["platform/c.py::PRICE_KINDS"], waits_on: [{ticket: "45", for: the switching price}]}'
plant resolves '  - {id: x, risk: r, mechanism: m, anchors: ["twin/VERSION", "platform/c.py::PRICE_KINDS"]}'

expect() {  # expect <fixture> <exit> <grep-for-last-line> <what>
  out="$(grade "$work/$1.yaml" "$work/issues" "$work/estate" 2>&1)"; rc=$?
  last="$(printf '%s\n' "$out" | tail -1)"
  if [ "$rc" -eq "$2" ] && printf '%s' "$last" | grep -q -- "$3"; then
    echo "PASS: selfcheck: $4 (exit $rc: $(printf '%s' "$last" | cut -c1-110))"
  else
    echo "FAIL: selfcheck: $4 expected exit $2 matching '$3', got exit $rc: $(printf '%s' "$last" | cut -c1-140)"
    fail=1
  fi
}
expect blank    1 'no mechanism'                 'a row with its mechanism blanked is refused by the loader'
expect missing  1 'no such file'                 'a row anchored to a file that does not exist fails'
expect token    1 'widen_to'                     'a row anchored to a token the file lacks fails'
expect closed   1 'resolved'                     'a row still waiting on a resolved ticket fails'
expect unknown  1 '999'                          'a row waiting on a ticket that does not exist fails'
expect bare     1 'neither a path nor the ticket' 'a row naming neither a path nor a ticket fails'
expect open     3 'could-not-look by name (x)'   'a row waiting on an open ticket is could-not-look by name'
expect resolves 0 '1 of 1 row(s) resolve'        'a row whose anchors all resolve passes'

# The script's own exit contract, end to end. A scratch hub: this script copied in, twin/ linked,
# a bin/twin that reports the harness check FAIL, and no .estate-clone or issues dir. Leg 2
# observes false; leg 3 cannot look. The run must end on a FAIL line with an exit that is neither
# 0 nor 3. The inner run is told not to plant this again, so it cannot recurse.
if [ -z "${VERIFY_MISUSE_INNER:-}" ]; then
  hub="$work/hub"
  mkdir -p "$hub/bin" "$hub/verify/misuse"
  ln -s "$ROOT/twin" "$hub/twin"
  [ -e "$ROOT/.venv" ] && ln -s "$ROOT/.venv" "$hub/.venv"
  cp "$HERE/verify-misuse.sh" "$hub/verify/misuse/verify-misuse.sh"
  printf '#!/usr/bin/env bash\necho "  11  FAIL  %s  Violated: planted by selfcheck"\nexit 1\n' "$CHECK" >"$hub/bin/twin"
  chmod +x "$hub/bin/twin"
  out="$(VERIFY_MISUSE_INNER=1 bash "$hub/verify/misuse/verify-misuse.sh" 2>&1)"; rc=$?
  last="$(printf '%s\n' "$out" | tail -1)"
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ] && printf '%s' "$last" | grep -q '^FAIL: ' \
     && printf '%s\n' "$out" | grep -q "^FAIL: $CHECK"; then
    echo "PASS: selfcheck: a leg-2 FAIL wins over leg 3's could-not-look (exit $rc: $(printf '%s' "$last" | cut -c1-110))"
  else
    echo "FAIL: selfcheck: a leg-2 FAIL must win over leg 3's could-not-look; expected an exit that is not 0 or 3 and a FAIL last line, got exit $rc: $(printf '%s' "$last" | cut -c1-140)"
    fail=1
  fi
fi

if [ "${1:-}" = "selfcheck" ]; then
  [ "$fail" -eq 0 ] && { echo "PASS: selfcheck: eight planted rows graded as their plants require, and a FAIL wins over a SKIP"; exit 0; }
  echo "FAIL: selfcheck: the grader did not grade a plant as required; see above"; exit 1
fi
[ "$fail" -eq 0 ] || { echo "FAIL: this script's own instrument is wrong; nothing below can be trusted"; exit 1; }

# -- 2: the harness check, as `twin verify` reports it -----------------------------------------
command -v git >/dev/null 2>&1 || skip "git is needed: twin verify builds its fixture repository"
det="$work/verify.out"
if bash "$ROOT/bin/twin" verify --only "$CHECK" >"$det" 2>&1 && grep -q "PASS  $CHECK" "$det"; then
  echo "PASS: $CHECK -- $(grep -o "$CHECK .*" "$det" | head -1 | sed "s/^$CHECK *//" | cut -c1-200)"
else
  echo "FAIL: $CHECK: $(grep -E "$CHECK|Violated|RESULT|Error" "$det" | head -1 | cut -c1-200)"
  fail=1
fi

# -- 3: the four eco-system rows, against this checkout ---------------------------------------
estate="$ROOT/.estate-clone"
[ -d "$estate/platform" ] && [ -d "$estate/ico" ] && [ -d "$estate/driftwood" ] \
  || skip "no assembled .estate-clone under $ROOT (platform, ico, driftwood): the rows' estate anchors cannot be looked at"
[ -d "$ROOT/.scratch/ecosystem/issues" ] || skip "no .scratch/ecosystem/issues under $ROOT: a waited-on ticket's status cannot be read"

rows="$work/rows.out"
grade "$ROOT/twin/ecosystem-misuse-catalogue.yaml" "$ROOT/.scratch/ecosystem/issues" "$estate" >"$rows" 2>&1; rc=$?
sed 's/^/  /' "$rows"
summary="$(tail -1 "$rows")"
case "$rc" in
  0) echo "PASS: eco-system rows: ${summary#PASS: }" ;;
  3) echo "FAIL: eco-system rows: every row is could-not-look, so nothing was graded: ${summary#SKIP: }"; fail=1 ;;
  *) echo "FAIL: eco-system rows: ${summary#FAIL: }"; fail=1 ;;
esac

if [ "$fail" -eq 0 ]; then
  echo "PASS: three misuse catalogues load through one loader and every row names a mechanism ($CHECK); eco-system rows: ${summary#PASS: }"
  exit 0
fi
echo "FAIL: the misuse catalogues observed false; see the lines above"
exit 1
