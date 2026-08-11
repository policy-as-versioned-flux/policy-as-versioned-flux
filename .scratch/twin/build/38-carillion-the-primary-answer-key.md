# 38 — Carillion: the primary answer key

**What to build:** The primary backtest key, chosen for **low notoriety** rather than fame — success against a famous
collapse is not distinguishable from reciting it.

Carillion is unusually well-instrumented for this: a free dated FCA short register plus HC 769 give
contemporaneous, adversarial ground truth rather than a cooperative survivor narrative.

Blocked only on the answer-key fixture format, not on the scoring engine — this is research and
authoring work and can start early.

**Blocked by:** 08

**Status:** done (2026-08-10)

**Reading list:** Decision ticket 19 (opportunity cases research) for the evidence-asymmetry argument; research 02. Spec story 45.

- [x] A dated answer key with contemporaneous sources, each cited and dated.
      `fixtures.build_carillion_org()`: eight signals, each a real, dated, publicly documented
      fact cited by URL — three RNS trading updates, three profit warnings, a reported
      short-interest position, and the compulsory liquidation itself
      (`tests/test_carillion.py::test_every_signal_carries_a_real_date_and_a_dated_source`).
- [x] Ground truth drawn from adversarial and contemporaneous records (short positions, statutory registers, inquiry evidence), not retrospective narrative.
      HC 769 (the joint parliamentary inquiry) is cited only on the resolved outcome, published
      after every signal, never used to date one —
      `tests/test_carillion.py::test_ground_truth_is_adversarial_and_contemporaneous_not_a_survivor_narrative`
      and `test_no_signal_dates_a_fact_using_hc_769_which_is_hindsight`.
- [x] Key conforms to the fixture format from ticket 08 and is machine-consumable.
      `tests/test_carillion.py::test_the_outcome_conforms_to_the_ticket_08_fixture_format` and
      `test_the_fixture_validates_against_its_closed_schema`.
- [x] Every fact in the key carries the date it became knowable, so regime gating can use it.
      The repository's own commits are dated to match, in order, so `regimes.ingestion_history`
      reports `available: true` at every date the tests try
      (`tests/test_carillion.py::test_the_commit_history_is_monotonically_dated`,
      `test_a_real_rewind_reads_the_repository_as_it_actually_stood`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`carillion_answer_key_is_dated_and_adversarial`), zero weakened.
      Cites decision ticket 19.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket: it authors an answer-key fixture, not a
      criterion of any of the seven tracked capabilities. Landed and ticked nothing.

**Retroactive closure note (build ticket 34).** Built and committed at `ace64f8` ("Build tickets
25, 32, 37, 38, 42, 60 and 62"), but this file's own `Status:` line and checklist were never
updated at the time. Found and closed during the build ticket 34 coherence audit; see ticket 25's
identical note for how.
