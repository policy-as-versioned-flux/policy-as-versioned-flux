# 52 — The end-to-end harness inside the gate

Type: task (AFK)
Status: resolved
Blocked by: 03

## Question

Build one verify script under `talk/verify-all.sh` that drives the seven NORTH-STAR §4 steps in order on an ephemeral KinD cluster inside the scheduled truth run. Each step is one graded sub-result: pass, fail or could-not-look. The harness owns no state and reads the same signed artefacts Flux reads. It grows one step at a time in the build order (21, 25, 26/28/32, 40/41/42, 29/49/50, 43/47) and reports could-not-look for steps not yet built. It never runs as a presenter-run number.

## Notes

Owner's seam choice on 2026-08-28 for `/to-spec`: "A new end-to-end harness", chosen over the one-seam option with the assistant's concern on record that a harness outside CI is a second clock. Reconciled by placing the harness inside the gate, so the TRUTH line stays the only citable number (D1, D4, ADR-0023). Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The harness is seven scripts under the gate, one graded sub-result per NORTH-STAR section 4 step, run inside the scheduled truth run and never as a presenter-run number. Step seven fails any step that exits 0 while its own transcript names something it could not look at.

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
