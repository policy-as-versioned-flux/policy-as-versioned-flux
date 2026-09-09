#!/usr/bin/env bash
# Beat (eco-system ticket 59): "a fall is a blocking event."
#
# NORTH-STAR §5's last bullet is two sentences. "The number and its date are recorded on every
# run" has been true since GAPS 2.1. "A fall is a blocking event" had NO implementation: nothing
# compared a TRUTH line to its predecessor. Run 13 fell 54 -> 53 and nothing fired. Run 105 took
# `fail` from 6 to 11 and nothing fired. The gate's own red could not carry the signal either --
# 17 of 21 runs were failing at the same step, so a fall inside a saturated red was invisible.
#
# WHAT IS BLOCKED, AND WHERE THE STOP IS ENFORCED, named precisely because a stop nobody can
# point at is not a stop:
#
#   THE SERVED ARTEFACT   the `truth` workflow's own run conclusion. NORTH-STAR §5 makes one
#                         command on a clock the only source any document may cite for "what
#                         works", and the deck, the reviews and every ticket read it that way.
#   THE OPERATION         `.github/workflows/truth.yml`, job `gate`, the step named
#                         `a fall is a blocking event`, which runs AFTER the observation cage
#                         (so the line is recorded whatever it says -- a clock appends
#                         observations, ADR-0024) and exits 1 with its own ::error:: and its own
#                         step-summary line. Distinct from `fail if the gate failed`: a run can
#                         be red for a fall while the gate's own count is unchanged, and a run
#                         whose gate is green cannot be cited as green if the number fell.
#   NOT BLOCKED           the recording (a clock that hides a fall is worse than one that
#                         reports it), and no unit's release. The eight units are independently
#                         versioned repositories; gating their releases on this repository's
#                         number would make each unit hostage to the hub's record, which
#                         NORTH-STAR §2 says the platform must never be. Leg 4 PRINTS how many
#                         workflows in this repository key off a successful truth run, so the
#                         day one is added the scope of this stop changes visibly.
#
# HOW THE STOP IS PROVED, and this is the part a YAML reader cannot do. Leg 3 lifts the step's
# OWN SHELL verbatim out of truth.yml -- through verify/can-record/can_record.py, the same
# extractor ticket 100 uses -- and runs it over throwaway git repositories in FOURTEEN states,
# counted by the fixture itself as it runs them and printed in its PASS line (review round 3,
# 2026-09-08: three prose copies of this number had drifted to ten, eleven and fifteen): no
# fall; a class losing a pass; a rise in fail; a pass that became a could-not-look inside one
# class with `fail` unchanged (the degradation that used to go green); a ceiling that fell with
# a manifest commit between the two commits the lines name, without one, and with a comment-only
# touch; a total that fell with an exclusions commit, without one, and with a comment-only touch;
# a re-class of a passing script; a fall with a committed reason; a falls file naming a run the
# log does not record; and a fall on a branch. Each state is measured by what the step DOES: its
# exit status, whether it printed ::error::, and what it wrote to the step summary. Nothing is
# inferred from the YAML looking right.
#
# Everything the fixture writes lives under a mktemp directory and is deleted. Every TRUTH-shaped
# line it plants is dated 1970 with a `fixture` run number, so no reader could mistake one for an
# observation, and it never touches this repository's talk/truth.log.
#
# TWO LIMITS OF THE FIXTURE, named rather than left to be found. It grades ONE step's shell, not
# the whole job: a change made in a fourth step or in the job's `if:` is invisible here and is
# leg 2's business. And it runs the step under `bash`, not under the Actions runner, so
# `$GITHUB_STEP_SUMMARY` is a file the fixture provides and `::error::` is graded as text on
# stdout rather than as an annotation GitHub rendered.
#
#   PASS (exit 0)  the pure half grades planted data as documented, truth.yml still carries the
#                  step in the right place, the step's own shell blocks exactly the states ticket
#                  59 decided it should, and the transition ENDING AT THE RUN BEING RECORDED
#                  carries no unaccounted fall
#   FAIL (exit 1)  one of those is false, named
#
# WHICH TRANSITION LEG 5 GRADES, and why it is not "the newest line on disk" (ticket 108,
# 2026-09-09). The clock's recording commit appends the run's own TRUTH line and carries
# `[skip ci]`, so it moves this check's input and nothing re-measures. Read the newest line on
# disk and run N's gate grades the transition ending at run N-1 -- which run N-1's OWN step had
# already graded and already blocked on -- then the cage commits that stale red into
# talk/captures/_grades.tsv, where verify/derived-status/ reads it as a live regression of the
# ticket that built this check. Measured on this estate, 2026-09-09: main's committed grade table
# says this script FAILED, and this script PASSES on the very tree that table is committed on.
#
# So leg 5 grades the transition ending at the RUN BEING RECORDED, named by `--recording-run`:
# the newest recorded line when no run is in flight (a builder, a review, a throwaway merge onto
# origin/main -- where a fall on the record still blocks here, unchanged), and DEFERRED to
# truth.yml's own step when the run being recorded has not landed its line yet, because inside
# the gate that line cannot exist -- this check's own verdict is one of the counts in it. The
# older transition is still compared, still printed and still counted; it is never faulted twice.
# THE STOP IS UNCHANGED: truth.yml's `a fall is a blocking event` step runs after the cage, sees
# the run's own line, and reds the run. Leg 3 below grades that step and is untouched.
#
# ON A BRANCH OR PULL-REQUEST CI RUN LEG 5 ALSO DEFERS, and that reaches further than the first
# draft of this note said (review F5a). GITHUB_RUN_NUMBER is set on EVERY truth.yml run, not only
# the recording one, so a branch run defers too -- where it previously reddened on the DEFAULT
# branch's newest unaccounted fall. That is right and it blocks nothing: a branch records no line
# (ticket 100), so the newest transition in the log is main's and not this run's, which is the
# same reason truth.yml's own stop step reports and does not block on a branch. The comparison is
# still printed in full for a reader to quote. The EMPTY case -- graded exactly as before -- is a
# checkout with no run in flight at all: a builder, a review, a throwaway merge onto origin/main.
#
# THE KEY IS VALIDATED BEFORE IT IS TRUSTED. A non-numeric --recording-run is a FAULT, not a
# defer, and run numbers are compared by value so `0200` is run 200: deferring means not grading,
# and an escape hatch keyed on an unchecked string is the shape this ticket exists to refuse.
#
# NO could-not-look, by decision (ticket 59, delegated under ADR-0025), following
# verify/can-record/ and verify/cited-truth/. Everything this script reads is in this repository
# -- truth.yml, talk/truth.log, talk/verify-falls.txt, .git -- and everything it runs is git and
# python, both of which the gate installs before it. The states it could have shrugged in are RED
# with their own sentence: no python, no git, no workflow. A runner that has lost its interpreter
# should go red, not shrug. So this row's manifest entry declares no skip pattern and there is
# none to declare.
#
#   verify-a-fall-blocks.sh            selfcheck, then the fixture, then the committed record
#   verify-a-fall-blocks.sh selfcheck  the pure half and the fixture only; the record is not read
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || { echo "FAIL: cannot enter the hub root"; exit 1; }
WORKFLOW="$ROOT/.github/workflows/truth.yml"
STEP_NAME="a fall is a blocking event"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
bad=0
note() { echo "  !! $*"; bad=$((bad + 1)); }
ok()   { echo "  ok   $*"; }
ONLY_SELFCHECK=0; [ "${1:-}" = "selfcheck" ] && ONLY_SELFCHECK=1

PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "FAIL: no python to run the comparison with; a gate that has lost its interpreter goes red, it does not shrug"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "FAIL: no git; the ceiling and total rules are graded against a git diff, so there is nothing to measure with"; exit 1; }
[ -f "$WORKFLOW" ] || { echo "FAIL: $WORKFLOW is missing, so the stop this grades has nowhere to live"; exit 1; }

# ---------------------------------------------------------------- 1. the pure half
say "1. the comparison grades planted lines as documented: what is a fall, and what is not"
"$PY" talk/fall_check.py selfcheck || note "talk/fall_check.py selfcheck did not pass"

# ---------------------------------------------------------------- 2. the shape
say "2. truth.yml carries the stop, after the cage, failing the run on its own"
shape="$("$PY" - "$WORKFLOW" "$STEP_NAME" <<'EOF'
import sys
import yaml

path, want = sys.argv[1], sys.argv[2]
doc = yaml.safe_load(open(path, encoding="utf-8"))
steps = list((doc.get("jobs") or {}).get("gate", {}).get("steps") or [])
names = [str(s.get("name") or "") for s in steps]
problems = []


def index_of(fragment):
    for i, n in enumerate(names):
        if fragment in n:
            return i
    return -1


i_fall = index_of(want)
i_cage = index_of("observation cage")
i_gatefail = index_of("fail if the gate failed")
if i_fall < 0:
    problems.append(f"truth.yml's gate job has no step named {want!r}; the stop has nowhere to "
                    f"live, and a fall would be a number in a log nobody acts on")
