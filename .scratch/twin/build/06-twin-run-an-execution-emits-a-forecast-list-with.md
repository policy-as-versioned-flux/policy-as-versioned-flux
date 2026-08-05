# 06 — `twin run` — an execution emits a forecast list with pins

**What to build:** One scenario executes at a declared time and emits **forecasts — plural, always a list**, each
with its pins. There is no code path anywhere that collapses the list to one, and there never will
be: the ability to collapse would be used.

Still stub-graded. The scenario object here is minimal; the standing library comes much later.

**Blocked by:** 05

**Status:** ready-for-agent

**Reading list:** Decision ticket 13 (scenario and gameplay engine). Spec stories 8, 35, 36.

- [ ] A scenario references {components, graph version, world model, time} and executes.
- [ ] The output is a list even when it has one member; no API accepts a request for a single forecast.
- [ ] `no_collapse_mechanism` and `no_recommended_action_field` go live.
- [ ] Pins captured on every forecast: model repo ref, world ref, command, and any model version involved.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
