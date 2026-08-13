# 51 — The substrate eval suite: fidelity measured, not asserted

**What to build:** **Fidelity is defined and tuned by measurement.** Signal-to-noise, plant difficulty, spine
consistency, reporting asymmetry, mundanity — each a metric with a target.

The record's **negativity bias** is modelled deliberately here rather than as a separate concern:
reporting asymmetry as measured and negativity bias as produced are the same asymmetry, and
separating them would have had two tickets fighting over one property.

**Blocked by:** 50

**Status:** done (2026-08-12)

**Reading list:** Decision ticket 12. Spec stories 56, 60.

- [x] Each fidelity dimension is a computed metric with a declared target and a current value.
      `twin/substrate_eval.py`'s `FidelityMetric` + `TARGETS` + `evaluate_fidelity()`: five named
      dimensions (`signal_to_noise`, `plant_difficulty`, `spine_consistency`,
      `reporting_asymmetry`, `mundanity`), each a real value computed from a generated batch's own
      content against its own declared `(target_low, target_high)` band — no manual eyeball,
      checked against real output in `tests/test_substrate_eval.py::test_evaluate_fidelity_returns_five_named_dimensions_with_targets_and_values`.
- [x] Tuning the generator against the targets is a supported loop, not a manual eyeball.
      `tune()` is a real, iterative loop: a balanced 50/50 negative/positive template mix
      genuinely misses `reporting_asymmetry` (0.586 against a 0.6 floor —
      `test_a_balanced_starting_pool_genuinely_misses_the_reporting_asymmetry_target`), and the
      loop raises the mix's negative fraction step by step, converging in more than one iteration
      to a batch clearing every band at once (`test_tune_converges_over_more_than_one_iteration`).
      Deterministic given identical inputs (`test_tune_is_deterministic_given_identical_inputs`)
      and honestly reports `converged=False` when the budget is too small
      (`test_tune_reports_not_converged_when_the_budget_is_too_small`).
- [x] Negativity bias is a measured, targeted property of the substrate — the record's real asymmetry, reproduced rather than idealised away.
      One metric, not two: `reporting_asymmetry()` is both AC's mechanism (decision ticket 12
      Q3c — "reporting asymmetry as measured and negativity bias as produced are the same
      asymmetry"). The generator's own committed mundane templates (ticket 49) carry no polarity
      vocabulary at all, so an unmixed batch measures `0.0` — a real, honest gap, not a strawman
      (`test_a_purely_neutral_batch_measures_zero_reporting_asymmetry`). The tuned batch's own
      value sits above 0.5, matching the record's real skew rather than an arbitrary balanced band
      (`test_the_tuned_batchs_asymmetry_skews_negative_matching_the_records_real_bias`).
- [x] The suite is the acceptance test for ticket 49's depth grade.
      Harness guard `substrate_fidelity_is_measured_and_tuning_closes_a_real_gap`
      (`twin/invariants/harness.py`) runs `substrate_generator.generate()` — ticket 49's own,
      unmodified — end to end through `evaluate_fidelity()`: a properly tuned recipe's real output
      clears every declared band at once, and a degraded batch (balanced polarity, un-camouflaged
      plant wording) fails more than one dimension simultaneously
      (`test_a_degraded_batch_fails_the_full_fidelity_suite`) — a harness with no subject proves
      nothing.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`substrate_fidelity_is_measured_and_tuning_closes_a_real_gap`),
      zero weakened, zero pinned hashes changed — the guard is new rather than a change to any of
      the sixteen constitution invariants in `twin/invariants/checks.py`, so no manifest re-bless
      was needed. The capability-grade change (below) did move `twin/invariants/golden-digests.json`'s
      committed artefact digests (every artefact's `depth` block carries `Capabilities.digest`,
      which is global across all capability files) — re-blessed for real via `./bin/twin verify
      --bless-goldens --authorise "decision ticket 12 — build ticket 51 (substrate eval suite)
      changes computed artefact bytes"`, not hand-edited.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/synthetic-substrate.yaml` AC 2 ("A fidelity target + a stated list of
      what would make the substrate an unfair test") ticks — the eval suite itself is the
      realisation: `TARGETS` is the fidelity target, `UNFAIR_TEST_CONDITIONS` is the stated list
      (matching decision ticket 12's own five failure modes, each demonstrated failing its own
      dimension on a real batch in `tests/test_substrate_eval.py`). `synthetic-substrate` moves
      from 2/7 to 3/7, still `partial` — AC 3's strength and lead-time clauses (decision ticket
      12's own planting protocol) are not this ticket's: only the distribution-of-difficulty
      clause (`plant_difficulty`) has code behind it, so AC 3 stays unticked on the same "one
      clause of a multi-clause criterion" ground build ticket 49 already left it on
      (`test_the_synthetic_substrate_capability_grade_moves_to_3_of_7`).
