"""Multi-channel enactment sensing, with corroboration setting the grade (build ticket 68).

Decision ticket 18 Q3: declarations and machine evidence are both sensor inputs, and corroboration
between channels sets the evidence grade. The tests that matter are the ones asserting what a
single channel **cannot** do — price on its own, and corroborate itself.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from twin import corroboration, evidence, verbs
from twin.grades import Capabilities
from twin.model import ModelError, Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

CORROBORATED = "pin-the-tooling-image-set"
SELF_DECLARED = "report-node-schedule-variance"
DECLARED_SIGNAL = "tooling-pins-declared-in-place"

BARE = {
    "id": "an-enactment",
    "kind": "enactment",
    "signal": "a-signal",
    "response": "a-response",
    "channel": "self-declaration",
    "evidence_grade": 4,
    "claimed_by": "model-steward",
    "evidence": "They said so.",
}


@pytest.fixture()
def intel(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "intel")


def write_table(tmp_path: Path, doc: dict) -> Path:
    """A scratch channel table. A new file each time — `table()` is cached per path."""
    path = tmp_path / f"channels-{len(list(tmp_path.iterdir()))}.yaml"
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return path


# -- the table ------------------------------------------------------------------------------------


def test_no_channel_prices_alone() -> None:
    """Every channel observes a proxy; the step from proxy to enactment is unevidenced alone."""
    for ident in corroboration.channel_ids():
        assert not evidence.may_price(corroboration.alone_grade(ident))


def test_a_channel_that_prices_alone_is_refused(tmp_path: Path) -> None:
    doc = copy.deepcopy(corroboration.table())
    doc["channels"][1]["alone"] = evidence.threshold()
    with pytest.raises(corroboration.CorroborationError, match="prices alone"):
        corroboration.table(write_table(tmp_path, doc))


def test_a_self_declared_channel_that_prices_alone_is_refused(tmp_path: Path) -> None:
    """The acceptance criterion, refused at load rather than checked at the point of use."""
    doc = copy.deepcopy(corroboration.table())
    declared = next(c for c in doc["channels"] if c["declared_by_subject"])
    declared["alone"] = 1
    with pytest.raises(corroboration.CorroborationError, match="prices alone"):
        corroboration.table(write_table(tmp_path, doc))


def test_the_table_is_closed_so_no_channel_can_be_privileged(tmp_path: Path) -> None:
    """`not privileged` is structural: there is no field by which one channel could outrank another."""
    doc = copy.deepcopy(corroboration.table())
    reconciler = next(c for c in doc["channels"] if c["channel"] == "reconciliation-state")
    reconciler["required_for_price"] = True
    with pytest.raises(corroboration.CorroborationError, match="no room for"):
        corroboration.table(write_table(tmp_path, doc))


def test_reconciliation_state_is_worth_what_every_other_machine_channel_is() -> None:
    machine = {
        c["channel"]: int(c["alone"])
        for c in corroboration.table()["channels"]
        if not c["declared_by_subject"]
    }
    assert len(set(machine.values())) == 1 and "reconciliation-state" in machine


def test_a_table_that_cannot_corroborate_is_refused(tmp_path: Path) -> None:
    doc = copy.deepcopy(corroboration.table())
    doc["channels"] = [c for c in doc["channels"] if c["declared_by_subject"]] + [
        next(c for c in doc["channels"] if not c["declared_by_subject"])
    ]
    with pytest.raises(corroboration.CorroborationError, match="fewer than two channels are independent"):
        corroboration.table(write_table(tmp_path, doc))


def test_a_channel_observing_people_walks_the_ethics_ladder(tmp_path: Path) -> None:
    """Decision ticket 18 Q3's guard: this does not licence sensing people to verify enactment."""
    doc = copy.deepcopy(corroboration.table())
    payroll = next(c for c in doc["channels"] if c["channel"] == "payroll-record")
    payroll["admission"]["necessity"].update({"kind": "behavioural", "level": "individual"})
    with pytest.raises(corroboration.CorroborationError, match="admission ladder refuses it"):
        corroboration.table(write_table(tmp_path, doc))


def test_a_channel_observing_people_with_no_admission_is_refused(tmp_path: Path) -> None:
    doc = copy.deepcopy(corroboration.table())
    payroll = next(c for c in doc["channels"] if c["channel"] == "payroll-record")
    payroll.pop("admission")
    with pytest.raises(corroboration.CorroborationError, match="declares no admission"):
        corroboration.table(write_table(tmp_path, doc))


def test_an_admission_on_a_channel_that_senses_nobody_is_refused(tmp_path: Path) -> None:
    """A gate applied where it was not needed is how it stops being read where it is."""
    doc = copy.deepcopy(corroboration.table())
    payroll = next(c for c in doc["channels"] if c["channel"] == "payroll-record")
    other = next(c for c in doc["channels"] if c["channel"] == "merged-change")
    other["admission"] = copy.deepcopy(payroll["admission"])
    with pytest.raises(corroboration.CorroborationError, match="observes nobody"):
        corroboration.table(write_table(tmp_path, doc))


