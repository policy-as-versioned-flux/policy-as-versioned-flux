# 49 — `substrate-generator`: the synthetic world

**What to build:** Generate the world — org events, communications, HR records, telemetry — as the **medium** in which
instrumented test cases sit. Believability serves measurement rather than competing with it, and
where they conflict, **measurability wins**.

The second of the two hardest tickets, split from the recipe mechanics for that reason.

**Blocked by:** 48

**Status:** ready-for-agent

**Reading list:** Decision ticket 12 (synthetic substrate). Spec stories 54, 55.

- [ ] Skill generates a coherent multi-modal substrate from a pinned recipe.
- [ ] Generation is seeded and regenerable via ticket 48's mechanics.
- [ ] Output is mundane by default — the substrate is mostly uninteresting, because real ones are.
- [ ] Where believability and measurability conflict, the resolution is recorded, and measurability wins.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
