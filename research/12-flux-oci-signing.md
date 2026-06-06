# Flux CD OCI Artifacts, Signing & Supply-Chain

Reference for the "signed, versioned policy artifact + SBOM" pillar. Maps the talk's
thesis — *policy is a dependency, so supply-chain security is not a new problem* — onto
Flux's OCI artifact tooling. Sources: fluxcd.io docs, fluxcd/source-controller (deepwiki),
sigstore/cosign + notaryproject docs, and 2025/2026 web articles (links at bottom).

---

## 1. Why OCI artifacts for policy distribution

The talk's core move: treat a bundle of policy (Kyverno/Gatekeeper/OPA, Kustomize
overlays, Helm values) as a **versioned, immutable dependency** rather than a moving Git
branch. An OCI registry is the natural store:

- **Immutable & content-addressable.** Every push resolves to a `sha256:` digest. A tag
  like `:1.4.2` is a convenience pointer; the digest is the truth. Pinning by digest in
  the `OCIRepository` gives you exactly-once, tamper-evident delivery.
- **Registry as source of truth ("Gitless GitOps").** CI stays driven by Git, but Flux
  reconciles from the registry. The registry gives you replication, geo-distribution,
  retention/GC, RBAC and signature storage that a Git server does not. Git is the *authoring*
  plane; the registry is the *distribution* plane.
- **Semver in the registry.** Tags carry semver; `OCIRepository.spec.ref.semver: ">=1.0.0"`
  lets the cluster track a constraint, exactly like a package manager resolving a dependency.
- **Supply-chain reuse.** Because it is an OCI artifact, *every* container supply-chain tool
  (cosign, notation, syft, Trivy, SLSA generators, admission policies like Kyverno
  `verifyImages`) works unchanged. This is the "not a new problem" point: policy inherits the
  whole image-signing ecosystem for free.

### OCI artifact vs GitRepository as a distribution channel

| Dimension | `GitRepository` | `OCIRepository` (OCI artifact) |
|---|---|---|
| Identity | branch/tag/commit SHA | content digest (`sha256:`) + tag |
| Immutability | tags are movable; branches mutable | artifact is immutable by digest |
| Versioning | git tags / semver on tags | registry tags + `spec.ref.semver` range |
| Provenance | commit history | OCI annotations (`source`, `revision`, `created`) |
| Signing | commit signing (GPG/ssh), not verified by Flux source | cosign **and** notation, **verified by source-controller** |
| Source of truth | Git server | registry (replicated, RBAC, GC) |
| Auth | SSH key / token | docker creds, cloud contextual login, workload identity |
| Built by | humans pushing to Git | CI pipeline (`flux push artifact`) |

Flux only natively verifies **signatures on OCI artifacts**, not Git commit signatures —
a concrete reason the OCI path is stronger for a "trusted policy bundle".

---

## 2. Packaging policy: `flux push artifact`

Flux packages a directory (or a single file, or piped stdin) into an OCI artifact with
these media types:

- manifest: `application/vnd.oci.image.manifest.v1+json`
- config:   `application/vnd.cncf.flux.config.v1+json`
- content:  `application/vnd.cncf.flux.content.v1.tar+gzip`

The tar layer is a gzipped tarball of the manifests/policy.

```bash
flux push artifact oci://ghcr.io/org/policies/baseline:$(git rev-parse --short HEAD) \
  --path="./policies" \
  --source="$(git config --get remote.origin.url)" \
  --revision="$(git branch --show-current)@sha1:$(git rev-parse HEAD)"
```

Output:
```
► pushing artifact to ghcr.io/org/policies/baseline:b3b00fe
✔ artifact successfully pushed to ghcr.io/org/policies/baseline@sha256:4f90664660b3...aed6
```

### Key flags

