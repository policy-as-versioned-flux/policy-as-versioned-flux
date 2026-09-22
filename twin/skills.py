"""The skill-eval harness — seam 3 (build ticket 42, decision ticket 20's determinism split).

**The six skills are non-deterministic by construction**, so they cannot be asserted at seam 1
(the artefact CLI) or seam 2 (the typed model API) at all — both of those assert that the same
pins produce the same bytes, and a skill is the one thing in this system that is allowed not to.
This module is the third seam: run a skill against a fixture corpus, score it with a **threshold,
not exact match**, and record the score against time so a model upgrade that quietly degrades
judgement shows up as a regression instead of being discovered inside an artefact months later.

**Skill-agnostic by construction, not by discipline.** `evaluate()` takes a bare callable and a
corpus; it does not know the name of a single one of the six real skills (signal-classify,
causal-claims, evolution-judge, substrate-generator, gameplay-lens, ethics-gate — decision ticket
20), none of which exist yet. Adding a seventh needs a corpus file and a threshold entry, never a
change here — `tests/test_skills.py` exercises the whole harness against a fixture skill
(`toy-classifier`) for exactly this reason: a harness tested only against skills that do not exist
yet is untested.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import yaml

from . import PACKAGE_DIR
from .canon import digest_of
from .corpus_size import CorpusSizeError, derived_min_items

# -- AC 1 (build ticket 90): the determinism-split test itself, queryable rather than prose the
#    capability inventory (`twin/honest_build.py`) would otherwise have to re-derive by hand from
#    this module's docstring above. Decision ticket 20 Q1's own words: "the test for the whole
#    inventory: if it must be reproducible from pins -> code; if it is a judgement landing at
#    grade 5 -> skill." `CODE_KIND`/`SKILL_KIND` are the two values `classify_by_determinism()`
#    returns; `INHERITED_KIND` (arckit-ported code) is `twin/honest_build.py`'s own concern, not
#    this module's, since inheritance is a provenance question orthogonal to determinism.
CODE_KIND = "code"
SKILL_KIND = "skill"

SKILL_DEFINITION = (
    "A skill is judgement that is irreducibly interpretive: it cannot be recomputed from pins "
    "(seeds, model versions, prompts) alone, and what it produces is a grade-5 model assertion "
    "rather than a derivation. Anything reproducible from pins is code, whatever heuristic "
    "implementation currently stands in for it (decision ticket 20 Q1). The unit of packaging is "
    "one module owning a `SKILL` name constant, a fixture corpus, and a threshold entry in "
    "skill-thresholds.yaml, run through this module's own evaluate()."
)


def classify_by_determinism(reproducible_from_pins: bool) -> str:
    """Decision ticket 20 Q1's own test, as one function: "if it must be reproducible from pins
    -> code; if it is a judgement landing at grade 5 -> skill." A caller asserts against this
    directly (`twin/honest_build.py`'s `CAPABILITY_INVENTORY`) instead of re-deriving the rule
    from this module's prose by hand, which is what AC 1 asks for."""
    return CODE_KIND if reproducible_from_pins else SKILL_KIND


THRESHOLDS_PATH = PACKAGE_DIR / "skill-thresholds.yaml"
SCORES_PATH = PACKAGE_DIR / "skill-scores.jsonl"
THRESHOLDS_SCHEMA = "twin.skill-thresholds/v1"

Scorer = Callable[[Any, Any], bool]

# -- the three run-level outcomes (eco-system ticket 112) -----------------------------------
# A run is graded at two levels, and the two are kept apart on purpose.
#   ITEM level: `ItemResult` says whether one corpus item was got right. `score` is the fraction.
#   RUN level:  `EvalResult.outcome` says what the run as a whole may claim. It reads the item
#               level through two numbers only: `score` (against the threshold) and
#               `measured_count` (against the minimum the threshold states).
# NOT_MEASURABLE is a run-level outcome: the corpus is too small for the threshold to mean
# anything, whatever the items scored. It is not an item state. Eco-system ticket 118 adds a third
# ITEM state (a right answer on a wrong basis); that changes the numerator of `score` and leaves
# this seam alone unless 118 also decides such an item should not count toward `measured_count`.
PASS = "pass"
FAIL = "fail"
NOT_MEASURABLE = "not-measurable"


class SkillError(RuntimeError):
    """A corpus that is not a corpus, a skill with no threshold, or a log that is not a log."""


def _exact_match(actual: Any, expected: Any) -> bool:
    return actual == expected


@lru_cache(maxsize=8)
def load_thresholds(path: Path | None = None) -> dict[str, Any]:
    """The versioned threshold set, validated on read — the same discipline the evidence ladder
    and the constraint set apply: a threshold file that has quietly lost an entry still looks set."""
    source = path or THRESHOLDS_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != THRESHOLDS_SCHEMA:
        raise SkillError(f"{source}: not a {THRESHOLDS_SCHEMA} document")
    thresholds = doc.get("thresholds")
    if not isinstance(thresholds, dict) or not thresholds:
        raise SkillError(f"{source}: declares no skill threshold")
    for name, entry in thresholds.items():
        if not isinstance(entry, dict) or "threshold" not in entry:
            raise SkillError(f"{source}: skill {name!r} declares no threshold")
        value = float(entry["threshold"])
        if not 0.0 <= value <= 1.0:
            raise SkillError(f"{source}: skill {name!r} threshold {value} is not a fraction in [0, 1]")
        # Eco-system ticket 112: every threshold states the corpus it is valid at, and the stated
        # number is the derived one. Below it the threshold claims more than its corpus carries;
        # above it the number was imported rather than derived. Both are refused on read, so a
        # hand edit cannot leave a stale minimum in force.
        stated = entry.get("min_items")
        if not isinstance(stated, int) or isinstance(stated, bool):
            raise SkillError(f"{source}: skill {name!r} states no min_items (an integer corpus size)")
        try:
            derived = derived_min_items(value)
        except CorpusSizeError as exc:
            raise SkillError(f"{source}: skill {name!r}: {exc}") from None
        if stated != derived:
            raise SkillError(
                f"{source}: skill {name!r} states min_items {stated}, but its threshold {value} "
                f"derives {derived} (twin/corpus_size.py); a minimum is derived, never typed"
            )
    return doc


def threshold_for(skill: str, path: Path | None = None) -> float:
    thresholds = load_thresholds(path)["thresholds"]
    if skill not in thresholds:
        known = ", ".join(sorted(thresholds)) or "none"
        raise SkillError(f"no threshold declared for skill {skill!r} (have: {known})")
    return float(thresholds[skill]["threshold"])


def min_items_for(skill: str, path: Path | None = None) -> int:
    """The corpus size the skill's threshold states it is valid at (eco-system ticket 112)."""
    threshold_for(skill, path)  # the same refusal for an unknown skill
    return int(load_thresholds(path)["thresholds"][skill]["min_items"])


@dataclass(frozen=True)
class ItemResult:
    item_id: str
    passed: bool


@dataclass(frozen=True)
class EvalResult:
    """One run of one skill against one corpus. `score` is the fraction of items that passed —
    proportion, never a raw count, so it compares across corpora of different sizes."""

    skill: str
    corpus_digest: str
    threshold: float
    items: tuple[ItemResult, ...]
    min_items: int

    @property
    def score(self) -> float:
        return sum(1 for i in self.items if i.passed) / len(self.items)

    @property
    def measured_count(self) -> int:
        """How many items the minimum is measured against. Today every item. The seam ticket 118
        builds on: an item state that should not count toward the corpus size changes this, and
        only this, on the run-level side."""
        return len(self.items)

    @property
    def measurable(self) -> bool:
        return self.measured_count >= self.min_items

    @property
    def clears_threshold(self) -> bool:
        """The score alone against the threshold, whatever the corpus size. What the per-skill
        guards assert when they prove a threshold gates something; never a pass on its own."""
        return self.score >= self.threshold

    @property
    def outcome(self) -> str:
        """PASS, FAIL or NOT_MEASURABLE. Measurability is decided first: below the minimum the
        threshold says nothing, so neither a perfect nor a zero score may speak for it."""
        if not self.measurable:
            return NOT_MEASURABLE
        return PASS if self.clears_threshold else FAIL

    @property
    def passed(self) -> bool:
        return self.outcome == PASS

    @property
    def failed(self) -> bool:
        return self.outcome == FAIL

    def as_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "corpus_digest": self.corpus_digest,
            "threshold": self.threshold,
            "min_items": self.min_items,
            "score": self.score,
            "outcome": self.outcome,
            "passed": self.passed,
            "total": len(self.items),
            "correct": sum(1 for i in self.items if i.passed),
            "items": [{"id": i.item_id, "passed": i.passed} for i in self.items],
        }


