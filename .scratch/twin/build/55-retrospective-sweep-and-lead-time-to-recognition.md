# 55 — Retrospective sweep and lead-time-to-recognition

**What to build:** A model change triggers a **retrospective sweep** of the unbound pool — and that is what makes
**lead-time-to-recognition measurable**.

This is the quantum / harvest-now-decrypt-later case mechanised: the signal was in the pool for two
years before the graph could interpret it, and that interval is the number that matters.

**Blocked by:** 54

**Status:** ready-for-agent

**Reading list:** Decision ticket 11. Spec stories 16, 17.

- [ ] A model change triggers a sweep of the pool and rebinds what has become interpretable.
- [ ] **Lead-time-to-recognition** is computed per rebound signal: pool-entry date to binding date.
- [ ] The metric is reported as a first-class output, not an internal statistic.
- [ ] A worked case demonstrating a multi-year lead time on a real dated signal class.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
