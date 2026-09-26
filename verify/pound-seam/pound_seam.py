#!/usr/bin/env python3
"""pound_seam.py — ticket 25 / ADR-0020 / ADR-0021 made checkable: every adopter's composed
evidence document prices under ONE perspective in ONE currency, names where each price came
from, and attributes its tier selection to a versioned selection policy.

What it observes, per adopter, on `.estate-clone/<adopter>/composed/evidence.json`:

  1. every prices[] entry carries perspective, currency, source, kind and per_customer;
  2. per_customer is the entry's own amount over the perspective party's signed size.customers,
     or null where that party declares no customer count;
  3. exactly one `source: twin` entry when that adopter publishes a forward-intel feed, carrying
     policy_version, curve_hash and tail — and NO twin entry when it publishes no such feed;
  4. the regime entry's (source: ico, kind: feed) holes[] amounts sum to its total, and the entry's own
     amount equals the sum of the lines the adopter has not implemented (status neither
     `covered` nor `closed`), so implementing a control reduces it (eco-system ticket 121);
  5. no list of amounts anywhere in the document mixes perspectives or currencies — a sum that
     crosses either is the live bug ADR-0020 was written against (GAPS 3.18);
  6. the adopter's appetite is a signed fact on its OWN party.yaml, platform/risk/appetite.json
     is gone, and no code left behind still reads it;
  7. every selection-policy version the document names matches the adopter's published
     selection-policy/VERSION (falling back to driftwood's, the estate's published package);
  8. the curve hash the estate recorded equals the one the adopter's OWN selection-policy
     package computes over the curve its own published feed carries;
  9. the adopter's OWN selection-policy package and platform/graded/cage.py pick the SAME rung
     over the same residuals — at each band boundary, and with every rung tried as a floor;
 10. the FX bridge resolves a published rate through the fx publisher's OWN converter, and
     refuses an unpublished date as a missing instrument rather than widening it;
 11. every SERVED total says what the number is -- "an ordinal, auditable comparison under one
     perspective; not an expected annual loss" (ticket 75 Q4 (a)) -- and carries the aggregate
     of its selected-tier residuals beside the one tolerance the appetite declares, so a breach
     of that aggregate is visible. Both sentences are written by the COMPOSER, so an adopter
     composed under an older platform tag is a NAMED could-not-look that says which tag it
     waits for (eco-system ticket 79 items 9 and 10).

A price with no amount that names why on `could_not_look` is a NAMED could-not-look (SKIP),
never a FAIL and never a PASS; a price with neither, or with both, is a FAIL (eco-system
ticket 127).

Checks 8 and 9 are the two-implementations guard: ADR-0021 has a versioned package the adopter
publishes make the selection, while cage.py is the engine wired to prices[] and the proposer. If
those two drift, a proposal PR names a policy version that did not in fact pick. Neither is in
the selfcheck fixture (both read the real estate); both were proven to bite by planting a
divergence in driftwood's package and watching the check refuse it.

Grading, per the gate contract: any FAIL -> 1; else any SKIP -> 3; else 0. A real absence (an
adopter that publishes no forward-intel feed yet) prints as a NAMED pass, never a silent one; a
document that contradicts itself is a FAIL.

Needs pyyaml (hub .venv); verify-pound-seam.sh picks the interpreter.

Usage:
    pound_seam.py check        # every adopter in .estate-clone/
    pound_seam.py selfcheck    # planted defects: proves each refusal bites
"""
from __future__ import annotations

import glob
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

LINES: list[str] = []

ISO4217 = re.compile(r"^[A-Z]{3}$")
# `supersede` (eco-system ticket 84): the surcharge on a feed line whose pin sits behind a newer
# tagged major, carried beside the line under the same perspective and currency, never summed
# into the exposure; verify/supersede/ grades its arithmetic.
# `agent-cage` (eco-system ticket 145, ADR-0031): the PLATFORM's price of the twin agent's cage,
# for a subject that is not a pod (`subject: twin-agent`), carried beside the exposure; its
# `proposed_tier` is the twin agent's rung and never folds into a Namespace. Leg 3b grades it.
KINDS = {"feed", "twin", "premium", "switching", "reliability", "supersede", "agent-cage"}
SOURCES = {"ico", "feeds", "twin", "insurer", "platform"}   # plus any party name in the estate
LADDER = ("baseline", "restricted", "quarantine", "isolated")
AGENT_CAGE_KIND, AGENT_CAGE_SUBJECT = "agent-cage", "twin-agent"
AGENT_TABLE_PREFIX = "platform-twin-agent-table@"
AMOUNT_KEYS = ("amount", "total", "new_price", "old_price")
# The statuses of a regime line the adopter has implemented (eco-system ticket 121).
IMPLEMENTED = ("covered", "closed")
RETIRED_APPETITE = "risk/appetite.json"
POLICY_PACKAGE = "selection-policy"


def out(status, msg):
    LINES.append(status)
    print(f"{status}: {msg}")


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def amount_of(entry):
    """The entry's own amount. `new_price` is what composition called it before the ticket-25
    schema pass; either key is read, never both meanings at once."""
    for k in ("amount", "new_price"):
        if isinstance(entry.get(k), (int, float)) and not isinstance(entry.get(k), bool):
            return entry[k]
    return None


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6)


# --------------------------------------------------------------------------
# the document checks — pure, so selfcheck can plant defects in a dict
# --------------------------------------------------------------------------
def _mixed_sums(node, path, inherited, found):
    """Every list in the document whose elements carry an amount must be summable: one
    perspective, one currency. An element that declares neither inherits the nearest enclosing
    declaration (a hole under a regime entry is priced under that entry's perspective)."""
    if isinstance(node, dict):
        here = (node.get("perspective", inherited[0]), node.get("currency", inherited[1]))
        for k, v in node.items():
            _mixed_sums(v, f"{path}.{k}", here, found)
    elif isinstance(node, list):
        seen = {}
        for i, el in enumerate(node):
            _mixed_sums(el, f"{path}[{i}]", inherited, found)
            if isinstance(el, dict) and any(k in el for k in AMOUNT_KEYS):
                key = (el.get("perspective", inherited[0]), el.get("currency", inherited[1]))
                seen.setdefault(key, i)
        if len(seen) > 1:
            found.append((path, sorted(seen)))


