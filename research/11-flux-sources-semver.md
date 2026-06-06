# Flux CD Sources & Semver Version Selection

Exhaustive reference on Flux `source-controller` sources, with focus on **semver version selection** — the mechanism that lets us model "policy as a versioned dependency" and satisfy the many-to-many requirement (different clusters pinning different version ranges of the same policy artifact).

Sources: deepwiki `fluxcd/source-controller`, fluxcd.io docs (v1 API), GitHub `fluxcd/source-controller` spec docs, WebSearch (2025/2026). API group `source.toolkit.fluxcd.io/v1`.

---

## 0. Core mental model

The source-controller turns an **external mutable source** (git history, an OCI registry, a Helm repo, an object store) into an **immutable, content-addressed Artifact** stored in-cluster. Consumers (Kustomization, HelmRelease) never touch the upstream — they consume `.status.artifact`. Version *selection policy* (which tag/version) lives in the source object's `spec.ref`. This is the key: **the version range is declarative, per-object, and reconciled continuously.**

Semver matching across ALL Flux sources uses the **`Masterminds/semver/v3`** library (the same one Helm uses). Selection is always: list candidates -> parse each as semver -> keep those satisfying the constraint -> sort descending -> pick the highest. Reconcile re-runs this every `spec.interval`, so a newly-pushed matching tag is auto-adopted within one interval.

---

## 1. GitRepository

### 1.1 `spec.ref` options & precedence

`GitRepositoryRef` has five mutually-influencing fields. **Precedence, lowest to highest:** `branch` < `tag` < `semver` < `name` < `commit`. The highest set field wins (`commit` can combine with `branch` for shallow-clone validation).

| Field | Meaning | Example |
|---|---|---|
| `branch` | Branch to track (HEAD). Default `master` if nothing set. | `branch: main` |
| `tag` | Exact tag. | `tag: v1.0.0` |
| `semver` | Semver range; selects **highest matching tag**. | `semver: ">=1.0.0 <2.0.0"` |
| `name` | Raw ref name: `refs/heads/...`, `refs/tags/...`, `refs/pull/*/head`, `refs/merge-requests/*/head`. | `name: refs/heads/main` |
| `commit` | Exact commit SHA (highest precedence). | `commit: "363a6a8..."` |

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: policy-bundle
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/acme/policies
  ref:
    semver: ">=1.0.0 <2.0.0"
```

### 1.2 How `spec.ref.semver` works (the linchpin)

1. Controller clones and lists **all tags** in the repo.
2. Each tag is parsed as a semver version (non-semver tags are ignored; a leading `v` is tolerated).
3. Tags satisfying the constraint are collected.
4. Collected versions are **sorted in reverse (descending)**; the **highest** is checked out.
5. The resulting Artifact `revision` is `<tag>@sha1:<commit-sha>`.

**Constraint syntax (Masterminds):**

| Constraint | Matches |
|---|---|
| `*` | highest tag available |
| `1.x` / `1.x.x` | any `1.*.*` |
| `~2.1` | `>=2.1.0 <2.2.0` (tilde: allows patch) |
| `~2.1.3` | `>=2.1.3 <2.2.0` |
| `^2.1.3` | `>=2.1.3 <3.0.0` (caret: allows minor+patch) |
| `>=2.0.0 <3.0.0` | explicit range (space = AND) |
| `1.2.x \|\| >=2.0.0` | OR with `\|\|` |
| `>=1.2.0-0` | range INCLUDING pre-releases (see §6) |

### 1.3 Reconcile behaviour when a new matching tag appears

Every `spec.interval` the controller re-lists tags and re-selects the highest match. If a higher matching tag now exists, it sets `Reconciling=True`, produces a new Artifact (new revision/digest), updates `.status.artifact`, and consumers re-apply. If the highest match is unchanged, it's a no-op (artifact stays). A tag *outside* the range is simply never selected. This is what gives us "auto-adopt patch/minor, never cross the pinned boundary" semantics for free.

### 1.4 `spec.verify` (commit/tag signature verification)

Git verification uses **GPG/PGP** (not cosign on the git object itself — cosign is for OCI). `mode`:
- `HEAD` (default) — verify the commit at the checked-out ref.
- `Tag` — verify the tag object (`spec.ref.tag`/`.semver`/`.name`).
- `TagAndHEAD` — verify both.

```yaml
spec:
  verify:
    mode: TagAndHEAD
    secretRef:
      name: pgp-public-keys
