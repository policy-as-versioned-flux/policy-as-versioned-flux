# 03 — Extract the PR gate into a versioned Action repo

**What to build:** The PR gate becomes a composite GitHub Action in its own component repo, released and pinned by fleet like any governed dependency — the extraction pattern's first instance, and philosophically on-thesis: the gate that verifies pins is itself pinned. Fleet's workflow shrinks to invoking the pinned action; the gate's behaviour (gitsign verify-tag identity-pinned, tag-resolves-to-commit, kyverno fixtures, flux build dry-run, and ticket 01's version cross-check) is unchanged. The component carries its own runnable self-check, per the established idiom.

**Blocked by:** 01 — Opening pass (the cross-check lands in the gate before the gate moves, not mid-flight).

**Status:** ready-for-agent

- [ ] New component repo with the composite Action + its own self-check, released with a version tag
- [ ] Fleet's CI consumes the Action at a pinned version and stays green
- [ ] The synthetic-mismatch and force-moved-tag rejections still fire through the extracted packaging
- [ ] Renovate can see the Action pin as a bumpable dependency
