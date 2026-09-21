"""Laya/loophole ticket 08: the two loophole candidates that survived, as checks.

`loophole` is non-deterministic, so under "derive what you assert" its output is a hypothesis and
never a finding. Ticket 07 ran one round against ADR-0022 and produced six candidates. This file
is what two of them became: the candidate was the pointer, the check is the finding. The other
four are recorded as discards in the ticket, with a reason each.

Neither survivor reproduces the wording of the scenario that pointed at it. Both were measured
and both came back with a different mechanism from the one the model named, which is the whole
reason the ticket refuses to catalogue a candidate unread.

  A. **`infra` is read by no served cage-tier body.** ADR-0022 gives a `platform`-role party the
     right to declare a Namespace at `infra`, and `platform/engine/namespaces.yaml` declares
     kube-system, flux-system and kyverno that way. No served policy body contains the word. The
     rung is absent from `variables.tier`'s membership test, so it falls to that test's else
     branch: `baseline` under v4.0.0, which all three adopters serve, and `isolated` under v5.0.0.
     Two consequences, both measured below under the pinned engine. A pod that CLAIMS a policy
     version in one of those three Namespaces lands on the LOOSEST rung, not on a substrate rung.
     A pod that claims none is skipped whether the declaration is there or not, so pulling the
     declaration changes nothing for CoreDNS -- and that is the hazard
     `distribution/verify-infra-declaration.sh` says it is the tripwire for.

  B. **A second governed Namespace document silences the hub's binding walk, at exit 0.**
     `platform/shift-left/tier_binding.py` returns 3 -- could-not-look -- when a party declares
     two governed Namespaces, because which one carries the party's tier is not the check's guess
     to make (ADR-0020). The adopter's own `shift-left.yml` turns that 3 into a failed pull
     request. The hub's estate walk, `verify/tier-binding/tier_binding_estate.py`, prints the
     party's SKIP line and CONTINUES, and exits 0 while any other party is bound. `verify-all.sh`
     grades a script by its exit code, so the gate reads PASS for an estate in which one party's
     cage is unobserved.

The `infra` legs that need an engine run under the version the release workflows pin, 1.18.2.
A different CLI is a could-not-look and says so: 1.19.1 refuses to compile the served body at all
(`expected type 'string' but found 'dyn'`), and grading that as a passing fixture would be this
file asserting a property it never looked at.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

HUB = Path(__file__).resolve().parent.parent
ESTATE = HUB / ".estate-clone"
PLATFORM = ESTATE / "platform"
ADOPTERS = ("driftwood", "ludlow", "tuppence")
PINNED_KYVERNO = "1.18.2"

# The rungs `variables.tier`'s membership test admits. `infra` is deliberately not among them
# (wargamer.LADDER says so too), which is exactly why the else branch is what an `infra`
# Namespace gets.
SELECTABLE = ("baseline", "restricted", "quarantine", "isolated")


def _served_cage_tier_bodies() -> list[Path]:
    """Every copy of cage-tier anyone serves: the hub's released trees, the authoring tree, and
    each adopter's composed copy. `.work/` is a builder's scratch tree and is not served."""
    found: list[Path] = []
    for pattern in ("distribution/policies/v*/cage-tier.yaml", "graded/policies/cage-tier.yaml"):
        found += [p for p in PLATFORM.glob(pattern)
                  if ".work" not in p.parts and "vselfcheck" not in p.parts]
    for adopter in ADOPTERS:
        found += sorted((ESTATE / adopter).glob("composed/policies/v*/cage-tier.yaml"))
    return sorted(found)


def _without_comments(body: Path) -> str:
    """The policy BODY, with the prose stripped. `verify-infra-declaration.sh` had to learn the
    same lesson on 2026-09-04: its own changelog comment quoted the shape it had replaced, and
    the check read the prose and reported an already-flipped body as unflipped."""
    return "\n".join(re.sub(r"#.*$", "", line) for line in body.read_text(encoding="utf-8").splitlines())


def _policy_version(body: Path) -> str:
    doc = yaml.safe_load(body.read_text(encoding="utf-8"))
    return doc["metadata"]["labels"]["policy-as-versioned.dev/policy-version"]


def _kyverno() -> str:
    """The pinned CLI, or a named could-not-look. Never another version: 1.19.1 does not compile
    the served body, so a skip here is the honest verdict and a pass would be a lie."""
    exe = shutil.which("kyverno")
    if exe is None:
        pytest.skip("no kyverno CLI on PATH -- the served cage body needs an engine to render")
    out = subprocess.run([exe, "version"], capture_output=True, text=True).stdout
    if PINNED_KYVERNO not in out:
        pytest.skip(f"kyverno on PATH is not the pinned {PINNED_KYVERNO} that release.yml "
                    f"installs -- {out.splitlines()[0] if out else 'no version line'}")
    return exe


def _render(tmp: Path, exe: str, body: Path, namespace_labels: dict, pod_labels: dict) -> dict:
    """One pod through one served cage-tier body, against one Namespace. Returns the mutated pod,
    or {} when the policy skipped it."""
    values = {"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Values",
              "namespaces": [{"apiVersion": "v1", "kind": "Namespace",
                              "metadata": {"name": "substrate", "labels": namespace_labels}}]}
    pod = {"apiVersion": "v1", "kind": "Pod",
           "metadata": {"name": "probe", "namespace": "substrate", "labels": pod_labels},
           "spec": {"containers": [{"name": "app", "image": "nginx"}]}}
    (tmp / "values.yaml").write_text(yaml.safe_dump(values))
    (tmp / "pod.yaml").write_text(yaml.safe_dump(pod))
    run = subprocess.run([exe, "apply", str(body), "--resource", str(tmp / "pod.yaml"),
                          "--values-file", str(tmp / "values.yaml")],
                         capture_output=True, text=True, cwd=tmp)
    assert "error: 0" in run.stdout, f"the engine refused the served body:\n{run.stdout}{run.stderr}"
    if "skipped mutate policy" in run.stdout:
        return {}
    # The engine prints `policy <name> applied to <ns>/Pod/<name>:` and then the mutated object.
    blocks = re.split(r"^policy .* applied to .*:$", run.stdout, flags=re.M)
    for block in blocks[1:]:
        for doc in yaml.safe_load_all(block):
            if isinstance(doc, dict) and doc.get("kind") == "Pod":
                return doc
    raise AssertionError(f"no mutated pod came back:\n{run.stdout}")


# --------------------------------------------------------------------------------------------
# A. `infra` is a declaration no served body reads
# --------------------------------------------------------------------------------------------

def test_the_platform_declares_three_namespaces_at_infra_and_governs_none_of_them():
    """The premise both legs below rest on, read rather than assumed."""
    docs = list(yaml.safe_load_all((PLATFORM / "engine" / "namespaces.yaml").read_text()))
    declared = {d["metadata"]["name"]: d["metadata"].get("labels", {}) for d in docs if d}
    assert set(declared) == {"kyverno", "flux-system", "kube-system"}
    for name, labels in declared.items():
        assert labels.get("posture.acme.io/tier") == "infra", name
        assert "policy-as-versioned.dev/governed" not in labels, \
            f"{name} is governed after all -- leg A's else branch is the UNGOVERNED one"


def test_infra_appears_in_no_served_cage_tier_body():
    """Read as text, over every copy anyone serves. The hub's own
    `distribution/verify-infra-declaration.sh` calls its proof-3 scan a live tripwire for CoreDNS;
    this is the sentence that tripwire assumes and nothing states."""
    bodies = _served_cage_tier_bodies()
    assert len(bodies) >= 4, f"only {len(bodies)} served cage-tier bodies found -- the scan is blind"
    carrying = [str(p.relative_to(HUB)) for p in bodies if "infra" in _without_comments(p)]
    assert carrying == [], f"a served body reads `infra` after all: {carrying}"


@pytest.mark.parametrize("adopter", ADOPTERS)
def test_a_claiming_pod_in_an_infra_namespace_lands_on_the_loosest_rung(adopter, tmp_path):
    """The rung an adopter's SERVED body gives a pod in the platform's substrate Namespaces.
    Not `infra`, and not the bottom rung either: the loosest one on the ladder."""
    exe = _kyverno()
    bodies = sorted((ESTATE / adopter).glob("composed/policies/v*/cage-tier.yaml"))
    assert bodies, f"{adopter} serves no cage-tier body"
    for body in bodies:
        version = _policy_version(body)
        pod = _render(tmp_path, exe, body,
                      {"platform.acme.io/plane": "engine", "posture.acme.io/tier": "infra"},
                      {"policy-as-versioned.dev/policy-version": version})
        tier = pod["metadata"]["labels"]["posture.acme.io/tier"]
        assert tier in SELECTABLE, f"{adopter} {version}: rendered {tier!r}, which is not a rung"
        assert tier != "infra"
        assert tier == "baseline", (
            f"{adopter} {version}: an ungoverned `infra` Namespace rendered {tier!r}. The finding "
            f"was `baseline`, the LOOSEST rung, measured 2026-09-21. If this now reads `isolated` "
            f"the adopter has re-pinned past the 2026-09-04 flip and the hole has closed -- "
            f"re-state the catalogue row rather than loosening this assertion.")
        assert pod["spec"]["priorityClassName"].startswith("cage-baseline-")


def test_pulling_the_infra_declaration_changes_nothing_for_an_unclaimed_pod(tmp_path):
    """CoreDNS claims no policy version, so cage-tier's own matchConditions skip it -- with the
    declaration and without it, under BOTH the flipped and the unflipped body. So the
    configuration `verify-infra-declaration.sh` says it is the tripwire for, "CoreDNS lands in
    isolated and the cluster stops", is not a configuration any served body produces."""
    exe = _kyverno()
    bodies = [p for p in PLATFORM.glob("distribution/policies/v*/cage-tier.yaml")
              if ".work" not in p.parts]
    assert bodies
    for body in bodies:
        with_label = _render(tmp_path, exe, body,
                             {"platform.acme.io/plane": "engine", "posture.acme.io/tier": "infra"},
                             {})
        without_label = _render(tmp_path, exe, body, {"platform.acme.io/plane": "engine"}, {})
        assert with_label == {} == without_label, (
            f"{body.name} {_policy_version(body)}: an unclaimed pod was caged -- the declaration "
            f"is doing work after all, and this leg of the finding has closed")


