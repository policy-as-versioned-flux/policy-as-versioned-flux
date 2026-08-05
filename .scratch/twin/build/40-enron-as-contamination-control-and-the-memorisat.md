# 40 — Enron as contamination control, and the memorisation-leakage discount

**What to build:** **The contamination pillar made quantitative.** An LLM asked about Enron has read the ending;
"flagging" Enron in 2000 is indistinguishable from reciting Enron in 2026.

So Enron is carried deliberately as a **control**: the measured gap between performance on Enron and
performance on an obscure key yields a **memorisation-leakage discount applied to every backtest
score**. The threat stops being acknowledged and starts being priced.

**Blocked by:** 39, 37

**Status:** ready-for-agent

**Reading list:** Decision tickets 01, 19; research on parametric contamination in map.md. Spec stories 46, 58.

- [ ] Enron key authored in the same format as the low-notoriety keys.
- [ ] The discount is **measured** from the Enron-versus-obscure gap, never hardcoded — a test asserts it changes when the underlying performance changes.
- [ ] Every backtest score carries its discount and the discount's basis.
- [ ] The discount is reported separately from the raw score so both are visible.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
