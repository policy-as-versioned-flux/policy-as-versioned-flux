"""Eco-system ticket 33: ledger, storefront and reports are lifted into their adopters.

The seam is `verify/lifted-apps/lifted_apps.py` — the grader that joins
`verify/lifted-apps/register.yaml` (which app went to which adopter, and with what) to what the
adopters' trees actually SERVE. `verify-lifted-apps.sh` runs it over the hub and the estate clone
and then runs kyverno over each served workload.

The rule these tests exist for: **name the served artefact and the operation that reaches it.**
The served artefact is the adopter's own `gitops/apps/` tree — the path its Flux Kustomization
reconciles (`gotk-sync.yaml`, `path: ./apps`). The operation is kustomize's resource accumulation
from `gitops/apps/kustomization.yaml`. A workload file that exists in that directory and is not
listed there is served to nobody, so "the file is present" is a proxy and is graded as one here.

What these tests hold down:

  1. the register covers the three apps of the ticket, each in exactly one adopter;
  2. a served file the kustomization does not list FAILS — the proxy above;
  3. the version label is measured against the ADOPTER'S OWN composed artefact
     (`composed/orphan-guard.yaml`'s allowed array), never against a constant in this repository;
  4. the old `mycompany.com/` label anywhere in the lifted tree FAILS — that is the re-label;
  5. a source tree without its stack manifest FAILS — without it there is nothing for the
     stack's Renovate manager to read, so the lift would be manifest-only;
  6. a renovate.json that does not enable the stack's manager, or leaves the dependency dashboard
     off, FAILS;
  7. an adopter that has not landed the lift is a could-not-look that NAMES its pull request —
     never a silent pass and never a red for work that is proposed and unmerged;
  8. the same app landing in two adopters FAILS — a lift is a move, not a copy;
  9. a copy of a lifted app inside the HUB FAILS — the thing this week is about;
 10. the residual (whose registry still publishes the image) is a NUMBER the report prints, not
     a sentence in a document that goes stale.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lifted_apps = _load("lifted_apps", ROOT / "verify" / "lifted-apps" / "lifted_apps.py")
REGISTER = ROOT / "verify" / "lifted-apps" / "register.yaml"


# --------------------------------------------------------------------------- fixture estate

ORPHAN_GUARD = """\
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata: {name: policy-version-orphan-guard}
spec:
  variables:
  - name: allowed
    expression: '[''4.0.0'']'
"""

SERVED = """\
apiVersion: v1
kind: Pod
metadata:
  name: ledger
  namespace: tuppence
  labels: {"policy-as-versioned.dev/policy-version": "4.0.0"}
spec:
  securityContext: {runAsNonRoot: true, runAsUser: 1000}
  containers:
    - name: ledger
      image: ghcr.io/policy-as-versioned-flux/ledger@sha256:0000
      securityContext: {readOnlyRootFilesystem: true}
"""

RENOVATE = {
    "enabledManagers": ["custom.regex", "maven"],
    "dependencyDashboard": True,
    "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\.xml$/"]},
}

REGISTER_ONE = """\
lifts:
- app: ledger
  origin: policy-as-versioned-flux/ledger
  origin_commit: 036bb97
  adopter: tuppence
  served: gitops/apps/ledger.yaml
  source_dir: apps/ledger
  stack_manifest: apps/ledger/pom.xml
  renovate_manager: maven
  image: ghcr.io/policy-as-versioned-flux/ledger@sha256:0000
  image_publisher: policy-as-versioned-flux
  pull_request: https://github.com/policy-as-versioned-tuppence/tuppence/pull/99
