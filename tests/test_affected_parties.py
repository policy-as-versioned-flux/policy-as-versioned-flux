"""The affected-parties register (build ticket 61)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import constraints, verbs
from twin.affected_parties import KIND, published, register
from twin.cli import main
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

MINIMAL = {
    "id": "s1", "question": "q", "proposition": "p1", "at": "2011-07-12",
    "components": ["c1"], "world_models": ["m1"],
}


@pytest.fixture()
def netflix(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "netflix")


# -- schema: required, and populated as a step of authoring, not optionally ------------------


def test_a_scenario_with_no_affected_parties_field_is_refused() -> None:
    with pytest.raises(SchemaError, match="missing required field"):
        validate("scenario", dict(MINIMAL), "planted")


def test_a_scenario_with_an_empty_affected_parties_list_is_refused() -> None:
    """`list_of` is already non-empty-only, the same rule `components` and `world_models` carry —
    a scenario cannot satisfy "populated" by declaring an empty list."""
    with pytest.raises(SchemaError, match="non-empty list"):
        validate("scenario", {**MINIMAL, "affected_parties": []}, "planted")


def test_an_affected_party_missing_a_required_field_is_refused() -> None:
    with pytest.raises(SchemaError, match="missing required field"):
        validate(
            "scenario",
            {**MINIMAL, "affected_parties": [{"id": "outsiders", "who": "some outsiders"}]},
            "planted",
        )


def test_a_well_formed_scenario_validates() -> None:
    validate(
        "scenario",
        {
            **MINIMAL,
            "affected_parties": [
                {"id": "outsiders", "who": "some outsiders", "consequence": "they bear a cost"},
            ],
        },
        "planted",
    )


def test_an_affected_party_naming_a_special_category_is_refused() -> None:
    """`Schema.validate` already runs `refuse_special_category` over the whole document — an
    affected-party entry gets no exemption from it."""
    from twin.schema import SpecialCategoryError

    with pytest.raises(SpecialCategoryError):
        validate(
            "scenario",
            {
                **MINIMAL,
                "affected_parties": [
                    {"id": "outsiders", "who": "staff on long-term sickness", "consequence": "x"},
                ],
            },
            "planted",
        )


# -- register: a flat, deduplicated roll-up of what scenarios already declared ----------------


def test_register_flattens_every_scenario_in_the_overlay(netflix: Overlay) -> None:
    rows = register(netflix)
    assert rows, "the fixture scenario declares at least one affected party"
    for row in rows:
        assert row["scenario"] == "dvd-decline-2011"
        assert row["who"]
        assert row["consequence"]
    ids = [row["id"] for row in rows]
    assert ids == sorted(ids), "sorted by party id within a scenario, for a deterministic register"


def test_register_is_read_only_never_authors_anything(netflix: Overlay) -> None:
    """Two calls against the same overlay return equal, independently-built lists — a roll-up,
    not a stateful accumulation."""
    assert register(netflix) == register(netflix)


# -- published: alongside the constraint set --------------------------------------------------


def test_published_carries_the_constraint_sets_own_pin(netflix: Overlay) -> None:
    body = published(netflix)
    assert body["constraints_pin"] == constraints.pin()
    assert body["org"] == "netflix"
    assert body["parties"] == register(netflix)


# -- the artefact and the CLI ------------------------------------------------------------------


def test_the_verb_emits_a_derived_artefact_with_no_capability_grade(repo: ModelRepo, caps) -> None:
    artefact = verbs.affected_parties(repo, caps, "netflix", ["twin", "affected-parties"])
    assert artefact.kind == KIND
    assert artefact.mark == "derived"
    assert artefact.depth["grade"] is None
    assert artefact.body["parties"]


def test_cli_emits_the_register(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "affected-parties.json"
    rc = main(["affected-parties", "--repo", str(model_repo_dir), "--org", "netflix", "--out", str(out)])
    assert rc == 0
    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == KIND
    assert doc["envelope"]["mark"] == "derived"
    assert doc["body"]["parties"]
    assert doc["body"]["constraints_pin"] == constraints.pin()


def test_the_scenario_fixture_declares_at_least_two_outsiders(netflix: Overlay) -> None:
    """A concrete demonstration the register is not degenerate on the fixture the golden digests
    and every other seam-1 test already exercise."""
    rows = register(netflix)
    assert len({row["id"] for row in rows}) >= 2
