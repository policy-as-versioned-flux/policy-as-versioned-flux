#!/usr/bin/env python3
"""wardley.py -- the AI-Wardley forward layer (spec stories 28, 32; ticket 23).

The fifth, FORWARD feed. The reactive feeds (threat register / CVE / EOL) report
what has already been seen. This layer maps MARKET intel onto a Wardley map and
reads the one thing the reactive feeds structurally cannot: components still
MOVING right. When an attacker-capability commoditises, its cost collapses and
the linked risk's loss-event-frequency rises BEFORE a single incident lands. When
a DEFENSIVE capability commoditises -- and its enactment is CORROBORATED, not
merely asserted -- the cost of the control it makes cheaper falls instead
(ticket 19). Either way this becomes a forward signal the war-gamer re-prices
ahead of time -- proportionality re-tunes before the threat, not after.

Three jobs (the ticket's three acceptance criteria):

  1. MAP  -- place every component on the evolution axis, project it forward over
            the intel horizon, and FLAG commoditisation MOVEMENT (a component that
            crosses a stage boundary, or reaches commodity, within the horizon).
  2. FORWARD SIGNAL -- for each commoditising ATTACKER-capability, collapse the
            attack cost into a forward LEF bump on its linked war-game risk; for
            each commoditising DEFENSIVE capability with a CORROBORATED enactment
            (enactment.json, gated fail-closed by corroborated_enactment() --
            ticket 19), collapse the cost of the control it makes cheaper
            (C_fix / C_cage via ../tcor's costs.cage_discount) instead. Either
            way, emit a scenario library in the exact shape the war-gamer already
            consumes (../wargamer + ../tcor). `forward_into_wargamer()` feeds it
            straight through the war-gamer's own scenario war-game.
  3. ATTESTABLE -- the map + intel are detached-signed (sign-map.sh, feeds key)
            and land as a reviewable, verifiable commit; a tampered map fails.

Pure/offline. Reuses wargamer.py unchanged; ../tcor/tcor.py gained one optional,
backward-compatible field (costs.cage_discount, default 1.0) for this ticket.

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
# Independent enactment corroboration (ticket 19) -- deliberately NOT inside
# market-intel.json. market-intel.json is platform's own commoditisation CLAIM, signed
# with the feeds key; a claim cannot corroborate itself. This file carries the editorial
# "which control would this commoditising defence make cheaper" link (the defensive
# mirror of an attacker-capability's own base_risk) AND the independent "was it actually
# enacted" channel, gated fail-closed by corroborated_enactment() below.
ENACTMENT = os.path.join(HERE, "enactment.json")

# Evolution-axis stage boundaries (Wardley's genesis/custom/product/commodity).
STAGES = [(0.25, "genesis"), (0.50, "custom"), (0.75, "product"), (1.01, "commodity")]

# How hard a commoditisation MOVEMENT bumps the linked attacker LEF. The movement
# (proj - evolution) is bounded in [0,1]; K scales it into a frequency multiplier
# (factor = 1 + K*movement; movement = velocity*horizon, so K*horizon is the one
# quantity that matters -- K and horizon are not independent knobs).
# ponytail: one linear knob, editorial -- a calibration dial, not a physics law.
# K=4.0 is MEASURED, not inherited: it sits in a stable plateau (3.0-5.0) for the
# current slate (full sweep: .scratch/multi-org-estate/research/scenario-slate.md
# S6). Do NOT "widen K to flip a move sooner" -- that advice is UNSAFE. cage.py's
# select_tier() returns the LOOSEST tier that still fits the band, and the tier
# TCoR curves cross, so cage TCoR is NON-MONOTONE in the threat: between K=5 and
# K=6 phishing-kits-aas STOPS drifting (a worse threat selects a tighter, cheaper
# tier). Changing K means re-running that sweep, not asserting a bigger number is
# safer. Upgrade path: a per-component collapse curve if one trajectory needs its
# own shape.
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


def load_enactment(path=ENACTMENT):
    with open(path) as fh:
        return json.load(fh)


NOT_ENACTED = "no-corroborated-enactment"


def corroborated_enactment(component_id, enactment=None):
    """Fail-closed enactment gate (ticket 19), mirroring the shape of the twin project's
    declared_by_subject / NOT_ENACTED gate (twin/corroboration.py): a claim about a defence's
    own commoditisation cannot corroborate whether that defence was actually put in place.

    Three ways to fail closed, all returning NOT_ENACTED: no record at all for this component;
    a record that is itself self-declared (declared_by_subject is not explicitly False); or a
    record that names evidence not one of which resolves to a real file on disk. A record with
    no evidence at all is the self-declared case by construction -- there is nothing independent
    to point at."""
    enactment = load_enactment() if enactment is None else enactment
    entry = enactment.get("components", {}).get(component_id)
    if entry is None:
        return {"corroborated": False, "reason": NOT_ENACTED,
                "detail": "%r carries no enactment record at all" % component_id}
    if entry.get("declared_by_subject", True) is not False:
        return {"corroborated": False, "reason": NOT_ENACTED,
                "detail": "%r's enactment record is self-declared, not independently observed"
                          % component_id}
    evidence = entry.get("evidence") or []
    missing = [e for e in evidence if not os.path.isfile(os.path.join(HERE, e))]
    if not evidence or missing:
        return {"corroborated": False, "reason": NOT_ENACTED,
                "detail": "%r names no evidence that resolves on disk (missing: %s)"
                          % (component_id, missing or "none named")}
    return {"corroborated": True, "reason": None,
            "detail": "independent channel %r, %d evidence path(s) resolve"
                      % (entry.get("channel"), len(evidence))}


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


def _forward_defence(component_id, entry, movement):
    """Collapse a commoditising DEFENSIVE capability's movement into a forward DISCOUNT on
    the cost-of-controls (C_fix / C_cage) of the control it makes cheaper -- the mirror
    image of _forward_risk: same K, opposite direction. LEF is left untouched: a cheaper
    defence does not change how often an attacker succeeds, only what it costs to build
    (C_fix) or run (C_cage) the control that stops them. Never called uncorroborated --
    forward_signal() gates on corroborated_enactment() first."""
    factor = 1.0 / (1.0 + ATTACK_COST_COLLAPSE_K * movement)
    r = copy.deepcopy(entry["control_risk"])
    r["costs"]["fix"] = round(r["costs"]["fix"] * factor, 2)
    r["costs"]["cage_discount"] = round(factor, 4)
    r["author"] = "ai-generated"
    r["forward"] = {"component": component_id, "movement": movement,
                    "control_cost_collapse_factor": round(factor, 3)}
    return r


def forward_signal(intel, org, enactment=None):
    """The forward scenario library for ONE institution -- war-gamer shape
    ({org, risks:[...]}). One risk per commoditising attacker-capability that carries a
    base FAIR posture (LEF bumped up), PLUS one per commoditising defensive-capability
    whose enactment is CORROBORATED (cost-of-controls discounted down) -- the same market
    movement, labelled for the institution whose band it will be priced against
    downstream. A commoditising defence with no corroborated enactment emits nothing:
    fail closed, no corroboration means no credit."""
    mp = {r["id"]: r for r in build_map(intel)["components"]}
    enact = load_enactment() if enactment is None else enactment
    risks = []
    for c in intel["components"]:
        row = mp[c["id"]]
        if not row["commoditising"]:
            continue
        if c["actor"] == "attacker-capability":
            if not c.get("base_risk"):
                continue
            risks.append(_forward_risk(c, row["movement"]))
        elif c["actor"] == "defensive-capability":
            entry = enact.get("components", {}).get(c["id"])
            if entry is None or "control_risk" not in entry:
                continue
            if not corroborated_enactment(c["id"], enact)["corroborated"]:
                continue
            risks.append(_forward_defence(c["id"], entry, row["movement"]))
    return {
        "org": org,
        "note": ("AI-Wardley forward signal (%s): %d commoditising attacker-capability(ies) "
                 "re-priced, %d commoditising defence(s) credited on corroborated enactment, "
                 "ahead of the reactive feeds."
                 % (org, sum(1 for r in risks if "attack_cost_collapse_factor" in r.get("forward", {})),
                    sum(1 for r in risks if "control_cost_collapse_factor" in r.get("forward", {})))),
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

    # 2. FORWARD SIGNAL: commoditising ATTACKER-capabilities raise LEF (attacker risk);
    #    a commoditising DEFENSIVE capability with corroborated enactment lowers
    #    cost-of-controls instead (ticket 19) -- neither ever moves the other's number.
    sig = forward_signal(intel, "driftwood")
    ids = {r["forward"]["component"] for r in sig["risks"]}
    attacker_ids = {r["forward"]["component"] for r in sig["risks"]
                     if "attack_cost_collapse_factor" in r["forward"]}
    defence_ids = {r["forward"]["component"] for r in sig["risks"]
                    if "control_cost_collapse_factor" in r["forward"]}
    assert "spiffe-workload-identity" not in attacker_ids, "a commoditising defence must never raise attacker risk"
    assert "spiffe-workload-identity" in defence_ids, (
        "spiffe-workload-identity is the corroborated test case -- it must move a number", ids)
    assert "credential-stuffing-aas" not in ids, "already-commodity (no movement) must not signal"
    assert {"phishing-kits-aas", "ransomware-aas"} <= attacker_ids, ("expected the commoditising attacker "
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

    # 2c. THE DEFENSIVE CREDIT (ticket 19): spiffe-workload-identity is the test case --
    #     already on the map, already flagged commoditising, previously unable to move a
    #     number at all. Its forward entry must lower cost-of-controls, never touch LEF.
    enact = load_enactment()
    spiffe_entry = enact["components"]["spiffe-workload-identity"]
    base_control = spiffe_entry["control_risk"]
    spiffe_fwd = next(r for r in sig["risks"] if r["forward"]["component"] == "spiffe-workload-identity")
    assert spiffe_fwd["forward"]["control_cost_collapse_factor"] < 1.0, spiffe_fwd
    assert spiffe_fwd["costs"]["fix"] < base_control["costs"]["fix"], (spiffe_fwd, base_control)
    assert spiffe_fwd["costs"]["cage_discount"] < 1.0, spiffe_fwd
    # LEF is byte-identical to the un-discounted control -- a cheaper defence changes what
    # the control costs, never how often an attacker succeeds:
    assert spiffe_fwd["warn"]["lef"] == base_control["warn"]["lef"], (spiffe_fwd, base_control)
    assert spiffe_fwd["behind"]["lef"] == base_control["behind"]["lef"], (spiffe_fwd, base_control)
    # the number that was previously stuck actually moves: the chosen move's own TCoR falls.
    import wargamer
    tol_dw_defence = wargamer.enforce.tolerance_for("driftwood")
    base_cross = tcor.crossover(base_control, tol_dw_defence)
    fwd_cross = tcor.crossover(spiffe_fwd, tol_dw_defence)
    assert fwd_cross["chosen"] == base_control["deployed_move"], (
        "the deployed move for the linked control must not need to flip for the bill to fall",
        base_cross, fwd_cross)
    assert fwd_cross["line"]["tcor"] < base_cross["line"]["tcor"], (
        "a corroborated commoditising defence must lower the board line", base_cross["line"], fwd_cross["line"])

    # 2d. THE GUARD BITES: plant a violation (an uncorroborated claim) and watch the credit
    #     disappear -- the way the twin's harness guards prove a gate by breaking it. Three
    #     ways to fail closed, each planted and each watched: no record, a self-declared
    #     record, and a record naming evidence that does not exist on disk.
    def _without_spiffe_credit(tampered):
        return "spiffe-workload-identity" in {
            r["forward"]["component"] for r in forward_signal(intel, "driftwood", enactment=tampered)["risks"]
            if "control_cost_collapse_factor" in r["forward"]
        }

    no_record = copy.deepcopy(enact)
    del no_record["components"]["spiffe-workload-identity"]
    assert _without_spiffe_credit(no_record) is False, "a component with no enactment record must earn no credit"

    self_declared = copy.deepcopy(enact)
    self_declared["components"]["spiffe-workload-identity"]["declared_by_subject"] = True
    assert _without_spiffe_credit(self_declared) is False, (
        "a self-declared enactment claim must earn no credit -- it cannot corroborate itself")

    forged_evidence = copy.deepcopy(enact)
    forged_evidence["components"]["spiffe-workload-identity"]["evidence"] = ["../does-not-exist.yaml"]
    assert _without_spiffe_credit(forged_evidence) is False, (
        "evidence that does not resolve on disk must earn no credit")

    # ...and the CORROBORATED case, replanted here rather than only trusted from `sig` above,
    # so this same guard proves it does not refuse everything indiscriminately:
    assert _without_spiffe_credit(enact) is True, "the genuinely corroborated case must still pass"
    verdict = corroborated_enactment("spiffe-workload-identity", no_record)
    assert verdict == {"corroborated": False, "reason": NOT_ENACTED,
                        "detail": verdict["detail"]}, verdict

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

    # 5. THE SCENARIO SLATE (ticket 06): guard against the obvious failure -- the
    #    slate must not be tuned so every scenario fires. nb-refining-capacity is
    #    the LOUDEST new flag on the map (crosses product->commodity) and carries
    #    a REAL base_risk (so the non-fire below is not vacuous), but the actor
    #    gate (supply-constraint, not attacker-capability) keeps it off the
    #    war-gamer entirely -- "this loud thing changes nothing above it".
    assert by["nb-refining-capacity"]["commoditising"] is True, by["nb-refining-capacity"]
    nb_base_risk = next(c for c in intel["components"]
                         if c["id"] == "nb-refining-capacity")["base_risk"]
    assert nb_base_risk is not None, "non-fire must not be vacuous: needs a real base_risk"
    assert "nb-refining-capacity" not in ids, (
        "a loud, non-attacker commoditisation must still emit nothing", ids)
    # pqc-transport-migration: a commoditising DEFENCE too, same shape as
    # spiffe-workload-identity -- but ticket 19 does NOT give it a linked control_risk in
    # enactment.json, on purpose. Its own market-intel.json note explains why: the
    # commoditised half (transport key agreement) is not what pq-harvest-now-decrypt-later's
    # costs.fix actually buys (discovery/inventory, WebPKI signatures, boot roots of trust
    # are the binding cost). A gate that credits any commoditising defence by construction,
    # whether or not the link is honest, would be exactly the unearned green this ticket
    # exists to refuse -- so this must still emit nothing, and for the right reason: no
    # link, not a broken one.
    assert by["pqc-transport-migration"]["commoditising"] is True, by["pqc-transport-migration"]
    assert "pqc-transport-migration" not in enact["components"], (
        "pqc-transport-migration must carry no enactment link -- it is the negative control")
    assert "pqc-transport-migration" not in ids, "an unlinked commoditising defence must not emit"

    # The slate is not tuned the OTHER way either: pkg-registry-worm DOES fire and
    # DOES flip the deployed move (cage -> fix) once the forward bump is applied.
    assert "pkg-registry-worm" in ids, ids
    worm_row = next(r for r in forward_into_wargamer(intel, "driftwood")["rows"]
                     if r["control"] == "dependency-worm-exfil")
    assert worm_row["deployed"] == "cage" and worm_row["implied"] == "fix", worm_row
    assert worm_row["drift"] is True, worm_row

    # agentic-commit-access fires and IS re-priced -- but the war-gamer proposes
    # NOTHING, because the deployed move was already `fix`. The reward for fixing
    # something is that the news stops mattering.
    assert "agentic-commit-access" in ids, ids
    agentic_base = next(c for c in intel["components"]
                         if c["id"] == "agentic-commit-access")["base_risk"]
    assert agentic_base["deployed_move"] == "fix", agentic_base
    agentic_fwd = next(r for r in sig["risks"] if r["forward"]["component"] == "agentic-commit-access")
    assert agentic_fwd["forward"]["attack_cost_collapse_factor"] > 2.0, agentic_fwd
    assert agentic_fwd["warn"]["lef"][2] > agentic_base["warn"]["lef"][2], (agentic_fwd, agentic_base)
    agentic_row = next(r for r in forward_into_wargamer(intel, "driftwood")["rows"]
                        if r["control"] == "agentic-commit-compromise")
    assert agentic_row["drift"] is False, (
        "a risk already deployed at fix must be ABSORBED, not proposed again", agentic_row)

    # 5b. THE FIX FIXED-POINT -- free, and nothing asserted it before now. fix and
    #     deny are computed from the untouched `deny` state; only cage/transfer
    #     scale with the forward bump. So a risk already deployed at `fix` cannot
    #     be flipped by ANY K or ANY movement -- proven by sweeping the bump
    #     factor directly (1 + K*movement), not just today's K=4.0 value.
    for factor in (1.0, 2.0, 4.0, 8.0, 20.0):
        bumped = copy.deepcopy(agentic_base)
        for state in ("warn", "behind"):
            bumped[state]["lef"] = [v * factor for v in bumped[state]["lef"]]
        assert tcor.crossover(bumped, tol_dw)["chosen"] == "fix", (
            "fix is a fixed point of the forward bump for every K/movement", factor)

    print(
        "ok  Wardley map: %d components, %d flagged commoditising (movement, not position); "
        "forward signal: %d attacker-capability(ies) re-priced (phishing collapse x%.2f), "
        "%d commoditising defence(s) credited on corroborated enactment (spiffe cost collapse "
        "x%.2f), per institution; fed through the war-gamer for %d institution(s) -> %d forward "
        "drift(s) -> %d PR(s) proposed, 0 merged, all gated."
        % (len(mp["components"]),
           sum(1 for c in mp["components"] if c["commoditising"]),
           len(attacker_ids), ph_fwd["forward"]["attack_cost_collapse_factor"],
           len(defence_ids), spiffe_fwd["forward"]["control_cost_collapse_factor"],
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
