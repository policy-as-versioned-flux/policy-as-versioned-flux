# 21 — Synthesis: Simplify / Modernise the Faithful Flux Port

**Purpose.** After the faithful expansion of "Policy as [Versioned] Code" onto Flux, this note does the
principal-engineer *subtraction* pass CNS asked for: *"research how to modernise (or better yet consider
where it could be SIMPLIFIED)."* Bias is strongly toward **deletion** — what disappears because Flux does
it natively — not toward adding cleverness. Inputs: dossiers `01`–`03` (originals + thesis) and `10`–`17`
(Flux). Where a claim rests on a specific dossier it is cited inline as e.g. `(see 14)`.

The original is a 2022 GitHub-org-shaped demo: a `policy` repo emitting git tags, a bespoke `policy-checker`
Docker/bash tool, a deprecated `policy-action` reusable workflow, Renovate regexManagers, and KiND e2e
repos (`e2e`, or `cluster1`/`cluster2`). Almost every *mechanism* in that list exists only because 2022
GitOps tooling could not express "versioned policy as a live dependency." Flux v2.8 (Feb 2026) can. The
*ideas* — semver policy, multi-version coexistence, PR-reviewed bumps, measurable compliance, the
lane-keeping/gate split — survive intact. Most of the *plumbing* is deletable.

---

## 1. What Flux makes redundant (component-by-component)

### 1.1 `policy-checker` (Docker/bash) → DELETE. Replace with `flux build|diff` + `kyverno`/`kubeconform` CLI.
The checker's entire job is: read the pinned version, `git clone --branch <tag>` the policy, render the
consumer's manifests, run `kyverno apply`/`checkov` `(see 01 §2.2, 02 §3.2)`. Every step is now native:

- **Read the pin + fetch the exact policy:** an `OCIRepository`/`GitRepository` with `ref.tag` *is* the pin;
  source-controller fetches and verifies it `(see 11, 12)`. No bespoke `yq`/`hcl2json`+`jq` discovery, no
  hardcoded clone URL, no caching gap, no 700 MB `alpine/k8s`+Go+Python image.
- **Render + check, shift-left in CI:** `flux build kustomization --dry-run | kubeconform` and pipe to
  `kyverno apply` / a CEL `ValidatingPolicy` test `(see 13)`. `flux diff` becomes the PR change-preview.
- **Render + check, in-cluster:** kustomize-controller's **server-side dry-run** already exercises the
  admission webhook before applying `(see 13, 14)`. The cluster *is* the checker.

The bash tool also carried real bugs the port simply never inherits: the `hcl2json`/`hcl2tojson`
binary-name mismatch (Terraform path broken as written), checkov version drift (`2.1.242` in the image vs
`3.2.485` in the policy repo), no auth for private policy `(see 02 §3.1)`. **Effort: low. Risk: low.** This is
the single biggest, safest subtraction.

### 1.2 `policy-action` (reusable workflow) → DELETE entirely.
Already deprecated in the original, superseded by `policy-checker` `(see 01 §3)`. With the checker gone too,
there is nothing to wrap. Flux's CLI + the engine's own `kyverno test`/`apply` cover CI. **Effort: trivial.
Risk: none.**

### 1.3 Bespoke KiND e2e harness (`e2e`, `cluster1`, `cluster2`) → SHRINK, don't delete.
The original's KiND CI applies policy at three refs and three apps, then polls `status.ready` jsonpath
`(see 01 §5, 02 §1.4)`. The *intent* — prove N versions coexist and apps bind to the right one — is still worth a
test, but the **machinery shrinks dramatically**:

- `kubectl apply -k …?ref=<tag>` ×N + sleep + jsonpath-poll → a handful of `OCIRepository`+`Kustomization`
  pairs (or one `ResourceSet` over a version matrix, `(see 17)`), with `wait: true`/`healthChecks`/CEL
  `healthCheckExprs` replacing the bespoke `status.ready` polling `(see 13)`.
- `cluster1` (all versions) vs `cluster2` (`>=2.0.0`, app1 dropped) `(see 02 §1.4–1.5)` becomes two cluster
  overlays pointing at different source sets — the canonical Flux monorepo pattern `(see 17)`.

Keep one smoke test; delete the hand-rolled readiness loops and the per-version `kubectl apply` lines.
**Effort: medium. Risk: low.**

