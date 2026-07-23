# Research 08 — enforcement engines, exemption & shift-left options under a fixed Flux anchor

Resolves ticket [`issues/08-research-enforcement-engines.md`](../issues/08-research-enforcement-engines.md).
Informs the architecture decision (02), the exemptions ledger (05), and the shift-left check (03).

**Frame:** Flux CD is fixed and load-bearing (ControlPlane stewards Flux). Everything else — including
the current Kyverno choice — is judged on merit against three criteria the design actually needs:

- **(a) Risk-tuned proportionality** — warn vs block, thresholds, per-control severity.
- **(b) Same evaluation offline** — the *identical* logic runs as a laptop/CI shift-left check, not a
  re-implementation that can drift.
- **(c) First-class scoped + expiring EXCEPTION primitive** — the ledger (05) needs an engine object
  that is namespace/resource-scoped, expires, and can carry external metadata (a risk price, a ledger ref).

---

## 1. How the estate is wired today (local inspection)

Grounding the recommendation in what already exists (`pavf-fleet`, `pavf-policy`):

- **Distribution:** Flux Operator **`ResourceSet`** (`fluxcd.controlplane.io/v1`) in
  `pavf-fleet/clusters/cluster1/policy-versions.yaml`. One `inputs.versions[]` array — each element
  `{version, tag, commit, sunset, policies[]}` — templates, per version: a `GitRepository` pinned to a
  signed tag+commit, one `Kustomization` per policy (path chosen by `plane: workload|cloud`), and a
  single catch-all **orphan-guard** `ValidatingPolicy` whose CEL allow-list is rendered from the *same*
  array so it cannot drift from the installed set. Adding/removing one array element is the only edit
  needed to install/retire a policy version.
- **Enforcement:** Kyverno **`ValidatingPolicy`** (`policies.kyverno.io/v1`, the GA CEL API), pinned
  **≥1.18** (ADR-0003). `validationActions: [Audit]` = lane-keeper, `[Deny]` = gate. Version self-scoping
  is a per-policy **`matchConditions`** CEL check on the `mycompany.com/policy-version` label — *not*
  `matchConstraints.objectSelector`, because Kyverno flattens every policy's objectSelector into one shared
  `ValidatingWebhookConfiguration` (last-reconciled wins), which silently broke multi-version coexistence
  until issue 08 fixed it live.
- **Cloud plane:** Crossplane v2 core + AWS provider-families (S3, RDS); the same `ValidatingPolicy`
  pattern judges Crossplane managed resources (`require-rds-multi-az`, `require-s3-bucket-encryption`).
- **Shift-left today:** `docs/shift-left-dev-workflow.md` — `kyverno test` / `kyverno apply` reproduce the
  admission verdict offline against the pinned tag; `pr-gate-action/pr-gate-check.sh` runs the identical
  commands in CI. Determinism is mandated: **no time-conditional logic in policy bodies** (ADR-0006).
- **Determinism constraint (load-bearing for 05):** ADR-0006 forbids expiry/date logic *inside* policy
  bodies. So any "expiring exception" must expire via an **external, Flux-reconciled** mechanism, never a
  CEL date check in the policy. This is the single biggest constraint on the exception design.

---

## 2. Engine survey against the three criteria

### Kyverno — `ValidatingPolicy` (CEL) + `PolicyException`  ✅ incumbent, recommended to keep

- **(a) Proportionality:** `validationActions` takes `Deny` / `Audit` / `Warn` (Kyverno's ValidatingPolicy
  extends the Kubernetes VAP type, whose valid combos are `[Deny]`, `[Warn, Audit]`, `[Audit]`
  [[k8s VAP docs](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)];
  repo ADR-0003 records `[Audit|Deny|Warn]`). Set **per policy**, promoted Audit→Deny by an editorial PR,
  never on a timer (ADR-0006). Thresholds can be parameterised via CEL variables / autogen, or an external
  param — see §5. This is a clean, three-position proportionality lever already in use.
