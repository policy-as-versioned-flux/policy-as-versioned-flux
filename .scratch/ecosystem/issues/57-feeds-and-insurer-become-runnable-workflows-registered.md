# 57 — feeds and insurer become runnable: workflows registered, first signed tags cut

Type: task (HITL)
Status: open
Blocked by: none

## Question

GitHub registers zero workflows in feeds and insurer (0 runs ever) despite files on the default branch with Actions enabled, so their crons never fire and cut-release cannot be dispatched — the only route to a gitsign-signed first tag. Diagnose the registration failure (the unconventional default branch ecosystem/thin-slice is the prime suspect; renaming or pushing a registering commit are the candidate fixes), then the owner dispatches cut-release once per repo to cut the first signed feed and quote tags, queues bump.yaml so releases can follow, and we confirm the next day's cron fires. HITL because the branch decision and every dispatch are the owner's. Done = both repos show a scheduled run and at least one signed tag each, and the adopter subscriptions' could-not-looks convert on a citable run.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M1 (feeds/insurer unrunnable, 2 confirmed findings), the zero-signed-tags leg of M10, minor stale feeds tree on platform (once first tag exists).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
