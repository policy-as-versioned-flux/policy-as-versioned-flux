# 88 — Scenario engine: versioning as map-diff, a proof the four-tier selection rule is exhaustive, and Intel's real opportunity scenario

**What to build:** Three gaps closing `scenario-engine` from 4/7 to 7/7.

AC 3's design (scenarios live git-native, branch-per-scenario, diffed as map-diffs) is fully
resolved but has zero code — confirmed by grep across `twin/*.py`, no matches for the diff mechanism
at all. Git already does the versioning; the actual gap is a diff renderer showing two scenario
definitions as a map-diff.

AC 6's design is a closed four-tier selection rule: standing library (scheduled unconditionally),
precondition-triggered sweep, event-triggered, ad-hoc — "nothing else is speculatively generated."
Each tier has its own code (`twin/schedule.py`'s `sweep()`, `twin/gameplay_lens.py`'s `sweep()`,
`twin run`) but nothing composes or proves the four are the complete, non-overlapping set.

AC 7 needs one real fear scenario and one real opportunity scenario exercised on each co-flagship.
Netflix already has both. Intel has only its fear scenario on the real spine
(`does-the-14a-bet-land-a-named-customer`); its opportunity scenario, `euv-slip-2026`, is still a
toy fixture citing `example.invalid`. This is the same underlying real-world fact (an EUV
lithography delay and its downstream process-node effects) that build ticket 81 adds as a causal
edge — this ticket wraps that real edge in a proper opportunity scenario, replacing the toy fixture.

