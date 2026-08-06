"""The typed schema (build ticket 12).

Two properties carry the weight: the schemas are **closed**, so there is no slot for anything
undeclared; and the behavioural overlay is a **separate unit**, so detaching it is an act rather
than a promise.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures
from twin.model import BehaviouralOverlay, ModelError, Overlay
from twin.repo import ModelRepo
from twin.schema import SPECIAL_CATEGORY, SchemaError, SpecialCategoryError, validate


def _commit(root: Path, rel: str, content: str, message: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", message)


COMPONENT = {"id": "a-component", "name": "A component", "kind": "activity"}


# -- closure ----------------------------------------------------------------------------------


def test_an_undeclared_field_is_refused() -> None:
    with pytest.raises(SchemaError, match="schema is closed"):
        validate("component", {**COMPONENT, "morale": 0.4}, "planted")


def test_a_missing_required_field_is_refused() -> None:
    with pytest.raises(SchemaError, match="missing required field"):
        validate("component", {"id": "a-component"}, "planted")


@pytest.mark.parametrize("value", ["A Component", "-leading", "x", "with_underscore"])
def test_an_identifier_that_is_not_one_is_refused(value: str) -> None:
    with pytest.raises(SchemaError, match="not an identifier"):
        validate("component", {**COMPONENT, "id": value}, "planted")


@pytest.mark.parametrize("value", [0.0, 1.0, -0.1, 1.5])
def test_a_belief_of_certainty_is_refused(value: float) -> None:
    """An infinite log-score penalty is not serialisable, so certainty cannot be authored."""
    with pytest.raises(SchemaError, match="strictly between 0 and 1"):
        validate(
            "world-model",
            {"id": "a-model", "name": "A model", "beliefs": {"a-proposition": value}},
            "planted",
        )


# -- Article 9 ---------------------------------------------------------------------------------


@pytest.mark.parametrize("category", SPECIAL_CATEGORY)
def test_every_article_nine_category_has_nowhere_to_go(category: str) -> None:
    with pytest.raises(SpecialCategoryError, match="Article 9"):
        validate("person", {"id": "someone", category: "a value"}, "planted")


@pytest.mark.parametrize("spelling", ["health-status", "Health_Status", "HEALTH"])
def test_respelling_the_category_does_not_help(spelling: str) -> None:
    with pytest.raises(SpecialCategoryError):
        validate("person", {"id": "someone", spelling: "a value"}, "planted")


def test_it_cannot_be_hidden_inside_a_free_form_container() -> None:
    """`provenance` takes any mapping — which would be the obvious place to smuggle one."""
    with pytest.raises(SpecialCategoryError):
        validate(
            "signal",
            {
                "id": "a-signal", "date": "2011-07-12", "steep": "economic", "source": "s",
                "statement": "t", "provenance": {"by": "x", "notes": [{"trade_union": "yes"}]},
            },
            "planted",
        )


def test_a_repository_carrying_article_nine_data_will_not_load(scratch_repo: Path) -> None:
    _commit(scratch_repo, "orgs/netflix/people/alex-rivera.yaml",
            "id: alex-rivera\nrole: Platform engineer\nhealth_status: on long-term leave\n",
            "plant Article 9 data")
    with pytest.raises(SpecialCategoryError, match="Article 9"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


# -- typed edges --------------------------------------------------------------------------------


def test_the_graph_carries_both_authoring_sites_as_one_typed_edge_set(repo: ModelRepo) -> None:
    graph = Overlay.load(repo, "netflix").graph()
    kinds = {e.type for e in graph.edges}
    assert kinds == {"needs", "maintains", "owns", "knows", "influences"}
    assert ("streaming-experience", "cloud-compute") in {(e.source, e.target) for e in graph.edges}
    assert ("alex-rivera", "streaming-experience") in {(e.source, e.target) for e in graph.edges}


def test_the_bus_factor_is_what_people_are_in_the_graph_for(repo: ModelRepo) -> None:
    graph = Overlay.load(repo, "netflix").graph()
    assert graph.bus_factor("streaming-experience") == ["alex-rivera"]
    assert graph.bus_factor("dvd-by-mail") == ["sam-okafor"]
    assert graph.bus_factor("content-delivery-network") == []


def test_a_structural_edge_authored_twice_is_refused(scratch_repo: Path) -> None:
    """One edge, one home: `needs` on the component, not also as a first-class edge."""
    _commit(scratch_repo, "orgs/netflix/edges/duplicate.yaml",
            "id: duplicate\ntype: needs\nfrom: streaming-experience\nto: cloud-compute\n",
            "author a structural edge twice")
    with pytest.raises(ModelError, match="One edge, one home"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_person_edge_must_start_at_a_person(scratch_repo: Path) -> None:
    _commit(scratch_repo, "orgs/netflix/edges/nobody.yaml",
            "id: nobody\ntype: maintains\nfrom: not-a-person\nto: dvd-by-mail\n", "dangle a person edge")
    with pytest.raises(ModelError, match="not a person"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_an_unknown_edge_type_is_refused(scratch_repo: Path) -> None:
    """`causal` arrives with build ticket 17. Until then the vocabulary is closed."""
    _commit(scratch_repo, "orgs/netflix/edges/causal.yaml",
            "id: causal\ntype: causal\nfrom: alex-rivera\nto: dvd-by-mail\n", "invent an edge type")
    with pytest.raises(SchemaError, match="expected one of"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


# -- the gated unit ------------------------------------------------------------------------------


def test_loading_an_overlay_never_reaches_the_behavioural_unit(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    assert not hasattr(overlay, "observations")
    assert "deploy-friction-2011-q2" not in str(overlay.__dict__)


def test_the_behavioural_unit_loads_only_when_asked_for_by_name(repo: ModelRepo) -> None:
    gated = BehaviouralOverlay.load(repo, "netflix")
    assert gated.meta["dpia"] and gated.meta["advisory_only"] is True
    assert set(gated.observations) == {"deploy-friction-2011-q2"}
    assert "person" not in gated.observations["deploy-friction-2011-q2"], "cohort over person"


def test_an_org_without_a_behavioural_unit_is_the_normal_case(repo: ModelRepo) -> None:
    with pytest.raises(ModelError, match="the default and the supported state|no behavioural overlay"):
        BehaviouralOverlay.load(repo, "intel")


def test_a_behavioural_unit_that_is_not_advisory_only_is_refused(scratch_repo: Path) -> None:
    """Article 22: behavioural inference may advise. It may not decide."""
    meta = (scratch_repo / "orgs/netflix/behavioural/meta.yaml").read_text(encoding="utf-8")
    _commit(scratch_repo, "orgs/netflix/behavioural/meta.yaml",
            meta.replace("advisory_only: true", "advisory_only: false"), "make it decisive")
    with pytest.raises(ModelError, match="advisory only"):
        BehaviouralOverlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_detaching_the_behavioural_unit_leaves_everything_else_working(scratch_repo: Path) -> None:
    """The demonstrable act. Not a flag that could be flipped back by whoever set it."""
    fixtures.detach_behavioural(scratch_repo)
    repo = ModelRepo.open(scratch_repo)
    assert Overlay.load(repo, "netflix").graph().bus_factor("dvd-by-mail") == ["sam-okafor"]
    with pytest.raises(ModelError):
        BehaviouralOverlay.load(repo, "netflix")


def test_an_observation_cannot_name_a_person(scratch_repo: Path) -> None:
    _commit(scratch_repo, "orgs/netflix/behavioural/observations/deploy-friction-2011-q2.yaml",
            "id: deploy-friction-2011-q2\ncohort: platform-engineering\nmetric: deploy-lead-time-index\n"
            "value: 0.62\nobserved_on: '2011-06-30'\nperson: alex-rivera\n", "name a person")
    with pytest.raises(SchemaError, match="schema is closed"):
        BehaviouralOverlay.load(ModelRepo.open(scratch_repo), "netflix")