@pytest.mark.parametrize("step", [0, -1, True])
def test_a_corroboration_step_that_moves_nothing_is_refused(tmp_path: Path, step: object) -> None:
    doc = copy.deepcopy(corroboration.table())
    doc["corroboration"]["step_rungs"] = step
    with pytest.raises(corroboration.CorroborationError, match="step_rungs"):
        corroboration.table(write_table(tmp_path, doc))


def test_the_pin_carries_the_ladder_the_grade_was_read_against() -> None:
    pin = corroboration.pin()
    assert pin["evidence_ladder"] == evidence.pin() and pin["digest"] and pin["version"] >= 1


# -- the computation ------------------------------------------------------------------------------


def test_corroboration_strengthens_a_declaration_into_a_price_eligible_grade(intel: Overlay) -> None:
    """Decision ticket 18 Q3's worked case: a declaration plus a reconciler beats either alone."""
    state = corroboration.state(intel, CORROBORATED)
    alone_grades = [row["alone"] for row in state["channels"]]
    assert state["independent_channels"] == 2
    assert state["evidence_grade"] < min(alone_grades)
    assert state["may_price"] and evidence.may_price(state["evidence_grade"])


def test_an_uncorroborated_self_declaration_cannot_reach_a_price_eligible_grade(intel: Overlay) -> None:
    state = corroboration.state(intel, SELF_DECLARED)
    assert state["independent_channels"] == 1
    assert state["evidence_grade"] == corroboration.alone_grade("self-declaration")
    assert not state["may_price"]


def test_declaring_twice_through_the_same_channel_corroborates_nothing(intel: Overlay) -> None:
    """Two claims, one channel. The incentive is to be verifiable, never to repeat yourself."""
    claims = corroboration.claims_for(intel, SELF_DECLARED)
    assert len(claims) == 2
    assert corroboration.corroborate(claims)["evidence_grade"] == corroboration.corroborate(claims[:1])["evidence_grade"]


def test_a_subject_cannot_corroborate_itself_through_two_of_its_own_channels(tmp_path: Path) -> None:
    """The rule is about independence, not about how many rows the table happens to have."""
    doc = copy.deepcopy(corroboration.table())
    second = copy.deepcopy(next(c for c in doc["channels"] if c["declared_by_subject"]))
    second["channel"] = "self-declaration-elsewhere"
    doc["channels"].append(second)
    path = write_table(tmp_path, doc)
    both = [
        {"id": "one", "channel": "self-declaration"},
        {"id": "two", "channel": "self-declaration-elsewhere"},
    ]
    state = corroboration.corroborate(both, path)
    assert state["independent_channels"] == 1
    assert state["evidence_grade"] == corroboration.alone_grade("self-declaration", path)
    assert not state["may_price"] and "cannot corroborate itself" in state["why"]


def test_the_grade_floors_at_the_strongest_rung() -> None:
    every = [{"id": f"c{i}", "channel": c} for i, c in enumerate(corroboration.channel_ids())]
    assert corroboration.corroborate(every)["evidence_grade"] == corroboration.STRONGEST_GRADE


def test_reconciliation_state_is_one_channel_among_several_and_not_privileged() -> None:
    """Swap the reconciler for any other machine channel and the grade does not move."""
    machine = [c for c in corroboration.channel_ids() if not corroboration.channel(c)["declared_by_subject"]]
    with_reconciler = corroboration.corroborate(
        [{"id": "a", "channel": "self-declaration"}, {"id": "b", "channel": "reconciliation-state"}]
    )
    for other in (c for c in machine if c != "reconciliation-state"):
        swapped = corroboration.corroborate(
            [{"id": "a", "channel": "self-declaration"}, {"id": "b", "channel": other}]
        )
        assert swapped["evidence_grade"] == with_reconciler["evidence_grade"]


def test_an_unobserved_response_is_no_observation_rather_than_a_weak_one(intel: Overlay) -> None:
    state = corroboration.state(intel, "a-response-nobody-has-observed")
    assert state["observed"] is False
    assert state["evidence_grade"] is None and not state["may_price"]


# -- the claim ------------------------------------------------------------------------------------


def test_an_enactment_claim_validates() -> None:
    validate("claim", dict(BARE), "here")


def test_a_claim_may_not_name_its_own_grade() -> None:
    """A self-declaration typed at grade 1 would make the corroboration rule advisory."""
    with pytest.raises(SchemaError, match="holds grade 4 alone"):
        validate("claim", {**BARE, "evidence_grade": 1}, "here")


def test_an_enactment_claim_is_attributable_to_a_registered_role() -> None:
    """The channel is declared, not verified, so labelling is somebody's to answer for.

    Nothing here can check that the merged change or the payroll run exists. What it can do is
    refuse an anonymous label, because "declare, then file your own machine-channel claim" is
    otherwise the cheap route past the rule that a subject cannot corroborate itself.
    """
    with pytest.raises(SchemaError, match="is not in the role register"):
        validate("claim", {**BARE, "claimed_by": "somebody (human)"}, "here")