- **(b) Offline:** **Yes, first-class.** `kyverno apply` and `kyverno test`
  ([[ValidatingPolicy docs](https://kyverno.io/docs/policy-types/validating-policy/)]) evaluate the *same*
  CEL `ValidatingPolicy` file offline with no cluster — this is exactly what the estate's shift-left doc and
  `pr-gate-check.sh` already lean on. **Known limitation:** the CLI evaluates one policy against one
  resource, so it *cannot* reproduce the shared-webhook flattening interaction that only appears with
  multiple versions co-installed (documented in the shift-left doc; `verify-coexistence.sh` covers that gap).
- **(c) Exception:** **`PolicyException`** is a first-class, namespaced CR
  ([[Exceptions guide](https://kyverno.io/docs/guides/exceptions/)]). Applies to `ValidatingPolicy`
  (admission *and* background) since 1.14. Scopes via `match`/`exclude` (kind, namespace, name+wildcards,
  `selector`/`namespaceSelector`) **and** CEL `matchConditions`; `podSecurity{}` allowlisting for PSS.
  Disabled by default — needs `enablePolicyException: true` + an `exceptionNamespace` allow-list (itself a
  useful blast-radius control). It feeds `reportResult` into PolicyReports so an exercised exception is
  *visible*, not silent — directly usable by the 05 ledger's "each exemption subtracts from coverage".
  **The one gap:** *no native expiry/TTL field* on PolicyException (confirmed on the docs page). See §4 for
  how to close it without violating ADR-0006.

### Native `ValidatingAdmissionPolicy` (VAP, no Kyverno)  — north-star only

- **(a)** Same `validationActions` enum + `paramRef` with `parameterNotFoundAction` — arguably the *cleanest*
  proportionality-by-parameter model in the survey.
- **(b)** **No official offline CLI.** You'd re-implement CEL evaluation to shift-left — precisely the
  drift the estate avoids. Disqualifying for criterion (b) today.
- **(c)** No exception object. Exemptions are hand-rolled via `matchConditions` / label exclusions — no
  scoped, expiring, metadata-carrying primitive.
- Rejected as the floor by ADR-0003 (drops PolicyReports, mutation, generation, the offline CLI). Keep as a
  future "engine could thin out to native" note — Kyverno's `autogen` can even *emit* VAPs from a
  ValidatingPolicy, so this is an escape hatch, not a fork.

### OPA / Gatekeeper  — capable, but worse fit here

- **(a)** `enforcementAction: deny | dryrun | warn`, plus `scoped` +`scopedEnforcementActions` to vary the
  action per enforcement point ([[enforcement points](https://open-policy-agent.github.io/gatekeeper/website/docs/enforcement-points/)]).
  Proportionality is there.
- **(b)** **`gator` CLI** (`gator test` / `gator verify`) runs the *same* Constraints+Templates offline and
  honours the enforcement action in its exit code
  ([[gator CLI](https://open-policy-agent.github.io/gatekeeper/website/docs/gator/)]). Solid shift-left story.
- **(c)** **No first-class expiring exception CR.** Exemptions are namespace exemptions (`Config`,
  `--exempt-namespace`) or match-tuning — no scoped, expiring, priced primitive. This is the criterion that
  matters most for 05, and Gatekeeper is weakest here.
- Also: Rego, not CEL — a *second* policy language to teach; and it duplicates what the estate already runs
  on Kyverno. No reason to switch given Flux is the fixed anchor, not the engine.

### Kubewarden  — capable, wrong shape for this design

- **(a)** Per-policy `mode: monitor | protect`
  ([[kwctl](https://docs.kubewarden.io/reference/kwctl-cli)]) — a two-position lever (no distinct warn tier).
- **(b)** `kwctl run` evaluates a policy (Wasm) offline against a pre-recorded `AdmissionReview` — genuinely
  offline, but the unit is a compiled Wasm module + a recorded request, heavier than `kyverno apply` on a
  plain YAML manifest.
- **(c)** No first-class exception CR; exemptions live *inside* policy code/settings.
- Interesting for supply-chain/Wasm-distributed policy, but it fragments the CEL story and adds a Wasm build
  step the estate doesn't need.

### jsPolicy (Loft)  — do not adopt

- **(a)** Arbitrary JavaScript, so anything is *expressible*, but there's no declarative action axis.
- **(b)** No offline CLI equivalent; controllers/webhooks run JS in-cluster.
- **(c)** No first-class expiring exception primitive.
- **Maintenance:** effectively dormant — last meaningful activity ~mid-2024
  ([[releases](https://github.com/loft-sh/jspolicy/releases)]). Betting a 2026 governance reference on it
  contradicts "faithful to intent". Excluded.

### Recommendation table (engine × criteria)

| Engine | (a) Proportionality | (b) Same eval offline | (c) Scoped+expiring exception | Verdict |
|---|---|---|---|---|
| **Kyverno `ValidatingPolicy` + `PolicyException`** | ✅ `Deny`/`Audit`/`Warn` per policy | ✅ `kyverno apply`/`test` (single-policy caveat) | ⚠️ first-class scoped exception, **no native expiry** → close via TTL/Flux (§4) | **Keep — best overall fit** |
| Native VAP (CEL) | ✅ + `paramRef` | ❌ no official offline CLI | ❌ no exception object | North-star only |
| OPA/Gatekeeper | ✅ scoped actions | ✅ `gator` | ❌ namespace exemption only, no expiry | Capable, weaker on (c); Rego tax |
| Kubewarden | ⚠️ monitor/protect (2-pos) | ✅ `kwctl run` (Wasm+AdmissionReview) | ❌ in-policy only | Wrong shape, fragments CEL |
| jsPolicy | ⚠️ code, no axis | ❌ | ❌ | Dormant — exclude |

---

## 3. `PolicyException` deep-dive (for the 05 ledger mechanism)

Exact capabilities and limits ([[Exceptions guide](https://kyverno.io/docs/guides/exceptions/)]):

- **Object:** a namespaced CR (`PolicyException`). Always namespaced, but *can* exempt cluster-scoped
  resources. Gated globally by `enablePolicyException: true` + `exceptionNamespace` allow-list.
- **What it targets:** `ValidatingPolicy` / `ImageValidatingPolicy` (admission + background), plus
  Generating/Mutating/Deleting and legacy ClusterPolicy rules. References the policy by name; a namespaced
  policy is `<namespace>/<name>`.
- **Scoping:** `match`/`exclude` on kind, namespace, name (wildcards), `selector`/`namespaceSelector`, **and**
  CEL `matchConditions`. Can allowlist specific values (e.g. `exceptions.allowedValues`) and specific PSS
  controls (`podSecurity{}` → `controlName`, `images`, `restrictedField`, `values`). → **Non-transferability
  (05's wedge-prevention) is native:** scope the exception to one team's namespace + the exact resource/policy;
  it cannot leak to another team by construction.
- **Visibility:** `reportResult` surfaces exercised exceptions in PolicyReports → the "each open exemption
  subtracts from coverage / adds to residual £" maths (05/06) reads real report data, not a spreadsheet.
- **External metadata round-trip:** standard Kubernetes `metadata.annotations`/`labels` — so a **risk price**
  and a **ledger ref** ride as annotations
  (e.g. `mycompany.com/risk-price: "4200"`, `mycompany.com/ledger-entry: "EX-2026-014"`). Kyverno doesn't
  interpret them, but they round-trip cleanly through git → Flux → cluster → PolicyReport, which is all the
  ledger needs.
- **Expiry — the gap and the fix:** **no native TTL/expiry field.** Two ADR-0006-compliant closes:
  1. **`cleanup.kyverno.io/ttl` label** on the PolicyException — ISO-8601 (`2026-09-01`) or relative (`720h`)
     — and Kyverno's cleanup controller deletes the object when it lapses
     ([[TTL cleanup](https://kyverno.io/docs/policy-types/cleanup-policy/)]). Expiry lives on the *object's
     lifecycle*, not in policy logic → ADR-0006 satisfied.
  2. **Ledger-as-source-of-truth + Flux prune (preferred):** the exception is a *rendered artifact* of a git
     ledger entry (`ResourceSet`, exactly like policy versions today). Remove/expire the ledger entry → Flux
     `prune: true` deletes the exception on the next reconcile. Expiry is a git edit (reviewed, revertible,
     audited) — matching how the estate already retires policy *versions*. The TTL label is the belt to
     Flux's braces (protects against an exception hand-created out-of-band).

**Design consequence for 05:** the ledger entry is authoritative; the `PolicyException` is derived and
disposable. "The exception is only valid if a live, unexpired, in-appetite ledger entry backs it" becomes
literally true — no ledger entry, no rendered exception. Same git-drives-cluster guarantee the `cluster-state`
Kustomization already enforces for the ResourceSet.

---

## 4. Flux's genuinely load-bearing hooks (lean, don't decorate)

Flux is central because versioned governance *is* a distribution problem, and these are jobs only a GitOps
engine does well — each already exercised in `pavf-fleet`:

- **`ResourceSet` (flux-operator) = the versioning primitive.** One `inputs.versions[]` array fans out into
  N GitRepositories + N×M Kustomizations + the orphan guard, collision-free via generated names. Multi-version
  coexistence, the whole point of the repo, is a *template expansion*, not hand-maintained YAML. **The
  exceptions ledger should reuse this exact pattern** — an `inputs.exemptions[]` array rendering
  `PolicyException` + (optionally) a risk-report object per entry.
- **`GitRepository` pinned to `tag` + `commit` (+ gitsign) = immutable, provenance-checked distribution.** A
  policy version is a signed git ref; the shift-left check verifies the *same* tag the cluster runs. This is
  what makes "same evaluation offline" trustworthy, not just reproducible.
- **`Kustomization` `prune: true` = prune-on-retire.** Drop a version (or exemption) from the array → Flux
  deletes its objects. Retirement is a git deletion, not a runbook. This is the mechanism that makes an
  *expiring* exemption safe (§3 fix #2).
- **Drift-heal (reconcile loop).** The estate found this the hard way: the ResourceSet inputs had been
  hand-edited out-of-band, causing a real admission failure until the `cluster-state` Kustomization put it
  under continuous reconciliation. For a *governance* control plane, "git is the only way cluster state
  changes" is the security property, not a nicety.
- **`dependsOn` + `healthCheckExprs` = ordered, gated rollout.** Cloud policies wait on
  `crossplane-providers` (CRDs Established); every policy Kustomization health-gates on the
  `ValidatingPolicy` reporting `Ready`. Per-team `Kustomization` `interval` gives independent reconcile
  cadence (03's "per-team cadence").
- **notification-controller (`Provider`/`Alert`) = the event spine.** Already broadcasts policy source-revision
  changes; the natural carrier for "deploy-time denial fired" alarms (03's culture wiring) and
  exemption-granted/expired events (05).
- **Image automation** — *not* load-bearing here (policy is the artifact, not a container image); note it as
  available but unused, so the design doesn't invent a reason for it. (ponytail: unused hook, wire it only if
  a policy ever ships as an OCI artifact.)

**Net:** the design leans on ResourceSet (versioning), pinned GitRepository (provenance), prune (retirement),
reconcile (drift-heal), dependsOn/health (ordering), notifications (events). That's Flux doing six real jobs,
not one decorative one.

---

## 5. Crossplane's possible role

The estate already runs Crossplane v2 as a *cloud plane* (targets of policy). The ticket asks whether it could
*also* model the governance contract. Assessment:

- **Model the cluster's "supported policy versions" contract? — Not needed; the `ResourceSet` inputs array
  already IS that contract.** `policy-versions.yaml`'s `inputs[0].versions[]` is a consumable, git-hosted,
  Flux-reconciled list of exactly what the cluster supports. Wrapping it in a Crossplane XR/Composition adds a
  control loop and a CRD for no new capability. **Skip it** (ponytail: speculative abstraction; the array is
  already the API — 03 should consume *it*, via `kubectl get resourceset ... -o jsonpath` or the git file).
- **Model org cloud posture / risk inputs? — This is Crossplane's real, legitimate lane.** If the 04/06 risk
  maths need *live cloud facts* (is this RDS actually Multi-AZ, is that S3 bucket actually encrypted, region,
  account), Crossplane managed resources already surface observed `status.atProvider` — a genuine source of
  posture truth an offline manifest check can't see. That's complementary to admission policy, not a
  replacement. Worth a place **only if** the risk model consumes live cloud state; otherwise defer.
- **Verdict for 02:** keep Crossplane as the *cloud plane it already is* (a policy target); do **not** promote
  it to model the version contract. Consider it for *live posture inputs* to quantification (06) if/when that
  ticket needs observed cloud state. Don't build it speculatively.

---

## 6. Shift-left / version-skew prior art (for 03's compatibility contract)

- **kubectl ±1 version skew** ([[version-skew-policy](https://kubernetes.io/releases/version-skew-policy)]):
  kubectl is supported within one minor of kube-apiserver; HA apiservers within one minor of each other.
  This is the canonical "client and server negotiate a compatibility window" precedent 03 should borrow: adopt
  a declared **±1 policy-version window** (cluster supports `{1.0.0, 2.0.0, 2.2.0}`; a workload on `2.0.0`
  against a cluster wanting `≥2.2.0` is one-minor-stale = warn, two = block), rather than exact-pin (too
  brittle across the estate) or unbounded range (defeats the point).
- **API discovery** as the "server advertises what it supports" analogue: Kubernetes clients discover
  supported groups/versions from the apiserver's discovery endpoint. The estate's equivalent already exists —
  the `ResourceSet` inputs array — so 03's "server advertises supported versions" is a *read* of that array
  (live via `kubectl get resourceset`, or the git file for a fully-offline check), no new discovery endpoint
  or ConfigMap needed.
- **`paramRef.parameterNotFoundAction`** (native VAP) is a neat prior-art pattern for "target cluster doesn't
  support this policy version": `Allow` vs `Deny` when the referenced parameter/version is absent — a ready
  vocabulary for 03's "compatible / incompatible when a control tightened Audit→Deny between versions".
- **"Compatible" across an Audit→Deny promotion:** the hard case. A workload that passed under `2.0.0` (Audit)
  can *fail* under `2.2.0` (Deny) unchanged — this is by design (ADR-0003/0006). So the compatibility check
  must run the target version's *actual action*, which `kyverno apply` does offline against the pinned tag.
  The estate's existing shift-left doc + `pr-gate-check.sh` already are the "same eval runs left" mechanism;
  03 extends them to *first resolve the target cluster's supported window* (read the array), then run
  `kyverno apply` for the highest in-window version.

---

## 7. What to KEEP vs RECONSIDER (given Flux is fixed)

**Keep:**
- **Kyverno `ValidatingPolicy` (CEL, `policies.kyverno.io/v1`, ≥1.18).** Wins on all three criteria; only real
  gap (exception expiry) is closeable without an engine change. Switching engines buys nothing when Flux, not
  the engine, is the fixed anchor — and costs a language migration + rewrite of the working shift-left path.
- **`validationActions` Audit/Deny/(Warn)** as the proportionality lever; promotions by editorial PR (ADR-0006).
- **`ResourceSet`-driven distribution + orphan guard** as-is; extend the same pattern to the exemptions ledger.
- **`kyverno apply`/`test` as the offline shift-left engine** (single-policy caveat noted).

**Reconsider / decide in 02:**
- **Adopt `Warn` as a distinct middle tier?** Today it's binary Audit/Deny. `Warn` (HTTP warning at admission,
  no block, no PolicyReport-Audit-lane) could be the "proportionate nudge that the developer *sees at deploy*"
  rung between silent-Audit and hard-Deny. Cheap to add; worth a design line in 04's proportionality model.
- **Parameterised thresholds.** If 04 wants *numeric* risk thresholds (not just Audit/Deny), evaluate CEL
  variables / an external param object (native VAP-style `paramRef` is the cleanest, but off-CLI). Don't build
  until 04 actually needs a threshold knob — Audit/Deny/Warn may be enough.
- **`enablePolicyException` + `exceptionNamespace`** must be turned on and scoped before 05 can ship — a fleet
  config change (Kyverno HelmRelease values in `pavf-fleet/infrastructure/kyverno/`), reviewed like any other.
- **Exception expiry mechanism:** pick **ledger-entry + Flux-prune as primary, `cleanup.kyverno.io/ttl` as
  backstop** (§3). Do *not* put expiry in policy CEL (ADR-0006).
- **Crossplane:** keep as cloud plane; promote to *live posture inputs* for 06 only if that ticket needs
  observed cloud state. Do not model the version contract (the array already is it).

---

## Sources

- Kyverno ValidatingPolicy — https://kyverno.io/docs/policy-types/validating-policy/
- Kyverno Policy Exceptions — https://kyverno.io/docs/guides/exceptions/
- Kyverno Cleanup / TTL — https://kyverno.io/docs/policy-types/cleanup-policy/
- Kyverno 1.16 release (CEL policy GA path) — https://kyverno.io/blog/2025/11/10/announcing-kyverno-release-1.16/
- Kubernetes ValidatingAdmissionPolicy (validationActions, paramRef, matchConditions) — https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
- Kubernetes version skew policy — https://kubernetes.io/releases/version-skew-policy
- Gatekeeper gator CLI — https://open-policy-agent.github.io/gatekeeper/website/docs/gator/
- Gatekeeper enforcement points (scoped actions) — https://open-policy-agent.github.io/gatekeeper/website/docs/enforcement-points/
- Kubewarden kwctl CLI (monitor/protect, offline run) — https://docs.kubewarden.io/reference/kwctl-cli
- Kubewarden vs Kyverno comparison — https://docs.kubewarden.io/admission-controller/1.36/en/explanations/comparisons/kyverno-comparison.html
- jsPolicy releases (maintenance signal) — https://github.com/loft-sh/jspolicy/releases
- Local: `pavf-fleet/clusters/cluster1/policy-versions.yaml`, `pavf-fleet/clusters/cluster1/bootstrap.yaml`,
  `pavf-policy/workloads/kyverno/*/policy.yaml`, `policy-as-versioned-flux/docs/adr/0003`, `0006`,
  `docs/shift-left-dev-workflow.md`
