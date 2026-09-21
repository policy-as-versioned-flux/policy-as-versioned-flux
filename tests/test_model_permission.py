"""The model-judging permission, at seam 2 (wayfinder ticket 05).

`verify/model-permission/verify-model-permission.sh` grades the same rule on the gate, against
the estate's own score log and corpora. These tests hold the parts the gate cannot: the shape of
each condition, the derivation of the clock, and the arithmetic of the frozen-field baseline
against corpora small enough to check by hand.
"""

from __future__ import annotations

import pytest

from twin import model_permission as mp
from twin import record_skill_scores as rss


# -- the frozen-field baseline -----------------------------------------------------------------

# A three-item corpus with two fields. `colour` is read and takes one value on two of three
# items; `size` is read and is all-distinct. Small enough that the answers are countable by eye.
_CORPUS = [
    {"id": "a", "input": 1, "expected": {"colour": "red", "size": 1}},
    {"id": "b", "input": 2, "expected": {"colour": "red", "size": 2}},
    {"id": "c", "input": 3, "expected": {"colour": "blue", "size": 3}},
]


def _answer(item):
    return {"colour": item["expected"]["colour"], "size": item["expected"]["size"], "unread": "noise"}


def _scorer(actual, expected):
    return actual["colour"] == expected["colour"] and actual["size"] == expected["size"]


def _answers():
    return [_answer(item) for item in _CORPUS]


def test_the_fields_a_scorer_reads_are_measured_not_listed() -> None:
    reads = mp.fields_the_scorer_reads(_answers(), _CORPUS, _scorer)
    assert set(reads) == {("colour",), ("size",)}, reads
    # `unread` is in the answer and the scorer never looks at it, so the baseline grants it.
    assert ("unread",) not in reads


def test_the_baseline_freezes_the_field_that_flatters_the_model_most() -> None:
    baseline = mp.frozen_field_baseline(_answers(), _CORPUS, _scorer)
    # "always red" is right on two of three; "always size=1" is right on one of three.
    assert baseline.score == pytest.approx(2 / 3)
    assert baseline.frozen_field == "colour"


def test_a_numeric_field_gets_its_own_corpus_mean_as_a_candidate() -> None:
    """`causal-claims`' elasticity constant is exactly its own corpus's mean, inside a tolerance
    that covers every label (ticket 04). A candidate set of only the observed values misses it."""
    corpus = [{"id": str(i), "input": i, "expected": {"x": x}} for i, x in enumerate([0.25, 0.30, 0.45, 0.50])]
    answers = [{"x": item["expected"]["x"]} for item in corpus]

    def tolerant(actual, expected):
        return abs(actual["x"] - expected["x"]) <= 0.15

    baseline = mp.frozen_field_baseline(answers, corpus, tolerant)
    assert baseline.score == 1.0, baseline
    assert float(baseline.frozen_value) == pytest.approx(0.375)


def test_an_empty_corpus_admits_no_baseline() -> None:
    with pytest.raises(mp.PermissionError_):
        mp.frozen_field_baseline([], [], _scorer)


def test_the_variance_is_counted_per_field_the_scorer_reads() -> None:
    baseline = mp.frozen_field_baseline(_answers(), _CORPUS, _scorer)
    assert mp.answer_variance(_answers(), baseline.reads) == {"colour": 2, "size": 3}


# -- the derived clock (item 6) ------------------------------------------------------------------


@pytest.mark.parametrize("marker", mp.GITHUB_CLOCK_MARKERS)
def test_a_github_marker_overrules_what_the_caller_says(marker: str) -> None:
    clock, why = mp.derive_clock("local", {marker: "true"})
    assert clock == mp.GOVERNED_CLOCK
    assert "not believed" in why and marker in why


def test_without_a_marker_the_callers_word_stands() -> None:
    assert mp.derive_clock("local", {})[0] == "local"
    assert mp.derive_clock("github", {})[0] == "github"
    assert mp.derive_clock(None, {})[0] == "human"


def test_a_clock_nobody_has_heard_of_is_not_believed() -> None:
    clock, why = mp.derive_clock("whatever-i-like", {})
    assert clock == "human" and "not believed" in why


# -- the permission (items 1, 2, 5, 8, 9, 10) -----------------------------------------------------

_FACTS_SKILL = "gameplay-lens"


@pytest.fixture(scope="module")
def facts():
    return rss.corpus_facts(_FACTS_SKILL)


@pytest.fixture()
def good_row(facts):
    return {
        "skill": _FACTS_SKILL,
        "model_version": "fixture-model-1.0.0",
        "score": 0.95,
        "threshold": 0.65,
        "corpus_digest": facts["corpus_digest"],
        "recorded_at": "2026-09-21T00:00:00Z",
    }


