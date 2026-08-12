# 54 — The decaying unbound signal pool

**What to build:** Signals the graph cannot yet interpret are **retained in a decaying pool** rather than discarded. A
signal the model could not interpret today is not the same as a signal that does not matter.

**Blocked by:** 53

**Status:** done (2026-08-12)

**Reading list:** Decision ticket 11. Spec story 16.

- [x] Unbound signals are retained with a decay function, not dropped.
      `twin/unbound_pool.py::unbound_ids()` reads every signal in an org's overlay carrying no
      `binding` claim — the exact complement of what `twin/verbs.py`'s `sense()` refuses
      (`tests/test_unbound_pool.py::test_unbound_ids_includes_a_signal_with_no_binding_claim`).
      Nothing here deletes a committed signal file; `pool()` computes a weight from the published
      decay function and reports it, decayed or not
      (`test_pool_retains_a_signal_that_has_decayed_rather_than_dropping_it`).
- [x] The decay function is a versioned, published parameter.
      `twin/decay.yaml` (`schema: twin.decay/v1`), read and validated on load the way
      `twin/attenuation.yaml` and `twin/evidence-ladder.yaml` are — a positive `half_life_days`
      and a `decayed_out_threshold` strictly between 0 and 1, refused otherwise
      (`test_decay_function_is_versioned_and_published`). `unbound_pool.pin()` carries the
      version, both parameters and a content digest into every emitted artefact's pins, the same
      discipline `evidence.pin()`/`propagate.schedule()`'s own version stamp use.
- [x] Pool size and age distribution are observable.
      `twin unbound-pool --repo R --org O --at T` emits an `unbound-signal-pool` artefact whose
      body carries `pool_size` (the live, non-decayed count) and `age_distribution` — a histogram
      binned by half-life multiple, every bin present with zero included, the same discipline
      `twin/benchmark.py`'s `confidence_distribution` uses against its own rule's bins
      (`test_age_distribution_bins_the_live_pool_by_half_life_multiple`,
      `test_unbound_pool_artefact_body_carries_observable_size_and_distribution`,
      `test_the_cli_verb_emits_an_unbound_signal_pool_artefact`).
- [x] A signal that decays out is recorded as having done so, not silently deleted.
      A decayed-out signal stays in the artefact's own `signals` list — `decayed: true` and a
      computed `decayed_on` date beside it — rather than being dropped once it crosses the
      threshold; only `pool_size`/`age_distribution` exclude it from the *live* count
      (`test_pool_size_counts_only_the_live_pool_not_the_decayed_out`,
      `test_age_distribution_excludes_decayed_out_signals`). Demonstrated live against the suite's
      own fixture, not just fixtures this ticket authored, by harness guard
      `unbound_pool_retains_a_decayed_signal_rather_than_dropping_it`.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added
      (`unbound_pool_retains_a_decayed_signal_rather_than_dropping_it`,
      `twin/invariants/harness.py`), zero weakened, zero pinned hashes changed — the guard is new
      rather than a change to any of the sixteen constitution invariants in
      `twin/invariants/checks.py`, so no manifest re-bless was needed.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `unbound_pool_artefact()` reuses `sense-move`'s existing depth grade
      (`CAPS_UNBOUND_POOL = verbs.CAPS_SENSE`), the same choice build ticket 53's `ingest.py` made
      — retention is part of decision ticket 11's own sense-move capability, not a capability of
      its own. `twin/capabilities/sense-move.yaml` AC5 ("Weak-signal retention + promotion rule.")
      stays **unchecked** on purpose: the criterion text is conjunctive and this ticket builds only
      the retention half — the promotion/rescue half (a model change triggering a retrospective
      sweep that rebinds a decayed signal) is build ticket 55's, not built here. Ticking AC5 now
      would be exactly the premature-done the constitution's computed-checklist discipline exists
      to prevent; `sense-move` stays at 5/8, and ticket 55 is expected to move it to 6/8 once both
      halves exist.
