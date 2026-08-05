# 60 — Contestability as a primary workflow

**What to build:** **Arguing with the artefact is the supported workflow, not a complaints box.** Challenges are
versioned objects against specific artefacts, and there is **no hiding behind aggregation** — a
challenge to a constituent cannot be deflected to the roll-up.

Pulled early: an earlier draft parked this at position 61 of 72, which is a strange place for
something the spec calls a primary feature. It needs artefacts and signatures, and nothing else.

**Blocked by:** 11, 12

**Status:** ready-for-agent

**Reading list:** Decision tickets 07, 15. Spec story 77.

- [ ] A challenge is a versioned, signed object attached to a specific artefact and claim.
- [ ] A challenge against a constituent cannot be answered by pointing at an aggregate.
- [ ] Challenges are visible wherever the challenged artefact is visible.
- [ ] An unresolved challenge is a displayed state of the artefact, not a hidden queue.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
