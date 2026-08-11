# 03 — Depth grades as computed checklists, and authored/derived marking

**What to build:** A capability's depth grade is **computed, never typed**. It is a checklist with one line per
acceptance criterion of its owning decision ticket, each checked or not; `full` means every line is
checked. Self-declared grades are how "premature done" happens, and story 87's guarantee that each
ticket's full acceptance criteria remain the yardstick has no enforcement without this.

Every artefact is marked authored or derived at load, and the marking is enforced rather than
conventional.

**Blocked by:** 02

**Status:** done (2026-08-05)

**Reading list:** Decision ticket 20 (per-capability depth grades; the three named failure modes). Spec stories 86, 87, 88.

- [x] A depth grade is a checklist referencing its owning decision ticket's ACs by index; `full` is derived from the checklist and cannot be asserted directly.
- [x] A capability with no depth grade fails to load.
- [x] `every_capability_depth_graded` and `every_artefact_marked` go live.
- [x] A malformed or hand-edited grade (claiming `full` with unchecked lines) is rejected with the specific unchecked criteria named.
- [x] Depth grades are readable at runtime by anything that renders a capability, so a partial capability announces itself without anyone remembering to.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/grades.py`, `twin/capabilities/*.yaml`; visible with `twin grade`.

- A capability's checklist has one line per acceptance criterion of its owning **decision** ticket, and
  the criterion text is copied in and **re-validated against the ticket on every load** — a checklist
  that has quietly drifted from its yardstick is worse than no checklist.
- `grade` is a property with no setter. A file that types one is rejected *and names the unchecked
  criteria that make the claim false*, rather than just refusing.
- A tick needs `evidence` and `ticked_by`; a tick with no witness is a self-declared grade wearing a
  checklist's clothes.
- The depth block travels in every artefact and the CLI prints it, so a partial capability announces
  itself without anyone remembering to.

Five capabilities are graded, all `partial` or `stub`; none can reach `full`, and the shipped grades are
asserted as such by a test.
