# 35 — The rewind primitive

**What to build:** Rewind to a dated past state — Pearl's **abduction**. The first of the two primitives from which
everything else composes.

**Blocked by:** 20

**Status:** ready-for-agent

**Reading list:** Decision ticket 13. Spec story 38.

- [ ] Rewind to a declared timestamp produces a model state, not a filtered view.
- [ ] The mapping to abduction is documented and the semantics tested, not asserted as a metaphor.
- [ ] Rewind composes with intervention (`do()` at a past time) without special-casing.
- [ ] Rewinding to a time before the model existed fails explicitly rather than returning an empty state.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
