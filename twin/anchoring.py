"""Empirical anchoring for `twin/severity.py` (build ticket 25), from decision ticket 09 and
research 02. Separated from ticket 24's module for the reason its docstring already gives: the
splice/TVaR maths and the empirical work are different jobs, and each needed its own window.

**Two parameters cited directly, two fit by closed-form two-point calibration, two left
unanchored.** `twin/severity-anchors.yaml` names which is which and why, per subject. This module
only does the arithmetic and the loading; the citations and the honesty about what has no
defensible anchor live in the data file, because a re-anchoring has to be a diff against a
version number rather than a code change nobody would think to review as data.

**The two-point lognormal fit is exact, not a numerical solve.** A lognormal's quantile is
`exp(mu + sigma * z(p))`, so two cited quantiles at two probabilities give two linear equations
in `(mu, sigma)`, solved in closed form (`fit_lognormal`). Precisely because it is closed-form,
it is unforgiving of a bad pair: two cited quantiles at the *same* probability, or citing the same
probability twice, is refused rather than left to divide by zero.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR
from .canon import digest_of
from .severity import Severity, SeverityError

ANCHORS_PATH = PACKAGE_DIR / "severity-anchors.yaml"
SCHEMA = "twin.severity-anchors/v1"


class AnchoringError(RuntimeError):
    """The anchor file does not say what it must, or a fit was asked of data that cannot give one."""


def fit_lognormal(p1: float, x1: float, p2: float, x2: float) -> tuple[float, float]:
    """`(mu, sigma)` such that the lognormal's `p1`-quantile is `x1` and `p2`-quantile is `x2`.

    Exact: `ln(quantile(p)) = mu + sigma * z(p)` is linear in `(mu, sigma)`, so two distinct
    points solve it directly rather than by search. Refuses two points at the same probability —
    that is one equation wearing two names, not two equations.
    """
    if not (0.0 < p1 < 1.0 and 0.0 < p2 < 1.0):
        raise AnchoringError(f"a quantile probability must be strictly between 0 and 1, got {p1} and {p2}")
    if x1 <= 0.0 or x2 <= 0.0:
        raise AnchoringError(f"a lognormal quantile must be positive, got {x1} and {x2}")
    z1, z2 = statistics.NormalDist().inv_cdf(p1), statistics.NormalDist().inv_cdf(p2)
    if z1 == z2:
        raise AnchoringError(
            f"two quantiles cited at the same probability ({p1}) fit nothing; a two-point "
            "calibration needs two distinct probabilities"
        )
    sigma = (math.log(x2) - math.log(x1)) / (z2 - z1)
    if sigma <= 0.0:
        raise AnchoringError(
            f"the fitted sigma is {sigma}, not positive — the higher-probability quantile "
            f"({p2}={x2}) must cite a larger amount than the lower one ({p1}={x1})"
        )
    mu = math.log(x1) - sigma * z1
    return mu, sigma


@dataclass(frozen=True)
class Parameter:
    name: str
    value: float
    anchored: bool
    method: str | None
    note: str | None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "value": self.value, "anchored": self.anchored}
        if self.method:
            out["method"] = self.method
        if self.note:
            out["note"] = self.note
        return out


@dataclass(frozen=True)
class Anchored:
    """One subject's fitted severity, with per-parameter anchoring provenance attached."""

    subject: str
    description: str
    quantiles: tuple[dict[str, Any], ...]
    parameters: tuple[Parameter, ...]
    severity: Severity

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "description": self.description,
            "cited_quantiles": [dict(q) for q in self.quantiles],
            "parameters": [p.as_dict() for p in self.parameters],
            "anchored_count": sum(1 for p in self.parameters if p.anchored),
            "unanchored_count": sum(1 for p in self.parameters if not p.anchored),
            "severity": self.severity.as_dict(),
        }


@lru_cache(maxsize=8)
def load(path: Path | None = None) -> dict[str, Any]:
    """The versioned anchor set, validated on read — the same discipline the constraint set and
    the evidence ladder apply: an anchor file that has quietly lost a citation still looks cited."""
    source = path or ANCHORS_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise AnchoringError(f"{source}: not a {SCHEMA} document")
    subjects = doc.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        raise AnchoringError(f"{source}: declares no anchored subject")
    ids = set()
    for entry in subjects:
        sid = str(entry.get("id", ""))
        if not sid:
            raise AnchoringError(f"{source}: a subject declares no id")
        if sid in ids:
            raise AnchoringError(f"{source}: subject {sid!r} declared twice")
        ids.add(sid)
        quantiles = entry.get("quantiles")
        if not isinstance(quantiles, list) or len(quantiles) < 2:
            raise AnchoringError(
                f"{source}: subject {sid!r} cites {len(quantiles) if isinstance(quantiles, list) else 0} "
                "quantile(s); a two-point calibration needs at least two"
            )
        for q in quantiles:
            missing = [f for f in ("probability", "amount", "source", "dated") if not str(q.get(f, "")).strip()]
            if missing:
                raise AnchoringError(f"{source}: subject {sid!r} has a quantile missing {', '.join(missing)}")
        params = entry.get("parameters")
        if not isinstance(params, dict):
            raise AnchoringError(f"{source}: subject {sid!r} declares no parameters")
        for name in ("mu", "sigma", "threshold", "xi", "beta"):
            if name not in params:
                raise AnchoringError(f"{source}: subject {sid!r} declares no {name!r} parameter")
            p = params[name]
            if "anchored" not in p:
                raise AnchoringError(f"{source}: subject {sid!r} parameter {name!r} does not say anchored: true|false")
            if p["anchored"] and not p.get("method"):
                raise AnchoringError(
                    f"{source}: subject {sid!r} parameter {name!r} is marked anchored with no method — "
                    "an anchored parameter with nothing saying how it was fit is a stated number wearing "
                    "the anchored label"
                )
            if not p["anchored"] and not p.get("reason"):
                raise AnchoringError(
                    f"{source}: subject {sid!r} parameter {name!r} is marked unanchored with no reason — "
                    "'unanchored' is a claim too, and it needs a reason the same way a checked "
                    "acceptance-criterion needs evidence"
                )
    return doc


