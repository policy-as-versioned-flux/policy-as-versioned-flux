"""Prediction-market price MOVES as world-layer signals, never price LEVELS as probabilities
(build ticket 59).

Assertions are on the emitted `market-signal-run` artefact's body and on the module's typed
functions, not on internals — `twin/market_signals.py` is as disposable as the rest of this
system.
"""

from __future__ import annotations

import inspect

import pytest

from twin import market_signals as ms
from twin.artefact import DERIVED
from twin.grades import Capabilities
from twin.repo import ModelRepo

COMMAND = ["twin", "market-signal-run"]


def _obs(**overrides: object) -> ms.PriceObservation:
    base: dict[str, object] = {
        "question_id": "cyberattack-iran-june",
        "venue": "kalshi",
        "date": "2026-06-01",
        "price_level": 0.08,
    }
    return ms.PriceObservation(**{**base, **overrides})  # type: ignore[arg-type]


# -- PriceObservation: a level in [0,1], nothing more -------------------------------------------


def test_price_observation_refuses_a_level_outside_zero_one() -> None:
    with pytest.raises(ms.MarketSignalError, match=r"\[0,1\]"):
        _obs(price_level=1.4)
    with pytest.raises(ms.MarketSignalError, match=r"\[0,1\]"):
        _obs(price_level=-0.1)


def test_price_observation_admits_the_closed_boundary() -> None:
    _obs(price_level=0.0)
    _obs(price_level=1.0)


# -- price_moves: the derivative, never a level in isolation -------------------------------------


def test_price_moves_pairs_consecutive_dated_observations_of_the_same_question() -> None:
    observations = [
        _obs(question_id="q-1", date="2026-06-01", price_level=0.08),
        _obs(question_id="q-1", date="2026-06-08", price_level=0.19),
        _obs(question_id="q-1", date="2026-06-15", price_level=0.31),
    ]
    moves = ms.price_moves(observations)
    assert len(moves) == 2
    assert (moves[0].from_date, moves[0].to_date) == ("2026-06-01", "2026-06-08")
    assert (moves[0].from_level, moves[0].to_level) == (0.08, 0.19)
    assert (moves[1].from_date, moves[1].to_date) == ("2026-06-08", "2026-06-15")


def test_price_moves_sorts_by_date_regardless_of_arrival_order() -> None:
    observations = [
        _obs(question_id="q-1", date="2026-06-15", price_level=0.31),
        _obs(question_id="q-1", date="2026-06-01", price_level=0.08),
        _obs(question_id="q-1", date="2026-06-08", price_level=0.19),
    ]
    moves = ms.price_moves(observations)
    assert [m.to_date for m in moves] == ["2026-06-08", "2026-06-15"]


def test_price_moves_produces_nothing_for_a_single_observation() -> None:
    """No move to derive: research 17 S4's value is the derivative, not the point — a lone
    observation is correctly silent, not an error."""
    assert ms.price_moves([_obs(question_id="q-1")]) == []


def test_price_moves_keeps_questions_independent() -> None:
    observations = [
        _obs(question_id="q-1", date="2026-06-01", price_level=0.10),
        _obs(question_id="q-1", date="2026-06-08", price_level=0.20),
        _obs(question_id="q-2", date="2026-06-01", price_level=0.60),
        _obs(question_id="q-2", date="2026-06-08", price_level=0.55),
    ]
    moves = ms.price_moves(observations)
    assert {m.question_id for m in moves} == {"q-1", "q-2"}
    assert len(moves) == 2


def test_price_move_direction_and_delta() -> None:
    up = ms.PriceMove("q", "kalshi", "2026-06-01", "2026-06-08", 0.10, 0.30)
    down = ms.PriceMove("q", "kalshi", "2026-06-01", "2026-06-08", 0.30, 0.10)
    flat = ms.PriceMove("q", "kalshi", "2026-06-01", "2026-06-08", 0.30, 0.30)
    assert up.direction == "up" and up.delta == pytest.approx(0.20)
    assert down.direction == "down" and down.delta == pytest.approx(-0.20)
    assert flat.direction == "flat" and flat.delta == 0.0


def test_no_price_move_field_is_shaped_like_a_probability() -> None:
    move = ms.PriceMove("q", "kalshi", "2026-06-01", "2026-06-08", 0.10, 0.30)
    fields = {f for f in vars(move)}
    assert "probability" not in fields
    assert "implied_probability" not in fields
    assert "belief" not in fields


# -- as_probability: refused, always, by construction --------------------------------------------


def test_as_probability_always_refuses() -> None:
    for level in (0.01, 0.1, 0.5, 0.9, 0.99):
        with pytest.raises(ms.PriceLevelAsProbabilityError, match="price_levels_never_probabilities"):
            ms.as_probability(_obs(price_level=level))


def test_as_probability_cites_the_bias_evidence_in_its_refusal() -> None:
    with pytest.raises(ms.PriceLevelAsProbabilityError, match="favourite-longshot"):
        ms.as_probability(_obs())


def test_as_probability_fails_outright_rather_than_warning() -> None:
    """The acceptance criterion is 'fails rather than warns' — checked at the source: no warning
    machinery anywhere in the function, only a raise."""
    source = inspect.getsource(ms.as_probability)
    for banned in ("warnings.warn(", ".warning(", "logging.warn(", "print("):
        assert banned not in source, f"as_probability's own source contains {banned!r}"
    assert "raise" in source


# -- move_statement: the change, never a level dressed as a belief -------------------------------


