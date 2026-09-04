#!/usr/bin/env bash
# Ecosystem ticket 92: the local clock, graded. The eco-system's third clock runs on the owner's
# machine (talk/local-clock.sh under launchd) because the model-backed steps can only run inside
# Claude Code there (ticket 75 Q10). This script asks:
#
#   * does talk/local-clock.sh exist, and does its README name exactly the flags --help prints;
#   * did the last run leave a dated marker (.local-clock/last-run.json), and has a scheduled
#     run stopped (older than its period plus a day of slack)? On a machine that is not the
#     owner's -- the GitHub runner -- there is no marker and that is could-not-look, not false;
#   * did any injected (world-simulator) signal reach a citable path: every committed envelope,
#     claim, observation or capture in the hub and the eight units is scanned for
#     `injected: true`, and talk/truth.log carries no run=local TRUTH line since the local clock
#     existed;
#   * does the launchd template hold no credential and log only under the ignored run root;
#   * and, offline and with no token, does the clock itself behave: run end to end against a
#     fixture adopter with a stub `claude`, a live run commits one claim on a branch and leaves
#     the marker, a rehearsal (--inject) stamps the signal and marks the claim, a commit outside
#     the step's paths is refused, and the validator refuses a rehearsal claim.
#
# Exit 0 observed true; 3 could not look, with the reason on the last line; 1 observed false.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
command -v git >/dev/null 2>&1 || { echo "SKIP: git is needed to make the fixture adopter"; exit 3; }

"$PY" "$HERE/local_clock.py" selfcheck >/dev/null \
  || { echo "FAIL: local_clock.py selfcheck -- the checks do not bite their own fixtures"; exit 1; }

# --- the offline dry path: the clock end to end, stub model, fixture adopter ------------------
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*"; exit 1; }
mkfixture() {  # a throwaway adopter checkout with a main branch and a twin/ overlay
  local u="$TMP/estate/$1"
  mkdir -p "$u/twin/orgs/$1/scenarios"
  git init -q -b main "$u"
  echo "org: $1" >"$u/twin/signals.yaml"; echo "roles: [adopter]" >"$u/party.yaml"
  git -C "$u" add -A; git -C "$u" -c user.name=f -c user.email=f@f commit -q -m "fixture $1"
}
mkfixture driftwood
export LOCAL_CLOCK_CLAUDE="$HERE/stub-claude.sh" LOCAL_CLOCK_HOME="$TMP/.local-clock" \
       LOCAL_CLOCK_ESTATE="$TMP/estate" LOCAL_CLOCK_PYTHON="$PY"
unset LOCAL_CLOCK_LAUNCHD

# 1. a live run: one stub claim committed on a local-clock/ branch, validated, marker written
LOCAL_CLOCK_STUB=claim bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/live.out" 2>&1 \
  || fail "a live run with a stub model did not exit 0: $(tail -1 "$TMP/live.out")"
grep -q '^ok .*committed on local-clock/classify-' "$TMP/live.out" || fail "the live run committed no claim branch: $(grep -E '^(fail|skip)' "$TMP/live.out" | head -1)"
grep -q 'all in the twin' "$TMP/live.out" || fail "the live run's claim file was not validated"
[ -f "$TMP/.local-clock/last-run.json" ] || fail "the live run left no marker"
"$PY" - "$TMP/.local-clock/last-run.json" <<'PY' || fail "the live marker is not what the gate grades"
import json, sys
m = json.load(open(sys.argv[1]))
assert m["mode"] == "live" and m["injected"] is False and m["scheduled"] is False and m["citable"] is False, m
assert [s["status"] for s in m["steps"]] == ["ok"], m["steps"]
assert m["steps"][0]["branch"].startswith("local-clock/classify-"), m["steps"][0]
PY
branch="$(git -C "$TMP/estate/driftwood" for-each-ref --format='%(refname:short)' 'refs/heads/local-clock/classify-*' | head -1)"
[ -n "$branch" ] || fail "no local-clock/classify-* branch in the fixture adopter"
[ "$(git -C "$TMP/estate/driftwood" diff --name-only "main...$branch")" = "twin/claims/$(date -u +%Y-%m-%d)-stub-classify.claim.yaml" ] \
  || fail "the branch carries something other than one claim file"
