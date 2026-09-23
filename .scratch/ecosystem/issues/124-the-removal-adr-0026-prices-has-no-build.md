# 124 — The removal ADR-0026 prices has no build

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by eco-system ticket
[120](120-the-eighteen-unchecked-candidates-against-adr-0026.md). This is not a loophole
survivor. It is the known lag ADR-0026 names, which ticket 120's rule 4 told its checker to
expect. Three of the eighteen candidates landed on it: round 1's `overreach-4`, round 2's
`loophole-1` and round 2's `overreach-4`. Checking them found that no ticket holds the build.

ADR-0026 point 5 decided on 2026-09-04 that a removal is priced, never refused. Its Consequences
list what "a platform build ticket" must change: delete the refusal in `check_selected_set`, add
the `removed-control` and `baseline-narrowing` delta kinds to `compute_deltas`, rewrite the
selfcheck's `run2-removed` case to expect `outcome: composed`, rewrite the party schema's
`overlay.controls` sentence, and add `removed-control` to the gone set in
`verify/priced-holes/priced_holes.py` `check_source`. Ticket 39's D9 left the number to the
integrator "at merge time". No ticket was opened. `grep -rln "removed-control"` over
`.scratch/ecosystem/issues/` on 2026-09-23 finds tickets 38, 39 and 120, and none of them is the
build.

Measured on platform origin/main `b2820d8` by
`tests/test_loophole_adr_0026.py::test_a_removal_still_refuses_where_adr_0026_says_the_code_lags`:
a narrowing from `SMALL` to `TINY` in the selfcheck's fixture estate is refused, `removed-control`
on `aa-1.1` and `aa-2`. The record has led the code for nineteen days.

What this ticket owes: the list above, in the platform repo, and the hub leg flipped to expect a
composed narrowing with two `removed-control` deltas and one `baseline-narrowing` delta. Ticket
[123](123-a-regulator-withdrawal-refuses-the-adopter-as-a-removal.md) changes the same function
and should land with this one or after it.

## Done

A removal composes and prints as priced deltas on platform main. ADR-0026's Consequences stop
saying the record leads the code, and `test_a_removal_still_refuses_where_adr_0026_says_the_code_lags`
is rewritten as a regression test of the priced removal.

## Build, 2026-09-22

Built on platform branch `ticket-124-price-the-removal` (platform PR 31, commit `f9311d8`, on
origin/main `101fe8a`) and hub branch `ticket-124-price-the-removal`. Merge platform PR 31
first, then the hub PR.

### What changed

Platform, `compose/composition.py`, only what ADR-0026's Consequences list:

- `check_selected_set` and its `removed-control` refusal are deleted. `removed_controls`
  returns the sorted keys that left the selected set.
- `_price_removed` gives each removed control the amount its hole carried: the regulator's
  weight times the triple, a bespoke control's own scenario residual, or a named absence.
- `compute_deltas` prints one `removed-control` delta per removed control and takes the
  `baseline-narrowing` summary from `baseline_narrowing_delta`. Both kinds join `DELTA_KINDS`.
- The selfcheck's `run2-removed` case expects `outcome: composed`, two `removed-control`
  deltas (`aa-1.1`, `aa-2`) and one `baseline-narrowing` delta, all named absences.
- `compose/verify-composition.sh` step 1b adds `removed-control` to its gone set.
- `party/schema.json`'s `overlay.controls` sentence and `compose/README.md` say a removal is
  priced, never refused.

Hub:

- `verify/priced-holes/priced_holes.py`: `removed-control` joins `GONE`. `removed-control` and
  `baseline-narrowing` join the `DELTA_KINDS` whitelist. The selfcheck fixture that planted
  `removed-control` as a passing refusal now must FAIL. The schema check fails a description
  that still says "May only grow" or "exemption by another name".
- `tests/test_priced_holes.py`: four new cases for those three changes.
- `tests/test_loophole_adr_0026.py`: the discard leg
  `test_a_removal_still_refuses_where_adr_0026_says_the_code_lags` is rewritten as
  `test_a_removal_composes_and_prints_as_priced_deltas`, the regression test of the priced
  removal. A new leg, `test_a_narrowing_prices_a_weighted_removal_and_names_each_unweighted_one`,
  holds round 2 `loophole-1`. The bespoke leg now withdraws its bespoke control and checks the
  delta carries the scenario's residual. The survivor 3 leg (ticket 123) now asserts the
  withdrawal composes as a `removed-control` delta in the adopter's name. Verdict facts that
  said "the removal still refuses" are rewritten. No verdict changes: 3 of 18 survive, as before.
