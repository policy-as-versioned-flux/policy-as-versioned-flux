# 82 — Ethics gate: the named sensor set, and the behavioural misuse catalogue

**What to build:** Two artefacts, both closed-table, both named directly by decision ticket 15 and
both explicitly carried forward rather than built by any ticket so far.

AC 2 wants an enumerated sensor list with declared granularity. `twin/ethics_gate.py` has the
admission ladder (walks a payload through purpose → necessity → proportionality) but accepts any
sensor id as a string — there is no closed table of named sensors it checks against, unlike
`enactment-channels.yaml`'s closed-table pattern for enactment channels.

AC 4 wants a *behavioural*-sensing misuse catalogue — grievance suppression, layoff justification,
surveillance creep — distinct from `twin/misuse-catalogue.yaml` (build ticket 62), which is scoped
to misuse of the twin's own governance/pricing/scoring machinery. Confirmed by grep: no pay/layoff/
surveillance entries exist in the ticket-62 catalogue. This is a second catalogue, not an extension
of the first — decision ticket 15's own Q3/Q3b table already names the cases in prose.

**Blocked by:** none

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 15 (`.scratch/twin/issues/15-sensing-ethics-misuse.md`), its Q3/Q3b
table specifically. `twin/capabilities/ethics-gate.yaml` for exact AC text. `twin/ethics_gate.py`,
`twin/misuse.py`, `twin/misuse-catalogue.yaml`, `twin/constraints.yaml`.

- [x] AC 2 — "The sensor set + granularity decision." A versioned `twin/sensors.yaml` (mirrors
      `enactment-channels.yaml`'s shape) naming each sensor, what it observes, and its
      coarsest-safe granularity. A loader that refuses an entry missing declared granularity.
      `ethics_gate.admit()` checks a payload's sensor id against this table rather than accepting
      any string.
      **Closed.** `twin/sensors.yaml` — a versioned, closed table of six sensors (the five
      `ethics_gate.labelled_corpus()` proposals plus `payroll-record`, the one enactment channel
      that observes people). `twin/ethics_gate.py load_sensors()` refuses a row missing a declared
      `kind` or `granularity` (`tests/test_ethics_gate.py::test_load_sensors_refuses_an_entry_missing_a_declared_granularity`,
      `::test_load_sensors_refuses_an_unknown_kind_or_granularity`,
      `::test_load_sensors_refuses_a_sensor_declared_twice`). `admit()` refuses a payload whose
      `sensor.id` is not in the table (`::test_admit_refuses_an_unnamed_sensor_id`) before the
      ladder is even walked. `twin/capabilities/ethics-gate.yaml` AC 2 ticked.
- [x] AC 4 — "A named misuse catalogue, each with its blocking constraint." A second catalogue file
      (e.g. `twin/behavioural-misuse-catalogue.yaml`), scoped to behavioural-sensing misuse per
      decision ticket 15's own Q3/Q3b table (suppressing pay, justifying layoffs, surveillance
      creep). Each entry names the misuse and which constraint or gate step blocks it, cross-
      referenced against `constraints.yaml` and `ethics_gate.py`'s ladder. Loaded and asserted the
      same way `twin/misuse.py` loads and asserts `misuse-catalogue.yaml` — reuse that loader's
      shape rather than inventing a second one; do not conflate the two catalogues' scopes.
      **Closed.** `twin/behavioural-misuse-catalogue.yaml` — the eight named misuses of decision
      ticket 15's own Q3 table (Q3b's five adversarial findings are not repeated here; they were
      already encoded in `twin/constraints.yaml`'s `scope_exclusions`/`positions` before this
      ticket, sourced to "decision ticket 15, Q3b finding N" — confirmed by reading that file).
      Loaded through `twin/misuse.py`'s existing `load_catalogue(BEHAVIOURAL_CATALOGUE_PATH)` —
      no second loader added. Scope separation checked directly, not merely asserted:
      `tests/test_misuse.py::test_the_two_catalogues_do_not_conflate_their_scopes` asserts no id
      overlap and that neither catalogue's own ids contain "pay"/"layoff"/"surveillance" words
      belonging to the other's scope. `twin/capabilities/ethics-gate.yaml` AC 4 ticked;
      `ethics-gate` reaches `full` at 5/5.

## Also found and fixed

