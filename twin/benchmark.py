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

**`proportionality_verdict()` (build ticket 84) lives here rather than in `twin/forecast_book.py`**
because that module's own public surface is a deliberately closed allow-list
(`forecast_book_is_blind_by_construction_and_observe_only`) and a fourth function there would need
a harness-guard change this ticket found no genuine reason to make. It closes decision ticket 21's
last acceptance criterion — see its own docstring for the reasoning.
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
from .forecast_book import CLAIM_SCOPE
from .grades import Capabilities

RULE_PATH = PACKAGE_DIR / "benchmark-selection-rule.yaml"

KIND_BENCHMARK_SET = "benchmark-set"
KIND_QUARANTINE_AUDIT = "quarantine-audit"
KIND_PROPORTIONALITY_VERDICT = "proportionality-verdict"

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


# -- decision ticket 21 AC 6: the proportionality verdict (build ticket 84) ----------------------
#
# Decision ticket 21 Q3's own resolved cost/benefit framing, cited verbatim rather than re-argued
# here — the verdict below is checked against the reasoning decision ticket 21 actually gave, not
# a fresh rationale invented for this artefact.
MARGINAL_COST = (
    "a versioned selection rule and a quarantine filter on the ingestion path (build ticket 57), "
    "plus a blind pinned-emission protocol (build ticket 58) and an observe-only signal connector "
    "(build ticket 59) — layered onto the scoring harness decision ticket 21 Q3 notes is already "
    "in the first slice (build ticket 20). Not a new forecasting system: a thin adapter pointing "
    "an existing one at extra questions"
)
DISPROPORTIONATE_VALUE = (
    "co-registration is the only falsification mechanism in this project that cannot be "
    "contaminated by construction (forward-dated questions cannot be in any training corpus); "
    "every other check here — synthetic substrate, historical backtests — has a memorisation "
    "problem that can be discounted but never eliminated. A narrow clean signal beats a broad "
    "compromised one (decision ticket 21 Q3)"
)


def proportionality_verdict(
    caps: Capabilities,
    rule: SelectionRule,
    benchmark: BenchmarkSet,
    resolved: list[dict[str, Any]],
    command: list[str],
) -> Artefact:
    """Decision ticket 21 AC 6, the one criterion build tickets 57-59 left open: given what
    forecast-book actually delivers, is it worth building at this coverage?

    A derived verdict, not a fresh opinion — every number below is read off what is actually
    delivered (the committed selection rule, an actually-selected benchmark set, actually-scored
    resolutions if any exist yet), not an aspiration, and the verdict is a function of them the
    same way `twin/verdict.py`'s `decide()` makes the Flux falsification question a function of
    its inputs rather than a declared conclusion. Two runs over the same inputs agree.

    **Coverage is judged on what the rule's own bar demands, not on a target this function
    invents.** `rule` requires the selected set to span every declared confidence bin
    (`twin/benchmark-selection-rule.yaml`'s own `confidence_bins`) — that is the "full confidence
    range" decision ticket 21 Q2 asked for, and it is checked against `benchmark`'s actual emitted
    distribution here exactly as `BenchmarkSet.spans_full_confidence_range()` already checks it,
    never asserted in prose.

    **The verdict is exactly one of three words, each earned by a structural fact:**
    - `no` — the set actually selected is empty. Building this delivers no coverage to weigh
      against any cost, so there is nothing here to be proportionate to.
    - `conditional` — questions are selected but the set does not yet span every declared
      confidence bin. The machinery holds (decision ticket 21 Q3's low marginal cost is real
      regardless), but the delivered coverage does not yet meet the rule's own bar for what "the
      boring near-certainties reliability diagrams need at the extremes" requires — a floor not
      yet held, not a floor rejected.
    - `yes` — a non-empty set that spans every declared bin. Decision ticket 21 Q3's own
      reasoning then applies as resolved: a low marginal cost (three already-built components
      layered on machinery that must exist anyway) against a value that is disproportionate to a
      thin coverage slice precisely because it is the one contamination-proof mechanism the
      project has.

    `resolved` is a list of already-scored resolution artefact bodies (`score_resolution`'s own
    output), never fabricated — this suite reaches no live venue (`twin/market_signals.py`'s own
    admission), so an empty list here states the cadence has not been measured yet rather than
    inventing one.
    """
    total_capabilities = len(list(caps))
    question_count = len(benchmark.questions)
    spans = benchmark.spans_full_confidence_range()
    resolved_count = len(resolved)

    if resolved_count >= 2:
        opens = sorted(str(r["resolution_window_opens_at"]) for r in resolved)
        cadence = (
            f"{resolved_count} resolution(s) recorded so far, resolution windows opening between "
            f"{opens[0]} and {opens[-1]} — measured, not designed"
        )
    elif resolved_count == 1:
        cadence = "1 resolution recorded so far — too few to state a cadence from"
    else:
        cadence = (
            f"no resolution recorded yet; the pre-registered horizon window "
            f"({rule.min_horizon_days}-{rule.max_horizon_days} days, "
            "twin/benchmark-selection-rule.yaml) is the designed cadence, not yet a measured one"
        )

    if question_count == 0:
        verdict = "no"
        reasoning = (
            "the selected benchmark set is empty — there is no coverage here to weigh a cost "
            "against, so building this at this coverage is not worth it: there is no coverage."
        )
    elif not spans:
        verdict = "conditional"
        reasoning = (
            f"{question_count} question(s) selected, but the set does not span every declared "
            f"confidence bin ({dict(benchmark.distribution)}) — the rule's own bar for 'the "
            "boring near-certainties reliability diagrams need at the extremes' (decision ticket "
            "21 Q2) is not yet met. The marginal cost stays low regardless (build tickets 57-59 "
            "are already built), but the coverage this verdict would be proportionate to has not "
            "yet been delivered."
        )
    else:
        verdict = "yes"
        reasoning = (
            f"{question_count} question(s) selected, spanning every declared confidence bin "
            f"({dict(benchmark.distribution)}) — forecast-book is 1 of {total_capabilities} "
            "capabilities this project declares, so this coverage is a genuinely thin slice, and "
            "it is worth building anyway: the marginal cost is low "
            f"({MARGINAL_COST}) and the value is disproportionate to the coverage "
            f"({DISPROPORTIONATE_VALUE})."
        )

    return Artefact(
        kind=KIND_PROPORTIONALITY_VERDICT,
        mark=DERIVED,
        command=command,
        pins={
            "rule": {"version": rule.version, "digest": rule.digest()},
            "benchmark": {"rule_version": benchmark.rule_version, "ids_digest": digest_of(sorted(benchmark.ids))},
            "tool": {"capabilities_digest": caps.digest},
        },
        depth=caps.depth_block(CAPS_BENCHMARK),
        body={
            "question_count": question_count,
            "spans_full_confidence_range": spans,
            "confidence_distribution": dict(benchmark.distribution),
            "capability_share": f"1 of {total_capabilities} capabilities this project declares",
            "resolution_cadence": cadence,
            "marginal_cost": MARGINAL_COST,
            "disproportionate_value": DISPROPORTIONATE_VALUE,
            "verdict": verdict,
            "reasoning": reasoning,
            "claim_scope": CLAIM_SCOPE,
        },
    )
