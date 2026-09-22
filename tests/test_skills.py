"""The skill-eval harness — seam 3 (build ticket 42)."""

from __future__ import annotations

from pathlib import Path

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
    assert result.score == pytest.approx(3 / len(TOY_SKILL_CORPUS))


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


# -- a threshold states the corpus it needs (eco-system ticket 112) ------------------------


def _threshold_file(tmp_path, threshold: float, min_items: int | None, name: str = "toy-classifier"):
    import yaml

    entry: dict = {"threshold": threshold}
    if min_items is not None:
        entry["min_items"] = min_items
    path = tmp_path / "thresholds.yaml"
    path.write_text(yaml.safe_dump({"schema": "twin.skill-thresholds/v1", "thresholds": {name: entry}}))
    return path


def _corpus(n: int) -> list[dict]:
    return [{"id": f"i{k}", "input": f"w{k}", "expected": f"W{k}"} for k in range(n)]


def test_every_threshold_states_the_minimum_its_own_derivation_gives() -> None:
    from twin.corpus_size import derived_min_items
    from twin.skills import load_thresholds

    for name, entry in load_thresholds()["thresholds"].items():
        assert entry["min_items"] == derived_min_items(entry["threshold"]), name


def test_a_threshold_that_states_no_minimum_is_refused(tmp_path) -> None:
    path = _threshold_file(tmp_path, 0.8, None)
    with pytest.raises(SkillError, match="states no min_items"):
        threshold_for("toy-classifier", path)


@pytest.mark.parametrize("stated", [1, 15, 17, 50])
def test_a_stated_minimum_the_method_does_not_derive_is_refused(tmp_path, stated: int) -> None:
    """Below the derivation is a threshold claiming more than its corpus can carry; above it is an
    imported number, the prior art's ~50 included."""
    path = _threshold_file(tmp_path, 0.8, stated)
    with pytest.raises(SkillError, match="derives 16"):
        threshold_for("toy-classifier", path)


def test_a_run_below_the_minimum_is_not_measurable_rather_than_passed(tmp_path) -> None:
    from twin.skills import NOT_MEASURABLE

    path = _threshold_file(tmp_path, 0.8, 16)
    result = evaluate("toy-classifier", toy_classifier, _corpus(3), threshold_path=path)
    assert result.score == 1.0
    assert result.clears_threshold
    assert result.outcome == NOT_MEASURABLE
    assert not result.passed
    assert not result.failed, "not measurable is a third outcome, not a failure"
    assert result.min_items == 16


def test_a_wrong_run_below_the_minimum_is_also_not_measurable(tmp_path) -> None:
    """Three wrong answers bound nothing either: the rule of three is symmetric."""
    from twin.skills import NOT_MEASURABLE

    path = _threshold_file(tmp_path, 0.8, 16)
    result = evaluate("toy-classifier", lambda x: "WRONG", _corpus(3), threshold_path=path)
    assert result.outcome == NOT_MEASURABLE
    assert not result.passed and not result.failed


def test_at_the_minimum_the_run_passes_or_fails_on_its_score(tmp_path) -> None:
    from twin.skills import FAIL, PASS

    path = _threshold_file(tmp_path, 0.8, 16)
    good = evaluate("toy-classifier", toy_classifier, _corpus(16), threshold_path=path)
    bad = evaluate("toy-classifier", lambda x: "WRONG", _corpus(16), threshold_path=path)
    assert (good.outcome, good.passed, good.failed) == (PASS, True, False)
    assert (bad.outcome, bad.passed, bad.failed) == (FAIL, False, True)


def test_the_toy_corpus_is_large_enough_for_its_own_threshold() -> None:
    """The fixture skill is how the harness proves itself. A fixture that is itself not
    measurable would prove only the third outcome."""
    result = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    assert len(TOY_SKILL_CORPUS) >= result.min_items
    assert result.passed


def test_the_recorded_entry_carries_the_outcome_and_the_minimum(tmp_path) -> None:
    from twin.skills import NOT_MEASURABLE

    path = _threshold_file(tmp_path, 0.8, 16)
    result = evaluate("toy-classifier", toy_classifier, _corpus(3), threshold_path=path)
    entry = record_score(result, "model-a", "2026-01-01T00:00:00Z", path=tmp_path / "s.jsonl")
    assert entry["outcome"] == NOT_MEASURABLE
    assert entry["min_items"] == 16
    assert entry["passed"] is False


def test_measurability_counts_the_items_the_seam_names() -> None:
    """The seam ticket 118 builds on: the run-level outcome reads the corpus size through
    `measured_count`, and the item-level state only through `score`. A third item state changes
    the numerator; it does not move this count unless 118 decides it should."""
    result = evaluate("toy-classifier", toy_classifier, TOY_SKILL_CORPUS)
    assert result.measured_count == len(result.items)