- ADR-0026 Consequences: the "What the code does today" bullet now says ticket 124 built the
  priced removal. It no longer says the record leads the code.
- `verify/adr-supersession/verify-adr-supersession.sh`: requires "ticket 124 built the priced
  removal" and refuses "check_selected_set ... still refuses".

### Measured

All on detached origin/main worktrees of each unit (`.estate-clone/<unit>/.work/t124-<unit>`,
and a second set under the scratchpad for the selfcheck, below), never the shared clones.

- Red first: `tests/test_loophole_adr_0026.py` against platform origin/main `101fe8a` failed
  4 legs, each with `assert 'refused' == 'composed'`. `tests/test_priced_holes.py` failed its 4
  new cases before the grader change.
- Green: both files against the platform branch, 33 passed.
- The real narrowing leg: tuppence from MODERATE to LOW, against a nist copy whose LOW also
  drops the weighted `ra-3`. The composition composes, with 139 `removed-control` deltas. One
  is priced, `ra-3` at 2711937.31 GBP, the same amount its regime line carried. The other 138
  are named absences. The `baseline-narrowing` delta reads dropped 139, priced 1, amount
  2711937.31 GBP. The regime entry stays at 9039791.02 GBP before and after, and the `ra-3` line
  reads `unselected`.
- `composition.py --selfcheck` passes on the branch. A symlinked estate view makes it fail on
  both main and the branch, at the review F2 leak check, because a `could_not_look` message
  carries the symlinked path. So `compose/verify-composition.sh` ran in an estate of real
  detached worktrees: exit 3 on the branch and exit 3 on origin/main, the row's declared SKIP at
  step 2. Step 1b lists ten refusal kinds on the branch and eleven on main; the extra one is
  `removed-control`.
- `verify/priced-holes/verify-priced-holes.sh` with the hub branch grader: exit 1 against
  platform origin/main (source and schema FAIL), exit 0 against the platform branch. The hub
  main grader against the platform branch: exit 0.
- `verify/adr-supersession/verify-adr-supersession.sh`: exit 0, and its selfcheck exit 0.
- mypy over `twin tests conftest.py`: no issues in 199 source files.

### Gate rows

- `verify/priced-holes/verify-priced-holes.sh`: if the hub PR merges before platform PR 31,
  this row falls from PASS to FAIL. Merged in order, it stays PASS.
- `.estate-clone/platform/compose/verify-composition.sh`: SKIP (declared) before and after.
- `verify/adr-supersession/verify-adr-supersession.sh`: PASS before and after.

### Decisions (delegated, ADR-0025)

1. **A narrowing is a strict subset, mirroring the widening.** `baseline-narrowing` fires only
   when the new named baseline drops controls and adds none. A change that adds and drops
   prints its per-control deltas and no summary. Reason: point 5 says the narrowing mirrors
   point 3, and point 3's widening fires only on a strict superset.
2. **The narrowing counts only what left the selected set.** A baseline control the overlay
   still selects is not counted. Reason: the delta sits "beside" the `removed-control` deltas,
   and a control the adopter still selects moved no pound.
3. **Every removed control is priced the same way, covered or not.** Its amount is what a hole
   on it carries. Reason: point 5 says the removal carries "the amount the hole carried", and
   the regulator's weight prices the control whether or not the adopter selected or covered it.
4. **A removal never refuses for a missing instrument.** A bespoke control with no scenario, or
   a band in another currency, prints a named absence. Reason: point 5 lists a named absence as
   one of the three amounts, and refusing here would bring the wall back by another name.
5. **The survivor 3 leg keeps its name.** Ticket 123's Done names
   `test_a_regulator_withdrawal_refuses_the_adopter_as_a_removal`, so renaming it would break
   that ticket's reference. Its docstring and assertions now say the withdrawal composes as a
   `removed-control` delta in the adopter's name. Ticket 123 flips it.
6. **`removed_controls` replaces `check_selected_set` by name.** Reason: the function no longer
   checks anything. Ticket 123 changes the same place and will find it by this name.

### What waits on the owner

- A signed platform tools release carrying `f9311d8` (or its merge commit).
- Each adopter's platform pin moving to that release, and the re-compose and push that follows.
  Until then no adopter's evidence is composed by this build. Read on 2026-09-23 at each
  adopter's origin/main, driftwood, tuppence and ludlow each carry no refusal and an empty
  `deltas[]` in `composed/evidence.json`, so their evidence changes only when one narrows.
