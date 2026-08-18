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

`horizons_for()` is where a committed recipe's horizons come from: `twin/plant-horizons.yaml`, a
versioned document keyed by recipe id, read the way `twin/decay.yaml` and `twin/evidence-ladder.yaml`
are. It lives on this side of the seal deliberately — a horizon is ground truth, and
`twin/detector.py` imports nothing from this module (build ticket 73).

**Strength (build ticket 87, decision ticket 12's own "planting protocol: strength, lead time,
burial, distribution of difficulty").** Lead time was already the actionability horizon above;
burial and its distribution are `substrate_eval.plant_difficulty`/`plant_difficulty_spread`. Only
strength — how loud the ground-truth signal itself is, independent of how well it is buried — had
no field anywhere. `Plant.strength` is that field: a declared unit-interval value, read from
`plant-horizons.yaml` beside the horizon and reason it already carries, and enforced the identical
way — `plant()` refuses a recipe whose planted signals are not every one covered by a strength, the
same "every plant must carry one" discipline Q3b already established for the horizon.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from . import PACKAGE_DIR
from .regimes import RegimeError, cutoff
from .substrate import SubstrateRecipe
from .substrate_generator import LINES_PER_CHANNEL, generate

HORIZONS_PATH = PACKAGE_DIR / "plant-horizons.yaml"
HORIZONS_SCHEMA = "twin.plant-horizons/v1"

SHARED_PRIOR_LIMITATION = (
    "planter and detector are the same model family and share model priors (decision ticket 12 "
    "Q2): a synthetic result is never evidence the twin anticipates the world, only evidence that "
    "the detection machinery works. The detector may find a plant because it thinks like the "
    "planter, not because the signal was findable by an independently-minded reader."
)


class PlanterError(RuntimeError):
    """A recipe schedules a planted signal with no declared actionability horizon, or a horizons
    document has drifted from the recipe it claims to cover."""


def horizons_for(
    recipe: SubstrateRecipe, path: Path | None = None
) -> tuple[dict[str, str], dict[str, str], dict[str, float]]:
    """`({signal: horizon}, {signal: reason}, {signal: strength})` for a committed recipe,
    validated on read.

    Drift in either direction is refused rather than absorbed. A horizons document naming a signal
    the recipe never plants is a stale seal — the plant it was written for is gone, and the file
    still reads as covering it. A recipe whose signals this document misses is `plant()`'s own
    refusal, left there because that is where the requirement lives.

    A horizon is validated by `regimes.cutoff` itself, not by a second date parser: it is compared
    against `detected_at` as text in `twin/scorer.py`, which is the identical day-string ordering
    the regime gate and `Spine.at` already use, so a horizon in another shape compares wrong rather
    than failing (`twin/spine.py` makes the same choice for the same reason).

    `strength` is a plain unit-interval float (build ticket 87) — how strong the planted signal
    itself is, a declared property distinct from how well it is buried (`plant_difficulty`) or how
    long it stays actionable (the horizon above).
    """
    source = path or HORIZONS_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != HORIZONS_SCHEMA:
        raise PlanterError(f"{source}: not a {HORIZONS_SCHEMA} document")
    declared = doc.get("recipes") or {}
    entries = declared.get(recipe.id) if isinstance(declared, dict) else None
    if not isinstance(entries, list):
        raise PlanterError(
            f"{source}: no actionability horizons declared for recipe {recipe.id!r} "
            f"(have: {', '.join(sorted(declared)) if isinstance(declared, dict) else 'none'})"
        )
    planted = set(recipe.planted_signals)
    dates: dict[str, str] = {}
    reasons: dict[str, str] = {}
    strengths: dict[str, float] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PlanterError(f"{source}: recipe {recipe.id!r} has a horizon entry that is not a mapping: {entry!r}")
        signal = str(entry.get("signal", "")).strip()
        reason = str(entry.get("reason", "")).strip()
        if signal not in planted:
            raise PlanterError(
                f"{source}: recipe {recipe.id!r} never plants {signal!r} — the horizons document "
                "has drifted from the recipe it covers"
            )
        try:
            horizon = cutoff(str(entry.get("horizon", "")).strip())
        except RegimeError as exc:
            raise PlanterError(f"{source}: {signal!r} declares an unusable horizon — {exc}") from None
        if not reason:
            raise PlanterError(
                f"{source}: {signal!r} declares a horizon with no reason — an undated-looking date "
                "nobody can argue with is how a self-declared number gets in"
            )
        if "strength" not in entry:
            raise PlanterError(
                f"{source}: {signal!r} declares a horizon with no strength — every plant's own "
                "severity is declared beside its lead time and burial (decision ticket 12 Q3)"
            )
        try:
            strength = float(entry["strength"])
        except (TypeError, ValueError):
            raise PlanterError(f"{source}: {signal!r} declares an unusable strength {entry['strength']!r}") from None
        if not 0.0 <= strength <= 1.0:
            raise PlanterError(f"{source}: {signal!r} declares a strength {strength!r} outside [0, 1]")
        dates[signal], reasons[signal], strengths[signal] = horizon, reason, strength
    return dates, reasons, strengths


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
    strength: float  # 0..1: how strong the signal itself is, declared apart from its burial (build ticket 87)


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
    strengths: Mapping[str, float],
    lines_per_channel: int = LINES_PER_CHANNEL,
) -> PlantedWorld:
    """The planter. One recipe (ticket 48's own, unmodified), one actionability horizon and one
    strength per planted signal in; a sealed `PlantedWorld` out.
    `substrate_generator.generate()` (ticket 49, unmodified) does the actual text generation —
    this function's own job is holding the ground truth apart from what it hands onward.
    """
    missing = [s for s in recipe.planted_signals if s not in horizons]
    if missing:
        raise PlanterError(
            f"planter: {len(missing)} planted signal(s) have no declared actionability horizon: "
            f"{missing} — every plant must carry one (decision ticket 12 Q3b)"
        )
    missing_strengths = [s for s in recipe.planted_signals if s not in strengths]
    if missing_strengths:
        raise PlanterError(
            f"planter: {len(missing_strengths)} planted signal(s) have no declared strength: "
            f"{missing_strengths} — every plant must carry one, the same discipline as its "
            "actionability horizon (decision ticket 12 Q3, build ticket 87)"
        )
    out_of_range = {s: v for s, v in strengths.items() if s in recipe.planted_signals and not 0.0 <= float(v) <= 1.0}
    if out_of_range:
        raise PlanterError(f"planter: strength must be in [0, 1], got {out_of_range}")
    batch = generate(recipe, lines_per_channel)
    ground_truth = tuple(
        Plant(
            channel=p["channel"], index=p["index"], signal=p["signal"],
            actionability_horizon=horizons[p["signal"]],
            strength=float(strengths[p["signal"]]),
        )
        for p in batch["plants"]
    )
    public = {k: v for k, v in batch.items() if k != "plants"}
    return PlantedWorld(public=public, ground_truth=ground_truth)
