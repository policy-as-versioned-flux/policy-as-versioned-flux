# 36 — the insurer quote slice

Type: task (AFK)
Status: resolved
Blocked by: 10, 21, 25

## Question

Insurer party.yaml with roles [publisher] and inherits[] (platform, driftwood exposure); quote-driftwood feed with priced_against, validity, conditions; scheduled pricer opening a PR under perspective insurer; verify script (retained + transferred + excluded == simulated total, premium from pinned quote, expiry priced, breached condition priced per consequence) wired into verify-all.sh.

## Notes

Graduated 2026-08-28 from ticket 14's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The insurer pins the platform and the adopter signed exposure, prices on its clock under its own perspective, and publishes one quote feed per adopter. The premium reaches the adopter prices[] as the contract-cost line ticket 25 reserved. A human merges the quote.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.
