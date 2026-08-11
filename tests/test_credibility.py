"""Bühlmann–Straub credibility blending (build ticket 31).

Property tests over `credibility_z`, per the ticket's own acceptance criterion: weight on
own-data rises with volume and falls with variance. No `hypothesis` dependency — a parametrised
grid is enough to demonstrate the monotonicity the formula guarantees analytically.
"""

from __future__ import annotations

import pytest

from twin.credibility import Blend, blend, credibility_z, variance
from twin.pert import Triple

INDUSTRY = Triple(20000.0, 50000.0, 140000.0)  # mean 60000, variance 3_200_000_000 / 7


# -- credibility_z: the property tests -----------------------------------------------------


def _strictly(zs: list[float], *, rising: bool, what: str) -> None:
    """`zs == sorted(zs)` alone tolerates a regression that collapses `Z` to a constant. Every
    consecutive pair here must move in the asserted direction — not merely never move backwards."""
    ordered = zs if rising else list(reversed(zs))
    for a, b in zip(ordered, ordered[1:]):
        assert a < b, f"Z must strictly {what}, got {zs}"


@pytest.mark.parametrize("own_variance", [1.0, 100.0, 1_000_000.0])
def test_z_rises_with_own_data_volume(own_variance: float) -> None:
    world_variance = 500_000.0
    zs = [credibility_z(n, own_variance, world_variance) for n in (0, 1, 2, 5, 20, 100)]
    _strictly(zs, rising=True, what="rise in n")
    assert zs[0] == 0.0, "no own-data at all carries no weight"
    assert zs[-1] < 1.0, "finite n never reaches full weight"


@pytest.mark.parametrize("n", [1, 5, 50])
def test_z_falls_as_own_variance_rises(n: int) -> None:
    world_variance = 500_000.0
    zs = [credibility_z(n, ov, world_variance) for ov in (1.0, 100.0, 10_000.0, 1_000_000.0)]
    _strictly(zs, rising=False, what="fall as own_variance rises")


@pytest.mark.parametrize("n", [1, 5, 50])
def test_z_rises_as_world_variance_rises(n: int) -> None:
    """A wider, less-certain industry prior is overridden faster by the same own evidence."""
    own_variance = 500_000.0
    zs = [credibility_z(n, own_variance, wv) for wv in (1_000.0, 100_000.0, 10_000_000.0)]
    _strictly(zs, rising=True, what="rise in world_variance")


def test_z_is_always_between_zero_and_one() -> None:
    for n in (0, 1, 3, 1000):
        for ov in (0.0, 1.0, 1e9):
            for wv in (0.0, 1.0, 1e9):
                z = credibility_z(n, ov, wv)
                assert 0.0 <= z <= 1.0, (n, ov, wv, z)


def test_no_own_data_carries_no_weight() -> None:
    assert credibility_z(0, 100.0, 100.0) == 0.0


def test_a_single_perfectly_consistent_observation_takes_full_weight() -> None:
    """Zero own-variance is not divide-by-zero; it is the strongest signal own-data can send."""
    assert credibility_z(1, 0.0, 100.0) == 1.0


def test_a_degenerate_industry_prior_yields_no_credibility() -> None:
    """No variance to compare against: the prior is treated as settled rather than divided by zero."""
    assert credibility_z(5, 100.0, 0.0) == 0.0


def test_a_degenerate_prior_wins_over_equally_degenerate_own_data() -> None:
    """Both checks can fire at once — an industry number stated with total certainty is
    immovable, even by own-data that happens to be just as consistent."""
    assert credibility_z(5, 0.0, 0.0) == 0.0


# -- variance -------------------------------------------------------------------------------


def test_variance_of_one_or_no_points_is_zero() -> None:
    assert variance([]) == 0.0
    assert variance([42.0]) == 0.0


def test_variance_matches_hand_arithmetic() -> None:
    # (30000-40000)^2 + (50000-40000)^2 + (40000-40000)^2, over (n-1) = 2
    assert variance([30000.0, 50000.0, 40000.0]) == pytest.approx(100_000_000.0)


# -- blend: the whole picture -----------------------------------------------------------------


def test_no_own_data_prices_from_the_world_prior_alone() -> None:
    result = blend("a-subject", INDUSTRY, [])
    assert result.n == 0
    assert result.blended == INDUSTRY
    body = result.as_dict()
    assert body["own_data"]["n"] == 0
    assert "world-layer prior alone" in body["own_data"]["note"]


def test_the_blend_is_visible_in_the_artefact() -> None:
    """Which component of the estimate came from where, not just the resulting number."""
    result = blend("a-subject", INDUSTRY, [30000.0, 50000.0, 40000.0])
    body = result.as_dict()
    credibility = body["credibility"]
    own_plus_world = credibility["own_component"] + credibility["world_component"]
    assert own_plus_world == pytest.approx(body["blended"]["mode"])
    assert 0.0 < credibility["z"] < 1.0


def test_re_estimating_as_own_data_accumulates_is_a_normal_read() -> None:
    """A pure function of its inputs: no ceremony, no regrade, just more data in, a new blend out.

    Repeating the same spread rather than widening it, so the comparison isolates volume from
    variance — `test_z_rises_with_own_data_volume` already covers variance held fixed by hand.
    """
    thin = blend("a-subject", INDUSTRY, [39000.0, 41000.0])
    fuller = blend("a-subject", INDUSTRY, [39000.0, 41000.0] * 5)
    assert fuller.z > thin.z, "more own-data at the same spread earns more credibility, not less"


def test_the_blended_triple_still_orders_low_mode_high() -> None:
    """A rigid translation of the whole triple preserves ordering regardless of shift direction."""
    for observations in ([1.0], [200000.0], [200000.0, 200000.0, 200000.0], [0.0, 0.0]):
        result = blend("a-subject", INDUSTRY, observations)
        assert result.blended.low <= result.blended.mode <= result.blended.high


def test_the_blend_never_narrows_the_priors_width() -> None:
    result = blend("a-subject", INDUSTRY, [10000.0, 12000.0, 11000.0])
    prior_width = INDUSTRY.high - INDUSTRY.low
    blended_width = result.blended.high - result.blended.low
    assert blended_width == pytest.approx(prior_width), (
        "the blend moves the centre, never manufactures a narrower band from a few points"
    )


def test_a_subject_carries_through_unmodified() -> None:
    assert blend("shared-database-outage", INDUSTRY, []).subject == "shared-database-outage"


def test_blend_is_a_dataclass_with_no_hidden_state() -> None:
    result = blend("a-subject", INDUSTRY, [10000.0])
    assert isinstance(result, Blend)
    # Calling again with the same inputs gives the same answer — a derived read, not a side effect.
    again = blend("a-subject", INDUSTRY, [10000.0])
    assert result.as_dict() == again.as_dict()
