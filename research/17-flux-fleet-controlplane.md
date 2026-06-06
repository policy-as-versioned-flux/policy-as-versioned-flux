# Flux CD Fleet / Multi-Cluster Patterns and the ControlPlane Ecosystem

Research note for the "policy-as-versioned-flux" PRD. Focus: how Flux does fleet/multi-cluster, how the ControlPlane Flux Operator templates "N clusters each pinned to a policy version", what ControlPlane's hardened Enterprise distribution adds, and which off-the-shelf features can replace bespoke tooling. Maps directly to the `cluster1`/`cluster2` pin-different-policy-versions scenario in the PRD.

Date: 2026-06-01. Author: research subagent.

---

## 1. Multi-cluster / fleet management with Flux

### 1.1 The two foundational models

**Per-cluster bootstrap (stand-alone)** — each cluster runs its own Flux controllers and reconciles its own path in Git. `flux bootstrap ... --path=clusters/<name>`. ControlPlane's architecture guide calls this "Standalone Mode": each cluster is self-sufficient, giving **reduced attack surface** and **reduced blast radius** (a compromised hub cannot reach other clusters), at the cost of bootstrapping/maintaining each instance separately. This is the safest default for the PRD's policy-distribution use case because each cluster independently chooses what it subscribes to.

**Hub-and-spoke** — one central "hub" cluster runs the Flux controllers and reconciles *into* the spoke clusters by connecting to their Kubernetes API servers (via kubeconfig secrets referenced from `Kustomization.spec.kubeConfig`). Centralises operations but the hub becomes a **single point of failure** for delivery across the fleet and a high-value attack target. For large fleets the hub is scaled horizontally with **sharding**: a primary Flux instance deploys "Flux shard instances" on the hub and distributes reconciliation across them; the bootstrap repo holds the **shard-to-cluster mapping and reconciliation order declaratively**.

Three ControlPlane-named topologies: **Standalone**, **Hub and Spoke**, **Hub Sharding / Horizontal Scaling**.

### 1.2 Standard monorepo structure (`clusters/`, `infrastructure/`, `apps/`)

The canonical Flux layout (from `fluxcd/flux2-kustomize-helm-example` and `fluxcd/flux2-multi-tenancy`):

```
├── clusters/            # per-cluster Flux entrypoints (one dir per cluster)
│   ├── staging/
│   │   ├── infrastructure.yaml   # Flux Kustomization -> ./infrastructure/...
│   │   └── apps.yaml             # Flux Kustomization -> ./apps/staging
│   └── production/
│       ├── infrastructure.yaml
│       └── apps.yaml
├── infrastructure/      # shared cluster services (ingress, cert-manager, policies)
│   ├── controllers/     # Helm-installed controllers (incl. CRDs)
│   └── configs/         # CRs that depend on those CRDs (ClusterIssuer, policies)
└── apps/                # application workloads
    ├── base/            # common HelmRelease + namespace
    ├── staging/         # kustomize overlay/patch
    └── production/      # kustomize overlay/patch
```

Key mechanics relevant to the PRD:

- **Per-cluster subscription**: each cluster's `clusters/<name>/*.yaml` files are Flux `Kustomization` objects whose `path:` points at the environment-specific overlay (e.g. `clusters/staging/apps.yaml` -> `./apps/staging`). Changing the path or the overlay is how a cluster subscribes to *different* config. This is the GitOps equivalent of "cluster1 pins policy v1.2, cluster2 pins policy v2.0".
- **Overlays per environment/cluster**: Kustomize `base/` + per-env patches. `apps/staging/podinfo-patch.yaml` patches the shared `HelmRelease`.
- **Semver version pinning per cluster**: `HelmRelease.spec.chart.spec.version` takes a semver range. The example uses `">=1.0.0-alpha"` (prereleases) in staging and `">=1.0.0"` (stable) in production. **This is the direct analogue for pinning different policy versions per cluster** — cluster1 could carry `version: "1.x"` while cluster2 carries `version: ">=2.0.0"`, or pin exact tags for OCI sources.
- **Dependency ordering**: Flux `dependsOn` enforces infra-before-apps. `infra-configs` dependsOn `infra-controllers` (so cert-manager CRDs exist before `ClusterIssuer`); `apps` dependsOn `infra-configs`. Relevant if policy CRDs (e.g. Kyverno) must land before policies that pin to a version.
- **`.sourceignore`** restricts Flux to watching only `apps/`, `clusters/`, `infrastructure/`.

