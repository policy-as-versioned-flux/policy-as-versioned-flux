#!/usr/bin/env python3
"""tcor.py — the balance-sheet number: Total Cost of Risk, and the four-move crossover.

The board line is not the mean loss and not a RAG colour. It is:

    TCoR = residual (£ carried after the chosen move)
         + cost-of-controls (fix spend + dynamic-cage run-cost)
         + transfer (insurance premiums)

For every risk the war-gamer weighs the FOUR risk-financing moves and books whichever
is cheapest — the crossover is *computed*, not asserted as "best practice":

  * fix       — remediate to compliant. Loss path closed (residual -> the deny-state
                ALE, ~0); pay an engineering spend C_fix. TCoR = residual_fixed + C_fix.
  * cage      — retain-with-mitigation (../graded/cage.py): the £ picks the loosest tier
                whose caged residual fits the band; residual R'>0 + cage run-cost C_cage.
  * transfer  — cede the exposure to a carrier. Premium priced off the residual the same
                way a cyber underwriter prices it (expected loss + insurer load); you keep
                the deductible. TCoR = premium + deductible.
  * deny      — the bottom rung. Close the loss path at admission; residual -> deny-ALE,
                pay the lost-business friction C_deny. TCoR = residual_deny + C_deny.

"Compliant = cheap" is exactly the point where one move's TCoR curve crosses another's.
fix beats deny while C_fix < C_deny; transfer beats fix while a premium beats the spend;
a cheap-enough cage beats them all. Move the inputs and the winner moves — that IS the
living-£ loop:

    accept a condition  -> residual RISES     (a broader conditional grant, LEF widens)
    tighten a control   -> residual FALLS      (a narrower versioned triple)
    a cage kicks in     -> control-spend RISES (C_cage joins cost-of-controls)
    a new threat / EOL  -> the number JUMPS    (past-EOL CVEs accumulate, LM ramps)

Reuses ../fair/fair.py (the £ maths), ../risk/enforce.py (the appetite band), and
../graded/cage.py (the cage tier + its TCoR). No new risk engine, no new appetite store.

Usage:
    tcor.py moves    <risk.json>       --org driftwood   # the 4 moves + the crossover
    tcor.py sheet    <portfolio.json>  --org driftwood   # the aggregate balance sheet
    tcor.py levers   <portfolio.json>  --org driftwood   # show the £ move on each lever
    tcor.py selfcheck
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in ("fair", "risk", "graded"):
    sys.path.insert(0, os.path.join(HERE, "..", _d))
import fair     # noqa: E402  the £ maths
import enforce  # noqa: E402  the appetite band
import cage     # noqa: E402  the graded cage + its TCoR

# ponytail: insurer load = expense + risk margin above the ceded expected loss. 0.40 sits
# in the middle of real cyber quotes; a documented-controls book swings the premium 20-40%
# (research 07). Calibration knob — override per risk via transfer.load. The board line does
# not depend on the exact number, only on transfer competing against fix/cage/deny on price.
DEFAULT_LOAD = 0.40
INF = float("inf")


# --- one risk's four moves ----------------------------------------------------
def _ale(triples):
    return fair.summarize(fair.simulate(triples["lef"], triples["lm"]))["ale"]


def moves(risk, tolerance):
    """Price every risk-financing move for one risk. Each move -> a TCoR decomposition
    {residual, cost_of_controls, transfer_premium, tcor}. Unavailable move -> tcor=inf.

    risk: {warn:{lef,lm}, deny:{lef,lm}, behind?:{lef,lm}, costs:{fix,deny,transfer:{load,deductible}}}
      warn   = do-nothing exposure (the retained ALE if you act on nothing)
      deny   = loss path closed (residual ~0)
      behind = the residual a cage collapses (defaults to warn)
    """
    ale_warn = _ale(fair.state(risk, "warn"))
    ale_deny = _ale(fair.state(risk, "deny"))
    behind = risk["behind"] if "behind" in risk else risk["warn"]
    ale_behind = _ale(behind)
    costs = risk.get("costs", {})
    c_fix = float(costs.get("fix", 0.0))
    c_deny = float(costs.get("deny", 0.0))
    xfer = costs.get("transfer", {})
    load = float(xfer.get("load", DEFAULT_LOAD))
    deductible = float(xfer.get("deductible", 0.0))

    def line(residual, controls, premium):
        return {"residual": residual, "cost_of_controls": controls,
                "transfer_premium": premium, "tcor": residual + controls + premium}

    out = {}
    # fix — remediate; loss path closed, pay the engineering spend.
    out["fix"] = line(ale_deny, c_fix, 0.0)
    # cage — the £ picks the tier (../graded/cage.py); Deny-fallthrough => cage unavailable.
    tier = cage.select_tier(ale_behind, tolerance)
    if tier == "deny":
        out["cage"] = {**line(INF, 0.0, 0.0), "tier": "deny (no tier fits the band)"}
    else:
        ct = cage.tcor(ale_behind, tier)
        out["cage"] = {**line(ct["residual"], ct["cost_of_controls"], 0.0), "tier": tier}
    # transfer — premium priced off the residual (expected loss + insurer load); keep the deductible.
    premium = ale_warn * (1.0 + load)
    out["transfer"] = line(deductible, 0.0, premium)
    # deny — bottom rung: close the path, pay the lost-business friction.
    out["deny"] = line(ale_deny, c_deny, 0.0)
    return out


ORDER = ["fix", "cage", "transfer", "deny"]


def crossover(risk, tolerance):
    """The computed decision: the cheapest APPLICABLE move. Ties break by ORDER.

    A risk may narrow the field via `applicable` — you cannot fix, cage or deny an
    exposure that is not a workload you admit (a third-party integration), so it lists
    only ["transfer"] (± "deny" if you can sever it). Default = all four moves.
    """
    m = moves(risk, tolerance)
    field = [k for k in ORDER if k in risk.get("applicable", ORDER)]
    chosen = min(field, key=lambda k: (m[k]["tcor"], ORDER.index(k)))
    return {"chosen": chosen, "moves": m, "line": m[chosen]}


# --- the portfolio balance sheet ----------------------------------------------
def balance_sheet(portfolio, tolerance):
    """The board line: sum each risk's cheapest-move TCoR into the three-line total."""
    residual = controls = premium = 0.0
    rows = []
    for risk in portfolio["risks"]:
        c = crossover(risk, tolerance)
        ln = c["line"]
        residual += ln["residual"]
        controls += ln["cost_of_controls"]
        premium += ln["transfer_premium"]
        rows.append({"id": risk.get("id", risk.get("name")), "chosen": c["chosen"],
                     **{k: ln[k] for k in ("residual", "cost_of_controls", "transfer_premium", "tcor")}})
    return {
        "org": portfolio.get("org"),
        "residual": residual,             # £ carried after each chosen move
        "cost_of_controls": controls,     # fix spend + dynamic-cage run-cost
        "transfer_premium": premium,      # insurance premiums
        "tcor": residual + controls + premium,   # THE balance-sheet number
        "rows": rows,
    }


