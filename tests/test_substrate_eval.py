"""The substrate fidelity eval suite (build ticket 51): fidelity is defined and tuned by
measurement — five declared, targeted dimensions, a real tuning loop that closes a genuine gap,
and negativity bias measured as the same property as reporting asymmetry.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.spine import Spine
from twin.substrate_generator import MIN_MUNDANE_FRACTION, generate
from twin.substrate_eval import (
    PLANTED_SIGNALS,
    TARGETS,
    UNCAMOUFLAGED_PLANTED_SIGNALS,
    UNFAIR_TEST_CONDITIONS,
    FidelityMetric,
    _recipe_for,
    classify_polarity,
    evaluate_fidelity,
    passes,
    plant_difficulty,
    reporting_asymmetry,
    spine_consistency,
    tune,
)


@pytest.fixture(scope="session")
def carillion_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_carillion_org(tmp_path_factory.mktemp("substrate-eval-carillion") / "repo")


@pytest.fixture()
def carillion_overlay(carillion_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(carillion_repo_dir), fixtures.CARILLION_ORG)


@pytest.fixture()
def spine(carillion_overlay: Overlay) -> Spine:
    return Spine.from_overlay(carillion_overlay)


@pytest.fixture()
def latest_checkpoint(spine: Spine) -> str:
    return sorted({f.date for f in spine.facts})[-1]


@pytest.fixture()
def earliest_checkpoint(spine: Spine) -> str:
    return sorted({f.date for f in spine.facts})[0]


# -- each dimension is a computed metric with a declared target and a current value --------------


def test_evaluate_fidelity_returns_five_named_dimensions_with_targets_and_values(
    spine: Spine, latest_checkpoint: str
) -> None:
    batch = generate(_recipe_for(0.6, PLANTED_SIGNALS, seed=42))
    metrics = evaluate_fidelity(batch, spine, latest_checkpoint)
    assert {m.name for m in metrics} == set(TARGETS)
    for m in metrics:
        assert isinstance(m, FidelityMetric)
        assert m.target_low <= m.target_high
        assert isinstance(m.value, float)
        # declared, not asserted: the target came from TARGETS, not typed on the metric by a caller
        assert (m.target_low, m.target_high) == TARGETS[m.name]


def test_within_target_is_computed_from_the_declared_band_not_a_flag() -> None:
    inside = FidelityMetric(name="x", target_low=0.1, target_high=0.5, value=0.3)
    below = FidelityMetric(name="x", target_low=0.1, target_high=0.5, value=0.05)
    above = FidelityMetric(name="x", target_low=0.1, target_high=0.5, value=0.9)
    assert inside.within_target
    assert not below.within_target
    assert not above.within_target


def test_the_tuned_generator_output_passes_every_declared_target(spine: Spine, latest_checkpoint: str) -> None:
    """The suite as the acceptance test for ticket 49's depth grade: a properly tuned recipe's
    real generator output — `substrate_generator.generate()`, unmodified — clears all five bands
    at once, not merely one at a time."""
    result = tune(spine, latest_checkpoint)
    assert result.converged
    assert passes(result.final.metrics)
    for m in result.final.metrics:
        assert m.within_target, f"{m.name}={m.value} outside {(m.target_low, m.target_high)}"


# -- tuning is a supported loop, not a manual eyeball ----------------------------------------------


def test_a_balanced_starting_pool_genuinely_misses_the_reporting_asymmetry_target(
    spine: Spine, latest_checkpoint: str
) -> None:
    """The real gap the tuning loop exists to close: a 50/50 negative/positive template mix is
    not a strawman built to fail — it is the untuned default, and it measurably misses its band."""
    batch = generate(_recipe_for(0.5, PLANTED_SIGNALS, seed=42))
    metrics = {m.name: m for m in evaluate_fidelity(batch, spine, latest_checkpoint)}
    assert not metrics["reporting_asymmetry"].within_target
    assert metrics["reporting_asymmetry"].value < TARGETS["reporting_asymmetry"][0]


def test_tune_converges_over_more_than_one_iteration(spine: Spine, latest_checkpoint: str) -> None:
    """Not a call that happens to pass on the first try: the starting point genuinely fails
    (previous test), so a real loop is what gets from there to a passing state."""
    result = tune(spine, latest_checkpoint, start_negative_fraction=0.5, step=0.05)
    assert result.converged
    assert result.iterations > 1
    assert not result.steps[0].passes  # the first step is the real, failing starting point
    assert result.steps[-1].passes


def test_tune_reports_not_converged_when_the_budget_is_too_small(spine: Spine, latest_checkpoint: str) -> None:
    result = tune(spine, latest_checkpoint, start_negative_fraction=0.5, step=0.05, max_iters=1)
    assert not result.converged
    assert result.iterations == 1


def test_tune_is_deterministic_given_identical_inputs(spine: Spine, latest_checkpoint: str) -> None:
    a = tune(spine, latest_checkpoint)
    b = tune(spine, latest_checkpoint)
    assert a.converged == b.converged
    assert a.iterations == b.iterations
    assert [s.negative_fraction for s in a.steps] == [s.negative_fraction for s in b.steps]
    assert [m.value for s in a.steps for m in s.metrics] == [m.value for s in b.steps for m in s.metrics]


# -- negativity bias: measured, targeted, and produced (not idealised away) -----------------------


def test_a_purely_neutral_batch_measures_zero_reporting_asymmetry() -> None:
    """The generator's own committed mundane templates (ticket 49) carry no polarity vocabulary
    at all — a real, honest failure against any target above zero, not a strawman built to fail."""
    neutral_batch = {"channels": {"events": ["Lunch order chat in #ops.", "A calendar invite gets rescheduled."]}}
    assert reporting_asymmetry(neutral_batch) == 0.0


def test_classify_polarity_finds_both_directions() -> None:
    assert classify_polarity("An incident review opens after the outage.") == "negative"
    assert classify_polarity("The team celebrates a record quarter after the launch.") == "positive"
    assert classify_polarity("Lunch order chat in #ops.") == "neutral"


def test_the_tuned_batchs_asymmetry_skews_negative_matching_the_records_real_bias(
    spine: Spine, latest_checkpoint: str
) -> None:
    """Decision ticket 12 Q3c: the record over-represents failure. The tuned batch's own measured
    value sits above 0.5 — produced, not merely inside an arbitrary band centred on balance."""
    result = tune(spine, latest_checkpoint)
    value = next(m.value for m in result.final.metrics if m.name == "reporting_asymmetry")
    assert value > 0.5


# -- the unfair-test list: a stated list, each condition demonstrated on a real batch --------------


def test_unfair_test_conditions_are_stated_and_named_against_a_real_dimension() -> None:
    assert len(UNFAIR_TEST_CONDITIONS) >= 4
    for _condition, dimension in UNFAIR_TEST_CONDITIONS:
        assert dimension in TARGETS or dimension == "spine.diff_against_spine"


def test_silent_drift_fails_spine_consistency(spine: Spine, latest_checkpoint: str) -> None:
    """An un-anchored batch — nothing ever inserted from the spine — silently drifts from a fact
    it must never contradict by omission (spine.py's own second failure mode)."""
    unanchored = generate(_recipe_for(0.6, PLANTED_SIGNALS, seed=42))
    assert spine_consistency(unanchored, spine, latest_checkpoint) < 1.0


def test_a_trivially_findable_plant_fails_plant_difficulty(spine: Spine, latest_checkpoint: str) -> None:
    """Foreign vocabulary, no burial in its surroundings: the un-camouflaged predecessor wording
    (this module's own negative control) shares almost no vocabulary with the generated pools."""
    batch = generate(_recipe_for(0.6, UNCAMOUFLAGED_PLANTED_SIGNALS, seed=42))
    assert plant_difficulty(batch) < TARGETS["plant_difficulty"][0]


def test_a_falsely_balanced_polarity_split_fails_reporting_asymmetry(
    spine: Spine, latest_checkpoint: str
) -> None:
    batch = generate(_recipe_for(0.5, PLANTED_SIGNALS, seed=42))
    metrics = {m.name: m for m in evaluate_fidelity(batch, spine, latest_checkpoint)}
    assert not metrics["reporting_asymmetry"].within_target


def test_volume_too_thin_fails_mundanity(spine: Spine, earliest_checkpoint: str) -> None:
    """Wrong (too thin) volume: a plant in every channel at the structural minimum
    `lines_per_channel=1`, checked at the earliest checkpoint (fewest spine facts padding the
    total) — a real construction, not an assertion that thinness would plausibly fail."""
    thin = generate(_recipe_for(0.6, PLANTED_SIGNALS, seed=42), lines_per_channel=1)
    metrics = {m.name: m for m in evaluate_fidelity(thin, spine, earliest_checkpoint)}
    assert not metrics["mundanity"].within_target
    assert metrics["mundanity"].value < MIN_MUNDANE_FRACTION


def test_a_degraded_batch_fails_the_full_fidelity_suite(spine: Spine, latest_checkpoint: str) -> None:
    """The suite as an acceptance gate, negative leg: a balanced, un-camouflaged batch fails on
    more than one dimension at once, and `passes()` reports the whole suite as failing."""
    degraded = generate(_recipe_for(0.5, UNCAMOUFLAGED_PLANTED_SIGNALS, seed=42))
    metrics = evaluate_fidelity(degraded, spine, latest_checkpoint)
    assert not passes(metrics)
    failing = {m.name for m in metrics if not m.within_target}
    assert "plant_difficulty" in failing
    assert "reporting_asymmetry" in failing


# -- the depth grade: this ticket ticks AC 2 -------------------------------------------------------


def test_the_synthetic_substrate_capability_grade_moves_to_3_of_7() -> None:
    """Build ticket 51 ticks decision ticket 12's AC 2 (a fidelity target + a stated unfair-test
    list) — the eval suite itself is the realisation, not a claim about it. AC 1 (build ticket 50)
    and AC 5 (build ticket 48) are unchanged; re-run here to pin exactly what this ticket moved.

    A subset check, not an exact match: a later ticket (build ticket 52 ticks AC 4) legitimately
    grows this set further, and this test's own job is only "ticket 51's tick still holds", the
    same forward-compatible shape build ticket 50 left `test_substrate.py` and
    `test_substrate_generator.py` in for the identical reason."""
    caps = Capabilities.load()
    graded = caps.require("synthetic-substrate")
    assert graded.owning_ticket == "12"
    assert graded.grade == "partial"
    checked = {c.index for c in graded.criteria if c.checked}
    assert {1, 2, 5} <= checked
