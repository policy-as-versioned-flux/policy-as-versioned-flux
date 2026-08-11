# 17 — Causal edges: sign, lag, and PERT elasticity

**What to build:** Every causal edge asserts a **sign**, a **lag**, and a calibrated-range **elasticity as a PERT
triple**, so propagation is quantitative rather than directional hand-waving.

**Blocked by:** 12

**Status:** done (2026-08-06)

**Reading list:** Decision ticket 08 (causal layer). Spec story 21.

- [x] Edges carry sign, lag and a min/mode/max elasticity triple, validated on write.
- [x] A degenerate triple (min = mode = max) is permitted but flagged, because false precision should be visible.
- [x] The **graded-edge fixture** is generated in CI as the boundary contract for the £ and skills tracks.
- [x] The pocket-org worksheet gains its edge elasticities here.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

The `influences` edge type in `twin/schema.py`, the causal block on every emitted edge, the new
`causal-layer` capability, and the `graded_edge_fixture_holds_its_contract` guard.

- **The structural/causal distinction is in the type, not in a comment.** `needs` says the value chain
  would break; `influences` says a change here moves something there, by this much, in this direction,
  after this long. Each family **refuses the other's fields**: a causal edge missing sign, lag,
  elasticity or evidence grade does not load, and a `knows` edge carrying a lag does not either. A
  structural dependency is not a measured effect.
- **The elasticity is a PERT triple, closed like everything else** — exactly min, mode and max, each on
  the unit interval, `min <= mode <= max`. There is no scalar form, because a single number cannot
  state its own uncertainty.
- **A degenerate triple is permitted and flagged.** An elasticity genuinely known to a point is
  representable; a point estimate wearing a range's clothes is not. Every emitted causal edge carries
  `degenerate_elasticity`, so false precision is visible in the artefact.
- **A causal edge runs component to component.** One from a person would be a measured effect
  attributed to a named individual, which is the thing decision ticket 15 refuses.
- **The graded-edge fixture is generated, never committed**, and asserted in CI as the boundary
  contract the £ and skills tracks build against: one real range, one degenerate, both fully graded,
  and a stripped edge refused.
- The pocket-org worksheet gained its edge elasticities here (lines 20-23).

Not built: nothing propagates yet. Sign, lag and elasticity are recorded and validated; no Monte-Carlo
reads them, there is no depth attenuation and no intervention semantics (build tickets 20-22). Decision
ticket 08's AC 5 asks for a **real** claim from each co-flagship; the fixture's EUV-delay edge is a toy
with invented numbers, so it stays unticked.
