---
status: accepted
---

# Cloud/IaC plane: fork and uplift ControlPlane's `collie` (cloud-as-CR), not Checkov

The cloud/IaC plane is built by **forking and uplifting** `controlplaneio/collie` (Apache-2.0,
dormant since Aug 2023) rather than reproducing the original's Checkov-in-CI scan. collie already
provides cloud-as-CR via **Crossplane** governed by **Kyverno**, **NIST 800-53r5** Kyverno policies
for AWS RDS/S3, an **OSCAL** control catalogue, and **Lula** compliance validation. This turns the
original's weakest, shift-left-only leg (the cloud side, which CNS admitted on stage had no runtime
loop and shipped broken) into a runtime-governed plane driven by the *same versioned Kyverno engine*
as the workload plane — a single policy mechanism across both planes.

## Why

- **On-thesis:** one versioned-dependency mechanism, one engine, governing both Kubernetes
  workloads and cloud resources at runtime. Closes the gap the talk admitted.
- **Leg-up:** the hard parts (Crossplane bootstrap, NIST policies, OSCAL catalogue, Lula wiring)
  already exist; we add the parts the thesis is about (versioning + Flux delivery).
- **ControlPlane alignment:** this work is for ControlPlane; uplifting their own dormant OSS is
  welcome, and the uplift PRs can flow back upstream.

## What we add over collie (the novel contribution)

- collie's policies are a *static* demo. We make them **versioned dependencies**: gitsign-signed
  semver tags, Flux `GitRepository` delivery, Renovate bumps, multi-version coexistence, and the
  Audit/Deny lane-keeping/gate split (ADR-0002, ADR-0003).
- **OSCAL + Lula become the "measurable" pillar** — control-framework attestation of compliance,
  a far stronger answer to "are we compliant?" than the original's "count the open PRs."

## Uplift scope (the fork earns its keep here)

- Migrate collie's Kyverno `ClusterPolicy` → `ValidatingPolicy` (consistent with ADR-0003).
- Bump Crossplane (and its providers) to current; make delivery Flux-native.
- Clear the two stalled issues (lula build cache; cluster bootstrap make target).

## Consequences

- Adds **Crossplane**, **Lula**, and an **OSCAL** toolchain as dependencies of the cloud plane.
- The cloud plane is an **integral second plane of the floor** (not deferred) — it satisfies the
  thesis's tool-agnostic / multi-plane pillar at runtime.
- **UK-context caveat:** collie's OSCAL/NIST 800-53r5 framing is US-federal. For CNS's UK
  public-sector audience it is illustrative; a UK catalogue (NCSC CAF / GovAssure) can be added
  later. OSCAL is framework-agnostic, so the mechanism ports.
- Feeds the measurability decision (was D4.1): OSCAL/Lula composes with Kyverno PolicyReports +
  the Flux source revision — to be settled when we reach that question.
- The fork is a **build dependency**; uplift changes should be offered back upstream where sensible.
