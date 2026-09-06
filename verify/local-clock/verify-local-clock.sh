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
#     the step's paths is refused, a live claim that omits run.headless or carries an override
#     is refused by the clock itself (the validator is told --headless), a file under the
#     step's paths that is not a *.claim.yaml is refused unchecked, a refusal deletes the PR
#     title and body the model wrote, and the validator refuses a rehearsal claim;
#   * round 4 (2026-09-06), the SERVED artefact and the OPERATION that reaches it (ticket 98):
#     the fixture adopter has a throwaway BARE ORIGIN and its local main is one commit behind
#     origin/main, as every real clone was that day. The proposal's parent must be origin/main's
#     tip, not local main's. With a stub `gh` (LOCAL_CLOCK_GH), --push must land the branch on
#     the ORIGIN with origin's main unmoved and ask gh for exactly that PR; with the stub
#     logged out, --push must refuse BEFORE the model is called (the stub touches a file when
#     it runs). The fixture's config signs every commit with a throwaway SSH key and names an
#     owner, as the real clones do: the proposal must be unsigned and authored as the clock,
#     and a model that signs anyway or names a person must be refused.
#
# The model and gh here are stand-ins (stub-claude.sh, stub-gh.sh) over throwaway repositories,
# and the verdict lines say so: this half proves what the clock DOES, not that it has run.
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
command -v ssh-keygen >/dev/null 2>&1 || { echo "SKIP: ssh-keygen is needed to make the fixture's throwaway signing key"; exit 3; }

"$PY" "$HERE/local_clock.py" selfcheck >/dev/null \
  || { echo "FAIL: local_clock.py selfcheck -- the checks do not bite their own fixtures"; exit 1; }

# --- the offline dry path: the clock end to end, stub model, stub gh, fixture adopter + origin --
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*"; exit 1; }
KEY="$TMP/throwaway_ed25519"
ssh-keygen -q -t ed25519 -N '' -C throwaway -f "$KEY" || fail "could not make a throwaway ssh key"
mkfixture() {  # a throwaway adopter checkout, a throwaway bare origin, local main ONE BEHIND origin/main
  local u="$TMP/estate/$1" o="$TMP/estate/$1.origin.git"
  mkdir -p "$u/twin/orgs/$1/scenarios"
  git init -q -b main "$u"
  echo "org: $1" >"$u/twin/signals.yaml"; echo "roles: [adopter]" >"$u/party.yaml"
  git -C "$u" add -A; git -C "$u" -c user.name=f -c user.email=f@f commit -q -m "fixture $1"
  git init -q --bare -b main "$o"
  git -C "$u" remote add origin "$o"
  echo "upstream: 1" >>"$u/twin/signals.yaml"
  git -C "$u" -c user.name=f -c user.email=f@f commit -q -am "upstream commit the clone has not pulled"
  git -C "$u" push -q -u origin main
  git -C "$u" reset -q --hard HEAD~1
  # what every real clone's config carried on 2026-09-06: an owner's name, SSH signing on
  git -C "$u" config user.name "The Owner"; git -C "$u" config user.email owner@fixture.invalid
  git -C "$u" config gpg.format ssh; git -C "$u" config user.signingkey "$KEY"; git -C "$u" config commit.gpgsign true
  git -C "$u" config tag.gpgsign true   # the owner's global config signs tags too (round 5 F6)
}
mkfixture driftwood
UNIT="$TMP/estate/driftwood"; ORIGIN="$TMP/estate/driftwood.origin.git"
SERVED="$(git -C "$ORIGIN" rev-parse main)"
[ "$(git -C "$UNIT" rev-parse main)" != "$SERVED" ] || fail "the fixture's local main is not behind origin/main"
export LOCAL_CLOCK_CLAUDE="$HERE/stub-claude.sh" LOCAL_CLOCK_HOME="$TMP/.local-clock" \
       LOCAL_CLOCK_ESTATE="$TMP/estate" LOCAL_CLOCK_PYTHON="$PY" \
       LOCAL_CLOCK_GH="$HERE/stub-gh.sh" LOCAL_CLOCK_GH_LOG="$TMP/gh-calls.log"
unset LOCAL_CLOCK_LAUNCHD
run_id() { sed -n 's/^local clock: run \([^ ]*\) .*/\1/p' "$1" | head -1; }
has_sig() { git -C "$1" cat-file commit "$2" | grep -q '^gpgsig'; }

