# 16 — Flux Image Automation vs Renovate for Auto-Bumping the Pinned Policy Version

**Question:** The original work used Renovate to open PRs when a new policy version is released. Should we keep that, switch to Flux image-automation, or drop commit-back entirely and let Flux follow a live semver range? This note researches the mechanics of each and frames the core PUSH-vs-PULL design tension for the PRD.

Sources: deepwiki `fluxcd/image-reflector-controller`, deepwiki `fluxcd/image-automation-controller`, fluxcd.io docs (OCIRepository), docs.renovatebot.com (flux manager), WebSearch 2025/2026. Links at the foot.

---

## 1. Flux Image Automation — the three-controller machine

Flux's image automation is **not one controller**. It is two controllers plus a source, working together:

1. **`image-reflector-controller`** — scans registries, stores tags, picks the "latest" (`ImageRepository` + `ImagePolicy`).
2. **`image-automation-controller`** — writes the chosen tag back into git and pushes (`ImageUpdateAutomation`).
3. A **`GitRepository`** source — the repo whose manifests get rewritten.

These are **not installed by default** with `flux bootstrap`; they are opt-in components.

### 1.1 `ImageRepository` — scanning a registry

`ImageRepository` defines *what to scan and how often*. It points at a registry path (e.g. `docker.io/library/alpine`) and an `interval`. The controller periodically lists tags, authenticates if needed (`secretRef` for Docker creds, `certSecretRef` for TLS, `serviceAccountName`, or cloud `provider: aws|azure|gcp` for keyless), applies an optional `exclusionList` of regex patterns, and **stores the surviving tags in its internal database**. Status reports `lastScanResult.tagCount` and `latestTags`.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata: { name: policy-bundle, namespace: flux-system }
spec:
  image: registry.example/policies/baseline
  interval: 5m
  # secretRef / provider for auth
```

Key point: `ImageRepository` does **not** decide what's "latest". It is a tag harvester.

### 1.2 `ImagePolicy` — choosing the latest tag

`ImagePolicy` references an `ImageRepository` and applies a selection rule over the harvested tags. Three policy types:

- **`semver`** — interprets tags as semantic versions, selects the highest within a `range` (e.g. range `5.1.x` selects `5.1.4`). Masterminds semver ranges (`^1.2.0`, `>=1.1.0 <2.0.0`, etc.).
- **`numerical`** — sorts numerically, picks first/last by `order: asc|desc`. Good for unix-timestamp or build-number tags.
- **`alphabetical`** — sorts lexically, picks by `order`. Good for date-ish or alpha-sortable tags.

**`filterTags`** runs *before* the policy rule and is the workhorse for messy tag schemes:

- `pattern` — a regex; only matching tags survive.
- `extract` — an optional capture group used *in place of* the raw tag for evaluation. This lets you match `release-v1.2.3-amd64`, extract `1.2.3`, and feed that clean string to the semver policy.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata: { name: policy-bundle, namespace: flux-system }
spec:
  imageRepositoryRef: { name: policy-bundle }
  filterTags:
    pattern: '^v(?P<ver>\d+\.\d+\.\d+)$'
    extract: '$ver'
  policy:
    semver: { range: '>=1.0.0 <2.0.0' }
```

Flow: harvest tags → `filterTags` regex/extract → policy picks latest → result published in `ImagePolicy.status.latestImage`.

### 1.3 `ImageUpdateAutomation` — commit-back to git

`ImageUpdateAutomation` is what makes it **PUSH**. It references a `GitRepository` as source and runs on an `interval`. Each run:

1. **Checkout** the repo (clone the configured branch).
2. **Scan** YAML under `spec.update.path` for image-policy markers (see §1.4).
3. **Rewrite** marked fields to the value from the referenced `ImagePolicy.status.latestImage`.
4. **Commit** with `spec.git.commit.author`, optional `messageTemplate` (Go template with `.Changed` data), optional GPG `signingKey`.
5. **Push** to `spec.git.push.branch` (created if absent), or to a `refspec`, or both.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata: { name: policy-bump, namespace: flux-system }
spec:
  interval: 30m
  sourceRef: { kind: GitRepository, name: flux-system }
  git:
    commit:
      author: { name: fluxbot, email: flux@example }
      messageTemplate: 'chore: bump policy to {{ range .Changed.Changes }}{{ .NewValue }}{{ end }}'
    push:
      branch: main
  update: { path: ./clusters/prod, strategy: Setters }
```

### 1.4 The `# {"$imagepolicy": "..."}` marker mechanism

