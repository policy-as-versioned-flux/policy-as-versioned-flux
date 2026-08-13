"""The retrospective sweep: the promotion/rescue half of the decaying unbound-signal pool (build
ticket 55, decision ticket 11 Q3).

Build ticket 54's `twin/unbound_pool.py` built retention — a signal the graph cannot yet
interpret decays rather than disappears. Q3's other half is the rescue: "a model change rescues:
adding a component, dependency or causal edge triggers a **retrospective sweep** of the unbound
pool, and a signal the new structure binds is promoted out and its decay reset." This module is
that sweep. It is deliberately the *other* module rather than a change to `unbound_pool.py` —
retention stays retention, and rescue is its own small, replaceable piece (the constitution's
sunk-cost-architecture guard), the same way `twin/ingest.py` sits beside `twin/signal_classify.py`
rather than growing it.

**No history is diffed.** "The new structure" is simply whatever `Overlay.load` reads right now —
after whatever component, dependency or causal edge a model change just added — so re-running
`signal_classify` against the *current* candidate set from scratch already means "re-examined
against the new structure." `ingest.py`'s own `candidates_of()` (build ticket 53) is reused
outright for that candidate set, not re-derived.

**A rescue must be genuine, not a rubber stamp.** `signal_classify.classify()`'s own binder
(`_bind`) always returns *some* candidate — `max` over zero overlap is still a choice — so this
module asks `signal_classify.best_match()` for the score behind that choice first: a signal whose
best-scoring candidate shares no vocabulary at all has not actually become interpretable, and
stays in the pool rather than getting silently bound to whatever candidate happened to sort first.

**Decay never blocks rescue.** Every unbound pool entry is attempted, decayed or not — plain decay
would preferentially delete the longest-lead-time signals, the exact ones a rescue path exists to
catch (Q3's own argument against discarding in the first place). `had_decayed_before_rescue` and
`weight_before_rescue` are carried on every rebound entry so that point is demonstrable, not just
asserted.

**Lead-time-to-recognition is the number the rescue makes measurable.** Pool-entry date (the
signal's own `date`) to binding date (the sweep's own declared `at`) is computed per rebound
signal and reported as a first-class body field, `lead_time_to_recognition`, not folded into an
internal statistic a caller would have to re-derive.
"""

from __future__ import annotations

from typing import Any

from . import TOOL_VERSION, verbs
from .artefact import Artefact, DERIVED
from .grades import Capabilities
from .ingest import candidates_of
from .model import Overlay
from .repo import ModelRepo
from .signal_classify import best_match, classify
from .unbound_pool import pin as decay_pin
from .unbound_pool import pool as unbound_pool_of

KIND_RETROSPECTIVE_SWEEP = "retrospective-sweep"

# Rescue completes decision ticket 11's own sense-move AC5 ("weak-signal retention + promotion
# rule") alongside build ticket 54's retention half; reused rather than a capability of its own,
# the same choice `unbound_pool.py` and `ingest.py` already made.
CAPS_RETROSPECTIVE_SWEEP = verbs.CAPS_SENSE


def rebind(overlay: Overlay, entry: dict[str, Any], candidates: list[dict[str, str]]) -> dict[str, Any] | None:
    """Attempt to bind one unbound-pool entry against the *current* candidate set.

    `None` if nothing in it genuinely bears on the signal (`best_match`'s own score is zero) —
    `classify()` would still return a claim in that case, `_bind`'s own tie-broken default, and
    binding onto it anyway would be exactly the premature promotion Q3's "unless something in the
    graph catches it" refuses. `candidates` must be non-empty; `sweep()` guards that.
    """
    signal = overlay.signals[entry["id"]]
    _, score = best_match(str(signal["statement"]), str(signal["source"]), candidates)
    if score == 0:
        return None
    return classify({"statement": signal["statement"], "source": signal["source"], "candidates": candidates})


def sweep(overlay: Overlay, at: str) -> dict[str, list[dict[str, Any]]]:
    """Re-examine every unbound signal in this overlay against its current model.

    Returns `{"rebound": [...], "still_unbound": [...]}`. A rebound entry carries the unbound-pool
    fields (`pool_entry_date`, decay state at the moment of rescue) plus the binding itself
    (`component`, `steep`, `evidence_grade`) and the metric this ticket exists to make measurable,
    `lead_time_to_recognition_days`. A still-unbound entry is exactly `unbound_pool.pool()`'s own
    shape, unchanged — nothing here mutates or re-reports what did not move.
    """
    entries = unbound_pool_of(overlay, at)
    candidates = candidates_of(overlay)

    rebound: list[dict[str, Any]] = []
    still_unbound: list[dict[str, Any]] = []
    for entry in entries:
        result = rebind(overlay, entry, candidates) if candidates else None
        if result is None:
            still_unbound.append(entry)
            continue
        rebound.append(
            {
                "id": entry["id"],
                "pool_entry_date": entry["date"],
                "binding_date": at,
                "lead_time_to_recognition_days": entry["age_days"],
                "component": result["claim"]["component"],
                "steep": result["steep"],
                "evidence_grade": result["claim"]["evidence_grade"],
                "had_decayed_before_rescue": entry["decayed"],
                "weight_before_rescue": entry["weight"],
            }
        )
    return {"rebound": rebound, "still_unbound": still_unbound}


def lead_time_summary(rebound: list[dict[str, Any]]) -> dict[str, Any]:
    """Lead-time-to-recognition as a first-class output (this ticket's own AC) — per signal and
    summarised, rather than left for a caller to re-derive from the rebound list by hand."""
    days = [int(r["lead_time_to_recognition_days"]) for r in rebound]
    return {
        "unit": "days",
        "count": len(days),
        "min_days": min(days) if days else None,
        "max_days": max(days) if days else None,
        "mean_days": (sum(days) / len(days)) if days else None,
        "per_signal": [{"id": r["id"], "days": r["lead_time_to_recognition_days"]} for r in rebound],
    }


def retrospective_sweep_artefact(
    repo: ModelRepo, caps: Capabilities, org: str, at: str, command: list[str]
) -> Artefact:
    """The sweep, as a derived artefact: nothing here could carry a human's accountability
    (`derived_never_human_signed`) — a fully-automated skill call over an already-committed model
    and an already-committed signal pool determines the output completely."""
    overlay = Overlay.load(repo, org)
    result = sweep(overlay, at)

    return Artefact(
        kind=KIND_RETROSPECTIVE_SWEEP,
        mark=DERIVED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "at": at,
            "decay": decay_pin(),
        },
        depth=caps.depth_block(CAPS_RETROSPECTIVE_SWEEP),
        body={
            "as_of": at,
            "rebound": result["rebound"],
            "still_unbound": result["still_unbound"],
            "lead_time_to_recognition": lead_time_summary(result["rebound"]),
            "counts": {
                "pool_size_examined": len(result["rebound"]) + len(result["still_unbound"]),
                "rebound": len(result["rebound"]),
                "still_unbound": len(result["still_unbound"]),
            },
        },
    )
