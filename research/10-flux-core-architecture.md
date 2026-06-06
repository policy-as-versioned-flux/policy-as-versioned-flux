# Flux CD — Core Architecture Reference

> Audience: an engineer designing a system on Flux CD.
> Scope: GitOps Toolkit controllers, reconciliation model, bootstrap, health/readiness,
> dependencies/ordering, the `flux` CLI for local build/validate/diff, and the security/multi-tenancy model.
> Sources: deepwiki (fluxcd/flux2, fluxcd/source-controller, fluxcd/kustomize-controller),
> fluxcd.io/flux docs, GitHub release notes. Cross-checked June 2026.

---

## 0. Version baseline (current GA)

- **Flux CLI / distribution: v2.8.x GA** (announced Feb 2026; `flux v2.8.1` patch). v2.7 is the prior minor.
- Bundled GitOps Toolkit controller versions in **Flux v2.8.0**:
  - source-controller **v1.8.0**
  - kustomize-controller **v1.8.0**
  - notification-controller **v1.8.0**
  - helm-controller **v1.5.0**
  - image-reflector-controller **v1.1.0**
  - image-automation-controller **v1.1.0**
  - source-watcher **v2.1.0**
- **Kubernetes support**: latest three minor versions. For Flux 2.8, baseline ≈ K8s v1.33 (later patches add 1.34/1.35).
- **2.8 notable changes**: ships **Helm v4** (server-side apply + kstatus health checking in helm-controller); `CancelHealthCheckOnNewRevision` extended to helm-controller; CEL health-check expressions for HelmReleases; custom SSA apply stages for kustomize-controller; Cosign v3; PR/MR-comment notification providers.
- **EOL APIs removed in 2.8**: `source.toolkit.fluxcd.io/v1beta2`, `kustomize.toolkit.fluxcd.io/v1beta2`, `helm.toolkit.fluxcd.io/v2beta2`. Migrate with `flux migrate`.

### API group / version map (Flux 2.7+/2.8)

| Kind | Group/Version | Owning controller |
|---|---|---|
| GitRepository, OCIRepository, Bucket, HelmRepository, HelmChart, ExternalArtifact | `source.toolkit.fluxcd.io/v1` | source-controller |
| Kustomization | `kustomize.toolkit.fluxcd.io/v1` | kustomize-controller |
| HelmRelease | `helm.toolkit.fluxcd.io/v2` | helm-controller |
| Receiver | `notification.toolkit.fluxcd.io/v1` | notification-controller |
| Alert, Provider | `notification.toolkit.fluxcd.io/v1beta3` | notification-controller |
| ImageRepository, ImagePolicy | `image.toolkit.fluxcd.io/v1` | image-reflector-controller |
| ImageUpdateAutomation | `image.toolkit.fluxcd.io/v1` | image-automation-controller |
| ArtifactGenerator | `source.watcher.fluxcd.io/v1beta1` | source-watcher |

> API stability: `v1`/`v2` are GA with strong backward-compatibility guarantees; breaking changes require a new major version. `Alert`/`Provider` remain at `v1beta3`.

---

## 1. The GitOps Toolkit controllers

Flux v2 is not a monolith. It is a set of single-purpose Kubernetes controllers ("the GitOps Toolkit") built on controller-runtime, sharing common libraries (`fluxcd/pkg`, the `apis/meta` condition types, and kstatus). Each controller owns its CRDs and runs as a Deployment in `flux-system`. They are loosely coupled via the **Artifact** abstraction (source-controller produces artifacts; appliers consume them) and via Kubernetes events (notification-controller).

### 1.1 source-controller
**Job:** acquire and cache the desired-state artifacts from external sources, expose them over an in-cluster HTTP file server, and verify their integrity/authenticity. It is the single ingress point for "what does Git/OCI/Helm/S3 say".

