# 11 — The sense→move loop: how a signal becomes a movement on the map

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07, 08 (both resolved)

## Question

The engine's heart. Horizon scanning + the Wardley evolution engine are one loop: a signal arrives,
is interpreted *against the model*, and something moves. Pin:

- **What is a signal** — the object: source, date, STEEP class, provenance, and its relation to the
  components it might bear on. What's ingested raw vs what's extracted.
- **The binding step** — how a signal is bound to component(s). Automated classification, judgement,
  or proposal-plus-review? (Research 03: detection automates cheaply; classification stays explainable
  judgement. Hiltunen's "future sign" interpretation dimension is exactly this step.)
- **Authored vs inferred position** — does a signal *edit* a component's evolution coordinate, or is
  position **inferred** from accumulated evidence with the map derived?
- **Propagation** — how a movement travels the dependency graph (and how this differs from ticket 08's
  intervention propagation, which is a `do()` not an observation).
- **Weak-signal handling** — how something too weak to move anything is still retained, and what makes
  it later become significant.
- **Goodhart / gameability** — inherited from ticket 10: sensors that change behaviour once known.
- **Volume** — the weather-forecast frame needs continuous dated forecasts; what cadence does the loop
  run at, and what triggers a re-price?

## Acceptance criteria
- [ ] A signal object defined in ubiquitous language, with provenance + STEEP class.
- [ ] The binding mechanism decided, incl. what is automated vs judged vs reviewed.
- [ ] Authored-vs-inferred position decided, consistent with ticket 07's authored/derived split.
- [ ] Observation-propagation semantics, distinguished from ticket 08's intervention propagation.
- [ ] Weak-signal retention + promotion rule.
- [ ] A stated position on sensor gameability.
- [ ] The loop's cadence + re-price triggers, sufficient to generate forecast volume.
- [ ] Exercised on a real signal for each co-flagship.

## Decided so far (grilling 2026-08-05)

**Q1 — position is INFERRED FIRST, then correctable, with the twin pushing back** (human: *"b, then c —
start with inferred, encourage correction, provide push back"*). Amends ticket 07's authored evolution
coordinate.
The loop: **evidence infers a position → that is the default map → a human may override (authored
correction) → the twin retains its inferred estimate and keeps surfacing the divergence.** Inference
proposes, the human disposes, the twin goes on arguing.
- **Inverts the burden of proof.** The map does not start as an assertion someone must disprove; it
  starts as what the evidence says, and the *human* must justify overriding it. The right stance for a
  system whose value is de-biasing organisational self-image.
- **Correction is encouraged, not merely permitted** — ticket 10's "a thing to argue with", applied to the
  map's own construction.
- **Divergence stays live.** An override does not silence the inferred estimate; the gap is surfaced
  continuously. That gap **is the belief-vs-actual anticipation failure** made first-class in ticket 07
  (Nokia: the map said one thing, the evidence another, the org kept the map).
- **An override is a recorded claim with provenance** — who, when, why, on what basis — so it can be
  **scored later like any other forecast**. Consequence: **humans get calibrated against evidence too**,
  not just the twin. The Nokia failure becomes *measurable* rather than anecdotal.
- Guard retained from the inference side: the evolution axis is an **interpretive judgement about
  ubiquity and certainty, not a measurable quantity** — the inferred estimate must not be presented with
  false precision (track 02's "no arithmetic on ordinal scales"). Inferred position carries its
  uncertainty and its evidence grades.

**Q2 — binding: (a) FULLY AUTOMATED, with spot-checks.** Classifiers/LLMs bind signals to components at
volume; no human gate at ingestion. This works **because the trust machinery is downstream, not at the
gate**:
- An automated binding is **grade 5 (model assertion)** on ticket 08's ladder, so it **cannot price a
  scored forecast** on its own — it informs and ranks, and is use-gated exactly like any other weak-
  evidence claim.
- **Contestable** (ticket 10): "this signal doesn't bear on that component" is a challenge with a
  recorded outcome.
- **Calibrated**: spot-check sampling feeds the calibration record, so binding quality is itself measured
  over time rather than assumed.
- Full automation is what makes the **forecast volume** the weather-forecast frame requires (ticket 08:
  calibration can't be judged from a few dramatic calls).
Rejected: (b) human judgement throughout (cannot keep up, and Q1 already recasts the human's role as
*correction*, not authoring); (c) impact-gated review (a human bottleneck the grading + contestability +
calibration stack makes unnecessary).

**Q3 — unbound signals: (c) RETAIN WITH DECAY, unless something in the graph catches it** (human,
2026-08-05). Decay is the default (bounded pool, bounded noise); a **model change rescues**: adding a
component, dependency or causal edge triggers a **retrospective sweep** of the unbound pool, and a signal
the new structure binds is promoted out and its decay reset.
- Rejected (a) discard: by construction the earliest, weakest signals are exactly the ones that bind to
  nothing *yet* — discarding deletes what the system exists to catch.
- Plain decay alone would preferentially delete the **longest-lead-time** signals (the most valuable
  ones); the rescue path is what fixes that.
- **The model changing re-interprets history.** Add "our authentication depends on this cryptographic
  primitive" and the sweep re-examines every unbound signal against the new structure — surfacing a paper
  from three years ago that now clearly bears on you. **The quantum/HNDL scenario the project started
  from, made mechanical rather than anecdotal.**
- **Free measurement for the backtest:** a dated unbound pool answers *"how long was this sitting there
  before the model caught up?"* — a directly measurable **lead-time-to-recognition**, which is the
  anticipation engine's actual product.
- **Decay half-life is a calibratable knob**, tuned against real lead times from the backtest suite
  ("would a longer half-life have caught this?"), not guessed.

**Q4 — propagation: (b) OBSERVATION and INTERVENTION are DISTINCT operations on the same edges.**
- **Observation** (a signal moved an inferred position) is *evidence*: it updates beliefs **in both
  directions** — a commoditised dependency is evidence about what is built on it, and observing a parent
  is evidence about its children. Reasoning from effect back to cause is *allowed and wanted*.
- **Intervention** (`do(x)`, ticket 08) **severs incoming edges** and propagates **downstream only** — you
  *made* it happen, so it tells you nothing new about its causes.
Conflating them (option a) would quietly corrupt everything: treating "we observed our crypto library
commoditising" as `do(commoditise)` cuts off the backward inference to the **shared cause** that is
probably also moving our other components. Rejected (c) no-propagation: too conservative — it discards
real inferential value and means the map only moves where someone explicitly looked.
This is why ticket 08's `do()` needed separate machinery rather than a special case: **same graph, same
edges, two different rules.**
Intel check: observing the process-node slip is evidence about *upstream* causes (EUV tooling, capital,
yield learning) **and** *downstream* dependents; whereas *deciding* to outsource to TSMC is an
intervention that says nothing new about EUV tooling.

**Q5 — cadence: (c) BOTH — event-driven re-pricing plus SCHEDULED forecast emission.**
The scheduled half is **non-negotiable, for a non-obvious reason: it protects the calibration record from
selection bias.** A twin that forecasts only when something happens — or only when it feels it has
something to say — scores beautifully and means nothing. Weather forecasts are emitted at fixed times
whether or not the weather is interesting, and that is exactly what makes reliability diagrams
meaningful. So: **dated forecasts emitted on a fixed cadence over the same components regardless of
change**, including the boring "no material change expected, 85%" ones — which is also what generates the
**volume** ticket 08 requires.
The event-driven half is responsiveness: a material move should not wait for the scheduled run.
**Machinery inherited, not built:** `/arckit:build --refresh` already does resumable, SHA-256
hash-staleness, DAG-cascading refresh with per-wave commits — the exact shape of a scheduled sweep over a
git-native model (research 04).

## The signal object

**Signal** = `{ source, date-observed, date-published, raw-ref, STEEP class, extracted claim, provenance,
binding(s) → components with evidence grade, decay state }`.
- **Raw ingest vs extraction:** bulk sources live outside git (ticket 07's bulk exception); the
  **extracted, dated, provenanced signal** is what enters the versioned graph.
- **Bindings are grade-5 by default** (automated/model assertion, Q2) and use-gated accordingly.
- **Unbound signals** carry decay state and sit in the pool until rescued by a model change (Q3).

## RESOLVED (2026-08-05)

**Position is inferred first, then correctable, with the twin pushing back** — an override is a
provenanced claim that is itself scored, so **humans get calibrated against evidence too**. **Binding is
fully automated** at volume, trusted not at the gate but downstream (grade-5 + use-gating +
contestability + calibration). **Unbound signals decay unless the graph catches them**, so model change
retroactively re-interprets history and lead-time-to-recognition becomes measurable. **Observation
propagates bidirectionally as belief update, distinct from intervention's downstream-only `do()`** —
same graph, same edges, two rules. **The loop runs event-driven *and* on a schedule**, with scheduled
emission protecting the calibration record from selection bias.

## Acceptance criteria — all met
- [x] Signal object defined in ubiquitous language, with provenance + STEEP class.
- [x] Binding mechanism decided (fully automated; trust machinery downstream).
- [x] Authored-vs-inferred decided — **inferred-first amends ticket 07's authored coordinate**.
- [x] Observation-propagation semantics, explicitly distinguished from intervention propagation.
- [x] Weak-signal retention + promotion rule (decay + graph-catch rescue).
- [x] A stated position on sensor gameability — **deferred with ticket 10's reflexivity decision**; the
      unbound-pool and calibration mechanics are unaffected, but gameable *behavioural* sensors remain a
      known, recorded gap for the ethics/horizon workstream.
- [x] Cadence + re-price triggers, sufficient to generate forecast volume.
- [x] Exercised on a co-flagship signal each (Intel process-node observation propagating bidirectionally;
      the unbound materials-paper → crypto-dependency rescue as the generalised quantum/HNDL case).

## Note, 2026-09-06 (eco-system ticket 93, delegated under ADR-0025): the grade-5 ruling, reopened

Q2 made an automated binding grade 5 -- "it informs and ranks, it cannot price a scored forecast
on its own" -- and Q1 said an inferred position "must not be presented with false precision (no
arithmetic on ordinal scales)". Eco-system ticket 93 builds the thing this ticket's loop was
missing: the twin now DERIVES a probability from bound signals (a model call on the owner's
local clock, ticket 92) instead of reading one from a world model's `beliefs`. The ruling
extends without change to the derivation: it is a model assertion, `evidence_grade: 5`, never
price-eligible, and it carries the weakest grade of the signals it rests on (a comparison, never
arithmetic). What the loop gains is the scoring half Q1 promised for overrides, now for the
twin's own forecast: pre-registered by the date the merge lands it on the adopter's `main`,
scored by `twin/scoring.py` against the overlay's own `outcome` record, with the recorded belief
kept beside the derivation so the disagreement is on the record. The full note is on ADR-0024
point 6 and twin ticket 08.

**Amended 2026-09-09 (eco-system ticket 93 review, F1/F2/F9).** Three corrections to the sentence
above. *Pre-registration* is not "the date the merge lands it on the adopter's `main`" alone: that
measures where a PATH first appeared, and a number rewritten after the answer was already on main
kept the original date and was scored. It is the date of the LAST first-parent write onto
`origin/main`, with the arrival date printed beside it. *The outcome record* is the answer key and
is immutable once it is there -- an outcome edited afterwards is refused by name, and two outcomes
resolving one proposition are refused rather than the first sorted one silently winning. *"It
carries the weakest grade of the signals it rests on"* is, today, a comparison with one value to
compare, because every signal is required to be grade 5; the check prints the count of distinct
grades so the tautology is visible rather than implied.

**Amended 2026-09-09 (eco-system ticket 51, delegated under ADR-0025): what "scored like any other
forecast" can mean for an override.** Q1 says an override "is a recorded claim with provenance ...
so it can be scored later like any other forecast", and that sentence taken literally scores
`|asserted - revealed|` on the evolution axis: arithmetic on an ordinal scale, against an answer
key nobody publishes -- which is the very thing Q1's own guard refuses two paragraphs later, and
which eco-system ticket 93's reopening does not reach (that admits an order statistic over
evidence GRADES and nothing else). So the sentence is sharpened rather than dropped. **An override
is never scored on its coordinate. It is scoreable only THROUGH a falsifiable proposition** -- the
proposition of a scenario in the same overlay that names the component the override moves -- and
an override that reaches no such scenario is `unscoreable` WITH A REASON, twin ticket 08's own
first-class result, never a zero. Q1's promise survives intact where it matters: the human is
still calibrated against evidence, on the same footing as the twin, because the proposition the
override is scored through is the same proposition the twin's own derived probability is scored on.
**And the date is measured, not authored.** An override registers on the LAST first-parent write of
its file onto the adopter's `origin/main` (eco-system ticket 93's `first_reached`, imported and
never re-implemented), so an override whose number is rewritten after it landed is a new claim and
re-registers on the day of the rewrite -- and so does a scenario-library ENTRY, which is the leg
ticket 93 did not have: a question is as rewritable as an answer, and editing a proposition, a
horizon or the words of a question after a forecast is registered against it moves every score
already taken. `verify/twin-evals/verify-scenario-registration.sh` grades both on `origin/main`, and
refuses an entry whose horizon is not strictly after its own `at`, because nothing could ever be
pre-registered against one. **What is graded today is narrower than that paragraph reads** (added
2026-09-09, ticket 51 review F7): the check grades an entry's own registration against its OWN
horizon, and names which of `proposition`, `horizon` and `question` moved when it was rewritten. It
does not yet compare a forecast's registration to the registration of the question it names -- a
question rewritten after it landed but before its horizon PASSes -- because no forecast has reached
any adopter's `origin/main`. That leg becomes measurable on the day the first one merges.
ADR-0024 point 6 and twin ticket 08 carry the rest.
