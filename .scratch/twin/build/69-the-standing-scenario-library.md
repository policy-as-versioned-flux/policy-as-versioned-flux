# 69 — The standing scenario library

**What to build:** Populate the committed set — **quantum/HNDL, bus-factor and key-person, insider and coercion,
supply shock, sanctions, M&A, memory cost, AI-model access, climate event** — plus opportunity plays
and backtest cases, each executable on the schedule.

**This is a ticket because leaving it as authoring work spread across other tickets was a scope
drop.** Only the entries the demo beats happen to need would have been written; nothing would have
forced the rest to exist, and the map treats the library contents as the acceptance tests each
workstream satisfies. Ownerless contents means dropped acceptance tests.

**Blocked by:** 09, 33, 37

**Status:** ready-for-agent

**Reading list:** Decision ticket 13; the map's committed signal classes. Spec story 43.

- [ ] One executable scenario per committed class, all nine named above.
- [ ] Opportunity plays represented, not only threats.
- [ ] Backtest cases included in the same library — no separate harness, per ticket 37.
- [ ] `standing_library_covers_committed_classes` added to the invariant suite, enumerating the committed set so a silently dropped class fails CI.
- [ ] The whole library executes on the schedule from ticket 09.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
