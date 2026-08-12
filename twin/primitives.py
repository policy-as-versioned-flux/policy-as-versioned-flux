"""The two composable primitives: **intervention** and **time**.

Build tickets 22 and 35, from decision tickets 08 (Q3, Q4) and 13 (Q2). One module because the
design says they are one machine, not two features: *"the engine is two composable primitives —
time and intervention — whose compositions give projection, act-now, the counterfactual, and the
backtest."* Splitting them would make the compositions look like integration work.

**Pearl's counterfactual algorithm, verbatim.** Abduction -> action -> prediction is rewind ->
play -> fast-forward. This module builds the first two:

* `rewind(...)` is **abduction**: restore the model to the state it was in at a declared time.
  Not a filtered view of today's model — a real model state, loaded from the commit that was
  current then, so anything that reads a model reads it unchanged.
* `Do` is **action**: `do(x)` **reports** the incoming causal edges of `x` as cut, and belief
  propagates **downstream only**. Nothing is removed from the graph, and nothing needs to be —
  the walk runs forward from the target, so an incoming edge is never traversed under either
  operation. The cut is a statement about what the operation means, not a mutation.
* `Observe` is the other half of action's contrast: learning a fact updates beliefs
  **bidirectionally**, including about the causes.

**Why the two are separate types rather than a flag.** A system that lets an intervention
back-propagate will cheerfully conclude that taking an action changed the past. A boolean
argument makes that one typo away; two types make it a type error that `mypy` catches before the
code runs, and a refusal if somebody reaches past the type checker.

**What `observe()` reports upstream, and what it does not.** The named ancestors whose belief the
observation updates — with **no magnitude**. An authored elasticity is `d(target)/d(cause)`, and
inverting it into a diagnostic update needs a prior over the causes that nothing in this model
authors. The honest output is therefore the same shape as a path past the attenuation boundary: a
direction, located in the graph, carrying no number. Manufacturing one would be exactly the
false precision the evidence ladder exists to prevent.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .repo import ModelRepo, RepoError
from .schema import CAUSAL_EDGE

if TYPE_CHECKING:  # pragma: no cover
    from .model import Edge, Graph


class PrimitiveError(RuntimeError):
    """One of the two primitives was asked for something it will not do.

    Four causes: an intervention used where an observation was meant (or the reverse), a rewind
    with no time, a rewind to a time that is not an ISO 8601 instant git can compare against, and
    a rewind to before the model existed.
    """


# -- intervention (build ticket 22) ---------------------------------------------------------


@dataclass(frozen=True)
class Do:
    """Pearl's `do(x)`. The target's incoming causal edges are cut; propagation is downstream only.

    Doing a thing does not rewrite its own causes. A separate type from `Observe` on purpose:
    the two have different propagation semantics, and a system that confuses them concludes that
    an action changed the past.
    """

    component: str

    verb = "intervene"
    upstream_semantics = "severed"


@dataclass(frozen=True)
class Observe:
    """A fact learned about the target. Belief updates bidirectionally, causes included.

    Learning that a component moved is evidence about what moved it. Nothing is severed, because
    nothing was done.
    """

    component: str

    verb = "observe"
    upstream_semantics = "updated"


def _incoming(graph: "Graph", component: str) -> list["Edge"]:
    return sorted(
        (e for e in graph.edges if e.type == CAUSAL_EDGE and e.target == component),
        key=lambda e: e.id,
    )


def _ancestor_paths(
    graph: "Graph", component: str, max_depth: int
) -> tuple[dict[str, tuple["Edge", ...]], bool]:
    """The shortest causal path from each ancestor to `component`, and whether the walk stopped.

    Breadth-first, so "shortest" holds by construction and the walk costs one visit per edge.
    Enumerating every simple path and then keeping one per ancestor would be exponential in
    branching factor for a result that discards almost all of it — the shape that produced the
    331 MB artefact recorded at the top of `twin/propagate.py`. The right walk makes the cost
    linear; it does not remove the **depth** bound, which is a separate limit and is reported.
    """
    inward: dict[str, list["Edge"]] = {}
    for edge in graph.edges:
        if edge.type == CAUSAL_EDGE:
            inward.setdefault(edge.target, []).append(edge)

    best: dict[str, tuple["Edge", ...]] = {}
    seen = {component}
    frontier: list[tuple[str, tuple["Edge", ...]]] = [(component, ())]
    truncated = False
    for depth in range(max_depth):
        onward: list[tuple[str, tuple["Edge", ...]]] = []
        for node, hops in frontier:
            for edge in sorted(inward.get(node, []), key=lambda e: (e.source, e.id)):
                if edge.source in seen:
                    continue  # already reached at this depth or shallower, and a cycle stops here
                path = (edge,) + hops
                best[edge.source] = path
                seen.add(edge.source)
                onward.append((edge.source, path))
        if not onward:
            break
        frontier = onward
        if depth == max_depth - 1:
            # There is more above and the bound stopped us. Reported rather than silent, for the
            # reason `propagate` reports its own truncation: a walk that stopped early and said
            # nothing is claiming a completeness it has not got.
            truncated = any(
                edge.source not in seen
                for node, _ in frontier
                for edge in inward.get(node, [])
            )
    return best, truncated


def severed(graph: "Graph", query: Do) -> list[dict[str, Any]]:
    """The incoming causal edges `do()` cuts. **Only accepts `Do`** — that is the whole point.

    An observation severs nothing, so handing this an `Observe` is a category error and is
    refused here as well as by the type checker: the runtime guard is what catches a caller that
    reached past `mypy` through `Any`.
    """
    if not isinstance(query, Do):
        raise PrimitiveError(
            f"severed() takes an intervention; {type(query).__name__} is an observation. "
            "Observation severs nothing, because nothing was done."
        )
    return [
        {
            "edge": edge.id,
            "from": edge.source,
            "to": edge.target,
            "evidence_grade": edge.grade,
            "sign": edge.causal.get("sign") if edge.causal else None,
        }
        for edge in _incoming(graph, query.component)
    ]


UPSTREAM_MAX_DEPTH = 5


def upstream_traversal(max_depth: int, truncated: bool, ran: bool) -> dict[str, Any]:
    """What the upstream walk did, including where it stopped. Published beside what it found."""
    return {
        "walked": ran,
        "max_depth": max_depth,
        "truncated": truncated,
        "known_limits": [
            f"ancestors more than {max_depth} causal hops above are not reported",
            "one path per ancestor, the shortest; a second route to the same cause is not listed",
        ]
        if ran
        else ["an intervention updates nothing upstream, so no walk ran"],
    }


def updated_beliefs(
    graph: "Graph", query: Observe, max_depth: int = UPSTREAM_MAX_DEPTH
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The causal ancestors an observation updates belief about, and how far the walk went.

    **Only accepts `Observe`.** Each ancestor is named, graded and located in the graph, and
    carries **no magnitude** — the diagnostic direction needs a prior over the causes and this
    model authors none.

    The traversal facts come back beside the ancestors rather than being dropped: the walk is
    bounded by depth, and a bound nobody reports is a bound nobody can allow for.
    """
    if not isinstance(query, Observe):
        raise PrimitiveError(
            f"updated_beliefs() takes an observation; {type(query).__name__} is an intervention. "
            "An intervention updates nothing upstream — that is what do() means."
        )
    found, truncated = _ancestor_paths(graph, query.component, max_depth)
    entries = [
        {
            "component": source,
            "depth": len(hops),
            "worst_evidence_grade": max((e.grade for e in hops if e.grade is not None), default=None),
            "path": [{"edge": e.id, "from": e.source, "to": e.target, "evidence_grade": e.grade}
                     for e in hops],
            # The claim, and the refusal, in one field. Reported for the reason a path past the
            # attenuation boundary keeps its name: a direction a reader cannot locate in the
            # graph is not a direction, and a magnitude nobody can derive is not a magnitude.
            "directional_only": True,
        }
        for source, hops in sorted(found.items())
    ]
    return entries, upstream_traversal(max_depth, truncated, ran=True)


