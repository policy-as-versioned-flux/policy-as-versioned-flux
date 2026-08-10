"""Seam 2 — the scoring rules.

A scoring rule is **proper** when the forecaster minimises their expected score by reporting what
they actually believe. That is the whole reason to use one, and it is a numerical property, so it
is asserted numerically rather than by naming the formula.
"""

from __future__ import annotations

import math

import pytest

from twin.scoring import LOWER_IS_BETTER, SIGNIFICANT_DIGITS, ScoreError, brier, log_loss, quantise, reliability_diagram

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


# -- the reliability diagram --------------------------------------------------------------------


def _entry(probability: float, observed: bool) -> dict:
    return {"probability": probability, "observed": observed}


def test_bins_carry_the_forecasts_that_land_in_their_range() -> None:
    scores = [_entry(0.05, False), _entry(0.85, True), _entry(0.9, True), _entry(0.92, False)]
    diagram = reliability_diagram(scores, bins=10)
    assert diagram["total"] == 4
    by_index = {b["bin"]: b for b in diagram["bins"]}
    assert by_index[0]["count"] == 1
    assert by_index[0]["range"] == [0.0, 0.1]
    assert by_index[8]["count"] == 1  # 0.85 falls in [0.8, 0.9)
    assert by_index[9]["count"] == 2  # 0.9 and 0.92 both fall in [0.9, 1.0]


def test_an_empty_bin_carries_a_count_and_no_fabricated_average() -> None:
    """A count of zero is shown rather than omitted — an omitted bin cannot be seen to be thin."""
    diagram = reliability_diagram([_entry(0.05, True)], bins=10)
    empty = [b for b in diagram["bins"] if b["bin"] != 0]
    assert len(empty) == 9
    assert all(b["count"] == 0 for b in empty)
    assert all(b["mean_forecast"] is None for b in empty)
    assert all(b["empirical_frequency"] is None for b in empty)


def test_every_bin_is_reported_even_from_an_empty_population() -> None:
    diagram = reliability_diagram([], bins=4)
    assert diagram["total"] == 0
    assert [b["count"] for b in diagram["bins"]] == [0, 0, 0, 0]


def test_empirical_frequency_is_the_observed_rate_within_a_bin() -> None:
    scores = [_entry(0.75, True), _entry(0.78, True), _entry(0.72, False)]
    diagram = reliability_diagram(scores, bins=10)
    bin_7 = next(b for b in diagram["bins"] if b["bin"] == 7)
    assert bin_7["count"] == 3
    assert bin_7["empirical_frequency"] == pytest.approx(2 / 3)
    assert bin_7["mean_forecast"] == pytest.approx((0.75 + 0.78 + 0.72) / 3)


def test_a_probability_on_a_bin_edge_falls_in_the_bin_it_opens() -> None:
    """0.5 belongs to [0.5, 0.6), not [0.4, 0.5) — `int(p * bins)`, not a rounding rule."""
    diagram = reliability_diagram([_entry(0.5, True)], bins=10)
    assert next(b for b in diagram["bins"] if b["bin"] == 5)["count"] == 1
    assert next(b for b in diagram["bins"] if b["bin"] == 4)["count"] == 0


def test_a_forecast_of_exactly_one_stays_in_the_top_bin_not_a_phantom_eleventh() -> None:
    diagram = reliability_diagram([_entry(1.0 - 1e-12, True)], bins=10)
    assert next(b for b in diagram["bins"] if b["bin"] == 9)["count"] == 1


def test_bins_must_be_at_least_one() -> None:
    with pytest.raises(ScoreError, match="at least one bin"):
        reliability_diagram([], bins=0)


def test_an_out_of_range_probability_is_refused_not_silently_clamped() -> None:
    with pytest.raises(ValueError, match="strictly between 0 and 1"):
        reliability_diagram([_entry(1.5, True)], bins=10)
