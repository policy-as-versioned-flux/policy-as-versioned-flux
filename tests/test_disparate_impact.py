"""The disparate-impact audit channel (build ticket 61)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin.cli import main
from twin.disparate_impact import (
    KIND_AUDIT,
    KIND_RESPONSE,
    OPEN,
    RESPONDENT_ROLE,
    DisparateImpactError,
    raise_audit,
    respond,
)

FINDING = "Cohort A receives systematically wider trade-off ranges than cohort B across the last quarter's scenarios."
SOURCE = "Independent audit, Doe & Partners, 2026-08-01, methodology in appendix C."


# -- raising an audit --------------------------------------------------------------------------


def test_raising_an_audit_captures_the_finding_open() -> None:
    artefact = raise_audit(FINDING, SOURCE, ["twin", "disparate-impact-audit"])
    assert artefact.kind == KIND_AUDIT
    assert artefact.mark == "authored"
    assert artefact.body == {"finding": FINDING, "source": SOURCE, "status": OPEN}
    assert artefact.depth["grade"] is None


def test_an_audit_with_no_finding_is_refused() -> None:
    with pytest.raises(DisparateImpactError, match="no finding"):
        raise_audit("   ", SOURCE, ["twin", "disparate-impact-audit"])


def test_an_audit_with_no_source_is_refused() -> None:
    """This system cannot measure disparate impact itself; a finding with nothing measured
    outside it is not falsifiable."""
    with pytest.raises(DisparateImpactError, match="cannot represent"):
        raise_audit(FINDING, "  ", ["twin", "disparate-impact-audit"])


def test_an_audit_naming_a_protected_characteristic_is_sealed_out() -> None:
    """The channel is sealed to the same refusal the model repository itself carries — an
    auditor may report what differs, never the protected ground that produced it."""
    with pytest.raises(DisparateImpactError, match="sealed"):
        raise_audit("disparity by race across cohorts", SOURCE, ["twin", "disparate-impact-audit"])


def test_an_audit_naming_a_protected_characteristic_via_the_source_field_is_also_sealed() -> None:
    with pytest.raises(DisparateImpactError, match="sealed"):
        raise_audit(FINDING, "measured against ethnicity records", ["twin", "disparate-impact-audit"])


# -- responding: the one defined role ------------------------------------------------------------


@pytest.fixture()
def audit_doc() -> dict:
    artefact = raise_audit(FINDING, SOURCE, ["twin", "disparate-impact-audit"])
    return json.loads(artefact.to_bytes())


def test_responding_names_only_what_the_audit_named(audit_doc: dict) -> None:
    artefact = respond(
        audit_doc, "sha-of-the-audit", "we are investigating and will report back",
        RESPONDENT_ROLE, ["twin", "disparate-impact-respond"],
    )
    assert artefact.kind == KIND_RESPONSE
    assert artefact.body["finding"] == FINDING
    assert artefact.body["audit_sha256"] == "sha-of-the-audit"
    assert artefact.body["responded_by_role"] == RESPONDENT_ROLE


def test_a_response_with_no_text_is_refused(audit_doc: dict) -> None:
    with pytest.raises(DisparateImpactError, match="answers nothing"):
        respond(audit_doc, "sha", "   ", RESPONDENT_ROLE, ["twin", "disparate-impact-respond"])


def test_a_response_from_a_role_that_is_not_the_defined_respondent_is_refused(audit_doc: dict) -> None:
    """A registered role — just not the one this channel is answerable to."""
    with pytest.raises(DisparateImpactError, match="defined respondent"):
        respond(audit_doc, "sha", "investigating", "model-steward", ["twin", "disparate-impact-respond"])


def test_respond_refuses_a_doc_that_is_not_an_audit() -> None:
    not_an_audit = {"envelope": {"kind": "graph"}, "body": {}}
    with pytest.raises(DisparateImpactError, match="is not a"):
        respond(not_an_audit, "sha", "text", RESPONDENT_ROLE, ["twin", "disparate-impact-respond"])


# -- CLI -----------------------------------------------------------------------------------------


def test_cli_raises_an_audit(tmp_path: Path) -> None:
    out = tmp_path / "audit.json"
    rc = main([
        "disparate-impact-audit", "--finding", FINDING, "--source", SOURCE, "--out", str(out),
    ])
    assert rc == 0
    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == KIND_AUDIT
    assert doc["body"]["status"] == OPEN


def test_cli_refuses_a_sealed_finding(tmp_path: Path) -> None:
    out = tmp_path / "audit.json"
    rc = main([
        "disparate-impact-audit", "--finding", "disparity by ethnicity", "--source", SOURCE, "--out", str(out),
    ])
    assert rc == 2
    assert not out.exists()


def test_cli_respond_refuses_the_wrong_role(tmp_path: Path) -> None:
    audit_out = tmp_path / "audit.json"
    assert main([
        "disparate-impact-audit", "--finding", FINDING, "--source", SOURCE, "--out", str(audit_out),
    ]) == 0

    resp_out = tmp_path / "resp.json"
    rc = main([
        "disparate-impact-respond", "--audit", str(audit_out), "--response", "investigating",
        "--role", "model-steward", "--out", str(resp_out),
    ])
    assert rc == 2
    assert not resp_out.exists()


def test_cli_respond_as_the_defined_role_and_signs_when_a_key_is_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TWIN_SIGNING_KEY", "test-key")
    audit_out = tmp_path / "audit.json"
    assert main([
        "disparate-impact-audit", "--finding", FINDING, "--source", SOURCE, "--out", str(audit_out),
    ]) == 0

    resp_out = tmp_path / "resp.json"
    rc = main([
        "disparate-impact-respond", "--audit", str(audit_out), "--response", "investigating",
        "--role", RESPONDENT_ROLE, "--out", str(resp_out),
    ])
    assert rc == 0
    doc = json.loads(resp_out.read_bytes())
    assert doc["envelope"]["kind"] == KIND_RESPONSE
    assert doc["body"]["responded_by_role"] == RESPONDENT_ROLE

    from twin import attest

    sidecar = attest.load(attest.sidecar_for(resp_out))
    assert attest.human_signed(sidecar)
