---
status: accepted
---

# "Measurable" = layered ground-truth; PR-acceptance demoted to adoption velocity

The measurable pillar is delivered as four complementary signals, each answering a distinct
question, surfaced in one dashboard:

| CIO question | Signal |
|---|---|
| Which policy version is each part of the estate on? | Flux source **revision** (`gotk_resource_info{revision}`) |
| Is each workload actually passing? | Kyverno **PolicyReports** |
| Does the estate satisfy control framework X? | **OSCAL assessment-results** emitted by **C2P `result2oscal`** from the Kyverno PolicyReports both planes already produce (ADR-0009) |
| How many teams accepted the latest bump? | **Renovate PR** state (adoption velocity) |

Each signal is one panel; the dashboard is **four panels over four datasources** joined by a shared
`cluster` + `policy-version` Grafana template variable — **not** a single Prometheus/PromQL join.
PolicyReports reach Prometheus via **Policy Reporter** (Kyverno sub-project); the OSCAL doc and
Renovate/GitHub PR state are read by first-party Grafana datasource plugins (`infinity`,
`github`) — no bespoke exporters.

The headline shifts from the 2022 pitch ("compliance is a GitHub PR search away") to **demonstrable
control satisfaction** with evidence. The PR-acceptance signal is retained but **explicitly
relabelled** as adoption velocity — it measures whether teams took the update, not whether their
workloads pass. This is a deliberate departure from the talk's framing, made because we now have
ground truth and OSCAL gives formal control attestation.

## Consequences

- Builds a compliance dashboard over Flux revision + PolicyReports + OSCAL (C2P) + Renovate PR state
  (four panels, shared template variable).
- **Phased acceptance.** On the **workload plane (P1)** "measurable" = Flux revision + PolicyReports
  (two of the four CIO signals). **OSCAL control-satisfaction (via C2P) lands with the cloud plane
  (P2)** — CIO question 3 is a cloud/framework question and there is no cloud plane at P1.
- OSCAL (US NIST 800-53r5 from collie's catalogue) is illustrative for UK; a UK CAF/GovAssure
  catalogue is a later addition (ADR-0004).
- The C2P dependency, its pre-GA status, and the ValidatingPolicy→report-mapping spike are recorded
  in ADR-0009.