def test_a_claim_on_an_unknown_channel_is_refused() -> None:
    with pytest.raises(SchemaError, match="not an enactment channel"):
        validate("claim", {**BARE, "channel": "a-friend-of-mine"}, "here")


@pytest.mark.parametrize("field", ["signal", "response", "channel"])
def test_an_enactment_claim_names_its_signal_response_and_channel(field: str) -> None:
    with pytest.raises(SchemaError, match=f"must name the {field}"):
        validate("claim", {k: v for k, v in BARE.items() if k != field}, "here")


@pytest.mark.parametrize("planted", [{"component": "foundry-services"}, {"confidence": 0.9}])
def test_an_enactment_claim_carries_no_component_and_no_confidence(planted: dict) -> None:
    """Corroboration weights an enactment; a per-claim confidence is the knob for arguing with it."""
    with pytest.raises(SchemaError, match="which it does not have"):
        validate("claim", {**BARE, **planted}, "here")


def test_a_binding_claim_may_not_wear_an_enactment_s_fields() -> None:
    binding = {
        "id": "a-binding", "kind": "binding", "signal": "a-signal", "component": "foundry-services",
        "evidence_grade": 5, "claimed_by": "model-steward", "evidence": "Reading of it.",
    }
    validate("claim", binding, "here")
    with pytest.raises(SchemaError, match="only an 'enactment' claim does"):
        validate("claim", {**binding, "response": "a-response"}, "here")


def test_a_claim_that_is_about_nothing_is_refused() -> None:
    with pytest.raises(SchemaError, match="must name the component"):
        validate("claim", {k: v for k, v in BARE.items() if k != "component"} | {"kind": "binding"}, "here")


def test_an_enactment_claim_names_a_response_that_exists(scratch_repo: Path) -> None:
    (scratch_repo / "orgs/intel/claims/enacted-a-phantom.yaml").write_text(
        "id: enacted-a-phantom\nkind: enactment\nsignal: tooling-pins-declared-in-place\n"
        "response: a-response-nobody-declared\nchannel: self-declaration\nevidence_grade: 4\n"
        "claimed_by: model-steward\nevidence: They said so.\n",
        encoding="utf-8",
    )
    fixtures_git(scratch_repo)
    with pytest.raises(ModelError, match="declares no such response"):
        Overlay.load(ModelRepo.open(scratch_repo), "intel")


def fixtures_git(root: Path) -> None:
    from twin import fixtures

    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", "a phantom response")


# -- the sensing path -----------------------------------------------------------------------------


def test_an_enactment_senses_through_the_ordinary_path(repo: ModelRepo, caps: Capabilities) -> None:
    """No enactment verb and no enactment pipeline: `twin sense` binds both kinds of claim."""
    artefact = verbs.sense(
        repo, caps, "intel", DECLARED_SIGNAL, verbs.command_for("sense", org="intel", signal=DECLARED_SIGNAL)
    )
    bound = artefact.body["bindings"]
    assert [b["kind"] for b in bound] == ["enactment"]
    assert bound[0]["response"] == CORROBORATED and bound[0]["channel"] == "self-declaration"
    assert artefact.body["action_state"][0]["evidence_grade"] == 2
    assert artefact.body["channels"]["pin"] == corroboration.pin()


def test_the_enactment_capability_s_depth_travels_only_where_it_produced_something(
    repo: ModelRepo, caps: Capabilities
) -> None:
    enacted = verbs.sense(repo, caps, "intel", DECLARED_SIGNAL, ["twin", "sense"])
    component = verbs.sense(repo, caps, "intel", "foundry-segment-loss-disclosed", ["twin", "sense"])
    assert "enactment" in enacted.depth["capabilities"]
    assert "enactment" not in component.depth["capabilities"]
    assert component.body["action_state"] == [] and component.body["channels"] is None


def test_an_enactment_is_about_no_component_until_a_forecast_is_conditional_on_it(intel: Overlay) -> None:
    """One place decides a claim's forecast subject, and for an enactment it decides `None`.

    An execution reads components, world models and propositions, never responses, so a dated
    enactment cannot change what it answers and the as-consumed refusal must not fire over one.
    Decision ticket 18's AC 5 is what changes this — when a forecast is conditional on whether a
    response was enacted, this must return the response's component, and this test with it.
    """
    enactment = next(iter(corroboration.claims_for(intel, CORROBORATED)))
    binding = intel.claims["bind-foundry-loss-to-foundry-services"]
    assert intel.forecast_subject(enactment) is None
    assert intel.forecast_subject(binding) == "foundry-services"
    assert str(intel.responses[CORROBORATED]["addresses"]) == "foundry-services"


def test_a_sensed_enactment_is_not_an_unbound_signal(intel: Overlay) -> None:
    """A screen for `binding` alone would drop every sensed enactment into the decaying pool."""
    from twin import unbound_pool

    assert DECLARED_SIGNAL not in unbound_pool.unbound_ids(intel)
