"""Blind pinned emission, resolution scoring, and the narrow claim (build ticket 58, decision
ticket 21 Q1(c)/Q4/Q5).

Assertions are on the emitted artefacts' bodies and on the module's typed functions, not on
internals — `twin/forecast_book.py` is as disposable as the rest of this system.
"""

from __future__ import annotations

import inspect

import pytest

from twin import attest, forecast_book as fb, scoring, sign
from twin.artefact import DERIVED
from twin.grades import Capabilities

COMMAND_EMIT = ["twin", "forecast-emit"]
COMMAND_SCORE = ["twin", "forecast-score"]

OPENS = "2026-09-01T00:00:00Z"
BEFORE = "2026-08-01T00:00:00Z"


def _question(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "q-1",
        "category": "macro",
        "resolution_window_opens_at": OPENS,
    }
    return {**base, **overrides}


# -- blind emission is refused structurally, not merely reviewed --------------------------------


def test_emit_refuses_a_probability_outside_the_open_interval(caps: Capabilities) -> None:
    with pytest.raises(fb.ForecastBookError, match="between 0 and 1"):
        fb.emit(caps, _question(), "twin-default", 1.0, BEFORE, COMMAND_EMIT)
    with pytest.raises(fb.ForecastBookError, match="between 0 and 1"):
        fb.emit(caps, _question(), "twin-default", 0.0, BEFORE, COMMAND_EMIT)


def test_emit_refuses_a_malformed_timestamp(caps: Capabilities) -> None:
    with pytest.raises(fb.ForecastBookError, match="not a UTC timestamp"):
        fb.emit(caps, _question(), "twin-default", 0.4, "2026-08-01", COMMAND_EMIT)
    with pytest.raises(fb.ForecastBookError, match="not a UTC timestamp"):
        fb.emit(caps, _question(resolution_window_opens_at="not-a-date"), "twin-default", 0.4, BEFORE, COMMAND_EMIT)


def test_emit_refuses_at_the_resolution_window_boundary_and_past_it(caps: Capabilities) -> None:
    """"Strictly before", not "on or before" — the boundary itself is not blind."""
    with pytest.raises(fb.ForecastBookError, match="not strictly before"):
        fb.emit(caps, _question(), "twin-default", 0.4, OPENS, COMMAND_EMIT)
    with pytest.raises(fb.ForecastBookError, match="not strictly before"):
        fb.emit(caps, _question(), "twin-default", 0.4, "2026-09-02T00:00:00Z", COMMAND_EMIT)


def test_emit_succeeds_strictly_before_the_window_and_records_blindness(caps: Capabilities) -> None:
    artefact = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    assert artefact.mark == DERIVED
    assert artefact.kind == fb.KIND_FORECAST_EMISSION
    assert artefact.body["emitted_at"] == BEFORE
    assert artefact.body["resolution_window_opens_at"] == OPENS
    assert artefact.body["probability"] == 0.35
    artefact.digest()  # does not raise: no forbidden key crept into the body


def test_emit_is_reproducible_against_identical_inputs(caps: Capabilities) -> None:
    first = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    second = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    assert first.to_bytes() == second.to_bytes()


def test_emit_pins_the_question_id_and_digest(caps: Capabilities) -> None:
    question = _question()
    artefact = fb.emit(caps, question, "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    assert artefact.pins["question"]["id"] == "q-1"
    from twin.canon import digest_of

    assert artefact.pins["question"]["digest"] == digest_of(question)
    assert artefact.pins["world_model"] == "twin-default"


def test_emit_carries_a_computed_grade(caps: Capabilities) -> None:
    artefact = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    computed = caps.require("forecast-book")
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] == computed.grade
    # forecast-book closed to full at build ticket 84 (decision ticket 21 AC 6, the
    # proportionality verdict, was the last of its six criteria left unchecked).
    assert artefact.depth["capabilities"]["forecast-book"]["grade"] == "full"


# -- is_blind(): the same check an auditor re-runs against the artefact's own recorded body ------


def test_is_blind_agrees_with_string_comparison_of_fixed_width_utc_timestamps() -> None:
    assert fb.is_blind(BEFORE, OPENS)
    assert not fb.is_blind(OPENS, OPENS)
    assert not fb.is_blind("2026-09-02T00:00:00Z", OPENS)


def test_is_blind_refuses_a_malformed_timestamp() -> None:
    with pytest.raises(fb.ForecastBookError, match="not a UTC timestamp"):
        fb.is_blind("2026-08-01", OPENS)


# -- observe-only is structural: the module cannot place a position ------------------------------


def test_the_module_exposes_no_position_placing_function() -> None:
    """An allow-list, not a keyword filter — the same discipline `prefilter_precedes_pricing` uses
    on `twin/options.py`: a differently-named function that still placed a position would still be
    caught, because the module's entire public surface must equal exactly this set."""
    allowed = {"emit", "score_resolution", "is_blind"}
    public = {
        name
        for name, value in vars(fb).items()
        if not name.startswith("_") and inspect.isfunction(value) and getattr(value, "__module__", "") == fb.__name__
    }
    assert public == allowed

    banned_verbs = ("place", "stake", "bet", "buy", "sell", "trade", "order", "wager", "hedge", "position")
    for name in public:
        assert not any(verb in name.lower() for verb in banned_verbs), name


