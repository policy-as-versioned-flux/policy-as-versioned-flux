# 84 — Forecast book: the proportionality verdict

**What to build:** The one remaining AC on `forecast-book` (5/6 checked, all five substantial:
selection rule, venue decision, blind-emission protocol, claim-scope statement, circularity
resolution — built by tickets 57–59). AC 6 asks a judgement question, not a mechanics one: given the
forecast book's actual delivered coverage, is it worth building at this scope?

This is a verdict artefact, not new pipeline code — the smallest of the twelve tickets in this batch.
`twin/forecast_book.py`'s existing `CLAIM_SCOPE` constant already admits the scope is narrow
(general world-forecasting only, never the org-twin causal machinery); this ticket states the
proportionality answer explicitly, against the real observed numbers (question count, confidence-bin
spread, resolution cadence), not against an aspiration.

**Blocked by:** none

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 21 (`.scratch/twin/issues/21-forecast-book.md`).
`twin/capabilities/forecast-book.yaml` for exact AC text. `twin/forecast_book.py`,
`twin/benchmark-selection-rule.yaml`, `twin/market_signals.py`.

- [x] AC 6 — "A proportionality verdict: is it worth building at this coverage?" A
      `proportionality_verdict()` function returning a derived artefact that cites the actual
      observed coverage numbers against decision ticket 21's own stated cost/benefit framing, and
      states the verdict plainly — yes, no, or conditional, with the reasoning that makes it
      checkable rather than asserted. Built as `twin/benchmark.py::proportionality_verdict()`
      (see "Where it actually lives" below for why not `forecast_book.py`, as this draft assumed).
      Every number the verdict is checked against is read off what is actually delivered: real
      `question_count`/`spans_full_confidence_range` from the live committed
      `twin/benchmark-selection-rule.yaml` run through `select_questions()`, real
      `capability_share` from `len(list(caps))` (the live count of `twin/capabilities/*.yaml`,
      not a hardcoded "~10%"), and an honestly-stated `resolution_cadence` that reads real
      resolved-score data when supplied and says plainly "not yet a measured one" when it is not
      (no live venue is reachable from this suite — `twin/market_signals.py`'s own admission).
      The verdict is exactly one of `yes`/`no`/`conditional`, each earned by a structural fact
      rather than a fresh opinion; against the committed rule and a pool shaped to satisfy it, it
      reads `yes`, citing decision ticket 21 Q3's own resolved cost (`MARGINAL_COST`) and value
      (`DISPROPORTIONATE_VALUE`) framing verbatim. Evidence:
      `twin/capabilities/forecast-book.yaml` AC 6; `tests/test_benchmark.py`'s eight new tests
      (`test_verdict_is_yes_when_the_delivered_set_spans_every_bin`,
      `test_verdict_is_conditional_when_the_delivered_set_does_not_span_every_bin`,
      `test_verdict_is_no_when_the_delivered_set_is_empty`,
      `test_verdict_reports_cadence_as_designed_not_measured_with_no_resolutions`,
      `test_verdict_reports_a_measured_cadence_from_real_resolutions`,
      `test_verdict_declares_the_same_computed_capability`,
      `test_verdict_capability_share_is_computed_against_the_live_capability_count`,
      `test_the_committed_rule_yields_a_yes_verdict_against_a_spanning_pool`).

## Where it actually lives

The draft above assumed `proportionality_verdict()` would sit in `twin/forecast_book.py`, beside
`CLAIM_SCOPE`. On inspection that module's own public surface is a deliberately closed allow-list
— harness guard `forecast_book_is_blind_by_construction_and_observe_only` asserts
`{emit, score_resolution, is_blind}` and nothing else, and adding a fourth function there fails
that guard immediately (confirmed live: `twin verify` failed on exactly this before the move). The
guard exists so "observe-only is structural" stays true without a keyword scan, and
`proportionality_verdict()` is not a position-placing function, but widening a deliberately narrow,
documented allow-list to admit it is a decision the guard's own author should make on purpose, not
a side effect of an unrelated ticket. The honest, lazy fix was to place the function in
`twin/benchmark.py` instead — it already houses `SelectionRule`/`BenchmarkSet`, the two real inputs
the verdict is checked against, and it imports `CLAIM_SCOPE` from `forecast_book.py` (one
direction, no import cycle) rather than duplicating it. `MARGINAL_COST`/`DISPROPORTIONATE_VALUE`
moved with it.

## Also found and fixed

- **Closing AC 6 moves `forecast-book` to `full` (6/6)**, which falsified five assertions written
  by earlier tickets that hardcoded "this capability stays `partial`" as a fact about the world
  rather than a fact about the code at the time: `tests/test_benchmark.py`,
  `tests/test_forecast_book.py` and `tests/test_market_signals.py` each had one
  `assert ... != "full"  # honestly partial` line, and `tests/test_grades.py` had two tests
  asserting `domain-model` was the *only* capability at `full`. Left unfixed, these would have been
  five new test failures caused by genuine progress, which the pytest baseline/after comparison
  would have surfaced as "new failures" rather than pre-existing ones. Updated all five to assert
  the honest current state (`== "full"`, and `{"domain-model", "forecast-book"}`) rather than
  deleting the checks — the point of each test (grade equals the computed grade; only capabilities
  that have actually earned it reach `full`) survives, only the hardcoded capability name/count
  needed correcting.
- **`twin/README.md`'s capability table, aggregate figure and two narrative sections were stale**
  the moment AC 6 closed: the table's `forecast-book` row (`partial`, `5/6`), the aggregate
  `test_the_published_aggregate_matches_the_computed_one` reads back out of the file (`45 of 73`),
  the "what is honestly built" `forecast-book` paragraph, and a bullet in "What is honestly
  incomplete" that said "only decision ticket 21 AC 6 ... stays open" — now false. All four
  recomputed live (`Capabilities.aggregate()` → `(46, 73)`) and updated, plus a new "The
  proportionality verdict" section narrating what this ticket actually built, the same shape every
  other build ticket's README section takes.
- **`forecast-book` reaching `full` moves `Capabilities.digest`, which every artefact pins as
  `tool.capabilities_digest` — so the committed golden byte fixture
  (`twin/invariants/golden-digests.json`) went stale the moment AC 6 closed**, the identical
  consequence build ticket 79 hit closing `domain-model`. Caught by the full suite, not assumed:
  `identical_pins_identical_bytes` and `test_artefacts_match_the_committed_golden_digests` both
  failed after the capability yaml edit, correctly — no scoring rule, serialisation or engine
  output changed, only the capability grade, and the goldens exist precisely to catch that class of
  drift. Re-blessed via `twin verify --bless-goldens --authorise "decision ticket 21 — ..."`, the
  same gated mechanism ticket 79 used, citing the decision ticket whose AC actually moved.

## Judgement calls made, not changed

- **The verdict's cost/benefit framing is decision ticket 21 Q3's own resolved reasoning, cited
  rather than re-derived.** `MARGINAL_COST`/`DISPROPORTIONATE_VALUE` restate Q3's prose (three
  already-built components; the only contamination-proof mechanism) rather than this ticket
  computing an independent cost or value figure from scratch. That is a deliberate reading of the
  AC: it asks for a verdict checked against "decision ticket 21's own stated cost/benefit framing",
  not a fresh cost/benefit analysis. What *is* newly computed, not restated, is whether the
  delivered coverage actually earns that framing today — the `yes`/`no`/`conditional` branch.