def _permission(facts, rows, **over):
    kwargs = {
        "scores": rows,
        "corpus_digest_now": facts["corpus_digest"],
        "baseline": facts["baseline"],
        "variance": facts["variance"],
        "readings": (),
        "fitted_models": {},
        "threshold_now": 0.65,
    }
    kwargs.update(over)
    return mp.permission_for(_FACTS_SKILL, "fixture-model-1.0.0", **kwargs)


def _refused_items(permission):
    return {c.item for c in permission.refusals}


def test_a_model_that_clears_every_condition_is_granted(facts, good_row) -> None:
    """The positive control. A rule that refuses everything passes every negative control there
    is, and nothing in this estate holds a permission today, so this is the assertion that tells
    a working rule from a stuck one."""
    permission = _permission(facts, [good_row])
    assert permission.granted, permission.why()
    assert permission.permits(mp.JUDGE)


def test_a_score_under_the_threshold_is_refused(facts, good_row) -> None:
    assert 1 in _refused_items(_permission(facts, [{**good_row, "score": 0.10}]))


def test_the_bar_is_the_one_the_tree_sets_today(facts, good_row) -> None:
    """A row carries the threshold as it stood when the run happened. Reading the row's own
    number would let a raised threshold grant a permission the estate no longer means to give —
    item 2's reasoning applied to the bar instead of the corpus."""
    assert 1 in _refused_items(_permission(facts, [good_row], threshold_now=0.99))
    # ...and a score recorded against a different bar is refused even when it clears this one.
    assert 1 in _refused_items(_permission(facts, [{**good_row, "threshold": 0.20}], threshold_now=0.65))


def test_a_row_with_no_threshold_and_no_bar_handed_in_is_refused(facts, good_row) -> None:
    row = {k: v for k, v in good_row.items() if k != "threshold"}
    assert 1 in _refused_items(_permission(facts, [row], threshold_now=None))


def test_a_stale_corpus_digest_is_refused(facts, good_row) -> None:
    assert 2 in _refused_items(_permission(facts, [{**good_row, "corpus_digest": "0" * 64}]))


def test_no_recorded_score_at_all_is_refused(facts) -> None:
    """Absence is not consent, and the three conditions that read the missing row say so rather
    than passing vacuously."""
    refused = _refused_items(_permission(facts, []))
    assert {1, 2, 5, 9} <= refused, refused


def test_a_score_equal_to_the_corpus_baseline_is_refused(facts, good_row) -> None:
    """Strictly above, never equal: a model that ties the best constant answer has shown nothing
    the constant did not."""
    at = _permission(facts, [{**good_row, "score": facts["baseline"].score}])
    assert 9 in _refused_items(at)


def test_a_constant_field_revokes_the_permission(facts, good_row) -> None:
    flat = dict(facts)
    flat["variance"] = {"opportunities": 1}
    assert 8 in _refused_items(_permission(flat, [good_row]))


def test_a_recorded_constant_head_revokes_the_permission(facts, good_row) -> None:
    reading = mp.HeadReading("fixture-model-1.0.0", "act_probability", 279, 1, "ticket 04")
    assert reading.constant
    assert 8 in _refused_items(_permission(facts, [good_row], readings=[reading]))


def test_one_call_is_not_enough_to_call_a_head_constant() -> None:
    assert not mp.HeadReading("m", "h", 1, 1, "somewhere").constant


def test_no_variance_measured_at_all_is_refused(facts, good_row) -> None:
    assert 8 in _refused_items(_permission(facts, [good_row], variance=None))


def test_a_model_fitted_on_its_own_corpus_is_refused(facts, good_row) -> None:
    fitted = {"fixture-model-1.0.0": mp.FITTED_CORPUS_KIND}
    assert 10 in _refused_items(_permission(facts, [good_row], fitted_models=fitted))


def test_a_held_out_corpus_lifts_the_fitted_condition(facts, good_row) -> None:
    fitted = {"fixture-model-1.0.0": "held-out"}
    assert _permission(facts, [good_row], fitted_models=fitted).granted


def test_the_incumbent_is_the_model_condition_10_refuses_today() -> None:
    """Read off the twin, never typed: the day `CORPUS_KIND` says held-out, this test changes
    with it rather than having to be found."""
    from twin.evolution_judge import CORPUS_KIND

    assert rss.fitted_models() == {rss.HEURISTIC_MODEL_VERSION: CORPUS_KIND}


def test_a_seam_that_did_not_run_is_refused(facts, good_row) -> None:
    assert 6 in _refused_items(_permission(facts, [good_row], seam_crossed=False))


def test_the_newest_row_for_a_model_wins(good_row) -> None:
    older = {**good_row, "score": 0.10}
    newer = {**good_row, "score": 0.90}
    other = {**good_row, "model_version": "somebody-else", "score": 1.0}
    assert mp.newest_score(_FACTS_SKILL, "fixture-model-1.0.0", [older, other, newer])["score"] == 0.90


# -- item 4, as a property of the type ------------------------------------------------------------


