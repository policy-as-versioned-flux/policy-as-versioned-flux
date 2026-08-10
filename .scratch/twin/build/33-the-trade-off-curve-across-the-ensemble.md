# 33 — The trade-off curve across the ensemble

**What to build:** The output shape: a **trade-off curve across the ensemble with a marked default** — never a
verdict. When two world models disagree about pay-rise-versus-hardening, **that disagreement is the
headline**.

A single number ends a conversation; a map sustains one. Every place this system could collapse to a
verdict, it deliberately does not, because terminating the argument would destroy the thing's
function.

**Blocked by:** 30, 32

**Status:** done (2026-08-10)

**Reading list:** Decision tickets 09, 13. Spec stories 34, 36.

- [x] Output is a curve over the ensemble, with the default marked and its basis stated.
      `twin/tradeoff.py curve()` and `twin trade-off` run `pricing.price` once per named causal
      account and report each admitted response's net cost of risk (`cost.mode - credit.mode`) per
      account in `curve[].net_cost_of_risk.by_account`. `default.option` is the option whose mean
      net cost across the named accounts is lowest, with `default.basis` stating in words that it
      is a computed default point, not a recommendation.
- [x] `no_recommended_action_field` is re-asserted against this richer output.
      Harness guard `trade_off_curve_reports_disagreement_never_a_scalar`
      (`twin/invariants/harness.py`) runs the identical banned-word scan against the trade-off
      curve — the same key- and prose-level checks `no_recommended_action_field` runs against the
      Wardley map — added as a guard rather than a seventeenth constitution invariant, the same
      shape `causal_accounts_have_no_privileged_default` (32) and
      `a_var_shaped_summary_hides_what_tvar_surfaces` (24) already are.
- [x] Ensemble disagreement is surfaced prominently rather than averaged away.
      `agreement.cheapest_by_account` and `agreement.unanimous` report per-account ranking
      agreement ahead of the default, and `net_cost_of_risk.by_account` / `.range` report the raw
      numeric spread rather than folding accounts into one figure. A new causal account,
      `rival-cdn-headwind`, was added to the netflix fixture (overriding `cdn-capacity-lifts-streaming`,
      grade 2) alongside a `mitigates` claim on `expand-the-delivery-network`, because build ticket
      32's three existing accounts all disagree only on `streaming-displaces-dvd` (grade 3), which
      never clears the pricing threshold and so never reaches a response's own figure —
      `tests/test_tradeoff.py::test_the_three_streaming_displaces_dvd_accounts_never_move_a_net_figure`
      demonstrates that negative case directly, alongside the positive one.
- [x] A test that no consumer-facing path reduces the curve to a scalar.
      `tests/test_tradeoff.py::test_the_cli_prints_every_account_never_one_collapsed_number`
      captures `twin trade-off`'s own stdout and asserts the printed line for the credited response
      names both accounts' own figures rather than an average.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`trade_off_curve_reports_disagreement_never_a_scalar`), zero
      weakened; the constitution's fixed sixteen are untouched. Cites decision tickets 09 and 13.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `CAPS_TRADEOFF` in `twin/verbs.py` carries `currency-regimes`, whose capability file
      (`twin/capabilities/currency-regimes.yaml`) now ticks ACs 5 ("a stated objective function
      with its qualifications") and 6 ("how rival-model £ spread is reported") against this
      ticket's own evidence, moving that capability from 3/6 to 5/6 — computed by `twin/grades.py`,
      never typed.

## Review-driven fixes (2026-08-10)

Three independent reviews (architecture, code quality/testing, security/correctness) converged on
one real issue and each added others:

- The new harness guard's banned-word list was a hand-copied duplicate of
  `no_recommended_action_field`'s own, with a comment claiming it wasn't. Fixed: both now import
  `NO_ACTION_BANNED_KEYS` / `NO_ACTION_BANNED_PHRASES` from `twin/invariants/__init__.py`. This
  changed `no_recommended_action_field`'s check-body hash, re-pinned via `twin verify --rehash`.
- `twin/tradeoff.py`'s closed-body check merged `pricing.BODY_KEYS` wholesale, legalising
  pricing's own vocabulary anywhere in tradeoff's top-level structure rather than only inside the
  embedded `pricing.price()` sub-bodies. Fixed: `BODY_KEYS` is now scoped to this module's own
  fields only; embedded sub-bodies are excluded from the walk (`_own_shape`) and trusted to
  `pricing.price()`'s own closure check, which already ran before this module ever saw them.
- No test exercised `agreement.unanimous is False` — no fixture in this repository makes two
  admitted responses swap which is cheapest between accounts. Fixed: extracted the pure,
  non-fixture part of `curve()` into `_assemble()` and added three tests against synthetic
  figures, including the tie-break-by-mean case.
- `twin/README.md`'s "What is honestly built" table and narrative had drifted before this ticket
  (`scenario-engine` was 1/7 in prose, 2/7 by `./bin/twin grade` — build ticket 37's tick was never
  folded in) and this ticket's own currency-regimes row would have made that worse. Fixed:
  re-derived every row from `./bin/twin grade` (11 of 41 → 14 of 41) rather than hand-incrementing,
  and removed the now-false "ACs 5–6 need build ticket 33" bullet.
- Minor: the CLI-output test only checked that both account labels appeared, not that their
  printed figures matched the artefact; added a numeric cross-check.

All three reviews independently reported no critical or high-severity findings beyond the above.
`twin verify` (36/36), the full test suite (770 passed, up from 767 — the 3 new `_assemble` tests)
and mypy are all clean after these fixes.
