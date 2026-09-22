"""How many labelled items a threshold needs before a score against it means anything.

Eco-system ticket 112. `twin/skill-thresholds.yaml` states one `min_items` per threshold, and
`twin/skills.py` refuses a stated number this module does not derive. A run on fewer items than
the minimum reports "not measurable", a third outcome that is neither a pass nor a failure.

THE METHOD comes from the Laya map's ticket 03 (`.scratch/laya-loophole/corpus/required_size.py`),
moved here because the gate runs it and `.scratch/` is not code the gate may depend on.

1. **Name the effect the threshold must detect.** Every heuristic scores 1.000 on its own corpus.
   A threshold exists to catch a fall from there to the floor, so the effect is `1 - threshold`.
2. **Size n so the standard error sits at half that effect.** The binomial variance is taken at
   its worst inside the band the threshold guards, `[threshold, 1]`: that is `p = threshold` for a
   bar at or above 0.5, and `p = 0.5` below it.
3. **A perfect score must be able to clear the threshold.** The rule of three bounds true accuracy
   at `1 - 3/n` (95%) after n successes in n trials. Below `3 / (1 - threshold)` even a perfect
   score is consistent with a skill under the bar.

The minimum is the larger of routes 2 and 3. Both are printed, so the binding one is visible.

**Per-bin.** Ticket 03 sized an expected-calibration-error estimate, which is binned, so its honest
number was the whole-set number times the bin count. The harness grades a plain proportion with one
bin, so the per-bin number equals the whole-set number here. `ESTIMATOR_BINS` says so rather than
leaving the reader to wonder where the multiplier went. A binned metric would raise it.

**Never imported.** The prior art's "~50 resolved forecasts" traces to one research document with
no formula (Laya map ticket 10). No threshold here derives 50.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any

RULE_OF_THREE = 3
# The standard error the minimum buys, as a fraction of the effect it must detect.
SE_FRACTION_OF_EFFECT = Fraction(1, 2)
# The harness's score is one proportion over the whole corpus: one bin.
ESTIMATOR_BINS = 1


class CorpusSizeError(ValueError):
    """A threshold no finite corpus can support, or one that is not a fraction."""


def _as_fraction(threshold: float) -> Fraction:
    # Through str so 0.8 is 4/5 exactly: float division gives 0.16 / 0.01 = 16.000000000000004,
    # and a ceiling of that is 17.
    t = Fraction(str(threshold))
    if not 0 <= t <= 1:
        raise CorpusSizeError(f"threshold {threshold} is not a fraction in [0, 1]")
    if t == 1:
        raise CorpusSizeError(
            "a threshold of 1.0 leaves no effect to detect, so no finite corpus can support it"
        )
    return t


def standard_error_route(threshold: float) -> int:
    """Items needed so the standard error at the threshold sits at half of `1 - threshold`."""
    t = _as_fraction(threshold)
    p = max(t, Fraction(1, 2))
    target_se = (1 - t) * SE_FRACTION_OF_EFFECT
    return math.ceil(p * (1 - p) / target_se**2)


def rule_of_three_route(threshold: float) -> int:
    """Items needed before a perfect score's 95% lower bound reaches the threshold."""
    t = _as_fraction(threshold)
    return math.ceil(Fraction(RULE_OF_THREE) / (1 - t))


def derived_min_items(threshold: float) -> int:
    """The minimum corpus size a threshold is valid at: the larger of the two routes."""
    return max(standard_error_route(threshold) * ESTIMATOR_BINS, rule_of_three_route(threshold))


def accuracy_lower_bound(n: int) -> float | None:
    """The 95% lower bound on true accuracy after a perfect n of n (the rule of three). Below
    three items the rule does not apply, and one item bounds nothing."""
    if n < RULE_OF_THREE:
        return None
    return max(0.0, 1 - RULE_OF_THREE / n)


def derivation(threshold: float) -> dict[str, Any]:
    """Every number the minimum rests on, for a surface to print beside it."""
    se = standard_error_route(threshold)
    return {
        "threshold": float(threshold),
        "effect": float(1 - _as_fraction(threshold)),
        "standard_error_route": se,
        "rule_of_three_route": rule_of_three_route(threshold),
        "bins": ESTIMATOR_BINS,
        "per_bin_min_items": se * ESTIMATOR_BINS,
        "min_items": derived_min_items(threshold),
    }
