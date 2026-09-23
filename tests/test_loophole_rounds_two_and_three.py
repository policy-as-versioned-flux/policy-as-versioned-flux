"""Eco-system ticket 116: the twelve loophole candidates of rounds two and three, checked.

Ticket 11 of the Laya and loophole map ran two more loophole rounds against ADR-0022 and
recorded twelve candidates that nobody had checked against the code. ADR-0030 says the tool is a
pointer generator: test the place a candidate points at, never its sentence, and count the
survival rate on the candidates as stated. This file is that check. Every candidate carries a
verdict in `VERDICTS`, and each verdict names the test in this file (or in
`tests/test_cage_ladder_holes.py`) that holds the fact it rests on.

One candidate survived.

  S. **A Namespace that carries none of the estate's labels is outside the cage and outside the
     price.** Round two's `loophole-2` said the cage only reaches Namespaces a discovery list
     enumerates. There is no discovery list. What the cage reaches is set by two labels: a pod
     is caged when it claims a policy version, or when its Namespace is governed. What the
     composition prices is set by a third: a Namespace is an "ungoverned namespace", priced as a
     share of the adopter's uncaged residual (ADR-0026), only when it carries the institution
     label. A Namespace that carries none of the three, holding a pod that claims nothing, is
     touched by no served policy and listed by no price. Which of its own Namespaces carry the
     institution label is the adopter's own choice, and nothing checks it. ADR-0022 says
     "silence buys nothing anywhere". Here silence buys both. Graduated as eco-system ticket 119.

Ticket 119 repaired it with a price, not a cage (delegated, ADR-0025). The composition now
treats every Namespace an adopter's repo declares or names as an institution Namespace, except
the substrate the platform declares `infra` in its own `engine/namespaces.yaml`, which no adopter
can write. So a Namespace with no label is an ungoverned Namespace and prices like any other.
The cage is left where it is, on purpose: at admission the only facts about a Namespace are its
name and its labels, and a cage that reached an unlabelled Namespace would have to tell kube-system
from an adopter's Namespace by one of them (ticket 113, proof 3). The engine leg is now the
regression test of that decision, and the price legs are the regression tests of the repair.

Counting rule (delegated, ticket 116): a candidate survives when checking the place it points at
finds a real defect that no earlier survivor or ticket already holds. That is the rule ticket 08
applied to round one, whose `overreach-5` pointed at the place its `loophole-2` had already
survived on, and the rule ticket 116 gives for round three's `loophole-1`. Two more candidates
here point at the survivor's place and are counted as discards, so the survival rate counts
defects found per candidate and not echoes of one defect.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

from test_cage_ladder_holes import (
    ADOPTERS,
    CLAIM,
    ESTATE,
    HUB,
    PLATFORM,
    _claim,
    _declared_versions,
    _delivered_bodies,
    _kyverno,
    _mutated_pod,
    _rung,
    _without_comments,
)

GOVERNED = "policy-as-versioned.dev/governed"
INSTITUTION = "policy-as-versioned.dev/institution"
TIER = "posture.acme.io/tier"
RESEARCH = HUB / ".scratch" / "laya-loophole" / "research"
POLICY_KINDS = {"MutatingPolicy", "ValidatingPolicy", "GeneratingPolicy"}

# The survival counting, in one place. Round one's two survivors are ticket 08's
# (`tests/test_cage_ladder_holes.py`); rounds two and three are this file's.
ROUND_ONE = {"checked": 6, "survived": 2}

# (round, candidate) -> (verdict, the test that holds the fact, the fact in one line).
VERDICTS: dict[tuple[str, str], tuple[str, str, str]] = {
    ("two", "loophole-1"): (
        "discard", "test_a_self_asserted_platform_role_is_read_by_nothing_that_places_a_pod",
        "the platform role is read from platform/party.yaml alone, and no served body reads a role"),
    ("two", "loophole-2"): (
        "survivor", "test_the_composition_prices_a_namespace_that_omits_the_institution_label",
        "no discovery list exists, but a Namespace with no label was outside the cage and the price;"
        " ticket 119 prices it"),
    ("two", "loophole-3"): (
        "discard", "test_a_recreated_namespace_is_bound_to_the_price_not_to_its_history",
        "the binding check compares the declaration with the price, never with an earlier label"),
    ("two", "overreach-4"): (
        "discard", "test_an_unclaimed_pod_in_an_unlabelled_namespace_stays_outside_the_cage_by_decision",
        "an ad hoc Namespace does not cage an unclaimed debug pod at all; the survivor's place"),
    ("two", "overreach-5"): (
        "discard", "test_loosening_is_a_recorded_decision_and_the_binding_check_refuses_it",
        "ADR-0022 records no fast loosening as the decision, and the binding check enforces it"),
    ("two", "overreach-6"): (
        "discard", "test_an_unclaimed_pod_in_a_governed_namespace_is_told_why",
        "the pod is not silent: the served guard refuses it by name, the next one reports why"),
    ("three", "loophole-1"): (
        "discard", "test_the_tripwire_names_exactly_the_bodies_the_engine_cages_loosely",
        "false as written against ADR-0022; the place is eco-system ticket 113's"),
    ("three", "loophole-2"): (
        "discard", "test_an_infra_label_moves_no_cage_on_any_namespace",
        "no served body reads `infra`, so declaring it on any Namespace moves no cage"),
    ("three", "loophole-3"): (
        "discard", "test_a_recreated_namespace_is_bound_to_the_price_not_to_its_history",
        "the binding check compares the declaration with the price, never with an earlier label"),
    ("three", "overreach-4"): (
        "discard", "test_restoring_a_dropped_claim_is_a_pod_edit_the_binding_check_never_reads",
        "the claim is a pod label; putting it back needs no tier edit and meets no binding check"),
    ("three", "overreach-5"): (
        "discard", "test_an_unclaimed_pod_in_an_unlabelled_namespace_stays_outside_the_cage_by_decision",
        "a sandbox Namespace does not cage an unclaimed pod at all; the survivor's place"),
    ("three", "overreach-6"): (
        "discard", "test_the_infra_tripwire_gates_no_unit_merge",
        "the tripwire runs in the hub's gate only; no unit's workflow calls it"),
}


# --------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------

def _load(name: str, path: Path, *extra_paths: Path) -> ModuleType:
    for extra in extra_paths:
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _policy_docs(path: Path) -> list[dict[str, Any]]:
    return [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8"))
            if isinstance(d, dict) and d.get("kind") in POLICY_KINDS]


def _cut_versions() -> list[str]:
    """The declared lines that carry a commit: the ones the machinery's allow-list ranges over."""
    doc = yaml.safe_load((PLATFORM / "distribution" / "versions.yaml").read_text())
    return [v["version"] for block in doc["spec"]["inputs"] for v in block["versions"]
            if v.get("commit")]


