#!/usr/bin/env python3
"""cage.py — the graded enforcement envelope: tiers over dials, the £ picks the tier.

Deny is only the bottom rung. A behind-posture workload does not get a blunt
admit/deny — it keeps running, *caged by degree*. This module is the source of
truth for:

  1. NAMED TIERS -> DIAL SETTINGS, deterministically (PSS-style presets over the
     independent dials Kyverno actually injects: cpu/mem limits, drop-ALL-caps,
     read-only-fs, an eviction PriorityClass, a WAF sidecar). One table; the
     `cage-tier` MutatingPolicy mirrors it (verify-graded.sh cross-checks drift).

  2. THE £ SELECTS THE TIER. A cage is a *priced partial-reduce on a retained
     risk*: it collapses part of the behind-posture residual (R' > 0 still) at a
     booked run-cost (C_cage > 0). Given the workload's uncaged residual ALE and
     the org's appetite band, pick the LOOSEST tier whose caged residual still
     fits — else Deny (the bottom rung). Same behind-posture workload -> baseline
     in loose-appetite driftwood, quarantine in strict-appetite ludlow.

  3. TCoR EMITTED. Total Cost of Risk of the chosen cage = caged residual +
     cost-of-controls (the cage's run-cost). Booked to the ledger, same shape the
     nist OSCAL risk / ico penalty consumers read.

Reuses ../fair/fair.py (the £ maths) and ../risk/enforce.py (the appetite band).
No new risk engine, no new appetite store.

Usage:
    cage.py dials <tier>                                   # tier -> dial JSON
    cage.py select <scenario.json> --org driftwood         # £ picks tier + TCoR
    cage.py selfcheck
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Reuse the £ engine and the appetite band — single sources of truth, one dir over.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fair"))
sys.path.insert(0, os.path.join(HERE, "..", "risk"))
import fair  # noqa: E402
import enforce  # noqa: E402

# --- The tier table: PSS-style presets over the dials Kyverno injects ----------
# `reduce`  = fraction of the behind-posture residual this cage collapses (R' shrinks).
# `cost`    = C_cage, the £/yr to OPERATE the cage (WAF sidecar compute + eviction
#             churn). Booked as cost-of-controls in TCoR. Both R' and C_cage stay
#             positive for any real cage — a cage retains-with-mitigation, it does
#             not close the loss path (that is what Deny, the bottom rung, does).
# The rest are the literal dials the `cage-tier` MutatingPolicy stamps onto the pod.
# ponytail: reduce/cost are calibration knobs — tune to real WAF/eviction telemetry;
# the ORDERING (tighter => more reduce AND more cost) is what the selection relies on.
TIERS = {
    "baseline": {
        "reduce": 0.30, "cost": 500,
        "cpu": "500m", "mem": "256Mi",
        "priorityClass": "cage-baseline", "dropAll": False, "readOnlyRootFs": False,
        "waf": "none",
    },
    "restricted": {
        "reduce": 0.70, "cost": 2000,
        "cpu": "250m", "mem": "128Mi",
        "priorityClass": "cage-restricted", "dropAll": True, "readOnlyRootFs": True,
        "waf": "light",
    },
    "quarantine": {
        "reduce": 0.92, "cost": 6000,
        "cpu": "100m", "mem": "64Mi",
        "priorityClass": "cage-quarantine", "dropAll": True, "readOnlyRootFs": True,
        "waf": "heavy",
    },
}
# Loosest -> tightest. The selection walks this order and stops at the first fit.
ORDER = ["baseline", "restricted", "quarantine"]


def dials(tier):
    """The deterministic tier -> dial-settings expansion. Pure lookup, no surprises."""
    if tier not in TIERS:
        sys.exit(f"unknown tier '{tier}' (known: {', '.join(ORDER)})")
    return dict(TIERS[tier])


def caged_residual(uncaged_ale, tier):
    """Residual ALE that survives this cage. R' = ALE * (1 - reduce), still > 0."""
    return uncaged_ale * (1.0 - TIERS[tier]["reduce"])


def tcor(uncaged_ale, tier):
    """Total Cost of Risk of running this cage = residual + cost-of-controls.

    (Transfer/premium is a separate line the risk officer may add; a bare cage
    books residual + C_cage.)
    """
    residual = caged_residual(uncaged_ale, tier)
    controls = float(TIERS[tier]["cost"])
    return {
        "tier": tier,
        "residual": residual,          # R' — retained, priced, still positive
        "cost_of_controls": controls,  # C_cage — the cage's run-cost
        "tcor": residual + controls,
    }


def select_tier(uncaged_ale, tolerance):
    """The £ picks the tier: loosest cage whose residual fits the appetite band.

    Deny is the bottom rung — reached only when even the tightest cage leaves a
    residual over the band. Deterministic: a pure function of (residual, band).
    """
    for tier in ORDER:
        if caged_residual(uncaged_ale, tier) <= tolerance:
            return tier
    return "deny"


