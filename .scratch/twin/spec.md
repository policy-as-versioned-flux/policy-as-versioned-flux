# Spec — Organisational digital twin + anticipatory strategic-intelligence engine

Status: ready-for-agent

> **Superseded in part, 2026-08-28.** The ratified [north star](../../NORTH-STAR.md) §7 overrides three
> framings below. Governance is not "one enactment arm": composition is the eco-system and the twin is one
> participant in it (re-grill 9). The estate is not "a prior to test": it is the reference implementation
> the eco-system lifts from or retires, one decision each (NORTH-STAR §6). The KinD clusters and the org
> repos are not "binned": the six orgs are live and Flux is the distribution arm (reversal 1). The twin's
> subjects are now driftwood, tuppence and ludlow; the real firms stay as the backtest corpus (re-grill 31).
> The talk is a read of the truth surface, never the definition of done. Nothing below is rewritten.

Source: `.scratch/twin/map.md` (`wayfinder:map`, decision-complete 2026-08-05) and its 22 resolved tickets.
Scope: **the whole system.** Each resolved ticket's full acceptance criteria remain the yardstick. The
walking skeleton is the *route*, not the destination.

---

## Problem Statement

An organisation's risk and strategy functions are siloed, and the silos are enforced by incommensurable
units. Security risk is scored on a colour, HR risk lives in an engagement survey, strategic risk lives in
a board deck, and supply-chain risk lives in a spreadsheet. Because none of them share a unit, nobody can
answer the question that actually matters: *given this threat, is the cheapest proportionate response a
security control, a pay rise, or a strategic play?* The question is unaskable, so it goes unasked, and the
answer defaults to whichever function shouted loudest.

Three failures compound it.

**Governance instruments are unfalsifiable.** They emit green ticks and compliance percentages that were
never checked against anything. A tool that cannot be wrong cannot be trusted, and everyone in the room
knows it — which is why the output is filed rather than acted on.

**Anticipation is asserted, not demonstrated.** Horizon-scanning decks list plausible futures with no
mechanism connecting a weak signal to a specific component of *this* organisation, no record of what was
predicted, and no score against what actually happened. When something arrives that the deck named, it is
claimed as foresight; when something arrives that it missed, the deck is simply reissued.

**An LLM asked to reason about a famous corporate collapse cannot demonstrate anticipation at all.** It has
read the ending. "Flagging" Enron in 2000 is indistinguishable from reciting Enron in 2026. Any system
built on models like these inherits the problem, and most such systems do not acknowledge it exists.

The prior effort in this repository (`.scratch/talk-spec/`, the `estate/` monorepo) is a worked example of
what happens when you optimise for a demo instead: a single repository standing in for an organisation, a
risk number with no calibration behind it, and no Wardley or causal modelling at all. It is retained as a
**prior to test**, not a foundation.

## Solution

A **digital twin of an organisation** — a typed, git-versioned knowledge graph spined on the Wardley value
chain — plus an **anticipatory engine** that runs over it.

The twin senses any dated signal, external (sanctions, quantum, memory cost, AI-model access, climate,
supply-chain, M&A) or internal (morale, knowledge concentration, comp, working patterns), binds it to the
components it touches, and propagates its consequences along typed causal edges. Every impact and every
candidate response is priced in **one £ currency**, so a pay rise and a hardening control become comparable
options against the same modelled risk. The output is a **trade-off curve across an ensemble**, not a
verdict.

Four properties distinguish it from what already exists.

**It is a weather forecast.** Individual forecasts are neither right nor wrong; the forecaster is calibrated
or not. The twin emits continuous, dated, low-stakes forecasts across the full confidence range, scored by
proper scoring rules and reliability diagrams over volume. Rival world-models and rival causal accounts are
held simultaneously as an **ensemble**, and their spread *is* the uncertainty.

**It can be proved wrong, and the proof is structural.** Rewind to a dated past state, gate every input to
what was knowable then, fast-forward, and score against what actually happened. Because history is surprise
we did not author, it is the strongest falsifiability mechanism available. It is backed by a **co-registered
forecast book** — blind forecasts emitted and signed before the resolution window, on the same questions and
timestamps as liquid prediction markets. Forward-dated questions cannot be in any training corpus, so this
is the one external gate that escapes contamination entirely.

**It treats contamination as a first-class threat.** Backtest subjects are chosen for *low notoriety*, not
fame. Enron is carried deliberately as a **contamination control**: the measured gap between performance on
Enron and performance on an obscure key yields a memorisation-leakage discount applied to every backtest
score.

