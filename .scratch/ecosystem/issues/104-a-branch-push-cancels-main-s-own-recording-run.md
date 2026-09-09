# 104 — A branch push cancels main's own recording run

Type: task (AFK)
Status: open
Blocked by: none

## Question

`.github/workflows/truth.yml` groups its concurrency as `truth-${{ github.event_name }}` with
`cancel-in-progress: false`. Every `push` on EVERY branch therefore shares one lane, `truth-push`,
and GitHub keeps only the run that is executing plus the newest queued one and cancels the rest.
So a push on a builder's branch — which since ticket 100 records nothing at all and is pure
measurement — can cancel a push run on `main`, which CAN record. Measured 2026-09-06 over the
newest 22 `main` push runs of `truth.yml`: **8 were cancelled** (run numbers 136, 130, 127, 125,
119, 112, 48, 42), and none of those eight run numbers appears in `talk/truth.log`. Eight citable
observations were queued, displaced and lost, and nothing anywhere says so.

Two decisions collided to make it. Ticket 56 (2026-09-04) split the single `truth` group into one
per event so that a scheduled run could no longer be cancelled by a push — which was right, and
which is why the SCHEDULED lane is safe. Ticket 100 (2026-09-05) then made branch runs record
nothing, which was also right, and which turned every branch push into a run that occupies main's
lane while having nothing to lose by being cancelled. Neither ticket could see the other's half.

Build: (a) key the concurrency group on the event AND the ref — `truth-${{ github.event_name }}-${{ github.ref }}`
— or exempt non-default-branch pushes from the default branch's group, so a branch push can only
ever displace another run of its own branch; decide which and record why. (b) `verify/schedules/`
grades a clock by its newest scheduled run and excuses `truth.yml` for a red gate, but it has no
reading at all for a `cancelled` run on the default branch: teach it that a cancelled run which
could have recorded is a LOST RECORDING, name the count on every run, and decide whether it is a
red or a reported number. (c) Decide whether the eight lost observations are re-runnable (the
trees are still on `main`, so a `workflow_dispatch` at each sha would measure the same tree at a
later date) or are simply gone and recorded as gone; a hand-written line into `talk/truth.log` is
not an option (ticket 100, `verify/can-record/`).

Done = a branch push demonstrably cannot cancel a `main` push run, proved over the real workflow
rather than by reading the YAML; and the citable record says how many recordings have been lost
this way.

## Notes

Charted 2026-09-06 by eco-system ticket 59, whose own branch lost both of its push-triggered
truth runs to this (34027684699 and 34027824771, both `cancelled`), and which then had to
dispatch `truth.yml` by hand to get any gate observation of its own work at all. That workaround
is worth keeping in the record: a `workflow_dispatch` run lands in `truth-workflow_dispatch`,
which no push shares, so it is the only reliable way for a builder to get a branch gate run today.

Record: eco-system ticket 59's Answer; `verify/schedules/schedules.py`'s `PERIOD_HOURS` and its
excused-conclusion table; ticket 56's per-event group; ticket 100's recording guard.

**2026-09-09, a fresh instance, and the first one measured on a BRANCH rather than on `main`.**
Run 34386266006's predecessor, push run **34384890318** on `ticket-48-the-demos-remaining-beats`
at head `1aa4054`, went `completed/cancelled` while queued. It was displaced by a push run on
`ticket-31-sensor-admission`, which entered the same `truth-push` lane a few minutes earlier. So
the fault is symmetric and the ticket's title understates it: a branch push does not only cancel
`main`'s recording run, it cancels other branches' measurement runs too, and two builders working
at once will take turns losing their gate observation of their own work.

That half costs no citable line, because a branch run records nothing (ticket 100). It costs
something else, and the cost is what makes the ordering wrong rather than merely untidy: the
reviewer of that branch has no gate run of the tree under review, so the branch either merges
unmeasured or somebody dispatches by hand. Here it was dispatched by hand, run 34386266006 in
`truth-workflow_dispatch`, which confirms the note above is still the only reliable route.

The `main` half did NOT fire today. `truth.yml` ran six times on `main` on 2026-09-09, five on
push (`cdc5fb9`, `302bf73`, `c1aee32`, `0c1cb54`, `041ecc8`) and one on schedule (`9517d98`).
Every one completed, and `talk/truth.log` carries a line for every one of the six shas: runs 186,
192, 194, 197, 200 and 207. Nothing was displaced on `main` today. Two `main` push runs were cancelled on 2026-09-08 (`e307152`,
`a12c2f7`), so the eight the Question counts are now ten. That is a count and not a new decision;
build item (b) still owns turning it into something the gate says on every run.

One thing this instance settles for item (a): keying the group on `github.ref` fixes BOTH halves
at once, because it puts every branch in its own lane, and no other option in the Question does.
