# 22 — Work backwards: the minimal demonstrable slice

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07–15, 18, 20, 21 (all resolved)

## Question

The map's stated final step: with the whole planned, define the **minimal demonstrable slice** and its
acceptance criteria. Ticket 20 already fixes the *build* shape (walking skeleton, scoring in the first
slice); this fixes what the slice must **demonstrate**.

**Constraints inherited:**
- Purpose order: **magnum-opus > product > research > persuasion**. The talk is a byproduct; the demo
  must not become the thing we optimise for (that produced the toy prior).
- Full transparency of method and content is available (public-record spines + synthetic substrate).
- Every capability carries a **depth grade**; the skeleton satisfies a *slice* of each ticket's ACs and
  never redefines them.
- Co-flagships: **Netflix** (retrospective/whole-engine) and **Intel** (live/forward).

**Open:**
- **The thesis** — what single thing must a viewer walk away believing?
- **Which subject + which scenarios** — one flagship or both? which library entries?
- **The honest boundary** — what is shown working vs stubbed vs absent, and how is that surfaced rather
  than hidden (the prior effort's overclaim failure)?
- **What makes it *done*** — acceptance criteria for the slice itself.

## Acceptance criteria
- [ ] A single demonstrable thesis, stated in one sentence.
- [ ] Subject + scenario selection, with rationale.
- [ ] An explicit shown/stubbed/absent boundary and how it is surfaced.
- [ ] Acceptance criteria for the slice, tied back to the owning tickets' criteria.

## Decided so far (grilling 2026-08-05)

**Q1 — thesis: (b) AND (c), SEQUENCED TO CONCLUDE IN (a)** (human, 2026-08-05).
- **Open with (b) — "an organisation's landscape can be modelled, its movements anticipated, and we can
  prove when we're wrong."** The only thesis showable **with evidence rather than assertion**: rewind
  Netflix to a dated past state under the **as-consumed** regime, fast-forward, score against what
  actually happened. The viewer does not have to trust the machinery — they watch it be checked. The
  second clause is the differentiator from every governance tool that ever showed a green tick.
- **Then (c) — "governance can be proportionate and versioned"**, now in its *narrowed, justified* form
  (ticket 18): the enactment channel for machine-enforceable controls **and the verification substrate
  proving a control is in force**.
- **Conclude in (a) — the one-currency cross-domain comparison.** Deliberately **last**: it is the most
  seductive claim and the least defensible standing alone (the £ is model-relative, causally gated,
  constraint-filtered, reported as a curve). Lead with it and the sharpest person in the room rightly
  asks *"where did that number come from?"* — **it is a conclusion the demo earns, not an opening.**
**The order IS the argument: earn credibility, then spend it.**
**Bonus property:** a demo whose thesis is *"we can prove when we're wrong"* **cannot be embarrassed by
showing failures** — the red beat becomes a feature. This is precisely the failure mode the prior effort
hit when it had to soften an overclaim.

**Q1b — FLUX IS A HYPOTHESIS: "integral part/enabler unless we prove otherwise"** (human, 2026-08-05).
Not inherited as true. **The case, now derived rather than assumed:** ticket 18 requires a control to be
**provably in force**, and continuous reconciliation from a **signed, pinned git source** is what makes
that verifiable rather than asserted. Ticket 18's multi-channel enactment sensing then gives Flux a
concrete role: **Flux reconciliation state is a HIGH-GRADE evidence channel** — machine-verified,
continuous, and not a self-declaration — so it raises the corroboration weight that a machine-enforceable
control is actually running.
**The falsification test (must be run, not assumed):** *if the verification substrate can be satisfied by
a signed attestation at deploy time with no continuous reconciliation, then Flux is a convenience, not an
enabler.* Specifically: does anything in the risk basis require **continuous** proof-of-force rather than
point-in-time? Drift between deploys is the candidate answer (a control silently removed after deployment
is exactly the case a point-in-time attestation misses and reconciliation catches) — but that must be
demonstrated, not asserted.

**Q2 — subjects: (c) THREE, each doing an irreplaceable job.**
- **Royal Mail — the falsifiability beat.** Rewind under the **as-consumed** regime, project, score. Chosen
  because **Netflix cannot carry this beat**: its story is famous, so a twin "anticipating" Qwikster or the
  2022 crash is **indistinguishable from reciting it** — the parametric-contamination pillar would
  undermine the very thesis we lead with. Royal Mail is low-contamination and unusually well-instrumented:
  the counterfactual sits **inside its own audited filings** (GLS reported line-by-line in the same
  segmental accounts), with 6+ dated checkpoints including a **legally-liable IPO prospectus forecasting
  the very trend it then underinvested against** (ticket 19).
- **Netflix — the whole-engine beat.** Rich, legible, fear *and* seize on dated evidence, deep behavioural
  substrate to synthesise, quarterly cadence. Carries thesis (c) versioned enactment and the concluding
  (a) cross-domain comparison.
- **Intel — the live forward beat.** Nearly free, and **the most honest thing in the demo**: a genuine
  *unresolved* forecast, emitted, pinned, signed, where **we do not know the answer either**. It cannot be
  scored yet, and **saying so on screen is the strongest demonstration of the falsifiability claim** — a
  dated prediction someone can come back and check beats any retrospective.
**The slice in one line: Royal Mail proves we can be checked. Netflix shows the engine. Intel shows we
will be checked next.**

**Q3 — the honest boundary: (b) DEPTH GRADES ATTACHED TO CAPABILITIES + a published DOES-NOT-DO
register.**
Depth grades (ticket 20) attach to **capabilities, not slides**, so any screen touching a partial
capability **displays that it is partial, automatically**. Honesty becomes **un-forgettable rather than
remembered** — (c) narrated gaps relies on someone remembering, which is exactly what failed in the prior
effort (a "Live" label on a beat that was not live, caught late in adversarial review). **(a) show-only-
what-works is the worst option here:** hiding incomplete parts is *how* overclaim happens, and it directly
contradicts a thesis of *"we can prove when we're wrong."*
**Plus a standing "what this does not do" register — ticket 15's published-scope-exclusions device pointed
at the demo itself.** Same mechanism, second use: built so strategic non-modelling would be visible rather
than deniable, applied here it makes demo omissions visible rather than deniable. **The symmetry is
evidence it is the right primitive.**
**The deep point: with this thesis, incompleteness is ON-MESSAGE.** A demo arguing that governance tools
lie by showing green ticks cannot itself show only green ticks. The red beat, the stub label, the
unscoreable Intel forecast — **each one IS the argument.** The prior effort had to soften an overclaim
because its thesis could not absorb failure; this one cannot be embarrassed by it.

## RESOLVED (2026-08-05)

**Thesis, sequenced:** prove anticipation **and provable falsifiability** (b), then **proportionate
versioned governance in its narrowed, justified form** (c), **concluding in the one-currency cross-domain
comparison** (a) — earned, never opened with. **Three subjects, each irreplaceable:** **Royal Mail** for
the falsifiability beat (low contamination — Netflix's fame would make "anticipation" indistinguishable
from recital), **Netflix** for the whole engine, **Intel** for a live, unresolved, pinned forward forecast
that cannot be scored yet and says so. **Flux is held as an integral enabler *unless proven otherwise*,
with its falsification test recorded.** **The honest boundary is structural**: capability depth grades
travel with the capability, plus a published does-not-do register.

## Acceptance criteria — all met
- [x] A single demonstrable thesis in one sentence — *"we can model an organisation's landscape,
      anticipate its movements, prove when we're wrong, and price the response wherever it lives."*
- [x] Subject + scenario selection with rationale (Royal Mail / Netflix / Intel, contamination-driven).
- [x] An explicit shown/stubbed/absent boundary and how it is surfaced (depth grades + does-not-do register).
- [x] Acceptance criteria for the slice, tied to owning tickets — the slice satisfies a *slice* of each
      resolved ticket's ACs at a declared depth grade, and **never redefines them** (ticket 20's guard).
