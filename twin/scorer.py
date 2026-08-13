"""`scorer` (build ticket 52, decision ticket 12 AC 4, Q3b): the half that "reads both."

Decision ticket 12 Q2: "a scorer reads both" — `score()` takes the planter's own sealed
`ground_truth` and the detector's own `detections` as two independent, explicit arguments, never a
merged object and never a shared container the two write into, so nothing about how one was
produced can leak into the other except by being handed to this function by its caller.

Q3b — the actionability horizon: "detection after the point of no return scores as the near-zero
option value it actually is. Finding it late is not finding it." `score()`'s own `detected_at`
argument is compared against each plant's `actionability_horizon` (day-string comparison, the same
ordering `regimes.cutoff` and `Spine.at` already use over dated facts elsewhere in this codebase):
a plant found on or before its horizon scores `TIMELY_SCORE`; found after, `LATE_SCORE` — near
zero, not zero, because a late detection is not worthless (a post-mortem still has value), just far
short of the option value a timely one would have carried. A plant never detected at all scores
`MISSED_SCORE`. Every outcome carries a plain-language `reason` a reader can act on without opening
this module's source.

Q2 also names the limit this split does not fix: "planter and detector are the same model family
and share priors... a synthetic result is never evidence the twin anticipates the world."
`ScoreResult.limitation` carries `planter.SHARED_PRIOR_LIMITATION` verbatim on every result this
module returns — published with the score itself, not left in a footnote or a README paragraph a
reader has to go find.
"""

from __future__ import annotations

from dataclasses import dataclass

from .detector import Detection
from .planter import SHARED_PRIOR_LIMITATION, Plant

TIMELY_SCORE = 1.0
LATE_SCORE = 0.05  # near-zero, not zero: a late detection is a post-mortem, not nothing.
MISSED_SCORE = 0.0


@dataclass(frozen=True)
class PlantScore:
    plant: Plant
    detected: bool
    timely: bool | None  # None when never detected — there is no "on time" question to answer
    score: float
    reason: str


@dataclass(frozen=True)
class ScoreResult:
    detected_at: str
    plant_scores: tuple[PlantScore, ...]
    limitation: str

    @property
    def hit_rate(self) -> float:
        if not self.plant_scores:
            return 0.0
        return sum(1 for p in self.plant_scores if p.detected) / len(self.plant_scores)

    @property
    def mean_score(self) -> float:
        if not self.plant_scores:
            return 0.0
        return sum(p.score for p in self.plant_scores) / len(self.plant_scores)


def score(
    ground_truth: tuple[Plant, ...], detections: tuple[Detection, ...], detected_at: str
) -> ScoreResult:
    """The scorer. `ground_truth` (from `planter.plant`) and `detections` (from `detector.detect`)
    are two independent arguments this function combines — never read from a shared object either
    module wrote into. `detected_at` is the date the detector's run is being scored as having
    happened.
    """
    found = {(d.channel, d.index) for d in detections}
    plant_scores: list[PlantScore] = []
    for p in ground_truth:
        if (p.channel, p.index) not in found:
            plant_scores.append(
                PlantScore(
                    plant=p, detected=False, timely=None, score=MISSED_SCORE,
                    reason=f"not detected: no detection at {p.channel}[{p.index}] ({p.signal!r})",
                )
            )
            continue
        timely = detected_at <= p.actionability_horizon
        if timely:
            plant_scores.append(
                PlantScore(
                    plant=p, detected=True, timely=True, score=TIMELY_SCORE,
                    reason=(
                        f"detected at {detected_at}, on or before the actionability horizon "
                        f"{p.actionability_horizon} — still actionable"
                    ),
                )
            )
        else:
            plant_scores.append(
                PlantScore(
                    plant=p, detected=True, timely=False, score=LATE_SCORE,
                    reason=(
                        f"detected at {detected_at}, after the actionability horizon "
                        f"{p.actionability_horizon} — the point of no return has passed; scored "
                        "near zero, not as a genuine finding (decision ticket 12 Q3b)"
                    ),
                )
            )
    return ScoreResult(detected_at=detected_at, plant_scores=tuple(plant_scores), limitation=SHARED_PRIOR_LIMITATION)
