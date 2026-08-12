# 16 — Believed map, rival forecasts, revealed truth — and the deltas between them

**What to build:** Three distinct things held separately: what the org **believes**, what **rivals forecast**, and
what was **revealed**. There is no privileged "actual" map anywhere — the twin's own belief is just
another scored position rather than an unexamined baseline.

The pairwise deltas are the point, not the separation. Believed-versus-revealed *is* the anticipation
failure, measured.

**Blocked by:** 12, 08

**Status:** done (2026-08-10)

**Reading list:** Decision tickets 07, 11. Spec stories 6, 7.

- [x] Three separate versioned position sets with no schema-level privilege between them.
      Believed maps and rival forecasts are ordinary `world-model` objects — no field distinguishes
      one role from another, so a "believed" map and a "rival" one are typed identically and both
      are git-versioned overlay/world content. Revealed truth is not even a world model: it is
      derived in `twin/positions.py::revealed()` from a resolved `outcome`, so there is no schema
      slot anywhere that a privileged "actual" map could occupy.
- [x] Each pairwise delta is computed and scored, not merely displayed.
      `twin/positions.py::pairwise_deltas()` computes `|a - b|` for every unordered pair of named
      positions; `against_revealed()` additionally scores each position against a resolved outcome
      with the existing proper rules (`twin/scoring.py` Brier and log loss) — a plain magnitude
      where there is no ground truth, and a proper score where there is, never one substituting
      for the other.
- [x] The twin's own belief is scored on the same footing as any other position.
      `against_revealed()` iterates every named id through one call with no branch on which id
      produced it; `tests/test_positions.py::test_against_revealed_matches_the_proper_score` checks
      `twin-default` (the twin's own default reference) scores through the identical path as
      `netflix-believed` and `rival-fast-commoditisation`, reproducing the exact Brier figures
      `twin score` already computes for the same fixture.
- [x] A demonstration that removing the 'actual' map breaks nothing, because nothing depended on one.
      `tests/test_positions.py::test_dropping_any_one_position_changes_nothing_else` drops each of
      the three fixture positions in turn — including the org's own believed map and the twin's
      default reference — and asserts the survivors' own scores do not move. Harness guard
      `position_deltas_have_no_privileged_default` asserts the same property at the suite level,
      against the live fixture repository rather than a unit-level call.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      A new harness guard, `position_deltas_have_no_privileged_default`, registered in
      `twin/invariants/harness.py` — the same shape as `an_intervention_never_reaches_upstream`
      (build ticket 22). No existing invariant's pinned body or `refuses_keys` changed, so no
      authorising citation was needed: only a new guard was added, guarding a semantic property of
      a module's contract rather than one of the constitution's sixteen named absences.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin verbs.py::positions()` calls `caps.depth_block(CAPS_POSITIONS)` against the existing
      `domain-model`, `provenance`, `scenario-engine` and `sense-move` capability checklists — the
      same computed-grade machinery every other verb uses. No new capability file was added and no
      existing checklist item was ticked: none of their remaining acceptance criteria names this
      capability precisely enough to tick honestly, so the artefact's depth stays `partial` at the
      same denominators as before, and that is the honest state.
