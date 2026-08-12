"""`gameplay-lens` (build ticket 46): Wardley plays whose preconditions actually hold, checked
against the current map, plus the scheduled sweep that pulls opportunity candidates forward
without waiting for a signal to push one — the third of the six skills seam 3 (build ticket 42)
exists to evaluate.
"""

from __future__ import annotations

import inspect

import pytest

from twin import fixtures
from twin.gameplay_lens import (
    PLAYS,
    SKILL,
    GameplayLensError,
    labelled_corpus,
    payload_for,
    propose,
    scorer,
    sweep,
)
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.skills import evaluate, threshold_for


@pytest.fixture(scope="session")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    return labelled_corpus(tmp_path_factory.mktemp("gameplay-lens-corpus"))


# -- propose() -------------------------------------------------------------------------------


def test_propose_refuses_a_payload_missing_a_field() -> None:
    with pytest.raises(GameplayLensError, match="declares no"):
        propose({"positions": [], "edges": []})


def test_propose_finds_nothing_on_an_empty_map() -> None:
    result = propose({"positions": [], "edges": [], "org_components": []})
    assert result == {"opportunities": []}


def test_land_grab_fires_on_netflix_streaming_experience(repo: ModelRepo) -> None:
    """streaming-experience is product-stage, deep enough to be nearing commodity, and the org
    already holds the adjacent cloud-compute (alex-rivera, `knows`)."""
    overlay = Overlay.load(repo, "netflix")
    result = propose(payload_for(overlay))
    hits = {(o["play"], o["component"]) for o in result["opportunities"]}
    assert ("land-grab", "streaming-experience") in hits


def test_land_grab_does_not_fire_on_intel_foundry_services(repo: ModelRepo) -> None:
    """foundry-services is custom-built — below the land-grab threshold — and intel's overlay
    declares no person edges at all, so nothing could be held even if it were."""
    overlay = Overlay.load(repo, "intel")
    result = propose(payload_for(overlay))
    assert result["opportunities"] == []


def test_exploit_commoditisation_fires_on_the_pocket_orgs_shared_database(tmp_path) -> None:
    """shared-database is commodity and identity-store still depends on it from custom-built —
    neither of the default fixture's commodity-stage components has a genesis/custom-built
    dependent, so this play needs its own fixture to be exercised at all."""
    pocket_dir = fixtures.build_pocket_org(tmp_path / "pocket")
    overlay = Overlay.load(ModelRepo.open(pocket_dir), "pocket")
    result = propose(payload_for(overlay))
    hits = {(o["play"], o["component"]) for o in result["opportunities"]}
    assert ("exploit-commoditisation", "shared-database") in hits


