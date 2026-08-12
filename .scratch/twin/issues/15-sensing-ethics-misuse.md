# 15 — Behavioural sensing, ethics gate, Goodhart & misuse

Type: grilling
Status: RESOLVED (2026-08-05) — 2 ACs partial, carried forward
Blocked by: 07, 10, 11, 12 (all resolved)

## Question

The people-sensing half, its ethics gate, and the two debts carried forward (Goodhart from 10+11; a
named misuse catalogue from 10).

**Already determined (not re-litigated):**
- Research 05: real deployment needs **legitimate interests + a documented LIA**, a **mandatory DPIA**,
  **advisory-only / human-in-the-loop** (Art. 22), **no special-category inference** (Art. 9),
  bias-tested against protected characteristics.
- Ticket 07: **sensitivity-split schema** — structural person↔component edges in-graph; behavioural
  inference in a **gated overlay**; **special-category structurally unrepresentable**.
- Ticket 10: **covert sensors permanently ruled out**; full transparency; contestability.
- Ticket 12: the demo substrate is synthetic, so the demo is exempt; the guardrail governs real use.

**Genuinely open:**
- **The admission rule for a sensor** — "everything is modelled" (ambition) collides with data
  minimisation (ethics). What test admits a behavioural sensor?
- **The sensor set** — which sensors are in scope at all, and at what granularity (individual vs
  aggregate vs cohort)?
- **Goodhart** — the owed position: sensors change behaviour once known; which are most gameable, and
  what does the twin do about it?
- **The misuse catalogue** — named misuses (justifying layoffs, suppressing pay, surveillance creep)
  and the constraint that blocks each.
- **The gate mechanism** — how the DPIA gate works operationally, and what "detaching the overlay"
  concretely means.

## Acceptance criteria
- [ ] A sensor admission rule reconciling total-scope ambition with minimisation.
- [ ] The sensor set + granularity decision.
- [ ] A stated Goodhart position with the most-gameable sensors named.
- [ ] A named misuse catalogue, each with its blocking constraint.
- [ ] The operational gate mechanism, incl. what detaching the overlay means.

## Decided so far (grilling 2026-08-05)

**Q1 — sensor admission: a LADDER of all three tests, applied in order.**

