# 126 — A control the catalogue marks withdrawn can still be selected

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 from ticket 123's build and review. It is unfixed.

NIST keeps 182 of its 1,196 control ids under `status: withdrawn`. An adopter's
`overlay.controls` can name one of them, for example `ac-2.10`, and platform
`compose/composition.py` selects it. It is not refused as `unknown-control-id`, because the
selection rule asks only whether the catalogue carries the id, under any status.

Two things follow:

1. An adopter can claim, and be priced as holding, a control the regulator has withdrawn.
2. Ticket 123's guard books the later removal of such an id as the adopter's own removal. That is
   correct under today's selection rule. With a legacy header that carries no `overlay-controls`,
   a real bump and the adopter's drop in the same run, the review found the id can still be
   booked as the regulator's withdrawal.

What this ticket owes:

1. Decide whether selecting a withdrawn-status control is refused, priced, or admitted with a
   named absence. Record the reason.
2. Make the selection rule and ticket 123's counterfactual use the same answer, so the removal
   and the withdrawal cannot disagree about who acted.
3. A regression test at the composer seam for each case above.

## Done

A withdrawn-status control is handled by one recorded rule at selection time, and ticket 123's
counterfactual follows it, including the legacy-header case.

## Build, 2026-09-23

Built on platform branch `ticket-126-a-withdrawn-control-is-not-selectable` and hub branch
`ticket-126-a-withdrawn-control-is-not-selectable`. The platform branch sits on platform
origin/main `5dadf00`, after tickets 123, 122 and 121. The hub branch sits on hub origin/main
`e13215b`.

### What was built

- `_defines` in platform `compose/composition.py` is the one selection rule. A catalogue
  defines an id when the id is present and not under `status: withdrawn`.
- `_unknown_control_refusals` uses it for `overlay.controls` and for every control claim. An id
  the catalogue keeps under `status: withdrawn` refuses `unknown-control-id`. Its detail says
  the id is there under that status. The overlay selects only ids `_defines` admits.
- The header records `withdrawn-selectable: false`. `compose/comparison_history.py` carries it
  as an optional boolean, so a header without it still validates and projects without it.
- `split_withdrawn` asks the last overlay with `_defines`, and uses the header's proof. The
  rewrite is below under decision 4.
- Platform `compose/README.md` and `party/schema.json` (`overlay.controls`) say so.
- Hub: `tests/test_loophole_adr_0026.py` gains 3 legs and rewrites the 2 review-round legs of
  ticket 123. Their first header is now one an older composer signed, because the new rule
  refuses the selection they started from. CONTEXT.md **Control id** and a dated ADR-0026 note
  record the rule.

### Decisions (all delegated, ADR-0025)

1. **Selecting a withdrawn-status control is refused, as `unknown-control-id`.** Reason:
   ADR-0026's Consequences already say an adopter still naming a withdrawn control meets
   `unknown-control-id`, and point 1 classifies that as an instrument fault. Nothing pinned
   defines a withdrawn control, so nothing can price holding it. Pricing it would price a claim
   on a control the regulator no longer asks for. Admitting it with a named absence would still
   let the adopter be shown as holding it. No refusal kind is added, so ADR-0026 point 6 and
   `verify-adr-supersession.sh` keep their list of eleven.
