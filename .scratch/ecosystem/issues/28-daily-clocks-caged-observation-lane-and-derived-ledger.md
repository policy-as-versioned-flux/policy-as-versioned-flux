# 28 — Daily clocks, caged observation lane and derived ledger

Type: task (AFK)
Status: resolved
Blocked by: 09, 21

## Question

Add a daily `schedule:` to the publisher fetch, Renovate, `propose-tier` and the org twin sweep on every unit. Cage the observation lane: a repo ruleset limits the scheduled workflow identity to observation paths (`truth.log`, `drift/samples.jsonl`, gate captures), bot commits are signed, verified live on the six repos. Make `propose-tier` re-compose at today's date before proposing, commit nothing. Derive the rejection ledger from closed-unmerged PRs on the dedupe branch with `sum(0.5 ** (age_days / h))`, key `<org>/<kind>/<slug>`, remove `DEFAULT_REJECTIONS`. Ship `verify-schedules.sh` in the gate: each clock ran within its period, no scheduled run changed a signed artefact. Supersede ADR-0015 point 5 with a new ADR.

## Notes

Graduated 2026-08-28 from ticket 10's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. Daily clocks on every unit, and the observation lane is caged. A scheduled job may append only truth.log, drift samples and captures; its git add is an explicit allow-list and the job fails on any other change. Each repo carries the ruleset it needs as a committed file for the owner to apply. verify/schedules/ parses the workflow YAML rather than grepping it. The rejection ledger is derived from closed unmerged PRs; DEFAULT_REJECTIONS is gone. ADR-0024 supersedes ADR-0015 point 5.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.

**Corrected 2026-09-03 (ticket 70).** "the observation lane is caged" and "Each repo carries the ruleset it needs as a committed file for the owner to apply" overstated what was built. The committed file was a branch ruleset carrying a push-ruleset rule (reshaped 2026-08-28), and a push ruleset cannot be applied to a public repository at all, so no ruleset has ever been in force on any of the nine and none can be while they stay public (ticket 58 Q4(b)). What held on 2026-08-29 was the cage step in each workflow and `verify-schedules`' parse of it: prevention with no server behind it. From 2026-09-03 the gate also grades what landed: `verify/schedules/verify-lane.sh` walks the first-parent history of every observation ref (each unit's `main`, the orphan `observations` branch on platform, feeds, nist, ico and insurer, and the hub's `main`) and fails on any commit a scheduled identity landed outside the lane or as a merge. On that day every landed commit was inside it: 4 drift samples on each of driftwood, tuppence and ludlow, 3 fetch observations on each publisher's `observations` branch and 1 on feeds', 17 truth commits on the hub. ADR-0023 carries the dated amendment and the revisit trigger (going private).