def select(scenario, org, tolerance):
    """Full graded decision for a behind-posture workload + its TCoR ledger line."""
    st = fair.state(scenario, "behind")
    uncaged = fair.summarize(fair.simulate(st["lef"], st["lm"]))["ale"]
    tier = select_tier(uncaged, tolerance)
    out = {
        "version": scenario.get("version"),
        "name": scenario.get("name"),
        "org": org,
        "uncaged_residual": uncaged,
        "tolerance": tolerance,
        "tier": tier,
    }
    if tier == "deny":
        out["action"] = "Deny"          # bottom rung: the loss path is closed, not caged
        out["reason"] = (
            f"even quarantine leaves £{caged_residual(uncaged, 'quarantine'):,.0f} "
            f"> band £{tolerance:,.0f} -> Deny (bottom rung)"
        )
        return out
    out["action"] = "Cage"
    out["dials"] = dials(tier)
    out["tcor"] = tcor(uncaged, tier)
    out["reason"] = (
        f"uncaged £{uncaged:,.0f}; {tier} cage -> residual "
        f"£{out['tcor']['residual']:,.0f} + controls £{out['tcor']['cost_of_controls']:,.0f} "
        f"= TCoR £{out['tcor']['tcor']:,.0f} (fits band £{tolerance:,.0f})"
    )
    return out


# --- CLI ----------------------------------------------------------------------
def cmd_dials(args):
    print(json.dumps(dials(args.tier), indent=2))


def cmd_select(args):
    sc = fair.load(args.scenario)
    tol = enforce.tolerance_for(args.org, args.appetite)
    print(json.dumps(select(sc, args.org, tol), indent=2))


def cmd_selfcheck(_args):
    # 1. Tier -> dials is deterministic and total over the catalogue.
    for t in ORDER:
        assert dials(t) == dials(t) == TIERS[t], t
        assert set(dials(t)) >= {"cpu", "mem", "priorityClass", "dropAll",
                                 "readOnlyRootFs", "waf", "reduce", "cost"}, t

    # 2. Tighter tier => more risk collapsed AND more run-cost (the monotonicity the
    #    £-selection relies on). No tier fully closes the loss path (that is Deny).
    reduces = [TIERS[t]["reduce"] for t in ORDER]
    costs = [TIERS[t]["cost"] for t in ORDER]
    assert reduces == sorted(reduces) and costs == sorted(costs), (reduces, costs)
    for t in ORDER:
        assert 0.0 < TIERS[t]["reduce"] < 1.0, t   # R' stays > 0: retained, not closed
        assert TIERS[t]["cost"] > 0, t             # C_cage booked

    # 3. The £ selects the tier: as the band tightens on a FIXED residual, the cage
    #    tightens deterministically, and an impossibly-tight band falls through to Deny.
    r = 30_000.0
    assert select_tier(r, 40_000) == "baseline",   select_tier(r, 40_000)
    assert select_tier(r, 20_000) == "restricted", select_tier(r, 20_000)
    assert select_tier(r, 5_000) == "quarantine",  select_tier(r, 5_000)
    assert select_tier(r, 1_000) == "deny",        select_tier(r, 1_000)

    # 4. TCoR is booked as residual + cost-of-controls, both positive (priced
    #    partial-reduce on a RETAINED risk), and tightening trades residual for cost.
    t_loose = tcor(r, "baseline")
    t_tight = tcor(r, "quarantine")
    assert t_loose["residual"] > t_tight["residual"] > 0, (t_loose, t_tight)
    assert t_tight["cost_of_controls"] > t_loose["cost_of_controls"] > 0, (t_loose, t_tight)
    assert t_loose["tcor"] == t_loose["residual"] + t_loose["cost_of_controls"]

    # 5. Same behind-posture workload, real scenario: loose driftwood cages light,
    #    strict ludlow cages hard — proportionality, tier edition (reuses appetite.json).
    sc = fair.load(os.path.join(HERE, "scenarios", "driftwood-behind-posture.json"))
    dw = select(sc, "driftwood", enforce.tolerance_for("driftwood"))
    lud = select(sc, "ludlow", enforce.tolerance_for("ludlow"))
    assert dw["action"] == "Cage" and lud["action"] == "Cage", (dw, lud)
    assert ORDER.index(dw["tier"]) < ORDER.index(lud["tier"]), (dw["tier"], lud["tier"])

    print(
        "ok  tiers %s | £ picks: band40k->%s band20k->%s band5k->%s band1k->deny | "
        "scenario £%.0f: driftwood->%s (TCoR £%.0f), ludlow->%s (TCoR £%.0f)"
        % (ORDER, "baseline", "restricted", "quarantine",
           dw["uncaged_residual"], dw["tier"], dw["tcor"]["tcor"],
           lud["tier"], lud["tcor"]["tcor"])
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Graded enforcement: tiers over dials, the £ picks the tier.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pd = sub.add_parser("dials", help="deterministic tier -> dial-settings expansion")
    pd.add_argument("tier")
    pd.set_defaults(func=cmd_dials)

    psel = sub.add_parser("select", help="the £ picks the tier + emits the TCoR ledger line")
    psel.add_argument("scenario")
    psel.add_argument("--org", required=True)
    psel.add_argument("--appetite", default=enforce.DEFAULT_APPETITE)
    psel.set_defaults(func=cmd_select)

    pk = sub.add_parser("selfcheck", help="run the graded-envelope assertions")
    pk.set_defaults(func=cmd_selfcheck)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
