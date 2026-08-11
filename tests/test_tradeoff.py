"""The trade-off curve across the ensemble, with a marked default (build ticket 33).

Exercised against the netflix fixture's `netflix-base-case` / `rival-cdn-headwind` causal
accounts, both bearing on `cdn-capacity-lifts-streaming` — the one edge in the fixture that both
prices (grade 2, inside the published threshold) and is named by a response's own mitigation
claim (`expand-the-delivery-network`, against `streaming-experience`). The three accounts build
ticket 32 already carries (`netflix-base-case`, `rival-aggressive-cannibalisation`,
`rival-conservative-view`) all share `streaming-displaces-dvd`, graded 3 — always outside the
pricing threshold — so none of them could move a response's own net figure at all.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from twin.artefact import ArtefactError
from twin.canon import walk_keys
from twin.cli import main
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.tradeoff import TradeOffError, _assemble, curve

ORG = "netflix"
ORIGIN = "content-delivery-network"
OPERATOR, COUNCIL = "the-operator", "the-staff-council"
ACCOUNTS = ["netflix-base-case", "rival-cdn-headwind"]
SURVIVOR = "expand-the-delivery-network"


@pytest.fixture()
def netflix(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, ORG)


def _point(body: dict, option: str) -> dict:
    return next(p for p in body["curve"] if p["option"] == option)


# -- the net figure, and how it moves across the ensemble ------------------------------------


def test_a_credited_responses_own_net_cost_moves_across_the_ensemble(netflix: Overlay) -> None:
    """The whole point: two accounts that genuinely disagree about the cdn edge produce a real,
    nonzero range in a response's own net cost of risk — not just in the impact beneath it."""
    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    point = _point(body, SURVIVOR)
    assert set(point["net_cost_of_risk"]["by_account"]) == set(ACCOUNTS)
    assert point["net_cost_of_risk"]["range"] > 0
    assert point["net_cost_of_risk"]["range"] == pytest.approx(
        point["net_cost_of_risk"]["max"] - point["net_cost_of_risk"]["min"]
    )


def test_the_weaker_cdn_account_earns_less_credit_and_a_higher_net_cost(netflix: Overlay) -> None:
    """`rival-cdn-headwind` authored a materially lower elasticity, so it should earn the response
    less credit, and therefore a higher net cost — not just a different number."""
    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    by_account = _point(body, SURVIVOR)["net_cost_of_risk"]["by_account"]
    assert by_account["rival-cdn-headwind"] > by_account["netflix-base-case"]


def test_both_accounts_credit_the_claim_since_both_stay_inside_the_pricing_threshold(
    netflix: Overlay,
) -> None:
    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    point = _point(body, SURVIVOR)
    assert set(point["credited_by"]) == set(ACCOUNTS)
    assert point["uncredited_by"] == []


def test_the_three_streaming_displaces_dvd_accounts_never_move_a_net_figure(netflix: Overlay) -> None:
    """The accounts build ticket 32 shipped all share an edge graded 3 — outside the pricing
    threshold — so a curve built only from those has nowhere for a net figure to move."""
    three = ["netflix-base-case", "rival-aggressive-cannibalisation", "rival-conservative-view"]
    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, three)
    point = _point(body, SURVIVOR)
    assert point["net_cost_of_risk"]["range"] == 0


# -- the default: computed, marked, and not a recommendation -------------------------------


def test_the_default_names_its_own_basis(netflix: Overlay) -> None:
    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    assert body["default"]["option"] == SURVIVOR
    assert "basis" in body["default"]
    assert "default" in body["default"]["basis"] or "point" in body["default"]["basis"]


def test_dropping_the_dissenting_account_changes_the_range_but_not_the_other_accounts_own_figure(
    netflix: Overlay,
) -> None:
    """The same 'no privileged account' contract `causal_accounts.py` established: a remaining
    account's own figure does not depend on who else was named."""
    full = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    solo_pair = curve(
        netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses,
        ["netflix-base-case", "rival-conservative-view"],
    )
    full_figure = _point(full, SURVIVOR)["net_cost_of_risk"]["by_account"]["netflix-base-case"]
    other_figure = _point(solo_pair, SURVIVOR)["net_cost_of_risk"]["by_account"]["netflix-base-case"]
    assert full_figure == other_figure