- **A judgement call made, then reversed, on `twin-inside-twin` AC 5.** Decision ticket 10's own
  AC 5 ("named misuse cases with the constraint that blocks each") reads as arguably the same
  criterion this ticket closes for decision ticket 15: its resolution explicitly carries the AC
  forward "to the ethics/reflexive-governance workstream", and its own Question text names the
  identical three worked examples (justifying layoffs, suppressing pay, surveillance creep) this
  catalogue covers. I ticked it, then found build ticket 83 (blocked by this one, already drafted
  in full) reads that same AC narrower and differently — misuse *of the twin itself by its own
  operator* (gaming a sensor's metric, selectively citing forecasts), extending build ticket 62's
  governance catalogue rather than this ticket's behavioural one. Ticking it here would pre-empt
  a call a ticket built specifically for that question should make with the fuller picture, so I
  reverted the tick and left it unchecked — `twin/capabilities/twin-inside-twin.yaml` AC 5 stays
  `checked: false`, and `twin/README.md`'s "What is honestly built" section states the tension
  explicitly rather than picking a side silently.
- **The golden digests needed re-blessing.** Ticking `ethics-gate` AC 2/AC 4 changes the depth
  block every emitted artefact carries, so `identical_pins_identical_bytes`
  (`tests/test_invariant_suite.py::test_every_live_invariant_actually_asserts_something`) failed
  against the previously-committed goldens for 12 artefact kinds — confirmed genuinely caused by
  this ticket, not a flake, by reproducing it on a clean stash of this ticket's changes (passes)
  and back on top of them (fails, deterministically, twice). Re-blessed with
  `twin verify --bless-goldens --authorise "decision ticket 15 — ..."`, the sanctioned,
  citation-gated path `cli.py _bless_goldens()` already provides — `twin/invariants/golden-digests.json`
  is part of this commit.
- **`tests/test_grades.py` pinned "only three capabilities are `full`" by name.** Two tests
  (`test_only_domain_model_forecast_book_and_synthetic_substrate_have_earned_full`,
  `test_domain_model_forecast_book_and_synthetic_substrate_are_the_shipped_capabilities_at_full`)
  hard-coded the exact set of `full` capabilities and failed once `ethics-gate` genuinely joined
  it — the correct failure mode for a pinned test meeting a real change, not a bug in the test.
  Updated both (renamed to name `ethics-gate` too) to assert the new, real set of four.
- **The two other README count reconciliations this ticket's own change requires** were re-derived
  live from `./bin/twin grade` rather than hand-incremented: the top-of-file capability table
  (51/73, four `full`) and the "What is honestly built" narrative bullet for decision ticket 15 —
  both would otherwise have gone stale the way ticket 77's own review found elsewhere in this file.

## What still isn't true

- Decision ticket 15's own Q3b adversarial-pass findings are not in `twin/behavioural-misuse-catalogue.yaml`
  — deliberately: they are a different shape (structural blind spots, not per-misuse blocking
  constraints) and already live in `twin/constraints.yaml`. Named here so a future reader does not
  go looking for a ninth or tenth entry that was never meant to exist in this file.
- `twin-inside-twin` AC 5 remains open — see "Also found and fixed" above. Build ticket 83 is the
  ticket that should resolve it, one way or the other.

## Evidence

Baseline, before any change (recorded first, per project convention):

```
$ .venv/bin/python -m pytest -q
...
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionError: ['drift_window_is_actually_being_sampled: ...']
1 failed, 1474 passed in 301.03s (0:05:01)
```

After this ticket's changes, the same suite, twice in a row (once before, once after re-blessing
the golden digests — see "Also found and fixed"):

```
$ .venv/bin/python -m pytest -q
...
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionError: ['drift_window_is_actually_being_sampled: ...']
1 failed, 1482 passed in 301.01s (0:05:01)
```

Same single pre-existing failure, identity unchanged (`drift_window_is_actually_being_sampled` —
`flux_coverage_floor_is_still_reachable` is a `twin verify`-only check, see below); +8 net new
tests (5 in `tests/test_ethics_gate.py`, 3 in `tests/test_misuse.py`), zero new failures.

```
$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 150 source files
```

```
$ .venv/bin/python -m twin verify
...
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5 day(s) old ...
  FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no longer be reached ...
```

Both `twin verify` failures are the pre-existing, named, owned Flux-probe gap (see the memory
`project_flux_verdict_unmeasured` / build ticket 70's finding 1) — untouched by this ticket.

```
$ .venv/bin/python -m twin grade
...
==> ethics-gate: full  (5/5 of decision ticket 15)
==> twin-inside-twin: partial  (2/5 of decision ticket 10)
==> aggregate: 51 of 73 across 13 capabilities, 4 at `full`
```

`identical_pins_identical_bytes` genuinely regressed once `ethics-gate`'s grade changed (confirmed
by reproducing on a clean stash of these changes — passes — and twice on top of them — fails
deterministically both times), because the depth block every emitted artefact carries changed
bytes. Re-blessed the sanctioned way:

```
$ .venv/bin/python -m twin verify --bless-goldens --authorise "decision ticket 15 — build ticket 82 ticks ethics-gate AC 2 and AC 4 ..."
golden digests -> golden-digests.json (12 artefacts)
  ...
```
