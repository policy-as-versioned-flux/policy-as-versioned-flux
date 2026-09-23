# 111 — The cage names priority classes its own delivery does not deliver

Type: task
Status: open
Blocked by: none

## Question

Ticket 86 made the estate's most distinctive claim gradable, and the first citable score is a red.
That is the instrument working. This ticket owns the defect the instrument found, which until now
was named only in ticket 86's "not this ticket's" list and belonged to nobody.

The scheduled sample on driftwood, run 35507849200 of 2026-09-20T11:28:25Z, records:

```
fact_6_the_bottom_rung_is_admitted_and_runs   observed=False
  the cage REFUSED the workload: Error from server (Forbidden): error when creating "STDIN":
  pods "cage-probe" is forbidden: no PriorityClass with name cage-baseline-3-0-0 was found

fact_7_the_bottom_rung_reaches_nothing_...    observed=None
  fact 6 did not deliver a workload running on the cage's bottom rung, so there was nothing to
  measure reach from; fact 6 carries what happened to it
```

Fact 7's could-not-look is correct and is worth keeping: it refuses to grade reach from a workload
that never ran, and it says which fact carries the reason.

**The cause, measured.** Platform ships `priorityclasses.yaml` in every policy version directory it
publishes (v2.0.0, v2.0.1, v3.0.0, v4.0.0, v5.0.0 and vselfcheck; not v1.0.0). Every adopter's
composed tree drops it: `git ls-tree -r composed/` on driftwood's `origin/main` returns no priority
class object at all. Meanwhile the composed `cage-tier` sets `priorityClassName` from its own tier
dial, to one of `cage-baseline-4-0-0`, `cage-restricted-4-0-0`, `cage-quarantine-4-0-0` or
`cage-isolated-4-0-0`, and platform's own `priorityclasses.yaml` for that version defines exactly
those four names.

So the mutating cage writes a `priorityClassName` that nothing in the delivery creates, and the
Priority admission plugin refuses the pod. **A cage that cannot admit a workload is not a cage.**

This is not a probe artefact. It is the served composition, and it means no workload the cage
mutates can run on any adopter, which is a stronger statement than the sample makes.

## A second mismatch, not yet run to ground

The refusal names `cage-baseline-3-0-0`, a 3.0.0-era class, while driftwood's composed tree carries
`composed/policies/v4.0.0/` and nothing else. The Kustomizations the ResourceSet generates are
`composed-v2-0-0`, `composed-v2-0-1` and `composed-v3-0-0`, ranged from platform's declared version
array rather than from what the adopter composed. Establish whether the set of versions INSTALLED
and the set of versions COMPOSED can differ, and if they can, whether that is intended. Do not
assume the priority class fix settles it; a delivery that installs a version the adopter did not
compose is its own question.

## What has to be decided

1. **Who delivers the priority classes.** They are cluster-scoped objects shared across versions
   by name-per-version. Candidates: compose them into each adopter's tree like any other member;
   or deliver them from platform's own Kustomization as part of the engine rather than the policy
   set. Say which, and why the other is wrong, because this decides whether an adopter can install
   a policy version without the platform's cooperation.
2. **Whether the composition should have refused.** A composed set that names an object it does not
   carry is a hole the composer could see at compose time. If it can be caught there, it should be,
   and then this class of defect cannot reach a cluster again.
3. **What the fact should say while it is broken.** It currently reads false, which is right. Check
   nothing downstream reads that false as "the cage does not hold", because what it actually says
   is "the cage never got the chance".

Done = `fact_6` reads true on a scheduled sample for all three adopters, with the priority classes
delivered by whatever route decision 1 picks, and the composer refusing a set that names an object
it does not carry.

## Notes

Charted 2026-09-21. The defect was named in ticket 86's build as not that ticket's and had no owner;
the three adopters' `verify-reconcile.sh` rows and `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh`
are red on main today and this is what they are red about.

Ticket 86's own record should be read beside this: its first citable score being a red, in the API
server's own words, is what it predicted and is the outcome it asked to be judged by.

Record: ticket 86; ticket 26 (the cage ladder lands); ticket 63; platform
`distribution/policies/v*/priorityclasses.yaml`; each adopter's `composed/policies/v4.0.0/cage-tier.yaml`.

## Build, 2026-09-22

Platform PR: https://github.com/policy-as-versioned-platform/platform/pull/30 (branch
`ticket-111-the-cage-delivers-its-classes`). No adopter PR: every adopter change waits on a tag
only the owner can cut (see "What remains"). Measured on detached `origin/main` worktrees of all
eight units, because the shared `.estate-clone` checkouts were behind `origin/main` on every unit.

### The cause, re-measured

