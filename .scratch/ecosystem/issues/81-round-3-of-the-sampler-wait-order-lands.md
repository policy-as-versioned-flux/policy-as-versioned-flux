# 81 — Round 3 of the sampler wait-order lands on tuppence and ludlow

Type: task (HITL)
Status: resolved
Blocked by: none

## Question

Tuppence's and ludlow's five-fact samples record 16 of 16 rendered objects absent from the cluster on every run they have ever appended, because the sampler waits for kyverno below the composed apply. Ticket 60's post-resolution note records round 3 as "committed and patched" on branch `ticket-60-wait-order` in each unit's `.estate-clone/` checkout. That branch exists on no adopter remote. `enact_guard` correctly refuses the push. Nothing owns it.

The owner pushes the three commits (patches in `.scratch/ecosystem/patches/ticket-60/`), opens and merges the three PRs, and the next scheduled sample, not a dispatch, is the proof. Then ticket 62's twelve refs land so the same two adopters can compose at all.

Done = tuppence's and ludlow's newest scheduled `drift/samples.jsonl` record facts 4 and 5 true for their composed source, and the three `verify-reconcile.sh` checks and step 4 grade from it on a citable run.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R8. Finding: demo-steps/DS-F6. With ticket 73's cert-skew fix, three of run 21's seven reds have a route to green. Fact 2 on driftwood and ludlow is ticket 73, not this one.

## Answer

**2026-09-03: the AFK half is built; the push, the merge and the proof are the owner's.**

What was true when this build started: `ticket-60-wait-order` in each of the three `.estate-clone/`
units held one commit (driftwood a396c3b, tuppence 50fa2da, ludlow 6dcba87) whose parent was the
`main` of 2026-09-01. `main` had since appended nine sample lines to `drift/samples.jsonl` on each
unit, so a PR from the branch as it stood would have shown a 9-line deletion. Nothing graded the
wait order: round 2 shipped mis-ordered and the gate stayed quiet.

What is now true:

1. **The three commits sit on top of today's `main`.** Each was cherry-picked onto the unit's
   integration branch in a ticket-81 worktree (`.estate-clone/<unit>/.work/ticket-81`, branch
   `ticket-81-round-3-of-the-sampler-wait-order-lands`): driftwood 41b09c9, tuppence 10fcf41,
   ludlow 9d14e39. Each touches one file, `.github/workflows/drift-sample.yml`, 4 insertions and
   4 deletions; `drift/samples.jsonl` is not in the diff. Cherry-pick applied cleanly: the
   pre-image blob of the workflow (`4473698`) is unchanged on `main`, so the regenerated patches
   under `.scratch/ecosystem/patches/ticket-60/<unit>/` differ from the old ones only in the
   `From <sha>` header.
2. **The wait order is graded, not assumed.** `verify/sampler-wait-order/verify-sampler-wait-order.sh`
   (discovered by `talk/verify-all.sh`'s glob) reads each adopter's checked-out
   `drift-sample.yml`, finds six non-comment lines (kyverno rollout wait, flux-operator rollout
   wait, `apply -k gitops/composed/`, Kustomization waits, ResourceSet waits, the five-fact sample
   step), and requires each exactly once and strictly in that order. A duplicate is a FAIL
   because round 2's bug was a first-occurrence replace that duplicated the kyverno line. Its
   `selfcheck` proves it grades: the round-3 order passes; round 2's order, a duplicated wait and a
   missing wait fail; an absent clone exits 3. Run against the round-2 checkout it was red on all
   three units (`kyverno wait` at line 182/185 below the apply, `ResourceSet waits` at 174/177
   above it); against the cherry-picked worktrees it is green
   (`driftwood: kyverno wait@174 flux-operator wait@175 composed apply@176 Kustomization waits@180 ResourceSet waits@183 five-fact sample@188`,
   tuppence and ludlow `@177 @178 @179 @183 @186 @191`).
3. **What that check says about the gate now.** It grades the checkout the gate reads. Until the
   integrator merges the three unit branches into `ecosystem/build-2026-09-03` and checks that
   out, and until round 3 is on each adopter's `main`, the check is red. That is the truth of the
   estate and the reason the check exists; it is not to be excluded.
4. **The PR text is written**: `.scratch/ecosystem/patches/ticket-60/PR-BODY-round-3.md`, one
   body for the three unit PRs.

Which check grades it: `verify/sampler-wait-order/verify-sampler-wait-order.sh` grades the order
in the checkout; the three `verify-reconcile.sh` checks grade the lane record, which only a
scheduled run after the merge can turn.

**Decisions (ADR-0025):**

- **Cherry-pick, not rebase, and the old branch is left where it was** -- delegated. The branch is
  exactly one commit ahead of its merge-base, so rebase and cherry-pick produce the same tree.
  Cherry-picking into a ticket-81 worktree leaves `ticket-60-wait-order` untouched, so ticket 60's
  post-resolution note still names commits that exist, and the wave's branch rule (never check
  out a branch in the unit clone itself) holds. The new commits are what the owner pushes.
