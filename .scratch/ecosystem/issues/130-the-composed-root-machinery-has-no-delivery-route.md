# 130 — The composed root machinery has no delivery route

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator, from ticket 111's "Also named, not built" and a read-only
map of the rollout. It blocks the adopters' move to policy 5.0.0, which the owner accepted on
2026-09-23.

Platform's composer renders three kinds of machinery at the root of an adopter's `composed/`
tree, not under `composed/policies/v*/`: the orphan cage (`composed/orphan-guard.yaml`), the
governed-namespace cages, and the unsuffixed `cage-isolated` PriorityClass they name. Measured by
the rollout map at platform main:

1. Each adopter's composed ResourceSet (`gitops/composed/composed-set.yaml`) reconciles only
   `composed/policies/v*/`. The root machinery reaches no cluster.
2. At the adopters' implementations pin today (`v2.0.1`) the orphan guard renders
   `validationActions: [Deny]`, and `composed-set.yaml` installs its own inline Deny orphan guard
   (lines 115-157 in driftwood). At platform main it renders `[Audit]` beside an orphan cage.
3. So when an adopter moves its implementations pin past `v3.0.0`, one of two things happens.
   Either the inline Deny stays and the new Audit plus cage never arrive, or the inline guard is
   dropped and an orphan claim reaches no cage at all.
4. Fact 4 of the lane sample compares the live guard with the offline render, so it can read
   FALSE after the move.

What this ticket owes:

1. A delivery route for every object the composer renders at the `composed/` root, decided and
   recorded with its reason. Candidates: a second Kustomization over the root, or the composer
   rendering the machinery under the version directory it belongs to.
2. The inline orphan guard in each adopter's `composed-set.yaml` is replaced by the delivered
   machinery, with nothing left uncaged in between.
3. A check, offline, that every object under `composed/` is reached by some Kustomization the
   adopter serves, and a planted object outside every path that the check refuses.
4. It lands before, or in the same PR as, each adopter's composed-set move to the new tag.

## Done

Every object the composer renders reaches the cluster through a route the adopter serves, the
inline guard is retired without a gap, and the offline check holds it.

## Build, 2026-09-22

Built on 2026-09-23 under this heading. There are four pull requests. Platform PR
https://github.com/policy-as-versioned-platform/platform/pull/38 merges before the next tools
release. Driftwood PR https://github.com/policy-as-versioned-driftwood/driftwood/pull/39,
tuppence PR https://github.com/policy-as-versioned-tuppence/tuppence/pull/35 and ludlow PR
https://github.com/policy-as-versioned-ludlow/ludlow/pull/32 each merge together with that
adopter's composed-set move. All four use branch `ticket-130-the-composed-root-is-delivered`.
Everything was measured on detached `origin/main` worktrees of all eight units, not on the shared
clones.

### What was measured first

- The platform `origin/main` composer, run against all three adopters with platform
  `origin/main` as the implementations parent, renders eight machinery files at the
  `composed/` root. It renders version trees for both `v4.0.0` and `v5.0.0`, because platform's
  `versions.yaml` declares both, each with a commit. Every array-ranged machinery object carries
  the allow-list `['4.0.0', '5.0.0']`: the orphan guard, the orphan cage, its holds and
  `cage-netpol-bottom-rung`.
- Every workload the adopters declare claims `4.0.0`. That covers `gitops/apps/`, `deploy/pod.yaml`
  and tuppence's `reset/workloads.yaml` (grep over each `origin/main`).
- Kyverno 1.18.2 `apply` of the composed v5.0.0 `cage-tier` plus `orphan-cage.yaml` on a pod that
  claims `4.0.0` gives `pass: 0, fail: 0, warn: 0, error: 0, skip: 4`. Nothing cages it. Add the
  v4.0.0 `cage-tier` and it gives `pass: 2`, with `posture.acme.io/tier` written.
- `flux build kustomization --dry-run` (flux 2.9.5) over `v1.1.0:composed/` fails:
  `failed to decode Kubernetes YAML from .../composed/HEADER.yaml: missing Resource metadata`.
  Flux cannot reconcile the root without a kustomization file.
