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

**Paths are reported separately and are never summed** (build ticket 21). They are combined —
which is a different operation, and the difference is the ticket. Two paths that share an edge are
not two independent pieces of evidence, so the dependence is carried structurally: a shared edge is
**drawn once per Monte-Carlo trial** and every path through it uses that same draw. The combined
figure is reported beside the figure the same paths would have produced under an independence
assumption, so the discount is visible rather than asserted — the same move as showing the composed
triple beside the attenuated one.

Its own module, like the Wardley maths and the blast radius, because this is an algorithm over the
graph rather than part of loading it.
"""

from __future__ import annotations

import itertools
import math
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

# How many paths to one component the exact combined figure is computed over.
#
# `ponytail:` inclusion-exclusion is 2^n subsets, so a fixed cap rather than an approximation —
# the exact answer up to the cap and an honest `null` past it beats a figure whose error nobody
# states. Ten paths is 1023 subsets and runs in microseconds; the sampled figure is dependence-
# correct at any path count, so nothing is lost past the cap except the hand-checkable form.
# Raise it, or switch to a sampling-only joint, if a real estate routinely exceeds it.
MAX_EXACT_PATHS = 10

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
        # The combined figure and how it was combined (build ticket 21). `if_independent` is
        # here because the discount has to be falsifiable: a dependence correction whose
        # un-corrected form was never shown is the same unfalsifiable move as an attenuated
        # number with no un-attenuated one beside it.
        "joint", "assumption", "shared_edges", "shares_ancestry", "paths_combined",
        "paths_directional", "paths_dropped_by_cap", "exact", "if_independent",
        "double_counting_avoided", "limit",
    }
)

POSITIVE, NEGATIVE = SIGNS
# What a combined figure's sign says when the paths under it disagree. Not a third direction —
# a refusal to state one, because two routes pushing opposite ways have no single direction.
MIXED = "mixed"


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


def _edge_draws(origin: str, edges: list["Edge"], draws: int, seed: str) -> dict[str, list[float]]:
    """One stream per **edge**, not per path. This is what stops a common cause double-counting.

    A shared edge is drawn once per trial and every path through it reads that same draw, so the
    dependence between two paths is carried by the graph itself rather than imposed afterwards by
    a parametric copula on the outputs (build ticket 21). Seeded by edge id rather than by draw
    order, so traversal order still cannot reach the bytes.
    """
    drawn: dict[str, list[float]] = {}
    for edge in sorted(edges, key=lambda e: e.id):
        triple = Triple.of(edge.causal["elasticity"])  # type: ignore[index]
        stream = pert.stream(f"{seed}:{origin}:{edge.id}")
        drawn[edge.id] = [triple.sample(stream) for _ in range(draws)]
    return drawn


def _path_entry(
    hops: tuple["Edge", ...], edge_draws: dict[str, list[float]], threshold: int
) -> tuple[dict[str, Any], list[float] | None]:
    """One path out of the origin, at all three depths of honesty.

    Returns the entry and the per-trial influences behind its `sampled` block — the second is what
    the combined figure needs, because combining the *summaries* would throw away exactly the
    trial-by-trial agreement that shared ancestry creates.
    """
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
        return entry, None

    composed = triples[0]
    for nxt in triples[1:]:
        composed = composed.times(nxt)

    sampled = [
        scale * math.prod(edge_draws[edge.id][trial] for edge in hops)
        for trial in range(len(edge_draws[hops[0].id]))
    ]
    if sampled and max(sampled) > 1.0:
        # Checked where it is used, not only where it is authored. The schema bounds an
        # elasticity to the unit interval and the schedule bounds every factor to (0, 1], so this
        # cannot fire through the CLI — but seam 2 hands this module a `Graph` directly, and an
        # influence above 1 breaks noisy-OR **silently and backwards**: two paths of 1.5 and 2.0
        # combine to 0.5, which is less than either. Sub-additivity and monotonicity are the two
        # properties the combination rule was chosen for, and both invert with no error raised.
        raise pert.PertError(
            f"a path to {hops[-1].target!r} transmits {max(sampled):.4f} of the shock, which is "
            "more than all of it. An elasticity is a magnitude in the unit interval; above one "
            "the combination rule silently reverses and two strong paths combine to less than "
            "either of them."
        )

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
    return entry, sampled


# -- shared ancestry (build ticket 21) ------------------------------------------------------
#
# The dependence rule, stated once here and published in every propagation that uses it.
#
# Paths are combined by **noisy-OR** — `1 - prod(1 - influence)` — rather than added. Addition is
# the operation that double-counts, and it is also insensitive to dependence: the expected sum of
# two paths is the same whether they share an ancestor or not, so a system that adds cannot even
# express the thing this ticket exists to prevent. Noisy-OR is sub-additive, so two routes for the
# same shock never total more than one certain route, and it is the standard reading of an
# elasticity in the unit interval: the share of the shock this path transmits.
#
# **The declared dependency handling, and its assumption.** Dependence is *structural*, not a
# fitted copula: a shared edge is drawn once per trial, so two paths agree exactly to the extent
# that they share edges. The assumption this makes, stated rather than implied, is that
# **conditional on the shared edges, the disjoint remainders are independent**. Its honest limit:
# a common cause the graph does not contain is not modelled here, so this corrects the
# double-counting the graph can see and makes no claim about the rest. A Gaussian copula on the
# path outputs was rejected — it would need a correlation matrix nobody in this system authors,
# and it would impose a dependence structure alongside the one the graph already states.

JOINT_RULE = (
    "paths to one component are combined by noisy-OR, `1 - prod(1 - influence)`, never summed: "
    "two routes for one shock cannot total more than one certain route. `exact` and "
    "`if_independent` are **expected values**, computed analytically so they are hand-checkable; "
    "the spread is in `sampled` and neither scalar stands in for it"
)
JOINT_ASSUMPTION = (
    "dependence is structural rather than fitted — a shared edge is drawn once per trial, so paths "
    "agree exactly to the extent that they share edges. Assumed: conditional on the shared edges "
    "the disjoint remainders are independent. Not modelled: a common cause the graph does not "
    "contain, so this corrects the double-counting the graph can see and claims nothing about the rest"
)


def _expected_product(paths: list[tuple["Edge", ...]], scales: list[float]) -> float:
    """`E[prod of these paths' influences]`, exactly.

    An edge appearing in two of the paths appears **squared** in the product, and `E[X^2]` exceeds
    `E[X]^2` by the variance. That gap is the whole of the shared-ancestry correction, so it is
    computed from the analytic moments rather than estimated.
    """
    multiplicity: dict[str, tuple["Edge", int]] = {}
    for hops in paths:
        for edge in hops:
            found, count = multiplicity.get(edge.id, (edge, 0))
            multiplicity[edge.id] = (found, count + 1)
    total = math.prod(scales)
    for edge, count in multiplicity.values():
        total *= Triple.of(edge.causal["elasticity"]).raw_moment(count)  # type: ignore[index]
    return total


def _joint(
    combined: list[tuple[dict[str, Any], tuple["Edge", ...], list[float]]],
    directional: int,
    threshold: int,
    dropped: int,
) -> dict[str, Any]:
    """One component's paths, combined with the dependence between them made explicit.

    `dropped` is how many routes the path cap removed **before** this function saw them. It is
    reported rather than assumed zero: the body-level `truncated_by_path_count` flag is no help
    to a reader holding one component's combined figure, and a joint over 32 of 90 routes that
    does not say so is claiming a completeness it has not got.
    """
    hops_of = [hops for _, hops, _ in combined]
    scales = [float(entry["attenuation"]) for entry, _, _ in combined]
    seen: dict[str, int] = {}
    for hops in hops_of:
        for edge in hops:
            seen[edge.id] = seen.get(edge.id, 0) + 1
    shared = sorted(ident for ident, count in seen.items() if count > 1)

    grades = [entry["worst_evidence_grade"] for entry, _, _ in combined]
    worst = max((g for g in grades if g is not None), default=None)
    signs = sorted({str(entry["sign"]) for entry, _, _ in combined})
    base: dict[str, Any] = {
        "rule": JOINT_RULE,
        "assumption": JOINT_ASSUMPTION,
        "paths_combined": len(combined),
        # Named rather than silently dropped: a path past the directional boundary carries no
        # magnitude, so it cannot enter a magnitude, and a reader should see that it was left out.
        "paths_directional": directional,
        # Routes the path cap removed before anything combined them. Zero for every graph small
        # enough to report all of its paths, and named here so it is visible where the figure is
        # rather than only in the body-level traversal block.
        "paths_dropped_by_cap": dropped,
        "sign": signs[0] if len(signs) == 1 else MIXED,
        "shares_ancestry": bool(shared),
        "shared_edges": shared,
        "worst_evidence_grade": worst,
        "may_price": worst is not None and worst <= threshold,
    }
    if len(signs) > 1:
        # **Opposing directions are not netted, and this is a refusal rather than a gap.** One
        # route raises the target and another lowers it. Noisy-OR on their magnitudes would say
        # they reinforce, which is the opposite of what the model states, and subtracting them
        # would be a sum by another name — the operation this whole block exists to avoid. The
        # paths are each still reported, with their own sign and their own magnitude, so a reader
        # has everything they need and no number pretending the tension is resolved.
        base["exact"] = None
        base["if_independent"] = None
        base["limit"] = (
            f"the paths to this component disagree in direction ({', '.join(signs)}), so they are "
            "not combined into one magnitude. Netting them would subtract, and combining them "
            "would claim they reinforce. Each path is reported with its own sign above"
        )
        return base

    # Independence applied to the same marginals — the falsifiability handle. Two figures that
    # differ only in their dependence assumption, so the correction is a difference a reader can
    # take rather than a claim they have to accept.
    marginals = [
        _expected_product([hops], [scale]) for hops, scale in zip(hops_of, scales)
    ]
    if_independent = 1.0 - math.prod(1.0 - m for m in marginals)

    exact: float | None = None
    limit: str | None = None
    if len(combined) <= MAX_EXACT_PATHS:
        # Inclusion-exclusion: `E[1 - prod(1 - I)] = -sum over non-empty subsets of (-1)^|T| E[prod I]`.
        total = 0.0
        for size in range(1, len(combined) + 1):
            for chosen in itertools.combinations(range(len(combined)), size):
                term = _expected_product([hops_of[i] for i in chosen], [scales[i] for i in chosen])
                total -= ((-1) ** size) * term
        exact = pert.quantise(total)
    else:
        limit = (
            f"{len(combined)} paths is past the {MAX_EXACT_PATHS}-path bound on the exact form, "
            "which is 2^n subsets. The sampled figure below carries the dependence at any path "
            "count; only the hand-checkable form stops here"
        )

    joint: dict[str, Any] = {
        **base,
        "exact": exact,
        "if_independent": pert.quantise(if_independent),
        # Note both figures below are the **quantised** ones. Subtracting the raw floats would
        # leave a negative 1e-17 where the two are mathematically equal, and a negative
        # double-counting correction reads as a defect rather than as the absence of one.
        "sampled": pert.summarise(
            [1.0 - math.prod(1.0 - values[trial] for _, _, values in combined)
             for trial in range(len(combined[0][2]))]
        ),
        "worst_evidence_grade": worst,
        "may_price": worst is not None and worst <= threshold,
    }
    if exact is not None:
        # Positive when the shared edges carry **width**, and exactly zero when they are
        # degenerate or absent. A zero-width common cause creates no dependence, so there is
        # nothing to discount — sharing a point estimate is not sharing an uncertainty.
        #
        # Both special cases below are float hygiene, not arithmetic. With no shared edge the two
        # figures are the same number reached by two routes — `m` and `1 - (1 - m)` — and those
        # round-trips disagree in the twelfth digit often enough to publish a correction, of
        # either sign, where there is none. With a shared edge the difference is non-negative by
        # Harris/FKG: every path's influence is non-**decreasing** in every edge draw, so the
        # paths are positively associated and the independent figure is the upper bound. A negative
        # here is therefore always noise, and a correction pointing the wrong way reads as a
        # defect rather than as the absence of one.
        residue = 0.0 if not shared else max(0.0, joint["if_independent"] - exact)
        joint["double_counting_avoided"] = pert.quantise(residue)
    if limit is not None:
        joint["limit"] = limit
    return joint


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

    causal = [e for e in graph.edges if e.type == CAUSAL_EDGE]
    # Drawn once, before any path is walked. Every path through an edge reads that edge's draws,
    # which is what makes shared ancestry structural rather than a correction applied afterwards.
    edge_draws = _edge_draws(origin, causal, draws, seed)

    reached = []
    by_path_count = False
    for component in sorted(found):
        # Ranked *before* truncation, so what survives a cap is the best-evidenced rather than
        # whichever the walk happened to reach first.
        paths = sorted(found[component], key=lambda hops: _rank(hops, threshold))
        dropped = max(0, len(paths) - max_paths)
        if dropped:
            by_path_count = True
            paths = paths[:max_paths]
        entries = []
        combinable: list[tuple[dict[str, Any], tuple["Edge", ...], list[float]]] = []
        for index, hops in enumerate(paths):
            entry, values = _path_entry(hops, edge_draws, threshold)
            # Ranked first, and marked rather than implied: several paths are reported and one of
            # them is the one a reader is being pointed at.
            entry["primary"] = index == 0
            entries.append(entry)
            if values is not None:
                combinable.append((entry, hops, values))
        entry_for: dict[str, Any] = {"component": component, "paths": entries}
        if combinable:
            # Combined, never summed, and only over paths that carry a magnitude at all — a
            # directional path has no number to combine and is counted rather than dropped.
            entry_for["joint"] = _joint(
                combinable, len(entries) - len(combinable), threshold, dropped
            )
        reached.append(entry_for)

    body: dict[str, Any] = {
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
                "several paths out of one shock share ancestry, so summing them double-counts. "
                "They are still never summed: a component with at least one path inside the "
                "attenuation boundary carries a `joint` figure combined by noisy-OR, with the "
                f"dependence carried structurally — {JOINT_ASSUMPTION}"
            ),
        },
        "sampler": pert.sampler(
            seed, draws, "origin and edge, never draw order, so traversal order cannot reach the "
            "bytes and a shared edge is drawn once per trial for every path through it"
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
    # Both refusals here rather than at the verb. Build ticket 22 gave this body a second
    # producer — an intervention embeds a whole propagation — and a guard applied by one caller
    # is a guard the other caller does not have. Enforced where the body is built, so wrapping it
    # cannot weaken it.
    refuse_undeclared_keys(body)
    refuse_directional_magnitudes(body)
    return body


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
        # And the combined figure obeys the same boundary. A component every path to which is
        # directional has no magnitude to combine, so a `joint` there would manufacture one out of
        # nothing — which is the exact failure the boundary exists to prevent (build ticket 21).
        if "joint" in entry and all(p.get("directional_only") for p in entry["paths"]):
            raise ArtefactError(
                f"every path to {entry['component']!r} is directional-only, and it carries a "
                "combined magnitude anyway. Combining no magnitudes gives no magnitude."
            )
