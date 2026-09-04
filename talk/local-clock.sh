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
# (the refusing mode: no merge, no enactment push, no tag), and with `gh` kept out of the child's
# allowed tools altogether. What the model may do is read, write the adopter's worktree, commit
# on the branch this script made for it, and stop. This script then reads what it committed,
# refuses anything outside the step's allowed paths, validates the claim file with the
# validator told --headless (the file must say run.headless: true and carry no override; the
# model's own say-so is not what the no-override invariant rests on), and either pushes
# and opens the PR (--push, the owner's hand, never from inside a Claude Code session) or prints
# the command for the owner to run.
#
# The steps table below is the seam ticket 93 stacks on: add a row, ship the skill, and the
# clock runs it. A row whose skill is not in .claude/skills yet is recorded as skipped, by name.
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
ROOT="${LOCAL_CLOCK_HOME:-$HUB/.local-clock}"
ESTATE="${LOCAL_CLOCK_ESTATE:-$HUB/.estate-clone}"
MAX_TURNS="${LOCAL_CLOCK_MAX_TURNS:-80}"
PERIOD="${LOCAL_CLOCK_PERIOD_HOURS:-24}"
SCHEDULED="${LOCAL_CLOCK_LAUNCHD:-0}"

# name | skill | paths the step's commit may touch (space-separated) | what it is
STEPS=(
  "classify|classify-and-judge|twin/claims|the unbound pool (news, market moves) classified against the adopter's overlay: bindings and positions, grade 5, no override, one claim file on a branch"
  "derive|derive-probability|twin/claims|ticket 93: a probability derived from the adopter's world model and the subscribed feeds' dated series, with its basis, grade and the signals it rested on; runs once .claude/skills/derive-probability/SKILL.md exists"
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
    --list-steps) for row in "${STEPS[@]}"; do IFS='|' read -r n s p d <<<"$row"; printf '%-10s /%-22s %-14s %s\n' "$n" "$s" "$p" "$d"; done; exit 0;;
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
if [ "$PUSH" = 1 ] && [ -n "${CLAUDECODE:-}" ]; then
  echo "FAIL: --push is refused inside a Claude Code session; the push to an adopter's repository is the owner's hand, from a terminal"; exit 2
fi
if [ "$PUSH" = 1 ] && [ -n "$INJECT" ]; then
  echo "FAIL: --push is refused on a rehearsal (--inject): an injected signal never leaves this machine"; exit 2
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

record() { "$PY" "$HELPER" record --run-dir "$RUN_DIR" "$@" </dev/null; }

