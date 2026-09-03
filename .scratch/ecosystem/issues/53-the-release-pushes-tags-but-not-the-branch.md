# 53 — cut-release.yml pushes the tag but never the branch, so signed evidence never reaches main

Type: task (HITL)
Status: resolved
Blocked by: none

## Question

Observed live on 2026-08-31, cutting two platform releases in sequence for the first time.

`.github/scripts/cut-release-push.sh` ends with:

    git push --atomic "$remote" "${tags[@]}"

Tags only. But the workflow **commits the signed release-gate evidence onto the checked-out
branch** first (`cs-27: signed release-gate evidence for policy/v4.0.0`, then `cs-27: point
versions.yaml commit field(s) at the evidence commit`). Those two commits are reachable only from
the tag. They are **not** ancestors of `main`:

    git merge-base --is-ancestor policy/v4.0.0^{} origin/main   -> NO
    git ls-tree origin/main computed-semver/evidence/ | grep 4.0.0
      computed-semver/evidence/4.0.0.json          (from an earlier dry run)
      # 4.0.0.json.bundle is ABSENT

So `main` carries the evidence document without its cosign bundle, and the bundle exists only
inside the `policy/v4.0.0` tag.

**What it breaks.** The next release cut from `main` inherits that hole. `v2.0.0`, cut minutes
later, contains `4.0.0.json` and not `4.0.0.json.bundle`. Every adopter pinned to `v2.0.0` then
fails its own gate, correctly:

    REFUSED: no cosign bundle committed for version 4.0.0 at
    platform/computed-semver/evidence/4.0.0.json.bundle

driftwood #12, tuppence #9 and ludlow #8 are red for exactly this reason and no other. Their pins,
party artefacts and composed trees are already correct and pushed.

**Why it hid.** It needs two releases in sequence to show. Every earlier release was the only one
of its day, so nothing ever read a `main` that had lost the previous release's evidence.

## What to decide

The commit is made on the branch, so landing it there is plainly the intent; only the push is
missing. But this is the trust machinery, and three things need a human:

1. **Does the branch get pushed with the tags, atomically?** That is the small fix, and it keeps
   the "either every ref lands or none do" promise the script's own header makes. The risk is that
   a release now writes to `main` directly, which is a push to a protected branch by a workflow.
2. **Or does the evidence land by pull request instead**, leaving the release to push tags only?
   Slower, reviewable, and it keeps every write to `main` human-approved — which is closer to the
   estate's own rule that the reviewed pull request is the unit of adoption.
3. **How is the already-orphaned evidence recovered?** `64635df` and `1d8cec2` hold it. They are
   signed commits on the tag. Cherry-picking them onto `main` re-signs them under a different
   identity, which is a second signature on the same content and needs a decision.

Whatever is chosen, `v2.0.0` cannot be repaired: a tag is immutable. A `v2.0.1` cut from a `main`
that carries the bundle is what unblocks the three adopters.

## Notes

Found while completing the merges on 2026-08-31. Everything else in the chain is done: the three
publisher pull requests are merged, `policy/v4.0.0`, ico `v3.0.0` and platform `v2.0.0` are cut and
signed by CI, and the three adopters' pin bumps are committed and pushed. This is the only thing
between here and the last three merges.

## Comments

- 2026-08-31 (ambition review): The defect is repaired in code and the record should say so: cut-release-push.sh pushes HEAD:branch atomically with the tags (b83eba1, on platform main), all four evidence bundles are on main, v2.0.0/v2.0.1 are cut and every adopter pins v2.0.1. Close with an Answer naming the check that proves it. Add one clarifying line: this ticket does NOT own the platform CEL/toolchain reds — new ticket 54 does.

## Answer (2026-09-03)

The defect was repaired and enacted by the owner on 2026-08-31; this ticket records it and adds the
two checks that prove it, so the record is graded and not merely stated.

**What is true now, read live from `.estate-clone/platform` on 2026-09-03:**

- `.github/scripts/cut-release-push.sh` line 34 on platform `origin/main` is
  `git push --atomic "$remote" "HEAD:refs/heads/${branch}" "${tags[@]}"` (repairing commit
  `b83eba1`, merged as platform PR 6). A detached HEAD is refused before anything is pushed.
- `git ls-tree origin/main computed-semver/evidence/` shows `2.0.0`, `2.0.1`, `3.0.0` and `4.0.0`,
  each with its `.json` and its `.json.bundle`.
- The evidence for `policy/v4.0.0` was re-committed onto `main` by the release bot as `533dccb`
  (2026-08-31T16:18Z). The orphaned signed commits `64635df` and `1d8cec2`, and the `policy/v4.0.0`
  tag commit, remain unreachable from `main` (`git merge-base --is-ancestor` says no for all three).
- Tags `v2.0.0` and `v2.0.1` exist. `v2.0.0` is immutable and still carries `4.0.0.json` with no
  bundle. `v2.0.1` carries all four pairs.
