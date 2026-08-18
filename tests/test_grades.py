"""Depth grades are computed, never typed — the guard against premature done."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from twin import PACKAGE_DIR
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


def test_only_domain_model_forecast_book_synthetic_substrate_ethics_gate_currency_regimes_and_sense_move_have_earned_full(caps: Capabilities) -> None:
    """The walking skeleton must not be able to claim `full` on say-so — but a capability that
    closes every acceptance criterion with a real, live-checked citation may: `domain-model` was
    the first to (build ticket 79), `forecast-book` the second (build ticket 84, the
    proportionality verdict), `synthetic-substrate` the third (build ticket 87, the planting
    protocol's strength and difficulty-distribution clauses plus anti-contamination and ethics),
    `ethics-gate` the fourth (build ticket 82, the named sensor table and the behavioural-sensing
    misuse catalogue), `currency-regimes` the fifth (build ticket 85, the ethical-harms leg of
    decision ticket 09 AC 4 already answered by the affected-parties register and wired in),
    `sense-move` the sixth (build ticket 80, observation propagation wired into `sense()` and
    exercised on a real signal for each co-flagship).
    Every other shipped capability stays `partial` or `stub`."""
    grades = {g.capability: g.grade for g in caps}
    assert set(grades) == {
        "causal-layer", "currency-regimes", "demo-slice", "domain-model", "enactment",
        "ethics-gate", "forecast-book", "honest-build", "provenance", "scenario-engine",
        "sense-move", "synthetic-substrate", "twin-inside-twin",
    }
    assert grades.pop("domain-model") == "full"
    assert grades.pop("forecast-book") == "full"
    assert grades.pop("synthetic-substrate") == "full"
    assert grades.pop("ethics-gate") == "full"
    assert grades.pop("currency-regimes") == "full"
    assert grades.pop("sense-move") == "full"
    assert "full" not in grades.values()


def test_the_depth_block_takes_the_worst_grade_of_the_capabilities_involved(tmp_path: Path) -> None:
    """A `full` capability must not mask a `stub` one — that is the whole point of the block.

    Built from a purpose-made set rather than the shipped one: a fixture needs a genuine `stub` in
    the mix, and a fixture that cannot tell `min` from `max` asserts nothing.
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


def test_domain_model_forecast_book_synthetic_substrate_ethics_gate_currency_regimes_and_sense_move_are_the_shipped_capabilities_at_full(
    caps: Capabilities,
) -> None:
    grades = {g.capability: g.grade for g in caps}
    assert {c for c, g in grades.items() if g == "full"} == {
        "domain-model", "forecast-book", "synthetic-substrate", "ethics-gate", "currency-regimes",
        "sense-move",
    }


# -- the aggregate is computed, not hand-summed (build ticket 70) -----------------------------


def test_the_aggregate_is_the_sum_of_the_computed_checklists(tmp_path: Path) -> None:
    _capability(tmp_path, "finished", "14", checked=[1, 2, 3, 4])
    _capability(tmp_path, "started", "14", checked=[2])
    assert Capabilities.load(directory=tmp_path).aggregate() == (5, 8)


def test_the_published_aggregate_matches_the_computed_one(caps: Capabilities) -> None:
    """`twin/README.md` publishes the aggregate in prose, and prose does not recompute itself.

    Build ticket 70's audit found the aggregate was the one figure in the depth-grade system that
    was never computed: `twin grade` printed twelve rows and no total, so the published number was
    a hand-sum. This file's own history records it going stale twice — carried as "32" after it had
    moved, then as "35/64" after build ticket 68 moved it again — each time caught by a human
    re-adding twelve numbers, which is the mechanism that failed. This is that check, mechanised.
    """
    checked, total = caps.aggregate()
    # Anchored to the section that owns the table, not to the first bold fraction in the file:
    # `**11 of 41**` appears elsewhere, and a test that reads whichever came first would start
    # asserting about a different number the day somebody moves a paragraph.
    section = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8").split("## What is honestly built", 1)
    assert len(section) == 2, "twin/README.md no longer has the section that publishes the aggregate"
    published = re.search(r"\*\*(\d+) of (\d+)\*\*", section[1])
    assert published, "twin/README.md no longer publishes an aggregate for the capability table"
    assert (int(published.group(1)), int(published.group(2))) == (checked, total)


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