**It is an artefact to argue with, not an oracle.** The point of a Wardley map is to give people something
to debate that is distanced from the human stories and emotion — the disagreement externalises onto the
artefact instead of running between people. A single number ends a conversation; a map sustains one. This is
why the design refuses to collapse plurality anywhere: competing world models, rival causal accounts,
ensemble spread, a trade-off curve rather than a recommendation, and contestability as a first-class
workflow rather than a complaints box.

Versioned, attestable governance — policy as a signed, pinned dependency — survives as **one enactment arm**
for machine-enforceable controls and as the substrate proving a control is in force. It is not the point.

---

## User Stories

### The graph and the model

1. As a **twin operator**, I want the organisation represented as a typed knowledge graph spined on the Wardley value chain, so that risk, strategy and dependency questions are asked against one structure rather than four disconnected artefacts.
2. As a **twin operator**, I want git-versioned text to be the source of truth and every store to be a derived index, so that any state of the model is addressable, diffable and reconstructable at any past commit.
3. As a **twin operator**, I want bulk synthetic substrate exempted from the git-is-truth rule, so that volume does not make the repository unusable.
4. As a **multi-org operator**, I want a shared **world layer** (landscape, technologies, markets, geopolitics) separate from **per-org overlays** each org owns and never shares, so that cross-org learning happens without private facts leaving the tenant.
5. As a **risk modeller**, I want the world/overlay split to double as the credibility-theory structure — industry prior in the world layer, sparse own-data in the overlay — so that a thinly-evidenced org still gets a defensible prior.
6. As a **strategist**, I want the org's *believed* map held distinctly from *rival forecasts* and from *revealed truth*, so that the believed-vs-revealed delta is measurable — that delta is the anticipation failure itself.
7. As a **strategist**, I want no privileged "actual" map anywhere in the system, so that the twin's own belief is just another scored position rather than an unexamined baseline.
8. As a **risk owner**, I want risks represented as first-class scenario objects referencing {components, graph version, world model, time}, so that a risk is always anchored to the exact model state that produced it.
9. As a **risk owner**, I want roll-ups derived rather than authored, so that an aggregate can never drift from its constituents.
10. As a **data-protection owner**, I want people's structural edges in the graph, behavioural observations in a gated overlay, and special-category data **structurally unrepresentable**, so that Article 9 compliance is an impossibility rather than a policy.
11. As a **builder**, I want every artefact marked authored or derived, so that provenance rules can be enforced mechanically rather than by convention.

### Sensing and binding

12. As a **twin operator**, I want any dated signal ingested, STEEP-tagged and bound to the components it touches, so that a weak signal becomes a specific consequence for *this* organisation rather than a line in a trend deck.
13. As a **twin operator**, I want a component's evolution position **inferred first from accumulated evidence**, then correctable by a human, so that the model starts from evidence rather than from opinion.
14. As a **twin operator**, I want the twin to **push back** on a human override, so that a correction is a provenanced claim that is itself scored — humans get calibrated against evidence too.
15. As a **twin operator**, I want binding fully automated at volume, trusted downstream rather than gated at entry, so that throughput is achievable — use-gating, contestability and calibration are what make this safe.
16. As a **twin operator**, I want unbound signals retained in a decaying pool rather than discarded, so that a signal the graph could not yet interpret is not lost.
17. As a **twin operator**, I want a model change to trigger a retrospective sweep of the unbound pool, so that **lead-time-to-recognition becomes measurable** — the quantum/harvest-now-decrypt-later case, mechanised.
18. As an **analyst**, I want observation to propagate bidirectionally but intervention to propagate downstream only, so that learning a fact updates beliefs everywhere while *doing* a thing does not rewrite its own causes.
19. As a **twin operator**, I want emission both event-driven and scheduled, so that the schedule protects the calibration record from selection bias — we cannot only forecast when we feel confident.
20. As an **enactment owner**, I want declarations and evidence both accepted as sensor inputs with **corroboration setting the evidence grade**, so that the action-state loop closes without new machinery and with *less* surveillance pressure, not more.

### The causal layer

