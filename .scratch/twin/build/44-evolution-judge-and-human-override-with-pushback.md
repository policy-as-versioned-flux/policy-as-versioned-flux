# 44 — `evolution-judge`, and human override with pushback

**What to build:** Infer a component's evolution position **from accumulated evidence first**, then let a human
correct it — and have the twin **push back** on the override.

The two halves are one contract: a correction is a provenanced claim that is **itself scored**.
Humans get calibrated against evidence too, which is the whole reason inference comes first rather
than starting from opinion.

**Blocked by:** 42, 14

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 11. Spec stories 13, 14.

- [x] Position inferred from accumulated evidence before any human input is accepted.
      `twin/evolution_judge.py::judge()` infers a position from a component's own description
      plus its accumulated bound evidence; `override()` takes that inferred claim as its
      **required first parameter** — there is no way to construct an override without one
      (`tests/test_evolution_judge.py::test_override_requires_the_inferred_position_first`,
      `test_override_has_inferred_as_its_first_parameter`), checked structurally by the harness
      guard so the property holds even if those tests are ever deleted.
- [x] An override is recorded as a provenanced, graded claim attributable to a role.
      `override()` returns a `kind: override` claim at evidence grade 4 — "calibrated expert
      judgement... named by role" is the evidence ladder's own definition of this rung
      (`twin/evidence-ladder.yaml`) — and `twin/schema.py::_refine_claim` refuses a `claimed_by`
      that is not in the registered role set (`twin/roles.yaml`), the same discipline
      `_refine_regrade` already applies to `by_role`
      (`tests/test_evolution_judge.py::test_an_override_claimed_by_an_unregistered_role_is_refused`).
      `signal` moved from required to optional on the claim schema, and `evolution_position`
      joined it, so a position/override claim carries the value it asserts instead of a
      signal id it does not have.
- [x] The twin states its disagreement and its basis when overridden — silence is not an option.
      `pushback()` always returns a populated `statement`, citing the inferred claim's own
      `evidence` on disagreement and saying so explicitly on agreement
      (`tests/test_evolution_judge.py::test_pushback_states_disagreement_and_its_basis`,
      `test_pushback_is_not_silent_on_agreement`), checked live by the harness guard against both
      cases.
- [x] Override accuracy is scored over time on the same footing as the twin's inference.
      No separate scoring path exists: a human override runs through the identical
      `twin/skills.py::evaluate()` call, corpus and threshold `judge()` does — proven by feeding a
      perfect and a careless simulated override through the same harness
      (`tests/test_evolution_judge.py::test_override_accuracy_is_scored_on_the_same_footing_as_the_twins_own_inference`).
      Score-over-time itself (`skills.record_score()`/`detect_regression()`) is unchanged and
      already skill-agnostic (build ticket 42); nothing here needed to touch it.
- [x] Evaluated against dated positions from the public spine.
      `twin/evolution_judge.py::labelled_corpus()` — one dated position per real backtest org
      (Carillion/NMC/Wirecard/Enron, build tickets 38-40), the fixture-author's own grade-4
      Wardley judgement about the industry each org's real, cited signals already describe, built
      fresh from `twin/fixtures.py`'s own builders. Stated limit: the axis moves over years, this
      window is ~1-2, so the corpus tests one dated position per org, not a trajectory.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added
      (`evolution_judge_output_is_graded_by_construction_and_never_silent`,
      `twin/invariants/harness.py`), zero weakened.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/sense-move.yaml` AC3 ("Authored-vs-inferred position decided, consistent
      with ticket 07's authored/derived split.") ticked, evidence citing this module. `sense-move`
      moves from 3/8 to 4/8 checked — still `partial`, not `full`; four ACs remain (observation-
      propagation semantics, weak-signal retention, sensor gameability, and one AC exercised on a
      real co-flagship signal this ticket does not touch — it evaluates against the backtest
      orgs' dated positions, not Netflix/Intel).