"""


def _estate(tmp_path: Path, *, served: str = SERVED, resources: list[str] | None = None,
            renovate: dict | None = None, stack: bool = True) -> Path:
    estate = tmp_path / "estate"
    a = estate / "tuppence"
    (a / "composed" / "policies" / "v4.0.0").mkdir(parents=True)
    (a / "composed" / "policies" / "v4.0.0" / "require-nonroot.yaml").write_text("{}\n")
    (a / "composed" / "orphan-guard.yaml").write_text(ORPHAN_GUARD)
    (a / "gitops" / "apps").mkdir(parents=True)
    (a / "gitops" / "apps" / "ledger.yaml").write_text(served)
    res = ["namespace.yaml", "ledger.yaml"] if resources is None else resources
    (a / "gitops" / "apps" / "kustomization.yaml").write_text(
        yaml.safe_dump({"apiVersion": "kustomize.config.k8s.io/v1beta1",
                        "kind": "Kustomization", "resources": res}))
    (a / "apps" / "ledger").mkdir(parents=True)
    if stack:
        (a / "apps" / "ledger" / "pom.xml").write_text("<project/>\n")
    (a / "renovate.json").write_text(json.dumps(RENOVATE if renovate is None else renovate))
    return estate


def _hub(tmp_path: Path) -> Path:
    hub = tmp_path / "hub"
    (hub / "twin").mkdir(parents=True)
    (hub / "twin" / "unrelated.py").write_text("x = 1\n")
    return hub


def _register(tmp_path: Path, text: str = REGISTER_ONE) -> Path:
    p = tmp_path / "register.yaml"
    p.write_text(text)
    return p


def _grade(tmp_path: Path, **kw):
    return lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=_estate(tmp_path, **kw),
                             register_path=_register(tmp_path))


# --------------------------------------------------------------------------- 1. the register

def test_the_register_names_the_three_apps_of_the_ticket_each_in_one_adopter():
    lifts = lifted_apps.load_register(REGISTER)
    assert {lift.app for lift in lifts} == {"ledger", "storefront", "reports"}
    assert len({lift.adopter for lift in lifts}) == 3
    for lift in lifts:
        assert lift.origin.startswith("policy-as-versioned-flux/")
        assert lift.renovate_manager
        assert lift.pull_request


# --------------------------------------------------------------------------- 2..6 the lift is real

def test_a_landed_lift_passes(tmp_path):
    report = _grade(tmp_path)
    assert report.exit_code == 0, report.text()
    assert report.rows[0].grade == "PASS"


def test_a_served_file_the_kustomization_does_not_list_fails(tmp_path):
    # The file is there; Flux's Kustomization renders resources[], so nobody is served it.
    report = _grade(tmp_path, resources=["namespace.yaml"])
    assert report.exit_code == 1, report.text()
    assert "not listed in gitops/apps/kustomization.yaml" in report.text()


def test_a_version_label_the_adopters_own_composed_artefact_does_not_allow_fails(tmp_path):
    report = _grade(tmp_path, served=SERVED.replace('"4.0.0"', '"3.0.0"'))
    assert report.exit_code == 1, report.text()
    assert "composed/orphan-guard.yaml" in report.text()


def test_the_old_label_anywhere_in_the_lifted_tree_fails(tmp_path):
    report = _grade(tmp_path, served=SERVED.replace(
        '"policy-as-versioned.dev/policy-version": "4.0.0"',
        '"mycompany.com/policy-version": "4.0.0", "policy-as-versioned.dev/policy-version": "4.0.0"'))
    assert report.exit_code == 1, report.text()
    assert "mycompany.com/" in report.text()


def test_a_workload_the_cage_would_not_admit_fails(tmp_path):
    report = _grade(tmp_path, served=SERVED.replace("readOnlyRootFilesystem: true",
                                                    "readOnlyRootFilesystem: false"))
    assert report.exit_code == 1, report.text()
    assert "readOnlyRootFilesystem" in report.text()


def test_a_source_tree_without_its_stack_manifest_fails(tmp_path):
    report = _grade(tmp_path, stack=False)
    assert report.exit_code == 1, report.text()
    assert "apps/ledger/pom.xml" in report.text()


def test_renovate_without_the_stacks_manager_fails(tmp_path):
    report = _grade(tmp_path, renovate={"enabledManagers": ["custom.regex"],
                                        "dependencyDashboard": True,
                                        "maven": RENOVATE["maven"]})
    assert report.exit_code == 1, report.text()
    assert "does not enable 'maven'" in report.text()


def test_a_manager_pointed_at_a_file_the_lift_did_not_bring_fails(tmp_path):
    # The manager is enabled and reads nothing that was lifted: a name in a list is not a bump
    # surface, and this is the shape a lift takes when the stack manifest moved and the config
    # was copied from another adopter.
    report = _grade(tmp_path, renovate={
        "enabledManagers": ["custom.regex", "maven"], "dependencyDashboard": True,
        "maven": {"managerFilePatterns": ["/^apps/somewhere-else/pom\\.xml$/"]}})
    assert report.exit_code == 1, report.text()
    assert "none of which matches apps/ledger/pom.xml" in report.text()


def test_a_manager_with_no_file_patterns_at_all_fails(tmp_path):
    report = _grade(tmp_path, renovate={"enabledManagers": ["custom.regex", "maven"],
                                        "dependencyDashboard": True})
    assert report.exit_code == 1, report.text()
    assert "managerFilePatterns" in report.text()


def test_renovate_without_the_dependency_dashboard_fails(tmp_path):
    report = _grade(tmp_path, renovate={"enabledManagers": ["custom.regex", "maven"],
                                        "maven": RENOVATE["maven"],
                                        "dependencyDashboard": False})
    assert report.exit_code == 1, report.text()
    assert "dependencyDashboard" in report.text()


# --------------------------------------------------------------------------- 7. not landed yet

def test_an_adopter_that_has_not_landed_the_lift_could_not_look_and_names_its_pull_request(tmp_path):
    estate = _estate(tmp_path)
    for p in [estate / "tuppence" / "gitops" / "apps" / "ledger.yaml",
              estate / "tuppence" / "apps" / "ledger" / "pom.xml"]:
        p.unlink()
    (estate / "tuppence" / "gitops" / "apps" / "kustomization.yaml").write_text(
        yaml.safe_dump({"resources": ["namespace.yaml"]}))
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=estate,
                               register_path=_register(tmp_path))
    assert report.exit_code == 3, report.text()
    assert report.rows[0].grade == "WAITS"
    assert "pull/99" in report.text()


def test_a_half_landed_lift_is_a_fail_not_a_wait(tmp_path):
    # The served workload arrived and the source tree did not: that is a broken lift, not a
    # lift that has yet to happen, and it must never be excused as one.
    estate = _estate(tmp_path)
    (estate / "tuppence" / "apps" / "ledger" / "pom.xml").unlink()
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=estate,
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()


# --------------------------------------------------------------------------- 8. a move, not a copy

def test_the_same_app_landing_in_a_second_adopter_fails(tmp_path):
    estate = _estate(tmp_path)
    other = estate / "ludlow" / "apps" / "ledger"
    other.mkdir(parents=True)
    (other / "pom.xml").write_text("<project/>\n")
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=estate,
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "ludlow" in report.text()


# --------------------------------------------------------------------------- 9. the hub keeps none

def test_a_copy_of_a_lifted_app_inside_the_hub_fails(tmp_path):
    hub = _hub(tmp_path)
    (hub / "apps" / "ledger").mkdir(parents=True)
    (hub / "apps" / "ledger" / "pom.xml").write_text("<project/>\n")
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "apps/ledger/pom.xml" in report.text()


def test_the_record_of_the_lift_is_not_itself_a_copy(tmp_path):
    # .scratch/ holds the ticket and the drift-review capture of the original org. Prose about a
    # lifted app is the record, not a working copy, and must not red the gate.
    hub = _hub(tmp_path)
    (hub / ".scratch" / "ecosystem").mkdir(parents=True)
    (hub / ".scratch" / "ecosystem" / "note.md").write_text("apps/ledger/pom.xml was lifted\n")
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 0, report.text()


# --------------------------------------------------------------------------- 10. the residual

def test_the_report_prints_the_residual_as_a_number(tmp_path):
    report = _grade(tmp_path)
    # 1 of 1 lifted app is still served an image built and published by the incumbent org. The
    # limit is counted on every run, so it cannot go stale in prose.
    assert "1 of 1" in report.text()
    assert "policy-as-versioned-flux" in report.text()


def test_no_estate_at_all_is_a_could_not_look(tmp_path):
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=tmp_path / "nope",
                               register_path=_register(tmp_path))
    assert report.exit_code == 3, report.text()
