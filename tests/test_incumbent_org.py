"""ADR-0036: current forge flags must not contradict the archive sequence.

The public seam is grade(), used by the credential-free incumbent register check.
These are synthetic forge observations, not archive actions or historical-order proof.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "incumbent_org", ROOT / "verify/incumbent-org/incumbent_org.py")
assert SPEC is not None and SPEC.loader is not None
incumbent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(incumbent)


@pytest.fixture
def completed():
    rows = incumbent.register(ROOT / "verify/incumbent-org/register.yaml")
    facts = {
        "schema": 1, "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repositories": {
            row["name"]: {"full_name": f"{row.get('owner', incumbent.ORG)}/{row['name']}",
                          "archived": row["disposition"] in {"dropped", "lifted"}}
            for row in rows
        },
        "images": [{"image": incumbent.PROBE_IMAGE, "pullable": True, "status": 200}],
    }
    checks = {check: "PASS" for row in rows for check in row["checks"]}
    return rows, facts, checks


@pytest.fixture
def before_first(completed):
    rows, facts, checks = completed
    for row in rows:
        if row["disposition"] in {"dropped", "lifted"} and row["name"] != "apps":
            facts["repositories"][row["name"]]["archived"] = False
    return rows, facts, checks


@pytest.mark.parametrize("later", [
    "pr-gate-action", "renovate-config", "handbook-generator", "c2p-collector",
    "datastore", "cloud", "fleet", "policy", "governance-agent",
])
def test_readiness_collector_must_precede_new_archives(before_first, later) -> None:
    rows, facts, checks = before_first
    facts["repositories"][later]["archived"] = True
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 1
    assert any(message.startswith("FAIL:") and "readiness-collector" in message
               and "first" in message for message in messages)


def test_historical_apps_archive_and_transfers_do_not_preempt_readiness(before_first) -> None:
    rows, facts, checks = before_first
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 0
    assert "PASS: apps: archived and its current prerequisite passes" in messages
    assert "LIMIT: readiness-collector: row passes; archive has not been performed" in messages


@pytest.mark.parametrize("later", [None, "pr-gate-action", "handbook-generator"])
def test_readiness_can_be_archived_first_then_other_eligible_rows(before_first, later) -> None:
    rows, facts, checks = before_first
    facts["repositories"]["readiness-collector"]["archived"] = True
    if later:
        facts["repositories"][later]["archived"] = True
    assert incumbent.grade(rows, facts, checks, True)[0] == 0


@pytest.mark.parametrize("unavailable", ["missing", "error"])
def test_unobserved_readiness_state_is_unknown_not_live(before_first, unavailable) -> None:
    rows, facts, checks = before_first
    facts["repositories"]["pr-gate-action"]["archived"] = True
    if unavailable == "missing":
        del facts["repositories"]["readiness-collector"]
    else:
        facts["repositories"]["readiness-collector"]["error"] = "forge unavailable"
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 3
    assert any(message.startswith("SKIP: readiness-collector:") for message in messages)
    assert not any(message.startswith("FAIL:") for message in messages)


@pytest.mark.parametrize("live", [
    ("fleet",), ("policy",), ("governance-agent",),
    ("fleet", "policy"), ("fleet", "governance-agent"), ("policy", "governance-agent"),
])
def test_final_archives_cannot_leave_part_of_the_group_live(completed, live) -> None:
    rows, facts, checks = completed
    for name in live:
        facts["repositories"][name]["archived"] = False
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 1
    assert any(message.startswith("FAIL:") and "together" in message for message in messages)


@pytest.mark.parametrize("earlier", [
    "apps", "readiness-collector", "pr-gate-action", "renovate-config",
    "handbook-generator", "c2p-collector", "datastore", "cloud",
])
def test_final_archives_cannot_precede_an_earlier_archive(completed, earlier) -> None:
    rows, facts, checks = completed
    facts["repositories"][earlier]["archived"] = False
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 1
    assert any(message.startswith("FAIL:") and "last" in message
               and earlier in message for message in messages)


def test_completed_current_flags_pass_without_claiming_their_historical_order(completed) -> None:
    rows, facts, checks = completed
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 0
    assert all(message.startswith("PASS:") for message in messages)


@pytest.mark.parametrize("earlier_live", [(), ("c2p-collector", "datastore", "cloud")])
def test_final_group_can_remain_an_unacted_limit(completed, earlier_live) -> None:
    rows, facts, checks = completed
    for name in ("fleet", "policy", "governance-agent", *earlier_live):
        facts["repositories"][name]["archived"] = False
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 0
    for name in ("fleet", "policy", "governance-agent"):
        assert f"LIMIT: {name}: row passes; archive has not been performed" in messages


@pytest.mark.parametrize("name", ["fleet", "c2p-collector"])
@pytest.mark.parametrize("unavailable", ["missing", "error"])
def test_unobserved_archive_state_remains_unknown(completed, name, unavailable) -> None:
    rows, facts, checks = completed
    if unavailable == "missing":
        del facts["repositories"][name]
    else:
        facts["repositories"][name].update(archived=False, error="forge unavailable")
    status, messages = incumbent.grade(rows, facts, checks, True)
    assert status == 3
    assert any(message.startswith(f"SKIP: {name}:") for message in messages)
    assert not any(message.startswith("FAIL:") for message in messages)


def test_existing_cage_prerequisite_still_refuses_archived_final_group(completed) -> None:
    rows, facts, checks = completed
    status, messages = incumbent.grade(rows, facts, checks, False)
    assert status == 1
    assert "FAIL: fleet: archived without a passing prerequisite ['cage-lane']" in messages


@pytest.mark.parametrize("pullable, expected", [(False, 1), (None, 3)])
def test_anonymous_image_faults_keep_their_existing_grades(completed, pullable, expected) -> None:
    rows, facts, checks = completed
    facts["images"][0]["pullable"] = pullable
    assert incumbent.grade(rows, facts, checks, True)[0] == expected
