"""The whole-engine beat (build ticket 74; decision ticket 22; spec stories 91, 93).

Build ticket 73 built the Netflix spine and the substrate against it. This runs the engine on it:
a threat path and an opportunity path from one dated state, a non-technical lever priced against
a technical control, and a trade-off curve where the rival causal accounts disagree about which
response is cheapest.

**No score here, and that is the design.** This org carries no answer key: Netflix's story is
famous enough that a twin "anticipating" 2011 cannot be told apart from reciting it, so the
falsifiability beat is Royal Mail's and lands red there. These tests assert the absence rather
than working around it.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from twin import fixtures
from twin.cli import main
from twin.grades import Capabilities
from twin.model import Overlay
from twin.primitives import rewind
from twin.repo import ModelRepo

ORG = fixtures.NETFLIX_ORG
SCENARIO = "would-the-twin-have-flagged-it"
PERSPECTIVE = "the-operator"
ORIGIN = "dvd-by-mail"
LEVER = "hold-the-bundled-price-for-one-quarter"
CONTROL = "ship-one-bill-and-one-sign-in-across-the-two-plans"
AT = "2011-08-01"
ACCOUNTS = (
    "the-shock-stayed-on-the-dvd-side",
    "the-shock-crossed-to-the-streaming-side",
    "the-damage-was-mostly-the-rebrand",
)

BEAT = Path(__file__).resolve().parents[1] / "twin" / "beat-netflix.sh"


@pytest.fixture(scope="session")
def caps() -> Capabilities:
    return Capabilities.load()


RECIPE_PATH = Path(__file__).resolve().parents[1] / "twin" / "netflix-substrate-recipe.yaml"
CHECKPOINT = "2011-10-24"


@pytest.fixture(scope="session")
def beat(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """The beat's own artefacts, produced through the CLI exactly as the script produces them.

    Session-scoped: one fixture repository and eight commands, built once. The script itself is
    run by CI rather than by pytest, for the same reason `twin/demo.sh` and
    `twin/beat-royal-mail.sh` are — a shell surface is checked by running it, and running it twice
    per suite buys nothing.
    """
    work = tmp_path_factory.mktemp("netflix-beat")
    repo = fixtures.build_netflix_org(work / "repo")
    out = work / "artefacts"

    paths = {
        name: out / f"{name}.json"
        for name in ("bundle", "rewind", "sweep", "options", "price", "curve", "proposal",
                     "substrate")
    }
    assert main([
        "backtest", "--repo", str(repo), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--at", AT, "--out", str(paths["bundle"]),
    ]) == 0
    assert main([
        "rewind", "--repo", str(repo), "--org", ORG, "--at", AT, "--out", str(paths["rewind"]),
    ]) == 0
    resolved = json.loads(paths["rewind"].read_bytes())["body"]["resolved"]["commit"]
    assert main([
        "gameplay-sweep", "--repo", str(repo), "--ref", resolved, "--out", str(paths["sweep"]),
    ]) == 0
    assert main([
        "options", "--repo", str(repo), "--org", ORG, "--perspective", PERSPECTIVE,
        "--out", str(paths["options"]),
    ]) == 0
    assert main([
        "price", "--repo", str(repo), "--org", ORG, "--origin", ORIGIN, "--out", str(paths["price"]),
    ]) == 0
    accounts = [arg for account in ACCOUNTS for arg in ("--account", account)]
    assert main([
        "trade-off", "--repo", str(repo), "--org", ORG, "--origin", ORIGIN,
        "--perspective", PERSPECTIVE, *accounts, "--out", str(paths["curve"]),
    ]) == 0
    assert main([
        "propose", "--repo", str(repo), "--org", ORG, "--response", LEVER,
        "--channel", "record", "--out", str(paths["proposal"]),
    ]) == 0
    assert main([
        "substrate", "--repo", str(repo), "--org", ORG, "--recipe", str(RECIPE_PATH),
        "--checkpoint", CHECKPOINT, "--out", str(paths["substrate"]),
    ]) == 0

    return {"repo": repo, "resolved": resolved, **paths}


def _body(path: Path) -> dict:
    return json.loads(Path(path).read_bytes())["body"]


# -- AC 1: a threat path and an opportunity path, both on dated evidence -------------------------


def test_both_paths_run_from_the_one_state_the_rewind_resolved(beat: dict[str, Path]) -> None:
    """The two directions share a date, and they share the commit that date resolved to.

    Asserted on the pins rather than on the `--at` string: two different answers to "what did the
    model look like on the day" would make fear and seize incomparable, which is the whole reason
    for running them at one date, and only the pins can catch that.
    """
    threat = _body(beat["bundle"])
    assert len(threat["forecasts"]) >= 2, "no ensemble to spread across on the threat side"
    # Length alone passes on three identical probabilities — a real ensemble disagrees.
    distinct = {f["probability"] for f in threat["forecasts"]}
    assert len(distinct) >= 2, f"all {len(threat['forecasts'])} forecasts agree: {distinct}"

    sweep = json.loads(beat["sweep"].read_bytes())
    assert sweep["envelope"]["pins"]["repos"][0]["commit"] == beat["resolved"]
    assert sweep["body"]["opportunities"], "the opportunity side pulled nothing"


def test_opportunities_are_pulled_and_signals_are_pushed_side_by_side(beat: dict[str, Path]) -> None:
    """Decision ticket 13 Q3's counterweight, measurable on a real subject rather than claimed.

    A threat announces itself when a filing lands; nothing arrives to say a component is about to
    commoditise, so the sweep has to go looking. Both volumes sit in the same artefact so a reader
    does not have to subtract two files.
    """
    counts = _body(beat["sweep"])["counts"]
    assert counts["opportunities"] >= 1
    # Pins build ticket 73's own spine dates: three of the six filings are dated on or before
    # 2011-08-01 (`tests/test_netflix.py` asserts the six dates directly). Exact rather than
    # `>= 1`, because a filing quietly moving across the AT boundary should fail a test somewhere,
    # and this is the one number in this file that would catch it.
    assert counts["signals"] == 3


def test_the_dated_state_carries_no_layer_that_postdates_it(beat: dict[str, Path]) -> None:
    """The cut is mechanical, not narrated.

    The causal edge and the perspective both rest on the Q4 2011 letter, filed 2012-01-25 — the
    first one to report the two domestic segments separately, which is what supplies a valuation
    and the after-side of a grade-1 claim. Neither may be visible six months earlier, and
    back-dating that commit fails here however the prose reads.
    """
    then = Overlay.load(rewind(beat["repo"], AT), ORG)
    assert not then.perspectives
    assert not [e for e in then.graph().edges if e.causal]

    now = Overlay.load(ModelRepo.open(beat["repo"]), ORG)
    assert PERSPECTIVE in now.perspectives
    assert [e for e in now.graph().edges if e.causal]


def test_this_subject_carries_no_answer_key_and_the_engine_says_so(beat: dict[str, Path]) -> None:
    """AC-adjacent, and the honest half of the beat: Netflix cannot carry falsifiability.

    Asserted as an absence in the model rather than as a sentence in the script, because a claim
    made only in prose is one somebody can quietly stop making. `twin score` has nothing to score
    against, and the refusal names what exists.
    """
    overlay = Overlay.load(ModelRepo.open(beat["repo"]), ORG)
    assert not overlay.outcomes

    out = io.StringIO()
    # Written outside the fixture repository on purpose: a path inside it would dirty the working
    # tree of the very model the rest of this file rewinds, on the day `twin score` stops refusing.
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = main([
            "score", "--repo", str(beat["repo"]), "--org", ORG, "--forecast", str(beat["bundle"]),
            "--outcome", "any-outcome-at-all", "--out", str(beat["repo"].parent / "never.json"),
        ])
    assert code != 0
    assert "any-outcome-at-all" in out.getvalue()


# -- AC 2: the cross-domain comparison ------------------------------------------------------------


def test_a_non_technical_lever_and_a_technical_control_price_in_one_unit(beat: dict[str, Path]) -> None:
    """Cost and credit in the same unit, so a price hold and a billing rebuild are comparable.

    The asymmetry is the finding, not a defect: the lever's mitigation claim rests on two dated
    price changes in this same business and prices; the control's rests on domain theory nobody
    measured here, so it is refused a figure and carries the reason instead. A zero would have
    read as "this control removes nothing", which is a different and probably false claim.
    """
    eye = next(
        e for e in _body(beat["price"])["perspectives"] if e["perspective"] == PERSPECTIVE
    )
    priced = {r["option"]: r for r in eye["responses"]["priced"]}
    assert set(priced) == {LEVER, CONTROL}
    for entry in priced.values():
        assert entry["cost"]["mean"] > 0

    assert priced[LEVER]["mitigation"]["credit"]["mode"] > 0
    control = priced[CONTROL]["mitigation"]
    assert "credit" not in control
    assert control["reason"] and control["detail"]


def test_the_prefilter_removes_an_option_before_any_of_this_prices_it(beat: dict[str, Path]) -> None:
    """A constraint is not a very large price. The removed option is the cheapest of the three on
    purpose, so "no magnitude brings it back" is demonstrable rather than asserted."""
    pre = _body(beat["options"])["prefilter"]
    removed = {r["option"]: r for r in pre["removed"]}
    assert "rank-domestic-members-by-cancellation-risk" in removed
    record = removed["rank-domestic-members-by-cancellation-risk"]
    assert record["constraint"] == "no-individual-level-output"
    assert "cost" not in record and "price" not in record


# -- AC 3: the curve is the output, and the disagreement is visible -------------------------------


def test_the_accounts_disagree_about_which_response_is_cheapest(beat: dict[str, Path]) -> None:
    """The first fixture in this repository where a ranking disagreement is real rather than
    synthesised in a unit test (`twin/tradeoff.py` `_assemble` carried that gap as a stated
    substitute until now).

    Asserted on `cheapest_by_account` rather than on any figure, so re-authoring a cost that keeps
    the flip still passes and one that collapses it does not.
    """
    curve = _body(beat["curve"])
    assert set(curve["accounts"]) == set(ACCOUNTS)
    assert curve["agreement"]["unanimous"] is False
    assert len(set(curve["agreement"]["cheapest_by_account"].values())) >= 2


def test_dropping_any_one_account_changes_nothing_about_the_rest(beat: dict[str, Path]) -> None:
    """No account is privileged — including the one that restates the overlay's own edge."""
    curve = _body(beat["curve"])
    for dropped in ACCOUNTS:
        kept = [a for a in ACCOUNTS if a != dropped]
        out = beat["repo"].parent / f"without-{dropped}.json"
        args = [arg for account in kept for arg in ("--account", account)]
        assert main([
            "trade-off", "--repo", str(beat["repo"]), "--org", ORG, "--origin", ORIGIN,
            "--perspective", PERSPECTIVE, *args, "--out", str(out),
        ]) == 0
        without = _body(out)
        for account in kept:
            before = {p["option"]: p["net_cost_of_risk"]["by_account"][account] for p in curve["curve"]}
            after = {p["option"]: p["net_cost_of_risk"]["by_account"][account] for p in without["curve"]}
            assert before == after, f"dropping {dropped} moved {account}'s own figures"


