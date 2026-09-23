"""When a model may judge on a clock — the permission, as ten conditions a check can grade.

Wayfinder ticket 05 (`.scratch/laya-loophole/issues/05-...`). On 2026-09-21 the owner permitted a
model to judge on a GitHub clock, **within thresholds**. This module turns "within thresholds"
into something that grades, because a permission stated in prose is a permission nobody can
refuse.

**Nothing here grants a permission today.** Every condition below is measured, and on 2026-09-21
every model in the score log failed at least one of them on every skill: the candidate on items
1, 2, 5, 8 and 9, and the incumbent on item 10. That is the honest output of the rule, not a
defect in it. The rule is built so the first model that clears it is the first one that has
earned it.

## The ten conditions

Items 1 to 9 are ticket 05's own, and item 10 was forced by the first run of the nine. Each is a
`Condition` row on the `Permission` this module returns, so a refusal always names which one
refused.

1. `threshold_cleared` — the newest recorded score for that skill AND that `model_version`
   clears the versioned threshold **in `twin/skill-thresholds.yaml` today**, and the bar it was
   recorded against is that same bar. A row carries the threshold as it stood when the run
   happened, so reading the row's own number would let a raised threshold grant a permission the
   estate no longer means to give. This is item 2's reasoning applied to the bar instead of the
   corpus. The run must also be measurable (ticket 112): a row whose outcome is `not-measurable`,
   or whose item count is below the `min_items` the tree states today, clears nothing, whatever
   it scored. And the number that meets the bar is the row's `attributable_rate`, not its
   `score` (eco-system ticket 118): a right answer on a wrong basis lowers the rate, and a row
   that records no rate, or a null one, clears nothing, because its score may rest on luck.
2. `corpus_current` — that scoring run's `corpus_digest` is the digest of the corpus in the tree
   today. A stale digest revokes the permission.
3. `claim_names_the_model` — the claim records which `model_version` judged it. Graded on the
   claim document (`check_claim_document`), not on the model.
4. `judging_only` — the permission covers judging and never merging. `Permission.permits()`
   returns False for every action but `judge`, and a model may not make an `override`, which is
   the grade a human's own judgement occupies.
5. `score_recorded` — a skill with no recorded score for this model has no permission. Absence
   is not consent.
6. `seam_crossed` — the permission binds at a seam the actor cannot route around. See **The
   seam** below.
7. `refusals_counted` — a run that declines to judge leaves a counted row, so the permission's
   real exercise rate is knowable. Graded on the claim document.
8. `head_varies` — the variance of the field a permission reads, not only its value. A field
   whose recorded outputs carry one distinct value across a run revokes the permission it was
   supposed to grant, whatever that value is.
9. `beats_constant_baseline` — the score must be strictly above the best score the corpus admits
   from an answer that holds that field constant. See **The frozen-field baseline**.
10. `corpus_not_fitted` — a score recorded against the corpus the model was FITTED on is not
    evidence of judgement, so it grants nothing. This is the tenth, beyond ticket 05's nine, and
    it was added because the first run of the nine granted the incumbent heuristic a permission
    on five of seven metrics. `twin/evolution_judge.py`'s own `CORPUS_KIND` already declares why
    that score is not one: it reads `harness-mechanism`, which its own comment defines as "while
    every corpus item is one the heuristic was fitted to". `verify-twin-evals.sh` prints the same
    word on every run. So the estate already said the incumbent's 1.000 grades the harness and
    not the twin's judgement, and a permission that rested on it would be the same defect class
    as items 8 and 9: a number that cannot come out any other way. It applies to the incumbent
    alone; a candidate model that was never fitted on these corpora is not touched by it, and the
    condition says which model it is refusing and why. One edit to `CORPUS_KIND`, the day a
    held-out corpus exists, lifts it.

Items 6 and 8 came from measurement rather than from reasoning, and both came from somebody
else's working system. Item 6 is the trdrbot prior art's own open defect I-68: a complete,
working permission ladder consulted in 2 of 89 decide cycles, because "the refusals that matter
happen upstream in prose". Item 7 is its sibling I-16: declines are never scored. Item 8 is
ticket 02 and ticket 04 in this estate: Laya's `act_probability` read exactly 1.000000 on all 279
calls, and loophole's judge called 17 of 18 candidates resolvable. A permission that always says
yes is not a permission.

## The seam

The seam is **the claim validator, run by the clock over every committed claim file, out of a
tree the model could not write to**:

    .claude/skills/classify-and-judge/assets/validate_claim.py::validate

`talk/local-clock.sh` copies the twin package and the skill to a judge tree **before** the child
model starts (ticket 93 review F5), refuses any committed file that is not a `*.claim.yaml`, and
runs that validator over every one of them. A refusal fails the step and the branch is never
pushed. The model never chooses whether the validator runs, which is exactly what the trdrbot
ladder's caller did choose.

`derive_clock()` closes the last way round it: the clock is **derived** from the environment the
run happened in, never believed off the file. A run inside GitHub Actions is a `github` clock
whatever its claim file says. This is the same discipline the `--headless` fix applied when the
no-override rule rested on the model declaring itself headless.

## The frozen-field baseline

Item 9's bar. `signal-classify`'s threshold is 0.80 and "always economic" scores 0.913 on its own
corpus, so a model that has learned nothing clears the threshold (ticket 04). The bar is
therefore the corpus's own best constant answer, not the threshold.

`frozen_field_baseline()` derives it rather than asserting it, in three measured steps:

1. **Which fields the scorer reads.** Each leaf of the model's answer is perturbed to a sentinel
   across the whole corpus. A leaf whose perturbation changes no item's score is not read, and is
   granted. Nothing is hand-listed, so a scorer that starts reading a new field is followed.
2. **The candidate constants.** For each read leaf, every distinct value the answers take there,
   plus the mean and median where the values are numeric. The mean matters: `causal-claims`'
   elasticity constant is 0.375, exactly the mean of its own four labels, inside a tolerance of
   0.15 that covers all four (ticket 04).
3. **The score.** One read leaf is frozen at a candidate, and every other field is granted from
   the item's own correct answer. The best such score is the baseline.

Read it precisely: the baseline is **the best score a model reaches while holding one field the
scorer reads constant, with every other field granted correct**. A score at or below it means the
corpus cannot show the model doing that field's work. It is deliberately the generous reading, so
the bar is hard rather than flattering.

The method reproduces both numbers ticket 04 measured by hand: `signal-classify` 0.913 from
"always economic", and `causal-claims` 1.000 from the elasticity constant.
"""

