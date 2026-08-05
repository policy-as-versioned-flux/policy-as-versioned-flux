# 36 — The three information regimes, gated by construction

**What to build:** **`as-consumed`** (only what the twin actually ingested by time T), **`as-knowable`** (everything
publicly available by T), **`with-hindsight`** (unrestricted). Only `as-consumed` produces a
scoring-eligible forecast.

The gaps localise failure: as-consumed versus as-knowable is a **sensing** failure; as-knowable
versus with-hindsight is an **interpretation** failure; present in all three, it is the **model**.
That triangulation is the reason for three regimes rather than one honest one.

**Blocked by:** 35

**Status:** ready-for-agent

**Reading list:** Decision tickets 11, 13, 19. Spec stories 39, 40.

- [ ] Regime is a required execution parameter with no default.
- [ ] `as_consumed_admits_no_post_T_fact` goes live, **asserted by construction** — the gate is structural, not a review step.
- [ ] A planted post-T fact causes an as-consumed run to fail rather than to quietly include it.
- [ ] The three-way gap is computed and reported as the localisation diagnostic, not left for a human to infer.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
