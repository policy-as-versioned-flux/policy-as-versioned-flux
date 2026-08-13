# 59 — Prediction-market price moves as world-layer signals

**What to build:** Consume market **price moves** as dated world-layer signals — while never treating price
**levels** as probabilities.

The reason is specific rather than fastidious: favourite–longshot bias is rejected-unbiased in every
subsample and is **worst in the deep tail**, which is exactly the region the risk engine exists to
reason about.

**Blocked by:** 57, 53

**Status:** done (2026-08-12)

**Reading list:** Decision ticket 21; research 17. Spec story 53.

- [x] Price moves ingest as dated world-layer signals through the normal sensing path.
      `twin/market_signals.py::market_signal_run()` turns a `PriceMove` into a dated statement and
      runs it through `signal_classify.classify()` unattended — the identical no-human-gate
      mechanism `twin/ingest.py` (build ticket 53) already proved at volume, exercised here over
      prediction-market price moves instead of synthetic substrate
      (`tests/test_market_signals.py::test_market_signal_run_ingests_moves_through_signal_classify`).
      Candidates come from the real fixture graph (`ingest.candidates_of`, reused rather than
      duplicated), so a move binds to a genuine world/overlay component, not a hand-typed stand-in.
- [x] `price_levels_never_probabilities` is added to the invariant suite and goes live.
      `twin/invariants/manifest.yaml` flips the entry from `pending` to `live` with a pinned
      `body_sha256`; the check itself
      (`twin/invariants/checks.py::_price_levels_never_probabilities`) is harness check 54, run
      as part of the standing suite.
- [x] An attempt to use a level as a probability fails rather than warns.
      `market_signals.as_probability()` raises `PriceLevelAsProbabilityError` unconditionally —
      never returns a number, never logs and continues. The invariant checks this at the source,
      not only by calling it once: `as_probability`'s own source is scanned for warning machinery
      (`warnings.warn(`, `.warning(`, `print(`) and finds none, and is exercised against five
      levels spanning the whole [0,1] range in both the suite and
      `tests/test_market_signals.py::test_as_probability_always_refuses`.