---
apiVersion: v1
kind: Secret
metadata: { name: pgp-public-keys }
type: Opaque
data:
  author1.asc: <BASE64>
```
Success -> condition `SourceVerified=True, reason=Succeeded`. (Note: Flux can *also* verify Flux-CLI-pushed git artifacts, but for OCI-signed supply chains use OCIRepository + cosign — see §2.4.)

---

## 2. OCIRepository

The natural home for "policy as a versioned artifact" — push the policy bundle (OPA/Gatekeeper/Kyverno manifests, Kustomize overlay, etc.) as an OCI artifact with `flux push artifact`, tag it semver, consume it here.

### 2.1 `spec.ref`: tag / semver / semverFilter / digest

Precedence, lowest to highest: `tag` < `semver` (+optional `semverFilter`) < `digest`. Default if nothing set: tag `latest`.

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: policy-bundle
  namespace: flux-system
spec:
  interval: 5m
  url: oci://ghcr.io/acme/policies   # NO tag in url
  ref:
    semver: ">=2.0.0 <3.0.0"
    # semverFilter: ".*-rc.*"   # optional regex pre-filter on tags
```

- `tag: "1.0.0"` — exact tag.
- `semver: ">= 6.1.5"` — highest matching tag (same Masterminds algorithm as git).
- `semverFilter` — a **regex applied to tag strings BEFORE semver evaluation**; only matching tags enter the semver pool (e.g. filter to a release channel).
- `digest: "sha256:<hash>"` — pin to an immutable manifest digest (highest precedence; ignores tags entirely). Can be combined with a tag for a belt-and-braces pin.

### 2.2 Semver tag selection (`getTagBySemver`)

Identical conceptually to git: `remote.List` all tags from the registry -> apply `semverFilter` regex if present -> parse remaining as semver -> filter by constraint -> sort descending -> pick highest. Revision becomes `<tag>@sha256:<digest>`.

### 2.3 How OCI artifacts are pulled, + `layerSelector`

`reconcileSource` authenticates (`spec.provider`: `generic`|`aws`|`azure`|`gcp`; or `secretRef` to a dockerconfigjson secret; or `serviceAccountName` for workload identity), resolves the ref via `getArtifactRef`, fetches the manifest, selects a layer, and stores it.

`spec.layerSelector` picks WHICH layer to materialise (default: first layer):
```yaml
spec:
  layerSelector:
    mediaType: "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    operation: extract   # default: untar into storage
    #operation: copy     # persist the tarball as-is, unaltered
```
`extract` = decompress/untar the layer into the artifact tree (what Kustomization wants). `copy` = store the raw compressed layer blob (useful for opaque bundles, e.g. a signed policy tarball consumed by something else).

`spec.insecure: true` allows plain HTTP registries.

### 2.4 `spec.verify` (cosign / notation)

```yaml
spec:
  verify:
    provider: cosign
    secretRef:
      name: cosign-public-keys   # key(s) for keyed verification
```
Keyless (Fulcio/Rekor) with OIDC identity matching:
```yaml
spec:
  verify:
    provider: cosign
    matchOIDCIdentity:
      - issuer: "^https://token.actions.githubusercontent.com$"
        subject: "^https://github.com/acme/policies.*$"
```
Notation (trust policy + CA cert live in the secret):
```yaml
spec:
  verify:
    provider: notation
    secretRef:
      name: notation-config
```
Success -> `SourceVerified=True`. **This is the supply-chain anchor: a cluster can refuse to adopt any policy version that isn't signed by the policy team's identity, independent of the semver range.**

---

