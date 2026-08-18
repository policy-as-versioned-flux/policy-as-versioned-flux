"""The intervention-aware scoring rule (decision ticket 08 Q4, build ticket 81).

AC 3 asked for one thing above all: a worked example, not prose. Three outcome records resolve
the identical proposition, from the identical forecast bundle, false — and the mitigation claim
attached to the outcome, not any change to the forecast itself, is what makes them score
differently. That is the point of the rule: the twin does not get to excuse a genuine miss with
"our warning prevented it" unless the prevention itself carries evidence, at the same grade a £
credit would need (`twin/pricing.py`'s own `_credit`, the identical discipline reused here rather
than reinvented).

* **Mitigated, evidenced (grade 1):** the event this forecast anticipated did not happen, and an
  evidenced intervention explains why. Excluded from the calibration record — `unscoreable`, not
  a miss.
* **Plain non-event, no claim at all:** the identical forecast, the identical non-event, and
  nothing on record to explain it. Scored exactly as it always was — a real, possibly bad, Brier
  score in the calibration pool.
* **Mitigated, but weakly (grade 4):** a claim was made, and it earns nothing. Decision ticket 08
  Q4's own words: "grades 4-5 earn NO calibration credit" — this forecast falls through to the
  identical plain scoring the no-claim case gets, because an ungraded excuse is worth exactly as
  much as no excuse.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures, verbs
from twin.grades import Capabilities
from twin.repo import ModelRepo

ORG = "netflix"
SCENARIO = "dvd-decline-2011"
AT = "2011-07-12"

MITIGATED_EVIDENCED = "dvd-decline-2011-mitigated-nonevent"
PLAIN_NONEVENT = "dvd-decline-2011-plain-nonevent"
MITIGATED_WEAK = "dvd-decline-2011-weak-mitigation-nonevent"

_OUTCOMES: dict[str, str] = {
    f"orgs/netflix/outcomes/{MITIGATED_EVIDENCED}.yaml": f"""\
id: {MITIGATED_EVIDENCED}
proposition: dvd-rental-revenue-falls-faster-than-streaming-adds
observed: false
resolved_on: '2012-12-31'
source: Test fixture, build ticket 81's worked example.
contamination: low
source_dated: true
mitigation:
  component: dvd-by-mail
  reduction:
    min: 0.5
    mode: 0.7
    max: 0.9
  evidence_grade: 1
  basis: >-
    The worked example's own dated natural experiment: a declared retention offer measured against
    subscriber numbers on both sides of it, the identical evidence shape decision ticket 08 Q2's
    own grade-1 example describes.
""",
    f"orgs/netflix/outcomes/{PLAIN_NONEVENT}.yaml": f"""\
id: {PLAIN_NONEVENT}
proposition: dvd-rental-revenue-falls-faster-than-streaming-adds
observed: false
resolved_on: '2012-12-31'
source: Test fixture, build ticket 81's worked example.
contamination: low
source_dated: true
""",
    f"orgs/netflix/outcomes/{MITIGATED_WEAK}.yaml": f"""\
id: {MITIGATED_WEAK}
proposition: dvd-rental-revenue-falls-faster-than-streaming-adds
observed: false
resolved_on: '2012-12-31'
source: Test fixture, build ticket 81's worked example.
contamination: low
source_dated: true
mitigation:
  component: dvd-by-mail
  reduction:
    min: 0.3
    mode: 0.5
    max: 0.7
  evidence_grade: 4
  basis: >-
    A calibration-trained estimator's judgement that the decline eased, recorded as judgement and
    never as an observation — decision ticket 08 Q4's own example of a grade that earns no
    calibration credit.
""",
}


@pytest.fixture()
def scoring_repo(scratch_repo: Path) -> Path:
    """The walking-skeleton fixture, widened with three outcomes for the identical proposition —
    the worked example's own dated evidence, added rather than fabricated into the shared fixture
    every other test reads (`twin/fixtures.py`'s own `build()`)."""
    for rel, content in _OUTCOMES.items():
        path = scratch_repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "build ticket 81: three outcomes, one forecast")
    return scratch_repo


