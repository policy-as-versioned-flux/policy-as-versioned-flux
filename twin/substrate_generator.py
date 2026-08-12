"""`substrate-generator` (build ticket 49, decision ticket 12) — the fifth of the six skills seam
3 (build ticket 42, `twin/skills.py`) exists to evaluate.

Decision ticket 12 Q1: a believable world as the **medium**, with instrumented test cases (planted
signals) inside it, **measurability winning ties**. Q4 resolved seeded LLM generation from a
versioned recipe as the generation method; build ticket 48 built that recipe format
(`twin/substrate.py`'s `SubstrateRecipe`) and the toy mechanics — `generate_deterministic`, pure
`random.Random(seed)`, no external entropy — plus the spike establishing that a *real* generator
(a live model call) cannot promise `identical_pins_identical_bytes` and so is marked `authored`,
never `derived`. This ticket builds the actual multi-modal generator: not a live model call (no
provider is reachable from this suite, the same reason `signal-classify`, `evolution-judge`,
`causal-claims` and `gameplay-lens` are heuristic reference implementations rather than model
calls) but a real, tested mechanism for turning one pinned recipe into a coherent, multi-channel
substrate — **org events, communications, HR records, telemetry** — with mundane content
dominating by construction and planted signals surfacing where the recipe schedules them.

**Seeded and regenerable via ticket 48's mechanics, literally.** Each channel's own content is
produced by calling `substrate.generate_deterministic` itself, not a re-implementation of it —
`recipe.templates` are round-robined across the four channels and each channel gets its own
derived (still pure-`random.Random`, still reproducible) recipe. Two calls to `generate()` against
the identical recipe therefore reproduce byte-for-byte, the same guarantee ticket 48 demonstrated
and the toy generator's own honest limit: this is the deterministic reference implementation, not
a claim about what a live LLM call would do.

**Coherent**, in the one sense this module can actually check: every batch draws one shared
"focus" entity (`recipe.seed`-derived, from `FOCUS_POOL`) and every generated line across every
channel carries it, so a batch is not four unrelated lists of sentences.

**Mundane by default.** `recipe.planted_signals` are capped at one per channel — the burial
protocol's own structural limit (`SubstrateGeneratorError` if the recipe schedules more plants
than there are channels to carry them, rather than silently dropping the overflow) — so the bulk
of any batch is ordinary, uninteresting content, checked against `MIN_MUNDANE_FRACTION` below.

**Where believability and measurability conflict, the resolution is recorded, and measurability
wins.** The concrete conflict: a *believable* substrate would scatter each planted signal at an
unpredictable position among the mundane lines, and vary how many plants land in a channel, for
verisimilitude. Doing that would make hit-rate and burial-depth unmeasurable against a known
ground truth. This generator always inserts a channel's (at most one) plant at the fixed midpoint
index of that channel's line list — a less "realistic" scatter, and the trade-off `generate()`
records in its own output (`resolution`) rather than leaving as prose here.
"""

from __future__ import annotations

import random
from typing import Any

from .substrate import SubstrateRecipe, generate_deterministic

SKILL = "substrate-generator"

CHANNELS = ("events", "communications", "hr", "telemetry")

# Round, not fitted: enough lines per channel for a genuine "mostly boring" impression without
# padding a fixture's runtime.
LINES_PER_CHANNEL = 6

# The floor `generate()`'s own output must clear — checked by this module's harness guard and by
# the corpus below, never asserted only in prose.
MIN_MUNDANE_FRACTION = 0.7

FOCUS_POOL = (
    "project-atlas", "project-kestrel", "the-migration", "project-lighthouse",
    "the-onboarding-flow", "project-harbour",
)

RESOLUTION = (
    "measurability wins: a believable substrate would scatter each planted signal at a random, "
    "unpredictable position among unrelated mundane lines, and vary how many plants land in a "
    "channel, for verisimilitude. This generator instead places at most one plant per channel, "
    "always at the fixed midpoint index recorded in plants[].index, so hit rate and burial depth "
    "are measurable against a known ground truth rather than an unrecoverable one "
    "(decision ticket 12, Q1: measurability wins ties)."
)


class SubstrateGeneratorError(RuntimeError):
    """A recipe too thin to cover every channel, or scheduling more plants than channels."""


def _channel_recipe(recipe: SubstrateRecipe, index: int, channel: str, templates: tuple[str, ...]) -> SubstrateRecipe:
    """A per-channel recipe reusing ticket 48's own shape — the seed is derived, not reused
    unmodified, so the four channels do not all draw the identical pseudorandom sequence."""
    return SubstrateRecipe(
        id=f"{recipe.id}-{channel}", seed=recipe.seed + index,
        templates=templates, model_version=recipe.model_version,
    )


def mundane_fraction(batch: dict[str, Any]) -> float:
    total = sum(len(lines) for lines in batch["channels"].values())
    if total == 0:
        return 0.0
    return (total - len(batch.get("plants", []))) / total