**The reconciliation first: "everything is modelled" ≠ "surveil everything."** Total scope was always
about the **world-model** — any factor that can move the landscape is in scope for *modelling*. The twin
can model the **mechanism** "grievance raises insider risk" — a causal edge evidenced from published
literature (research 05) — **without sensing a single employee's mood.** Mechanisms live in the **shared
world layer**; observations live in the **overlay** (ticket 07's layering, doing the reconciling work).
**Model the mechanism universally; sense sparingly.**

**The ladder, in order:**
1. **Purpose limitation** — which *named scenario* consumes this sensor, and will anyone act on it? A
   sensor feeding nothing is surveillance for its own sake. No scenario → no sensor.
2. **Necessity** — is there a less intrusive route to the same question? **Prefer structural over
   behavioural** (bus-factor from commit *structure*, never from reading message content), **aggregate
   over individual**, **cohort over person**.
3. **Proportionality** — does the risk illuminated outweigh the intrusion imposed? **This is computable,
   not a hand-wave:** ticket 09's causal-path rule applies symmetrically, so **the £ engine prices the
   intrusion too** — monitoring imposes morale/attrition costs and feeds the grievance→insider path that
   is already modelled. The intrusion side of the ledger is real and evidenced.

**Q2 — Goodhart (the position owed from tickets 10 + 11): (b) design rule + (c) backstop.**
Covert sensors are permanently ruled out, so **everyone knows what is measured — gaming is a certainty to
design for, not a risk to mitigate.**

**(b) The design rule — prefer sensors where GAMING THE METRIC *IS* THE DESIRED BEHAVIOUR.** If the only
way to improve a bus-factor score is to genuinely spread knowledge to more people, then someone gaming it
has done exactly what was wanted. **Goodhart-proof by construction, not by vigilance** — a mechanism-design
property we can *select for*, and far more robust than detecting cheating.
Contrast the ones to avoid or mark heavily: **commit counts, message sentiment, hours-online** — cheaply
faked *without* doing anything useful, so gaming them is pure loss.
This adds a fourth consideration at selection time, after Q1's ladder: among sensors that pass
purpose/necessity/proportionality, **prefer those whose gaming is beneficial; where none exists, mark
gameability explicitly** as a first-class sensor attribute.

**(c) The backstop — a metric improving faster than the underlying reality raises a flag, not a cheer.**
**Honest limit:** without independent ground truth (which we usually lack) this cannot distinguish gaming
from genuine improvement, so **(c) surfaces suspicion, never a verdict** — consistent with everything else
being contestable rather than authoritative.

**Q3 — the misuse catalogue (human reviewed 2026-08-05: nothing missing from the table; fable pass
commissioned for additions).** The catalogue and its blocking constraints:

| Misuse | What blocks it |
|---|---|
| **Suppressing pay** | Perspectival £ (09) — an employee-side twin can exist and disagree; non-nettable register entries make externalised cost visible; the grievance→insider path prices it back into the firm's own ledger |
| **Justifying layoffs** | Advisory-only (Art. 22); individual-level outputs not produced (Q1 necessity rung prefers cohort/aggregate) |
| **Surveillance creep** | Purpose limitation (Q1 rung 1): a sensor is bound to a named scenario; reuse must re-pass the ladder + a fresh DPIA |
| **Performance management by proxy** | Gated, detachable behavioural overlay; advisory-only; special-category unrepresentable |
| **Blame attribution after an incident** | **NEW constraint:** knowledge edges may feed *capability* scenarios (bus-factor, succession, resilience) but are **inadmissible as inputs to any retrospective individual-attribution scenario** — a scenario-level admissibility rule, not a data restriction, since the data is legitimately needed elsewhere |
| **Detecting union organising** | Universal constraint: trade-union membership is Art. 9 special-category → **structurally unrepresentable** (07) |
| **Decision laundering** (re-running until a scenario agrees) | Scheduled execution + scoreability declared at run time (11, 13); *every* execution recorded, so cherry-picking is visible in the record |
| **Weaponising another org's twin** | Per-org overlays never leave the tenant (07) |

**Observation: that the constraints mostly already existed is evidence the design is coherent rather than
accreted** — no bolt-on ethics layer was needed, because perspectivalism, purpose limitation, structural
unrepresentability and recorded executions were already doing the work.
**Pending:** a fable adversarial pass (`research/misuse-catalogue-fable.md`) for what a systematic list
cannot see — misuses routing *around* structural constraints, harms to non-employees, weaponised
transparency/contestability, discoverability/liability effects, and harms with no bad actor.

**Q3b — adversarial pass returned (2026-08-05, `research/misuse-catalogue-fable.md`, 40+ findings; run on
Opus after three fable capacity failures). It found a gap in the THINKING, not the list.**

**The five to add:**
1. **Strategic non-modelling** — documented foreseeability creates liability, so the rational deployer
   scopes the twin to *exclude* the scenarios most likely to produce it. **Our sensor ladder ("must feed a
   named scenario someone will act on") supplies the principled vocabulary for refusing to look** — the
   anti-surveillance safeguard doubles as a **certified mechanism for deliberate ignorance**, and the twin
   then confers documented diligence on the domains where it looked hardest at nothing.
2. **The outsiders** — 7 of 8 catalogue entries concern employees, while the twin's sharpest commercial
   edge points at **suppliers, contractors, applicants, acquisition targets**. **Perspectival £
   *legitimises* this**: their harm is outside the currency by construction, and "they can run their own
   twin" is a joke aimed at a six-person subcontractor. Plus **procurement-mandated twins** conscripting a
   supply chain (how SBOMs and ESG questionnaires propagated).
3. **Exit-cost asymmetry** — the grievance→insider counter-price **only bites for people who can credibly
   leave**. From *permitted structural fields alone* (comp history, working patterns, location, skill
   specificity) the twin identifies exactly who cannot. **A precision instrument for locating the
   population the pay-suppression block does not protect.**
4. **Absence-as-alibi** — structural unrepresentability of Art. 9 data prevents discrimination
   **detection**, not discrimination. **Disparate impact needs no protected field to occur, but does need
   one to be measured.** Needs a sealed audit channel, or an explicit admission that the system cannot be
   checked for disparate impact.
5. **Unauditable constraint removal + constraint-adjacent optimisation** — removing forbidden options
   *before* optimisation means the record **cannot distinguish an ethical exclusion from a convenient
   one**, and destroys the most informative signal available: **how attractive the forbidden option was.**
   Meanwhile the optimiser walks to the nearest permitted point — usually **the same harm minus the name**
   (constructive dismissal for dismissal; a structural proxy for the banned sensor).

**Runners-up:** immutable-git vs **Art. 17 erasure**, with twin-transfers-on-acquisition (most legally
exposed); **role-not-person signatures** (cheapest real fix — human signatures currently manufacture a
named-target list); **ensemble stuffing** (get your world-model admitted and the curve widens toward your
preference, no argument needed); the **union twin forcing the union to surveil its own members**.

**THE STRUCTURAL BLIND SPOT (accepted as correct):** *every constraint in the design is **epistemic** —
what may be represented, inferred, produced, traced, exported. **Not one constrains power** — who may act,
on whom, with what asymmetry, and with what recourse.* Hence a catalogue full of forbidden data and empty
of protected parties, and a blank where the whole outside of the organisation should be.
*"Perspectival £ is the tell: faced with an irreducible conflict of interest, the design converts a power
asymmetry into a plurality of viewpoints and calls the symmetry a virtue — when only one of those
viewpoints can afford to be instantiated, and it's the one holding the data, writing the constraints,
curating the ensemble and paying the bill."*

**Q4 — response to the blind spot: (b) ACCEPT THE LIMIT AND SCOPE IT EXPLICITLY.**
**A system cannot constrain power it does not hold.** Constraining who may act, on whom, with what
recourse belongs to **law and governance outside the twin**. We state that plainly rather than implying
the epistemic constraints protect anyone — no power layer is claimed, and the design must stop reading as
though one exists.
**What the twin CAN do: refuse to be the alibi, and make asymmetry legible.** Delivered by these
mechanisms (same structural-not-procedural pattern used throughout):
- **Publish the SCOPE EXCLUSIONS alongside the constraint set** — what the twin was *not* asked to model,
  listed. Turns **strategic non-modelling from invisible into legible** (finding #1). Does not stop the
  behaviour; removes its deniability.
- **Log constraint removals WITH the attractiveness of the forbidden option** — recovers the signal
  finding #5 says pre-filtering destroys, and lets a principled exclusion be told from a convenient one.
- **An affected-parties register** — outsiders bearing modelled costs are **named**, though outside the
  currency (finding #2). Gives them no power; refuses to let their absence look like their non-existence.
- **A sealed audit channel for disparate impact**, or an explicit admission the system cannot be checked
  for it (finding #4's honest fork).
- **Role-not-person signatures** — human signatures currently manufacture a named-target list. Cheapest
  real fix identified.
**UNSOLVED, RECORDED AS SUCH: #3 exit-cost asymmetry.** From data we have decided is legitimate
(comp history, working patterns, location, skill specificity) the twin can identify **who cannot afford to
leave** — precisely the population the pay-suppression counter-price fails to protect. **No structural
constraint proposed; inventing a reassuring rule here would be worse than the honest gap.** Carried as a
known harm.

## RESOLVED (2026-08-05) — with two items carried forward

Sensor admission is a **ladder** (purpose → necessity → proportionality) reconciled by **"model the
mechanism universally, sense sparingly"** — mechanisms live in the shared world layer, observations in the
overlay. **Goodhart** is handled by **preferring sensors whose gaming IS the desired behaviour**, marking
gameability, and treating suspiciously fast improvement as suspicion never verdict. The **misuse
catalogue** is recorded with its blocking constraints, extended by an adversarial pass whose **structural
finding is accepted: every constraint here is epistemic, none constrains power** — so the design
**explicitly disclaims a power layer** and instead makes asymmetry legible (published scope exclusions,
logged constraint removals with attractiveness, an affected-parties register, a disparate-impact audit
channel, role-not-person signatures). **Exit-cost asymmetry is recorded as an unsolved harm.**

## Acceptance criteria
- [x] Sensor admission rule reconciling total-scope ambition with minimisation.
- [~] Sensor set + granularity — **the RULE is decided** (structural over behavioural, aggregate over
      individual, cohort over person; each sensor bound to a named scenario). **The enumerated set is a
      build-time artefact, carried forward, not decided here.**
- [x] Goodhart position with the most-gameable sensors named (commit counts, message sentiment, hours-online).
- [x] Named misuse catalogue with blocking constraints, plus the adversarial extension and the accepted
      structural critique.
- [~] Operational gate mechanism — **derived**: the behavioural overlay is a separately-gated store whose
      detachment is a demonstrable act (ticket 07), admission requires passing the ladder + a DPIA
      (research 05), and reuse re-triggers both. **The concrete DPIA workflow is carried forward.**
