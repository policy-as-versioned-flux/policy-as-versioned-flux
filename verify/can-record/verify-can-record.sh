#!/usr/bin/env bash
# Beat (eco-system ticket 100): "a run that cannot record its line says so before it measures."
#
# `.github/workflows/truth.yml` runs on every push that touches the gate, on whatever branch. On
# a ticket branch the cage's `git pull --rebase --autostash origin main` replays the branch's own
# commits onto origin/main with new SHAs, HEAD stops being a descendant of origin/<branch>, and
# `push origin HEAD:"${GITHUB_REF_NAME}"` is refused non-fast-forward. Run 98 on
# ticket-89-deny-is-not-a-rung is the recorded negative control -- nobody else pushing, the remote
# tip unmoved, `Rebasing (12/12)`, `Successfully rebased`, `! [rejected] (non-fast-forward)`. Run
# 100 on the same branch is the positive one: it landed, because that branch had been REBASED onto
# main rather than merged, so the rebase replayed nothing. The line was produced, committed and
# thrown away, and nothing anywhere said so.
#
# WHAT THIS GRADES, in three parts and one instrument.
#
#   1. THE RECORD. Every TRUTH line in talk/truth.log is blamed to the commit that introduced it,
#      and a line naming a run number must come from the clock's own commit whose message names
#      the SAME run. A hand-written line is named. One historical `run=local` line is
#      grandfathered by count (see can_record.py); a second fails.
#   2. THE SHAPE. truth.yml still carries the guard, before the measurement, with the record step
#      and the cage consulting it, still pushing the one refspec it is allowed to push and no
#      force push anywhere.
#   3. THE MECHANISM, measured rather than read. This is the part that matters and the part a
#      YAML reader cannot do. The fixture lifts the workflow's OWN shell -- the guard step, the
#      record step and the cage, verbatim out of truth.yml, with two substitutions it prints --
#      and runs it over two throwaway git repositories in five states: on main at the tip, on main
#      behind the tip, on a branch rebased onto main, on a branch carrying a merge of main, and on
#      a branch behind main. In each state it runs the cage TWICE: once with CAN_RECORD forced to
#      `yes`, to observe what the push actually does to the remote ref, and once for real. The
#      test is that the guard's verdict EQUALS that observation, every time. The served artefact
#      is the remote branch ref; the operation that reaches it is the push; nothing here is
#      inferred from a file existing or from what the YAML looks like it means.
#
#      Everything the fixture writes lives under a mktemp directory and is deleted. It never
#      touches this repository's talk/truth.log, and the TRUTH-shaped line it plants is dated
#      1970 with a zero hub sha so that no reader could mistake one for an observation.
#
#   PASS (exit 0)  the log, the shape and the mechanism all hold
#   FAIL (exit 1)  one of them does not, named
#
# NO could-not-look, by decision (ticket 100, delegated under ADR-0025). Everything this script
# reads is in this repository -- truth.yml, talk/truth.log, .git -- and everything it runs is git
# and python, both of which the gate installs before it. The three states in which it could have
# shrugged are graded RED instead, each with its own sentence: no python3 to parse the workflow
# with, no git, and a SHALLOW checkout (in which `git blame` attributes every line past the graft
# to the boundary commit, so the log would read clean for the wrong reason). A runner that has
# lost its interpreter or its history should go red, not shrug -- the same call
# verify-branch-refs.sh and verify-twin-per-adopter.sh already record for their wrappers.
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
say "1. every TRUTH line in talk/truth.log came from a run that could record it"
if [ "$(git -C "$ROOT" rev-parse --is-shallow-repository 2>/dev/null)" != false ]; then
  note "this checkout is shallow (or is not a git repository), so git blame would attribute every truth.log line past the graft to the boundary commit and the log would read clean for the wrong reason"
else
  "$PY" "$HERE/can_record.py" log "$ROOT" || note "talk/truth.log carries a line no run recorded (above)"
fi