### 1.4 Renovate regexManagers → SIMPLIFY to Renovate's native `flux` manager (do **not** delete Renovate).
The original abused `regexManagers` to treat a label string / TF var default as a github-tags dependency
`(see 01 §4.1, 02 §4.3)`. Renovate now has a **native `flux` manager** that understands `OCIRepository`/
`GitRepository`/`HelmRelease` `ref.tag`/`digest` directly `(see 16 §5)`. The brittle regex + `lookupName`
legacy keys vanish; you keep PR-native, cross-forge, grouped/scheduled bumps. **Do not** swap Renovate for
Flux image-automation here — image-automation is commit-first with a clunky, forge-specific PR story
`(see 16 §1.5, §6)`, which *loses* the PR-debate ethos CNS cares about. **Effort: low. Risk: low.**

### 1.5 The "count open PRs to measure compliance" trick → REPLACE with first-class Flux signals.
The original measured adoption by GitHub PR search ("a GitHub PR search away", "over 1,222 PRs")
`(see 03 §4d)`. That is a GitHub-org-shaped proxy. Flux exposes the real thing:

- **Which version each cluster runs:** `OCIRepository/GitRepository .status.artifact.revision`, surfaced as
  the `revision` label on `gotk_resource_info` kube-state-metrics `(see 15)`. No PR-counting; you read the
  *actual resolved version* per cluster.
- **Is it actually compliant:** Kyverno **PolicyReports** via Policy Reporter, joined with the revision in
  one cluster-labelled Grafana `(see 14, 15)`. This is *stronger* than the original — the PR count measured
  "did someone accept a bump," not "is the workload passing."
- **Per-PR/commit compliance:** notification-controller writes **git commit status** (green tick / red cross)
  onto the reconciled commit, with `commitStatusExpr` giving each cluster its own status context, gateable by
  branch protection `(see 15)`. This is the modern, native form of the original CI gate.

**Effort: medium. Risk: low** — and it upgrades the *measurable* "-able" property from proxy to truth.

---

## 2. PUSH vs PULL distribution — recommendation: **OCI artifacts, PUSH-pinned**

Two independent axes are often conflated. Keep them separate.

**Transport (git tags vs OCI artifacts):** recommend **OCI**. The policy bundle pushed via
`flux push artifact` is immutable, content-addressed by digest, cosign/notation-verifiable *natively* by
source-controller (`spec.verify` → `SourceVerified` condition, blocks unverified) `(see 12)`, and can carry
SBOM/SLSA attestations on the same digest `(see 12)` — directly satisfying the talk's "policy is a dependency,
so supply-chain is not a new problem." Git tags are mutable (a tag can be force-moved), have no native
in-source signature gate, and conflate "source repo" with "released artifact." OCI also unifies the k8s and
(future) non-k8s policy into one registry-as-source-of-truth. The cost is one `flux push artifact` step in
the policy repo's release pipeline — trivial, and it *replaces* the manual tag-push the original did by hand
(the `release` job was commented out, tags pushed manually `(see 01 §1.7)`).

**Resolution (pinned commit-back vs live range):** this is the *separate* PUSH-vs-PULL question and the
answer is **per-environment** — see §3. OCI supports both (`ref.digest` pin, `ref.semver` range) `(see 11, 12)`.