def check_doc(doc, ctx):
    """Grade one adopter's evidence document. `ctx` carries the facts read off the estate:
    adopter, parties, customers (party -> size.customers or None), forward_intel (bool),
    policy_version (str or None) and policy_version_source."""
    who = ctx["adopter"]
    prices = doc.get("prices")
    if not isinstance(prices, list) or not prices:
        out("FAIL", f"{who}: composed evidence has no prices[] — an adopter with declared "
                    f"parents prices them or refuses; it never prices nothing")
        return

    # 1 + 2: labelling and the per-customer restatement
    for i, e in enumerate(prices):
        at = f"{who} prices[{i}]"
        missing = [f for f in ("perspective", "currency", "source", "kind", "per_customer")
                   if f not in e]
        if missing:
            out("FAIL", f"{at} ({e.get('source', '?')}/{e.get('name', e.get('kind', '?'))}) "
                        f"is missing {', '.join(missing)} (ADR-0021: every price carries "
                        f"perspective and currency)")
            continue
        if e["perspective"] not in ctx["parties"]:
            out("FAIL", f"{at}: perspective {e['perspective']!r} is not a party in this estate")
        if not ISO4217.match(str(e["currency"])):
            out("FAIL", f"{at}: currency {e['currency']!r} is not an ISO 4217 code")
        if e["kind"] not in KINDS:
            out("FAIL", f"{at}: kind {e['kind']!r} is not one of {sorted(KINDS)}")
        if e["source"] not in SOURCES | ctx["parties"]:
            out("FAIL", f"{at}: source {e['source']!r} is neither a party nor one of "
                        f"{sorted(SOURCES)}")
        amount = amount_of(e)
        refusal = e.get("could_not_look")
        if amount is None and isinstance(refusal, str) and refusal.strip():
            # Eco-system ticket 127. The composer writes no amount exactly when it names why
            # (platform compose/composition.py: `amount = None if could_not_look else ...`).
            # That is a named could-not-look: never a FAIL, and never a PASS.
            if e["per_customer"] is not None:
                out("FAIL", f"{at}: could not be priced ({refusal}) yet restates an amount "
                            f"per customer: {e['per_customer']!r}")
            else:
                out("SKIP", f"{at} ({e['source']}/{e.get('name', '?')} {e['kind']}) could not "
                            f"be priced, and says why: {refusal}")
            continue
        if amount is None:
            out("FAIL", f"{at}: carries no numeric amount and no could_not_look reason, so "
                        f"nothing can be restated per customer or summed")
            continue
        if refusal:
            out("FAIL", f"{at}: carries an amount {amount} and a could_not_look reason "
                        f"({refusal!r}) -- one price, priced and not priced at once")
            continue
        customers = ctx["customers"].get(e.get("perspective"))
        pc = e["per_customer"]
        if customers:
            if not isinstance(pc, dict) or "amount" not in pc or "currency" not in pc:
                out("FAIL", f"{at}: {e['perspective']} signs size.customers={customers}, so "
                            f"per_customer must be an (amount, currency), not {pc!r}")
            elif not close(pc["amount"], amount / customers):
                out("FAIL", f"{at}: per_customer {pc['amount']} is not {amount} / {customers} "
                            f"= {amount / customers}")
            elif pc["currency"] != e["currency"]:
                out("FAIL", f"{at}: per_customer currency {pc['currency']!r} is not the "
                            f"entry's own {e['currency']!r}")
        elif pc is not None:
            out("FAIL", f"{at}: {e.get('perspective')} signs no size.customers, so per_customer "
                        f"must be null, not {pc!r}")

    # 3: the twin edge
    twins = [e for e in prices if e.get("source") == "twin"]
    if ctx["forward_intel"]:
        if len(twins) != 1:
            out("FAIL", f"{who} publishes a forward-intel feed but its evidence carries "
                        f"{len(twins)} `source: twin` prices[] entries, not exactly one")
        for e in twins:
            miss = [f for f in ("policy_version", "curve_hash", "tail") if not e.get(f)]
            if e.get("kind") != "twin":
                out("FAIL", f"{who}: the twin entry declares kind {e.get('kind')!r}, not 'twin'")
            if miss:
                out("FAIL", f"{who}: the twin entry is missing {', '.join(miss)} — a twin edge "
                            f"names the policy that picked, the curve it picked from and the "
                            f"tail it priced with (ADR-0021)")
            elif e.get("perspective") != who:
                out("FAIL", f"{who}: the twin entry prices {e.get('perspective')}'s balance "
                            f"sheet but sits in {who}'s prices[] and was tiered against {who}'s "
                            f"own appetite band — one composition holds one party's band, and "
                            f"another party's money is never tiered against it (ADR-0020)")
            else:
                out("PASS", f"{who}: one twin edge, policy {e['policy_version']}, curve "
                            f"{str(e['curve_hash'])[:12]}, tail {e['tail']}, perspective "
                            f"{e.get('perspective')} in {e.get('currency')}")
    elif twins:
        out("FAIL", f"{who}: {len(twins)} `source: twin` prices[] entries but {who} publishes "
                    f"no forward-intel feed — a twin price with no signed scenario behind it")
    else:
        out("PASS", f"{who}: publishes no forward-intel feed yet, so no twin entry is expected "
                    f"(named absence, not a silent pass)")

    # 3b: the twin agent's cage line (eco-system ticket 145; ADR-0031). At most one, priced by
    # the PLATFORM for the subject it names -- the twin never prices its own cage -- and, when
    # priced, carrying the derivation the rung can be re-derived from: residuals at every rung
    # under a named twin-agent table, what each misuse path reaches, the rungs that close them,
    # the scenario (the gap read off THIS document's twin line, over a window with a source) and
    # the register row's frequency. Check 3 counts `source: twin` lines and stays honest: this
    # line's source is `platform`. An unpriced line was printed by leg 1 as a named SKIP; here it
    # may propose no rung.
    agents = [e for e in prices if e.get("kind") == AGENT_CAGE_KIND]
    if len(agents) > 1:
        out("FAIL", f"{who}: {len(agents)} `agent-cage` prices[] entries; the twin agent has one "
                    f"cage and one line (eco-system ticket 145)")
    for e in agents:
        at = f"{who} prices[{prices.index(e)}] agent-cage"
        if e.get("subject") != AGENT_CAGE_SUBJECT:
            out("FAIL", f"{at}: names subject {e.get('subject')!r}, not {AGENT_CAGE_SUBJECT!r}; a "
                        f"kind for a subject that is not a pod names its subject on the line")
        if e.get("source") != "platform":
            out("FAIL", f"{at}: priced by {e.get('source')!r}; the platform prices the twin agent's "
                        f"cage and the twin never prices its own (ADR-0031 decision 5)")
        if amount_of(e) is None:
            if e.get("proposed_tier") is not None:
                out("FAIL", f"{at}: could not be priced yet proposes rung {e.get('proposed_tier')!r}")
            continue
        missing = [f for f in ("proposed_tier", "residuals", "residual_basis", "reach", "closes",
                               "scenario", "lef", "lef_from", "policy_version", "window")
                   if e.get(f) in (None, {}, [], "")]
        if missing:
            out("FAIL", f"{at}: priced, but carries no {', '.join(missing)} -- the rung cannot be "
                        f"re-derived from the line (ADR-0021)")
            continue
        tier, residuals = e["proposed_tier"], e["residuals"]
        if tier not in LADDER:
            out("FAIL", f"{at}: proposes rung {tier!r}, which is not on the ladder {list(LADDER)}")
            continue
        if not isinstance(residuals, dict) or set(residuals) != set(LADDER):
            out("FAIL", f"{at}: residuals cover {sorted(residuals) if isinstance(residuals, dict) else residuals!r}, "
                        f"not every rung {list(LADDER)}")
            continue
        if residuals.get(tier) is None:
            out("FAIL", f"{at}: selected {tier!r}, a rung whose residual could not be derived")
            continue
        if not str(e["residual_basis"]).startswith(AGENT_TABLE_PREFIX):
            out("FAIL", f"{at}: residual_basis {e['residual_basis']!r} names no twin-agent table "
                        f"({AGENT_TABLE_PREFIX}<version>); pod reductions never price the twin agent")
        if e.get("lef_from") != "threat-register":
            out("FAIL", f"{at}: frequency comes from {e.get('lef_from')!r}, not the threat register "
                        f"(ticket 30 decision 12)")
        sc = e["scenario"]
        twin = twins[0] if len(twins) == 1 else None
        tres = (twin or {}).get("residuals") or {}
        loosest, selected = sc.get("loosest_pod_tier"), sc.get("selected_pod_tier")
        if twin is None or loosest not in tres or selected not in tres:
            out("FAIL", f"{at}: its gap reads rungs {loosest!r} and {selected!r} off a twin line this "
                        f"document does not carry residuals for")
        elif selected != twin.get("proposed_tier"):
            out("FAIL", f"{at}: its gap is read at pod rung {selected!r}, but the twin line selected "
                        f"{twin.get('proposed_tier')!r}")
        elif not close(float(sc.get("gap", -1)), float(tres[loosest]) - float(tres[selected])):
            out("FAIL", f"{at}: gap {sc.get('gap')} is not the twin line's {loosest} residual "
                        f"({tres[loosest]}) minus its {selected} residual ({tres[selected]})")
        elif not (isinstance(sc.get("lm"), list) and len(sc["lm"]) == 3
                  and all(close(float(x), float(sc["gap"]) * float(sc.get("window_days", 0)) / 365.25)
                          for x in sc["lm"])):
            out("FAIL", f"{at}: loss magnitude {sc.get('lm')} is not the gap {sc.get('gap')} times "
                        f"the window ({sc.get('window_days')} day(s) of 365.25)")
        elif not sc.get("window_source"):
            out("FAIL", f"{at}: the detection window names no source")
        elif sc.get("annualised_by") == "expectation" and not close(
                amount_of(e),
                (float(e["lef"][0]) + 4.0 * float(e["lef"][1]) + float(e["lef"][2])) / 6.0
                * (float(sc["lm"][0]) + 4.0 * float(sc["lm"][1]) + float(sc["lm"][2])) / 6.0):
            out("FAIL", f"{at}: amount {amount_of(e)} is not the PERT-mean frequency times the "
                        f"PERT-mean magnitude the line says it was annualised by")
        elif residuals["restricted"] != residuals["baseline"]:
            out("FAIL", f"{at}: restricted's residual ({residuals['restricted']}) differs from "
                        f"baseline's ({residuals['baseline']}); a model claim never prices, so the "
                        f"model step closes no priced loss (ADR-0031 consequences)")
        else:
            out("PASS", f"{at}: the platform prices the twin agent's cage under {e['residual_basis']} "
                        f"at rung {tier!r} (policy {e['policy_version']}), a gap of "
                        f"{float(sc['gap']):,.2f} {e.get('currency')} between pod rungs "
                        f"{loosest!r} and {selected!r} over {sc.get('window_days')} day(s), at "
                        f"threat-register@{e.get('register_version')}'s frequency; restricted "
                        f"carries baseline's residual and isolated {residuals['isolated']}")

    # 4: the regime entry's holes partition it. The regime entry is ico's `kind: feed`
    # price. ico's switching and supersede prices are not regime entries and carry no
    # holes[]; they are graded by the legs above and by verify/supersede/ (eco-system
    # ticket 127). A regime entry the composer could not price is the SKIP leg 1 printed.
    regimes = [e for e in prices if e.get("source") == "ico" and e.get("kind") == "feed"]
    if not regimes:
        out("PASS", f"{who}: declares no ico regime edge, so there is no hole breakdown to "
                    f"check (named absence)")
    for e in regimes:
        if amount_of(e) is None and e.get("could_not_look"):
            continue
        at = f"{who} regime entry ({e.get('name', 'penalty-schema')})"
        holes = e.get("holes")
        weights = ctx.get("regime_weights") or {}
        if not holes and not weights.get("available"):
            # A could-not-look, NOT a pass: the version this adopter pins publishes no
            # control_weights, so nothing partitions the regime exposure — and that absence is
            # one pin bump away from being observable. A green here would be a green for a
            # requirement no adopter satisfies.
            out("SKIP", f"{at}: pinned at {weights.get('version')}, which publishes no "
                        f"control_weights, so the hole partition could not be looked at "
                        f"(the weights ship in ico penalty-schema v3)")
            continue
        if not isinstance(holes, list):
            out("FAIL", f"{at}: carries no holes[] — a regime price is the sum of its holes, so "
                        f"implementing one reduces it (ticket 15 answer 1)")
            continue
        bad = [h for h in holes if not isinstance(h, dict)
               or not {"source", "id", "weight", "amount"} <= set(h)]
        if bad:
            out("FAIL", f"{at}: {len(bad)} hole(s) missing source/id/weight/amount: {bad[:1]}")
            continue
        total = e.get("total")
        s = sum(h["amount"] for h in holes)
        # Eco-system ticket 121: the entry prices the lines still open. A line
        # the adopter implements reads `covered` or `closed` and comes off.
        still_open = sum(h["amount"] for h in holes if h.get("status") not in IMPLEMENTED)
        weight_sum = sum(float(h["weight"]) for h in holes)
        priced = e.get("new_price")
        if not isinstance(total, (int, float)):
            out("FAIL", f"{at}: holes[] with no total")
        elif not close(s, total):
            out("FAIL", f"{at}: holes[] sum to {s} but total says {total}")
        elif not close(weight_sum, 1.0):
            # A partition covers the whole exposure. Weights summing to less than one
            # silently shrink the regime price; more than one double-counts it.
            out("FAIL", f"{at}: its published control weights sum to {weight_sum}, not 1.0 — a "
                        f"partition that does not cover the exposure is not a partition, and "
                        f"the share it leaves out has no price")
        elif isinstance(priced, (int, float)) and not close(priced, still_open):
            out("FAIL", f"{at}: the entry prices the regime at {priced} but its open lines sum "
                        f"to {still_open} — one entry, two contradictory prices")
        elif (amt := amount_of(e)) is not None and not close(amt, still_open):
            out("FAIL", f"{at}: amount {amt} is not the sum of its open lines {still_open} (a "
                        f"line reading covered or closed is implemented and comes off; ticket 121)")
        else:
            out("PASS", f"{at}: {len(holes)} priced hole(s) sum to its total {total:,.2f} "
                        f"{e.get('currency')}; the open lines price it at {still_open:,.2f}")
        for h in holes:
            if not isinstance(h["weight"], (int, float)) or not 0 < h["weight"] <= 1:
                out("FAIL", f"{at}: hole {h['source']}/{h['id']} has weight {h['weight']!r}, "
                            f"not a share in (0, 1]")

    # 5: nothing in the document is summable across a perspective or a currency
    found = []
    _mixed_sums(doc, who, (None, None), found)
    for path, keys in found:
        out("FAIL", f"{who}: {path} is a list of amounts spanning {keys} — a sum there would "
                    f"cross perspectives or currencies (ADR-0020)")
    if not found:
        out("PASS", f"{who}: every list of amounts in the document is one perspective in one "
                    f"currency")

    # 7: the selection policy that picked is named and versioned
    named = sorted({v for v in _walk_key(doc, "policy_version")})
    if named and ctx["policy_version"] is None:
        out("FAIL", f"{who}: names selection policy {named} but no {POLICY_PACKAGE}/VERSION is "
                    f"published anywhere in the estate")
    elif named and any(v != ctx["policy_version"] for v in named):
        out("FAIL", f"{who}: names selection policy {named}, but "
                    f"{ctx['policy_version_source']} says {ctx['policy_version']!r}")
    elif named:
        out("PASS", f"{who}: selection policy {ctx['policy_version']} matches "
                    f"{ctx['policy_version_source']}")
    elif ctx["forward_intel"]:
        out("FAIL", f"{who}: publishes forward intel but its evidence names no policy_version — "
                    f"the curve never picks (ADR-0021)")
    else:
        out("PASS", f"{who}: selects no tier through a published selection policy yet "
                    f"(named absence: no forward-intel feed)")


