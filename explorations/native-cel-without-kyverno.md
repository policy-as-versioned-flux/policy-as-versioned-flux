# Native CEL without Kyverno — an exploration

*Project: Policy as Versioned Code, on Flux. Standalone exploration — not woven into the existing docs.*

## 1. Executive answer

**Verdict: partial — native CEL cannot replace Kyverno for the floor as designed; it can only replace the *gating* half.**

Native Kubernetes CEL admission (`ValidatingAdmissionPolicy` + `ValidatingAdmissionPolicyBinding`, `admissionregistration.k8s.io/v1`, GA in Kubernetes 1.30) is a genuine, faithful substitute for the **enforcement-split** and the **admission gate**: the Deny/Audit/Warn axis, per-version label self-selection via `objectSelector`, distinct named policy objects, and Crossplane-CR targeting all map across cleanly at request time. But three decisive reasons stop it from carrying the whole design:

1. **No PolicyReports.** Native VAP `validationActions: [Audit]` writes failures *only* into the API-server audit log under the annotation `validation.policy.admission.k8s.io/validation_failure`. It emits no `wgpolicyk8s.io/v1alpha2` `PolicyReport`/`ClusterPolicyReport` CRs. The design's "measurable" pillar (PRD §4, ADR-0008) — "is each workload actually passing?" feeding Policy Reporter → Prometheus → Grafana — has no native object to read.
2. **No background scan.** Native VAP is strictly admission-time (CREATE/UPDATE/DELETE). It never re-evaluates resources already in etcd. KEP-3488 lists auditing already-written resources as out-of-scope (deferred to the ecosystem). Stable workloads can go indefinitely without any compliance signal, and the orphan guard's *background* signal disappears. This gap is **architectural, not a version-maturity problem** — no Kubernetes version closes it.
3. **The "Audit" word maps, the observability behind it does not.** Native Audit gives you an audit-log line on *failure only*; the absence of a line is not proof of compliance. Kyverno Audit gives you a queryable per-workload pass/fail record plus background re-evaluation.

The honest conclusion: **Kyverno stays as the engine for the floor.** Native VAP is a credible *north-star / engine-agnostic option* and is already useful as a belt-and-braces second gate, but a native-only build silently drops the project's measurability and continuous-re-evaluation guarantees — exactly the proxy-to-ground-truth upgrade the mea-culpa set out to make. Note that in every "remediation" path examined, the thing that fills the gap is *still Kyverno* (its reports-controller), which defeats the purpose of removing it.

## 2. The Kyverno-dependency surface

| What the design uses Kyverno for | Criticality | Native-CEL substitutable? |
|---|---|---|
| Admission gate (Deny) for the catastrophic minority | core | Yes (VAP Binding `validationActions: [Deny]`) |
| Audit lane-keeping for the ~80% surface | core | Partial — request-time only; loses PolicyReport |
| Enforcement-action axis (Audit vs Deny), decoupled from cadence | core | Yes, but axis lives on the *Binding*, not the policy body |
| CEL ValidatingPolicy as the authoring API | core | Native VAP is CEL; different object model |
| Multi-version coexistence — collision-free objects via `nameSuffix` | core | Yes, with coordinated patching of the Binding's `policyName` |
| Multi-version coexistence — self-selection via label `objectSelector` | core | Yes (`spec.matchConstraints.objectSelector`) |
| Orphan / catch-all guard | core | Partial — needs externally-reconciled ConfigMap param |
| PolicyReports for measurable ground-truth | core | **Gap — no native equivalent** |
| Background scans (continuous re-evaluation) | important | **Gap — no native equivalent** |
| One engine governing Crossplane cloud-plane CRs | core | Yes (VAP `matchConstraints` on CR kinds) |
| `kyverno apply` / `kyverno test` shift-left | core | **Gap — no native offline CLI evaluator/test harness** |
| In-cluster SSA dry-run exercising the webhook | important | Yes — VAP evaluates dry-run admission requests |
| Carrying the "why" as advisory metadata | important | Yes — `metadata.annotations`, engine-agnostic |
| Deterministic policy bodies (no time logic) | important | Yes — authoring discipline, engine-neutral |
| `PolicyException` (carried forward, not relied on) | nice-to-have | No native exception object; not load-bearing |
| Engine install + ordering as a Flux dependency | core | N/A — VAP is in-tree, removes the HelmRelease/cert ordering need (a genuine simplification) |

## 3. Capability-by-capability mapping

