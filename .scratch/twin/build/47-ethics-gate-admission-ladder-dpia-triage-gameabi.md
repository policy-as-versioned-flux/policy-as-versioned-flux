# 47 — `ethics-gate`: admission ladder, DPIA triage, gameability, and fast improvement

**What to build:** Walk the sensor admission ladder — **purpose, then necessity, then proportionality** — so adding a
sensor is a decision with a recorded justification rather than a default.

Carries the doctrine **"model the mechanism universally, sense sparingly"**: mechanisms live in the
world layer, observations in the overlay, which is what stops total-scope ambition and data
minimisation being in conflict.

Two further judgements land here: **gameability marking**, with sensors preferred where gaming the
metric *is* the desired behaviour and marked where it is not; and **fast improvement as grounds for
suspicion but never a verdict**, so a genuine improvement is not punished.

**Blocked by:** 42

**Status:** done (2026-08-12)

**Reading list:** Decision ticket 15; research 05 (insider ethics). Spec stories 65, 66, 67, 68.

- [x] Ladder walked in order with a recorded justification per rung; failing a rung stops the process.
      `twin/ethics_gate.py::walk_ladder()` — purpose, then necessity, then proportionality, in that
      order, and a failing rung breaks the loop before the next rung's check function is even
      called (`tests/test_ethics_gate.py::test_walk_ladder_stops_at_purpose_and_never_evaluates_the_rest`,
      `test_walk_ladder_stops_at_necessity_when_a_less_intrusive_alternative_exists`,
      `test_walk_ladder_stops_at_proportionality_when_intrusion_outweighs_value`). Every evaluated
      rung carries a non-empty `justification`
      (`tests/test_ethics_gate.py::test_walk_ladder_admits_when_every_rung_passes`). Harness guard
      `ethics_gate_ladder_stops_early_and_fast_improvement_is_never_an_automatic_finding` proves the
      stop structurally, by handing the later rungs a payload that would raise if ever read.
- [x] DPIA triage identifies when a DPIA is mandatory under UK GDPR / DPA 2018 / the ICO 2023 monitoring guidance.
      `twin/ethics_gate.py::dpia_triage()` — the ICO's own 2023 monitoring-guidance triggers
      (research 05 Part B.2): email/message, keystroke, biometric monitoring, profiling, or a risk
      of financial loss to the worker (`tests/test_ethics_gate.py::test_dpia_triage_flags_keystroke_monitoring_as_mandatory`,
      `test_dpia_triage_flags_profiling_as_mandatory_with_no_channel`,
      `test_dpia_triage_is_not_mandatory_when_nothing_triggers_it`). `admit()` combines the triage
      with the ladder into the operational gate: admission needs the ladder to pass **and** any
      mandatory DPIA recorded complete
      (`tests/test_ethics_gate.py::test_admit_refuses_when_dpia_mandatory_and_not_complete_even_though_ladder_passes`).
- [x] Every sensor carries a gameability marking, and the preference rule is applied and recorded.
      `twin/ethics_gate.py::classify_gameability()` marks `goodhart-proof` only on positive
      evidence that gaming the metric requires doing the genuinely desired thing, defaulting to
      `marked` otherwise (`tests/test_ethics_gate.py::test_classify_gameability_marks_a_bus_factor_metric_as_goodhart_proof`,
      `test_classify_gameability_marks_a_commit_count_metric_as_marked_by_default`); `prefer()`
      applies that as a preference rule across candidates and records which it chose and why
      (`test_prefer_prefers_the_goodhart_proof_candidate_among_several`,
      `test_prefer_names_no_preference_when_no_candidate_is_goodhart_proof`).
- [x] Fast improvement raises a flag with a required human adjudication, never an automatic adverse finding.
      `twin/ethics_gate.py::flag_fast_improvement()` never carries an action- or verdict-shaped
      field — checked against the same banned-word/phrase lists `no_recommended_action_field` runs
      (`tests/test_ethics_gate.py::test_flag_fast_improvement_output_carries_no_action_or_verdict_shaped_field`).
      `adjudicate_fast_improvement()` is the only way a flag becomes an actual finding: it refuses
      to run against a flag that was never raised and refuses a role the register does not carry
      (`test_adjudicate_fast_improvement_requires_a_raised_flag`,
      `test_adjudicate_fast_improvement_requires_a_registered_role`). Harness guard
      `ethics_gate_ladder_stops_early_and_fast_improvement_is_never_an_automatic_finding` carries
      all of this into the permanent suite.
- [x] Evaluated against sensor proposals with known ladder outcomes.
      `twin/ethics_gate.py::labelled_corpus()` — five hand-authored sensor proposals spanning every
      way the ladder can stop (purpose, necessity, proportionality) plus admission and the
      DPIA-gated refusal, evaluated through `twin/skills.py::evaluate()` exactly as the other five
      skills are (`tests/test_ethics_gate.py::test_ethics_gate_passes_its_own_labelled_corpus`,
      `test_a_degraded_gate_fails_the_threshold`). No sensor fixture exists in `twin/fixtures.py`
      to derive this from — decision ticket 15's own resolution carries the sensor set itself
      forward as a build-time artefact — so this corpus is hand-authored, the stated limit named in
      the module docstring.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added
      (`ethics_gate_ladder_stops_early_and_fast_improvement_is_never_an_automatic_finding`,
      `twin/invariants/harness.py`), zero weakened, zero manifest hashes touched — the guard lives
      outside `twin/invariants/checks.py`, so `checks_module_sha256` does not move. Golden digests
      re-blessed once, because every artefact's `capabilities_digest` pin moved when
      `twin/capabilities/ethics-gate.yaml` was added and `twin/capabilities/sense-move.yaml` was
      extended — authorised: "decision ticket 15 — build ticket 47 (ethics-gate) changes computed
      artefact bytes".
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/ethics-gate.yaml` — decision ticket 15 had **no capability file at all**
      before this ticket (build ticket 61 found the gap and declined to fill it with an empty one).
      Ticks AC 1 (the admission rule), AC 3 (the Goodhart position) and AC 5 (the operational gate
      mechanism); AC 2 (the sensor set itself) and AC 4 (a named misuse catalogue matching decision
      ticket 15's own Q3/Q3b table — distinct from build ticket 62's governance-misuse catalogue)
      stay open, named as such rather than silently claimed. `ethics-gate` grades `partial` at
      3/5 — never `full`. The same code also ticks `twin/capabilities/sense-move.yaml` AC 6 ("a
      stated position on sensor gameability", decision ticket 11), moving that capability from 4/8
      to 5/8: sensor gameability is the genuine overlap between sensing and its ethics gate, so one
      module answers both capabilities' own criteria.
