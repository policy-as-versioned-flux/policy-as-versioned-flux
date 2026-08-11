"""PERT sampling and calibrated-range triples (build ticket 23).

Property tests against **known analytic moments**, because a sampler is exactly the kind of code
whose defect is silent: a wrong shape parameter still produces plausible numbers in the right
range, and only the mean and the variance say so.
"""

from __future__ import annotations

import pytest

from twin import pert
from twin.pert import PertError, Triple

# min, mode, max, and the mean the formula must produce. Skewed both ways and degenerate, because
# a sampler that only ever sees a symmetric triple never exercises the shape parameters at all.
CASES = [
    ((0.3, 0.5, 0.7), 0.5),
    ((0.0, 0.1, 1.0), (0.0 + 0.4 + 1.0) / 6),
    ((0.2, 0.9, 1.0), (0.2 + 3.6 + 1.0) / 6),
    ((0.4, 0.4, 0.4), 0.4),
]


@pytest.mark.parametrize("triple,expected_mean", CASES)
def test_the_mean_is_the_pert_mean(triple: tuple[float, float, float], expected_mean: float) -> None:
    assert Triple(*triple).mean == pytest.approx(expected_mean)


@pytest.mark.parametrize("triple,_expected", CASES)
def test_the_variance_is_the_pert_variance(triple: tuple[float, float, float], _expected: float) -> None:
    found = Triple(*triple)
    assert found.variance == pytest.approx((found.mean - found.low) * (found.high - found.mean) / 7.0)


@pytest.mark.parametrize("triple,_expected", CASES)
def test_the_raw_moments_recover_the_mean_and_the_variance(
    triple: tuple[float, float, float], _expected: float
) -> None:
    """The yardstick claim, made falsifiable (build ticket 21).

    `raw_moment` is derived from the Beta shape parameters and the PERT mean and variance are
    derived from the triple directly. They are two independent routes to the same numbers, so
    agreement is evidence and a docstring saying so is not.
    """
    found = Triple(*triple)
    assert found.raw_moment(0) == pytest.approx(1.0)
    assert found.raw_moment(1) == pytest.approx(found.mean)
    assert found.raw_moment(2) - found.raw_moment(1) ** 2 == pytest.approx(found.variance)


@pytest.mark.parametrize("triple,_expected", CASES)
def test_the_raw_moments_agree_with_the_sampler(
    triple: tuple[float, float, float], _expected: float
) -> None:
    """Third order too, which is where a wrong Beta recursion first shows and the variance does not."""
    found = Triple(*triple)
    stream = pert.stream(f"moments:{triple}")
    draws = [found.sample(stream) for _ in range(60000)]
    for order in (2, 3):
        empirical = sum(value**order for value in draws) / len(draws)
        assert empirical == pytest.approx(found.raw_moment(order), rel=0.02)


def test_a_negative_raw_moment_is_a_refusal() -> None:
    with pytest.raises(PertError, match="order zero or more"):
        Triple(0.3, 0.5, 0.7).raw_moment(-1)


@pytest.mark.parametrize("triple,expected_mean", CASES)
def test_sampling_converges_on_the_analytic_moments(
    triple: tuple[float, float, float], expected_mean: float
) -> None:
    """The property that catches a wrong shape parameter. A plausible range is not evidence."""
    found = Triple(*triple)
    stream = pert.stream(f"moments:{triple}")
    draws = [found.sample(stream) for _ in range(20000)]

    mean = sum(draws) / len(draws)
    variance = sum((d - mean) ** 2 for d in draws) / len(draws)
    assert mean == pytest.approx(found.mean, abs=0.01)
    # Relative, not absolute. The analytic variance of the first case is 0.0057, so an absolute
    # tolerance of 0.01 is wider than the quantity being asserted — a sampler that halved the
    # spread, which is exactly the over-confidence this test exists to catch, passed it.
    if not found.degenerate:
        assert variance == pytest.approx(found.variance, rel=0.05)
    else:
        assert variance == pytest.approx(0.0, abs=1e-12)
    assert all(found.low <= d <= found.high for d in draws), "a draw outside the authored range"


def test_a_degenerate_triple_draws_its_point_and_consumes_no_randomness() -> None:
    point = Triple(0.4, 0.4, 0.4)
    stream = pert.stream("degenerate")
    assert [point.sample(stream) for _ in range(50)] == [0.4] * 50
    assert point.degenerate is True
    with pytest.raises(PertError, match="no Beta shape"):
        point.shape


