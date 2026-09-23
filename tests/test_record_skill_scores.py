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
    assert not any(e["outcome"] == "fail" for e in entries), f"a real skill failed its own real corpus: {entries}"
    assert all(e["score"] >= e["threshold"] for e in entries), f"a real skill fell below its threshold: {entries}"
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


def test_a_corpus_below_its_stated_minimum_is_recorded_as_not_measurable(tmp_path: Path) -> None:
    """Eco-system ticket 112. The outcome follows the corpus size against the minimum the
    threshold states, read off each entry rather than typed: a skill whose corpus grows past its
    minimum moves from not-measurable to pass without this test changing."""
    entries = rss.run("2026-09-22T00:00:00Z", "heuristic-test", path=tmp_path / "s.jsonl")
    for e in entries:
        # The row states the count its minimum is measured against, so the permission (condition
        # 1 in twin/model_permission.py) can read measurability off the row it grades.
        # Ticket 118: an item right on no checkable basis is unscoreable and is not measured.
        assert e["measured_count"] == e["total"] - e["unscoreable"], e
        expected = "pass" if e["measured_count"] >= e["min_items"] else "not-measurable"
        assert e["outcome"] == expected, e
        assert e["passed"] is (expected == "pass"), e



def test_every_row_records_the_attributable_rate_beside_the_score(tmp_path: Path) -> None:
    """Eco-system ticket 118. Each row carries the rate and the counts it is derived from, and
    the rate is recomputable from them. A metric that measured nothing records null, never 0."""
    entries = rss.run("2026-09-22T00:00:00Z", "heuristic-test", path=tmp_path / "s.jsonl")
    for e in entries:
        assert {"attributable_rate", "wrong_basis", "unscoreable", "measured_count"} <= e.keys(), e
        right = round(e["score"] * e["total"]) - e["unscoreable"]
        if e["measured_count"] == 0:
            assert e["attributable_rate"] is None, e
        else:
            assert e["attributable_rate"] == right / e["measured_count"], e
