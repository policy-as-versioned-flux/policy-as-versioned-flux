"""Causal edges — sign, lag and a PERT elasticity (build ticket 17).

The distinction the whole causal layer rests on: `needs` says the value chain would break,
`influences` says a change here moves something there, by this much, in this direction, after
this long. Propagation on anything less is directional hand-waving, so the fields are required
at the boundary rather than defaulted later.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, verbs
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import CAUSAL_EDGE, SchemaError, degenerate, validate

GRADED = {
    "id": "a-moves-b",
    "type": CAUSAL_EDGE,
    "from": "comp-a",
    "to": "comp-b",
    "sign": "negative",
    "lag_days": 180,
    "elasticity": {"min": 0.2, "mode": 0.45, "max": 0.8},
    "evidence_grade": 3,
}


def test_a_graded_causal_edge_validates() -> None:
    validate("edge", GRADED, "ok")
    validate("edge", {**GRADED, "confidence": 0.5, "note": "why"}, "ok")


@pytest.mark.parametrize("missing", ["sign", "lag_days", "elasticity", "evidence_grade"])
def test_a_causal_edge_missing_any_of_its_assertions_is_refused(missing: str) -> None:
    doc = {k: v for k, v in GRADED.items() if k != missing}
    with pytest.raises(SchemaError, match=missing):
        validate("edge", doc, "planted")


def test_a_person_edge_may_not_carry_a_causal_assertion() -> None:
    """A structural dependency is not a measured effect, and neither is knowing something."""
    with pytest.raises(SchemaError, match="only a 'influences' edge may assert"):
        validate(
            "edge",
            {"id": "an-edge", "type": "knows", "from": "a-person", "to": "a-component", "lag_days": 3},
            "planted",
        )


@pytest.mark.parametrize(
    "triple",
    [
        {"min": 0.5, "mode": 0.2, "max": 0.8},   # mode below min
        {"min": 0.2, "mode": 0.9, "max": 0.8},   # mode above max
        {"min": 0.9, "mode": 0.9, "max": 0.2},   # max below min
        {"min": 0.2, "mode": 0.4},               # not a range
        {"min": 0.2, "mode": 0.4, "max": 0.8, "mean": 0.5},  # closed, like everything else
        {"min": -0.1, "mode": 0.4, "max": 0.8},  # off the interval
    ],
)
def test_an_elasticity_that_is_not_a_calibrated_range_is_refused(triple: dict[str, float]) -> None:
    with pytest.raises(SchemaError):
        validate("edge", {**GRADED, "elasticity": triple}, "planted")


@pytest.mark.parametrize("grade", [0, 6, True, False, "3", 3.0, None])
def test_an_evidence_grade_that_is_not_on_the_ladder_is_refused(grade: object) -> None:
    """`True` matters: it equals 1 in Python, so a boolean would otherwise pass as the weakest
    grade — silently, on an edge nobody graded."""
    with pytest.raises(SchemaError, match="evidence grade"):
        validate("edge", {**GRADED, "evidence_grade": grade}, "planted")


def test_a_degenerate_triple_is_permitted_and_flagged() -> None:
    """False precision is representable. It is never allowed to look like a range."""
    point = {"min": 0.5, "mode": 0.5, "max": 0.5}
    validate("edge", {**GRADED, "elasticity": point}, "permitted")
    assert degenerate(point) is True
    assert degenerate(GRADED["elasticity"]) is False  # type: ignore[arg-type]


def test_a_causal_edge_may_carry_a_calibration_record() -> None:
    """Proof that the range came from the procedure, not that it must have (build ticket 23)."""
    validate("edge", {**GRADED, "calibration": {
        "estimator": "model-steward", "date": "2026-01-01", "reference_class": "similar-edges",
    }}, "ok")


def test_a_structural_edge_may_not_carry_a_calibration_record() -> None:
    """No triple, nothing to calibrate — same refusal as any other causal-only field."""
    with pytest.raises(SchemaError, match="only a 'influences' edge may assert"):
        validate(
            "edge",
            {
                "id": "an-edge", "type": "needs", "from": "comp-a", "to": "comp-b",
                "calibration": {
                    "estimator": "model-steward", "date": "2026-01-01", "reference_class": "x",
                },
            },
            "planted",
        )


@pytest.mark.parametrize("missing", ["estimator", "date", "reference_class"])
def test_a_calibration_record_missing_any_field_is_refused(missing: str) -> None:
    record = {"estimator": "model-steward", "date": "2026-01-01", "reference_class": "similar-edges"}
    del record[missing]
    with pytest.raises(SchemaError, match=missing):
        validate("edge", {**GRADED, "calibration": record}, "planted")


def test_the_pocket_org_shared_elasticity_carries_a_calibration_record(tmp_path: Path) -> None:
    """The one non-degenerate elasticity in the pocket org — the yardstick this ticket needed:
    at least one triple in the repository demonstrably went through the procedure."""
    pocket_repo = ModelRepo.open(fixtures.build_pocket_org(tmp_path / "pocket"))
    graph = Overlay.load(pocket_repo, "pocket").graph()
    edge = next(e for e in graph.edges if e.id == "database-slows-orders")
    assert edge.causal is not None
    assert edge.causal["calibration"] == {
        "estimator": "model-steward",
        "date": "2025-12-15",
        "reference_class": "outage-postmortems-for-shared-database-dependencies-on-order-processing",
    }


def test_the_graded_edge_fixture_reaches_the_emitted_graph(repo: ModelRepo, caps: Capabilities) -> None:
    """The boundary contract the £ and skills tracks test against — generated, never committed."""
    for org, edge_id, flagged in (("netflix", "streaming-displaces-dvd", False),
                                  ("intel", "euv-delay-slips-the-node", True)):
        artefact = verbs.graph(repo, caps, org, verbs.command_for("graph", org=org))
        edges = {e["id"]: e for e in json.loads(artefact.to_bytes())["body"]["edges"]}
        edge = edges[edge_id]
        assert edge["type"] == CAUSAL_EDGE
        assert edge["sign"] in ("positive", "negative")
        assert set(edge["elasticity"]) == {"min", "mode", "max"}
        assert isinstance(edge["lag_days"], int)
        assert edge["evidence_grade"] in (1, 2, 3, 4, 5)
        assert edge["degenerate_elasticity"] is flagged

    structural = [e for e in edges.values() if e["type"] == "needs"]
    assert structural, "the fixture still carries structural edges"
    assert all("elasticity" not in e for e in structural), "a needs edge asserts no quantity"


def test_a_causal_edge_may_not_start_at_a_person(scratch_repo: Path) -> None:
    """A measured effect attributed to a named individual is the thing decision ticket 15 refuses."""
    path = scratch_repo / "orgs" / "netflix" / "edges" / "alex-moves-dvd.yaml"
    path.write_text(
        "id: alex-moves-dvd\ntype: influences\nfrom: alex-rivera\nto: dvd-by-mail\n"
        "sign: negative\nlag_days: 30\nelasticity:\n  min: 0.1\n  mode: 0.2\n  max: 0.3\n"
        "evidence_grade: 2\n",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "a causal edge from a person")

    with pytest.raises(Exception, match="no component 'alex-rivera'"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")
