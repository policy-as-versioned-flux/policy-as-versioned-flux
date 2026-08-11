# 41 — Hindsight-resistance cases and inverted scoring

**What to build:** Cases where the **contemporaneous record contradicts the canonical story**. Here, confident
agreement with the canonical story is evidence of *memorisation*, not of skill — so these cases
score **inverted**, and they function as a memorisation detector rather than a performance test.

This is the sharpest instrument in the falsifiability track: it can catch contamination that the
Enron control's aggregate gap would miss.

**Blocked by:** 40

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 19. Spec story 47.

- [x] At least two cases where the contemporaneous record and the canonical narrative diverge, both documented.
      `fixtures.build_astrazeneca_org()` (rejects Pfizer's bid, 2014 — punished 11-13% on the
      day, a named ~2% holder publicly critical, now retold as visionary ahead of a 2026 mega-
      merger) and `build_sanofi_org()` (exits diabetes/cardiovascular for GLP-1 obesity, 2019 —
      approved +5% at the time, later reframed once a rival's obesity drug became a blockbuster
      from 2022). An inverse pair, not two of the same shape: AZ was punished then vindicated by
      the retelling, Sanofi was approved then blamed by it
      (`tests/test_hindsight_resistance.py::test_the_two_cases_are_an_inverse_pair`). Every signal
      real, dated and cited by URL (`test_every_signal_carries_a_real_date_and_a_dated_source`).
- [x] Scoring inverted for these cases, with the inversion explicit in the score card.
      No special-cased scoring math — `scoring.score()` runs unmodified. Each fixture carries
      **two world models** on one scenario (`no_collapse_mechanism` already forbids collapsing an
      execution's forecasts): `contemporaneous-consensus` reasons from what was knowable at the
      time, `canonical-hindsight-consensus` reports the belief a system reciting the now-common
      story would hold. Both score against the *contemporaneous* outcome, so agreement with the
      canonical story is what scores badly — the inversion is structural, in the fixture, not a
      code branch. `hindsight_trap: true` on the outcome (new optional field, twin/schema.py)
      threads through `verbs.score()`'s `answer_key` block, making it explicit in the card rather
      than implicit in which case it happens to be
      (`tests/test_hindsight_resistance.py::test_the_az_outcome_declares_the_hindsight_trap`,
      `test_the_sanofi_outcome_declares_the_hindsight_trap`).
- [x] A demonstration that a memorising system scores worse on these than a non-memorising one would.
      `canonical-hindsight-consensus` scores worse (higher brier and log-loss) than
      `contemporaneous-consensus` on both cases, run through the real CLI
      (`twin run` + `twin score`), not asserted synthetically
      (`test_the_canonical_hindsight_world_model_scores_worse_than_the_honest_one`, parametrized
      over both). The suite's own guard reproduces this at CI time
      (`twin/invariants/harness.py::_hindsight_resistance_cases_score_a_memorising_system_worse`).
- [x] Results feed the contamination discount rather than sitting alongside it.
      `scoring.measure_discount()` (built at ticket 40) takes optional `hindsight_memorising`/
      `hindsight_honest` score lists and averages their own gap into the *same* returned
      `discount`, reporting both legs in `legs` rather than a second, parallel number
      (`tests/test_scoring.py::test_hindsight_legs_fold_into_the_same_discount_rather_than_sitting_beside_it`,
      exercised against the real AstraZeneca fixture's own scores in
      `tests/test_hindsight_resistance.py::test_the_hindsight_gap_folds_into_the_same_discount_enron_versus_obscure_measures`).
      **No CLI flag for this** — see the closure note for why that is deliberate, not a gap.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`hindsight_resistance_cases_score_a_memorising_system_worse`), zero
      weakened. Cites decision ticket 19.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket, the same finding tickets 38-40 record: it
      authors two answer-key fixtures and extends ticket 40's scoring machinery, not a criterion
      of any of the seven tracked capabilities. Landed and ticked nothing.

**Closure note.** An earlier version of this ticket added `--discount-hindsight-memorising`/
`--discount-hindsight-honest` CLI flags alongside ticket 40's `--discount-enron`/
`--discount-obscure`. They were removed: `twin score`'s discount loading (`cli._pooled_scores`)
concatenates every scored forecast in each named card with no `world_model` filter, which is
correct for ticket 40's Enron/obscure cards (one world model each) but silently wrong for a
hindsight card, since one AstraZeneca or Sanofi score card carries *both* world models together —
pointing the flags at a real one would have mixed memorising and honest scores into both legs and
produced a meaningless gap. Adding a `--discount-hindsight-*-world-model` filter to make it work
would have been new surface area no AC asked for, to serve a use case (folding a *specific* real
hindsight case into a *specific* live discount computation via the CLI) nothing in this ticket or
ticket 40 needs — the AC only requires that the fold happen, which `measure_discount()` already
proves against real fixture data. Removed rather than half-fixed: the honest state is that this
fold is proven at the function level, not exposed as a CLI feature, and the ticket file should say
exactly that rather than tick a box for a flag that could not do what its own help text claimed.

**Review note (Standards + Spec, `mattpocock-skills:code-review`).** Spec's sharpest finding was
exactly this: the ticket had checked `[x]` on "results feed the contamination discount" while
citing CLI flags its own closure note admitted were "not directly usable" for the fixtures the
ticket exists to score — the caveat was buried in prose after the box was already ticked, which
is the "premature done" failure mode the constitution names, not a passing grade with an asterisk.
Fixed by removing the non-functional flags rather than rationalising them, and rewriting this
ticket's AC evidence and closure note to describe what was actually delivered: a fold proven at
the function level against real AstraZeneca/Sanofi scores, with no claim of CLI-level support.
Spec also independently verified every AstraZeneca/Sanofi citation (the Bloomberg, AstraZeneca,
Fortune, Sanofi, BioPharmaDive, FiercePharma and 2026 TechTimes sources) against the live web and
found none fabricated — including the 2026-08-02 AstraZeneca/BMS piece, which is a genuine,
current article rather than an invented one. Standards found no issues specific to this ticket's
own diff beyond the two shared with ticket 40 (score-card-loading duplication, `--discount-rule`
missing `choices=`), both fixed there.
