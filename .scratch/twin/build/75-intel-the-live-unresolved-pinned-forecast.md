# 75 — Intel: the live, unresolved, pinned forecast

**What to build:** **The most honest thing in the demo.** A genuine *unresolved* forward forecast — emitted, pinned,
signed — where **we do not know the answer either**.

It cannot be scored yet, and **saying so on screen is the strongest demonstration of the
falsifiability claim**. A dated prediction someone can come back and check beats any
retrospective.

**Blocked by:** 70, 58

**Status:** done — 2026-08-17. `twin/beat-intel.sh`, four ordinary CLI verbs (`fixture`, `sweep`,
`run`, `score`, `verify` twice), no beat-specific code path. `fixtures.build_intel_org` replaces
the walking-skeleton's `example.invalid`-cited toy `intel` overlay with nine real, dated, cited
signals (Intel's own primary releases where one exists, contemporaneous trade-press reporting of
Intel's own dated disclosures otherwise, graded 2 rather than 1 for exactly that reason) spanning
2024-08-01 through 2026-07-23. **No outcome is authored, and none ever will be by this fixture**:
the proposition — does a named external customer commit to Intel's leading-edge foundry node
inside the window Intel's own CEO named on the record (H2 2026 into H1 2027) — genuinely has not
resolved.

**Reading list:** Decision tickets 06, 22. Spec story 92.

- [x] A forward forecast on Intel, pinned and signed before any resolution.
      `twin sweep --repo <intel>` emits a `sweep` artefact carrying the forecast; both it and a
      standalone `twin run` on the same scenario are `derived`, carry pins, and agent-sign —
      `signature_status is None` and `agent_signature` present, `human_involvement.present` false —
      asserted directly on the sidecar rather than inferred from `derived_never_human_signed`
      holding elsewhere (`tests/test_intel_beat.py::test_the_sweep_artefact_is_derived_pinned_and_agent_signed`,
      `::test_the_standalone_run_is_also_signed_and_reproduces_from_its_pins`). The scenario's own
      `at: '2026-08-17'` is today — the forecast is dated now, not backdated for the demo.
- [x] Explicitly unscoreable, and the artefact says so rather than showing a placeholder.
      Read back out of the **emitted forecast bundle's own body** (`scenario.question`), not the
      fixture source or a script's prose — build ticket 74's own review found exactly that gap
      (a caveat that reached a script's `echo` lines and never the artefact) and this ticket tests
      against it directly
      (`tests/test_intel_beat.py::test_the_emitted_body_names_its_own_unscoreability_and_checking_procedure`).
      The absence is structural, not narrated: the `intel` overlay carries zero outcomes, and
      `twin score` against any outcome id refuses and names the absence — the identical refusal
      build ticket 74 demonstrated for Netflix, for a different, stated reason (that story is over;
      this one has not happened yet) — both asserted in
      `::test_no_outcome_is_authored_and_score_refuses_and_names_the_absence` and in the new harness
      guard below.
- [x] The resolution date and the checking procedure are published with it.
      The proposition's own `resolves_on: '2027-06-30'` (`world/propositions/a-leading-edge-
      foundry-node-lands-a-named-external-customer.yaml`) is checked directly
      (`::test_the_proposition_declares_a_resolution_date`), and the scenario's own `question` —
      which flows verbatim into every emitted forecast bundle via `verbs.run`'s existing
      `body.scenario.question` field, with no change to that shared, universal code path — names
      the decision window Intel's own CEO stated on the record (second half of 2026 into first half
      of 2027, signal `tan-14a-customer-guidance-2026-01-23`) and the checking procedure: read
      Intel's own quarterly releases and calls from newsroom.intel.com and SEC EDGAR (the venue
      every signal already cites), author an outcome once Intel discloses a result, run `twin
      score`. Deliberately not wired into `verbs.run`'s per-forecast dict: that dict's digest feeds
      `identical_pins_identical_bytes` for every fixture in this file, and widening it would move
      every golden digest in the repository for one ticket's own narrow claim — the same reasoning
      build ticket 73 gave for keeping Netflix out of the toy fixture.
- [x] It is emitted through the normal scheduled production line, not hand-made for the demo.
      `twin sweep` is `twin/schedule.py`'s own "no human names a scenario" mechanism. The sweep's
      embedded forecast bundle is asserted **byte-identical** to an independently-run standalone
      `twin run` on the same scenario (`digest_of_file`, the same check
      `identical_pins_identical_bytes` makes elsewhere) —
      `::test_the_sweep_embedded_forecast_is_byte_identical_to_a_standalone_run` — so the number the
      demo shows is provably the number the scheduler would have produced with nobody watching, not
      a separately-authored one. The forecast is plural and the two-world-model ensemble genuinely
      disagrees (0.3 vs 0.55), not a single figure dressed as a forecast
      (`::test_the_forecast_is_plural_and_the_ensemble_genuinely_disagrees`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One new harness guard,
      `intel_forecast_is_pinned_signed_and_names_its_own_unscoreability`
      (`twin/invariants/harness.py`), citing decision tickets 06 and 22 in its own docstring. It
      drives `cli.main` throughout (`sweep`, `run`, `score`), the same seam-1 discipline build
      ticket 74's own review established for `netflix_runs_both_paths_and_the_curve_keeps_the_
      disagreement`. Not a constitutional invariant — no `manifest.yaml` entry, no
      `body_sha256`/`checks_module_sha256` to move, the identical shape ticket 74's own new guard
      took. Asserted live against the real fixture in
      `tests/test_intel_beat.py::test_the_new_harness_guard_passes` via `invariants.run(only=[...])`,
      the same pattern `tests/test_scenario_library.py` established.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      Every artefact this ticket emits carries `depth=caps.depth_block(...)` automatically — no
      code change needed, since `verbs.run`/`schedule.sweep` already compute it for every fixture in
      this file — checked in test against `Capabilities.load()` computing the identical block
      rather than merely checked for shape
      (`::test_the_forecast_carries_a_computed_depth_grade`). `twin/capabilities/scenario-engine.yaml`
      criterion 7 and `twin/capabilities/causal-layer.yaml` criterion 5 are each updated to name
      what this ticket landed and what is still missing — see "What this ticket does not close"
      below — rather than left describing a real Intel spine as future work now that one exists.

## What this ticket does not close

**Decision ticket 13 AC 7 (`scenario-engine.yaml` criterion 7) stays unchecked.** It asks for one
fear scenario and one opportunity scenario on each co-flagship. This ticket's own checklist asked
for a forward, unscoreable forecast — a fear scenario — and that is what was built
(`does-the-14a-bet-land-a-named-customer`). No opportunity/gameplay scenario exists on the real
Intel spine: `twin gameplay-sweep` has nothing to pull there, only the toy fixture's
`euv-slip-2026` does, and that one still cites `example.invalid`. Widening this ticket to also
author an opportunity scenario was not asked for and was not done; the capability file names the
gap precisely so a later ticket does not have to rediscover it.

**Decision ticket 08 AC 5 (`causal-layer.yaml` criterion 5) stays unchecked**, for the identical
reason: it asks for a real causal claim from each co-flagship (`euv-delay-slips-the-node`'s own
real-spine equivalent), and this ticket authored a forecast, not a causal edge. `leading-edge-
foundry-node` and `external-foundry-customer-base` carry no `influences` edge between them on the
real spine.

**The evidence grading is honest about its own distance from the primary document.** Six of nine
signals cite contemporaneous trade-press reporting of Intel's own dated disclosure (graded 2)
rather than the primary filing itself (graded 1, the other three — the two quarterly results
releases and the CEO-appointment press release, all read directly from intc.com). Two of the
grade-2 signals — the US government equity stake and the Nvidia investment — do have a primary SEC
8-K on the record; this ticket cites the press coverage it actually read rather than a filing URL
it did not independently render, which is the honest choice between the two, not the maximal one.
