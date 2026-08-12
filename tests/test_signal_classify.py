"""`signal-classify` (build ticket 43): STEEP-tag a signal and bind it to the components it
touches — the first of the six skills seam 3 (build ticket 42) exists to evaluate.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from twin.schema import SCHEMAS, STEEP
from twin.signal_classify import SKILL, SignalClassifyError, classify, labelled_corpus, scorer
from twin.skills import evaluate, threshold_for


@pytest.fixture(scope="session")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    return labelled_corpus(tmp_path_factory.mktemp("signal-classify-corpus"))


def test_classify_produces_a_grade_5_claim_shaped_dict() -> None:
    result = classify(
        {
            "statement": "A dated event about this business.",
            "source": "Press coverage",
            "candidates": [{"id": "some-component", "name": "Some business"}],
        }
    )
    assert result["steep"] in STEEP
    claim = result["claim"]
    assert claim["kind"] == "binding"
    assert claim["component"] == "some-component"
    assert claim["evidence_grade"] == 5
    assert SKILL in claim["claimed_by"]
    assert claim["evidence"]


def test_the_claim_half_conforms_to_the_claim_schema_once_id_and_signal_are_added() -> None:
    """`classify()` cannot know a signal's own id — only the caller committing it does — so the
    claim half is genuinely `schema.SCHEMAS["claim"]`-shaped only once those two are added."""
    result = classify(
        {
            "statement": "A dated event.",
            "source": "Press coverage",
            "candidates": [{"id": "some-component", "name": "Some business"}],
        }
    )
    doc = {**result["claim"], "id": "bind-signal-x", "signal": "signal-x"}
    SCHEMAS["claim"].validate(doc, "test")  # raises SchemaError if the shape is wrong


def test_classify_has_no_parameter_that_can_set_a_different_grade() -> None:
    """Grade 5 is not a default that a caller can override — it is not a parameter at all."""
    params = inspect.signature(classify).parameters
    assert "grade" not in params
    assert "evidence_grade" not in params
    assert list(params) == ["payload"]


def test_classify_refuses_a_payload_missing_a_field() -> None:
    with pytest.raises(SignalClassifyError, match="declares no"):
        classify({"statement": "x", "source": "y"})


def test_classify_refuses_an_empty_candidate_list() -> None:
    with pytest.raises(SignalClassifyError, match="no candidate components"):
        classify({"statement": "x", "source": "y", "candidates": []})


def test_classify_binds_to_the_only_candidate_when_there_is_one() -> None:
    result = classify(
        {
            "statement": "Anything at all.",
            "source": "Anything",
            "candidates": [{"id": "only-one", "name": "The only component"}],
        }
    )
    assert result["claim"]["component"] == "only-one"


def test_classify_discriminates_between_multiple_candidates_by_word_overlap() -> None:
    """A real Carillion statement against two real candidates — Carillion's own and Enron's,
    which share no vocabulary with it — proves binding is a genuine choice, not a rubber stamp
    that only ever happens to see one option."""
    result = classify(
        {
            "statement": (
                "A trading update on financial performance generally and the UK construction "
                "business specifically."
            ),
            "source": "Carillion plc RNS announcement, 2016-12-07",
            "candidates": [
                {"id": "energy-trading-book", "name": "The subject's energy-trading and mark-to-market business"},
                {"id": "carillion-uk-construction", "name": "Carillion's UK construction and support-services business"},
            ],
        }
    )
    assert result["claim"]["component"] == "carillion-uk-construction"


def test_classify_tags_a_compulsory_liquidation_as_political() -> None:
    result = classify(
        {
            "statement": "A compulsory liquidation order is made against the subject plc.",
            "source": "High Court compulsory liquidation order, 2018-01-15",
            "candidates": [{"id": "c", "name": "n"}],
        }
    )
    assert result["steep"] == "political"


def test_classify_tags_a_bafin_short_selling_ban_as_political() -> None:
    result = classify(
        {
            "statement": "A regulator bans net short positions in the subject's shares.",
            "source": "BaFin General Administrative Act, 2019-02-18",
            "candidates": [{"id": "c", "name": "n"}],
        }
    )
    assert result["steep"] == "political"


def test_classify_tags_an_ordinary_trading_update_as_economic() -> None:
    result = classify(
        {
            "statement": "A profit warning: contract write-downs, the chief executive resigns.",
            "source": "Company trading update, 2017-07-10",
            "candidates": [{"id": "c", "name": "n"}],
        }
    )
    assert result["steep"] == "economic"


# -- the labelled corpus ----------------------------------------------------------------------


def test_the_labelled_corpus_pools_all_four_backtest_keys(corpus: list[dict]) -> None:
    assert len(corpus) == 8 + 5 + 6 + 4  # carillion, nmc, wirecard, enron
    orgs = {item["id"].split(":", 1)[0] for item in corpus}
    assert orgs == {"carillion", "nmc", "wirecard", "enron"}


def test_every_corpus_item_carries_the_fields_evaluate_requires(corpus: list[dict]) -> None:
    for item in corpus:
        assert {"id", "input", "expected"} <= item.keys()
        assert {"statement", "source", "candidates"} <= item["input"].keys()
        assert {"steep", "component"} <= item["expected"].keys()


def test_signal_classify_passes_its_own_labelled_corpus(corpus: list[dict]) -> None:
    result = evaluate(SKILL, classify, corpus, scorer=scorer)
    assert result.passed, f"scored {result.score}, threshold {result.threshold}: {result.as_dict()}"
    assert result.threshold == threshold_for(SKILL)


def test_a_degraded_classifier_fails_the_threshold(corpus: list[dict]) -> None:
    def always_wrong(payload: dict) -> dict:
        return {"steep": "environmental", "claim": {"component": "not-a-real-component"}}

    result = evaluate(SKILL, always_wrong, corpus, scorer=scorer)
    assert result.score == 0.0
    assert not result.passed
