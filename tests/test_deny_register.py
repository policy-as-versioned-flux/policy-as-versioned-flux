"""Eco-system ticket 89: deny is not a rung.

The seam is `verify/deny-is-not-a-rung/deny_register.py` — the scanner that finds every
Deny-shaped rule in a tree, and the grader that joins those findings to the register of
recorded choices. `verify-deny-is-not-a-rung.sh` runs it over the hub and the estate clone.

What these tests hold down, in the order the ticket asks for it:

  1. a Deny-shaped rule is found whether it is a parsed policy document or a line inside a
     ResourceSet template string (the adopters' `gitops/composed/composed-set.yaml` carries
     three of them that way, so a YAML-document scan alone reads the estate as cleaner than
     it is);
  2. a Deny nobody recorded a choice for FAILS — that is the whole inventory duty of item 1;
  3. the register may not lie in either direction: a rule the register calls converted may
     not still be found, and a rule the register says is still served may not have vanished;
  4. a rule whose source still emits the Deny cannot be called converted-at-source;
  5. a served copy that is still Deny-shaped is a could-not-look that NAMES what it waits
     for, never a pass and never a silent fail.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: a module holding a dataclass needs to find itself in sys.modules
    # while the decorator runs, and a file-spec load does not put it there on its own.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


deny_register = _load("deny_register", ROOT / "verify" / "deny-is-not-a-rung" / "deny_register.py")


VALIDATING_DENY = """\
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata:
  name: policy-version-orphan-guard
spec:
  validationActions:
  - Deny
"""

VALIDATING_AUDIT = VALIDATING_DENY.replace("- Deny", "- Audit")

RESOURCESET_WITH_EMBEDDED_DENY = """\
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSet
metadata:
  name: composed
spec:
  resourcesTemplate: |
    apiVersion: policies.kyverno.io/v1alpha1
    kind: ValidatingPolicy
    metadata:
      name: policy-version-orphan-guard
      labels:
        policy-as-versioned.dev/policy: platform-machinery
    spec:
      validationActions:
      - Deny
"""

LEGACY_ENFORCE = """\
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-department-label
spec:
  validationFailureAction: enforce
"""


# -- 1. the scanner sees both shapes, in a document and in a template string ----------------------

def test_a_deny_shaped_policy_document_is_found_with_its_name_and_kind() -> None:
    found = deny_register.scan_text(VALIDATING_DENY, "composed/orphan-guard.yaml")
    assert [(f.name, f.shape) for f in found] == [
        ("policy-version-orphan-guard", "validationActions: Deny"),
    ]
    assert found[0].kind == "ValidatingPolicy"
    assert found[0].path == "composed/orphan-guard.yaml"


def test_an_audit_policy_is_not_a_finding() -> None:
    assert deny_register.scan_text(VALIDATING_AUDIT, "composed/orphan-guard.yaml") == []


def test_a_deny_inside_a_resourceset_template_string_is_found_and_named() -> None:
    """A YAML-document scan cannot see these: the policy is a string, not a document. Three
    of the estate's Denys ship exactly this way, one per adopter."""
    found = deny_register.scan_text(RESOURCESET_WITH_EMBEDDED_DENY, "gitops/composed/composed-set.yaml")
    assert [(f.name, f.shape) for f in found] == [
        ("policy-version-orphan-guard", "validationActions: Deny"),
    ]


def test_the_2022_validation_failure_action_enforce_is_a_deny_shape() -> None:
    found = deny_register.scan_text(LEGACY_ENFORCE, "legacy.yaml")
    assert [(f.name, f.shape) for f in found] == [
        ("require-department-label", "validationFailureAction: Enforce"),
    ]


def test_an_inline_flow_sequence_is_found_too() -> None:
    text = "metadata:\n  name: n\nspec:\n  validationActions: [Deny]\n"
    assert [f.shape for f in deny_register.scan_text(text, "p.yaml")] == ["validationActions: Deny"]


def test_a_finding_with_no_recoverable_name_is_still_a_finding() -> None:
    found = deny_register.scan_text("spec:\n  validationActions: [Deny]\n", "p.yaml")
    assert len(found) == 1 and found[0].name is None


# -- 2. an unrecorded Deny fails -----------------------------------------------------------------

def _register(**rules_over) -> dict:
    base = {
        "version": 1,
        "excluded": [{"path": "spikes/", "reason": "spike material, never served"}],
        "rules": [
            {
                "rule": "policy-version-orphan-guard",
                "matches": "^policy-version-orphan-guard$",
                "choice": "re-expressed",
                "state": "converted-at-source",
                "reason": "the bottom rung, not a refusal",
                "source_clean": ["platform/distribution/render-orphan-guard.py"],
                "served_copies": ["*/composed/orphan-guard.yaml"],
                "awaits": "the next signed platform tag, then each adopter's pin bump",
            },
        ],
    }
    base.update(rules_over)
    return base


def _finding(path: str, name: str = "policy-version-orphan-guard"):
    return deny_register.Finding(path=path, line=1, name=name, kind="ValidatingPolicy",
                                 shape="validationActions: Deny")


