---
status: accepted
---

# Engine API: Kyverno CEL `ValidatingPolicy`, not the 2022 `ClusterPolicy`

> **Amended 2026-09-25 and 2026-09-26 (eco-system ticket 71, delegated under [ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md)).**
> Four statements in the "Version pin" point below are false about the estate as built, or claim
> more than was measured. The choice of Kyverno and of CEL policies stands.
>
> 1. *"author every policy as `apiVersion: policies.kyverno.io/v1`"*. Every served body is
>    `policies.kyverno.io/v1alpha1`. Kyverno 1.18.2 and 1.19.1 both serve `v1` and mark `v1alpha1`
>    deprecated, for each policy kind that has a `v1alpha1`. The next policy line moves the bodies to `v1`. For the
>    cage fixtures, the move changed no result on either engine.
> 2. *"the build is all-`ValidatingPolicy`"*. The served lines also carry two `MutatingPolicy`
>    bodies (stamp-posture and cage-tier) and a `GeneratingPolicy` (cage-netpol), as
>    [ADR-0016](0016-a-subclass-never-restates-a-mutate.md) records. The
>    `ClusterPolicy` removal is still a non-event, because no body is a `ClusterPolicy`.
> 3. *"bumped via the same reviewed Renovate PR path as policy"*. No Renovate configuration names
>    Kyverno. The engine version window and the bump route are now
>    [ADR-0033](0033-a-policy-line-supports-exactly-the-engines-it-passed-on-and-any-other-engine-is-priced.md):
>    a line supports exactly the engines it passed on, and the route is a reviewed PR that the gate
>    grades.
> 4. *"The reference pins Kyverno **≥1.18** as a hard dependency"*. That is a range, and no run
>    measured it. ADR-0033 replaces it: a line supports exactly the engine versions on which every
>    body it serves compiles and its fixtures pass.

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
  self-scoped via a `matchConditions` CEL expression on the `mycompany.com/policy-version` label
  (the direct analogue of the original's `match.selector`) -- **not** `matchConstraints`
  `objectSelector`, corrected after issue 08's live testing found Kyverno's admission-controller
  flattens every installed ValidatingPolicy's `objectSelector` into one shared Kubernetes
  `ValidatingWebhookConfiguration` (last-reconciled wins, not unioned), so with >1 version
  installed only the most-recently-reconciled version's workloads were ever evaluated at all.
  `matchConditions` is evaluated per-policy inside Kyverno, not flattened onto the shared webhook.
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