- **The order is graded by a hub verify script with a selfcheck, not a grep inside the workflow**
  -- delegated. A grep inside `drift-sample.yml` would run only on the lane, ~5 hours after a
  merge, and could not have caught round 2 before it shipped; the hub check runs in the gate on
  every truth run and fails on the checkout before anything is pushed. It is one script for the
  three adopters, so the three workflows cannot drift apart in this respect either.
- **Driftwood is in scope** -- delegated. The title names tuppence and ludlow because they are the
  ones observed red; the body says three commits and three PRs, and driftwood's round-2 green was
  a 3-minute timeout, not an ordered wait. Shipping the same sampler to all three is what makes
  one check honest for all three.
- **The remote branch keeps the name `ticket-60-wait-order`** -- delegated. The commit message,
  ticket 60's note and the patch directory all say ticket 60; the PR is the third round of that
  fix, and this ticket is the record that it landed.

Map line: Ticket 81 -- round 3 of the sampler wait order cherry-picked onto today's main in all three adopters, patches regenerated, the order graded by verify-sampler-wait-order.sh (red until merged), push and merge held for the owner.

## Waits on the owner

**Spent 2026-09-04, recorded 2026-09-08.** Nothing below is still owed: the three commits reached each
adopter's `main` by the second route (the wave's integration branch), the proof ran on the schedule,
and what it proved is written under *Recorded 2026-09-08* at the bottom of this file. The commands are
left as the record of what was asked.

Push is refused to an agent by `enact_guard` on every enactment repo; the merge must be the other
hand's. Run from the hub root, in this order, for each of driftwood, tuppence, ludlow:

1. Push the cherry-picked commit as the branch the ticket names (the sha is the ticket-81 branch
   head in the unit's `.work/ticket-81` worktree; `push` from the clone works because the object
   is in the clone's store):

       git -C .estate-clone/driftwood push origin 41b09c9:refs/heads/ticket-60-wait-order
       git -C .estate-clone/tuppence  push origin 10fcf41:refs/heads/ticket-60-wait-order
       git -C .estate-clone/ludlow    push origin 9d14e39:refs/heads/ticket-60-wait-order

   or, equivalently, `git am` the regenerated patch under
   `.scratch/ecosystem/patches/ticket-60/<unit>/0001-ticket-60-the-webhook-waits-really-do-precede-the-co.patch`
   onto a fresh `main` checkout of the real repo and push that.

2. Open the three PRs (base `main`, head `ticket-60-wait-order`, title
   `ticket 60: the webhook waits really do precede the composed apply`, body
   `.scratch/ecosystem/patches/ticket-60/PR-BODY-round-3.md`):

       gh pr create --repo policy-as-versioned-driftwood/driftwood --base main --head ticket-60-wait-order --title "ticket 60: the webhook waits really do precede the composed apply" --body-file .scratch/ecosystem/patches/ticket-60/PR-BODY-round-3.md
       gh pr create --repo policy-as-versioned-tuppence/tuppence  --base main --head ticket-60-wait-order --title "ticket 60: the webhook waits really do precede the composed apply" --body-file .scratch/ecosystem/patches/ticket-60/PR-BODY-round-3.md
       gh pr create --repo policy-as-versioned-ludlow/ludlow      --base main --head ticket-60-wait-order --title "ticket 60: the webhook waits really do precede the composed apply" --body-file .scratch/ecosystem/patches/ticket-60/PR-BODY-round-3.md

3. Merge each as the other hand, never with the owner's token (guard mode `other-hand`, ticket 88;
   the token is minted in the same shell segment):

       GH_TOKEN="$(.venv/bin/python -m twin.other_hand token --org policy-as-versioned-driftwood)" gh pr merge --repo policy-as-versioned-driftwood/driftwood ticket-60-wait-order --merge --delete-branch
       GH_TOKEN="$(.venv/bin/python -m twin.other_hand token --org policy-as-versioned-tuppence)"  gh pr merge --repo policy-as-versioned-tuppence/tuppence  ticket-60-wait-order --merge --delete-branch
       GH_TOKEN="$(.venv/bin/python -m twin.other_hand token --org policy-as-versioned-ludlow)"    gh pr merge --repo policy-as-versioned-ludlow/ludlow      ticket-60-wait-order --merge --delete-branch

