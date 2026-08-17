"""The breadth portfolio (build ticket 76, decision tickets 01 and 06): Kodak and Maersk, each
present at declared stub depth on its own independent track — not a third and fourth answer key.
Decision ticket 01: portfolio orgs "don't carry the backtest burden" the flagships and the
dedicated backtest suite do, so there is no outcome/score test here, unlike `test_nmc_health.py`.
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
from twin.repo import ModelRepo
from twin.reproduce import reproduce

SCENARIO = "would-the-twin-have-flagged-it"

ORGS = {
    fixtures.KODAK_ORG: (fixtures.build_kodak_org, "consumer-film-and-imaging-business"),
    fixtures.MAERSK_ORG: (fixtures.build_maersk_org, "global-container-logistics-it"),
}


@pytest.fixture(scope="session", params=sorted(ORGS))
def org(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="session")
def repo_dir(org: str, tmp_path_factory: pytest.TempPathFactory) -> Path:
    builder, _ = ORGS[org]
    return builder(tmp_path_factory.mktemp(org) / "repo")


@pytest.fixture()
def overlay(repo_dir: Path, org: str) -> Overlay:
    return Overlay.load(ModelRepo.open(repo_dir), org)


def test_the_fixture_validates_against_its_closed_schema(repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(repo_dir)]) == 0


def test_every_signal_carries_a_real_date_and_a_dated_source(overlay: Overlay) -> None:
    assert len(overlay.signals) == 2, "stub is the declared depth — two real signals, not five"
    for signal_id, signal in overlay.signals.items():
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", signal["date"]), f"{signal_id} has no dated fact"
        assert signal["source"], f"{signal_id} names no source"
        url = signal["provenance"]["url"]
        assert url.startswith("https://"), f"{signal_id} carries no real citation"
        assert "example.invalid" not in url


def test_every_signal_is_bound_to_the_component_it_evidences(overlay: Overlay, org: str) -> None:
    _, component = ORGS[org]
    assert len(overlay.claims) == 2
    for claim in overlay.claims.values():
        assert claim["component"] == component
        assert claim["signal"] in overlay.signals
        assert claim["evidence_grade"] == 1


def test_the_commit_history_is_monotonically_dated(repo_dir: Path) -> None:
    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(repo_dir),
        stdout=subprocess.PIPE, check=True,
    )
    dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    assert dates == sorted(dates), "a commit is dated behind an earlier one"


def test_the_world_layer_names_no_tenant(repo_dir: Path) -> None:
    assert check_direction(ModelRepo.open(repo_dir)) == []


def test_no_outcome_is_authored(overlay: Overlay) -> None:
    """Decision ticket 01: a portfolio org does not carry the backtest burden. Structural, not
    prose — an outcome appearing here would silently promote this org into the answer-key suite."""
    assert overlay.outcomes == {}


def test_a_run_succeeds_and_reproduces_from_its_own_pins(tmp_path: Path, repo_dir: Path, org: str) -> None:
    bundle = tmp_path / "bundle.json"
    assert main([
        "run", "--repo", str(repo_dir), "--org", org, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(bundle),
    ]) == 0
    report = reproduce(repo_dir, bundle)
    assert report.reproduces, report.diff


def test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences(
    repo_dir: Path, org: str, overlay: Overlay
) -> None:
    """Same discipline every answer-key fixture carries (build ticket 38 onward): the binding
    exists in history as of the date the signal does, so a rewind before it sees neither."""
    earliest = min(overlay.signals.values(), key=lambda s: str(s["date"]))["date"]
    day_before = (datetime.date.fromisoformat(earliest) - datetime.timedelta(days=1)).isoformat()
    repo = ModelRepo.open_at_time(repo_dir, day_before)
    before = Overlay.load(repo, org)
    assert before.signals == {}, "a rewind before the first signal still sees it"
