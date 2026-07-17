# 07 — First real app, end to end: storefront

**What to build:** The tracer bullet for the whole consumer story. One new team repo, `storefront`: a real (minimal) old-Angular static build served behind nginx, with a genuine npm dependency tree that is deliberately very stale; the workload labels itself policy-version 2.2.0 and carries its department label. Fleet gains the GitRepository+Kustomization pair; the workload admits under the real gates; Renovate (via ticket 06's preset) sees the stale package.json and opens real update PRs. This proves the full path once — repo → reconcile → admission under pinned version → live dependency signal — so the remaining four teams follow a proven road.

**Blocked by:** 06 — Renovate org preset (the repo extends it from birth).

**Status:** done

- [x] `storefront` repo with a real buildable app and deliberately old npm dependencies
- [x] Fleet reconciles it; the workload is Running, admitted under 2.2.0's gates, live-verified
- [x] A real Renovate PR against storefront's dependencies is observed (live-Renovate seam) — resolved 2026-07-17 (see ticket 06's follow-up): storefront#1/#2/#4 are real, live PRs including the Angular monorepo bump
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

Image public on GHCR, confirmed pullable with zero credentials.

## Follow-up (2026-07-17)

An adversarial audit flagged two staleness issues in this doc, both now corrected:
- The digest quoted above was superseded twice by later fixes (the npm lockfile fix, then shipping
  real `node_modules` for scanner visibility — see ticket 11's comments). Deliberately not pinning
  a specific digest in this doc anymore, since the deployed digest is expected to keep moving as
  the app evolves; the live source of truth is `storefront`'s own `k8s/deployment.yaml`, currently
  `sha256:ef53f41d...`.
- The "Renovate PR observed" checkbox is now checked: storefront#1/#2/#4 are real, confirmed live
  via `gh pr list` (see ticket 06's 2026-07-17 follow-up for the root cause and fix that unblocked
  this).