def _machinery() -> list[dict[str, Any]]:
    """The platform machinery the ResourceSet renders beside the policy lines, read through the
    platform's own reader of the live template."""
    resourceset = _load("_t116_resourceset", PLATFORM / "distribution" / "resourceset.py")
    allowed = "[" + ", ".join(f"'{v}'" for v in _cut_versions()) + "]"
    docs = resourceset.guard_docs(PLATFORM / "distribution" / "versions.yaml", allowed)
    return [d for d in docs.values() if d.get("kind") in POLICY_KINDS]


def _served_sets() -> dict[str, list[dict[str, Any]]]:
    """Every policy document anyone serves or is delivered, grouped by who holds it. Each
    adopter's composed tree is what its cluster serves today. The platform's declared lines, its
    graded authoring copy and its machinery are what the next recomposition delivers."""
    sets: dict[str, list[dict[str, Any]]] = {}
    for adopter in ADOPTERS:
        composed = ESTATE / adopter / "composed"
        files = sorted(composed.glob("policies/v*/*.yaml"))
        files += [composed / "governed-namespace-guard.yaml", composed / "orphan-guard.yaml"]
        sets[adopter] = [d for f in files if f.is_file() for d in _policy_docs(f)]
    for version in _declared_versions():
        tree = PLATFORM / "distribution" / "policies" / f"v{version}"
        sets[f"platform v{version}"] = [d for f in sorted(tree.glob("*.yaml")) for d in _policy_docs(f)]
    sets["platform graded"] = [d for f in sorted((PLATFORM / "graded" / "policies").glob("*.yaml"))
                               for d in _policy_docs(f)]
    sets["platform machinery"] = _machinery()
    for name, docs in sets.items():
        assert docs, f"{name}: no policy document found -- the scan is blind"
    return sets


