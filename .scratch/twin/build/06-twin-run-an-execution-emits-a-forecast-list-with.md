# 06 — `twin run` — an execution emits a forecast list with pins

**What to build:** One scenario executes at a declared time and emits **forecasts — plural, always a list**, each
with its pins. There is no code path anywhere that collapses the list to one, and there never will
be: the ability to collapse would be used.

Still stub-graded. The scenario object here is minimal; the standing library comes much later.

**Blocked by:** 05

**Status:** done (2026-08-05)

**Reading list:** Decision ticket 13 (scenario and gameplay engine). Spec stories 8, 35, 36.

- [ ] A scenario references {components, graph version, world model, time} and executes.
- [x] The output is a list even when it has one member; no API accepts a request for a single forecast.
- [x] `no_collapse_mechanism` and `no_recommended_action_field` go live.
- [x] Pins captured on every forecast: model repo ref, world ref, command, and any model version involved.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/verbs.py` `run()`.

- A scenario references {components, graph version, world models, time} and emits **forecasts, plural,
  always** — one per named world model, each carrying its own pins. The fixture scenario names three
  rival world models including the org's own believed map, so the spread is visible in the output.
- There is no singular `forecast` field to read instead of the list, no flag that selects one, and no
  function that combines them. `no_collapse_mechanism` asserts all three: the list, the absent fields,
  and a source scan of `verbs.py` and `cli.py` for collapse affordances.
- Forbidden field names are refused **at emission** as well as asserted by the suite, so the absence
  holds by construction and not only by review.
- "Any model version involved" is currently the tool version and the capabilities digest. No LLM model
  versions yet, because no skill runs on this path.
