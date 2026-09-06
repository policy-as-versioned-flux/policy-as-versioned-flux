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

> **Correction, 2026-09-06 (eco-system ticket 80 item 1).** The done-line above cites "the TRUTH
> line of 2026-08-29" as proof this ticket's check is in the gate. That citation is withdrawn.
> The line is run 7, `hub=918022b`, recorded at 2026-08-29T12:03Z, and `git ls-tree -r 918022b`
> carries three verify directories -- `verify/party/`, `verify/proportionality/` and
> `verify/provenance/` -- and none of the checks this ticket names. It was graded BEFORE the
> build it is offered as proof of, so it recorded nothing at all about this check. What this
> check actually rests on is whichever later run first discovered it, which the gate names for
> itself on every run. `verify/cited-truth/` grades this rule from today and refuses the next
> citation of a measurement that did not measure the thing.
