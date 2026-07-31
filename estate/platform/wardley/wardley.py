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
    wardley.py map              [--intel <file>]   # the Wardley map + commoditisation flags
    wardley.py forward-signal   [--intel <file>]   # the forward scenario library (war-gamer shape)
    wardley.py wargame          [--intel <file>]   # feed the forward signal THROUGH the war-gamer
    wardley.py selfcheck                            # the projection + seam asserts
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


def forward_signal(intel):
    """The forward scenario library -- war-gamer shape ({org, risks:[...]}). One
    risk per commoditising attacker-capability that carries a base FAIR posture."""
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
        "org": "driftwood",
        "note": ("AI-Wardley forward signal: %d commoditising attacker-capabilit"
                 "y(ies) re-priced ahead of the reactive feeds." % len(risks)),
        "source": "platform/wardley/wardley.py forward-signal @ intel %s" % intel["intel_version"],
        "risks": risks,
    }


# --- 3. feed the forward signal THROUGH the war-gamer -------------------------
def forward_into_wargamer(intel):
    """Hand the forward library to the war-gamer's OWN scenario war-game, unmodified.
    This is the seam: the forward signal is consumed exactly like the reactive
    library, and any re-priced move that no longer matches the deployed posture is
    drift the war-gamer will propose a PR to re-tune -- before the threat lands."""
    import wargamer  # imported here so `wardley.py map` needs only tcor
    lib = forward_signal(intel)
    tol = wargamer.enforce.tolerance_for(lib["org"])
    rows = wargamer.wargame_scenarios({"library": lib})
    props = [wargamer.propose(r) for r in rows]
    return {"library": lib, "tolerance": tol, "rows": rows,
            "proposals": [p for p in props if p]}


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
    sig = forward_signal(intel)
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

    # 3. the FORWARD VALUE: the reactive base posture is NOT drift -- the deployed
    #    move is proportionate at today's feed. The commoditisation bump is the ONLY
    #    reason a drift appears -> the war-gamer re-tunes BEFORE the threat lands.
    import wargamer
    tol = wargamer.enforce.tolerance_for(sig["org"])
    base_move = tcor.crossover(ph_base, tol)["chosen"]
    fwd_move = tcor.crossover(ph_fwd, tol)["chosen"]
    assert base_move == ph_base["deployed_move"], (
        "reactive base must NOT drift -- else it's a misconfig, not a forward discovery",
        base_move, ph_base["deployed_move"])
    assert fwd_move != ph_base["deployed_move"], (
        "the forward commoditisation bump must be what flips the move", base_move, fwd_move)

    # 4. the SEAM: the forward signal drives the war-gamer, and the forward re-price
    #    surfaces drift the reactive posture would have missed -> a proposed PR.
    out = forward_into_wargamer(intel)
    drifts = [r for r in out["rows"] if r["drift"]]
    assert drifts, ("the forward signal must surface at least one drift the war-gamer "
                    "re-tunes before the threat lands", out["rows"])
    assert out["proposals"], "forward drift detected but the war-gamer proposed no PR"
    for p in out["proposals"]:
        assert p["merged"] is False and p["auto_merge"] is False, p  # propose, never dispose
        assert "cross-check" in p["required_gate"], p                # rides the existing gate
        assert p["signed"] is True and "Rekor" in p["identity"], p   # attestable identity

    print(
        "ok  Wardley map: %d components, %d flagged commoditising (movement, not position); "
        "forward signal: %d attacker-capability(ies) re-priced (phishing collapse x%.2f); "
        "fed through the war-gamer -> %d forward drift(s) -> %d PR(s) proposed, 0 merged, all gated."
        % (len(mp["components"]),
           sum(1 for c in mp["components"] if c["commoditising"]),
           len(sig["risks"]), ph_fwd["forward"]["attack_cost_collapse_factor"],
           len(drifts), len(out["proposals"]))
    )


# --- CLI ----------------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("map", "forward-signal", "wargame"):
        sp = sub.add_parser(name)
        sp.add_argument("--intel", default=INTEL)
    sub.add_parser("selfcheck")
    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return
    intel = load(args.intel)
    if args.cmd == "map":
        print(json.dumps(build_map(intel), indent=2))
    elif args.cmd == "forward-signal":
        print(json.dumps(forward_signal(intel), indent=2))
    elif args.cmd == "wargame":
        print(json.dumps(forward_into_wargamer(intel), indent=2))


if __name__ == "__main__":
    main()
