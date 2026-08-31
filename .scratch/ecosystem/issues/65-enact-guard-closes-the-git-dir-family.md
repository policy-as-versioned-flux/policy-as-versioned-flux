# 65 — enact_guard closes the --git-dir family

Type: task (AFK)
Status: open
Blocked by: none

## Question

git --git-dir=<enactment>/.git push origin main resolves the remote against the caller's cwd, matches the self-push carve-out, and is ADMITTED — the same cwd-dependent class as the fixed -C hole. Extend _effective_cwd to --git-dir and --git-dir= (and --work-tree), scrub or handle GIT_DIR from the environment at the guard boundary, and ship tests that fail against current behaviour, mirroring the four tests the -C fix landed. Done = the probe shapes REFUSE and the tests run in the gate.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M17 (enact_guard --git-dir bypass).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
