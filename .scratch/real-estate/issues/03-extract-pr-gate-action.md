# 03 — Extract the PR gate into a versioned Action repo

**What to build:** The PR gate becomes a composite GitHub Action in its own component repo, released and pinned by fleet like any governed dependency — the extraction pattern's first instance, and philosophically on-thesis: the gate that verifies pins is itself pinned. Fleet's workflow shrinks to invoking the pinned action; the gate's behaviour (gitsign verify-tag identity-pinned, tag-resolves-to-commit, kyverno fixtures, flux build dry-run, and ticket 01's version cross-check) is unchanged. The component carries its own runnable self-check, per the established idiom.

**Blocked by:** 01 — Opening pass (the cross-check lands in the gate before the gate moves, not mid-flight).

**Status:** done

- [x] New component repo with the composite Action + its own self-check, released with a version tag
- [x] Fleet's CI consumes the Action at a pinned version and stays green
- [x] The synthetic-mismatch and force-moved-tag rejections still fire through the extracted packaging
- [x] Renovate can see the Action pin as a bumpable dependency

## Comments

Done 2026-07-16. `policy-as-versioned-flux/pr-gate-action`, tagged `v1.0.0`
(`98939ebd5ea5df7577eee71c21c3a25a4b68f123`). Composite Action wrapping the same
`pr-gate-check.sh` logic (gitsign verify-tag, tag-resolves-to-commit, kyverno test, flux build
dry-run, ticket 01's rendered-version cross-check), now operating on the caller's checkout
(`GITHUB_WORKSPACE`) instead of its own script directory -- the one real behavioural difference
extraction required, since the script no longer lives inside the repo it inspects.

Fleet's `pr-gate.yml` now invokes it digest-pinned
(`policy-as-versioned-flux/pr-gate-action@98939eb... # v1.0.0`), which Renovate's native
`github-actions` manager tracks out of the box (no customManager needed, unlike the policy
`{tag, commit}` pair — a `uses: owner/repo@sha # vX.Y.Z` line is exactly the shape that manager
already bumps).

**Proven three ways, not just replayed:**
1. Local replay of the extracted script against fleet's real `695cd13..c5a7cb0` diff — byte-
   identical `PASS` output to the pre-extraction script.
2. The component's own `verify.sh` self-check — clean pass against a real signed tag, rejection
   of a synthetic declared-version mismatch (`array declares 1.0.1` while the tag renders
   `1.0.0`) — proving the extraction preserved both success and failure paths.
3. **Real GitHub Actions, twice**: fleet PR #23 (the real change) confirmed the workflow wiring
   resolves and the no-op path still reports success; a throwaway PR (#24, closed unmerged once
   observed) forced a real `clusters/` diff and confirmed the *full* chain fires correctly
   through the extracted action in actual CI, not just locally — all nine policy/plane pairs
   rendered and cross-checked, `PR gate: PASS`.

Shipped as `fleet#23` (self-merged, standing authorization).
