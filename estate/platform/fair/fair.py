#!/usr/bin/env python3
"""fair.py — lightweight, deterministic FAIR risk engine (pure stdlib, offline).

Turns versioned (min, mode, max) risk triples into an annual-loss distribution and
reads the board numbers off it: ALE, VaR95, TVaR, and the £ actually carried
(TVaR + a risk load, so the balance sheet never charges the mean).

This is the load-bearing seam for the whole risk thesis: the "£ moves when you
tighten a control" beat is two invocations of this CLI differing by one input.

Deps: none. beta-PERT is sampled via random.betavariate (stdlib Mersenne Twister,
deterministic and portable across platforms given a fixed seed).

Usage:
    fair.py summary   scenarios/driftwood-cart-pii.json [--mode warn|deny]
    fair.py compare   scenarios/driftwood-cart-pii.json     # what a Deny buys
    fair.py selfcheck                                        # runnable asserts

Scenario JSON (versioned triples):
    { "version": "v1", "name": "...",
      "warn": {"lef": [min,mode,max], "lm": [min,mode,max]},
      "deny": {"lef": [min,mode,max], "lm": [min,mode,max]} }
  or a single unnamed control state:
    { "version": "v1", "name": "...", "lef": [...], "lm": [...] }
"""
from __future__ import annotations

import argparse
import json
import random
import sys

# Defaults. ponytail: PERT lambda fixed at 4 (standard FAIR confidence); cost-of-
# capital fixed at Solvency-II's 6% risk-margin rate. Expose per-scenario only if
# an estimator actually needs to widen/narrow either.
ITERATIONS = 10_000
SEED = 42
PERT_LAMBDA = 4.0
COST_OF_CAPITAL = 0.06  # risk load = COC * economic capital (TVaR - ALE)


def pert(lo, mode, hi, n, rng, lam=PERT_LAMBDA):
    """Sample n values from a beta-PERT on [lo, hi] peaked at mode."""
    if hi <= lo:  # degenerate / point estimate
        return [float(lo)] * n
    a = 1.0 + lam * (mode - lo) / (hi - lo)
    b = 1.0 + lam * (hi - mode) / (hi - lo)
    span = hi - lo
    return [lo + rng.betavariate(a, b) * span for _ in range(n)]


def simulate(lef, lm, n=ITERATIONS, seed=SEED):
    """Aggregate annual-loss distribution.

    lef, lm are (min, mode, max) triples. Per simulated year: sample how many loss
    events happen (freq ~ PERT(lef)), then sum a magnitude per event (PERT(lm)).
    Returns a list of annual losses, one per simulated year.
    """
    rng = random.Random(seed)
    freqs = [max(0, round(f)) for f in pert(*lef, n, rng)]
    losses = []
    for f in freqs:
        losses.append(sum(pert(*lm, f, rng)) if f > 0 else 0.0)
    return losses


def percentile(xs, p):
    """Linear-interpolated percentile (numpy 'linear' method) over unsorted xs."""
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    k = (p / 100.0) * (len(s) - 1)
    lo = int(k)
    frac = k - lo
    if lo + 1 >= len(s):
        return s[lo]
    return s[lo] + frac * (s[lo + 1] - s[lo])


def summarize(losses, coc=COST_OF_CAPITAL):
    """The board numbers. ALE = mean, VaR95 = 95th pct, TVaR = mean beyond VaR95.

    £ carried = TVaR + risk load, where risk load = coc * economic capital and
    economic capital = TVaR - ALE (the unexpected loss you must hold capital for).
    By construction TVaR >= VaR95 >= ALE for a right-skewed non-negative loss.
    """
    ale = sum(losses) / len(losses)
    var95 = percentile(losses, 95)
    tail = [x for x in losses if x >= var95]
    tvar = sum(tail) / len(tail) if tail else var95
    econ_capital = tvar - ale
    risk_load = coc * econ_capital
    return {
        "iterations": len(losses),
        "ale": ale,
        "var95": var95,
        "tvar": tvar,
        "economic_capital": econ_capital,
        "risk_load": risk_load,
        "carried": tvar + risk_load,
        "p_gt_0": sum(1 for x in losses if x > 0) / len(losses),
    }