`flux2-multi-tenancy` adds the **`tenants/`** dir (base + per-env overlays) and the tenant lockdown flags on the controllers: `--no-cross-namespace-refs=true`, `--no-remote-bases=true`, `--default-service-account=default`, plus per-tenant service-account impersonation and RBAC. This is the multi-tenant isolation model platform teams expect.

---

## 2. The Flux Operator (controlplaneio-fluxcd/flux-operator)

A free, open-source Kubernetes operator that replaces the imperative `flux bootstrap` with a **declarative install/configure/upgrade** API, and adds self-service, preview environments, a status page, and AI-assisted operations. Four CRDs (group `fluxcd.controlplane.io/v1`): `FluxInstance`, `FluxReport`, `ResourceSet`, `ResourceSetInputProvider`.

### 2.1 `FluxInstance` — declarative Flux install

Manages the lifecycle of the Flux controllers themselves (replaces bootstrap). Notable fields:

- `spec.distribution.version` (e.g. `"2.x"`), `.registry`, and `.artifact` — an **OCI artifact URL** (`oci://ghcr.io/controlplaneio-fluxcd/flux-operator-manifests:latest`) that the operator polls to pull updated manifests, **enabling CVE patches/hotfixes without an operator upgrade**.
- `spec.distribution.variant` — selects the build: stock upstream, or ControlPlane **`enterprise-distroless`** / **`enterprise-distroless-fips`** (hardened images from `ghcr.io/controlplaneio-fluxcd/distroless`). `imagePullSecret` for private registries.
- `spec.cluster.multitenant: true`, `multitenantWorkloadIdentity`, `tenantDefaultServiceAccount`, `networkPolicy` — turnkey tenant lockdown (the flags `flux2-multi-tenancy` sets by hand).
- `spec.sync` — `kind: GitRepository|OCIRepository`, `url`, `ref`, `path`. The real d2-fleet example syncs from **OCI** (`oci://ghcr.io/controlplaneio-fluxcd/d2-fleet`, `ref: latest-stable`, `path: clusters/prod-eu`) — "Gitless GitOps": clusters reconcile signed OCI artifacts, not a Git checkout, with cosign verification (`matchOIDCIdentity` against the GitHub Actions OIDC issuer).

### 2.2 `ResourceSet` — fleet templating

Lets platform teams define a group of Flux + Kubernetes resources as one templated, parameterised unit. It **iterates a matrix of inputs** and renders `resources`/`resourcesTemplate` once per input set. Inputs come from `spec.inputs` (inline) or `spec.inputsFrom` (from `ResourceSetInputProvider`). Templating uses Go templates with **`<< >>` delimiters** (e.g. `<< inputs.tenant >>`, `<< inputs.tag >>`) to avoid clashing with other `{{ }}` tooling.

This is the mechanism for **"N clusters/tenants each pinned to a different version"**: one `ResourceSet` whose input matrix carries a `version`/`tag` per entry, generating per-entry `OCIRepository` + `Kustomization`/`HelmRelease`/`FluxInstance`.

Real example (d2-fleet `tenants/apps.yaml`, abridged) — one tenant per input, each pinned to a tag, generating namespace + RBAC + signed OCI source + Kustomization:

```yaml
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSet
metadata: { name: apps, namespace: flux-system }
spec:
  inputs:
    - { tenant: "frontend", tag: "${ARTIFACT_TAG}", environment: "${ENVIRONMENT}" }
    - { tenant: "backend",  tag: "${ARTIFACT_TAG}", environment: "${ENVIRONMENT}" }
  resources:
    - apiVersion: source.toolkit.fluxcd.io/v1
      kind: OCIRepository
      metadata: { name: apps, namespace: << inputs.tenant >> }
      spec:
        url: "oci://ghcr.io/controlplaneio-fluxcd/d2-apps/<< inputs.tenant >>"
        ref: { tag: << inputs.tag >> }            # <-- per-input version pin
        verify: { provider: cosign, matchOIDCIdentity: [ ... ] }
    - apiVersion: kustomize.toolkit.fluxcd.io/v1
      kind: Kustomization
      metadata: { name: apps, namespace: << inputs.tenant >> }
      spec:
        sourceRef: { kind: OCIRepository, name: apps }
        path: "./<< inputs.environment >>"         # <-- per-input overlay
```