| Capability | Native mechanism (API + version) | Verdict | Severity |
|---|---|---|---|
| Deny gate | `ValidatingAdmissionPolicyBinding.spec.validationActions: [Deny]` (`admissionregistration.k8s.io/v1`, GA 1.30) | Parity | — |
| Audit lane-keeping (request-time) | `validationActions: [Audit]` → audit-log annotation only | Partial | major |
| Enforcement-action axis | `validationActions` on the **Binding** (Deny/Audit/Warn; Deny+Warn cannot combine) | Partial | minor (wiring) |
| CEL authoring API | `ValidatingAdmissionPolicy.spec.validations[].expression` (CEL) | Parity | — |
| Coexistence — distinct objects | N VAP objects, `nameSuffix` patched on policy **and** Binding `policyName` | Partial | minor |
| Coexistence — label self-selection | `spec.matchConstraints.objectSelector.matchLabels` | Parity | — |
| Orphan guard | catch-all VAP + `paramKind: ConfigMap` / `paramRef` + CEL membership test | Partial | major |
| PolicyReports (ground-truth) | none in-tree | **Gap** | blocker |
| Background scan | none in-tree (KEP-3488 non-goal) | **Gap** | blocker |
| Cloud-plane CRs (Crossplane) | VAP `matchConstraints.resourceRules` on CR kinds | Parity | — |
| Shift-left CLI (`apply`/`test`) | no in-tree offline evaluator/test harness | **Gap** | major |
| SSA dry-run gate | VAP evaluates dry-run admission requests; abort-before-apply holds | Parity | — |
| Advisory "why" metadata | `metadata.annotations` | Parity (not-needed from engine) | — |
| Deterministic bodies | authoring discipline; CEL has no required time funcs | Parity | — |
| Mutation (not used by floor) | `MutatingAdmissionPolicy` (`admissionregistration.k8s.io/v1`, **GA shipped in 1.36**) | Not-needed | — |

**Enforcement-split.** The Deny/Audit verdict is structurally sound: Warn (HTTP 299) is also present, exceeding the design's two named tiers (which is harmless — the design only uses Audit/Deny). One structural wrinkle: native VAP puts `validationActions` on the *Binding*, not the policy body, so achieving "this version gates, that version lane-keeps" needs either two Bindings or two VAP objects per version. *What would need to be true:* each version's Binding objects carry the `nameSuffix` too, and the kustomize overlay patches the Binding's `policyName` to track the suffixed policy name. Manageable, but it is explicit wiring Kyverno absorbs into a single `spec` field. **Correction reflected:** the original "GA targeted v1.36" framing for MutatingAdmissionPolicy is stale — it *shipped* GA in v1.36 (`[stable]`, enabled by default), and was alpha in v1.32 (not v1.30). Mutation is not used by the floor, so this is informational.

**Multi-version coexistence.** `objectSelector` is a real field on `MatchResources` in GA v1 VAP, so per-version label self-selection works. But the adversarial pass downgraded two claims to *partly*: (a) `objectSelector` filters *which objects a policy acts on* — it is an admission-time label filter, not an inherent per-schema-version router; the "one label, two jobs" trick works only if labels are structured deliberately. (b) `kustomize nameSuffix` does **not** "apply identically" — the Binding references the policy by `spec.policyName`, so suffixing the policy without a coordinated patch on the Binding yields a broken reference. *What would need to be true:* the overlay patches both objects in lockstep, and the version label is treated as the sole match key (not conflated with CRD versioning).

**Measurability.** This is where the design breaks. Native VAP offers three thin surfaces — the audit-log annotation (failures only), two apiserver metrics, and Warn headers. **Correction reflected (claim downgraded false→corrected):** those metrics (`apiserver_validating_admission_policy_check_total`, `..._check_duration_seconds`) are **beta**, not alpha as originally stated — better than feared, but still only counters/histograms labelled by policy and result, not per-workload records. None of this produces the `wgpolicyk8s.io` objects ADR-0008 and Policy Reporter consume. *What would need to be true:* a controller that bridges admission events **and** a periodic re-scan into PolicyReport CRs, plus Policy Reporter declaring native-VAP/audit-log as a first-class source. Today the only thing that does the bridging is Kyverno's own reports-controller.

**Background scan.** No native loop exists, by design (KEP-3488). **Correction reflected (claim downgraded partly):** the KEP frames "auditing already written resources" as an example of ecosystem *framework* work it defers, not a standalone bullet labelled "background scanning" — directionally the same conclusion, but stated precisely. *What would need to be true:* an out-of-tree audit controller (Gatekeeper-style) listing live resources, re-evaluating with the CEL evaluator library (`k8s.io/apiserver/pkg/admission/plugin/...`), and writing PolicyReports. **Correction reflected:** Kyverno's `--validatingAdmissionPolicyReports=true` flag generates reports for native VAPs but **admission-time only** — it does *not* background-scan existing resources against native VAPs. So even the Kyverno shim does not fully close this for native objects.

## 4. What would need to be true (consolidated checklist)

For an all-native-CEL floor that preserves the design's promises:

