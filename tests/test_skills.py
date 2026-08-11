"""The skill-eval harness — seam 3 (build ticket 42)."""

from __future__ import annotations

import pytest

from twin.skills import (
    SkillError,
    TOY_SKILL_CORPUS,
    detect_regression,
    evaluate,
    load_scores,
    record_score,
    threshold_for,
    toy_classifier,
)


def test_the_toy_skill_passes_its_own_corpus() -> None:
    result = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    assert result.score == 1.0
    assert result.passed
    assert result.threshold == threshold_for("toy-classifier")


def test_a_degraded_skill_fails_the_threshold() -> None:
    """A skill that gets everything wrong scores 0.0 and fails, regardless of the threshold."""
    result = evaluate("toy-classifier", lambda x: "WRONG", TOY_SKILL_CORPUS)
    assert result.score == 0.0
    assert not result.passed


def test_score_is_a_proportion_not_a_raw_count() -> None:
    def half_right(text: str) -> str:
        return text.upper() if text in ("hello", "WORLD", "MiXeD") else "nope"

    result = evaluate("toy-classifier", half_right, TOY_SKILL_CORPUS)
    assert result.score == pytest.approx(3 / 5)


def test_the_harness_is_skill_agnostic() -> None:
    """`evaluate` and its supporting functions take a bare callable, a corpus and a skill name;
    none of their bodies hardcodes a single one of the six real skills — the module docstring
    names them only as context (none exist yet), which is documentation, not a code path."""
    import inspect

    from twin import skills

    real_skills = (
        "signal-classify", "causal-claims", "evolution-judge", "substrate-generator",
        "gameplay-lens", "ethics-gate",
    )
    for fn in (
        skills.evaluate, skills.threshold_for, skills.load_thresholds, skills.record_score,
        skills.load_scores, skills.history_for, skills.detect_regression,
    ):
        body = inspect.getsource(fn)
        for real_skill in real_skills:
            assert real_skill not in body, f"{fn.__name__} names {real_skill!r} — it is not skill-agnostic"


def test_an_empty_corpus_is_refused() -> None:
    with pytest.raises(SkillError, match="empty corpus"):
        evaluate("toy-classifier", toy_classifier, [])


def test_an_unknown_skill_has_no_threshold() -> None:
    with pytest.raises(SkillError, match="no threshold declared.*toy-classifier"):
        threshold_for("no-such-skill")


def test_a_corpus_item_missing_a_field_is_refused() -> None:
    with pytest.raises(SkillError, match="declares no"):
        evaluate("toy-classifier", toy_classifier, [{"id": "x", "input": "y"}])


# -- score over time and regression detection -----------------------------------------------


def test_recording_and_reading_back_a_score(tmp_path) -> None:
    log = tmp_path / "scores.jsonl"
    result = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    entry = record_score(result, "model-a", "2026-01-01T00:00:00Z", path=log)
    assert entry["skill"] == "toy-classifier"
    loaded = load_scores(log)
    assert loaded == [entry]


def test_a_missing_score_log_is_empty_not_an_error(tmp_path) -> None:
    assert load_scores(tmp_path / "nope.jsonl") == []


def test_regression_needs_at_least_two_model_versions(tmp_path) -> None:
    log = tmp_path / "scores.jsonl"
    result = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    record_score(result, "model-a", "2026-01-01T00:00:00Z", path=log)
    report = detect_regression("toy-classifier", path=log)
    assert report["computed"] is False


def test_a_model_upgrade_that_degrades_judgement_is_surfaced_as_a_regression(tmp_path) -> None:
    log = tmp_path / "scores.jsonl"
    good = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    bad = evaluate("toy-classifier", lambda x: "WRONG", TOY_SKILL_CORPUS)
    record_score(good, "model-a", "2026-01-01T00:00:00Z", path=log)
    record_score(bad, "model-b", "2026-02-01T00:00:00Z", path=log)
    report = detect_regression("toy-classifier", path=log)
    assert report["computed"] is True
    assert report["regressed"] is True
    assert report["previous"]["model_version"] == "model-a"
    assert report["latest"]["model_version"] == "model-b"
    assert report["delta"] < 0


def test_an_improved_model_is_not_flagged_as_a_regression(tmp_path) -> None:
    log = tmp_path / "scores.jsonl"
    bad = evaluate("toy-classifier", lambda x: "WRONG", TOY_SKILL_CORPUS)
    good = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    record_score(bad, "model-a", "2026-01-01T00:00:00Z", path=log)
    record_score(good, "model-b", "2026-02-01T00:00:00Z", path=log)
    report = detect_regression("toy-classifier", path=log)
    assert report["regressed"] is False


def test_a_reevaluated_version_moves_to_latest_even_if_first_seen_earlier(tmp_path) -> None:
    """model-a, then model-b, then model-a again (a rollback re-check) — "latest" must be
    model-a's second entry, not model-b, which was only ever seen once and is now stale."""
    log = tmp_path / "scores.jsonl"
    good = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    bad = evaluate("toy-classifier", lambda x: "WRONG", TOY_SKILL_CORPUS)
    record_score(good, "model-a", "2026-01-01T00:00:00Z", path=log)
    record_score(bad, "model-b", "2026-01-02T00:00:00Z", path=log)
    record_score(bad, "model-a", "2026-01-03T00:00:00Z", path=log)
    report = detect_regression("toy-classifier", path=log)
    assert report["computed"] is True
    assert report["latest"]["model_version"] == "model-a"
    assert report["latest"]["score"] == pytest.approx(bad.score)
    assert report["previous"]["model_version"] == "model-b"


def test_two_runs_of_the_same_model_version_are_not_a_regression_comparison(tmp_path) -> None:
    """Re-running the same model version twice, once worse, is noise — not an upgrade — so it
    must not appear as a two-version comparison at all."""
    log = tmp_path / "scores.jsonl"
    good = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    bad = evaluate("toy-classifier", lambda x: "WRONG", TOY_SKILL_CORPUS)
    record_score(good, "model-a", "2026-01-01T00:00:00Z", path=log)
    record_score(bad, "model-a", "2026-01-02T00:00:00Z", path=log)
    report = detect_regression("toy-classifier", path=log)
    assert report["computed"] is False


def test_a_malformed_log_line_is_refused_not_silently_skipped(tmp_path) -> None:
    log = tmp_path / "scores.jsonl"
    log.write_text("not json\n")
    from twin.skills import SkillError as Err

    with pytest.raises(Err, match="not a JSON object"):
        load_scores(log)
