# 16 — Research: Google TabFM — real reduction in ML build, or hype?

Type: research
Status: RESOLVED (2026-08-05) — **VERDICT: REJECT**. See [research/tabfm-assessment.md](../research/tabfm-assessment.md).
Blocked by: none

## Verdict (2026-08-05)

**REJECT** for all six analytical needs. Decisive: TabFM's regression head is a scalar MLP
(`MLP(d_model, [hidden], 1)`) — architecturally incapable of a predictive distribution — and its
shipped preprocessing z-scores the target and clips features at ±4σ, destroying the exact tail the
risk engine measures. TabPFN-3 kept the bar-distribution head TabFM dropped. Contamination is the
one pillar it genuinely passes (synthetic-SCM-only pretraining, no real tables) but that was never
the binding constraint. Weights are non-commercial/non-production licensed; there is no technical
report. Narrow surviving use — unpriced null baseline in the scoring harness — is dominated by
LightGBM/TabPFN-3 at ~1/40th the compute cost.

## Question

Google Research released **TabFM**, a zero-shot foundation model for tabular data
(https://research.google/blog/introducing-tabfm-a-zero-shot-foundation-model-for-tabular-data/).
Assess **skeptically** — do NOT assume it fits just because it was raised.

- What it actually is, what it does zero-shot, and its documented limits.
- Where it sits vs TabPFN and the prior tabular-foundation-model line; what is genuinely new.
- **Could it reduce ML model development we would otherwise have to do?** Our tabular needs:
  inferring evolution positions from evidence, elasticity estimation, calibration/scoring,
  anomaly/weak-signal detection, credibility-theory blending.
- Where it would be **actively wrong** for us: uncertainty quantification (we need calibrated
  distributions, not point predictions), explainability (we need evidence-graded claims), tiny-n and
  heavy-tailed regimes, causal vs correlational use.
- **Contamination risk** — a foundation model trained on public data used on famous public events.
- Licensing/availability/practicality.

Output: `research/tabfm-assessment.md`. Verdict must be explicit: adopt / adopt-narrowly / reject, with
what it replaces and what it cannot.
