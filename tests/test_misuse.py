"""The misuse catalogue and constraint-removal logging (build ticket 62)."""

from __future__ import annotations

from pathlib import Path

import pytest

from twin.misuse import (
    BEHAVIOURAL_CATALOGUE_PATH,
    CATALOGUE_PATH,
    COULD_NOT_LOOK,
    ECOSYSTEM_CATALOGUE_PATH,
    ECOSYSTEM_ROW_IDS,
    FAIL,
    PASS,
    MisuseError,
    compute_attractiveness,
    ecosystem_ticket_status,
    grade_entry,
    load_all_catalogues,
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


# -- the eco-system misuse catalogue (ticket 44, from ticket 19's resolution) -----------------


def test_the_ecosystem_catalogue_loads_through_the_same_loader_and_names_a_mechanism_each() -> None:
    """Third file, same `load_catalogue()` — ticket 19's default: no third loader."""
    doc = load_catalogue(ECOSYSTEM_CATALOGUE_PATH)
    assert len(doc["entries"]) == 4
    for entry in doc["entries"]:
        assert entry["risk"].strip()
        assert entry["mechanism"].strip()


def test_the_ecosystem_catalogue_names_ticket_19s_four_rows() -> None:
    ids = {entry["id"] for entry in load_catalogue(ECOSYSTEM_CATALOGUE_PATH)["entries"]}
    assert ids == set(ECOSYSTEM_ROW_IDS) == {
        "publisher-games-own-feed-price",
        "regulator-data-mispriced-downstream",
        "adopter-buys-intel-on-rival",
        "twin-valuation-used-in-negotiation",
    }


def test_the_three_catalogues_do_not_conflate_their_scopes() -> None:
    """Three files, three scopes: no path is another's, no id appears twice across them, and the
    eco-system rows each name a marketplace party the twin-scoped catalogues never mention."""
    paths = {CATALOGUE_PATH, BEHAVIOURAL_CATALOGUE_PATH, ECOSYSTEM_CATALOGUE_PATH}
    assert len(paths) == 3
    loaded = load_all_catalogues()
    assert [path for path, _ in loaded] == [CATALOGUE_PATH, BEHAVIOURAL_CATALOGUE_PATH, ECOSYSTEM_CATALOGUE_PATH]
    seen: set[str] = set()
    for _, doc in loaded:
        ids = {e["id"] for e in doc["entries"]}
        assert not (ids & seen)
        seen |= ids
    twin_scoped = {e["id"] for _, doc in loaded[:2] for e in doc["entries"]}
    for word in ("publisher", "regulator", "rival", "negotiation"):
        assert not any(word in tid for tid in twin_scoped), (
            f"{word!r} found in a twin-scoped catalogue's own ids — the eco-system scope has leaked"
        )
    for entry in loaded[2][1]["entries"]:
        assert any(w in entry["id"] for w in ("publisher", "regulator", "adopter", "twin-valuation"))


def test_load_all_catalogues_refuses_an_id_declared_in_two_catalogues(tmp_path: Path) -> None:
    import yaml

    dup = tmp_path / "dup.yaml"
    dup.write_text(yaml.safe_dump({
        "schema": "twin.misuse-catalogue/v1", "version": 1,
        "entries": [{"id": "suppressing-pay", "risk": "r", "mechanism": "m"}],
    }))
    with pytest.raises(MisuseError, match="declared in two catalogues"):
        load_all_catalogues([BEHAVIOURAL_CATALOGUE_PATH, dup])


def test_every_ecosystem_row_names_a_path_or_a_waiting_ticket() -> None:
    """Ticket 19's default: every entry names an estate mechanism by path or a cage price. A row
    whose price is not built yet says which ticket builds it, by number, rather than naming a
    path that does not exist."""
    for entry in load_catalogue(ECOSYSTEM_CATALOGUE_PATH)["entries"]:
        assert entry.get("anchors") or entry.get("waits_on"), entry["id"]
        for anchor in entry.get("anchors") or []:
            assert isinstance(anchor, str) and anchor.strip()
        for wait in entry.get("waits_on") or []:
            assert str(wait["ticket"]).strip() and str(wait["for"]).strip()


def test_the_harness_check_loads_all_three_catalogues_and_proves_the_refusal(tmp_path: Path) -> None:
    """The check `twin verify` reports and `verify/misuse/verify-misuse.sh` grades: three files,
    one loader, four ticket-19 ids, and a planted row with no mechanism refused."""
    from twin.invariants import harness_registry
    from twin.invariants.harness import context

    check = harness_registry()["misuse_catalogues_load_and_every_row_names_a_mechanism"]
    claim = check(context(tmp_path))
    assert "3 catalogues" in claim and "4 eco-system rows" in claim and "refused" in claim


# -- grading one row against a checkout ------------------------------------------------------


def _open(number: str) -> str | None:
    return "open"


def _resolved(number: str) -> str | None:
    return "resolved"


def _unknown(number: str) -> str | None:
    return None


def _row(**fields: object) -> dict[str, object]:
    return {"id": "x", "risk": "r", "mechanism": "m", **fields}


def test_a_row_whose_anchors_all_resolve_passes(tmp_path: Path) -> None:
    (tmp_path / "hub.py").write_text("def price(): ...\n")
    estate = tmp_path / "estate"
    (estate / "platform").mkdir(parents=True)
    (estate / "platform" / "c.py").write_text("PRICE_KINDS = ()\n")
    grade = grade_entry(
        _row(anchors=["hub.py::price", "platform/c.py::PRICE_KINDS", "platform/c.py"]),
        root=tmp_path, estate=estate, ticket_status=_open,
    )
    assert grade.outcome == PASS
    assert "3 anchor" in grade.reason


def test_a_row_anchored_to_a_missing_file_fails(tmp_path: Path) -> None:
    grade = grade_entry(_row(anchors=["nowhere.py"]), root=tmp_path, estate=tmp_path, ticket_status=_open)
    assert grade.outcome == FAIL
    assert "nowhere.py" in grade.reason


def test_a_row_anchored_to_a_token_the_file_lacks_fails(tmp_path: Path) -> None:
    (tmp_path / "hub.py").write_text("def price(): ...\n")
    grade = grade_entry(_row(anchors=["hub.py::widen_to"]), root=tmp_path, estate=tmp_path, ticket_status=_open)
    assert grade.outcome == FAIL
    assert "widen_to" in grade.reason


def test_a_row_waiting_on_an_open_ticket_is_could_not_look_by_name(tmp_path: Path) -> None:
    grade = grade_entry(
        _row(waits_on=[{"ticket": "45", "for": "the switching price"}]),
        root=tmp_path, estate=tmp_path, ticket_status=_open,
    )
    assert grade.outcome == COULD_NOT_LOOK
    assert "ticket 45" in grade.reason and "the switching price" in grade.reason


def test_a_row_still_waiting_on_a_resolved_ticket_fails(tmp_path: Path) -> None:
    """The escape hatch closes itself: once the ticket a row waits on is resolved, the row must
    name the built mechanism, or the gate says so."""
    grade = grade_entry(
        _row(waits_on=[{"ticket": "45", "for": "the switching price"}]),
        root=tmp_path, estate=tmp_path, ticket_status=_resolved,
    )
    assert grade.outcome == FAIL
    assert "resolved" in grade.reason and "45" in grade.reason


def test_a_row_waiting_on_a_ticket_that_does_not_exist_fails(tmp_path: Path) -> None:
    grade = grade_entry(
        _row(waits_on=[{"ticket": "999", "for": "nothing"}]),
        root=tmp_path, estate=tmp_path, ticket_status=_unknown,
    )
    assert grade.outcome == FAIL
    assert "999" in grade.reason


def test_a_row_with_neither_anchor_nor_waiting_ticket_fails(tmp_path: Path) -> None:
    grade = grade_entry(_row(), root=tmp_path, estate=tmp_path, ticket_status=_open)
    assert grade.outcome == FAIL


def test_anchors_are_checked_before_a_waiting_ticket_can_excuse_them(tmp_path: Path) -> None:
    """A row may name what exists today AND what it waits on; the missing path still fails."""
    grade = grade_entry(
        _row(anchors=["gone.py"], waits_on=[{"ticket": "45", "for": "x"}]),
        root=tmp_path, estate=tmp_path, ticket_status=_open,
    )
    assert grade.outcome == FAIL


def test_an_estate_anchor_with_no_estate_is_could_not_look(tmp_path: Path) -> None:
    grade = grade_entry(_row(anchors=["platform/c.py"]), root=tmp_path, estate=None, ticket_status=_open)
    assert grade.outcome == COULD_NOT_LOOK
    assert "estate" in grade.reason


def test_ecosystem_ticket_status_reads_the_status_line(tmp_path: Path) -> None:
    (tmp_path / "45-switching.md").write_text("# 45\n\nType: task\nStatus: open\n")
    (tmp_path / "19-misuse.md").write_text("# 19\n\nStatus: resolved\n")
    assert ecosystem_ticket_status("45", tmp_path) == "open"
    assert ecosystem_ticket_status("19", tmp_path) == "resolved"
    assert ecosystem_ticket_status("7", tmp_path) is None


def test_the_four_rows_grade_against_this_checkout() -> None:
    """Every anchor the real rows name resolves in this checkout (hub, or the estate clone when
    it is assembled), and the rows that wait on a ticket name one that is still open."""
    from twin import ESTATE_CLONE_DIR, REPO_DIR

    estate = ESTATE_CLONE_DIR if ESTATE_CLONE_DIR.is_dir() else None
    for entry in load_catalogue(ECOSYSTEM_CATALOGUE_PATH)["entries"]:
        grade = grade_entry(entry, root=REPO_DIR, estate=estate, ticket_status=ecosystem_ticket_status)
        assert grade.outcome != FAIL, (entry["id"], grade.reason)


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
