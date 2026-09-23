# 123 — A regulator's withdrawal refuses the adopter as a removal

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-23 from eco-system ticket
[120](120-the-eighteen-unchecked-candidates-against-adr-0026.md). It is one of three survivors
of the eighteen loophole candidates against ADR-0026. Round 3's `loophole-3` pointed at it.
Reproduced by `tests/test_loophole_adr_0026.py`, leg
`test_a_regulator_withdrawal_refuses_the_adopter_as_a_removal`, against platform origin/main
`b2820d8`.

The candidate said a control the regulator withdraws leaves the adopter's selection with no
price and no trace, while an adopter's own removal is priced. That is false: the composition
refuses. The place is real, and it is the other way round.

1. **The composition cannot tell a withdrawal from a removal.** `check_selected_set` in
   `compose/composition.py` compares the selected set with the last signed header's
   `selected-controls` and refuses `removed-control` on any control that left. It never asks
   why the control left.
2. **Measured.** In the composition selfcheck's own fixture estate, an adopter selects the
   baseline `SMALL` and composes. The regulator's next catalogue drops `aa-2` from the catalogue
   and from `SMALL`. The adopter changes nothing, byte for byte. Its next composition refuses,
   `removed-control` on `aa-2`, whose detail says "a control may be added, never removed
   (ADR-0013)".
3. **The record says the opposite.** ADR-0026's Consequences: "A control the regulator withdraws
   from its catalogue is not an adopter removal: it leaves the selected set with the catalogue
   bump". The revisit trigger it names is "the first such bump". The first such bump will refuse
   every adopter that selected the control, for an act none of them took.

The removal refusal itself is a known lag. ADR-0026 point 5 retires it and its Consequences name
the platform build that must price it instead (charted in
[124](124-the-removal-adr-0026-prices-has-no-build.md)). That build alone does not repair this.
After it lands, a withdrawal would print as a `removed-control` delta under the adopter's
perspective: a removal the adopter did not make, in the adopter's name.

What this ticket owes:

1. Decide, as delegated under ADR-0025, how the composition tells the two apart. Known shape:
   a control that left the selected set and is also gone from the pinned catalogue, or from the
   named baseline at the new pin, left with the regulator's bump. It prints its own delta kind
   naming the catalogue versions, not `removed-control`.
2. Say what a weights feed that still names a withdrawn control does. ADR-0026 calls it "that
   feed's own fact to fix in its next version".
3. Land with ticket 124 or after it. Both change `check_selected_set`.

## Done

`test_a_regulator_withdrawal_refuses_the_adopter_as_a_removal` flips to a regression test: a
catalogue bump that withdraws a selected control composes, prints a delta that names the
regulator's bump, and never names the adopter as the one who removed it.

## Build, 2026-09-22

Built on platform branch `ticket-123-a-withdrawal-is-the-regulators` (platform PR 33) and hub PR 99 on hub
branch `ticket-123-a-withdrawal-is-the-regulators`. The platform branch sits on platform
origin/main `f5213df`, after ticket 124 (`6c29a30`) and ticket 119. It does not touch
`ungoverned_namespaces` or the `since` lookup, which ticket 122 changes.

### What was built

- `split_withdrawn` in `compose/composition.py` replaces the plain use of `removed_controls`. It
  asks one question of each control that left the selected set: would the adopter's last
  baseline name and last overlay still select it against the catalogue pinned now? If yes, it is
  the adopter's `removed-control`. If no, it is the regulator's `withdrawn-control`.
- `withdrawn_deltas` prints the new kind. Each delta carries `withdrawn_by` (the regulator),
  `reason` (`catalogue` or `baseline`), `catalogue.from` and `catalogue.to` (the pin on each side
  of the bump, `<version>@<sha12>`), the amount the hole carried and `priced_by`. Its detail names
  the regulator and the bump and never the adopter.
- The header records `overlay-controls`: what the adopter's own overlay selected.
  `compose/comparison_history.py` carries it as an optional field, so a header from before it
  still validates and projects without it.
- A regime line whose control the pinned catalogue withdrew reads `withdrawn`.
- Hub: `verify/priced-holes/priced_holes.py` admits `withdrawn-control` and the `withdrawn`
  regime status. The loophole leg flipped to a regression test and three legs joined it.
  CONTEXT.md's **Hole** and **Delta** entries and ADR-0026's ticket-120 note are updated.

### Decisions (all delegated, ADR-0025)

1. **One counterfactual tells the two apart.** Ask whether the adopter's last inputs would still
   select the control against the catalogue pinned now. Reason: it is the only question whose
   answer changes with the adopter's act and not with the regulator's. It covers a catalogue
   withdrawal, a same-name baseline drop, and both acts in one run with one rule.
