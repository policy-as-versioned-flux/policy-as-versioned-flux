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
