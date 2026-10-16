#!/usr/bin/env bash
# Grade the clock's provenance, workflow shape, and protected-default delivery mechanism.
# The real guard, record and cage shell run over disposable Git remotes whose default branch
# rejects every direct push. A fixture gh opens a pending PR only; a separate exact-head review
# model attempts a normal two-parent merge preserving the original clock commit and source parent.
# Log/capture overlap produces a real merge conflict while the durable ref/PR and main stay intact;
# the missing citable line remains red until recovery. Feature runs record nothing;
# forged eligibility, declarations, PR refusal, delivery collision, shallow history and missing
# default-branch identity each have explicit refusal cases.
#
# Fixture limits are printed: commits are unsigned and the token is synthetic. This grades the
# Git mechanism and exact workflow shell, never genuine signing or GitHub authorization. Fixture
# TRUTH lines are dated 1970, name their synthetic source commit, and remain in disposable repos.
# FAIL, rather than could-not-look, when repository-local provenance or mechanism cannot be read.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
WORKFLOW="$ROOT/.github/workflows/truth.yml"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
bad=0
note() { echo "  !! $*"; bad=$((bad + 1)); }
ok()   { echo "  ok   $*"; }

PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "FAIL: no python3 to read $WORKFLOW with; a gate that cannot read the workflow it grades is red, not a could-not-look"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "FAIL: no git; the mechanism this grades IS git's, so there is nothing to measure with"; exit 1; }
[ -f "$WORKFLOW" ] || { echo "FAIL: $WORKFLOW is missing"; exit 1; }

# ---------------------------------------------------------------- 0. the grader can fail
say "0. the pure half grades planted data as documented"
"$PY" "$HERE/can_record.py" selfcheck || note "can_record.py selfcheck did not pass"

# ---------------------------------------------------------------- 1. the record
say "1. every TRUTH line in talk/truth.log was ADDED by a run that could record it"
if [ "$(git -C "$ROOT" rev-parse --is-shallow-repository 2>/dev/null)" != false ]; then
  note "this checkout is shallow (or is not a git repository), so the commit that added a line is not in this history, every line would attribute to the graft boundary and the log would read clean for the wrong reason"
else
  "$PY" "$HERE/can_record.py" log "$ROOT" || note "talk/truth.log carries a line no run recorded (above)"
fi

say "1b. no citable TRUTH line is stranded on a branch that merged without it"
"$PY" "$HERE/can_record.py" stranded "$ROOT" \
  || note "a clock line that measured a tree on the default branch has not reached that branch's log (above); pending delivery is not exempt. Recover the clock's own original commit through reviewed integration, preserving its identity, signature and exact line; never type a replacement observation"

# ---------------------------------------------------------------- 2. the shape
say "2. truth.yml still has the shape ticket 100 decided"
if "$PY" "$HERE/can_record.py" shape "$WORKFLOW"; then
  ok "the guard runs before measurement; the cage publishes its original source-parent object on the exact run/attempt pending ref without producer integration, direct default-branch push or self-merge"
else
  note "truth.yml no longer has the shape (above)"
fi

# ---------------------------------------------------------------- 3. the mechanism
say "3. actual workflow shell: durable original publication precedes separate review and conflicts stay pending"
"$PY" "$HERE/can_record.py" delivery "$WORKFLOW" \
  || note "the actual guard, record or cage violated protected-default delivery (above)"

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: recorded TRUTH lines retain clock provenance; default-branch measurements durably publish their original source-parent commit before separate review; a normal merge preserves it, while real log/capture conflicts retain the exact pending ref and missing-line failure without claiming recording; branch and unsafe delivery cases refuse as named"
  exit 0
fi
echo "FAIL: $bad fault(s) -- the clock's recording provenance or protected-default delivery does not hold"
exit 1
