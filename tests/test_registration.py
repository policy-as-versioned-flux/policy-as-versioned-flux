"""What a `needs` edge may move, and when a resolution question registers (ecosystem ticket 51).

Three seams, all pure code, none needing a token or a network:

  * **the actor path.** `nb-refining-capacity -> pq-cryptanalysis` is not a twin `needs` edge
    because neither id is a component of any twin model, and the ruling holds even where the edge
    is PLANTED: a structural relation moves reachability and nothing else, a causal one moves a
    magnitude AND reachability and still no coordinate, a two-hop path is reachable without being
    adjacent, and no relation of any type moves an `evolution_position`, an `evidence_grade`, a
    `weight` or a `probability`. What any of that says about reachability is asserted on the BLAST
    SET `twin/blast.py` returns, never on the admission's own sentence: the module was wrong about
    the traversal twice while only ever reading it (review F1, F2, F4);
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

from twin import blast
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


def test_the_planted_needs_entry_is_what_moves_the_reachability_set(tmp_path: Path):
    """The module's ONE affirmative claim, asserted on the BLAST SET rather than on its own words.

    Review F4: everything this module says about dates it derives from git, and everything it said
    about reachability it derived from READING `twin/blast.py`. The same overlay is built twice --
    with the planted `needs` entries and without them -- and the traversal is run over both.
    """
    with_needs, without = tmp_path / "with", tmp_path / "without"
    fx.build(with_needs)
    fx.build(without, with_needs=False)
    moved = reg.reached_set(reg.read_model(with_needs / "driftwood", "driftwood"), "nb-refining-capacity")
    empty = reg.reached_set(reg.read_model(without / "driftwood", "driftwood"), "nb-refining-capacity")
    assert empty == ()
    assert moved == (("pq-cryptanalysis", 1), ("unwatched-thing", 2))


def test_reachability_is_transitive_and_adjacency_is_not(model: reg.Model):
    """Review F2: `admits()` read only DIRECT relations and reported the absence as an absolute --
    "there is no dependency between them, in either direction" -- for a pair `twin/blast.py`
    reaches at depth 2."""
    admission = reg.admits(model, "unwatched-thing", "nb-refining-capacity")
    assert admission.verdict == reg.REACHABLE_NOT_ADJACENT
    assert admission.admits == ("reachability",)
    assert "at depth 2" in admission.reason
    reg.refuse_move(admission, "reachability")
    for asked in ("magnitude", "price", "evolution_position", "evidence_grade", "weight", "probability"):
        with pytest.raises(reg.RegistrationError):
            reg.refuse_move(admission, asked)


def test_no_relation_is_a_measurement_bounded_by_the_traversal_depth(model: reg.Model):
    """The one pair on no chain at all. The refusal says how far it looked, because the traversal
    stops at `blast.MAX_DEPTH` and a claim that outran its own cap would be the same defect
    wearing a longer number."""
    admission = reg.admits(model, "island-thing", "nb-refining-capacity")
    assert admission.verdict == reg.NO_RELATION
    assert f"max_depth of {blast.MAX_DEPTH}" in admission.refused["reachability"]
    assert reg.reached_set(model, "island-thing") == ()


def test_a_move_nobody_named_is_refused_rather_than_admitted_by_omission(model: reg.Model):
    admission = reg.admits(model, *reg.SUPPLY_CONSTRAINT_PATH)
    with pytest.raises(reg.RegistrationError, match="is not one of the things a relation could move"):
        reg.refuse_move(admission, "the-coordinate-but-spelled-differently")


def test_a_causal_edge_moves_a_magnitude_and_reachability_and_still_no_coordinate(model: reg.Model):
    """Review F1: `admits()` refused `reachability` on a causal edge, and the refusal stated a
    false fact about the estate's own traversal. `blast.radius()` builds `causal_out` and walks it
    FORWARDS exactly as it walks `structural_in` backwards, so a causal edge is a dependency path
    as well as a priced one. Measured on the blast set, planted rather than hand-constructed."""
    before = reg.reached_set(model, "nb-refining-capacity")
    model.edges["planted-influence"] = {
        "id": "planted-influence", "type": "influences",
        "from": "nb-refining-capacity", "to": "island-thing",
        "sign": "increases", "lag_days": 30,
        "elasticity": {"min": 0.1, "mode": 0.2, "max": 0.3}, "evidence_grade": 2,
    }
    after = reg.reached_set(model, "nb-refining-capacity")
    assert sorted(c for c, _ in after) == sorted([c for c, _ in before] + ["island-thing"])
    causal = reg.admits(model, "nb-refining-capacity", "island-thing")
    assert causal.verdict == reg.PRICED_CAUSAL
    assert causal.admits == ("reachability", "magnitude")
    reg.refuse_move(causal, "magnitude")
    reg.refuse_move(causal, "reachability")
    for asked in ("evolution_position", "evidence_grade", "weight", "probability"):
        with pytest.raises(reg.RegistrationError):
            reg.refuse_move(causal, asked)


def test_two_components_with_nothing_between_them_is_not_the_same_answer_as_absent(model: reg.Model):
    """`no-relation-in-this-model` is a modelling gap somebody could close; `not-in-this-model`
    is a pair that is not here at all. Reading the first as the second is how a pair that lives in
    another repository's JSON gets discussed as an edge."""
    assert reg.admits(model, "island-thing", "unwatched-thing").verdict == reg.NO_RELATION
    assert reg.admits(model, "nb-refining-capacity", "not-a-component").verdict == reg.NOT_IN_THIS_MODEL


