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
# (the basis a skill stated, the basis the corpus item carries) -> did the stated basis hold.
BasisScorer = Callable[[Any, Any], bool]

# -- the three run-level outcomes (eco-system ticket 112) -----------------------------------
# A run is graded at two levels, and the two are kept apart on purpose.
#   ITEM level: `ItemResult.verdict` says what one corpus item showed (ticket 118, below).
#   RUN level:  `EvalResult.outcome` says what the run as a whole may claim. It reads the item
#               level through two numbers only: `attributable_rate` (against the threshold) and
#               `measured_count` (against the minimum the threshold states).
# NOT_MEASURABLE is a run-level outcome: too few items were measured for the threshold to mean
# anything, whatever they scored. It is not an item state.
PASS = "pass"
FAIL = "fail"
NOT_MEASURABLE = "not-measurable"

# -- the item verdicts (eco-system ticket 118) ------------------------------------------------
# An item is read twice: was the answer right, and did the basis the skill stated hold against
# the basis the corpus item carries. `attribute()` turns the two readings into one verdict.
#   RIGHT        the answer was right and its stated basis was checked and held
#   WRONG        the answer was wrong, whatever its basis
#   WRONG_BASIS  the answer was right and its stated basis was checked and did not hold
#   UNSCOREABLE  the answer was right and no basis could be checked: the corpus item carries
#                none, or the skill stated none
# The words differ from the run outcomes on purpose, so an item verdict is never read as one.
# WRONG_BASIS is named for what the harness observes. "Lucky" would name a cause (chance) the
# harness never measures: a skill that learned a shortcut is right on a wrong basis every time.
RIGHT = "right"
WRONG = "wrong"
WRONG_BASIS = "wrong-basis"
UNSCOREABLE = "unscoreable"
ITEM_VERDICTS = (RIGHT, WRONG, WRONG_BASIS, UNSCOREABLE)


@dataclass(frozen=True)
class Stated:
    """A skill's answer together with the basis it states for it. A skill that returns a bare
    value states no basis, so a right answer from it is UNSCOREABLE. `evaluate()` scores `answer`
    with the scorer and `basis` with the basis scorer; neither ever sees the other half."""

    answer: Any
    basis: Any


def attribute(answer_right: bool, basis_held: bool | None) -> str:
    """One item's verdict from its two readings. `basis_held` is None when no basis could be
    checked. A pure function, so the whole table is one test (eco-system ticket 118)."""
    if not answer_right:
        return WRONG
    if basis_held is None:
        return UNSCOREABLE
    return RIGHT if basis_held else WRONG_BASIS


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
    """One corpus item's verdict, one of `ITEM_VERDICTS`. Not a `passed` flag: a bool cannot
    hold a right answer on a wrong basis (eco-system ticket 118)."""

    item_id: str
    verdict: str

    @property
    def answered_right(self) -> bool:
        return self.verdict != WRONG


@dataclass(frozen=True)
class EvalResult:
    """One run of one skill against one corpus.

    Two rates, both proportions so they compare across corpora of different sizes:

    - `score` is the fraction of all items answered right, less those whose stated basis was
      checked and was wrong. Luck never raises it. On a corpus that carries no basis it is the
      plain fraction of right answers, which is what every row before ticket 118 recorded.
    - `attributable_rate` is the fraction of MEASURED items that were right on a basis that held.
      WRONG_BASIS stays in its denominator and out of its numerator, so luck lowers it.
      UNSCOREABLE is in neither: nothing was measured. It is None when nothing was measured.

    The threshold grades `attributable_rate`, over `measured_count` items (eco-system ticket 118).
    """

    skill: str
    corpus_digest: str
    threshold: float
    items: tuple[ItemResult, ...]
    min_items: int

    def _count(self, verdict: str) -> int:
        return sum(1 for i in self.items if i.verdict == verdict)

    @property
    def answered_right(self) -> int:
        return sum(1 for i in self.items if i.answered_right)

    @property
    def wrong_basis(self) -> int:
        return self._count(WRONG_BASIS)

    @property
    def unscoreable(self) -> int:
        return self._count(UNSCOREABLE)

    @property
    def score(self) -> float:
        return (self.answered_right - self.wrong_basis) / len(self.items)

    @property
    def measured_count(self) -> int:
        """How many items the rate and the minimum are measured against: every item but the
        unscoreable ones. A wrong-basis item IS measured, because its basis was checked and
        failed; leaving it out would let luck shrink the corpus instead of lowering the rate. A
        wrong answer is measured whatever its basis, because it is evidence against the skill
        either way (eco-system ticket 118)."""
        return len(self.items) - self.unscoreable

    @property
    def attributable_rate(self) -> float | None:
        if self.measured_count == 0:
            return None
        return self._count(RIGHT) / self.measured_count

    @property
    def measurable(self) -> bool:
        return self.measured_count >= self.min_items

    @property
    def clears_threshold(self) -> bool:
        """The score alone against the threshold, whatever the corpus size or its bases. What the
        per-skill guards assert when they prove a threshold gates something; never a pass on its
        own."""
        return self.score >= self.threshold

    @property
    def outcome(self) -> str:
        """PASS, FAIL or NOT_MEASURABLE. Measurability is decided first: below the minimum the
        threshold says nothing, so neither a perfect nor a zero rate may speak for it. Then the
        attributable rate, not the score, meets the threshold: a threshold graded on a score that
        counts luck grades nothing (eco-system ticket 118)."""
        rate = self.attributable_rate
        if not self.measurable or rate is None:
            return NOT_MEASURABLE
        return PASS if rate >= self.threshold else FAIL

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
            "measured_count": self.measured_count,
            "score": self.score,
            "attributable_rate": self.attributable_rate,
            "outcome": self.outcome,
            "passed": self.passed,
            "total": len(self.items),
            "correct": self.answered_right,
            "wrong_basis": self.wrong_basis,
            "unscoreable": self.unscoreable,
            "items": [{"id": i.item_id, "verdict": i.verdict} for i in self.items],
        }


