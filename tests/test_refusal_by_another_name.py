"""Eco-system ticket 98: a refusal by another name.

The estate grades every Deny-shaped rule (ticket 89). Nothing graded the other way a workload
can be stopped: a MUTATION whose product the API server rejects. Four instances are on the
record, one of them live in the estate today.

The seam is `verify/refusal-by-another-name/refusal_scan.py` — what a mutation WRITES, what
NAMES it writes into a reference field, which OPERATIONS reach it, and the join of those facts
to `register.yaml`, which records the refusals the estate has decided to accept. The shell
script runs it over the served surface and adds the one leg that has to be executed rather than
read (idempotence on UPDATE, through the kyverno CLI).

What these tests hold down, one per instance the estate has produced:

  1. the priority trio (2026-08-28, ticket 26): a mutation that writes `priorityClassName`
     without the two fields the Priority admission plugin re-derives from it refuses every pod
     it touches;
  2. the unsuffixed PriorityClass (2026-09-05, ticket 89 round 2): a name written into a
     reference field that the same release does not ship;
  3. the full cage body on UPDATE (2026-09-05, ticket 89 round 2): a field written on an
     operation the resource does not allow it to change on;
  4. the live one (2026-09-05, ticket 89 S3): the same shape, DECIDED as correct — so the
     register must let a refusal be reported without being called a defect, and must go red
     when the row stops describing the code.
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
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rs = _load("refusal_scan", ROOT / "verify" / "refusal-by-another-name" / "refusal_scan.py")


# --------------------------------------------------------------- fixtures, all policy-shaped

CAGE_BODY = """Object{
  metadata: Object.metadata{ labels: {
    "posture.acme.io/caged": "true",
    "posture.acme.io/tier": variables.tier
  } },
  spec: Object.spec{
    hostNetwork: false,
    priorityClassName: variables.dial.pc,
    priority: int(variables.dial.prio),
    preemptionPolicy: "Never",
    containers: object.spec.containers.filter(c, c.name != "waf-sidecar").map(c,
      Object.spec.containers{
        name: c.name,
        resources: Object.spec.containers.resources{
          limits: {"cpu": variables.dial.cpu, "memory": variables.dial.mem}
        }
      })
  }
}"""

DIAL = (
    "{'baseline':  {'cpu':'500m','pc':'cage-baseline-4-0-0','prio':'-10'},"
    " 'isolated':  {'cpu':'100m','pc':'cage-isolated-4-0-0','prio':'-10000'}}[variables.tier]"
)


def cage(operations=("CREATE",), body=CAGE_BODY, dial=DIAL, name="cage-tier-4-0-0"):
    return {
        "apiVersion": "policies.kyverno.io/v1alpha1",
        "kind": "MutatingPolicy",
        "metadata": {"name": name},
        "spec": {
            "matchConstraints": {"resourceRules": [
                {"apiGroups": [""], "apiVersions": ["v1"],
                 "operations": list(operations), "resources": ["pods"]}]},
            "variables": [{"name": "dial", "expression": dial}],
            "mutations": [{"patchType": "ApplyConfiguration",
                           "applyConfiguration": {"expression": body}}],
        },
    }


HOLD_BODY = """Object{
  metadata: Object.metadata{ labels: {
    "posture.acme.io/caged": "true",
    "posture.acme.io/tier": "isolated"
  } }
}"""


def hold():
    return cage(operations=("UPDATE",), body=HOLD_BODY, name="governed-namespace-cage-holds")


# ------------------------------------------------------------------- what a mutation writes

def test_object_literal_paths_reads_nested_spec_writes() -> None:
    paths = rs.object_literal_paths(CAGE_BODY)
    assert "spec.priorityClassName" in paths
    assert "spec.priority" in paths
    assert "spec.preemptionPolicy" in paths
    assert "spec.hostNetwork" in paths
    assert "metadata.labels" in paths


def test_object_literal_paths_walks_into_a_mapped_container_list() -> None:
    paths = rs.object_literal_paths(CAGE_BODY)
    assert "spec.containers[*].name" in paths
    assert "spec.containers[*].resources.limits" in paths


def test_a_labels_only_hold_writes_nothing_under_spec() -> None:
    paths = rs.object_literal_paths(HOLD_BODY)
    assert paths == {"metadata.labels"}


def test_jsonpatch_paths_wildcard_the_index() -> None:
    expr = ('object.spec.containers.map(c, JSONPatch{op: "add", path: "/spec/containers/" + '
            'string(object.spec.containers.indexOf(c)) + "/securityContext/capabilities", '
            'value: {"drop": ["ALL"]}})')
    assert rs.jsonpatch_paths(expr) == {"spec.containers[*].securityContext.capabilities"}


def test_written_paths_covers_every_mutation_in_the_policy() -> None:
    doc = cage()
    doc["spec"]["mutations"].append({"patchType": "JSONPatch", "jsonPatch": {
        "expression": '[JSONPatch{op: "add", path: "/spec/nodeName", value: "n"}]'}})
    assert "spec.nodeName" in rs.written_paths(doc)
    assert "spec.priorityClassName" in rs.written_paths(doc)


# ---------------------------------------------- instance 3 and 4: field x operation legality

def test_a_field_immutable_on_a_running_pod_is_a_hazard_on_update() -> None:
    found = {h.path for h in rs.hazards(rs.mutation(cage(operations=("CREATE", "UPDATE"))))}
    assert "spec.priorityClassName" in found
    assert "spec.containers[*].name" in found


def test_the_same_body_on_create_only_is_no_hazard_at_all() -> None:
    assert rs.hazards(rs.mutation(cage(operations=("CREATE",)))) == ()


def test_labels_are_mutable_on_a_running_pod_so_a_hold_is_no_hazard() -> None:
    assert rs.hazards(rs.mutation(hold())) == ()


def test_a_container_image_is_mutable_on_a_running_pod() -> None:
    body = 'Object{spec: Object.spec{containers: object.spec.containers.map(c, ' \
           'Object.spec.containers{image: "pinned"})}}'
    doc = cage(operations=("UPDATE",), body=body)
    assert rs.hazards(rs.mutation(doc)) == ()


# ------------------------------------------- instance 2: a name the release does not ship

def test_reference_names_resolve_through_a_variable_map() -> None:
    refs = rs.reference_names(cage())
    assert refs["spec.priorityClassName"].names == frozenset(
        {"cage-baseline-4-0-0", "cage-isolated-4-0-0"})
    assert refs["spec.priorityClassName"].kind == "PriorityClass"
    assert refs["spec.priorityClassName"].unresolved is False


def test_a_dial_table_indexed_by_a_pinned_tier_resolves_to_that_rung_only() -> None:
    """The machinery cages pin `tier` to the literal 'isolated' and index the shared dial table
    with it, so the only class they can ever write is the bottom rung's. Reading all four would
    demand the machinery ship three PriorityClasses no policy of its can name -- a red that is
    wrong, which is worse than no check at all."""
    doc = cage(dial=DIAL + "")
    doc["spec"]["variables"] = [
        {"name": "tier", "expression": "'isolated'"},
        {"name": "dial", "expression": DIAL},
    ]
    refs = rs.reference_names(doc)
    assert refs["spec.priorityClassName"].names == frozenset({"cage-isolated-4-0-0"})


def test_a_dial_table_indexed_by_a_computed_tier_resolves_to_every_rung() -> None:
    doc = cage()
    doc["spec"]["variables"] = [
        {"name": "tier", "expression": "variables.nsTier in ['baseline'] ? 'baseline' : 'isolated'"},
        {"name": "dial", "expression": DIAL},
    ]
    refs = rs.reference_names(doc)
    assert refs["spec.priorityClassName"].names == frozenset(
        {"cage-baseline-4-0-0", "cage-isolated-4-0-0"})


def test_reference_names_resolve_a_literal() -> None:
    body = 'Object{spec: Object.spec{priorityClassName: "cage-isolated"}}'
    refs = rs.reference_names(cage(body=body))
    assert refs["spec.priorityClassName"].names == frozenset({"cage-isolated"})


def test_a_name_the_release_does_not_ship_is_a_dangling_reference() -> None:
    m = rs.mutation(cage(body='Object{spec: Object.spec{priorityClassName: "cage-isolated"}}'))
    shipped = {"PriorityClass": {"cage-isolated-4-0-0"}}
    dangling = rs.dangling_references(m, shipped)
    assert [d.name for d in dangling] == ["cage-isolated"]
    assert "PriorityClass" in dangling[0].why


def test_a_name_the_release_ships_is_not_dangling() -> None:
    m = rs.mutation(cage(body='Object{spec: Object.spec{priorityClassName: "cage-isolated"}}'))
    assert rs.dangling_references(m, {"PriorityClass": {"cage-isolated"}}) == ()


def test_an_unresolved_reference_is_reported_and_never_silently_passes() -> None:
    m = rs.mutation(cage(body='Object{spec: Object.spec{priorityClassName: object.metadata.name}}'))
    assert m.references["spec.priorityClassName"].unresolved is True
    assert rs.unresolved_references(m)


# ------------------------------------------------ instance 1a: the priority trio

def test_writing_a_priority_class_without_its_integer_is_a_defect() -> None:
    body = 'Object{spec: Object.spec{priorityClassName: variables.dial.pc}}'
    broken = rs.priority_trio(rs.mutation(cage(body=body)))
    assert broken
    assert "priority" in broken[0].why


def test_the_complete_trio_is_clean() -> None:
    assert rs.priority_trio(rs.mutation(cage())) == ()


def test_a_mutation_that_names_no_priority_class_owes_no_trio() -> None:
    assert rs.priority_trio(rs.mutation(hold())) == ()


# ----------------------------------------------------------------- the join to the register

def _reg(**over):
    row = {"policy": "cage-tier*", "policies": ["cage-tier-4-0-0"], "operation": "UPDATE",
           "fields": ["spec.priorityClassName", "spec.priority", "spec.preemptionPolicy",
                      "spec.hostNetwork", "spec.containers[*].name",
                      "spec.containers[*].resources.limits"],
           "decision": "accepted", "recorded": "2026-09-06",
           "reason": "ticket 89 S3 decided the API server's refusal is the correct outcome",
           "remediation": "recreate the pod"}
    row.update(over)
    return {"accepted": [row]}


def _mutations(**over):
    return [rs.mutation(cage(operations=("CREATE", "UPDATE")), path="platform/x.yaml",
                        surface="served-cut", **over)]


def test_an_unregistered_hazard_fails() -> None:
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0",
                                                         "cage-isolated-4-0-0"}},
                 register={"accepted": []})
    assert v.code == 1
    assert any("no register row" in line for line in v.lines)


def test_a_registered_hazard_is_reported_and_is_not_a_defect() -> None:
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0",
                                                         "cage-isolated-4-0-0"}},
                 register=_reg())
    assert v.code == 0
    assert any("accepted refusal" in line for line in v.lines)
    assert any("recreate the pod" in line for line in v.lines)


def test_a_register_row_that_matches_nothing_is_stale_and_fails() -> None:
    reg = _reg()
    reg["accepted"].append(dict(reg["accepted"][0], policy="cage-that-went-away*"))
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0",
                                                         "cage-isolated-4-0-0"}},
                 register=reg)
    assert v.code == 1
    assert any("matches no mutation" in line for line in v.lines)


def test_a_row_whose_field_set_disagrees_with_the_code_fails() -> None:
    reg = _reg(fields=["spec.priorityClassName"])
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0",
                                                         "cage-isolated-4-0-0"}},
                 register=reg)
    assert v.code == 1
    assert any("field set" in line for line in v.lines)


def test_a_row_with_no_reason_fails() -> None:
    reg = _reg()
    reg["accepted"][0].pop("reason")
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0",
                                                         "cage-isolated-4-0-0"}},
                 register=reg)
    assert v.code == 1


def test_a_dangling_reference_fails_even_with_every_hazard_registered() -> None:
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0"}},
                 register=_reg())
    assert v.code == 1
    assert any("cage-isolated-4-0-0" in line for line in v.lines)


def test_an_unresolved_reference_could_not_be_looked_at_rather_than_passed() -> None:
    body = ('Object{spec: Object.spec{priorityClassName: object.x, priority: -10, '
            'preemptionPolicy: "Never"}}')
    ms = [rs.mutation(cage(body=body), path="platform/x.yaml", surface="served-cut")]
    v = rs.grade(ms, shipped={"PriorityClass": set()}, register={"accepted": []})
    assert v.code == 3
    assert any("could not resolve" in line for line in v.lines)


# ------------------------------------------------------------------- the served partition

def test_the_authoring_tree_is_excluded_by_name_and_not_graded() -> None:
    s = rs.classify("platform/graded/policies/cage-tier.yaml", declared={}, cut={})
    assert s.surface == "authoring"
    assert "Kustomization" in s.why


def test_a_declared_and_cut_version_directory_is_served() -> None:
    s = rs.classify("platform/distribution/policies/v4.0.0/cage-tier.yaml",
                    declared={"platform": {"4.0.0"}}, cut={"platform": {"4.0.0"}})
    assert s.surface == "served-cut"


def test_a_version_directory_the_array_no_longer_declares_is_not_served() -> None:
    s = rs.classify("platform/distribution/policies/v2.0.0/cage-tier.yaml",
                    declared={"platform": {"4.0.0"}}, cut={"platform": {"4.0.0"}})
    assert s.surface == "unserved-on-disk"
    assert "array" in s.why


def test_a_declared_but_uncut_version_is_pending_and_still_graded() -> None:
    s = rs.classify("platform/distribution/policies/v5.0.0/cage-tier.yaml",
                    declared={"platform": {"4.0.0", "5.0.0"}}, cut={"platform": {"4.0.0"}})
    assert s.surface == "pending"
    assert s.graded is True


def test_the_resource_set_template_is_the_served_machinery() -> None:
    s = rs.classify("platform/distribution/versions.yaml", declared={}, cut={})
    assert s.surface == "served-machinery"


# ----------------------------------------------------------- reading a templated document

def test_documents_are_read_out_of_a_resourceset_template() -> None:
    text = """
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSet
metadata:
  name: policy-versions
