# 65 — The Flux falsification verdict

**What to build:** **Run the test rather than assume the answer.** What does the risk basis require?

**The question was widened from two branches to three on 2026-08-10**, three days into the 91-day
measurement window and before any verdict could be read from the data. The original pair:

1. **Continuous proof of force**, meaning reconciliation from a signed pinned source.
2. **Point-in-time proof**, meaning a deploy-time attestation suffices.

The third branch, which did not exist when the pair was framed:

3. **Continuous proof at the ACTION boundary rather than the STATE boundary.** Flux proves the
   *state* of a control between deploys. An action-boundary monitor proves *no action crossed* the
   control, continuously and fail-closed. Both are continuous. They are continuous about different
   things, and a control can hold its declared state for a whole window while an action crosses it.

**Ticket 64's window cannot see branch 3, and its addendum now says so.** It measures state drift
only. So a null result falsifies branch 1 and leaves branch 3 untouched. Reading a null result as
"Flux is a convenience, therefore point-in-time suffices" would be a false dichotomy, on the
critical path, written into a durable artefact.

**This branch is not an AWS product decision.** Action-boundary monitoring has at least five
independent implementations, of which AWS Dogwood (2026-08-06) is the newest and, on the evidence,
not the best: Progent (Apr 2025), AgentSpec (ICSE 2026, Mar 2025), Agent-C (Mar 2026), Causal Past
Logic (May 2026), VIGIL (Jun 2026). Judge the *class*, not the product.

**If branch 1 fails, Flux is a convenience rather than an enabler, and the spec is amended.** Write
the amendment either way; a test whose negative result changes nothing was not a test.

**Blocked by:** 64, 29, 11

**Status:** pre-registered, **VERDICT PENDING** — 2026-08-15. The same honest split build tickets
64 and 78 drew for themselves. Everything that must be fixed *before* the result is known is built,
tested and committed: the risk basis, the three branches, the coverage floor, the decision rule and
the spec amendment for the failing case. What is not done is the verdict, because the data cannot
carry one — build ticket 64's window is 9% elapsed at **1% coverage** and closes 2026-11-06.

> **Two of the nine criteria below are open and stay open until the window closes.** Reading the
> verdict now, at this coverage, is the same act as truncating the window once it looked worse. The
> decision rule is in code and the elimination path is closed, so when the data does arrive the
> reading is mechanical rather than argued — which is the whole point of doing this half first.

**Reading list:** Decision ticket 22. Spec stories 81, 85.

- [ ] The verdict is derived from ticket 64's measured drift data, not from argument.
      **Open, and open on purpose.** The derivation is built — `twin/verdict.py`'s `decide()` reads
      `drift.coverage()` and `drift.events()` and returns a branch state, so no step between the
      data and the verdict is an argument. What is missing is the data: 1% coverage, window closes
      2026-11-06. `_state_branch` returns `pending` with the coverage figure in the reason rather
      than a verdict, and `tests/test_verdict.py::test_below_the_coverage_floor_no_branch_resolves`
      asserts that an unsampled window that ran its full length is still not a falsifier.
- [x] The risk basis is stated precisely: which priced impact, at which evidence grade, requires continuity.
      `verdict.yaml`'s `risk_basis`, stated in the £ engine's own terms rather than in general
      ones: an impact prices only if every hop on its causal path is graded at or inside
      `path_admission_threshold` (build ticket 29). A deploy-time attestation evidences an
      **instant**, so a hop claiming the control held across the **interval** since rests on an
      unobserved mechanism — grade 3, which may not price. Continuous reconciliation evidences the
      interval itself — grade 1. So continuity is required exactly where a priced impact's path
      carries an interval-shaped hop, and nowhere else. `Protocol.load` refuses a protocol whose
      declared `path_admission_threshold` or ladder version disagrees with the live
      `twin/evidence-ladder.yaml` (`test_a_protocol_disagreeing_with_the_live_ladder_does_not_load`),
      so the statement cannot rot away from the gate it cites.