# --- the moving-£ levers (pure portfolio transforms) --------------------------
# Each lever scales one triple across the whole book — an estate-wide reassessment.
# `warn` drives the transfer premium and the do-nothing exposure; `behind` drives the
# cage residual — scale both so an exposure move reaches whichever move a row booked.
def _scale(portfolio, key, factor):
    pf = copy.deepcopy(portfolio)
    for r in pf["risks"]:
        for state in ("warn", "behind"):
            if state in r:
                r[state][key] = [v * factor for v in r[state][key]]
    return pf


def accept_condition(pf, factor=1.6):
    """Grant a broader conditional branch -> more loss events land -> LEF widens."""
    return _scale(pf, "lef", factor)


def tighten_control(pf, factor=0.5):
    """Tighten the versioned control -> the exposure shrinks -> LM narrows."""
    return _scale(pf, "lm", factor)


def threat_or_eol(pf, factor=2.5):
    """A new threat / past-EOL CVE accrual -> per-event loss magnitude ramps -> LM jumps."""
    return _scale(pf, "lm", factor)


# --- CLI ----------------------------------------------------------------------
def _org_tol(args):
    return enforce.tolerance_for(args.org, args.appetite)


def cmd_moves(args):
    print(json.dumps(crossover(fair.load(args.risk), _org_tol(args)), indent=2))


def cmd_sheet(args):
    pf = fair.load(args.portfolio)
    print(json.dumps(balance_sheet(pf, _org_tol(args)), indent=2))


def cmd_levers(args):
    pf = fair.load(args.portfolio)
    tol = _org_tol(args)
    show = {"baseline_tcor": balance_sheet(pf, tol)["tcor"]}
    for name, fn in (("accept_condition", accept_condition),
                     ("tighten_control", tighten_control),
                     ("threat_or_eol", threat_or_eol)):
        show[name] = balance_sheet(fn(pf), tol)["tcor"]
    print(json.dumps(show, indent=2))


