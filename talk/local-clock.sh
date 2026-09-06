#!/usr/bin/env bash
# talk/local-clock.sh -- the local clock (ecosystem ticket 92; ticket 75 Q10, owner-reasoned).
#
# The eco-system's third clock. truth.yml on the hub and the per-unit fetch / propose-tier /
# twin-sweep clocks run on GitHub and never call a model (ADR-0024). The steps that NEED a model
# can only run inside Claude Code on the owner's machine, because no tokens exist anywhere else.
# This script runs those steps, in order, from this machine -- by hand or from launchd
# (talk/local-clock.plist) -- and every result lands as a branch plus a pull-request body, never
# as a commit to main. Read talk/local-clock.README.md before running it.
#
# Each step calls Claude Code non-interactively with a NAMED SKILL:
#   claude -p "/<skill> <adopter>" --max-turns N --permission-mode acceptEdits --allowedTools ...
# with the hub's own PreToolUse hook (twin/enact_guard.py) in force, under TWIN_ENACT_MODE=operations
# (the refusing mode: no merge, no enactment push -- the guard ADMITS `git tag` and
# `git update-ref`, so any ref the child makes or moves besides its own branch is refused by
# this script's read-back, below), and with `gh` kept out of the child's
# allowed tools altogether. What the model may do is read, write the adopter's worktree, commit
# on the branch this script made for it, and stop. This script then reads what it committed,
# refuses anything outside the step's allowed paths, refuses any file under them that is not a
# *.claim.yaml, validates every claim file with the validator told --headless (the file must
# say run.headless: true and carry no override; the model's own say-so is not what the
# no-override invariant rests on), and either pushes and opens the PR (--push, the owner's
# hand, never from inside a Claude Code session) or prints the command for the owner to run.
# A refused step keeps its branch and deletes the PR title and body the model may have written.
#
# The steps table below is the seam ticket 93 stacks on: add a row, ship the skill, and the
# clock runs it. A row whose skill is not in .claude/skills yet is recorded as skipped, by name.
#
# Round 4 (2026-09-06), the SERVED artefact and the OPERATION that reaches it (ticket 98's
# rule; ticket 100's "say what you can land before you measure"):
#   * the proposal is cut from origin/main AS FETCHED NOW, never from the clone's own `main`
#     (every clone under .estate-clone was behind origin/main on 2026-09-06, by 1 to 4
#     commits; a proposal cut from local main reads a pool the served branch has moved past).
#     The run prints the base sha and how far local main lags. A fetch that fails is said so
#     and the last-fetched origin/main is used; no origin/main at all refuses the step
#     (a missing instrument refuses, ADR-0020).
#   * the child commits as THE CLOCK, unsigned. The owner's GLOBAL git config (~/.gitconfig:
#     user.name, user.signingkey, commit.gpgsign=true, tag.gpgsign=true, core.hookspath), which
#     every clone and worktree inherits (the clones' own .git/config carry none of it), signs
#     every commit and tag with the owner's SSH key and names the owner; a model with nobody at
#     the keyboard may do neither. GIT_AUTHOR_*/GIT_COMMITTER_*, commit.gpgsign=false and
#     tag.gpgsign=false go into the child's environment, and the clock then READS THE BRANCH
#     back -- every commit between the base and HEAD, not HEAD alone (review F1: a signed,
#     person-authored first commit hid behind a clean second, and a declaration added then
#     deleted hid behind a clean tree diff) -- and admits exactly ONE commit, authored and
#     committed as the clock, with no signature block; anything else is refused, branch kept.
#     Any ref the child made or moved besides its branch (a tag, refs/heads/main) is refused
#     and named. The merge is the human act; the release tag is the signature that prices.
#   * round 5 (2026-09-06 re-review): the same snapshot-compare-refuse shape, widened. ALL refs
#     (a `git replace` under refs/replace/ stood a clean double before a signed commit and the
#     origin received the signed one); the unit's git CONFIG by key (a core.hooksPath the child
#     wrote ran its pre-push hook in the owner's shell under the clock's own push; a
#     core.fsmonitor ran at the clock's `git status`; a `remote set-url origin` sent the push
#     elsewhere); the admitted commit's PARENT must be the base and only the base (an amend of
#     the base or a merge-shaped commit is one clean commit that is not a proposal on
#     origin/main); trailers naming anyone but the clock; and the signature read from the
#     header block only. The clock's own git runs with GIT_NO_REPLACE_OBJECTS=1, no hooks and
#     no fsmonitor (cgit, above). CLAUDECODE and LOCAL_CLOCK_STEP/RUN_DIR are conventions a
#     child with Bash(git *) can unset (`git -c alias.x='!...' x`); what bounds a nested clock
#     is this read-back, not those variables.
#   * --push establishes its instruments BEFORE the model runs: `gh auth status` and
#     `git ls-remote origin main` for every adopter. Either failing refuses the whole run, so a
#     model call is never spent on a proposal that cannot reach its PR (before this, a run with
#     no usable gh pushed the branch and then failed to open the PR: a branch on origin with
#     nothing naming it). LOCAL_CLOCK_GH names a stand-in for tests.
#   * the marker records which binary stood as the model; a stand-in's marker is never graded
#     as the clock having run.
#
# World simulator (--inject FILE): the same run reads one dated external signal from a file (a
# headline, a market move, a regulator publish). It is stamped `injected: true` with its
# provenance, written ONLY under the run root, and the run is a rehearsal: its branch is named
# rehearsal, its claim files must carry `injected: true` (the claim validator refuses them, so
# they can never pass a gate), --push is refused, and the marker says rehearsal. Never cite one.
#
# What it writes (all under .local-clock/, gitignored). <run> is the run id: the UTC stamp plus
# a random suffix from mktemp (20260904T101500Z-a1b2c3), so two runs started in the same second
# never share a directory or a branch:
#   .local-clock/runs/<run>/       one directory per run: the rendered headless prompts, the
#                                  child's JSON transcript and stderr, PR title and body per
#                                  step, steps.jsonl, marker.json, injected-signal.json
#   .local-clock/last-run.json     the dated marker verify/local-clock/verify-local-clock.sh grades
#   .local-clock/logs/             launchd's stdout/stderr (from the plist)
#   .estate-clone/<adopter>/.work/local-clock/<run>-<step>/   the adopter worktree on the
#                                  branch local-clock/<step>-<run>, kept until pushed; a step
#                                  that proposes nothing, and a dry run, remove theirs
#
# This script never appends talk/truth.log. A local run is not citable (NORTH-STAR S5).
set -uo pipefail
HUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HUB" || exit 2