## 3. HelmRepository / HelmChart

If policy ships as a Helm chart, the semver range lives on the **HelmChart** (HelmRelease auto-creates one).

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata: { name: acme, namespace: flux-system }
spec:
  interval: 10m
  url: https://acme.github.io/charts   # or oci:// for OCI Helm
  type: default   # or "oci"
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmChart
metadata: { name: policy, namespace: flux-system }
spec:
  interval: 5m
  chart: policy
  version: ">=1.0.0 <2.0.0"   # fixed, "4.0.x", or any range
  reconcileStrategy: ChartVersion   # default; or "Revision" for git/bucket
  sourceRef:
    kind: HelmRepository
    name: acme
```
`spec.version` is the semver range — same Masterminds semantics; selects the **latest matching chart version** from the repo index. `reconcileStrategy: Revision` (for GitRepository/Bucket-sourced charts) re-packages on any source-revision change even without a chart version bump.

---

## 4. Bucket

Object-store source (S3/GCS/Azure/MinIO). **No semver** — revision is content-derived.

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: Bucket
metadata: { name: policy-bucket, namespace: flux-system }
spec:
  interval: 5m
  provider: generic        # generic | aws | gcp | azure
  bucketName: acme-policies
  endpoint: storage.example.com
  region: us-east-1
  prefix: policies/         # optional server-side key prefix filter
  insecure: false
  timeout: 60s
  secretRef:
    name: bucket-credentials
```
**Revision computation:** the controller lists object keys + their ETags (after default ignore rules / `.sourceignore`), and takes the SHA256 digest of that list as `.status.artifact.revision`. When that digest changes, all objects are re-fetched and archived. Versioning here would have to be encoded in `prefix` paths, which is clumsier than OCI/git semver — **not recommended for the versioned-policy pattern.**

---

## 5. Artifact API, checksums, storage

Every source reports `.status.artifact` — a content-addressed, immutable gzip TAR:

```yaml
status:
  artifact:
    revision: master@sha1:363a6a8fe6a7f13e05d34c163b0ef02a777da20a   # human+content id
    digest: sha256:e750c7a46724acaef8f8aa926259af30bbd9face2ae065ae8896ba5ee5ab832b  # of the tar.gz
    path: gitrepository/flux-system/policy-bundle/363a6a8....tar.gz
    url: http://source-controller.flux-system.svc.cluster.local./gitrepository/flux-system/policy-bundle/363a6a8....tar.gz
    lastUpdateTime: "2022-01-29T06:59:23Z"
    size: 91318
```
- `revision` — semantic id; format differs per source (`<branch|tag>@sha1:<sha>` git, `<tag>@sha256:<digest>` OCI, `sha256:<digest>` bucket).
- `digest` — checksum of the produced `.tar.gz` (algorithm-prefixed; SHA256 default).
- `url` — in-cluster HTTP download; consumers fetch from here, never from upstream.
- Storage = source-controller's PVC + HTTP file server.

Consumers gate on `revision`; the digest provides tamper-evidence end-to-end.

---

## 6. Pre-release handling (gotcha)

Masterminds **excludes pre-release versions** (`1.2.0-rc.1`) from a constraint that has no pre-release comparator. To opt in, add a `-0` suffix to a bound: `semver: ">=1.2.0-0"` (or `">= 6.1.x-0"`). For OCI you can additionally narrow to a channel with `semverFilter: ".*-rc.*"`. This matters for canary/preview policy channels.

---

## 7. THE COEXISTENCE PATTERN (many-to-many requirement)

**Key fact:** a source object is *just declarative data*. There is no global "current version" of a policy — each source object holds its OWN constraint and resolves it independently. So **N clusters (or N namespaces/tenants) can each pin a different semver range of the SAME upstream policy repo/registry simultaneously**, and each tracks its own highest-matching version, reconciled independently. Publishing a new tag fans out only to the objects whose range admits it.

### 7.1 Worked example — two clusters, one OCI policy registry

