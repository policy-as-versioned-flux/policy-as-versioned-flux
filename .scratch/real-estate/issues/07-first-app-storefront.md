# 07 — First real app, end to end: storefront

**What to build:** The tracer bullet for the whole consumer story. One new team repo, `storefront`: a real (minimal) old-Angular static build served behind nginx, with a genuine npm dependency tree that is deliberately very stale; the workload labels itself policy-version 2.2.0 and carries its department label. Fleet gains the GitRepository+Kustomization pair; the workload admits under the real gates; Renovate (via ticket 06's preset) sees the stale package.json and opens real update PRs. This proves the full path once — repo → reconcile → admission under pinned version → live dependency signal — so the remaining four teams follow a proven road.

**Blocked by:** 06 — Renovate org preset (the repo extends it from birth).

**Status:** ready-for-agent

- [ ] `storefront` repo with a real buildable app and deliberately old npm dependencies
- [ ] Fleet reconciles it; the workload is Running, admitted under 2.2.0's gates, live-verified
- [ ] A real Renovate PR against storefront's dependencies is observed (live-Renovate seam)
- [ ] The workload appears correctly in the existing dashboard's per-version data
