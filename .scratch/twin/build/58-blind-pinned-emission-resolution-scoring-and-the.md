# 58 — Blind pinned emission, resolution scoring, and the narrow claim

**What to build:** Forecasts emitted, **pinned and signed before the resolution window opens**, on the same questions
and timestamps as liquid prediction markets. Forward-dated questions cannot be in any training
corpus, so this is the one external gate contamination cannot reach.

**Observe only, never place** — no UK gambling exposure, and play money tracks real money to within
1–5 percentage points anyway, so money-backing buys nothing.

The claim scope is stated **narrowly on purpose**: evidence of non-overconfidence in general
world-forecasting, and **nothing** about Wardley propagation, elasticities, £ pricing or the org
overlay. A real external gate oversold becomes a fake one.

**Blocked by:** 57, 11

**Status:** ready-for-agent

**Reading list:** Decision ticket 21; research 17 (prediction markets). Spec stories 48, 51, 52.

- [ ] Emission is signed and pinned before the resolution window, verifiably.
- [ ] Resolutions score against the same questions and timestamps, co-registered.
- [ ] No code path places a position; observe-only is structural.
- [ ] The narrow claim scope is published **with** every result, stating what the gate does not evidence.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
