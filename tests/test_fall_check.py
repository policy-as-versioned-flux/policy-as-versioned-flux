"""talk/fall_check.py: a fall is a blocking event (NORTH-STAR §5, eco-system ticket 59).

The seam is the comparison of two consecutive TRUTH lines, class by class, against the diff of
the two commits they name. These tests pin what a FALL is and what one is not -- the two ways a
ceiling or a total may legitimately move -- and the escape hatch's validation against the log.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
for _name in ("truth_manifest", "fall_check"):
    _spec = importlib.util.spec_from_file_location(_name, _ROOT / "talk" / f"{_name}.py")
    assert _spec is not None and _spec.loader is not None
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_name] = _mod
    _spec.loader.exec_module(_mod)
fc = sys.modules["fall_check"]


def line(run: str, hub: str = "aaaaaaa", *, observed: int = 10, self_: int = 20,
         simulated: int = 5, meta: int = 3, fail: int = 4, never: int = 2, waits: int = 3,
         excluded: int = 8, total: int = 60, ceiling: int = 55) -> str:
    passed = observed + self_ + simulated + meta
    skip = never + waits
    return (f"TRUTH 2026-09-06T09:00Z run={run} hub={hub} enact=development units=[u=1@main] "
            f"pass={passed} [observed={observed} self={self_} simulated={simulated} meta={meta}] "
            f"fail={fail} skip={skip} [never={never} waits={waits}] excluded={excluded} "
            f"total={total} ceiling={ceiling}")


# ------------------------------------------------------------------ what a fall is

def test_two_identical_lines_are_not_a_fall() -> None:
    assert fc.compare(line("1"), line("2"), changed=set()) == []


def test_a_class_losing_a_pass_is_a_fall_named_by_class() -> None:
    falls = fc.compare(line("1", observed=10), line("2", observed=9, waits=4), changed=set())
    assert len(falls) == 1
    assert falls[0].kind == "class-pass"
    assert "observed" in falls[0].detail and "10" in falls[0].detail and "9" in falls[0].detail


def test_a_pass_that_became_a_skip_inside_one_class_is_a_fall_though_fail_is_unchanged() -> None:
    """The case the contract calls out: fail is identical, so a bare pass/fail reading sees
    nothing. Only the class split and the skip split together say a green stopped looking."""
    before = line("1", meta=3, waits=3, fail=4)
    after = line("2", meta=2, waits=4, fail=4)
    falls = fc.compare(before, after, changed=set())
    assert [f.kind for f in falls] == ["class-pass"]
    assert "became a could-not-look" in falls[0].detail


def test_a_rise_in_fail_is_a_fall() -> None:
    falls = fc.compare(line("1", fail=4), line("2", fail=5, waits=2), changed=set())
    assert any(f.kind == "fail" for f in falls)


def test_a_fall_in_pass_with_no_split_on_either_line_still_reads_the_bare_count() -> None:
    old = "TRUTH 2026-09-03T19:09Z run=1 hub=aaaaaaa units=[] pass=58 fail=7 skip=18 excluded=2 total=85"
    new = "TRUTH 2026-09-03T20:09Z run=2 hub=bbbbbbb units=[] pass=57 fail=7 skip=19 excluded=2 total=85"
    falls = fc.compare(old, new, changed=set())
    assert [f.kind for f in falls] == ["pass"]
    assert "no split" in falls[0].detail


# ------------------------------------------------------------------ what a fall is not

def test_a_ceiling_that_fell_with_a_manifest_change_in_the_same_span_is_not_a_fall() -> None:
    """A script re-classed `never` lowers the ceiling. That is the manifest telling the truth
    about what can never pass, not the estate losing a green."""
    falls = fc.compare(line("1", ceiling=55), line("2", ceiling=54),
                       changed={"talk/verify-manifest.txt"})
    assert falls == []


def test_a_ceiling_that_fell_with_no_manifest_change_is_a_fall() -> None:
    falls = fc.compare(line("1", ceiling=55), line("2", ceiling=54), changed=set())
    assert [f.kind for f in falls] == ["ceiling"]


def test_a_total_that_fell_with_an_exclusions_change_is_not_a_fall() -> None:
    falls = fc.compare(line("1", total=60, ceiling=55), line("2", total=59, ceiling=55),
                       changed={"talk/verify-exclusions.txt"})
    assert falls == []


def test_a_total_that_fell_with_no_exclusions_change_is_a_fall() -> None:
    falls = fc.compare(line("1", total=60), line("2", total=59), changed=set())
    assert [f.kind for f in falls] == ["total"]


def test_a_manifest_change_does_not_excuse_a_lost_pass() -> None:
    """The escape for a moving ceiling is not an escape for anything else: the two rules that
    consult the diff are the ceiling's and the total's, and no other."""
    falls = fc.compare(line("1", observed=10, ceiling=55), line("2", observed=9, waits=4, ceiling=54),
                       changed={"talk/verify-manifest.txt", "talk/verify-exclusions.txt"})
    assert [f.kind for f in falls] == ["class-pass"]


def test_a_run_the_diff_cannot_be_read_for_treats_a_ceiling_drop_as_a_fall_and_says_so() -> None:
    falls = fc.compare(line("1", ceiling=55), line("2", ceiling=54), changed=None)
    assert [f.kind for f in falls] == ["ceiling"]
    assert "could not read" in falls[0].detail


# ------------------------------------------------------------------ the escape hatch

FALLS = """# committed reasons, one per accepted fall
run=105 | the platform pin bump reddened four adopter checks; owned by ticket 61
run=113 | a deliberate re-class
"""


def test_the_escape_file_parses_run_and_reason() -> None:
    accepted, problems = fc.parse_falls(FALLS)
    assert problems == []
    assert set(accepted) == {"105", "113"}
    assert accepted["105"].startswith("the platform pin bump")


def test_an_escape_line_naming_a_run_the_log_does_not_record_is_itself_a_fail() -> None:
    accepted, _ = fc.parse_falls(FALLS)
    problems = fc.falls_problems(accepted, recorded={"105", "122"})
    assert len(problems) == 1
    assert "113" in problems[0]


def test_an_escape_line_with_no_reason_is_refused() -> None:
    _, problems = fc.parse_falls("run=105 |   \n")
    assert len(problems) == 1 and "reason" in problems[0]


def test_an_escape_line_that_is_not_run_n_pipe_reason_is_refused() -> None:
    _, problems = fc.parse_falls("105 the number fell\n")
    assert len(problems) == 1 and "run=N | reason" in problems[0]


# ------------------------------------------------------------------ the report

def test_the_report_grades_the_newest_transition_and_only_counts_the_older_ones() -> None:
    """The recorded log is append-only, so an old fall has no finishing move and is REPORTED as
    a number rather than failed forever (the shape ticket 55 rules out). The newest transition
    is the one a run can still do something about."""
    log = [line("1", observed=10), line("2", observed=9, waits=4), line("3", observed=9)]
    rep = fc.report(log, falls_text="", changed=lambda a, b: set())
    assert rep.newest == []
    assert rep.older_unaccounted == 1
    assert rep.ok is True


def test_an_unaccounted_fall_on_the_newest_transition_fails_the_report() -> None:
    log = [line("1", observed=10), line("2", observed=9, waits=4)]
    rep = fc.report(log, falls_text="", changed=lambda a, b: set())
    assert rep.ok is False and len(rep.newest) == 1


def test_a_committed_reason_for_the_newest_run_accepts_the_fall() -> None:
    log = [line("1", observed=10), line("2", observed=9, waits=4)]
    rep = fc.report(log, falls_text="run=2 | the observed lane lost a sample; ticket 61 owns it",
                    changed=lambda a, b: set())
    assert rep.ok is True and len(rep.newest) == 1 and rep.accepted_reason


def test_a_reason_committed_for_the_wrong_run_does_not_accept_the_fall() -> None:
    log = [line("1", observed=10), line("2", observed=9, waits=4)]
    rep = fc.report(log, falls_text="run=1 | not this transition", changed=lambda a, b: set())
    assert rep.ok is False


def test_a_log_with_one_line_has_nothing_to_compare_and_says_so() -> None:
    rep = fc.report([line("1")], falls_text="", changed=lambda a, b: set())
    assert rep.ok is True and rep.newest == [] and "one recorded line" in rep.note


@pytest.mark.parametrize("bad", ["", "not a truth line\n"])
def test_a_log_with_no_truth_line_is_not_a_crash(bad: str) -> None:
    rep = fc.report([l for l in bad.splitlines() if l.startswith("TRUTH ")],
                    falls_text="", changed=lambda a, b: set())
    assert rep.ok is True and "no recorded" in rep.note


# ------------------------------------------------------------------ review 2026-09-06, F3

def test_a_reclass_that_moves_a_passing_script_between_classes_is_not_called_a_lost_look() -> None:
    """F3. The split sum is unchanged and the manifest moved in the span: a PASSING script was
    re-classed. It is still a fall by the contract (a class's passes fell), but nothing became a
    could-not-look and the message must not say one did."""
    before = line("1", observed=10, meta=3)
    after = line("2", observed=9, meta=4)
    falls = fc.compare(before, after, changed={"talk/verify-manifest.txt"})
    assert [f.kind for f in falls] == ["class-pass"]
    assert "became a could-not-look" not in falls[0].detail
    assert "between classes" in falls[0].detail


def test_a_lost_pass_with_no_cause_visible_does_not_invent_one() -> None:
    """Total passes fell, fail did not rise and skips did not rise: something left the surface.
    The message says what is known and names nothing it cannot see."""
    falls = fc.compare(line("1", observed=10, total=60), line("2", observed=9, total=59),
                       changed={"talk/verify-exclusions.txt"})
    assert [f.kind for f in falls] == ["class-pass"]
    assert "became a could-not-look" not in falls[0].detail
    assert "the surface" in falls[0].detail


def test_the_no_split_message_says_which_line_lacks_the_split() -> None:
    old = "TRUTH 2026-09-03T19:09Z run=1 hub=aaaaaaa units=[] pass=58 fail=7 skip=18 excluded=2 total=85"
    falls = fc.compare(old, line("2", observed=1, self_=1, simulated=1, meta=1,
                                total=85, ceiling=80), changed=set())
    assert [f.kind for f in falls] == ["pass"]
    assert "the older line" in falls[0].detail and "neither" not in falls[0].detail


# ------------------------------------------------------------------ review 2026-09-06, F5

def test_a_reason_may_contain_a_hash_and_is_not_truncated() -> None:
    accepted, problems = fc.parse_falls("run=105 | issue #12 reddened it; ticket 61 owns it\n")
    assert problems == []
    assert accepted["105"] == "issue #12 reddened it; ticket 61 owns it"


def test_a_whole_line_comment_is_still_a_comment() -> None:
    accepted, problems = fc.parse_falls("  # run=105 | not a real entry\nrun=106 | a real one\n")
    assert problems == [] and set(accepted) == {"106"}


def test_a_committed_reason_for_a_transition_that_did_not_fall_is_a_fault() -> None:
    """F5. A stale reason was accepted in silence, so the hatch grew entries nobody could
    check -- the same defect as an exclusion for a script that no longer exists."""
    log = [line("1"), line("2"), line("3")]
    rep = fc.report(log, falls_text="run=2 | nothing fell here", changed=lambda a, b: set())
    assert rep.ok is False
    assert any("did not fall" in p for p in rep.problems)


def test_the_ceiling_excuse_needs_a_material_change_not_just_a_touched_file() -> None:
    """F5. `changed` now carries only files whose MEANING moved between the two commits, so a
    comment-only edit to the manifest no longer excuses a ceiling drop. The seam is the caller's
    lookup; this pins that compare() trusts it and nothing else."""
    assert [f.kind for f in fc.compare(line("1"), line("2", ceiling=54), set())] == ["ceiling"]
    assert fc.compare(line("1"), line("2", ceiling=54), {"talk/verify-manifest.txt"}) == []


def test_material_paths_ignores_a_comment_only_edit() -> None:
    before = {"talk/verify-manifest.txt": "a.sh | meta | -   # one comment\n"}
    after = {"talk/verify-manifest.txt": "a.sh | meta | -   # a different comment\n\n# and a new one\n"}
    assert fc.material_paths(before, after) == set()


def test_material_paths_sees_a_real_edit_and_an_added_or_removed_file() -> None:
    before = {"talk/verify-manifest.txt": "a.sh | meta | -\n"}
    after = {"talk/verify-manifest.txt": "a.sh | meta | never: nothing to look at\n"}
    assert fc.material_paths(before, after) == {"talk/verify-manifest.txt"}
    assert fc.material_paths({}, after) == {"talk/verify-manifest.txt"}
    assert fc.material_paths(before, {}) == {"talk/verify-manifest.txt"}


# ---------------------------------------------------------- ticket 108: which transition is mine
#
# The clock's recording commit moves this module's input and carries `[skip ci]`, so "the newest
# line on disk" is one transition inside the gate and a different one a commit later. `report()`
# grades the transition ENDING AT THE RUN BEING RECORDED instead. These tests pin the four cases
# and the counted residue.

def _flat_then_fall() -> list[str]:
    return [line("1"), line("2"), line("3", observed=9, fail=5)]


def test_no_run_in_flight_grades_the_newest_recorded_transition() -> None:
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set())
    assert not rep.ok and not rep.deferred_to
    assert {f.kind for f in rep.newest} == {"class-pass", "fail"}


def test_the_recording_run_is_the_newest_line_so_the_fall_still_blocks() -> None:
    """truth.yml's own step, which runs after the cage has appended the line. Unchanged."""
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set(), recording_run="3")
    assert not rep.ok and not rep.deferred_to and rep.newest


