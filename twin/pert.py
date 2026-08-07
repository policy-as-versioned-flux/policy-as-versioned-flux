"""PERT triples: the calibrated range, its analytic moments, and seeded sampling.

Build ticket 23, from decision ticket 08 (Q1). One estimation discipline (Hubbard calibration),
one propagation engine (Monte-Carlo), across both the causal layer and the £ engine — not two
epistemologies bolted together.

**Compose by sampling, never by multiplying point estimates.** A product of modes is not the mode
of a product, and averaging the uncertainty away is the move that turns a wide honest range into a
confident wrong number.

The triple is a **90% credible interval with a most-likely value**. `twin/calibration.md` is the
authoring discipline behind it, and `procedure()` below reads that file and requires its steps by
name — so a step that disappears from the document fails here rather than lapsing quietly. Every
artefact that samples a triple pins the procedure by digest.

This module sits below the £ engine and below propagation, and knows about neither. Pricing takes
a distribution as input and does not care where it came from, which is what lets the £ chain run
parallel to the causal chain instead of queueing behind it.
"""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import PACKAGE_DIR
from .canon import sha256_hex

CALIBRATION_PATH = PACKAGE_DIR / "calibration.md"

# Required by name, for the reason the constraint set's positions are: "presumably covered" is how
# a step disappears. The order is the order the document runs them in.
REQUIRED_STEPS = (
    "absurdity-test",
    "equivalent-bet",
    "name-the-reference-class",
    "state-the-decomposition",
    "record-the-estimator-and-the-date",
)

_STEP = re.compile(r"^###\s+step:\s*([a-z0-9-]+)\s*$", re.M)

# The declared precision of every sampled figure in an artefact, matching the scoring rules'
# reason: a Monte-Carlo mean is floating-point arithmetic over thousands of draws and the last
# units in the last place are not worth asserting. Declared in the format, never in the comparison.
SIGNIFICANT_DIGITS = 12


class PertError(ValueError):
    """A triple that is not a triple, or an authoring discipline that has lost a step."""


def quantise(value: float) -> float:
    """Round to `SIGNIFICANT_DIGITS` significant decimal digits, and refuse a non-finite result.

    Every derived figure in this module funnels through here, which is why the finiteness guard
    lives here. An authored cost is bounded only by *finite*, so a wide enough triple overflows in
    the variance before it overflows anywhere else — and `canonical_json` refuses to serialise the
    infinity, several steps later, as a bare `ValueError` that reads as a crash rather than as a
    refusal. A number that has stopped meaning anything should be refused where it stops.
    """
    if not math.isfinite(value):
        raise PertError(
            f"a derived figure came out as {value}. The authored range is wide enough to overflow "
            "the arithmetic, so the result carries no information; narrow the triple rather than "
            "reading an infinity as a number."
        )
    return float(f"{value:.{SIGNIFICANT_DIGITS - 1}e}")


def procedure(path: Path | None = None) -> dict[str, Any]:
    """The calibration discipline, pinned by digest, with its steps required by name.

    Validated rather than trusted, for the reason the ladder and the constraint set are: a
    procedure that has quietly lost its widening step still looks documented.
    """
    source = path or CALIBRATION_PATH
    raw = source.read_bytes()
    found = tuple(_STEP.findall(raw.decode("utf-8")))
    missing = [step for step in REQUIRED_STEPS if step not in found]
    if missing:
        raise PertError(
            f"{source}: the calibration procedure declares no {', '.join(missing)}. Each step is "
            "required by name, because a discipline with a missing step is not a discipline."
        )
    return {
        "document": source.name,
        "sha256": sha256_hex(raw),
        "interval": "90% credible interval with a most-likely value",
        "steps": list(found),
    }


