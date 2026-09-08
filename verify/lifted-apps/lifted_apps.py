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

NAME THE SERVED ARTEFACT AND THE OPERATION THAT REACHES IT -- BY READING THEM, NOT BY NAMING
THEM. The operation is the adopter's own `gitops/flux-system/gotk-sync.yaml`: a GitRepository
pinned to `ref: {tag, commit}` and a Kustomization whose `spec.path` is the directory Flux
renders. Both are READ here, never assumed (review 2026-09-08, F1: the first cut held the path as
prose, and driftwood's file said `./apps` -- a directory its remote does not have -- while the
check said "served"). So:

  * `spec.path`, normalised, must be the directory the served manifest is in (`gitops/apps`), or
    the row FAILS by name: a path that resolves to nothing at the remote means the Kustomization
    never becomes Ready and the file this check reads is served to nobody;
  * membership of the kustomization's `resources[]` is graded TWICE -- at the checked-out tree
    (what a merge to main would serve once the pin moves) and at `git show <ref.tag>:<path>/
    kustomization.yaml` (what the GitRepository actually pins today). The second is not a pass or
    a fail; it is a COUNTED LIMIT printed on every run: how many lifts are listed at the checkout
    and absent from the pinned tree. Nothing bumps an adopter's self-pin (its renovate
    customManagers cover the parents only), so this number moves only when an adopter cuts a tag;
  * the version the manifest claims is measured against the ADOPTER'S OWN composed artefact
    (composed/orphan-guard.yaml's allowed array -- never a constant held here), and the cage
    constraints the composed set enforces are checked structurally. `verify-lifted-apps.sh` then
    runs the real `kyverno apply` over the adopter's own `composed/policies/v<claimed>/` plus its
    `composed/orphan-guard.yaml`, so the last word belongs to the estate's own engine -- at CREATE
    only, under the baseline dial, because that is all the CLI evaluates (see the shell script).

WHAT IT CANNOT LOOK AT is printed on every run from BLIND_SPOTS, and the limits that matter are
numbers, not sentences: how many lifted apps are still served an image built and published by the
incumbent org (lifting the build needs a workflow job and a registry under the adopter's own
organisation -- ticket 33 `## Waits on the owner`), and how many are absent from the pinned tree.

  PASS (0)   every registered lift has landed at the checkout, on the path its own gotk-sync.yaml
             reconciles, is listed there, is re-labelled, is graded and is bumped
  FAIL (1)   a landed lift is wrong in any of those ways; the same app landed in two adopters; a
             working copy of a lifted app is in the hub; a register row disagrees with the tree
  WAITS (3)  a registered lift has not landed in its adopter yet -- the line names the pull
             request each one waits on -- or there is no estate clone to read at all
"""
from __future__ import annotations

import fnmatch
import json
import os
import posixpath
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

LABEL = "policy-as-versioned.dev/policy-version"
OLD_LABEL_PREFIX = "mycompany.com/"
TIER_LABEL = "posture.acme.io/tier"
SERVED_DIR = "gitops/apps"
SERVED_KUSTOMIZATION = "gitops/apps/kustomization.yaml"
FLUX_SYNC = "gitops/flux-system/gotk-sync.yaml"

# Directories in the hub that hold the RECORD rather than a working copy: tickets, ADRs, the
# drift-review's captured trees of the incumbent org. Prose about a lifted app is not a copy of
# it, and a grader that cannot tell the two apart would make the record unwritable.
HUB_RECORD_DIRS = (".scratch", ".git", "docs", "research", "explorations")
# Directories that are not the hub's tree at all: the estate clone (other parties' trees, which
# is where the lifted apps are SUPPOSED to be), interpreters, dependency caches.
HUB_SKIP_DIRS = (".estate-clone", ".venv", "node_modules", "__pycache__", ".mypy_cache",
                 ".pytest_cache")

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
    "whether any adopter's composed set admits the workload at UPDATE. Every composed policy and "
    "the orphan guard declare CREATE+UPDATE; `kyverno apply` evaluates CREATE only, and no "
    "UPDATE-scoped evaluation exists anywhere in this estate",
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
    # A regular expression the stack manifest's CONTENT carries and nothing else in the estate
    # does (the pom's groupId+artifactId, the package's name, the pinned framework line). The
    # hub-copy rule matches on this anywhere under the hub's non-record directories, so a copy
    # parked at `spikes/ledger/pom.xml` is a copy (review 2026-09-08, F4).
    identity: str


def load_register(path: Path) -> list[Lift]:
    doc = yaml.safe_load(Path(path).read_text()) or {}
    return [Lift(**{k: str(v) for k, v in row.items()}) for row in doc.get("lifts", [])]


# ------------------------------------------------------------------------------------ the report

@dataclass(frozen=True)
class FluxSync:
    """What the adopter's own gotk-sync.yaml says Flux reads: the GitRepository's pin and the
    Kustomization's path. Read, never assumed."""
    path: str | None
    tag: str | None
    commit: str | None
    url: str | None


@dataclass(frozen=True)
class PinnedRead:
    """`git show <tag>:<path>/kustomization.yaml`, parsed for the served manifest.

    state: listed | absent | unreadable | unpinned
    """
    state: str
    tag: str | None
    resolved: str | None
    detail: str


@dataclass
class Row:
    app: str
    adopter: str
    grade: str          # PASS | FAIL | WAITS
    reasons: list[str] = field(default_factory=list)
    pinned: PinnedRead | None = None


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

    @property
    def pinned_absent(self) -> list[Row]:
        return [r for r in self.rows if r.pinned is not None and r.pinned.state == "absent"]

    @property
    def pinned_unreadable(self) -> list[Row]:
        return [r for r in self.rows
                if r.pinned is not None and r.pinned.state in ("unreadable", "unpinned")]

    def text(self) -> str:
        out: list[str] = []
        for r in self.rows:
            out.append(f"{r.grade:5} {r.app} -> {r.adopter}")
            out.extend(f"        {reason}" for reason in r.reasons)
            if r.pinned is not None:
                out.append(f"        pinned tree: {r.pinned.detail}")
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


def kustomization_names(text: str) -> list[str]:
    """The `resources[]` a kustomization file names, normalised (`./ledger.yaml` is
    `ledger.yaml`: kustomize reads both as the same file, review F5)."""
    doc = yaml.safe_load(text) or {}
    return [posixpath.normpath(str(r)) for r in (doc.get("resources") or [])]


def served_resources(adopter_dir: Path) -> list[str] | None:
    """The resource list Flux's Kustomization renders at the checked-out tree, or None if there
    is no kustomization to render. Not a directory listing: a file in that directory which the
    kustomization does not name is served to nobody."""
    k = adopter_dir / SERVED_KUSTOMIZATION
    if not k.is_file():
        return None
    return kustomization_names(k.read_text())


def flux_sync(adopter_dir: Path) -> FluxSync | None:
    """Read `gitops/flux-system/gotk-sync.yaml`: the GitRepository's `ref.tag`/`ref.commit`/`url`
    and the Flux Kustomization's `spec.path`. None when the file is not there at all."""
    f = adopter_dir / FLUX_SYNC
    if not f.is_file():
        return None
    path = tag = commit = url = None
    for d in yaml.safe_load_all(f.read_text()):
        if not isinstance(d, dict):
            continue
        spec = d.get("spec") or {}
        api = str(d.get("apiVersion") or "")
        if d.get("kind") == "Kustomization" and api.startswith("kustomize.toolkit.fluxcd.io"):
            path = spec.get("path")
        elif d.get("kind") == "GitRepository" and api.startswith("source.toolkit.fluxcd.io"):
            url = spec.get("url")
            ref = spec.get("ref") or {}
            # str(): YAML reads an all-digit sha as an integer, and 0 is falsy.
            tag = None if ref.get("tag") is None else str(ref.get("tag"))
            commit = None if ref.get("commit") is None else str(ref.get("commit"))
    return FluxSync(path=path, tag=tag, commit=commit, url=url)


def _git(adopter_dir: Path, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", str(adopter_dir), *args],
                           capture_output=True, text=True, check=False)
    except OSError as exc:
        return 127, str(exc)
    return p.returncode, (p.stdout if p.returncode == 0 else p.stderr).strip()


def checkout_head(adopter_dir: Path) -> str:
    rc, out = _git(adopter_dir, "rev-parse", "--short", "HEAD")
    return out if rc == 0 else "not a git checkout"


def pinned_membership(adopter_dir: Path, sync: FluxSync | None, served: str) -> PinnedRead:
    """Is the served manifest listed by the kustomization in the tree the GitRepository PINS?

    `git show <ref.tag>:<spec.path>/kustomization.yaml`, read from the adopter's own clone. The
    pin is what a cluster reconciling from the github.com remote is actually served today; the
    checked-out tree is what it will be served once the adopter cuts a tag and moves the pin.
    """
    if sync is None or not sync.tag:
        return PinnedRead("unpinned", None, None,
                          f"{FLUX_SYNC} pins no ref.tag, so there is no pinned tree to read")
    rc, resolved = _git(adopter_dir, "rev-parse", "--verify", f"{sync.tag}^{{commit}}")
    if rc != 0:
        return PinnedRead("unreadable", sync.tag, None,
                          f"tag {sync.tag} is not in this clone (fetch tags), so the pinned "
                          f"tree could not be read")
    path = posixpath.normpath(sync.path or SERVED_DIR)
    rc, text = _git(adopter_dir, "show", f"{sync.tag}:{path}/kustomization.yaml")
    short = resolved[:7]
    if rc != 0:
        return PinnedRead("absent", sync.tag, resolved,
                          f"{sync.tag} ({short}) carries no {path}/kustomization.yaml, so "
                          f"nothing under {path} is served from the pinned tree")
    names = kustomization_names(text)
    rel = posixpath.relpath(served, path) if served.startswith(path + "/") else Path(served).name
    if rel in names:
        return PinnedRead("listed", sync.tag, resolved,
                          f"{sync.tag} ({short}) lists {rel} in {path}/kustomization.yaml")
    return PinnedRead("absent", sync.tag, resolved,
                      f"{sync.tag} ({short}) does not list {rel} in {path}/kustomization.yaml "
                      f"(it lists {names}); the lift is listed at the checkout and not in the "
                      f"tree the GitRepository pins")


def _old_labels(node: object) -> list[str]:
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


def grade_sync(lift: Lift, sync: FluxSync | None) -> list[str]:
    """The operation that reaches the served artefact, read from the adopter's own file."""
    served_dir = posixpath.dirname(lift.served)
    if sync is None:
        return [f"{lift.adopter} has no {FLUX_SYNC}, so nothing names the path Flux reconciles "
                f"or the tree it pins, and whether {lift.served} is served cannot be derived"]
    bad: list[str] = []
    if sync.path is None:
        bad.append(f"{lift.adopter}/{FLUX_SYNC} has no Flux Kustomization with a spec.path, so "
                   f"the directory Flux renders is unknown and {lift.served} is served to nobody "
                   f"that this check can name")
    elif posixpath.normpath(sync.path) != served_dir:
        bad.append(f"{lift.adopter}/{FLUX_SYNC} reconciles `path: {sync.path}`, not "
                   f"{served_dir}: at the GitRepository's remote ({sync.url}) the tree root holds "
                   f"gitops/, so `{sync.path}` resolves to no directory, the Kustomization never "
                   f"becomes Ready, and {lift.served} -- the file this check reads -- is served "
                   f"to nobody")
    if not sync.tag:
        bad.append(f"{lift.adopter}/{FLUX_SYNC}'s GitRepository pins no ref.tag, so there is no "
                   f"pinned tree to grade the lift against")
    return bad


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


def pattern_matches(pattern: str, target: str) -> bool:
    """One Renovate `managerFilePatterns` entry against a path. Renovate reads a slash-delimited
    entry (`/^apps/ledger/pom\\.xml$/`, optional trailing flags) as a regular expression and
    anything else as a glob (`**/pom.xml`). The first cut fed every entry to `re.search`, and a
    glob crashed it (review F5)."""
    m = re.fullmatch(r"/(.*)/([a-z]*)", pattern, re.S)
    if m:
        flags = re.I if "i" in m.group(2) else 0
        try:
            return re.search(m.group(1), target, flags) is not None
        except re.error:
            return False
    return fnmatch.fnmatchcase(target, pattern) or fnmatch.fnmatchcase(target, pattern.lstrip("./"))


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
    elif not any(pattern_matches(str(p), lift.stack_manifest) for p in patterns):
        bad.append(f"{lift.adopter}/renovate.json points {lift.renovate_manager!r} at "
                   f"{patterns}, none of which matches {lift.stack_manifest}")
    if cfg.get("dependencyDashboard") is not True:
        bad.append(f"{lift.adopter}/renovate.json leaves dependencyDashboard off, so the stale "
                   f"tree {lift.app} was built to show is visible nowhere")
    # Ticket 33 decision 7: the lifted tree's bumps sit behind dashboard approval, or the first
    # run opens a branch per stale dependency. Prose until review F6; graded now.
    approved = any(
        lift.renovate_manager in (rule.get("matchManagers") or [])
        and rule.get("dependencyDashboardApproval") is True
        for rule in (cfg.get("packageRules") or []) if isinstance(rule, dict))
    if not approved:
        bad.append(f"{lift.adopter}/renovate.json has no packageRule with matchManagers "
                   f"containing {lift.renovate_manager!r} and dependencyDashboardApproval true, "
                   f"so the first run opens a branch per stale dependency instead of a dashboard "
                   f"row each (ticket 33 decision 7)")
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
    sync = flux_sync(adopter_dir)
    bad.extend(grade_sync(lift, sync))
    row.pinned = pinned_membership(adopter_dir, sync, lift.served)
    if sync is not None and sync.commit and row.pinned.resolved \
            and not row.pinned.resolved.startswith(sync.commit):
        bad.append(f"{lift.adopter}/{FLUX_SYNC} pins tag {sync.tag} and commit {sync.commit[:7]}, "
                   f"but the tag resolves to {row.pinned.resolved[:7]}: Flux verifies the pair "
                   f"and reconciles neither")

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
        assert sync is not None
        row.reasons.append(
            f"listed by {SERVED_KUSTOMIZATION} at the checked-out tree "
            f"({checkout_head(adopter_dir)}), on the path {FLUX_SYNC} reconciles "
            f"({sync.path}); versioned by {lift.adopter} at {lift.source_dir}; bumped by "
            f"renovate's {lift.renovate_manager} manager behind dependencyDashboardApproval; "
            f"lifted from {lift.origin}@{lift.origin_commit}")
    return row


def _safe_read(path: Path) -> str:
    try:
        return path.read_text()
    except (UnicodeDecodeError, OSError):
        return ""


def hub_copies(hub_root: Path, lifts: list[Lift], register_path: Path | None = None) -> list[str]:
    """Working copies of a lifted app inside the hub. The record (tickets, ADRs, the drift
    review's captures of the incumbent org) is not a working copy: HUB_RECORD_DIRS names those
    and the report prints the list, so what is excused is visible rather than assumed.

    Three shapes count (review F4 -- the first cut matched the lifted PATHS only, so a full copy
    at `spikes/ledger/` passed):
      1. the lifted paths themselves (`apps/<app>/...`, `gitops/apps/<app>.yaml`);
      2. `<app>/<stack manifest>` under any directory;
      3. a file named like the stack manifest whose content carries the app's identity, or a
         YAML file pinning the app's served image, anywhere -- except the register itself,
         which names the image on purpose.
    """
    found: list[str] = []
    register = register_path.resolve() if register_path else None
    for dirpath, dirnames, filenames in os.walk(hub_root):
        rel_dir = Path(dirpath).relative_to(hub_root).as_posix()
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in HUB_SKIP_DIRS and not (rel_dir == "." and d in HUB_RECORD_DIRS))
        for fn in sorted(filenames):
            path = Path(dirpath) / fn
            if register is not None and path.resolve() == register:
                continue
            rel = fn if rel_dir == "." else f"{rel_dir}/{fn}"
            parts = rel.split("/")
            for lift in lifts:
                manifest = Path(lift.stack_manifest).name
                if rel == lift.stack_manifest or rel == lift.served \
                        or rel.startswith(lift.source_dir + "/"):
                    found.append(rel)
                elif fn == manifest and len(parts) >= 2 and parts[-2] == lift.app:
                    found.append(f"{rel} ({lift.app}/{manifest} under {'/'.join(parts[:-2]) or '.'})")
                elif fn == manifest and re.search(lift.identity, _safe_read(path), re.M | re.S):
                    found.append(f"{rel} (carries {lift.app}'s identity /{lift.identity}/)")
                elif fn.endswith((".yaml", ".yml")) and lift.image in _safe_read(path):
                    found.append(f"{rel} (pins {lift.app}'s served image {lift.image})")
                else:
                    continue
                break
    return found


