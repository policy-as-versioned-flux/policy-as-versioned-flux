# 148 — Composition prices an unsupported pairing

Type: task
Status: open
Blocked by: 146, 147, and the owner's authorisation for a platform tools tag

## Question

Graduated 2026-09-25 from grilling ticket 71, decision 6 (delegated), and ADR-0033 point 3.

An unsupported pairing is an adopter whose declared engine is not a supported engine of a line
that the adopter composes. Composition prices it and never refuses it. Build the following:

1. **Composition reads two facts.** It reads the adopter's declared engine from the adopter's
   `gitops/engine/kyverno.yaml` (ticket 147). It reads each composed line's `tested_engines` from
   the platform's `distribution/versions.yaml` at the adopter's pinned platform tag.
2. **An unsupported pairing makes every claimed control a hole.** On an engine that is not in a
   line's `tested_engines`, the line's control claims do not count. Each control that the line
   claims is then a hole, priced as ADR-0026 prices a hole. The evidence document shows an
   `unsupported-engine` delta that names the line and the engine.
3. **No declaration is priced the same way,** under an `undeclared-engine` delta.
4. **The composed header records the declared engine.**
5. **The machinery bodies that the composer renders move to `policies.kyverno.io/v1`** in the
   same platform tools release. They are `v1alpha1` today, and both engines mark `v1alpha1`
   deprecated. Ticket 149 moves the policy line's bodies.
6. **A hub check grades the price.** A planted declaration of an engine that a composed line does
   not list gives the `unsupported-engine` delta. Its amount equals the sum of the hole prices of
   the controls that the line claims.

Then the rollout: a platform tools tag, a pin move on each adopter, and a recompose on each
adopter.

## Done

Each adopter's composed evidence records its declared engine, 1.18.2, and shows no engine delta.
The hub check passes on its planted cases. The truth run after the recomposes records no fall.

## Notes

- The order is a safety rule. This ticket lands only after ticket 147 has landed on all three
  adopters. Otherwise all three get the `undeclared-engine` price, all their claimed controls
  become holes, and the gate records a fall.
- ADR-0020 refuses a missing instrument and prices a missing behaviour. An unsupported engine is
  priced, because the worst case is a behaviour: the cage does not load. On 1.19.1 the 5.0.0
  cage-tier body does not compile at all.
- The composer reads the substrate from the platform's `engine/namespaces.yaml`, never from the
  adopter (ticket 119). The engine version is the adopter's own fact, so it is read from the
  adopter.
