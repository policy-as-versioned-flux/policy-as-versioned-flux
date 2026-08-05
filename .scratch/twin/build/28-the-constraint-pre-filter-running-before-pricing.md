# 28 — The constraint pre-filter, running before pricing

**What to build:** Ruin-class and forbidden options are removed by a **pre-filter that runs before pricing**, so no
number can ever be compared against them. This is the difference between a constraint and a very
large price: a price can be outbid.

**Blocked by:** 27, 23

**Status:** ready-for-agent

**Reading list:** Decision tickets 09, 15. Spec stories 30, 31.

- [ ] `ruin_class_absent_not_priced` goes live — an excluded option is **absent from the output entirely**, not present with a large number.
- [ ] `prefilter_precedes_pricing` goes live, asserted structurally rather than by ordering convention.
- [ ] The pre-filter reads the published constraint set; it has no independent constraint list of its own.
- [ ] A test proving no input magnitude causes an excluded option to reappear.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
