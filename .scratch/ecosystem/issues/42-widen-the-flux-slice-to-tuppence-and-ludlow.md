# 42 — Widen the Flux slice to tuppence and ludlow

Type: task (AFK)
Status: resolved
Blocked by: 40, 41

## Question

Install the engine and CRDs on tuppence and ludlow, re-land the mo-09 git-server removal in all three up.sh, and bring their samples into verify-all once driftwood is green.

## Notes

Graduated 2026-08-28 from ticket 16's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. Tuppence and ludlow carry driftwood five-fact sampler, falsifiers and scheduled lane, each with its own sources and floor, and the same refusal of a hand-typed sample. Both verify-reconcile.sh scripts read could-not-look until their lane runs on the remote.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.
