# 40 — Enron as contamination control, and the memorisation-leakage discount

**What to build:** **The contamination pillar made quantitative.** An LLM asked about Enron has read the ending;
"flagging" Enron in 2000 is indistinguishable from reciting Enron in 2026.

So Enron is carried deliberately as a **control**: the measured gap between performance on Enron and
performance on an obscure key yields a **memorisation-leakage discount applied to every backtest
score**. The threat stops being acknowledged and starts being priced.

**Blocked by:** 39, 37

**Status:** done (2026-08-11)

**Reading list:** Decision tickets 01, 19; research on parametric contamination in map.md. Spec stories 46, 58.

- [x] Enron key authored in the same format as the low-notoriety keys.
      `fixtures.build_enron_org()`: four signals, each a real, dated, publicly documented fact
      cited by URL — the CEO's sudden resignation, the Q3 loss and equity writedown, the
      1997-2000 restatement, and the Chapter 11 filing itself
      (`tests/test_enron.py::test_every_signal_carries_a_real_date_and_a_dated_source`).
      `CONTAMINATION` (twin/schema.py) already reserved `"control"` for exactly this fixture;
      the outcome declares it, not `"low"` — not a fourth low-notoriety key
      (`test_the_outcome_declares_the_contamination_control_class_not_a_fourth_low_notoriety_key`).
- [x] The discount is **measured** from the Enron-versus-obscure gap, never hardcoded — a test asserts it changes when the underlying performance changes.
      `scoring.measure_discount()`: the mean-loss gap between an obscure key's score population
      and Enron's, quantised, never a literal. Two pure-function tests assert it moves with the
      inputs (`tests/test_scoring.py::test_the_discount_changes_when_the_underlying_performance_changes`)
      and that a forecaster with no memorisation advantage shows a gap near zero rather than a
      floor (`test_a_gap_near_zero_when_enron_earns_no_special_advantage`). The suite's own guard
      recomputes it twice against two different synthetic populations at CI time and refuses if
      they match (`twin/invariants/harness.py::_measure_discount_is_computed_not_hardcoded`).
- [x] Every backtest score carries its discount and the discount's basis.
      `twin score --discount-enron <card>... --discount-obscure <card>...` (repeatable, `twin
      score --discount-rule`): `verbs.score()` accepts a precomputed `discount` basis and stamps
      `discount`/`adjusted_<rule>` onto every scored forecast and `contamination_discount` (basis
      + legs) onto the card body — `None` when no discount was supplied, never a fabricated zero
      (`tests/test_enron.py::test_the_discount_measured_from_enron_versus_carillion_is_measured_not_hardcoded`).
      The obscure leg draws from Carillion (ticket 39's own note), not Wirecard.
- [x] The discount is reported separately from the raw score so both are visible.
      Raw `brier`/`log_loss` are untouched; `discount` and `adjusted_<rule>` are additive fields
      beside them, never a substitution (same test, asserting `entry["brier"] !=
      entry["adjusted_brier"]` while the raw figure survives unchanged).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`measure_discount_is_computed_not_hardcoded`); Enron's own dated-
      and-cited contract joined `further_answer_keys_are_dated_and_evidenced` (build ticket 39's
      table) as a third row rather than a fourth near-duplicate guard — see the review note. Zero
      weakened. Cites decision ticket 19. The golden `score-card` digest moved because the body
      shape grew two always-present fields (`hindsight_trap`, `contamination_discount`); re-blessed
      citing decision ticket 19 — see the closure note.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket, the same finding tickets 38 and 39 record: it
      authors an answer-key fixture and a scoring extension, not a criterion of any of the seven
      tracked capabilities. Landed and ticked nothing.

**Closure note.** Pinning the discount cost more than the diff shows. The first design threaded
`--discount-enron`/`--discount-obscure` *file paths* straight into the recorded command — until
`verbs.command_for`'s own docstring ("A forecast being scored is named by its digest here for the
same reason — by pin, never by path") made the mistake obvious: a machine-local path in the
command breaks `identical_pins_identical_bytes` across machines, and worse, `reproduce.py`'s
`replay()` would silently rebuild a discount-carrying score card *without* the discount (it parses
no `--discount-*` flags), producing a mismatched digest that reads as a bug rather than a stated
limit. Fixed the same way `twin reliability` already accepts: the discount is pinned by digest
(`--discount-sha256`, computed from the discount's own canonical JSON), never by path, and
`replay()` now refuses a discount-carrying score card explicitly and by name
(`tests/test_enron.py::test_a_discounted_score_card_honestly_refuses_to_replay_from_pins`) rather
than mis-replaying it — the identical limit `reliability`'s own pooled score-card inputs already
carry, since neither verb is in `reproduce.VERBS`'s replay chain. An undiscounted score card
(Carillion, NMC, Wirecard, Enron, or anything else) reproduces exactly as before.

**Review note (Standards + Spec, `mattpocock-skills:code-review`).** Standards found two real
Duplicated Code smells, both fixed: the Enron harness guard had re-copied the four-leg
dated-and-cited check ticket 39's `_FURTHER_ANSWER_KEYS` table exists specifically to avoid
re-copying — Enron is now that table's third row, and the Enron guard shrank to the one leg the
table cannot cover (`measure_discount` is genuinely computed, renamed
`measure_discount_is_computed_not_hardcoded`); and `cli.py`'s score-card-loading loop claimed to
reuse `cmd_reliability`'s shape while actually re-deriving it with a different exception type —
fixed by pulling the shared read-and-kind-check into `verbs.load_score_card()`, used by both.
Also fixed: `--discount-rule` gained `choices=list(RULES)` to match `--regime`'s
`choices=list(REGIMES)` idiom, and a date-arithmetic slip ("nearly three months" for a 61-day gap)
corrected to "just over two months" in both the fixture's own note and the test docstring. Spec
independently verified every Enron citation (SEC EDGAR filings, the Powers Report) is real and
accurately dated, and confirmed the discount is genuinely measured rather than hardcoded by
reading `measure_discount` and running the suite. Its sharpest finding concerned ticket 41, not
this one — see that ticket's review note.
