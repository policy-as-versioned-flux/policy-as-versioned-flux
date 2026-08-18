# 83 — Twin inside the twin: a threat model, a stated Goodhart position, and named misuse of itself

**What to build:** Three gaps closing `twin-inside-twin` from 2/5 to 5/5, all reusing existing
general-purpose machinery rather than inventing new subsystems — decision ticket 10's own resolution
already committed to depth-1 self-modelling using the same graph and currency the twin uses for
everything else.

AC 2 wants a threat model for the twin itself, priced in the same £ currency as every other
component. `fixtures.py` already carries a `TWIN_SELF_ORG` overlay (build ticket 63); this adds a
scenario/component set of threats to it, priced via the existing `twin/pricing.py` engine — no new
pricing machinery.

AC 4 wants a stated position on Goodhart/reflexivity, including which sensors are most gameable.
This depends on this ticket's sensor table being named first: build ticket 82's `twin/sensors.yaml`
is what makes "which sensors are most gameable" answerable concretely rather than as prose. Reuse
`twin/ethics_gate.py`'s existing gameability-classification machinery against that table.

AC 5 wants named misuse-of-the-twin-itself cases, each with its blocking constraint. The mechanism
already exists and is general-purpose: `twin/misuse.py` (build ticket 62) with
`twin/misuse-catalogue.yaml`, `log_removal()`, `compute_attractiveness()`. Nothing in that catalogue
today is scoped to misuse of the twin itself (as opposed to misuse of an org being modelled) — this
ticket adds those cases to the existing catalogue, it does not build a third catalogue file.

**Blocked by:** 82 (AC 4 needs 82's named sensor table to state which sensors are most gameable
against something concrete)

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 10 (`.scratch/twin/issues/10-twin-inside-twin.md`).
`twin/capabilities/twin-inside-twin.yaml` for exact AC text. `twin/fixtures.py` (`TWIN_SELF_ORG`),
`twin/pricing.py`, `twin/ethics_gate.py`, `twin/misuse.py`, `twin/misuse-catalogue.yaml`.