- [ ] **PolicyReport emitter exists** — a controller writes `wgpolicyk8s.io/v1alpha2` `PolicyReport`/`ClusterPolicyReport` CRs from VAP results, covering both pass and fail paths. *(No in-tree component does this at any Kubernetes version.)*
- [ ] **Background re-evaluation exists** — a periodic loop re-checks all in-scope live resources against bound VAPs and writes PolicyReports, so pre-existing/drifted/orphaned workloads are visible. *(No in-tree component; KEP-3488 defers this.)*
- [ ] **Dashboard re-sourced** — ADR-0008's "is each workload passing?" signal comes from PolicyReports *or* a replacement audit-log→Prometheus pipeline; Policy Reporter (or equivalent exporter) declares the native source first-class.
- [ ] **Binding-layer wiring** — every policy version gets `nameSuffix`-named Binding object(s) encoding the Audit/Deny choice, with the Binding's `policyName` patched to track the suffixed policy.
- [ ] **Orphan-guard param auto-reconciled** — the installed-versions ConfigMap behind the catch-all `paramRef` is generated from the same ResourceSet matrix that installs/removes versions (Flux Kustomization or controller), so it cannot go stale.
- [ ] **Label discipline** — the version label is the sole `objectSelector` key and is not conflated with CRD schema versions.
- [ ] **Shift-left replacement** — an offline CEL evaluator and a test-fixture harness replace `kyverno apply`/`kyverno test` for `flux build … --dry-run | <evaluator>` and CI assertions (no in-tree CLI exists; would need a bespoke tool — the very thing the design deleted).
- [ ] **Metrics maturity accepted** — the beta VAP apiserver metrics are accepted as the only native instrumentation (counters/histograms, not per-workload truth).
- [ ] **Cloud-plane parity confirmed** — VAP `matchConstraints.resourceRules` proven against Crossplane CR kinds in KiND; Lula/OSCAL wired to a PolicyReport-or-equivalent query target (Lula currently queries cluster state directly and does not fill the per-workload gap).
- [ ] **Cluster floor ≥ 1.30** for GA `admissionregistration.k8s.io/v1`.

## 5. Residual gaps with no clean native answer