2. **A catalogue "no longer defines" a control when the id is absent or carries
   `status: withdrawn`.** Reason: NIST keeps withdrawn controls in its catalogue under that
   status and drops them from every baseline. Measured: 182 of the 1196 ids in the pinned nist
   catalogue carry it. An absent-id rule alone would never fire on a real NIST withdrawal.
3. **The header records `overlay-controls`.** Reason: a same-name baseline drop and an overlay
   removal look the same without knowing what the last overlay selected. Reading the old
   catalogue from the old pin needs the regulator's git history, which a vendored or fixture tree
   does not have. The field is optional in the comparison history, because absent (the header
   predates the field) is not the same fact as empty.
4. **A header without `overlay-controls` tells only a catalogue withdrawal apart.** A same-name
   baseline drop then stays the adopter's removal. Reason: the other default would book an
   adopter's own overlay removal as the regulator's. That opens a loophole; this default only
   keeps the old attribution for one run.
5. **Both acts in one run go to the adopter.** A control the adopter's last overlay still
   selects, and the catalogue still defines, is the adopter's removal even when the regulator
   also dropped it from the baseline. Reason: had the adopter kept its overlay, the control
   would still be selected.
6. **A control of the adopter's own catalogue is never a withdrawal, and nor is one from a
   source the adopter stopped pinning.** Reason: the adopter publishes the first and dropped the
   second. The round 1 `loophole-1` leg (a bespoke withdrawal prints `removed-control`) still
   passes.
7. **A new delta kind, `withdrawn-control`, and the adopter's perspective stays on it.** Reason:
   every delta carries the adopter's perspective and currency, and the hub grader checks that.
   The perspective says whose pound the amount is. Who acted is `withdrawn_by`.
8. **Item 2: a weights feed that still names a withdrawn control.** The composition does not
   refuse and does not re-partition. The `withdrawn-control` delta carries the price the pinned
   weight gives the hole, and its detail says the feed still names a withdrawn control. The
   regime entry keeps its amount, and that control's line reads `withdrawn`. Reason: ADR-0026
   calls it the feed's own fact to fix in its next version. Re-partitioning here would mint a
   number no publisher signed.
9. **The survivor verdict stays `survivor`.** Only its test name and fact line changed. Reason:
   the survival count is a record of what ticket 120 found, and ADR-0030's note states it.

### Measured

- Before the change, `tests/test_loophole_adr_0026.py` passed 16 of 16 with the survivor leg
  asserting the defect.
- Red: the flipped leg and the three new legs failed on platform origin/main: no
  `withdrawn-control` delta, and no `overlay-controls` in the header. The weights leg first
  printed `removed-control` for `pl-2` at 2711937.31 GBP. Two new `tests/test_priced_holes.py`
  cases failed until the grader admitted the kind and the status.
- Green, with a scratch estate whose `platform` is this branch:
  `.venv/bin/python -m pytest tests/test_loophole_adr_0026.py tests/test_priced_holes.py -n0 -q`
  gives 41 passed. `tests/test_loophole_rounds_two_and_three.py tests/test_misuse.py` gives 53
  passed, 6 skipped. mypy over `twin tests conftest.py` is clean on 199 files.
- Platform, with `PAVC_ESTATE_CLONE` set to the shared estate clone: `composition.py
  --selfcheck` exits 0 with 93 OK lines; origin/main gives 89. `python3 -m unittest
  test_comparison_history` runs 12 tests, OK. `verify-composition.sh` exits 3 on the branch and
  on origin/main, with the same step 2 SKIP (platform@2.0.1 lacks the rendered versions).
- `verify/priced-holes/priced_holes.py check` exits 1 with 3 FAILs, the same 3 with this change
  stashed. All three are tuppence evidence that predates ticket 119.
- Real estate, composed with this branch: LOW, MODERATE and HIGH select 149, 287 and 370 ids,
  none withdrawn. driftwood, tuppence and ludlow each select 287, and each regime entry has 4
  weighted lines, none withdrawn. So no real regime line changes status today. Each header
  gains `overlay-controls: []` on its next compose.

### What remains

- **Owner:** a signed platform tools release that carries this build, and each adopter's pin
  moving to it. Then re-compose and push driftwood, tuppence and ludlow. Only then does an
  adopter's own evidence print a withdrawal as the regulator's. These are enactment and release
  steps.
- **The revisit trigger** in ADR-0026, the first real withdrawal bump, has not happened. The
  first real run of this code on a bump waits on a regulator.
- **A gap this build found and did not close.** ADR-0026 says an adopter still naming a
  withdrawn control in `overlay.controls` meets `unknown-control-id`. That holds for an id the
  catalogue drops. It does not hold for one NIST keeps under `status: withdrawn`. Measured:
  tuppence with `overlay.controls: [ac-2.10]` composes with no refusal and selects `ac-2.10`.
  It needs its own ticket. Closing it changes what a claim against a withdrawn id does, which
  is wider than this ticket.
