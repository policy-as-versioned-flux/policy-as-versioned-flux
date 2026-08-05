# 57 — Benchmark question selection and ingestion quarantine

**What to build:** Questions selected by a **versioned, pre-registered mechanical rule** spanning the full confidence
range — so a change to the selection rule is as visible as a change to the constraint set, and
cherry-picking easy questions is structurally prevented.

The benchmark set is **quarantined from ingestion at any lag**, and the quarantine is **auditable
because ingestion is provenanced**. That is what makes *"we forecast before we looked"* provable
rather than asserted.

**Blocked by:** 08, 53

**Status:** ready-for-agent

**Reading list:** Decision ticket 21 (forecast book). Spec stories 49, 50.

- [ ] Selection rule is mechanical, versioned and pre-registered; running it is reproducible.
- [ ] Selected questions span the full confidence range, demonstrated by their distribution.
- [ ] Quarantine holds at any lag and is auditable against the ingestion provenance record.
- [ ] A planted quarantine breach is detected by audit.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
