# 80 — Sense→move: wire observation propagation into `sense()`, and exercise it for real

**What to build:** Two related gaps in `sense-move`, both narrow.

`twin/primitives.py` already has fully-tested `Observe`/`updated_beliefs()`, correctly distinguished
from `Do`/`severed()` — bidirectional propagation vs downstream-only. But `twin/verbs.py`'s
`sense()` (~line 174) never calls it: a bound signal stops at the binding and never propagates.
The only caller of `Observe` is the standalone `twin observe` CLI verb, disconnected from the sense
loop this decision ticket is actually about.

Separately, no beat script (`twin/beat-netflix.sh`, `twin/beat-intel.sh`, `twin/beat-royal-mail.sh`)
ever calls `twin sense` — confirmed by grep, zero hits. Unit tests exercise the sense/bind path in
isolation (`tests/test_refusals.py`, `tests/test_corroboration.py`) but the checklist's own
convention (every other `ticked_by` line cites a real command run, not just a unit test) is unmet.

**Blocked by:** none

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 11 (`.scratch/twin/issues/11-sense-move-loop.md`).
`twin/capabilities/sense-move.yaml` for exact AC text. `twin/primitives.py`, `twin/verbs.py`.

- [x] AC 4 — "Observation-propagation semantics, distinguished from ticket 08's intervention
      propagation." Have `sense()` run `updated_beliefs()` on each component binding and include
      the reach (which components' beliefs updated, upstream and downstream) in the bound-signal
      artefact body. Add a test showing a bound signal's belief update reaches an ancestor,
      contrasted directly against an intervention on the same edge staying downstream-only —
      the distinction this AC names, made concrete rather than asserted.
      `twin/verbs.py` `sense()` now runs `propagate_mod.propagate()` (downstream) and
      `primitives_mod.updated_beliefs(graph, Observe(component))` (upstream) on every
      component-kind binding and publishes both under a `propagation` field on the binding —
      `twin/verbs.py:237-251`.
      `tests/test_primitives.py::test_sense_reaches_an_ancestor_the_same_component_intervention_would_not`
      exercises it against the real Netflix fixture data `sense()` already binds
      (`price-separation-announced` → `dvd-by-mail`): sensing reaches the causal ancestors
      `streaming-experience` (depth 1) and `content-delivery-network` (depth 2), and an
      `intervene()` on the identical component over the identical edges reaches neither —
      the distinction made concrete against real data, not asserted only against the bare
      primitives (which `tests/test_primitives.py`'s pre-existing tests already covered).
- [x] AC 8 — "Exercised on a real signal for each co-flagship." Add a `twin sense` step to
      `beat-netflix.sh` and `beat-intel.sh` against real signals already used elsewhere in this
      project's tests (Netflix: `price-separation-announced`; Intel: a signal from the real Intel
      fixture) — ideally the same signals AC 4's propagation change touches, so the beat script
      demonstrates the exact mechanism this ticket adds, not an unrelated one.
      **The draft's own example signal doesn't exist on the beat scripts' subject.** `twin
      fixture --name netflix` builds `fixtures.build_netflix_org` (the real, dated Netflix
      spine build ticket 73 built), not the toy overlay `price-separation-announced` lives in —
      confirmed live (`twin sense --signal price-separation-announced` against the real fixture
      refuses: "no signal 'price-separation-announced' in overlay 'netflix'"). `beat-netflix.sh`
      step 0b now senses `q4-2011-letter-2012-01-25` (bound to `streaming-service`) instead —
      the real checkpoint AC 4's own change touches, since it is the one whose late arrival
      first supplies the causal edge `dvd-by-mail → streaming-service` (see "Also found and
      fixed" below for why that signal's binding claim needed touching, and honestly, for the
      five other Netflix and eight other Intel checkpoints that still don't). `beat-intel.sh`
      step 0b
      senses `tan-14a-customer-guidance-2026-01-23` (bound to `leading-edge-foundry-node`) from
      the real Intel spine build ticket 75 built. Both steps run live and print the reach; both
      beat scripts pass end to end (see Evidence).

## What still isn't true

Intel's real fixture (`fixtures.build_intel_org`) carries no causal (`influences`) edge between
its two components (`leading-edge-foundry-node`, `external-foundry-customer-base`) at all, so
`beat-intel.sh`'s sense step genuinely finds zero reach in either direction — reported honestly
in the step's own output ("none — no causal edge into/out of this component yet") rather than
manufactured. AC 8 asks for the step to run against a real signal, not for that org's own causal
layer to exist; adding one is no part of this ticket's scope and is not attempted here.

Five of the six real Netflix checkpoints, and eight of the nine real Intel checkpoints, still
carry a binding claim graded at their signal's own sourcing grade (1 or 2) rather than the grade
5 `sense()` requires — so `twin sense` still cannot run against them. Only the one signal each
beat script now demonstrates was touched (see "Also found and fixed"); fixing the rest is a
real, named, out-of-scope gap, not attempted here.

## Also found and fixed

- **Spec axis, real gap.** The ticket's own suggested Netflix signal, `price-separation-announced`,
  does not exist anywhere `beat-netflix.sh` can reach — it lives only in the toy overlay
  `fixtures.build()`/`repo`/`scratch_repo` use, and the beat script builds
  `fixtures.build_netflix_org` (the real, dated spine, build ticket 73). Confirmed live before
  changing anything (`twin sense --signal price-separation-announced` against the real fixture
  refuses `no signal 'price-separation-announced' in overlay 'netflix'`). Fixed by using a real
  checkpoint that actually exists on the beat's own subject (`q4-2011-letter-2012-01-25`) instead
  of forcing the draft's example, per this project's honesty rule ("follow the real scope, not
  the draft's guess").
- **Spec axis, real gap, found while making AC 8 actually run.** Every real-org fixture built for
  the co-flagship and answer-key backtests (Netflix, Intel, Carillion, NMC, Wirecard, Enron,
  AstraZeneca, Sanofi, Kodak, Maersk) authors its `binding`-kind claims at the *signal's own
  sourcing grade* (1 primary / 2 trade-press), not the grade 5 `sense()` requires of a binding
  claim "by construction" (build ticket 43, decision ticket 11 Q2 — a binding is a classification
  act, not a magnitude claim, and the toy fixture's own `bind-price-separation-to-dvd-by-mail`
  already carries grade 5 despite weak reading confidence, for exactly that reason). This is why
  AC 8's checklist gap existed at all: nobody had ever run `twin sense` against a real fixture, so
  nothing had caught it. Fixing every fixture's binding grade is a large, unauthorised change well
  outside this ticket's stated scope ("two related gaps, both narrow"); fixed narrowly instead —
  `fixtures.py`'s `_netflix_claim`/`_intel_claim` gained an optional `binding_grade` override,
  applied only to `NETFLIX_SENSE_DEMO_SIGNAL`/`INTEL_SENSE_DEMO_SIGNAL`, leaving every other
  checkpoint's grade exactly as it was (see "What still isn't true").
- **Standards axis, real gap.** `twin/invariants/golden-digests.json` needed re-blessing twice,
  not once: the first bless (right after wiring `sense()`) only changed `bound-signal`'s digest,
  but ticking `sense-move` AC 4/AC 8 afterward changed the capabilities digest embedded in every
  artefact's pins, moving all twelve. Caught by re-running the full suite after the capability
  file edit rather than treating the first green run as final — a second `pytest -q` after a
  checklist edit is now the pattern this ticket's own evidence trail records.
- **Standards axis, real gap.** Two tests hard-coded the set of capabilities allowed to be `full`
  (`tests/test_grades.py`) and one hard-coded that `sense-move` must stay non-`full`
  (`tests/test_ingest.py`) — both correct when they were written, both now stale because
  `sense-move` genuinely reached `full`. Fixed: the two `test_grades.py` tests (renamed to name
  `sense-move` alongside the other five) now assert it; `test_ingest.py`'s test dropped the
  incidental `!= "full"` pin and kept the real property under test (the depth block reads the
  checklist's grade, whatever it is, rather than asserting one of its own).
- **Standards axis, judgement call, not fixed.** The top-of-file banner
  ("**This is 75 of 78 build tickets closed...**") is already stale independent of this ticket —
  a live recount against tracked `.scratch/twin/build/*.md` files finds more than 78 exist and
  more than 75 are done, and several other tickets landed concurrently with this one without
  touching that line either. Left alone: it names a fact this ticket's own change does not
  affect, and a shared, frequently-touched banner is exactly the line to avoid colliding on
  when other tickets are landing at the same time.

## Evidence

```
$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 150 source files

$ .venv/bin/python -m pytest -q
[...]
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1484 passed in 335.40s (0:05:35)
```

The one failure is pre-existing and unrelated (the same one the true, unmodified baseline shows —
recorded below): `drift_window_is_actually_being_sampled`, named in project memory as an
already-known, owner-accepted gap (the drift probe's crontab was never installed). Baseline, taken
by stashing every change this ticket makes and re-running the full suite against unmodified
`main` (`a60a994`):

```
$ git stash push -- tests/test_primitives.py tests/test_grades.py tests/test_ingest.py \
    twin/beat-intel.sh twin/beat-netflix.sh twin/fixtures.py twin/verbs.py \
    twin/invariants/golden-digests.json twin/capabilities/sense-move.yaml twin/README.md
$ .venv/bin/python -m pytest -q
[...]
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1483 passed in 337.28s (0:05:37)
$ git stash pop
```

One new test, zero new failures, same one pre-existing failure by name.

```
$ .venv/bin/python -m twin verify
[...]
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5 day(s)
       old [...] The probe has stopped [...]
  FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no
       longer be reached [...] **This guard staying red is the finding, not a defect in it**
       — see build ticket 70's finding 1.
```

Both pre-existing, both already named in project memory (the Flux drift probe's crontab was never
installed; recorded, not restarted).

```
$ .venv/bin/python -m twin grade --capability sense-move
==> sense-move: full  (8/8 of decision ticket 11)
  [x] 1. A signal object defined in ubiquitous language, with provenance + STEEP class.
  [x] 2. The binding mechanism decided, incl. what is automated vs judged vs reviewed.
  [x] 3. Authored-vs-inferred position decided, consistent with ticket 07's authored/derived split.
  [x] 4. Observation-propagation semantics, distinguished from ticket 08's intervention propagation.
        build ticket 80: [...]
  [x] 5. Weak-signal retention + promotion rule.
  [x] 6. A stated position on sensor gameability.
  [x] 7. The loop's cadence + re-price triggers, sufficient to generate forecast volume.
  [x] 8. Exercised on a real signal for each co-flagship.
        build ticket 80: [...]
```

```
$ bash twin/beat-netflix.sh
[...]
==> 0b. THE SENSE STEP — a bound signal is an observation, and belief updates both ways (build ticket 80)
  signal q4-2011-letter-2012-01-25 binds streaming-service; belief updates UPSTREAM about
  ['dvd-by-mail'] (an observation, decision ticket 11 Q4) and DOWNSTREAM about (nothing further
  downstream of streaming-service) — an intervention on this same component would reach the same
  downstream and none of that upstream
[...]
PASS: a threat path and an opportunity path both ran end to end on the same dated state. [...]

$ bash twin/beat-intel.sh
[...]
==> 0b. THE SENSE STEP — a bound signal is an observation, and belief updates both ways (build ticket 80)
  signal tan-14a-customer-guidance-2026-01-23 binds leading-edge-foundry-node; the observation
  walk ran both ways and found UPSTREAM (none — no causal edge into this component yet),
  DOWNSTREAM (none — no causal edge out of it yet)
[...]
PASS: swept through the scheduled production line, pinned and agent-signed [...]
```
