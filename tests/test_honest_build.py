"""`honest-build` (build ticket 90, decision ticket 20): the skill definition and the capability
inventory, as data instead of prose.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from twin.honest_build import (
    CAPABILITY_INVENTORY,
    INHERITED_KIND,
    SKILL_OWNING_TICKET,
    CapabilityEntry,
    HonestBuildError,
    inventory_summary,
    validate_inventory,
    validate_owning_tickets,
)
from twin.skills import CODE_KIND, SKILL_KIND, SKILL_DEFINITION, classify_by_determinism


# -- AC 1: the determinism-split test is a queryable function, not only prose -------------------


def test_classify_by_determinism_matches_decision_ticket_20s_own_words() -> None:
    """"if it must be reproducible from pins -> code; if it is a judgement landing at grade 5 ->
    skill" (decision ticket 20 Q1) — as a predicate, not a docstring a human has to keep in sync."""
    assert classify_by_determinism(True) == CODE_KIND
    assert classify_by_determinism(False) == SKILL_KIND


def test_skill_definition_is_a_real_string_not_empty() -> None:
    assert isinstance(SKILL_DEFINITION, str) and SKILL_DEFINITION.strip()


# -- AC 2: the inventory, checked against real files ---------------------------------------------


def test_the_real_inventory_validates_clean() -> None:
    """The shipped `CAPABILITY_INVENTORY`, checked against the real `twin/` tree and the real
    `skill-thresholds.yaml` — this is the actual proof, not a fixture standing in for it."""
    validate_inventory()


def test_the_real_owning_tickets_validate_clean() -> None:
    validate_owning_tickets()


def test_every_named_kind_is_one_of_the_three(tmp_path: Path) -> None:
    for entry in CAPABILITY_INVENTORY:
        assert entry.kind in (CODE_KIND, SKILL_KIND, INHERITED_KIND)


def test_a_capability_declared_twice_is_refused(tmp_path: Path) -> None:
    dupe = CAPABILITY_INVENTORY + (CAPABILITY_INVENTORY[0],)
    with pytest.raises(HonestBuildError, match="declared twice"):
        validate_inventory(inventory=dupe)


def test_an_unknown_kind_is_refused() -> None:
    bad = (replace(CAPABILITY_INVENTORY[0], kind="mythical"),)
    with pytest.raises(HonestBuildError, match="unknown kind"):
        validate_inventory(inventory=bad)


def test_a_code_entry_whose_module_does_not_exist_is_refused() -> None:
    bad = (replace(CAPABILITY_INVENTORY[0], module="no-such-module.py"),)
    with pytest.raises(HonestBuildError, match="not a real, non-empty file"):
        validate_inventory(inventory=bad)


def test_a_skill_entry_with_no_threshold_is_refused() -> None:
    fake_skill = CapabilityEntry(
        "not-a-real-skill", SKILL_KIND, "signal_classify.py", False, "no threshold entry exists"
    )
    with pytest.raises(HonestBuildError, match="no threshold"):
        validate_inventory(inventory=(fake_skill,))


def test_a_kind_that_contradicts_its_own_determinism_flag_is_refused() -> None:
    """AC 1's predicate is genuinely load-bearing in AC 2: a hand-edited `kind` cannot silently
    disagree with the `reproducible_from_pins` flag the same entry declares."""
    contradiction = replace(CAPABILITY_INVENTORY[0], reproducible_from_pins=False)  # was code
    with pytest.raises(HonestBuildError, match="determinism-split test reads as a skill"):
        validate_inventory(inventory=(contradiction,))

    skill_entry = next(e for e in CAPABILITY_INVENTORY if e.kind == SKILL_KIND)
    contradiction2 = replace(skill_entry, reproducible_from_pins=True)
    with pytest.raises(HonestBuildError, match="determinism-split test reads as code"):
        validate_inventory(inventory=(contradiction2,))


def test_inventory_summary_groups_by_kind() -> None:
    summary = inventory_summary()
    assert set(summary) == {CODE_KIND, SKILL_KIND, INHERITED_KIND}
    assert sum(len(v) for v in summary.values()) == len(CAPABILITY_INVENTORY)
    assert "signal-classify" in summary[SKILL_KIND]
    assert "wardley-maths" in summary[INHERITED_KIND]


# -- the ethics-gate finding: a corrected classification, not a forced consistent one ------------


def test_ethics_gate_is_classified_code_not_skill() -> None:
    """The open tension build ticket 90 named: decision ticket 20 Q3 lists `ethics-gate` as the
    sixth skill, but the surface its own threshold entry scores (`ethics_gate.scorer()`, which
    compares only `admitted` and `stopped_at`) is a deterministic rule engine over an
    already-quantified payload — it fails decision ticket 20 Q1's own test. Corrected here rather
    than forced onto the skill side to keep the six-skill count consistent-looking."""
    entry = next(e for e in CAPABILITY_INVENTORY if e.name == "ethics-gate")
    assert entry.kind == CODE_KIND
    assert entry.reproducible_from_pins is True
    assert "ethics-gate" not in SKILL_OWNING_TICKET


def test_ethics_gates_own_scorer_only_reads_the_deterministic_ladder_surface() -> None:
    """Grounds the finding above in the actual code, not just an assertion about it: the function
    `skill-thresholds.yaml`'s `ethics-gate` entry is scored through never touches
    `classify_gameability` — the one piece of the module that reads free text."""
    import inspect

    from twin.ethics_gate import scorer

    body = inspect.getsource(scorer)
    assert "classify_gameability" not in body
    assert "admitted" in body and "stopped_at" in body


# -- AC 4: the skill-owning-ticket map, checked against real ticket files -----------------------


def test_owning_tickets_are_exactly_the_skill_classified_capabilities() -> None:
    skill_names = {e.name for e in CAPABILITY_INVENTORY if e.kind == SKILL_KIND}
    assert set(SKILL_OWNING_TICKET) == skill_names
    assert len(skill_names) == 5  # signal-classify, causal-claims, evolution-judge,
    #                               substrate-generator, gameplay-lens — ethics-gate excluded


def test_a_skill_with_no_owning_ticket_is_refused() -> None:
    extra_skill = CapabilityEntry(
        "another-fake-skill", SKILL_KIND, "signal_classify.py", False, "no owning ticket declared"
    )
    with pytest.raises(HonestBuildError, match="no owning ticket"):
        validate_owning_tickets(inventory=CAPABILITY_INVENTORY + (extra_skill,))


def test_an_owning_ticket_naming_a_non_skill_capability_is_refused() -> None:
    with pytest.raises(HonestBuildError, match="does not classify"):
        validate_owning_tickets(mapping={**SKILL_OWNING_TICKET, "ethics-gate": "15"})


def test_an_owning_ticket_that_names_no_real_file_is_refused(tmp_path: Path) -> None:
    with pytest.raises(HonestBuildError, match="has no file under"):
        validate_owning_tickets(
            mapping={**SKILL_OWNING_TICKET, "signal-classify": "999"}, tickets_dir=tmp_path
        )
