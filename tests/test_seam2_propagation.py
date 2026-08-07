"""Seam 2 — the propagation harness (build tickets 20, 21 and 22).

**This module is the named boundary that build tickets 21 and 22 extended.** Shared ancestry (21)
and intervention-versus-observation (22) assert on the same graphs, through the same helpers, at
the same seam. A test that reached inside the propagation engine instead would become the sunk
cost that resists the rewrite, which is one of the three named failure modes.

Justified because a propagation defect and a graph-validation defect are indistinguishable at seam
1 — both surface as "wrong number" — and the Monte-Carlo layer is where a silent statistical error
is most likely and least visible.

Kept deliberately thin: assertions are on **numerical and structural properties**, never on call
sequences or object shapes. `attenuation reduces influence with depth` is asserted as a monotonic
property across depths, not as a fixed number, because a fixed number would pin the schedule and
the schedule is data somebody is allowed to change.
"""

from __future__ import annotations

from typing import Any

import pytest

from twin import propagate as propagate_mod
from twin.artefact import ArtefactError
from twin.model import Edge, Graph
from twin.propagate import AttenuationError, propagate
from twin.schema import CAUSAL_EDGE, STRUCTURAL_EDGE

# A wide triple: composition through several of these compounds visibly, so "uncertainty compounds
# rather than being averaged away" has something to be true of.
WIDE = {"min": 0.2, "mode": 0.5, "max": 0.8}
# A unit triple composes to exactly 1.0 at every depth, so anything that shrinks with depth
# shrank because of attenuation and for no other reason.
UNIT = {"min": 1.0, "mode": 1.0, "max": 1.0}


def causal(ident: str, source: str, target: str, elasticity: dict[str, float], grade: int = 2) -> Edge:
    return Edge(
        id=ident,
        type=CAUSAL_EDGE,
        source=source,
        target=target,
        causal={
            "sign": "positive",
            "lag_days": 1,
            "elasticity": dict(elasticity),
            "evidence_grade": grade,
        },
    )


def graph_of(edges: tuple[Edge, ...], extra: tuple[str, ...] = ()) -> Graph:
    """A graph made of the nodes these edges name. The helper tickets 21 and 22 build on."""
    names = {e.source for e in edges} | {e.target for e in edges} | set(extra)
    return Graph(
        org="probe",
        components={n: {"id": n, "name": n, "kind": "activity"} for n in sorted(names)},
        people={},
        edges=edges,
    )


def chain(length: int, elasticity: dict[str, float] = WIDE, grade: int = 2) -> Graph:
    """`c0 -> c1 -> ... -> cN`, every hop identical. Depth is then the only variable."""
    return graph_of(
        tuple(causal(f"e{i}", f"c{i}", f"c{i + 1}", elasticity, grade) for i in range(length))
    )


def primary(body: dict[str, Any], component: str) -> dict[str, Any]:
    reached = next(r for r in body["reached"] if r["component"] == component)
    return next(p for p in reached["paths"] if p["primary"])


# -- the property this ticket exists for ----------------------------------------------------


def test_attenuation_reduces_influence_with_depth() -> None:
    """Monotonic across depths, never a fixed number: the schedule is data somebody may change.

    Unit elasticities compose to exactly 1.0 at every depth, so the only thing that can move the
    attenuated value is the attenuation itself.

    **The sampled draws are asserted too**, and that is the leg that matters. `attenuated` is
    `composed.scaled(factor)` — a different code path from the sampler — so a Monte-Carlo that
    silently stopped applying the schedule would leave every other assertion here green while
    inflating the headline `sampled` figure by the whole attenuation.
    """
    depth = propagate_mod.pin()["directional_beyond_depth"]
    body = propagate(chain(depth + 1, UNIT), "c0", draws=512, max_depth=depth + 1)
    numbered = [
        primary(body, f"c{d}")
        for d in range(1, depth + 2)
        if not primary(body, f"c{d}")["directional_only"]
    ]
    assert len(numbered) >= 3, "too few depths carry a number for a monotonic claim to mean anything"

    for shallower, deeper in zip(numbered, numbered[1:]):
        assert deeper["depth"] == shallower["depth"] + 1
        assert deeper["attenuation"] < shallower["attenuation"]
        assert deeper["attenuated"]["mode"] < shallower["attenuated"]["mode"]
        assert deeper["sampled"]["p50"] < shallower["sampled"]["p50"], (
            "the sampled draws did not attenuate; the schedule reached the analytic triple and "
            "not the Monte-Carlo"
        )
    assert numbered[0]["attenuation"] == 1.0, "one hop is the authored claim and is not scaled"
    for entry in numbered:
        assert entry["attenuated"]["mode"] <= entry["composed"]["mode"]
        # A unit chain composes to exactly 1.0, so the sampled median *is* the factor.
        assert entry["sampled"]["p50"] == pytest.approx(entry["attenuation"])