`spec.dependsOn` (with CEL `readyExpr`) orders ResourceSets/Kustomizations — d2-fleet's `infra` ResourceSet dependsOn the `policies` ResourceSet being Ready (CEL: `status.conditions.filter(e, e.type=='Ready').all(...)`), and `apps` dependsOn `infra-configs`. **Directly relevant**: policies can be made a hard predecessor of apps fleet-wide.

To template **per-cluster pinned versions** specifically, a `ResourceSet` generating `FluxInstance`s (or `OCIRepository`s) keyed off a versions matrix:

```yaml
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSetInputProvider
metadata: { name: policy-versions, namespace: flux-system }
spec:
  type: Static
  defaultValues:
    versions:
      - { cluster: cluster1, policyTag: "1.4.2" }
      - { cluster: cluster2, policyTag: "2.0.1" }
---
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSet
metadata: { name: fleet-policies, namespace: flux-system }
spec:
  inputsFrom:
    - { kind: ResourceSetInputProvider, name: policy-versions }
  resources:
    - apiVersion: source.toolkit.fluxcd.io/v1
      kind: OCIRepository
      metadata: { name: policy, namespace: flux-system }
      spec:
        url: "oci://registry/policies"
        ref: { tag: << inputs.policyTag >> }       # cluster1->1.4.2, cluster2->2.0.1
```

### 2.3 `ResourceSetInputProvider` (RSIP) — dynamic inputs

Polls an external source, filters, and exports rows into `status.exportedInputs` for a `ResourceSet` to consume. Types:

- **Git providers**: `GitHubPullRequest`, `GitHubBranch`, `GitHubTag` (and GitLab MR, Gitea, Azure DevOps equivalents).
  - PRs export `id` (PR number), `sha`, `branch`, `author`, `title`; filter by **labels** (e.g. `deploy/flux-preview`) — used to build **ephemeral preview environments per PR** (Flux Operator v0.14+), torn down on merge.
  - Tags export `id`, `tag`, `sha`; **filterable by semver range** — list a repo's tags, keep those matching a range, emit one input row per tag. This is exactly the primitive for "watch policy releases and roll them out".
- **OCI artifact tags**: `OCIArtifactTag` (generic), `ACRArtifactTag`, `ECRArtifactTag`, `GARArtifactTag` — export `id`, `tag`, `digest`; semver-filterable.
- **Static**: `spec.defaultValues` inline map.

---

## 3. ControlPlane "Enterprise for Flux CD" (hardened distribution)

ControlPlane employs/funds the core Flux maintainers and ships a hardened, supported distribution (`control-plane.io/enterprise-for-flux-cd`, `fluxcd.control-plane.io`). What it adds over upstream:

