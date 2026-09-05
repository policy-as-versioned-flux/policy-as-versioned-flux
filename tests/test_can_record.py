"""Ecosystem ticket 100: a branch run says what it can record, before it measures.

Two seams, and this file is the pure one.

`verify/can-record/can_record.py` holds three questions that are decidable from data:

1. **the shape** -- does `.github/workflows/truth.yml` still carry the guard this ticket put in
   front of the measurement, in the order that makes it a guard, and does it still push the one
   refspec it is allowed to push;
2. **the record** -- is every TRUTH line in `talk/truth.log` blamed to the clock commit whose
   message names the same run number, so no line in the log was written by a hand;
3. **the extraction** -- can the fixture lift a step's own shell out of the workflow, and does it
   say out loud what it changed to run it off the runner.

What is NOT here: whether the guard's verdict is TRUE of git. No amount of reading the YAML
settles that. `verify/can-record/verify-can-record.sh` answers it by running the workflow's own
shell over two throwaway repositories and comparing the guard's verdict with what the push
actually does to the remote ref, in every case including the one that reproduces run 98's
`! [rejected] (non-fast-forward)`.
"""
from __future__ import annotations

import copy
import importlib.util
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "truth.yml"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cr = _load("can_record", ROOT / "verify" / "can-record" / "can_record.py")


def _doc() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


# -- 1. the shape of the workflow this ticket decided ---------------------------------------------


def _repo(tmp_path: Path) -> Path:
    """A throwaway git repository with a talk/truth.log carrying one clock-written line."""
    repo = tmp_path / "repo"
    (repo / "talk").mkdir(parents=True)
    env = dict(os.environ, GIT_AUTHOR_NAME="truth", GIT_AUTHOR_EMAIL=cr.CLOCK_EMAIL,
               GIT_COMMITTER_NAME="truth", GIT_COMMITTER_EMAIL=cr.CLOCK_EMAIL)
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "chris@cns.me.uk"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Chris Nesbitt-Smith"], check=True)
    (repo / "talk" / "truth.log").write_text(
        "TRUTH 2026-01-01T00:00Z run=1 hub=0000000 pass=1 fail=0\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "truth: record run 1 [skip ci]"],
                   check=True, capture_output=True, env=env)
    return repo


def test_the_committed_workflow_carries_the_shape() -> None:
    assert cr.shape_faults(_doc(), _text()) == []


def test_a_gate_checkout_that_is_shallow_cannot_answer_the_question() -> None:
    doc = _doc()
    for step in doc["jobs"]["gate"]["steps"]:
        if str(step.get("uses", "")).startswith("actions/checkout"):
            step["with"].pop("fetch-depth", None)
    faults = cr.shape_faults(doc, _text())
    assert any("fetch-depth" in f for f in faults), faults


def test_removing_the_guard_step_is_a_fault() -> None:
    doc = _doc()
    steps = doc["jobs"]["gate"]["steps"]
    doc["jobs"]["gate"]["steps"] = [s for s in steps if cr.GUARD_STEP not in str(s.get("name", ""))]
    faults = cr.shape_faults(doc, _text())
    assert any(cr.GUARD_STEP in f for f in faults), faults


def test_a_guard_that_runs_after_the_measurement_is_not_a_guard() -> None:
    doc = _doc()
    steps = doc["jobs"]["gate"]["steps"]
    guard = [s for s in steps if cr.GUARD_STEP in str(s.get("name", ""))][0]
    rest = [s for s in steps if s is not guard]
    doc["jobs"]["gate"]["steps"] = rest + [guard]
    faults = cr.shape_faults(doc, _text())
    assert any("before" in f for f in faults), faults


def test_a_guard_that_takes_the_default_branch_from_a_literal_is_a_fault() -> None:
    doc = _doc()
    for step in doc["jobs"]["gate"]["steps"]:
        if cr.GUARD_STEP in str(step.get("name", "")):
            step["env"] = {"DEFAULT_BRANCH": "main"}
    faults = cr.shape_faults(doc, _text())
    assert any("default_branch" in f for f in faults), faults


