# Flux CD `Kustomization` — Resource & Lifecycle Reference

**Scope:** exhaustive reference on the Flux `kustomize-controller` `Kustomization`
CRD and its lifecycle features, with real YAML. Relevance to this repo: replacing
a bash `policy-checker` with native Flux ordering (`dependsOn`), readiness gating
(`wait`/health checks/CEL), version templating (`postBuild`), and shift-left
validation (`flux build` + `flux diff`).

- **API group/version:** `kustomize.toolkit.fluxcd.io/v1` (GA; `v1beta2` deprecated).
- **Controller:** `fluxcd/kustomize-controller`.
- **Sources verified:** DeepWiki (`fluxcd/kustomize-controller`, `fluxcd/flux2`),
  fluxcd.io docs (Kustomization spec, CEL cheatsheet, CLI), Flux v2.5 release notes
  (CEL GA), WebSearch (2025/2026).

---

## 1. Full `Kustomization` spec (annotated)

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: podinfo
  namespace: flux-system
spec:
  # --- Source ---
  sourceRef:                # REQUIRED. GitRepository | OCIRepository | Bucket | ExternalArtifact
    kind: GitRepository
    name: podinfo
    namespace: flux-system  # optional; cross-ns can be disabled cluster-wide
                            #   with --no-cross-namespace-refs=true
  path: "./kustomize"       # optional; dir containing kustomization.yaml (or plain YAML).
                            #   Defaults to source root.

  # --- Timing ---
  interval: 10m             # REQUIRED. Reconcile cadence. Min effective 60s.
                            #   Source revision change / generation bump triggers instantly.
  retryInterval: 2m         # optional. Retry cadence after failure. Defaults to interval.
  timeout: 5m               # optional. Caps build + apply + health-check. Defaults to interval.

  # --- Apply behaviour ---
  prune: true               # REQUIRED. Garbage-collect objects removed from source.
  wait: true                # optional. Health-check ALL applied objects (ignores healthChecks).
  force: false              # optional. Recreate (delete+create) on immutable-field patch failure.
  targetNamespace: default  # optional. Override namespace of every object. Must exist or be in the set.

  # --- Metadata injection ---
  commonMetadata:           # optional. Labels/annotations applied to every object.
    labels:
      environment: prod
    annotations:
      team: platform

  # --- Ordering / gating ---
  dependsOn:                # optional. Wait for other Kustomizations to be Ready first.
    - name: kyverno
      namespace: flux-system

  # --- Health gating ---
  healthChecks:             # optional. Specific objects to wait on (ignored if wait:true).
    - apiVersion: apps/v1
      kind: Deployment
      name: podinfo
      namespace: default
  healthCheckExprs:         # optional (GA in 2.5). CEL health for custom resources.
    - apiVersion: cert-manager.io/v1
      kind: Certificate
      current: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'True')"
      failed:  "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'False')"

  # --- Templating ---
  postBuild:
    substitute:
      cluster_env: "prod"
    substituteFrom:
      - kind: ConfigMap
        name: cluster-vars
        optional: true
      - kind: Secret
        name: cluster-secret-vars

  # --- Secrets ---
  decryption:               # optional. SOPS decryption before apply.
    provider: sops
    secretRef:
      name: sops-age

  # --- Kustomize components ---
  components:
    - ../security
  ignoreMissingComponents: false
```

Default values worth knowing: `retryInterval` → `interval`; `timeout` → `interval`;
`path` → source root; `force`/`wait` → `false`; `ignoreMissingComponents` → `false`.

---

## 2. `dependsOn` — ordering & gating (the install-then-policies-then-apps pattern)

`dependsOn` makes a Kustomization wait until each named Kustomization reports
`Ready=True`. The controller checks the dependency's `Ready` condition; if not
true it **requeues without applying** (the object sits in a "dependency not ready"
state). Circular dependencies stall reconciliation and must be avoided.

This is exactly the chain this repo needs:

```yaml
# 1. Install the policy engine (CRDs + controller)
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: policy-engine, namespace: flux-system }
spec:
  interval: 10m
  prune: true
  wait: true                      # block until Kyverno/Gatekeeper Deployment is healthy
  sourceRef: { kind: GitRepository, name: platform }
  path: ./infra/kyverno
---
# 2. Apply the policies — only after the engine is Ready
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: policies, namespace: flux-system }
spec:
  interval: 10m
  prune: true
  wait: true
  dependsOn:
    - name: policy-engine
  sourceRef: { kind: GitRepository, name: platform }
  path: ./policies
---
# 3. Apply workloads — only after policies are enforced
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: apps, namespace: flux-system }
spec:
  interval: 10m
  prune: true
  wait: true
  dependsOn:
    - name: policies
  sourceRef: { kind: GitRepository, name: platform }
  path: ./apps
