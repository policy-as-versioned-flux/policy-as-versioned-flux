"""What a `needs` edge may move, and when a resolution question registers (ecosystem ticket 51).

Three seams, all pure code, none needing a token or a network:

  * **the actor path.** `nb-refining-capacity -> pq-cryptanalysis` is not a twin `needs` edge
    because neither id is a component of any twin model, and the ruling holds even where the edge
    is PLANTED: a structural relation moves reachability and nothing else, a causal one moves a
    magnitude and still no coordinate, and no relation of any type moves an `evolution_position`,
    an `evidence_grade`, a `weight` or a `probability`;
  * **the resolution question.** A scenario-library entry resolves on its own proposition at its
    own horizon; an entry whose horizon is not strictly after its own authoring date is refused,
    because nothing could ever be pre-registered against it;
  * **the registration date.** Read off git, not off a field: the LAST first-parent write onto
    the served ref (`twin/derived_forecast.py::first_reached`, imported and never re-implemented),
    so a question or an override rewritten after it landed re-registers on the day of the rewrite.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

from twin import registration as reg
from twin import schema

HUB = Path(__file__).resolve().parents[1]
FIXTURE_PATH = HUB / "verify" / "twin-evals" / "registration_fixture.py"


def _fixture_module():
    spec = importlib.util.spec_from_file_location("registration_fixture", FIXTURE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["registration_fixture"] = module
    spec.loader.exec_module(module)
    return module


fx = _fixture_module()


@pytest.fixture()
def planted(tmp_path: Path) -> Path:
    """A throwaway adopter with a bare origin, carrying the PLANTED pair and one question."""
    fx.build(tmp_path)
    return tmp_path


@pytest.fixture()
def model(planted: Path) -> reg.Model:
    return reg.read_model(planted / "driftwood", "driftwood")


# --- the actor path -----------------------------------------------------------------------------


def test_the_ticket_s_pair_is_in_no_twin_model_the_estate_actually_carries():
    """The finding itself, measured against the estate's own overlays rather than asserted."""
    estate = HUB / ".estate-clone"
    if not (estate / "driftwood" / ".git").exists():
        pytest.skip("no .estate-clone/driftwood: the served overlays cannot be read here")
    model = reg.read_model(estate / "driftwood", "driftwood")
    for ident in reg.SUPPLY_CONSTRAINT_PATH:
        assert model.component(ident) is None
    assert reg.admits(model, *reg.SUPPLY_CONSTRAINT_PATH).verdict == reg.NOT_IN_THIS_MODEL


def test_a_planted_needs_edge_moves_reachability_and_nothing_else(model: reg.Model):
    admission = reg.admits(model, *reg.SUPPLY_CONSTRAINT_PATH)
    assert admission.verdict == reg.UNPRICED_STRUCTURAL
    assert admission.admits == ("reachability",)
    reg.refuse_move(admission, "reachability")
    for asked in ("evolution_position", "evidence_grade", "weight", "probability", "magnitude", "price"):
        with pytest.raises(reg.RegistrationError, match=asked):
            reg.refuse_move(admission, asked)


def test_a_move_nobody_named_is_refused_rather_than_admitted_by_omission(model: reg.Model):
    admission = reg.admits(model, *reg.SUPPLY_CONSTRAINT_PATH)
    with pytest.raises(reg.RegistrationError, match="is not one of the things a relation could move"):
        reg.refuse_move(admission, "the-coordinate-but-spelled-differently")


def test_a_causal_edge_moves_a_magnitude_and_still_no_coordinate():
    causal = reg.Admission(source="a", target="b", verdict=reg.PRICED_CAUSAL, reason="fixture",
                           admits=("magnitude",), refused=dict(reg.ALWAYS_REFUSED))
    reg.refuse_move(causal, "magnitude")
    for asked in ("evolution_position", "evidence_grade", "weight", "probability"):
        with pytest.raises(reg.RegistrationError):
            reg.refuse_move(causal, asked)


def test_two_components_with_nothing_between_them_is_not_the_same_answer_as_absent(model: reg.Model):
    """`no-relation-in-this-model` is a modelling gap somebody could close; `not-in-this-model`
    is a pair that is not here at all. Reading the first as the second is how a pair that lives in
    another repository's JSON gets discussed as an edge."""
    assert reg.admits(model, "nb-refining-capacity", "unwatched-thing").verdict == reg.NO_RELATION
    assert reg.admits(model, "nb-refining-capacity", "not-a-component").verdict == reg.NOT_IN_THIS_MODEL


# --- the resolution question ---------------------------------------------------------------------


def test_a_scenario_entry_resolves_on_its_own_proposition_at_its_own_horizon(model: reg.Model):
    question = reg.resolution_question(model, "planted-supply-2026")
    assert question["proposition"] == "a-planted-supplier-fails-within-the-horizon"
    assert question["resolves_on"] == fx.HORIZON
    assert question["register_before"] == "2026-06-29"
    assert "pre-registers nothing by existing" in question["never_scored_on"]


def test_a_horizon_that_is_not_after_its_own_authoring_date_is_refused(planted: Path):
    """RED, measured: `twin/schema.py` validates this entry cleanly, so it merges, and until this
    ticket nothing said that nothing could ever be registered against it."""
    fx.bad_horizon(planted)
    doc = yaml.safe_load((planted / "driftwood" / fx.BAD_HORIZON_PATH).read_text())
    schema.validate("scenario", doc, "planted")          # the RED: still accepted where it lives
    model = reg.read_model(planted / "driftwood", "driftwood")
    with pytest.raises(reg.RegistrationError, match="is not after its own at"):
        reg.resolution_question(model, "planted-same-day-2026")


