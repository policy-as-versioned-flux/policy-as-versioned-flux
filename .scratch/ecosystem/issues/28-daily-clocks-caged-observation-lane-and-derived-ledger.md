# 28 — Daily clocks, caged observation lane and derived ledger

Type: task (AFK)
Status: open
Blocked by: 09, 21

## Question

Add a daily `schedule:` to the publisher fetch, Renovate, `propose-tier` and the org twin sweep on every unit. Cage the observation lane: a repo ruleset limits the scheduled workflow identity to observation paths (`truth.log`, `drift/samples.jsonl`, gate captures), bot commits are signed, verified live on the six repos. Make `propose-tier` re-compose at today's date before proposing, commit nothing. Derive the rejection ledger from closed-unmerged PRs on the dedupe branch with `sum(0.5 ** (age_days / h))`, key `<org>/<kind>/<slug>`, remove `DEFAULT_REJECTIONS`. Ship `verify-schedules.sh` in the gate: each clock ran within its period, no scheduled run changed a signed artefact. Supersede ADR-0015 point 5 with a new ADR.

## Notes

Graduated 2026-08-28 from ticket 10's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