from __future__ import annotations

import copy
import json
import os
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import yaml

from . import PACKAGE_DIR
from .skills import NOT_MEASURABLE

# -- what a clock is -------------------------------------------------------------------------

# `human`  somebody at a keyboard; the skill's ordinary path, and no model judged.
# `local`  the owner's own machine, from his own schedule (ecosystem ticket 92). Governed by
#          that ticket's own terms: no override, stop-and-ask items left unbound, a human merges.
# `github` a GitHub Actions clock. This is the route the owner opened on 2026-09-21, and the one
#          this module governs: ADR-0024 and ticket 75 Q10 forbade it outright before that.
CLOCKS = ("human", "local", "github")
GOVERNED_CLOCK = "github"

# The environment variables a GitHub Actions run cannot honestly be without. The clock is derived
# from these and never read off the claim file, because a model that writes its own clock field
# writes its own permission. `verify-model-permission.sh` asserts separately that no workflow in
# the tree sets or clears any of them, which is the only way left to lie about this.
GITHUB_CLOCK_MARKERS = ("GITHUB_ACTIONS", "GITHUB_RUN_ID", "GITHUB_WORKFLOW")

# The seam, named in code so a check can assert the name and a reader can find the file.
SEAM = ".claude/skills/classify-and-judge/assets/validate_claim.py::validate"
SEAM_RUNNER = "talk/local-clock.sh"