spec:
  resourcesTemplate: |
    << range $v := (index (inputs) "versions") >>
    ---
    apiVersion: kustomize.toolkit.fluxcd.io/v1
    kind: Kustomization
    metadata:
      name: policies-<< $v.version | slugify >>
    << end >>
    ---
    apiVersion: scheduling.k8s.io/v1
    kind: PriorityClass
    metadata:
      name: cage-isolated
    value: -10000
"""
    names = {(d.get("kind"), (d.get("metadata") or {}).get("name"))
             for d in rs.read_documents(text)}
    assert ("PriorityClass", "cage-isolated") in names


def test_shipped_names_are_collected_by_kind() -> None:
    docs = [{"kind": "PriorityClass", "metadata": {"name": "cage-isolated"}},
            {"kind": "MutatingPolicy", "metadata": {"name": "cage"}}]
    assert rs.shipped_names(docs) == {"PriorityClass": {"cage-isolated"}}


# ------------------------------------------------------------- the disclosed limit is a test

def test_the_blind_spots_are_declared_dated_and_non_empty() -> None:
    assert rs.BLIND_SPOTS
    for spot in rs.BLIND_SPOTS:
        assert "2026-" in spot, f"an undated disclosure goes stale unnoticed: {spot}"


@pytest.mark.parametrize("kind", ["ValidatingPolicy", "ClusterPolicy", "GeneratingPolicy"])
def test_only_a_mutating_policy_is_a_candidate(kind: str) -> None:
    doc = cage()
    doc["kind"] = kind
    assert rs.mutation(doc) is None


# ======================================================================================
# Review, 2026-09-06. Every test below is a defect the reviewer PLANTED and the check let
# through. Each one is a served thing that was never measured while the run's sentence
# claimed it was -- the ticket's own subject, one level up.
# ======================================================================================

# ------------------------------------------------- F1: `operations: ["*"]` is not a gap

def test_a_wildcard_operation_reaches_update() -> None:
    """`operations: ["*"]` is legal in a resourceRule and means every operation, UPDATE
    among them. Gating on the literal string dropped the policy out of the register join
    AND out of the execution probe, while the verdict still said every write on UPDATE was
    recorded. One field edit voided the central join."""
    m = rs.mutation(cage(operations=("*",)))
    assert m is not None
    assert "UPDATE" in m.operations
    assert "CREATE" in m.operations
    assert "spec.priorityClassName" in {h.path for h in rs.hazards(m)}


def test_a_wildcard_is_expanded_in_the_recorded_operations() -> None:
    m = rs.mutation(cage(operations=("*",)))
    assert m is not None
    assert set(m.operations) == {"CREATE", "UPDATE", "DELETE", "CONNECT"}
    assert "*" not in m.operations


# --------------------------- F2: a mutation on an unrecognised path is not invisible

def _plant(tmp_path: Path, rel: str, text: str) -> Path:
    f = tmp_path / ".estate-clone" / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)
    return f


SNEAKY = """apiVersion: policies.kyverno.io/v1alpha1
kind: MutatingPolicy
metadata:
  name: apps-sneaky-cage
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE"]
        resources: ["pods"]
  mutations:
    - patchType: ApplyConfiguration
      applyConfiguration:
        expression: >-
          Object{spec: Object.spec{priorityClassName: "cage-does-not-exist",
                                   priority: -10, preemptionPolicy: "Never"}}
