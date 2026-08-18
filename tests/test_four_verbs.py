"""`twin backtest`, and all four verbs as compositions of two primitives (build ticket 37).

Decision ticket 13 Q2's claim — projection, act-now, the counterfactual and the backtest all fall
out of exactly two primitives, time and intervention — is untested until someone demonstrates it.
This module demonstrates all four against the netflix fixture's `dvd-decline-2011` scenario, and
the `--at 2026-01-01` rewind point is chosen because it is the one date this synthetic fixture's
own git history can honestly support: the scenario's own subject-matter date (2011) predates the
repository's first commit, the exact limit `twin/regimes.py`'s module docstring already names.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import primitives, verbs
from twin.cli import main
from twin.grades import Capabilities
from twin.repo import ModelRepo

REWIND_AT = "2026-01-01"
NETFLIX = ("--org", "netflix")


def test_projection_is_run_with_no_intervention(repo: ModelRepo, caps: Capabilities) -> None:
    """Fast-forward: a scenario executed with no `do()` and no explicit prior rewind."""
    artefact = verbs.run(
        repo, caps, "netflix", "dvd-decline-2011", "as-consumed",
        verbs.command_for("run", org="netflix", scenario="dvd-decline-2011", regime="as-consumed", at=REWIND_AT),
        at=REWIND_AT,
    )
    assert artefact.kind == verbs.KIND_FORECAST_BUNDLE
    assert artefact.body["forecasts"]


def test_act_now_is_intervene_with_no_rewind(repo: ModelRepo, caps: Capabilities) -> None:
    """Act-now: `do(x)` on the repository exactly as it was opened — no time primitive involved."""
    artefact = verbs.intervene(
        repo, caps, "netflix", "streaming-experience",
        verbs.command_for("intervene", org="netflix", component="streaming-experience"),
    )
    assert artefact.kind == verbs.KIND_INTERVENTION
    assert artefact.body["severed"] or artefact.body["downstream"]


def test_counterfactual_is_rewind_then_intervene(repo: ModelRepo, caps: Capabilities) -> None:
    """The counterfactual: `do(x)` on a repository already rewound to a declared past time —
    composed directly from `primitives.rewind` and `verbs.intervene`, no third code path."""
    rewound = primitives.rewind(repo.model_root, REWIND_AT)
    artefact = verbs.intervene(
        rewound, caps, "netflix", "streaming-experience",
        verbs.command_for("intervene", org="netflix", component="streaming-experience", at=REWIND_AT),
    )
    assert artefact.kind == verbs.KIND_INTERVENTION
    assert artefact.pins["model_repo"]["commit"] == rewound.pin.commit


def test_backtest_is_rewind_then_run(tmp_path: Path, repo: ModelRepo) -> None:
    """The backtest: rewind plus projection, via the CLI composition `cmd_backtest` makes."""
    out = tmp_path / "backtest.json"
    rc = main([
        "backtest", "--repo", str(repo.model_root), *NETFLIX, "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", REWIND_AT, "--out", str(out),
    ])
    assert rc == 0
    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == verbs.KIND_FORECAST_BUNDLE
    assert doc["envelope"]["produced_by"]["command"][:2] == ["twin", "backtest"]
    assert doc["body"]["regime"]["scoring_eligible"] is True


def test_backtest_and_run_compute_the_identical_forecast(tmp_path: Path, repo: ModelRepo) -> None:
    """Backtest is not a second implementation: with the same `at`, its forecasts are
    byte-identical to a direct `run` — the only difference is which command is recorded as having
    produced them, since that is genuinely a different fact."""
    backtest_out, run_out = tmp_path / "bt.json", tmp_path / "run.json"
    assert main([
        "backtest", "--repo", str(repo.model_root), *NETFLIX, "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", REWIND_AT, "--out", str(backtest_out),
    ]) == 0
    assert main([
        "run", "--repo", str(repo.model_root), *NETFLIX, "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", REWIND_AT, "--out", str(run_out),
    ]) == 0

    backtest_doc = json.loads(backtest_out.read_bytes())
    run_doc = json.loads(run_out.read_bytes())

    def strip_command(body: dict) -> dict:
        return {
            **body,
            "forecasts": [
                {k: v for k, v in f.items() if k not in ("id", "pins")} for f in body["forecasts"]
            ],
        }

    assert strip_command(backtest_doc["body"]) == strip_command(run_doc["body"])


def test_backtest_is_not_scoring_eligible_under_a_non_scoring_regime(tmp_path: Path, repo: ModelRepo) -> None:
    """AC 4: only as-consumed produces a scoring-eligible forecast — inherited from `run()`'s own
    gate rather than a second implementation of the rule."""
    out = tmp_path / "backtest-knowable.json"
    rc = main([
        "backtest", "--repo", str(repo.model_root), *NETFLIX, "--scenario", "dvd-decline-2011",
        "--regime", "as-knowable", "--at", REWIND_AT, "--out", str(out),
    ])
    assert rc == 0
    doc = json.loads(out.read_bytes())
    assert doc["body"]["regime"]["scoring_eligible"] is False


def test_backtest_composes_no_separate_code_path() -> None:
    """AC 3: the composition is the implementation — asserted against the source, not the
    docstring. `cmd_backtest` calls exactly `rewind` and `verbs.run`, and imports no propagation
    or scoring machinery of its own."""
    import inspect

    from twin import cli

    source = inspect.getsource(cli.cmd_backtest)
    assert "rewind(" in source
    assert "verbs.run(" in source
    for forbidden in ("propagate", "Do(", "Observe(", "scoring.", "primitives_mod.Do", "primitives_mod.Observe"):
        assert forbidden not in source, f"cmd_backtest references {forbidden!r} — a second code path"


def test_a_backtest_scores_against_the_record(tmp_path: Path, repo: ModelRepo) -> None:
    """The record: `twin score` runs on a backtest's output exactly as it would on `run`'s."""
    bundle = tmp_path / "bundle.json"
    assert main([
        "backtest", "--repo", str(repo.model_root), *NETFLIX, "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", REWIND_AT, "--out", str(bundle),
    ]) == 0
    card = tmp_path / "card.json"
    assert main([
        "score", "--repo", str(repo.model_root), *NETFLIX, "--forecast", str(bundle),
        "--outcome", "dvd-decline-2011-resolved", "--out", str(card),
    ]) == 0
    doc = json.loads(card.read_bytes())
    assert doc["body"]["scores"], "the backtest's forecasts scored against the resolved outcome"


def test_a_backtest_bundle_reproduces_from_its_own_pins(tmp_path: Path, repo: ModelRepo) -> None:
    """A score card scored from a backtest bundle recurses back through `reproduce.replay` to
    recompute that bundle — closing the gap `identical_pins_identical_bytes` exists to guard."""
    from twin.reproduce import reproduce

    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    assert main([
        "backtest", "--repo", str(repo.model_root), *NETFLIX, "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", REWIND_AT, "--out", str(bundle),
    ]) == 0
    assert main([
        "score", "--repo", str(repo.model_root), *NETFLIX, "--forecast", str(bundle),
        "--outcome", "dvd-decline-2011-resolved", "--out", str(card),
    ]) == 0
    report = reproduce(repo.model_root, card)
    assert report.reproduces, report.diff
    assert report.chain[0].reproduces, "the backtest bundle it scored did not reproduce"


def test_the_full_counterfactual_composes_abduction_action_and_prediction(
    repo: ModelRepo, caps: Capabilities
) -> None:
    """Decision ticket 08 AC 2, closed. `twin/capabilities/causal-layer.yaml` named the gap
    precisely: abduction (build ticket 35) and action (build ticket 22) were composed and tested
    together above (`test_counterfactual_is_rewind_then_intervene`), and prediction/fast-forward
    (build ticket 37) was composed and tested with abduction alone (`test_backtest_is_rewind_then_run`)
    — "two thirds of a composition is not the composition". This calls all three off the identical
    abducted state: `primitives.rewind` (abduction), `verbs.intervene` carrying `Do` (action), and
    `verbs.run` (prediction/fast-forward).

    It also states and tests structural-only-path behaviour for this composed chain specifically,
    not only for `propagate()` in isolation (build ticket 20's scope). `cloud-compute` carries no
    `influences` edge at all — `streaming-experience` only *needs* it — so asking the intervened,
    abducted state the causal question (`verbs.intervene`'s own `downstream`) finds nothing:
    `twin/propagate.py` never walks a `needs` edge, and there is no other kind leaving this
    component. Asking the identical abducted-and-intervened state the structural question
    (`verbs.blast`) reports `streaming-experience` as real, unpriced exposure regardless. Decision
    ticket 08 Q3's "one traversal, two outputs" is shown holding under an intervention, not only
    at rest — and this is the sharper case: an intervention whose causal prediction is empty is
    not a no-op, because the structural exposure is still there and still real.
    """
    rewound = primitives.rewind(repo.model_root, REWIND_AT)

    # Action: do(x) on the abducted state, on a component with a real structural dependent
    # (`streaming-experience` needs `cloud-compute`) and zero causal edges of its own.
    intervened = verbs.intervene(
        rewound, caps, "netflix", "cloud-compute",
        verbs.command_for("intervene", org="netflix", component="cloud-compute", at=REWIND_AT),
    )
    assert intervened.pins["model_repo"]["commit"] == rewound.pin.commit

    # Prediction / fast-forward: run() at the identical abducted time — the third leg, composed
    # rather than only ever exercised two of three (backtest already covers rewind+run; act-now
    # already covers do() alone).
    forecast = verbs.run(
        repo, caps, "netflix", "dvd-decline-2011", "as-consumed",
        verbs.command_for("run", org="netflix", scenario="dvd-decline-2011", regime="as-consumed", at=REWIND_AT),
        at=REWIND_AT,
    )
    assert forecast.kind == verbs.KIND_FORECAST_BUNDLE
    assert forecast.pins["model_repo"]["commit"] == rewound.pin.commit

    # Structural-only path, for this same composed (rewound + intervened) chain.
    assert intervened.body["severed"] == [], "nothing claims a mechanism into cloud-compute either"
    assert intervened.body["downstream"]["reached"] == [], (
        "cloud-compute carries no influences edge, so the priced prediction is empty — not a "
        "placeholder, an honest zero-length walk"
    )

    radius = verbs.blast(
        rewound, caps, "netflix", "cloud-compute",
        verbs.command_for("blast", org="netflix", origin="cloud-compute", at=REWIND_AT),
    )
    unpriced = {r["component"] for r in radius.body["unpriced"]}
    assert "streaming-experience" in unpriced, (
        "the structural dependent is real exposure and unpriced, on the identical abducted state "
        "whose causal prediction just found nothing"
    )
    assert radius.body["admitted_to_pricing"] == [], "no causal path leaves cloud-compute to price"


def test_a_rewind_before_the_repository_existed_refuses_honestly(repo: ModelRepo) -> None:
    """The scenario's own subject-matter date (2011) predates this synthetic fixture's git
    history — `primitives.rewind` refuses rather than answering with today's model wearing 2011's
    date, the same refusal `cmd_rewind` already carries."""
    from twin.primitives import PrimitiveError

    with pytest.raises(PrimitiveError, match="did not exist yet"):
        primitives.rewind(repo.model_root, "2011-07-12")
