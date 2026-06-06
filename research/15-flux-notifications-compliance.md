# Flux CD — Notifications, Events & Observability

> Maps to the original work's **"measurable / visible compliance"** pillar.
> Sources: deepwiki (`fluxcd/notification-controller`), fluxcd.io docs, web search (2025/2026). Current API versions: `notification.toolkit.fluxcd.io/v1beta3` (Provider, Alert), `notification.toolkit.fluxcd.io/v1` (Receiver). `v1beta1`/`v1beta2` are deprecated.

---

## 1. notification-controller in one picture

The notification-controller is the GitOps Toolkit **event forwarder + webhook dispatcher**. It does two opposite-direction jobs:

- **Outbound (Alert + Provider):** Flux controllers (source/kustomize/helm/image) emit Kubernetes `Events`; the notification-controller filters them (Alert) and ships them to a destination (Provider) — Slack, Teams, GitHub commit status, generic webhook, etc.
- **Inbound (Receiver):** external systems (GitHub, GitLab, image registries) POST a webhook to the controller, which validates it and pokes the named Flux resources to reconcile **immediately** rather than waiting for the poll interval.

Three CRDs: **Provider** (where + how to send), **Alert** (what to send, filtering), **Receiver** (what incoming webhooks trigger).

---

## 2. Provider CRD — where events go

`ProviderSpec` key fields: `type`, `address`, `channel`, `username`, `timeout`, `secretRef`, `certSecretRef`, `proxySecretRef` (replaces deprecated `proxy`), `serviceAccountName` (object-level workload identity), `commitStatusExpr` (CEL, Git providers only), `suspend`.

### Slack
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: platform-alerts
  address: https://slack.com/api/chat.postMessage
  secretRef:
    name: slack-token
---
apiVersion: v1
kind: Secret
metadata:
  name: slack-token
  namespace: flux-system
stringData:
  token: xoxb-...        # Slack bot token
```

### Microsoft Teams
Address is the **Teams Incoming Webhook Workflow URL** (Power Automate), held in the secret. The controller auto-formats as an Adaptive Card or Office365 connector message depending on the host.
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: msteams
  namespace: flux-system
spec:
  type: msteams
  secretRef:
    name: msteams-webhook
---
apiVersion: v1
kind: Secret
metadata:
  name: msteams-webhook
  namespace: flux-system
stringData:
  address: https://prod-xx.logic.azure.com:443/workflows/.../invoke?...
```

### Generic webhook (+ HMAC)
Generic POSTs the JSON `Event` object with a `Gotk-Component` header. `generic-hmac` additionally signs the body with sha256 in an `X-Signature` header so the receiver can verify authenticity.
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: generic-hmac
  namespace: flux-system
spec:
  type: generic-hmac          # use "generic" for unsigned
  address: https://my-eventbus.internal/flux
  secretRef:
    name: webhook-auth
---
apiVersion: v1
kind: Secret
metadata:
  name: webhook-auth
  namespace: flux-system
stringData:
  token: shared-hmac-secret
  headers: |                  # extra static headers (generic)
    Authorization: Bearer xxxx
```
Other built-in types: `googlechat`, `webex`, `sentry`, `telegram`, `discord`, `googlepubsub`, `azureeventhub`, `nats`, `opsgenie`, `pagerduty`, `rocket`, `lark`, `matrix`, `grafana` (annotations), `alertmanager`. mTLS via `certSecretRef`; authenticated proxy via `proxySecretRef`.

---

## 3. Alert CRD — what gets sent (filtering)

`AlertSpec`: `providerRef`, `eventSources[]` (`kind`/`name`, `name: '*'` = all), `eventSeverity` (`info`|`error`), `inclusionList`/`exclusionList` (regex on the message), `eventMetadata` (extra KV attached to outbound events — handy for tagging cluster/region/policy version), `summary`, `suspend`.

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: on-call
  namespace: flux-system
spec:
  summary: "Reconciliation failed in prod-eu-west-2"
  providerRef:
    name: slack
  eventSeverity: error
  eventMetadata:
    cluster: prod-eu-west-2
    env: production
  eventSources:
    - kind: Kustomization
      name: '*'
    - kind: HelmRelease
      name: '*'
    - kind: GitRepository
      name: '*'
  exclusionList:
    - "waiting for dependencies"
```

---

## 4. Git commit status — "clear CI feedback when non-compliant"

