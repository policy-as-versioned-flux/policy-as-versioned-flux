"""The suite that guards the suite.

A guardrail nobody tests is a guardrail nobody has. These plant the weakenings the manifest
exists to catch, and assert on the `Result` the runner emits rather than on the check functions
themselves — the harness is as disposable as everything else here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import invariants
from twin.invariants import FAIL, PASS, SKIP, Result, body_hash, registry
from twin.invariants.harness import (
    LIVE,
    PENDING,
    Entry,
    build_ticket_status,
    constitution_invariants,
    load_manifest,
    may_skip,
    ticket_is_closed,
)


@pytest.fixture(scope="module")
def suite_results(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, Result], bool]:
    results, ok = invariants.run(tmp=tmp_path_factory.mktemp("verify"))
    return {r.name: r for r in results}, ok


def _one(name: str, tmp_path: Path) -> Result:
    results, _ = invariants.run(only=[name], tmp=tmp_path)
    assert len(results) == 1
    return results[0]


def test_the_suite_is_green(suite_results: tuple[dict[str, Result], bool]) -> None:
    by_name, ok = suite_results
    failed = [r for r in by_name.values() if r.status == FAIL]
    assert not failed, [f"{r.name}: {r.detail}" for r in failed]
    assert ok


def test_every_live_invariant_actually_asserts_something(
    suite_results: tuple[dict[str, Result], bool]
) -> None:
    """A live invariant that skips is a silent weakening; only `pending` may decline to assert."""
    by_name, _ = suite_results
    for entry in load_manifest():
        if entry.state == LIVE:
            assert by_name[entry.name].status == PASS, f"{entry.name}: {by_name[entry.name].detail}"


def test_pending_invariants_say_which_ticket_activates_them(
    suite_results: tuple[dict[str, Result], bool]
) -> None:
    by_name, _ = suite_results
    for entry in load_manifest():
        if entry.state == PENDING:
            assert by_name[entry.name].status == SKIP
            assert f"build ticket {entry.activating_ticket}" in by_name[entry.name].detail


def test_the_manifest_matches_the_constitution() -> None:
    assert {e.name for e in load_manifest()} == set(constitution_invariants())
    assert len(constitution_invariants()) == 16


def test_every_activating_ticket_exists() -> None:
    for entry in load_manifest():
        assert build_ticket_status(entry.activating_ticket) is not None, entry.activating_ticket


def test_a_closed_ticket_is_recognised_in_the_format_this_repository_writes() -> None:
    """Statuses carry a date. Exact-matching the whole line made this guard inert."""
    assert ticket_is_closed("done (2026-08-05)")
    assert ticket_is_closed("done")
    assert not ticket_is_closed("ready-for-agent")
    assert not ticket_is_closed(None)
    assert ticket_is_closed(build_ticket_status("01")), "ticket 01 is closed and must read as closed"


def test_a_weakened_test_body_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tampered = [e for e in load_manifest() if e.name != "store_rebuildable_from_git"]
    tampered.append(
        Entry(name="store_rebuildable_from_git", activating_ticket="01", state=LIVE, asserts="",
              body_sha256="0" * 64)
    )
    monkeypatch.setattr("twin.invariants.harness.load_manifest", lambda path=None: tampered)

    result = _one("invariant_bodies_match_manifest_hashes", tmp_path)
    assert result.status == FAIL and "re-blessed" in result.detail


def test_a_hash_that_moved_with_no_citation_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The weakening this guard exists for: gut a check, re-pin its hash, commit both together."""
    baseline = [
        Entry(name=e.name, activating_ticket=e.activating_ticket, state=e.state, asserts="",
              body_sha256="f" * 64 if e.name == "store_rebuildable_from_git" else e.body_sha256,
              refuses_keys=e.refuses_keys)
        for e in load_manifest()
    ]
    monkeypatch.setattr(
        "twin.invariants.harness._manifest_at",
        lambda root, ref: (baseline, {"checks_module_sha256": "unchanged"}),
    )
    monkeypatch.setattr(
        "twin.invariants.harness.manifest_doc", lambda path=None: {"checks_module_sha256": "unchanged"}
    )
    result = _one("hash_changes_are_authorised", tmp_path)
    assert result.status == FAIL and "store_rebuildable_from_git" in result.detail


def test_a_deleted_refusal_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The manifest declares what each invariant refuses, so deleting one from the code fails."""
    from twin import artefact

    thinned = {k: v for k, v in artefact.FORBIDDEN_KEYS.items() if k != "combined_forecast"}
    monkeypatch.setattr(artefact, "FORBIDDEN_KEYS", thinned)

    result = _one("no_collapse_mechanism", tmp_path)
    assert result.status == FAIL and "combined_forecast" in result.detail


def test_an_invariant_pending_past_a_closed_ticket_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("twin.invariants.harness.build_ticket_status", lambda number: "done (2026-08-05)")
    result = _one("no_invariant_pending_past_its_ticket", tmp_path)
    assert result.status == FAIL and "pending past a closed ticket" in result.detail


def test_an_implemented_but_unlisted_check_is_caught(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unlisted check is an unguarded one: nothing would notice if it stopped running."""
    monkeypatch.setattr(
        "twin.invariants.harness.registry",
        lambda: {**registry(), "a_check_nobody_declared": lambda ctx: "ok"},
    )
    result = _one("live_invariants_have_checks", tmp_path)
    assert result.status == FAIL and "not marked live in the manifest" in result.detail


def test_a_missing_yardstick_fails_rather_than_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Losing `.scratch/` must not turn three guards green by making them silently absent."""
    monkeypatch.setattr("twin.invariants.harness.CONSTITUTION", tmp_path / "gone.md")
    monkeypatch.setattr("twin.invariants.harness.BUILD_TICKETS_DIR", tmp_path / "gone")

    assert _one("manifest_names_every_invariant", tmp_path).status == FAIL
    assert _one("no_invariant_pending_past_its_ticket", tmp_path).status == FAIL


def test_a_check_that_errors_is_a_failure_not_a_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(_ctx: object) -> str:
        raise ZeroDivisionError("the check itself is broken")

    monkeypatch.setattr(
        "twin.invariants.harness.registry",
        lambda: {**registry(), "store_rebuildable_from_git": explode},
    )
    result = _one("store_rebuildable_from_git", tmp_path)
    assert result.status == FAIL and "ZeroDivisionError" in result.detail


def test_only_declared_guards_may_decline_to_assert() -> None:
    live = {e.name for e in load_manifest() if e.state == LIVE}
    assert may_skip("cross_architecture_determinism", False, live), "needs a CI matrix"
    assert may_skip("hash_changes_are_authorised", False, live), "needs two committed versions"
    assert not may_skip("manifest_names_every_invariant", False, live)
    assert not may_skip("invariant_bodies_match_manifest_hashes", False, live)
    assert not may_skip("no_collapse_mechanism", True, live)
    assert may_skip("only_as_consumed_scores", True, live), "pending, and says so in the manifest"


def test_running_a_single_check_by_name_is_supported(tmp_path: Path) -> None:
    assert _one("no_collapse_mechanism", tmp_path).status == PASS


def test_body_hash_is_stable_and_distinguishes_bodies() -> None:
    checks = registry()
    one, two = checks["store_rebuildable_from_git"], checks["no_collapse_mechanism"]
    assert body_hash(one) == body_hash(one)
    assert body_hash(one) != body_hash(two)