- flux-operator's ResourceSet reconciler applies, then garbage-collects, then waits for health.
  Source: `internal/controller/resourceset_controller.go`, read through DeepWiki.
- Each adopter applies `gitops/composed/` in exactly one place: `drift-sample.yml`, on an
  ephemeral cluster (`git grep` in each adopter).
- `drift-sample.yml` typed `COMPOSED_REF: v1.1.0`. `render_composed.versions(ref)` read the
  array from the tag's own copy of `composed-set.yaml`. The move comes after the tag is cut, so
  that copy lags the move. After the move, fact 4 would have rendered the wrong tree on both
  counts.

### Decision 1: the composer renders the root's kustomization, and the adopter reconciles `./composed` (delegated)

The composer now renders `composed/kustomization.yaml`. It lists exactly the machinery files the
composer wrote at the root, from the same list that wrote them. It names files only. Each adopter's
ResourceSet gains one Kustomization, `composed-machinery`, with `path: ./composed`, `prune: true`
and `wait: true`.

Why not a hand-written kustomization in the adopter: `verify()` refuses any committed
`composed/**/*.yaml` the composer did not render. A hand-kept list would also drift from what the
composer renders.

Why not move the machinery under a version directory, the ticket's second candidate: the orphan
machinery is ranged over the whole served set, not one version. Two installed versions would give
two objects with one name. Moving it to another directory would also break the hub checks that
read `composed/orphan-guard.yaml` by path (`verify/deny-is-not-a-rung/`, `verify/lifted-apps/`).

Why files only: a directory entry would reach `composed/policies/v*/` a second time, and every
versioned object would have two owners.

### Decision 2: the inline guard is retired in the same change that adds the route (delegated)

The inline Deny `policy-version-orphan-guard` and the composed Audit one share a name. Keeping both
gives one name two owners, which ticket 40 Q5 removed. So the adopter PR removes the inline block
and adds `composed-machinery` in one change.

Merged alone, while the tag is still `v1.1.0`, it would leave nothing to cage or refuse an orphan
claim. The new check refuses that state with 18 faults on every adopter, including
`orphan-uncaged`. That is why each adopter PR merges together with its composed-set move.

"Nothing uncaged in between" holds in commits, and the check grades it. Within one reconcile on a
long-lived cluster there would be a window of one Kustomization apply, because the ResourceSet
garbage-collects the inline guard before `composed-machinery` has applied. No cluster carries the
old state across the move: the only applier is the ephemeral lane, which applies fresh on every
run. This is recorded as the ceiling, not closed.

### Decision 3: the installed array is exactly what was composed, so the move is `["4.0.0", "5.0.0"]` (delegated)

The integrator planned the array `[5.0.0]`. Measured, that is unsafe. The next tools tag composes
both served lines, and every machinery allow-list admits `4.0.0`. Every adopter workload claims
`4.0.0`. With `[5.0.0]` installed, those workloads match no `cage-tier` and no orphan cage, and run
uncaged (the kyverno run above).

The rule the check enforces: the array equals the `composed/policies/v*` directories at the pinned
tag, and every machinery allow-list equals the array. Ticket 111 named this check but did not
build it.

To reach `[5.0.0]` later, the order is:

1. Relabel the workloads to `5.0.0`.
2. Retire `4.0.0` from platform's `versions.yaml`.
3. Cut a platform tag, then recompose.

Considered and rejected: a party declaration naming the served subset an adopter composes. It is a
new composer input, it touches pricing and evidence, and with the workloads still on `4.0.0` it
would move every adopter workload to the bottom rung through the orphan cage.

### Decision 4: the check lives in each adopter's `render_composed.py`, beside the render it grades (delegated)

`render_composed.py` is each adopter's offline twin of what its ResourceSet installs. The three
copies differ only in the adopter's name (`diff`), so `reach` joins them in the same shape.

Changes to the module:

- It reads the ResourceSet from the checkout and `composed/` at the pinned tag.
- It expands the template. It reads the subset of the flux-operator template language the
  ResourceSets use, and anything else is could-not-look.
- It counts a route that reaches a non-object file as delivering nothing, as flux does.

`reach` refuses on nine fault kinds: `array-not-tree`, `missing-route`, `missing-file`,
`unreached`, `reached-twice`, `not-an-object`, `two-owners`, `allow-list` and `orphan-uncaged`.

