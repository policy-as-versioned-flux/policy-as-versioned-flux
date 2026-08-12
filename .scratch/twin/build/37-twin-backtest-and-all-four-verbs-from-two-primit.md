# 37 — `twin backtest`, and all four verbs from two primitives

**What to build:** Backtest is **rewind plus projection scored against the record** — deliberately not a separate
harness, because a second harness is a second implementation of the same thing and it would drift.

The spec claims all four operations fall out of exactly two primitives. That claim is untested until
someone demonstrates it, so this ticket demonstrates all four: projection (time-forward), act-now
(intervention-at-present), counterfactual (rewind + intervention), backtest (rewind + projection).

**Blocked by:** 36

**Status:** done (2026-08-10)

**Reading list:** Decision ticket 13. Spec stories 35, 38.

- [x] Backtest implemented purely as a composition of rewind and projection, with no backtest-specific code path.
      `cmd_backtest` (`twin/cli.py`) calls exactly `primitives.rewind` then `verbs.run`, checked
      against its own source by harness guard `backtest_is_a_pure_composition` rather than trusted
      from a docstring.
- [x] All four operations demonstrated as compositions of the same two primitives.
      `tests/test_four_verbs.py`: `test_projection_is_run_with_no_intervention` (fast-forward),
      `test_act_now_is_intervene_with_no_rewind`, `test_counterfactual_is_rewind_then_intervene`,
      `test_backtest_is_rewind_then_run`.
- [x] A test asserting no separate backtest harness exists — the composition is the implementation.
      `tests/test_four_verbs.py::test_backtest_composes_no_separate_code_path`, and
      `test_backtest_and_run_compute_the_identical_forecast` shows the composition and `run()`'s
      own internal `as-consumed` rewind reach a byte-identical forecast.
- [x] Backtest emits scoring-eligible forecasts only under `as-consumed`.
      `tests/test_four_verbs.py::test_backtest_is_not_scoring_eligible_under_a_non_scoring_regime`.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`backtest_is_a_pure_composition`), zero weakened. Cites decision
      ticket 13.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `scenario-engine` (decision ticket 13) AC 2, "concrete semantics for fast-forward, rewind and
      play, each distinguished," ticks against this ticket's evidence
      (`twin/capabilities/scenario-engine.yaml`), moving the capability to 2/7 — already reflected
      in `twin/README.md`'s honest-build table, computed by `twin/grades.py`, never typed.

**Retroactive closure note (build ticket 34).** Built and committed at `ace64f8` ("Build tickets
25, 32, 37, 38, 42, 60 and 62"), but this file's own `Status:` line and checklist were never
updated at the time. Found and closed during the build ticket 34 coherence audit; see ticket 25's
identical note for how.