def test_a_deny_no_rule_matches_is_a_failure_that_names_the_path() -> None:
    v = deny_register.grade([_finding("platform/posture/policies/posture-trust-boundary.yaml",
                                      name="posture-trust-boundary")],
                            _register(), source_text={})
    assert v.verdict == "FAIL"
    assert any("posture-trust-boundary" in f and "no register row" in f for f in v.failures), v.failures


# -- 3. the register may not lie in either direction ----------------------------------------------

def test_a_rule_the_register_calls_converted_may_not_still_be_found() -> None:
    reg = _register()
    reg["rules"][0]["state"] = "converted"
    reg["rules"][0].pop("served_copies")
    reg["rules"][0].pop("awaits")
    v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], reg, source_text={})
    assert v.verdict == "FAIL"
    assert any("says converted" in f for f in v.failures), v.failures


def test_a_rule_the_register_says_is_still_served_may_not_have_vanished() -> None:
    v = deny_register.grade([], _register(), source_text={})
    assert v.verdict == "FAIL"
    assert any("no copy of it is left" in f for f in v.failures), v.failures


def test_a_served_copy_outside_the_declared_globs_is_a_failure() -> None:
    v = deny_register.grade([_finding("platform/distribution/policies/v9.0.0/orphan-guard.yaml")],
                            _register(), source_text={})
    assert v.verdict == "FAIL"
    assert any("not one of the copies the register declares" in f for f in v.failures), v.failures


# -- 4. converted-at-source means the source really is clean --------------------------------------

def test_a_source_that_still_emits_the_deny_cannot_be_called_converted_at_source() -> None:
    v = deny_register.grade(
        [_finding("driftwood/composed/orphan-guard.yaml")],
        _register(),
        source_text={"platform/distribution/render-orphan-guard.py":
                     '"validationActions": ["Deny"],\n'},
    )
    assert v.verdict == "FAIL"
    assert any("still emits a Deny" in f for f in v.failures), v.failures


def test_a_waiting_row_whose_source_is_already_clean_must_move_on() -> None:
    """Without this the register lags the code by exactly the interval between a merge and
    somebody remembering to edit a yaml file, which is the shape of every stale record the
    2026-09-02 review found."""
    reg = _register()
    reg["rules"][0]["state"] = "waiting"
    v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], reg,
                            source_text={"platform/distribution/render-orphan-guard.py": "# clean\n"})
    assert v.verdict == "FAIL"
    assert any("no longer emits it" in f for f in v.failures), v.failures


def test_a_waiting_row_whose_source_still_emits_the_deny_is_a_skip() -> None:
    reg = _register()
    reg["rules"][0]["state"] = "waiting"
    v = deny_register.grade(
        [_finding("driftwood/composed/orphan-guard.yaml")], reg,
        source_text={"platform/distribution/render-orphan-guard.py": '  validationActions: [Deny]\n'})
    assert v.verdict == "SKIP"


def test_a_clean_source_with_copies_outstanding_is_a_could_not_look_that_names_the_wait() -> None:
    v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], _register(),
                            source_text={"platform/distribution/render-orphan-guard.py": "# no deny here\n"})
    assert v.verdict == "SKIP"
    assert v.outstanding == 1
    assert "the next signed platform tag" in v.line
    assert "policy-version-orphan-guard" in v.line


# -- 5. nothing outstanding is the only PASS ------------------------------------------------------

def test_every_rule_converted_and_nothing_found_is_the_pass() -> None:
    reg = _register()
    reg["rules"][0]["state"] = "converted"
    reg["rules"][0].pop("served_copies")
    reg["rules"][0].pop("awaits")
    v = deny_register.grade([], reg, source_text={"platform/distribution/render-orphan-guard.py": ""})
    assert v.verdict == "PASS"
    assert v.failures == []


def test_a_register_row_with_no_reason_is_a_failure() -> None:
    reg = _register()
    reg["rules"][0].pop("reason")
    v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], reg, source_text={})
    assert v.verdict == "FAIL"
    assert any("no reason" in f for f in v.failures), v.failures


def test_an_outstanding_row_with_no_awaits_is_a_failure_not_a_skip() -> None:
    reg = _register()
    reg["rules"][0].pop("awaits")
    v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], reg, source_text={})
    assert v.verdict == "FAIL"
    assert any("does not name what it waits for" in f for f in v.failures), v.failures


def test_an_unknown_choice_is_a_failure() -> None:
    reg = _register()
    reg["rules"][0]["choice"] = "leave it alone"
    v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], reg, source_text={})
    assert v.verdict == "FAIL"
    assert any("choice" in f for f in v.failures), v.failures


# -- the committed register is a real one over the real trees -------------------------------------

def test_the_committed_register_covers_every_deny_the_real_trees_carry() -> None:
    """Not a fixture: the register that ships must account for the estate as it is today. If
    the estate clone is not assembled there is nothing to grade and the test says so."""
    register = deny_register.load_register(
        ROOT / "verify" / "deny-is-not-a-rung" / "register.yaml")
    estate = ROOT / ".estate-clone"
    if not (estate / "platform").is_dir():
        pytest.skip("no .estate-clone/platform — clone-estate.sh has not run here")
    findings = deny_register.scan_tree(ROOT, register["excluded"])
    unmatched = [f for f in findings if deny_register.rule_for(f, register["rules"]) is None]
    assert unmatched == [], f"Denys with no register row: {[(f.path, f.name) for f in unmatched]}"
