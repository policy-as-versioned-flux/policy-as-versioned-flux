# 09 — Reliability diagrams over volume, and scheduled emission

**What to build:** Calibration is a property measured over volume, so the two halves belong together: the reliability
diagram needs forecasts, and scheduled emission is what produces them. The schedule also protects
the record from selection bias — we cannot only forecast when we feel confident.

Scheduled-execution orchestration is inherited from `/arckit:build --refresh`, which **assumes a
single repository while this is an org of repositories**. That adaptation is this ticket's work, not
a footnote.

**Blocked by:** 08

**Status:** done (2026-08-10)

**Reading list:** Decision tickets 11, 13. Research 04 (arckit toolkit) for the refresh caveat. Spec stories 19, 37, 44.

- [x] Reliability diagram produced over a forecast population, with bin counts shown so a thin bin cannot masquerade as calibration.
      `twin/scoring.py reliability_diagram()` pools the `scores` from as many named score cards as
      the caller gives it and bins them by predicted probability. Every bin is reported, including an
      empty one — `count` is what makes a thin bin visible, and `mean_forecast` /
      `empirical_frequency` are `None` rather than a fabricated `0.0` where nothing landed. Exposed as
      `twin reliability --score-card ... --out F`. The pooling claim is exercised with two separately
      named cards, not one, at both the CLI (`test_reliability_pools_scores_across_two_separately_named_score_cards`)
      and in `twin/demo.sh` step 20 — a review pass flagged that the first draft only ever proved
      pooling with a population of one card end to end, which was a real gap and is now closed.
- [x] Scheduled execution runs the standing scenario set without human initiation.
      `twin/schedule.py sweep()` runs every scenario in every org overlay of every named repository —
      there is no `--scenario` flag on `twin sweep`. "The standing scenario set" is read literally
      here: every scenario currently declared, since the library's own curation (admissibility,
      precondition-triggered plays) is build ticket 69 and does not exist yet.
- [x] The single-repository assumption in the inherited orchestration is adapted to an org of repositories, and the adaptation is documented as a deviation.
      `sweep()` takes a **list** of opened `ModelRepo`s rather than one, and `twin sweep --repo`
      is repeatable. The deviation and its reasoning are in `twin/schedule.py`'s module docstring
      rather than left implicit in the signature.
- [x] Emission is provably not event-gated: a run with no new signals still emits.
      `schedule.py` carries no SHA-256 staleness check at all — the second adaptation from
      `/arckit:build --refresh`, and the one that matters more: a scheduler that skips an unchanged
      scenario is the selection-bias mechanism decision ticket 11 Q5 warns against, wearing arckit's
      clothes. Harness guard `scheduled_emission_ignores_signal_presence` asserts the consequence —
      two sweeps back to back over the same, unchanged fixture repository emit the same, non-zero
      forecast count — and `tests/test_schedule.py` asserts it again at the unit level.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One guard added, none weakened, no manifest invariant touched: `scheduled_emission_ignores_signal_presence`
      is a harness check (`twin/invariants/harness.py`), not a constitution invariant — the same
      shape as the pocket-org worksheet and the drift-window guards, because it guards a property of
      the scheduler rather than a named absence the constitution enumerates. The sixteen-invariant
      count in the manifest is unchanged.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `sense-move` (decision ticket 11) moves from 1/8 to **2/8**: criterion 7, "the loop's cadence +
      re-price triggers, sufficient to generate forecast volume", is now checked —
      `twin/capabilities/sense-move.yaml` names the evidence. `scenario-engine` (decision ticket 13)
      stays at 1/7: criterion 6 wants the **full** selection rule (standing library + precondition
      -triggered + event-triggered + ad-hoc), and this ticket builds only the first of those four, so
      the criterion stays honestly unticked.
