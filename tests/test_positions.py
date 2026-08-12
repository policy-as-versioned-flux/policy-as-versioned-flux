"""Believed map, rival forecasts, revealed truth — and the deltas between them (build ticket 16).

Exercised against the netflix fixture's existing ensemble (`twin-default`,
`rival-fast-commoditisation`, `netflix-believed`) rather than new fixture data: `twin run` and
`twin score` already treat these three identically, and this module reads the same ids.
"""

from __future__ import annotations

import pytest

from twin import fixtures
from twin.model import ModelError, Overlay
from twin.positions import PositionError, deltas
from twin.repo import ModelRepo

PROPOSITION = "dvd-rental-revenue-falls-faster-than-streaming-adds"
ALL_MODELS = ["twin-default", "rival-fast-commoditisation", "netflix-believed"]


@pytest.fixture()
def netflix(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "netflix")


def test_three_positions_and_no_field_called_actual(netflix: Overlay) -> None:
    body = deltas(netflix, PROPOSITION, ALL_MODELS)
    assert {p["id"] for p in body["positions"]} == set(ALL_MODELS)
    assert not body["abstained"]
    assert "actual" not in body


def test_pairwise_deltas_are_computed_for_every_pair(netflix: Overlay) -> None:
    body = deltas(netflix, PROPOSITION, ALL_MODELS)
    pairs = {(row["a"], row["b"]): row["delta"] for row in body["pairwise"]}
    assert len(pairs) == 3, "three positions, three unordered pairs"
    assert pairs[("netflix-believed", "twin-default")] == pytest.approx(0.37)
    assert pairs[("netflix-believed", "rival-fast-commoditisation")] == pytest.approx(0.56)
    assert pairs[("rival-fast-commoditisation", "twin-default")] == pytest.approx(0.19)


def test_against_revealed_matches_the_proper_score(netflix: Overlay) -> None:
    """The same Brier scores `twin score` computes — the twin's own belief on the same footing."""
    body = deltas(netflix, PROPOSITION, ALL_MODELS)
    scored = {row["id"]: row for row in body["against_revealed"]}
    assert body["revealed"] == {
        "resolved": True,
        "outcome": "dvd-decline-2011-resolved",
        "observed": True,
        "resolved_on": "2012-12-31",
        "source": "Fixture answer key (stands in for the segmental filing).",
    }
    assert scored["netflix-believed"]["brier"] == pytest.approx(0.5625)
    assert scored["twin-default"]["brier"] == pytest.approx(0.1444)
    assert scored["rival-fast-commoditisation"]["brier"] == pytest.approx(0.0361)
    assert scored["netflix-believed"]["delta_from_revealed"] == pytest.approx(0.75), (
        "the plain magnitude of disagreement against certainty, distinct from the proper score"
    )


def test_dropping_any_one_position_changes_nothing_else(netflix: Overlay) -> None:
    """No id is required. The org's own believed map, the twin's default, or a rival — dropping
    any one of them still computes, and the survivors' own figures do not move."""
    full = deltas(netflix, PROPOSITION, ALL_MODELS)
    full_scores = {row["id"]: row["brier"] for row in full["against_revealed"]}

    for dropped in ALL_MODELS:
        remaining = [m for m in ALL_MODELS if m != dropped]
        body = deltas(netflix, PROPOSITION, remaining)
        assert {p["id"] for p in body["positions"]} == set(remaining)
        assert len(body["pairwise"]) == 1, "two positions, one pair"
        for row in body["against_revealed"]:
            assert row["brier"] == full_scores[row["id"]], (
                f"dropping {dropped!r} moved a surviving position's own score"
            )


def test_order_of_the_named_ids_does_not_matter(netflix: Overlay) -> None:
    forwards = deltas(netflix, PROPOSITION, ALL_MODELS)
    backwards = deltas(netflix, PROPOSITION, list(reversed(ALL_MODELS)))
    assert forwards == backwards


def test_no_world_model_named_is_refused(netflix: Overlay) -> None:
    with pytest.raises(PositionError, match="no world model named"):
        deltas(netflix, PROPOSITION, [])


def test_a_world_model_with_no_belief_about_the_proposition_abstains(netflix: Overlay) -> None:
    """`netflix-believed` holds a belief about the dvd proposition and not the euv one — it
    abstains rather than crashing, and the artefact says why."""
    other_proposition = "euv-tool-deliveries-slip-past-2026"
    body = deltas(netflix, other_proposition, ["twin-default", "netflix-believed"])
    assert {p["id"] for p in body["positions"]} == {"twin-default"}
    assert body["abstained"] == [
        {
            "id": "netflix-believed",
            "name": "The org's believed map",
            "credence": 0.2,
            "layer": "overlay",
            "reason": "holds no belief about this proposition",
        }
    ]
    assert body["revealed"]["resolved"] is False, "no outcome resolves this proposition yet"


def test_none_of_the_named_models_holds_a_belief_is_refused(netflix: Overlay) -> None:
    with pytest.raises(PositionError, match="none of netflix-believed holds a belief"):
        deltas(netflix, "euv-tool-deliveries-slip-past-2026", ["netflix-believed"])


def test_an_unresolved_proposition_reports_why_rather_than_a_number(repo: ModelRepo) -> None:
    intel = Overlay.load(repo, "intel")
    body = deltas(intel, "euv-tool-deliveries-slip-past-2026", ["twin-default", "intel-believed"])
    assert body["revealed"] == {
        "resolved": False,
        "reason": "no outcome in this overlay resolves this proposition yet",
    }
    assert body["against_revealed"] == []


def test_an_unknown_proposition_is_refused(netflix: Overlay) -> None:
    with pytest.raises(ModelError, match="no proposition"):
        deltas(netflix, "no-such-proposition", ALL_MODELS)