def test_a_scenario_with_no_horizon_names_no_date_to_register_before(model: reg.Model):
    model.scenarios["planted-supply-2026"].pop("horizon")
    with pytest.raises(reg.RegistrationError, match="declares no horizon"):
        reg.resolution_question(model, "planted-supply-2026")


def test_a_proposition_the_world_layer_does_not_carry_is_refused(model: reg.Model):
    model.scenarios["planted-supply-2026"]["proposition"] = "a-question-nobody-wrote-down"
    with pytest.raises(reg.RegistrationError, match="the world layer .* does not carry"):
        reg.resolution_question(model, "planted-supply-2026")


# --- the override ---------------------------------------------------------------------------------


def test_an_override_is_scoreable_only_through_a_proposition_never_on_its_coordinate(model: reg.Model):
    resolution = reg.override_resolution(model, "planted-supply-position")
    assert resolution["scoreable"] is True
    assert [entry["scenario"] for entry in resolution["through"]] == ["planted-supply-2026"]
    assert "arithmetic on an ordinal scale" in resolution["never_scored_on"]
    assert resolution["unscoreable_because"] is None


def test_an_override_no_question_reaches_is_unscoreable_with_a_reason_not_a_zero(planted: Path):
    fx.orphan_override(planted)
    model = reg.read_model(planted / "driftwood", "driftwood")
    resolution = reg.override_resolution(model, "planted-orphan-position")
    assert resolution["scoreable"] is False
    assert "not a zero" in str(resolution["unscoreable_because"])
    assert "brier" not in yaml.safe_dump(resolution)


def test_an_override_on_a_component_the_model_does_not_carry_is_refused(model: reg.Model):
    model.claims["planted-supply-position"]["component"] = "a-component-nobody-declared"
    with pytest.raises(reg.RegistrationError, match="a-component-nobody-declared"):
        reg.override_resolution(model, "planted-supply-position")


def test_only_an_override_is_read_as_an_override(model: reg.Model):
    model.claims["planted-supply-position"]["kind"] = "position"
    with pytest.raises(reg.RegistrationError, match="not an override"):
        reg.override_resolution(model, "planted-supply-position")


# --- the registration date -------------------------------------------------------------------------


def test_registration_is_the_last_write_onto_the_served_ref(planted: Path):
    mark = reg.registered_on(planted / "driftwood", fx.OVERRIDE_PATH, before=fx.HORIZON)
    assert mark["on_ref"] is True
    assert mark["arrived"] == "2026-02-01"
    assert mark["registers_on"] == "2026-02-01"
    assert mark["rewritten"] is False
    assert mark["in_time"] is True


def test_an_override_rewritten_after_it_landed_re_registers_on_the_day_of_the_rewrite(planted: Path):
    """RED, and the whole of ticket 93's F1 applied to an override: keying on the arrival would
    keep 2026-02-01 and score a number written on 2026-07-20, after the horizon."""
    fx.rewrite_override(planted)
    mark = reg.registered_on(planted / "driftwood", fx.OVERRIDE_PATH, before=fx.HORIZON)
    assert mark["arrived"] == "2026-02-01"
    assert mark["registers_on"] == "2026-07-20"
    assert mark["rewritten"] is True
    assert mark["in_time"] is False
    assert "rewritten after it landed" in mark["sentence"]


def test_a_question_rewritten_after_its_own_horizon_re_registers_too(planted: Path):
    """The leg ticket 93 did not have: the QUESTION is as rewritable as the answer."""
    fx.rewrite_question(planted)
    mark = reg.registered_on(planted / "driftwood", fx.SCENARIO_PATH, before=fx.HORIZON)
    assert mark["registers_on"] == "2026-07-20"
    assert mark["in_time"] is False


def test_a_file_that_has_not_reached_the_ref_registers_nothing(planted: Path):
    mark = reg.registered_on(planted / "driftwood", "twin/orgs/driftwood/claims/never-merged.yaml")
    assert mark["on_ref"] is False
    assert "nothing is registered until it is merged there" in mark["sentence"]


# --- the check --------------------------------------------------------------------------------------


def test_the_check_fails_a_same_day_horizon_and_a_rewritten_override(planted: Path, capsys):
    fx.bad_horizon(planted)
    fx.rewrite_override(planted)
    assert reg.check(str(planted), str(HUB)) == 1
    out = capsys.readouterr().out
    assert "nothing could ever be registered against it" in out
    assert "registered on 2026-07-20, not before 2026-06-30" in out


def test_the_check_passes_a_clean_planted_estate(planted: Path, capsys):
    assert reg.check(str(planted), str(HUB)) == 0
    out = capsys.readouterr().out
    assert "1 override(s), 1 scoreable through a proposition" in out
    assert "0 rewritten since they arrived" in out


def test_the_check_waits_rather_than_passing_when_no_override_has_reached_the_ref(tmp_path: Path, capsys):
    fx.build(tmp_path, with_override=False)
    assert reg.check(str(tmp_path), str(HUB)) == 3
    assert "0 override claim has reached" in capsys.readouterr().out


def test_a_claim_and_a_scenario_sharing_an_id_do_not_share_a_path(model: reg.Model):
    """Ids are unique inside a collection and nothing makes them unique across collections. Keyed
    by id alone, `repo_relative` would have handed git the wrong file -- and a registration date
    read off the wrong file is the class of defect this module exists to close."""
    scenario = reg.repo_relative(model, "scenarios", "planted-supply-2026")
    claim = reg.repo_relative(model, "claims", "planted-supply-position")
    assert scenario == fx.SCENARIO_PATH
    assert claim == fx.OVERRIDE_PATH
    assert reg.repo_relative(model, "claims", "planted-supply-2026") is None
    assert reg.repo_relative(model, "scenarios", "planted-supply-position") is None