def test_a_guard_that_does_not_compare_the_ref_with_the_default_branch_is_a_fault() -> None:
    doc = _doc()
    for step in doc["jobs"]["gate"]["steps"]:
        if cr.GUARD_STEP in str(step.get("name", "")):
            step["run"] = 'echo "CAN_RECORD=yes" >> "$GITHUB_ENV"\n'
    faults = cr.shape_faults(doc, _text())
    assert any("GITHUB_REF_NAME" in f for f in faults), faults


def test_a_record_step_that_appends_unconditionally_is_a_fault() -> None:
    doc = _doc()
    for step in doc["jobs"]["gate"]["steps"]:
        if cr.RECORD_STEP in str(step.get("name", "")):
            step["run"] = 'grep "^TRUTH " "$RUNNER_TEMP/gate.out" | tee -a talk/truth.log\n'
    faults = cr.shape_faults(doc, _text())
    assert any(cr.RECORD_STEP in f for f in faults), faults


def test_a_cage_that_commits_before_it_consults_the_guard_is_a_fault() -> None:
    doc = _doc()
    for step in doc["jobs"]["gate"]["steps"]:
        if cr.CAGE_STEP in str(step.get("name", "")):
            step["run"] = step["run"].replace("${CAN_RECORD}", "${NOT_THE_GUARD}")
    faults = cr.shape_faults(doc, _text())
    assert any(cr.CAGE_STEP in f for f in faults), faults


def test_a_force_push_anywhere_in_the_workflow_is_a_fault() -> None:
    text = _text().replace('push origin HEAD:"${GITHUB_REF_NAME}"',
                           'push --force origin HEAD:"${GITHUB_REF_NAME}"')
    faults = cr.shape_faults(_doc(), text)
    assert any("force" in f for f in faults), faults


def test_a_plus_refspec_is_a_force_push_by_another_name() -> None:
    text = _text().replace('push origin HEAD:"${GITHUB_REF_NAME}"',
                           'push origin +HEAD:"${GITHUB_REF_NAME}"')
    faults = cr.shape_faults(_doc(), text)
    assert any("force" in f for f in faults), faults


def test_losing_the_one_allowed_refspec_is_a_fault() -> None:
    doc = _doc()
    for step in doc["jobs"]["gate"]["steps"]:
        if cr.CAGE_STEP in str(step.get("name", "")):
            step["run"] = step["run"].replace('HEAD:"${GITHUB_REF_NAME}"', "HEAD:main")
    faults = cr.shape_faults(doc, _text())
    assert any("refspec" in f for f in faults), faults


# -- 2. the record: who wrote each line of talk/truth.log ------------------------------------------

def _row(line: str, email: str, subject: str, commit: str = "abc1234") -> Any:
    return cr.TruthRow(line=line, email=email, subject=subject, commit=commit)


CLOCK = "truth@users.noreply.github.com"


def test_a_clock_line_blamed_to_its_own_run_commit_is_clean() -> None:
    rows = [_row("TRUTH 2026-09-05T09:44Z run=99 hub=e68a82a pass=68", CLOCK,
                 "truth: record run 99 [skip ci]")]
    assert cr.truth_log_faults(rows) == []


def test_a_line_a_hand_wrote_is_named() -> None:
    rows = [_row("TRUTH 2026-09-05T09:44Z run=99 hub=e68a82a pass=68",
                 "chris@cns.me.uk", "Ticket 100: tidy the log")]
    faults = cr.truth_log_faults(rows)
    assert len(faults) == 1
    assert "run=99" in faults[0] and "chris@cns.me.uk" in faults[0]


def test_a_line_whose_run_number_disagrees_with_its_commit_is_named() -> None:
    rows = [_row("TRUTH 2026-09-05T09:44Z run=99 hub=e68a82a pass=68", CLOCK,
                 "truth: record run 87 [skip ci]")]
    faults = cr.truth_log_faults(rows)
    assert len(faults) == 1
    assert "87" in faults[0] and "99" in faults[0]


