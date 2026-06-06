# 22 — PRD Decision Register: "Policy as Versioned Code, on Flux"

**Purpose.** A single de-duplicated, prioritised register of every open design decision raised by the
faithful-mapping (20) and simplify/modernise (21) syntheses. Drives the requirements-grilling session
before the PRD. Each item: why it matters, options A/B/C with trade-offs, recommended default + confidence,
and a plain-English Flux primer (since Flux jargon recurs).

**Priority key:** **P0** = blocks the PRD (scope/shape can't be written without it). **P1** = shapes the
PRD. **P2** = detail that can be settled in design.

**Primer — the spine.** *In Flux, you stop running a bash tool that clones the policy. Instead you declare
a "source" object that says "the policy lives at this URL, this version" and a "Kustomization" object that
says "apply it, after the engine is healthy." Flux pulls and applies it continuously. The version pin and
the policy are now declarative data, not a script.*

---

## Theme 1 — Distribution & versioning

### D1.1 — Transport: Git tags vs OCI artifacts `[P0]`
**Why it matters.** This is the foundational shape of the whole port — everything downstream (signing,
verification, the consumer object type, the demo repo layout) hangs off it. The original shipped git tags
only; both syntheses say OCI is the faithful-*intent* upgrade.
*Primer: an "OCI artifact" is the policy bundle pushed into a container registry (like a Docker image, but
it's policy files). `flux push artifact` does this; an `OCIRepository` object pulls it. Git tags are just
tags in a normal repo, pulled by a `GitRepository` object.*
- **A — Git tags + `GitRepository`** (max fidelity to 2022). Trade-off: keeps "just a git tag, inspectable
  in the GitHub UI" legibility; but tags are mutable (force-movable), no native in-source signature gate.
- **B — OCI artifacts + `OCIRepository`** (fidelity to intent). Trade-off: immutable, digest-addressed,
  native cosign verify, carries SBOM/attestations, unifies k8s + future cloud into one registry; costs one
  `flux push artifact` step (which *replaces* the manual tag-push the original did by hand) and gives up
  GitHub-UI browsability.
- **C — Both: Git as authoring plane, OCI as distribution plane.** Trade-off: maximal fidelity + intent, but
  two artifacts to reason about.
- **Recommended: B (OCI). Confidence: high.** 21 §2 is unambiguous; the git-tag origin was a 2022 artefact,
  not a design choice. Grill: does Chris value git-tag legibility as part of the *visible/consumable* ethos
  enough to keep A?

### D1.2 — Resolution: pinned `ref.tag` + Renovate PR vs live `ref.semver` range `[P0]`
**Why it matters.** The thesis's core value is *reviewed* upgrades ("debate happens in PRs, not exemptions").
Live ranges quietly drop the review gate; for policy a bad bump breaks admission cluster-wide.
*Primer: a "pin" is an exact version (`ref.tag: 2.1.1`). A "range" (`ref.semver: ">=2.0.0"`) lets Flux
auto-adopt new versions on its own — no human in the loop. Renovate is a bot that opens a pull request to
bump the pin, so a human reviews each change.*
- **A — Pinned everywhere + Renovate PR.** Trade-off: every bump reviewed/revertible; re-imports some manual
  bump cadence (but automated by Renovate, not by hand).
- **B — Live `ref.semver` everywhere.** Trade-off: lightest, most GitOps-pure; surrenders the review gate the
  whole thesis depends on. Effectively out for policy.
- **C — Per-environment split: range in dev/staging, pinned + Renovate PR in prod.** Trade-off: proportional
  to risk — fast feedback where breakage is cheap, locked door where catastrophe lives; adds the concept of
  environment overlays.
- **Recommended: C (split). Confidence: medium-high.** 21 §3 argues this is the ethos *applied
  proportionally*, matching the lane-keeping/gate distinction. 20 is more conservative (pinned + Renovate as
  the single faithful default, live semver "out"). **This is the sharpest cross-doc disagreement — grill
  hard.** Sub-question: is dev-cluster cross-drift (different dev clusters resolving different versions at any
  moment) acceptable?

### D1.3 — One pin string or two? `[P1]`
**Why it matters.** The original's signature party-trick was ONE string doing two jobs: the Renovate pin AND
the Kyverno selector. In Flux the pin naturally lives on `spec.ref` and the selector on a stamped label.
*Primer: the "selector" is a label on workloads (`policy-version: 2.1.1`) that tells a policy which workloads
it judges. `postBuild.substitute` lets Flux inject the ref value into that label so both stay equal.*
- **A — Force equal via `postBuild.substitute ${policy_version}`.** Trade-off: preserves the one-string magic;
  slightly more wiring.
- **B — Accept two coupled values.** Trade-off: cleaner/explicit; loses the party trick that made the talk land.
- **Recommended: A. Confidence: medium.** The one-string elegance is thesis-identity (21 §8 "one pin string,
  single source of truth"). Grill: is the magic worth the substitution coupling?

---

## Theme 2 — Multi-version coexistence & runtime

### D2.1 — How versions are wired per cluster: N explicit pairs vs ResourceSet matrix `[P1]`
**Why it matters.** Coexistence ("the crux", 20 §3) is delivered by N source+Kustomization pairs. How they're
generated is the MVP-vs-Full fork.
*Primer: a `ResourceSet` (ControlPlane Flux Operator) templates many objects from a table of inputs — e.g. one
row per cluster→version — instead of hand-writing each pair.*
- **A — N explicit `OCIRepository`+`Kustomization` pairs per cluster.** Trade-off: maximal fidelity to the
  cluster1/cluster2 demo, vanilla Flux; verbose at fleet scale.
- **B — `ResourceSet` over a version matrix.** Trade-off: real fleet primitive, DRY; non-core dependency (see D7.1).
- **Recommended: A for MVP, B for Full. Confidence: high.** Both docs converge (20 Q8, 21 §6/ledger #9).

### D2.2 — Orphaned-version-label guard `[P1]`
**Why it matters.** When a cluster retires a version, any workload still pinned to it is matched by *no* policy
and silently un-guarded. The original demonstrated this gap and never closed it; both docs flag it.
- **A — Leave as acknowledged gap (faithful).** Trade-off: 1:1 with original; ships a known silent-failure mode.
- **B — Add a catch-all policy that denies/audits any `policy-version` label not currently installed.**
  Trade-off: closes a real safety hole; is it faithful expansion or a redesign?
- **Recommended: B (as Audit first). Confidence: medium.** 21 §8 says "surface by a guard, not paper over."
  Grill: faithful phase or Full-only?

### D2.3 — Half-deploy / transactional boundary expectations `[P2]`
**Why it matters.** The talk's "✅❌✅✅✅ = ❌" concern is sharper than thought: Flux is eventually-consistent,
not transactional — all-or-nothing *within* a stage, no rollback *across* Kustomizations.
*Primer: Flux applies in stages and dry-runs each first; a rejection aborts that stage before applying, but
partial state can survive across separate Kustomizations. `wait: true` + health checks gate readiness.*
- **A — Accept eventual consistency; heal via re-reconcile + health-gating + PolicyReports.** **Recommended.
  Confidence: high.** This is just how Flux works; design for it. Detail-level, but set the expectation.

---

## Theme 3 — Consumer experience & shift-left

### D3.1 — Local developer story: `flux diff` on PR vs a runnable artifact `[P1]`
**Why it matters.** `policy-checker` was one thing a dev could `docker run` on their laptop. Deleting it (the
single highest-value subtraction) removes that single runnable artifact.
*Primer: `flux build kustomization --dry-run` renders exactly what the cluster would apply; pipe it to
`kyverno apply` to check locally. `flux diff` shows what a PR would change.*
- **A — `flux build/diff` + `kyverno` CLI in CI, SSA dry-run in-cluster (no checker).** Trade-off: native, drops
  inherited bugs (hcl2json mismatch, checkov drift, no auth, 700MB image); the local story is now "run a few
  CLIs" not "one docker run."
- **B — Keep a thin wrapper for laptop ergonomics.** Trade-off: preserves the one-command local UX; reintroduces
  a bespoke artifact to maintain.
- **Recommended: A. Confidence: high.** Both docs agree (21 §1.1 "biggest, safest subtraction"). Grill: does
  Chris lose anything he valued about the single runnable artifact?

### D3.2 — Retire `policy-action` reusable workflow `[P2]`
**Why it matters.** Already deprecated in the original; with the checker gone, nothing to wrap.
- **A — Delete.** **Recommended. Confidence: high.** Trivial, no risk (21 §1.2).

---

## Theme 4 — Compliance visibility / measurement

### D4.1 — What "measurable" means: PR-count proxy vs PolicyReports + revision label `[P1]`
**Why it matters.** The original measured adoption by counting GitHub PRs ("over 1,222 PRs") — a proxy for
"did someone accept a bump," not "is the workload passing." Flux exposes ground truth.
*Primer: `gotk_resource_info{revision=...}` is a Prometheus metric showing which version each cluster actually
resolved. Kyverno PolicyReports show pass/fail per workload. notification-controller writes a green/red commit
status onto each reconciled commit.*
- **A — Adopt PolicyReports + revision label + commit status, one Grafana joins them.** Trade-off: upgrades
  *measurable* from proxy to truth; medium build effort.
- **B — Keep the PR-search proxy.** Trade-off: zero build; but measures bump-acceptance, not compliance.
- **Recommended: A. Confidence: high.** Grill the framing: for the CIO conversation, is "teams accepted the
  bump" actually the adoption metric Chris wants, or is "workloads passing" the real target? (21 §1.5 Q.)

---

## Theme 5 — Scope (k8s-only vs Terraform/cloud; MVP vs Full; demo vs prod)

### D5.1 — MVP vs Full — what are we building first? `[P0]`
**Why it matters.** Sets the entire PRD boundary. The ledger's proposed floor: vanilla Flux + OCI + Renovate +
Kyverno; **no** image-automation, **no** Terraform, **no** flux-operator, **no** ResourceSet.
- **A — MVP floor as above (single cluster, N pairs, CI gate, PolicyReports).** Trade-off: smallest port that
  still proves the thesis; defers fleet/cloud/signing polish.
- **B — Full reference** (OCI cosign verify + attestations, commit-status + Grafana fleet view, FluxInstance +
  ResourceSet matrix, per-env split, cloud-as-CR, human-governance layer). Trade-off: the real reference; large.
- **Recommended: A first, B as the documented north star. Confidence: high.** Confirm the floor explicitly —
  this gates almost every P1 below.

### D5.2 — Terraform / cloud plane: how far? `[P0]`
**Why it matters.** The original's TF path was Checkov-in-CI only (shift-left, no runtime loop) and was the
buggiest part (hcl2json bug). There's now a real GitOps answer but at high adoption cost.
*Primer: "cloud-as-CR" means representing cloud resources as Kubernetes objects (via Crossplane/Cluster API/
tofu-controller) so the *same* Kyverno engine governs cloud the way it governs workloads — runtime, not one-shot.*
- **A — Keep Checkov-in-CI, labelled as a legacy bridge.** Trade-off: matches what shipped, no runtime loop;
  honestly the weakest leg.
- **B — Cloud-as-CR via Crossplane/tofu-controller (same engine governs both planes).** Trade-off: genuinely
  better, on-thesis (one engine, one pin, both planes); large adoption cost (must run Crossplane/CAPI, model
  cloud as CRs).
- **C — tofu-controller `Terraform` CR only (runtime loop for raw TF, no Crossplane).** Trade-off: middle ground.
- **Recommended: A in MVP, B as strategic direction for Full — explicitly labelled, not dressed as parity.
  Confidence: high.** Both docs agree (20 Q6, 21 §4). Grill: is Chris ready to *demote* Checkov publicly?

### D5.3 — Demo (KiND e2e) vs production fleet shape `[P1]`
**Why it matters.** The original proved coexistence only on KiND in CI with hand-rolled `status.ready` polling.
- **A — Shrink to one smoke test; replace polling with `wait`/`healthChecks`/CEL `healthCheckExprs`; two cluster
  overlays.** **Recommended. Confidence: high.** Keep the proof, delete the machinery (21 §1.3).

---

## Theme 6 — Supply chain & signing

### D6.1 — Sign the policy artifact (and verify pre-apply)? `[P1]`
**Why it matters.** The original cosign-signed the *checker image* — the wrong thing. The thesis gestured at
"supply chain is not a new problem" but never closed it.
*Primer: `OCIRepository.spec.verify` makes source-controller check a cosign/notation signature before applying;
the `SourceVerified` condition blocks unverified policy from ever reaching the cluster.*
- **A — `OCIRepository spec.verify` cosign keyless on the policy bundle.** Trade-off: signs the right thing,
  gated pre-apply; depends on D1.1 = OCI.
- **B — Stay unsigned (faithful to what shipped).** Trade-off: 1:1 fidelity; ships the original's actual gap.
- **Recommended: A (Full; optional in MVP). Confidence: high.** Cheap once on OCI (21 ledger #7).

### D6.2 — Does the rationale/"why" get *enforced* via attestations? `[P2]`
*See D8.1 — the rationale's gating question lives there.*

---

## Theme 7 — Fleet / multi-cluster & ControlPlane stack

### D7.1 — Take a dependency on ControlPlane Flux Operator (FluxInstance/ResourceSet)? `[P0]`
**Why it matters.** Fleet templating, declarative bootstrap, FIPS/distroless variants are **ControlPlane Flux
Operator**, not upstream Flux. Relevant given Chris's UK public-sector / G-Cloud context.
*Primer: `flux bootstrap` is the vanilla way to install Flux from a git repo. `FluxInstance` (Operator) is a
declarative replacement that also offers ResourceSet templating and hardened distroless/FIPS images.*
- **A — Vanilla upstream Flux + `flux bootstrap` only.** Trade-off: no extra dependency, maximal fidelity;
  verbose fleet, no FIPS variant.
- **B — ControlPlane Flux Operator (FluxInstance + ResourceSet).** Trade-off: elegant cluster/version matrix,
  hardened images suited to public sector; non-core dependency that arguably betrays "minimal viable."
- **Recommended: A for MVP, B for Full. Confidence: medium.** This is a commercial/positioning call as much as
  technical (ControlPlane's own stack) — grill on intent: is this reference meant to showcase ControlPlane?

---

## Theme 8 — "Policy carries its why" / risk-rationale feature

### D8.1 — Where the rationale lives, and is it *enforced*? `[P1]`
**Why it matters.** Thesis-core ("purposeless policy is pointless"; debate in PRs not exemptions). Flux gives
nothing for this — it must be *added*, not subtracted. Today it's only Kyverno annotations.
*Primer: a cosign "attestation" is signed metadata attached to an artifact's digest — e.g. a threat-model
predicate. Flux verifies *signatures* but not attestation *contents*; gating on the predicate needs Kyverno
`verifyImages`.*
- **A — Keep rationale in Kyverno annotations (faithful, carried not enforced).** Trade-off: 1:1; "why" travels
  but nothing checks it's present/defended.
- **B — Add OCI artifact annotations + `rationale.md` in the bundle (travels with the versioned artifact).**
  Trade-off: surfaces in `OCIRepository.status`; still not enforced.
- **C — Cosign attestation with a risk/threat-model predicate, gated via Kyverno `verifyImages`.** Trade-off:
  enforced "no rationale, no admit"; a step *beyond* the original.
- **Recommended: B in MVP, C as Full ambition. Confidence: medium.** Carrying is faithful; enforcing is new.

### D8.2 — Human-governance layer (dated/reviewed/delete-if-undefended) + last-mile to non-technical consumers `[P1]`
**Why it matters.** Thesis-core per dossier 03, but Flux provides nothing. Risk of over-claiming.
- **A — In-scope: build dated/reviewed/expiry metadata + review process.** Trade-off: delivers the full thesis;
  significant non-Flux work.
- **B — Explicitly park as "the part versioning doesn't solve"; keep last-mile an acknowledged open problem.**
  Trade-off: honest, smaller; thesis stays partially unrealised.
- **Recommended: B for this port, with A flagged as future work. Confidence: medium.** 21 §8 insists last-mile
  stays an *acknowledged* gap, not a claimed solution.

---

## Cross-cutting engine decision

### E1 — Kyverno engine API: legacy `ClusterPolicy` vs CEL `ValidatingPolicy` `[P0]`
**Why it matters.** `ClusterPolicy` is deprecated (removal ~Kyverno 1.20, ~Oct 2026); the original is entirely
`ClusterPolicy`/`validationFailureAction`. This affects how the version self-selector is expressed and whether
policy bodies are rewritten.
*Primer: `ValidatingPolicy` is Kyverno's newer CEL-based policy type; `validationActions: [Audit|Deny|Warn]`
replaces the old `validationFailureAction: Audit|Enforce`.*
- **A — Keep `ClusterPolicy` (verbatim 1:1 fidelity).** Trade-off: matches original exactly; builds on a type
  being removed within the year.
- **B — Migrate to CEL `ValidatingPolicy` + `validationActions`.** Trade-off: future-proof, free background-scan
  measurability; rewrites the policy bodies.
- **Recommended: B. Confidence: high.** 21 §5/ledger #8 is firm; keep Audit during version overlap. Grill: is
  verbatim fidelity worth building on a removed API?

### E2 — Stay Kyverno-only? `[P2]`
- **A — Kyverno-only (faithful; reference engine both eras).** **Recommended. Confidence: high.**
  Gatekeeper/Kubewarden map identically onto the Flux shape; treat engine-agnosticism as later (20 Q10).

---

## Grilling order (suggested)
P0 first, in this sequence: **D5.1 (MVP/Full floor) → D1.1 (OCI) → D1.2 (pin/range) → E1 (Kyverno API) →
D5.2 (Terraform) → D7.1 (ControlPlane dependency)**. These six fix the PRD's shape; everything else (P1/P2)
is detail within that frame. The single biggest live disagreement between the two syntheses is **D1.2**
(20 = pinned-everywhere faithful default; 21 = per-env split) — resolve it explicitly.
