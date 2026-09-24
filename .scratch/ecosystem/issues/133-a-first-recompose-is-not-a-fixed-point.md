# 133 — A first recompose is not a fixed point

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator from the v3.3.0 rollout on tuppence (PR 36) and its review.

The composer reads the working tree's `composed/` as its "before". On tuppence the first
recompose under v3.3.0 emitted a `new-ungoverned-namespace` delta for `openbao` of
2,315,591.33 GBP. A second pass recorded `openbao` as `recorded` and carried no delta, and passes
two to four were byte-identical. The first builder committed the second pass and so hid the
delta. The fix restored `origin/main`'s `composed/`, recomposed, and kept the delta.

The reviewer found why: when the recorded `comparison-inputs.after` identity does not match the
current identity and replay is false, `resolve()` silently takes the working-tree header and
prices as the "before". So a recompose over a half-written `composed/` reports against itself.

What this ticket owes:

1. The composer's "before" is the last committed artefact, not whatever the working tree holds,
   or a mismatch is refused by name rather than taken silently. Decide which, and record why.
2. A test at the `compose()` seam: two recomposes in a row from a committed artefact produce the
   same deltas as one.

## Done

A recompose is a fixed point from the committed artefact, and a stale working-tree "before" can
no longer hide a delta.
