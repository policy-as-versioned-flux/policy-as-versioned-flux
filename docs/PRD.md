# PRD — Policy as Versioned Code, on Flux

| | |
|---|---|
| **Status** | Draft for review |
| **Author** | Chris Nesbitt-Smith (CNS) with Claude |
| **Posture** | Faithful-to-intent build. A separate [north-star report](north-star-modern-reference.md) documents the fuller modern reference. |
| **Decisions** | [ADR-0001](adr/0001-transport-signed-git-tags-gitsign.md)…[ADR-0009](adr/0009-oscal-attestation-via-c2p.md); ubiquitous language in [CONTEXT.md](../CONTEXT.md) |
| **Research** | `research/01`–`03` (original work + thesis), `research/10`–`17` (Flux), `research/20`–`22` (synthesis) |

> **One-line summary.** Re-implement CNS's *Policy as [Versioned] Code* thesis on Flux CD —
> distributing organisational policy as a semantically-versioned, signed dependency, governed by a
> single [Kyverno](https://kyverno.io) engine across both a Kubernetes workload plane and a [Crossplane](https://crossplane.io) cloud plane, with
> reviewed (PR-gated) upgrades, multi-version runtime coexistence, ground-truth compliance, and an
> agent-assisted human-governance layer — proven reproducibly on [KiND](https://kind.sigs.k8s.io).

---

## 1. Background & thesis

Policy in most organisations is emotionally-led, slow to change, hard to communicate, and harder to
measure; it accretes case-by-case exemptions like case law. *Policy as code* tools (Kyverno, OPA,
Checkov, …) help, but most deployments make policy an **opaque deploy-time gate** that engineers
reverse-engineer by hitting "computer says no". The thesis: **treat policy as a versioned software
dependency** — visible, communicable, consumable, testable, usable, updatable, measurable — and let
the risk mitigations move as fast as the risk, **just as features already move as fast as the
opportunity**. Modern delivery lets the product manager chase opportunity risk at deploy cadence —
features ship continuously. Defensive risk should travel at the same speed; today policy is the one
passenger left behind, still moving at memo-and-noticeboard pace while everything around it ships.

The **refined thesis** (the "mea culpa"), which this PRD honours over the original talk:

- **Lane-keeping vs. gate** (after [Gregor Hohpe](https://platformengineering.org/talks-library/the-magic-of-platforms)). Most of the policy surface enterprises struggle
  with — labelling, tagging, configuration standards, operational metadata — should be
  *lane-keeping*: a versioned dependency, adopted gradually, nudging not blocking. A *catastrophic
  minority* — access control, data classification, cryptographic key management; anything governing
  *whether a workload may exist at all* — belongs at the **gate**: "a locked door." **Build both.**
  A gate-only system is the exact mistake the mea-culpa walked back.
- **Carry the "why".** Each policy carries its risk/rationale so disagreement is resolved by a
  **pull request to the policy**, not an out-of-band exemption. "Purposeless policy is potentially
  practically pointless policy."
- **The human-governance layer.** Versioning distributes policy to engineers but does not *govern*
  it. After [GDS Way](https://gds-way.digital.cabinet-office.gov.uk/): every policy is **dated, regularly reviewed, and removed if no longer
  defensible** ("Not archived. Not deprecated. Removed.").
- **The last mile.** Versioning reaches technical consumers but not non-technical ones (the talk's
  "Cleaner"). An explicit, partly-cultural problem — to be *attempted*, not over-claimed.

Lineage credit, per the mea-culpa: the idea traces to **[Michael Brunton-Spall's](https://www.youtube.com/watch?v=txEWO4uyVnY)** 2016 [GOTO
Amsterdam talk](https://www.youtube.com/watch?v=txEWO4uyVnY); this work cites it.

### 1.1 What the 2022 implementation proved, and where it fell short

The reference orgs ([`example-policy-org`](https://github.com/example-policy-org), [`policy-as-versioned-code`](https://github.com/policy-as-versioned-code)) demonstrated: semver policy
in git tags; one string serving as both [Renovate](https://docs.renovatebot.com/modules/manager/flux/) pin and Kyverno selector; multi-version
coexistence on one cluster (`nameSuffix` + version-label self-selector); Renovate auto-PRs; a
`policy-checker` for local/CI shift-left; KiND e2e. Shortfalls this PRD closes or honestly carries:
the bespoke bash/Docker checker and its bugs (hardcoded URL, no caching, `hcl2json` mismatch,
Checkov drift), signing the *checker image* rather than the policy, the cloud/Terraform side being
shift-left-only (admitted on stage), the orphaned-version-label silent gap, compliance measured as
*PR-acceptance* rather than ground truth, and the absence of any governance or last-mile story.

---

## 2. Goals / non-goals

**Goals**

1. Distribute policy as a **semver, signed, versioned dependency** consumed by [Flux](https://fluxcd.io/).
2. Support **multiple policy versions concurrently** in one runtime, with reviewed retirement.
3. Govern **both planes** — Kubernetes workloads and cloud resources — with **one** versioned engine.
4. Make every of the **seven "-ables"** demonstrably true (§4).
5. Deliver the refined thesis: **lane-keeping + gate**, **carry the why**, **human governance**,
   **attempt the last mile**.
6. Be **reproducible for free** (KiND) and **faithful to intent** (no bespoke tooling, deterministic
   policy, vanilla-Flux-expressible).

**Non-goals (this build; see north-star report)**

- OCI artifact transport, [cosign](https://github.com/sigstore/cosign) attestations, SBOM, enforced "why".
- Flux-native keyless-git verification (blocked on upstream [#1068](https://github.com/fluxcd/source-controller/issues/1068)).
- A UK CAF/GovAssure [OSCAL](https://pages.nist.gov/OSCAL) catalogue (NIST 800-53r5 is the worked example).
- Real-cloud fleet e2e at scale; a production-grade risk-intelligence agent.
- Engine-agnosticism (Gatekeeper/Kubewarden); Kyverno-only here.

---

## 3. Principles (binding constraints)

| Principle | Source |
|---|---|
| **Faithful to intent** — reproduce the thesis 1:1; let Flux do natively what 2022 hacked | CONTEXT, Q1 |
| **Deterministic policy** — no time-conditional logic in policy bodies | ADR-0006 |
| **Reviewed upgrades** — pinned everywhere; new versions only via a reviewed Renovate PR | ADR-0002 |
| **Two axes are independent** — adoption cadence (pin/range) ≠ enforcement action (Audit/Deny) | ADR-0002/0003 |
| **One engine, both planes** — same versioned Kyverno governs workloads and cloud | ADR-0004 |
| **Thesis stays vanilla-Flux-expressible** — the Operator is install/fleet sugar, not the mechanism | ADR-0005 |
| **No bespoke tooling** — native CLIs for shift-left; the bash checker is deleted, not ported | CONTEXT |
| **Carry, don't (yet) enforce, the why**; the engine never consumes advisory metadata | ADR-0007 |
| **Proportionality** — lane-keeping for the ~80%, a hard gate only for catastrophic boundaries | thesis |

---

## 4. The seven "-ables" as acceptance criteria

The build is accepted only when each is demonstrably true:

| "-able" | Mechanism | Demonstrable evidence |
|---|---|---|
| **visible** | Policy in a public git repo; every cluster's `GitRepository` makes "what/which version/where" queryable | `flux get sources git`, `gotk_resource_info{revision}` |
| **communicable** | Semver tags + release notes + advisory rationale; notification-controller broadcasts version changes | Alert fires on new tag; release notes render |
| **consumable** | A consumer adds one label (workload) / the cluster adds one [`ResourceSet`](https://fluxoperator.dev/docs/crd/resourceset/) input | A new app onboards by setting one `policy-version` label |
| **testable** | `kyverno test` fixtures (pass/fail) double as worked examples | CI runs fixtures; fixtures readable as docs |
| **usable** | `flux build … --dry-run \| kyverno apply` locally and in CI; in-cluster SSA dry-run | A dev reproduces the cluster verdict on their laptop |
| **updatable** | Renovate PRs the pin bump (`automerge:false`): native `flux` manager for literal app sources, a `customManager` for the fleet version-array (§6.2) | A new tag → a reviewable PR within one Renovate run |
| **measurable** | Layered ground-truth: Flux revision + Kyverno [PolicyReports](https://kyverno.io/docs/policy-reports/) + OSCAL via [C2P](https://github.com/oscal-compass/compliance-to-policy-go); PR-state = adoption velocity | One dashboard (four panels, shared `cluster`+`policy-version` variable) answers the four CIO questions (§9); at P1 the workload plane is measured by revision + PolicyReports, OSCAL control-satisfaction lands with the cloud plane at P2 |

---

## 5. Architecture overview

Two planes, one engine, one versioned-dependency mechanism.

```mermaid
flowchart TD
  subgraph Author["policy repo (authoring plane — files in git)"]
    PR["PR w/ rationale + kyverno test fixtures"] --> TAG["signed git tag 2.1.1\n(gitsign keyless -> Rekor)"]
    AGENT["agent governance layer\n(reads rationale+risk+signals)"] -. opens review PRs .-> PR
  end

  subgraph Update["update lifecycle (PUSH, reviewed)"]
    TAG -. new tag .-> REN["Renovate (flux manager for app sources;\ncustomManager for the version-array matrix)"]
    REN -->|PR: bump {version, commit}, automerge:false| FLEET["fleet config repo"]
    FLEET -->|CI: flux build/diff + kyverno apply/test + gitsign verify (offline Rekor bundle, pinned commit)| MERGE{{review + merge}}
  end

  subgraph Cluster["cluster (Flux Operator)"]
    direction TB
    RS["ResourceSet\n(range over {version, commit} array)"] --> SRC["GitRepository(s) pinned per version\n(spec.ref.tag + spec.ref.commit)"]
    SRC --> KS["Kustomization(s) dependsOn kyverno, wait"]
    KS --> KY["Kyverno engine"]
    KY --> VP["ValidatingPolicy *-<v>\n(nameSuffix, version self-selector,\nAudit=lane / Deny=gate)"]
    GUARD["orphan guard (catch-all)"] --> KY
    WL["workloads (label policy-version=<v>)"] -->|admission| VP
    XR["Crossplane CRs (RDS/S3)"] -->|admission| VP
  end

  MERGE --> RS
  VP -->|PolicyReport| OBS["Policy Reporter -> Prometheus"]
  KS -->|reconcile event| NC["notification-controller"]
  OBS -->|PolicyReports both planes| C2P["C2P result2oscal\n-> OSCAL assessment-results"]
  OBS & C2P & SRC --> DASH["one dashboard (4 panels, shared cluster+version var):\nversion-per-estate x passing? x controls satisfied? x adoption"]
```

### 5.1 Repo layout

```
policy-as-versioned-flux/
├── policy/                      # THE versioned policy source (== 2022 `policy` repo)
│   ├── workloads/kyverno/       #   ValidatingPolicy bodies (CEL); nameSuffix + version self-selector
│   │   ├── require-department-label/
│   │   └── require-known-department-label/
│   ├── cloud/                   #   hand-authored RDS/S3 CEL ValidatingPolicies, NIST-mapped (collie's intent, rebuilt)
│   ├── rationale/               #   the "why": rationale.md + advisory metadata per policy
│   ├── tests/                   #   kyverno test fixtures (pass/fail = worked examples)
│   └── .github/workflows/       #   tag -> gitsign-signed release; CI runs fixtures
├── fleet/                       # the config repo Flux reconciles
│   ├── flux-instance.yaml        #   FluxInstance (Operator; distroless/FIPS)
│   ├── resourcesets/             #   ResourceSet over the cluster x policyVersion matrix
│   ├── infrastructure/kyverno/   #   engine HelmRelease + the orphan guard
│   └── clusters/                 #   per-cluster inputs (cluster1 = all versions; cluster2 = >=2.0.0)
├── cloud/                       # harvested from collie: OSCAL 800-53r5 catalogue + Crossplane v2 setup
│   └── c2p/                     #   C2P component-definition (controls <-> policy names) + result2oscal collection job
├── apps/                        # consumers (== app1/2/3) — each carries one policy-version label
├── governance/agent/            # the agent governance demonstrator
├── docs/                        # this PRD, ADRs, north-star report, upstream actions
└── research/                    # the dossiers
```

### 5.2 CRD inventory

`GitRepository` (pinned per version, gitsign-signed source) · `Kustomization` (`dependsOn` engine,
`wait`, `prune`) · `HelmRelease` (Kyverno) · Kyverno [`ValidatingPolicy`](https://kyverno.io/docs/policy-types/validating-policy/) (CEL; Audit/Deny) ·
`FluxInstance` + `ResourceSet` (+ `ResourceSetInputProvider`) · `Provider`/`Alert` (notifications) ·
Crossplane provider CRs + managed resources (cloud plane).

---

## 6. Detailed design

### 6.1 Distribution & versioning — signed git tags (ADR-0001)

Policy is authored and reviewed as files in git, released as **semver git tags**, signed **keyless
with [gitsign](https://github.com/sigstore/gitsign)** ([Sigstore](https://docs.sigstore.dev): ephemeral [Fulcio](https://github.com/sigstore/fulcio) cert via OIDC, logged in [Rekor](https://github.com/sigstore/rekor) — no GPG key custody).
Consumed by a Flux `GitRepository` pinned on **`spec.ref.tag` and `spec.ref.commit`** (the tag's
resolved SHA). Semver carries meaning: **major** = breaking tightening (e.g. free-text → enum),
**minor** = backwards-compatible addition, **patch** = additive widening.

**Integrity — pin the commit, not just the tag (ADR-0001).** A tag-only pin re-resolves every
reconcile, so a force-moved tag would be pulled silently and the cluster would run something CI never
verified. Renovate therefore writes the resolved **commit SHA** alongside the tag (`git-refs`
datasource); Flux pins that immutable commit. Release tags are additionally **forge-protected/
immutable** (GitHub ruleset / Immutable Releases), and `notification-controller` alerts on unexpected
revision drift.

**Known limitation (accepted, ADR-0001):** Flux `GitRepository.spec.verify` is PGP-only (v2.9, Jun
2026, added SSH — still not Sigstore/gitsign) and cannot verify gitsign today, so there is **no
Flux-native verified-source gate on the floor**. Verification runs **in CI / at-merge** (`gitsign
verify` against a **persisted offline Rekor bundle**, `GITSIGN_REKOR_MODE=offline`, gitsign pinned —
so the gate does not depend on Sigstore's public-good Rekor turndown schedule). Closing the on-cluster
gate natively is the single upstream dependency — tracked as a project action against [fluxcd#1068](upstream/fluxcd-source-controller-1068-gitsign.md).

### 6.2 Adoption — pinned everywhere + Renovate PR (ADR-0002)

Consumers and clusters pin **exact** tags (+ commit SHA). New versions land **only** via a reviewed,
CI-gated Renovate PR (`automerge:false`), in **every** environment. No live `ref.semver` ranges. The
PR is the unit of debate that carries the "why".

**Two update surfaces (ADR-0002).** Literal `GitRepository` app sources are bumped by Renovate's
**native `flux` manager**. The fleet's single **`{version, commit}` array** — the one source of truth
the `ResourceSet` expands into per-version sources (§6.4) — lives inside a `ResourceSet` the native
manager cannot parse, so it is bumped by a Renovate **`customManager`** (git-refs datasource, ~10
lines of declarative config, writing both fields). A `customManager` is **not** bespoke tooling in the
sense the "no bespoke tooling" principle forbids (that targets the deleted bash/Docker checker); the
exemption is explicit.

### 6.3 Engine & policy authoring — Kyverno CEL `ValidatingPolicy` (ADR-0003)

Policies are CEL `ValidatingPolicy`. `validationActions` is the **enforcement-action axis**:
`Audit` = lane-keeping (nudge + PolicyReport), `Deny` = gate ("locked door"). This is independent
of adoption cadence. Background scans + PolicyReports give measurability for free.

### 6.4 Multi-version coexistence (the crux) — `ResourceSet` matrix (ADR-0005)

A single cluster runs N policy versions side by side:

1. **Versioned dependency** = N `GitRepository` objects, distinct names, each pinned on its
   `{spec.ref.tag, spec.ref.commit}` pair (§6.1).
2. **Collision-free objects** = the bundle's kustomize `nameSuffix: "-<v>"` (kept verbatim).
3. **Version self-scoping** = each `ValidatingPolicy` matches only workloads carrying its
   `mycompany.com/policy-version` label (CEL `matchConstraints` objectSelector).
4. **Workload opt-in** = the consumer stamps one version label.
5. **Cluster narrows the set** = the fleet holds a **single `{version, commit}` array** (bumped by the
   Renovate `customManager`, §6.2); a `ResourceSet` **`range`s** over it to generate the per-version
   source+Kustomization pairs, and the same array element sets `spec.ref.tag`+`spec.ref.commit` and,
   via `postBuild.substitute`, the policy bundle's self-selector label value. **One semver string,
   reused by three authors** (the ResourceSet input → the source ref + policy label; the consumer
   mirrors it on workloads) — the tag and the selector cannot drift because they template from one
   value (this is what "one value, two jobs — D1.3" now means precisely).
6. **Ordering** = every policy `Kustomization` `dependsOn` the Kyverno `Kustomization`, `wait: true`;
   the cloud-policy `Kustomization` additionally `dependsOn` the Crossplane provider CRDs being
   Established (so the admission webhook is registered — §6.5).
7. **Orphan guard** = one deterministic catch-all `ValidatingPolicy` whose CEL carries a **literal
   allow-list rendered from the same `{version}` array** (`!(label in ['1.0.0','2.0.0','2.1.1'])`),
   regenerated by the ResourceSet on every array change, so it cannot drift from the installed set. It
   flags any workload whose `policy-version` label is not installed. It starts in **Audit**; promotion
   to **Deny** is an **editorial PR** flipping `validationActions` (never automated — ADR-0006), not a
   timed transition. Closes the silent-ungovernance gap.

### 6.5 Cloud plane — harvest collie, rebuild native (ADR-0004)

We **harvest** [`controlplaneio/collie`](https://github.com/controlplaneio/collie) (Apache-2.0) rather than fork its toolchain. collie's Kyverno
policies are *generated* legacy `ClusterPolicy` artifacts (its OSCAL→policy generator is built on the
now-dropped Lula 1), so we take collie's reusable **IP** — the NIST 800-53r5 → RDS/S3 policy intent
and its **OSCAL catalogue** — and rebuild: **hand-author** the RDS/S3 rules as CEL `ValidatingPolicy`,
**version them** as first-class dependencies (gitsign tags + commit pin, Renovate, coexistence,
Audit/Deny), and reshape the OSCAL catalogue into a C2P **component-definition** (§6.6). Policies
target **current Crossplane v2 + AWS provider-family** CRD groups. The same engine that judges
workloads judges Crossplane CRs at admission — closing the runtime-cloud gap the talk admitted. Proof
is **KiND-only, spec-based**: install the provider CRDs (no ProviderConfig/auth/reconcile), apply the
CRs, and Kyverno judges the spec at admission; the cloud-policy `Kustomization` `dependsOn` the
provider CRDs Established, and any `Deny` gate scopes to CREATE/UPDATE excluding provider-authored
status updates. collie's generator, Lula wiring, and EKS/Terraform bootstrap are **dropped**, not
ported.

### 6.6 Compliance / measurable — layered ground-truth (ADR-0008, ADR-0009)

One dashboard, **four panels over four datasources** joined by a shared `cluster`+`policy-version`
template variable (not a PromQL join): **Flux revision** (which version, where) · **PolicyReports**
via Policy Reporter → Prometheus (is it passing) · **OSCAL assessment-results** (controls satisfied)
· **Renovate PR state** (adoption velocity — the 2022 "PR search away", explicitly relabelled). The
OSCAL signal is produced by **Compliance-to-Policy (C2P) `result2oscal`** (CNCF Sandbox, ADR-0009),
which normalises the Kyverno PolicyReports both planes already emit into OSCAL — **no second
validation engine** (this is why Lula was dropped: it ran its own parallel checks). collie's OSCAL
catalogue supplies C2P's control↔policy mapping. The OSCAL doc and Renovate/PR panels use first-party
Grafana datasource plugins (`infinity`, `github`) — no bespoke exporters. Headline = *demonstrable,
machine-checkable control satisfaction*.

### 6.7 Governance — deterministic policy + editorial review + agent layer (ADR-0006, ADR-0007)

Policy bodies are deterministic (no time conditions). "Dated/reviewed/removed-if-undefended" is an
**editorial** action (a reviewed PR), supported by the **agent governance layer**:

- **Inputs:** versioned policy + embedded rationale/risk/ethos + external signals (CVEs, cloud/regulatory
  change, [Wardley climatic movement](https://medium.com/wardleymaps/exploring-the-map-ad0266fad59b)).
- **Output:** noise-reduced **business decisions** surfaced as review PRs/issues ("this rationale may
  be stale because X; consequence Y; do you still defend it?").
- **Boundary:** never edits enforcement; prompts the human. Built as a **bounded demonstrator** (one
  signal source) plus a complete architectural spec.
- **Advisory metadata** (`created`/`lastReviewed`/rationale/risk) is read by humans + agents only,
  never by the engine.

### 6.8 Last mile (attempt)

Auto-generate an **always-in-sync, human-readable policy handbook** from the versioned source (the
"operational manual" can never drift from enforced policy), with **agent-authored plain-language
summaries** of each policy + its "why". Full non-technical adoption remains a named, partly-cultural
open problem.

### 6.9 Shift-left dev story (CONTEXT)

Documented native commands; no wrapper, no checker:
`flux build kustomization … --dry-run | kyverno apply` (and `kyverno test`), `flux diff` for PR
preview, `gitsign verify` for provenance. In-cluster, kustomize-controller's SSA dry-run exercises
the admission webhook before apply.

### 6.10 Lifecycle & the half-deploy (D2.3)

Flux is eventually-consistent, not transactional: SSA dry-runs each stage (a Deny aborts the stage
before applying — all-or-nothing *within* a stage), but there is no rollback *across*
Kustomizations. Design for re-reconcile to heal; gate readiness with `wait` + CEL health checks;
surface partial state via health conditions + PolicyReports.

---

## 7. Proof / demo (CONTEXT)

KiND, reproducible, free (no cloud spend). Workload plane runs fully; the cloud plane is proven at the
**admission level** — current Crossplane v2 + AWS provider-family **CRDs installed in KiND** (no
ProviderConfig/auth/reconcile), Crossplane CR **specs** judged by Kyverno at admission, and **C2P
`result2oscal`** attests control satisfaction from the resulting PolicyReports. **No LocalStack/AWS on
the critical path** (both admission and C2P attestation read the CR spec in the API server). `wait` +
CEL `healthCheckExprs` replace the original's jsonpath polling. Two cluster profiles prove coexistence:
`cluster1` (all versions), `cluster2` (`>=2.0.0`, `1.0.0` retired — exercising the orphan guard). A
real-cloud e2e (live RDS/S3, optional LocalStack S3 provisioning) is optional and documented, not
required for acceptance.

---

## 8. Delivery phases

**P1 — Workload plane, end-to-end (proves the thesis).**
policy repo with two `ValidatingPolicy` examples (one Audit/lane-keeping, one Deny/gate) + rationale
+ `kyverno test` fixtures → gitsign-signed tags → CI gitsign verify → Renovate flux manager → [Flux
Operator](https://fluxoperator.dev/) + `ResourceSet` multi-version coexistence on KiND (`cluster1`/`cluster2`) → orphan guard →
layered compliance dashboard (Flux revision + PolicyReports). *Acceptance: all seven "-ables"
demonstrable on the workload plane — with **measurable** at the revision + PolicyReports level
(OSCAL/C2P control-satisfaction is a cloud-plane signal deferred to P2); coexistence + retirement +
orphan-guard shown.*

**P2 — Cloud plane (collie harvest + OSCAL via C2P).**
Harvest collie's OSCAL catalogue + RDS/S3 intent; hand-author the cloud `ValidatingPolicy`s and
version them; current Crossplane v2 provider-family CRDs in KiND; same engine governs Crossplane CR
specs at admission; **C2P `result2oscal`** turns the PolicyReports into OSCAL for the dashboard.
**Retire the C2P `ValidatingPolicy`→report-mapping spike first** (all upstream C2P testdata is legacy
`ClusterPolicy`; confirm VP report naming keys cleanly, else apply the ~50-line shim — ADR-0009).
*Acceptance: a cloud policy (e.g. S3 encryption gate) versioned and coexisting; and, on KiND with no
live cloud, for one compliant + one non-compliant resource per plane, `result2oscal` emits an OSCAL
assessment-results doc that schema-validates (`oscal-cli`) and marks the mapped NIST control
satisfied/not-satisfied — regenerable in CI.*

**P3 — Governance + agent + last mile.**
Advisory metadata schema; editorial-review process docs; agent governance demonstrator (one signal
source, opens review PRs); auto-generated policy handbook + agent summaries. *Acceptance: the agent
surfaces a stale-rationale business decision as a PR; the handbook regenerates from a tag.*

---

## 9. The CIO conversation (what "done" looks like)

Four questions, four ground-truth answers: *Which policy version is each part of my estate on?*
(Flux revision) · *Is everything actually passing?* (PolicyReports) · *Do we satisfy the control
framework?* (OSCAL assessment-results via C2P) · *How fast are teams adopting the latest?* (Renovate
PR state).

---

## 10. Risks & open problems

- **gitsign not Flux-verifiable yet** → verify in CI (offline Rekor bundle, pinned); native on-cluster
  gate pending #1068 (tracked). Tamper window closed by **commit-SHA pin + forge-immutable tags** (§6.1).
- **Last-mile residual** → partly cultural; handbook is an attempt, not a claimed solution.
- **US-NIST vs UK** → NIST 800-53r5 is illustrative; UK CAF/GovAssure catalogue is north-star.
- **Half-deploys** → eventual consistency, not transactions; design to re-reconcile + health-gate.
- **Agent over-claiming** → demonstrator is bounded; never edits enforcement.
- **C2P is pre-GA (accepted)** → `compliance-to-policy-go` v2 at rc; pin + vendor the plugin. The one
  build precondition is the **VP→report mapping spike, retired before P2** (ADR-0009).
- **collie staleness** → now a *harvest* (catalogue + intent), not a toolchain fork; the feared
  Crossplane/CEL uplift cost lived in the dropped generator + auth.
- **Crossplane adoption cost** → cloud-as-CR assumes Crossplane v2; admission-only proof needs CRDs
  only (no auth/reconcile). Acknowledged in scope.

---

## 11. Project actions (not build-blocking)

1. Rework + post the gitsign revival comment on **[fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068)**
   (`docs/upstream/fluxcd-source-controller-1068-gitsign.md`).
2. **Harvest `controlplaneio/collie`** (ADR-0004; [announcement](https://control-plane.io/posts/collie-open-source-release/), from [ControlPlane](https://control-plane.io)) — reuse its OSCAL 800-53r5
   catalogue + RDS/S3 policy intent; hand-author the CEL policies natively. Offer genuinely-reusable
   improvements upstream where sensible.

---

## 12. Out of scope → north-star

OCI+cosign transport, signed attestations + enforced "why", SBOM, Flux-native keyless-git gate (post
#1068), UK CAF OSCAL catalogue, real-cloud fleet e2e, production risk-intelligence agent,
engine-agnosticism. See [north-star-modern-reference.md](north-star-modern-reference.md).

---

## References

See [docs/references.md](references.md) for the full citation registry. The most load-bearing
sources behind this PRD:

- [What is Policy As [versioned] Code? (original Medium post)](https://chrisns.medium.com/what-is-policy-as-versioned-code-306e0341290b)
- [Policy as [Versioned] Code: A Mea Culpa (blog)](https://blog.cns.me/posts/policy-versioned-code-mea-culpa-technical-argument-nesbitt-smith-pedef/) — the refined thesis this PRD honours
- [Rugged: Being Secure & Agile — Michael Brunton-Spall, GOTO 2016](https://www.youtube.com/watch?v=txEWO4uyVnY) — credited lineage
- [The Magic of Platforms — Gregor Hohpe](https://platformengineering.org/talks-library/the-magic-of-platforms) — lane-keeping vs gate
- [The GDS Way](https://gds-way.digital.cabinet-office.gov.uk/) — dated/reviewed/removed governance
- [Kyverno ValidatingPolicy (CEL)](https://kyverno.io/docs/policy-types/validating-policy/) and [Policy Reports](https://kyverno.io/docs/policy-reports/) — the engine + measurability
- [Flux Operator: ResourceSet CRD](https://fluxoperator.dev/docs/crd/resourceset/) — the coexistence matrix
- [source-controller #1068](https://github.com/fluxcd/source-controller/issues/1068) — the single upstream dependency (gitsign verifier)
- [sigstore/gitsign](https://github.com/sigstore/gitsign) and [sigstore/cosign](https://github.com/sigstore/cosign) — keyless signing
- [controlplaneio/collie](https://github.com/controlplaneio/collie) and its [announcement](https://control-plane.io/posts/collie-open-source-release/) — the cloud plane
- [OSCAL](https://pages.nist.gov/OSCAL) and [OSCAL Compass / Compliance-to-Policy (C2P)](https://github.com/oscal-compass/compliance-to-policy-go) — compliance ground-truth (PolicyReports → OSCAL assessment-results); see ADR-0009 on why not [Lula](https://github.com/defenseunicorns/lula)
