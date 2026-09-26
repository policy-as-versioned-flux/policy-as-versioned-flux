---
status: accepted
---

# A policy line supports exactly the engines it passed on, and an adopter on any other engine is priced

Decided 2026-09-25 and 2026-09-26 by the assistant under
[ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md), labelled delegated.
Eco-system ticket 71, rounds 1 to 5. Amends [ADR-0003](0003-kyverno-validatingpolicy-cel.md) and
supersedes its "≥1.18" floor.

## Context

A published policy line is a set of immutable policy bytes. The engine that runs those bytes is a
separate dependency, and a new engine version can change what the same bytes do. Kyverno 1.19.1
does not compile the 5.0.0 cage-tier body at all.

Before this ADR, the estate claimed a floor, "Kyverno ≥1.18", in ADR-0003, `docs/PRD.md` and a
comment in platform `engine/kyverno/helmrelease.yaml`. No run measured that range. The estate
pinned 1.18.2 in ten live install pins across the hub, the platform and the three adopters (hub
spikes excluded), and in one hub test constant. Two things tied some of them together: the platform
grader requires the hub CLI to equal each cut line's tested engines, and the hub test skips unless
the CLI on `PATH` reports its constant.

Platform PR 26 (97dd40d, 2026-09-10) added a `tested_engines` field to the 4.0.0 and 5.0.0
elements of `distribution/versions.yaml`, and a grader, `computed-semver/engine_compatibility.py`.
4.0.0 has since retired. The platform README calls the field "not a runtime support range", and
the grader grades only cage-tier and cage-netpol. This ADR makes the field a support range and
widens what it grades.

## Decision

1. **A line supports exactly the engines it passed on.** A line's supported engines are the exact
   versions in its `tested_engines`. On each of them, every body that the line serves compiles and
   its fixtures pass. No range is declared, and no neighbouring patch is inferred. `1.18.3` is
   unsupported until the line passes on it. The machinery that the platform tools release renders
   carries its own `tested_engines`, graded the same way. CONTEXT.md: **Supported engine**.
2. **The adopter owns its engine version.** The platform cannot choose another org's engine. The
   adopter's engine install file, `gitops/engine/kyverno.yaml` in its own repo, is its declared
   engine. Every cluster of the adopter that runs an engine installs Kyverno from that file. Today
   that is each adopter's drift lane, and `kind-driftwood`, which driftwood owns and where
   tuppence's workload flagship also runs. `kind-tuppence` and `kind-ludlow` run no engine today,
   and this ADR adds none. A cluster that more than one adopter uses runs one engine, so those
   adopters must declare the same engine, and a check asserts that. A static check asserts that the file's
   version, install URL and checksum agree with the platform engine table's row for that version.
   No drift fact compares the lane's engine with the file, because the lane installs from that
   file and such a fact can only read true. CONTEXT.md: **Declared engine**.
3. **An unsupported pairing is priced, never refused.** If the adopter's declared engine is not a
   supported engine of a line that the adopter composes, the line's control claims do not count on
   that engine. Every control that the line claims is then a hole, as
   [ADR-0026](0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md) prices it.
   The evidence document shows an `unsupported-engine` delta that names the pairing. The same rule
   applies to the machinery and its claims. A line or a machinery release with no `tested_engines`
   supports no engine.
   - An adopter with no declared engine gets the same price under an `undeclared-engine` delta.
     Under [ADR-0020](0020-a-missing-instrument-refuses-a-missing-behaviour-is-priced.md) this is a
     missing behaviour, not a missing instrument. The gate can read everything the price needs: the
     line's claims and their hole prices. Only the engine is unknown, and the price already assumes
     the worst engine.
   - The worst case is that a body does not load. Whether a body that does not compile fails open
     or refuses at admission is not measured. Ticket 150 measures it. If admission refuses, this
     point reopens, because a refusal is not a hole (ticket 98).
   CONTEXT.md: **Unsupported pairing**.
4. **One grader run grades every cell, before and after the cut.** A cell is one line on one
   engine. The caller supplies one binary for each engine. A listed cell with no binary reads
   could-not-look, which is red. The platform keeps one table of engine versions, with a pinned
   checksum for each CLI and each `install.yaml`, and the Helm chart version where one applies. An
   uncut element that carries `tested_engines` is graded on the tree of the commit that declares
   it. The cut is signed only after every cell passes. After the cut, the grade reads the tag. This
   reverses the platform README, which says that the grader is "deliberately **not** wired as a
   new-policy pre-cut gate".
5. **An engine bump is not a policy version.** The policy bytes do not change, so the line keeps
   its version.
   - To add an engine to a line changes metadata only. The same change must pass the new cells.
   - To remove an engine narrows the line's support. An adopter that declares that engine gets the
     `unsupported-engine` delta at its next composition.
   - Composition reads `tested_engines` at the adopter's pinned platform tag. So a support change
     reaches an adopter only through a signed platform tools tag and the adopter's pin move.
   - The estate's own pins must name a supported engine of every served line: the hub truth CLI,
     the platform release CLI, the platform reference install and the hub test constant. A gate
     check asserts this.
   - The route is a reviewed PR that the gate grades. There is no Renovate path.
6. **A fixture grades what is generated, not how the engine reports a miss.** A "generates
   nothing" check compares the generated documents with an empty expected set. It does not assert a
   `skip` result. Kyverno 1.19 returns no result for a GeneratingPolicy that does not match, so a
   `skip` row cannot pass on 1.19. The diagnosis is in
   `.scratch/ecosystem/research/kyverno-1.19-cage-diagnosis/`.
7. **An adopter's shift-left check runs each line only on engines that the line supports.** The
   check uses the declared engine. A line in its window that does not support that engine is
   reported by name as an unsupported pairing. It is not a compile error and not a pass.

## Considered options

- **A declared range, such as `>=1.18.0 <1.20.0`.** Rejected. A range asserts behaviour on engines
  that no run measured.
- **Support means the cage fixtures only.** Rejected. The bodies that carry the control claims
  would then be priced on a support claim that never tested them.
- **The platform supplies the adopter's engine.** Rejected. It hides the real failure, an adopter
  that runs a different engine.
- **A drift fact that compares the lane's running engine with the declaration.** Rejected. The
  lane installs from the declaration, so the fact can only read true.
- **Refuse an unsupported pairing as an instrument fault.** Rejected. It adds a refusal that
  ADR-0026 retired. It also blocks all three adopters today, because none of them declares an
  engine.
- **An engine bump cuts a new policy version.** Rejected. It adds versions with unchanged bytes,
  and each one needs every adopter's acceptance. A failed cell already guards behaviour, because a
  changed verdict on a new engine keeps that engine out of the tested set.
- **Write `tested_engines` only after the cut.** Rejected. A tag would then be signed before anyone
  knew whether the line passes on its engines.
- **Expected results for each engine in the fixture.** Rejected. It puts one engine's reporting
  quirk into the claim.

## Consequences

- A new Kyverno patch release is unsupported by every line until the gate grades it.
- Until an adopter declares its engine, composition prices the adopter's composed lines as holes.
  So the adopters' declarations must land before the pricing does.
- On 2026-09-26 only point 1's field and a grader for one engine and two families exist. The
  grader requires `tested_engines.kyverno == [running version]`, so a second engine reads
  could-not-look. Points 2 to 7 wait on eco-system tickets 146 to 150.
