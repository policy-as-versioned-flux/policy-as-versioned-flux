# 14 — Policy Reporter → Prometheus + PolicyReports panel

**What to build:** The "is it actually passing?" layer of measurable (ADR-0008): Policy Reporter installed (pinned, like the engine) turning Kyverno PolicyReports into Prometheus metrics, and a Grafana panel answering pass/fail per policy per version. Background scans mean lane-keeping violations are visible without blocking anything.

**Blocked by:** 08 — ResourceSet coexistence matrix.

**Status:** done

- [x] PolicyReport results for all installed versions appear as Prometheus metrics
- [x] A Grafana panel shows pass/fail counts filterable by `policy-version`
- [x] A deliberately non-compliant Audit-mode workload shows as failing without being evicted

## Comments

Done 2026-07-14, proven live on `cluster1`. `fleet/infrastructure/monitoring/`: kube-prometheus-stack
+ Policy Reporter, both pinned (same governed-dependency posture as Kyverno). Policy Reporter's
`metrics.enabled`/`mode: detailed` turns PolicyReport results into Prometheus metrics labelled by
`policy` (which carries the version suffix baked into each ValidatingPolicy's nameSuffix) --
`monitoring.grafana.dashboards.enabled` ships its own pre-built dashboards (PolicyReports,
PolicyReport Details, ClusterPolicyReport Details) as ConfigMaps for kube-prometheus-stack's
Grafana sidecar to auto-discover. No hand-authored dashboard JSON -- the "policy" filter these
dashboards already have covers "filterable by policy-version" since that's part of the label
value. Alertmanager disabled (issue 16 is a different mechanism/signal, Flux's own
notification-controller); no PersistentVolume (ephemeral demo infra).

Found and fixed live: kube-prometheus-stack's Prometheus only selects ServiceMonitors carrying
`release: kube-prometheus-stack` -- without that label Policy Reporter's ServiceMonitor existed
but was silently never scraped (metrics visible at Policy Reporter's own `/metrics`, absent from
every Prometheus query). Fixed via `monitoring.serviceMonitor.labels`.

`fleet/verify-monitoring.sh`: queries Prometheus (not Policy Reporter directly) for metrics
mentioning every installed version, then creates a pod that's non-compliant under the Audit-only
`require-owner-annotation` policy and confirms it shows `status="fail"` in Prometheus while
staying `Running` throughout (polled, same async-report pattern as issues 03/06). Both green.

Landed via `policy-as-versioned-flux/fleet#3`, merged 2026-07-15. `verify-monitoring.sh` updated
(was hardcoded to the retired `2.1.1` version string) and re-run green against the real, merged,
live cluster -- metrics present for all 3 currently-installed versions (`1.0.0`/`2.0.0`/`2.2.0`),
non-compliant Audit workload reported as failing without eviction.
