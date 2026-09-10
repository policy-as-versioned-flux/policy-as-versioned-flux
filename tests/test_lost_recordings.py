"""Ticket 104: cancelled recording opportunities remain visible in collected facts."""
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "lost_recordings", Path(__file__).parents[1] / "verify/schedules/lost_recordings.py")
assert spec is not None and spec.loader is not None
lost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lost)


def test_cancelled_main_runs_are_lost_except_when_their_number_was_recorded():
    rows = [
        {"run_number": 1, "head_branch": "main", "event": "push", "conclusion": "cancelled"},
        {"run_number": 2, "head_branch": "feature", "event": "push", "conclusion": "cancelled"},
        {"run_number": 3, "head_branch": "main", "event": "schedule", "conclusion": "success"},
        {"run_number": 4, "head_branch": "main", "event": "workflow_dispatch", "conclusion": "cancelled"},
    ]
    report = lost.grade({"default_branch": "main", "runs": rows}, {4})
    assert "LOST RECORDING count=1" in report
    assert "runs=1" in report
    assert "retained GitHub history" in report


def test_duplicate_api_rows_do_not_inflate_the_count():
    row = {"run_number": 9, "head_branch": "main", "event": "push", "conclusion": "cancelled"}
    assert "count=1" in lost.grade({"default_branch": "main", "runs": [row, row]}, set())


@pytest.mark.parametrize("facts", [{}, {"default_branch": "main", "runs": None},
                                     {"default_branch": "main", "runs": [{}]}])
def test_missing_or_malformed_history_cannot_report_zero(facts):
    with pytest.raises(ValueError):
        lost.grade(facts, set())


def test_real_workflow_keeps_main_and_builder_pending_slots_separate():
    import yaml
    doc = yaml.safe_load((Path(__file__).parents[1] / ".github/workflows/truth.yml").read_text())
    group = doc["concurrency"]["group"]
    def key(ref):
        return group.replace("${{ github.event_name }}", "push").replace("${{ github.ref }}", ref).lower()
    assert key("refs/heads/main") != key("refs/heads/builder")
    assert doc["concurrency"]["cancel-in-progress"] is False


def test_collector_reads_all_pages_and_passes_only_observation_fields():
    calls = []
    def gh(*args):
        calls.append(args)
        if len(calls) == 1:
            return json.dumps({"default_branch": "trunk"})
        return json.dumps([{"workflow_runs": [
            {"run_number": 12, "head_branch": "trunk", "event": "push",
             "conclusion": "cancelled", "actor": {"login": "unneeded"}}]},
            {"workflow_runs": [{"run_number": 13, "head_branch": "trunk",
                                "event": "push", "conclusion": None}]}])
    facts = lost.collect("owner/repo", gh)
    assert "--paginate" in calls[1] and "--slurp" in calls[1]
    assert facts["default_branch"] == "trunk"
    assert len(facts["runs"]) == 2
    assert "actor" not in facts["runs"][0]
    assert "count=1" in lost.grade(facts, set())
