"""The misuse catalogue and constraint-removal logging (build ticket 62)."""

from __future__ import annotations

from pathlib import Path

import pytest

from twin.misuse import (
    BEHAVIOURAL_CATALOGUE_PATH,
    CATALOGUE_PATH,
    MisuseError,
    compute_attractiveness,
    load_catalogue,
    load_removal_log,
    log_removal,
    removed_ids,
    verify_removals,
)
from twin.model import Overlay
from twin.repo import ModelRepo

PERSPECTIVE, OPTION, CONSTRAINT = "the-operator", "stake-the-quarter-on-one-title", "insolvency"


@pytest.fixture()
def netflix(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "netflix")


# -- the catalogue ---------------------------------------------------------------------------


def test_the_catalogue_loads_and_every_entry_names_a_mechanism() -> None:
    doc = load_catalogue()
    assert len(doc["entries"]) >= 5
    for entry in doc["entries"]:
        assert entry["risk"].strip()
        assert entry["mechanism"].strip()


# -- the behavioural-sensing misuse catalogue (build ticket 82, decision ticket 15 Q3) --------


def test_the_behavioural_catalogue_loads_through_the_same_loader_and_names_a_mechanism_each() -> None:
    """Reuses `load_catalogue()` with a path override, per build ticket 82's own instruction —
    there is no second loader function to import."""
    doc = load_catalogue(BEHAVIOURAL_CATALOGUE_PATH)
    assert len(doc["entries"]) == 8
    for entry in doc["entries"]:
        assert entry["risk"].strip()
        assert entry["mechanism"].strip()


def test_the_behavioural_catalogue_names_decision_ticket_15s_q3_misuses() -> None:
    ids = {entry["id"] for entry in load_catalogue(BEHAVIOURAL_CATALOGUE_PATH)["entries"]}
    assert ids == {
        "suppressing-pay",
        "justifying-layoffs",
        "surveillance-creep",
        "performance-management-by-proxy",
        "blame-attribution-after-an-incident",
        "detecting-union-organising",
        "decision-laundering",
        "weaponising-another-orgs-twin",
    }


def test_the_two_catalogues_do_not_conflate_their_scopes() -> None:
    """AC 4's own condition: the behavioural catalogue is not the governance one extended — no id
    or subject overlaps, and neither catalogue's file is the other's."""
    assert BEHAVIOURAL_CATALOGUE_PATH != CATALOGUE_PATH
    governance_ids = {e["id"] for e in load_catalogue(CATALOGUE_PATH)["entries"]}
    behavioural_ids = {e["id"] for e in load_catalogue(BEHAVIOURAL_CATALOGUE_PATH)["entries"]}
    assert not (governance_ids & behavioural_ids)
    for word in ("pay", "layoff", "surveillance"):
        assert not any(word in gid for gid in governance_ids), (
            f"{word!r} found in the governance catalogue's own ids — the two catalogues have "
            "started to overlap in scope"
        )


def test_a_catalogue_entry_with_no_mechanism_is_refused(tmp_path: Path) -> None:
    import yaml

    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({
        "schema": "twin.misuse-catalogue/v1", "version": 1,
        "entries": [{"id": "x", "risk": "something bad"}],
    }))
    with pytest.raises(MisuseError, match="no mechanism"):
        load_catalogue(bad)


# -- computed attractiveness ------------------------------------------------------------------


def test_attractiveness_is_computed_from_the_real_cost(netflix: Overlay) -> None:
    result = compute_attractiveness(netflix.perspectives[PERSPECTIVE], netflix.responses, OPTION, CONSTRAINT)
    assert result["mode"] == 5.0


def test_an_unknown_option_has_nothing_to_compute(netflix: Overlay) -> None:
    with pytest.raises(MisuseError, match="no response"):
        compute_attractiveness(netflix.perspectives[PERSPECTIVE], netflix.responses, "no-such-option", CONSTRAINT)


def test_an_option_that_does_not_cross_the_constraint_has_nothing_to_compute(netflix: Overlay) -> None:
    with pytest.raises(MisuseError, match="does not cross"):
        compute_attractiveness(
            netflix.perspectives[PERSPECTIVE], netflix.responses, "expand-the-delivery-network", CONSTRAINT
        )


def test_the_universal_floor_is_not_a_perspective_to_remove_from(netflix: Overlay) -> None:
    """`no-covert-sensing` is a floor constraint; `the-operator` does not declare it itself, so it
    cannot be "removed" from this perspective — only a perspective's own declared constraint can."""
    with pytest.raises(MisuseError, match="does not declare"):
        compute_attractiveness(
            netflix.perspectives[PERSPECTIVE], netflix.responses,
            "instrument-viewers-without-telling-them", "no-covert-sensing",
        )


