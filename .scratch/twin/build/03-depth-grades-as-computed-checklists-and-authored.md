# 03 — Depth grades as computed checklists, and authored/derived marking

**What to build:** A capability's depth grade is **computed, never typed**. It is a checklist with one line per
acceptance criterion of its owning decision ticket, each checked or not; `full` means every line is
checked. Self-declared grades are how "premature done" happens, and story 87's guarantee that each
ticket's full acceptance criteria remain the yardstick has no enforcement without this.

Every artefact is marked authored or derived at load, and the marking is enforced rather than
conventional.

**Blocked by:** 02

**Status:** ready-for-agent

**Reading list:** Decision ticket 20 (per-capability depth grades; the three named failure modes). Spec stories 86, 87, 88.

- [ ] A depth grade is a checklist referencing its owning decision ticket's ACs by index; `full` is derived from the checklist and cannot be asserted directly.
- [ ] A capability with no depth grade fails to load.
- [ ] `every_capability_depth_graded` and `every_artefact_marked` go live.
- [ ] A malformed or hand-edited grade (claiming `full` with unchecked lines) is rejected with the specific unchecked criteria named.
- [ ] Depth grades are readable at runtime by anything that renders a capability, so a partial capability announces itself without anyone remembering to.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