def test_the_disagreement_reaches_the_surface_before_the_default(beat: dict[str, Path]) -> None:
    """Printed order, not only artefact content. A disagreement a reader has to scroll past the
    default to find is reported only technically — the same reasoning that puts the worst score
    first in `cli._say_score`.

    Anchored on the line prefixes `cli.cmd_trade_off` actually prints (`"  agreement  "`,
    `"  default    "`), not on the bare words: `body['agreement']['note']` itself contains the
    word "default" when the accounts disagree ("... rather than smoothed into the default
    below ..."), so a plain `printed.index("agreement") < printed.index("default")` would still
    pass with the default line deleted outright — the exact regression this test exists to catch.
    """
    out = io.StringIO()
    args = [arg for account in ACCOUNTS for arg in ("--account", account)]
    with contextlib.redirect_stdout(out):
        assert main([
            "trade-off", "--repo", str(beat["repo"]), "--org", ORG, "--origin", ORIGIN,
            "--perspective", PERSPECTIVE, *args,
            "--out", str(beat["repo"].parent / "printed.json"),
        ]) == 0
    printed = out.getvalue()
    assert printed.index("  agreement  ") < printed.index("  default    ")
    assert "unanimous=False" in printed


# -- versioned enactment, the thesis (c) half decision ticket 22 assigns to this subject ----------


