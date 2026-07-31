#!/usr/bin/env python3
"""enforce.py — the £ picks Audit or Deny (pure stdlib, offline, no date logic).

The proportionality decision, made a number instead of a vibe. Reads a versioned
FAIR scenario (warn/deny triples) and an org's risk-appetite tolerance band, then:

    risk_bought = ALE_warn - ALE_deny        # what escalating to Deny buys
    verdict     = Deny  if risk_bought > tolerance  else  Audit

That verdict IS the Kyverno `validationActions` value. So tightening a versioned
triple raises ALE_warn, pushes risk_bought over the band, and flips Audit->Deny —
in a reviewable PR whose justification is the £, never a timer (ADR-0006).

Reuses the load-bearing maths in ../fair/fair.py (control_value); adds only the
appetite comparison. No new risk engine.

Usage:
    enforce.py decide <scenario.json> --org driftwood [--appetite appetite.json]
    enforce.py action <scenario.json> --org driftwood     # bare 'Audit'|'Deny'
    enforce.py selfcheck
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Reuse the FAIR engine one dir over — it is the single source of the £ maths.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fair"))
import fair  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_APPETITE = os.path.join(HERE, "appetite.json")


def tolerance_for(org, appetite_path=DEFAULT_APPETITE):
    with open(appetite_path) as fh:
        appetite = json.load(fh)
    orgs = appetite.get("orgs", {})
    if org not in orgs:
        sys.exit(f"no risk appetite declared for org '{org}' in {appetite_path}")
    return float(orgs[org]["tolerance"])


def decide(scenario, org, tolerance):
    """Return the enforcement decision + the number that justifies it.

    verdict = Deny iff the risk a Deny buys (ALE_warn - ALE_deny) exceeds the
    org's tolerance band. No dates, no timers — a pure function of the £.
    """
    cv = fair.control_value(fair.state(scenario, "warn"), fair.state(scenario, "deny"))
    risk_bought = cv["risk_bought"]  # ALE_warn - ALE_deny
    verdict = "Deny" if risk_bought > tolerance else "Audit"
    headroom = tolerance - risk_bought
    return {
        "version": scenario.get("version"),
        "name": scenario.get("name"),
        "org": org,
        "verdict": verdict,
        "validationActions": [verdict],
        "residual_warn": cv["residual_warn"],   # ALE_warn (Audit still ships)
        "residual_deny": cv["residual_deny"],   # ALE_deny (path closed)
        "risk_bought": risk_bought,             # ALE_warn - ALE_deny
        "tolerance": tolerance,
        "headroom": headroom,                   # <0 means over-band -> Deny
        "reason": (
            f"risk_bought £{risk_bought:,.0f} "
            f"{'>' if verdict == 'Deny' else '<='} tolerance £{tolerance:,.0f} "
            f"-> {verdict} (justified by the £, not a timer)"
        ),
    }


# --- CLI ----------------------------------------------------------------------
def cmd_decide(args):
    sc = fair.load(args.scenario)
    print(json.dumps(decide(sc, args.org, tolerance_for(args.org, args.appetite)), indent=2))


def cmd_action(args):
    sc = fair.load(args.scenario)
    print(decide(sc, args.org, tolerance_for(args.org, args.appetite))["verdict"])


def cmd_selfcheck(_args):
    loose = fair.load(os.path.join(HERE, "..", "fair", "scenarios", "driftwood-cart-pii.json"))
    tight = fair.load(os.path.join(HERE, "scenarios", "driftwood-cart-pii-tightened.json"))

    dw = tolerance_for("driftwood")
    lud = tolerance_for("ludlow")

    d_loose = decide(loose, "driftwood", dw)
    d_tight = decide(tight, "driftwood", dw)

    # 1. Below the band -> Audit; above it -> Deny.
    assert d_loose["verdict"] == "Audit", d_loose
    assert d_tight["verdict"] == "Deny", d_tight

    # 2. Tightening the triple RAISES the £ (that is what drives the flip).
    assert d_tight["risk_bought"] > d_loose["risk_bought"], (d_loose, d_tight)
    assert d_loose["risk_bought"] <= dw < d_tight["risk_bought"], (d_loose, d_tight)

    # 3. Same control, different band -> different verdict (proportionality money-shot):
    #    the loose cart-PII that Audits in driftwood Denies under ludlow's strict band.
    assert decide(loose, "ludlow", lud)["verdict"] == "Deny", (loose, lud)

    # 4. The escalation is justified by a number, not a timer: this module imports
    #    no clock. Scan real import statements only (not these string literals).
    with open(os.path.abspath(__file__)) as fh:
        for line in fh:
            s = line.strip()
            if s.startswith(("import ", "from ")):
                assert "datetime" not in s and "time" not in s, \
                    f"date/timer logic leaked into enforcement: {s}"

    print(
        "ok  driftwood(£%.0f tol): loose buys £%.0f -> Audit | tightened buys £%.0f -> Deny "
        "| same loose under ludlow(£%.0f tol) -> Deny"
        % (dw, d_loose["risk_bought"], d_tight["risk_bought"], lud)
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Risk-tuned enforcement: the £ picks Audit or Deny.")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, helptext in (
        ("decide", cmd_decide, "full decision + the £ that justifies it (JSON)"),
        ("action", cmd_action, "bare validationActions value: Audit|Deny"),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("scenario")
        sp.add_argument("--org", required=True)
        sp.add_argument("--appetite", default=DEFAULT_APPETITE)
        sp.set_defaults(func=fn)

    pk = sub.add_parser("selfcheck", help="run the enforcement assertions")
    pk.set_defaults(func=cmd_selfcheck)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
