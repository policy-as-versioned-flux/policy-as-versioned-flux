# 85 — Currency regimes: the last incommensurable

**What to build:** `currency-regimes` is 5/6. The remaining AC asks for treatment of every named
incommensurable, including where the twin refuses to price. Five of six are already handled:
reputation/morale via `twin/pricing.py`'s refusal register (five named reasons), existential/tail
risk via `twin severity`/`severity-anchor` (tickets 24/25). The sixth, ethical harms, was noted in
`twin/capabilities/currency-regimes.yaml` as waiting on the affected-parties register — but that
register (`twin/affected_parties.py`) already exists, built for decision ticket 15's misuse-catalogue
work. Check live, before scoping new code, whether it is already wired to the incommensurables
register or just sitting unconnected next to it.

**Blocked by:** none

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 09 (`.scratch/twin/issues/09-currency-regimes.md`).
`twin/capabilities/currency-regimes.yaml` for exact AC text. `twin/pricing.py`,
`twin/affected_parties.py`.

- [x] AC 4 — "Treatment of each named incommensurable, incl. where we refuse to price." Verified
      live: `twin/affected_parties.py` already answered the ethical-harms leg — built at build
      ticket 61 for decision ticket 15's Q4 mechanism list, it already names every non-contracting
      party a scenario declares and already refuses to price their harm
      (`twin/constraints.yaml`'s `harms-to-non-contracting-parties`) — but it was unwired from
      decision ticket 09: nothing in the artefact or the checklist said this *was* the sixth
      incommensurable. This was the small-connection case, not the new-machinery one. Wired in at
      `twin/affected_parties.py`'s `published()` `currency_note`, which now names "decision ticket
      09 AC 4's ethical-harms leg" directly, and exercised by
      `tests/test_affected_parties.py::test_published_names_ethical_harms_as_the_incommensurable_it_treats`.
      `twin/capabilities/currency-regimes.yaml` AC 4 ticked; `currency-regimes` reaches `full`
      (6/6), `./bin/twin grade` aggregate moves from 51/73 (4 full) to 52/73 (5 full).

## Also found and fixed

- **The golden-digest guard fired, correctly.** `currency-regimes` reaching `full` changes
  `Capabilities.digest`, which every emitted artefact's `depth` block carries — so the committed
  cross-architecture golden digests (`twin/invariants/golden-digests.json`) went stale the moment
  AC 4 ticked, and `tests/test_seam1_cli.py::test_artefacts_match_the_committed_golden_digests`
  failed on twelve artefact kinds that have nothing to do with `affected_parties.py`. Not a
  regression: `twin verify --bless-goldens --authorise "decision ticket 09 — ..."` is the
  sanctioned re-recording path (the same one build ticket 82 used when `ethics-gate` reached
  `full`), and it is gated exactly the way `--rehash` is — it refuses to move a digest without a
  citation. Re-blessed, citing this ticket.
- **Two harness guards in `tests/test_grades.py` hardcode the shipped-`full` set by name** —
  `test_only_domain_model_forecast_book_synthetic_substrate_and_ethics_gate_have_earned_full` and
  `test_domain_model_forecast_book_synthetic_substrate_and_ethics_gate_are_the_shipped_capabilities_at_full`
  — and both refused a fifth legitimately-`full` capability. Updated both to include
  `currency-regimes` (and renamed the first to name it), the same maintenance every prior ticket
  that reached `full` for the first time (79, 84, 87, 82) already did to this same pair of tests.
- **Self-review typo:** the first draft of the new README paragraph called ethical harms "the
  fifth of the six named incommensurables" — it is the sixth. Fixed before commit.

Neither finding changed AC 4's own scope; both are the mechanical, structural consequence of
closing it for real, and both are exactly what these guards exist to catch.

## Evidence

`.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:
```
Success: no issues found in 150 source files
```

`.venv/bin/python -m twin grade` (relevant lines):
```
==> currency-regimes: full  (6/6 of decision ticket 09)
  [x] 4. Treatment of each named incommensurable, incl. where we refuse to price.
        build ticket 85: ...
==> aggregate: 52 of 73 across 13 capabilities, 5 at `full`
```

`.venv/bin/python -m pytest -q tests/test_affected_parties.py tests/test_grades.py tests/test_seam1_cli.py::test_artefacts_match_the_committed_golden_digests`:
```
..............................                                           [100%]
30 passed in 10.82s
```

Full suite before any change (baseline): `1 failed, 1482 passed` — the sole failure
`tests/test_invariant_suite.py::test_the_suite_is_green`, itself aggregating two pre-existing,
already-known-red invariants (`drift_window_is_actually_being_sampled`,
`flux_coverage_floor_is_still_reachable` — see ticket 65/70/78, the Flux verdict is recorded as
closing `unmeasured`).

Full suite after this ticket's change (`.venv/bin/python -m pytest -q`):
```
1 failed, 1483 passed in 364.58s (0:06:04)
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionError...
```
Same single pre-existing failure, one more passing test than baseline (the new ethical-harms
test) — zero new failures, zero failures fixed (drift/flux-floor are recorded, not re-probed,
per the standing decision).

`.venv/bin/python -m twin verify` (after `--bless-goldens`):
```
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5 day(s) old ...
  FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no longer be reached ...
```
(Down from 3 failed before `--bless-goldens`: re-blessing also cleared `identical_pins_identical_bytes`,
which was red only because the stale committed golden digests no longer matched the new,
correctly-`full` `currency-regimes` depth block.)