# --------------------------------------------------------------------------------------------
# B. a second governed Namespace document silences the hub's walk, at exit 0
# --------------------------------------------------------------------------------------------

NAMESPACE = """\
apiVersion: v1
kind: Namespace
metadata:
  name: {name}
  labels:
    policy-as-versioned.dev/governed: "true"
    posture.acme.io/tier: "{tier}"
"""
PRICE = {"source": "feeds", "kind": "feed", "name": "threat-register",
         "proposed_tier": "isolated", "changed": False}


def _plant(root: Path, ambiguous: str | None) -> Path:
    """Two parties, each bound, against the REAL platform checkout. `ambiguous` names the one
    party that also declares a second governed Namespace."""
    estate = root / "estate"
    estate.mkdir()
    (estate / "platform").symlink_to(PLATFORM)
    for party in ("driftwood", "ludlow"):
        apps = estate / party / "gitops" / "apps"
        apps.mkdir(parents=True)
        body = NAMESPACE.format(name=party, tier="isolated")
        if party == ambiguous:
            body += "---\n" + NAMESPACE.format(name=f"{party}-second", tier="baseline")
        (apps / "namespace.yaml").write_text(body)
        (estate / party / "composed").mkdir()
        (estate / party / "composed" / "evidence.json").write_text(json.dumps({"prices": [PRICE]}))
    return estate