else:
    shell = str(steps[i_fall].get("run") or "")
    if i_cage >= 0 and i_fall < i_cage:
        problems.append("the stop runs BEFORE the observation cage, so a fall would stop the "
                        "clock recording the very line that shows it; a clock appends "
                        "observations (ADR-0024) and the stop turns the run red afterwards")
    if "talk/fall_check.py" not in shell:
        problems.append("the step no longer runs talk/fall_check.py, so nothing compares the "
                        "two lines")
    if "talk/verify-falls.txt" not in shell:
        problems.append("the step no longer names talk/verify-falls.txt, so the escape hatch is "
                        "unreachable and an accepted fall could not be accepted")
    if "CAN_RECORD" not in shell:
        problems.append("the step does not consult CAN_RECORD, so a branch run -- which records "
                        "nothing (ticket 100) -- would be graded against a transition that is "
                        "not its own")
    if "::error::" not in shell:
        problems.append("the step raises no ::error:: annotation, so the fall is not the "
                        "distinct, unmissable failure ticket 59 asks for")
    if "exit 1" not in shell:
        problems.append("the step never exits nonzero, so it reports a fall and blocks nothing")
    if str(steps[i_fall].get("if") or "") == "":
        problems.append("the step has no `if:`, so a failing cage step would skip it and a fall "
                        "would go ungraded exactly on the runs that went wrong")
if i_gatefail >= 0 and i_fall >= 0 and i_fall > i_gatefail:
    problems.append("the stop runs after `fail if the gate failed`, which exits the job first, "
                    "so on a red gate the fall would never be graded")
print("\n".join(problems) if problems else
      f"the gate job's steps are: {' | '.join(n for n in names if n)}")
raise SystemExit(1 if problems else 0)
EOF
)"; src=$?
printf '  %s\n' "$shape"
[ "$src" -eq 0 ] || note "truth.yml no longer carries the stop in the shape ticket 59 decided"

# ---------------------------------------------------------------- 3. the mechanism
say "3. the step's own shell, lifted verbatim out of truth.yml, over throwaway repositories"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
if ! "$PY" verify/can-record/can_record.py step "$WORKFLOW" gate "$STEP_NAME" \
       >"$T/fall.sh" 2>"$T/fall.notes"; then
  note "could not lift the step named '$STEP_NAME' out of truth.yml"
  sed 's/^/       /' "$T/fall.notes"
  echo; echo "FAIL: the step could not be lifted out of truth.yml, so the stop could not be measured"
  exit 1
fi
sed 's/^/  (lift) /' "$T/fall.notes"

# THE RUNNER'S OWN FLAGS, read out of the step, never assumed (review F1, 2026-09-06). This step
# declares no `shell:`, so GitHub Actions executes it as `/usr/bin/bash -e {0}`; `set -uo
# pipefail` in the body does not clear `-e`. The first version of this fixture ran the lifted
# shell under a plain `bash`, so `-e` was OFF, so `out="$(...)"; rc=$?` survived a non-zero exit
# here and died on the runner -- and every state in which the checker exits 1 was measured under
# a shell the runner does not use. Six of the eleven states that then existed (fourteen now; the
# `states` counter below is the one place the number lives) were green for that reason alone.
# can_record.py step_shell_flags() is now the one place that answers "what will the runner run
# this under", so the fixture and the workflow cannot diverge again.
if ! FLAGS="$("$PY" verify/can-record/can_record.py stepshell "$WORKFLOW" gate "$STEP_NAME")"; then
  note "could not read the step's effective shell out of truth.yml"
  echo; echo "FAIL: the runner's own flags for this step could not be read, so running it under a guessed shell would prove nothing"
  exit 1
