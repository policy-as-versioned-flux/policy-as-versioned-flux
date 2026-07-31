#!/usr/bin/env python3
"""calibration.py — is the £ honest *today*? Back-test it against real losses and
recalibrate with Bühlmann credibility (pure stdlib, offline).

Story 17: the £ must stay falsifiable. A number nobody ever checks against the
world is a vibe with a currency symbol. This does two honest things:

  1. BACK-TEST — take the FAIR model's prediction (per-org warn-state ALE + VaR95
     from ../fair/fair.py) and hold it against the incident log (real annual
     losses + near-misses). Report the prediction error and the VaR exceedance
     rate: did actuals breach the 95th percentile more than ~5% of the time?
     Too many breaches -> the model under-prices; zero breaches over many years
     -> it over-prices. That is the falsifiable test an auditor/insurer wants.

  2. RECALIBRATE — classic Bühlmann credibility over the *portfolio* of orgs.
     Each org's credibility premium blends its own observed mean with the
     collective (grand) mean:

         Z_i     = n / (n + k)               credibility weight
         k       = EPV / VHM                 Bühlmann's constant (portfolio-estimated)
         prem_i  = Z_i * Xbar_i + (1 - Z_i) * mu       shrink toward the collective

     A sparse, noisy org (few years, high within-year variance -> big EPV -> big
     k -> small Z) is pulled toward the collective; a data-rich, distinct org
     (its mean far from its peers -> big VHM -> small k -> big Z) keeps its own
     experience. The recalibration factor prem_i / model_ale_i is the reviewable
     diff that re-tunes the £ -- same "a number, not a timer" discipline as
     enforce.py: fair.py itself is never edited.

ponytail: classic Bühlmann (equal exposure per org-year), not Bühlmann-Straub.
Straub's varying weights buy nothing until org-years differ in exposure; add the
w_ij weights when the incident log carries per-year exposure. The credibility
maths is exact for the equal-exposure case we have.

Usage:
    calibration.py backtest    [--incidents incidents.json]   # model vs actuals
    calibration.py recalibrate [--incidents incidents.json]   # Bühlmann premiums + £ factor
    calibration.py selfcheck
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Reuse the FAIR engine — the single source of the £ maths. No new risk engine.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fair"))
import fair  # noqa: E402

DEFAULT_INCIDENTS = os.path.join(HERE, "incidents.json")


def _mean(xs):
    return sum(xs) / len(xs)


def _sample_var(xs):
    """Unbiased (n-1) sample variance; 0 for a single point."""
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


# --- Bühlmann credibility over the portfolio ----------------------------------
def buhlmann(org_losses):
    """Classic Bühlmann credibility premiums for a portfolio of equal-exposure risks.

    org_losses: {org: [annual_loss, ...]} — same n per org (equal exposure).
    Returns per-org {xbar, Z, premium} plus the shared {mu, EPV, VHM, k}.

    EPV = mean within-org variance (the irreducible process noise).
    VHM = between-org variance of the means, de-biased by EPV/n (the signal that
          orgs genuinely differ). k = EPV/VHM: how many org-years of data it takes
          to trust an org's own experience as much as the collective.
    """
    orgs = list(org_losses)
    n = len(next(iter(org_losses.values())))
    xbars = {o: _mean(org_losses[o]) for o in orgs}
    mu = _mean(list(xbars.values()))

    epv = _mean([_sample_var(org_losses[o]) for o in orgs])
    var_of_means = _sample_var(list(xbars.values()))
    vhm = var_of_means - epv / n            # de-bias: observed spread includes EPV/n
    vhm = max(vhm, 1e-9)                     # floor: orgs differ at least infinitesimally
    k = epv / vhm
    z = n / (n + k)

    out = {"mu": mu, "epv": epv, "vhm": vhm, "k": k, "z": z, "n": n, "orgs": {}}
    for o in orgs:
        premium = z * xbars[o] + (1 - z) * mu
        out["orgs"][o] = {"xbar": xbars[o], "premium": premium}
    return out


# --- back-test: model prediction vs the world ---------------------------------
def backtest_org(scenario, losses, near_misses):
    """Hold the FAIR model against one org's incident history.

    Model prediction is the warn-state (control still Audits, loss path open) ALE
    and VaR95 — what we'd have carried. Compare to observed annual losses; count
    VaR95 exceedances (expected ~5%). near_misses back-test the LEF assumption:
    every event that reached the control (a loss year or a near-miss) is a draw on
    the modelled loss-event frequency.
    """
    warn = fair.state(scenario, "warn")
    s = fair.summarize(fair.simulate(warn["lef"], warn["lm"]))
    model_ale, var95 = s["ale"], s["var95"]

    obs_ale = _mean(losses)
    exceedances = sum(1 for x in losses if x > var95)
    loss_years = sum(1 for x in losses if x > 0)
    # Observed event frequency = loss-causing years + near-misses that the control
    # caught; the modelled LEF mode is the prediction for that rate.
    obs_event_freq = (loss_years + sum(near_misses)) / len(losses)
    model_lef_mode = warn["lef"][1]

    return {
        "model_ale": model_ale,
        "observed_ale": obs_ale,
        "ale_error": obs_ale - model_ale,
        "ale_ratio": obs_ale / model_ale if model_ale else float("inf"),
        "var95": var95,
        "exceedances": exceedances,
        "exceedance_rate": exceedances / len(losses),
        "years": len(losses),
        "model_lef_mode": model_lef_mode,
        "observed_event_freq": obs_event_freq,
        # honest verdict: is the model defensible, or does it need a look?
        "verdict": _backtest_verdict(exceedances, len(losses), obs_ale, model_ale),
    }


def _backtest_verdict(exceedances, years, obs_ale, model_ale):
    # Expected VaR95 breaches ~= 5% of years. A binomial with n<10 is too small for
    # Kupiec, so use a plain-English rule an auditor can follow.
    expected = 0.05 * years
    if exceedances > max(1, 2 * expected):
        return "under-prices (too many VaR95 breaches) — recalibrate up"
    if obs_ale > 1.5 * model_ale:
        return "under-prices (actuals run hot) — recalibrate up"
    if obs_ale < 0.5 * model_ale and model_ale > 0:
        return "over-prices (actuals run cold) — recalibrate down"
    return "defensible (actuals inside the modelled band)"


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _org_losses(incidents):
    return {o: incidents["orgs"][o]["annual_losses_gbp"] for o in incidents["orgs"]}


def _scenario_path(incidents, org):
    return os.path.normpath(os.path.join(HERE, incidents["orgs"][org]["scenario"]))


# --- commands -----------------------------------------------------------------
def run_backtest(incidents):
    out = {}
    for org, rec in incidents["orgs"].items():
        sc = _load(_scenario_path(incidents, org))
        out[org] = backtest_org(sc, rec["annual_losses_gbp"], rec.get("near_misses", []))
    return out


def run_recalibrate(incidents):
    cred = buhlmann(_org_losses(incidents))
    out = {"buhlmann": {k: cred[k] for k in ("mu", "epv", "vhm", "k", "z", "n")}, "orgs": {}}
    for org, rec in incidents["orgs"].items():
        sc = _load(_scenario_path(incidents, org))
        warn = fair.state(sc, "warn")
        model_ale = fair.summarize(fair.simulate(warn["lef"], warn["lm"]))["ale"]
        prem = cred["orgs"][org]["premium"]
        out["orgs"][org] = {
            "observed_mean": cred["orgs"][org]["xbar"],
            "credibility_premium": prem,       # Z-blended actuals
            "model_ale": model_ale,            # what fair.py predicts today
            # the reviewable diff: multiply the scenario's LM by this to re-tune £.
            "recalibration_factor": prem / model_ale if model_ale else float("inf"),
        }
    return out


def cmd_backtest(args):
    print(json.dumps(run_backtest(_load(args.incidents)), indent=2))


def cmd_recalibrate(args):
    print(json.dumps(run_recalibrate(_load(args.incidents)), indent=2))


def cmd_selfcheck(_args):
    inc = _load(DEFAULT_INCIDENTS)
    org_losses = _org_losses(inc)

    # --- Bühlmann properties ---------------------------------------------------
    cred = buhlmann(org_losses)
    assert 0.0 < cred["z"] < 1.0, cred                       # credibility is a proper weight
    mu = cred["mu"]
    for o, r in cred["orgs"].items():
        # Shrinkage: every premium sits between the org's own mean and the collective.
        lo, hi = sorted((r["xbar"], mu))
        assert lo - 1e-6 <= r["premium"] <= hi + 1e-6, (o, r, mu)

    # A hotter-than-collective org is priced above the collective, a cooler one below
    # (direction of credibility, not just the interval).
    hottest = max(cred["orgs"], key=lambda o: cred["orgs"][o]["xbar"])
    coolest = min(cred["orgs"], key=lambda o: cred["orgs"][o]["xbar"])
    assert cred["orgs"][hottest]["premium"] >= mu >= cred["orgs"][coolest]["premium"], cred

    # More data -> more credibility (Z rises with n; k held by the same portfolio).
    long = {o: v * 4 for o, v in org_losses.items()}         # 4x the years, same pattern
    assert buhlmann(long)["z"] > cred["z"], "Z must rise with more org-years"

    # k falls (Z rises) when orgs are more distinct (VHM up); rises when noisier (EPV up).
    distinct = {"a": [10, 10, 10], "b": [1000, 1000, 1000], "c": [50, 50, 50]}
    noisy = {"a": [0, 20, 0], "b": [0, 2000, 0], "c": [0, 100, 0]}
    assert buhlmann(distinct)["k"] < buhlmann(noisy)["k"], "distinct orgs must earn lower k"

    # --- back-test properties --------------------------------------------------
    bt = run_backtest(inc)
    for org, r in bt.items():
        assert r["var95"] >= r["model_ale"], (org, r)        # tail sits above the mean
        assert 0.0 <= r["exceedance_rate"] <= 1.0, (org, r)
        assert isinstance(r["verdict"], str) and r["verdict"], (org, r)

    # The log is deliberately authored so at least one org runs hot enough to fail
    # the back-test — an honesty layer that can never say "recalibrate" is theatre.
    assert any("recalibrate" in r["verdict"] for r in bt.values()), \
        "incident log must exercise a real recalibration verdict"

    # --- recalibration re-tunes the £ toward the credibility premium -----------
    rc = run_recalibrate(inc)
    for org, r in rc["orgs"].items():
        assert r["recalibration_factor"] > 0, (org, r)
        # Applying the factor moves the model ALE onto the credibility premium.
        assert abs(r["model_ale"] * r["recalibration_factor"] - r["credibility_premium"]) < 1.0, (org, r)

    hot = bt[hottest]
    print(
        "ok  Bühlmann Z=%.2f k=%.0f mu=£%.0f | back-test %s: model £%.0f vs actual £%.0f "
        "(%d/%d VaR95 breaches) -> %s"
        % (cred["z"], cred["k"], mu, hottest, hot["model_ale"], hot["observed_ale"],
           hot["exceedances"], hot["years"], hot["verdict"])
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Back-test + Bühlmann-recalibrate the £.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in (
        ("backtest", cmd_backtest, "model prediction vs the incident log"),
        ("recalibrate", cmd_recalibrate, "Bühlmann credibility premiums + £ recalibration factor"),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("--incidents", default=DEFAULT_INCIDENTS)
        sp.set_defaults(func=fn)
    sub.add_parser("selfcheck", help="run the calibration assertions").set_defaults(func=cmd_selfcheck)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