- **FIPS compliance**: "FIPS 140-3 compliant hardened distroless images"; Flux controller binaries built in FIPS 140-3 mode with the Go runtime restricting TLS to FIPS-approved settings; also described as "FIPS 140-2 validated BoringSSL builds." Selected via `FluxInstance` variant `enterprise-distroless-fips`.
- **Hardened distroless containers**: Google-Distroless-based images for all GitOps Toolkit controllers; access to "Enterprise Image Repositories" (HA, OCI-compliant, secure mirrors) for air-gapped/private pulls.
- **CVE management / SLAs**: "Zero CVEs for last 3 Flux CD versions with continuous scanning"; continuous scanning + **backported security fixes to n-1 and n-2**; **full SBOM** traceability per release; SLA-bound patch + security bulletin (CVE details + fixed image digests) for proven-exploitable vulns.
- **n-2 version support**: hardened/patched builds for the current Flux minor plus the two previous minors; extended K8s compatibility (last 6 K8s releases, last 4 OpenShift releases); 12 months support for Kubernetes LTS.
- **Support tiers / SLAs**: 24/7 on-call with guaranteed response SLAs; tiers sized at 1 / 10 / 25 / 100+ clusters; global teams (NA, EMEA, APAC).
- **Platform coverage**: OpenShift, EKS, AKS, GKE. Available via **AWS Marketplace** and the **UK G-Cloud Digital Marketplace** (relevant for CNS's UK public-sector context).
- **Compliance posture**: "EU Cyber Resilience Act compliance-ready from day one."
- Bundles the **Flux Operator** with "AI-assisted GitOps capabilities."

---

## 4. Ecosystem features that could replace bespoke tooling

- **MCP server for Flux** (`cmd/mcp` in flux-operator, image `flux-operator-mcp`): connects AI assistants to clusters for GitOps debugging/RCA, config comparison, dependency visualisation, and issuing Flux operations conversationally. Tools incl. `install_flux_instance`, `get_flux_instance`, `get_kubernetes_resources`, `get_kubernetes_logs`. Deployable as a Deployment, HTTP/SSE transport. Could replace bespoke "explain why this policy version didn't roll out" scripts.
- **RSIP GitHub PR/tag/OCI providers** replace bespoke CI glue: ephemeral preview envs per labelled PR, and **semver-filtered tag/OCI watchers** replace custom "poll for new release and bump the manifest" automation — the operator does list+filter+template natively.
- **ResourceSet matrices** replace per-cluster copy-paste / scripted manifest generation for fleets.
- **FluxInstance OCI artifact sync** delivers CVE patches without re-bootstrapping (replaces patch-and-redeploy pipelines).
- **`flux-operator-mcp` + FluxReport** give a status page / aggregated health view, replacing bespoke dashboards.

---

## 5. Reference repo structures to borrow for the PRD layout

- **`controlplaneio-fluxcd/d2-fleet`** — *the most directly relevant.* Hub fleet repo with "Gitless GitOps" (OCI + cosign-verified sync). Structure:
  ```
  clusters/{prod-eu,prod-us,staging}/flux-system/{flux-operator.yaml,flux-instance.yaml,flux-operator-values.yaml,kustomization.yaml,runtime-info.yaml}
  clusters/{...}/tenants.yaml
  clusters/update/{automation.yaml,flux-system/...}
  tenants/{apps.yaml,infra.yaml,policies.yaml}   # ResourceSets, << >> templated
  terraform/{main.tf,...}                         # cluster provisioning
  ```
  Each cluster's `flux-instance.yaml` pins `distribution.version` and syncs its own `path: clusters/<cluster>` from a signed OCI artifact at `ref: latest-stable`. Tenants (`apps`/`infra`/`policies`) are `ResourceSet`s with `dependsOn` ordering (`policies` -> `infra` -> `apps`). **This is the template to borrow for "cluster1/cluster2 pinning different policy versions."**
- **`fluxcd/flux2-kustomize-helm-example`** — canonical `clusters/`+`infrastructure/`+`apps/` monorepo with per-env Helm semver pinning and `dependsOn`.
- **`fluxcd/flux2-multi-tenancy`** — adds `tenants/` + controller lockdown flags + RBAC/impersonation for the multi-tenant isolation story.

### Recommendation for the PRD

Adopt the **d2-fleet shape**: one `clusters/<name>/flux-system/flux-instance.yaml` per cluster (each pinning its own policy version via OCI tag or semver range), with a `policies` `ResourceSet` templated from a versions matrix or an `OCIArtifactTag`/`GitHubTag` `ResourceSetInputProvider`. Pin via `OCIRepository.ref.tag` per input (`<< inputs.policyTag >>`) so cluster1 and cluster2 trivially carry different policy versions. Use ControlPlane Enterprise `enterprise-distroless-fips` variant + OCI artifact sync for hardening and CVE patching, and the Flux MCP server for AI-assisted troubleshooting — replacing bespoke version-rollout and dashboard tooling.

---

## Sources
- DeepWiki: controlplaneio-fluxcd/flux-operator; fluxcd/flux2-multi-tenancy; fluxcd/flux2-kustomize-helm-example
- control-plane.io/enterprise-for-flux-cd/ ; fluxcd.control-plane.io (distribution, security, architecture guides)
- fluxoperator.dev/docs (ResourceSet, ResourceSetInputProvider, GitHub PRs, GitLab MRs)
- fluxcd.io (multi-cluster config, repository-structure guide, 2025/07 time-based-deployments blog)
- GitHub: controlplaneio-fluxcd/d2-fleet (file tree + flux-instance.yaml, tenants/apps.yaml, tenants/infra.yaml fetched via gh API)
- AWS Marketplace + UK G-Cloud Digital Marketplace listings for ControlPlane Enterprise for Flux CD
