# 17 — Causal edges: sign, lag, and PERT elasticity

**What to build:** Every causal edge asserts a **sign**, a **lag**, and a calibrated-range **elasticity as a PERT
triple**, so propagation is quantitative rather than directional hand-waving.

**Blocked by:** 12

**Status:** ready-for-agent

**Reading list:** Decision ticket 08 (causal layer). Spec story 21.

- [ ] Edges carry sign, lag and a min/mode/max elasticity triple, validated on write.
- [ ] A degenerate triple (min = mode = max) is permitted but flagged, because false precision should be visible.
- [ ] The **graded-edge fixture** is generated in CI as the boundary contract for the £ and skills tracks.
- [ ] The pocket-org worksheet gains its edge elasticities here.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
