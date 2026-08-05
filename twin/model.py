"""The world layer and per-org overlays.

A shared **world layer** holds the common landscape; each org owns a scoped **overlay** it never
shares. An overlay may reference the world layer; the world layer may **never** reference an
overlay. That single directional rule is what makes multi-tenancy and the credibility-theory
prior the same mechanism rather than two (decision ticket 07, Q1b; build ticket 04).

An overlay pins the world commit it resolves against, so an overlay stays reproducible while the
world moves underneath it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .repo import ModelRepo, RepoError, UnitRef, load_yaml

WORLD = "world"
ORGS = "orgs"

WORLD_COLLECTIONS = ("components", "propositions", "world_models")
OVERLAY_COLLECTIONS = ("components", "world_models", "signals", "claims", "scenarios", "outcomes")


class ModelError(RuntimeError):
    pass


class DirectionError(ModelError):
    """The world layer referenced an overlay."""


def _collection(repo: ModelRepo, tree: str, prefix: str, subdir: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path in repo.list_tree(tree, subdir):
        if not path.endswith((".yaml", ".yml")):
            continue
        doc = repo.read_yaml_at(tree, path)
        ident = doc.get("id")
        if not ident:
            raise ModelError(f"{prefix}/{path}: every model object needs an `id`")
        if ident in out:
            raise ModelError(f"{prefix}/{subdir}: duplicate id {ident!r}")
        out[str(ident)] = doc
    return out


def orgs(repo: ModelRepo) -> list[str]:
    seen = {p.split("/")[1] for p in repo.list(ORGS) if p.count("/") >= 2}
    return sorted(seen)


@dataclass(frozen=True)
class World:
    ref: UnitRef
    components: dict[str, dict[str, Any]]
    propositions: dict[str, dict[str, Any]]
    world_models: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, repo: ModelRepo, at_commit: str | None = None) -> "World":
        ref = repo.unit_ref_at(WORLD, at_commit) if at_commit else repo.unit_ref(WORLD)
        loaded = {name: _collection(repo, ref.tree, WORLD, name) for name in WORLD_COLLECTIONS}
        return cls(ref=ref, **loaded)


@dataclass(frozen=True)
class Overlay:
    """One org's private layer. Loading it reads that org's subtree and the world — nothing else."""

    org: str
    ref: UnitRef
    world: World
    components: dict[str, dict[str, Any]]
    world_models: dict[str, dict[str, Any]]
    signals: dict[str, dict[str, Any]]
    claims: dict[str, dict[str, Any]]
    scenarios: dict[str, dict[str, Any]]
    outcomes: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, repo: ModelRepo, org: str) -> "Overlay":
        enforce_direction(repo)
        base = f"{ORGS}/{org}"
        if not repo.exists(f"{base}/meta.yaml"):
            raise ModelError(f"no overlay for org {org!r} (expected {base}/meta.yaml)")
        ref = repo.unit_ref(base)
        meta = repo.read_yaml_at(ref.tree, "meta.yaml")
        world_ref = meta.get("world_ref")
        if not world_ref:
            raise ModelError(
                f"{base}/meta.yaml must declare `world_ref` — an overlay resolves world-layer "
                "references at a pinned world commit, or it is not reproducible against a moving world"
            )
        try:
            world = World.load(repo, at_commit=str(world_ref))
        except RepoError as exc:
            raise ModelError(f"{base}/meta.yaml: world_ref {world_ref!r} — {exc}") from None

        loaded = {name: _collection(repo, ref.tree, base, name) for name in OVERLAY_COLLECTIONS}
        overlay = cls(org=org, ref=ref, world=world, **loaded)
        overlay._check_references()
        return overlay

    # -- resolution ----------------------------------------------------------------------

    def component(self, ident: str) -> dict[str, Any]:
        if ident in self.components:
            return self.components[ident]
        if ident in self.world.components:
            return self.world.components[ident]
        raise ModelError(f"no component {ident!r} in overlay {self.org!r} or its pinned world layer")

    def world_model(self, ident: str) -> dict[str, Any]:
        if ident in self.world_models:
            return self.world_models[ident]
        if ident in self.world.world_models:
            return self.world.world_models[ident]
        raise ModelError(f"no world model {ident!r} in overlay {self.org!r} or its pinned world layer")

    def proposition(self, ident: str) -> dict[str, Any]:
        if ident in self.world.propositions:
            return self.world.propositions[ident]
        raise ModelError(f"no proposition {ident!r} in the pinned world layer")

    def _check_references(self) -> None:
        for ident, comp in sorted(self.components.items()):
            for need in comp.get("needs", []) or []:
                if need not in self.components and need not in self.world.components:
                    raise ModelError(f"component {ident!r} needs {need!r}, which does not exist")

    def pins(self) -> dict[str, Any]:
        return {"overlay": self.ref.as_dict(), "world": self.world.ref.as_dict(), "org": self.org}


def enforce_direction(repo: ModelRepo) -> None:
    """Refuse to load anything from a repository whose world layer references an overlay.

    Checked here rather than only in the invariant suite: a rule that holds for the fixture and
    not for the repository in front of you is a property of the fixture.
    """
    if repo.direction_checked:
        return
    violations = check_direction(repo)
    if violations:
        raise DirectionError(
            "the world layer references an overlay, which it may never do:\n  "
            + "\n  ".join(violations)
        )
    repo.direction_checked = True


def check_direction(repo: ModelRepo) -> list[str]:
    """Violations of `world_never_references_overlay`, as human-readable strings.

    The world layer must not name a tenant or anything a tenant defines. Three ways it could:
    a value, a mapping *key*, or prose. All three are checked, in every file under `world/`
    including non-YAML ones, and in **every world tree an overlay actually pins** — checking only
    the world at the repository pin would miss an overlay that resolves against a different one.

    An id the world layer declares itself is excluded: an overlay is allowed to shadow a world
    component, and one tenant doing so must not red-light the check for everybody.
    """
    org_ids = set(orgs(repo))
    overlay_ids: set[str] = set()
    for path in repo.list(ORGS):
        if path.endswith((".yaml", ".yml")):
            ident = repo.read_yaml(path).get("id")
            if ident:
                overlay_ids.add(str(ident))

    trees = {repo.unit_ref(WORLD).tree}
    for org in org_ids:
        meta = f"{ORGS}/{org}/meta.yaml"
        if repo.exists(meta):
            pinned = repo.read_yaml(meta).get("world_ref")
            if pinned:
                try:
                    trees.add(repo.unit_ref_at(WORLD, str(pinned)).tree)
                except RepoError:
                    continue  # an unresolvable pin is Overlay.load's error to report, not this one

    violations: list[str] = []
    for tree in sorted(trees):
        world_ids = {
            repo.read_yaml_at(tree, p).get("id")
            for p in repo.list_tree(tree)
            if p.endswith((".yaml", ".yml"))
        }
        forbidden = (org_ids | overlay_ids) - {str(i) for i in world_ids if i}
        prose = re.compile(r"\b(" + "|".join(re.escape(o) for o in sorted(org_ids)) + r")\b") if org_ids else None

        for path in repo.list_tree(tree):
            raw = repo.read_blob(tree, path).decode("utf-8", "replace")
            where = f"world/{path}"
            if path.endswith((".yaml", ".yml")):
                doc = load_yaml(raw)
                for key, value in _scalars(doc):
                    if isinstance(value, str):
                        if value in forbidden:
                            violations.append(f"{where}: {key or '<root>'} references overlay-scoped {value!r}")
                        elif f"{ORGS}/" in value:
                            violations.append(f"{where}: {key or '<root>'} points into the overlay tree ({value!r})")
                for key in _keys(doc):
                    if key in forbidden or key in ("org", "overlay", "tenant"):
                        violations.append(f"{where}: carries an overlay-scoped key {key!r}")
            elif f"{ORGS}/" in raw:
                violations.append(f"{where}: points into the overlay tree")
            if prose and prose.search(raw):
                violations.append(f"{where}: names a tenant ({prose.search(raw).group(1)!r})")  # type: ignore[union-attr]
    return sorted(set(violations))


def _scalars(node: Any, path: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += _scalars(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _scalars(v, f"{path}[{i}]")
    else:
        out.append((path, node))
    return out


def _keys(node: Any) -> list[str]:
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.append(str(k))
            out += _keys(v)
    elif isinstance(node, list):
        for v in node:
            out += _keys(v)
    return out
