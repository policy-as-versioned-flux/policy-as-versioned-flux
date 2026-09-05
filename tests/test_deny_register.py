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


def test_a_row_naming_a_source_that_cannot_be_read_fails_whatever_its_state() -> None:
    """A register that names a file nobody can open is a register that cannot be checked. It
    fails in both states, or renaming the renderer would quietly freeze the row."""
    for state in ("waiting", "converted-at-source"):
        reg = _register()
        reg["rules"][0]["state"] = state
        v = deny_register.grade([_finding("driftwood/composed/orphan-guard.yaml")], reg,
                                source_text={})
        assert v.verdict == "FAIL", state
        assert any("could not be read" in f for f in v.failures), (state, v.failures)


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


# -- 6. the blind spots the reviewer planted (all of these were misses) ---------------------------

def test_a_second_document_never_inherits_the_first_documents_name() -> None:
    """THE EXPLOITABLE ONE. Name attribution was positional and unbounded, so a document whose
    `metadata:` follows its `spec:` picked up the PREVIOUS document's name -- and a second Deny
    appended to a file a register row's globs already cover was reported as accounted for."""
    text = (
        "apiVersion: policies.kyverno.io/v1alpha1\n"
        "kind: ValidatingPolicy\n"
        "metadata:\n"
        "  name: policy-version-orphan-guard\n"
        "spec:\n"
        "  validationActions: [Audit]\n"
        "---\n"
        "apiVersion: policies.kyverno.io/v1alpha1\n"
        "kind: ValidatingPolicy\n"
        "spec:\n"
        "  validationActions: [Deny]\n"
        "metadata:\n"
        "  name: a-refusal-nobody-recorded\n"
    )
    found = deny_register.scan_text(text, "composed/orphan-guard.yaml")
    assert [f.name for f in found] == ["a-refusal-nobody-recorded"], [f.name for f in found]


def test_a_name_is_never_taken_from_a_different_document_even_looking_backwards() -> None:
    text = ("metadata:\n  name: first\nspec:\n  validationActions: [Audit]\n"
            "---\n"
            "spec:\n  validationActions: [Deny]\n")
    found = deny_register.scan_text(text, "p.yaml")
    assert [f.name for f in found] == [None], [f.name for f in found]


def test_a_one_line_flow_mapping_is_found() -> None:
    text = "metadata: {name: sneaky}\nspec: {validationActions: [Deny]}\n"
    assert [(f.name, f.shape) for f in deny_register.scan_text(text, "p.yaml")] == [
        ("sneaky", "validationActions: Deny")]


def test_a_multi_line_flow_sequence_is_found() -> None:
    text = "metadata:\n  name: sneaky\nspec:\n  validationActions: [\n    Deny\n  ]\n"
    assert [f.shape for f in deny_register.scan_text(text, "p.yaml")] == ["validationActions: Deny"]


def test_validation_failure_action_overrides_to_enforce_is_a_deny_shape() -> None:
    """A real Kyverno field: it turns an Audit policy into Enforce for named namespaces, so a
    policy that reads Audit at the top can refuse in production."""
    text = ("metadata:\n  name: sneaky\nspec:\n  validationFailureAction: audit\n"
            "  validationFailureActionOverrides:\n    - action: Enforce\n"
            "      namespaces: [prod]\n")
    shapes = [f.shape for f in deny_register.scan_text(text, "p.yaml")]
    assert "validationFailureActionOverrides: Enforce" in shapes, shapes


def test_a_json_policy_is_scanned_too() -> None:
    body = ('{"kind": "ValidatingPolicy", "metadata": {"name": "json-deny"},'
            ' "spec": {"validationActions": ["Deny"]}}')
    assert [(f.name, f.shape) for f in deny_register.scan_text(body, "p.json")] == [
        ("json-deny", "validationActions: Deny")]


def test_the_yaml_anchor_blind_spot_is_declared_rather_than_silently_missed() -> None:
    """An anchored action (`validationActions: *deny`) is NOT found, and the module says so.
    A scanner that cannot see something must name what it cannot see; the register's README and
    the gate script carry the same list."""
    text = "x: &deny [Deny]\nmetadata:\n  name: anchored\nspec:\n  validationActions: *deny\n"
    assert deny_register.scan_text(text, "p.yaml") == []
    assert any("anchor" in b.lower() for b in deny_register.BLIND_SPOTS), deny_register.BLIND_SPOTS


