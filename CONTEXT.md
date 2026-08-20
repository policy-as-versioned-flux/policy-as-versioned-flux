# Context: Policy as Versioned Code, on Flux

The ubiquitous language for this project. A glossary, not a spec — no implementation
details. When a term here conflicts with how someone is speaking, the term here wins
(or we change it here, deliberately).

This project is a faithful re-implementation of Chris Nesbitt-Smith's (CNS) **Policy as
[Versioned] Code** thesis onto **Flux CD**. Source material: the talk, the original Medium
post, the later "mea culpa" blog post, and two reference GitHub orgs (`example-policy-org`,
`policy-as-versioned-code`). Full research is in `./research/`.

---

## Core thesis terms

- **Party** — Any of the six units of the estate. Deliberately *not* given a collective noun in
  prose: name the kind instead ("the platform, two regulators and three institutions"), because the
  argument depends on these being different kinds of party exchanging signed dependencies across
  trust boundaries. What is true of all six: each is represented by its own **independent GitHub
  organisation**.

- **Role** — What a party *does*. Roles **compose**; they are not a partition, and a party may hold
  several:
  - **publisher** — ships a signed, versioned artefact others pin (`platform`, `nist`, `ico`);
  - **risk-bearer** — has a declared risk-appetite band, so the £ engine can price it
    (`driftwood`, `tuppence`, `ludlow`, **and `platform`** — the apparatus prices its own risk
    against a strict £10k band, see *reflexive*);
  - **adopter** — pins and consumes another party's artefact (the three institutions; `platform`
    itself as it pins `nist`).

- **Institution** — A regulated, risk-bearing adopter: `driftwood` (UK retail), `tuppence` (UK bank),
  `ludlow` (US health). Kept over "consumer" because it carries the regulatory weight the
  proportionality argument depends on, even though "consumer" better describes the dependency
  direction.

- **Regulator** — A publisher that ships controls or penalties as a signed, versioned artefact and
  bears no risk of its own here (`nist`, `ico`).

- **`org`** — **A deliberately overloaded term, documented rather than renamed.** In code and in
  emitted artefact fields it means *risk-bearer* — `tolerance_for(org)` resolves an appetite band and
  exits for a party that has none. In infrastructure it means *GitHub organisation*, which all six
  parties have. The overload is tolerated because `org` is a field name in emitted artefacts and
  golden digests, and renaming it would churn the provenance surface for a vocabulary win. Read it as
  "risk-bearer" in code, "GitHub organisation" in deployment.


