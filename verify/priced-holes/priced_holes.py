#!/usr/bin/env python3
"""priced_holes.py — eco-system ticket 38 made checkable: a hole is priced, not counted.

What it observes, on the estate's committed files only:

  1. `platform/compose/composition.py` no longer emits the new-hole, baseline-widening,
     new-ungoverned-namespace or removed-control refusal (the last since eco-system ticket 124,
     ADR-0026 point 5), and the one hole-shaped refusal it still emits is `missing-instrument`
     (a bespoke control with no signed scenario, ADR-0020);
  2. `platform/party/schema.json` admits `overlay.controls` in both the bare and the `party:id`
     form, and its description says an addition is priced, not refused, and no longer says a
     removal refuses;
  3. per adopter, `composed/evidence.json`:
     a. carries `deltas[]` (else it was composed under the refusal shape: a could-not-look, because
        re-composing an adopter is an enactment push only the owner makes);
     b. `refusals[]` carries none of the four deleted kinds;
     c. every `holes[]` entry is keyed `(source, control_id)` with a status, the adopter's own
        perspective and currency, and an amount that is numeric with a `priced_by`, or null with
        none — never a zero nobody priced;
     d. every open `ungoverned[]` entry carries a price whose share is workloads inside over
        workloads across the institution namespaces (re-counted here from the adopter's own
        manifests; since eco-system ticket 119 every Namespace the repo declares or a workload
        names counts, labelled or not, except the substrate the platform declares `infra`, and
        every ungoverned one the recount finds must carry a price), whose ramp is the EOL feed's own ramp from `since` to `as_of` (re-derived
        here; `as_of` is the composer's rule since eco-system ticket 138, the newest of every
        pinned envelope's published_at, read from the adopter's vendored copy first, and every
        edge's own since), whose amount is `min(base, base * share * ramp)` with `base` the header's signed
        exposure total, and whose `since` is the date of the first signed tag whose header names
        the namespace, or names as ungoverned a Namespace a workload now in it has left
        (eco-system ticket 122; re-read here from the adopter clone's tags and tagged trees), or
        null with a named limit; a `since` later than `as_of` holds the ramp at its start and
        must say so in a limit (eco-system ticket 139: a tag date is history, not an input);
     d3. every closed `ungoverned[]` entry says why in `closed_by`, `governed` or `left-repo`, and
        the recount agrees (eco-system ticket 122);
     e. the regime entry's `holes[]` lines each carry the adopter's status for that control, and
        the open ones agree with `holes[]`;
     f. every `deltas[]` entry is one of the ten kinds `DELTA_KINDS` names (the eight hole,
        removal, withdrawal, baseline and namespace kinds, plus ticket 69's two untagged-pin
        kinds), under the adopter's perspective and currency, and the new/closed hole and
        namespace deltas match the entries they report.

Grading, per the gate contract: any FAIL -> 1; else any SKIP -> 3; else 0.

Usage:
    priced_holes.py check        # every adopter in .estate-clone/
    priced_holes.py selfcheck    # planted defects: proves each refusal bites

PAVC_ESTATE_CLONE=<dir> names another estate to grade -- the same override composition.py
takes -- so a scratch estate holding freshly composed adopter copies can be graded before the
owner pushes the real ones. The gate never sets it.
"""
from __future__ import annotations

import datetime
import glob
import json
import os
import re
import subprocess
import sys
from typing import Any

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # type: ignore[import-not-found]  # noqa: E402

LINES: list[str] = []

GONE = {"new-hole", "baseline-widening", "new-ungoverned-namespace", "removed-control"}
# The kinds compute_deltas may print. `new-untagged-pin` and `closed-untagged-pin` are
# ticket 69's: an untagged feed pin is a priced hole on the premium entry, and its moves are
# reported as deltas like every other hole's. This set is a whitelist, so a kind missing from
# it fails the adopter that reports it -- adding a kind here is how a new delta is admitted.
DELTA_KINDS = {"new-hole", "closed-hole", "baseline-widening",
               "removed-control", "baseline-narrowing", "withdrawn-control",
               "new-ungoverned-namespace", "closed-ungoverned-namespace",
               "new-untagged-pin", "closed-untagged-pin"}
HOLE_STATUS = {"new", "recorded", "closed"}
# `withdrawn` is eco-system ticket 123's: the weight names a control its pinned catalogue
# no longer defines, the feed's own fact to fix in its next version.
REGIME_STATUS = HOLE_STATUS | {"covered", "withdrawn", "unselected"}
HOLE_FIELDS = {"source", "control_id", "status", "perspective", "currency", "amount", "priced_by"}
PRICE_FIELDS = {"perspective", "currency", "amount", "share", "workloads", "workloads_total",
                "base", "ramp", "since", "as_of", "bounded", "limits"}
WORKLOAD_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}
INSTITUTION_LABEL = "policy-as-versioned.dev/institution"
GOVERNED_LABEL = "policy-as-versioned.dev/governed"
TIER_LABEL = "posture.acme.io/tier"
HEADER_COMMENT_LINE = "# advisory header -- policy-as-versioned.dev/composed"
RAMP_CAP_YEARS = 4.0


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


def close(a: float, b: float) -> bool:
    return abs(a - b) <= max(1e-6, 1e-9 * max(abs(a), abs(b)))


# --------------------------------------------------------------------------
# the arithmetic, re-derived here so the check does not trust the producer
# --------------------------------------------------------------------------
def expected_ramp(since: str | None, as_of: str | None) -> float:
    """The EOL feed's own ramp (platform/feeds/to_fair_scenario.py:eol_ramp): 1.0 up to
    `since`, then +1x per year past it, capped at +4x. 1.0 where either date is unknown.
    An `as_of` before `since` holds the ramp at its value on the since day (eco-system ticket
    139): the window is read as `since` to `max(since, as_of)`, never backwards."""
    if not since or not as_of:
        return 1.0
    as_of = max(since, as_of)
    days = (datetime.date.fromisoformat(as_of) - datetime.date.fromisoformat(since)).days
    if days <= 0:
        return 1.0
    return 1.0 + min(days / 365.0, RAMP_CAP_YEARS)


