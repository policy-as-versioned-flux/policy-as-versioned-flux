"""A threshold states the corpus it needs (eco-system ticket 112).

The minimum is derived from the threshold, never typed. These tests pin the method, not a table:
each expected number below is worked by hand in the test's own docstring from the two routes the
module names, so a changed method fails here with the arithmetic beside it.
"""

from __future__ import annotations

import pytest

from twin import corpus_size as cs


def test_the_standard_error_route_puts_the_noise_at_half_the_effect() -> None:
    """t = 0.8: the effect is 1 - 0.8 = 0.2, half of it is 0.1, and the binomial variance at the
    threshold is 0.8 * 0.2 = 0.16. n = 0.16 / 0.1**2 = 16, exactly, with no float rounding up to 17."""
    assert cs.standard_error_route(0.8) == 16
    assert cs.standard_error_route(0.75) == 12  # 0.1875 / 0.125**2 = 12
    assert cs.standard_error_route(0.65) == 8   # 0.2275 / 0.175**2 = 7.43


def test_the_rule_of_three_route_needs_a_perfect_score_to_clear_the_threshold() -> None:
    """A perfect n of n bounds true accuracy at 1 - 3/n (95%). It clears t only when n >= 3/(1-t)."""
    assert cs.rule_of_three_route(0.8) == 15   # 3 / 0.2
    assert cs.rule_of_three_route(0.75) == 12  # 3 / 0.25
    assert cs.rule_of_three_route(0.65) == 9   # 3 / 0.35 = 8.57


def test_the_minimum_is_the_larger_of_the_two_routes() -> None:
    assert cs.derived_min_items(0.8) == 16
    assert cs.derived_min_items(0.75) == 12
    assert cs.derived_min_items(0.65) == 9


def test_at_the_minimum_a_perfect_score_clears_its_threshold_by_the_rule_of_three() -> None:
    for threshold in (0.65, 0.75, 0.8, 0.9):
        n = cs.derived_min_items(threshold)
        bound = cs.accuracy_lower_bound(n)
        assert bound is not None and bound >= threshold - 1e-12, (threshold, n, bound)


def test_the_variance_is_taken_at_its_worst_inside_the_band_the_threshold_guards() -> None:
    """Below 0.5 the binomial variance peaks at p = 0.5, not at the threshold. Taking it at the
    threshold would under-size a low bar."""
    # t = 0.3: at p = 0.5 the route is 0.25 / 0.35**2 = 2.04 -> 3; at p = 0.3 it would be 1.71 -> 2
    assert cs.standard_error_route(0.3) == 3
    # the rule of three binds here: 3 / 0.7 = 4.29 -> 5
    assert cs.derived_min_items(0.3) == cs.rule_of_three_route(0.3) == 5


def test_a_threshold_of_one_has_no_finite_minimum() -> None:
    with pytest.raises(cs.CorpusSizeError, match="no finite corpus"):
        cs.derived_min_items(1.0)


def test_a_threshold_outside_zero_to_one_is_refused() -> None:
    with pytest.raises(cs.CorpusSizeError):
        cs.derived_min_items(1.2)


def test_the_imported_fifty_is_not_what_the_method_derives() -> None:
    """Ticket 112 item 2: the prior art's ~50 carries no formula. No threshold this estate uses
    derives it."""
    assert 50 not in {cs.derived_min_items(t) for t in (0.65, 0.75, 0.8)}


def test_the_derivation_reports_both_routes_and_the_per_bin_number() -> None:
    d = cs.derivation(0.8)
    assert d["effect"] == pytest.approx(0.2)
    assert d["standard_error_route"] == 16
    assert d["rule_of_three_route"] == 15
    assert d["bins"] == cs.ESTIMATOR_BINS == 1
    assert d["per_bin_min_items"] == d["standard_error_route"] * d["bins"]
    assert d["min_items"] == 16


def test_accuracy_lower_bound_matches_the_ticket_table() -> None:
    assert cs.accuracy_lower_bound(23) == pytest.approx(0.870, abs=5e-4)
    assert cs.accuracy_lower_bound(5) == pytest.approx(0.4)
    assert cs.accuracy_lower_bound(4) == pytest.approx(0.25)
    assert cs.accuracy_lower_bound(3) == 0.0
    assert cs.accuracy_lower_bound(1) is None
