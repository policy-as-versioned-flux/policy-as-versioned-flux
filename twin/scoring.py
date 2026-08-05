"""Proper scoring rules.

A scoring rule is **proper** when a forecaster minimises their expected score by reporting what
they actually believe. Anything else rewards hedging, and a calibration record built on an
improper rule measures the rule rather than the forecaster (build ticket 08; spec story 44).

Both rules here are losses: **lower is better**, stated once so nothing downstream has to guess.
"""

from __future__ import annotations

import math

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