def test_a_run_whose_line_is_not_recorded_yet_defers_and_does_not_re_grade() -> None:
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set(), recording_run="4")
    assert rep.ok and rep.deferred_to == "4" and rep.newest == []
    # nothing stops looking: the older transition is still compared, printed and counted
    assert {f.kind for f in rep.deferred_falls} == {"class-pass", "fail"}
    assert rep.older_unaccounted == 1


def test_deferring_does_not_excuse_a_broken_escape_hatch() -> None:
    """The append cannot fix a hole in talk/verify-falls.txt, so deferral must not hide one."""
    rep = fc.report(_flat_then_fall(), "run=99 | no such run", lambda a, b: set(),
                    recording_run="4")
    assert not rep.ok and rep.deferred_to == "4"


def test_a_recording_run_that_is_recorded_but_not_newest_is_a_problem() -> None:
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set(), recording_run="2")
    assert not rep.ok and any("moved under this run" in p for p in rep.problems)


def test_a_reason_accepts_the_fall_for_the_run_being_recorded() -> None:
    rep = fc.report(_flat_then_fall(), "run=3 | ticket 108 owns it", lambda a, b: set(),
                    recording_run="3")
    assert rep.ok and rep.accepted_reason


@pytest.mark.parametrize("recording_run", ["", "1"])
def test_one_line_log_has_no_transition(recording_run: str) -> None:
    assert fc.report([line("1")], "", lambda a, b: set(), recording_run=recording_run).ok


