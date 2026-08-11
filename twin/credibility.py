"""Bühlmann–Straub credibility: blend the world-layer industry prior with an org's own sparse data.

Build ticket 31, from decision tickets 07 (Q1b — the world/overlay split IS the credibility
structure) and 09 (the £ is perspectival and evidence-graded); research 02 §1.4.

    estimate = Z x (own-data mean) + (1 - Z) x (industry prior mode),   Z = n / (n + K)

Z is the credibility factor, and it has to rise with the volume of own-data and fall with its
variance. `research/risk-threat-sota.md` sets K from the ratio of *within-risk* to *between-risk*
variance — the spread of the true means across a whole portfolio of organisations. This system
pins one org's overlay against one world layer, not a portfolio of orgs to estimate a
between-risk variance from directly, so K substitutes the world-layer prior's own variance for
it: a wide, uncertain industry number lets an org's own data override it faster than a narrow,
well-established one does.

`ponytail:` that substitution is the honest single-org stand-in for a portfolio-estimated K. The
upgrade, once the world layer ever carries more than one org's worth of hypothetical means, is
estimating K from their variance directly, the way Bühlmann–Straub is specified.

The blend never narrows the industry prior's own uncertainty band from a handful of own-data
points — narrowing a 90% interval on the strength of two or three observations would be exactly
the false precision `twin/calibration.md`'s discipline exists to catch. Instead the whole triple
translates by the credibility-weighted shift in its mode, so the reported width is unchanged and
the reported centre moves only as far as the org's own evidence, weighted by how much it earns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .pert import Triple, quantise


def variance(values: list[float]) -> float:
    """Sample variance (n-1 divisor). Zero for fewer than two points — one observation has no
    spread to measure, and treating it as zero-variance is what lets `credibility_z` give it
    full weight rather than dividing by zero."""
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return sum((v - mean) ** 2 for v in values) / (n - 1)


def credibility_z(n: int, own_variance: float, world_variance: float) -> float:
    """`Z = n / (n + K)`, `K = own_variance / world_variance`.

    Rises with `n` (own-data volume rules 1 and 2 of the ticket). Falls as `own_variance` rises —
    noisier own data is trusted less (rule 3). Rises as `world_variance` rises: a wider, less
    certain industry prior is overridden faster by the same amount of own evidence.

    The two degenerate-variance checks are ordered deliberately: a **degenerate world prior is
    checked first**, and wins even when own-data is also degenerate. An industry number stated
    with total certainty is immovable by construction — there is no amount of own evidence,
    however consistent, that should be read as overriding a number nothing said varies at all.
    """
    if n <= 0:
        return 0.0
    if world_variance <= 0.0:
        # A degenerate industry prior carries no variance to compare against; treat it as
        # settled and let it stand rather than fabricating a division by zero.
        return 0.0
    if own_variance <= 0.0:
        # Perfectly consistent own data against a genuinely uncertain prior. Nothing here says
        # how much *more* consistent than the world prior it is, so it takes full weight rather
        # than dividing by zero.
        return 1.0
    k = own_variance / world_variance
    return n / (n + k)


@dataclass(frozen=True)
class Blend:
    subject: str
    n: int
    own_mean: float | None
    own_variance: float
    world: Triple
    world_variance: float
    z: float
    k: float | None
    blended: Triple

    def as_dict(self) -> dict[str, Any]:
        own_mean = self.own_mean if self.own_mean is not None else 0.0
        own_component = quantise(self.z * own_mean)
        world_component = quantise((1.0 - self.z) * self.world.mode)
        return {
            "subject": self.subject,
            "own_data": (
                {"n": self.n, "mean": quantise(own_mean), "variance": quantise(self.own_variance)}
                if self.n
                else {
                    "n": 0, "mean": None, "variance": None,
                    "note": "no own-data observations; pricing from the world-layer prior alone",
                }
            ),
            "world_prior": {**self.world.as_dict(), "variance": quantise(self.world_variance)},
            "credibility": {
                "z": quantise(self.z),
                "k": None if self.k is None else quantise(self.k),
                # Which component of the blended mode came from where — the blend has to be
                # visible in the artefact, not just its result.
                "own_component": own_component,
                "world_component": world_component,
                "note": (
                    "z is the weight on the org's own data; 1-z is the weight on the world-layer "
                    "prior's mode. own_component + world_component is the blended mode below."
                ),
            },
            "blended": self.blended.as_dict(),
            "known_limit": (
                "the blend translates the whole prior triple by the credibility-weighted shift "
                "in its mode, so the width never narrows on a handful of own-data points; nothing "
                "clips the translated bounds, so an own-mean far below a wide prior's mode can in "
                "principle carry the low end negative — clipping would silently narrow the range "
                "from as little as one observation, which is the false precision this avoids"
            ),
        }


def blend(subject: str, industry: Triple, observations: list[float]) -> Blend:
    """The credibility-weighted blend for one subject. Re-run as `observations` accumulates —
    this is a plain function of its inputs, so re-estimating is a normal read, not a re-authoring.
    """
    n = len(observations)
    own_mean = sum(observations) / n if n else None
    own_var = variance(observations)
    world_var = industry.variance
    z = credibility_z(n, own_var, world_var)

    if n == 0 or z == 0.0:
        blended = industry
    else:
        assert own_mean is not None  # n > 0 guarantees it; spelled out for the type checker
        shift = z * (own_mean - industry.mode)
        blended = Triple(industry.low + shift, industry.mode + shift, industry.high + shift)

    k = (own_var / world_var) if (n > 0 and own_var > 0.0 and world_var > 0.0) else None
    return Blend(subject, n, own_mean, own_var, industry, world_var, z, k, blended)
