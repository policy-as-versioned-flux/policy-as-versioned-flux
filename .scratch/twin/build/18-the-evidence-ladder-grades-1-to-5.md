# 18 — The evidence ladder, grades 1 to 5

**What to build:** A typed ladder from **1 (dated natural experiment)** to **5 (model assertion)**, with the grade
travelling with the claim rather than living in a side table. The strength of a claim has to be
inseparable from the claim, because the whole use-gating mechanism depends on it.

**Blocked by:** 17

**Status:** ready-for-agent

**Reading list:** Decision ticket 08. Spec story 22.

- [ ] Five typed grades with written admission criteria per grade, versioned.
- [ ] The grade is a required field on every causal claim; an ungraded claim does not load.
- [ ] Grade is immutable without a provenanced regrade event recording who and why.
- [ ] A regrade upward is distinguishable from a regrade downward in the record — the former is the one to be suspicious of.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