# 0. the fixture's config really does sign, and really does name the owner (the control)
git -C "$UNIT" commit -q --allow-empty -m "control: the clone's own config signs as the owner" || fail "the control commit failed"
has_sig "$UNIT" HEAD || fail "the fixture's config did not sign the control commit, so the proof below would be empty"
[ "$(git -C "$UNIT" log -1 --format=%an HEAD)" = "The Owner" ] || fail "the control commit is not authored as the owner"
git -C "$UNIT" tag -a control-signed -m "control: the config signs tags" || fail "the control tag failed"
git -C "$UNIT" cat-file tag control-signed | grep -q 'SIGNATURE' || fail "the fixture's config did not sign the control tag, so the unsigned-tag proof below would be empty"

# 1. a live run: one stub claim committed on a local-clock/ branch, cut from ORIGIN/MAIN,
#    unsigned, authored as the clock, validated, marker written, main and origin unmoved
LOCAL_CLOCK_STUB=claim bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/live.out" 2>&1 \
  || fail "a live run with a stub model did not exit 0: $(tail -1 "$TMP/live.out")"
grep -q '^ok .*committed on local-clock/classify-' "$TMP/live.out" || fail "the live run committed no claim branch: $(grep -E '^(fail|skip)' "$TMP/live.out" | head -1)"
grep -q 'all in the twin' "$TMP/live.out" || fail "the live run's claim file was not validated"
grep -q "^base .*origin/main@${SERVED:0:7} (local main 1 behind" "$TMP/live.out" || fail "the run did not name origin/main as its base with local main 1 behind: $(grep '^base' "$TMP/live.out")"
grep -q '^this run: proposes from origin/main' "$TMP/live.out" || fail "the run did not say what it may do before it did it"
[ -f "$TMP/.local-clock/last-run.json" ] || fail "the live run left no marker"
"$PY" - "$TMP/.local-clock/last-run.json" "$SERVED" <<'PY' || fail "the live marker is not what the gate grades"
import json, sys
m = json.load(open(sys.argv[1]))
assert m["mode"] == "live" and m["injected"] is False and m["scheduled"] is False and m["citable"] is False, m
assert m["model"] == "stub-claude.sh", m["model"]          # a stand-in's marker says so
assert [s["status"] for s in m["steps"]] == ["ok"], m["steps"]
assert m["steps"][0]["branch"].startswith("local-clock/classify-"), m["steps"][0]
assert m["steps"][0]["base"] == sys.argv[2] and m["steps"][0]["signature_block"] is False, m["steps"][0]
assert "local clock" in m["steps"][0]["author"], m["steps"][0]
PY
branch="$(git -C "$UNIT" for-each-ref --format='%(refname:short)' 'refs/heads/local-clock/classify-*' | head -1)"
[ -n "$branch" ] || fail "no local-clock/classify-* branch in the fixture adopter"
[ "$(git -C "$UNIT" rev-parse "$branch~1")" = "$SERVED" ] || fail "the proposal's parent is $(git -C "$UNIT" rev-parse --short "$branch~1"), not origin/main ${SERVED:0:7}: it was cut from the clone's stale main"
[ "$(git -C "$UNIT" diff --name-only "origin/main...$branch")" = "twin/claims/$(date -u +%Y-%m-%d)-stub-classify.claim.yaml" ] \
  || fail "the branch carries something other than one claim file"
has_sig "$UNIT" "$branch" && fail "the proposal commit carries a signature block: the clone's config signed a headless model's commit as the owner"
[ "$(git -C "$UNIT" log -1 --format=%an "$branch")" = "local clock (headless model, ticket 92)" ] || fail "the proposal is authored as '$(git -C "$UNIT" log -1 --format=%an "$branch")', not the clock"
[ "$(git -C "$UNIT" rev-parse main)" != "$SERVED" ] || fail "the clock moved the adopter's local main"
[ "$(git -C "$ORIGIN" rev-parse main)" = "$SERVED" ] || fail "the clock moved origin's main"
[ -z "$(git -C "$ORIGIN" for-each-ref 'refs/heads/local-clock/')" ] || fail "a run without --push pushed something to origin"
# a marker left by a stand-in is dated, never graded as the clock having run
"$PY" "$HERE/local_clock.py" check --hub "$ROOT" --root "$LOCAL_CLOCK_HOME" --estate "$TMP/no-estate" >"$TMP/stub-marker.out" 2>&1
grep -q '^SKIP: .*stand-in model (stub-claude.sh)' "$TMP/stub-marker.out" || fail "the stand-in's marker was graded as the clock having run: $(grep -E '^(PASS|FAIL|SKIP):.*(marker|run)' "$TMP/stub-marker.out" | head -1)"

