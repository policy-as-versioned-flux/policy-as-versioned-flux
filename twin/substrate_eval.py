"""The substrate fidelity eval suite (build ticket 51, decision ticket 12): **fidelity is defined
and tuned by measurement, not asserted in prose.**

Decision ticket 12's own resolution names the eval suite as the concrete form of Q1's
"measurability wins ties": "Realism is *encoded as evals and tuned*... Evals measure at least:
signal-to-noise ratio, planted-signal difficulty, spine consistency, reporting asymmetry, and
volume/mundanity." Ticket 49 (`substrate_generator.py`) built the generator; ticket 50
(`spine.py`) built the anchoring the third dimension needs. This ticket is the fifth piece: a
**declared target per dimension**, a **current value computed from real output**, and a **tuning
loop** that closes the gap between them — not a manual eyeball, and not a claim the earlier
tickets already made true by construction.

**The record's negativity bias is modelled here rather than as a separate concern** (decision
ticket 12 Q3c, spec story 60): "reporting asymmetry as measured and negativity bias as produced
are the same asymmetry" — one metric (`reporting_asymmetry`), not two tickets fighting over one
property. The mundane-only template pool `substrate_generator.py` ships with carries no polarity
vocabulary at all (lunch orders, staging threads), so a batch generated from it alone measures
`reporting_asymmetry == 0.0` — a real, honest failure against a target that says the record should
skew *negative*, not a strawman. Closing that gap is exactly what `tune()` demonstrates: mixing in
a deliberately negative-skewed pool of authored content (`NEGATIVE_TEMPLATES` outweighing
`POSITIVE_TEMPLATES`, this module's own — the generator's committed template contract from ticket
49 is untouched) until the measured asymmetry clears its target band.

`ponytail:` `classify_polarity()` is a keyword scan, the same stand-in-for-judgement shape
`signal_classify.py`'s docstring names explicitly. What is being proven is that a *declared,
targeted, measured* metric exists and a tuning loop closes a real gap against it — not that this
particular keyword list is a good sentiment classifier. Upgrade path: swap the classifier body,
nothing else here changes, because every metric function reads a bare batch dict.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from typing import Any

from . import spine as spine_mod
from .spine import Spine
from .substrate import SubstrateRecipe
from .substrate_generator import MIN_MUNDANE_FRACTION, generate, mundane_fraction

MODEL_VERSION = "toy-model-v1"
POOL_SIZE = 12  # a multiple of len(CHANNELS): every channel's own slice is representative, not lopsided.


class SubstrateEvalError(RuntimeError):
    pass


# -- reporting asymmetry / negativity bias: the record's real, deliberate skew -------------------

# Deliberately outnumbered 6:3 in the raw pools below — decision ticket 12 Q3c's "bad news
# generates post-mortems... good decisions generate a quiet year" reproduced as authored content,
# not idealised into balance. `_asymmetric_templates()` mixes them at a tunable ratio; these two
# tuples are the ingredients, not the recipe.
NEGATIVE_TEMPLATES: tuple[str, ...] = (
    "An incident review opens after last night's brief service outage.",
    "The vendor contract is cancelled after repeated missed deadlines.",
    "A customer complaint escalates into a formal investigation.",
    "Quarterly numbers show a shortfall against the plan, prompting a write-down.",
    "A senior engineer's resignation is confirmed after months of friction.",
    "The rollout is delayed again, the third slip this quarter.",
)
POSITIVE_TEMPLATES: tuple[str, ...] = (
    "The team celebrates a record quarter after the launch.",
    "A milestone is reached ahead of schedule, and the lead is praised.",
    "The pilot's early growth surprises even the sponsors.",
)

_NEGATIVE_KEYWORDS = (
    "incident", "outage", "cancelled", "missed", "complaint", "investigation", "shortfall",
    "write-down", "resign", "friction", "delayed", "slip",
)
_POSITIVE_KEYWORDS = ("record", "launch", "milestone", "praised", "growth", "surprises")


def classify_polarity(line: str) -> str:
    """`negative`, `positive`, or `neutral` — a keyword scan, the same stand-in-for-judgement
    shape `signal_classify._steep` uses (see module docstring)."""
    haystack = line.lower()
    if any(keyword in haystack for keyword in _NEGATIVE_KEYWORDS):
        return "negative"
    if any(keyword in haystack for keyword in _POSITIVE_KEYWORDS):
        return "positive"
    return "neutral"


def reporting_asymmetry(batch: dict[str, Any]) -> float:
    """The negative fraction among every polarity-classified line (plants included — a planted
    anomaly is itself part of "what got documented"). Neutral lines (the bulk of ordinary
    mundane content) do not enter the ratio, the same way a sentiment split ignores what nobody
    reacted to. Zero classified lines is the degenerate case (a purely neutral corpus asserts no
    asymmetry at all) and scores `0.0` — a real failure against any target above zero, not a
    vacuous pass.
    """
    counts = {"negative": 0, "positive": 0}
    for lines in batch.get("channels", {}).values():
        for line in lines:
            polarity = classify_polarity(line)
            if polarity in counts:
                counts[polarity] += 1
    total = counts["negative"] + counts["positive"]
    return counts["negative"] / total if total else 0.0


def _asymmetric_templates(negative_fraction: float, size: int = POOL_SIZE) -> tuple[str, ...]:
    """`size` lines drawn from `NEGATIVE_TEMPLATES`/`POSITIVE_TEMPLATES` at `negative_fraction`,
    cycling each pool to fill its share. `substrate_generator.generate()` round-robins a recipe's
    `templates` across the four channels by *position* (`templates[i % len(CHANNELS)]`), so a
    pool grouped negative-then-positive still lands each channel a representative slice as long
    as `size` is a multiple of `len(CHANNELS)` — no interleaving needed.
    """
    if not 0.0 <= negative_fraction <= 1.0:
        raise SubstrateEvalError(f"negative_fraction {negative_fraction} is not a fraction in [0, 1]")
    negative_count = round(size * negative_fraction)
    positive_count = size - negative_count
    negative = list(itertools.islice(itertools.cycle(NEGATIVE_TEMPLATES), negative_count))
    positive = list(itertools.islice(itertools.cycle(POSITIVE_TEMPLATES), positive_count))
    return tuple(negative + positive)


# -- planted-signal difficulty: not trivially findable, not impossible ---------------------------

_STOPWORDS = frozenset(
    ("a", "an", "and", "as", "at", "be", "by", "for", "from", "given", "in", "is", "it", "no",
     "of", "on", "or", "reason", "that", "the", "this", "to", "with", "after", "again")
)
_FOCUS_PREFIX = re.compile(r"^\[[^\]]*\]\s*")


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) >= 2 and w not in _STOPWORDS}


def plant_difficulty(batch: dict[str, Any]) -> float:
    """Mean, across every plant in `batch`, of how much of the plant line's own vocabulary
    (after stripping the shared focus-entity prefix) also appears in its channel's *other*
    lines. `0.0` means the plant shares no vocabulary at all with its surroundings — foreign,
    and trivially findable by a lexical-outlier scan. `1.0` means the plant is lexically
    indistinguishable from its context — the burial protocol's own forbidden extreme, decision
    ticket 12 Q3's "actively dangerous" over-anchoring case in miniature. A batch with no plants
    scores `0.0`: there is nothing to measure difficulty of, which is itself the degenerate,
    unfair-test condition (see `UNFAIR_TEST_CONDITIONS`).
    """
    scores: list[float] = []
    for plant in batch.get("plants", []):
        channel_lines = batch["channels"][plant["channel"]]
        plant_line = channel_lines[plant["index"]]
        plant_tokens = _tokens(_FOCUS_PREFIX.sub("", plant_line))
        if not plant_tokens:
            scores.append(0.0)
            continue
        context_tokens: set[str] = set()
        for i, line in enumerate(channel_lines):
            if i != plant["index"]:
                context_tokens |= _tokens(_FOCUS_PREFIX.sub("", line))
        scores.append(len(plant_tokens & context_tokens) / len(plant_tokens))
    return sum(scores) / len(scores) if scores else 0.0


# Camouflaged deliberately: each borrows a word or two from NEGATIVE_TEMPLATES's own vocabulary
# ("incident review", "resignation", "contract", "cancelled", "complaint") rather than describing
# the anomaly in a lexically foreign register — the tuning story `tests/test_substrate_eval.py`
# demonstrates directly against `UNCAMOUFLAGED_PLANTED_SIGNALS` below, its less-buried predecessor.
PLANTED_SIGNALS: tuple[str, ...] = (
    "an unusual incident review opens after hours, examining access to the finance share",
    "a senior engineer's calendar clears for three unexplained days, following an earlier resignation",
    "a contractor's laptop is returned early, days after the vendor contract review",
    "an internal all-hands is cancelled abruptly, with no reason given after a recent complaint",
)

# The pre-camouflage wording: shares almost no vocabulary with the generated pools, so
# `plant_difficulty` on a batch planted with these scores near zero — trivially findable, the
# negative control `tests/test_substrate_eval.py` runs against `PLANTED_SIGNALS` above.
UNCAMOUFLAGED_PLANTED_SIGNALS: tuple[str, ...] = (
    "unusual after-hours access to the finance share",
    "a senior engineer's calendar clears for three unexplained days",
    "a contractor's laptop returned unexpectedly early",
    "an internal all-hands abruptly cancelled with no reason given",
)


# -- signal-to-noise and spine consistency: thin wrappers over ticket 49/50's own metrics --------


def signal_to_noise(batch: dict[str, Any]) -> float:
    """The proportion of a batch's own lines that are planted signal, not mundane or anchored
    content — the complement `substrate_generator.mundane_fraction` already computes, named as
    its own declared-target dimension rather than read only as "the mundane floor's complement"."""
    total = sum(len(lines) for lines in batch.get("channels", {}).values())
    return len(batch.get("plants", [])) / total if total else 0.0


def spine_consistency(batch: dict[str, Any], spine: Spine, checkpoint: str) -> float:
    """The fraction of every spine fact knowable by `checkpoint` that is present, verbatim,
    somewhere in `batch` — `spine.reconcile`'s own check, as a graded fraction rather than an
    all-or-nothing refusal, so a partially-reconciled batch reports *how* inconsistent it is
    rather than only that it is. A spine with nothing knowable yet scores `1.0`: vacuously
    consistent, nothing to contradict.
    """
    known = spine.at(checkpoint)
    if not known:
        return 1.0
    present = {line for lines in batch.get("channels", {}).values() for line in lines}
    return sum(1 for fact in known if fact.statement in present) / len(known)


# -- the five declared, targeted dimensions -------------------------------------------------------

# Round bands, not fitted to one batch: each has real headroom on both sides, checked in
# `tests/test_substrate_eval.py` against genuine positive and negative controls (an
# over-anchored/trivially-findable/falsely-balanced/thin-volume batch each fails the dimension it
# names), not merely against the tuned default landing inside it.
TARGETS: dict[str, tuple[float, float]] = {
    "signal_to_noise": (0.05, 0.25),
    "plant_difficulty": (0.05, 0.5),
    "spine_consistency": (1.0, 1.0),
    "reporting_asymmetry": (0.6, 0.95),
    "mundanity": (MIN_MUNDANE_FRACTION, 1.0),
}

# Decision ticket 12's own unfair-test list (AC 2), each clause paired with the dimension whose
# target catches it — the "stated list" the acceptance criterion asks for, checked against real
# batches in `tests/test_substrate_eval.py` (not left as prose alone) rather than guessed: the
# thin-volume clause fails BOTH `mundanity` and `signal_to_noise` on a real construction (a plant
# in every channel at `lines_per_channel=1`, empirically confirmed, not merely asserted plausible).
# "Over-anchored noise" is named for completeness — decision ticket 12 Q3's own attack — but it is
# `spine.diff_against_spine` (build ticket 50) that catches it, not a new dimension here: an
# over-anchored batch's spine facts are, tautologically, perfectly consistent with the spine, so
# `spine_consistency` alone reads it as clean. `spine_consistency`'s own failure mode is the
# opposite one: silent drift, an un-anchored batch quietly contradicting a fact it should carry.
UNFAIR_TEST_CONDITIONS: tuple[tuple[str, str], ...] = (
    ("over-anchored noise, so a diff against the spine recovers the plants directly (caught by build ticket 50's diff_against_spine, not a dimension here)", "spine.diff_against_spine"),
    ("the substrate silently drifting from a dated public fact it must never contradict", "spine_consistency"),
    ("a planted signal trivially findable — foreign vocabulary, no burial in its surroundings", "plant_difficulty"),
    ("a falsely balanced positive/negative documentation split that erases the record's real negativity bias", "reporting_asymmetry"),
    ("volume too thin for boring content to genuinely bury a plant, or to keep plant density proportionate", "mundanity"),
)


@dataclass(frozen=True)
class FidelityMetric:
    name: str
    target_low: float
    target_high: float
    value: float

    @property
    def within_target(self) -> bool:
        return self.target_low <= self.value <= self.target_high

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "target_low": self.target_low, "target_high": self.target_high,
            "value": self.value, "within_target": self.within_target,
        }


def evaluate_fidelity(batch: dict[str, Any], spine: Spine, checkpoint: str) -> tuple[FidelityMetric, ...]:
    """The five declared dimensions, each a real value computed from `batch` against its own
    target band — `batch` is anchored to `spine` at `checkpoint` internally (additive, per
    `spine.anchor`), so a caller hands over the generator's raw output and gets every dimension
    back, spine consistency included, without a second anchoring step of its own.
    """
    anchored = spine_mod.anchor(batch, spine, checkpoint)
    values = {
        "signal_to_noise": signal_to_noise(anchored),
        "plant_difficulty": plant_difficulty(anchored),
        "spine_consistency": spine_consistency(anchored, spine, checkpoint),
        "reporting_asymmetry": reporting_asymmetry(anchored),
        "mundanity": mundane_fraction(anchored),
    }
    return tuple(
        FidelityMetric(name=name, target_low=lo, target_high=hi, value=values[name])
        for name, (lo, hi) in TARGETS.items()
    )


def passes(metrics: tuple[FidelityMetric, ...]) -> bool:
    return all(m.within_target for m in metrics)


# -- the tuning loop: a supported loop, not a manual eyeball --------------------------------------


@dataclass(frozen=True)
class TuningStep:
    negative_fraction: float
    metrics: tuple[FidelityMetric, ...]

    @property
    def passes(self) -> bool:
        return passes(self.metrics)


@dataclass(frozen=True)
class TuningResult:
    converged: bool
    steps: tuple[TuningStep, ...]

    @property
    def iterations(self) -> int:
        return len(self.steps)

    @property
    def final(self) -> TuningStep:
        return self.steps[-1]


def _recipe_for(negative_fraction: float, planted_signals: tuple[str, ...], seed: int) -> SubstrateRecipe:
    return SubstrateRecipe(
        id="substrate-eval-tuning", seed=seed,
        templates=_asymmetric_templates(negative_fraction),
        model_version=MODEL_VERSION, planted_signals=planted_signals,
    )


def tune(
    spine: Spine,
    checkpoint: str,
    planted_signals: tuple[str, ...] = PLANTED_SIGNALS,
    start_negative_fraction: float = 0.5,
    step: float = 0.05,
    max_iters: int = 20,
    seed: int = 42,
) -> TuningResult:
    """Tune the generator's template mix against the five declared targets — a real, iterative
    loop, not a single call the caller eyeballs. `signal_to_noise`, `plant_difficulty`,
    `spine_consistency` and `mundanity` do not move with `negative_fraction` (they are fixed by
    plant count, wording and channel structure, all held constant here); `reporting_asymmetry`
    does, and a balanced starting pool (`start_negative_fraction=0.5`) measurably misses its
    target — the real gap this loop exists to close, not a strawman that happens to pass on
    iteration one. Each step raises `negative_fraction` by `step` and regenerates; stops the
    moment every dimension is within target, or reports `converged=False` after `max_iters`.
    """
    steps: list[TuningStep] = []
    fraction = start_negative_fraction
    for _ in range(max_iters):
        batch = generate(_recipe_for(fraction, planted_signals, seed))
        metrics = evaluate_fidelity(batch, spine, checkpoint)
        this_step = TuningStep(negative_fraction=fraction, metrics=metrics)
        steps.append(this_step)
        if this_step.passes:
            return TuningResult(converged=True, steps=tuple(steps))
        fraction = min(1.0, fraction + step)
    return TuningResult(converged=False, steps=tuple(steps))
