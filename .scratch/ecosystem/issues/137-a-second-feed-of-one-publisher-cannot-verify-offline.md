# 137 — A second feed of one publisher cannot verify offline

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator from ticket 136's named residual.

`compose()` keeps one parent tree per party. When a publisher's clone is absent, as in the
offline re-verify that tickets 45 and 110 promise, a second feed of the same publisher reads the
first feed's vendored tree and refuses: "observation does not belong to this feed pin and parent
SHA". Ticket 136's builder measured it on platform 38089a6 with a fixture of cve@v1 and eol@v2.

tuppence pins two feeds of the feeds publisher, threat-register@v1 and cve@v2, so its offline
verify is exposed. The refusal names itself and never prices from the wrong bytes, but it breaks
the portability promise: an adopter can no longer re-verify its own signed tree with the
publisher absent.

What this ticket owes:

1. `compose()` resolves a parent tree per feed edge, not per party, so each feed reads its own
   vendored tree when the publisher is absent.
2. A red-first test at the `compose()` seam: two feeds of one publisher at different majors
   verify byte-identically with the publisher present and absent.
3. Run `verify` for the real tuppence with the feeds clone absent, before and after.

## Done

An adopter that pins two feeds of one publisher re-verifies its signed tree byte-identically with
that publisher's clone absent.
