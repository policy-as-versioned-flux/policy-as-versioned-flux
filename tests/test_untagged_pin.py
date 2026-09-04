"""verify/feed-contract/untagged_pin.py — the grade and the signature-state reading, at the
grader's own seam (eco-system ticket 69).

An untagged pin is never refused and never free: signed passes with no hole, untagged passes
only where the adopter's evidence prices it as an open hole under the adopter's own perspective
and currency, and a lookup that could not look is a SKIP. These tests pin the pure grade and the
state reading down so a change on either side shows up here before the gate.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "feed-contract" / "untagged_pin.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("untagged_pin", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KW: dict[str, Any] = dict(party="insurer", name="quote-driftwood", version="v1",
                          adopter="driftwood", currency="GBP")
SIGNED = {"state": "signed", "tag": "v1.0.0", "detail": "tag v1.0.0 on insurer: VERIFIED"}
UNTAGGED = {"state": "untagged", "tag": None, "detail": "no tag"}


def hole(**over: Any) -> dict:
    h = {"kind": "untagged-pin", "source": "insurer", "name": "quote-driftwood", "version": "v1",
         "status": "new", "perspective": "driftwood", "currency": "GBP", "amount": 113403.3,
         "priced_by": "insurer quote-driftwood@v1: the premium the pin books", "detail": "x"}
    h.update(over)
    return h


def evidence(h: dict | None) -> dict:
    return {"prices": [{"source": "insurer", "kind": "premium", "name": "quote-driftwood",
                        "perspective": "driftwood", "currency": "GBP", "amount": 113403.3, "hole": h}]}


# -- the grade ---------------------------------------------------------------------------------


def test_signed_pin_passes_with_no_hole(grader: ModuleType) -> None:
    status, msg = grader.grade(SIGNED, evidence(None), **KW)
    assert status == "PASS" and "no hole" in msg


def test_signed_pin_with_a_stale_open_hole_passes_and_says_so(grader: ModuleType) -> None:
    status, msg = grader.grade(SIGNED, evidence(hole()), **KW)
    assert status == "PASS" and "re-composition closes it" in msg


@pytest.mark.parametrize("status", ["new", "recorded"])
def test_untagged_pin_priced_as_an_open_hole_passes(grader: ModuleType, status: str) -> None:
    got, msg = grader.grade(UNTAGGED, evidence(hole(status=status)), **KW)
    assert got == "PASS" and f"{status} hole of 113,403.30 GBP" in msg


@pytest.mark.parametrize("ev", [None, {"prices": []}, evidence(None), evidence(hole(status="closed"))])
def test_untagged_pin_with_nothing_pricing_it_fails(grader: ModuleType, ev: dict | None) -> None:
    assert grader.grade(UNTAGGED, ev, **KW)[0] == "FAIL"


@pytest.mark.parametrize("bad", [
    {"perspective": "ludlow"}, {"currency": "USD"}, {"amount": 0.0}, {"amount": None},
    {"amount": True}, {"priced_by": None}, {"kind": "hole"}, {"name": "quote-ludlow"},
])
def test_a_malformed_hole_fails(grader: ModuleType, bad: dict) -> None:
    assert grader.grade(UNTAGGED, evidence(hole(**bad)), **KW)[0] == "FAIL"


def test_a_hole_missing_a_field_fails(grader: ModuleType) -> None:
    h = hole()
    h.pop("version")
    assert grader.grade(UNTAGGED, evidence(h), **KW)[0] == "FAIL"


@pytest.mark.parametrize("state", [
    {"state": "unreachable", "tag": None, "detail": "could not reach"},
    {"state": "unverifiable", "tag": "v1.0.0", "detail": "COULD-NOT-LOOK: no roots"},
])
def test_could_not_look_is_a_skip_never_a_pass(grader: ModuleType, state: dict) -> None:
    assert grader.grade(state, evidence(None), **KW)[0] == "SKIP"


# -- the state reading -------------------------------------------------------------------------


def test_signature_state_reads_existence_then_verification(grader: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    entry = {"kind": "feed", "name": "quote-driftwood", "path": "quote/driftwood"}
    monkeypatch.setattr(grader, "_remote_tags", lambda party: {"v1.0.0", "v1.3.0", "v2.0.0"})
    calls: list[str] = []

    def verified(estate: str, party: str, tag: str) -> tuple[str, str]:
        calls.append(tag)
        return "verified", "VERIFIED"

    monkeypatch.setattr(grader, "_verify", verified)
    s = grader.signature_state("/nowhere", "insurer", entry, "v1")
    assert s["state"] == "signed" and s["tag"] == "v1.3.0" and calls == ["v1.3.0"]
    assert grader.signature_state("/nowhere", "insurer", entry, "v3")["state"] == "untagged"
    assert grader.signature_state("/nowhere", "insurer", entry, "1.0.0")["tag"] == "v1.0.0"


def test_a_rejected_signature_is_untagged_and_a_could_not_look_is_not(grader: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    entry = {"kind": "feed", "name": "quote-driftwood", "path": "quote/driftwood"}
    monkeypatch.setattr(grader, "_remote_tags", lambda party: {"v1.0.0"})
    monkeypatch.setattr(grader, "_verify", lambda estate, party, tag: ("rejected", "REJECTED: identity"))
    s = grader.signature_state("/nowhere", "insurer", entry, "v1")
    assert s["state"] == "untagged" and s["tag"] == "v1.0.0" and "does not verify" in s["detail"]
    monkeypatch.setattr(grader, "_verify", lambda estate, party, tag: ("could-not-look", "COULD-NOT-LOOK"))
    assert grader.signature_state("/nowhere", "insurer", entry, "v1")["state"] == "unverifiable"
    monkeypatch.setattr(grader, "_remote_tags", lambda party: None)
    assert grader.signature_state("/nowhere", "insurer", entry, "v1")["state"] == "unreachable"


def test_identity_pins_and_skew_are_read_off_the_estate_never_literals(grader: ModuleType, tmp_path: Path) -> None:
    wf = tmp_path / "insurer" / ".github" / "workflows" / "release.yml"
    wf.parent.mkdir(parents=True)
    wf.write_text("env:\n  EXPECTED_IDENTITY_REGEXP: ^https://github\\.com/x/y/\\.github/workflows/cut-release\\.yml@refs/heads/main$\n"
                  "  EXPECTED_ISSUER: https://token.actions.githubusercontent.com\n")
    assert grader._identity_pins(str(tmp_path), "insurer") == (
        "^https://github\\.com/x/y/\\.github/workflows/cut-release\\.yml@refs/heads/main$",
        "https://token.actions.githubusercontent.com")
    assert grader._identity_pins(str(tmp_path), "nobody") is None
    dep = tmp_path / "platform" / "identity" / "gitsign-verifier" / "deployment.yaml"
    dep.parent.mkdir(parents=True)
    dep.write_text("env:\n  - name: GITSIGN_TAGGER_SKEW_SECONDS\n    value: \"60\"\n")
    assert grader._declared_skew(str(tmp_path)) == "60"
