"""Eco-system ticket 33: ledger, storefront and reports are lifted into their adopters.

The seam is `verify/lifted-apps/lifted_apps.py` — the grader that joins
`verify/lifted-apps/register.yaml` (which app went to which adopter, and with what) to what the
adopters' trees actually SERVE. `verify-lifted-apps.sh` runs it over the hub and the estate clone
and then runs kyverno over each served workload.

The rule these tests exist for: **name the served artefact and the operation that reaches it —
by reading them.** The operation is the adopter's own `gitops/flux-system/gotk-sync.yaml`: a
GitRepository pinned to `ref: {tag, commit}` and a Kustomization whose `spec.path` is the
directory Flux renders. The served artefact is that directory's `kustomization.yaml` and its
`resources[]`. Neither is a constant here (review 2026-09-08 F1: the first cut held the path as
prose and driftwood's file said `./apps`, a directory its remote does not have).

What these tests hold down:

  1. the register covers the three apps of the ticket, each in exactly one adopter;
  2. a served file the kustomization does not list FAILS — "the file is present" is a proxy;
  3. the Flux path is READ from gotk-sync.yaml: a path that is not the directory the check reads
     FAILS by name, and a missing gotk-sync.yaml FAILS;
  4. membership is graded twice: at the checkout, and at `git show <ref.tag>:<path>/
     kustomization.yaml`. The second is a COUNTED LIMIT, not a pass or fail, and a tag+commit
     pair that disagree FAILS;
  5. the version label is measured against the ADOPTER'S OWN composed artefact
     (`composed/orphan-guard.yaml`'s allowed array), never against a constant in this repository;
  6. the old `mycompany.com/` label anywhere in the lifted tree FAILS — that is the re-label;
  7. a source tree without its stack manifest FAILS — without it there is nothing for the
     stack's Renovate manager to read, so the lift would be manifest-only;
  8. a renovate.json that does not enable the stack's manager, points it at nothing the lift
     brought, leaves the dashboard off, or lacks the dependencyDashboardApproval packageRule
     FAILS; a glob-form pattern and a `./`-prefixed resource entry are NOT failures (F5);
  9. an adopter that has not landed the lift is a could-not-look that NAMES its pull request —
     never a silent pass and never a red for work that is proposed and unmerged;
 10. the same app landing in two adopters FAILS — a lift is a move, not a copy;
 11. a copy of a lifted app inside the HUB FAILS, wherever it is parked (F4): at the lifted
     path, under any `<app>/` directory, or by the stack manifest's identity;
 12. the residuals (whose registry still publishes the image; how many lifts the pinned tree
     does not list) are NUMBERS the report prints, not sentences in a document that go stale.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
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

POM = "<project>\n  <groupId>com.mycompany</groupId>\n  <artifactId>ledger</artifactId>\n</project>\n"

RENOVATE = {
    "enabledManagers": ["custom.regex", "maven"],
    "dependencyDashboard": True,
    "packageRules": [{"matchManagers": ["maven"], "dependencyDashboardApproval": True}],
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
  identity: '<groupId>com\\.mycompany</groupId>\\s*<artifactId>ledger</artifactId>'
"""

GOTK_SYNC = """\
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: {name: tuppence, namespace: flux-system}
spec:
  interval: 1m
  url: https://example.invalid/planted/tuppence
  ref:
    tag: v1.0.0
    commit: %(commit)s
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: {name: tuppence, namespace: flux-system}
spec:
  interval: 5m
  sourceRef: {kind: GitRepository, name: tuppence}
  path: %(path)s
  prune: true
"""

# The fixture's own git runs no hook: the owner's global core.hooksPath runs a rate-limited
# network scan on every commit, fixture commits included (estate-clone hazards, note 5).
NO_HOOKS = Path(tempfile.mkdtemp(prefix="lifted-apps-no-hooks-"))


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-c", f"core.hooksPath={NO_HOOKS}", "-c", "user.name=test",
         "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
         "-c", "tag.gpgsign=false", "-c", "init.defaultBranch=main", "-C", str(repo), *args],
        capture_output=True, text=True, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr}")
    return p.stdout.strip()


def _kustomization(resources: list[str]) -> str:
    return yaml.safe_dump({"apiVersion": "kustomize.config.k8s.io/v1beta1",
                           "kind": "Kustomization", "resources": resources})


