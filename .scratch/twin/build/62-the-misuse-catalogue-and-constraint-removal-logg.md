# 62 — The misuse catalogue and constraint-removal logging

**What to build:** Constraint removals are **logged together with the forbidden option's attractiveness at the moment
of removal** — so the motive is recorded when it exists rather than reconstructed afterwards, when
everyone has a better story.

**Blocked by:** 27

**Status:** ready-for-agent

**Reading list:** Decision ticket 15. Spec stories 60, 72.

- [ ] Misuse catalogue is a versioned artefact naming mechanisms, not just risks.
- [ ] Removing a constraint requires logging the excluded option's current attractiveness, computed not stated.
- [ ] The removal log is append-only and published.
- [ ] A removal with no attractiveness record is rejected.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
