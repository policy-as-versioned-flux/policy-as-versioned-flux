# 41 — The gitsign-verifying source controller

Type: task (AFK)
Status: resolved
Blocked by: 16

## Question

Build the identity-pinned gitsign-verifying controller at the Flux source boundary, time-boxed until fluxcd/source-controller#1068, with a verify script that goes red when the trigger fires, after first testing whether mode Tag verifies when spec.ref.commit differs from the tag target.

## Notes

Graduated 2026-08-28 from ticket 16's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The gitsign-verifying controller sits at the Flux source boundary, identity-pinned, time-boxed until Flux #1068, and re-signs nothing. verify-source-verification.sh proves it rejects a tampered bundle, a wrong identity and a wrong issuer against real committed material, and exits 3 where no cluster carries it.

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