say "1b. no citable TRUTH line is stranded on a branch that merged without it"
"$PY" "$HERE/can_record.py" stranded "$ROOT" \
  || note "a clock line that measured a tree the default branch has never reached that branch's log (above); the repair is a cherry-pick of the clock's own commit, author preserved, as the integrator did for run 101 on 2026-09-05 -- not a line typed by hand"

# ---------------------------------------------------------------- 2. the shape
say "2. truth.yml still has the shape ticket 100 decided"
if "$PY" "$HERE/can_record.py" shape "$WORKFLOW"; then
  ok "the guard runs before the gate, the record step and the cage both consult it, and the one push is HEAD:\${GITHUB_REF_NAME} with no force anywhere"
else
  note "truth.yml no longer has the shape (above)"
fi

# ---------------------------------------------------------------- 3. the mechanism
say "3. the workflow's own shell, over two throwaway repositories, in five states"

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
export GIT_CONFIG_GLOBAL="$T/gitconfig" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
: >"$GIT_CONFIG_GLOBAL"
git config --global init.defaultBranch main
git config --global user.name "fixture"
git config --global user.email "fixture@example.invalid"
git config --global commit.gpgsign false
git config --global advice.detachedHead false

# The three shells, lifted out of truth.yml. `step` prints every substitution it made on stderr;
# they are echoed here so a reader of this output knows exactly what was changed and why.
for pair in "guard:does this run record" "record:record the TRUTH line" "cage:observation cage"; do
  key="${pair%%:*}"; frag="${pair#*:}"
  if ! "$PY" "$HERE/can_record.py" step "$WORKFLOW" gate "$frag" >"$T/$key.sh" 2>"$T/$key.notes"; then
    note "could not lift the step named '$frag' out of truth.yml"; cat "$T/$key.notes"; lifted=0
  fi
  sed "s/^/  ($key) /" "$T/$key.notes"
done
# Only an extraction failure stops the fixture. A fault found above -- a stranded line, a shape
# that drifted -- is a red that must not also cost the estate the measurement below.
[ "${lifted:-1}" = 1 ] || { echo; echo "FAIL: the steps could not be lifted out of truth.yml, so the mechanism could not be measured"; exit 1; }
ok "lifted the guard, the record step and the cage verbatim out of truth.yml"

gitcfg() { git config user.name fixture; git config user.email fixture@example.invalid; }

# new_estate <dir>: a bare "remote" and a clone of it, with one commit on main.
new_estate() {
  local d="$1"
  mkdir -p "$d"
  git init -q --bare -b main "$d/remote.git"
  git clone -q "$d/remote.git" "$d/work" 2>/dev/null
  ( cd "$d/work" && gitcfg \
    && mkdir -p talk && printf 'TRUTH 1970-01-01T00:00Z run=0 hub=0000000 pass=0\n' >talk/truth.log \
    && echo base >README.md && git add -A && git commit -qm base && git push -q origin main )
}

# advance_main <dir> <tag>: a commit lands on the remote's main from somewhere else entirely.
advance_main() {
  local d="$1" tag="$2"
  git clone -q "$d/remote.git" "$d/other"
  ( cd "$d/other" && gitcfg && echo "$tag" >"moved-$tag.txt" && git add -A \
    && git commit -qm "main moves ($tag)" && git push -q origin main )
  rm -rf "$d/other"
}

# work_commit <dir> <file>: one commit of the ref's own on the work checkout.
work_commit() { ( cd "$1/work" && echo "$2" >"$2.txt" && git add -A && git commit -qm "$2" ); }