# ------------------------------------------------------- ticket 108: the residue, as a number

def test_inversions_counts_the_runs_whose_own_recording_turned_it_red() -> None:
    assert fc.inversions(_flat_then_fall(), "", lambda a, b: set()) == (1, 2)


def test_a_committed_reason_removes_a_run_from_the_inversion_count() -> None:
    assert fc.inversions(_flat_then_fall(), "run=3 | accepted", lambda a, b: set()) == (0, 2)


def test_a_fall_that_stays_red_across_two_recordings_inverted_once() -> None:
    log = _flat_then_fall() + [line("4", observed=8, fail=6)]
    assert fc.inversions(log, "", lambda a, b: set()) == (1, 3)


def test_inversions_on_a_log_with_no_transition() -> None:
    assert fc.inversions([line("1")], "", lambda a, b: set()) == (0, 0)


# ------------------------------------- ticket 108 review F5b: the defer key is validated
#
# Deferring means NOT grading, so a key nobody checks is an escape hatch keyed on an unchecked
# string -- the shape this ticket exists to refuse. Both holes below were measured on the first
# build: `abc` deferred and exited 0, and `0200` deferred where `200` graded.

def test_a_non_numeric_recording_run_is_a_problem_and_never_a_defer() -> None:
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set(), recording_run="abc")
    assert not rep.ok and rep.deferred_to == ""
    assert any("not a run number" in p for p in rep.problems)
    # and it GRADED rather than shrugging: the fall is still reported
    assert {f.kind for f in rep.newest} == {"class-pass", "fail"}


def test_a_run_number_is_compared_by_value_not_by_string() -> None:
    """`0200` is run 200. Comparing strings made a padded key defer on a run the log carries."""
    assert fc._run_key("0200") == "200"
    assert fc._run_key("fixture-2") == "fixture-2"      # a non-numeric recorded run is itself
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set(), recording_run="003")
    assert rep.deferred_to == "" and not rep.ok        # graded run 3's transition, which fell


def test_a_re_run_of_an_older_recorded_run_is_red_and_says_why() -> None:
    """Review F6, recorded not fixed: re-running an older truth run now guarantees this red."""
    rep = fc.report(_flat_then_fall(), "", lambda a, b: set(), recording_run="2")
    assert not rep.ok and any("moved under this run" in p for p in rep.problems)
    assert any("RE-RUN" in p for p in rep.problems)
