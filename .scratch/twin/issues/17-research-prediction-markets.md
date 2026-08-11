# 17 — Research: prediction markets (Polymarket et al.) as signal + calibration benchmark

Type: research
Status: RESOLVED (2026-08-05) — see `research/prediction-markets.md`

**Verdict:** signal source **yes, narrowly** (world layer only; consume price *moves*, not levels);
calibration benchmark **yes but only co-registered** (same question, same timestamp, blind emission) —
and it tests the *forecaster*, not the org-twin causal layer, so the circularity critique stays OPEN.
Aggregate-Brier comparison is rejected outright (scores aren't comparable across question sets).
Coverage is brutal: ~1 of 10 scenario families properly covered, 0% of the per-org overlay.
Decisive caution: favourite–longshot bias is significant in *every* subsample incl. highest-volume and
largest-transaction quintiles — liquidity does not fix it, and it is worst at the tails we care about.
Blocked by: none

## Question

How Polymarket and comparable world-event markets actually work, and how they could serve this project.
Assess skeptically; do not assume they fit.

- **Mechanics** — how these markets work (AMM vs order book, resolution/oracles, fees, liquidity,
  settlement disputes), and what a "price" actually means as a probability.
- **Calibration evidence** — how well do prediction-market prices actually forecast? Known biases
  (longshot bias, thin markets, manipulation, resolution ambiguity). Peer-reviewed evidence, not vibes.
- **As a SIGNAL SOURCE** — continuously-updated, money-backed, timestamped probabilities on real-world
  events that could feed our horizon scanning and move components.
- **As an EXTERNAL CALIBRATION BENCHMARK (the strong hypothesis to test)** — our project needs an
  external, adversarially-produced, timestamped answer key. A market price is exactly that: opposed-
  interest, money-backed, dated. Could our twin's forecasts be scored *against* market prices, or
  better, could the twin post forecasts on questions markets also price? What does that prove and what
  does it not?
- **Comparable systems** — Metaculus, Good Judgment/superforecasting, Kalshi, internal corporate
  prediction markets (and why those mostly failed), Brier-scoring communities.
- **Access** — APIs, data availability, historical price series, licensing, legality/jurisdiction (UK).
- **Limits** — what markets cover (mostly politics/crypto/sport) vs what we need (org-specific,
  technology-evolution, supply-chain). Is coverage too thin to be useful?

Output: `research/prediction-markets.md`. Verdict explicit: signal source? calibration benchmark? both?
neither? — with concrete integration shape if yes.
