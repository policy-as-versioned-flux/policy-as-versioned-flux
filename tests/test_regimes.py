"""The three information regimes and the gate that makes `as-consumed` mean something.

Build ticket 36. Seam 1 wherever a claim is about an emitted artefact, seam 2 where the claim is
numerical or structural — the gap arithmetic and the absence of a default are properties of the
model API, and asserting them through the CLI would only test argparse.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, verbs
from twin.cli import main
from twin.model import Overlay
from twin.regimes import (
    AS_CONSUMED, AS_KNOWABLE, WITH_HINDSIGHT, RegimeError, cutoff, require,
)
from twin.repo import ModelRepo
from twin.schema import REGIMES, SchemaError, validate

SCENARIO = "did-it-land-2011"


@pytest.fixture(scope="session")
def regime_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_regime_org(tmp_path_factory.mktemp("regime") / "repo")


@pytest.fixture(scope="session")
def planted_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_regime_org(tmp_path_factory.mktemp("planted") / "repo", planted=True)


def _run(repo_dir: Path, caps, regime: str, org: str = fixtures.REGIME_ORG, scenario: str = SCENARIO):
    return json.loads(
        verbs.run(
            ModelRepo.open(repo_dir), caps, org, scenario, regime,
            verbs.command_for("run", org=org, scenario=scenario, regime=regime),
        ).to_bytes()
    )["body"]


# -- AC 1: a required parameter with no default ---------------------------------------------


def test_an_execution_with_no_regime_is_refused_rather_than_defaulted(model_repo_dir: Path, caps) -> None:
    """The regime a default would pick is the one whose forecasts score."""
    with pytest.raises(RegimeError, match="there is no default"):
        verbs.run(ModelRepo.open(model_repo_dir), caps, "netflix", "dvd-decline-2011", None, ["twin", "run"])


@pytest.mark.parametrize("bad", ["", "   ", "as-consumed-ish", "AS-CONSUMED"])
def test_only_the_three_named_regimes_are_accepted(bad: str) -> None:
    with pytest.raises(RegimeError):
        require(bad)


@pytest.mark.parametrize("bad", ["20110712", "2011-07-12T09:00:00+00:00", "2011-7-12", "yesterday"])
def test_a_cutoff_that_is_not_a_plain_day_is_refused(bad: str) -> None:
    """The filter compares dates as text, so a cutoff in another shape compares wrong.

    `'2011-09-01' > '20110712'` is `False`, and `datetime.fromisoformat` accepts the basic form —
    so the rewind's own parser is no guard. Refused rather than coerced, because truncating an
    instant to its day would answer a question about a moment with an answer about a day.
    """
    with pytest.raises(RegimeError, match="YYYY-MM-DD"):
        cutoff(bad)


def test_a_run_at_a_malformed_execution_time_is_refused_rather_than_leaky(
    planted_repo_dir: Path, caps
) -> None:
    """The live path to the defect: `--at` is the one execution time nothing else validates."""
    with pytest.raises(RegimeError, match="YYYY-MM-DD"):
        verbs.run(
            ModelRepo.open(planted_repo_dir), caps, fixtures.REGIME_ORG, SCENARIO, AS_CONSUMED,
            ["twin", "run"], at="20110712",
        )


def test_a_scenario_cannot_declare_its_own_regime(model_repo_dir: Path) -> None:
    """An authored regime is a default wearing a different hat.

    The closed schema is what makes this structural rather than a convention: there is no slot,
    so an execution that omitted the flag has nothing to silently inherit.
    """
    with pytest.raises(SchemaError):
        validate(
            "scenario",
            {"id": "planted", "question": "q", "proposition": "p", "at": "2011-07-12",
             "components": ["c"], "world_models": ["m"], "regime": AS_CONSUMED},
            "planted",
        )


def test_the_cli_refuses_a_run_with_no_regime(model_repo_dir: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exit_code:
        main(["run", "--repo", str(model_repo_dir), "--org", "netflix",
              "--scenario", "dvd-decline-2011", "--out", str(tmp_path / "nope.json")])
    assert exit_code.value.code == 2
    assert not (tmp_path / "nope.json").exists()


# -- AC 2: the gate is absence, not screening ------------------------------------------------


def test_a_post_T_fact_is_absent_from_the_model_an_as_consumed_run_reads(
    regime_repo_dir: Path, caps
) -> None:
    """Absence rather than a flag: there is no post-T fact available to reference."""
    body = _run(regime_repo_dir, caps, AS_CONSUMED)
    gate = body["regime"]["gate"]
    assert body["regime"]["gated"] is True and body["regime"]["scoring_eligible"] is True
    assert gate["admitted"] == {"outcomes": [], "signals": ["known-early"]}
    assert [w["id"] for w in gate["withheld"]] == []  # removed by the rewind, before any filter


def test_the_looser_regimes_admit_strictly_more(regime_repo_dir: Path, caps) -> None:
    admitted = {}
    for regime in REGIMES:
        gate = _run(regime_repo_dir, caps, regime)["regime"]["gate"]
        admitted[regime] = {f"{c}/{i}" for c, ids in gate["admitted"].items() for i in ids}
    assert admitted[AS_CONSUMED] < admitted[AS_KNOWABLE] < admitted[WITH_HINDSIGHT]


def test_a_date_filtered_fact_is_named_and_dated_rather_than_counted(regime_repo_dir: Path, caps) -> None:
    """`as-knowable` withholds by date, and says which fact and when it was dated."""
    withheld = _run(regime_repo_dir, caps, AS_KNOWABLE)["regime"]["gate"]["withheld"]
    assert {w["id"]: w["dated"] for w in withheld} == {
        "after-the-fact": "2011-09-01",
        "did-it-land-resolved": "2012-12-31",
    }


def test_a_claim_goes_with_the_signal_it_binds(planted_repo_dir: Path, caps) -> None:
    """A reading of a document the twin did not have is not a claim the twin held."""
    gate = _run(planted_repo_dir, caps, AS_KNOWABLE)["regime"]["gate"]
    assert gate["claims_withheld_with_their_signal"] == ["bind-planted-to-catalogue"]


# -- AC 3: a planted post-T fact fails the run ----------------------------------------------


def test_a_post_T_fact_committed_before_T_refuses_an_as_consumed_run(planted_repo_dir: Path, caps) -> None:
    """The one shape the rewind cannot remove, so it is the shape that proves the date filter."""
    with pytest.raises(RegimeError, match="planted-post-t"):
        _run(planted_repo_dir, caps, AS_CONSUMED)


def test_the_same_plant_runs_under_the_looser_regimes(planted_repo_dir: Path, caps) -> None:
    """It is the regime that refuses, not the repository — otherwise this is a broken fixture."""
    for regime in (AS_KNOWABLE, WITH_HINDSIGHT):
        assert _run(planted_repo_dir, caps, regime)["forecasts"]


def test_a_post_T_fact_bound_to_nothing_the_scenario_forecasts_does_not_refuse(
    model_repo_dir: Path, caps
) -> None:
    """The answer key is dated after T by definition, and it is not the subject being forecast.

    Refusing on its presence would make a backtest impossible in any repository that also holds
    the key it will later be scored against.
    """
    body = _run(model_repo_dir, caps, AS_CONSUMED, org="netflix", scenario="dvd-decline-2011")
    assert [w["id"] for w in body["regime"]["gate"]["withheld"]] == ["dvd-decline-2011-resolved"]
    assert body["forecasts"]


# -- AC 4: the three-way gap, computed ------------------------------------------------------


def test_the_two_gaps_are_computed_and_localised(regime_repo_dir: Path, caps, tmp_path: Path) -> None:
    artefact = verbs.regime_gap(
        ModelRepo.open(regime_repo_dir), caps, fixtures.REGIME_ORG, SCENARIO,
        verbs.command_for("regimes", org=fixtures.REGIME_ORG, scenario=SCENARIO),
    )
    localisation = json.loads(artefact.to_bytes())["body"]["localisation"]

    assert localisation["admitted_counts"] == {AS_CONSUMED: 1, AS_KNOWABLE: 2, WITH_HINDSIGHT: 4}
    by_kind = {g["localises"]: g for g in localisation["gaps"]}
    assert by_kind["sensing"]["facts"] == ["signals/known-late"]
    assert by_kind["interpretation"]["facts"] == [
        "outcomes/did-it-land-resolved", "signals/after-the-fact"
    ]
    # The third comparison is refused rather than reported as zero: nothing infers a probability
    # from a fact yet, so a computed residual would read as "the model is fine".
    assert localisation["model_residual"]["computed"] is False


def test_the_gap_artefact_reproduces_from_its_own_pins(regime_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "regime-gap.json"
    assert main(["regimes", "--repo", str(regime_repo_dir), "--org", fixtures.REGIME_ORG,
                 "--scenario", SCENARIO, "--out", str(out)]) == 0

    from twin.reproduce import reproduce

    report = reproduce(regime_repo_dir, out)
    assert report.reproduces, report.as_dict()


# -- the named limits, asserted rather than described ----------------------------------------


def test_an_unavailable_ingestion_history_is_reported_not_skipped(model_repo_dir: Path, caps) -> None:
    """The netflix subject is dated 2011 and its repository was built this year.

    The date filter still applies; the history filter cannot, and `as-consumed` is genuinely
    weaker here. An artefact that stayed quiet about that would claim an ingestion history it
    never had.
    """
    history = _run(model_repo_dir, caps, AS_CONSUMED, org="netflix", scenario="dvd-decline-2011")[
        "regime"
    ]["gate"]["ingestion_history"]
    assert history["available"] is False
    assert "no commit at or before" in history["reason"]


def test_the_gate_carries_no_machine_varying_fact(model_repo_dir: Path, caps) -> None:
    """A path on disk in the artefact would break identical bytes on the next machine."""
    body = _run(model_repo_dir, caps, AS_CONSUMED, org="netflix", scenario="dvd-decline-2011")
    assert str(model_repo_dir) not in json.dumps(body)


def test_a_scenario_authored_after_T_did_not_exist_then(regime_repo_dir: Path, caps) -> None:
    """The rewind is a model state, so a question nobody had asked yet is an answer."""
    with pytest.raises(verbs.VerbError, match="was authored later"):
        verbs.run(
            ModelRepo.open(regime_repo_dir), caps, fixtures.REGIME_ORG, SCENARIO,
            AS_CONSUMED, ["twin", "run"], at="2011-06-15",
        )


def test_the_ungated_overlay_still_holds_everything(regime_repo_dir: Path) -> None:
    """The gate is applied where the model is read, not by deleting facts from the repository."""
    overlay = Overlay.load(ModelRepo.open(regime_repo_dir), fixtures.REGIME_ORG)
    assert set(overlay.signals) == {"known-early", "known-late", "after-the-fact"}
    assert set(overlay.outcomes) == {"did-it-land-resolved"}
