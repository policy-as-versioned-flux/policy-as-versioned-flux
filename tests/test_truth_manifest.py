"""talk/truth_manifest.py: the TRUTH line says what it measured (eco-system ticket 83).

The manifest classes every script the gate discovers; the split of passes by class and the
ceiling are computed here, once, and quoted by verify-all.sh and build_deck.py. These tests
pin the seam: parsing, refusal of a bad line, the judge of a declared skip, the arithmetic,
and reading the line back (the fall-checker of ticket 59 reads it through parse_truth).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "truth_manifest", Path(__file__).resolve().parent.parent / "talk" / "truth_manifest.py")
assert _SPEC is not None and _SPEC.loader is not None
tm = importlib.util.module_from_spec(_SPEC)
sys.modules["truth_manifest"] = tm      # dataclasses resolve annotations through sys.modules
_SPEC.loader.exec_module(tm)

GOOD = """# comment
a/verify-a.sh | estate-observation | -
b/verify-b.sh | self-proof | never: kind cluster 'driftwood' (is not listed|does not exist)
c/verify-c.sh | simulation | waits: declares one version   # borderline: the material is planted
d/verify-d.sh | meta | -
"""


def test_a_good_manifest_parses_with_class_kind_and_pattern_keeping_alternation() -> None:
    entries, problems = tm.parse_manifest(GOOD)
    assert problems == []
    assert [e.split_key for e in entries.values()] == ["observed", "self", "simulated", "meta"]
    assert entries["b/verify-b.sh"].skip_kind == "never"
    assert entries["c/verify-c.sh"].skip_kind == "waits"
    assert entries["b/verify-b.sh"].pattern == "kind cluster 'driftwood' (is not listed|does not exist)"
    assert entries["a/verify-a.sh"].pattern is None


@pytest.mark.parametrize("line, why", [
    ("x/verify-x.sh | unit-test | -", "not one of"),
    ("x/verify-x.sh | meta | sometimes: foo", "skip must be"),
    ("x/verify-x.sh | meta", "needs `path | class | skip`"),
    ("x/verify-x.sh | meta | never: (unclosed", "does not compile"),
])
def test_a_bad_line_is_reported_and_dropped_never_guessed(line: str, why: str) -> None:
    entries, problems = tm.parse_manifest(GOOD + line + "\n")
    assert len(problems) == 1 and why in problems[0], problems
    assert "x/verify-x.sh" not in entries


def test_a_path_listed_twice_is_a_problem() -> None:
    _, problems = tm.parse_manifest(GOOD + "a/verify-a.sh | meta | -\n")
    assert problems == ["line 6: a/verify-a.sh is listed twice"]


def test_load_manifest_raises_with_every_problem_at_once(tmp_path: Path) -> None:
    p = tmp_path / "m.txt"
    p.write_text("x | nope | -\ny | meta | when: z\n")
    with pytest.raises(tm.ManifestError) as ei:
        tm.load_manifest(str(p))
    assert len(ei.value.problems) == 2


def test_judge_declared_skip_matches_the_pattern_case_insensitively() -> None:
    entries, _ = tm.parse_manifest(GOOD)
    ok, why = tm.judge(entries, "b/verify-b.sh", "SKIP: offline holds; Kind Cluster 'driftwood' does not exist")
    assert ok and why == "declared never"
    ok, why = tm.judge(entries, "c/verify-c.sh", "SKIP: distribution/versions.yaml declares one version (4.0.0)")
    assert ok and why == "declared waits"


def test_judge_undeclared_skip_names_the_manifest() -> None:
    entries, _ = tm.parse_manifest(GOOD)
    ok, why = tm.judge(entries, "b/verify-b.sh", "SKIP: the API server returned no pods")
    assert not ok and "does not match" in why and "talk/verify-manifest.txt" in why
    ok, why = tm.judge(entries, "a/verify-a.sh", "SKIP: no cluster")
    assert not ok and "declares no skip" in why
    ok, why = tm.judge(entries, "new/verify-new.sh", "SKIP: no cluster")
    assert not ok and "has no line in talk/verify-manifest.txt" in why


def test_coverage_fails_in_both_directions_but_an_excluded_script_needs_no_line() -> None:
    entries, _ = tm.parse_manifest(GOOD)
    problems, row_level, notes = tm.coverage_problems(
        entries, ["a/verify-a.sh", "new/verify-new.sh", "helper/verify.sh"],
        {"helper/verify.sh": "takes arguments"}, exists=lambda p: p != "d/verify-d.sh")
    assert notes == []
    assert len(row_level) == 1 and "new/verify-new.sh is discovered but has no line" in row_level[0]
    assert len(problems) == 1
    assert "d/verify-d.sh is listed" in problems[0] and "no longer exists" in problems[0]


def test_a_unit_line_whose_script_this_checkout_lacks_is_a_note_not_a_problem() -> None:
    """A unit publishes on its own train: the script may be on its build branch and not yet on
    its main. The hub half stays strict, so hub rot is still a fail."""
    entries, _ = tm.parse_manifest(
        ".estate-clone/u/verify-u.sh | meta | -\nverify/h/verify-h.sh | meta | -\n")
    problems, row_level, notes = tm.coverage_problems(entries, [], {}, exists=lambda p: False)
    assert len(problems) == 1 and "verify/h/verify-h.sh" in problems[0] and row_level == []
    assert len(notes) == 1 and "verify-u.sh" in notes[0] and "not in this checkout" in notes[0]


def test_the_split_sums_to_pass_and_the_ceiling_is_total_minus_excluded_minus_never() -> None:
    entries, _ = tm.parse_manifest(GOOD)
    rows = [("a/verify-a.sh", "PASS", "PASS: x"),
            ("b/verify-b.sh", "SKIP", "SKIP: kind cluster 'driftwood' does not exist"),
            ("c/verify-c.sh", "SKIP", "SKIP: declares one version"),
            ("d/verify-d.sh", "FAIL", "FAIL: y"),
            ("helper/verify.sh", "EXCLUDED", "")]
    s = tm.summarise(entries, rows)
    assert s.fragment() == ("pass=1 [observed=1 self=0 simulated=0 meta=0] fail=1 skip=2 "
                            "[never=1 waits=1] excluded=1 total=5 ceiling=3")
    assert sum(s.split.values()) == s.passed
    assert s.ceiling == s.total - s.excluded - 1
    assert s.extra_rows == []


def test_a_pass_with_no_line_and_a_never_that_passes_are_fails_with_a_row_each() -> None:
    entries, _ = tm.parse_manifest(GOOD)
    rows = [("a/verify-a.sh", "PASS", ""), ("b/verify-b.sh", "PASS", ""),
            ("new/verify-new.sh", "PASS", "")]
    s = tm.summarise(entries, rows, extra_fail=2)
    assert (s.passed, s.failed) == (1, 4)
    assert s.split == {"observed": 1, "self": 0, "simulated": 0, "meta": 0}
    assert any("stale" in r for r in s.extra_rows) and any("no line" in r for r in s.extra_rows)
    # b is still a `never` script, so it stays outside the ceiling until the manifest changes
    assert s.ceiling == 3 - 0 - 1


def test_parse_truth_reads_old_and_new_lines_and_keeps_the_unit_text_for_ticket_77() -> None:
    old = ("TRUTH 2026-09-03T19:09Z run=23 hub=b75eecb units=[driftwood=4b28aa3 feeds=69c89b0] "
           "pass=58 fail=7 skip=18 excluded=2 total=85")
    t = tm.parse_truth(old)
    assert (t["run"], t["hub"], t["pass"], t["fail"], t["skip"], t["excluded"], t["total"]) == \
        ("23", "b75eecb", 58, 7, 18, 2, 85)
    assert t["split"] is None and t["skip_split"] is None and t["ceiling"] is None
    new = ("TRUTH 2026-09-05T05:47Z run=24 hub=abc1234 units=[driftwood=4b28aa3@v1.2.0 feeds=69c89b0] "
           "pass=57 [observed=20 self=31 simulated=5 meta=1] fail=7 skip=18 [never=12 waits=6] "
           "excluded=2 total=84 ceiling=70")
    t = tm.parse_truth(new)
    assert t["split"] == {"observed": 20, "self": 31, "simulated": 5, "meta": 1}
    assert t["skip_split"] == {"never": 12, "waits": 6}
    assert t["ceiling"] == 70 and t["units"]["driftwood"] == "4b28aa3@v1.2.0"
    assert not t["live"] and not t["fixture"]
    with pytest.raises(ValueError):
        tm.parse_truth("not a line")


def test_measured_states_the_split_and_ceiling_or_says_the_line_has_none() -> None:
    new = ("TRUTH 2026-09-05T05:47Z run=24 hub=abc1234 units=[] pass=57 [observed=20 self=31 "
           "simulated=5 meta=1] fail=7 skip=18 [never=12 waits=6] excluded=2 total=84 ceiling=70")
    m = tm.measured(new)
    assert m == ("measured: 57 passes are observed 20 + self 31 + simulated 5 + meta 1, against a "
                 "ceiling of 70 of 84 (2 excluded, 12 can never pass on this runner); fail 7, "
                 "skip 18 (never 12, waits 6)")
    old = "TRUTH 2026-09-03T19:09Z run=23 hub=b75eecb units=[] pass=58 fail=7 skip=18 excluded=2 total=85"
    assert tm.measured(old) == ("measured: run 23's line carries no split and no ceiling; "
                                "talk/verify-manifest.txt landed after it (ticket 83), so the bare "
                                "count pass=58 of total=85 is all that run says about itself")


def test_the_selfcheck_passes() -> None:
    tm.selfcheck()