This is the killer feature for the compliance pillar: Flux writes the **apply result back onto the Git commit / PR** as a status check (green tick / red cross), so a policy bump that fails to apply on a cluster shows up *on the commit that introduced it*.

**Mechanism:** push commit → source-controller syncs → kustomize-controller reconciles → emits an event carrying the **commit hash it reconciled** → notification-controller calls the Git SaaS status API for that SHA. **Only `Kustomization` events carry the commit ref**, so commit-status Alerts must target Kustomizations.

Supported provider types: `github`, `gitlab`, `gitea`, `bitbucket`, `bitbucketserver`, `azuredevops`.

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: github-status
  namespace: flux-system
spec:
  type: github
  address: https://github.com/my-org/fleet-config   # repo URL
  secretRef:
    name: github-token                               # PAT or GitHub App creds
  # Optional CEL: customise the status context string so each
  # cluster/kustomization gets its own distinct check
  commitStatusExpr: >-
    (event.involvedObject.kind + '/' + event.involvedObject.name +
     '/' + provider.metadata.uid.split('-').first().value()).lowerAscii()
---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: github-status
  namespace: flux-system
spec:
  providerRef:
    name: github-status
  eventSources:
    - kind: Kustomization
      name: flux-system        # the Kustomization carrying the policy version
```
`commitStatusExpr` CEL variables: `event`, `provider`, `alert`. Custom contexts matter at fleet scale: if every cluster reports to the **same** default status context they overwrite each other; the expression gives each cluster a unique check so a PR shows N green ticks ("applied cleanly on all N clusters") or a red cross on the one that failed. PR-gating: branch protection can require those checks before merge → a policy change cannot merge unless it reconciles.

### githubdispatch — trigger Actions from Flux events
Distinct from `github`. Sends a `repository_dispatch` with `event_type = {Kind}/{Name}.{Namespace}` and `client_payload` = full Flux event. Use to kick CI (e.g. smoke tests) after a successful apply.
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata: { name: github-dispatch, namespace: flux-system }
spec:
  type: githubdispatch
  address: https://github.com/my-org/fleet-config
  secretRef: { name: github-token }
```
```yaml
# .github/workflows/post-apply.yaml
on:
  repository_dispatch:
    types: [Kustomization/podinfo.flux-system]
jobs:
  smoke:
    if: github.event.client_payload.metadata.summary == 'production'
    runs-on: ubuntu-latest
    steps: [{ run: echo "running post-apply tests" }]
```

---

## 5. Receiver CRD — instant reconcile from webhooks

Without a Receiver, Flux polls Git on `spec.interval` (e.g. 1m–10m). A Receiver collapses that to **seconds**: GitHub push → webhook → reconcile now.

`ReceiverSpec`: `type` (`github`, `gitlab`, `bitbucket`, `generic`, `generic-hmac`, plus registry types `harbor`/`dockerhub`/`quay`/`gcr`/`acr`/`nexus`, and `cdevents`), `resources[]` (objects to reconcile; `name: '*'` + `matchLabels` for label selection), `secretRef` (token used both for HMAC validation **and** to derive the webhook path), `events[]` (filter e.g. `push`/`ping`), `resourceFilter` (CEL over `req` payload + `res` resource), `interval`, `suspend`.

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1
kind: Receiver
metadata:
  name: github-receiver
  namespace: flux-system
spec:
  type: github
  events: ["ping", "push"]
  secretRef:
    name: receiver-token
  resources:
    - apiVersion: source.toolkit.fluxcd.io/v1
      kind: GitRepository
      name: flux-system
```
```bash
TOKEN=$(head -c 12 /dev/urandom | shasum | cut -d ' ' -f1)
kubectl -n flux-system create secret generic receiver-token --from-literal=token=$TOKEN
```
**Exposing the endpoint:** the controller generates a path `/hook/<sha256(token+name+namespace)>`. Read it from `kubectl -n flux-system describe receiver github-receiver` (Status → Webhook Path), expose the `notification-controller` Service's `webhook-receiver` port via Ingress, then point the GitHub webhook at `https://<host>/hook/<sha>` using the same `$TOKEN` as the webhook secret. GitHub validates with `X-Hub-Signature` HMAC; GitLab uses `X-Gitlab-Token`.

---

## 6. Events & metrics

