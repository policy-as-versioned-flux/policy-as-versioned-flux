"""The Wardley spine — evolution positions and D/K/R (build ticket 14).

One property test per relation, as the ticket asks. No property-testing library: the relations
are two-variable and bounded, so a deterministic grid covers the space exactly and adds no
dependency. The grid is also reproducible, which a random search is not.

The three worked examples from arckit's own `mathematical-models.md` are asserted directly. They
are the evidence that the maths was **inherited** rather than reimplemented from the prose: if a
port drifted, the published example is what would catch it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, verbs, wardley
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

GRID = [i / 20 for i in range(21)]  # 0.00 .. 1.00 in twentieths, both axes


def test_the_inherited_worked_examples_still_hold() -> None:
    """arckit mathematical-models.md section B, its own three examples.

    The third is asserted at full precision rather than at the figure arckit prints: the source
    shows `0.85 x 0.75 = 0.64`, which is 0.6375 rounded to two decimals. Inheriting the rounding
    would put a display convention into an artefact that has to be byte-reproducible.
    """
    assert wardley.differentiation_pressure(0.80, 0.30) == pytest.approx(0.56)
    assert wardley.commodity_leverage(0.20, 0.90) == pytest.approx(0.72)
    assert wardley.dependency_risk(0.85, 0.25) == 0.85 * 0.75 == pytest.approx(0.6375)


def test_differentiation_pressure_over_the_whole_grid() -> None:
    for visibility in GRID:
        for evolution in GRID:
            d = wardley.differentiation_pressure(visibility, evolution)
            assert 0.0 <= d <= 1.0
            assert (d == 0.0) == (visibility == 0.0 or evolution == 1.0)
            # Rises with visibility, falls with maturity — the whole point of the relation.
            assert d >= wardley.differentiation_pressure(max(0.0, visibility - 0.05), evolution)
            assert d >= wardley.differentiation_pressure(visibility, min(1.0, evolution + 0.05))


def test_commodity_leverage_over_the_whole_grid() -> None:
    for visibility in GRID:
        for evolution in GRID:
            k = wardley.commodity_leverage(visibility, evolution)
            assert 0.0 <= k <= 1.0
            assert (k == 0.0) == (visibility == 1.0 or evolution == 0.0)
            assert k >= wardley.commodity_leverage(min(1.0, visibility + 0.05), evolution)
            assert k >= wardley.commodity_leverage(visibility, max(0.0, evolution - 0.05))


def test_dependency_risk_over_the_whole_grid() -> None:
    """R is D read across a dependency: the visible end's visibility, the depended-on end's maturity."""
    for visibility_a in GRID:
        for evolution_b in GRID:
            r = wardley.dependency_risk(visibility_a, evolution_b)
            assert 0.0 <= r <= 1.0
            assert r == wardley.differentiation_pressure(visibility_a, evolution_b)
            assert (r == 0.0) == (visibility_a == 0.0 or evolution_b == 1.0)


def test_every_stage_maps_to_its_own_band_and_back() -> None:
    for name, low, high in wardley.BANDS:
        assert wardley.band(name) == (low, high)
        assert wardley.stage_of(wardley.midpoint(name)) == name
        assert wardley.stage_of(low) == name
    assert wardley.stage_of(1.0) == "commodity", "the top of the axis is inside the last band"
    with pytest.raises(wardley.WardleyError):
        wardley.stage_of(1.5)


def test_a_position_outside_its_declared_stage_is_refused() -> None:
    base = {"id": "a-thing", "name": "A thing", "kind": "activity", "visibility": 0.5}
    validate("component", {**base, "evolution": "product", "evolution_position": 0.6}, "ok")
    with pytest.raises(SchemaError, match="outside the 'product' band"):
        validate("component", {**base, "evolution": "product", "evolution_position": 0.9}, "planted")
    unplaced = {"id": "a-thing", "name": "A thing", "kind": "activity"}
    with pytest.raises(SchemaError, match="without the evolution stage"):
        validate("component", {**unplaced, "evolution_position": 0.6}, "planted")


def test_a_component_positioned_on_one_axis_only_is_refused() -> None:
    """Half a position reads as a whole one, so there is no half."""
    base = {"id": "a-thing", "name": "A thing", "kind": "activity"}
    validate("component", base, "ok — off the map entirely")
    with pytest.raises(SchemaError, match="missing visibility"):
        validate("component", {**base, "evolution": "product"}, "planted")
    with pytest.raises(SchemaError, match="missing evolution"):
        validate("component", {**base, "visibility": 0.4}, "planted")


def test_an_authored_position_is_distinguishable_from_a_derived_one() -> None:
    derived = wardley.Position.of("a", {"evolution": "product", "visibility": 0.5})
    authored = wardley.Position.of("a", {"evolution": "product", "visibility": 0.5, "evolution_position": 0.72})
    assert derived is not None and authored is not None
    assert derived.evolution == 0.625 and not derived.position_authored
    assert authored.evolution == 0.72 and authored.position_authored
    assert wardley.Position.of("a", {"kind": "activity"}) is None, "never guessed"


def test_the_map_renders_from_the_graph_with_no_authoring_step(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = verbs.graph(repo, caps, "netflix", verbs.command_for("graph", org="netflix"))
    body = json.loads(artefact.to_bytes())["body"]
    graph = Overlay.load(repo, "netflix").graph()

    assert body["wardley"] == graph.wardley(), "the artefact's map is the graph's map"
    assert {p["component"] for p in body["wardley"]["positions"]} <= set(body["rollups"] and graph.components)
    assert body["wardley"]["axis"]["action_bands_inherited"] is False

    risks = {(r["from"], r["to"]): r["dependency_risk"] for r in body["wardley"]["dependency_risk"]}
    assert risks[("streaming-experience", "cloud-compute")] == pytest.approx(0.9 * (1 - 0.875))

    rendered = wardley.plot(body["wardley"])
    for entry in body["wardley"]["positions"]:
        assert entry["component"] in rendered, "every positioned component appears in the render"


def test_a_component_with_no_position_is_named_rather_than_dropped(scratch_repo: Path) -> None:
    """An omission the reader cannot see is worse than a gap they can."""
    path = scratch_repo / "orgs" / "netflix" / "components" / "unplaced.yaml"
    path.write_text("id: unplaced\nname: Unplaced\nkind: practice\n", encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "a component with no position")

    graph = Overlay.load(ModelRepo.open(scratch_repo), "netflix").graph()
    assert "unplaced" in graph.wardley()["unpositioned"]
    assert "unplaced" not in {p["component"] for p in graph.wardley()["positions"]}
