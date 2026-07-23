# RESEARCH: cyber-risk quantification (FAIR and peers)

Type: research
Status: resolved
Blocked by: —

## Question

How do mature organisations turn technological/cyber risk into a defensible £ number? Surface the
facts the risk model (04) and balance-sheet (06) wait on:

- **FAIR** (Factor Analysis of Information Risk) — its model (threat event frequency × loss
  magnitude → loss exceedance curve / annualised loss expectancy). Enough to *implement a
  lightweight version*, not just cite it.
- **Proportionality** — how appetite/tolerance bands are set and how a control's strength is
  justified against a quantified risk (so Audit→Deny is a number, not a vibe).
- **Balance-sheet / insurance reality** — how cyber risk actually reaches financial statements,
  cyber-insurance underwriting inputs, and M&A diligence. What's genuinely done vs aspirational.
- **Residual risk maths** — coverage − accepted-risk, and how exemptions/waivers are priced.

Findings → write to `.scratch/talk-spec/research/07-risk-quantification.md`; link it back here.

## Answer

Full findings + a runnable reference implementation: [`../research/07-risk-quantification.md`](../research/07-risk-quantification.md).

- **FAIR taxonomy is implementable directly:** Risk = Loss Event Frequency × Loss Magnitude, where
  LEF = Threat Event Frequency × Vulnerability, TEF = Contact Frequency × Probability of Action, and
  Loss Magnitude = Primary Loss + (Secondary LEF × Secondary Loss Magnitude). Loss magnitude is built
  from six named loss forms (productivity, response, replacement, fines/judgements, competitive
  advantage, reputation) — forms 1–3 usually primary, 4–6 usually secondary.
- **You simulate, never multiply means.** Each leaf is a `(min, mode, max)` triple → **beta-PERT**
  (`α=1+λ(mode−lo)/(hi−lo)`, `β=1+λ(hi−mode)/(hi−lo)`, λ=4) → **Monte Carlo** (10k+ runs): per year
  sample event count, sum a magnitude per event. Outputs: **ALE** (mean), **VaR95** (95th pct),
  **loss-exceedance curve** (`P(loss>x)`). Canonical example LEF(2,4,9)/LM(£1k,4k,9k) → mean ≈ £17k
  but VaR95 ≈ £31k — the mean/tail gap is the whole reason to simulate.
- **Inputs come from calibrated experts** giving 90% confidence intervals (Hubbard); untrained
  experts are overconfident, and the "equivalent bet" test + calibration training fixes it. Wide
  honest ranges beat fake point estimates.
- **"Audit → Deny" becomes a number:** Deny raises Resistance Strength → Vulnerability→~0 → residual
  ALE≈0; Warn only aids detection (trims secondary loss, not primary LEF). The £ a control buys =
  `ALE_warn − ALE_deny`. Enforce when residual `ALE_warn` exceeds the tolerance band.
- **Appetite vs tolerance:** appetite is qualitative/board-level, tolerance is quantitative
  thresholds. Wire three bands — below appetite → Audit; appetite→tolerance → Warn+SLO; above
  tolerance → Deny. Where no direct risk measure exists, use control-adherence as a proxy.
- **Insurance is the strongest external validation:** underwriters gate coverage on MFA / EDR /
  immutable-tested-backups / IR plan / patch mgmt (conditions, not rating factors) and price them —
  MFA ≈15–25%, EDR ≈10–20%, backups ≈10–15%, overall ±20–40% at renewal. Carriers literally price the
  same controls the policy engine enforces.
- **Balance sheet / M&A:** SEC rules (8-K Item 1.05 + Reg S-K 106) force material-incident and
  governance disclosure — quantified ALE/VaR increasingly defends the materiality call. Cyber rarely
  sits as a booked forward liability (reaches accounts mostly as post-incident cost + premiums). In
  M&A, CRQ drives valuation/SPA reps/R&W-insurance scope; a live incident can cut value 15–30%.
- **Residual & waiver pricing:** `Residual = Inherent×(1−Control Effectiveness)`, or in money the
  residual *is* `ALE_deny`. Exemptions/waivers = consciously-accepted risk priced at the exempted
  set's `ALE_warn`; total residual = `ALE_deny·covered + ALE_warn·exempted`. Every waiver gets a £
  tag, an owner, and an expiry (time-boxed "ratchet down") — a priced accepted-risk line, not a
  loophole. The reference `fair.py` (numpy-only, ~40 lines, self-check passes) computes all of this,
  and because inputs are versioned triples in the repo, **the risk number is versioned with the
  policy**.
