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

from . import evidence, wardley
from .repo import ModelRepo, RepoError, UnitRef, load_yaml
from .schema import (
    CAUSAL_EDGE,
    CAUSAL_FIELDS,
    CAUSAL_ONLY_OPTIONAL,
    COLLECTION_KINDS,
    PERSON_EDGES,
    STRUCTURAL_EDGE,
    degenerate,
    validate,
)

WORLD = "world"
ORGS = "orgs"
BEHAVIOURAL = "behavioural"

WORLD_COLLECTIONS = ("components", "propositions", "world_models", "priors")
OVERLAY_COLLECTIONS = (
    "components", "world_models", "signals", "claims", "scenarios", "outcomes", "people", "edges",
    "perspectives", "regrades", "responses", "own_data", "causal_accounts",
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


def _refuse_duplicate_subject(collection: dict[str, dict[str, Any]], prefix: str, subdir: str) -> None:
    """Two files naming the same `subject` leaves it ambiguous which one is authoritative.

    The `id` uniqueness `_collection` already checks guards the file name; this guards the
    field the credibility blend actually looks up by (build ticket 31).
    """
    seen: dict[str, str] = {}
    for ident, doc in sorted(collection.items()):
        subject = str(doc["subject"])
        if subject in seen:
            raise ModelError(
                f"{prefix}/{subdir}: {seen[subject]!r} and {ident!r} both name subject "
                f"{subject!r} — a subject may have only one authority per layer"
            )
        seen[subject] = ident


def orgs(repo: ModelRepo) -> list[str]:
    seen = {p.split("/")[1] for p in repo.list(ORGS) if p.count("/") >= 2}
    return sorted(seen)


@dataclass(frozen=True)
class World:
    ref: UnitRef
    components: dict[str, dict[str, Any]]
    propositions: dict[str, dict[str, Any]]
    world_models: dict[str, dict[str, Any]]
    # The credibility-theory industry prior (build ticket 31, decision ticket 07 Q1b). Keyed by
    # subject via `Overlay.prior`, not by id here — the id is just the file's own identifier.
    priors: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, repo: ModelRepo, at_commit: str | None = None) -> "World":
        ref = repo.unit_ref_at(WORLD, at_commit) if at_commit else repo.unit_ref(WORLD)
        validate("world-meta", repo.read_yaml_at(ref.tree, "meta.yaml"), f"{WORLD}/meta.yaml")
        _refuse_unread_directories(repo, ref.tree, WORLD, WORLD_COLLECTIONS)
        loaded = {name: _collection(repo, ref.tree, WORLD, name) for name in WORLD_COLLECTIONS}
        _refuse_duplicate_subject(loaded["priors"], WORLD, "priors")
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
    perspectives: dict[str, dict[str, Any]]
    regrades: dict[str, dict[str, Any]]
    responses: dict[str, dict[str, Any]]
    # Sparse own-data observations, keyed by the file's own id (build ticket 31). Looked up by
    # subject via `own_data_for`, the overlay half of the credibility blend.
    own_data: dict[str, dict[str, Any]]
    # Rival causal accounts (build ticket 32) — each a sparse set of overrides on specific causal
    # edge ids, held beside `edges` rather than replacing it. None is canonical; `causal_graph`
    # treats every id the same way, this overlay's own `edges` collection included.
    causal_accounts: dict[str, dict[str, Any]]

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

    def causal_account(self, ident: str) -> dict[str, Any]:
        if ident not in self.causal_accounts:
            known = ", ".join(sorted(self.causal_accounts)) or "none"
            raise ModelError(f"no causal account {ident!r} in overlay {self.org!r} (have: {known})")
        return self.causal_accounts[ident]

    def proposition(self, ident: str) -> dict[str, Any]:
        if ident in self.world.propositions:
            return self.world.propositions[ident]
        raise ModelError(f"no proposition {ident!r} in the pinned world layer")

    def prior(self, subject: str) -> dict[str, Any]:
        """The industry prior for a subject (build ticket 31). Priors live in the world layer only
        — there is no overlay-authored prior, because "industry" is the shared layer's whole job."""
        found = [p for p in self.world.priors.values() if p["subject"] == subject]
        if not found:
            known = ", ".join(sorted({p["subject"] for p in self.world.priors.values()})) or "none"
            raise ModelError(f"no world-layer prior for subject {subject!r} (have: {known})")
        return found[0]

    def own_data_for(self, subject: str) -> dict[str, Any] | None:
        """This org's own observations for a subject, or `None` — the honest default (build ticket 31)."""
        return next((d for d in self.own_data.values() if d["subject"] == subject), None)

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
        self._check_regrades()
        for ident, perspective in sorted(self.perspectives.items()):
            for component_id in sorted(perspective.get("values", {})):
                try:
                    self.component(str(component_id))
                except ModelError:
                    raise ModelError(
                        f"perspective {ident!r} values {component_id!r}, which is not a component "
                        "in this overlay or its pinned world layer"
                    ) from None
            for component_id in perspective.get("cash_flow", []) or []:
                try:
                    self.component(str(component_id))
                except ModelError:
                    raise ModelError(
                        f"perspective {ident!r} names {component_id!r} as a cash flow, and it is "
                        "not a component in this overlay or its pinned world layer"
                    ) from None
        self._check_scenarios()
        self._check_responses()
        self._check_own_data()
        self._check_causal_accounts()

    def _check_causal_accounts(self) -> None:
        for account_id, account in sorted(self.causal_accounts.items()):
            for edge_id, override in sorted(account["edges"].items()):
                for end in ("from", "to"):
                    try:
                        self.component(str(override[end]))
                    except ModelError:
                        raise ModelError(
                            f"causal account {account_id!r} edge {edge_id!r}: {end} "
                            f"{override[end]!r} is not a component in this overlay or its "
                            "pinned world layer"
                        ) from None

    def _check_own_data(self) -> None:
        """Own-data observations name a subject a world-layer prior actually declares.

        An own-data file for a subject nobody published an industry prior for is orphaned: the
        blend has a numerator and no denominator to weigh it against (build ticket 31).
        """
        _refuse_duplicate_subject(self.own_data, f"{ORGS}/{self.org}", "own_data")
        world_subjects = {str(p["subject"]) for p in self.world.priors.values()}
        for ident, doc in sorted(self.own_data.items()):
            subject = str(doc["subject"])
            if subject not in world_subjects:
                raise ModelError(
                    f"own-data {ident!r} names subject {subject!r}, which no world-layer prior "
                    "declares. Own-data blends against an industry prior; with none published "
                    "for this subject there is nothing to blend it into."
                )

    def _check_scenarios(self) -> None:
        """A scenario names components that exist.

        Checked here rather than only where it bites: `twin validate` used to pass a repository
        that `twin exposure` then refused, because the scenario's components were never resolved
        and admission is the first thing that needs them to exist.
        """
        for ident, scenario in sorted(self.scenarios.items()):
            for component_id in scenario.get("components", []) or []:
                try:
                    self.component(str(component_id))
                except ModelError:
                    raise ModelError(
                        f"scenario {ident!r} names component {component_id!r}, which is not a "
                        "component in this overlay or its pinned world layer"
                    ) from None

    def _check_responses(self) -> None:
        """A response addresses a real component and crosses a constraint somebody declared.

        The second half is what keeps the pre-filter honest. A `crosses` id that matches nothing
        would silently never filter, so an option could name a red line that does not exist and
        survive every perspective — which is the same failure as having no constraint at all.
        """
        from . import constraints

        declarable = constraints.floor_ids() | {
            str(i)
            for perspective in self.perspectives.values()
            for field in ("ruin", "forbidden")
            for i in (perspective.get(field) or {})
        }
        for ident, response in sorted(self.responses.items()):
            try:
                self.component(str(response["addresses"]))
            except ModelError:
                raise ModelError(
                    f"response {ident!r} addresses {response['addresses']!r}, which is not a "
                    "component in this overlay or its pinned world layer"
                ) from None
            unknown = sorted({str(c) for c in (response.get("crosses") or {})} - declarable)
            if unknown:
                raise ModelError(
                    f"response {ident!r} says it crosses {', '.join(unknown)}, which no universal "
                    "constraint and no perspective in this overlay declares. A red line nobody "
                    "declared filters nothing, so this option would survive every pre-filter."
                )

    def _check_regrades(self) -> None:
        """A grade is immutable without a regrade record, and the record has to add up.

        The chain must be contiguous and must end at the grade the file now declares. This is the
        half that runs on every load; the half that reads git history is `twin validate`, because
        it costs a process per commit per graded file and a load happens constantly.
        """
        graded = {k: v for name in evidence.GRADED_COLLECTIONS for k, v in getattr(self, name).items()}
        for ident, regrade in sorted(self.regrades.items()):
            subject = str(regrade["subject"])
            if subject not in graded:
                raise ModelError(
                    f"regrade {ident!r} names subject {subject!r}, which is not an edge or a claim "
                    "in this overlay. A regrade with no subject records nothing."
                )
        for subject, doc in sorted(graded.items()):
            if "evidence_grade" not in doc:
                continue
            chain = evidence.chain_for(subject, self.regrades)
            try:
                evidence.check_chain(subject, int(doc["evidence_grade"]), chain, f"overlay {self.org!r}")
            except evidence.EvidenceError as exc:
                raise ModelError(str(exc)) from None

    def regrade_records(self) -> list[dict[str, Any]]:
        """Every regrade, with its direction derived. Ordered by subject, then oldest first."""
        return [
            evidence.record(regrade)
            for subject in sorted({str(r["subject"]) for r in self.regrades.values()})
            for regrade in evidence.chain_for(subject, self.regrades)
        ]

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
                # `CAUSAL_ONLY_OPTIONAL` (`calibration`) is optional provenance, not a causal
                # assertion (build ticket 23) — carried through beside `confidence` for the same
                # reason: a reader of the graph should not have to open the source file to see it.
                # Read from the schema's own constant so a future addition there does not also
                # need remembering here.
                causal={
                    f: e[f] for f in CAUSAL_FIELDS + CAUSAL_ONLY_OPTIONAL + ("confidence",) if f in e
                } or None,
            )
            for ident, e in sorted(self.edges.items())
        ]
        return Graph(
            org=self.org,
            components=components,
            people=dict(self.people),
            edges=tuple(sorted(edges, key=lambda e: (e.type, e.source, e.target))),
            regrades=tuple(self.regrade_records()),
        )

    def causal_graph(self, account_id: str) -> "Graph":
        """The graph `graph()` builds, with a named rival causal account's edge overrides applied
        (build ticket 32). Sparse by design: an account overrides only the causal edge ids it
        names, so most of a graph is inherited unchanged and an account exists to say where it
        differs, not to re-author everything. Structural and person edges never change — a causal
        account is a claim about measured effect, never about which components exist.
        """
        account = self.causal_account(account_id)
        base = self.graph()
        overrides = {str(k): v for k, v in account["edges"].items()}
        edges = [e for e in base.edges if not (e.type == CAUSAL_EDGE and e.id in overrides)]
        edges += [
            Edge(
                id=ident,
                type=CAUSAL_EDGE,
                source=str(e["from"]),
                target=str(e["to"]),
                causal={f: e[f] for f in CAUSAL_FIELDS + CAUSAL_ONLY_OPTIONAL + ("confidence",) if f in e},
            )
            for ident, e in sorted(overrides.items())
        ]
        return Graph(
            org=self.org,
            components=base.components,
            people=base.people,
            edges=tuple(sorted(edges, key=lambda e: (e.type, e.source, e.target))),
            regrades=base.regrades,
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

    @property
    def grade(self) -> int | None:
        return int(self.causal["evidence_grade"]) if self.causal else None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.id, "type": self.type, "from": self.source, "to": self.target}
        if self.causal:
            out.update(self.causal)
            # Flagged on read rather than refused on write: a point estimate is representable,
            # but it must never be readable as a range.
            out["degenerate_elasticity"] = degenerate(self.causal["elasticity"])
            # The rung, spelled out, and the gate that reads it (build tickets 18 and 19). A
            # number on its own says nothing about what admitted it, and a reader of the graph
            # should not have to hold a five-rung ladder in their head to know whether an edge
            # can carry a price.
            grade = int(self.causal["evidence_grade"])
            out["evidence_grade_name"] = str(evidence.rung(grade)["name"])
            out["may_price"] = evidence.may_price(grade)
        return out


