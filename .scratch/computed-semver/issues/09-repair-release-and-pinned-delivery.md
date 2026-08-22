# 09 — Cut the repair release: pinned delivery for every policy

Type: task
Status: open
Blocked by: 10

## Question

Spun out of [ticket 07](07-platform-version-under-the-same-rule.md), which settled the design. This
ticket cuts the release. It is blocked by [ticket 10](10-render-mandatory-members.md), because the
version trees it publishes are rendered, not hand-written.

**One release, one commit, three tags: platform `1.0.0`, policy `1.0.2`, policy `2.0.1`.** It is
hand-classified, because cs-05 settled that the five unversioned policies are repaired *before* the
gate ships, with no grace mode. Write the classification and the reasoning into the release commit.
cs-05's honesty check re-runs it once the gate exists, and prints rather than fails.

**The job:**

1. **Bring `./graded` and `./posture` into the pinned path.** No Flux Kustomization targets either
   today. Their policies reach a cluster only through `graded/up.sh` and `posture/up.sh` running
   `kubectl apply -f`, not even `-k`, so their `kustomization.yaml` files are dead. After this release
   every policy is delivered by the version trees the array renders.
2. **Publish `1.0.2` and `2.0.1` with the full policy set, and swap the array elements.** `policy/v1.0.0`
   and `policy/v2.0.0` are cut tags and cannot gain files. If the shared copies are deleted without
   replacement versions, every pod pinned to either version loses its cage, its network policy and its
   posture check on the same day. Both new elements must be in the array before the old two leave it.
3. **Fold `policy/policies/v1.0.0/` into the distribution line at `1.0.1`.** Its rule
   `nonroot || (attested && hardened)` is strictly wider than `1.0.0`, and a widening is a patch. Because
   `2.0.0` already exists this is a backport, so it needs the maintenance branch and the anchored
   `--certificate-identity-regexp` that cs-05 specified. The `policy/` tree then goes.
4. **Fill the empty `commit` fields.** Both array elements carry `commit: ""`, so every per-version
   `GitRepository` is pinned by tag alone. ADR-0001 wants the resolved SHA as belt and braces.
5. **Delete the array's `action` field.** Nothing reads it. It duplicates `validationActions`, which is
   the copy admission reads and the copy `rederive_bumps.py` parses.
6. **Cut platform `1.0.0`.** At `0.x` semver gives no compatibility guarantee, so the gate would have
   nothing to refuse during exactly the period these repairs land.
7. **Rewrite `graded/up.sh` and `posture/up.sh` as offline twins.** They render the version trees as the
   ResourceSet would and apply that, so the demo runs without Flux and there is still one truth. They
   stop being a delivery path.
8. **Change `cut-release.yml` to carry more than one tag on one release**, by a named change and not a
   silent one. It takes a single `version` input today.

**Warning before step 2.** Three institutions pin platform and adopt by reviewed Renovate PR. Every
step above reaches them. Do not delete a shared policy in the same commit that publishes its
replacement version unless the array swap lands with it.

## Comments

Raised 2026-08-22 from ticket 07's grilling. See that ticket's sections 4 and 6 for the reasoning and
for the options that were rejected.
