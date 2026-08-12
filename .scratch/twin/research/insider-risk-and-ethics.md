# Insider-risk modelling + the behavioural-sensing ethics/law guardrail

Research for ticket `05-research-insider-ethics`. Two halves: (A) how insider risk is
quantified, and (B) the legal/ethical hard constraint on behavioural sensing of employees.

> **DEMO vs REAL-DEPLOYMENT boundary (read first).**
> Our demo uses **AI-synthesised, deliberately noisy behavioural data for a fictitious org** —
> no real person is sensed, no real comp/promotion/email/commit data is processed. On synthetic
> data about invented people, **UK GDPR and employment law do not bite** (no data subjects, no
> workers). So Part B is **not** a demo blocker; it is the specification the **people-twin must
> satisfy before it is ever pointed at a real workforce**. The demo should visibly flag this — e.g.
> a "SYNTHETIC — no real surveillance" banner — and the twin's design should carry Part B as
> enforced guardrail config so the switch from synthetic to real data is a governed, gated act, not
> a silent one. Part A (the modelling) is real and reusable as-is; Part B is a compliance gate on
> real inputs only.

---

## Part A — how insider risk is modelled quantitatively

### A.1 The behavioural spine: CERT/CMU Critical Pathway to Insider Risk (CPIR)

The dominant practitioner model is CMU/CERT's **Critical Pathway to Insider Risk**, refined with
the SEI insider-threat corpus. It is not a formula; it is a **staged pathway** that says risk is
rarely a single trait and instead accumulates through five stages ([CREST/CMU CPIR](https://crestresearch.ac.uk/comment/implications-of-the-critical-pathway-to-insider-risk-for-current-personnel-security/),
[Claycomb, CPIR Overview 2024 (PDF)](https://insiderthreatmitigation.org/wp-content/uploads/2025/01/Claycomb-Critical-Pathway-to-Insider-Risk-Overview-2024.pdf)):

1. **Personal predispositions** — personality traits, psychiatric issues, prior rule violations,
   social-network vulnerabilities; recent additions include immaturity/gullibility.
2. **Stressors / triggers** — *personal* (divorce, debt), *organisational* (reorg, merger,
   redundancy, passed-over promotion), and *community* (pandemic, social-identity conflict).
3. **Concerning behaviours** — observable indicators, notably **disgruntlement** = "levels of
   Anger, Blame and Victimisation significantly different than peers."
4. **Maladaptive organisational responses** — the org sees warning signs and mishandles them,
   escalating rather than defusing risk (the lever most under an employer's own control).
5. **Crime scripts** — the concrete actions of the eventual act (theft, sabotage, fraud).

**Motivation taxonomy.** The classic counter-intelligence acronym **MICE(S)** — **M**oney,
**I**deology, **C**oercion, **E**go, and **(S)** disgruntlement/grievance — maps directly onto the
ticket's list (financial pressure, ideology, coercion, ego, disgruntlement). CERT's empirical
finding is that **~80% of malicious insiders were motivated by a workplace grievance**
([CREST/CMU](https://crestresearch.ac.uk/comment/implications-of-the-critical-pathway-to-insider-risk-for-current-personnel-security/)),
which is why "disgruntlement relative to peers" is the single highest-signal behavioural feature.
CPIR also names **mitigating factors** that pull someone *off* the pathway (strong social/family
support, capacity for insight, enlightened management) — these are modellable as risk-*reducing*
terms, not just risk drivers.

> **For the twin:** CPIR gives the *feature set* (predisposition, stressor, concerning-behaviour,
> org-response signals) and the *directionality* (grievance and passed-over promotion push up;
> support and fair management pull down). It is the justification for sensing comp/promotion/
> workload/working-patterns at all — they are proxies for stage-2 stressors and stage-3
> disgruntlement. That same fact is exactly what makes them legally sensitive (Part B).

### A.2 The quantitative wrapper: FAIR (turning the pathway into money)

CPIR tells you *who is drifting toward risk*; **FAIR (Factor Analysis of Information Risk)** turns
that into a defensible number ([FAIR Institute standard v3.0 (PDF)](https://www.fairinstitute.org/hubfs/Standards%20Artifacts/Factor%20Analysis%20of%20Information%20Risk%20(FAIR)%20Standard%20v3.0%20(January%202025).pdf),
[Open Group FAIR whitepaper](https://collaboration.opengroup.org/projects/security/fair/documents/16708/fair_whitepaper.pdf)):

```
Risk  =  Loss Event Frequency (LEF)  ×  Loss Magnitude (LM)

LEF   =  Threat Event Frequency (TEF)  ×  Vulnerability
         TEF = Contact Frequency × Probability of Action
         Vulnerability = f(Threat Capability vs Control/Difficulty)

LM    =  Primary Loss  +  (Secondary Loss Event Frequency × Secondary Loss Magnitude)
```

FAIR is a **"glass-box" probabilistic** model — inputs are ranges/distributions, output is a
loss-exceedance curve in currency, not a red/amber/green cell. For insider risk the mapping is:

- **CPIR stage score → Probability of Action** (a disgruntled, stressed insider is likelier to act).
- **Privilege / access breadth → Vulnerability and Loss Magnitude** (a privileged user converts more
  threat events into loss, and each loss is bigger).
- **Controls (below) → Difficulty**, which suppresses Vulnerability and detection latency, which
  caps Loss Magnitude.

### A.3 Cost of compromising a privileged user, and the levers that move it

Empirical cost anchors (Ponemon *Cost of Insider Risks Global Report*, via
[Proofpoint](https://www.proofpoint.com/us/resources/threat-reports/cost-of-insider-threats) /
[Ponemon-Sullivan 2023](https://ponemonsullivanreport.com/2023/10/cost-of-insider-risks-global-report-2023/)):

- **Credential/privileged-account theft ≈ $679k per incident** (2023; ~$842k in later figures) —
  the most expensive insider category, because privilege = blast radius.
- **Detection latency dominates total cost:** incidents contained in **<30 days ≈ $11.9M** average
  annualised activity cost vs **>90 days ≈ $18.3M** — a ~50% swing purely on how fast you detect.
- **Containment ≈ $179k** per incident; **Privileged Access Management saves ≈ $5.9M** annually.

**Levers that move the number (each maps to a FAIR factor):**

| Lever | FAIR factor it moves | Effect |
|---|---|---|
| **Least privilege** | Loss Magnitude + Vulnerability | Shrinks blast radius per compromised identity |
| **JIT / time-boxed access** | Threat Event Frequency (Contact Frequency) | Standing privilege → zero when not in use; smaller window |
| **Separation of duties** | Vulnerability (Difficulty) | No single identity can complete a high-value action alone |
| **Monitoring / UEBA** | Detection latency → Loss Magnitude | Peer-relative anomaly detection shortens the >90d→<30d gap |
| **Detection latency itself** | Loss Magnitude (secondary loss) | The single biggest cost multiplier per Ponemon |

(Least-privilege / UEBA / privileged-user risk corroborated by
[Gurucul](https://gurucul.com/blog/risks-and-mitigation-of-insider-threats/) and
[Microsoft Insider Risk](https://www.microsoft.com/en-us/security/business/security-101/what-is-insider-risk-management);
FAIR+MITRE insider mapping by [Safe Security](https://safe.security/resources/blog/learn-the-indicators-of-insider-threats/).)

### A.4 Key-person / bus-factor risk

Distinct from *malicious* insider risk: the **availability** risk of losing a critical person. The
**bus factor** = the minimum number of people who must vanish before a project stalls for lack of
knowledge; **bus factor 1 = worst case** ([Wikipedia](https://en.wikipedia.org/wiki/Bus_factor),
[generic.de](https://www.generic.de/en/blog/busfaktor-in-software-projekten)). It is empirically
severe: a study of 133 popular GitHub projects found **46% had a bus factor of 1** and a further
**28% sat at 2** ([Soto-Valero](https://www.cesarsotovalero.net/blog/bus-factor-a-human-centered-risk-metric-in-the-software-supply-chain.html)).

Quantify per component as: `bus_factor(c) = min authors covering ≥ ~50% of that component's
knowledge/commits`, then weight by component criticality. It is the older **key-person risk** idea
specialised to technical experts. For the twin this doubles as a *retention/loss* signal that
**interacts with CPIR stage-2**: a passed-over, overloaded, sole-maintainer of a critical system is
simultaneously the highest bus-factor risk *and* a high disgruntlement risk — the same person on
both axes, which is the interesting modelling result.

### A.5 Modelling approach (recommended for the people-twin)

1. **Per-person CPIR feature vector** — predisposition (static), stressors (comp delta, missed
   promotion, workload/on-call load), concerning behaviour (**peer-relative** disgruntlement from
   working-pattern/comms anomalies), org-response quality. Peer-relative, not absolute — CPIR's
   own definition.
2. **Map to FAIR** — CPIR score → Probability of Action; privilege/access → Vulnerability + Loss
   Magnitude; controls (LP/JIT/SoD/monitoring) → Difficulty and detection latency. Output a
   **currency loss-exceedance estimate per identity**, not a colour.
3. **Overlay bus-factor** as a parallel availability score; flag the overlap set (high blast-radius
   *and* high grievance *and* sole-maintainer) as the priority cohort.
4. **Levers are the actionable output** — the twin should say "JIT-gating these 6 standing admin
   grants removes $X of modelled loss," i.e. recommend control changes, **not** verdicts about people.

---

## Part B — the guardrail a REAL deployment must satisfy (hard constraint)

Governing law for a UK/EU workforce: **UK GDPR + Data Protection Act 2018**, the **ICO Employment
Practices guidance on *Monitoring workers* (finalised Oct 2023)**, **UK GDPR Art. 22** (automated
decisions/profiling), and the **Equality Act 2010** (discrimination). Everything below applies to
**real employee data only** — not the synthetic demo.

### B.1 You need a lawful basis, and it is almost never consent

Monitoring must be **lawful, fair and transparent**. Employers must pick one of the six UK GDPR
lawful bases *at the outset* and document it — and "get it right first time; you should not change
it later without good reason" ([ICO guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/),
[Data Protection Report](https://www.dataprotectionreport.com/2023/10/uk-information-commissioners-office-publishes-final-guidance-on-employee-monitoring/)).

- **Consent is generally invalid in employment** — the power imbalance means it is rarely "freely
  given." Do not build on it.
- **Legitimate interests** is the usual basis for security monitoring, but it requires a documented
  **Legitimate Interests Assessment (three-part test):** (1) **Purpose** — a real, articulated
  interest (here: preventing insider harm); (2) **Necessity** — monitoring is genuinely needed and
  there is **no less intrusive way** to achieve it; (3) **Balancing** — the interest does not
  override workers' rights and reasonable expectation of privacy.
  ([ICO](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/))
- **Remote/home workers have a higher expectation of privacy** — raising the balancing-test bar.

### B.2 What *requires* a DPIA (mandatory, before you start)

A **Data Protection Impact Assessment** is mandatory before any processing likely to be **high
risk**. The ICO explicitly lists the monitoring cases that trigger it — and several are exactly what
insider sensing implies ([ICO](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/),
[Hunton](https://www.hunton.com/privacy-and-cybersecurity-law-blog/uk-ico-publishes-guidance-on-workplace-monitoring)):

- Monitoring **emails and messages**;
- **Keystroke** monitoring;
- Processing workers' **biometric** data (DPIA needed *wherever* biometrics uniquely identify);
- Monitoring likely to result in **financial loss** to the worker;
- Any **profiling** or use of **special category data**.

The ICO's steer: even when *not* strictly mandatory, **do a DPIA anyway** to prove the monitoring is
fair. For the twin, treat **DPIA-complete + LIA-complete as a hard precondition gate** on connecting
any real data source. Also **consult workers or their representatives (e.g. trade unions)** and
document their views unless there is good reason not to.

### B.3 What is off-limits / high-risk (design constraints)

- **Special category data by inference.** Email/chat/working-pattern sensing can *reveal* special
  category data — e.g. **emails to a union rep or occupational-health/therapy**, health from absence
  patterns, religion/belief from working-hours. Inferring special-category data needs an **Article 9
  condition** and is a red line if done without one. The twin must not derive or store these.
- **Solely-automated decisions with legal/"similarly significant" effect are prohibited by
  Art. 22** unless a narrow exception (contract, law, or explicit consent) applies, and even then a
  worker has rights to **human intervention, to contest, and to a review**
  ([ICO Art. 22](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/rights-related-to-automated-decision-making-including-profiling/)).
  An insider-risk score that on its own gates access, pay, promotion, or discipline is squarely in
  scope. **Keep a human in the loop and keep the score advisory.**
- **Discrimination (Equality Act 2010).** Profiling that correlates with protected characteristics
  can be **indirect discrimination** even if unintended; the Act applies to AI-supported decisions
  just as to human ones ([Fisher Phillips](https://www.fisherphillips.com/en/insights/insights/what-us-employers-need-to-know-about-ai-hiring-bias-laws-in-the-eu-and-uk)).
  Sensing "workload," "working patterns," or "comms tempo" can proxy for disability, caring
  responsibilities (sex/age), religion (prayer/observance hours), or pregnancy. Requires bias
  testing and Art. 22 §71 duty to "prevent errors, bias and discrimination."
- **Covert monitoring** is exceptional — permissible only for suspected serious wrongdoing where
  telling workers would prejudice detection, and time-boxed. Not a general operating mode.

### B.4 Guardrails a real deployment must satisfy — checklist

The people-twin, when pointed at a **real** workforce, must:

1. **Not run on consent** — use documented legitimate interests + a completed **LIA (3-part test)**.
2. **Complete a DPIA before ingesting** email/chat/keystroke/biometric/profiling/financial-impact
   data — this is mandatory, not optional; gate data connection on it.
3. **Be transparent** — workers told what is sensed, why, and how; **consult worker reps/unions**.
4. **Keep the score advisory / human-in-the-loop** — never a solely-automated decision with
   significant effect (Art. 22); provide contest + human-review paths.
5. **Enforce data minimisation & least-intrusive means** — the "necessity" limb; prefer aggregate/
   peer-relative signals over raw content; justify every field.
6. **Block special-category inference** — no deriving/storing health, union membership, religion,
   etc. (Art. 9); design comms sensing to exclude protected recipients (union/OH).
7. **Bias-test the model** against protected characteristics (Equality Act 2010) and record it.
8. **Respect remote-worker privacy** (higher expectation) and time-box/justify any covert element.

### B.5 Demo vs real — what each requires

| | **Demo (synthetic, fictitious org)** | **Real deployment (actual workforce)** |
|---|---|---|
| Data | AI-synthesised, noisy, invented people | Real employees' comp/comms/patterns |
| GDPR / DPA 2018 | **N/A** — no data subjects | Fully applies |
| DPIA | Not required (nothing to assess) | **Mandatory** before ingest (B.2) |
| LIA / lawful basis | N/A | Legitimate interests + LIA (B.1) |
| Art. 22 / Equality Act | N/A | Human-in-loop, bias-tested (B.3) |
| Transparency / union consult | Show "SYNTHETIC" banner | Required (B.4) |
| What the guardrail is *for* | Prove the *shape* of governance | The actual legal precondition |

The value of building the guardrail into the demo now is that the demo can **show the governance
working** (DPIA gate, advisory-only scores, special-category exclusion) on safe synthetic data, so
that flipping to real data is a **deliberate, gated, audited** act — which is the whole point of the
reflexive-governance workstream.

---

## Sources

**Part A:**
- [CREST — implications of the Critical Pathway to Insider Risk](https://crestresearch.ac.uk/comment/implications-of-the-critical-pathway-to-insider-risk-for-current-personnel-security/)
- [Claycomb / CMU — Critical Pathway to Insider Risk Overview 2024 (PDF)](https://insiderthreatmitigation.org/wp-content/uploads/2025/01/Claycomb-Critical-Pathway-to-Insider-Risk-Overview-2024.pdf)
- [CERT Guide to Insider Threats (sample, PDF)](https://ptgmedia.pearsoncmg.com/images/9780321812575/samplepages/9780321812575.pdf)
- [SEI — Insider Threat Deep Dive: IT Sabotage](https://www.sei.cmu.edu/blog/insider-threat-deep-dive-it-sabotage/)
- [FAIR Institute — FAIR Standard v3.0, Jan 2025 (PDF)](https://www.fairinstitute.org/hubfs/Standards%20Artifacts/Factor%20Analysis%20of%20Information%20Risk%20(FAIR)%20Standard%20v3.0%20(January%202025).pdf)
- [Open Group — FAIR whitepaper (PDF)](https://collaboration.opengroup.org/projects/security/fair/documents/16708/fair_whitepaper.pdf)
- [Safe Security — insider indicators with FAIR + MITRE](https://safe.security/resources/blog/learn-the-indicators-of-insider-threats/)
- [Ponemon Cost of Insider Threats (Proofpoint)](https://www.proofpoint.com/us/resources/threat-reports/cost-of-insider-threats) · [Ponemon-Sullivan 2023 summary](https://ponemonsullivanreport.com/2023/10/cost-of-insider-risks-global-report-2023/)
- [Gurucul — risks & mitigation of insider threats](https://gurucul.com/blog/risks-and-mitigation-of-insider-threats/) · [Microsoft — insider risk management](https://www.microsoft.com/en-us/security/business/security-101/what-is-insider-risk-management)
- [Wikipedia — Bus factor](https://en.wikipedia.org/wiki/Bus_factor) · [Soto-Valero — bus factor as supply-chain risk metric](https://www.cesarsotovalero.net/blog/bus-factor-a-human-centered-risk-metric-in-the-software-supply-chain.html) · [generic.de — bus factor in industry](https://www.generic.de/en/blog/busfaktor-in-software-projekten)

**Part B:**
- [ICO — Monitoring workers (guidance)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/)
- [ICO — Rights related to automated decision-making including profiling (Art. 22)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/rights-related-to-automated-decision-making-including-profiling/)
- [ICO — impact of Article 22 on fairness in AI](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-fairness-in-ai/what-is-the-impact-of-article-22-of-the-uk-gdpr-on-fairness/)
- [Norton Rose — ICO final guidance on employee monitoring](https://www.dataprotectionreport.com/2023/10/uk-information-commissioners-office-publishes-final-guidance-on-employee-monitoring/)
- [Hunton — ICO guidance on workplace monitoring](https://www.hunton.com/privacy-and-cybersecurity-law-blog/uk-ico-publishes-guidance-on-workplace-monitoring)
- [Ogletree — new ICO guidance on employee monitoring](https://ogletree.com/insights-resources/blog-posts/uk-information-commissioner-publishes-new-guidance-on-employee-monitoring/)
- [Fisher Phillips — AI hiring bias laws in EU & UK (Equality Act 2010)](https://www.fisherphillips.com/en/insights/insights/what-us-employers-need-to-know-about-ai-hiring-bias-laws-in-the-eu-and-uk)
