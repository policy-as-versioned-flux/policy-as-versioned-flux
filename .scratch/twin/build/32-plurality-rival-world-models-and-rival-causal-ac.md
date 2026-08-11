# 32 — Plurality: rival world models and rival causal accounts

**What to build:** Competing world models and rival causal accounts as **first-class versioned units**, coexisting as
**ensemble spread** adjudicated by the calibration record over time rather than resolved by whoever
authored last.

Three things that looked like separate design choices in earlier drafts are one thing, so they are
one ticket: legitimate disagreement is represented, not resolved.

**Blocked by:** 16, 18

**Status:** done (2026-08-10)

**Reading list:** Decision tickets 07, 08. Spec stories 6, 27, 36.

- [x] Rival world models are separate versioned units executable against the same scenario.
      Pre-existing, and confirmed still standing: a `world-model` is an ordinary schema object
      (build ticket 04) and one scenario execution already emits one forecast per named world
      model (build ticket 06). `twin positions` (16) reports the deltas between them with no
      privileged map — `tests/test_positions.py`, harness guard
      `position_deltas_have_no_privileged_default`.
- [x] Rival causal accounts coexist over the same components without one being canonical.
      New at this ticket. A `causal-account` (`twin/schema.py`) is a named, sparse set of
      overrides on causal-edge ids; `Overlay.causal_graph(account_id)` reads it beside the
      overlay's own `edges`, itself just another nameable account
      (`tests/test_causal_accounts.py::test_this_overlays_own_edges_are_nameable_as_just_another_account`,
      `test_no_field_named_actual_or_canonical`).
- [x] Ensemble spread is computed and is the reported uncertainty.
      `twin/causal_accounts.py ensemble_spread` propagates each named account's own graph
      independently and compares the primary path's attenuated mean at every reached component —
      the spread between accounts is the reported figure, not either account's own
      (`tests/test_causal_accounts.py::test_the_rival_account_claims_the_stronger_effect`).
- [ ] Adjudication is by accumulated calibration score, and no mechanism exists to adjudicate by authorship or recency.
      The negative half holds: the `causal-account` schema is closed to `id`/`name`/`edges`/`note`,
      so no author or date field exists to adjudicate by, checked directly
      (`tests/test_causal_accounts.py::test_a_causal_account_carries_no_author_or_date_field`,
      harness guard `causal_accounts_have_no_privileged_default`). The positive half does not: a
      causal account does not itself emit a scoreable forecast, so nothing yet accumulates a
      calibration score *per account* to adjudicate by. `twin/README.md` states this plainly —
      "adjudicated by calibration over time" is a property this ticket makes representable, not a
      scoring loop it closes. Stays unchecked rather than ticked on the negative half alone.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`causal_accounts_have_no_privileged_default`), zero weakened; the
      constitution's fixed sixteen are untouched. Cites decision tickets 07 and 08.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket. `causal-layer` (decision ticket 08) stands
      where build ticket 22 left it; rival accounts are a plurality mechanism, not a leg of
      intervention/counterfactual semantics, confounding discipline or a co-flagship exercise, so
      none of its remaining criteria are what this ticket built. Landed and ticked nothing.

**Retroactive closure note (build ticket 34).** Built and committed at `ace64f8` ("Build tickets
25, 32, 37, 38, 42, 60 and 62"), but this file's own `Status:` line and checklist were never
updated at the time. Found and closed during the build ticket 34 coherence audit; see ticket 25's
identical note for how.
