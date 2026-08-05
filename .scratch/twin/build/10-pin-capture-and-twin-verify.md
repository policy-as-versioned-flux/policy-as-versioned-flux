# 10 — Pin capture and `twin verify`

**What to build:** Derivation is reconstructable rather than materialised — which works precisely because git is the
source of truth and everything else is derived. `twin verify` takes an artefact, recomputes it from
its pins, and reports whether it reproduces.

This is where determinism-given-pins stops being an aspiration. Includes the **cross-machine**
question: seeded floating-point identity across platform maths libraries and reduction orders is an
architectural constraint, and finding it late forces re-architecting the artefact format under sunk
cost.

**Blocked by:** 03

**Status:** ready-for-agent

**Reading list:** Decision ticket 14 (provenance and attestation). Spec stories 61, 64.

- [ ] `twin verify <artefact>` recomputes from pins and reports reproduce / diverge with a diff.
- [ ] Verification runs on a different machine from the one that produced the artefact, in CI.
- [ ] A deliberately non-deterministic operation is caught by verify rather than passing silently.
- [ ] Any tolerance or normalisation needed for cross-platform float identity is a **declared, tested** property of the artefact format, not an implicit one.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
