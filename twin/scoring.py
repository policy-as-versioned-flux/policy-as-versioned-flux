"""Proper scoring rules.

A scoring rule is **proper** when a forecaster minimises their expected score by reporting what
they actually believe. Anything else rewards hedging, and a calibration record built on an
improper rule measures the rule rather than the forecaster (build ticket 08; spec story 44).

Both rules here are losses: **lower is better**, stated once so nothing downstream has to guess.
"""

from __future__ import annotations

import math
from typing import Any

class ScoreError(ValueError):
    """Not scoreable. A refusal, not a bug."""


LOWER_IS_BETTER = True
RULES = ("brier", "log_loss")

# The declared precision of every score in an artefact.
#
# `math.log` is not correctly-rounded on every platform, so two architectures can disagree in the
# last unit in the last place — which would break `identical_pins_identical_bytes` for any
# artefact carrying a log score. Rounding to a fixed number of significant decimal digits absorbs
# that. It is a **declared, tested property of the artefact format**, not an implicit convenience,
# and it is not a proof: two values straddling a rounding boundary would still diverge, and the
# CI architecture matrix is what would catch that.
SIGNIFICANT_DIGITS = 12


def quantise(value: float) -> float:
    """Round to `SIGNIFICANT_DIGITS` significant decimal digits."""
    return float(f"{value:.{SIGNIFICANT_DIGITS - 1}e}")


def _check(probability: float) -> float:
    if not 0.0 < probability < 1.0:
        raise ScoreError(
            f"a forecast must be strictly between 0 and 1, got {probability} — a claim of "
            "certainty carries an infinite log-score penalty and is not a forecast"
        )
    return float(probability)


def brier(probability: float, observed: bool) -> float:
    """Squared error against the outcome. Pure arithmetic, so exact on every platform."""
    p = _check(probability)
    return (p - (1.0 if observed else 0.0)) ** 2


def log_loss(probability: float, observed: bool) -> float:
    """Negative log of the probability given to what actually happened."""
    p = _check(probability)
    return -math.log(p if observed else 1.0 - p)


def score(probability: float, observed: bool) -> dict[str, float]:
    """Every rule at once. Collapsing to one score is a choice the reader makes, not this code."""
    return {
        "brier": quantise(brier(probability, observed)),
        "log_loss": quantise(log_loss(probability, observed)),
    }


# -- the reliability diagram (build ticket 09; spec story 44) --------------------------------


def _mean(entries: list[dict[str, Any]], rule: str) -> float:
    return sum(float(e[rule]) for e in entries) / len(entries)


def measure_discount(
    enron: list[dict[str, Any]],
    obscure: list[dict[str, Any]],
    rule: str = "brier",
    hindsight_memorising: list[dict[str, Any]] | None = None,
    hindsight_honest: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """The memorisation-leakage discount (build ticket 40; decision ticket 19).

    Measured, never hardcoded: the mean `rule` loss on an obscure (low-notoriety) key, minus the
    mean loss on the Enron contamination-control key. A forecaster that has memorised Enron's
    ending scores artificially well there — a lower loss than its honest skill on an obscure case
    earns — and that gap is exactly the inflation, priced. A positive discount is evidence of
    inflation; the sign is not clamped, because a model with no such advantage would show a gap
    near zero rather than a floor.

    Build ticket 41's hindsight-resistance cases fold into this same number rather than sitting
    beside it (that ticket's AC): when both `hindsight_*` lists are given, the memorising-versus-
    honest world model's own gap on those cases is measured the same way — mean loss on the
    memorising world model minus mean loss on the honest one — and averaged with the
    Enron-versus-obscure gap. Both legs are reported in `legs` so the basis stays inspectable; the
    two are not the same physical quantity, but both are evidence of the same threat, and the
    project's own culture is to price a threat rather than merely note it.
    """
    if rule not in RULES:
        raise ScoreError(f"{rule!r} is not a scoring rule; have {RULES}")
    if not enron or not obscure:
        raise ScoreError("the discount needs at least one Enron score and one obscure-key score")
    if bool(hindsight_memorising) != bool(hindsight_honest):
        raise ScoreError(
            "both hindsight_memorising and hindsight_honest are needed to fold in the hindsight gap, or neither"
        )

    legs: list[dict[str, Any]] = [
        {
            "leg": "enron-vs-obscure",
            "gap": quantise(_mean(obscure, rule) - _mean(enron, rule)),
            "n_control": len(enron),
            "n_obscure": len(obscure),
        }
    ]
    if hindsight_memorising and hindsight_honest:
        legs.append(
            {
                "leg": "hindsight-memorising-vs-honest",
                "gap": quantise(_mean(hindsight_memorising, rule) - _mean(hindsight_honest, rule)),
                "n_memorising": len(hindsight_memorising),
                "n_honest": len(hindsight_honest),
            }
        )

    discount = quantise(sum(float(leg["gap"]) for leg in legs) / len(legs))
    return {"rule": rule, "discount": discount, "legs": legs}


def reliability_diagram(scores: list[dict[str, Any]], bins: int = 10) -> dict[str, Any]:
    """Bin a scored-forecast **population** by predicted probability.

    Calibration is a property of volume, so this reads many scored forecasts at once (`scores`,
    pooled across as many score cards as the caller names) rather than judging one.

    Every bin is reported, including an empty one — the **count** is what stops a thin bin
    masquerading as calibration, and omitting an empty bin would hide the thinnest one of all.
    `mean_forecast` and `empirical_frequency` are `None` on an empty bin: there is no average of
    zero numbers, and reporting `0.0` there would read as "always wrong" rather than "nothing
    landed here yet".
    """
    if bins < 1:
        raise ScoreError(f"a reliability diagram needs at least one bin, got {bins}")
    width = 1.0 / bins
    counts = [0] * bins
    sums = [0.0] * bins
    observed_counts = [0] * bins
    for entry in scores:
        p = _check(float(entry["probability"]))
        index = min(int(p * bins), bins - 1)
        counts[index] += 1
        sums[index] += p
        if entry["observed"]:
            observed_counts[index] += 1

    out = []
    for i in range(bins):
        n = counts[i]
        out.append(
            {
                "bin": i,
                "range": [quantise(i * width), quantise((i + 1) * width)],
                "count": n,
                "mean_forecast": quantise(sums[i] / n) if n else None,
                "empirical_frequency": quantise(observed_counts[i] / n) if n else None,
            }
        )
    return {"bins": out, "total": len(scores)}