# build_case <dir> <case>: put <dir>/work on the ref the case names, in the case's state.
build_case() {
  local d="$1" kase="$2"
  new_estate "$d"
  case "$kase" in
    main-at-tip) ;;                                  # on main, nothing moved
    main-behind)
      advance_main "$d" a
      ;;
    branch-rebased)                                  # the shape run 100 landed from
      ( cd "$d/work" && git checkout -q -b feature )
      work_commit "$d" own1; work_commit "$d" own2
      ( cd "$d/work" && git push -q -u origin feature )
      ;;
    branch-with-merge)                               # the shape run 98 died on
      ( cd "$d/work" && git checkout -q -b feature )
      work_commit "$d" own1; work_commit "$d" own2
      ( cd "$d/work" && git push -q -u origin feature )
      advance_main "$d" a
      ( cd "$d/work" && git fetch -q origin main && git merge -q --no-edit FETCH_HEAD )
      ;;
    branch-behind)                                   # own commits, main moved, no merge
      ( cd "$d/work" && git checkout -q -b feature )
      work_commit "$d" own1
      ( cd "$d/work" && git push -q -u origin feature )
      advance_main "$d" a
      ;;
    *) note "unknown fixture case $kase"; return 1 ;;
  esac
}

# run_steps <dir> <ref> <forced>: run the record step and the cage in <dir>/work.
#   forced=yes   CAN_RECORD is planted as `yes` whatever the guard thinks -- the control that
#                observes what the push DOES to the remote ref in this state
#   forced=no    CAN_RECORD comes from the guard step's own $GITHUB_ENV
# Echoes "<can> <rc> <remote-before> <remote-after> <head-before> <head-after> <appended>".
run_steps() {
  # Split across two `local` statements on purpose: bash expands every word of one `local` before
  # it assigns any of them, so `local d="$1" w="$d/work"` reads the CALLER's d.
  local d="$1" ref="$2" forced="$3"
  local w="$d/work" env="$d/env" can reason rc
  : >"$env"; : >"$d/summary"; mkdir -p "$d/temp"
  { echo "some gate output"; printf 'TRUTH 1970-01-01T00:00Z run=%s hub=0000000 pass=1 fail=0\n' 7; echo "more"; } >"$d/temp/gate.out"

  ( cd "$w" && GITHUB_REF_NAME="$ref" GITHUB_ENV="$env" DEFAULT_BRANCH=main \
      bash "$T/guard.sh" ) >"$d/guard.out" 2>&1
  local grc=$?
  can="$(sed -n 's/^CAN_RECORD=//p' "$env" | tail -1)"
  reason="$(sed -n 's/^CANNOT_REASON=//p' "$env" | tail -1)"
  [ "$grc" -eq 0 ] || can="guard-failed"
  [ "$forced" = yes ] && can=yes

  local rbefore rafter hbefore hafter appended=no
  rbefore="$(git -C "$d/remote.git" rev-parse "refs/heads/$ref" 2>/dev/null || echo none)"
  hbefore="$(git -C "$w" rev-parse HEAD)"
  local before_len; before_len="$(wc -l <"$w/talk/truth.log")"

  ( cd "$w" && CAN_RECORD="$can" CANNOT_REASON="$reason" RUNNER_TEMP="$d/temp" \
      GITHUB_STEP_SUMMARY="$d/summary" bash "$T/record.sh" ) >"$d/record.out" 2>&1
  local rrc=$?
  [ "$(wc -l <"$w/talk/truth.log")" -gt "$before_len" ] && appended=yes

  ( cd "$w" && CAN_RECORD="$can" CANNOT_REASON="$reason" GITHUB_REF_NAME="$ref" \
      GITHUB_RUN_NUMBER=7 GH_TOKEN=not-a-token \
      OBSERVATION_LANE="talk/truth.log drift/samples.jsonl talk/captures observations" \
      bash "$T/cage.sh" ) >"$d/cage.out" 2>&1
  rc=$?
  rafter="$(git -C "$d/remote.git" rev-parse "refs/heads/$ref" 2>/dev/null || echo none)"
  hafter="$(git -C "$w" rev-parse HEAD)"
  echo "$can $rc $rbefore $rafter $hbefore $hafter $appended $rrc $grc"
}

