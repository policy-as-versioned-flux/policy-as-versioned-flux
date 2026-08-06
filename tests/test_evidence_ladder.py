"""The evidence ladder and the regrade record (build ticket 18).

The strength of a claim has to be inseparable from the claim, because the use-gate depends on it.
So: five typed rungs with written admission criteria, a grade required on every graded object, and
a grade that cannot move without a provenanced record of who moved it and why.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from twin import evidence, fixtures, verbs
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.cli import main
from twin.schema import EVIDENCE_GRADES, SchemaError, validate

REGRADE = {
    "id": "an-edge-weakened",
    "subject": "an-edge",
    "from_grade": 1,
    "to_grade": 3,
    "regraded_on": "2026-04-01",
    "by_role": "model-steward",
    "reason": "The series turned out to cover one instance rather than a dated change.",
    "evidence": "Review of the source series.",
}


# -- the ladder ------------------------------------------------------------------------------


def test_the_ladder_has_five_rungs_each_with_written_admission_criteria() -> None:
    rungs = evidence.ladder()["grades"]
    assert [r["grade"] for r in rungs] == list(EVIDENCE_GRADES)
    for rung in rungs:
        assert rung["name"].strip()
        assert rung["admits"].strip()
        assert rung["example"].strip()


def test_the_ladder_is_versioned_and_pinned_by_content() -> None:
    """A threshold that moved later must not silently change what an old gate meant."""
    pin = evidence.pin()
    assert pin["version"] == evidence.ladder()["version"]
    assert pin["pricing_threshold"] == evidence.threshold()
    assert len(pin["digest"]) == 64


def _ladder_with(tmp_path: Path, name: str, *replacements: tuple[str, str]) -> Path:
    text = evidence.LADDER_PATH.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    path = tmp_path / name / "evidence-ladder.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_ladder_missing_a_rung_is_refused(tmp_path: Path) -> None:
    """Five rungs or none: a ladder with a gap gates on nothing while still looking published."""
    trimmed = _ladder_with(
        tmp_path, "trimmed", ("  - grade: 5\n    name: model assertion\n", "  - grade: 9\n    name: model assertion\n")
    )
    with pytest.raises(evidence.EvidenceError, match="a rung with no grade"):
        evidence.ladder(trimmed)


def test_a_rung_with_no_admission_criterion_is_refused(tmp_path: Path) -> None:
    """A rung with nothing written against it admits anything."""
    doc = dict(evidence.ladder())
    doc["grades"] = [{**g, "admits": " "} if g["grade"] == 5 else g for g in doc["grades"]]
    blank = tmp_path / "blank" / "evidence-ladder.yaml"
    blank.parent.mkdir(parents=True, exist_ok=True)
    blank.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(evidence.EvidenceError, match="admission criterion"):
        evidence.ladder(blank)


def test_a_ladder_whose_rungs_disagree_with_its_threshold_is_refused(tmp_path: Path) -> None:
    """`may_price` per rung and the threshold say the same thing, or the gate is ambiguous."""
    contradictory = _ladder_with(tmp_path, "contradictory", ("pricing_threshold: 2", "pricing_threshold: 1"))
    with pytest.raises(evidence.EvidenceError, match="disagrees with pricing_threshold"):
        evidence.ladder(contradictory)


# -- the grade travels with the claim ---------------------------------------------------------


@pytest.mark.parametrize("grade", [0, 6, True, 3.0, "3", None])
def test_a_claim_off_the_ladder_does_not_load(grade: object) -> None:
    """The grade is the ladder's rung, not any whole number."""
    with pytest.raises(SchemaError, match="evidence grade"):
        validate(
            "claim",
            {"id": "a-claim", "kind": "binding", "signal": "a-signal", "component": "a-component",
             "evidence_grade": grade, "claimed_by": "someone", "evidence": "why"},
            "planted",
        )


def test_an_ungraded_claim_does_not_load() -> None:
    with pytest.raises(SchemaError, match="evidence_grade"):
        validate(
            "claim",
            {"id": "a-claim", "kind": "binding", "signal": "a-signal", "component": "a-component",
             "claimed_by": "someone", "evidence": "why"},
            "planted",
        )


def test_every_causal_edge_in_the_graph_names_its_rung(repo: ModelRepo, caps: Capabilities) -> None:
    """A number alone says nothing about what admitted it."""
    artefact = verbs.graph(repo, caps, "netflix", verbs.command_for("graph", org="netflix"))
    causal = [e for e in json.loads(artefact.to_bytes())["body"]["edges"] if "evidence_grade" in e]
    assert causal
    for edge in causal:
        assert edge["evidence_grade_name"] == evidence.rung(edge["evidence_grade"])["name"]
        assert edge["may_price"] is evidence.may_price(edge["evidence_grade"])


# -- the regrade record ------------------------------------------------------------------------