def expected_amount(base: float | None, workloads: int, total: int, ramp: float
                    ) -> tuple[float | None, bool]:
    """Workload share of the whole uncaged residual, ramped, bounded at the whole residual.
    (None, False) where nothing priced the residual -- a named absence, never a zero."""
    if base is None:
        return None, False
    share = workloads / total if total else 0.0
    raw = base * share * ramp
    return min(base, raw), raw > base


# --------------------------------------------------------------------------
# the source and schema checks
# --------------------------------------------------------------------------
def _refusal_kinds(body: str) -> set[str]:
    """The refusal kinds a composition source emits: a refusal dict carries `needs_composition`
    within its own literal; a deltas[] entry of the same name (`baseline-widening`) does not --
    that distinction is the whole point of ticket 38."""
    return {m.group(1) for m in re.finditer(r'"kind":\s*"([a-z-]+)"', body)
            if "needs_composition" in body[m.end():m.end() + 400]}


def check_source(src: str) -> None:
    body = src.split("\ndef selfcheck()", 1)[0]
    emitted = _refusal_kinds(body)
    still = sorted(emitted & GONE)
    if still:
        out("FAIL", f"composition.py still emits {still} — a new hole, a widened baseline, a new "
                    f"ungoverned namespace and a removal are priced deltas, never refusals "
                    f"(tickets 38 and 124, ADR-0020, ADR-0026)")
    else:
        out("PASS", "composition.py emits none of new-hole, baseline-widening, "
                    "new-ungoverned-namespace, removed-control")
    if "missing-instrument" not in emitted:
        out("FAIL", "composition.py emits no missing-instrument refusal — a bespoke control with no "
                    "signed scenario must still refuse as an instrument fault (ADR-0020)")
    if "deltas" not in body or "def compute_deltas" not in body:
        out("FAIL", "composition.py builds no deltas[] — the refusals were deleted with nothing "
                    "priced in their place")
    if "def ungoverned_price" not in body or "eol_ramp" not in body:
        out("FAIL", "composition.py carries no ungoverned ramp reusing the feeds module's eol_ramp")


def check_schema(schema: dict) -> None:
    try:
        desc = str(schema["properties"]["overlay"]["properties"]["controls"]["description"])
    except (KeyError, TypeError):
        out("FAIL", "party schema.json does not admit overlay.controls")
        return
    if "party:id" not in desc:
        out("FAIL", "overlay.controls description does not admit the `party:id` form a bespoke "
                    "control needs (ticket 38)")
    elif "priced" not in desc or "never refused" not in desc:
        out("FAIL", "overlay.controls description still reads as a refusal on addition; an added "
                    "control is a priced hole (ticket 38)")
    elif "May only grow" in desc or "exemption by another name" in desc:
        out("FAIL", "overlay.controls description still says a removal refuses; a removal is a "
                    "priced removed-control delta (ticket 124, ADR-0026 point 5)")
    else:
        out("PASS", "party schema.json admits overlay.controls as bare ids and `party:id`, and "
                    "says an addition and a removal are priced, never refused")