def test_the_ruling_is_graded_and_its_reachability_claim_checked_against_the_traversal(model: reg.Model):
    """`grade_admission` is what turns a printed verdict into an observation: every always-refused
    move stays refused, and what the admission says about reachability is what the walk found."""
    assert reg.grade_admission(model, *reg.SUPPLY_CONSTRAINT_PATH) == []
    assert reg.grade_admission(model, "island-thing", "nb-refining-capacity") == []
    assert reg.grade_admission(model, "nb-refining-capacity", "not-a-component") == []


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


def test_a_rewrite_says_which_field_moved_and_an_appended_note_says_none_did(planted: Path):
    """Ticket 93's review G2 on a forecast's numbers, applied to the words that make a question.

    The rule is blob identity, so both of these re-register the file. But "rewritten" on its own
    cannot tell an appended note from a changed question, and the override PR this ticket writes
    appends a note to driftwood's niobium entry -- so the distinction is not hypothetical.
    """
    fx.rewrite_question(planted)
    mark = reg.registered_on(planted / "driftwood", fx.SCENARIO_PATH, before=fx.HORIZON,
                             moved_fields=reg.QUESTION_FIELDS)
    assert mark["moved"] == [
        "question: 'Does the planted supplier fail inside the horizon?' -> "
        "'A DIFFERENT question, written after the answer was knowable.'"
    ]
    assert "question:" in mark["sentence"]


def test_an_appended_note_re_registers_the_entry_without_moving_the_question(tmp_path: Path):
    fx.build(tmp_path)
    fx.append_note(tmp_path)
    mark = reg.registered_on(tmp_path / "driftwood", fx.SCENARIO_PATH, before=fx.HORIZON,
                             moved_fields=reg.QUESTION_FIELDS)
    assert mark["rewritten"] is True          # the blob changed, so the file re-registers
    assert mark["registers_on"] == "2026-07-20"
    assert mark["moved"] == []                # and the question itself did not move
    assert "none of proposition, horizon, question moved" in mark["moved_sentence"]


def test_an_override_rewrite_names_the_number_that_moved(planted: Path):
    fx.rewrite_override(planted)
    mark = reg.registered_on(planted / "driftwood", fx.OVERRIDE_PATH, before=fx.HORIZON,
                             moved_fields=reg.OVERRIDE_FIELDS)
    assert mark["moved"] == ["evolution_position: 0.55 -> 0.95"]


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


def test_the_decisions_premise_about_platform_s_intel_is_graded_not_printed(planted: Path, capsys):
    """RED, measured: before review F5 the two intel rows were printed on every run and observed
    on none, so editing platform's file so one row's `links_risk` names the other id -- the exact
    shape ticket 23 recorded and Decision 1 rests on not existing -- left the check at exit 0."""
    fx.plant_platform(planted)
    assert reg.check(str(planted), str(HUB)) == 0
    assert "so neither row points at the other" in capsys.readouterr().out


def test_an_intel_row_naming_the_other_id_turns_the_check_red(tmp_path: Path, capsys):
    fx.build(tmp_path)
    fx.plant_platform(tmp_path, cross_link=True)
    assert reg.check(str(tmp_path), str(HUB)) == 1
    assert "which is the OTHER id in the pair" in capsys.readouterr().out


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