@dataclass(frozen=True)
class Triple:
    """A calibrated range. `low <= mode <= high`, and nothing here collapses it to a point."""

    low: float
    mode: float
    high: float

    def __post_init__(self) -> None:
        for name, value in (("min", self.low), ("mode", self.mode), ("max", self.high)):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise PertError(f"a triple's {name} is {value!r}, which is not a finite number")
        if not self.low <= self.mode <= self.high:
            raise PertError(f"expected min <= mode <= max, got {self.low} / {self.mode} / {self.high}")

    @classmethod
    def of(cls, triple: dict[str, Any]) -> "Triple":
        """From the authored `min`/`mode`/`max` mapping the schema validates."""
        try:
            return cls(float(triple["min"]), float(triple["mode"]), float(triple["max"]))
        except (KeyError, TypeError, ValueError) as exc:
            # `ValueError` too: `float("x")` raises it, and a bare one escaping here would reach
            # the CLI as a traceback rather than as a sentence.
            raise PertError(f"{triple!r} is not a min/mode/max triple") from exc

    @property
    def degenerate(self) -> bool:
        """No width. Permitted, and flagged wherever it is read — never silently a range."""
        return self.low == self.mode == self.high

    @property
    def mean(self) -> float:
        """The PERT mean, `(min + 4*mode + max) / 6`. Analytic, so a property test has a yardstick."""
        return (self.low + 4.0 * self.mode + self.high) / 6.0

    @property
    def variance(self) -> float:
        """The PERT variance, `(mean - min) * (max - mean) / 7`."""
        return (self.mean - self.low) * (self.high - self.mean) / 7.0

    @property
    def shape(self) -> tuple[float, float]:
        """The underlying Beta shape parameters, `alpha` and `beta`. They always sum to 6."""
        if self.degenerate:
            raise PertError("a degenerate triple has no Beta shape; it is a point")
        width = self.high - self.low
        return (
            1.0 + 4.0 * (self.mode - self.low) / width,
            1.0 + 4.0 * (self.high - self.mode) / width,
        )

    def raw_moment(self, k: int) -> float:
        """`E[X^k]`, analytically. The yardstick the sampled figures are checked against.

        Needed by shared-ancestry aggregation (build ticket 21): when two paths share an edge,
        the expectation of their product carries that edge **squared**, and the difference
        between `E[X^2]` and `E[X]^2` is exactly the double-counting a naive independence
        assumption would invent. Analytic rather than sampled, because the pocket-org worksheet
        has to be hand-checkable and a Monte-Carlo estimate is not.

        `X = min + w*B` with `B ~ Beta(alpha, beta)` and `alpha + beta = 6`, so
        `E[B^j] = prod (alpha + i) / (6 + i)` and the binomial expansion does the rest.
        `k = 1` recovers the PERT mean and `k = 2` recovers the PERT variance, which is what
        makes this a yardstick rather than a second opinion.
        """
        if k < 0:
            raise PertError(f"a raw moment is of order zero or more, not {k}")
        if self.degenerate:
            return float(self.low) ** k
        alpha, _ = self.shape
        width = self.high - self.low
        total = 0.0
        beta_moment = 1.0
        for j in range(k + 1):
            if j:
                beta_moment *= (alpha + j - 1) / (6.0 + j - 1)
            total += math.comb(k, j) * self.low ** (k - j) * width**j * beta_moment
        return total

    def sample(self, rng: random.Random) -> float:
        """One draw. A degenerate triple draws its point and consumes no randomness."""
        if self.degenerate:
            return self.low
        alpha, beta = self.shape
        return self.low + (self.high - self.low) * rng.betavariate(alpha, beta)

    def times(self, other: "Triple") -> "Triple":
        """Point-wise composition of two ranges.

        Correct only for non-negative elasticities, which is what the schema admits: an elasticity
        is a magnitude in the unit interval and the *sign* of an effect travels on the edge, never
        inside the range. It is the **un-attenuated** composition, and it is not the distribution
        of the product — that is what sampling is for, and both are reported side by side so the
        difference between them is visible rather than assumed away.
        """
        return Triple(self.low * other.low, self.mode * other.mode, self.high * other.high)

    def scaled(self, factor: float) -> "Triple":
        return Triple(self.low * factor, self.mode * factor, self.high * factor)

    def as_dict(self) -> dict[str, Any]:
        return {"min": self.low, "mode": self.mode, "max": self.high}

    def moments(self) -> dict[str, Any]:
        """The analytic moments, beside the triple. Never a substitute for it.

        The three points are quantised too. The declared precision applies to the whole figure or
        it is not a declared precision — a triple emitted as `0.22399999999999998` beside a mean
        rounded to twelve digits says the format holds for half of itself.
        """
        return {
            "min": quantise(self.low),
            "mode": quantise(self.mode),
            "max": quantise(self.high),
            "mean": quantise(self.mean),
            "variance": quantise(self.variance),
            "degenerate": self.degenerate,
        }


def stream(seed: str) -> random.Random:
    """A named, independent random stream.

    Seeded by **name** rather than by draw order, so a path's numbers do not depend on how the
    traversal reached it. Two runs that visit the graph in a different order still produce
    identical bytes, which is what `identical_pins_identical_bytes` asks of anything that samples.
    """
    return random.Random(seed)


def sampler(seed: str, draws: int, seeded_by: str) -> dict[str, Any]:
    """How a sampled figure was produced, as it appears in an artefact.

    Here rather than in each caller because it describes **this module's** sampler: two callers
    with their own copy of the prose is two places for it to stop being true.
    """
    return {
        "engine": "python random.Random (Mersenne Twister), Beta variates for PERT",
        "seed": seed,
        "draws": draws,
        "seeded_by": seeded_by,
        "reproducible_within": (
            "one interpreter version — the Beta variate is the standard library's, so a different "
            "Python may draw a different stream from the same seed"
        ),
        "significant_digits": SIGNIFICANT_DIGITS,
    }


def summarise(draws: list[float]) -> dict[str, Any]:
    """What a Monte-Carlo run reports: a spread, never a single number.

    `ponytail:` nearest-rank quantiles on a sorted list rather than an interpolating estimator. The
    draw count is large and fixed, so the difference is below the declared precision; swap in an
    interpolating quantile if a caller ever needs a small-sample one.
    """
    if not draws:
        raise PertError("no draws to summarise")
    ordered = sorted(draws)
    return {
        "draws": len(ordered),
        "mean": quantise(sum(ordered) / len(ordered)),
        "p05": quantise(_quantile(ordered, 0.05)),
        "p50": quantise(_quantile(ordered, 0.50)),
        "p95": quantise(_quantile(ordered, 0.95)),
        "min": quantise(ordered[0]),
        "max": quantise(ordered[-1]),
    }


def _quantile(ordered: list[float], q: float) -> float:
    index = min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))
    return ordered[index]