# --------------------------------------------------------------------------
# the document check — pure, so selfcheck can plant defects in a dict
# --------------------------------------------------------------------------
def check_doc(doc: dict, ctx: dict) -> None:
    """Grade one adopter's evidence document. `ctx`: adopter, currency, since (namespace ->
    date or None, or the key absent where the clone's tags could not be read), workloads
    (namespace -> count), institution (set of namespace names), exposure_total (float or None),
    as_of (str or None)."""
    who = ctx["adopter"]
    if "deltas" not in doc:
        out("SKIP", f"{who}: composed/evidence.json carries no deltas[] — it was composed under "
                    f"the refusal shape; re-composing an adopter is an enactment push the owner makes")
        return
    bad = sorted({r.get("kind") for r in doc.get("refusals") or []} & GONE)
    if bad:
        out("FAIL", f"{who}: refusals[] carries {bad} — those are priced deltas since ticket 38")
    else:
        out("PASS", f"{who}: no new-hole, baseline-widening or new-ungoverned-namespace refusal")

    # c. holes[] keyed (source, id), priced or a named absence
    holes = doc.get("holes")
    if not isinstance(holes, list):
        out("FAIL", f"{who}: no holes[] list")
        holes = []
    problems = []
    for i, h in enumerate(holes):
        if not isinstance(h, dict) or not HOLE_FIELDS <= set(h):
            problems.append(f"holes[{i}] lacks {sorted(HOLE_FIELDS - set(h if isinstance(h, dict) else []))}")
            continue
        if h["status"] not in HOLE_STATUS:
            problems.append(f"holes[{i}] status {h['status']!r}")
        if h["perspective"] != who or h["currency"] != ctx["currency"]:
            problems.append(f"holes[{i}] is under {h['perspective']}/{h['currency']}, not "
                            f"{who}/{ctx['currency']}")
        amount, by = h["amount"], h["priced_by"]
        if amount is None and by is not None:
            problems.append(f"holes[{i}] names a pricer but no amount")
        elif amount is not None and (not isinstance(amount, (int, float)) or isinstance(amount, bool)
                                     or not by):
            problems.append(f"holes[{i}] carries amount {amount!r} with priced_by {by!r}")
    if problems:
        out("FAIL", f"{who}: {len(problems)} hole(s) malformed: {problems[:3]}")
    elif holes:
        priced = sum(1 for h in holes if h["amount"] is not None)
        out("PASS", f"{who}: {len(holes)} hole(s) keyed (source, id) under {who}/{ctx['currency']}, "
                    f"{priced} priced by a pinned weight or a signed scenario, the rest a named absence")
    else:
        out("PASS", f"{who}: no holes (named absence)")

    # d. the ungoverned price
    for e in doc.get("ungoverned") or []:
        ns = e.get("namespace")
        at = f"{who} ungoverned {ns}"
        if e.get("status") == "closed":
            # d3. a close says why, and the recount agrees (eco-system ticket 122): governed when
            # the repo still declares the Namespace and not ungoverned, left-repo when nothing
            # declares or names it. Before ticket 122 every close printed as governed.
            institution, ungoverned = ctx.get("institution"), ctx.get("ungoverned")
            why = e.get("closed_by")
            if why not in ("governed", "left-repo"):
                out("FAIL", f"{at}: closed with closed_by {why!r}, not governed or left-repo; the "
                            f"artefact predates eco-system ticket 122 or says nothing of why")
            elif institution is not None and ungoverned is not None:
                real = "governed" if ns in institution and ns not in ungoverned else "left-repo"
                if why != real:
                    out("FAIL", f"{at}: closed_by {why} but the repo walk says {real}")
                else:
                    out("PASS", f"{at}: closed_by {why}, as the repo walk finds")
            else:
                out("SKIP", f"{at}: closed_by {why}, not recounted: the substrate could not be "
                            f"read, so the repo walk cannot say governed or left-repo")
            continue
        p = e.get("price")
        if not isinstance(p, dict) or not PRICE_FIELDS <= set(p):
            out("FAIL", f"{at}: no price with {sorted(PRICE_FIELDS)} — an ungoverned namespace is "
                        f"priced, never merely listed (ticket 38)")
            continue
        if p["perspective"] != who or p["currency"] != ctx["currency"]:
            out("FAIL", f"{at}: priced under {p['perspective']}/{p['currency']}, not {who}/{ctx['currency']}")
        counts, institution = ctx.get("workloads"), ctx.get("institution")
        if counts is not None and institution is not None:
            inside = counts.get(ns, 0)
            total = sum(n for k, n in counts.items() if k in institution)
            if p["workloads"] != inside or p["workloads_total"] != total:
                out("FAIL", f"{at}: counts {p['workloads']}/{p['workloads_total']} workloads but the "
                            f"repo walk finds {inside}/{total}")
            share = inside / total if total else 0.0
            if not close(float(p["share"]), share):
                out("FAIL", f"{at}: share {p['share']} is not {inside}/{total}")
        if "since" in ctx:
            real = ctx["since"].get(ns)
            if p["since"] != real:
                out("FAIL", f"{at}: since {p['since']!r} but the first signed tag naming {ns}, or "
                            f"a Namespace its workloads left, says {real!r} — a since is read off "
                            f"a signed tag, never typed")
        if p["since"] is None and not any("no signed composed artefact names" in str(lim)
                                          for lim in p.get("limits") or []):
            out("FAIL", f"{at}: since is null and no limit says so")
        # Eco-system ticket 139. as_of is the newest signed input the composition's tree carries;
        # a tag date is history, not an input, so the first tag naming a Namespace can be cut
        # after it. The ramp then holds at its start, and the price says so with both dates.
        if p["since"] and p["as_of"] and str(p["since"]) > str(p["as_of"]) \
                and not any("precedes since" in str(lim) for lim in p.get("limits") or []):
            out("FAIL", f"{at}: since {p['since']} is later than as_of {p['as_of']} and no limit "
                        f"says the ramp holds at its start")
        if "as_of" in ctx and p["as_of"] != ctx["as_of"]:
            out("FAIL", f"{at}: as_of {p['as_of']!r} but the newest signed input, a pinned feed's "
                        f"published_at or an edge's since, is {ctx['as_of']!r}")
        ramp = expected_ramp(p["since"], p["as_of"])
        if not close(float(p["ramp"]), ramp):
            out("FAIL", f"{at}: ramp {p['ramp']} is not the EOL ramp from {p['since']} to "
                        f"{p['as_of']} ({ramp:.6f})")
        if "exposure_total" in ctx and p["base"] != ctx["exposure_total"]:
            out("FAIL", f"{at}: base {p['base']!r} is not the header's signed exposure total "
                        f"{ctx['exposure_total']!r}")
        amount, bounded = expected_amount(p["base"], int(p["workloads"]), int(p["workloads_total"]),
                                          float(p["ramp"]))
        if amount is None:
            if p["amount"] is not None:
                out("FAIL", f"{at}: prices {p['amount']} off no base — an invented number")
            elif not any("no priced exposure" in str(lim) for lim in p.get("limits") or []):
                out("FAIL", f"{at}: no amount and no limit naming the missing exposure")
            else:
                out("PASS", f"{at}: no priced exposure to take a share of, and the entry says so")
            continue
        if p["amount"] is None or not close(float(p["amount"]), amount):
            out("FAIL", f"{at}: amount {p['amount']} is not min(base, base x share x ramp) = {amount:.2f}")
        elif float(p["amount"]) > float(p["base"]) + 1e-6:
            out("FAIL", f"{at}: amount {p['amount']} exceeds the whole residual {p['base']}")
        elif bool(p["bounded"]) != bounded:
            out("FAIL", f"{at}: bounded says {p['bounded']} but the arithmetic says {bounded}")
        else:
            out("PASS", f"{at}: {p['amount']:,.2f} {p['currency']} = {p['workloads']}/"
                        f"{p['workloads_total']} workloads x ramp {p['ramp']:.4f} from since "
                        f"{p['since']} as of {p['as_of']}, of {p['base']:,.2f}"
                        + (", bounded at the whole residual" if bounded else ""))

    # d2. every Namespace the repo walk finds ungoverned carries a price (eco-system ticket 119).
    #     Leaving a Namespace unlabelled, or never declaring it, no longer keeps it out.
    if "ungoverned" in ctx:
        open_ns = {e.get("namespace") for e in doc.get("ungoverned") or [] if e.get("status") != "closed"}
        unpriced = sorted(set(ctx["ungoverned"]) - open_ns)
        if unpriced:
            out("FAIL", f"{who}: {', '.join(unpriced)} ungoverned in the adopter's repo but carries no "
                        f"price in composed/evidence.json; a Namespace with no label is priced "
                        f"since eco-system ticket 119, and the artefact predates that rule")
        else:
            out("PASS", f"{who}: every ungoverned Namespace the repo walk finds is priced "
                        f"({', '.join(sorted(ctx['ungoverned'])) or 'none'})")

    # e. the regime entry's holes[] carry status and agree with holes[]
    status_by_key = {(h["source"], h["control_id"]): h["status"] for h in holes
                     if isinstance(h, dict) and HOLE_FIELDS <= set(h)}
    for e in doc.get("prices") or []:
        if e.get("kind") != "feed" or not e.get("holes"):
            continue
        at = f"{who} regime entry ({e.get('name')})"
        lines = e["holes"]
        missing = [h for h in lines if h.get("status") not in REGIME_STATUS]
        wrong = [h for h in lines if (h.get("source"), h.get("id")) in status_by_key
                 and h.get("status") != status_by_key[(h.get("source"), h.get("id"))]]
        if missing:
            out("FAIL", f"{at}: {len(missing)} weighted hole(s) carry no status in {sorted(REGIME_STATUS)}")
        elif wrong:
            out("FAIL", f"{at}: {len(wrong)} weighted hole(s) disagree with holes[] on status: "
                        f"{wrong[:2]}")
        else:
            out("PASS", f"{at}: all {len(lines)} weighted holes carry the adopter's status "
                        f"({', '.join(sorted({h['status'] for h in lines}))})")

    # f. deltas[]
    deltas = doc.get("deltas")
    if not isinstance(deltas, list):
        out("FAIL", f"{who}: deltas is not a list")
        return
    problems = []
    for i, d in enumerate(deltas):
        if not isinstance(d, dict) or d.get("kind") not in DELTA_KINDS:
            problems.append(f"deltas[{i}] kind {d.get('kind') if isinstance(d, dict) else d!r}")
            continue
        if d.get("perspective") != who or d.get("currency") != ctx["currency"]:
            problems.append(f"deltas[{i}] is not under {who}/{ctx['currency']}")
        if "amount" not in d:
            problems.append(f"deltas[{i}] carries no amount field")
    want_holes = {(h["source"], h["control_id"], h["status"]) for h in holes
                  if isinstance(h, dict) and h.get("status") in ("new", "closed")}
    got_holes = {(d.get("source"), d.get("control_id"), d["kind"].split("-")[0])
                 for d in deltas if isinstance(d, dict) and d.get("kind") in ("new-hole", "closed-hole")}
    if want_holes != got_holes:
        problems.append(f"hole deltas {sorted(got_holes)[:3]} do not match new/closed holes "
                        f"{sorted(want_holes)[:3]}")
    want_ns = {(e["namespace"], e["status"]) for e in doc.get("ungoverned") or []
               if e.get("status") in ("new", "closed")}
    got_ns = {(d.get("namespace"), d["kind"].split("-")[0]) for d in deltas
              if isinstance(d, dict) and d.get("kind", "").endswith("ungoverned-namespace")}
    if want_ns != got_ns:
        problems.append(f"namespace deltas {sorted(got_ns)} do not match new/closed entries {sorted(want_ns)}")
    if problems:
        out("FAIL", f"{who}: deltas[] observed false: {problems[:3]}")
    else:
        out("PASS", f"{who}: {len(deltas)} delta(s), each one of the {len(DELTA_KINDS)} kinds under "
                    f"{who}/{ctx['currency']}, matching the holes and namespaces they report")


