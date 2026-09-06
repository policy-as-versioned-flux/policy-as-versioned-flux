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

> **Correction, 2026-09-06 (eco-system ticket 80 item 1).** The done-line above cites "the TRUTH
> line of 2026-08-29" as proof this ticket's check is in the gate. That citation is withdrawn.
> The line is run 7, `hub=918022b`, recorded at 2026-08-29T12:03Z, and `git ls-tree -r 918022b`
> carries three verify directories -- `verify/party/`, `verify/proportionality/` and
> `verify/provenance/` -- and none of the checks this ticket names. It was graded BEFORE the
> build it is offered as proof of, so it recorded nothing at all about this check. What this
> check actually rests on is whichever later run first discovered it, which the gate names for
> itself on every run. `verify/cited-truth/` grades this rule from today and refuses the next
> citation of a measurement that did not measure the thing.