"""


def test_a_mutation_on_a_path_the_scan_does_not_know_is_not_dropped(tmp_path: Path) -> None:
    """It used to be. `scan_tree` skipped an unrecognised path BEFORE reading the file, so a
    MutatingPolicy under an adopter's gitops/apps/ -- a tree its root Kustomization really
    reconciles, with prune: true -- was neither graded, nor excluded with a reason, nor
    counted, and the verdict still read `every mutation the estate SERVES was graded`."""
    _plant(tmp_path, "driftwood/gitops/apps/sneaky.yaml", SNEAKY)
    mutations, _, _ = rs.scan_tree(tmp_path)
    found = [m for m in mutations if m.name == "apps-sneaky-cage"]
    assert found, "a mutating policy on an unrecognised path vanished from the scan"
    assert found[0].surface == "unclassified"


def test_an_unclassified_mutation_with_a_dangling_reference_fails(tmp_path: Path) -> None:
    _plant(tmp_path, "driftwood/gitops/apps/sneaky.yaml", SNEAKY)
    mutations, groups, _ = rs.scan_tree(tmp_path)
    v = rs.grade(mutations, groups, {"accepted": []})
    assert v.code == 1
    assert any("cage-does-not-exist" in line for line in v.lines)


def test_an_unclassified_mutation_that_is_otherwise_clean_could_not_be_looked_at(
        tmp_path: Path) -> None:
    _plant(tmp_path, "driftwood/gitops/apps/sneaky.yaml",
           SNEAKY.replace("cage-does-not-exist", "cage-here") + """---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: cage-here