# 1b. --push, the OPERATION: the branch lands on the ORIGIN, origin's main is unmoved, gh is
#     asked for exactly that pull request, and the local worktree and branch are gone
env -u CLAUDECODE -u CLAUDE_CODE_CHILD_SESSION LOCAL_CLOCK_STUB=claim LOCAL_CLOCK_GH_STUB=ok \
  bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify --push >"$TMP/push-ok.out" 2>&1 \
  || fail "a --push run with a stub gh did not exit 0: $(grep -E '^(fail|FAIL)' "$TMP/push-ok.out" | head -1)"
prid="$(run_id "$TMP/push-ok.out")"; pbranch="local-clock/classify-$prid"
grep -q '^this run: .*push=yes' "$TMP/push-ok.out" || fail "the run did not say it could push before it ran"
landed="$(git -C "$ORIGIN" rev-parse --verify -q "refs/heads/$pbranch")" || fail "--push did not land $pbranch on the origin"
[ "$(git -C "$ORIGIN" rev-parse "$landed~1")" = "$SERVED" ] || fail "the pushed commit's parent is not origin/main"
[ "$(git -C "$ORIGIN" rev-parse main)" = "$SERVED" ] || fail "--push moved origin's main"
has_sig "$ORIGIN" "$landed" && fail "the pushed commit carries a signature block"
grep -q "^pr create --repo policy-as-versioned-driftwood/driftwood --base main --head $pbranch " "$TMP/gh-calls.log" \
  || fail "gh was not asked for the PR the clock said it opened: $(grep 'pr create' "$TMP/gh-calls.log" | head -1)"
grep -q "^ok .*opened https://github.invalid/" "$TMP/push-ok.out" || fail "the run did not report the stand-in's PR URL"
git -C "$UNIT" show-ref -q --verify "refs/heads/$pbranch" && fail "the local branch survived the push"
git -C "$UNIT" worktree list --porcelain | grep -q -- "$prid" && fail "the worktree survived the push"

# 1c. --push with gh logged out: refused BEFORE the model is called, nothing started
rm -f "$LOCAL_CLOCK_HOME/model-was-called"
n_before="$(ls -d "$LOCAL_CLOCK_HOME"/runs/*/ 2>/dev/null | wc -l | tr -d ' ')"
env -u CLAUDECODE -u CLAUDE_CODE_CHILD_SESSION LOCAL_CLOCK_STUB=claim LOCAL_CLOCK_GH_STUB=unauth \
  bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify --push >"$TMP/push-unauth.out" 2>&1
[ $? -eq 2 ] || fail "--push with a logged-out gh was not refused (exit 2): $(tail -1 "$TMP/push-unauth.out")"
tail -1 "$TMP/push-unauth.out" | grep -q '^FAIL: --push needs an authenticated gh' || fail "--push was refused for the wrong reason: $(tail -1 "$TMP/push-unauth.out")"
[ ! -e "$LOCAL_CLOCK_HOME/model-was-called" ] || fail "the model was called before the missing instrument was noticed"
[ "$(ls -d "$LOCAL_CLOCK_HOME"/runs/*/ 2>/dev/null | wc -l | tr -d ' ')" = "$n_before" ] || fail "a refused --push still started a run"

# 1d. a model that signs anyway, names a person as author, hides a signed person's commit
#     under a clean second commit (review F1), hides a declaration in history behind a clean
#     tree (F1), or makes a tag (F2) is refused with the branch kept and nothing pushed
for case in signed:signature asowner:author twocommits:"2 commit" history:"2 commit" tag:refs/tags/local-clock-v1 amend:"not the base" merge:"not the base" signoff:trailer; do
  stub="${case%%:*}"; word="${case#*:}"
  LOCAL_CLOCK_STUB="$stub" LOCAL_CLOCK_STUB_KEY="$KEY" bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/$stub.out" 2>&1 \
    && fail "a $stub proposal was admitted"
  grep '^fail' "$TMP/$stub.out" | head -1 | grep -Fq "$word" || fail "the $stub proposal was refused for the wrong reason: $(grep '^fail' "$TMP/$stub.out" | head -1)"
  grep -q 'signature: none' "$TMP/$stub.out" && fail "the clock vouched 'signature: none' for the $stub branch"
  rid="$(run_id "$TMP/$stub.out")"
  git -C "$UNIT" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$rid" || fail "the $stub proposal's branch was not kept for inspection"
  [ ! -e "$LOCAL_CLOCK_HOME/runs/$rid/classify-driftwood.pr-body.md" ] || fail "a PR body survived the $stub refusal"
