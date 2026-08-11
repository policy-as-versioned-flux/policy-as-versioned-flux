"""Believed map, rival forecasts, revealed truth — held as separate position sets, and the
deltas between them (build ticket 16, from decision tickets 07 (Q1c, Q2) and 11).

Decision ticket 07 names three senses of `WorldModel`: **believed** (where an org thinks things
sit), **rival forecasts** (held simultaneously, never merged), and **revealed truth** (the
answer key, retrospective). None of the three loads through a schema slot the others do not — a
world model is a world model, ordinary and unprivileged, distinguished only by the name its
author gave it. Revealed truth is not even a world model: it is derived from a resolved
`outcome` rather than authored as a belief. There is no field anywhere called `actual`.

**No schema-level privilege.** This module takes whichever `world_model` ids the caller names —
ordinarily a scenario's own `world_models` list — and treats every one of them identically: same
lookup, same delta arithmetic, same scoring. Dropping any one of them, including the org's own
named "believed" map or the twin's own default reference, changes nothing about how the rest are
computed (`tests/test_positions.py::test_dropping_any_one_position_changes_nothing_else`).

**Delta, computed and scored, never merely displayed.** Between two forecasts there is no ground
truth, so the only honest comparison is the plain magnitude of disagreement, `|a - b|`. Between a
forecast and revealed truth there *is* a ground truth, so that pair also carries the proper score
(`twin/scoring.py`'s Brier and log loss) — the twin's own belief scored on exactly the same
footing as any rival's, because nothing here special-cases which id produced it.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any

from . import scoring
from .model import ModelError, Overlay
from .pert import quantise


class PositionError(ModelError):
    """No positions were named, or none of them address the proposition asked about."""


def _belief(world_model: dict[str, Any], proposition_id: str) -> float | None:
    beliefs = world_model.get("beliefs") or {}
    return float(beliefs[proposition_id]) if proposition_id in beliefs else None


def revealed(overlay: Overlay, proposition_id: str) -> dict[str, Any]:
    """Revealed truth for a proposition — derived from a resolved outcome, never authored as a
    belief. Not a world model: there is no schema slot here for one to be privileged through."""
    for outcome in overlay.outcomes.values():
        if outcome.get("proposition") == proposition_id:
            return {
                "resolved": True,
                "outcome": outcome["id"],
                "observed": bool(outcome["observed"]),
                "resolved_on": outcome.get("resolved_on"),
                "source": outcome.get("source"),
            }
    return {
        "resolved": False,
        "reason": "no outcome in this overlay resolves this proposition yet",
    }


def pairwise_deltas(positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every unordered pair among the named positions, computed — not merely displayed.

    A plain magnitude of disagreement: there is no ground truth between two forecasts, so a
    proper scoring rule does not apply here. `against_revealed` is the pairing that has one.
    """
    return [
        {"a": a["id"], "b": b["id"], "delta": quantise(abs(a["probability"] - b["probability"]))}
        for a, b in combinations(sorted(positions, key=lambda p: str(p["id"])), 2)
    ]


def against_revealed(positions: list[dict[str, Any]], truth: dict[str, Any]) -> list[dict[str, Any]]:
    """Every position against revealed truth: a plain delta, computed, and a proper score.

    The twin's own default reference is scored through the exact same call as any rival's id —
    there is no branch anywhere that treats one id differently from another.
    """
    if not truth.get("resolved"):
        return []
    observed = bool(truth["observed"])
    out = []
    for position in sorted(positions, key=lambda p: str(p["id"])):
        p = position["probability"]
        out.append(
            {
                "id": position["id"],
                "probability": p,
                "delta_from_revealed": quantise(abs(p - (1.0 if observed else 0.0))),
                **scoring.score(p, observed),
            }
        )
    return out


def deltas(overlay: Overlay, proposition_id: str, world_model_ids: list[str]) -> dict[str, Any]:
    """The whole picture for one proposition: every named position, the pairwise deltas between
    them, and each one scored against revealed truth where it has resolved.

    `world_model_ids` is ordinarily a scenario's own `world_models` list — the same ensemble
    `twin run` already forecasts over — so this reads the identical ids rather than inventing a
    second notion of which positions are "in play".
    """
    proposition = overlay.proposition(proposition_id)
    ids = sorted(dict.fromkeys(str(i) for i in world_model_ids))
    if not ids:
        raise PositionError("no world model named; a delta between zero positions is not a delta")

    positions: list[dict[str, Any]] = []
    abstained: list[dict[str, Any]] = []
    for world_model_id in ids:
        model = overlay.world_model(world_model_id)
        entry = {
            "id": world_model_id,
            "name": model.get("name"),
            "credence": model.get("credence"),
            "layer": "overlay" if world_model_id in overlay.world_models else "world",
        }
        probability = _belief(model, proposition_id)
        if probability is None:
            abstained.append({**entry, "reason": "holds no belief about this proposition"})
        else:
            positions.append({**entry, "probability": probability})

    if not positions:
        raise PositionError(
            f"none of {', '.join(ids)} holds a belief about {proposition_id!r}; a delta needs at "
            "least one position to compare"
        )

    truth = revealed(overlay, proposition_id)
    return {
        "proposition": {"id": proposition_id, "text": proposition.get("text")},
        "positions": positions,
        "abstained": abstained,
        "revealed": truth,
        "pairwise": pairwise_deltas(positions),
        "against_revealed": against_revealed(positions, truth),
        "no_privileged_position": (
            "every position above is a world model like any other, named only by the id its "
            "author gave it; nothing here reads a field called 'actual', and dropping any one of "
            "them — including the org's own believed map or the twin's default reference — "
            "changes nothing about how the remaining ones are computed"
        ),
    }