def _apply_one(tmp: Path, exe: str, policy: dict[str, Any], namespace_labels: dict[str, str],
               pod_labels: dict[str, str]) -> tuple[dict[str, Any], int, str]:
    """One policy document against one pod in one Namespace. Returns the pod as the policy
    changed it ({} when unchanged), the number of failed validations, and the engine's output."""
    values = {"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Values",
              "namespaces": [{"apiVersion": "v1", "kind": "Namespace",
                              "metadata": {"name": "scratch", "labels": namespace_labels}}]}
    pod = {"apiVersion": "v1", "kind": "Pod",
           "metadata": {"name": "probe", "namespace": "scratch", "labels": pod_labels},
           "spec": {"containers": [{"name": "app", "image": "nginx"}]}}
    (tmp / "policy.yaml").write_text(yaml.safe_dump(policy))
    (tmp / "values.yaml").write_text(yaml.safe_dump(values))
    (tmp / "pod.yaml").write_text(yaml.safe_dump(pod))
    run = subprocess.run([exe, "apply", str(tmp / "policy.yaml"), "--resource", str(tmp / "pod.yaml"),
                          "--values-file", str(tmp / "values.yaml")],
                         capture_output=True, text=True, cwd=tmp)
    out = run.stdout + run.stderr
    assert "error: 0" in run.stdout, f"the engine refused {policy['metadata']['name']}:\n{out}"
    summary = re.search(r"fail: (\d+)", run.stdout)
    assert summary, out
    changed = _mutated_pod(run.stdout, pod) if policy["kind"] == "MutatingPolicy" else {}
    return changed, int(summary.group(1)), out


def _requires_a_caged_pod(policy: dict[str, Any]) -> bool:
    """A generating policy fires only for a pod the cage has already caged."""
    return any("posture.acme.io/caged" in c.get("expression", "") and "'true'" in c.get("expression", "")
               for c in policy["spec"].get("matchConditions") or [])


def _outcomes(tmp: Path, exe: str, namespace_labels: dict[str, str],
              pod_labels: dict[str, str]) -> dict[str, list[str]]:
    """What every served policy does to one pod: the names that caged it and the names that
    failed it, per set. Generating policies are read statically: every one needs a caged pod."""
    touched: dict[str, list[str]] = {}
    for name, docs in _served_sets().items():
        hits = []
        for doc in docs:
            if doc["kind"] == "GeneratingPolicy":
                assert _requires_a_caged_pod(doc), f"{name}: {doc['metadata']['name']} fires on an uncaged pod"
                continue
            changed, failed, _ = _apply_one(tmp, exe, doc, namespace_labels, pod_labels)
            if changed:
                hits.append(f"{doc['metadata']['name']} caged it at "
                            f"{changed['metadata'].get('labels', {}).get(TIER)!r}")
            if failed:
                hits.append(f"{doc['metadata']['name']} failed it")
        touched[name] = hits
    return touched


def _composition() -> ModuleType:
    compose = PLATFORM / "compose"
    return _load("_t116_composition", compose / "composition.py", compose)


def _adopter_repo(root: Path, side_labels: dict[str, str]) -> Path:
    """A planted adopter repo: its governed home Namespace, and a second Namespace `side`
    carrying `side_labels`, with one Deployment in each. No claim on either pod template."""
    repo = root / "adopter"
    (repo / "gitops" / "apps").mkdir(parents=True)
    home = {"apiVersion": "v1", "kind": "Namespace",
            "metadata": {"name": "home", "labels": {INSTITUTION: "adopter", GOVERNED: "true"}}}
    side = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "side", "labels": side_labels}}
    (repo / "gitops" / "apps" / "namespace.yaml").write_text(yaml.safe_dump_all([home, side]))
    for ns in ("home", "side"):
        deploy = {"apiVersion": "apps/v1", "kind": "Deployment",
                  "metadata": {"name": f"{ns}-app", "namespace": ns},
                  "spec": {"template": {"spec": {"containers": [{"name": "app", "image": "nginx"}]}}}}
        (repo / "gitops" / "apps" / f"{ns}-app.yaml").write_text(yaml.safe_dump(deploy))
    return repo


