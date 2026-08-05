# 64 — Flux drift measurement: instrument and wait

**What to build:** **Started near the front deliberately, because it needs elapsed calendar time and nothing from the
twin.** Instrument real enactment repositories and measure whether controls actually drift between
deploys, and whether that drift matters.

The falsification verdict (ticket 65) cannot be honest without a measurement window, and starting
the measurement at its natural dependency position would delay the answer by that window on top of
everything else.

Record now, as a precondition rather than a ticket-66 discovery: the **org-wide GitHub setting that
blocks Actions from creating PRs is currently off and needs an admin** to change.

**Blocked by:** 01

**Status:** ready-for-agent

**Reading list:** Decision ticket 22 (the Flux falsification test as recorded). Spec story 85.

- [ ] Real enactment repositories instrumented to record control state continuously.
- [ ] Measurement runs for a declared window and the window is stated up front, not chosen after seeing results.
- [ ] Drift events recorded with the interval between deploy and divergence.
- [ ] The org Actions-create-PRs setting is recorded as an open precondition with a named owner.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
