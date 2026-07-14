---
status: accepted
---

# Adoption cadence: pin exact versions everywhere, bump via reviewed Renovate PR

Every consumer (and every cluster's set of installed policy versions) pins an **exact** policy tag
(with its resolved commit SHA — ADR-0001) on `GitRepository.spec.ref`; new versions are adopted only
via a **Renovate PR** that a human reviews and merges (`automerge:false`), in **every environment**. We deliberately reject Flux's
live semver ranges (`spec.ref.semver`) — even though they are the GitOps-native, lower-toil move —
because the thesis's non-negotiable is the **reviewed upgrade** ("debate happens in pull requests,
not exemption requests"), and a live range silently deletes that review gate and lets clusters
drift to different resolved versions.

## Considered options

- **Pinned everywhere + Renovate PR (chosen).** Identical to the 2022 original; every bump is
  reviewed, revertible, and CI-gated (`flux build/diff` + `kyverno apply` + `gitsign verify`).
- **Per-environment split (rejected).** Live range in dev/staging, pinned in prod. Risk-proportional
  but drops the review gate in non-prod and introduces cross-cluster version drift. Recorded as a
  north-star option only.
- **Per-policy-class split (rejected).** Ranges for lane-keeping, pins for gates. Conflates two
  independent axes (adoption cadence vs enforcement action) and can auto-adopt a broken policy
  fleet-wide unreviewed.

## Consequences

- **Adoption cadence and enforcement action are independent axes.** The lane-keeping (Audit) vs
  gate (Deny) split governs *how strict* a policy is, not *how fast its version updates*. A
  lane-keeping policy is still bumped by a reviewed PR.
- Renovate is a required component. **One update surface, one manager:** Renovate's native `flux`
  manager tracks a `GitRepository`'s tag *or* its commit, exclusively — it cannot maintain the
  `{tag, commit}` pair ADR-0001's integrity model requires. So every policy pin — consumer/app
  sources and the fleet's single version-array source of truth (which the ResourceSet expands into
  per-version sources — see ADR-0005) — is bumped
  by one Renovate **`customManager`** (git-refs datasource: tag as `currentValue`, resolved commit
  SHA as `currentDigest`). A `customManager` is a few lines of declarative Renovate config, **not** the bespoke
  bash/Docker checker the "no bespoke tooling" principle deleted — that exemption is explicit. The
  reviewed PR is also the unit that carries the "why" debate.