def _walk(estate: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(HUB / "verify" / "tier-binding" / "tier_binding_estate.py"),
         "check", "--estate-clone", str(estate)],
        capture_output=True, text=True)


def test_the_hub_walk_passes_a_clean_planted_estate(tmp_path):
    """The control. Without it, leg B's exit 0 could be the walk passing everything."""
    run = _walk(_plant(tmp_path, ambiguous=None))
    assert run.returncode == 0, run.stdout + run.stderr
    assert len(re.findall(r"^PASS: ", run.stdout, re.M)) == 2, run.stdout


def test_a_second_governed_namespace_document_silences_one_party_and_the_walk_still_exits_zero(tmp_path):
    """The finding. driftwood's binding goes unobserved, ludlow's passes, and the script hands
    `talk/verify-all.sh` the exit code it grades PASS on."""
    run = _walk(_plant(tmp_path, ambiguous="driftwood"))
    assert "SKIP: driftwood: 2 governed Namespace declarations" in run.stdout, run.stdout
    assert re.search(r"^PASS: ludlow: ", run.stdout, re.M), run.stdout
    assert run.returncode == 0, (
        "the estate walk now refuses an unobserved party -- the hole has closed and this "
        "reproduction should become the repair's regression test")


def test_verify_all_grades_a_script_by_its_exit_code_alone():
    """Why leg B's exit 0 is the whole finding: the gate never reads the per-party SKIP line."""
    gate = (HUB / "talk" / "verify-all.sh").read_text(encoding="utf-8")
    assert "exit 3" in gate and "SKIP" in gate
    walk = (HUB / "verify" / "tier-binding" / "tier_binding_estate.py").read_text(encoding="utf-8")
    assert "return 1 if failed else 0" in walk, \
        "the walk's return no longer reads this way -- re-measure before trusting leg B"
