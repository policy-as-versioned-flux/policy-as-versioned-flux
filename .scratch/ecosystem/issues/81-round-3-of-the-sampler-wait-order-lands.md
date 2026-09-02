# 81 — Round 3 of the sampler wait-order lands on tuppence and ludlow

Type: task (HITL)
Status: open
Blocked by: none

## Question

Tuppence's and ludlow's five-fact samples record 16 of 16 rendered objects absent from the cluster on every run they have ever appended, because the sampler waits for kyverno below the composed apply. Ticket 60's post-resolution note records round 3 as "committed and patched" on branch `ticket-60-wait-order` in each unit's `.estate-clone/` checkout. That branch exists on no adopter remote. `enact_guard` correctly refuses the push. Nothing owns it.

The owner pushes the three commits (patches in `.scratch/ecosystem/patches/ticket-60/`), opens and merges the three PRs, and the next scheduled sample, not a dispatch, is the proof. Then ticket 62's twelve refs land so the same two adopters can compose at all.

Done = tuppence's and ludlow's newest scheduled `drift/samples.jsonl` record facts 4 and 5 true for their composed source, and the three `verify-reconcile.sh` checks and step 4 grade from it on a citable run.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R8. Finding: demo-steps/DS-F6. With ticket 73's cert-skew fix, three of run 21's seven reds have a route to green. Fact 2 on driftwood and ludlow is ticket 73, not this one.
