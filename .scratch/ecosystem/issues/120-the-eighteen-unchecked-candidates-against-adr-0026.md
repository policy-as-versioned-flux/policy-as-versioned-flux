# 120 — The eighteen unchecked loophole candidates against ADR-0026

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-22 by eco-system ticket 115, which ran the procedure in
[`bench/loophole/`](../../../bench/loophole/README.md) against a second document.

Three loophole rounds ran against
[ADR-0026](../../../docs/adr/0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md),
"a hole is priced, never refused". All three were clean: 0 parse failures, 0 under-production,
0 judge replies without a verdict. They produced **18 candidates**, 9 loophole and 9 overreach,
in `bench/loophole/rounds/adr-0026/round-{1,2,3}/candidates.json`. **None has been checked
against the code.** Ticket 115 was told not to check them, so the checking is this ticket.

At the survival rate measured on ADR-0022 (2 of 6, ADR-0030), 18 candidates hold about 6 real
defects. That rate rests on six checked candidates from one round and a different document, so
it is a budget, not a forecast.

What ticket 115 saw while recording them, read from the candidate text and not from the code:

- Several candidates point at the same places. The `since` date of an ungoverned namespace
  (round 1 loophole-2, round 2 loophole-3, round 3 loophole-2), a bespoke control priced by the
  adopter's own scenario (round 1 loophole-1 and loophole-3, round 2 loophole-2, round 3
  loophole-1), and a namespace created for a short task and swept into the ungoverned walk
  (round 1 overreach-5, round 2 overreach-5, round 3 overreach-6).
- The judge called 11 of 18 resolvable (3, 3 and 5 by round, from each `summary.json`). ADR-0030
  point 5 says that verdict is not a filter.

The rules this ticket works under, from ADR-0030:

1. **Test the place, never the sentence** (point 3).
2. **Count the survival rate on the candidates as stated** (point 3).
3. **Check every candidate whatever the judge said** (point 5).
4. ADR-0026 names a place where the record leads the code: the platform still refuses
   `removed-control`. A candidate that lands there is already known, and says so.
5. The reachable code for ADR-0026 is on the platform integration branch
   `ecosystem/build-2026-09-03` (`compose/composition.py`) and in
   `verify/priced-holes/`. Confirm which branch is live before checking.

## Done

Each of the 18 candidates has a verdict against the code, with the command that decided it. The
survival rate is stated on the candidates as stated. Each survivor is held by a deterministic
test and charted as its own ticket. The matching across the three rounds (same place, same
reason) is recorded, so ADR-0030 point 2's overlap has a second document behind it.
