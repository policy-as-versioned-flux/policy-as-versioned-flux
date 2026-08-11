"""The Carillion answer key (build ticket 38): a real, dated, adversarially-sourced backtest key.

Chosen for low notoriety over fame — success against a famous collapse is not distinguishable
from reciting it (research/opportunity-cases.md). Unlike the main netflix/intel fixture, this
repository's own commit history genuinely spans 2016-2018, so a real rewind has something to read.
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import pytest

from twin import fixtures
from twin.cli import main
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.reproduce import reproduce

SCENARIO = "would-the-twin-have-flagged-it"
ORG = fixtures.CARILLION_ORG


@pytest.fixture(scope="session")
def carillion_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_carillion_org(tmp_path_factory.mktemp("carillion") / "repo")


@pytest.fixture()
def carillion_overlay(carillion_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(carillion_repo_dir), ORG)


def test_the_fixture_validates_against_its_closed_schema(carillion_repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(carillion_repo_dir)]) == 0


def test_every_signal_carries_a_real_date_and_a_dated_source(carillion_overlay: Overlay) -> None:
    """AC: every fact in the key carries the date it became knowable."""
    assert len(carillion_overlay.signals) == 8
    for signal_id, signal in carillion_overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        assert "example.invalid" not in signal["provenance"].get("url", ""), (
            f"{signal_id} carries a placeholder URL, not a real citation"
        )
        assert signal["provenance"]["url"].startswith("https://")


def test_every_signal_is_bound_to_the_component_it_evidences(carillion_overlay: Overlay) -> None:
    assert len(carillion_overlay.claims) == 8
    for claim in carillion_overlay.claims.values():
        assert claim["component"] == "carillion-uk-construction"
        assert claim["signal"] in carillion_overlay.signals


def test_the_commit_history_is_monotonically_dated(carillion_repo_dir: Path) -> None:
    """A fixture that back-dated a commit behind its parent would make a rewind's answer depend
    on how far git chooses to keep walking (the same discipline `build_regime_org` documents)."""
    import subprocess

    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(carillion_repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


def test_ground_truth_is_adversarial_and_contemporaneous_not_a_survivor_narrative(
    carillion_overlay: Overlay,
) -> None:
    """AC: ground truth drawn from adversarial and contemporaneous records, not retrospective
    narrative. The regulator's misleading-statement finding and the market's short position are
    both adversarial to the company's own account of itself; neither is a cooperative retelling."""
    urls = {s["provenance"]["url"] for s in carillion_overlay.signals.values()}
    assert any("fca.org.uk" in u for u in urls), "no adversarial regulatory finding cited"
    assert any("short-selling" in u or "commonslibrary" in u for u in urls)


def test_the_outcome_conforms_to_the_ticket_08_fixture_format(carillion_overlay: Overlay) -> None:
    outcome = carillion_overlay.outcomes["carillion-collapse-resolved"]
    assert outcome["proposition"] == "contractor-enters-insolvency-by-2018"
    assert outcome["observed"] is True
    assert outcome["resolved_on"] == "2018-01-15"
    assert outcome["contamination"] == "low"
    assert outcome["source_dated"] is True
    assert "HC 769" in outcome["source"]


def test_the_world_layer_names_no_tenant(carillion_repo_dir: Path) -> None:
    """`world_never_references_overlay`: the proposition is generic, the same way netflix's own
    proposition never says "Netflix" — Carillion's name lives only in the overlay."""
    from twin.model import check_direction

    assert check_direction(ModelRepo.open(carillion_repo_dir)) == []


@pytest.mark.parametrize(
    ("at", "expect_available"),
    [("2017-01-01", True), ("2017-08-01", True), ("2019-01-01", True)],
)
def test_a_real_rewind_reads_the_repository_as_it_actually_stood(
    carillion_repo_dir: Path, at: str, expect_available: bool
) -> None:
    """Unlike netflix's 2011 subject (whose repository was built in 2026),
    Carillion's own commit history genuinely spans the subject's dates — `ingestion_history`
    reports a real commit, not `available: false`."""
    from twin import regimes

    repo = ModelRepo.open(carillion_repo_dir)
    history = regimes.ingestion_history(repo, at)
    assert history["available"] is expect_available
    assert "commit" in history


def test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences(carillion_repo_dir: Path) -> None:
    """Each claim exists in this repository's history as of the same real date the signal does,
    not batched into one commit after the collapse — otherwise an as-consumed backtest at any
    real date before the batch would see the signal but find nothing bound to it."""
    from twin import regimes

    repo = ModelRepo.open_at_time(carillion_repo_dir, "2017-08-01")
    overlay = Overlay.load(repo, ORG)
    assert "bind-profit-warning-2017-07-10" in overlay.claims
    assert "bind-profit-warning-2017-09-29" not in overlay.claims


def test_a_backtest_before_the_first_signal_sees_none_of_them(tmp_path: Path, carillion_repo_dir: Path) -> None:
    out = tmp_path / "backtest.json"
    assert main([
        "backtest", "--repo", str(carillion_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", "2016-11-20", "--out", str(out),
    ]) == 0
    doc = json.loads(out.read_bytes())
    assert doc["body"]["regime"]["gate"]["ingestion_history"]["available"] is True
    committed = doc["body"]["regime"]["gate"]["ingestion_history"]["committed"]
    assert committed < "2016-12-07"


def test_a_carillion_forecast_scores_against_the_resolved_answer_key(tmp_path: Path, carillion_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(carillion_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(carillion_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "carillion-collapse-resolved", "--out", str(card),
    ]) == 0
    doc = json.loads(card.read_bytes())
    assert doc["body"]["scores"]
    assert doc["body"]["answer_key"]["contamination"] == "low"


def test_a_carillion_score_card_reproduces_from_its_own_pins(tmp_path: Path, carillion_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(carillion_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(carillion_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "carillion-collapse-resolved", "--out", str(card),
    ]) == 0
    report = reproduce(carillion_repo_dir, card)
    assert report.reproduces, report.diff


def test_no_signal_dates_a_fact_using_hc_769_which_is_hindsight(carillion_overlay: Overlay) -> None:
    """HC 769 is published 2018-05-16, after every signal's own date — cited only on the outcome,
    never used to date a signal, or hindsight leaks into what is supposed to be contemporaneous."""
    for signal_id, signal in carillion_overlay.signals.items():
        assert "769" not in signal["provenance"]["url"], f"{signal_id} cites the post-collapse inquiry report"
        assert signal["date"] < "2018-05-16"
