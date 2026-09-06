"""verify/real-signature — does every adopter gate really check a real signature?

Eco-system ticket 101. Ticket 99 found that no adopter gate in the estate had ever been observed
verifying a signature platform actually published, and that ludlow's could not: with the cosign
version ludlow itself pins, its own invocation refused every bundle platform publishes before it
looked at the signature at all. The defect was latent for weeks because a gate reaches its
signature check only when its composed member set moves, and nothing graded the one sentence that
would have caught it.

These tests pin the pure half of the grader beside them: the corruption it plants, and the way it
judges what two runs of a real gate said. The estate half — real clones, real cosign, real exit
codes — is verify-a-real-signature-is-checked.sh.

The load-bearing case is `test_a_gate_that_refuses_both_halves_is_false`: that is the exact shape
ludlow shipped, and a check that graded only the refusal would have called it a pass.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "real-signature" / "real_signature.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("real_signature", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _result(verdict: str, output: str = "", exit_code: int | None = None) -> dict:
    return {"verdict": verdict, "composed": None,
            "exit": (0 if verdict == "adopt" else 1) if exit_code is None else exit_code,
            "argv": [], "output": output}


ADOPT = _result("adopt", "PASS: declared=minor composed=none")
REFUSE_SIGNATURE = _result("refuse", "cosign verify-blob refused the evidence signature")
REFUSE_FLAG = _result("refuse", "Error: --trusted-root only supported with --new-bundle-format")


# --------------------------------------------------------------------------------------------
# tamper_signature — the corruption the REFUSE half rests on
# --------------------------------------------------------------------------------------------
def test_tamper_changes_the_legacy_signature_and_nothing_else(grader: ModuleType) -> None:
    """Platform publishes the legacy shape today, so this is the path that runs."""
    original = {"base64Signature": "AAAA", "cert": "Y2VydA==", "rekorBundle": {"Payload": {"logID": "ab"}}}
    tampered = json.loads(grader.tamper_signature(json.dumps(original)))
    assert tampered["base64Signature"] != original["base64Signature"]
    assert tampered["cert"] == original["cert"]
    assert tampered["rekorBundle"] == original["rekorBundle"]


def test_tamper_changes_a_new_format_signature(grader: ModuleType) -> None:
    """A new-format bundle is where the estate is going; the corruption has to reach it too, or
    the refuse half silently stops corrupting anything on the day platform re-signs."""
    original = {"mediaType": "application/vnd.dev.sigstore.bundle.v0.3+json",
                "verificationMaterial": {}, "messageSignature": {"signature": "BBBB"}}
    tampered = json.loads(grader.tamper_signature(json.dumps(original)))
    assert tampered["messageSignature"]["signature"] != "BBBB"
    assert tampered["verificationMaterial"] == {}


def test_tamper_never_leaves_the_signature_unchanged(grader: ModuleType) -> None:
    """The first character is replaced with one it is not, whichever it was — so a bundle whose
    signature happens to begin with the replacement character is still really corrupted."""
    for first in ("A", "B", "C"):
        tampered = json.loads(grader.tamper_signature(json.dumps({"base64Signature": first + "ZZ", "cert": "x"})))
        assert tampered["base64Signature"] != first + "ZZ"


@pytest.mark.parametrize("bundle, why", [
    (json.dumps({"nothing": "here"}), "no signature field anywhere"),
    (json.dumps(["not", "an", "object"]), "not a bundle object at all"),
    (json.dumps({"mediaType": "m", "messageSignature": {"signature": ""}}), "an empty signature"),
    ("this is not JSON", "not JSON"),
])
def test_a_bundle_whose_signature_cannot_be_reached_raises(grader: ModuleType, bundle: str, why: str) -> None:
    """Returning the bundle unchanged would turn the REFUSE half into a second ACCEPT — and it
    would pass, reporting that a gate refuses a corrupted signature when nothing was corrupted."""
    with pytest.raises((ValueError, json.JSONDecodeError)):
        grader.tamper_signature(bundle)


# --------------------------------------------------------------------------------------------
# grade — both halves, and neither alone
# --------------------------------------------------------------------------------------------
def test_accepting_the_real_signature_and_refusing_the_corrupted_one_passes(grader: ModuleType) -> None:
    verdict, _ = grader.grade({"driftwood": {"version": "2.0.1", "accept": ADOPT, "refuse": REFUSE_SIGNATURE}})
    assert verdict == "PASS"


def test_a_gate_that_refuses_both_halves_is_false(grader: ModuleType) -> None:
    """The exact shape ludlow shipped until 2026-09-06: its invocation refused every bundle
    platform publishes, on the flag, before reaching the signature. A grader that only asked
    "does it refuse a corrupted signature?" would have called that a pass and the defect would
    have survived another week."""
    verdict, lines = grader.grade({"ludlow": {"version": "2.0.1", "accept": REFUSE_FLAG, "refuse": REFUSE_FLAG}})
    assert verdict == "FAIL"
    assert any("ludlow" in text and "did NOT accept" in text for level, text in lines if level == "FAIL")


def test_a_gate_that_adopts_a_corrupted_signature_is_false(grader: ModuleType) -> None:
    verdict, lines = grader.grade({"a": {"version": "2.0.1", "accept": ADOPT, "refuse": ADOPT}})
    assert verdict == "FAIL"
    assert any("ADOPTED the same evidence" in text for level, text in lines if level == "FAIL")


def test_a_refusal_that_names_neither_cosign_nor_the_signature_is_false(grader: ModuleType) -> None:
    """A gate can refuse a corrupted bundle for a reason that has nothing to do with the
    signature — a pin mismatch, a missing file, a crash. That is not evidence that the signature
    was read, and reading it as one is how a check comes to grade its own assumption."""
    refuse_pin = _result("refuse", "platform tag resolves to a different commit than the pin names")
    verdict, _ = grader.grade({"a": {"version": "2.0.1", "accept": ADOPT, "refuse": refuse_pin}})
    assert verdict == "FAIL"


def test_a_gate_that_could_not_be_invoked_is_a_could_not_look(grader: ModuleType) -> None:
    """Never a pass. An uninvokable gate has not said that it checks a signature, and this whole
    check exists because something never observed was assumed for weeks."""
    verdict, lines = grader.grade({"a": {"version": "2.0.1", "accept": None, "refuse": None,
                                          "reason": "carries no adopter gate script"}})
    assert verdict == "SKIP"
    assert any("could not be invoked" in text for _, text in lines)


def test_one_unknown_beside_an_observed_pass_is_still_a_could_not_look(grader: ModuleType) -> None:
    """The estate has not been observed whole, and saying PASS would claim it had."""
    verdict, _ = grader.grade({
        "a": {"version": "2.0.1", "accept": ADOPT, "refuse": REFUSE_SIGNATURE},
        "b": {"version": "2.0.1", "accept": None, "refuse": None, "reason": "no identity constant"},
    })
    assert verdict == "SKIP"


def test_one_false_beside_one_unknown_is_false(grader: ModuleType) -> None:
    """An observed falsehood outranks an unobserved one: a red that is real is not softened to a
    could-not-look because some other unit could not be looked at."""
    verdict, _ = grader.grade({
        "ludlow": {"version": "2.0.1", "accept": REFUSE_FLAG, "refuse": REFUSE_FLAG},
        "b": {"version": "2.0.1", "accept": None, "refuse": None, "reason": "no identity constant"},
    })
    assert verdict == "FAIL"


def test_the_selfcheck_the_verify_script_runs_first_passes(grader: ModuleType) -> None:
    """verify-a-real-signature-is-checked.sh runs --selfcheck before it grades the estate, so a
    run that reports the estate green has already shown the comparator goes red on a gate that
    does not check what it says it checks."""
    assert grader.selfcheck() == 0


# --------------------------------------------------------------------------------------------
# the planting itself — the false green of 2026-09-06
# --------------------------------------------------------------------------------------------
def test_a_planting_whose_commit_failed_is_not_gradeable(grader: ModuleType) -> None:
    """Found by running this check, not by reading it. This machine's global `core.hooksPath` hook
    stopped being able to run, `git commit` failed inside the planting, and
    fold_agreement._commit returns `git rev-parse HEAD`'s stdout -- which on a repository with no
    commits is the literal string "HEAD", with a non-zero exit nobody reads. Two of three gates
    then answered a question nobody had planted and the run would have reported the estate green.
    A sha that is not a sha means nothing downstream of it is about anything."""
    assert grader._planted_or_none({"base_sha": "HEAD", "head_sha": "HEAD"}) is not None
    assert grader._planted_or_none({"base_sha": "", "head_sha": "a" * 40}) is not None
    assert grader._planted_or_none({"base_sha": "a" * 40, "head_sha": "zzzz" + "a" * 36}) is not None
    assert grader._planted_or_none({"base_sha": "a" * 40, "head_sha": "0" * 40}) is None


def test_the_reason_a_failed_planting_gives_says_nothing_was_planted(grader: ModuleType) -> None:
    reason = grader._planted_or_none({"base_sha": "HEAD", "head_sha": "HEAD"})
    assert reason is not None and "nothing was planted" in reason


def test_the_planting_is_hermetic_against_the_operators_git_config(grader: ModuleType) -> None:
    """A grader that somebody's laptop hook can turn green is worse than no grader."""
    env = grader._hermetic_git()
    assert set(env) == {"GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"}
    assert all(value == os.devnull for value in env.values())


