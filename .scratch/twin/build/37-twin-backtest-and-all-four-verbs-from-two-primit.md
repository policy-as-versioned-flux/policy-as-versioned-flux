# 37 — `twin backtest`, and all four verbs from two primitives

**What to build:** Backtest is **rewind plus projection scored against the record** — deliberately not a separate
harness, because a second harness is a second implementation of the same thing and it would drift.

The spec claims all four operations fall out of exactly two primitives. That claim is untested until
someone demonstrates it, so this ticket demonstrates all four: projection (time-forward), act-now
(intervention-at-present), counterfactual (rewind + intervention), backtest (rewind + projection).

**Blocked by:** 36

**Status:** ready-for-agent

**Reading list:** Decision ticket 13. Spec stories 35, 38.

- [ ] Backtest implemented purely as a composition of rewind and projection, with no backtest-specific code path.
- [ ] All four operations demonstrated as compositions of the same two primitives.
- [ ] A test asserting no separate backtest harness exists — the composition is the implementation.
- [ ] Backtest emits scoring-eligible forecasts only under `as-consumed`.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
