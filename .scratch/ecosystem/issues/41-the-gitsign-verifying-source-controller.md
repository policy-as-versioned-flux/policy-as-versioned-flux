# 41 — The gitsign-verifying source controller

Type: task (AFK)
Status: open
Blocked by: 16

## Question

Build the identity-pinned gitsign-verifying controller at the Flux source boundary, time-boxed until fluxcd/source-controller#1068, with a verify script that goes red when the trigger fires, after first testing whether mode Tag verifies when spec.ref.commit differs from the tag target.

## Notes

Graduated 2026-08-28 from ticket 16's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
