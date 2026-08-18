"""Netflix: the spine, the substrate, and the report that publishes both (build ticket 73).

Part 1 built the spine and the recipe and measured the five fidelity dimensions by hand from a
library call. This file is part 2's own boundary: the horizons are declared, the
planter/detector/scorer walk runs on the real subject, and `twin substrate` emits a report a
reader gets without opening a Python prompt.

The detection numbers here are deliberately not flattering and are asserted as they fall. The
detector is build ticket 52's lexical-outlier stand-in, the plants are camouflaged on purpose,
and it finds one of the four. Asserting the honest figure is the point — a test tuned until the
stand-in looked good would be measuring the tuning.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, planter, substrate_report
from twin.cli import main
from twin.detector import detect
from twin.model import Overlay
from twin.planter import PlanterError, plant
from twin.repo import ModelRepo
from twin.scorer import MISSED_SCORE, TIMELY_SCORE, score
from twin.spine import Spine, diff_against_spine
from twin.substrate import SubstrateRecipe
from twin.substrate_eval import evaluate_fidelity, passes
from twin.substrate_generator import generate

CHECKPOINT = "2011-10-24"
RECIPE_PATH = Path(__file__).resolve().parent.parent / "twin" / "netflix-substrate-recipe.yaml"


@pytest.fixture(scope="session")
def netflix_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_netflix_org(tmp_path_factory.mktemp("netflix") / "repo")


@pytest.fixture()
def netflix_spine(netflix_repo_dir: Path) -> Spine:
    return Spine.from_overlay(Overlay.load(ModelRepo.open(netflix_repo_dir), "netflix"))


@pytest.fixture()
def recipe() -> SubstrateRecipe:
    return SubstrateRecipe.from_yaml(RECIPE_PATH.read_text(encoding="utf-8"))


# -- the spine: six filings, and the gate that reads them ----------------------------------------


def test_the_spine_is_six_dated_checkpoints(netflix_spine: Spine) -> None:
    assert sorted(f.date for f in netflix_spine.facts) == [
        "2011-01-26", "2011-04-25", "2011-07-25", "2011-09-15", "2011-10-24", "2012-01-25",
    ]
    for fact in netflix_spine.facts:
        assert "sec.gov" in fact.source or "SEC" in fact.source


def test_the_spine_gates_to_what_was_knowable(netflix_spine: Spine) -> None:
    assert len(netflix_spine.at("2011-09-30")) == 4, "the September interim is in; Q3 and Q4 are not"
    assert len(netflix_spine.at(CHECKPOINT)) == 5
    assert len(netflix_spine.at("2012-01-25")) == 6


# -- the substrate: free-running, and inside every band -------------------------------------------


def test_no_substrate_line_restates_a_spine_fact(recipe: SubstrateRecipe, netflix_spine: Spine) -> None:
    """Generating the substrate from the spine is what would make the plants findable by diffing
    against it (decision ticket 12 Q3). The unanchored batch carries nothing of the spine at all.
    """
    split = diff_against_spine(generate(recipe), netflix_spine)
    assert split["anchored"] == []
    assert len(split["free_running"]) == 28


def test_every_fidelity_dimension_lands_inside_its_band(
    recipe: SubstrateRecipe, netflix_spine: Spine
) -> None:
    metrics = {m.name: m for m in evaluate_fidelity(generate(recipe), netflix_spine, CHECKPOINT)}
    assert passes(tuple(metrics.values()))
    assert round(metrics["signal_to_noise"].value, 3) == 0.121
    assert round(metrics["plant_difficulty"].value, 3) == 0.275
    assert round(metrics["plant_difficulty_spread"].value, 3) == 0.6
    assert metrics["spine_consistency"].value == 1.0
    assert round(metrics["reporting_asymmetry"].value, 3) == 0.667
    assert round(metrics["mundanity"].value, 3) == 0.879
    assert metrics["contamination"].value == 0.0


# -- the horizons: declared, or the planter refuses the recipe -------------------------------------


def test_every_planted_signal_carries_a_declared_horizon_and_a_reason(recipe: SubstrateRecipe) -> None:
    dates, reasons, strengths = planter.horizons_for(recipe)
    assert set(dates) == set(recipe.planted_signals)
    assert set(reasons) == set(recipe.planted_signals)
    assert set(strengths) == set(recipe.planted_signals)
    for date in dates.values():
        assert len(date) == 10 and date.startswith("2011-")
    for strength in strengths.values():
        assert 0.0 <= strength <= 1.0


def test_a_horizon_file_declaring_a_signal_the_recipe_never_plants_is_refused(
    recipe: SubstrateRecipe, tmp_path: Path
) -> None:
    drifted = tmp_path / "drifted.yaml"
    drifted.write_text(
        "schema: twin.plant-horizons/v1\nrule: r\nauthored: a\nrecipes:\n"
        f"  {recipe.id}:\n    - signal: a signal this recipe never plants\n"
        "      horizon: '2011-09-30'\n      reason: drift\n",
        encoding="utf-8",
    )
    with pytest.raises(PlanterError, match="never plants"):
        planter.horizons_for(recipe, path=drifted)


def test_a_recipe_with_no_declared_horizons_is_refused() -> None:
    unknown = SubstrateRecipe(
        id="not-a-declared-recipe", seed=1, templates=("a", "b", "c", "d"),
        model_version="toy-model-v1", planted_signals=("x",),
    )
    with pytest.raises(PlanterError, match="not-a-declared-recipe"):
        planter.horizons_for(unknown)


def test_a_horizon_that_is_not_a_day_is_refused_through_the_regime_gate(
    recipe: SubstrateRecipe, tmp_path: Path
) -> None:
    """A horizon is compared against `detected_at` as text, so one in another shape compares wrong
    rather than failing. `regimes.cutoff` is the parser that catches it — the same one `Spine.at`
    uses, not a second one that happens to agree with it today.
    """
    malformed = tmp_path / "malformed.yaml"
    malformed.write_text(
        "schema: twin.plant-horizons/v1\nrecipes:\n"
        f"  {recipe.id}:\n    - signal: {recipe.planted_signals[0]}\n"
        "      horizon: '2011-09-30T00:00:00Z'\n      reason: a moment, not a day\n",
        encoding="utf-8",
    )
    with pytest.raises(PlanterError, match="unusable horizon"):
        planter.horizons_for(recipe, path=malformed)


def test_a_horizon_with_no_reason_is_refused(recipe: SubstrateRecipe, tmp_path: Path) -> None:
    silent = tmp_path / "silent.yaml"
    silent.write_text(
        "schema: twin.plant-horizons/v1\nrecipes:\n"
        f"  {recipe.id}:\n    - signal: {recipe.planted_signals[0]}\n"
        "      horizon: '2011-09-30'\n",
        encoding="utf-8",
    )
    with pytest.raises(PlanterError, match="no reason"):
        planter.horizons_for(recipe, path=silent)


# -- the walk: planter, detector, scorer, on the real subject --------------------------------------


def test_the_walk_finds_one_plant_of_four_and_says_so(recipe: SubstrateRecipe) -> None:
    dates, _reasons, strengths = planter.horizons_for(recipe)
    world = plant(recipe, dates, strengths)
    assert len(world.ground_truth) == 4
    assert "plants" not in world.public

    result = score(world.ground_truth, detect(world.public), detected_at=CHECKPOINT)
    assert result.hit_rate == 0.25
    found = [p for p in result.plant_scores if p.detected]
    assert len(found) == 1
    assert found[0].plant.channel == "hr"
    assert found[0].timely is True and found[0].score == TIMELY_SCORE
    assert all(p.score == MISSED_SCORE for p in result.plant_scores if not p.detected)
    assert result.limitation == planter.SHARED_PRIOR_LIMITATION


# -- the report: the figures exist without a Python prompt ------------------------------------------


def test_twin_substrate_emits_a_report_carrying_both_halves(
    netflix_repo_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "substrate-report.json"
    assert main([
        "substrate", "--repo", str(netflix_repo_dir), "--org", "netflix",
        "--recipe", str(RECIPE_PATH), "--checkpoint", CHECKPOINT, "--out", str(out),
    ]) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == substrate_report.KIND_SUBSTRATE_REPORT
    assert doc["envelope"]["mark"] == "derived"
    assert doc["envelope"]["depth"]["capabilities"]["synthetic-substrate"]
    assert doc["envelope"]["pins"]["recipe"]["sha256"]
    assert doc["envelope"]["pins"]["spine"]["digest"]

    body = doc["body"]
    assert body["fidelity"]["passes"] is True
    assert [m["name"] for m in body["fidelity"]["metrics"]] == [
        "signal_to_noise", "plant_difficulty", "plant_difficulty_spread", "spine_consistency",
        "reporting_asymmetry", "mundanity", "contamination",
    ]
    assert body["spine"]["anchored_lines"] == 5
    assert body["spine"]["free_running_lines"] == 28
    assert body["detection"]["hit_rate"] == 0.25
    assert body["detection"]["limitation"] == planter.SHARED_PRIOR_LIMITATION
    for entry in body["detection"]["plants"]:
        assert entry["actionability_horizon"]
        assert entry["horizon_reason"]
        assert 0.0 <= entry["strength"] <= 1.0


def test_the_report_reproduces_byte_for_byte(netflix_repo_dir: Path, tmp_path: Path) -> None:
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    for out in (first, second):
        assert main([
            "substrate", "--repo", str(netflix_repo_dir), "--org", "netflix",
            "--recipe", str(RECIPE_PATH), "--checkpoint", CHECKPOINT, "--out", str(out),
        ]) == 0
    assert first.read_bytes() == second.read_bytes()


def test_a_late_detection_is_scored_late_in_the_report(netflix_repo_dir: Path, tmp_path: Path) -> None:
    """The one found plant, scored a year after its own horizon. The report carries the near-zero
    score and the reason naming the horizon, rather than the hit rate alone.
    """
    out = tmp_path / "late.json"
    assert main([
        "substrate", "--repo", str(netflix_repo_dir), "--org", "netflix",
        "--recipe", str(RECIPE_PATH), "--checkpoint", CHECKPOINT,
        "--detected-at", "2012-10-24", "--out", str(out),
    ]) == 0

    detection = json.loads(out.read_bytes())["body"]["detection"]
    found = [p for p in detection["plants"] if p["detected"]]
    assert len(found) == 1
    assert found[0]["timely"] is False
    assert found[0]["score"] < 0.1
    assert found[0]["actionability_horizon"] in found[0]["reason"]
