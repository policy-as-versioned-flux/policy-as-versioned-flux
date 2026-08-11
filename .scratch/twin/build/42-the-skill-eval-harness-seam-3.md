# 42 — The skill-eval harness (seam 3)

**What to build:** The six skills are **non-deterministic by construction**, so they cannot be asserted at seam 1 or
seam 2 at all. This harness runs each against a fixture corpus and scores its output against expected
classifications with a **pass threshold, not exact match**.

It also records **score-over-time per skill per model version**, so a model upgrade that degrades
judgement shows up as a regression rather than being discovered inside an artefact months later.
Without this seam, skill regression is the failure most likely to go entirely silent.

**Blocked by:** 03

**Status:** done (2026-08-10)

**Reading list:** Decision ticket 20 (the determinism split). Spec: Testing Decisions, seam 3.

- [x] Harness runs a skill against a fixture corpus and produces a threshold-based pass/fail plus a score.
      `twin/skills.py evaluate()` against the fixture skill `toy-classifier` and its corpus
      (`tests/test_skills.py::test_the_toy_skill_passes_its_own_corpus`,
      `test_a_degraded_skill_fails_the_threshold`, `test_score_is_a_proportion_not_a_raw_count`).
- [x] Score-over-time recorded per skill per model version, and a degradation is surfaced as a regression.
      `tests/test_skills.py::test_recording_and_reading_back_a_score`,
      `test_a_model_upgrade_that_degrades_judgement_is_surfaced_as_a_regression`,
      `test_an_improved_model_is_not_flagged_as_a_regression`.
- [x] Thresholds are versioned; lowering one is a visible, cited change.
      `twin/skill-thresholds.yaml` is versioned; harness guard
      `skill_eval_harness_is_agnostic_and_thresholds_are_guarded` refuses a threshold lowered since
      HEAD with no `authorised_by` citation.
- [x] The harness is skill-agnostic — adding a skill requires a corpus, not harness changes.
      `evaluate()` takes a bare callable and a corpus; no harness function names one of the six real
      skills (`tests/test_skills.py::test_the_harness_is_skill_agnostic`). Exercised against
      `toy-classifier` because a harness tested only against skills that do not exist yet is
      untested — none of the six real skills exist, so this closes the mechanism, not the gap it
      guards (`twin/README.md`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`skill_eval_harness_is_agnostic_and_thresholds_are_guarded`), zero
      weakened. Cites decision ticket 20.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket. `honest-build` (decision ticket 20) AC 1 ("a
      definition of 'skill' for this project") is the closest criterion and stays unchecked: this
      ticket builds the mechanism a skill would run through, not the definition or the inventory —
      `twin/README.md` states the distinction plainly ("this closes the mechanism, not the gap it
      guards"). Landed and ticked nothing.

**Retroactive closure note (build ticket 34).** Built and committed at `ace64f8` ("Build tickets
25, 32, 37, 38, 42, 60 and 62"), but this file's own `Status:` line and checklist were never
updated at the time. Found and closed during the build ticket 34 coherence audit; see ticket 25's
identical note for how.
