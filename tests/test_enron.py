"""The Enron contamination-control fixture (build ticket 40): not a fourth low-notoriety key —
the opposite. An LLM asked about Enron has read the ending, so this fixture holds the identical
contract Carillion/NMC/Wirecard do (dated signals, a closed schema, an adversarial post-mortem
cited only on the outcome, a real monotonic commit history) so that scoring against it is
comparable to scoring against an obscure key, not a different measurement.
"""

from __future__ import annotations

import datetime
import json
import re
import subprocess
from pathlib import Path

import pytest

from twin import fixtures
from twin.cli import main
from twin.model import Overlay
from twin.reproduce import ReproduceError, reproduce
from twin.repo import ModelRepo
from twin.scoring import measure_discount

SCENARIO = "would-the-twin-have-flagged-it"
ORG = fixtures.ENRON_ORG


@pytest.fixture(scope="session")
def enron_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_enron_org(tmp_path_factory.mktemp("enron") / "repo")


@pytest.fixture(scope="session")
def carillion_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_carillion_org(tmp_path_factory.mktemp("carillion") / "repo")


@pytest.fixture()
def enron_overlay(enron_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(enron_repo_dir), ORG)


def test_the_fixture_validates_against_its_closed_schema(enron_repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(enron_repo_dir)]) == 0


def test_every_signal_carries_a_real_date_and_a_dated_source(enron_overlay: Overlay) -> None:
    """AC: Enron key authored in the same format as the low-notoriety keys."""
    assert len(enron_overlay.signals) == 4
    for signal_id, signal in enron_overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        assert "example.invalid" not in signal["provenance"].get("url", ""), (
            f"{signal_id} carries a placeholder URL, not a real citation"
        )
        assert signal["provenance"]["url"].startswith("https://")


def test_every_signal_is_bound_to_the_component_it_evidences(enron_overlay: Overlay) -> None:
    assert len(enron_overlay.claims) == 4
    for claim in enron_overlay.claims.values():
        assert claim["component"] == "energy-trading-book"
        assert claim["signal"] in enron_overlay.signals


