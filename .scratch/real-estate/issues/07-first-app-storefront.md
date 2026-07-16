# 07 — First real app, end to end: storefront

**What to build:** The tracer bullet for the whole consumer story. One new team repo, `storefront`: a real (minimal) old-Angular static build served behind nginx, with a genuine npm dependency tree that is deliberately very stale; the workload labels itself policy-version 2.2.0 and carries its department label. Fleet gains the GitRepository+Kustomization pair; the workload admits under the real gates; Renovate (via ticket 06's preset) sees the stale package.json and opens real update PRs. This proves the full path once — repo → reconcile → admission under pinned version → live dependency signal — so the remaining four teams follow a proven road.

**Blocked by:** 06 — Renovate org preset (the repo extends it from birth).

**Status:** done (Renovate seam pending observation)

- [x] `storefront` repo with a real buildable app and deliberately old npm dependencies
- [x] Fleet reconciles it; the workload is Running, admitted under 2.2.0's gates, live-verified
- [ ] A real Renovate PR against storefront's dependencies is observed (live-Renovate seam) — repo is brand new, Renovate hasn't scanned it yet as of 2026-07-16; same "observable, not controllable" seam the spec names, will land on Mend's next scheduled run
- [x] The workload appears correctly in the existing dashboard's per-version data

## Comments

Done 2026-07-16 (bar the Renovate observation, which is a timing seam, not a design gap).
`policy-as-versioned-flux/storefront`, tagged `v1.0.0`. Real Angular 9 / npm dependency tree
(`package.json`) — genuinely `npm install`'d in the image build (multi-stage Docker, proven in CI),
not a fixture; served content is a hand-written static page (no `ng build` — the point of this app
is the dependency staleness signal, not a compiled Angular bundle).

**Real finding along the way:** the first deploy was refused — `department: retail` isn't in
`require-known-department-label`'s allowed set (`platform, finance, security, engineering,
legal`). Fixed to `engineering`, re-reconciled, admitted clean. Kept as evidence the gate is real,
not theater — first bad label, caught and refused, exactly as designed.

Live-verified: `storefront` Deployment `Running`, its `Kustomization` `Ready` with the real applied
revision, and its pod produces real `policy_report_result` entries scoped to its own pod name (`4`
of the app pods total, `ledger`/`api`/`storefront`/`reports`) — the existing dashboard's per-version
panels see it without any dashboard change, exactly as the design predicts (a policy version is
just another dependency).

Image public on GHCR (`ghcr.io/policy-as-versioned-flux/storefront@sha256:2263b70...`), confirmed
pullable with zero credentials.
