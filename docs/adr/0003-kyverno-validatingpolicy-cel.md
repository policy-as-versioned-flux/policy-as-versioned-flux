---
status: accepted
---

# Engine API: Kyverno CEL `ValidatingPolicy`, not the 2022 `ClusterPolicy`

The reference policies are authored as Kyverno **`ValidatingPolicy`** (CEL expressions,
`validationActions: [Audit|Deny|Warn]`), not the original's **`ClusterPolicy`** /
`validationFailureAction`. The 2022 type is deprecated with removal targeted ~Kyverno 1.20
(~Oct 2026); building a new 2026 reference on a dying API contradicts "faithful to intent". Kyverno
remains the engine (it is the reference engine in both eras); only the policy-body syntax changes.

## Consequences

- A reader comparing this to the 2022 talk/repos will find the policy bodies rewritten in CEL —
  this is deliberate, not drift.
- **`validationActions` is the enforcement-action axis:** `Audit` = lane-keeping (nudge, reported
  via PolicyReports), `Deny` = gate ("locked door"). This is the runtime expression of the
  mea-culpa's split, and is independent of adoption cadence (ADR-0002).
- Multi-version coexistence is preserved: distinct `ValidatingPolicy` names per version, each
  self-scoped via a CEL `matchConstraints` objectSelector on the `mycompany.com/policy-version`
  label (the direct analogue of the original's `match.selector`).
- Background scans + PolicyReports come from the engine, feeding the "measurable" pillar.
- Pure Kubernetes-native `ValidatingAdmissionPolicy` (no Kyverno) was rejected for the floor — it
  drops PolicyReports/mutation/generation and abandons the reference engine — and is noted only as
  a north-star consideration.