def test_past_the_boundary_a_path_carries_a_direction_and_no_magnitude() -> None:
    """A five-hop elasticity chain is not a number. Not a small number — no magnitude."""
    boundary = propagate_mod.pin()["directional_beyond_depth"]
    body = propagate(chain(boundary + 2, UNIT), "c0", draws=64, max_depth=boundary + 2)

    inside = primary(body, f"c{boundary}")
    beyond = primary(body, f"c{boundary + 1}")
    assert inside["directional_only"] is False and "composed" in inside
    assert beyond["directional_only"] is True
    assert beyond["may_price"] is False
    for absent in ("composed", "attenuated", "sampled", "attenuation"):
        assert absent not in beyond, f"a directional-only path still carries {absent}"
    # The path is still named, graded and dated — a direction a reader cannot locate in the graph
    # is not a direction. What is absent is the magnitude of influence, and only that.
    assert beyond["sign"] in ("positive", "negative")
    assert beyond["path"] and beyond["worst_evidence_grade"] is not None
    propagate_mod.refuse_directional_magnitudes(body)


def test_a_planted_magnitude_on_a_directional_path_is_refused() -> None:
    boundary = propagate_mod.pin()["directional_beyond_depth"]
    body = propagate(chain(boundary + 1, UNIT), "c0", draws=64, max_depth=boundary + 1)
    primary(body, f"c{boundary + 1}")["sampled"] = {"p50": 0.4}

    with pytest.raises(ArtefactError, match="carries sampled"):
        propagate_mod.refuse_directional_magnitudes(body)


def test_the_propagation_body_is_closed() -> None:
    body = propagate(chain(2), "c0", draws=64)
    propagate_mod.refuse_undeclared_keys(body)
    with pytest.raises(ArtefactError, match="undeclared field"):
        propagate_mod.refuse_undeclared_keys({**body, "headline": 0.5})


def test_the_primary_path_is_the_one_the_blast_radius_would_headline() -> None:
    """Two artefacts, one shock. A reader lays them side by side, so they must agree."""
    from twin.blast import radius

    edges = (
        causal("asserted", "c0", "target", WIDE, grade=5),
        causal("solid-a", "c0", "via", WIDE, grade=1),
        causal("solid-b", "via", "target", WIDE, grade=1),
    )
    graph = graph_of(edges)
    chosen = primary(propagate(graph, "c0", draws=64), "target")
    best = next(e for e in radius(graph, "c0")["admitted_to_pricing"] if e["component"] == "target")

    assert [hop["edge"] for hop in chosen["path"]] == [hop["edge"] for hop in best["path"]]
    assert chosen["worst_evidence_grade"] == 1, "the ranked path is the well-evidenced one"
    assert chosen["may_price"] is True


def test_between_two_priceable_paths_the_shorter_one_is_primary() -> None:
    edges = (
        causal("direct", "c0", "target", WIDE, grade=2),
        causal("long-a", "c0", "via", WIDE, grade=2),
        causal("long-b", "via", "target", WIDE, grade=2),
    )
    chosen = primary(propagate(graph_of(edges), "c0", draws=64), "target")
    assert [hop["edge"] for hop in chosen["path"]] == ["direct"]


def test_uncertainty_compounds_rather_than_being_averaged_away() -> None:
    """The reason for sampling. A product of modes is not the mode of a product."""
    body = propagate(chain(3, WIDE), "c0", draws=4000)
    spreads = []
    for depth in (1, 2, 3):
        sampled = primary(body, f"c{depth}")["sampled"]
        spreads.append((sampled["p95"] - sampled["p05"]) / sampled["p50"])
    assert spreads[0] < spreads[1] < spreads[2], f"relative spread did not widen with depth: {spreads}"


# -- structure ------------------------------------------------------------------------------


