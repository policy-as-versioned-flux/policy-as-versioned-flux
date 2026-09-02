# 71 — Which kyverno versions does the estate support?

Type: grilling (HITL)
Status: open
Blocked by: none

## Question

Ticket 54 pinned the gate to kyverno 1.18.2, the version the estate is authored against. That
makes the gate honest, but it does not answer the real question: the composed v4.0.0 that all
three adopters pin does not load on a 1.19 cluster at all.

Two incompatibilities are proven, and they are not the same size:

1. `cage-tier`'s label map fails to compile: `expected type 'string' but found 'dyn'` at
   `"posture.acme.io/tier": variables.tier`. `string(variables.tier)` compiles under both 1.18.2
   and 1.19.0, so this one is a one-line, backward-compatible fix.
2. With that applied, `cage-netpol`'s per-tier reach matrix then fails under 1.19 with a
   behavioural difference in the generated NetworkPolicy, not a compile error. Depth unknown.

The decisions the owner owns. What engine versions does a published policy line claim to support,
and where is that claim declared and graded? Does a supported-version claim belong on the
`versions.yaml` array element, so an adopter can price a cluster it cannot serve? Is fixing 1.19
a new policy version (the engine computes the bump), and if so does it ride with ticket 63's
isolated-default cut or stand alone? And does an adopter's declared cluster version become a fact
composition reads, so an unsupported pairing is a priced hole rather than a surprise at admission?

## Notes

Raised by the ambition review of 2026-08-31 and split out of ticket 54, which fixed the instrument
only. Evidence and the A/B table are in ticket 54's Answer.

## Comments

**2026-09-02, review.** One fact to add: every shipped policy is `policies.kyverno.io/v1alpha1` (69 files estate-wide), and no participant publishes a supported-engine-version matrix. A policy-as-a-versioned-dependency thesis owes its consumers a substrate compatibility window. Grade (a) whether the API is GA, (b) whether any artefact declares its substrate range, (c) whether a Kyverno bump goes through the computed-semver gate. Record: REVIEW-2026-09-02.md, completeness C4.
