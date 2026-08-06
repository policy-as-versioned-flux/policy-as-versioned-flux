"""Seam 2 — the propagation harness (build ticket 20).

**This module is the named boundary that build tickets 21 and 22 extend.** Shared ancestry (21)
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
    """Two routes out of one shock are not independent, so nothing here aggregates them."""
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

    for absent in ("total", "combined", "aggregate", "sum", "headline"):
        assert absent not in set(walk_keys(target))


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