def generate(recipe: SubstrateRecipe, lines_per_channel: int = LINES_PER_CHANNEL) -> dict[str, Any]:
    """The skill. One pinned recipe in, one coherent multi-channel substrate out.

    Returns `{"recipe_id", "focus_entity", "channels": {channel: [line, ...]}, "plants":
    [{"channel", "index", "signal"}, ...], "resolution"}`. Regenerating from the identical recipe
    reproduces byte-for-byte — `random.Random(recipe.seed)` and `generate_deterministic`
    (ticket 48) are the only sources of variation, and neither draws external entropy.
    """
    if lines_per_channel < 1:
        raise SubstrateGeneratorError(f"{SKILL}: lines_per_channel must be at least 1")
    if len(recipe.templates) < len(CHANNELS):
        raise SubstrateGeneratorError(
            f"{SKILL}: recipe {recipe.id!r} declares {len(recipe.templates)} template(s), fewer "
            f"than the {len(CHANNELS)} channels a multi-modal substrate needs at least one each for"
        )
    if len(recipe.planted_signals) > len(CHANNELS):
        raise SubstrateGeneratorError(
            f"{SKILL}: recipe {recipe.id!r} schedules {len(recipe.planted_signals)} planted "
            f"signal(s), more than the {len(CHANNELS)} channels — the burial protocol caps at one "
            "plant per channel rather than silently dropping the overflow"
        )

    focus = random.Random(recipe.seed).choice(FOCUS_POOL)

    templates_by_channel: dict[str, list[str]] = {c: [] for c in CHANNELS}
    for i, template in enumerate(recipe.templates):
        templates_by_channel[CHANNELS[i % len(CHANNELS)]].append(template)

    plant_by_channel: dict[str, str] = {}
    for i, signal in enumerate(recipe.planted_signals):
        plant_by_channel[CHANNELS[i % len(CHANNELS)]] = signal

    channels: dict[str, list[str]] = {}
    plants: list[dict[str, Any]] = []
    for i, channel in enumerate(CHANNELS):
        pool = tuple(templates_by_channel[channel])
        channel_recipe = _channel_recipe(recipe, i, channel, pool)
        raw = generate_deterministic(channel_recipe, count=lines_per_channel).decode("utf-8").splitlines()
        lines = [f"[{focus}] {line}" for line in raw]

        plant = plant_by_channel.get(channel)
        if plant is not None:
            index = lines_per_channel // 2
            lines.insert(index, f"[{focus}] {plant}")
            plants.append({"channel": channel, "index": index, "signal": plant})
        channels[channel] = lines

    return {
        "recipe_id": recipe.id,
        "focus_entity": focus,
        "channels": channels,
        "plants": plants,
        "resolution": RESOLUTION,
    }


def generate_from_recipe_yaml(text: str) -> dict[str, Any]:
    """`evaluate()` (`twin/skills.py`) needs `skill_fn(item["input"])` to accept a JSON-digestible
    input, and a `SubstrateRecipe` object is not one; the recipe's own versioned YAML round-trip
    (build ticket 48) is the existing text form, reused rather than inventing a second one only
    for the harness."""
    return generate(SubstrateRecipe.from_yaml(text))


def scorer(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    """A pass needs every expected channel populated, exactly the expected set of planted signals
    present (no more, no fewer — the same discipline `gameplay_lens.scorer` applies), and the
    mundane fraction at or above the expected floor."""
    channels = expected["channels"]
    if set(actual.get("channels", {})) != set(channels):
        return False
    if any(not actual["channels"].get(c) for c in channels):
        return False
    found = sorted(p["signal"] for p in actual.get("plants", []))
    if found != sorted(expected["planted_signals"]):
        return False
    return mundane_fraction(actual) >= float(expected["min_mundane_fraction"])


# -- the labelled corpus: recipes with a known plant schedule, from none to one-per-channel -----

_MUNDANE_TEMPLATES: tuple[str, ...] = (
    "Lunch order chat in #ops.",
    "A long thread about the staging environment.",
    "Expense report chasing.",
    "Sprint planning grumbling.",
    "Someone asking if the deploy window moved again.",
    "A calendar invite nobody can attend gets rescheduled twice.",
    "Routine access request for a shared drive.",
    "Onboarding checklist ticked off for a new starter.",
)

_PLANTED_SIGNALS: tuple[str, ...] = (
    "unusual after-hours access to the finance share",
    "a senior engineer's calendar clears for three unexplained days",
    "a contractor's laptop returned unexpectedly early",
    "an internal all-hands abruptly cancelled with no reason given",
)


def labelled_corpus() -> list[dict[str, Any]]:
    """Three recipes, plant count 0 through 4 (one per channel, the structural cap): the negative
    case (nothing planted, still multi-channel and mundane), a sparse case, and the dense case
    that saturates every channel at once."""
    items = []
    for item_id, seed, planted in (
        ("quiet-week", 101, ()),
        ("sparse-plants", 202, _PLANTED_SIGNALS[:2]),
        ("dense-plants", 303, _PLANTED_SIGNALS),
    ):
        recipe = SubstrateRecipe(
            id=f"ops-{item_id}", seed=seed, templates=_MUNDANE_TEMPLATES,
            model_version="toy-model-v1", planted_signals=planted,
        )
        items.append(
            {
                "id": item_id,
                "input": recipe.to_yaml(),
                "expected": {
                    "channels": list(CHANNELS),
                    "planted_signals": list(planted),
                    "min_mundane_fraction": MIN_MUNDANE_FRACTION,
                },
            }
        )
    return items