done
git -C "$UNIT" cat-file tag refs/tags/local-clock-v1 | grep -q 'SIGNATURE' && fail "the tag the child made was signed: tag.gpgsign=false did not reach the child"
git -C "$UNIT" tag -d local-clock-v1 >/dev/null
# a gpgsig WORD in the message body is text: admitted (round 5 F5)
LOCAL_CLOCK_STUB=bodysig bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/bodysig.out" 2>&1 || fail "a commit whose message body says gpgsig was refused: $(grep '^fail' "$TMP/bodysig.out" | head -1)"
grep -q 'signature: none' "$TMP/bodysig.out" || fail "the bodysig run did not read the header block"
# 1d2. round 5: three routes under --push, each read on the ORIGIN (and on evil.git)
push_refused() {  # stub word -- run --push with the stub, expect refusal naming word, nothing on origin, gh not asked
  local stub="$1" word="$2" before rid
  before="$(grep -c 'pr create' "$LOCAL_CLOCK_GH_LOG" 2>/dev/null || echo 0)"
  env -u CLAUDECODE -u CLAUDE_CODE_CHILD_SESSION LOCAL_CLOCK_STUB="$stub" LOCAL_CLOCK_STUB_KEY="$KEY" LOCAL_CLOCK_GH_STUB=ok \
    bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify --push >"$TMP/$stub-push.out" 2>&1 && fail "the $stub branch was pushed"
  grep '^fail' "$TMP/$stub-push.out" | head -1 | grep -Fq "$word" || fail "the $stub run was refused for the wrong reason: $(grep '^fail' "$TMP/$stub-push.out" | head -1)"
  grep -q 'signature: none' "$TMP/$stub-push.out" && fail "the clock vouched 'signature: none' for the $stub branch"
  rid="$(run_id "$TMP/$stub-push.out")"
  git -C "$ORIGIN" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$rid" && fail "the $stub branch reached the origin"
  [ "$(grep -c 'pr create' "$LOCAL_CLOCK_GH_LOG" 2>/dev/null || echo 0)" = "$before" ] || fail "gh was asked for a PR on the refused $stub branch"
}
push_refused replace refs/replace/
# the real object behind the replace ref is the signed person's commit, read with replacement off
S="$(git -C "$UNIT" for-each-ref --format='%(refname)' refs/replace/ | head -1 | sed 's#refs/replace/##')"
[ -n "$S" ] || fail "the replace stub left no refs/replace entry"
GIT_NO_REPLACE_OBJECTS=1 git -C "$UNIT" cat-file commit "$S" | sed '/^$/q' | grep -q '^gpgsig' || fail "the replaced object is not the signed commit the stub made"
git -C "$UNIT" update-ref -d "refs/replace/$S"
push_refused hooks core.hookspath
[ ! -e "$LOCAL_CLOCK_HOME/hook-ran" ] || fail "the child's pre-push hook ran under the clock's git"
[ ! -e "$LOCAL_CLOCK_HOME/fsmonitor-ran" ] || fail "the child's fsmonitor ran under the clock's git"
git -C "$UNIT" config --unset core.hooksPath; git -C "$UNIT" config --unset core.fsmonitor   # the owner's repair by hand
push_refused remoteurl remote.origin.url
[ -z "$(git -C "$LOCAL_CLOCK_HOME/evil.git" for-each-ref)" ] || fail "evil.git received a push"
git -C "$UNIT" remote set-url origin "$ORIGIN"   # the owner's repair by hand
# 1e. the twocommits branch under --push: read the ORIGIN -- nothing landed, gh never asked
n_gh="$(grep -c 'pr create' "$LOCAL_CLOCK_GH_LOG" 2>/dev/null || echo 0)"
env -u CLAUDECODE -u CLAUDE_CODE_CHILD_SESSION LOCAL_CLOCK_STUB=twocommits LOCAL_CLOCK_STUB_KEY="$KEY" LOCAL_CLOCK_GH_STUB=ok \
  bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify --push >"$TMP/twocommits-push.out" 2>&1 && fail "a two-commit branch with a signed person's commit was pushed"