- [x] AC 2 — "A threat model for the twin, with controls priced in the same currency." A scenario/
      component set of threats to the twin itself on `TWIN_SELF_ORG`, priced through the ordinary
      `twin/pricing.py` path — no bespoke pricing. **Closed:** `twin/fixtures.py`
      `_TWIN_SELF_OVERLAY` gains a third component, `the-twin-analytical-surface` (the graph data,
      evidence claims, pricing rules and sensor inputs), targeted by decision ticket 10's own named
      threats (exfiltration, model extraction, sensor poisoning) via a causal edge honestly graded 3
      (literature/domain theory — Tramér et al. 2016, "Stealing Machine Learning Models via
      Prediction APIs"; Biggio & Roli 2018, "Wild Patterns"). The impact stays an unpriced register
      entry (grade 3 is outside `evidence-ladder.yaml`'s `pricing_threshold: 2`) — no fabricated
      number — while its two controls (`restrict-and-log-query-access-to-the-priced-output`,
      `attest-provenance-on-every-signal-before-admission`) price through the unmodified
      `twin/pricing.py` + `twin/options.py` path in the same £ PERT currency. Cited:
      `tests/test_twin_inside_twin.py::test_the_threat_controls_are_priced_in_the_ordinary_currency_even_though_the_impact_is_not`.
- [x] AC 4 — "A stated position on Goodhart/reflexivity, incl. which sensors are most gameable." A
      written position (a doc or a derived artefact), plus a gameability field or classification run
      against build ticket 82's `twin/sensors.yaml` table using `ethics_gate.py`'s existing ladder
      machinery. **Closed:** decision ticket 10 Q4 already stated the position in prose; this ticket
      adds `twin/ethics_gate.py::classify_named_sensors()`, which runs the module's own existing
      `classify_gameability()` against every row of `sensors.yaml` — no new classifier. Only
      `bus-factor-structural-aggregate` classifies `goodhart-proof`; the other five (every
      behavioural/individual sensor) classify `marked`, the safe default, and are the most gameable
      of the named set. Written position: see `twin/README.md`, "The threat model, the Goodhart
      classification, and misuse of the twin itself". Cited:
      `tests/test_twin_inside_twin.py::test_the_named_sensor_table_is_classified_and_most_of_it_is_marked_gameable`.
- [x] AC 5 — "Named misuse cases with the constraint that blocks each." Add cases to the existing
      `twin/misuse-catalogue.yaml` / `twin/misuse.py` mechanism scoped to misuse *of the twin by its
      own operator* (e.g. selectively citing forecasts, gaming a sensor's metric), each with its
      blocking constraint — do not duplicate build ticket 62's machinery, extend its data.
      **Closed:** three entries added to `twin/misuse-catalogue.yaml` (v1 -> v2), loaded through the
      existing `twin/misuse.py::load_catalogue()` — no second catalogue file:
      `selectively-cites-the-twins-own-forecast-to-win-an-argument-about-it`,
      `games-a-sensor-about-the-twins-own-operation-to-look-healthier-than-it-is`,
      `treats-the-twins-own-priced-figure-as-a-binding-instruction`, each naming the real mechanism
      that blocks it (`twin/positions.py`, `twin/ethics_gate.py`, invariant
      `no_recommended_action_field` / `twin/tradeoff.py`). No id or subject overlap with build
      ticket 62's original six entries or build ticket 82's `behavioural-misuse-catalogue.yaml`.
      Cited: `tests/test_twin_inside_twin.py::test_misuse_of_the_twin_itself_is_named_with_a_mechanism_each`.

`twin-inside-twin` moves from `partial` (2/5) to `full` (5/5) at this ticket.

## What still isn't true

Nothing was left honestly unclosed on this ticket's own three ACs — all three tick with real
citations. Two scope limits from decision ticket 10 itself remain exactly as recorded there and are
not this ticket's job to revisit: reflexivity is still **accepted as noise, deliberately** (Q4) —
this ticket backs the *gameability* half of that position with a live classification, but does not
build the deferred self-attribution/intervention-as-graph-event modelling Q4 itself named as future
work; and the depth-1 bound (Q1) is unchanged — `the-twin-analytical-surface` is a third ordinary
component, not a second layer of self-modelling.

## Judgement calls made, named rather than silent

- **AC 2's impact edge is graded 3, not 2 — honestly, not for lack of trying.** A real cross-
  organisation, repeated-instance citation for "compromise of a decision-support instrument damages
  its own adoption" does not exist in the public literature the way Cowgill & Zitzewitz's corporate-
  prediction-market study does for the adoption edge itself. Tramér et al. and Biggio & Roli are real
  and directly on point for the *mechanisms* (extraction, poisoning), but neither measures the effect
  on an instrument's adoption, so grade 3 (literature/domain theory) is the honest ceiling, and the
  impact is an unpriced register entry rather than a fabricated grade-2 number. The AC's own words —
  "controls priced in the same currency" — are satisfied regardless: a response's £ cost samples
  independent of whether the shock it addresses ever prices (`twin/pricing.py`'s own docstring makes
  this explicit), so both controls price while the shock stays a register entry. Not changed.
- **AC 2's three named threats (exfiltration, model extraction, sensor poisoning) share one
  component and one edge, not three.** The depth-1 bound this ticket inherits is about
  self-reference, not about how finely one asset's own attack surface is sliced, and a threat model
  does not need a component per attack mode to be a real threat model. Not changed.
- **AC 4's "written position" is a README section plus a docstring, not a new markdown artefact.**
  Decision ticket 10 Q4 already wrote the prose position; ethics-gate AC 3's precedent (its own
  Goodhart position lives in code comments + `twin/README.md`, not a standalone doc) is the pattern
  followed here, so the position and the classification that backs it sit together rather than in a
  third location a reader would have to cross-reference. Not changed.
- **AC 5's scope (misuse of the twin by its own operator, not of behavioural sensing or of the
  twin's general machinery) follows the ticket's own examples verbatim** — selectively citing
  forecasts, gaming a sensor's metric — plus a third case (treating a priced figure as a mandate)
  that is the same shape decision ticket 10 Q3's advisory-vs-binding question already named. Three
  named cases, each with a real, checkable mechanism, is read as satisfying "named misuse cases"
  (plural, no stated count) rather than needing a fourth or fifth to pad the number. Not changed.
- **The top-of-file build-ticket-closed banner (`twin/README.md` line 10, "75 of 78 build tickets
  closed") is stale independent of this ticket** — live recount finds 92 ticket files (00-91), 82
  already `**Status:** done` before this ticket (83 makes 83), and several beyond 78 (79-91) exist.
  This predates this ticket's own change and fixing it needs a full-repo status audit, not a
  targeted capability closure — left alone rather than scope-creeping into an unrelated cleanup, and
  named here explicitly rather than silently.

## Also found and fixed

- **The world-layer proposition id was 68 characters and `schema.py`'s `IDENT` regex caps identifiers
  at 64.** `twin validate` caught it immediately on the first live run; shortened to
  `a-decision-support-instruments-model-or-data-is-compromised` (59 chars), text unchanged.
- **Adding two new responses to `TWIN_SELF_ORG` changed what two existing build-ticket-63 tests
  asserted about the whole overlay's priced response set**, because `twin/verbs.py::price()` and
  `options()` both price every response in the overlay regardless of the shock's origin —
  `test_adoption_has_priced_responses_not_just_a_narrative_note` and
  `test_adoption_responses_also_price_through_the_options_prefilter` hard-coded a 2-response set and
  would have failed as false negatives. Updated to a subset check and a corrected total of 4,
  with a comment naming why.
- **`test_the_twin_appears_as_ordinary_components_in_its_own_graph` and the propagate-reachability
  test in the same file** hard-coded the two-component, one-reached-component shape from build
  ticket 63; both now include `the-twin-analytical-surface` and its real reach (adoption directly,
  the-twin-model at depth 2 through the pre-existing cycle).
- **`tests/test_grades.py`'s two long-named `full`-capability-set tests** did not know about
  `twin-inside-twin` moving to `full`; renamed both (matching the exact rename build ticket 81 did
  for `causal-layer`) and added the capability to both the docstring and the asserted set.
- **`twin/invariants/golden-digests.json` needed re-blessing.** Every emitted artefact's `tool` pin
  carries `capabilities_digest`, which changed the moment `twin/capabilities/twin-inside-twin.yaml`'s
  content changed — `test_artefacts_match_the_committed_golden_digests` failed until
  `twin verify --bless-goldens --authorise "decision ticket 10 — build ticket 83 ..."` re-recorded it,
  the same step build ticket 82's own commit message names taking for the identical reason.

## Evidence

`.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:

    Success: no issues found in 151 source files

`.venv/bin/python -m pytest -q` (full suite, after this ticket's changes):

    1 failed, 1496 passed in 427.77s (0:07:07)
    FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionError: [...
    'drift_window_is_actually_being_sampled: the window is open and the newest sample is 5 day(s)
    old ...']

The one failure is the pre-existing, clock-bound `drift_window_is_actually_being_sampled` finding
(build ticket 65/70's own recorded, deliberately-red probe — see the memory note "Flux verdict
closes unmeasured"), unrelated to this ticket and present before it. Zero new failures.

`.venv/bin/python -m twin verify`:

    RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
      FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5
      day(s) old (2026-08-13T02:53:15+00:00) ...
      FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no
      longer be reached ... **This guard staying red is the finding, not a defect in it**

Both failures are the same pre-existing, clock-bound pair. `twin_self_reference_is_cut_not_recursed`
(guard 53) passes — the new `the-twin-analytical-surface` component does not disturb the depth-1
self-reference cycle build ticket 63 closed.

`./bin/twin grade` (aggregate, after this ticket):

    ==> aggregate: 60 of 73 across 13 capabilities, 8 at `full`

`twin-inside-twin` reports `full` (5/5), up from `partial` (2/5).