HELPER="$HUB/verify/local-clock/local_clock.py"
TEMPLATE="$HUB/talk/local-clock.headless.md"
PY="${LOCAL_CLOCK_PYTHON:-$HUB/.venv/bin/python}"; [ -x "$PY" ] || PY=python3
CLAUDE="${LOCAL_CLOCK_CLAUDE:-claude}"
GH="${LOCAL_CLOCK_GH:-gh}"
ROOT="${LOCAL_CLOCK_HOME:-$HUB/.local-clock}"
# Every git command THIS script runs goes through cgit (review round 5). GIT_NO_REPLACE_OBJECTS=1:
# a `git replace` the child made would otherwise stand a clean double in front of a signed
# commit for every read here while the origin receives the real object. core.hooksPath at a
# directory that is never created and core.fsmonitor off: a hook or monitor the child wrote
# into the unit's config must never run in the owner's shell under the clock's own git (a
# pre-push hook ran with the owner's gh on PATH and no guard when this was probed). The child's
# config writes themselves are refused by the snapshot in run_step.
NO_HOOKS="$ROOT/no-hooks"
cgit() { GIT_NO_REPLACE_OBJECTS=1 git -c core.hooksPath="$NO_HOOKS" -c core.fsmonitor=false "$@"; }
# the identity the child commits under: the clock's own, never a person's. `.invalid` is the
# reserved TLD -- it is not a mailbox and cannot be mistaken for one. No signature: nobody at
# the keyboard signed anything (the clone's own config would sign as the owner; see below).
CLOCK_AUTHOR_NAME="local clock (headless model, ticket 92)"
CLOCK_AUTHOR_EMAIL="local-clock@policy-as-versioned-flux.invalid"
ESTATE="${LOCAL_CLOCK_ESTATE:-$HUB/.estate-clone}"
MAX_TURNS="${LOCAL_CLOCK_MAX_TURNS:-80}"
PERIOD="${LOCAL_CLOCK_PERIOD_HOURS:-24}"
SCHEDULED="${LOCAL_CLOCK_LAUNCHD:-0}"

# name | skill | paths the step's commit may touch (space-separated; {adopter} is substituted)
#      | the name pattern every committed file must match | the validator, relative to the
#        skill's directory, run as `<validator> FILE --twin <hub> --headless` on every file
#      | what it is
# A row's validator is what makes its files proposable: a step whose validator is not shipped
# cannot propose a file, whatever the file says about itself. Ticket 93 owns the derive row's
# paths, pattern and validator names; they are placeholders until its skill lands.
STEPS=(
  "classify|classify-and-judge|twin/claims|*.claim.yaml|assets/validate_claim.py|the unbound pool (news, market moves) classified against the adopter's overlay: bindings and positions, grade 5, no override, one claim file on a branch"
  "derive|derive-probability|twin/orgs/{adopter}/forecasts|*.forecast.yaml|assets/validate_forecast.py|ticket 93: a probability derived from the adopter's world model and the subscribed feeds' dated series, with its basis, grade and the signals it rested on, written to the adopter's overlay; runs once .claude/skills/derive-probability/SKILL.md exists"
)
ALL_ADOPTERS="driftwood tuppence ludlow"

# The child's tools. No `gh` at all: a pull request is opened by THIS script under the owner's
# own session, after it has read what the model committed. No Task: a subagent's tool calls are
# the runner's business (twin/enact_guard.py docstring), and this run has one job.
ALLOWED_TOOLS="Read,Glob,Grep,Write,Edit,Bash(git *),Bash(python3 *),Bash(ls *),Bash(cat *),Bash(head *),Bash(wc *)"
DISALLOWED_TOOLS="Task,WebFetch,WebSearch,NotebookEdit,Bash(gh *),Bash(curl *),Bash(launchctl *)"