So: **OCI transport, default to pinned `ref.tag`/`ref.digest` + Renovate auto-PR**, with live `ref.semver`
reserved for environments that explicitly opt into liveness. OCI does genuinely *simplify* (deletes the
checker's clone logic, gives free signature verification); the git-tag origin was an artefact of 2022, not a
design choice worth preserving.

---

## 3. Pin-vs-range — recommendation: **range in dev, pinned in prod** (a genuine, nuanced split)

This is the load-bearing trade-off and it is **not** a pure simplification. Dropping pins for live
`ref.semver` everywhere would be *lighter* (zero extra machinery, most GitOps-pure `(see 16 §4)`) but it
**surrenders the per-version review gate** — and the PR-based debate is the thing CNS most cares about
(*"debate happens in PRs, not exemption requests"*, `(see 03 §3)`). For *policy* specifically, a bad bump
breaks admission cluster-wide `(see 16 §4)`, so the gate has real value. Equally, pinning *everywhere*
re-imports the original's manual-bump toil that the thesis wanted to automate away.

The honest answer is environment-differentiated, which the canonical Flux monorepo already expresses via
overlays `(see 17)`:

- **dev / staging:** live `ref.semver` range (e.g. `>=2.0.0-0`) — the policy author's changes flow in within
  one reconcile interval; this *is* the fast feedback loop, and a broken policy here is cheap. This restores
  the "lane-keeping assist" feel for the 80% surface area.
- **prod:** pinned `ref.tag`/`ref.digest`, bumped only by a reviewed **Renovate PR**, gated by CI
  (`flux diff` + commit status) and branch protection `(see 15, 16)`. This preserves the reviewable-control
  ethos exactly where catastrophe lives — and aligns with the mea-culpa's "locked door" for the gate-class
  policies `(see 03 §4c)`.

This is not a loss of the ethos; it is the ethos *applied proportionally to risk*, which is precisely the
guardrail-vs-lane-keeping distinction the refined thesis demands `(see 03 §4c)`.

---

## 4. The Terraform / cloud gap — recommendation: **narrow it, honestly; don't over-promise**

The original covered Terraform with Checkov-in-CI (the `infra*` repos, `policy-checker`'s TF path) — which
is *shift-left only*: it never reconciles, never measures live drift, and was the buggiest part of the
original `(see 01 §2.5, 02 §3.1)`. There is now a real GitOps answer, with caveats `(see 14)`:

- **Modern, honest:** make cloud intent a **Kubernetes CR** (Crossplane, Cluster API, or `tofu-controller`/
  flux-iac), then *the same versioned Kyverno/CEL policy engine governs cloud exactly as it governs
  workloads* — runtime reconciliation + PolicyReports, not a one-shot CI scan `(see 14)`. This is genuinely
  better and is on-thesis (one policy engine, one version pin, both planes).
- **The catch:** that is a large adoption cost (you must run Crossplane/CAPI and model your cloud as CRs).
  For the faithful port it is **out of scope of the minimal version** but **the recommended direction for the
  full version**. Keeping raw-Terraform-via-Checkov is defensible as a *transitional* shim, but it should be
  named as the weakest leg, not dressed up as parity. Recommend: **document the CR-as-cloud-intent path as
  the strategic answer; keep Checkov-in-CI only as an optional legacy bridge, clearly labelled.**

---

## 5. Post-2023 Flux features that change the design (didn't exist in 2022)

- **OCIRepository maturity (GA, `source…/v1`)** `(see 10, 11, 12)` — makes §2's OCI transport real and is the
  foundation for deleting `policy-checker`.
- **Native cosign / notation `spec.verify`** `(see 12)` — signature verification moves from "sign the checker
  *image*" (the original's only signing, and it signed the wrong thing `(see 01 §2.4, 02 §3.3)`) to "verify the
  *policy artifact* before it is ever applied." This is the supply-chain story the thesis gestured at.
- **flux-operator `FluxInstance` + `ResourceSet`/`ResourceSetInputProvider`** `(see 17)` — one `ResourceSet`
  templates N clusters each pinned to a different version (the cluster1/cluster2 matrix as data, not repos);
  RSIP can pull semver-filtered tags or GitHub-PR inputs for ephemeral policy previews. Declarative
  replacement for `flux bootstrap` and for the bespoke multi-version e2e wiring.
- **CEL health checks (`healthCheckExprs`, GA 2.5) + `readyExpr` `dependsOn`** `(see 13)` — replace the e2e
  `status.ready` jsonpath polling and gate "policy engine actually healthy" before apps apply.
- **notification-controller git commit status + `commitStatusExpr`** `(see 15)` — the native compliance
  signal replacing PR-counting (§1.5).
- **Kyverno CEL `ValidatingPolicy` (GA), `validationActions`, deprecation of `ClusterPolicy`** `(see 14)` — the
  port should target `ValidatingPolicy`, not the original's `ClusterPolicy` (removal ~Kyverno 1.20). Audit +
  background scan + PolicyReport give measurability for free.
- **Capacitor / flux-operator FluxReport UI** `(see 15)` — replaces any bespoke dashboard ambition.

---

## 6. Minimal Viable vs Full

**Minimal Viable (smallest faithful port that still proves the thesis):**
- One `policy` repo → `flux push artifact` an OCI bundle on release (semver tags).
- One cluster, Kyverno via HelmRelease, policy CRs via a `Kustomization` `dependsOn` the engine `(see 14)`.
- Multi-version coexistence preserved *exactly as the original*: per-version `nameSuffix` + `commonLabels`
  version stamp + in-policy `match.selector` on that label `(see 02 §1.1–1.2)`. N `OCIRepository`+`Kustomization`
  pairs, one per pinned version.
- Consumers pin via `ref.tag`; **Renovate native flux manager** raises bump PRs `(see 16 §5)`.
- CI gate: `flux build … | kyverno apply` (no checker, no action) `(see 13)`.
- Measurability: PolicyReports + `gotk_resource_info` revision label `(see 15)`.
- **No** image-automation controllers, **no** Terraform, **no** flux-operator, **no** ResourceSet.

**Full (the modern reference):** add OCI cosign `spec.verify` + SBOM/SLSA attestations `(see 12)`; commit-status
compliance + Grafana fleet view `(see 15)`; flux-operator `FluxInstance` + `ResourceSet` over a cluster/version
matrix `(see 17)`; per-env pin/range split (§3); cloud-as-CR via Crossplane/tofu-controller for the Terraform
plane (§4); the human-governance layer (dated/reviewed/delete-if-undefended) and last-mile note the thesis
demands `(see 03 §4c–4d)`.

---

## 7. SIMPLIFICATION LEDGER (prioritised)

| # | Original component | Flux-native replacement / deletion | Effort | Risk | Recommendation |
|---|---|---|---|---|---|
| 1 | `policy-checker` Docker/bash tool | DELETE → `flux build/diff` + `kyverno`/`kubeconform` CLI in CI; SSA dry-run in-cluster | Low | Low | **Delete.** Highest-value subtraction; also drops inherited bugs (hcl2json mismatch, checkov drift, no auth, huge image). |
| 2 | `policy-action` reusable workflow | DELETE | Trivial | None | **Delete.** Already deprecated; nothing left to wrap. |
| 3 | Git tags as policy transport | OCI artifact via `flux push artifact` + `OCIRepository` | Low | Low | **Switch to OCI.** Immutable, digest-addressed, native signature verify; replaces manual tag-push. |
| 4 | Renovate `regexManagers` (label/var hacks) | Renovate **native `flux` manager** on `OCIRepository.ref.tag` | Low | Low | **Keep Renovate, simplify config.** Do NOT switch to Flux image-automation (weaker PR story). |
| 5 | "Count open PRs" compliance proxy | `gotk_resource_info` revision label + Kyverno PolicyReports + commit status | Medium | Low | **Replace.** Upgrades *measurable* from proxy to ground truth. |
| 6 | KiND e2e + `status.ready` jsonpath polling (`e2e`/`cluster1`/`cluster2`) | `wait`/`healthChecks`/CEL `healthCheckExprs`; cluster overlays or `ResourceSet` | Medium | Low | **Shrink, keep one smoke test.** Delete hand-rolled loops and per-version `kubectl apply`. |
| 7 | Cosign-signing the *checker image* | `OCIRepository spec.verify` (cosign/notation) on the *policy artifact* + attestations | Low | Low | **Move signing to the policy bundle.** Signs the right thing, gated pre-apply. |
| 8 | `ClusterPolicy` (Kyverno v1) | Kyverno CEL `ValidatingPolicy` + `validationActions` | Medium | Medium | **Migrate.** `ClusterPolicy` deprecated, removal ~1.20; keep Audit during overlap. |
| 9 | Manual per-version `kubectl apply -k …?ref=<v>` | `ResourceSet` over a version matrix (flux-operator) | Medium | Medium | **Full version only.** MVP can use N explicit source/Kustomization pairs. |
| 10 | Checkov-in-CI for Terraform | Cloud-as-CR (Crossplane/CAPI/tofu-controller) governed by the same engine | High | Medium | **Strategic direction for Full; keep Checkov as a clearly-labelled legacy bridge in MVP.** |
| 11 | `flux bootstrap` gotk manifests | flux-operator `FluxInstance` (declarative, distroless/FIPS variants) | Medium | Low | **Full version.** MVP can stay on bootstrap. |
| 12 | Pin *everywhere* (manual bump toil) | Per-env: live `ref.semver` in dev, pinned + Renovate PR in prod | Medium | Medium | **Adopt the split.** Proportional to risk; preserves the PR-debate ethos where it matters. |

---

## 8. What I would NOT change — it is core to the thesis

- **Semver with meaning** (major = breaking tightening, patch = additive widening) — the entire dependency
  framing dies without it `(see 03 §1, 01 §1.3)`.
- **Per-version coexistence via `nameSuffix` + `commonLabels` version stamp + in-policy `match.selector` on
  that label.** This is "the trick" `(see 02 §1.1–1.2)`. Flux changes *how versions are delivered* (OCI/Kustomization),
  not *how they coexist and self-scope*. Preserve verbatim. The "orphaned version label" risk (a dropped
  version silently un-guarding pinned apps `(see 02 §1.5)`) should be surfaced by a guard policy, not papered over.
- **The PR as the unit of debate.** Pinned-prod + Renovate-PR + commit-status keeps every policy bump a
  reviewable, revertible, *defended* change `(see 03 §3, §4c)`. Do not trade this for fully-live ranges in prod.
- **The lane-keeping / gate split.** Build BOTH: Audit/PolicyReport lane-keeping for the ~80% (labels, tags,
  config, metadata) AND a hard Enforce/Deny gate for catastrophic boundaries (access, data classification,
  crypto) `(see 03 §4c)`. A gate-only system is the exact mistake the mea-culpa walked back.
- **One pin string, the single source of truth.** Whatever its form (`ref.tag`/version label), the consumer
  declares its version in one place `(see 01 §7, 02 §7)`.
- **Carry the "why"** — rationale/risk metadata on each policy (and the human-governance layer: dated,
  reviewed, delete-if-undefended) `(see 03 §3, §4c)`. Flux does not provide this; it is thesis-core and must be
  added, not subtracted.
- **The last-mile-to-non-technical-consumers gap** stays an *acknowledged open problem*, not a claimed
  solution `(see 03 §4c)`.

---

## 9. OPEN QUESTIONS FOR CNS (simplification trade-offs)

- If `flux build/diff` + the in-cluster SSA dry-run fully replace `policy-checker`, do you lose anything you
  valued about a single runnable artifact the developer can `docker run` on their laptop — or is `flux diff`
  on a PR a good-enough local story?
- OCI vs git tags as the policy transport: are you willing to give up the "just a git tag, inspectable in the
  GitHub UI" simplicity for OCI's immutability + native cosign verification? Or is the git-tag legibility part
  of the *visible/consumable* ethos you want to keep?
- Per-env pin/range split (range in dev, pinned in prod): does that feel like the right proportional answer,
  or do you want pinned-everywhere to keep every environment's policy version equally reviewable?
- Is the live `ref.semver` range in dev acceptable given it means dev clusters can diverge from each other on
  which version they've resolved at any moment (cross-env drift)?
- Compliance-by-PolicyReport+revision-label vs "a GitHub PR search away": the new signal measures *actual
  pass/fail*, not *bump acceptance*. Is that the measurement you actually wanted, or was "teams have accepted
  the bump" the real adoption metric for the CIO conversation?
- Terraform: are you ready to say cloud-as-CR (Crossplane/tofu-controller) is the strategic answer and demote
  Checkov-in-CI to a labelled legacy bridge — or must the faithful port keep Checkov at apparent parity?
- How much flux-operator (`FluxInstance`/`ResourceSet`) do you want in the *reference* implementation? It is
  elegant for the cluster1/cluster2 matrix but adds a non-core dependency beyond vanilla Flux — does that
  betray "minimal viable"?
- Migrate the reference policies to Kyverno CEL `ValidatingPolicy` now (future-proof, `ClusterPolicy` removal
  ~1.20), or keep `ClusterPolicy` for faithful 1:1 fidelity with the 2022 original?
- The human-governance layer (dated/reviewed/delete-if-undefended) and the last-mile problem are thesis-core
  but Flux gives you nothing for them. Are they in-scope for this port, or explicitly parked as "the part
  versioning doesn't solve"?
- Do you want an explicit "orphaned version label" guard policy (to catch apps pinned to a version a cluster
  has retired), given the original demonstrated that silent-un-guarding gap but never guarded against it?
- Minimal vs Full: which are we actually building first? The ledger assumes MVP = vanilla Flux + OCI +
  Renovate + Kyverno, no image-automation/Terraform/flux-operator. Is that the right floor?