# -- ranking disagreement, on synthetic figures -----------------------------------------------
#
# No fixture in this repository makes two admitted responses actually swap which is cheapest
# between accounts (`expand-the-delivery-network` costs orders of magnitude more than
# `stake-the-quarter-on-one-title` under every account named, so the ranking is always unanimous
# in practice — see test_a_second_admitted_response_under_the_council_gets_its_own_row below).
# `_assemble` is the pure part of `curve()` — everything after the per-account `pricing.price()`
# calls — so the disagreement path is exercised directly against hand-picked numbers instead.


def test_assemble_reports_a_ranking_disagreement_across_accounts() -> None:
    """`account-a` prefers `cheap-under-a`; `account-b` prefers `cheap-under-b`. Neither the
    `unanimous` flag nor the per-account picks may paper over that."""
    ids = ["account-a", "account-b"]
    option_ids = ["cheap-under-a", "cheap-under-b"]
    names = {"cheap-under-a": "Cheap under A", "cheap-under-b": "Cheap under B"}
    by_account = {
        "account-a": {"cheap-under-a": 10.0, "cheap-under-b": 90.0},
        "account-b": {"cheap-under-a": 90.0, "cheap-under-b": 10.0},
    }
    body = _assemble(ids, option_ids, names, by_account, credited_by={})

    assert body["agreement"]["unanimous"] is False
    assert body["agreement"]["cheapest_by_account"] == {
        "account-a": "cheap-under-a", "account-b": "cheap-under-b",
    }
    assert "disagree" in body["agreement"]["note"]


def test_assemble_reports_unanimous_when_every_account_agrees() -> None:
    ids = ["account-a", "account-b"]
    option_ids = ["always-cheaper", "always-pricier"]
    names = {"always-cheaper": "Always cheaper", "always-pricier": "Always pricier"}
    by_account = {
        "account-a": {"always-cheaper": 10.0, "always-pricier": 20.0},
        "account-b": {"always-cheaper": 15.0, "always-pricier": 25.0},
    }
    body = _assemble(ids, option_ids, names, by_account, credited_by={})

    assert body["agreement"]["unanimous"] is True
    assert body["agreement"]["cheapest_by_account"] == {
        "account-a": "always-cheaper", "account-b": "always-cheaper",
    }
    assert "agree" in body["agreement"]["note"]
    # The mean across both accounts is lower for always-cheaper (12.5 vs 22.5): the default
    # agrees with the unanimous per-account picks here, not just by coincidence of the fixture.
    assert body["default"]["option"] == "always-cheaper"


def test_assemble_defaults_to_the_lowest_mean_even_when_accounts_disagree() -> None:
    """A tie-breaker on `sum(...)/len(ids)`, not on either account's own figure alone."""
    ids = ["account-a", "account-b"]
    option_ids = ["cheap-under-a", "cheap-under-b"]
    names = {"cheap-under-a": "Cheap under A", "cheap-under-b": "Cheap under B"}
    by_account = {
        "account-a": {"cheap-under-a": 10.0, "cheap-under-b": 12.0},
        "account-b": {"cheap-under-a": 90.0, "cheap-under-b": 12.0},
    }
    # cheap-under-a: mean (10+90)/2 = 50. cheap-under-b: mean (12+12)/2 = 12. b wins the mean
    # despite a winning under account-a alone — the default reads no single account as privileged.
    body = _assemble(ids, option_ids, names, by_account, credited_by={})
    assert body["default"]["option"] == "cheap-under-b"


# -- two admitted responses under a different eye -------------------------------------------


def test_a_second_admitted_response_under_the_council_gets_its_own_row(netflix: Overlay) -> None:
    """`stake-the-quarter-on-one-title` crosses the operator's ruin boundary and not the
    council's, so under this eye two responses are admitted rather than one."""
    body = curve(netflix, netflix.perspectives[COUNCIL], ORIGIN, netflix.responses, ACCOUNTS)
    assert {p["option"] for p in body["curve"]} == {SURVIVOR, "stake-the-quarter-on-one-title"}
    # Costed at 5 against a multi-million-pound response: unanimous is the honest answer here,
    # not a sign the mechanism failed to look — see test_the_three_streaming_displaces_dvd_accounts
    # and test_a_credited_responses_own_net_cost above for where the disagreement actually shows.
    assert body["agreement"]["unanimous"] is True
    assert body["default"]["option"] == "stake-the-quarter-on-one-title"


