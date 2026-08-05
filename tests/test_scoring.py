"""Seam 2 — the scoring rules.

A scoring rule is **proper** when the forecaster minimises their expected score by reporting what
they actually believe. That is the whole reason to use one, and it is a numerical property, so it
is asserted numerically rather than by naming the formula.
"""

from __future__ import annotations

import math

import pytest

from twin.scoring import LOWER_IS_BETTER, SIGNIFICANT_DIGITS, brier, log_loss, quantise

GRID = [0.02, 0.1, 0.25, 0.4, 0.5, 0.63, 0.8, 0.95, 0.99]


def _expected(rule, truth: float, forecast: float) -> float:
    """Expected score of forecasting `forecast` when the outcome is true with probability `truth`."""
    return truth * rule(forecast, True) + (1.0 - truth) * rule(forecast, False)


@pytest.mark.parametrize("rule", [brier, log_loss], ids=["brier", "log-loss"])
@pytest.mark.parametrize("truth", GRID)
def test_the_rule_is_proper(rule, truth: float) -> None:
    """Honesty is optimal: no other forecast has a lower expected score than the true probability."""
    honest = _expected(rule, truth, truth)
    for forecast in GRID:
        if forecast == truth:
            continue
        assert honest < _expected(rule, truth, forecast), (
            f"reporting {forecast} beat reporting the truth {truth} — the rule is not proper"
        )


@pytest.mark.parametrize("rule", [brier, log_loss], ids=["brier", "log-loss"])
def test_a_forecast_that_was_right_scores_better_than_one_that_was_wrong(rule) -> None:
    assert rule(0.9, True) < rule(0.5, True) < rule(0.1, True)
    assert rule(0.1, False) < rule(0.5, False) < rule(0.9, False)


@pytest.mark.parametrize("rule", [brier, log_loss], ids=["brier", "log-loss"])
def test_lower_is_better_is_the_declared_orientation(rule) -> None:
    assert LOWER_IS_BETTER
    assert rule(0.99, True) < rule(0.01, True)


def test_brier_is_the_squared_error() -> None:
    assert brier(0.62, True) == pytest.approx(0.1444)
    assert brier(0.25, True) == pytest.approx(0.5625)
    assert brier(0.5, False) == pytest.approx(0.25)


def test_log_loss_is_the_negative_log_of_the_probability_given_to_what_happened() -> None:
    assert log_loss(0.62, True) == pytest.approx(-math.log(0.62))
    assert log_loss(0.62, False) == pytest.approx(-math.log(0.38))


@pytest.mark.parametrize("rule", [brier, log_loss], ids=["brier", "log-loss"])
@pytest.mark.parametrize("certain", [0.0, 1.0])
def test_a_claim_of_certainty_is_refused(rule, certain: float) -> None:
    """An infinite penalty is not serialisable, so certainty is refused where it is authored."""
    with pytest.raises(ValueError, match="strictly between 0 and 1"):
        rule(certain, True)


# -- the declared quantisation ----------------------------------------------------------------


def test_scores_are_quantised_to_a_declared_precision() -> None:
    """`log` is not correctly-rounded on every platform, so a last-ulp difference is real.

    Rounding to a declared number of significant digits is a property of the artefact format,
    not an implicit convenience — which is what makes the identical-bytes claim checkable.
    """
    assert SIGNIFICANT_DIGITS == 12
    value = log_loss(0.62, True)
    assert quantise(value) == quantise(math.nextafter(value, math.inf))
    assert quantise(value) == quantise(math.nextafter(value, -math.inf))


def test_quantising_twice_changes_nothing() -> None:
    for value in (0.1, 1 / 3, math.pi, 1e-9, 123456.789):
        assert quantise(quantise(value)) == quantise(value)


def test_quantisation_keeps_far_more_precision_than_any_decision_needs() -> None:
    assert quantise(0.123456789012345) == pytest.approx(0.123456789012, abs=1e-14)
    assert quantise(0.5) == 0.5
    assert quantise(0.0) == 0.0
