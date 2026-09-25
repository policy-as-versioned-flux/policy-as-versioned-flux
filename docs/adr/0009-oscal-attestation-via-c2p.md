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
  (a) schema-validates (C2P's built-in OSCAL validation plus an independent schema validator) and
  (b) marks each mapped NIST 800-53r5 control satisfied
  for the compliant resource and not-satisfied for the non-compliant one; the document is regenerable
  in CI.* The non-compliant exemplar is admitted under an **Audit**-mode policy — a `Deny` gate
  leaves no failing resource on-cluster to report, so gate controls' OSCAL evidence is **pass-only
  by construction** (denied resources are compliance successes that leave no failure trail); the
  not-satisfied path is therefore always demonstrated on the Audit tier.

## Position on maturity

We **accept** C2P at its current pre-GA status. The maintained line is `compliance-to-policy-go` v2
(rc); we **pin the v2 rc and vendor the kyverno-plugin binary**, and track for GA. This is consistent
with the whole thesis (pin a dependency; adopt new versions via reviewed PR). CNCF Sandbox governance
and IBM Research backing make it the right long-horizon bet; it is Kyverno-native and adds no second
validation engine.

## Build precondition — spike done, risk retired

The ValidatingPolicy→report mapping was proven live (KiND + Kyverno 1.18.2 + C2P `v2.0.0-rc.1`,
2026-07-14; runnable check in [`spikes/c2p-validatingpolicy-oscal/`](../../spikes/c2p-validatingpolicy-oscal/)). Findings:

- **The crux holds.** C2P `result2oscal` keys on `results[].policy` only (string-equal to the
  component-definition `Check_Id`). Kyverno writes the policy's own `metadata.name` there for a CEL
  `ValidatingPolicy` exactly as for a `ClusterPolicy` (`rule`/`source`/kind are never read). So a
  two-control component-definition mapped to two VPs produced correct OSCAL: the violated control
  `not-satisfied`, the all-pass control `satisfied`, oscal-version 1.1.3, C2P-self-validated.
- **One shape fix, confirmed and small.** Kyverno ≥1.18 emits **per-resource** reports with the
  subject in `.scope` and `results[].resources = null`; C2P reads subjects from `results[].resources`,
  so raw reports yield zero subjects and every in-scope control falsely defaults to `not-satisfied`.
  A **~6-line jq shim** at collection time (copy `.scope` into each `results[].resources`) fixes it —
  smaller than the ~50 lines budgeted. The C2P collection job (CronJob / Flux `Kustomization`)
  carries this normalization; it is declarative jq, not bespoke tooling.
- **Suffix normalization rides in the same shim.** The spike ran unsuffixed policy names; the build
  deploys coexisting versions as `<policy>-<version>` (`nameSuffix`), which would break the
  string-equality against the component-definition `Check_Id`s. The collection shim strips the
  version suffix from `results[].policy` (the version dimension is already carried by the report's
  `policy-version` context), so one component-definition maps all coexisting versions.

## Note, 2026-09-25 (eco-system ticket 35): collection is a lane step, and the criterion narrows

The Consequences above wire collection as a `CronJob` or Flux `Kustomization`. Ticket 35 changes
that shape, delegated under [ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md).
The adopter's cluster is the drift lane's ephemeral KinD, which lives for one run. So collection is a
step in that lane. After the facts, the step runs `result2oscal.py` from the platform tag the lane
pins, over the PolicyReports on the cluster. Its assessment-results is an **Observation**, not a
signed feed, because nothing prices from it. The `c2p-collector` image is dropped: platform owns the
glue, as this ADR says.

The acceptance criterion above asks for both planes. Until eco-system ticket 151 lands the cloud
plane, the live half covers one plane, and only the pods the lane runs. The component-definition
maps two Check_Ids today. The step prints that count, and records a could-not-look when no
PolicyReport exists before the cluster is deleted. Built by eco-system ticket 155.