def test_the_one_historical_local_line_is_allowed_and_a_second_is_not() -> None:
    local = _row("TRUTH 2026-08-28T04:00Z run=local hub=2326f31 pass=40",
                 "chris@cns.me.uk", "the local gate")
    assert cr.truth_log_faults([local]) == []
    faults = cr.truth_log_faults([local, copy.copy(local)])
    assert len(faults) == 1
    assert "run=local" in faults[0]


def test_a_run_that_is_neither_a_number_nor_local_is_named() -> None:
    rows = [_row("TRUTH 2026-09-05T09:44Z run=rehearsal hub=e68a82a", CLOCK, "truth: record")]
    faults = cr.truth_log_faults(rows)
    assert len(faults) == 1
    assert "rehearsal" in faults[0]


def test_the_clock_never_writes_a_line_that_names_no_run_number() -> None:
    rows = [_row("TRUTH 2026-08-28T04:00Z run=local hub=2326f31", CLOCK,
                 "truth: record run 4 [skip ci]")]
    faults = cr.truth_log_faults(rows)
    assert len(faults) == 1
    assert "local" in faults[0]


def test_the_committed_log_is_clean_under_the_rule() -> None:
    rows = cr.blame_rows(ROOT)
    assert rows, "talk/truth.log carries no TRUTH line"
    assert cr.truth_log_faults(rows) == []


# -- 2b. the third failure mode: a line landed on a branch that then merged without it -------------
#
# Run 101 landed on ticket-89-deny-is-not-a-rung at 14:45Z on 2026-09-05, three minutes after that
# branch was merged to main at 14:42Z, so main's log went from run 100 to run 102. The tree it
# measured was already on main, so the observation was citable; only the line was stranded. The
# integrator rescued that one by cherry-picking the clock's own commit. Runs 76, 84 and 88 were
# stranded the same way and nobody had noticed until this check looked.

def _stranded(run: str, in_log: bool, on_main: bool) -> Any:
    return cr.Stranded(commit="abc1234", ref="origin/ticket-x",
                       line=f"TRUTH 2026-09-05T01:20Z run={run} hub=17106c2 pass=60",
                       in_main_log=in_log, tree_on_main=on_main)


def test_a_citable_line_that_never_reached_the_default_branch_is_a_fault() -> None:
    faults, notes = cr.stranded_faults([_stranded("88", in_log=False, on_main=True)])
    assert len(faults) == 1 and notes == []
    assert "run=88" in faults[0]


def test_a_rescued_line_is_a_note_not_a_fault() -> None:
    faults, notes = cr.stranded_faults([_stranded("101", in_log=True, on_main=True)])
    assert faults == [] and len(notes) == 1


def test_a_line_measuring_a_tree_the_default_branch_never_had_is_a_note() -> None:
    faults, notes = cr.stranded_faults([_stranded("9", in_log=False, on_main=False)])
    assert faults == [] and len(notes) == 1
    assert "correctly absent" in notes[0]


def test_stranded_entries_reads_the_refs_this_checkout_carries() -> None:
    entries, refs = cr.stranded_entries(ROOT)
    # No assertion about how many: a runner checkout may carry one ref and a laptop fifty, and a
    # branch already deleted cannot be seen from either. What is asserted is that every entry it
    # does return is coherent enough to grade.
    for e in entries:
        assert e.line.startswith("TRUTH ") and len(e.commit) == 7
        assert isinstance(e.in_main_log, bool) and isinstance(e.tree_on_main, bool)
    assert isinstance(refs, list)


# -- 3. the extraction the fixture runs ------------------------------------------------------------

def test_a_named_step_is_lifted_whole() -> None:
    shell = cr.step_shell(_doc(), "gate", cr.CAGE_STEP)
    assert "git reset -q" in shell
    assert 'push origin HEAD:"${GITHUB_REF_NAME}"' in shell