fi
# shellcheck disable=SC2086
ok "lifted the step's shell verbatim out of truth.yml ($(grep -c . "$T/fall.sh") lines), and it will be run under the runner's own flags: bash ${FLAGS:-<none>}"

export GIT_CONFIG_GLOBAL="$T/gitconfig" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
: >"$GIT_CONFIG_GLOBAL"
git config --global init.defaultBranch main
git config --global user.name "fixture"
git config --global user.email "fixture@example.invalid"
git config --global commit.gpgsign false

# A TRUTH-shaped line. Dated 1970 and numbered `fixture-N` so nothing here could be read as an
# observation of this estate.
line() { # <run> <hub> <observed> <meta> <fail> <waits> <total> <ceiling>
  local run="$1" hub="$2" observed="$3" meta="$4" fail="$5" waits="$6" total="$7" ceiling="$8"
  printf 'TRUTH 1970-01-01T00:00Z run=%s hub=%s enact=development units=[fixture] pass=%s [observed=%s self=20 simulated=5 meta=%s] fail=%s skip=%s [never=2 waits=%s] excluded=8 total=%s ceiling=%s\n' \
    "$run" "$hub" "$((observed + 25 + meta))" "$observed" "$meta" "$fail" "$((2 + waits))" \
    "$waits" "$total" "$ceiling"
}

# new_repo <dir> <touch>: a git repository with two commits. <touch> names the file the SECOND
# commit changes -- `manifest`, `exclusions` or `other` -- which is exactly what the ceiling and
# total rules read. Echoes "<sha1> <sha2>".
new_repo() {
  local d="$1" touch="$2"
  mkdir -p "$d/talk"
  cp "$ROOT/talk/fall_check.py" "$ROOT/talk/truth_manifest.py" "$d/talk/"
  git -C "$d" init -q
  printf 'a/verify-a.sh | meta | -\n' >"$d/talk/verify-manifest.txt"
  printf 'x/verify-x.sh | helper\n' >"$d/talk/verify-exclusions.txt"
  printf 'nothing\n' >"$d/other.txt"
  : >"$d/talk/truth.log"
  git -C "$d" add -A >/dev/null && git -C "$d" commit -qm one
  case "$touch" in
    manifest)   printf 'b/verify-b.sh | meta | never: nothing here can look\n' >>"$d/talk/verify-manifest.txt" ;;
    exclusions) printf 'y/verify-y.sh | a second helper\n' >>"$d/talk/verify-exclusions.txt" ;;
    # A COMMENT-ONLY touch of BOTH record files (review F5, 2026-09-06). The excuse used to be
    # granted by file NAME, so this -- which this repository does several times a week -- excused
    # any ceiling or total drop at all. Nothing a reader of either file would act on has changed.
    comments)   printf '# a note about the class legend\n' >>"$d/talk/verify-manifest.txt"
                printf '# a note about why this one is excluded\n' >>"$d/talk/verify-exclusions.txt" ;;
    *)          printf 'something\n' >>"$d/other.txt" ;;
  esac
  git -C "$d" add -A >/dev/null && git -C "$d" commit -qm two
  echo "$(git -C "$d" rev-parse HEAD~1) $(git -C "$d" rev-parse HEAD)"
}

# run_step <dir> <can_record>: run the lifted shell in <dir>. Echoes "<rc>".
run_step() {
  local d="$1" can="$2"
  : >"$d/summary"
  # ${FLAGS} unquoted on purpose: it is a word list of shell flags, not one argument.
  # shellcheck disable=SC2086
  ( cd "$d" && CAN_RECORD="$can" GITHUB_STEP_SUMMARY="$d/summary" GITHUB_RUN_NUMBER=fixture-run \
      bash ${FLAGS} "$T/fall.sh" ) >"$d/out" 2>&1
  echo $?
}