def _walk_key(node, key):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and v is not None:
                yield v
            else:
                yield from _walk_key(v, key)
    elif isinstance(node, list):
        for el in node:
            yield from _walk_key(el, key)


# --------------------------------------------------------------------------
# reading the estate
# --------------------------------------------------------------------------
def _parties(estate):
    return {os.path.basename(os.path.dirname(p)): load_yaml(p)
            for p in sorted(glob.glob(os.path.join(estate, "*", "party.yaml")))}


def _policy_version(estate, adopter):
    """The adopter's own published selection-policy version, else driftwood's — the one package
    ticket 25 publishes and Renovate pins."""
    for owner in (adopter, "driftwood"):
        p = os.path.join(estate, owner, POLICY_PACKAGE, "VERSION")
        if os.path.exists(p):
            with open(p) as fh:
                return fh.read().strip(), f"{owner}/{POLICY_PACKAGE}/VERSION"
    return None, None


def _regime_weights(estate, parties, adopter_doc):
    """The version of the regime feed this adopter pins, and whether that version publishes the
    control_weights a hole breakdown partitions by (ico penalty-schema v3 onward)."""
    for edge in adopter_doc.get("inherits") or []:
        if edge.get("kind") != "feed" or edge.get("party") != "ico":
            continue
        pub = parties.get("ico") or {}
        path = next((r.get("path") for r in pub.get("publishes") or []
                     if r.get("name") == edge.get("name")), edge.get("name"))
        feed = os.path.join(estate, "ico", str(path), str(edge.get("version")), "feed.json")
        available = False
        if os.path.exists(feed):
            with open(feed) as fh:
                available = "control_weights" in fh.read()
        return {"version": edge.get("version"), "available": available}
    return {"version": None, "available": False}


def check_appetite(estate, parties):
    """Appetite is the adopter's own signed fact. The platform fixture is retired, and no reader
    is left pointing at it."""
    stale = os.path.join(estate, "platform", RETIRED_APPETITE)
    if os.path.exists(stale):
        out("FAIL", f"platform/{RETIRED_APPETITE} still exists — appetite is a signed fact on "
                    f"each party's own party.yaml (ticket 08 answer 5, ADR-0021)")
    else:
        out("PASS", f"platform/{RETIRED_APPETITE} is retired")
        # A deleted fixture with a live reader still pointing at it is the self-contradicting
        # case: the reader crashes, or worse, silently falls back. ponytail CEILING: this is a
        # one-line grep over python and shell, keeping only lines that name the path AND open
        # it. A reader that puts the path in a constant and opens the constant somewhere else
        # — the idiomatic form — is invisible to it, and so is a yaml manifest that mounts the
        # file. Blast radius is small because the fixture is genuinely deleted, so a surviving
        # reader crashes rather than reading a stale band. Upgrade path: an import-graph walk,
        # or drop the loader-token filter and eyeball every live mention.
        try:
            hits = subprocess.run(["grep", "-rn", "--exclude-dir=.git", "--exclude-dir=.work",
                                   "--exclude-dir=__pycache__", "appetite.json", estate],
                                  capture_output=True, text=True, timeout=120).stdout.splitlines()
        except (OSError, subprocess.SubprocessError) as exc:
            out("SKIP", f"could not grep the estate for readers of {RETIRED_APPETITE}: {exc}")
            hits = []
        loaders = ("open(", "read_text", "json.load", "-f ", "cat ")
        code = sorted({h.split(":", 1)[0] for h in hits
                       if h.split(":")[0].endswith((".py", ".sh"))
                       and not h.split(":", 2)[-1].lstrip().startswith("#")
                       and any(m in h.split(":", 2)[-1] for m in loaders)})
        if code:
            out("FAIL", f"{len(code)} file(s) still load the retired {RETIRED_APPETITE}: "
                        f"{', '.join(os.path.relpath(h, estate) for h in code[:6])}")
        else:
            out("PASS", "no python or shell line in the estate both names the retired appetite "
                        "fixture and opens it (a path held in a constant and opened elsewhere "
                        "is outside this grep's reach -- see the ceiling note above)")

    for name, doc in sorted(parties.items()):
        if "adopter" not in (doc.get("roles") or []):
            continue
        tol = (doc.get("appetite") or {}).get("tolerance")
        if not isinstance(tol, dict) or "amount" not in tol or "currency" not in tol:
            out("FAIL", f"{name}: party.yaml declares no appetite.tolerance (amount, currency) "
                        f"— a party with no appetite is a MISSING INSTRUMENT and refuses "
                        f"(ADR-0020)")
        else:
            out("PASS", f"{name}: appetite {tol['amount']:,} {tol['currency']}, signed on its "
                        f"own party.yaml")