# --------------------------------------------------------------------------
# reading the estate
# --------------------------------------------------------------------------
def _parties(estate: str) -> dict[str, dict]:
    found = {}
    for p in sorted(glob.glob(os.path.join(estate, "*", "party.yaml"))):
        with open(p) as fh:
            found[os.path.basename(os.path.dirname(p))] = yaml.safe_load(fh) or {}
    return found


def _substrate(estate: str) -> set[str] | None:
    """The Namespaces the platform declares `infra` in its own engine/namespaces.yaml (ADR-0022,
    eco-system ticket 113). Since ticket 119 they are the only ones an adopter's walk leaves
    unpriced. None where the declaration cannot be read: the recount cannot tell the substrate."""
    path = os.path.join(estate, "platform", "engine", "namespaces.yaml")
    try:
        with open(path) as fh:
            docs = [d for d in yaml.safe_load_all(fh) if isinstance(d, dict)]
    except (OSError, yaml.YAMLError):
        return None
    names = {str((d.get("metadata") or {}).get("name")) for d in docs
             if d.get("kind") == "Namespace"
             and (((d.get("metadata") or {}).get("labels") or {}).get(TIER_LABEL) == "infra")}
    return names or None


def _namespace_facts(root: str, substrate: set[str]) -> tuple[set[str], dict[str, int], set[str]]:
    """The recount, by the rule composition.py follows since eco-system ticket 119: every
    Namespace the repo declares or a workload names is an institution Namespace, whatever labels
    it carries, except the platform's substrate. Returns that set, the workloads per Namespace,
    and the ungoverned ones (declared without `governed: "true"`, or never declared)."""
    institution: set[str] = set()
    governed: set[str] = set()
    workloads: dict[str, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "composed", ".work")]
        for name in sorted(filenames):
            if not name.endswith(".yaml"):
                continue
            try:
                with open(os.path.join(dirpath, name)) as fh:
                    docs = [d for d in yaml.safe_load_all(fh) if isinstance(d, dict)]
            except (OSError, yaml.YAMLError):
                continue
            for d in docs:
                md = d.get("metadata") or {}
                if d.get("kind") == "Namespace":
                    ns = str(md.get("name"))
                    if ns not in substrate:
                        institution.add(ns)
                        if (md.get("labels") or {}).get(GOVERNED_LABEL) == "true":
                            governed.add(ns)
                elif d.get("kind") in WORKLOAD_KINDS:
                    ns = str(md.get("namespace") or "default")
                    workloads[ns] = workloads.get(ns, 0) + 1
    institution |= {ns for ns in workloads if ns not in substrate}
    return institution, workloads, institution - governed


