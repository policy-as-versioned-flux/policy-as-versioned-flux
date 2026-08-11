# 43 — `signal-classify`

**What to build:** STEEP-tag a dated signal and **bind it to the components it touches**. The judgement that turns a
line in a trend deck into a specific consequence for *this* organisation.

A grade-5 claim by construction, which is exactly why it is a skill and not code.

**Blocked by:** 42, 12

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 11. Spec stories 12, 15.

- [x] Skill produces STEEP tag plus binding targets, output as a graded claim file.
      `twin/signal_classify.py::classify()` returns `{"steep": ..., "claim": {"kind": "binding",
      "component", "evidence_grade", "claimed_by", "evidence"}}` — two schema-relevant halves
      rather than one flat dict, because `steep` belongs on a `signal` document and the rest on a
      `claim` (`twin/schema.py`); the `claim` half becomes a genuine `schema.SCHEMAS["claim"]`
      document once a caller adds the `id`/`signal` only it knows
      (`tests/test_signal_classify.py::test_the_claim_half_conforms_to_the_claim_schema_once_id_and_signal_are_added`).
      The heuristic is a keyword/word-overlap stand-in for a real model call, honestly proven only
      against `political` and `economic` signals — the only two the committed fixtures carry.
- [x] Evaluated against a **labelled signal corpus** with a declared pass threshold.
      `twin/skills.py::evaluate("signal-classify", classify, corpus, scorer=scorer)` against
      `twin/skill-thresholds.yaml`'s `signal-classify: 0.8` entry
      (`tests/test_signal_classify.py::test_signal_classify_passes_its_own_labelled_corpus`, and
      `test_a_degraded_classifier_fails_the_threshold` proves the threshold actually gates).
- [x] The labelled corpus is the boundary fixture the sensing track consumes.
      `twin/signal_classify.py::labelled_corpus()` builds the four backtest orgs
      (Carillion/NMC/Wirecard/Enron, build tickets 38-40) fresh via `twin/fixtures.py`'s own
      builders and reads their committed signals/claims back through `Overlay` — generated in CI,
      never fossilised, per `00-constitution.md`'s "boundary fixtures" section, which already
      names this fixture as "(43)".
- [x] Output is grade 5 by construction and cannot self-assert a higher grade.
      `classify()`'s signature is `classify(payload)` — no grade-shaped parameter exists to call it
      with, and `evidence_grade` is a literal `5` in the return
      (`tests/test_signal_classify.py::test_classify_has_no_parameter_that_can_set_a_different_grade`),
      checked structurally by harness guard `signal_classify_is_grade_5_by_construction` so the
      property holds even if that unit test is ever deleted.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`signal_classify_is_grade_5_by_construction`,
      `twin/invariants/harness.py`), zero weakened. Re-blessed golden digests
      (`--authorise "decision ticket 11 — ..."`), since the AC2 tick below moves
      `capabilities_digest`, which every artefact's pins carry.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/sense-move.yaml` AC2 ("The binding mechanism decided, incl. what is
      automated vs judged vs reviewed.") ticked, evidence citing this module and the harness guard.
      `sense-move` moves from 2/8 to 3/8 checked — still `partial`, not `full`; six ACs remain
      (authored-vs-inferred position, observation-propagation semantics, weak-signal retention,
      gameability, and one exercised-on-a-real-signal AC this ticket does not touch).
