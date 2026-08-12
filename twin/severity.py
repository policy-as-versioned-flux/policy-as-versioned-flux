"""Heavy-tailed severity, TVaR, and the loss-exceedance curve.

Build ticket 24, from decision ticket 09 (the £'s TVaR-over-VaR commitment) and research 02
(cyber severity is heavy-tailed: ~85% of events cost under $2M while a tiny fraction exceed $1B;
a lognormal body decays too fast to carry that tail, which is exactly why Google TabFM was
rejected — a single-scalar regression head cannot express this shape at all, and a ±4σ clip
amputates it on purpose).

## The composition, and the threshold-selection method

**Peaks-over-threshold, and the threshold is authored, not fit.** Below a declared threshold
`u` the body is lognormal; above it, the *conditional* excess follows a Generalised Pareto
Distribution (GPD). This module accepts `u` as a parameter and does not run a mean-residual-life
plot or a Hill estimator to choose it — that is real empirical work, and it is build ticket 25's
job, not this one's. What this module does declare is the splice: `tail_probability`, the mass
beyond `u`, is **derived** from the lognormal body at `u` rather than authored as a second,
independent number. Two authored numbers describing the same point can disagree; one derived from
the other cannot.

    S(x) = S_lognormal(x)                                          for x <= u
    S(x) = S_lognormal(u) * (1 + xi*(x-u)/beta)^(-1/xi)             for x >  u

`S(u)` on both sides of that boundary is the same number by construction, so the composite is
continuous without a separate matching step to get wrong.

## TVaR, not VaR

VaR names a threshold and says nothing about what lies beyond it — the entire region a heavy-tail
model exists to reason about. TVaR (`E[X | X > VaR_alpha]`, aka expected shortfall) is what
`tvar()` computes, in closed form for a POT-composed tail (McNeil & Frey 2000): two distributions
can share an identical VaR at the threshold's own exceedance probability and diverge sharply in
TVaR once the tail's shape differs — `test_a_var_shaped_summary_hides_what_tvar_surfaces` in
`tests/test_severity.py` builds exactly that pair.

**The shape-parameter boundary.** A GPD's mean is `beta/(1-xi)`, which only exists for `xi < 1`.
At `xi >= 1` the tail is so heavy that "the average loss beyond this point" is not a number, and
`tvar()` refuses rather than returning whatever `(1-xi)` happens to divide into — a boundary this
sharp does not get a silently wrong answer.

`ponytail:` `tvar()` is tail-only — it refuses when the requested confidence level's VaR falls
inside the lognormal body rather than the declared tail, because reaching there needs the
lognormal body's own partial mean (a `∫ x f(x) dx` up to the threshold), a second closed form
this module does not carry. Add it if a caller ever needs TVaR below the anchored tail; every
call this system makes today asks for TVaR at a confidence high enough that the tail already
covers it.

## What this is not

**Not a new severity slot.** `twin/pricing.py` prices a component from the perspective's declared
valuation, on purpose, and the docstring there explains why a second authored magnitude per
component would be a way to launder a price through whichever number is watched less. This module
is a standalone risk-quantification capability — the FAIR engine's tail model — used the way `twin
price` composes a valuation with a propagated influence, not a field on a component.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from typing import Any

from .pert import quantise


class SeverityError(ValueError):
    """Not a severity distribution, or a risk measure asked of it this module cannot honestly answer."""


def _lognormal_survival(x: float, mu: float, sigma: float) -> float:
    if x <= 0.0:
        return 1.0
    return 1.0 - statistics.NormalDist(mu, sigma).cdf(math.log(x))


def _lognormal_quantile(p: float, mu: float, sigma: float) -> float:
    return math.exp(statistics.NormalDist(mu, sigma).inv_cdf(p))


def _gpd_survival(y: float, xi: float) -> float:
    """The GPD survival function at a scaled excess `y = (x - threshold) / beta`, `y >= 0`."""
    if xi == 0.0:
        return math.exp(-y)
    base = 1.0 + xi * y
    if base <= 0.0:
        # xi < 0 gives the GPD a finite right endpoint; beyond it, survival is exactly zero.
        return 0.0
    return base ** (-1.0 / xi)


def _gpd_quantile(q: float, xi: float) -> float:
    """Inverse of `_gpd_survival`: the scaled excess `y` such that `_gpd_survival(y, xi) == q`."""
    if xi == 0.0:
        return -math.log(q)
    return (q ** (-xi) - 1.0) / xi


@dataclass(frozen=True)
class Severity:
    """A lognormal body with a GPD tail, spliced at an authored threshold.

    `mu`/`sigma` are the lognormal body's underlying-normal parameters. `threshold` is the
    peaks-over-threshold cut, authored directly (see the module docstring). `xi`/`beta` are the
    GPD tail's shape and scale.
    """

    mu: float
    sigma: float
    threshold: float
    xi: float
    beta: float

    def __post_init__(self) -> None:
        for name, value in (
            ("mu", self.mu), ("sigma", self.sigma), ("threshold", self.threshold),
            ("xi", self.xi), ("beta", self.beta),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise SeverityError(f"a severity's {name} is {value!r}, which is not a finite number")
        if self.sigma <= 0.0:
            raise SeverityError(f"sigma must be positive, got {self.sigma}")
        if self.threshold <= 0.0:
            raise SeverityError(f"the threshold must be positive, got {self.threshold}")
        if self.beta <= 0.0:
            raise SeverityError(f"the GPD scale beta must be positive, got {self.beta}")

    @property
    def tail_probability(self) -> float:
        """`P(X > threshold)`, derived from the lognormal body — never a second authored number."""
        return _lognormal_survival(self.threshold, self.mu, self.sigma)

    def survival(self, x: float) -> float:
        """`P(X > x)`. The loss-exceedance curve is this function, read at a grid of `x`."""
        if x <= self.threshold:
            return _lognormal_survival(x, self.mu, self.sigma)
        y = (x - self.threshold) / self.beta
        return self.tail_probability * _gpd_survival(y, self.xi)

    def cdf(self, x: float) -> float:
        return 1.0 - self.survival(x)

    def _quantile(self, p: float) -> float:
        """Inverse CDF. Shared by `var()` and `sample()` so both routes to a number agree by
        construction rather than by two implementations staying in sync."""
        if not 0.0 < p < 1.0:
            raise SeverityError(f"a quantile is asked at a probability strictly between 0 and 1, got {p}")
        exceed = 1.0 - p
        tail_probability = self.tail_probability
        if exceed >= tail_probability:
            return _lognormal_quantile(p, self.mu, self.sigma)
        y = _gpd_quantile(exceed / tail_probability, self.xi)
        return self.threshold + self.beta * y

    def var(self, alpha: float) -> float:
        """Value-at-Risk: the loss level exceeded with probability `1 - alpha`."""
        return self._quantile(alpha)

    def tvar(self, alpha: float) -> float:
        """Tail-Value-at-Risk: `E[X | X > VaR_alpha]`. See the module docstring for both refusals."""
        v = self.var(alpha)
        if v < self.threshold:
            raise SeverityError(
                f"VaR at alpha={alpha} is {v}, inside the lognormal body below the declared "
                f"threshold {self.threshold}. This module's TVaR is tail-only (see the module "
                "docstring's ponytail note) — raise alpha, or lower the threshold, so the "
                "confidence level lands in the declared tail."
            )
        if self.xi >= 1.0:
            raise SeverityError(
                f"the GPD shape xi={self.xi} is >= 1, so the tail's mean does not exist. TVaR is "
                "undefined here, not a large or negative number — this is the boundary the "
                "closed-form estimator breaks at, and refusing is the honest answer."
            )
        return v / (1.0 - self.xi) + (self.beta - self.xi * self.threshold) / (1.0 - self.xi)

    def sample(self, rng: random.Random) -> float:
        """One draw, via the same inversion `var()` uses — so a sampled mean and an analytic TVaR
        are two independent routes to the same claim rather than one implementation twice."""
        return self._quantile(rng.random())

    def loss_exceedance_curve(self, alphas: list[float]) -> list[dict[str, Any]]:
        """VaR and TVaR at each confidence level, sorted — the curve as an artefact body.

        TVaR is never omitted silently: a level whose VaR falls below the tail carries
        `tvar: None` and the refusal's reason in `tvar_refused`, so a reader sees *why* a row has
        no tail figure rather than mistaking the absence for a zero.
        """
        out: list[dict[str, Any]] = []
        for alpha in sorted(set(alphas)):
            v = self.var(alpha)
            row: dict[str, Any] = {
                "alpha": quantise(alpha),
                "exceedance_probability": quantise(1.0 - alpha),
                "var": quantise(v),
            }
            try:
                row["tvar"] = quantise(self.tvar(alpha))
                row["tvar_refused"] = None
            except SeverityError as exc:
                row["tvar"] = None
                row["tvar_refused"] = str(exc)
            out.append(row)
        return out

    def as_dict(self) -> dict[str, Any]:
        return {
            "mu": quantise(self.mu),
            "sigma": quantise(self.sigma),
            "threshold": quantise(self.threshold),
            "xi": quantise(self.xi),
            "beta": quantise(self.beta),
            "tail_probability": quantise(self.tail_probability),
            "composition": "lognormal body below the threshold, GPD tail above it, spliced continuously",
        }
