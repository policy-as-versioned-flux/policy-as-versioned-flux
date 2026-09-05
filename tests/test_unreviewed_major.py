"""verify/unreviewed-major — the standing report's own rules, at the grader's own seam.

Eco-system ticket 99. "An institution should not quietly carry a major nobody reviewed" is a real
property, and until this ticket tuppence's adopter gate enforced it as a per-pull-request refusal:
the wrong shape, because the fact does not depend on anyone opening a pull request. It is a report
now, carried by the truth surface on every run, red on its own terms.

These tests pin the pure half: what counts as the composed window, where each adopter's own
identity constant is read from, and what the report says. The estate half — each adopter's real
composed evidence, platform's real signed evidence at the tag that adopter really pins, and a real
cosign verification — is verify-unreviewed-major-in-window.sh.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "unreviewed-major" / "unreviewed_major.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("unreviewed_major", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- the window ---------------------------------------------------------------------------------


def test_the_window_is_the_member_versions_deduplicated(grader: ModuleType) -> None:
    doc = {"members": [{"name": "a", "version": "4.0.0"}, {"name": "b", "version": "4.0.0"},
                       {"name": "c", "version": "2.0.1"}]}
    assert grader.window_from_evidence(doc) == ["2.0.1", "4.0.0"]


def test_a_platform_machinery_member_carries_no_version_and_is_not_one(grader: ModuleType) -> None:
    doc = {"members": [{"name": "policy-version-orphan-guard"}, {"name": "a", "version": "4.0.0"}]}
    assert grader.window_from_evidence(doc) == ["4.0.0"]


# -- the pin ------------------------------------------------------------------------------------


def test_the_pinned_tag_is_read_off_the_gitrepository_document_of_a_multi_document_stream(
        grader: ModuleType) -> None:
    text = ("apiVersion: source.toolkit.fluxcd.io/v1\nkind: GitRepository\nmetadata:\n"
            "  name: platform\nspec:\n  ref:\n    tag: v2.0.1\n    commit: " + "d" * 40 + "\n"
            "---\napiVersion: kustomize.toolkit.fluxcd.io/v1\nkind: Kustomization\nspec:\n  path: x\n")
    assert grader.pin_from_pin_yaml(text) == ("v2.0.1", "d" * 40)
    assert grader.pin_from_pin_yaml("kind: Kustomization\nspec:\n  path: x\n") is None


# -- the identity constant, read where the adopter's own operation reads it ----------------------


def test_the_identity_constant_is_read_out_of_the_workflow_env_when_it_lives_there(
        grader: ModuleType) -> None:
    text = ("env:\n"
            "  EVIDENCE_EXPECTED_IDENTITY_REGEXP: ^https://github\\.com/org/platform/x\\.yml@refs/heads/main$\n"
            "  EXPECTED_ISSUER: https://token.actions.githubusercontent.com\n")
    got = grader.identity_from_workflow(text)
    assert got is not None
    regexp, issuer = got
    assert regexp.startswith("^https://github") and issuer.endswith("githubusercontent.com")


def test_the_identity_constant_is_read_out_of_the_gate_script_when_it_lives_there(
        grader: ModuleType) -> None:
    source = ('EXPECTED_PLATFORM_IDENTITY_REGEXP = (\n'
              '    r"^https://github\\.com/org/platform/"\n'
              '    r"\\.github/workflows/cut-release\\.yml@refs/heads/main$"\n'
              ')\n'
              'EXPECTED_PLATFORM_ISSUER = "https://token.actions.githubusercontent.com"\n')
    got = grader.identity_from_script(source)
    assert got is not None
    regexp, issuer = got
    # implicit concatenation across lines is one constant, not two
    assert regexp.endswith("refs/heads/main$") and "cut-release" in regexp
    assert issuer == "https://token.actions.githubusercontent.com"


def test_a_repository_that_holds_no_identity_constant_yields_nothing_rather_than_a_default(
        grader: ModuleType) -> None:
    assert grader.identity_from_workflow("env:\n  FOO: bar\n") is None
    assert grader.identity_from_script("X = 1\n") is None


# -- the report ---------------------------------------------------------------------------------


def test_a_major_standing_in_a_window_is_named_with_its_adopter_and_the_tag_it_was_read_at(
        grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "tuppence", "tag": "v2.0.1", "window": ["4.0.0"],
         "computed": {"4.0.0": "major"}, "skip": None},
    ])
    assert status == "FAIL"
    body = " ".join(m for _, m in lines)
    assert "tuppence" in body and "4.0.0" in body and "v2.0.1" in body and "major" in body


def test_a_window_of_no_majors_is_the_pass(grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "driftwood", "tag": "v2.0.1", "window": ["2.0.1", "3.0.0"],
         "computed": {"2.0.1": "none", "3.0.0": "patch"}, "skip": None},
    ])
    assert status == "PASS"


def test_an_adopter_that_could_not_be_looked_at_makes_the_whole_report_a_could_not_look(
        grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "driftwood", "tag": "v2.0.1", "window": ["2.0.1"],
         "computed": {"2.0.1": "none"}, "skip": None},
        {"adopter": "ludlow", "tag": None, "window": [], "computed": {},
         "skip": "pins platform tag v9.9.9, which this checkout of platform has no tag object for"},
    ])
    assert status == "SKIP"
    assert any("v9.9.9" in m for _, m in lines)


def test_a_major_outranks_a_could_not_look_because_it_was_actually_observed(grader: ModuleType) -> None:
    # A red that was seen is not softened by a second adopter that could not be seen.
    status, _ = grader.grade([
        {"adopter": "tuppence", "tag": "v2.0.1", "window": ["4.0.0"],
         "computed": {"4.0.0": "major"}, "skip": None},
        {"adopter": "ludlow", "tag": None, "window": [], "computed": {}, "skip": "no clone"},
    ])
    assert status == "FAIL"


def test_no_adopter_at_all_is_a_could_not_look(grader: ModuleType) -> None:
    status, lines = grader.grade([])
    assert status == "SKIP"
    assert any("adopter role" in m for _, m in lines)