def check_curve_agreement(estate, parties):
    """The estate and the adopter must not disagree about WHICH curve was priced.

    Two implementations of the same digest exist by design: the estate's, inside
    `platform/compose/composition.py:_curve_hash`, and the adopter's own vendorable
    `selection-policy/selection_policy.py:curve_hash` (ADR-0021 -- the package is the thing
    Renovate pins and the proposal PR names). Nothing else asserts they stay in step, so a
    drift would show up only as a rejection ledger that silently stops resetting. This runs
    the ADOPTER's function over the curve its OWN published feed carries and compares it with
    the hash the estate recorded in the composed evidence.
    """
    for name, doc in sorted(parties.items()):
        feed = _forward_intel_feed(estate, name, doc)
        ev = os.path.join(estate, name, "composed", "evidence.json")
        if not (feed and os.path.exists(ev)):
            continue                    # not a publisher of forward intel: nothing to compare
        pkg = os.path.join(estate, name, POLICY_PACKAGE, "selection_policy.py")
        if not os.path.exists(pkg):
            # A party that publishes a curve and composed evidence but ships no
            # package: the comparison cannot be made. That is a could-not-look,
            # not a pass, and never silence — the wrapper's sentence claims the
            # two engines agree, and silence would let it claim it of nobody.
            out("SKIP", f"{name} publishes forward intel but no {POLICY_PACKAGE} package, so "
                        f"the curve hash the estate recorded cannot be checked against the "
                        f"adopter's own")
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"_sp_{name}", pkg)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            with open(feed) as fh:
                curve = json.load(fh)["payload"]["curve"]
            with open(ev) as fh:
                recorded = [e.get("curve_hash") for e in (json.load(fh).get("prices") or [])
                            if e.get("source") == "twin"]
        except Exception as exc:                                  # noqa: BLE001 -- report, never crash
            out("FAIL", f"{name}: could not run its own {POLICY_PACKAGE} curve_hash against its "
                        f"published curve: {exc}")
            continue
        theirs = mod.curve_hash(curve)
        if not recorded:
            continue          # check 3 already graded the missing twin edge
        if any(r != theirs for r in recorded):
            out("FAIL", f"{name}: the estate recorded curve_hash {recorded[0]!r} but {name}'s own "
                        f"{POLICY_PACKAGE} package hashes its published curve as {theirs!r} — the "
                        f"two engines disagree about which curve was priced (ADR-0021)")
        else:
            out("PASS", f"{name}: the estate and {name}'s own {POLICY_PACKAGE} package agree on "
                        f"the curve hash ({theirs[:19]}) — one curve, two implementations, "
                        f"no drift")


def check_residual_basis(estate, parties):
    """WHOSE reduction set priced the twin entry, and do the two disagree about the rung?

    The residuals on a `source: twin` entry are `ale * (1 - reduce)` off `platform/graded/cage.py`,
    a table that flags itself as calibration knobs evidenced by nothing. The adopter publishes its
    OWN graded response curve, and driftwood's is materially different -- mode reductions of
    0.05/0.30/0.65/0.90 against the table's 0.30/0.70/0.92/0.98. The rung came out the same, but
    the sentence the entry carried about WHY was only true of a table the adopter did not author.

    Two things, both observations:
      1. the entry NAMES the reduction set that priced it (`residual_basis`);
      2. the table and the adopter's own published curve still agree about which rung is cheapest.
         That is what the selection actually turns on, and it is checkable from the published
         payload -- the per-rung reduction is not, because the curve publishes one figure per rung
         (`net_cost_of_risk = impact * (1 - reduction) + cost`) and two unknowns behind it.
         When they stop agreeing, this goes red instead of the divergence staying silent.
    """
    sys.path.insert(0, os.path.join(estate, "platform", "graded"))
    try:
        import cage                                              # noqa: PLC0415
    except ImportError as exc:                                   # noqa: BLE001
        out("SKIP", f"platform/graded/cage.py could not be imported ({exc}), so the reduction set "
                    f"the twin entries were priced with cannot be read")
        return
    for name, doc in sorted(parties.items()):
        feed = _forward_intel_feed(estate, name, doc)
        ev = os.path.join(estate, name, "composed", "evidence.json")
        if not (feed and os.path.exists(ev)):
            continue
        try:
            with open(feed) as fh:
                payload = json.load(fh)["payload"]
            with open(ev) as fh:
                twins = [e for e in (json.load(fh).get("prices") or []) if e.get("source") == "twin"]
        except (OSError, ValueError, KeyError) as exc:           # noqa: BLE001
            out("FAIL", f"{name}: could not read its published curve or its twin entry: {exc}")
            continue
        if not twins:
            continue                     # check 3 already graded the missing twin edge
        unnamed = [e for e in twins if not e.get("residual_basis")]
        out("FAIL" if unnamed else "PASS",
            f"{name}: the twin entry names the reduction set its residuals came from"
            + (" -- it does not, so a reader attributes them to the adopter's own published curve"
               if unnamed else f" ({twins[0]['residual_basis']})"))

        curve = {str(c.get("account")): c.get("net_cost_of_risk") for c in payload.get("curve") or []}
        lm = payload.get("lm") or []
        if len(lm) != 3 or not curve:
            out("SKIP", f"{name}: its feed carries no lm triple or no curve, so the table and the "
                        f"curve cannot be compared on the same shock")
            continue
        impact = float(lm[1])            # the mode, the same figure the emitter builds the curve from
        table = {t: impact * (1 - cage.TIERS[t]["reduce"]) + cage.TIERS[t]["cost"]
                 for t in curve if t in cage.TIERS}
        if len(table) != len(curve):
            out("FAIL", f"{name}: its curve prices rungs the table does not: "
                        f"{sorted(set(curve) - set(table))}")
            continue
        cheapest_table = min(table, key=lambda t: table[t])
        cheapest_curve = min(curve, key=lambda t: float(curve[t]))
        spread = max(abs(float(curve[t]) - table[t]) for t in table)
        out("FAIL" if cheapest_table != cheapest_curve else "PASS",
            f"{name}: platform's tier table and {name}'s own graded curve still pick the same "
            f"rung as cheapest on the same shock ({cheapest_table}); they differ by up to "
            f"{spread:,.0f} on the rungs themselves, which is why the entry names which set "
            f"priced it"
            + ("" if cheapest_table == cheapest_curve else
               f" -- the table says {cheapest_table} and the adopter's own evidence says "
               f"{cheapest_curve}, so the tier the entry attributes to the curve is not the tier "
               f"the curve would pick"))


def check_engine_agreement(estate, parties):
    """The two engines must pick the SAME rung, to the boundary.

    ADR-0021 says a versioned selection-policy package the adopter publishes turns the curve
    into one tier, while `platform/graded/cage.py` is the engine actually wired to `prices[]`
    and the proposer. Two implementations of one rule is a standing invitation to drift, and a
    proposal PR that names a policy version which did not in fact pick is exactly the
    unfalsifiable claim this estate refuses. So: run both over the SAME residuals, at each
    tier's exact band boundary as well as either side of it, with and without the party's own
    declared floor, and refuse any disagreement.
    """
    graded = os.path.join(estate, "platform", "graded")
    if not os.path.exists(os.path.join(graded, "cage.py")):
        out("SKIP", "no platform/graded/cage.py in the estate: cannot compare the two engines")
        return
    for d in (graded, os.path.join(estate, "platform", "risk")):
        if d not in sys.path:
            sys.path.insert(0, d)
    try:
        import cage                                              # noqa: PLC0415
    except Exception as exc:                                     # noqa: BLE001
        out("SKIP", f"could not import platform/graded/cage.py: {exc}")
        return

    compared = 0
    for name, doc in sorted(parties.items()):
        pkg = os.path.join(estate, name, POLICY_PACKAGE, "selection_policy.py")
        tol = (doc.get("appetite") or {}).get("tolerance")
        if not (isinstance(tol, dict) and "amount" in tol):
            continue                                  # not a risk-bearing party
        if not os.path.exists(pkg):
            # Absence is graded, never silent. A party whose own evidence
            # attributes a tier to a policy version, with no package on disk
            # that could have made it, is observed FALSE (ADR-0021). One that
            # selects nothing through a package has no second engine to drift
            # from, and says so. Either way the wrapper's claim is not earned
            # by a party nobody looked at.
            names = _policy_versions_named(estate, name)
            if names:
                out("FAIL", f"{name}'s composed evidence attributes a tier to selection policy "
                            f"{sorted(names)} but {name} ships no {POLICY_PACKAGE}/"
                            f"selection_policy.py that could have made it (ADR-0021)")
            elif _forward_intel_feed(estate, name, doc):
                out("FAIL", f"{name} publishes a forward-intel feed but ships no "
                            f"{POLICY_PACKAGE}/selection_policy.py, so no versioned rule can "
                            f"turn its curve into a tier (ADR-0021)")
            else:
                out("PASS", f"{name} selects no tier through a {POLICY_PACKAGE} package and its "
                            f"evidence attributes none, so there is no second engine to drift "
                            f"from (named absence, not a silent skip)")
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"_sp_sel_{name}", pkg)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:                                 # noqa: BLE001
            out("FAIL", f"{name}: its own {POLICY_PACKAGE} package does not import: {exc}")
            continue
        limit, cur = float(tol["amount"]), str(tol["currency"])
        floor = (doc.get("overlay") or {}).get("floor")
        # One ALE per tier that lands that tier's residual EXACTLY on the band, plus a nudge
        # either side of each -- the boundary is where a `<` and a `<=` part company.
        ales = []
        for tier in cage.ORDER:
            reduce = cage.TIERS[tier]["reduce"]
            if reduce >= 1.0:
                continue
            exact = limit / (1.0 - reduce)
            ales += [exact * 0.999999, exact, exact * 1.000001]
        # Every rung is tried as a floor, not just the one this party declares today (it
        # declares none), so the tighten-only clamp is exercised either way.
        floors = [None] + [f for f in [floor] + list(cage.ORDER) if f is not None]
        floors = list(dict.fromkeys(floors))
        disagreements = []
        for f in floors:
            for ale in ales:
                residuals = {t: {"amount": cage.caged_residual(ale, t), "currency": cur}
                             for t in cage.ORDER}
                theirs = mod.select(residuals, {"amount": limit, "currency": cur}, f)["tier"]
                ours = cage.select_tier(ale, limit, f)
                if theirs != ours:
                    disagreements.append((f, ale, ours, theirs))
        if disagreements:
            f, ale, ours, theirs = disagreements[0]
            out("FAIL", f"{name}: the two selection engines disagree on {len(disagreements)} of "
                        f"{len(ales) * len(floors)} priced cases — at an uncaged ALE of {ale:,.2f} {cur} "
                        f"with floor {f!r}, platform/graded/cage.py picks {ours!r} and {name}'s "
                        f"own {POLICY_PACKAGE} package picks {theirs!r} (ADR-0021)")
        else:
            compared += 1
            out("PASS", f"{name}: platform/graded/cage.py and {name}'s own {POLICY_PACKAGE} "
                        f"package pick the same rung in all {len(ales) * len(floors)} cases, band "
                        f"boundaries and every rung tried as a floor (it declares {floor!r})")
    if not compared:
        # The wrapper's PASS sentence asserts the two engines agree. With
        # nothing compared it would be asserting it of no one.
        out("SKIP", "no party in this estate was compared across the two selection engines, so "
                    "nothing here observed that they agree")