grade_case() {
  local kase="$1" ref="$2" expect="$3"
  local d="$T/$kase"
  build_case "$d/probe" "$kase" || return 1
  build_case "$d/real"  "$kase" || return 1

  # The control: force the guard's answer to `yes` and watch what the push does to the remote ref.
  read -r _ prc pb pa phb _ _ _ _ < <(run_steps "$d/probe" "$ref" yes)
  local landed=no; [ "$pb" != "$pa" ] && landed=yes

  # The real run: the guard decides.
  read -r can rc rb ra hb ha appended rrc grc < <(run_steps "$d/real" "$ref" no)
  local moved=no; [ "$rb" != "$ra" ] && moved=yes

  printf '  %-18s guard=%-4s forced-push-landed=%s  real: pushed=%s appended=%s head-moved=%s\n' \
    "$kase" "$can" "$landed" "$moved" "$appended" "$([ "$hb" = "$ha" ] && echo no || echo yes)"

  # (a) the guard said what this ticket decided it should say in this state...
  [ "$can" = "$expect" ] && ok "$kase: the guard said '$can'" \
    || { note "$kase: the guard said '$can' where ticket 100 decided '$expect'"; sed 's/^/       /' "$d/real/guard.out"; }
  # ...and a run that says it CAN record is never wrong about the push. (The converse is not
  # asserted: after this ticket a branch run says no even where the push would land, because a
  # landed line is mode 3 waiting to happen -- which case (d) below then measures.)
  if [ "$can" = yes ] && [ "$landed" = no ]; then
    note "$kase: the guard promised a record and a forced push was refused"
    sed 's/^/       probe: /' "$d/probe/cage.out" | tail -5
  fi
  # (b) the TRUTH line is printed for a reader whatever the verdict.
  grep -q '^TRUTH 1970' "$d/real/record.out" \
    && ok "$kase: the run printed its TRUTH line for a reader to quote" \
    || note "$kase: the run did not print its TRUTH line"
  [ "$rrc" -eq 0 ] || note "$kase: the record step exited $rrc"
  # (c) a run that cannot record writes nothing and commits nothing.
  if [ "$can" = no ]; then
    [ "$appended" = no ] && ok "$kase: nothing was appended to talk/truth.log" \
      || note "$kase: a run that cannot record appended a line to talk/truth.log anyway"
    [ "$hb" = "$ha" ] && ok "$kase: no commit was made and thrown away (HEAD is where it was)" \
      || note "$kase: a commit was made on a run that cannot push it ($hb -> $ha)"
    [ "$rc" -eq 0 ] && ok "$kase: the cage exited 0 -- a run that cannot record is not a red" \
      || { note "$kase: the cage exited $rc on a run that simply cannot record"; sed 's/^/       /' "$d/real/cage.out" | tail -5; }
    grep -qi 'CANNOT RECORD' "$d/real/guard.out" \
      && ok "$kase: the guard said so in as many words, before the gate ran" \
      || { note "$kase: the guard did not say it cannot record"; sed 's/^/       /' "$d/real/guard.out"; }
    # (d) and what the OLD behaviour did here, measured rather than remembered.
    if [ "$landed" = no ]; then
      grep -qiE 'rejected|non-fast-forward' "$d/probe/cage.out" \
        && ok "$kase: mode 1 reproduced -- a forced run committed, rebased, and had its push refused non-fast-forward (run 98's shape)" \
        || { note "$kase: a forced push did not land and did not say non-fast-forward"; sed 's/^/       /' "$d/probe/cage.out" | tail -8; }
    else
      ok "$kase: mode 2 reproduced -- a forced run's push LANDED on $ref (run 100's shape)"
      # ...and mode 3: the integrator merges the tip they reviewed, which is the tip BEFORE the
      # clock's commit, and the observation goes with the branch. Run 101 landed at 14:45Z on a
      # branch merged at 14:42Z; no check made at merge time could have caught that, which is why
      # this ticket stops the landing rather than policing the merge.
      git clone -q "$d/probe/remote.git" "$d/probe/merger"
      ( cd "$d/probe/merger" && gitcfg && git checkout -q main \
        && git merge -q --no-ff -m "merge the reviewed tip" "$phb" && git push -q origin main ) >/dev/null 2>&1
      if git -C "$d/probe/remote.git" show refs/heads/main:talk/truth.log 2>/dev/null | grep -q 'run=7'; then
        note "$kase: the fixture could not reproduce mode 3 -- main's log carries the branch's line"
      else
        ok "$kase: mode 3 reproduced -- after the branch merged without that commit, main's talk/truth.log does NOT carry the line, and the observation is stranded on $ref (run 101's shape)"
      fi
    fi
  else
    [ "$appended" = yes ] && ok "$kase: the line was appended to talk/truth.log" \
      || note "$kase: a run that can record appended nothing"
    [ "$moved" = yes ] && ok "$kase: the remote ref $ref carries the run's commit" \
      || { note "$kase: the push did not move origin/$ref"; sed 's/^/       /' "$d/real/cage.out" | tail -5; }
    [ "$rc" -eq 0 ] || { note "$kase: the cage exited $rc"; sed 's/^/       /' "$d/real/cage.out" | tail -5; }
    git -C "$d/real/remote.git" show "refs/heads/$ref:talk/truth.log" 2>/dev/null | grep -q '^TRUTH 1970-01-01T00:00Z run=7' \
      && ok "$kase: the line is readable on the remote ref, which is the artefact a reader cites" \
      || note "$kase: origin/$ref does not carry the recorded line"
    grep -qi 'CAN RECORD' "$d/real/guard.out" \
      && ok "$kase: the guard said so before the gate ran" \
      || note "$kase: the guard did not say it can record"
  fi
}