Where it runs:

- Adopter `shift-left.yml` runs it on every pull request. It fetches tags because that checkout is
  shallow.
- `drift-sample.yml` prints it and now reads `COMPOSED_REF` from `composed-set.yaml`.

Why not a platform tool: the adopters call platform tools through `.github/scripts/platform-tools.py`,
whose subcommands are fixed. A new one would change that runner in three repos, and the check
could run only once the tools pin had moved.

### Tests run

- Platform `compose/test_machinery_delivery.py`: 5 tests at the `compose()` seam. Red first:
  4 failed with `KeyError: 'composed/kustomization.yaml'`. The handbook test then failed until
  `handbook._policy_objects` skipped the file. All 5 pass.
- Platform `pytest test_machinery_delivery.py test_priority_classes.py test_portable_observations.py
  test_floor_change.py test_comparison_history.py -n0 -q`: 51 passed, 14 subtests passed.
  `handbook.py --selfcheck`: PASS, 47 checks. `verify-fresh.sh`: PASS.
- Platform `composition.py --selfcheck`, with `PAVC_ESTATE_CLONE` set to detached `origin/main`
  worktrees: it stops at the same assertion on the branch and on `origin/main` (review F2,
  `assert absolute not in blob`), after 94 OK lines each. The one differing line counts 41
  rendered files, not 40. The extra file is the new kustomization.
- Platform `mypy compose/composition.py compose/handbook.py`: 94 errors before and after, none
  new (diffed after stripping line numbers).
- Adopter `tests/test_composed_reach.py`: 13 tests. Red first on driftwood with the `origin/main`
  module: 13 failed. All 13 pass on driftwood, tuppence and ludlow, under pytest and under
  `unittest discover`. They include the planted object the ticket asks for, at the root and in a
  subdirectory. `mypy` on the module and the test: no issues. `render_composed.py selfcheck`: ok, 15
  objects at `v1.1.0`. `drift/five-facts.py selfcheck`: ok.
- `render_composed.py reach` on each adopter branch against `v1.1.0`: REFUSED, 18 faults.
- The move, simulated: each adopter's recomposed tree (the branch composer, platform `origin/main`
  as parent) committed and tagged in a throwaway repository, with the branch's
  `composed-set.yaml` moved to that tag. `["4.0.0", "5.0.0"]` gives 0 faults and renders 26
  objects. `["5.0.0"]` gives 14 faults: `array-not-tree`, 9 `unreached` for the v4.0.0 tree and 4
  `allow-list`.
- Hub `verify-sampler-wait-order.sh` over the three branches: PASS. Hub
  `verify-deny-is-not-a-rung.sh`: the same SKIP as `origin/main`, with outstanding Deny copies
  down from 19 to 16. The three inline guards are gone.

### What remains, in order

1. **Merge platform PR 38.** Integrator.
2. **Owner: cut the next platform tools release** from platform `main`. It carries this and
   ticket 111's platform PR 30.
3. **Per adopter, the pin-move PR:** the tools pin, `gitops/platform/platform-pin.yaml` and
   `party.yaml`'s implementations edge move to that tag, then recompose. The recompose writes
   `composed/kustomization.yaml` beside the machinery. Integrator.
4. **Owner: cut each adopter's next tag.**
5. **Per adopter, this PR plus the composed-set move, as one merge.** Push the move commit onto
   the ticket-130 branch. In it, move `tag` and `commit` to the new adopter tag, set the array to
   `{ version: "4.0.0" }, { version: "5.0.0" }`, and set `gitsign-gates` to
   `flux-system/composed-v4-0-0,flux-system/composed-v5-0-0,flux-system/composed-machinery`. The
   shift-left `reach` step then reads green. Integrator.
6. **Hub, after step 5:** the `policy-version-orphan-guard` row of
   `verify/deny-is-not-a-rung/register.yaml` loses its last served Deny copies. The check will ask
   for the row to move. Integrator.
7. **Clock:** a scheduled `drift-sample.yml` run on each adopter reads facts 4 and 5 true, with
   the machinery in the render and in the `composed-machinery` inventory. No run is dispatched to
   stand in for it.