CRDs (`source.toolkit.fluxcd.io/v1`):
- **GitRepository** — clones Git over HTTPS/SSH, checks out a ref, produces a `.tar.gz` artifact. Auth: `secretRef` (basic auth `username`/`password`, `bearerToken`, SSH `identity`+`known_hosts`), provider auth (GitHub App, Azure, GCP, AWS via `spec.provider`).
- **OCIRepository** — pulls an OCI artifact (tag/digest/semver) → `.tar.gz`. Supports cloud provider auth (`spec.provider: aws|azure|gcp`) and **verification** (`spec.verify` with Cosign keyful/keyless + `matchOIDCIdentity`, or Notation trust policy).
- **HelmRepository** — HTTP/S repo → caches `index.yaml` artifact; or `type: oci` (acts as a credential/config container, produces no artifact itself).
- **HelmChart** — packages a chart from a HelmRepository/GitRepository/Bucket into a `.tgz`. `spec.reconcileStrategy: ChartVersion|Revision`. Usually created implicitly by a HelmRelease.
- **Bucket** — fetches objects from S3-compatible storage → `.tar.gz`. Static creds or cloud provider auth.
- **ExternalArtifact** — artifact produced by an external/third-party producer (e.g. source-watcher's ArtifactGenerator) rather than source-controller's own fetchers.

**Artifact** (the core abstraction): a file on the controller's storage volume, served at a URL in `status.artifact.url`. Fields: `path`, `url`, `revision` (human-traceable, e.g. `main@sha1:1eabc9a4…`, a tag, or chart version), `digest` (`<algorithm>:<hex>`, default sha256), `lastUpdateTime`, `size`. Other controllers fetch by URL and verify against `digest`.

### 1.2 kustomize-controller
**Job:** take a source artifact, build Kustomize overlays (or raw manifests), decrypt secrets (SOPS), and **apply to the cluster via server-side apply**, with pruning, health checks, and drift correction. Owns **Kustomization** (`kustomize.toolkit.fluxcd.io/v1`). This is the workhorse that also reconciles Flux itself (see Bootstrap).

### 1.3 helm-controller
**Job:** manage the full Helm release lifecycle declaratively. Owns **HelmRelease** (`helm.toolkit.fluxcd.io/v2`). From 2.8 uses **Helm v4** with server-side apply + kstatus health checks. Handles install/upgrade/test/rollback/uninstall, retries/remediation, and drift detection.

### 1.4 notification-controller
**Job:** the eventing hub — route **outbound** alerts about Flux events to external systems, and accept **inbound** webhooks to trigger reconciliation. CRDs:
- **Provider** (`v1beta3`) — outbound destination (Slack, Teams, Discord, generic webhook, Git provider commit-status, and 2.8 PR/MR-comment providers `githubpullrequestcomment`/`gitlabmergerequestcomment`/`giteapullrequestcomment`).
- **Alert** (`v1beta3`) — selects `eventSources` (by kind/name) and routes to a `providerRef` with a severity filter.
- **Receiver** (`v1`) — exposes an HTTP webhook endpoint (GitHub/GitLab/generic/etc.) that, on a matched event, annotates referenced objects to force reconciliation. (Receivers replace polling — push instead of pull.)

### 1.5 image-reflector-controller
**Job:** scan container registries and compute the "latest" tag per policy. CRDs (`image.toolkit.fluxcd.io/v1`):
- **ImageRepository** — registry/image to scan on an `interval`; stores tag list in status.
- **ImagePolicy** — picks a tag from a referenced ImageRepository. Policy types: **semver** (range, e.g. `>=1.0.0 <2.0.0`), **numerical** (asc/desc), **alphabetical** (asc/desc), plus `filterTags` (regex `pattern` + optional `extract`) to pre-filter/transform tags.

### 1.6 image-automation-controller
**Job:** write the chosen image tags back into Git. Owns **ImageUpdateAutomation** (`image.toolkit.fluxcd.io/v1`): references a GitRepository (write), an `update.path`, `update.strategy: Setters`, and a `git.commit`/`git.push` spec. Updates YAML at **markers** like `# {"$imagepolicy": "<namespace>:<imagepolicy-name>"}` (or `:tag`/`:name` variants), then commits and pushes. This closes the loop: registry → policy → Git → source-controller → kustomize/helm.

### 1.7 source-watcher (advanced)
Owns **ArtifactGenerator** (`source.watcher.fluxcd.io/v1beta1`) for advanced source composition (combining/transforming artifacts; 2.8 adds Helm chart support). Produces `ExternalArtifact`s.

---

## 2. The reconciliation model

### 2.1 Desired-state-in-Git + continuous reconciliation
Flux is **pull-based**. The desired state lives in Git/OCI; controllers continuously converge the cluster toward it. There is no push from CI. Each object declares an `interval`; the controller re-reconciles at least that often regardless of whether anything changed (self-healing), and additionally on events (source revision change, webhook, manual trigger).

### 2.2 Intervals, retry, jitter
- `spec.interval` — base reconcile cadence (e.g. `10m`). Applied with jitter to avoid thundering herds.
- `spec.retryInterval` (kustomize) — backoff after a failed reconcile (defaults to `interval`).
- `spec.timeout` — bound for build/apply/health-check phases (defaults to `interval`).

### 2.3 Server-side apply (SSA)
kustomize-controller (and helm-controller from 2.8) apply via **server-side apply** with a field manager owned by Flux. Resources are sorted into ordered **stages** — CRDs, then Namespaces, then (Cluster)?-scoped classes, then everything else — so dependencies within a single Kustomization apply correctly. 2.8 adds **custom SSA apply stages** for kustomize-controller.

### 2.4 Drift detection & correction
At each interval the controller compares live cluster state against the desired manifests (SSA dry-run / managed-fields diff). Any divergence ("drift") is **corrected** by re-applying. This is what makes manual `kubectl edit` changes get reverted. For HelmRelease, drift handling is explicit via `spec.driftDetection.mode`:
- `disabled` — no detection
- `warn` — detect + emit events, no correction
- `enabled` — detect AND correct via SSA

### 2.5 Pruning / garbage collection
- `spec.prune: true` (Kustomization) — objects previously applied by this Kustomization but no longer present in the current revision are **deleted**. Tracked via an inventory in status.
- On Kustomization deletion, GC removes all owned objects.
- `spec.deletionPolicy`: `MirrorPrune` (mirror the `prune` setting), `Delete`, or `Orphan` (leave objects behind).
- Opt out per-object with label/annotation `kustomize.toolkit.fluxcd.io/prune: disabled`.

### 2.6 Suspend / resume
`spec.suspend: true` pauses reconciliation for that object — no new revisions applied, **drift correction paused** (drift will accumulate while suspended). CLI: `flux suspend|resume <kind> <name>`. Suspend a source to freeze everything downstream; suspend a Kustomization/HelmRelease to freeze just that app.

### 2.7 Force-reconcile annotation
Manual triggers set `reconcile.fluxcd.io/requestedAt: <RFC3339 timestamp>` on the object (what `flux reconcile` does under the hood). The controller compares it to `status.lastHandledReconcileAt` to fire an out-of-band reconcile. `--with-source` first reconciles the upstream source.

---

## 3. Health checks, readiness, conditions, kstatus

Flux objects follow the **kstatus** convention and standard Kubernetes `status.conditions`:
- **Ready** — `True` = converged successfully; `False` = failed (with a `reason`); `Unknown` = currently reconciling.
- **Reconciling** — present/`True` while work is in progress (in-progress signal).
- **Stalled** — `True` when retries are exhausted / a terminal error means no progress will be made without a change (won't self-recover on interval alone).
- `status.observedGeneration` vs `metadata.generation` — tells you whether the controller has acted on the latest spec.

**Source Ready** is `True` when: an artifact is reported, the artifact exists in storage, the remote was contacted, and the artifact revision matches the latest resolved upstream revision.

**Kustomization health checks:**
- `spec.wait: true` — health-check **all** applied resources via kstatus (ignores `healthChecks` list when set).
- `spec.healthChecks: []` — explicit list of `apiVersion/kind/name/namespace` to gate readiness on. Works for built-in kinds (Deployment, etc.), Flux kinds, and any kstatus-compatible CRD.
- `spec.timeout` bounds the wait.
- Failure reasons on Ready=False include: `ArtifactFailed`, `BuildFailed`, `HealthCheckFailed`, `PruneFailed`, `DependencyNotReady`, `ReconciliationFailed`.

**HelmRelease health checks (2.8):** kstatus-based plus **CEL-based health-check expressions** for custom readiness logic. `CancelHealthCheckOnNewRevision` lets in-flight health checks abort when a new spec/values/source revision arrives — reducing MTTR.

---

## 4. Dependencies & ordering

`spec.dependsOn` (`[]NamespacedObjectReference`) declares that this object must wait until the referenced objects are **Ready** before reconciling. Supported on **Kustomization** and **HelmRelease** (cross-object ordering across the same kind).

- Combine with `spec.wait: true` so a dependency is only considered Ready once its workloads are actually healthy — otherwise `dependsOn` only waits for the apply, not the rollout.
- Use to sequence: CRDs → operators → CRs; infra → platform → apps.
- Reason `DependencyNotReady` is surfaced on the dependent while waiting.
- Within a *single* Kustomization, ordering is handled by SSA stages (CRDs/Namespaces first); `dependsOn` is for *between* objects.

---

## 5. The bootstrap model

`flux bootstrap {github|gitlab|git|...}` makes Flux **self-managed via Git**:

1. **Validation** — pre-flight checks of CLI/cluster (`flux check --pre`).
2. **Manifest generation** — renders controller Deployments, CRDs, RBAC, optional NetworkPolicies, a source secret (deploy key / token), and the sync resources.
3. **Git operations** — commits manifests into the repo (path like `clusters/<name>/flux-system/`) and pushes.
4. **Cluster apply** — applies the manifests to the cluster.
5. **Health check** — waits for all controllers Ready.

**`flux-system` namespace** holds the controllers and the bootstrap objects. The committed files:
- **`gotk-components.yaml`** — all controller Deployments, CRDs, RBAC (the "gitops toolkit components").
- **`gotk-sync.yaml`** — a **GitRepository** pointing at the bootstrap repo/path + a **Kustomization** that applies that path.
- **`kustomization.yaml`** — references the above.

**Self-management loop:** the `flux-system` GitRepository continuously pulls the bootstrap repo; the `flux-system` Kustomization applies `gotk-components.yaml` (and anything else in the path) back onto the cluster. Therefore **upgrading Flux = bumping the manifests in Git** (or `flux bootstrap` again with a newer CLI); the running Kustomization rolls the new controller versions out. Everything else (your apps) is added as more GitRepository/Kustomization/HelmRelease objects under the same repo.

Relevant bootstrap flags: `--components-extra` (enable image controllers), `--watch-all-namespaces`, `--network-policy`, `--cluster-domain`, `--path`, `--default-components`.

---

## 6. The `flux` CLI for build / validate / diff / trace (local + cluster)

| Command | Purpose |
|---|---|
| `flux build kustomization <name> --path ./path` | Locally reproduces what kustomize-controller would build (fetches the Flux Kustomization spec, applies SOPS/substitutions/patches, builds overlays) and prints the rendered multi-doc YAML. Use in CI to validate output before merge. `--kustomization-file` to use a local spec without the cluster. |
| `flux diff kustomization <name> --path ./path` | Server-side **dry-run** diff: builds locally then compares against live cluster state, showing per-object `created/configured/deleted` (drift preview). The standard "what will this change?" gate in PRs. |
| `flux diff artifact` / `flux diff helmrelease` | Diff OCI artifacts / HelmRelease renderings. |
| `flux reconcile <kind> <name> [--with-source]` | Force an immediate reconcile (sets `requestedAt`). `--with-source` reconciles the upstream source first (pull latest Git/OCI before applying). |
| `flux trace <kind> <name>` | Walks the ownership/source chain for a workload: which Kustomization/HelmRelease manages it, from which source, at which revision — invaluable for "where did this object come from?". |
| `flux check [--pre]` | `--pre`: prerequisite/cluster-readiness checks before bootstrap. Without: validates installed controllers + CRD versions are healthy. |
| `flux get <kind> [-A]` | List Flux objects with Ready status/message (`flux get sources git`, `flux get kustomizations -A`, `flux get helmreleases`). |
| `flux suspend|resume <kind> <name>` | Toggle `spec.suspend`. |
| `flux logs`, `flux events`, `flux stats` | Aggregated controller logs / object events / object counts. |
| `flux create|export` | Scaffold/serialize CRs as YAML (GitOps-friendly authoring). |
| `flux migrate` | Rewrite stored CRs to the latest API versions (required before upgrading across EOL-API boundaries, e.g. into 2.8). |

CI pattern: `flux build kustomization` → `kubeconform`/policy lint the output → `flux diff kustomization` against a staging cluster as a merge gate.

---

## 7. Security & multi-tenancy model

### 7.1 RBAC / impersonation
- **`spec.serviceAccountName`** (Kustomization & HelmRelease) — the controller **impersonates** that ServiceAccount for all apply/prune operations. The SA's RBAC (Role/RoleBinding) is the actual authority — this is how you scope a tenant to its own namespace(s) and resource types. Without it, the controller uses its own (cluster-admin-ish) identity.
- **`--default-service-account=<name>`** (controller flag) — forces every object that omits `serviceAccountName` to impersonate `<name>` in its own namespace. Set on a multi-tenant cluster so a tenant **cannot** escalate by leaving the field blank.

### 7.2 Cross-namespace isolation
- **`--no-cross-namespace-refs=true`** (kustomize/helm/notification/image controllers) — forbids `sourceRef`/`dependsOn`/etc. pointing at objects in *other* namespaces. With this on, a tenant's Kustomization can only reference sources in its own namespace → hard tenant boundary.
- Without it, `spec.sourceRef.namespace` can cross namespaces.
- **NetworkPolicies** (from `flux bootstrap --network-policy`) deny ingress to controllers from other namespaces.

### 7.3 Tenant isolation pattern (the standard model)
Per tenant: a dedicated namespace + a ServiceAccount with namespace-scoped RBAC + the tenant's own GitRepository/Kustomization referencing `serviceAccountName`. Platform admin owns the root `flux-system` Kustomization (which the tenant cannot modify) and onboards tenants by adding their Kustomization there with `--default-service-account` and `--no-cross-namespace-refs` enforced cluster-wide. `spec.targetNamespace` can pin all objects in a tenant Kustomization to one namespace.

### 7.4 Remote-cluster / hub-and-spoke
- **`spec.kubeConfig.secretRef`** (Kustomization & HelmRelease) — reconcile onto a **remote** cluster using a kubeconfig stored in a Secret. The controller runs centrally (hub) and applies to spokes. Combine with `serviceAccountName` to also impersonate a SA *on the target cluster*.
- Cloud workload identity: objects can carry a ServiceAccount whose cloud identity the controller assumes for registry/source auth (per-object workload identity), avoiding shared static credentials.

### 7.5 Secrets
SOPS decryption is built into kustomize-controller (`spec.decryption.provider: sops` + `secretRef` to the keys, or cloud KMS via workload identity). Encrypted values live in Git; decryption happens in-cluster at apply time.

---

## 8. CRD examples

### 8.1 GitRepository (source)
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: app-repo
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/app
  ref:
    branch: main            # or tag:, semver:, commit:, name: (refspec)
  secretRef:                # optional: basic auth / bearer / SSH identity+known_hosts
    name: git-credentials
  ignore: |                 # .sourceignore-style excludes
    /docs
```

### 8.2 OCIRepository with Cosign keyless verification
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata: { name: app-oci, namespace: flux-system }
spec:
  interval: 5m
  url: oci://ghcr.io/org/app-config
  ref: { semver: ">=1.0.0" }   # or tag:/digest:
  provider: generic             # aws|azure|gcp for registry auth
  verify:
    provider: cosign
    matchOIDCIdentity:
      - issuer: "^https://token.actions.githubusercontent.com$"
        subject: "^https://github.com/org/app/.github/workflows/.+@refs/tags/v.+$"
```

### 8.3 Kustomization (apply, prune, wait, depends, tenant SA, remote)
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: app, namespace: tenant-a }
spec:
  interval: 10m
  retryInterval: 1m
  timeout: 5m
  sourceRef: { kind: GitRepository, name: app-repo }
  path: ./deploy/overlays/prod
  prune: true
  wait: true                       # kstatus health-check all applied objects
  targetNamespace: tenant-a
  serviceAccountName: tenant-a-deployer   # RBAC scoping / impersonation
  dependsOn:
    - { name: infra, namespace: flux-system }
  healthChecks:                    # ignored when wait: true
    - apiVersion: apps/v1
      kind: Deployment
      name: app
      namespace: tenant-a
  postBuild:
    substitute: { region: "eu-west-2" }
  decryption: { provider: sops, secretRef: { name: sops-age } }
  # kubeConfig: { secretRef: { name: spoke-cluster-kubeconfig } }   # remote apply
```

### 8.4 HelmRelease (chartRef, remediation, drift)
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata: { name: podinfo, namespace: tenant-a }
spec:
  interval: 10m
  chartRef:                        # OCIRepository or HelmChart; OR use spec.chart template
    kind: OCIRepository
    name: podinfo-oci
  serviceAccountName: tenant-a-deployer
  dependsOn:
    - { name: redis }
  driftDetection: { mode: enabled }   # enabled|warn|disabled
  install:
    remediation: { retries: 3 }       # uninstall before retry
  upgrade:
    remediation:
      retries: 3
      strategy: rollback              # rollback (default) | uninstall
      remediateLastFailure: true
  test: { enable: true }
  values: { replicaCount: 2 }
  valuesFrom:
    - { kind: ConfigMap, name: podinfo-values }
```

### 8.5 Image automation chain
```yaml
apiVersion: image.toolkit.fluxcd.io/v1
kind: ImageRepository
metadata: { name: app, namespace: flux-system }
spec: { image: ghcr.io/org/app, interval: 5m }
---
apiVersion: image.toolkit.fluxcd.io/v1
kind: ImagePolicy
metadata: { name: app, namespace: flux-system }
spec:
  imageRepositoryRef: { name: app }
  filterTags: { pattern: '^main-[a-f0-9]+-(?P<ts>[0-9]+)', extract: '$ts' }
  policy: { numerical: { order: asc } }   # or semver: { range: ">=1.0.0" }
---
apiVersion: image.toolkit.fluxcd.io/v1
kind: ImageUpdateAutomation
metadata: { name: app, namespace: flux-system }
spec:
  interval: 30m
  sourceRef: { kind: GitRepository, name: app-repo }
  git:
    commit: { author: { name: fluxbot, email: flux@org } }
    push: { branch: main }
  update: { path: ./deploy, strategy: Setters }
```
YAML marker in the tracked file:
```yaml
image: ghcr.io/org/app:main-abc123 # {"$imagepolicy": "flux-system:app"}
```

### 8.6 Notification (outbound Alert + inbound Receiver)
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata: { name: slack, namespace: flux-system }
spec: { type: slack, channel: alerts, secretRef: { name: slack-url } }
---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata: { name: on-call, namespace: flux-system }
spec:
  providerRef: { name: slack }
  eventSeverity: error
  eventSources:
    - { kind: Kustomization, name: '*' }
---
apiVersion: notification.toolkit.fluxcd.io/v1
kind: Receiver
metadata: { name: github, namespace: flux-system }
spec:
  type: github
  events: [ping, push]
  secretRef: { name: webhook-token }
  resources:
    - { kind: GitRepository, name: app-repo }
```

---

## 9. Design takeaways for building on Flux

- Treat **Git/OCI as the only write path**; never `kubectl apply` into Flux-managed namespaces — drift correction will fight you (or set `prune: disabled` / suspend deliberately).
- Model ordering explicitly with `dependsOn` + `wait: true`; don't rely on luck. Keep CRDs/operators in a separate, earlier Kustomization.
- For multi-tenant: enforce `--default-service-account` + `--no-cross-namespace-refs` cluster-wide, give each tenant a scoped SA, and keep the root Kustomization admin-owned.
- Gate merges with `flux build` + `flux diff` in CI; use `flux trace` for incident triage.
- Pin upgrade discipline: `flux migrate` before crossing EOL-API boundaries (e.g. into 2.8 which drops the v1beta2 source/kustomize and v2beta2 helm APIs).
- Use OCIRepository + Cosign/Notation `verify` for supply-chain integrity; SOPS for secrets-in-Git.

## Sources
- deepwiki: fluxcd/flux2, fluxcd/source-controller, fluxcd/kustomize-controller (queried Jun 2026)
- https://fluxcd.io/flux/ (components, kustomize, helm, image automation, security/multi-tenancy docs)
- https://fluxcd.io/blog/2026/02/flux-v2.8.0/ (Flux 2.8 GA announcement)
- https://github.com/fluxcd/flux2/releases/tag/v2.8.0 (bundled controller versions, K8s support)