def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=60)


def _add_workload_keys(docs: list, into: dict[str, set[str]]) -> None:
    for d in docs:
        if isinstance(d, dict) and d.get("kind") in WORKLOAD_KINDS:
            md = d.get("metadata") or {}
            into.setdefault(str(md.get("namespace") or "default"), set()).add(f"{d['kind']}/{md.get('name')}")


def _workloads_now(root: str) -> dict[str, set[str]]:
    """Namespace -> `Kind/name` of every workload the adopter's checkout declares in it, over the
    same files `_namespace_facts` walks."""
    found: dict[str, set[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "composed", ".work")]
        for name in sorted(filenames):
            if not name.endswith(".yaml"):
                continue
            try:
                with open(os.path.join(dirpath, name)) as fh:
                    _add_workload_keys(list(yaml.safe_load_all(fh)), found)
            except (OSError, yaml.YAMLError):
                continue
    return found


def _workloads_at(repo: str, tag: str) -> dict[str, set[str]]:
    """The same walk over the tree a tag points at, read one file at a time from git objects."""
    found: dict[str, set[str]] = {}
    listed = _git(repo, "ls-tree", "-r", "--name-only", tag)
    for path in listed.stdout.splitlines():
        parts = path.split("/")
        if not path.endswith(".yaml") or {".git", "composed", ".work"} & set(parts):
            continue
        shown = subprocess.run(["git", "-C", repo, "show", f"{tag}:{path}"], capture_output=True, timeout=60)
        try:
            _add_workload_keys(list(yaml.safe_load_all(shown.stdout.decode())), found)
        except (yaml.YAMLError, UnicodeDecodeError):
            continue
    return found


def _signed_since(repo: str, namespaces: list[str],
                  ungoverned: set[str] | None = None) -> dict[str, str | None] | None:
    """namespace -> the date of the first signed tag whose composed header names it, or names as
    ungoverned a Namespace that held, in that tag's tree, a workload (`Kind/name`) this one holds
    now and that Namespace no longer holds as an ungoverned Namespace (eco-system ticket 122: the
    age follows the workloads, so a rename keeps its ramp and a copy beside the original does not
    take it). "As an ungoverned Namespace" is the review round's repair: re-declaring the old
    name governed, with inert manifests of the same kind and name, would otherwise drop the age,
    and a governed Namespace pays no ramp. `ungoverned` is the recount's ungoverned set; None
    derives it from the repo walk with no substrate. None per namespace where no tag carries it.
    None overall where the clone is not a git repo or lists no tags (could not look).
    Re-derived here from the clone; composition.py is not imported."""
    if not os.path.exists(os.path.join(repo, ".git")):
        return None
    listed = _git(repo, "for-each-ref", "--sort=creatordate",
                  "--format=%(refname:short) %(creatordate:short) %(objecttype)", "refs/tags")
    tags = [line.split() for line in listed.stdout.splitlines()]
    tags = [t for t in tags if len(t) == 3 and t[2] == "tag"]
    if not tags:
        return None
    result: dict[str, str | None] = {ns: None for ns in namespaces}
    now = _workloads_now(repo)
    if ungoverned is None:
        ungoverned = _namespace_facts(repo, set())[2]
    still = {ns: keys for ns, keys in now.items() if ns in ungoverned}
    for tag, date, _kind in tags:
        if "-----BEGIN" not in _git(repo, "cat-file", "-p", tag).stdout:
            continue
        shown = _git(repo, "show", f"{tag}:composed/HEADER.yaml")
        if shown.returncode != 0:
            continue
        try:
            header = yaml.safe_load(shown.stdout)
        except yaml.YAMLError:
            continue
        named = set((header or {}).get("ungoverned-namespaces") or []) if isinstance(header, dict) else set()
        held = _workloads_at(repo, tag) if named and None in result.values() else {}
        for ns in namespaces:
            if result[ns] is not None:
                continue
            mine = now.get(ns, set())
            if ns in named or any((held.get(x, set()) & mine) - still.get(x, set()) for x in named):
                result[ns] = date
    return result


def _header(repo: str) -> dict:
    path = os.path.join(repo, "composed", "HEADER.yaml")
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    return doc if isinstance(doc, dict) else {}


def _published_dir(tree: str, name: str) -> str:
    """The directory the publisher's own party.yaml declares for a feed name, or the name."""
    try:
        with open(os.path.join(tree, "party.yaml")) as fh:
            doc = yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        doc = {}
    return next((str(r.get("path")) for r in doc.get("publishes") or []
                 if isinstance(r, dict) and r.get("name") == name and r.get("path")), name)