### Controller-native Prometheus metrics (port `:8080/metrics`)
- `gotk_reconcile_duration_seconds_{bucket,sum,count}{kind,name,namespace,le}` — reconcile latency histogram.
- `gotk_reconcile_condition{kind,name,namespace,type,status}` — condition state. `type` ∈ `Ready`,`Reconciling`,`Stalled`,`Healthy`; `status` ∈ `True`,`False`,`Unknown`,`Deleted`. **Note:** since Flux v2.1 this only exports for *live* objects; for HelmRelease it was briefly missing in 2.2.x — the recommended modern path for resource readiness is kube-state-metrics (`gotk_resource_info`, below).
- `gotk_suspend_status{kind,name,namespace}` — 1 if suspended.
- `controller_runtime_reconcile_total{controller,result}`, workqueue depth/latency — controller-runtime health.
- `gotk_token_cache_events_total`, `gotk_cache_events_total` — cache hit/miss.

Scrape with a **PodMonitor** (all four controllers carry `app.kubernetes.io/part-of: flux`):
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: flux-system
  namespace: flux-system
spec:
  namespaceSelector: { matchNames: [flux-system] }
  selector:
    matchExpressions:
      - { key: app, operator: In,
          values: [source-controller, kustomize-controller, helm-controller, notification-controller, image-automation-controller, image-reflector-controller] }
  podMetricsEndpoints:
    - port: http-prom
```

### kube-state-metrics: `gotk_resource_info` (the fleet-compliance metric)
Resource state metrics are **not** emitted by Flux controllers; they are generated by configuring kube-state-metrics' `CustomResourceStateMetrics` over the Flux CRDs (see `fluxcd/flux2-monitoring-example`). This exposes one info-metric per object with `ready`/`suspended` and — crucially — the **revision** label that carries the source tag in use:
```yaml
kind: CustomResourceStateMetrics
spec:
  resources:
    - groupVersionKind:
        group: kustomize.toolkit.fluxcd.io
        version: v1
        kind: Kustomization
      metricNamePrefix: gotk
      metrics:
        - name: resource_info
          help: "The current state of a GitOps Toolkit resource."
          each:
            type: Info
            info:
              labelsFromPath:
                name: [metadata, name]
          labelsFromPath:
            exported_namespace: [metadata, namespace]
            ready:     [status, conditions, "[type=Ready]", status]
            suspended: [spec, suspend]
            revision:  [status, lastAppliedRevision]   # <-- the policy version applied
    # repeat for GitRepository (status.artifact.revision / spec.ref.tag),
    # OCIRepository, HelmRelease (status.lastAppliedRevision), HelmRepository
```
Yielding e.g. `gotk_resource_info{customresource_kind="Kustomization", name="kyverno-policies", exported_namespace="flux-system", ready="True", suspended="false", revision="v3.4.1@sha256:..."}`.

PromQL building blocks:
```promql
# Failing Kustomizations across the fleet
gotk_resource_info{customresource_kind="Kustomization", ready="False"}

# Count ready vs not, per cluster (cluster label added by Prometheus external_labels / federation)
sum by (cluster) (gotk_resource_info{customresource_kind="Kustomization", ready="True"})