trid="$(run_id "$TMP/twocommits-push.out")"
git -C "$ORIGIN" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$trid" && fail "the two-commit branch reached the origin"
[ "$(grep -c 'pr create' "$LOCAL_CLOCK_GH_LOG" 2>/dev/null || echo 0)" = "$n_gh" ] || fail "gh was asked for a PR on the refused two-commit branch"
grep -q '"commits": 2' "$LOCAL_CLOCK_HOME/runs/$trid/steps.jsonl" || fail "the refusal did not record the commit count"
# 1f. a nested clock (a child that inherited LOCAL_CLOCK_STEP) is refused before anything starts
n_before="$(ls -d "$LOCAL_CLOCK_HOME"/runs/*/ 2>/dev/null | wc -l | tr -d ' ')"
LOCAL_CLOCK_STEP=classify LOCAL_CLOCK_RUN_DIR="$TMP/outer" LOCAL_CLOCK_STUB=claim bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/nested.out" 2>&1
[ $? -eq 2 ] && tail -1 "$TMP/nested.out" | grep -q '^FAIL: a nested clock is refused' || fail "a nested clock was not refused: $(tail -1 "$TMP/nested.out")"
[ "$(ls -d "$LOCAL_CLOCK_HOME"/runs/*/ 2>/dev/null | wc -l | tr -d ' ')" = "$n_before" ] || fail "a nested clock started a run"

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
# the gate's scan reads that branch without checking it out: counted as a rehearsal, never a FAIL
"$PY" "$HERE/local_clock.py" check --hub "$ROOT" --root "$TMP/no-marker" --estate "$TMP/estate" >"$TMP/scan.out" 2>&1
grep -q 'note: 1 rehearsal branch(es) in the checkouts, 1 carrying injected: true by design' "$TMP/scan.out" || fail "the rehearsal branch was not counted by the scan: $(grep -E 'rehearsal|FAIL' "$TMP/scan.out" | head -2)"
grep -q '^FAIL:' "$TMP/scan.out" && fail "the scan failed the fixture: $(grep '^FAIL:' "$TMP/scan.out" | head -1)"
grep -Eq '^PASS: .*origin/main of [0-9]+ \(oldest last updated [0-9]+h ago' "$TMP/scan.out" || fail "the scan did not print its served-ref count and age as numbers: $(grep '^PASS:.*injected' "$TMP/scan.out")"
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
# 3b. a live claim that omits run.headless and carries an override -- the skill's own worked
# example, committed as if a model had written it -- fails the step: the no-override invariant
# is checked by the clock (--headless to the validator), not declared by the model. The branch
# is kept and the clock's "no override is claimed" PR body is never written.
LOCAL_CLOCK_STUB=example bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/example.out" 2>&1 && fail "a live claim with an override and no headless mark was admitted"
grep -Eq '^fail .*headless' "$TMP/example.out" || fail "the unmarked claim was refused for the wrong reason: $(grep '^fail' "$TMP/example.out" | head -1)"
erid="$(sed -n 's/^local clock: run \([^ ]*\) .*/\1/p' "$TMP/example.out" | head -1)"
[ -n "$erid" ] || fail "the example run printed no run id"
[ ! -e "$TMP/.local-clock/runs/$erid/classify-driftwood.pr-body.md" ] || fail "the clock wrote a PR body for a claim it refused"
git -C "$TMP/estate/driftwood" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$erid" || fail "the refused claim's branch was not kept for inspection"
grep -q '"status": "fail"' "$TMP/.local-clock/runs/$erid/steps.jsonl" || fail "the refused claim was not recorded as fail"
# and the validator, told --headless, refuses the same file by itself, for both reasons
"$PY" "$ROOT/.claude/skills/classify-and-judge/assets/validate_claim.py" "$ROOT/.claude/skills/classify-and-judge/assets/example-claim.yaml" --twin "$ROOT" --headless >"$TMP/headless.out" 2>&1 \
  && fail "validate_claim.py --headless ACCEPTED the worked example, which carries an override and no headless mark"
