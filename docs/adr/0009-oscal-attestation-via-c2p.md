---
status: accepted
---

# OSCAL attestation via Compliance-to-Policy (C2P), not Lula

The "measurable / controls-satisfied" pillar's machine-readable **OSCAL assessment-results** are
produced by **OSCAL Compass — Compliance-to-Policy (C2P)** (`oscal-compass/compliance-to-policy-go`,
Apache-2.0, CNCF Sandbox), using **only** its `result2oscal` direction: the single versioned Kyverno
engine already emits `wgpolicyk8s.io` PolicyReports for both planes, and C2P normalises them into an
OSCAL assessment-results document mapping each NIST 800-53r5 control to satisfied / not-satisfied.
**Lula is dropped entirely.**

## Why not Lula (the original plan)

The PRD/ADR-0004/ADR-0008 originally cited `defenseunicorns/lula` for this pillar. Verified 2026-07:

- **`defenseunicorns/lula` is now Lula 2** — a SvelteKit/Express compliance-*documentation* web app
  (YAML-in-Git + spreadsheet import) that **deliberately dropped OSCAL** and has no cluster/domain/
  provider layer, no admission hook, and no PolicyReport consumer. It cannot validate live
  Kubernetes/Crossplane state or emit machine-readable results. "Replan around Lula 2" is impossible:
  it is a different product solving a different problem.
- The capability the pillar needs survives only in **`defenseunicorns-labs/lula1`** (v0.16.0),
  explicitly **maintenance-mode**. So "maintained" and "Lula" are mutually exclusive here.
- Lula ran its **own** validation engine, duplicating policy evaluation against the "one engine, both
  planes" thesis. A Lula path — either generation — was therefore both unmaintained *and*
  architecturally redundant.

## Why C2P

- **On-thesis:** C2P adds no second evaluator. It translates the PolicyReports the one Kyverno engine
  already produces into OSCAL — the cleanest possible expression of "one engine, one result stream,
  formal attestation on top."
- **Maintained:** `compliance-to-policy-go` v2 is the live line (v2.0.0-rc.1, Nov 2025; commits into
  2026), under CNCF Sandbox (`oscal-compass`, since Jun 2024), with `compliance-trestle` (the OSCAL
  SDK) very active. Apache-2.0.
- **Fits both planes:** workloads and Crossplane CRs both emit the same PolicyReport CRs; C2P keys on
  report result entries, not resource kind.

## Consequences

- Adds **C2P (`result2oscal`)** as a cloud-plane dependency; **removes Lula**. collie's OSCAL
  catalogue is reshaped into a C2P **component-definition** mapping controls ↔ our hand-authored
  policy names (ADR-0004). Policy Reporter provides the live PolicyReport→Prometheus layer.
- We use **only** `result2oscal`; C2P's `oscal2policy` (deploy policies) is redundant here because
  Flux already delivers the signed `ValidatingPolicy`s.
- **No Flux-native C2P controller:** collection is wired as a `CronJob` / Flux `Kustomization` that
  runs `result2oscal` and publishes `assessment-results.yaml` (small glue we own).
- **New pillar acceptance criterion** (replaces the vaguer "OSCAL control satisfaction shown for both
  planes on KiND+LocalStack"): *On KiND with no live cloud, for one compliant and one deliberately
  non-compliant resource on each plane (a workload and a Crossplane RDS or S3 CR), `result2oscal`
  consumes the (Cluster)PolicyReport CRs and produces an OSCAL assessment-results document that
  (a) schema-validates under `oscal-cli` and (b) marks each mapped NIST 800-53r5 control satisfied
  for the compliant resource and not-satisfied for the non-compliant one; the document is regenerable
  in CI.*

## Position on maturity

We **accept** C2P at its current pre-GA status. The maintained line is `compliance-to-policy-go` v2
(rc); we **pin the v2 rc and vendor the kyverno-plugin binary**, and track for GA. This is consistent
with the whole thesis (pin a dependency; adopt new versions via reviewed PR). CNCF Sandbox governance
and IBM Research backing make it the right long-horizon bet; it is Kyverno-native and adds no second
validation engine.

## Build precondition (one spike, before P2)

**ValidatingPolicy→report mapping must be confirmed once.** Every C2P example/testdata uses legacy
`ClusterPolicy`; no CEL `ValidatingPolicy` example exists as of 2026-07. In principle it works — VP
emits the same `wgpolicyk8s.io` PolicyReport/ClusterPolicyReport CRs and C2P keys on result entries,
not policy kind — but the mapping keys must line up with VP report naming. A **one-day spike retires
this** before P2 build; if the keys don't align, a ~50-line `result2oscal` mapping shim closes it.
