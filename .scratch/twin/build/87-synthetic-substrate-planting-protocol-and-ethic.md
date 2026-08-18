# 87 — Synthetic substrate: the planting protocol's missing legs, and two checks that don't exist yet

**What to build:** Three gaps closing `synthetic-substrate` from 4/7 to 7/7.

AC 3 wants the planting protocol to cover strength, lead time, burial, and distribution of
difficulty. Lead time exists (`twin/planter.py`'s `actionability_horizon`), burial-in-context exists
as a scalar (`twin/substrate_eval.py`'s `plant_difficulty()`), but strength has no field and
difficulty distribution has no check — `plant_difficulty` currently checks a mean-target band, not
a declared spread.

AC 6 wants anti-contamination measures. The only contamination-discount machinery that exists
(`twin/scoring.py`'s Enron-as-control) is scoped to the real-history backtest suite, not the
substrate this ticket is about — confirmed by grep, no contamination check exists over
`twin/substrate.py`/`substrate_eval.py` output at all.

AC 7 wants an ethics/non-identification check. Zero code exists — only a prose comment in
`twin/fixtures.py`. No scan anywhere checks generated substrate content against real, identifiable
people or organisations.

**Blocked by:** none

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 12 (`.scratch/twin/issues/12-synthetic-substrate.md`).
`twin/capabilities/synthetic-substrate.yaml` for exact AC text. `twin/planter.py`,
`twin/substrate_eval.py`, `twin/substrate.py`, `twin/schema.py` (`Plant`).

- [x] AC 3 — "The planting protocol (strength, lead time, burial, distribution of difficulty)."
      Add a `strength` field to `Plant` in `twin/schema.py`. Add a batch-level check in
      `substrate_eval.py` that plants span a declared difficulty distribution, not just clear a
      mean-target band — extend the existing `TARGETS`/`UNFAIR_TEST_CONDITIONS` machinery.
      **Closed, with one correction to this ticket's own draft (see "Also found and fixed"):**
      `Plant` lives in `twin/planter.py`, not `twin/schema.py` — `schema.py` has no `Plant` at all
      and never did (`grep -n "class Plant" twin/`). `twin/planter.py`'s `Plant` dataclass now
      carries `strength: float`, a declared unit-interval value read from
      `twin/plant-horizons.yaml` beside the horizon and reason it already carries, enforced with
      the identical "every plant must carry one" discipline `plant()` already applies to the
      horizon (`tests/test_planter.py::test_plant_refuses_a_planted_signal_with_no_declared_strength`,
      `test_plant_refuses_a_strength_outside_the_unit_interval`). The committed Netflix recipe's
      four plants now declare real, differentiated strengths (0.4-0.85,
      `twin/plant-horizons.yaml`). "Distribution of difficulty" is
      `twin/substrate_eval.py::plant_difficulty_spread()` — the max-minus-min across a batch's own
      per-plant difficulty scores (refactored out of `plant_difficulty()` via a shared
      `_per_plant_difficulty_scores()` helper so the mean and the spread can never quietly
      disagree about one plant's score), added as a sixth `TARGETS` entry, band `(0.05, 1.0)`, and
      a new `UNFAIR_TEST_CONDITIONS` clause. A real negative control
      (`tests/test_substrate_eval.py::test_a_uniform_difficulty_batch_fails_plant_difficulty_spread`,
      using `UNCAMOUFLAGED_PLANTED_SIGNALS`) genuinely fails it at spread `0.0`, while the
      camouflaged default batch and the real committed Netflix substrate both show a genuine
      spread (0.333 and 0.6 respectively — `test_the_tuned_batchs_plants_show_a_genuine_difficulty_spread`,
      `tests/test_netflix.py::test_every_fidelity_dimension_lands_inside_its_band`).
- [x] AC 6 — "Anti-contamination measures." A check in `substrate_eval.py`, run as part of
      `evaluate_fidelity()`, that generated content doesn't parametrically leak or closely resemble
      real named companies or events — a blocklist or similarity check against a small known-real
      list, distinct from and not confused with the backtest suite's Enron-as-control mechanism.
      **Closed.** `twin/substrate_eval.py::KNOWN_REAL_ENTITIES` is a small, named blocklist — the
      org roster already committed across the backtest/flagship fixtures (Carillion, Enron,
      Wirecard, NMC Health, Kodak, Netflix, Intel, Maersk, AstraZeneca, Sanofi, Royal Mail) plus
      three real, publicly-named people tied to those same events — deliberately distinct from
      `twin/scoring.py`'s Enron-as-control discount (that mechanism prices memorisation on the
      real-history backtest suite; grep confirms it touches nothing in `substrate.py`/
      `substrate_eval.py`). `contamination_hits()` scans a batch's *free-running* content only,
      skipping any line identical to one of `spine.anchor()`'s own inserted facts — those
      legitimately name the real subject verbatim by design, and scanning them would flag the
      consistency mechanism decision ticket 12 Q3 requires, not a leak
      (`tests/test_substrate_eval.py::test_contamination_ignores_the_anchored_spine_facts`,
      which confirms a real anchored fact literally naming "Carillion" is present and still
      scores clean despite "Carillion" being on the blocklist). `contamination()` is a seventh
      `TARGETS` entry, zero-tolerance band `(0.0, 0.0)`, run inside `evaluate_fidelity()` as the AC
      asks. The real committed Netflix substrate scores `contamination == 0.0`
      (`tests/test_netflix.py::test_every_fidelity_dimension_lands_inside_its_band`).
- [x] AC 7 — "Ethics/non-identification check." A check (may share machinery with AC 6's scan) that
      flags any generated entity name or detail matching a real, identifiable person or organisation
      before a substrate batch is committed. Cite a test that proves the check actually fires on a
      planted real-name collision, not just that it runs.
      **Closed.** `twin/substrate_eval.py::refuse_if_contaminated()` shares `contamination_hits()`'s
      blocklist machinery with AC 6, as invited, but is the harder gate: not a target band a batch
      can still be reported as failing while shipping anyway, but a raised `ContaminationError` —
      the same shape `schema.refuse_special_category` uses for Article 9. Wired into
      `twin/substrate_report.report()`, called on the anchored batch immediately after the fidelity
      metrics and the spine diff are computed and before the `Artefact` is constructed — "before a
      substrate batch is committed" realised literally at this codebase's own commit point for a
      substrate batch's figures. Proven to fire on a planted collision, not merely to run clean:
      `tests/test_substrate_eval.py::test_refuse_if_contaminated_fires_on_a_planted_real_name_collision`
      plants "Markus Braun" (real, publicly identifiable — Wirecard's former CEO) into a
      constructed batch's free-running content and asserts the raised error names that entity;
      `test_refuse_if_contaminated_is_silent_on_clean_content` proves the same call does not raise
      on genuine content, so the gate is real and not merely always-on. No prior code checked
      generated substrate content against real, identifiable people or organisations at all — only
      a prose line in decision ticket 12 named the requirement before this ticket (the ticket
      draft's claim of "a prose comment in `twin/fixtures.py`" does not literally exist either;
      corrected in "Also found and fixed" below).

## Also found and fixed

- **This ticket's own draft named the wrong file for `Plant`.** It says "Add a `strength` field to
  `Plant` in `twin/schema.py`" and lists `twin/schema.py` (`Plant`) in the reading list. `grep -n
  "class Plant" twin/` shows `Plant` has only ever lived in `twin/planter.py` — `twin/schema.py`
  has no `Plant` class, and has never declared one (it is the closed model-repository schema
  format; the substrate's ground-truth `Plant` is a different type entirely, sealed to the
  planter/scorer). Followed the real code rather than the draft's guess: the field was added to
  `twin/planter.py::Plant`, and `twin/plant-horizons.yaml`/`horizons_for()`/`plant()` were extended
  to declare and validate it, the same discipline already used for the horizon.
- **The draft's claim about a "prose comment in `twin/fixtures.py`" does not literally exist.**
  Grepping `twin/fixtures.py` for ethics/non-identification language turns up nothing matching;
  the actual prior prose lives only in decision ticket 12 itself
  (`.scratch/twin/issues/12-synthetic-substrate.md`, "Ethics — the substrate is why the demo is
  exempt; keep it genuinely synthetic and non-identifying."). Noted rather than silently corrected,
  since it does not change what needed building — zero code existed for this check either way.
- **`plant_difficulty()` and `plant_difficulty_spread()` shared a computation, refactored rather
  than duplicated.** Both dimensions need one score per plant; extracting
  `_per_plant_difficulty_scores()` means the mean-based and spread-based dimensions read the
  identical per-plant number and can never quietly disagree about one plant's own difficulty.
- **`twin/substrate_report.py::_detection()` publishes `strength` per plant**, the same way it
  already publishes `actionability_horizon` and `horizon_reason` — a field added to `Plant` with
  no way for a report reader to ever see it would be plumbing nobody could inspect.
- **`horizons_for()`'s return arity grew from two to three** (`dates, reasons, strengths`), which
  is a breaking signature change; every call site in this codebase was updated in the same commit
  (`substrate_report.py`, `twin/invariants/harness.py`'s two guards, `tests/test_netflix.py`) —
  checked by grep for every caller, not assumed complete. `plant()` gained a required `strengths`
  parameter the same way, and every one of its ~11 call sites across
  `tests/test_planter.py`/`tests/test_scorer.py`/`twin/invariants/harness.py` was updated.
- **`twin/capabilities/synthetic-substrate.yaml` reaching `full` changes `Capabilities.digest`,
  which is embedded in every artefact's `tool.capabilities_digest` pin** — this moved every
  committed golden digest (`twin/invariants/golden-digests.json`), the identical, already-precedented
  consequence build ticket 84 recorded when it moved `forecast-book` to `full`. Re-blessed via
  `./bin/twin verify --bless-goldens --authorise "decision ticket 12 — ..."`; no scoring rule,
  serialisation or engine output changed, confirmed by the digests moving as one uniform block
  rather than selectively.
- **Six tests asserted `synthetic-substrate`'s grade was `"partial"` or an exact checked-set that
  excluded 3/6/7**, and would have failed the moment this ticket did its job:
  `tests/test_grades.py`'s two full-capability-set tests (one renamed, one exact-set extended),
  `tests/test_spine.py`, `tests/test_substrate.py`, `tests/test_substrate_generator.py` (all three
  had their `grade == "partial"` line removed, subset checks kept — the same forward-compatible
  shape earlier tickets already used elsewhere), and `tests/test_scorer.py` (its own checked-set
  assertion switched from `==` to a subset check, the one place in this family that had drifted to
  exact equality). `tests/test_scorer.py` also had a module-level `_PLANT` fixture and two more
  inline `Plant(...)` constructions with no `strength` — a collection-time `TypeError`, not a test
  failure, until fixed.
- **`twin/README.md` and `twin/cli.py` both had a "five [fidelity] dimensions" claim that quietly
  stopped being true**: the eval-suite section's opening description, its tuning-loop paragraph,
  its harness-guard paragraph, the "Run it" quick reference line for `twin substrate`, and
  `cmd_substrate()`'s own docstring in `twin/cli.py` all said "five"; corrected to the current
  count (or de-hardcoded where a specific ticket's historical count is what the sentence actually
  describes) rather than leaving five separate places where the number silently went stale.
- **The "What is not built" section's own substrate bullet asserted a gap** ("Still not built:
  decision ticket 12 AC 3's strength and lead-time clauses ... which is why `synthetic-substrate`
  sits at 4/7 rather than higher") **that this ticket closes** — trimmed to the one limit that is
  still genuinely true (the generator is a heuristic stand-in, not a live model call) rather than
  leaving a "what is not built" section naming something that is now built.

## What still isn't true

Nothing about decision ticket 12's own seven ACs — all seven are now checked with real citations.
Two judgement calls, stated rather than left silent:

- **`strength` is declared, not measured.** Unlike `plant_difficulty` or `plant_difficulty_spread`,
  nothing in this codebase computes a plant's strength from its own text — it is authored ground
  truth, the same status `actionability_horizon` already has. That is the honest reading of "the
  planting protocol's strength" (a property the planter declares about the signal it is planting,
  not a property a reader could recover by inspecting the batch), but it means `strength` does not
  yet feed any scoring or fidelity check the way the horizon feeds `scorer.score()`. No acceptance
  criterion asks for that; recorded so a future reader does not assume it is wired in.
- **`KNOWN_REAL_ENTITIES` is a small, hand-picked list, not a general named-entity recognizer.**
  AC 6 explicitly permits "a blocklist or similarity check against a small known-real list" — this
  is the blocklist reading, and it will not catch a real company or person not on the list. The
  list is the org roster already committed across every backtest/flagship fixture in this
  codebase, which is exactly the set a leak from this project's own training data would most
  plausibly resemble; a determined author could still author a collision with an unlisted real
  entity, the identical honest limit `schema.SPECIAL_CATEGORY`'s own docstring states for its Article
  9 word list.

## Evidence

```
$ grep -n "class Plant" twin/planter.py
140:class Plant:
```

```
$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 150 source files
```

**Baseline** (before this ticket's changes): `.venv/bin/python -m pytest -q` — 1463 passed, 1 failed
(`tests/test_invariant_suite.py::test_the_suite_is_green`, on the pre-existing, unrelated Flux
drift-floor finding — the same family named in this project's own working conventions as an
example of a known, already-accepted pre-existing failure).

**After this ticket's changes:**

```
$ .venv/bin/python -m pytest -q
...
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1474 passed in 316.55s (0:05:16)
```

The one remaining failure is the identical pre-existing, owner-accepted Flux drift-floor gap, not
introduced by this ticket — confirmed directly via `./bin/twin verify` below, which surfaces its
own name rather than pytest's aggregate wrapper:

```
$ ./bin/twin verify
...
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5
       day(s) old (2026-08-13T02:53:15+00:00). The probe has stopped, and a stopped probe writes
       no `unreachable` sample either — the silence is indistinguishable from stability
  FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no
       longer be reached: 3/1966 sample(s), only 79 days, 17:48:50 of window left ... **This guard
       staying red is the finding, not a defect in it** — see build ticket 70's finding 1. It goes
       green only if the floor is actually reached
```

Both are the recorded, owner-accepted Flux drift-floor gap (Chris Nesbitt-Smith owns the probe;
`window.yaml`'s `operation.crontab` line was never installed) — pre-existing and unrelated to
substrate work. Every substrate-chain check in the same run passes, including the two this ticket
touches directly:

```
24  PASS  substrate_fidelity_is_measured_and_tuning_closes_a_real_gap  evaluate_fidelity() returns
    exactly the 7 declared dimensions; ... a degraded batch fails 3 dimension(s) at once
    (plant_difficulty, plant_difficulty_spread, reporting_asymmetry)
26  PASS  netflix_substrate_is_free_running_and_every_plant_carries_a_horizon  ... every fidelity
    dimension is inside its band at 2011-10-24; the report reproduces byte-for-byte and scores
    every plant, misses included, at a hit rate of 0.25
27  PASS  netflix_runs_both_paths_and_the_curve_keeps_the_disagreement  ... 1/8 emitted artefacts
    claim synthetic-substrate and all carry the limitation
```

```
$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 150 source files
```

```
$ .venv/bin/python -c "from twin import substrate_eval as se; print(list(se.TARGETS)); print(len(se.UNFAIR_TEST_CONDITIONS))"
['signal_to_noise', 'plant_difficulty', 'plant_difficulty_spread', 'spine_consistency', 'reporting_asymmetry', 'mundanity', 'contamination']
7
```

```
$ .venv/bin/python -m pytest -q tests/test_grades.py tests/test_substrate_eval.py tests/test_substrate.py \
    tests/test_substrate_generator.py tests/test_spine.py tests/test_scorer.py tests/test_planter.py tests/test_netflix.py
119 passed in 9.04s
```