# What a permission covers. A frozenset of one, and `permits()` is the only reader: item 4 is a
# property of the type, not a rule somebody remembers to apply.
JUDGE = "judge"
MERGE = "merge"
COVERS = frozenset({JUDGE})

# Which skill's score governs which claim kind. A model may make neither of the other two kinds:
# an `override` is grade-4 calibrated judgement claimed by a role, which is a human's, and an
# `enactment` records that a lever was pulled, which is nobody's judgement at all.
SKILL_FOR_CLAIM_KIND: dict[str, str] = {
    "binding": "signal-classify",
    "position": "evolution-judge",
}
MODEL_FORBIDDEN_CLAIM_KINDS = ("override", "enactment")

# Condition 10. The corpus kind the estate declares for the incumbent's own scores, and the one
# value of it that means "fitted on the corpus it is graded against". Read off the skill module
# rather than typed, so the day a held-out corpus lands this condition lifts itself.
FITTED_CORPUS_KIND = "harness-mechanism"

HEAD_READINGS_PATH = PACKAGE_DIR / "model-head-readings.yaml"
HEAD_READINGS_SCHEMA = "twin.model-head-readings/v1"

# A one-value field is only evidence of a constant head once there was something to vary over.
MIN_READINGS_FOR_VARIANCE = 2

_SENTINELS: tuple[Any, ...] = ("\x00not-an-answer\x00", None)


class PermissionError_(RuntimeError):
    """A head-reading file that is not one, or a corpus a baseline cannot be derived from."""


# -- the derived clock (item 6) ----------------------------------------------------------------


def derive_clock(declared: str | None, env: Mapping[str, str] | None = None) -> tuple[str, str]:
    """The clock this run really happened on, and why.

    `declared` is what the caller says. The environment overrules it: a run carrying any GitHub
    Actions marker is a `github` clock whatever anybody wrote down. Returns `(clock, why)`; the
    `why` is printed by the validator, because a derivation nobody can read is an assertion.
    """
    environment = os.environ if env is None else env
    seen = [name for name in GITHUB_CLOCK_MARKERS if environment.get(name)]
    if seen:
        why = f"{', '.join(seen)} is set in the environment, so this run is on a GitHub clock"
        if declared and declared != GOVERNED_CLOCK:
            why += f" — the file declares {declared!r}, which is not believed"
        return GOVERNED_CLOCK, why
    if declared is None:
        return "human", "no GitHub Actions marker and no clock declared, so a human ran it"
    if declared not in CLOCKS:
        return "human", f"declared clock {declared!r} is not one of {CLOCKS}, so it is not believed"
    return declared, f"no GitHub Actions marker in the environment, and the caller says {declared!r}"


# -- the frozen-field baseline (item 9) ---------------------------------------------------------


@dataclass(frozen=True)
class Baseline:
    """The best constant answer a corpus admits, and which field was held constant to reach it."""

    score: float
    frozen_field: str
    frozen_value: str
    reads: tuple[str, ...]

    @property
    def description(self) -> str:
        return (
            f"always {self.frozen_field}={self.frozen_value}, every other field the scorer reads "
            f"granted correct"
        )


def _leaf_paths(doc: Any, prefix: tuple[str, ...] = ()) -> Iterable[tuple[str, ...]]:
    if isinstance(doc, dict):
        for key in doc:
            yield from _leaf_paths(doc[key], prefix + (key,))
    else:
        yield prefix


def _read_leaf(doc: Any, path: tuple[str, ...]) -> Any:
    cursor = doc
    try:
        for key in path:
            cursor = cursor[key]
    except (KeyError, TypeError, IndexError):
        return None
    return cursor


def _with_leaf(doc: Any, path: tuple[str, ...], value: Any) -> Any:
    out = copy.deepcopy(doc)
    cursor = out
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return out