def evaluate(
    skill: str,
    skill_fn: Callable[[Any], Any],
    corpus: list[dict[str, Any]],
    scorer: Scorer = _exact_match,
    threshold_path: Path | None = None,
) -> EvalResult:
    """Run `skill_fn` against every corpus item, score it, and compare to the versioned threshold.

    A corpus item is `{"id": ..., "input": ..., "expected": ...}`. `skill_fn` sees only `input` —
    it has no way to read `expected`, which is what keeps this an evaluation rather than a
    tautology. The default scorer is exact match; a skill whose output space is not equality-
    comparable (free text, say) supplies its own.
    """
    if not corpus:
        raise SkillError(f"skill {skill!r}: an empty corpus evaluates nothing")
    for i, item in enumerate(corpus):
        missing = [f for f in ("id", "input", "expected") if f not in item]
        if missing:
            raise SkillError(f"skill {skill!r}: corpus item {i} declares no {', '.join(missing)}")

    threshold = threshold_for(skill, threshold_path)
    min_items = min_items_for(skill, threshold_path)
    items = tuple(
        ItemResult(item_id=str(item["id"]), passed=bool(scorer(skill_fn(item["input"]), item["expected"])))
        for item in corpus
    )
    return EvalResult(
        skill=skill, corpus_digest=digest_of(corpus), threshold=threshold, items=items, min_items=min_items,
    )