# -- resolution scoring reuses twin/scoring.py, and is co-registered to the emission -------------


def test_score_resolution_refuses_a_non_emission_artefact(caps: Capabilities) -> None:
    not_an_emission = {"envelope": {"kind": "quarantine-audit", "pins": {}}, "body": {}}
    with pytest.raises(fb.ForecastBookError, match="not a"):
        fb.score_resolution(caps, not_an_emission, "deadbeef", True, COMMAND_SCORE)


def test_score_resolution_calls_scoring_module_not_a_reimplementation() -> None:
    source = inspect.getsource(fb.score_resolution)
    assert "scoring.score(" in source


def test_score_resolution_reproduces_scoring_py_bit_for_bit(caps: Capabilities) -> None:
    emission = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    resolved = fb.score_resolution(caps, emission.envelope(), emission.digest(), True, COMMAND_SCORE)
    expected = scoring.score(0.35, True)
    assert resolved.body["brier"] == expected["brier"]
    assert resolved.body["log_loss"] == expected["log_loss"]
    assert resolved.body["observed"] is True


def test_score_resolution_reads_the_question_and_timestamps_from_the_emission_itself(caps: Capabilities) -> None:
    """Co-registered: nothing about which question or which timestamps is a fresh parameter a
    caller could supply out of step — both travel from the pinned emission, unconditionally."""
    emission = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    resolved = fb.score_resolution(caps, emission.envelope(), emission.digest(), False, COMMAND_SCORE)
    assert resolved.pins["emission"]["question"] == emission.pins["question"]
    assert resolved.body["emitted_at"] == BEFORE
    assert resolved.body["resolution_window_opens_at"] == OPENS


def test_score_resolution_refuses_a_doctored_emission_that_no_longer_attests_blindness(caps: Capabilities) -> None:
    """A defence against a forged or hand-edited emission doc, not only against the honest path
    `emit()` already gates — an auditor may be handed an arbitrary JSON file."""
    emission = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    doctored = emission.envelope()
    doctored["body"] = {**doctored["body"], "emitted_at": "2026-09-15T00:00:00Z"}
    with pytest.raises(fb.ForecastBookError, match="does not attest blindness"):
        fb.score_resolution(caps, doctored, emission.digest(), True, COMMAND_SCORE)


def test_score_resolution_pins_the_emission_sha256(caps: Capabilities) -> None:
    emission = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    resolved = fb.score_resolution(caps, emission.envelope(), emission.digest(), True, COMMAND_SCORE)
    assert resolved.pins["emission"]["sha256"] == emission.digest()
    assert resolved.mark == DERIVED
    resolved.digest()  # does not raise


def test_score_resolution_declares_the_same_computed_capability(caps: Capabilities) -> None:
    emission = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    resolved = fb.score_resolution(caps, emission.envelope(), emission.digest(), True, COMMAND_SCORE)
    computed = caps.require("forecast-book")
    assert resolved.depth["capabilities"]["forecast-book"]["grade"] == computed.grade


# -- the narrow claim scope is published with every result, not asserted only in prose -----------


def test_the_claim_scope_is_published_on_both_the_emission_and_the_resolution_score(caps: Capabilities) -> None:
    emission = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    resolved = fb.score_resolution(caps, emission.envelope(), emission.digest(), True, COMMAND_SCORE)
    for body in (emission.body, resolved.body):
        scope = body["claim_scope"]
        does_not = " ".join(scope["does_not_evidence"]).lower()
        assert "wardley propagation" in does_not
        assert "causal elasticities" in does_not
        assert "£ pricing" in does_not
        assert "org" in does_not
        assert scope["evidences"]


# -- signed and pinned via the existing machinery, reused rather than reinvented -----------------


def test_the_emission_is_signable_and_verifiable_through_the_shared_attest_machinery(caps: Capabilities) -> None:
    artefact = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    material = b"a-test-signing-key"
    doc = attest.build(artefact, human_signatures=None, material=material)
    assert doc["mark"] == DERIVED
    assert doc["agent_signature"] is not None
    problems = attest.check(doc, artefact.to_bytes(), material)
    assert problems == []


def test_a_human_signature_on_an_emission_is_refused(caps: Capabilities) -> None:
    """`derived_never_human_signed`, reused rather than reinvented: an emission is computed from
    its pins, so nobody signs off on it the way an authored artefact is signed."""
    artefact = fb.emit(caps, _question(), "twin-default", 0.35, BEFORE, COMMAND_EMIT)
    material = b"a-test-signing-key"
    fake_human_sig = sign.human("model-steward", artefact.digest(), material)
    with pytest.raises(attest.AttestationError):
        attest.build(artefact, human_signatures=[fake_human_sig], material=material)
