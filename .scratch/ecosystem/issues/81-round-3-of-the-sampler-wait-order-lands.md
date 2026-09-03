# 81 — Round 3 of the sampler wait-order lands on tuppence and ludlow

Type: task (HITL)
Status: prepared
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
