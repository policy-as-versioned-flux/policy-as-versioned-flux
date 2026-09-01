# 74 — Step 3 happens once, for real

Type: task (AFK watch, HITL merge)
Status: open
Blocked by: none

## Question

The proposer is proven: propose-tier runs on every adopter's clock, re-composes at today's date
through the pinned platform, and correctly proposes nothing while no residual crosses a band
(first scheduled firing 2026-09-01 12:01Z returned `[]`). What has never happened is the event
itself: a residual really crossing a band, the proposal PR opening with its priced evidence, and
a human merging it once — NORTH-STAR §4 step 3, review finding M9. Watch for the crossing and
see the first proposal PR through to a human merge. Three concrete movers can cause it: a feed
bump that moves a price (ticket 61's machinery now raises those), the EOL ramp's date-driven
price (moves daily by `--as-of`), and a size or appetite change on party.yaml. Do not
manufacture a crossing: the first step 3 must be a real one. Done = one proposal PR opened by
the clock on a real crossing, merged by a human, and the tier move visible in the composed
artefact on the next citable run.

## Notes

Graduated from ticket 60, whose grading half completed on TRUTH run 20 (2026-09-01T21:07Z).
Tuppence and ludlow's proposers also need ticket 62 (their feeds/insurer checkouts still name
the deleted `ecosystem/thin-slice` branch and fail before composing); driftwood's proposer is
fully operational today.
