# 81 — Causal layer: composed counterfactual semantics, an intervention-aware scoring rule, and Intel's own causal claim

**What to build:** Three related gaps, closing `causal-layer` from 2/5 to 5/5.

`twin/primitives.py` has `Do`/`Observe` (build ticket 22) and structural-only-path handling via
`needs` edges (build ticket 20) as separately-existing, separately-tested pieces. Abduction (build
ticket 35) and fast-forward (build ticket 37) likewise exist separately. Decision ticket 08 AC 2
asks for these composed — abduction → action → prediction as one documented, tested path — with
behaviour on structural-only paths stated for the composition, not just the individual legs.

AC 3 asks for the scoring rule to be intervention-aware, with a worked example: a mitigation that
prevented an event should score differently from one that never had an event to prevent. Grep shows
several modules reference "mitigat..." but none tie an intervention to a scored outcome end to end.

AC 5 asks for a real causal claim exercised on each co-flagship. Netflix already has one
(Qwikster→churn, build ticket 74). Intel does not — `fixtures.build_intel_org` (build ticket 75) was
built for a pinned forward forecast only, by design, and carries no causal edge. This ticket adds
one real, cited causal claim to the Intel fixture: EUV lithography delay → process-node slip.

**Blocked by:** 80 (touches `twin/primitives.py` and `twin/verbs.py`; sequencing after 80's
observation-propagation change avoids two tickets editing the same seam out of order)

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 08 (`.scratch/twin/issues/08-causal-layer.md`).
`twin/capabilities/causal-layer.yaml` for exact AC text. `twin/primitives.py`, `twin/pricing.py`,
`twin/fixtures.py` (`build_netflix_org`, `build_intel_org`).

- [x] AC 2 — "Defined intervention + counterfactual semantics, incl. behaviour on structural-only
      paths." Compose abduction (35) → action (`Do`, 22) → prediction (fast-forward, 37) as one
      function or documented, directly-tested path. State and test what happens when the composed
      chain crosses a structural-only (`needs`-edge) path.
      `tests/test_four_verbs.py::test_the_full_counterfactual_composes_abduction_action_and_prediction`
      calls `primitives.rewind` (abduction), `verbs.intervene` carrying `Do` (action) and
      `verbs.run` (prediction/fast-forward) off the identical abducted commit, asserted by pin
      rather than assumed. The two prior tests each composed only two of the three legs
      (`test_counterfactual_is_rewind_then_intervene`: abduction+action;
      `test_backtest_is_rewind_then_run`: abduction+prediction) — what
      `twin/capabilities/causal-layer.yaml`'s own prior note called "two thirds of a composition".
      Structural-only-path behaviour is stated and tested for this same composed chain, not only
      for `propagate()` at rest: `do(cloud-compute)` (zero `influences` edges of its own) produces
      an empty priced prediction, while `verbs.blast` on the identical abducted-and-intervened
      state reports `streaming-experience` — a real `needs` dependent — as unpriced exposure.
- [x] AC 3 — "The intervention-aware scoring rule, with a worked example of a mitigated non-event."
      Score a claim where an intervention (mitigation) prevented an event differently from an
      identical claim with no intervention and no event — the worked example is the evidence, not
      prose about the rule.
      `twin/schema.py`'s `outcome` schema gains an optional `mitigation` field, reusing
      `response.mitigates`'s own validator. `verbs.score` (`twin/verbs.py`) gates a non-event's
      calibration eligibility on it at the identical evidence threshold `pricing.py`'s own
      mitigation credit already uses (`evidence.may_price`): grade 1-2 excludes the forecast from
      the calibration record (`unscoreable`, reason `MITIGATED_NON_EVENT`) rather than scoring it
      as a miss; no claim, or a claim graded 3-5, scores exactly as before. The worked example:
      `tests/test_intervention_aware_scoring.py` — one forecast bundle, three outcome records
      resolving the identical proposition false,
      `test_a_well_evidenced_mitigation_excludes_the_non_event_from_the_calibration_record` (grade
      1, unscoreable), `test_the_identical_claim_with_no_mitigation_scores_as_an_ordinary_non_event`
      (scored, an ordinary calibration point) and `test_a_weakly_graded_mitigation_claim_earns_no_calibration_credit`
      (grade 4, byte-identical to the no-claim case — "grades 4-5 earn NO calibration credit",
      literal). A fourth test confirms the gate never engages when the event happened anyway.