# grade_case <name> <touch> <falls> <can_record> <expect-rc> <expect-blocked> <what>
#   the two planted lines come from LINE_A and LINE_B, set by the caller with the two shas
#   substituted in; <expect-blocked> is yes when the step must print the ::error::
states=0
grade_case() {
  local name="$1" touch="$2" falls="$3" can="$4" want_rc="$5" want_block="$6" what="$7"
  local d="$T/$name"
  states=$((states + 1))
  local shas; shas="$(new_repo "$d" "$touch")"
  SHA1="${shas%% *}"; SHA2="${shas##* }"
  eval "printf '%s\n' \"$LINE_A\" \"$LINE_B\"" >"$d/talk/truth.log"
  printf '%s\n' "$falls" >"$d/talk/verify-falls.txt"
  local rc; rc="$(run_step "$d" "$can")"
  local blocked=no
  grep -q '::error::' "$d/out" && blocked=yes
  printf '  %-22s rc=%-2s blocked=%-3s  %s\n' "$name" "$rc" "$blocked" "$what"
  if [ "$rc" = "$want_rc" ] && [ "$blocked" = "$want_block" ]; then
    ok "$name: the step did what ticket 59 decided (rc=$want_rc, blocked=$want_block)"
  else
    note "$name: the step exited $rc and blocked=$blocked, where ticket 59 decided rc=$want_rc blocked=$want_block"
    sed 's/^/       /' "$d/out"
  fi
  # the step summary is the artefact a reader of a red run opens first
  grep -q 'transition' "$d/summary" 2>/dev/null \
    || note "$name: the step wrote no transition line to \$GITHUB_STEP_SUMMARY"
}

# The states. LINE_A and LINE_B are evaluated inside grade_case with $SHA1/$SHA2 bound.
LINE_A='$(line fixture-1 $SHA1 10 3 4 3 60 55)'

LINE_B='$(line fixture-2 $SHA2 10 3 4 3 60 55)'
grade_case no-fall other "" yes 0 no "nothing moved"

LINE_B='$(line fixture-2 $SHA2 9 3 4 4 60 55)'
grade_case class-lost-a-pass other "" yes 1 yes "the observed class fell 10 -> 9"

LINE_B='$(line fixture-2 $SHA2 10 3 5 2 60 55)'
grade_case fail-rose other "" yes 1 yes "fail rose 4 -> 5"

LINE_B='$(line fixture-2 $SHA2 10 2 4 4 60 55)'
grade_case pass-became-a-skip other "" yes 1 yes "meta 3 -> 2 with fail unchanged: the degradation that used to go green"

LINE_B='$(line fixture-2 $SHA2 10 3 4 3 60 54)'
grade_case ceiling-fell-with-manifest manifest "" yes 0 no "a re-class lowered the ceiling and the manifest moved in the same span: not a fall"
grade_case ceiling-fell-alone other "" yes 1 yes "the ceiling fell with no manifest change: a fall"
grade_case ceiling-fell-comment-only comments "" yes 1 yes "the manifest was touched but only its COMMENTS moved: still a fall (review F5)"

LINE_B='$(line fixture-2 $SHA2 10 3 4 3 59 55)'
grade_case total-fell-with-exclusion exclusions "" yes 0 no "an exclusion lowered the total: not a fall"
grade_case total-fell-alone other "" yes 1 yes "the total fell with no exclusions change: a fall"
grade_case total-fell-comment-only comments "" yes 1 yes "the exclusions file was touched but only its COMMENTS moved: still a fall (review F5)"

# A re-class that moves a PASSING script between classes: the split sum does not fall, so nothing
# became a could-not-look, and the message must not say one did (review F3).
LINE_A='$(line fixture-1 $SHA1 10 3 4 3 60 55)'
LINE_B='$(line fixture-2 $SHA2 9 4 4 3 60 55)'
grade_case reclass-of-a-passing-script manifest "" yes 1 yes "a passing script moved class: a fall, and reported as a re-class rather than a lost look"

LINE_B='$(line fixture-2 $SHA2 9 3 4 4 60 55)'
grade_case fall-with-a-reason other \
  "run=fixture-2 | the observed lane lost a sample on purpose; ticket 61 owns getting it back" \
  yes 0 no "a committed reason accepts the fall"
grade_case reason-for-an-unrecorded-run other \
  "run=fixture-99 | a reason for a run the log does not record" \
  yes 1 yes "the escape hatch names a run talk/truth.log has never recorded"
grade_case fall-on-a-branch other "" no 0 no "a branch recorded nothing, so the transition is not this run's and blocks nothing"

# ---------------------------------------------------------------- 4. what keys off a green run
say "4. how much this stop reaches, as a number rather than a claim"
downstream="$("$PY" - <<'EOF'
import pathlib

import yaml