| Flag | Purpose |
|---|---|
| `--path` | directory **or** single file of manifests; `-f -` / `--path=-` reads stdin |
| `--source` | provenance: source address (Git URL). Stored as OCI annotation. |
| `--revision` | provenance: `<branch\|tag>@sha1:<commit>`. Stored as annotation. |
| `--annotations` | arbitrary `key=value` OCI annotations (e.g. `org.opencontainers.image.licenses=Apache-2.0`) |
| `--creds` | `<username>[:<password>]` registry creds |
| `--provider` | `generic` (default), `aws`, `azure`, `gcp` — contextual cloud login |
| `--output` | `json` / `yaml` (machine-readable result incl. digest, for CI) |
| `--reproducible` | set `created` timestamp to `1970-01-01T00:00:00Z` so the digest is reproducible |
| `--ignore-paths` | `.gitignore`-style excludes |

`--source` and `--revision` are written as OCI annotations and surface in
`OCIRepository.status` when Flux pulls — that is the in-cluster provenance trail tying a
running policy bundle back to a Git commit.

### Reproducible digests

A bit-identical input must produce a bit-identical digest, otherwise signatures churn.
The `created` annotation defeats this. Pin it:

```bash
flux push artifact oci://ghcr.io/org/policies/baseline:1.4.2 \
  --path=./policies \
  --source="$(git config --get remote.origin.url)" \
  --revision="v1.4.2@sha1:$(git rev-parse HEAD)" \
  --reproducible
# or pin the epoch explicitly to the commit time:
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
```

### Piped build (Kustomize/Helm template → artifact)

```bash
kustomize build ./policies | \
flux push artifact oci://ghcr.io/org/policies/baseline:$(git rev-parse --short HEAD) -f - \
  --source="$(git config --get remote.origin.url)" \
  --revision="$(git branch --show-current)@sha1:$(git rev-parse HEAD)" \
  --annotations='org.opencontainers.image.licenses=Apache-2.0'
```

---

## 3. `flux tag / list / pull artifact`

Promote an immutable build-tagged artifact to channel tags (`latest`, `stable`):

```bash
flux tag artifact oci://ghcr.io/org/policies/baseline:$(git rev-parse --short HEAD) \
  --tag latest --tag stable
# ✔ artifact tagged as ghcr.io/org/policies/baseline:latest

flux tag artifact oci://ghcr.io/org/policies/baseline:$(git tag --points-at HEAD) \
  --tag stable
```

List tags in a repo:
```bash
flux list artifacts oci://ghcr.io/org/policies/baseline
```

Pull/unpack to a local dir (inspection, drift checks, debugging):
```bash
flux pull artifact oci://ghcr.io/org/policies/baseline:latest --output=./extracted
```

---

## 4. Consuming the artifact: `OCIRepository`

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: baseline-policies
  namespace: flux-system
spec:
  interval: 5m
  url: oci://ghcr.io/org/policies/baseline   # NO tag/digest in url
  ref:
    semver: ">=1.0.0"        # or tag: latest | digest: sha256:...
    # semverFilter: '.*'     # optional regex pre-filter on tags
  provider: generic          # generic | aws | azure | gcp
  secretRef:
    name: ghcr-auth          # docker-registry secret (omit for cloud/SA auth)
```

`spec.ref` precedence: `digest` > `semver` > `tag` > defaults to `latest`. Pinning a
digest is the strongest guarantee; semver is the "dependency range" pattern.

Wire it to a Kustomization:
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: baseline-policies, namespace: flux-system }
spec:
  interval: 10m
  prune: true
  sourceRef: { kind: OCIRepository, name: baseline-policies }
  path: ./
```

Helm chart variant uses `layerSelector` + `chartRef`:
```yaml
spec:
  url: oci://ghcr.io/org/charts/policy-pack
  ref: { semver: ">=6.9.0" }
  layerSelector:
    mediaType: "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    operation: copy
```

---

## 5. Signing

### 5a. cosign — key-based

```bash
cosign generate-key-pair                       # cosign.key + cosign.pub
cosign sign --key cosign.key \
  ghcr.io/org/policies/baseline@sha256:4f90...  # sign by digest, not tag
```