grep -q 'run.headless' "$TMP/headless.out" || fail "validate_claim.py --headless did not name the missing headless mark"
grep -q 'override from a headless run' "$TMP/headless.out" || fail "validate_claim.py --headless did not refuse the override"
# 3c. the same worked example committed under a name that is not *.claim.yaml, with a PR title
# and body the model wrote itself -- fails the step unchecked: a file under the step's paths
# the clock has no check for is not proposed, the branch is kept, and the model's own title
# and body are deleted so nothing in the run directory says "no override is claimed"
LOCAL_CLOCK_STUB=misnamed bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step classify >"$TMP/misnamed.out" 2>&1 && fail "a file under twin/claims that is not a *.claim.yaml was admitted unchecked"
grep -Eq '^fail .*is not a \*\.claim\.yaml' "$TMP/misnamed.out" || fail "the misnamed file was refused for the wrong reason: $(grep '^fail' "$TMP/misnamed.out" | head -1)"
mrid="$(sed -n 's/^local clock: run \([^ ]*\) .*/\1/p' "$TMP/misnamed.out" | head -1)"
[ -n "$mrid" ] || fail "the misnamed run printed no run id"
[ ! -e "$TMP/.local-clock/runs/$mrid/classify-driftwood.pr-body.md" ] || fail "the model's PR body survived the refusal"
[ ! -e "$TMP/.local-clock/runs/$mrid/classify-driftwood.pr-title" ] || fail "the model's PR title survived the refusal"
# (the rendered prompt *.system.md carries the phrase as the instruction to the model, and the
# transcript *.claude.json is the model's words; every other file in the run dir is the clock's)
said="$(grep -rli 'no override is claimed' "$TMP/.local-clock/runs/$mrid" | grep -Ev '\.(system\.md|claude\.json|claude\.err)$' | head -1)"
[ -z "$said" ] || fail "a file the clock wrote for the refused run still says no override is claimed: $said"
git -C "$TMP/estate/driftwood" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$mrid" || fail "the misnamed file's branch was not kept for inspection"
grep -q '"status": "fail"' "$TMP/.local-clock/runs/$mrid/steps.jsonl" || fail "the misnamed file was not recorded as fail"

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
[ "$n_runs" -eq 22 ] || fail "22 runs were started (live, push, signed, asowner, twocommits, history, tag, amend, merge, signoff, bodysig, replace-push, hooks-push, remoteurl-push, twocommits-push, rehearsal, leak, dirty, example, misnamed, nothing, dry; the refused --push and the nested clock started none) and $n_runs run directories exist: run ids collided or a refusal started a run"
# the derive step (ticket 93's seam) is recorded as skipped by name until its skill ships, and
# its row declares where its files go, what they are named and which validator checks them
LOCAL_CLOCK_STUB=nothing bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive >"$TMP/derive.out" 2>&1
grep -q 'derive-driftwood' "$TMP/derive.out" || fail "the derive step is not in the steps table"
bash "$ROOT/talk/local-clock.sh" --list-steps | grep -E '^derive ' | grep -q 'assets/validate_' || fail "the derive row names no validator: ticket 93 has no seam to fill"
echo "PASS: offline, with stub-claude.sh and stub-gh.sh standing in over a throwaway adopter and a throwaway bare origin (a fixture, not the clock having run) -- the proposal is cut from origin/main with local main 1 behind, is one commit, unsigned, authored and committed as the clock although the config signs as the owner, --push lands it on the origin with main unmoved and asks gh for that PR, --push with gh logged out refuses before any model call, a signed or person-authored proposal, a two-commit branch hiding either behind a clean tip, a git replace standing a clean double before a signed commit, a hook or fsmonitor or remote written into the unit's config (the hook never ran, evil.git got nothing), an amended base or merge-shaped commit, a trailer naming a person, a tag the child made and a nested clock are each refused, a rehearsal is stamped, marked, counted by the scan and refused by the validator, a declaration, unfinished work, a file that is not a *.claim.yaml or a claim without the headless mark is refused with the model's PR body deleted, and a nothing run or a dry run leaves no worktree or branch"

# --- the real machine: the script, README, marker, leak scan, truth log, template --------------
unset LOCAL_CLOCK_CLAUDE LOCAL_CLOCK_HOME LOCAL_CLOCK_ESTATE LOCAL_CLOCK_GH LOCAL_CLOCK_GH_LOG
[ -d "$ROOT/.estate-clone/platform" ] || bash "$ROOT/clone-estate.sh" >/dev/null \
  || { echo "FAIL: could not assemble .estate-clone/"; exit 1; }
log="$(mktemp)"; trap 'rm -rf "$TMP" "$log"' EXIT
# the helper's per-check lines are indented: the verdict below is the one last line
"$PY" "$HERE/local_clock.py" check --hub "$ROOT" | tee "$log" | sed 's/^/    /'
rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: the local clock exists with its README, its last run (by claude, not a stand-in) left a dated marker inside its window, no injected signal is on HEAD or origin/main of any checkout or on a live local-clock branch, and the launchd template holds no credential";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)";;
  *) echo "FAIL: $(grep -c '^FAIL:' "$log") local-clock check(s) observed false";;
esac
exit "$rc"
