"""Plurality: rival world models and rival causal accounts (build ticket 32), from decision
tickets 07 and 08.

`twin/positions.py` (build ticket 16) already gives rival **world models** — belief probabilities
— a place to coexist with no privilege between them. This module gives rival **causal accounts**
the same treatment for the other half of a scenario's uncertainty: not "what does each eye believe
will happen" but "how, mechanically, does a shock actually propagate" — and two evidenced people
can disagree about that too.

**No account is canonical.** `twin/model.py Overlay.causal_graph(account_id)` treats every named
account identically, this overlay's own `edges` collection included as just another named id
alongside it — the same non-privilege `positions.py` already established for world models. The
`causal-account` schema (`twin/schema.py`) is closed to `id`/`name`/`edges`/`note`: there is no
field for an author or a date, so nothing could rank one account above another by either even if
a caller wanted to (decision ticket 08 — adjudication is by accumulated calibration score over
time, never by authorship or recency; this module builds no calibration mechanism of its own,
because rival *causal* accounts do not themselves emit the scoreable forecasts `twin/scoring.py`
grades — that is still a world model's job, via `twin run` and `twin score`).

**Ensemble spread is computed, not merely displayed** — the same discipline `positions.py`'s
`pairwise_deltas` applies to belief. For a shock at one origin, each account's own graph is
propagated independently (`twin/propagate.py`, unmodified), and the primary path's attenuated mean
at every component the shock reaches is compared across accounts. The spread between them — not
either account's own figure alone — is what a reader is meant to take as the uncertainty here.
"""

from __future__ import annotations

from typing import Any

from . import propagate as propagate_mod
from .model import ModelError, Overlay
from .pert import quantise


class CausalAccountError(ModelError):
    """Fewer than two accounts were named, or an account reaches nothing the others do."""


def _primary_mean(entry_for_component: dict[str, Any]) -> float | None:
    """The primary path's attenuated mean for one reached component, or `None` past the
    attenuation boundary — a directional-only path carries no magnitude to compare."""
    primary = next((p for p in entry_for_component["paths"] if p.get("primary")), None)
    if primary is None or primary.get("directional_only"):
        return None
    return float(primary["attenuated"]["mean"])


def ensemble_spread(overlay: Overlay, account_ids: list[str], origin: str) -> dict[str, Any]:
    """Every named account's own propagation from `origin`, and the spread between them.

    `account_ids` is exactly the list the caller names, read identically for each — the same
    "no privileged id" contract `positions.deltas` gives `world_model_ids`. Dropping any one
    account changes nothing about how the remaining ones are computed
    (`tests/test_causal_accounts.py::test_dropping_any_one_account_changes_nothing_else`).
    """
    ids = sorted(dict.fromkeys(str(i) for i in account_ids))
    if len(ids) < 2:
        raise CausalAccountError(
            f"{len(ids)} account(s) named; an ensemble spread needs at least two rival accounts "
            "to have a spread between"
        )

    per_account: list[dict[str, Any]] = []
    means_by_component: dict[str, list[tuple[str, float]]] = {}
    for account_id in ids:
        account = overlay.causal_account(account_id)
        graph = overlay.causal_graph(account_id)
        if origin not in graph.components:
            raise CausalAccountError(f"no component {origin!r} in the graph account {account_id!r} builds")
        result = propagate_mod.propagate(graph, origin)
        reached = sorted(result["reached"], key=lambda e: str(e["component"]))
        for entry in reached:
            mean = _primary_mean(entry)
            if mean is not None:
                means_by_component.setdefault(str(entry["component"]), []).append((account_id, mean))
        per_account.append({
            "account": account_id,
            "name": account.get("name"),
            "overrides": sorted(account["edges"]),
            "reached": reached,
        })

    spread = []
    for component in sorted(means_by_component):
        pairs = means_by_component[component]
        values = [v for _, v in pairs]
        spread.append({
            "component": component,
            "accounts_with_a_magnitude": [a for a, _ in pairs],
            "by_account": {a: quantise(v) for a, v in pairs},
            "min": quantise(min(values)),
            "max": quantise(max(values)),
            "range": quantise(max(values) - min(values)),
        })

    return {
        "origin": origin,
        "accounts": per_account,
        "spread": spread,
        "spread_basis": (
            "the primary path's attenuated mean at each reached component, compared across "
            "accounts — a component past the attenuation boundary under every account carries no "
            "magnitude anywhere and so has no spread row, rather than a manufactured zero"
        ),
        "no_privileged_account": (
            "every account above is read by the id its author gave it, this overlay's own `edges` "
            "collection included as just another named account; the causal-account schema has no "
            "field for an author or a date, so nothing could rank one above another by either even "
            "if a caller wanted to — adjudication is by accumulated calibration score over time, "
            "never by authorship or recency"
        ),
    }