- driftwood, tuppence and ludlow `gitops/platform/platform-pin.yaml` all pin `tag: v2.0.1`.

**The three decisions posed above (owner-instructed, 2026-08-31, enacted as `b83eba1`):**

1. The branch is pushed with the tags, atomically. A workflow now writes to `main` by atomic push;
   the alternative of landing evidence by pull request was not taken.
2. Not by pull request. The evidence is the gate's own signed output for a tag that already exists;
   a reviewer has nothing to dispose of, and the window between "tag exists" and "main carries its
   evidence" is the defect itself.
3. The orphaned commits were not cherry-picked (that would put a second signature under a different
   identity on the same content). The release bot re-committed the evidence (`533dccb`) and `v2.0.1`
   was cut from a `main` that carries every bundle.

**Decisions taken here (delegated, ADR-0025):**

- **The citable check is the hub-side one.** `verify/provenance/verify-release-evidence-reaches-main.sh`
  grades what the adopters actually read: every evidence document on platform `origin/main` and on
  each adopter's pinned tag has its bundle beside it, and the push line on `origin/main` is the
  atomic branch-plus-tags one. Reason: it runs from the hub against the published ref with no
  platform push needed, so it is green on the gate today, and it grades the outcome the three
  adopters refused on. It exits 3 when the platform clone cannot be read, 1 on any finding. Its
  `selfcheck` (run first on every invocation) proves the graders bite: a bundle-less tree fails, the
  pre-repair tags-only push line fails (a comment carrying the right line does not count), an empty
  tree fails, and the real, immutable platform `v2.0.0` fails the pairing exactly as it did for the
  adopters. Discovered by `talk/verify-all.sh`'s `find verify -name 'verify*.sh'`.
- **Platform's own offline twin grades the mechanism.** `verify-cut-release-tags.sh` case 8 (on the
  platform branch `ticket-53-the-release-pushes-tags-but-not-the-branch`, commit `951f5a8`) commits a
  stand-in evidence file on the branch, runs the real `cut-release-push.sh` against the script's
  scratch bare remote, and requires the remote's `refs/heads/main` to be the tagged commit; then a
  rejected push (a tag already on the remote at a different object) must move neither the tags nor
  the branch; then a detached HEAD must be refused. Written first and watched fail against the
  pre-repair push line (`remote refs/heads/main is 59721a3..., not the tagged commit f262f6a...`),
  then green against `b83eba1`. It reaches the gate only when the owner pushes platform.
- **The orphaned commits stay orphaned.** `64635df`, `1d8cec2` and the `policy/v4.0.0` tag commit
  are not to be cherry-picked, rebased or merged onto `main` later: the evidence is on `main` as
  `533dccb`, the tag is immutable, and a second copy would be a second signature. Recorded as the
  accepted state so nobody later "repairs" it.
- **The hub check reads `origin/main`, not the working checkout**, so a local branch in the clone
  (the integration branch, a ticket worktree) can neither fake nor spoil the grade; the published
  ref is what adopters pin from.
- **The ADR note goes on ADR-0011** (release gate computes the bump), whose consequence "the
  publisher gate runs before `git tag`" is the step that commits the evidence. Dated note added,
  no new ADR number.

**Clarifying line:** this ticket does not own the platform CEL/toolchain reds. Ticket 54 does.

**How verified (from the hub worktree root):**

    bash verify/provenance/verify-release-evidence-reaches-main.sh selfcheck   # exit 0
    bash verify/provenance/verify-release-evidence-reaches-main.sh             # exit 0, PASS
    RELEASE_EVIDENCE_PLATFORM=/nonexistent bash verify/provenance/verify-release-evidence-reaches-main.sh   # exit 3, SKIP
    bash .estate-clone/platform/verify-cut-release-tags.sh                     # exit 0, PASS (case 8 included)

Map line: [53 — The release pushes tags but not the branch](issues/53-the-release-pushes-tags-but-not-the-branch.md) — owner-instructed 2026-08-31 (platform `b83eba1`): the branch goes in the same atomic push as the tags, never by PR; orphaned signed commits stay unreachable, the release bot re-committed the evidence (`533dccb`), `v2.0.1` carries every bundle and all three adopters pin it; graded by the hub's `verify-release-evidence-reaches-main.sh` (outcome, green now) and platform `verify-cut-release-tags.sh` case 8 (mechanism, waits on the owner's push); ADR-0011 dated note; ticket 54 owns the CEL/toolchain reds.

## Waits on the owner

- Pushing platform branch `ticket-53-the-release-pushes-tags-but-not-the-branch` (commit `951f5a8`,
  case 8 in `verify-cut-release-tags.sh`) once the integrator has merged it into
  `ecosystem/build-2026-09-03`. The guard refuses enactment pushes. Nothing else waits.
