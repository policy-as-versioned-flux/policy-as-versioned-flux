# 08 — The causal layer: making fast-forward/rewind/play interventional

Type: grilling
Status: RESOLVED (2026-08-04)
Blocked by: 07 (resolved)

## Question

Ticket 07 decided causal edges exist as a typed layer with evidence + confidence. This ticket decides
**how they actually work** — fable's #2 finding: a knowledge graph gives Pearl rung 1, but *play* is
rung 2 (intervention) and *rewind* is rung 3 (counterfactual).

- **Claim model** — what exactly does a causal edge assert (direction, sign, lag, functional form,
  strength)? Point estimate or distribution?
- **Evidence grades** — what backs a causal claim (documented mechanism, historical co-movement,
  expert judgement, literature)? How is confidence expressed, and when is an edge too weak to use?
- **Intervention semantics** — how `do(x)` propagates: which edges carry it, how effects compose along
  paths, what happens where only structural edges exist.
- **Counterfactual/rewind semantics** — what "would it have happened if we'd patched?" computes over.
- **Intervention-aware scoring** — the forecast record must know a prediction was *acted upon*, else a
  mitigated non-event scores as a bad forecast and poisons calibration. How is action recorded and
  netted out?
- **Confounding discipline** — how much identification rigour without stalling on causal purism.

## Acceptance criteria
- [ ] A causal-edge schema (assertion + evidence grade + confidence) in ubiquitous language.
- [ ] Defined intervention + counterfactual semantics, incl. behaviour on structural-only paths.
- [ ] The intervention-aware scoring rule, with a worked example of a mitigated non-event.
- [ ] A stated identification/confounding discipline + its honest limits.
- [ ] Exercised on a real claim from each co-flagship (Qwikster→churn; EUV delay→node slip).

## Decided so far (grilling 2026-08-04)

**Q1 — a causal edge asserts (b) sign + lag + an ELASTICITY AS A CALIBRATED RANGE.** e.g. "a 1-unit slip
in EUV availability moves the process-node evolution coordinate by 0.1–0.3, lagged 6–18 months",
expressed as a **PERT/triple with uncertainty** — the *same representational move already committed for
the FAIR leaves*. One estimation discipline (Hubbard calibration), one propagation engine (Monte-Carlo),
across both the causal layer and the £ engine — not two epistemologies bolted together.
- **(a) qualitative (direction + coarse strength) is a LEGAL DEGRADED STATE**, not a failure — it just
  cannot produce a £ delta, only a ranking.
- **(c) full functional forms are reachable per-edge** where evidence justifies it; the schema carries it.
  Rejected as a blanket requirement (would stall on fitting forms for hundreds of edges with no data).
**Corollary (load-bearing):** *a wide range is not the same as a missing edge, and both are honest.* A
claim we can only state qualitatively must be **representable and visibly weak**, never silently promoted
to a number — the "reject arithmetic on ordinal scales" discipline (track 02) applied to causation.
Co-flagship check: "Qwikster → churn" supports a real elasticity (dated subscriber numbers both sides);
"sanctions tighten → talent-pool contraction" supports only sign-and-lag with a very wide range. Both
belong in the graph; they must not look equally confident.

**Q2 — evidence: (b) a TYPED EVIDENCE LADDER + separate confidence, with USE-GATING by grade.**
GRADE-style: *how we know* is recorded separately from *how sure we are* (you can be highly confident in
a grade-3 literature mechanism, or unsure about a grade-1 experiment with noisy measurement — a single
scalar loses exactly that).

**The ladder**
1. **Dated natural experiment / documented mechanism** — observable data both sides (Qwikster: dated
   price change, churn measured after).
2. **Repeated historical co-movement** across multiple instances or orgs.
3. **Literature / domain theory** — established mechanism, not observed here.
4. **Calibrated expert judgement** — Hubbard-trained, explicitly recorded *as* judgement.
5. **Model assertion** — the LLM "just knows" this is causal.

**Grade 5 is where parametric contamination hides.** The pillar banked for the backtest (an LLM
"flagging" a famous collapse is indistinguishable from memorisation) reappears *identically* here: a
causal edge asserted from training data looks exactly like a well-evidenced one unless the schema forces
the distinction. Grade 5 makes it visible and auditable.

**Use-gating (not binary exclusion):** only **grades 1–2** may carry an interventional **£ delta into a
scored forecast**. Grades 3–5 may shape scenarios and rank options but are **flagged and excluded from the
calibration record** — weak causal knowledge still informs thinking without contaminating the
falsifiability claim. Same separation drawn everywhere else in the model.

**Q3 — intervention propagation: (c) ONE traversal, TWO distinct outputs.**
- **Causal paths → a quantified £ delta** (elasticities composed by Monte-Carlo through the graph).
- **Structural-only paths → an unpriced BLAST-RADIUS** — "these components are downstream and exposed;
  nobody has claimed a mechanism" — **flagged explicitly as non-quantified**.
Rejected: (a) causal-only, which throws away the working reverse-dependency traversal (`/arckit:impact`)
— blast-radius is useful even without a magnitude; (b) structural-as-weakly-causal, which manufactures
numbers where no mechanism was claimed and is how a dependency graph quietly becomes a fake causal model.
(c) keeps both and makes the boundary between *"we can price this"* and *"we only know it's downstream"*
**visible in the output**.

**Composition rules (from the calibrated-range commitment):**
- **Compose by sampling, not by multiplying point estimates** — Monte-Carlo through the graph so
  uncertainty compounds honestly instead of being averaged away.
- **Attenuate with depth** — long chains multiply uncertainty until the answer is noise; past a depth
  threshold the result degrades to **directional only** and drops out of the priced set. A 5-hop
  elasticity chain is not a number.
