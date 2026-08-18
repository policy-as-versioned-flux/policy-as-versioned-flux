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
    return doc


def threshold_for(skill: str, path: Path | None = None) -> float:
    thresholds = load_thresholds(path)["thresholds"]
    if skill not in thresholds:
        known = ", ".join(sorted(thresholds)) or "none"
        raise SkillError(f"no threshold declared for skill {skill!r} (have: {known})")
    return float(thresholds[skill]["threshold"])


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

    @property
    def score(self) -> float:
        return sum(1 for i in self.items if i.passed) / len(self.items)

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold

    def as_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "corpus_digest": self.corpus_digest,
            "threshold": self.threshold,
            "score": self.score,
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
    items = tuple(
        ItemResult(item_id=str(item["id"]), passed=bool(scorer(skill_fn(item["input"]), item["expected"])))
        for item in corpus
    )
    return EvalResult(skill=skill, corpus_digest=digest_of(corpus), threshold=threshold, items=items)


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
]


def toy_classifier(text: str) -> str:
    """A trivial fixture skill — not one of the six real skills. Exists only so the harness has
    something to run against; the harness itself must not name this function anywhere."""
    return text.upper()
