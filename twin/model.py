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

from . import wardley
from .repo import ModelRepo, RepoError, UnitRef, load_yaml
from .schema import (
    CAUSAL_EDGE,
    CAUSAL_FIELDS,
    COLLECTION_KINDS,
    PERSON_EDGES,
    STRUCTURAL_EDGE,
    degenerate,
    validate,
)

WORLD = "world"
ORGS = "orgs"
BEHAVIOURAL = "behavioural"

WORLD_COLLECTIONS = ("components", "propositions", "world_models")
OVERLAY_COLLECTIONS = (
    "components", "world_models", "signals", "claims", "scenarios", "outcomes", "people", "edges",
)


class ModelError(RuntimeError):
    pass


class DirectionError(ModelError):
    """The world layer referenced an overlay."""


def _collection(repo: ModelRepo, tree: str, prefix: str, subdir: str) -> dict[str, dict[str, Any]]:
    """Load and validate one collection. Every object is typed by the directory it sits in."""
    kind = COLLECTION_KINDS[subdir]
    out: dict[str, dict[str, Any]] = {}
    for path in repo.list_tree(tree, subdir):
        if not path.endswith((".yaml", ".yml")):
            continue
        doc = repo.read_yaml_at(tree, path)
        validate(kind, doc, f"{prefix}/{path}")
        ident = str(doc["id"])
        if ident in out:
            raise ModelError(f"{prefix}/{subdir}: duplicate id {ident!r}")
        out[ident] = doc
    return out


def _refuse_unread_directories(repo: ModelRepo, tree: str, prefix: str, known: tuple[str, ...]) -> None:
    """A directory nobody loads is a directory nobody validates.

    Silently ignoring it would let an author believe their file is in the model — and would let
    Article 9 data sit in the repository unread rather than refused.
    """
    stray = sorted(
        {p.split("/")[0] for p in repo.list_tree(tree) if "/" in p} - set(known)
    )
    if stray:
        raise ModelError(
            f"{prefix}: nothing loads {', '.join(stray)}, so nothing validates it. "
            f"This unit reads {', '.join(known)} and refuses to ignore anything else."
        )


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
        validate("world-meta", repo.read_yaml_at(ref.tree, "meta.yaml"), f"{WORLD}/meta.yaml")
        _refuse_unread_directories(repo, ref.tree, WORLD, WORLD_COLLECTIONS)
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
    people: dict[str, dict[str, Any]]
    edges: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, repo: ModelRepo, org: str) -> "Overlay":
        enforce_direction(repo)
        base = f"{ORGS}/{org}"
        if not repo.exists(f"{base}/meta.yaml"):
            raise ModelError(f"no overlay for org {org!r} (expected {base}/meta.yaml)")
        ref = repo.unit_ref(base)
        meta = repo.read_yaml_at(ref.tree, "meta.yaml")
        validate("overlay-meta", meta, f"{base}/meta.yaml")
        _refuse_unread_directories(repo, ref.tree, base, OVERLAY_COLLECTIONS + (BEHAVIOURAL,))
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
        for ident, edge in sorted(self.edges.items()):
            if edge["type"] == STRUCTURAL_EDGE:
                raise ModelError(
                    f"edge {ident!r}: structural {STRUCTURAL_EDGE!r} edges are declared as a "
                    "component's `needs`, so the value chain reads as a value chain. One edge, one home."
                )
            if edge["type"] == CAUSAL_EDGE:
                # Component to component. A causal edge from a person would be a claim about a
                # named individual's effect on the world, which is the thing decision ticket 15
                # refuses; people reach the graph through role edges only.
                self.component(str(edge["from"]))
                self.component(str(edge["to"]))
                continue
            if edge["from"] not in self.people:
                raise ModelError(f"edge {ident!r}: {edge['from']!r} is not a person in this overlay")
            self.component(str(edge["to"]))

    def graph(self) -> "Graph":
        """The typed knowledge graph: one edge collection, two authoring sites.

        Structural edges are authored as a component's `needs` because the Wardley value chain
        should read as one; person edges are authored as first-class objects because they are not
        a chain. Both arrive here as the same typed edge.
        """
        components = {**self.world.components, **self.components}
        # Both layers: the world layer carries the common value chain and an overlay may shadow a
        # node of it. Reading only the overlay would drop the shared spine from every graph.
        edges = [
            Edge(id=f"{ident}--{STRUCTURAL_EDGE}--{need}", type=STRUCTURAL_EDGE, source=ident, target=str(need))
            for ident, comp in sorted(components.items())
            for need in dict.fromkeys(comp.get("needs", []) or [])  # a repeated `needs` is one edge
        ]
        edges += [
            Edge(
                id=ident,
                type=str(e["type"]),
                source=str(e["from"]),
                target=str(e["to"]),
                causal={f: e[f] for f in CAUSAL_FIELDS + ("confidence",) if f in e} or None,
            )
            for ident, e in sorted(self.edges.items())
        ]
        return Graph(
            org=self.org,
            components=components,
            people=dict(self.people),
            edges=tuple(sorted(edges, key=lambda e: (e.type, e.source, e.target))),
        )

    def pins(self) -> dict[str, Any]:
        return {"overlay": self.ref.as_dict(), "world": self.world.ref.as_dict(), "org": self.org}