def _tier_binding(tmp: Path, namespace_yaml: str, proposed: str,
                  party_yaml: str | None = None) -> subprocess.CompletedProcess[str]:
    adopter = tmp / "adopter"
    (adopter / "gitops" / "apps").mkdir(parents=True, exist_ok=True)
    (adopter / "gitops" / "apps" / "namespace.yaml").write_text(namespace_yaml)
    if party_yaml is not None:
        (adopter / "party.yaml").write_text(party_yaml)
    (tmp / "evidence.json").write_text(json.dumps({"prices": [
        {"source": "feeds", "kind": "feed", "name": "threat-register",
         "proposed_tier": proposed, "changed": False}]}))
    return subprocess.run(["python3", str(PLATFORM / "shift-left" / "tier_binding.py"), "check",
                           "--evidence", str(tmp / "evidence.json"), "--adopter-dir", str(adopter)],
                          capture_output=True, text=True)


def _namespace(name: str, labels: dict[str, str]) -> str:
    return yaml.safe_dump({"apiVersion": "v1", "kind": "Namespace",
                           "metadata": {"name": name, "labels": labels}})


# --------------------------------------------------------------------------------------------
# S. the survivor: a Namespace with none of the labels was outside the cage and the price.
#    Ticket 119 prices it and keeps the cage where it is.
# --------------------------------------------------------------------------------------------

SUBSTRATE = {"kube-system", "flux-system", "kyverno"}


def test_an_unclaimed_pod_in_an_unlabelled_namespace_stays_outside_the_cage_by_decision(tmp_path):
    """The engine half of the survivor, kept as the regression test of ticket 119's decision.
    Every policy document each adopter serves today, and every one the platform delivers next,
    leaves an unclaimed pod in an unlabelled Namespace exactly as it arrived. That is the same
    fact that keeps CoreDNS running (ticket 113, proof 3): at admission an unlabelled adopter
    Namespace and kube-system look alike. The repair is the price, in the legs below."""
    exe = _kyverno()
    touched = _outcomes(tmp_path, exe, {}, {})
    assert set(touched) >= set(ADOPTERS) | {"platform machinery", "platform graded"}
    assert all(hits == [] for hits in touched.values()), f"a served policy reached the pod: {touched}"


def test_the_same_pod_in_a_governed_namespace_is_reached(tmp_path):
    """The control. Without it the leg above could be a probe that sees no policy at all. Govern
    the Namespace and every adopter's served guard fails the pod, and the platform's machinery
    cages it on the bottom rung."""
    exe = _kyverno()
    touched = _outcomes(tmp_path, exe, {GOVERNED: "true"}, {})
    for adopter in ADOPTERS:
        assert "governed-namespace-requires-claim failed it" in touched[adopter], touched[adopter]
    assert "governed-namespace-requires-claim caged it at 'isolated'" in touched["platform machinery"], \
        touched["platform machinery"]


def test_the_composition_prices_a_namespace_that_omits_the_institution_label(tmp_path):
    """The price half of the survivor, flipped by ticket 119. A Namespace the adopter declares
    with no label is an ungoverned Namespace, its workloads enter the share's denominator, and it
    carries a price. The same Namespace with the institution label prices the same way, so the
    label no longer decides whether a Namespace is priced."""
    composition = _composition()
    bare = _adopter_repo(tmp_path / "bare", {})
    institution, workloads = composition._namespace_facts(bare)
    assert institution == {"home": True, "side": False} and workloads == {"home": 1, "side": 1}, \
        (institution, workloads)
    assert composition.ungoverned_namespaces(bare) == ["side"], "an unlabelled Namespace is still unpriced"

    labelled = _adopter_repo(tmp_path / "labelled", {INSTITUTION: "adopter"})
    assert composition.ungoverned_namespaces(labelled) == ["side"], \
        "the control: the same Namespace with the institution label is an ungoverned namespace"
    assert composition._namespace_facts(labelled) == (institution, workloads), \
        "the institution label changed what the walk reads"