# p95 reconcile latency
histogram_quantile(0.95, sum(rate(gotk_reconcile_duration_seconds_bucket[5m])) by (le, kind))
```

### Grafana dashboards
`fluxcd/flux2-monitoring-example` ships two: **Flux Cluster Stats** (source + reconciler ready/suspended counts, per kind) and **Flux Control Plane** (controller CPU/mem, reconcile rate, workqueue). Both are fed by the PodMonitor + KSM config above.

---

## 7. Measuring FLEET COMPLIANCE — answering the CIO's question

> *"What version of policy is each part of my estate on, and is it compliant?"*

Two independent facts, joined on cluster:

**(A) Which policy VERSION each cluster runs** comes from the Flux **source revision** + the `revision` label on `gotk_resource_info` for the Kustomization/OCIRepository that delivers the policy bundle. If policies are shipped as a semver-tagged OCI artifact or Git tag (e.g. `OCIRepository` pinned to `v3.4.1`), the tag *is* the estate-wide policy version. A single-stat/table panel keyed on `gotk_resource_info{name="kyverno-policies"}` grouped by `cluster` answers "version per cluster" directly.

**(B) Whether each cluster is COMPLIANT** comes from **Kyverno PolicyReports** (namespaced `PolicyReport` / cluster-scoped `ClusterPolicyReport`, Policy WG standard) with `pass`/`fail`/`warn`/`error`/`skip` summary counts. Expose these as Prometheus metrics via **Policy Reporter** (`kyverno/policy-reporter`), which watches the report CRDs, emits metrics + ships a Grafana dashboard and a ServiceMonitor, and can fan out to Slack/Teams/Loki/Elasticsearch.

**Concrete observability design (single Grafana, fleet-wide):**
1. Each cluster runs Flux (PodMonitor + KSM `gotk_resource_info`) and Kyverno + Policy Reporter.
2. Add a `cluster` external label per Prometheus (or Prometheus Agent → central Thanos/Mimir, or `--federate`). Now every series is cluster-attributable.
3. **Panel 1 — "Policy version per cluster":** table of `gotk_resource_info{name="kyverno-policies", customresource_kind=~"OCIRepository|Kustomization"}` showing `cluster` × `revision`. Drift (a cluster lagging on an old tag) is visually obvious.
4. **Panel 2 — "Delivery health":** `gotk_resource_info{ready="False"}` by cluster — a policy bump that failed to apply (= the cluster is *stuck* on the old version) lights up red, and the same failure already appears as a red commit status on the offending PR (§4).
5. **Panel 3 — "Runtime compliance":** Policy Reporter `policy_report_result{status="fail"}` by cluster/policy/namespace — workloads actually violating policy *right now*.
6. **The join:** "version applied (Flux revision) + version enforcing-cleanly (Ready=True) + zero failing PolicyReport results" = green across the row. Any cluster on an old `revision`, or `Ready=False`, or with `fail>0`, is non-compliant and identifiable by name. Alerts in §3 (error-severity Alert → Slack/Teams) and §4 (red commit status) close the loop so non-compliance is *pushed*, not just dashboarded.

This is the full "measurable / visible compliance" story: **Git commit status = compliance feedback at change time; Flux revision metrics = which version is deployed where; Kyverno PolicyReports = is it actually compliant; one Grafana = the estate view the CIO asked for.**

---

## 8. Flux UIs / dashboards for visibility

- **Capacitor** (`gimlet-io/capacitor`) — the de-facto open-source Flux UI in 2025/26. Browser view of GitRepositories, OCIRepositories, Kustomizations, HelmReleases with source ref, path, **last applied revision**, Ready/Progressing/Failed status and error messages; trigger reconcile/suspend from the UI. Most ex-Weave users land here.
- **Weave GitOps OSS** — historically the reference Flux UI, but the v0.38.0 dashboard calls a removed Flux API and is effectively broken; the fix sits unpromoted in v0.39.1-rc.1. Treat as legacy; prefer Capacitor.
- **flux-operator** (`controlplaneio-fluxcd/flux-operator`) + its MCP server / `FluxInstance` + reporting — operator-managed Flux installs with an aggregated `FluxReport` resource summarising component + resource health, useful as a machine-readable estate status object.
- **CLI:** `flux get all -A`, `flux get kustomizations -A`, `flux tree kustomization` for terminal-level status; pairs with the metrics for automation.

---

## Sources
- deepwiki: [fluxcd/notification-controller](https://deepwiki.com/fluxcd/notification-controller)
- [Flux Providers](https://fluxcd.io/flux/components/notification/providers/) · [Alerts](https://fluxcd.io/flux/components/notification/alerts/) · [Receivers](https://fluxcd.io/flux/components/notification/receivers/) · [Setup Notifications guide](https://fluxcd.io/flux/guides/notifications/)
- [Flux Prometheus metrics](https://fluxcd.io/flux/monitoring/metrics/) · [Flux custom metrics](https://fluxcd.io/flux/monitoring/custom-metrics/) · [fluxcd/flux2-monitoring-example](https://github.com/fluxcd/flux2-monitoring-example)
- [kube-state-metrics CustomResourceState](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/metrics/extend/customresourcestate-metrics.md)
- [Introducing Capacitor](https://fluxcd.io/blog/2024/02/introducing-capacitor/) · [Weave GitOps as Flux UI](https://fluxcd.io/blog/2023/04/how-to-use-weave-gitops-as-your-flux-ui/) · [Weave GitOps 2026 status](https://computingforgeeks.com/weave-gitops-install-migration-flux/)
- [Policy Reporter](https://kyverno.github.io/policy-reporter/) · [Kyverno monitoring](https://kyverno.io/docs/guides/monitoring/)
- [Monitoring & Hardening the GitOps pipeline with Flux (MediaMarktSaturn)](https://medium.com/mediamarktsaturn-tech-blog/monitoring-and-hardening-the-gitops-delivery-pipeline-with-flux-a226bdef0351)
