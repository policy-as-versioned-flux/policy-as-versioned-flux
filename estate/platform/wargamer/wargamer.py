#!/usr/bin/env python3
"""wargamer.py — the governance-agent evolved into a war-gaming policy-PR proposer.

The loop-closer (spec stories 28-33). It:

  1. COLLECTS the signed feeds -- the platform reactive feeds (threat register /
     CVE / EOL via ../feeds/to_fair_scenario.py) plus its own war-game scenario
     library (human/device attack paths + the forward ransomware/PQ/Wardley
     class in scenarios/human-device.json). Regulator feeds (nist OSCAL, ico
     penalties) are pinned upstream deps already wired into ../tcor; the
     war-gamer references their pinned versions as evidence, it does not re-price
     them here.

  2. WAR-GAMES current controls against that intelligence:
       * enforcement controls -- the £-implied Audit/Deny (../risk/enforce.py)
         at the CURRENT feed vs the action deployed at the BASELINE feed; a
         changed verdict is proportionality drift.
       * human/device + ransomware/PQ risks -- the cheapest of the four
         risk-financing moves (../tcor/tcor.py crossover) vs the deployed move;
         a changed move is drift (a control gone over-priced, or a stale blunt
         deny a cage/transfer now beats).

  3. On drift, PROPOSES a signed policy PR -- and NEVER DISPOSES. `propose()`
     returns a proposal that is opened, never merged, and carries the version
     cross-check gate (../shift-left/ci-check.py). This module exposes no merge
     capability by construction: a human + the PR gate dispose. Every proposal
     carries the war-gamer's own attestable identity (gitsign keyless -> Rekor,
     stamped at commit time by propose-policy-pr.sh, not here).

Pure/offline. Reuses fair.py, enforce.py, tcor.py, to_fair_scenario.py unchanged.

Usage:
    wargamer.py wargame  [--baseline <feed>] [--current <feed>]   # the drift report
    wargamer.py propose  [--baseline <feed>] [--current <feed>]   # the PR proposals (never merged)
    wargamer.py selfcheck                                         # the feed->PR seam asserts
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.join(HERE, "..")
for _d in ("fair", "risk", "tcor", "graded"):
    sys.path.insert(0, os.path.join(PLATFORM, _d))
import fair      # noqa: E402  the £ maths
import enforce   # noqa: E402  the appetite band + Audit/Deny verdict
import tcor      # noqa: E402  the four-move crossover


def _load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ../feeds/to_fair_scenario.py: the feed -> scenario converter, reused unmodified.
feeds = _load_by_path("platform_feeds", os.path.join(PLATFORM, "feeds", "to_fair_scenario.py"))

BASELINE_FEED = os.path.join(PLATFORM, "feeds", "threat-register", "v1", "register.json")
# The current feed defaults to the war-gamer's signed drift fixture: a driftwood
# skimmer-campaign LEF uptick that pushes the cart-PII control past driftwood's band.
CURRENT_FEED = os.path.join(HERE, "fixtures", "threat-register", "v3", "register.json")
LIBRARY = os.path.join(HERE, "scenarios", "human-device.json")

# The deployed enforcement control the war-gamer stress-tests the feeds against.
# require-nonroot ships Audit at v2.0.0 (distribution/policies/v2.0.0); its cart-PII
# £ scenario is the threat-register's per-institution lm band (THREAT_LM_GBP), so
# threat_scenario(feed, org) IS the control's war-game scenario -- feed LEF x control LM.
CONTROL = {
    "policy": "require-nonroot",
    "version": "2.0.0",
    "policy_file": "distribution/policies/v2.0.0/require-nonroot.yaml",
}

GATE = "shift-left version cross-check (../shift-left/ci-check.py, target +/-1 window)"


# --- collect ------------------------------------------------------------------
def collect(baseline_feed=BASELINE_FEED, current_feed=CURRENT_FEED, library=LIBRARY):
    """Gather the intelligence the war-gamer reasons over: the baseline + current
    threat feed (per institution) and the war-game scenario library."""
    with open(baseline_feed) as fh:
        base = json.load(fh)
    with open(current_feed) as fh:
        cur = json.load(fh)
    with open(library) as fh:
        lib = json.load(fh)
    return {"baseline": base, "current": cur, "library": lib,
            "baseline_feed": baseline_feed, "current_feed": current_feed}


# --- war-game -----------------------------------------------------------------
def wargame_enforcement(intel):
    """Per institution: the deployed action (verdict at the baseline feed) vs the
    £-implied action at the current feed. A changed verdict is proportionality drift."""
    base, cur = intel["baseline"], intel["current"]
    rows = []
    for org in base["institutions"]:
        deployed = enforce.decide(
            feeds.threat_scenario(base, org), org, enforce.tolerance_for(org))
        implied = enforce.decide(
            feeds.threat_scenario(cur, org), org, enforce.tolerance_for(org))
        drift = deployed["verdict"] != implied["verdict"]
        rows.append({
            "kind": "enforcement",
            "org": org,
            "control": f"{CONTROL['policy']}@{CONTROL['version']}",
            "policy_file": CONTROL["policy_file"],
            "deployed": deployed["verdict"],
            "implied": implied["verdict"],
            "risk_bought_deployed": deployed["risk_bought"],
            "risk_bought_current": implied["risk_bought"],
            "tolerance": deployed["tolerance"],
            "drift": drift,
            "evidence": {
                "baseline_feed": os.path.relpath(intel["baseline_feed"], HERE),
                "current_feed": os.path.relpath(intel["current_feed"], HERE),
                "feed_version": cur.get("feed_version"),
            },
        })
    return rows


def wargame_scenarios(intel):
    """Human/device + ransomware/PQ: the cheapest of the four risk-financing moves
    (tcor crossover) vs the deployed move. A changed move is drift."""
    lib = intel["library"]
    org = lib.get("org", "driftwood")
    tol = enforce.tolerance_for(org)
    rows = []
    for risk in lib["risks"]:
        chosen = tcor.crossover(risk, tol)["chosen"]
        deployed = risk.get("deployed_move", chosen)
        rows.append({
            "kind": "scenario",
            "org": org,
            "control": risk["id"],
            "author": risk.get("author"),
            "deployed": deployed,
            "implied": chosen,
            "drift": deployed != chosen,
            "evidence": {"scenario_library": os.path.relpath(LIBRARY, HERE),
                         "risk": risk["id"], "author": risk.get("author")},
        })
    return rows


def wargame(intel=None):
    intel = intel or collect()
    return wargame_enforcement(intel) + wargame_scenarios(intel)


# --- propose (never dispose) --------------------------------------------------
def propose(row):
    """Turn a drift row into a signed-policy-PR proposal. Opened, never merged;
    carries the version cross-check gate + the war-gamer's gitsign identity.

    There is deliberately NO merge()/dispose() here -- the agent proposes, a human
    + the PR gate dispose. That absence IS the safety property (selfcheck asserts it)."""
    if not row["drift"]:
        return None
    slug = f"{row['org']}-{row['control']}".replace("@", "-").replace(".", "-")
    return {
        "branch": f"wargamer/retune-{slug}",
        "title": f"[war-gamer] re-tune {row['control']} ({row['org']}): "
                 f"{row['deployed']} -> {row['implied']}",
        "actor": "wargamer-agent",
        "identity": "gitsign keyless (OIDC -> Fulcio) -> Rekor transparency log",
        "signed": True,               # stamped at commit time by propose-policy-pr.sh
        "from_evidence": row["evidence"],
        "change": {
            "target": row.get("policy_file", row["control"]),
            "from": row["deployed"],
            "to": row["implied"],
        },
        "required_gate": GATE,
        "merged": False,              # propose-never-dispose: the agent never merges
        "auto_merge": False,
        "disposition": "OPEN -- awaiting human review + version cross-check gate",
    }


def proposals(intel=None):
    return [p for p in (propose(r) for r in wargame(intel)) if p]


# --- selfcheck: the feed->PR seam ---------------------------------------------
def selfcheck():
    intel = collect()
    rows = wargame(intel)

    # 1. COLLECT: the signed feed-change fixture is in, and the library loaded.
    assert intel["current"]["feed_version"] == "v3", intel["current"].get("feed_version")
    assert len(intel["library"]["risks"]) >= 5, "war-game scenario library too small"
    authors = {r.get("author") for r in intel["library"]["risks"]}
    assert {"human-seed", "ai-generated"} <= authors, ("scenarios must be both "
                                                       "human-seed and AI-generated", authors)

    # 2. WAR-GAME both classes: enforcement drift AND a human/device path drift.
    enf = [r for r in rows if r["kind"] == "enforcement"]
    scn = [r for r in rows if r["kind"] == "scenario"]
    # driftwood's cart-PII control was proportionately Audit at v1; the v3 skimmer
    # uptick pushes its residual over the £40k band -> the £ now implies Deny.
    dw = next(r for r in enf if r["org"] == "driftwood")
    assert dw["deployed"] == "Audit", dw
    assert dw["implied"] == "Deny", dw
    assert dw["drift"] is True, dw
    assert dw["risk_bought_current"] > dw["tolerance"] >= dw["risk_bought_deployed"], dw
    # a feed bump that does NOT cross a band must NOT drift (ludlow unchanged in v3):
    lud = next(r for r in enf if r["org"] == "ludlow")
    assert lud["drift"] is False, ("unchanged institution must not drift", lud)
    # at least one human/device/ransomware path drifts (a stale move the £ re-prices):
    assert any(r["drift"] for r in scn), ("a war-gamed human/device scenario must "
                                          "surface drift", scn)

    # 2b. hyperscaler-region-concentration: tcor.py's `applicable` field narrows the
    #     move to what an org can actually do to a third party (you cannot fix, cage
    #     or deny a hyperscaler's control plane). Pin down BOTH sides of that: with
    #     `applicable`, transfer wins and matches deployed_move (no drift); strip
    #     `applicable` and the engine defaults costs.fix to 0 and nonsensically
    #     "fixes" the outage for ~£3,726 -- the exact regression research 05 named.
    hyper = next(r for r in scn if r["control"] == "hyperscaler-region-concentration")
    assert hyper["deployed"] == "transfer" and hyper["implied"] == "transfer", hyper
    assert hyper["drift"] is False, ("applicable must keep this risk from drifting", hyper)
    hyper_org = intel["library"].get("org", "driftwood")
    hyper_tol = enforce.tolerance_for(hyper_org)
    hyper_risk = next(r for r in intel["library"]["risks"]
                       if r["id"] == "hyperscaler-region-concentration")
    assert tcor.crossover(hyper_risk, hyper_tol)["chosen"] == "transfer", hyper_risk
    stripped = {k: v for k, v in hyper_risk.items() if k != "applicable"}
    broken = tcor.crossover(stripped, hyper_tol)
    assert broken["chosen"] == "fix", ("without `applicable` the engine must default "
                                       "to the nonsensical free fix", broken)
    assert abs(broken["line"]["tcor"] - 3726) < 1, ("the free-fix number must be the "
                                                    "~£3,726 the ticket names", broken)

    # 3. PROPOSE, NEVER DISPOSE.
    props = proposals(intel)
    assert props, "drift detected but no PR proposed"
    # a PR IS opened for the driftwood flip, and it flips Audit->Deny:
    dw_pr = next(p for p in props if p["change"]["from"] == "Audit"
                 and p["change"]["to"] == "Deny")
    assert dw_pr["change"]["target"].endswith("require-nonroot.yaml"), dw_pr
    for p in props:
        # never auto-merged:
        assert p["merged"] is False and p["auto_merge"] is False, p
        # carries the version cross-check gate:
        assert "cross-check" in p["required_gate"], p
        # carries the war-gamer's own attestable identity:
        assert p["signed"] is True and "Rekor" in p["identity"], p
        # traces to the evidence it was proposed from:
        assert p["from_evidence"], p
    # the SAFETY property, structurally: the agent has no way to merge/dispose.
    assert not hasattr(sys.modules[__name__], "merge"), "war-gamer must expose no merge()"
    assert not hasattr(sys.modules[__name__], "dispose"), "war-gamer must expose no dispose()"

    print(
        "ok  collected v1->v3 signed feed + %d-scenario library (human-seed + AI); "
        "war-game: driftwood cart-PII £%.0f>£%.0f band -> Audit->Deny drift, ludlow steady; "
        "%d scenario-path drift(s); proposed %d signed PR(s), 0 merged, all carry the gate."
        % (len(intel["library"]["risks"]), dw["risk_bought_current"], dw["tolerance"],
           sum(1 for r in scn if r["drift"]), len(props))
    )


# --- CLI ----------------------------------------------------------------------
def _feed_args(p):
    p.add_argument("--baseline", default=BASELINE_FEED)
    p.add_argument("--current", default=CURRENT_FEED)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pw = sub.add_parser("wargame", help="the drift report (enforcement + scenarios)")
    _feed_args(pw)

    pp = sub.add_parser("propose", help="the signed policy PR proposals (never merged)")
    _feed_args(pp)

    sub.add_parser("selfcheck", help="the feed->PR seam asserts (propose-never-dispose)")

    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return
    intel = collect(args.baseline, args.current)
    if args.cmd == "wargame":
        print(json.dumps(wargame(intel), indent=2))
    elif args.cmd == "propose":
        print(json.dumps(proposals(intel), indent=2))


if __name__ == "__main__":
    main()