This is the crux of how Flux knows *which line* to edit. You annotate the manifest with an inline YAML comment naming the `ImagePolicy` (as `namespace:name`). The controller uses **kyaml setters** to perform a surgical, structure-preserving replace — no templating, no full re-render.

```yaml
spec:
  image: registry.example/policies/baseline:1.4.2  # {"$imagepolicy": "flux-system:policy-bundle"}
```

Setter syntax variations in the marker:

- `flux-system:policy-bundle` — replace the **whole image ref** (`name:tag`).
- `flux-system:policy-bundle:tag` — replace **only the tag** portion (value is on a separate field, e.g. a Helm `tag:` value).
- `flux-system:policy-bundle:name` — replace **only the name/repository** portion.

So the marker both *locates* the field and *scopes* what part of it gets rewritten. It can sit on the same line as the value or on the line above.

### 1.5 PR flow

Flux image-automation is **commit-first, not PR-first**. Natively it pushes commits to a branch. To get a *reviewable PR* you either:

- push to a **non-default branch** (`push.branch: flux-image-updates`) and have an external job/Action raise the PR, or
- use **git push options** (`push.options`) where the *forge* turns them into a merge request — e.g. GitLab `merge_request.create`/`merge_request.target`. GitHub has no equivalent push-option-to-PR, so GitHub users wire a GitHub Action on the pushed branch.

This matters for the PRD: Flux's "PR" story is weaker and more bespoke than Renovate's, which is PR-native everywhere.

---

## 2. The other Flux-native path: live semver ranges (no commit-back)

There is a fundamentally different option that needs **none** of the three controllers above. If the policy bundle is an **OCI artifact** (or a chart, or a git tag), Flux's *source* layer can follow a semver range **live**:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata: { name: policy-bundle, namespace: flux-system }
spec:
  interval: 10m
  url: oci://registry.example/policies/baseline
  ref:
    semver: '>= 1.x'        # range; latest match wins
    semverFilter: '.*'      # optional regex pre-filter on tags