# -- refusals --------------------------------------------------------------------------------


def test_fewer_than_two_accounts_is_refused(netflix: Overlay) -> None:
    with pytest.raises(TradeOffError, match="at least two"):
        curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ["netflix-base-case"])


def test_no_admitted_response_is_refused(netflix: Overlay) -> None:
    excluded_only = {
        k: v for k, v in netflix.responses.items()
        if k in ("instrument-viewers-without-telling-them", "stake-the-quarter-on-one-title")
    }
    with pytest.raises(TradeOffError, match="no admitted response"):
        curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, excluded_only, ACCOUNTS)


def test_an_unknown_account_names_what_exists(netflix: Overlay) -> None:
    from twin.model import ModelError

    with pytest.raises(ModelError, match="no-such-account.*have"):
        curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses,
              ["no-such-account", "netflix-base-case"])


# -- closed body, and no action-shaped field -------------------------------------------------


def test_the_curve_body_is_closed(netflix: Overlay) -> None:
    from twin.tradeoff import refuse_undeclared_keys

    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    with pytest.raises(ArtefactError, match="undeclared field"):
        refuse_undeclared_keys({**body, "recommended_option": SURVIVOR})


def test_no_field_named_actual_canonical_or_recommended(netflix: Overlay) -> None:
    body = curve(netflix, netflix.perspectives[OPERATOR], ORIGIN, netflix.responses, ACCOUNTS)
    keys = set(walk_keys(body))
    assert "actual" not in keys
    assert "canonical" not in keys
    assert "recommended" not in keys
    assert "recommended_option" not in keys
    assert "ranking" not in keys
    assert "verdict" not in keys


# -- seam 1 ------------------------------------------------------------------------------------
#
# No `test_..._reproduces_from_its_own_pins` here: `twin/reproduce.py`'s `VERBS` allow-list does
# not cover `positions`, `credibility` or `causal-accounts` either (16, 31, 32) — the same
# established gap, not reopened by this ticket.


def test_the_cli_prints_every_account_never_one_collapsed_number(
    model_repo_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The ticket's own checklist: no consumer-facing path reduces the curve to a scalar. The CLI
    summary line for the credited response must show both accounts' own figures, not an average."""
    out = tmp_path / "trade-off-curve.json"
    capsys.readouterr()
    assert main([
        "trade-off", "--repo", str(model_repo_dir), "--org", ORG,
        "--origin", ORIGIN, "--perspective", OPERATOR,
        "--account", ACCOUNTS[0], "--account", ACCOUNTS[1], "--out", str(out),
    ]) == 0
    printed = capsys.readouterr().out

    body = json.loads(out.read_bytes())["body"]
    by_account = _point(body, SURVIVOR)["net_cost_of_risk"]["by_account"]
    assert by_account["netflix-base-case"] != by_account["rival-cdn-headwind"]

    line = next(row for row in printed.splitlines() if SURVIVOR in row)
    assert "netflix-base-case=" in line and "rival-cdn-headwind=" in line, (
        f"the CLI line for {SURVIVOR!r} does not show a distinct figure per account: {line!r}"
    )
    assert "range=" in line

    # Not just present labels: the printed number for each account must match the artefact's own
    # figure, so a CLI bug that showed two correct-looking labels beside one repeated number would
    # still fail here.
    printed_by_account = {
        account: float(figure.replace(",", ""))
        for account, figure in re.findall(r"([a-z0-9-]+)=([\d,]+)", line)
        if account in ACCOUNTS  # the same line also carries `range=...`, not an account figure
    }
    assert set(printed_by_account) == set(ACCOUNTS)
    for account, expected in by_account.items():
        assert abs(printed_by_account[account] - expected) < 1, (
            f"the CLI printed {account}={printed_by_account[account]}, the artefact says {expected}"
        )


def test_a_perspective_the_overlay_does_not_hold_is_a_sentence(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "trade-off-curve.json"
    assert main([
        "trade-off", "--repo", str(model_repo_dir), "--org", ORG,
        "--origin", ORIGIN, "--perspective", "nobody",
        "--account", ACCOUNTS[0], "--account", ACCOUNTS[1], "--out", str(out),
    ]) == 2
    assert not out.exists()