def test_enactment_is_proposed_through_the_channel_a_lever_that_is_not_code_uses(
    beat: dict[str, Path],
) -> None:
    """The `record` channel, not `policy` — proposed on the price hold, not the billing rebuild.

    Decision ticket 22 gives Netflix thesis (c), proportionate versioned governance in its
    narrowed form. The narrowing *is* the point here, and it has to land on the right response:
    `record` is the channel for a lever that is **not** code, and `LEVER` (the price hold) is the
    one that is not code — `CONTROL` (a billing/SSO rebuild) is code with a real enforcement
    point, the textbook `policy` case. Proposing `CONTROL` through `record` would print "this
    lever is not code" directly under a response that is, and this test asserts the response id
    itself rather than only the channel's own constant text, so that mistake fails here rather
    than only reading wrong on screen.

    If versioned policy were the shape of governance, the cross-domain comparison two sections up
    could not exist at all — that is `narrowed_claim`, asserted on its content rather than as an
    opaque constant, since `enact.NARROWED_CLAIM` is identical for every org and every proposal
    and `tests/test_enact.py` already pins it directly.

    That the twin proposes and never disposes is `enactment_is_propose_only_at_both_layers`' job
    at both layers, and is not restated here.
    """
    body = _body(beat["proposal"])
    assert body["response"]["id"] == LEVER
    assert body["channel"]["role"] == "record"
    assert "cross-domain comparison" in body["narrowed_claim"]
    # The estate caveat travels in the artefact, not only in the script's own echo lines — see
    # twin/enact.py `_dependency_block`'s last `limits` entry.
    assert any(
        "not from any repository" in limit and repr(ORG) in limit
        for limit in body["dependency"]["limits"]
    )


