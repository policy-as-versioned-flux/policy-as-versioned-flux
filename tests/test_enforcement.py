"""Graded enforcement, and posture-as-identity narrowed (build ticket 67).

Two prior-estate hypotheses, tested against the risk basis by decision ticket 18 Q4. Graded
enforcement survives with no special status; posture-as-identity survives only where the evidence
supports it. The tests that matter are the ones asserting what a rung **cannot** do: buy credit,
and declare itself a proof of force.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import enforcement, fixtures, options
from twin.artefact import AUTHORED, load as load_artefact
from twin.cli import main
from twin.grades import Capabilities
from twin.model import ModelError, Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

CONTROL = "pin-the-tooling-image-set"
OBSERVING = "report-node-schedule-variance"
LEVER = "expand-the-delivery-network"

BARE = {
    "id": "a-control",
    "name": "A control",
    "addresses": "foundry-services",
    "cost": {"min": 1, "mode": 2, "max": 3},
}


@pytest.fixture()
def intel(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "intel")


# -- the ladder ---------------------------------------------------------------------------------


@pytest.mark.parametrize("grade", enforcement.grades())
def test_a_control_can_occupy_any_rung(grade: str) -> None:
    validate("response", {**BARE, "enforcement": {"grade": grade, "point": "a decision point"}}, "here")


def test_the_bottom_rung_is_one_of_several_that_change_the_outcome() -> None:
    """`block` is the bottom rung of a ladder, never the mechanism — the whole of "spectrum"."""
    intervening = [g for g in enforcement.grades() if enforcement.changes_the_outcome(g)]
    assert enforcement.grades()[-1] == "block"
    assert len(intervening) >= 2 and "constrain" in intervening


@pytest.mark.parametrize("planted", [{"reduction": 0.4}, {"run_cost": {"gbp": 500}}])
def test_a_rung_that_carries_a_number_is_refused(tmp_path: Path, planted: dict) -> None:
    """A reduction per rung is a free multiplier: tighten the rung, earn more, evidence nothing.

    Nested as well as flat: a `run_cost: {gbp: 500}` is the same multiplier one level down, and a
    flat key scan would admit it.
    """
    import yaml

    doc = dict(enforcement.ladder())
    doc["grades"] = [{**dict(rung), **planted} for rung in doc["grades"]]
    path = tmp_path / f"priced-{sorted(planted)[0]}.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")

    with pytest.raises(enforcement.EnforcementError, match="reduction nobody evidenced"):
        enforcement.ladder(path)


def test_a_ladder_whose_every_rung_changes_the_outcome_is_a_cliff_edge(tmp_path: Path) -> None:
    import yaml

    doc = dict(enforcement.ladder())
    doc["grades"] = [{**dict(rung), "changes_the_outcome": True} for rung in doc["grades"]]
    path = tmp_path / "cliff.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")

    with pytest.raises(enforcement.EnforcementError, match="cliff edge"):
        enforcement.ladder(path)


# -- the rung never prices ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "planted",
    [
        {"reduction": {"min": 0.0, "mode": 0.5, "max": 1.0}},
        {"cost": 5},
        {"posture_as_identity": True},
    ],
)
def test_the_enforcement_block_admits_no_number_and_no_declared_posture(planted: dict) -> None:
    with pytest.raises(SchemaError, match="unknown field"):
        validate(
            "response",
            {**BARE, "enforcement": {"grade": "block", "point": "a decision point", **planted}},
            "planted",
        )


def test_the_same_control_is_one_option_at_every_rung(intel: Overlay) -> None:
    """`Option` is the only thing the pre-filter accepts, so it is the only thing that can price.

    If the rung reached it, graded enforcement would be a multiplier the £ engine never agreed to.
    """
    control = dict(intel.responses[CONTROL])
    at_each = [
        options.Option.of(dict(control, enforcement={**control["enforcement"], "grade": grade}))
        for grade in enforcement.grades()
    ]
    assert all(option == at_each[0] for option in at_each)


def test_an_unknown_rung_is_refused() -> None:
    with pytest.raises(SchemaError, match="not a rung"):
        validate("response", {**BARE, "enforcement": {"grade": "whatever", "point": "here"}}, "planted")


# -- posture-as-identity, computed rather than declared ------------------------------------------


def test_a_stamped_control_at_an_outcome_changing_rung_qualifies(intel: Overlay) -> None:
    verdict = enforcement.posture_as_identity(intel.responses[CONTROL])
    assert verdict["admitted"]
    assert "in force at issue" in verdict["because"]
    # Admitted and still bounded: the identity attests the posture at issue, never since.
    assert verdict["still_not"] == enforcement.POSTURE_EXCLUSIONS[4]["case"]


def test_a_lever_that_is_not_code_is_excluded(repo: ModelRepo) -> None:
    netflix = Overlay.load(repo, "netflix")
    verdict = enforcement.posture_as_identity(netflix.responses[LEVER])
    assert not verdict["admitted"]
    assert verdict["excluded_as"] == enforcement.POSTURE_EXCLUSIONS[0]["case"]


def test_an_observing_control_is_excluded(intel: Overlay) -> None:
    verdict = enforcement.posture_as_identity(intel.responses[OBSERVING])
    assert not verdict["admitted"]
    assert verdict["excluded_as"] == enforcement.POSTURE_EXCLUSIONS[1]["case"]


def test_a_posture_the_subject_can_write_is_excluded(intel: Overlay) -> None:
    control = dict(intel.responses[CONTROL])
    unstamped = {k: v for k, v in control["enforcement"].items() if k != "stamped_by"}
    verdict = enforcement.posture_as_identity(dict(control, enforcement=unstamped))
    assert not verdict["admitted"]
    assert verdict["excluded_as"] == enforcement.POSTURE_EXCLUSIONS[2]["case"]


def test_a_trusted_stamper_at_a_rung_that_changes_nothing_is_refused() -> None:
    """Refused rather than computed to false: the field would sit in the model looking like the
    claim while meaning nothing, and the claim reading bigger than it is was the original defect."""
    with pytest.raises(SchemaError, match="does not change the outcome"):
        validate(
            "response",
            {**BARE, "enforcement": {"grade": "observe", "point": "here", "stamped_by": "the controller"}},
            "planted",
        )


# -- moving a control between rungs --------------------------------------------------------------


def test_direction_is_derived_from_the_rank_not_from_the_name() -> None:
    assert enforcement.direction("warn", "constrain") == enforcement.TIGHTENED
    assert enforcement.direction("block", "observe") == enforcement.LOOSENED
    with pytest.raises(enforcement.EnforcementError, match="changes nothing"):
        enforcement.direction("block", "block")


def test_the_fixture_carries_a_recorded_move_with_its_direction_derived(intel: Overlay) -> None:
    (move,) = intel.enforcement_move_records()
    assert move["subject"] == CONTROL
    assert (move["from_grade"], move["to_grade"]) == ("warn", "constrain")
    assert move["direction"] == enforcement.TIGHTENED
    assert move["by_role"] and move["reason"] and move["evidence"]


def test_a_chain_that_does_not_end_at_the_declared_rung_refuses_to_load(scratch_repo: Path) -> None:
    path = scratch_repo / fixtures.ENFORCED_CONTROL
    path.write_text(path.read_text(encoding="utf-8").replace("grade: constrain", "grade: block"), encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "move a rung and leave the record behind")

    with pytest.raises(ModelError, match="immutable without a move event"):
        Overlay.load(ModelRepo.open(scratch_repo), "intel")


def test_a_move_naming_no_control_refuses_to_load(scratch_repo: Path) -> None:
    _write_move(scratch_repo, "orphan", subject="a-control-that-does-not-exist")
    with pytest.raises(ModelError, match="not a response"):
        Overlay.load(ModelRepo.open(scratch_repo), "intel")


def test_a_move_against_a_lever_that_occupies_no_rung_refuses_to_load(scratch_repo: Path) -> None:
    """A lever that is not code has no consequence to move, and pretending otherwise is how
    policy-as-code becomes the definition of governance again."""
    _write_move(scratch_repo, "against-a-lever", subject=OBSERVING, org="intel")
    path = scratch_repo / "orgs" / "intel" / "responses" / f"{OBSERVING}.yaml"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.split("enforcement:")[0], encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "a move against a lever that is not code")

    with pytest.raises(ModelError, match="occupies no rung"):
        Overlay.load(ModelRepo.open(scratch_repo), "intel")


def test_a_move_by_an_unregistered_role_refuses_to_load(scratch_repo: Path) -> None:
    _write_move(scratch_repo, "by-nobody", subject=CONTROL, by_role="whoever-was-around")
    with pytest.raises(Exception, match="not in the register"):
        Overlay.load(ModelRepo.open(scratch_repo), "intel")


def test_an_unrecorded_move_fails_the_gate(scratch_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The half the chain check cannot see: only the file's own git history says a rung moved."""
    fixtures.plant_unrecorded_enforcement_move(scratch_repo)
    Overlay.load(ModelRepo.open(scratch_repo), "intel")  # loads: nothing in the tree disagrees

    assert main(["validate", "--repo", str(scratch_repo)]) == 1
    out = capsys.readouterr().out
    assert "moved constrain -> block" in out and "no move event" in out


