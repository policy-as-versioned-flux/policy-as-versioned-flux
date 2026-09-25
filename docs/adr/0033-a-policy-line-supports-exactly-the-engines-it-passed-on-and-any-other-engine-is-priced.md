---
status: accepted
---

# A policy line supports exactly the engines it passed on, and an adopter on any other engine is priced

Decided 2026-09-25 by the assistant under [ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md),
labelled delegated. Eco-system ticket 71, rounds 1 to 3. Amends
[ADR-0003](0003-kyverno-validatingpolicy-cel.md), which chose the engine but decided no engine
version window.

## Context

A published policy line is a set of immutable policy bytes. The engine that runs those bytes is a
separate dependency, and a new engine version can change what the same bytes do. Kyverno 1.19.1
does not compile the 5.0.0 cage-tier body at all. The estate claimed no engine window before this
ADR. It pinned one engine, 1.18.2, in ten places across the hub, the platform and the three adopters.
Nothing asserted that those pins agree.

Before this ADR, platform PR 26 added a `tested_engines` field to the 5.0.0 element of
`distribution/versions.yaml`, and a grader, `computed-semver/engine_compatibility.py`. The platform
README calls the field "not a runtime support range". This ADR makes it one.

## Decision

1. **A line supports exactly the engines it passed on.** A line's supported engines are the exact
   versions in its `tested_engines`. On each of them, the line's cage fixtures passed. No range is
   declared, and no neighbouring patch is inferred. `1.18.3` is unsupported until the line passes
   on it. CONTEXT.md: **Supported engine**.
2. **The adopter owns its engine version.** The adopter installs its own engine. The platform
   cannot choose another org's engine. The adopter's engine install pin, in its own gitops, is the
   declaration. Composition reads the version from that file. The drift sample installs from
   that file, observes the running engine, and records "the running engine equals the declared
   engine" as a drift fact. A false fact is a red. CONTEXT.md: **Declared engine**.
3. **An unsupported pairing is priced, never refused.** If the adopter's declared engine is not a
   supported engine of a line that the adopter composes, the line's control claims do not count on
   that engine. Every control that the line claims is then a hole, as
   [ADR-0026](0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md) prices it. The evidence document shows an
   `unsupported-engine` delta that names the pairing. An adopter with no declared engine gets the
   same price under an `undeclared-engine` delta. CONTEXT.md: **Unsupported pairing**.
4. **One grader run grades every cell.** A cell is one line on one engine. The caller supplies
   one binary for each engine. A listed cell with no binary reads could-not-look, and that is red.
   The platform keeps one table of engine versions, with a pinned checksum for each CLI and each
   `install.yaml`.
5. **An engine bump is not a policy version.** The policy bytes do not change, so the line keeps
   its version.
   - To add an engine to a cut line changes metadata only. The same change must pass the new
     cells.
   - To remove an engine narrows the line's support. An adopter that declares that engine gets the
     `unsupported-engine` delta at its next composition.
   - The estate's own pins must name a supported engine of every served line. These pins are the
     hub truth CLI, the platform release CLI and the platform in-cluster engine. A gate check
     asserts this.
   - The route is a reviewed PR that the gate grades. There is no Renovate path.
6. **A fixture grades what is generated, not how the engine reports a miss.** A "generates
   nothing" check compares the generated documents with an empty expected set. It does not assert
   a `skip` result. Kyverno 1.19 returns no result for a GeneratingPolicy that does not match, so a
   `skip` row cannot pass on 1.19. The diagnosis is in
   `.scratch/ecosystem/research/kyverno-1.19-cage-diagnosis/`.

## Considered options

- **A declared range, such as `>=1.18.0 <1.20.0`.** Rejected. A range asserts behaviour on
  engines that no run measured.
- **The platform supplies the adopter's engine through its distribution.** Rejected. It hides the
  real failure, an adopter that runs a different engine.
- **Refuse an unsupported pairing as an instrument fault.** Rejected. It adds a refusal that
  ADR-0026 retired. It also blocks all three adopters today, because none of them declares an
  engine.
- **An engine bump cuts a new policy version.** Rejected. It adds versions with unchanged bytes,
  and each one needs every adopter's acceptance. A failed cell already guards behaviour, because a
  changed verdict on a new engine keeps that engine out of the tested set.
- **Expected results for each engine in the fixture.** Rejected. It puts one engine's reporting
  quirk into the claim.

## Consequences

- A new Kyverno patch release is unsupported by every line until the gate grades it.
- Until an adopter declares its engine, composition prices the adopter's composed lines as holes.
  So the adopters' declarations must land before the pricing does.
- On 2026-09-25 only point 1's field and a grader for one engine exist. The grader requires
  `tested_engines.kyverno == [running version]`, so a second engine reads could-not-look. Points 2
  to 6 wait on eco-system tickets 146 to 150.
