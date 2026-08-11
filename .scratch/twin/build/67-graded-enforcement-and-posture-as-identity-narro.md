# 67 — Graded enforcement and posture-as-identity, narrowed

**What to build:** Consequence as a **spectrum rather than a cliff edge**, and posture-as-identity retained only where
the evidence supports it.

**Blocked by:** 66

**Status:** ready-for-agent

**Reading list:** Decision ticket 18. Spec stories 83, 84.

- [ ] Enforcement grades are implemented and a control can occupy any of them.
- [ ] Posture-as-identity is scoped to the cases the evidence supports, with the unsupported cases named as excluded.
- [ ] Moving a control between grades is a versioned, signed change.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