@dataclass(frozen=True)
class Graph:
    """Components and people as nodes, typed edges between them. No behavioural data, ever."""

    org: str
    components: dict[str, dict[str, Any]]
    people: dict[str, dict[str, Any]]
    edges: tuple[Edge, ...]
    regrades: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "org": self.org,
            "components": [
                {"id": i, "kind": c["kind"], "evolution": c.get("evolution"), "visibility": c.get("visibility")}
                for i, c in sorted(self.components.items())
            ],
            "people": [{"id": i, "role": p.get("role")} for i, p in sorted(self.people.items())],
            "edges": [e.as_dict() for e in self.edges],
            "regrades": list(self.regrades),
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
            # How much of the causal layer could carry a price at all (build ticket 19). A count
            # rather than a ratio: a ratio of two small numbers reads as a quality score.
            "causal_edges_admissible_to_pricing": sum(
                1 for e in causal if e.grade is not None and evidence.may_price(e.grade)
            ),
            "causal_edges_by_evidence_grade": dict(
                sorted((str(g), sum(1 for e in causal if e.grade == g)) for g in {e.grade for e in causal})
            ),
            "regrades": len(self.regrades),
            "regrades_by_direction": dict(
                sorted(
                    (d, sum(1 for r in self.regrades if r["direction"] == d))
                    for d in {str(r["direction"]) for r in self.regrades}
                )
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
