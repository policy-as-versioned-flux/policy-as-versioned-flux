# 53 — cut-release.yml pushes the tag but never the branch, so signed evidence never reaches main

Type: task (HITL)
Status: open
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
