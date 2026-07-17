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
revision, and its workload produces real `policy_report_result` entries (`4` of the app workloads
total, `ledger`/`api`/`storefront`/`reports`) — the existing dashboard's per-version panels see it
without any dashboard change, exactly as the design predicts (a policy version is just another
dependency). **Correction (2026-07-17, later adversarial pass)**: an earlier version of this line
said these metrics are "scoped to its own pod name" — that's wrong. `policy-reporter`'s own config
(`sourceFilters: uncontrolledOnly: true, kinds.exclude: [ReplicaSet]`) means Pod- and
ReplicaSet-kind results never reach `/metrics` at all; what actually feeds Prometheus/Grafana is
scoped to the owning **Deployment** name (`kind=Deployment, name=storefront`), confirmed by
querying `policy-reporter`'s `/metrics` endpoint directly. The Pod-kind `PolicyReport` *does* still
exist as a real Kubernetes object (`kubectl get policyreport` shows it, `orphan-guard: pass`
included) — it just isn't the layer the dashboard reads from. The higher-level claim ("appears
correctly in the dashboard's per-version data, zero dashboard changes needed") still holds; only
the specific pod-vs-Deployment scoping detail was wrong.

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

**A more serious finding from the same audit pass, also fixed**: a skeptic re-check pulled
storefront's *full* live `PolicyReport` (not just the two rules this doc happens to quote) and
found `orphan-guard=fail` — its pod would have been **denied at admission if recreated**, because
the live cluster's `ResourceSet` had drifted out of band (hand-edited outside git: the `2.2.0`
entry's `version` field was bumped to `2.2.1` while `tag`/`commit` still pointed at what git calls
`2.2.0`). Root cause: `clusters/cluster1/policy-versions.yaml` was never wired into continuous
Flux reconciliation, so nothing was correcting drift — see ticket 09's 2026-07-17 follow-up for
the full fix (a new `cluster-state` Kustomization) and its live proof. Restored the live
`ResourceSet` to match git immediately; confirmed `storefront`'s (and `api`'s, same drift)
`PolicyReport` shows `orphan-guard=pass` again. This is now structurally prevented from recurring,
not just patched once — Flux self-heals this file the same way it already self-heals every other
resource in this cluster.
