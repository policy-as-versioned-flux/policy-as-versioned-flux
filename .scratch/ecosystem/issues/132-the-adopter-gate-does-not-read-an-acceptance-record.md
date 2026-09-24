# 132 — The adopter gate does not read an acceptance record

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Ticket 129 defined the major acceptance record and taught
the hub's `verify/unreviewed-major` check to read it. Each adopter's own gate does not.

On the v3.3.0 rollout PRs (driftwood 40, tuppence 36 and 37, ludlow 33 and 34), the shift-left job
failed with "composed bump is major" for the added policy 5.0.0, although each PR carried
`accepted-majors/platform-5.0.0.yaml`. The integrator merged over that red on the owner's
acceptance of 2026-09-23. A required check that must be merged over on every accepted major
teaches nothing.

What this ticket owes:

1. Each adopter's `adopter-gate.py` (driftwood, tuppence, ludlow) reads `accepted-majors/` at the
   head it grades, with the same matching rule as the hub check (party, publisher and exact
   version), and admits a composed major only when every major it adds is accepted.
2. An unaccepted major still refuses, and a record for another party, publisher or version does
   not count. Tests for each.
3. The hub check and the adopter gates read one format; say where it is defined so the two
   cannot drift.

## Done

A pull request that adds an accepted major passes the adopter gate, and one that adds an
unaccepted major still refuses.