def test_a_recorded_move_passes_the_gate(scratch_repo: Path) -> None:
    """Not vacuous: the rung really moves in git history, and the record really covers it."""
    fixtures.record_an_enforcement_move(scratch_repo)
    repo = ModelRepo.open(scratch_repo)
    overlay = Overlay.load(repo, "intel")

    assert overlay.responses[CONTROL]["enforcement"]["grade"] == "block"
    assert repo.commits_touching(f"{overlay.ref.path}/responses/{CONTROL}.yaml")
    assert enforcement.history_violations(
        repo, overlay.ref.path, overlay.ref.tree, overlay.enforcement_moves
    ) == []
    assert main(["validate", "--repo", str(scratch_repo)]) == 0


def test_deleting_a_control_s_rung_is_a_move_the_history_check_reports(scratch_repo: Path) -> None:
    """Losing a rung removes every consequence a control carried, and a deletion is the shape a
    weakening takes when nothing forces it to be recorded."""
    path = scratch_repo / "orgs" / "intel" / "responses" / f"{OBSERVING}.yaml"
    path.write_text(path.read_text(encoding="utf-8").split("enforcement:")[0], encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "quietly un-enforce a control")

    repo = ModelRepo.open(scratch_repo)
    overlay = Overlay.load(repo, "intel")
    found = enforcement.history_violations(
        repo, overlay.ref.path, overlay.ref.tree, overlay.enforcement_moves
    )
    assert len(found) == 1 and f"observe -> {enforcement.NO_RUNG}" in found[0]