- All three adopters record the refusal, not only driftwood. `drift/samples.jsonl` on each
  adopter's `origin/main` has fact 6 observed false with `no PriorityClass with name
  cage-baseline-3-0-0 was found` in driftwood runs 35438978784, 35507849200 and 35722798027,
  tuppence runs 35443208275, 35512492431, 35617054533 and 35733680722, and ludlow runs
  35444849712, 35513883790 and 35621907951. Read with a script over the last twelve records per
  adopter.
- The cause is in the composer. `compose/composition.py` `load_implementations` skipped every
  document whose kind was not an admission kind, with the comment "PriorityClasses are dials, not
  admission". Adopters compose with platform tools `v3.0.0` (`.github/platform-tools-pin.yaml`,
  commit 3602142e, identical on all three), whose `load_implementations` carries the same skip.
- A new check (below) run over each adopter's committed `composed/` on `origin/main` names four
  missing classes, `cage-{baseline,restricted,quarantine,isolated}-4-0-0@4.0.0`. Run over each
  adopter's `v1.1.0` tag, which is what the lane installs, it names nine: the baseline, restricted
  and quarantine classes of 2.0.0, 2.0.1 and 3.0.0.

### Decision 1: the composed tree delivers the classes, one version directory at a time (delegated)

Each version's PriorityClasses are composed into `composed/policies/v<version>/`, one per file,
beside the cage that names them. The version's own composed Kustomization applies them and prunes
them when the version leaves the array.

Why not platform's own Kustomization: the lane applies `gitops/platform/platform-pin.yaml` only,
never `platform-distribution.yaml`. Ticket 40 (Q5) split them because installing platform's fan-out
beside the composed set gave one cluster-scoped name two owners, and fact 4 read the loser. Asking
platform's Kustomization to deliver the classes would reinstall that second owner, and an adopter
could then install a policy version only with platform's cooperation. The adopter would not own
what its own composed artefact needs to admit a pod. Composing the classes keeps the composed
artefact self-sufficient, signed by the adopter's own tag like every other member.

Why per version and not once at `composed/`: the classes are named per version
(`cage-isolated-4-0-0`), so versions never share one. The one Kustomization that reconciles a
version's directory is the one that prunes it, so a class lives exactly as long as the cage that
names it. `composed/` root is not reconciled by the composed ResourceSet at all today.

### Decision 2: the composer refuses a set that names a class it does not carry (delegated)

`compose()` now refuses with `undelivered-priority-class` (subject `<class>@<version>`, or
`@machinery`) when a member writes a `priorityClassName` its own version directory does not carry,
and with `unreadable-priority-class` when it assigns one the composer cannot resolve.
`named_priority_classes()` reads a literal field, and a CEL assignment that is a quoted literal or
`variables.<map>.<field>` over a literal dial table. A dial indexed by a variable that is itself a
literal counts only that row, which is how the machinery cages (tier pinned to `'isolated'`) name
only `cage-isolated`.

Why a refusal and not a price: ADR-0020 prices a missing behaviour of the estate. This is neither
a behaviour nor an instrument. It is an artefact that cannot do what it says, the same shape as a
restated mutate that ADR-0016 refuses. Why refuse the unreadable case: a class the composer cannot
name is one it cannot prove it carries, and guessing would reopen this ticket's hole.

A third change fell out of building it. `_load_guards` rebound the shared module name `cage_body`
to whichever parent tree composed last and left it there, so a later composition could render its
cages through another tree's module, or a deleted one. The new tests hit that. `_load_guards` now
binds the parent's own `cage_body` for the render and restores the previous binding (delegated).

### Decision 3: fact 6 stays false, and nothing downstream reads it as "the cage does not hold" (delegated)

Read on each adopter's `origin/main`: `drift/five-facts.py` grades fact 6 false and fires
`the_cage_refuses_or_never_runs_the_workload_it_caged`, whose declared meaning in
`drift/window.yaml` is "a refusal here is a denial by another name, and it is the composed set that
produced it". That is what happened. Fact 7, the reach claim, reads could-not-look and names fact 6
as the carrier. `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` quotes the grader's last
line. `twin/drift.py` reads drift subjects, not facts 6 and 7. No reader turns this false into a
statement about reach, so no code change.

### The second mismatch: installed and composed can differ, and one of the two ways is not intended (delegated)

- The lane installs `gitops/composed/composed-set.yaml`. It pins the adopter's own tag `v1.1.0`
  and declares `2.0.0`, `2.0.1`, `3.0.0` in a hand-written array. `render_composed.py` and the
  ResourceSet both read that array. It is not ranged from platform's array.
- Between the pinned tag and `main` they differ, and that is intended: the lane installs only a
  signed tag, and `main` has moved to `composed/policies/v4.0.0/` alone. The array's own comment
  says 4.0.0 joins in the same pull request that moves the pin to a tag whose tree carries it.
- Between the array and the pinned tag's own tree they must not differ. Today they agree:
  `git ls-tree v1.1.0 composed/policies/` holds exactly v2.0.0, v2.0.1 and v3.0.0 on all three.
  Nothing checks it, though. A pin moved without the array reconciles a path that does not exist.
- All three still install 2.0.0, 2.0.1 and 3.0.0, which platform retired on 2026-08-29. Platform's
  own `versions.yaml` says why those lines cannot deploy even with their classes: they write
  `priorityClassName` without the `priority` pair and the Priority plugin refuses the mismatch. So
  the classes alone would not close fact 6 on the installed lines. The route has to move the lane
  to 4.0.0.
- Not built: a check that the composed-set array equals `composed/policies/` at the pinned tag.
  It belongs in the same adopter pull request that moves the pin, which waits on the owner.

### Tests run

- `compose/test_priority_classes.py`, 10 tests at the `compose()` seam. Red first: 9 of 10 failed
  on `origin/main` (the byte-for-byte verify test passed before and after). Green after.
- `.venv/bin/python -m pytest test_priority_classes.py test_portable_observations.py
  test_floor_change.py test_comparison_history.py -n0 -q` in platform `compose/`: 34 passed.
- `compose/verify-composition.sh` with `PAVC_ESTATE_CLONE` on a fresh origin/main estate: exit 3
  with the same SKIP as `origin/main` before the change (platform@2.0.1 lacks v5.0.0). Step 1b
  lists the two new refusal kinds.
- `compose/verify-fresh.sh` own proofs: PASS. `compose/handbook.py --selfcheck`: PASS.
- `mypy compose/composition.py`: 86 errors, equal to `origin/main`, none in the new code.
- Composing driftwood, tuppence and ludlow with the new composer against platform `v2.0.1` (their
  implementations pin): `outcome: composed`, zero refusals, and four new files each,
  `composed/policies/v4.0.0/cage-{baseline,restricted,quarantine,isolated}.yaml`.
- Not run: a cluster rehearsal. Fact 6 true is claimed by nobody until the scheduled lane says so.

### What remains, in order

1. **Merge** platform PR 30.
2. **Owner: cut the platform tools release** from platform `main` with `cut-release.yml`, the next
   `v*` after `v3.2.0` (`v3.3.0` if declared minor; the release gate grades the declaration). It
   also carries tickets 113 and 110 (platform PRs 28 and 29), already on `main`.
3. **Pin moves, one pull request per adopter** (agent work once step 2 exists): move
   `.github/platform-tools-pin.yaml` from `v3.0.0` to the new tag and commit, then recompose
   `composed/` in the same pull request. The recomposition adds the four
   `composed/policies/v4.0.0/cage-*.yaml` classes. The jump from tools v3.0.0 also brings the
   v3.1.0 and v3.2.0 composer changes, so the rest of `composed/` moves too. Tuppence PR 27 and
   ludlow PR 24 are held under ticket 84 and are not touched by this.
4. **Owner: cut each adopter's next release tag** with its `cut-release.yml`, after step 3 merges.
   Today each adopter has `v1.0.0` and `v1.1.0` only.
5. **Composed-set moves, one pull request per adopter** (agent work once step 4 exists): in
   `gitops/composed/composed-set.yaml` move `tag` and `commit` to that tag, set the array to
   `{ version: "4.0.0" }` alone, and move the `gitsign-gates` annotation to
   `flux-system/composed-v4-0-0`. Add the array-equals-tree check from above in the same pull
   request.
6. **Clock: a scheduled `drift-sample.yml` run on each adopter reading fact 6 true.** Waiting on
   the clock. No run is dispatched to stand in for it.

Ludlow carries one more blocker, not this ticket's, which step 4 may or may not clear. Its lane
sample of 2026-09-22T14:12:23Z (run 35737379620) has fact 2 false: the gitsign controller's verdict
on ludlow's `v1.1.0` is `certificate is not yet valid` at tagger time, and the three composed
Kustomizations report `Source artifact not found`, so no cage-tier was installed and fact 6 read
could-not-look. Driftwood's run 35601938687 of 2026-09-21 read the same could-not-look. Whether a
freshly cut ludlow tag verifies is unmeasured until the tag exists.

Also named, not built: the platform machinery (orphan cage, governed-namespace cages and their
`cage-isolated` class) composes at `composed/` root, and the composed ResourceSet reconciles only
`composed/policies/v*/`. No adopter pins a platform tree that carries the machinery cages today
(their implementations pin is `v2.0.1`), so nothing is refused on a cluster yet. The day an
adopter's implementations pin moves past `v3.0.0`, those objects need a delivery route too.