```

`spec.ref` subfields have **precedence: `digest` > `semver` > `tag`**. With `semver` set, every reconcile (`spec.interval`) re-lists tags, re-evaluates the range, and **auto-pulls the newest matching version** — pre-releases excluded unless the range carries a `-0` suffix. The same `ref.semver` mechanism exists on **`GitRepository`** (`ref.semver` over git tags) and on **`HelmRelease`** chart versions. Optional `verify` (cosign keyless) and `layerSelector` round it out.

This is **PULL**. There is no commit, no PR, no marker. Git holds a *range*, and the live cluster resolves it. The range itself is still in git (so still GitOps-auditable), but the *resolved version* is not pinned in git — it lives in `OCIRepository.status.artifact.revision`.

---

## 3. Can image-automation track POLICY artifact versions?

Yes, with a caveat. `image-reflector-controller` scans **container-image-style registries** via the registry tag-list API. OCI artifacts (policy bundles pushed with `flux push artifact`, ORAS, cosign) live in the **same OCI registries and expose the same `/tags/list`**, so an `ImageRepository` + `ImagePolicy` can in practice harvest and semver-select their tags exactly as it would for a container image. The marker then rewrites the pinned tag in an `OCIRepository` manifest.

But this is the **awkward** path: you'd be running image-reflector + image-automation purely to rewrite the `tag:` of an `OCIRepository` that Flux could have followed itself via `ref.semver`. The cleaner Flux-native PULL path makes the two image controllers redundant for this job. Image-automation earns its keep when you specifically want **pinned + commit-back + review**, which `ref.semver` cannot give you.

---

## 4. PUSH vs PULL — the design tension

| Dimension | PUSH (Renovate **or** Flux image-automation) | PULL (Flux `ref.semver` range) |
|---|---|---|
| What's in git | An **exact pinned version** | A **range** |
| Who resolves | A bot, at PR/commit time | The cluster, every interval |
| Reviewable | **Yes** — PR (Renovate) or branch/MR (Flux) | No gate; merge of the range is the only review |
| Audit trail | Each bump is a git commit/PR | Resolution recorded only in CR `.status`, not git history |
| Rollback | `git revert` the pin | Edit the range / pin a tag; no per-version commit to revert |
| Drift between envs | None — same SHA everywhere until promoted | Possible — two clusters may resolve the same range to different versions at different times |
| Blast radius of a bad release | Contained — human (or PR check) sees it first | Immediate — auto-pulled on next reconcile |
| GitOps "purity" | Slightly less (a bot mutates git) | Higher (git is declarative intent, cluster reconciles) |
| Operational weight | Renovate app/cron, or 2 extra Flux controllers | Zero extra components (source controller only) |

The tension is **control vs liveness**:

- **PUSH / pin + auto-PR** preserves the **original ethos**: a human (or policy CI gate) reviews each new policy version before it can affect anything; every change is a discrete, revertible commit; environments are promoted deliberately. This is what Renovate gave the original work, and Flux image-automation can approximate it (with a clunkier PR story).
- **PULL / live range** is **more GitOps-native and lighter**, but surrenders the per-version review gate and introduces possible cross-environment drift. For *policy* (where a bad bump could break admission across a cluster), giving up the review gate is a meaningful loss.

---

## 5. Renovate in a Flux world

Renovate has a **native `flux` manager** that understands Flux CRs directly:

- **`HelmRelease`** — bumps the chart version; for charts sourced from `HelmRepository` (incl. `type: oci`) it updates the version, and it also updates Docker image refs inside `spec.values` (helm-values style).
- **`GitRepository`** — updates `spec.ref.tag` or `spec.ref.commit` (only those keys).
- **`OCIRepository`** — updates `spec.ref.tag` and/or `spec.ref.digest`.

Caveats from the docs: namespaces must be **explicitly set** on resources (not inferred); by default the manager only matches `gotk-components.yaml`, so you must set `managerFilePatterns` (e.g. `"/flux/.+\\.yaml$/"`) to pick up your own manifests; and it won't preserve custom bootstrap flags in system manifests.

**How Renovate + Flux compose:** Renovate reads the **pinned** tag/digest in your Flux CRs, checks the upstream registry/repo for newer versions matching its own configured rules (which can include semver ranges, grouping, scheduling, stability-days, automerge), and opens a **PR** that rewrites the pin. Flux then reconciles the merged result. Renovate is the PUSH engine; Flux is the apply engine. Critically, Renovate works against **`OCIRepository.spec.ref.tag`** — i.e. it operates on the *pinned* form, not the *range* form, so adopting Renovate means committing to the **pin model**.

### When to use which

- **Renovate** — when you want **pinned versions + rich, reviewable PRs** across *many* dependency types (policies, charts, images, base images, CI actions) with grouping, scheduling, changelogs and automerge policies. Best fit for the original "auto-PR on new policy release" ethos. One tool covers Flux CRs *and* everything else in the repo. Cross-forge PR support (GitHub/GitLab/etc.).
- **Flux image-automation** — when you want commit-back **inside the cluster's trust boundary** with **no external bot/SaaS**, GPG-signed commits, and you're already all-in on Flux. Good for high-frequency image tags (numerical/timestamp build tags) where opening a PR per build is overkill and you just want a commit. Weaker, forge-specific PR story.
- **Live `ref.semver` range** — when **liveness beats control**: you trust the upstream's semver discipline, want zero extra machinery, and accept auto-follow within a range without per-version review. Lightest weight, most GitOps-pure, least control.

---

## 6. Recommendation for the PRD

For **policy** specifically, the review gate is valuable — a bad policy version can break admission cluster-wide. That argues for the **PIN + auto-PR (PUSH)** model, preserving the original ethos. Between the two PUSH options, **Renovate** is the stronger choice: PR-native on all forges, one tool for policies *and* charts *and* images, with scheduling/grouping/stability controls — versus Flux image-automation's commit-first model and bespoke PR wiring. Keep Flux's **`OCIRepository`/`GitRepository` with a pinned `ref.tag`**, and let **Renovate** raise the bump PRs against that pin. Reserve **live `ref.semver`** for low-risk, fast-moving, non-policy sources where auto-follow is acceptable. Document this as an explicit, per-source choice rather than a single repo-wide rule.

---

## Sources

- [fluxcd.io — OCIRepository](https://fluxcd.io/flux/components/source/ocirepositories/)
- [fluxcd.io — OCI cheatsheet](https://fluxcd.io/flux/cheatsheets/oci-artifacts/)
- deepwiki — fluxcd/image-reflector-controller (ImageRepository, ImagePolicy, filterTags, policy types)
- deepwiki — fluxcd/image-automation-controller (ImageUpdateAutomation, `$imagepolicy` marker, commit/push/PR)
- [docs.renovatebot.com — Flux manager](https://docs.renovatebot.com/modules/manager/flux/)
- [Renovate issue #18509 — Flux: support updating OCI helm charts](https://github.com/renovatebot/renovate/issues/18509)
- [Flux2 Discussion #1705 — RFP: OCI artifacts as sources](https://github.com/fluxcd/flux2/discussions/1705)