def _feed_path(estate: str, parties: dict, edge: dict, repo: str | None = None) -> str | None:
    """The envelope the adopter priced this feed edge from. First the adopter's own vendored copy,
    `composed/feeds/<party>/<name>/<version>` (eco-system ticket 136): its bytes are the ones the
    adopter's signature digested, so a publisher that republished since does not move a signed
    price (ticket 138). Then the publisher's tree in the estate, then the two pre-envelope files."""
    party, name, version = edge.get("party"), edge.get("name"), str(edge.get("version"))
    major = "v" + version.lstrip("v").split(".")[0]
    if repo:
        copy = os.path.join(repo, "composed", "feeds", str(party), str(name), version)
        vendored = os.path.join(copy, _published_dir(copy, str(name)), major, "feed.json")
        if os.path.exists(vendored):
            return vendored
    pub = parties.get(party) or {}
    path = next((r.get("path") for r in pub.get("publishes") or [] if r.get("name") == name), name)
    envelope = os.path.join(estate, str(party), str(path), major, "feed.json")
    if os.path.exists(envelope):
        return envelope
    legacy = {"penalty-schema": os.path.join(estate, "ico", "schema", version, "penalty-schema.json"),
              "threat-register": os.path.join(estate, "feeds", "threat-register", version, "register.json")}
    fallback = legacy.get(str(name))
    return fallback if fallback and os.path.exists(fallback) else None


def _as_of(estate: str, parties: dict, adopter_doc: dict, repo: str | None = None) -> str | None:
    """The date composition prices as of: the newest SIGNED date among its inputs. That is every
    pinned feed envelope's published_at and, since platform ticket 84, every edge's own `since`
    (composition.py `_composition_as_of`, ADR-0006's 2026-09-08 note). Before eco-system ticket 138
    this read the envelopes only, and tuppence's cve@v2 edge, signed 2026-09-08 over envelopes
    published by 2026-08-28, graded as two dates."""
    dates = [str(edge["since"])[:10] for edge in adopter_doc.get("inherits") or []
             if isinstance(edge, dict) and edge.get("since")]
    for edge in adopter_doc.get("inherits") or []:
        if edge.get("kind") not in ("feed", "pricing", "threat"):
            continue
        if edge.get("kind") != "feed":
            edge = dict(edge, name={"pricing": "penalty-schema", "threat": "threat-register"}[edge["kind"]])
        path = _feed_path(estate, parties, edge, repo)
        if not path:
            continue
        try:
            with open(path) as fh:
                published = json.load(fh).get("published_at")
        except (OSError, ValueError):
            continue
        if isinstance(published, str):
            dates.append(published[:10])
    return max(dates) if dates else None


def run(estate: str) -> None:
    comp = os.path.join(estate, "platform", "compose", "composition.py")
    schema = os.path.join(estate, "platform", "party", "schema.json")
    if not os.path.exists(comp):
        out("SKIP", f"no {comp}: nothing to look at")
        return
    with open(comp) as fh:
        check_source(fh.read())
    if os.path.exists(schema):
        with open(schema) as fh:
            check_schema(json.load(fh))
    else:
        out("SKIP", f"no {schema}")
    parties = _parties(estate)
    adopters = [n for n, d in sorted(parties.items()) if "adopter" in (d.get("roles") or [])]
    if not adopters:
        out("FAIL", f"no adopter party under {estate}")
    for name in adopters:
        repo = os.path.join(estate, name)
        ev = os.path.join(repo, "composed", "evidence.json")
        if not os.path.exists(ev):
            out("SKIP", f"{name} has no composed/evidence.json — nothing composed to grade")
            continue
        try:
            with open(ev) as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as exc:
            out("FAIL", f"{name}: composed/evidence.json does not parse: {exc}")
            continue
        namespaces = [e.get("namespace") for e in doc.get("ungoverned") or []]
        ctx: dict[str, Any] = {
            "adopter": name,
            "currency": parties[name].get("reporting_currency") or "USD",
            "exposure_total": (_header(repo).get("exposure") or {}).get("total"),
            "as_of": _as_of(estate, parties, parties[name], repo),
        }
        substrate = _substrate(estate)
        if substrate is None:
            out("SKIP", f"{name}: platform/engine/namespaces.yaml declares no infra Namespace, so "
                        f"the recount cannot tell the substrate from an adopter Namespace")
        else:
            institution, workloads, ungoverned = _namespace_facts(repo, substrate)
            ctx.update(workloads=workloads, institution=institution, ungoverned=ungoverned)
        if namespaces and "ungoverned" not in ctx:
            out("SKIP", f"{name}: without the substrate the recount has no ungoverned set, so a "
                        f"since carried by a rename (eco-system ticket 122) could not be read back")
        else:
            since = _signed_since(repo, [str(n) for n in namespaces], ctx.get("ungoverned")) \
                if namespaces else {}
            if since is None:
                out("SKIP", f"{name}: the clone lists no signed tag, so the since of its ungoverned "
                            f"namespaces could not be read back")
            else:
                ctx["since"] = since
        check_doc(doc, ctx)


def exit_code() -> int:
    if "FAIL" in LINES:
        return 1
    return 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
