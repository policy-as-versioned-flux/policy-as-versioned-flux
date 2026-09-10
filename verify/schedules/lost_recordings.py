"""Ticket 104: retained cancelled recording opportunities, never invented observations.

GitHub's retained workflow history is the census boundary; deleted runs cannot be counted.
Cancellation does not establish its cause. Report losses without blaming concurrency for
manual cancellations, and exclude a cancelled run if its number actually reached truth.log.
"""
from __future__ import annotations

import json


def collect(remote: str, gh) -> dict:
    branch = json.loads(gh("api", f"repos/{remote}"))["default_branch"]
    pages = json.loads(gh("api", "--paginate", "--slurp",
                         f"repos/{remote}/actions/workflows/truth.yml/runs?per_page=100"))
    runs: list[dict] = []
    for page in pages:
        rows = page.get("workflow_runs")
        if not isinstance(rows, list):
            raise ValueError("workflow run history is not a list")
        runs.extend({key: row.get(key) for key in
                     ("run_number", "head_branch", "event", "conclusion")} for row in rows)
    facts = {"default_branch": branch, "runs": runs}
    grade(facts, set())  # malformed API data is missing evidence, never a zero
    return facts


def grade(facts: dict, recorded: set[int]) -> str:
    branch, rows = facts.get("default_branch"), facts.get("runs")
    if not isinstance(branch, str) or not branch or not isinstance(rows, list):
        raise ValueError("default branch or retained run history missing")
    cancelled = set()
    for row in rows:
        if (not isinstance(row, dict) or type(row.get("run_number")) is not int
                or not isinstance(row.get("head_branch"), str)
                or not isinstance(row.get("event"), str)
                or row.get("conclusion") not in
                (None, "success", "failure", "cancelled", "skipped", "neutral",
                 "timed_out", "action_required", "stale", "startup_failure")):
            raise ValueError("malformed retained workflow run")
        if (row["head_branch"] == branch
                and row["event"] in ("push", "schedule", "workflow_dispatch")
                and row["conclusion"] == "cancelled"
                and row["run_number"] not in recorded):
            cancelled.add(row["run_number"])
    numbers = ",".join(map(str, sorted(cancelled))) or "none"
    return (f"LOST RECORDING count={len(cancelled)} runs={numbers}; "
            f"{len(rows)} runs in retained GitHub history; cancelled {branch} recording "
            "opportunities without a TRUTH line, cause unknown; historical losses reported, "
            "not replayed")