@pytest.fixture()
def bundle_path(scoring_repo: Path, caps: Capabilities, tmp_path: Path) -> Path:
    """One forecast bundle, scored three times against three different outcomes below — the
    "identical claim" AC 3 itself asks for."""
    repo = ModelRepo.open(scoring_repo)
    artefact = verbs.run(
        repo, caps, ORG, SCENARIO, "as-consumed",
        verbs.command_for("run", org=ORG, scenario=SCENARIO, regime="as-consumed", at=AT),
        at=AT,
    )
    out = tmp_path / "bundle.json"
    artefact.write(out)
    return out


def _without_pins(scores: list[dict]) -> list[dict]:
    """Every score, minus its own forecast pins — the same bundle, scored twice, carries the
    identical pins either way, and comparing them adds nothing to the byte-for-byte claim."""
    return [{k: v for k, v in entry.items() if k != "pins"} for entry in scores]


def _score(scoring_repo: Path, caps: Capabilities, bundle_path: Path, outcome_id: str) -> dict:
    repo = ModelRepo.open(scoring_repo)
    artefact = verbs.score(
        repo, caps, ORG, bundle_path, outcome_id,
        verbs.command_for("score", org=ORG, forecast=str(bundle_path), outcome=outcome_id),
    )
    return artefact.body


def test_a_well_evidenced_mitigation_excludes_the_non_event_from_the_calibration_record(
    scoring_repo: Path, caps: Capabilities, bundle_path: Path
) -> None:
    body = _score(scoring_repo, caps, bundle_path, MITIGATED_EVIDENCED)
    assert body["scores"] == [], "a grade-1 mitigation claim excludes every forecast from scoring"
    reasons = {e["reason"] for e in body["unscoreable"]}
    assert reasons == {verbs.MITIGATED_NON_EVENT}
    entry = body["unscoreable"][0]
    assert entry["mitigation"]["evidence_grade"] == 1
    assert entry["mitigation"]["component"] == "dvd-by-mail"


def test_the_identical_claim_with_no_mitigation_scores_as_an_ordinary_non_event(
    scoring_repo: Path, caps: Capabilities, bundle_path: Path
) -> None:
    body = _score(scoring_repo, caps, bundle_path, PLAIN_NONEVENT)
    assert body["unscoreable"] == [], "nothing here excuses a plain non-event from scoring"
    assert body["scores"], "an unexplained non-event is an ordinary, scoreable calibration point"
    for entry in body["scores"]:
        assert entry["observed"] is False
        assert entry["brier"] == pytest.approx(entry["probability"] ** 2)


def test_a_weakly_graded_mitigation_claim_earns_no_calibration_credit(
    scoring_repo: Path, caps: Capabilities, bundle_path: Path
) -> None:
    """Decision ticket 08 Q4, verbatim: "grades 4-5 earn NO calibration credit." A grade-4 claim
    is not silently ignored — it is read, and it changes nothing: this scores byte-for-byte like
    the no-claim case above, because an ungraded excuse is worth exactly as much as none."""
    weak = _score(scoring_repo, caps, bundle_path, MITIGATED_WEAK)
    plain = _score(scoring_repo, caps, bundle_path, PLAIN_NONEVENT)
    assert weak["unscoreable"] == []
    assert _without_pins(weak["scores"]) == _without_pins(plain["scores"])


def test_the_same_mitigation_grade_is_moot_when_the_event_happened_anyway(
    scoring_repo: Path, caps: Capabilities, bundle_path: Path
) -> None:
    """A mitigation claim only ever explains a *non*-event. `dvd-decline-2011-resolved` — the
    fixture's own answer key — records `observed: true`, so the gate never engages regardless of
    what any outcome's `mitigation` block might say: there is nothing here to have prevented."""
    body = _score(scoring_repo, caps, bundle_path, "dvd-decline-2011-resolved")
    assert body["scores"], "an observed event scores plainly; mitigation only ever excuses a miss"
    assert all(e["observed"] is True for e in body["scores"])