def test_a_structural_edge_never_propagates() -> None:
    """A `needs` edge claims no mechanism, so nothing composes along it — at any depth."""
    edges = (
        causal("measured", "c0", "c1", WIDE),
        Edge(id="depends", type=STRUCTURAL_EDGE, source="c1", target="c2"),
    )
    body = propagate(graph_of(edges), "c0", draws=64)
    assert [r["component"] for r in body["reached"]] == ["c1"]
    assert all(hop["edge"] != "depends" for r in body["reached"] for p in r["paths"] for hop in p["path"])


def test_paths_are_reported_separately_and_never_summed() -> None:
    """Two routes out of one shock are combined, never summed — and both stay visible.

    Extended at build ticket 21: the combined figure now exists, so the assertion is no longer
    "nothing aggregates" but the stronger pair — every path is still reported individually, and
    the combined figure is strictly below the sum a naive aggregation would have produced.
    """
    edges = (
        causal("left", "c0", "via-a", WIDE),
        causal("right", "c0", "via-b", WIDE),
        causal("join-a", "via-a", "target", WIDE),
        causal("join-b", "via-b", "target", WIDE),
    )
    body = propagate(graph_of(edges), "c0", draws=64)
    target = next(r for r in body["reached"] if r["component"] == "target")

    assert len(target["paths"]) == 2, "both routes must be visible"
    assert sum(1 for p in target["paths"] if p["primary"]) == 1, "exactly one path is the ranked one"
    # At every depth, not only the top level: an aggregate planted inside a path entry is the
    # shape this refusal is actually guarding against.
    from twin.canon import walk_keys

    # Still every name the original refusal listed, `combined` included: the combined figure is
    # keyed `joint`, and `paths_combined` is a count of what went into it rather than a second
    # aggregate. Nothing here needed relaxing to let build ticket 21 land.
    for absent in ("total", "combined", "aggregate", "sum", "headline"):
        assert absent not in set(walk_keys(target))

    naive = sum(p["sampled"]["mean"] for p in target["paths"])
    assert target["joint"]["exact"] < naive, "the combined figure is a sum by another name"


# -- shared ancestry (build ticket 21) ------------------------------------------------------


def diamond(elasticity: dict[str, float] = WIDE) -> Graph:
    """Two paths to `target`, both through the shared first hop `s`. Depth 3 each."""
    return graph_of(
        (
            causal("s", "c0", "mid", elasticity),
            causal("via-a", "mid", "a", elasticity),
            causal("via-b", "mid", "b", elasticity),
            causal("join-a", "a", "target", elasticity),
            causal("join-b", "b", "target", elasticity),
        )
    )


def disjoint(elasticity: dict[str, float] = WIDE) -> Graph:
    """Two paths to `target` of the same depth and strength, sharing no edge at all."""
    return graph_of(
        (
            causal("first-a", "c0", "p", elasticity),
            causal("first-b", "c0", "q", elasticity),
            causal("via-a", "p", "a", elasticity),
            causal("via-b", "q", "b", elasticity),
            causal("join-a", "a", "target", elasticity),
            causal("join-b", "b", "target", elasticity),
        )
    )


def joint_of(graph: Graph, draws: int = 64) -> dict[str, Any]:
    body = propagate(graph, "c0", draws=draws)
    return next(r for r in body["reached"] if r["component"] == "target")["joint"]


def test_shared_ancestry_does_not_double_count() -> None:
    """The property this ticket exists for.

    A diamond and a pair of disjoint paths of the **same depth and the same strength**, so the
    marginals are identical and dependence is the only difference between them. The diamond must
    combine to strictly less, because its two paths are one common cause seen twice.
    """
    shared, apart = joint_of(diamond()), joint_of(disjoint())

    assert shared["shares_ancestry"] is True and shared["shared_edges"] == ["s"]
    assert apart["shares_ancestry"] is False and apart["shared_edges"] == []
    # Identical marginals: the independence reference is computed from the per-path means alone,
    # so if these differ the two graphs were not comparable and the claim below means nothing.
    assert shared["if_independent"] == pytest.approx(apart["if_independent"])
    assert shared["exact"] < apart["exact"], "the diamond did not discount its common cause"
    assert shared["double_counting_avoided"] > 0
    assert apart["double_counting_avoided"] == 0, "disjoint paths need no correction at all"