def _estate(tmp_path: Path, *, served: str = SERVED, resources: list[str] | None = None,
            renovate: dict | None = None, stack: bool = True, flux_path: str = "./gitops/apps",
            sync: bool = True, pinned_has_lift: bool = False) -> Path:
    """One adopter, as a real git repository: v1.0.0 is tagged BEFORE the lift lands (the shape
    all three real adopters have today) unless pinned_has_lift moves the tag to the checkout."""
    estate = tmp_path / "estate"
    a = estate / "tuppence"
    (a / "composed" / "policies" / "v4.0.0").mkdir(parents=True)
    (a / "composed" / "policies" / "v4.0.0" / "require-nonroot.yaml").write_text("{}\n")
    (a / "composed" / "orphan-guard.yaml").write_text(ORPHAN_GUARD)
    (a / "gitops" / "apps").mkdir(parents=True)
    (a / "gitops" / "flux-system").mkdir(parents=True)
    (a / "gitops" / "apps" / "namespace.yaml").write_text(
        "apiVersion: v1\nkind: Namespace\nmetadata: {name: tuppence}\n")
    (a / "gitops" / "apps" / "kustomization.yaml").write_text(_kustomization(["namespace.yaml"]))
    _git(a, "init", "-q")
    _git(a, "add", "-A")
    _git(a, "commit", "-qm", "v1.0.0: before the lift")
    _git(a, "tag", "v1.0.0")
    # the checkout: the lift landed
    (a / "gitops" / "apps" / "ledger.yaml").write_text(served)
    res = ["namespace.yaml", "ledger.yaml"] if resources is None else resources
    (a / "gitops" / "apps" / "kustomization.yaml").write_text(_kustomization(res))
    (a / "apps" / "ledger").mkdir(parents=True)
    if stack:
        (a / "apps" / "ledger" / "pom.xml").write_text(POM)
    (a / "renovate.json").write_text(json.dumps(RENOVATE if renovate is None else renovate))
    _git(a, "add", "-A")
    _git(a, "commit", "-qm", "ticket 33: the lift")
    if pinned_has_lift:
        _git(a, "tag", "-f", "v1.0.0", "HEAD")
    commit = _git(a, "rev-parse", "v1.0.0^{commit}")
    if sync:
        (a / "gitops" / "flux-system" / "gotk-sync.yaml").write_text(
            GOTK_SYNC % {"commit": commit, "path": flux_path})
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
        assert lift.identity


# --------------------------------------------------------------------------- 2. the lift is real

def test_a_landed_lift_passes(tmp_path):
    report = _grade(tmp_path)
    assert report.exit_code == 0, report.text()
    assert report.rows[0].grade == "PASS"
    assert "on the path gitops/flux-system/gotk-sync.yaml reconciles (./gitops/apps)" in report.text()


def test_a_served_file_the_kustomization_does_not_list_fails(tmp_path):
    # The file is there; Flux's Kustomization renders resources[], so nobody is served it.
    report = _grade(tmp_path, resources=["namespace.yaml"])
    assert report.exit_code == 1, report.text()
    assert "not listed in gitops/apps/kustomization.yaml" in report.text()


# --------------------------------------------------------------------------- 3. the path is read

def test_a_flux_path_that_is_not_the_directory_the_check_reads_fails_by_name(tmp_path):
    # driftwood, 2026-09-08: gotk-sync.yaml said `path: ./apps` at a remote whose root holds
    # gitops/. The file the check read was served to nobody, and the check said "served".
    report = _grade(tmp_path, flux_path="./apps")
    assert report.exit_code == 1, report.text()
    assert "reconciles `path: ./apps`, not gitops/apps" in report.text()
    assert "served to nobody" in report.text()


def test_an_adopter_without_gotk_sync_fails(tmp_path):
    report = _grade(tmp_path, sync=False)
    assert report.exit_code == 1, report.text()
    assert "has no gitops/flux-system/gotk-sync.yaml" in report.text()


# --------------------------------------------------------------------------- 4. the pinned tree

def test_a_lift_the_pinned_tree_does_not_list_is_a_counted_limit_not_a_pass(tmp_path):
    report = _grade(tmp_path)
    assert report.exit_code == 0, report.text()
    assert "LIMIT  1 of 1 lifts are listed at main and not in the tree the GitRepository pins (v1.0.0): ledger->tuppence" in report.text()
    assert report.rows[0].pinned is not None and report.rows[0].pinned.state == "absent"


