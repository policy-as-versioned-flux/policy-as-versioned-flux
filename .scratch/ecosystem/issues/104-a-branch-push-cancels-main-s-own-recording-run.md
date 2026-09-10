# 104 — A branch push cancels main's own recording run

Type: task (AFK)
Status: resolved
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

## Implementation, 2026-09-10 — review pending

Decisions delegated under ADR-0025:

- The group is keyed by event **and ref**, preserving scheduled-vs-push isolation while
  separating every builder from main and other builders. Same-ref pending runs can still
  displace each other; this is not a promise that GitHub retains an unlimited queue.
- Lost recordings are a reported historical count, not a permanently red gate. The collector
  pages through retained `truth.yml` run history, records the default branch and minimal run
  facts, and the credential-free gate subtracts cancelled run numbers that actually appear in
  `talk/truth.log`. A missing history is `count=unknown` and SKIP, never zero. Cancellation's
  cause is unknown: a manual cancellation is a lost opportunity too, but is not blamed on a
  concurrency collision. GitHub-deleted history is outside the declared census.
- Past observations are gone. A dispatch today observes today's estate, even at yesterday's
  hub commit; it cannot recreate a lost observation. No truth line is invented or replayed.

Measured 2026-09-10 from 239 retained runs across three GitHub API pages: **19** cancelled
main recording opportunities absent from the committed log: 34, 36, 37, 38, 42, 48, 63, 112,
119, 125, 127, 130, 136, 149, 155, 156, 159, 168 and 175. This is a dated local API census,
not a citable TRUTH run and not proof that all cancellations had one cause.

Validation: red-first tests at the workflow concurrency-key and collected-facts seams;
39 focused tests pass, including pagination, malformed-history refusal, recorded-run exclusion,
duplicate suppression and collector-to-verdict reading without credentials. The schedule
selfcheck passes. Live overlapping-run proof and a scheduled capture of the new count remain
outstanding; the ticket stays open until review and those observations complete.

Source for concurrency semantics:
https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

### Independent review

Standards: no hard violations; the one maintainability finding (a second TRUTH-field regex)
was fixed by using `truth_manifest.parse_truth`. Spec: no code defects; live overlapping-run
proof and a scheduled capture remain required. The 39 focused tests pass after the correction.
The repository-wide type check passes across 190 source files. The configured commit hook's
remote secret-scan quota rejected the checkpoint commit; a separate local TruffleHog scan found
zero secrets, but substitution permission remains pending and no production hook was bypassed.


## Answer — completed against the original Done, 2026-09-10

The reviewed implementation merged through hub PR77 as e214bed. Real push runs
[34505271984](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/34505271984)
on the implementation branch and
[34505741926](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/34505741926)
on main executed their gate jobs concurrently: the former began at 16:58:29Z and was still
running when the latter began at 17:03:21Z. Both completed; neither was cancelled. This is actual
workflow execution in distinct ref groups, not inference from the YAML alone.

Main's recording commit 5ebeba4 appended run 242 at 17:28Z and is retained by main's later merge
0647a55. Its committed `talk/captures/verify_schedules_verify-schedules.out` begins with
`LOST RECORDING count=19` and names the missing run numbers, the 242-run retained-history
boundary, unknown cancellation cause and no-replay disposition. The clock wrote this evidence;
no observation was written by hand. Its overall 80 pass/8 fail/29 skip result remains red.

Earlier implementation/review notes asked for a scheduled capture. The original Done requires
that the citable record contain the count, not that its event be schedule. Ticket 100 admits a
main push recording, and run 242 is in `talk/truth.log`; it therefore meets that original
criterion. The extra event restriction is not retained. Same-ref pending cancellations remain
an explicitly stated limit, not a promise of an unlimited queue.

## Existing clock failures, 2026-09-10

**2026-09-10, standing schedule failures.**
`verify/schedules/verify-schedules.sh` remains FAIL in recorded run 242 for feeds/fetch.yml,
insurer/fetch.yml and the missing ludlow/tuppence `twin-sweep.yml` workflows. The lost-recording census is a
reported historical count and does not excuse any of those failures. Tickets 85/77 and the
missing-workflow findings retain their own work; ticket 104's queue isolation and census are complete.

### Superseded map entry retained as history

- [104 — A branch push cancels main's own recording run](issues/104-a-branch-push-cancels-main-s-own-recording-run.md) — CHARTED, not built. `truth.yml`'s concurrency group is `truth-${{ github.event_name }}`, so every push on every branch shares one lane and GitHub cancels all but the running and the newest queued run: 8 of the newest 22 `main` push runs were cancelled (136, 130, 127, 125, 119, 112, 48, 42) and none of those run numbers is in `talk/truth.log` — eight lost citable observations. Ticket 56's per-event group protected the scheduled lane; ticket 100 then made branch runs pure measurement that still occupies main's lane. Key the group on event AND ref, and teach `verify/schedules/` to read a cancelled default-branch run as a lost recording, which it cannot today.

Map line: `- [104 — A branch push cancels main's own recording run](issues/104-a-branch-push-cancels-main-s-own-recording-run.md) — resolved, event-and-ref queues are proven by overlapping real main/branch push gates, and recorded run 242 captures LOST RECORDING count=19 across 242 retained runs. Historical cancellations have unknown cause and are reported without replay; same-ref pending runs can still displace each other.`