def test_the_dependence_correction_is_exactly_the_common_cause_variance() -> None:
    """Not merely smaller — smaller by a stated amount, so the correction is falsifiable.

    With degenerate remainders the only width in the diamond is the shared triple, and the gap
    between the combined figure and the independent one is `scale_a * scale_b * Var(shared)`.
    """
    from twin.pert import Triple

    triple = {"min": 0.2, "mode": 0.5, "max": 0.8}
    edges = (
        causal("s", "c0", "mid", triple),
        causal("via-a", "mid", "a", UNIT),
        causal("via-b", "mid", "b", UNIT),
        causal("join-a", "a", "target", UNIT),
        causal("join-b", "b", "target", UNIT),
    )
    joint = joint_of(graph_of(edges))
    scale = propagate_mod.factor(3)
    assert scale is not None
    assert joint["double_counting_avoided"] == pytest.approx(
        scale * scale * Triple.of(triple).variance, rel=1e-9
    )


def test_no_shared_ancestry_reports_an_exact_zero_rather_than_float_residue() -> None:
    """A correction of 1e-14, of either sign, where there is none.

    `exact` and `if_independent` reach the same number by two routes when nothing is shared —
    `m` and `1 - (1 - m)` — and those float round-trips disagree in the twelfth digit often
    enough to publish a discount that does not exist, sometimes negative. Awkward elasticities
    on purpose: the shipped fixtures use round numbers and would never show this.
    """
    awkward_a = {"min": 0.18880988978835878, "mode": 0.2790971271918109, "max": 0.36433917833245766}
    awkward_b = {"min": 0.5096570189316966, "mode": 0.7145731845518067, "max": 0.9057195453436149}
    edges = (
        causal("one", "c0", "mid", awkward_a),
        causal("two", "mid", "target", awkward_b),
        causal("three", "target", "sink", awkward_a),
    )
    joint = next(
        r for r in propagate(graph_of(edges), "c0", draws=8)["reached"] if r["component"] == "target"
    )["joint"]

    assert joint["shares_ancestry"] is False
    assert joint["double_counting_avoided"] == 0.0, "a discount was published where there is none"


def test_routes_that_disagree_in_direction_are_not_combined_at_all() -> None:
    """One route raises the target and another lowers it. There is no single magnitude.

    Combining their magnitudes by noisy-OR would claim they reinforce, which is the opposite of
    what the model says; subtracting them would be the sum this whole block exists to avoid. So
    the joint carries no figure and says why, and every path keeps its own sign and its own
    number. This is the defect review found in the pocket-org fixture, made a property.
    """
    def signed(ident: str, source: str, target: str, sign: str) -> Edge:
        edge = causal(ident, source, target, WIDE)
        return Edge(edge.id, edge.type, edge.source, edge.target, {**dict(edge.causal or {}), "sign": sign})

    edges = (
        signed("up", "c0", "via-a", "positive"),
        signed("down", "c0", "via-b", "negative"),
        signed("join-a", "via-a", "target", "positive"),
        signed("join-b", "via-b", "target", "positive"),
    )
    body = propagate(graph_of(edges), "c0", draws=64)
    target = next(r for r in body["reached"] if r["component"] == "target")

    assert sorted(p["sign"] for p in target["paths"]) == ["negative", "positive"]
    joint = target["joint"]
    assert joint["sign"] == propagate_mod.MIXED
    assert joint["exact"] is None and joint["if_independent"] is None
    assert "sampled" not in joint, "a spread is a magnitude, and there is no single magnitude here"
    assert "disagree in direction" in joint["limit"]
    # The paths keep everything. The refusal is to invent one number, not to report less.
    assert all("composed" in p and "sampled" in p for p in target["paths"])


def test_paths_that_agree_in_direction_carry_that_direction_on_the_combined_figure() -> None:
    joint = joint_of(diamond())
    assert joint["sign"] == "positive", "every hop is positive, so the combination is too"


def test_an_influence_above_one_is_refused_where_it_would_reverse_the_combination() -> None:
    """Two paths of 1.5 and 2.0 combine by noisy-OR to 0.5, which is less than either.

    Sub-additivity and monotonicity are the two properties the combination rule was chosen for,
    and both invert above one. The schema bounds an elasticity to the unit interval, so this
    cannot arrive through the CLI — but seam 2 hands the engine a `Graph` directly, which is
    exactly why the guard is here rather than only at the schema.
    """
    from twin.pert import PertError

    edges = (causal("hot", "c0", "target", {"min": 1.5, "mode": 1.5, "max": 1.5}),)
    with pytest.raises(PertError, match="more than all of it"):
        propagate(graph_of(edges), "c0", draws=8)


