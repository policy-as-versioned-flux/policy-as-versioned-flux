# 127 — The pound seam reads a switching price as a regime entry

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator from a read-only map of the gate's reds. No ticket owns
this red. Ticket 79 built the check, and ticket 121 measured the same four FAILs and said "not
this ticket's".

`verify/pound-seam/verify-pound-seam.sh` FAILs with "4 £-seam check(s) observed false" on run
296. Measured on main:

1. `verify/pound-seam/pound_seam.py:210` treats every price with `source: ico` as a regime entry,
   and lines 227-230 demand `holes[]` from it. Each adopter's `composed/evidence.json` carries two
   ico prices: `kind: feed`, which has `holes[]`, and `kind: switching`, which has none. Three of
   the four FAILs are the switching entries (driftwood `prices[4]`, ludlow and tuppence
   `prices[3]`).
2. The fourth is driftwood `prices[5]`, feeds/threat-register `kind: switching`, with
   `amount: None` and a named `could_not_look`: its forward-intel feed supplies no lef.

Ticket 128 adds `kind: supersede` prices from ico too, so the misreading will grow.

What this ticket owes:

1. Check 4 selects regime entries by kind, not by source alone.
2. A price that carries a non-empty `could_not_look` grades as a named could-not-look, declared in
   `talk/verify-manifest.txt`, not as a FAIL. It must not grade PASS either.
3. Selfcheck cases for both, each red on today's code.

## Done

The check grades each ico price by its kind, a named could-not-look is a declared SKIP, and the
selfcheck holds both. Whether driftwood's forward-intel feed can ever supply a lef is a separate
question near grilling ticket 30 and is not this ticket's.