# --------------------------------------------------------------------------------------------
# the cold environment — ticket 101 review, F2
# --------------------------------------------------------------------------------------------
def test_the_cold_environment_clears_no_proxy(grader: ModuleType, tmp_path) -> None:
    """Setting the proxies is not enough to make the network unreachable. Measured 2026-09-06:
    with an ambient `NO_PROXY=*` exported, Go bypasses the closed port, cosign reaches Sigstore's
    CDN, and the offline measurement returns 0 — so the number printed would read "no network
    needed" for a gate that had just used the network. A measurement that fails in the reassuring
    direction is worse than none, because nobody looks behind a green one."""
    cold = grader.COLD_ENV(tmp_path / "home", tmp_path / "tuf")
    assert cold["NO_PROXY"] == ""
    assert cold["no_proxy"] == ""


def test_the_cold_environment_sets_both_spellings_of_every_proxy(grader: ModuleType, tmp_path) -> None:
    """Go reads the lowercase spellings too, and a tool that reads only those would have walked
    straight past an upper-case-only block."""
    cold = grader.COLD_ENV(tmp_path / "home", tmp_path / "tuf")
    for upper, lower in (("HTTPS_PROXY", "https_proxy"), ("HTTP_PROXY", "http_proxy"),
                         ("ALL_PROXY", "all_proxy")):
        assert cold[upper] and cold[lower], (upper, lower)
        assert "127.0.0.1:1" in cold[lower]


def test_the_cold_environment_isolates_the_caches_it_is_given(grader: ModuleType, tmp_path) -> None:
    cold = grader.COLD_ENV(tmp_path / "home", tmp_path / "tuf")
    assert cold["HOME"] == str(tmp_path / "home")
    assert cold["TUF_ROOT"] == str(tmp_path / "tuf")