@dataclass(frozen=True)
class Edge:
    id: str
    type: str
    source: str
    target: str
    # Sign, lag, elasticity and evidence grade — present on a causal edge, absent on every other
    # kind, because only a causal edge measures anything (build ticket 17).
    causal: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.id, "type": self.type, "from": self.source, "to": self.target}
        if self.causal:
            out.update(self.causal)
            # Flagged on read rather than refused on write: a point estimate is representable,
            # but it must never be readable as a range.
            out["degenerate_elasticity"] = degenerate(self.causal["elasticity"])
        return out


@dataclass(frozen=True)
class Graph:
    """Components and people as nodes, typed edges between them. No behavioural data, ever."""

    org: str
    components: dict[str, dict[str, Any]]
    people: dict[str, dict[str, Any]]
    edges: tuple[Edge, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "org": self.org,
            "components": [
                {"id": i, "kind": c["kind"], "evolution": c.get("evolution"), "visibility": c.get("visibility")}
                for i, c in sorted(self.components.items())
            ],
            "people": [{"id": i, "role": p.get("role")} for i, p in sorted(self.people.items())],
            "edges": [e.as_dict() for e in self.edges],
        }

    def bus_factor(self, component: str) -> list[str]:
        """Who would have to be replaced. The only reason people are in the graph at all."""
        return sorted({e.source for e in self.edges if e.type in PERSON_EDGES and e.target == component})

    def wardley(self) -> dict[str, Any]:
        """The map, derived from this graph. No authoring step (build ticket 14)."""
        return wardley.map_of(self.components, self.edges)

    def rollups(self) -> dict[str, Any]:
        """Aggregates, computed from the constituents on every read (build ticket 13).

        There is no authored form and no stored form: a roll-up exists only for as long as it
        takes to serialise it. That is what makes "an aggregate can never drift from its
        constituents" structural — there is no second copy to drift.
        """
        causal = [e for e in self.edges if e.type == CAUSAL_EDGE]
        by_kind: dict[str, int] = {}
        by_stage: dict[str, int] = {}
        for doc in self.components.values():
            by_kind[str(doc["kind"])] = by_kind.get(str(doc["kind"]), 0) + 1
            stage = doc.get("evolution")
            if stage is not None:
                by_stage[str(stage)] = by_stage.get(str(stage), 0) + 1
        return {
            "components": len(self.components),
            "components_by_kind": dict(sorted(by_kind.items())),
            "components_by_evolution": dict(sorted(by_stage.items())),
            "people": len(self.people),
            "edges": len(self.edges),
            "edges_by_type": dict(
                sorted((t, sum(1 for e in self.edges if e.type == t)) for t in {e.type for e in self.edges})
            ),
            "causal_edges": len(causal),
            "causal_edges_with_degenerate_elasticity": sum(
                1 for e in causal if e.causal and degenerate(e.causal["elasticity"])
            ),
            "components_with_a_named_holder": sum(
                1 for i in self.components if self.bus_factor(i)
            ),
            "components_positioned_on_the_map": len(wardley.positions(self.components)),
        }


@dataclass(frozen=True)
class BehaviouralOverlay:
    """The most private object in the system, and a separately gated unit.

    Never reached by `Overlay.load`. It has its own directory, its own metadata, and its own
    admission requirements, so detaching it is a demonstrable act rather than a promise: delete
    the directory and everything else still loads (decision tickets 07 and 15).
    """

    org: str
    ref: UnitRef
    meta: dict[str, Any]
    observations: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, repo: ModelRepo, org: str) -> "BehaviouralOverlay":
        base = f"{ORGS}/{org}/{BEHAVIOURAL}"
        if not repo.exists(f"{base}/meta.yaml"):
            raise ModelError(
                f"org {org!r} has no behavioural overlay. Its absence is the default and the "
                "supported state; nothing else in the model depends on it."
            )
        ref = repo.unit_ref(base)
        meta = repo.read_yaml_at(ref.tree, "meta.yaml")
        validate("behavioural-meta", meta, f"{base}/meta.yaml")
        if not meta.get("advisory_only"):
            raise ModelError(
                f"{base}/meta.yaml declares advisory_only: false. Behavioural inference is "
                "advisory only — Article 22 does not permit it to decide anything."
            )
        observations = _collection(repo, ref.tree, base, "observations")
        return cls(org=org, ref=ref, meta=meta, observations=observations)


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
        prose = (
            re.compile(r"\b(" + "|".join(re.escape(o) for o in sorted(org_ids)) + r")\b", re.IGNORECASE)
            if org_ids
            else None
        )

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