[ "$(git -C "$TMP/estate/driftwood" rev-parse main)" = "$(git -C "$TMP/estate/driftwood" rev-parse HEAD)" ] || fail "the clock moved the adopter's main"

# 2. a rehearsal: the signal is stamped under the run root only, the claim says injected, --push refused
cat >"$TMP/signal.yaml" <<'EOF'
date: '2026-09-03'
kind: headline
statement: rehearsal -- the niobium supply shock from driftwood's own scenario library
source: twin/orgs/driftwood/scenarios/niobium-supply-shock-2026.yaml
EOF
LOCAL_CLOCK_STUB=claim bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify --inject "$TMP/signal.yaml" >"$TMP/rehearsal.out" 2>&1 \
  || fail "a rehearsal run did not exit 0: $(tail -1 "$TMP/rehearsal.out")"
grep -q 'is marked injected and the validator refused it' "$TMP/rehearsal.out" || fail "the clock did not prove the validator refuses its rehearsal claim: $(grep -E '^(fail|ok)' "$TMP/rehearsal.out" | head -1)"
grep -q '"mode": "rehearsal"' "$TMP/.local-clock/last-run.json" || fail "the rehearsal marker does not say rehearsal"
inj="$(ls "$TMP"/.local-clock/runs/*/injected-signal.json | tail -1)"
grep -q '"injected": true' "$inj" || fail "the injected envelope is not stamped"
rbranch="$(git -C "$TMP/estate/driftwood" for-each-ref --format='%(refname:short)' 'refs/heads/local-clock/rehearsal/*' | head -1)"
[ -n "$rbranch" ] || fail "the rehearsal branch is not named rehearsal"
git -C "$TMP/estate/driftwood" show "$rbranch:twin/claims/$(date -u +%Y-%m-%d)-stub-classify.claim.yaml" >"$TMP/rehearsal.claim.yaml"
"$PY" "$ROOT/.claude/skills/classify-and-judge/assets/validate_claim.py" "$TMP/rehearsal.claim.yaml" --twin "$ROOT" >"$TMP/validate.out" 2>&1 \
  && fail "the claim validator ACCEPTED a rehearsal claim marked injected"
grep -q 'rehearsal' "$TMP/validate.out" || fail "the validator refused the rehearsal claim for the wrong reason: $(tail -1 "$TMP/validate.out")"
# (CLAUDECODE unset for this one call: inside a Claude Code session --push is refused earlier,
# for the other reason, and this line is about the rehearsal refusal)
env -u CLAUDECODE bash "$ROOT/talk/local-clock.sh" --adopter driftwood --inject "$TMP/signal.yaml" --push >"$TMP/push.out" 2>&1 && fail "--push was admitted on a rehearsal"
grep -q 'refused on a rehearsal' "$TMP/push.out" || fail "--push on a rehearsal was refused for the wrong reason: $(tail -1 "$TMP/push.out")"
CLAUDECODE=1 bash "$ROOT/talk/local-clock.sh" --adopter driftwood --push >"$TMP/push2.out" 2>&1 && fail "--push was admitted inside a Claude Code session"
grep -q 'refused inside a Claude Code session' "$TMP/push2.out" || fail "--push in a session was refused for the wrong reason"
"$PY" "$HERE/local_clock.py" stamp --signal "$TMP/signal.yaml" --out "$TMP/estate/driftwood/observations/x.json" --root "$LOCAL_CLOCK_HOME" >/dev/null 2>&1 \
  && fail "the stamp wrote an injected signal onto a citable path"

# 3. a commit outside the step's paths is refused, and uncommitted work is refused
LOCAL_CLOCK_STUB=leak bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/leak.out" 2>&1 && fail "a commit carrying composed/x.yaml was admitted"
grep -q 'outside this step' "$TMP/leak.out" || fail "the declaration was refused for the wrong reason: $(grep '^fail' "$TMP/leak.out" | head -1)"
LOCAL_CLOCK_STUB=dirty bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/dirty.out" 2>&1 && fail "uncommitted work was admitted"
grep -q 'uncommitted changes' "$TMP/dirty.out" || fail "uncommitted work was refused for the wrong reason"

