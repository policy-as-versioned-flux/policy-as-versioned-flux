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


def test_the_key_shape_is_read_and_a_lone_key_identifies_nothing():
    (fig,) = ms.figures_quoted("pass=53 fail=7 skip=21\n")
    assert fig.counts == {"pass": 53, "fail": 7, "skip": 21}
    (lone,) = ms.figures_quoted("decomposes the local `fail=24` row by row\n")
    assert lone.counts == {"fail": 7 * 0 + 24}
    r = ms.grade_figures("decomposes the local `fail=24` row by row\n", LOG)
    assert r.findings == [] and r.exempted == [] and r.unattributed == 1


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


def test_a_line_that_says_not_citable_is_exempt_and_the_exemption_is_named():
    r = ms.grade_figures("65 pass, 0 fail, 16 could-not-look of 83, from a run not citable here\n",
                         LOG)
    assert r.findings == []
    assert r.declared_uncitable == 1
    assert r.graded == 0
    assert r.exempted == [(ms.MAP, 1, "not citable")]


def test_the_runners_own_uncitable_tokens_are_the_other_two_phrases():
    for token in ("fixture=1", "run=local"):
        r = ms.grade_figures(f"65 pass, 0 fail of 83 on a line carrying {token}\n", LOG)
        assert r.findings == [], token
        assert r.declared_uncitable == 1, token


@pytest.mark.parametrize("laundered", [
    # review F1: each of these was exempt under the seven-substring bag, reported as +1 in a count
    "verify/local-clock: the surface stood at 65 pass, 0 fail, 16 could-not-look of 83\n",
    "the surface stood at 65 pass, 0 fail of 83, and that is NOT a rehearsal\n",
    "as the Actions log confirms, the surface stood at 65 pass, 0 fail of 83\n",
    "no fixture was used: the surface stood at 65 pass, 0 fail of 83\n",
    "the surface stood at 65 pass, 0 fail of 83, hypothetically\n",
])
def test_a_bag_of_words_disclaimer_launders_nothing(laundered):
    r = ms.grade_figures(laundered, LOG)
    assert r.findings and not r.exempted


def test_a_negated_marker_and_a_quoted_one_each_spend_nothing():
    negated = ms.grade_figures("65 pass, 0 fail of 83, and this does not make it not citable\n",
                               LOG)
    assert negated.findings and not negated.exempted
    quoted = ms.grade_figures("grep for `not citable`: 65 pass, 0 fail of 83\n", LOG)
    assert quoted.findings and not quoted.exempted
    linked = ms.grade_figures("see [x](docs/not citable.md): 65 pass, 0 fail of 83\n", LOG)
    assert linked.findings and not linked.exempted


def test_a_wrong_run_figure_is_not_excused_by_a_disclaimer_word():
    # review F1's third case: `planted` anywhere on the line excused a figure that disagreed
    # with the run cited beside it.
    r = ms.grade_figures("run 13 recorded 43/11/0 of 56 and was planted\n", LOG)
    assert kinds(r.findings) == ["figure-disagrees"]


def test_a_dated_correction_directly_below_the_claim_disposes_of_it_and_says_so():
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was unrecorded and no TRUTH\n"
        "> line carries it.\n"
    )
    r = ms.grade_figures(text, LOG)
    assert r.findings == []
    assert r.disposed == 1
    assert r.disposals == [(ms.MAP, 1, "2026-08-31")]


def test_a_correction_disposes_only_for_the_paragraph_directly_above_it():
    # review F2: the correction of a sentence used to launder a fresh copy of that same sentence
    # written into a later section -- the exact sentence this ticket was charted to refuse.
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was unrecorded.\n"
        "\n"
        "## A section written later\n"
        "\n"
        "Nothing is red: 65 pass, 0 fail, 16 could-not-look of 83.\n"
    )
    r = ms.grade_figures(text, LOG)
    assert kinds(r.findings) == ["no-such-figure"]
    assert r.findings[0].lineno == 7
    assert r.disposed == 1


