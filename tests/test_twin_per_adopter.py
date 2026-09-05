"""verify/twin-per-adopter — the parity claim eco-system ticket 64 makes, at the grader's seam.

REGRILL answer 39 promised a twin each for driftwood, tuppence and ludlow. Ticket 29 resolved
claiming all three and built one. The grader here answers a structural question about the whole
estate rather than about any single adopter: which parties claim the adopter role, which of them
carry a twin overlay, whether the vendored world layer is the same bytes at the same
content-addressed ref in every one of them, and whether each carries the six standing scenarios
and an emitter.

The seam is pure: `adopters`, `survey` and `grade` read a directory and return data. The estate
itself is graded by `verify/twin-per-adopter/verify-twin-per-adopter.sh`, not here — these tests
pin the rules so a change to either side shows up before the gate.

The rule that matters most, and the one these tests exist to hold: an adopter with NO overlay is
a could-not-look that NAMES it, never a pass and never a silent omission. A gate that scored
"every overlay present is fine" over a set of one would have read green through the whole of the
period ticket 64 exists to end.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "twin-per-adopter" / "twin_per_adopter.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("twin_per_adopter", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- who is an adopter -------------------------------------------------------------------------


def _party(estate: Path, org: str, roles: list[str]) -> None:
    unit = estate / org
    unit.mkdir(parents=True, exist_ok=True)
    (unit / "party.yaml").write_text(
        "party: %s\nroles: [%s]\nreporting_currency: GBP\n" % (org, ", ".join(roles))
    )


def test_adopters_are_read_from_the_signed_party_artefact(grader, tmp_path: Path) -> None:
    """Derived, never a list typed into the grader: a fourth adopter joining the estate has to
    reach this check by publishing a party artefact, not by somebody remembering to edit it."""
    _party(tmp_path, "driftwood", ["risk-bearer", "adopter", "publisher"])
    _party(tmp_path, "tuppence", ["risk-bearer", "adopter"])
    _party(tmp_path, "platform", ["publisher"])
    _party(tmp_path, "nist", ["publisher"])
    assert grader.adopters(tmp_path) == ["driftwood", "tuppence"]


def test_a_unit_with_no_party_artefact_is_not_an_adopter(grader, tmp_path: Path) -> None:
    (tmp_path / "scratch").mkdir(parents=True)
    _party(tmp_path, "ludlow", ["adopter"])
    assert grader.adopters(tmp_path) == ["ludlow"]


# -- what one adopter's overlay carries ---------------------------------------------------------


def _overlay(estate: Path, org: str, *, scenarios: int = 6, world: int = 30,
             emitter: bool = True, world_ref: str = "c2d0733") -> None:
    twin = estate / org / "twin"
    (twin / "world" / "components").mkdir(parents=True, exist_ok=True)
    for i in range(world):
        (twin / "world" / "components" / f"c{i}.yaml").write_text("id: c%d\n" % i)
    org_dir = twin / "orgs" / org
    (org_dir / "scenarios").mkdir(parents=True, exist_ok=True)
    for i in range(scenarios):
        (org_dir / "scenarios" / f"s{i}.yaml").write_text("id: s%d\n" % i)
    (org_dir / "meta.yaml").write_text("id: %s\nunit: overlay\norg: %s\nworld_ref: %s\n"
                                       % (org, org, world_ref))
    if emitter:
        (twin / "emit-forward-intel.py").write_text("# emitter\n")


def test_survey_of_an_adopter_with_no_twin_directory(grader, tmp_path: Path) -> None:
    _party(tmp_path, "tuppence", ["adopter"])
    seen = grader.survey(tmp_path, "tuppence")
    assert seen["has_overlay"] is False
    assert seen["scenarios"] == 0
    assert seen["world_ref"] is None


def test_survey_counts_scenarios_world_files_and_the_ref(grader, tmp_path: Path) -> None:
    _party(tmp_path, "driftwood", ["adopter"])
    _overlay(tmp_path, "driftwood")
    seen = grader.survey(tmp_path, "driftwood")
    assert seen["has_overlay"] is True
    assert seen["scenarios"] == 6
    assert seen["world_files"] == 30
    assert seen["world_ref"] == "c2d0733"
    assert seen["has_emitter"] is True


# -- the grade ----------------------------------------------------------------------------------


def test_every_adopter_complete_and_agreeing_is_a_pass(grader, tmp_path: Path) -> None:
    for org in ("driftwood", "tuppence", "ludlow"):
        _party(tmp_path, org, ["adopter"])
        _overlay(tmp_path, org)
    status, lines = grader.grade([grader.survey(tmp_path, o) for o in grader.adopters(tmp_path)])
    assert status == "PASS", lines
    assert any("3 of 3" in msg for _, msg in lines)


def test_an_adopter_with_no_overlay_is_named_and_the_grade_is_could_not_look(grader, tmp_path: Path) -> None:
    """The whole point of ticket 64's gate clause. Two adopters carry an overlay, one does not,
    and the verdict must be could-not-look with the missing one NAMED -- not a pass over the two
    that are there."""
    for org in ("driftwood", "tuppence"):
        _party(tmp_path, org, ["adopter"])
        _overlay(tmp_path, org)
    _party(tmp_path, "ludlow", ["adopter"])
    status, lines = grader.grade([grader.survey(tmp_path, o) for o in grader.adopters(tmp_path)])
    assert status == "SKIP", lines
    assert any(s == "SKIP" and "ludlow" in msg for s, msg in lines)


def test_a_world_ref_that_disagrees_across_adopters_is_observed_false(grader, tmp_path: Path) -> None:
    """The vendored bytes are identical by construction, so the content-addressed ref they stage
    to is identical too. Two adopters pinning different refs means one of them is vendoring
    something else, and that is false rather than unlooked-at."""
    _party(tmp_path, "driftwood", ["adopter"])
    _overlay(tmp_path, "driftwood", world_ref="c2d0733")
    _party(tmp_path, "tuppence", ["adopter"])
    _overlay(tmp_path, "tuppence", world_ref="deadbee")
    status, lines = grader.grade([grader.survey(tmp_path, o) for o in grader.adopters(tmp_path)])
    assert status == "FAIL", lines
    assert any(s == "FAIL" and "world_ref" in msg for s, msg in lines)


def test_an_overlay_short_of_six_scenarios_is_observed_false(grader, tmp_path: Path) -> None:
    _party(tmp_path, "driftwood", ["adopter"])
    _overlay(tmp_path, "driftwood", scenarios=4)
    status, lines = grader.grade([grader.survey(tmp_path, "driftwood")])
    assert status == "FAIL", lines
    assert any(s == "FAIL" and "4" in msg and "six" in msg.lower() for s, msg in lines)


def test_an_overlay_with_no_emitter_is_observed_false(grader, tmp_path: Path) -> None:
    _party(tmp_path, "ludlow", ["adopter"])
    _overlay(tmp_path, "ludlow", emitter=False)
    status, lines = grader.grade([grader.survey(tmp_path, "ludlow")])
    assert status == "FAIL", lines
    assert any(s == "FAIL" and "emitter" in msg for s, msg in lines)


def test_no_adopters_at_all_is_could_not_look_and_never_a_pass(grader, tmp_path: Path) -> None:
    """An empty estate scores nothing. A grade of PASS over an empty set is the exact shape of
    claim the brief forbids: no sentence may claim more than the run observed."""
    status, lines = grader.grade([])
    assert status == "SKIP", lines
    assert any("no party" in msg.lower() or "no adopter" in msg.lower() for _, msg in lines)


# -- the --list mode step 5 consumes ------------------------------------------------------------


def test_list_mode_prints_one_adopter_per_line(grader, tmp_path: Path, capsys) -> None:
    """`verify/e2e/verify-e2e-step5-twin-forecasts.sh` reads its adopter list from here rather
    than hardcoding one, which is the whole of ticket 64's gate clause. One name per line and
    nothing else, so `mapfile` in bash gets an array and not a sentence."""
    _party(tmp_path, "ludlow", ["adopter"])
    _party(tmp_path, "driftwood", ["risk-bearer", "adopter"])
    _party(tmp_path, "nist", ["publisher"])
    assert grader.main(["--list", str(tmp_path)]) == 0
    assert capsys.readouterr().out.split() == ["driftwood", "ludlow"]


def test_list_mode_on_an_estate_with_no_adopter_could_not_look(grader, tmp_path: Path) -> None:
    _party(tmp_path, "nist", ["publisher"])
    assert grader.main(["--list", str(tmp_path)]) == 3