grade_case main-at-tip       main    yes
grade_case main-behind       main    yes
grade_case branch-rebased    feature no
grade_case branch-with-merge feature no
grade_case branch-behind     feature no

# Two states in which the guard cannot answer at all. It refuses rather than guessing: a wrong
# `yes` commits a line that is thrown away, and a wrong `no` loses a citable observation.
say "4. the guard refuses where it cannot know, rather than guessing"
d="$T/refusals"; build_case "$d" branch-rebased
git clone -q --depth 1 "file://$d/remote.git" "$d/shallow-work" 2>/dev/null
if ( cd "$d/shallow-work" && GITHUB_REF_NAME=main GITHUB_ENV="$d/env" DEFAULT_BRANCH=main \
     bash "$T/guard.sh" ) >"$d/shallow.out" 2>&1; then
  note "the guard answered in a shallow checkout, where it cannot know"
else
  grep -q 'shallow' "$d/shallow.out" && ok "a shallow checkout: refused, and named as shallow" \
    || { note "the guard failed in a shallow checkout without naming shallowness"; cat "$d/shallow.out"; }
fi
if ( cd "$d/work" && GITHUB_REF_NAME=main GITHUB_ENV="$d/env2" DEFAULT_BRANCH= \
     bash "$T/guard.sh" ) >"$d/nodefault.out" 2>&1; then
  note "the guard answered with no default branch name, which means it guessed one"
else
  grep -qi 'default_branch' "$d/nodefault.out" \
    && ok "an empty default branch name: refused, rather than assuming 'main'" \
    || { note "the guard failed with no default branch and did not say why"; cat "$d/nodefault.out"; }
fi

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: every recorded TRUTH line is blamed to the clock commit naming the same run; truth.yml's guard runs before the gate, the record step and the cage consult it, and the one push is HEAD:\${GITHUB_REF_NAME} with no force anywhere; and the workflow's own shell, run over two throwaway repositories in five states, records exactly when its guard said it could and commits nothing when it said it could not"
  exit 0
fi
echo "FAIL: $bad fault(s) -- the clock's account of what it can record does not match what it does (ticket 100)"
exit 1
