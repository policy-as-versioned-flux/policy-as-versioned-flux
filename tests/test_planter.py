"""`planter` (build ticket 52, decision ticket 12 AC 4, Q2, Q3b): the sealed half of the
planter/detector/scorer split. The only module that ever reads `substrate_generator.generate()`'s
own `plants` field; everything it hands onward (`PlantedWorld.public`) has that field already
stripped.
"""

from __future__ import annotations

import pytest

from twin.planter import Plant, PlanterError, PlantedWorld, plant
from twin.substrate import SubstrateRecipe
from twin.substrate_generator import CHANNELS, generate

_TEMPLATES = (
    "Lunch order chat in #ops.",
    "A long thread about the staging environment.",
    "Expense report chasing.",
    "Sprint planning grumbling.",
)


def _recipe(**overrides: object) -> SubstrateRecipe:
    base: dict[str, object] = {
        "id": "planter-test-recipe", "seed": 11, "templates": _TEMPLATES, "model_version": "toy-model-v1",
    }
    return SubstrateRecipe(**{**base, **overrides})  # type: ignore[arg-type]


# -- every plant must carry a horizon, enforced not merely documented ----------------------------


def test_plant_refuses_a_planted_signal_with_no_declared_horizon() -> None:
    recipe = _recipe(planted_signals=("signal a", "signal b"))
    with pytest.raises(PlanterError, match="signal b"):
        plant(recipe, horizons={"signal a": "2018-06-01"}, strengths={"signal a": 0.5, "signal b": 0.5})


def test_a_recipe_with_no_planted_signals_needs_no_horizons() -> None:
    world = plant(_recipe(), horizons={}, strengths={})
    assert world.ground_truth == ()


# -- every plant must carry a strength, enforced not merely documented ---------------------------


def test_plant_refuses_a_planted_signal_with_no_declared_strength() -> None:
    recipe = _recipe(planted_signals=("signal a", "signal b"))
    with pytest.raises(PlanterError, match="signal b"):
        plant(recipe, horizons={"signal a": "2018-06-01", "signal b": "2018-06-02"}, strengths={"signal a": 0.5})


def test_plant_refuses_a_strength_outside_the_unit_interval() -> None:
    recipe = _recipe(planted_signals=("signal a",))
    with pytest.raises(PlanterError, match=r"\[0, 1\]"):
        plant(recipe, horizons={"signal a": "2018-06-01"}, strengths={"signal a": 1.5})


# -- the sealed split: ground truth never appears in the public view -----------------------------


def test_planted_world_public_carries_no_plants_key() -> None:
    recipe = _recipe(planted_signals=("an unusual after-hours access to the finance share",))
    world = plant(
        recipe,
        horizons={"an unusual after-hours access to the finance share": "2018-06-01"},
        strengths={"an unusual after-hours access to the finance share": 0.7},
    )
    assert "plants" not in world.public
    assert set(world.public["channels"]) == set(CHANNELS)


def test_planted_world_public_matches_generate_output_minus_plants() -> None:
    recipe = _recipe(planted_signals=("a distinctive planted line",))
    horizons = {"a distinctive planted line": "2018-06-01"}
    strengths = {"a distinctive planted line": 0.6}
    world = plant(recipe, horizons, strengths)
    raw = generate(recipe)
    assert world.public["channels"] == raw["channels"]
    assert world.public["focus_entity"] == raw["focus_entity"]
    assert world.public["resolution"] == raw["resolution"]
    assert set(world.public) == set(raw) - {"plants"}


def test_ground_truth_carries_the_declared_horizon_per_plant() -> None:
    recipe = _recipe(planted_signals=("a distinctive planted line",))
    world = plant(
        recipe,
        horizons={"a distinctive planted line": "2018-06-01"},
        strengths={"a distinctive planted line": 0.6},
    )
    assert len(world.ground_truth) == 1
    p = world.ground_truth[0]
    assert isinstance(p, Plant)
    assert p.signal == "a distinctive planted line"
    assert p.actionability_horizon == "2018-06-01"
    assert p.strength == 0.6
    assert world.public["channels"][p.channel][p.index] == generate(recipe)["channels"][p.channel][p.index]


def test_plant_is_deterministic_given_identical_recipe_and_horizons() -> None:
    recipe = _recipe(planted_signals=("a", "b"))
    horizons = {"a": "2018-01-01", "b": "2018-02-01"}
    strengths = {"a": 0.4, "b": 0.9}
    a, b = plant(recipe, horizons, strengths), plant(recipe, horizons, strengths)
    assert a.public == b.public
    assert a.ground_truth == b.ground_truth


def test_planted_world_is_the_only_type_returned() -> None:
    world = plant(_recipe(), horizons={}, strengths={})
    assert isinstance(world, PlantedWorld)
