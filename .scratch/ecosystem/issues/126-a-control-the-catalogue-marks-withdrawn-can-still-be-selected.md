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
