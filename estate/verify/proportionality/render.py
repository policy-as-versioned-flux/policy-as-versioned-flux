#!/usr/bin/env python3
"""render.py — stamp the SHARED encrypt-at-rest control with a per-institution,
£-DERIVED validationActions, proving the divergence is proportionality not opinion.

The control body (control/encrypt-at-rest.tmpl.yaml) is byte-identical across
institutions; the ONLY thing that differs is validationActions, and that value is
NOT authored — it is whatever platform/risk/enforce.py decides for the org from the
FAIR £ (ALE_warn - ALE_deny) against the org's appetite band. So:

    driftwood  £40k band  ->  risk_bought £~21k <= band  ->  Audit
    ludlow      £5k band  ->  risk_bought £~21k  > band  ->  Deny

Same control, same £, opposite verdict — because the band each institution carries
differs. That is the money shot, and this renderer makes it mechanical.

Reuses enforce.py (which reuses fair.py) — no new risk maths here.

Usage:
    render.py <org>            # print the rendered policy for one institution
    render.py --write          # (re)write policies/encrypt-at-rest-<org>.yaml for all
    render.py --check          # assert committed policies == freshly rendered (drift guard)
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RISK = os.path.join(HERE, "..", "..", "platform", "risk")
sys.path.insert(0, RISK)
sys.path.insert(0, os.path.join(HERE, "..", "..", "platform", "fair"))
import enforce  # noqa: E402  (reuses fair.py under the hood)
import fair      # noqa: E402

TMPL = os.path.join(HERE, "control", "encrypt-at-rest.tmpl.yaml")
SCENARIO = os.path.join(HERE, "scenarios", "encrypt-at-rest.json")
ORGS = ("driftwood", "ludlow")


def action_for(org):
    """The £-derived validationActions value for this institution. Pure enforce.py."""
    sc = fair.load(SCENARIO)
    tol = enforce.tolerance_for(org)
    return enforce.decide(sc, org, tol)


def render(org):
    with open(TMPL) as fh:
        body = fh.read()
    verdict = action_for(org)["verdict"]
    return body.replace("__ACTION__", verdict).replace("__ORG__", org)


def out_path(org):
    return os.path.join(HERE, "policies", f"encrypt-at-rest-{org}.yaml")


def cmd_write():
    for org in ORGS:
        with open(out_path(org), "w") as fh:
            fh.write(render(org))
        print(f"wrote {out_path(org)} ({action_for(org)['verdict']})")


def cmd_check():
    """Fail if any committed policy has drifted from what the £ renders today."""
    for org in ORGS:
        want = render(org)
        p = out_path(org)
        if not os.path.exists(p):
            sys.exit(f"missing rendered policy {p} — run render.py --write")
        with open(p) as fh:
            got = fh.read()
        if got != want:
            sys.exit(f"DRIFT: {p} != render.py output (the £-derived action changed; re-run --write)")
    print("ok  committed policies match the £-derived render for", ", ".join(ORGS))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("org", nargs="?", help="print the rendered policy for one institution")
    g.add_argument("--write", action="store_true", help="(re)write policies/ for all institutions")
    g.add_argument("--check", action="store_true", help="assert committed policies == fresh render")
    args = p.parse_args(argv)
    if args.write:
        cmd_write()
    elif args.check:
        cmd_check()
    else:
        sys.stdout.write(render(args.org))


if __name__ == "__main__":
    main()
