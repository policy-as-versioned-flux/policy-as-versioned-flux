# 10 — The twin inside the twin: dependency, target, and authority

Type: grilling
Status: RESOLVED (2026-08-05) — two ACs partially met, carried forward (see below)
Blocked by: 07 (resolved)

## Question

Fable's #4 finding. Ticket 07 satisfied the *epistemic* half (the twin's world-model is itself a scored
model). This ticket handles the *operational* half — the twin as an object in the org it models.

- **As a dependency** — the twin becomes the org's biggest new bus-factor-1 risk. It must appear as
  components in its own graph, with its own scenarios priced in the same currency.
- **As a target** — a signed, £-ranked vulnerability dossier is a *shopping list*. Threat-model the
  twin itself (exfiltration, model extraction, sensor poisoning, gaming the scores).
- **As authority** — £-denominated advice is executable political authority. Decision governance: who
  may query, who may cite it in a decision, how outputs are contested, what is advisory vs binding,
  and how misuse (justifying layoffs, suppressing pay, surveillance creep) is constrained.
- **Reflexivity** — the org acts on advice, changing the org the twin then senses: Goodhart on every
  sensor, self-fulfilling/self-defeating prophecy. How is the twin's own effect modelled?

## Acceptance criteria
- [ ] The twin represented as components + scenarios inside its own graph.
- [ ] A threat model for the twin, with controls priced in the same currency.
- [ ] A decision-governance model: query rights, citation rules, contestability, advisory-vs-binding.
- [ ] A stated position on Goodhart/reflexivity, incl. which sensors are most gameable.
- [ ] Named misuse cases with the constraint that blocks each.

## Decided so far (grilling 2026-08-05)

**Q1 — (b) the twin IS an ordinary set of components in its own graph — with a BOUNDED recursion depth**
(human: *"to a limited constraint to avoid infinite loops and inception"*).
The twin's models, data pipelines, compute and **maintainers** are components with dependencies, its own
**bus-factor** (it starts life at bus-factor 1), and its own risk scenarios priced in the same currency.
Rationale: (1) once decisions route through it, it genuinely *is* load-bearing — exempting it from the
treatment every other component gets would be incoherent; (2) it is a high-value target (a signed,
£-ranked inventory of weaknesses is a shopping list), so that risk belongs in the same register as the
risks it catalogues; (3) a separate meta-model (option c) just moves the problem — the watcher is
unwatched, giving infinite regress or an arbitrary stop.
**Bounded self-reference (the guard):** self-modelling terminates at **depth 1** — the twin appears as
components and its risks are priced, but it does **not** model "the twin modelling the twin" as a further
layer. Graph traversal detects and cuts self-referential cycles (the same cycle/shared-ancestry handling
ticket 08 already needs). No meta-meta layer, no inception.
**Consistency test that falls out:** the twin should be able to **price the risk of its own failure**, and
that number should be comparable to the value it claims to add. A twin that cannot justify its own
existence in its own currency is telling you something.
Ticket 09's constraints apply to it too — e.g. a twin proposing to remove its own oversight hits a
**universal** constraint.

**Q2 — transparency: (a) FULLY OPEN — method *and* content** (human: *"we need to demo it"*).
The whole twin is inspectable: schema, rules, constraint list, evidence grades, calibration record —
*and* the graph content, scenarios and £ rankings. This is safe **because of the subject decisions**: the
co-flagship strategic spines (Netflix, Intel) are **public record**, and the behavioural substrate is
**synthetic**. There is no shopping-list problem to protect against, and full openness is what makes the
thing demonstrable and auditable.
**The compartment mechanism still exists and is unused, not absent.** Ticket 07's per-org private overlay
means a **real** deployment can compartment content (open method / closed content — Kerckhoffs) with **no
model change**. Same shape as the ethics guardrail: the demo is open because the data is safe; the
capability governs real use.

