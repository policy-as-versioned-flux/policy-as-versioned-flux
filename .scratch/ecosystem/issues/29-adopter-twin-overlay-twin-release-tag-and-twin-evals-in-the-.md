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