21. As a **causal modeller**, I want every causal edge to assert sign, lag and a calibrated-range elasticity as a PERT triple, so that propagation is quantitative rather than directional hand-waving.
22. As a **causal modeller**, I want each edge to carry an **evidence grade** on a typed ladder from 1 (dated natural experiment) to 5 (model assertion), so that the strength of a claim travels with the claim.
23. As a **sceptic**, I want **use-gating** — only grades 1–2 may price a scored forecast — so that grade-5 model assertions, exactly where contamination hides, cannot silently become the basis of a number someone acts on.
24. As an **analyst**, I want two outputs from propagation: a priced causal delta *and* an unpriced structural blast-radius, so that "we know this is connected but cannot price it" is a first-class answer rather than a gap papered over.
25. As a **risk modeller**, I want Monte-Carlo composition with depth attenuation and shared-ancestry handling, so that a long chain does not manufacture confidence and a common cause is not double-counted.
26. As a **sceptic**, I want mitigation credit to be **itself evidence-graded**, so that the classic unfalsifiability loophole — "the incident didn't happen *because* of our control" — is closed.
27. As a **strategist**, I want rival causal accounts to coexist as **ensemble spread** adjudicated by the calibration record over time, so that legitimate disagreement is represented rather than resolved by whoever authored last.

### The £ currency

28. As a **risk owner**, I want impacts and candidate responses priced in the same unit, so that an HR lever, a security control and a strategic play are comparable and the cheapest proportionate one can be identified.
29. As a **non-employer stakeholder** (union, regulator, employee body), I want the £ to be **perspectival** — it belongs to whoever pays to run the twin — so that I can instantiate my own perspective rather than inherit the employer's.
30. As an **ethics owner**, I want ruin-class and forbidden options handled as **hard pre-filters, never as prices**, so that no sufficiently large number can purchase an excluded option.
31. As a **sceptic**, I want the constraint set **published upfront**, so that paperclip-maximiser risk is disclosed rather than discovered.
32. As an **ethics owner**, I want a universal legal/ethical floor distinguished from perspective-declared red lines, so that a perspective can add constraints but never remove the floor.
33. As a **sceptic**, I want only evidence-graded causal paths to cash flow admitted into the £, so that the pricing boundary is **derived, not declared** — reputation and morale price via churn, attrition and grievance paths, or they do not price at all.
34. As a **decision-maker**, I want the output as a **trade-off curve across the ensemble with a marked default**, not a verdict, so that when two world-models disagree about pay-rise-versus-hardening, *that disagreement is the headline*.

### Scenarios, gameplay and time

35. As an **analyst**, I want the engine built from exactly two composable primitives — **time** and **intervention** — so that projection, act-now, counterfactual and the backtest all fall out of the same machinery with no separate harness.
36. As an **analyst**, I want **scenario → execution → forecast(s)**, where one execution emits *multiple differing* forecasts, so that the ensemble is presented rather than collapsed.
37. As a **twin operator**, I want scheduled execution of the standing scenario library to *be* the forecast production line, so that calibration accumulates continuously rather than in bursts around interesting events.
38. As an **analyst**, I want **fast-forward, rewind and play** to map onto Pearl's abduction → action → prediction, so that the three verbs have a rigorous semantics rather than a UI metaphor.
39. As a **backtester**, I want rewind to support three information regimes — **as-consumed**, **as-knowable**, **with-hindsight** — so that the gaps between them localise failure to sensing, interpretation, or the model itself.
40. As a **backtester**, I want **only as-consumed to score**, so that the honest number is never contaminated by what we know now.
41. As a **strategist**, I want opportunity found by **sweeping for Wardley-play preconditions on schedule**, so that opportunities are pulled — threats push themselves forward, opportunities never do.
42. As a **strategist**, I want the scheduled opportunity sweep to act as the structural counterweight to the evidence record's negativity bias, so that the twin is not merely a better fear machine.
43. As an **analyst**, I want the standing scenario library to cover the committed set — quantum/HNDL, bus-factor and key-person, insider and coercion, supply shock, sanctions, M&A, memory cost, AI-model access, climate event — plus opportunity plays and backtest cases, so that no signal class is hand-waved.

### Falsifiability and scoring

