# 09 — Reliability diagrams over volume, and scheduled emission

**What to build:** Calibration is a property measured over volume, so the two halves belong together: the reliability
diagram needs forecasts, and scheduled emission is what produces them. The schedule also protects
the record from selection bias — we cannot only forecast when we feel confident.

Scheduled-execution orchestration is inherited from `/arckit:build --refresh`, which **assumes a
single repository while this is an org of repositories**. That adaptation is this ticket's work, not
a footnote.

**Blocked by:** 08

**Status:** ready-for-agent

**Reading list:** Decision tickets 11, 13. Research 04 (arckit toolkit) for the refresh caveat. Spec stories 19, 37, 44.

- [ ] Reliability diagram produced over a forecast population, with bin counts shown so a thin bin cannot masquerade as calibration.
- [ ] Scheduled execution runs the standing scenario set without human initiation.
- [ ] The single-repository assumption in the inherited orchestration is adapted to an org of repositories, and the adaptation is documented as a deviation.
- [ ] Emission is provably not event-gated: a run with no new signals still emits.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