def test_the_commit_history_is_monotonically_dated(enron_repo_dir: Path) -> None:
    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(enron_repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


def test_the_outcome_conforms_to_the_ticket_08_fixture_format(enron_overlay: Overlay) -> None:
    outcome = enron_overlay.outcomes["enron-bankruptcy-resolved"]
    assert outcome["proposition"] == "the-subject-enters-bankruptcy-protection-by-2002"
    assert outcome["observed"] is True
    assert outcome["resolved_on"] == "2001-12-02"
    assert outcome["source_dated"] is True
    assert "Powers Report" in outcome["source"]


def test_the_outcome_declares_the_contamination_control_class_not_a_fourth_low_notoriety_key(
    enron_overlay: Overlay,
) -> None:
    """AC: not a fourth low-notoriety key. `CONTAMINATION` (twin/schema.py) reserves `"control"`
    for exactly this fixture."""
    outcome = enron_overlay.outcomes["enron-bankruptcy-resolved"]
    assert outcome["contamination"] == "control"
    from twin.schema import CONTAMINATION

    assert "control" in CONTAMINATION


def test_the_world_layer_names_no_tenant(enron_repo_dir: Path) -> None:
    from twin.model import check_direction

    assert check_direction(ModelRepo.open(enron_repo_dir)) == []


@pytest.mark.parametrize(
    ("at", "expect_available"),
    [("2001-09-01", True), ("2001-10-20", True), ("2002-01-01", True)],
)
def test_a_real_rewind_reads_the_repository_as_it_actually_stood(
    enron_repo_dir: Path, at: str, expect_available: bool
) -> None:
    from twin import regimes

    repo = ModelRepo.open(enron_repo_dir)
    history = regimes.ingestion_history(repo, at)
    assert history["available"] is expect_available
    assert "commit" in history


def test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences(enron_repo_dir: Path) -> None:
    from twin import regimes

    repo = ModelRepo.open_at_time(enron_repo_dir, "2001-09-01")
    overlay = Overlay.load(repo, ORG)
    assert "bind-skilling-resigns-2001-08-14" in overlay.claims
    assert "bind-q3-loss-and-equity-writedown-2001-10-16" not in overlay.claims


def test_a_backtest_before_the_first_signal_sees_none_of_them(tmp_path: Path, enron_repo_dir: Path) -> None:
    out = tmp_path / "backtest.json"
    assert main([
        "backtest", "--repo", str(enron_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", "2001-07-20", "--out", str(out),
    ]) == 0
    doc = json.loads(out.read_bytes())
    assert doc["body"]["regime"]["gate"]["ingestion_history"]["available"] is True
    committed = doc["body"]["regime"]["gate"]["ingestion_history"]["committed"]
    assert committed < "2001-08-14"


def test_an_enron_forecast_scores_against_the_resolved_answer_key(tmp_path: Path, enron_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(enron_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(enron_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "enron-bankruptcy-resolved", "--out", str(card),
    ]) == 0
    doc = json.loads(card.read_bytes())
    assert doc["body"]["scores"]
    assert doc["body"]["answer_key"]["contamination"] == "control"
    assert doc["body"]["answer_key"]["hindsight_trap"] is False
    assert doc["body"]["contamination_discount"] is None


def test_an_enron_score_card_reproduces_from_its_own_pins(tmp_path: Path, enron_repo_dir: Path) -> None:
    """Undiscounted, an Enron score card is exactly as reproducible as any other."""
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(enron_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(enron_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "enron-bankruptcy-resolved", "--out", str(card),
    ]) == 0
    report = reproduce(enron_repo_dir, card)
    assert report.reproduces, report.diff


def test_no_signal_cites_the_powers_report_which_is_hindsight(enron_overlay: Overlay) -> None:
    """The Powers Report is published 2002-02-01, just over two months after resolution — cited
    only on the outcome, never used to date a signal, or hindsight leaks into what is supposed to
    be contemporaneous ground truth."""
    for signal_id, signal in enron_overlay.signals.items():
        assert "powers.report" not in signal["provenance"]["url"], (
            f"{signal_id} cites the post-collapse Powers Report"
        )
        assert signal["date"] < "2002-02-01"


def test_the_discount_measured_from_enron_versus_carillion_is_measured_not_hardcoded(
    tmp_path: Path, enron_repo_dir: Path, carillion_repo_dir: Path,
) -> None:
    """AC: the discount is measured from the Enron-versus-obscure gap, never hardcoded — and the
    obscure leg is Carillion (or NMC), never Wirecard (build ticket 39's own note)."""
    enron_bundle, enron_card = tmp_path / "enron-bundle.json", tmp_path / "enron-card.json"
    carillion_bundle, carillion_card = tmp_path / "carillion-bundle.json", tmp_path / "carillion-card.json"

    assert main([
        "run", "--repo", str(enron_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(enron_bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(enron_repo_dir), "--org", ORG, "--forecast", str(enron_bundle),
        "--outcome", "enron-bankruptcy-resolved", "--out", str(enron_card),
    ]) == 0
    assert main([
        "run", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--scenario", SCENARIO, "--regime", "as-consumed", "--out", str(carillion_bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--forecast", str(carillion_bundle), "--outcome", "carillion-collapse-resolved",
        "--out", str(carillion_card),
    ]) == 0

    from twin.artefact import load as load_artefact

    enron_scores = load_artefact(enron_card)["body"]["scores"]
    carillion_scores = load_artefact(carillion_card)["body"]["scores"]
    expected = measure_discount(enron_scores, carillion_scores, rule="brier")

    # A downstream score card, scored under the same CLI, carries the identical measurement.
    third_bundle, third_card = tmp_path / "third-bundle.json", tmp_path / "third-card.json"
    assert main([
        "run", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--scenario", SCENARIO, "--regime", "as-consumed", "--out", str(third_bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--forecast", str(third_bundle), "--outcome", "carillion-collapse-resolved",
        "--out", str(third_card), "--discount-enron", str(enron_card),
        "--discount-obscure", str(carillion_card),
    ]) == 0
    doc = load_artefact(third_card)
    assert doc["body"]["contamination_discount"] == expected
    assert expected["discount"] != 0, "a degenerate fixture would not exercise the additive leg below"
    for entry in doc["body"]["scores"]:
        assert entry["discount"] == expected["discount"]
        assert entry["adjusted_brier"] == pytest.approx(entry["brier"] + expected["discount"])
        # AC: reported separately from the raw score so both are visible — the raw figure survives
        # untouched beside the adjusted one, rather than being overwritten by it.
        assert entry["brier"] != entry["adjusted_brier"]


def test_a_discounted_score_card_honestly_refuses_to_replay_from_pins(
    tmp_path: Path, enron_repo_dir: Path, carillion_repo_dir: Path,
) -> None:
    """A discount is measured from other score cards named by path at the CLI, never pinned in
    the command (the same reason `--forecast` is pinned by digest, not by path). Rather than
    silently mis-replaying to a mismatched digest, `reproduce()` refuses honestly. `twin
    reliability`'s own pooled inputs no longer share this limit (build ticket 89 gave them a
    `produced_by` pin to walk, not just a digest to check) — a discount's sources carry no such
    pin at all, so there is nothing here to walk even in principle."""
    enron_bundle, enron_card = tmp_path / "enron-bundle.json", tmp_path / "enron-card.json"
    carillion_bundle, carillion_card = tmp_path / "carillion-bundle.json", tmp_path / "carillion-card.json"
    assert main([
        "run", "--repo", str(enron_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(enron_bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(enron_repo_dir), "--org", ORG, "--forecast", str(enron_bundle),
        "--outcome", "enron-bankruptcy-resolved", "--out", str(enron_card),
    ]) == 0
    assert main([
        "run", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--scenario", SCENARIO, "--regime", "as-consumed", "--out", str(carillion_bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--forecast", str(carillion_bundle), "--outcome", "carillion-collapse-resolved",
        "--out", str(carillion_card),
    ]) == 0

    discounted_card = tmp_path / "discounted-card.json"
    assert main([
        "score", "--repo", str(carillion_repo_dir), "--org", fixtures.CARILLION_ORG,
        "--forecast", str(carillion_bundle), "--outcome", "carillion-collapse-resolved",
        "--out", str(discounted_card), "--discount-enron", str(enron_card),
        "--discount-obscure", str(carillion_card),
    ]) == 0
    with pytest.raises(ReproduceError, match="discount-sha256"):
        reproduce(carillion_repo_dir, discounted_card)