Upstream `oci://ghcr.io/acme/policies` has tags: `1.4.2`, `1.5.0`, `2.0.0`, `2.1.0`, `2.1.1`, `3.0.0-rc.1`.

**Cluster A (conservative — pinned to v2 line):**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata: { name: policies, namespace: flux-system }
spec:
  interval: 5m
  url: oci://ghcr.io/acme/policies
  ref:
    semver: ">=2.0.0 <3.0.0"     # resolves -> 2.1.1
  verify:
    provider: cosign
    matchOIDCIdentity:
      - issuer: "^https://token.actions.githubusercontent.com$"
        subject: "^https://github.com/acme/policies.*$"
```

**Cluster B (bleeding edge — everything incl. pre-release):**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata: { name: policies, namespace: flux-system }
spec:
  interval: 5m
  url: oci://ghcr.io/acme/policies
  ref:
    semver: ">=0.0.0-0"          # resolves -> 3.0.0-rc.1
  verify:
    provider: cosign
    matchOIDCIdentity:
      - issuer: "^https://token.actions.githubusercontent.com$"
        subject: "^https://github.com/acme/policies.*$"
```

Now `acme` pushes `2.1.2`: Cluster A auto-adopts it within 5m (still `<3.0.0`); Cluster B ignores it (3.0.0-rc.1 is still highest). Push `3.0.0`: A still ignores (boundary holds), B adopts. **No coordination, no central switch — the version policy is per-consumer data.**

### 7.2 Same, with GitRepository (tags `v1.0.0`…`v2.1.0`, `v3.0.0`)

```yaml
# tenant-stable: highest 1.x, never crosses to 2.x
spec: { url: https://github.com/acme/policies, ref: { semver: "1.x" } }       # -> v1.x.y
---
# tenant-current: highest 2.x
spec: { url: https://github.com/acme/policies, ref: { semver: ">=2.0.0 <3.0.0" } }  # -> v2.1.0
---
# tenant-latest: track absolutely everything
spec: { url: https://github.com/acme/policies, ref: { semver: "*" } }          # -> v3.0.0
```

### 7.3 Multiplexing in one cluster

The same coexistence works WITHIN one cluster: create multiple `OCIRepository`/`GitRepository` objects (distinct names/namespaces) each with a different range, then point different `Kustomization`/`HelmRelease` objects at the appropriate source. One cluster can simultaneously run "policy v1 for legacy namespace, v2 for the rest, v3-rc in a canary namespace." This is the direct Flux realisation of policy-as-a-versioned-dependency with many-to-many fan-out.

---

## 8. Mapping back to "policy as a versioned dependency"

- **Artifact = the dependency.** Publish policy as an OCI artifact (preferred) or git tags; semver tag it on release.
- **`spec.ref.semver` = the version constraint** in a consumer's "lockfile" — exactly like `^2.1` in package.json, but continuously re-resolved.
- **Continuous reconcile = automatic patch/minor uptake** within the pinned range; the range boundary is the safety rail against breaking majors.
- **`spec.verify` = signed-dependency enforcement** (cosign keyless tied to the publisher's CI identity).
- **Many-to-many = many source objects, each with its own range**, all reading one upstream — no central version registry needed.
- Bucket is the weak option (no native semver); OCIRepository is the strongest (digest pinning + cosign + semver + layerSelector). GitRepository is the strongest for raw-manifest GitOps where the policy lives as files.

---

### Sources
- deepwiki `fluxcd/source-controller` (semver selection internals, `getTagBySemver`, `getArtifactRef`, layerSelector, verify)
- https://fluxcd.io/flux/components/source/gitrepositories/
- https://fluxcd.io/flux/components/source/ocirepositories/
- https://fluxcd.io/flux/components/source/helmcharts/
- https://fluxcd.io/flux/components/source/buckets/
- https://github.com/fluxcd/source-controller/blob/main/docs/spec/v1/ocirepositories.md
- https://github.com/Masterminds/semver (constraint syntax)
- WebSearch (2025/2026): pre-release `-0` suffix behaviour, semverFilter usage