value: -10
""")
    mutations, groups, _ = rs.scan_tree(tmp_path)
    v = rs.grade(mutations, groups, {"accepted": []})
    assert v.code == 3
    assert any("does not know whether" in line for line in v.lines)


# ------------------------------- F3: the row is graded per policy, not against the union

def _two(fields_second):
    """Two served policies the same glob matches: the real one, and a second whose writes
    are a SUBSET. The union hides the second entirely."""
    body_full = CAGE_BODY
    body_subset = 'Object{spec: Object.spec{priorityClassName: variables.dial.pc, ' \
                  'priority: 1, preemptionPolicy: "Never"}}'
    return [
        rs.mutation(cage(operations=("CREATE", "UPDATE"), body=body_full),
                    path="platform/a.yaml", surface="served-cut"),
        rs.mutation(cage(operations=("CREATE", "UPDATE"),
                         body=body_subset if fields_second else body_full,
                         name="cage-tier-5-0-0"),
                    path="platform/b.yaml", surface="served-cut"),
    ]


_SHIPPED = {"PriorityClass": {"cage-baseline-4-0-0", "cage-isolated-4-0-0"}}


def _reg2(**over):
    row = dict(_reg()["accepted"][0])
    row["policies"] = ["cage-tier-4-0-0", "cage-tier-5-0-0"]
    row.update(over)
    return {"accepted": [row]}


def test_a_second_policy_writing_a_subset_is_not_hidden_by_the_union() -> None:
    v = rs.grade(_two(True), shipped=_SHIPPED, register=_reg2())
    assert v.code == 1
    assert any("cage-tier-5-0-0" in line and "field set" in line for line in v.lines)


def test_two_policies_that_both_match_the_row_exactly_pass() -> None:
    v = rs.grade(_two(False), shipped=_SHIPPED, register=_reg2())
    assert v.code == 0


def test_a_row_must_name_the_policies_it_covers() -> None:
    """Widening the glob to `*` used to pass, because the union still equalled the row.
    The row names its policies now, so a new match is a change the row has to admit."""
    v = rs.grade(_two(False), shipped=_SHIPPED,
                 register=_reg2(policy="*", policies=["cage-tier-4-0-0"]))
    assert v.code == 1
    assert any("cage-tier-5-0-0" in line for line in v.lines)


def test_a_row_that_names_a_policy_the_surface_no_longer_carries_fails() -> None:
    v = rs.grade(_two(False), shipped=_SHIPPED,
                 register=_reg2(policies=["cage-tier-4-0-0", "cage-tier-5-0-0",
                                          "cage-tier-6-0-0"]))
    assert v.code == 1


# ------------------------------------------ F4: the mutability table is pinned by a test

def test_the_mutable_on_update_table_is_the_api_servers_own_list() -> None:
    """Observed on kind-driftwood (v1.36.1) on 2026-09-06, refusing a pod update:

        The Pod "t98-probe" is invalid: spec: Forbidden: pod updates may not change fields
        other than `spec.containers[*].image`,`spec.initContainers[*].image`,
        `spec.activeDeadlineSeconds`,`spec.tolerations` (only additions to existing
        tolerations),`spec.terminationGracePeriodSeconds` (allow it to be set to 1 if it
        was previously negative)

    Nothing pinned this tuple before the review: adding an entry silently deleted that field
    from every hazard set with nothing red. platform/graded/verify-graded.sh step 8b compares
    the same five to the live message as a SET, in both directions."""
    assert rs.MUTABLE_ON_UPDATE == (
        "metadata",
        "status",
        "spec.containers[*].image",
        "spec.initContainers[*].image",
        "spec.activeDeadlineSeconds",
        "spec.tolerations",
        "spec.terminationGracePeriodSeconds",
    )


def test_the_posture_authoring_tree_is_excluded_in_the_platforms_own_words() -> None:
    """Found by the F2 fix: `posture/policies/` was the one real file the new unclassified
    bucket caught. It is an authoring tree — render-and-prove.py and posture/up.sh both call
    it that — and the served copies are the per-version ones render-version-tree.py emits."""
    s = rs.classify("platform/posture/policies/stamp-posture.yaml", declared={}, cut={})
    assert s.surface == "authoring"
    assert s.graded is False


def test_a_wildcard_reaches_the_execution_probe_too(tmp_path: Path) -> None:
    """F1's other half: refusal_probe.collect() gated on the same literal, so a policy set to
    `operations: ["*"]` silently dropped out of leg B and the count fell with no omission
    named."""
    _plant(tmp_path, "platform/distribution/policies/v4.0.0/cage.yaml",
           SNEAKY.replace('operations: ["CREATE"]', 'operations: ["*"]')
                 .replace("cage-does-not-exist", "cage-here"))
    _plant(tmp_path, "platform/distribution/versions.yaml",
           "apiVersion: fluxcd.controlplane.io/v1\nkind: ResourceSet\nmetadata:\n"
           "  name: policy-versions\nspec:\n  inputs:\n    - versions:\n"
           "        - {version: \"4.0.0\", commit: abc}\n")
    mutations, _, _ = rs.scan_tree(tmp_path)
    m = [x for x in mutations if x.name == "apps-sneaky-cage"]
    assert m and m[0].surface == "served-cut"
    assert "UPDATE" in m[0].operations


# ======================================================================================
# Review round 3, 2026-09-06. A could-not-look anywhere used to turn the live instance red
# with a WRONG reason, which made the third declared could-not-look unreachable -- a stale
# disclosure, this week's lesson, in the check that exists to stop stale disclosures.
# ======================================================================================

def test_the_live_instance_is_still_reported_when_something_else_could_not_be_looked_at(
        tmp_path: Path) -> None:
    """The reviewer planted a HARMLESS label-only hold in `driftwood/gitops/apps/`, register
    row intact. The grade correctly returned 3 (the hold's path cannot be placed), and
    `replay_4` -- which asserted `v.code == 0` -- reported "the live instance is NOT reported
    -- either the row went stale or the code moved", exited the run at step 2, and the SKIP
    line the manifest declares never printed. The predicate asks about the ROW now."""
    ms = _mutations() + [rs.mutation(
        {"kind": "MutatingPolicy", "metadata": {"name": "apps-hold"},
         "spec": {"matchConstraints": {"resourceRules": [
             {"operations": ["UPDATE"], "resources": ["pods"]}]},
             "mutations": [{"patchType": "ApplyConfiguration", "applyConfiguration": {
                 "expression": HOLD_BODY}}]}},
        path="driftwood/gitops/apps/hold.yaml", surface="unclassified")]
    v = rs.grade(ms, shipped={"PriorityClass": {"cage-baseline-4-0-0", "cage-isolated-4-0-0"}},
                 register=_reg())
    assert v.code == 3, "the unplaceable path is still a could-not-look"
    ok, why = rs.live_instance_reported(v)
    assert ok, why
    assert "accepted refusal" in why


def test_the_live_instance_predicate_is_red_when_the_row_really_did_go_stale() -> None:
    v = rs.grade(_mutations(), shipped={"PriorityClass": {"cage-baseline-4-0-0",
                                                         "cage-isolated-4-0-0"}},
                 register={"accepted": []})
    ok, why = rs.live_instance_reported(v)
    assert not ok
    assert "no register row" in why or "not reported" in why


# ------------------------------- R3: case, and an operations list nobody wrote

def test_operations_are_matched_case_insensitively() -> None:
    """Confirmed against the CRD with `kubectl apply --dry-run=server`: `operations: ["Update"]`
    is accepted. A registered policy is caught by the row's `policies:` set; a NEW one written
    that way would have been read as not reaching UPDATE at all."""
    m = rs.mutation(cage(operations=("Update", "create")))
    assert m is not None
    assert set(m.operations) == {"UPDATE", "CREATE"}
    assert "spec.priorityClassName" in {h.path for h in rs.hazards(m)}


def test_a_mutating_policy_with_no_operations_at_all_is_a_could_not_look() -> None:
    doc = cage()
    doc["spec"]["matchConstraints"]["resourceRules"][0].pop("operations")
    m = rs.mutation(doc, path="platform/x.yaml", surface="served-cut")
    assert m is not None and m.operations_unstated is True
    v = rs.grade([m], shipped={"PriorityClass": {"cage-baseline-4-0-0", "cage-isolated-4-0-0"}},
                 register={"accepted": []})
    assert v.code == 3
    assert any("declares no operations" in line for line in v.lines)


# --------------------- R2: a mutation that writes nothing, versus one that writes the same

def test_a_body_with_no_mutations_writes_nothing() -> None:
    doc = cage()
    doc["spec"]["mutations"] = []
    assert rs.written_paths(doc) == set()


def test_a_clobber_that_writes_the_value_the_object_already_has_still_writes() -> None:
    """D6 in a new place: a red that is wrong is worse than no check. `stamp-posture`'s own
    header describes a defensive clobber -- it OVERWRITES unconditionally so a post-admission
    relabel is re-clobbered. Handed a pod that already carries the value, it changes nothing,
    and leg B's `must change the pod` rule called that `a policy that writes nothing`."""
    body = 'Object{metadata: Object.metadata{labels: {"posture.acme.io/caged": "true"}}}'
    assert rs.written_paths(cage(body=body)) == {"metadata.labels"}