usage() {
  cat <<EOF
talk/local-clock.sh -- run the model-backed steps of the eco-system's clock from this machine

usage: talk/local-clock.sh [--adopter UNIT ...] [--step NAME ...] [--inject FILE] [--push] [--dry-run]
       talk/local-clock.sh --list-steps
       talk/local-clock.sh --help

  --adopter UNIT   an adopter to run the steps for (repeatable; \`all\` = $ALL_ADOPTERS).
                   default: driftwood, the teaching default
  --step NAME      run only this step (repeatable). default: every step, in order
  --inject FILE    world simulator: read one dated external signal (yaml or json with date,
                   kind, statement, optional source) and run as a REHEARSAL. Every output is
                   marked injected, --push is refused, nothing is citable
  --push           after a live step commits, push its branch to the adopter's repo and open
                   the pull request with gh. Refused inside a Claude Code session and refused
                   on a rehearsal: the push is the owner's hand
  --dry-run        make the worktrees and render the prompts, but call no model; report
                   every step as skipped
  --list-steps     print the steps table and exit
  --help           this

environment (all optional): LOCAL_CLOCK_CLAUDE (the claude binary; a stub for tests),
  LOCAL_CLOCK_HOME (run root, default <hub>/.local-clock), LOCAL_CLOCK_ESTATE (default
  <hub>/.estate-clone), LOCAL_CLOCK_MAX_TURNS ($MAX_TURNS), LOCAL_CLOCK_PERIOD_HOURS ($PERIOD),
  LOCAL_CLOCK_LAUNCHD=1 (set by the plist, so the marker says scheduled)
EOF
}

ADOPTERS=(); ONLY_STEPS=(); INJECT=""; PUSH=0; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --adopter) shift; [ $# -gt 0 ] || { echo "FAIL: --adopter needs a unit"; exit 2; }
               if [ "$1" = all ]; then for a in $ALL_ADOPTERS; do ADOPTERS+=("$a"); done; else ADOPTERS+=("$1"); fi;;
    --step) shift; [ $# -gt 0 ] || { echo "FAIL: --step needs a name"; exit 2; }; ONLY_STEPS+=("$1");;
    --inject) shift; [ $# -gt 0 ] || { echo "FAIL: --inject needs a file"; exit 2; }; INJECT="$1";;
    --push) PUSH=1;;
    --dry-run) DRY=1;;
    --list-steps) for row in "${STEPS[@]}"; do IFS='|' read -r n s p g v d <<<"$row"; printf '%-10s /%-22s %-32s %-16s %-28s %s\n' "$n" "$s" "$p" "$g" "$v" "$d"; done; exit 0;;
    --help|-h) usage; exit 0;;
    *) echo "FAIL: unknown flag $1 (see --help)"; exit 2;;
  esac
  shift
done
[ "${#ADOPTERS[@]}" -gt 0 ] || ADOPTERS=(driftwood)

[ -f "$HELPER" ] || { echo "FAIL: $HELPER is missing"; exit 2; }
[ -f "$TEMPLATE" ] || { echo "FAIL: $TEMPLATE is missing"; exit 2; }
if [ "$DRY" = 0 ] && ! command -v "$CLAUDE" >/dev/null 2>&1; then
  echo "FAIL: no claude binary at '$CLAUDE' -- install Claude Code, or set LOCAL_CLOCK_CLAUDE"; exit 2
fi
# A nested clock is refused first. A child of a running clock inherits LOCAL_CLOCK_STEP and
# LOCAL_CLOCK_RUN_DIR; the CLAUDECODE test below is a convention the owner's terminal upholds
# (`env -u CLAUDECODE` defeats it, and so can a child with python3), so the inherited variables
# are the control: a child that re-invokes the clock with --push under the owner's real gh
# stops here, whatever it did to CLAUDECODE.
if [ -n "${LOCAL_CLOCK_STEP:-}" ] || [ -n "${LOCAL_CLOCK_RUN_DIR:-}" ]; then
  echo "FAIL: a nested clock is refused -- LOCAL_CLOCK_STEP/LOCAL_CLOCK_RUN_DIR are already set, so this shell is a child of a running clock (step '${LOCAL_CLOCK_STEP:-}', run dir '${LOCAL_CLOCK_RUN_DIR:-}')"; exit 2
fi
if [ "$PUSH" = 1 ] && [ -n "${CLAUDECODE:-}" ]; then
  echo "FAIL: --push is refused inside a Claude Code session; the push to an adopter's repository is the owner's hand, from a terminal"; exit 2
fi
if [ "$PUSH" = 1 ] && [ -n "$INJECT" ]; then
  echo "FAIL: --push is refused on a rehearsal (--inject): an injected signal never leaves this machine"; exit 2
fi
# --push: establish the instruments BEFORE any model runs (ADR-0020: a missing instrument
# refuses; ticket 100: say what this run can land before it measures). The served artefact of
# a pushed step is a branch on the adopter's origin and the pull request naming it; both need
# an authenticated gh and a reachable origin with a main. Nothing below is started otherwise,
# so no model call is spent on a proposal that cannot reach its PR.
PUSH_NOTE="no: the exact push-and-PR command is printed for the owner"
if [ "$PUSH" = 1 ]; then
  command -v "$GH" >/dev/null 2>&1 || { echo "FAIL: --push needs gh and none is at '$GH' -- refused before any model runs"; exit 2; }
  if ! "$GH" auth status >/dev/null 2>&1; then
    echo "FAIL: --push needs an authenticated gh and '$GH auth status' failed (exit $?) -- refused before any model runs; log in with gh auth login, or drop --push"; exit 2
  fi
  for a in "${ADOPTERS[@]}"; do
    u="$ESTATE/$a"
    if [ ! -d "$u/.git" ] && [ ! -f "$u/.git" ]; then
      echo "FAIL: --push needs a checkout of $a at $u and there is none (run clone-estate.sh) -- refused before any model runs"; exit 2
    fi
    if ! GIT_TERMINAL_PROMPT=0 cgit -C "$u" ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
      echo "FAIL: --push needs origin of $a reachable with a main branch, and 'git ls-remote origin main' at $u failed -- refused before any model runs"; exit 2
    fi
  done
  PUSH_NOTE="yes: gh is authenticated and origin/main of [${ADOPTERS[*]}] answered ls-remote"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$ROOT/runs" "$ROOT/logs"
# mktemp makes the run id unique on the filesystem: two runs in one second (a launchd fire
# beside a run by hand, or a test running the clock back to back) get distinct directories and
# distinct branch names, and steps.jsonl is never appended across runs.
RUN_DIR="$(mktemp -d "$ROOT/runs/$STAMP-XXXXXX")" || { echo "FAIL: could not make a run directory under $ROOT/runs"; exit 2; }
RUN_ID="$(basename "$RUN_DIR")"
MODE=live; BRANCH_PREFIX="local-clock"
INJECTED_FILE=""
if [ -n "$INJECT" ]; then
  MODE=rehearsal; BRANCH_PREFIX="local-clock/rehearsal"
  INJECTED_FILE="$RUN_DIR/injected-signal.json"
  "$PY" "$HELPER" stamp --signal "$INJECT" --out "$INJECTED_FILE" --root "$ROOT" --by "talk/local-clock.sh --inject" \
    || { echo "FAIL: the injected signal was refused (see above)"; exit 2; }
fi
echo "local clock: run $RUN_ID mode=$MODE scheduled=$SCHEDULED adopters=[${ADOPTERS[*]}] run_dir=$RUN_DIR"
echo "this run: proposes from origin/main of each adopter as fetched now; commits as '$CLOCK_AUTHOR_NAME', unsigned; writes only $ROOT and .estate-clone/<adopter>/.work/local-clock; push=$PUSH_NOTE; never main, never a merge, never a tag, and never appends talk/truth.log; not citable"

record() { "$PY" "$HELPER" record --run-dir "$RUN_DIR" "$@" </dev/null; }

drop_worktree() {  # unit wt branch -- remove a step's worktree and its branch; true only when both are gone
  local unit="$1" wt="$2" branch="$3" err="$RUN_DIR/cleanup.err"
  cgit -C "$unit" worktree remove --force "$wt" 2>>"$err" \
    && cgit -C "$unit" branch -q -D "$branch" 2>>"$err" \
    && [ ! -e "$wt" ] \
    && ! cgit -C "$unit" show-ref -q --verify "refs/heads/$branch"
}

cleanup_or_fail() {  # step adopter unit wt branch status reason -- drop the worktree, record, and say what is true
  local step="$1" adopter="$2" unit="$3" wt="$4" branch="$5" status="$6" reason="$7" tag="$1-$2"
  if drop_worktree "$unit" "$wt" "$branch"; then
    echo "        $tag: worktree and branch removed"
    record --step "$step" --adopter "$adopter" --status "$status" --reason "$reason"; return 0
  fi
  echo "fail  $tag: $reason, but the worktree $wt or the branch $branch could not be removed ($(tail -1 "$RUN_DIR/cleanup.err" 2>/dev/null | cut -c1-120)); remove them by hand"
  record --step "$step" --adopter "$adopter" --status fail --reason "$reason; cleanup of $wt / $branch failed" --branch "$branch"; return 1
}

refuse() {  # step adopter branch title body reason -- a live step the clock will not propose
  # The branch is kept for inspection, never pushed. Whatever PR title or body the model wrote
  # before the refusal is deleted, so nothing in the run directory reads as a proposal or says
  # "no override is claimed" about a commit the clock refused; the child's transcript
  # (<step>-<adopter>.claude.json) still holds the model's words.
  local step="$1" adopter="$2" branch="$3" title="$4" body="$5" reason="$6"
  shift 6   # anything left is extra record fields (--base, --commits)
  rm -f "$title" "$body"
  record --step "$step" --adopter "$adopter" --status fail --reason "$reason" --branch "$branch" "$@"
  return 1
}

unit_refs() {  # unit branch -- EVERY ref (heads, tags, remotes, replace, notes, ...) but the step's own
  cgit -C "$1" for-each-ref --format='%(refname) %(objectname)' | grep -v "^refs/heads/$2 " || true
}
unit_config() {  # wt -- every config entry git reads there (system, global, local, worktree), with its file
  cgit -C "$1" config --list --show-origin 2>/dev/null | grep -v '^command line:' || true
}

render_prompt() {  # step skill adopter unit_wt branch paths out
  STEP="$1" SKILL="$2" ADOPTER="$3" UNIT_WT="$4" BRANCH="$5" PATHS="$6" OUT="$7" \
  RUN_DIR="$RUN_DIR" HUB="$HUB" ESTATE="$ESTATE" INJECTED_FILE="$INJECTED_FILE" TEMPLATE="$TEMPLATE" \
  "$PY" - <<'PY'
import json, os
text = open(os.environ["TEMPLATE"]).read()
inj = os.environ.get("INJECTED_FILE") or ""
if inj:
    block = ("## THIS IS A REHEARSAL (world simulator)\n\n"
             "An INJECTED external signal is present at `" + inj + "`:\n\n```json\n"
             + open(inj).read().strip() + "\n```\n\n"
             "Treat it as one more unbound dated statement beside the real pool. It is not in any "
             "published feed and it is NOT real. Every claim file you write MUST carry "
             "`injected: true` at its top level and `injected: true` on every claim, and its "
             "`derived_from` must NOT cite the injected signal as a pin (it has none). Nothing "
             "from this run is citable and it will never be pushed.\n")
else:
    block = "## This is a live run\n\nNo injected signal. Read only the published pool at the pinned versions.\n"
fields = {k: os.environ.get(k, "") for k in ("STEP", "SKILL", "ADOPTER", "UNIT_WT", "BRANCH", "PATHS", "RUN_DIR", "HUB", "ESTATE")}
fields["TITLE_FILE"] = os.path.join(os.environ["RUN_DIR"], f"{fields['STEP']}-{fields['ADOPTER']}.pr-title")
fields["BODY_FILE"] = os.path.join(os.environ["RUN_DIR"], f"{fields['STEP']}-{fields['ADOPTER']}.pr-body.md")
fields["INJECTED_BLOCK"] = block
for key, value in fields.items():
    text = text.replace("{{" + key + "}}", value)
open(os.environ["OUT"], "w").write(text)
PY
}