**Blocked by:** 81 (AC 7 needs 81's real Intel EUV-delay causal edge to exist first, so the
opportunity scenario is built on real data rather than duplicating the toy fixture's placeholder)

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 13 (`.scratch/twin/issues/13-scenario-gameplay-engine.md`).
`twin/capabilities/scenario-engine.yaml` for exact AC text and its inline comment on AC 7 (states
this is the sole remaining condition to tick it). `twin/schedule.py`, `twin/gameplay_lens.py`,
`twin/fixtures.py` (`build_intel_org`, the `euv-slip-2026` fixture).

- [x] AC 3 — "Where scenarios live + how they are versioned/diffed." A `twin scenario-diff` command
      or equivalent rendering two scenario definitions as a map-diff, thin given git already
      supplies the storage/versioning half.
      **Closed.** `twin/scenario_diff.py`'s `diff()` takes a scenario id and two git refs — a
      branch-per-scenario pair (research 03), or two commits on one branch — reusing
      `ModelRepo.open(path, ref=...)` unchanged (build ticket 06) rather than building any new
      storage. Reports two legs: a field-level diff of the scenario itself (question, proposition,
      at, horizon, components, world_models — added/removed for the list fields, before/after for
      the scalars) and a map-diff of every component either side's overlay places, reusing
      `Graph.wardley()` (build ticket 14, no separate authoring step) rather than a second
      position model. Wired as `twin scenario-diff` (`twin/cli.py` `cmd_scenario_diff`).
      `tests/test_scenario_diff.py` exercises a real repository with a real `explore` branch: a
      scalar field change and a component's evolution-stage regression are both reported
      (`test_a_scalar_field_change_is_reported_before_after`,
      `test_a_moved_component_appears_in_the_map_diff`), an unchanged field/component is not
      (`test_an_unchanged_field_or_component_is_not_reported`), identical refs diff to nothing
      (`test_identical_refs_diff_to_nothing`), a scenario authored on only one side is reported via
      `scenario_present` rather than refused — mid-flight branch authoring is a real state
      (`test_a_scenario_authored_only_on_one_side_is_reported_not_refused`) — and absence at both
      sides is refused (`test_absent_at_both_sides_is_refused`).
- [x] AC 6 — "A selection/prioritisation rule for which scenarios run (the combinatorics answer)."
      A thin orchestrator or a direct test asserting the four tiers (standing library, precondition-
      triggered, event-triggered, ad-hoc) are the complete, non-overlapping set — that a scenario
      outside all four never runs.
      **Closed with a direct test, not an orchestrator** — the codebase already has no single
      place that "decides" which scenario runs; the four tiers are four different *callers* of two
      primitives, so the honest proof is that nothing else calls either primitive, checked against
      the source directly (`tests/test_scenario_selection_tiers.py`), the same discipline harness
      guard `backtest_is_a_pure_composition` already uses for a CLI command's own structural claim
      (`inspect.getsource`, not the docstring). Exactly two primitives can produce a scenario
      execution or an opportunity anywhere in `twin/*.py` — `verbs.run()` and
      `gameplay_lens.propose()`/`.sweep()` — and every call site of either is one of:
      `schedule.sweep()` (tier 1, standing library, an unconditional loop over every scenario in
      every overlay, no scenario named —
      `test_the_standing_library_names_no_scenario_at_the_call_site`), `gameplay_lens.sweep()`
      (tier 2, precondition-triggered, an unconditional map scan, no component named —
      `test_the_precondition_sweep_names_no_component_at_the_call_site`,
      `test_no_gameplay_opportunity_is_a_scenario_execution_under_another_name`), or
      `cli.cmd_run`/`cli.cmd_backtest` (tiers 3 and 4, event-triggered and ad-hoc, the identical
      call — decision ticket 13 distinguishes the two only by *why* a human or automation invoked
      it, never by a different code path —
      `test_run_and_backtest_are_the_only_human_or_automation_named_entry_points`).
      `reproduce.replay` also calls `verbs.run()`, but originates nothing: `verb` and every flag it
      passes on are read out of an already-emitted artefact's own recorded command, never a fresh
      argument this function exposes
      (`test_reproduce_replay_reads_the_scenario_from_the_recorded_command_not_a_fresh_argument`).
      `test_verbs_run_is_called_only_from_the_named_tiers` and
      `test_gameplay_lens_is_called_only_from_the_named_tier` are the exhaustiveness proof itself:
      a fifth caller anywhere in `twin/*.py` fails the test.
- [x] AC 7 — "Exercised on one fear scenario and one opportunity scenario across the co-flagships."
      Replace the toy `euv-slip-2026` fixture (`example.invalid`) with a real, sourced Intel
      opportunity scenario built on build ticket 81's real EUV-delay causal edge.
      **Closed.** `fixtures.build_intel_org` gains `euv-readiness-wins-the-14a-opportunity` (plus
      its own proposition, `euv-readiness-holds-through-the-14a-go-no-go`, and a belief on it added
      to both existing world models) — build ticket 81's own real, cited EUV causal edge
      (`euv-lithography` -> `leading-edge-foundry-node`), read the upside way: does the subject's
      own High-NA EUV tooling readiness hold through its own named 2026 go/no-go, positioning it to
      win the external customer commitment two prospective customers are already evaluating — the
      reverse of the historical, multi-year lithography-driven slip the same edge's own note cites.
      Checked live rather than assumed to need the pulled shape Netflix's own opportunity took:
      `gameplay_lens.propose()` genuinely finds nothing to pull on this org's overlay (no person
      edges, no component within the product/commodity band), so the opportunity is authored as a
      scenario on the same real edge and world models the fear scenario already uses, not pulled by
      the sweep — named as a real, checked difference from Netflix's shape, not glossed over.
      `twin/beat-intel.sh` steps 3a/3b now run both scenarios standalone and inside `twin sweep`,
      asserting byte-identity and plural, distinct forecasts for each.
      `tests/test_intel_beat.py::test_the_opportunity_scenario_is_framed_as_a_win_not_a_threat`
      (the same threat-word discipline `test_scenario_library.py`'s M&A-framing test uses),
      `::test_the_opportunity_scenario_is_built_on_the_real_euv_edge_not_a_toy_one` (no
      `example.invalid` anywhere in the emitted artefact),
      `::test_the_opportunity_forecast_is_plural_and_the_ensemble_genuinely_disagrees`, and
      `::test_no_outcome_is_authored_for_the_opportunity_scenario_either`. The toy `euv-slip-2026`
      fixture in the walking-skeleton `intel` overlay (`fixtures.build()`, a different function
      from `build_intel_org`) is left untouched — it was never the real spine and this criterion
      never asked for that fixture to change, only for the real spine to stop lacking an
      opportunity side (see "Judgement calls", below).

## Also found and fixed: two-axis review of the diff

Same discipline build tickets 77, 78 and 81 name for themselves: findings recorded and fixed, not
glossed over.

- **Spec/mechanical consequence.** Adding a second scenario to `fixtures.build_intel_org` means
  `twin sweep` over the intel repository now emits **two** clean executions, not one. Two places
  hard-coded "exactly one": the pre-existing harness guard
  `intel_forecast_is_pinned_signed_and_names_its_own_unscoreability`
  (`twin/invariants/harness.py`) and `twin/beat-intel.sh` step 3b's own Python check. Both now
  assert two executions, select the fear scenario's own execution by name (`by_scenario[...]`)
  rather than by list position for the checks that only apply to it, and the beat script gained a
  step 3a exercising the opportunity scenario standalone the same way step 3 already exercises the
  fear one. Found live: `.venv/bin/python -m pytest -q` failed
  `tests/test_intel_beat.py::test_the_new_harness_guard_passes` before this fix, and `bash
  twin/beat-intel.sh` was run directly to confirm the fixed script actually passes end to end, not
  only the harness guard's own in-process copy of the same check.
- **Spec/mechanical consequence.** `tests/test_netflix_beat.py`'s own
  `test_the_scenario_engine_criterion_this_beat_touches_needs_the_other_co_flagship` carried an
  explicit instruction in its own docstring — "Build ticket 75 is expected to tick this and to
  change this test with it; a test that had to be edited is the visible form of that" — naming
  build ticket 75 because AC 7 looked, from build ticket 75's own vantage, like it needed only the
  Intel fear scenario. It did not: AC 7 needed the opportunity half too, which this ticket
  supplies. The test's own docstring and assertion are updated to match, following its own
  instruction rather than leaving it stale.
- **Standards axis.** `tests/test_grades.py`'s two hardcoded assertions of exactly which
  capabilities have earned `full` — the same shape of drift build tickets 78 and 81 each found in
  their own turn — went stale the moment `scenario-engine` reached `full`. Both test names and
  bodies now include `scenario-engine`, the tenth.
- **Standards axis.** `twin/README.md` carried two stale counts unrelated to this ticket's own
  narrow AC text but directly affected by closing it: the "What is honestly built" table's own
  aggregate (61 of 73, nine `full`) and, found while touching that same paragraph, the prose above
  it ("Seven capabilities now reach `full`") had *already* drifted one behind the table's own nine
  `full` rows before this ticket ever touched it — a second, independent staleness bug, not caused
  by this ticket's own change, found and fixed in the same pass rather than left for the next
  ticket to trip over. Both are re-derived live from `./bin/twin grade` (64 of 73, ten `full`) and
  recorded as found, not silently corrected without comment. The top-of-file build-ticket-closed
  banner ("75 of 78") was similarly nine tickets behind the live `grep -l '**Status:** done'` count
  (85 of 92) — the same drift the banner's own parenthetical already says build ticket 77 found
  once before; recomputed live rather than incremented by one on top of a stale base.
- **Standards axis.** `twin/README.md`'s "What is not built" section carried a bullet — "the
  standing scenario set has an admissibility rule now; it still has no selection or prioritisation
  rule" — naming exactly the gap AC 6 closes. Rewritten to state both are closed and to cite the
  new proof, while keeping its still-true half (nothing calls either sweep on a clock yet).

**Judgement calls, considered and left as found:**

- **The toy `euv-slip-2026` fixture (`fixtures.build()`'s `OVERLAY_FILES`) is left untouched,
  `example.invalid` citation and all.** It lives on the walking-skeleton `intel` overlay, a
  different function from `build_intel_org`, and is exercised by other tests
  (`tests/test_refusals.py`, `tests/test_gameplay_lens.py`'s labelled corpus, which explicitly
  relies on this overlay's own `foundry-services` component sitting *below* the land-grab
  threshold as its negative case) for reasons that have nothing to do with decision ticket 13 AC 7.
  The ticket's own text says "replacing the toy fixture" in the sense of replacing what evidences
  AC 7 — build ticket 81's own module comment above `build_intel_org` already draws this exact
  distinction ("Distinct from the toy `intel` overlay in `build()` ... This is the real subject").
  Deleting or rewriting the toy fixture was not this ticket's gap to close and risked breaking
  unrelated coverage for no benefit; left as found, named rather than silently decided.
- **The opportunity scenario is authored, not pulled by `gameplay_lens.sweep()`.** Netflix's own
  opportunity is a `land-grab` the sweep pulls with no human naming a component — the shape
  decision ticket 13's own resolution describes. Checked live rather than assumed: `intel`'s
  overlay (`build_intel_org`) declares no person edges anywhere and every component sits at
  genesis or custom-built, below the land-grab threshold (0.6) and outside the commodity stage
  `exploit-commoditisation` needs — `gameplay_lens.propose()` returns `{"opportunities": []}`
  against it, confirmed by direct call before writing the fixture and pinned as fact in this
  ticket's own capability-yaml evidence and README section rather than left implicit. AC 7's own
  literal text asks only for "one fear scenario and one opportunity scenario," not for the
  Netflix's own mechanism to be replicated; authoring a scenario on the same real edge and world
  models the fear scenario already uses satisfies the literal AC without inventing a person edge
  or an evolution-position claim this org's own real, cited record does not support.
- **`tests/test_scenario_selection_tiers.py` scopes its exhaustiveness claim to `twin/*.py`, not
  `twin/invariants/*.py`.** `twin/invariants/checks.py` and `twin/invariants/harness.py` also call
  `verbs.run()` directly, to construct a scenario execution as an input to checking some other,
  unrelated property (determinism, regime gating) — the test harness exercising a primitive on
  itself, not a fifth way a scenario gets selected to run in the product. Stated in the test
  module's own docstring rather than left as a silent narrowing a reader would have to discover by
  grepping.

## What is honestly true now, and what still isn't

True, and computed rather than asserted: `scenario-engine` is 7/7, `full` (`./bin/twin grade
--capability scenario-engine`, re-run live). AC 3 has real code — a renderer, not new storage —
wired as a CLI command and exercised against a real repository with a real branch. AC 6 is proven
by reading the source directly rather than asserted in prose: every call site of the two
scenario/opportunity-producing primitives across the product surface is accounted for, and a
fifth caller anywhere would fail a test on the next run, not merely disappoint a reviewer reading
a docstring. AC 7's Intel opportunity scenario is real, dated, sourced identically to the fear
scenario beside it, checked live against `gameplay_lens.propose()` rather than assumed to need
that shape, and framed as upside on its own emitted `question` text, not merely by this ticket's
own prose describing it that way.

Still not true, or named as a deliberate limit rather than closed silently: the standing library
still runs on nobody's clock — build ticket 64's own gap, unrelated to and untouched by this
ticket. `twin scenario-diff` diffs one named scenario at a time; it does not enumerate every
scenario that changed between two refs, because AC 3's own text asks for a renderer of "two
scenario definitions," singular, not a repository-wide changelog — a real, narrower scope than a
reader might assume from the word "diff" alone. The four-tier proof is a structural claim about
*this codebase's own source*, not a runtime enforcement mechanism that would stop a future ticket
from adding a fifth caller; it will simply fail the test the moment one is added, which is the
same shape every other harness guard in this project already takes.

## Evidence

```
$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 154 source files

$ .venv/bin/python -m pytest -q
1 failed, 1516 passed in 369.06s (0:06:09)
FAILED tests/test_invariant_suite.py::test_the_suite_is_green — the wrapper around the same two
pre-existing, unrelated invariant failures `twin verify` names below
(drift_window_is_actually_being_sampled, flux_coverage_floor_is_still_reachable); every test this
ticket added or touched (tests/test_scenario_diff.py, tests/test_scenario_selection_tiers.py,
tests/test_intel_beat.py, tests/test_netflix_beat.py, tests/test_grades.py) is in the 1516 passed,
none in the 1 failed.

$ .venv/bin/python -m twin verify --bless-goldens --authorise "decision ticket 13 — build ticket 88
  moves scenario-engine to full 7/7 (the map-diff renderer, the four-tier scenario-selection proof,
  and the real Intel opportunity scenario wrapping build ticket 81's own EUV causal edge), which
  changes every artefact's depth block and capabilities_digest"
golden digests -> golden-digests.json (12 artefacts)

$ .venv/bin/python -m twin verify
RESULT: 69 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: known, pre-existing (build ticket 78's own finding
  stays open; the probe has not been re-armed since)
  FAIL flux_coverage_floor_is_still_reachable: known, pre-existing (see project memory
  "Flux verdict closes unmeasured" — the owner recorded this rather than restarting the probe)
identical_pins_identical_bytes: PASS — 12 artefacts identical across runs, processes, hash seeds
and the re-blessed goldens. This check runs against the default fixture (2 scenarios already,
unaffected by this ticket, whose own change is scoped to `fixtures.build_intel_org` — a different
function); the live proof that the intel repository's own standing library picked up the new
scenario unconditionally is `tests/test_intel_beat.py::test_the_sweep_embedded_forecast_is_byte_identical_to_a_standalone_run`
and harness guard `intel_forecast_is_pinned_signed_and_names_its_own_unscoreability`, both updated
from "exactly one execution" to "exactly two" and both passing above.

$ .venv/bin/python -m twin grade --capability scenario-engine
==> scenario-engine: full  (7/7 of decision ticket 13)

$ .venv/bin/python -m twin grade   (tail)
==> aggregate: 64 of 73 across 13 capabilities, 10 at `full`

$ bash twin/beat-intel.sh
... (full run, exit 0) ...
==> 3b. the sweep and both standalone runs agree byte-for-byte — nothing here was hand-made
  ok   does-the-14a-bet-land-a-named-customer: 2 forecast(s), 2 distinct: [0.3, 0.55]
  ok   euv-readiness-wins-the-14a-opportunity: 2 forecast(s), 2 distinct: [0.5, 0.7]
  ok   sweep-embedded digests == standalone `twin run` digests, both scenarios
...
PASS: swept through the scheduled production line, pinned and agent-signed, reproduced
byte-for-byte through an independent run of the same scenario.
```
