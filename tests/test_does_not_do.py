"""The does-not-do register: generated from the depth-grade checklists, never authored
(build ticket 77, decision tickets 15 and 22)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin.does_not_do import artefact, published, register
from twin.grades import Capabilities, acceptance_criteria


def _capability(directory: Path, name: str, ticket: str, checked: list[int]) -> Path:
    texts = acceptance_criteria(ticket)
    body = f"capability: {name}\nowning_ticket: '{ticket}'\ncriteria:\n"
    for i, text in enumerate(texts, start=1):
        body += f"  - index: {i}\n    text: {json.dumps(text)}\n    checked: {str(i in checked).lower()}\n"
        if i in checked:
            body += "    evidence: a test that fails if this stops being true\n    ticked_by: a build ticket\n"
    path = directory / f"{name}.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_a_full_capability_contributes_nothing(tmp_path: Path) -> None:
    _capability(tmp_path, "finished", "14", checked=[1, 2, 3, 4])
    caps = Capabilities.load(directory=tmp_path)
    assert register(caps) == []


def test_one_entry_per_unchecked_criterion(tmp_path: Path) -> None:
    _capability(tmp_path, "started", "14", checked=[2])
    caps = Capabilities.load(directory=tmp_path)
    entries = register(caps)
    assert {e["id"] for e in entries} == {"started-1", "started-3", "started-4"}
    assert all(e["does_not_do"] and e["because"] and e["source"] for e in entries)

    texts = acceptance_criteria("14")
    entry = next(e for e in entries if e["id"] == "started-3")
    assert entry["does_not_do"] == texts[2]
    assert "14" in entry["because"] and "3" in entry["because"] and "'partial'" in entry["because"]
    assert entry["source"] == "decision ticket 14, capability 'started'"


def test_the_register_is_deterministically_ordered(tmp_path: Path) -> None:
    _capability(tmp_path, "zeta", "14", checked=[])
    _capability(tmp_path, "alpha", "14", checked=[])
    caps = Capabilities.load(directory=tmp_path)
    entries = register(caps)
    assert [e["id"] for e in entries] == [
        "alpha-1", "alpha-2", "alpha-3", "alpha-4", "zeta-1", "zeta-2", "zeta-3", "zeta-4",
    ]


def test_the_register_tracks_the_checklist_live_not_a_cache(tmp_path: Path) -> None:
    """Checking one criterion off removes exactly its entry — proof the register is a live read of
    `Capabilities`, not a snapshot that happened to agree with it once."""
    _capability(tmp_path, "started", "14", checked=[2])
    before = register(Capabilities.load(directory=tmp_path))
    _capability(tmp_path, "started", "14", checked=[2, 3])
    after = register(Capabilities.load(directory=tmp_path))
    assert len(before) - len(after) == 1
    assert "started-3" in {e["id"] for e in before}
    assert "started-3" not in {e["id"] for e in after}


def test_published_totals_match_the_capabilities_aggregate(tmp_path: Path) -> None:
    _capability(tmp_path, "finished", "14", checked=[1, 2, 3, 4])
    _capability(tmp_path, "started", "14", checked=[2])
    caps = Capabilities.load(directory=tmp_path)
    body = published(caps)
    checked, total = caps.aggregate()
    assert (body["criteria_checked"], body["criteria_total"]) == (checked, total)
    assert body["capabilities_surveyed"] == 2
    assert len(body["entries"]) == total - checked


def test_the_artefact_is_derived_never_authored(tmp_path: Path) -> None:
    _capability(tmp_path, "started", "14", checked=[2])
    caps = Capabilities.load(directory=tmp_path)
    art = artefact(["twin", "does-not-do"], caps)
    assert art.mark == "derived"
    assert art.depth["capabilities"].keys() == {"started"}
    assert len(art.body["entries"]) == 3


def test_register_is_complete_against_the_shipped_capabilities(caps: Capabilities) -> None:
    """No silent omission: the register names exactly every unchecked criterion that exists today,
    never a sampled or capped subset of it."""
    checked, total = caps.aggregate()
    assert len(register(caps)) == total - checked


def test_an_ungraded_capability_appearing_is_impossible_by_construction(caps: Capabilities) -> None:
    """Every entry names a capability `Capabilities` actually loaded — there is no second, looser
    source an entry could be invented from."""
    names = {g.capability for g in caps}
    assert {e["id"].rsplit("-", 1)[0] for e in register(caps)} <= names