def scores_item(scorer: Callable[[Any, Any], bool], answer: Any, expected: Any) -> bool:
    """A scorer that raises on a perturbed answer has said "wrong", which is what a caller
    handing it a malformed answer would get. Never an error here: the perturbation is the
    instrument, and an instrument that crashes measures nothing."""
    try:
        return bool(scorer(copy.deepcopy(answer), expected))
    except Exception:  # noqa: BLE001 — any refusal to score is a False, see docstring
        return False


def _key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def fields_the_scorer_reads(
    answers: Sequence[Any], corpus: Sequence[Mapping[str, Any]], scorer: Callable[[Any, Any], bool]
) -> tuple[tuple[str, ...], ...]:
    """Which leaves of the answer the scorer actually reads, measured by perturbation.

    Nothing is hand-listed. A leaf is read when replacing it with a sentinel changes at least one
    item's score; a leaf that changes nothing is granted by the baseline below, which raises the
    bar rather than lowering it.
    """
    if not answers:
        raise PermissionError_("no answers: the fields a scorer reads cannot be measured from nothing")
    base = [scores_item(scorer, a, item["expected"]) for a, item in zip(answers, corpus)]
    out: list[tuple[str, ...]] = []
    for path in _leaf_paths(answers[0]):
        for sentinel in _SENTINELS:
            perturbed = [scores_item(scorer, _with_leaf(a, path, sentinel), item["expected"]) for a, item in zip(answers, corpus)]
            if perturbed != base:
                out.append(path)
                break
    return tuple(out)


def frozen_field_baseline(
    answers: Sequence[Any], corpus: Sequence[Mapping[str, Any]], scorer: Callable[[Any, Any], bool]
) -> Baseline:
    """The best score reachable while one field the scorer reads is held constant.

    See this module's docstring for the three steps and for how to read the number. The
    `answers` are a reference answer set — one correct answer per item — which is what grants the
    other fields. `record_skill_scores`' incumbent supplies them while it scores 1.000.
    """
    if not corpus:
        raise PermissionError_("an empty corpus admits no constant answer")
    reads = fields_the_scorer_reads(answers, corpus, scorer)
    total = len(corpus)
    best = Baseline(score=0.0, frozen_field="none", frozen_value="none", reads=tuple(".".join(p) for p in reads))
    for path in reads:
        values: list[Any] = []
        seen: set[str] = set()
        for answer in answers:
            value = _read_leaf(answer, path)
            if _key(value) not in seen:
                seen.add(_key(value))
                values.append(value)
        numbers = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if numbers:
            # The mean is a candidate because a fitted constant hides there: `causal-claims`'
            # elasticity constant is exactly its own corpus's mean (ticket 04).
            values = values + [statistics.fmean(numbers), statistics.median(numbers)]
        for value in values:
            hits = sum(
                scores_item(scorer, _with_leaf(answer, path, value), item["expected"])
                for answer, item in zip(answers, corpus)
            )
            score = hits / total
            if score > best.score:
                best = Baseline(
                    score=score,
                    frozen_field=".".join(path),
                    frozen_value=_key(value)[:60],
                    reads=tuple(".".join(p) for p in reads),
                )
    return best


def answer_variance(answers: Sequence[Any], reads: Sequence[str]) -> dict[str, int]:
    """How many distinct values each field the scorer reads took across the run. Item 8's input:
    a field that took one is a constant head, and a constant head is not a signal."""
    out: dict[str, int] = {}
    for dotted in reads:
        path = tuple(dotted.split("."))
        out[dotted] = len({_key(_read_leaf(answer, path)) for answer in answers})
    return out


# -- recorded head readings (item 8, for a model the gate cannot run) ---------------------------


@dataclass(frozen=True)
class HeadReading:
    model_version: str
    head: str
    n: int
    distinct: int
    measured_by: str

    @property
    def constant(self) -> bool:
        return self.n >= MIN_READINGS_FOR_VARIANCE and self.distinct <= 1