def test_the_sampled_joint_carries_the_dependence_too() -> None:
    """The sampler really does draw a common cause once. This is the ticket's other half.

    A tolerance-based check cannot assert this. On the plain diamond the dependence moves the
    mean by 0.2% while Monte-Carlo noise at 20 000 draws is larger than that, so `approx(exact,
    rel=0.02)` passes just as happily against a sampler that drew the shared edge twice — which
    is exactly the defect. Two changes make it bite.

    First, a graph where the common cause is the *only* source of width: a wide shared hop and
    degenerate remainders, so the two paths are perfectly correlated and the gap between the
    dependent and independent figures is 2.6% of the value rather than 0.2%.

    Second, the assertion is **which figure the sample is nearer to**, not how near. That has no
    tolerance to tune and it is the question the ticket actually asks.
    """
    wide = {"min": 0.0, "mode": 0.5, "max": 1.0}
    edges = (
        causal("s", "c0", "mid", wide),
        causal("via-a", "mid", "a", UNIT),
        causal("via-b", "mid", "b", UNIT),
        causal("join-a", "a", "target", UNIT),
        causal("join-b", "b", "target", UNIT),
    )
    joint = joint_of(graph_of(edges), draws=50000)
    sampled = joint["sampled"]["mean"]

    assert joint["exact"] < joint["if_independent"], "the graph does not exercise dependence"
    assert abs(sampled - joint["exact"]) < abs(sampled - joint["if_independent"]), (
        f"the sampled joint ({sampled}) sits nearer the independent figure "
        f"({joint['if_independent']}) than the dependent one ({joint['exact']}) — the shared edge "
        "is being drawn once per path rather than once per trial"
    )


def test_the_sampled_joint_is_smaller_when_ancestry_is_shared() -> None:
    """The same claim without any analytic figure in it at all.

    Two graphs with identical marginals and identical draw counts, differing only in whether the
    paths share an edge. If the sampler ignored the sharing, both would sample the same
    distribution and this comparison would be a coin toss.
    """
    wide = {"min": 0.0, "mode": 0.5, "max": 1.0}
    shared = joint_of(diamond(wide), draws=50000)["sampled"]["mean"]
    apart = joint_of(disjoint(wide), draws=50000)["sampled"]["mean"]
    assert shared < apart, f"shared {shared} is not below independent {apart}"


def test_a_directional_path_carries_no_magnitude_into_the_combined_figure() -> None:
    """Combining no magnitudes gives no magnitude, not a small one."""
    boundary = propagate_mod.pin()["directional_beyond_depth"]
    body = propagate(chain(boundary + 1, UNIT), "c0", draws=64, max_depth=boundary + 1)

    beyond = next(r for r in body["reached"] if r["component"] == f"c{boundary + 1}")
    assert "joint" not in beyond
    inside = next(r for r in body["reached"] if r["component"] == f"c{boundary}")
    assert inside["joint"]["paths_directional"] == 0
    propagate_mod.refuse_directional_magnitudes(body)

    beyond["joint"] = {"exact": 0.1}
    with pytest.raises(ArtefactError, match="Combining no magnitudes"):
        propagate_mod.refuse_directional_magnitudes(body)


def _fan(width: int) -> Graph:
    """`width` disjoint two-hop routes from `c0` to `target`. The path count is the variable."""
    mids = [f"m{i}" for i in range(width)]
    edges = tuple(causal(f"out-{m}", "c0", m, WIDE) for m in mids)
    edges += tuple(causal(f"in-{m}", m, "target", WIDE) for m in mids)
    return graph_of(edges)


def test_the_exact_form_stops_at_its_declared_bound_and_says_so() -> None:
    """A cap that truncated silently would read as "we computed this" when it did not."""
    joint = joint_of(_fan(propagate_mod.MAX_EXACT_PATHS + 2))

    assert joint["paths_combined"] > propagate_mod.MAX_EXACT_PATHS
    assert joint["exact"] is None
    assert "double_counting_avoided" not in joint, "no exact figure means no exact difference"
    assert str(propagate_mod.MAX_EXACT_PATHS) in joint["limit"]
    # The sampled figure carries the dependence at any path count, which is what the limit claims.
    assert joint["sampled"]["mean"] > 0


