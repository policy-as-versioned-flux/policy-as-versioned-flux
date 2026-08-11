"""Plurality: rival world models and rival causal accounts (build ticket 32).

Exercised against the netflix fixture's `netflix-base-case` / `rival-aggressive-cannibalisation`
causal accounts, both overriding `streaming-displaces-dvd` — a genuine disagreement about
magnitude and lag over the same two components, so the ensemble spread has something real to
compute rather than comparing a claim against itself.
"""

from __future__ import annotations

import pytest

from twin.causal_accounts import CausalAccountError, ensemble_spread
from twin.model import Overlay
from twin.repo import ModelRepo

ACCOUNTS = ["netflix-base-case", "rival-aggressive-cannibalisation"]
THREE_ACCOUNTS = ACCOUNTS + ["rival-conservative-view"]


@pytest.fixture()
def netflix(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "netflix")


def test_both_accounts_reach_the_shocked_component(netflix: Overlay) -> None:
    body = ensemble_spread(netflix, ACCOUNTS, "streaming-experience")
    assert {a["account"] for a in body["accounts"]} == set(ACCOUNTS)
    row = next(r for r in body["spread"] if r["component"] == "dvd-by-mail")
    assert set(row["accounts_with_a_magnitude"]) == set(ACCOUNTS)
    assert row["range"] == pytest.approx(row["max"] - row["min"])
    assert row["range"] > 0, "two genuinely different elasticities should not land on one figure"


def test_the_rival_account_claims_the_stronger_effect(netflix: Overlay) -> None:
    """`rival-aggressive-cannibalisation` authored a materially higher elasticity — the spread
    should say so, not just report a nonzero range."""
    body = ensemble_spread(netflix, ACCOUNTS, "streaming-experience")
    row = next(r for r in body["spread"] if r["component"] == "dvd-by-mail")
    assert row["by_account"]["rival-aggressive-cannibalisation"] > row["by_account"]["netflix-base-case"]


def test_an_inherited_edge_still_propagates_downstream_of_the_override(netflix: Overlay) -> None:
    """Neither account overrides `price-separation-erodes-goodwill`, so both inherit it unchanged
    — brand-goodwill is still reached, through the SAME downstream edge, by every account."""
    body = ensemble_spread(netflix, ACCOUNTS, "streaming-experience")
    row = next(r for r in body["spread"] if r["component"] == "brand-goodwill")
    assert set(row["accounts_with_a_magnitude"]) == set(ACCOUNTS)


def test_no_field_named_actual_or_canonical(netflix: Overlay) -> None:
    body = ensemble_spread(netflix, ACCOUNTS, "streaming-experience")
    from twin.canon import walk_keys

    keys = set(walk_keys(body))
    assert "actual" not in keys
    assert "canonical" not in keys
    assert "primary_account" not in keys


def test_this_overlays_own_edges_are_nameable_as_just_another_account(netflix: Overlay) -> None:
    """`netflix-base-case` restates the overlay's own authored edge almost exactly — proving the
    code path for a named account and for "the primary graph" are the same code path."""
    from twin.propagate import propagate

    via_account = netflix.causal_graph("netflix-base-case")
    via_overlay = netflix.graph()
    a = propagate(via_account, "streaming-experience")
    b = propagate(via_overlay, "streaming-experience")
    by_component_a = {e["component"]: e for e in a["reached"]}
    by_component_b = {e["component"]: e for e in b["reached"]}
    assert by_component_a.keys() == by_component_b.keys()


def test_dropping_any_one_account_changes_nothing_else(netflix: Overlay) -> None:
    full = ensemble_spread(netflix, THREE_ACCOUNTS, "streaming-experience")
    full_by_component = {r["component"]: r["by_account"] for r in full["spread"]}
    for dropped in THREE_ACCOUNTS:
        remaining = [a for a in THREE_ACCOUNTS if a != dropped]
        narrowed = ensemble_spread(netflix, remaining, "streaming-experience")
        for row in narrowed["spread"]:
            for account_id, value in row["by_account"].items():
                assert value == full_by_component[row["component"]][account_id]


def test_fewer_than_two_accounts_is_refused(netflix: Overlay) -> None:
    with pytest.raises(CausalAccountError, match="at least two"):
        ensemble_spread(netflix, ["netflix-base-case"], "streaming-experience")


def test_an_unknown_account_names_what_exists(netflix: Overlay) -> None:
    from twin.model import ModelError

    with pytest.raises(ModelError, match="no-such-account.*have"):
        ensemble_spread(netflix, ["no-such-account", "netflix-base-case"], "streaming-experience")


def test_a_causal_account_edge_missing_elasticity_is_refused() -> None:
    from twin.schema import SchemaError, validate

    with pytest.raises(SchemaError):
        validate(
            "causal-account",
            {"id": "x", "name": "x", "edges": {"e": {"from": "a", "to": "b", "sign": "positive",
                                                       "lag_days": 1, "evidence_grade": 3}}},
            "planted",
        )


def test_a_causal_account_carries_no_author_or_date_field() -> None:
    """Structural: the schema is closed to id/name/edges/note, so nothing could rank one account
    above another by authorship or recency even if a caller wanted to (AC 4)."""
    from twin.schema import SchemaError, validate

    base = {
        "id": "x", "name": "x",
        "edges": {"e": {"from": "a", "to": "b", "sign": "positive", "lag_days": 1,
                         "elasticity": {"min": 0.1, "mode": 0.2, "max": 0.3}, "evidence_grade": 3}},
    }
    for planted in ("author", "authored_by", "created_at", "priority", "recency"):
        with pytest.raises(SchemaError):
            validate("causal-account", {**base, planted: "x"}, "planted")
