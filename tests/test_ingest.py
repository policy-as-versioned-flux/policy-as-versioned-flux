"""Ingest, STEEP tagging, and automated binding at throughput (build ticket 53).

Assertions are on the emitted `ingest-run` artefact's body, not on internals — `twin/ingest.py`
is as disposable as the rest of this system.
"""

from __future__ import annotations

import inspect

import pytest

from twin import ingest
from twin.artefact import DERIVED
from twin.blob import BlobRef
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.substrate import SubstrateRecipe

COMMAND = ["twin", "ingest"]

_TEMPLATES = (
    "A trading update describes deteriorating margins in the core business.",
    "An industry report flags rising input costs across the sector.",
    "A regulator opens an administrative act against a market participant.",
    "A quarterly filing shows revenue growth slowing for the second straight period.",
)


def _recipe(**overrides: object) -> SubstrateRecipe:
    base: dict[str, object] = {
        "id": "ingest-test-recipe",
        "seed": 13,
        "templates": _TEMPLATES,
        "model_version": "toy-model-v1",
    }
    return SubstrateRecipe(**{**base, **overrides})  # type: ignore[arg-type]


# -- runs unattended, at a declared volume -----------------------------------------------------


def test_ingest_runs_unattended_against_a_declared_substrate_volume(repo: ModelRepo, caps: Capabilities) -> None:
    """No confirmation, no review, no interactive step — a declared count in, an accounted-for
    count out."""
    artefact = ingest.ingest_run(repo, caps, "netflix", _recipe(), 200, COMMAND)
    body = artefact.body
    assert len(body["items"]) + len(body["failures"]) == 200
    assert len(body["items"]) > 0
    assert artefact.kind == ingest.KIND_INGEST_RUN
    assert artefact.mark == DERIVED  # no human gate: nothing here could carry a human's signature
    artefact.digest()  # does not raise: no forbidden key crept into the body


def test_ingest_refuses_a_non_positive_count(repo: ModelRepo, caps: Capabilities) -> None:
    with pytest.raises(ingest.IngestError, match="positive"):
        ingest.ingest_run(repo, caps, "netflix", _recipe(), 0, COMMAND)


def test_ingest_refuses_when_the_overlay_has_no_candidate_component(
    repo: ModelRepo, caps: Capabilities, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ingest, "candidates_of", lambda overlay: [])
    with pytest.raises(ingest.IngestError, match="no component"):
        ingest.ingest_run(repo, caps, "netflix", _recipe(), 5, COMMAND)


# -- every ingested item is provenanced --------------------------------------------------------


def test_every_ingested_item_is_provenanced(repo: ModelRepo, caps: Capabilities) -> None:
    recipe = _recipe()
    artefact = ingest.ingest_run(repo, caps, "netflix", recipe, 30, COMMAND)
    payload_ref = BlobRef.parse(artefact.pins["substrate"])

    for row in artefact.body["items"] + artefact.body["failures"]:
        provenance = row["provenance"]
        assert {"substrate", "recipe", "model_version", "index"} <= provenance.keys()
        assert BlobRef.parse(provenance["substrate"]) == payload_ref
        assert provenance["recipe"] == recipe.id
        assert provenance["model_version"] == recipe.model_version
    indices = sorted(row["provenance"]["index"] for row in artefact.body["items"] + artefact.body["failures"])
    assert indices == list(range(30))


# -- no human gate at entry --------------------------------------------------------------------


def test_ingest_run_has_no_parameter_shaped_like_a_human_gate() -> None:
    params = inspect.signature(ingest.ingest_run).parameters
    for banned in ("review", "reviewed_by", "approve", "approved_by", "confirm", "human"):
        assert banned not in params, f"ingest_run accepts {banned!r} — a human gate could exist at entry"


def test_ingest_run_calls_no_confirmation_or_signing_step() -> None:
    source = inspect.getsource(ingest.ingest_run)
    for banned in ("input(", "sign.human", "approve", "confirm"):
        assert banned not in source, f"ingest_run's own source contains {banned!r}"


def test_every_ingested_item_stays_grade_5_because_binding_is_trusted_downstream_not_at_entry(
    repo: ModelRepo, caps: Capabilities
) -> None:
    """Decision ticket 11 Q2: automated output is grade 5 by construction, and that is exactly
    why no gate is needed at entry — `grade_5_only_path_never_prices` is the downstream gate."""
    artefact = ingest.ingest_run(repo, caps, "netflix", _recipe(), 40, COMMAND)
    assert artefact.body["items"]
    for item in artefact.body["items"]:
        assert item["claim"]["evidence_grade"] == 5
    assert "no human gate" in artefact.body["gate"]


# -- throughput is measured, not assumed --------------------------------------------------------


def test_throughput_is_measured_from_wall_clock_not_assumed(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = ingest.ingest_run(repo, caps, "netflix", _recipe(), 300, COMMAND)
    throughput = artefact.body["throughput"]
    assert throughput["declared_count"] == 300
    assert throughput["elapsed_seconds"] >= 0
    assert throughput["elapsed_seconds"] > 0  # 300 real classify() calls take measurable time
    assert throughput["items_per_second"] == pytest.approx(300 / throughput["elapsed_seconds"])


def test_throughput_report_does_not_divide_by_zero_when_elapsed_is_zero() -> None:
    report = ingest.throughput_report(declared_count=10, elapsed_seconds=0.0)
    assert report["items_per_second"] is None  # measured as "not measurable", never a fabricated rate


# -- depth grade is declared as a computed checklist, never asserted -----------------------------


def test_ingest_declares_its_depth_grade_as_the_computed_sense_move_checklist(
    repo: ModelRepo, caps: Capabilities
) -> None:
    artefact = ingest.ingest_run(repo, caps, "netflix", _recipe(), 10, COMMAND)
    depth = artefact.depth
    computed = caps.require("sense-move")
    assert depth["capabilities"]["sense-move"]["grade"] == computed.grade
    assert depth["capabilities"]["sense-move"]["grade"] != "full"  # honestly partial, not asserted


# -- candidates ------------------------------------------------------------------------------


def test_candidates_of_merges_world_and_overlay_components(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    candidates = ingest.candidates_of(overlay)
    ids = {c["id"] for c in candidates}
    merged = {**overlay.world.components, **overlay.components}
    assert ids == set(merged)
    assert all({"id", "name"} == set(c) for c in candidates)
