# 28 — The constraint pre-filter, running before pricing

**What to build:** Ruin-class and forbidden options are removed by a **pre-filter that runs before pricing**, so no
number can ever be compared against them. This is the difference between a constraint and a very
large price: a price can be outbid.

**Blocked by:** 27, 23

**Status:** done (2026-08-06)

**Reading list:** Decision tickets 09, 15. Spec stories 30, 31.

- [x] `ruin_class_absent_not_priced` goes live — an excluded option is **absent from the output entirely**, not present with a large number.
      Met as *absent from the priced set, carrying no figure*. The removal **is** listed, with the constraint
      it crossed and no number anywhere in the record, because decision ticket 09 requires the exclusion to
      be disclosed rather than silent. A silently dropped option would satisfy the criterion as literally
      worded and defeat what it is for. The wording is what is wrong here, not the code.
- [x] `prefilter_precedes_pricing` goes live, asserted structurally rather than by ordering convention.
- [x] The pre-filter reads the published constraint set; it has no independent constraint list of its own.
- [x] A test proving no input magnitude causes an excluded option to reappear.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
