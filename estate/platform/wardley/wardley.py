#!/usr/bin/env python3
"""wardley.py -- the AI-Wardley forward layer (spec stories 28, 32; ticket 23).

The fifth, FORWARD feed. The reactive feeds (threat register / CVE / EOL) report
what has already been seen. This layer maps MARKET intel onto a Wardley map and
reads the one thing the reactive feeds structurally cannot: components still
MOVING right. When an attacker-capability commoditises, its cost collapses and
the linked risk's loss-event-frequency rises BEFORE a single incident lands. That
becomes a forward signal the war-gamer re-prices ahead of time -- proportionality
re-tunes before the threat, not after.

Three jobs (the ticket's three acceptance criteria):

  1. MAP  -- place every component on the evolution axis, project it forward over
            the intel horizon, and FLAG commoditisation MOVEMENT (a component that
            crosses a stage boundary, or reaches commodity, within the horizon).
  2. FORWARD SIGNAL -- for each commoditising ATTACKER-capability, collapse the
            attack cost into a forward LEF bump on its linked war-game risk and
            emit a scenario library in the exact shape the war-gamer already
            consumes (../wargamer + ../tcor). `forward_into_wargamer()` feeds it
            straight through the war-gamer's own scenario war-game.
  3. ATTESTABLE -- the map + intel are detached-signed (sign-map.sh, feeds key)
            and land as a reviewable, verifiable commit; a tampered map fails.

Pure/offline. Reuses tcor.py + wargamer.py unchanged.

Usage:
    wardley.py map              [--intel <file>]                # the Wardley map + commoditisation flags
    wardley.py forward-signal   [--intel <file>] [--org <org>]   # forward scenario library (one org, or all three institutions)
    wardley.py wargame          [--intel <file>] [--org <org>]   # feed the forward signal THROUGH the war-gamer (one org, or all three)
    wardley.py selfcheck                                         # the projection + seam asserts
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(PLATFORM, "tcor"))
sys.path.insert(0, os.path.join(PLATFORM, "wargamer"))
import tcor       # noqa: E402  the four-move crossover the war-gamer prices with

INTEL = os.path.join(HERE, "intel", "market-intel.json")
# The risk-bearing institutions the forward layer must speak for -- read from the
# same appetite file tolerance_for() judges against (../risk/appetite.json), so the
# org set can never drift out of step with the bands it is priced into.
APPETITE = os.path.join(PLATFORM, "risk", "appetite.json")

# Evolution-axis stage boundaries (Wardley's genesis/custom/product/commodity).
STAGES = [(0.25, "genesis"), (0.50, "custom"), (0.75, "product"), (1.01, "commodity")]

# How hard a commoditisation MOVEMENT bumps the linked attacker LEF. The movement
# (proj - evolution) is bounded in [0,1]; K scales it into a frequency multiplier.
# ponytail: one linear knob, editorial. It's a calibration dial, not a physics law
# -- widen K if a real trajectory should flip a move sooner. Upgrade path: a
# per-component collapse curve if any single trajectory needs its own shape.
ATTACK_COST_COLLAPSE_K = 4.0


def _stage(x):
    for hi, name in STAGES:
        if x < hi:
            return name
    return "commodity"


def _stage_idx(x):
    return next(i for i, (hi, _) in enumerate(STAGES) if x < hi)


def load(intel_path=INTEL):
    with open(intel_path) as fh:
        return json.load(fh)


def institutions(appetite_path=APPETITE):
    """The risk-bearing institutions the forward signal runs against, in appetite-file
    order (driftwood, tuppence, ludlow) -- one band per org, never a single stand-in."""
    with open(appetite_path) as fh:
        return list(json.load(fh)["orgs"])


# --- 1. the Wardley map + commoditisation flags -------------------------------
def build_map(intel):
    """Place every component and flag commoditisation MOVEMENT: a component whose
    projected position over the horizon crosses into a more-evolved stage (or
    reaches commodity). Already-commodity + near-stationary components do NOT flag
    -- there is no *movement* left to anticipate."""
    horizon = intel["horizon_years"]
    rows = []
    for c in intel["components"]:
        ev = c["evolution"]
        proj = min(1.0, ev + c["velocity"] * horizon)
        movement = round(proj - ev, 4)
        crosses = _stage_idx(proj) > _stage_idx(ev)
        reaches_commodity = _stage(proj) == "commodity"
        commoditising = crosses or (reaches_commodity and _stage(ev) != "commodity")
        rows.append({
            "id": c["id"],
            "label": c["label"],
            "actor": c["actor"],
            "visibility": c["visibility"],
            "evolution": ev,
            "stage": _stage(ev),
            "projected": round(proj, 4),
            "projected_stage": _stage(proj),
            "movement": movement,
            "commoditising": commoditising,
            "links_risk": c.get("links_risk"),
        })
    return {"intel_version": intel["intel_version"], "horizon_years": horizon, "components": rows}


# --- 2. the forward signal into the war-gamer ---------------------------------
def _forward_risk(component, movement):
    """Collapse a commoditising attacker-capability's movement into a forward LEF
    bump on its linked war-game risk. Higher commoditisation -> cheaper attack ->
    higher frequency -> the war-gamer re-prices the cheapest move over the FORWARD
    exposure, not the reactive one."""
    factor = 1.0 + ATTACK_COST_COLLAPSE_K * movement
    r = copy.deepcopy(component["base_risk"])
    for state in ("warn", "behind"):
        if state in r:
            r[state]["lef"] = [round(v * factor, 3) for v in r[state]["lef"]]
    r["author"] = "ai-generated"
    r["forward"] = {"component": component["id"], "movement": movement,
                    "attack_cost_collapse_factor": round(factor, 3)}
    return r


def forward_signal(intel, org):
    """The forward scenario library for ONE institution -- war-gamer shape
    ({org, risks:[...]}). One risk per commoditising attacker-capability that
    carries a base FAIR posture; the same market movement, labelled for the
    institution whose band it will be priced against downstream."""
    mp = {r["id"]: r for r in build_map(intel)["components"]}
    risks = []
    for c in intel["components"]:
        row = mp[c["id"]]
        if c["actor"] != "attacker-capability" or not row["commoditising"]:
            continue
        if not c.get("base_risk"):
            continue
        risks.append(_forward_risk(c, row["movement"]))
    return {
        "org": org,
        "note": ("AI-Wardley forward signal (%s): %d commoditising attacker-capabilit"
                 "y(ies) re-priced ahead of the reactive feeds." % (org, len(risks))),
        "source": "platform/wardley/wardley.py forward-signal @ intel %s" % intel["intel_version"],
        "risks": risks,
    }


def forward_signal_all(intel):
    """The forward scenario library for every risk-bearing institution -- three
    different orgs, one call each, never one org standing in for the estate."""
    return {org: forward_signal(intel, org) for org in institutions()}


# --- 3. feed the forward signal THROUGH the war-gamer -------------------------
def forward_into_wargamer(intel, org):
    """Hand ONE institution's forward library to the war-gamer's OWN scenario
    war-game, unmodified. This is the seam: the forward signal is consumed exactly
    like the reactive library, and any re-priced move that no longer matches the
    deployed posture is drift the war-gamer will propose a PR to re-tune -- before
    the threat lands. The verdict is the org's own band, not a stand-in's."""
    import wargamer  # imported here so `wardley.py map` needs only tcor
    lib = forward_signal(intel, org)
    tol = wargamer.enforce.tolerance_for(lib["org"])
    rows = wargamer.wargame_scenarios({"library": lib})
    props = [wargamer.propose(r) for r in rows]
    return {"library": lib, "tolerance": tol, "rows": rows,
            "proposals": [p for p in props if p]}


def forward_into_wargamer_all(intel):
    """Run the seam for every risk-bearing institution -- three orgs, three bands,
    honestly three (possibly different) drift sets and proposal counts."""
    return {org: forward_into_wargamer(intel, org) for org in institutions()}


# --- selfcheck ----------------------------------------------------------------
def selfcheck():
    intel = load()
    mp = build_map(intel)

    # 1. MAP flags commoditisation MOVEMENT, not mere position.
    by = {c["id"]: c for c in mp["components"]}
    # a fast-moving product-stage attack IS flagged as commoditising movement:
    assert by["phishing-kits-aas"]["commoditising"] is True, by["phishing-kits-aas"]
    assert by["phishing-kits-aas"]["projected_stage"] == "commodity", by["phishing-kits-aas"]
    # already-commodity + near-stationary is NOT flagged (no movement to anticipate):
    assert by["credential-stuffing-aas"]["stage"] == "commodity", by["credential-stuffing-aas"]
    assert by["credential-stuffing-aas"]["commoditising"] is False, by["credential-stuffing-aas"]
    # movement is monotone in velocity*horizon:
    assert by["phishing-kits-aas"]["movement"] > by["pq-cryptanalysis"]["movement"], mp

    # 2. FORWARD SIGNAL: only commoditising ATTACKER-capabilities become risks;
    #    the defensive commoditisation does NOT bump any attacker LEF.
    sig = forward_signal(intel, "driftwood")
    ids = {r["forward"]["component"] for r in sig["risks"]}
    assert "spiffe-workload-identity" not in ids, "defensive commoditisation must not raise attacker risk"
    assert "credential-stuffing-aas" not in ids, "already-commodity (no movement) must not signal"
    assert {"phishing-kits-aas", "ransomware-aas"} <= ids, ("expected the commoditising attacker "
                                                            "capabilities in the forward signal", ids)
    # the attack-cost collapse RAISES frequency vs the reactive base (forward > reactive):
    ph_base = next(c for c in intel["components"] if c["id"] == "phishing-kits-aas")["base_risk"]
    ph_fwd = next(r for r in sig["risks"] if r["forward"]["component"] == "phishing-kits-aas")
    assert ph_fwd["warn"]["lef"][2] > ph_base["warn"]["lef"][2], (ph_fwd, ph_base)
    assert ph_fwd["forward"]["attack_cost_collapse_factor"] > 1.0, ph_fwd

    # 2b. the "no movement" exclusion above is VACUOUS as a regression test: real
    #     credential-stuffing-aas ALSO carries base_risk: null, so even if the
    #     commoditising gate broke, the null-base_risk gate would still mask the
    #     bug and this same assertion would still pass -- for the wrong reason.
    #     Isolate the gate under test by giving the same stationary component a
    #     REAL base_risk; only the movement gate is left to exclude it.
    stationary_intel = copy.deepcopy(intel)
    stationary = next(c for c in stationary_intel["components"] if c["id"] == "credential-stuffing-aas")
    stationary["base_risk"] = copy.deepcopy(ph_base)
    stationary_row = {r["id"]: r for r in build_map(stationary_intel)["components"]}["credential-stuffing-aas"]
    assert stationary_row["commoditising"] is False, (
        "control case must stay stationary -- movement, not a missing base_risk, is under test",
        stationary_row)
    stationary_ids = {r["forward"]["component"] for r in forward_signal(stationary_intel, "driftwood")["risks"]}
    assert "credential-stuffing-aas" not in stationary_ids, (
        "an already-commodity, non-moving component must not signal EVEN WITH a real base_risk",
        stationary_ids)

    # 3. the FORWARD VALUE, per institution's OWN band -- not one org standing in
    #    for the estate. At driftwood's loose band the reactive base posture is NOT
    #    drift; the commoditisation bump is the ONLY reason a drift appears -> the
    #    war-gamer re-tunes BEFORE the threat lands.
    import wargamer
    tol_dw = wargamer.enforce.tolerance_for("driftwood")
    base_move = tcor.crossover(ph_base, tol_dw)["chosen"]
    fwd_move = tcor.crossover(ph_fwd, tol_dw)["chosen"]
    assert base_move == ph_base["deployed_move"], (
        "reactive base must NOT drift at driftwood -- else it's a misconfig, not a forward discovery",
        base_move, ph_base["deployed_move"])
    assert fwd_move != ph_base["deployed_move"], (
        "the forward commoditisation bump must be what flips the move", base_move, fwd_move)

    # 3b. the SAME forward signal, judged against ludlow's far stricter band, gives a
    #     DIFFERENT verdict -- proof this is per-institution, not driftwood run thrice.
    #     At ludlow: phishing does NOT drift (already Deny-leaning); ransomware
    #     already drifts at the reactive BASE, before any forward bump at all.
    tol_lud = wargamer.enforce.tolerance_for("ludlow")
    ph_fwd_lud = next(r for r in forward_signal(intel, "ludlow")["risks"]
                       if r["forward"]["component"] == "phishing-kits-aas")
    rw_base = next(c for c in intel["components"] if c["id"] == "ransomware-aas")["base_risk"]
    assert tcor.crossover(ph_fwd_lud, tol_lud)["chosen"] == ph_base["deployed_move"], (
        "at ludlow's tighter band the phishing forward signal must NOT drift",
        tcor.crossover(ph_fwd_lud, tol_lud)["chosen"], ph_base["deployed_move"])
    assert tcor.crossover(rw_base, tol_lud)["chosen"] != rw_base["deployed_move"], (
        "at ludlow's band even the reactive ransomware BASE must already drift",
        tcor.crossover(rw_base, tol_lud)["chosen"], rw_base["deployed_move"])

    # 4. the SEAM, run for the SET: the forward signal drives the war-gamer for every
    #    institution, and each institution's own band decides its own drift + PRs --
    #    three institutions, honestly three (here, different) sets, never one count.
    out_all = forward_into_wargamer_all(intel)
    assert set(out_all) == set(institutions()), (set(out_all), institutions())
    total_drifts = total_props = 0
    for org, out in out_all.items():
        drifts = [r for r in out["rows"] if r["drift"]]
        assert drifts, (org, "the forward signal must surface at least one drift the "
                        "war-gamer re-tunes before the threat lands", out["rows"])
        assert out["proposals"], (org, "forward drift detected but the war-gamer proposed no PR")
        for p in out["proposals"]:
            assert p["merged"] is False and p["auto_merge"] is False, p  # propose, never dispose
            assert "cross-check" in p["required_gate"], p                # rides the existing gate
            assert p["signed"] is True and "Rekor" in p["identity"], p   # attestable identity
        total_drifts += len(drifts)
        total_props += len(out["proposals"])
    # the divergence, machine-checked: driftwood and ludlow must NOT drift on the
    # identical control set, or the "own band" claim above is not actually wired in.
    dw_drift_ids = {r["control"] for r in out_all["driftwood"]["rows"] if r["drift"]}
    lud_drift_ids = {r["control"] for r in out_all["ludlow"]["rows"] if r["drift"]}
    assert dw_drift_ids != lud_drift_ids, (
        "driftwood and ludlow must not drift on the identical set -- the band, not the "
        "signal, decides", dw_drift_ids, lud_drift_ids)

    print(
        "ok  Wardley map: %d components, %d flagged commoditising (movement, not position); "
        "forward signal: %d attacker-capability(ies) re-priced (phishing collapse x%.2f), "
        "per institution; fed through the war-gamer for %d institution(s) -> %d forward "
        "drift(s) -> %d PR(s) proposed, 0 merged, all gated."
        % (len(mp["components"]),
           sum(1 for c in mp["components"] if c["commoditising"]),
           len(sig["risks"]), ph_fwd["forward"]["attack_cost_collapse_factor"],
           len(out_all), total_drifts, total_props)
    )


# --- CLI ----------------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("map").add_argument("--intel", default=INTEL)
    for name in ("forward-signal", "wargame"):
        sp = sub.add_parser(name)
        sp.add_argument("--intel", default=INTEL)
        sp.add_argument("--org", default=None,
                         help="one institution; omit to run all three (driftwood, tuppence, ludlow)")
    sub.add_parser("selfcheck")
    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return
    intel = load(args.intel)
    if args.cmd == "map":
        print(json.dumps(build_map(intel), indent=2))
    elif args.cmd == "forward-signal":
        out = forward_signal(intel, args.org) if args.org else forward_signal_all(intel)
        print(json.dumps(out, indent=2))
    elif args.cmd == "wargame":
        out = forward_into_wargamer(intel, args.org) if args.org else forward_into_wargamer_all(intel)
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
