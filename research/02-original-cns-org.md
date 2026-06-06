# Research 02 — Original CNS Org: `policy-as-versioned-code`

> Exhaustive dissection of Chris Nesbitt-Smith's **original** "Policy as Versioned Code" proof-of-concept GitHub org.
> Source: <https://github.com/policy-as-versioned-code> (all repos public, archived). Cloned to `/tmp/pavc-cns/<name>`.
> Supporting code for a [talk](https://talks.cns.me). All repos MIT, © 2022 Chris Nesbitt-Smith.

This is the **predecessor** to `example-policy-org`. The crux for any Flux redesign is the **many-to-many multi-version coexistence** mechanism demonstrated by `cluster1`/`cluster2` — multiple policy versions installed side-by-side on a *single* Kubernetes cluster, each evaluating only the workloads pinned to it. That mechanism is documented with full fidelity below.

---

## 0. Repo inventory

| Repo | Description | Notable |
|---|---|---|
| `policy` | Company Policy codified into Kyverno + Checkov | **Versioned by git tag** (1.0.0, 2.0.0, 2.1.0, 2.1.1); 4 GitHub Releases |
| `policy-checker` | Docker/bash compliance checker, local + CI | Hardcoded to this org; image `ghcr.io/policy-as-versioned-code/policy-checker` |
| `cluster1` | **All** policy versions co-existing on one cluster | KiND CI; installs 1.0.0 + 2.0.0 + 2.1.0 + 2.1.1 + app1/2/3 |
| `cluster2` | **`>=2.0.0`** policy versions co-existing on one cluster | KiND CI; installs 2.0.0 + 2.1.0 + 2.1.1 + app2/3 (no app1) |
| `app1` | Kubernetes app, compliant with **1.0.0 only** | kustomize, pins `policy-version: "1.0.0"` |
| `app2` | Kubernetes app, compliant with **2.0.0** | kustomize, pins `2.0.0` |
| `app3` | Kubernetes app, compliant with **2.1.1** | kustomize, pins `2.1.1` |
| `infra1` | Terraform, compliant with **1.0.0 only** | tf var pins `1.0.0` |
| `infra2` | Terraform, compliant with **2.0.0** | tf var pins `2.0.0` |
| `infra3` | Terraform, compliant with **2.1.1** | tf var pins `2.1.1` |
| `.github` | Org profile, repo-config, dependency graph | `repos.dot` gravizo diagram |

No tags/releases exist on any repo **except `policy`**. The `policy-checker` image is versioned by CI (sha/edge/semver) but has no git tags/releases.

---

## 1. THE CRUX — Multi-version coexistence on a single cluster

### 1.1 The core trick (two kustomize transformers in the `policy` repo)

Every version tag of `policy/kubernetes/kyverno/kustomization.yaml` applies **two** transformers that together make N versions coexist without collision:

`policy` @ `2.1.1` — `kubernetes/kyverno/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

nameSuffix: "-2.1.1"                       # (1) renames every resource → avoids name collisions

commonLabels:
  mycompany.com/policy-version: "2.1.1"    # (2) stamps a version label on the ClusterPolicy AND
                                           #     (via Kyverno match selector) scopes WHICH workloads it judges

resources:
  - require-department-label/policy.yaml
  - require-known-department-label/policy.yaml
```

Two independent collision-avoidance/scoping mechanisms work in tandem:

1. **`nameSuffix: "-<version>"`** — kustomize renames the cluster-scoped `ClusterPolicy` objects. So `require-department-label` becomes `require-department-label-2.1.1`, `require-department-label-2.0.0`, etc. Without this, four installs of a same-named `ClusterPolicy` would clobber each other (last-write-wins). This is what lets all four versions physically exist as distinct objects in one cluster.

2. **`commonLabels.mycompany.com/policy-version: "<version>"`** — kustomize stamps this label on the `ClusterPolicy` metadata. **Crucially**, the *body* of each policy's Kyverno `match` block ALSO selects on that exact label value (see below). So a `ClusterPolicy` of version 2.1.1 only matches/admits workloads carrying `mycompany.com/policy-version: "2.1.1"`. Each version judges only its own opted-in workloads.

### 1.2 How the policy body self-scopes by version

Inside each policy (e.g. `require-department-label/policy.yaml` @ 2.1.1):
```yaml
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: require-department-label
    exclude:
      any:
      - resources: { namespaces: [kube-system] }
      - resources: { namespaceSelector: { matchLabels: { "mycompany.com/require-department-label": exempt } } }
      - resources: { selector:          { matchLabels: { "mycompany.com/require-department-label": exempt } } }
    match:
      all:
      - resources:
          namespaces: ["*?"]          # any non-empty namespace
          kinds: ["*"]
          selector:
            matchLabels:
              mycompany.com/policy-version: "2.1.1"   # ← ONLY judges workloads carrying THIS version label
    validate:
      message: "The label `mycompany.com/department` is required."
      pattern:
        metadata:
          labels:
            "mycompany.com/department": "?*"
```

So the **coexistence contract** is:
- A workload opts into a policy version by carrying `mycompany.com/policy-version: "<v>"`.
- Only the `ClusterPolicy` set whose `match.selector` equals `<v>` evaluates it.
- All other installed versions ignore that workload (selector miss).
- `nameSuffix` keeps the N `ClusterPolicy` objects from colliding in the cluster-scoped namespace.

This is **opt-in, label-gated, per-workload version selection** — a many-to-many where one cluster hosts many policy versions and many apps each bind to exactly one.

### 1.3 Per-version evolution of the policy (full fidelity)

| Tag | `nameSuffix` / version label | Policies present | `require-known-department-label` allowed values | Note |
|---|---|---|---|---|
| `1.0.0` | `-1.0.0` | `require-department-label` **only** | n/a (policy absent) | Only requires the label exists |
| `2.0.0` | `-2.0.0` | both | `tech\|acounts\|servicedesk\|hr` | **typo**: `acounts` (one 'c'), no `sales` |
| `2.1.0` | `-2.1.0` | both | `tech\|accounts\|servicedesk\|hr` | typo fixed (patch-style change, but minor bump) |
| `2.1.1` | `-2.1.1` | both | `tech\|accounts\|servicedesk\|hr\|sales` | adds `sales` |

The `require-department-label` policy body is **identical across all four tags** except for the version string in `nameSuffix`/`commonLabels`/`match.selector`. Only `require-known-department-label`'s allowed-value enum evolved.

The Checkov equivalents (`infra/checkov/require-known-department-label/policy.yaml` at HEAD/2.1.1) allow `tech, hr, accounts, servicedesk, sales` — note Checkov uses an `or` of five `equals` conditions rather than a regex alternation.

### 1.4 `cluster1` — accepts ALL versions

`cluster1/README.md` (demo transcript) and `cluster1/.github/workflows/ci.yaml` install **all four** versions side-by-side using kustomize remote refs:

```bash
kubectl apply -k "github.com/policy-as-versioned-code/policy/kubernetes/kyverno?ref=1.0.0"
kubectl apply -k "github.com/policy-as-versioned-code/policy/kubernetes/kyverno?ref=2.0.0"
kubectl apply -k "github.com/policy-as-versioned-code/policy/kubernetes/kyverno?ref=2.1.0"
kubectl apply -k "github.com/policy-as-versioned-code/policy/kubernetes/kyverno?ref=2.1.1"
```
Resulting cluster objects (from README):
```
clusterpolicy.kyverno.io/require-department-label-1.0.0 created
clusterpolicy.kyverno.io/require-department-label-2.0.0 created
clusterpolicy.kyverno.io/require-known-department-label-2.0.0 created
clusterpolicy.kyverno.io/require-department-label-2.1.0 created
clusterpolicy.kyverno.io/require-known-department-label-2.1.0 created
clusterpolicy.kyverno.io/require-department-label-2.1.1 created
clusterpolicy.kyverno.io/require-known-department-label-2.1.1 created
```
Then **all three apps** (app1@1.0.0, app2@2.0.0, app3@2.1.1) deploy and pass. The `nameSuffix` is exactly what makes `require-department-label-1.0.0` and `require-department-label-2.1.1` non-colliding sibling objects.

Full `cluster1/.github/workflows/ci.yaml` flow:
1. `actions/checkout@2541b1...` (v3.0.2, SHA-pinned)
2. `container-tools/kind-action@fdfd7e...` (v1.7.0) — spins KiND
3. Install Kyverno: `kubectl apply --wait -k github.com/kyverno/kyverno/config`
4. `sleep 5` + `kubectl wait ... -n kyverno deployment/kyverno`
5. Apply all four policy versions (above)
6. **Wait for readiness** by polling `status.ready` jsonpath:
   - 1.0.0 expects `"true"` (one policy)
   - 2.0.0 / 2.1.0 / 2.1.1 each expect `"true true"` (two policies)
7. Deploy app1, app2, app3
8. `kubectl wait --for=condition=available --timeout=600s deployment/app1 deployment/app2 deployment/app3`

The readiness gate is itself a proof the multi-version install reconciled before workloads land.

### 1.5 `cluster2` — accepts `>=2.0.0`

Identical structure to cluster1 but **omits 1.0.0** and **omits app1**:
- Installs policy 2.0.0, 2.1.0, 2.1.1.
- Deploys app2 (2.0.0) and app3 (2.1.1) only.
- Readiness loop only checks the three `>=2.0.0` versions (each `"true true"`).
- Demonstrates a cluster that has **dropped support** for the old 1.0.0 contract: an app1 (pinned 1.0.0) deployed here would carry `policy-version: "1.0.0"`, which no installed `ClusterPolicy` selects → it would be **unguarded** (admitted with no enforcement), illustrating the lifecycle risk of retiring a version while apps still pin it. (README's final echo lines erroneously print "app1 condition met" — a copy-paste artefact; app1 is not deployed in cluster2.)

### 1.6 Why this matters for a Flux design

- Coexistence relies on **`kustomize?ref=<tag>` remote bases** + **`nameSuffix`** + **a self-referential version label**. There is **no Helm, no namespace-per-version** — all `ClusterPolicy` objects are cluster-scoped and disambiguated purely by name suffix.
- For Flux: this maps cleanly to N `Kustomization`/`OCIRepository`/`GitRepository` sources each pinned to a different `ref`/`tag`, or a single Kustomization listing multiple remote bases. The label-gated selector means Flux does **not** need to namespace or isolate versions — collision avoidance is entirely in `nameSuffix`, and scoping is in the workload label. A Flux redesign must preserve: (a) per-version `nameSuffix`, (b) the `commonLabels` version stamp, (c) the in-policy `match.selector` on that same label. Retiring a version (cluster2 dropping 1.0.0) is just removing a source — but leaves pinned apps silently unguarded, which a Flux design should detect (e.g. an "orphaned version label" guard policy).

---

## 2. `policy` repo (versioned policy source)

- `README.md` "Policy as \[versioned\] code" — Kyverno for k8s, Checkov for Terraform IaaC. Stresses **immutable refs (git-sha)** when inheriting external policies for determinism.
- `requirements.txt`: `checkov==3.2.485` (HEAD; note `policy-checker` pins the older `2.1.242`).
- **Releases** (4): `1.0.0` (2022-05-12, "Initial Policy Release"), `2.0.0`, `2.1.0`, `2.1.1` (Latest). Tags exist both bare (`1.0.0`) and `v`-prefixed (`v1.0.0`) — 8 tags total. The `?ref=` / `--branch` consumers use the **bare** form.

### 2.1 Kyverno tests
Each policy dir has a `test.yaml` (Kyverno CLI test spec) + fixtures named `fail0/pass0/skip0/skip1`.
- `require-department-label`: fail0 (no dept label) → fail; pass0 (`department: finance`) → pass; skip0 (`require-department-label: exempt`) → skip; skip1 (in `kube-system`) → skip. **All fixtures carry `mycompany.com/policy-version: "2.1.1"`** so the match selector fires.
- `require-known-department-label`: fail0 (`department: nothr`) → fail; pass0 `hr`, pass1 `accounts`, pass2 `sales` → pass; skip0 (exempt) & skip1 (kube-system) → skip.

### 2.2 Checkov policies (YAML custom policies)
- `infra/checkov/config.yaml`:
  ```yaml
  framework: [terraform]
  external-checks-dir: ../policy/infra/checkov/
  run-all-external-checks: true
  check: [CUSTOM_*]
  ```
- `require-department-label/policy.yaml` → `id: CUSTOM_AWS_1`, attribute `tags.mycompany.com.department` `exists`, scope `aws`, `resource_types: all`.
- `require-known-department-label/policy.yaml` → `id: CUSTOM_AWS_2`, `or` of five `equals` (tech/hr/accounts/servicedesk/sales).
- Fixtures: `pass*.tf` / `fail*.tf` (S3 bucket ± `aws_ami`). Note tag key written as `mycompany.com.department` (HCL dotted key, mirrors the k8s label after `/`→`.`).

### 2.3 Checkov tests — BATS
`infra/checkov/test.bats`: a **single `@test "checkov"`** that loops every `*/` policy dir, runs `checkov` on each `pass*.tf` (must exit 0) and each `fail*.tf` (must exit non-zero via `!`). Comment explains BATS lacks dynamic test definitions (links bats-core issue #306) — a known limitation, so all cases collapse into one test.

### 2.4 CI — `policy/.github/workflows/ci.yaml`
Two jobs on push/PR to `main`:
- **kyverno**: checkout (`08c6903...` v5.0.0) → download Kyverno CLI **v1.6.2** (raw GitHub release tarball) → `kyverno test kubernetes/kyverno`.
- **checkov**: checkout → `pip install -r requirements.txt` → `mig4/setup-bats@af9a00...` (bats 1.6.0) → `bats infra/checkov/test.bats`.

There is **no release-signing in the `policy` repo** — releases are plain git tags. Signing (cosign) exists only in `policy-checker`.

---

## 3. `policy-checker` (the Docker/bash checker)

`README.md` — runs locally + in CI to decide if a repo is compliant. Version detection:
- **Kubernetes**: reads `kustomization.yaml` → `commonLabels['mycompany.com/policy-version']`.
- **Terraform**: reads the `default` value of the `mycompany.com/policy-version` variable.
- If `.tf` files present → check Terraform; if `kustomization.yaml` present → check Kubernetes (both can run).
- **Explicit limitations** (verbatim spirit): policy location is **hardcoded** to `policy-as-versioned-code/policy`; to be reusable it would need private-repo auth, a much smaller image, policy caching (not re-cloned every run), and a faster-than-Docker local story.

### 3.1 `Dockerfile`
```dockerfile
FROM ghcr.io/kyverno/kyverno-cli:1.8-dev-latest@sha256:496d1a3c... as kyverno-cli
FROM alpine/k8s:1.22.6@sha256:00ac10bc...
RUN apk add --no-cache yq python3 python3-dev alpine-sdk libffi-dev py3-wheel go
RUN GO11MODULE=on go get github.com/tmccombs/hcl2json
COPY requirements.txt ./ ; RUN pip install -r requirements.txt
COPY --from=kyverno-cli /kyverno /usr/local/bin/kyverno
COPY run.sh /usr/local/bin/run.sh
ENV POLICY_VERSION=0.0.0
CMD run.sh
```
- `requirements.txt`: `checkov==2.1.242` (older than `policy` repo's 3.2.485 — a drift).
- **Bugs/limitations**: installs `hcl2json` but `run.sh` calls `hcl2tojson` (binary-name mismatch — Terraform path is effectively broken as written); `go get` is deprecated; image is large (full `alpine/k8s` + go toolchain).

### 3.2 `run.sh` (full behaviour)
```bash
set -e
git config --global advice.detachedHead false

# --- Kubernetes path ---
if test -f "kustomization.yaml"; then
  FETCHED_POLICY_VERSION=$(yq eval '.commonLabels["mycompany.com/policy-version"]' kustomization.yaml)
  POLICY_VERSION="${FETCHED_POLICY_VERSION:=$POLICY_VERSION}"          # falls back to env (0.0.0)
  git clone --quiet --depth 1 --branch ${POLICY_VERSION} https://github.com/policy-as-versioned-code/policy.git /policy
  kubectl kustomize . | kyverno apply /policy/kubernetes/kyverno/*/policy.yaml --resource -
fi

# --- Terraform path ---
if compgen -G "./*.tf" > /dev/null; then
  mkdir /tmp/tf ; cp -r * /tmp/tf
  hcl2tojson -s /tmp/tf /tmp/hcl2tojson                                # <- mismatched binary name
  FETCHED_POLICY_VERSION=$(jq -n '[inputs]' /tmp/hcl2tojson/*.json | jq -r 'map(select(.variable))[].variable|map(select(.["mycompany.com/policy-version"]))[0]["mycompany.com/policy-version"].default[0]')
  POLICY_VERSION="${FETCHED_POLICY_VERSION:=$POLICY_VERSION}"
  git clone --quiet --depth 1 --branch ${POLICY_VERSION} ... /policy
  checkov --external-checks-dir /policy/infra/checkov --config-file /policy/infra/checkov/config.yaml --directory .
fi
```
Key insight: the checker **clones the policy repo at the exact tag the consumer declares** (`--branch ${POLICY_VERSION}`), then runs that version's policies against the rendered manifest/HCL. The version pin in the consumer repo is the single source of truth.

### 3.3 CI — `policy-checker/.github/workflows/ci.yaml`
- **build** job: login ghcr → `docker/metadata-action` (tags: `sha,format=long`; `edge` on default branch; `semver {{version}}` and `{{major}}.{{minor}}`; `latest=true`) → buildx → `docker/build-push-action` (push only on non-PR). amd64 only (arm64/amd64 line commented out). All actions SHA-pinned. Tight least-privilege `permissions` (only `packages: write`).
- **sign** job (non-PR): `sigstore/cosign-installer@9becc6...` (v2.8.1) → `cosign sign ${TAGS}` with `COSIGN_EXPERIMENTAL: 1` (keyless OIDC, `id-token: write`). **This is the only signing in the whole org**, and it signs the checker *image*, not the policy releases.

---

## 4. Consumers — apps & infra (version-pinning + renovate + CI)

### 4.1 Version dependency table

| Repo | Type | Pin location | Pinned version | Dept value | Compliant-with (per `repos.dot`) | Not-compliant-with |
|---|---|---|---|---|---|---|
| `app1` | k8s/kustomize | `kustomization.yaml` `commonLabels` | `1.0.0` | finance | 1.0.0 (green) | 2.0.0/2.1.0/2.1.1 (red) |
| `app2` | k8s/kustomize | `kustomization.yaml` `commonLabels` | `2.0.0` | hr | 2.0.0 (green) | 2.1.0/2.1.1 (orange) |
| `app3` | k8s/kustomize | `kustomization.yaml` `commonLabels` | `2.1.1` | sales | 2.1.1 (green) | — |
| `infra1` | terraform | `variable.tf` var default | `1.0.0` | finance | 1.0.0 (green) | 2.x (red) |
| `infra2` | terraform | `variable.tf` var default | `2.0.0` | hr | 2.0.0 (green) | 2.1.x (orange) |
| `infra3` | terraform | `variable.tf` var default | `2.1.1` | sales | 2.1.1 (green) | — |

(Note: org repo *descriptions* for app2/infra2 say "Depends on version 2.0.0 compliant with 2.1.1" — slightly garbled labels; the actual pins are 2.0.0. `repos.dot` is the authoritative dependency model. "orange" = compliant-but-could-upgrade; "red" = would fail.)

### 4.2 Pinning mechanisms
- **Apps** (`app*/kustomization.yaml`):
  ```yaml
  commonLabels:
    mycompany.com/policy-version: "1.0.0"   # the single pin
  resources: [deployment.yaml]
  ```
  `deployment.yaml` is an `nginx` Deployment carrying `mycompany.com/department: <finance|hr|sales>` on both the Deployment and pod template. The `commonLabels` propagate the version label onto the pod, which is what the cluster's matching `ClusterPolicy` selects.
- **Infra** (`infra*/variable.tf`):
  ```hcl
  variable "mycompany.com/policy-version" {
    type    = string
  # renovate: policy
    default = "2.1.1"
  }
  ```
  `main.tf` is a single `aws_s3_bucket` with `tags = { mycompany.com.department = "<dept>" }`.

### 4.3 Renovate (auto-bump of the policy pin)
All six consumers + `policy`/`policy-checker`/`.github` carry `.github/renovate.json5`. The **consumer** configs (app/infra) are full custom-manager configs (the policy repos just `extends: github>chrisns/.github:renovate`):
```json5
{
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  dependencyDashboard: true, automerge: false, pinDigests: true,
  separateMajorMinor: true, separateMinorPatch: true, separateMultipleMajor: true,
  rollbackPrs: true, labels: ["policy"],
  regexManagers: [
    { // Kubernetes
      fileMatch: ["kustomization.yaml"],
      matchStrings: ['mycompany.com/policy-version: "(?<currentValue>.*)"\\s+'],
      datasourceTemplate: "github-tags",
      depNameTemplate: "policy",
      packageNameTemplate: "policy-as-versioned-code/policy",
      versioningTemplate: "semver",
    },
    { // Terraform
      fileMatch: [".*tf$"],
      matchStrings: ['#\\s*renovate:\\s*policy?\\s*default = "(?<currentValue>.*)"\\s'],
      datasourceTemplate: "github-tags",
      depNameTemplate: "policy",
      lookupNameTemplate: "policy-as-versioned-code/policy",   // note: legacy lookupName vs packageName
      versioningTemplate: "semver",
    },
  ],
}
```
So Renovate watches `github-tags` of `policy-as-versioned-code/policy` and opens a PR to bump the version string in `kustomization.yaml` / `variable.tf`. `automerge:false` + `labels:[policy]` ⇒ a human reviews every policy-version bump. This is the **"as code, versioned, PR-reviewed"** lifecycle: upgrading an app's policy compliance is a Renovate PR that changes one line and re-runs the checker in CI.

### 4.4 Consumer CI — `app*/infra*/.github/workflows/policy.yaml`
Identical across all six:
```yaml
name: Policy Compliance
on: [push, pull_request]
jobs:
  policy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@2541b1... # v3.0.2
      - uses: docker://ghcr.io/policy-as-versioned-code/policy-checker:latest
```
The whole compliance gate is **one line**: run the `policy-checker` container against the repo. The checker reads the pin, clones that policy tag, evaluates. README transcripts show app1 → "Applying 1 policy ... pass: 1"; app2/app3 → "Applying 2 policies ... pass: 2"; infra → Checkov "Passed checks: 2/3".

---

## 5. `.github` org repo

- `profile/README.md`: title + "Supporting code for a talk (talks.cns.me)" + embeds `repos.dot` via gravizo.
- `repos.dot` (graphviz): the authoritative dependency model — `policy` subgraph holds the four versioned policy nodes; apps/infra (cylinders) point at versions with **green=compliant / orange=upgradeable / red=non-compliant** edges; `cluster1 → {all 4 versions, app1, app2, app3}` and `cluster2 → {2.0.0, 2.1.0, 2.1.1, app2, app3}`. Legend defines edge semantics.
- `repo-config.yml`: org-wide repo settings — squash+rebase only (no merge commits), delete-branch-on-merge, auto-merge on; branch protection on default branch with `required_status_checks.contexts: ALL`, linear history, no required reviews; vuln alerts + automated security fixes on; MIT license text; templated `FUNDING.yml` (`github:[chrisns]`, paypal.me/cns), `SECURITY.md` (chris@cns.me.uk + gpg), and Contributor Covenant 1.4 `CODE_OF_CONDUCT.md`. These templated files are pushed into every repo.
- `.github/renovate.json5`: `extends: github>chrisns/.github:renovate`.

---

## 6. How this org DIFFERS from `example-policy-org` (the successor)

| Aspect | `policy-as-versioned-code` (THIS / original) | `example-policy-org` (successor) |
|---|---|---|
| **Multi-version cluster** | **Two** dedicated repos: `cluster1` (all versions) + `cluster2` (`>=2.0.0`) — explicitly demonstrates *lifecycle* (a cluster dropping an old version). | **One** repo `e2e` — "everything coexisting on a single cluster for simplicity." No cluster1/cluster2 split, so no explicit "drop a version" lifecycle story. |
| **Policy action** | **None** — compliance gate is `docker://ghcr.io/.../policy-checker` used directly as a workflow step. | Has a dedicated **`policy-action`** repo (a reusable GitHub Action wrapper), in addition to `policy-checker`. |
| **Policy versions** | 1.0.0, 2.0.0, 2.1.0, 2.1.1 (the 2.0.0→2.1.0 fix is the `acounts` typo). | Uses **2.0.1** (e.g. infra2/infra3 "compliant with 2.0.1"); different version line. |
| **Repo naming/descriptions** | app1 "1.0.0 only", app2 "2.0.0", app3 "2.1.1". | app3/infra3 explicitly model "compliant with 2.0.0 but only using 1.0.0, **can be updated with a PR**" — foregrounds the Renovate upgrade narrative more than the original. |
| **Consumer set** | app1/2/3 + infra1/2/3 (six). | app1/2/3 + infra1/2/3 but mapped to the 2.0.x line. |
| **`e2e`/cluster CI** | KiND per push (cluster1/cluster2), readiness via `status.ready` jsonpath polling. | `e2e` README: KiND each run, "but this could just as well be a real cluster(s)" — same KiND-as-proof philosophy. |
| **Checker framing** | "⚠️ Not for general use", hardcoded to org. | Description softened to dev-facing ("simple tool to help our developers test their apps"). |

**Net:** the original org is the more *architecturally explicit* one for the coexistence problem — `cluster1` vs `cluster2` is the literal "many policy versions on one cluster, and how a cluster narrows the set it accepts" demonstration that a Flux design must replicate. The successor `example-policy-org` collapsed that into a single `e2e` repo and added a `policy-action` abstraction, trading the lifecycle clarity for a cleaner consumer DX.

---

## 7. Verbatim mechanism cheat-sheet (for the Flux redesign)

1. **Source of versions**: git tags on `policy` (`kustomize?ref=<tag>` / `git clone --branch <tag>`).
2. **Install N versions on one cluster**: apply `policy/kubernetes/kyverno?ref=<v>` once per version. Collision-free because of `nameSuffix: "-<v>"`.
3. **Scope each version to its opted-in workloads**: `commonLabels.mycompany.com/policy-version: "<v>"` on the ClusterPolicy **and** an identical `match.spec.rules[].match.all.resources.selector.matchLabels` inside the policy body.
4. **A workload opts in**: carries `mycompany.com/policy-version: "<v>"` (apps via kustomize `commonLabels`; the label propagates to pods).
5. **A cluster narrows accepted versions**: simply install fewer version bases (cluster2 = no 1.0.0). Dropped versions silently un-guard apps still pinned to them — a gap a Flux design should surface.
6. **Compliance gate (CI, pre-cluster)**: `policy-checker` reads the pin, clones that policy tag, runs `kyverno apply` / `checkov`.
7. **Lifecycle/upgrade**: Renovate `regexManager` watches `github-tags` of `policy`, PRs the one-line version bump, `automerge:false` ⇒ human review, CI re-checks.
8. **Exempting**: namespace or resource label `mycompany.com/require-<policy>: exempt`, plus blanket `kube-system` exclusion.
