# 22 — Intervention versus observation: `do()` downstream-only

**What to build:** **Observation propagates bidirectionally; intervention propagates downstream only.** Learning a
fact updates beliefs everywhere, including about causes. *Doing* a thing does not rewrite its own
causes. This is Pearl's `do()` and it is not a nicety — a system that lets an intervention
back-propagate will cheerfully conclude that taking an action changed the past.

**Blocked by:** 20

**Status:** ready-for-agent

**Reading list:** Decision ticket 08. Spec story 18.

- [ ] `do()` and `observe()` are separate operations with different propagation semantics.
- [ ] Seam-2 property test: **`do()` leaves upstream beliefs untouched while `observe()` updates them**.
- [ ] An attempt to use one where the other is meant is a type error, not a runtime surprise.
- [ ] The pocket-org worksheet gains one of each and their differing expected outcomes.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
