"""The Royal Mail answer key (build ticket 71): the falsifiability subject and the primary
missed-opportunity backtest case (decision tickets 19, 22; spec story 90).

Netflix cannot carry this beat: its story is famous, so a twin "anticipating" it is
indistinguishable from reciting it. Royal Mail is low-notoriety and unusually well-instrumented
— the counterfactual sits inside its own audited filings (GLS, reported line-by-line in the same
segmental accounts as the under-automated domestic business), anchored by a legally-liable IPO
prospectus forecasting the very trend it then underinvested against.
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
ORG = fixtures.ROYAL_MAIL_ORG


@pytest.fixture(scope="session")
def royal_mail_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_royal_mail_org(tmp_path_factory.mktemp("royal-mail") / "repo")


@pytest.fixture()
def royal_mail_overlay(royal_mail_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(royal_mail_repo_dir), ORG)


def test_the_fixture_validates_against_its_closed_schema(royal_mail_repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(royal_mail_repo_dir)]) == 0


def test_every_signal_carries_a_real_date_and_a_dated_source(royal_mail_overlay: Overlay) -> None:
    """AC: every fact in the key carries the date it became knowable."""
    assert len(royal_mail_overlay.signals) == 6
    for signal_id, signal in royal_mail_overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        assert "example.invalid" not in signal["provenance"].get("url", ""), (
            f"{signal_id} carries a placeholder URL, not a real citation"
        )
        assert signal["provenance"]["url"].startswith("https://")


def test_every_fact_carries_a_knowability_date_for_regime_gating(royal_mail_overlay: Overlay) -> None:
    """AC: every fact carries a knowability date for regime gating — the schema's own
    `DATED_FACTS` contract (`twin/schema.py`), not merely a human-readable date somewhere."""
    from twin.schema import DATED_FACTS

    signal_field = DATED_FACTS["signals"]
    outcome_field = DATED_FACTS["outcomes"]
    for signal_id, signal in royal_mail_overlay.signals.items():
        assert signal.get(signal_field), f"{signal_id} carries no {signal_field!r}"
    outcome = royal_mail_overlay.outcomes["royal-mail-concedes-the-automation-shortfall-2019"]
    assert outcome.get(outcome_field), f"the outcome carries no {outcome_field!r}"


def test_the_ipo_prospectus_signal_carries_its_date_and_legal_status(royal_mail_overlay: Overlay) -> None:
    """AC: the IPO prospectus forecast is captured with its date and its legal status noted."""
    signal = royal_mail_overlay.signals["ipo-prospectus-2013-09-27"]
    assert signal["date"] == "2013-09-27"
    legal_status = signal["provenance"].get("legal_status", "")
    assert legal_status, "the prospectus signal carries no legal_status field"
    assert "FSMA" in legal_status or "liab" in legal_status.lower()


def test_the_gls_counterfactual_sits_inside_the_subjects_own_filings(royal_mail_overlay: Overlay) -> None:
    """The distinguishing claim over every other missed-opportunity candidate (decision ticket
    19): the counterfactual is reported inside the subject's own segmental accounts, so no
    outside-rival inference is needed."""
    signal = royal_mail_overlay.signals["gls-outperforms-ukpil-fy2017-18-2018-05-17"]
    assert "own" in signal["statement"].lower()
    assert "segmental accounts" in signal["statement"]


def test_every_signal_is_bound_to_the_component_it_evidences(royal_mail_overlay: Overlay) -> None:
    assert len(royal_mail_overlay.claims) == 6
    for claim in royal_mail_overlay.claims.values():
        assert claim["component"] == "uk-parcels-and-letters-operator"
        assert claim["signal"] in royal_mail_overlay.signals


def test_the_commit_history_is_monotonically_dated(royal_mail_repo_dir: Path) -> None:
    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(royal_mail_repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


def test_the_outcome_conforms_to_the_ticket_08_fixture_format(royal_mail_overlay: Overlay) -> None:
    outcome = royal_mail_overlay.outcomes["royal-mail-concedes-the-automation-shortfall-2019"]
    assert outcome["proposition"] == "automation-shortfall-forces-a-remedial-investment-by-2019"
    assert outcome["observed"] is True
    assert outcome["resolved_on"] == "2019-05-23"
    assert outcome["contamination"] == "low"
    assert outcome["source_dated"] is True
    assert "ipc.be" in outcome["source"]


def test_the_notoriety_assessment_is_recorded_not_asserted(royal_mail_overlay: Overlay) -> None:
    """AC: notoriety assessed and recorded, the same discipline build ticket 39 established."""
    outcome = royal_mail_overlay.outcomes["royal-mail-concedes-the-automation-shortfall-2019"]
    assert "notoriety" in outcome["note"].lower()
    assert outcome["contamination"] == "low"


def test_the_world_layer_names_no_tenant(royal_mail_repo_dir: Path) -> None:
    """`world_never_references_overlay`: the proposition is generic; the subject's name lives
    only in the overlay."""
    from twin.model import check_direction

    assert check_direction(ModelRepo.open(royal_mail_repo_dir)) == []


@pytest.mark.parametrize(
    ("at", "expect_available"),
    [("2015-01-01", True), ("2018-06-01", True), ("2020-01-01", True)],
)
def test_a_real_rewind_reads_the_repository_as_it_actually_stood(
    royal_mail_repo_dir: Path, at: str, expect_available: bool
) -> None:
    from twin import regimes

    repo = ModelRepo.open(royal_mail_repo_dir)
    history = regimes.ingestion_history(repo, at)
    assert history["available"] is expect_available
    assert "commit" in history


def test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences(royal_mail_repo_dir: Path) -> None:
    from twin import regimes

    repo = ModelRepo.open_at_time(royal_mail_repo_dir, "2018-03-01")
    overlay = Overlay.load(repo, ORG)
    assert "bind-cwu-four-pillars-2018-01-31" in overlay.claims
    assert "bind-gls-outperforms-ukpil-fy2017-18-2018-05-17" not in overlay.claims


def test_a_backtest_before_the_first_signal_sees_none_of_them(
    tmp_path: Path, royal_mail_repo_dir: Path
) -> None:
    out = tmp_path / "backtest.json"
    assert main([
        "backtest", "--repo", str(royal_mail_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", "2013-09-15", "--out", str(out),
    ]) == 0
    doc = json.loads(out.read_bytes())
    assert doc["body"]["regime"]["gate"]["ingestion_history"]["available"] is True
    committed = doc["body"]["regime"]["gate"]["ingestion_history"]["committed"]
    assert committed < "2013-09-27"


def test_a_royal_mail_forecast_scores_against_the_resolved_answer_key(
    tmp_path: Path, royal_mail_repo_dir: Path
) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(royal_mail_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(royal_mail_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "royal-mail-concedes-the-automation-shortfall-2019", "--out", str(card),
    ]) == 0
    doc = json.loads(card.read_bytes())
    assert doc["body"]["scores"]
    assert doc["body"]["answer_key"]["contamination"] == "low"


def test_a_royal_mail_score_card_reproduces_from_its_own_pins(
    tmp_path: Path, royal_mail_repo_dir: Path
) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "run", "--repo", str(royal_mail_repo_dir), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(royal_mail_repo_dir), "--org", ORG, "--forecast", str(bundle),
        "--outcome", "royal-mail-concedes-the-automation-shortfall-2019", "--out", str(card),
    ]) == 0
    report = reproduce(royal_mail_repo_dir, card)
    assert report.reproduces, report.diff


def test_no_signal_cites_the_investment_concession_which_is_hindsight(royal_mail_overlay: Overlay) -> None:
    """The May 2019 investment-programme announcement is the answer key's own resolving source —
    cited only on the outcome, published after every signal's own date, never on a signal, or
    hindsight leaks into what is supposed to be contemporaneous."""
    for signal_id, signal in royal_mail_overlay.signals.items():
        assert "ipc.be" not in signal["provenance"]["url"], (
            f"{signal_id} cites the resolving investment-concession announcement"
        )
        assert signal["date"] < "2019-05-23"
