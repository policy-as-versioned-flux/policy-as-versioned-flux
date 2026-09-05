#!/usr/bin/env python3
"""render.py — stamp the SHARED governed Namespace with a per-institution, £-DERIVED
cage TIER, proving the divergence is proportionality and not opinion.

The Namespace body (control/governed-namespace.tmpl.yaml) is byte-identical across
institutions; the only things that differ are `posture.acme.io/tier` and the org name,
and the tier is NOT hand-authored — it is whatever platform/graded/cage.py selects for
the org from the FAIR uncaged residual against that party's OWN SIGNED appetite band
(`appetite.tolerance` on its party.yaml, ADR-0021). So:

    driftwood  £40,000 band  ->  quarantine residual is not needed  ->  baseline
    ludlow      £5,000 band  ->  only quarantine's residual fits     ->  quarantine

Same workload, same £21,360 uncaged residual, different RUNG — because the band each
institution carries differs. That is the money shot, and this renderer makes it
mechanical.

Eco-system ticket 89 re-pointed this from enforcement action to tier selection. Until
2026-09-05 `action_for()` asked platform/risk/enforce.py for `Audit` or `Deny` and
stamped it into a per-institution ValidatingPolicy body. Deny is not a rung: nothing in
the estate is deliberately denied, and a workload that does not fit its cage does not
run (owner, 2026-09-02, ticket 75 Q5). The band still does exactly one job here; it now
picks a rung on the ladder instead of an enforcement action, which is the mechanism the
estate actually ships (`cage.py select_tier`, `wargamer.select_party_tier`, `tier_pr.py`).

Reuses cage.py (which reuses fair.py and enforce.py) — no new risk maths here.

Usage:
    render.py <org>            # print the rendered Namespace for one institution
    render.py --write          # (re)write namespaces/proportionality-<org>.yaml for all
    render.py --check          # assert committed namespaces == freshly rendered (drift guard)
    render.py --json <org>     # the whole £ decision for one institution, as JSON
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # verify/, for _estate
from _estate import ESTATE  # noqa: E402

sys.path.insert(0, os.path.join(ESTATE, "platform", "graded"))
sys.path.insert(0, os.path.join(ESTATE, "platform", "risk"))
sys.path.insert(0, os.path.join(ESTATE, "platform", "fair"))
import cage      # noqa: E402  (reuses fair.py and enforce.py under the hood)
import enforce   # noqa: E402
import fair      # noqa: E402

TMPL = os.path.join(HERE, "control", "governed-namespace.tmpl.yaml")
SCENARIO = os.path.join(HERE, "scenarios", "encrypt-at-rest.json")
ORGS = ("driftwood", "ludlow")


def decision_for(org):
    """The whole £ decision for this institution: uncaged residual, the signed band, the
    selected rung and its dials. Pure cage.py — no floor is passed, because this beat is
    about the band and nothing else."""
    sc = fair.load(SCENARIO)
    tol = enforce.tolerance_for(org)
    return cage.select(sc, org, tol)


def tier_for(org):
    """The £-derived rung for this institution."""
    return decision_for(org)["tier"]


def render(org):
    with open(TMPL) as fh:
        body = fh.read()
    return body.replace("__TIER__", tier_for(org)).replace("__ORG__", org)


def out_path(org):
    return os.path.join(HERE, "namespaces", f"proportionality-{org}.yaml")


def cmd_write():
    os.makedirs(os.path.join(HERE, "namespaces"), exist_ok=True)
    for org in ORGS:
        with open(out_path(org), "w") as fh:
            fh.write(render(org))
        print(f"wrote {out_path(org)} ({tier_for(org)})")


def cmd_check():
    """Fail if any committed Namespace has drifted from what the £ renders today."""
    for org in ORGS:
        want = render(org)
        p = out_path(org)
        if not os.path.exists(p):
            sys.exit(f"missing rendered namespace {p} — run render.py --write")
        with open(p) as fh:
            got = fh.read()
        if got != want:
            sys.exit(f"DRIFT: {p} != render.py output (the £-derived tier changed; re-run --write)")
    print("ok  committed namespaces match the £-derived render for", ", ".join(ORGS))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("org", nargs="?", help="print the rendered Namespace for one institution")
    p.add_argument("--write", action="store_true", help="(re)write namespaces/ for all institutions")
    p.add_argument("--check", action="store_true", help="assert committed namespaces == fresh render")
    p.add_argument("--json", action="store_true", help="print the whole £ decision for <org>")
    args = p.parse_args(argv)
    if args.write:
        cmd_write()
    elif args.check:
        cmd_check()
    elif args.json:
        if not args.org:
            p.error("--json needs an org")
        print(json.dumps(decision_for(args.org)))
    elif args.org:
        sys.stdout.write(render(args.org))
    else:
        p.error("give an org, --write or --check")


if __name__ == "__main__":
    main()