def test_an_undated_correction_disposes_of_nothing():
    text = (
        "The surface went to 65 pass, 0 fail, 16 could-not-look of 83.\n"
        "\n"
        "> **Correction.** The 65/0/16 figure was unrecorded.\n"
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
        "> **Correction, 2026-08-31.** The 40/16/0 figure was unrecorded.\n"
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


@pytest.mark.parametrize("excuse", [
    "", " (built, PR 44, not yet merged)", " (unmerged)", " (not yet in the gate)",
])
def test_a_check_the_gate_does_not_discover_is_red_whatever_the_line_says(excuse):
    # review F4: the hatch's phrases were ordinary prose -- map.md line 29 already contains
    # "unmerged" -- and it never checked the named script existed anywhere at all.
    findings = ms.grade_checks(f"the counterpart to `verify/cited-truth/`{excuse}\n", MANIFEST)
    assert kinds(findings) == ["check-not-in-the-gate"]


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


# --- review F3: the verdict must not turn on the venue -----------------------------------------
#
# The rule reads what `origin/main` SERVES. Read from the working copy it turned on where the
# check happened to run: the reviewer got 0 findings with the units checked out at the ticket
# branch, 33 at origin/main, and made ico's three findings vanish with an uncommitted
# `git checkout <branch> -- fetch.yml`. These run over real throwaway repositories, no estate.

WORKFLOW = """\
name: fetch
on:
  schedule: [{{cron: "0 6 * * *"}}]
env:
  OBSERVATION_LANE: "{lane}"
jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - run: mkdir -p observations && echo x >> observations/feed.jsonl
"""


def _repo(tmp_path, served_lane, checkout_lane=None):
    """A throwaway unit: `origin/main` declares `served_lane`; the working copy declares
    `checkout_lane` when that differs, uncommitted."""
    import subprocess

    origin = tmp_path / "origin"
    work = tmp_path / "unit"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    seed = tmp_path / "seed"
    (seed / ".github" / "workflows").mkdir(parents=True)
    (seed / ".github" / "workflows" / "fetch.yml").write_text(
        WORKFLOW.format(lane=served_lane))
    git = ["git", "-C", str(seed), "-c", "user.name=t", "-c", "user.email=t@t.invalid"]
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-qm", "seed"], check=True)
    subprocess.run(git + ["push", "-q", str(origin), "main"], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], check=True)
    if checkout_lane is not None:
        (work / ".github" / "workflows" / "fetch.yml").write_text(
            WORKFLOW.format(lane=checkout_lane))
    return work


def test_the_served_ref_is_what_is_graded_not_the_working_copy(tmp_path):
    unit = _repo(tmp_path, served_lane="observations",
                 checkout_lane="talk/truth.log drift/samples.jsonl talk/captures observations")
    assert ms.refresh_served_ref(unit) is None
    texts = ms._workflow_texts(unit)
    assert 'OBSERVATION_LANE: "observations"' in texts["fetch.yml"]
    assert "talk/truth.log" not in texts["fetch.yml"]
    assert ms.checkout_behind(unit) == ["fetch.yml"]


def test_a_served_lane_the_repo_does_not_own_is_red_however_clean_the_checkout(tmp_path):
    unit = _repo(tmp_path, served_lane="talk/truth.log observations",
                 checkout_lane="observations")
    lanes = {"u": {"fetch.yml": []}}
    for m in ms.LANE_ENV.finditer(ms._workflow_texts(unit)["fetch.yml"]):
        lanes["u"]["fetch.yml"] = m.group(1).split()
    owned = ms.owned_lane_paths(unit)
    assert owned == {"observations"}, owned
    findings = ms.grade_lanes(lanes, {"u": owned})
    assert kinds(findings) == ["lane-not-owned"]
    assert "talk/truth.log" in str(findings[0])


def test_ownership_is_read_from_the_served_tree_a_ref_and_the_workflow_shell(tmp_path):
    unit = _repo(tmp_path, served_lane="observations")
    # nothing named `observations` is in the tree and no observations branch exists here: it is
    # owned because this repository's own scheduled shell appends to it
    assert ms.owned_lane_paths(unit) == {"observations"}


def test_a_checkout_whose_remote_is_gone_is_red_rather_than_read_locally(tmp_path):
    import shutil

    unit = _repo(tmp_path, served_lane="observations")
    shutil.rmtree(tmp_path / "origin")
    why = ms.refresh_served_ref(unit)
    assert why and "fetch" in why
