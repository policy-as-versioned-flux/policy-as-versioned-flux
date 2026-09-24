# 139 — An ungoverned Namespace can be priced before it existed

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator from ticket 138's review.

tuppence's `composed/evidence.json` prices `openbao` with `since: 2026-09-24` (the first signed
tag that names it, v2.0.0) and `as_of: 2026-09-08`. The ramp is measured over a negative window
and clamps to 1.0. `verify-priced-holes.sh` prints:

```
PASS: tuppence ungoverned openbao: ... ramp 1.0000 from since 2026-09-24 as of 2026-09-08
```

The composer's `as_of` counts edge `since` dates and envelope `published_at` only, never the
adopter's own tags. So a Namespace that a tag cut after the newest signed input names first is
priced as of a day before it was ungoverned. Today the ramp clamps to 1.0 and nothing is
mispriced. It will matter the day the ramp is not flat at the start.

What this ticket owes:

1. Decide whether `as_of` must be at least every `since` the composition prices, and record why
   (ADR-0026 point 4 and ticket 122).
2. Make the composer and the grader agree on the rule, with a test that plants a `since` after
   `as_of`.

## Done

No price carries a `since` later than its `as_of`, or the record says why that is correct.
