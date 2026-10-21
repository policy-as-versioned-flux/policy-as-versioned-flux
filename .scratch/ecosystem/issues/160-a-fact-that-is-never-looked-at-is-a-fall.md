# 160 — A fact that is never looked at is a fall

Type: task (AFK)
Status: resolved
Blocked by: 161

## Question

Ticket 152 Q10 made a cage fact that is null on three samples in a row read FAIL. Ticket 161 builds that rule for facts 6 and 7. Apply the same rule to the five facts of each adopter's drift lane.

The reason: the four `talk/verify-manifest.txt` rows for each adopter's `verify-reconcile.sh` and for step 4 match "the lane sample cannot stand in" anywhere in the line (`talk/truth_manifest.py:133`). So any lane could-not-look reads as a declared wait, whatever its cause. From 2026-09-24 fact 7 was null on every sample because the cage put both probe pods on one rung. Before that, fact 6 was observed FALSE and each sample read FAIL. On 2026-09-25 the gate judged fact 7's null a declared wait. A fact that stays null must become a fall, while a null that clears on the next sample stays a could-not-look.

The five facts have no registration by section today. The guard over `drift/window.yaml` reads the file's first commit, and a later commit does not move it (ludlow `drift/window.yaml:164-167`). `grade` applies no registration date to facts 1 to 5. So this ticket must either add a registration for the five facts and say that it starts a new clock, or record that the rule changes grading without moving any registration.

## Notes

Graduated 2026-09-25 from ticket 152, Q10 and Q11. Blocked by 161 so that the rule's form is settled on the cage facts first. Definition of done: `grade` reports FAIL for any of the five facts that is null on three samples in a row, a selfcheck branch proves it, and the adopters' checks under `talk/verify-all.sh` carry it.

On tuppence, fact 2 changes between null and true (ticket 157). A single null between two trues must stay a could-not-look. A run of five nulls, 2026-09-17 to 09-21, would be a fall under this rule.

## Answer

**Local implementation, 2026-10-03.** Built the three-null fall rule for facts 1–5 separately for each source, using the three newest sample timestamps. Missing facts count as unmeasured; a true or observed false breaks the null streak; a single null between trues remains a wait. This changes grading without moving the original registration. A regression at the existing selfcheck seam failed before implementation, then passed on all three adopters. Rollout and a scheduled lane sample carrying the new grade remain pending.

**Software delivery reconciled, 2026-10-18; dependency remains open.** The published [Driftwood](https://github.com/policy-as-versioned-driftwood/driftwood/blob/5a1b9a1ae85f88dfe91a71aca8eeb308349097ff/drift/five-facts.py), [Tuppence](https://github.com/policy-as-versioned-tuppence/tuppence/blob/e7e2969cd50ab3e88fa11afe61d5bee5d1db30d4/drift/five-facts.py) and [Ludlow](https://github.com/policy-as-versioned-ludlow/ludlow/blob/e65acc95bd107e0ba2864b2ca2f23b51714dc4c1/drift/five-facts.py) graders implement the three-newest-timestamp rule separately for each source and each fact 1–5. Three null or absent values FAIL; a true or observed false interrupts the streak; a single null between trues remains could-not-look. The existing selfcheck exercises three-null FAIL, true interruption and three-missing FAIL. The registered `.estate-clone/driftwood/verify-cage-probe.sh`, `.estate-clone/tuppence/verify-cage-probe.sh` and `.estate-clone/ludlow/verify-cage-probe.sh` invoke that selfcheck and all have PASS in the unchanged [recorded run 432 table](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/d096cd2f0515a8aa2f9de1b671f5f227beba5478/talk/captures/_grades.tsv). No new check or test run is claimed here.

The original registration for facts 1–5 is unchanged. The honest October 18 current re-registration in [Driftwood](https://github.com/policy-as-versioned-driftwood/driftwood/commit/5a1b9a1ae85f88dfe91a71aca8eeb308349097ff), [Tuppence](https://github.com/policy-as-versioned-tuppence/tuppence/commit/e7e2969cd50ab3e88fa11afe61d5bee5d1db30d4) and [Ludlow](https://github.com/policy-as-versioned-ludlow/ludlow/commit/e65acc95bd107e0ba2864b2ca2f23b51714dc4c1) moves only the cage facts 6/7 section boundary. Ticket 161 still needs genuine scheduled observations after those main landings; older samples cannot answer the new registration. This ticket therefore stays claimed with its original `Blocked by: 161` intact. Tuppence's preserved scheduled fact 5 FALSE (one of 41 rendered objects missing from Flux inventory) is a measured failure, not a null or a reason to suppress a fall. No sample, original, grade, registration cutoff or first-new-schedule result is rewritten or invented.

**Resolved, 2026-10-21.** Ticket 161's first genuine post-registration schedules now satisfy
its literal criteria. The delivered facts 1–5 rule was also checked against this ticket's
own Done criterion: `grade` delegates to `_score`, which calls
`_source_facts_stay_unmeasured` separately for each source and every fact 1–5 over the three
newest distinct sample timestamps. Missing sources or facts count as unmeasured; an observed
TRUE or FALSE interrupts the null streak. Three nulls produce a named FAIL, without moving
the original facts 1–5 registration.

The existing public selfcheck has actual branches for two-null could-not-look, three-null
FAIL naming the fact/reason, TRUE interruption and three missing facts becoming FAIL.
The registered `.estate-clone/driftwood/verify-cage-probe.sh`,
`.estate-clone/tuppence/verify-cage-probe.sh` and
`.estate-clone/ludlow/verify-cage-probe.sh` each execute that selfcheck and all pass in the
unchanged recorded TRUTH436–438 captures. No new selfcheck or grader run is claimed by this
reconciliation. Tuppence's observed fact 5 FALSE remains a measured failure, not a null to
excuse or suppress. The `Blocked by: 161` declaration remains as dependency history; that
ticket is now resolved. [Ticket 161's record](161-fact-7-is-registered-again-with-a-reference-workload.md#answer)
links the exact first-scheduled originals and unchanged recorded probe tables; the published
grader links above carry the rule and selfcheck branches.