- **Policy** — A set of rules that mitigates a risk. Comes in two intents: *security-enforcing*
  (e.g. data-at-rest encryption) and *consistency-enforcing* (e.g. required labels). A policy is
  only worth having if it carries its **purpose** ("purposeless policy is potentially practically
  pointless policy").

- **Exemption** — **A banned concept. There are none, ever.** An exemption is a carve-out for a named
  workload, and this project does not have them at any scope, in any file, under any name — the
  everything-is-codified rule admits no exceptions to itself. The legitimate alternatives, in order
  of preference: express the allowance as **conditional policy** ("you may do X *if* you meet
  conditions C", so anyone meeting C is treated identically and nobody asks a favour); or let the
  **cage implement the control on the workload's behalf** and price the residual. A workload that can
  satisfy neither does not run — refusal is the bottom rung of the cage ladder, reached by the £,
  never by a carve-out. (The estate shipped an exemptions ledger that contradicted this; it is
  removed — see `.scratch/govern-what-you-dont-control/issues/05-remove-the-exemption-ledger.md`.)

- **Policy as a dependency** — The central move: treat a body of policy like a software
  dependency — semantically versioned, stored in version control, distributed to consumers,
  unit-tested, and updated via reviewed pull requests. NOT (primarily) a deploy-time gate.

- **The seven "-ables"** — The talk's checklist for "what good looks like". Each is an acceptance
  property the system must be able to claim: **visible, communicable, consumable, testable,
  usable, updatable, measurable.**

- **Lane-keeping vs. gate** (the mea-culpa's load-bearing distinction) —
  - **Lane-keeping assist** — Continuous, corrective, non-blocking guidance for the *majority*
    of the policy surface enterprises actually struggle with: labelling, tagging, configuration
    standards, operational metadata. Delivered as a *versioned dependency* (the ~80% case).
  - **Gate** ("a locked door") — A hard admission block reserved for the *catastrophic minority*:
    access control, data classification/protection, cryptographic key management — policies
    governing *whether a workload may exist at all*.
  - The system must support BOTH. A gate-only system is the exact mistake the mea-culpa walked back.
  - **Engine mapping:** Kyverno `ValidatingPolicy` `validationActions: Audit` = lane-keeping;
    `Deny` = gate. (See ADR-0003.) This *enforcement-action* axis is independent of *adoption
    cadence* (ADR-0002).

- **The "why" / rationale** — Risk/threat-model metadata that travels *with* each policy version,
  so disagreement is resolved by a **pull request to the policy** (informed debate), not by an
  out-of-band **exemption request**. Grounded in threat modelling, not "emotional and anecdotal"
  reasoning.

- **Human-governance layer** (mea-culpa addition) — Versioning distributes policy to *engineers*
  but does not *govern* it. Borrowed from GDS Way: every accepted policy is **dated**, **regularly
  reviewed**, and **deleted if no longer defensible** ("Not archived. Not deprecated. Removed.").
  Realised as **editorial review** (a reviewed PR changes/removes a policy — never time-triggered;
  see [ADR-0006](docs/adr/0006-deterministic-policy-no-time-conditions.md)), supported by the agent
  governance layer. See [ADR-0007](docs/adr/0007-agent-assisted-editorial-governance.md).

- **Agent governance layer** — An AI/agent layer that reads each policy's embedded
  rationale/risk/ethos plus external signals (CVEs, cloud/regulatory change, Wardley climatic
  movement) and surfaces noise-reduced **business decisions** as review PRs/issues. It **prompts**
  editorial review; it **never edits enforcement**. Specified as architecture + a thin demonstrator.

- **Advisory metadata** — `created` / `lastReviewed` / rationale / risk / ethos carried on each
  policy version (annotations + `rationale.md`, OSCAL-mappable). Read by humans and the agent layer
  only; **never consumed by the engine** (keeps policy deterministic).

- **The last-mile problem** (mea-culpa addition) — Versioning reaches technical consumers but not
  non-technical ones (the talk's "Cleaner"). An explicitly **acknowledged open problem**, not
  something the system claims to solve.

- **Policy version** — A semantic version of the whole policy body. Semver carries meaning, defined
  by **verdict impact on currently-compliant workloads**: **major** = any change that can turn a
  pass into a fail at the gate (a new or tightened `Deny` policy, an `Audit`→`Deny` promotion,
  free-text label → enum); **minor** = an addition that cannot fail an existing compliant workload
  (e.g. a new `Audit` policy); **patch** = fix/widening (the passing set only grows). ("Don't be
  fooled by the decimal points — 1.20.0 > 1.3.0.")

- **Multi-version coexistence** — A single runtime (cluster) must accept and evaluate **multiple
  policy versions simultaneously** (≥3), so old versions can be retired over a transition window
  rather than via a flag-day breaking change. *The crux of the original implementation.*

- **Version pin** — The single declaration by which a consumer (workload / cluster) states which
  policy version applies to it. The original's signature elegance: **one string** served as both
  the dependency pin *and* the engine's workload selector.

- **Compliance / measurable** — The ability to answer "which part of the estate is on which policy
  version, and is it actually passing?" In the original this was a proxy ("a GitHub PR search
  away" — i.e. *bump acceptance*). See open question on proxy-vs-ground-truth.

- **Consumer** — A repo/workload that depends on a policy version (the original's `app1..3`,
  `infra1..3`). Opts in to a version and is judged against it.

- **Orphan guard** — A deterministic catch-all `ValidatingPolicy` that **denies at admission** any
  workload whose `policy-version` label is **missing or not in** the cluster's currently-installed
  version set (derived from the `ResourceSet` version array), with background-scan Audit reports
  covering pre-existing orphans (a brownfield estate may start it in Audit and promote by editorial
  PR). Because every versioned policy — gates included — matches only workloads that opt in via the
  label, the guard is what makes the gate tier a locked door rather than an opt-in door. Closes the
  original's silent-ungovernance gap where a
  workload pinned to a retired version was matched by no policy.

---

## Project posture (resolved)

- **Fidelity = "faithful to intent."** Reproduce the thesis and its ethos 1:1, but let Flux do
  natively what the 2022 implementation had to hack (the scaffolding that only existed because
  GitOps tooling couldn't yet express "versioned policy as a live dependency" is dropped, not
  preserved). The PRD targets this **faithful-to-intent floor**; a separate **modern-reference
  report** documents the fuller "north star" design.

- **Transport = signed git tags, keyless (gitsign).** Policy is distributed as semver **git tags**
  (faithful to 2022), signed **keyless** with `sigstore/gitsign` (no long-lived GPG keys). Consumed
  via a Flux `GitRepository` pinned on `spec.ref.tag` **and `spec.ref.commit`** (the tag's resolved
  SHA — force-move-proof; Renovate writes both). See [ADR-0001](docs/adr/0001-transport-signed-git-tags-gitsign.md).
  - **Known limitation (accepted):** Flux `GitRepository.spec.verify` is PGP-only and cannot verify
    gitsign signatures today, so there is **no Flux-native verified-source admission gate** on the
    floor. Verification happens **in CI / at-merge** (`gitsign verify` against Rekor). The native
    gate is pending upstream **[fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068)**
    (a tracked project action — see `docs/upstream/`).
  - **Deferred to north-star (need OCI):** signed *attestations* carrying the "why", and SBOM. On
    the floor the rationale rides as versioned files in the policy repo (Kyverno annotations +
    `rationale.md`).

- **Adoption cadence = pinned everywhere + Renovate PR.** Consumers and clusters pin exact tags;
  new versions land only via a reviewed Renovate PR (`automerge:false`), in every environment.
  Live semver ranges are rejected. See [ADR-0002](docs/adr/0002-adoption-pinned-plus-renovate-pr.md).
  **Adoption cadence (pin vs range) and enforcement action (Audit vs Deny) are independent axes** —
  do not conflate them.

- **Engine = Kyverno; policies authored as CEL `ValidatingPolicy`.** See
  [ADR-0003](docs/adr/0003-kyverno-validatingpolicy-cel.md).

- **Two planes:** **workload plane** (native Kubernetes workloads) and **cloud plane** (cloud
  resources). Both governed by the *same* versioned Kyverno engine. The cloud plane is built by
  **harvesting** ControlPlane's **collie** (cloud-as-CR) — its OSCAL catalogue + policy intent as
  data; its generator/Lula toolchain dropped. See
  [ADR-0004](docs/adr/0004-cloud-plane-fork-collie.md).

- **Deterministic policy.** Policy bodies contain no time-conditional logic (no expiry/start
  dates); the same manifest + same policy version always evaluates the same. See
  [ADR-0006](docs/adr/0006-deterministic-policy-no-time-conditions.md).

- **Sunset = scheduled proposal, never scheduled application.** A fleet's array entry may carry a
  `sunset:` date; on that date a machine opens a retirement PR that a human must merge — nothing
  timed ever changes an admission verdict on its own. See
  [ADR-0010](docs/adr/0010-sunset-scheduled-proposals-not-application.md).

- **Install/fleet layer = ControlPlane Flux Operator** (`FluxInstance` + `ResourceSet` matrix);
  thesis stays vanilla-Flux-expressible. See
  [ADR-0005](docs/adr/0005-controlplane-flux-operator-resourceset.md).

- **No bespoke tooling.** Developer/CI shift-left uses native CLIs directly (`flux build`/`flux
  diff` | `kyverno apply`/`kyverno test`, `gitsign verify`) — no wrapper, no re-implemented
  `policy-checker`. The 2022 bash/Docker checker is deleted, not ported.

- **Proof = KiND, free & reproducible.** Workload plane runs fully on KiND; the cloud plane is
  proven at the admission level — current Crossplane v2 provider-family CRDs installed in KiND, CR
  specs judged by Kyverno at admission (no ProviderConfig, auth, or reconcile); no LocalStack/AWS on
  the critical path. `wait` + CEL health checks replace jsonpath polling. A
  real-cloud e2e (live RDS/S3, optional LocalStack provisioning, C2P over realized state) is
  optional and documented.

---

## Flux terms (plain-English, for the glossary)

- **[Flux](https://fluxcd.io/) / GitOps Toolkit** — A set of Kubernetes controllers that continuously make the cluster
  match desired state declared in Git/registries. Replaces "run a script to apply things".
- **Source object** (`GitRepository` / `OCIRepository`) — A declarative object saying "the policy
  lives *here*, at *this version*." The **pin** lives on its `spec.ref`.
- **`Kustomization`** (Flux) — A declarative object saying "apply the manifests from that source,
  in this order, and keep them applied."
- **OCI artifact** — The policy bundle packaged and pushed into a container registry (like an
  image, but it's policy files), addressable by an immutable digest and signable with cosign.
  *Not used on the faithful floor* (see ADR-0001); relevant to the north-star report.
- **[gitsign](https://github.com/sigstore/gitsign)** — Sigstore's keyless signer for git **commits/tags**: signs with a short-lived
  Fulcio cert via OIDC (no long-lived key), logged in the Rekor transparency log. Verified with
  `gitsign verify` (not plain `git verify-commit`). Flux cannot verify it yet (issue #1068).
- **[cosign](https://github.com/sigstore/cosign)** — Sigstore's keyless signer/verifier for **OCI** artifacts. Flux *can* verify it
  (`OCIRepository.spec.verify`). The OCI-world counterpart to gitsign.
- **Pin vs. range** — A *pin* is an exact version (`ref.tag: 2.1.1`); a *range* (`ref.semver:
  ">=2.0.0"`) lets Flux auto-adopt new matching versions with no human in the loop.
- **Flux Operator** (ControlPlane) — Installs/manages Flux declaratively via a `FluxInstance` CR,
  with distroless/FIPS-hardened images. Used as the install + fleet layer (ADR-0005). The thesis
  stays vanilla-Flux-expressible regardless.
- **`ResourceSet`** (Flux Operator) — Templates many objects from a table of inputs. Used to
  generate the coexistence matrix (clusters × policy versions) as data.

## Cloud-plane terms

- **[Crossplane](https://crossplane.io)** — Lets you declare cloud resources (an RDS instance, an S3 bucket) as Kubernetes
  custom resources, so cloud is provisioned and reconciled by Kubernetes controllers.
- **cloud-as-CR** — The pattern of representing cloud intent as Kubernetes CRs (via Crossplane) so
  the *same* Kyverno engine governs cloud at admission/runtime, exactly as it governs workloads.
- **[collie](https://github.com/controlplaneio/collie)** — ControlPlane's (Apache-2.0, dormant since 2023) toolkit demonstrating Kyverno
  governance + compliance for Crossplane-provisioned cloud infra. We **harvest** its reusable IP (the
  NIST 800-53r5 → RDS/S3 policy intent + OSCAL catalogue) and rebuild the cloud plane natively; its
  generator/Lula/bootstrap are dropped (ADR-0004).
- **[OSCAL](https://pages.nist.gov/OSCAL)** — NIST's Open Security Controls Assessment Language: a machine-readable standard for
  expressing security control catalogues, baselines, and assessment results. The formal carrier of
  the "measurable" pillar on the cloud plane.
- **[C2P — Compliance-to-Policy](https://github.com/oscal-compass/compliance-to-policy-go)** — OSCAL Compass (CNCF Sandbox) tool. Its `result2oscal`
  direction consumes the Kyverno PolicyReports the single engine already emits and produces OSCAL
  **assessment-results** (controls satisfied/not). The carrier of the "measurable" pillar's control
  attestation. See [ADR-0009](docs/adr/0009-oscal-attestation-via-c2p.md).
- **[Policy Reporter](https://github.com/kyverno/policy-reporter)** — Kyverno sub-project: PolicyReport CRs → Prometheus/UI/dashboards. The
  live measurability layer beneath C2P.
- **NIST 800-53r5** — The US-federal control catalogue collie ships policies against (illustrative
  for UK; a UK CAF/GovAssure catalogue can be added — OSCAL is framework-agnostic).

---

## Decision log

See `docs/adr/` for the hard-to-reverse decisions and their rationale.