run_step() {  # step skill paths pattern validator adopter
  local step="$1" skill="$2" paths="${3//\{adopter\}/$6}" pattern="$4" validator_rel="$5" adopter="$6"
  local unit="$ESTATE/$adopter" tag="$step-$adopter"
  if [ ! -f "$HUB/.claude/skills/$skill/SKILL.md" ]; then
    echo "skip  $tag: no .claude/skills/$skill/SKILL.md yet -- the step is charted, the skill is not shipped"
    record --step "$step" --adopter "$adopter" --status skip --reason "skill $skill not shipped"; return 0
  fi
  if [ ! -d "$unit/.git" ] && [ ! -f "$unit/.git" ]; then
    echo "skip  $tag: no checkout at $unit (run clone-estate.sh)"
    record --step "$step" --adopter "$adopter" --status skip --reason "no checkout at $unit"; return 0
  fi
  # The base is the SERVED default branch, origin/main as fetched now. The clone's own `main`
  # is nobody's artefact: it lags origin by however long since somebody last pulled it, and a
  # proposal cut from it reads a pool the served branch has moved past. A fetch that fails is
  # said so and the last-fetched origin/main stands, dated by the run log; no origin/main at
  # all is a missing instrument and refuses the step.
  local base fetch_note behind ahead
  if GIT_TERMINAL_PROMPT=0 cgit -C "$unit" fetch -q origin main 2>"$RUN_DIR/$tag.fetch.err"; then
    fetch_note="fetched now"
  else
    fetch_note="fetch FAILED ($(tail -1 "$RUN_DIR/$tag.fetch.err" | cut -c1-80)); using origin/main as last fetched"
  fi
  if ! base="$(cgit -C "$unit" rev-parse --verify -q refs/remotes/origin/main)"; then
    echo "fail  $tag: no origin/main in $unit to propose against ($fetch_note) -- a missing instrument refuses; run clone-estate.sh or git fetch"
    record --step "$step" --adopter "$adopter" --status fail --reason "no origin/main to propose against"; return 1
  fi
  behind="$(cgit -C "$unit" rev-list --count main..origin/main 2>/dev/null || echo '?')"
  ahead="$(cgit -C "$unit" rev-list --count origin/main..main 2>/dev/null || echo '?')"
  echo "base  $tag: origin/main@${base:0:7} (local main $behind behind, $ahead ahead; $fetch_note)"
  local branch="$BRANCH_PREFIX/$step-$RUN_ID" wt="$unit/.work/local-clock/$RUN_ID-$step"
  mkdir -p "$unit/.work/local-clock"
  if ! cgit -C "$unit" worktree add -q "$wt" -b "$branch" "$base" 2>"$RUN_DIR/$tag.worktree.err"; then
    echo "fail  $tag: could not make a worktree on $branch from origin/main@${base:0:7} ($(tail -1 "$RUN_DIR/$tag.worktree.err"))"
    record --step "$step" --adopter "$adopter" --status fail --reason "worktree add failed" --base "$base"; return 1
  fi
  local prompt="$RUN_DIR/$tag.system.md" title="$RUN_DIR/$tag.pr-title" body="$RUN_DIR/$tag.pr-body.md"
  render_prompt "$step" "$skill" "$adopter" "$wt" "$branch" "$paths" "$prompt"

  if [ "$DRY" = 1 ]; then
    echo "dry   $tag: would run  $CLAUDE -p \"/$skill $adopter\" --max-turns $MAX_TURNS --append-system-prompt \"\$(cat $prompt)\"  (worktree $wt on $branch; prompt kept at $prompt)"
    cleanup_or_fail "$step" "$adopter" "$unit" "$wt" "$branch" skip "dry run"; return $?
  fi

  echo "run   $tag: /$skill $adopter on $branch (worktree $wt, max $MAX_TURNS turns)"
  # Every branch and tag of the unit but the step's own, before the child: after it, any ref
  # that appeared or moved is refused and named. The guard admits `git tag -a` (the owner's
  # global tag.gpgsign would sign it) and `git update-ref refs/heads/main HEAD` (which moves
  # the clone's main under the worktree); this read-back is what catches both.
  local refs_before refs_after config_before config_after origin_url origin_pushurl
  refs_before="$(unit_refs "$unit" "$branch")"
  # ... and the unit's git config, every entry with its file: Bash(git *) admits `git config`
  # and `git remote set-url`, and a hooksPath, an fsmonitor or a remote written there would run
  # under, or be pushed to by, the owner's own shell. Any key that differs afterwards is refused.
  config_before="$(unit_config "$wt")"
  origin_url="$(cgit -C "$unit" config --get remote.origin.url || true)"
  origin_pushurl="$(cgit -C "$unit" config --get remote.origin.pushurl || true)"
  # TWIN_ENACT_MODE=operations: the refusing mode for the whole child, whatever twin/ENACT_MODE
  # says today (the guard reads the environment before the file: twin/enact_guard.py). The child
  # cannot merge and cannot push an enactment repository; a tag it makes is caught above.
  # GIT_AUTHOR_* / GIT_COMMITTER_*, commit.gpgsign=false and tag.gpgsign=false: the child
  # commits as the clock, unsigned. The owner's global git config names the owner and signs
  # commits and tags with the owner's SSH key; a model with nobody at the keyboard may do
  # neither, and the clock reads the whole branch back below.
  env -u CLAUDECODE -u CLAUDE_CODE_CHILD_SESSION \
    TWIN_ENACT_MODE=operations \
    GIT_AUTHOR_NAME="$CLOCK_AUTHOR_NAME" GIT_AUTHOR_EMAIL="$CLOCK_AUTHOR_EMAIL" \
    GIT_COMMITTER_NAME="$CLOCK_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$CLOCK_AUTHOR_EMAIL" \
    GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false \
    GIT_CONFIG_KEY_1=tag.gpgsign GIT_CONFIG_VALUE_1=false \
    LOCAL_CLOCK_STEP="$step" LOCAL_CLOCK_ADOPTER="$adopter" LOCAL_CLOCK_UNIT_WT="$wt" \
    LOCAL_CLOCK_RUN_DIR="$RUN_DIR" LOCAL_CLOCK_INJECTED="$INJECTED_FILE" \
    LOCAL_CLOCK_TITLE_FILE="$title" LOCAL_CLOCK_BODY_FILE="$body" \
    "$CLAUDE" -p "/$skill $adopter" \
      --max-turns "$MAX_TURNS" --output-format json \
      --permission-mode acceptEdits \
      --allowedTools "$ALLOWED_TOOLS" --disallowedTools "$DISALLOWED_TOOLS" \
      --add-dir "$wt" \
      --append-system-prompt "$(cat "$prompt")" \
      >"$RUN_DIR/$tag.claude.json" 2>"$RUN_DIR/$tag.claude.err" </dev/null
  local rc=$?
  [ "$rc" = 0 ] || echo "warn  $tag: claude exited $rc ($(tail -1 "$RUN_DIR/$tag.claude.err" | cut -c1-120)); reading what it left anyway"

  # What did the model leave? First the unit's refs: a headless run writes one branch and
  # nothing else. Then uncommitted work is a step that did not finish. No commit is nothing to
  # propose. A commit is judged file by file against the step's allowed paths.
  local dirty changed moved changed_keys
  config_after="$(unit_config "$wt")"
  if [ "$config_after" != "$config_before" ]; then
    changed_keys="$(diff <(echo "$config_before") <(echo "$config_after") | grep -E '^[<>]' | sed $'s/^[<>] [^\t]*\t//' | cut -d= -f1 | sort -u | tr '\n' ' ')"
    echo "fail  $tag: the child changed the unit's git config: $changed_keys-- a hook, a monitor or a remote written there would run under, or be pushed to by, the owner's own shell. Branch kept at $wt, never pushed; repair the config by hand before the next run."
    refuse "$step" "$adopter" "$branch" "$title" "$body" "child changed git config: $changed_keys" --base "$base"; return 1
  fi
  refs_after="$(unit_refs "$unit" "$branch")"
  if [ "$refs_after" != "$refs_before" ]; then
    moved="$(diff <(echo "$refs_before") <(echo "$refs_after") | grep -E '^[<>]' | awk '{print $2}' | sort -u | tr '\n' ' ')"
    echo "fail  $tag: the child made or moved a ref besides its branch: $moved-- a headless run writes one branch and nothing else (a tag would carry the owner's global tag.gpgsign; refs/heads/main moving would shift the clone under the worktree). Branch kept at $wt, never pushed; remove the ref by hand."
    refuse "$step" "$adopter" "$branch" "$title" "$body" "child made or moved refs: $moved" --base "$base"; return 1
  fi
  dirty="$(cgit -C "$wt" status --porcelain --untracked-files=all)"
  if [ -n "$dirty" ]; then
    echo "fail  $tag: the model left uncommitted changes in $wt:"; echo "$dirty" | sed 's/^/        /'
    refuse "$step" "$adopter" "$branch" "$title" "$body" "uncommitted changes left in the worktree"; return 1
  fi
  changed="$(cgit -C "$wt" diff --name-only "$base" HEAD)"
  if [ -z "$changed" ]; then
    echo "skip  $tag: nothing to propose (no commit on $branch)"
    cleanup_or_fail "$step" "$adopter" "$unit" "$wt" "$branch" skip "nothing to propose"; return $?
  fi
  # The BRANCH is read back before its files are -- every commit between the base and HEAD,
  # not HEAD alone. Whose is each, and does it carry a signature? A signature block means a
  # key signed content nobody at the keyboard read -- with the owner's global config, the
  # owner's key. Any author or committer but the clock's is a person's name on a model's work.
  # And the headless brief asks for ONE commit, which is what the clock admits: with two, a
  # signed first commit hides behind a clean second and a declaration added then deleted hides
  # behind a clean tree diff (review F1, proved over this script's own fixture). Refusals name
  # the commit and the fact; the count is recorded either way.
  local commits sig_lines author committer trailers c bad_commit=""
  commits="$(cgit -C "$wt" rev-list --count "$base..HEAD")"
  for c in $(cgit -C "$wt" rev-list "$base..HEAD"); do
    # the signature is a HEADER: read the header block only (up to the first blank line), so a
    # `gpgsig` word in the message body is text, not a signature (review round 5, F5)
    sig_lines="$(cgit -C "$wt" cat-file commit "$c" | sed '/^$/q' | grep -c '^gpgsig')"
    author="$(cgit -C "$wt" log -1 --format='%an <%ae>' "$c")"
    committer="$(cgit -C "$wt" log -1 --format='%cn <%ce>' "$c")"
    # a Signed-off-by / Co-authored-by line is a person's name on a model's work. Read over the
    # WHOLE message, not `interpret-trailers --parse` (which sees nothing when the line sits in
    # the first paragraph), and the value must EQUAL the clock's identity, not contain it
    # ("The Owner <...>, local clock <...>" contains it) -- follow-up R1.
    trailers="$(cgit -C "$wt" log -1 --format=%B "$c" | grep -Ei '^(Signed-off-by|Co-authored-by):' | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+$//' | grep -Fvx "$CLOCK_AUTHOR_NAME <$CLOCK_AUTHOR_EMAIL>" || true)"
    if [ "$sig_lines" != 0 ]; then bad_commit="commit ${c:0:7} carries a signature block"; break; fi
    if [ "$author" != "$CLOCK_AUTHOR_NAME <$CLOCK_AUTHOR_EMAIL>" ]; then bad_commit="commit ${c:0:7} is authored as '$author', not the clock"; break; fi
    if [ "$committer" != "$CLOCK_AUTHOR_NAME <$CLOCK_AUTHOR_EMAIL>" ]; then bad_commit="commit ${c:0:7} is committed as '$committer', not the clock"; break; fi
    if [ -n "$trailers" ]; then bad_commit="commit ${c:0:7} carries a trailer naming someone but the clock: $(echo "$trailers" | head -1)"; break; fi
  done
  if [ -n "$bad_commit" ]; then
    echo "fail  $tag: $commits commit(s) on $branch and $bad_commit -- nobody at the keyboard signed or was named; a headless commit is the clock's and unsigned by design, and the merge is the human act. Branch kept at $wt, never pushed."
    refuse "$step" "$adopter" "$branch" "$title" "$body" "$bad_commit" --base "$base" --commits "$commits"; return 1
  fi
  if [ "$commits" != 1 ]; then
    echo "fail  $tag: $commits commit(s) on $branch -- the headless brief asks for one and the clock admits one: history is where a signed commit or a declaration hides behind a clean tip. Branch kept at $wt, never pushed."
    refuse "$step" "$adopter" "$branch" "$title" "$body" "$commits commits on the branch, not 1" --base "$base" --commits "$commits"; return 1
  fi
  # The one commit's PARENT is the base, and it has one parent: an amend of the base folds the
  # upstream commit's changes under the clock's name with parent base^, and a merge-shaped
  # commit (-p base -p base^) is one commit too; either would make the record's `base` a lie
  # about what the pushed commit sits on (review round 5, F3).
  local commit parents; commit="$(cgit -C "$wt" rev-parse HEAD)"
  parents="$(cgit -C "$wt" rev-parse 'HEAD^@' | tr '\n' ' ')"
  if [ "$parents" != "$base " ]; then
    echo "fail  $tag: commit ${commit:0:7} has parent(s) $parents-- not the base ${base:0:7} alone: an amended base or a merge-shaped commit is not a proposal on origin/main, whatever the record would say. Branch kept at $wt, never pushed."
    refuse "$step" "$adopter" "$branch" "$title" "$body" "commit $commit parents [$parents] are not the base $base" --base "$base" --commits 1; return 1
  fi
  echo "ok    $tag: 1 commit ${commit:0:7} on origin/main@${base:0:7}; signature: none; author: $author; committer: $committer"
  local f ok bad=""
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    ok=0; for p in $paths; do case "$f" in "$p"/*) ok=1;; esac; done
    [ "$ok" = 1 ] || bad="$bad $f"
  done <<<"$changed"
  if [ -n "$bad" ]; then
    echo "fail  $tag: the commit touches$bad -- outside this step's allowed paths ($paths). A claim is a claim; a declaration is a different review. Branch kept for inspection, never pushed."
    refuse "$step" "$adopter" "$branch" "$title" "$body" "commit outside $paths:$bad"; return 1
  fi
  # Every file the commit carries must be a claim file (*.claim.yaml), and every claim file is
  # run through the skill's own validator, told --headless: THIS script knows nobody was at the
  # keyboard, so the validator requires run.headless: true on the file and refuses an override
  # whatever the file declares about itself. A file under the step's paths with any other name
  # is refused outright: the clock has no check for it, and a file nobody can check is not
  # proposed (the worked example saved as twin/claims/<date>-probe.yaml would otherwise pass
  # with zero checks). Live: the file must say headless on its face and the validator must
  # pass. Rehearsal: it must say injected on its face AND the validator must refuse it for that
  # reason -- the refusal is what keeps a rehearsal out of every gate, so the clock proves it
  # here rather than trusting it. A skill that ships no validator cannot propose a claim file.
  # Nothing below this loop (the PR body and its "no override is claimed") is written unless
  # every file passed, and a refusal deletes what the model wrote to the title and body files.
  local validator="$HUB/.claude/skills/$skill/$validator_rel" vout="$RUN_DIR/$tag.validate.out"
  while IFS= read -r f; do
    # shellcheck disable=SC2254  # the pattern is the row's glob, unquoted on purpose
    case "$(basename "$f")" in
      $pattern) ;;
      *) echo "fail  $tag: $f is under $paths but is not a $pattern -- the clock has no check for a file with that name, and a file nobody can check is not proposed. Branch kept at $wt, never pushed."
         refuse "$step" "$adopter" "$branch" "$title" "$body" "$f is not a $pattern; unchecked"; return 1;;
    esac
    if [ ! -f "$validator" ]; then
      echo "fail  $tag: $f matches $pattern and /$skill ships no $validator_rel -- a file nobody can check is not proposed. Branch kept at $wt, never pushed."
      refuse "$step" "$adopter" "$branch" "$title" "$body" "no validator for $skill; $f unchecked"; return 1
    fi
    if [ "$MODE" = rehearsal ]; then
      if ! grep -Eq '^injected: true' "$wt/$f"; then
        echo "fail  $tag: rehearsal claim $f does not carry injected: true at its top level"
        refuse "$step" "$adopter" "$branch" "$title" "$body" "rehearsal claim $f not marked injected"; return 1
      fi
      if "$PY" "$validator" "$wt/$f" --twin "$HUB" --headless >"$vout" 2>&1 </dev/null; then
        echo "fail  $tag: the validator ACCEPTED rehearsal claim $f -- an injected claim must be refused, and this one would pass a gate. Branch kept at $wt, never pushed."
        refuse "$step" "$adopter" "$branch" "$title" "$body" "validator accepted rehearsal claim $f"; return 1
      fi
      if ! grep -Eqi 'injected|rehearsal' "$vout"; then
        echo "fail  $tag: the validator refused rehearsal claim $f for a reason other than the injected mark ($(tail -1 "$vout" | cut -c1-120))"
        refuse "$step" "$adopter" "$branch" "$title" "$body" "rehearsal claim $f refused for the wrong reason"; return 1
      fi
      echo "ok    $tag: $f is marked injected and the validator refused it, by design ($(grep -Ei 'injected|rehearsal' "$vout" | head -1 | sed "s#$wt/##" | cut -c1-120))"
    else
      if ! grep -Eq '^[[:space:]]+headless: true[[:space:]]*$' "$wt/$f"; then
        echo "fail  $tag: live claim $f does not carry headless: true in its run block -- a claim this clock made says so on its face, or it is not this clock's claim. Branch kept at $wt, never pushed."
        refuse "$step" "$adopter" "$branch" "$title" "$body" "live claim $f not marked headless"; return 1
      fi
      if ! "$PY" "$validator" "$wt/$f" --twin "$HUB" --headless >"$vout" 2>&1 </dev/null; then
        echo "fail  $tag: the validator refused live claim $f ($(grep -c '^not ok' "$vout") reason(s); first: $(grep -m1 '^not ok' "$vout" | cut -c9-160)). Branch kept at $wt, never pushed."
        refuse "$step" "$adopter" "$branch" "$title" "$body" "claim file refused: $f: $(grep -m1 '^not ok' "$vout" | cut -c9-160)"; return 1
      fi
      echo "ok    $tag: $(tail -1 "$vout" | sed "s#$wt/##" | cut -c1-160)"
    fi
  done <<<"$changed"
  [ -s "$title" ] || cgit -C "$wt" log -1 --format=%s >"$title"
  [ -s "$body" ] || { cgit -C "$wt" log -1 --format=%b >"$body"; printf '\n%s\n' "Made by the local clock (talk/local-clock.sh, ticket 92), run $RUN_ID, on origin/main@${base:0:7}. A model ran on the owner's local clock, not on a GitHub clock. No override is claimed. The commit is unsigned and authored as the clock: nobody at the keyboard signed it, and the merge is the human act. Never merged by the clock." >>"$body"; }

  if [ "$PUSH" = 1 ]; then
    local repo="policy-as-versioned-$adopter/$adopter" url tip_now
    # origin/main may have moved since the fetch; the branch lands on the fetched base and the
    # record says which tip origin had at push time (review F6)
    # the remote the branch goes to is the one the step began with (the config snapshot above
    # already refused a rewrite; this is the second net, read just before the push)
    if [ "$(cgit -C "$unit" config --get remote.origin.url || true)" != "$origin_url" ] \
       || [ "$(cgit -C "$unit" config --get remote.origin.pushurl || true)" != "$origin_pushurl" ]; then
      echo "fail  $tag: remote.origin.url or pushurl changed since the step began ('$origin_url' -> '$(cgit -C "$unit" config --get remote.origin.url || true)'); not pushing. Branch kept at $wt."
      record --step "$step" --adopter "$adopter" --status fail --reason "remote.origin.url changed during the step" --branch "$branch" --base "$base"; return 1
    fi
    tip_now="$(GIT_TERMINAL_PROMPT=0 cgit -C "$wt" ls-remote --exit-code origin refs/heads/main 2>/dev/null | cut -f1)"
    if [ -n "$tip_now" ] && [ "$tip_now" != "$base" ]; then
      echo "note  $tag: origin/main is ${tip_now:0:7} now, ${base:0:7} when fetched -- the branch lands on the fetched base"
    fi
    if GIT_TERMINAL_PROMPT=0 cgit -C "$wt" push -q -u origin "$branch" 2>"$RUN_DIR/$tag.push.err" \
       && url="$("$GH" pr create --repo "$repo" --base main --head "$branch" --title "$(cat "$title")" --body-file "$body" 2>"$RUN_DIR/$tag.pr.err")"; then
      echo "ok    $tag: pushed $branch and opened $url"
      record --step "$step" --adopter "$adopter" --status ok --branch "$branch" --pr "$url" \
             --base "$base" --commits 1 --commit "$commit" --signature-block false \
             --author "$author" --committer "$committer" ${tip_now:+--origin-main-at-push "$tip_now"}
      # the branch lives on origin now; the local worktree and branch have done their work
      if drop_worktree "$unit" "$wt" "$branch"; then
        echo "        $tag: worktree and local branch removed"
      else
        echo "warn  $tag: the PR is open but $wt or the local branch $branch could not be removed ($(tail -1 "$RUN_DIR/cleanup.err" 2>/dev/null | cut -c1-120)); remove them by hand"
      fi
    else
      echo "fail  $tag: push or gh pr create failed ($(tail -1 "$RUN_DIR/$tag.push.err" "$RUN_DIR/$tag.pr.err" 2>/dev/null | tail -1 | cut -c1-120)); branch kept at $wt"
      record --step "$step" --adopter "$adopter" --status fail --reason "push or pr create failed" --branch "$branch" --base "$base"; return 1
    fi
  else
    echo "ok    $tag: committed on $branch at $wt; PR title/body in $RUN_DIR"
    if [ "$MODE" = rehearsal ]; then
      echo "        rehearsal: this branch is never pushed. Remove it with:  git -C $unit worktree remove --force $wt; git -C $unit branch -D $branch"
    else
      echo "        to land it as a PR (the owner's hand):  git -C $wt push -u origin $branch && gh pr create --repo policy-as-versioned-$adopter/$adopter --base main --head $branch --title \"\$(cat $title)\" --body-file $body"
    fi
    record --step "$step" --adopter "$adopter" --status ok --branch "$branch" \
           --base "$base" --commits 1 --commit "$commit" --signature-block false \
           --author "$author" --committer "$committer"
  fi
}

failed=0
for row in "${STEPS[@]}"; do
  IFS='|' read -r name skill paths pattern validator _desc <<<"$row"
  if [ "${#ONLY_STEPS[@]}" -gt 0 ]; then
    wanted=0; for s in "${ONLY_STEPS[@]}"; do [ "$s" = "$name" ] && wanted=1; done
    [ "$wanted" = 1 ] || continue
  fi
  for adopter in "${ADOPTERS[@]}"; do
    run_step "$name" "$skill" "$paths" "$pattern" "$validator" "$adopter" || failed=$((failed+1))
  done
done

"$PY" "$HELPER" finish --run-dir "$RUN_DIR" --root "$ROOT" --hub "$HUB" --scheduled "$SCHEDULED" \
  --period-hours "$PERIOD" --model "$(basename "$CLAUDE")" ${INJECTED_FILE:+--injected "$INJECTED_FILE"}
echo "local clock: done mode=$MODE failed=$failed marker=$ROOT/last-run.json (this run never appends talk/truth.log; it is not citable)"
[ "$failed" = 0 ] || exit 1