def test_a_lift_the_pinned_tree_lists_counts_zero(tmp_path):
    report = _grade(tmp_path, pinned_has_lift=True)
    assert report.exit_code == 0, report.text()
    assert "LIMIT  0 of 1 lifts are listed at main and not in the tree the GitRepository pins (v1.0.0)" in report.text()
    assert report.rows[0].pinned is not None and report.rows[0].pinned.state == "listed"


def test_a_tag_and_commit_that_disagree_fail(tmp_path):
    estate = _estate(tmp_path)
    sync = estate / "tuppence" / "gitops" / "flux-system" / "gotk-sync.yaml"
    sync.write_text(GOTK_SYNC % {"commit": "deadbeef" * 5, "path": "./gitops/apps"})
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=estate,
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "but the tag resolves to" in report.text()


def test_a_tag_this_clone_does_not_carry_is_counted_as_unreadable(tmp_path):
    estate = _estate(tmp_path)
    _git(estate / "tuppence", "tag", "-d", "v1.0.0")
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=estate,
                               register_path=_register(tmp_path))
    assert report.exit_code == 0, report.text()
    assert "LIMIT  1 of 1 pinned trees could not be read" in report.text()
    assert "tag v1.0.0 is not in this clone" in report.text()


# --------------------------------------------------------------------------- 5..8 label, tree, renovate

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
    report = _grade(tmp_path, renovate={**RENOVATE, "enabledManagers": ["custom.regex"]})
    assert report.exit_code == 1, report.text()
    assert "does not enable 'maven'" in report.text()


def test_a_manager_pointed_at_a_file_the_lift_did_not_bring_fails(tmp_path):
    # The manager is enabled and reads nothing that was lifted: a name in a list is not a bump
    # surface, and this is the shape a lift takes when the stack manifest moved and the config
    # was copied from another adopter.
    report = _grade(tmp_path, renovate={
        **RENOVATE, "maven": {"managerFilePatterns": ["/^apps/somewhere-else/pom\\.xml$/"]}})
    assert report.exit_code == 1, report.text()
    assert "none of which matches apps/ledger/pom.xml" in report.text()


def test_a_manager_with_no_file_patterns_at_all_fails(tmp_path):
    cfg = {k: v for k, v in RENOVATE.items() if k != "maven"}
    report = _grade(tmp_path, renovate=cfg)
    assert report.exit_code == 1, report.text()
    assert "managerFilePatterns" in report.text()


def test_a_glob_form_file_pattern_is_read_as_a_glob_not_a_regex(tmp_path):
    # Renovate reads `**/pom.xml` as a glob; the first cut fed it to re.search and crashed
    # (`nothing to repeat`, review F5).
    report = _grade(tmp_path, renovate={**RENOVATE, "maven": {"managerFilePatterns": ["**/pom.xml"]}})
    assert report.exit_code == 0, report.text()


def test_a_dot_slash_resource_entry_is_the_same_file(tmp_path):
    report = _grade(tmp_path, resources=["./namespace.yaml", "./ledger.yaml"])
    assert report.exit_code == 0, report.text()


def test_renovate_without_the_dependency_dashboard_fails(tmp_path):
    report = _grade(tmp_path, renovate={**RENOVATE, "dependencyDashboard": False})
    assert report.exit_code == 1, report.text()
    assert "dependencyDashboard" in report.text()


def test_renovate_without_the_dashboard_approval_rule_fails(tmp_path):
    # Ticket 33 decision 7 was prose until review F6: removing the packageRule graded 0.
    report = _grade(tmp_path, renovate={k: v for k, v in RENOVATE.items() if k != "packageRules"})
    assert report.exit_code == 1, report.text()
    assert "dependencyDashboardApproval" in report.text()


# --------------------------------------------------------------------------- 9. not landed yet

def test_an_adopter_that_has_not_landed_the_lift_could_not_look_and_names_its_pull_request(tmp_path):
    estate = _estate(tmp_path)
    for p in [estate / "tuppence" / "gitops" / "apps" / "ledger.yaml",
              estate / "tuppence" / "apps" / "ledger" / "pom.xml"]:
        p.unlink()
    (estate / "tuppence" / "gitops" / "apps" / "kustomization.yaml").write_text(
        _kustomization(["namespace.yaml"]))
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


# --------------------------------------------------------------------------- 10. a move, not a copy

def test_the_same_app_landing_in_a_second_adopter_fails(tmp_path):
    estate = _estate(tmp_path)
    other = estate / "ludlow" / "apps" / "ledger"
    other.mkdir(parents=True)
    (other / "pom.xml").write_text(POM)
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=estate,
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "ludlow" in report.text()


