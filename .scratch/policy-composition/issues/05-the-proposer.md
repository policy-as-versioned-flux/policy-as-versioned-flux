# 05 — The proposer

Type: grilling
Status: open
Blocked by: none

Graduated from the map's Not yet specified: "The proposer." Ticket
[`01`](01-does-composition-hold-up.md)'s prototype prints a proposed tier when a feed re-prices a
cage. Nothing raises the PR from that proposal, and the map's standing preference is clear that a
feed may re-price but never apply: every resulting change must land as a reviewed PR.

## Question

What raises the PR for a proposed tier change, and where does it run? `docs/adr/0007` says the agent
layer prompts editorial review and never edits enforcement directly, so what shape does the proposer
take within that constraint?
