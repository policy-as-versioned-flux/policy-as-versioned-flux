"""The hindsight-resistance controls (build ticket 41): two cases where the contemporaneous
record and the now-canonical story disagree. AstraZeneca (rejects Pfizer, 2014) and Sanofi (exits
diabetes/cardiovascular for GLP-1 obesity, 2019) are inverse pairs — one contemporaneously
punished then retold as visionary, one contemporaneously approved then retold as a miss. Each
carries two world models on one scenario, so confident agreement with the canonical story is
caught structurally: it scores against the recorded (contemporaneous) outcome, not the story.
"""

from __future__ import annotations

import datetime
import re
import subprocess
from pathlib import Path

import pytest

from twin import fixtures
from twin.cli import main
from twin.model import Overlay, check_direction
from twin.reproduce import reproduce
from twin.repo import ModelRepo
from twin.scoring import measure_discount

SCENARIO = "would-the-twin-recite-the-ending"


@pytest.fixture(scope="session")
def az_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_astrazeneca_org(tmp_path_factory.mktemp("astrazeneca") / "repo")


@pytest.fixture(scope="session")
def sanofi_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_sanofi_org(tmp_path_factory.mktemp("sanofi") / "repo")


@pytest.fixture()
def az_overlay(az_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(az_repo_dir), fixtures.ASTRAZENECA_ORG)


@pytest.fixture()
def sanofi_overlay(sanofi_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(sanofi_repo_dir), fixtures.SANOFI_ORG)


# -- shape shared by both cases ------------------------------------------------------------


@pytest.mark.parametrize("fixture_name", ["az_repo_dir", "sanofi_repo_dir"])
def test_the_fixture_validates_against_its_closed_schema(fixture_name: str, request: pytest.FixtureRequest) -> None:
    repo_dir = request.getfixturevalue(fixture_name)
    assert main(["validate", "--repo", str(repo_dir)]) == 0


@pytest.mark.parametrize("overlay_name", ["az_overlay", "sanofi_overlay"])
def test_every_signal_carries_a_real_date_and_a_dated_source(
    overlay_name: str, request: pytest.FixtureRequest
) -> None:
    """AC: at least two cases where the contemporaneous record and canonical narrative diverge,
    both documented."""
    overlay = request.getfixturevalue(overlay_name)
    assert len(overlay.signals) == 3
    for signal_id, signal in overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        assert "example.invalid" not in signal["provenance"].get("url", ""), (
            f"{signal_id} carries a placeholder URL, not a real citation"
        )
        assert signal["provenance"]["url"].startswith("https://")


@pytest.mark.parametrize(
    ("repo_fixture", "org"),
    [("az_repo_dir", fixtures.ASTRAZENECA_ORG), ("sanofi_repo_dir", fixtures.SANOFI_ORG)],
)
def test_the_commit_history_is_monotonically_dated(
    repo_fixture: str, org: str, request: pytest.FixtureRequest
) -> None:
    repo_dir = request.getfixturevalue(repo_fixture)
    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


@pytest.mark.parametrize("repo_fixture", ["az_repo_dir", "sanofi_repo_dir"])
def test_the_world_layer_names_no_tenant(repo_fixture: str, request: pytest.FixtureRequest) -> None:
    repo_dir = request.getfixturevalue(repo_fixture)
    assert check_direction(ModelRepo.open(repo_dir)) == []


@pytest.mark.parametrize("overlay_name", ["az_overlay", "sanofi_overlay"])
def test_both_world_models_are_present_on_the_same_scenario(
    overlay_name: str, request: pytest.FixtureRequest
) -> None:
    """No collapse mechanism: one execution emits both the honest and the canonical-hindsight
    forecast, never one or the other."""
    overlay = request.getfixturevalue(overlay_name)
    scenario = overlay.scenarios[SCENARIO]
    assert set(scenario["world_models"]) == {"contemporaneous-consensus", "canonical-hindsight-consensus"}


# -- the inversion is explicit in the score card (AC 2) -------------------------------------


def test_the_az_outcome_declares_the_hindsight_trap(az_overlay: Overlay) -> None:
    outcome = az_overlay.outcomes["az-market-verdict-resolved"]
    assert outcome["hindsight_trap"] is True
    assert outcome["contamination"] == "high"
    assert outcome["observed"] is False, "the contemporaneous market punished the decision"


def test_the_sanofi_outcome_declares_the_hindsight_trap(sanofi_overlay: Overlay) -> None:
    outcome = sanofi_overlay.outcomes["sanofi-market-verdict-resolved"]
    assert outcome["hindsight_trap"] is True
    assert outcome["contamination"] == "high"
    assert outcome["observed"] is True, "the contemporaneous market approved the decision"


def test_no_astrazeneca_signal_cites_the_2026_canonical_retelling_which_is_hindsight(
    az_overlay: Overlay,
) -> None:
    """The techtimes piece reframing this as visionary is published 2026-08-02, over twelve years
    after resolution — cited only on the outcome, never used to date a signal."""
    for signal_id, signal in az_overlay.signals.items():
        assert "techtimes.com" not in signal["provenance"]["url"], (
            f"{signal_id} cites the 2026 canonical retelling"
        )
        assert signal["date"] < "2014-05-21"


