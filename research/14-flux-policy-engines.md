# Flux CD + Kubernetes Policy/Admission Engines, and Multi-Version Policy Coexistence

Research date: 2026-06-01. Sources: deepwiki (kyverno/kyverno, fluxcd/kustomize-controller),
fluxcd.io docs, kyverno.io docs, web search (2025/2026). Links collected at the foot of the doc.

This note maps the original talk's themes ("versioned policy as Flux", the
"✅❌✅✅✅ = ❌ inconsistent half-deploy" problem, "measurable compliance",
"policy-checker / shift-left", "no runtime lifecycle for cloud/TF") onto what Flux
and the three main K8s policy engines actually do in 2025/2026.

---

## 0. Headline findings (read this first)

1. **Flux does NOT apply a Kustomization atomically.** The kustomize-controller applies
   resources in **three ordered stages** (CRDs+Namespaces → "class" types like
   StorageClass/RuntimeClass → everything else). *Within* a stage it does a server-side
   **dry-run of the whole stage first**, so an admission-webhook rejection of one object
   aborts that stage **before** anything in it is applied. *Across* stages there is **no
   rollback**: if stage 1 succeeds and stage 3 is rejected, stage-1 objects stay on the
   cluster. **This is exactly where the "half-deploy" lives** — not inside a manifest set,
   but at the stage seam and across reconciliations.

2. **The half-deploy is therefore avoidable for the common case** (all your app objects
   land in stage 3 and are validated together by dry-run before apply), but **not for the
   CRD/Namespace-first case** and **not across multiple Kustomizations**. The mitigations
   are `spec.wait` health-gating, `dependsOn` ordering, splitting policy infra from
   workloads, and keeping a logical deploy inside a single Kustomization/stage.

3. **Kyverno is mid-migration.** As of 1.17 (Feb 2026) the legacy `ClusterPolicy`/`Policy`
   are **Deprecated**, removal targeted for **v1.20 (~Oct 2026)**. The future is CEL-based
   `ValidatingPolicy`/`MutatingPolicy`/etc. (GA in 1.17). `validationFailureAction:
   Audit|Enforce` becomes `validationActions: [Audit|Deny|Warn]`. Any new design should
   target the CEL types, but understand both.

4. **Multi-version coexistence is a naming + match-scoping problem, and it is solvable.**
   Kyverno (and Gatekeeper/Kubewarden) policies are independent objects; two policies with
   distinct names and **disjoint match scopes** (by namespace label, resource label, or CEL
   condition) coexist cleanly. A workload "selects" its policy version via a **label or
   namespace label** the policy's `selector`/`namespaceSelector`/`matchConditions` keys off.

5. **The Terraform/cloud gap is real but partially closed.** `tofu-controller` (ex-Weave
   tf-controller, now under `flux-iac`, actively released — v0.16.3, May 2026) gives Flux a
   genuine *runtime* reconciliation loop for Terraform/OpenTofu with drift detection and
   plan/approve. Crossplane and Cluster API offer continuous reconciliation for cloud
   resources too. Checkov remains shift-left/CI only — no runtime lifecycle. Be honest:
   GitOps can give cloud/IaC a runtime loop, but only if you adopt one of these controllers;
   a Checkov-in-CI posture has no runtime enforcement.

---

## 1. How Kyverno is installed and managed by Flux

### 1.1 Engine install (HelmRelease)
Standard pattern: a `HelmRepository` (`https://kyverno.github.io/kyverno/`) + `HelmRelease`
for the `kyverno` chart, reconciled by helm-controller. Policies often shipped via the
companion `kyverno-policies` chart or as raw CRs through a Kustomization.

Because `spec.dependsOn` only links **same-kind** Flux objects (Kustomization→Kustomization,
HelmRelease→HelmRelease), the idiomatic way to sequence "install engine, *then* apply
policies" is to wrap the HelmRelease in a Kustomization and have the **policy Kustomization
`dependsOn` the engine Kustomization**:

