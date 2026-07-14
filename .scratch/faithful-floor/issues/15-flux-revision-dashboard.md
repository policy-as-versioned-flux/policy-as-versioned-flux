# 15 — Flux revision metrics + shared-variable dashboard

**What to build:** The "which version, where?" layer (ADR-0008): Flux source revision exposed via kube-state-metrics `customResourceState` (the flux2-monitoring-example pattern — Flux does not export this itself), joined with the PolicyReports panel on one dashboard through a shared `cluster` + `policy-version` template variable (not a PromQL join). At this point the P1 **measurable** acceptance holds: revision + PolicyReports levels answer the first two CIO questions.

**Blocked by:** 14 — Policy Reporter → Prometheus.

**Status:** ready-for-agent

- [x] `gotk_resource_info`-style revision metrics show every pinned policy version per cluster
- [x] One dashboard, shared `cluster`+`policy-version` variable driving both panels
- [x] Selecting a version shows where it's installed and whether workloads on it pass

## Comments

Done 2026-07-14, proven live on `cluster1`. `kube-state-metrics`'s `customResourceState` feature
(the `flux2-monitoring-example` pattern -- Flux doesn't export its own resource state as metrics),
trimmed to the 3 Flux kinds this repo actually uses (`GitRepository`, `Kustomization`,
`HelmRelease`) rather than upstream's full 12-kind coverage. `flux-policy-dashboard.json` (via a
kustomize `configMapGenerator`, same Grafana-sidecar auto-discovery mechanism as issue 14's Policy
Reporter dashboards): one dashboard, two panels sharing a `cluster`+`policy_version` variable --
"which version, where" (`gotk_resource_info`) and "is it passing" (`policy_report_result`).
`policy_version` is a real Prometheus query variable (regex over `GitRepository` names like
`policy-2.1.1`), not a hardcoded list.

Tried Prometheus `externalLabels` first for the `cluster` variable, reverted it: those only apply
to federation/remote-write, confirmed empty on every local query even after a real Prometheus pod
restart (not a caching artifact) -- not what a shared dashboard variable needs. `cluster` is a
single fixed value today (one Prometheus per cluster); real cross-cluster querying (Thanos,
federation, or a per-cluster datasource this variable picks between) is issue 10's design question
once `cluster2` exists, deferred rather than faked with a value that doesn't actually filter
anything.

`fleet/verify-flux-dashboard.sh` proves live: `gotk_resource_info` covers every installed version,
the dashboard ConfigMap carries the sidecar label, and selecting each of the three installed
versions resolves real, non-empty data on both panels (not just "some data exists somewhere" --
counted per version).

Landed via `policy-as-versioned-flux/fleet#4` (stacked on the still-open #3, branch ruleset
requires PRs now, issue 12) -- CI-green, waiting on the user to review and merge (in order, #3
then #4).