def test_a_regrade_records_who_moved_it_and_why() -> None:
    validate("regrade", REGRADE, "ok")


def test_a_regrade_by_an_unregistered_role_is_refused() -> None:
    """A role nobody holds records nobody."""
    with pytest.raises(SchemaError, match="not in the register"):
        validate("regrade", {**REGRADE, "by_role": "nobody-in-particular"}, "planted")


def test_a_regrade_that_changes_nothing_is_refused() -> None:
    with pytest.raises(SchemaError, match="not a regrade"):
        validate("regrade", {**REGRADE, "to_grade": 1}, "planted")


def test_direction_is_derived_and_never_authored() -> None:
    """`up` is ambiguous on a ladder whose strongest rung is numbered 1, so it is named."""
    assert evidence.record({**REGRADE, "from_grade": 4, "to_grade": 3})["direction"] == "strengthened"
    assert evidence.record({**REGRADE, "from_grade": 1, "to_grade": 2})["direction"] == "weakened"
    with pytest.raises(SchemaError, match="closed"):
        validate("regrade", {**REGRADE, "direction": "strengthened"}, "planted")


def test_the_fixture_carries_a_regrade_in_each_direction(repo: ModelRepo, caps: Capabilities) -> None:
    directions = {}
    for org in ("netflix", "intel"):
        artefact = verbs.graph(repo, caps, org, verbs.command_for("graph", org=org))
        for entry in json.loads(artefact.to_bytes())["body"]["regrades"]:
            directions[entry["subject"]] = entry
    assert directions["streaming-displaces-dvd"]["direction"] == "strengthened"
    assert directions["euv-delay-slips-the-node"]["direction"] == "weakened"
    for entry in directions.values():
        assert entry["by_role"] and entry["reason"] and entry["evidence"]


def test_a_chain_that_does_not_end_at_the_declared_grade_refuses_to_load(scratch_repo: Path) -> None:
    """The half of immutability that runs on every load: the record has to add up."""
    path = scratch_repo / "orgs" / "netflix" / "edges" / "streaming-displaces-dvd.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("evidence_grade: 3", "evidence_grade: 2"),
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "move a grade and leave the record behind")

    with pytest.raises(Exception, match="immutable without a regrade event"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_regrade_naming_no_subject_refuses_to_load(scratch_repo: Path) -> None:
    path = scratch_repo / "orgs" / "netflix" / "regrades" / "orphan.yaml"
    path.write_text(
        "id: orphan\nsubject: an-edge-that-does-not-exist\nfrom_grade: 4\nto_grade: 3\n"
        "regraded_on: '2026-05-01'\nby_role: model-steward\nreason: A reason.\nevidence: Some.\n",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "an orphan regrade")

    with pytest.raises(Exception, match="not an edge or a claim"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_an_unrecorded_grade_change_fails_the_gate(scratch_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The half the chain check cannot see, because after the edit there is no chain at all.

    Only the file's own git history says a grade moved — which is why the check reads it. Asserted
    at seam 1, where the gate actually lives: `twin validate` is what an author or CI runs.
    """
    fixtures.plant_unrecorded_regrade(scratch_repo, grade=1)
    Overlay.load(ModelRepo.open(scratch_repo), "netflix")  # loads: nothing in the tree disagrees

    assert main(["validate", "--repo", str(scratch_repo)]) == 1
    out = capsys.readouterr().out
    assert "moved 2 -> 1" in out and "no regrade event" in out


def test_a_recorded_grade_change_passes_the_gate(scratch_repo: Path) -> None:
    """Not vacuous: the grade really moves in git history, and the record really covers it."""
    fixtures.record_a_regrade(scratch_repo, grade=4)
    repo = ModelRepo.open(scratch_repo)
    overlay = Overlay.load(repo, "netflix")

    assert overlay.edges["cdn-capacity-lifts-streaming"]["evidence_grade"] == 4
    assert repo.commits_touching(f"{overlay.ref.path}/edges/cdn-capacity-lifts-streaming.yaml")
    assert evidence.history_violations(repo, overlay.ref.path, overlay.ref.tree, overlay.regrades) == []
    assert main(["validate", "--repo", str(scratch_repo)]) == 0


def test_a_regrade_that_does_not_match_the_move_still_fails(scratch_repo: Path) -> None:
    """A record that exists but says something else is not a record of this move."""
    fixtures.record_a_regrade(scratch_repo, grade=4)
    path = scratch_repo / "orgs" / "netflix" / "regrades" / "cdn-capacity-weakened.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("from_grade: 2", "from_grade: 3"), encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "a regrade that describes a different move")

    repo = ModelRepo.open(scratch_repo)
    overlay = Overlay.load(repo, "netflix")
    found = evidence.history_violations(repo, overlay.ref.path, overlay.ref.tree, overlay.regrades)
    assert len(found) == 1 and "moved 2 -> 4" in found[0]
