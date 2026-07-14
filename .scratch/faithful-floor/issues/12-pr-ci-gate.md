# 12 — PR CI gate on bump PRs

**What to build:** Make the Renovate bump PR trustworthy before merge (PRD §5 update lifecycle): CI on the fleet/consumer PR runs `flux build`/`flux diff` (what will change), `kyverno apply` + `kyverno test` against the incoming version (what will be judged), identity-pinned `gitsign verify` of the incoming tag (offline Rekor bundle), and the tag-resolves-to-pinned-SHA assertion. A reviewer sees exactly what merging adopts.

**Blocked by:** 04 — Signed release pipeline, 11 — Renovate customManager.

**Status:** ready-for-agent

- [x] The bump PR's CI renders a flux diff of the change
- [x] Fixtures for the incoming policy version run in the PR; a failing fixture fails the PR
- [x] `gitsign verify` (issuer+subject pinned, offline Rekor) and the tag→SHA check gate the merge
- [x] A deliberately force-moved tag in a test scenario is caught by CI, not adopted

## Comments

Done 2026-07-14. `fleet/pr-gate-check.sh` (called by `.github/workflows/pr-gate.yml`, and directly
runnable locally against any two refs) does exactly the four checklist items per `{version, tag,
commit}` array entry: `gitsign verify-tag` identity-pinned against an offline Rekor bundle
(reusing the actions/checkout tag-flattening fix from issue 04), the tag-resolves-to-pinned-commit
assertion (this is where ADR-0001's "a mismatched pair would otherwise be invisible at runtime"
check actually lives -- issue 04's own release workflow could only check same-run consistency),
`kyverno test` against the incoming commit's own fixtures, and `flux build --dry-run` (no cluster
needed) diffed against the base ref's pin for the same entry.

Proven three ways: a local run against the real array using tags that already exist (clean
3-entry pass); a synthetic "changed" base built in a throwaway git worktree, to exercise the
diff-detection path; a synthetic mismatched-commit case, proving the gate genuinely rejects a bad
pin rather than adopting it. Then proven live in real GitHub Actions with an actual test PR
(policy-as-versioned-flux/fleet#1, closed without merging).

Found and fixed along the way: the gate is required by a branch ruleset
(`policy-as-versioned-flux/fleet`, "require-pr-gate"), and a required check originally gated by
the workflow's own `paths: [clusters/**]` trigger filter never reports any status on a PR that
doesn't touch those paths -- a well-known GitHub gotcha where the merge then blocks forever
waiting on a check that was never going to run. Moved the path decision into the script itself (a
plain `git diff`), so the workflow always runs and always reports a real status.

That fix (plus README docs) is sitting in an open, CI-green PR
(policy-as-versioned-flux/fleet#2) rather than pushed directly to main -- the ruleset now requires
it, and even if it didn't, merging my own PR without a human's review would contradict the exact
"the PR is the unit of debate, never automerged" principle this ticket exists to prove. Waiting on
the user to review and merge it.