def refuse_upstream_under_intervention(body: dict[str, Any]) -> None:
    """An intervention that updated a belief upstream has concluded that acting changed the past.

    The refusal `do()` exists for, enforced where it would show: at emission, on the body, rather
    than trusted to hold because the walk was written the right way round.
    """
    from .artefact import ArtefactError

    if body.get("operation") != Do.verb:
        return
    updated = body.get("upstream") or []
    if updated:
        named = ", ".join(str(e.get("component")) for e in updated)
        raise ArtefactError(
            f"an intervention at {body.get('component')!r} updated belief about {named}. "
            "Observation propagates bidirectionally; intervention propagates downstream only, "
            "because doing a thing does not rewrite its own causes."
        )
    if not isinstance(body.get("severed"), list):
        raise ArtefactError(
            f"an intervention at {body.get('component')!r} records no severed edges, not even an "
            "empty list. do() cuts the incoming edges, and an artefact that does not say which is "
            "not saying what it did."
        )


# -- time (build ticket 35) -----------------------------------------------------------------


def rewind(path: str | Path, at: str) -> ModelRepo:
    """**Abduction.** The model as it stood at `at`, as a model state rather than a filtered view.

    The repository *is* the model and git already dates every version of it, so a past state is a
    commit rather than a projection. This opens the repository at the last commit on or before
    `at`, and everything downstream — loading an overlay, building the graph, propagating,
    intervening — then works on it unchanged. That is what "composes with intervention without
    special-casing" means: there is no rewound mode anywhere in this system, and `do()` at a past
    time is `do()` against a repository that happens to be open at an older commit.

    A filtered view would be the other design, and it fails on exactly the case that matters: a
    filter can hide today's rows but it cannot restore an elasticity that was later recalibrated,
    so a backtest run through one would score the past using today's numbers.

    Rewinding to a time before the model existed **fails explicitly**. An empty state is a
    perfectly good model of an organisation with nothing in it, so returning one would answer a
    question about a model that did not exist with a confident claim that it was empty.
    """
    try:
        return ModelRepo.open_at_time(path, at)
    except RepoError as exc:
        raise PrimitiveError(str(exc)) from None