**Q3 — authority: (b) CONTESTABILITY BY CONSTRUCTION — and it is the POINT, not a guardrail** (human,
2026-08-05: *"the large point of wardley mapping is to have a thing you can argue with and debate that is
distanced from the human stories and emotion"*).
The map's core value is that it is **an artefact you argue *with***: the disagreement is externalised onto
the artefact instead of running between people. You are not telling a colleague they are wrong — you are
both pointing at a component and arguing about where it sits. So contestability is **the primary
feature**, not an Art. 22 compliance bolt-on (a mere "advisory" label has never stopped a number ending an
argument, and (c) access controls protect the twin rather than the people it is used on).
**Already ~90% built:** provenance on every claim (07), evidence grades (08), rival causal accounts
coexisting as ensemble (08), named perspective + published constraints (09). A contest is literally *"I
dispute this edge / this grade / this world-model / this constraint"* — the machinery to hold a competing
account exists; this exposes it as a **first-class, versioned workflow** where the challenge and its
outcome are recorded.
**The twin cannot hide behind aggregation:** for any number you can ask *"which claim produces this, and
what backs it?"* and get a specific, gradeable, disputable answer — and if you are right, the record shows
the model changed because you pushed. Composes with the weather-forecast frame: a contested claim that
keeps being right accrues calibration credit; one that keeps being wrong loses it, publicly.

**Q4 — reflexivity: (a) ACCEPTED AS NOISE FOR NOW, to avoid inception** (human, 2026-08-05). A
**deliberate scope limit, not a solution** — consistent with Q1's depth-1 bound. The twin does not model
its own effect on the org it senses.
**Known, accepted limitations (recorded honestly, not waved away):**
- **Goodhart on every sensor.** Once a sensor is known, it stops measuring what it measured (commit
  frequency gamed; bus-factor score encouraging knowledge-hoarding to look indispensable; morale proxies
  managed rather than improved). A suspiciously improving metric may be a *signal*, not a success — and
  the twin will not currently notice.
- **Self-attribution.** The twin is a common cause of both its advice and the later observation; without
  that edge it can read its own effects as evidence about the world and congratulate itself.
- **Sensor disclosure changes behaviour** — required by transparency + track 05 proportionality, and
  therefore a real effect we are choosing not to model yet.
**Cost of deferring is low and reversible:** ticket 08's forecasts are already conditional on action-state,
so **which recommendations were adopted is recorded anyway** — the attribution data accumulates whether or
not the reflexive model is built. Deferred for later: modelling twin interventions as first-class graph
events, and **gameability as a first-class sensor attribute** (belongs with the horizon-scanning /
sensor workstream, which must face Goodhart directly).
**Ruled out permanently: covert sensors.** They contradict the transparency decision and are precisely the
surveillance posture the ethics guardrail exists to prevent — and a secret sensor cannot be contested, so
it cannot be corrected.

## RESOLVED (2026-08-05)

The twin is **an ordinary set of components in its own graph** (depth-1 bounded — no inception), **fully
transparent in method and content** (safe because the flagship spines are public record and the substrate
is synthetic; the compartment mechanism exists but is unused), governed by **contestability as its primary
feature** — the map is a thing to argue *with*, distanced from human stories and emotion — and it
**explicitly defers reflexivity/Goodhart modelling** as a recorded limitation.

## Acceptance criteria
- [x] The twin represented as components + scenarios inside its own graph (depth-1 bounded).
- [~] A threat model for the twin, with controls priced in the same currency — **method decided** (it is
      in-graph, so the same scenario/pricing machinery applies; transparency decision removes the
      shopping-list concern for the demo). **The threat-modelling exercise itself is a build task, not a
      decision — carried forward, not done here.**
- [x] A decision-governance model: contestability by construction; challenges + outcomes versioned;
      no hiding behind aggregation. (Query rights are moot under full transparency.)
- [x] A stated position on Goodhart/reflexivity — deferred, with the limitation recorded explicitly.
- [~] Named misuse cases with the constraint that blocks each — **partially**: ticket 09 supplies the
      mechanism (universal + perspective-declared constraints, published upfront; non-nettable register
      entries so externalising onto employees is visible). **A named misuse catalogue is carried forward
      to the ethics/reflexive-governance workstream.**