drop_worktree() {  # unit wt branch -- remove a step's worktree and its branch; true only when both are gone
  local unit="$1" wt="$2" branch="$3" err="$RUN_DIR/cleanup.err"
  git -C "$unit" worktree remove --force "$wt" 2>>"$err" \
    && git -C "$unit" branch -q -D "$branch" 2>>"$err" \
    && [ ! -e "$wt" ] \
    && ! git -C "$unit" show-ref -q --verify "refs/heads/$branch"
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

run_step() {  # step skill paths adopter
  local step="$1" skill="$2" paths="$3" adopter="$4"
  local unit="$ESTATE/$adopter" tag="$step-$adopter"
  if [ ! -f "$HUB/.claude/skills/$skill/SKILL.md" ]; then
    echo "skip  $tag: no .claude/skills/$skill/SKILL.md yet -- the step is charted, the skill is not shipped"
    record --step "$step" --adopter "$adopter" --status skip --reason "skill $skill not shipped"; return 0
  fi
  if [ ! -d "$unit/.git" ] && [ ! -f "$unit/.git" ]; then
    echo "skip  $tag: no checkout at $unit (run clone-estate.sh)"
    record --step "$step" --adopter "$adopter" --status skip --reason "no checkout at $unit"; return 0
  fi
  local branch="$BRANCH_PREFIX/$step-$RUN_ID" wt="$unit/.work/local-clock/$RUN_ID-$step"
  mkdir -p "$unit/.work/local-clock"
  if ! git -C "$unit" worktree add -q "$wt" -b "$branch" main 2>"$RUN_DIR/$tag.worktree.err"; then
    echo "fail  $tag: could not make a worktree on $branch from main ($(tail -1 "$RUN_DIR/$tag.worktree.err"))"
    record --step "$step" --adopter "$adopter" --status fail --reason "worktree add failed"; return 1
  fi
  local prompt="$RUN_DIR/$tag.system.md" title="$RUN_DIR/$tag.pr-title" body="$RUN_DIR/$tag.pr-body.md"
  render_prompt "$step" "$skill" "$adopter" "$wt" "$branch" "$paths" "$prompt"

  if [ "$DRY" = 1 ]; then
    echo "dry   $tag: would run  $CLAUDE -p \"/$skill $adopter\" --max-turns $MAX_TURNS --append-system-prompt \"\$(cat $prompt)\"  (worktree $wt on $branch; prompt kept at $prompt)"
    cleanup_or_fail "$step" "$adopter" "$unit" "$wt" "$branch" skip "dry run"; return $?
  fi

  echo "run   $tag: /$skill $adopter on $branch (worktree $wt, max $MAX_TURNS turns)"
  # TWIN_ENACT_MODE=operations: the refusing mode for the whole child, whatever twin/ENACT_MODE
  # says today. The child cannot merge, cannot push an enactment repository, cannot tag.
  env -u CLAUDECODE -u CLAUDE_CODE_CHILD_SESSION \
    TWIN_ENACT_MODE=operations \
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

  # What did the model leave? Uncommitted work is a step that did not finish. No commit is
  # nothing to propose. A commit is judged file by file against the step's allowed paths.
  local dirty changed
  dirty="$(git -C "$wt" status --porcelain --untracked-files=all)"
  if [ -n "$dirty" ]; then
    echo "fail  $tag: the model left uncommitted changes in $wt:"; echo "$dirty" | sed 's/^/        /'
    record --step "$step" --adopter "$adopter" --status fail --reason "uncommitted changes left in the worktree" --branch "$branch"; return 1
  fi
  changed="$(git -C "$wt" diff --name-only "main...HEAD")"
  if [ -z "$changed" ]; then
    echo "skip  $tag: nothing to propose (no commit on $branch)"
    cleanup_or_fail "$step" "$adopter" "$unit" "$wt" "$branch" skip "nothing to propose"; return $?
  fi
  local f ok bad=""
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    ok=0; for p in $paths; do case "$f" in "$p"/*) ok=1;; esac; done
    [ "$ok" = 1 ] || bad="$bad $f"
  done <<<"$changed"
  if [ -n "$bad" ]; then
    echo "fail  $tag: the commit touches$bad -- outside this step's allowed paths ($paths). A claim is a claim; a declaration is a different review. Branch kept for inspection, never pushed."
    record --step "$step" --adopter "$adopter" --status fail --reason "commit outside $paths:$bad" --branch "$branch"; return 1
  fi
  # Every claim file the commit carries is run through the skill's own validator, told
  # --headless: THIS script knows nobody was at the keyboard, so the validator requires
  # run.headless: true on the file and refuses an override whatever the file declares about
  # itself. Live: the file must say headless on its face and the validator must pass. Rehearsal:
  # it must say injected on its face AND the validator must refuse it for that reason -- the
  # refusal is what keeps a rehearsal out of every gate, so the clock proves it here rather than
  # trusting it. A skill that ships no validator cannot propose a claim file. Nothing below
  # this loop (the PR body and its "no override is claimed") is written unless every file passed.
  local validator="$HUB/.claude/skills/$skill/assets/validate_claim.py" vout="$RUN_DIR/$tag.validate.out"
  while IFS= read -r f; do
    case "$f" in *.claim.yaml) ;; *) continue;; esac
    if [ ! -f "$validator" ]; then
      echo "fail  $tag: $f is a claim file and /$skill ships no assets/validate_claim.py -- a claim nobody can check is not proposed. Branch kept at $wt, never pushed."
      record --step "$step" --adopter "$adopter" --status fail --reason "no validator for $skill; $f unchecked" --branch "$branch"; return 1
    fi
    if [ "$MODE" = rehearsal ]; then
      if ! grep -Eq '^injected: true' "$wt/$f"; then
        echo "fail  $tag: rehearsal claim $f does not carry injected: true at its top level"
        record --step "$step" --adopter "$adopter" --status fail --reason "rehearsal claim $f not marked injected" --branch "$branch"; return 1
      fi
      if "$PY" "$validator" "$wt/$f" --twin "$HUB" --headless >"$vout" 2>&1 </dev/null; then
        echo "fail  $tag: the validator ACCEPTED rehearsal claim $f -- an injected claim must be refused, and this one would pass a gate. Branch kept at $wt, never pushed."
        record --step "$step" --adopter "$adopter" --status fail --reason "validator accepted rehearsal claim $f" --branch "$branch"; return 1
      fi
      if ! grep -Eqi 'injected|rehearsal' "$vout"; then
        echo "fail  $tag: the validator refused rehearsal claim $f for a reason other than the injected mark ($(tail -1 "$vout" | cut -c1-120))"
        record --step "$step" --adopter "$adopter" --status fail --reason "rehearsal claim $f refused for the wrong reason" --branch "$branch"; return 1
      fi
      echo "ok    $tag: $f is marked injected and the validator refused it, by design ($(grep -Ei 'injected|rehearsal' "$vout" | head -1 | sed "s#$wt/##" | cut -c1-120))"
    else
      if ! grep -Eq '^[[:space:]]+headless: true[[:space:]]*$' "$wt/$f"; then
        echo "fail  $tag: live claim $f does not carry headless: true in its run block -- a claim this clock made says so on its face, or it is not this clock's claim. Branch kept at $wt, never pushed."
        record --step "$step" --adopter "$adopter" --status fail --reason "live claim $f not marked headless" --branch "$branch"; return 1
      fi
      if ! "$PY" "$validator" "$wt/$f" --twin "$HUB" --headless >"$vout" 2>&1 </dev/null; then
        echo "fail  $tag: the validator refused live claim $f ($(grep -c '^not ok' "$vout") reason(s); first: $(grep -m1 '^not ok' "$vout" | cut -c9-160)). Branch kept at $wt, never pushed."
        record --step "$step" --adopter "$adopter" --status fail --reason "claim file refused: $f: $(grep -m1 '^not ok' "$vout" | cut -c9-160)" --branch "$branch"; return 1
      fi
      echo "ok    $tag: $(tail -1 "$vout" | sed "s#$wt/##" | cut -c1-160)"
    fi
  done <<<"$changed"
  [ -s "$title" ] || git -C "$wt" log -1 --format=%s >"$title"
  [ -s "$body" ] || { git -C "$wt" log -1 --format=%b >"$body"; printf '\n%s\n' "Made by the local clock (talk/local-clock.sh, ticket 92), run $RUN_ID. A model ran on the owner's local clock, not on a GitHub clock. No override is claimed. Never merged by the clock." >>"$body"; }

  if [ "$PUSH" = 1 ]; then
    local repo="policy-as-versioned-$adopter/$adopter" url
    if git -C "$wt" push -q -u origin "$branch" 2>"$RUN_DIR/$tag.push.err" \
       && url="$(gh pr create --repo "$repo" --base main --head "$branch" --title "$(cat "$title")" --body-file "$body" 2>"$RUN_DIR/$tag.pr.err")"; then
      echo "ok    $tag: pushed $branch and opened $url"
      record --step "$step" --adopter "$adopter" --status ok --branch "$branch" --pr "$url"
      # the branch lives on origin now; the local worktree and branch have done their work
      if drop_worktree "$unit" "$wt" "$branch"; then
        echo "        $tag: worktree and local branch removed"
      else
        echo "warn  $tag: the PR is open but $wt or the local branch $branch could not be removed ($(tail -1 "$RUN_DIR/cleanup.err" 2>/dev/null | cut -c1-120)); remove them by hand"
      fi
    else
      echo "fail  $tag: push or gh pr create failed ($(tail -1 "$RUN_DIR/$tag.push.err" "$RUN_DIR/$tag.pr.err" 2>/dev/null | tail -1 | cut -c1-120)); branch kept at $wt"
      record --step "$step" --adopter "$adopter" --status fail --reason "push or pr create failed" --branch "$branch"; return 1
    fi
  else
    echo "ok    $tag: committed on $branch at $wt; PR title/body in $RUN_DIR"
    if [ "$MODE" = rehearsal ]; then
      echo "        rehearsal: this branch is never pushed. Remove it with:  git -C $unit worktree remove --force $wt; git -C $unit branch -D $branch"
    else
      echo "        to land it as a PR (the owner's hand):  git -C $wt push -u origin $branch && gh pr create --repo policy-as-versioned-$adopter/$adopter --base main --head $branch --title \"\$(cat $title)\" --body-file $body"
    fi
    record --step "$step" --adopter "$adopter" --status ok --branch "$branch"
  fi
}

failed=0
for row in "${STEPS[@]}"; do
  IFS='|' read -r name skill paths _desc <<<"$row"
  if [ "${#ONLY_STEPS[@]}" -gt 0 ]; then
    wanted=0; for s in "${ONLY_STEPS[@]}"; do [ "$s" = "$name" ] && wanted=1; done
    [ "$wanted" = 1 ] || continue
  fi
  for adopter in "${ADOPTERS[@]}"; do
    run_step "$name" "$skill" "$paths" "$adopter" || failed=$((failed+1))
  done
done

"$PY" "$HELPER" finish --run-dir "$RUN_DIR" --root "$ROOT" --hub "$HUB" --scheduled "$SCHEDULED" \
  --period-hours "$PERIOD" ${INJECTED_FILE:+--injected "$INJECTED_FILE"}
echo "local clock: done mode=$MODE failed=$failed marker=$ROOT/last-run.json (this run never appends talk/truth.log; it is not citable)"
[ "$failed" = 0 ] || exit 1