def test_every_opportunity_states_its_checked_preconditions_and_a_reason(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    result = propose(payload_for(overlay))
    assert result["opportunities"]
    for opportunity in result["opportunities"]:
        assert opportunity["reason"]
        assert opportunity["preconditions"]
        assert opportunity["play"] in PLAYS


def test_a_target_outside_org_components_is_never_proposed(repo: ModelRepo) -> None:
    """content-delivery-network sits at the same qualifying position as streaming-experience and
    is held by nobody's ownership check either way, but it is a world-layer component, not one of
    netflix's own — only a component the org's own overlay declares is an actionable target."""
    overlay = Overlay.load(repo, "netflix")
    payload = payload_for(overlay)
    assert "content-delivery-network" not in payload["org_components"]
    result = propose(payload)
    assert all(o["component"] != "content-delivery-network" for o in result["opportunities"])


# -- grade-5 by construction, and no recommendation -----------------------------------------


def test_propose_has_no_parameter_that_can_set_a_different_grade() -> None:
    params = inspect.signature(propose).parameters
    assert "grade" not in params
    assert "evidence_grade" not in params
    assert list(params) == ["payload"]


def test_every_opportunitys_claim_is_grade_5(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    result = propose(payload_for(overlay))
    assert result["opportunities"]
    for opportunity in result["opportunities"]:
        claim = opportunity["claim"]
        assert claim["evidence_grade"] == 5
        assert SKILL in claim["claimed_by"]
        assert claim["evidence"] == opportunity["reason"]


_BANNED_SUBSTRINGS = ("action", "band", "verdict", "advice", "should", "must_invest", "outsource")


def test_no_field_or_prose_in_an_opportunity_is_action_shaped(repo: ModelRepo) -> None:
    """The same refusal `no_recommended_action_field` asserts elsewhere (constitution): the reader
    draws the play, the artefact never states one as an instruction."""
    overlay = Overlay.load(repo, "netflix")
    result = propose(payload_for(overlay))
    assert result["opportunities"]

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                assert not any(word in key.lower() for word in _BANNED_SUBSTRINGS), key
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            assert "must invest" not in node.lower()
            assert "should " not in node.lower()

    walk(result)


# -- the labelled corpus: preconditions known to hold, and known not to ---------------------


def test_the_labelled_corpus_covers_three_org_maps(corpus: list[dict]) -> None:
    assert len(corpus) == 3
    assert {item["id"] for item in corpus} == {"netflix", "intel", "pocket"}


def test_every_corpus_item_carries_the_fields_evaluate_requires(corpus: list[dict]) -> None:
    for item in corpus:
        assert {"id", "input", "expected"} <= item.keys()
        assert {"positions", "edges", "org_components"} <= item["input"].keys()
        assert "opportunities" in item["expected"]


def test_gameplay_lens_passes_its_own_labelled_corpus(corpus: list[dict]) -> None:
    result = evaluate(SKILL, propose, corpus, scorer=scorer)
    assert result.passed, f"scored {result.score}, threshold {result.threshold}: {result.as_dict()}"
    assert result.threshold == threshold_for(SKILL)


def test_a_degraded_skill_fails_the_threshold(corpus: list[dict]) -> None:
    def always_nothing(payload: dict) -> dict:
        return {"opportunities": []}

    result = evaluate(SKILL, always_nothing, corpus, scorer=scorer)
    assert result.score < result.threshold
    assert not result.passed


# -- the scheduled sweep: opportunity candidates, unconditionally, beside signal volume -----


def test_sweep_runs_without_a_named_scenario_or_component() -> None:
    assert "scenario" not in inspect.signature(sweep).parameters
    assert "component" not in inspect.signature(sweep).parameters


def test_sweep_finds_the_netflix_opportunity_across_the_default_fixture(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = sweep([repo], caps, ["twin", "gameplay-sweep"])
    hits = {(o["org"], o["play"], o["component"]) for o in artefact.body["opportunities"]}
    assert ("netflix", "land-grab", "streaming-experience") in hits
    assert artefact.body["counts"]["repos"] == 1
    assert artefact.body["counts"]["orgs"] == 2
    assert artefact.body["counts"]["opportunities"] >= 1


def test_sweep_reports_opportunity_volume_beside_signal_volume(repo: ModelRepo, caps: Capabilities) -> None:
    """AC: opportunity output volume is reported alongside threat output volume."""
    artefact = sweep([repo], caps, ["twin", "gameplay-sweep"])
    counts = artefact.body["counts"]
    assert {"opportunities", "signals"} <= counts.keys()
    assert counts["signals"] > 0  # the default fixture binds one signal per org
    for entry in artefact.body["by_org"]:
        assert {"repo", "org", "opportunities", "signals"} <= entry.keys()


def test_two_sweeps_over_an_unchanged_repository_emit_the_same_volume(repo: ModelRepo, caps: Capabilities) -> None:
    """No staleness check — the same unconditional discipline `schedule.sweep` carries (build
    ticket 09), read across to this sweep's own opportunity side."""
    first = sweep([repo], caps, ["twin", "gameplay-sweep"])
    second = sweep([repo], caps, ["twin", "gameplay-sweep"])
    assert first.body["counts"] == second.body["counts"]


def test_sweep_spans_an_org_of_repositories(tmp_path, caps: Capabilities) -> None:
    pocket_dir = fixtures.build_pocket_org(tmp_path / "pocket")
    default_dir = fixtures.build(tmp_path / "default")
    repos = [ModelRepo.open(default_dir), ModelRepo.open(pocket_dir)]

    artefact = sweep(repos, caps, ["twin", "gameplay-sweep"])

    assert artefact.body["counts"]["repos"] == 2
    hits = {(o["org"], o["play"], o["component"]) for o in artefact.body["opportunities"]}
    assert ("pocket", "exploit-commoditisation", "shared-database") in hits


def test_repos_are_pinned_by_git_identity_not_by_filesystem_path(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = sweep([repo], caps, ["twin", "gameplay-sweep"])
    assert artefact.pins["repos"] == [repo.pin.as_dict()]
    assert str(repo.model_root) not in str(artefact.pins)


def test_sweep_depth_grade_travels_with_the_artefact(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = sweep([repo], caps, ["twin", "gameplay-sweep"])
    assert "scenario-engine" in artefact.depth["capabilities"]
