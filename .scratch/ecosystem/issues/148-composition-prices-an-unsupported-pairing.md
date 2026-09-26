# 148 — Composition prices an unsupported pairing

Type: task
Status: open
Blocked by: 146, 147, and the owner's authorisation for a platform tools tag and the adopter tags

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 6, 16 and 18 (delegated), and ADR-0033
points 3 and 7.

An unsupported pairing is an adopter whose declared engine is not a supported engine of a line, or
of the machinery, that the adopter composes. Composition prices it and never refuses it. Build the
following in the platform tools:

1. **Composition reads three facts.**
   - The adopter's declared engine, from its `gitops/engine/kyverno.yaml` (ticket 147).
   - Each composed line's `tested_engines`, from the platform's `distribution/versions.yaml` at the
     adopter's pinned platform tag.
   - The machinery's `tested_engines`, from the same platform tag (ticket 146 item 4).
2. **An unsupported pairing makes every claimed control a hole.** On an engine that a line does
   not support, the line's control claims do not count. Each control that the line claims is then
   a hole, priced as ADR-0026 prices a hole. The evidence document shows an `unsupported-engine`
   delta that names the line and the engine. The machinery's claim, cm-6, is priced the same way.
   A line or a machinery release with no `tested_engines` supports no engine.
3. **No declaration is priced the same way,** under an `undeclared-engine` delta. Under ADR-0020
   this is a missing behaviour, not a missing instrument: the gate can read the claims and their
   hole prices, and only the engine is unknown.
4. **The composed header records the declared engine.**
5. **The shift-left check runs each line only on engines that the line supports** (decision 18).
   `shift-left/ci-check.py` runs every line in the ±1-major window with the adopter's declared
   engine. A line in the window that does not support that engine is reported by name as an
   unsupported pairing. It is not a compile error and not a pass.
6. **The machinery supports 1.19.1 and moves to `policies.kyverno.io/v1`** in the same tools
   release. Some machinery bodies build the same `variables.tier` label map that does not compile
   on 1.19.1, so fix each body that ticket 146 item 4 grades red, as ticket 149 fixes cage-tier.
   Then the machinery's `tested_engines` is `[1.18.2, 1.19.1]`. The bodies are `v1alpha1` today,
   and both engines mark `v1alpha1` deprecated. Ticket 149 moves the policy line's bodies.
7. **A hub check grades the price.** A planted declaration of an engine that a composed line does
   not list gives the `unsupported-engine` delta. Its amount equals the sum of the hole prices of
   the controls that the line claims.

Then the rollout. Each step after the first is an owner step:

- a signed platform tools tag;
- a pin move on each adopter;
- a recompose on each adopter;
- each adopter's signed composed tag, and its composed-set move to that tag (ticket 130's route).
  The machinery reaches a cluster only through that move.

## Done

Each adopter's composed evidence records its declared engine, 1.18.2, and shows no engine delta.
The hub check passes on its planted cases. The truth run after the recomposes records no fall.

## Notes

- The order is a safety rule. This ticket lands only after ticket 147 has landed on all three
  adopters. Otherwise all three get the `undeclared-engine` price, all their claimed controls
  become holes, and the gate records a fall.
- The price assumes the worst case: the body does not load. Whether a body that does not compile
  fails open or refuses at admission is not measured. Ticket 150 measures it. If admission refuses,
  ADR-0033 point 3 reopens.
- The composer reads the substrate from the platform's `engine/namespaces.yaml`, never from the
  adopter (ticket 119). The engine version is the adopter's own fact, so it is read from the
  adopter.
