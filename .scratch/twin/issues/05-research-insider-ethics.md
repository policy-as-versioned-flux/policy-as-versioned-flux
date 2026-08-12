# RESEARCH: insider-risk modelling + the behavioural-sensing ethics/law guardrail

Type: research
Status: resolved
Blocked by: none

## Question

Two halves, both needed before the people-layer can be designed:

- **Insider-risk modelling** — how is it quantified? CERT/SEI insider-threat models, motivation +
  indicator frameworks (financial pressure, disgruntlement, coercion, ideology, ego), the **cost of
  compromising a privileged user** and the **levers that move it** (least-privilege, JIT, separation
  of duties, monitoring, detection latency), key-person / bus-factor risk.
- **The guardrail (hard constraint)** — the legal/ethical limits of **behavioural sensing** (comp,
  promotion, workload, email/chat/commit/working-patterns) for security: UK/EU **GDPR**, employee-
  monitoring law, ICO guidance, discrimination, proportionality, **DPIA** requirements, transparency
  and consent. What is permissible, what requires a DPIA, what is off-limits.

Output: `research/insider-risk-and-ethics.md` — cited; the modelling approach *and* the guardrails
the people-twin must satisfy (feeds the reflexive-governance workstream).

## Answer (2026-08-04) — resolved

**Modelling** = CERT **Critical Pathway to Insider Risk** (predispositions → stressors → concerning
behaviours → maladaptive org responses → crime scripts) for the *features*, wrapped in **FAIR** for
the £. Motivations = **MICE(S)**; CERT's key finding: **~80% of malicious insiders acted on a
workplace grievance** → peer-relative **disgruntlement is the highest-signal feature**. Cost of a
privileged compromise (Ponemon): credential theft ≈ $679k; **detection latency dominates** (<30d
≈ $11.9M vs >90d ≈ $18.3M); PAM saves ≈ $5.9M. **Levers map cleanly onto FAIR factors:** least-
privilege = blast radius, JIT = exposure window, SoD = difficulty, monitoring/UEBA = latency — so the
pay-rise-vs-hardening comparison is computable. **Bus-factor** risk runs in parallel (bus factor 1 =
worst; 46% of GitHub projects there) and *interacts* with CPIR (the overloaded, passed-over sole
maintainer scores high on both blast-radius and grievance).
**Guardrail (real deployments only):** UK GDPR + DPA 2018 + ICO 2023 monitoring guidance — **don't
rely on consent** (invalid in employment) → legitimate interests + a documented **3-part LIA**; a
**DPIA is mandatory** before email/chat/keystroke/biometric/profiling sensing. **Red lines:** no
special-category inference (Art. 9), scores **advisory / human-in-the-loop** only (Art. 22),
bias-tested against protected characteristics (Equality Act 2010). **Demo vs real:** synthetic data on
a fictitious org means GDPR/DPA don't bite — Part B governs *real* deployment; the demo's value is
showing the DPIA-gate / advisory-only / special-category-exclusion working on safe data. Full: `research/insider-risk-and-ethics.md`.
