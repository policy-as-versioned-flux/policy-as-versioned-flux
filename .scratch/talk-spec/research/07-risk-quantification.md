# Research: cyber-risk quantification (FAIR and peers)

Status: resolved · Ticket: `../issues/07-research-risk-quantification.md`

Purpose: give whoever builds the risk model (04) and the balance-sheet view (06) enough to
**implement a lightweight, defensible FAIR-style engine** — concrete formulas, worked numbers,
and a minimal reference implementation — plus the appetite / insurance / M&A / residual-risk
context so that "Audit → Deny" is a number, not a vibe.

TL;DR of the shape we want: a policy control's job is to **reduce Loss Event Frequency**
(a block removes a loss path; an audit/warn only detects it). Quantify the risk with and without
the control as an **annualised loss distribution**, read the residual off a **loss-exceedance
curve**, compare it to an **appetite band**. Enforce (Deny) when residual > tolerance; Warn when
residual sits in the tolerated band; the £ delta between the two is what the control "buys".
Exemptions/waivers are **consciously-accepted risk** priced at the annualised loss of the
exempted set.

---

## 1. The FAIR model — enough to implement

FAIR (Factor Analysis of Information Risk) is the open standard behind Open FAIR (The Open Group)
and the FAIR Institute. It defines **risk as "the probable frequency and probable magnitude of
future loss"** — a *distribution*, not a point estimate — and gives a taxonomy that decomposes
that into estimable leaf factors.
([FAIR Institute standard v3.0](https://www.fairinstitute.org/hubfs/Standards%20Artifacts/Factor%20Analysis%20of%20Information%20Risk%20(FAIR)%20Standard%20v3.0%20(January%202025).pdf),
[Wikipedia: FAIR](https://en.wikipedia.org/wiki/Factor_analysis_of_information_risk))

### 1.1 The taxonomy (top to leaves)

```
Risk
 └─ Loss Event Frequency (LEF)              events / year
 │   ├─ Threat Event Frequency (TEF)        contacts that could cause loss / year
 │   │   ├─ Contact Frequency (CF)          how often the threat touches the asset
 │   │   └─ Probability of Action (PoA)     P(threat acts, given contact)
 │   └─ Vulnerability / Susceptibility (V)  P(threat event becomes a loss event)  ∈ [0,1]
 │       ├─ Threat Capability (TCap)        skill/resources of the threat  (percentile)
 │       └─ Resistance / Control Strength   how hard the control makes the attack (percentile)
 └─ Loss Magnitude (LM)                     £ per loss event
     ├─ Primary Loss (PL)                   falls directly on the org
     └─ Secondary Risk (SR)
         ├─ Secondary Loss Event Frequency (SLEF)  P(stakeholders react | primary loss)
         └─ Secondary Loss Magnitude (SLM)         £ from that reaction (fines, churn, ...)
```

### 1.2 The core equations

- **Risk = Loss Event Frequency × Loss Magnitude** (as *distributions*, combined by simulation —
  see §2, not a scalar multiply).
- **LEF = TEF × Vulnerability**
- **TEF = Contact Frequency × Probability of Action**
- **Vulnerability = P(TCap > Resistance Strength)** — i.e. the probability the threat's capability
  exceeds the control's resistance. Practically estimated directly as a 0–1 susceptibility.
- **Loss Magnitude = Primary Loss + Secondary Loss** where
  **Secondary Loss (expected) = SLEF × SLM**.

([TechTarget: using FAIR](https://www.techtarget.com/searchsecurity/tip/Using-the-FAIR-model-to-quantify-cyber-risk),
[CyberSaint pocket guide](https://www.cybersaint.io/blog/a-pocket-guide-to-factor-analysis-of-information-risk),
[Safe Security: FAIR in 90s](https://safe.security/resources/blog/fair-model-explained-90-seconds/))

### 1.3 The six forms of loss (how you build a Loss-Magnitude estimate)

Every £ figure in PL/SLM is one of these — enumerate them so magnitude estimates are grounded,
not plucked:

1. **Productivity** — lost capacity to deliver (downtime, halted transactions).
2. **Response** — money spent reacting (IR, forensics, overtime, notification).
3. **Replacement** — repair/replace the asset (rebuild, restore, new hardware).
4. **Fines & judgements** — regulatory penalties, legal, settlements.
5. **Competitive advantage** — value of lost IP / secrets / lead.
6. **Reputation** — lost future sales / higher cost of capital from damaged image.

Rule of thumb the standard uses: forms 1–3 are usually **Primary Loss** (land immediately on you);
4–6 are usually **Secondary Loss** (materialise only if stakeholders — regulators, customers,
markets — react). ([Wikipedia: FAIR](https://en.wikipedia.org/wiki/Factor_analysis_of_information_risk),
[CIS: FAIR](https://www.cisecurity.org/insights/blog/fair-a-framework-for-revolutionizing-your-risk-analysis))

### 1.4 Getting the input numbers — calibrated estimation

You will not have clean data for most leaves. FAIR practice (per Hubbard & Seiersen, *How to
Measure Anything in Cybersecurity Risk*) is to use **calibrated experts giving 90 % confidence
intervals** (a min and a max they're 90 % sure the true value falls between), plus a most-likely
value. Key facts for the builder:

- A **calibrated** 90 % interval is right ~90 % of the time; untrained experts are systematically
  **overconfident** (intervals too narrow). Calibration training + the **"equivalent bet"** test
  (would you rather win £X on your range being right, or spin a 90/10 wheel?) measurably fixes this.
- "You have more data than you think and need less than you think" — a wide honest interval beats a
  fake point estimate. Each input is therefore **(min, mode, max)** feeding a distribution.

([FAIR Institute: calibrated estimation / Hubbard](https://www.fairinstitute.org/blog/cyber-risk-calibrated-estimation-learn-from-douglas-hubbard-faircon22),
[Hubbard Decision Research: role of calibration](https://hubbardresearch.com/the-role-of-calibration-in-risk-analysis/))

---

## 2. From inputs to money — the simulation engine

You **cannot** just multiply the means: risk is skewed and fat-tailed, and the board cares about
the tail, not the average. FAIR tools run a **Monte Carlo** over **beta-PERT** distributions.

### 2.1 beta-PERT (turns min/mode/max into a sampleable distribution)

PERT is a Beta distribution rescaled to `[min, max]`, weighted toward the mode. With shape λ
(default **4** = standard confidence; raise for more certainty, lower for less):

```
α = 1 + λ·(mode − min)/(max − min)
β = 1 + λ·(max − mode)/(max − min)
sample = min + Beta(α, β)·(max − min)
```

This is the distribution FAIR engines (RiskLens, FAIR-U, open tools) use for every leaf factor.
([FAIR-U loss-exceedance](https://www.fairinstitute.org/blog/announcing-loss-exceedance-charts-in-the-fair-u-training-app),
[Kindly Ops FAIR example](https://www.kindlyops.com/knowledge-base/fair-example/))

### 2.2 The compound loop (why it's not one multiply)

Per simulated year: sample **how many** loss events happen, then sample **a magnitude for each**
and sum them. Over N years you get a distribution of annual loss.

```
for i in 1..N:                       # N = 10,000+ iterations
    f = round(PERT(lef_min, lef_mode, lef_max))     # events this year
    year_loss = sum( PERT(lm_min, lm_mode, lm_max) for 1..f )
    ALE[i] = year_loss
```

- **Annualised Loss Expectancy (ALE)** = `mean(ALE)` — the "expected" annual cost.
- **Value at Risk (e.g. VaR95)** = `percentile(ALE, 95)` — the bad-but-plausible year.
- **Loss-Exceedance Curve (LEC)**: for each £ threshold x, plot `P(annual loss > x)`
  (i.e. `mean(ALE > x)`). This is the money chart for the board: "there's a 10 % chance we lose
  more than £X in a year." ([RiskLens: reading LECs](https://www.risklens.com/resource-center/blog/reading-loss-exceedance-curves),
  [Kindly Ops](https://www.kindlyops.com/knowledge-base/fair-example/))

### 2.3 Worked example (canonical, from the Kindly Ops reference)

Inputs (direct LEF/LM for brevity): LEF = (min 2, mode 4, max 9) events/yr;
LM = (min £1k, mode £4k, max £9k). 10,000 iterations, PERT λ=4:

| Metric | Value |
|---|---|
| Mean ALE | ≈ £17,293 |
| 95th pct (VaR95) | ≈ £30,648 |
| Max simulated year | ≈ £42,588 |

Note the mean (£17k) is **far below** the tail (£31k+): that gap is exactly why point estimates
mislead and why we simulate. ([Kindly Ops FAIR example](https://www.kindlyops.com/knowledge-base/fair-example/))

---

## 3. Proportionality — making "Audit → Deny" a number

This is the crux for the talk: a Kubernetes admission policy (Kyverno/Gatekeeper/VAP) can run in
**Audit/Warn** (observe + report) or **Enforce/Deny** (block admission). FAIR lets you price that
choice.

### 3.1 What each control mode does to the taxonomy

- **Deny / Enforce** raises **Resistance Strength** so the loss path is (near-)closed →
  **Vulnerability → ~0** for that vector → **LEF collapses** → residual ALE ≈ 0 for that scenario.
- **Audit / Warn** does *not* touch primary LEF (the bad config still ships); it improves
  **detection/response**, which mainly trims **Secondary Loss** and time-to-remediate. Treat it as
  a modest cut to LM and/or a small cut to PoA, **not** to Vulnerability.

So the model computes two ALE distributions — `ALE_warn` and `ALE_deny` — and the **risk the
control buys** is `ALE_warn − ALE_deny` (compare whole curves, headline the means/VaR95).

### 3.2 Appetite & tolerance bands (the decision rule)

Standard practice separates **risk appetite** (qualitative, board-level "how much risk we'll take
for our goals") from **risk tolerance** (quantitative, measurable thresholds). Operationalise as
**two numeric tiers**:

- **Threshold** — cross it and you escalate / reallocate (a *warning* band).
- **Limit** — cross it and you must act now, up to halting the activity (a *hard* band).

Map straight onto three bands (this is exactly how CRQ tools wire it):

| Residual ALE vs bands | State | Control decision |
|---|---|---|
| below **appetite** | OK | Audit only (cheap visibility) |
| between appetite and **tolerance** | Warn | Warn + owner + time-boxed fix SLO |
| above **tolerance** | Breach | **Deny/Enforce** |

Concrete tolerance-statement style (from Venables' practical approach): *"systems 99.9 % available,
isolated dips to 99.5 % tolerated"*, *"conformance to vuln-resolution SLOs by severity"*,
*"number of identities whose privileges exceed a defined blast radius"*. Where you lack a direct
risk measure, **measure control adherence as a proxy** for it.
([Venables: appetite & tolerance](https://www.philvenables.com/post/risk-appetite-and-risk-tolerance-a-practical-approach),
[Kovrr: operationalising cyber risk appetite](https://www.kovrr.com/blog-post/quantifying-cyber-risk-appetite-a-framework-for-decision-making),
[Safe Security: risk thresholds](https://safe.security/resources/blog/cybersecurity-risk-thresholds/))

The proportionality argument then writes itself: **Deny is justified iff `ALE_warn` (the residual
if we only warn) exceeds the tolerance band**, *and* the risk it buys (`ALE_warn − ALE_deny`)
exceeds the cost/friction of enforcing. That's the number behind the vibe.

---

## 4. Balance-sheet / insurance / M&A reality (done vs aspirational)

### 4.1 Financial statements & disclosure — mostly narrative, quantification rising
- **SEC rules (Reg S-K Item 106 + 8-K Item 1.05, in force since Dec 2023)** require disclosing
  **material** incidents (within 4 business days of a materiality determination) and describing risk
  **management, strategy and governance** annually. Materiality is the judgement gate — and a
  quantified ALE/VaR is increasingly how firms *defend* that judgement.
- **Genuinely done:** incident-driven 8-K disclosures; qualitative risk-factor narrative; some large
  firms now cite CRQ figures to boards. **Still aspirational:** cyber risk as a standing, audited
  line in the financial statements. It reaches the accounts mostly as **incident costs after the
  fact** and **insurance premiums**, not as a forward-looking booked liability.
- SEC expectations now **cascade** into supply-chain questionnaires, lender covenants, insurance,
  and M&A. ([SEC cyber disclosure 2026](https://blog.cyberadvisors.com/sec-cyber-disclosure-rules-what-private-mid-market-companies-should-prepare-for-in-2026))

### 4.2 Cyber-insurance underwriting — evidence-based, control-gated (very real)
Underwriting has shifted "from trust to verification" — a technical audit, not a form. Model inputs:
technical controls, incident history, network architecture, asset inventory, third-party risk.

- **Conditions of coverage** (no MFA/EDR/backups → often no policy at all): enforced **MFA**,
  **EDR/MDR on every endpoint**, **immutable + tested backups**, a **written IR plan with a recent
  tabletop**, **documented patch management**, security-awareness training.
- **Premium levers** (real, quoted ranges): MFA ≈ **15–25 %**, EDR ≈ **10–20 %**, tested offline
  backups ≈ **10–15 %**; overall documented controls swing premiums **20–40 %** at renewal.

This is the cleanest external validation of proportionate control strength: **carriers literally
price the same controls the policy engine enforces.** A demo can say "Deny on this policy is worth
~X % of premium." ([hyperexponential cyber pricing](https://www.hyperexponential.com/lob-pricing-factors/cyber),
[Consilien 2026 requirements](https://consilien.com/news/cyber-insurance-requirements-2026-checklist),
[EmergeIT: underwriting as technical audit](https://emergeits.com/blog/cyber-insurance-requirements-underwriting-has-quietly-become-a-technical-audit/))

### 4.3 M&A due diligence — quantified into deal terms (real, growing)
Cyber posture moves **valuation, timelines and price**. CRQ shows up as: valuation adjustment, SPA
representations, **reps-and-warranties (R&W) insurance scope** (underwriters price exclusions hard
when diligence is thin), and post-close **remediation budget**. A live incident at the target during
close can cut valuation **15–30 %** or break the deal.
([WTW: cyber in M&A](https://www.wtwco.com/en-us/insights/2024/08/cybersecurity-considerations-in-merger-and-acquisitions-transactions-an-in-depth-analysis),
[CrossCountry: cyber in M&A diligence](https://www.crosscountry-consulting.com/insights/blog/assessing-cybersecurity-during-ma-due-diligence/))

---

## 5. Residual-risk maths & pricing accepted risk (exemptions/waivers)

### 5.1 Two compatible formulations

**GRC/scorecard form** (simple, ordinal-friendly):
```
Residual = Inherent × (1 − Control Effectiveness)
Control Effectiveness % = (Inherent − Residual) / Inherent × 100
```

**FAIR/money form** (what we want): residual risk **is** the ALE computed with the control in
place. `Residual ALE = ALE_deny`; risk reduced = `ALE_warn − ALE_deny`; effectiveness =
`1 − ALE_deny/ALE_warn`.
([FinancialCrimeAcademy: risk formula](https://financialcrimeacademy.org/risk-formula-definition/),
[RiskWatch: inherent vs residual](https://www.riskwatch.com/inherent-vs-residual-risk/))

### 5.2 Coverage − consciously-accepted risk

An **exemption/waiver** is a policy rule NOT enforced on some workloads → those workloads keep
their un-mitigated LEF → they carry the full-strength ALE. So:

```
Enforced (covered) set      → residual ALE ≈ ALE_deny  (small)
Exempted (accepted) set     → residual ALE  = ALE_warn  (full, consciously accepted)

Total residual ALE = ALE_deny·(covered workloads) + ALE_warn·(exempted workloads)
Coverage = covered / (covered + exempted)          # by workload, or better by £-at-risk
Consciously-accepted risk = Σ ALE_warn over exempted set   ← the price of the waivers
```

### 5.3 Pricing an accepted risk (waiver)

A risk-acceptance decision should carry a **number and an owner and an expiry** (accept / treat /
transfer / avoid; named owner; deadline; target residual; review date — the standard risk-register
fields). Price the waiver as:

- **Annualised £ carried** = the exempted set's `ALE_warn` (its mean, and quote VaR95 for the tail).
- Sanity-check against alternatives: **cost to remediate** (make it comply) vs **cost to transfer**
  (marginal insurance premium for that exposure) vs **cost to accept** (the ALE). Cheapest wins;
  the waiver is defensible only while `accept < remediate` and residual stays inside appetite.
- Make waivers **time-boxed** so accepted risk can't silently compound (the "ratchet down"
  pattern — cap and reduce the exempted population over time).
([Venables](https://www.philvenables.com/post/risk-appetite-and-risk-tolerance-a-practical-approach),
[Empowered: inherent vs residual](https://empoweredsystems.com/blog/understanding-inherent-and-residual-risk-in-enterprise-risk-management/))

This is the honest version of the talk's punchline: **an exemption isn't a loophole, it's a priced,
owned, expiring line of accepted £ risk** — and versioning the policy versions that number too.

---

## 6. How we'd implement a minimal version

Ladder check: don't build a CRQ platform. A ~40-line numpy Monte Carlo over PERT inputs gives ALE,
VaR95 and a loss-exceedance curve — everything §2–§5 needs. Inputs are `(min, mode, max)` triples a
calibrated human fills in per scenario; the policy's mode (`warn`/`deny`) selects which triple set.

```python
# fair.py  — lightweight FAIR engine. Deps: numpy only.
import numpy as np

def pert(lo, mode, hi, n, rng, lam=4.0):
    """Sample n values from a beta-PERT on [lo,hi] peaked at mode (lam=4 default)."""
    if hi <= lo:                      # degenerate / point estimate
        return np.full(n, lo)
    a = 1 + lam * (mode - lo) / (hi - lo)
    b = 1 + lam * (hi - mode) / (hi - lo)
    return lo + rng.beta(a, b, n) * (hi - lo)

def simulate(lef, lm, n=10_000, seed=42):
    """lef, lm = (min, mode, max). Returns array of annual loss (one per simulated year)."""
    rng = np.random.default_rng(seed)
    freqs = np.rint(pert(*lef, n, rng)).astype(int)          # events per year
    tot = np.zeros(n)
    for i, f in enumerate(freqs):
        if f > 0:
            tot[i] = pert(*lm, f, rng).sum()                 # sum a magnitude per event
    return tot

def summary(ale):
    return dict(mean=ale.mean(),
                var95=np.percentile(ale, 95),
                p_gt_0=float((ale > 0).mean()))

def lec(ale, xs):                    # loss-exceedance curve: P(loss > x) for each x
    return {x: float((ale > x).mean()) for x in xs}

# --- proportionality / residual / waiver pricing -------------------------------
def control_value(scenario_warn, scenario_deny, n=10_000):
    """£ a Deny buys vs Warn, and residual under each. Each scenario = (lef, lm)."""
    warn = simulate(*scenario_warn, n)
    deny = simulate(*scenario_deny, n)
    return dict(residual_warn=warn.mean(), residual_deny=deny.mean(),
                risk_bought=warn.mean() - deny.mean(),
                effectiveness=1 - deny.mean() / max(warn.mean(), 1e-9))

def portfolio_residual(ale_deny, ale_warn, n_covered, n_exempt):
    """Total residual + the priced accepted risk from waivers (per-workload mean ALEs)."""
    accepted = ale_warn * n_exempt                    # £ consciously carried
    return dict(total_residual=ale_deny * n_covered + accepted,
                accepted_risk=accepted,
                coverage=n_covered / (n_covered + n_exempt))

# --- self-check (ponytail: the one runnable check) -----------------------------
if __name__ == "__main__":
    # Canonical Kindly Ops numbers: LEF(2,4,9), LM(1k,4k,9k) -> mean ~17k, VaR95 ~31k
    ale = simulate((2, 4, 9), (1_000, 4_000, 9_000))
    s = summary(ale)
    assert 14_000 < s["mean"] < 21_000, s        # mean ALE in expected band
    assert 26_000 < s["var95"] < 36_000, s       # tail well above the mean
    assert s["var95"] > s["mean"]                 # skew: tail > mean, always
    # Deny (near-zero residual) must buy positive risk vs Warn
    cv = control_value(((2, 4, 9), (1_000, 4_000, 9_000)),   # warn: full exposure
                       ((0, 0, 1), (1_000, 4_000, 9_000)))   # deny: LEF collapsed
    assert cv["risk_bought"] > 0 and cv["effectiveness"] > 0.8, cv
    print("ok", s, cv)
```

**What this gives the demo, directly:**
- Per policy scenario: **mean ALE, VaR95, loss-exceedance curve** (the board chart).
- **`control_value()`**: the £ that flipping Audit→Deny buys, plus residual under each — the
  proportionality number.
- **`portfolio_residual()`**: coverage, total residual, and the **priced accepted risk** from
  exemptions — feeds the balance-sheet view (06) and lets a waiver show its £ tag.
- Because inputs are just versioned `(min,mode,max)` triples in the repo, **the risk number is
  itself versioned alongside the policy** — which is the whole thesis of the talk.

**Deliberately skipped (add only if asked):** separate TEF×Vulnerability decomposition (fold into
LEF triples until a scenario needs to reason about control-strength-vs-threat-capability
explicitly); secondary-loss branch as its own simulation (fold into the LM triple); correlation
between scenarios; a distribution-fitting UI. `ponytail:` PERT λ fixed at 4 — expose per-scenario
only if an estimator needs to widen/narrow confidence.

---

## Sources
- [FAIR Institute — FAIR Standard v3.0 (Jan 2025, PDF)](https://www.fairinstitute.org/hubfs/Standards%20Artifacts/Factor%20Analysis%20of%20Information%20Risk%20(FAIR)%20Standard%20v3.0%20(January%202025).pdf)
- [Wikipedia — Factor Analysis of Information Risk](https://en.wikipedia.org/wiki/Factor_analysis_of_information_risk)
- [TechTarget — Using the FAIR model to quantify cyber-risk](https://www.techtarget.com/searchsecurity/tip/Using-the-FAIR-model-to-quantify-cyber-risk)
- [CyberSaint — A Pocket Guide to FAIR](https://www.cybersaint.io/blog/a-pocket-guide-to-factor-analysis-of-information-risk)
- [Safe Security — The FAIR Model in 90 Seconds](https://safe.security/resources/blog/fair-model-explained-90-seconds/)
- [CIS — FAIR: A Framework for Revolutionizing Your Risk Analysis](https://www.cisecurity.org/insights/blog/fair-a-framework-for-revolutionizing-your-risk-analysis)
- [Kindly Ops — FAIR worked example (PERT + Monte Carlo + LEC)](https://www.kindlyops.com/knowledge-base/fair-example/)
- [FAIR Institute — Loss Exceedance Charts in FAIR-U](https://www.fairinstitute.org/blog/announcing-loss-exceedance-charts-in-the-fair-u-training-app)
- [RiskLens — How to Read Loss Exceedance Curves](https://www.risklens.com/resource-center/blog/reading-loss-exceedance-curves)
- [FAIR Institute — Calibrated Estimation (Hubbard)](https://www.fairinstitute.org/blog/cyber-risk-calibrated-estimation-learn-from-douglas-hubbard-faircon22)
- [Hubbard Decision Research — The Role of Calibration in Risk Analysis](https://hubbardresearch.com/the-role-of-calibration-in-risk-analysis/)
- [Phil Venables — Risk Appetite and Risk Tolerance: A Practical Approach](https://www.philvenables.com/post/risk-appetite-and-risk-tolerance-a-practical-approach)
- [Kovrr — Quantifying & Operationalising Cyber Risk Appetite](https://www.kovrr.com/blog-post/quantifying-cyber-risk-appetite-a-framework-for-decision-making)
- [Safe Security — How to Set Cybersecurity Risk Thresholds](https://safe.security/resources/blog/cybersecurity-risk-thresholds/)
- [hyperexponential — Cyber Insurance Pricing Guide](https://www.hyperexponential.com/lob-pricing-factors/cyber)
- [Consilien — Cyber Insurance Requirements: 2026 Checklist](https://consilien.com/news/cyber-insurance-requirements-2026-checklist)
- [EmergeIT — Cyber Insurance Underwriting as a Technical Audit](https://emergeits.com/blog/cyber-insurance-requirements-underwriting-has-quietly-become-a-technical-audit/)
- [Cyber Advisors — SEC Cyber Disclosure Rules 2026](https://blog.cyberadvisors.com/sec-cyber-disclosure-rules-what-private-mid-market-companies-should-prepare-for-in-2026)
- [WTW — Cybersecurity Considerations in M&A](https://www.wtwco.com/en-us/insights/2024/08/cybersecurity-considerations-in-merger-and-acquisitions-transactions-an-in-depth-analysis)
- [CrossCountry — Assessing Cybersecurity During M&A Due Diligence](https://www.crosscountry-consulting.com/insights/blog/assessing-cybersecurity-during-ma-due-diligence/)
- [FinancialCrimeAcademy — Risk Formula: Inherent, Residual, Control Effectiveness](https://financialcrimeacademy.org/risk-formula-definition/)
- [RiskWatch — Inherent vs Residual Risk](https://www.riskwatch.com/inherent-vs-residual-risk/)
- [Empowered — Understanding Inherent and Residual Risk](https://empoweredsystems.com/blog/understanding-inherent-and-residual-risk-in-enterprise-risk-management/)
