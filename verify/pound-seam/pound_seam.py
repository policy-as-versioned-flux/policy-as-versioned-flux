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
  4. the regime entry's (source: ico) holes[] amounts sum to its total, and the entry's own
     amount equals that total;
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
     refuses an unpublished date as a missing instrument rather than widening it.

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
KINDS = {"feed", "twin", "premium", "switching", "reliability"}
SOURCES = {"ico", "feeds", "twin", "insurer", "platform"}   # plus any party name in the estate
AMOUNT_KEYS = ("amount", "total", "new_price", "old_price")
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
        if amount is None:
            out("FAIL", f"{at}: carries no numeric amount, so nothing can be restated per "
                        f"customer or summed")
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

    # 4: the regime entry's holes partition it
    regimes = [e for e in prices if e.get("source") == "ico"]
    if not regimes:
        out("PASS", f"{who}: declares no ico regime edge, so there is no hole breakdown to "
                    f"check (named absence)")
    for e in regimes:
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
        elif isinstance(priced, (int, float)) and not close(priced, total):
            out("FAIL", f"{at}: the entry prices the regime at {priced} but its holes partition "
                        f"{total} — one entry, two contradictory prices")
        elif (amt := amount_of(e)) is not None and not close(amt, total):
            out("FAIL", f"{at}: amount {amt} is not the hole total {total}")
        else:
            out("PASS", f"{at}: {len(holes)} priced hole(s) sum to its total {total:,.2f} "
                        f"{e.get('currency')}")
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


def run(estate):
    parties = _parties(estate)
    if not parties:
        out("FAIL", f"no party.yaml anywhere under {estate} — an empty estate is not a pass")
        return
    check_appetite(estate, parties)
    check_curve_agreement(estate, parties)
    check_engine_agreement(estate, parties)
    check_fx_bridge(estate)
    customers = {n: ((d.get("size") or {}).get("customers")) for n, d in parties.items()}
    adopters = [n for n, d in sorted(parties.items()) if "adopter" in (d.get("roles") or [])]
    if not adopters:
        out("FAIL", f"no adopter party in {estate}")
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
    doc["prices"][1]["perspective"] = "ico"
    doc["prices"][1]["per_customer"] = None
    _grade(doc, ctx, "a twin entry priced under another party's perspective fails", True)

    doc, ctx = _good()
    doc["prices"] = []
    _grade(doc, ctx, "an empty prices[] is not a pass", True)

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