def test_an_unknown_step_name_raises_rather_than_returning_empty_shell() -> None:
    try:
        cr.step_shell(_doc(), "gate", "a step that does not exist")
    except KeyError:
        return
    raise AssertionError("an unknown step name returned a shell instead of raising")


def test_every_substitution_the_fixture_makes_is_declared() -> None:
    shell, notes = cr.portable(cr.step_shell(_doc(), "gate", cr.CAGE_STEP))
    assert notes, "the cage's shell needs at least the signing substitution off the runner"
    for note in notes:
        before, after = note.split(" -> ", 1)
        assert before.strip() not in shell, note
        assert after.strip() in shell, note


def test_the_substitutions_leave_the_push_line_alone() -> None:
    shell, _ = cr.portable(cr.step_shell(_doc(), "gate", cr.CAGE_STEP))
    assert 'push origin HEAD:"${GITHUB_REF_NAME}"' in shell


# -- 4. a legitimate repair grades clean; a hand-authored line still does not ---------------------
#
# Measured on main on 2026-09-05, after the rescue of runs 76, 84 and 88 was reverted and redone
# as cherry-picks of the clock's own commits: `git blame` STILL named the hand's commit, because
# at the merge it prefers the parent where identical content already existed. This check reported
# three faults on a log that had been put right -- a false red on the citable branch, and the
# reviewer's grading of the branch before the merge could not see it. The rule wants the commit
# that put the line where it now is, which `git blame` does not answer.


def _clock_commit(repo, message, env_extra=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="truth", GIT_AUTHOR_EMAIL=cr.CLOCK_EMAIL,
               GIT_COMMITTER_NAME="truth", GIT_COMMITTER_EMAIL=cr.CLOCK_EMAIL)
    env.update(env_extra or {})
    subprocess.run(["git", "-C", str(repo), "commit", "-am", message], check=True, env=env,
                   capture_output=True)


def test_a_reverted_then_clock_readded_line_attributes_to_the_clock(tmp_path) -> None:
    repo = _repo(tmp_path)                      # helper already used by this module
    log = repo / "talk" / "truth.log"
    line = "TRUTH 2026-09-04T16:34Z run=76 hub=7d9b6a0 pass=1 fail=0"

    # a hand adds it -- the fault this check exists for
    log.write_text(log.read_text() + line + "\n")
    subprocess.run(["git", "-C", str(repo), "commit", "-am", "hand-authored rescue"],
                   check=True, capture_output=True)
    rows = cr.blame_rows(repo)
    assert any(r.line == line and r.email != cr.CLOCK_EMAIL for r in rows), \
        "a hand-authored line must still fault"
    assert cr.truth_log_faults(rows), "a hand-authored line must still fault"

    # reverted, then re-added by the clock: the legitimate repair
    log.write_text(log.read_text().replace(line + "\n", ""))
    subprocess.run(["git", "-C", str(repo), "commit", "-am", "Revert the hand-authored rescue"],
                   check=True, capture_output=True)
    log.write_text(log.read_text() + line + "\n")
    _clock_commit(repo, "truth: record run 76 [skip ci]")

    rows = cr.blame_rows(repo)
    row = next(r for r in rows if r.line == line)
    assert row.email == cr.CLOCK_EMAIL, (
        f"after a revert and a clock re-add the line attributed to {row.email}; git blame names "
        f"the hand here, which is why this uses the adding commit instead")
    assert cr.truth_log_faults(rows) == [], cr.truth_log_faults(rows)


def test_a_line_no_commit_adds_is_a_fault_not_a_shrug(tmp_path) -> None:
    repo = _repo(tmp_path)
    (repo / "talk" / "truth.log").write_text(
        (repo / "talk" / "truth.log").read_text() + "TRUTH 2026-01-01T00:00Z run=999 pass=1\n")
    # deliberately NOT committed: no commit in history adds this line
    with pytest.raises(cr.GitFailed) as e:
        cr.blame_rows(repo)
    assert "no commit in this history adds the line" in str(e.value)