def test_the_bound_is_inclusive_so_the_last_exact_case_is_still_exact() -> None:
    """Off by one here means the deepest hand-checkable case silently stops being computed.

    The test above uses `bound + 2`, which passes whether the comparison is `<=` or `<`. This is
    the case that tells them apart.
    """
    joint = joint_of(_fan(propagate_mod.MAX_EXACT_PATHS))
    assert joint["paths_combined"] == propagate_mod.MAX_EXACT_PATHS
    assert joint["exact"] is not None, "the last case inside the bound was not computed exactly"
    assert "limit" not in joint


def test_a_component_reached_both_with_and_without_a_magnitude_counts_both() -> None:
    """The directional count is a real count, not a zero nobody ever looks at.

    Needs a component reached by a short path that carries a magnitude *and* a long one past the
    attenuation boundary. Without such a fixture the arithmetic `combined + directional == paths`
    holds for a graph where `directional` is always zero, and that proves nothing.
    """
    boundary = propagate_mod.pin()["directional_beyond_depth"]
    edges: tuple[Edge, ...] = (
        causal("direct", "c0", "target", UNIT),
        *(causal(f"long-{i}", f"c{i}", f"c{i + 1}", UNIT) for i in range(boundary + 1)),
        causal("rejoin", f"c{boundary + 1}", "target", UNIT),
    )
    body = propagate(graph_of(edges), "c0", draws=64, max_depth=boundary + 3)
    target = next(r for r in body["reached"] if r["component"] == "target")
    joint = target["joint"]

    assert sum(1 for p in target["paths"] if p["directional_only"]) >= 1
    assert joint["paths_directional"] >= 1, "a directional path was not counted"
    assert joint["paths_combined"] >= 1
    assert joint["paths_combined"] + joint["paths_directional"] == len(target["paths"])


def test_a_cycle_is_traversed_once_and_the_pruning_is_disclosed() -> None:
    edges = (
        causal("there", "c0", "c1", WIDE),
        causal("back", "c1", "c0", WIDE),
    )
    body = propagate(graph_of(edges), "c0", draws=64)
    assert [r["component"] for r in body["reached"]] == ["c1"]
    # An artefact that pruned paths and said nothing would be claiming a completeness it has not
    # got. `truncated` is the honest flag and the limit is named beside it.
    assert body["traversal"]["truncated"] is True
    assert any("cyclic" in limit for limit in body["traversal"]["known_limits"])


def test_a_cycle_that_does_not_contain_the_origin_is_also_traversed_once() -> None:
    edges = (
        causal("in", "c0", "c1", WIDE),
        causal("round", "c1", "c2", WIDE),
        causal("back", "c2", "c1", WIDE),
    )
    body = propagate(graph_of(edges), "c0", draws=64)
    assert sorted(r["component"] for r in body["reached"]) == ["c1", "c2"]


def test_an_origin_with_no_outgoing_causal_edge_reaches_nothing() -> None:
    edges = (causal("elsewhere", "c1", "c2", WIDE),)
    body = propagate(graph_of(edges, extra=("lonely",)), "lonely", draws=64)
    assert body["reached"] == []
    assert body["traversal"]["truncated"] is False


def test_too_many_paths_to_one_component_are_capped_and_the_cap_is_disclosed() -> None:
    """Simple-path enumeration is exponential; a dense graph produced a 331 MB artefact.

    The cap ranks first and truncates second, so what survives is the best-evidenced rather than
    whichever the walk happened to reach first.
    """
    names = [f"n{i}" for i in range(6)]
    edges = tuple(
        causal(f"{a}-to-{b}", a, b, WIDE, grade=2)
        for i, a in enumerate(["c0", *names])
        for b in [*names[i:], "target"]
        if a != b
    )
    body = propagate(graph_of(edges), "c0", draws=8, max_paths=4)
    target = next(r for r in body["reached"] if r["component"] == "target")

    assert len(target["paths"]) == 4
    assert body["traversal"]["truncated_by_path_count"] is True
    assert body["traversal"]["max_paths"] == 4
    assert sum(1 for p in target["paths"] if p["primary"]) == 1