def _doc(**entries: dict) -> dict:
    return {"schema": "twin.skill-thresholds/v1", "thresholds": entries}


def test_a_lowered_minimum_needs_a_citation_like_a_lowered_threshold() -> None:
    from twin.invariants.harness import _lowered_without_citation

    before = _doc(s={"threshold": 0.8, "min_items": 16})
    assert _lowered_without_citation(before, _doc(s={"threshold": 0.8, "min_items": 9})) == ["s min_items 16 -> 9"]
    assert _lowered_without_citation(before, _doc(s={"threshold": 0.65, "min_items": 16})) == ["s threshold 0.8 -> 0.65"]
    cited = {"threshold": 0.65, "min_items": 9, "authorised_by": "decision ticket 20 - a reason"}
    assert _lowered_without_citation(before, _doc(s=cited)) == []


def test_a_minimum_appearing_for_the_first_time_is_not_a_lowering() -> None:
    from twin.invariants.harness import _lowered_without_citation

    assert _lowered_without_citation(_doc(s={"threshold": 0.8}), _doc(s={"threshold": 0.8, "min_items": 16})) == []
    assert _lowered_without_citation(_doc(s={"threshold": 0.8, "min_items": 16}),
                                     _doc(s={"threshold": 0.8, "min_items": 20})) == []


# -- the citation guard's baseline, at its seam (review of ticket 112) ------------------------

_THRESHOLDS_REL = "twin/skill-thresholds.yaml"


def _threshold_repo(tmp_path: Path, *versions: dict) -> Path:
    """A throwaway git repository holding one commit per thresholds document. It runs no hook, so
    the fixture never calls the network."""
    import subprocess

    import yaml

    repo = tmp_path / "repo"
    (repo / "twin").mkdir(parents=True)
    hooks = tmp_path / "no-hooks"
    hooks.mkdir()

    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-c", f"core.hooksPath={hooks}", "-c", "commit.gpgsign=false",
             "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", *args],
            cwd=repo, check=True, capture_output=True,
        )

    git("init", "-q")
    for number, doc in enumerate(versions):
        (repo / _THRESHOLDS_REL).write_text(yaml.safe_dump(doc), encoding="utf-8")
        git("add", _THRESHOLDS_REL)
        git("commit", "-q", "-m", f"version {number}")
    return repo


def test_a_committed_lowering_is_seen_when_the_tree_equals_head(tmp_path) -> None:
    """The CI case. The checkout IS HEAD, so a baseline of HEAD can only equal itself and a
    lowering committed in the same diff was never seen. The previous committed version is the
    baseline instead, and the lowering is caught."""
    from twin.invariants.harness import _lowered_without_citation, _thresholds_at, _thresholds_baseline

    before = _doc(s={"threshold": 0.65, "min_items": 9})
    after = _doc(s={"threshold": 0.6, "min_items": 8})
    repo = _threshold_repo(tmp_path, before, after)

    # The old HEAD-only comparison is blind: this is the defect, reproduced.
    head = _thresholds_at(repo, "HEAD", _THRESHOLDS_REL)
    assert head == after
    assert _lowered_without_citation(head, after) == []

    baseline = _thresholds_baseline(repo, after, _THRESHOLDS_REL)
    assert baseline is not None
    earlier, source = baseline
    assert earlier == before
    assert source.startswith("the previous version")
    assert _lowered_without_citation(earlier, after) == ["s min_items 9 -> 8", "s threshold 0.65 -> 0.6"]


def test_an_uncommitted_lowering_is_measured_against_head(tmp_path) -> None:
    from twin.invariants.harness import _thresholds_baseline

    before = _doc(s={"threshold": 0.65, "min_items": 9})
    repo = _threshold_repo(tmp_path, before)
    edited = _doc(s={"threshold": 0.6, "min_items": 8})
    baseline = _thresholds_baseline(repo, edited, _THRESHOLDS_REL)
    assert baseline is not None and baseline[0] == before
    assert "uncommitted" in baseline[1]


def test_one_committed_version_has_no_baseline(tmp_path) -> None:
    from twin.invariants.harness import _thresholds_baseline

    only = _doc(s={"threshold": 0.6, "min_items": 8})
    assert _thresholds_baseline(_threshold_repo(tmp_path, only), only, _THRESHOLDS_REL) is None


def test_the_guard_skips_rather_than_passes_when_it_has_no_history(monkeypatch) -> None:
    """A check that stops looking must not read green. `hash_changes_are_authorised` raises Skip
    on one committed version; this guard does the same, so a depth-1 checkout whose only commit
    lowers a threshold reads SKIP, never PASS."""
    from twin.invariants import Skip
    from twin.invariants import harness

    monkeypatch.setattr(harness, "_thresholds_baseline", lambda *a, **k: None)
    with pytest.raises(Skip):
        harness._skill_eval_harness_is_agnostic_and_thresholds_are_guarded(None)  # type: ignore[arg-type]
