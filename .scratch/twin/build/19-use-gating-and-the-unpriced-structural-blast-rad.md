# 19 — Use-gating and the unpriced structural blast-radius

**What to build:** **Only grades 1–2 may price a scored forecast.** Grade-5 model assertions are exactly where
contamination hides, so they must never silently become the basis of a number someone acts on.

The consequence is the second output: when a path is real but too weakly evidenced to price, the
answer is an **unpriced structural blast-radius** — "we know this is connected but cannot price
it" as a first-class result rather than a gap papered over.

Blast-radius traversal is **inherited from `/arckit:impact`**, whose known limits (no history, £
deltas as prose) apply.

**Blocked by:** 18

**Status:** ready-for-agent

**Reading list:** Decision tickets 08, 09; research 04. Spec stories 23, 24.

- [ ] `grade_5_only_path_never_prices` goes live: a scenario whose only causal path runs through a grade-5 edge emits blast-radius, never a price.
- [ ] Blast-radius is a distinct artefact type, not a price with a null field.
- [ ] The gating threshold is a versioned, published parameter — changing it is as visible as changing the constraint set.
- [ ] Reverse-dependency traversal inherited rather than rebuilt, with the arckit caveats recorded.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
