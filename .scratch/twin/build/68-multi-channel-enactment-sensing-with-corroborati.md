# 68 — Multi-channel enactment sensing, with corroboration setting the grade

**What to build:** **Declarations and machine-verified evidence are both sensor inputs, and corroboration between
channels sets the evidence grade.**

The elegant part is what this avoids: the action-state loop closes with **no new machinery** and with
*less* surveillance pressure rather than more — a self-declaration corroborated by reconciliation
state grades higher than either alone, so the incentive is to be verifiable rather than to be
watched.

**Blocked by:** 67, 53

**Status:** ready-for-agent

**Reading list:** Decision ticket 18. Spec story 20.

- [ ] Declarations and machine evidence ingest through the normal sensing path, with no enactment-specific pipeline.
- [ ] Corroboration between channels computes the evidence grade; single-channel claims grade lower.
- [ ] An uncorroborated self-declaration cannot reach a price-eligible grade.
- [ ] Reconciliation state (if Flux survived ticket 65) is one channel among several, not privileged.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
