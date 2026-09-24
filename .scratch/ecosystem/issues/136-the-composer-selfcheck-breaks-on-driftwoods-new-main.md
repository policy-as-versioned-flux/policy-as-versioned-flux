# 136 — The composer selfcheck breaks on driftwood's new main

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Truth run 314 graded
`.estate-clone/platform/compose/verify-composition.sh` FAIL on `composition.py --selfcheck`,
after driftwood moved to platform tools v3.3.0 (driftwood PR 40) and its composed set to v2.0.0
(driftwood PR 39). Run 310 graded it SKIP.

Ticket 134's builder measured the selfcheck against driftwood's main `3f8943d` and saw it stop
with "two feed edges of feeds at v2 both vendor to composed/feeds/feeds/v2". The selfcheck uses
the real driftwood as its fixture, so a real change in driftwood broke an assumption in it.

What this ticket owes:

1. Find which assumption broke and whether driftwood's state is valid. If driftwood now carries
   two feed edges at the same major that the composer cannot vendor apart, that is a composer
   defect or a driftwood defect, not a selfcheck one; say which.
2. Fix it where it is wrong, red first, on platform main, so the next tools release carries it.

## Done

`composition.py --selfcheck` passes against the real estate at each adopter's main, and the
record says what broke.
