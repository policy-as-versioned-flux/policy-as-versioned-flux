"""Benchmark question selection and ingestion quarantine (build ticket 57).

Assertions are on the emitted artefacts' bodies and on the module's typed functions, not on
internals — `twin/benchmark.py` is as disposable as the rest of this system.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import benchmark as bm
from twin.artefact import DERIVED
from twin.grades import Capabilities

COMMAND_SELECT = ["twin", "benchmark-select"]
COMMAND_AUDIT = ["twin", "benchmark-audit"]


def _rule(**overrides: object) -> bm.SelectionRule:
    base: dict[str, object] = {
        "version": "test-1",
        "min_liquidity": 1000.0,
        "min_horizon_days": 1,
        "max_horizon_days": 30,
        "categories": ("macro", "technology"),
        "confidence_bins": ((0.0, 0.5), (0.5, 1.0)),
        "max_questions": 10,
        "sample_seed": 7,
    }
    return bm.SelectionRule(**{**base, **overrides})  # type: ignore[arg-type]


def _question(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "q-1",
        "category": "macro",
        "liquidity": 5000.0,
        "horizon_days": 10,
        "implied_probability": 0.2,
    }
    return {**base, **overrides}


# -- the committed rule loads and is versioned, resolvable in its own right ---------------------


def test_the_committed_rule_loads_and_is_versioned() -> None:
    rule = bm.SelectionRule.load()
    assert rule.version
    assert rule.max_questions > 0
    assert len(rule.confidence_bins) >= 2  # more than one bin, or "spans the range" is vacuous


def test_a_rule_missing_a_required_key_refuses(tmp_path: Path) -> None:
    bad = tmp_path / "bad-rule.yaml"
    bad.write_text("version: '1'\nmin_liquidity: 1.0\n", encoding="utf-8")
    with pytest.raises(bm.BenchmarkError, match="missing required key"):
        bm.SelectionRule.load(bad)


# -- eligibility is resolvable-terms only: liquidity, horizon, category -------------------------


def test_eligible_requires_liquidity_horizon_and_category_all_at_once() -> None:
    rule = _rule()
    assert bm.eligible(rule, _question())
    assert not bm.eligible(rule, _question(liquidity=1.0))
    assert not bm.eligible(rule, _question(horizon_days=999))
    assert not bm.eligible(rule, _question(category="sports"))


# -- selection is mechanical and reproducible ----------------------------------------------------


def test_select_questions_is_reproducible_against_the_identical_pool() -> None:
    rule = _rule()
    pool = [_question(id=f"q-{i}", implied_probability=0.1 * i) for i in range(1, 9)]
    first = bm.select_questions(rule, pool)
    second = bm.select_questions(rule, pool)
    assert first == second


def test_select_questions_sorts_by_id_not_arrival_order() -> None:
    rule = _rule()
    pool = [_question(id="q-z"), _question(id="q-a"), _question(id="q-m")]
    selected = bm.select_questions(rule, pool)
    assert [q["id"] for q in selected.questions] == ["q-a", "q-m", "q-z"]


def test_select_questions_refuses_an_empty_pool() -> None:
    with pytest.raises(bm.BenchmarkError, match="empty"):
        bm.select_questions(_rule(), [])


def test_select_questions_refuses_when_nothing_in_the_pool_is_eligible() -> None:
    rule = _rule()
    pool = [_question(category="sports")]
    with pytest.raises(bm.BenchmarkError, match="no question"):
        bm.select_questions(rule, pool)


def test_the_volume_valve_is_a_deterministic_seeded_sample_not_an_ad_hoc_cut() -> None:
    """Decision ticket 21 Q2's "(c) random sampling ... if the rule selects too many" — applies
    only past max_questions, draws via the rule's own committed seed rather than truncating the
    sorted candidates, and the identical seed against the identical pool always draws the
    identical subset."""
    rule = _rule(max_questions=3)
    pool = [_question(id=f"q-{i:02d}", implied_probability=0.05 * i) for i in range(20)]
    first = bm.select_questions(rule, pool)
    second = bm.select_questions(rule, pool)
    assert len(first.questions) == 3
    assert first == second

    naive_first_three = sorted(str(q["id"]) for q in pool)[:3]
    assert sorted(str(q["id"]) for q in first.questions) != naive_first_three  # real sampling, not truncation

    other_seed = bm.select_questions(_rule(max_questions=3, sample_seed=999), pool)
    assert {q["id"] for q in other_seed.questions} != {q["id"] for q in first.questions}


# -- the distribution demonstrates the full confidence range, rather than claiming it ------------


def test_confidence_distribution_counts_every_declared_bin_including_empty_ones() -> None:
    rule = _rule(confidence_bins=((0.0, 0.3), (0.3, 0.6), (0.6, 1.0)))
    pool = [_question(id="q-1", implied_probability=0.1)]
    selected = bm.select_questions(rule, pool)
    assert selected.distribution == {"0-0.3": 1, "0.3-0.6": 0, "0.6-1": 0}
    assert not selected.spans_full_confidence_range()


def test_a_set_covering_every_bin_spans_the_full_confidence_range() -> None:
    rule = _rule(confidence_bins=((0.0, 0.5), (0.5, 1.0)))
    pool = [_question(id="q-lo", implied_probability=0.1), _question(id="q-hi", implied_probability=0.9)]
    selected = bm.select_questions(rule, pool)
    assert selected.spans_full_confidence_range()


def test_the_top_bin_is_closed_and_admits_a_probability_of_exactly_one() -> None:
    rule = _rule(confidence_bins=((0.0, 0.5), (0.5, 1.0)))
    pool = [_question(id="q-certain", implied_probability=1.0)]
    selected = bm.select_questions(rule, pool)
    assert selected.distribution["0.5-1"] == 1


# -- the selection, as a derived artefact ---------------------------------------------------------


def test_benchmark_set_artefact_is_derived_and_carries_a_computed_partial_grade(caps: Capabilities) -> None:
    rule = _rule()
    pool = [_question(id=f"q-{i}", implied_probability=0.1 * i) for i in range(1, 9)]
    artefact = bm.benchmark_set_artefact(caps, rule, pool, COMMAND_SELECT)
    assert artefact.mark == DERIVED
    assert artefact.kind == bm.KIND_BENCHMARK_SET
    artefact.digest()  # does not raise: no forbidden key crept into the body

    computed = caps.require("forecast-book")
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] == computed.grade
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] != "full"  # honestly partial


def test_benchmark_set_artefact_pins_the_rule_version_and_digest(caps: Capabilities) -> None:
    rule = _rule()
    pool = [_question(id=f"q-{i}", implied_probability=0.1 * i) for i in range(1, 9)]
    artefact = bm.benchmark_set_artefact(caps, rule, pool, COMMAND_SELECT)
    assert artefact.pins["rule"]["version"] == rule.version
    assert artefact.pins["rule"]["digest"] == rule.digest()


# -- the quarantine audit: a scan over ingestion provenance, not a single named field ------------


def test_audit_quarantine_refuses_an_empty_benchmark() -> None:
    empty = bm.BenchmarkSet(rule_version="1", rule_digest="d", questions=(), distribution={})
    with pytest.raises(bm.BenchmarkError, match="empty"):
        bm.audit_quarantine(empty, [])


def test_audit_quarantine_reports_clean_against_unrelated_records() -> None:
    rule = _rule()
    pool = [_question(id="quarantined-q-1", implied_probability=0.2)]
    benchmark = bm.select_questions(rule, pool)
    records = [("run-1", {"provenance": {"recipe": "unrelated-recipe", "index": 0}})]
    assert bm.audit_quarantine(benchmark, records) == []


def test_a_planted_quarantine_breach_nested_in_provenance_is_detected() -> None:
    rule = _rule()
    pool = [_question(id="quarantined-q-1", implied_probability=0.2)]
    benchmark = bm.select_questions(rule, pool)
    records = [
        ("run-clean", {"provenance": {"recipe": "unrelated-recipe", "index": 0}}),
        # planted: the quarantined id shows up nested inside a recipe id, not in a field named
        # for the purpose — this is the "in any form" leg.
        ("run-breached", {"provenance": {"recipe": "derived-from-quarantined-q-1", "index": 1}}),
    ]
    breaches = bm.audit_quarantine(benchmark, records)
    assert len(breaches) == 1
    assert breaches[0].question_id == "quarantined-q-1"
    assert breaches[0].where == "run-breached"


def test_the_quarantine_holds_regardless_of_which_record_is_checked_first_or_last() -> None:
    """"At any lag" — nothing in the audit reads a timestamp, so an old record and a much later
    one are scanned identically; a breach buried anywhere in the sequence is still caught."""
    rule = _rule()
    pool = [_question(id="quarantined-q-1", implied_probability=0.2)]
    benchmark = bm.select_questions(rule, pool)
    old = ("run-old", {"provenance": {"recipe": "derived-from-quarantined-q-1", "index": 0}})
    clean = [("run-clean", {"provenance": {"recipe": "unrelated", "index": i}}) for i in range(5)]

    breaches_first = bm.audit_quarantine(benchmark, [old, *clean])
    breaches_last = bm.audit_quarantine(benchmark, [*clean, old])
    assert len(breaches_first) == 1
    assert len(breaches_last) == 1
    assert breaches_first[0].question_id == breaches_last[0].question_id == "quarantined-q-1"


def test_quarantine_audit_artefact_reports_clean_and_breached_states(caps: Capabilities) -> None:
    rule = _rule()
    pool = [_question(id="quarantined-q-1", implied_probability=0.2)]
    benchmark = bm.select_questions(rule, pool)

    clean_artefact = bm.quarantine_audit_artefact(
        caps, benchmark, [("run-1", {"provenance": {"recipe": "unrelated"}})], COMMAND_AUDIT
    )
    assert clean_artefact.mark == DERIVED
    assert clean_artefact.body["clean"] is True
    assert clean_artefact.body["breaches"] == []
    clean_artefact.digest()

    breached_artefact = bm.quarantine_audit_artefact(
        caps,
        benchmark,
        [("run-1", {"provenance": {"recipe": "derived-from-quarantined-q-1"}})],
        COMMAND_AUDIT,
    )
    assert breached_artefact.body["clean"] is False
    assert len(breached_artefact.body["breaches"]) == 1
    breached_artefact.digest()


def test_quarantine_audit_artefact_declares_the_same_computed_capability(caps: Capabilities) -> None:
    rule = _rule()
    pool = [_question(id="quarantined-q-1", implied_probability=0.2)]
    benchmark = bm.select_questions(rule, pool)
    artefact = bm.quarantine_audit_artefact(caps, benchmark, [], COMMAND_AUDIT)
    computed = caps.require("forecast-book")
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] == computed.grade
