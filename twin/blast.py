"""The blast radius: one traversal, two outputs (build ticket 19).

Reverse-dependency traversal, **inherited from `/arckit:impact`** rather than rebuilt, with that
tool's known limits carried with it. Two kinds of hop, and the distinction is the whole point:

* a **causal** hop follows an `influences` edge forwards — somebody claimed a mechanism, and it
  carries an evidence grade;
* a **structural** hop follows a `needs` edge backwards to whoever depends on this node — real
  exposure with **no claimed mechanism**, so it can never carry a price.

A path prices only when every hop is causal *and* every grade is inside the published threshold.
Everything else is reported as an unpriced structural blast radius, which is a first-class answer
rather than a gap: "we know this is connected but cannot price it" is what the output has to be
able to say.

Its own module rather than a method on the graph, for the reason the Wardley maths has one: this
is a ranking algorithm over the graph, not part of loading it, and a module that changes for
loading *and* for traversal changes for two reasons.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from . import evidence
from .artefact import ArtefactError
from .canon import walk_keys
from .schema import CAUSAL_EDGE, STRUCTURAL_EDGE

if TYPE_CHECKING:  # pragma: no cover
    from .model import Edge, Graph

# How far a traversal walks before it stops. `ponytail:` a fixed cap rather than a cost model —
# path enumeration is exponential in branching factor and the artefact says where it stopped, so
# a truncated answer is visible rather than silently partial. Raise it, or switch to a frontier
# budget, if a real estate ever needs more than six hops.
MAX_DEPTH = 6

# Why a reached component is not admitted to pricing. Both are answers, not gaps.
NO_MECHANISM = "no-claimed-mechanism"
BELOW_THRESHOLD = "evidence-grade-below-threshold"

_REASON_RANK = {None: 0, BELOW_THRESHOLD: 1, NO_MECHANISM: 2}

# The body, closed. Every key it may carry at any depth is listed here and a key that is not
# listed refuses to serialise.
#
# This is what makes "blast radius is a distinct artefact type, not a price with a null field"
# structural rather than a naming convention: there is no `price`, no `cost`, no `loss` and no
# `severity` in this set, so an unpriced result has nowhere to put a number even if somebody
# later wanted one there. Same move as the closed model schemas and Article 9.
BODY_KEYS = frozenset(
    {
        "origin", "traversal", "gating", "admitted_to_pricing", "unpriced",
        "inherited_from", "max_depth", "truncated", "known_limits",
        "pin", "version", "pricing_threshold", "digest", "rule", "grades",
        "grade", "name", "admits", "example", "may_price",
        "component", "worst_evidence_grade", "depth", "path", "reason", "detail",
        "edge", "hop", "evidence_grade",
    }
)

KNOWN_LIMITS = (
    "reverse dependency only: it reads the graph as it stands and carries no history",
    "the inherited tool reports currency deltas as prose; nothing here reports one at all",
    "simple paths only, so a cyclic dependency is traversed once and no more",
)


@dataclass(frozen=True)
class Reached:
    """One component, and the best path the traversal found to it."""

    component: str
    reason: str | None
    detail: str | None
    worst_evidence_grade: int | None
    path: tuple[tuple["Edge", bool], ...]

    @property
    def priced(self) -> bool:
        return self.reason is None

    @property
    def rank(self) -> tuple[Any, ...]:
        """Priced beats claimed beats merely structural; then shorter and better evidenced.

        Deterministic down to the path itself, because two paths of equal rank would otherwise
        resolve to whichever the walk happened to reach first.
        """
        return (
            _REASON_RANK[self.reason],
            self.worst_evidence_grade if self.worst_evidence_grade is not None else 99,
            len(self.path),
            [edge.id for edge, _ in self.path],
        )

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "component": self.component,
            "depth": len(self.path),
            "worst_evidence_grade": self.worst_evidence_grade,
            "path": [
                {"edge": edge.id, "hop": CAUSAL_EDGE if is_causal else STRUCTURAL_EDGE,
                 "evidence_grade": edge.grade if is_causal else None}
                for edge, is_causal in self.path
            ],
        }
        if not self.priced:
            out["reason"], out["detail"] = self.reason, self.detail
        return out


def classify(component: str, path: tuple[tuple["Edge", bool], ...], threshold: int) -> Reached:
    """What one path licenses: a price, a claim too weak to price, or no mechanism at all."""
    all_causal = all(is_causal for _, is_causal in path)
    grades = [edge.grade for edge, is_causal in path if is_causal and edge.grade is not None]
    worst = max(grades) if grades else None
    if all_causal and worst is not None and evidence.may_price(worst):
        return Reached(component, None, None, worst, path)
    if all_causal:
        return Reached(
            component,
            BELOW_THRESHOLD,
            f"every hop claims a mechanism, but the weakest runs at evidence grade {worst}, "
            f"outside the published threshold of {threshold}",
            worst,
            path,
        )
    return Reached(
        component,
        NO_MECHANISM,
        "at least one hop is a structural dependency rather than a measured effect, so the "
        "exposure is real and nobody has claimed a mechanism for it",
        worst,
        path,
    )


def radius(graph: "Graph", origin: str, max_depth: int = MAX_DEPTH) -> dict[str, Any]:
    """Every component downstream of `origin`, split by whether it may carry a price."""
    from .model import ModelError

    if origin not in graph.components:
        raise ModelError(f"no component {origin!r} in the graph of {graph.org!r}")
    threshold = evidence.threshold()

    causal_out: dict[str, list["Edge"]] = {}
    structural_in: dict[str, list["Edge"]] = {}
    for edge in graph.edges:
        if edge.type == CAUSAL_EDGE:
            causal_out.setdefault(edge.source, []).append(edge)
        elif edge.type == STRUCTURAL_EDGE:
            structural_in.setdefault(edge.target, []).append(edge)

    best: dict[str, Reached] = {}
    truncated = False

    def walk(node: str, seen: tuple[str, ...], hops: tuple[tuple["Edge", bool], ...]) -> None:
        nonlocal truncated
        onward = [(e, e.target, True) for e in causal_out.get(node, [])]
        onward += [(e, e.source, False) for e in structural_in.get(node, [])]
        if len(hops) >= max_depth:
            truncated = truncated or any(nxt not in seen for _, nxt, _ in onward)
            return
        for edge, nxt, is_causal in sorted(onward, key=lambda t: (t[1], t[0].id)):
            if nxt in seen:
                continue  # simple paths only: a cycle would traverse for ever and say nothing new
            path = hops + ((edge, is_causal),)
            found = classify(nxt, path, threshold)
            incumbent = best.get(nxt)
            if incumbent is None or found.rank < incumbent.rank:
                best[nxt] = found
            walk(nxt, seen + (nxt,), path)

    walk(origin, (origin,), ())

    return {
        "origin": origin,
        "traversal": {
            "inherited_from": "/arckit:impact",
            "max_depth": max_depth,
            "truncated": truncated,
            "known_limits": list(KNOWN_LIMITS),
        },
        "gating": evidence.published(),
        "admitted_to_pricing": [r.as_dict() for r in sorted(best.values(), key=lambda r: r.component) if r.priced],
        "unpriced": [r.as_dict() for r in sorted(best.values(), key=lambda r: r.component) if not r.priced],
    }


def refuse_undeclared_keys(body: dict[str, Any]) -> None:
    """The blast-radius body is closed. A key nobody declared does not serialise."""
    stray = sorted(set(walk_keys(body)) - BODY_KEYS)
    if stray:
        raise ArtefactError(
            f"a blast radius carries undeclared field(s) {', '.join(stray)}. This body is closed: "
            "it is the artefact for what cannot be priced, so there is no slot for a price and "
            "adding one needs an authorising decision ticket."
        )
