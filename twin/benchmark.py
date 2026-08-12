"""Benchmark question selection and ingestion quarantine (build ticket 57, decision ticket 21).

Decision ticket 21 Q1 named two mechanisms that defend different failures, both needed: temporal
separation (pinned, signed emission before a resolution window — build ticket 58's job) and a
**quarantined benchmark set**, never ingested as a signal in any form, at any lag. This ticket
builds the second half plus the machinery Q2 asks the first half to rest on: a **mechanical,
versioned, pre-registered selection rule**, so cherry-picking easy questions is structurally
prevented and a change to the rule is as visible as a change to the constraint set
(`twin/constraints.yaml`).

**The rule is mechanical and reproducible, not a per-run judgement call.**
`twin/benchmark-selection-rule.yaml` states everything in resolvable terms — a liquidity
threshold, a resolution-horizon window, a category list — so `eligible()` needs no interpretation,
and `select_questions()` sorts by id before anything else touches the candidate pool, so arrival
order (which a venue adapter could quietly reorder) never matters. The one place chance enters is
decision ticket 21 Q2's own named exception — "(c) random sampling as a volume valve if the rule
selects too many" — and even that draws from the rule's own committed `sample_seed`, so a re-run
against the identical pool selects the identical subset rather than an ad hoc cut.

**The distribution is emitted, not claimed.** `confidence_distribution()` bins the selected set by
its own `implied_probability`, and `BenchmarkSet.spans_full_confidence_range()` is true only when
every declared bin holds at least one question — "the boring near-certainties reliability diagrams
need at the extremes" (decision ticket 21 Q2), checked against the artefact's own body rather than
asserted in prose.

**The quarantine is a scan, not a filter with a blind spot.** `audit_quarantine()` serialises each
ingestion-provenance record whole and checks it for a substring match against every quarantined
question id, so a breach hiding in a nested field — a recipe id, a source string, a claim's own
text — is caught rather than only a single named field a caller happened to check. Nothing here
reads a timestamp, which is what makes the quarantine hold "at any lag": a record from the day the
benchmark was drawn and one audited a year later are scanned identically.

**The residual limit is stated, not papered over (decision ticket 21 Q1).** A clean audit proves
*no direct ingestion* of a quarantined question id. It cannot prove the twin's priors were
unshaped by market-adjacent information reaching it some other way — that is the gap temporal
separation (build ticket 58) exists to narrow, not this ticket's to close.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import PACKAGE_DIR
from .artefact import DERIVED, Artefact
from .canon import digest_of
from .grades import Capabilities

RULE_PATH = PACKAGE_DIR / "benchmark-selection-rule.yaml"

KIND_BENCHMARK_SET = "benchmark-set"
KIND_QUARANTINE_AUDIT = "quarantine-audit"

# The capability this module's artefacts declare (`twin/capabilities/forecast-book.yaml`, owning
# decision ticket 21) — a list because `caps.depth_block` takes one, not because a second
# capability is expected here.
CAPS_BENCHMARK = ["forecast-book"]

_REQUIRED_RULE_KEYS = (
    "version", "min_liquidity", "min_horizon_days", "max_horizon_days",
    "categories", "confidence_bins", "max_questions", "sample_seed",
)


class BenchmarkError(RuntimeError):
    pass


@dataclass(frozen=True)
class SelectionRule:
    """The mechanical rule, loaded from a committed, versioned file. Every field is resolvable —
    no field here asks a reader to exercise judgement."""

    version: str
    min_liquidity: float
    min_horizon_days: int
    max_horizon_days: int
    categories: tuple[str, ...]
    confidence_bins: tuple[tuple[float, float], ...]
    max_questions: int
    sample_seed: int

    @staticmethod
    def load(path: Path | None = None) -> "SelectionRule":
        source = path or RULE_PATH
        raw = yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise BenchmarkError(f"{source}: expected a mapping")
        missing = [k for k in _REQUIRED_RULE_KEYS if k not in raw]
        if missing:
            raise BenchmarkError(f"{source}: missing required key(s): {', '.join(missing)}")
        bins = tuple((float(lo), float(hi)) for lo, hi in raw["confidence_bins"])
        if not bins:
            raise BenchmarkError(f"{source}: confidence_bins is empty — nothing to demonstrate a spread over")
        if int(raw["max_questions"]) <= 0:
            raise BenchmarkError(f"{source}: max_questions must be positive, got {raw['max_questions']!r}")
        return SelectionRule(
            version=str(raw["version"]),
            min_liquidity=float(raw["min_liquidity"]),
            min_horizon_days=int(raw["min_horizon_days"]),
            max_horizon_days=int(raw["max_horizon_days"]),
            categories=tuple(str(c) for c in raw["categories"]),
            confidence_bins=bins,
            max_questions=int(raw["max_questions"]),
            sample_seed=int(raw["sample_seed"]),
        )

    def digest(self) -> str:
        """The rule's own content digest — the identical role a recipe's id/digest plays in
        `twin/ingest.py`'s provenance: what a reader compares to confirm which version of the
        rule produced a given selection."""
        return digest_of(
            {
                "version": self.version,
                "min_liquidity": self.min_liquidity,
                "min_horizon_days": self.min_horizon_days,
                "max_horizon_days": self.max_horizon_days,
                "categories": list(self.categories),
                "confidence_bins": [list(b) for b in self.confidence_bins],
                "max_questions": self.max_questions,
                "sample_seed": self.sample_seed,
            }
        )


def eligible(rule: SelectionRule, question: dict[str, Any]) -> bool:
    """The resolvable-terms filter decision ticket 21 Q2 requires: liquidity, horizon, category —
    nothing here calls for interpretation."""
    return (
        float(question["liquidity"]) >= rule.min_liquidity
        and rule.min_horizon_days <= int(question["horizon_days"]) <= rule.max_horizon_days
        and str(question["category"]) in rule.categories
    )


def _bin_label(lo: float, hi: float) -> str:
    return f"{lo:g}-{hi:g}"


def _bin_of(rule: SelectionRule, probability: float) -> tuple[float, float] | None:
    for lo, hi in rule.confidence_bins:
        if lo <= probability < hi:
            return (lo, hi)
    top = rule.confidence_bins[-1]
    if probability == top[1]:
        return top
    return None


def confidence_distribution(rule: SelectionRule, questions: Iterable[dict[str, Any]]) -> dict[str, int]:
    """A histogram over the rule's own declared bins — every bin present, zero included, so an
    empty bin is visible rather than merely absent from the count."""
    counts = {_bin_label(lo, hi): 0 for lo, hi in rule.confidence_bins}
    for q in questions:
        located = _bin_of(rule, float(q["implied_probability"]))
        if located is not None:
            counts[_bin_label(*located)] += 1
    return counts


@dataclass(frozen=True)
class BenchmarkSet:
    rule_version: str
    rule_digest: str
    questions: tuple[dict[str, Any], ...]
    distribution: dict[str, int]

    @property
    def ids(self) -> frozenset[str]:
        return frozenset(str(q["id"]) for q in self.questions)

    def spans_full_confidence_range(self) -> bool:
        """True only when every declared bin holds at least one selected question — the
        demonstrated spread decision ticket 21 Q2 asks for, not merely a range at the extremes."""
        return all(count > 0 for count in self.distribution.values())


def select_questions(rule: SelectionRule, pool: list[dict[str, Any]]) -> BenchmarkSet:
    """Mechanical and reproducible: the identical rule against the identical pool always draws
    the identical selection, in the identical order — sorted by id, never by arrival order (which
    a venue adapter could quietly reorder to bias what gets selected first when a volume cap
    bites). The volume valve (decision ticket 21 Q2's own "(c)") applies only once the mechanical
    filter selects more than `rule.max_questions`, drawing deterministically from the rule's own
    committed seed rather than an ad hoc trim.
    """
    if not pool:
        raise BenchmarkError("select_questions: pool is empty — nothing to select from")
    candidates = sorted((q for q in pool if eligible(rule, q)), key=lambda q: str(q["id"]))
    if not candidates:
        raise BenchmarkError("select_questions: no question in the pool satisfies the rule")
    if len(candidates) > rule.max_questions:
        rng = random.Random(rule.sample_seed)
        candidates = sorted(rng.sample(candidates, rule.max_questions), key=lambda q: str(q["id"]))
    return BenchmarkSet(
        rule_version=rule.version,
        rule_digest=rule.digest(),
        questions=tuple(candidates),
        distribution=confidence_distribution(rule, candidates),
    )


def benchmark_set_artefact(
    caps: Capabilities, rule: SelectionRule, pool: list[dict[str, Any]], command: list[str]
) -> Artefact:
    """The selection, as a derived artefact: nothing here could carry a human's accountability
    (`derived_never_human_signed`) — the rule and the pool determine the output completely."""
    benchmark = select_questions(rule, pool)
    return Artefact(
        kind=KIND_BENCHMARK_SET,
        mark=DERIVED,
        command=command,
        pins={
            "rule": {"version": rule.version, "digest": rule.digest()},
            "pool_digest": digest_of(sorted(pool, key=lambda q: str(q["id"]))),
            "tool": {"capabilities_digest": caps.digest},
        },
        depth=caps.depth_block(CAPS_BENCHMARK),
        body={
            "questions": [
                {"id": q["id"], "category": q["category"], "implied_probability": q["implied_probability"]}
                for q in benchmark.questions
            ],
            "distribution": benchmark.distribution,
            "spans_full_confidence_range": benchmark.spans_full_confidence_range(),
            "pool_size": len(pool),
            "selected": len(benchmark.questions),
        },
    )


@dataclass(frozen=True)
class QuarantineBreach:
    question_id: str
    where: str

    def as_dict(self) -> dict[str, str]:
        return {"question_id": self.question_id, "where": self.where}


def audit_quarantine(
    benchmark: BenchmarkSet, ingestion_records: Iterable[tuple[str, dict[str, Any]]]
) -> list[QuarantineBreach]:
    """Scan ingestion-provenance records for any reference to a quarantined question id, in any
    form, at any lag (decision ticket 21 Q1(b)). Each record is serialised whole and scanned for a
    substring match against every quarantined id, so a breach hiding anywhere nested — a recipe
    id, a source string, a claim's own text — is caught rather than only a single named field a
    caller happened to check. Lag is not a parameter: nothing here reads a timestamp, so a record
    from the day the benchmark was drawn and one audited a year later are scanned identically.
    """
    if not benchmark.ids:
        raise BenchmarkError("audit_quarantine: benchmark set is empty — nothing to audit against")
    breaches: list[QuarantineBreach] = []
    ids = sorted(benchmark.ids)
    for label, record in ingestion_records:
        haystack = json.dumps(record, sort_keys=True, default=str, ensure_ascii=True)
        for qid in ids:
            if qid in haystack:
                breaches.append(QuarantineBreach(question_id=qid, where=label))
    return breaches


def quarantine_audit_artefact(
    caps: Capabilities,
    benchmark: BenchmarkSet,
    ingestion_records: list[tuple[str, dict[str, Any]]],
    command: list[str],
) -> Artefact:
    breaches = audit_quarantine(benchmark, ingestion_records)
    return Artefact(
        kind=KIND_QUARANTINE_AUDIT,
        mark=DERIVED,
        command=command,
        pins={
            "benchmark": {
                "rule_version": benchmark.rule_version,
                "rule_digest": benchmark.rule_digest,
                "ids_digest": digest_of(sorted(benchmark.ids)),
            },
            "tool": {"capabilities_digest": caps.digest},
        },
        depth=caps.depth_block(CAPS_BENCHMARK),
        body={
            "records_checked": len(ingestion_records),
            "clean": not breaches,
            "breaches": [b.as_dict() for b in breaches],
        },
    )