- [x] The bias evidence is cited in the artefact that consumes these signals.
      Every `market-signal-run` artefact carries `body["bias_evidence"]` — the Bürgi, Deng &
      Whelan (2026) favourite-longshot finding, verbatim, research ticket 17 §3.1 — asserted
      directly against the emitted body in both the harness guard and
      `tests/test_market_signals.py::test_bias_evidence_is_cited_in_the_artefact_that_consumes_the_signals`,
      not merely present in a docstring.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One invariant activated (`price_levels_never_probabilities`, pending since the manifest was
      first written, now live), zero weakened. Activating it changed `checks_module_sha256`
      (a new check function was added to `twin/invariants/checks.py`), re-pinned via `twin verify
      --rehash --authorise "decision ticket 21 — build ticket 59: adds the
      price_levels_never_probabilities check to checks.py..."` — cited in the manifest's
      `checks_module_authorised_by` field and in this ticket's commit message. No existing check
      body changed.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `market_signal_run()` declares `CAPS_MARKET_SIGNALS = ["forecast-book"]`, the same
      capability build ticket 57's benchmark module declares (owning decision ticket 21).
      `twin/capabilities/forecast-book.yaml` AC5 ("the circularity question resolved — signal
      source vs benchmark") ticks on this ticket's evidence, moving `forecast-book` from 1/6 to
      2/6 — computed by `./bin/twin grade`, not hand-typed; `grade` stays `partial`, honestly, per
      `tests/test_market_signals.py::test_market_signal_run_declares_its_depth_grade_as_the_computed_forecast_book_checklist`.

## Built (2026-08-12)

`twin/market_signals.py`, one harness guard (`price_levels_never_probabilities`, the sixteenth
constitution invariant, now live), `tests/test_market_signals.py`.

- **Price levels never reach a probability-shaped slot, structurally.** `PriceObservation` and
  `PriceMove` (`twin/market_signals.py`) carry `price_level`/`from_level`/`to_level`, never
  `probability` or `implied_probability` — checked directly against the dataclass fields in both
  suites. `as_probability()` is the one function that would translate a level into a belief, and
  it refuses unconditionally, citing research 17 §3.1's favourite-longshot finding
  (Bürgi, Deng & Whelan 2026: Mincer–Zarnowitz regressions reject unbiasedness in every subsample
  tested, worst in the low-price tail) in its own refusal message, so the citation travels with
  the code path that respects it rather than sitting only in a comment.
- **Price moves — the derivative, never a level in isolation — are what gets ingested.**
  `price_moves()` pairs consecutive dated observations of the same question, sorted by date
  regardless of arrival order; a single observation produces no move, which is the correct answer
  (research 17 §4: the value is the change, not the point), not a tolerated edge case.
  `move_statement()` turns a move into the dated, sourced sentence `signal-classify` reads, and
  never mentions a probability.
- **Signal source vs benchmark (decision ticket 21 Q1(b)) holds end to end, not on paper.**
  `market_signal_run()` excludes a quarantined question id (`twin/benchmark.py`, build ticket 57)
  *before* classification ever runs, and the harness guard re-runs build ticket 57's own
  `audit_quarantine()` over this pipeline's live ingestion-provenance output, requiring it clean —
  so the quarantine and the live signal source are asserted together, in one pipeline, rather than
  trusted to agree because they were each tested in isolation.
  `tests/test_market_signals.py::test_a_quarantined_question_id_is_excluded_before_classification_ever_runs`
  exercises the same shape at seam 2.
- **No human gate, matching the sensing path this reuses (decision ticket 11 Q2).**
  `market_signal_run` has no confirm/review/approve-shaped parameter and calls no confirmation
  step, checked by source inspection the same way `twin/ingest.py`'s own tests check it; every
  ingested item stays grade 5 by construction (`signal_classify.classify()`'s own guarantee, build
  ticket 43), trusted downstream rather than gated at entry.
- **The capability declared is `forecast-book` (decision ticket 21), reused rather than invented.**
  `CAPS_MARKET_SIGNALS = ["forecast-book"]` — the same list-of-one shape `twin/benchmark.py`'s
  `CAPS_BENCHMARK` uses — because this ticket's reading list names decision ticket 21 and its work
  is the "signal source" half of that ticket's own Q1(b), not a capability of its own. AC5 ticks;
  the other four criteria (venue/observe-only in code, blind pinned emission, the published claim
  scope, the proportionality verdict) are build ticket 58's, left honestly unticked.
- Extends the invariant suite by activating `price_levels_never_probabilities` (pending since the
  manifest was first written, now live) — no manifest hash changed on an existing live check;
  `checks_module_sha256` moved because a new check function was added, re-pinned with
  `--authorise "decision ticket 21 — build ticket 59: adds price_levels_never_probabilities check
  to checks.py..."`. Adding `forecast-book`'s new tick also moves `Capabilities.digest`, and every
  artefact's pins with it — the same consequence build ticket 57's own notes named — so
  `twin/invariants/golden-digests.json` was re-blessed via `bin/twin verify --bless-goldens
  --authorise "decision ticket 21 - build ticket 59 (prediction market price moves) changes
  computed artefact bytes"` in the same change.
- `ponytail:` no CLI verb, the identical choice build tickets 53 and 57 made for the same reason:
  `market_signal_run`/`price_moves`/`as_probability` are typed functions exercised at seam 2, and
  a real Polymarket/Kalshi venue adapter (not this ticket, and not yet scheduled) is what would
  give a CLI invocation something live to point at. Built against a caller-supplied fixture price
  series throughout, the same way build ticket 57 built against a caller-supplied candidate pool —
  no live market API connection is reachable from this suite.

**This ticket activates the sixteenth and last pending invariant the constitution names — every
invariant in `twin/invariants/manifest.yaml` is now `live`, none `pending`.** That is a genuine
milestone, and it broke an assumption two pre-existing suite-guard tests carried without stating
it: `tests/test_invariant_suite.py::test_an_invariant_pending_past_a_closed_ticket_fails` and
`::test_only_declared_guards_may_decline_to_assert` both fished "any pending entry" out of the
real, committed manifest to use as their test subject. With zero pending entries left, the first
found nothing to trip `no_invariant_pending_past_its_ticket` into failing (a vacuous pass instead
of the expected fail) and the second raised `StopIteration` outright. Both are fixed here, honestly
— not by weakening either check, but by decoupling the *test's own subject* from the real manifest:
the first now monkeypatches `load_manifest` to return a synthetic pending entry (the same pattern
`test_a_weakened_test_body_is_caught` already uses for a synthetic live one), and the second checks
`may_skip`'s actual rule for an invariant — "not in the live set" — directly, against a name that is
provably absent from it, rather than assuming the committed manifest will always supply one. Neither
fix touches the invariants or checks themselves, and both are exercised at
`tests/test_invariant_suite.py`.

**A pre-existing, unrelated failure found while verifying, not introduced here:**
`drift_window_is_actually_being_sampled` (build ticket 64's Flux drift instrument) fails in this
environment because its background sampling probe is not running here — "the window is open and
the newest sample is 1 day(s) old... the probe has stopped." Confirmed present, identically, on
the clean pre-ticket state (`git stash` back to before this ticket's changes) before this ticket
touched anything, and confirmed unaffected by this ticket's own changes. Every other check,
including this ticket's own `price_levels_never_probabilities` and `identical_pins_identical_bytes`
(which this ticket's capability-digest change requires a golden re-bless for, done above), passes.
