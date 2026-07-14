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
- **Version pin:** author every policy as `apiVersion: policies.kyverno.io/v1` (the GA CEL API —
  introduced in Kyverno **1.17**, Feb 2026; marked **Stable in 1.18** — not the `v1alpha1`/`v1beta1`
  forms in older tutorials). The reference pins Kyverno **≥1.18** as a hard dependency: 1.17.0
  shipped with `ValidatingPolicy` background-scan PolicyReports broken
  ([kyverno#15233](https://github.com/kyverno/kyverno/issues/15233), fixed 1.17.2), and that feature
  is exactly what the measurable pillar (ADR-0008) rides on. Because the build is
  all-`ValidatingPolicy`,
  the `ClusterPolicy` removal (~1.20) is a non-event here rather than a migration risk. The engine
  itself is a governed dependency — pinned, bumped via the same reviewed Renovate PR path as policy —
  since an engine upgrade can change verdicts across every installed policy version; the pending
  `wgpolicyk8s.io`→`openreports.io` report-API migration (opt-in today) is tracked for the same
  reason.
- `Audit` and `Deny` are set **per policy** (lane vs gate); they are not a graduated `[Audit, Deny]`
  list on one policy. An `Audit→Deny` promotion is an **editorial PR** flipping `validationActions`,
  never an automated/time-based transition (ADR-0006).
- Pure Kubernetes-native `ValidatingAdmissionPolicy` (no Kyverno) was rejected for the floor — it
  drops PolicyReports/mutation/generation and abandons the reference engine — and is noted only as
  a north-star consideration.