def load_head_readings(path: Path | None = None) -> list[HeadReading]:
    """The recorded variance of a head this gate cannot re-measure, because the model is not in
    the tree. Validated on read, the same discipline `load_thresholds` applies: a readings file
    that has quietly lost an entry still looks recorded."""
    source = path or HEAD_READINGS_PATH
    if not source.is_file():
        return []
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != HEAD_READINGS_SCHEMA:
        raise PermissionError_(f"{source}: not a {HEAD_READINGS_SCHEMA} document")
    rows = doc.get("readings")
    if not isinstance(rows, list):
        raise PermissionError_(f"{source}: declares no readings list")
    out = []
    for index, row in enumerate(rows):
        missing = [f for f in ("model_version", "head", "n", "distinct", "measured_by") if f not in row]
        if missing:
            raise PermissionError_(f"{source}: reading {index} declares no {', '.join(missing)}")
        out.append(
            HeadReading(
                model_version=str(row["model_version"]),
                head=str(row["head"]),
                n=int(row["n"]),
                distinct=int(row["distinct"]),
                measured_by=str(row["measured_by"]),
            )
        )
    return out


# -- the permission --------------------------------------------------------------------------


@dataclass(frozen=True)
class Condition:
    item: int
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Permission:
    skill: str
    model_version: str
    conditions: tuple[Condition, ...]

    @property
    def granted(self) -> bool:
        return all(c.passed for c in self.conditions)

    @property
    def refusals(self) -> tuple[Condition, ...]:
        return tuple(c for c in self.conditions if not c.passed)

    @property
    def covers(self) -> frozenset[str]:
        """Item 4, as a property of the type. Judging, and nothing else, and only once granted."""
        return COVERS if self.granted else frozenset()

    def permits(self, action: str) -> bool:
        return action in self.covers

    def why(self) -> str:
        if self.granted:
            return f"{self.model_version} may judge {self.skill}: all {len(self.conditions)} conditions hold"
        reasons = "; ".join(f"item {c.item} ({c.name}): {c.detail}" for c in self.refusals)
        return f"{self.model_version} may not judge {self.skill} — {reasons}"


def newest_score(
    skill: str, model_version: str, scores: Iterable[Mapping[str, Any]]
) -> Mapping[str, Any] | None:
    """The last row this skill and this model version recorded. The log is append-only and
    chronological, so the last matching row is the newest one without reading a timestamp — the
    same reasoning `skills.detect_regression` gives for its own ordering."""
    found = None
    for row in scores:
        if row.get("skill") == skill and str(row.get("model_version")) == model_version:
            found = row
    return found


def _below_minimum(row: Mapping[str, Any], min_items_now: int | None) -> str:
    """Why a score row is not measurable, or "" when it is. Ticket 112: a run below the minimum
    corpus its threshold states is not measurable whatever it scored, so it cannot clear item 1.
    The minimum is the tree's today, as the threshold is; the row's own number stands only when
    none is handed in."""
    if str(row.get("outcome", "")) == NOT_MEASURABLE:
        return "the row records its own outcome as not-measurable"
    minimum = min_items_now if min_items_now is not None else row.get("min_items")
    if minimum is None:
        return "no minimum corpus size is stated for this threshold"
    counted = row.get("measured_count", row.get("total"))
    if counted is None:
        return "the row records no item count to set against the minimum"
    if int(counted) < int(minimum):
        return f"it counted {int(counted)} items against a stated minimum of {int(minimum)}"
    return ""


def _attributable_rate(row: Mapping[str, Any]) -> tuple[float | None, str]:
    """The rate item 1 grades, or None with the reason it cannot. Eco-system ticket 118: the
    threshold is met by the attributable rate, which a right answer on a wrong basis lowers, and
    never by the score. A row written before ticket 118 records no rate, and a row that measured
    nothing records null. Both are refused: absence is not consent."""
    if "attributable_rate" not in row:
        return None, "the row records no attributable rate, so its score may rest on luck"
    if row["attributable_rate"] is None:
        return None, "the row measured no item on a checkable basis, so nothing separates its score from luck"
    return float(row["attributable_rate"]), ""