# selfcheck — planted defects, each of which must be observed false
# --------------------------------------------------------------------------
def _good() -> tuple[dict, dict]:
    ramp = expected_ramp("2026-08-25", "2026-08-28")
    doc = {
        "outcome": "composed",
        "refusals": [],
        "holes": [
            {"source": "nist", "control_id": "pl-2", "status": "recorded", "perspective": "driftwood",
             "currency": "GBP", "amount": 90.0, "priced_by": "ico penalty-schema@v3 uk-gdpr/lower-tier weight 0.3"},
            {"source": "nist", "control_id": "ac-6.10", "status": "new", "perspective": "driftwood",
             "currency": "GBP", "amount": None, "priced_by": None},
            {"source": "driftwood", "control_id": "dw-1", "status": "recorded", "perspective": "driftwood",
             "currency": "GBP", "amount": 12.5, "priced_by": "driftwood scenario scenarios/dw-1.json"},
        ],
        "ungoverned": [
            {"namespace": "reset", "status": "recorded", "price": {
                "perspective": "driftwood", "currency": "GBP", "amount": 300.0 * 0.5 * ramp,
                "share": 0.5, "workloads": 1, "workloads_total": 2, "base": 300.0,
                "ramp": ramp, "since": "2026-08-25",
                "as_of": "2026-08-28", "bounded": False, "limits": []}},
        ],
        "prices": [
            {"source": "ico", "kind": "feed", "name": "penalty-schema", "perspective": "driftwood",
             "currency": "GBP", "amount": 300.0, "total": 300.0,
             "holes": [{"source": "nist", "id": "pl-2", "weight": 0.3, "amount": 90.0, "status": "recorded"},
                       {"source": "nist", "id": "ac-6", "weight": 0.7, "amount": 210.0, "status": "covered"}]},
        ],
        "deltas": [
            {"kind": "new-hole", "source": "nist", "control_id": "ac-6.10", "perspective": "driftwood",
             "currency": "GBP", "amount": None, "priced_by": None, "detail": "x"},
        ],
    }
    ctx = {"adopter": "driftwood", "currency": "GBP",
           "workloads": {"reset": 1, "driftwood": 1, "flux-system": 1},
           "institution": {"reset", "driftwood"}, "ungoverned": {"reset"},
           "exposure_total": 300.0, "as_of": "2026-08-28", "since": {"reset": "2026-08-25"}}
    return doc, ctx


def _grade(doc: dict, ctx: dict, label: str, want_fail: bool, want_skip: bool = False) -> None:
    LINES.clear()
    check_doc(doc, ctx)
    failed = "FAIL" in LINES
    assert failed == want_fail, f"{label}: expected {'FAIL' if want_fail else 'no FAIL'}, got {LINES}"
    if want_skip:
        assert "SKIP" in LINES, f"{label}: expected a SKIP, got {LINES}"
    print(f"ok  {label}")