- [x] AC 5 — "Exercised on a real claim from each co-flagship (Qwikster→churn; EUV delay→node
      slip)." Netflix side already done (build ticket 74) — cite it. Add the Intel side: a real,
      sourced EUV delay → process-node slip causal edge on `fixtures.build_intel_org`, exercised the
      same way the Netflix edge is.
      `fixtures.build_intel_org` gains `euv-lithography` (component) and `euv-delay-slips-the-node`
      (a grade-2 `influences` edge, `euv-lithography` -> `leading-edge-foundry-node`), dated and
      cited to Intel's own 2014-09-04 decision to forgo EUV at the 10nm node (Krzanich, Citi Global
      Technology Conference, reported by KitGuru) and the multi-year node slip that followed
      (Krzanich's own July 2015 earnings-call admission; Tom's Hardware and TOP500's retrospectives),
      contrasted with the subject's own current High-NA EUV bet on the identical component and its
      own reported 2026 go/no-go decision point. Exercised live: `twin/beat-intel.sh` step 0c runs
      `twin propagate --origin euv-lithography` and asserts a real, grade-2, non-directional
      elasticity reaches `leading-edge-foundry-node`; step 0b's sense step now finds
      `euv-lithography` upstream of the bound component too. Asserted in pytest:
      `tests/test_intel_beat.py::test_the_real_euv_causal_edge_composes_to_a_priced_elasticity`.

## Also found and fixed: two-axis review of the diff

Same discipline build tickets 77 and 78 name for themselves: findings recorded and fixed, not
glossed over.

- **Standards axis.** `twin/beat-intel.sh` step 0b's own comment and printed message — "this org's
  two components carry no causal edge between them yet" — would have gone stale silently the
  moment AC 5's edge landed, misleading a reader of the live demo output about what the twin
  actually finds now. Fixed: the comment and print statement name the edge and assert
  `euv-lithography` appears upstream of the bound component (the step now fails loudly if it does
  not), and a new step 0c exercises `twin propagate --origin euv-lithography` directly, checked
  live rather than only described.
- **Standards axis.** `tests/test_grades.py`'s two hardcoded assertions of exactly which
  capabilities have earned `full` went stale the moment `causal-layer` reached full — the same
  shape of drift build ticket 78's own review found in `twin/README.md`. Fixed: both tests now
  include `causal-layer`, one test's own name and docstring updated to name it the seventh full
  capability; `twin/README.md`'s table, its "Six"→"Seven capabilities" prose and its published
  aggregate (54 of 73 → 57 of 73) were all re-derived live from `./bin/twin grade`, never
  hand-incremented (`tests/test_grades.py::test_the_published_aggregate_matches_the_computed_one`
  checks this mechanically).
- **Mechanical consequence, not a defect, recorded for the reader who greps `twin verify`'s
  output next.** Editing `twin/capabilities/causal-layer.yaml` moves `Capabilities.digest`, which
  is embedded in every artefact's `pins.tool.capabilities_digest` — so `identical_pins_identical_bytes`
  failed against all twelve committed golden artefacts until re-blessed
  (`twin verify --bless-goldens --authorise "decision ticket 08 — build ticket 81 ..."`), the same
  step every prior capability-grade-moving ticket in this project's own git log has needed.

**Judgement calls, considered and left as found:**

- The outcome-level `mitigation` claim (AC 3) does not validate that its `component` names a real
  component in the org's graph at schema-validation time. This matches `response.mitigates`'s own
  existing precedent exactly: `pricing.py`'s `_credit()` does not validate the mitigated
  component's existence either — it looks for a *priced impact* at that name and reports
  `NOTHING_PRICED_THERE` if none exists, the same shape of soft failure. Consistency with the
  established pattern, not a stricter or looser rule invented for this ticket.
- A mitigation claim graded 3-5 falls through to plain scoring with no visible "considered and
  declined" marker on the score entry, unlike `pricing.py`'s own weak-claim register entries which
  carry a named reason. The numeric outcome is identical either way (decision ticket 08 Q4's own
  words, "grades 4-5 earn NO calibration credit", hold exactly), and AC 3's literal wording asks
  for the worked example to show the scoring differs — which it does, by inclusion in `scores` vs
  `unscoreable` — not for a third, cosmetic field. Left out rather than added speculatively.
- AC 2's structural-only-path test uses `cloud-compute`, chosen because it carries zero causal
  edges of its own in the fixture, giving the cleanest possible contrast (an empty priced
  prediction against a real, named, unpriced exposure). A component that is reached by *both* a
  causal hop and a structural-only hop on the same walk is a different, already-covered case
  (`twin/blast.py`'s own `classify()`, `all_causal`, exercised by that module's own test suite);
  re-covering it here under an intervention would be duplication, not new evidence, so it was not
  added.

## What is honestly true now, and what still isn't

True, and computed rather than asserted: `causal-layer` is 5/5 (`./bin/twin grade --capability
causal-layer`, re-run live, not carried from this ticket's own draft). The three-leg Pearl
composition (rewind → `Do` → `run`) is called together and pinned to the identical abducted
commit in one test, with structural-only-path behaviour stated and tested for that same composed
chain rather than only for `propagate()` at rest. The intervention-aware scoring rule is real
code — a schema field plus a use-gate in `verbs.score`, reusing the identical evidence threshold
`pricing.py` already gates £ credit on rather than inventing a second one — demonstrated by a
worked example that scores the *identical* claim two different ways depending on what the
outcome's own mitigation record says. The Intel co-flagship now carries a real, dated, cited
causal edge, exercised live the same way Netflix's is.

Still not true, or named as a deliberate limit rather than closed silently: AC 3's mitigation gate
lives only in `verbs.score` — it is not, and decision ticket 08 never asked it to be, wired into
`pricing.py`'s existing, separate £-credit machinery; the two share a vocabulary and a threshold,
not a code path, and joining them would be scope this ticket did not open. The EUV edge's
magnitude (elasticity 0.2/0.4/0.65, grade 2) is a genuine range grounded in real, dated,
sourced history, not a calibrated-range estimate from a trained forecaster at grade 1 — the note
on the edge says so itself, and the evidence ladder's own grade-2 example describes exactly this
shape of claim. The three judgement calls above are stated, not silently decided.

## Evidence

```
$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 151 source files

$ .venv/bin/python -m pytest -q
1490 passed, 1 failed in 369.31s (0:06:09)
FAILED tests/test_invariant_suite.py::test_the_suite_is_green — the wrapper around the same two
pre-existing, unrelated invariant failures `twin verify` names below (drift_window_is_actually_being_sampled,
flux_coverage_floor_is_still_reachable); every test this ticket added or touched
(tests/test_four_verbs.py, tests/test_intel_beat.py, tests/test_intervention_aware_scoring.py,
tests/test_grades.py) is in the 1490 passed, none in the 1 failed.

$ .venv/bin/python -m twin verify --bless-goldens --authorise "decision ticket 08 — build ticket 81
  moves causal-layer to full 5/5 (composed abduction/action/prediction, the intervention-aware
  scoring gate, and the real Intel EUV causal edge), which changes every artefact's depth block
  and the intel graph/propagation bytes"
golden digests -> golden-digests.json (12 artefacts)

$ .venv/bin/python -m twin verify
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: known, pre-existing (build ticket 78's own finding
  stays open; the probe has not been re-armed since)
  FAIL flux_coverage_floor_is_still_reachable: known, pre-existing (see project memory
  "Flux verdict closes unmeasured" — the owner recorded this rather than restarting the probe)
identical_pins_identical_bytes: PASS — 12 artefacts identical across runs, processes, hash seeds
and the re-blessed goldens.

$ .venv/bin/python -m twin grade --capability causal-layer
==> causal-layer: full  (5/5 of decision ticket 08)

$ .venv/bin/python -m twin grade   (tail)
==> aggregate: 57 of 73 across 13 capabilities, 7 at `full`
```
