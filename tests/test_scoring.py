"""Seam 2 — the scoring rules.

A scoring rule is **proper** when the forecaster minimises their expected score by reporting what
they actually believe. That is the whole reason to use one, and it is a numerical property, so it
is asserted numerically rather than by naming the formula.
"""

from __future__ import annotations

import math

import pytest

from twin.scoring import (
    LOWER_IS_BETTER,
    SIGNIFICANT_DIGITS,
    ScoreError,
    brier,
    log_loss,
    measure_discount,
    quantise,
    reliability_diagram,
    score,
)

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


# -- the memorisation-leakage discount (build ticket 40) ---------------------------------------


def test_the_discount_is_measured_from_the_enron_versus_obscure_gap() -> None:
    """AC: the discount is measured, never hardcoded."""
    enron = [score(0.02, False)]  # a very confident, very cheap-looking win
    obscure = [score(0.4, False)]  # a more honest, more expensive miss
    result = measure_discount(enron, obscure, rule="brier")
    assert result["rule"] == "brier"
    assert result["discount"] == pytest.approx(brier(0.4, False) - brier(0.02, False))
    assert result["legs"] == [
        {"leg": "enron-vs-obscure", "gap": result["discount"], "n_control": 1, "n_obscure": 1}
    ]


def test_the_discount_changes_when_the_underlying_performance_changes() -> None:
    """AC: a test asserts it changes when the underlying performance changes — the discount is
    not a constant wearing a function's clothes."""
    enron = [score(0.02, False)]
    obscure_a = [score(0.4, False)]
    obscure_b = [score(0.1, False)]
    a = measure_discount(enron, obscure_a, rule="brier")
    b = measure_discount(enron, obscure_b, rule="brier")
    assert a["discount"] != b["discount"]


def test_a_positive_discount_means_enron_looked_artificially_cheap() -> None:
    enron = [score(0.02, False)]  # near-certain and right: an artificially cheap loss
    obscure = [score(0.5, False)]  # honest uncertainty, a more expensive loss
    result = measure_discount(enron, obscure, rule="brier")
    assert result["discount"] > 0


def test_a_gap_near_zero_when_enron_earns_no_special_advantage() -> None:
    """The sign is not clamped: a forecaster with no memorisation advantage on Enron shows a gap
    near zero rather than a floor at zero."""
    enron = [score(0.3, False)]
    obscure = [score(0.3, False)]
    result = measure_discount(enron, obscure, rule="brier")
    assert result["discount"] == pytest.approx(0.0)


def test_the_discount_is_reported_separately_from_the_raw_score() -> None:
    """AC: reported separately so both are visible — `measure_discount` never mutates its inputs."""
    enron = [score(0.02, False)]
    obscure = [score(0.4, False)]
    before = [dict(s) for s in enron + obscure]
    measure_discount(enron, obscure, rule="brier")
    assert enron + obscure == before


def test_hindsight_legs_fold_into_the_same_discount_rather_than_sitting_beside_it() -> None:
    """AC (build ticket 41): results feed the contamination discount rather than sitting
    alongside it — the number itself moves when the hindsight legs are supplied."""
    enron = [score(0.02, False)]
    obscure = [score(0.4, False)]
    without_hindsight = measure_discount(enron, obscure, rule="brier")

    memorising = [score(0.9, False)]  # confidently wrong: recites the canonical story
    honest = [score(0.2, False)]  # correctly uncertain: reasons from the period record
    with_hindsight = measure_discount(
        enron, obscure, rule="brier", hindsight_memorising=memorising, hindsight_honest=honest
    )

    assert with_hindsight["discount"] != without_hindsight["discount"]
    assert [leg["leg"] for leg in with_hindsight["legs"]] == [
        "enron-vs-obscure", "hindsight-memorising-vs-honest",
    ]
    hindsight_leg = with_hindsight["legs"][1]
    assert hindsight_leg["gap"] == pytest.approx(brier(0.9, False) - brier(0.2, False))
    assert hindsight_leg["gap"] > 0, "the memorising world model should score worse than the honest one"


def test_both_hindsight_lists_are_needed_together_or_neither() -> None:
    enron = [score(0.02, False)]
    obscure = [score(0.4, False)]
    with pytest.raises(ScoreError, match="both hindsight_memorising and hindsight_honest"):
        measure_discount(enron, obscure, hindsight_memorising=[score(0.9, False)])


def test_the_discount_needs_at_least_one_score_on_each_side() -> None:
    with pytest.raises(ScoreError, match="at least one Enron score"):
        measure_discount([], [score(0.4, False)])
    with pytest.raises(ScoreError, match="at least one Enron score"):
        measure_discount([score(0.4, False)], [])


def test_an_unknown_rule_is_refused() -> None:
    with pytest.raises(ScoreError, match="is not a scoring rule"):
        measure_discount([score(0.4, False)], [score(0.4, False)], rule="made-up-rule")