- [x] A written verdict either way, with the spec amendment drafted for the failing case before the result is known.
      `verdict.yaml`'s `amendment_if_falsified`, written 2026-08-15 with the window at 1% coverage
      and 83 days left to run. It names what spec story 81 loses (the "verification substrate"
      half), what the Enactment section loses and gains, and where a priced impact that leaned on
      the dropped evidence goes instead (build ticket 19's unpriced structural blast radius).
      **Drafted, not applied** — applying it now would presume the result. `Protocol.load` refuses
      a protocol that omits it (`test_a_protocol_with_no_drafted_amendment_does_not_load`), because
      a test whose negative result changes nothing was not a test.
- [~] If Flux survives, its role is stated as narrowly as the evidence supports.
      **Written, not yet earned.** `decide()` emits, for the surviving case, exactly one sentence:
      Flux is the evidence a control held its declared **state** between deploys, and it is not
      evidence that no action crossed the control. `test_a_drift_event_at_full_coverage_holds_the_
      state_branch` and `test_the_overall_verdict_needs_every_branch_resolved` exercise that path on
      a synthetic full-coverage log, so the narrowing is committed before the result rather than
      negotiated after it. It stays `[~]` until real data reaches the branch.
- [x] **All three branches are answered separately.** A null state-drift result closes branch 1 only, and the verdict says so explicitly rather than concluding branch 2 by elimination.
      **Closed in code rather than warned against**, because the defect is an inference and no
      arithmetic test catches one. `point-in-time` is the residual branch and resolves only when
      **both** other branches are falsified; `continuous-action` cannot be falsified without a
      window nobody has opened, so the residual cannot resolve at all today.
      `test_a_falsified_state_branch_never_concludes_the_point_in_time_branch` asserts it on the
      strongest null result the state instrument can produce — full coverage, closed window, zero
      drift events — and the residual still reads `pending`.
- [x] **Branch 3 is answered on the class, not on any product.** If the answer needs evidence, it needs its own pre-registered window; the verdict records that no such window is open rather than inferring one is unnecessary.
      `verdict.yaml`'s `continuous-action` branch names six implementations, Dogwood last and
      marked as the newest rather than the best. `Protocol.load` refuses the branch if it names
      fewer than two (`MINIMUM_CLASS_IMPLEMENTATIONS`,
      `test_the_action_branch_resting_on_one_product_does_not_load`) — one name is a procurement
      opinion wearing a falsification test's clothes. Its state is `unmeasured`, never `falsified`,
      and its reason says no pre-registered window measures it and none is open
      (`test_the_action_branch_is_unmeasured_and_says_no_window_is_open`).
- [x] The verdict cites `estate/driftwood/drift/window.yaml`'s `scope_limit` addendum and states what the instrument could not see.
      `Window` now carries `does_not_measure` and `scope_consequence` from the addendum, and every
      `decide()` result returns them under `scope_limit`. A citation that means re-opening the yaml
      is one an artefact quietly stops making, so `decide()` **refuses** a window that declares no
      scope limit rather than footnoting the omission, and refuses one that names the limitation
      without naming what it does to the reading
      (`test_a_window_with_no_scope_limit_yields_no_verdict` and
      `test_a_window_whose_scope_limit_states_no_consequence_yields_no_verdict`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added, `flux_verdict_is_pre_registered_and_derived` — the same class of
      addition build tickets 34, 56 and 78 already used, and for the same reason: it guards a
      yardstick (the pre-registration) and a semantic property (the closed elimination path), not
      one of the sixteen named absences. No constitutional invariant, no
      `twin/invariants/manifest.yaml` entry and no `checks_module_sha256` changed. Four direct
      tests exercise all four of its raise sites
      (`tests/test_invariant_suite.py::test_a_verdict_protocol_committed_after_the_window_closed_is_caught`
      and three siblings) — build ticket 78's own review found untested failure branches to be a
      real gap, this ticket's first draft repeated it on the fourth arm, and the review below caught
      it.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      **No owning decision ticket exists.** The reading list names decision ticket 22 and build
      ticket 64 already recorded that no such ticket was ever written — `.scratch/twin/issues/22`
      is the demo slice. The Flux falsification test is recorded in spec stories 81 and 85 and
      nowhere else, so `twin/grades.py`'s machinery (which grades a capability against a *decision*
      ticket) has no yardstick to compute against, the same position build tickets 34, 56 and 78
      found. This checklist is the evidence instead, and it computes to **partial**: seven of nine
      met, one partial, one open, with the two unmet items naming the date their evidence arrives.
      A capability file claiming `full` here would be the invented yardstick decision ticket 15's
      refusal already ruled out at build ticket 27.

## Why this half ran while the ticket is still blocked

**The ticket is blocked by 64 and that has not changed.** What moved is the recognition that its
third criterion — *"the spec amendment drafted for the failing case **before the result is
known**"* — cannot be satisfied at any later date. Waiting for 2026-11-06 and then drafting the
amendment would produce a file whose git history proves it was written with the data in view, which
is precisely what the harness guard added here refuses. The criterion has a deadline of *now*, and
every criterion that does not depend on the measurement travels with it for free.

So the ticket splits the way build ticket 64 split: the half that must precede the data is done and
committed, the half that reads the data is open and named. Nothing here reads a verdict, and
`./bin/twin verify` proves it on every run rather than on this file's say-so.

**The blocking chain is unchanged and still real.** 66 → 67 → 68 → 70 → the beats all wait on 65's
verdict, which waits on the window. The constitution's own note stands: relaxing `66 ← 65` is the
next largest available cut, because the propose-only PR channel needs no verdict — only the
policy-pinning half does.

## What is honestly not yet true

There is **no verdict**. The state branch is `pending` at 1% coverage, the residual branch is
`pending` because it always will be until a second window exists, and the action branch is
`unmeasured`. `twin drift` prints all three and prints `none yet — no branch has earned one`.

The action-boundary window is still not open. This ticket records its absence in a third place now
(the window's addendum, this ticket, and `verdict.yaml`'s `settled_by`) and does not open it.
Opening it is a real instrument against a real cluster, the same shape and cost as build ticket 78,
and it needs its own ticket rather than a paragraph in this one.

**Build ticket 64's probe is stale as this is written** — its newest sample is 2026-08-13 and
`drift_window_is_actually_being_sampled` is red. That is the known, pre-existing failure, and it is
also the single biggest threat to this ticket ever closing: at the current sampling rate the window
reaches its close well below the 90% floor, and a below-floor close resolves nothing in either
direction. The crontab line is in `window.yaml` and installing it remains the operator's.

## Also found and fixed: two-axis review of the working tree

Same discipline build tickets 56 and 78 name for themselves. Findings recorded and fixed, not
glossed over. Both axes ran against the diff *before* these fixes.

- **Spec axis, the serious one.** The elimination path was **not** actually closed. `decide()` read
  the rule off the yaml — `protocol.branches[RESIDUAL].get("entailed_only_if_both_falsified", [])`
  — so deleting one key from a data file re-opened the exact false dichotomy this ticket exists to
  refuse, and the reviewer reproduced it: full coverage, closed window, zero drift, and `decide()`
  returned `"point-in-time attestation suffices"`. The module's own docstring gave the reasoning
  that should have caught it, about `BRANCHES` — "a protocol that declares its own branch set could
  drop one and still validate against itself" — and then did not apply it to the more important of
  the two rules. Fixed: `ENTAILS_RESIDUAL` is hardcoded beside `BRANCHES`, the file still declares
  the rule so a reader of the pre-registration can see it, and `Protocol.load` refuses a file that
  disagrees with the code. Two tests added, one for the refusal and one asserting the door stays
  shut even when a *loaded* protocol's rule is mutated in memory.
- **Spec axis, real gap.** The guard had four raise sites and three tests, and the untested one was
  the arm that goes live the day the window closes — an uncommitted `verdict.yaml`. Build ticket
  78's own review found untested failure branches to be a real gap and this repeated it one ticket
  later. Fixed: `test_an_uncommitted_verdict_protocol_after_the_window_closed_is_caught`.
- **Spec axis, scope creep — reverted, not defended.** `twin drift` had grown a printed verdict
  block. No acceptance criterion asks for CLI output, and it coupled build ticket 64's command to
  build ticket 65's file hard enough that a malformed `verdict.yaml` would break a working command.
  Removed entirely. The verdict is readable from `./bin/twin verify`'s guard line and from
  `verdict.yaml` itself; a surface of its own can wait for the half of this ticket that has a
  verdict to show.
- **Spec axis, minor.** `decide()` refused a blank `does_not_measure` but accepted a blank
  `consequence_for_the_verdict`, so half a citation still shipped. Both are required now.
- **Spec axis, minor.** The window's falsifier says coverage **above** 90% and the comparison was
  `<`, so exactly 90.0% read as sufficient. Now `<=`, with the strict reading — the one that
  refuses a verdict — chosen deliberately, and `test_exactly_the_floor_is_not_above_the_floor`
  pinning it.
- **Standards axis, real.** `twin/README.md`'s "The invariants" section carried three stale
  numbers, the same drift build tickets 56 and 78 each found and fixed once before: "1 skipped"
  when `twin verify` reports 2, "1236 tests" when the live count is 1263, and a claim that
  `drift_window_is_actually_being_sampled` is "the one check in the suite that reads the actual
  wall clock" — which this ticket's own guard falsified in the same diff. All three re-derived from
  live runs.
- **Standards axis, real.** The ladder cross-check looped over `("path_admission_threshold",
  "version")` with an inline key rewrite, so a version mismatch raised `declares version 2, the
  live evidence ladder says 3` — naming a key `verdict.yaml` does not have. Fixed with explicit
  `(our_key, ladder_key)` pairs.
- **Standards axis, real.** `cmd_drift` imported `drift` a second time under an alias while the
  same function already had it bound. Moot now the block is reverted.
- **Standards axis, judgement call, fixed anyway.** `requires_window_closed` was a knob with one
  live value and no test for the other. Kept, because it is pre-registered data a reader must see,
  and now exercised: `test_a_protocol_that_does_not_require_a_closed_window_reads_one_early`.
- **Standards axis, judgement call, not fixed** — noted, left as found: two of the guard's tests
  monkeypatch `verdict.decide` and mutate its returned dict, which pins that dict's layout. With
  the elimination rule now enforced from code there is no craftable protocol that opens the door,
  so a boundary fixture cannot reach the guard's arm at all — the monkeypatch is the only way to
  assert it, and the same precedent already exists for `_first_commit_date`.
- **Both axes agreed on one thing worth recording:** nothing in the change declares ticket 65 done,
  no capability file claims `full`, and the 7/9 checklist arithmetic is right.

## Evidence

Re-run after the review fixes above.

```
.venv/bin/python -m pytest tests/test_verdict.py tests/test_drift.py -q
  44 passed

.venv/bin/python -m pytest tests/test_invariant_suite.py -q
  22 passed, 1 failed
  FAILED test_the_suite_is_green — drift_window_is_actually_being_sampled: known, pre-existing,
  unrelated (build ticket 64's probe stale since 2026-08-13; this ticket's new guard,
  flux_verdict_is_pre_registered_and_derived, is not in the failure list and passed clean)

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 132 source files

.venv/bin/python -m pytest -q
  1262 passed, 1 failed in 329.92s (0:05:29) — the same single, pre-existing, unrelated failure,
  unmoved by anything this ticket touched. 1263 collected.

.venv/bin/python -m twin verify
  RESULT: 59 passed, 1 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  Same known failure. 58 → 59 is this ticket's own harness guard going live, not a change
  elsewhere in the suite.
  40  PASS  flux_verdict_is_pre_registered_and_derived  3 branches, floor 90%, amendment drafted;
            state=pending, residual=pending, action=unmeasured, verdict=none yet
```

## Found later: the floor had an expiry date and this ticket never computed it

Added by build ticket 70's confirmatory audit, 2026-08-15, following build ticket 34's precedent of
amending the ticket that should have caught a finding rather than only naming it.

This ticket pre-registered `minimum_coverage: 0.90` and honestly recorded the shortfall against it
("9% elapsed at **1% coverage**"). What it did not do is compute what that shortfall would cost.
Pre-registering a threshold against a sampled instrument commits you to a **deadline**, whether or
not anybody works it out: unsampled hours cannot be sampled later, so the floor stops being
reachable at a fixed moment. For this window that moment is **2026-08-16T05:00Z** — 1966 samples
needed of 2184 owed, 3 taken, and from then on no probing schedule reaches it.

The reading gate is `requires_window_closed: true`, so this ticket's own machinery looks at coverage
for the first time on 2026-11-06, which is the first moment nothing can be done about it. That is
correct for reading a verdict and useless as a warning. The two needed to be separate and were not.

**What changed:** `twin/drift.py` `floor_reachable()` and the harness guard
`flux_coverage_floor_is_still_reachable`. `Protocol.load` also now refuses a floor of 1, which the
old `0 < floor <= 1` admitted and which no window can ever clear under an *above-the-floor* gate.

**Consequence for this ticket, recorded rather than fixed.** The owner was asked during the audit
whether to install the probe schedule and declined. So `continuous-state` will close **`unmeasured`**
rather than `falsified`, `amendment_if_falsified` above does **not** fire, spec story 81 is not
amended, and the residual `point-in-time` branch cannot be concluded either. The elimination path
staying closed on this outcome is this ticket's own protection working as designed. Nothing here is
weakened to accommodate that: the floor stands at 0.90 and the window stands as declared.