def permission_for(
    skill: str,
    model_version: str,
    *,
    scores: Iterable[Mapping[str, Any]],
    corpus_digest_now: str,
    threshold_now: float | None = None,
    min_items_now: int | None = None,
    baseline: Baseline | None,
    variance: Mapping[str, int] | None,
    readings: Sequence[HeadReading] = (),
    seam_crossed: bool = True,
    seam_detail: str = "",
    fitted_models: Mapping[str, str] | None = None,
) -> Permission:
    """Grade the seven conditions a model and its record can carry, and return the permission.

    Items 3, 4 and 7 are properties of the claim document and of this type, not of the model, so
    they are graded by `check_claim_document()` and by `Permission.covers`. Items 1, 2, 5, 8, 9
    and 10 are graded here, and item 6 is handed in by the caller that knows whether the seam ran.

    `threshold_now` is the versioned threshold in the tree, which item 1 compares against; the
    row's own recorded threshold is compared to it as well, because a score graded against a
    different bar is not a score against this one. Left out, the row's own number stands, which
    is only safe for a caller that has no threshold file to read.

    `min_items_now` is the minimum corpus size the tree states for that threshold today (ticket
    112). Item 1 refuses a row whose own outcome is `not-measurable`, and a row whose measured
    count (`measured_count`, else `total`) is below this minimum, whatever it scored. Left out,
    the row's own `min_items` stands; a row with neither has no minimum and is refused, as a row
    with no threshold is. The number item 1 compares with the threshold is the row's
    `attributable_rate` (eco-system ticket 118); a row without one is refused.

    `fitted_models` maps a model version to the corpus kind its recorded scores were measured
    under. A model whose kind is `FITTED_CORPUS_KIND` was fitted on the corpus it is graded
    against, so condition 10 refuses it.
    """
    rows = list(scores)
    latest = newest_score(skill, model_version, rows)
    conditions: list[Condition] = []

    # Item 5 first: every later condition reads the row this one looks for.
    if latest is None:
        conditions.append(
            Condition(5, "score_recorded", False, f"no row in the score log for {skill!r} and {model_version!r}; absence is not consent")
        )
        conditions.append(Condition(1, "threshold_cleared", False, "no recorded score to compare against a threshold"))
        conditions.append(Condition(2, "corpus_current", False, "no recorded score, so no corpus digest to compare"))
        conditions.append(Condition(9, "beats_constant_baseline", False, "no recorded score to compare against the corpus baseline"))
    else:
        score = float(latest["score"])
        recorded_threshold = float(latest["threshold"]) if "threshold" in latest else None
        threshold = threshold_now if threshold_now is not None else recorded_threshold
        digest = str(latest.get("corpus_digest", ""))
        conditions.append(
            Condition(5, "score_recorded", True, f"score {score:.3f} recorded at {latest.get('recorded_at', 'an unstated time')}")
        )
        if threshold is None:
            conditions.append(
                Condition(1, "threshold_cleared", False, "the row records no threshold and none was handed in, so there is no bar to clear")
            )
        else:
            bar_moved = recorded_threshold is not None and abs(recorded_threshold - threshold) > 1e-9
            rate, unattributed = _attributable_rate(latest)
            shown = "none" if rate is None else f"{rate:.3f}"
            detail = f"attributable rate {shown} (score {score:.3f}) against the versioned threshold {threshold:.3f}"
            if unattributed:
                detail += f"; {unattributed}"
            if bar_moved:
                detail += (
                    f"; the score was recorded against {recorded_threshold:.3f}, a different bar, so it "
                    f"is not a score against this one"
                )
            short = _below_minimum(latest, min_items_now)
            if short:
                detail += f"; {short}, so the run is not measurable and its score clears nothing"
            # The score is read as well. An honest row's rate never exceeds its score (a rate drops
            # the unscoreable items the score counts, and counts only right-on-a-held-basis), so a
            # row with a rate over the bar and a score under it is not an honest row.
            cleared = rate is not None and rate >= threshold and score >= threshold and not bar_moved and not short
            conditions.append(Condition(1, "threshold_cleared", cleared, detail))
        conditions.append(
            Condition(
                2,
                "corpus_current",
                digest == corpus_digest_now,
                f"scored on corpus {digest[:12]}, the tree holds {corpus_digest_now[:12]}",
            )
        )
        if baseline is None:
            conditions.append(
                Condition(9, "beats_constant_baseline", False, "the corpus baseline could not be derived, so the score cannot be placed against it")
            )
        else:
            conditions.append(
                Condition(
                    9,
                    "beats_constant_baseline",
                    score > baseline.score,
                    f"score {score:.3f} against the corpus's own best constant answer {baseline.score:.3f} ({baseline.description})",
                )
            )

    # Item 8: the variance of what the permission reads, not only its value.
    constant_fields = sorted(name for name, distinct in (variance or {}).items() if distinct <= 1)
    constant_heads = [r for r in readings if r.model_version == model_version and r.constant]
    if variance is None and not readings:
        conditions.append(
            Condition(8, "head_varies", False, "no variance was measured or recorded for this model, and an unmeasured head is not a varying one")
        )
    elif constant_fields or constant_heads:
        parts = []
        if constant_fields:
            parts.append(f"the scorer reads {', '.join(constant_fields)}, which took one distinct value across the corpus")
        for reading in constant_heads:
            parts.append(f"{reading.head} read one distinct value on all {reading.n} calls ({reading.measured_by})")
        conditions.append(Condition(8, "head_varies", False, "; ".join(parts)))
    else:
        measured = ", ".join(f"{k}={v}" for k, v in sorted((variance or {}).items()))
        conditions.append(Condition(8, "head_varies", True, f"every field the scorer reads took more than one value ({measured or 'no fields measured'})"))

    # Item 10: a score on the corpus the model was fitted on is not evidence of judgement.
    kind = (fitted_models or {}).get(model_version)
    if kind is None:
        conditions.append(
            Condition(10, "corpus_not_fitted", True, f"{model_version} was not fitted on this corpus, so its score measures judgement rather than the harness")
        )
    elif kind == FITTED_CORPUS_KIND:
        conditions.append(
            Condition(
                10,
                "corpus_not_fitted",
                False,
                f"{model_version} is graded against the corpus it was fitted on (corpus kind {kind!r}), "
                f"so its score grades the harness and not its judgement; the estate says so itself in "
                f"twin/evolution_judge.py's CORPUS_KIND and on every verify-twin-evals.sh run",
            )
        )
    else:
        conditions.append(Condition(10, "corpus_not_fitted", True, f"the corpus kind for {model_version} is {kind!r}, not {FITTED_CORPUS_KIND!r}"))

    # Item 6: whether the seam ran. The caller knows; this type records it beside the rest so a
    # refusal that is really "nobody checked" cannot read as "the model passed".
    conditions.append(
        Condition(6, "seam_crossed", seam_crossed, seam_detail or f"the seam is {SEAM}, run by {SEAM_RUNNER}")
    )
    return Permission(skill=skill, model_version=model_version, conditions=tuple(sorted(conditions, key=lambda c: c.item)))