def test_a_namespace_only_a_workload_names_is_priced(tmp_path):
    """The adopter need not declare a Namespace at all: a workload that names one is enough. This
    is tuppence's `openbao` Job's shape, planted."""
    composition = _composition()
    repo = _adopter_repo(tmp_path, {})
    job = {"apiVersion": "batch/v1", "kind": "Job", "metadata": {"name": "setup", "namespace": "elsewhere"},
           "spec": {"template": {"spec": {"containers": [{"name": "app", "image": "nginx"}]}}}}
    (repo / "reset.yaml").write_text(yaml.safe_dump(job))
    assert composition.ungoverned_namespaces(repo) == ["elsewhere", "side"]


def test_the_substrate_the_composition_skips_is_the_platform_infra_declaration(tmp_path):
    """What keeps the price off kube-system, flux-system and kyverno is the platform's own `infra`
    declaration, read from the platform tree. An adopter cannot add to it: the same label on the
    adopter's own Namespace moves nothing, and the Namespace prices like any other."""
    composition = _composition()
    assert composition.substrate_namespaces() == SUBSTRATE
    declared = {d["metadata"]["name"] for d in yaml.safe_load_all(
                    (PLATFORM / "engine" / "namespaces.yaml").read_text(encoding="utf-8"))
                if isinstance(d, dict) and d.get("kind") == "Namespace"
                and (d["metadata"].get("labels") or {}).get(TIER) == "infra"}
    assert declared == SUBSTRATE, declared

    repo = _adopter_repo(tmp_path, {TIER: "infra"})
    for ns in sorted(SUBSTRATE):
        deploy = {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "x", "namespace": ns},
                  "spec": {"template": {"spec": {"containers": [{"name": "app", "image": "nginx"}]}}}}
        (repo / f"in-{ns}.yaml").write_text(yaml.safe_dump(deploy))
    (repo / "kube-system.yaml").write_text(_namespace("kube-system", {}))
    institution, workloads = composition._namespace_facts(repo)
    assert set(institution) == {"home", "side"}, institution
    assert all(workloads[ns] == 1 for ns in SUBSTRATE), workloads
    assert composition.ungoverned_namespaces(repo) == ["side"], "an adopter's own `infra` label bought an exemption"


def test_tuppence_openbao_job_is_priced_by_the_next_composition():
    """Ticket 119's decision for the live case. tuppence's `openbao-reset-role` Job runs in the
    platform's `openbao` Namespace, which tuppence never declares, and claims no version. It is
    neither moved nor claimed: the next composition prices `openbao` as a tuppence ungoverned
    Namespace, and `tuppence-reset` keeps its place."""
    composition = _composition()
    tuppence = ESTATE / "tuppence"
    job = yaml.safe_load((tuppence / "reset" / "openbao-role.yaml").read_text(encoding="utf-8"))
    assert job["kind"] == "Job" and job["metadata"]["namespace"] == "openbao"
    assert CLAIM not in str(job["spec"]["template"]), "the Job claims a version now; the decision is stale"
    ungoverned = composition.ungoverned_namespaces(tuppence)
    assert {"openbao", "tuppence-reset"} <= set(ungoverned), ungoverned
    assert "openbao" not in composition.substrate_namespaces()


# --------------------------------------------------------------------------------------------
# the discards, each with the fact that makes it false
# --------------------------------------------------------------------------------------------

def test_a_self_asserted_platform_role_is_read_by_nothing_that_places_a_pod(tmp_path):
    """Round two, `loophole-1`. The `platform` role grants the `infra` declaration, and the one
    reader of that grant is the tripwire, which opens platform/party.yaml and no other file. No
    served body reads a role at all. An adopter that writes `platform` into its own party.yaml
    and declares a governed Namespace `infra` is bound as the `isolated` it renders."""
    tripwire = (PLATFORM / "distribution" / "verify-infra-declaration.sh").read_text(encoding="utf-8")
    reader = tripwire[tripwire.index("def platform_role_ok"):]
    reader = reader[:reader.index("\ndef ", 1)]
    assert 'os.path.join(platform_dir, "party.yaml")' in reader, reader
    for body in _delivered_bodies():
        text = _without_comments(body)
        assert "roles" not in text and "party.yaml" not in text, f"{body} reads a party artefact"
    run = _tier_binding(tmp_path, _namespace("x", {GOVERNED: "true", TIER: "infra"}), "isolated",
                        party_yaml="party: x\nroles: [adopter, platform]\n")
    assert run.returncode == 0 and "declares 'infra' (renders 'isolated'" in run.stdout, run.stdout + run.stderr


