# 59 — Prediction-market price moves as world-layer signals

**What to build:** Consume market **price moves** as dated world-layer signals — while never treating price
**levels** as probabilities.

The reason is specific rather than fastidious: favourite–longshot bias is rejected-unbiased in every
subsample and is **worst in the deep tail**, which is exactly the region the risk engine exists to
reason about.

**Blocked by:** 57, 53

**Status:** ready-for-agent

**Reading list:** Decision ticket 21; research 17. Spec story 53.

- [ ] Price moves ingest as dated world-layer signals through the normal sensing path.
- [ ] `price_levels_never_probabilities` is added to the invariant suite and goes live.
- [ ] An attempt to use a level as a probability fails rather than warns.
- [ ] The bias evidence is cited in the artefact that consumes these signals.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
