"""Depth grades are computed, never typed — the guard against premature done."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin.grades import Capabilities, GradeError, acceptance_criteria


def _capability(directory: Path, name: str, ticket: str, checked: list[int], extra: str = "") -> Path:
    texts = acceptance_criteria(ticket)
    body = f"capability: {name}\nowning_ticket: '{ticket}'\n{extra}criteria:\n"
    for i, text in enumerate(texts, start=1):
        body += f"  - index: {i}\n    text: {json.dumps(text)}\n    checked: {str(i in checked).lower()}\n"
        if i in checked:
            body += "    evidence: a test that fails if this stops being true\n    ticked_by: a build ticket\n"
    path = directory / f"{name}.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_full_is_derived_from_the_checklist(tmp_path: Path) -> None:
    _capability(tmp_path, "all-ticked", "14", checked=[1, 2, 3, 4])
    assert Capabilities.load(directory=tmp_path).require("all-ticked").grade == "full"


def test_no_ticks_is_stub_and_some_ticks_is_partial(tmp_path: Path) -> None:
    _capability(tmp_path, "none", "14", checked=[])
    _capability(tmp_path, "some", "14", checked=[3])
    loaded = Capabilities.load(directory=tmp_path)
    assert loaded.require("none").grade == "stub"
    assert loaded.require("some").grade == "partial"


def test_a_typed_grade_is_rejected_and_names_the_unchecked_criteria(tmp_path: Path) -> None:
    _capability(tmp_path, "liar", "14", checked=[1], extra="grade: full\n")
    with pytest.raises(GradeError) as exc:
        Capabilities.load(directory=tmp_path)
    message = str(exc.value)
    assert "grades are computed" in message
    assert "AC 2" in message and "AC 3" in message and "AC 4" in message
    assert "AC 1 " not in message, "a criterion that IS ticked should not be listed as unchecked"


def test_a_capability_with_no_checklist_fails_to_load(tmp_path: Path) -> None:
    (tmp_path / "empty.yaml").write_text("capability: empty\nowning_ticket: '14'\n", encoding="utf-8")
    with pytest.raises(GradeError, match="declares no depth-grade checklist"):
        Capabilities.load(directory=tmp_path)


def test_a_tick_with_no_witness_is_refused(tmp_path: Path) -> None:
    texts = acceptance_criteria("14")
    (tmp_path / "bare.yaml").write_text(
        "capability: bare\nowning_ticket: '14'\ncriteria:\n"
        + "".join(
            f"  - index: {i}\n    text: {json.dumps(t)}\n    checked: true\n"
            for i, t in enumerate(texts, start=1)
        ),
        encoding="utf-8",
    )
    with pytest.raises(GradeError, match="a tick with no witness"):
        Capabilities.load(directory=tmp_path)


def test_a_checklist_that_drifts_from_its_ticket_is_refused(tmp_path: Path) -> None:
    path = _capability(tmp_path, "drifted", "14", checked=[])
    path.write_text(path.read_text(encoding="utf-8").replace("attestation", "attestation (reworded)", 1), encoding="utf-8")
    with pytest.raises(GradeError, match="drifted from decision ticket"):
        Capabilities.load(directory=tmp_path)


def test_a_checklist_with_the_wrong_number_of_criteria_is_refused(tmp_path: Path) -> None:
    texts = acceptance_criteria("14")[:2]
    (tmp_path / "short.yaml").write_text(
        "capability: short\nowning_ticket: '14'\ncriteria:\n"
        + "".join(
            f"  - index: {i}\n    text: {json.dumps(t)}\n    checked: false\n"
            for i, t in enumerate(texts, start=1)
        ),
        encoding="utf-8",
    )
    with pytest.raises(GradeError, match="drifted from the yardstick"):
        Capabilities.load(directory=tmp_path)


def test_an_ungraded_capability_cannot_be_used(caps: Capabilities) -> None:
    with pytest.raises(GradeError, match="has no depth grade"):
        caps.require("something-nobody-graded")


def test_the_shipped_capabilities_are_all_partial_or_stub(caps: Capabilities) -> None:
    """The walking skeleton must not be able to claim `full` anywhere."""
    grades = {g.capability: g.grade for g in caps}
    assert set(grades) == {
        "causal-layer", "currency-regimes", "domain-model", "honest-build", "provenance",
        "scenario-engine", "sense-move", "synthetic-substrate", "twin-inside-twin",
    }
    assert "full" not in grades.values()


def test_the_depth_block_takes_the_worst_grade_of_the_capabilities_involved(tmp_path: Path) -> None:
    """A `full` capability must not mask a `stub` one — that is the whole point of the block.

    Built from a purpose-made set rather than the shipped one: the shipped capabilities all happen
    to sit at the same grade today, and a fixture that cannot tell `min` from `max` asserts nothing.
    """
    _capability(tmp_path, "finished", "14", checked=[1, 2, 3, 4])
    _capability(tmp_path, "started", "14", checked=[2])
    _capability(tmp_path, "untouched", "14", checked=[])
    caps = Capabilities.load(directory=tmp_path)

    assert caps.depth_block(["finished"])["grade"] == "full"
    assert caps.depth_block(["finished", "started"])["grade"] == "partial"
    assert caps.depth_block(["finished", "untouched"])["grade"] == "stub"
    assert caps.depth_block(["finished", "started", "untouched"])["grade"] == "stub"

    block = caps.depth_block(["finished", "untouched"])
    assert set(block["capabilities"]) == {"finished", "untouched"}
    assert block["capabilities"]["untouched"]["unchecked"], "unchecked criteria travel with the artefact"
    assert block["capabilities"]["finished"]["unchecked"] == []


def test_the_shipped_capabilities_never_reach_full(caps: Capabilities) -> None:
    assert "full" not in {g.grade for g in caps}


def test_a_nested_checkbox_in_a_ticket_is_refused_rather_than_miscounted(tmp_path: Path) -> None:
    """Gluing a sub-item onto its parent would shrink the denominator every grade divides by."""
    (tmp_path / "99-nested.md").write_text(
        "# 99 — a ticket\n\n## Acceptance criteria\n\n"
        "- [ ] Pricing is causally gated.\n"
        "  - [ ] The gate is enforced at emission.\n"
        "- [ ] Ruin-class options are absent, not priced.\n",
        encoding="utf-8",
    )
    with pytest.raises(GradeError, match="nested checkbox"):
        acceptance_criteria("99", tmp_path)


def test_criteria_stop_at_any_heading_not_only_a_level_two_one(tmp_path: Path) -> None:
    (tmp_path / "98-sub.md").write_text(
        "# 98 — a ticket\n\n## Acceptance criteria\n\n"
        "- [ ] The real criterion.\n\n### Notes for later\n\n- [ ] A stray checkbox.\n",
        encoding="utf-8",
    )
    assert acceptance_criteria("98", tmp_path) == ["The real criterion."]


def test_the_parser_reads_the_real_ticket_text_not_something_it_generated() -> None:
    """Pinned literally, because every other test in this file builds fixtures from the parser."""
    assert acceptance_criteria("20") == [
        'A definition of "skill" for this project, and the unit of packaging.',
        "The inventory: which capabilities are skills, which are code, which are inherited from arckit.",
        "A build order with the bootstrap sequence made explicit.",
        "Each skill's owned decision-record (which resolved ticket defines its contract).",
    ]


def test_acceptance_criteria_come_from_the_yardstick_not_the_authors_claim() -> None:
    """A resolved ticket also carries 'Acceptance criteria — all met'; that is a claim, not the list."""
    criteria = acceptance_criteria("07")
    assert len(criteria) == 7
    assert criteria[0].startswith("A named core ontology")
    assert not any(c.startswith("Named core ontology") for c in criteria)
