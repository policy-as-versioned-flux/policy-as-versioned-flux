# 21 — The co-registered forecast book: the external gate

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 08, 11, 13, 17 (all resolved)

## Question

`research/prediction-markets.md` identified the one mechanism that escapes the memorisation problem:
**co-registered forecasting** — the twin emits blind on the same questions, timestamps and resolution
criteria as a liquid market, and both are scored on the same set. **Forward-dated questions cannot be
in any training corpus**, so it is contamination-proof by construction.

**Already determined:**
- Consume market **price moves** as world-layer signals; never price **levels** as probabilities
  (favourite–longshot bias rejects unbiasedness in every subsample, worst in the deep tail) (17).
- Aggregate Brier comparison is rejected — Brier is a property of *(forecaster, question set)* (17).
- Scheduled emission, scoreability declared at run time, only *as-consumed* regime scores (11, 13).
- Coverage is thin: ~1 in 10 scenario families, **0% of the per-org overlay** — world-layer only (17).

**Open:**
- **Which questions** — how are they selected without reintroducing selection bias?
- **Which venues** — Polymarket, Kalshi, Metaculus; regulated vs not; UK legality for *participation*
  vs mere observation.
- **The blind-emission protocol** — what stops the twin seeing the market price before it forecasts?
- **What is claimed** — the honest scope of what a good score proves, and what it does not.
- **Does it feed the model, or only score it?** (Using market moves as signals AND scoring against
  markets risks a circularity.)
- **Cost/effort** — is this worth building for a capability that touches ~10% of the scenario library?

## Acceptance criteria
- [ ] A question-selection rule that does not reintroduce selection bias.
- [ ] Venue decision + the observe-vs-participate call (incl. UK legality).
- [ ] A blind-emission protocol that is mechanically enforceable.
- [ ] An explicit claim-scope statement: what a good score proves and what it does not.
- [ ] The circularity question resolved (signal source vs benchmark).
- [ ] A proportionality verdict: is it worth building at this coverage?

## Decided so far (grilling 2026-08-05)

**Q1 — circularity: (b) QUARANTINED BENCHMARK SET + (c) TEMPORAL SEPARATION.** They defend different
failures and both are needed.
- **(b) The quarantine makes the claim clean.** A defined **benchmark set** of markets is **never ingested
  as a signal, in any form, at any lag**; the rest of the market universe may feed the twin freely.
  Mechanically enforceable as an ingestion filter on a named list, and **auditable because ingestion is
  provenanced** (14). Cheap, since markets already touch only ~10% of the scenario families.
- **(c) Temporal separation handles the operational side** within that set: emission timestamps are
  **pinned and signed before the resolution window**, so *"we forecast before we looked"* is a **provable
  claim rather than an assurance** — precisely what ticket 14's machinery exists for.
- **(c) alone is insufficient:** even unseen, a market's price may reach the twin via correlated markets or
  the news that moved them, and the ensemble world-models may be shaped by market-derived signals
  generally. Temporal separation stops **direct copying**, not **indirect inheritance**.
**Residual honesty, to be written into the claim scope rather than papered over: quarantine proves NO
DIRECT INGESTION; it cannot prove the model's priors were unshaped by market-adjacent information.** That
narrower claim is the difference between a gate and a boast.

**Q2 — question selection: (b) A VERSIONED, PRE-REGISTERED MECHANICAL RULE**, with (c) random sampling as
a volume valve if the rule selects too many.
Choosing *which* questions to co-register is the same hazard ticket 11's scheduled emission exists to
prevent, wearing a different hat. (a) forecasting *everything* is impractical and drowns the signal
(mostly sports/crypto, where a good score says nothing about organisational anticipation) — but any
**relevance filter is itself a selection lever**, so the rule must be **fixed and dated before seeing the
questions**.
**What makes it honest is machinery we already have:** the selection rule is an **authored artefact —
versioned, signed, dated** (14). The rule is inspectable, the selection is **reproducible from it**, and
**a change to the rule is as visible as a change to the constraint set** — *"we narrowed the categories
after a bad quarter"* becomes a dated diff someone can point at rather than invisible drift. We cannot
stop rule-gaming; we can make it legible.
**Baked into the rule rather than left to judgement:**
- it must span the **full confidence range** — the boring near-certainties are what reliability diagrams
  need at the extremes;
- it must be stated in **resolvable terms** (liquidity threshold, resolution horizon, category list) so
  applying it requires **no interpretation**.

**Q3 — proportionality: (b) BUILD IT MINIMALLY — a small standing set, continuously run, treated as a
FLOOR not a proof.**
**The proportionality is better than the coverage number suggests, because ticket 20 already puts the
scoring harness in the first slice.** The marginal cost of co-registration is then small: a **selection
rule**, a **quarantine filter** on the ingestion path, and a **venue adapter**. We are not building a
forecasting system — we are pointing an existing one at extra questions. At 10% coverage a *major* build
would be indefensible; a thin adapter onto machinery that must exist anyway is easily worth it.
**The value is disproportionate to the coverage because it is the only mechanism that CANNOT be
contaminated.** Every other check — synthetic substrate, historical backtests — has a memorisation problem
we can discount but never eliminate. This one is clean by construction, and a narrow clean signal beats a
broad compromised one.

**Q4 (derived) — venue: OBSERVE ONLY, NEVER PARTICIPATE.** We need prices and resolutions, not positions.
Participation would add UK legal exposure (Polymarket's regulatory history; gambling-law framing) for **no
epistemic gain** — research 17 found **play-money forecasts land within 1–5pp of real-money ones**, so
"money-backed" buys almost nothing. Observing public prices carries none of that exposure. Venues to
adapt: the liquid, well-resolved ones (Kalshi as the regulated option; Polymarket for coverage;
Metaculus for long-horizon and its published scoring practice).

**Q5 (derived) — CLAIM SCOPE, stated narrowly and on purpose.**
A good co-registered score demonstrates: **the twin is not systematically overconfident** on
world-events it forecast blind, on a pre-registered question set, against an external adversarial
baseline it cannot grade itself against.
It demonstrates **nothing** about: the Wardley propagation, the causal elasticities, the £ pricing, the
org-specific overlay, or anything at organisational scale. **It tests general world-forecasting, not the
org-twin causal machinery** (research 17). And per Q1, the quarantine proves **no direct ingestion**, not
that priors were unshaped by market-adjacent information.
**So fable's "every loop closes through one mind" critique NARROWS but does not close** — this is the
first genuinely external, contamination-proof gate the project has, and it is deliberately a floor.

## RESOLVED (2026-08-05)

A **minimal, continuously-run co-registered forecast book**: a **versioned, pre-registered mechanical
selection rule** (spanning the full confidence range, stated in resolvable terms, its changes as visible
as constraint changes), a **quarantined benchmark set never ingested as signal**, **pinned and signed
emission before the resolution window** so blindness is provable, **observe-only venues**, and a
**deliberately narrow claim**: evidence of non-overconfidence in general world-forecasting, not validation
of the org-twin machinery. It is the project's only contamination-proof external gate — and a floor, not a
proof.

## Acceptance criteria — all met
- [x] Question-selection rule that does not reintroduce selection bias (versioned, pre-registered, mechanical).
- [x] Venue decision + observe-vs-participate (observe only; UK legality avoided; play≈real money).
- [x] A mechanically enforceable blind-emission protocol (quarantine list + pinned signed pre-emission).
- [x] Explicit claim-scope: what a good score proves and what it does not.
- [x] Circularity resolved (quarantine + temporal separation; residual limit stated).
- [x] Proportionality verdict (build minimally; marginal cost is low because scoring is already core).