1. **PolicyReports (blocker).** No native object. Realistic workarounds, all imperfect: (a) **run Kyverno's reports-controller alongside native VAP** via `--validatingAdmissionPolicyReports=true` — but this re-introduces Kyverno (defeating the exercise) *and* is admission-time only; (b) build an **audit-log → exporter → Prometheus** pipeline outside the Kubernetes object model — loses kubectl-queryable per-workload records and the wg-policy ecosystem; (c) use another wg-policy emitter (Gatekeeper's policyreport controller, Kubescape) — that is "replace Kyverno with a different engine," not "go native."
2. **Background scan (blocker).** No native loop. Workarounds: a Gatekeeper-style audit controller (third-party); scripted list-and-evaluate using the CEL evaluator library run as a sidecar (no shipping implementation); or accept admission-time-only coverage and lose retroactive/drift/orphan-background signals. **The orphan guard degrades from a continuous signal to an admission-only one** — a workload pinned to a retired version sits silently un-reported between admission events, re-opening exactly the silent-ungovernance gap the guard was built to close.
3. **Shift-left CLI (major).** No in-tree `apply`/`test`. Either keep `kyverno` CLI as a *dev/CI-only* tool against native VAP objects, or build a bespoke evaluator — reintroducing the "bespoke tooling" the design deleted.
4. **`gitsign`/source verification (out of scope here).** Already a Flux/source-controller gap (`GitRepository.spec.verify` is PGP-only, #1068), not a Kyverno or CEL concern; verification runs in CI regardless of engine.
5. **Known frictions that change shape but persist.** flux2 #2620 (status/default mutation read as "configured" on every reconcile) is *reduced* under native VAP — there is no Helm-installed controller mutating Kyverno CRD status the same way, though the API server still defaults fields. flux2 #4911 (deletes don't trigger webhooks consistently) is engine-independent and remains.

## 6. Kubernetes version floor

- **`ValidatingAdmissionPolicy` / `...Binding`:** `admissionregistration.k8s.io/v1`, **GA in Kubernetes 1.30** (feature gate removed, always on). Earlier: `v1beta1` (1.28+), `v1alpha1` (1.26+) behind gates — not recommended for a 2026 reference.
- **`spec.matchConstraints.objectSelector`:** present in GA v1 (≥1.30) — confirmed.
- **Audit annotation key `validation.policy.admission.k8s.io/validation_failure`:** available from 1.27 (beta era). Note #125522 documents a version-window bug where the annotation also fired on *passing* validations — so its presence/absence was unreliable in affected releases; do not treat it as authoritative pass/fail.
- **VAP apiserver metrics:** **beta** (corrected from "alpha"); usable but coarse.
- **`MutatingAdmissionPolicy`:** GA in **1.36** (shipped, enabled by default) — not used by the floor.
- **The PolicyReport/background-scan gap has no version that closes it.** It is architectural; it requires Kyverno (or an equivalent external engine) at any Kubernetes version.

**KiND implications.** Pick a KiND node image ≥ 1.30 (e.g. `kindest/node:v1.30+`) so GA VAP is on by default; everything in the gating path reproduces for free with no cloud spend, and LocalStack covers any cloud provisioning, exactly as the Kyverno floor intends. **But the measurable pillar will not reproduce natively on KiND** — there will be no PolicyReports and no background counts to drive the dashboard, so the "measurable" and "orphan guard shown" acceptance criteria fail on a native-only KiND unless Kyverno's reports-controller (or a bespoke emitter) is added back.

## 7. Verdict & recommended posture

**Kyverno for the floor; native VAP as the north-star / engine-agnostic option.** This is faithful-to-intent: the floor's binding promises are *measurable ground-truth* (ADR-0008) and *continuous re-evaluation*, and those are precisely the two capabilities native CEL cannot supply without re-adding Kyverno. A native-only floor would quietly regress the project back toward proxy signals — the exact mistake the mea-culpa walked back.

What the exploration *does* validate for the north-star (PRD §2 non-goals, north-star §8):

- The **gate is fully portable.** If the project ever needs to demonstrate engine-agnosticism, the Deny tier, label self-selection, multi-version coexistence, and Crossplane-CR gating all lift to native VAP with modest re-wiring (Binding `policyName` patching, ConfigMap param reconciliation).
- A **hybrid is the most defensible intermediate**: keep policy *bodies* expressed in CEL (already true under Kyverno ValidatingPolicy), so a future migration is a re-targeting of the wrapper objects, not a rewrite of logic. Run native VAP as a second, in-tree gate (belt-and-braces) while Kyverno owns Audit/PolicyReports/background scan.

**Condition under which to switch to native-only:** when an in-tree or CNCF-graduated controller exists that (1) emits wg-policy PolicyReports from VAP results and (2) background-scans existing resources — *and* Policy Reporter consumes it. Until then, switching costs the measurable pillar.

## 8. Confidence & open questions

**High confidence (verified true):** native VAP emits no PolicyReports and writes Audit only to the audit log; native VAP has no background scan; VAP is GA at 1.30; MutatingAdmissionPolicy shipped GA at 1.36; the Kyverno background-scan + PolicyReport + Policy Reporter chain is the literal implementation of ADR-0008.

**Downgraded by the adversarial pass (reflected above):**
- Metrics stability — **was "alpha", corrected to "beta"** (claim marked *false*). Slightly better instrumentation than first stated, still not per-workload.
- Kyverno ValidatingPolicy GA version — **1.18 stable, not 1.17** (v1 API *available* in 1.17). Does not affect the native-vs-Kyverno verdict.
- MutatingAdmissionPolicy lineage — **alpha 1.32, not 1.30; GA shipped, not merely targeted.**
- `objectSelector` "one label, two jobs" — **partly**: the field is real, but it is an admission-time filter, not an inherent version router; depends on deliberate label structure (confidence medium).
- `kustomize nameSuffix` "applies identically" — **partly**: Binding `policyName` cross-reference needs coordinated patching (confidence medium).
- "PolicyReport is Kyverno-exclusive" — **overstated**: wg-policy is an open standard other engines (Gatekeeper, Falco, jsPolicy) emit; it is simply *absent from the native pipeline*.
- KEP-3488 "background scanning is a non-goal" — **partly**: it is deferred to the ecosystem as an example of framework work, not a standalone labelled non-goal; conclusion stands.

**Open questions to resolve on a real KiND ≥1.30 cluster:**
1. Confirm a versioned VAP `objectSelector` correctly self-scopes ≥3 concurrent versions, and that the `nameSuffix`+`policyName` patch chain produces no dangling Bindings.
2. Measure how stale the orphan-guard ConfigMap can get between ResourceSet changes, and whether a Flux-generated ConfigMap closes the reconciliation gap cleanly.
3. Verify VAP evaluates Flux's SSA *server dry-run* requests so the all-or-nothing stage abort holds without Kyverno's webhook.
4. Validate VAP `matchConstraints.resourceRules` against real Crossplane managed-resource kinds (e.g. S3) in KiND + LocalStack.
5. Test whether Kyverno-reports-controller-only (no Kyverno webhook) over native VAPs gives an acceptable *partial* dashboard, and quantify exactly what the admission-time-only limitation costs versus a real background scan.
6. Confirm the audit-annotation pass/fail reliability on the chosen Kubernetes patch version (re: #125522) before any audit-log pipeline is trusted as a compliance source.