4. Do nothing else. The proof is the next **scheduled** `drift-sample` run on each adopter
   (driftwood 06:20Z, tuppence 08:22Z, ludlow 09:16Z, each landing ~5 hours late in this estate),
   not a `workflow_dispatch`. When it has appended, an agent pulls `main` into the clones, runs
   the truth surface, and writes the citable TRUTH line and a dated comment here and in `map.md`.
   Done is then: tuppence's and ludlow's newest scheduled sample records facts 4 and 5 true for
   their composed source. Fact 2 on driftwood and ludlow stays with ticket 73; ludlow-composed
   fact 3 (3 of 3 Kustomizations not at pinned commit a800a58e) is to be read off that same
   sample before anyone charts it.

If the owner prefers to let the wave land it: the same three commits reach `main` when the
integrator merges the ticket-81 unit branches into `ecosystem/build-2026-09-03` and the owner
pushes the eight integration branches. That route ties the proof to the whole wave's review; the
route above lets the next clock prove this one fix on its own, which is what the ticket asks.

## Recorded 2026-09-08 — round 3 landed, the order is measured, Done is not met and is re-charted

Every sentence below was measured on 2026-09-08 against `origin/main` of each repository after
`git fetch`, and against the runs named. The build of 2026-09-03 above is left as it was written.

**What landed, and how.** On each adopter's `origin/main` the newest commit touching
`.github/workflows/drift-sample.yml` is the round-3 commit this ticket cherry-picked
(`git log --oneline origin/main -- .github/workflows/drift-sample.yml | head -1`):

| adopter   | commit    | authored               | reached `main` by                                   | merged (UTC)          | merged by            |
|-----------|-----------|------------------------|-----------------------------------------------------|-----------------------|----------------------|
| driftwood | `41b09c9` | 2026-09-03T20:03+01:00 | PR #23 (head `ecosystem/build-2026-09-03`, `fdd66c1`) | 2026-09-04T14:50:21Z | `app/pavc-other-hand` |
| tuppence  | `10fcf41` | 2026-09-03T20:03+01:00 | PR #15 (head `ecosystem/build-2026-09-03`, `f74dbdf`) | 2026-09-04T14:51:13Z | `app/pavc-other-hand` |
| ludlow    | `9d14e39` | 2026-09-03T20:03+01:00 | PR #13 (head `ecosystem/build-2026-09-03`, `6cfb529`) | 2026-09-04T14:51:19Z | `app/pavc-other-hand` |

So the three `ticket-60-wait-order` pull requests the section above prescribes were never opened; the
wave route it names as the alternative is the one that happened, and the merge identity is the other
hand's, as ticket 88 requires.

**What the citable hub runs say.** `verify/sampler-wait-order/verify-sampler-wait-order.sh` grades
PASS on run 177 (`hub=a08f868`) and on run 179 (`hub=fbbb547`), both recorded in `talk/truth.log`;
both trees carry the check, which commit `4b24c48` (Ticket 81) added. The recorded capture
`talk/captures/verify_sampler-wait-order_verify-sampler-wait-order.out` on `origin/main` reads:

    ok   driftwood: kyverno wait@174 flux-operator wait@175 composed apply@176 Kustomization waits@180 ResourceSet waits@183 five-fact sample@188
    ok   tuppence: kyverno wait@177 flux-operator wait@178 composed apply@179 Kustomization waits@183 ResourceSet waits@186 five-fact sample@191
    ok   ludlow: kyverno wait@177 flux-operator wait@178 composed apply@179 Kustomization waits@183 ResourceSet waits@186 five-fact sample@191
    PASS: driftwood, tuppence and ludlow each wait for the webhooks before applying the composed set, then wait for what they applied (round 3 order)

The clock rewrites and force-adds every capture on every run (`truth.yml`, `OBSERVATION_LANE`,
`git add -Af`), and those bytes have not changed since the clock commit `93d862c` of 2026-09-04; the
Actions logs of run 177 and run 179 each print
`verify/sampler-wait-order/verify-sampler-wait-order.sh PASS` as well. The manifest row is
`estate-observation | -`. Item 3 of the Answer ("red until merged") is therefore over: the map line
that still said so was corrected on 2026-09-08.

**Done is not met.** The served record is each adopter's `drift/samples.jsonl` at its `origin/main`,
appended by the adopter's own scheduled `drift-sample` lane. The newest line per adopter, composed
source, quoting the sample's own `why` strings:

- tuppence, drift-sample run 34228832561 (schedule, `ts` 2026-09-08T12:56:30Z), source
  `tuppence-composed`: fact 3 **True** — "every Kustomization consuming tuppence-composed applied
  751522b3bca9"; fact 4 **False** — "1 of 16 rendered objects are absent from the cluster and 0 are
  live but unequal to the offline render", `objects_absent` =
  `policies.kyverno.io/v1alpha1/GeneratingPolicy/cage-netpol-2-0-0`; fact 5 **False** — "15 of 16
  rendered objects are in no Flux inventory (absent from the cluster, or live but put there by
  something other than Flux)", `inventory_entries` 8.
- ludlow, drift-sample run 34232921856 (schedule, `ts` 2026-09-08T13:36:58Z), source
  `ludlow-composed`: fact 3 **True** — "every Kustomization consuming ludlow-composed applied
  a800a58e2547", so the item-4 question in the section above (3 of 3 not at pinned commit a800a58e) is
  answered by the sample: it is at the pin now; fact 4 **True** — "all 16 rendered objects are live
  and equal to the offline render"; fact 5 **False** — the same 15-of-16 sentence, `inventory_entries`
  8.

Every scheduled sample since the merge, composed source (`f4`/`f5` observed, `absent` =
`objects_absent`, `uninv` = `objects_not_in_inventory`, `inv` = `inventory_entries`):

| adopter   | `ts`                  | drift-sample run | f3    | f4    | absent | f5    | uninv | inv |
|-----------|-----------------------|------------------|-------|-------|--------|-------|-------|-----|
| tuppence  | 2026-09-05T11:53:26Z  | 33964466808      | True  | True  | 0      | False | 15    | 8   |
| tuppence  | 2026-09-06T12:13:09Z  | 34032373363      | True  | False | 5      | False | 15    | 8   |
| tuppence  | 2026-09-07T14:20:21Z  | 34132234986      | True  | False | 5      | False | 15    | 8   |
| tuppence  | 2026-09-08T12:56:30Z  | 34228832561      | True  | False | 1      | False | 15    | 8   |
| ludlow    | 2026-09-05T12:42:12Z  | 33966710005      | True  | True  | 0      | False | 10    | 13  |
| ludlow    | 2026-09-06T12:53:37Z  | 34034379528      | True  | True  | 0      | False | 15    | 8   |
| ludlow    | 2026-09-07T15:04:12Z  | 34136173752      | True  | True  | 0      | False | 15    | 8   |
| ludlow    | 2026-09-08T13:36:58Z  | 34232921856      | True  | True  | 0      | False | 15    | 8   |
| driftwood | 2026-09-05T10:41:34Z  | 33961154234      | True  | True  | 0      | True  | 0     | 19  |
| driftwood | 2026-09-06T11:04:15Z  | 34028943241      | True  | True  | 0      | True  | 0     | 19  |
| driftwood | 2026-09-07T12:40:10Z  | 34122734820      | True  | True  | 0      | True  | 0     | 19  |
| driftwood | 2026-09-08T11:25:31Z  | 34220235347      | False | False | 15     | False | 15    | 4   |

The fifteen objects tuppence and ludlow record as uninventoried are the fifteen under
`composed/policies/v{2.0.0,2.0.1,3.0.0}/` (five kinds by three versions); the sixteenth, the
orphan-guard the ResourceSet itself renders, is the one that IS in an inventory. Fact 4's absence on
tuppence is not one fixed object: five on 09-06 and 09-07, one (`cage-netpol-2-0-0`) on 09-08, none on
09-05. It moves because it is timing, below.

**Why, traced rather than read off the sentence.** Fact 5's `why` offers two readings, "absent" or
"put there by something other than Flux". Neither is what happened. `kubectl apply -k
gitops/composed/` (tuppence line 179, ludlow line 179, driftwood line 176 of `drift-sample.yml`, in
the step `install the engine, then reconcile from the REAL remotes`) applies exactly two objects: the
GitRepository `<unit>-composed` and the ResourceSet `composed-set`. The fifteen policies are applied
by the three Kustomizations `composed-v2-0-0`, `composed-v2-0-1`, `composed-v3-0-0` that the
ResourceSet's `resourcesTemplate` generates (`path: ./composed/policies/v<version>`, `wait: true`).
Nothing but Flux puts a policy on that cluster.

The Actions log of tuppence run 34228832561, step by step, with the workflow's line numbers:

1. 12:56:29.36 — `resourceset.fluxcd.controlplane.io/composed-set created`: the apply (line 179)
   returns.
