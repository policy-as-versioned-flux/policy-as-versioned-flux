"""The falsifiability beat, run and scored (build ticket 72; decision ticket 22; stories 90, 93).

Build ticket 71 authored the Royal Mail answer key. This runs it: rewind under `as-consumed`,
project, score against the key with the contamination discount applied, and show the three-regime
gap beside it.

The result is red. The one world model this key carries is the market consensus at flotation,
which put the shortfall at 0.05, and the shortfall happened — brier 0.9025, worse than a coin
flip. A demo whose thesis is *"we can prove when we're wrong"* cannot be embarrassed by that, so
these tests assert the red result **survives to the surface** rather than asserting it is small.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from twin import fixtures
from twin.artefact import Artefact
from twin.cli import _say_score, main
from twin.grades import STUB, Capabilities

ORG = fixtures.ROYAL_MAIL_ORG
SCENARIO = "would-the-twin-have-flagged-it"
KEY = "royal-mail-concedes-the-automation-shortfall-2019"
AT = "2018-06-01"

BEAT = Path(__file__).resolve().parents[1] / "twin" / "beat-royal-mail.sh"


@pytest.fixture(scope="session")
def beat(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """The beat's own artefacts, produced through the CLI exactly as the script produces them.

    Session-scoped: three fixture repositories and six commands, built once. The script itself is
    run by CI rather than by pytest, for the same reason `twin/demo.sh` is — a shell surface is
    checked by running it, and running it twice per suite buys nothing.
    """
    work = tmp_path_factory.mktemp("beat")
    repos = {name: fixtures.BUILDERS[name](work / name) for name in (ORG, "carillion", "enron")}
    out = work / "artefacts"

    bundle = out / "forecast-bundle.json"
    assert main([
        "backtest", "--repo", str(repos[ORG]), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", AT, "--out", str(bundle),
    ]) == 0

    legs = {}
    for name, outcome in (("carillion", "carillion-collapse-resolved"), ("enron", "enron-bankruptcy-resolved")):
        leg_bundle, leg_card = out / f"{name}-bundle.json", out / f"{name}-card.json"
        assert main([
            "run", "--repo", str(repos[name]), "--org", name, "--scenario", SCENARIO,
            "--regime", "as-consumed", "--out", str(leg_bundle),
        ]) == 0
        assert main([
            "score", "--repo", str(repos[name]), "--org", name, "--forecast", str(leg_bundle),
            "--outcome", outcome, "--out", str(leg_card),
        ]) == 0
        legs[name] = leg_card

    card = out / "score-card.json"
    assert main([
        "score", "--repo", str(repos[ORG]), "--org", ORG, "--forecast", str(bundle),
        "--outcome", KEY, "--discount-enron", str(legs["enron"]),
        "--discount-obscure", str(legs["carillion"]), "--out", str(card),
    ]) == 0

    gap = out / "regime-gap.json"
    assert main([
        "regimes", "--repo", str(repos[ORG]), "--org", ORG, "--scenario", SCENARIO,
        "--at", AT, "--out", str(gap),
    ]) == 0

    return {"repo": repos[ORG], "bundle": bundle, "card": card, "gap": gap}


def _body(path: Path) -> dict:
    return json.loads(path.read_bytes())["body"]


def test_the_beat_rewinds_under_as_consumed_before_it_projects(beat: dict[str, Path]) -> None:
    """AC 1, the rewind half: the projection reads the repository as it stood at T, not today.

    The pinned commit is the FY2017-18 results commit — the last one dated on or before
    2018-06-01 — so the October profit warning and the answer key itself are both absent from the
    tree this forecast was computed against, rather than present and filtered afterwards.
    """
    body = _body(beat["bundle"])
    assert body["regime"]["declared"] == "as-consumed"
    assert body["regime"]["scoring_eligible"] is True
    committed = body["regime"]["gate"]["ingestion_history"]["committed"]
    assert committed[:10] <= AT, f"the rewind pinned a commit dated {committed}, after {AT}"
    assert all(f["regime"] == "as-consumed" for f in body["forecasts"])


def test_the_beat_scores_against_the_key_with_the_discount_applied(beat: dict[str, Path]) -> None:
    """AC 1, the scoring half: scored against the resolved key, and the memorisation-leakage
    discount is a measurement carried into the card rather than an absent field."""
    body = _body(beat["card"])
    assert body["answer_key"]["id"] == KEY
    assert body["answer_key"]["observed"] is True
    assert body["answer_key"]["contamination"] == "low"

    discount = body["contamination_discount"]
    assert discount is not None, "the beat scored with no contamination discount"
    assert [leg["leg"] for leg in discount["legs"]] == ["enron-vs-obscure"]
    # That the adjustment is additive and leaves the raw figure standing is build ticket 40's own
    # AC, asserted against the arithmetic in tests/test_enron.py. Not restated here.
    for entry in body["scores"]:
        assert entry["discount"] == discount["discount"]


def test_the_score_lands_poor_and_says_so(beat: dict[str, Path]) -> None:
    """AC 2: the result is worse than a coin flip and is reported, not softened.

    Asserted on the *worst* score rather than on a fixed number, so adding a world model that
    reads the signals — the ensemble this key does not yet carry — leaves this passing.
    """
    scores = _body(beat["card"])["scores"]
    worst = max(scores, key=lambda s: float(s["brier"]))
    assert float(worst["brier"]) > 0.25, "the beat's red result has been tuned away"
    assert float(worst["adjusted_brier"]) > 0.25, "the discount rescued a forecast it should not"


def test_the_poor_score_is_printed_first_rather_than_buried() -> None:
    """AC 2: `lower-is-better`, so the surface prints descending — the bad news is the first row.

    Built from a two-score card rather than the beat's own single-forecast one: ordering cannot be
    demonstrated on a list of one, and the property under test is the surface's, not the key's.
    """
    card = Artefact(
        kind="score-card", mark="derived", command=["twin", "score"], pins={}, depth={"grade": STUB},
        body={
            "answer_key": {"id": "k", "observed": True, "resolved_on": "2019-05-23", "contamination": "low"},
            "contamination_discount": None,
            "rules": ["brier", "log_loss"],
            "orientation": "lower-is-better",
            "scores": [
                {"world_model": "the-good-one", "probability": 0.9, "brier": 0.01,
                 "log_loss": 0.105, "regime": "as-consumed"},
                {"world_model": "the-bad-one", "probability": 0.05, "brier": 0.9025,
                 "log_loss": 2.99, "regime": "as-consumed"},
            ],
            "unscoreable": [],
        },
    )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        _say_score(card)
    out = printed.getvalue()
    assert out.index("the-bad-one") < out.index("the-good-one"), "the poor score was printed last"


def test_the_three_regime_gap_localises_a_failure(beat: dict[str, Path]) -> None:
    """AC 3: the two gaps are computed and each is labelled with what it would localise to.

    The interpretation gap is the honest one here: the profit warning and the answer key are both
    dated after T, so reading them as foreseeable at T would be hindsight. The sensing gap is
    empty, which is the correct answer for a fixture whose claims land in the same commit as the
    signals they bind — everything knowable had been ingested.
    """
    localisation = _body(beat["gap"])["localisation"]
    assert localisation["admitted_counts"]["as-consumed"] == localisation["admitted_counts"]["as-knowable"]
    assert localisation["admitted_counts"]["with-hindsight"] > localisation["admitted_counts"]["as-knowable"]

    gaps = {entry["localises"]: entry for entry in localisation["gaps"]}
    assert set(gaps) == {"sensing", "interpretation"}
    assert gaps["sensing"]["facts"] == []
    assert "outcomes/" + KEY in gaps["interpretation"]["facts"]

    # The model residual is declined with a stated reason rather than reported as a zero — a zero
    # would read as "the model is fine" when what it means is "nothing here consumes a signal".
    assert localisation["model_residual"]["why"]


def test_every_artefact_the_beat_emits_carries_computed_depth_grades(
    beat: dict[str, Path], caps: Capabilities
) -> None:
    """AC 4: displayed automatically, from the envelope, on every artefact — no hand labelling.

    Compared against the grade `Capabilities.load()` computes from the decision tickets, not
    merely checked for shape: a grade written into an envelope by hand would satisfy any
    shape check and is exactly the failure depth grades exist to prevent.
    """
    for name in ("bundle", "card", "gap"):
        depth = json.loads(beat[name].read_bytes())["envelope"]["depth"]
        assert depth["capabilities"], f"the {name} artefact names no producing capability"
        for capability, summary in depth["capabilities"].items():
            assert summary == caps.require(capability).summary(), (
                f"the {name} artefact carries a depth grade for {capability} that the checklist "
                "does not compute"
            )
        assert depth["grade"] == min(
            (s["grade"] for s in depth["capabilities"].values()),
            key=["stub", "partial", "full"].index,
        ), f"the {name} artefact's overall grade is not the worst of its capabilities"


def test_the_demo_slice_grade_is_computed_from_decision_ticket_22(caps: Capabilities) -> None:
    """AC 6: the beat's own depth grade is a computed checklist, and it opens at `stub`.

    Decision ticket 22 had no capability file before this ticket. Nothing is ticked because
    nothing honestly is: three of the four beats do not exist, and build ticket 77 owns the other
    three criteria. `full` is derived from the checklist, so it cannot be typed here at all —
    `tests/test_grades.py` proves the refusal.
    """
    graded = caps.require("demo-slice")
    assert graded.owning_ticket == "22"
    assert graded.grade == STUB
    # The criterion *text* is not restated here: `Capabilities.load()` already refuses a checklist
    # that has drifted from its decision ticket (twin/grades.py `_validate_against_ticket`, proved
    # in tests/test_grades.py), so a copy of the four strings could never fail on its own.
    assert len(graded.criteria) == 4


def test_the_beat_script_is_executable() -> None:
    """CI runs `bash twin/beat-royal-mail.sh` end to end, which is the real check on its steps.
    This is only the bit CI cannot catch by running it through `bash`."""
    assert BEAT.stat().st_mode & 0o111, "the beat script is not executable"