- **Handle shared ancestry** — multiple paths from one intervention are not independent; naive summing
  double-counts. Aggregate with explicit dependence (track 02's copula guidance).
Intel check: EUV → process node → product competitiveness is a *causal* chain with priceable
elasticities; process node → dozens of downstream SKUs / partner roadmaps / fab-siting is *structural* —
real exposure, no claimed mechanism. The output must say so rather than pricing the lot.

**Q4 — scoring: (b) forecasts are CONDITIONAL BY CONSTRUCTION — and the whole thing is a WEATHER
FORECAST** (human framing, 2026-08-04, and it corrects the framing the grill started with).

Each forecast records its assumed action-state ("given no intervention, X; given intervention I, Y") and
is scored against the branch that actually occurred. No new machinery — an intervention is `do(x)`, so a
conditioned forecast is just another query on the causal model. An unenumerated action makes a forecast
**off-branch: unscoreable, not wrong** — and that is itself data (a twin repeatedly surprised by which
lever the org pulls is failing at something real).

**Mitigation credit is itself a causal claim and carries its own evidence grade.** Otherwise the twin
excuses every miss with "our warning prevented it" and becomes unfalsifiable by construction (the fable
trap). **Grades 4–5 (expert judgement, model assertion) earn NO calibration credit**; a prevented event
counts only when the prevention is evidenced at grade 1–2, else the outcome is recorded unscoreable. The
Q2 use-gating rule pointed at the twin's own excuses — the strictest gate where the incentive to cheat is
strongest.

**THE WEATHER-FORECAST FRAME (load-bearing, reshapes the honesty claim):**
- Forecasts are **probabilistic, not binary claims**. "Not everything we predict will happen" is the
  correct behaviour, not a defect. A 30%-rain forecast is not falsified by a dry day.
- **Individual forecasts are neither right nor wrong — the FORECASTER is calibrated or not**, across many
  forecasts. Scoring is by **proper scoring rules (Brier / log score) + reliability diagrams** over a
  *set*, never a verdict on a single call. Replaces "was the twin right?" with "is the twin calibrated?"
- **Implication — the twin needs forecast VOLUME to be scoreable at all.** Calibration can't be assessed
  from a few dramatic calls: the twin must make **continuous, dated, low-stakes forecasts at varied
  confidence levels**, routinely. This retro-justifies the backtest *suite* (several orgs × many dated
  forecasts = enough n).
- **Ensembles complete ticket 07's competing world models.** Operational weather forecasting runs the
  model many times with perturbed conditions and treats the **spread as the uncertainty**. Our rival
  world-models with credences ARE that ensemble — their disagreement is the honest confidence interval,
  not noise to resolve away.

**Q5 — confounding: (b) declared assumptions + a MANDATORY alternative-explanation field + graph-based
confounder flagging.** Every grade-1/2 edge must name at least one plausible confounder and say why it is
discounted; **the dependency graph is already a confounder detector** — shared ancestors of both endpoints
surface automatically as candidate common causes, a free structural check. The usual failure is *not
considering* the alternative, not failing to formally rule it out. Strictness stays proportional to
stakes (only grade-1/2 edges price a scored forecast, so only they carry the obligation). Formal
identification (do-calculus, back-door, sensitivity analysis) stays available for a handful of
high-stakes edges but is rejected as a blanket requirement — same failure as full SCM in ticket 07:
it demands data and assumptions we won't have across an org landscape.
**Honest limit, stated up front:** most causal edges will be observational and non-identified. **The
calibration record — not an identification proof — is what earns them trust.** If the edges are
systematically wrong, the reliability diagrams show it.

**Q5b — RIVAL CAUSAL CLAIMS ARE FIRST-CLASS** (human insight, 2026-08-04: *"sometimes the meteorologists
get it wrong even with the same data in front of them; they can disagree; sometimes both are right in
some ways, sometimes both wrong, sometimes one is right — that's okay"*).
The graph does **not** force one elasticity per relationship. **Competing causal accounts of the same
relationship coexist**, each with its own evidence grade, assumptions, alternatives and credence — the
causal-layer analogue of ticket 07's competing world models. **The calibration record adjudicates over
time; not an author, not an identification proof.** Disagreement is **ensemble spread**, not a
data-quality defect to be resolved away. Consequences: the schema keys causal claims by
{relationship, claimant, evidence, credence}; scenario runs may be executed per-account, and the spread
across accounts is reported as uncertainty.

## RESOLVED (2026-08-04)

The causal layer: **calibrated-range elasticities** (sign + lag + PERT triple), on a **typed evidence
ladder** with **use-gating** (only grades 1–2 price a scored forecast; grade 5 = model assertion, where
parametric contamination hides), propagating as **two outputs** (priced causal delta + unpriced
structural blast-radius) composed by **Monte-Carlo with depth attenuation and shared-ancestry handling**.
Forecasts are **conditional by construction** and judged as a **weather forecast** — probabilistic, scored
by proper scoring rules + reliability diagrams over *volume*, never a verdict on one call — with
**evidence-graded mitigation credit** closing the unfalsifiability loophole. Confounding is handled by
**declared assumptions + mandatory alternatives + free graph-based confounder flagging**, and **rival
causal accounts coexist as ensemble spread**, adjudicated by calibration rather than by argument.

## Acceptance criteria — all met
- [x] Causal-edge schema (assertion + evidence grade + confidence) in ubiquitous language.
- [x] Intervention + counterfactual semantics, incl. behaviour on structural-only paths.
- [x] Intervention-aware scoring rule (conditional-by-construction + graded mitigation credit).
- [x] Identification/confounding discipline + its honest limits.
- [x] Exercised on a real claim from each co-flagship (Qwikster→churn grade-1 elasticity; EUV→node slip
      causal chain vs the structural fan-out below it).
