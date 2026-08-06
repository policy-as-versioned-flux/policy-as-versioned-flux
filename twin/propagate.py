"""Monte-Carlo propagation through the causal layer, with depth attenuation.

Build ticket 20, from decision ticket 08 (Q3). A shock at one component composes along causal
edges, and three things are reported for every path it takes:

* the **composed** triple — the point-wise product of the authored elasticities, exact arithmetic,
  hand-checkable, and un-attenuated;
* the **attenuated** triple — the composed one scaled by the published depth schedule;
* the **sampled** spread — Monte-Carlo through the graph, so uncertainty compounds honestly
  instead of being averaged away.

All three, side by side, on purpose. A composed product of modes is not the mode of a product, and
an attenuated number that never showed its un-attenuated form makes the attenuation unfalsifiable.

**Structural edges do not propagate here at all.** A `needs` edge says the value chain would break;
it claims no mechanism and no magnitude, so composing anything along it would manufacture a number
where nobody asserted one. Structural exposure is the blast radius (`twin/blast.py`) and it stays
unpriced. This module walks `influences` edges and nothing else.

**Paths are reported separately and are never summed.** Two paths out of one shock share ancestry,
so naive aggregation double-counts; aggregation with explicit dependence is build ticket 21 and
this module leaves the seam rather than filling it with something wrong.

Its own module, like the Wardley maths and the blast radius, because this is an algorithm over the
graph rather than part of loading it.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from . import PACKAGE_DIR, evidence, pert
from .canon import digest_of, walk_keys
from .pert import Triple
from .schema import CAUSAL_EDGE, SIGNS

if TYPE_CHECKING:  # pragma: no cover
    from .model import Edge, Graph

SCHEDULE_PATH = PACKAGE_DIR / "attenuation.yaml"
SCHEMA = "twin.attenuation/v1"

# How far the walk goes before it stops. Deliberately one depth past the schedule, so the first
# depth that carries no number is **visible as directional** rather than invisible by truncation —
# and no deeper, because every further depth is another exponential of paths that say the same
# thing. In a fully-connected causal layer of eleven components, depths 5 and 6 were 97% of the
# paths and 100% of them carried no magnitude.
MAX_DEPTH = 5

# How many paths to one component are reported before the walk stops enumerating them.
#
# `ponytail:` a fixed cap rather than a cost model, for the reason blast.py's depth cap is one —
# simple-path enumeration is exponential in branching factor, and a dense graph produced a 331 MB
# artefact and 2.7 GB of memory before this existed. The artefact says where it stopped, so a
# truncated answer is visible rather than silently partial. Paths are ranked before truncation, so
# what survives is the best-evidenced, not whichever the walk happened to reach first.
MAX_PATHS = 32

# The seed and the draw count are part of the artefact format, not a tuning knob: they are recorded
# in every propagation so a reader can reproduce the sample rather than trust it.
SEED = "twin-propagation-v1"
DRAWS = 2000

# The body, closed, for the reason the blast radius and the priced option set are: this is the
# module with the largest number surface and the one case — directional-only — where a magnitude
# must not appear. A key nobody declared does not serialise.
BODY_KEYS = frozenset(
    {
        "origin", "traversal", "sampler", "attenuation", "calibration", "gating", "elasticities",
        "reached",
        "follows", "max_depth", "max_paths", "truncated", "truncated_by_depth",
        "truncated_by_path_count", "gated_at_grade", "known_limits",
        "structural_edges_do_not_propagate", "paths_are_not_aggregated",
        "engine", "seed", "draws", "seeded_by", "reproducible_within", "significant_digits",
        "pin", "version", "directional_beyond_depth", "digest", "rule", "factors", "depth",
        "factor", "because",
        "document", "sha256", "interval", "steps",
        "pricing_threshold", "path_admission_threshold", "admission_rule", "grades", "grade",
        "name", "admits", "example", "may_price",
        "edge", "from", "to", "evidence_grade", "sign", "lag_days",
        "component", "paths", "primary", "worst_evidence_grade", "path", "directional_only",
        "composed", "attenuated", "sampled", "min", "mode", "max", "mean", "variance",
        "degenerate", "p05", "p50", "p95",
    }
)

POSITIVE, NEGATIVE = SIGNS


class AttenuationError(RuntimeError):
    """The attenuation schedule does not say what it must."""


@lru_cache(maxsize=8)
def schedule(path: Path | None = None) -> dict[str, Any]:
    """The versioned depth schedule, validated on read.

    Validated rather than trusted, for the reason the ladder is: a schedule whose factors have
    quietly stopped decreasing would attenuate nothing while still looking published.
    """
    source = path or SCHEDULE_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise AttenuationError(f"{source}: not a {SCHEMA} document")

    factors = doc.get("factors")
    if not isinstance(factors, list) or not factors:
        raise AttenuationError(
            f"{source}: declares no factors. A schedule with no factors attenuates nothing, which "
            "is the thing depth attenuation exists to prevent."
        )
    for entry in factors:
        # A sentence, not a `KeyError`. Every other malformed field in a versioned data file in
        # this system gets a refusal that says what is wrong; a typo here should too.
        if not isinstance(entry, dict) or "depth" not in entry or "factor" not in entry:
            raise AttenuationError(
                f"{source}: a factor entry is {entry!r}; each declares a depth, a factor and a reason"
            )
    depths = [int(entry["depth"]) for entry in factors]
    if depths != list(range(1, len(depths) + 1)):
        raise AttenuationError(f"{source}: depths must run 1..N in order, got {depths}")
    values = [float(entry["factor"]) for entry in factors]
    if values[0] != 1.0:
        raise AttenuationError(
            f"{source}: depth 1 carries factor {values[0]}, not 1.0. One hop is the authored claim "
            "itself, and scaling it would mean the schedule disagreed with the model."
        )
    for depth, (earlier, later) in enumerate(zip(values, values[1:]), start=1):
        if later >= earlier:
            raise AttenuationError(
                f"{source}: factor at depth {depth + 1} is {later}, not below the {earlier} at "
                f"depth {depth} — influence must fall with depth or this schedule attenuates nothing"
            )
    if values[-1] <= 0.0:
        raise AttenuationError(f"{source}: the deepest factor is {values[-1]}; a factor is above zero")
    for entry in factors:
        if not str(entry.get("because", "")).strip():
            raise AttenuationError(f"{source}: depth {entry['depth']} gives no reason for its factor")

    limit = doc.get("directional_beyond_depth")
    if limit != len(values):
        raise AttenuationError(
            f"{source}: directional_beyond_depth is {limit!r} and the schedule covers depth "
            f"1-{len(values)}. They are the same boundary and must be the same number."
        )
    return doc


def factor(depth: int, path: Path | None = None) -> float | None:
    """The scale at this depth, or `None` where the result is directional only.

    `None` is not zero. Zero would say "no influence", which is a measurement; `None` says the
    chain is too long for the number to mean anything, which is a refusal.
    """
    doc = schedule(path)
    if depth < 1:
        raise AttenuationError(f"depth {depth} is not a depth; propagation starts at one hop")
    if depth > int(doc["directional_beyond_depth"]):
        return None
    return float(doc["factors"][depth - 1]["factor"])


def pin(path: Path | None = None) -> dict[str, Any]:
    doc = schedule(path)
    return {
        "version": int(doc["version"]),
        "directional_beyond_depth": int(doc["directional_beyond_depth"]),
        "digest": digest_of(doc),
    }


def published(path: Path | None = None) -> dict[str, Any]:
    """The schedule as it goes into an artefact: the pin, the rule, and every factor with its why."""
    doc = schedule(path)
    return {
        "pin": pin(path),
        "rule": (
            f"a composed influence is scaled by the factor at its depth; past depth "
            f"{doc['directional_beyond_depth']} it carries a direction and **no magnitude** — the "
            "path is still named, graded and dated, because a direction a reader cannot locate in "
            "the graph is not a direction"
        ),
        "factors": [
            {"depth": int(e["depth"]), "factor": float(e["factor"]), "because": str(e["because"]).strip()}
            for e in doc["factors"]
        ],
    }


def _sign_of(hops: tuple["Edge", ...]) -> str:
    """A chain of two negatives is a positive. Sign travels on the edge, never inside the range."""
    negatives = sum(1 for edge in hops if edge.causal and edge.causal.get("sign") == NEGATIVE)
    return NEGATIVE if negatives % 2 else POSITIVE


def _rank(hops: tuple["Edge", ...], threshold: int) -> tuple[Any, ...]:
    """Priceable beats better-evidenced beats shorter beats lexicographic.

    The same order `blast.Reached.rank` uses, and for the same reason it must be: the blast radius
    and the propagation are emitted from the same origin so a reader can lay them side by side. A
    ranking that put depth first would headline a one-hop model assertion here while the blast
    radius headlined the two-hop measured route, and the reader would be looking at a
    contradiction rather than at two views of one shock.
    """
    grades = [e.grade for e in hops if e.grade is not None]
    worst = max(grades) if grades else 99
    return (0 if worst <= threshold else 1, worst, len(hops), [e.id for e in hops])


def _path_entry(
    origin: str, hops: tuple["Edge", ...], draws: int, seed: str, threshold: int
) -> dict[str, Any]:
    """One path out of the origin, at all three depths of honesty."""
    triples = [Triple.of(edge.causal["elasticity"]) for edge in hops]  # type: ignore[index]
    grades = [e.grade for e in hops if e.grade is not None]
    worst = max(grades) if grades else None
    depth = len(hops)
    scale = factor(depth)

    entry: dict[str, Any] = {
        "depth": depth,
        "sign": _sign_of(hops),
        "worst_evidence_grade": worst,
        "path": [
            {
                "edge": edge.id,
                "from": edge.source,
                "to": edge.target,
                "evidence_grade": edge.grade,
                "sign": edge.causal.get("sign") if edge.causal else None,
                "lag_days": edge.causal.get("lag_days") if edge.causal else None,
            }
            for edge in hops
        ],
        "lag_days": sum(int(e.causal.get("lag_days", 0)) for e in hops if e.causal),
    }

    if scale is None:
        # No **magnitude of influence** — the thing this module computes. Depth, grade and lag are
        # facts about the path rather than measurements of the effect, and they stay, because a
        # direction a reader cannot locate in the graph is not a direction.
        entry["directional_only"] = True
        entry["may_price"] = False
        return entry

    composed = triples[0]
    for nxt in triples[1:]:
        composed = composed.times(nxt)

    stream = pert.stream(f"{seed}:{origin}:{'>'.join(e.id for e in hops)}")
    sampled = []
    for _ in range(draws):
        value = scale
        for triple in triples:
            value *= triple.sample(stream)
        sampled.append(value)

    entry.update(
        {
            "directional_only": False,
            "attenuation": scale,
            "composed": composed.moments(),
            "attenuated": composed.scaled(scale).moments(),
            "sampled": pert.summarise(sampled),
            # The gate, applied where a magnitude appears. A path composed entirely of well-graded
            # hops may carry a price; one weaker hop and the whole path may not. Compared against
            # the threshold this traversal was given, for the reason blast.classify is: the
            # artefact publishes two rules, and a reader must be able to tell which one decided.
            "may_price": worst is not None and worst <= threshold,
        }
    )
    return entry


def propagate(
    graph: "Graph",
    origin: str,
    max_depth: int = MAX_DEPTH,
    draws: int = DRAWS,
    seed: str = SEED,
    max_paths: int = MAX_PATHS,
    threshold: int | None = None,
) -> dict[str, Any]:
    """Every component a shock at `origin` reaches through the causal layer, path by path."""
    from .model import ModelError

    if origin not in graph.components:
        raise ModelError(f"no component {origin!r} in the graph of {graph.org!r}")
    threshold = evidence.threshold() if threshold is None else int(threshold)

    outward: dict[str, list["Edge"]] = {}
    for edge in graph.edges:
        if edge.type == CAUSAL_EDGE:
            outward.setdefault(edge.source, []).append(edge)

    found: dict[str, list[tuple["Edge", ...]]] = {}
    by_depth = False
    by_cycle = False

    def walk(node: str, seen: tuple[str, ...], hops: tuple["Edge", ...]) -> None:
        nonlocal by_depth, by_cycle
        onward = sorted(outward.get(node, []), key=lambda e: (e.target, e.id))
        if len(hops) >= max_depth:
            by_depth = by_depth or any(e.target not in seen for e in onward)
            return
        for edge in onward:
            if edge.target in seen:
                # Simple paths only: a cycle composes for ever and says nothing new. Reported
                # rather than silent, because an artefact that pruned paths and said `truncated:
                # false` is claiming a completeness it does not have.
                by_cycle = True
                continue
            path = hops + (edge,)
            found.setdefault(edge.target, []).append(path)
            walk(edge.target, seen + (edge.target,), path)

    walk(origin, (origin,), ())

    reached = []
    by_path_count = False
    for component in sorted(found):
        # Ranked *before* truncation, so what survives a cap is the best-evidenced rather than
        # whichever the walk happened to reach first.
        paths = sorted(found[component], key=lambda hops: _rank(hops, threshold))
        if len(paths) > max_paths:
            by_path_count = True
            paths = paths[:max_paths]
        entries = [_path_entry(origin, hops, draws, seed, threshold) for hops in paths]
        for index, entry in enumerate(entries):
            # Ranked first, and marked rather than implied: several paths are reported and one of
            # them is the one a reader is being pointed at.
            entry["primary"] = index == 0
        reached.append({"component": component, "paths": entries})

    causal = [e for e in graph.edges if e.type == CAUSAL_EDGE]
    return {
        "origin": origin,
        "traversal": {
            "follows": CAUSAL_EDGE,
            "max_depth": max_depth,
            "max_paths": max_paths,
            "gated_at_grade": threshold,
            "truncated": by_depth or by_cycle or by_path_count,
            "truncated_by_depth": by_depth,
            "truncated_by_path_count": by_path_count,
            "known_limits": [
                "simple paths only, so a cyclic dependency is traversed once and no more"
                + (" — and this graph has one" if by_cycle else ""),
                f"at most {max_paths} paths per component are reported, best-evidenced first",
            ],
            "structural_edges_do_not_propagate": (
                "a needs edge claims no mechanism and no magnitude, so nothing composes along it; "
                "structural exposure is the unpriced blast radius and stays unpriced"
            ),
            "paths_are_not_aggregated": (
                "several paths out of one shock share ancestry, so summing them double-counts; "
                "aggregation with explicit dependence is build ticket 21 and is not done here"
            ),
        },
        "sampler": pert.sampler(
            seed, draws, "origin and path, never draw order, so traversal order cannot reach the bytes"
        ),
        "attenuation": published(),
        "calibration": pert.procedure(),
        "gating": evidence.published(),
        "elasticities": [
            {
                "edge": edge.id,
                "from": edge.source,
                "to": edge.target,
                "evidence_grade": edge.grade,
                "sign": edge.causal.get("sign") if edge.causal else None,
                **Triple.of(edge.causal["elasticity"]).moments(),  # type: ignore[index]
            }
            for edge in sorted(causal, key=lambda e: e.id)
        ],
        "reached": reached,
    }


def refuse_undeclared_keys(body: dict[str, Any]) -> None:
    """The propagation body is closed. A key nobody declared does not serialise.

    Same lock as the blast radius and the priced option set, and this is the module that most
    needs it: it has the largest number surface in the system, and one case — directional-only —
    where a magnitude must not appear at all.
    """
    from .artefact import ArtefactError

    stray = sorted(set(walk_keys(body)) - BODY_KEYS)
    if stray:
        raise ArtefactError(
            f"a propagation carries undeclared field(s) {', '.join(stray)}. This body is closed: "
            "a directional-only path has nowhere to put a magnitude, and adding a slot needs an "
            "authorising decision ticket."
        )


def refuse_directional_magnitudes(body: dict[str, Any]) -> None:
    """A path past the directional boundary carries no magnitude of influence, anywhere.

    The key closure above says the *body* may carry `composed`, `attenuated` and `sampled` —
    because the shallow paths legitimately do. This says the directional ones may not, which is
    the claim the published rule actually makes.
    """
    from .artefact import ArtefactError

    for entry in body.get("reached", []):
        for path in entry["paths"]:
            if not path.get("directional_only"):
                continue
            stray = sorted({"composed", "attenuated", "sampled", "attenuation"} & set(path))
            if stray:
                raise ArtefactError(
                    f"a directional-only path to {entry['component']!r} at depth {path['depth']} "
                    f"carries {', '.join(stray)}. Past the published boundary a chain carries a "
                    "direction and no magnitude — not a small magnitude, none."
                )