def test_move_statement_names_venue_question_levels_and_dates() -> None:
    move = ms.PriceMove("cyberattack-iran-june", "kalshi", "2026-06-01", "2026-06-08", 0.08, 0.19)
    statement = ms.move_statement(move)
    assert "kalshi" in statement
    assert "cyberattack-iran-june" in statement
    assert "0.08" in statement and "0.19" in statement
    assert "2026-06-01" in statement and "2026-06-08" in statement
    assert "probability" not in statement.lower()


# -- market_signal_run: the normal sensing path, unattended ---------------------------------------


def _moves() -> list[ms.PriceMove]:
    observations = [
        ms.PriceObservation("cyberattack-iran-june", "kalshi", "2026-06-01", 0.08),
        ms.PriceObservation("cyberattack-iran-june", "kalshi", "2026-06-08", 0.19),
        ms.PriceObservation("cyberattack-iran-june", "polymarket", "2026-06-15", 0.31),
    ]
    return ms.price_moves(observations)


def test_market_signal_run_ingests_moves_through_signal_classify(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)
    assert artefact.kind == ms.KIND_MARKET_SIGNAL_RUN
    assert artefact.mark == DERIVED
    assert len(artefact.body["items"]) + len(artefact.body["failures"]) == len(_moves())
    assert artefact.body["items"]
    artefact.digest()  # does not raise: no forbidden key crept into the body


def test_market_signal_run_refuses_with_no_moves(repo: ModelRepo, caps: Capabilities) -> None:
    with pytest.raises(ms.MarketSignalError, match="no price moves"):
        ms.market_signal_run(repo, caps, "netflix", [], frozenset(), COMMAND)


def test_market_signal_run_refuses_when_the_overlay_has_no_candidate_component(
    repo: ModelRepo, caps: Capabilities, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ms, "candidates_of", lambda overlay: [])
    with pytest.raises(ms.MarketSignalError, match="no component"):
        ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)


def test_every_item_is_provenanced_with_levels_never_a_probability_field(
    repo: ModelRepo, caps: Capabilities
) -> None:
    artefact = ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)
    for row in artefact.body["items"] + artefact.body["failures"]:
        provenance = row["provenance"]
        assert {
            "venue", "question_id", "from_date", "to_date",
            "price_level_from", "price_level_to", "bias_citation", "index",
        } <= provenance.keys()
        assert "probability" not in provenance
        assert "implied_probability" not in provenance


def test_items_stay_grade_5_because_binding_is_trusted_downstream_not_at_entry(
    repo: ModelRepo, caps: Capabilities
) -> None:
    artefact = ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)
    assert artefact.body["items"]
    for item in artefact.body["items"]:
        assert item["claim"]["evidence_grade"] == 5


def test_bias_evidence_is_cited_in_the_artefact_that_consumes_the_signals(
    repo: ModelRepo, caps: Capabilities
) -> None:
    artefact = ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)
    assert artefact.body["bias_evidence"] == ms.BIAS_CITATION
    assert "favourite-longshot" in artefact.body["bias_evidence"]


def test_market_signal_run_has_no_parameter_shaped_like_a_human_gate() -> None:
    params = inspect.signature(ms.market_signal_run).parameters
    for banned in ("review", "reviewed_by", "approve", "approved_by", "confirm", "human"):
        assert banned not in params, f"market_signal_run accepts {banned!r} — a human gate could exist at entry"


def test_market_signal_run_calls_no_confirmation_or_signing_step() -> None:
    source = inspect.getsource(ms.market_signal_run)
    for banned in ("input(", "sign.human", "approve", "confirm"):
        assert banned not in source, f"market_signal_run's own source contains {banned!r}"


# -- decision ticket 21 Q1(b): signal source respects the quarantine, at ingestion ---------------


def test_a_quarantined_question_id_is_excluded_before_classification_ever_runs(
    repo: ModelRepo, caps: Capabilities
) -> None:
    observations = [
        ms.PriceObservation("cyberattack-iran-june", "kalshi", "2026-06-01", 0.08),
        ms.PriceObservation("cyberattack-iran-june", "kalshi", "2026-06-08", 0.19),
        ms.PriceObservation("quarantined-question-1", "kalshi", "2026-06-01", 0.55),
        ms.PriceObservation("quarantined-question-1", "kalshi", "2026-06-10", 0.61),
    ]
    moves = ms.price_moves(observations)
    quarantined = frozenset({"quarantined-question-1"})

    artefact = ms.market_signal_run(repo, caps, "netflix", moves, quarantined, COMMAND)

    ingested_ids = {row["provenance"]["question_id"] for row in artefact.body["items"] + artefact.body["failures"]}
    assert "quarantined-question-1" not in ingested_ids
    assert "cyberattack-iran-june" in ingested_ids

    excluded_ids = {e["question_id"] for e in artefact.body["excluded_quarantined"]}
    assert excluded_ids == {"quarantined-question-1"}


def test_an_empty_quarantine_excludes_nothing(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)
    assert artefact.body["excluded_quarantined"] == []


# -- depth grade: computed against decision ticket 21's checklist, never asserted -----------------


def test_market_signal_run_declares_its_depth_grade_as_the_computed_forecast_book_checklist(
    repo: ModelRepo, caps: Capabilities
) -> None:
    artefact = ms.market_signal_run(repo, caps, "netflix", _moves(), frozenset(), COMMAND)
    computed = caps.require("forecast-book")
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] == computed.grade
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] != "full"  # honestly partial