# -- ACs 5 and 6: the suite, and the computed grade ------------------------------------------------


def test_every_artefact_the_beat_emits_carries_computed_depth_grades(
    beat: dict[str, Path], caps: Capabilities
) -> None:
    """Displayed automatically, from the envelope, on every artefact the beat presents.

    Compared against what `Capabilities.load()` computes from the decision tickets rather than
    merely checked for shape: a grade written into an envelope by hand satisfies any shape check,
    and that is the failure depth grades exist to prevent.
    """
    for name in ("bundle", "rewind", "sweep", "options", "price", "curve", "proposal", "substrate"):
        depth = json.loads(beat[name].read_bytes())["envelope"]["depth"]
        assert depth["capabilities"], f"the {name} artefact names no producing capability"
        for capability, summary in depth["capabilities"].items():
            assert summary == caps.require(capability).summary(), (
                f"the {name} artefact carries a depth grade for {capability} that the checklist "
                "does not compute"
            )


def test_the_scenario_engine_criterion_this_beat_touches_needs_the_other_co_flagship(
    caps: Capabilities,
) -> None:
    """AC 6, and the honest reading: **this ticket moves no grade.**

    Decision ticket 13 AC 7 asks for one fear scenario and one opportunity scenario *across the
    co-flagships*. Netflix now has both, on dated evidence, through the ordinary verbs. Intel has
    neither on a real spine — that is build ticket 75 — so half a criterion is not a criterion,
    and `full` stays derived rather than typed. Build ticket 75 is expected to tick this and to
    change this test with it; a test that had to be edited is the visible form of that.
    """
    graded = caps.require("scenario-engine")
    unchecked = {c["index"] for c in graded.summary()["unchecked"]}
    assert 7 in unchecked, (
        "decision ticket 13 AC 7 is ticked; if the Intel half now exists, update this test and "
        "say which ticket supplied it"
    )


def test_the_beat_script_is_executable() -> None:
    """CI runs `bash twin/beat-netflix.sh` end to end, which is the real check on its steps. This
    is only the bit CI cannot catch by running it through `bash`."""
    assert BEAT.stat().st_mode & 0o111, "the beat script is not executable"
