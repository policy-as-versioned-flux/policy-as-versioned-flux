"""verify/trust-root — the committed trust roots are dated, and they carry what the served artefact names.

Eco-system ticket 105. Ticket 101 pinned ludlow's Sigstore trust material in a committed
trusted_root.json; ticket 105 puts the same pin in driftwood and tuppence. A pinned root refuses
BY NAME when it lacks a key for the log an artefact names, which is the correct failure and a real
maintenance obligation: Sigstore rotating a log turns three required checks red until three pull
requests land. This check turns that from a surprise into a schedule -- per adopter it prints the
age of the committed root and the validity window of every key against today, as numbers and
dates, and it grades only what cannot go stale: that every log platform's evidence at that
adopter's pin names is carried by that adopter's root inside the key's own window.

These tests pin the pure half beside the grader: the DER reading, the window arithmetic and the
judgement. The estate half -- real clones, real committed files -- is the verify script.
"""

from __future__ import annotations

import base64
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "trust-root" / "trust_root.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("trust_root", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TODAY = datetime(2026, 9, 9, tzinfo=timezone.utc)
STAMP = datetime(2026, 8, 25, 16, 31, 21, 909000, tzinfo=timezone.utc)


def _b64(hex_id: str) -> str:
    return base64.b64encode(bytes.fromhex(hex_id)).decode()


def _root(ct_ids=("dd" * 32,), tlog_ids=("c0" * 32,), ct_end: str | None = None) -> dict:
    return {
        "certificateAuthorities": [
            {"uri": "https://fulcio.sigstore.dev",
             "validFor": {"start": "2021-03-07T03:20:29Z", "end": "2022-12-31T23:59:59.999Z"},
             "certChain": {"certificates": [{"rawBytes": "QUJD"}]}},
            {"uri": "https://fulcio.sigstore.dev", "validFor": {"start": "2022-04-13T20:06:15Z"},
             "certChain": {"certificates": [{"rawBytes": "QUJD"}, {"rawBytes": "REVG"}]}},
        ],
        "tlogs": [{"baseUrl": "https://rekor.sigstore.dev", "logId": {"keyId": _b64(i)},
                   "publicKey": {"rawBytes": "REVG", "keyDetails": "PKIX_ECDSA_P256_SHA_256",
                                 "validFor": {"start": "2021-01-12T11:53:27Z"}}} for i in tlog_ids],
        "ctlogs": [{"baseUrl": "https://ctfe.sigstore.dev/2022", "logId": {"keyId": _b64(i)},
                    "publicKey": {"rawBytes": "R0hJ", "keyDetails": "PKIX_ECDSA_P256_SHA_256",
                                  "validFor": {"start": "2022-10-20T00:00:00Z",
                                               **({"end": ct_end} if ct_end else {})}}} for i in ct_ids]
                  + [{"baseUrl": "https://ctfe.sigstore.dev/test", "logId": {"keyId": _b64("08" * 32)},
                      "publicKey": {"rawBytes": "R0hJ", "keyDetails": "PKIX_ECDSA_P256_SHA_256",
                                    "validFor": {"start": "2021-03-14T00:00:00Z",
                                                 "end": "2022-10-31T23:59:59.999Z"}}}],
    }


# --------------------------------------------------------------------------------------------
# the certificate's own SCTs -- log id and timestamp, read out of the DER
# --------------------------------------------------------------------------------------------
def _sct_cert(log_ids: list[str], stamp_ms: int, oid: bytes) -> bytes:
    scts = b""
    for log_id in log_ids:
        sct = bytes([0]) + bytes.fromhex(log_id) + stamp_ms.to_bytes(8, "big") + b"\x00\x00\x00\x00"
        scts += len(sct).to_bytes(2, "big") + sct
    inner = len(scts).to_bytes(2, "big") + scts

    def octet(payload: bytes) -> bytes:
        return b"\x04" + bytes([len(payload)]) + payload
    return b"\x30\x82\x00\x10" + oid + octet(octet(inner))