2. 12:56:29.65 — `kustomization.kustomize.toolkit.fluxcd.io/tuppence condition met`: the
   Kustomization loop (line 183) has enumerated `get kustomizations -o name`, found only `tuppence`,
   which was already Ready, and returned. The composed Kustomizations do not exist yet.
3. 12:56:30.28 — `resourceset.fluxcd.controlplane.io/composed-set condition met`: the ResourceSet
   loop (line 186). Ready on a ResourceSet means it has applied the objects it renders, not that
   they have reconciled.
4. 12:56:30.41 — the `get ... -o wide` listing shows `composed-v2-0-0`, `composed-v2-0-1`,
   `composed-v3-0-0` aged `0s` with no status, and `tuppence-composed` at `Unknown  building artifact`.
5. `ts` 2026-09-08T12:56:30Z — the sample is taken, the second the composed Kustomizations exist.
   `drift/five-facts.py` reads the inventories once, at the top of `composed_set_facts` (line 260),
   and the sixteen objects afterwards, so during the seconds the sample takes the policies land: by
   the object reads fifteen (tuppence) or sixteen (ludlow) are live and byte-equal, and at the
   inventory read none of them was in any inventory. Which eight objects the inventories did hold
   was not read off the run; what is measured is that none of the fifteen is among them.

Run 33964466808 of 09-05 has the same shape (`composed-v*` aged `0s` at 11:53:26.78, inventory 8),
and ludlow's `inv 13 / uninv 10` on 09-05 is the same race won for one version. No line in any of these
logs says `composed-v2-0-0 condition met`: nothing waited for them.

Driftwood is the control, and its green is the accident item 3 of the Decisions above warned about.
Its `kustomizations/driftwood` did not reach Ready on the ephemeral cluster in either run read, so
the Kustomization loop blocks on it for the full bound — `error: timed out waiting for the condition on
kustomizations/driftwood` at 12:40:10 in run 34122734820, three minutes after the ResourceSet was
created at 12:37:09 — and that three-minute stall is what gave `composed-v*` time to apply
(`Applied revision` on all three at `3m`, inventory 19, facts 4 and 5 True on the three scheduled
samples of 09-05 to 09-07).
On 09-08 (run 34220235347) the stall was not enough: `composed-v*` at `3m` with no status, fact 3
False, fifteen absent, inventory 4. Driftwood's fact 5 is therefore reachable as defined, under this
exact code, which is why fact 5 is not to be redefined; it is the moment of sampling that is wrong.

**The finding.** Round 3's order — Kustomization waits before ResourceSet waits — cannot wait for
Kustomizations a ResourceSet has not generated yet, and the composed Kustomizations are all of that
kind. `verify-sampler-wait-order.sh` grades that order green because its `NAMES` array (line 40) pins
it, so the check is honest about what the workflow does and wrong about what the workflow should do.
Done — facts 4 and 5 true for tuppence's and ludlow's composed source on a scheduled sample — is a
wait-order question still, but not this order's. It is charted as ticket 107, with the fix candidates
and what each costs, no decision.

**Status: resolved, and why that word.** This ticket's own scope is the third round of the wait order:
cherry-picked, graded, landed on three adopters' `main`, and measured on the schedule. All of that is
done and on the record. Its Done is not met, and pretending otherwise would be the false green this
estate exists to refuse; but re-opening this ticket would hand round 4 to a ticket whose Answer,
Decisions and patches are all round 3's. The unmet Done moves to 107 with its evidence. Delegated
(ADR-0025).

**How the checks read this section.** The drift-sample run ids above are the adopters' own scheduled
observations, recorded by each adopter's lane commit into its `drift/samples.jsonl`; they are not hub
TRUTH runs and do not appear in `talk/truth.log`. `verify/cited-truth/` reads a run citation as one to
four digits, so an eleven-digit Actions id is no citation to it and is graded by nothing in the hub;
what grades those lines is the adopter's own `verify-reconcile.sh`, whose runner path reads that
committed file. The two hub runs this section cites, 177 and 179, are the only ones offered as proof
of a hub check.

Map line (2026-09-08): Ticket 81 -- round 3 is on all three adopters' main (driftwood 41b09c9,
tuppence 10fcf41, ludlow 9d14e39, merged 2026-09-04 by the other hand through the wave's pull
requests); verify-sampler-wait-order.sh PASS on recorded runs 177 and 179. Done is not met: tuppence's
and ludlow's composed source records fact 5 false on every scheduled sample since, because the order
waits for Kustomizations before the ResourceSet has generated them, and driftwood's greens rest on a
three-minute timeout on its own Kustomization. Re-charted as ticket 107.