44. As a **sceptic**, I want forecasts scored by proper scoring rules with reliability diagrams over volume, so that calibration is a measured property rather than a claim.
45. As a **sceptic**, I want backtests run against **low-notoriety** answer keys (Carillion primary, NMC Health, Wirecard), so that success is not explicable by fame. *(Build ticket 39 finding: Wirecard does not meet this bar — a bestselling book and a Netflix documentary put it on a level with Enron — so it is built and scored as a second contamination `high` case instead, alongside Enron at build ticket 40; Carillion and NMC Health are this story's actual low-notoriety pair.)*
46. As a **sceptic**, I want **Enron carried as a contamination control** and a measured memorisation-leakage discount applied to every backtest score, so that the contamination threat is quantified rather than acknowledged.
47. As a **sceptic**, I want **hindsight-resistance controls** — cases where the contemporaneous record contradicts the canonical story — so that confident agreement with the canonical story functions as a **memorisation detector**.
48. As a **sceptic**, I want a **co-registered forecast book**: blind forecasts on the same questions, timestamps and resolutions as liquid prediction markets, so that there exists at least one external gate that contamination cannot reach.
49. As a **sceptic**, I want the benchmark question set **quarantined from ingestion at any lag**, auditable because ingestion is provenanced, so that *"we forecast before we looked"* is provable rather than asserted.
50. As a **sceptic**, I want benchmark questions selected by a **versioned, pre-registered mechanical rule** spanning the full confidence range, so that a change to the selection rule is as visible as a change to the constraint set.
51. As a **compliance owner**, I want the forecast book to **observe only, never participate**, so that there is no UK gambling exposure — and play money is within 1–5 percentage points of real money anyway, so money-backing buys nothing.
52. As an **honest builder**, I want the forecast book's claim scope stated narrowly — evidence of non-overconfidence in general world-forecasting, and **nothing** about Wardley propagation, elasticities, £ pricing or the org overlay — so that a real external gate is not oversold into a fake one.
53. As a **strategist**, I want prediction-market **price moves** consumed as dated world-layer signals but price **levels never treated as probabilities**, so that favourite–longshot bias — rejected-unbiased in every subsample and worst in the deep tail we care about — does not enter the model.

### The synthetic substrate

54. As a **builder**, I want a believable synthetic world as the *medium* with instrumented test cases inside it, and **measurability winning ties**, so that realism serves measurement rather than competing with it.
55. As a **builder**, I want the substrate generated by seeded LLM generation from a **versioned recipe**, so that it is regenerable rather than merely stored.
56. As a **builder**, I want an **eval suite that defines and tunes fidelity** — signal-to-noise, plant difficulty, spine consistency, reporting asymmetry, mundanity — so that the fidelity target is measured rather than asserted.
57. As a **builder**, I want the substrate anchored to the immutable public spine but free-running where the record is silent, so that plants are not trivially findable by diffing against the spine.
58. As a **sceptic**, I want an **enforced planter/detector/scorer split** with its limits stated plainly — shared model priors mean synthetic results evidence *detection mechanics only*, never anticipation of the world — so that the synthetic result is not overclaimed.
59. As a **risk owner**, I want every plant to carry an **actionability horizon**, so that detection after the point of no return scores as the near-zero option value it actually is.
60. As a **builder**, I want the record's negativity bias modelled deliberately, so that the substrate reproduces the asymmetry that real evidence has rather than an idealised balance.

### Provenance and attestation

61. As an **auditor**, I want the artefact signed, the inputs pinned and the *why* recomputable, so that derivation is reconstructable rather than materialised — which works precisely because git is the source of truth and everything else is derived.
62. As an **auditor**, I want **human signatures to assert accountability for a judgement** and **agent signatures to assert reproducible origin only** — runtime, model version, config — so that agent output never inherits human authority.
63. As an **auditor**, I want signatures to attest the **absence** of human involvement, CI-style, so that the authored/derived split becomes cryptographically enforceable and a derived artefact carrying human fingerprints is a detectable anomaly.
64. As a **builder**, I want determinism given the pins as a hard requirement, so that attestation is a proof rather than a claim.

### Ethics, misuse and the twin's view of itself

65. As an **ethics owner**, I want sensor admission to run a **ladder** — purpose, then necessity, then proportionality — so that adding a sensor is a decision with a recorded justification.
66. As an **ethics owner**, I want **"model the mechanism universally, sense sparingly"**: mechanisms live in the world layer, observations in the overlay — so that total-scope ambition and data minimisation stop being in conflict.
67. As an **ethics owner**, I want sensors preferred where **gaming the metric IS the desired behaviour**, and gameability marked where it is not, so that Goodhart is designed around rather than lamented.
68. As an **ethics owner**, I want fast improvement treated as grounds for suspicion but never as a verdict, so that a genuine improvement is not punished.
69. As an **affected party**, I want an **affected-parties register** for people outside the contracting org, so that those who bear consequences without holding the perspective are at least visible.
70. As an **affected party**, I want a **disparate-impact audit channel**, so that differential harm has a route to surface.
71. As a **sceptic**, I want **published scope exclusions**, so that strategic non-modelling is visible rather than deniable.
72. As a **sceptic**, I want **constraint removals logged together with the forbidden option's attractiveness**, so that the motive for loosening a constraint is recorded at the moment it is loosened.
73. As an **affected party**, I want **role-not-person signatures**, so that accountability attaches without creating a personal target.
74. As a **sceptic**, I want the design to **explicitly disclaim a power layer**, so that the accepted structural critique — every constraint here is epistemic, none constrains power — is stated rather than patched over.
75. As a **sceptic**, I want **exit-cost asymmetry recorded as an unsolved harm**, so that the strongest objection is carried openly.
76. As a **twin operator**, I want the twin present as an ordinary component set in its own graph, **depth-1 bounded**, so that it is subject to its own analysis without infinite regress.
77. As a **sceptic**, I want **contestability as a primary feature** with challenges versioned and no hiding behind aggregation, so that arguing with the artefact is the supported workflow rather than a complaint path.
78. As a **twin operator**, I want reflexivity and Goodhart-on-the-twin recorded as a deferred limitation, and covert sensors ruled out permanently, so that the boundary is explicit in both directions.
79. As a **product owner**, I want **organisational adoption modelled as a risk about the twin itself**, because corporate prediction markets beat their own experts by up to 25% MSE reduction and were killed anyway — by manager incentives, not by being wrong.

### Enactment

80. As a **governance owner**, I want the twin to **propose only** — never changing the world without a human, while changing its own model constantly — derived from Article 22, from the fact that a trade-off curve has nothing to auto-execute, and from agent signatures asserting origin rather than endorsement.
81. As a **platform owner**, I want **policy as a versioned, signed, pinned dependency** as the enactment channel for machine-enforceable controls and as the **verification substrate** proving a control is in force.
82. As a **governance owner**, I want that claim held in its narrowed form — policy-as-code is *an* arm, not *the* definition of governance — because the £ engine's whole value depends on most levers *not* being code.
83. As a **platform owner**, I want graded enforcement retained, so that consequence is a spectrum rather than a cliff edge.
84. As a **platform owner**, I want posture-as-identity retained in its narrowed form, so that the claim survives only where the evidence supports it.
85. As a **platform owner**, I want the **Flux falsification test run rather than assumed**: does the risk basis require *continuous* proof-of-force, or would a deploy-time attestation suffice? Drift between deploys is the candidate answer and must be demonstrated.

### Building honestly

86. As a **builder**, I want each capability to carry a **depth grade** (stub / partial / full) against its owning ticket's contract, so that a stub cannot appear unlabelled anywhere it is used.
87. As a **builder**, I want each resolved ticket's **full acceptance criteria to remain the yardstick**, so that the walking skeleton satisfies a *slice* of them and never redefines them.
88. As a **builder**, I want **code treated as disposable by default**, because the durable artefacts are the versioned model and the decision record — replacing code is normal rather than wasteful.
89. As a **demo viewer**, I want a published **does-not-do register**, so that omissions are visible rather than deniable — the same primitive as published scope exclusions, turned on the demo itself.
90. As a **demo viewer**, I want the **Royal Mail** beat to carry falsifiability — rewound under as-consumed, projected, scored — because Netflix's fame would make anticipation indistinguishable from recital.
91. As a **demo viewer**, I want the **Netflix** beat to carry the whole engine — fear and seize on dated evidence, with the deep behavioural substrate.
92. As a **demo viewer**, I want the **Intel** beat to carry a live, unresolved, pinned forward forecast that **cannot be scored yet and says so on screen**, because a dated prediction someone can come back and check beats any retrospective.
93. As a **demo viewer**, I want the thesis sequenced — anticipation and provable falsifiability first, then proportionate versioned governance, **concluding** in the one-currency comparison — so that the most seductive and least self-evident claim is earned rather than asserted at the open.

---

## Implementation Decisions

### The determinism split — what is code and what is a skill

The unit of packaging is decided by one test: **if it must be reproducible from pins, it is code; if it is a
judgement landing at evidence grade 5, it is a skill.** This is forced by the attestation requirement, not
chosen for taste — *"an agent did it, roughly"* cannot be recomputed, so anything on the derivation path
must be code. The partition is non-arbitrary because skills produce exactly the grade-5 claims that the
evidence ladder already distrusts: the architecture and the epistemics land on the same boundary
independently.

**Code** (deterministic, attestable, on the derivation path):
graph schema, validation and authored/derived enforcement; causal propagation by Monte-Carlo with depth
attenuation and shared-ancestry handling; intervention-versus-observation semantics; the FAIR engine (PERT
sampling, heavy-tailed severity, TVaR, constraint pre-filter, trade-off curve); scenario/execution/forecast
objects with pin capture and time-gating by information regime; the scoring harness (proper scoring rules,
reliability diagrams, regime tagging, contamination discount); the unbound-signal decay pool and
retrospective sweep; provenance signing, pin capture and reproducibility checks; the substrate eval suite.

**Skills** (irreducible judgement, each contracted by its owning resolved ticket):
`signal-classify` (11), `causal-claims` (08), `evolution-judge` (11), `substrate-generator` (12),
`gameplay-lens` (13), `ethics-gate` (15). A skill's acceptance criteria *are* its owning ticket's criteria,
not a fresh invention.

**Inherited from arckit** rather than built: D/K/R Wardley maths from `/arckit:wardley`, blast-radius and
reverse-dependency traversal from `/arckit:impact`, scheduled-execution orchestration from
`/arckit:build --refresh`. Known caveats to work around: `impact` has no history, its £ deltas are prose
rather than formulas, and `refresh` assumes a single repository while this is an org of repositories.

**Neither** — governance artefacts, authored and human-signed rather than capabilities: the constraint set,
published scope exclusions, the affected-parties register, the misuse catalogue.

### Storage and the model repository

Git-versioned text is the source of truth; every store is a derived index rebuildable from it. Bulk
synthetic substrate is the sole exception, addressed by content hash rather than held inline. Every artefact
is marked authored or derived, and that marking is enforced cryptographically — a derived artefact carrying
a human signature is an anomaly the provenance check surfaces.

The world layer and each org overlay are separate versioned units. An overlay may reference the world layer;
the world layer may never reference an overlay. This single directional rule is what makes multi-tenancy and
the credibility-theory prior the same mechanism.

Special-category data has **no schema slot**. Compliance is an impossibility of representation, not a
validation rule that could be relaxed.

### The engine

Two primitives compose everything: **time** and **intervention**. Projection is time-forward; act-now is
intervention-at-present; counterfactual is rewind-plus-intervention; backtest is rewind-plus-projection
scored against the record. There is deliberately no separate backtest harness — it would be a second
implementation of the same thing and would drift.

Rewind takes an **information regime** parameter with three values: `as-consumed` (only what the twin
actually ingested by time T), `as-knowable` (everything publicly available by T), `with-hindsight`
(unrestricted). Only `as-consumed` produces a scoring-eligible forecast. The gap between as-consumed and
as-knowable localises a failure to sensing; the gap between as-knowable and with-hindsight localises it to
interpretation; a failure present in all three is the model.

An execution emits **multiple forecasts** — the ensemble — and the API has no mechanism for collapsing them
to one. This is deliberate: the ability to collapse would be used.

### Pricing

The £ is perspectival: a perspective declares who is paying and what their red lines are, and the same
scenario prices differently under different perspectives. Ruin-class and forbidden options are removed by a
**pre-filter that runs before pricing**, so no number can ever be compared against them. The constraint set
is a published artefact.

Admission to the £ is causally gated: a path from a component to cash flow must exist at an adequate
evidence grade or the impact is reported in the unpriced structural blast-radius instead. The pricing
boundary is therefore derived from the evidence, not declared by an author.

Output is a trade-off curve across the ensemble with a marked default. There is no "recommended action"
field.

### Scoring, first

The scoring harness is built in the **first slice**, not retrofitted. Two reasons, both load-bearing: without
it we cannot tell whether any later capability helped, so we would be building blind; and scoring dictates
what every other component must record, so retrofitting it means revisiting everything.

Scores carry a **contamination discount** derived from the measured Enron-versus-obscure-key gap, and a
regime tag. Hindsight-resistance cases are scored inverted — confident agreement with the canonical story is
evidence of memorisation, not of skill.

### The forecast book

An adapter, not a system, and proportionate only because scoring is already core. Questions are selected by
a versioned, pre-registered mechanical rule spanning the full confidence range. The benchmark set is
quarantined from ingestion at any lag, and the quarantine is auditable because ingestion is provenanced.
Emission is pinned and signed before the resolution window opens. Observe only — never place.

### Build order

A **walking skeleton with scoring in the first slice**: one dated signal → binds to a component → an
inferred position moves → one scenario execution → a forecast with its pins → a score against a known
outcome. Then deepen each layer. The mutual dependency between capabilities only bites if you build
layer-by-layer; a vertical cut passes through all of them at once.

Three named failure modes are guarded explicitly:

- **Skeleton-as-ceiling** — guarded by each resolved ticket's full acceptance criteria remaining the yardstick.
- **Premature done** — guarded by per-capability depth grades (stub / partial / full) against the owning ticket's contract.
- **Sunk-cost architecture** — guarded by treating code as disposable; the durable artefacts are the versioned model and the decision record.

Depth grades travel with the capability at runtime, so any surface touching a partial capability displays
that it is partial without anyone having to remember.

### Enactment

Propose only. The twin opens pull requests against the enactment repositories and never merges. Policy ships
as a signed, pinned dependency; graded enforcement and posture-as-identity are retained in their narrowed
forms. Enactment is sensed multi-channel — declarations and machine-verified evidence both count, and
corroboration between channels sets the evidence grade.

The **Flux hypothesis is held pending its falsification test**, which is a work item rather than an
assumption: determine whether the risk basis requires continuous proof-of-force or whether a deploy-time
attestation suffices. Drift between deploys is the candidate justification and must be demonstrated, not
asserted. If it fails, Flux is a convenience and the spec is amended.

### Subjects

**Netflix** (retrospective, whole-engine) and **Intel** (live, forward) are co-flagships. The backtest suite
is **Carillion** (primary, low-contamination, free dated FCA short register plus HC 769), **NMC Health**,
**Wirecard**, and **Enron as contamination control**. **Royal Mail** carries the falsifiability beat — the
counterfactual sits inside its own audited segmental filings, with six-plus dated checkpoints including a
legally-liable IPO prospectus forecasting the very trend it then underinvested against. Portfolio: **Kodak**
and **Maersk**. Each org carries a depth grade and is upgradable on its own independent track.

---

## Testing Decisions

A good test here asserts on **external behaviour at a boundary** — an emitted artefact, a validated claim, a
score — and never on internal structure. This matters more than usual because code is explicitly disposable:
a test coupled to internals becomes the sunk cost that resists the rewrite, which is one of the three named
failure modes.

Three seams, each testing a different kind of thing.

### Seam 1 — the artefact CLI (primary)

The highest boundary in the system. A command takes a pinned model repository, a scenario, a time and an
information regime, and emits a signed artefact: a forecast bundle, a score card, or a price curve. Because
attestation already requires determinism given the pins, this seam is **golden-file testable** — the same
inputs must produce byte-identical output, and that property is itself the first test.

Everything on the derivation path is exercised here: graph validation, propagation, the FAIR engine,
information-regime gating, scoring, pin capture. Skills sit *upstream* of this seam — they author grade-5
claim files that are committed to the model repository, so from the CLI's point of view a skill's output is
just input.

Tests at this seam:
- Determinism: identical pins produce identical artefacts, across runs and machines.
- Regime gating: an `as-consumed` execution cannot reference a fact dated after T, asserted by construction rather than by review.
- Use-gating: a scenario whose only causal path runs through a grade-5 edge produces an unpriced blast-radius, never a price.
- Constraint pre-filter: a ruin-class option is absent from the output entirely, not present with a large number.
- Ensemble integrity: an execution with rival world-models emits multiple forecasts, and no code path collapses them.
- Provenance: a derived artefact carrying a human signature fails the reproducibility check.
- Backtest scoring: a known answer key produces a score, and the Enron control produces a measurably different one.

### Seam 2 — the typed model API

Below the CLI: load graph → propagate → price, called directly. Justified because a propagation defect and a
graph-validation defect are indistinguishable at seam 1 — both surface as "wrong number" — and the
Monte-Carlo layer is where a silent statistical error is most likely and least visible.

Kept deliberately thin: assertions are on numerical and structural properties (does attenuation reduce
influence with depth; does shared ancestry avoid double-counting; does `do()` leave upstream beliefs
untouched while observation updates them), never on call sequences or object shapes.

### Seam 3 — the skill-eval harness

The six skills are non-deterministic by construction, so they cannot be asserted at seams 1 or 2. This seam
runs each skill against a fixture corpus and scores its output against expected classifications with a
**pass threshold**, not exact match — the same shape as the substrate eval suite, which covers
`substrate-generator` only and therefore leaves the other five with no boundary of their own. Without this
seam, skill regression is the failure most likely to go silent.

Per skill: `signal-classify` against a labelled signal corpus (STEEP tag plus binding target);
`causal-claims` against edges with known evidence grades, scored on grade accuracy as much as on the claim
— over-grading is the dangerous failure; `evolution-judge` against dated positions from the public spine;
`gameplay-lens` against plays whose preconditions are known to hold or not; `ethics-gate` against sensor
proposals with known ladder outcomes; `substrate-generator` against the ticket-12 fidelity targets.

The harness records score-over-time per skill per model version, so a model upgrade that degrades judgement
is visible as a regression rather than discovered in an artefact months later.

### Prior art

There is no prior art in this repository — the twin is greenfield, and the prior effort under `estate/` is
explicitly a prior to test rather than a foundation. Its verify-script pattern (a numbered script per claim,
each independently runnable and reporting pass/fail) is worth carrying forward as a *shape* for seam 1,
since it produced an honest 27-of-28 result rather than a rounded-up one. Nothing else transfers.

---

## Out of Scope

**Talk-first framing.** The conference talk is a byproduct of the real system, never its driver. Optimising
for a demo is what produced the monorepo and the toy risk model. It returns only as a downstream showcase.

**The `estate/` monorepo and the KinD clusters.** Binned. The enactment arm is real separate repositories
with real signed dependency pins.

**Google TabFM**, and tabular foundation models as a class for this purpose. Rejected decisively: the
regression head is a single scalar, so it is architecturally incapable of a predictive distribution — no
PERT triples, no GPD tail, no TVaR — and the shipped pipeline clips at ±4σ, amputating exactly the heavy
tail the risk engine exists to measure. The framing conclusion stands beyond the specific model: **these are
inference and calibration problems, not tabular-prediction problems.**

**Aggregate Brier comparison against prediction markets.** Rejected because Brier is a property of a
*(forecaster, question set)* pair, so an aggregate comparison across different question sets is
meaningless. Co-registration on identical questions is the only admissible form.

**Participating in prediction markets.** Observe only.

**A power layer.** The design explicitly disclaims one. Every constraint in it is epistemic; none constrains
power. This is an accepted structural limitation, stated rather than patched, with **exit-cost asymmetry
recorded as an unsolved harm.**

**Covert sensing**, permanently.

**Reflexivity and Goodhart effects on the twin itself** — deferred as a recorded limitation, not solved.

**Depth-2 self-modelling.** The twin models itself at depth 1 only; no inception.

**Real behavioural surveillance data.** The substrate is synthetic. The ethics guardrail exists to govern
real deployment, which is not in this scope.

**Opportunity cases held to the collapse-case evidential bar.** Structurally unreachable and ruled out as a
goal rather than left as a gap — collapse evidence exists *because the collapse pays for it* (short theses,
statutory short registers, examiner reports, inquiries, CDS curves), and **there is no short side of an
opportunity**. Nobody convenes an inquiry into a success. This bounds any claim the twin makes about
opportunity performance, and the bound is published rather than hidden.

---

## Further Notes

**On the negative findings.** Three tickets resolved *against* their own hypothesis — TabFM rejected,
opportunity cases shown structurally unreachable, and the power-layer critique accepted rather than answered.
These are the most valuable results in the map, and the spec keeps them visible rather than tidying them
away. A plan with no negative findings has not been tested.

**On what the forecast book does and does not buy.** It is the only external gate that contamination cannot
reach, and it is deliberately narrow: evidence of non-overconfidence in general world-forecasting, and
nothing whatsoever about Wardley propagation, elasticities, £ pricing or the org overlay. The critique that
every loop closes through one mind **narrows but does not close**, and the spec should not be read as
claiming otherwise.

**On adoption as a risk about the twin itself.** Corporate prediction markets at Google and Ford beat their
own experts by up to 25% MSE reduction and were killed anyway — by manager incentives and information
control, not by being wrong. A better artefact does not automatically win the argument. This is aimed
directly at the transparency bet, and the twin should model it about itself rather than assume it away.

**On why plurality is never collapsed.** Competing world models, rival causal accounts, ensemble spread, a
trade-off curve instead of a verdict, contestability as a workflow — these look like five separate design
choices and are one. The point of a Wardley map is to give people something to argue with that is distanced
from the human stories and emotion. **A single number ends a conversation; a map sustains one.** Terminating
the argument would destroy the thing's function, so every place the system could collapse to a verdict, it
deliberately does not.

**On the standing guard.** *"Be careful not to allow scope to drop and prematurely declare things done, and
be prepared to always change our code and never be married to previous investments."* This is why full
acceptance criteria stay the yardstick, why depth grades travel with capabilities, and why code is
disposable by default. It is the reason this spec covers the whole system rather than the skeleton.