# A workflow that keys off another workflow finishing. Counted, not asserted: ticket 59 decided
# the stop is this repository's own run conclusion because no unit may be made hostage to the
# hub's number, and the day something here does key off a green truth run the scope of the stop
# changes. A sentence saying "nothing does" would rot; this number does not.
hits = []
for p in sorted(pathlib.Path(".github/workflows").glob("*.y*ml")):
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    on = doc.get("on") if "on" in doc else doc.get(True)     # YAML 1.1 reads bare `on` as True
    triggers = on if isinstance(on, dict) else {on: None} if isinstance(on, str) else {}
    if "workflow_run" in triggers:
        hits.append(p.name)
print(f"{len(hits)} of {len(list(pathlib.Path('.github/workflows').glob('*.y*ml')))} workflows in "
      f"this repository are triggered by another workflow finishing"
      + (f": {', '.join(hits)}" if hits else
         ", so today this stop reaches this run's own conclusion and nothing downstream"))
EOF
)"
printf '  %s\n' "$downstream"

# ---------------------------------------------------------------- 5. the committed record
if [ "$ONLY_SELFCHECK" = 1 ]; then
  echo
  if [ "$bad" -eq 0 ]; then
    echo "PASS: selfcheck: the comparison grades planted lines as documented, truth.yml carries the stop after the cage, and the step's own shell -- run over throwaway git repositories in $states states -- blocks a lost pass, a rise in fail, a pass that became a could-not-look, an unexplained ceiling and an unexplained total, while letting a re-class, an exclusion, an accepted fall and a branch run through"
    exit 0
  fi
  echo "FAIL: $bad selfcheck fault(s) (named above)"
  exit 1
fi

# THE TRANSITION THIS PROCESS OWNS IS THE ONE ENDING AT THE RUN BEING RECORDED (ticket 108).
# `--recording-run` is passed from GITHUB_RUN_NUMBER, and it is passed HERE rather than read
# inside talk/fall_check.py, because leg 3 above lifts truth.yml's own step shell and runs it over
# planted logs whose runs are named `fixture-N`: a run number picked up implicitly by the module
# would defer every one of those fourteen states the moment this script ran in CI, and the fixture
# would grade nothing while still printing fourteen ok lines.
#
# Empty (a builder, a review, a throwaway merge onto origin/main) -> the run being recorded is the
# newest line the log carries and the transition ending at it is graded, exactly as before: a fall
# on the record still blocks here. Set, and its line not in the log yet (the GATE of a clock run,
# where this comparison's own verdict is one of the counts in the line that does not exist) ->
# DEFERRED to truth.yml's `a fall is a blocking event` step, which runs after the cage has recorded
# it. That step is unchanged by ticket 108 and is where NORTH-STAR §5's stop lives.
#
# What the split removes: without it, run N's gate re-graded the transition ending at run N-1 --
# which run N-1's own step had already graded and already blocked on -- and wrote that stale red
# into talk/captures/_grades.tsv, where verify/derived-status/ read it as a live regression of the
# ticket that built this check. Measured on this estate: main's committed grade table said this
# script FAILED while this script PASSED on the very tree that table is committed on.
say "5. the transition ending at the run being recorded carries no unaccounted fall"
record="$("$PY" talk/fall_check.py check --log talk/truth.log --falls talk/verify-falls.txt \
            --root "$ROOT" --recording-run "${GITHUB_RUN_NUMBER:-}")"; rrc=$?
printf '%s\n' "$record"
[ "$rrc" -eq 0 ] || note "the transition ending at the run being recorded carries a fall no committed reason accepts"

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: talk/fall_check.py grades planted lines as ticket 83's contract documents, truth.yml carries the stop as a step of its own after the observation cage, that step's OWN shell -- lifted verbatim and run over throwaway git repositories in $states states -- turns the run red on a lost class pass, a rise in fail, a pass that became a could-not-look, an unexplained ceiling and an unexplained total while letting a re-class, an exclusion, an accepted fall and a branch run through, and the transition ending at the run being recorded carries no fall no committed reason accepts -- deferring that transition to truth.yml's own step, and never re-grading it, when the run being recorded has not yet landed its line (ticket 108)"
  exit 0
fi
echo "FAIL: $bad fault(s) -- a fall in the citable number is not a blocking event (ticket 59)"
exit 1