def test_the_blind_spots_are_a_non_empty_declared_list() -> None:
    assert len(deny_register.BLIND_SPOTS) >= 2
    assert all(isinstance(b, str) and b.strip() for b in deny_register.BLIND_SPOTS)


# -- 7. the reviewer's second plant: a `- name:` in a list is not the policy's name ---------------

#: The decoy sits BETWEEN the real metadata name and the Deny, which is what makes the
#: backwards search land on it. Order is the whole exploit.
PLANTED_LIST_NAME = """\
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata:
  name: block-all-images-from-anywhere
spec:
  matchConditions:
    - name: posture-trust-boundary
      expression: "true"
  validationActions: [Deny]
"""


def test_a_list_item_name_is_never_read_as_the_policys_name() -> None:
    """THE SECOND PLANT. Round 2 widened the name regex from `^\\s*name:` (a match, which
    skipped list items) to a search, so a `- name:` inside matchConditions, variables or
    validations became readable as the document's own name. The reviewer used that to camouflage
    an unrecorded Deny as a copy of `posture-trust-boundary`: the register's globs already cover
    the file, so the inventory reported it accounted-for and the check stayed on its normal SKIP.
    """
    found = deny_register.scan_text(PLANTED_LIST_NAME, "composed/policies/v4.0.0/posture-trust-boundary.yaml")
    assert [f.name for f in found] == ["block-all-images-from-anywhere"], [f.name for f in found]


def test_the_planted_camouflage_is_graded_as_an_undeclared_deny() -> None:
    """End to end: the plant must FAIL the grade, not ride in on another rule's globs."""
    register = deny_register.load_register(
        ROOT / "verify" / "deny-is-not-a-rung" / "register.yaml")
    findings = deny_register.scan_text(
        PLANTED_LIST_NAME, ".estate-clone/driftwood/composed/policies/v4.0.0/posture-trust-boundary.yaml")
    verdict = deny_register.grade(findings, register, source_text={})
    assert verdict.verdict == "FAIL", verdict.line
    assert any("no register row" in f for f in verdict.failures), verdict.failures


def test_a_list_item_name_does_not_mask_a_missing_metadata_name() -> None:
    """No `metadata.name` at all, only a list-item one: the finding is unnamed, so it belongs to
    no row and fails, rather than borrowing the list item's."""
    text = ("spec:\n  validationActions: [Deny]\n  matchConditions:\n"
            "    - name: posture-trust-boundary\n      expression: \"true\"\n")
    found = deny_register.scan_text(text, "p.yaml")
    assert [f.name for f in found] == [None], [f.name for f in found]


def test_a_deeper_metadata_name_loses_to_the_shallowest_one_in_a_template_string() -> None:
    """Inside a ResourceSet's template string there is no document to parse, so the shallowest
    non-list `name:` wins -- which is the policy's own metadata, not anything nested under it."""
    text = ("    apiVersion: policies.kyverno.io/v1alpha1\n"
            "    kind: ValidatingPolicy\n"
            "    metadata:\n"
            "      name: real-policy-name\n"
            "    spec:\n"
            "      validationActions: [Deny]\n"
            "      variables:\n"
            "        - name: decoy\n"
            "          expression: \"1\"\n")
    found = deny_register.scan_text(text, "gitops/composed/composed-set.yaml")
    assert [f.name for f in found] == ["real-policy-name"], [f.name for f in found]


def test_round_ones_plant_still_attributes_correctly() -> None:
    """The first plant must not regress while the second is fixed."""
    found = deny_register.scan_text(
        "apiVersion: v1\nkind: ValidatingPolicy\nmetadata:\n  name: first\n"
        "spec:\n  validationActions: [Audit]\n"
        "---\n"
        "apiVersion: v1\nkind: ValidatingPolicy\nspec:\n  validationActions: [Deny]\n"
        "metadata:\n  name: second-unrecorded\n", "p.yaml")
    assert [f.name for f in found] == ["second-unrecorded"], [f.name for f in found]


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