```yaml
# infra/kyverno -> Kustomization "kyverno" (contains the HelmRelease)
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: kyverno-policies, namespace: flux-system }
spec:
  dependsOn:
    - name: kyverno          # engine must be Ready first
  wait: true                  # health-gate: don't mark Ready until CRs settle
  path: ./policies
  prune: true
  sourceRef: { kind: GitRepository, name: flux-system }
```

### 1.2 Policy delivery (Kustomization)
`ClusterPolicy`/`Policy` (legacy) or `ValidatingPolicy`/`MutatingPolicy` (CEL, 1.17+) are
ordinary CRs committed to Git and applied by the kustomize-controller via server-side apply.

**Gotcha (flux2 #2620):** kustomize-controller historically reported a Kyverno
`ClusterPolicy` as `configured` on *every* reconcile because Kyverno mutates the policy
status / adds defaults; the SSA field-ownership diff then never converges. Mitigations:
ignore-managed-fields patterns, or treat noisy "configured" as benign. Worth noting in any
"measurable compliance" dashboard so drift noise isn't read as real change.

---

## 2. Validation / admission flow and the half-deploy problem

### 2.1 How Kyverno gates Flux-applied resources
Kyverno dynamically manages `ValidatingWebhookConfiguration`s. The API server calls the
webhook **per admission request** (per object/operation matching the webhook rules). Flux's
server-side apply (creates/updates) **does** trigger admission webhooks, including during the
server-side **dry-run** Flux runs first. `failurePolicy: Fail` (Kyverno's default for
enforced policies) means a webhook error/timeout/rejection blocks that object; `Ignore`
lets it through (used for non-critical or bootstrap phases).

> Deletes do NOT trigger admission webhooks the way creates/updates do. flux2 #4911:
> a validating webhook can block a delete, but the Kustomization may still clear the object
> from `status.inventory` without erroring — a silent inventory/cluster divergence. Relevant
> if a policy is meant to *prevent* deletion of protected resources.

### 2.2 The atomicity truth (the core nuance)
From the kustomize-controller source (`fluxcd/pkg/ssa` `ResourceManager`, staged apply):

- Apply runs in **three stages**: (1) CRDs + Namespaces, (2) "class" types, (3) all others.
- **`ApplyAll` per stage does a server-side dry-run of the entire stage first.** If any
  object in the stage fails the dry-run (e.g. Kyverno `Enforce`/`Deny` rejects it), the
  stage **aborts before applying anything in that stage**. So *within a stage*, the
  "✅❌✅✅✅" set behaves as **all-or-nothing at the validation gate** — you do NOT get a
  partial apply of that stage's surviving objects.
- **BUT there is no cross-stage rollback.** If stage 1 (CRDs/Namespaces) applied and stage 3
  is rejected, the stage-1 objects **remain**. And across **separate reconciliations**, an
  earlier successful apply is not reverted when a later commit fails.

So the precise statement of the talk's problem:

> **The half-deploy is not "3 of 5 objects in a set landed". Inside one stage it's
> all-or-nothing (dry-run gate). The half-deploy appears (a) at stage boundaries —
> namespaces/CRDs persist while workloads are blocked — and (b) across reconciliations and
> across multiple Kustomizations, where there is no transactional rollback.**

### 2.3 How to avoid / contain partial deploys
- **Keep a logical unit in one Kustomization, in one stage.** Plain app workloads all land
  in stage 3 and are dry-run-validated together → atomic at the gate.
- **`spec.wait: true` (+ `spec.healthChecks`)**: don't report `Ready` until resources are
  healthy; downstream `dependsOn` consumers then won't proceed on a half-applied parent.
- **`dependsOn` + webhook readiness**: ensure Kyverno (and its webhook + cert) is Ready
  before applying resources it gates, or `failurePolicy: Fail` + not-yet-ready webhook will
  reject/timeout the whole apply. (oneuptime "validation webhook errors" guidance, 2026.)
- **Server-side dry-run in CI** (`flux build kustomization` / `kubectl apply --server-side
  --dry-run=server`) to catch rejections shift-left, before Flux ever applies.
- **`spec.validation: none`** disables the dry-run gate (deprecated in v1beta2; don't —
  it's what makes within-stage apply all-or-nothing).
- Accept that **Flux is eventually-consistent, not transactional**: design for
  re-reconciliation to heal, and surface partial state via health + PolicyReports rather
  than assuming atomic deploys.

---

## 3. Many-to-many: multiple concurrent VERSIONS of one logical policy

This is the hard design question: run policy **v1** and **v2** of the same logical rule in
one cluster, each applying only to workloads pinned to that version, with no name collisions.

### 3.1 Why it works at all
Kyverno/Gatekeeper/Kubewarden policies are **independent named CRs**. Two policies coexist if
they have (a) **distinct names** and (b) **disjoint match scopes**. A resource that matches
both runs both (rules evaluate independently/sequentially) — so the whole game is making the
match scopes **mutually exclusive by version**.

### 3.2 Naming convention
Encode the version in the policy name and a label, never rely on a single mutable name:

```
require-resource-limits-v1     labels: { policy.example.com/name: require-resource-limits,
                                          policy.example.com/version: "1" }
require-resource-limits-v2     labels: { policy.example.com/name: require-resource-limits,
                                          policy.example.com/version: "2" }
```

This gives stable, collision-free identities and lets dashboards group "all versions of
require-resource-limits" by the `name` label while counting compliance per `version`.

### 3.3 How a workload SELECTS its policy version (three concrete patterns)

**Pattern A — workload label + `selector` (finest grained).**
Workload opts in by carrying a label; each policy version matches only its value.

```yaml
# v1 policy
spec:
  rules:
    - name: limits
      match:
        any:
          - resources:
              kinds: [Pod]
              selector:
                matchLabels:
                  policy.example.com/limits-version: "v1"
# v2 policy: identical but matchLabels value "v2"
```
A pod with `policy.example.com/limits-version: v2` is governed only by v2. Disjoint by
construction. (CEL `ValidatingPolicy` equivalent uses `objectSelector` or a
`matchConditions` CEL expr: `object.metadata.?labels["policy.example.com/limits-version"]
.orValue("") == "v2"`.)

**Pattern B — namespace label + `namespaceSelector` (the cleanest for tenancy/rollout).**
Pin a *namespace* to a version; everything in it gets that version. Best when versions track
team/tenant onboarding or a phased rollout.

```yaml
match:
  any:
    - resources: { kinds: [Pod] }
      namespaceSelector:
        matchLabels:
          policy.example.com/limits-version: "v2"
```
`team-a` namespace labelled `...version: v1`, `team-b` labelled `v2`. No pod-level labels
needed; the namespace is the version boundary. This is the recommended default — it makes
"which version applies here" answerable by reading one namespace label, and it composes with
Flux per-tenant Kustomizations.

**Pattern C — `matchExpressions` for ranges / negation (migration windows).**
Use set operators so v2 covers "v2 and anything not yet pinned", v1 covers only explicit v1,
enabling a default-forward migration:

```yaml
# v1: only explicit opt-in
selector: { matchExpressions: [ { key: limits-version, operator: In, values: ["v1"] } ] }
# v2: everything except explicit v1 (default = newest)
selector: { matchExpressions: [ { key: limits-version, operator: NotIn, values: ["v1"] } ] }
```
Caveat: `NotIn`/`DoesNotExist` defaults are powerful but easy to make overlap — always keep
the value sets partitioned so no resource matches two enforcing versions with conflicting
rules.

### 3.4 Practical guidance
- **Prefer namespace-label selection (Pattern B) as the primary axis**; use resource-label
  (A) only where a single namespace must run mixed versions.
- **Only one version should ever be `Enforce`/`Deny` for a given resource.** If two enforcing
  versions can match the same object, you can deadlock a deploy (object satisfies neither, or
  must satisfy both). Keep older versions on `Audit` during overlap, newest on `Enforce`.
- **Drive the selector label from GitOps**: the same Flux overlay that pins a workload's
  image/version also stamps `policy.example.com/...-version`, so policy version is pinned in
  the same commit as the workload version — *policy as versioned Flux*.
- **Prune on retirement**: delete `...-v1` from Git → Flux prunes the CR → version retired,
  cleanly, with audit history in Git.

---

## 4. Kyverno features that map to the talk's pillars

| Talk concept | Kyverno (legacy) | Kyverno (CEL, 1.17+) |
|---|---|---|
| warn vs error | `validationFailureAction: Audit` (allow + report) vs `Enforce` (block) | `validationActions: [Audit]` / `[Warn]` / `[Deny]` |
| per-namespace severity | `validationFailureActionOverrides` (namespaces / namespaceSelector) | per-policy scope + multiple policies |
| exceptions | `PolicyException` (kyverno.io/v2) | `PolicyException` (carried forward) |
| measurable compliance | `background: true` scans + `PolicyReport`/`ClusterPolicyReport` (wgpolicyk8s.io/v1alpha2) | same reports, plus CEL engines |
| shift-left / policy-checker | `kyverno apply` (eval against manifests) and `kyverno test` (assertion suites in CI) | same CLI, gains CEL `cli` support |

Notes:
- **Audit vs Enforce maps directly to warn vs error.** Audit lets the resource through and
  records a violation in a PolicyReport; Enforce blocks at admission. `Warn` (CEL) returns a
  warning to the client without blocking — a third, softer tier between Audit and Deny.
- **`validationFailureActionOverrides`** lets one policy be Enforce in prod namespaces and
  Audit elsewhere via `namespaceSelector` — useful for staged rollout *without* a second
  policy version.
- **Background scans + PolicyReport = "measurable compliance".** Background scanning
  re-evaluates *existing* resources (not just admission), so you get a continuously-updated
  count of compliant/violating workloads per policy — the runtime measurement the talk wants.
  PolicyReports are queryable CRs; aggregate them (e.g. Policy Reporter UI) for dashboards.
- **`kyverno apply` / `kyverno test` = the policy-checker.** `apply` evaluates policies
  against resource manifests offline; `test` runs declarative test cases (resource +
  expected result) in CI. This is the shift-left gate that should run on every PR *before*
  Flux applies — the same policies, evaluated twice (CI + admission), is the belt-and-braces
  story.

---

## 5. Other engines (parity check)

- **OPA Gatekeeper**: `ConstraintTemplate` (Rego) + `Constraint` CRs, both Git-managed via
  Flux; `dependsOn` to apply templates+constraints after Gatekeeper is Ready. Enforcement
  ladder `enforcementAction: dryrun → warn → deny` mirrors Kyverno Audit→Warn→Enforce.
  Multi-version coexistence: same recipe — distinct Constraint names + disjoint
  `match.namespaceSelector` / `labelSelector`. Gatekeeper also produces audit violations
  (status) for measurable compliance; Constraints reference a shared template, so "logical
  policy, many versions" can be many Constraints over one template, scoped by selector.
- **Kubewarden**: policies are WASM modules delivered as `ClusterAdmissionPolicy` /
  `AdmissionPolicy` CRs (Git-managed via Flux). Has its own `mode: monitor` vs `protect`
  (= audit vs enforce). Versioning is natural because a policy references a specific WASM
  module **version/tag** (OCI artifact) — so "policy v1 vs v2" can literally be two CRs
  pointing at two pinned module versions, scoped by selector. The OCI-pinned module is a
  cleaner versioning primitive than Kyverno's name-encoded versions.

All three share the same Flux integration shape (HelmRelease engine + Kustomization policies
+ `dependsOn`/`wait`) and the same multi-version mechanism (independent named CRs +
disjoint label/namespace selectors). The engine choice doesn't change the versioning design.

---

## 6. The Terraform / cloud side — runtime lifecycle gap (be honest)

The original work admits **no runtime lifecycle** for cloud/Terraform policy (Checkov runs in
CI; nothing reconciles cloud state continuously). What GitOps/Flux can offer:

- **tofu-controller (flux-iac, ex-Weave tf-controller)** — *actively maintained* (v0.16.3,
  May 2026; OpenSSF Best Practices; CNCF Slack). A genuine Flux controller that reconciles
  `Terraform`/OpenTofu resources as CRs: drift detection, plan/manual-approve, full
  GitOps automation, or enforce-existing-state. **This closes most of the gap** — it gives TF
  a *runtime* reconciliation loop with the same Git-as-source model. Health/drift surface in
  the CR status, which can feed the same compliance dashboard as PolicyReports.
  Caveat: Weaveworks shut down (Feb 2024); the project survived under community governance,
  so assess maintainer bandwidth before betting an org on it.
- **Crossplane** — manage cloud resources as K8s CRs with continuous reconciliation; combine
  with Kyverno/Gatekeeper to apply the *same* admission policies to cloud-resource CRs as to
  in-cluster workloads. This is the strongest "one policy engine over both K8s and cloud"
  story, but it's a heavier adoption than wrapping existing Terraform.
- **Cluster API** — continuous reconciliation for *cluster* infra specifically; narrower.

**Honest gap statement:** Checkov/Terraform-in-CI is shift-left only — it validates plans, it
does not enforce or remediate at runtime, and it has no equivalent of background scans /
PolicyReports for drift. To get a runtime lifecycle for cloud/IaC policy you must adopt a
reconciling controller (tofu-controller, Crossplane, or Cluster API). None of them makes
Checkov-style Rego/policy rules run *at cloud admission time* the way Kyverno gates K8s
admission — the closest equivalent is Kyverno/Gatekeeper gating the *CRs* (Crossplane/
tofu-controller `Terraform` objects) that represent cloud intent. That is the bridge: make
cloud intent a K8s object, then your existing versioned K8s policy engine governs it too.

---

## 7. Sources

- Flux Kustomization docs — https://fluxcd.io/flux/components/kustomize/kustomizations/
- Flux HelmRelease docs — https://fluxcd.io/flux/components/helm/helmreleases/
- Flux FAQ — https://fluxcd.io/flux/faq/
- Flux troubleshooting cheatsheet — https://fluxcd.io/flux/cheatsheets/troubleshooting/
- kustomize-controller CHANGELOG — https://github.com/fluxcd/kustomize-controller/blob/main/CHANGELOG.md
- flux2 #2620 (Kyverno ClusterPolicy "configured" every reconcile) — https://github.com/fluxcd/flux2/issues/2620
- flux2 #4911 (delete blocked by webhook, inventory divergence) — https://github.com/fluxcd/flux2/issues/4911
- flux2 #4073 (admission webhook dry-run support) — https://github.com/fluxcd/flux2/issues/4073
- Kyverno match/exclude (Selecting Resources) — https://kyverno.io/docs/policy-types/cluster-policy/match-exclude/
- Kyverno ValidatingPolicy (CEL) — https://kyverno.io/docs/policy-types/validating-policy/
- Kyverno 1.17 release — https://kyverno.io/blog/2026/02/02/announcing-kyverno-release-1.17/
- Kyverno 1.16 release — https://kyverno.io/blog/2025/11/10/announcing-kyverno-release-1.16/
- Kyverno CLI — https://kyverno.io/docs/kyverno-cli/
- OPA Gatekeeper howto (enforcementAction) — https://open-policy-agent.github.io/gatekeeper/website/docs/howto/
- Gatekeeper #2047 (deploy ConstraintTemplate/Constraint with Flux) — https://github.com/open-policy-agent/gatekeeper/issues/2047
- tofu-controller (flux-iac) — https://github.com/flux-iac/tofu-controller and https://flux-iac.github.io/tofu-controller/
- oneuptime: Flux + Kyverno / Gatekeeper / webhook errors / dry-run (2026 guides) — https://oneuptime.com/blog/
- deepwiki: kyverno/kyverno; fluxcd/kustomize-controller (ApplyAllStaged behavior)
