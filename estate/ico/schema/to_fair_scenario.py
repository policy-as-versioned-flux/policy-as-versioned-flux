#!/usr/bin/env python3
"""to_fair_scenario.py — turn an ico penalty-schema entry into a fair.py scenario.

Reads the ico penalty schema (regime -> violation-type -> fine formula/cap + real
public examples) and emits a scenario JSON in the same (min,mode,max) shape
`platform/fair/fair.py` already consumes (see estate/platform/fair/scenarios/
driftwood-cart-pii.json) — so bumping the schema version is the whole diff needed
to move the £ fair.py reports; no change to fair.py itself.

Loss-magnitude (lm) triple per formula type:
  - pct_of_global_turnover / pct_of_relevant_revenue_plus_discretion:
      min = smallest real example, mode = median of real examples, max = cap
      (or, absent a cap, 1.2x the largest example -- FCA has no statutory cap).
  - per_violation_tier (HIPAA): min/max straight from the statutory tier,
      mode = median of real examples clipped into [min, max].
  - per_month_escalating (PCI): steady-state (7+ months) monthly band annualised
      by the ponytail LEF below, mode = midpoint of that band.

Loss-event-frequency (lef) is NOT in the schema -- the schema prices "when it
lands", not "how often". ponytail: a flat editorial per-regime warn-LEF, tune per
institution if a scenario needs it; deny collapses LEF the same way every other
scenario in this estate does (deny.lef ~ (0,0,1)).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys

DEFAULT_WARN_LEF = (1, 2, 4)   # plausible regulatory-incident frequency, events/yr
DEFAULT_DENY_LEF = (0, 0, 1)   # admission blocks the loss path (matches driftwood-cart-pii.json)


def _examples(vt: dict, currency_key: str) -> list[float]:
    key = f"real_examples_{currency_key.lower()}"
    return [e[f"fine_{currency_key.lower()}"] for e in vt.get(key, []) if f"fine_{currency_key.lower()}" in e]


def lm_triple(regime: dict, vt: dict) -> tuple[float, float, float]:
    currency = regime["currency"]
    f = vt["formula"]
    ex = _examples(vt, currency)
    t = f["type"]

    if t in ("pct_of_global_turnover", "pct_of_relevant_revenue_plus_discretion"):
        if not ex:
            sys.exit(f"no real_examples for formula type {t}; cannot derive a grounded lm")
        lo = min(ex)
        mode = statistics.median(ex)
        # the statutory cap is a floor on the ceiling, not a hard override: a real
        # example can exceed today's cap (e.g. BA/Marriott were fined under the
        # pre-Brexit EU GDPR cap) -- the triple must still satisfy lo<=mode<=hi.
        hi = max(f.get("cap_gbp") or 0, max(ex) * 1.2, mode)
        return (float(lo), float(mode), float(hi))

    if t == "per_violation_tier":
        lo, hi = float(f["min_usd" if currency == "USD" else "min_gbp"]), float(f["max_usd" if currency == "USD" else "max_gbp"])
        mode = statistics.median(ex) if ex else (lo + hi) / 2
        mode = min(max(mode, lo), hi)
        return (lo, mode, hi)

    if t == "per_month_escalating":
        steady = f["tiers"][-1]["gbp_per_month"]
        lo, hi = float(steady[0]) * 12, float(steady[1]) * 12  # ponytail: annualised steady-state band
        return (lo, (lo + hi) / 2, hi)

    sys.exit(f"unknown formula type: {t}")


def build_scenario(schema: dict, regime_name: str, vt_name: str,
                    warn_lef=DEFAULT_WARN_LEF, deny_lef=DEFAULT_DENY_LEF) -> dict:
    regime = schema["regimes"][regime_name]
    vt = regime["violation_types"][vt_name]
    lm = lm_triple(regime, vt)
    return {
        "version": schema["schema_version"],
        "name": f"ico:{schema['schema_version']} {regime_name}/{vt_name}",
        "note": f"lm sourced from {regime['authority']} real public fines ({regime['statute']}). "
                f"warn/deny lef are editorial (schema doesn't carry frequency).",
        "warn": {"lef": list(warn_lef), "lm": list(lm)},
        "deny": {"lef": list(deny_lef), "lm": list(lm)},
    }


def selfcheck():
    """Every (regime, violation_type) in every schema version must yield a valid
    lo<=mode<=hi triple -- the one invariant fair.py's pert() needs to not blow up."""
    import glob
    import os

    checked = 0
    for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "v*/penalty-schema.json"))):
        with open(path) as fh:
            schema = json.load(fh)
        for regime_name, regime in schema["regimes"].items():
            for vt_name in regime["violation_types"]:
                lo, mode, hi = lm_triple(regime, regime["violation_types"][vt_name])
                assert lo <= mode <= hi, (path, regime_name, vt_name, lo, mode, hi)
                checked += 1
    assert checked >= 8, f"expected to check every regime x violation-type, only checked {checked}"
    print(f"ok  {checked} (schema-version, regime, violation-type) triples are all lo<=mode<=hi")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd")

    pc = sub.add_parser("build", help="emit a fair.py scenario for one regime/violation-type (default)")
    pc.add_argument("schema", help="path to a penalty-schema.json")
    pc.add_argument("regime")
    pc.add_argument("violation_type")
    pc.add_argument("-o", "--out", help="write scenario JSON here (default: stdout)")

    sub.add_parser("selfcheck", help="assert every schema entry yields a valid lm triple")

    # allow the old positional form (no subcommand) to keep working
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] not in ("build", "selfcheck", "-h", "--help"):
        argv = ["build"] + list(argv)

    args = p.parse_args(argv)
    if args.cmd == "selfcheck":
        selfcheck()
        return

    with open(args.schema) as fh:
        schema = json.load(fh)
    scenario = build_scenario(schema, args.regime, args.violation_type)
    out = json.dumps(scenario, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(out + "\n")
    else:
        print(out)


if __name__ == "__main__":
    main()