def control_value(warn, deny, n=ITERATIONS, seed=SEED):
    """£ a Deny buys vs Warn. warn/deny are {'lef':triple, 'lm':triple} dicts."""
    a = summarize(simulate(warn["lef"], warn["lm"], n, seed))
    d = summarize(simulate(deny["lef"], deny["lm"], n, seed))
    return {
        "residual_warn": a["ale"],
        "residual_deny": d["ale"],
        "risk_bought": a["ale"] - d["ale"],  # ALE_warn - ALE_deny
        "carried_warn": a["carried"],
        "carried_deny": d["carried"],
        "capital_released": a["carried"] - d["carried"],
        "effectiveness": 1.0 - d["ale"] / max(a["ale"], 1e-9),
        "warn": a,
        "deny": d,
    }


# --- scenario loading ---------------------------------------------------------
def load(path):
    with open(path) as fh:
        return json.load(fh)


def state(scenario, mode):
    """Pull one control state's triples out of a scenario dict."""
    if mode in scenario:
        return scenario[mode]
    if "lef" in scenario and "lm" in scenario:
        return {"lef": scenario["lef"], "lm": scenario["lm"]}
    sys.exit(f"scenario has no '{mode}' block and no top-level lef/lm")


# --- CLI ----------------------------------------------------------------------
def _fmt(d):
    return json.dumps(d, indent=2)


def cmd_summary(args):
    sc = load(args.scenario)
    s = summarize(simulate(**state(sc, args.mode)))
    s = {"version": sc.get("version"), "name": sc.get("name"), "mode": args.mode, **s}
    print(_fmt(s))


def cmd_compare(args):
    sc = load(args.scenario)
    cv = control_value(state(sc, "warn"), state(sc, "deny"))
    cv = {"version": sc.get("version"), "name": sc.get("name"), **cv}
    print(_fmt(cv))


def cmd_selfcheck(_args):
    # Canonical Kindly Ops numbers: LEF(2,4,9), LM(1k,4k,9k) -> mean ~17k, VaR95 ~31k.
    s = summarize(simulate((2, 4, 9), (1_000, 4_000, 9_000)))
    assert 14_000 < s["ale"] < 21_000, s
    assert 26_000 < s["var95"] < 36_000, s
    # The tail ordering that makes the £ never charge the mean.
    assert s["tvar"] >= s["var95"] >= s["ale"], s
    assert s["carried"] >= s["tvar"], s          # risk load is non-negative
    assert s["risk_load"] > 0, s

    # Determinism: same seed -> identical distribution.
    a = simulate((2, 4, 9), (1_000, 4_000, 9_000), seed=7)
    b = simulate((2, 4, 9), (1_000, 4_000, 9_000), seed=7)
    assert a == b, "not deterministic under a fixed seed"

    # A Deny buys positive risk vs Warn (LEF collapsed toward zero).
    cv = control_value(
        {"lef": (2, 4, 9), "lm": (1_000, 4_000, 9_000)},   # warn: full exposure
        {"lef": (0, 0, 1), "lm": (1_000, 4_000, 9_000)},   # deny: loss path closed
    )
    assert cv["risk_bought"] > 0, cv
    assert cv["effectiveness"] > 0.8, cv
    assert cv["capital_released"] > 0, cv                   # frees economic capital
    print("ok  ALE=%.0f VaR95=%.0f TVaR=%.0f carried=%.0f | Deny buys %.0f (%.0f%% effective)" % (
        s["ale"], s["var95"], s["tvar"], s["carried"],
        cv["risk_bought"], 100 * cv["effectiveness"]))


def main(argv=None):
    p = argparse.ArgumentParser(description="Deterministic FAIR risk engine.")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("summary", help="ALE/VaR95/TVaR/carried for one control state")
    ps.add_argument("scenario")
    ps.add_argument("--mode", default="warn", help="warn|deny (default warn)")
    ps.set_defaults(func=cmd_summary)

    pc = sub.add_parser("compare", help="what flipping Warn->Deny buys")
    pc.add_argument("scenario")
    pc.set_defaults(func=cmd_compare)

    pk = sub.add_parser("selfcheck", help="run the engine's assertions")
    pk.set_defaults(func=cmd_selfcheck)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