def cmd_selfcheck(_args):
    tol = enforce.tolerance_for("driftwood")            # £40k band
    pf = fair.load(os.path.join(HERE, "scenarios", "driftwood-portfolio.json"))

    # 1. Every move books a TCoR = residual + cost-of-controls + transfer premium.
    r = pf["risks"][0]
    m = moves(r, tol)
    for k, ln in m.items():
        if ln["tcor"] == INF:
            continue
        assert abs(ln["tcor"] - (ln["residual"] + ln["cost_of_controls"]
                                 + ln["transfer_premium"])) < 1e-6, (k, ln)
    # ...and each move books the right kind of £: fix/deny -> controls (no premium);
    #    cage -> a positive retained residual AND controls; transfer -> a premium, no controls.
    assert m["fix"]["cost_of_controls"] > 0 and m["fix"]["transfer_premium"] == 0, m["fix"]
    assert m["cage"]["residual"] > 0 and m["cage"]["cost_of_controls"] > 0, m["cage"]
    assert m["transfer"]["transfer_premium"] > 0 and m["transfer"]["cost_of_controls"] == 0, m["transfer"]
    assert m["deny"]["cost_of_controls"] > 0 and m["deny"]["transfer_premium"] == 0, m["deny"]

    # 2. The crossover is COMPUTED: the cheapest move wins, and moving a cost flips it.
    #    A cheap fix wins; make the fix ruinous and the same risk crosses over to another move.
    cheap = crossover(r, tol)
    assert cheap["chosen"] == min(cheap["moves"], key=lambda k: cheap["moves"][k]["tcor"]), cheap
    r_pricey = copy.deepcopy(r)
    r_pricey["costs"]["fix"] = 10_000_000            # fixing is now absurd
    crossed = crossover(r_pricey, tol)
    assert crossed["chosen"] != "fix", crossed        # it crossed OFF fix
    assert crossed["moves"][crossed["chosen"]]["tcor"] < crossed["moves"]["fix"]["tcor"], crossed
    # crossover between fix and deny is exactly C_fix vs C_deny (same closed-path residual):
    assert (m["fix"]["tcor"] < m["deny"]["tcor"]) == (r["costs"]["fix"] < r["costs"]["deny"]), m

    # 3. The balance-sheet number = the three lines summed, over the whole portfolio.
    bs = balance_sheet(pf, tol)
    assert abs(bs["tcor"] - (bs["residual"] + bs["cost_of_controls"]
                             + bs["transfer_premium"])) < 1e-6, bs
    assert abs(bs["tcor"] - sum(row["tcor"] for row in bs["rows"])) < 1e-6, bs
    # at least one risk in the book is transferred -> the premium line is real, not decorative.
    assert bs["transfer_premium"] > 0, bs

    # 4. THE LIVING-£ LOOP — the number moves in the direction each lever predicts.
    base = bs["tcor"]
    up = balance_sheet(accept_condition(pf), tol)["tcor"]
    dn = balance_sheet(tighten_control(pf), tol)["tcor"]
    jump = balance_sheet(threat_or_eol(pf), tol)["tcor"]
    assert up > base, ("accept a condition must RAISE the £", base, up)
    assert dn < base, ("tighten a control must LOWER the £", base, dn)
    assert jump > up, ("a new threat/EOL must JUMP the £ hardest", base, up, jump)

    # 4b. A cage kicking in RAISES the cost-of-controls line: a risk cheapest to retain-bare
    #     (controls 0) versus the same risk forced past the point where a cage is cheapest.
    retain = {"warn": {"lef": [0, 0, 1], "lm": [100, 200, 300]},        # trivial: transfer wins, controls 0
              "deny": {"lef": [0, 0, 0], "lm": [100, 200, 300]},
              "costs": {"fix": 9_000, "deny": 9_000, "transfer": {"load": 0.4, "deductible": 200}}}
    caged = {"warn": {"lef": [3, 6, 12], "lm": [1500, 5000, 9000]},     # real exposure: a cage is cheapest
             "deny": {"lef": [0, 0, 1], "lm": [1500, 5000, 9000]},
             "costs": {"fix": 50_000, "deny": 80_000, "transfer": {"load": 0.9, "deductible": 30_000}}}
    c_retain = crossover(retain, tol)
    c_caged = crossover(caged, tol)
    assert c_caged["chosen"] == "cage", c_caged
    assert c_caged["line"]["cost_of_controls"] > c_retain["line"]["cost_of_controls"], \
        ("a cage kicking in must raise control-spend", c_retain["line"], c_caged["line"])

    print(
        "ok  balance sheet £%.0f = residual £%.0f + controls £%.0f + premium £%.0f | "
        "levers: accept->£%.0f  tighten->£%.0f  threat/EOL->£%.0f | "
        "crossover: cheap-fix->%s, ruinous-fix->%s"
        % (bs["tcor"], bs["residual"], bs["cost_of_controls"], bs["transfer_premium"],
           up, dn, jump, cheap["chosen"], crossed["chosen"])
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Total Cost of Risk: the balance-sheet number + the four-move crossover.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("moves", help="the four moves priced + the computed crossover (one risk)")
    pm.add_argument("risk")
    pm.add_argument("--org", required=True)
    pm.add_argument("--appetite", default=enforce.DEFAULT_APPETITE)
    pm.set_defaults(func=cmd_moves)

    ps = sub.add_parser("sheet", help="the aggregate balance sheet (a portfolio)")
    ps.add_argument("portfolio")
    ps.add_argument("--org", required=True)
    ps.add_argument("--appetite", default=enforce.DEFAULT_APPETITE)
    ps.set_defaults(func=cmd_sheet)

    pl = sub.add_parser("levers", help="show the £ move as each lever is pulled")
    pl.add_argument("portfolio")
    pl.add_argument("--org", required=True)
    pl.add_argument("--appetite", default=enforce.DEFAULT_APPETITE)
    pl.set_defaults(func=cmd_levers)

    pk = sub.add_parser("selfcheck", help="run the TCoR assertions")
    pk.set_defaults(func=cmd_selfcheck)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