def test_a_granted_permission_never_covers_the_merge(facts, good_row) -> None:
    permission = _permission(facts, [good_row])
    assert permission.granted
    assert permission.covers == mp.COVERS == frozenset({mp.JUDGE})
    assert not permission.permits(mp.MERGE)


def test_a_refused_permission_covers_nothing(facts) -> None:
    permission = _permission(facts, [])
    assert permission.covers == frozenset()
    assert not permission.permits(mp.JUDGE)


# -- the claim document (items 3, 4 and 7) ---------------------------------------------------------


def _doc(**run):
    block = {"skill": "classify-and-judge", "clock": "github", "model_version": "fixture-model-1.0.0", "declined": []}
    block.update(run)
    return {
        "schema": "twin.headline-claim/v1",
        "org": "driftwood",
        "run": block,
        "claims": [
            {
                "id": "c1",
                "kind": "binding",
                "component": "x",
                "evidence_grade": 5,
                "claimed_by": "signal-classify (skill)",
                "evidence": "e",
                "price_eligible": False,
            }
        ],
    }


@pytest.fixture()
def granting(facts, good_row):
    def lookup(skill, model_version):
        # The document maps `binding` to signal-classify; this fixture answers for whichever
        # skill it is asked about with the one corpus these tests measure against, because what
        # is under test here is the document rule, not the per-skill score.
        return _permission(facts, [good_row])

    return lookup


def test_a_github_clock_claim_naming_no_model_is_refused(granting) -> None:
    bad = mp.check_claim_document(_doc(model_version=None), "github", granting)
    assert any("item 3" in line for line in bad), bad


def test_an_ungoverned_clock_is_left_exactly_as_it_was(granting) -> None:
    """A human run is the skill's ordinary path and a local-clock run keeps ecosystem ticket 92's
    own terms. This rule governs the GitHub clock, which is the one the owner opened."""
    assert mp.check_claim_document(_doc(), "human", granting) == []
    assert mp.check_claim_document(_doc(), "local", granting) == []


def test_a_model_may_not_make_an_override(granting) -> None:
    doc = _doc()
    doc["claims"][0]["kind"] = "override"
    bad = mp.check_claim_document(doc, "github", granting)
    assert any("item 4" in line for line in bad), bad


def test_a_model_prices_nothing(granting) -> None:
    doc = _doc()
    doc["claims"][0]["price_eligible"] = True
    bad = mp.check_claim_document(doc, "github", granting)
    assert any("item 4" in line for line in bad), bad


def test_a_missing_decline_count_is_refused(granting) -> None:
    doc = _doc()
    del doc["run"]["declined"]
    bad = mp.check_claim_document(doc, "github", granting)
    assert any("item 7" in line for line in bad), bad


def test_a_decline_with_no_reason_is_refused(granting) -> None:
    bad = mp.check_claim_document(_doc(declined=[{"subject": "s"}]), "github", granting)
    assert any("item 7" in line for line in bad), bad


def test_a_claim_whose_permission_is_refused_is_refused(facts) -> None:
    def refusing(skill, model_version):
        return _permission(facts, [])

    bad = mp.check_claim_document(_doc(), "github", refusing)
    assert any("may not judge" in line for line in bad), bad


def test_a_fully_compliant_github_clock_file_is_accepted(granting) -> None:
    assert mp.check_claim_document(_doc(), "github", granting) == []


def test_an_exercise_rate_over_no_rows_is_undefined_never_full() -> None:
    """trdrbot defect I-16: a ladder that never counts its declines reports no rate, and a rate
    nobody can compute reads as 100%."""
    empty = mp.Exercise(judged=0, declined=0)
    assert empty.rate is None
    assert "undefined" in empty.describe() and "100%" in empty.describe()


def test_the_exercise_rate_counts_the_files_own_rows() -> None:
    worked = mp.exercise_of(_doc(declined=[{"subject": "s", "reason": "r"}, {"subject": "t", "reason": "r"}]))
    assert (worked.judged, worked.declined) == (1, 2)
    assert worked.rate == pytest.approx(1 / 3)


# -- the head readings file -------------------------------------------------------------------------


def test_the_readings_file_records_the_head_ticket_04_measured() -> None:
    readings = mp.load_head_readings()
    act = [r for r in readings if r.head == "act_probability"]
    assert act and act[0].n == 279 and act[0].distinct == 1 and act[0].constant


def test_a_readings_file_that_is_not_one_is_refused(tmp_path) -> None:
    path = tmp_path / "readings.yaml"
    path.write_text("schema: something-else\nreadings: []\n", encoding="utf-8")
    with pytest.raises(mp.PermissionError_):
        mp.load_head_readings(path)


def test_a_missing_readings_file_is_empty_never_an_error(tmp_path) -> None:
    assert mp.load_head_readings(tmp_path / "nothing.yaml") == []
