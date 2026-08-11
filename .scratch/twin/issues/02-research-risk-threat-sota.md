# RESEARCH: state of the art — quantified risk & threat modelling

Type: research
Status: resolved
Blocked by: none

## Question

How is risk *actually* quantified rigorously today — so we build on real methodology, not the toy
prior? Investigate against primary/high-trust sources and write a cited briefing:

- **FAIR** done properly: real calibration (calibrated estimation, credibility theory / Bühlmann),
  where loss-event-frequency and loss-magnitude numbers *legitimately* come from, back-testing.
- **Threat modelling**: STRIDE, attack trees, kill chains, **MITRE ATT&CK**, threat-intel feeds —
  how they ground the frequencies risk maths needs.
- **Insider-risk quantification** (link to ticket 05), **cyber-actuarial / insurance pricing**,
  Monte-Carlo practice, aggregation, tail/VaR/TVaR, economic capital.
- What is **real vs snake-oil** in "cyber risk quantification".

Output: `research/risk-threat-sota.md` — a cited briefing on rigorous risk+threat quantification we
can actually build the £ engine on, with a verdict on which methods are load-bearing.

## Answer (2026-08-04) — resolved

Keep the **FAIR skeleton** (LEF × LM → PERT leaves → Monte-Carlo → loss-exceedance curve; Open FAIR
O-RT/O-RA, not a vendor black box). Add the four things the toy lacked:
1. **Calibrated estimation (Hubbard)** — fixes the overconfident hand-asserted triple directly.
2. **Empirical anchoring** — Cyentia IRIS, Verizon DBIR, NetDiligence; **heavy-tailed severity**
   (lognormal body + Pareto/GPD tail — the tail is where the money is).
3. **Credibility theory (Bühlmann–Straub)** — optimally blend sparse own-data with an industry prior;
   usable *now*, highest-leverage + most under-used.
4. **Back-testing / calibration** so the model can be shown wrong.

Threat modelling **grounds the frequencies**: STRIDE / attack-trees enumerate scenarios; MITRE ATT&CK
+ DBIR shape Threat Event Frequency and map controls onto the resistance term — but ATT&CK gives
*relative* prevalence, so the *absolute* anchor stays with loss data + calibrated judgement. Aggregate
with **copulas** (explicit dependence); report **TVaR / Expected Shortfall**, not VaR (incoherent on
cyber's heavy tails). **Reject outright:** risk matrices/heat-maps, arithmetic on ordinal/CVSS scores
(Cox), black-box single-number CRQ, any "validated" claim with no calibration curves. Honest gap: too
few per-firm tail events for classical back-testing → lean on estimator calibration + out-of-sample
pooled fit + model-risk sensitivity. Full cited briefing: `research/risk-threat-sota.md`.
