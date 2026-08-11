"""The NMC Health answer key (build ticket 39): a second real, dated, publicly documented
backtest key, low-notoriety on the same basis Carillion is (twin/fixtures.py's ticket 39 note).
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
from twin.repo import ModelRepo
from twin.reproduce import reproduce

SCENARIO = "would-the-twin-have-flagged-it"
ORG = fixtures.NMC_ORG


@pytest.fixture(scope="session")
def nmc_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_nmc_health_org(tmp_path_factory.mktemp("nmc-health") / "repo")


@pytest.fixture()
def nmc_overlay(nmc_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(nmc_repo_dir), ORG)


def test_the_fixture_validates_against_its_closed_schema(nmc_repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(nmc_repo_dir)]) == 0


def test_every_signal_carries_a_real_date_and_a_dated_source(nmc_overlay: Overlay) -> None:
    """AC: every fact in the key carries the date it became knowable."""
    assert len(nmc_overlay.signals) == 5
    for signal_id, signal in nmc_overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        assert "example.invalid" not in signal["provenance"].get("url", ""), (
            f"{signal_id} carries a placeholder URL, not a real citation"
        )
        assert signal["provenance"]["url"].startswith("https://")


def test_every_signal_is_bound_to_the_component_it_evidences(nmc_overlay: Overlay) -> None:
    assert len(nmc_overlay.claims) == 5
    for claim in nmc_overlay.claims.values():
        assert claim["component"] == "uk-listed-hospital-group"
        assert claim["signal"] in nmc_overlay.signals


def test_the_commit_history_is_monotonically_dated(nmc_repo_dir: Path) -> None:
    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(nmc_repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


def test_ground_truth_is_adversarial_and_contemporaneous_not_a_survivor_narrative(
    nmc_overlay: Overlay,
) -> None:
    """A capital-backed, dated short thesis is adversarial to the subject's own account of
    itself; using it as ground truth is not a cooperative retelling (decision ticket 19)."""
    urls = {s["provenance"]["url"] for s in nmc_overlay.signals.values()}
    assert any("muddywatersresearch.com" in u for u in urls), "no capital-backed short thesis cited"


def test_the_outcome_conforms_to_the_ticket_08_fixture_format(nmc_overlay: Overlay) -> None:
    outcome = nmc_overlay.outcomes["nmc-administration-resolved"]
    assert outcome["proposition"] == "the-subject-enters-formal-insolvency-proceedings-by-2020"
    assert outcome["observed"] is True
    assert outcome["resolved_on"] == "2020-04-09"
    assert outcome["contamination"] == "low"
    assert outcome["source_dated"] is True
    assert "healthcareandprotection.com" in outcome["source"]


def test_the_notoriety_assessment_is_recorded_not_asserted(nmc_overlay: Overlay) -> None:
    """AC: notoriety assessed and recorded per case (build ticket 39)."""
    outcome = nmc_overlay.outcomes["nmc-administration-resolved"]
    assert "notoriety" in outcome["note"].lower()
    assert outcome["contamination"] == "low"


def test_the_world_layer_names_no_tenant(nmc_repo_dir: Path) -> None:
    from twin.model import check_direction

    assert check_direction(ModelRepo.open(nmc_repo_dir)) == []


@pytest.mark.parametrize(
    ("at", "expect_available"),
    [("2019-12-01", True), ("2020-03-01", True), ("2021-01-01", True)],
)
def test_a_real_rewind_reads_the_repository_as_it_actually_stood(
    nmc_repo_dir: Path, at: str, expect_available: bool
) -> None:
    from twin import regimes

    repo = ModelRepo.open(nmc_repo_dir)
    history = regimes.ingestion_history(repo, at)
    assert history["available"] is expect_available
    assert "commit" in history


def test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences(nmc_repo_dir: Path) -> None:
    from twin import regimes

    repo = ModelRepo.open_at_time(nmc_repo_dir, "2020-03-15")
    overlay = Overlay.load(repo, ORG)
    assert "bind-debt-revised-5bn-2020-03-10" in overlay.claims
    assert "bind-debt-revised-6-6bn-2020-03-24" not in overlay.claims


def test_a_backtest_before_the_first_signal_sees_none_of_them(tmp_path: Path, nmc_repo_dir: Path) -> None:
    out = tmp_path / "backtest.json"
    assert main([
        "backtest", "--repo", str(nmc_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", "2019-11-20", "--out", str(out),
    ]) == 0
    doc = json.loads(out.read_bytes())
    assert doc["body"]["regime"]["gate"]["ingestion_history"]["available"] is True
    committed = doc["body"]["regime"]["gate"]["ingestion_history"]["committed"]
    assert committed < "2019-12-17"


def test_an_nmc_forecast_scores_against_the_resolved_answer_key(tmp_path: Path, nmc_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(nmc_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(nmc_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "nmc-administration-resolved", "--out", str(card),
    ]) == 0
    doc = json.loads(card.read_bytes())
    assert doc["body"]["scores"]
    assert doc["body"]["answer_key"]["contamination"] == "low"


def test_an_nmc_score_card_reproduces_from_its_own_pins(tmp_path: Path, nmc_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(nmc_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(nmc_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "nmc-administration-resolved", "--out", str(card),
    ]) == 0
    report = reproduce(nmc_repo_dir, card)
    assert report.reproduces, report.diff


def test_no_signal_cites_the_2023_fca_final_notice_which_is_hindsight(nmc_overlay: Overlay) -> None:
    """The Final Notice is published nearly four years after resolution — cited only on the
    outcome, never on a signal, or hindsight leaks into what is supposed to be contemporaneous."""
    for signal_id, signal in nmc_overlay.signals.items():
        assert "healthcareandprotection.com" not in signal["provenance"]["url"], (
            f"{signal_id} cites the post-collapse Final Notice"
        )
        assert signal["date"] < "2023-11-17"