def test_sampling_is_seeded_and_repeatable() -> None:
    triple = Triple(0.1, 0.25, 0.4)
    first = [triple.sample(pert.stream("same")) for _ in range(5)]
    again = [triple.sample(pert.stream("same")) for _ in range(5)]
    other = [triple.sample(pert.stream("different")) for _ in range(5)]

    assert first == again, "the same named stream must draw the same numbers"
    assert first != other, "two different names must not draw the same numbers"


def test_a_stream_is_named_rather_than_ordered() -> None:
    """Seeded by name, so traversal order cannot reach the bytes of an artefact."""
    triple = Triple(0.1, 0.25, 0.4)
    forwards = {name: triple.sample(pert.stream(name)) for name in ("a", "b", "c")}
    backwards = {name: triple.sample(pert.stream(name)) for name in ("c", "b", "a")}
    assert forwards == backwards


def test_composition_multiplies_point_wise_and_scaling_is_linear() -> None:
    composed = Triple(0.3, 0.5, 0.7).times(Triple(0.4, 0.4, 0.4))
    assert (composed.low, composed.mode, composed.high) == pytest.approx((0.12, 0.2, 0.28))
    scaled = composed.scaled(0.8)
    assert (scaled.low, scaled.mode, scaled.high) == pytest.approx((0.096, 0.16, 0.224))


def test_an_out_of_order_triple_is_refused() -> None:
    with pytest.raises(PertError, match="min <= mode <= max"):
        Triple(0.7, 0.5, 0.3)
    with pytest.raises(PertError, match="not a finite number"):
        Triple(0.1, float("inf"), 0.4)


def test_the_calibration_procedure_is_documented_and_pinned() -> None:
    """Documented and *used*: every artefact that samples pins this by digest."""
    found = pert.procedure()
    assert found["steps"][: len(pert.REQUIRED_STEPS)] == list(pert.REQUIRED_STEPS)
    assert len(found["sha256"]) == 64
    assert "90%" in found["interval"]


def test_a_procedure_missing_a_step_is_refused(tmp_path) -> None:
    """A discipline with a missing step is not a discipline, and it still looks documented."""
    thinned = tmp_path / "calibration.md"
    thinned.write_text(
        pert.CALIBRATION_PATH.read_text(encoding="utf-8").replace("### step: equivalent-bet", "### notes"),
        encoding="utf-8",
    )
    with pytest.raises(PertError, match="equivalent-bet"):
        pert.procedure(thinned)


def test_a_figure_that_overflows_is_refused_where_it_stops_meaning_anything() -> None:
    """A cost is bounded only by *finite*, so a wide enough triple overflows in the variance.

    Without this the infinity travels several steps and surfaces as a bare `ValueError` out of
    the JSON encoder — a crash, where every other bad input in this tool gets a sentence.
    """
    huge = Triple(0.0, 1e200, 1e308)
    with pytest.raises(PertError, match="overflow"):
        huge.moments()
    with pytest.raises(PertError, match="overflow"):
        pert.quantise(float("inf"))


def test_a_triple_whose_points_are_not_numbers_is_a_refusal_not_a_traceback() -> None:
    with pytest.raises(PertError, match="not a min/mode/max triple"):
        Triple.of({"min": "x", "mode": 1, "max": 2})
    with pytest.raises(PertError, match="not a min/mode/max triple"):
        Triple.of({"min": 0, "mode": 1})


def test_the_declared_precision_applies_to_the_whole_triple() -> None:
    """Half a figure rounded to twelve digits and half not is not a declared precision."""
    moments = Triple(0.3, 0.5, 0.7).times(Triple(0.4, 0.4, 0.4)).scaled(0.8).moments()
    assert moments["max"] == 0.224, "the emitted point carries binary float noise"
    assert moments["mode"] == 0.16


def test_a_summary_is_a_spread_and_never_one_number() -> None:
    found = pert.summarise([float(i) for i in range(101)])
    assert found["min"] == 0.0 and found["max"] == 100.0
    assert found["p05"] <= found["p50"] <= found["p95"]
    assert found["draws"] == 101
    with pytest.raises(PertError, match="no draws"):
        pert.summarise([])
