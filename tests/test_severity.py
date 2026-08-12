"""Heavy-tailed severity, TVaR, and the loss-exceedance curve (build ticket 24).

Property tests against the composite distribution's own definition — a spliced tail is exactly
the kind of code whose defect is silent: a wrong scale still produces a plausible-looking curve,
and only cross-checking the two routes to a number (the closed form and the sampler; `var()` and
`sample()` sharing one inversion) says so.
"""

from __future__ import annotations

import math
import random

import pytest

from twin.severity import Severity, SeverityError

# A representative body/tail: threshold chosen so ~15.7% of mass sits in the tail (comfortably
# above the 0.9/0.95/0.99 confidence levels the tests below ask for), a moderate shape that keeps
# the mean well inside "exists" (xi < 1) so the closed-form legs have something to check
# themselves against.
BODY = dict(mu=10.0, sigma=1.5)
TAIL = dict(threshold=100_000.0, xi=0.3, beta=80_000.0)


def make(**overrides: float) -> Severity:
    return Severity(**{**BODY, **TAIL, **overrides})


def test_the_tail_probability_is_derived_not_authored() -> None:
    """Two Severities sharing a body and threshold share a tail_probability even with different
    tails — it is a property of the splice point, not of the GPD parameters."""
    light = make(xi=0.1, beta=100_000.0)
    heavy = make(xi=0.8, beta=400_000.0)
    assert light.tail_probability == pytest.approx(heavy.tail_probability)
    assert 0.0 < light.tail_probability < 1.0


def test_survival_is_continuous_at_the_threshold() -> None:
    s = make()
    below = s.survival(s.threshold - 1e-6)
    above = s.survival(s.threshold + 1e-6)
    assert below == pytest.approx(s.tail_probability, rel=1e-4)
    assert above == pytest.approx(s.tail_probability, rel=1e-4)


def test_survival_is_monotonically_non_increasing() -> None:
    s = make()
    xs = [1_000.0, 10_000.0, s.threshold / 2, s.threshold, s.threshold * 2, s.threshold * 10]
    values = [s.survival(x) for x in xs]
    assert values == sorted(values, reverse=True)
    assert values[0] <= 1.0
    assert values[-1] >= 0.0


@pytest.mark.parametrize("alpha", [0.5, 0.8, 0.9, 0.95, 0.99, 0.999])
def test_cdf_of_var_recovers_alpha(alpha: float) -> None:
    """`var()` and `cdf()` are inverses of each other by construction — the property a spliced
    quantile function is most likely to get wrong at exactly the splice point."""
    s = make()
    assert s.cdf(s.var(alpha)) == pytest.approx(alpha, rel=1e-6)


def test_var_is_monotonically_increasing_in_alpha() -> None:
    s = make()
    alphas = [0.5, 0.7, 0.85, 0.9, 0.95, 0.99, 0.999]
    values = [s.var(a) for a in alphas]
    assert values == sorted(values)


def test_var_at_the_threshold_exceedance_probability_is_exactly_the_threshold() -> None:
    """At `alpha = 1 - tail_probability`, VaR lands exactly on the splice point — independent of
    the tail's shape, because `_gpd_quantile` at its own boundary is zero for any `xi`."""
    for xi in (-0.2, 0.0, 0.3, 0.9):
        s = make(xi=xi)
        alpha = 1.0 - s.tail_probability
        assert s.var(alpha) == pytest.approx(s.threshold, rel=1e-6)


def test_a_var_shaped_summary_hides_what_tvar_surfaces() -> None:
    """The ticket's demonstration. Same body, same threshold, same beta: at the threshold's own
    exceedance probability, VaR is identical for a light and a heavy tail (see the test above) —
    a report carrying only VaR could not tell these two risks apart. TVaR immediately can, because
    it is exactly the average of what lies beyond that point, and more of that mass is far out in
    the heavy case."""
    light = make(xi=0.1)
    heavy = make(xi=0.7)
    alpha = 1.0 - light.tail_probability
    assert light.var(alpha) == pytest.approx(heavy.var(alpha), rel=1e-6)

    light_tvar = light.tvar(alpha)
    heavy_tvar = heavy.tvar(alpha)
    assert heavy_tvar > light_tvar * 1.5, (
        "a heavier tail must carry a materially larger TVaR even though VaR agreed exactly — "
        "otherwise TVaR is not surfacing anything VaR did not already show"
    )


def test_tvar_is_never_smaller_than_var() -> None:
    for alpha in (0.9, 0.95, 0.99):
        s = make()
        assert s.tvar(alpha) >= s.var(alpha)


def test_tvar_below_the_threshold_is_refused() -> None:
    """The body-region boundary this module declines to cross (ponytail note in severity.py)."""
    s = make()
    low_alpha = 1.0 - s.tail_probability - 0.05  # exceedance above the tail's own mass: body region
    assert s.var(low_alpha) < s.threshold
    with pytest.raises(SeverityError, match="inside the lognormal body"):
        s.tvar(low_alpha)


