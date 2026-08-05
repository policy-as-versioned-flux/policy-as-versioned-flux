# 13 — Derived roll-ups

**What to build:** Roll-ups are derived, never authored, so an aggregate can never drift from its constituents.

**Blocked by:** 12

**Status:** ready-for-agent

**Reading list:** Decision ticket 07. Spec story 9.

- [ ] A roll-up is computed from constituents on read and has no authored form.
- [ ] An attempt to author a roll-up value directly is rejected.
- [ ] Changing a constituent changes the roll-up with no separate step.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