# -- the claim document (items 3, 4 and 7) ------------------------------------------------------


@dataclass(frozen=True)
class Exercise:
    """How often the permission was really exercised, and how often it was declined. trdrbot's
    defect I-16: a ladder that never counts its declines cannot report its own exercise rate, and
    a rate nobody can compute reads as 100%."""

    judged: int
    declined: int

    @property
    def total(self) -> int:
        return self.judged + self.declined

    @property
    def rate(self) -> float | None:
        return None if self.total == 0 else self.judged / self.total

    def describe(self) -> str:
        if self.total == 0:
            return "0 judged and 0 declined: no clock run has landed a claim file, so the exercise rate is not 100%, it is undefined, and this says so"
        return f"{self.judged} judged, {self.declined} declined, exercise rate {self.rate:.3f}"


def exercise_of(doc: Mapping[str, Any]) -> Exercise:
    """One claim file's own counted rows. `run.declined` is where a decline is counted; it is a
    list of `{subject, reason}`, and an empty list is a real answer while a missing key is not."""
    run = doc.get("run") or {}
    declined = run.get("declined")
    return Exercise(judged=len(doc.get("claims") or []), declined=len(declined) if isinstance(declined, list) else 0)


def check_claim_document(
    doc: Mapping[str, Any],
    clock: str,
    permission_for_skill: Callable[[str, str], Permission],
) -> list[str]:
    """Every reason this claim file may not land on this clock; `[]` when it may.

    Only a `github` clock is governed here. A `human` run is the skill's ordinary path and a
    `local` run keeps ecosystem ticket 92's own terms, which this module does not reopen. The
    clock is the caller's derived fact (`derive_clock`), never the file's word.
    """
    if clock != GOVERNED_CLOCK:
        return []
    bad: list[str] = []
    run = doc.get("run") or {}

    # Item 3. A claim with no recorded model is not a permitted claim.
    model_version = str(run.get("model_version") or "")
    if not model_version:
        bad.append(
            "run.model_version is not stated: this ran on a GitHub clock, and a claim that does "
            "not record which model judged it is not a permitted claim (item 3)"
        )
    if run.get("clock") != GOVERNED_CLOCK:
        bad.append(
            f"run.clock is {run.get('clock')!r} but this run is on a GitHub clock "
            f"({', '.join(GITHUB_CLOCK_MARKERS)} decide, not the file) (item 6)"
        )

    # Item 7. A decline must leave a counted row, or the exercise rate is unknowable.
    if not isinstance(run.get("declined"), list):
        bad.append(
            "run.declined is not a list: a run that declines to judge must leave a counted row, "
            "or the permission's real exercise rate is unknowable (item 7). An empty list is an "
            "answer; a missing key is not"
        )
    else:
        for index, row in enumerate(run["declined"]):
            if not isinstance(row, dict) or not row.get("subject") or not row.get("reason"):
                bad.append(f"run.declined[{index}] does not name both a subject and a reason: an uncounted decline is item 7's whole defect")

    for claim in doc.get("claims") or []:
        where = f"claim {claim.get('id')!r}"
        kind = str(claim.get("kind") or "")

        # Item 4. Judging only. An override is grade-4 judgement claimed by a role, which is a
        # human's; pricing is the override's alone; and merging is never covered at all.
        if kind in MODEL_FORBIDDEN_CLAIM_KINDS:
            bad.append(
                f"{where}: a {kind!r} from a model on a GitHub clock — the permission covers "
                f"{sorted(COVERS)} and nothing else, and a {kind!r} is not a judgement a model may make (item 4)"
            )
            continue
        if claim.get("price_eligible"):
            bad.append(f"{where}: price_eligible from a model on a GitHub clock; only an override prices, and a model makes none (item 4)")

        skill = SKILL_FOR_CLAIM_KIND.get(kind)
        if skill is None:
            bad.append(f"{where}: kind {kind!r} maps to no skill whose score could grant a permission (item 1)")
            continue
        if not model_version:
            continue
        permission = permission_for_skill(skill, model_version)
        if not permission.granted:
            bad.append(f"{where}: {permission.why()}")
        elif not permission.permits(JUDGE):
            bad.append(f"{where}: the permission is granted and still does not cover judging, which is a bug in this module, not in the file")

    return bad
