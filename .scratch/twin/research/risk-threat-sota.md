# State of the Art: Rigorous Quantified Risk & Threat Modelling

**Purpose.** Ground a real £-denominated risk engine in defensible methodology. The prior
attempt used hand-asserted FAIR triples with no calibration and no back-testing — this
briefing sets out what "done properly" looks like, sourced to primary/high-trust references,
and ends with a blunt verdict on what is load-bearing versus snake-oil.

**Bottom line up front.** The maths of Factor Analysis of Information Risk (FAIR) —
decompose risk into frequency × magnitude, express every uncertain input as a probability
distribution, and Monte-Carlo the aggregate — is sound and is the right skeleton. What was
missing (and what everyone's prior toy gets wrong) is the *inputs*: calibrated estimation to
stop overconfident three-point guesses, empirical loss/frequency data to anchor the numbers,
credibility-weighting to blend sparse own-data with portfolio priors, heavy-tailed severity
models so the tail isn't understated, and back-testing so the model can actually be wrong.
FAIR without those is astrology with a Monte-Carlo engine bolted on.

---

## 1. FAIR done properly — the model, and the four things that make it real

### 1.1 The taxonomy is sound; that is the part to keep

FAIR (Jack Jones, 2005; standardised by The Open Group as the Open FAIR Body of Knowledge —
the O-RT Risk Taxonomy and O-RA Risk Analysis standards) defines risk as *"the probable
frequency and probable magnitude of future loss"* and decomposes it into a factor tree:

- **Risk = Loss Event Frequency (LEF) × Loss Magnitude (LM)**
- **LEF = Threat Event Frequency (TEF) × Vulnerability**, where TEF = Contact Frequency ×
  Probability of Action, and Vulnerability = f(Threat Capability, Resistance/Control Strength)
- **LM = Primary Loss + Secondary Loss** (secondary = fines, response, reputation, incident
  handling — the part naïve models omit)

Each leaf is a *distribution*, not a point: a three-point (min / most-likely / max) estimate
sampled through a modified-beta **PERT** distribution, and the whole tree is resolved by
**Monte-Carlo** simulation into a loss-exceedance curve, not a single number.

- FAIR Standard v3.0 (Jan 2025), The Open Group / FAIR Institute —
  https://www.fairinstitute.org/hubfs/Standards%20Artifacts/Factor%20Analysis%20of%20Information%20Risk%20(FAIR)%20Standard%20v3.0%20(January%202025).pdf
- FAIR terminology (Risk, TEF, Vulnerability) — https://www.fairinstitute.org/blog/fair-terminology-101-risk-threat-event-frequency-and-vulnerability
- FAIR loss magnitude (primary vs secondary) — https://www.fairinstitute.org/blog/fair-risk-basics-what-is-loss-magnitude

**Verdict on the skeleton:** keep it. Frequency × magnitude, distributions not points, PERT
inputs, Monte-Carlo aggregation, loss-exceedance output. This is the correct structure and is
an open standard, not a vendor's black box.

### 1.2 Calibrated estimation (Hubbard) — the input discipline the toy lacked

The failure mode of the prior attempt is *uncalibrated* three-point estimates. Hubbard &
Seiersen (*How to Measure Anything in Cybersecurity Risk*, Wiley, 2nd ed. 2023) show why this
matters: unaided experts are systematically **overconfident** — stated 90% confidence
intervals contain the true value well under half the time. **Calibration training** (batteries
of trivia + range questions with feedback, equivalent-bet tests) demonstrably fixes this:
roughly 70% of people reach near-perfect calibration after ~half a day, and the skill carries
over to real estimates. A calibrated 90% interval actually contains the truth ~90% of the time.

- Hubbard & Seiersen, *How to Measure Anything in Cybersecurity Risk* (Wiley) — https://onlinelibrary.wiley.com/doi/book/10.1002/9781119892335
- Hubbard Decision Research, "Calibrated Probability Assessments: An Introduction" (PDF) — http://www.hubbardresearch.com/wp-content/uploads/2019/06/Introduction-to-Calibrating-Probability-Assessments-Hubbard-Decision-Research.pdf
- Calibration training method — https://hubbardresearch.com/calibration-training/

**Build implication:** any human-supplied input (min/likely/max) must come from a calibrated
estimator, and we should record who estimated it and their calibration score. An uncalibrated
PERT triple is the exact "hand-asserted FAIR triple" failure we are replacing.

### 1.3 Where LEF and LM numbers *legitimately* come from

In priority order — never invent a number if a real one exists:

1. **Your own incident/loss history** — the ground truth, but almost always too sparse for the
   tail (this is precisely why credibility theory exists, §1.4).
2. **Industry empirical datasets** for frequency and severity:
   - **Cyentia IRIS** — longest-running loss study (15+ yrs of events); publishes frequency and
     severity by industry/revenue band; the reference source for lognormal-with-heavy-tail loss
     fitting. https://www.cyentia.com/iris/ ; methodology: https://www.cyentia.com/risk-data/
   - **Verizon DBIR** — tens of thousands of incidents/breaches; grounds TEF and initial-access
     patterns (which ATT&CK techniques actually occur, and how often). https://www.verizon.com/business/resources/reports/dbir/
   - **NetDiligence Cyber Claims Study** — insurer claims severity by cause and firm size.
3. **Threat intelligence** to shape TEF for a specific actor/technique (§2).
4. **Calibrated expert estimate** — the *fallback*, used only where 1–3 give nothing, and
   flagged as such.

Empirically, cyber **severity is heavy-tailed**: ~85% of events cause <$2M loss while a tiny
number exceed $1B; a lognormal body with a **Pareto/GPD tail** fits far better than lognormal
alone (whose tail decays too fast). Getting the tail model wrong is the single biggest source
of premium/economic-capital mispricing.

- "The nature of losses from cyber-related events" (*J. Cybersecurity*, OUP, 2023) — https://academic.oup.com/cybersecurity/article/9/1/tyac016/7000422
- "Heavy-tailed distribution of cyber-risks" — https://arxiv.org/pdf/0803.2256
- "The changing landscape of cyber risk: loss severity and tail dynamics" (*Insurance: Math & Econ*, 2025) — https://www.sciencedirect.com/science/article/pii/S0167668725001428
- "Cyber loss model risk translates to premium mispricing" — https://arxiv.org/pdf/2202.10588

### 1.4 Credibility theory / Bühlmann — blending sparse own-data with a prior

The core estimation problem is that your organisation has too few loss events to estimate its
own frequency/severity, but the industry portfolio is only partly relevant to you.
**Bühlmann credibility** (Hans Bühlmann, 1967) is the rigorous actuarial answer: the estimate
is a credibility-weighted blend

> estimate = Z × (your own experience) + (1 − Z) × (portfolio/industry mean)

where the credibility factor **Z = n / (n + k)** grows with your volume of experience *n*, and
*k* is set from the ratio of within-risk to between-risk variance. Bühlmann and
Bühlmann–Straub estimators are the **best linear Bayes** predictors (they minimise Bayes risk
in the linear class) — i.e. this is not a heuristic, it is optimal least-squares prediction.
Bühlmann–Straub extends it to Poisson/negative-binomial claim *counts*, which is exactly the
LEF (frequency) case.

- *Loss Data Analytics*, Ch. 9 "Experience Rating Using Credibility Theory" (open text) — https://openacttexts.github.io/Loss-Data-Analytics/ChapCredibility.html
- Bühlmann model overview — https://en.wikipedia.org/wiki/B%C3%BChlmann_model
- Credibility for claim frequency (Poisson/NB extension) — https://onlinelibrary.wiley.com/doi/10.1155/2018/6250686

**Build implication:** this is the mechanism that makes "our own data" usable *now* rather than
after a decade of breaches. Start every LEF/LM prior from the industry distribution (§1.3) and
credibility-weight in the organisation's own signal as it accrues. This is the single most
under-used rigorous technique in cyber CRQ.

### 1.5 Back-testing / validation — without this it isn't science

A model you cannot check is a belief. Validation means:

- **Calibration back-testing of the forecasters** — track whether events in the "90% interval"
  land there ~90% of the time (Brier scores, calibration curves), per Hubbard §1.2.
- **Distributional back-testing of outcomes** — treat the loss-exceedance curve as a
  probabilistic forecast and score realised losses against it (VaR/TVaR breach counts vs
  expected, PIT histograms), exactly as insurers back-test capital models.
- **Model risk** — different tail fits give materially different premiums; the divergence is
  itself a measurable quantity to report, not hide (the "model risk" paper above).

Honest limitation: cyber has too few tail events per firm for classical back-testing power, so
validation leans on (a) calibration of estimators, (b) out-of-sample fit against pooled
industry loss data, and (c) sensitivity/model-risk reporting. Any vendor claiming a
"validated" single number without showing these is overselling.

---

## 2. Threat modelling that GROUNDS the frequencies

Risk maths needs a *frequency* (TEF/LEF). Threat modelling is where that frequency stops being
a guess. The frameworks are complementary, not competing:

- **STRIDE** (Microsoft) — asset/design-centric enumeration (Spoofing, Tampering, Repudiation,
  Info-disclosure, DoS, Elevation). Answers *"what could go wrong here"* → the scenario set
  that each FAIR analysis quantifies. https://owasp.org/www-community/Threat_Modeling_Process
- **Attack trees** (Schneier) — decompose a goal into AND/OR sub-goals; each leaf can carry a
  probability/cost, so the tree composes into a scenario likelihood — a natural feed into TEF.
- **Cyber Kill Chain** (Lockheed Martin, 2011) — 7 linear stages (Recon → Weaponise → Deliver →
  Exploit → Install → C2 → Actions). Good for control-coverage reasoning ("break the chain").
  https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html
- **MITRE ATT&CK** — the empirical backbone. A curated matrix of real-world adversary tactics &
  techniques (TTPs) observed in the wild; the modern grounding for *which* techniques a given
  actor uses and how prevalent they are. https://attack.mitre.org/ ;
  Center for Threat-Informed Defense, "Threat Modeling with ATT&CK" — https://ctid.mitre.org/projects/threat-modeling-with-attack/

**How they feed LEF (the actual mechanism):**

1. STRIDE/attack-trees enumerate the loss *scenarios* (the unit a FAIR analysis prices).
2. ATT&CK + threat intel supply **empirical technique prevalence** → informs **Threat Event
   Frequency** and, via technique difficulty vs your control coverage, **Vulnerability
   (Resistance Strength)**.
3. DBIR-class datasets give the base-rate frequency of the *initial-access* techniques those
   scenarios start from → anchors TEF numerically.
4. Control coverage mapped onto ATT&CK (which techniques you detect/block) directly sets the
   Resistance-Strength distribution in the FAIR Vulnerability term.

Current research is explicitly hybrid: STRIDE for enumeration + ATT&CK for adversary behaviour
+ empirical technique frequency for quantitative prioritisation (e.g. "strideSEA"-style
pipelines; ATT&CK-driven quantitative risk scoring).

- Hybrid STRIDE+ATT&CK quantitative modelling — https://www.emergentmind.com/topics/structured-threat-and-attack-modelling
- ATT&CK-driven quantitative risk scoring (edge/IoT) — https://www.sciencedirect.com/org/science/article/pii/S1526149225003881
- Kill Chain vs ATT&CK (use together) — https://www.infosecinstitute.com/resources/mitre-attck/how-to-use-the-mitre-attck-framework-and-the-lockheed-martin-cyber-kill-chain-together/

**Caveat (don't over-claim):** ATT&CK gives *relative* technique prevalence and coverage, not a
calibrated absolute annual probability out of the box. It shapes and bounds TEF; it does not
by itself hand you a frequency. The absolute anchor still comes from loss/incident datasets
(§1.3) plus calibrated judgement, credibility-blended.

**Insider risk (ties to ticket 05):** insider scenarios are a distinct STRIDE/attack-tree
branch with their own base rates. The **CERT/SEI Insider Threat** corpus (Carnegie Mellon) is
the canonical scenario taxonomy and dataset for enumerating insider TTPs; frequency still has
to be credibility-blended from own HR/security telemetry against sparse public base rates —
insider events are rarer and worse-reported than external ones, so the prior dominates longer.
- CERT Insider Threat dataset overview — https://www.emergentmind.com/topics/cert-insider-threat-dataset

---

## 3. Cyber-actuarial / insurance pricing, Monte-Carlo, aggregation, tail measures

### 3.1 How insurers actually price (and its honest limits)

Cyber insurance pricing is the most mature real-world CRQ, and its candour is instructive:
insurers **still lean heavily on qualitative control assessments** because credible actuarial
loss data is thin and "knowledge about effective loss controls accrues slowly as claims
evidence accumulates." The direction of travel is FAIR-style frequency/severity modelling fed
by pooled claims (Cyentia, NetDiligence, DHS CIDAWG) plus firmographic rating factors.

- Geneva Association, "Strengthening Cyber Resilience Through Insurance" — https://www.genevaassociation.org/publication/cyber/strengthening-cyber-resilience-through-insurance
- "How do carriers price cyber risk?" (*J. Cybersecurity*, OUP) — https://academic.oup.com/cybersecurity/article/5/1/tyz002/5366419
- Cyber insurance/audit review & recommendations — https://arxiv.org/pdf/2602.03127

### 3.2 Pricing the *controls* — investment models

For "what is a control worth in £", the reference model is **Gordon–Loeb** (optimal security
investment as a function of breach probability and loss), now extended to clustered/correlated
attacks. It formalises the non-obvious result that prevention reduces both expected loss *and*
loss variance — i.e. controls buy tail reduction, which is what capital/premium actually pays
for.
- Stochastic Gordon–Loeb under clustered attacks — https://arxiv.org/pdf/2505.01221

### 3.3 Monte-Carlo, aggregation, and tail measures — the engine

- **Monte-Carlo** is the standard resolution method: sample every input distribution (lognormal
  severity, Poisson/NB frequency, PERT expert inputs) thousands of times → empirical loss
  distribution. https://www.tcs.com/what-we-do/services/cybersecurity/white-paper/monte-carlo-method-quantify-cyber-risks
- **Aggregation** across scenarios/business units must model **dependence**, not just add:
  copulas capture correlated/systemic cyber events (a single vendor compromise hitting many
  units at once). Naïve independence *understates* aggregate tail risk. Cyber-specific caution:
  heavy tails mean diversification behaves counter-intuitively (aggregating more risks does not
  always reduce VaR).
  - Risk aggregation & capital allocation with copulas — https://arxiv.org/pdf/2103.10989
  - Aggregate cyber-risk cautionary statistics for (re)insurers — https://arxiv.org/pdf/2105.01792
- **Tail measures** — report the *curve*, and summarise it with:
  - **VaR** (loss at a percentile) — regulatory workhorse but ignores severity beyond the
    threshold and is **not sub-additive** (can penalise diversification).
  - **TVaR / CVaR / Expected Shortfall** (mean loss beyond VaR) — coherent, captures tail
    severity, preferred for heavy-tailed/cat-like cyber losses. Cyentia specifically studied
    TVaR stability for reporting. https://www.cyentia.com/back-to-the-tvar/
  - **Economic capital** = capital to survive to a chosen tail percentile (e.g. 1-in-200 /
    99.5% VaR, the Solvency II bar) — the natural "how much should this risk cost us to hold"
    output.
  - Cyber Value-at-Risk system — https://www.sciencedirect.com/science/article/pii/S0167404821003692

**Build implication:** the engine's output is a **loss-exceedance curve** annotated with
Expected Loss, VaR and **TVaR** at chosen percentiles — prefer TVaR as the headline because
VaR is incoherent on exactly the heavy tails cyber has. Model dependence explicitly when
aggregating.

---

## 4. Blunt verdict — load-bearing vs snake-oil

### Load-bearing (build on these)
- **FAIR factor decomposition** (frequency × magnitude, PERT inputs, Monte-Carlo, loss-exceedance
  output). Open standard, sound structure. **Keep.**
- **Calibrated estimation** (Hubbard). Non-negotiable input discipline; it is the fix for the
  exact "hand-asserted triple" failure being replaced. Track calibration per estimator.
- **Credibility theory (Bühlmann/-Straub)**. The rigorous way to use sparse own-data now by
  blending it with an industry prior. Most under-used, highest leverage.
- **Empirical loss/frequency data** (Cyentia IRIS, DBIR, NetDiligence) with **heavy-tailed
  severity** (lognormal body + Pareto/GPD tail). Anchors the numbers and the tail.
- **ATT&CK/DBIR-grounded TEF and control-coverage → Resistance Strength.** Ties frequency to
  observed adversary behaviour and to your actual controls.
- **TVaR / Expected Shortfall + explicit dependence modelling** for aggregation and capital.

### Snake-oil (reject / treat as red flags)
- **Risk matrices, heat-maps, high/med/low, and multiplying ordinal scores** (incl. arithmetic on
  CVSS as if it were a probability). Cox proves matrices can be *worse than useless*
  (worse-than-random ranking, range compression); Hubbard shows ordinals add error. Do not build
  on these. — Cox, "What's Wrong with Risk Matrices?" *Risk Analysis* 28(2), 2008 —
  https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1539-6924.2008.01030.x ;
  ordinal-scale problems — https://arxiv.org/pdf/2103.05440
- **Black-box CRQ scores** — a single proprietary number with no visible factor tree, no inputs,
  no method. Un-auditable, un-defendable to a board, un-back-testable. Insist on the Open FAIR
  tree and named data sources instead. — https://securityboulevard.com/2020/07/efficient-demotivation-how-black-box-risk-solutions-disempower-cyber-professionals/
- **False precision / uncalibrated inputs** — GIGO. A Monte-Carlo over garbage triples is
  garbage with error bars. The engine is only as good as calibration + data provenance behind
  each leaf. — https://www.risklens.com/resource-center/blog/avoiding-garbage-in-garbage-out-in-cyber-risk-measurement
- **Point estimates and light/normal tails** — omitting the tail (or using lognormal/normal
  where a Pareto tail is needed) systematically under-prices exactly the events that bankrupt.
- **Any "validated" claim without back-testing evidence** — calibration curves, out-of-sample
  fit, and model-risk sensitivity must be shown, or the validation claim is marketing.

---

## What we should actually build on

A defensible £-engine is: **an Open-FAIR factor tree**, whose every leaf is **a distribution
sourced by provenance rank** — (1) own loss data, (2) industry empirical data (Cyentia/DBIR/
NetDiligence), (3) ATT&CK/threat-intel-shaped TEF, (4) *calibrated* expert estimate as flagged
fallback — with **sparse own-data credibility-blended (Bühlmann–Straub) into industry priors**,
**heavy-tailed severity (lognormal body + Pareto/GPD tail)**, **Monte-Carlo with explicit
dependence for aggregation**, output as a **loss-exceedance curve summarised by Expected Loss +
TVaR/economic capital**, and a **back-testing/calibration loop** so the model can be shown
wrong. STRIDE/attack-trees enumerate the scenarios; ATT&CK grounds the frequencies and maps
controls to the Resistance-Strength term.

Every one of these is traceable to a primary source above. The prior toy had the FAIR skeleton
and none of the four things (calibration, empirical anchoring, credibility-blending,
back-testing) that make the skeleton mean anything. Those four are the whole job.

### The three most load-bearing methods
1. **Calibrated estimation (Hubbard)** — fixes the exact failure being replaced; the price of
   admission for any human input.
2. **Credibility theory (Bühlmann–Straub)** — the rigorous, optimal way to use thin own-data
   today by blending it with an empirical industry prior; the highest-leverage under-used technique.
3. **Empirical, heavy-tailed frequency/severity data (Cyentia IRIS / DBIR)** fed through the
   **FAIR Monte-Carlo tree** and reported as **TVaR/loss-exceedance** — anchors the numbers and
   prices the tail that actually matters.
