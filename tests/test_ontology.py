"""The named core ontology: generated from schema.py's own vocabulary, never authored
(build ticket 79, decision ticket 07 AC 1 and AC 6)."""

from __future__ import annotations

import pytest

from twin import model, schema
from twin.grades import Capabilities
from twin.ontology import (
    ATTACHMENT,
    KIND,
    _check_attachment_vocabulary,
    artefact,
    backbone,
    entity_types,
    published,
    relationship_types,
)


def test_every_schema_kind_is_a_named_entity_type() -> None:
    """Adding or removing a `schema.SCHEMAS` entry changes this with no second edit anywhere."""
    assert {e["kind"] for e in entity_types()} == set(schema.SCHEMAS)


def test_an_entity_types_fields_are_read_from_its_own_schema_not_retyped() -> None:
    component = next(e for e in entity_types() if e["kind"] == "component")
    assert component["required_fields"] == sorted(schema.SCHEMAS["component"].required)
    assert component["optional_fields"] == sorted(schema.SCHEMAS["component"].optional)


def test_every_edge_type_is_classified_into_exactly_one_family() -> None:
    rels = {r["type"]: r["family"] for r in relationship_types()}
    assert rels[schema.STRUCTURAL_EDGE] == "structural"
    assert rels[schema.CAUSAL_EDGE] == "causal"
    for person_edge in schema.PERSON_EDGES:
        assert rels[person_edge] == "knowledge"
    assert set(rels) == set(schema.EDGE_TYPES)


def test_a_causal_edge_carries_a_measured_effect_and_a_structural_edge_does_not() -> None:
    rels = {r["type"]: r for r in relationship_types()}
    assert "evidence grade" in rels[schema.CAUSAL_EDGE]["carries"]
    assert "no measured effect" in rels[schema.STRUCTURAL_EDGE]["carries"]


def test_the_backbone_is_the_wardley_spine() -> None:
    spine = backbone()
    assert spine["component_kinds"] == list(schema.COMPONENT_KINDS)
    assert spine["evolution_stages"] == list(schema.EVOLUTION)


def test_ac6_names_exactly_the_four_things_the_ticket_names() -> None:
    assert {a["named"] for a in ATTACHMENT} == {"£/risk", "people", "assets", "signals"}


def test_ac6_attachment_vocabulary_is_checked_against_real_schema_kinds() -> None:
    """Passes today because every `schema_kinds` entry names a real schema.py kind — proof this
    is checked, not merely asserted in prose."""
    _check_attachment_vocabulary()  # raises on drift; this is the live check


def test_ac6_attachment_vocabulary_catches_a_renamed_schema_kind(monkeypatch: pytest.MonkeyPatch) -> None:
    """The guard actually bites: point one entry at a kind schema.py does not declare."""
    import twin.ontology as ontology_mod

    broken = ({**ATTACHMENT[0], "schema_kinds": ("not-a-real-kind",)},) + ATTACHMENT[1:]
    monkeypatch.setattr(ontology_mod, "ATTACHMENT", broken)
    with pytest.raises(KeyError, match="not-a-real-kind"):
        ontology_mod._check_attachment_vocabulary()


def test_published_calls_the_vocabulary_check() -> None:
    body = published()
    assert len(body["entity_types"]) == len(schema.SCHEMAS)
    assert len(body["relationship_types"]) == len(schema.EDGE_TYPES)
    assert len(body["attachment"]) == 4


def test_the_artefact_is_derived_and_pinned_to_the_source_it_read(caps: Capabilities) -> None:
    art = artefact(["twin", "ontology"], caps)
    assert art.kind == KIND
    assert art.mark == "derived"
    assert art.depth["capabilities"].keys() == {"domain-model"}
    assert "schema_sha256" in art.pins and "model_sha256" in art.pins


def test_the_artefact_reproduces_byte_for_byte(caps: Capabilities) -> None:
    first = artefact(["twin", "ontology"], caps)
    second = artefact(["twin", "ontology"], caps)
    assert first.digest() == second.digest()


def test_people_attach_through_the_edge_types_model_py_actually_uses() -> None:
    """AC 6's people entry names `edge`; confirm `model.Graph.bus_factor` — the one place a person
    edge is actually read back out of the graph — filters on the identical `schema.PERSON_EDGES`
    constant this artefact cites, rather than a second, hand-typed list that could disagree with
    it."""
    import inspect

    people_entry = next(a for a in ATTACHMENT if a["named"] == "people")
    assert "edge" in people_entry["schema_kinds"]
    assert "PERSON_EDGES" in inspect.getsource(model.Graph.bus_factor)
