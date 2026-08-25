#!/usr/bin/env python3
"""PROTOTYPE — spike cs-06b. Throwaway. Cross-party policy composition.

  Can a party's effective policy set be INHERITED from several other parties,
  the way a class inherits, and still render down to what Kyverno runs today?

The class analogy, mapped onto the estate as it really is:

  nist       controls          ABSTRACT BASE.   Says what must hold, never how.
  ico        pricing           A MIXIN on the money axis. Contributes no rules.
  platform   implementations   CONCRETE CLASS.  Implements nist's controls.
  driftwood  (adopter)         SUBCLASS.        Inherits platform AND nist.

driftwood inheriting both parents is the diamond, and it is real today:
driftwood -> platform -> nist, and driftwood -> nist.

Everything platform publishes is read LIVE from .estate-clone/platform. The
party manifests in material/parties/ are the only invented part, because the
inheritance edges do not exist in the estate yet. That is the point.

Run: ./run.sh
"""

import copy
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import yaml

HERE = pathlib.Path(__file__).parent
PARTIES = HERE / "material" / "parties"
CLONE = HERE.parents[1] / ".estate-clone"

VERSION_SUFFIX = re.compile(r"-\d+-\d+-\d+$")
STRICTNESS = {"Audit": 0, "Deny": 1}