def grade(hub_root: Path, estate_root: Path, register_path: Path) -> Report:
    lifts = load_register(register_path)
    report = Report()
    report.hub_copies = hub_copies(Path(hub_root), lifts, Path(register_path))
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
    absent = report.pinned_absent
    tags = sorted({r.pinned.tag for r in absent if r.pinned and r.pinned.tag}) or \
        sorted({r.pinned.tag for r in report.rows if r.pinned and r.pinned.tag})
    report.notes.append(
        f"LIMIT  {len(absent)} of {len(lifts)} lifts are listed at main and not in the tree the "
        f"GitRepository pins ({', '.join(tags) if tags else 'no tag read'})"
        + (f": {', '.join(f'{r.app}->{r.adopter}' for r in absent)}" if absent else "")
        + ": a cluster reconciling that pin is served none of these until the adopter cuts a "
          "tag and moves its own ref.tag+commit, which no renovate customManager bumps")
    unreadable = report.pinned_unreadable
    if unreadable:
        report.notes.append(
            f"LIMIT  {len(unreadable)} of {len(lifts)} pinned trees could not be read: "
            + "; ".join(f"{r.app}->{r.adopter}: {r.pinned.detail}" for r in unreadable if r.pinned))
    for b in BLIND_SPOTS:
        report.notes.append(f"BLIND  {b}")
    report.notes.append(f"NOTE   the hub's record directories are not read as working copies: "
                        f"{list(HUB_RECORD_DIRS)}; not the hub's tree at all: "
                        f"{list(HUB_SKIP_DIRS)}; the register names the images on purpose")
    return report


def kyverno_plan(estate_root: Path, register_path: Path) -> list[tuple[str, str, str, str, str]]:
    """(app, adopter, policy directory, orphan guard, served manifest) for every lift that has
    landed. `verify-lifted-apps.sh` runs the real `kyverno apply` over each, so the last word on
    whether the adopter's own composed set admits the workload belongs to the estate's own engine
    rather than to this file's reading of a manifest."""
    plan: list[tuple[str, str, str, str, str]] = []
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
        guard = adopter_dir / "composed" / "orphan-guard.yaml"
        if policies.is_dir():
            plan.append((lift.app, lift.adopter, str(policies), str(guard), str(served)))
    return plan


def main(argv: list[str]) -> int:
    import argparse
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hub-root", type=Path, default=here.parent.parent)
    ap.add_argument("--estate-root", type=Path, default=here.parent.parent / ".estate-clone")
    ap.add_argument("--register", type=Path, default=here / "register.yaml")
    ap.add_argument("--kyverno-plan", action="store_true",
                    help="print `app<TAB>adopter<TAB>policy-dir<TAB>orphan-guard<TAB>served-manifest` "
                         "per landed lift and exit 0; the shell script runs kyverno over the rows")
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
