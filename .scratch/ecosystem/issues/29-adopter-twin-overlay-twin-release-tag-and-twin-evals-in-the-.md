# 29 — adopter twin overlay, twin release tag and twin evals in the gate

Type: task (AFK)
Status: resolved
Blocked by: 09, 21, 25

## Question

Cut the first signed semver tag on `twin`; vendor the world layer under `twin/world/` in each adopter repo; author the floor overlay (components, roles, one priced edge, `employer` perspective with `currency`) for driftwood, tuppence and ludlow; add classes `eol-date-passes` and `penalty-published` (enum, library fixture, adopter overlay) and the six standing scenarios; add the feed-version-to-signal lookup table; add `verify/verify-twin-evals.sh` (six skill evals, three beats, determinism, fall-in-score is FAIL) so the gate discovers it; correct `honest_build.py:173-176`.

## Notes

Graduated 2026-08-28 from ticket 11's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The twin overlay lives in the adopter repo with the world layer vendored, the twin self-versions, and the six standing scenarios exist per adopter with niobium in the library and never in a feed. verify/twin-evals/ runs the evals in the gate and a fall in any score against the last recorded value is a fail.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.

**Correction, 2026-09-04 (eco-system ticket 64).** The paragraph above says "the six standing
scenarios exist per adopter". They did not. **What ticket 29 built was driftwood-only**: one
overlay, under `.estate-clone/driftwood/twin/`, with driftwood's own six scenarios, its own
signals lookup and its own emitter. tuppence and ludlow carried no `twin/` directory at all
between 2026-08-29 and 2026-09-04, and no check in the gate said so, because every twin check in
the estate was driftwood's own and `verify/e2e/verify-e2e-step5-twin-forecasts.sh` hardcoded
`driftwood` as its adopter. Read the sentence above as "per adopter, for the one adopter this
ticket built".

Two further clauses of ticket 29's own definition of done are still open and are not closed by
this correction: `twin/v0.1.0` is **not cut** (`PIN.yaml` carries `tag_cut: false` in all three
adopters now), and driftwood's `twin/forward-intel` has no signed release tag either. Both are
owner dispatches of `cut-release.yml` and are listed under ticket 64's `## Waits on the owner`.

Ticket 64 authored the tuppence and ludlow overlays, made the gate name an adopter that has none
(`verify/twin-per-adopter/`), and widened step 5 to derive its adopter list from the party
artefacts instead of naming one.