def rule(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


# ---------------------------------------------------------------------------
# What platform really publishes. Read from the clone, never invented.
# ---------------------------------------------------------------------------


def load_publications():
    """Every ValidatingPolicy platform ships, which control it claims, and
    which policy versions the ResourceSet array actually reconciles."""
    root = CLONE / "platform"

    impls = {}  # (policy, version) -> {"action", "tree", "installed"}
    for tree in ("distribution", "policy"):
        if not (root / tree / "policies").is_dir():
            continue   # cs-16 deleted policy/policies/. Section 11 records it.
        for path in sorted((root / tree / "policies").rglob("*.yaml")):
            if path.name == "kustomization.yaml":
                continue
            # safe_load_all: the version trees now ship a multi-document
            # priorityclasses.yaml, which safe_load refuses outright.
            docs = [d for d in yaml.safe_load_all(path.read_text()) if isinstance(d, dict)]
            doc = next((d for d in docs if d.get("kind") == "ValidatingPolicy"), None)
            if doc is None:
                continue
            labels = (doc.get("metadata") or {}).get("labels") or {}
            name = labels.get("policy-as-versioned.dev/policy") or \
                VERSION_SUFFIX.sub("", doc["metadata"]["name"])
            version = labels.get("policy-as-versioned.dev/policy-version") or path.parent.name.lstrip("v")
            impls[(name, version)] = {
                "action": (doc["spec"]["validationActions"] or ["Audit"])[0],
                "tree": tree,
                "path": str(path.relative_to(root)),
                "doc": doc,          # the whole body, so render() is not a husk
            }

    # The version array: the single edit that installs or retires a version.
    rs = yaml.safe_load((root / "distribution" / "versions.yaml").read_text())
    array = rs["spec"]["inputs"][0]["versions"]
    live = [v["version"] for v in array]
    # The array reconciles ./distribution/policies/v<version> and nothing else.
    for (name, version), meta in impls.items():
        meta["installed"] = meta["tree"] == "distribution" and version in live

    # control -> the policy names claimed as its evidence.
    #
    # Keyed CASE-FOLDED on purpose. The catalogue's own control ids are
    # lowercase: 'ac-6', 'cm-6', verified against
    # nist/catalog/NIST_SP-800-53_rev5.2.0_catalog.json. The component
    # definition writes them uppercase: 'nist-800-53:AC-6'. A resolver doing an
    # exact string match between the two finds nothing. This spike folds the
    # case so it can get on with its real question, and reports the mismatch.
    cd = json.loads((root / "oscal" / "component-definition.json").read_text())
    mapping, raw_ids = {}, []
    for comp in cd["component-definition"]["components"]:
        for ci in comp["control-implementations"]:
            for req in ci["implemented-requirements"]:
                raw_ids.append(req["control-id"])
                mapping[req["control-id"].lower()] = [
                    p["value"] for p in req.get("props", []) if p["name"] == "Check_Id"
                ]

    return {"impls": impls, "live": live, "mapping": mapping, "raw_control_ids": raw_ids,
            "cage": load_engine(), "bands": appetite_bands()}


ADMISSION_KINDS = ("ValidatingPolicy", "MutatingPolicy", "GeneratingPolicy")


def load_live_set(version):
    """TICKET 06. The WHOLE admission set one claimed version installs — every
    kind, not just ValidatingPolicy — plus the orphan guard.

    load_publications() above reads ValidatingPolicy only, which is why the
    first pass composed 3 policies out of 8. cs-03 called the other five
    "unversioned". Four of them no longer are: cs-12's render-version-tree.py
    now emits cage-tier, cage-netpol, stamp-posture and posture-trust-boundary
    into every version tree, self-scoped on the claim. So they compose exactly
    like require-nonroot does.

    The fifth, the orphan guard, is the aggregate over the version ARRAY and
    cannot self-scope to one claim. cs-22 gave it the `platform-machinery`
    identity: numbered by the platform tag, not by a policy version. It is
    rendered here through the estate's OWN offline twin, never re-modelled.

    Keyed on (family, base name), per cs-22: the identity label is a FAMILY
    name, not a unique key. `graded-enforcement` alone covers cage-tier,
    cage-netpol and three PriorityClasses.
    """
    root = CLONE / "platform"
    members, kinds = {}, {}
    for path in sorted((root / "distribution" / "policies" / f"v{version}").glob("*.yaml")):
        if path.name == "kustomization.yaml":
            continue
        for doc in yaml.safe_load_all(path.read_text()):
            if not isinstance(doc, dict):
                continue
            kinds[doc.get("kind")] = kinds.get(doc.get("kind"), 0) + 1
            if doc.get("kind") not in ADMISSION_KINDS:
                continue        # PriorityClasses are dials, not admission.
            labels = (doc["metadata"].get("labels") or {})
            family = labels.get("policy-as-versioned.dev/policy", "(none)")
            base = VERSION_SUFFIX.sub("", doc["metadata"]["name"])
            members[(family, base)] = {
                "kind": doc["kind"], "doc": doc,
                "path": str(path.relative_to(root)),
                "declared": labels.get("policy-as-versioned.dev/policy-version"),
            }

    # The estate's own offline twin. Its filename is hyphenated, so it loads by
    # path rather than by import name.
    rog = importlib.util.spec_from_file_location(
        "render_orphan_guard", root / "distribution" / "render-orphan-guard.py")
    twin = importlib.util.module_from_spec(rog)
    rog.loader.exec_module(twin)
    guard = twin.orphan_guard(twin.versions(root / "distribution" / "versions.yaml"))
    members[("platform-machinery", "policy-version-orphan-guard")] = {
        "kind": guard["kind"], "doc": guard,
        "path": "distribution/versions.yaml (rendered from the array)",
        "declared": None,
    }
    return members, kinds


def load_engine():
    """Import the estate's REAL £ engine rather than modelling it again.

    graded/cage.py picks the loosest tier whose caged residual fits the org's
    appetite band, and returns Deny only when even quarantine is over-band. It
    reuses fair/fair.py and risk/enforce.py. fair.py samples beta-PERT with a
    fixed seed, so every number below is reproducible.
    """
    sys.path.insert(0, str(CLONE / "platform" / "graded"))
    import cage  # noqa: E402
    return cage


def appetite_bands():
    """REAL. platform/risk/appetite.json is the single source of truth for the
    per-party tolerance in GBP/year."""
    data = json.loads((CLONE / "platform" / "risk" / "appetite.json").read_text())
    return {org: v["tolerance"] for org, v in data["orgs"].items()}


def threat_scenario(feed_version, institution):
    """REAL. Turn the signed, versioned threat register into a fair.py scenario
    using the estate's own converter. No maths of this spike's own."""
    out = subprocess.run(
        [sys.executable, str(CLONE / "platform" / "feeds" / "to_fair_scenario.py"), "threat",
         str(CLONE / "platform" / "feeds" / "threat-register" / feed_version / "register.json"),
         institution],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def load_parties():
    return {p.stem: yaml.safe_load(p.read_text()) for p in sorted(PARTIES.glob("*.yaml"))}


# ---------------------------------------------------------------------------
# The resolver
# ---------------------------------------------------------------------------


class Composition:
    def __init__(self, party):
        self.party = party
        self.edges = []       # (parent, kind, version, path-taken)
        self.diamonds = {}    # (parent, kind) -> {version: [paths]}
        self.baseline = []    # controls this party must satisfy
        self.effective = {}   # (policy, version) -> meta, with provenance
        self.collisions = {}  # version -> [policy names from >1 tree]
        self.uncovered = []   # (control, why) — a hard stop
        self.partial = []     # (control, missing, uninstalled) — a claim wider than reality
        self.refusals = []    # hard stops
        self.orphans = []     # workloads whose pin left the array
        self.cannot_satisfy = []  # declared inabilities, priced into cages
        self.cages = []       # the cage decision for each one
        self.rule_conflicts = []  # (key, source A, source B) — peers disagreeing

    @property
    def refused(self):
        return bool(self.refusals)


def walk(name, parties, comp, path=()):
    """Transitive inheritance walk. Records every route to every parent, so a
    diamond is visible rather than silently collapsed."""
    for edge in parties[name].get("inherits", []) or []:
        route = path + (name,)
        comp.edges.append((edge["party"], edge["kind"], edge["version"], route))
        comp.diamonds.setdefault((edge["party"], edge["kind"]), {}) \
            .setdefault(edge["version"], []).append(" -> ".join(route + (edge["party"],)))
        walk(edge["party"], parties, comp, route)


def resolve(name, parties, pubs):
    comp = Composition(name)
    walk(name, parties, comp)

    # 1. The diamond. Two routes to one parent at two versions is a conflict,
    #    not a coexistence. Refuse; never pick one quietly.
    for (parent, kind), by_version in sorted(comp.diamonds.items()):
        if len(by_version) > 1:
            routes = "; ".join(f"{v} via {' , '.join(p)}" for v, p in sorted(by_version.items()))
            comp.refusals.append(
                f"diamond: {parent} ({kind}) is inherited at {len(by_version)} versions -> {routes}")

    # 2. The baseline is inherited and cannot be dropped. A subclass may add a
    #    requirement. It may never drop one its parent declared.
    for parent, kind, version, _ in comp.edges:
        if kind != "controls":
            continue
        published = parties[parent]["publishes"]["versions"].get(version)
        if published is None:
            comp.refusals.append(f"{parent} publishes no version {version}")
            continue
        comp.baseline += [c for c in published["baseline"] if c not in comp.baseline]
    comp.baseline += [c for c in parties[name].get("requires", []) or [] if c not in comp.baseline]

    # 3. Gather implementations from every implementations parent.
    #
    #    HONEST LIMIT: `pubs` holds only platform's publications, because
    #    platform is the estate's ONLY implementations publisher today. With a
    #    second one this needs a per-party publication store. The conflict
    #    detection below is written for that case and fires now only on the two
    #    trees INSIDE platform, which is the same disagreement one level down.
    for parent, kind, version, _ in comp.edges:
        if kind != "implementations":
            continue
        for key, meta in pubs["impls"].items():
            src = f"{parent}@{version}:{meta['tree']}"
            prior = comp.effective.get(key)
            if prior is not None and prior["doc"] != meta["doc"]:
                # TWO SOURCES, ONE KEY, DIFFERENT CONTENT. This is the case
                # class inheritance would settle with most-derived-wins. There
                # is no most-derived here: these are peers. Refuse; do not pick.
                comp.rule_conflicts.append((key, prior["via_source"], src))
            comp.effective[key] = dict(meta, via=f"{parent}@{version}", via_source=src)
    if comp.rule_conflicts:
        comp.refusals.append(
            f"{len(comp.rule_conflicts)} rule(s) supplied by two sources with different content")

    for add in parties[name].get("overlay", {}).get("add", []) or []:
        comp.effective[(add["policy"], add["version"])] = {
            "action": add["action"], "tree": "overlay", "path": "(this party)",
            "installed": True, "via": name}

    # 4. Same version, different content, from two trees. The map's own open
    #    question, surfaced rather than decided.
    for (policy, version), meta in comp.effective.items():
        comp.collisions.setdefault(version, set()).add(meta["tree"])
    comp.collisions = {v: sorted(t) for v, t in comp.collisions.items() if len(t) > 1}

    # 5. Coverage. An uncovered control is an unimplemented abstract method.
    installed = {p for (p, v), m in comp.effective.items() if m["installed"]}
    declared = {p for (p, v) in comp.effective}
    for control in comp.baseline:
        claimed = pubs["mapping"].get(control.lower(), [])
        missing = [c for c in claimed if c not in declared]
        uninstalled = [c for c in claimed if c in declared and c not in installed]
        if not claimed:
            comp.uncovered.append((control, "no policy claims this control at all"))
        elif not any(c in installed for c in claimed):
            comp.uncovered.append((control, f"claimed by {claimed}; none of them is installed"))
        elif missing or uninstalled:
            # At least one live implementation exists, so the control is not
            # uncovered. But the claim is broader than the reality.
            comp.partial.append((control, missing, uninstalled))
    if comp.uncovered:
        comp.refusals.append(f"{len(comp.uncovered)} control(s) in the baseline have no live implementation")

    # 6. Divergence from an inherited rule.
    #
    #    TIGHTENING is just a restatement: a subclass may always be stricter.
    #
    #    WEAKENING IS NOT AN OVERRIDE AND IS NEVER AN EXEMPTION. A subclass that
    #    cannot meet an inherited rule does not get a pass and does not get to
    #    edit the rule. It declares the inability, the £ prices the residual
    #    against THIS party's appetite band and its pinned threat feed, and the
    #    composition renders a CAGE. Deny is the bottom rung of that ladder,
    #    reached by the money, never by a carve-out.
    for r in parties[name].get("overlay", {}).get("restate", []) or []:
        inherited = comp.effective.get((r["policy"], r["version"]))
        if not inherited:
            continue
        if STRICTNESS[r["action"]] >= STRICTNESS[inherited["action"]]:
            comp.effective[(r["policy"], r["version"])] = dict(
                inherited, action=r["action"], via=f"{name} (tightened)")
        else:
            # Re-read as what it actually is: a declared inability to satisfy.
            comp.cannot_satisfy.append({
                "workload": r.get("workload", f"(any {name} workload)"),
                "policy": r["policy"], "version": r["version"],
                "why": r.get("why", f"restated {inherited['action']} as {r['action']}"),
                "scenario": r.get("scenario"),
            })
    comp.cannot_satisfy += parties[name].get("overlay", {}).get("cannot_satisfy", []) or []

    # 7. Retirement. A pin that left the array is an orphan, denied by the
    #    orphan-guard the array itself renders.
    for w in parties[name].get("workloads", []) or []:
        if w["pins"] not in pubs["live"]:
            comp.orphans.append(w)
    if comp.orphans:
        comp.refusals.append(
            f"{len(comp.orphans)} workload(s) pin a version the composed array no longer declares")

    # 8. Price every declared inability. THIS is what a subclass gets instead of
    #    an override: an informed cage, chosen by the £ from this party's own
    #    appetite band and its pinned threat feed.
    price_cages(comp, parties, pubs)
    return comp


def price_cages(comp, parties, pubs):
    if not comp.cannot_satisfy:
        return
    cage = pubs["cage"]
    band = pubs["bands"].get(comp.party)
    if band is None:
        comp.refusals.append(f"{comp.party} has no appetite band, so nothing can price its residual")
        return
    threat_pin = next((v for p, k, v, _ in comp.edges if k == "threat"), None)

    for want in comp.cannot_satisfy:
        if want.get("scenario"):
            scenario = json.loads((CLONE / "platform" / want["scenario"]).read_text())
            source = want["scenario"]
        elif threat_pin is None:
            # No named scenario and no threat parent: nothing can price this.
            # Refuse rather than invent a number for a cage that constrains a
            # real workload.
            comp.refusals.append(
                f"{want['workload']}: declared an inability with no scenario, and "
                f"{comp.party} inherits no threat parent to price it from")
            continue
        else:
            scenario = threat_scenario(threat_pin, comp.party)
            source = f"threat-register {threat_pin}"
        # mode="warn": the deviation is in place, which is exactly this case.
        decision = cage.select(scenario, comp.party, band, mode="warn")
        comp.cages.append(dict(decision, workload=want["workload"], why=want["why"],
                               priced_from=source))


# ---------------------------------------------------------------------------
# Render down: the hard constraint. Source-level only, flat per version.
# ---------------------------------------------------------------------------


PROVENANCE = ("policy-as-versioned.dev/inherited-from",
              "policy-as-versioned.dev/source-path")
COMPOSED_FOR = "policy-as-versioned.dev/composed-for"


def render(comp, policy, version):
    """Flatten one composed policy version to WHAT KYVERNO GETS TODAY.

    The whole inherited body is carried, not a summary of it: validations,
    matchConstraints, matchConditions. The composition adds exactly two
    annotations and one label, all advisory, none of which the engine reads
    (CONTEXT.md: advisory metadata). Strip those and you must be left with the
    committed file, byte for byte after parsing — render_is_faithful() asserts
    precisely that.
    """
    meta = comp.effective[(policy, version)]
    doc = copy.deepcopy(meta["doc"])
    # Only a ValidatingPolicy HAS an action. Writing validationActions onto a
    # MutatingPolicy or a GeneratingPolicy would invent a field the schema does
    # not have, and section 11 is what caught that.
    if doc.get("kind") == "ValidatingPolicy":
        doc["spec"]["validationActions"] = [meta["action"]]
    md = doc.setdefault("metadata", {})
    md.setdefault("labels", {})[COMPOSED_FOR] = comp.party
    md.setdefault("annotations", {}).update({
        PROVENANCE[0]: meta["via"],
        PROVENANCE[1]: meta["path"],
    })
    return doc


def render_is_faithful(comp, policy, version):
    """Strip the composition's additions; what remains must equal the committed
    file. This is the hard constraint, and it is asserted, not asserted-about."""
    meta = comp.effective[(policy, version)]
    stripped = copy.deepcopy(render(comp, policy, version))
    md = stripped["metadata"]
    md["labels"].pop(COMPOSED_FOR, None)
    for key in PROVENANCE:
        md.get("annotations", {}).pop(key, None)
    if not md.get("annotations"):
        md.pop("annotations", None)
    return stripped == meta["doc"], stripped


def report(comp, indent="    "):
    for r in comp.refusals:
        print(f"{indent}REFUSED: {r}")
    for control, why in comp.uncovered:
        print(f"{indent}  uncovered {control}: {why}")
    for control, missing, uninstalled in comp.partial:
        detail = []
        if missing:
            detail.append(f"{missing} named but no such policy exists")
        if uninstalled:
            detail.append(f"{uninstalled} exists but the version array never installs it")
        print(f"{indent}  OVERCLAIMED {control}: " + "; ".join(detail))
    for w in comp.orphans:
        print(f"{indent}  orphan {w['name']} pins {w['pins']}")
    for (policy, version), a, b in comp.rule_conflicts:
        print(f"{indent}  conflict {policy}@{version}: {a} vs {b}")
    if not comp.refused:
        print(f"{indent}composes cleanly")


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------


def main():
    if not (CLONE / "platform").is_dir():
        print("SKIP: .estate-clone/platform absent. Run ./clone-estate.sh first.")
        return 0

    failures = []
    pubs = load_publications()
    parties = load_parties()

    rule("0. WHAT PLATFORM REALLY PUBLISHES — read from .estate-clone")
    print(f"    version array declares: {pubs['live']}")
    for (p, v), m in sorted(pubs["impls"].items()):
        mark = "installed" if m["installed"] else "NOT installed by the array"
        print(f"    {p:26} {v:7} {m['action']:6} {m['tree']:13} {mark}")
    print("\n    control -> the policies claimed as its evidence:")
    for c, ids in sorted(pubs["mapping"].items()):
        print(f"    {c:22} {ids}")

    rule("1. THE INHERITANCE GRAPH — driftwood, as the estate really pins it")
    comp = resolve("driftwood", parties, pubs)
    for parent, kind, version, route in comp.edges:
        print(f"    {' -> '.join(route + (parent,)):34} {kind:16} @{version}")
    routes = comp.diamonds[("nist", "controls")]
    print(f"\n    nist is reached by {sum(len(r) for r in routes.values())} routes, "
          f"at {len(routes)} version(s): directly, and through platform")
    print("    (twice, because platform is itself inherited for two different")
    print("    kinds). That is the diamond, and it is live today.")
    print("    ONE version across every route, so there is nothing to refuse.")
    print("    Section 5 splits it and shows what happens then.")
    if sum(len(r) for r in routes.values()) < 2:
        failures.append("expected nist to be reached by more than one route")
    if len(routes) != 1:
        failures.append("the baseline composition should reach nist at exactly one version")

    rule("2. BASELINE COMPOSITION — what driftwood must satisfy")
    print(f"    inherited baseline: {comp.baseline}")
    print("\n    A subclass inherits its parent's requirements and may add to them.")
    print("    It may never drop one. That is the abstract-method contract.")

    rule("3. COVERAGE — four real gaps, found by composing, not by review")
    report(comp)
    print("\n    All four are facts about the estate as it stands today:")
    print("    1. cm-6's only claimed evidence is 'require-policy-version'. No")
    print("       ValidatingPolicy of that name exists anywhere in the estate.")
    print("       The real guard is named policy-version-orphan-guard. The name")
    print("       appears only in the OSCAL map and in a hand-authored fixture")
    print("       PolicyReport, which is why the up-flow passes today.")
    print("    2. ac-6 claims may-run-root-if-attested, which is real, but it")
    print("       lives in policy/policies/ and the version array only ever")
    print("       reconciles distribution/policies/. Flux never installs it.")
    print("       ac-6 is still covered, by require-nonroot. The CLAIM is wider")
    print("       than the reality, which is why this is OVERCLAIMED, not")
    print("       uncovered. It would become uncovered the moment require-nonroot")
    print("       moved trees.")
    print("    3. LATENT, not live. The component definition writes control ids")
    print(f"       {pubs['raw_control_ids']}, and the")
    print("       catalogue writes them lowercase and UNPREFIXED ('ac-6').")
    print("       Two mismatches, not one: case AND the 'nist-800-53:' prefix.")
    print("       Nothing in the estate resolves one against the other today, so")
    print("       nothing is broken yet. It breaks the resolver this spike")
    print("       proposes. Be clear about what this spike does NOT do: it folds")
    print("       case against its OWN baseline in material/parties/nist.yaml,")
    print("       which was hand-authored in the prefixed form. The cure is")
    print("       untested against the real catalogue.")
    print("    4. Nothing in the estate declares a baseline. nist ships 1196")
    print("       controls. The estate implements two. The baseline in")
    print("       material/parties/nist.yaml is this spike's proposal, not a")
    print("       reading of an existing file. It is needed for the ac-6.10 case")
    print("       (a required control nothing claims). Gaps 1 and 2 need no")
    print("       baseline: a lint of the component definition against the")
    print("       policy trees finds both. Composition is not the only way.")
    if not comp.uncovered:
        failures.append("expected cm-6 uncovered in the live estate")
    if not comp.partial:
        failures.append("expected ac-6 overclaimed in the live estate")
    if not any(c.isupper() for c in "".join(pubs["raw_control_ids"])):
        failures.append("expected the uppercase control ids in the component definition")

    rule("4. SAME VERSION, TWO TREES — CLOSED by the estate, not by this spike")
    for version, trees in sorted(comp.collisions.items()):
        print(f"    version {version} is declared by {len(trees)} trees: {trees}")
    print("    (none)")
    print("\n    The first pass found v1.0.0 declared by BOTH distribution/ and")
    print("    policy/, each self-scoping on the same claim, and raised it as the")
    print("    map's open question. cs-16 then DELETED policy/policies/ and folded")
    print("    may-run-root-if-attested's widening into require-nonroot@2.0.1.")
    print("    The collision is gone because the tree is gone. cs-22 kept the gate")
    print("    rule that refuses it, so a reappearance still fails. Recorded as an")
    print("    answered question, not a passing check.")
    if comp.collisions:
        failures.append("policy/policies/ is deleted, so no collision should remain")

    rule("5. SCENARIO — the regulator bumps. A minor upstream, a break downstream")
    s = copy.deepcopy(parties)
    for e in s["driftwood"]["inherits"]:
        if e["party"] == "nist":
            e["version"] = "2.0.0"
    c2 = resolve("driftwood", s, pubs)
    print("    driftwood moves its nist pin to 2.0.0. platform stays on 1.0.0.")
    report(c2)
    print("\n    Two refusals at once, and they are different failures. The diamond")
    print("    splits, AND the new control ac-6.10 has no implementation anywhere.")
    print("    At nist this bump only ADDS a control. Nothing existing changed.")
    print("    At driftwood it breaks the build. The bump is institution-relative,")
    print("    which is ticket cs-02's finding seen from the other side.")
    if len(c2.refusals) < 2:
        failures.append("scenario 5 should refuse for two distinct reasons")

    rule("6. SCENARIO — the aligned bump. Both parents move together")
    s = copy.deepcopy(parties)
    for p in ("driftwood", "platform"):
        for e in s[p]["inherits"]:
            if e["party"] == "nist":
                e["version"] = "2.0.0"
    c3 = resolve("driftwood", s, pubs)
    print("    platform and driftwood both move to nist 2.0.0.")
    report(c3)
    print("\n    The diamond closes. The uncovered control does not. Aligning the")
    print("    pins was never the fix; someone has to implement ac-6.10.")
    if any("diamond" in r for r in c3.refusals):
        failures.append("scenario 6 should close the diamond")

    rule("7. SCENARIO — platform retires a version. Invisible in any policy diff")
    live = [v for v in pubs["live"] if v != "1.0.0"]
    retired = dict(pubs, live=live,
                   impls={k: dict(m, installed=m["tree"] == "distribution" and k[1] in live)
                          for k, m in pubs["impls"].items()})
    c4 = resolve("driftwood", parties, retired)
    print("    platform deletes 1.0.0 from the version array. driftwood's own")
    print("    workload pins 1.0.0 (gitops/apps/version-configmap.yaml).")
    report(c4)
    print("\n    No policy BODY changed. No diff of any rule shows this. The")
    print("    orphan-guard refuses driftwood's workload at admission, so for")
    print("    driftwood this is a major. For platform it is one array element.")
    if not c4.orphans:
        failures.append("scenario 7 should orphan driftwood's workload")

    rule("8. A SUBCLASS CANNOT SATISFY AN INHERITED RULE — it is caged, not excused")
    print("    A legacy till needs CAP_NET_RAW. It cannot meet condition C in")
    print("    may-run-root-if-attested. It does not get an override and it does")
    print("    not get an exemption. The £ prices the residual against THIS")
    print("    party's appetite band and picks the loosest cage that fits.")
    print("    Priced from the estate's own scenario for exactly this deviation:")
    print("    policy/scenarios/driftwood-root-residual.json\n")
    print(f"    {'party':11} {'band £/yr':>10}  {'tier':11} {'action':6} {'residual':>9} {'+controls':>10} {'= TCoR':>9}")
    tiers = {}
    for org in ("driftwood", "tuppence", "ludlow"):
        s = copy.deepcopy(parties)
        s[org]["overlay"]["cannot_satisfy"] = [{
            "workload": f"{org}-legacy-till", "why": "needs CAP_NET_RAW; cannot meet condition C",
            "scenario": "policy/scenarios/driftwood-root-residual.json"}]
        c = resolve(org, s, pubs)
        d = c.cages[0]
        tiers[org] = d["tier"]
        money = (f"{d['tcor']['residual']:>9,.0f} {d['tcor']['cost_of_controls']:>10,.0f} "
                 f"{d['tcor']['tcor']:>9,.0f}") if d["action"] == "Cage" else "  loss path closed"
        print(f"    {org:11} {pubs['bands'][org]:>10,}  {d['tier']:11} {d['action']:6} {money}")
    print("\n    The band is compared against the RESIDUAL, not the TCoR: the cage's")
    print("    own run-cost is a booked cost, not retained risk. tuppence's TCoR")
    print("    sits over its band for that reason and is still proportionate.")
    print("\n    Same rule, same inability, three answers. That is proportionality,")
    print("    not a favour. Nobody asked, and nobody was granted anything.")
    print("\n    Two things this scenario does NOT prove, said plainly:")
    print("    * tuppence fits baseline by about £48 on a Monte-Carlo output.")
    print("      One knob twitch flips this table's centrepiece.")
    print("    * The rule it cannot meet is may-run-root-if-attested, which")
    print("      gap 2 above proves the version array NEVER INSTALLS. It cages")
    print("      against a rule not in force. The mechanism is sound; this")
    print("      particular subject is not yet real.")
    if not (tiers["driftwood"] == "baseline" and tiers["ludlow"] == "quarantine"):
        failures.append("scenario 8: the band should change the tier")

    rule("9. INFORMED — a bump to a PRICING parent re-prices every cage below it")
    print("    ico publishes a signed, versioned penalty schema and no rules at")
    print("    all. Bumping it is a dependency bump like any other. Here the")
    print("    SAME uk-gdpr lower-tier exposure is priced at v1 and at v2,")
    print("    through ico's OWN converter. lower-tier is the entry v2 actually")
    print("    changed, so this is the real diff, not a chosen one.\n")
    ico_conv = CLONE / "ico" / "schema" / "to_fair_scenario.py"
    priced = []
    for v in ("v1", "v2"):
        sc = json.loads(subprocess.run(
            [sys.executable, str(ico_conv), "build",
             str(CLONE / "ico" / "schema" / v / "penalty-schema.json"),
             "uk-gdpr", "lower-tier"], capture_output=True, text=True, check=True).stdout)
        d = pubs["cage"].select(sc, "driftwood", pubs["bands"]["driftwood"], mode="warn")
        priced.append(d["uncaged_residual"])
        print(f"    ico penalty-schema {v}  ->  uncaged £{d['uncaged_residual']:>12,.0f}   {d['action']}")
    print(f"    the bump moves the priced exposure by £{abs(priced[0] - priced[1]):,.0f}.")
    print("    v2's changelog says why: it adds the Doorstep Dispensaree notice,")
    print("    a smaller real case that pulls the lower-tier mode down.")

    print("\n    Same for the threat register, which raises tuppence's LEF at v2:")
    tp = []
    for v in ("v1", "v2"):
        d = pubs["cage"].select(threat_scenario(v, "tuppence"), "tuppence",
                                pubs["bands"]["tuppence"], mode="warn")
        tp.append(d["uncaged_residual"])
        print(f"    threat-register {v}     ->  uncaged £{d['uncaged_residual']:>12,.0f}   {d['action']}")

    print("\n    HONEST RESULT: the pricing parents are genuinely consumed and the")
    print("    numbers genuinely move. THE DECISION DOES NOT. Every subject above")
    print("    sits far over every band in the estate, so both versions land on")
    print("    the same rung. On the estate's real feeds and real bands, NO feed")
    print("    bump changes a cage decision. The wiring is proved; the claim")
    print("    'a feed bump re-tunes every cage below it' is proved for the PRICE")
    print("    and NOT for the outcome. Do not read more into it than that.")
    if not (priced[0] != priced[1] and tp[0] != tp[1]):
        failures.append("section 9: a feed bump should move the priced exposure")

    rule("9b. BUT A FEED MUST NOT APPLY THE CHANGE ITSELF — ADR-0006 / ADR-0010")
    print("    The EOL feed is time-varying: to_fair_scenario.py ramps LEF by how")
    print("    far --as-of sits past the eol_date. Nothing is edited at all, and")
    print("    the price still moves:\n")
    conv = CLONE / "platform" / "feeds" / "to_fair_scenario.py"
    feed = CLONE / "platform" / "feeds" / "eol" / "v1" / "eol-feed.json"
    seen = []
    for as_of in ("2025-10-31", "2026-08-21", "2027-08-21", "2029-08-21"):
        sc = json.loads(subprocess.run(
            [sys.executable, str(conv), "eol", str(feed), "python-3.9", "--as-of", as_of],
            capture_output=True, text=True, check=True).stdout)
        d = pubs["cage"].select(sc, "driftwood", pubs["bands"]["driftwood"], mode="warn")
        seen.append(d["tier"])
        print(f"    as-of {as_of}  ->  proposed tier {d['tier']:11} {d['action']}")
    print("\n    An earlier draft of this spike called that \"the cage tightens on")
    print("    its own\" and treated it as a feature. THAT WOULD VIOLATE A DECIDED")
    print("    ADR. ADR-0006's later extension is explicit: timed nudges to humans")
    print("    are fine \"as long as nothing timed ever changes an admission")
    print("    verdict on its own, and every resulting change still lands via a")
    print("    reviewed, human-merged PR\". ADR-0010 is named for the same rule:")
    print("    sunset is SCHEDULED PROPOSALS, NOT APPLICATION. And cs-02 settled")
    print("    that the cage SPEC is the verdict, so a self-tightening cage is a")
    print("    timed verdict change, not a nudge.")
    print("\n    So the correct output of every row above is a PROPOSED tier that")
    print("    the agent governance layer raises as a reviewed PR. It prompts")
    print("    editorial review; it never edits enforcement. The word 'proposed'")
    print("    above is doing real work, and this spike does not implement the")
    print("    proposer.")
    if seen != sorted(seen, key=["baseline", "restricted", "quarantine", "deny"].index):
        failures.append("scenario 9b: the proposed tier should only tighten as the component ages")

    rule("10. RENDER DOWN — the hard constraint still holds")
    clean = resolve("driftwood", parties, pubs)
    # may-run-root-if-attested was here on the first pass. cs-16 deleted
    # policy/policies/ and folded its widening into require-nonroot@2.0.1.
    for policy, version in (("require-nonroot", "1.0.0"), ("require-nonroot", "2.0.0"),
                            ("require-nonroot", "2.0.1")):
        faithful, _ = render_is_faithful(clean, policy, version)
        print(f"    {policy}@{version}: strip the composition's additions -> "
              f"equals the committed file: {'YES' if faithful else 'NO'}")
        if not faithful:
            failures.append(f"render of {policy}@{version} is not faithful")
    doc = render(clean, "require-nonroot", "2.0.0")
    print("\n" + yaml.safe_dump(doc, sort_keys=False, width=100).rstrip())
    print("\n    The WHOLE body is carried: validations, matchConstraints,")
    print("    matchConditions. The composition adds one label and two")
    print("    annotations, all advisory, none read by the engine. Strip them and")
    print("    the committed file is what is left, which is what the check above")
    print("    asserts. Flat, per version, self-scoping on matchConditions, so")
    print("    runtime inheritance stays ruled out and multi-version coexistence")
    print("    is untouched.")
    if "objectSelector" in yaml.safe_dump(doc):
        failures.append("render leaked an objectSelector")

    rule("11. TICKET 06 — THE OTHER FIVE. The whole live set, not 3 of 8")
    version = pubs["live"][-1]
    members, kinds = load_live_set(version)
    print(f"    the version tree v{version} ships: {kinds}")
    print(f"\n    {'family':22} {'member':30} {'kind':18} declares")
    for (family, base), m in sorted(members.items()):
        print(f"    {family:22} {base:30} {m['kind']:18} "
              f"{m['declared'] or '— (platform tag)'}")

    live = Composition("driftwood")
    for (family, base), m in members.items():
        # The action is read from the member itself. A mutate and a generate
        # have none at all, which is finding 1 below.
        actions = m["doc"]["spec"].get("validationActions") or ["Audit"]
        live.effective[(base, version)] = dict(
            m, action=actions[0], installed=True, tree="distribution",
            via=f"platform@{version}")
    print("\n    render down, every member, every kind:")
    for (family, base), m in sorted(members.items()):
        faithful, _ = render_is_faithful(live, base, version)
        print(f"    {base:30} {'FAITHFUL' if faithful else 'NOT FAITHFUL'}")
        if not faithful:
            failures.append(f"render of {base} is not faithful")

    print(f"""
    FOUR OF THE FIVE ARE NO LONGER UNVERSIONED. cs-03 counted eight live
    policies, five carrying no version. cs-12's render-version-tree.py now
    emits cage-tier, cage-netpol, stamp-posture and posture-trust-boundary
    into EVERY version tree, self-scoped on the claim. They compose exactly
    as require-nonroot does, and they render back down byte-identical. The
    ticket's premise was true when it was written and the estate has since
    overtaken it.

    THE FIFTH CANNOT BE VERSIONED, AND THAT IS CORRECT. The orphan guard is
    the aggregate OVER the array, so it cannot self-scope to one claim. cs-22
    gave it the `platform-machinery` identity: numbered by the platform tag.
    Composition must carry a second numbering axis, not force it onto the
    first. This section renders it from the array through the estate's own
    render-orphan-guard.py, so the simulated list-membership check the first
    pass admitted to is now gone.

    WHAT COMPOSING THEM CHANGED, and it is a real defect in this spike:
    1. An ACTION IS A VALIDATINGPOLICY CONCEPT. render() wrote
       spec.validationActions unconditionally, which invents a field on a
       MutatingPolicy and a GeneratingPolicy. Fixed above. The consequence is
       bigger than the fix: the Audit < Deny strictness ladder that
       overlay.restate compares on has NO MEANING for {len([m for m in members.values() if m['kind'] != 'ValidatingPolicy'])} of the
       {len(members)} members. A subclass cannot tighten a mutate. What it can do to a
       cage is change the TIER, which is a label the £ sets upstream — so
       ticket 05's proposer, not the overlay, is the only legal path.
    2. THE IDENTITY LABEL IS A FAMILY, NOT A KEY. `graded-enforcement` covers
       cage-tier, cage-netpol and three PriorityClasses; `posture` covers two
       policies. load_publications() keys on (label, version), so a second
       member of one family SILENTLY OVERWRITES the first. It has not fired
       yet only because one ValidatingPolicy per family per version exists.
       That is luck. cs-22 already settled the cure for the gate — key on
       identity AND the name with its version stripped — and the resolver
       needs the same key. This section uses it.
    3. TWO OF THE EIGHT MUTATE, so composition order is now observable.
       stamp-posture writes the label posture-trust-boundary validates, and
       cage-tier writes the label cage-netpol generates from. Rendering flat
       per version does not express that, and Kyverno's webhook ordering is
       what makes it work. Composition inherits that dependency without
       stating it. Not a defect found today, but it is the first thing a
       second implementations publisher would break.

    ONE HONEST LIMIT ON THE CHECK ABOVE. Five of the six render back down to a
    COMMITTED file. The orphan guard has no committed rendered form — the repo
    holds the Go template inside versions.yaml — so its row compares against
    the estate's own render-orphan-guard.py output. That proves composition
    carries the guard unchanged. It does NOT prove the twin matches what
    flux-operator renders in-cluster. verify-orphan-guard.sh covers that, and
    this spike does not run a cluster.""")
    if len(members) != 6:
        failures.append("expected 5 versioned admission members plus the orphan guard")
    if not any(m["kind"] == "MutatingPolicy" for m in members.values()):
        failures.append("expected the mutating half of the live set to compose")
    if members[("platform-machinery", "policy-version-orphan-guard")]["declared"] is not None:
        failures.append("the orphan guard must carry no policy-version")

    rule("VERDICT")
    print(VERDICT)

    if failures:
        print("\nSELF-CHECK FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("self-check: all assertions held")
    return 0


VERDICT = """\
  Cross-party inheritance is a REAL and MISSING layer. The earlier spike
  answered a narrower question and does not settle this one.

  It is now its own map (.scratch/policy-composition/). computed-semver takes
  exactly one fact from it: the bump is a property of a composition, so the
  gate computes it after composition.

  What composition is, in this estate. Parents are of DIFFERENT KINDS, and
  that is the part a flat pin model cannot express:
    nist       CONTROLS          what must hold. The abstract base.
    platform   IMPLEMENTATIONS   how. The concrete class.
    ico        PRICING           prices the consequence. No rules at all.
    feeds      THREAT            moves the price. No rules at all.
    driftwood  (adopter)         the subclass, and the diamond.

  Four gaps fell out of composing what is already committed, before any
  scenario ran. Two of them a plain lint would also find, and saying otherwise
  would be self-serving:
    * cm-6's claimed evidence names a policy that does not exist. (A lint
      finds this. Composition is not required.)
    * ac-6's second implementation is never installed by the version array.
      (A lint finds this too.)
    * the component definition's control ids match neither the catalogue's
      case nor its lack of a prefix. LATENT: nothing resolves them today.
    * no baseline is declared anywhere. THIS one needs composition: it is what
      catches a required control that nothing claims at all.

  What it does to the bump, which is this map's business:
    * The bump is a property of a COMPOSITION, not of a file. A regulator's
      addition is a downstream build break. A retired array element is a
      downstream major with no policy diff at all.
    * cs-01's method is EXTENDED, not unchanged. Its verdict-movement half
      works as-is on the composed OLD and NEW sets, because composition is
      rendering. But a composition also refuses on COVERAGE — an uncovered
      control, a split diamond — with zero verdict movement. That is a second
      structural axis, exactly as cs-01's minor finding was a first.
    * The publisher still tags ONE bump, computed at the strictest band, with
      the per-institution matrix as evidence. cs-02 settled that and it is not
      reopened here. What composition adds is the mechanism BEHIND that
      matrix: the per-adopter computation that the matrix reports.

  What a subclass gets INSTEAD of an override:
    * Nothing is ever excused. A subclass that cannot meet an inherited rule
      declares the inability. It does not edit the rule and it does not ask a
      favour. The estate's own cage.py prices the residual against THAT
      party's appetite band and picks the loosest cage that fits. Deny is the
      bottom rung of that ladder, reached by the money.
    * So the same rule and the same inability give three different answers
      across driftwood, tuppence and ludlow. That is proportionality, and that
      case needs no override semantics at all.
    * BUT THAT IS ONE CASE, NOT THE GENERAL ONE. Caging settles a CHILD that
      cannot meet a parent. It says nothing about TWO PARENTS whose rules
      disagree, which is the case override semantics exist for. This spike now
      REFUSES that instead of picking silently, and it is untested across
      parties because the estate has only one implementations publisher.
      Saying "divergence is priced, not merged" would fuse two different
      mechanisms: the conflict is refused, and what is priced is not it.
    * INFORMED means the parents that move the price are parents of their own
      kinds: a signed, versioned penalty schema, a threat register, a CVE
      feed, an EOL feed. None of them ships a rule. Section 9 proves the
      wiring: a bump to one moves the priced exposure with no policy edit. It
      also proves the limit — on the estate's REAL feeds and REAL bands, no
      bump changes a cage DECISION. Price moved; outcome did not.

  A LINE THIS MODEL MUST NOT CROSS:
    * A feed may re-price. It may NOT apply. ADR-0006's extension allows timed
      nudges only "as long as nothing timed ever changes an admission verdict
      on its own, and every resulting change still lands via a reviewed,
      human-merged PR". ADR-0010 says the same: scheduled PROPOSALS, not
      application. cs-02 settled that the cage spec IS the verdict. So a cage
      that tightens itself as a component ages is a timed verdict change, and
      it is forbidden. The output is a PROPOSED tier for the agent governance
      layer to raise as a PR. This spike does not implement the proposer.

  Constraints that held:
    * Source-level only. The render is flat, per version, self-scoping on
      matchConditions. Multi-version coexistence is untouched.
    * The baseline is inherited and cannot be dropped by a subclass.
    * No exemption exists anywhere in this model, at any scope, under any name.\
"""


if __name__ == "__main__":
    sys.exit(main())
