# 14 — The Wardley spine: evolution positions and D/K/R

**What to build:** Real Wardley maths, **inherited from `/arckit:wardley`** rather than rebuilt: evolution positions
on the axis, and the D/K/R relations (`D = vis·(1−evo)`, `K = (1−vis)·evo`,
`R = vis(a)·(1−evo(b))`).

Inherited because it carries deterministic maths validated on write — which is exactly the code side
of the determinism split. The judgement side (which position, which play) is a skill and lands
later.

**Blocked by:** 12

**Status:** ready-for-agent

**Reading list:** Decision ticket 07; research 04 (arckit toolkit) for what is inherited and its caveats. Spec story 1.

- [ ] Evolution positions are first-class on components and validated.
- [ ] D/K/R computed via the inherited implementation, with a property test per relation.
- [ ] The arckit caveats are recorded where they bite: `impact` has no history and its £ deltas are prose rather than formulas.
- [ ] A map renders from the graph without a separate authoring step.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
