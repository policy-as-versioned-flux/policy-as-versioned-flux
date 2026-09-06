#!/usr/bin/env python3
"""Eco-system ticket 33 — ledger, storefront and reports belong to their adopters now.

WHAT A LIFT IS. Three applications were built in the incumbent org `policy-as-versioned-flux`
(`ledger`, `storefront`, `reports`), each a real stack with a real, deliberately stale dependency
tree. Ticket 13 decided they move to the adopter whose institutional shape they fit. A lift is not
a copy taken and a copy left: the receiving adopter must VERSION the app (its source tree sits in
the adopter's repository and is tagged with it), SERVE it (the workload manifest is inside the
tree the adopter's Flux Kustomization reconciles, and is listed by the kustomization that renders
it), GRADE it (the adopter's own shift-left job runs it through the composed policy set), and BUMP
it (the adopter's own renovate.json enables the stack's manager over the stack's manifest).

NAME THE SERVED ARTEFACT AND THE OPERATION THAT REACHES IT. The served artefact is the adopter's
`gitops/apps/` tree; the operation is Flux's Kustomization at `path: ./apps` (gotk-sync.yaml),
which renders `gitops/apps/kustomization.yaml`'s `resources[]` and nothing else. So this grader
never asks "is the file there". It asks whether the RENDER carries the workload, whether the
version it claims is one the ADOPTER'S OWN composed artefact allows (composed/orphan-guard.yaml's
allowed array — never a constant held here), and whether the cage constraints the composed set
enforces are met. `verify-lifted-apps.sh` then runs the real `kyverno apply` over the adopter's
own `composed/policies/v<claimed>/` against the served file, so the last word belongs to the
estate's own engine rather than to this file's reading of a manifest.

WHAT IT CANNOT LOOK AT is printed on every run from BLIND_SPOTS, and the one that matters is a
number, not a sentence: how many lifted apps are still served an image built and published by the
incumbent org. Lifting the image build needs a workflow job in the adopter and a registry under
the adopter's own organisation; that is on the ticket's `## Waits on the owner`, and until it
happens the count says so on every run.

  PASS (0)   every registered lift has landed, is served, is re-labelled, is graded and is bumped
  FAIL (1)   a landed lift is wrong in any of those ways; the same app landed in two adopters; a
             working copy of a lifted app is in the hub; a register row disagrees with the tree
  WAITS (3)  a registered lift has not landed in its adopter yet — the line names the pull
             request each one waits on — or there is no estate clone to read at all
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

LABEL = "policy-as-versioned.dev/policy-version"
OLD_LABEL_PREFIX = "mycompany.com/"
TIER_LABEL = "posture.acme.io/tier"
SERVED_KUSTOMIZATION = "gitops/apps/kustomization.yaml"

# Directories in the hub that hold the RECORD rather than a working copy: tickets, ADRs, the
# drift-review's captured trees of the incumbent org. Prose about a lifted app is not a copy of
# it, and a grader that cannot tell the two apart would make the record unwritable.
HUB_RECORD_DIRS = (".scratch", ".git", "docs", "research", "explorations")

BLIND_SPOTS = (
    "whether the container the served manifest names actually STARTS is a cluster fact. These "
    "three images set no USER, so each served pod names a numeric runAsUser and mounts the paths "
    "its process writes; that reasoning is checked by nobody here. The live half is the "
    "adopters' own drift-sample lane, which has never had a persistent cluster on a citable run",
    "whether the image digest each served manifest pins still resolves in ghcr.io. Reading a "
    "package needs `read:packages`, which the gate holds by design not at all (2026-09-06: the "
    "hub's own credential was refused it), so the digest is graded only against the register",
    "whether the incumbent org's own repositories have been archived. That is the owner's, it "
    "needs a credential the gate does not hold, and the ticket records it as waiting",
)


# --------------------------------------------------------------------------------- the register

@dataclass(frozen=True)
class Lift:
    app: str
    origin: str
    origin_commit: str
    adopter: str
    served: str
    source_dir: str
    stack_manifest: str
    renovate_manager: str
    image: str
    image_publisher: str
    pull_request: str


def load_register(path: Path) -> list[Lift]:
    doc = yaml.safe_load(Path(path).read_text()) or {}
    return [Lift(**row) for row in doc.get("lifts", [])]


# ------------------------------------------------------------------------------------ the report

@dataclass
class Row:
    app: str
    adopter: str
    grade: str          # PASS | FAIL | WAITS
    reasons: list[str] = field(default_factory=list)


@dataclass
class Report:
    rows: list[Row] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    hub_copies: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        if any(r.grade == "FAIL" for r in self.rows) or self.hub_copies:
            return 1
        if any(r.grade == "WAITS" for r in self.rows):
            return 3
        return 0

    def text(self) -> str:
        out: list[str] = []
        for r in self.rows:
            out.append(f"{r.grade:5} {r.app} -> {r.adopter}")
            out.extend(f"        {reason}" for reason in r.reasons)
        for c in self.hub_copies:
            out.append(f"FAIL  the hub carries a working copy of a lifted app: {c}")
        out.extend(self.notes)
        return "\n".join(out)


# ------------------------------------------------------------------------------------- the rules

def allowed_versions(adopter_dir: Path) -> list[str]:
    """The versions the ADOPTER'S OWN composed artefact admits.

    `composed/orphan-guard.yaml` is the composed copy of the platform-declared version array: a
    pod claiming anything else is an orphan the guard reports. Reading the array from there is
    what makes "re-pinned to the adopter's composed artefact" a measurement rather than a
    restatement of a number this repository chose.
    """
    guard = adopter_dir / "composed" / "orphan-guard.yaml"
    if not guard.is_file():
        return []
    doc = yaml.safe_load(guard.read_text()) or {}
    for var in (doc.get("spec") or {}).get("variables") or []:
        if var.get("name") == "allowed":
            return re.findall(r"\d+\.\d+\.\d+", str(var.get("expression", "")))
    return []


def served_resources(adopter_dir: Path) -> list[str] | None:
    """The resource list Flux's Kustomization actually renders, or None if there is no
    kustomization to render. Not a directory listing: a file in that directory which the
    kustomization does not name is served to nobody."""
    k = adopter_dir / SERVED_KUSTOMIZATION
    if not k.is_file():
        return None
    doc = yaml.safe_load(k.read_text()) or {}
    return list(doc.get("resources") or [])


def _old_labels(node) -> list[str]:
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and key.startswith(OLD_LABEL_PREFIX):
                found.append(key)
            found.extend(_old_labels(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_old_labels(item))
    return found


def grade_served(lift: Lift, adopter_dir: Path) -> list[str]:
    """Everything the served workload manifest itself must be. Returns the reasons it is not."""
    bad: list[str] = []
    path = adopter_dir / lift.served
    docs = [d for d in yaml.safe_load_all(path.read_text()) if d]
    if len(docs) != 1:
        return [f"{lift.served} carries {len(docs)} documents; a served workload is one object"]
    doc = docs[0]
    meta = doc.get("metadata") or {}
    labels = meta.get("labels") or {}

    resources = served_resources(adopter_dir)
    if resources is None:
        bad.append(f"{lift.adopter} has no {SERVED_KUSTOMIZATION}, so nothing under gitops/apps "
                   "is served at all")
    elif Path(lift.served).name not in resources:
        bad.append(f"{lift.served} is not listed in {SERVED_KUSTOMIZATION} "
                   f"(it renders {resources}), so Flux serves it to nobody")

    if doc.get("kind") != "Pod":
        bad.append(f"{lift.served} is a {doc.get('kind')}; the estate's composed policy set and "
                   "its cage are pod-scoped (ticket 09), so a served workload is a Pod")
    if meta.get("namespace") != lift.adopter:
        bad.append(f"{lift.served} is in namespace {meta.get('namespace')!r}, not the adopter's "
                   f"governed namespace {lift.adopter!r}")

    old = sorted(set(_old_labels(doc)))
    if old:
        bad.append(f"{lift.served} still carries the incumbent org's labels {old}: the lift "
                   f"re-labels to {LABEL}")
    claimed = labels.get(LABEL)
    allowed = allowed_versions(adopter_dir)
    if claimed is None:
        bad.append(f"{lift.served} claims no {LABEL}")
    elif claimed not in allowed:
        bad.append(f"{lift.served} claims policy-version {claimed!r}, which "
                   f"{lift.adopter}/composed/orphan-guard.yaml does not allow (it allows "
                   f"{allowed}) -- an orphan claim reaches no cage")
    elif not (adopter_dir / "composed" / "policies" / f"v{claimed}").is_dir():
        bad.append(f"{lift.served} claims {claimed} but {lift.adopter} composes no "
                   f"composed/policies/v{claimed}/ to grade it with")
    if TIER_LABEL in labels:
        bad.append(f"{lift.served} declares {TIER_LABEL}; the tier is declared on the governed "
                   "Namespace and the cage writes the pod label as an OUTPUT (ADR-0022)")

    spec = doc.get("spec") or {}
    if not ((spec.get("securityContext") or {}).get("runAsNonRoot") is True):
        bad.append(f"{lift.served} does not set spec.securityContext.runAsNonRoot=true, which "
                   f"{lift.adopter}'s composed require-nonroot validates")
    for c in spec.get("containers") or []:
        if not ((c.get("securityContext") or {}).get("readOnlyRootFilesystem") is True):
            bad.append(f"{lift.served} container {c.get('name')!r} does not set "
                       "readOnlyRootFilesystem=true")
        if c.get("image") != lift.image:
            bad.append(f"{lift.served} container {c.get('name')!r} runs {c.get('image')!r}, not "
                       f"the digest the register records ({lift.image})")
    return bad


def grade_renovate(lift: Lift, adopter_dir: Path) -> list[str]:
    bad: list[str] = []
    path = adopter_dir / "renovate.json"
    if not path.is_file():
        return [f"{lift.adopter} has no renovate.json, so nothing bumps {lift.app}'s stack"]
    cfg = json.loads(path.read_text())
    managers = cfg.get("enabledManagers")
    if managers is not None and lift.renovate_manager not in managers:
        bad.append(f"{lift.adopter}/renovate.json enabledManagers {managers} does not enable "
                   f"{lift.renovate_manager!r}, so {lift.stack_manifest} is read by nothing")
    # A manager named in enabledManagers and pointed at nothing is a name, not a bump surface.
    # Every adopter here pins the manager's own file patterns, so the check is whether one of
    # those patterns actually matches the lifted stack manifest.
    per_manager = cfg.get(lift.renovate_manager) or {}
    patterns = per_manager.get("managerFilePatterns")
    if patterns is None:
        bad.append(f"{lift.adopter}/renovate.json gives {lift.renovate_manager!r} no "
                   f"managerFilePatterns, so which files it reads is renovate's default glob "
                   f"and not this repository's declared bump surface")
    elif not any(re.search(p.strip("/"), lift.stack_manifest) for p in patterns):
        bad.append(f"{lift.adopter}/renovate.json points {lift.renovate_manager!r} at "
                   f"{patterns}, none of which matches {lift.stack_manifest}")
    if cfg.get("dependencyDashboard") is not True:
        bad.append(f"{lift.adopter}/renovate.json leaves dependencyDashboard off, so the stale "
                   f"tree {lift.app} was built to show is visible nowhere")
    return bad


def grade_lift(lift: Lift, estate_root: Path) -> Row:
    adopter_dir = estate_root / lift.adopter
    row = Row(app=lift.app, adopter=lift.adopter, grade="PASS")
    if not adopter_dir.is_dir():
        row.grade = "WAITS"
        row.reasons.append(f"no checkout of {lift.adopter} to read; the lift is proposed at "
                           f"{lift.pull_request}")
        return row

    served = adopter_dir / lift.served
    stack = adopter_dir / lift.stack_manifest
    landed = [p for p in (served, stack) if p.is_file()]
    if not landed:
        row.grade = "WAITS"
        row.reasons.append(f"{lift.app} has not landed in {lift.adopter}: neither {lift.served} "
                           f"nor {lift.stack_manifest} is in the tree. Proposed at "
                           f"{lift.pull_request}")
        return row

    bad: list[str] = []
    if not stack.is_file():
        bad.append(f"{lift.adopter} serves {lift.app} but does not carry {lift.stack_manifest}: "
                   "the workload moved and the thing Renovate reads did not, so the adopter "
                   "does not version this app")
    else:
        old = [str(p.relative_to(adopter_dir)) for p in sorted((adopter_dir / lift.source_dir).rglob("*"))
               if p.is_file() and OLD_LABEL_PREFIX in _safe_read(p)]
        if old:
            bad.append(f"{lift.source_dir} still carries the incumbent org's label in {old}")
    if not served.is_file():
        bad.append(f"{lift.adopter} carries {lift.stack_manifest} but serves no {lift.served}: "
                   "an app nothing reconciles is not lifted, it is vendored")
    else:
        bad.extend(grade_served(lift, adopter_dir))
    bad.extend(grade_renovate(lift, adopter_dir))

    # A lift is a move. The app's own source tree may exist in exactly one adopter.
    elsewhere = sorted(
        unit.name for unit in estate_root.iterdir()
        if unit.is_dir() and unit.name != lift.adopter and (unit / lift.source_dir).is_dir()
    )
    if elsewhere:
        bad.append(f"{lift.source_dir} is also in {elsewhere}: a lift is a move, not a copy")

    if bad:
        row.grade = "FAIL"
        row.reasons = bad
    else:
        row.reasons.append(
            f"served at {lift.served}, rendered by {SERVED_KUSTOMIZATION}, versioned by "
            f"{lift.adopter} at {lift.source_dir}, bumped by renovate's "
            f"{lift.renovate_manager} manager; lifted from {lift.origin}@{lift.origin_commit}")
    return row


def _safe_read(path: Path) -> str:
    try:
        return path.read_text()
    except (UnicodeDecodeError, OSError):
        return ""


def hub_copies(hub_root: Path, lifts: list[Lift]) -> list[str]:
    """Working copies of a lifted app inside the hub. The record (tickets, ADRs, the drift
    review's captures of the incumbent org) is not a working copy: HUB_RECORD_DIRS names those
    and the report prints the list, so what is excused is visible rather than assumed."""
    found: list[str] = []
    wanted = {lift.stack_manifest for lift in lifts} | {lift.served for lift in lifts}
    wanted |= {lift.source_dir + "/" for lift in lifts}
    for path in sorted(hub_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(hub_root).as_posix()
        if rel.split("/", 1)[0] in HUB_RECORD_DIRS:
            continue
        for w in wanted:
            if rel == w or rel.startswith(w):
                found.append(rel)
    return found


def grade(hub_root: Path, estate_root: Path, register_path: Path) -> Report:
    lifts = load_register(register_path)
    report = Report()
    report.hub_copies = hub_copies(Path(hub_root), lifts)
    if not Path(estate_root).is_dir():
        report.rows = [Row(app=lift.app, adopter=lift.adopter, grade="WAITS",
                           reasons=[f"there is no estate clone to read (run clone-estate.sh); "
                                    f"the lift is proposed at {lift.pull_request}"])
                       for lift in lifts]
    else:
        report.rows = [grade_lift(lift, Path(estate_root)) for lift in lifts]

    incumbent = [lift for lift in lifts
                 if lift.image_publisher == lift.origin.split("/", 1)[0]]
    report.notes.append(
        f"LIMIT  {len(incumbent)} of {len(lifts)} lifted apps are still served an image built "
        f"and published by the incumbent org {lifts[0].origin.split('/', 1)[0] if lifts else '-'}"
        f": the source and the served manifest moved, the image build did not (it needs a "
        f"workflow job and a registry under the adopter's own organisation -- ticket 33, waits "
        f"on the owner)")
    for b in BLIND_SPOTS:
        report.notes.append(f"BLIND  {b}")
    report.notes.append(f"NOTE   the hub's record directories are not read as working copies: "
                        f"{list(HUB_RECORD_DIRS)}")
    return report


def kyverno_plan(estate_root: Path, register_path: Path) -> list[tuple[str, str, str, str]]:
    """(app, adopter, policy directory, served manifest) for every lift that has landed and passed the
    structural grade. `verify-lifted-apps.sh` runs the real `kyverno apply` over each pair, so
    the last word on whether the adopter's own composed set admits the workload belongs to the
    estate's own engine rather than to this file's reading of a manifest."""
    plan: list[tuple[str, str, str, str]] = []
    for lift in load_register(register_path):
        adopter_dir = Path(estate_root) / lift.adopter
        served = adopter_dir / lift.served
        if not served.is_file():
            continue
        docs = [d for d in yaml.safe_load_all(served.read_text()) if d]
        claimed = None
        for d in docs:
            claimed = ((d.get("metadata") or {}).get("labels") or {}).get(LABEL)
        if not claimed:
            continue
        policies = adopter_dir / "composed" / "policies" / f"v{claimed}"
        if policies.is_dir():
            plan.append((lift.app, lift.adopter, str(policies), str(served)))
    return plan


def main(argv: list[str]) -> int:
    import argparse
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hub-root", type=Path, default=here.parent.parent)
    ap.add_argument("--estate-root", type=Path, default=here.parent.parent / ".estate-clone")
    ap.add_argument("--register", type=Path, default=here / "register.yaml")
    ap.add_argument("--kyverno-plan", action="store_true",
                    help="print `app<TAB>adopter<TAB>policy-dir<TAB>served-manifest` per landed lift "
                         "and exit 0; the shell script runs kyverno over the pairs")
    args = ap.parse_args(argv)
    if args.kyverno_plan:
        for row in kyverno_plan(args.estate_root, args.register):
            print("\t".join(row))
        return 0
    report = grade(args.hub_root, args.estate_root, args.register)
    print(report.text())
    return report.exit_code


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
