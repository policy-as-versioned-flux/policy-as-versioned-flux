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