2. **The rule covers the overlay and control claims, not the regulator's baseline.** Reason: the
   overlay and a claim are what an adopter or an implementer names. The baseline is the
   regulator's signed selection, which compose already reads without checking ids. Measured:
   nist v1.1.0's LOW, MODERATE and HIGH name 149, 287 and 370 ids, none under `status:
   withdrawn` and none absent. A baseline naming a withdrawn id would be the regulator's own
   fact to fix, like the weights feed.
3. **The header records `withdrawn-selectable: false`.** Reason: after this rule, every id a
   header selected was defined at its pin. The next run needs to know that to book a
   now-withdrawn id as the regulator's. A header without the field came from an older composer,
   and absent is not the same fact as false. `overlay-controls` cannot stand in for it: platform
   main already writes that field without this rule. Measured: platform tags v3.1.0 and v3.2.0
   do not contain ticket 123's commit `6cb95e9`, so no released composer writes it yet. The
   owner could cut one before this merges, so the explicit field is the safer proof.
4. **`split_withdrawn` follows the rule, and a header proves only what it can.** For a control
   that left the selected set where the regulator's pin moved:
   - The last baseline name still includes it at the new pin: the adopter's. It changed its
     baseline.
   - The last overlay named it and the catalogue still defines it: the adopter's.
   - The last overlay named it and the catalogue no longer defines it: the regulator's
     (`catalogue`) when the id is absent or the header carries `withdrawn-selectable: false`.
     Otherwise the adopter's, because an older overlay may have selected it already withdrawn.
   - The header has no `overlay-controls`: the regulator's only when the id is absent. An id
     now under `status: withdrawn`, or still defined, stays the adopter's for that one run.
   - Otherwise it came from the last baseline: the regulator's, `baseline` if still defined,
     else `catalogue`.
   Reason: under any composer an id had to be present to be selected, so an absent id is always
   the regulator's. An id now under `status: withdrawn` is the regulator's only if the header
   proves it was defined when selected. This fixes the review's legacy-header case: a legacy
   header, a real bump and the adopter's drop of `ac-2.10` in one run. `ac-2.10` now prints
   `removed-control`. The cost is ticket 123 decision 4's cost, widened to the withdrawn
   status. A real NIST withdrawal of a baseline control, landing in the same run as an
   adopter's first compose under this build, prints as that adopter's `removed-control` for
   that one run. The other default would book an adopter's own drop as the regulator's, which
   is the defect the review blocked on.
5. **A last baseline that still names the control makes it the adopter's even when the
   catalogue dropped it.** Reason: had the adopter kept its baseline name, the control would
   still be selected, because compose reads the baseline as signed (decision 2). Before, the
   catalogue test ran first and booked it as the regulator's.

### Measured

- Adopters at origin/main (driftwood `c96c412`, tuppence `7009ea9`, ludlow `32d5696`), read with
  `git show` and a scratch script: each pins nist 1.1.0 and platform 2.0.1, selects MODERATE,
  and has `overlay.controls: []`. Each committed header selects 287 ids, none under `status:
  withdrawn` at nist v1.1.0, and carries no `overlay-controls`. No adopter owns a
  component-definition. Platform's component-definition at v2.0.1, v3.2.0 and origin/main
  claims 2 ids, none withdrawn and none absent. So no adopter selects or claims a
  withdrawn-status id today, and the rule refuses none of them.
- nist v1.0.0, v1.1.0 and origin/main each carry 1196 ids, 182 under `status: withdrawn`,
  `ac-2.10` among them.
- Recomposed each adopter in a detached origin/main worktree, once with platform origin/main's
  composer and once with this branch's, against the shared estate clone. The outputs differ by
  exactly one header line per adopter, `withdrawn-selectable: false`. `evidence.json` is byte
  identical. Each composes with no refusal and no `removed-control` or `withdrawn-control`
  delta. The committed `composed/` trees already differ from either recompose in 25, 23 and 23
  files, the same count for both composers. That drift predates this ticket.
- Red first. The 3 new hub legs and the rewritten ones failed on platform origin/main: 6 failed,
  5 on the missing `withdrawn-selectable` field. With that field's assertions stubbed out, 3
  still failed. tuppence naming `ac-2.10` composed instead of refusing. In the new-rule leg,
  tuppence keeping an id NIST had just marked withdrawn composed instead of refusing. The
  legacy-header leg printed `withdrawn-control` for `ac-2.10`, the review's case. Two selfcheck probes on copies of the branch failed where they should.
  Restoring the old selection rule failed the first new case (`doc_sel` composed). Restoring
  the old legacy branch failed the legacy-header bump case (`aa-1.1` and `aa-3`).
- Green, with a scratch estate whose `platform` is this branch:
  `.venv/bin/python -m pytest tests/test_loophole_adr_0026.py tests/test_priced_holes.py -n0 -q`
  gives 54 passed. `tests/test_loophole_rounds_two_and_three.py tests/test_misuse.py` gives 53
  passed, 6 skipped. mypy over `twin tests conftest.py` finds no issues in 199 files.
  `verify/adr-supersession/verify-adr-supersession.sh` passes.
- Platform, with `PAVC_ESTATE_CLONE` set to the shared estate clone: `composition.py
  --selfcheck` exits 0 with 102 OK lines; origin/main gives 97. Two old cases were replaced
  and seven added. `python3 -m unittest test_comparison_history` runs 13 tests, OK; the new one
  errors on origin/main. `party/party_artefact.py --selfcheck` passes. `verify-composition.sh`
  exits 3 on the branch and on origin/main, with the same step 2 SKIP (platform@2.0.1 lacks the
  rendered versions).
- `verify/priced-holes/priced_holes.py check` exits 1 with the same 3 tuppence FAILs that
  predate ticket 119 (acknowledged in hub PR 103).

### What remains

- **Owner:** a signed platform tools release that carries this build, and each adopter's pin
  moving to it. Then re-compose and push driftwood, tuppence and ludlow. Each header then gains
  `overlay-controls: []` and `withdrawn-selectable: false`. These are release and enactment
  steps.
- **Owner, ordering:** move each adopter's tools pin and re-compose once before moving a nist
  pin whose tag withdraws a control. Then the header proves what was defined, and the
  withdrawal prints as NIST's. Done the other way round, it prints as the adopter's
  `removed-control` for one run (decision 4).
- **The revisit trigger** in ADR-0026, the first real withdrawal bump, has not happened.
