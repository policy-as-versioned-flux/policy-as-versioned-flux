"""`planter` (build ticket 52, decision ticket 12 AC 4, Q2, Q3b): the sealed half of the
planter/detector/scorer split.

Decision ticket 12 Q2: "A planter agent holds ground truth in a sealed artefact; a detector agent
runs with no access to it and no shared context; a scorer reads both." This module is the sealed
side: the only code in this system that ever reads `substrate_generator.generate()`'s own
`plants` field. Everything it hands onward (`PlantedWorld.public`) has that field already
stripped — structurally, not by convention: `twin/detector.py` imports nothing from this module
(`twin/invariants/harness.py`'s `planter_detector_scorer_are_structurally_separated_and_...` guard
proves it on the real source, not a promise in a docstring).

**What this does NOT fix, recorded rather than papered over (decision ticket 12 Q2):** planter and
detector are the same model family and share priors here, the same way they would in a live
deployment before it is deliberately varied. `SHARED_PRIOR_LIMITATION` is exported so
`twin/scorer.py` can publish it with every result rather than leaving it in this module's own
docstring where a caller of the score would never see it.

Q3b — the actionability horizon: "by the time something is detectable it's often too late to
course correct... every planted signal carries a point of no return." The horizon is supplied by
the caller alongside the recipe, not folded into `SubstrateRecipe` itself (ticket 48's own closed,
versioned schema — `twin.substrate-recipe/v1` — describes *what text to generate*, not the
planter's own ground-truth metadata about when a plant stops being actionable). `plant()` refuses
a recipe whose planted signals are not every one covered by a horizon: "every plant carries an
actionability horizon" is enforced here, not merely documented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .substrate import SubstrateRecipe
from .substrate_generator import LINES_PER_CHANNEL, generate

SHARED_PRIOR_LIMITATION = (
    "planter and detector are the same model family and share model priors (decision ticket 12 "
    "Q2): a synthetic result is never evidence the twin anticipates the world, only evidence that "
    "the detection machinery works. The detector may find a plant because it thinks like the "
    "planter, not because the signal was findable by an independently-minded reader."
)


class PlanterError(RuntimeError):
    """A recipe schedules a planted signal with no declared actionability horizon."""


@dataclass(frozen=True)
class Plant:
    """One planted signal's ground truth: where it sits, and when it stops being actionable.

    Sealed — the planter and the scorer are the only modules in this codebase that construct or
    read one; `twin/detector.py` imports neither this class nor this module.
    """

    channel: str
    index: int
    signal: str
    actionability_horizon: str  # YYYY-MM-DD: the point of no return (decision ticket 12 Q3b)


@dataclass(frozen=True)
class PlantedWorld:
    """`public` is exactly what a detector may see — `substrate_generator.generate()`'s own batch
    with the `plants` key removed, nothing else changed. `ground_truth` never leaves this module
    and `twin/scorer.py`, except by being handed explicitly to `scorer.score()` as an argument.
    """

    public: dict[str, Any]
    ground_truth: tuple[Plant, ...]


def plant(
    recipe: SubstrateRecipe,
    horizons: Mapping[str, str],
    lines_per_channel: int = LINES_PER_CHANNEL,
) -> PlantedWorld:
    """The planter. One recipe (ticket 48's own, unmodified) and one actionability horizon per
    planted signal in; a sealed `PlantedWorld` out. `substrate_generator.generate()` (ticket 49,
    unmodified) does the actual text generation — this function's own job is holding the ground
    truth apart from what it hands onward.
    """
    missing = [s for s in recipe.planted_signals if s not in horizons]
    if missing:
        raise PlanterError(
            f"planter: {len(missing)} planted signal(s) have no declared actionability horizon: "
            f"{missing} — every plant must carry one (decision ticket 12 Q3b)"
        )
    batch = generate(recipe, lines_per_channel)
    ground_truth = tuple(
        Plant(
            channel=p["channel"], index=p["index"], signal=p["signal"],
            actionability_horizon=horizons[p["signal"]],
        )
        for p in batch["plants"]
    )
    public = {k: v for k, v in batch.items() if k != "plants"}
    return PlantedWorld(public=public, ground_truth=ground_truth)
