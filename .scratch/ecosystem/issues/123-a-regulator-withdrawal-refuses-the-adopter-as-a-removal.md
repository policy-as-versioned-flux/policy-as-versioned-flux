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