def check_agent_cage(estate, parties, adopters):
    """Eco-system ticket 145 (ADR-0031 decisions 5 and 6), on each adopter's committed
    evidence: the twin agent's rung is what the adopter's OWN selection-policy package picks
    over the residuals the line carries and the party's own signed band and floor (the
    two-implementations guard, as leg 9 applies it to the pod line); and platform's own
    tier fold, run over the document with and without the line, moves the Namespace tier
    not at all. An adopter whose evidence carries no such line was composed under a platform
    tag that predates the kind: a NAMED could-not-look naming the pin, never a FAIL against
    an adopter that has done nothing wrong, and never a PASS."""
    wargamer_dir = os.path.join(estate, "platform", "wargamer")
    if wargamer_dir not in sys.path:
        sys.path.insert(0, wargamer_dir)
    try:
        import wargamer                                          # noqa: PLC0415
    except Exception as exc:                                     # noqa: BLE001
        wargamer, fold_why = None, f"platform/wargamer/wargamer.py could not be imported ({exc})"
    else:
        fold_why = None
    for name in adopters:
        ev = os.path.join(estate, name, "composed", "evidence.json")
        if not os.path.exists(ev):
            continue                                  # run() names the missing document
        try:
            with open(ev) as fh:
                prices = json.load(fh).get("prices") or []
        except (OSError, ValueError):
            continue                                  # run() names the unreadable document
        agents = [e for e in prices if e.get("kind") == AGENT_CAGE_KIND]
        if not agents:
            pin = _platform_pin(estate, name)
            out("SKIP", f"{name}'s evidence carries no `agent-cage` line: it was composed under "
                        f"platform {pin or 'an unrecorded pin'}, which predates the kind "
                        f"(eco-system ticket 145). It waits on the owner's next signed platform "
                        f"tag and on this adopter's pin moving to it; nothing here may be "
                        f"re-rendered from an untagged branch")
            continue
        e = agents[0]
        if amount_of(e) is None or e.get("proposed_tier") not in LADDER:
            continue                                  # leg 1 printed the named SKIP; leg 3b the shape
        doc = parties.get(name) or {}
        tol = (doc.get("appetite") or {}).get("tolerance")
        floor = (doc.get("overlay") or {}).get("floor")
        pkg = os.path.join(estate, name, POLICY_PACKAGE, "selection_policy.py")
        if not (isinstance(tol, dict) and "amount" in tol) or not os.path.exists(pkg):
            out("FAIL", f"{name}: its agent-cage line names selection policy "
                        f"{e.get('policy_version')!r} but the party signs no appetite.tolerance or "
                        f"ships no {POLICY_PACKAGE}/selection_policy.py that could have picked "
                        f"(ADR-0021)")
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"_sp_agent_{name}", pkg)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            candidates = {r: {"amount": v, "currency": e.get("currency")}
                          for r, v in (e.get("residuals") or {}).items() if v is not None}
            theirs = mod.select(candidates, {"amount": float(tol["amount"]),
                                             "currency": str(tol["currency"])}, floor)["tier"]
        except Exception as exc:                                 # noqa: BLE001
            out("FAIL", f"{name}: its own {POLICY_PACKAGE} package could not re-pick the twin-agent "
                        f"rung from the line's residuals: {exc}")
            continue
        if theirs != e["proposed_tier"]:
            out("FAIL", f"{name}: the agent-cage line proposes {e['proposed_tier']!r} but {name}'s own "
                        f"{POLICY_PACKAGE} package picks {theirs!r} over the same residuals and band "
                        f"(ADR-0021: the package named is the package that picked)")
            continue
        if wargamer is None:
            out("SKIP", f"{name}: the twin-agent rung re-derives ({theirs!r}), but whether it folds "
                        f"into the Namespace could not be looked at: {fold_why}")
            continue
        try:
            with_line = wargamer.select_party_tier(prices, current=None, floor=floor)
            without = wargamer.select_party_tier([p for p in prices if p is not e],
                                                 current=None, floor=floor)
        except ValueError as exc:
            out("FAIL", f"{name}: platform's tier fold refused this document: {exc}")
            continue
        if (with_line["tier"], with_line["lines"]) != (without["tier"], without["lines"]):
            out("FAIL", f"{name}: the agent-cage line moves the Namespace fold from "
                        f"{without['tier']!r} to {with_line['tier']!r}; a rung for the twin agent "
                        f"never folds into a Namespace (ADR-0031 decision 6)")
            continue
        out("PASS", f"{name}: the twin-agent rung {theirs!r} is what {name}'s own {POLICY_PACKAGE} "
                    f"package picks over the line's residuals and its signed band (floor "
                    f"{floor!r}), and platform's tier fold gives the Namespace {without['tier']!r} "
                    f"with the line and without it")


def _policy_versions_named(estate, name):
    """The selection-policy versions this party's composed evidence attributes a tier to."""
    ev = os.path.join(estate, name, "composed", "evidence.json")
    if not os.path.exists(ev):
        return set()
    try:
        with open(ev) as fh:
            return {v for v in _walk_key(json.load(fh), "policy_version")}
    except (OSError, ValueError):
        return set()