```

**Critical nuance:** `dependsOn` only gates *applying*. Without `wait: true` (or
explicit `healthChecks`) on the dependency, "Ready" means "applied successfully",
**not** "the engine's webhook is actually serving". For a policy engine you almost
always want `wait: true` on `policy-engine` so that "Ready" means the admission
webhook pods are healthy before policies (and then apps) are admitted.

### `readyExpr` — CEL-gated dependencies (2.5+)

`dependsOn[].readyExpr` lets you define a custom CEL readiness condition with
`dep` (the dependency object) and `self` (this Kustomization):

```yaml
dependsOn:
  - name: app-backend
    readyExpr: >
      dep.metadata.labels['app/version'] == self.metadata.labels['app/version'] &&
      dep.status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'True')
```

By default `readyExpr` *replaces* the built-in Ready check; enable the
`AdditiveCELDependencyCheck` feature gate to make it *additive* (both must pass).

---

## 3. Health checks, `wait`, and readiness gating

Three mechanisms, evaluated **after apply, before garbage collection**, bounded by
`timeout`:

1. **`wait: true`** — run kstatus health assessment on *every* object the
   Kustomization applied. Simplest and safest; **ignores `healthChecks`**.
2. **`healthChecks`** — wait only on a named list (`NamespacedObjectKindReference`).
   Works for K8s built-ins (Deployment, StatefulSet, DaemonSet, Job…), Flux kinds
   (`HelmRelease`, nested `Kustomization`), and any kstatus-compatible CR.
3. **`healthCheckExprs`** — CEL health logic for CRs whose conditions kstatus does
   not natively understand (see §4).

If health checks fail to pass within `timeout`, the Kustomization goes
`Ready=False` with a `HealthCheckFailed`-style reason, and dependents (via
`dependsOn`) stay gated. This is the GitOps "block until healthy" guarantee.

---

## 4. CEL health checks (`healthCheckExprs`) — GA in Flux 2.5

For custom resources, define expressions evaluated against the object. Three fields,
evaluated in order **`inProgress` → `failed` → `current`**; first to return `true`
decides the state. Default (no expr) is kstatus condition-type inference.

```yaml
spec:
  wait: true            # or list the CRs in healthChecks
  healthCheckExprs:
    # cert-manager ClusterIssuer
    - apiVersion: cert-manager.io/v1
      kind: ClusterIssuer
      current: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'True')"
      failed:  "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'False')"
    # Crossplane Provider
    - apiVersion: pkg.crossplane.io/v1
      kind: Provider
      current: "status.conditions.filter(e, e.type == 'Healthy').all(e, e.status == 'True')"
      failed:  "status.conditions.filter(e, e.type == 'Healthy').all(e, e.status == 'False')"
    # Cluster API Cluster (fleet readiness)
    - apiVersion: cluster.x-k8s.io/v1beta1
      kind: Cluster
      current: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'True')"
      failed:  "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'False')"
```

Pitfalls / tips:
- Referencing a field that doesn't exist → the expr never goes `current`, so the
  Kustomization **hangs until `timeout`**. Guard with the `has(...)` macro.
- Validate expressions in the CEL Playground; Flux maintains a **community health
  check library** of vetted CR expressions (PRs welcome, must include evidence).

---

## 5. Drift detection & correction, server-side apply, field managers, `force`

- **Server-side apply (SSA):** the controller applies via SSA so the API server
  tracks **field ownership** (`managedFields`). Objects are applied in dependency
  stages — **CRDs → Namespaces → cluster/class types → everything else** — to keep
  ordering sane within a single Kustomization.
- **Field manager:** the controller owns fields under a field-manager named after
  itself (`kustomize-controller`). It also actively **migrates/cleans `kubectl`
  managed-fields** (both `Apply` and `Update` operations) and strips deprecated
  Flux labels/annotations so post-`kubectl` edits don't fight Flux.
- **Drift detection & correction:** every `interval` (and on source/generation
  change) the desired state is re-applied. Because of SSA field ownership, any
  out-of-band change to a Flux-owned field is detected as drift and **reverted** on
  the next reconcile. Fields Flux doesn't own are left alone.
- **`force: true`:** when a patch fails due to an **immutable field** change
  (e.g. a Job's `spec.selector`, a Service `clusterIP`), the controller **deletes
  and recreates** the object. Use sparingly/temporarily.
  Per-object override: annotate the resource
  `kustomize.toolkit.fluxcd.io/force: enabled`.

---

## 6. Pruning / garbage collection

- Requires `prune: true`. The controller keeps an **inventory** of objects it has
  applied (stored in the Kustomization status). When a manifest is removed from git
  and a new revision is reconciled, objects in the old inventory but not the new
  desired set are flagged **stale and deleted** during the GC phase.
- **What happens when a resource is removed from git:** on the next reconcile its
  GVK/name/namespace is no longer in the rendered set, so it's pruned from the
  cluster (assuming `prune: true`). If `prune: false`, it's orphaned (left running,
  no longer managed).
- **Exclude an object from pruning** (e.g. a PVC or a one-time bootstrap secret):

```yaml
metadata:
  labels:
    kustomize.toolkit.fluxcd.io/prune: disabled