def test_a_control_arriving_at_a_rung_is_not_a_move(scratch_repo: Path) -> None:
    """The other direction, so the check above is a rule rather than a blanket refusal: a control
    that gains consequence has none to have moved from."""
    path = scratch_repo / "orgs" / "netflix" / "responses" / f"{LEVER}.yaml"
    path.write_text(
        path.read_text(encoding="utf-8") + "enforcement:\n  grade: observe\n  point: A review.\n",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "a lever takes on a rung for the first time")

    repo = ModelRepo.open(scratch_repo)
    overlay = Overlay.load(repo, "netflix")
    assert enforcement.history_violations(
        repo, overlay.ref.path, overlay.ref.tree, overlay.enforcement_moves
    ) == []


def test_an_evidence_regrade_does_not_cover_an_enforcement_move(scratch_repo: Path) -> None:
    """The two records are separate, so one may never be offered in place of the other."""
    fixtures.plant_unrecorded_enforcement_move(scratch_repo)
    repo = ModelRepo.open(scratch_repo)
    overlay = Overlay.load(repo, "intel")

    assert enforcement.history_violations(repo, overlay.ref.path, overlay.ref.tree, overlay.regrades)


# -- the published posture -------------------------------------------------------------------------


def test_the_posture_is_authored_so_somebody_is_accountable_for_it(
    model_repo_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TWIN_SIGNING_KEY", "test-key")
    out = tmp_path / "enforcement-posture.json"
    assert main(["enforcement", "--repo", str(model_repo_dir), "--org", "intel", "--out", str(out)]) == 0

    doc = load_artefact(out)
    assert doc["envelope"]["mark"] == AUTHORED
    sidecar = json.loads(Path(str(out) + ".att.json").read_bytes())
    (signature,) = sidecar["human_involvement"]["signatures"]
    assert signature["role"] == enforcement.ROLE


def test_the_posture_publishes_the_ladder_the_moves_and_what_occupies_no_rung(
    model_repo_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "posture.json"
    assert main(["enforcement", "--repo", str(model_repo_dir), "--org", "intel", "--out", str(out)]) == 0
    body = load_artefact(out)["body"]

    assert [g["grade"] for g in body["ladder"]["grades"]] == list(enforcement.grades())
    assert "earns nothing on its own" in body["ladder"]["grade_never_prices"]
    assert {c["control"] for c in body["controls"]} == {CONTROL, OBSERVING}
    assert [m["direction"] for m in body["moves"]] == [enforcement.TIGHTENED]
    assert [case["case"] for case in body["posture_as_identity"]["excluded"]] == [
        case["case"] for case in enforcement.POSTURE_EXCLUSIONS
    ]


def test_a_lever_that_is_not_code_appears_as_occupying_no_rung(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "posture-netflix.json"
    assert main(["enforcement", "--repo", str(model_repo_dir), "--org", "netflix", "--out", str(out)]) == 0
    body = load_artefact(out)["body"]

    assert body["controls"] == []
    assert LEVER in {c["control"] for c in body["not_enforced"]["controls"]}
    assert "most levers are not code" in body["not_enforced"]["why"]


def test_the_capability_now_ticks_decision_ticket_18s_fourth_criterion(caps: Capabilities) -> None:
    grade = caps.require("enactment")
    assert grade.owning_ticket == "18"
    assert [c.index for c in grade.criteria if c.checked] == [1, 3, 4]


def _write_move(root: Path, ident: str, subject: str, by_role: str = "model-steward", org: str = "intel") -> None:
    path = root / "orgs" / org / "enforcement_moves" / f"{ident}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"id: {ident}\nsubject: {subject}\nfrom_grade: observe\nto_grade: warn\n"
        f"moved_on: '2026-05-01'\nby_role: {by_role}\nreason: A reason.\nevidence: Some.\n",
        encoding="utf-8",
    )
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", f"an enforcement move: {ident}")
