"""Empirical severity anchoring (build ticket 25)."""

from __future__ import annotations

import math

import pytest

from twin.anchoring import AnchoringError, anchored, fit_lognormal, sensitivity, subject_ids
from twin.severity import SeverityError


def test_fit_lognormal_recovers_the_two_cited_quantiles() -> None:
    mu, sigma = fit_lognormal(0.50, 600_000.0, 0.95, 32_000_000.0)
    from statistics import NormalDist

    assert math.exp(mu) == pytest.approx(600_000.0, rel=1e-9)
    assert math.exp(mu + sigma * NormalDist().inv_cdf(0.95)) == pytest.approx(32_000_000.0, rel=1e-6)


def test_fit_lognormal_refuses_two_points_at_the_same_probability() -> None:
    with pytest.raises(AnchoringError, match="same probability"):
        fit_lognormal(0.5, 100.0, 0.5, 200.0)


def test_fit_lognormal_refuses_a_non_increasing_pair() -> None:
    with pytest.raises(AnchoringError, match="not positive"):
        fit_lognormal(0.5, 32_000_000.0, 0.95, 600_000.0)


@pytest.mark.parametrize("p1,p2", [(0.0, 0.5), (0.5, 1.0), (-0.1, 0.5), (0.5, 1.1)])
def test_fit_lognormal_refuses_a_probability_outside_the_open_unit_interval(p1: float, p2: float) -> None:
    with pytest.raises(AnchoringError, match="strictly between 0 and 1"):
        fit_lognormal(p1, 100.0, p2, 200.0)


@pytest.mark.parametrize("x1,x2", [(0.0, 200.0), (-5.0, 200.0), (100.0, 0.0)])
def test_fit_lognormal_refuses_a_non_positive_quantile(x1: float, x2: float) -> None:
    with pytest.raises(AnchoringError, match="must be positive"):
        fit_lognormal(0.5, x1, 0.95, x2)


def test_data_breach_loss_is_the_committed_subject() -> None:
    assert subject_ids() == ["data-breach-loss"]


def test_anchored_severity_reproduces_its_own_cited_quantiles() -> None:
    """The whole point of fitting rather than storing: `var()` at the cited probabilities lands
    back on the cited amounts, so the citation and the code cannot silently drift apart."""
    result = anchored("data-breach-loss")
    lo, hi = result.quantiles[0], result.quantiles[-1]
    assert result.severity.var(float(lo["probability"])) == pytest.approx(float(lo["amount"]), rel=1e-6)
    assert result.severity.var(float(hi["probability"])) == pytest.approx(float(hi["amount"]), rel=1e-6)


def test_anchored_severity_names_which_parameters_are_anchored() -> None:
    result = anchored("data-breach-loss")
    by_name = {p.name: p for p in result.parameters}
    assert by_name["mu"].anchored and by_name["mu"].method
    assert by_name["sigma"].anchored and by_name["sigma"].method
    assert by_name["threshold"].anchored and by_name["threshold"].method
    assert not by_name["xi"].anchored and by_name["xi"].note
    assert not by_name["beta"].anchored and by_name["beta"].note
    body = result.as_dict()
    assert body["anchored_count"] == 3
    assert body["unanchored_count"] == 2


def test_a_threshold_method_other_than_cited_is_refused(tmp_path) -> None:
    """`anchored()` only knows how to honour a threshold cited as a named quantile amount — a
    subject that declares any other method is refused rather than guessed at."""
    import yaml

    from twin.anchoring import ANCHORS_PATH, anchored

    doc = yaml.safe_load(ANCHORS_PATH.read_text(encoding="utf-8"))
    doc["subjects"][0]["parameters"]["threshold"]["method"] = "fit-from-quantiles"
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(doc))
    with pytest.raises(AnchoringError, match="is not 'cited'"):
        anchored("data-breach-loss", bad)


def test_unknown_subject_names_what_exists() -> None:
    with pytest.raises(AnchoringError, match="no-such-subject.*data-breach-loss"):
        anchored("no-such-subject")


def test_a_bad_anchor_file_is_refused_not_silently_loaded(tmp_path) -> None:
    import yaml

    from twin.anchoring import load

    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"schema": "twin.severity-anchors/v1", "version": 1, "subjects": []}))
    with pytest.raises(AnchoringError, match="no anchored subject"):
        load(bad)


def test_an_unanchored_parameter_with_no_reason_is_refused(tmp_path) -> None:
    import yaml

    from twin.anchoring import load

    doc = {
        "schema": "twin.severity-anchors/v1",
        "version": 1,
        "subjects": [{
            "id": "x",
            "quantiles": [
                {"probability": 0.5, "amount": 1.0, "source": "s", "dated": "2026"},
                {"probability": 0.9, "amount": 2.0, "source": "s", "dated": "2026"},
            ],
            "parameters": {
                "mu": {"anchored": True, "method": "fit-from-quantiles"},
                "sigma": {"anchored": True, "method": "fit-from-quantiles"},
                "threshold": {"anchored": True, "method": "cited"},
                "xi": {"anchored": False},  # no reason — this is the planted violation
                "beta": {"anchored": False, "reason": "because"},
            },
        }],
    }
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(doc))
    with pytest.raises(AnchoringError, match="no reason"):
        load(bad)


def test_sensitivity_varies_only_the_unanchored_xi() -> None:
    report = sensitivity("data-breach-loss", alpha=0.99, grid=[0.3, 0.6, 0.9])
    tvars = [row["tvar"] for row in report["grid"] if row["tvar"] is not None]
    assert len(tvars) >= 2
    assert tvars == sorted(tvars), "TVaR should rise monotonically with a heavier xi at fixed alpha"
    assert report["spread"]["max"] > report["spread"]["min"]
    fixed = report["held_fixed"]
    base = anchored("data-breach-loss").severity
    assert fixed["mu"] == pytest.approx(base.mu)
    assert fixed["sigma"] == pytest.approx(base.sigma)
    assert fixed["threshold"] == pytest.approx(base.threshold)


def test_sensitivity_reports_a_refusal_rather_than_dropping_a_row_silently() -> None:
    """A grid point at or past the shape boundary (xi >= 1) still gets a row — refused, not absent."""
    report = sensitivity("data-breach-loss", alpha=0.99, grid=[0.6, 1.0, 1.5])
    by_xi = {row["xi"]: row for row in report["grid"]}
    assert by_xi[1.0]["tvar"] is None
    assert by_xi[1.0]["refused"] is not None
    assert by_xi[0.6]["tvar"] is not None
