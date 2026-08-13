"""One thing that fails if `record_skill_scores.run()` stops actually evaluating the six real
skills against their own real corpora (build ticket 56's coherence audit: the score-over-time log
existed as a mechanism and had never been run for real)."""

from __future__ import annotations

from pathlib import Path

from twin import record_skill_scores as rss
from twin.skills import load_scores

_EXPECTED_SKILLS = {
    "signal-classify",
    "evolution-judge",
    "causal-claims",
    "causal-claims-grade-accuracy",
    "gameplay-lens",
    "substrate-generator",
    "ethics-gate",
}


def test_run_records_a_real_passing_entry_for_every_real_skill_and_metric(tmp_path: Path) -> None:
    log = tmp_path / "skill-scores.jsonl"
    entries = rss.run("2026-08-13T00:00:00Z", "heuristic-test", path=log)

    assert {e["skill"] for e in entries} == _EXPECTED_SKILLS
    assert all(e["passed"] for e in entries), f"a real skill failed its own real corpus: {entries}"
    assert all(e["model_version"] == "heuristic-test" for e in entries)
    assert all(e["recorded_at"] == "2026-08-13T00:00:00Z" for e in entries)

    logged = load_scores(log)
    assert len(logged) == len(entries)


def test_run_is_append_only_across_two_calls(tmp_path: Path) -> None:
    log = tmp_path / "skill-scores.jsonl"
    rss.run("2026-08-13T00:00:00Z", "heuristic-test-a", path=log)
    rss.run("2026-08-14T00:00:00Z", "heuristic-test-b", path=log)

    logged = load_scores(log)
    assert len(logged) == 2 * len(_EXPECTED_SKILLS)
    versions = {e["model_version"] for e in logged}
    assert versions == {"heuristic-test-a", "heuristic-test-b"}