def test_an_option_excluded_by_something_else_too_has_nothing_to_compute(netflix: Overlay) -> None:
    """A response that crosses two constraints is still excluded after only one is removed —
    there is nothing to attribute an attractiveness figure to yet."""
    perspective = {
        **netflix.perspectives[PERSPECTIVE],
        "forbidden": {**(netflix.perspectives[PERSPECTIVE].get("forbidden") or {}), "also-forbidden": "a second red line"},
    }
    responses = {
        **netflix.responses,
        OPTION: {**netflix.responses[OPTION], "crosses": {"insolvency": "ruin", "also-forbidden": "x"}},
    }
    # insolvency alone is not enough now — the option also crosses also-forbidden, which is still
    # declared on this perspective, so compute_attractiveness must not invent a figure for it.
    with pytest.raises(MisuseError, match="still excluded"):
        compute_attractiveness(perspective, responses, OPTION, "insolvency")


# -- the append-only log ----------------------------------------------------------------------


def test_log_removal_requires_no_number_from_the_caller(netflix: Overlay, tmp_path: Path) -> None:
    """`log_removal`'s own signature has no float parameter — inspected here so the guarantee is
    checked against the code, not just exercised by a test that happens not to pass one."""
    import inspect

    sig = inspect.signature(log_removal)
    for name, param in sig.parameters.items():
        assert param.annotation not in (float, "float"), f"log_removal accepts a raw {name}: float"


def test_logging_and_reading_back_a_removal(netflix: Overlay, tmp_path: Path) -> None:
    log = tmp_path / "removal-log.jsonl"
    entry = log_removal(
        netflix.perspectives[PERSPECTIVE], netflix.responses, OPTION, CONSTRAINT,
        "constraint-owner", "the option is now within risk appetite", "2026-08-10", path=log,
    )
    assert entry["attractiveness"]["mode"] == 5.0
    loaded = load_removal_log(log)
    assert loaded == [entry]


def test_a_removal_with_no_reason_is_refused(netflix: Overlay, tmp_path: Path) -> None:
    with pytest.raises(MisuseError, match="no reason"):
        log_removal(
            netflix.perspectives[PERSPECTIVE], netflix.responses, OPTION, CONSTRAINT,
            "constraint-owner", "   ", "2026-08-10", path=tmp_path / "log.jsonl",
        )


def test_a_removal_that_computes_nothing_is_not_logged(netflix: Overlay, tmp_path: Path) -> None:
    """Logging fails the same way computing does — there is no separate path that lets a caller
    log a removal `compute_attractiveness` itself refused."""
    log = tmp_path / "log.jsonl"
    with pytest.raises(MisuseError, match="does not cross"):
        log_removal(
            netflix.perspectives[PERSPECTIVE], netflix.responses, "expand-the-delivery-network",
            CONSTRAINT, "constraint-owner", "reason", "2026-08-10", path=log,
        )
    assert load_removal_log(log) == []


def test_a_missing_log_is_empty_not_an_error(tmp_path: Path) -> None:
    assert load_removal_log(tmp_path / "nope.jsonl") == []


def test_a_malformed_log_line_is_refused_not_silently_skipped(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    log.write_text("not json\n")
    with pytest.raises(MisuseError, match="not a JSON object"):
        load_removal_log(log)


def test_a_log_line_missing_a_field_is_refused(tmp_path: Path) -> None:
    import json

    log = tmp_path / "log.jsonl"
    log.write_text(json.dumps({"perspective": "the-operator", "constraint_id": "insolvency"}) + "\n")
    with pytest.raises(MisuseError, match="declares no"):
        load_removal_log(log)


# -- verification: a removal with no log entry is rejected ------------------------------------


def test_removed_ids_finds_the_difference(netflix: Overlay) -> None:
    before = netflix.perspectives[PERSPECTIVE]
    after = {**before, "ruin": {}}
    assert removed_ids(before, after) == {"insolvency"}


def test_a_logged_removal_verifies_clean(netflix: Overlay, tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    entry = log_removal(
        netflix.perspectives[PERSPECTIVE], netflix.responses, OPTION, CONSTRAINT,
        "constraint-owner", "reason", "2026-08-10", path=log,
    )
    before = netflix.perspectives[PERSPECTIVE]
    after = {**before, "ruin": {}}
    assert verify_removals(before, after, [entry]) == []


def test_an_unlogged_removal_is_rejected(netflix: Overlay) -> None:
    before = netflix.perspectives[PERSPECTIVE]
    after = {**before, "ruin": {}}
    violations = verify_removals(before, after, [])
    assert len(violations) == 1
    assert "insolvency" in violations[0]
    assert "the-operator" in violations[0]


def test_a_removal_logged_for_a_different_perspective_does_not_count(netflix: Overlay, tmp_path: Path) -> None:
    """The log entry names a perspective too — a removal on `the-operator` is not covered by a
    removal logged against `the-staff-council`, even for the same constraint id."""
    log = tmp_path / "log.jsonl"
    entry = log_removal(
        netflix.perspectives[PERSPECTIVE], netflix.responses, OPTION, CONSTRAINT,
        "constraint-owner", "reason", "2026-08-10", path=log,
    )
    entry = {**entry, "perspective": "the-staff-council"}
    before = netflix.perspectives[PERSPECTIVE]
    after = {**before, "ruin": {}}
    violations = verify_removals(before, after, [entry])
    assert len(violations) == 1


def test_no_removal_at_all_verifies_clean(netflix: Overlay) -> None:
    before = netflix.perspectives[PERSPECTIVE]
    assert verify_removals(before, before, []) == []