def check_fx_bridge(estate):
    """The FX seam is two repos: `feeds` publishes the signed monthly rates and ships the
    converter beside them; `platform/compose/composition.py` calls it when a price is not
    already in the perspective's reporting currency. Every party in this estate reports in GBP
    and prices in GBP today, so the bridge NEVER runs in a real composition -- which is exactly
    how it would rot unnoticed until the first non-GBP party arrives. So it is exercised here,
    directly, against the real published feed: a date the feed publishes gives the published
    rate, and a date it does not refuses as a missing instrument (ADR-0020), never zero and
    never last month's number."""
    comp = os.path.join(estate, "platform", "compose", "composition.py")
    conv = os.path.join(estate, "feeds", "converters", "fx.py")
    published = sorted(glob.glob(os.path.join(estate, "feeds", "fx", "v*", "feed.json")))
    if not (os.path.exists(comp) and os.path.exists(conv) and published):
        out("SKIP", "no fx feed, converter or composition.py in the estate: no FX bridge to look at")
        return
    try:
        with open(published[-1]) as fh:
            payload = json.load(fh)["payload"]
        month, base, rates = payload["period"], payload["base"], payload["rates"]
        quote = sorted(rates)[0]
        spec = importlib.util.spec_from_file_location("_composition_fx", comp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # The converter is resolved from a PINNED parent tree only, so the tree
        # is named here the same way a composition names it.
        trees = {"feeds": os.path.join(estate, "feeds")}
        rate, provenance = mod._fx_rate(base, quote, f"{month}-15", trees)
    except Exception as exc:                                     # noqa: BLE001
        out("FAIL", f"the FX bridge does not resolve a rate the fx feed publishes: {exc}")
        return
    if abs(rate - float(rates[quote])) > 1e-9:
        out("FAIL", f"composition resolves {base}->{quote} on {month}-15 as {rate}, but the "
                    f"signed fx feed publishes {rates[quote]} — the estate is not reading the "
                    f"rate the publisher signed")
    elif not provenance.get("fx_feed_version"):
        out("FAIL", f"the FX bridge resolved {base}->{quote} at {rate} but recorded no "
                    f"fx_feed_version, so a converted price could not be re-derived from the "
                    f"signed parent set: {provenance!r}")
    else:
        out("PASS", f"the FX bridge reads the publisher's own converter: {base}->{quote} on "
                    f"{month}-15 is {rate}, the rate the signed fx feed publishes, recorded "
                    f"against {provenance['fx_publisher']}'s fx feed "
                    f"{provenance['fx_feed_version']}")
    unpublished = f"{int(month[:4]) - 1}-{month[5:7]}-15"
    try:
        mod._fx_rate(base, quote, unpublished, trees)
    except Exception as exc:                                     # noqa: BLE001
        detail = str(exc).lower()
        if "missing instrument" in detail:
            out("PASS", f"a date the fx feed does not publish ({unpublished}) refuses as a "
                        f"missing instrument, and prices nothing (ADR-0020)")
        else:
            out("FAIL", f"an unpublished FX date refused, but not as a missing instrument: {exc}")
    else:
        out("FAIL", f"the FX bridge returned a rate for {unpublished}, which the fx feed does "
                    f"not publish — a widened, zeroed or stale rate is the live bug ADR-0020 "
                    f"was written against")


def _forward_intel_feed(estate, name, doc):
    """The path the party's own publishes[] gives for its forward-intel feed, highest major."""
    rec = next((r for r in (doc.get("publishes") or []) if r.get("name") == "forward-intel"), None)
    if not rec:
        return None
    found = sorted(glob.glob(os.path.join(estate, name, str(rec.get("path", "")), "v*", "feed.json")))
    return found[-1] if found else None



# --------------------------------------------------------------------------
# 11. what the number IS, and the aggregate beside the band
#     (eco-system ticket 79 items 9 and 10; ticket 75 Q4 (a))
# --------------------------------------------------------------------------

ORDINAL_STATEMENT = ("an ordinal, auditable comparison under one perspective; not an expected "
                      "annual loss")
# What the probe below hands the composer, and therefore what the composer must
# come back with: two lines at 100.00 and 200.00 GBP, both at tier `baseline`,
# which platform/graded/cage.py leaves 0.70 of. 0.70 x 300.00 = 210.00, against
# a 1.00 GBP band, so it breaches (review N1).
PROBE_TOTAL = 210.0


def check_ordinal_and_aggregate(estate, adopters):
    """Ticket 75 Q4 answered (a): the GBP is an ordinal, auditable comparison
    instrument under one perspective, and EVERY ARTEFACT THAT SHOWS A TOTAL SAYS
    SO. And ticket 79 item 9: `appetite.tolerance` is ONE annual aggregate, so
    the sum of what the selected tiers leave belongs beside it, because lines
    that each fit the band can breach it together.

    WHAT THIS READS, and what it therefore may say. The served artefact is
    `<adopter>/composed/HEADER.yaml` on the adopter's own checkout -- the file
    the adopter's own tag signs and the insurer prices a layer from. Both
    sentences are written by the COMPOSER (platform/compose/composition.py
    `exposure_section`), so an adopter carries them only from the first
    composition run under a platform tag that has them. Until then this is a
    NAMED could-not-look that says which tag it waits for -- never a pass, and
    never a FAIL against an adopter that has done nothing wrong.
    """
    # REVIEW F9. The first cut set this by substring-matching `ORDINAL_STATEMENT`
    # and `def aggregate_section` in the composer's SOURCE and then claimed
    # BEHAVIOUR -- a comment naming either would have satisfied it. It now IMPORTS
    # the composer and RUNS `exposure_section` over a two-line synthetic book,
    # then reads the two keys off what comes back. That is the property the line
    # asserts, derived rather than inferred. An import that fails, or a composer
    # too old to have the function at all, is a named could-not-look.
    composer = os.path.join(estate, "platform", "compose", "composition.py")
    composer_has_it, why = False, "no platform/compose/composition.py in this estate checkout"
    if os.path.exists(composer):
        try:
            spec = importlib.util.spec_from_file_location("t79_composition", composer)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["t79_composition"] = mod
            spec.loader.exec_module(mod)
            probe = [{"source": "p", "kind": "feed", "name": "a", "perspective": "x",
                      "currency": "GBP", "amount": 100.0, "proposed_tier": "baseline"},
                     {"source": "p", "kind": "feed", "name": "b", "perspective": "x",
                      "currency": "GBP", "amount": 200.0, "proposed_tier": "baseline"}]
            # REVIEW N1: THE PROBE KNOWS THE ANSWER, SO IT ASSERTS IT. Two lines
            # at 100.00 and 200.00, both at `baseline`, against a 1.00 GBP band:
            # cage.py's baseline leaves 0.70 of each, so the aggregate is
            # 210.00 and it breaches. Testing only that `ordinal` is non-empty
            # and that the aggregate carries A total let a seven-line stub
            # returning {"ordinal": "not the real sentence", "aggregate":
            # {"selected_tier_residual_total": 0.0, "breaches_band": False}}
            # print PASS -- a check that claims the composer works while the
            # composer computes nothing.
            got = mod.exposure_section(probe, "x", {"amount": 1.0, "currency": "GBP"}, "GBP")
            agg = got.get("aggregate") if isinstance(got, dict) else None
            if not isinstance(got, dict):
                why = "exposure_section returned nothing for a two-line synthetic book"
            elif not (got.get("ordinal") or "").strip():
                why = "exposure_section returned a total and no `ordinal` statement"
            elif (got.get("ordinal") or "").strip() != ORDINAL_STATEMENT:
                why = (f"exposure_section returned {got['ordinal']!r} as its `ordinal` statement, "
                       f"and the sentence ticket 75 Q4 (a) settled is {ORDINAL_STATEMENT!r}")
            elif not isinstance(agg, dict):
                why = "exposure_section returned a total and no `aggregate` section"
            elif agg.get("selected_tier_residual_total") is None:
                why = "the `aggregate` it returned carries no selected_tier_residual_total"
            elif abs(float(agg["selected_tier_residual_total"]) - PROBE_TOTAL) > 1e-6:
                why = (f"the probe hands over 100.00 + 200.00 GBP at tier `baseline`, whose "
                       f"aggregate is {PROBE_TOTAL:.2f}, and exposure_section returned "
                       f"{float(agg['selected_tier_residual_total']):.2f}")
            elif agg.get("breaches_band") is not True:
                why = (f"the probe's {PROBE_TOTAL:.2f} GBP aggregate is measured against a 1.00 "
                       f"GBP band, which it plainly breaches, and exposure_section returned "
                       f"breaches_band={agg.get('breaches_band')!r}")
            else:
                composer_has_it = True
                probe_total = agg["selected_tier_residual_total"]
                probe_breach = agg["breaches_band"]
        except Exception as exc:                       # noqa: BLE001 -- any import/run failure
            why = f"{type(exc).__name__}: {exc}"
    if not composer_has_it:
        # A NAMED could-not-look, not a FAIL. Nothing an adopter did is wrong: the
        # composer in THIS estate checkout cannot produce either sentence, so
        # grading the adopters for carrying them would be grading them against a
        # thing that does not exist. The hard assertion lives where the composer
        # IS the served artefact -- platform's own compose/composition.py
        # --selfcheck, which refuses an exposure section with no `ordinal` and no
        # `aggregate` by name.
        out("SKIP", f"the composer in this estate checkout ({composer}) does not return an "
                    f"exposure section carrying both an `ordinal` statement and an `aggregate` "
                    f"when it is RUN over a synthetic two-line book -- {why} -- so no adopter "
                    f"here can carry either by composing and this check cannot look at whether "
                    f"they do. "
                    f"Graded in platform's own compose/composition.py --selfcheck; this leg "
                    f"reads green once the estate clone carries a composer that has them "
                    f"(eco-system ticket 79 items 9 and 10)")
        return
    out("PASS", f"the composer was RUN, not read: exposure_section over a synthetic two-line "
                f"book (100.00 + 200.00 GBP, both at tier `baseline`, against a 1.00 GBP band) "
                f"came back with the exact sentence ticket 75 Q4 (a) settled and the aggregate "
                f"that book has to produce -- {probe_total:.2f} GBP, breaches_band="
                f"{probe_breach!r} -- not merely with a non-empty string and some number")

    for name in adopters:
        header = os.path.join(estate, name, "composed", "HEADER.yaml")
        if not os.path.exists(header):
            out("SKIP", f"{name} has no composed/HEADER.yaml, so no total of its is served and "
                        f"there is nothing to grade for the ordinal statement")
            continue
        try:
            doc = load_yaml(header) or {}
        except Exception as exc:                       # noqa: BLE001 -- any parse failure
            out("FAIL", f"{name}: composed/HEADER.yaml does not parse: {exc}")
            continue
        exposure = doc.get("exposure")
        if not isinstance(exposure, dict) or exposure.get("total") is None:
            out("PASS", f"{name} serves no exposure total, so nothing of its states a number "
                        f"that would need the sentence (a named absence)")
            continue
        total, currency = exposure["total"], exposure.get("currency")
        pin = _platform_pin(estate, name)
        # REVIEW F13. A REWORDED sentence is not an ABSENT one, and saying
        # "carrying no `ordinal`" of an artefact that carries a different one is
        # the same class of wrong sentence this leg exists to catch.
        missing, different = [], []
        served_ordinal = (exposure.get("ordinal") or "").strip()
        if not served_ordinal:
            missing.append("`ordinal`")
        elif served_ordinal != ORDINAL_STATEMENT:
            different.append(f"`ordinal` reads {served_ordinal!r}, and the sentence ticket 75 "
                             f"Q4 (a) settled is {ORDINAL_STATEMENT!r}")
        if not isinstance(exposure.get("aggregate"), dict):
            missing.append("`aggregate`")
        if different:
            out("FAIL", f"{name} serves a total of {total:,.2f} {currency} whose statement of "
                        f"what the number is has been REWORDED, not omitted: "
                        f"{'; '.join(different)}. The composer writes one sentence; an adopter "
                        f"serving another one has had it edited after composition")
            continue
        if not missing:
            agg = exposure["aggregate"]
            out("PASS", f"{name} serves a total of {total:,.2f} {currency} that says what it "
                        f"is -- {ORDINAL_STATEMENT} -- with the aggregate of its selected-tier "
                        f"residuals ({agg.get('selected_tier_residual_total')}) beside a "
                        f"tolerance of {agg.get('tolerance')}")
            continue
        out("SKIP", f"{name} serves a total of {total:,.2f} {currency} carrying no "
                    f"{' and no '.join(missing)}: composition.py writes both, and this adopter "
                    f"was composed under platform {pin or 'an unrecorded pin'}, which predates "
                    f"them. It waits on the owner's next signed platform tag and on this "
                    f"adopter's pin moving to it; nothing here may be re-rendered from an "
                    f"untagged branch (eco-system ticket 79 items 9 and 10)")


def _platform_pin(estate, name):
    """The platform version this adopter's own party.yaml pins, for naming the
    tag a could-not-look waits on. None where it pins none."""
    try:
        doc = load_yaml(os.path.join(estate, name, "party.yaml")) or {}
    except Exception:                                   # noqa: BLE001
        return None
    for edge in doc.get("inherits") or []:
        if edge.get("party") == "platform" and edge.get("kind") == "implementations":
            return f"v{edge.get('version')}"
    return None


def run(estate):
    parties = _parties(estate)
    if not parties:
        out("FAIL", f"no party.yaml anywhere under {estate} — an empty estate is not a pass")
        return
    check_appetite(estate, parties)
    check_curve_agreement(estate, parties)
    check_residual_basis(estate, parties)
    check_engine_agreement(estate, parties)
    check_fx_bridge(estate)
    customers = {n: ((d.get("size") or {}).get("customers")) for n, d in parties.items()}
    adopters = [n for n, d in sorted(parties.items()) if "adopter" in (d.get("roles") or [])]
    if not adopters:
        out("FAIL", f"no adopter party in {estate}")
    check_ordinal_and_aggregate(estate, adopters)
    check_agent_cage(estate, parties, adopters)
    for name in adopters:
        ev = os.path.join(estate, name, "composed", "evidence.json")
        if not os.path.exists(ev):
            out("SKIP", f"{name} has no composed/evidence.json — nothing composed to grade")
            continue
        try:
            with open(ev) as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as exc:
            out("FAIL", f"{name}: composed/evidence.json does not parse: {exc}")
            continue
        version, source = _policy_version(estate, name)
        publishes = parties[name].get("publishes") or []
        check_doc(doc, {
            "regime_weights": _regime_weights(estate, parties, parties[name]),
            "adopter": name,
            "parties": set(parties),
            "customers": customers,
            "forward_intel": any(p.get("name") == "forward-intel" for p in publishes),
            "policy_version": version,
            "policy_version_source": source,
        })


def exit_code():
    if "FAIL" in LINES:
        return 1
    return 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
# selfcheck — planted defects, each of which must be observed false
# --------------------------------------------------------------------------
def _good():
    doc = {
        "outcome": "composed",
        "prices": [
            {"source": "ico", "kind": "feed", "name": "penalty-schema",
             "perspective": "driftwood", "currency": "GBP", "amount": 300.0,
             "per_customer": {"amount": 3.0, "currency": "GBP"}, "total": 300.0,
             "holes": [{"source": "nist", "id": "ac-6", "weight": 0.6, "amount": 200.0},
                       {"source": "nist", "id": "cm-6", "weight": 0.4, "amount": 100.0}]},
            {"source": "twin", "kind": "twin", "perspective": "driftwood", "currency": "GBP",
             "amount": 50.0, "per_customer": {"amount": 0.5, "currency": "GBP"},
             "policy_version": "1.0.0", "curve_hash": "deadbeefcafe", "tail": "bounded-pert"},
        ],
    }
    ctx = {"adopter": "driftwood", "parties": {"driftwood", "ico", "nist", "platform"},
           "customers": {"driftwood": 100}, "forward_intel": True,
           "regime_weights": {"version": "v3", "available": True},
           "policy_version": "1.0.0", "policy_version_source": "driftwood/selection-policy/VERSION"}
    return doc, ctx


def _switching(source, amount, could_not_look=None):
    """A `kind: switching` price shaped as composition.py writes one (eco-system ticket 127)."""
    return {"source": source, "kind": "switching", "name": "penalty-schema",
            "perspective": "driftwood", "currency": "GBP", "amount": amount,
            "per_customer": (None if amount is None
                             else {"amount": amount / 100, "currency": "GBP"}),
            "version": "v3", "could_not_look": could_not_look, "alternates": [],
            "basis": "re-composed with this publisher's feed edges dropped"}


def _supersede(source, amount):
    """A `kind: supersede` price shaped as composition.py writes one (eco-system ticket 128)."""
    return {"source": source, "kind": "supersede", "name": "penalty-schema",
            "perspective": "driftwood", "currency": "GBP", "amount": amount,
            "per_customer": {"amount": amount / 100, "currency": "GBP"}, "version": "v3",
            "newer": {"version": "v4", "tag": "v4.0.0"}, "ramp": 1.0, "base": 300.0}


def _grade(doc, ctx, label, want_fail, want_skip=False):
    LINES.clear()
    check_doc(doc, ctx)
    failed = "FAIL" in LINES
    assert failed == want_fail, f"{label}: expected {'FAIL' if want_fail else 'no FAIL'}, got {LINES}"
    if want_skip:
        assert "SKIP" in LINES, f"{label}: expected a SKIP, got {LINES}"
    print(f"ok  {label}")


def selfcheck():
    doc, ctx = _good()
    _grade(doc, ctx, "a well-formed priced document passes", False)

    doc, ctx = _good()
    doc["prices"][1]["currency"] = "USD"
    doc["prices"][1]["per_customer"]["currency"] = "USD"
    _grade(doc, ctx, "a mixed-currency prices[] fails", True)

    doc, ctx = _good()
    doc["prices"][1]["perspective"] = "insurer"
    doc["prices"][1]["per_customer"] = None
    ctx["parties"] = ctx["parties"] | {"insurer"}
    _grade(doc, ctx, "a prices[] spanning two perspectives fails", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"][1]["amount"] = 90.0
    _grade(doc, ctx, "a hole total that does not add up fails", True)

    doc, ctx = _good()
    del doc["prices"][1]["policy_version"]
    _grade(doc, ctx, "a twin entry with no policy_version fails", True)

    doc, ctx = _good()
    del doc["prices"][1]["curve_hash"]
    _grade(doc, ctx, "a twin entry with no curve_hash fails", True)

    doc, ctx = _good()
    del doc["prices"][0]["per_customer"]
    _grade(doc, ctx, "a price with no per-customer restatement fails", True)

    doc, ctx = _good()
    doc["prices"][0]["per_customer"]["amount"] = 2.5
    _grade(doc, ctx, "a per-customer restatement that is not amount/customers fails", True)

    doc, ctx = _good()
    ctx["customers"] = {"driftwood": None}
    _grade(doc, ctx, "a per-customer restatement with no signed customer count fails", True)

    doc, ctx = _good()
    doc["prices"][0].pop("holes")
    _grade(doc, ctx, "a regime entry with no hole breakdown fails", True)

    doc, ctx = _good()
    ctx["forward_intel"] = False
    _grade(doc, ctx, "a twin price with no published forward-intel feed fails", True)

    doc, ctx = _good()
    doc["prices"] = [doc["prices"][0]]
    ctx["forward_intel"] = False
    _grade(doc, ctx, "no twin entry and no forward-intel feed is a named pass", False)

    doc, ctx = _good()
    ctx["policy_version"] = "2.0.0"
    _grade(doc, ctx, "a selection policy version the package does not publish fails", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"] = []
    doc["prices"][0]["total"] = None
    _grade(doc, ctx, "no holes against a version that publishes weights fails", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"] = []
    doc["prices"][0]["total"] = None
    ctx["regime_weights"] = {"version": "v1", "available": False}
    _grade(doc, ctx, "no holes against a version publishing no weights is a graded SKIP, "
                     "not a pass", False, want_skip=True)

    doc, ctx = _good()
    # A publisher typo that halves the published shares: the holes still add up to the
    # total, and the total is still the entry's amount, but half the exposure vanished.
    for h in doc["prices"][0]["holes"]:
        h["weight"] /= 2
        h["amount"] /= 2
    doc["prices"][0]["total"] = 150.0
    doc["prices"][0]["amount"] = 150.0
    doc["prices"][0]["per_customer"]["amount"] = 1.5
    _grade(doc, ctx, "a hole partition whose weights do not sum to 1.0 fails", True)

    doc, ctx = _good()
    doc["prices"][0]["new_price"] = 600.0
    _grade(doc, ctx, "an entry whose partition contradicts its own new_price fails", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"][0]["status"] = "covered"
    doc["prices"][0]["amount"] = 100.0
    doc["prices"][0]["per_customer"]["amount"] = 1.0
    _grade(doc, ctx, "an implemented line comes off the entry and the rest prices it", False)

    doc, ctx = _good()
    doc["prices"][0]["holes"][0]["status"] = "covered"
    _grade(doc, ctx, "an entry that still charges an implemented line fails (ticket 121)", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"][0]["status"] = "unselected"
    _grade(doc, ctx, "an unselected line stays on the price", False)

    doc, ctx = _good()
    doc["prices"][1]["perspective"] = "ico"
    doc["prices"][1]["per_customer"] = None
    _grade(doc, ctx, "a twin entry priced under another party's perspective fails", True)

    doc, ctx = _good()
    doc["prices"] = []
    _grade(doc, ctx, "an empty prices[] is not a pass", True)

    # Eco-system ticket 127: check 4 selects the regime entry by kind. ico also prices a
    # switching line (what dropping its feed edges would save) and, from ticket 128, a
    # supersede line (the surcharge for sitting behind a newer major). Neither is a regime
    # entry and neither carries holes[]; each is graded by what its kind says it is.
    doc, ctx = _good()
    doc["prices"].append(_switching("ico", 300.0))
    _grade(doc, ctx, "an ico switching price is not read as a regime entry", False)

    doc, ctx = _good()
    doc["prices"].append(_supersede("ico", 0.0))
    _grade(doc, ctx, "an ico supersede price is not read as a regime entry", False)

    doc, ctx = _good()
    doc["prices"][0].pop("holes")
    doc["prices"].append(_switching("ico", 300.0))
    _grade(doc, ctx, "the ico feed entry still owes holes[] beside a switching price", True)

    # A price the composer could not size carries no amount and names why. That is a named
    # could-not-look: never a FAIL, and never a PASS either.
    doc, ctx = _good()
    _grade(doc, ctx, "baseline for the could-not-look count", False)
    base_pass, base_skip = LINES.count("PASS"), LINES.count("SKIP")
    doc["prices"].append(_switching("feeds", None, could_not_look=(
        "missing instrument: twin/forward-intel/v1/feed.json supplies no lef")))
    _grade(doc, ctx, "a price with no amount and a named could_not_look is a SKIP", False,
           want_skip=True)
    assert LINES.count("PASS") == base_pass and LINES.count("SKIP") == base_skip + 1, (
        f"a could-not-look must add one SKIP and no PASS, got {LINES}")

    doc, ctx = _good()
    doc["prices"].append(_switching("feeds", None, could_not_look=""))
    _grade(doc, ctx, "a price with no amount and an empty could_not_look fails", True)

    doc, ctx = _good()
    doc["prices"].append(_switching("feeds", None, could_not_look="no lef"))
    doc["prices"][-1]["per_customer"] = {"amount": 1.0, "currency": "GBP"}
    _grade(doc, ctx, "a could-not-look that still restates an amount per customer fails", True)

    doc, ctx = _good()
    doc["prices"].append(_switching("feeds", 10.0, could_not_look="no lef"))
    _grade(doc, ctx, "a price that carries both an amount and a could_not_look fails", True)

    # --- eco-system ticket 145: the twin agent's cage line (leg 3b) ---
    def _agent(**over):
        """An `agent-cage` price shaped as composition.py price_twin_agent writes one, over the
        _good() document's twin line (residuals 100 at baseline, 10 at isolated; selected isolated)."""
        lef = [8e-5, 8e-5, 3e-4]
        lm = 90.0 * 1.0 / 365.25
        amount = (lef[0] + 4 * lef[1] + lef[2]) / 6 * lm
        line = {"source": "platform", "kind": "agent-cage", "subject": "twin-agent", "name": "twin-agent",
                "perspective": "driftwood", "currency": "GBP", "amount": amount,
                "per_customer": {"amount": amount / 100, "currency": "GBP"},
                "proposed_tier": "baseline", "old_tier": "baseline", "changed": False,
                "residual_basis": "platform-twin-agent-table@1.0.0",
                "residuals": {"baseline": amount, "restricted": amount, "quarantine": amount, "isolated": 0.0},
                "reach": {"p1": 1.0, "p2": 1.0, "p3": 0.0, "p4": 0.0},
                "closes": {"baseline": [], "restricted": ["p4"], "quarantine": ["p3", "p4"],
                           "isolated": ["p1", "p2", "p3", "p4"]},
                "scenario": {"gap": 90.0, "loosest_pod_tier": "baseline", "selected_pod_tier": "isolated",
                             "window_days": 1.0, "window_source": "fixture truth.yml cron",
                             "lm": [lm, lm, lm], "annualised_by": "expectation"},
                "lef": lef, "lef_from": "threat-register", "register_version": "v4",
                "policy_version": "1.0.0", "window": {"days": 1.0}}
        line.update(over)
        return line

    def _with_agent(**over):
        doc, ctx = _good()
        doc["prices"][1].update(residuals={"baseline": 100.0, "restricted": 40.0,
                                           "quarantine": 20.0, "isolated": 10.0},
                                proposed_tier="isolated")
        doc["prices"].append(_agent(**over))
        return doc, ctx

    _grade(*_with_agent(), "a priced agent-cage line with a re-derivable gap, magnitude, amount and "
                            "rung passes leg 3b", False)
    doc, ctx = _with_agent()
    doc["prices"].append(_agent())
    _grade(doc, ctx, "two agent-cage lines fail: one cage, one line", True)
    _grade(*_with_agent(subject="namespace"), "an agent-cage line whose subject is not the twin "
                                               "agent fails", True)
    _grade(*_with_agent(source="twin"), "an agent-cage line priced by the twin fails: the twin never "
                                         "prices its own cage", True)
    _grade(*_with_agent(residual_basis="platform-cage-tiers@1.0.0"),
           "an agent-cage line priced under the pod table fails", True)
    _grade(*_with_agent(scenario=dict(_agent()["scenario"], gap=50.0)),
           "a gap that is not the twin line's loosest minus selected residual fails", True)
    _grade(*_with_agent(scenario=dict(_agent()["scenario"], selected_pod_tier="baseline", gap=0.0)),
           "a gap read at a pod rung the twin line did not select fails", True)
    _grade(*_with_agent(scenario=dict(_agent()["scenario"], lm=[1.0, 1.0, 1.0])),
           "a magnitude that is not the gap times the window fails", True)
    _grade(*_with_agent(amount=1.0, per_customer={"amount": 0.01, "currency": "GBP"}),
           "an amount that is not the PERT-mean frequency times the magnitude fails", True)
    _grade(*_with_agent(residuals={"baseline": 1.0, "restricted": 0.5, "quarantine": 0.5, "isolated": 0.0},
                        amount=1.0, per_customer={"amount": 0.01, "currency": "GBP"},
                        scenario=dict(_agent()["scenario"], annualised_by="simulation")),
           "a restricted residual below baseline's fails: a model claim never prices", True)
    _grade(*_with_agent(proposed_tier="paranoid"), "an off-ladder twin-agent rung fails", True)
    _grade(*_with_agent(residuals={"baseline": 1.0}), "residuals that do not cover every rung fail", True)
    _grade(*_with_agent(lef_from="editorial"), "a frequency not from the threat register fails", True)
    _grade(*_with_agent(amount=None, per_customer=None, proposed_tier="baseline",
                        could_not_look="missing instrument: fixture"),
           "an unpriced agent-cage line that still proposes a rung fails", True)
    _grade(*_with_agent(amount=None, per_customer=None, proposed_tier=None,
                        could_not_look="missing instrument: threat-register@v2 publishes no row"),
           "an unpriced agent-cage line naming why is a SKIP, never a FAIL", False, want_skip=True)
    doc, ctx = _with_agent()
    del doc["prices"][-1]["residuals"]
    _grade(doc, ctx, "a priced agent-cage line with no residuals fails: the rung cannot be re-derived", True)

    LINES.clear()
    print("ok  selfcheck: labelling, per-customer, twin edge, hole partition, mixed sums, "
          "policy version and an empty document all graded")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "selfcheck":
        selfcheck()
        sys.exit(0)
    if cmd != "check":
        print(__doc__)
        sys.exit(2)
    if not os.path.isdir(ESTATE):
        print(f"SKIP: {ESTATE} absent — run ./clone-estate.sh first")
        sys.exit(3)
    run(ESTATE)
    sys.exit(exit_code())