In-cluster verify — put the public key(s) in a Secret (keys must end `.pub`):
```bash
kubectl -n flux-system create secret generic cosign-pub \
  --from-file=cosign.pub=cosign.pub
```
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata: { name: baseline-policies, namespace: flux-system }
spec:
  interval: 5m
  url: oci://ghcr.io/org/policies/baseline
  ref: { semver: "*" }
  verify:
    provider: cosign
    secretRef:
      name: cosign-pub      # iterates all *.pub keys; any match passes
```

### 5b. cosign — keyless (OIDC / Fulcio / Rekor)

CI (e.g. GitHub Actions with OIDC) signs with no long-lived key:
```bash
COSIGN_EXPERIMENTAL=1 cosign sign \
  ghcr.io/org/policies/baseline@sha256:4f90...
# identity bound to the workflow's OIDC token; cert from Fulcio, logged in Rekor
```

In-cluster verify — omit `secretRef`, constrain the identity with `matchOIDCIdentity`
(regex on the Fulcio cert's issuer/subject). source-controller uses the Fulcio root CA and
`rekor.sigstore.dev`:
```yaml
spec:
  verify:
    provider: cosign
    matchOIDCIdentity:
      - issuer:  "^https://token.actions.githubusercontent.com$"
        subject: "^https://github.com/org/policies.*$"
```
Verification succeeds if **any** matcher matches. This is the strongest model for the
talk: the policy bundle is provably built by a named CI workflow, no key to leak.

### 5c. notation (Notary Project)

```bash
notation sign ghcr.io/org/policies/baseline@sha256:4f90...   # uses configured key/cert
```
In-cluster verify needs CA cert(s) (`.pem`/`.crt`) **and** a `trustpolicy.json` in the
Secret:
```yaml
spec:
  verify:
    provider: notation
    secretRef:
      name: notation-config
---
apiVersion: v1
kind: Secret
metadata: { name: notation-config, namespace: flux-system }
type: Opaque
data:
  ca.crt:           <base64 CA cert>          # .pem or .crt
  trustpolicy.json: <base64 trust policy>     # MUST be named trustpolicy.json
```
Note: notation support was contributed partly by Microsoft; some managed offerings (e.g.
the AKS Flux extension) currently support only cosign.

### Verification outcome (both providers)

source-controller sets a `SourceVerified` condition on the `OCIRepository`:
`status: "True", reason: Succeeded` on pass; `status: "False", reason: VerificationError`
on fail. A failed verification blocks the artifact from being applied. Same `verify`
schema also applies to `HelmChart` pulled from OCI.

---

## 6. SBOM / provenance attestations & SLSA

Because the policy bundle is an OCI artifact, you attach SBOMs and SLSA provenance as
cosign **attestations** (in-toto predicates) keyed to the same digest — identical to
signing a container image.

Generate + attach an SBOM:
```bash
syft ghcr.io/org/policies/baseline@sha256:4f90... -o cyclonedx-json > sbom.cdx.json
cosign attest --key cosign.key --type cyclonedx \
  --predicate sbom.cdx.json \
  ghcr.io/org/policies/baseline@sha256:4f90...
```

Attach SLSA provenance (predicate emitted by the CI/SLSA generator):
```bash
cosign attest --key cosign.key --type slsaprovenance \
  --predicate provenance.json \
  ghcr.io/org/policies/baseline@sha256:4f90...