@pytest.mark.parametrize("xi", [1.0, 1.5, 3.0])
def test_tvar_at_and_beyond_the_shape_boundary_is_refused(xi: float) -> None:
    """The AC's named boundary: where the GPD mean stops existing, TVaR refuses rather than
    dividing by a `(1 - xi)` that has gone to zero or negative."""
    s = make(xi=xi)
    alpha = 1.0 - s.tail_probability + 0.01  # comfortably inside the declared tail
    assert s.var(alpha) >= s.threshold
    with pytest.raises(SeverityError, match="does not exist"):
        s.tvar(alpha)


def test_just_below_the_shape_boundary_still_computes() -> None:
    """The refusal is a boundary, not a wall: xi approaching 1 from below still returns a number,
    and that number grows without bound as xi climbs toward the boundary it will soon refuse at."""
    alpha = 0.995
    tvars = [make(xi=xi).tvar(alpha) for xi in (0.5, 0.9, 0.99)]
    assert tvars == sorted(tvars), "TVaR must grow as the tail approaches the undefined-mean boundary"


def test_sampling_converges_on_the_analytic_tvar() -> None:
    """The property that catches a wrong sampler or a wrong closed form independently: draws above
    a fixed VaR average out to the analytic TVaR, exactly as `test_sampling_converges_on_the_analytic_moments`
    does for a PERT triple."""
    s = make(xi=0.3)
    alpha = 0.95
    v = s.var(alpha)
    rng = random.Random("severity-tvar-convergence")
    draws = [s.sample(rng) for _ in range(200_000)]
    beyond = [d for d in draws if d > v]
    assert len(beyond) / len(draws) == pytest.approx(1.0 - alpha, rel=0.1)
    empirical_tvar = sum(beyond) / len(beyond)
    assert empirical_tvar == pytest.approx(s.tvar(alpha), rel=0.1)


def test_sampling_is_seeded_and_repeatable() -> None:
    s = make()
    first = [s.sample(random.Random("same")) for _ in range(5)]
    again = [s.sample(random.Random("same")) for _ in range(5)]
    other = [s.sample(random.Random("different")) for _ in range(5)]
    assert first == again
    assert first != other


def test_loss_exceedance_curve_reports_both_figures_and_names_a_refusal_honestly() -> None:
    s = make()
    curve = s.loss_exceedance_curve([1.0 - s.tail_probability - 0.05, 0.9, 0.95, 0.99])
    assert [row["alpha"] for row in curve] == sorted(row["alpha"] for row in curve)
    below_threshold_row = curve[0]
    assert below_threshold_row["var"] is not None
    assert below_threshold_row["tvar"] is None
    assert "lognormal body" in below_threshold_row["tvar_refused"]
    for row in curve[1:]:
        assert row["tvar"] is not None and row["tvar"] >= row["var"]
        assert row["tvar_refused"] is None


def test_the_declared_precision_applies_to_every_figure_in_the_curve() -> None:
    s = make()
    curve = s.loss_exceedance_curve([0.95])
    row = curve[0]
    assert row["var"] == float(f"{row['var']:.11e}")
    assert row["tvar"] == float(f"{row['tvar']:.11e}")


def test_a_degenerate_or_non_finite_parameter_is_refused() -> None:
    with pytest.raises(SeverityError, match="not a finite number"):
        Severity(mu=10.0, sigma=float("inf"), threshold=1.0, xi=0.3, beta=1.0)
    with pytest.raises(SeverityError, match="sigma must be positive"):
        Severity(mu=10.0, sigma=0.0, threshold=1.0, xi=0.3, beta=1.0)
    with pytest.raises(SeverityError, match="threshold must be positive"):
        Severity(mu=10.0, sigma=1.0, threshold=0.0, xi=0.3, beta=1.0)
    with pytest.raises(SeverityError, match="beta must be positive"):
        Severity(mu=10.0, sigma=1.0, threshold=1.0, xi=0.3, beta=-1.0)


def test_a_quantile_outside_the_open_unit_interval_is_refused() -> None:
    s = make()
    with pytest.raises(SeverityError, match="strictly between 0 and 1"):
        s.var(0.0)
    with pytest.raises(SeverityError, match="strictly between 0 and 1"):
        s.var(1.0)


def test_xi_zero_is_the_exponential_tail_special_case() -> None:
    """`xi == 0` divides by nothing anywhere in `_gpd_survival`/`_gpd_quantile`; asserted directly
    because it is the one value both closed forms branch on."""
    s = make(xi=0.0)
    alpha = 1.0 - s.tail_probability + 0.02
    v = s.var(alpha)
    assert v > s.threshold
    assert math.isfinite(s.tvar(alpha))


def test_negative_xi_gives_the_tail_a_finite_right_endpoint() -> None:
    """`xi < 0` is a bounded GPD; survival must reach exactly zero at and beyond that endpoint
    rather than the formula going complex or negative."""
    s = make(xi=-0.5, beta=100_000.0)
    endpoint = s.threshold + s.beta / 0.5  # -beta/xi
    assert s.survival(endpoint) == pytest.approx(0.0, abs=1e-9)
    assert s.survival(endpoint * 2) == 0.0
