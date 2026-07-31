#!/usr/bin/env python3
"""to_fair_scenario.py — turn a signed platform feed entry into a fair.py scenario.

Same shape as estate/ico/schema/to_fair_scenario.py: reads a versioned feed and
emits scenario JSON in the (min,mode,max) shape `platform/fair/fair.py` already
consumes -- bumping a feed version is the whole diff needed to move the £; no
change to fair.py itself.

Three feeds:
  threat  institution threat register -> lef straight from the feed, lm editorial
          per-institution (matches driftwood-cart-pii.json's lm band).
  cve     trivy/GHSA-style feed -> lm from severity_lm_gbp, lef from epss
          (exploit-probability proxy) scaled onto an editorial annual event count.
  eol     endoflife.date-style feed -> lm/lef straight from the component's base
          bands, with lef RAMPED by how far --as-of sits past eol_date: this is
          the time-varying thread (past-EOL -> unpatched CVEs accumulate -> £
          ramps), not a one-off sunset event.

Deny state (all three): loss path closed, lef ~ (0,0,1), same convention as
every other scenario in this estate.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys

DENY_LEF = (0, 0, 1)

# Institution-editorial lm bands (impact per loss event), consistent with the
# driftwood-cart-pii.json scenario already in the estate. ponytail: flat per
# institution -- tune per-threat if a scenario ever needs it.
THREAT_LM_GBP = {
    "driftwood": (1_000, 4_000, 9_000),
    "tuppence": (5_000, 25_000, 90_000),
    "ludlow": (20_000, 100_000, 400_000),
}


# --- threat register -----------------------------------------------------------
def threat_scenario(feed: dict, institution: str) -> dict:
    entry = feed["institutions"][institution]
    lm = THREAT_LM_GBP.get(institution, (1_000, 5_000, 20_000))
    lef = tuple(entry["lef"])
    return {
        "version": feed["feed_version"],
        "name": f"threat-register:{feed['feed_version']} {institution}",
        "note": f"{entry['threat']} ({entry['flavour']}). lef sourced from {entry['source']}.",
        "warn": {"lef": list(lef), "lm": list(lm)},
        "deny": {"lef": list(DENY_LEF), "lm": list(lm)},
    }


# --- CVE feed --------------------------------------------------------------------
def cve_scenario(feed: dict, cve_id: str, annual_events_if_exploited=(1, 2, 6)) -> dict:
    cve = feed["cves"][cve_id]
    lm = tuple(feed["severity_lm_gbp"][cve["severity"]])
    # lef: epss (0..1 exploit-probability proxy) scales an editorial "if this CVE
    # is actively exploited against us, how many loss events/yr" band.
    epss = cve["epss"]
    lo, mode, hi = annual_events_if_exploited
    lef = (lo * epss, mode * epss, hi * epss)
    return {
        "version": feed["feed_version"],
        "name": f"cve:{feed['feed_version']} {cve_id}",
        "note": f"{cve['component']} CVSS {cve['cvss']} ({cve['severity']}), epss={epss}. Source: {cve['source']}.",
        "warn": {"lef": list(lef), "lm": list(lm)},
        "deny": {"lef": list(DENY_LEF), "lm": list(lm)},
    }


# --- EOL feed (time-varying) ------------------------------------------------------
def eol_ramp(eol_date: str, as_of: str) -> float:
    """Loss-event-frequency multiplier for how far as_of sits past eol_date.

    <= eol_date: 1.0 (still in support, base rate applies).
    past eol: unpatched CVEs accumulate -- ramps linearly, +1x per year past EOL,
    capped at 4x (ponytail: linear ramp capped at 4yrs-worth; a real curve would
    taper as attackers move to newer targets, but monotonic-and-bounded is the
    only property fair.py's caller needs).
    """
    eol = datetime.date.fromisoformat(eol_date)
    asof = datetime.date.fromisoformat(as_of)
    days_past = (asof - eol).days
    if days_past <= 0:
        return 1.0
    years_past = days_past / 365.0
    return 1.0 + min(years_past, 4.0)


def eol_scenario(feed: dict, component: str, as_of: str) -> dict:
    c = feed["components"][component]
    ramp = eol_ramp(c["eol_date"], as_of)
    lo, mode, hi = c["base_lef"]
    lef = (lo * ramp, mode * ramp, hi * ramp)
    lm = tuple(c["base_lm_gbp"])
    return {
        "version": feed["feed_version"],
        "name": f"eol:{feed['feed_version']} {component}@{as_of}",
        "note": f"eol_date={c['eol_date']}, as_of={as_of}, ramp={ramp:.2f}x. Source: {c['source']}.",
        "warn": {"lef": list(lef), "lm": list(lm)},
        "deny": {"lef": list(DENY_LEF), "lm": list(lm)},
    }


# --- selfcheck -------------------------------------------------------------------
def selfcheck():
    import glob
    import os

    root = os.path.dirname(__file__)

    checked = 0
    for path in sorted(glob.glob(os.path.join(root, "threat-register/v*/register.json"))):
        with open(path) as fh:
            feed = json.load(fh)
        for inst in feed["institutions"]:
            sc = threat_scenario(feed, inst)
            lo, mode, hi = sc["warn"]["lef"]
            assert lo <= mode <= hi, (path, inst, sc)
            checked += 1

    for path in sorted(glob.glob(os.path.join(root, "cve/v*/cve-feed.json"))):
        with open(path) as fh:
            feed = json.load(fh)
        for cve_id in feed["cves"]:
            sc = cve_scenario(feed, cve_id)
            lo, mode, hi = sc["warn"]["lef"]
            assert lo <= mode <= hi, (path, cve_id, sc)
            checked += 1

    for path in sorted(glob.glob(os.path.join(root, "eol/v*/eol-feed.json"))):
        with open(path) as fh:
            feed = json.load(fh)
        for comp in feed["components"]:
            sc = eol_scenario(feed, comp, "2026-07-31")
            lo, mode, hi = sc["warn"]["lef"]
            assert lo <= mode <= hi, (path, comp, sc)
            checked += 1

    # EOL ramp: the time-varying property the ticket cares about.
    r_before = eol_ramp("2025-10-31", "2025-01-01")
    r_at = eol_ramp("2025-10-31", "2025-10-31")
    r_1yr = eol_ramp("2025-10-31", "2026-10-31")
    r_2yr = eol_ramp("2025-10-31", "2027-10-31")
    r_10yr = eol_ramp("2025-10-31", "2035-10-31")
    assert r_before == 1.0, r_before
    assert r_at == 1.0, r_at
    assert 1.0 < r_1yr < r_2yr < r_10yr, (r_1yr, r_2yr, r_10yr)
    assert r_10yr == 5.0, r_10yr  # capped at +4x

    assert checked >= 9, f"expected to check every feed-version x entry, only checked {checked}"
    print(f"ok  {checked} feed entries valid (lo<=mode<=hi); EOL ramp monotonic & capped "
          f"(1yr={r_1yr:.2f}x 2yr={r_2yr:.2f}x 10yr={r_10yr:.2f}x)")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pt = sub.add_parser("threat", help="threat-register feed -> scenario")
    pt.add_argument("feed")
    pt.add_argument("institution")
    pt.add_argument("-o", "--out")

    pc = sub.add_parser("cve", help="cve feed -> scenario")
    pc.add_argument("feed")
    pc.add_argument("cve_id")
    pc.add_argument("-o", "--out")

    pe = sub.add_parser("eol", help="eol feed -> scenario (time-varying)")
    pe.add_argument("feed")
    pe.add_argument("component")
    pe.add_argument("--as-of", default=datetime.date.today().isoformat())
    pe.add_argument("-o", "--out")

    sub.add_parser("selfcheck", help="assert every feed entry yields a valid triple + EOL ramp behaves")

    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return

    with open(args.feed) as fh:
        feed = json.load(fh)

    if args.cmd == "threat":
        scenario = threat_scenario(feed, args.institution)
    elif args.cmd == "cve":
        scenario = cve_scenario(feed, args.cve_id)
    elif args.cmd == "eol":
        scenario = eol_scenario(feed, args.component, args.as_of)
    else:
        sys.exit(f"unknown cmd {args.cmd}")

    out = json.dumps(scenario, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(out + "\n")
    else:
        print(out)


if __name__ == "__main__":
    main()