def test_sct_entries_read_every_log_id_and_its_timestamp_out_of_the_der(grader: ModuleType) -> None:
    stamp_ms = int(STAMP.timestamp() * 1000)
    der = _sct_cert(["dd" * 32, "ee" * 32], stamp_ms, grader.SCT_EXTENSION_OID_DER)
    got = grader.sct_entries(der)
    assert [log_id for log_id, _ in got] == ["dd" * 32, "ee" * 32]
    assert all(abs((at - STAMP).total_seconds()) < 0.001 for _, at in got)


def test_a_certificate_without_the_extension_names_no_log(grader: ModuleType) -> None:
    assert grader.sct_entries(b"\x30\x82\x00\x10no extension here") == []


# --------------------------------------------------------------------------------------------
# the committed root -- keys, windows, ages
# --------------------------------------------------------------------------------------------
def test_root_keys_carry_kind_id_and_window(grader: ModuleType) -> None:
    keys = grader.root_keys(_root())
    kinds = {(k.kind, k.key_id) for k in keys}
    assert ("ctlog", "dd" * 32) in kinds and ("tlog", "c0" * 32) in kinds and ("ctlog", "08" * 32) in kinds
    retired = next(k for k in keys if k.key_id == "08" * 32)
    assert retired.end is not None and retired.end.year == 2022
    assert sum(1 for k in keys if k.kind == "ca") == 2


def test_window_status_is_a_date_and_a_number_never_an_adjective_alone(grader: ModuleType) -> None:
    current = grader.window_status(datetime(2022, 10, 20, tzinfo=timezone.utc), None, TODAY)
    assert current.startswith("current") and "2022-10-20" in current and "days" in current
    retired = grader.window_status(datetime(2021, 3, 14, tzinfo=timezone.utc),
                                   datetime(2022, 10, 31, 23, 59, 59, tzinfo=timezone.utc), TODAY)
    assert retired.startswith("retired") and "2022-10-31" in retired and "1408 days ago" in retired
    future = grader.window_status(TODAY + timedelta(days=10), None, TODAY)
    assert future.startswith("not yet valid") and "in 10 days" in future


def test_carries_selects_the_key_whose_window_covers_the_artefact(grader: ModuleType) -> None:
    keys = grader.root_keys(_root())
    assert grader.carries(keys, "ctlog", "dd" * 32, STAMP) is not None
    assert grader.carries(keys, "ctlog", "08" * 32, STAMP) is None   # retired 2022, the artefact is 2026
    assert grader.carries(keys, "ctlog", "ab" * 32, STAMP) is None   # never pinned
    assert grader.carries(keys, "tlog", "c0" * 32, STAMP) is not None


def test_newest_start_is_the_youngest_log_key(grader: ModuleType) -> None:
    newest = grader.newest_start(grader.root_keys(_root()))
    assert newest == datetime(2022, 10, 20, tzinfo=timezone.utc)


# --------------------------------------------------------------------------------------------
# the judgement
# --------------------------------------------------------------------------------------------
_UNSET: list = []


def _obs(root=_root(), committed=datetime(2026, 8, 24, tzinfo=timezone.utc), sha="0160b5f5a304",
         logs=_UNSET, reason="") -> dict:
    if logs is _UNSET:
        logs = [{"kind": "ctlog", "id": "dd" * 32, "at": STAMP}, {"kind": "tlog", "id": "c0" * 32, "at": STAMP}]
    return {"pin": "v2.0.1",
            "root": None if root is None else {"sha": sha, "committed": committed, "keys": _keys(root)},
            "reason": reason,
            "artefacts": [{"version": "2.0.1", "logs": logs}]}


_KEYS_CACHE: dict = {}