- **`resolution_cadence` falls back to the rule's designed horizon window (7–365 days) rather than
  computing a number from zero resolutions.** No live venue is reachable from this suite
  (`twin/market_signals.py`'s own admission, unchanged by this ticket), so there is no real
  resolution data to compute a cadence from yet. Stating the designed window and saying plainly
  that it is not yet measured was judged more honest than inventing a synthetic cadence figure or
  omitting the field.

## Evidence

Baseline (before this ticket's changes), `.venv/bin/python -m pytest -q`:

```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1455 passed in 281.84s (0:04:41)
```

After this ticket's changes, `.venv/bin/python -m pytest -q` (final run):

```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1463 passed in 325.56s (0:05:25)
```

Same single pre-existing failure (`test_the_suite_is_green`, which itself fails only because of
`drift_window_is_actually_being_sampled` and `flux_coverage_floor_is_still_reachable` — the two
named, unrelated, already-recorded gaps this project's own culture tracks separately, see
`.scratch/twin/build/70-*.md` finding 1). +8 net passing (the new `proportionality_verdict()`
tests), zero new failures.

`.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:

```
Success: no issues found in 150 source files
```

`.venv/bin/python -m twin verify` (final run):

```
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5 day(s) old ...
  FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no longer be reached ...
```

Same two pre-existing, named, unrelated failures as the recorded baseline (confirmed live before
this ticket's changes: `67 passed, 3 failed` — the third being
`forecast_book_is_blind_by_construction_and_observe_only`, which failed transiently while
`proportionality_verdict()` briefly lived in `twin/forecast_book.py` and passed again once it
moved to `twin/benchmark.py`, see "Where it actually lives"). `identical_pins_identical_bytes`
and `test_artefacts_match_the_committed_golden_digests` also failed transiently after the
capability yaml edit and before `twin verify --bless-goldens` re-recorded the golden bytes — see
"Also found and fixed".

```
$ .venv/bin/python -c "
from twin.grades import Capabilities
caps = Capabilities.load()
print(caps.require('forecast-book').grade, caps.require('forecast-book').summary())
print(caps.aggregate())
"
full {'grade': 'full', 'owning_ticket': '21', 'checked': 6, 'total': 6, 'unchecked': []}
(46, 73)
```
