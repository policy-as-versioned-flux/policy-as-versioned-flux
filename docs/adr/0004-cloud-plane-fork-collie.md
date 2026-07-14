---
status: accepted
---

# Cloud/IaC plane: harvest ControlPlane's `collie` (cloud-as-CR), not Checkov

The cloud/IaC plane is built by **harvesting** `controlplaneio/collie` (Apache-2.0, dormant since Aug
2023) rather than reproducing the original's Checkov-in-CI scan. collie demonstrated cloud-as-CR via
**Crossplane** governed by **Kyverno**, with **NIST 800-53r5** policies for AWS RDS/S3 and an **OSCAL**
control catalogue. We take collie's reusable *IP* — the NIST→RDS/S3 policy intent and the OSCAL
catalogue — and rebuild the plane natively, so the *same versioned Kyverno engine* that governs the
workload plane also governs Crossplane CRs at admission. This turns the original's weakest,
shift-left-only leg (the cloud side, which CNS admitted on stage had no runtime loop and shipped
broken) into a runtime-governed plane under one policy mechanism.

Why harvest rather than fork the toolchain: collie's Kyverno policies are **generated build
artifacts** (its OSCAL→policy generator emits legacy `ClusterPolicy`), and the OSCAL validator it
paired with is unusable — `defenseunicorns/lula` is now Lula 2, a compliance-documentation web app
that dropped OSCAL (see ADR-0009). So we **hand-author** the RDS/S3 policies as CEL `ValidatingPolicy`,
keep collie's OSCAL catalogue as data, and drop collie's generator, Lula wiring, and bootstrap harness.
This also keeps the Crossplane cost small — the feared "uplift" lived in the generator and provider-auth
we are deleting, not in a handful of hand-authored policies.

## Why

- **On-thesis:** one versioned-dependency mechanism, one engine, governing both Kubernetes
  workloads and cloud resources at runtime. Closes the gap the talk admitted.
- **Leg-up (as data, not code):** collie's NIST 800-53r5 → RDS/S3 policy intent and its OSCAL
  catalogue already exist; we reuse them and add the parts the thesis is about (versioning + Flux
  delivery + one engine). We do **not** inherit collie's generator, Lula wiring, or bootstrap.
- **ControlPlane alignment:** this work is for ControlPlane; reviving their dormant OSS is welcome,
  and any genuinely reusable improvements can be offered upstream.

## What we build over collie (the novel contribution)

- collie's policies were a *generated, static* demo. We **hand-author** the RDS/S3 rules as CEL
  `ValidatingPolicy` and make them **versioned dependencies**: gitsign-signed semver tags (+ commit
  pin, ADR-0001), Flux delivery, Renovate bumps, multi-version coexistence, and the Audit/Deny
  lane-keeping/gate split (ADR-0002, ADR-0003).
- **OSCAL attestation becomes the "measurable" pillar via C2P** (ADR-0009): the single Kyverno engine
  emits PolicyReports for both planes; **Compliance-to-Policy (`result2oscal`)** normalises them into
  OSCAL assessment-results — a far stronger, machine-checkable answer to "are we compliant?" than the
  original's "count the open PRs", with **no second validation engine** duplicating policy logic
  (which is exactly what a Lula fork would have reintroduced).

## Harvest scope (what we take, build, and drop)

- **Take (as data):** collie's OSCAL 800-53r5 catalogue and the control→RDS/S3 intent; reshaped into
  a C2P **component-definition** mapping NIST controls ↔ our hand-authored policy names.
- **Build:** the RDS/S3 CEL `ValidatingPolicy` bodies; target **current Crossplane v2 + AWS
  provider-family** CRD groups (v2 managed resources are namespaced by default; the policies and
  the orphan guard match the namespaced kinds). Proof is **KiND-only, spec-based** — install the provider CRDs (no
  ProviderConfig, no auth, no reconcile); Kyverno judges the CR spec at admission and C2P attests from
  the PolicyReport. No LocalStack/AWS on the critical path (real-cloud/LocalStack e2e stays optional,
  §7). The cloud-policy `Kustomization` `dependsOn` the provider CRDs being Established so the
  admission webhook is registered; any `Deny` gate scopes to CREATE/UPDATE and excludes
  provider-authored status-only updates via `matchConditions`.
- **Drop:** collie's OSCAL→policy generator, its Lula 1 validation YAML, and its EKS/Terraform/IRSA
  bootstrap harness. The two 2023 "stalled issues" (lula build cache; cluster bootstrap target) are
  moot — those components are gone.

## Consequences

- Adds **Crossplane v2** (+ AWS provider-family CRDs) and the **C2P** OSCAL emitter (ADR-0009) as
  cloud-plane dependencies. **Lula is not a dependency.**
- The cloud plane is an **integral second plane of the floor** (not deferred) — it satisfies the
  thesis's tool-agnostic / multi-plane pillar at runtime, proven at the admission level on KiND.
- **UK-context caveat:** collie's OSCAL/NIST 800-53r5 framing is US-federal. For CNS's UK
  public-sector audience it is illustrative; a UK catalogue (NCSC CAF / GovAssure) can be added
  later. OSCAL is framework-agnostic, so the mechanism ports.
- Measurability (was D4.1) is settled in ADR-0008/ADR-0009: OSCAL (via C2P) composes with Kyverno
  PolicyReports + the Flux source revision + Renovate PR state on one dashboard.