# 4. a run that proposes nothing, and a dry run, leave no worktree and no branch behind -- as a
# fact in the fixture, not as a sentence in the output. Runs are told apart by run id, which is
# unique even when two start in the same second (the runs above are back to back).
left_nothing() {  # out-file what -- the run's worktree, branch and directory are gone
  local rid
  rid="$(sed -n 's/^local clock: run \([^ ]*\) .*/\1/p' "$1" | head -1)"
  [ -n "$rid" ] || fail "the $2 run printed no run id: $(head -1 "$1")"
  grep -q 'worktree and branch removed' "$1" || fail "the $2 run did not report its cleanup: $(grep -E '^(fail|warn)' "$1" | head -1)"
  git -C "$TMP/estate/driftwood" worktree list --porcelain | grep -q -- "$rid" && fail "the $2 run left its worktree registered ($rid)"
  git -C "$TMP/estate/driftwood" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$rid" && fail "the $2 run left its branch ($rid)"
  [ -z "$(ls -d "$TMP/estate/driftwood/.work/local-clock/$rid-"* 2>/dev/null)" ] || fail "the $2 run left a directory under .work/local-clock ($rid)"
  [ "$(wc -l <"$TMP/.local-clock/runs/$rid/steps.jsonl")" -eq 1 ] || fail "the $2 run's steps.jsonl holds another run's steps"
}
LOCAL_CLOCK_STUB=nothing bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/nothing.out" 2>&1 || fail "a run with nothing to propose did not exit 0: $(grep -E '^fail' "$TMP/nothing.out" | head -1)"
grep -q 'nothing to propose' "$TMP/nothing.out" || fail "nothing-to-propose was not recorded"
left_nothing "$TMP/nothing.out" nothing-to-propose
bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify --dry-run >"$TMP/dry.out" 2>&1 || fail "a dry run did not exit 0: $(grep -E '^fail' "$TMP/dry.out" | head -1)"
grep -q '^dry .*would run' "$TMP/dry.out" || fail "the dry run did not print the command it would run"
left_nothing "$TMP/dry.out" dry
n_runs="$(ls -d "$TMP"/.local-clock/runs/*/ | wc -l | tr -d ' ')"
[ "$n_runs" -eq 6 ] || fail "6 runs were started (live, rehearsal, leak, dirty, nothing, dry) and $n_runs run directories exist: run ids collided"
# the derive step (ticket 93's seam) is recorded as skipped by name until its skill ships
LOCAL_CLOCK_STUB=nothing bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive >"$TMP/derive.out" 2>&1
grep -q 'derive-driftwood' "$TMP/derive.out" || fail "the derive step is not in the steps table"
echo "PASS: offline -- with a stub model the clock commits one claim on a branch and leaves the marker, a rehearsal is stamped, marked and refused by the validator, a declaration or unfinished work is refused, and a nothing run or a dry run leaves no worktree or branch"

# --- the real machine: the script, README, marker, leak scan, truth log, template --------------
unset LOCAL_CLOCK_CLAUDE LOCAL_CLOCK_HOME LOCAL_CLOCK_ESTATE
[ -d "$ROOT/.estate-clone/platform" ] || bash "$ROOT/clone-estate.sh" >/dev/null \
  || { echo "FAIL: could not assemble .estate-clone/"; exit 1; }
log="$(mktemp)"; trap 'rm -rf "$TMP" "$log"' EXIT
# the helper's per-check lines are indented: the verdict below is the one last line
"$PY" "$HERE/local_clock.py" check --hub "$ROOT" | tee "$log" | sed 's/^/    /'
rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: the local clock exists with its README, its last run left a dated marker inside its window, no injected signal is on any citable path, and the launchd template holds no credential";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") local-clock check(s) observed false";;
esac
exit "$rc"
