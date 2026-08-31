# 55 — Every red on the clock is real, explained, and finishable

Type: task (AFK)
Status: open
Blocked by: none

## Question

Three of run 13's reds are instrument faults, not estate state. (a) verify-corpus-generator: replace the ls|head pipeline with a glob so SIGPIPE cannot red a healthy generator. (b) verify-publisher-gate: set VERIFY_TIMEOUT for the scheduled run or split the four parts into separately graded scripts, and make each part flush incremental output so a timeout still leaves evidence. (c) verify-source-verification: teach verify_gitsign.py to print trust-material failures ("unable to get local issuer certificate") as could-not-look exit 3, never REJECTED, and fix the CI runner's chain build so the real tag verifies (it verifies locally against only the pinned roots). Also stop discarding stderr in render-version-tree and change its exit-0-on-missing-kyverno to exit 3. Done = each script either passes, or reds with its observed-false named, on a scheduled run.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M2 (source-verification, 3 confirmed findings), M3 (publisher-gate, 2 confirmed findings), M4 (corpus SIGPIPE), minors render-red-carries-no-reason and skip-graded-as-pass.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