def selfcheck() -> None:
    assert expected_ramp("2026-08-25", "2026-08-28") == 1.0 + 3 / 365.0
    assert expected_ramp("2026-08-25", "2026-08-20") == 1.0 and expected_ramp(None, "x") == 1.0
    assert expected_ramp("2020-01-01", "2030-01-01") == 5.0
    assert expected_amount(1000.0, 1, 4, 1.0) == (250.0, False)
    assert expected_amount(1000.0, 1, 4, 5.0) == (1000.0, True)
    assert expected_amount(None, 1, 4, 1.0) == (None, False)
    assert expected_amount(1000.0, 0, 0, 2.0) == (0.0, False)
    print("ok  the ramp and the bound re-derive: +1x/yr past since, capped +4x; share x base, never above base")

    doc, ctx = _good()
    _grade(doc, ctx, "a well-formed priced document passes", False)

    doc, ctx = _good()
    doc.pop("deltas")
    _grade(doc, ctx, "an evidence document composed under the refusal shape is a graded SKIP", False, want_skip=True)

    doc, ctx = _good()
    doc["refusals"] = [{"kind": "new-hole", "subject": "ac-6.10"}]
    _grade(doc, ctx, "a new-hole refusal fails", True)

    doc, ctx = _good()
    doc["holes"][0].pop("source")
    _grade(doc, ctx, "a hole with no source fails", True)

    doc, ctx = _good()
    doc["holes"][1]["amount"] = 0.0
    _grade(doc, ctx, "a hole priced at zero by nobody fails", True)

    doc, ctx = _good()
    doc["holes"][0]["perspective"] = "ludlow"
    _grade(doc, ctx, "a hole under another party's perspective fails", True)

    doc, ctx = _good()
    doc["ungoverned"][0].pop("price")
    _grade(doc, ctx, "an ungoverned namespace with no price fails", True)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"]["ramp"] = 1.5
    _grade(doc, ctx, "a ramp that is not the EOL ramp from since to as_of fails", True)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"]["amount"] = 400.0
    _grade(doc, ctx, "an amount above the whole residual fails", True)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"]["share"] = 1.0
    _grade(doc, ctx, "a share that is not workloads inside over institution workloads fails", True)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"]["since"] = "2026-08-01"
    _grade(doc, ctx, "a since no signed tag carries fails (a typed date)", True)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"]["since"] = None
    doc["ungoverned"][0]["price"]["ramp"] = 1.0
    doc["ungoverned"][0]["price"]["amount"] = 150.0
    ctx["since"] = {"reset": None}
    _grade(doc, ctx, "a null since with no limit naming it fails", True)
    doc["ungoverned"][0]["price"]["limits"] = ["no signed composed artefact names reset: ramp held at 1.0"]
    _grade(doc, ctx, "a null since with the limit named passes", False)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"].update(since="2026-09-24", as_of="2026-09-08", ramp=1.0, amount=150.0)
    ctx.update(since={"reset": "2026-09-24"}, as_of="2026-09-08")
    _grade(doc, ctx, "a since later than as_of with no limit naming it fails (ticket 139)", True)
    doc["ungoverned"][0]["price"]["limits"] = ["as_of 2026-09-08 precedes since 2026-09-24: ramp held at its start"]
    _grade(doc, ctx, "a since later than as_of with the ramp at its start and the limit named passes", False)

    doc, ctx = _good()
    doc["ungoverned"][0]["status"] = "new"        # reopened: keeps the since the first signed tag carries
    doc["deltas"].append({"kind": "new-ungoverned-namespace", "namespace": "reset", "perspective": "driftwood",
                          "currency": "GBP", "amount": doc["ungoverned"][0]["price"]["amount"], "detail": "x"})
    _grade(doc, ctx, "a reopened namespace keeps its original since (since-preservation)", False)

    doc, ctx = _good()
    doc["ungoverned"][0]["price"]["base"] = 250.0
    _grade(doc, ctx, "a base that is not the header's signed exposure total fails", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"][0].pop("status")
    _grade(doc, ctx, "a weighted hole with no status fails", True)

    doc, ctx = _good()
    doc["prices"][0]["holes"][0]["status"] = "closed"
    _grade(doc, ctx, "a weighted hole whose status disagrees with holes[] fails", True)

    doc, ctx = _good()
    doc["deltas"][0]["kind"] = "refusal"
    _grade(doc, ctx, "a delta of an unknown kind fails", True)

    # Ticket 69's two kinds are admitted -- an untagged feed pin is a priced hole on the
    # premium entry and its moves are deltas -- while a kind DELTA_KINDS does not name still
    # fails, so the whitelist is a whitelist and not a hole in this check.
    for kind in ("new-untagged-pin", "closed-untagged-pin"):
        doc, ctx = _good()
        doc["deltas"].append({"kind": kind, "source": "insurer", "name": "quote-driftwood",
                              "version": "v2", "perspective": "driftwood", "currency": "GBP",
                              "amount": 113403.3, "priced_by": "the premium the pin books",
                              "detail": "x"})
        _grade(doc, ctx, f"a {kind} delta (ticket 69) passes", False)

    doc, ctx = _good()
    doc["deltas"].append({"kind": "reopened-untagged-pin", "source": "insurer", "perspective": "driftwood",
                          "currency": "GBP", "amount": 1.0, "detail": "x"})
    _grade(doc, ctx, "a delta whose kind merely looks like ticket 69's still fails", True)

    doc, ctx = _good()
    doc["deltas"] = []
    _grade(doc, ctx, "a new hole with no delta reporting it fails", True)

    doc, ctx = _good()
    ctx["ungoverned"] = {"reset", "openbao"}
    _grade(doc, ctx, "an ungoverned Namespace the repo walk finds and the evidence leaves unpriced "
                     "fails (ticket 119)", True)

    doc, ctx = _good()
    doc["ungoverned"].append({"namespace": "side", "status": "closed", "closed_by": "left-repo"})
    doc["deltas"].append({"kind": "closed-ungoverned-namespace", "namespace": "side",
                          "perspective": "driftwood", "currency": "GBP", "amount": None, "detail": "x"})
    _grade(doc, ctx, "a close the repo walk agrees left the repo passes (ticket 122)", False)
    doc["ungoverned"][-1]["closed_by"] = "governed"
    _grade(doc, ctx, "a rename that prints as governance fails (ticket 122)", True)
    doc["ungoverned"][-1].pop("closed_by")
    _grade(doc, ctx, "a close that does not say why fails (ticket 122)", True)

    doc, ctx = _good()
    doc["deltas"][0]["currency"] = "USD"
    _grade(doc, ctx, "a delta in another currency fails", True)

    LINES.clear()
    src_bad = ('refusals.append({"kind": "new-hole", "subject": cid, "needs_composition": True})\n'
               '{"kind": "missing-instrument", "needs_composition": True}\n'
               'def compute_deltas\ndef ungoverned_price eol_ramp deltas')
    check_source(src_bad)
    assert "FAIL" in LINES, LINES
    LINES.clear()
    # ticket 124: the removal refusal ADR-0026 point 5 retired is gone too
    src_removal = ('{"kind": "missing-instrument", "needs_composition": True}\n'
                   '{"kind": "removed-control", "needs_composition": True}\n'
                   'def compute_deltas\ndeltas\ndef ungoverned_price\neol_ramp')
    check_source(src_removal)
    assert "FAIL" in LINES, LINES
    LINES.clear()
    src_good = ('{"kind": "missing-instrument", "needs_composition": True}\n'
                'deltas.append({"kind": "removed-control", "source": s, "perspective": p})\n'
                'return {"kind": "baseline-widening", "subject": s, "perspective": p}\n'   # a delta, not a refusal
                'def compute_deltas\ndeltas\ndef ungoverned_price\neol_ramp')
    check_source(src_good)
    assert "FAIL" not in LINES, LINES
    print("ok  the source check bites on a surviving refusal literal, and a delta of the same "
          "name is not mistaken for one")

    LINES.clear()
    check_schema({"properties": {"overlay": {"properties": {"controls": {
        "description": "May only grow: a composition refuses on any id that leaves the set."}}}}})
    assert "FAIL" in LINES, LINES
    LINES.clear()
    check_schema({"properties": {"overlay": {"properties": {"controls": {
        "description": "bare or `party:id`; an addition is a priced hole, never refused."}}}}})
    assert "FAIL" not in LINES, LINES
    print("ok  the schema check bites on a refusal-only description and passes the priced one")

    LINES.clear()
    print("ok  selfcheck: refusal absence, (source, id) holes, the ungoverned share/ramp/bound/since, "
          "regime status and deltas[] all graded")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "selfcheck":
        selfcheck()
        sys.exit(0)
    if cmd != "check":
        print(__doc__)
        sys.exit(2)
    estate = os.environ.get("PAVC_ESTATE_CLONE") or ESTATE
    if not os.path.isdir(estate):
        print(f"SKIP: {estate} absent — run ./clone-estate.sh first")
        sys.exit(3)
    run(estate)
    sys.exit(exit_code())