# --------------------------------------------------------------------------- 11. the hub keeps none

def test_a_copy_of_a_lifted_app_inside_the_hub_fails(tmp_path):
    hub = _hub(tmp_path)
    (hub / "apps" / "ledger").mkdir(parents=True)
    (hub / "apps" / "ledger" / "pom.xml").write_text("<project/>\n")
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "apps/ledger/pom.xml" in report.text()


@pytest.mark.parametrize("where", ["spikes/ledger", "twin/apps/ledger"])
def test_a_copy_parked_under_another_directory_fails(tmp_path, where):
    # Review F4: the path-literal rule let `spikes/ledger/pom.xml` pass.
    hub = _hub(tmp_path)
    (hub / where).mkdir(parents=True)
    (hub / where / "pom.xml").write_text("<project/>\n")
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert f"{where}/pom.xml" in report.text()


def test_a_stack_manifest_carrying_the_apps_identity_anywhere_fails(tmp_path):
    hub = _hub(tmp_path)
    (hub / "twin" / "lab").mkdir(parents=True)
    (hub / "twin" / "lab" / "pom.xml").write_text(POM)
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "carries ledger's identity" in report.text()


def test_a_manifest_pinning_the_served_image_anywhere_fails(tmp_path):
    hub = _hub(tmp_path)
    (hub / "twin" / "manifests").mkdir(parents=True)
    (hub / "twin" / "manifests" / "anything.yaml").write_text(SERVED)
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 1, report.text()
    assert "pins ledger's served image" in report.text()


def test_a_pom_that_is_not_the_apps_is_not_a_copy(tmp_path):
    hub = _hub(tmp_path)
    (hub / "twin" / "other").mkdir(parents=True)
    (hub / "twin" / "other" / "pom.xml").write_text(
        "<project>\n  <groupId>org.example</groupId>\n  <artifactId>other</artifactId>\n</project>\n")
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=_register(tmp_path))
    assert report.exit_code == 0, report.text()


def test_the_record_of_the_lift_is_not_itself_a_copy(tmp_path):
    # .scratch/ holds the ticket and the drift-review capture of the original org. Prose about a
    # lifted app is the record, not a working copy, and must not red the gate. Nor is the
    # register, which names the served image on purpose, nor the estate clone, which is where
    # the lifted apps are supposed to be.
    hub = _hub(tmp_path)
    (hub / ".scratch" / "ecosystem").mkdir(parents=True)
    (hub / ".scratch" / "ecosystem" / "note.md").write_text("apps/ledger/pom.xml was lifted\n")
    (hub / ".scratch" / "ecosystem" / "capture.yaml").write_text(SERVED)
    (hub / ".estate-clone" / "tuppence" / "apps" / "ledger").mkdir(parents=True)
    (hub / ".estate-clone" / "tuppence" / "apps" / "ledger" / "pom.xml").write_text(POM)
    register = hub / "verify" / "lifted-apps" / "register.yaml"
    register.parent.mkdir(parents=True)
    register.write_text(REGISTER_ONE)
    report = lifted_apps.grade(hub_root=hub, estate_root=_estate(tmp_path),
                               register_path=register)
    assert report.exit_code == 0, report.text()


# --------------------------------------------------------------------------- 12. the residuals

def test_the_report_prints_the_residual_as_a_number(tmp_path):
    report = _grade(tmp_path)
    # 1 of 1 lifted app is still served an image built and published by the incumbent org. The
    # limit is counted on every run, so it cannot go stale in prose.
    assert "LIMIT  1 of 1 lifted apps are still served an image" in report.text()
    assert "policy-as-versioned-flux" in report.text()


def test_no_estate_at_all_is_a_could_not_look(tmp_path):
    report = lifted_apps.grade(hub_root=_hub(tmp_path), estate_root=tmp_path / "nope",
                               register_path=_register(tmp_path))
    assert report.exit_code == 3, report.text()


def test_the_kyverno_plan_names_the_orphan_guard(tmp_path):
    plan = lifted_apps.kyverno_plan(_estate(tmp_path), _register(tmp_path))
    assert len(plan) == 1
    app, adopter, policies, guard, served = plan[0]
    assert (app, adopter) == ("ledger", "tuppence")
    assert policies.endswith("composed/policies/v4.0.0")
    assert guard.endswith("composed/orphan-guard.yaml")
    assert served.endswith("gitops/apps/ledger.yaml")