def test_a_recreated_namespace_is_bound_to_the_price_not_to_its_history(tmp_path):
    """Round two `loophole-3` and round three `loophole-3`. Both say delete-and-recreate resets a
    tighten-only memory kept per Namespace. There is no such memory to reset: the binding check
    compares the declaration with the party's strictest priced line, whatever the Namespace is
    called. A new name declared looser fails. A new Namespace with no tier renders `isolated`."""
    renamed = _tier_binding(tmp_path / "renamed",
                            _namespace("payments-v48", {GOVERNED: "true", TIER: "baseline"}), "isolated")
    assert renamed.returncode == 1 and "LOOSER than strictest priced line 'isolated'" in renamed.stdout, \
        renamed.stdout + renamed.stderr
    untiered = _tier_binding(tmp_path / "untiered", _namespace("payments-v48", {GOVERNED: "true"}), "isolated")
    assert untiered.returncode == 0 and "isolated by default" in untiered.stdout, untiered.stdout
    exe = _kyverno()
    for body in _delivered_bodies():
        assert _rung(tmp_path, exe, body, {GOVERNED: "true"}) == "isolated", body


def test_loosening_is_a_recorded_decision_and_the_binding_check_refuses_it(tmp_path):
    """Round two, `overreach-5`. True that no fast loosening path exists, and ADR-0022 records
    that as the decision in its own words. The binding check holds it."""
    adr = (HUB / "docs" / "adr" / "0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md")
    assert "Loosening is not implemented, and that is the decision, not an omission." in adr.read_text()
    run = _tier_binding(tmp_path, _namespace("team", {GOVERNED: "true", TIER: "baseline"}), "restricted")
    assert run.returncode == 1 and "LOOSER" in run.stdout, run.stdout + run.stderr


def test_an_unclaimed_pod_in_a_governed_namespace_is_told_why(tmp_path):
    """Round two, `overreach-6`, which says the bottom rung arrives with no message beyond a label
    diff. Each adopter's served guard refuses the pod and names the missing claim. The platform's
    next machinery cages it and its report names the claim and the reason."""
    exe = _kyverno()
    sets = _served_sets()
    for adopter in ADOPTERS:
        guard = next(d for d in sets[adopter] if d["metadata"]["name"] == "governed-namespace-requires-claim")
        _, failed, out = _apply_one(tmp_path, exe, guard, {GOVERNED: "true"}, {})
        assert failed == 1 and f"carry a {CLAIM} claim" in out, out
    report = next(d for d in sets["platform machinery"]
                  if d["metadata"]["name"] == "governed-namespace-unclaimed-report")
    _, failed, out = _apply_one(tmp_path, exe, report, {GOVERNED: "true"}, {})
    assert failed == 1 and f"carries no {CLAIM} claim" in out and "bottom rung" in out, out


def test_an_infra_label_moves_no_cage_on_any_namespace(tmp_path):
    """Round three, `loophole-2`: a platform-role party declares a business Namespace `infra`.
    No served body reads the word, so the label changes nothing. A claiming pod gets the same
    rung with it as without it, governed or not, under every delivered body."""
    exe = _kyverno()
    for body in _delivered_bodies():
        for governed in ({}, {GOVERNED: "true"}):
            with_infra = _rung(tmp_path, exe, body, {**governed, TIER: "infra"})
            without = _rung(tmp_path, exe, body, dict(governed))
            assert with_infra == without, f"{body}: `infra` moved a claiming pod {without!r} -> {with_infra!r}"


