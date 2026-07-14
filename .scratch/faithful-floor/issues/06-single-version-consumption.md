# 06 — Single-version consumption + one consumer app

**What to build:** The first end-to-end tracer: the cluster consumes policy `v1.0.0` as a versioned dependency — a `GitRepository` pinned on both `spec.ref.tag` and `spec.ref.commit` (ADR-0001), a `Kustomization` that `dependsOn` the Kyverno Kustomization with `wait: true` — and one consumer app opts in by stamping the single `policy-version` label (the **consumable** "-able": onboarding = one label). Admission verdicts happen live: the labelled app is judged by the Audit lane-keeper and the Deny gate.

**Blocked by:** 04 — Signed release pipeline (produces the `v1.0.0` tag to pin), 05 — KiND + Flux Operator + Kyverno.

**Status:** ready-for-agent

- [x] The pinned source reconciles; the versioned ValidatingPolicies are live with their nameSuffix
- [x] A compliant labelled workload admits; a gate-violating one is denied at admission
- [x] A lane-keeper violation admits but appears in a PolicyReport
- [x] An unlabelled workload is untouched by the versioned policies (orphan guard comes later)
- [x] Onboarding the consumer required exactly one label

## Comments

Done 2026-07-14. `fleet/clusters/cluster1/`:
- `bootstrap.yaml` — a self-referential `GitRepository`+`Kustomization("kyverno")`: the fleet
  repo now syncs itself, turning the Kyverno install from `up.sh`'s former one-shot `kubectl
  apply` into a real Kustomization other Kustomizations can `dependsOn` (PRD §6.4 point 6).
- `policy-v1.0.0.yaml` — `GitRepository` pinned on both `spec.ref.tag: v1.0.0` and
  `spec.ref.commit` (ADR-0001), one `Kustomization` per policy (the policy repo has no
  aggregating `kustomization.yaml` at `workloads/kyverno/` yet, only one per policy dir —
  adding one would need a new patch release; two per-policy Kustomizations avoided that and
  cost nothing since PRD's ResourceSet design (issue 08) ranges over *versions*, not
  policies-within-a-version, so this doesn't complicate that later). Both `dependsOn: [kyverno]`,
  `wait: true`.
- `apps.yaml` — the new `apps` repo (`policy-as-versioned-flux/apps`, `app1`), branch-tracked
  ordinary GitOps, `dependsOn` the policy Kustomizations for a deterministic demo.

`up.sh` wires all of this into the documented sequence; `verify-live.sh` (new) proves the four
admission-verdict checklist items directly against the live cluster (polled PolicyReport check
for the "admits but reported" case, mirroring the policy repo's own verify-live.sh). Ran green
against `cluster1`: `app1` (compliant) admitted; a Deny-gate violation refused outright; an
Audit-lane-keeper violation admitted with a PolicyReport fail entry; an unlabelled pod admitted
untouched (the orphan guard that would catch this is issue 09).

One fix along the way: Flux's drift-detection health check errored on `app1`'s Pod
("namespace not specified") until the manifest set `metadata.namespace: default` explicitly —
relying on kubectl's implicit default-namespace behaviour doesn't work for Flux's server-side
apply/diff.
