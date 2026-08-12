# 13 — The scenario / gameplay engine: fast-forward · rewind · play

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07, 08, 09, 11 (all resolved)

## Question

What turns the sense→move loop into a war-gaming machine — and where the *opportunity* half finally
gets built rather than promised. Pin:

- **The scenario object** — research 04 said this is the genuine net-new vs arckit:
  `{baseline, moves[], drivers[]}`. What exactly is it, and how does it reference
  {graph-version, world-model, time} (ticket 09's scenario objects)?
- **The three verbs** — what *fast-forward*, *rewind* and *play* each concretely compute, and how they
  differ mechanically (ticket 11 already split observation from intervention).
- **Where scenarios live** — branch-per-scenario in git (research 03) vs objects in the graph. What is
  a scenario's relationship to a *forecast* (ticket 08) — are they the same thing?
- **Gameplay / opportunity** — Wardley gameplay + doctrine + climate as automatable lenses (research
  03: climate = rules, doctrine = lint, gameplay = suggestions). How does the engine *propose* moves to
  seize, not just defend? This is where the negativity bias (ticket 12) must be counterweighted.
- **The scenario library** — the committed set (quantum/HNDL, bus-factor/key-person, insider/coercion,
  supply-shock, sanctions, M&A, memory cost, AI-model access, climate event) doubling as **acceptance
  tests** for other workstreams. What makes a scenario admissible to the library?
- **Combinatorics** — the space of what-ifs is unbounded. What decides which scenarios get run?

## Acceptance criteria
- [ ] The scenario object defined, incl. its references and its relationship to forecasts.
- [ ] Concrete semantics for fast-forward, rewind and play, each distinguished.
- [ ] Where scenarios live + how they are versioned/diffed.
- [ ] How opportunity/gameplay moves are proposed, with the negativity counterweight addressed.
- [ ] Admissibility rule for the scenario library.
- [ ] A selection/prioritisation rule for which scenarios run (the combinatorics answer).
- [ ] Exercised on one fear scenario and one opportunity scenario across the co-flagships.

## Decided so far (grilling 2026-08-05)

**Q1 — (c) scenario as container, refined by the human into THREE LEVELS:**
**Scenario** (the definition — `{baseline, moves[], drivers[]}`) → **Execution** (a run of that scenario
**at a point in time**) → **Forecast(s)** (the outputs of an execution — **plural**).
- **An execution yields multiple differing forecasts**, one per ensemble member (rival **world-models** ×
  rival **causal accounts**). They are **presented to a human, not collapsed** — ticket 09's trade-off
  curve and ticket 10's argue-with-it principle, now with an object model behind them. Judging/scoring is
  applied where applicable; presentation is unconditional.
- **Re-running is native:** the same scenario executed repeatedly gives a **time series of executions**,
  each with its ensemble of forecasts.
- **UNIFICATION: scheduled execution of the standing scenario library IS the forecast production line.**
  Ticket 11 requires scheduled emission to keep calibration free of selection bias; the library gives it
  the thing to emit. **The library is not only a set of acceptance tests — it is what runs every cadence**,
  producing the dated volume the weather-forecast frame needs.
- Rejected (a) scenario≡forecast: most scenarios are **deliberately counterfactual** ("what if we'd never
  launched Qwikster?") and have no truth value to check — scoring them is a category error, and it would
  push us toward only running scenarios we can score (the exact selection bias ticket 11 guards against).
  Rejected (b) fully separate: a scenario that never emits anything scoreable is unfalsifiable
  exploration.
- **Scoreability is declared at RUN time, not at review time** — otherwise misses can be retro-classified
  as "just exploration."

**Q2 — (b) TWO COMPOSABLE PRIMITIVES: time and intervention.** The three verbs are compositions, not
three features.
**Notable:** the verbs, chosen intuitively, are **Pearl's counterfactual algorithm** — *abduction →
action → prediction* is exactly **rewind → play → fast-forward**.
- **Rewind** = restore the graph to a past state under an **information gate** (below).
- **Fast-forward** = project with **no** intervention; components continue along inferred trajectories,
  drivers apply — ticket 11's *observation-side* extrapolation ("what if we do nothing").
- **Play** = apply moves as **`do(x)`** — ticket 08's intervention semantics, downstream-only, incoming
  edges severed.
**The compositions are the whole product surface:** fast-forward alone = a projection; play→fast-forward =
"what if we act now"; rewind→play→fast-forward = the counterfactual; rewind→fast-forward (no play) = **the
backtest**. Consequence: **the backtest is not a special mode and needs no separate harness** — build
time-gating and intervention, and it falls out.

**Q2b — REWIND HAS THREE INFORMATION REGIMES, and the gaps between them are a DIAGNOSTIC LADDER**
(human, 2026-08-05: *"value in layering knowledge we now have (hindsight, to eval models) and knowledge we
could have consumed but didn't, to iteratively improve models"*).
- **As-consumed** — only what we actually ingested by time T. **The honest backtest; the only regime that
  scores.**
- **As-knowable** — everything that was *public* at T, ingested or not.
- **With-hindsight** — includes post-T knowledge. **Never scoreable**; for diagnosis and model improvement.
**The gaps localise the failure:**
- as-consumed vs as-knowable → a **sensing/coverage failure** (it was out there; we didn't ingest it —
  fixable by better collection; connects to ticket 12's unbound pool and ticket 11's decay/rescue).
- as-knowable vs the right answer → an **interpretation/model failure** (we had it and made nothing of it
  — the Nokia case).
- still wrong under hindsight → **the model cannot represent what happened** — the deepest failure, and
  the most valuable to know.
**Hard rule: the regime is recorded on every run, and only *as-consumed* enters the calibration record.**
Hindsight leaking into a scored run would manufacture precisely the false confidence the falsifiability
apparatus exists to prevent.

**Q3 — opportunity: (a) PRECONDITION-MATCHED WARDLEY PLAYS, SWEPT ON SCHEDULE.**
Wardley's gameplay catalogue already exists (land grab, exploiting constraint, buyer/supplier power,
undermining barriers, open approach, …), each with stated **preconditions checkable against the map**
(evolution position, dependency structure, ownership, incumbency). The engine evaluates which
preconditions currently hold and suggests those plays, **with the reason attached** ("land grab: this
component is about to commoditise, you own the adjacent capability, no incumbent holds position").
**THE STRUCTURAL FIX FOR THE NEGATIVITY BIAS: threats are PUSH; opportunities must be PULLED.**
A threat announces itself — a signal lands, binds, moves something. An opportunity usually does not:
nothing arrives to tell you a component is about to commoditise in a way you could exploit. So the engine
**actively sweeps the map for gameplay preconditions on every scheduled run** rather than waiting for a
signal. **An asymmetry in the mechanism to counterweight the asymmetry in the record** (ticket 12, Q3c) —
the honest fix, since a data bias cannot be corrected by wishing.
Rejected: **(b) search/optimisation** — explodes combinatorially and optimises against a £ model we have
already said is uncertain and model-relative (false precision at scale); **(c) LLM suggestion** — grade-5
model assertion by construction: acceptable as a *candidate generator* feeding the pattern-matcher, never
as the authority.

**Derived — library admissibility (AC 5):** a scenario is **admissible to the standing library if its
preconditions/triggers are checkable against the map**, which is exactly what makes it **re-runnable every
cadence** rather than a one-off story. Follows directly from Q3 + Q1's unification (the library is the
forecast production line).
**Derived — selection/prioritisation (AC 6, the combinatorics answer):** the what-if space is unbounded,
so the engine does **not** enumerate it. What runs is: (1) the **standing library**, every scheduled
cadence — unconditionally, which is what keeps the calibration record unbiased (ticket 11); (2)
**precondition-triggered plays** surfaced by the sweep; (3) **event-triggered** re-runs when a material
move lands (ticket 11's event-driven half); (4) **ad-hoc human-posed** scenarios, which are always
admissible but marked as such. Nothing else is speculatively generated.

## RESOLVED (2026-08-05)

**Scenario → Execution → Forecast(s)**: a scenario is a definition, an execution is a run at a point in
time, and one execution emits **multiple differing forecasts** (the ensemble), presented rather than
collapsed. **Scheduled execution of the standing library is the forecast production line.** The engine is
**two composable primitives — time and intervention** — whose compositions give projection, "what if we
act now", the counterfactual, and **the backtest (which therefore needs no separate harness)**; the verbs
turn out to be **Pearl's abduction→action→prediction**. **Rewind has three information regimes**
(as-consumed / as-knowable / with-hindsight) whose gaps **localise the failure** to sensing, interpretation
or the model itself — with only *as-consumed* ever scoring. Opportunity is found by **sweeping the map for
Wardley-play preconditions on schedule**, because **threats push and opportunities must be pulled**.

## Acceptance criteria — all met
- [x] Scenario object defined, incl. references and its relationship to forecasts (three-level model).
- [x] Concrete semantics for fast-forward, rewind and play, each distinguished (two primitives + compositions).
- [x] Where scenarios live + versioning — git-native per ticket 07; an execution pins
      {graph-version, world-model(s), time, information-regime}; branch-per-scenario for exploratory work,
      diffed as map-diffs (research 03).
- [x] How opportunity/gameplay moves are proposed, with the negativity counterweight addressed (push/pull).
- [x] Admissibility rule for the library (preconditions checkable against the map → re-runnable).
- [x] Selection/prioritisation rule (standing library + precondition-triggered + event-triggered + ad-hoc;
      nothing speculatively enumerated).
- [x] Exercised on one fear and one opportunity scenario — *fear:* Intel process-node slip (signal pushes;
      rewind→fast-forward under as-consumed gives the backtest, play adds the foundry-outsourcing
      intervention). *Opportunity:* Netflix ad-tier / password-sharing monetisation as a precondition-
      matched play (adjacent capability owned, component commoditising, no incumbent) — surfaced by the
      sweep, not by an arriving signal.
