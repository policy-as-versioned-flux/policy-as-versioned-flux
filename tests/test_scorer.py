"""`scorer` (build ticket 52, decision ticket 12 AC 4, Q3b): the half that "reads both" — ground
truth from `planter.plant` and detections from `detector.detect`, as two independent arguments —
and scores a detection against its own plant's actionability horizon: on time scores full marks,
after the point of no return scores near zero, and the reason is always visible. Every result also
carries the shared-prior limitation, published with the score rather than left in a footnote.
"""

from __future__ import annotations

import inspect

from twin.detector import Detection
from twin.grades import Capabilities
from twin.planter import SHARED_PRIOR_LIMITATION, Plant
from twin.scorer import LATE_SCORE, MISSED_SCORE, TIMELY_SCORE, ScoreResult, score

_PLANT = Plant(channel="events", index=3, signal="a distinctive planted line", actionability_horizon="2018-06-01")


def test_score_takes_ground_truth_and_detections_as_two_independent_arguments() -> None:
    params = list(inspect.signature(score).parameters)
    assert params == ["ground_truth", "detections", "detected_at"]


def test_a_detection_on_or_before_the_horizon_scores_full_marks() -> None:
    detection = (Detection(channel="events", index=3, line="whatever", outlier_score=0.0),)
    result = score((_PLANT,), detection, detected_at="2018-05-01")
    ps = result.plant_scores[0]
    assert ps.detected and ps.timely
    assert ps.score == TIMELY_SCORE


def test_a_detection_exactly_on_the_horizon_date_scores_full_marks() -> None:
    detection = (Detection(channel="events", index=3, line="whatever", outlier_score=0.0),)
    result = score((_PLANT,), detection, detected_at="2018-06-01")
    assert result.plant_scores[0].score == TIMELY_SCORE


def test_a_detection_after_the_horizon_scores_near_zero_and_names_the_horizon() -> None:
    detection = (Detection(channel="events", index=3, line="whatever", outlier_score=0.0),)
    result = score((_PLANT,), detection, detected_at="2018-06-02")
    ps = result.plant_scores[0]
    assert ps.detected and ps.timely is False
    assert ps.score == LATE_SCORE
    assert 0.0 < ps.score < 0.1, "late is near-zero, not zero and not still-substantial"
    assert "2018-06-01" in ps.reason
    assert "horizon" in ps.reason.lower()


def test_a_missed_plant_scores_zero_and_names_the_miss() -> None:
    result = score((_PLANT,), (), detected_at="2018-05-01")
    ps = result.plant_scores[0]
    assert not ps.detected
    assert ps.timely is None
    assert ps.score == MISSED_SCORE
    assert "not detected" in ps.reason.lower()


def test_a_detection_at_the_wrong_location_does_not_count() -> None:
    wrong = (Detection(channel="hr", index=0, line="whatever", outlier_score=0.0),)
    result = score((_PLANT,), wrong, detected_at="2018-05-01")
    assert not result.plant_scores[0].detected


def test_every_score_result_carries_the_shared_prior_limitation_verbatim() -> None:
    for detections, detected_at in (
        ((Detection(channel="events", index=3, line="x", outlier_score=0.0),), "2018-05-01"),
        ((), "2018-05-01"),
    ):
        result = score((_PLANT,), detections, detected_at)
        assert isinstance(result, ScoreResult)
        assert result.limitation == SHARED_PRIOR_LIMITATION
        assert result.limitation, "published, not an empty string"


def test_hit_rate_and_mean_score_across_multiple_plants() -> None:
    """One timely, one late (its own horizon already passed by `detected_at`), one missed."""
    timely = Plant(channel="events", index=0, signal="s1", actionability_horizon="2018-12-01")
    late = Plant(channel="hr", index=1, signal="s2", actionability_horizon="2018-01-01")
    missed = Plant(channel="telemetry", index=2, signal="s3", actionability_horizon="2018-06-01")
    detections = (
        Detection(channel="events", index=0, line="x", outlier_score=0.0),
        Detection(channel="hr", index=1, line="x", outlier_score=0.0),
    )
    result = score((timely, late, missed), detections, detected_at="2018-06-15")
    assert result.hit_rate == 2 / 3
    scores = sorted(ps.score for ps in result.plant_scores)
    assert scores == sorted([TIMELY_SCORE, LATE_SCORE, MISSED_SCORE])
    assert result.mean_score == (TIMELY_SCORE + LATE_SCORE + MISSED_SCORE) / 3


# -- the depth grade: this ticket ticks decision ticket 12 AC 4 -----------------------------------


def test_the_synthetic_substrate_capability_grade_moves_to_4_of_7() -> None:
    """Build ticket 52 ticks decision ticket 12's AC 4 (a blind/adversarial separation mechanism
    between planter and detector) — the planter/detector/scorer split itself is the realisation.
    AC 3 (planting protocol) stays unticked: the actionability horizon covers the lead-time clause
    but "strength" is untouched, the same "one clause of a multi-clause criterion" ground build
    tickets 49 and 51 already left it on."""
    caps = Capabilities.load()
    graded = caps.require("synthetic-substrate")
    assert graded.owning_ticket == "12"
    assert graded.grade == "partial"
    checked = {c.index for c in graded.criteria if c.checked}
    assert checked == {1, 2, 4, 5}
