# 62 — The misuse catalogue and constraint-removal logging

**What to build:** Constraint removals are **logged together with the forbidden option's attractiveness at the moment
of removal** — so the motive is recorded when it exists rather than reconstructed afterwards, when
everyone has a better story.

**Blocked by:** 27

**Status:** done (2026-08-10)

**Reading list:** Decision ticket 15. Spec stories 60, 72.

- [x] Misuse catalogue is a versioned artefact naming mechanisms, not just risks.
      `twin/misuse-catalogue.yaml` — seven entries, each naming a mechanism a reader can go and
      check (`prefilter_precedes_pricing`, `derived_never_human_signed`, the regime gate, this
      ticket's own removal log, build ticket 60's `refuse_answering_a_different_claim`), not a
      sentence anyone could write (`tests/test_misuse.py::test_the_catalogue_loads_and_every_entry_names_a_mechanism`,
      `test_a_catalogue_entry_with_no_mechanism_is_refused`).
- [x] Removing a constraint requires logging the excluded option's current attractiveness, computed not stated.
      `misuse.log_removal()` carries no float parameter in its signature; the only way to produce a
      figure is to name a perspective, an option and the constraint, and
      `compute_attractiveness()` re-runs `twin/options.py prefilter()` with that one constraint
      stripped (`tests/test_misuse.py::test_attractiveness_is_computed_from_the_real_cost`,
      `test_log_removal_requires_no_number_from_the_caller`). Harness guard
      `a_constraint_removal_with_no_computed_attractiveness_is_rejected` checks the signature
      itself, not just correct usage of it.
- [x] The removal log is append-only and published.
      `misuse.log_removal()` opens its target in append mode (`twin/misuse.py`), never rewrites,
      and `verify_removals()` reads it back
      (`tests/test_misuse.py::test_logging_and_reading_back_a_removal`,
      `test_a_missing_log_is_empty_not_an_error`).
- [x] A removal with no attractiveness record is rejected.
      `verify_removals()` compares a perspective's declared constraint ids before and after and
      demands a matching log entry for every one that disappeared, per perspective
      (`tests/test_misuse.py::test_an_unlogged_removal_is_rejected`,
      `test_a_removal_logged_for_a_different_perspective_does_not_count`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`a_constraint_removal_with_no_computed_attractiveness_is_rejected`),
      zero weakened. Cites decision ticket 15.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket: it closes decision ticket 15's carried-forward
      item, but decision ticket 15 has no tracked capability file among the seven in
      `twin/capabilities/`. Landed and ticked nothing.

**Retroactive closure note (build ticket 34).** Built and committed at `ace64f8` ("Build tickets
25, 32, 37, 38, 42, 60 and 62"), but this file's own `Status:` line and checklist were never
updated at the time. Found and closed during the build ticket 34 coherence audit; see ticket 25's
identical note for how.