def evaluate(
    skill: str,
    skill_fn: Callable[[Any], Any],
    corpus: list[dict[str, Any]],
    scorer: Scorer = _exact_match,
    threshold_path: Path | None = None,
    basis_scorer: BasisScorer = _exact_match,
) -> EvalResult:
    """Run `skill_fn` against every corpus item, score it, and compare to the versioned threshold.

    A corpus item is `{"id": ..., "input": ..., "expected": ...}`, with an optional `"basis"`:
    the reason a right answer must rest on. `skill_fn` sees only `input`: it has no way to read
    `expected` or `basis`, which is what keeps this an evaluation rather than a tautology. The
    default scorer is exact match; a skill whose output space is not equality-comparable (free
    text, say) supplies its own. The same holds for `basis_scorer`.

    A skill states a basis by returning `Stated(answer, basis)`. A right answer is RIGHT only when
    both the item and the skill carry a basis and the basis scorer says the stated one held
    (eco-system ticket 118). Otherwise `attribute()` decides, and `ITEM_VERDICTS` lists the rest.
    """
    if not corpus:
        raise SkillError(f"skill {skill!r}: an empty corpus evaluates nothing")
    for i, item in enumerate(corpus):
        missing = [f for f in ("id", "input", "expected") if f not in item]
        if missing:
            raise SkillError(f"skill {skill!r}: corpus item {i} declares no {', '.join(missing)}")

    threshold = threshold_for(skill, threshold_path)
    min_items = min_items_for(skill, threshold_path)
    items = tuple(_verdict(item, skill_fn(item["input"]), scorer, basis_scorer) for item in corpus)
    return EvalResult(
        skill=skill, corpus_digest=digest_of(corpus), threshold=threshold, items=items, min_items=min_items,
    )


def _verdict(item: dict[str, Any], output: Any, scorer: Scorer, basis_scorer: BasisScorer) -> ItemResult:
    answer, stated = (output.answer, output.basis) if isinstance(output, Stated) else (output, None)
    right = bool(scorer(answer, item["expected"]))
    basis = item.get("basis")
    held = None
    if right and basis is not None and stated is not None:
        held = bool(basis_scorer(stated, basis))
    return ItemResult(item_id=str(item["id"]), verdict=attribute(right, held))


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
        # Eco-system ticket 118: the rate the threshold grades, beside the score, with the two
        # counts that separate them. None when nothing was measured, never 0.
        "attributable_rate": result.attributable_rate,
        "wrong_basis": result.wrong_basis,
        "unscoreable": result.unscoreable,
        "threshold": result.threshold,
        "min_items": result.min_items,
        "outcome": result.outcome,
        "passed": result.passed,
        "corpus_digest": result.corpus_digest,
        "total": len(result.items),
        "measured_count": result.measured_count,
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

# Eco-system ticket 118: every toy item carries the basis a right answer must rest on, and the toy
# states it, so the fixture proves an attributable pass and not only the unscoreable state.
TOY_BASIS = "upper-case every letter"

TOY_SKILL_CORPUS: list[dict[str, Any]] = [
    {"id": "shout", "input": "hello", "expected": "HELLO", "basis": TOY_BASIS},
    {"id": "already-upper", "input": "WORLD", "expected": "WORLD", "basis": TOY_BASIS},
    {"id": "mixed", "input": "MiXeD", "expected": "MIXED", "basis": TOY_BASIS},
    {"id": "empty", "input": "", "expected": "", "basis": TOY_BASIS},
    {"id": "punctuation", "input": "hi!", "expected": "HI!", "basis": TOY_BASIS},
    # Eco-system ticket 112: the fixture's 0.8 threshold states a 16-item minimum, and a fixture
    # that is itself not measurable would prove only the third outcome. Eleven more, all trivial.
    {"id": "digits", "input": "abc123", "expected": "ABC123", "basis": TOY_BASIS},
    {"id": "space", "input": "a b", "expected": "A B", "basis": TOY_BASIS},
    {"id": "single", "input": "q", "expected": "Q", "basis": TOY_BASIS},
    {"id": "title", "input": "Title Case", "expected": "TITLE CASE", "basis": TOY_BASIS},
    {"id": "tab", "input": "x\ty", "expected": "X\tY", "basis": TOY_BASIS},
    {"id": "hyphen", "input": "re-run", "expected": "RE-RUN", "basis": TOY_BASIS},
    {"id": "underscore", "input": "snake_case", "expected": "SNAKE_CASE", "basis": TOY_BASIS},
    {"id": "trailing-space", "input": "end ", "expected": "END ", "basis": TOY_BASIS},
    {"id": "numbers-only", "input": "2026", "expected": "2026", "basis": TOY_BASIS},
    {"id": "sentence", "input": "a threshold states its corpus.", "expected": "A THRESHOLD STATES ITS CORPUS.", "basis": TOY_BASIS},
    {"id": "camel", "input": "camelCase", "expected": "CAMELCASE", "basis": TOY_BASIS},
]


def toy_classifier(text: str) -> Stated:
    """A trivial fixture skill — not one of the six real skills. Exists only so the harness has
    something to run against; the harness itself must not name this function anywhere. It states
    its basis, as a skill must for a right answer to count (eco-system ticket 118)."""
    return Stated(text.upper(), TOY_BASIS)
