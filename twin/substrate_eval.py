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

**Build ticket 87 adds two more dimensions, closing decision ticket 12 AC 3 and AC 6.**
`plant_difficulty_spread` is AC 3's own remaining clause: "distribution of difficulty" asks
whether a batch's *plants* — plural — span a genuine spread, not merely whether their mean clears
a band; a batch where every plant is equally (trivially) findable passes the mean and fails the
spread. `contamination` is AC 6's anti-contamination measure: a small, named blocklist of real
companies, events and people (`KNOWN_REAL_ENTITIES`) — deliberately distinct from
`twin/scoring.py`'s Enron-as-control discount, which prices memorisation on the real-history
backtest suite and has no view of this module's synthetic output at all. The blocklist is checked
against a batch's *free-running* content only: `spine.anchor()`'s own insertions are expected to
name the real subject verbatim (that is what anchoring is), so scanning them would flag the
consistency mechanism decision ticket 12 Q3 requires, not a leak. `refuse_if_contaminated()` is
the harder AC 7 gate sharing this same scan: not a target band a batch can still "pass" while
carrying a hit, but a refusal, the same shape `schema.refuse_special_category` uses for Article 9.
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


def _per_plant_difficulty_scores(batch: dict[str, Any]) -> list[float]:
    """One difficulty score per plant in `batch`, in `batch["plants"]` order — the shared
    computation `plant_difficulty` (the mean) and `plant_difficulty_spread` (the distribution)
    both read, so the two dimensions can never quietly disagree about one plant's own score.
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
    return scores


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
    scores = _per_plant_difficulty_scores(batch)
    return sum(scores) / len(scores) if scores else 0.0


def plant_difficulty_spread(batch: dict[str, Any]) -> float:
    """The spread (max minus min) across a batch's own per-plant difficulty scores — decision
    ticket 12 AC 3's "distribution of difficulty", not merely a mean landing in a band. A batch
    where every plant is equally easy (or equally hard) to find has a real mean and zero spread —
    passing `plant_difficulty` while failing this dimension outright, which is the gap this metric
    exists to catch: `plant_difficulty` alone cannot distinguish "a genuine spread of difficulty"
    from "every plant at the same difficulty, by chance the mean of a fair band". Fewer than two
    plants have nothing to spread and score `0.0`, the same degenerate-case shape
    `plant_difficulty` already uses for zero plants.
    """
    scores = _per_plant_difficulty_scores(batch)
    if len(scores) < 2:
        return 0.0
    return max(scores) - min(scores)


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


# -- contamination: a small, named blocklist, distinct from the Enron-as-control discount --------

# The org roster already committed across the backtest and flagship fixtures (`twin/fixtures.py`)
# — a small, known-real list, exactly what AC 6 asks for, reused rather than invented a second
# time. Not the Enron-as-control mechanism (`twin/scoring.py`): that prices memorisation on the
# real-history backtest suite; this blocklist catches a *synthetic* batch parametrically leaking or
# closely resembling a real company or event it was never anchored to.
KNOWN_REAL_ORGS: tuple[str, ...] = (
    "Carillion", "Enron", "Wirecard", "NMC Health", "Kodak", "Netflix", "Intel", "Maersk",
    "AstraZeneca", "Sanofi", "Royal Mail",
)

# Real, identifiable people, publicly tied to the same real, dated corporate events the backtest
# roster already covers — AC 7's "real, identifiable person", not a fabricated stand-in. None of
# these names is ever authored into this codebase's own generated content; they exist only as
# blocklist entries a planted collision is checked against (see `tests/test_substrate_eval.py`).
KNOWN_REAL_PEOPLE: tuple[str, ...] = ("Jeffrey Skilling", "Markus Braun", "Richard Howson")

KNOWN_REAL_ENTITIES: tuple[str, ...] = KNOWN_REAL_ORGS + KNOWN_REAL_PEOPLE

_ENTITY_PATTERNS = tuple((entity, re.compile(rf"\b{re.escape(entity)}\b", re.IGNORECASE)) for entity in KNOWN_REAL_ENTITIES)


class ContaminationError(SubstrateEvalError):
    """A substrate batch names a real, identifiable company, event or person outside the anchored
    spine (decision ticket 12 AC 6/7)."""


def contamination_hits(batch: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    """Every `(channel, index, entity, line)` where a free-running line names a
    `KNOWN_REAL_ENTITIES` entry.

    Lines identical to one of `batch["anchored"]`'s own spine-fact statements are skipped —
    `spine.anchor()` inserts the real subject's own dated facts verbatim, by design (decision
    ticket 12 Q3's "anchored where dated"), and scanning them would flag the very consistency
    mechanism this project relies on rather than a leak. `batch.get("anchored", [])` is empty for
    a batch nobody has anchored yet, so every line is scanned in that case — the correct behaviour
    for the generator's own raw output.
    """
    anchored_statements = {fact["statement"] for fact in batch.get("anchored", [])}
    hits: list[dict[str, Any]] = []
    for channel, lines in batch.get("channels", {}).items():
        for index, line in enumerate(lines):
            if line in anchored_statements:
                continue
            for entity, pattern in _ENTITY_PATTERNS:
                if pattern.search(line):
                    hits.append({"channel": channel, "index": index, "entity": entity, "line": line})
    return tuple(hits)


def contamination(batch: dict[str, Any]) -> float:
    """The count of `contamination_hits`, as a float so it reads like every other dimension's
    value. `0.0` is the only value inside `TARGETS["contamination"]` — any hit at all is outside
    the declared band, the same all-or-nothing shape `spine_consistency`'s `(1.0, 1.0)` target
    uses for its own zero-tolerance property.
    """
    return float(len(contamination_hits(batch)))


def refuse_if_contaminated(batch: dict[str, Any]) -> None:
    """The AC 7 gate: not a target band a batch can still be reported as "failing" while shipping
    anyway, but a refusal — the same shape `schema.refuse_special_category` uses for Article 9,
    called before a batch is committed to an artefact (`substrate_report.report()`).
    """
    hits = contamination_hits(batch)
    if hits:
        names = sorted({h["entity"] for h in hits})
        raise ContaminationError(
            f"substrate batch names real, identifiable entit{'y' if len(names) == 1 else 'ies'} "
            f"{', '.join(names)} outside the anchored spine — refused before commit (decision "
            "ticket 12 AC 6/7)"
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


# -- the seven declared, targeted dimensions --------------------------------------------------------

# Round bands, not fitted to one batch: each has real headroom on both sides, checked in
# `tests/test_substrate_eval.py` against genuine positive and negative controls (an
# over-anchored/trivially-findable/falsely-balanced/thin-volume/uniform-difficulty/contaminated
# batch each fails the dimension it names), not merely against the tuned default landing inside it.
TARGETS: dict[str, tuple[float, float]] = {
    "signal_to_noise": (0.05, 0.25),
    "plant_difficulty": (0.05, 0.5),
    "plant_difficulty_spread": (0.05, 1.0),
    "spine_consistency": (1.0, 1.0),
    "reporting_asymmetry": (0.6, 0.95),
    "mundanity": (MIN_MUNDANE_FRACTION, 1.0),
    "contamination": (0.0, 0.0),
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
    ("every plant sitting at a uniform difficulty rather than a genuine spread — no plant harder to find than another", "plant_difficulty_spread"),
    ("a falsely balanced positive/negative documentation split that erases the record's real negativity bias", "reporting_asymmetry"),
    ("volume too thin for boring content to genuinely bury a plant, or to keep plant density proportionate", "mundanity"),
    ("generated content parametrically leaking or closely resembling a real named company, event or person outside the anchored spine", "contamination"),
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
    """The seven declared dimensions, each a real value computed from `batch` against its own
    target band — `batch` is anchored to `spine` at `checkpoint` internally (additive, per
    `spine.anchor`), so a caller hands over the generator's raw output and gets every dimension
    back, spine consistency included, without a second anchoring step of its own.
    """
    anchored = spine_mod.anchor(batch, spine, checkpoint)
    values = {
        "signal_to_noise": signal_to_noise(anchored),
        "plant_difficulty": plant_difficulty(anchored),
        "plant_difficulty_spread": plant_difficulty_spread(anchored),
        "spine_consistency": spine_consistency(anchored, spine, checkpoint),
        "reporting_asymmetry": reporting_asymmetry(anchored),
        "mundanity": mundane_fraction(anchored),
        "contamination": contamination(anchored),
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
    """Tune the generator's template mix against the seven declared targets — a real, iterative
    loop, not a single call the caller eyeballs. `signal_to_noise`, `spine_consistency` and
    `mundanity` do not move with `negative_fraction` (they are fixed by plant count and channel
    structure, held constant here); `contamination` does not move either (the blocklist scan has
    nothing to do with polarity mix); `reporting_asymmetry` does, and a balanced starting pool
    (`start_negative_fraction=0.5`) measurably misses its target — the real gap this loop exists to
    close, not a strawman that happens to pass on iteration one. Each step raises
    `negative_fraction` by `step` and regenerates; stops the moment every dimension is within
    target, or reports `converged=False` after `max_iters`.
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