def _keys(root: dict):
    spec = importlib.util.spec_from_file_location("trust_root_k", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.root_keys(root)


def test_a_root_carrying_every_named_log_inside_its_window_passes_and_prints_the_ages(grader: ModuleType) -> None:
    verdict, lines = grader.grade({"ludlow": _obs()}, TODAY)
    assert verdict == "PASS", lines
    text = "\n".join(t for _, t in lines)
    assert "committed 2026-08-24" in text and "16 days ago" in text
    assert "newest log key starts 2022-10-20" in text and "1420 days ago" in text
    assert "ctfe.sigstore.dev/test" in text and "retired" in text


def test_a_log_the_root_does_not_carry_is_false_and_named(grader: ModuleType) -> None:
    verdict, lines = grader.grade({"driftwood": _obs(root=_root(ct_ids=("ab" * 32,)))}, TODAY)
    assert verdict == "FAIL"
    fails = [t for lvl, t in lines if lvl == "FAIL"]
    assert any("driftwood" in t and "dd" * 8 in t and "carries no key" in t for t in fails), fails


def test_a_key_whose_window_has_closed_before_the_artefact_is_false_and_dated(grader: ModuleType) -> None:
    verdict, lines = grader.grade({"tuppence": _obs(root=_root(ct_end="2026-01-01T00:00:00Z"))}, TODAY)
    assert verdict == "FAIL"
    fails = [t for lvl, t in lines if lvl == "FAIL"]
    assert any("tuppence" in t and "2026-01-01" in t and "2026-08-25" in t for t in fails), fails


def test_an_absent_root_is_a_could_not_look_by_name_never_a_pass(grader: ModuleType) -> None:
    verdict, lines = grader.grade(
        {"driftwood": _obs(root=None, reason="driftwood commits no .github/scripts/trusted_root.json at HEAD")}, TODAY)
    assert verdict == "SKIP"
    assert any(lvl == "SKIP" and "driftwood" in t and "trusted_root.json" in t for lvl, t in lines)


def test_one_absent_root_beside_one_stale_root_is_false(grader: ModuleType) -> None:
    verdict, _ = grader.grade({"a": _obs(root=None, reason="a commits no root"),
                               "b": _obs(root=_root(ct_ids=("ab" * 32,)))}, TODAY)
    assert verdict == "FAIL"


def test_identical_and_differing_roots_are_reported_as_a_fact_not_graded(grader: ModuleType) -> None:
    verdict, lines = grader.grade({"a": _obs(sha="aaaa"), "b": _obs(sha="aaaa"), "c": _obs(sha="cccc")}, TODAY)
    assert verdict == "PASS"
    note = next(t for lvl, t in lines if lvl == "note" and "byte-identical" in t or "differ" in t)
    assert "c" in note and "cccc" in note
    verdict, lines = grader.grade({"a": _obs(sha="aaaa"), "b": _obs(sha="aaaa")}, TODAY)
    assert any(lvl == "note" and "byte-identical" in t and "2 adopter" in t for lvl, t in lines)


def test_an_artefact_naming_no_log_at_all_is_false(grader: ModuleType) -> None:
    # A certificate without an SCT, or a bundle without a rekorBundle: nothing to pin against, and
    # a root "carrying everything the artefact names" would be vacuously true.
    verdict, lines = grader.grade({"a": _obs(logs=[])}, TODAY)
    assert verdict == "FAIL"
    assert any("names no" in t for lvl, t in lines if lvl == "FAIL")


def test_a_bundle_that_could_not_be_read_is_false_and_does_not_say_it_named_no_log(grader: ModuleType) -> None:
    # artefact_logs() returns None for a served bundle of neither shape, or one whose certificate
    # cannot be decoded. That is a different fact from "the artefact names no log", and saying the
    # second when the first happened would be a sentence the run did not derive.
    verdict, lines = grader.grade({"a": _obs(logs=None)}, TODAY)
    assert verdict == "FAIL"
    fails = [t for lvl, t in lines if lvl == "FAIL"]
    assert any("could not be read as a bundle" in t for t in fails), fails
    assert not any("names no transparency log" in t for t in fails), fails


def test_the_selfcheck_the_verify_script_runs_first_passes(grader: ModuleType) -> None:
    assert grader.selfcheck() == 0