def pin(path: Path | None = None) -> dict[str, Any]:
    doc = load(path)
    return {"version": int(doc["version"]), "digest": digest_of(doc)}


def subject_ids(path: Path | None = None) -> list[str]:
    return sorted(str(s["id"]) for s in load(path)["subjects"])


def anchored(subject_id: str, path: Path | None = None) -> Anchored:
    """Build the `Severity` a subject's cited quantiles and unanchored illustrative values imply.

    `mu`/`sigma`/`threshold` are recomputed here from the cited quantiles rather than read as
    stored numbers — a stored fitted value could silently drift from the citations that are
    supposed to justify it, and recomputing on every load is what keeps the two the same thing.
    """
    doc = load(path)
    entry = next((s for s in doc["subjects"] if str(s["id"]) == subject_id), None)
    if entry is None:
        raise AnchoringError(f"no anchored subject {subject_id!r} (have: {', '.join(subject_ids(path))})")

    quantiles = sorted(entry["quantiles"], key=lambda q: float(q["probability"]))
    if len(quantiles) < 2:
        raise AnchoringError(f"subject {subject_id!r} cites fewer than two quantiles")
    lo, hi = quantiles[0], quantiles[-1]
    try:
        mu, sigma = fit_lognormal(
            float(lo["probability"]), float(lo["amount"]), float(hi["probability"]), float(hi["amount"])
        )
    except AnchoringError as exc:
        raise AnchoringError(f"subject {subject_id!r}: {exc}") from exc

    params = entry["parameters"]
    threshold_p = params["threshold"]
    # `cited` means "equal to a named quantile amount" (see the module docstring); anything else
    # this module does not know how to honour, so it refuses rather than guessing at intent.
    if threshold_p["method"] != "cited":
        raise AnchoringError(f"subject {subject_id!r}: threshold method {threshold_p['method']!r} is not 'cited'")
    threshold = float(hi["amount"])

    xi_p, beta_p = params["xi"], params["beta"]
    xi = float(xi_p.get("illustrative_value", xi_p.get("value")))
    beta = float(beta_p.get("illustrative_value", beta_p.get("value")))

    try:
        severity = Severity(mu=mu, sigma=sigma, threshold=threshold, xi=xi, beta=beta)
    except SeverityError as exc:
        raise AnchoringError(f"subject {subject_id!r}: fitted parameters do not compose: {exc}") from exc

    parameters = (
        Parameter("mu", mu, True, params["mu"].get("method"), params["mu"].get("note")),
        Parameter("sigma", sigma, True, params["sigma"].get("method"), params["sigma"].get("note")),
        Parameter("threshold", threshold, True, "cited", threshold_p.get("note")),
        Parameter("xi", xi, False, None, xi_p.get("reason")),
        Parameter("beta", beta, False, None, beta_p.get("reason")),
    )
    return Anchored(
        subject=subject_id,
        description=str(entry.get("description", "")).strip(),
        quantiles=tuple(dict(q) for q in quantiles),
        parameters=parameters,
        severity=severity,
    )


def sensitivity(subject_id: str, alpha: float, grid: list[float], path: Path | None = None) -> dict[str, Any]:
    """How far the headline TVaR at `alpha` moves as the unanchored `xi` sweeps `grid`, holding
    every other parameter fixed (AC: sensitivity of the headline outputs to each anchor).

    `mu`/`sigma`/`threshold` and `beta` are the subject's fit/illustrative values throughout —
    only `xi` varies, so a reader sees what moving the *unanchored shape* parameter alone does,
    not a conflation with the anchored ones or with `beta` (also unanchored, but held fixed here
    rather than swept, so the grid isolates one parameter at a time).
    """
    base = anchored(subject_id, path)
    rows = []
    for xi in sorted(set(grid)):
        candidate = Severity(
            mu=base.severity.mu, sigma=base.severity.sigma, threshold=base.severity.threshold,
            xi=xi, beta=base.severity.beta,
        )
        row: dict[str, Any] = {"xi": xi}
        try:
            row["tvar"] = candidate.tvar(alpha)
            row["refused"] = None
        except SeverityError as exc:
            row["tvar"] = None
            row["refused"] = str(exc)
        rows.append(row)
    computed = [r["tvar"] for r in rows if r["tvar"] is not None]
    return {
        "subject": subject_id,
        "alpha": alpha,
        "varying": "xi",
        "held_fixed": {"mu": base.severity.mu, "sigma": base.severity.sigma, "threshold": base.severity.threshold,
                       "beta": base.severity.beta},
        "grid": rows,
        "spread": {
            "min": min(computed) if computed else None,
            "max": max(computed) if computed else None,
            "note": (
                "min/max TVaR across the grid, holding every anchored (cited or fit-from-quantiles) "
                "parameter fixed — the spread this reports is entirely attributable to the "
                "unanchored xi, which is exactly the parameter twin/severity-anchors.yaml marks as such"
            ),
        },
    }