def test_the_composed_triple_is_the_point_wise_product() -> None:
    """Exact arithmetic, hand-checkable, and reported beside the sampled spread rather than instead."""
    edges = (
        causal("first", "c0", "c1", {"min": 0.3, "mode": 0.5, "max": 0.7}),
        causal("second", "c1", "c2", {"min": 0.4, "mode": 0.4, "max": 0.4}),
    )
    composed = primary(propagate(graph_of(edges), "c0", draws=64), "c2")["composed"]
    assert (composed["min"], composed["mode"], composed["max"]) == pytest.approx((0.12, 0.2, 0.28))


def test_the_sign_of_a_chain_is_the_product_of_its_signs() -> None:
    first = causal("first", "c0", "c1", WIDE)
    second = causal("second", "c1", "c2", WIDE)
    flipped = tuple(
        Edge(e.id, e.type, e.source, e.target, {**dict(e.causal or {}), "sign": "negative"})
        for e in (first, second)
    )
    body = propagate(graph_of(flipped), "c0", draws=64)
    assert primary(body, "c1")["sign"] == "negative"
    assert primary(body, "c2")["sign"] == "positive", "two negatives compose to a positive"


def test_the_gate_reaches_propagation_too() -> None:
    """A path is priceable only when every hop is inside the published threshold."""
    edges = (
        causal("strong", "c0", "c1", WIDE, grade=2),
        causal("asserted", "c1", "c2", WIDE, grade=5),
    )
    body = propagate(graph_of(edges), "c0", draws=64)
    assert primary(body, "c1")["may_price"] is True
    assert primary(body, "c2")["may_price"] is False
    assert primary(body, "c2")["worst_evidence_grade"] == 5


# -- determinism ----------------------------------------------------------------------------


def test_the_sample_is_reproducible_and_independent_of_traversal_order() -> None:
    edges = (
        causal("left", "c0", "via-a", WIDE),
        causal("right", "c0", "via-b", WIDE),
    )
    forwards = propagate(graph_of(edges), "c0", draws=256)
    backwards = propagate(graph_of(tuple(reversed(edges))), "c0", draws=256)
    assert forwards == backwards, "traversal order reached the numbers"


# -- the schedule itself ---------------------------------------------------------------------


def test_a_schedule_whose_factors_stop_falling_is_refused(tmp_path) -> None:
    """It would attenuate nothing while still looking published."""
    flat = tmp_path / "attenuation.yaml"
    flat.write_text(
        propagate_mod.SCHEDULE_PATH.read_text(encoding="utf-8").replace("factor: 0.8", "factor: 1.0"),
        encoding="utf-8",
    )
    with pytest.raises(AttenuationError, match="must fall with depth"):
        propagate_mod.schedule(flat)


def test_a_schedule_that_scales_the_first_hop_is_refused(tmp_path) -> None:
    """Depth 1 is the authored claim; scaling it would mean the schedule disagreed with the model."""
    scaled = tmp_path / "attenuation.yaml"
    scaled.write_text(
        propagate_mod.SCHEDULE_PATH.read_text(encoding="utf-8").replace("factor: 1.0", "factor: 0.9"),
        encoding="utf-8",
    )
    with pytest.raises(AttenuationError, match="depth 1 carries factor"):
        propagate_mod.schedule(scaled)


def test_the_boundary_and_the_schedule_are_one_number(tmp_path) -> None:
    disagreeing = tmp_path / "attenuation.yaml"
    disagreeing.write_text(
        propagate_mod.SCHEDULE_PATH.read_text(encoding="utf-8").replace(
            "directional_beyond_depth: 4", "directional_beyond_depth: 2"
        ),
        encoding="utf-8",
    )
    with pytest.raises(AttenuationError, match="same boundary"):
        propagate_mod.schedule(disagreeing)


def test_the_schedule_is_pinned_so_moving_it_moves_a_digest(tmp_path) -> None:
    moved = tmp_path / "attenuation.yaml"
    moved.write_text(
        propagate_mod.SCHEDULE_PATH.read_text(encoding="utf-8").replace("factor: 0.4", "factor: 0.35"),
        encoding="utf-8",
    )
    assert propagate_mod.pin(moved)["digest"] != propagate_mod.pin()["digest"]