# -- scoring against the recorded (contemporaneous) outcome, per case -----------------------


def _run_and_score(tmp_path: Path, repo_dir: Path, org: str, outcome_id: str, tag: str) -> Path:
    bundle, card = tmp_path / f"{tag}-bundle.json", tmp_path / f"{tag}-card.json"
    assert main([
        "run", "--repo", str(repo_dir), "--org", org, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(repo_dir), "--org", org, "--forecast", str(bundle),
        "--outcome", outcome_id, "--out", str(card),
    ]) == 0
    return card


def _scores_by_world_model(card: Path) -> dict[str, dict]:
    from twin.artefact import load as load_artefact

    doc = load_artefact(card)
    return {entry["world_model"]: entry for entry in doc["body"]["scores"]}


@pytest.mark.parametrize(
    ("repo_fixture", "org", "outcome_id", "tag"),
    [
        ("az_repo_dir", fixtures.ASTRAZENECA_ORG, "az-market-verdict-resolved", "az"),
        ("sanofi_repo_dir", fixtures.SANOFI_ORG, "sanofi-market-verdict-resolved", "sanofi"),
    ],
)
def test_the_canonical_hindsight_world_model_scores_worse_than_the_honest_one(
    tmp_path: Path, repo_fixture: str, org: str, outcome_id: str, tag: str, request: pytest.FixtureRequest,
) -> None:
    """AC: a demonstration that a memorising system scores worse on these than a non-memorising
    one would. No special-cased scoring code: `scoring.score` runs unmodified — the trap is that
    the canonical story and the contemporaneous ground truth disagree, so a forecast that recites
    the story is simply wrong about the recorded outcome."""
    repo_dir = request.getfixturevalue(repo_fixture)
    card = _run_and_score(tmp_path, repo_dir, org, outcome_id, tag)
    scores = _scores_by_world_model(card)

    honest = scores["contemporaneous-consensus"]
    memorising = scores["canonical-hindsight-consensus"]
    assert memorising["brier"] > honest["brier"]
    assert memorising["log_loss"] > honest["log_loss"]


def test_the_two_cases_are_an_inverse_pair(tmp_path: Path, az_repo_dir: Path, sanofi_repo_dir: Path) -> None:
    """AZ was contemporaneously punished then retold as visionary; Sanofi was contemporaneously
    approved then retold as a miss. The canonical-hindsight world model is confidently wrong in
    opposite directions on the same proposition."""
    az_scores = _scores_by_world_model(
        _run_and_score(tmp_path, az_repo_dir, fixtures.ASTRAZENECA_ORG, "az-market-verdict-resolved", "az")
    )
    sanofi_scores = _scores_by_world_model(
        _run_and_score(tmp_path, sanofi_repo_dir, fixtures.SANOFI_ORG, "sanofi-market-verdict-resolved", "sanofi")
    )
    assert az_scores["canonical-hindsight-consensus"]["probability"] > 0.5
    assert az_scores["contemporaneous-consensus"]["probability"] < 0.5
    assert sanofi_scores["canonical-hindsight-consensus"]["probability"] < 0.5
    assert sanofi_scores["contemporaneous-consensus"]["probability"] > 0.5


def test_an_undiscounted_hindsight_score_card_reproduces_from_its_own_pins(
    tmp_path: Path, az_repo_dir: Path,
) -> None:
    card = _run_and_score(tmp_path, az_repo_dir, fixtures.ASTRAZENECA_ORG, "az-market-verdict-resolved", "az")
    report = reproduce(az_repo_dir, card)
    assert report.reproduces, report.diff


# -- results feed the contamination discount rather than sitting alongside it (AC 4) --------


def test_the_hindsight_gap_folds_into_the_same_discount_enron_versus_obscure_measures(
    tmp_path: Path, az_repo_dir: Path,
) -> None:
    """AC (build ticket 41): results feed the contamination discount rather than sitting
    alongside it. Built from the real AstraZeneca fixture's own scores, not synthetic numbers —
    the unit-level proof that the mechanism folds two legs together already lives in
    tests/test_scoring.py."""
    card = _run_and_score(tmp_path, az_repo_dir, fixtures.ASTRAZENECA_ORG, "az-market-verdict-resolved", "az")
    scores = _scores_by_world_model(card)
    memorising = [scores["canonical-hindsight-consensus"]]
    honest = [scores["contemporaneous-consensus"]]

    enron = [{"brier": 0.9409, "log_loss": 2.813}]  # a representative obscure-key-style loss pair
    obscure = [{"brier": 0.9025, "log_loss": 2.708}]

    without_hindsight = measure_discount(enron, obscure, rule="brier")
    with_hindsight = measure_discount(
        enron, obscure, rule="brier", hindsight_memorising=memorising, hindsight_honest=honest
    )
    assert with_hindsight["discount"] != without_hindsight["discount"]
    assert len(with_hindsight["legs"]) == 2
    assert with_hindsight["legs"][1]["leg"] == "hindsight-memorising-vs-honest"
    assert with_hindsight["legs"][1]["gap"] > 0, "the memorising world model scores worse, confirming the trap"
