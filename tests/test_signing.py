"""Signing: accountability, origin, and the derived-artefact anomaly (build ticket 11).

The asymmetry under test: a human signature asserts accountability for a judgement, an agent
signature asserts reproducible origin and nothing else, and the two never substitute for each
other. Because a derived artefact may carry only the second, a human signature on one is a
**detectable anomaly** rather than a breach of convention.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import attest, sign
from twin.artefact import AUTHORED, DERIVED, Artefact
from twin.attest import AttestationError
from twin.canon import sha256_hex

KEY = b"a-test-key"
SUBJECT = sha256_hex(b"some artefact bytes")


def _artefact(mark: str = DERIVED) -> Artefact:
    return Artefact(kind="probe", mark=mark, command=["twin", "run"], pins={}, depth={}, body={"a": 1})


# -- the two types --------------------------------------------------------------------------


def test_a_human_signature_asserts_accountability_and_an_agent_one_asserts_origin() -> None:
    human = sign.human("model-steward", SUBJECT, KEY)
    agent = sign.agent(SUBJECT, {"python": "3.12"}, KEY)

    assert human["asserts"] == sign.ASSERTS[sign.HUMAN]
    assert agent["asserts"] == sign.ASSERTS[sign.AGENT]
    assert "correctness" in agent["asserts_nothing_about"]
    assert "accountability" in agent["asserts_nothing_about"]
    assert "role" not in agent, "an agent has no role to be accountable in"


@pytest.mark.parametrize("presented_as", [sign.HUMAN, sign.AGENT])
def test_the_two_signature_types_are_not_interchangeable(presented_as: str) -> None:
    """Refused as a type error even though the value itself verifies."""
    wrong = sign.agent(SUBJECT, {}, KEY) if presented_as == sign.HUMAN else sign.human("model-steward", SUBJECT, KEY)
    with pytest.raises(sign.SignatureError, match="not interchangeable"):
        sign.verify(wrong, presented_as, SUBJECT, KEY)


def test_a_signature_verifies_only_over_the_artefact_it_names() -> None:
    signature = sign.human("model-steward", SUBJECT, KEY)
    sign.verify(signature, sign.HUMAN, SUBJECT, KEY)

    with pytest.raises(sign.SignatureError, match="not over this artefact"):
        sign.verify(signature, sign.HUMAN, sha256_hex(b"different bytes"), KEY)
    with pytest.raises(sign.SignatureError, match="does not verify"):
        sign.verify({**signature, "role": "worksheet-author"}, sign.HUMAN, SUBJECT, KEY)
    with pytest.raises(sign.SignatureError, match="does not verify"):
        sign.verify(signature, sign.HUMAN, SUBJECT, b"another key")


# -- roles, not people ----------------------------------------------------------------------


def test_a_signature_binds_to_a_role_the_register_carries() -> None:
    assert "model-steward" in sign.role_ids()
    with pytest.raises(sign.SignatureError, match="not in the register"):
        sign.human("chief-of-everything", SUBJECT, KEY)


@pytest.mark.parametrize("field", sign.PERSONAL_FIELDS)
def test_a_signature_naming_an_individual_is_refused(field: str) -> None:
    """Accountability attaches without creating a personal target."""
    signature = {**sign.human("model-steward", SUBJECT, KEY), field: "someone@example.invalid"}
    with pytest.raises(sign.SignatureError, match="bind to roles"):
        sign.verify(signature, sign.HUMAN, SUBJECT, KEY)
    with pytest.raises(AttestationError, match="bind to roles"):
        attest.build(_artefact(AUTHORED), [signature], material=KEY)


def test_the_role_register_is_versioned_and_pinned_into_the_signature() -> None:
    pin = sign.human("model-steward", SUBJECT, KEY)["role_register"]
    assert pin == sign.register_pin()
    assert pin["version"] == sign.roles()["version"]
    assert len(pin["digest"]) == 64, "the exact register content, not just its version"


# -- the anomaly ----------------------------------------------------------------------------


def test_a_derived_artefact_refuses_a_human_signature_at_emission() -> None:
    with pytest.raises(AttestationError, match="derived_never_human_signed"):
        attest.build(_artefact(), [sign.human("model-steward", SUBJECT, KEY)], material=KEY)


def test_a_planted_human_signature_on_a_derived_sidecar_is_detected_on_read() -> None:
    artefact = _artefact()
    doc = attest.build(artefact, material=KEY)
    assert attest.check(doc, artefact.to_bytes(), KEY) == []

    tampered = {**doc, "human_involvement": {"present": True, "signatures": [
        sign.human("model-steward", artefact.digest(), KEY)
    ]}}
    problems = attest.check(tampered, artefact.to_bytes(), KEY)
    assert any("derived_never_human_signed" in p for p in problems)


def test_an_edited_artefact_no_longer_matches_its_sidecar() -> None:
    artefact = _artefact()
    doc = attest.build(artefact, material=KEY)
    problems = attest.check(doc, artefact.to_bytes() + b"\n", KEY)
    assert any("has been edited since" in p for p in problems)


def test_an_authored_artefact_without_a_signature_has_nobody_accountable() -> None:
    artefact = _artefact(AUTHORED)
    problems = attest.check(attest.build(artefact, material=KEY), artefact.to_bytes(), KEY)
    assert any("nobody is accountable" in p for p in problems)

    signed = attest.build(artefact, [sign.human("worksheet-author", artefact.digest(), KEY)], material=KEY)
    assert attest.check(signed, artefact.to_bytes(), KEY) == []


def test_an_agent_signature_may_not_be_passed_off_as_a_human_one() -> None:
    agent = sign.agent(SUBJECT, {"python": "3.12"}, KEY)
    with pytest.raises(AttestationError, match="never carries accountability"):
        attest.build(_artefact(AUTHORED), [agent], material=KEY)


def test_an_untyped_signature_counts_as_human() -> None:
    """The refusal is the default: deleting the type field must not be a way past the check."""
    assert sign.is_human({"asserts": "something"}) is True
    with pytest.raises(AttestationError, match="derived_never_human_signed"):
        attest.build(_artefact(), [{"asserts": "something"}], material=KEY)


# -- the sidecar is read back ---------------------------------------------------------------


def test_with_no_key_nothing_is_signed_and_the_sidecar_says_so(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(sign.KEY_ENV, raising=False)
    artefact = _artefact()
    path = artefact.write(tmp_path / "probe.json")
    sidecar = attest.write(artefact, path)

    doc = json.loads(sidecar.read_bytes())
    assert doc["agent_signature"] is None
    assert sign.KEY_ENV in doc["signature_status"], "a placeholder that reads as signed would be worse"
    assert attest.check(doc, path.read_bytes(), None) == []


def test_the_signature_never_enters_the_artefact_itself(tmp_path: Path, monkeypatch) -> None:
    """A keyed value in the envelope would break identical bytes on the first machine with a
    different key."""
    unsigned = _artefact().to_bytes()
    monkeypatch.setenv(sign.KEY_ENV, "a-key")
    assert _artefact().to_bytes() == unsigned
    assert attest.build(_artefact())["agent_signature"] is not None
