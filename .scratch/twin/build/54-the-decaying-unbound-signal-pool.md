# 54 — The decaying unbound signal pool

**What to build:** Signals the graph cannot yet interpret are **retained in a decaying pool** rather than discarded. A
signal the model could not interpret today is not the same as a signal that does not matter.

**Blocked by:** 53

**Status:** ready-for-agent

**Reading list:** Decision ticket 11. Spec story 16.

- [ ] Unbound signals are retained with a decay function, not dropped.
- [ ] The decay function is a versioned, published parameter.
- [ ] Pool size and age distribution are observable.
- [ ] A signal that decays out is recorded as having done so, not silently deleted.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
