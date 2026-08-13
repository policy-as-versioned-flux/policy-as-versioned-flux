# 55 — Retrospective sweep and lead-time-to-recognition

**What to build:** A model change triggers a **retrospective sweep** of the unbound pool — and that is what makes
**lead-time-to-recognition measurable**.

This is the quantum / harvest-now-decrypt-later case mechanised: the signal was in the pool for two
years before the graph could interpret it, and that interval is the number that matters.

**Blocked by:** 54

**Status:** done (2026-08-12)

**Reading list:** Decision ticket 11. Spec stories 16, 17.

- [x] A model change triggers a sweep of the pool and rebinds what has become interpretable.
      `twin/retrospective_sweep.py::sweep(overlay, at)` re-examines every entry
      `unbound_pool.pool()` reports — decayed or not — against the overlay's *current* candidate
      components (`twin/ingest.py`'s `candidates_of()`, reused rather than re-derived). A rebind
      is gated on a real score: `signal_classify.best_match()` (new in this ticket) exposes the
      token-overlap score behind `_bind`'s own choice, and a zero score leaves the signal in
      `still_unbound` rather than rubber-stamping it onto whatever candidate sorted first
      (`tests/test_retrospective_sweep.py::test_sweep_leaves_a_signal_unbound_when_nothing_in_the_graph_catches_it`,
      `test_sweep_rebinds_once_a_model_change_adds_a_matching_component`). Decay never blocks
      rescue — the whole point of Q3's rule — proved on the suite's own fixture by harness guard
      `retrospective_sweep_rescues_a_decayed_signal_when_a_model_change_binds_it`, which plants a
      signal 945 days old (past `twin/decay.yaml`'s own threshold) and shows it stays unbound with
      no matching component and rebinds the moment a model change adds one.
- [x] **Lead-time-to-recognition** is computed per rebound signal: pool-entry date to binding date.
      Every rebound entry carries `pool_entry_date` (the signal's own `date`), `binding_date` (the
      sweep's own declared `at`) and `lead_time_to_recognition_days`, the difference between them
      (`test_sweep_rebinds_once_a_model_change_adds_a_matching_component`,
      `test_lead_time_to_recognition_is_reported_per_rebound_signal`).
- [x] The metric is reported as a first-class output, not an internal statistic.
      The emitted `retrospective-sweep` artefact's body carries a top-level
      `lead_time_to_recognition` field — per-signal days plus `min_days`/`max_days`/`mean_days` —
      beside `rebound` and `still_unbound`, not folded into either list for a caller to re-derive
      (`retrospective_sweep.lead_time_summary()`,
      `test_artefact_body_carries_rebound_still_unbound_and_lead_time`,
      `test_the_cli_verb_emits_a_retrospective_sweep_artefact`).
- [x] A worked case demonstrating a multi-year lead time on a real dated signal class.
      `test_worked_case_a_multi_year_old_quantum_signal_is_rescued_by_a_new_crypto_dependency`
      (`tests/test_retrospective_sweep.py`): against the standing scenario library's own
      `quantum-hndl` class (`twin/fixtures.py::build_library_org`, build ticket 69), a
      materials-science signal about a lattice-based cryptanalysis advance, dated 2023-11-02, sits
      unbound and decayed until a new component naming the cryptographic dependency it bears on is
      added — decision ticket 11 Q3's own example made real ("add 'our authentication depends on
      this cryptographic primitive'... surfacing a paper from three years ago that now clearly
      bears on you"). The rescued lead time exceeds two years, asserted rather than eyeballed.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added
      (`retrospective_sweep_rescues_a_decayed_signal_when_a_model_change_binds_it`,
      `twin/invariants/harness.py`), zero weakened, zero pinned hashes changed — the guard is new
      rather than a change to any of the sixteen constitution invariants in
      `twin/invariants/checks.py`, so no manifest re-bless was needed. `signal_classify.py`'s
      `_bind()` was refactored onto a new public `best_match()` without changing its own
      behaviour or `classify()`'s signature (`signal_classify_is_grade_5_by_construction` still
      passes unmodified) — a genuine extension, not a change to any existing check body.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `retrospective_sweep_artefact()` reuses `sense-move`'s existing depth grade
      (`CAPS_RETROSPECTIVE_SWEEP = verbs.CAPS_SENSE`), the same choice build ticket 54's
      `unbound_pool.py` made. `twin/capabilities/sense-move.yaml` AC5 ("Weak-signal retention +
      promotion rule") is now genuinely **checked** — both conjuncts exist together, retention
      from build ticket 54 and promotion here — moving `sense-move` from 5/8 to 6/8, derived by
      `./bin/twin grade` rather than hand-typed. AC5 was the only criterion this ticket's work
      bears on; the other seven, including AC8 ("exercised on a real signal for each
      co-flagship"), are untouched.
