# 52 — The planter/detector/scorer split and actionability horizons

**What to build:** An **enforced** separation between what plants a signal, what detects it, and what scores the
detection — with its limits stated plainly: shared model priors mean synthetic results evidence
**detection mechanics only**, never anticipation of the world.

Every plant carries an **actionability horizon**, so detection after the point of no return scores as
the near-zero option value it actually is. Finding it late is not finding it.

**Blocked by:** 51

**Status:** done (2026-08-13)

**Reading list:** Decision ticket 12. Spec stories 58, 59.

- [x] Planter, detector and scorer cannot share state; the split is structural, not procedural.
      `twin/planter.py`, `twin/detector.py`, `twin/scorer.py` — three separate modules, not three
      functions in one. `planter.plant()` is the only function in the codebase that reads
      `substrate_generator.generate()`'s own `plants` field; it hands a detector only
      `PlantedWorld.public`, the same batch with that field stripped. `twin/detector.py` imports
      nothing naming `planter` — checked by an AST scan of its real source, not a promise in a
      docstring (`tests/test_detector.py::test_detector_module_imports_nothing_naming_planter`,
      harness guard `planter_detector_scorer_are_structurally_separated_and_...`). Checkable, not
      only conventional: `detect()` returns byte-identical output whether or not a caller splices a
      decoy `plants` key into its input
      (`tests/test_detector.py::test_detect_is_indifferent_to_a_spliced_in_ground_truth_key`) — it
      does not even look at the key, so ground truth cannot leak back in even by accident. The
      scorer (`twin/scorer.py`) is the one module allowed to see both, and takes them as two
      independent arguments (`score(ground_truth, detections, detected_at)`), never a merged object
      either side wrote into.
- [x] The shared-prior limitation is published with the results, every time, not in a footnote.
      `planter.SHARED_PRIOR_LIMITATION` states decision ticket 12 Q2's own limit — planter and
      detector are the same model family and share priors, so a synthetic result is never evidence
      the twin anticipates the world, only that the detection machinery works — and
      `scorer.ScoreResult.limitation` carries it verbatim on every result `score()` returns
      (`tests/test_scorer.py::test_every_score_result_carries_the_shared_prior_limitation_verbatim`),
      not stated once in a module docstring a caller of the score would never see.
- [x] Every plant carries an actionability horizon; detection is scored against it.
      `planter.plant(recipe, horizons, ...)` refuses a recipe whose planted signals are not every
      one covered by a declared horizon (`tests/test_planter.py::test_plant_refuses_a_planted_signal_with_no_declared_horizon`),
      so `Plant.actionability_horizon` is never absent by omission. `scorer.score()`'s own
      `detected_at` argument is compared against it directly (day-string comparison, the same
      ordering `regimes.cutoff`/`Spine.at` already use over dated facts elsewhere in this codebase).
- [x] A late detection scores near zero and the scoring makes the reason visible.
      A detection on or before its plant's horizon scores `TIMELY_SCORE` (1.0); the identical
      detection one day after scores `LATE_SCORE` (0.05) — near zero, not zero, because a late
      detection is a post-mortem, not nothing — and `PlantScore.reason` names the horizon and says
      the point of no return has passed
      (`tests/test_scorer.py::test_a_detection_after_the_horizon_scores_near_zero_and_names_the_horizon`).
      A plant never detected scores `MISSED_SCORE` (0.0) and names the miss. The end-to-end
      demonstration lives in the harness guard so it stays part of the permanent suite, not only a
      unit test:
      `planter_detector_scorer_are_structurally_separated_and_late_detection_scores_near_zero`.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added
      (`planter_detector_scorer_are_structurally_separated_and_late_detection_scores_near_zero`),
      zero weakened, zero pinned hashes changed — the guard is new rather than a change to any of
      the sixteen constitution invariants in `twin/invariants/checks.py`, so no manifest re-bless
      was needed. The capability-grade change (below) did move
      `twin/invariants/golden-digests.json`'s committed `capabilities_digest` (every artefact's
      `depth` block digest is global across all capability files) — re-blessed for real via
      `./bin/twin verify --bless-goldens --authorise "decision ticket 12 — build ticket 52
      (planter/detector/scorer split) changes computed artefact bytes"`, not hand-edited.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/synthetic-substrate.yaml` AC 4 ("a blind/adversarial separation mechanism
      between planter and detector") ticks — the split itself is the realisation. `synthetic-substrate`
      moves from 3/7 to 4/7, still `partial` — AC 3 (the planting protocol) stays unticked: the
      actionability horizon supplies its lead-time clause, but "strength" is untouched, so it stays
      on the same "one clause of a multi-clause criterion" ground build tickets 49 and 51 already
      left it on (`tests/test_scorer.py::test_the_synthetic_substrate_capability_grade_moves_to_4_of_7`).

## Built (2026-08-13)

`twin/planter.py`, `twin/detector.py`, `twin/scorer.py`, `tests/test_planter.py`,
`tests/test_detector.py`, `tests/test_scorer.py`, one harness guard
(`planter_detector_scorer_are_structurally_separated_and_late_detection_scores_near_zero`). No new
invariant manifest entry — a harness guard, the same shape build tickets 16, 31, 33, 46, 49–51,
60–62 left behind, not a seventeenth invariant.

- **The split is enforced, not promised.** The planter is the sole reader of ground truth; the
  detector is proven blind both structurally (no import of `twin.planter`) and behaviourally
  (indifferent to a decoy ground-truth key spliced into its own input); the scorer is the only
  module handed both, as two independent arguments.
- **The shared-prior limit (decision ticket 12 Q2) is recorded, not papered over** — published on
  every `ScoreResult`, not left in a docstring.
- **The actionability horizon (Q3b) is a scored property, not only a stated one** — timely
  detection scores full marks, late detection scores near zero with the horizon named in the
  reason, and a miss scores zero and names the miss.
- **Depth grade.** `synthetic-substrate` moves from 3/7 to 4/7 (AC 4). AC 3 stays unticked — the
  horizon covers its lead-time clause, but "strength" has no code behind it yet.
- See "The planter/detector/scorer split, and actionability horizons" in `twin/README.md` for the
  full narration.