# keyless equivalent: COSIGN_EXPERIMENTAL=1 cosign attest --type slsaprovenance ...
```
`--type` accepts: `slsaprovenance`, `slsaprovenance02`, `slsaprovenance1`, `spdx`,
`spdxjson`, `cyclonedx`, `vuln`, `openvex`, `link`, or a custom predicate.

Verify attestations:
```bash
cosign verify-attestation --type cyclonedx     --key cosign.pub  ghcr.io/org/policies/baseline:1.4.2
cosign verify-attestation --type slsaprovenance --certificate-identity-regexp '...' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com ghcr.io/org/policies/baseline:1.4.2
```

**Caveat:** Flux's `OCIRepository.spec.verify` checks the **signature** of the artifact,
not the attestations. To gate on SBOM/SLSA attestations in-cluster you pair Flux with an
admission policy (e.g. Kyverno `verifyImages`/attestation rules or a custom check). The
talk's framing — "policy is a dependency, so SBOM/supply-chain is not a new problem" —
lands precisely here: the policy bundle gets the same SBOM + SLSA + signature treatment as
any production image, using the same off-the-shelf tooling.

---

## 7. Registries & authentication

Any OCI-compliant registry works: GHCR, ECR, ACR, GAR/GCR, Docker Hub, Harbor (which adds
replication + signature storage, good for multi-zone signed-artifact distribution),
self-hosted Zot/Distribution.

**Static creds (generic):**
```bash
flux create secret oci ghcr-auth \
  --url=ghcr.io --username=flux --password=${GITHUB_PAT}
# referenced via spec.secretRef.name
```
Equivalent to a standard `kubernetes.io/dockerconfigjson` secret, also usable as
`imagePullSecrets` on a referenced ServiceAccount via `spec.serviceAccountName`.

**Contextual cloud login (no stored creds)** — set `spec.provider` and grant the
controller's identity:

AWS ECR (IRSA):
```yaml
spec: { provider: aws, url: oci://1234.dkr.ecr.us-east-1.amazonaws.com/repo, serviceAccountName: source-controller }
```
```yaml
# flux-system kustomization patch
patches:
  - patch: |
      apiVersion: v1
      kind: ServiceAccount
      metadata:
        name: source-controller
        annotations:
          eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/ROLE_NAME
    target: { kind: ServiceAccount, name: source-controller }
```

Azure ACR (Workload Identity) — annotate the SA with
`azure.workload.identity/client-id` and label both SA and the source-controller
Deployment pod template with `azure.workload.identity/use: "true"`; `spec.provider: azure`.

GCP GAR/GCR (Workload Identity) — annotate SA with
`iam.gke.io/gcp-service-account: SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com`;
`spec.provider: gcp`.

`flux push artifact --provider aws|azure|gcp` uses the same contextual login from CI.

---

## Sources

- Flux OCI cheatsheet — https://fluxcd.io/flux/cheatsheets/oci-artifacts/
- Flux `OCIRepository` reference — https://fluxcd.io/flux/components/source/ocirepositories/
- `flux push artifact` CLI — https://fluxcd.io/flux/cmd/flux_push_artifact/
- source-controller verify internals (deepwiki: fluxcd/source-controller)
- cosign attest / verify-attestation — https://github.com/sigstore/cosign/blob/main/doc/cosign_attest.md , https://github.com/sigstore/cosign/blob/main/doc/cosign_verify-attestation.md
- Sigstore attestation docs — https://docs.sigstore.dev/cosign/verifying/attestation/
- Sign an SBOM with cosign (Chainguard) — https://edu.chainguard.dev/open-source/sigstore/cosign/how-to-sign-an-sbom-with-cosign/
- Creating SBOM attestations w/ syft + sigstore (Anchore) — https://anchore.com/sbom/creating-sbom-attestations-using-syft-and-sigstore/
- Gitless GitOps with Flux + OCI — https://oneuptime.com/blog/post/2026-03-05-gitless-gitops-flux-cd-oci/view
- Harbor as universal OCI hub (signed multi-zone) — https://goharbor.io/blog/harbor-as-universal-oci-hub/
- Secure GitOps with signed OCI artifacts in AKS — https://teknologi.nl/posts/aksfluxociartifacts/
- GitLab: OCI images as source of truth for CD — https://about.gitlab.com/blog/2025/02/19/how-to-use-oci-images-as-the-source-of-truth-for-continuous-delivery/
- RFP: OCI artifacts as sources (fluxcd/flux2 #1705) — https://github.com/fluxcd/flux2/discussions/1705
