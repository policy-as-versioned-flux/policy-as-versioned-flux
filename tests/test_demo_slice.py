"""The demo slice's own rendered artefact: thesis, subjects, boundary, AC map
(build ticket 91, decision ticket 22)."""

from __future__ import annotations

from twin import demo_slice
from twin.grades import Capabilities


def test_touched_capabilities_is_a_real_subset_naming_demo_slice(caps: Capabilities) -> None:
    all_names = {g.capability for g in caps}
    touched = set(demo_slice.TOUCHED_CAPABILITIES)
    assert touched <= all_names
    assert 0 < len(touched) < len(all_names), "the boundary is only interesting if it excludes something"
    assert "demo-slice" in touched


def test_boundary_shown_and_absent_partition_the_loaded_capabilities(caps: Capabilities) -> None:
    b = demo_slice.boundary(caps)
    all_names = {g.capability for g in caps}
    assert set(b["shown"]) == set(demo_slice.TOUCHED_CAPABILITIES)
    assert set(b["absent"]) == all_names - set(demo_slice.TOUCHED_CAPABILITIES)
    assert set(b["shown"]) & set(b["absent"]) == set()


def test_boundary_stubbed_entries_are_scoped_to_touched_capabilities_only(caps: Capabilities) -> None:
    b = demo_slice.boundary(caps)
    touched = set(demo_slice.TOUCHED_CAPABILITIES)
    for entry in b["stubbed"]:
        assert entry["id"].rsplit("-", 1)[0] in touched


def test_demo_slice_itself_closes_its_own_unchecked_entries(caps: Capabilities) -> None:
    """This ticket's own work: `demo-slice` was 0/4 before it, so a stale checklist would still
    show demo-slice-1..4 in the register. If they are gone, the checklist genuinely closed."""
    b = demo_slice.boundary(caps)
    ids = {e["id"] for e in b["stubbed"]}
    assert not any(i.startswith("demo-slice-") for i in ids)


def test_summary_composes_all_four_pieces(caps: Capabilities) -> None:
    body = demo_slice.summary(caps)
    assert body["thesis"] == demo_slice.THESIS
    assert {s["org"] for s in body["subjects"]} == {"royal-mail", "netflix", "intel"}
    assert all(s["rationale"] for s in body["subjects"])
    assert set(body["boundary"].keys()) == {"shown", "stubbed", "absent", "depth"}
    assert [ac["index"] for ac in body["acceptance_criteria"]] == [1, 2, 3, 4]
    assert all(ac["build_tickets"] for ac in body["acceptance_criteria"])


def test_the_artefact_is_derived_and_depth_scoped_to_touched_capabilities(caps: Capabilities) -> None:
    art = demo_slice.artefact(["twin", "demo-slice"], caps)
    assert art.mark == "derived"
    assert set(art.depth["capabilities"].keys()) == set(demo_slice.TOUCHED_CAPABILITIES)


def test_artefact_accepts_a_precomputed_body_without_recomputing(caps: Capabilities) -> None:
    body = demo_slice.summary(caps)
    body_id = id(body)
    art = demo_slice.artefact(["twin", "demo-slice"], caps, body=body)
    assert id(art.body) == body_id
