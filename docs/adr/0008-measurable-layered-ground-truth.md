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
| Does the estate satisfy control framework X? | **OSCAL / Lula** attestation (via the collie cloud plane) |
| How many teams accepted the latest bump? | **Renovate PR** state (adoption velocity) |

The headline shifts from the 2022 pitch ("compliance is a GitHub PR search away") to **demonstrable
control satisfaction** with evidence. The PR-acceptance signal is retained but **explicitly
relabelled** as adoption velocity — it measures whether teams took the update, not whether their
workloads pass. This is a deliberate departure from the talk's framing, made because we now have
ground truth and OSCAL gives formal control attestation.

## Consequences

- Builds a compliance dashboard joining Flux revision + PolicyReports + OSCAL/Lula results.
- OSCAL/Lula (US NIST 800-53r5 from collie) is illustrative for UK; a UK CAF/GovAssure catalogue is
  a later addition (ADR-0004).
