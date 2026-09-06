"""The map matches the surface (eco-system ticket 67).

The seam is pure: every rule takes text, a recorded log, a set of manifest paths, a callable that
says whether a link resolves, and two dicts of lane declarations and owned paths. No git, no
estate, no filesystem.

Sibling: tests/test_cited_truth.py (ticket 80) grades the same class of claim in
.scratch/ecosystem/issues/*.md. This file grades .scratch/ecosystem/map.md, which ticket 80's
module names as out of its scope, and the two never read the same file.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HUB = Path(__file__).resolve().parents[1]
MODULE = HUB / "verify" / "map-surface" / "map_surface.py"

spec = importlib.util.spec_from_file_location("map_surface", MODULE)
assert spec is not None and spec.loader is not None
ms = importlib.util.module_from_spec(spec)
# registered before exec: the module defines dataclasses, and @dataclass reads
# sys.modules[cls.__module__] while it builds the class
sys.modules[spec.name] = ms
spec.loader.exec_module(ms)


LOG = "\n".join([
    "TRUTH 2026-08-28T04:00Z run=local hub=2326f31 units=[ico=8902b66] "
    "pass=40 fail=16 skip=0 excluded=0 total=56 live=0",
    "TRUTH 2026-08-31T17:22Z run=13 hub=eba3569 units=[ico=9d09222] "
    "pass=53 fail=7 skip=21 excluded=2 total=83",
    "TRUTH 2026-09-01T21:07Z run=20 hub=ad0f6f2 units=[ico=9d09222] "
    "pass=57 fail=7 skip=18 excluded=2 total=84",
]) + "\n"


def kinds(findings):
    return sorted(f.kind for f in findings)


# --- reading a figure off a line ---------------------------------------------------------------

def test_the_slash_shape_is_read_as_pass_fail_skip_of_total():
    (fig,) = ms.figures_quoted("the gate went to 57/7/18 of 84 on the clock\n")
    assert fig.counts == {"pass": 57, "fail": 7, "skip": 18, "total": 84}
    assert fig.lineno == 1


def test_the_prose_shape_is_read_with_and_without_the_skip_clause():
    (a,) = ms.figures_quoted("40 pass, 16 fail of 56\n")
    assert a.counts == {"pass": 40, "fail": 16, "total": 56}
    (b,) = ms.figures_quoted("65 pass, 0 fail, 16 could-not-look of 83\n")
    assert b.counts == {"pass": 65, "fail": 0, "skip": 16, "total": 83}


def test_the_key_shape_needs_two_keys_or_a_run_beside_it():
    (fig,) = ms.figures_quoted("pass=53 fail=7 skip=21\n")
    assert fig.counts == {"pass": 53, "fail": 7, "skip": 21}
    assert ms.figures_quoted("decomposes the local `fail=24` row by row\n") == []
    (lone,) = ms.figures_quoted("run 13 recorded fail=7 and nothing else\n")
    assert lone.counts == {"fail": 7}


def test_a_bare_number_is_not_a_figure():
    assert ms.figures_quoted("55 agents, 38 shortfalls, 10 claims refuted\n") == []
    assert ms.figures_quoted("invariant 45 and invariant 44 are red\n") == []


def test_a_run_citation_is_digits_and_never_the_word_local():
    assert ms.run_cited("the TRUTH line of run 20 says") == "20"
    assert ms.run_cited("`TRUTH 2026-08-31T17:22Z run=13 hub=eba3569 pass=53`") == "13"
    assert ms.run_cited("run=local hub=2326f31") is None
    assert ms.run_cited("the /implement run of 2026-08-28") is None


# --- rule 1: every figure the map quotes is a figure the log recorded --------------------------

def test_a_figure_that_matches_a_recorded_line_passes():
    r = ms.grade_figures("the surface stood at 57/7/18 of 84\n", LOG)
    assert r.findings == []
    assert r.graded == 1


def test_a_figure_no_line_records_is_red():
    r = ms.grade_figures("the surface stood at 65 pass, 0 fail, 16 could-not-look of 83\n", LOG)
    assert kinds(r.findings) == ["no-such-figure"]
    assert "65" in str(r.findings[0])


def test_a_figure_beside_a_run_must_be_that_run_s_figure():
    r = ms.grade_figures("run 20 recorded 53/7/21 of 83\n", LOG)
    assert kinds(r.findings) == ["figure-disagrees"]
    assert "run 20" in str(r.findings[0])


def test_a_figure_beside_a_run_the_log_never_recorded_is_red():
    r = ms.grade_figures("run 92 recorded 65/13/19 of 105\n", LOG)
    assert kinds(r.findings) == ["no-such-line"]


def test_a_line_that_calls_itself_a_rehearsal_is_counted_not_graded():
    r = ms.grade_figures("a local rehearsal reached 65 pass, 0 fail, 16 could-not-look of 83\n",
                         LOG)
    assert r.findings == []
    assert r.declared_uncitable == 1
    assert r.graded == 0


def test_a_dated_correction_naming_the_figure_disposes_of_it():
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was a local rehearsal and no TRUTH\n"
        "> line records it.\n"
    )
    r = ms.grade_figures(text, LOG)
    assert r.findings == []
    assert r.disposed == 1


def test_an_undated_correction_disposes_of_nothing():
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction.** The 65/0/16 figure was a local rehearsal.\n"
    )
    assert kinds(ms.grade_figures(text, LOG).findings) == ["no-such-figure"]


def test_a_correction_does_not_excuse_the_replacement_figure_it_offers():
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was a rehearsal; the citable line is\n"
        "> run 13, 52/7/21 of 83.\n"
    )
    r = ms.grade_figures(text, LOG)
    assert kinds(r.findings) == ["figure-disagrees"]
    assert r.disposed == 1


def test_a_correction_naming_a_different_figure_disposes_of_nothing():
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction, 2026-08-31.** The 40/16/0 figure was a local rehearsal.\n"
    )
    assert kinds(ms.grade_figures(text, LOG).findings) == ["no-such-figure"]


def test_an_empty_log_makes_every_figure_red_rather_than_vacuously_green():
    r = ms.grade_figures("the surface stood at 57/7/18 of 84\n", "")
    assert kinds(r.findings) == ["no-such-figure"]


# --- rule 2: every check the map names is one the gate discovers -------------------------------

MANIFEST = {
    "verify/misuse/verify-misuse.sh",
    "verify/priced-holes/verify-priced-holes.sh",
    "verify/record/verify-record-states-the-purpose.sh",
    ".estate-clone/platform/verify-graded.sh",
}


def test_a_named_check_the_manifest_carries_passes_by_path_basename_or_prefix():
    text = ("`verify/misuse/verify-misuse.sh`, `verify-graded.sh` and `verify/priced-holes` "
            "all grade something.\n")
    assert ms.grade_checks(text, MANIFEST) == []


def test_a_named_check_the_gate_does_not_discover_is_red():
    findings = ms.grade_checks("graded by `verify-nothing-at-all.sh`\n", MANIFEST)
    assert kinds(findings) == ["check-not-in-the-gate"]
    assert "verify-nothing-at-all.sh" in str(findings[0])


def test_the_runner_is_never_graded_as_one_of_the_checks_it_runs():
    assert ms.grade_checks("`talk/verify-all.sh` discovers them\n", MANIFEST) == []
    assert ms.grade_checks("`verify-all.sh --selfcheck` proves the instrument\n", MANIFEST) == []


def test_a_check_the_line_declares_not_in_the_gate_yet_is_counted_not_graded():
    pending: list[int] = []
    line = "the counterpart to `verify/cited-truth/` (built, PR 44, not yet merged)\n"
    assert ms.grade_checks(line, MANIFEST, pending) == []
    assert pending == [1]


def test_a_check_absent_from_the_gate_with_no_such_declaration_is_still_red():
    pending: list[int] = []
    findings = ms.grade_checks("the counterpart to `verify/cited-truth/`\n", MANIFEST, pending)
    assert kinds(findings) == ["check-not-in-the-gate"]
    assert pending == []


def test_a_backticked_token_that_is_not_a_check_path_is_ignored():
    assert ms.grade_checks("`./bin/twin verify` and `cage-tier` and `main`\n", MANIFEST) == []


def test_a_module_or_a_data_file_under_verify_is_not_a_check():
    text = ("`verify/schedules/lane.py` is a module the gate imports and "
            "`verify/deny-is-not-a-rung/register.yaml` is data\n")
    assert ms.grade_checks(text, MANIFEST) == []


# --- rule 3: a reader following the map meets no dead link -------------------------------------

def test_a_link_that_resolves_passes_and_one_that_does_not_is_red():
    text = "see [a](issues/04-x.md) and [b](../gone/NORTH-STAR.md)\n"
    findings = ms.grade_links(text, lambda p: p == "issues/04-x.md")
    assert kinds(findings) == ["dead-link"]
    assert "../gone/NORTH-STAR.md" in str(findings[0])


def test_an_absolute_or_anchor_link_is_not_a_file_claim():
    text = "see [a](https://example.invalid/x) and [b](#destination)\n"
    assert ms.grade_links(text, lambda p: False) == []


# --- rule 4: a unit declares only the lane paths it owns ---------------------------------------

def test_a_lane_trimmed_to_what_the_repo_owns_passes():
    decls = {"ico": {"fetch.yml": ["observations"]}}
    owned = {"ico": {"observations"}}
    assert ms.grade_lanes(decls, owned) == []


def test_a_lane_carrying_a_path_the_repo_does_not_own_is_red():
    decls = {"ico": {"fetch.yml": ["talk/truth.log", "drift/samples.jsonl", "observations"]}}
    owned = {"ico": {"observations"}}
    findings = ms.grade_lanes(decls, owned)
    assert kinds(findings) == ["lane-not-owned", "lane-not-owned"]
    assert "talk/truth.log" in str(findings[0])
    assert "ico/fetch.yml" in str(findings[0])


def test_a_unit_that_declares_no_lane_at_all_is_not_this_rule_s_business():
    assert ms.grade_lanes({"nist": {}}, {"nist": {"observations"}}) == []


# --- rule 5: ticket 67's own record corrections stay corrected ---------------------------------

def test_the_record_facts_are_graded_as_must_carry_and_must_no_longer_carry():
    good = {
        ".scratch/ecosystem/map.md": "[NORTH-STAR.md](../../NORTH-STAR.md) §4 is the build order",
        ".scratch/drift-review-2026-08-27/NORTH-STAR.md":
            "All 22 reversals were confirmed on 2026-08-28.",
    }
    assert ms.grade_record(good) == []

    bad = {
        ".scratch/ecosystem/map.md":
            "[NORTH-STAR.md](../drift-review-2026-08-27/NORTH-STAR.md) §4 is the build order",
        ".scratch/drift-review-2026-08-27/NORTH-STAR.md":
            "The 22 reversals in Appendix C still await the owner's yes or no.",
    }
    assert kinds(ms.grade_record(bad)) == [
        "record-carries", "record-carries", "record-lacks", "record-lacks"]


def test_a_file_the_record_check_cannot_read_is_red_and_not_a_shrug():
    findings = ms.grade_record({})
    assert findings and all(f.kind == "record-unreadable" for f in findings)


# --- the grader can fail -----------------------------------------------------------------------

def test_selfcheck_plants_a_defect_of_every_kind_and_finds_each_one():
    assert ms.selfcheck() == 0


def test_selfcheck_fails_when_a_rule_stops_biting(monkeypatch):
    monkeypatch.setattr(ms, "grade_figures",
                        lambda *a, **k: ms.FigureReport())
    with pytest.raises(AssertionError):
        ms.selfcheck()
