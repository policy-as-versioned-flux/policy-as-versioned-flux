# 14 — The Wardley spine: evolution positions and D/K/R

**What to build:** Real Wardley maths, **inherited from `/arckit:wardley`** rather than rebuilt: evolution positions
on the axis, and the D/K/R relations (`D = vis·(1−evo)`, `K = (1−vis)·evo`,
`R = vis(a)·(1−evo(b))`).

Inherited because it carries deterministic maths validated on write — which is exactly the code side
of the determinism split. The judgement side (which position, which play) is a skill and lands
later.

**Blocked by:** 12

**Status:** done (2026-08-06)

**Reading list:** Decision ticket 07; research 04 (arckit toolkit) for what is inherited and its caveats. Spec story 1.

- [x] Evolution positions are first-class on components and validated.
- [x] D/K/R computed via the inherited implementation, with a property test per relation.
- [x] The arckit caveats are recorded where they bite: `impact` has no history and its £ deltas are prose rather than formulas.
- [x] A map renders from the graph without a separate authoring step.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`twin/wardley.py`, the `wardley` block in every graph artefact, and `twin map`.

- **Inherited, not rebuilt.** The stage bands come from arckit 6.7.5's
  `hooks/validate-wardley-math.mjs` (`evolutionToStage`) and D/K/R from
  `skills/wardley-mapping/references/mathematical-models.md` section B. arckit's own three worked
  examples are asserted as tests: if the port drifts, the published example is what catches it.
- **A property test per relation**, over a deterministic 21x21 grid rather than a random search:
  bounds, the exact zero cases, monotonicity in each argument, and `R(a,b) == D` read across a
  dependency. No property-testing library and no new dependency.
- **Positions are first-class and validated.** A component declaring one map axis and not the other
  is refused — a half-position reads as a whole one. `evolution_position` refines the stage and must
  sit inside its band; absent, the band midpoint is derived and the artefact records that it was
  derived rather than authored. A component with no stage is **named** in `wardley.unpositioned`
  rather than silently dropped.
- **The map renders from the graph.** `twin map` reads the artefact's own `wardley` block and nothing
  else, so a map cannot say something the graph does not. There is no authoring step and no map file.

**The four arckit caveats are recorded in `twin/wardley.py` where they bite**, and one of them is now
an invariant. arckit publishes each relation with an **action band** ("must invest", "strong candidate
for outsourcing"); the number is inherited and the band is not, because an action band is a recommended
action under another name. `no_recommended_action_field` was extended to assert it. The others: arckit's
`impact` carries no history so no D/K/R number may be treated as a forecast and nothing scores them;
its £ deltas are prose rather than formulas and no money enters through this module; and its published
`R` example prints `0.85 x 0.75 = 0.64`, a display rounding of 0.6375 that is deliberately not inherited.

Not built: nothing here ticks a decision-ticket criterion either. Decision ticket 07's AC 6 asks where
£, risk, people, **assets** and signals attach to the graph; assets have no schema and £ has no engine.
