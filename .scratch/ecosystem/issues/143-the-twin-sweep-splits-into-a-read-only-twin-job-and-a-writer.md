# 143 — The twin sweep splits into a read-only twin job and a writer

Type: task
Status: open
Blocked by: 145

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 7, 8, 9 and 11 (delegated), and
ADR-0031. In each adopter (driftwood, tuppence, ludlow):

1. **The pin.** The sweep checks out the hub at the commit `twin/PIN.yaml` names, not at `main`.
   The adopter moves the pin by a reviewed PR. When the signed `twin/v0.1.0` tag exists, the tag
   replaces the commit.
2. **The split.** The twin job holds `contents: read` and runs the twin code. It hands its
   observation line and its proposal to the writer job as an artifact. The writer job has no hub
   checkout, no twin code and inline shell only; it validates every path in the artifact against
   the observation lane and the proposal paths before it writes.
3. **The network dial.** Every download is pinned by hash, including `pip install pyyaml`.
4. **The rung gate.** The writer's steps follow the rung the adopter's selection policy selected
   (ticket 145): baseline and restricted append an observation and propose; quarantine appends an
   observation only; isolated runs the twin job and writes nothing.
5. **A refused directory is not a move.** tuppence's and ludlow's `.github/scripts/twin-sweep.py`
   record a loader `ModelError` (exit 1) as `moved: true`, review required. Record it as a render
   that could not be made.

## Notes

Blocked by 145 for item 4 only; items 1, 2, 3 and 5 can land first. Adopter tags wait for the
owner's authorisation. Ticket 142's check grades the result.