```

- Deleting the **Kustomization itself** triggers a finalizer that prunes all owned
  objects (unless prune is disabled). For a policy-engine Kustomization this means
  deleting the Kustomization tears down CRDs/policies — order matters.

---

## 7. Post-build variable substitution — templating policy version into manifests

Runs **after** the kustomize build, on the rendered YAML (envsubst-style; supports
bash-like `${var:=default}`, `${var:offset:length}`, `${var/old/new}`).

```yaml
spec:
  postBuild:
    substitute:
      policy_version: "v1.4.2"      # inline (highest precedence)
    substituteFrom:
      - kind: ConfigMap
        name: policy-config
        optional: true
      - kind: Secret
        name: policy-secrets
        optional: false              # default; fails if missing
```

Manifest consuming it:

```yaml
metadata:
  labels:
    policy.example.com/version: "${policy_version}"
```

Notes for the policy-versioning use case:
- Var names must match `^[_[:alpha:]][_[:alpha:][:digit:]]*$`.
- `substituteFrom` entries are merged in order (later overrides earlier); inline
  `substitute` overrides all `substituteFrom`.
- Disable on a specific object: annotate `kustomize.toolkit.fluxcd.io/substitute: disabled`.
- Numbers/bools must be quoted strings; reconstruct quoting with a `${quote}` var.
- Feature gate `StrictPostBuildSubstitutions=true` makes undefined `${var}` a hard
  error (recommended in CI-driven setups to avoid silently empty values).

---

## 8. Decryption (SOPS)

```yaml
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age            # holds the key(s)/cloud creds
    serviceAccountName: sops-identity   # optional, for cloud KMS workload identity
```

- Providers: **age**, **OpenPGP**, and KMS (**AWS**, **Azure**, **GCP**, **Hashicorp Vault**).
- The decryption Secret entries are keyed by suffix/name:
  `*.agekey` (age), `*.asc` (PGP armored keyring), `sops.aws-kms`, `sops.azure-kv`,
  `sops.gcp-kms`, `sops.vault-token`.
- Encrypt **only `data`/`stringData`** so metadata stays mergeable:
  `sops --encrypted-regex '^(data|stringData)$'`.
- Per-object skip: annotate `kustomize.toolkit.fluxcd.io/decrypt: Disabled`.
- Decryption happens in the build phase **before** post-build substitution and apply.

---

## 9. Validation — replacing the bash `policy-checker` with native Flux + shift-left

### In-cluster validation
The controller validates during reconcile primarily through **server-side apply
dry-run**: the API server runs the manifests through schema validation **and
admission webhooks** (so your policy engine's webhook itself validates the apply).
This is the native replacement for an external `policy-checker` — the policy engine
admission webhook is exercised on every apply, and a rejected object fails the
Kustomization. (Note: older `v1beta2` exposed an explicit `spec.validation:
none|client|server`; in `v1` SSA dry-run is the effective mechanism — DeepWiki
found **no `kubeconform` usage inside the controller**; kubeconform is a *CI-side*
tool, see below.)

### Shift-left (local/CI) validation — recommended
`flux build kustomization` renders the **exact** YAML the controller would apply
(same kustomize overlay logic, post-build substitution, components), and
`flux diff kustomization` shows a unified create/update/delete diff vs the live
cluster (or, with `--dry-run` + `--kustomization-file`, fully offline).

```bash
# Render exactly what Flux would apply (offline, for CI)
flux build kustomization policies \
  --path ./policies \
  --kustomization-file ./policies/flux-kustomization.yaml \
  --dry-run > rendered.yaml

# Schema-validate the rendered output (CI policy-checker replacement)
kubeconform -strict -summary -schema-location default rendered.yaml

# Preview what would change against the cluster (PR gate)
flux diff kustomization policies --path ./policies
```

Recommended CI pipeline (PR gate, the shift-left "policy-checker"):
1. `flux build kustomization … --dry-run` → render with substitutions/components.
2. `kubeconform` (and/or `kubectl apply --server-side --dry-run=server`) → schema +
   admission validation.
3. Optionally run the policy engine's own CLI on the rendered YAML
   (e.g. `kyverno apply`, `conftest`, `gator test`) for true policy enforcement
   pre-merge.
4. `flux diff kustomization` for human-readable change preview.

This gives two layers: **CI** (`flux build` + kubeconform + policy CLI) catches
errors pre-merge; **cluster** (SSA dry-run + admission webhook + health checks)
catches anything that slips through, and `dependsOn`/`wait` enforce ordering.

---

## Sources
- DeepWiki — `fluxcd/kustomize-controller` (CRD spec, reconciliation, SSA/field
  managers, pruning, validation phases) and `fluxcd/flux2` (build/diff).
- Flux docs — Kustomization: https://fluxcd.io/flux/components/kustomize/kustomizations/
- Flux docs — CEL health checks cheatsheet: https://fluxcd.io/flux/cheatsheets/cel-healthchecks/
- Flux docs — `flux build kustomization`: https://fluxcd.io/flux/cmd/flux_build_kustomization/
- Flux docs — `flux diff kustomization`: https://fluxcd.io/flux/cmd/flux_diff_kustomization/
- Flux 2.5 GA (CEL GA, readyExpr): https://fluxcd.io/blog/2025/02/flux-v2.5.0/
- RFC-0007/0009 custom health checks (CEL): https://github.com/fluxcd/flux2/tree/main/rfcs/0009-custom-health-checks