def test_restoring_a_dropped_claim_is_a_pod_edit_the_binding_check_never_reads(tmp_path):
    """Round three, `overreach-4`, which says restoring a dropped claim during an incident is a
    Namespace edit the binding check forbids. The claim is a pod label. The binding check reads
    Namespace declarations and prices and never a claim. A pod that claims again gets its
    Namespace's declared tier from the served body, with no Namespace edited."""
    source = (PLATFORM / "shift-left" / "tier_binding.py").read_text(encoding="utf-8")
    assert CLAIM not in source and "policy-version" not in source
    exe = _kyverno()
    newest = max(_declared_versions(), key=lambda v: tuple(int(x) for x in v.split(".")))
    for body in [PLATFORM / "distribution" / "policies" / f"v{newest}" / "cage-tier.yaml",
                 *sorted(ESTATE.glob("*/composed/policies/v*/cage-tier.yaml"))]:
        assert _claim(body) != "graded"
        assert _rung(tmp_path, exe, body, {GOVERNED: "true", TIER: "baseline"}) == "baseline", body


def test_the_infra_tripwire_gates_no_unit_merge():
    """Round three, `overreach-6`: the tripwire blocks an unrelated CoreDNS patch mid-rollout. No
    unit's workflow calls it. It runs in the hub's gate, as an estate observation, and a red there
    stops no merge in any unit."""
    callers = [str(w.relative_to(ESTATE)) for w in sorted(ESTATE.glob("*/.github/workflows/*.y*ml"))
               if "verify-infra-declaration" in w.read_text(encoding="utf-8")]
    assert callers == [], f"a unit's workflow runs the tripwire: {callers}"
    assert sorted(ESTATE.glob("platform/.github/workflows/*.yml")), "no platform workflow read -- the scan is blind"
    manifest = (HUB / "talk" / "verify-manifest.txt").read_text(encoding="utf-8")
    line = next(ln for ln in manifest.splitlines() if "verify-infra-declaration.sh" in ln)
    assert "| estate-observation |" in line, line


# --------------------------------------------------------------------------------------------
# the record: every candidate has a verdict, and the survival rate is computed from them
# --------------------------------------------------------------------------------------------

def _candidates() -> set[tuple[str, str]]:
    found = set()
    for rnd in ("two", "three"):
        for case in json.loads((RESEARCH / f"11-loophole-round-{rnd}" / "candidates.json").read_text()):
            found.add((rnd, case["key"]))
    return found


def test_every_candidate_of_rounds_two_and_three_carries_a_verdict():
    assert set(VERDICTS) == _candidates() and len(VERDICTS) == 12
    here = {name for name in globals() if name.startswith("test_")}
    ladder = (HUB / "tests" / "test_cage_ladder_holes.py").read_text(encoding="utf-8")
    for key, (verdict, test, fact) in VERDICTS.items():
        assert verdict in {"survivor", "discard"} and fact.strip(), key
        assert test in here or f"def {test}(" in ladder, f"{key}: no test named {test}"


def test_the_survival_rate_is_derived_from_the_verdicts():
    """One of twelve here, two of six in round one: three of eighteen. ADR-0030 said "about a
    third" on round one alone; its 2026-09-22 note corrects that to the number computed here."""
    survived = sum(1 for verdict, _, _ in VERDICTS.values() if verdict == "survivor")
    assert (survived, len(VERDICTS)) == (1, 12)
    total = (ROUND_ONE["survived"] + survived, ROUND_ONE["checked"] + len(VERDICTS))
    assert total == (3, 18)
    adr = (HUB / "docs" / "adr" /
           "0030-loophole-runs-as-an-external-tool-in-rounds-and-the-estate-keeps-the-pointer.md").read_text()
    assert f"{total[0]} of {total[1]} candidates survived" in adr


def test_three_of_the_twelve_restate_a_reason_round_one_gave():
    """Ticket 116 said four restate a round-one reason. Ticket 11's own reason table says three:
    round two `overreach-4` (no break-glass path), round two `overreach-6` and round three
    `overreach-5` (an innocent omission draws the bottom rung)."""
    targets = json.loads((RESEARCH / "11-targets.json").read_text())["rounds"]
    first = {reason for _, reason in targets["one"].values()}
    restating = sorted((rnd, key) for rnd in ("two", "three")
                       for key, (_, reason) in targets[rnd].items() if reason in first)
    assert restating == [("three", "overreach-5"), ("two", "overreach-4"), ("two", "overreach-6")]
