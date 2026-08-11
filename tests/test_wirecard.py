"""The Wirecard answer key (build ticket 39): a third real, dated, publicly documented backtest
key. Unlike Carillion and NMC Health, the ticket 39 notoriety assessment finds this case is NOT
low-notoriety (twin/fixtures.py's note) — `contamination: high` records that honestly.
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
ORG = fixtures.WIRECARD_ORG


@pytest.fixture(scope="session")
def wirecard_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_wirecard_org(tmp_path_factory.mktemp("wirecard") / "repo")


@pytest.fixture()
def wirecard_overlay(wirecard_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(wirecard_repo_dir), ORG)


def test_the_fixture_validates_against_its_closed_schema(wirecard_repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(wirecard_repo_dir)]) == 0


def test_every_signal_carries_a_real_date_and_a_dated_source(wirecard_overlay: Overlay) -> None:
    """AC: every fact in the key carries the date it became knowable."""
    assert len(wirecard_overlay.signals) == 6
    for signal_id, signal in wirecard_overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        assert "example.invalid" not in signal["provenance"].get("url", ""), (
            f"{signal_id} carries a placeholder URL, not a real citation"
        )
        assert signal["provenance"]["url"].startswith("https://")


def test_every_signal_is_bound_to_the_component_it_evidences(wirecard_overlay: Overlay) -> None:
    assert len(wirecard_overlay.claims) == 6
    for claim in wirecard_overlay.claims.values():
        assert claim["component"] == "third-party-acquiring-business"
        assert claim["signal"] in wirecard_overlay.signals


def test_the_commit_history_is_monotonically_dated(wirecard_repo_dir: Path) -> None:
    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(wirecard_repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


def test_ground_truth_includes_an_official_regulatory_record(wirecard_overlay: Overlay) -> None:
    """The regulator's own short-selling ban is a dated, official record that the subject's
    accounts were under public dispute — adversarial context, not a survivor narrative."""
    urls = {s["provenance"]["url"] for s in wirecard_overlay.signals.values()}
    assert any("bafin.de" in u for u in urls), "no official regulatory record cited"


def test_the_outcome_conforms_to_the_ticket_08_fixture_format(wirecard_overlay: Overlay) -> None:
    outcome = wirecard_overlay.outcomes["wirecard-insolvency-resolved"]
    assert outcome["proposition"] == "the-subject-enters-formal-insolvency-proceedings-by-2020"
    assert outcome["observed"] is True
    assert outcome["resolved_on"] == "2020-06-25"
    assert outcome["contamination"] == "high"
    assert outcome["source_dated"] is True
    assert "bundestag.de" in outcome["source"]


def test_the_notoriety_assessment_finds_this_case_is_not_low_notoriety(wirecard_overlay: Overlay) -> None:
    """AC: notoriety assessed and recorded per case, evidenced rather than asserted (build
    ticket 39) — the honest finding here diverges from spec story 45's shorthand grouping of
    Carillion, NMC Health and Wirecard as uniformly "low-notoriety"."""
    outcome = wirecard_overlay.outcomes["wirecard-insolvency-resolved"]
    assert outcome["contamination"] == "high"
    assert "NOT low-notoriety" in outcome["note"]
    from twin.schema import CONTAMINATION

    assert "high" in CONTAMINATION


def test_the_world_layer_names_no_tenant(wirecard_repo_dir: Path) -> None:
    from twin.model import check_direction

    assert check_direction(ModelRepo.open(wirecard_repo_dir)) == []


@pytest.mark.parametrize(
    ("at", "expect_available"),
    [("2016-03-01", True), ("2019-06-01", True), ("2020-07-01", True)],
)
def test_a_real_rewind_reads_the_repository_as_it_actually_stood(
    wirecard_repo_dir: Path, at: str, expect_available: bool
) -> None:
    from twin import regimes

    repo = ModelRepo.open(wirecard_repo_dir)
    history = regimes.ingestion_history(repo, at)
    assert history["available"] is expect_available
    assert "commit" in history


def test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences(wirecard_repo_dir: Path) -> None:
    from twin import regimes

    repo = ModelRepo.open_at_time(wirecard_repo_dir, "2019-03-01")
    overlay = Overlay.load(repo, ORG)
    assert "bind-bafin-short-selling-ban-2019-02-18" in overlay.claims
    assert "bind-kpmg-special-audit-2020-04-28" not in overlay.claims


def test_a_backtest_before_the_first_signal_sees_none_of_them(tmp_path: Path, wirecard_repo_dir: Path) -> None:
    out = tmp_path / "backtest.json"
    assert main([
        "backtest", "--repo", str(wirecard_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", "2016-02-10", "--out", str(out),
    ]) == 0
    doc = json.loads(out.read_bytes())
    assert doc["body"]["regime"]["gate"]["ingestion_history"]["available"] is True
    committed = doc["body"]["regime"]["gate"]["ingestion_history"]["committed"]
    assert committed < "2016-02-24"


def test_a_wirecard_forecast_scores_against_the_resolved_answer_key(tmp_path: Path, wirecard_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(wirecard_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(wirecard_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "wirecard-insolvency-resolved", "--out", str(card),
    ]) == 0
    doc = json.loads(card.read_bytes())
    assert doc["body"]["scores"]
    assert doc["body"]["answer_key"]["contamination"] == "high"


def test_a_wirecard_score_card_reproduces_from_its_own_pins(tmp_path: Path, wirecard_repo_dir: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(wirecard_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(wirecard_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "wirecard-insolvency-resolved", "--out", str(card),
    ]) == 0
    report = reproduce(wirecard_repo_dir, card)
    assert report.reproduces, report.diff


def test_no_signal_cites_the_2021_bundestag_report_which_is_hindsight(wirecard_overlay: Overlay) -> None:
    """The Bundestag inquiry report is published nearly a year after resolution — cited only on
    the outcome, never on a signal, or hindsight leaks into what is supposed to be
    contemporaneous ground truth."""
    for signal_id, signal in wirecard_overlay.signals.items():
        assert "bundestag.de" not in signal["provenance"]["url"], (
            f"{signal_id} cites the post-collapse Bundestag report"
        )
        assert signal["date"] < "2021-06-22"
