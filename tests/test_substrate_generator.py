"""`substrate-generator` (build ticket 49): a coherent multi-channel substrate regenerated from
one pinned recipe — the fifth of the six skills seam 3 (build ticket 42) exists to evaluate.
"""

from __future__ import annotations

import pytest

from twin.grades import Capabilities
from twin.substrate import SubstrateRecipe
from twin.substrate_generator import (
    CHANNELS,
    MIN_MUNDANE_FRACTION,
    SKILL,
    SubstrateGeneratorError,
    generate,
    generate_from_recipe_yaml,
    labelled_corpus,
    mundane_fraction,
    scorer,
)
from twin.skills import evaluate, threshold_for

_TEMPLATES = (
    "Lunch order chat in #ops.",
    "A long thread about the staging environment.",
    "Expense report chasing.",
    "Sprint planning grumbling.",
)


def _recipe(**overrides: object) -> SubstrateRecipe:
    base: dict[str, object] = {
        "id": "test-recipe", "seed": 7, "templates": _TEMPLATES, "model_version": "toy-model-v1",
    }
    return SubstrateRecipe(**{**base, **overrides})  # type: ignore[arg-type]


# -- validation --------------------------------------------------------------------------------


def test_a_recipe_with_too_few_templates_is_refused() -> None:
    with pytest.raises(SubstrateGeneratorError, match="fewer than"):
        generate(_recipe(templates=("only one",)))


def test_a_recipe_scheduling_more_plants_than_channels_is_refused() -> None:
    with pytest.raises(SubstrateGeneratorError, match="caps at one plant per channel"):
        generate(_recipe(planted_signals=("a", "b", "c", "d", "one too many")))


# -- coherent multi-modal generation ------------------------------------------------------------


def test_generate_produces_every_channel() -> None:
    batch = generate(_recipe())
    assert set(batch["channels"]) == set(CHANNELS)
    assert all(batch["channels"][c] for c in CHANNELS)


def test_every_line_carries_the_shared_focus_entity() -> None:
    """Coherence: one focus entity threads through every channel of a batch, not four unrelated
    lists of sentences."""
    batch = generate(_recipe())
    focus = batch["focus_entity"]
    assert focus
    for lines in batch["channels"].values():
        assert all(focus in line for line in lines)


# -- seeded and regenerable via ticket 48's mechanics --------------------------------------------


def test_regenerating_the_identical_recipe_reproduces_byte_for_byte() -> None:
    recipe = _recipe()
    assert generate(recipe) == generate(recipe)


def test_a_different_seed_regenerates_different_substrate() -> None:
    a = generate(_recipe(seed=7))
    b = generate(_recipe(seed=8))
    assert a != b


def test_generate_from_recipe_yaml_reuses_the_versioned_recipe_round_trip() -> None:
    recipe = _recipe(planted_signals=("a planted anomaly",))
    assert generate_from_recipe_yaml(recipe.to_yaml()) == generate(recipe)


# -- mundane by default -------------------------------------------------------------------------


def test_output_is_mundane_by_default_with_no_plants_scheduled() -> None:
    batch = generate(_recipe())
    assert batch["plants"] == []
    assert mundane_fraction(batch) == 1.0


def test_output_stays_mostly_mundane_with_plants_scheduled() -> None:
    batch = generate(_recipe(planted_signals=("a", "b", "c", "d")))
    assert len(batch["plants"]) == 4
    assert mundane_fraction(batch) >= MIN_MUNDANE_FRACTION


def test_at_most_one_plant_lands_per_channel() -> None:
    batch = generate(_recipe(planted_signals=("a", "b", "c", "d")))
    channels_planted = [p["channel"] for p in batch["plants"]]
    assert sorted(channels_planted) == sorted(set(channels_planted))
    assert set(channels_planted) == set(CHANNELS)


def test_a_plant_sits_at_its_recorded_index_in_its_channel() -> None:
    batch = generate(_recipe(planted_signals=("a distinctive planted line",)))
    plant = batch["plants"][0]
    line = batch["channels"][plant["channel"]][plant["index"]]
    assert plant["signal"] in line


# -- measurability wins, and the resolution is recorded ------------------------------------------


def test_the_resolution_names_measurability_winning_over_believability() -> None:
    batch = generate(_recipe())
    assert "measurability" in batch["resolution"].lower()
    assert "believ" in batch["resolution"].lower()


# -- the labelled corpus, and the skill through the seam-3 harness -------------------------------


def test_the_labelled_corpus_spans_zero_to_one_plant_per_channel() -> None:
    corpus = labelled_corpus()
    assert len(corpus) == 3
    assert {item["id"] for item in corpus} == {"quiet-week", "sparse-plants", "dense-plants"}
    for item in corpus:
        assert {"id", "input", "expected"} <= item.keys()
        assert isinstance(item["input"], str)  # the recipe's own YAML form, not the object


def test_substrate_generator_passes_its_own_labelled_corpus() -> None:
    corpus = labelled_corpus()
    result = evaluate(SKILL, generate_from_recipe_yaml, corpus, scorer=scorer)
    assert result.passed, f"scored {result.score}, threshold {result.threshold}: {result.as_dict()}"
    assert result.threshold == threshold_for(SKILL)


def test_a_degraded_generator_fails_the_threshold() -> None:
    def silent(text: str) -> dict:
        return {"channels": {}, "plants": [], "resolution": ""}

    corpus = labelled_corpus()
    result = evaluate(SKILL, silent, corpus, scorer=scorer)
    assert result.score < result.threshold
    assert not result.passed


# -- the depth grade: ticket 49 ticks no new criterion ---------------------------------------------


def test_the_synthetic_substrate_capability_grade_ticks_no_new_criterion_here() -> None:
    """Ticket 49 builds real generation mechanics, but decision ticket 12's AC 3 (planting
    protocol) asks for the full bundle — strength, lead time, burial *and* difficulty
    distribution — and this ticket builds burial only; AC 3 stays unticked on the same "one
    clause of a multi-clause criterion" ground several earlier tickets already left criteria on
    (README, until build ticket 87 closes the remaining clauses). The grade is still computed,
    not asserted — the same check `test_substrate.py` already runs, re-run here to pin that this
    ticket did not quietly move it.

    AC 1 (the real/synthetic seam) is build ticket 50's own tick, not this one's — this asserts
    only what ticket 49 itself moved, so `{5}` here would go stale the moment 50 landed; it is
    `test_spine.py::test_the_synthetic_substrate_capability_grade_moves_to_2_of_7` that pins the
    post-50 state, and `test_substrate_eval.py::test_the_synthetic_substrate_capability_reaches_full_at_build_ticket_87`
    that pins the fully-ticked state. This test only pins "AC 5 was ticked here", not a grade
    snapshot later work legitimately moves."""
    caps = Capabilities.load()
    graded = caps.require("synthetic-substrate")
    assert graded.owning_ticket == "12"
    checked = {c.index for c in graded.criteria if c.checked}
    assert {5} <= checked
