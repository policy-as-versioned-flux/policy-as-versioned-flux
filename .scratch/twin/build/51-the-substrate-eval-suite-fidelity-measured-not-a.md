# 51 — The substrate eval suite: fidelity measured, not asserted

**What to build:** **Fidelity is defined and tuned by measurement.** Signal-to-noise, plant difficulty, spine
consistency, reporting asymmetry, mundanity — each a metric with a target.

The record's **negativity bias** is modelled deliberately here rather than as a separate concern:
reporting asymmetry as measured and negativity bias as produced are the same asymmetry, and
separating them would have had two tickets fighting over one property.

**Blocked by:** 50

**Status:** ready-for-agent

**Reading list:** Decision ticket 12. Spec stories 56, 60.

- [ ] Each fidelity dimension is a computed metric with a declared target and a current value.
- [ ] Tuning the generator against the targets is a supported loop, not a manual eyeball.
- [ ] Negativity bias is a measured, targeted property of the substrate — the record's real asymmetry, reproduced rather than idealised away.
- [ ] The suite is the acceptance test for ticket 49's depth grade.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