# -- score over time -------------------------------------------------------------------------


def record_score(
    result: EvalResult, model_version: str, recorded_at: str, path: Path | None = None
) -> dict[str, Any]:
    """Append one eval to the score-over-time log. `recorded_at` is supplied by the caller rather
    than read from the clock — the same discipline `drift.report(now, ...)` uses — so recording is
    a function of its inputs rather than of when it happened to run.

    Append-only: this never rewrites a prior line. `twin/invariants/harness.py`'s
    `skill_score_log_is_append_only` guard asserts that against git history the same way
    `hash_changes_are_authorised` does for the invariant manifest.
    """
    entry = {
        "skill": result.skill,
        "model_version": model_version,
        "recorded_at": recorded_at,
        "score": result.score,
        "threshold": result.threshold,
        "min_items": result.min_items,
        "outcome": result.outcome,
        "passed": result.passed,
        "corpus_digest": result.corpus_digest,
        "total": len(result.items),
    }
    target = path or SCORES_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def load_scores(path: Path | None = None) -> list[dict[str, Any]]:
    """Every recorded eval, oldest first. A missing log is empty, never an error — the ordinary
    state before a skill's first run, the same way an unsampled drift window is (`drift.py`)."""
    source = path or SCORES_PATH
    if not source.is_file():
        return []
    out = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            raise SkillError(f"{source}:{number}: not a JSON object") from None
        missing = [f for f in ("skill", "model_version", "score") if f not in doc]
        if missing:
            raise SkillError(f"{source}:{number}: a score entry declares no {', '.join(missing)}")
        out.append(doc)
    return out


def history_for(skill: str, path: Path | None = None) -> list[dict[str, Any]]:
    return [e for e in load_scores(path) if e["skill"] == skill]


def detect_regression(skill: str, path: Path | None = None) -> dict[str, Any]:
    """Compare the most recent two **distinct model versions'** latest scores for one skill.

    Per-model-version, not per-entry: two evals of the same model version are re-runs, not an
    upgrade, and diffing consecutive log lines would flag ordinary re-run noise as a regression.
    The log is append-only and chronological, so "latest score for a model version" is well
    defined without a timestamp comparison.
    """
    entries = history_for(skill, path)
    by_version: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for entry in entries:
        version = str(entry["model_version"])
        if version in order:
            # Re-evaluated after a different version was logged (a rollback re-check, an
            # interleaved candidate run) — move it to the end so "latest" tracks recency of
            # evaluation, not first sighting. Without this a version seen once early and never
            # touched again could still be reported as "the latest" over one genuinely re-run since.
            order.remove(version)
        order.append(version)
        by_version[version] = entry  # last write per version wins — the latest score for it

    if len(order) < 2:
        return {
            "skill": skill,
            "computed": False,
            "reason": f"{len(order)} model version(s) recorded; a regression needs at least two to compare",
        }
    previous_version, latest_version = order[-2], order[-1]
    previous, latest = by_version[previous_version], by_version[latest_version]
    regressed = latest["score"] < previous["score"]
    return {
        "skill": skill,
        "computed": True,
        "previous": {"model_version": previous_version, "score": previous["score"]},
        "latest": {"model_version": latest_version, "score": latest["score"]},
        "regressed": regressed,
        "delta": latest["score"] - previous["score"],
    }


# -- a fixture skill, for the harness to prove itself against ------------------------------

TOY_SKILL_CORPUS: list[dict[str, Any]] = [
    {"id": "shout", "input": "hello", "expected": "HELLO"},
    {"id": "already-upper", "input": "WORLD", "expected": "WORLD"},
    {"id": "mixed", "input": "MiXeD", "expected": "MIXED"},
    {"id": "empty", "input": "", "expected": ""},
    {"id": "punctuation", "input": "hi!", "expected": "HI!"},
    # Eco-system ticket 112: the fixture's 0.8 threshold states a 16-item minimum, and a fixture
    # that is itself not measurable would prove only the third outcome. Eleven more, all trivial.
    {"id": "digits", "input": "abc123", "expected": "ABC123"},
    {"id": "space", "input": "a b", "expected": "A B"},
    {"id": "single", "input": "q", "expected": "Q"},
    {"id": "title", "input": "Title Case", "expected": "TITLE CASE"},
    {"id": "tab", "input": "x\ty", "expected": "X\tY"},
    {"id": "hyphen", "input": "re-run", "expected": "RE-RUN"},
    {"id": "underscore", "input": "snake_case", "expected": "SNAKE_CASE"},
    {"id": "trailing-space", "input": "end ", "expected": "END "},
    {"id": "numbers-only", "input": "2026", "expected": "2026"},
    {"id": "sentence", "input": "a threshold states its corpus.", "expected": "A THRESHOLD STATES ITS CORPUS."},
    {"id": "camel", "input": "camelCase", "expected": "CAMELCASE"},
]


def toy_classifier(text: str) -> str:
    """A trivial fixture skill — not one of the six real skills. Exists only so the harness has
    something to run against; the harness itself must not name this function anywhere."""
    return text.upper()
